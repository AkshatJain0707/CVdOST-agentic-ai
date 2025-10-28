# utils/llm_wrapper.py
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("LLMWrapper")
logger.setLevel(logging.INFO)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# try to import openai client (v1.0.0+)
openai_client = None
try:
    from openai import OpenAI
    if OPENAI_KEY:
        openai_client = OpenAI(api_key=OPENAI_KEY)
except Exception as e:
    logger.warning("OpenAI client not available: %s", e)
    openai_client = None

# try to import local generator (sentence-transformers + text-generation not used as default)
local_generator = None
try:
    from transformers import pipeline
    local_generator = pipeline if pipeline else None
except Exception:
    local_generator = None


class LLMWrapper:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.openai_available = openai_client is not None
        self.openai_client = openai_client
        self.local_available = local_generator is not None
        self._init_local()

        if self.openai_available:
            try:
                logger.info("OpenAI client initialized and will be used for LLM calls.")
            except Exception as e:
                logger.warning("OpenAI init failed: %s", e)
                self.openai_available = False

    def _init_local(self):
        self.local_gen = None
        if self.local_available:
            try:
                self.local_gen = local_generator("text-generation", model="distilgpt2")
                logger.info("Local fallback generator loaded (distilgpt2).")
            except Exception as e:
                logger.warning("Local generator not available: %s", e)
                self.local_gen = None

    def call(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Returns dict with keys: { 'text': str, 'raw': Any, 'meta': {} }
        """
        if self.openai_available and self.openai_client:
            try:
                # Use new OpenAI v1.0.0+ API
                resp = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = resp.choices[0].message.content.strip()
                return {"text": text, "raw": resp, "meta": {"backend": "openai"}}
            except Exception as e:
                logger.warning("OpenAI call failed: %s. Falling back.", e)

        # fallback to local generator if available
        if self.local_gen:
            try:
                out = self.local_gen(prompt, max_length= max_tokens, do_sample=False)
                text = out[0]["generated_text"]
                return {"text": text, "raw": out, "meta": {"backend": "local"}}
            except Exception as e:
                logger.warning("Local generator failed: %s", e)

        # deterministic simulated reply as last resort
        logger.info("LLM not available. Returning simulated response.")
        simulated = "SIMULATED: " + prompt[:400].replace("\n", " ") + "..."
        return {"text": simulated, "raw": None, "meta": {"backend": "simulated"}}
