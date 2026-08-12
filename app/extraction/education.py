import re
from typing import List, Dict, Any

EDUCATION_PATTERNS = {
    "B.E": re.compile(r'\bB\.?\s*E\.?\b', re.IGNORECASE),
    "B.Tech": re.compile(r'\bB\.?\s*Tech\b', re.IGNORECASE),
    "M.Tech": re.compile(r'\bM\.?\s*Tech\b', re.IGNORECASE),
    "MCA": re.compile(r'\bMCA\b', re.IGNORECASE),
    "BCA": re.compile(r'\bBCA\b', re.IGNORECASE),
    "Bachelor": re.compile(r'\bBachelors?\b|\bB\.?\s*S\.?\b|\bB\.?\s*A\.?\b', re.IGNORECASE),
    "Master": re.compile(r'\bMasters?\b|\bM\.?\s*S\.?\b|\bM\.?\s*B\.?\s*A\.?\b', re.IGNORECASE),
    "PhD": re.compile(r'\bPh\.?\s*D\.?\b|\bDoctorate\b', re.IGNORECASE)
}

def extract_education_requirements(text: str) -> List[str]:
    """
    Scans the Job Description text and returns a list of matched education degree requirements.
    """
    matched = []
    for degree, regex in EDUCATION_PATTERNS.items():
        if regex.search(text):
            matched.append(degree)
    return matched

def extract_education(text: str) -> List[Dict[str, Any]]:
    """
    Extracts education details from candidate resumes (compatibility placeholder).
    """
    degrees = extract_education_requirements(text)
    if degrees:
        return [{"degree": d, "school": "Unknown School", "year": "Unknown Year"} for d in degrees]
    return [{"degree": "Bachelor", "school": "Unknown School", "year": "Unknown Year"}]
