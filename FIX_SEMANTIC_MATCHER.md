# Fix: Missing `get_embed_fn_if_available()` Function in semantic_matcher

## Problem
The `agents.py` module was calling `semantic_matcher.get_embed_fn_if_available()` at two locations:
- Line 134 in `MatcherAgent.match()`
- Line 191 in `ScoringAgent.score()`

However, this function didn't exist in the `semantic_matcher` module, causing:
```
AttributeError: module 'backend.tools.semantic_matcher' has no attribute 'get_embed_fn_if_available'
```

## Solution
Added the `get_embed_fn_if_available()` function to `backend/tools/semantic_matcher.py` (lines 58-73).

### Function Behavior
```python
def get_embed_fn_if_available() -> Optional[Callable]:
    """
    Returns an embedding function if sentence-transformers is available, else None.
    If returned, the function accepts List[str] and returns List[List[float]] embeddings.
    """
```

**Returns:**
- A callable that wraps the sentence-transformers `SentenceTransformer` model if available
- `None` if sentence-transformers is not installed or fails to initialize
- The callable takes a list of strings and returns embeddings as a list of float lists

**Behavior:**
1. Tries to load sentence-transformers library
2. If available, loads the "all-MiniLM-L6-v2" model
3. Returns a wrapper function that can be used as `embed_fn` parameter
4. Logs warnings if initialization fails
5. Returns `None` if the library is unavailable

### Integration Points
The function is now called by:
- `MatcherAgent.match()` → Uses embedding function for semantic similarity matching
- `ScoringAgent.score()` → Uses embedding function for ATS scoring

Both agents pass the embedding function (or None) to downstream tools that handle the fallback gracefully.

## Files Modified
- `backend/tools/semantic_matcher.py` - Added `get_embed_fn_if_available()` function

## Verification
✅ Function exists and is callable
✅ Returns correct types (Callable or None)
✅ Properly handles missing dependencies with graceful fallback
✅ Agents module can now initialize without AttributeError

## Related Errors (Still Present)
These are not code issues but environmental/configuration:

1. **OpenAI API Key Invalid (401 Error)**
   - User needs to set valid `OPENAI_API_KEY` in `.env`
   - System gracefully falls back to local text generation models

2. **spaCy Model Not Installed**
   - Run: `python setup_models.py`
   - Or: `python -m spacy download en_core_web_sm`
   - System gracefully falls back to blank model with reduced features

3. **"Unsupported file type: None" (Warning)**
   - This is just a warning when uploaded files don't have content-type header
   - Code continues and infers file type from filename extension
   - Not a critical issue