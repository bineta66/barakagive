from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.ia.views import compute_finance_payload as compute_view_payload
from apps.ia.tasks import compute_finance_payload as compute_task_payload


class EmptyQuerySet(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.filter_calls = []

    def select_related(self, *fields):
        return self

    def filter(self, *args, **kwargs):
        self.filter_calls.append((args, kwargs))
        return self

    def distinct(self):
        return self


class FinancePayloadOrganizationTests(SimpleTestCase):
    def setUp(self):
        self.organization = SimpleNamespace(pk=41)
        self.project = SimpleNamespace(pk=52)
        self.campaign = SimpleNamespace(
            id="campaign-a",
            projet=self.project,
            organization=self.organization,
            organization_id=self.organization.pk,
            nom="Campagne A",
            date_fin=date(2030, 1, 1),
        )

    @patch("apps.ia.views.Depense.objects.filter", return_value=EmptyQuerySet())
    @patch("apps.ia.views.Budget.objects.filter", return_value=EmptyQuerySet())
    def test_user_finance_payload_filters_by_campaign_and_organization(self, budgets, expenses):
        compute_view_payload(self.campaign, user=None)
        budgets.assert_called_once_with(
            projet=self.project, organization_id=self.organization.pk,
        )
        expenses.assert_called_once_with(
            organization_id=self.organization.pk,
        )
        self.assertEqual(len(expenses.return_value.filter_calls), 1)
        self.assertTrue(expenses.return_value.filter_calls[0][0])

    @patch("apps.ia.tasks.Depense.objects.filter", return_value=EmptyQuerySet())
    @patch("apps.ia.tasks.Budget.objects.filter", return_value=EmptyQuerySet())
    def test_scheduled_finance_payload_filters_by_campaign_and_organization(self, budgets, expenses):
        compute_task_payload(self.campaign)
        budgets.assert_called_once_with(
            projet=self.project, organization_id=self.organization.pk,
        )
        expenses.assert_called_once()
        expense_filter_args, expense_filter_kwargs = expenses.call_args
        self.assertEqual(expense_filter_kwargs, {"organization_id": self.organization.pk})
        self.assertEqual(len(expense_filter_args), 2)
        self.assertIn("projet", str(expense_filter_args[0]))
        self.assertIn("organization_id", str(expense_filter_args[1]))
        self.assertIn("budget__projet__organization_id", str(expense_filter_args[1]))
        self.assertIn("campagne__projet__organization_id", str(expense_filter_args[1]))
        self.assertEqual(expenses.return_value.filter_calls, [])
