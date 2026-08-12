import re
from typing import List, Optional
from app.models.schemas import CandidateProfile
from app.extraction.skills import match_skills_in_text
from app.extraction.education import extract_education_requirements
from app.extraction.experience import extract_minimum_experience_years

def extract_name(text: str) -> Optional[str]:
    """
    Extracts candidate name based on heuristics.
    Looks at the first few lines of the text and filters out contact details,
    common keywords, and job title markers.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    exclude_keywords = {
        "resume", "cv", "curriculum", "vitae", "profile", "contact", "email",
        "phone", "skills", "experience", "education", "summary", "objective",
        "engineer", "developer", "designer", "architect", "scientist", "analyst"
    }
    
    for line in lines[:5]:
        # Skip if contains email symbol or digit sequences (phone number)
        if "@" in line or any(c.isdigit() for c in line if c in "+-() "):
            continue
            
        # Skip if line contains any of the exclude keywords in a simple search
        lower_line = line.lower()
        if any(kw in lower_line for kw in exclude_keywords):
            continue
            
        # Check if line words are capitalized (common for names)
        words = [w for w in line.split() if w]
        if 2 <= len(words) <= 4:
            # Check capitalization of each word
            if all(word[0].isupper() or word[0].isdigit() or word in ["and", "of", "de", "di"] for word in words if word):
                return line
                
    return None

def extract_email(text: str) -> Optional[str]:
    """
    Extracts email address using a robust regex pattern.
    """
    pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    match = pattern.search(text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """
    Extracts phone number using standard formats (supporting 7-digit, 10-digit, and international).
    """
    pattern = re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|'
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{4}\b|'
        r'(?:\+91|0)?\s*[789]\d{9}\b'
    )
    match = pattern.search(text)
    return match.group(0).strip() if match else None

def extract_work_experience_section(text: str) -> Optional[str]:
    """
    Extracts and preserves the work experience block from the resume.
    """
    lines = text.split("\n")
    experience_headers = [
        "experience", "work experience", "professional experience", 
        "employment", "work history", "employment history", "experience history"
    ]
    other_headers = [
        "education", "skills", "projects", "certifications", 
        "interests", "languages", "summary", "objective", "publications",
        "key skills", "technical skills", "profile"
    ]
    
    in_section = False
    section_lines = []
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            if in_section:
                section_lines.append("")
            continue
            
        lower_line = clean_line.lower().rstrip(":")
        
        # Check if entering experience section
        if any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in experience_headers) and len(clean_line) < 40:
            in_section = True
            continue
            
        # Check if leaving section and entering another
        if in_section:
            if any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in other_headers) and len(clean_line) < 40:
                in_section = False
                break
            section_lines.append(clean_line)
            
    if section_lines:
        return "\n".join(section_lines).strip()
    return None

def extract_summary_section(text: str) -> Optional[str]:
    """
    Extracts and preserves the summary/about block from the resume.
    """
    lines = text.split("\n")
    summary_headers = ["summary", "objective", "professional summary", "about me", "profile", "career objective"]
    other_headers = [
        "experience", "work experience", "professional experience", 
        "employment", "education", "skills", "projects", "certifications",
        "key skills", "technical skills"
    ]
    
    in_section = False
    section_lines = []
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            if in_section:
                section_lines.append("")
            continue
            
        lower_line = clean_line.lower().rstrip(":")
        
        # Check if entering summary section
        if any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in summary_headers) and len(clean_line) < 40:
            in_section = True
            continue
            
        # Check if leaving section and entering another
        if in_section:
            if any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in other_headers) and len(clean_line) < 40:
                in_section = False
                break
            section_lines.append(clean_line)
            
    if section_lines:
        return "\n".join(section_lines).strip()
    return None

def extract_candidate_profile(raw_text: str, filename: str, candidate_id: str) -> CandidateProfile:
    """
    Coordinates the deterministic extraction of CandidateProfile fields from resume text.
    """
    name = extract_name(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    skills = match_skills_in_text(raw_text)
    education = extract_education_requirements(raw_text)
    years_exp = extract_minimum_experience_years(raw_text)  # uses regex matching
    work_exp = extract_work_experience_section(raw_text)
    summary = extract_summary_section(raw_text)
    
    return CandidateProfile(
        candidate_id=candidate_id,
        filename=filename,
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        education=education,
        years_of_experience=years_exp,
        work_experience=work_exp,
        summary=summary,
        raw_text=raw_text
    )
