
# backend/utils/text_utils.py
"""
Helpers: docx extraction, cleaning, tokenization
"""
import io, tempfile, logging
logger = logging.getLogger("resumate.textutils")

def extract_text_from_docx_bytes(b: bytes) -> str:
    try:
        import docx2txt
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(b); tmp.flush()
            return docx2txt.process(tmp.name) or ""
    except Exception as e:
        logger.warning("docx2txt not available: %s", e)
        try:
            return b.decode("utf-8", errors="ignore")
        except Exception:
            return ""

def simple_tokenize(text: str):
    return [t for t in text.split() if t.strip()]

