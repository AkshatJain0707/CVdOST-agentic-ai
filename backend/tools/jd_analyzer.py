# tools/jd_analyzer.py
import logging
import re
from typing import Dict, Any, List
from backend.utils.openai_wrapper import LLMWrapper

logger = logging.getLogger("JDAnalyzer")
logger.setLevel(logging.INFO)

llm = LLMWrapper()


def heuristic_extract(jd_text: str) -> Dict[str, Any]:
    # simple heuristics for skills and seniority
    skills = set(re.findall(r"\b[A-Za-z+#\.\-]{2,}\b", jd_text))
    # filter common words
    stop = {"and", "or", "the", "to", "with", "of", "in", "for", "on"}
    skills = [s for s in skills if s.lower() not in stop and len(s) > 2]
    # pick lines with keywords
    lines = jd_text.splitlines()
    responsibilities = [l.strip() for l in lines if re.search(r"\b(responsibilit|responsible|must have|should|experience|responsibilities)\b", l, re.I)]
    seniority = "senior" if re.search(r"\b(senior|lead|principal)\b", jd_text, re.I) else ("junior" if re.search(r"\b(junior|entry)\b", jd_text, re.I) else "mid")
    return {"skills": skills[:120], "responsibilities": responsibilities, "seniority": seniority}


def extract_requirements(jd_text: str) -> Dict[str, Any]:
    """
    1. Try LLM extraction (preferred).
    2. On failure, fallback to heuristics.
    """
    prompt = f"""Extract a JSON object from the following job description with keys:
- required_skills: list of phrases
- preferred_skills: list of phrases
- responsibilities: list of short strings
- seniority: one of [junior, mid, senior]
Return only JSON.

JD:
---
{jd_text}
---
"""
    try:
        resp = llm.call(prompt, max_tokens=400)
        if resp and resp.get("text"):
            import json
            txt = resp["text"].strip()
            # attempt parse JSON block inside returned text
            start = txt.find("{")
            end = txt.rfind("}") + 1
            if start != -1 and end != -1:
                jtxt = txt[start:end]
                try:
                    parsed = json.loads(jtxt)
                    return parsed
                except Exception:
                    logger.warning("LLM returned non-JSON; falling back to heuristics.")
    except Exception as e:
        logger.warning("LLM JD extraction failed: %s", e)
    # fallback
    return heuristic_extract(jd_text)
