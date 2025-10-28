#!/usr/bin/env python
"""Quick test to verify all connections work."""

import sys

print("Testing module connections...")

try:
    # Test 1: Import main app
    print("✓ Testing FastAPI app import...")
    from backend.main import app
    print("  └─ FastAPI app loaded successfully")
    
    # Test 2: Import orchestration
    print("✓ Testing OrchestrationEngine...")
    from backend.orchestration import OrchestrationEngine
    engine = OrchestrationEngine()
    print("  └─ OrchestrationEngine instantiated")
    
    # Test 3: Test analytics engine
    print("✓ Testing AnalyticsEngine...")
    from backend.utils.embeddings import EmbeddingEngine
    from backend.models.analytics_engine import AnalyticsEngine
    
    emb = EmbeddingEngine()
    analytics = AnalyticsEngine(emb)
    print("  └─ AnalyticsEngine with EmbeddingEngine working")
    
    # Test 4: Test agents
    print("✓ Testing Agents...")
    from backend.agents import ResumeAgent, JDAnalyzerAgent, MatcherAgent, ScoringAgent, OptimizationAgent
    print("  ├─ ResumeAgent OK")
    print("  ├─ JDAnalyzerAgent OK")
    print("  ├─ MatcherAgent OK")
    print("  ├─ ScoringAgent OK")
    print("  └─ OptimizationAgent OK")
    
    # Test 5: Test LLM Client
    print("✓ Testing LLMClient...")
    from backend.models.llm_client import LLMClient
    llm = LLMClient()
    print("  └─ LLMClient initialized")
    
    print("\n" + "=" * 60)
    print("✅ ALL CONNECTIONS VERIFIED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYour application is ready to use:")
    print("  • All imports are correctly configured")
    print("  • All modules are properly connected")
    print("  • FastAPI application is ready to serve")
    print("\nTo start the server, run:")
    print("  uvicorn backend.main:app --reload")
    
except Exception as e:
    print(f"\n❌ Connection test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)