from fastapi import FastAPI, HTTPException
from typing import List
from app.models.schemas import ResumeDocument
from app.services.screening_service import parse_resumes
from pathlib import Path

app = FastAPI(title="Resume Screening AI Agent API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Resume Screening AI Agent API is running."}

@app.post("/parse", response_model=List[ResumeDocument])
def parse_endpoint():
    """
    Parses resumes in the data/resumes directory.
    Creates a dummy text resume if the directory is empty.
    """
    resumes_dir = Path("data/resumes")
    resumes_dir.mkdir(parents=True, exist_ok=True)
    
    allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}
    resume_paths = [
        p for p in resumes_dir.iterdir() 
        if p.is_file() and p.suffix.lower() in allowed_suffixes
    ]
    
    if not resume_paths:
        dummy_path = resumes_dir / "candidate_01.txt"
        with open(dummy_path, "w", encoding="utf-8") as f:
            f.write("Python Software Engineer\nExperience: 3 years\nSkills: FastAPI, SQL")
        resume_paths = [dummy_path]
        
    try:
        return parse_resumes(resume_paths)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
