from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CandidateProfile(BaseModel):
    candidate_id: str
    filename: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    years_of_experience: float = 0.0
    work_experience: Optional[str] = None
    summary: Optional[str] = None
    raw_text: str

class JobDescription(BaseModel):
    title: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_experience_years: float = 0.0
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: str

class ScoreBreakdown(BaseModel):
    semantic_score: float
    skills_score: float
    experience_score: float
    education_score: float
    final_score: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)

class ScreeningResult(BaseModel):
    candidate_name: str
    relevance_score: float
    skills_match_score: float
    experience_match_score: float
    semantic_similarity_score: float
    reasoning: str
    breakdown: ScoreBreakdown
    details: Dict[str, Any] = Field(default_factory=dict)

class ResumeDocument(BaseModel):
    filename: str
    file_type: str
    raw_text: str
    normalized_text: str
    character_count: int
    word_count: int

class SimilarityResult(BaseModel):
    candidate_id: str
    semantic_similarity: float
    matched_text_context: Optional[str] = None

class BatchScreeningResult(BaseModel):
    job_title: str
    total_candidates: int
    processed_candidates: int
    failed_candidates: List[Dict[str, str]] = Field(default_factory=list)
    ranked_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time: float
