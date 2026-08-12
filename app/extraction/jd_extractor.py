import re
from typing import List
from app.models.schemas import JobDescription
from app.extraction.skills import extract_skills_categorized
from app.extraction.education import extract_education_requirements
from app.extraction.experience import extract_minimum_experience_years

def extract_title(text: str) -> str:
    """
    Extracts the job title, which is assumed to be the first non-empty line.
    """
    for line in text.split("\n"):
        clean = line.strip()
        if clean:
            # Remove markdown header markers if any (e.g. # Job Title)
            clean = re.sub(r'^#+\s*', '', clean)
            return clean
    return "Unknown Position"

def extract_responsibilities(text: str) -> List[str]:
    """
    Extracts list items or lines from the Responsibilities section of the JD.
    """
    lines = text.split("\n")
    responsibilities = []
    in_section = False
    
    headers = [
        "responsibilities", "what you will do", "key responsibilities", 
        "role and responsibilities", "duties", "essential functions",
        "what you'll do", "what you will perform"
    ]
    
    other_headers = [
        "requirements", "qualifications", "skills", "about us", "who you are",
        "benefits", "perks", "nice to have", "preferred", "education", "experience",
        "about the role"
    ]
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        lower_line = clean_line.lower().rstrip(":")
        
        # Check if entering responsibilities section
        if any(h in lower_line for h in headers) and len(clean_line) < 40:
            in_section = True
            continue
            
        # Check if leaving section
        if in_section:
            if any(h in lower_line for h in other_headers) and len(clean_line) < 40:
                in_section = False
                break
                
            # Strip bullet prefix
            bullet_match = re.match(r'^[\-\*\•\d+\.]\s*(.*)', clean_line)
            if bullet_match:
                item = bullet_match.group(1).strip()
            else:
                item = clean_line
                
            if item:
                responsibilities.append(item)
                
    return responsibilities

def extract_job_description(raw_text: str) -> JobDescription:
    """
    Deterministic extraction of JobDescription structure from raw text.
    """
    title = extract_title(raw_text)
    req_skills, pref_skills = extract_skills_categorized(raw_text)
    min_exp = extract_minimum_experience_years(raw_text)
    edu_reqs = extract_education_requirements(raw_text)
    resps = extract_responsibilities(raw_text)
    
    return JobDescription(
        title=title,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        minimum_experience_years=min_exp,
        education_requirements=edu_reqs,
        responsibilities=resps,
        raw_text=raw_text
    )
