# tools/skill_comparator.py
"""
Skill Comparator
- Input: resume_skills (list or dict), jd_skills (list or text)
- Outputs:
    {
        "skill_fit_index": float (0..1),
        "match_percentage": float (0..100),
        "matched_skills": [{"resume_skill": str, "jd_skill": str, "similarity": float}],
        "missing_skills": [ {"skill": str, "suggestion": str (maybe phrase)} ],
        "extra_resume_skills": [str],
        "summary": str
    }

- Uses normalized string matching + embedding fallback to detect near-synonyms.
"""

from __future__ import annotations
import logging
from typing import Callable, Dict, List, Optional, Tuple
import re
import numpy as np
from collections import defaultdict

logger = logging.getLogger("skill_comparator")
logger.setLevel(logging.INFO)


def _normalize(x: str) -> str:
    x = (x or "").strip().lower()
    x = re.sub(r"[^a-z0-9+#\.\- ]", "", x)
    x = re.sub(r"\s+", " ", x)
    return x


def _simple_token_overlap(a: str, b: str) -> float:
    aset = set(_normalize(a).split())
    bset = set(_normalize(b).split())
    if not aset or not bset:
        return 0.0
    return len(aset & bset) / max(len(aset), len(bset))


def _embedding_similarity(a_emb: np.ndarray, b_emb: np.ndarray) -> float:
    denom = (np.linalg.norm(a_emb) * np.linalg.norm(b_emb))
    if denom == 0:
        return 0.0
    return float(np.dot(a_emb, b_emb) / denom)


def compare_skills(
    resume_skills: List[str],
    jd_skills: List[str],
    embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    semantic_threshold: float = 0.75
) -> Dict:
    """
    Compare two skill lists.

    If embed_fn provided, it should accept List[str] and return numpy-like embeddings.

    Returns dict described above.
    """
    rskills = [s for s in resume_skills or []]
    jskills = [s for s in jd_skills or []]
    rnorm = [_normalize(s) for s in rskills]
    jnorm = [_normalize(s) for s in jskills]

    # fast exact or token-overlap matching
    matched = []
    matched_j_idx = set()
    for i, r in enumerate(rnorm):
        best_j = None
        best_sim = 0.0
        for j, jj in enumerate(jnorm):
            if j in matched_j_idx:
                continue
            sim = _simple_token_overlap(r, jj)
            if sim > best_sim:
                best_sim = sim
                best_j = (j, jj)
            # perfect exact
            if r == jj:
                best_sim = 1.0
                best_j = (j, jj)
                break
        if best_j and best_sim > 0.6:
            matched.append({"resume_skill": rskills[i], "jd_skill": best_j[1], "similarity": float(round(best_sim, 3))})
            matched_j_idx.add(best_j[0])

    # If embedding function is provided, run semantic matching for unmatched items
    if embed_fn:
        # Build lists of unmatched items
        unmatched_r = [r for idx, r in enumerate(rskills) if idx >= 0 and all(m["resume_skill"] != r for m in matched)]
        unmatched_j = [j for idx, j in enumerate(jskills) if idx not in matched_j_idx]
        try:
            cand_texts = unmatched_r + unmatched_j
            if cand_texts:
                embs = embed_fn(cand_texts)
                # convert to numpy arrays
                import numpy as _np
                embs = [_np.array(e) for e in embs]
                r_embs = embs[:len(unmatched_r)]
                j_embs = embs[len(unmatched_r):]
                for i_r, r in enumerate(unmatched_r):
                    best_j = None
                    best_sim = 0.0
                    for j_i, j in enumerate(unmatched_j):
                        sim = _embedding_similarity(r_embs[i_r], j_embs[j_i])
                        if sim > best_sim:
                            best_sim = sim
                            best_j = j
                    if best_sim >= semantic_threshold:
                        matched.append({"resume_skill": r, "jd_skill": best_j, "similarity": float(round(best_sim, 3))})
                        # mark j matched
                        j_index = jskills.index(best_j)
                        matched_j_idx.add(j_index)
        except Exception as e:
            logger.warning("Embedding-based matching failed: %s", e)

    # compute missing skills = jd skills not matched
    missing = []
    for idx, j in enumerate(jskills):
        if idx not in matched_j_idx:
            missing.append(j)

    # extras: resume skills not mapped to JD
    matched_resumes = {m["resume_skill"] for m in matched}
    extras = [r for r in rskills if r not in matched_resumes]

    # compute match percentage and Skill Fit Index (SFI)
    match_pct = (len(jskills) - len(missing)) / max(1, len(jskills))
    # SFI: combine match_pct with average similarity of matched pairs and penalize major gaps
    if matched:
        avg_sim = sum(m["similarity"] for m in matched) / len(matched)
    else:
        avg_sim = 0.0
    # Experience of resume isn't part here; Orchestrator adds experience relevance later.
    sfi = 0.7 * match_pct + 0.3 * avg_sim  # weights can be tuned

    # Suggestions: for each missing skill provide phrase suggestions
    suggestions = []
    for ms in missing:
        suggestions.append({"skill": ms, "suggestion": f"Include relevant projects or keywords related to '{ms}' (e.g., 'Worked with {ms} to ...')"} )

    return {
        "skill_fit_index": float(round(sfi, 4)),
        "match_percentage": float(round(match_pct * 100, 2)),
        "matched_skills": matched,
        "missing_skills": suggestions,
        "extra_resume_skills": extras,
        "summary": f"Matched {len(jskills)-len(missing)} of {len(jskills)} JD skills."
    }


# Quick demo
if __name__ == "__main__":
    resume = ["Python", "tensorflow", "aws", "data analysis", "team leadership"]
    jd = ["Python", "PyTorch", "model deployment", "AWS", "communication"]
    out = compare_skills(resume, jd)
    import json
    print(json.dumps(out, indent=2))
