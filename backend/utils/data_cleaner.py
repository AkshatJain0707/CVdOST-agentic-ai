"""
Data Cleaner
------------
Responsible for normalization, stopword filtering, and text de-noising.
Ensures consistency before embedding or ATS scoring.
"""

import re
import unicodedata

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^A-Za-z0-9.,;:\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()
