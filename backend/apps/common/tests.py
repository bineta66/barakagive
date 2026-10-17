from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from .validators import (
    validate_email,
    validate_montant,
    validate_nom,
    validate_phone_senegal,
    validate_pourcentage,
)
from .uploads import validate_image_upload, validate_pdf_upload


class InputValidationBypassTests(SimpleTestCase):
    def test_person_names_accept_realistic_unicode_names_and_normalize_spaces(self):
        self.assertEqual(validate_nom("  Diop-Ndiaye  "), "Diop-Ndiaye")
        self.assertEqual(validate_nom("O’Connor"), "O’Connor")
        self.assertEqual(validate_nom("Sarr   Fall"), "Sarr Fall")

    def test_names_reject_numeric_input(self):
        for value in (12345, "12345", "Aminata2", "<script>"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_nom(value)

    def test_long_names_reject_non_text_values(self):
        from .validators import validate_nom_long

        with self.assertRaises(ValidationError):
            validate_nom_long(12345)

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_email("invalid-email")

    def test_invalid_phone_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_phone_senegal("abc")

    def test_amount_rejects_negative_and_non_finite_values(self):
        for value in ("-1", "NaN", "Infinity", "abc", None):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_montant(value)

    def test_percentage_rejects_out_of_range_and_fractional_values(self):
        for value in ("101", "-1", "12.5"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_pourcentage(value)

    def test_pdf_upload_checks_extension_and_content_signature(self):
        valid = SimpleUploadedFile("document.pdf", b"%PDF-1.7 content")
        invalid = SimpleUploadedFile("document.pdf", b"not a PDF")
        wrong_extension = SimpleUploadedFile("document.txt", b"%PDF-1.7 content")

        self.assertIs(validate_pdf_upload(valid), valid)
        for upload in (invalid, wrong_extension):
            with self.subTest(name=upload.name), self.assertRaises(ValidationError):
                validate_pdf_upload(upload)

    def test_image_upload_checks_extension_and_content_signature(self):
        valid = SimpleUploadedFile("logo.png", b"\x89PNG\r\n\x1a\nimage")
        invalid = SimpleUploadedFile("logo.png", b"not an image")

        self.assertIs(validate_image_upload(valid), valid)
        with self.assertRaises(ValidationError):
            validate_image_upload(invalid)


class DefaultAPIPermissionTests(SimpleTestCase):
    def test_api_view_requires_authentication_by_default(self):
        class PrivateProbeView(APIView):
            def get(self, request):
                return Response({"ok": True})

        response = PrivateProbeView.as_view()(APIRequestFactory().get("/private-probe/"))

        self.assertEqual(response.status_code, 401)

    def test_explicit_public_permission_remains_public(self):
        class PublicProbeView(APIView):
            permission_classes = [AllowAny]

            def get(self, request):
                return Response({"ok": True})

        response = PublicProbeView.as_view()(APIRequestFactory().get("/public-probe/"))

        self.assertEqual(response.status_code, 200)
