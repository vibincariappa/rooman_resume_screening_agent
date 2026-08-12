import re
from typing import List, Tuple, Set

# Centralized skills catalog
SKILLS_CATALOGUE = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Next.js", 
    "Node.js", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", 
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Machine Learning", 
    "Deep Learning", "NLP", "LLM", "RAG", "TensorFlow", "PyTorch", 
    "scikit-learn", "Pandas", "NumPy", "Git"
]

def get_skill_regex(skill_name: str) -> re.Pattern:
    """
    Creates a case-insensitive regex for the given skill, taking into account
    word boundaries and special ending characters (like C++ or Next.js).
    """
    escaped = re.escape(skill_name)
    start_boundary = r'\b' if escaped[0].isalnum() else ''
    
    # If the skill ends in non-word chars (like ++), we require that it is not followed by a word character.
    # Otherwise, standard word boundary \b.
    if skill_name[-1].isalnum():
        end_boundary = r'\b'
    else:
        end_boundary = r'(?!\w)'
        
    return re.compile(start_boundary + escaped + end_boundary, re.IGNORECASE)

def match_skills_in_text(text: str) -> List[str]:
    """
    Matches any skills from the SKILLS_CATALOGUE present in the text, avoiding false matches.
    """
    matched = []
    for skill in SKILLS_CATALOGUE:
        regex = get_skill_regex(skill)
        if regex.search(text):
            matched.append(skill)
    return matched

def extract_skills(text: str) -> List[str]:
    """
    Extracts all matched skills from text.
    """
    return match_skills_in_text(text)

def extract_skills_categorized(text: str) -> Tuple[List[str], List[str]]:
    """
    Parses sections of the Job Description to categorize skills into required and preferred.
    """
    lines = text.split("\n")
    required_skills: Set[str] = set()
    preferred_skills: Set[str] = set()
    
    # Headers indicating preferred section
    preferred_headers = [
        "nice to have", "preferred", "plus", "bonus", "desired",
        "preferred qualifications", "highly preferred", "good to have",
        "assets", "additional qualifications"
    ]
    
    # Headers indicating required section
    required_headers = [
        "requirements", "qualifications", "what you need", "skills",
        "must have", "basic qualifications", "experience required",
        "responsibilities", "key requirements"
    ]
    
    is_preferred = False
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        lower_line = clean_line.lower().rstrip(":")
        
        # Section headers are short, don't start with list bullet points
        is_bullet = clean_line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5."))
        is_header = len(clean_line) < 40 and not is_bullet
        
        if is_header:
            if any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in preferred_headers):
                is_preferred = True
                continue
            elif any(lower_line == h or lower_line.startswith(h + " ") or lower_line.endswith(h) for h in required_headers):
                is_preferred = False
                continue
            
        # Match skills on this line
        matched = match_skills_in_text(clean_line)
        if matched:
            if is_preferred:
                preferred_skills.update(matched)
            else:
                required_skills.update(matched)
                
    # Deduplicate: if a skill is in required, it should not be in preferred
    preferred_skills = preferred_skills - required_skills
    
    return sorted(list(required_skills)), sorted(list(preferred_skills))
