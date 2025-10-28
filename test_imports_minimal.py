#!/usr/bin/env python
"""Minimal import test without heavy model downloads."""

import sys

def test_imports():
    """Test all critical imports without loading models."""
    errors = []
    
    # Test 1: Logger
    try:
        from backend.utils.logger import get_logger
        logger = get_logger("test")
        print("✓ Logger import OK")
    except Exception as e:
        errors.append(f"Logger: {e}")
        print(f"✗ Logger failed: {e}")
    
    # Test 2: OpenAI Wrapper
    try:
        from backend.utils.openai_wrapper import LLMWrapper
        print("✓ LLMWrapper import OK")
    except Exception as e:
        errors.append(f"LLMWrapper: {e}")
        print(f"✗ LLMWrapper failed: {e}")
    
    # Test 3: LLM Client
    try:
        from backend.models.llm_client import LLMClient
        print("✓ LLMClient import OK")
    except Exception as e:
        errors.append(f"LLMClient: {e}")
        print(f"✗ LLMClient failed: {e}")
    
    # Test 4: Tool imports
    try:
        from backend.tools import resume_parser
        from backend.tools import skill_extractor
        from backend.tools import jd_analyzer
        from backend.tools import semantic_matcher
        from backend.tools import skill_comparator
        from backend.tools import ats_scorer
        from backend.tools import resume_optimizer
        print("✓ All tool modules imported OK")
    except Exception as e:
        errors.append(f"Tools: {e}")
        print(f"✗ Tool imports failed: {e}")
    
    # Test 5: Agent imports
    try:
        from backend.agents import (
            ResumeAgent, JDAnalyzerAgent, MatcherAgent, 
            ScoringAgent, OptimizationAgent
        )
        print("✓ All agents imported OK")
    except Exception as e:
        errors.append(f"Agents: {e}")
        print(f"✗ Agents failed: {e}")
    
    # Test 6: Orchestration
    try:
        from backend.orchestration import OrchestrationEngine
        print("✓ OrchestrationEngine import OK")
    except Exception as e:
        errors.append(f"OrchestrationEngine: {e}")
        print(f"✗ OrchestrationEngine failed: {e}")
    
    # Test 7: Main app (without instantiating)
    try:
        # Don't fully import app to avoid model loading
        # Just check syntax/structure
        with open("c:\\Users\\asus\\resumate-agentic-ai\\backend\\main.py", "r") as f:
            compile(f.read(), "main.py", "exec")
        print("✓ main.py syntax OK")
    except Exception as e:
        errors.append(f"main.py: {e}")
        print(f"✗ main.py failed: {e}")
    
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ {len(errors)} import errors found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("✅ ALL IMPORTS VERIFIED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYour application structure is correct:")
        print("  • All modules properly named")
        print("  • All imports resolve correctly")
        print("  • Package structure is valid")
        print("\nTo start the server, run:")
        print("  uvicorn backend.main:app --reload")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)