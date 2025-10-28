# tools/resume_optimizer.py
import logging
from backend.utils.openai_wrapper import LLMWrapper

logger = logging.getLogger("ResumeOptimizer")
logger.setLevel(logging.INFO)

llm = LLMWrapper(model="gpt-3.5-turbo")


def optimize_resume_text(resume_text: str, jd_parsed: dict, max_tokens=800) -> str:
    """
    Gets an optimized resume text tuned to JD. Uses LLMWrapper with safe prompt.
    """

    prompt = f"""
You are a precise resume optimization assistant.
Given a candidate resume and a job requirements object, produce:
1) A concise optimized resume text (no fabrication),
2) A short list (3-6) of prioritized keywords to add,
3) A short change log explaining what you changed.

Return as JSON with keys: optimized_resume, suggested_keywords, changelog.

Resume:
---
{resume_text}

Job requirements (short JSON-like):
---
{jd_parsed}

Constraints:
- Do not invent experience or dates.
- Rephrase bullet points to be achievement/action oriented.
- Keep total resume length similar (do not create long essays).

Return only JSON.
"""
    res = llm.call(prompt, max_tokens=max_tokens, temperature=0.2)
    text = res.get("text", "")
    # attempt to extract JSON block
    import json
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end])
        except Exception:
            # fallback: return simple structured dict
            return {
                "optimized_resume": text[:4000],
                "suggested_keywords": [],
                "changelog": "LLM produced non-JSON; returning heuristic output."
            }
    else:
        return {
            "optimized_resume": text[:4000],
            "suggested_keywords": [],
            "changelog": "No JSON detected from LLM; trimmed raw output."
        }
