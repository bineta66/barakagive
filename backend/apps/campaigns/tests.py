from datetime import date

from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.projects.models import Project
from .agent_views import AgentCampaignListView
from .models import Campaign, CampagneAffectation


class CampagneAffectationTests(TestCase):
	def setUp(self):
		self.organization = Organization.objects.create(
			name="ONG Test",
			email="ong-test@example.com",
			phone="+221770000000",
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
		self.assertEqual([item["nom"] for item in response.data], ["Campagne assignée"])

	def test_affectation_unique_par_campagne_et_agent(self):
		with self.assertRaises(IntegrityError):
			CampagneAffectation.objects.create(
				campagne=self.assigned,
				agent=self.agent,
				zone="Dakar Centre",
				objectif_beneficiaires=10,
				created_by=self.chef,
			)
