#!/usr/bin/env python3
"""Test that the semantic_matcher fix works in agents."""

try:
    from backend.tools import semantic_matcher, skill_comparator
    from backend.agents import MatcherAgent, ScoringAgent
    
    # Test MatcherAgent
    matcher = MatcherAgent()
    resume_data = {
        "raw_text": "Python developer with 5 years experience",
        "clean_text": "Python developer with 5 years experience",
        "skills": {"skills": ["Python"], "tools": []}
    }
    jd_text = "Looking for Python developer"
    
    result = matcher.match(resume_data, jd_text)
    print("[OK] MatcherAgent.match() works")
    print(f"[OK] Result keys: {list(result.keys())}")
    
    # Test ScoringAgent  
    scorer = ScoringAgent()
    jd_data = {"requirements": {}, "parsed_skills": []}
    score = scorer.score(resume_data, jd_data, result)
    print("[OK] ScoringAgent.score() works")
    print("[SUCCESS] All semantic_matcher fixes are working!")
    
except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    traceback.print_exc()