import sys
import importlib
import argparse
from pathlib import Path

def verify_environment():
    print("=" * 60)
    print("Resume Screening AI Agent - Environment Verification")
    print("=" * 60)
    
    # 1. Check Python Version
    print(f"Python Version: {sys.version}")
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 11):
        print("[ERROR] Python 3.11+ is required.")
        sys.exit(1)
    else:
        print("[OK] Python version check passed.")
        
    # 2. Check Package Imports
    packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "fitz": "pymupdf",
        "docx": "python-docx",
        "sentence_transformers": "sentence-transformers",
        "sklearn": "scikit-learn",
        "pydantic": "pydantic",
        "pandas": "pandas",
        "pytest": "pytest",
        "dotenv": "python-dotenv",
        "openai": "openai"
    }
    
    print("\nVerifying package imports:")
    all_passed = True
    for module_name, package_name in packages.items():
        try:
            importlib.import_module(module_name)
            print(f"  [OK] {package_name} (imported successfully)")
        except ImportError:
            print(f"  [MISSING] {package_name} (failed to import)")
            all_passed = False
            
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] All systems ready! The environment is correctly configured.")
        print("To run the server, use: uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("[WARNING] Some packages are missing. Run: pip install -r requirements.txt")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Resume Screening AI Agent Tool")
    parser.add_argument("--resume", type=str, help="Path to a resume file to parse")
    parser.add_argument("--all-resumes", type=str, help="Path to a directory containing resumes to summarize")
    parser.add_argument("--job-description", type=str, help="Path to a job description file to parse")
    parser.add_argument("--resumes", type=str, help="Path to a directory containing resumes to screen")
    parser.add_argument("--screen", action="store_true", help="Screen resumes against the Job Description and rank them")
    parser.add_argument("--match", nargs=2, metavar=("JD_PATH", "RESUMES_DIR"), help="Calculate similarity scores between a JD and all resumes in a directory")
    args = parser.parse_args()
    
    if args.resume:
        try:
            from app.parsers import parse_document
            from app.extraction import extract_candidate_profile
            
            file_path = Path(args.resume)
            doc = parse_document(file_path)
            profile = extract_candidate_profile(doc.normalized_text, file_path.name, file_path.stem)
            
            print(f"Candidate Profile:")
            print(f"  Candidate ID: {profile.candidate_id}")
            print(f"  Filename: {profile.filename}")
            print(f"  Name: {profile.name or 'N/A'}")
            print(f"  Email: {profile.email or 'N/A'}")
            print(f"  Phone: {profile.phone or 'N/A'}")
            print(f"  Skills: {', '.join(profile.skills) if profile.skills else 'None'}")
            print(f"  Education: {', '.join(profile.education) if profile.education else 'None'}")
            print(f"  Years of Experience: {profile.years_of_experience}")
            print(f"  Summary: {profile.summary or 'N/A'}")
            print(f"\nWork Experience Section:")
            print(profile.work_experience or 'N/A')
            sys.exit(0)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.all_resumes:
        try:
            from app.parsers import parse_document
            from app.extraction import extract_candidate_profile
            
            resumes_dir = Path(args.all_resumes)
            if not resumes_dir.is_dir():
                raise FileNotFoundError(f"Directory not found: {args.all_resumes}")
                
            allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}
            files = sorted([p for p in resumes_dir.iterdir() if p.is_file() and p.suffix.lower() in allowed_suffixes])
            
            if not files:
                print("No resumes found in the directory.")
                sys.exit(0)
                
            print("=" * 100)
            print("Parsed Candidates Summary")
            print("=" * 100)
            print(f"{'Filename':<20} | {'Name':<15} | {'Email':<25} | {'Exp':<5} | {'Skills':<30}")
            print("-" * 100)
            
            for file in files:
                try:
                    parsed_doc = parse_document(file)
                    profile = extract_candidate_profile(parsed_doc.normalized_text, file.name, file.stem)
                    
                    name_str = profile.name or "N/A"
                    email_str = profile.email or "N/A"
                    skills_str = ", ".join(profile.skills[:4])
                    if len(profile.skills) > 4:
                        skills_str += "..."
                        
                    print(f"{file.name:<20} | {name_str:<15} | {email_str:<25} | {profile.years_of_experience:<5} | {skills_str:<30}")
                except Exception as e:
                    print(f"{file.name:<20} | Error: {e}")
            print("=" * 100)
            sys.exit(0)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.job_description and not args.screen:
        try:
            from app.extraction import extract_job_description
            file_path = Path(args.job_description)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
                
            jd = extract_job_description(raw_text)
            
            print(f"Job Title: {jd.title}")
            print(f"Minimum Experience (Years): {jd.minimum_experience_years}")
            print(f"Education Requirements: {', '.join(jd.education_requirements) if jd.education_requirements else 'None specified'}")
            print(f"Required Skills: {', '.join(jd.required_skills) if jd.required_skills else 'None'}")
            print(f"Preferred Skills: {', '.join(jd.preferred_skills) if jd.preferred_skills else 'None'}")
            print("\nResponsibilities:")
            for r in jd.responsibilities:
                print(f"  - {r}")
            sys.exit(0)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.screen:
        if not args.job_description or not args.resumes:
            print("Error: --screen requires both --job-description and --resumes directory.", file=sys.stderr)
            sys.exit(1)
            
        try:
            from app.parsers import parse_document
            from app.extraction import extract_job_description, extract_candidate_profile
            from app.matching.embeddings import generate_embedding
            from app.matching.similarity import calculate_similarity
            from app.matching.scoring import calculate_candidate_score
            
            jd_path = Path(args.job_description)
            resumes_dir = Path(args.resumes)
            
            if not jd_path.exists():
                raise FileNotFoundError(f"Job Description file not found: {jd_path}")
            if not resumes_dir.is_dir():
                raise FileNotFoundError(f"Resumes directory not found: {resumes_dir}")
                
            with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
                jd_text = f.read()
                
            jd = extract_job_description(jd_text)
            jd_embedding = generate_embedding(jd_text)
            
            allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}
            files = sorted([p for p in resumes_dir.iterdir() if p.is_file() and p.suffix.lower() in allowed_suffixes])
            
            if not files:
                print("No resumes found in the directory.")
                sys.exit(0)
                
            results = []
            for file in files:
                try:
                    parsed_doc = parse_document(file)
                    profile = extract_candidate_profile(parsed_doc.normalized_text, file.name, file.stem)
                    
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
                    
                    candidate_embedding = generate_embedding(meaningful_text)
                    sim = calculate_similarity(jd_embedding, candidate_embedding)
                    
                    breakdown = calculate_candidate_score(profile, jd, sim)
                    results.append((file.stem, breakdown))
                except Exception as e:
                    print(f"Error parsing/scoring candidate {file.name}: {e}", file=sys.stderr)
                    
            results.sort(key=lambda x: x[1].final_score, reverse=True)
            
            print(f"{'Rank':<5} {'Candidate':<14} {'Score':<7} {'Skills':<8} {'Semantic':<10} {'Experience':<10}")
            print("-" * 61)
            for idx, (stem, breakdown) in enumerate(results, 1):
                pretty_name = stem.replace("_", " ").title()
                print(f"{idx:<5} {pretty_name:<14} {breakdown.final_score:<7.2f} {breakdown.skills_score:<8.2f} {breakdown.semantic_score:<10.2f} {breakdown.experience_score:<10.2f}")
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected Error during screening: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.match:
        try:
            from app.parsers import parse_document
            from app.extraction import extract_candidate_profile
            from app.matching.embeddings import generate_embedding
            from app.matching.similarity import calculate_similarity
            
            jd_path_str, resumes_dir_str = args.match
            jd_path = Path(jd_path_str)
            resumes_dir = Path(resumes_dir_str)
            
            if not jd_path.exists():
                raise FileNotFoundError(f"Job Description file not found: {jd_path}")
            if not resumes_dir.is_dir():
                raise FileNotFoundError(f"Resumes directory not found: {resumes_dir}")
                
            with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
                jd_text = f.read()
                
            jd_embedding = generate_embedding(jd_text)
            
            allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}
            files = sorted([p for p in resumes_dir.iterdir() if p.is_file() and p.suffix.lower() in allowed_suffixes])
            
            if not files:
                print("No resumes found in the directory.")
                sys.exit(0)
                
            results = []
            
            for file in files:
                try:
                    parsed_doc = parse_document(file)
                    profile = extract_candidate_profile(parsed_doc.normalized_text, file.name, file.stem)
                    
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
                    
                    candidate_embedding = generate_embedding(meaningful_text)
                    sim = calculate_similarity(jd_embedding, candidate_embedding)
                    
                    results.append((file.stem, sim))
                except Exception as e:
                    results.append((file.stem, f"Error: {e}"))
                    
            def get_sort_key(item):
                score = item[1]
                return score if isinstance(score, float) else -1.0
                
            results.sort(key=get_sort_key, reverse=True)
            
            print(f"{'Candidate':<15} | {'Similarity':<10}")
            print("-" * 32)
            for stem, score in results:
                pretty_name = stem.replace("_", " ").title()
                if isinstance(score, float):
                    print(f"{pretty_name:<15} | {score:<10.1f}")
                else:
                    print(f"{pretty_name:<15} | {score:<10}")
            sys.exit(0)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    # Default behavior is environment verification
    verify_environment()

if __name__ == "__main__":
    main()
