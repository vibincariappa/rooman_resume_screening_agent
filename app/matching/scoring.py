from typing import List, Dict, Any
from app.models.schemas import CandidateProfile, JobDescription, ScoreBreakdown

def calculate_candidate_score(profile: CandidateProfile, jd: JobDescription, semantic_score: float) -> ScoreBreakdown:
    """
    Calculates a deterministic ScoreBreakdown for a candidate against a Job Description.
    Weights:
      - Skills Match: 45%
      - Semantic Similarity: 30%
      - Experience Match: 15%
      - Education Match: 10%
    """
    # 1. Skills score
    matched_required = [s for s in jd.required_skills if s in profile.skills]
    missing_required = [s for s in jd.required_skills if s not in profile.skills]
    matched_preferred = [s for s in jd.preferred_skills if s in profile.skills]
    
    if not jd.required_skills:
        req_score = 100.0
    else:
        req_score = (len(matched_required) / len(jd.required_skills)) * 100.0
        
    if not jd.preferred_skills:
        pref_score = 100.0
    else:
        pref_score = (len(matched_preferred) / len(jd.preferred_skills)) * 100.0
        
    # Required skills are weighted more heavily (80% req, 20% pref within the skills block)
    skills_score = (req_score * 0.8) + (pref_score * 0.2)
    
    # 2. Experience score
    if jd.minimum_experience_years <= 0.0:
        experience_score = 100.0
    else:
        if profile.years_of_experience >= jd.minimum_experience_years:
            experience_score = 100.0
        else:
            experience_score = (profile.years_of_experience / jd.minimum_experience_years) * 100.0
            
    # 3. Education score
    if not jd.education_requirements:
        education_score = 100.0
    else:
        has_match = False
        for req_edu in jd.education_requirements:
            for cand_edu in profile.education:
                if req_edu.lower() in cand_edu.lower() or cand_edu.lower() in req_edu.lower():
                    has_match = True
                    break
        if has_match:
            education_score = 100.0
        else:
            education_score = 50.0 if profile.education else 0.0
            
    # 4. Final score
    final_score = (semantic_score * 0.30) + (skills_score * 0.45) + (experience_score * 0.15) + (education_score * 0.10)
    
    return ScoreBreakdown(
        semantic_score=round(semantic_score, 2),
        skills_score=round(skills_score, 2),
        experience_score=round(experience_score, 2),
        education_score=round(education_score, 2),
        final_score=round(final_score, 2),
        matched_skills=matched_required,
        missing_required_skills=missing_required
    )

def generate_screening_explanation(profile: CandidateProfile, jd: JobDescription, breakdown: ScoreBreakdown) -> str:
    """
    Generates a deterministic, human-readable summary detailing the screening outcome.
    """
    if breakdown.final_score >= 80.0:
        level = "Strong match"
    elif breakdown.final_score >= 60.0:
        level = "Moderate match"
    else:
        level = "Weak match"
        
    num_req_matched = len(breakdown.matched_skills)
    num_req_total = len(jd.required_skills)
    
    if num_req_total > 0:
        skills_part = f"matches {num_req_matched}/{num_req_total} required skills"
    else:
        skills_part = "matches all required skills"
        
    if profile.years_of_experience >= jd.minimum_experience_years:
        if jd.minimum_experience_years > 0:
            exp_part = "exceeds the minimum experience requirement"
        else:
            exp_part = "meets the experience requirement"
    else:
        exp_part = f"has insufficient experience ({profile.years_of_experience} years vs {jd.minimum_experience_years} required)"
        
    if breakdown.semantic_score >= 70.0:
        sim_part = "high semantic similarity"
    elif breakdown.semantic_score >= 50.0:
        sim_part = "moderate semantic similarity"
    else:
        sim_part = "low semantic similarity"
        
    return f"{level}. Candidate {skills_part}, {exp_part}, and has {sim_part} with the job description."
