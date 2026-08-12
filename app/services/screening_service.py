from pathlib import Path
from typing import List
from app.models.schemas import ResumeDocument
from app.parsers import parse_document

def parse_resumes(resume_paths: List[Path]) -> List[ResumeDocument]:
    """
    Parses a list of resume paths and returns a list of ResumeDocument models.
    """
    documents = []
    for path in resume_paths:
        doc = parse_document(path)
        documents.append(doc)
    return documents
