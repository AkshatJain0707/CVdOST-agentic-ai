# tools/ats_scorer.py
"""
R-ATSX 2.0 — Robust, explainable ATS scoring engine.

Combines:
 - semantic_score (0..1)     -> how semantically close resume is to JD
 - skill_fit_index (0..1)    -> skill coverage & similarity
 - keyword_density (0..1)    -> JD keywords density in resume
 - action_verb_ratio (0..1)  -> measure of active verbs (impactful language)
 - experience_relevance (0..1) -> years / role match heuristic
 - formatting_penalty (0..1) -> penalize extremely short/poorly structured resumes

Produces:
 {
   "score": 0..100,
   "components": {... each 0..100 ...},
   "weights": {...},
   "explanations": [...],
   "suggestions": [...]
 }
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Callable, Optional

# Small helper sets
_ACTION_VERBS = {
    "achieved","improved","reduced","increased","developed","designed","built",
    "led","managed","created","launched","delivered","optimized","implemented","engineered",
    "streamlined","orchestrated","built","spearheaded","built","coordinated","advised"
}
_JD_KEYWORD_SPLIT_RE = re.compile(r"[^\w+#\.\-]+")

def _clamp01(x):
    return max(0.0, min(1.0, float(x)))

def _safe_len(x):
    try:
        return len(x)
    except Exception:
        return 0

def compute_keyword_density(resume_text: str, jd_text: str, jd_keywords: Optional[List[str]] = None) -> float:
    """
    Keyword density: fraction of JD keywords that appear in resume (normalized).
    If jd_keywords not provided, derive from jd_text by tokenizing and taking unique tokens.
    Returns 0..1
    """
    if not jd_keywords:
        tokens = [t.lower() for t in re.split(_JD_KEYWORD_SPLIT_RE, jd_text) if t and len(t) > 1]
        # select candidate keywords by frequency heuristics
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        # pick top 30 distinct tokens as "keywords"
        jd_keywords = [k for k, _ in sorted_tokens[:30]]
    if not jd_keywords:
        return 0.0
    rt = resume_text.lower()
    found = 0
    for kw in jd_keywords:
        if kw.strip() and kw.lower() in rt:
            found += 1
    return _clamp01(found / len(jd_keywords))


def compute_action_verb_ratio(resume_text: str) -> float:
    """
    Fraction of sentences that include an action verb from the curated list.
    Gives a sense of "active language".
    """
    sents = re.split(r"[.?!\n]+", resume_text)
    if not sents:
        return 0.0
    hit = 0
    for s in sents:
        words = set([w.lower().strip(".,;:()") for w in s.split() if w])
        if words & _ACTION_VERBS:
            hit += 1
    return _clamp01(hit / len(sents))


def compute_formatting_penalty(resume_text: str) -> float:
    """
    Return a penalty in 0..1 where 1 is full penalty (bad formatting).
    Penalty increases for extremely short resumes, huge blocks of text, or very few bullets.
    We'll invert it later (we want a 'format_quality' signal).
    """
    text = resume_text.strip()
    if not text:
        return 1.0
    # penalize if <100 words
    words = re.findall(r"\w+", text)
    if len(words) < 120:
        base_pen = 0.7
    elif len(words) < 250:
        base_pen = 0.3
    else:
        base_pen = 0.0
    # add penalty for long paragraphs (no newlines)
    paragraphs = [p for p in re.split(r"\n{2,}", text) if p.strip()]
    long_para_pen = 0.0
    if paragraphs:
        avg_len = sum(len(p) for p in paragraphs) / len(paragraphs)
        if avg_len > 1000:
            long_para_pen = 0.4
        elif avg_len > 400:
            long_para_pen = 0.2
    # few bullets check
    bullets = len(re.findall(r"^[\-\*\u2022]\s+", text, flags=re.MULTILINE))
    bullet_pen = 0.0
    if bullets < 3:
        bullet_pen = 0.2
    total_pen = _clamp01(base_pen + long_para_pen + bullet_pen)
    return total_pen


def compute_experience_relevance(resume_text: str, jd_text: str) -> float:
    """
    Heuristic to evaluate years-of-experience relevance:
    - Extract 'X years' mentions, prefer >= required years in JD (if JD states years)
    - If JD mentions seniority words (senior, lead), reward presence of similar in resume
    Returns 0..1
    """
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    # find years mentioned in JD
    def _extract_years(s):
        m = re.search(r"(\d+)\+?\s*(years|yrs|year)", s)
        if m:
            return int(m.group(1))
        return None
    req_years = _extract_years(jd_lower)
    res_years = _extract_years(resume_lower)
    score = 0.0
    # if JD asks specific years
    if req_years:
        if res_years:
            # clamp difference
            diff = res_years - req_years
            if diff >= 0:
                score = 1.0
            else:
                score = _clamp01(0.5 + 0.5 * (res_years / req_years))
        else:
            # no explicit years, try look for 'senior/lead' vs 'junior'
            if re.search(r"\b(senior|lead|principal|manager|director)\b", resume_lower):
                score = 0.9
            else:
                score = 0.5
    else:
        # no explicit req -> score from presence of senior keywords
        if re.search(r"\b(senior|lead|principal|manager|director)\b", jd_lower):
            score = 0.8 if re.search(r"\b(senior|lead|principal|manager|director)\b", resume_lower) else 0.4
        else:
            # default: presence of experience lines -> decent
            if re.search(r"\b(years?|\d{4})\b", resume_lower):
                score = 0.75
            else:
                score = 0.45
    return _clamp01(score)


def fuse_components(
    semantic_score: float,
    skill_fit_index: float,
    keyword_density: float,
    action_verb_ratio: float,
    experience_relevance: float,
    formatting_penalty: float,
    weights: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Combine signals using tunable weights and produce normalized 0..100 final score.
    Returns dict with components (0..100), final score, and explanations.
    """
    # default weights (sum to 1)
    if not weights:
        weights = {
            "semantic": 0.30,
            "skills": 0.30,
            "keywords": 0.15,
            "action_verbs": 0.08,
            "experience": 0.12,
            "formatting": -0.05  # negative weight (penalty), applied subtractively
        }
    # clamp inputs to 0..1
    s_sem = _clamp01(semantic_score)
    s_ski = _clamp01(skill_fit_index)
    s_key = _clamp01(keyword_density)
    s_act = _clamp01(action_verb_ratio)
    s_exp = _clamp01(experience_relevance)
    s_fmt_pen = _clamp01(formatting_penalty)

    # component scores 0..100
    c_sem = round(s_sem * 100, 2)
    c_ski = round(s_ski * 100, 2)
    c_key = round(s_key * 100, 2)
    c_act = round(s_act * 100, 2)
    c_exp = round(s_exp * 100, 2)
    c_fmt = round(s_fmt_pen * 100, 2)

    # Weighted sum (formatting is a penalty -> subtract)
    positive_sum = (
        weights["semantic"] * s_sem
        + weights["skills"] * s_ski
        + weights["keywords"] * s_key
        + weights["action_verbs"] * s_act
        + weights["experience"] * s_exp
    )
    penalty = max(0.0, weights.get("formatting", 0.0) * s_fmt_pen)  # negative already
    raw_score = positive_sum + penalty
    # normalize raw_score to 0..1 (weights are small; ensure we clamp)
    final_norm = _clamp01(raw_score / (sum(abs(v) for k, v in weights.items() if k != "formatting") or 1))
    final_pct = round(final_norm * 100, 2)

    explanations = [
        f"Semantic match contributes {round(weights['semantic']*100,1)}% -> {c_sem} pts",
        f"Skill fit contributes {round(weights['skills']*100,1)}% -> {c_ski} pts",
        f"Keyword density contributes {round(weights['keywords']*100,1)}% -> {c_key} pts",
        f"Action verbs contribute {round(weights['action_verbs']*100,1)}% -> {c_act} pts",
        f"Experience relevance contributes {round(weights['experience']*100,1)}% -> {c_exp} pts",
    ]
    if weights.get("formatting", 0) < 0:
        explanations.append(f"Formatting penalty (subtracts) {abs(round(weights['formatting']*100,1))}% -> {c_fmt} pts penalty")

    suggestions: List[str] = []
    if c_ski < 60:
        suggestions.append("Add or highlight missing technical skills that match the JD (see 'missing_skills' in comparison).")
    if c_key < 50:
        suggestions.append("Include more JD keywords (exact phrases) in relevant bullet points, without fabricating experience.")
    if c_act < 40:
        suggestions.append("Use more active verbs (achieved, improved, designed, led) to describe responsibilities and impact.")
    if c_fmt > 50:
        suggestions.append("Improve formatting: use concise bullets, add section headers, and increase resume length if under 120 words.")
    if c_exp < 50:
        suggestions.append("Clarify years of experience and emphasize senior-level roles or results if applicable.")

    return {
        "components": {
            "semantic": c_sem,
            "skills": c_ski,
            "keyword_density": c_key,
            "action_verb_ratio": c_act,
            "experience_relevance": c_exp,
            "formatting_penalty": c_fmt
        },
        "weights": weights,
        "final_score": final_pct,
        "final_score_norm": final_norm,
        "explanations": explanations,
        "suggestions": suggestions
    }


