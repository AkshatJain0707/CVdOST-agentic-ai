#!/usr/bin/env python3
"""
Setup script to download required language models for the application.
Run this once after installing dependencies.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SetupModels")

def setup_spacy_model():
    """Download spaCy English model"""
    try:
        import spacy
        logger.info("Attempting to download spaCy model 'en_core_web_sm'...")
        # Try to load it first
        try:
            spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model already installed")
            return True
        except OSError:
            # Download if not found
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✅ spaCy model downloaded successfully")
                return True
            else:
                logger.error(f"Failed to download spaCy model: {result.stderr}")
                return False
    except Exception as e:
        logger.error(f"Error setting up spaCy model: {e}")
        return False


def setup_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        logger.info("Downloading NLTK data...")
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        logger.info("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up NLTK data: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Setting up language models and data...")
    logger.info("=" * 60)
    
    spacy_ok = setup_spacy_model()
    nltk_ok = setup_nltk_data()
    
    logger.info("=" * 60)
    if spacy_ok and nltk_ok:
        logger.info("✅ Setup completed successfully!")
        sys.exit(0)
    else:
        logger.warning("⚠️  Some models failed to download. The app will use fallbacks.")
        sys.exit(1)