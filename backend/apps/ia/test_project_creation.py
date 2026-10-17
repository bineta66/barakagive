from datetime import date
from uuid import uuid4

from django.test import TestCase
from django.db.models import Sum
from django.db import DatabaseError
from unittest.mock import patch
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.ia.models import ProjectCreationSession
from apps.organizations.models import Organization
from apps.projects.models import Project, ProjectCriteria


class ConversationalProjectCreationTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name="ONG Dialogue", email="dialogue@example.test", phone="771234111",
            address="Dakar", region="Dakar", country="Senegal",
            intervention_domain="Humanitaire",
        )
        self.other_org = Organization.objects.create(
            name="ONG Autre", email="autre@example.test", phone="771234112",
            address="Thies", region="Thies", country="Senegal",
            intervention_domain="Education",
        )
        self.manager = self._user("manager@example.test", User.Role.GERANT, self.org)
        self.chef = self._user("chef@example.test", User.Role.CHEF_PROJET, self.org)
        self.finance = self._user("finance@example.test", User.Role.FINANCE, self.org)
        self.other_chef = self._user("other@example.test", User.Role.CHEF_PROJET, self.other_org)
        self.client = APIClient()
        self.client.force_authenticate(self.manager)
        self.session_id = str(uuid4())

    @staticmethod
    def _user(email, role, organization):
        return User.objects.create_user(
            email=email, password="SafePass123!", first_name=role.title(),
            last_name="Test", role=role, organization=organization,
            status=User.Status.ACTIVE, is_active=True,
        )

    def _send(self, text, client=None):
        return (client or self.client).post(
            "/api/assistant/chat/", {"question": text, "session_id": self.session_id}, format="json",
        )

    def _prepare_confirmation(self):
        response = self._send("Créer un projet Distribution alimentaire")
        self.assertEqual(response.status_code, 200)
        self._send("Description : distribution de kits aux familles")
        self._send("Objectif : aider 300 familles vulnérables")
        self._send("Région : Dakar")
        self._send("01/11/2026 au 31/12/2026")
        response = self._send("1")
        self.assertIn("responsable finance", response.data["answer"])
        response = self._send("1")
        self.assertIn("Pertinence du besoin", response.data["answer"])
        response = self._send("oui")
        self.assertIn("Repondez confirmer", response.data["answer"])
        return response

    def _finish_conversation(self, confirmation="confirmer"):
        self._prepare_confirmation()
        return self._send(confirmation)

    def test_project_creation_requires_summary_confirmation_and_persists_valid_data(self):
        response = self._finish_conversation()
        self.assertEqual(response.status_code, 200)
        self.assertIn("cree avec succes", response.data["answer"])
        project = Project.objects.get(name="Distribution alimentaire")
        self.assertEqual(project.organization, self.org)
        self.assertEqual(project.chef_projet, self.chef)
        self.assertEqual(project.responsable_finance, self.finance)
        self.assertEqual(project.start_date, date(2026, 11, 1))
        self.assertEqual(project.criteres.aggregate(total=Sum("poids"))["total"], 100)

    def test_conversation_can_be_restored_after_a_reload(self):
        self._send("Créer un projet Distribution alimentaire")
        response = self.client.get("/api/assistant/chat/", {"session_id": self.session_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["messages"][-1]["role"], "assistant")
        self.assertIn("description", response.data["messages"][-1]["content"])

    def test_one_message_can_supply_multiple_project_facts(self):
        response = self._send(
            "Créer un projet\nNom : Aide alimentaire\n"
            "Description : Distribution de vivres\nObjectif : Soutenir 300 familles\n"
            "Région : Dakar\nDates : 01/11/2026 au 31/12/2026"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("chef de projet", response.data["answer"])
        session = ProjectCreationSession.objects.get(user=self.manager, conversation_id=self.session_id)
        self.assertEqual(session.state["data"]["name"], "Aide alimentaire")
        self.assertEqual(session.state["data"]["start_date"], "2026-11-01")
        self.assertEqual(session.state["data"]["end_date"], "2026-12-31")

    def test_confirmation_requires_explicit_word_and_region_can_be_corrected(self):
        self._send(
            "Créer un projet\nNom : Aide alimentaire\nDescription : Distribution de vivres\n"
            "Objectif : Soutenir 300 familles\nRégion : Dakar\nDates : 01/11/2026 au 31/12/2026"
        )
        self._send("1")
        self._send("1")
        self._send("oui")
        response = self._send("oui")
        self.assertIn("confirmer", response.data["answer"])
        self.assertFalse(Project.objects.filter(name="Aide alimentaire").exists())
        self._send("corriger région")
        summary = self._send("Kaolack")
        self.assertIn("Kaolack", summary.data["answer"])
        response = self._send("confirmer")
        self.assertIn("cree avec succes", response.data["answer"])
        self.assertEqual(Project.objects.get(name="Aide alimentaire").region, "Kaolack")

    def test_repeated_confirmation_returns_same_project(self):
        response = self._finish_conversation()
        self.assertEqual(response.status_code, 200)
        self._send("confirmer")
        self.assertEqual(Project.objects.filter(organization=self.org, name="Distribution alimentaire").count(), 1)

    def test_common_confirmation_typos_create_the_project(self):
        for phrase in ("Comfirmer", "oui je comfirme"):
            with self.subTest(phrase=phrase):
                self.session_id = str(uuid4())
                response = self._finish_conversation(phrase)
                self.assertIn("cree avec succes", response.data["answer"])
        self.assertEqual(Project.objects.filter(organization=self.org, name="Distribution alimentaire").count(), 2)

    def test_copying_the_instruction_is_not_confirmation(self):
        self._prepare_confirmation()
        response = self._send("« confirmer » pour enregistrer ce projet")
        self.assertIn("brouillon est conserve", response.data["answer"])
        self.assertFalse(Project.objects.filter(name="Distribution alimentaire").exists())

    def test_denial_and_correction_do_not_create(self):
        self._prepare_confirmation()
        response = self._send("Je ne confirme pas")
        self.assertIn("n'enregistre pas", response.data["answer"])
        response = self._send("Je veux corriger le budget avant de confirmer")
        self.assertIn("budget", response.data["answer"].lower())
        self.assertIn("pas inclus", response.data["answer"].lower())
        self.assertFalse(Project.objects.filter(name="Distribution alimentaire").exists())
        self.assertTrue(ProjectCreationSession.objects.get(conversation_id=self.session_id).state["stage"].endswith("CONFIRMATION"))

    def test_question_about_confirmation_asks_for_clarification(self):
        self._prepare_confirmation()
        response = self._send("Que signifie confirmer ?")
        self.assertIn("n'ai pas compris", response.data["answer"])
        self.assertFalse(Project.objects.filter(name="Distribution alimentaire").exists())

    def test_serializer_errors_are_shown_and_draft_is_preserved(self):
        self._prepare_confirmation()
        self.finance.role = User.Role.AGENT
        self.finance.save(update_fields=["role"])
        response = self._send("confirmer")
        self.assertIn("n'a pas ete enregistre", response.data["answer"])
        self.assertIn("responsable_finance", response.data["answer"])
        session = ProjectCreationSession.objects.get(conversation_id=self.session_id)
        self.assertIsNone(session.project_id)
        self.assertEqual(session.state["stage"], "AWAITING_CONFIRMATION")

    def test_database_failure_preserves_draft_and_can_be_retried(self):
        self._prepare_confirmation()
        with patch("apps.ia.project_creation.ProjectCreateSerializer.save", side_effect=DatabaseError("temporary failure")):
            response = self._send("confirmer")
        self.assertIn("Django n'a pas pu enregistrer", response.data["answer"])
        self.assertIsNone(ProjectCreationSession.objects.get(conversation_id=self.session_id).project_id)
        response = self._send("confirmer")
        self.assertIn("cree avec succes", response.data["answer"])

    def test_token_question_is_out_of_scope_without_summary_data(self):
        with patch("apps.ia.views.build_chat_context") as build_context:
            response = self._send("C'est quoi un token ?")
        self.assertEqual(response.status_code, 200)
        self.assertIn("assistant exécutif de BarakaGive360", response.data["answer"])
        build_context.assert_not_called()

    def test_explicit_summary_routes_to_summary_only(self):
        with patch("apps.ia.views.build_chat_context", return_value={"organisation": "ONG Dialogue"}), \
             patch("apps.ia.views._build_agent_tool_results", return_value=[]) as tools, \
             patch("apps.ia.views.post_to_ai_service") as ai:
            ai.return_value.json.return_value = {"answer": "Bilan de l'ONG"}
            response = self._send("Fais-moi le bilan de mon ONG")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tools.call_args.args[2], ["get_ong_summary"])

    def test_out_of_scope_question_during_creation_preserves_the_draft(self):
        self._send("Créer un projet Distribution alimentaire")
        session = ProjectCreationSession.objects.get(conversation_id=self.session_id)
        stage = session.state["stage"]
        response = self._send("C'est quoi un token ?")
        self.assertIn("assistant exécutif de BarakaGive360", response.data["answer"])
        session.refresh_from_db()
        self.assertEqual(session.state["stage"], stage)
        self.assertNotIn("objectif", session.state["data"])

    def test_business_query_during_creation_is_routed_without_consuming_answer(self):
        self._send("Créer un projet Distribution alimentaire")
        session = ProjectCreationSession.objects.get(conversation_id=self.session_id)
        stage = session.state["stage"]
        with patch("apps.ia.views.build_chat_context", return_value={"organisation": "ONG Dialogue"}), \
             patch("apps.ia.views._build_agent_tool_results", return_value=[]) as tools, \
             patch("apps.ia.views.post_to_ai_service") as ai:
            ai.return_value.json.return_value = {"answer": "Voici le budget."}
            response = self._send("Quel est mon budget ?")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tools.call_args.args[2], ["get_financial_summary", "get_budgets"])
        session.refresh_from_db()
        self.assertEqual(session.state["stage"], stage)
        self.assertNotIn("objectif", session.state["data"])

    def test_completed_flow_does_not_block_normal_chat_or_a_new_project(self):
        self._finish_conversation()
        from apps.ia.project_creation import handle_project_creation
        self.assertIsNone(handle_project_creation(self.manager, self.session_id, "Fais le bilan de mon ONG", None))
        response = self._send("Créer un nouveau projet")
        self.assertEqual(response.status_code, 200)
        self.assertIn("nom", response.data["answer"].lower())

    def test_non_manager_cannot_start_project_flow(self):
        client = APIClient()
        client.force_authenticate(self.chef)
        response = self._send("Créer un projet de test", client)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ProjectCreationSession.objects.filter(user=self.chef).exists())

    def test_session_is_bound_to_user_and_organization(self):
        foreign_manager = self._user("manager-other@example.test", User.Role.GERANT, self.other_org)
        client = APIClient()
        client.force_authenticate(foreign_manager)
        response = self._send("Je veux créer un projet", client)
        self.assertEqual(response.status_code, 200)
        session = ProjectCreationSession.objects.get(user=foreign_manager, conversation_id=self.session_id)
        self.assertEqual(session.organization, self.other_org)
        self.assertNotIn(self.chef.full_name, response.data["answer"])
        self.assertNotIn(self.other_chef.full_name, response.data["answer"])

    def test_projects_can_be_cancelled_before_creation(self):
        self._send("Créer un projet Distribution alimentaire")
        response = self._send("annuler")
        self.assertIn("annule", response.data["answer"].lower())
        self.assertFalse(Project.objects.filter(name="Distribution alimentaire").exists())
