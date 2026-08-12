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
    parser.add_argument("--job-description", type=str, help="Path to a job description file to parse")
    args = parser.parse_args()
    
    if args.resume:
        try:
            from app.parsers import parse_document
            file_path = Path(args.resume)
            doc = parse_document(file_path)
            
            print(f"Filename: {doc.filename}")
            print(f"File type: {doc.file_type}")
            print(f"Characters: {doc.character_count}")
            print(f"Words: {doc.word_count}")
            print("\nExtracted text:")
            print(doc.normalized_text)
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
            
    if args.job_description:
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
            
    # Default behavior is environment verification
    verify_environment()

if __name__ == "__main__":
    main()
