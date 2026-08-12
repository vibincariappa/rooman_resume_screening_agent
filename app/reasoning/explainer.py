from typing import Dict, Any

def explain_screening_decision(candidate_name: str, score: float, details: Dict[str, Any]) -> str:
    """
    Generates a written explanation detailing why the candidate received their score.
    Placeholder implementation.
    """
    skills = details.get("skills", [])
    return f"Candidate {candidate_name} scored {score:.2f} due to matching skills: {', '.join(skills)}."
