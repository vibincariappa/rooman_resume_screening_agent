import os
import json
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.screening_service import screen_candidates
from app.models.schemas import BatchScreeningResult

# Max file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

app = FastAPI(
    title="Resume Screening AI Agent API",
    description="Deterministic NLP & LLM Resume Screening backend service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for the active session
_SESSION_CACHE: Optional[BatchScreeningResult] = None

class ResumeInput(BaseModel):
    filename: str
    content: str = Field(description="Raw text content of the resume.")

class ScreenJSONRequest(BaseModel):
    job_description: str
    resumes: List[ResumeInput]

def get_active_results() -> Optional[BatchScreeningResult]:
    """
    Tries to retrieve active session results or load from output JSON file.
    """
    global _SESSION_CACHE
    if _SESSION_CACHE:
        return _SESSION_CACHE
        
    persisted_path = Path("data/output/ranked_candidates.json")
    if persisted_path.exists():
        try:
            with open(persisted_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _SESSION_CACHE = BatchScreeningResult(**data)
                return _SESSION_CACHE
        except Exception:
            pass
    return None

def validate_file_metadata(filename: str, size: int):
    """
    Validates file extension and size constraints.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {filename}. Supported formats are: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {filename} is empty."
        )
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {filename} exceeds maximum size limit of 5MB."
        )

@app.get("/health")
def health_check():
    """
    Health check endpoint returning system status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Resume Screening AI Agent"
    }

@app.post("/api/screen", response_model=BatchScreeningResult)
def screen_json_endpoint(request: ScreenJSONRequest):
    """
    Screen resumes provided directly in JSON body format.
    """
    global _SESSION_CACHE
    
    if not request.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job Description cannot be empty."
        )
    if not request.resumes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one candidate resume must be provided."
        )
        
    temp_dir = Path("data/temp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    req_dir = temp_dir / str(time.time_ns())
    req_dir.mkdir(parents=True)
    
    try:
        # Write Job Description
        jd_file = req_dir / "jd.txt"
        with open(jd_file, "w", encoding="utf-8") as jdf:
            jdf.write(request.job_description)
            
        # Write Resumes
        resumes_dir = req_dir / "resumes"
        resumes_dir.mkdir()
        
        for resume in request.resumes:
            if not resume.filename.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resume filename cannot be empty."
                )
            ext = Path(resume.filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported format: {resume.filename}."
                )
            if not resume.content.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Content for resume {resume.filename} is empty."
                )
                
            res_file = resumes_dir / resume.filename
            with open(res_file, "w", encoding="utf-8") as resf:
                resf.write(resume.content)
                
        # Execute Pipeline
        result = screen_candidates(
            job_description_path=str(jd_file),
            resumes_directory=str(resumes_dir),
            output_directory="data/output"
        )
        _SESSION_CACHE = result
        return result
    finally:
        shutil.rmtree(req_dir, ignore_errors=True)

@app.post("/api/screen/upload", response_model=BatchScreeningResult)
async def screen_upload_endpoint(
    job_description: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
    resumes: List[UploadFile] = File(...)
):
    """
    Screen candidates using multipart form-data upload.
    Accepts job_description text or file, and multiple resume files.
    """
    global _SESSION_CACHE
    
    # 1. Validate JD presence
    jd_content = ""
    if job_description and job_description.strip():
        jd_content = job_description
    elif job_description_file:
        content_bytes = await job_description_file.read()
        jd_content = content_bytes.decode("utf-8", errors="ignore")
        
    if not jd_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job Description is missing (provide text form field or file upload)."
        )
        
    # 2. Validate Resumes list
    if not resumes or len(resumes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidate resumes uploaded."
        )
        
    temp_dir = Path("data/temp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    req_dir = temp_dir / str(time.time_ns())
    req_dir.mkdir(parents=True)
    
    try:
        # Write Job Description
        jd_file = req_dir / "jd.txt"
        with open(jd_file, "w", encoding="utf-8") as jdf:
            jdf.write(jd_content)
            
        # Validate and Write Resumes
        resumes_dir = req_dir / "resumes"
        resumes_dir.mkdir()
        
        for upload in resumes:
            # We read metadata first, then contents
            # Reading small chunks to check size or read all
            file_bytes = await upload.read()
            validate_file_metadata(upload.filename, len(file_bytes))
            
            res_file = resumes_dir / upload.filename
            with open(res_file, "wb") as rf:
                rf.write(file_bytes)
                
        # Execute pipeline
        result = screen_candidates(
            job_description_path=str(jd_file),
            resumes_directory=str(resumes_dir),
            output_directory="data/output"
        )
        _SESSION_CACHE = result
        return result
    finally:
        shutil.rmtree(req_dir, ignore_errors=True)

@app.get("/api/results", response_model=BatchScreeningResult)
def get_results():
    """
    Retrieves the latest ranked candidates screening results.
    """
    results = get_active_results()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No screening results found. Please run a screening session first."
        )
    return results

@app.get("/api/results/{candidate_id}")
def get_candidate_details(candidate_id: str):
    """
    Retrieves detailed scores and reasoning for a specific candidate ID.
    """
    results = get_active_results()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No screening results found. Please run a screening session first."
        )
        
    for cand in results.ranked_candidates:
        if cand["candidate_id"] == candidate_id:
            return cand
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Candidate with ID '{candidate_id}' not found."
    )
