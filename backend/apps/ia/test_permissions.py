from unittest.mock import Mock, patch
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.organizations.models import Organization


class IARoleGateTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def authenticate_as(self, role):
        user = User(
            id=1,
            email="role@example.test",
            role=role,
            organization=Organization(id=10, name="ONG test"),
            is_active=True,
        )
        self.client.force_authenticate(user)

    def test_agent_cannot_access_strategic_dashboard(self):
        self.authenticate_as(User.Role.AGENT)
        response = self.client.get("/api/assistant/dashboard/")
        self.assertEqual(response.status_code, 403)

    def test_project_lead_cannot_access_financial_analysis_endpoint(self):
        self.authenticate_as(User.Role.CHEF_PROJET)
        response = self.client.get(
            "/api/ia/budget-analysis/00000000-0000-0000-0000-000000000001"
        )
        self.assertEqual(response.status_code, 403)

    def test_agent_cannot_trigger_global_region_analysis(self):
        self.authenticate_as(User.Role.AGENT)
        response = self.client.post("/api/ia/regions/Dakar/analyze-ia")
        self.assertEqual(response.status_code, 403)

    def test_finance_role_cannot_read_beneficiary_zone_analysis(self):
        self.authenticate_as(User.Role.FINANCE)
        response = self.client.get("/api/ia/regions/Dakar/analysis")
        self.assertEqual(response.status_code, 403)

    def test_project_lead_cannot_read_organization_finance_assistant(self):
        self.authenticate_as(User.Role.CHEF_PROJET)
        response = self.client.get("/api/finance/assistant/home/")
        self.assertEqual(response.status_code, 403)

    def test_project_lead_cannot_request_global_campaign_budget_analysis(self):
        self.authenticate_as(User.Role.CHEF_PROJET)
        response = self.client.get(
            "/api/finance/ia/budget-analysis/00000000-0000-0000-0000-000000000001/"
        )
        self.assertEqual(response.status_code, 403)

    def test_agent_cannot_request_finance_report_from_client_supplied_data(self):
        self.authenticate_as(User.Role.AGENT)
        response = self.client.post(
            "/api/ia/rapport/generate",
            {"dashboard": {"solde": 999999999}},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(IA_SERVICE_URL="http://ia_service:8001", AI_SERVICE_TOKEN="internal-test", AI_CONTEXT_SIGNING_KEY="test-context-key")
    @patch("apps.finance.views.build_finance_chat_context", return_value={"finances": {"budget_total": 125}})
    @patch("apps.finance.views.requests.post")
    def test_finance_report_ignores_client_payload_and_sends_server_context(self, post, _context):
        self.authenticate_as(User.Role.FINANCE)
        post.return_value = Mock(
            json=Mock(return_value={"report": "Rapport"}),
            raise_for_status=Mock(),
        )
        response = self.client.post(
            "/api/ia/rapport/generate",
            {"dashboard": {"solde": 999999999}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(__import__("json").loads(post.call_args.kwargs["data"].decode("utf-8")), {"finances": {"budget_total": 125}})


