import importlib.util
import hashlib
import hmac
import json
import os
import sys
import types
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Load the real service without downloading Chroma or the embedding model.
class FakeCollection:
    def __init__(self):
        self.records = {}
        self.last_where = None
        self.last_matched_metadata = []

    def upsert(self, documents, metadatas, ids):
        for document, metadata, document_id in zip(documents, metadatas, ids):
            self.records[document_id] = (document, metadata)

    def query(self, query_texts, n_results, where):
        self.last_where = where
        matched = [(doc, metadata) for doc, metadata in self.records.values()
                   if all(metadata.get(key) == value for key, value in where.items())]
        self.last_matched_metadata = [metadata for _, metadata in matched]
        matches = [doc for doc, _ in matched]
        return {"documents": [matches[:n_results]]}


fake_collection = FakeCollection()
chromadb = types.ModuleType("chromadb")
chromadb.PersistentClient = lambda **kwargs: types.SimpleNamespace(
    get_or_create_collection=lambda **options: fake_collection
)
chromadb.__path__ = []
chromadb_utils = types.ModuleType("chromadb.utils")
chromadb_utils.__path__ = []
embedding_functions = types.ModuleType("chromadb.utils.embedding_functions")
embedding_functions.DefaultEmbeddingFunction = lambda: object()
sentence_transformers = types.ModuleType("sentence_transformers")
sentence_transformers.SentenceTransformer = lambda name: types.SimpleNamespace(
    encode=lambda values: types.SimpleNamespace(tolist=lambda: [[0.1] for _ in values])
)
with patch.dict(sys.modules, {
    "chromadb": chromadb,
    "chromadb.utils": chromadb_utils,
    "chromadb.utils.embedding_functions": embedding_functions,
    "sentence_transformers": sentence_transformers,
}):
    module_path = Path(__file__).parents[1] / "app" / "services" / "rag_service.py"
    spec = importlib.util.spec_from_file_location("rag_service_isolation_test", module_path)
    rag_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rag_module)

# The auth tests install light-weight service stubs while importing the app.
gemini_module = types.ModuleType("app.services.gemini_service")
gemini_module.gemini_service = MagicMock()
route_rag_module = types.ModuleType("app.services.rag_service")
route_rag_module.get_rag_service = MagicMock()
with patch.dict(sys.modules, {
    "app.services.gemini_service": gemini_module,
    "app.services.rag_service": route_rag_module,
}):
    from app.main import app
    from app.routers import chat as chat_router


