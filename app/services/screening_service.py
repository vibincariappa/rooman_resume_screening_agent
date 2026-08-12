import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.models.schemas import (
    ResumeDocument,
    CandidateProfile,
    JobDescription,
    ScoreBreakdown,
    BatchScreeningResult
)
from app.parsers import parse_document
from app.extraction import extract_job_description, extract_candidate_profile
from app.matching.embeddings import generate_embedding
from app.matching.similarity import calculate_similarity
from app.matching.scoring import calculate_candidate_score
from app.reasoning import query_llm_reasoning

def parse_resumes(resume_paths: List[Path]) -> List[ResumeDocument]:
    """
    Parses a list of resume paths and returns a list of ResumeDocument models.
    """
    documents = []
    for path in resume_paths:
        doc = parse_document(path)
        documents.append(doc)
    return documents

def screen_candidates(
    job_description_path: str,
    resumes_directory: str,
    output_directory: Optional[str] = None
) -> BatchScreeningResult:
    """
    Screens all candidates in resumes_directory against job_description_path,
    calculates scores, generates explanations, sorts by score descending,
    and optionally exports JSON/CSV.
    """
    start_time = time.time()
    
    jd_path = Path(job_description_path)
    res_dir = Path(resumes_directory)
    
    if not jd_path.exists():
        raise FileNotFoundError(f"Job Description file not found: {jd_path}")
    if not res_dir.is_dir():
        raise FileNotFoundError(f"Resumes directory not found: {res_dir}")
        
    # 1. Parse JD
    print(f"[*] Loading and parsing Job Description from: {jd_path.name}")
    with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
        jd_text = f.read()
    jd = extract_job_description(jd_text)
    
    # 2. Embed JD
    print("[*] Generating semantic embeddings for Job Description...")
    jd_embedding = generate_embedding(jd_text)
    
    # 3. Find resumes
    allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}
    resume_files = sorted([
        p for p in res_dir.iterdir()
        if p.is_file() and p.suffix.lower() in allowed_suffixes
    ])
    
    total_count = len(resume_files)
    print(f"[*] Found {total_count} candidate resume(s) to process.")
    
    processed_count = 0
    failed_candidates: List[Dict[str, str]] = []
    ranked_candidates: List[Dict[str, Any]] = []
    
    # 4. Process each resume
    for idx, file in enumerate(resume_files, 1):
        print(f"[{idx}/{total_count}] Processing resume: {file.name}...", end="", flush=True)
        try:
            # Parse document
            doc = parse_document(file)
            # Extract structured CandidateProfile
            profile = extract_candidate_profile(doc.normalized_text, file.name, file.stem)
            
            # Extract meaningful text context for similarity embedding (ignoring headers/contact info)
            meaningful_parts = []
            if profile.summary:
                meaningful_parts.append(profile.summary)
            if profile.skills:
                meaningful_parts.append("Skills: " + ", ".join(profile.skills))
            if profile.work_experience:
                meaningful_parts.append("Experience:\n" + profile.work_experience)
            if profile.education:
                meaningful_parts.append("Education: " + ", ".join(profile.education))
            meaningful_text = "\n\n".join(meaningful_parts) if meaningful_parts else profile.raw_text
            
            # Embed candidate
            cand_embedding = generate_embedding(meaningful_text)
            sim = calculate_similarity(jd_embedding, cand_embedding)
            
            # Score candidate
            breakdown = calculate_candidate_score(profile, jd, sim)
            
            # Get reasoning explanation
            reasoning = query_llm_reasoning(profile, jd, breakdown)
            
            # Record success details
            candidate_record = {
                "candidate_id": profile.candidate_id,
                "candidate_name": profile.name or "N/A",
                "filename": profile.filename,
                "final_score": breakdown.final_score,
                "semantic_score": breakdown.semantic_score,
                "skills_score": breakdown.skills_score,
                "experience_score": breakdown.experience_score,
                "education_score": breakdown.education_score,
                "matched_skills": breakdown.matched_skills,
                "missing_required_skills": breakdown.missing_required_skills,
                "recommendation": reasoning.recommended_decision,
                "explanation": reasoning.suitability_explanation
            }
            ranked_candidates.append(candidate_record)
            processed_count += 1
            print(" SUCCESS")
        except Exception as e:
            print(" FAILED")
            failed_candidates.append({
                "filename": file.name,
                "error": str(e)
            })
            
    # 5. Sort candidates by final score descending
    ranked_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Add ranks to records
    for rank_idx, cand in enumerate(ranked_candidates, 1):
        cand["rank"] = rank_idx
        
    processing_time = round(time.time() - start_time, 2)
    
    result = BatchScreeningResult(
        job_title=jd.title or "N/A",
        total_candidates=total_count,
        processed_candidates=processed_count,
        failed_candidates=failed_candidates,
        ranked_candidates=ranked_candidates,
        processing_time=processing_time
    )
    
    # 6. Export results if requested
    if output_directory:
        out_dir = Path(output_directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = out_dir / "ranked_candidates.json"
        csv_path = out_dir / "ranked_candidates.csv"
        
        # Save JSON
        print(f"[*] Saving JSON results to: {json_path}")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(result.model_dump(), jf, indent=2)
            
        # Save CSV
        print(f"[*] Saving CSV results to: {csv_path}")
        csv_columns = [
            "rank",
            "candidate_id",
            "candidate_name",
            "filename",
            "final_score",
            "semantic_score",
            "skills_score",
            "experience_score",
            "education_score",
            "matched_skills",
            "missing_required_skills",
            "recommendation"
        ]
        
        with open(csv_path, "w", encoding="utf-8", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=csv_columns, extrasaction="ignore")
            writer.writeheader()
            for cand in ranked_candidates:
                # Format list values as comma-separated strings
                row = cand.copy()
                if isinstance(row.get("matched_skills"), list):
                    row["matched_skills"] = ", ".join(row["matched_skills"])
                if isinstance(row.get("missing_required_skills"), list):
                    row["missing_required_skills"] = ", ".join(row["missing_required_skills"])
                writer.writerow(row)
                
    return result
