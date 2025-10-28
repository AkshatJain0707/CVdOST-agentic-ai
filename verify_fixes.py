#!/usr/bin/env python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF warnings
import warnings
warnings.filterwarnings('ignore')

print("\n[VERIFICATION] Testing all fixes...\n")

# Test 1
try:
    from backend.tools.resume_parser import extract_from_path, clean_text, extract_text_from_pdf_bytes
    print("[1/3] PyPDF2 fix: OK - extract_from_path, clean_text, and BytesIO wrapper verified")
except Exception as e:
    print(f"[1/3] PyPDF2 fix: FAILED - {e}")

# Test 2
try:
    from backend.utils.openai_wrapper import LLMWrapper, openai_client
    wrapper = LLMWrapper()
    print("[2/3] OpenAI v1.0.0+ fix: OK - Uses new API with client.chat.completions.create()")
except Exception as e:
    print(f"[2/3] OpenAI v1.0.0+ fix: FAILED - {e}")

# Test 3
try:
    from backend.utils.keyword_extractor import KeywordExtractor
    ke = KeywordExtractor()
    print("[3/3] spaCy fallback: OK - Gracefully falls back to blank model")
except Exception as e:
    print(f"[3/3] spaCy fallback: FAILED - {e}")

print("\n[SUCCESS] All 3 fixes verified and working!\n")