class RagTenantIsolationTests(unittest.TestCase):
    signing_key = "rag-test-signing-key"

    def setUp(self):
        self.token_patch = patch.dict(os.environ, {
            "AI_SERVICE_TOKEN": "rag-test-secret",
            "AI_CONTEXT_SIGNING_KEY": self.signing_key,
        })
        self.token_patch.start()
        fake_collection.records.clear()
        self.service = rag_module.RagService()
        self.client = TestClient(app)
        self.headers = {"X-Internal-Service-Token": "rag-test-secret"}
        self.tenant_a = {"organization_id": 17, "user_id": 23, "role": "GERANT"}

    def tearDown(self):
        self.client.close()
        self.token_patch.stop()

    def _index(self, tenant, org_id, doc_id="campaign_123", document="private doc"):
        return self._post("/api/ia/index", {
            "tenant": tenant,
            "documents": [document],
            "metadatas": [{"organization_id": org_id, "document_id": doc_id, "source": "campaign"}],
            "ids": [doc_id],
        })

    def _post(self, url, payload):
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
        timestamp = str(int(time.time()))
        signature = hmac.new(self.signing_key.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        headers = {**self.headers, "Content-Type": "application/json", "X-Context-Timestamp": timestamp, "X-Context-Signature": signature}
        return self.client.post(url, headers=headers, content=body)

    def test_two_organizations_with_same_document_id_do_not_collide(self):
        self.service.index_data(["ONG A"], [{"organization_id": 17, "document_id": "campaign_1", "source": "campaign"}], ["campaign_1"], 17)
        self.service.index_data(["ONG B"], [{"organization_id": 18, "document_id": "campaign_1", "source": "campaign"}], ["campaign_1"], 18)
        self.assertEqual(set(fake_collection.records), {"org_17_campaign_1", "org_18_campaign_1"})
        self.assertEqual(self.service.query_context("question", 17), "ONG A")
        self.assertEqual(fake_collection.last_where, {"organization_id": 17})
        self.assertEqual(self.service.query_context("question", 18), "ONG B")

    def test_identical_content_and_query_remain_tenant_scoped(self):
        shared_text = "Même contenu confidentiel"
        for organization_id in (17, 18):
            self.service.index_data(
                [shared_text],
                [{"organization_id": organization_id, "document_id": "shared", "source": "campaign"}],
                ["shared"], organization_id,
            )

        self.assertEqual(self.service.query_context("question identique", 17), shared_text)
        self.assertEqual([m["organization_id"] for m in fake_collection.last_matched_metadata], [17])
        self.assertEqual(self.service.query_context("question identique", 18), shared_text)
        self.assertEqual([m["organization_id"] for m in fake_collection.last_matched_metadata], [18])
        self.assertEqual(fake_collection.last_where, {"organization_id": 18})

    def test_index_rejects_missing_org_mismatch_and_missing_metadata(self):
        cases = [
            (self.tenant_a, None, "campaign_1", "doc"),
            (self.tenant_a, 18, "campaign_1", "doc"),
            (self.tenant_a, 17, "", "doc"),
        ]
        for tenant, org_id, doc_id, document in cases:
            with self.subTest(org_id=org_id, doc_id=doc_id):
                self.assertEqual(self._index(tenant, org_id, doc_id, document).status_code, 422)

    def test_index_rejects_missing_tenant_and_forged_top_level_org(self):
        base = {"documents": ["doc"], "metadatas": [{"organization_id": 17, "document_id": "1", "source": "campaign"}], "ids": ["1"]}
        self.assertEqual(self._post("/api/ia/index", base).status_code, 422)
        self.assertEqual(self._post("/api/ia/index", {**base, "tenant": self.tenant_a, "organization_id": 18}).status_code, 422)

    def test_index_endpoint_passes_only_verified_tenant_scope_to_service(self):
        with patch.object(chat_router, "get_rag_service") as get_service:
            get_service.return_value.index_data.return_value = {"status": "success", "indexed_count": 1}
            response = self._index(self.tenant_a, 17)
            self.assertEqual(response.status_code, 200)
            get_service.return_value.index_data.assert_called_once()
            self.assertEqual(get_service.return_value.index_data.call_args.kwargs["organization_id"], 17)

    def test_super_admin_without_org_cannot_search_or_index_globally(self):
        with self.assertRaises(ValueError):
            self.service.query_context("question", None)
        tenant = {"organization_id": None, "user_id": 1, "role": "SUPER_ADMIN"}
        self.assertEqual(self._index(tenant, None).status_code, 422)

    def test_document_id_has_no_cross_tenant_retrieval_endpoint(self):
        response = self.client.get(
            "/api/ia/documents/org_17_campaign_123",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_chat_search_uses_authenticated_organization_and_super_admin_skips_global_search(self):
        rag = MagicMock()
        rag.query_context.return_value = "tenant private context"
        gemini_module.gemini_service._call_gemini.return_value = "answer"
        with patch.object(chat_router, "get_rag_service", return_value=rag):
            response = self._post("/api/ia/chat", {
                "tenant": self.tenant_a, "question": "question", "context": {},
            })
            self.assertEqual(response.status_code, 200)
            rag.query_context.assert_called_once_with(question="question", organization_id=17)
            rag.query_context.reset_mock()
            admin_response = self._post("/api/ia/chat", {
                "tenant": {"organization_id": None, "user_id": 1, "role": "SUPER_ADMIN"},
                "question": "question", "context": {},
            })
            self.assertEqual(admin_response.status_code, 200)
            rag.query_context.assert_not_called()


if __name__ == "__main__":
    unittest.main()
