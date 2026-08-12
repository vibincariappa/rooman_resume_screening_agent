from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CandidateProfile(BaseModel):
    name: str
    skills: List[str] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    raw_text: Optional[str] = None

class JobDescription(BaseModel):
    title: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_experience_years: float = 0.0
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: str

class ScreeningResult(BaseModel):
    candidate_name: str
    relevance_score: float
    skills_match_score: float
    experience_match_score: float
    semantic_similarity_score: float
    reasoning: str
    details: Dict[str, Any] = Field(default_factory=dict)

class ResumeDocument(BaseModel):
    filename: str
    file_type: str
    raw_text: str
    normalized_text: str
    character_count: int
    word_count: int
