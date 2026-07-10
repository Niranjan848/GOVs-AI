"""
GOVs-AI FAISS Retriever
Wrapper around FAISS index for semantic search over document chunks.
"""

import os
import json
import numpy as np
import logging
from typing import List, Dict, Optional

from config import settings

logger = logging.getLogger(__name__)

# Global FAISS state
_index = None
_metadata: List[Dict] = []  # Parallel list storing chunk metadata
_METADATA_FILE = os.path.join(settings.FAISS_INDEX_PATH, "metadata.json")
_INDEX_FILE = os.path.join(settings.FAISS_INDEX_PATH, "index.faiss")


def _load_faiss():
    """Import FAISS (lazy to avoid import errors if not installed)."""
    try:
        import faiss
        return faiss
    except ImportError:
        logger.warning("FAISS not installed. Using mock retriever.")
        return None


def init_index(dimension: int = 384) -> None:
    """Initialize or load existing FAISS index."""
    global _index, _metadata
    faiss = _load_faiss()

    if faiss is None:
        logger.info("FAISS unavailable — running in mock retrieval mode.")
        return

    if os.path.exists(_INDEX_FILE):
        logger.info(f"Loading existing FAISS index from {_INDEX_FILE}")
        _index = faiss.read_index(_INDEX_FILE)
        if os.path.exists(_METADATA_FILE):
            with open(_METADATA_FILE, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
        logger.info(f"Loaded FAISS index with {_index.ntotal} vectors.")
    else:
        logger.info("Creating new FAISS index.")
        _index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity with normalized vectors)
        _metadata = []


def add_documents(embeddings: np.ndarray, metadata_list: List[Dict]) -> int:
    """Add document embeddings and metadata to the index."""
    global _index, _metadata
    faiss = _load_faiss()

    if faiss is None or _index is None:
        init_index()
        if _index is None:
            logger.warning("Cannot add documents — FAISS unavailable.")
            return 0

    # Ensure float32
    embeddings = embeddings.astype(np.float32)

    _index.add(embeddings)
    _metadata.extend(metadata_list)

    # Persist to disk
    faiss.write_index(_index, _INDEX_FILE)
    with open(_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(_metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Added {len(metadata_list)} documents. Total: {_index.ntotal}")
    return len(metadata_list)


def retrieve(query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
    """
    Retrieve top-k most similar documents for a query.
    Returns list of dicts with 'content', 'source', 'page', 'score'.
    """
    global _index, _metadata

    if _index is None or _index.ntotal == 0:
        return _get_mock_results()

    # Ensure proper shape
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    query_embedding = query_embedding.astype(np.float32)

    k = min(k, _index.ntotal)
    scores, indices = _index.search(query_embedding, k)

    results = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < 0 or idx >= len(_metadata):
            continue
        result = _metadata[idx].copy()
        result["score"] = float(score)
        result["rank"] = i + 1
        results.append(result)

    return results


def get_index_stats() -> Dict:
    """Return index statistics for admin dashboard."""
    if _index is None:
        return {"status": "not_initialized", "total_vectors": 0, "total_documents": 0}

    unique_sources = set()
    for m in _metadata:
        unique_sources.add(m.get("source", "unknown"))

    return {
        "status": "active",
        "total_vectors": _index.ntotal,
        "total_documents": len(unique_sources),
        "sources": list(unique_sources),
    }


def _get_mock_results() -> List[Dict]:
    """Return mock retrieval results when FAISS is empty or unavailable."""
    return [
        {
            "content": "PM Kisan Samman Nidhi provides ₹6,000 per year to small and marginal farmers in three installments of ₹2,000 each. Eligibility: All landholding farmer families with cultivable land. Exclusions: Institutional landholders, farmer families with government employees, income tax payers.",
            "source": "pm_kisan_guidelines.pdf",
            "page": 1,
            "score": 0.92,
            "rank": 1,
        },
        {
            "content": "Pradhan Mantri Mudra Yojana (PMMY) offers loans up to ₹10 lakh for non-corporate, non-farm small/micro enterprises. Three categories: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 lakh), Tarun (₹5 lakh to ₹10 lakh). No collateral required.",
            "source": "mudra_yojana_scheme.pdf",
            "page": 2,
            "score": 0.87,
            "rank": 2,
        },
        {
            "content": "Ayushman Bharat PM-JAY provides health coverage of ₹5 lakh per family per year. Covers secondary and tertiary hospitalization. Eligibility based on SECC 2011 data and expanded categories including senior citizens aged 70+.",
            "source": "ayushman_bharat_pmjay.pdf",
            "page": 1,
            "score": 0.83,
            "rank": 3,
        },
    ]
