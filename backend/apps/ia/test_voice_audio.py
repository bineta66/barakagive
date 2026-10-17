from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.response import Response

from apps.ia.views import AssistantAudioTranscriptionView


class AssistantAudioTranscriptionTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AssistantAudioTranscriptionView.as_view()
        self.gerant = SimpleNamespace(role="GERANT", organization_id=17, is_authenticated=True)

    def post(self, user=None, audio=None, duration="5"):
        data = {"duration_seconds": duration}
        if audio is not None:
            data["audio"] = audio
        request = self.factory.post(
            "/api/assistant/audio/",
            data,
            format="multipart",
        )
        force_authenticate(request, user=user or self.gerant)
        return self.view(request)

    def test_only_gerant_with_organization_can_transcribe(self):
        for user in (
            SimpleNamespace(role="CHEF_PROJET", organization_id=17, is_authenticated=True),
            SimpleNamespace(role="GERANT", organization_id=None, is_authenticated=True),
        ):
            response = self.post(user=user, audio=SimpleUploadedFile("voice.webm", b"audio", "audio/webm"))
            self.assertEqual(response.status_code, 403)

    def test_missing_or_unsupported_audio_is_rejected(self):
        self.assertEqual(self.post(audio=None).status_code, 400)
        unsupported = SimpleUploadedFile("voice.txt", b"audio", "text/plain")
        self.assertEqual(self.post(audio=unsupported).status_code, 415)

    @override_settings(IA_SERVICE_URL="http://ia_service:8001", AI_SERVICE_TOKEN="internal-test-token", AI_CONTEXT_SIGNING_KEY="test-context-key")
    @patch("apps.ia.views.requests.post")
    def test_audio_is_proxied_to_private_service_and_transcription_returned(self, post):
        upstream = Mock(ok=True)
        upstream.json.return_value = {"transcription": "Quels projets sont en retard ?"}
        post.return_value = upstream
        audio = SimpleUploadedFile("voice.webm", b"fake-audio-bytes", "audio/webm")

        response = self.post(audio=audio, duration="8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"transcription": "Quels projets sont en retard ?"})
        args, kwargs = post.call_args
        self.assertEqual(args[0], "http://ia_service:8001/api/ia/audio/transcribe")
        self.assertEqual(kwargs["data"], b"fake-audio-bytes")
        self.assertEqual(kwargs["headers"]["X-Audio-Duration-Seconds"], "8")
        self.assertEqual(kwargs["headers"]["X-Internal-Service-Token"], "internal-test-token")

    def test_duration_over_limit_is_rejected(self):
        audio = SimpleUploadedFile("voice.webm", b"audio", "audio/webm")
        self.assertEqual(self.post(audio=audio, duration="121").status_code, 400)

