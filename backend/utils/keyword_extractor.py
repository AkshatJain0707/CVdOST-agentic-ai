"""
Keyword Extractor
-----------------
Extracts and classifies domain-relevant skills from resumes and JDs
using hybrid linguistic + semantic filters.
"""

import re
import logging
import spacy
import nltk
from nltk.corpus import stopwords

logger = logging.getLogger("KeywordExtractor")

nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

# Try to load spaCy model, fall back to blank if not available
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully")
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Using blank model. Run: python -m spacy download en_core_web_sm")
    nlp = spacy.blank("en")
except Exception as e:
    logger.warning("Failed to load spaCy model: %s. Using blank model.", e)
    nlp = spacy.blank("en")

TECH_KEYWORDS = [
    "python", "sql", "r", "machine learning", "tensorflow", "pandas",
    "tableau", "deep learning", "chemistry", "formulation", "qc", "hplc"
]

class KeywordExtractor:
    def extract_skills(self, text: str):
        doc = nlp(text.lower())
        tokens = [t.text for t in doc if t.is_alpha and t.text not in stop_words]
        
        # Try to extract noun chunks, fall back to empty list if not available
        noun_chunks = []
        try:
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        except Exception as e:
            logger.debug("Could not extract noun_chunks: %s. Using tokens only.", e)
        
        keywords = set(tokens + noun_chunks)
        return [kw for kw in keywords if kw in TECH_KEYWORDS or re.search(r"[A-Za-z]+ing$", kw)]
