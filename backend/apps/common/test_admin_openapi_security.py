from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory

from apps.accounts.models import User
from apps.beneficiaries.models import Beneficiary, FormResponse
from apps.campaigns.models import Campaign
from apps.finance.models import Budget, Depense, Don, Financement, Justification
from apps.forms.models import Formulaire
from apps.organizations.models import Organization, OrganisationRequest
from apps.projects.models import Project
from apps.zones.models import Zone


class AdminAndOpenAPISecurityTests(TestCase):
    protected_models = (
        User, Organization, OrganisationRequest, Project, Campaign, Beneficiary,
        FormResponse, Budget, Depense, Don, Financement, Justification,
        Formulaire, Zone,
    )

    def setUp(self):
        self.org_a = Organization.objects.create(
            name="Admin ONG A", email="admin-a@example.test", phone="771230101",
            address="Dakar", region="Dakar",
        )
        self.org_b = Organization.objects.create(
            name="Admin ONG B", email="admin-b@example.test", phone="771230102",
            address="Thies", region="Thies",
        )
        self.manager_a = self._user(
            "admin-manager-a@example.test", User.Role.GERANT, self.org_a,
            is_staff=True, is_superuser=True,
        )
        self.manager_b = self._user(
            "admin-manager-b@example.test", User.Role.GERANT, self.org_b,
            is_staff=True,
        )
        self.super_admin = self._user(
            "admin-super@example.test", User.Role.SUPER_ADMIN, None,
            is_staff=True,
        )
        self.suspended_super_admin = self._user(
            "admin-suspended-super@example.test", User.Role.SUPER_ADMIN, None,
            is_staff=True, status=User.Status.SUSPENDED,
        )
        self.client = APIClient()

    @staticmethod
    def _user(email, role, organization, **kwargs):
        return User.objects.create_user(
            email=email, password="SafePass123!", first_name="Admin", last_name="Audit",
            role=role, organization=organization, status=kwargs.pop("status", User.Status.ACTIVE),
            is_active=True, **kwargs,
        )

    def test_registered_tenant_admins_deny_every_non_super_admin_role(self):
        request_factory = APIRequestFactory()
        for user in (self.manager_a, self.manager_b):
            request = request_factory.get("/admin/")
            request.user = user
            for model in self.protected_models:
                with self.subTest(user=user.email, model=model._meta.label):
                    model_admin = admin.site._registry[model]
                    self.assertFalse(model_admin.has_module_permission(request))
                    self.assertFalse(model_admin.has_view_permission(request))
                    self.assertFalse(model_admin.has_add_permission(request))
                    self.assertFalse(model_admin.has_change_permission(request))
                    self.assertFalse(model_admin.has_delete_permission(request))
                    self.assertFalse(model_admin.get_queryset(request).exists())

    def test_admin_model_routes_block_staff_and_django_superuser_without_super_admin_role(self):
        for user in (self.manager_a, self.manager_b):
            self.client.force_login(user)
            self.assertEqual(self.client.get("/admin/").status_code, 403)
            for url in (
                reverse("admin:accounts_user_changelist"),
                reverse("admin:auth_group_changelist"),
                reverse("admin:organizations_organization_changelist"),
                reverse("admin:projects_project_changelist"),
                reverse("admin:campaigns_campaign_changelist"),
                reverse("admin:beneficiaries_beneficiary_changelist"),
                reverse("admin:finance_depense_changelist"),
                reverse("admin:forms_formulaire_changelist"),
                reverse("admin:zones_zone_changelist"),
            ):
                with self.subTest(user=user.email, url=url):
                    self.assertEqual(self.client.get(url).status_code, 403)

    def test_active_super_admin_has_global_admin_access_but_suspended_one_does_not(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse("admin:organizations_organization_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.org_a.name)
        self.assertContains(response, self.org_b.name)

        self.client.force_login(self.suspended_super_admin)
        self.assertEqual(
            self.client.get(reverse("admin:organizations_organization_changelist")).status_code,
            403,
        )

    def test_user_admin_does_not_let_role_super_admin_grant_django_superuser_flags(self):
        model_admin = admin.site._registry[User]
        request = APIRequestFactory().get("/admin/accounts/user/")
        request.user = self.super_admin
        readonly = set(model_admin.get_readonly_fields(request))
        self.assertTrue({"is_superuser", "is_staff", "groups", "user_permissions"}.issubset(readonly))
        self.assertTrue(model_admin.has_add_permission(request))
        self.assertTrue(model_admin.has_change_permission(request))

    def test_openapi_and_swagger_require_an_active_super_admin(self):
        for url in ("/api/schema/", "/api/swagger/"):
            with self.subTest(url=url, actor="anonymous"):
                self.client.force_authenticate(user=None)
                self.assertIn(self.client.get(url).status_code, (401, 403))

            self.client.force_authenticate(self.manager_a)
            with self.subTest(url=url, actor="ONG A"):
                self.assertEqual(self.client.get(url).status_code, 403)

            self.client.force_authenticate(self.manager_b)
            with self.subTest(url=url, actor="ONG B"):
                self.assertEqual(self.client.get(url).status_code, 403)

            self.client.force_authenticate(self.suspended_super_admin)
            with self.subTest(url=url, actor="SUPER_ADMIN suspendu"):
                self.assertEqual(self.client.get(url).status_code, 403)

            self.client.force_authenticate(self.super_admin)
            with self.subTest(url=url, actor="SUPER_ADMIN actif"):
                self.assertEqual(self.client.get(url).status_code, 200)
