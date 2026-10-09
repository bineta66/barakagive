from datetime import date
import uuid
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.contrib.gis.geos import Point, Polygon
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.beneficiaries.models import Beneficiary, FormResponse
from apps.beneficiaries.services import BeneficiaryError, store_response
from apps.campaigns.models import Campaign
from apps.organizations.models import Organization
from apps.projects.models import Project, ProjectCriteria
from apps.zones.models import Department, Region, Zone
from .models import FormField, Formulaire
from .services import FormulaireError, update_formulaire
from .serializers import FormFieldCreateSerializer, FormFieldUpdateSerializer


class DynamicQuestionValidationTests(SimpleTestCase):
    def test_choice_questions_require_unique_non_empty_text_options(self):
        invalid_options = (
            {"choice": "not a list"},
            ["Oui", ""],
            ["Oui", "Oui"],
        )
        for options in invalid_options:
            with self.subTest(options_type=type(options).__name__):
                serializer = FormFieldCreateSerializer(data={
                    "label": "Réponse",
                    "type": FormField.TypeChoices.SELECT,
                    "options": options,
                })
                self.assertFalse(serializer.is_valid())
                self.assertIn("options", serializer.errors)

    def test_choice_question_accepts_unique_text_options(self):
        serializer = FormFieldCreateSerializer(data={
            "label": "Réponse",
            "type": FormField.TypeChoices.SELECT,
            "options": ["Oui", "Non"],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["options"], ["Oui", "Non"])

    def test_question_update_rejects_non_list_options(self):
        question = type("Question", (), {
            "type": FormField.TypeChoices.SELECT,
            "options": ["Oui", "Non"],
        })()
        serializer = FormFieldUpdateSerializer(
            instance=question,
            data={"options": {"Oui": True}},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("options", serializer.errors)


class FormOrganizationIsolationTests(TestCase):
    """HTTP and relation-level tenant boundary checks for dynamic forms."""

    def setUp(self):
        self.org_a = self._organization("Forms ONG A", "forms-a")
        self.org_b = self._organization("Forms ONG B", "forms-b")
        self.chef_a = self._user("forms-chef-a", User.Role.CHEF_PROJET, self.org_a)
        self.chef_b = self._user("forms-chef-b", User.Role.CHEF_PROJET, self.org_b)
        self.manager_a = self._user("forms-manager-a", User.Role.GERANT, self.org_a)
        self.manager_b = self._user("forms-manager-b", User.Role.GERANT, self.org_b)
        self.agent_a = self._user("forms-agent-a", User.Role.AGENT, self.org_a)
        self.agent_b = self._user("forms-agent-b", User.Role.AGENT, self.org_b)
        self.super_admin = self._user("forms-super", User.Role.SUPER_ADMIN, None)
        self.project_a, self.campaign_a = self._project_campaign(
            "A", self.org_a, self.chef_a
        )
        self.project_b, self.campaign_b = self._project_campaign(
            "B", self.org_b, self.chef_b
        )
        self.zone_a = self._zone(self.org_a, self.chef_a, "A")
        self.zone_b = self._zone(self.org_b, self.chef_b, "B")
        self.form_a = self._form("A", self.org_a, self.campaign_a, self.chef_a)
        self.form_b = self._form("B", self.org_b, self.campaign_b, self.chef_b)
        self.question_a = self._question(self.form_a, "A question")
        self.question_b = self._question(self.form_b, "B question")
        self.criterion_b = ProjectCriteria.objects.create(
            projet=self.project_b, nom="B criterion", poids=10, created_by=self.chef_b,
        )
        self.beneficiary_a = self._beneficiary(
            self.org_a, self.campaign_a, self.zone_a, self.chef_a, "A"
        )
        self.beneficiary_b = self._beneficiary(
            self.org_b, self.campaign_b, self.zone_b, self.chef_b, "B"
        )

    @staticmethod
    def _organization(name, slug):
        return Organization.objects.create(
            name=name, email=f"{slug}@example.test", phone="771230001",
            address="Dakar", region="Dakar", country="Senegal",
            intervention_domain="Humanitaire", status=Organization.Status.ACTIVE,
            is_active=True,
        )

    @staticmethod
    def _user(prefix, role, organization):
        return User.objects.create_user(
            email=f"{prefix}@example.test", password="SafePass123!",
            first_name="Forms", last_name=prefix, role=role,
            organization=organization, status=User.Status.ACTIVE, is_active=True,
            is_staff=role == User.Role.SUPER_ADMIN,
        )

    @staticmethod
    def _project_campaign(suffix, organization, chef):
        project = Project.objects.create(
            name=f"Forms project {suffix}", description="Forms isolation",
            region=organization.region, objectif="Test",
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            chef_projet=chef, responsable_finance=chef,
            organization=organization, created_by=chef,
        )
        campaign = Campaign.objects.create(
            projet=project, organization=organization,
            nom=f"Forms campaign {suffix}", code_campagne=f"FORMS-{suffix}-{organization.pk}",
            description="Forms isolation", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=chef,
        )
        return project, campaign

    @staticmethod
    def _form(suffix, organization, campaign, creator, status=None):
        return Formulaire.objects.create(
            campagne=campaign, organization=organization,
            nom=f"Form {suffix}", statut=status or Formulaire.Statut.BROUILLON,
            created_by=creator,
        )

    @staticmethod
    def _zone(organization, chef, suffix):
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        region = Region.objects.create(nom=f"Forms region {suffix}", geometrie=polygon)
        department = Department.objects.create(
            nom=f"Forms department {suffix}", region=region, geometrie=polygon,
        )
        return Zone.objects.create(
            nom=f"Forms zone {suffix}", region=region, departement=department,
            latitude=14.7, longitude=-17.4, location=Point(-17.4, 14.7, srid=4326),
            rayon=1000, organization=organization, created_by=chef,
        )

    @staticmethod
    def _question(form, label):
        return FormField.objects.create(
            formulaire=form, label=label, type=FormField.TypeChoices.TEXT,
        )

    @staticmethod
    def _beneficiary(organization, campaign, zone, creator, suffix):
        return Beneficiary.objects.create(
            campagne=campaign, zone=zone, organization=organization,
            nom=f"Beneficiary {suffix}", prenom="Test",
            telephone=f"+22177000{suffix}01", sexe=Beneficiary.Sexe.F,
            date_naissance=date(1990, 1, 1), latitude=14.7, longitude=-17.4,
            local_id=uuid.uuid4(), device_id=f"forms-{suffix}", created_by=creator,
        )

    @staticmethod
    def _client(user):
        token = str(RefreshToken.for_user(user).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def assert_denied(self, response):
        self.assertIn(response.status_code, (403, 404), response.status_code)

    def test_form_lists_and_details_are_scoped_in_both_directions(self):
        for user, own, foreign in (
            (self.manager_a, self.form_a, self.form_b),
            (self.manager_b, self.form_b, self.form_a),
        ):
            client = self._client(user)
            listing = client.get("/api/forms/")
            self.assertEqual(listing.status_code, 200)
            ids = [item["id"] for item in listing.data]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)
            self.assertEqual(client.get(f"/api/forms/{own.pk}/").status_code, 200)
            self.assert_denied(client.get(f"/api/forms/{foreign.pk}/"))

    def test_agents_only_list_published_forms_from_their_organization(self):
        self.form_a.statut = Formulaire.Statut.PUBLIE
        self.form_a.save(update_fields=["statut"])
        self.form_b.statut = Formulaire.Statut.PUBLIE
        self.form_b.save(update_fields=["statut"])
        unpublished_a = self._form("A draft", self.org_a, self.campaign_a, self.chef_a)
        for agent, own, foreign, draft in (
            (self.agent_a, self.form_a, self.form_b, unpublished_a),
            (self.agent_b, self.form_b, self.form_a, unpublished_a),
        ):
            response = self._client(agent).get("/api/forms/")
            self.assertEqual(response.status_code, 200)
            ids = [item["id"] for item in response.data]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)
            self.assertNotIn(str(draft.pk), ids)

    def test_cross_tenant_form_patch_delete_and_put_do_not_mutate(self):
        for actor, own, foreign in (
            (self.chef_a, self.form_a, self.form_b),
            (self.chef_b, self.form_b, self.form_a),
        ):
            client = self._client(actor)
            initial_name = foreign.nom
            self.assertEqual(client.get(f"/api/forms/{own.pk}/").status_code, 200)
            self.assert_denied(client.get(f"/api/forms/{foreign.pk}/"))
            self.assert_denied(client.patch(f"/api/forms/{foreign.pk}/", {"nom": "intrusion"}, format="json"))
            self.assert_denied(client.delete(f"/api/forms/{foreign.pk}/"))
            self.assertEqual(client.put(f"/api/forms/{foreign.pk}/", {"nom": "intrusion"}, format="json").status_code, 405)
            foreign.refresh_from_db()
            self.assertEqual(foreign.nom, initial_name)
            self.assertTrue(Formulaire.objects.filter(pk=foreign.pk).exists())

    def test_form_service_rejects_direct_cross_tenant_mutation(self):
        initial_name = self.form_b.nom
        with self.assertRaises(FormulaireError):
            update_formulaire(self.form_b, {"nom": "direct service intrusion"}, self.chef_a)
        self.form_b.refresh_from_db()
        self.assertEqual(self.form_b.nom, initial_name)

    def test_form_creation_derives_organization_and_rejects_foreign_campaign(self):
        client = self._client(self.chef_a)
        before = Formulaire.objects.count()
        own = client.post("/api/forms/", {
            "campagne_id": str(self.campaign_a.pk), "organization_id": self.org_b.pk,
            "project_id": self.project_b.pk, "nom": "New A form", "fields": [],
        }, format="json")
        self.assertEqual(own.status_code, 201, own.data)
        created = Formulaire.objects.get(pk=own.data["id"])
        self.assertEqual(created.organization_id, self.org_a.pk)
        self.assertEqual(created.campagne_id, self.campaign_a.pk)
        foreign = client.post("/api/forms/", {
            "campagne_id": str(self.campaign_b.pk), "nom": "Foreign campaign",
        }, format="json")
        self.assertEqual(foreign.status_code, 400, foreign.data)
        self.assertEqual(Formulaire.objects.count(), before + 1)

    def test_question_crud_is_scoped_and_foreign_criterion_rejected(self):
        for actor, own, foreign in (
            (self.chef_a, self.question_a, self.question_b),
            (self.chef_b, self.question_b, self.question_a),
        ):
            client = self._client(actor)
            initial = foreign.label
            self.assert_denied(client.patch(
                f"/api/forms/questions/{foreign.pk}/", {"label": "intrusion"}, format="json"
            ))
            self.assert_denied(client.delete(f"/api/forms/questions/{foreign.pk}/"))
            self.assertEqual(client.put(
                f"/api/forms/questions/{foreign.pk}/", {"label": "intrusion"}, format="json"
            ).status_code, 405)
            foreign.refresh_from_db()
            self.assertEqual(foreign.label, initial)
            self.assertTrue(FormField.objects.filter(pk=foreign.pk).exists())

        client_a = self._client(self.chef_a)
        invalid = client_a.post(f"/api/forms/{self.form_a.pk}/questions/", {
            "label": "Foreign criterion", "type": "TEXT", "critere": self.criterion_b.pk,
        }, format="json")
        self.assertEqual(invalid.status_code, 400, invalid.data)
        self.assertFalse(self.form_a.fields.filter(label="Foreign criterion").exists())

    def test_cross_tenant_question_create_duplicate_and_reorder_are_refused(self):
        client_a = self._client(self.chef_a)
        before_b = self.form_b.fields.count()
        response = client_a.post(
            f"/api/forms/{self.form_b.pk}/questions/",
            {"label": "Intrusion", "type": "TEXT"}, format="json",
        )
        self.assert_denied(response)
        self.assert_denied(client_a.post(
            f"/api/forms/questions/{self.question_b.pk}/duplicate/", {}, format="json"
        ))
        reorder = client_a.patch("/api/forms/questions/reorder/", {
            "formulaire_id": str(self.form_a.pk),
            "questions": [{"id": str(self.question_b.pk), "ordre": "0"}],
        }, format="json")
        self.assertEqual(reorder.status_code, 400, reorder.data)
        self.assertEqual(self.form_b.fields.count(), before_b)
        self.question_b.refresh_from_db()
        self.assertEqual(self.question_b.ordre, 0)

    def test_suspended_chef_old_jwt_cannot_list_or_modify_forms(self):
        client = self._client(self.chef_a)
        self.chef_a.status = User.Status.SUSPENDED
        self.chef_a.save(update_fields=["status"])
        self.assertEqual(client.get("/api/forms/").status_code, 403)
        self.assertEqual(client.patch(
            f"/api/forms/{self.form_a.pk}/", {"nom": "suspended"}, format="json"
        ).status_code, 403)
        self.form_a.refresh_from_db()
        self.assertEqual(self.form_a.nom, "Form A")

    def test_suspended_manager_and_agent_old_jwts_cannot_read_forms(self):
        for user in (self.manager_a, self.agent_a):
            client = self._client(user)
            user.status = User.Status.SUSPENDED
            user.save(update_fields=["status"])
            self.assertEqual(client.get("/api/forms/").status_code, 403)

    def test_super_admin_has_no_global_access_on_form_routes(self):
        client = self._client(self.super_admin)
        self.assertEqual(client.get("/api/forms/").status_code, 403)
        self.assertEqual(client.get(f"/api/forms/{self.form_a.pk}/").status_code, 403)

    def test_form_response_service_rejects_foreign_beneficiary_and_form_links(self):
        with self.assertRaises(BeneficiaryError):
            store_response(
                self.beneficiary_b, self.form_a, self.question_a, "foreign beneficiary"
            )
        with self.assertRaises(BeneficiaryError):
            store_response(
                self.beneficiary_a, self.form_b, self.question_b, "foreign form"
            )
        self.assertEqual(FormResponse.objects.count(), 0)

    def test_read_does_not_disclose_project_from_incoherent_form_chain(self):
        # Adverse fixture: ONG A form and campaign are attached to ONG B project.
        malformed_campaign = Campaign.objects.create(
            projet=self.project_b, organization=self.org_a,
            nom="B project exposed through A", code_campagne=f"BAD-{self.org_a.pk}-{uuid.uuid4().hex[:6]}",
            description="Inconsistent relation", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=self.chef_a,
        )
        malformed_form = self._form("Malformed", self.org_a, malformed_campaign, self.chef_a)
        response = self._client(self.manager_a).get(f"/api/forms/{malformed_form.pk}/")
        # Expected tenant boundary: an inconsistent parent chain is not readable.
        self.assertEqual(response.status_code, 404)

    def test_form_list_does_not_disclose_inconsistent_foreign_campaign(self):
        malformed_campaign = Campaign.objects.create(
            projet=self.project_b, organization=self.org_a,
            nom="Foreign campaign metadata", code_campagne=f"BADLIST-{self.org_a.pk}-{uuid.uuid4().hex[:6]}",
            description="Inconsistent relation", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=self.chef_a,
        )
        malformed_form = self._form("Malformed list", self.org_a, malformed_campaign, self.chef_a)
        response = self._client(self.manager_a).get("/api/forms/")
        self.assertEqual(response.status_code, 200)
        returned = {item["id"]: item for item in response.data}
        self.assertNotIn(str(malformed_form.pk), returned)

    def test_ai_question_generation_rejects_inconsistent_foreign_project(self):
        foreign_project_led_by_a = Project.objects.create(
            name="ONG B confidential project", description="Inconsistent test relation",
            region=self.org_b.region, objectif="B data", start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31), chef_projet=self.chef_a,
            responsable_finance=self.chef_b, organization=self.org_b,
            created_by=self.chef_a,
        )
        foreign_campaign = Campaign.objects.create(
            projet=foreign_project_led_by_a, organization=self.org_a,
            nom="Campaign A with foreign project", code_campagne=f"BADAI-{self.org_a.pk}-{uuid.uuid4().hex[:6]}",
            description="Inconsistent test relation", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=self.chef_a,
        )
        foreign_criterion = ProjectCriteria.objects.create(
            projet=foreign_project_led_by_a, nom="B private criterion", poids=10,
            created_by=self.chef_b,
        )
        with patch("apps.forms.views.post_to_ai_service") as ai_call:
            response = self._client(self.chef_a).post(
                f"/api/forms/campaigns/{foreign_campaign.pk}/generate-questions/", {}, format="json"
            )
        self.assertEqual(response.status_code, 404)
        ai_call.assert_not_called()
        self.assertTrue(ProjectCriteria.objects.filter(pk=foreign_criterion.pk).exists())
