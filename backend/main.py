# backend/main.py
"""
FastAPI entrypoint for Resumate-Agentic-AI.
Implements a single robust /analyze route for resume analysis.
"""

import os
import tempfile
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.orchestration import OrchestrationEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Resumate Agentic Backend", version="1.0")

# CORS - allow all for dev; pin to your frontend origin in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported resume file types
SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain"
}

# Orchestrator instance (lightweight)
engine = OrchestrationEngine(results_dir=os.getenv("RESULTS_DIR", "data/results"))


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    target_role: str = Form(default=None),
):
    """
    Analyze resume against job description.
    
    Args:
        resume_file: Resume file (PDF, DOCX, or TXT)
        job_description: Job description text
        target_role: Optional target role for optimization
    
    Returns:
        Analysis result with scores, matches, and optimizations
    """
    # Validate inputs
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    if resume_file.content_type not in SUPPORTED_CONTENT_TYPES:
        logger.warning("Unsupported file type: %s", resume_file.content_type)
    
    # Save file to temp location with proper cleanup
    tmp_file = None
    try:
        file_ext = os.path.splitext(resume_file.filename)[1] or ".bin"
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        
        # Efficiently copy file content
        shutil.copyfileobj(resume_file.file, tmp_file)
        tmp_file.flush()
        tmp_file.close()
        
        # Run orchestration pipeline
        result = await engine.run(
            tmp_file.name, 
            job_description.strip(), 
            target_role.strip() if target_role else None
        )
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analysis failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal processing error")
    
    finally:
        # Clean up temp file
        if tmp_file:
            try:
                os.unlink(tmp_file.name)
            except Exception as e:
                logger.debug("Failed to clean up temp file: %s", e)
