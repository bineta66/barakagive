import asyncio
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

audio_path = Path(__file__).parents[1] / "app" / "routers" / "audio.py"
audio_spec = importlib.util.spec_from_file_location("audio_transcription_under_test", audio_path)
audio_module = importlib.util.module_from_spec(audio_spec)
audio_spec.loader.exec_module(audio_module)
transcribe_audio = audio_module.transcribe_audio


class FakeRequest:
    def __init__(self, content=b"voice bytes", media_type="audio/webm", duration="8", filename="message.webm"):
        self.headers = {
            "Content-Type": media_type,
            "X-Audio-Duration-Seconds": duration,
            "X-Audio-Filename": filename,
        }
        self.content = content

    async def body(self):
        return self.content

    async def stream(self):
        yield self.content


class FakeResponse:
    is_error = False
    status_code = 200

    def json(self):
        return {"text": "Quels projets sont en retard ?"}


class FakeAsyncClient:
    def __init__(self, response=None, **kwargs):
        self.response = response or FakeResponse()
        self.kwargs = kwargs
        self.call = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, *args, **kwargs):
        self.call = (args, kwargs)
        return self.response


class AudioTranscriptionTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GROQ_BASE_URL": "https://speech.invalid/openai/v1",
            "GROQ_STT_MODEL": "whisper-test-model",
            "AI_AUDIO_MAX_BYTES": "64",
            "AI_AUDIO_MAX_DURATION_SECONDS": "120",
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_transcribes_supported_audio_with_whisper_without_logging_or_storing_it(self):
        client = FakeAsyncClient()
        with patch.object(audio_module.httpx, "AsyncClient", return_value=client):
            result = asyncio.run(transcribe_audio(FakeRequest()))
        self.assertEqual(result["transcription"], "Quels projets sont en retard ?")
        args, kwargs = client.call
        self.assertEqual(args[0], "https://speech.invalid/openai/v1/audio/transcriptions")
        self.assertEqual(kwargs["data"]["model"], "whisper-test-model")
        self.assertEqual(kwargs["files"]["file"][2], "audio/webm")

    def test_rejects_unsupported_type_oversized_or_too_long_audio(self):
        with self.assertRaises(HTTPException) as unsupported:
            asyncio.run(transcribe_audio(FakeRequest(media_type="application/octet-stream")))
        self.assertEqual(unsupported.exception.status_code, 415)
        with self.assertRaises(HTTPException) as oversized:
            asyncio.run(transcribe_audio(FakeRequest(content=b"x" * 65)))
        self.assertEqual(oversized.exception.status_code, 413)
        with self.assertRaises(HTTPException) as too_long:
            asyncio.run(transcribe_audio(FakeRequest(duration="121")))
        self.assertEqual(too_long.exception.status_code, 400)

    def test_missing_provider_key_returns_controlled_unavailable(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaises(HTTPException) as unavailable:
                asyncio.run(transcribe_audio(FakeRequest()))
        self.assertEqual(unavailable.exception.status_code, 503)

    def test_unintelligible_audio_does_not_get_a_fabricated_transcription(self):
        response = FakeResponse()
        response.json = lambda: {"text": "  "}
        with patch.object(audio_module.httpx, "AsyncClient", return_value=FakeAsyncClient(response)):
            with self.assertRaises(HTTPException) as empty:
                asyncio.run(transcribe_audio(FakeRequest()))
        self.assertEqual(empty.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
