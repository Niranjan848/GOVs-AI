"""
GOVs-AI Embedding Module
Singleton embedding model for FAISS vector operations.
Uses sentence-transformers/all-MiniLM-L6-v2 for lightweight, fast embeddings.
"""

import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Global singleton — loaded once on first use
_model = None
_dimension = 384  # all-MiniLM-L6-v2 output dimension


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
            logger.info("Loading embedding model: all-MiniLM-L6-v2...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model: {e}")
            logger.info("Falling back to mock embeddings for demo mode.")
            _model = "mock"
    return _model


def embed_query(text: str) -> np.ndarray:
    """Generate embedding for a single query string."""
    model = _get_model()
    if model == "mock":
        return _mock_embedding(text)
    return model.encode(text, normalize_embeddings=True)


def embed_documents(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """Generate embeddings for a batch of document chunks."""
    model = _get_model()
    if model == "mock":
        return np.array([_mock_embedding(t) for t in texts])
    return model.encode(texts, normalize_embeddings=True, batch_size=batch_size, show_progress_bar=True)


def get_dimension() -> int:
    """Return the embedding vector dimension."""
    return _dimension


def _mock_embedding(text: str) -> np.ndarray:
    """Generate deterministic mock embeddings for demo mode (no model download needed)."""
    np.random.seed(hash(text) % (2**31))
    vec = np.random.randn(_dimension).astype(np.float32)
    vec = vec / np.linalg.norm(vec)  # L2 normalize
    return vec
