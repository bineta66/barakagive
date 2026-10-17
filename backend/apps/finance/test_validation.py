from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.organizations.models import Organization
from apps.projects.models import Project
from apps.campaigns.models import Campaign
from apps.finance.models import Budget, Depense, Bailleur, Partenaire
from apps.zones.models import Region
from django.contrib.gis.geos import Polygon

User = get_user_model()


class DataValidationTestCase(APITestCase):

    def setUp(self):
        self.ong = Organization.objects.create(name="ONG Test", email="contact@ong.org", phone="123")
        self.user = User.objects.create_user(
            email="gerant@ong.org", password="password123",
            first_name="G", last_name="T", role=User.Role.GERANT,
            organization=self.ong, is_active=True
        )
        self.client.force_authenticate(user=self.user)
        
        self.user_chef = User.objects.create_user(
            email="chef@ong.org", password="password123",
            first_name="Chef", last_name="Projet", role=User.Role.CHEF_PROJET,
            organization=self.ong, is_active=True
        )
        self.user_finance = User.objects.create_user(
            email="finance@ong.org", password="password123",
            first_name="Resp", last_name="Fin", role=User.Role.FINANCE,
            organization=self.ong, is_active=True
        )
        
        self.projet = Project.objects.create(
            name="Projet Test", code="PRJ-T", description="Desc",
            region="Dakar", objectif="Obj",
            start_date=date.today(), end_date=date.today(),
            chef_projet=self.user, responsable_finance=self.user,
            organization=self.ong, created_by=self.user
        )
        self.campagne = Campaign.objects.create(
            projet=self.projet, organization=self.ong,
            nom="Campagne Test", code_campagne="CMP-T", description="Desc",
            date_debut=date.today(), date_fin=date.today(),
            created_by=self.user
        )
        self.budget = Budget.objects.create(
            projet=self.projet, montant=10000, source_financement="Source",
            organization=self.ong, created_by=self.user
        )
        poly = Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)))
        self.region = Region.objects.create(nom="Dakar", geometrie=poly)
        self.depense = Depense.objects.create(
            budget=self.budget, campagne=self.campagne, projet=self.projet,
            categorie="Cat", montant=100, organization=self.ong, created_by=self.user
        )

    def test_mandatory_fields(self):
        """1. Champs obligatoires : erreur 400 avec message clair"""
        # Test sur la création de dépense sans catégorie et montant
        data = {
            "date": str(date.today()),
            "budget": str(self.budget.id)
        }
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("montant", response.data)
        self.assertIn("categorie", response.data)

        # Champ vide ou null
        data["categorie"] = ""
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_types(self):
        """2. Types de données : refus de type invalide"""
        # Montant sous forme de chaîne invalide
        data = {
            "categorie": "Catégorie Test",
            "montant": "invalid_number",
            "date": str(date.today())
        }
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("montant", response.data)

    def test_dates_logic(self):
        """3. Vérifier les dates : date_fin >= date_debut"""
        from django.urls import reverse
        data = {
            "name": "Projet Invalide",
            "description": "Desc",
            "objectif": "Obj",
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today()),
            "chef_projet": str(self.user_chef.id),
            "responsable_finance": str(self.user_finance.id),
            "region": "Dakar",
            "criteres": [{"nom": "Critère test", "poids": 100}],
        }
        response = self.client.post(reverse("projects:project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)

    def test_financial_amounts(self):
        """4. Vérifier les montants financiers (montant > 0)"""
        data = {
            "categorie": "Cat",
            "montant": -50,
            "date": str(date.today())
        }
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("montant", response.data)

        data["montant"] = 0
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("montant", response.data)

    def test_choices(self):
        """5. Vérifier les choix (choices) : sexe invalide"""
        from django.urls import reverse
        data = {
            "campagne_id": str(self.campagne.id),
            "zone_id": str(self.region.id),
            "beneficiary": {
                "nom": "Doe",
                "prenom": "John",
                "telephone": "+221770000000",
                "sexe": "INVALID_SEX",
                "date_naissance": "1990-01-01"
            }
        }
        # Assumption: URL is beneficiaries:beneficiary-list
        # Since we just want to test validation, maybe reverse("beneficiaries:beneficiary-list")
        response = self.client.post("/api/beneficiaries/", data, format="json") # Using hardcode but guessing correct path based on typical structure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relations(self):
        """6. Vérifier les relations (ID inexistant)"""
        import uuid
        data = {
            "categorie": "Cat",
            "montant": 100,
            "date": str(date.today()),
            "budget": str(uuid.uuid4()) # ID inexistant
        }
        response = self.client.post("/api/finance/depenses/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("budget", response.data)

    def test_vulnerability_criteria(self):
        """7. Critères de vulnérabilité : somme = 100 et noms uniques"""
        from django.urls import reverse
        data = {
            "name": "Projet Vuln",
            "objectif": "Obj",
            "start_date": str(date.today()),
            "end_date": str(date.today()),
            "chef_projet": str(self.user_chef.id),
            "responsable_finance": str(self.user_finance.id),
            "region": "Dakar",
            "criteres": [
                {"nom": "Crit 1", "poids": 50, "question": "Q1"},
                {"nom": "Crit 2", "poids": 40, "question": "Q2"}
            ]
        }
        response = self.client.post(reverse("projects:project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("criteres", response.data)

        data["criteres"] = [
            {"nom": "Crit 1", "poids": 50, "question": "Q1"},
            {"nom": "Crit 1", "poids": 50, "question": "Q2"}
        ]
        response = self.client.post(reverse("projects:project-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("criteres", response.data)

    def test_file_upload(self):
        """8. Vérifier les fichiers : extension non autorisée"""
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        data = {
            "fichier": invalid_file,
            "type_fichier": "txt"
        }
        # Assuming Justification list create is /api/finance/depenses/<id>/justifications/
        # Or maybe it's /api/finance/justifications/
        response = self.client.post(f"/api/finance/depenses/{self.depense.id}/justifications/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fichier", response.data)

    def test_duplicates(self):
        """9. Vérifier les doublons : email"""
        from django.urls import reverse
        # User create email duplicate
        data = {
            "first_name": "Test",
            "last_name": "Test",
            "email": "gerant@ong.org", # Déjà utilisé
            "role": User.Role.AGENT
        }
        response = self.client.post(reverse("accounts:user-create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_finance_objects_from_another_organization_are_not_addressable_by_id(self):
        foreign_org = Organization.objects.create(
            name="ONG Finance étrangère",
            email="foreign-finance@example.test",
            phone="771234570",
            address="Thiès",
            region="Thiès",
            country="Senegal",
            intervention_domain="Humanitaire",
        )
        foreign_user = User.objects.create_user(
            email="foreign-finance-user@example.test",
            password="SafePass123!",
            role=User.Role.FINANCE,
            organization=foreign_org,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        foreign_project = Project.objects.create(
            name="Projet financier étranger",
            code="PRJ-FOREIGN-FIN",
            description="",
            region="Thiès",
            objectif="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            chef_projet=foreign_user,
            responsable_finance=foreign_user,
            organization=foreign_org,
            created_by=foreign_user,
        )
        foreign_budget = Budget.objects.create(
            projet=foreign_project,
            montant=5000,
            source_financement="Test",
            organization=foreign_org,
            created_by=foreign_user,
        )
        foreign_expense = Depense.objects.create(
            projet=foreign_project,
            budget=foreign_budget,
            categorie="Transport",
            montant=100,
            date=date.today(),
            organization=foreign_org,
            created_by=foreign_user,
        )

        budget_response = self.client.get(f"/api/finance/budgets/{foreign_budget.pk}/")
        expense_response = self.client.get(f"/api/finance/depenses/{foreign_expense.pk}/")
        self.assertEqual(budget_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(expense_response.status_code, status.HTTP_404_NOT_FOUND)
