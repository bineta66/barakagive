from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.finance.models import Budget
from apps.organizations.models import Organization
from .models import Project, ProjectCriteria
from .serializers import BudgetUpdateSerializer, ProjectCriteriaCreateSerializer, ProjectSerializer
from .permissions import CanManageProjectCriteria

# Create your tests here.


class ProjectInputValidationTests(SimpleTestCase):
    def test_budget_update_rejects_negative_amount(self):
        serializer = BudgetUpdateSerializer(data={"budget": "-1"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("budget", serializer.errors)

    def test_criteria_rejects_weight_above_hundred(self):
        serializer = ProjectCriteriaCreateSerializer(data={
            "nom": "Critère valide",
            "poids": 150,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("poids", serializer.errors)

    def test_project_patch_checks_date_against_existing_counterpart(self):
        instance = SimpleNamespace(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 30),
        )
        serializer = ProjectSerializer(
            instance,
            data={"end_date": "2026-05-31"},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_date", serializer.errors)

    def test_project_patch_rejects_blank_name(self):
        instance = SimpleNamespace(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        serializer = ProjectSerializer(instance, data={"name": "   "}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_project_patch_accepts_optional_blank_description(self):
        instance = SimpleNamespace(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        serializer = ProjectSerializer(instance, data={"description": ""}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class ProjectCriteriaPermissionTests(SimpleTestCase):
    def test_only_managers_and_project_leads_can_write_criteria(self):
        permission = CanManageProjectCriteria()
        request = SimpleNamespace(method="PATCH", user=SimpleNamespace(role="AGENT"))
        self.assertFalse(permission.has_permission(request, SimpleNamespace()))

        request.user.role = "FINANCE"
        self.assertFalse(permission.has_permission(request, SimpleNamespace()))

        request.user.role = "GERANT"
        self.assertTrue(permission.has_permission(request, SimpleNamespace()))

    def test_project_lead_can_change_only_their_own_project_criteria(self):
        permission = CanManageProjectCriteria()
        chef = SimpleNamespace(role="CHEF_PROJET")
        request = SimpleNamespace(method="PATCH", user=chef)
        criterion = SimpleNamespace(projet=SimpleNamespace(chef_projet=chef))
        other_criterion = SimpleNamespace(projet=SimpleNamespace(chef_projet=object()))

        self.assertTrue(permission.has_object_permission(request, SimpleNamespace(), criterion))
        self.assertFalse(permission.has_object_permission(request, SimpleNamespace(), other_criterion))


class ProjectBudgetPersistenceTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Budget",
            email="budget@example.test",
            phone="771234567",
            address="Dakar",
            region="Dakar",
            country="Sénégal",
            intervention_domain="Humanitaire",
        )
        self.user = User.objects.create_user(
            email="chef-budget@example.test",
            password="SafePass123!",
            first_name="Aminata",
            last_name="Diallo",
            role=User.Role.GERANT,
            organization=self.organization,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        self.project = Project.objects.create(
            name="Projet Budget",
            description="Test",
            region="Dakar",
            objectif="Test",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.user,
            responsable_finance=self.user,
            organization=self.organization,
            created_by=self.user,
        )

    def test_project_budget_patch_persists_in_finance_budget_model(self):
        serializer = ProjectSerializer(
            self.project,
            data={"budget": "250000.00"},
            partial=True,
            context={"request": SimpleNamespace(user=self.user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        allocation = Budget.objects.get(
            projet=self.project,
            source_financement="Allocation projet",
        )
        self.assertEqual(allocation.montant, Decimal("250000.00"))
        self.assertEqual(Decimal(serializer.data["budget"]), Decimal("250000.00"))


class ProjectDashboardScopeTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ONG Dashboard",
            email="dashboard@example.test",
            phone="771234568",
            address="Dakar",
            region="Dakar",
            country="Senegal",
            intervention_domain="Humanitaire",
        )
        self.chef = User.objects.create_user(
            email="chef-dashboard@example.test",
            password="SafePass123!",
            role=User.Role.CHEF_PROJET,
            organization=self.organization,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        self.other_chef = User.objects.create_user(
            email="other-chef-dashboard@example.test",
            password="SafePass123!",
            role=User.Role.CHEF_PROJET,
            organization=self.organization,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        self.project = Project.objects.create(
            name="Projet du chef",
            description="",
            region="Dakar",
            objectif="Pilotage",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        Project.objects.create(
            name="Projet autre chef",
            description="",
            region="Dakar",
            objectif="Autre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.other_chef,
            responsable_finance=self.other_chef,
            organization=self.organization,
            created_by=self.other_chef,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.chef)

    def test_dashboard_returns_real_empty_metrics_and_only_assigned_project(self):
        response = self.client.get("/api/projects/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["operationnel"]["projets"], 1)
        self.assertEqual(response.data["operationnel"]["projets_actifs"], 1)
        self.assertEqual(response.data["operationnel"]["taux_prise_en_charge"], 0)
        self.assertEqual(response.data["operationnel"]["taux_realisation_campagnes"], 0)
        self.assertEqual(response.data["beneficiaires_par_niveau"], {
            "total": 0,
            "evalues": 0,
            "prioritaires": 0,
            "pris_en_charge": 0,
            "taux_evalues": 0,
            "taux_prioritaires": 0,
            "taux_pris_en_charge": 0,
        })
        self.assertEqual([item["id"] for item in response.data["filtres"]["projets"]], [self.project.pk])
        self.assertEqual(response.data["beneficiaires_prioritaires"], [])
        self.assertEqual(response.data["activites_recentes"], [])

    def test_gerant_dashboard_includes_project_states_and_only_own_organization_users(self):
        gerant = User.objects.create_user(
            email="gerant-dashboard@example.test",
            password="SafePass123!",
            role=User.Role.GERANT,
            organization=self.organization,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        other_organization = Organization.objects.create(
            name="Autre ONG Dashboard",
            email="autre-dashboard@example.test",
            phone="771234569",
            address="Thies",
            region="Thies",
            country="Senegal",
            intervention_domain="Humanitaire",
        )
        outsider = User.objects.create_user(
            email="outsider-dashboard@example.test",
            password="SafePass123!",
            role=User.Role.AGENT,
            organization=other_organization,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        self.client.force_authenticate(gerant)

        response = self.client.get("/api/projects/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(sum(row["total"] for row in response.data["graphiques"]["projets_statuts"]), 2)
        self.assertEqual(response.data["utilisateurs"]["total"], 3)
        self.assertNotIn(outsider.pk, [row["id"] for row in response.data["utilisateurs"]["recents"]])

    def test_dashboard_rejects_project_outside_chef_scope(self):
        other_project = Project.objects.get(name="Projet autre chef")
        response = self.client.get("/api/projects/dashboard/", {"project_id": other_project.pk})

        self.assertEqual(response.status_code, 404)

    def test_project_list_returns_paginated_project_results(self):
        Project.objects.create(
            name="Second project for pagination",
            description="",
            region="Dakar",
            objectif="Test",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            chef_projet=self.chef,
            responsable_finance=self.chef,
            organization=self.organization,
            created_by=self.chef,
        )
        response = self.client.get("/api/projects/?page=1&page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])

    def test_suspended_project_lead_cannot_read_project_list(self):
        access_token = str(RefreshToken.for_user(self.chef).access_token)
        self.chef.status = User.Status.SUSPENDED
        self.chef.save(update_fields=["status"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get("/api/projects/")

        self.assertEqual(response.status_code, 403)

    def test_suspended_project_lead_is_denied_on_project_mutation_methods(self):
        self.chef.status = User.Status.SUSPENDED
        self.chef.save(update_fields=["status"])
        self.client.force_authenticate(self.chef)
        project_url = f"/api/projects/{self.project.pk}/"
        cases = (
            ("post", "/api/projects/", {}),
            ("patch", project_url, {"name": "Blocked"}),
            ("delete", project_url, None),
            ("patch", f"/api/projects/{self.project.pk}/budget/", {"budget": 100}),
            ("get", f"/api/projets/{self.project.pk}/criteres/", None),
            ("post", f"/api/projets/{self.project.pk}/criteres/", {}),
            ("get", "/api/criteres/1/", None),
            ("patch", "/api/criteres/1/", {"nom": "Blocked"}),
            ("delete", "/api/criteres/1/", None),
        )

        for method, url, payload in cases:
            with self.subTest(method=method, url=url):
                request = getattr(self.client, method)
                if payload is None:
                    response = request(url)
                else:
                    response = request(url, payload, format="json")
                self.assertEqual(response.status_code, 403)

    def test_manager_active_and_suspended_access_to_project_list(self):
        manager = User.objects.create_user(
            email="manager-projects@example.test", password="SafePass123!",
            role=User.Role.GERANT, organization=self.organization,
            status=User.Status.ACTIVE, is_active=True,
        )
        self.client.force_authenticate(manager)
        self.assertEqual(self.client.get("/api/projects/").status_code, 200)

        manager.status = User.Status.SUSPENDED
        manager.save(update_fields=["status"])
        self.client.force_authenticate(manager)
        self.assertEqual(self.client.get("/api/projects/").status_code, 403)

    def test_finance_active_and_suspended_access_to_assigned_project_list(self):
        finance = User.objects.create_user(
            email="finance-projects@example.test", password="SafePass123!",
            role=User.Role.FINANCE, organization=self.organization,
            status=User.Status.ACTIVE, is_active=True,
        )
        self.project.responsable_finance = finance
        self.project.save(update_fields=["responsable_finance"])

        self.client.force_authenticate(finance)
        active_response = self.client.get("/api/projects/")
        self.assertEqual(active_response.status_code, 200)
        self.assertEqual(active_response.data["count"], 1)

        finance.status = User.Status.SUSPENDED
        finance.save(update_fields=["status"])
        self.client.force_authenticate(finance)
        self.assertEqual(self.client.get("/api/projects/").status_code, 403)

    def test_active_super_admin_keeps_global_project_list_access(self):
        super_admin = User.objects.create_user(
            email="superadmin-projects@example.test", password="SafePass123!",
            role=User.Role.SUPER_ADMIN, organization=None,
            status=User.Status.ACTIVE, is_active=True,
        )
        self.client.force_authenticate(super_admin)

        response = self.client.get("/api/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_project_id_search_stays_inside_chef_scope(self):
        other_project = Project.objects.get(name="Projet autre chef")
        response = self.client.get(f"/api/projects/?ids={other_project.pk}&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(f"/api/projects/?ids={self.project.pk}&page=1&page_size=20")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.project.pk)

    @patch("apps.projects.views.post_to_ai_service")
    def test_dashboard_assistant_receives_only_aggregated_filtered_context(self, post):
        post.return_value.json.return_value = {
            "answer": "Un projet est dans le filtre.",
            "sources": ["PostgreSQL (Temps reel)"],
            "generated_at": "2026-10-01T00:00:00Z",
        }
        response = self.client.post(
            f"/api/projects/dashboard/chat/?project_id={self.project.pk}",
            {"question": "Resume la situation"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        context = post.call_args.kwargs["payload"]["context"]
        self.assertEqual(context["operationnel"]["projets"], 1)
        self.assertEqual(context["filtres"]["project_id"], str(self.project.pk))
        self.assertNotIn("beneficiaires_prioritaires", context)


class ProjectOrganizationIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(
            name="ONG Isolation A", email="isolation-a@example.test",
            phone="771234801", address="Dakar", region="Dakar",
            country="Senegal", intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG Isolation B", email="isolation-b@example.test",
            phone="771234802", address="Thies", region="Thies",
            country="Senegal", intervention_domain="Education",
        )
        self.chef_a = self._chef("chef-a-isolation@example.test", self.org_a)
        self.chef_b = self._chef("chef-b-isolation@example.test", self.org_b)
        self.finance_b = User.objects.create_user(
            email="finance-b-isolation@example.test", password="SafePass123!",
            role=User.Role.FINANCE, organization=self.org_b,
            status=User.Status.ACTIVE, is_active=True,
        )
        self.manager_b = User.objects.create_user(
            email="manager-b-isolation@example.test", password="SafePass123!",
            role=User.Role.GERANT, organization=self.org_b,
            status=User.Status.ACTIVE, is_active=True,
        )
        self.project_a = self._project("Projet ONG A", self.org_a, self.chef_a)
        self.project_b = self._project("Projet ONG B", self.org_b, self.chef_b)
        self.budget_a = Budget.objects.create(
            projet=self.project_a, organization=self.org_a, montant=Decimal("1250.00"),
            source_financement="Allocation test A", created_by=self.chef_a,
        )
        self.criteria_a = ProjectCriteria.objects.create(
            projet=self.project_a, nom="Critere A", poids=100, created_by=self.chef_a,
        )
        access_token = str(RefreshToken.for_user(self.chef_b).access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    @staticmethod
    def _chef(email, organization):
        return User.objects.create_user(
            email=email, password="SafePass123!", first_name="Chef", last_name="ONG",
            role=User.Role.CHEF_PROJET, organization=organization,
            status=User.Status.ACTIVE, is_active=True,
        )

    @staticmethod
    def _project(name, organization, chef):
        return Project.objects.create(
            name=name, description="Projet de test inter-ONG", region="Dakar",
            objectif="Test d'isolation", start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31), chef_projet=chef,
            responsable_finance=chef, organization=organization, created_by=chef,
        )

    def _assert_not_found_or_forbidden(self, response):
        self.assertIn(response.status_code, (403, 404), response.data)

    def test_chef_b_project_list_and_detail_do_not_expose_project_a(self):
        list_response = self.client.get("/api/projects/?page=1&page_size=50")
        self.assertEqual(list_response.status_code, 200)
        listed_ids = [item["id"] for item in list_response.data["results"]]
        self.assertIn(self.project_b.pk, listed_ids)
        self.assertNotIn(self.project_a.pk, listed_ids)

        response = self.client.get(f"/api/projects/{self.project_a.pk}/")
        self._assert_not_found_or_forbidden(response)

    def test_chef_b_cannot_patch_or_archive_project_a(self):
        url = f"/api/projects/{self.project_a.pk}/"
        response = self.client.patch(url, {"name": "Projet modifie par ONG B"}, format="json")
        self._assert_not_found_or_forbidden(response)
        response = self.client.delete(url)
        self._assert_not_found_or_forbidden(response)

        self.project_a.refresh_from_db()
        self.assertEqual(self.project_a.name, "Projet ONG A")
        self.assertFalse(self.project_a.archived)

    def test_chef_b_cannot_change_project_a_budget(self):
        response = self.client.patch(
            f"/api/projects/{self.project_a.pk}/budget/", {"budget": "999999.00"},
            format="json",
        )
        self._assert_not_found_or_forbidden(response)
        self.budget_a.refresh_from_db()
        self.assertEqual(self.budget_a.montant, Decimal("1250.00"))
        self.assertEqual(Budget.objects.filter(projet=self.project_a).count(), 1)

    def test_chef_b_cannot_list_or_create_criteria_on_project_a(self):
        list_response = self.client.get(f"/api/projets/{self.project_a.pk}/criteres/")
        self._assert_not_found_or_forbidden(list_response)

        before = ProjectCriteria.objects.filter(projet=self.project_a).count()
        create_response = self.client.post(
            f"/api/projets/{self.project_a.pk}/criteres/",
            {"nom": "Critere injecte B", "poids": 1}, format="json",
        )
        self._assert_not_found_or_forbidden(create_response)
        self.assertEqual(ProjectCriteria.objects.filter(projet=self.project_a).count(), before)

    def test_chef_b_cannot_read_change_or_delete_criterion_a(self):
        url = f"/api/criteres/{self.criteria_a.pk}/"
        self._assert_not_found_or_forbidden(self.client.get(url))
        self._assert_not_found_or_forbidden(
            self.client.patch(url, {"nom": "Critere modifie B"}, format="json")
        )
        self._assert_not_found_or_forbidden(self.client.delete(url))

        self.criteria_a.refresh_from_db()
        self.assertEqual(self.criteria_a.nom, "Critere A")
        self.assertEqual(self.criteria_a.poids, 100)
        self.assertTrue(self.criteria_a.actif)

    def test_chef_b_cannot_inject_foreign_organization_or_assignees_on_create(self):
        project_count = Project.objects.count()
        common = {
            "name": "Tentative ONG B", "description": "", "region": "Thies",
            "objectif": "Test", "start_date": "2026-01-01", "end_date": "2026-12-31",
            "responsable_finance": self.finance_b.pk,
            "criteres": [{"nom": "Critere", "poids": 100}],
        }
        manager_token = str(RefreshToken.for_user(self.manager_b).access_token)
        manager_client = APIClient()
        manager_client.credentials(HTTP_AUTHORIZATION=f"Bearer {manager_token}")
        foreign_org_response = manager_client.post(
            "/api/projects/", {**common, "chef_projet": self.chef_b.pk,
                               "organization_id": self.org_a.pk}, format="json",
        )
        self.assertEqual(foreign_org_response.status_code, 400)

        foreign_assignee_response = manager_client.post(
            "/api/projects/", {**common, "chef_projet": self.chef_a.pk}, format="json",
        )
        self.assertEqual(foreign_assignee_response.status_code, 400)
        self.assertEqual(Project.objects.count(), project_count)

    def test_chef_a_and_chef_b_can_read_own_projects_but_not_each_others(self):
        client_a = APIClient()
        token_a = str(RefreshToken.for_user(self.chef_a).access_token)
        client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {token_a}")

        self.assertEqual(client_a.get(f"/api/projects/{self.project_a.pk}/").status_code, 200)
        self._assert_not_found_or_forbidden(
            client_a.get(f"/api/projects/{self.project_b.pk}/")
        )
        self.assertEqual(self.client.get(f"/api/projects/{self.project_b.pk}/").status_code, 200)
        self._assert_not_found_or_forbidden(
            self.client.get(f"/api/projects/{self.project_a.pk}/")
        )

    def test_active_super_admin_can_list_projects_from_both_organizations(self):
        super_admin = User.objects.create_user(
            email="superadmin-isolation@example.test", password="SafePass123!",
            first_name="Super", last_name="Admin", role=User.Role.SUPER_ADMIN,
            status=User.Status.ACTIVE, is_active=True,
        )
        access_token = str(RefreshToken.for_user(super_admin).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = client.get("/api/projects/?page=1&page_size=50")

        self.assertEqual(response.status_code, 200)
        listed_ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.project_a.pk, listed_ids)
        self.assertIn(self.project_b.pk, listed_ids)
