# tools/resume_parser.py
import os
import io
import tempfile
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger("ResumeParser")
logger.setLevel(logging.INFO)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        raise RuntimeError("PyPDF2 is required for PDF extraction. pip install PyPDF2")
    # Wrap bytes in BytesIO to provide file-like interface that PdfReader expects
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for p in reader.pages:
        try:
            txt = p.extract_text() or ""
        except Exception:
            txt = ""
        pages.append(txt)
    return "\n\n".join(pages)


def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    try:
        import docx2txt
    except Exception:
        raise RuntimeError("docx2txt is required for docx extraction. pip install docx2txt")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as nt:
        nt.write(docx_bytes)
        nt.flush()
        text = docx2txt.process(nt.name) or ""
    try:
        os.unlink(nt.name)
    except Exception:
        pass
    return text


def simple_section_parse(text: str) -> Dict[str, str]:
    """
    Heuristic: split by headers commonly found in resumes
    Returns mapping header -> text (lowercase headers)
    """
    import re
    headers = ["education", "experience", "work experience", "skills", "projects", "summary", "certifications", "publications"]
    sections = {}
    lower = text.lower()
    for h in headers:
        idx = lower.find(h)
        if idx != -1:
            # try to get until next header
            end = len(text)
            for h2 in headers:
                if h2 == h:
                    continue
                pos = lower.find(h2, idx + 1)
                if pos != -1:
                    end = min(end, pos)
            sections[h] = text[idx:end].strip()
    # default fallback whole text
    if not sections:
        sections["full_text"] = text
    return sections


def extract_from_uploaded(uploaded_file) -> Tuple[str, Dict[str, str]]:
    """
    uploaded_file is a Streamlit-like UploadedFile or FastAPI UploadFile.file object that exposes .read()
    Returns (text, sections)
    """
    try:
        content = uploaded_file.read()
    except Exception:
        # if it's a bytes-like already
        content = uploaded_file

    name = getattr(uploaded_file, "name", "") or ""
    name = name.lower()
    if name.endswith(".pdf"):
        text = extract_text_from_pdf_bytes(content)
    elif name.endswith(".docx"):
        text = extract_text_from_docx_bytes(content)
    elif name.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
    else:
        # try pdf then docx fallback
        try:
            text = extract_text_from_pdf_bytes(content)
        except Exception:
            try:
                text = extract_text_from_docx_bytes(content)
            except Exception:
                text = content.decode("utf-8", errors="ignore")
    sections = simple_section_parse(text)
    return text, sections


def extract_from_path(file_path: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract text and sections from a file on disk.
    Supports .pdf, .docx, and .txt files.
    
    Args:
        file_path: Path to the resume file
    
    Returns:
        Tuple of (text, sections)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    file_path_lower = file_path.lower()
    if file_path_lower.endswith(".pdf"):
        text = extract_text_from_pdf_bytes(content)
    elif file_path_lower.endswith(".docx"):
        text = extract_text_from_docx_bytes(content)
    elif file_path_lower.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
    else:
        # try pdf then docx fallback
        try:
            text = extract_text_from_pdf_bytes(content)
        except Exception:
            try:
                text = extract_text_from_docx_bytes(content)
            except Exception:
                text = content.decode("utf-8", errors="ignore")
    
    sections = simple_section_parse(text)
    return text, sections


def clean_text(text: str) -> str:
    """
    Clean and normalize resume text.
    - Removes extra whitespace
    - Normalizes line breaks
    - Removes special characters that aren't relevant
    
    Args:
        text: Raw extracted text
    
    Returns:
        Cleaned text
    """
    import re
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove extra spaces around punctuation
    text = re.sub(r'\s+([,.])', r'\1', text)
    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()
