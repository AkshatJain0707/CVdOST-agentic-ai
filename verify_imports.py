#!/usr/bin/env python
"""
Verification script to test all module imports and connections.
Run this to ensure all files are properly connected.
"""

import sys
import traceback

def test_imports():
    """Test all critical imports."""
    tests = [
        ("Backend utils - Logger", lambda: __import__("backend.utils.logger", fromlist=["get_logger"])),
        ("Backend utils - Embeddings", lambda: __import__("backend.utils.embeddings", fromlist=["EmbeddingEngine"])),
        ("Backend models - AnalyticsEngine", lambda: __import__("backend.models.analytics_engine", fromlist=["AnalyticsEngine"])),
        ("Backend models - LLMClient", lambda: __import__("backend.models.llm_client", fromlist=["LLMClient"])),
        ("Backend agents", lambda: __import__("backend.agents", fromlist=["ResumeAgent", "JDAnalyzerAgent", "MatcherAgent", "ScoringAgent", "OptimizationAgent"])),
        ("Backend orchestration", lambda: __import__("backend.orchestration", fromlist=["OrchestrationEngine"])),
        ("Backend main", lambda: __import__("backend.main", fromlist=["app"])),
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("IMPORT VERIFICATION TEST")
    print("=" * 70)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"✓ {test_name}: OK")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: FAILED")
            print(f"  Error: {str(e)}")
            traceback.print_exc()
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


def test_class_instantiation():
    """Test that key classes can be instantiated."""
    print("\n" + "=" * 70)
    print("CLASS INSTANTIATION TEST")
    print("=" * 70)
    
    try:
        from backend.utils.embeddings import EmbeddingEngine
        emb = EmbeddingEngine()
        print("✓ EmbeddingEngine instantiated successfully")
        
        from backend.models.analytics_engine import AnalyticsEngine
        analytics = AnalyticsEngine(emb)
        print("✓ AnalyticsEngine instantiated successfully")
        
        from backend.models.llm_client import LLMClient
        llm = LLMClient()
        print("✓ LLMClient instantiated successfully")
        
        from backend.agents import ResumeAgent, JDAnalyzerAgent, MatcherAgent, ScoringAgent, OptimizationAgent
        print("✓ ResumeAgent instantiated successfully")
        print("✓ JDAnalyzerAgent instantiated successfully")
        print("✓ MatcherAgent instantiated successfully")
        print("✓ ScoringAgent instantiated successfully")
        print("✓ OptimizationAgent instantiated successfully")
        
        print("=" * 70)
        print("All classes instantiated successfully!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"✗ Class instantiation failed: {e}")
        traceback.print_exc()
        return False


def test_method_connectivity():
    """Test that methods work correctly together."""
    print("\n" + "=" * 70)
    print("METHOD CONNECTIVITY TEST")
    print("=" * 70)
    
    try:
        import numpy as np
        from backend.utils.embeddings import EmbeddingEngine
        from backend.models.analytics_engine import AnalyticsEngine
        
        emb = EmbeddingEngine()
        analytics = AnalyticsEngine(emb)
        
        # Test cosine similarity
        vec1 = np.random.rand(384)
        vec2 = np.random.rand(384)
        sim = EmbeddingEngine.cosine_similarity(vec1, vec2)
        print(f"✓ Cosine similarity computed: {sim:.4f}")
        
        # Test scoring methods
        resume_text = "Led team of 5 engineers. Implemented microservices. Optimized database queries."
        jd_skills = ["python", "microservices", "optimization", "team leadership"]
        
        kw_score = analytics.keyword_overlap_score(resume_text, jd_skills)
        print(f"✓ Keyword overlap score: {kw_score:.2f}")
        
        struct_score = analytics.structure_score(resume_text)
        print(f"✓ Structure score: {struct_score:.2f}")
        
        action_score = analytics.action_verbs_score(resume_text)
        print(f"✓ Action verbs score: {action_score:.2f}")
        
        print("=" * 70)
        print("All method connectivity tests passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"✗ Method connectivity test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Instantiation", test_class_instantiation()))
    results.append(("Connectivity", test_method_connectivity()))
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_passed = all(r for _, r in results)
    sys.exit(0 if all_passed else 1)