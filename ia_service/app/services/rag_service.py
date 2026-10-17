import logging
import os
from typing import Any, Dict, List

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="barakagive_knowledge",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_function,
        )
        logger.info("Using Chroma's ONNX all-MiniLM-L6-v2 embedding function.")

    def index_data(
        self, documents: List[str], metadatas: List[Dict[str, Any]],
        ids: List[str], organization_id: int,
    ):
        if not isinstance(organization_id, int) or organization_id <= 0:
            raise ValueError("A valid organization is required for indexing.")
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("Documents, metadata and IDs must have the same length.")
        if not documents:
            return {"status": "success", "message": "Aucun document à indexer."}

        safe_metadatas, safe_ids = [], []
        for metadata, document_id in zip(metadatas, ids):
            if not isinstance(metadata, dict) or metadata.get("organization_id") != organization_id:
                raise ValueError("Missing or mismatched organization_id metadata.")
            if not metadata.get("document_id") or not metadata.get("source"):
                raise ValueError("document_id and source metadata are required.")
            safe_metadata = dict(metadata)
            safe_metadata["organization_id"] = organization_id
            safe_metadatas.append(safe_metadata)
            safe_ids.append(f"org_{organization_id}_{document_id}")

        self.collection.upsert(
            documents=documents, metadatas=safe_metadatas, ids=safe_ids,
        )
        return {"status": "success", "indexed_count": len(documents)}

    def query_context(self, question: str, organization_id: int, n_results: int = 5) -> str:
        if not isinstance(organization_id, int) or organization_id <= 0:
            raise ValueError("A valid organization is required for search.")
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
            where={"organization_id": organization_id},
        )
        if not results["documents"] or not results["documents"][0]:
            return "Aucun contexte pertinent trouvé."
        return "\n---\n".join(results["documents"][0])


rag_service = None


def get_rag_service():
    global rag_service
    if rag_service is None:
        rag_service = RagService()
    return rag_service
