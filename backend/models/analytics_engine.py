# backend/models/analytics_engine.py
"""
Optimized Analytics Engine for ATS scoring.
Combines semantic, keyword, structural, and linguistic analysis for robust scoring.
"""

import re
import numpy as np
from math import exp
from typing import List, Dict, Any, Optional

from backend.utils.embeddings import EmbeddingEngine
from backend.utils.logger import get_logger

logger = get_logger("AnalyticsEngine")

# Pre-compiled regex patterns for performance
_CONTACT_PATTERN = re.compile(r"\b(contact|email|phone|address)\b", re.I)
_BULLET_PATTERN = re.compile(r"\n\s*[-•\*]\s+")
_SECTION_PATTERN = re.compile(r"\b(experience|education|skills|projects)\b", re.I)
_TOKENIZE_PATTERN = re.compile(r"\b[a-z0-9\+\#\.\-]+\b")

# Action verbs used in professional resumes
_ACTION_VERBS = frozenset([
    "led", "implemented", "built", "designed", "optimized", "improved", 
    "reduced", "increased", "achieved", "delivered", "managed", "created",
    "launched", "orchestrated", "engineered", "developed", "spearheaded"
])

# Scoring weights (tuned for conservative scoring)
_DEFAULT_WEIGHTS = {
    "semantic": 0.35,
    "keyword": 0.30,
    "structure": 0.20,
    "action": 0.15,
}


def _tokenize(s: str) -> List[str]:
    """Fast tokenization: lowercase and extract alphanumeric + common symbols."""
    return _TOKENIZE_PATTERN.findall(s.lower())


class AnalyticsEngine:
    """
    Multi-dimensional ATS scoring engine.
    
    Combines:
    - Semantic similarity (embedding-based)
    - Keyword overlap (skill matching)
    - Structure analysis (formatting, sections)
    - Action verb density (impact language)
    """
    
    def __init__(self, emb_service: EmbeddingEngine):
        """
        Initialize with an embedding service.
        
        Args:
            emb_service: EmbeddingEngine instance for semantic scoring
        """
        self.emb = emb_service
        self._score_cache = {}

    def semantic_match_score(self, resume_vec: np.ndarray, jd_vec: np.ndarray) -> float:
        """
        Compute semantic similarity score (0-100).
        
        Args:
            resume_vec: Resume embedding vector
            jd_vec: Job description embedding vector
        
        Returns:
            float: Similarity score 0-100
        """
        if resume_vec is None or jd_vec is None:
            return 0.0
        sim = EmbeddingEngine.cosine_similarity(resume_vec, jd_vec)
        return float(sim * 100.0)

    def keyword_overlap_score(self, resume_text: str, jd_skills: Optional[List[str]]) -> float:
        """
        Compute keyword overlap score (0-100).
        
        Args:
            resume_text: Resume text
            jd_skills: List of required skills from JD
        
        Returns:
            float: Overlap score 0-100
        """
        if not jd_skills:
            return 0.0
        
        resume_tokens = set(_tokenize(resume_text))
        jd_tokens = set(s.lower() for s in jd_skills)
        
        if not jd_tokens:
            return 0.0
        
        overlap = len(resume_tokens.intersection(jd_tokens))
        score = overlap / len(jd_tokens)
        return float(score * 100.0)

    def structure_score(self, resume_text: str) -> float:
        """
        Evaluate resume structure quality (0-100).
        Heuristics: contact info, bullet points, standard sections.
        
        Args:
            resume_text: Resume text
        
        Returns:
            float: Structure score 0-100
        """
        score = 0.0
        
        # Contact information
        if _CONTACT_PATTERN.search(resume_text):
            score += 25
        
        # Bullet points (max 20 points)
        bullets = len(_BULLET_PATTERN.findall(resume_text))
        score += min(bullets, 10) * 2
        
        # Standard sections
        if _SECTION_PATTERN.search(resume_text):
            score += 25
        
        return float(min(score, 100.0))

    def action_verbs_score(self, resume_text: str) -> float:
        """
        Score based on impact/action verb density (0-100).
        
        Args:
            resume_text: Resume text
        
        Returns:
            float: Action verb score 0-100
        """
        text_lower = resume_text.lower()
        verb_count = sum(text_lower.count(verb) for verb in _ACTION_VERBS)
        return float(min(verb_count * 10, 100.0))

    def ats_score(
        self, 
        resume_text: str, 
        jd_text: str, 
        semantic_score: float, 
        keyword_overlap: float,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Compute comprehensive ATS score with breakdown.
        
        Args:
            resume_text: Resume text
            jd_text: Job description text
            semantic_score: Semantic similarity score (0-100)
            keyword_overlap: Keyword overlap score (0-100)
            weights: Optional custom weight dict (defaults to _DEFAULT_WEIGHTS)
        
        Returns:
            Dict with score, components, and weights breakdown
        """
        if weights is None:
            weights = _DEFAULT_WEIGHTS.copy()
        
        # Compute structural scores
        struct_score = self.structure_score(resume_text)
        action_score = self.action_verbs_score(resume_text)
        
        # Normalize inputs to 0-100 range
        sem_norm = float(semantic_score) / 100.0
        kw_norm = float(keyword_overlap) / 100.0
        struct_norm = struct_score / 100.0
        action_norm = action_score / 100.0
        
        # Weighted combination
        raw = (
            sem_norm * weights["semantic"]
            + kw_norm * weights["keyword"]
            + struct_norm * weights["structure"]
            + action_norm * weights["action"]
        )
        
        # Apply sigmoid smoothing to pull extremes inward
        sigmoid = 100.0 / (1.0 + exp(-(raw / 0.25 - 2.0)))
        final_score = float(sigmoid)
        
        return {
            "score": round(final_score, 2),
            "components": {
                "semantic": round(semantic_score, 2),
                "keyword_overlap": round(keyword_overlap, 2),
                "structure": round(struct_score, 2),
                "action_verbs": round(action_score, 2),
            },
            "weights": weights,
            "interpretation": self._score_interpretation(final_score)
        }

    @staticmethod
    def _score_interpretation(score: float) -> str:
        """Provide human-readable interpretation of ATS score."""
        if score >= 80:
            return "Excellent match - highly likely to pass ATS"
        elif score >= 60:
            return "Good match - likely to pass ATS"
        elif score >= 40:
            return "Moderate match - may pass ATS with optimization"
        else:
            return "Poor match - significant optimization needed"

    def clear_cache(self):
        """Clear any internal caches."""
        self._score_cache.clear()
        if hasattr(self.emb, 'clear_cache'):
            self.emb.clear_cache()
