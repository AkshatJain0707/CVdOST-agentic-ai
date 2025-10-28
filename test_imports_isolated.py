#!/usr/bin/env python
"""Test imports with detailed diagnostics."""

import sys
import time

print("Starting import tests...\n")

# Test 1: Logger
try:
    print("1. Testing logger import...")
    start = time.time()
    from backend.utils.logger import get_logger
    elapsed = time.time() - start
    print(f"   ✓ Logger: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ Logger failed: {e}\n")
    sys.exit(1)

# Test 2: OpenAI Wrapper (this may hang)
try:
    print("2. Testing openai_wrapper import...")
    start = time.time()
    from backend.utils.openai_wrapper import LLMWrapper
    elapsed = time.time() - start
    print(f"   ✓ LLMWrapper: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ LLMWrapper failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: LLM Client
try:
    print("3. Testing llm_client import...")
    start = time.time()
    from backend.models.llm_client import LLMClient
    elapsed = time.time() - start
    print(f"   ✓ LLMClient: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ LLMClient failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Embeddings (this might hang with model download)
try:
    print("4. Testing embeddings import...")
    start = time.time()
    from backend.utils.embeddings import EmbeddingEngine
    elapsed = time.time() - start
    print(f"   ✓ EmbeddingEngine: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ EmbeddingEngine failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Analytics Engine
try:
    print("5. Testing analytics_engine import...")
    start = time.time()
    from backend.models.analytics_engine import AnalyticsEngine
    elapsed = time.time() - start
    print(f"   ✓ AnalyticsEngine: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ AnalyticsEngine failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Resume Parser
try:
    print("6. Testing resume_parser import...")
    start = time.time()
    from backend.tools import resume_parser
    elapsed = time.time() - start
    print(f"   ✓ resume_parser: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ resume_parser failed: {e}\n")
    sys.exit(1)

# Test 7: Agents
try:
    print("7. Testing agents import...")
    start = time.time()
    from backend.agents import ResumeAgent
    elapsed = time.time() - start
    print(f"   ✓ agents: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ agents failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Orchestration
try:
    print("8. Testing orchestration import...")
    start = time.time()
    from backend.orchestration import OrchestrationEngine
    elapsed = time.time() - start
    print(f"   ✓ orchestration: {elapsed:.3f}s\n")
except Exception as e:
    print(f"   ✗ orchestration failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print("✅ ALL IMPORTS VERIFIED SUCCESSFULLY!")
print("=" * 60)