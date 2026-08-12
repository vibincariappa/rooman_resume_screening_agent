# Resume Screening AI Agent

A pipeline-based Resume Screening AI Agent designed to parse, extract, match, rank, and explain candidates' resumes against a Job Description. 

This project is built using a deterministic, NLP-similarity-driven scoring framework combined with clean Python architecture to ensure auditability, performance, and transparency.

---

## 📅 Project Phase: Deterministic Candidate Scoring Engine (Step 5 Completed)

We have completed **Step 5: Deterministic Candidate Scoring Engine**. Candidates can now be ranked and screened using a deterministic multi-criteria scoring algorithm based on Skills Match (45%), Semantic Similarity (30%), Experience Match (15%), and Education Match (10%).



---

## 📁 Directory Structure

```text
resume-screening-agent/
│
├── app/                        # Main application source code
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and routing entry point
│   │
│   ├── parsers/                # Document parsing (PDF, DOCX, TXT to Raw Text)
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── txt_parser.py
│   │
│   ├── extraction/             # Info extraction (Skills, Experience, Education)
│   │   ├── __init__.py
│   │   ├── skills.py
│   │   ├── education.py
│   │   └── experience.py
│   │
│   ├── matching/               # Semantic alignment & score calculations
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── similarity.py
│   │   └── scoring.py
│   │
│   ├── reasoning/              # Explainability & candidate screening reasoning
│   │   ├── __init__.py
│   │   └── explainer.py
│   │
│   ├── models/                 # Pydantic schemas / request-response DTOs
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   └── services/               # Core orchestration layer
│       ├── __init__.py
│       └── screening_service.py
│
├── data/                       # Directory for local mock files
│   ├── resumes/                # Input resume files (PDF, DOCX, TXT)
│   ├── job_descriptions/       # Input Job Description files
│   └── output/                 # CSV / JSON report output targets
│
├── tests/                      # Automated test suite (pytest)
├── scripts/                    # Helper scripts for preprocessing or generation
│
├── .env.example                # Config template
├── .gitignore                  # Git exclude patterns
├── requirements.txt            # System dependencies list
├── README.md                   # Project documentation (this file)
└── run.py                      # Environment verification and local running utility
```

### Directory Roles:
- **`app/parsers`**: Isolates file format extraction logic using `PyMuPDF` (PDF), `python-docx` (DOCX), and native tools (TXT).
- **`app/extraction`**: Uses rule-based or NLP mechanisms to identify specific metadata (skills, degrees, years of experience) from the raw text.
- **`app/matching`**: Utilizes embedding models (e.g. `sentence-transformers`) and cosine similarity from `scikit-learn` to calculate deterministic scores.
- **`app/reasoning`**: Provides LLM-driven textual explanations detailing why a candidate did or did not match.
- **`app/models`**: Declares structured data contracts using Pydantic.
- **`app/services`**: Orchestrates the entire screening workflow cleanly.

---

## 🛠️ How to Run and Verify the Project

### 1. Prerequisites
- Python 3.11+ is required.

### 2. Environment Setup
Create a virtual environment and install the dependencies:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Environment
Run the validation script to verify python version and checking importable modules:
```bash
python run.py
```

### 4. Running the Development Server
To launch the API server locally:
```bash
uvicorn app.main:app --reload
```
Once started, API documentation will be available at `http://127.0.0.1:8000/docs`.

### 5. Running Tests
Run all unit tests using pytest:
```bash
python -m pytest
```

---

## 📄 Document Parser Usage & CLI Interface

### Supported Formats
The system includes specialized parsers for:
*   **PDF (`.pdf`)**: Using PyMuPDF (`fitz`) to extract structured page text.
*   **Word (`.docx`)**: Using `python-docx` to extract text from paragraphs and tables.
*   **Plain Text (`.txt`, `.md`)**: Raw UTF-8 string reader.

### Whitespace Normalization
All extractors route raw content through a normalizer that:
1. Strips leading and trailing whitespaces on each line.
2. Collapses 3+ consecutive newlines down to exactly 2 newlines (double newlines) to preserve paragraph structure without clutter.

### CLI Extraction Commands

#### 1. Parse and Extract a Single Resume
Extract structured fields and profile information of a single resume file:
```bash
python run.py --resume data/resumes/candidate_01.pdf
```

**Expected Output:**
```text
Candidate Profile:
  Candidate ID: candidate_01
  Filename: candidate_01.pdf
  Name: John Doe
  Email: john.doe@example.com
  Phone: +1-555-0101
  Skills: Python, FastAPI, SQL, PostgreSQL, Docker, PyTorch, scikit-learn, Git
  Education: B.Tech
  Years of Experience: 3.0
  Summary: Experienced Software Engineer specializing in AI pipelines and FastAPI backend services.

Work Experience Section:
Tech Corp - Software Engineer
3 years of experience.
- Designed and deployed FastAPI backend apps with SQL.
- Used Docker for containerizing models.
```

#### 2. Summarize All Resumes in a Directory
Run batch parsing and structured extraction across all files in a folder to print a summary table:
```bash
python run.py --all-resumes data/resumes/
```

**Expected Output:**
```text
====================================================================================================
Parsed Candidates Summary
====================================================================================================
Filename             | Name            | Email                     | Exp   | Skills                        
----------------------------------------------------------------------------------------------------
candidate_01.pdf     | John Doe        | john.doe@example.com      | 3.0   | Python, FastAPI, SQL, PostgreSQL...
candidate_02.docx    | Jane Smith      | jane.smith@example.com    | 4.0   | Python, SQL, Deep Learning, TensorFlow...
candidate_03.txt     | Alex Jones      | alex.jones@example.com    | 2.0   | Python, Docker, Kubernetes, AWS...
...
```

#### 3. Screen and Rank Candidates
Compare candidates against a job description using the deterministic scoring engine and print a ranked evaluation table:
```bash
python run.py --screen --job-description data/job_descriptions/sample_jd.txt --resumes data/resumes/
```

**Expected Output:**
```text
Rank  Candidate      Score   Skills   Semantic   Experience
-------------------------------------------------------------
1     Candidate 01   74.54   62.22    71.80      100.00    
2     Candidate 02   70.72   53.33    72.40      100.00    
3     Candidate 04   64.95   44.44    66.50      100.00    
...
```

### Error Handling
The parser detects and handles exceptions gracefully, outputting a clear diagnostic error and exiting with code `1`:
*   *Unsupported File Type*: Throws `Error: Unsupported file type: .xyz`
*   *Missing File*: Throws `Error: File not found: path/to/file`
*   *Empty File*: Throws `Error: Empty or unreadable <format> document.`
*   *Corrupted File*: Throws `Error: Corrupted or invalid <format> file: <details>`
