import tempfile
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import ActivationToken, User
from apps.organizations.models import Organization, OrganisationRequest


class OrganizationReadIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org_a = Organization.objects.create(
            name="ONG A",
            email="a@example.test",
            phone="+221771234567",
            address="Dakar",
            region="Dakar",
            intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG B",
            email="b@example.test",
            phone="+221771234568",
            address="Thiès",
            region="Thiès",
            intervention_domain="Santé",
        )
        self.manager_a = User.objects.create_user(
            email="manager-a@example.test",
            password="Password123!",
            first_name="Awa",
            last_name="Diop",
            role=User.Role.GERANT,
            organization=self.org_a,
            status=User.Status.ACTIVE,
            is_active=True,
        )
        self.super_admin = User.objects.create_user(
            email="admin@example.test",
            password="Password123!",
            first_name="Super",
            last_name="Admin",
            role=User.Role.SUPER_ADMIN,
            is_active=True,
            is_staff=True,
        )

    def test_organization_list_requires_authentication(self):
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_only_lists_own_organization(self):
        manager_b = User.objects.create_user(
            email="manager-b@example.test", password="Password123!",
            first_name="Moussa", last_name="Ba", role=User.Role.GERANT,
            organization=self.org_b, status=User.Status.ACTIVE, is_active=True,
        )
        for manager, organization in ((self.manager_a, self.org_a), (manager_b, self.org_b)):
            self.client.force_authenticate(manager)
            response = self.client.get("/api/organizations/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual([item["id"] for item in response.data], [organization.id])

    def test_manager_cannot_read_another_organization(self):
        manager_b = User.objects.create_user(
            email="manager-b@example.test", password="Password123!",
            first_name="Moussa", last_name="Ba", role=User.Role.GERANT,
            organization=self.org_b, status=User.Status.ACTIVE, is_active=True,
        )
        for manager, own, foreign in (
            (self.manager_a, self.org_a, self.org_b),
            (manager_b, self.org_b, self.org_a),
        ):
            self.client.force_authenticate(manager)
            self.assertEqual(self.client.get(f"/api/organizations/{own.id}/").status_code, status.HTTP_200_OK)
            initial_foreign_name = foreign.name
            response = self.client.get(f"/api/organizations/{foreign.id}/")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            for method in (self.client.put, self.client.patch, self.client.delete):
                self.assertEqual(method(f"/api/organizations/{foreign.id}/", {"name": "intrusion"}, format="json").status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            foreign.refresh_from_db()
            self.assertEqual(foreign.name, initial_foreign_name)

    def test_organization_request_detail_is_superadmin_only_for_legacy_integer_ids(self):
        url = f"/api/superadmin/organisations/{self.org_b.id}/"
        self.client.force_authenticate(self.manager_a)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.super_admin)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_suspended_user_cannot_read_organization_request_detail(self):
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.is_active = False
        self.manager_a.save(update_fields=["status", "is_active"])
        self.client.force_authenticate(self.manager_a)
        response = self.client.get(f"/api/superadmin/organisations/{self.org_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @staticmethod
    def _jwt_client(user):
        client = APIClient()
        token = str(RefreshToken.for_user(user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_pre_suspension_jwt_cannot_read_organizations(self):
        self.manager_a.status = User.Status.ACTIVE
        self.manager_a.is_active = True
        self.manager_a.save(update_fields=["status", "is_active"])
        client = self._jwt_client(self.manager_a)
        self.assertEqual(client.get("/api/organizations/").status_code, status.HTTP_200_OK)
        self.assertEqual(client.get(f"/api/organizations/{self.org_a.pk}/").status_code, status.HTTP_200_OK)

        self.manager_a.status = User.Status.SUSPENDED
        # Keep is_active true to ensure the permission checks the live status,
        # rather than relying only on SimpleJWT's is_active check.
        self.manager_a.save(update_fields=["status"])
        self.assertEqual(client.get("/api/organizations/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(client.get(f"/api/organizations/{self.org_a.pk}/").status_code, status.HTTP_403_FORBIDDEN)

    def test_pre_suspension_jwts_for_all_organization_roles_are_refused(self):
        for role in (User.Role.CHEF_PROJET, User.Role.FINANCE, User.Role.AGENT):
            with self.subTest(role=role):
                user = User.objects.create_user(
                    email=f"{role.lower()}-organization@example.test", password="Password123!",
                    first_name="Role", last_name=role, role=role,
                    organization=self.org_a, status=User.Status.ACTIVE, is_active=True,
                )
                client = self._jwt_client(user)
                user.status = User.Status.SUSPENDED
                user.save(update_fields=["status"])
                self.assertEqual(client.get("/api/organizations/").status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_and_suspended_organization_states_do_not_change_tenant_scope(self):
        self.org_a.status = Organization.Status.EN_ATTENTE
        self.org_a.is_active = False
        self.org_a.save(update_fields=["status", "is_active"])
        self.org_b.status = Organization.Status.SUSPENDED
        self.org_b.is_active = False
        self.org_b.save(update_fields=["status", "is_active"])
        self.client.force_authenticate(self.manager_a)
        self.assertEqual(self.client.get(f"/api/organizations/{self.org_a.pk}/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(f"/api/organizations/{self.org_b.pk}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_non_admin_cannot_change_another_organizations_status(self):
        self.client.force_authenticate(self.manager_a)
        initial = (self.org_b.status, self.org_b.is_active)
        for method, url, payload in (
            (self.client.post, f"/api/organizations/admin/{self.org_b.pk}/approve/", {}),
            (self.client.post, f"/api/organizations/admin/{self.org_b.pk}/reject/", {}),
            (self.client.patch, f"/api/superadmin/organisations/{self.org_b.pk}/decision/", {"decision": "APPROUVEE"}),
        ):
            response = method(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.org_b.refresh_from_db()
            self.assertEqual((self.org_b.status, self.org_b.is_active), initial)

    def test_suspended_super_admin_jwt_cannot_list_or_decide_organizations(self):
        self.super_admin.status = User.Status.ACTIVE
        self.super_admin.is_active = True
        self.super_admin.save(update_fields=["status", "is_active"])
        client = self._jwt_client(self.super_admin)
        self.super_admin.status = User.Status.SUSPENDED
        self.super_admin.save(update_fields=["status"])

        self.assertEqual(client.get("/api/organizations/admin/demandes/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(client.get("/api/superadmin/organisations/").status_code, status.HTTP_403_FORBIDDEN)
        response = client.post(f"/api/organizations/admin/{self.org_b.pk}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = client.patch(
            f"/api/superadmin/organisations/{self.org_b.pk}/decision/",
            {"decision": "APPROUVEE"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.org_b.refresh_from_db()
        self.assertEqual(self.org_b.status, Organization.Status.EN_ATTENTE)
        self.assertFalse(self.org_b.is_active)

    def test_activation_token_cannot_reactivate_a_suspended_account(self):
        self.manager_a.status = User.Status.SUSPENDED
        self.manager_a.is_active = True
        self.manager_a.save(update_fields=["status", "is_active"])
        activation = ActivationToken.objects.create(
            user=self.manager_a, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        response = self.client.post("/api/organizations/activation/", {
            "token": str(activation.pk), "password": "NewPassword123!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post("/api/accounts/activate/", {
            "token": str(activation.pk), "password": "NewPassword123!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.manager_a.refresh_from_db()
        activation.refresh_from_db()
        self.assertEqual(self.manager_a.status, User.Status.SUSPENDED)
        self.assertFalse(activation.used)


class OrganizationDocumentIsolationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_dir = tempfile.TemporaryDirectory()
        cls.media_settings = override_settings(MEDIA_ROOT=cls.media_dir.name)
        cls.media_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_settings.disable()
        cls.media_dir.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.org_a = Organization.objects.create(
            name="ONG Doc A", email="doc-a@example.test", phone="771234570",
            address="Dakar", region="Dakar", intervention_domain="Humanitaire",
        )
        self.org_b = Organization.objects.create(
            name="ONG Doc B", email="doc-b@example.test", phone="771234571",
            address="Thiès", region="Thiès", intervention_domain="Santé",
        )
        self.user_a = User.objects.create_user(
            email="doc-user-a@example.test", password="Password123!",
            first_name="Awa", last_name="A", role=User.Role.GERANT,
            organization=self.org_a, is_active=True,
        )
        self.user_a.status = User.Status.ACTIVE
        self.user_a.save(update_fields=["status"])
        self.super_admin = User.objects.create_user(
            email="doc-admin@example.test", password="Password123!",
            first_name="Super", last_name="Admin", role=User.Role.SUPER_ADMIN,
            is_active=True, is_staff=True,
        )
        self.org_a.document_receipt.save("receipt.pdf", ContentFile(b"%PDF-1.4 ONG A"))
        self.org_b.document_receipt.save("receipt.pdf", ContentFile(b"%PDF-1.4 ONG B"))
        self.user_b = User.objects.create_user(
            email="doc-user-b@example.test", password="Password123!",
            first_name="Moussa", last_name="B", role=User.Role.GERANT,
            organization=self.org_b, is_active=True,
        )

    def test_document_requires_authentication_and_stays_in_organization_scope(self):
        url = f"/api/organizations/{self.org_a.pk}/documents/document_receipt/"
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user_a)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        foreign_url = f"/api/organizations/{self.org_b.pk}/documents/document_receipt/"
        self.assertEqual(self.client.get(foreign_url).status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user_b)
        reverse_url = f"/api/organizations/{self.org_a.pk}/documents/document_receipt/"
        self.assertEqual(self.client.get(reverse_url).status_code, status.HTTP_404_NOT_FOUND)
        own_url = f"/api/organizations/{self.org_b.pk}/documents/document_receipt/"
        self.assertEqual(self.client.get(own_url).status_code, status.HTTP_200_OK)

    def test_onboarding_documents_are_superadmin_only(self):
        request = OrganisationRequest.objects.create(
            nom_ong="ONG en demande", email="request@example.test", telephone="771234599",
            gerant_prenom="Awa", gerant_nom="Diop", gerant_email="gerante@example.test",
            recepisse_pdf=ContentFile(b"%PDF-1.4 receipt", name="receipt.pdf"),
            ninea_pdf=ContentFile(b"%PDF-1.4 ninea", name="ninea.pdf"),
            statuts_pdf=ContentFile(b"%PDF-1.4 statutes", name="statutes.pdf"),
        )
        url = f"/api/superadmin/organisations/{request.pk}/documents/recepisse_pdf/"

        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user_a)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.super_admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4 receipt")

        self.assertEqual(self.client.get("/api/superadmin/organisations/").status_code, status.HTTP_200_OK)
        for organization in (self.org_a, self.org_b):
            response = self.client.get(
                f"/api/organizations/{organization.pk}/documents/document_receipt/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suspended_account_cannot_download_organization_document(self):
        self.user_a.status = User.Status.SUSPENDED
        self.user_a.is_active = False
        self.user_a.save(update_fields=["status", "is_active"])
        self.client.force_authenticate(self.user_a)
        response = self.client.get(
            f"/api/organizations/{self.org_a.pk}/documents/document_receipt/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_serializer_uses_private_document_route(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.get(f"/api/organizations/{self.org_a.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            f"/api/organizations/{self.org_a.pk}/documents/document_receipt/",
            response.data["document_receipt"],
        )

    def test_known_sensitive_media_path_is_not_served_directly(self):
        media_url = f"/media/{self.org_a.document_receipt.name}"
        self.assertEqual(self.client.get(media_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_sensitive_media_roots_are_not_served_directly(self):
        for path in (
            "/media/organisation_requests/recepisse/private.pdf",
            "/media/organizations/documents/receipts/private.pdf",
            "/media/justifications/private.pdf",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, status.HTTP_404_NOT_FOUND)


class OrganizationRequestUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_dir = tempfile.TemporaryDirectory()
        cls.media_settings = override_settings(MEDIA_ROOT=cls.media_dir.name)
        cls.media_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_settings.disable()
        cls.media_dir.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()

    def payload(self, recepisse=None, ninea=None, statuts=None):
        pdf = lambda name: SimpleUploadedFile(name, b"%PDF-1.7 test", content_type="application/pdf")
        return {
            "nom_ong": "ONG Test Upload",
            "email": "ong-upload@example.test",
            "telephone": "771234590",
            "gerant_prenom": "Awa",
            "gerant_nom": "Diop",
            "gerant_email": "gerante-upload@example.test",
            "recepisse_pdf": recepisse or pdf("recepisse.pdf"),
            "ninea_pdf": ninea or pdf("ninea.pdf"),
            "statuts_pdf": statuts or pdf("statuts.pdf"),
        }

    @patch("apps.organizations.views.OrganisationRequestCreateView._send_to_ia", return_value={})
    def test_valid_onboarding_document_uploads(self, _send_to_ia):
        response = self.client.post(
            "/api/organizations/request/", self.payload(), format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        request = OrganisationRequest.objects.get(pk=response.data["id"])
        self.assertTrue(request.recepisse_pdf.name.endswith("recepisse.pdf"))
        self.assertTrue(request.ninea_pdf.name.endswith("ninea.pdf"))
        self.assertTrue(request.statuts_pdf.name.endswith("statuts.pdf"))

    @patch("apps.organizations.views.OrganisationRequestCreateView._send_to_ia", return_value={})
    def test_onboarding_payload_cannot_attach_foreign_organization_user_or_request(self, _send_to_ia):
        org = Organization.objects.create(
            name="Existing ONG", email="existing@example.test", phone="771234580",
            address="Dakar", region="Dakar", intervention_domain="Humanitaire",
        )
        existing_user = User.objects.create_user(
            email="existing-user@example.test", password="Password123!",
            first_name="Existing", last_name="User", role=User.Role.GERANT,
            organization=org, is_active=True, status=User.Status.ACTIVE,
        )
        payload = self.payload(
            recepisse=SimpleUploadedFile("spoof-recepisse.pdf", b"%PDF-1.7 test", content_type="application/pdf"),
            ninea=SimpleUploadedFile("spoof-ninea.pdf", b"%PDF-1.7 test", content_type="application/pdf"),
            statuts=SimpleUploadedFile("spoof-statuts.pdf", b"%PDF-1.7 test", content_type="application/pdf"),
        )
        payload.update({
            "organization_id": str(org.pk),
            "user_id": str(existing_user.pk),
            "request_id": "00000000-0000-0000-0000-000000000001",
        })
        response = self.client.post("/api/organizations/request/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        request = OrganisationRequest.objects.get(pk=response.data["id"])
        self.assertIsNone(request.organization_id)

    def test_onboarding_upload_rejects_oversized_pdf(self):
        payload = self.payload(recepisse=SimpleUploadedFile(
            "recepisse.pdf", b"%PDF-" + b"x" * (5 * 1024 * 1024), content_type="application/pdf"
        ))
        response = self.client.post("/api/organizations/request/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recepisse_pdf", response.data)
        self.assertEqual(OrganisationRequest.objects.count(), 0)

    def test_onboarding_upload_rejects_wrong_extension_and_signature(self):
        cases = (
            SimpleUploadedFile("recepisse.txt", b"%PDF-1.7 test", content_type="text/plain"),
            SimpleUploadedFile("recepisse.pdf", b"not a PDF", content_type="application/pdf"),
        )
        for invalid_file in cases:
            with self.subTest(filename=invalid_file.name):
                response = self.client.post(
                    "/api/organizations/request/",
                    self.payload(recepisse=invalid_file),
                    format="multipart",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("recepisse_pdf", response.data)
        self.assertEqual(OrganisationRequest.objects.count(), 0)

class OrganizationDashboardTests(OrganizationReadIsolationTests):
    def test_super_admin_can_list_all_organizations(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_super_admin_dashboard_is_role_protected_and_uses_real_counts(self):
        response = self.client.get("/api/superadmin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.manager_a)
        response = self.client.get("/api/superadmin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.super_admin)
        self.org_a.status = Organization.Status.ACTIVE
        self.org_a.is_active = True
        self.org_a.save(update_fields=["status", "is_active"])
        self.manager_a.status = User.Status.ACTIVE
        self.manager_a.is_active = True
        self.manager_a.save(update_fields=["status", "is_active"])
        response = self.client.get("/api/superadmin/dashboard/?period=7d")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ongs"]["total"], 2)
        self.assertEqual(response.data["ongs"]["actives"], 1)
        self.assertEqual(response.data["ongs"]["par_statut"][Organization.Status.ACTIVE], 1)
        self.assertEqual(response.data["ongs"]["par_region"], [
            {"region": "Dakar", "total": 1},
            {"region": "Thiès", "total": 1},
        ])
        self.assertEqual(response.data["gerants"]["total"], 1)
        self.assertEqual(response.data["gerants"]["actifs"], 1)
        self.assertEqual(response.data["projets"]["total"], 0)
        self.assertEqual(response.data["evolution"]["projets"][-1]["date"], timezone.localdate().isoformat())
