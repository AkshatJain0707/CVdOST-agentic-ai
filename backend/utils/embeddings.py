"""
Embedding Engine
----------------
Unified vectorization layer supporting OpenAI + local transformer fallback.
Optimized for semantic alignment in ATS scoring and similarity search.
"""

import os
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("EmbeddingEngine")
logger.setLevel(logging.INFO)

class EmbeddingEngine:
    """Unified embedding engine with OpenAI + local model fallback."""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        self.local_model = None
        self.model_name = model_name
        self._embedding_cache = {}
        self._init_models()

    def _init_models(self):
        """Initialize OpenAI and local embedding models."""
        if self.api_key:
            try:
                self.openai_client = OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI embeddings initialized.")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI init failed: {e}")
        try:
            self.local_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("🧠 Local embedding model loaded (MiniLM).")
        except Exception as e:
            logger.warning(f"⚠️ Local model init failed: {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text, with caching and fallback.
        
        Args:
            text: Input text to embed
        
        Returns:
            np.ndarray: Embedding vector (1536 for OpenAI, 384 for MiniLM)
        """
        if not text.strip():
            return np.zeros(384)
        
        # Check cache
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        # Try OpenAI first
        if self.openai_client:
            try:
                res = self.openai_client.embeddings.create(
                    input=text, model=self.model_name
                )
                embedding = np.array(res.data[0].embedding)
                self._embedding_cache[text] = embedding
                return embedding
            except Exception as e:
                logger.warning(f"⚠️ OpenAI embedding failed: {e}")
        
        # Fallback to local model
        if self.local_model:
            embedding = np.array(self.local_model.encode(text, normalize_embeddings=True))
            self._embedding_cache[text] = embedding
            return embedding
        
        # Final fallback
        logger.warning("No embedding model available, returning zeros")
        return np.zeros(384)

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1, vec2: Embedding vectors
        
        Returns:
            float: Similarity score (0..1)
        """
        if vec1 is None or vec2 is None:
            return 0.0
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def clear_cache(self):
        """Clear embedding cache."""
        self._embedding_cache.clear()
