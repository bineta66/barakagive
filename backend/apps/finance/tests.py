from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from apps.organizations.models import Organization
from apps.projects.models import Project
from apps.campaigns.models import Campaign
from apps.finance.models import (
    Budget, Depense, Justification, Bailleur, Partenaire, LigneBudgetaire,
    Don, Donateur, Financement,
)
from apps.finance.views import build_finance_chat_context
from apps.finance.services import _approved_expenses, _received_for_project
from apps.zones.models import Region
from django.contrib.gis.geos import Polygon
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
import tempfile

User = get_user_model()


class FinanceSecurityTestCase(APITestCase):

    def setUp(self):
        # 1. Créer deux organisations
        self.ong_a = Organization.objects.create(
            name="ONG A", email="contact@onga.org", phone="111", address="A"
        )
        self.ong_b = Organization.objects.create(
            name="ONG B", email="contact@ongb.org", phone="222", address="B"
        )

        # 2. Créer des utilisateurs GÉRANTS pour les deux organisations
        self.user_a = User.objects.create_user(
            email="user_a@onga.org", password="password123",
            first_name="User", last_name="A",
            role=User.Role.GERANT, organization=self.ong_a, is_active=True
        )
        self.user_b = User.objects.create_user(
            email="user_b@ongb.org", password="password123",
            first_name="User", last_name="B",
            role=User.Role.GERANT, organization=self.ong_b, is_active=True
        )
        self.finance_a = User.objects.create_user(
            email="finance@onga.org", password="password123",
            first_name="Finance", last_name="A",
            role=User.Role.FINANCE, organization=self.ong_a, is_active=True,
        )
        self.finance_b = User.objects.create_user(
            email="finance@ongb.org", password="password123",
            first_name="Finance", last_name="B",
            role=User.Role.FINANCE, organization=self.ong_b, is_active=True,
        )

        # 3. Préparer des données pour ONG A
        self.projet_a = Project.objects.create(
            name="Projet A", code="PRJ-A", description="Desc",
            region="Dakar", objectif="Obj",
            start_date=date.today(), end_date=date.today(),
            chef_projet=self.user_a, responsable_finance=self.user_a,
            organization=self.ong_a, created_by=self.user_a
        )
        self.campagne_a = Campaign.objects.create(
            projet=self.projet_a, organization=self.ong_a,
            nom="Campagne A", code_campagne="CMP-A", description="Desc",
            date_debut=date.today(), date_fin=date.today(),
            created_by=self.user_a
        )
        self.budget_a = Budget.objects.create(
            projet=self.projet_a, montant=10000, source_financement="Source A",
            organization=self.ong_a, created_by=self.user_a
        )
        self.ligne_a = LigneBudgetaire.objects.create(
            budget=self.budget_a, libelle="Ligne A", montant_prevu=5000,
            organization=self.ong_a, created_by=self.user_a,
        )

        # Region nécessaire pour la dépense
        poly = Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)))
        self.region = Region.objects.create(nom="Dakar", geometrie=poly)

        self.depense_a = Depense.objects.create(
            budget=self.budget_a, campagne=self.campagne_a,
            projet=self.projet_a, categorie="Cat A", montant=100,
            organization=self.ong_a, created_by=self.user_a
        )

        self.bailleur_a = Bailleur.objects.create(
            nom="Bailleur A", organization=self.ong_a
        )
        self.partenaire_a = Partenaire.objects.create(
            nom="Partenaire A", organization=self.ong_a
        )

        # 4. Préparer des données pour ONG B
        self.projet_b = Project.objects.create(
            name="Projet B", code="PRJ-B", description="Desc",
            region="Thies", objectif="Obj",
            start_date=date.today(), end_date=date.today(),
            chef_projet=self.user_b, responsable_finance=self.user_b,
            organization=self.ong_b, created_by=self.user_b
        )
        self.campagne_b = Campaign.objects.create(
            projet=self.projet_b, organization=self.ong_b,
            nom="Campagne B", code_campagne="CMP-B", description="Desc",
            date_debut=date.today(), date_fin=date.today(),
            created_by=self.user_b
        )
        self.budget_b = Budget.objects.create(
            projet=self.projet_b, montant=20000, source_financement="Source B",
            organization=self.ong_b, created_by=self.user_b
        )
        self.ligne_b = LigneBudgetaire.objects.create(
            budget=self.budget_b, libelle="Ligne B", montant_prevu=10000,
            organization=self.ong_b, created_by=self.user_b,
        )
        self.bailleur_b = Bailleur.objects.create(
            nom="Bailleur B", organization=self.ong_b
        )
        self.partenaire_b = Partenaire.objects.create(
            nom="Partenaire B", organization=self.ong_b
        )
        self.donateur_b = Donateur.objects.create(nom="Donateur B", organization=self.ong_b)
        self.don_b = Don.objects.create(
            donateur=self.donateur_b, campagne=self.campagne_b, montant=1000,
            organization=self.ong_b, created_by=self.user_b,
        )
        self.financement_b = Financement.objects.create(
            projet=self.projet_b, budget=self.budget_b, campagne=self.campagne_b,
            bailleur=self.bailleur_b, montant=1000,
            organization=self.ong_b, created_by=self.user_b,
        )

    def test_access_own_data(self):
        """1. Accès à ses propres données : 200 OK"""
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.get(f"/api/finance/depenses/{self.depense_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suspended_finance_user_cannot_read_expense(self):
        access_token = str(RefreshToken.for_user(self.finance_a).access_token)
        self.finance_a.status = User.Status.SUSPENDED
        self.finance_a.save(update_fields=["status"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(f"/api/finance/depenses/{self.depense_a.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_super_admin_keeps_global_expense_access(self):
        expense_b = Depense.objects.create(
            budget=self.budget_b, campagne=self.campagne_b,
            projet=self.projet_b, categorie="Cat B", montant=50,
            organization=self.ong_b, created_by=self.user_b,
        )
        super_admin = User.objects.create_user(
            email="super-admin-finance@example.test", password="password123",
            first_name="Super", last_name="Admin", role=User.Role.SUPER_ADMIN,
            organization=None, status=User.Status.ACTIVE, is_active=True,
        )
        self.client.force_authenticate(user=super_admin)

        response = self.client.get(f"/api/finance/depenses/{expense_b.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suspended_finance_user_access_to_other_finance_reads(self):
        self.finance_a.status = User.Status.ACTIVE
        self.finance_a.save(update_fields=["status"])
        access_token = str(RefreshToken.for_user(self.finance_a).access_token)
        paths = (
            "/api/finance/dashboard/",
            "/api/finance/lignes-budgetaires/",
            f"/api/finance/lignes-budgetaires/{self.ligne_a.id}/",
            "/api/finance/donateurs/",
            "/api/finance/financements/",
            "/api/finance/budgets/",
            f"/api/finance/budgets/{self.budget_a.id}/",
            "/api/finance/dons/",
            "/api/finance/depenses/",
            "/api/finance/bailleurs/",
            "/api/finance/partenaires/",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        active_statuses = {path: self.client.get(path).status_code for path in paths}
        self.assertTrue(all(code == 200 for code in active_statuses.values()), active_statuses)

        self.finance_a.status = User.Status.SUSPENDED
        self.finance_a.save(update_fields=["status"])
        suspended_statuses = {path: self.client.get(path).status_code for path in paths}
        self.assertTrue(
            all(code == 403 for code in suspended_statuses.values()),
            suspended_statuses,
        )

    def test_finance_assistant_groups_expenses_by_project_region(self):
        self.depense_a.statut = Depense.Status.APPROUVE
        self.depense_a.save(update_fields=["statut"])

        context = build_finance_chat_context(self.finance_a)

        self.assertEqual(context["finances"]["depenses_par_region"], {"Dakar": 100.0})

    def test_financial_creation_requires_form_dates(self):
        self.client.force_authenticate(user=self.finance_a)
        cases = (
            ("/api/finance/budgets/", {
                "projet": self.projet_a.id,
                "montant": 100,
                "source_financement": "Source valide",
            }),
            ("/api/finance/depenses/", {"categorie": "Transport", "montant": 100}),
            ("/api/finance/dons/", {"montant": 100}),
        )
        for endpoint, payload in cases:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("date", response.data)

    def test_financial_creation_rejects_future_form_dates(self):
        self.client.force_authenticate(user=self.finance_a)
        future_date = str(timezone.localdate() + timedelta(days=1))
        cases = (
            ("/api/finance/budgets/", {
                "projet": self.projet_a.id,
                "montant": 100,
                "source_financement": "Source valide",
                "date": future_date,
            }),
            ("/api/finance/depenses/", {
                "categorie": "Transport", "montant": 100, "date": future_date,
            }),
            ("/api/finance/dons/", {"montant": 100, "date": future_date}),
        )
        for endpoint, payload in cases:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("date", response.data)

    def test_finance_role_can_validate_expenses_but_budget_approval_stays_with_manager(self):
        self.client.force_authenticate(user=self.finance_a)

        budget_response = self.client.patch(
            f"/api/finance/budgets/{self.budget_a.id}/",
            {"statut": Budget.Status.APPROUVE},
        )
        self.assertEqual(budget_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("statut", budget_response.data)

        expense_response = self.client.patch(
            f"/api/finance/depenses/{self.depense_a.id}/",
            {"statut": Depense.Status.APPROUVE},
        )
        self.assertEqual(expense_response.status_code, status.HTTP_200_OK, expense_response.data)
        self.depense_a.refresh_from_db()
        self.assertEqual(self.depense_a.statut, Depense.Status.APPROUVE)

        self.client.force_authenticate(user=self.user_a)
        approval = self.client.post("/api/finance/budgets/approval/", {
            "budget_id": str(self.budget_a.id), "action": "APPROVE",
        })
        self.assertEqual(approval.status_code, status.HTTP_200_OK, approval.data)

    def test_received_funding_cannot_exceed_project_budget(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post("/api/finance/financements/", {
            "projet": self.projet_a.pk,
            "budget": str(self.budget_a.pk),
            "montant": "10001",
            "date": str(date.today()),
            "statut": Financement.Status.RECU,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("montant", response.data)

    def test_donation_cannot_overfund_project_after_received_funding(self):
        self.client.force_authenticate(user=self.finance_a)
        financing = self.client.post("/api/finance/financements/", {
            "projet": self.projet_a.pk,
            "budget": str(self.budget_a.pk),
            "montant": "10000",
            "date": str(date.today()),
            "statut": Financement.Status.RECU,
        }, format="json")
        self.assertEqual(financing.status_code, status.HTTP_201_CREATED, financing.data)
        response = self.client.post("/api/finance/dons/", {
            "campagne": str(self.campagne_a.pk),
            "montant": "1",
            "date": str(date.today()),
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("montant", response.data)

    def test_approved_expense_cannot_exceed_budget_or_line(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post("/api/finance/depenses/", {
            "projet": self.projet_a.pk,
            "budget": str(self.budget_a.pk),
            "ligne_budgetaire": str(self.ligne_a.pk),
            "categorie": "Transport",
            "montant": "5001",
            "date": str(date.today()),
            "statut": Depense.Status.APPROUVE,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("montant", response.data)

    def test_financing_update_replaces_old_amount_in_available_calculation(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post("/api/finance/financements/", {
            "projet": self.projet_a.pk,
            "budget": str(self.budget_a.pk),
            "montant": "5000",
            "date": str(date.today()),
            "statut": Financement.Status.RECU,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        updated = self.client.patch(
            f"/api/finance/financements/{response.data['id']}/",
            {"montant": "7000"}, format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK, updated.data)

    def test_justification_status_cannot_be_marked_conformant_at_upload(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post(
            f"/api/finance/depenses/{self.depense_a.id}/justifications/",
            {
                "fichier": SimpleUploadedFile(
                    "recu.pdf", b"%PDF-1.4\nRecu de test", content_type="application/pdf"
                ),
                "type_fichier": "pdf",
                "statut": "CONFORME",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        justification = Justification.objects.get(pk=response.data["id"])
        self.assertEqual(justification.statut, Justification.Status.A_VERIFIER)

    def test_isolation_between_orgs(self):
        """2. Isolation entre organisations : ONG B ne peut pas lire les données de ONG A (404)"""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(f"/api/finance/depenses/{self.depense_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_justification_document_is_private_across_indirect_finance_relations(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            justification = Justification.objects.create(
                depense=self.depense_a,
                fichier=SimpleUploadedFile(
                    "recu.pdf", b"%PDF-1.4\nRecu ONG A", content_type="application/pdf"
                ),
                type_fichier="pdf",
                uploaded_by=self.finance_a,
            )
            url = f"/api/finance/justifications/{justification.pk}/document/"

            self.client.force_authenticate(user=None)
            self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

            self.client.force_authenticate(user=self.finance_a)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4\nRecu ONG A")

            self.client.force_authenticate(user=self.finance_b)
            self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_justification_upload_is_tenant_scoped_and_requires_active_account(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            url_a = f"/api/finance/depenses/{self.depense_a.id}/justifications/"
            def payload():
                return {
                    "fichier": SimpleUploadedFile(
                        "recu.pdf", b"%PDF-1.4\nRecu ONG A", content_type="application/pdf"
                    ),
                    "type_fichier": "pdf",
                }

            self.client.force_authenticate(user=self.finance_b)
            foreign_upload = self.client.post(url_a, payload(), format="multipart")
            self.assertEqual(foreign_upload.status_code, status.HTTP_404_NOT_FOUND)

            self.client.force_authenticate(user=self.finance_a)
            own_upload = self.client.post(url_a, payload(), format="multipart")
            self.assertEqual(own_upload.status_code, status.HTTP_201_CREATED, own_upload.data)
            document_url = f"/api/finance/justifications/{own_upload.data['id']}/document/"

            self.finance_a.status = User.Status.SUSPENDED
            self.finance_a.is_active = False
            self.finance_a.save(update_fields=["status", "is_active"])
            self.client.force_authenticate(user=self.finance_a)
            suspended_upload = self.client.post(url_a, payload(), format="multipart")
            self.assertEqual(suspended_upload.status_code, status.HTTP_403_FORBIDDEN)
            suspended_download = self.client.get(document_url)
            self.assertEqual(suspended_download.status_code, status.HTTP_403_FORBIDDEN)

    def test_justification_upload_rejects_oversized_extension_and_signature(self):
        self.client.force_authenticate(user=self.finance_a)
        url = f"/api/finance/depenses/{self.depense_a.id}/justifications/"
        invalid_files = (
            SimpleUploadedFile("recu.exe", b"MZ executable", content_type="application/octet-stream"),
            SimpleUploadedFile("recu.pdf", b"not a PDF", content_type="application/pdf"),
            SimpleUploadedFile(
                "grand.pdf", b"%PDF-" + b"x" * (10 * 1024 * 1024),
                content_type="application/pdf",
            ),
        )
        for invalid_file in invalid_files:
            with self.subTest(filename=invalid_file.name):
                response = self.client.post(
                    url,
                    {"fichier": invalid_file, "type_fichier": "pdf"},
                    format="multipart",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Justification.objects.count(), 0)

    def test_bailleur_rejects_invalid_email_and_phone(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post("/api/finance/bailleurs/", {
            "nom": "Bailleur valide",
            "type": "National",
            "email": "adresse-invalide",
            "telephone": "abc",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("telephone", response.data)

    def test_partenaire_rejects_invalid_email(self):
        self.client.force_authenticate(user=self.finance_a)
        response = self.client.post("/api/finance/partenaires/", {
            "nom": "Partenaire valide",
            "domaine": "Santé",
            "email": "adresse-invalide",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_modification_interdite(self):
        """3. Modification interdite : ONG B ne peut pas modifier la dépense de ONG A"""
        self.client.force_authenticate(user=self.finance_b)
        response = self.client.patch(f"/api/finance/depenses/{self.depense_a.id}/", {"montant": 500})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_suppression_interdite(self):
        """4. Suppression interdite : ONG B ne peut pas supprimer la dépense de ONG A"""
        self.client.force_authenticate(user=self.finance_b)
        response = self.client.delete(f"/api/finance/depenses/{self.depense_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_creation_with_foreign_organization_id(self):
        """5. Création avec une organisation étrangère est bloquée ou ignorée"""
        self.client.force_authenticate(user=self.finance_a)

        # Test avec la vue Bailleurs
        data = {
            "nom": "Bailleur Hack",
            "email": "bailleur-hack@example.com",
            "type": "Institutionnel",
            "organization_id": str(self.ong_b.id),
            "organization": str(self.ong_b.id),
        }
        response = self.client.post("/api/finance/bailleurs/", data)
        # S'il renvoie 400 Validation Error grâce à reject_foreign_organization_payload
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("organization", response.data)
        else:
            # S'il crée quand même (car le serializer ignore le payload), on vérifie l'organisation forcée
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            bailleur = Bailleur.objects.get(id=response.data["id"])
            self.assertEqual(bailleur.organization, self.ong_a)
            self.assertNotEqual(bailleur.organization, self.ong_b)

    def test_depense_with_foreign_budget_or_campaign(self):
        """6. Dépense avec budget étranger : User A tente de créer une dépense avec un budget de ONG B"""
        self.client.force_authenticate(user=self.finance_a)
        data = {
            "categorie": "Hack",
            "montant": 500,
            "date": str(date.today()),
            "budget": str(self.budget_b.id),
            "campagne": str(self.campagne_a.id),
        }
        response = self.client.post("/api/finance/depenses/", data)
        # Doit être refusé (400)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("budget", response.data)

        # Idem avec campagne_id de ONG B
        data = {
            "categorie": "Hack 2",
            "montant": 500,
            "date": str(date.today()),
            "budget": str(self.budget_a.id),
            "campagne": str(self.campagne_b.id),
        }
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campagne", response.data)

    def test_expense_create_validates_all_relation_ids_and_project_lineage(self):
        self.client.force_authenticate(user=self.finance_a)
        base = {
            "categorie": "Achat", "montant": 500, "date": str(date.today()),
            "projet": str(self.projet_a.id), "campagne": str(self.campagne_a.id),
            "budget": str(self.budget_a.id), "ligne_budgetaire": str(self.ligne_a.id),
        }
        valid = self.client.post("/api/finance/depenses/", base)
        self.assertEqual(valid.status_code, status.HTTP_201_CREATED, valid.data)

        for relation, foreign_id, expected_field in (
            ("projet", self.projet_b.id, "projet"),
            ("campagne", self.campagne_b.id, "campagne"),
            ("budget", self.budget_b.id, "budget"),
            ("ligne_budgetaire", self.ligne_b.id, "ligne_budgetaire"),
        ):
            with self.subTest(relation=relation):
                response = self.client.post(
                    "/api/finance/depenses/", {**base, relation: str(foreign_id)}
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(expected_field, response.data)

        # Even records carrying ONG A's organization cannot link to an ONG B project.
        self.campagne_a.projet = self.projet_b
        self.campagne_a.save(update_fields=["projet"])
        inconsistent = self.client.post("/api/finance/depenses/", base)
        self.assertEqual(inconsistent.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expense_update_rejects_foreign_and_inconsistent_relations(self):
        self.client.force_authenticate(user=self.finance_a)
        self.depense_a.ligne_budgetaire = self.ligne_a
        self.depense_a.save(update_fields=["ligne_budgetaire"])

        for relation, foreign_id in (
            ("projet", self.projet_b.id),
            ("campagne", self.campagne_b.id),
            ("budget", self.budget_b.id),
            ("ligne_budgetaire", self.ligne_b.id),
        ):
            with self.subTest(relation=relation):
                response = self.client.patch(
                    f"/api/finance/depenses/{self.depense_a.id}/",
                    {relation: str(foreign_id)},
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # A same-organization line from a different budget must also be refused.
        other_budget = Budget.objects.create(
            projet=self.projet_a, montant=5000, source_financement="Autre",
            organization=self.ong_a, created_by=self.user_a,
        )
        other_line = LigneBudgetaire.objects.create(
            budget=other_budget, libelle="Autre ligne", montant_prevu=1000,
            organization=self.ong_a, created_by=self.user_a,
        )
        response = self.client.patch(
            f"/api/finance/depenses/{self.depense_a.id}/",
            {"ligne_budgetaire": str(other_line.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_financial_relations_cannot_cross_organizations(self):
        self.client.force_authenticate(user=self.finance_a)
        line_response = self.client.post("/api/finance/lignes-budgetaires/", {
            "budget": str(self.budget_b.id), "libelle": "Injected", "montant_prevu": 100,
        })
        self.assertEqual(line_response.status_code, status.HTTP_400_BAD_REQUEST)

        financing_response = self.client.post("/api/finance/financements/", {
            "projet": str(self.projet_a.id), "budget": str(self.budget_a.id),
            "campagne": str(self.campagne_a.id), "bailleur": str(self.bailleur_b.id),
            "montant": 1000,
        })
        self.assertEqual(financing_response.status_code, status.HTTP_400_BAD_REQUEST)

        donation_response = self.client.post("/api/finance/dons/", {
            "donateur": str(self.donateur_b.id), "campagne": str(self.campagne_a.id),
            "montant": 1000,
        })
        self.assertEqual(donation_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_foreign_financial_objects_cannot_be_read_or_deleted(self):
        self.client.force_authenticate(user=self.finance_a)
        for path in (
            f"/api/finance/budgets/{self.budget_b.id}/",
            f"/api/finance/financements/{self.financement_b.id}/",
            f"/api/finance/dons/{self.don_b.id}/",
            f"/api/finance/lignes-budgetaires/{self.ligne_b.id}/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(self.client.delete(path).status_code, status.HTTP_404_NOT_FOUND)

    def test_reads_hide_own_financial_rows_with_foreign_relations(self):
        self.client.force_authenticate(user=self.user_a)
        invalid_budget = Budget.objects.create(
            projet=self.projet_b, montant=1000, source_financement="Mismatch",
            organization=self.ong_a, created_by=self.user_a,
        )
        invalid_line = LigneBudgetaire.objects.create(
            budget=self.budget_b, libelle="Mismatch", montant_prevu=100,
            organization=self.ong_a, created_by=self.user_a,
        )
        invalid_expense = Depense.objects.create(
            budget=self.budget_b, projet=self.projet_a, ligne_budgetaire=self.ligne_b,
            campagne=self.campagne_b, categorie="Mismatch", montant=100,
            organization=self.ong_a, created_by=self.user_a,
        )
        invalid_financing = Financement.objects.create(
            projet=self.projet_a, budget=self.budget_a, bailleur=self.bailleur_b,
            montant=100, organization=self.ong_a, created_by=self.user_a,
        )
        invalid_donation = Don.objects.create(
            donateur=self.donateur_b, campagne=self.campagne_a, montant=100,
            organization=self.ong_a, created_by=self.user_a,
        )

        paths = (
            f"/api/finance/budgets/{invalid_budget.id}/",
            f"/api/finance/lignes-budgetaires/{invalid_line.id}/",
            f"/api/finance/depenses/{invalid_expense.id}/",
            f"/api/finance/financements/{invalid_financing.id}/",
            f"/api/finance/dons/{invalid_donation.id}/",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, status.HTTP_404_NOT_FOUND)

    def test_bailleur_and_partenaire_autocomplete_is_paginated_and_tenant_scoped(self):
        self.client.force_authenticate(user=self.user_a)

        bailleurs = self.client.get(
            "/api/finance/bailleurs/?search=Bailleur&page=1&page_size=20"
        )
        partenaires = self.client.get(
            "/api/finance/partenaires/?search=Partenaire&page=1&page_size=20"
        )

        self.assertEqual(bailleurs.status_code, status.HTTP_200_OK)
        self.assertEqual(bailleurs.data["count"], 1)
        self.assertEqual([item["id"] for item in bailleurs.data["results"]], [str(self.bailleur_a.id)])
        self.assertEqual(partenaires.status_code, status.HTTP_200_OK)
        self.assertEqual(partenaires.data["count"], 1)
        self.assertEqual([item["id"] for item in partenaires.data["results"]], [str(self.partenaire_a.id)])

    def test_bailleur_et_partenaire_foreign_access(self):
        """7. Bailleur et partenaire : ONG A ne peut pas lire/modifier ceux de ONG B"""
        self.client.force_authenticate(user=self.finance_a)

        # Tentative de lecture
        response_read = self.client.get(f"/api/finance/bailleurs/{self.bailleur_b.id}/")
        self.assertEqual(response_read.status_code, status.HTTP_404_NOT_FOUND)

        response_read_part = self.client.get(f"/api/finance/partenaires/{self.partenaire_b.id}/")
        self.assertEqual(response_read_part.status_code, status.HTTP_404_NOT_FOUND)

        # Tentative de modification
        response_patch = self.client.patch(f"/api/finance/bailleurs/{self.bailleur_b.id}/", {"nom": "Hack"})
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND)

    def test_dashboard_finance_ne_compte_que_les_flux_recus_et_valides(self):
        self.client.force_authenticate(user=self.finance_a)
        self.budget_a.statut = Budget.Status.APPROUVE
        self.budget_a.save(update_fields=["statut"])

        self.depense_a.statut = Depense.Status.APPROUVE
        self.depense_a.save(update_fields=["statut"])
        Depense.objects.create(
            budget=self.budget_a,
            projet=self.projet_a,
            categorie="En attente",
            montant=900,
            statut=Depense.Status.EN_ATTENTE,
            organization=self.ong_a,
            created_by=self.user_a,
        )

        Financement.objects.create(
            projet=self.projet_a,
            budget=self.budget_a,
            montant=2000,
            statut=Financement.Status.RECU,
            organization=self.ong_a,
            created_by=self.user_a,
        )
        Financement.objects.create(
            projet=self.projet_a,
            budget=self.budget_a,
            montant=1500,
            statut=Financement.Status.CONFIRME,
            organization=self.ong_a,
            created_by=self.user_a,
        )
        Don.objects.create(
            campagne=self.campagne_a,
            montant=1000,
            organization=self.ong_a,
            created_by=self.user_a,
        )

        response = self.client.get("/api/finance/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["budget_total"], 10000.0)
        self.assertEqual(response.data["financements_recus"], 2000.0)
        self.assertEqual(response.data["dons_recus"], 1000.0)
        self.assertEqual(response.data["depenses_validees"], 100.0)
        self.assertEqual(response.data["solde"], 2900.0)
        self.assertEqual(response.data["taux_financement"], 30.0)
        self.assertEqual(response.data["taux_execution"], 1.0)

    def test_shared_finance_services_ignore_cross_organization_indirect_relations(self):
        malformed_campaign = Campaign.objects.create(
            projet=self.projet_a,
            organization=self.ong_b,
            nom="Inconsistent foreign campaign",
            code_campagne="CMP-FOREIGN-LINK",
            description="Test fixture with a deliberately inconsistent tenant chain",
            date_debut=date.today(),
            date_fin=date.today(),
            created_by=self.user_b,
        )
        Don.objects.create(
            campagne=malformed_campaign,
            montant=700,
            organization=self.ong_a,
            created_by=self.user_a,
        )
        Depense.objects.create(
            projet=self.projet_a,
            campagne=malformed_campaign,
            categorie="Foreign campaign link",
            montant=800,
            statut=Depense.Status.APPROUVE,
            organization=self.ong_a,
            created_by=self.user_a,
        )

        self.assertEqual(_received_for_project(self.projet_a), 0)
        self.assertEqual(_approved_expenses(self.projet_a), 0)