def score_application(
    resume_text: str,
    jd_text: str,
    semantic_score: float,
    skill_fit_index: float,
    jd_keywords: Optional[List[str]] = None,
    embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict:
    """
    High-level function used by orchestrator. Accepts precomputed semantic_score (0..1)
    and skill_fit_index (0..1). Computes other signals and fuses them.
    """
    # compute keyword density
    kd = compute_keyword_density(resume_text, jd_text, jd_keywords=jd_keywords)
    av = compute_action_verb_ratio(resume_text)
    exp_rel = compute_experience_relevance(resume_text, jd_text)
    fmt_pen = compute_formatting_penalty(resume_text)
    fused = fuse_components(
        semantic_score=semantic_score,
        skill_fit_index=skill_fit_index,
        keyword_density=kd,
        action_verb_ratio=av,
        experience_relevance=exp_rel,
        formatting_penalty=fmt_pen,
        weights=weights
    )
    # give final shape
    return {
        "ats": fused,
        "raw_signals": {
            "semantic_score": round(semantic_score, 4),
            "skill_fit_index": round(skill_fit_index, 4),
            "keyword_density": round(kd, 4),
            "action_verb_ratio": round(av, 4),
            "experience_relevance": round(exp_rel, 4),
            "formatting_penalty": round(fmt_pen, 4)
        }
    }


