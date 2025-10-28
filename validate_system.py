#!/usr/bin/env python
"""
System validation script - tests core functionality without model downloads.
"""

import sys
import json
import tempfile
import os

def test_analytics_engine():
    """Test AnalyticsEngine scoring functionality."""
    print("\n▶ Testing AnalyticsEngine...")
    try:
        from backend.utils.embeddings import EmbeddingEngine
        from backend.models.analytics_engine import AnalyticsEngine
        import numpy as np
        
        # Initialize
        emb = EmbeddingEngine()
        analytics = AnalyticsEngine(emb)
        
        # Test scoring
        resume_text = "Experienced Python developer with 5 years in web development"
        jd_skills = ["python", "web development", "database", "api"]
        
        # Test keyword overlap
        score = analytics.keyword_overlap_score(resume_text, jd_skills)
        assert 0 <= score <= 100, f"Keyword score out of range: {score}"
        
        # Test structure scoring
        struct_score = analytics.structure_score(resume_text)
        assert 0 <= struct_score <= 100, f"Structure score out of range: {struct_score}"
        
        # Test action verbs
        action_score = analytics.action_verbs_score(resume_text)
        assert 0 <= action_score <= 100, f"Action score out of range: {action_score}"
        
        # Test composite ATS score
        result = analytics.ats_score(
            resume_text=resume_text,
            jd_text="Looking for Python developer",
            semantic_score=75.5,
            keyword_overlap=score
        )
        
        assert "score" in result
        assert "components" in result
        assert "interpretation" in result
        assert 0 <= result["score"] <= 100
        
        print(f"  ✓ AnalyticsEngine: {result['score']:.1f} (Interpretation: {result['interpretation']})")
        return True
    except Exception as e:
        print(f"  ✗ AnalyticsEngine failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_client():
    """Test LLMClient chat functionality."""
    print("\n▶ Testing LLMClient...")
    try:
        from backend.models.llm_client import LLMClient
        
        llm = LLMClient()
        response = llm.chat("Say 'Connected' in one word")
        
        assert response is not None
        assert len(response) > 0
        
        print(f"  ✓ LLMClient responded (fallback mode OK)")
        return True
    except Exception as e:
        print(f"  ✗ LLMClient failed: {e}")
        return False

def test_resume_parser():
    """Test resume parser with sample text."""
    print("\n▶ Testing ResumeParser...")
    try:
        from backend.tools import resume_parser
        
        # Test cleaning
        sample_text = "John Doe\nEmail: john@example.com\n• Experienced Python developer"
        clean = resume_parser.clean_text(sample_text)
        
        assert clean is not None
        assert len(clean) > 0
        assert "john" in clean.lower()  # Should preserve content
        
        print(f"  ✓ ResumeParser: Text cleaning works")
        return True
    except Exception as e:
        print(f"  ✗ ResumeParser failed: {e}")
        return False

def test_skill_extractor():
    """Test skill extraction."""
    print("\n▶ Testing SkillExtractor...")
    try:
        from backend.tools import skill_extractor
        
        text = "Proficient in Python, Java, and SQL. Experience with AWS and Docker."
        result = skill_extractor.extract_skills(text)
        
        assert isinstance(result, dict)
        assert "skills" in result or "tools" in result
        
        print(f"  ✓ SkillExtractor: Found skills/tools in text")
        return True
    except Exception as e:
        print(f"  ✗ SkillExtractor failed: {e}")
        return False

def test_agents():
    """Test agent instantiation and methods."""
    print("\n▶ Testing Agents...")
    try:
        from backend.agents import (
            ResumeAgent, JDAnalyzerAgent, MatcherAgent, 
            ScoringAgent, OptimizationAgent
        )
        
        agents = [
            ("ResumeAgent", ResumeAgent()),
            ("JDAnalyzerAgent", JDAnalyzerAgent()),
            ("MatcherAgent", MatcherAgent()),
            ("ScoringAgent", ScoringAgent()),
            ("OptimizationAgent", OptimizationAgent()),
        ]
        
        for name, agent in agents:
            assert agent is not None
            assert hasattr(agent, '__class__')
        
        print(f"  ✓ All {len(agents)} agents instantiated successfully")
        return True
    except Exception as e:
        print(f"  ✗ Agents failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestration():
    """Test orchestration engine instantiation."""
    print("\n▶ Testing OrchestrationEngine...")
    try:
        from backend.orchestration import OrchestrationEngine
        
        engine = OrchestrationEngine()
        assert engine.resume_agent is not None
        assert engine.jd_agent is not None
        assert engine.matcher_agent is not None
        assert engine.scoring_agent is not None
        assert engine.optimizer_agent is not None
        
        print(f"  ✓ OrchestrationEngine: All agents ready")
        return True
    except Exception as e:
        print(f"  ✗ OrchestrationEngine failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("SYSTEM VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        ("Analytics Engine", test_analytics_engine),
        ("LLM Client", test_llm_client),
        ("Resume Parser", test_resume_parser),
        ("Skill Extractor", test_skill_extractor),
        ("Agents", test_agents),
        ("Orchestration", test_orchestration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"✗ {name} test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL {total} TESTS PASSED!")
        print("=" * 60)
        print("\nSystem Status: ✅ FULLY OPERATIONAL")
        print("\nYour application is ready to use!")
        print("\nTo start the server:")
        print("  uvicorn backend.main:app --reload")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed, {total - passed} failed")
        print("=" * 60)
        print("\nPlease review failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())