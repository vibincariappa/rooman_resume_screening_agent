import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from typing_extensions import Literal
from dotenv import load_dotenv

from app.models.schemas import CandidateProfile, JobDescription, ScoreBreakdown
from app.matching.scoring import generate_screening_explanation

load_dotenv()

class LLMReasoningOutput(BaseModel):
    summary: str = Field(description="A concise summary of the candidate's background and experience.")
    strengths: List[str] = Field(description="List of candidate's key strengths and matching qualifications.")
    gaps: List[str] = Field(description="List of candidate's key gaps or missing requirements.")
    suitability_explanation: str = Field(description="Detailed explanation of why the candidate is suitable or not suitable for the role.")
    recommended_decision: Literal["Strong Match", "Good Match", "Potential Match", "Weak Match"] = Field(
        description="Recommended hiring match decision."
    )

def get_llm_client_and_model() -> Tuple[Optional[Any], Optional[str]]:
    """
    Returns a configured OpenAI-compatible client and model name based on .env config.
    """
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Auto-resolve provider if not explicitly defined
    if not provider:
        if gemini_key:
            provider = "gemini"
        elif openai_key:
            provider = "gemini" if openai_key.startswith("AIzaSy") else "openai"
            
    if provider == "gemini":
        key = gemini_key or openai_key
        if not key:
            return None, None
        from openai import OpenAI
        client = OpenAI(
            api_key=key,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )
        model = os.getenv("OPENAI_MODEL", "gemini-1.5-flash").strip()
        return client, model
        
    elif provider == "openai":
        if not openai_key:
            return None, None
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        return client, model
        
    elif provider == "ollama":
        from openai import OpenAI
        client = OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
        model = os.getenv("OLLAMA_MODEL", "llama3").strip()
        return client, model
        
    return None, None

def get_deterministic_reasoning(profile: CandidateProfile, jd: JobDescription, breakdown: ScoreBreakdown) -> LLMReasoningOutput:
    """
    Generates a structured candidate explanation deterministically as a fallback.
    """
    suitability = generate_screening_explanation(profile, jd, breakdown)
    
    if breakdown.final_score >= 80.0:
        decision = "Strong Match"
    elif breakdown.final_score >= 60.0:
        decision = "Good Match"
    elif breakdown.final_score >= 40.0:
        decision = "Potential Match"
    else:
        decision = "Weak Match"
        
    summary = profile.summary or f"Candidate {profile.name or 'N/A'} with {profile.years_of_experience} years of experience."
    
    # Strengths
    strengths = []
    if breakdown.matched_skills:
        strengths.append(f"Matches skills: {', '.join(breakdown.matched_skills)}")
    if profile.years_of_experience >= jd.minimum_experience_years and jd.minimum_experience_years > 0:
        strengths.append(f"Meets or exceeds experience requirement of {jd.minimum_experience_years} years.")
    if breakdown.education_score == 100.0:
        strengths.append("Meets education requirements.")
        
    # Gaps
    gaps = []
    if breakdown.missing_required_skills:
        gaps.append(f"Missing required skills: {', '.join(breakdown.missing_required_skills)}")
    if profile.years_of_experience < jd.minimum_experience_years:
        gaps.append(f"Under-experienced: has {profile.years_of_experience} years vs {jd.minimum_experience_years} required.")
    if breakdown.education_score < 100.0:
        gaps.append("Does not meet preferred education degree requirement.")
        
    return LLMReasoningOutput(
        summary=summary,
        strengths=strengths if strengths else ["Basic profile matching."],
        gaps=gaps if gaps else ["No major gaps identified."],
        suitability_explanation=suitability,
        recommended_decision=decision
    )

def query_llm_reasoning(profile: CandidateProfile, jd: JobDescription, breakdown: ScoreBreakdown) -> LLMReasoningOutput:
    """
    Queries the LLM provider to construct structured recruiting summaries and gaps details.
    Falls back to deterministic rules if client setup or network call fails.
    """
    client, model = get_llm_client_and_model()
    if not client or not model:
        return get_deterministic_reasoning(profile, jd, breakdown)
        
    system_prompt = (
        "You are an expert AI recruiter. Analyze the candidate against the Job Description.\n"
        "Rules:\n"
        "- Use ONLY the supplied candidate data. Do not infer or extrapolate missing qualifications.\n"
        "- Do not hallucinate skills, companies, education, experience, or any candidate facts.\n"
        "- Do not change or recalculate the scores. The deterministic score is the source of truth."
    )
    
    user_content = (
        f"Job Description:\n"
        f"Title: {jd.title}\n"
        f"Required Skills: {', '.join(jd.required_skills)}\n"
        f"Preferred Skills: {', '.join(jd.preferred_skills)}\n"
        f"Minimum Experience: {jd.minimum_experience_years} years\n"
        f"Education Requirements: {', '.join(jd.education_requirements)}\n\n"
        f"Candidate Profile:\n"
        f"Name: {profile.name or 'N/A'}\n"
        f"Summary: {profile.summary or 'N/A'}\n"
        f"Skills: {', '.join(profile.skills)}\n"
        f"Education: {', '.join(profile.education)}\n"
        f"Years of Experience: {profile.years_of_experience}\n"
        f"Work Experience Block:\n{profile.work_experience or 'N/A'}\n\n"
        f"Deterministic Scoring & Match Data:\n"
        f"Final Score: {breakdown.final_score}\n"
        f"Skills Score: {breakdown.skills_score}\n"
        f"Semantic Score: {breakdown.semantic_score}\n"
        f"Experience Score: {breakdown.experience_score}\n"
        f"Education Score: {breakdown.education_score}\n"
        f"Matched Skills: {', '.join(breakdown.matched_skills)}\n"
        f"Missing Required Skills: {', '.join(breakdown.missing_required_skills)}\n"
    )
    
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format=LLMReasoningOutput,
            temperature=0.0
        )
        parsed = response.choices[0].message.parsed
        if parsed:
            return parsed
        raise ValueError("Failed to parse LLM structured output.")
    except Exception as e:
        print(f"\n[WARNING] LLM reasoning generation failed: {e}. Falling back to deterministic reasoning.")
        return get_deterministic_reasoning(profile, jd, breakdown)
