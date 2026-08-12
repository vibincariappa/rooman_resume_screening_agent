import re
from typing import List, Dict, Any

def extract_minimum_experience_years(text: str) -> float:
    """
    Extracts the minimum experience years requested in the Job Description.
    Looks for phrases such as "3 years experience", "3+ years", "minimum 2 years".
    """
    min_patterns = [
        re.compile(r'\b(?:minimum|min|at least|required)\s*of?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:year|yr)s?', re.IGNORECASE),
        re.compile(r'\b(\d+(?:\.\d+)?)\s*\+?\s*(?:year|yr)s?\s*(?:of)?\s*(?:required|minimum|min)\b', re.IGNORECASE),
        re.compile(r'\b(\d+(?:\.\d+)?)\s*\+?\s*(?:year|yr)s?\s*(?:of)?\s*experience\b', re.IGNORECASE),
        re.compile(r'\b(\d+(?:\.\d+)?)\+?\s*(?:year|yr)s?\b', re.IGNORECASE)
    ]
    
    for pattern in min_patterns:
        matches = pattern.findall(text)
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                continue
    return 0.0

def extract_experience(text: str) -> List[Dict[str, Any]]:
    """
    Extracts work experience details from candidate resumes (compatibility placeholder).
    """
    years = extract_minimum_experience_years(text)
    return [{"company": "Previous Corp", "role": "Software Engineer", "years": years}]
