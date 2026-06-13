import os
import re
import numpy as np
import chromadb
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
import google.generativeai as genai

# Try to configure GenAI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class HybridEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function that uses Gemini embeddings if API key is present,
    otherwise falls back to a zero-dependency TF-IDF style vector generator.
    """
    def __init__(self):
        self.vocabulary = {}
        self.next_vocab_id = 0

    def _get_gemini_embeddings(self, texts: Documents) -> Embeddings:
        embeddings = []
        for text in texts:
            try:
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(response['embedding'])
            except Exception as e:
                # If Gemini fails, fallback to local
                embeddings.append(self._get_local_embedding(text))
        return embeddings

    def _get_local_embedding(self, text: str) -> list:
        # Simple TF-IDF/Bag of words embedding generator normalized to 768 dimensions
        words = re.findall(r'\w+', text.lower())
        vector = np.zeros(768)
        
        # Hash each word into a index of 768 dimensions
        for word in words:
            # Simple deterministic hash
            idx = sum(ord(c) * (i + 1) for i, c in enumerate(word)) % 768
            vector[idx] += 1.0
            
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()

    def __call__(self, input: Documents) -> Embeddings:
        if GEMINI_API_KEY:
            try:
                return self._get_gemini_embeddings(input)
            except Exception:
                pass
        return [self._get_local_embedding(text) for text in input]

class VectorService:
    def __init__(self):
        # Local persistent vector store
        db_path = os.path.join(os.getcwd(), "vector_db")
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = HybridEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="aegisops_knowledge",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Adds documents/runbooks to vector DB"""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_similar(self, query: str, limit: int = 3) -> list[dict]:
        """Searches vector DB for similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            output = []
            if results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
                distances = results["distances"][0] if results["distances"] else [0.0] * len(docs)
                ids = results["ids"][0]
                
                for d, m, dist, doc_id in zip(docs, metas, distances, ids):
                    # Higher distance means less similar, convert to similarity score
                    similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                    output.append({
                        "id": doc_id,
                        "content": d,
                        "metadata": m,
                        "similarity": similarity
                    })
            return output
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []

vector_service = VectorService()
