# tools/semantic_matcher.py
"""
Semantic Matcher
- Computes semantic similarity between resume and JD using embeddings.
- Supports:
    - sentence-transformers (local) if installed
    - a user-provided embedding callable (e.g., OpenAI wrapper) via `embed_fn`
- Provides paragraph-level scores and overall semantic score (0..1)
- Returns structured dict consumable by the ATS scorer / frontend visualization
"""

from __future__ import annotations
import math
import logging
from typing import Callable, Dict, List, Optional
import numpy as np
import re

logger = logging.getLogger("semantic_matcher")
logger.setLevel(logging.INFO)


def _safe_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer
    except Exception:
        return None


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _chunk_text_to_paragraphs(text: str) -> List[str]:
    # split on two or more newlines or lines that look like separate bullets
    parts = re.split(r"\n{2,}|\r\n{2,}", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        # fallback: split into sentences groups of 3
        import nltk
        try:
            sents = nltk.sent_tokenize(text)
        except Exception:
            sents = re.split(r"[.?!]\s+", text)
        chunks = []
        for i in range(0, len(sents), 3):
            chunks.append(" ".join(sents[i:i+3]))
        return chunks or [text]
    return parts


def get_embed_fn_if_available() -> Optional[Callable]:
    """
    Returns an embedding function if sentence-transformers is available, else None.
    If returned, the function accepts List[str] and returns List[List[float]] embeddings.
    """
    ST = _safe_sentence_transformer()
    if ST:
        try:
            model = ST("all-MiniLM-L6-v2")
            def embed_fn(texts: List[str]) -> List[List[float]]:
                embs = model.encode(texts, convert_to_numpy=True)
                return [e.astype(float) for e in embs]
            return embed_fn
        except Exception as e:
            logger.warning("Failed to initialize sentence-transformers: %s", e)
    return None


def _get_embeddings_for_texts(texts: List[str], embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None):
    """
    embed_fn should accept List[str] and return List[List[float]] embeddings.
    If not provided, tries to use sentence-transformers all-MiniLM-L6-v2.
    """
    if embed_fn:
        return embed_fn(texts)

    ST = _safe_sentence_transformer()
    if ST:
        try:
            model = ST("all-MiniLM-L6-v2")
            embs = model.encode(texts, convert_to_numpy=True)
            return [e.astype(float) for e in embs]
        except Exception as e:
            logger.warning("sentence-transformers failed: %s", e)

    # Last resort: deterministic hash vectors (NOT semantically accurate)
    logger.warning("No embeddings backend available — using deterministic hash embeddings (fallback, low-quality).")
    embs = []
    for t in texts:
        vec = np.zeros(384, dtype=float)
        for i, ch in enumerate(t[:200]):
            vec[i % 384] += ord(ch) % 97
        embs.append(vec)
    return embs


def semantic_similarity_resume_jd(resume_text: str, jd_text: str, embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None) -> Dict:
    """
    Returns:
    {
        "overall_score": float (0..1),
        "paragraph_scores": [
            {"paragraph": str, "score": float, "best_matching_jd_chunk": str}
        ],
        "resume_chunks": [str],
        "jd_chunks": [str]
    }
    """
    resume_chunks = _chunk_text_to_paragraphs(resume_text)
    jd_chunks = _chunk_text_to_paragraphs(jd_text)

    # compute embeddings
    texts = resume_chunks + jd_chunks
    embs = _get_embeddings_for_texts(texts, embed_fn=embed_fn)
    # map
    r_embs = embs[:len(resume_chunks)]
    j_embs = embs[len(resume_chunks):]

    # Build paragraph-level similarity (each resume chunk matched against best jd chunk)
    paragraph_scores = []
    sums = []
    for i, r in enumerate(resume_chunks):
        best_score = 0.0
        best_j = None
        for j, j_emb in enumerate(j_embs):
            sc = _cosine(np.array(r_embs[i]), np.array(j_emb))
            if sc > best_score:
                best_score = sc
                best_j = jd_chunks[j]
        paragraph_scores.append({
            "paragraph": r,
            "score": float(best_score),
            "best_matching_jd_chunk": best_j
        })
        sums.append(best_score)

    # Overall score: mean of paragraph best matches but weighted by paragraph length
    weights = [max(1, len(p.split())) for p in resume_chunks]
    weighted_sum = sum(s * w for s, w in zip(sums, weights))
    overall = (weighted_sum / sum(weights)) if weights else 0.0
    # normalize to 0..100 for UI convenience
    overall_pct = float(round(overall * 100, 2))

    return {
        "overall_score": overall,            # 0..1
        "overall_pct": overall_pct,         # 0..100
        "paragraph_scores": paragraph_scores,
        "resume_chunks": resume_chunks,
        "jd_chunks": jd_chunks
    }


# Quick test / usage
if __name__ == "__main__":
    res = """
    Experienced Data Scientist skilled with Python, TensorFlow, and deploying models to AWS.
    Worked on model interpretability and production pipelines.
    """
    jd = """
    Looking for a Data Scientist with experience in Python, PyTorch or TensorFlow, cloud deployment (AWS/GCP),
    and knowledge of model explainability.
    """
    out = semantic_similarity_resume_jd(res, jd)
    import json
    print(json.dumps(out, indent=2))
