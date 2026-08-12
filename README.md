# Resume Screening AI Agent

A pipeline-based Resume Screening AI Agent designed to parse, extract, match, rank, and explain candidates' resumes against a Job Description. 

This project is built using a deterministic, NLP-similarity-driven scoring framework combined with clean Python architecture to ensure auditability, performance, and transparency.

---

## 📅 Project Phase: Document Parsing (Step 1 Completed)

We have completed **Step 1: Resume Document Parsing**. The pipeline now supports importing, parsing, and normalizing `.pdf`, `.docx`, and `.txt` files with type-safety and detailed validations.


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

### Parser CLI Command
You can run the CLI parser directly from the terminal to inspect metadata and normalized outputs of any resume file:
```bash
python run.py --resume data/resumes/candidate_01.pdf
```

**Expected Output:**
```text
Filename: candidate_01.pdf
File type: pdf
Characters: 174
Words: 27

Extracted text:
John Doe
Python Software Engineer
Skills: Python, FastAPI, Docker, PostgreSQL
Experience:
- Backend Engineer at Tech Corp (2 years)
- Junior Developer at StartUp Inc (1 year)
```

### Error Handling
The parser detects and handles exceptions gracefully, outputting a clear diagnostic error and exiting with code `1`:
*   *Unsupported File Type*: Throws `Error: Unsupported file type: .xyz`
*   *Missing File*: Throws `Error: File not found: path/to/file`
*   *Empty File*: Throws `Error: Empty or unreadable <format> document.`
*   *Corrupted File*: Throws `Error: Corrupted or invalid <format> file: <details>`
