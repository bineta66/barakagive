import uuid
from datetime import date, timedelta
from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.projects.models import Project
from apps.campaigns.models import Campaign
from apps.zones.models import Zone
from apps.beneficiaries.models import Beneficiary
from apps.finance.models import Don, Budget, Depense
from apps.zones.models import Region, Department
from apps.ia.views import compute_assistant_dashboard


class AssistantDashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(
            name="ONG Solidarité Sénégal",
            email="contact@solidarite.sn",
            phone="+221771234567",
            address="Dakar",
            region="Dakar",
            intervention_domain="Aide alimentaire",
        )
        self.gerant = User.objects.create_user(
            email="gerant@solidarite.sn",
            password="Password123!",
            role="GERANT",
            organization=self.org,
            first_name="Amadou",
            last_name="Ba",
            is_active=True,
            status=User.Status.ACTIVE,
        )
        self.chef_projet = User.objects.create_user(
            email="cp@solidarite.sn",
            password="Password123!",
            role="CHEF_PROJET",
            organization=self.org,
            first_name="Chef",
            last_name="Projet",
            is_active=True,
            status=User.Status.ACTIVE,
        )
        self.finance_user = User.objects.create_user(
            email="fin@solidarite.sn",
            password="Password123!",
            role="FINANCE",
            organization=self.org,
            first_name="Finance",
            last_name="User",
            is_active=True,
            status=User.Status.ACTIVE,
        )

        # Create Project
        self.project = Project.objects.create(
            name="Programme Vivres & Santé",
            description="Assistance alimentaire et médicale",
            region="Kaolack",
            objectif="Secourir 500 familles",
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=60),
            chef_projet=self.chef_projet,
            responsable_finance=self.finance_user,
            organization=self.org,
            created_by=self.gerant,
        )

        # Create GIS region, department and zone
        geometry = Polygon.from_bbox((-18, 12, -15, 16))
        geometry.srid = 4326
        self.region = Region.objects.create(nom="Kaolack", geometrie=geometry)
        self.department = Department.objects.create(
            nom="Kaolack", region=self.region, geometrie=geometry,
        )
        self.zone = Zone.objects.create(
            nom="Zone Kaolack Centre",
            region=self.region,
            departement=self.department,
            latitude=14.137,
            longitude=-16.073,
            location=Point(-16.073, 14.137, srid=4326),
            rayon=5000,
            organization=self.org,
            created_by=self.gerant,
        )

        # Create Campaign
        self.campaign = Campaign.objects.create(
            projet=self.project,
            organization=self.org,
            nom="Distribution Alimentaire Kaolack",
            description="Distribution mensuelle de kits",
            date_debut=timezone.now().date() - timedelta(days=10),
            date_fin=timezone.now().date() + timedelta(days=5),
            statut=Campaign.Statut.EN_COURS,
            created_by=self.chef_projet,
        )
        self.campaign.zones.add(self.zone)

        # Create Beneficiaries
        self.ben1 = Beneficiary.objects.create(
            campagne=self.campaign,
            zone=self.zone,
            organization=self.org,
            nom="Diop",
            prenom="Fatou",
            telephone="+221770001122",
            sexe="F",
            date_naissance=date(1985, 4, 12),
            latitude=14.138,
            longitude=-16.072,
            local_id=uuid.uuid4(),
            device_id="DEV-001",
            score_vulnerabilite=85.0,
            created_by=self.gerant,
        )
        self.ben2 = Beneficiary.objects.create(
            campagne=self.campaign,
            zone=self.zone,
            organization=self.org,
            nom="Fall",
            prenom="Mamadou",
            telephone="+221770001133",
            sexe="M",
            date_naissance=date(1978, 1, 25),
            latitude=14.139,
            longitude=-16.071,
            local_id=uuid.uuid4(),
            device_id="DEV-001",
            score_vulnerabilite=60.0,
            created_by=self.gerant,
        )

        # Create current finance records
        self.don = Don.objects.create(
            organization=self.org,
            campagne=self.campaign,
            montant=50000000.0,
            date=timezone.now().date() - timedelta(days=20),
            created_by=self.gerant,
        )
        self.budget = Budget.objects.create(
            organization=self.org,
            projet=self.project,
            montant=50000000.0,
            source_financement="Don Fondation Espoir",
            statut=Budget.Status.APPROUVE,
            created_by=self.finance_user,
        )
        self.depense = Depense.objects.create(
            organization=self.org,
            projet=self.project,
            categorie="Alimentation",
            montant=15000000.0,
            date=timezone.now().date() - timedelta(days=5),
            statut=Depense.Status.APPROUVE,
            created_by=self.finance_user,
        )

    def test_compute_assistant_dashboard(self):
        data = compute_assistant_dashboard(self.gerant)
        self.assertEqual(data["projets_actifs"], 1)
        self.assertEqual(data["campagnes_actives"], 1)
        self.assertEqual(data["beneficiaires"], 2)
        self.assertEqual(data["budget_total"], 50000000.0)
        self.assertEqual(data["depenses"], 15000000.0)
        self.assertEqual(data["solde"], 35000000.0)
        self.assertEqual(data["campagne_prioritaire"]["region"], "Kaolack")
        self.assertIsInstance(data["alertes"], list)
        self.assertIsInstance(data["recommandations"], list)
        self.assertIn("generated_at", data)

    def test_api_endpoint_assistant_dashboard(self):
        self.client.force_authenticate(user=self.gerant)
        response = self.client.get("/api/assistant/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["projets_actifs"], 1)
        self.assertEqual(data["campagnes_actives"], 1)
        self.assertEqual(data["beneficiaires"], 2)
        self.assertEqual(data["budget_total"], 50000000.0)
        self.assertEqual(data["depenses"], 15000000.0)
        self.assertEqual(data["solde"], 35000000.0)

    def test_suspended_manager_cannot_access_assistant_dashboard(self):
        access_token = str(RefreshToken.for_user(self.gerant).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.assertEqual(
            self.client.get("/api/assistant/dashboard/").status_code,
            status.HTTP_200_OK,
        )

        self.gerant.status = User.Status.SUSPENDED
        self.gerant.save(update_fields=["status"])
        response = self.client.get("/api/assistant/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access(self):
        response = self.client.get("/api/assistant/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
