from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.organizations.models import Organization
from .models import Subscription, Transaction
from .webhooks import handle_cancelled_payment, handle_failed_payment, process_paytech_webhook


class PaymentTenantIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="ONG Paiement A", email="payment-a@example.test", phone="770000091",
            address="Dakar", region="Dakar", intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG Paiement B", email="payment-b@example.test", phone="770000092",
            address="Thiès", region="Thiès", intervention_domain="Humanitaire",
        )
        self.manager_a = self.make_user("payment-manager-a@example.test", User.Role.GERANT, self.org_a)
        self.manager_b = self.make_user("payment-manager-b@example.test", User.Role.GERANT, self.org_b)
        self.subscription_a = Subscription.objects.create(
            ong=self.org_a, statut=Subscription.Statut.TRIAL, is_active=True,
        )
        self.subscription_b = Subscription.objects.create(
            ong=self.org_b, statut=Subscription.Statut.TRIAL, is_active=True,
        )
        self.transaction_a = self.make_transaction(self.subscription_a, "TXN-ORG-A-01")
        self.transaction_b = self.make_transaction(self.subscription_b, "TXN-ORG-B-01")

    @staticmethod
    def make_user(email, role, organization):
        return User.objects.create_user(
            email=email, password="SafePass123!", role=role,
            status=User.Status.ACTIVE, is_active=True, organization=organization,
        )

    @staticmethod
    def make_transaction(subscription, transaction_id):
        return Transaction.objects.create(
            subscription=subscription, montant=subscription.prix,
            transaction_id=transaction_id, statut=Transaction.Statut.PENDING,
        )

    @staticmethod
    def jwt_client(user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client

    def test_each_manager_reads_only_own_subscription_and_transactions(self):
        for manager, own_transaction, foreign_transaction in (
            (self.manager_a, self.transaction_a, self.transaction_b),
            (self.manager_b, self.transaction_b, self.transaction_a),
        ):
            client = APIClient()
            client.force_authenticate(manager)
            for path in (
                "/api/payment/subscription/",
                "/api/payment/subscription/detail/",
                "/api/payment/subscription/check/",
            ):
                response = client.get(path)
                self.assertEqual(response.status_code, 200, (manager.email, path))
            history = client.get("/api/payment/history/")
            self.assertEqual(history.status_code, 200)
            transaction_ids = {item["transaction_id"] for item in history.data}
            self.assertEqual(transaction_ids, {own_transaction.transaction_id})
            self.assertNotIn(foreign_transaction.transaction_id, transaction_ids)

    @patch("apps.payment.views.paytech_service.create_payment")
    def test_payment_initiation_uses_authenticated_tenant_and_ignores_foreign_ids(self, create_payment):
        create_payment.return_value = {
            "payment_url": "https://paytech.invalid/checkout/test",
            "transaction_id": "TXN-ORG-A-NEW",
        }
        client = APIClient()
        client.force_authenticate(self.manager_a)
        response = client.post("/api/payment/subscribe/", {
            "organization_id": self.org_b.pk,
            "project_id": 999999,
            "campaign_id": 999999,
            "donor_id": 999999,
            "financement_id": 999999,
            "payment_id": str(self.transaction_b.pk),
        }, format="json")
        self.assertEqual(response.status_code, 201)
        create_payment.assert_called_once_with(self.subscription_a)
        self.transaction_b.refresh_from_db()
        self.subscription_b.refresh_from_db()
        self.assertEqual(self.transaction_b.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_b.statut, Subscription.Statut.TRIAL)

    @patch("apps.payment.services.requests.post")
    def test_provider_request_amount_comes_from_own_subscription(self, post):
        class ProviderResponse:
            status_code = 200

            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"token": "mock-checkout-token"}

        post.return_value = ProviderResponse()
        from .services import PayTechService

        service = PayTechService()
        service.create_payment(self.subscription_a)
        sent_payload = post.call_args.kwargs["data"]
        self.assertEqual(sent_payload["item_price"], str(int(self.subscription_a.prix)))
        self.assertEqual(sent_payload["currency"], "XOF")
        self.assertEqual(sent_payload["ref_command"].split("-")[1], str(self.org_a.pk))

    def test_payment_routes_reject_unsupported_methods_without_mutation(self):
        client = APIClient()
        client.force_authenticate(self.manager_a)
        get_routes = (
            "/api/payment/subscription/",
            "/api/payment/subscription/detail/",
            "/api/payment/subscription/check/",
            "/api/payment/history/",
            "/api/payment/admin/subscriptions/",
            f"/api/payment/admin/subscriptions/{self.subscription_a.pk}/",
        )
        post_routes = (
            "/api/payment/subscribe/",
            "/api/payment/webhook/",
            f"/api/payment/admin/subscriptions/{self.subscription_a.pk}/suspend/",
            f"/api/payment/admin/subscriptions/{self.subscription_a.pk}/reactivate/",
        )
        for path in get_routes:
            for method in (client.post, client.put, client.patch, client.delete):
                response = method(path, {}, format="json")
                self.assertEqual(response.status_code, 405, (method.__name__, path))
        for path in post_routes:
            for method in (client.get, client.put, client.patch, client.delete):
                response = method(path)
                self.assertEqual(response.status_code, 405, (method.__name__, path))
        self.transaction_a.refresh_from_db()
        self.transaction_b.refresh_from_db()
        self.subscription_a.refresh_from_db()
        self.subscription_b.refresh_from_db()
        self.assertEqual(self.transaction_a.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.transaction_b.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_a.statut, Subscription.Statut.TRIAL)
        self.assertEqual(self.subscription_b.statut, Subscription.Statut.TRIAL)

    def test_suspended_manager_old_jwt_cannot_read_or_initiate_payment(self):
        client = self.jwt_client(self.manager_a)
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])

        with patch("apps.payment.views.paytech_service.create_payment") as create_payment:
            for path in (
                "/api/payment/subscription/",
                "/api/payment/subscription/detail/",
                "/api/payment/history/",
                "/api/payment/subscription/check/",
            ):
                self.assertIn(client.get(path).status_code, (401, 403), path)
            response = client.post("/api/payment/subscribe/", {}, format="json")
            self.assertIn(response.status_code, (401, 403))
            create_payment.assert_not_called()

        self.subscription_a.refresh_from_db()
        self.assertEqual(self.subscription_a.statut, Subscription.Statut.TRIAL)
        self.assertFalse(Transaction.objects.filter(subscription=self.subscription_a).exclude(pk=self.transaction_a.pk).exists())

    def test_suspended_super_admin_old_jwt_cannot_manage_subscriptions(self):
        admin = self.make_user("payment-admin@example.test", User.Role.SUPER_ADMIN, None)
        client = self.jwt_client(admin)
        admin.status = User.Status.SUSPENDED
        admin.save(update_fields=["status"])

        detail = f"/api/payment/admin/subscriptions/{self.subscription_a.pk}/"
        for method, path, body in (
            (client.get, "/api/payment/admin/subscriptions/", None),
            (client.get, detail, None),
            (client.post, f"{detail}suspend/", {}),
            (client.post, f"{detail}reactivate/", {}),
        ):
            response = method(path, body, format="json") if body is not None else method(path)
            self.assertIn(response.status_code, (401, 403), path)
        self.subscription_a.refresh_from_db()
        self.assertEqual(self.subscription_a.statut, Subscription.Statut.TRIAL)

    @patch("apps.payment.views.paytech_service.verify_payment")
    def test_public_webhook_requires_provider_confirmation_and_is_idempotent(self, verify_payment):
        verify_payment.return_value = {"success": 0, "message": "pending"}
        client = APIClient()
        response = client.post("/api/payment/webhook/", {
            "ref_command": self.transaction_b.transaction_id,
            "status": "success",
            "organization_id": self.org_a.pk,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        verify_payment.assert_called_once_with(self.transaction_b.transaction_id)
        self.transaction_b.refresh_from_db()
        self.subscription_b.refresh_from_db()
        self.assertEqual(self.transaction_b.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_b.statut, Subscription.Statut.TRIAL)

        verify_payment.return_value = {"success": 1, "ref_command": self.transaction_b.transaction_id}
        response = client.post("/api/payment/webhook/", {
            "transaction_id": self.transaction_b.transaction_id,
            "status": "success",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.transaction_b.refresh_from_db()
        self.transaction_a.refresh_from_db()
        self.subscription_b.refresh_from_db()
        self.subscription_a.refresh_from_db()
        self.assertEqual(self.transaction_b.statut, Transaction.Statut.SUCCESS)
        self.assertEqual(self.subscription_b.statut, Subscription.Statut.ACTIVE)
        self.assertEqual(self.transaction_a.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_a.statut, Subscription.Statut.TRIAL)

    @patch("apps.payment.webhooks.paytech_service.verify_payment")
    def test_unrouted_webhook_helper_does_not_trust_client_success_status(self, verify_payment):
        verify_payment.return_value = {"success": 0, "message": "pending"}
        result = process_paytech_webhook({
            "transaction_id": self.transaction_b.transaction_id,
            "status": "success",
        })
        self.assertFalse(result["success"])
        verify_payment.assert_called_once_with(self.transaction_b.transaction_id)
        self.transaction_b.refresh_from_db()
        self.subscription_b.refresh_from_db()
        self.assertEqual(self.transaction_b.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_b.statut, Subscription.Statut.TRIAL)

    def test_webhook_verification_outage_and_unverified_negative_helpers_do_not_mutate(self):
        client = APIClient()
        with patch("apps.payment.views.paytech_service.verify_payment") as verify_payment:
            verify_payment.return_value = {"success": 0, "verification_unavailable": True}
            response = client.post("/api/payment/webhook/", {
                "ref_command": self.transaction_a.transaction_id,
                "status": "failed",
            }, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(handle_failed_payment(self.transaction_a, {"status": "failed"})["success"])
        self.assertFalse(handle_cancelled_payment(self.transaction_a, {"status": "cancelled"})["success"])
        self.transaction_a.refresh_from_db()
        self.subscription_a.refresh_from_db()
        self.assertEqual(self.transaction_a.statut, Transaction.Statut.PENDING)
        self.assertEqual(self.subscription_a.statut, Subscription.Statut.TRIAL)

    def test_super_admin_access_is_explicitly_global(self):
        admin = self.make_user("payment-admin-active@example.test", User.Role.SUPER_ADMIN, None)
        client = APIClient()
        client.force_authenticate(admin)
        listing = client.get("/api/payment/admin/subscriptions/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual({row["id"] for row in listing.data}, {
            str(self.subscription_a.pk), str(self.subscription_b.pk),
        })
        detail = client.get(f"/api/payment/admin/subscriptions/{self.subscription_b.pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["ong_nom"], self.org_b.name)
