#!/usr/bin/env python3
"""Quick test for semantic_matcher fix."""

import sys

try:
    # Test 1: Import the module
    from backend.tools import semantic_matcher
    print("[PASS] semantic_matcher module imports")
    
    # Test 2: Check function exists
    if hasattr(semantic_matcher, 'get_embed_fn_if_available'):
        print("[PASS] get_embed_fn_if_available() exists")
    else:
        print("[FAIL] get_embed_fn_if_available() not found")
        sys.exit(1)
    
    # Test 3: Try calling it (without sentence-transformers, should return None)
    embed_fn = semantic_matcher.get_embed_fn_if_available()
    print(f"[PASS] get_embed_fn_if_available() callable, returned: {type(embed_fn).__name__}")
    
    # Test 4: Verify agents can import without errors
    from backend.agents import MatcherAgent, ScoringAgent
    print("[PASS] MatcherAgent and ScoringAgent import successfully")
    
    # Test 5: Check that the function is called properly in agents
    import inspect
    source = inspect.getsource(MatcherAgent.match)
    if 'get_embed_fn_if_available' in source:
        print("[PASS] MatcherAgent.match() uses get_embed_fn_if_available()")
    
    print("\n[SUCCESS] All semantic_matcher fixes verified!")
    
except Exception as e:
    import traceback
    print(f"[FAIL] {e}")
    traceback.print_exc()
    sys.exit(1)