import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
from PIL import Image

try:
    import google.generativeai as genai
    USE_LEGACY_SDK = True
except ImportError:
    from google import genai
    USE_LEGACY_SDK = False

from src.vector_store.store import VectorStoreManager

load_dotenv()

class MultimodalRAGEngine:
    """Combines vector search with Gemini 3.8 Flash for multimodal RAG QA."""

    def __init__(self, vector_store: VectorStoreManager = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        if USE_LEGACY_SDK:
            genai.configure(api_key=api_key)
            # Updated to gemini-3.8-flash
            self.model = genai.GenerativeModel("gemini-3.8-flash")
        else:
            self.client = genai.Client(api_key=api_key)
        
        # Use provided vector store instance to prevent Qdrant local file lock contention
        self.vstore = vector_store if vector_store is not None else VectorStoreManager()

    def answer_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        retrieved_docs = self.vstore.search_similar(query, top_k=top_k)
        
        if not retrieved_docs:
            return {
                "answer": "No relevant documents found in vector store.",
                "sources": []
            }

        # Build context prompt
        context_text = ""
        images = []

        for doc in retrieved_docs:
            page_num = doc.get("page_number", "Unknown")
            doc_id = doc.get("document_id", "Unknown")
            text = doc.get("text", "")
            tables = doc.get("tables", [])
            img_path = doc.get("image_path")

            context_text += f"\n--- Source Document: {doc_id} (Page {page_num}) ---\n"
            context_text += f"Text:\n{text}\n"

            if tables:
                context_text += "Tables:\n"
                for table in tables:
                    for row in table:
                        context_text += " | ".join(row) + "\n"

            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    images.append(img)
                except Exception as e:
                    print(f"Warning: Failed to load image at {img_path}: {e}")

        prompt = f"""You are HealthOS, an AI assistant analyzing health facility specifications and documents.
Answer the user query based strictly on the retrieved document context and attached page images below.

User Query: {query}

Retrieved Document Context:
{context_text}

Provide a concise, accurate, and professional response. Cite page numbers where applicable.
"""

        contents = [prompt] + images

        if USE_LEGACY_SDK:
            response = self.model.generate_content(contents)
            answer_text = response.text
        else:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents
            )
            answer_text = response.text

        return {
            "answer": answer_text,
            "sources": retrieved_docs
        }