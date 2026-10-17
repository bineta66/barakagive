import logging
import os
import unittest
from unittest.mock import patch

from app.services.ai_router import AIRouter
from app.services.providers.base import AIErrorType, AIProviderError, error_from_status
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.groq_provider import GroqProvider


class FakeProvider:
    def __init__(self, name, outcomes, enabled=True):
        self.name = name
        self.model_name = f"{name}-model"
        self.outcomes = list(outcomes)
        self.enabled = enabled
        self.calls = 0

    def is_enabled(self):
        return self.enabled

    def generate(self, prompt, *, timeout):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class AIRouterTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "AI_PROVIDER_ORDER": "gemini,groq,openrouter",
            "AI_REQUEST_TIMEOUT": "4",
            "AI_MAX_RETRIES": "0",
            "AI_PROVIDER_COOLDOWN_SECONDS": "60",
            "AI_CIRCUIT_FAILURE_THRESHOLD": "3",
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_primary_success_does_not_call_fallbacks(self):
        gemini, groq, router_provider = (FakeProvider("gemini", ["ok"]), FakeProvider("groq", ["unused"]), FakeProvider("openrouter", ["unused"]))
        result = AIRouter([gemini, groq, router_provider]).generate_response("prompt")
        self.assertEqual((result.content, result.provider), ("ok", "gemini"))
        self.assertEqual((gemini.calls, groq.calls, router_provider.calls), (1, 0, 0))

    def test_every_provider_output_is_secret_filtered_without_changing_finance_values(self):
        provider = FakeProvider("gemini", ["api_key=synthetic-key-value; budget=15 000 000 FCFA"])
        answer = AIRouter([provider]).generate("demo finance prompt")
        self.assertNotIn("synthetic-key-value", answer)
        self.assertIn("15 000 000 FCFA", answer)

    def test_rate_limit_falls_back_to_groq(self):
        gemini = FakeProvider("gemini", [AIProviderError(AIErrorType.RATE_LIMIT, status=429)])
        groq = FakeProvider("groq", ["ok"])
        self.assertEqual(AIRouter([gemini, groq]).generate("prompt"), "ok")
        self.assertEqual((gemini.calls, groq.calls), (1, 1))

    def test_groq_server_error_continues_to_openrouter(self):
        providers = [
            FakeProvider("gemini", [AIProviderError(AIErrorType.RATE_LIMIT, status=429)]),
            FakeProvider("groq", [AIProviderError(AIErrorType.SERVER_ERROR, status=503)]),
            FakeProvider("openrouter", ["ok"]),
        ]
        result = AIRouter(providers).generate_response("prompt")
        self.assertEqual((result.provider, result.content), ("openrouter", "ok"))

    def test_bad_request_does_not_fallback(self):
        gemini, groq = FakeProvider("gemini", [AIProviderError(AIErrorType.BAD_REQUEST, status=400)]), FakeProvider("groq", ["unused"])
        with self.assertRaises(RuntimeError):
            AIRouter([gemini, groq]).generate("prompt")
        self.assertEqual((gemini.calls, groq.calls), (1, 0))

    def test_timeout_falls_back(self):
        providers = [FakeProvider("gemini", [AIProviderError(AIErrorType.TIMEOUT)]), FakeProvider("groq", ["ok"])]
        self.assertEqual(AIRouter(providers).generate("prompt"), "ok")

    def test_configured_order_is_respected(self):
        gemini, groq = FakeProvider("gemini", ["gemini"]), FakeProvider("groq", ["groq"])
        with patch.dict(os.environ, {"AI_PROVIDER_ORDER": "groq,gemini"}):
            result = AIRouter([gemini, groq]).generate_response("prompt")
        self.assertEqual(result.provider, "groq")
        self.assertEqual((groq.calls, gemini.calls), (1, 0))

    def test_retry_is_bounded_to_configured_retries(self):
        gemini = FakeProvider("gemini", [AIProviderError(AIErrorType.TIMEOUT), "ok"])
        groq = FakeProvider("groq", ["unused"])
        with patch.dict(os.environ, {"AI_MAX_RETRIES": "1"}):
            self.assertEqual(AIRouter([gemini, groq]).generate("prompt"), "ok")
        self.assertEqual((gemini.calls, groq.calls), (2, 0))

    def test_http_500_does_not_trigger_fallback(self):
        self.assertFalse(error_from_status(500).retryable)
        gemini = FakeProvider("gemini", [error_from_status(500)])
        groq = FakeProvider("groq", ["unused"])
        with self.assertRaises(RuntimeError):
            AIRouter([gemini, groq]).generate("prompt")
        self.assertEqual((gemini.calls, groq.calls), (1, 0))

    def test_only_transient_http_codes_are_retryable(self):
        for status in (408, 429, 502, 503, 504):
            with self.subTest(status=status):
                self.assertTrue(error_from_status(status).retryable)
        for status in (400, 401, 403, 500):
            with self.subTest(status=status):
                self.assertFalse(error_from_status(status).retryable)

    def test_disabled_provider_is_skipped(self):
        gemini, groq = FakeProvider("gemini", ["unused"], enabled=False), FakeProvider("groq", ["ok"])
        with patch.dict(os.environ, {"AI_PROVIDER_ORDER": "gemini,groq"}):
            self.assertEqual(AIRouter([gemini, groq]).generate("prompt"), "ok")
        self.assertEqual((gemini.calls, groq.calls), (0, 1))

    def test_gemini_disabled_environment_flag_is_honored(self):
        gemini = GeminiProvider(model=object())
        with patch.dict(os.environ, {"GEMINI_ENABLED": "false", "AI_PROVIDER_ORDER": "gemini,groq"}):
            groq = FakeProvider("groq", ["ok"])
            self.assertEqual(AIRouter([gemini, groq]).generate("prompt"), "ok")

    def test_groq_disabled_environment_flag_is_honored(self):
        with patch.dict(os.environ, {
            "GROQ_ENABLED": "false",
            "GROQ_API_KEY": "test-secret",
            "GROQ_MODEL": "test-model",
            "AI_PROVIDER_ORDER": "groq,openrouter",
        }):
            groq = GroqProvider()
            backup = FakeProvider("openrouter", ["ok"])
            self.assertEqual(AIRouter([groq, backup]).generate("prompt"), "ok")
            self.assertEqual(groq.is_enabled(), False)

    def test_groq_is_enabled_by_default_when_credentials_are_present(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret", "GROQ_MODEL": "test-model"}, clear=False):
            os.environ.pop("GROQ_ENABLED", None)
            self.assertTrue(GroqProvider().is_enabled())

    def test_all_providers_failing_returns_controlled_error(self):
        providers = [FakeProvider("gemini", [AIProviderError(AIErrorType.RATE_LIMIT)]), FakeProvider("groq", [AIProviderError(AIErrorType.SERVER_ERROR)])]
        with self.assertRaisesRegex(RuntimeError, "indisponibles"):
            AIRouter(providers).generate("prompt")

    def test_secrets_are_not_logged_and_request_id_is_shared(self):
        providers = [FakeProvider("gemini", [AIProviderError(AIErrorType.RATE_LIMIT)]), FakeProvider("groq", ["ok"])]
        with self.assertLogs("app.services.ai_router", level=logging.INFO) as captured:
            result = AIRouter(providers).generate_response("private prompt", operation="demo", request_id="request-123")
        logs = "\n".join(captured.output)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(logs.count("request-123"), 2)
        for secret in ("private prompt", "GROQ_API_KEY", "AI_SERVICE_TOKEN", "password", "JWT"):
            self.assertNotIn(secret, logs)


if __name__ == "__main__":
    unittest.main()
