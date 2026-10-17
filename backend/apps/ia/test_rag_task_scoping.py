from datetime import date
import uuid
from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.beneficiaries.models import Beneficiary
from apps.campaigns.models import Campaign
from apps.organizations.models import Organization
from apps.projects.models import Project
from apps.zones.models import Department, Region, Zone
from apps.ia.tasks import index_data_for_rag, run_ia_analyses


class RAGTaskOrganizationScopeTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="ONG A", email="rag-a@example.test", phone="770000041",
            address="Dakar", region="Dakar", intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG B", email="rag-b@example.test", phone="770000042",
            address="Thiès", region="Thiès", intervention_domain="Humanitaire",
        )
        self.manager_a = User.objects.create_user(
            email="rag-manager-a@example.test", password="SafePass123!",
            role=User.Role.GERANT, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_a,
        )
        self.manager_b = User.objects.create_user(
            email="rag-manager-b@example.test", password="SafePass123!",
            role=User.Role.GERANT, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_b,
        )
        chef_a = User.objects.create_user(
            email="rag-chef-a@example.test", password="SafePass123!",
            role=User.Role.CHEF_PROJET, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_a,
        )
        finance_a = User.objects.create_user(
            email="rag-finance-a@example.test", password="SafePass123!",
            role=User.Role.FINANCE, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_a,
        )
        project_a = Project.objects.create(
            name="Projet RAG A", description="", region="Dakar",
            objectif="Aider les familles", start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31), chef_projet=chef_a,
            responsable_finance=finance_a, organization=self.org_a,
            created_by=self.manager_a,
        )
        chef_b = User.objects.create_user(
            email="rag-chef-b@example.test", password="SafePass123!",
            role=User.Role.CHEF_PROJET, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_b,
        )
        finance_b = User.objects.create_user(
            email="rag-finance-b@example.test", password="SafePass123!",
            role=User.Role.FINANCE, status=User.Status.ACTIVE, is_active=True,
            organization=self.org_b,
        )
        project_b = Project.objects.create(
            name="Projet RAG B", description="", region="Thiès",
            objectif="Aider les familles", start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31), chef_projet=chef_b,
            responsable_finance=finance_b, organization=self.org_b,
            created_by=self.manager_b,
        )
        self.project_b = project_b
        campaign_a = Campaign.objects.create(
            projet=project_a, organization=self.org_a, nom="Campagne RAG A",
            code_campagne="RAG-A-001", description="Test de cloisonnement RAG",
            date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
            created_by=self.manager_a,
        )
        self.inconsistent_campaign = Campaign.objects.create(
            projet=project_b, organization=self.org_a, nom="Campagne incohérente",
            code_campagne="RAG-A-BAD", description="Must not enter ONG A index",
            date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
            created_by=self.manager_a,
        )
        polygon = Polygon((
            (-18, 14), (-16, 14), (-16, 16), (-18, 16), (-18, 14),
        ), srid=4326)
        region = Region.objects.create(nom="Région RAG", geometrie=polygon)
        department = Department.objects.create(
            nom="Département RAG", region=region, geometrie=polygon,
        )
        self.zone_a = Zone.objects.create(
            nom="Zone RAG A", region=region, departement=department,
            latitude=15, longitude=-17, location=Point(-17, 15, srid=4326),
            rayon=1, organization=self.org_a, created_by=self.manager_a,
        )
        campaign_a.zones.add(self.zone_a)

        Beneficiary.objects.create(
            campagne=campaign_a, zone=self.zone_a, organization=self.org_a,
            nom="Diallo", prenom="ONG A", telephone="770000044",
            sexe="F", date_naissance=date(1990, 1, 1), latitude=15,
            longitude=-17, local_id=uuid.uuid4(), device_id="rag-test",
            created_by=self.manager_a,
        )

        # Reproduce an inconsistent relation that can be created outside the
        # validated HTTP serializers: ONG B beneficiary attached to ONG A zone.
        Beneficiary.objects.create(
            campagne=campaign_a, zone=self.zone_a, organization=self.org_b,
            nom="Bénéficiaire", prenom="ONG B", telephone="770000043",
            sexe="F", date_naissance=date(1990, 1, 1), latitude=15,
            longitude=-17, local_id=uuid.uuid4(), device_id="rag-test",
            created_by=self.manager_a,
        )

    @override_settings(IA_SERVICE_URL="http://ia-service")
    @patch("apps.ia.tasks.post_to_ai_service")
    def test_rag_zone_document_excludes_foreign_organization_beneficiaries(self, post):
        post.return_value = Mock(
            status_code=200, json=Mock(return_value={}), raise_for_status=Mock(),
        )

        index_data_for_rag()

        payload_a = next(
            call.kwargs["payload"] for call in post.call_args_list
            if call.kwargs["payload"]["tenant"]["organization_id"] == self.org_a.pk
        )
        zone_document = next(
            text for text, metadata in zip(
                payload_a["documents"], payload_a["metadatas"],
            ) if metadata["type"] == "zone" and metadata["id"] == str(self.zone_a.pk)
        )
        self.assertIn("Nombre de bénéficiaires: 1", zone_document)
        self.assertTrue(all(
            metadata["organization_id"] == self.org_a.pk
            for metadata in payload_a["metadatas"]
        ))
        self.assertNotIn(f"campaign_{self.inconsistent_campaign.pk}", payload_a["ids"])

    @override_settings(IA_SERVICE_URL="http://ia-service")
    @patch("apps.ia.tasks.post_to_ai_service")
    def test_rag_builds_separate_valid_batches_for_both_organizations(self, post):
        post.return_value = Mock(
            status_code=200, json=Mock(return_value={}), raise_for_status=Mock(),
        )
        campaign_b = Campaign.objects.create(
            projet=self.project_b, organization=self.org_b, nom="Campagne RAG B",
            code_campagne="RAG-B-001", description="Données ONG B",
            date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
            created_by=self.manager_b,
        )
        zone_b = Zone.objects.create(
            nom="Zone RAG B", region=self.zone_a.region,
            departement=self.zone_a.departement, latitude=15, longitude=-17,
            location=Point(-17, 15, srid=4326), rayon=1,
            organization=self.org_b, created_by=self.manager_b,
        )
        campaign_b.zones.add(zone_b)
        Beneficiary.objects.create(
            campagne=campaign_b, zone=zone_b, organization=self.org_b,
            nom="Fall", prenom="ONG B", telephone="770000045", sexe="F",
            date_naissance=date(1990, 1, 1), latitude=15, longitude=-17,
            local_id=uuid.uuid4(), device_id="rag-test", created_by=self.manager_b,
        )

        index_data_for_rag()

        payloads = {
            call.kwargs["payload"]["tenant"]["organization_id"]: call.kwargs["payload"]
            for call in post.call_args_list
        }
        self.assertEqual(set(payloads), {self.org_a.pk, self.org_b.pk})
        self.assertIn(f"campaign_{campaign_b.pk}", payloads[self.org_b.pk]["ids"])
        self.assertNotIn(f"campaign_{campaign_b.pk}", payloads[self.org_a.pk]["ids"])
        self.assertTrue(all(
            metadata["organization_id"] == self.org_b.pk
            for metadata in payloads[self.org_b.pk]["metadatas"]
        ))

    @override_settings(IA_SERVICE_URL="http://ia-service")
    @patch("apps.ia.tasks.compute_finance_payload", return_value={"finance": True})
    @patch("apps.ia.tasks.compute_executive_payload", return_value={"executive": True})
    @patch("apps.ia.tasks.post_to_ai_service")
    def test_scheduled_analysis_skips_campaign_with_foreign_project(self, post, _executive, _finance):
        post.return_value = Mock(
            status_code=200, json=Mock(return_value={}), raise_for_status=Mock(),
        )
        valid_campaign = Campaign.objects.get(nom="Campagne RAG A")
        valid_campaign.statut = Campaign.Statut.EN_COURS
        valid_campaign.save(update_fields=["statut"])
        self.inconsistent_campaign.statut = Campaign.Statut.EN_COURS
        self.inconsistent_campaign.save(update_fields=["statut"])

        result = run_ia_analyses()

        self.assertEqual(result, 1)
        post.assert_called_once()
        _executive.assert_called_once_with(valid_campaign)
        _finance.assert_called_once_with(valid_campaign)
        self.assertEqual(post.call_args.kwargs["payload"], {
            "executive": True, "finance": True,
        })

    @override_settings(IA_SERVICE_URL="http://ia-service")
    @patch("apps.ia.tasks.compute_finance_payload", side_effect=lambda campaign: {"finance_id": str(campaign.pk)})
    @patch("apps.ia.tasks.compute_executive_payload", side_effect=lambda campaign: {"executive_id": str(campaign.pk)})
    @patch("apps.ia.tasks.post_to_ai_service")
    def test_scheduled_analysis_processes_each_valid_tenant_campaign(self, post, _executive, _finance):
        post.return_value = Mock(
            status_code=200, json=Mock(return_value={}), raise_for_status=Mock(),
        )
        campaign_a = Campaign.objects.get(nom="Campagne RAG A")
        campaign_b = Campaign.objects.create(
            projet=self.project_b, organization=self.org_b, nom="Campagne active B",
            code_campagne="RAG-B-002", description="Analyse ONG B",
            date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
            created_by=self.manager_b, statut=Campaign.Statut.EN_COURS,
        )
        campaign_a.statut = Campaign.Statut.EN_COURS
        campaign_a.save(update_fields=["statut"])

        result = run_ia_analyses()

        self.assertEqual(result, 2)
        sent_campaign_ids = {
            call.kwargs["payload"]["finance_id"] for call in post.call_args_list
        }
        self.assertEqual(sent_campaign_ids, {str(campaign_a.pk), str(campaign_b.pk)})
