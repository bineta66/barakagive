from unittest.mock import patch

from django.test import TestCase

from apps.accounts.models import User
from apps.organizations.models import Organization, Subscription as OrganizationSubscription
from apps.payment.models import Subscription
from apps.payment.tasks import send_subscription_reminder


class SubscriptionReminderTenantIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="ONG rappel A", email="reminder-a@example.test", phone="770000081",
            address="Dakar", region="Dakar", intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG rappel B", email="reminder-b@example.test", phone="770000082",
            address="Thiès", region="Thiès", intervention_domain="Humanitaire",
        )
        self.manager_a = User.objects.create_user(
            email="reminder-manager-a@example.test", password="SafePass123!",
            role=User.Role.GERANT, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_a,
        )
        self.manager_b = User.objects.create_user(
            email="reminder-manager-b@example.test", password="SafePass123!",
            role=User.Role.GERANT, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_b,
        )
        Subscription.objects.create(ong=self.org_a)
        Subscription.objects.create(ong=self.org_b)
        OrganizationSubscription.objects.create(organization=self.org_a)
        OrganizationSubscription.objects.create(organization=self.org_b)

    @patch("apps.accounts.tasks.send_invitation_email.delay")
    def test_reminder_resolves_only_manager_in_requested_organization(self, enqueue_email):
        send_subscription_reminder(
            self.manager_b.pk, 3, is_trial=True, organization_id=self.org_a.pk,
        )

        enqueue_email.assert_not_called()

    @patch("apps.accounts.tasks.send_invitation_email.delay")
    def test_reminder_for_suspended_manager_is_dropped(self, enqueue_email):
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])

        send_subscription_reminder(
            self.manager_a.pk, 3, is_trial=True, organization_id=self.org_a.pk,
        )

        enqueue_email.assert_not_called()

    @patch("apps.accounts.tasks.send_invitation_email.delay")
    def test_valid_manager_gets_only_own_organization_reminder(self, enqueue_email):
        send_subscription_reminder(
            self.manager_b.pk, 1, is_trial=False, organization_id=self.org_b.pk,
        )

        enqueue_email.assert_called_once()
        self.assertEqual(
            enqueue_email.call_args.kwargs["recipient_email"],
            self.manager_b.email,
        )
