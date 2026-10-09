from datetime import date
import uuid

from django.db import IntegrityError
from django.contrib.gis.geos import Point, Polygon
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.projects.models import Project
from .agent_views import AgentCampaignFormView, AgentCampaignListView, AgentDashboardView
from .views import CampaignAgentZonesView, CampaignDetailView, CampaignListCreateView
from .models import Campaign, CampagneAffectation
from .services import generate_campaign_code
from .serializers import CampaignCreateSerializer, CampaignUpdateSerializer
from apps.zones.models import Department, Region, Zone
from apps.beneficiaries.models import Beneficiary


class CampaignFormPayloadValidationTests(SimpleTestCase):
    def test_create_accepts_zone_uuid_and_same_start_end_date(self):
        serializer = CampaignCreateSerializer(data={
            "projet_id": 1,
            "nom": "Campagne valide",
            "zone_ids": [str(uuid.uuid4())],
            "date_debut": "2026-05-01",
            "date_fin": "2026-05-01",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_campaign_types_distinguish_needs_collection_from_fundraising(self):
        base = {
            "projet_id": 1,
            "nom": "Collecte des besoins",
            "zone_ids": [str(uuid.uuid4())],
            "date_debut": "2026-05-01",
            "date_fin": "2026-05-02",
        }
        operational = CampaignCreateSerializer(data={
            **base,
            "type": Campaign.Type.COLLECTE_BESOINS,
        })
        self.assertTrue(operational.is_valid(), operational.errors)

        legacy_fundraising = CampaignCreateSerializer(data={
            **base,
            "type": Campaign.Type.COLLECTE,
        })
        self.assertFalse(legacy_fundraising.is_valid())
        self.assertIn("type", legacy_fundraising.errors)

    def test_create_rejects_invalid_and_duplicate_zone_ids(self):
        base = {
            "projet_id": 1,
            "nom": "Campagne valide",
            "date_debut": "2026-05-01",
            "date_fin": "2026-05-02",
        }
        invalid = CampaignCreateSerializer(data={**base, "zone_ids": ["pas-un-uuid"]})
        self.assertFalse(invalid.is_valid())
        self.assertIn("zone_ids", invalid.errors)

        zone_id = str(uuid.uuid4())
        duplicate = CampaignCreateSerializer(data={**base, "zone_ids": [zone_id, zone_id]})
        self.assertFalse(duplicate.is_valid())
        self.assertIn("zone_ids", duplicate.errors)

    def test_update_rejects_end_date_before_start_date(self):
        serializer = CampaignUpdateSerializer(data={
            "date_debut": "2026-05-03",
            "date_fin": "2026-05-02",
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("date_fin", serializer.errors)

    def test_campaign_status_accepts_only_model_choices(self):
        create_serializer = CampaignCreateSerializer(data={
            "projet_id": 1,
            "nom": "Campagne valide",
            "zone_ids": [str(uuid.uuid4())],
            "date_debut": "2026-05-01",
            "date_fin": "2026-05-02",
            "statut": "PLANIFIER",
        })
        self.assertTrue(create_serializer.is_valid(), create_serializer.errors)

        update_serializer = CampaignUpdateSerializer(data={"statut": "INVALIDE"}, partial=True)
        self.assertFalse(update_serializer.is_valid())
        self.assertIn("statut", update_serializer.errors)

        valid_update = CampaignUpdateSerializer(data={"statut": "ANNULEE"}, partial=True)
        self.assertTrue(valid_update.is_valid(), valid_update.errors)


class CampaignStatusPersistenceTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Statut",
            email="statut@example.test",
            phone="+221770000100",
            address="Dakar",
            region="Dakar",
            country="Sénégal",
            intervention_domain="Humanitaire",
        )
        self.chef = User.objects.create_user(
            email="chef-statut@example.test",
            password="password123",
            first_name="Chef",
            last_name="Statut",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.project = Project.objects.create(
            name="Projet Statut",
            description="Description",
            region="Dakar",
            objectif="Collecte",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        region = Region.objects.create(nom="Dakar Statut", geometrie=polygon)
        department = Department.objects.create(
            nom="Dakar Statut", region=region, geometrie=polygon,
        )
        self.zone = Zone.objects.create(
            nom="Zone Statut",
            region=region,
            departement=department,
            latitude=14.7,
            longitude=-17.4,
            location=Point(-17.4, 14.7, srid=4326),
            rayon=1000,
            organization=self.organization,
            created_by=self.chef,
        )

    def test_create_and_update_persist_allowed_campaign_statuses(self):
        request = APIRequestFactory().post("/api/campaigns/", {
            "projet_id": self.project.pk,
            "nom": "Campagne Statut",
            "description": "Test",
            "zone_ids": [str(self.zone.pk)],
            "date_debut": "2026-10-01",
            "date_fin": "2026-10-02",
            "statut": Campaign.Statut.PLANIFIER,
        }, format="json")
        force_authenticate(request, user=self.chef)
        created = CampaignListCreateView.as_view()(request)

        self.assertEqual(created.status_code, 201, created.data)
        campaign = Campaign.objects.get(pk=created.data["id"])
        self.assertEqual(campaign.statut, Campaign.Statut.PLANIFIER)

        request = APIRequestFactory().patch(
            f"/api/campaigns/{campaign.pk}/",
            {"statut": Campaign.Statut.ANNULEE},
            format="json",
        )
        force_authenticate(request, user=self.chef)
        updated = CampaignDetailView.as_view()(request, campaign.pk)

        self.assertEqual(updated.status_code, 200, updated.data)
        campaign.refresh_from_db()
        self.assertEqual(campaign.statut, Campaign.Statut.ANNULEE)

    def test_campaign_list_uses_backend_pagination_and_project_scope(self):
        for index in range(2):
            Campaign.objects.create(
                projet=self.project,
                organization=self.organization,
                nom=f"Campagne pagination {index}",
                code_campagne=f"TEST-PAGE-{index}",
                description="Test pagination",
                date_debut=date(2026, 10, 1),
                date_fin=date(2026, 10, 2),
                created_by=self.chef,
            )
        request = APIRequestFactory().get("/api/campaigns/?page=2&page_size=1")
        force_authenticate(request, user=self.chef)
        response = CampaignListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["previous"])

    def test_campaign_id_search_stays_inside_chef_project_scope(self):
        campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne à retrouver",
            code_campagne="TEST-ID-SEARCH",
            description="Test",
            date_debut=date(2026, 10, 1),
            date_fin=date(2026, 10, 2),
            created_by=self.chef,
        )
        other_chef = User.objects.create_user(
            email="chef-id-search-other@example.test",
            password="password123",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        other_project = Project.objects.create(
            name="Projet hors périmètre",
            description="",
            region="Dakar",
            objectif="Test",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=other_chef,
            responsable_finance=other_chef,
            organization=self.organization,
            created_by=other_chef,
        )
        other_campaign = Campaign.objects.create(
            projet=other_project,
            organization=self.organization,
            nom="Campagne hors périmètre",
            code_campagne="TEST-ID-OTHER",
            description="Test",
            date_debut=date(2026, 10, 1),
            date_fin=date(2026, 10, 2),
            created_by=other_chef,
        )

        request = APIRequestFactory().get(f"/api/campaigns/?ids={campaign.pk}")
        force_authenticate(request, user=self.chef)
        response = CampaignListCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(campaign.pk))

        request = APIRequestFactory().get(f"/api/campaigns/?ids={other_campaign.pk}")
        force_authenticate(request, user=self.chef)
        response = CampaignListCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_project_lead_cannot_read_another_leads_campaign(self):
        campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne périmètre chef",
            code_campagne="TEST-CHEF-READ",
            description="Test",
            date_debut=date(2026, 10, 1),
            date_fin=date(2026, 10, 2),
            created_by=self.chef,
        )
        other_chef = User.objects.create_user(
            email="autre-chef-statut@example.test",
            password="password123",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        request = APIRequestFactory().get(f"/api/campaigns/{campaign.pk}/")
        force_authenticate(request, user=other_chef)
        response = CampaignDetailView.as_view()(request, campaign.pk)
        self.assertEqual(response.status_code, 404)


class CampagneAffectationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Test",
            email="ong-test@example.com",
            phone="+221770000",
            address="Dakar",
            region="Dakar",
            country="Sénégal",
            intervention_domain="Solidarité",
        )
        self.chef = User.objects.create_user(
            email="chef@example.com",
            password="password123",
            first_name="Chef",
            last_name="Projet",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.agent = User.objects.create_user(
            email="agent@example.com",
            password="password123",
            first_name="Agent",
            last_name="Terrain",
            role=User.Role.AGENT,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.project = Project.objects.create(
            name="Projet test",
            description="Projet test",
            region="Dakar",
            objectif="Collecte",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        self.assigned = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne assignée",
            code_campagne="CMP-TEST-001",
            description="Test",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            created_by=self.chef,
        )
        self.unassigned = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne non assignée",
            code_campagne="CMP-TEST-002",
            description="Test",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            created_by=self.chef,
        )
        CampagneAffectation.objects.create(
            campagne=self.assigned,
            agent=self.agent,
            zone="Dakar Nord",
            objectif_beneficiaires=20,
            created_by=self.chef,
        )

    def test_agent_ne_voit_que_ses_campagnes(self):
        request = APIRequestFactory().get("/api/agent/campagnes/")
        force_authenticate(request, user=self.agent)
        response = AgentCampaignListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            [item["nom"] for item in response.data["results"]],
            ["Campagne assignée"],
        )

    def test_agent_cannot_open_unassigned_campaign_by_id(self):
        request = APIRequestFactory().get(
            f"/api/agent/campagnes/{self.unassigned.pk}/formulaire/"
        )
        force_authenticate(request, user=self.agent)
        response = AgentCampaignFormView.as_view()(request, pk=self.unassigned.pk)
        self.assertEqual(response.status_code, 403)

    def test_agent_dashboard_exposes_only_agent_scope_and_expected_kpis(self):
        request = APIRequestFactory().get("/api/agent/dashboard/")
        force_authenticate(request, user=self.agent)
        response = AgentDashboardView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["campagnes_actives"], 1)
        self.assertEqual(response.data["zones_assignees"], 1)
        self.assertEqual(response.data["beneficiaires_enregistres"], 0)
        self.assertEqual(response.data["beneficiaires_prioritaires"], 0)

    def test_affectation_unique_par_campagne_et_agent(self):
        # Un doublon strict (campagne, agent, zone) doit etre refuse.
        with self.assertRaises(IntegrityError):
            CampagneAffectation.objects.create(
                campagne=self.assigned,
                agent=self.agent,
                zone="Dakar Nord",
                objectif_beneficiaires=10,
                created_by=self.chef,
            )


class CampaignOrganizationIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="Campaign ONG A", email="camp-a@example.test", phone="771230001",
            address="Dakar", region="Dakar", country="Senegal",
            intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="Campaign ONG B", email="camp-b@example.test", phone="771230002",
            address="Thies", region="Thies", country="Senegal",
            intervention_domain="Education",
        )
        self.manager_a = self._user("camp-manager-a@example.test", User.Role.GERANT, self.org_a)
        self.manager_b = self._user("camp-manager-b@example.test", User.Role.GERANT, self.org_b)
        self.chef_a = self._user("camp-chef-a@example.test", User.Role.CHEF_PROJET, self.org_a)
        self.chef_b = self._user("camp-chef-b@example.test", User.Role.CHEF_PROJET, self.org_b)
        self.agent_a = self._user("camp-agent-a@example.test", User.Role.AGENT, self.org_a)
        self.agent_b = self._user("camp-agent-b@example.test", User.Role.AGENT, self.org_b)
        self.super_admin = self._user("camp-super@example.test", User.Role.SUPER_ADMIN, None)
        self.project_a = self._project("Project A", self.org_a, self.chef_a)
        self.project_b = self._project("Project B", self.org_b, self.chef_b)
        self.zone_a = self._zone("Zone A", self.org_a, self.chef_a, "Region Camp A")
        self.zone_b = self._zone("Zone B", self.org_b, self.chef_b, "Region Camp B")
        self.campaign_a = self._campaign("Campaign A", "CMP-ORG-A", self.project_a, self.org_a, self.chef_a, self.zone_a)
        self.campaign_b = self._campaign("Campaign B", "CMP-ORG-B", self.project_b, self.org_b, self.chef_b, self.zone_b)
        CampagneAffectation.objects.create(
            campagne=self.campaign_a, agent=self.agent_a, zone=self.zone_a.nom,
            objectif_beneficiaires=10, created_by=self.chef_a,
        )
        CampagneAffectation.objects.create(
            campagne=self.campaign_b, agent=self.agent_b, zone=self.zone_b.nom,
            objectif_beneficiaires=20, created_by=self.chef_b,
        )

    @staticmethod
    def _user(email, role, organization):
        return User.objects.create_user(
            email=email, password="SafePass123!", first_name="Test", last_name="User",
            role=role, organization=organization, status=User.Status.ACTIVE,
            is_active=True, is_staff=(role == User.Role.SUPER_ADMIN),
        )

    @staticmethod
    def _project(name, organization, chef):
        return Project.objects.create(
            name=name, description="Campaign isolation", region=organization.region,
            objectif="Multi-organization test", start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31), chef_projet=chef,
            responsable_finance=chef, organization=organization, created_by=chef,
        )

    @staticmethod
    def _zone(name, organization, creator, region_name):
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        region = Region.objects.create(nom=region_name, geometrie=polygon)
        department = Department.objects.create(nom=region_name, region=region, geometrie=polygon)
        return Zone.objects.create(
            nom=name, region=region, departement=department, latitude=14.7,
            longitude=-17.4, location=Point(-17.4, 14.7, srid=4326), rayon=1000,
            organization=organization, created_by=creator,
        )

    @staticmethod
    def _campaign(name, code, project, organization, creator, zone):
        campaign = Campaign.objects.create(
            projet=project, organization=organization, nom=name, code_campagne=code,
            description="Campaign test", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=creator,
        )
        campaign.zones.add(zone)
        return campaign

    @staticmethod
    def _client(user):
        token = str(RefreshToken.for_user(user).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def assert_denied(self, response):
        self.assertIn(response.status_code, (403, 404), response.status_code)

    def test_a_and_b_lists_and_campaign_details_are_tenant_scoped(self):
        for manager, own, foreign in (
            (self.manager_a, self.campaign_a, self.campaign_b),
            (self.manager_b, self.campaign_b, self.campaign_a),
        ):
            client = self._client(manager)
            response = client.get("/api/campaigns/?page=1&page_size=50")
            self.assertEqual(response.status_code, 200)
            ids = [row["id"] for row in response.data["results"]]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)
            self.assertEqual(client.get(f"/api/campaigns/{own.pk}/").status_code, 200)
            self.assert_denied(client.get(f"/api/campaigns/{foreign.pk}/"))

    def test_chef_b_cannot_patch_put_or_delete_campaign_a(self):
        client = self._client(self.chef_b)
        url = f"/api/campaigns/{self.campaign_a.pk}/"
        original = (self.campaign_a.nom, self.campaign_a.description, self.campaign_a.statut)
        self.assert_denied(client.patch(url, {"nom": "Changed by B"}, format="json"))
        self.assertEqual(client.put(url, {"nom": "Changed by B"}, format="json").status_code, 405)
        self.assert_denied(client.delete(url))
        self.campaign_a.refresh_from_db()
        self.assertEqual((self.campaign_a.nom, self.campaign_a.description, self.campaign_a.statut), original)
        self.assertTrue(Campaign.objects.filter(pk=self.campaign_a.pk).exists())

    def test_foreign_project_and_zone_are_rejected_on_campaign_creation(self):
        client_a, client_b = self._client(self.chef_a), self._client(self.chef_b)
        baseline = Campaign.objects.count()
        payload = {"nom": "New Campaign", "description": "Test",
                   "date_debut": "2026-05-01", "date_fin": "2026-05-02"}
        cross_project = client_b.post(
            "/api/campaigns/", {**payload, "projet_id": self.project_a.pk,
                                "zone_ids": [str(self.zone_a.pk)]}, format="json",
        )
        self.assertEqual(cross_project.status_code, 400)
        cross_zone_b = client_b.post(
            "/api/campaigns/", {**payload, "projet_id": self.project_b.pk,
                                "zone_ids": [str(self.zone_a.pk)]}, format="json",
        )
        self.assertEqual(cross_zone_b.status_code, 400)
        cross_zone_a = client_a.post(
            "/api/campaigns/", {**payload, "nom": "Campaign A foreign zone",
                                "projet_id": self.project_a.pk,
                                "zone_ids": [str(self.zone_b.pk)]}, format="json",
        )
        self.assertEqual(cross_zone_a.status_code, 400)
        self.assertEqual(Campaign.objects.count(), baseline)

    def test_campaign_organization_is_taken_from_project_not_request(self):
        response = self._client(self.chef_b).post(
            "/api/campaigns/",
            {"projet_id": self.project_b.pk, "organization_id": self.org_a.pk,
             "nom": "Campaign B server tenant", "description": "Test",
             "zone_ids": [str(self.zone_b.pk)], "date_debut": "2026-05-01",
             "date_fin": "2026-05-02"}, format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        created = Campaign.objects.get(pk=response.data["id"])
        self.assertEqual(created.organization_id, self.org_b.pk)
        self.assertEqual(created.projet_id, self.project_b.pk)

    def test_campaign_project_cannot_be_changed_through_patch(self):
        response = self._client(self.chef_a).patch(
            f"/api/campaigns/{self.campaign_a.pk}/",
            {"projet_id": self.project_b.pk, "nom": "Still A"}, format="json",
        )
        self.assertIn(response.status_code, (200, 400))
        self.campaign_a.refresh_from_db()
        self.assertEqual(self.campaign_a.projet_id, self.project_a.pk)
        self.assertEqual(self.campaign_a.organization_id, self.org_a.pk)

    def test_agent_assignments_reject_cross_organization_targets(self):
        client_a, client_b = self._client(self.chef_a), self._client(self.chef_b)
        count_before = CampagneAffectation.objects.filter(campagne=self.campaign_a).count()
        payload = {"agent_id": self.agent_b.pk, "zones": [self.zone_a.nom], "objectif": 5}
        response = client_a.put(
            f"/api/campaigns/{self.campaign_a.pk}/agents/zones/", payload, format="json",
        )
        self.assertEqual(response.status_code, 404)
        response = client_b.put(
            f"/api/campaigns/{self.campaign_a.pk}/agents/zones/", payload, format="json",
        )
        self.assert_denied(response)
        self.assertEqual(CampagneAffectation.objects.filter(campagne=self.campaign_a).count(), count_before)
        self.assertFalse(CampagneAffectation.objects.filter(campagne=self.campaign_a, agent=self.agent_b).exists())

    def test_campaign_creation_rejects_agent_from_other_organization(self):
        before = Campaign.objects.count()
        response = self._client(self.chef_b).post(
            "/api/campaigns/",
            {"projet_id": self.project_b.pk, "nom": "Foreign agent", "description": "Test",
             "zone_ids": [str(self.zone_b.pk)], "date_debut": "2026-05-01",
             "date_fin": "2026-05-02",
             "agents": [{"agent_id": self.agent_a.pk, "zones": [self.zone_b.nom], "objectif": 5}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Campaign.objects.count(), before)

    def test_agent_campaign_list_only_shows_own_assigned_campaign(self):
        for agent, own, foreign in (
            (self.agent_a, self.campaign_a, self.campaign_b),
            (self.agent_b, self.campaign_b, self.campaign_a),
        ):
            response = self._client(agent).get("/api/agent/campagnes/?page=1&page_size=50")
            self.assertEqual(response.status_code, 200)
            ids = [row["id"] for row in response.data["results"]]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)

    def test_agent_b_cannot_read_or_create_beneficiaries_through_campaign_a(self):
        client_b = self._client(self.agent_b)
        url = f"/api/agent/campagnes/{self.campaign_a.pk}/beneficiaires/"
        before = Beneficiary.objects.count()
        self.assertEqual(client_b.get(url).status_code, 403)
        self.assertEqual(client_b.post(url, {"nom": "Foreign", "prenom": "Attempt"}, format="json").status_code, 403)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_foreign_beneficiary_row_does_not_contaminate_agent_campaign_count(self):
        Beneficiary.objects.create(
            campagne=self.campaign_a, zone=self.zone_a, organization=self.org_a,
            nom="Beneficiary A", prenom="Alice", telephone="+221770004001",
            sexe=Beneficiary.Sexe.F, date_naissance=date(1990, 1, 1), latitude=14.7,
            longitude=-17.4, local_id=uuid.uuid4(), device_id="device-A", created_by=self.agent_a,
        )
        Beneficiary.objects.create(
            campagne=self.campaign_a, zone=self.zone_a, organization=self.org_b,
            nom="Inconsistent B row", prenom="Binta", telephone="+221770004002",
            sexe=Beneficiary.Sexe.F, date_naissance=date(1990, 1, 1), latitude=14.7,
            longitude=-17.4, local_id=uuid.uuid4(), device_id="device-B", created_by=self.agent_a,
        )
        response = self._client(self.agent_a).get("/api/agent/campagnes/?page=1&page_size=50")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["collectes"], 1)

    def test_suspended_manager_chef_and_agent_are_denied_with_old_jwt(self):
        for user, path in (
            (self.manager_a, "/api/campaigns/"),
            (self.chef_a, f"/api/campaigns/{self.campaign_a.pk}/"),
            (self.agent_a, "/api/agent/campagnes/"),
        ):
            with self.subTest(role=user.role):
                client = self._client(user)
                user.status = User.Status.SUSPENDED
                user.save(update_fields=["status"])
                self.assertEqual(client.get(path).status_code, 403)

    def test_active_super_admin_keeps_global_campaign_access(self):
        client = self._client(self.super_admin)
        response = client.get("/api/campaigns/?page=1&page_size=50")
        self.assertEqual(response.status_code, 200)
        ids = [row["id"] for row in response.data["results"]]
        self.assertIn(str(self.campaign_a.pk), ids)
        self.assertIn(str(self.campaign_b.pk), ids)
        self.assertEqual(client.get(f"/api/campaigns/{self.campaign_a.pk}/").status_code, 200)
        self.assertEqual(client.get(f"/api/campaigns/{self.campaign_b.pk}/").status_code, 200)
        update = client.patch(
            f"/api/campaigns/{self.campaign_a.pk}/", {"nom": "Campaign A admin"}, format="json",
        )
        self.assertEqual(update.status_code, 200)

    def test_campaign_code_sequence_is_scoped_to_organization(self):
        first_a = generate_campaign_code(self.project_a)
        generate_campaign_code(self.project_b)
        self.assertEqual(generate_campaign_code(self.project_a), first_a)

        Campaign.objects.create(
            projet=self.project_a, organization=self.org_a, nom="Generated A",
            code_campagne=first_a, description="Generated code isolation",
            date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
            created_by=self.chef_a,
        )
        next_a = generate_campaign_code(self.project_a)
        first_b = generate_campaign_code(self.project_b)
        self.assertNotEqual(first_b, first_a)
        self.assertIn(f"-O{self.org_a.pk}-", first_a)
        self.assertIn(f"-O{self.org_b.pk}-", first_b)
        self.assertTrue(next_a.endswith("002"))


class AgentZonesMultiTests(TestCase):
    """Un agent peut intervenir dans plusieurs zones de la meme campagne."""

    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Multi",
            email="ong-multi@example.com",
            phone="+221770000001",
            address="Kaolack",
            region="Kaolack",
            country="Sénégal",
            intervention_domain="Solidarité",
        )
        self.chef = User.objects.create_user(
            email="chef-multi@example.com",
            password="password123",
            first_name="Chef",
            last_name="Multi",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.agent = User.objects.create_user(
            email="agent-multi@example.com",
            password="password123",
            first_name="Agent",
            last_name="Multi",
            role=User.Role.AGENT,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        self.project = Project.objects.create(
            name="Projet multi",
            description="Projet multi",
            region="Kaolack",
            objectif="Collecte",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        self.campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne multi",
            code_campagne="CMP-MULTI-001",
            description="Test",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            created_by=self.chef,
        )

    def test_agent_peut_avoir_plusieurs_zones(self):
        # Trois affectations (une par zone) autorisees pour le meme agent.
        for zone in ["Kaolack Centre", "Médina", "Ndorong"]:
            CampagneAffectation.objects.create(
                campagne=self.campaign,
                agent=self.agent,
                zone=zone,
                objectif_beneficiaires=10,
                created_by=self.chef,
            )

        zones = list(
            CampagneAffectation.objects
            .filter(campagne=self.campaign, agent=self.agent)
            .values_list("zone", flat=True)
        )
        self.assertEqual(len(zones), 3)
        self.assertIn("Kaolack Centre", zones)
        self.assertIn("Médina", zones)
        self.assertIn("Ndorong", zones)

    def test_get_affectations_groupees_par_agent(self):
        # Le GET retourne les zones regroupees par agent.
        for zone in ["Kaolack Centre", "Médina"]:
            CampagneAffectation.objects.create(
                campagne=self.campaign,
                agent=self.agent,
                zone=zone,
                objectif_beneficiaires=10,
                created_by=self.chef,
            )

        request = APIRequestFactory().get(
            f"/api/campaigns/{self.campaign.id}/agents/zones/"
        )
        force_authenticate(request, user=self.chef)
        response = CampaignAgentZonesView.as_view()(request, self.campaign.id)

        self.assertEqual(response.status_code, 200)
        affectations = response.data["affectations"]
        self.assertEqual(len(affectations), 1)
        self.assertEqual(affectations[0]["agent"]["id"], str(self.agent.id))
        self.assertCountEqual(affectations[0]["zones"], ["Kaolack Centre", "Médina"])
