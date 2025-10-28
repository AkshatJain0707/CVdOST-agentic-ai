# backend/utils/pdf_extractor.py
"""
Lightweight PDF extraction helper using PyPDF2 if available,
fallback to returning bytes decode attempt.
"""
import io, logging
logger = logging.getLogger("resumate.pdf")

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n\n".join(pages)
    except Exception as e:
        logger.warning("PyPDF2 not available or failed: %s", e)
        try:
            return pdf_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""
