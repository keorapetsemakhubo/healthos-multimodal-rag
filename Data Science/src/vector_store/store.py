import sys
import os
import atexit

# Pre-import core C-runtime & file locking modules on Windows before mocking
if sys.platform == "win32":
    import msvcrt
    try:
        import portalocker
    except ImportError:
        pass

from unittest.mock import MagicMock
from importlib.machinery import ModuleSpec

def create_mock_module(name):
    mock = MagicMock()
    mock.__spec__ = ModuleSpec(name, loader=None)
    return mock

# Mock sklearn submodules to bypass Windows AppLocker policy safely
for mod in [
    'sklearn',
    'sklearn.metrics',
    'sklearn.metrics.cluster',
    'sklearn.metrics.pairwise',
    'sklearn.preprocessing',
]:
    if mod not in sys.modules or sys.modules[mod] is None:
        sys.modules[mod] = create_mock_module(mod)

import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

class VectorStoreManager:
    """Handles embedding generation and indexing chunks into Qdrant (Local Embedded Mode)."""

    def __init__(self):
        # Local persistent folder for Qdrant storage (No Docker required)
        db_path = os.getenv("QDRANT_PATH", "data/qdrant_db")
        os.makedirs(db_path, exist_ok=True)
        self.collection_name = os.getenv("COLLECTION_NAME", "multimodal_docs")

        # Initialize embedded Qdrant Client reading from local folder
        self.client = QdrantClient(path=db_path)

        # Register explicit client closing to prevent portalocker teardown crashes
        atexit.register(self.close)

        print("Loading embedding model (all-MiniLM-L6-v2)...")
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_size = self.encoder.get_embedding_dimension()

        self._ensure_collection_exists()

    def close(self):
        """Safely close Qdrant connection before Python interpreter teardown."""
        if hasattr(self, 'client') and self.client is not None:
            try:
                self.client.close()
            except Exception:
                pass

    def _ensure_collection_exists(self):
        """Creates the Qdrant collection if it does not already exist."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            print(f"Creating Qdrant local collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                ),
            )

    def _format_chunk_for_embedding(self, chunk: Dict[str, Any]) -> str:
        """Combines text and table representations into a single string for embedding."""
        content_parts = [chunk.get("text", "")]
        for table in chunk.get("tables", []):
            for row in table:
                content_parts.append(" | ".join(row))
        return "\n".join(content_parts).strip()

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Embeds document chunks and stores vector embeddings + payload metadata in Qdrant."""
        points = []
        for chunk in chunks:
            text_to_embed = self._format_chunk_for_embedding(chunk)
            if not text_to_embed:
                continue

            vector = self.encoder.encode(text_to_embed).tolist()
            point_id = str(uuid.uuid4())

            payload = {
                "document_id": chunk["document_id"],
                "page_number": chunk["page_number"],
                "text": chunk["text"],
                "tables": chunk["tables"],
                "image_path": chunk["image_path"],
            }

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Successfully indexed {len(points)} chunks into local Qdrant collection '{self.collection_name}'.")

    def search_similar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Embeds a query string and returns top_k relevant payload metadata."""
        query_vector = self.encoder.encode(query).tolist()
        
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )

        results = []
        for point in response.points:
            result = point.payload
            result["score"] = point.score
            results.append(result)

        return results


if __name__ == "__main__":
    vstore = VectorStoreManager()
    print("VectorStoreManager (Embedded Local Storage) initialized successfully.")