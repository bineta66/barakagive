from datetime import date
from types import SimpleNamespace
import uuid
from unittest.mock import patch
from django.contrib.gis.geos import Point, Polygon
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.projects.models import Project
from apps.campaigns.models import Campaign, CampagneAffectation
from apps.zones.models import Department, Region, Zone
from apps.beneficiaries.models import Beneficiary, FormResponse
from apps.forms.models import Formulaire
from .views import ProjectRegionsView, RegionPrioritiesView, BeneficiaryListCreateView
from .services import (
    BeneficiaryError,
    validate_agent_permissions,
    validate_form_responses,
)
from .serializers import BeneficiaryCreateSerializer, BeneficiaryUpdateSerializer
from apps.forms.models import FormField
from .permissions import CanManageBeneficiary


class BeneficiaryRelationshipIsolationTests(SimpleTestCase):
    def test_campaign_from_another_organization_is_rejected(self):
        org_a = object()
        org_b = object()
        user = SimpleNamespace(organization=org_a)
        campaign = SimpleNamespace(organization=org_b)

        with self.assertRaisesRegex(BeneficiaryError, "campagne n'appartient pas"):
            validate_agent_permissions(user, campaign, None, None)

    def test_campaign_with_project_from_another_organization_is_rejected(self):
        org = SimpleNamespace(id=1)
        other_org = SimpleNamespace(id=2)
        user = SimpleNamespace(organization=org)
        campaign = SimpleNamespace(
            organization=org,
            organization_id=org.id,
            projet=SimpleNamespace(organization_id=other_org.id),
        )

        with self.assertRaisesRegex(BeneficiaryError, "projet de la campagne"):
            validate_agent_permissions(user, campaign, None, None)


