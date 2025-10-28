# backend/tools/skill_extr# tools/resume_skill_extractor.py
"""
Resume Skill Extractor (production-ready)
- Attempts to extract: technical skills, tools/platforms, soft skills, experiences, education
- Primary strategy: spaCy NER + pattern extraction for "Skills:" lists
- Fallbacks: regex heuristics and simple token frequency
- Returns a normalized dict all modules can consume
"""

from __future__ import annotations
import re
import logging
from collections import Counter
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("resume_skill_extractor")
logger.setLevel(logging.INFO)


def _safe_import_spacy():
    try:
        import spacy
        return spacy
    except Exception:
        return None


def _normalize_token(tok: str) -> str:
    t = tok.strip().lower()
    t = re.sub(r"[^a-z0-9+\-#\.\s]", "", t)  # keep + - # . for things like C++, c#, node.js
    t = re.sub(r"\s+", " ", t)
    return t


def _extract_list_from_text(text: str, label_keywords: List[str]) -> List[str]:
    """
    Find lines containing label keywords (e.g. 'skills', 'technologies') and parse
    comma/pipe/semicolon separated values.
    """
    results = []
    lines = text.splitlines()
    for line in lines:
        low = line.lower()
        for key in label_keywords:
            if key in low:
                # extract after the keyword
                # e.g. "Skills: Python, SQL, TensorFlow"
                part = re.split(rf"{re.escape(key)}\s*[:\-]?", low, maxsplit=1)
                if len(part) > 1:
                    vals = re.split(r"[;,|/••·]", part[1])
                else:
                    vals = re.split(r"[,;|/••·]", line)
                for v in vals:
                    v = v.strip()
                    if v:
                        results.append(v)
    return results


def _top_n_terms(text: str, n: int = 30) -> List[str]:
    # Simple fallback: word frequency (excluding stopwords)
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stopwords = set(ENGLISH_STOP_WORDS)
    except Exception:
        stopwords = {
            "and", "or", "the", "a", "an", "with", "experience", "years", "year", "candidate",
            "worked", "work", "in", "of", "for", "to", "on", "as", "is"
        }
    tokens = re.findall(r"[A-Za-z0-9+#\.\-]+", text)
    tokens = [t for t in tokens if t.lower() not in stopwords and len(t) > 1]
    counts = Counter(t.lower() for t in tokens)
    common = [t for t, _ in counts.most_common(n)]
    return common


def extract_skills(resume_text: str, top_n: int = 80) -> Dict:
    """
    Main entrypoint.

    Returns:
        {
            "skills": List[str],        # technical hard skills (normalized)
            "tools": List[str],         # tools/platforms
            "soft_skills": List[str],   # soft skills heuristically detected
            "experience_lines": List[str], # key experience lines (for later parsing)
            "education_lines": List[str],  # education lines
            "raw_text": str
        }
    """
    resume_text = resume_text or ""
    out = {
        "skills": [],
        "tools": [],
        "soft_skills": [],
        "experience_lines": [],
        "education_lines": [],
        "raw_text": resume_text
    }

    # 1) Try spaCy NER if available for ORG, PRODUCT, SKILL-like tokens
    spacy = _safe_import_spacy()
    if spacy:
        try:
            # try medium small english model first (fast)
            try:
                nlp = spacy.load("en_core_web_sm")
            except Exception:
                # if model missing, load blank and add tagger — still useful for POS
                nlp = spacy.blank("en")
            doc = nlp(resume_text)
            # heuristics: capture noun chunks and entities that look like technologies
            tech_candidates = set()
            soft_candidates = set()
            for ent in doc.ents:
                text = ent.text.strip()
                if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART", "LANGUAGE"):
                    tech_candidates.add(text)
            # noun chunks
            for nc in doc.noun_chunks:
                txt = nc.text.strip()
                if len(txt.split()) <= 4 and re.search(r"[A-Za-z0-9+#\-\.]", txt):
                    tech_candidates.add(txt)
            # POS-based soft skills (adjectives + nouns like leadership)
            for token in doc:
                if token.pos_ in ("ADJ", "NOUN") and len(token.text) > 2:
                    if token.text.lower() in {"leadership", "communication", "teamwork", "management", "collaboration", "problem-solving", "organization", "organized"}:
                        soft_candidates.add(token.text)
            tech_list = [_normalize_token(t) for t in tech_candidates if len(t.strip()) > 1]
            out["skills"].extend(tech_list[:top_n])
            out["soft_skills"].extend(list(set(_normalize_token(s) for s in soft_candidates)))
        except Exception as e:
            logger.warning("spaCy extraction failed, falling back to heuristics: %s", e)

    # 2) Extract explicit lists like "Skills:" "Technical Skills:" "Tools:"
    list_skills = _extract_list_from_text(resume_text, ["skills", "technical skills", "technologies", "tools", "proficient in", "skills & technologies", "tech stack"])
    list_skills = [_normalize_token(s) for s in list_skills if s.strip()]
    if list_skills:
        out["skills"].extend(list_skills)

    # 3) Experience and Education heuristics
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    exp_lines = [ln for ln in lines if re.search(r"\b(years?|yrs?|\d{4})\b", ln.lower()) and len(ln) > 20]
    edu_lines = [ln for ln in lines if re.search(r"\b(bachelor|master|b\.sc|m\.sc|phd|degree|university|college)\b", ln.lower())]
    out["experience_lines"] = exp_lines[:20]
    out["education_lines"] = edu_lines[:10]

    # 4) If still short on skills, use top term frequency
    if len(out["skills"]) < 8:
        top_terms = _top_n_terms(resume_text, n=top_n)
        out["skills"].extend([_normalize_token(t) for t in top_terms])

    # 5) simple split into tools vs skills by heuristics (tools often short tokens, languages, libs)
    candidates = list(dict.fromkeys([_normalize_token(s) for s in out["skills"] if s]))
    tool_like = []
    skill_like = []
    for c in candidates:
        # heuristics: languages / framework patterns
        if re.search(r"^(c#|c\+\+|python|java(script)?|node|nodejs|react|angular|tensorflow|pytorch|sql|postgres|mysql|excel|docker|kubernetes|aws|azure|gcp|matlab|r\b|scala|bash|powershell|keras|spark|hadoop|git)$", c):
            tool_like.append(c)
        elif len(c.split()) <= 3 and re.search(r"[a-z0-9+#\-\.]", c):
            skill_like.append(c)
        else:
            skill_like.append(c)

    # Soft skills candidate from simple word lists
    known_soft = {"communication", "leadership", "teamwork", "collaboration", "management", "problem solving", "adaptability", "time management", "presentation", "negotiation"}
    soft_found = [s for s in candidates if s in known_soft]
    out["soft_skills"] = list(dict.fromkeys(out["soft_skills"] + soft_found))

    out["tools"] = list(dict.fromkeys(tool_like))
    out["skills"] = list(dict.fromkeys([s for s in skill_like if s not in out["tools"]]))

    # Return trimmed lists
    for k in ("skills", "tools", "soft_skills"):
        out[k] = out[k][:120]

    return out


# Quick test
if __name__ == "__main__":
    sample = """
    John Doe
    Skills: Python, SQL, TensorFlow, PyTorch, Docker, Kubernetes, Git
    Experience: 5 years as Data Scientist at Acme Corp (2018-2023)
    Soft Skills: Leadership, Communication, Teamwork
    Education: Master of Science in Computer Science, University X
    """
    print(extract_skills(sample))
