from django.test import TestCase
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.organizations.models import Organization
from .models import InAppNotification, User


class UserOrganizationSecurityTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="ONG A",
            email="contact-a@example.test",
            phone="+221700000001",
            address="Dakar",
            region="Dakar",
            intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG B",
            email="contact-b@example.test",
            phone="+221700000002",
            address="Thiès",
            region="Thiès",
            intervention_domain="Humanitaire",
        )
        self.manager_a = self.make_user(
            "gerant-a@example.test", User.Role.GERANT, self.org_a
        )
        self.manager_b = self.make_user(
            "gerant-b@example.test", User.Role.GERANT, self.org_b
        )
        self.finance_a = self.make_user(
            "finance-a@example.test", User.Role.FINANCE, self.org_a
        )
        self.chef_a = self.make_user(
            "chef-a@example.test", User.Role.CHEF_PROJET, self.org_a
        )
        self.agent_a = self.make_user(
            "agent-a@example.test", User.Role.AGENT, self.org_a
        )
        self.finance_b = self.make_user(
            "finance-b@example.test", User.Role.FINANCE, self.org_b
        )
        self.chef_b = self.make_user(
            "chef-b@example.test", User.Role.CHEF_PROJET, self.org_b
        )
        self.agent_b = self.make_user(
            "agent-b@example.test", User.Role.AGENT, self.org_b
        )
        self.client = APIClient()
        self.client.force_authenticate(self.manager_a)

    @staticmethod
    def make_user(email, role, organization, **extra_fields):
        first_name = extra_fields.pop("first_name", "Test")
        last_name = extra_fields.pop("last_name", "User")
        return User.objects.create_user(
            email=email,
            password="SafePass123!",
            first_name=first_name,
            last_name=last_name,
            role=role,
            organization=organization,
            status=User.Status.ACTIVE,
            is_active=True,
            **extra_fields,
        )

    @staticmethod
    def detail_url(user):
        return f"/api/accounts/users/{user.pk}/"

    @staticmethod
    def jwt_client(user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client, str(refresh)

    def test_manager_can_list_and_read_users_in_own_organization(self):
        self.assertEqual(self.client.get("/api/accounts/users/").status_code, 200)
        response = self.client.get(self.detail_url(self.finance_a))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["organization"], self.org_a.pk)

    def test_both_tenants_can_list_and_read_own_users_only(self):
        for manager, own, foreign in (
            (self.manager_a, self.finance_a, self.finance_b),
            (self.manager_b, self.finance_b, self.finance_a),
        ):
            client = APIClient()
            client.force_authenticate(manager)
            listing = client.get("/api/accounts/users/?organization_id=%s" % foreign.organization_id)
            self.assertEqual(listing.status_code, 200)
            ids = {row["id"] for row in listing.data["results"]}
            self.assertIn(own.pk, ids)
            self.assertNotIn(foreign.pk, ids)
            self.assertEqual(client.get(self.detail_url(own)).status_code, 200)
            self.assertEqual(client.get(self.detail_url(foreign)).status_code, 404)

    def test_agent_autocomplete_is_paginated_and_organization_scoped(self):
        agent_a = self.make_user(
            "awa-agent@example.test", User.Role.AGENT, self.org_a,
            first_name="Awa", last_name="Diop",
        )
        agent_b = self.make_user(
            "awa-foreign@example.test", User.Role.AGENT, self.org_b,
            first_name="Awa", last_name="Ba",
        )

        response = self.client.get(
            "/api/accounts/agents/?search=Awa&page=1&page_size=1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], agent_a.pk)

        foreign = self.client.get(
            f"/api/accounts/agents/?search={agent_b.email}&page=1&page_size=20"
        )
        self.assertEqual(foreign.status_code, 200)
        self.assertEqual(foreign.data["count"], 0)
        client_b = APIClient()
        client_b.force_authenticate(self.manager_b)
        reverse = client_b.get("/api/accounts/agents/?search=Awa&page=1&page_size=20")
        self.assertEqual(reverse.status_code, 200)
        self.assertEqual(reverse.data["count"], 1)
        self.assertEqual(reverse.data["results"][0]["id"], agent_b.pk)

    def test_manager_cannot_read_or_modify_foreign_users(self):
        for actor, foreign in ((self.manager_a, self.manager_b), (self.manager_b, self.manager_a)):
            client = APIClient()
            client.force_authenticate(actor)
            before = (foreign.first_name, foreign.last_name, foreign.role, foreign.organization_id)
            for method, payload in (
                ("get", None),
                ("put", {"first_name": "Changed", "last_name": "User"}),
                ("patch", {"first_name": "Changed"}),
                ("delete", None),
            ):
                with self.subTest(actor=actor.email, method=method):
                    response = getattr(client, method)(
                        self.detail_url(foreign), payload, format="json"
                    ) if payload is not None else getattr(client, method)(self.detail_url(foreign))
                    self.assertIn(response.status_code, (403, 404, 405))
            foreign.refresh_from_db()
            self.assertEqual(
                (foreign.first_name, foreign.last_name, foreign.role, foreign.organization_id),
                before,
            )

    def test_manager_can_edit_same_org_profile_and_invalid_values_are_rejected(self):
        invalid = self.client.patch(
            self.detail_url(self.finance_a),
            {"first_name": "12345", "phone": "abcdef"},
            format="json",
        )
        self.assertEqual(invalid.status_code, 400)
        self.finance_a.refresh_from_db()
        self.assertEqual(self.finance_a.first_name, "Test")

        valid = self.client.patch(
            self.detail_url(self.finance_a),
            {"first_name": "Aminata", "last_name": "Diallo"},
            format="json",
        )
        self.assertEqual(valid.status_code, 200)
        self.finance_a.refresh_from_db()
        self.assertEqual(self.finance_a.first_name, "Aminata")
        self.assertEqual(self.finance_a.last_name, "Diallo")

    def test_status_endpoint_parses_boolean_false_without_treating_it_as_true(self):
        response = self.client.patch(
            self.detail_url(self.finance_a), {"is_active": "false"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.finance_a.refresh_from_db()
        self.assertFalse(self.finance_a.is_active)

    def test_put_and_patch_reject_role_and_organization_changes(self):
        attempts = (
            {"role": User.Role.SUPER_ADMIN},
            {"organization": self.org_b.pk},
            {"organization_id": self.org_b.pk},
            {"is_staff": True},
            {"is_superuser": True},
            {"is_super_admin": True},
        )
        for payload in attempts:
            for method in ("put", "patch"):
                with self.subTest(method=method, payload=payload):
                    body = {"first_name": "Test", "last_name": "User", **payload}
                    response = getattr(self.client, method)(
                        self.detail_url(self.manager_a), body, format="json"
                    )
                    self.assertEqual(response.status_code, 400)
        self.manager_a.refresh_from_db()
        self.assertEqual(self.manager_a.role, User.Role.GERANT)
        self.assertEqual(self.manager_a.organization, self.org_a)
        self.assertFalse(self.manager_a.is_staff)
        self.assertFalse(self.manager_a.is_superuser)

    def test_manager_cannot_promote_another_user_to_super_admin(self):
        response = self.client.put(
            self.detail_url(self.finance_a),
            {
                "first_name": "Test",
                "last_name": "User",
                "role": User.Role.SUPER_ADMIN,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.finance_a.refresh_from_db()
        self.assertEqual(self.finance_a.role, User.Role.FINANCE)

    def test_create_user_rejects_client_organization_and_super_admin_role(self):
        from unittest.mock import patch

        foreign_org_response = self.client.post(
            "/api/accounts/users/create/",
            {
                "first_name": "New",
                "last_name": "Agent",
                "email": "new-agent@example.test",
                "phone": "+221700000003",
                "role": User.Role.AGENT,
                "organization": self.org_b.pk,
            },
            format="json",
        )
        self.assertEqual(foreign_org_response.status_code, 400)
        self.assertFalse(User.objects.filter(email="new-agent@example.test").exists())

        with patch("apps.accounts.services.send_invitation_email.delay"):
            response = self.client.post(
                "/api/accounts/users/create/",
                {
                    "first_name": "New",
                    "last_name": "Agent",
                    "email": "new-agent@example.test",
                    "phone": "+221700000003",
                    "role": User.Role.AGENT,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201)
        created = User.objects.get(email="new-agent@example.test")
        self.assertEqual(created.organization, self.org_a)

        response = self.client.post(
            "/api/accounts/users/create/",
            {
                "first_name": "New",
                "last_name": "Admin",
                "email": "new-admin@example.test",
                "phone": "+221700000004",
                "role": User.Role.SUPER_ADMIN,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="new-admin@example.test").exists())

    def test_non_manager_cannot_manage_users(self):
        self.client.force_authenticate(self.finance_a)
        response = self.client.patch(
            self.detail_url(self.manager_a), {"status": User.Status.SUSPENDED}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_old_access_and_refresh_tokens_are_refused_after_suspension(self):
        client, refresh = self.jwt_client(self.manager_a)
        self.assertEqual(client.get("/api/accounts/me/").status_code, 200)
        self.manager_a.status = User.Status.SUSPENDED
        # Keep is_active true so these endpoints must check the current status.
        self.manager_a.save(update_fields=["status"])

        for method, url, data in (
            (client.get, "/api/accounts/me/", None),
            (client.get, "/api/accounts/users/", None),
            (client.get, "/api/accounts/agents/", None),
            (client.get, "/api/accounts/notifications/", None),
            (client.post, "/api/accounts/notifications/00000000-0000-0000-0000-000000000001/read/", {}),
            (client.post, "/api/accounts/change-password/", {
                "current_password": "SafePass123!",
                "new_password": "NewStrongPass123!",
                "new_password_confirm": "NewStrongPass123!",
            }),
        ):
            response = method(url, data, format="json") if data is not None else method(url)
            self.assertIn(response.status_code, (401, 403), (url, response.status_code))

        for url in ("/api/accounts/refresh/", "/api/token/refresh/"):
            response = self.client.post(url, {"refresh": refresh}, format="json")
            self.assertIn(response.status_code, (401, 400), (url, response.status_code))
        self.manager_a.refresh_from_db()
        self.assertEqual(self.manager_a.status, User.Status.SUSPENDED)
        self.assertTrue(self.manager_a.is_active)

    def test_all_organization_roles_lose_old_jwt_access_when_suspended_by_manager(self):
        users = (
            self.make_user("stale-chef@example.test", User.Role.CHEF_PROJET, self.org_a),
            self.make_user("stale-finance@example.test", User.Role.FINANCE, self.org_a),
            self.make_user("stale-agent@example.test", User.Role.AGENT, self.org_a),
        )
        clients = [(user, *self.jwt_client(user)) for user in users]
        for user, client, _refresh in clients:
            response = self.client.patch(
                self.detail_url(user), {"status": User.Status.SUSPENDED}, format="json"
            )
            self.assertEqual(response.status_code, 200)
            for url in ("/api/accounts/me/", "/api/accounts/notifications/"):
                self.assertIn(client.get(url).status_code, (401, 403))

    def test_resend_activation_does_not_enumerate_accounts(self):
        from unittest.mock import patch

        pending = User.objects.create_user(
            email="pending@example.test", password="SafePass123!",
            first_name="Pending", last_name="User", role=User.Role.AGENT,
            organization=self.org_a, status=User.Status.INVITED, is_active=False,
        )
        suspended = self.make_user("suspended@example.test", User.Role.AGENT, self.org_a)
        suspended.status = User.Status.SUSPENDED
        suspended.is_active = False
        suspended.save(update_fields=["status", "is_active"])
        responses = []
        with patch("apps.accounts.tasks.send_invitation_email.delay") as send_email:
            for email in (pending.email, "absent@example.test", self.manager_a.email, suspended.email):
                responses.append(self.client.post(
                    "/api/accounts/resend-activation/", {"email": email}, format="json"
                ))
        self.assertEqual({response.status_code for response in responses}, {200})
        self.assertTrue(all(response.data == responses[0].data for response in responses))
        send_email.assert_called_once()

    def test_password_reset_cannot_change_password_of_suspended_account(self):
        payload = {
            "uid": str(self.manager_a.pk),
            "reset_token": default_token_generator.make_token(self.manager_a),
        }
        token = signing.dumps(payload, salt="barakagive.password-reset")
        old_password_hash = self.manager_a.password
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])
        response = self.client.post(
            "/api/accounts/password-reset/confirm/",
            {
                "token": token,
                "password": "NewStrongPass123!",
                "password_confirm": "NewStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.manager_a.refresh_from_db()
        self.assertEqual(self.manager_a.password, old_password_hash)

    def test_notification_ids_are_recipient_and_organization_scoped(self):
        notification_a = InAppNotification.objects.create(
            recipient=self.manager_a, organization=self.org_a,
            title="A only", message="A message",
        )
        notification_b = InAppNotification.objects.create(
            recipient=self.manager_b, organization=self.org_b,
            title="B only", message="B message",
        )
        for user, own, foreign in (
            (self.manager_a, notification_a, notification_b),
            (self.manager_b, notification_b, notification_a),
        ):
            client = APIClient()
            client.force_authenticate(user)
            listing = client.get("/api/accounts/notifications/")
            self.assertEqual(listing.status_code, 200)
            self.assertEqual([row["id"] for row in listing.data["results"]], [str(own.pk)])
            denied = client.post(
                f"/api/accounts/notifications/{foreign.pk}/read/", {}, format="json"
            )
            self.assertEqual(denied.status_code, 404)
        notification_a.refresh_from_db()
        notification_b.refresh_from_db()
        self.assertIsNone(notification_a.read_at)
        self.assertIsNone(notification_b.read_at)

    def test_notification_routes_reject_unsupported_methods_without_mutation(self):
        notification = InAppNotification.objects.create(
            recipient=self.manager_a, organization=self.org_a,
            title="A only", message="A message",
        )
        url = f"/api/accounts/notifications/{notification.pk}/read/"
        for method, path, data in (
            (self.client.post, "/api/accounts/notifications/", {}),
            (self.client.put, "/api/accounts/notifications/", {}),
            (self.client.patch, "/api/accounts/notifications/", {}),
            (self.client.delete, "/api/accounts/notifications/", None),
            (self.client.get, url, None),
            (self.client.put, url, {}),
            (self.client.patch, url, {}),
            (self.client.delete, url, None),
        ):
            response = method(path, data, format="json") if data is not None else method(path)
            self.assertEqual(response.status_code, 405, (method.__name__, path))
        notification.refresh_from_db()
        self.assertIsNone(notification.read_at)

    def test_both_notification_url_prefixes_allow_each_tenant_to_read_own_item(self):
        for user, organization, title in (
            (self.manager_a, self.org_a, "A private"),
            (self.manager_b, self.org_b, "B private"),
        ):
            notification = InAppNotification.objects.create(
                recipient=user, organization=organization,
                title=title, message="Private message",
            )
            client = APIClient()
            client.force_authenticate(user)
            for prefix in ("/api/accounts", "/api/auth"):
                listing = client.get(f"{prefix}/notifications/")
                self.assertEqual(listing.status_code, 200)
                self.assertIn(str(notification.pk), {row["id"] for row in listing.data["results"]})
            marked = client.post(
                f"/api/auth/notifications/{notification.pk}/read/", {}, format="json"
            )
            self.assertEqual(marked.status_code, 200)
            self.assertTrue(marked.data["read"])
            notification.refresh_from_db()
            self.assertIsNotNone(notification.read_at)

    def test_notification_api_excludes_recipient_with_foreign_organization_field(self):
        inconsistent = InAppNotification.objects.create(
            recipient=self.manager_a, organization=self.org_b,
            title="Incohérente", message="Ne doit pas être visible",
        )
        response = self.client.get("/api/accounts/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(str(inconsistent.pk), {row["id"] for row in response.data["results"]})
        response = self.client.post(
            f"/api/accounts/notifications/{inconsistent.pk}/read/", {}, format="json"
        )
        self.assertEqual(response.status_code, 404)
        inconsistent.refresh_from_db()
        self.assertIsNone(inconsistent.read_at)

    def test_super_admin_has_no_cross_organization_notification_access(self):
        notification = InAppNotification.objects.create(
            recipient=self.manager_a, organization=self.org_a,
            title="A only", message="A message",
        )
        admin = self.make_user(
            "notification-admin@example.test", User.Role.SUPER_ADMIN, None,
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(admin)
        response = client.get("/api/accounts/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])
        denied = client.post(
            f"/api/accounts/notifications/{notification.pk}/read/", {}, format="json"
        )
        self.assertEqual(denied.status_code, 404)
        notification.refresh_from_db()
        self.assertIsNone(notification.read_at)

    def test_suspended_old_jwt_cannot_trigger_assistant_notifications(self):
        client, _refresh = self.jwt_client(self.manager_a)
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])

        response = client.post(
            "/api/assistant/chat/",
            {"question": "notifie les chefs des projets en retard"},
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(InAppNotification.objects.filter(recipient__organization=self.org_a).exists())

    def test_super_admin_global_gérant_list_and_manager_only_routes(self):
        admin = self.make_user(
            "admin-global@example.test", User.Role.SUPER_ADMIN, None,
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(admin)
        response = client.get("/api/accounts/gerants/")
        self.assertEqual(response.status_code, 200)
        listed = {row["id"] for row in response.data}
        self.assertEqual(listed, {self.manager_a.pk, self.manager_b.pk})
        self.assertEqual(client.get("/api/accounts/users/").status_code, 403)
        self.assertEqual(client.get(self.detail_url(self.manager_a)).status_code, 403)

    def test_super_admin_retains_existing_cross_organization_manager_list(self):
        admin = self.make_user(
            "admin@example.test",
            User.Role.SUPER_ADMIN,
            None,
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(admin)
        response = self.client.get("/api/accounts/gerants/")
        self.assertEqual(response.status_code, 200)
        listed_ids = {row["id"] for row in response.data}
        self.assertIn(self.manager_a.pk, listed_ids)
        self.assertIn(self.manager_b.pk, listed_ids)

    def test_password_reset_request_is_non_enumerating_and_queues_known_account(self):
        from unittest.mock import patch

        with patch("apps.accounts.tasks.send_invitation_email.delay") as send_email:
            known = self.client.post(
                "/api/accounts/password-reset/",
                {"email": self.manager_a.email},
                format="json",
            )
            unknown = self.client.post(
                "/api/accounts/password-reset/",
                {"email": "absent@example.test"},
                format="json",
            )
        self.assertEqual(known.status_code, 200)
        self.assertEqual(unknown.status_code, 200)
        self.assertEqual(known.data, unknown.data)
        send_email.assert_called_once()

    def test_password_reset_confirm_requires_valid_token_and_changes_password(self):
        payload = {
            "uid": str(self.manager_a.pk),
            "reset_token": default_token_generator.make_token(self.manager_a),
        }
        token = signing.dumps(payload, salt="barakagive.password-reset")
        response = self.client.post(
            "/api/accounts/password-reset/confirm/",
            {
                "token": token,
                "password": "NewStrongPass123!",
                "password_confirm": "NewStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.manager_a.refresh_from_db()
        self.assertTrue(self.manager_a.check_password("NewStrongPass123!"))

        replay = self.client.post(
            "/api/accounts/password-reset/confirm/",
            {
                "token": token,
                "password": "AnotherStrongPass123!",
                "password_confirm": "AnotherStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(replay.status_code, 400)
