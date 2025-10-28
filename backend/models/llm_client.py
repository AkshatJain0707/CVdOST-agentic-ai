# backend/models/llm_client.py
"""
Lightweight LLM client abstraction that supports:
- OpenAI (official package)
- Simulated fallback or local transformers (if required)
This file should not raise on import; it logs and gracefully degrades.
"""
import os, logging, time
from typing import Optional, List, Dict
logger = logging.getLogger("resumate.llmclient")

# Try to import openai (official) but handle missing/invalid packages.
try:
    from openai import OpenAI, APIError, AuthenticationError
except Exception:
    OpenAI = None
    APIError = Exception
    AuthenticationError = Exception
    logger.warning("openai package not available; LLM calls will be simulated or local fallback used.")

# Optional local fallback via transformers (light)
try:
    from transformers import pipeline
except Exception:
    pipeline = None

class LLMClient:
    def __init__(self, provider: str = "auto"):
        self.provider = provider
        self.client = None
        self._init()

    def _init(self):
        # Use explicit env key or fallback
        api_key = os.getenv("OPENAI_API_KEY")
        if self.provider in ("openai", "auto") and api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=api_key)
                # simple validation
                try:
                    _ = self.client.models.list()  # quick call to validate
                except Exception:
                    # not fatal; still keep client
                    logger.info("OpenAI client created (validation may have failed).")
                logger.info("LLMClient: OpenAI initialized.")
                return
            except AuthenticationError as e:
                logger.error("LLMClient: OpenAI authentication error: %s", e)

        # local fallback
        if pipeline:
            try:
                self.client = pipeline("text-generation", model=os.getenv("LOCAL_MODEL", "distilgpt2"))
                self.provider = "local"
                logger.info("LLMClient: local transformer fallback initialized.")
                return
            except Exception as e:
                logger.warning("LLMClient: local pipeline not available: %s", e)

        # final: simulated stub
        self.client = None
        logger.warning("LLMClient: no real model available, using simulated responses.")

    def chat(self, prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.3, max_tokens: int = 512) -> str:
        if self.client is None:
            # simulated answer (deterministic lightweight)
            return f"[SIMULATED RESPONSE] Summary length {min(200, len(prompt)//4)} characters."
        if self.provider == "openai":
            try:
                resp = self.client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=temperature, max_tokens=max_tokens)
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.exception("OpenAI call failed")
                return f"[OPENAI ERROR] {e}"
        else:
            # local pipeline expects text input
            try:
                out = self.client(prompt, max_new_tokens=200)
                return out[0]["generated_text"]
            except Exception as e:
                logger.exception("Local pipeline call failed")
                return f"[LOCAL ERROR] {e}"

    def embed(self, text: str) -> List[float]:
        # prefer OpenAI embeddings if available
        if self.provider == "openai" and self.client:
            try:
                resp = self.client.embeddings.create(model="text-embedding-3-small", input=text)
                return resp.data[0].embedding
            except Exception as e:
                logger.exception("OpenAI embed failed")
                return []
        # else simulated: use very lightweight hashing to produce vector-like list
        v = [float((hash(text) >> i) & 0xFF) / 255.0 for i in range(0, 128)]
        return v