class BeneficiaryValidationBypassTests(SimpleTestCase):
    def test_create_accepts_backend_sex_choices_and_country_code_phone(self):
        base = {
            "campagne_id": str(uuid.uuid4()),
            "zone_id": str(uuid.uuid4()),
            "beneficiary": {
                "nom": "Diallo",
                "prenom": "Aminata",
                "telephone": "+221 77 123 45 67",
                "date_naissance": "1990-01-01",
            },
        }
        for sex in ("F", "M", "AUTRE"):
            with self.subTest(sex=sex):
                serializer = BeneficiaryCreateSerializer(data={
                    **base,
                    "beneficiary": {**base["beneficiary"], "sexe": sex},
                })
                self.assertTrue(serializer.is_valid(), serializer.errors)

        for sex in ("FEMME", "HOMME"):
            with self.subTest(sex=sex):
                serializer = BeneficiaryCreateSerializer(data={
                    **base,
                    "beneficiary": {**base["beneficiary"], "sexe": sex},
                })
                self.assertFalse(serializer.is_valid())

    def test_create_rejects_out_of_range_gps_coordinates(self):
        serializer = BeneficiaryCreateSerializer(data={
            "campagne_id": str(uuid.uuid4()),
            "zone_id": str(uuid.uuid4()),
            "beneficiary": {
                "nom": "Diallo", "prenom": "Aminata", "telephone": "771234567",
                "sexe": "F", "date_naissance": "1990-01-01",
                "latitude": "91", "longitude": "-17.4",
            },
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("beneficiary", serializer.errors)

    def test_update_rejects_out_of_range_gps_coordinates(self):
        serializer = BeneficiaryUpdateSerializer(data={"longitude": "181"}, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("longitude", serializer.errors)

    def test_update_rejects_numeric_name_and_invalid_phone(self):
        serializer = BeneficiaryUpdateSerializer(data={
            "nom": "12345",
            "telephone": "abc",
        }, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertIn("nom", serializer.errors)
        self.assertIn("telephone", serializer.errors)

    def test_update_rejects_future_birth_date(self):
        serializer = BeneficiaryUpdateSerializer(
            data={"date_naissance": "2999-01-01"}, partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_naissance", serializer.errors)

    def test_dynamic_number_answer_rejects_non_numeric_value(self):
        question = SimpleNamespace(
            id=uuid.uuid4(),
            label="Quantité",
            type=FormField.TypeChoices.NUMBER,
            obligatoire=True,
            options=None,
            critere_id=None,
            criteria=SimpleNamespace(all=lambda: []),
        )
        formulaire = SimpleNamespace(
            campagne=SimpleNamespace(
                organization_id=1,
                projet=SimpleNamespace(organization_id=1),
            ),
            organization_id=1,
            fields=SimpleNamespace(
                select_related=lambda *args: SimpleNamespace(all=lambda: [question]),
            ),
        )

        with self.assertRaisesRegex(BeneficiaryError, "nombre valide"):
            validate_form_responses(formulaire, [{
                "question_id": str(question.id),
                "value": "abc",
            }])

    def test_dynamic_answers_reject_question_ids_outside_form(self):
        formulaire = SimpleNamespace(
            campagne=SimpleNamespace(
                organization_id=1,
                projet=SimpleNamespace(organization_id=1),
            ),
            organization_id=1,
            fields=SimpleNamespace(
                select_related=lambda *args: SimpleNamespace(all=lambda: []),
            ),
        )

        with self.assertRaisesRegex(BeneficiaryError, "ne fait pas partie"):
            validate_form_responses(formulaire, [{
                "question_id": str(uuid.uuid4()),
                "value": "answer",
            }])

    @patch("apps.beneficiaries.permissions._agent_is_assigned_to_beneficiary", return_value=True)
    def test_agent_can_manage_only_their_own_beneficiaries_on_apiview(self, is_assigned):
        organization = object()
        agent = SimpleNamespace(
            is_authenticated=True,
            role=User.Role.AGENT,
            organization=organization,
        )
        permission = CanManageBeneficiary()
        view = SimpleNamespace()

        own_beneficiary = SimpleNamespace(organization=organization, created_by=agent)
        other_beneficiary = SimpleNamespace(organization=organization, created_by=object())

        self.assertTrue(permission.has_object_permission(
            SimpleNamespace(user=agent, method="PATCH"), view, own_beneficiary
        ))
        self.assertFalse(permission.has_object_permission(
            SimpleNamespace(user=agent, method="PATCH"), view, other_beneficiary
        ))
        is_assigned.assert_called_once_with(agent, own_beneficiary)

    def test_project_manager_can_manage_only_assigned_campaign_beneficiaries(self):
        organization = object()
        chef = SimpleNamespace(
            is_authenticated=True,
            role=User.Role.CHEF_PROJET,
            organization=organization,
        )
        beneficiary = SimpleNamespace(
            organization=organization,
            campagne=SimpleNamespace(projet=SimpleNamespace(chef_projet=chef)),
        )

        self.assertTrue(CanManageBeneficiary().has_object_permission(
            SimpleNamespace(user=chef, method="PATCH"), SimpleNamespace(), beneficiary
        ))

    def test_manager_cannot_manage_beneficiary(self):
        organization = object()
        manager = SimpleNamespace(
            is_authenticated=True,
            role=User.Role.GERANT,
            organization=organization,
        )
        beneficiary = SimpleNamespace(organization=organization)

        self.assertFalse(CanManageBeneficiary().has_object_permission(
            SimpleNamespace(user=manager, method="PATCH"), SimpleNamespace(), beneficiary
        ))

class CartePrioritesTests(TestCase):
    """Tests des endpoints de la Carte des Priorites."""

    @classmethod
    def setUpTestData(cls):
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        cls.region = Region.objects.create(nom="Dakar", geometrie=polygon)
        cls.department = Department.objects.create(
            nom="Dakar", region=cls.region, geometrie=polygon,
        )
        cls.organization = Organization.objects.create(
            name="ONG Baraka",
            email="baraka-test@example.com",
            phone="+221770000",
            address="Dakar",
            region="Dakar",
            country="Senegal",
            intervention_domain="Solidarite",
        )
        cls.chef = User.objects.create_user(
            email="chef-carte@example.com",
            password="password123",
            first_name="Chef",
            last_name="Carte",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=cls.organization,
        )
        cls.project = Project.objects.create(
            name="Projet Carte",
            description="Projet de test de la carte",
            region="Dakar",
            objectif="Collecte",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=cls.chef,
            responsable_finance=cls.chef,
            organization=cls.organization,
            created_by=cls.chef,
        )

    def _get(self, view_cls, url, *args):
        request = APIRequestFactory().get(url)
        force_authenticate(request, user=self.chef)
        return view_cls.as_view()(request, *args)

    def test_agent_cannot_read_project_wide_priority_map(self):
        agent = User.objects.create_user(
            email="agent-carte@example.com",
            password="password123",
            role=User.Role.AGENT,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        request = APIRequestFactory().get(f"/api/projets/{self.project.pk}/regions/")
        force_authenticate(request, user=agent)
        response = ProjectRegionsView.as_view()(request, self.project.pk)
        self.assertEqual(response.status_code, 403)

    def test_beneficiary_list_uses_paginated_response_shape(self):
        request = APIRequestFactory().get("/api/beneficiaries/?page=1&page_size=10")
        force_authenticate(request, user=self.chef)
        response = BeneficiaryListCreateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
        self.assertIsNone(response.data["next"])

    def test_chef_cannot_read_another_chefs_project_priorities(self):
        other_chef = User.objects.create_user(
            email="autre-chef-carte@example.com",
            password="password123",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.organization,
        )
        request = APIRequestFactory().get(
            f"/api/projets/{self.project.pk}/regions/Dakar/priorites/"
        )
        force_authenticate(request, user=other_chef)
        response = RegionPrioritiesView.as_view()(
            request, self.project.pk, "Dakar",
        )
        self.assertEqual(response.status_code, 404)

    def test_regions_retourne_200_meme_sans_beneficiaire(self):
        """Projet sans aucun beneficiaire : 200 + liste vide, jamais 500."""
        response = self._get(
            ProjectRegionsView,
            f"/api/projets/{self.project.pk}/regions/",
            self.project.pk,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["region"], "Dakar")
        self.assertEqual(response.data[0]["total_beneficiaires"], 0)

    def test_regions_projet_inexistant_renvoie_404(self):
        response = self._get(
            ProjectRegionsView,
            "/api/projets/999/regions/",
            999,
        )
        self.assertEqual(response.status_code, 404)

    def test_priorites_region_sans_beneficiaire_renvoie_200(self):
        """La region existe (declared sur le projet) mais n'a aucun beneficiaire."""
        response = self._get(
            RegionPrioritiesView,
            f"/api/projets/{self.project.pk}/regions/Dakar/priorites/",
            self.project.pk,
            "Dakar",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_beneficiaires"], 0)
        self.assertIsNone(response.data["score_region"])
        self.assertEqual(response.data["zones"], [])

    def test_priorites_region_inconnue_renvoie_404(self):
        response = self._get(
            RegionPrioritiesView,
            f"/api/projets/{self.project.pk}/regions/RegionInexistante/priorites/",
            self.project.pk,
            "RegionInexistante",
        )
        self.assertEqual(response.status_code, 404)

    def test_priorites_projet_inexistant_renvoie_404(self):
        response = self._get(
            RegionPrioritiesView,
            "/api/projets/999/regions/Dakar/priorites/",
            999,
            "Dakar",
        )
        self.assertEqual(response.status_code, 404)

    def _make_zone(self, nom, region="Dakar"):
        zone = Zone.objects.create(
            nom=nom,
            region=self.region,
            departement=self.department,
            latitude=14.6928,
            longitude=-17.4467,
            location=Point(-17.4467, 14.6928, srid=4326),
            rayon=1000,
            organization=self.organization,
            created_by=self.chef,
        )
        # DecimalField values read back from the database have fixed scale.
        zone.refresh_from_db()
        return zone

    def test_priorites_retourne_toutes_les_zones_meme_sans_beneficiaire(self):
        # Toutes les zones de la region doivent apparaitre, meme a 0 beneficiaire.
        self._make_zone("Zone Vide A")
        self._make_zone("Zone Vide B")

        response = self._get(
            RegionPrioritiesView,
            f"/api/projets/{self.project.pk}/regions/Dakar/priorites/",
            self.project.pk,
            "Dakar",
        )
        self.assertEqual(response.status_code, 200)

        zones = response.data["zones"]
        noms = {z["nom"] for z in zones}
        self.assertIn("Zone Vide A", noms)
        self.assertIn("Zone Vide B", noms)
        for zone in zones:
            if zone["nom"].startswith("Zone Vide"):
                self.assertIsNone(zone["score"])
                self.assertIsNone(zone["niveau"])
                self.assertEqual(zone["total_beneficiaires"], 0)
                self.assertEqual(zone["beneficiaires"], [])

    def test_regions_contient_les_zones_geolocalisees_du_projet(self):
        from apps.campaigns.models import Campaign

        zone = self._make_zone("Zone Carte")
        campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.organization,
            nom="Campagne Carte",
            description="Test carte",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            created_by=self.chef,
        )
        campaign.zones.add(zone)

        response = self._get(ProjectRegionsView, f"/api/projets/{self.project.pk}/regions/", self.project.pk)

        self.assertEqual(response.status_code, 200)
        zone_data = response.data[0]["zones"][0]
        self.assertEqual(zone_data["id"], str(zone.pk))
        self.assertEqual(zone_data["latitude"], str(zone.latitude))
        self.assertEqual(zone_data["longitude"], str(zone.longitude))
        self.assertIsNone(zone_data["score_moyen"])


class VulnerabilityScoreCalculationTests(TestCase):
    """
    Tests de vérification du calcul du score de vulnérabilité :
    - 1 critère coché (10 pts) -> score = 10
    - 3 critères cochés (60 pts) -> score = 60
    - Tous les critères cochés (100 pts) -> score = 100
    """

    @classmethod
    def setUpTestData(cls):
        from apps.projects.models import ProjectCriteria
        from apps.campaigns.models import Campaign
        from apps.forms.models import Formulaire, FormField
        from apps.beneficiaries.models import Beneficiary, FormResponse
        import uuid

        cls.org = Organization.objects.create(
            name="ONG Test",
            email="ong@test.com",
            phone="+221770001",
            address="Dakar",
            region="Dakar",
            country="Senegal",
            intervention_domain="Humanitaire",
        )
        cls.chef = User.objects.create_user(
            email="chef-test@example.com",
            password="password123",
            first_name="Chef",
            last_name="Test",
            role=User.Role.CHEF_PROJET,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=cls.org,
        )
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        region = Region.objects.create(nom="Dakar", geometrie=polygon)
        department = Department.objects.create(
            nom="Dakar", region=region, geometrie=polygon,
        )
        cls.zone = Zone.objects.create(
            nom="Zone Test",
            region=region,
            departement=department,
            latitude=14.6928,
            longitude=-17.4467,
            location=Point(-17.4467, 14.6928, srid=4326),
            rayon=1000,
            organization=cls.org,
            created_by=cls.chef,
        )
        cls.project = Project.objects.create(
            name="Projet Score Test",
            description="Test calcul scores",
            region="Dakar",
            objectif="Secours",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=cls.chef,
            responsable_finance=cls.chef,
            organization=cls.org,
            created_by=cls.chef,
        )
        cls.campaign = Campaign.objects.create(
            projet=cls.project,
            organization=cls.org,
            nom="Campagne Test",
            description="Campagne",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            statut=Campaign.Statut.EN_COURS,
            created_by=cls.chef,
        )
        cls.campaign.zones.add(cls.zone)

        cls.formulaire = Formulaire.objects.create(
            campagne=cls.campaign,
            organization=cls.org,
            nom="Formulaire Test",
            statut=Formulaire.Statut.PUBLIE,
            created_by=cls.chef,
        )

        # 5 critères avec poids total = 100 : 30, 25, 20, 15, 10
        criteres_def = [
            ("Sans soutien familial", 30),
            ("Manque de nourriture", 25),
            ("Santé fragile", 20),
            ("Difficulté scolaire", 15),
            ("Besoins spécifiques", 10),
        ]
        cls.fields = []
        cls.criteres = []
        for nom, poids in criteres_def:
            field = FormField.objects.create(
                formulaire=cls.formulaire,
                label=nom,
                type=FormField.TypeChoices.YES_NO,
            )
            critere = ProjectCriteria.objects.create(
                projet=cls.project,
                nom=nom,
                poids=poids,
                question=field,
                created_by=cls.chef,
            )
            cls.fields.append(field)
            cls.criteres.append(critere)

    def _creer_beneficiaire_avec_reponses(self, reponses_bool_list, created_by=None):
        import uuid
        from apps.beneficiaries.models import Beneficiary, FormResponse
        from apps.beneficiaries.services import update_vulnerability_score

        b = Beneficiary.objects.create(
            campagne=self.campaign,
            zone=self.zone,
            organization=self.org,
            nom=f"Nom_{uuid.uuid4().hex[:6]}",
            prenom="Prenom",
            telephone=f"+22177{uuid.uuid4().int % 10000000:07d}",
            sexe=Beneficiary.Sexe.M,
            date_naissance=date(1990, 1, 1),
            latitude=14.69,
            longitude=-17.44,
            local_id=uuid.uuid4(),
            device_id="DEV-TEST",
            created_by=created_by or self.chef,
        )
        for field, is_oui in zip(self.fields, reponses_bool_list):
            FormResponse.objects.create(
                beneficiary=b,
                formulaire=self.formulaire,
                question=field,
                value_boolean=is_oui,
                value_text="Oui" if is_oui else "Non",
            )
        return update_vulnerability_score(b)

    def test_un_seul_critere_coche_donne_10(self):
        """Cas 1 : Uniquement le critère 'Besoins spécifiques' (10 pts) coché Oui -> Score = 10"""
        reponses = [False, False, False, False, True]
        beneficiary = self._creer_beneficiaire_avec_reponses(reponses)
        self.assertEqual(int(beneficiary.score_vulnerabilite), 10)

    def test_trois_criteres_coches_donne_60(self):
        """Cas 2 : 3 critères cochés : 30 + 20 + 10 = 60 pts -> Score = 60"""
        reponses = [True, False, True, False, True]
        beneficiary = self._creer_beneficiaire_avec_reponses(reponses)
        self.assertEqual(int(beneficiary.score_vulnerabilite), 60)

    def test_tous_les_criteres_coches_donne_100(self):
        """Cas 3 : Tous les critères cochés Oui -> Score = 100"""
        reponses = [True, True, True, True, True]
        beneficiary = self._creer_beneficiaire_avec_reponses(reponses)
        self.assertEqual(int(beneficiary.score_vulnerabilite), 100)

    def test_score_normalise_quand_le_total_des_poids_est_inferieur_a_100(self):
        self.project.criteres.update(poids=10)
        beneficiary = self._creer_beneficiaire_avec_reponses([True, False, False, False, False])
        self.assertEqual(int(beneficiary.score_vulnerabilite), 20)

    def test_score_normalise_quand_le_total_des_poids_est_superieur_a_100(self):
        self.project.criteres.update(poids=40)
        beneficiary = self._creer_beneficiaire_avec_reponses([True, False, False, False, False])
        self.assertEqual(int(beneficiary.score_vulnerabilite), 20)

    def test_score_endpoint_uses_metier_name(self):
        from apps.beneficiaries.views import BeneficiaryVulnerabilityScoreView

        beneficiary = self._creer_beneficiaire_avec_reponses(
            [False, False, False, False, True]
        )
        request = APIRequestFactory().post(
            f"/api/beneficiaries/{beneficiary.pk}/vulnerability-score/"
        )
        force_authenticate(request, user=self.chef)

        response = BeneficiaryVulnerabilityScoreView.as_view()(
            request, pk=beneficiary.pk
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score_vulnerabilite"], "10.00")
        self.assertNotIn("ai_score", response.data)

    def test_suspended_project_lead_cannot_recalculate_beneficiary_score(self):
        beneficiary = self._creer_beneficiaire_avec_reponses(
            [False, False, False, False, True]
        )
        access_token = str(RefreshToken.for_user(self.chef).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        active_response = client.post(
            f"/api/beneficiaries/{beneficiary.pk}/vulnerability-score/",
            {}, format="json",
        )
        self.assertEqual(active_response.status_code, 200)

        self.chef.status = User.Status.SUSPENDED
        self.chef.save(update_fields=["status"])
        response = client.post(
            f"/api/beneficiaries/{beneficiary.pk}/vulnerability-score/",
            {}, format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_assigned_agent_can_record_humanitarian_action(self):
        from apps.campaigns.models import CampagneAffectation
        from apps.beneficiaries.models import Beneficiary
        from apps.beneficiaries.views import BeneficiaryActionListCreateView

        agent = User.objects.create_user(
            email="agent-action@example.com",
            password="password123",
            first_name="Agent",
            last_name="Terrain",
            role=User.Role.AGENT,
            status=User.Status.ACTIVE,
            is_active=True,
            organization=self.org,
        )
        CampagneAffectation.objects.create(
            campagne=self.campaign,
            agent=agent,
            zone=self.zone.nom,
            created_by=self.chef,
        )
        beneficiary = self._creer_beneficiaire_avec_reponses(
            [False] * 5,
            created_by=agent,
        )
        request = APIRequestFactory().post(
            f"/api/beneficiaries/{beneficiary.pk}/actions/",
            {
                "type_aide": "ALIMENTAIRE",
                "date_action": "2026-10-01",
                "quantite": "1",
                "statut": "REALISEE",
                "resultat": "Kit remis au bénéficiaire.",
            },
            format="json",
        )
        force_authenticate(request, user=agent)

        response = BeneficiaryActionListCreateView.as_view()(
            request, pk=beneficiary.pk
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["beneficiary"], str(beneficiary.pk))
        self.assertEqual(response.data["campagne"], str(self.campaign.pk))
        self.assertEqual(response.data["agent"]["id"], agent.pk)
        beneficiary.refresh_from_db()
        self.assertEqual(beneficiary.statut, Beneficiary.Statut.PRIS_EN_CHARGE)


class BeneficiaryOrganizationIsolationTests(TestCase):
    """HTTP regressions for tenant boundaries in beneficiary endpoints."""

    def setUp(self):
        self.org_a = self._organization("Beneficiary ONG A", "ben-a")
        self.org_b = self._organization("Beneficiary ONG B", "ben-b")
        self.manager_a = self._user("manager-a", User.Role.GERANT, self.org_a)
        self.manager_b = self._user("manager-b", User.Role.GERANT, self.org_b)
        self.chef_a = self._user("chef-a", User.Role.CHEF_PROJET, self.org_a)
        self.chef_b = self._user("chef-b", User.Role.CHEF_PROJET, self.org_b)
        self.agent_a = self._user("agent-a", User.Role.AGENT, self.org_a)
        self.agent_b = self._user("agent-b", User.Role.AGENT, self.org_b)
        self.super_admin = self._user("super", User.Role.SUPER_ADMIN, None)
        self.project_a, self.zone_a, self.campaign_a, self.form_a = self._tenant_data(
            self.org_a, self.chef_a, "A"
        )
        self.project_b, self.zone_b, self.campaign_b, self.form_b = self._tenant_data(
            self.org_b, self.chef_b, "B"
        )
        self.campaign_a.zones.add(self.zone_a)
        self.campaign_b.zones.add(self.zone_b)
        CampagneAffectation.objects.create(
            campagne=self.campaign_a, agent=self.agent_a, zone=self.zone_a.nom,
            created_by=self.chef_a,
        )
        CampagneAffectation.objects.create(
            campagne=self.campaign_b, agent=self.agent_b, zone=self.zone_b.nom,
            created_by=self.chef_b,
        )
        self.beneficiary_a = self._beneficiary(
            self.org_a, self.campaign_a, self.zone_a, self.agent_a, "A"
        )
        self.beneficiary_b = self._beneficiary(
            self.org_b, self.campaign_b, self.zone_b, self.agent_b, "B"
        )

    @staticmethod
    def _organization(name, prefix):
        return Organization.objects.create(
            name=name, email=f"{prefix}@example.test", phone="771230001",
            address="Dakar", region="Dakar", country="Senegal",
            intervention_domain="Humanitaire", status=Organization.Status.ACTIVE,
            is_active=True,
        )

    @staticmethod
    def _user(prefix, role, organization):
        return User.objects.create_user(
            email=f"{prefix}@example.test", password="SafePass123!",
            first_name="Test", last_name=prefix, role=role,
            organization=organization, status=User.Status.ACTIVE,
            is_active=True, is_staff=role == User.Role.SUPER_ADMIN,
        )

    def _tenant_data(self, organization, chef, suffix):
        project = Project.objects.create(
            name=f"Beneficiary project {suffix}", description="Isolation",
            region=organization.region, objectif="Test",
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            chef_projet=chef, responsable_finance=chef,
            organization=organization, created_by=chef,
        )
        polygon = Polygon(((-18, 12), (-16, 12), (-16, 15), (-18, 15), (-18, 12)), srid=4326)
        region = Region.objects.create(nom=f"Ben Region {suffix}", geometrie=polygon)
        department = Department.objects.create(
            nom=f"Ben Department {suffix}", region=region, geometrie=polygon,
        )
        zone = Zone.objects.create(
            nom=f"Ben Zone {suffix}", region=region, departement=department,
            latitude=14.7, longitude=-17.4,
            location=Point(-17.4, 14.7, srid=4326), rayon=1000,
            organization=organization, created_by=chef,
        )
        campaign = Campaign.objects.create(
            projet=project, organization=organization, nom=f"Ben Campaign {suffix}",
            code_campagne=f"BEN-{suffix}-{organization.pk}",
            description="Isolation test", date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31), created_by=chef,
        )
        form = Formulaire.objects.create(
            campagne=campaign, organization=organization,
            nom=f"Published form {suffix}", statut=Formulaire.Statut.PUBLIE,
            created_by=chef,
        )
        return project, zone, campaign, form

    @staticmethod
    def _beneficiary(organization, campaign, zone, creator, suffix):
        return Beneficiary.objects.create(
            campagne=campaign, zone=zone, organization=organization,
            nom=f"Nom {suffix}", prenom=f"Prenom {suffix}",
            telephone=f"+22177000{suffix}01", sexe=Beneficiary.Sexe.F,
            date_naissance=date(1990, 1, 1), latitude=14.7, longitude=-17.4,
            local_id=uuid.uuid4(), device_id=f"device-{suffix}", created_by=creator,
        )

    @staticmethod
    def _client(user):
        token = str(RefreshToken.for_user(user).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def _sync_payload(self, suffix, campaign, zone, form, **extra):
        return {
            "local_id": str(uuid.uuid4()),
            "device_id": f"sync-{suffix}",
            "campagne_id": str(campaign.pk),
            "formulaire_id": str(form.pk),
            "zone_id": str(zone.pk),
            "beneficiary": {
                "nom": "Collecte Locale", "prenom": "Beneficiaire",
                "telephone": f"+22177{suffix.zfill(7)}", "sexe": "F",
                "date_naissance": "1990-01-01",
            },
            **extra,
        }

    def test_pwa_sync_is_symmetric_and_ignores_foreign_tenant_id_injections(self):
        for user, campaign, zone, form, org, project, suffix in (
            (self.agent_a, self.campaign_a, self.zone_a, self.form_a, self.org_a, self.project_a, "101"),
            (self.agent_b, self.campaign_b, self.zone_b, self.form_b, self.org_b, self.project_b, "102"),
        ):
            response = self._client(user).post(
                "/api/beneficiaries/pwa-sync/",
                self._sync_payload(
                    suffix, campaign, zone, form,
                    organization_id=(self.org_b.pk if org == self.org_a else self.org_a.pk),
                    project_id=(self.project_b.pk if project == self.project_a else self.project_a.pk),
                    agent_id=(self.agent_b.pk if user == self.agent_a else self.agent_a.pk),
                    user_id=(self.agent_b.pk if user == self.agent_a else self.agent_a.pk),
                    beneficiary_id=str(self.beneficiary_b.pk if user == self.agent_a else self.beneficiary_a.pk),
                ),
                format="json",
            )
            self.assertEqual(response.status_code, 201, response.data)
            created = Beneficiary.objects.get(pk=response.data["id"])
            self.assertEqual(created.organization_id, org.pk)
            self.assertEqual(created.campagne_id, campaign.pk)
            self.assertEqual(created.zone_id, zone.pk)
            self.assertEqual(created.created_by_id, user.pk)

    def test_pwa_sync_rejects_foreign_campaign_and_zone_without_mutation(self):
        client_a, client_b = self._client(self.agent_a), self._client(self.agent_b)
        before = Beneficiary.objects.count()
        cases = (
            (client_a, "201", self.campaign_b, self.zone_b, self.form_b),
            (client_b, "202", self.campaign_a, self.zone_a, self.form_a),
        )
        for client, suffix, campaign, zone, form in cases:
            response = client.post(
                "/api/beneficiaries/pwa-sync/",
                self._sync_payload(suffix, campaign, zone, form), format="json",
            )
            self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_same_local_uuid_and_device_are_scoped_to_each_organization(self):
        local_id = uuid.uuid4()
        created_ids = {}
        payload_a = None
        for user, campaign, zone, form, suffix in (
            (self.agent_a, self.campaign_a, self.zone_a, self.form_a, "301"),
            (self.agent_b, self.campaign_b, self.zone_b, self.form_b, "302"),
        ):
            payload = self._sync_payload(suffix, campaign, zone, form)
            payload.update(local_id=str(local_id), device_id="shared-device-id")
            response = self._client(user).post(
                "/api/beneficiaries/pwa-sync", payload, format="json",
            )
            self.assertEqual(response.status_code, 201, response.data)
            created_ids[user.organization_id] = response.data["id"]
            if user == self.agent_a:
                payload_a = payload
        self.assertEqual(
            Beneficiary.objects.filter(local_id=local_id, device_id="shared-device-id").count(), 2,
        )
        self.assertEqual(
            set(Beneficiary.objects.filter(local_id=local_id).values_list("organization_id", flat=True)),
            {self.org_a.pk, self.org_b.pk},
        )
        duplicate = self._client(self.agent_a).post(
            "/api/beneficiaries/pwa-sync", payload_a, format="json",
        )
        self.assertEqual(duplicate.status_code, 200, duplicate.data)
        self.assertEqual(duplicate.data["id"], created_ids[self.org_a.pk])
        self.assertEqual(
            Beneficiary.objects.filter(local_id=local_id, device_id="shared-device-id").count(), 2,
        )

    def test_legacy_sync_rejects_foreign_campaigns_for_both_tenants(self):
        before = Beneficiary.objects.count()
        for user, campaign, zone, form, foreign_campaign, foreign_zone, foreign_form, suffix in (
            (self.agent_a, self.campaign_a, self.zone_a, self.form_a, self.campaign_b, self.zone_b, self.form_b, "401"),
            (self.agent_b, self.campaign_b, self.zone_b, self.form_b, self.campaign_a, self.zone_a, self.form_a, "402"),
        ):
            response = self._client(user).post(
                "/api/beneficiaries/sync/",
                [self._sync_payload(suffix, foreign_campaign, foreign_zone, foreign_form)],
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["failed"], 1)
            self.assertEqual(response.data["synced"], 0)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_agent_sync_rejects_foreign_campaign_for_both_tenants(self):
        before = Beneficiary.objects.count()
        cases = (
            (self.agent_a, self.campaign_b, self.zone_b, self.form_b, "451"),
            (self.agent_b, self.campaign_a, self.zone_a, self.form_a, "452"),
        )
        for user, campaign, zone, form, suffix in cases:
            response = self._client(user).post(
                "/api/agent/synchronisation/",
                [self._sync_payload(suffix, campaign, zone, form)], format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["synced"], [])
            self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_legacy_and_agent_sync_accept_each_tenants_own_records(self):
        for user, campaign, zone, form, suffix, endpoint, wrap_list in (
            (self.agent_a, self.campaign_a, self.zone_a, self.form_a, "601", "/api/beneficiaries/sync/", True),
            (self.agent_b, self.campaign_b, self.zone_b, self.form_b, "602", "/api/beneficiaries/sync/", True),
            (self.agent_a, self.campaign_a, self.zone_a, self.form_a, "603", "/api/agent/synchronisation/", True),
            (self.agent_b, self.campaign_b, self.zone_b, self.form_b, "604", "/api/agent/synchronisation/", True),
        ):
            payload = self._sync_payload(suffix, campaign, zone, form)
            payload["beneficiary"]["nom"] = (
                "Agent Envoi" if endpoint == "/api/agent/synchronisation/"
                else "Offline Envoi"
            )
            response = self._client(user).post(
                endpoint, [payload] if wrap_list else payload, format="json",
            )
            self.assertEqual(response.status_code, 200, response.data)
            if endpoint == "/api/beneficiaries/sync/":
                self.assertEqual(response.data["synced"], 1, response.data)
            else:
                self.assertEqual(len(response.data["synced"]), 1, response.data)
            created = Beneficiary.objects.get(local_id=payload["local_id"])
            self.assertEqual(created.organization_id, user.organization_id)
            self.assertEqual(created.campagne_id, campaign.pk)

    def test_legacy_sync_without_local_id_reports_saved_record_as_synced(self):
        payload = self._sync_payload("605", self.campaign_a, self.zone_a, self.form_a)
        payload.pop("local_id")

        response = self._client(self.agent_a).post(
            "/api/beneficiaries/sync/", [payload], format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["synced"], 1, response.data)
        self.assertEqual(response.data["failed"], 0, response.data)
        created = Beneficiary.objects.get(telephone=payload["beneficiary"]["telephone"])
        self.assertEqual(response.data["details"][0]["local_id"], str(created.local_id))

    def test_legacy_sync_persists_serializer_normalized_values(self):
        payload = self._sync_payload("606", self.campaign_a, self.zone_a, self.form_a)
        payload["beneficiary"]["nom"] = "  Nom Normalise  "

        response = self._client(self.agent_a).post(
            "/api/beneficiaries/sync/", [payload], format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["synced"], 1, response.data)
        created = Beneficiary.objects.get(local_id=payload["local_id"])
        self.assertEqual(created.nom, "Nom Normalise")

    def test_pwa_sync_malformed_list_item_is_rejected_without_crashing_or_mutation(self):
        payload = self._sync_payload("607", self.campaign_a, self.zone_a, self.form_a)
        before = Beneficiary.objects.count()

        response = self._client(self.agent_a).post(
            "/api/beneficiaries/pwa-sync/", [payload, "not-an-object"], format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["synced"], 1, response.data)
        self.assertEqual(response.data["failed"], 1, response.data)
        self.assertEqual(Beneficiary.objects.count(), before + 1)
        self.assertEqual(Beneficiary.objects.filter(local_id=payload["local_id"]).count(), 1)

    def test_pwa_sync_rejects_invalid_local_uuid_before_duplicate_lookup(self):
        payload = self._sync_payload("608", self.campaign_a, self.zone_a, self.form_a)
        payload["local_id"] = "not-a-uuid"
        before = Beneficiary.objects.count()

        response = self._client(self.agent_a).post(
            "/api/beneficiaries/pwa-sync/", payload, format="json",
        )

        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_pwa_sync_rejects_unexpected_fields_without_mutation(self):
        before = Beneficiary.objects.count()
        for payload in (
            self._sync_payload("609", self.campaign_a, self.zone_a, self.form_a, unexpected="x"),
            self._sync_payload(
                "610", self.campaign_a, self.zone_a, self.form_a,
            ),
        ):
            if "unexpected" not in payload:
                payload["beneficiary"]["organization_id"] = self.org_b.pk
            with self.subTest(payload=payload):
                response = self._client(self.agent_a).post(
                    "/api/beneficiaries/pwa-sync/", payload, format="json",
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.assertEqual(Beneficiary.objects.count(), before)

    def test_pwa_sync_rejects_invalid_types_required_values_and_formats_without_mutation(self):
        base = self._sync_payload("611", self.campaign_a, self.zone_a, self.form_a)
        cases = []
        for field, value in (
            ("nom", 123),
            ("prenom", None),
            ("telephone", 771234567),
            ("date_naissance", "19900101"),
            ("date_naissance", "not-a-date"),
            ("sexe", "ABC"),
            ("nom", "   "),
        ):
            payload = {**base, "beneficiary": {**base["beneficiary"], field: value}}
            cases.append(payload)
        missing_required = {**base, "beneficiary": dict(base["beneficiary"])}
        missing_required["beneficiary"].pop("telephone")
        cases.append(missing_required)
        invalid_coordinate = {**base, "beneficiary": {
            **base["beneficiary"], "latitude": "91", "longitude": "-17.4",
        }}
        cases.append(invalid_coordinate)
        invalid_campaign_uuid = {**base, "campagne_id": "invalid-uuid"}
        cases.append(invalid_campaign_uuid)
        missing_campaign = {**base, "campagne_id": str(uuid.uuid4())}
        cases.append(missing_campaign)

        before = Beneficiary.objects.count()
        client = self._client(self.agent_a)
        for index, payload in enumerate(cases):
            payload = {**payload, "local_id": str(uuid.uuid4())}
            with self.subTest(index=index, payload=payload):
                response = client.post(
                    "/api/beneficiaries/pwa-sync/", payload, format="json",
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.assertTrue(response.data.get("detail") or response.data.get("errors"))
                self.assertEqual(Beneficiary.objects.count(), before)

    def test_pwa_sync_rejects_foreign_question_answer_before_any_write(self):
        foreign_question = FormField.objects.create(
            formulaire=self.form_b, label="Réponse de B", type=FormField.TypeChoices.TEXT,
        )
        payload = self._sync_payload("612", self.campaign_a, self.zone_a, self.form_a)
        payload["responses"] = [{
            "question_id": str(foreign_question.pk), "value": "Réponse étrangère",
        }]
        before = Beneficiary.objects.count()

        response = self._client(self.agent_a).post(
            "/api/beneficiaries/pwa-sync/", payload, format="json",
        )

        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Beneficiary.objects.count(), before)
        self.assertEqual(FormResponse.objects.count(), 0)

    def test_service_revalidates_direct_payload_before_writes(self):
        from .services import create_beneficiary_with_responses

        payload = self._sync_payload("613", self.campaign_a, self.zone_a, self.form_a)
        payload["beneficiary"]["nom"] = 123
        before = Beneficiary.objects.count()

        with self.assertRaises(BeneficiaryError):
            create_beneficiary_with_responses(payload, self.agent_a)

        self.assertEqual(Beneficiary.objects.count(), before)

    def test_agent_sync_rejects_invalid_batch_envelopes_without_mutation(self):
        client = self._client(self.agent_a)
        before = Beneficiary.objects.count()
        for payload in ("not-an-object", {"beneficiaires": "not-a-list"}, {}):
            with self.subTest(payload=payload):
                response = client.post(
                    "/api/agent/synchronisation/", payload, format="json",
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.assertEqual(Beneficiary.objects.count(), before)

    def test_sync_rejects_inconsistent_campaign_project_tenant_chain(self):
        before = Beneficiary.objects.count()
        cases = (
            (self.agent_a, self.campaign_a, self.project_b, self.zone_a, self.form_a, "701"),
            (self.agent_b, self.campaign_b, self.project_a, self.zone_b, self.form_b, "702"),
        )
        for user, campaign, foreign_project, zone, form, suffix in cases:
            campaign.projet = foreign_project
            campaign.save(update_fields=["projet"])
            response = self._client(user).post(
                "/api/beneficiaries/pwa-sync/",
                self._sync_payload(suffix, campaign, zone, form), format="json",
            )
            self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_agent_sync_status_excludes_inconsistent_foreign_rows(self):
        valid = self.beneficiary_a
        valid.sync_status = Beneficiary.SyncStatus.PENDING
        valid.save(update_fields=["sync_status"])
        Beneficiary.objects.create(
            campagne=self.campaign_a, zone=self.zone_a, organization=self.org_b,
            nom="Inconsistent sync row", prenom="Hidden", telephone="+221770099991",
            sexe=Beneficiary.Sexe.F, date_naissance=date(1990, 1, 1),
            latitude=14.7, longitude=-17.4, local_id=uuid.uuid4(),
            device_id="inconsistent", created_by=self.agent_a,
            sync_status=Beneficiary.SyncStatus.PENDING,
        )
        response = self._client(self.agent_a).get("/api/agent/synchronisation/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pending"], 1)

    def test_sync_routes_reject_suspended_old_jwts_and_super_admin(self):
        before = Beneficiary.objects.count()
        paths_and_payloads = (
            ("/api/beneficiaries/sync/", [self._sync_payload("501", self.campaign_a, self.zone_a, self.form_a)]),
            ("/api/beneficiaries/pwa-sync/", self._sync_payload("502", self.campaign_a, self.zone_a, self.form_a)),
            ("/api/agent/synchronisation/", [self._sync_payload("503", self.campaign_a, self.zone_a, self.form_a)]),
        )
        for path, payload in paths_and_payloads:
            response = self._client(self.super_admin).post(path, payload, format="json")
            self.assertEqual(response.status_code, 403, (path, response.data))
        suspended_client = self._client(self.agent_a)
        self.agent_a.status = User.Status.SUSPENDED
        self.agent_a.save(update_fields=["status"])
        for path, payload in paths_and_payloads:
            response = suspended_client.post(path, payload, format="json")
            self.assertEqual(response.status_code, 403, (path, response.data))
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_sync_endpoints_are_post_only_and_have_no_delete_or_update_path(self):
        client = self._client(self.agent_a)
        for path in (
            "/api/beneficiaries/sync/",
            "/api/beneficiaries/pwa-sync/",
            "/api/beneficiaries/pwa-sync",
            "/api/agent/synchronisation/",
        ):
            with self.subTest(path=path):
                expected_get_status = 200 if path == "/api/agent/synchronisation/" else 405
                self.assertEqual(client.get(path).status_code, expected_get_status)
                self.assertEqual(client.put(path, {}, format="json").status_code, 405)
                self.assertEqual(client.patch(path, {}, format="json").status_code, 405)
                self.assertEqual(client.delete(path).status_code, 405)

    def assert_denied(self, response):
        self.assertIn(response.status_code, (403, 404), response.status_code)

    def test_manager_a_and_b_list_only_their_beneficiaries(self):
        for user, own, foreign in (
            (self.manager_a, self.beneficiary_a, self.beneficiary_b),
            (self.manager_b, self.beneficiary_b, self.beneficiary_a),
        ):
            response = self._client(user).get("/api/beneficiaries/?page=1&page_size=50")
            self.assertEqual(response.status_code, 200)
            ids = [item["id"] for item in response.data["results"]]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)

    def test_detail_access_is_symmetric_between_organizations(self):
        for user, own, foreign in (
            (self.manager_a, self.beneficiary_a, self.beneficiary_b),
            (self.manager_b, self.beneficiary_b, self.beneficiary_a),
        ):
            client = self._client(user)
            detail_response = client.get(f"/api/beneficiaries/{own.pk}/")
            self.assertEqual(detail_response.status_code, 200)
            payload = detail_response.json()
            self.assertEqual(payload["zone"]["region"], own.zone.region.nom)
            self.assertEqual(payload["zone"]["departement"], own.zone.departement.nom)
            self.assert_denied(client.get(f"/api/beneficiaries/{foreign.pk}/"))

    def test_foreign_campaign_and_zone_injection_is_rejected_on_create(self):
        client = self._client(self.agent_a)
        payload = {
            "campagne_id": str(self.campaign_a.pk), "formulaire_id": str(self.form_a.pk),
            "zone_id": str(self.zone_a.pk), "beneficiary": {
                "nom": "Nouveau", "prenom": "Test", "telephone": "+221771234567",
                "sexe": "F", "date_naissance": "1990-01-01",
            },
        }
        baseline = Beneficiary.objects.count()
        response = client.post(
            "/api/beneficiaries/", {**payload, "organization_id": str(self.org_b.pk),
                                     "project_id": str(self.project_b.pk)}, format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        created = Beneficiary.objects.get(pk=response.data["id"])
        self.assertEqual(created.organization_id, self.org_a.pk)
        self.assertEqual(created.campagne_id, self.campaign_a.pk)
        self.assertEqual(created.zone_id, self.zone_a.pk)
        self.assertEqual(Beneficiary.objects.count(), baseline + 1)

        cross_campaign = client.post(
            "/api/beneficiaries/", {**payload, "campagne_id": str(self.campaign_b.pk)}, format="json",
        )
        self.assertEqual(cross_campaign.status_code, 400, cross_campaign.data)
        cross_zone = client.post(
            "/api/beneficiaries/", {**payload, "zone_id": str(self.zone_b.pk)}, format="json",
        )
        self.assertEqual(cross_zone.status_code, 400, cross_zone.data)
        self.assertEqual(Beneficiary.objects.count(), baseline + 1)

    def test_patch_and_delete_foreign_beneficiary_are_refused_without_mutation(self):
        client = self._client(self.agent_a)
        original = (self.beneficiary_b.nom, self.beneficiary_b.telephone)
        self.assert_denied(client.patch(
            f"/api/beneficiaries/{self.beneficiary_b.pk}/", {"nom": "Intrus"}, format="json"
        ))
        self.assert_denied(client.delete(f"/api/beneficiaries/{self.beneficiary_b.pk}/"))
        self.beneficiary_b.refresh_from_db()
        self.assertEqual((self.beneficiary_b.nom, self.beneficiary_b.telephone), original)
        self.assertTrue(Beneficiary.objects.filter(pk=self.beneficiary_b.pk).exists())

    def test_campaign_and_zone_membership_is_valid_for_both_tenants(self):
        client_a = self._client(self.agent_a)
        client_b = self._client(self.agent_b)
        for client, own, foreign in (
            (client_a, self.beneficiary_a, self.beneficiary_b),
            (client_b, self.beneficiary_b, self.beneficiary_a),
        ):
            self.assertEqual(client.get(f"/api/beneficiaries/{own.pk}/").status_code, 200)
            self.assert_denied(client.get(f"/api/beneficiaries/{foreign.pk}/"))
        before = Beneficiary.objects.count()
        invalid = client_a.post(
            "/api/beneficiaries/",
            {"campagne_id": str(self.campaign_a.pk), "formulaire_id": str(self.form_a.pk),
             "zone_id": str(self.zone_b.pk), "beneficiary": {
                 "nom": "Cross", "prenom": "Zone", "telephone": "+221771234568",
                 "sexe": "F", "date_naissance": "1990-01-01",
             }}, format="json",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(Beneficiary.objects.count(), before)

    def test_project_scope_is_enforced_on_project_region_report(self):
        for user, own, foreign in (
            (self.chef_a, self.project_a, self.project_b),
            (self.chef_b, self.project_b, self.project_a),
        ):
            client = self._client(user)
            self.assertEqual(client.get(f"/api/projets/{own.pk}/regions/").status_code, 200)
            self.assert_denied(client.get(f"/api/projets/{foreign.pk}/regions/"))

    def test_zone_list_and_detail_are_symmetric_between_organizations(self):
        for user, own, foreign in (
            (self.manager_a, self.zone_a, self.zone_b),
            (self.manager_b, self.zone_b, self.zone_a),
        ):
            client = self._client(user)
            listed = client.get("/api/zones/")
            self.assertEqual(listed.status_code, 200)
            ids = [row["id"] for row in listed.data]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)
            self.assertEqual(client.get(f"/api/zones/{own.pk}/").status_code, 200)
            self.assert_denied(client.get(f"/api/zones/{foreign.pk}/"))

    def test_foreign_zone_put_patch_delete_are_refused_without_mutation(self):
        for user, foreign in (
            (self.manager_a, self.zone_b),
            (self.manager_b, self.zone_a),
        ):
            client = self._client(user)
            foreign.refresh_from_db()
            original = (foreign.nom, foreign.organization_id, foreign.latitude)
            self.assert_denied(client.put(
                f"/api/zones/{foreign.pk}/",
                {"nom": "Intrusion", "latitude": 14.8, "longitude": -17.3,
                 "rayon": 1000, "region": foreign.region_id,
                 "departement": foreign.departement_id},
                format="json",
            ))
            self.assert_denied(client.patch(
                f"/api/zones/{foreign.pk}/", {"nom": "Intrusion"}, format="json"
            ))
            self.assert_denied(client.delete(f"/api/zones/{foreign.pk}/"))
            foreign.refresh_from_db()
            # Compare persisted DecimalField values on both sides of the check.
            self.assertEqual(
                (foreign.nom, foreign.organization_id, foreign.latitude), original
            )

    def test_zone_create_ignores_tenant_and_relationship_id_injections(self):
        client = self._client(self.manager_a)
        before = Zone.objects.count()
        response = client.post("/api/zones/", {
            "nom": "Zone créée depuis A",
            "region": self.zone_a.region.nom,
            "departement": self.zone_a.departement.nom,
            "latitude": "14.7000000", "longitude": "-17.4000000", "rayon": 1000,
            "organization_id": self.org_b.pk,
            "project_id": self.project_b.pk,
            "campaign_id": str(self.campaign_b.pk),
            "zone_id": str(self.zone_b.pk),
            "region_id": self.zone_b.region_id,
            "user_id": self.agent_b.pk,
            "agent_id": self.agent_b.pk,
            "beneficiary_id": str(self.beneficiary_b.pk),
        }, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        created = Zone.objects.get(nom="Zone créée depuis A")
        self.assertEqual(created.organization_id, self.org_a.pk)
        self.assertEqual(created.created_by_id, self.manager_a.pk)
        self.assertEqual(Zone.objects.count(), before + 1)

    def test_zone_crud_is_allowed_for_each_owning_organization(self):
        for suffix, user, organization, reference_zone in (
            ("A", self.manager_a, self.org_a, self.zone_a),
            ("B", self.manager_b, self.org_b, self.zone_b),
        ):
            client = self._client(user)
            created = client.post("/api/zones/", {
                "nom": f"Zone CRUD {suffix}",
                "region": reference_zone.region.nom,
                "departement": reference_zone.departement.nom,
                "latitude": "14.7000000", "longitude": "-17.4000000", "rayon": 1000,
            }, format="json")
            self.assertEqual(created.status_code, 201, created.data)
            zone_id = Zone.objects.get(nom=f"Zone CRUD {suffix}", organization=organization).pk
            zone_url = f"/api/zones/{zone_id}/"
            self.assertEqual(client.get(zone_url).status_code, 200)
            updated = client.put(zone_url, {
                "nom": f"Zone CRUD {suffix} modifiée",
                "region": reference_zone.region_id,
                "departement": reference_zone.departement_id,
                "latitude": "14.7100000", "longitude": "-17.4100000", "rayon": 1200,
                "statut": True,
            }, format="json")
            self.assertEqual(updated.status_code, 200, updated.data)
            patched = client.patch(zone_url, {"nom": f"Zone CRUD {suffix} patchée"}, format="json")
            self.assertEqual(patched.status_code, 200, patched.data)
            deleted = client.delete(zone_url)
            self.assertEqual(deleted.status_code, 204)
            self.assertFalse(Zone.objects.filter(pk=zone_id).exists())

    def test_super_admin_can_read_all_zones_but_cannot_mutate_them(self):
        client = self._client(self.super_admin)
        listing = client.get("/api/zones/")
        self.assertEqual(listing.status_code, 200)
        ids = {row["id"] for row in listing.data}
        self.assertIn(str(self.zone_a.pk), ids)
        self.assertIn(str(self.zone_b.pk), ids)
        self.assertEqual(client.get(f"/api/zones/{self.zone_b.pk}/").status_code, 200)
        original_name = self.zone_b.nom
        self.assertEqual(
            client.patch(f"/api/zones/{self.zone_b.pk}/", {"nom": "Admin change"}, format="json").status_code,
            403,
        )
        self.zone_b.refresh_from_db()
        self.assertEqual(self.zone_b.nom, original_name)

    def test_regions_are_global_reference_data_and_get_does_not_create_rows(self):
        before = Region.objects.count()
        response = self._client(self.manager_a).get("/api/regions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Region.objects.count(), before)
        region_ids = {row["id"] for row in response.data}
        self.assertIn(self.zone_a.region_id, region_ids)
        self.assertIn(self.zone_b.region_id, region_ids)

    def test_region_map_filters_inconsistent_cross_organization_relationships(self):
        # Deliberately create impossible links to model legacy/corrupt rows:
        # project/campaign A points to zone B, and a beneficiary joins A to B.
        self.campaign_a.zones.add(self.zone_b)
        inconsistent = self._beneficiary(
            self.org_b, self.campaign_a, self.zone_b, self.agent_b, "Y"
        )
        client = self._client(self.manager_a)
        regions = client.get(f"/api/projets/{self.project_a.pk}/regions/")
        self.assertEqual(regions.status_code, 200, regions.data)
        serialized = str(regions.data)
        self.assertNotIn(self.zone_b.region.nom, serialized)
        self.assertNotIn(self.zone_b.nom, serialized)

        priorities = client.get(
            f"/api/projets/{self.project_a.pk}/regions/{self.zone_b.region.nom}/priorites/"
        )
        self.assertEqual(priorities.status_code, 404)
        self.assertNotIn(str(inconsistent.pk), str(priorities.data))

    def test_pre_suspension_jwt_is_refused_by_region_map_routes(self):
        client = self._client(self.manager_a)
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])
        self.assertEqual(
            client.get(f"/api/projets/{self.project_a.pk}/regions/").status_code, 403
        )
        self.assertEqual(
            client.get(
                f"/api/projets/{self.project_a.pk}/regions/{self.zone_a.region.nom}/priorites/"
            ).status_code,
            403,
        )

    def test_agent_list_is_assignment_and_organization_scoped(self):
        for agent, own, foreign in (
            (self.agent_a, self.beneficiary_a, self.beneficiary_b),
            (self.agent_b, self.beneficiary_b, self.beneficiary_a),
        ):
            response = self._client(agent).get("/api/beneficiaries/?page=1&page_size=50")
            self.assertEqual(response.status_code, 200)
            ids = [item["id"] for item in response.data["results"]]
            self.assertIn(str(own.pk), ids)
            self.assertNotIn(str(foreign.pk), ids)

    def test_agent_cannot_access_foreign_campaign_beneficiary_endpoint(self):
        response = self._client(self.agent_a).get(
            f"/api/agent/campagnes/{self.campaign_b.pk}/beneficiaires/"
        )
        self.assert_denied(response)

    def test_score_endpoint_is_organization_scoped_for_project_leads(self):
        for chef, own, foreign in (
            (self.chef_a, self.beneficiary_a, self.beneficiary_b),
            (self.chef_b, self.beneficiary_b, self.beneficiary_a),
        ):
            client = self._client(chef)
            own_response = client.post(f"/api/beneficiaries/{own.pk}/vulnerability-score/", {}, format="json")
            self.assertEqual(own_response.status_code, 200, own_response.data)
            self.assert_denied(client.post(
                f"/api/beneficiaries/{foreign.pk}/vulnerability-score/", {}, format="json"
            ))

    def test_suspended_agent_and_chef_old_jwts_are_refused(self):
        for user, path in (
            (self.agent_a, "/api/beneficiaries/"),
            (self.chef_a, f"/api/beneficiaries/{self.beneficiary_a.pk}/vulnerability-score/"),
        ):
            client = self._client(user)
            user.status = User.Status.SUSPENDED
            user.save(update_fields=["status"])
            response = client.get(path) if path.endswith("/") and "vulnerability-score" not in path else client.post(path, {}, format="json")
            self.assertEqual(response.status_code, 403)

    def test_inconsistent_foreign_beneficiary_does_not_contaminate_zone_ranking(self):
        inconsistent = self._beneficiary(
            self.org_b, self.campaign_a, self.zone_a, self.agent_b, "X"
        )
        response = self._client(self.manager_a).get(
            f"/api/beneficiaries/zone-ranking/?campaign_id={self.campaign_a.pk}"
        )
        self.assertEqual(response.status_code, 200, response.data)
        ids = [row["id"] for zone in response.data for row in zone["top5"]]
        self.assertNotIn(str(inconsistent.pk), ids)

    def test_super_admin_access_matches_list_endpoint_role_policy(self):
        response = self._client(self.super_admin).get("/api/beneficiaries/?page=1&page_size=50")
        # The list permission admits only AGENT/CHEF_PROJET/GERANT; global admin
        # access is not declared on this endpoint.
        self.assertEqual(response.status_code, 403)

    def test_suspended_manager_is_refused_even_with_preexisting_jwt(self):
        client = self._client(self.manager_a)
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.save(update_fields=["status"])
        self.assertEqual(client.get("/api/beneficiaries/").status_code, 403)
