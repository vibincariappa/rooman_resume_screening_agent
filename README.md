# Resume Screening AI Agent

## Overview

The Resume Screening AI Agent is a pipeline-based system that parses, extracts, matches, ranks, and explains candidate resumes against a Job Description. Developed as a submission for the Rooman Technologies 24-Hour AI Agent Challenge, it combines a deterministic, transparent scoring engine with an optional LLM reasoning layer to assist recruiters in evaluating candidates at scale.

---

## Quick Start

Clone the repository and run the CLI agent in under five minutes.

```bash
# 1. Clone the repository
git clone https://github.com/vibincariappa/rooman_resume_screening_agent.git
cd rooman_resume_screening_agent

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the environment
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the full batch screening pipeline
python run.py --screen \
  --job-description data/job_descriptions/sample_jd.txt \
  --resumes data/resumes/ \
  --output data/output/
```

Results are written to:
- `data/output/ranked_candidates.json`
- `data/output/ranked_candidates.csv`

---

## Features

- **Document Parsing**: Extracts text from PDF, DOCX, TXT, and MD resume files.
- **Information Extraction**: Extracts candidate name, email, phone, skills, years of experience, and education using rule-based heuristics and regular expressions.
- **Semantic Alignment**: Measures NLP similarity between the Job Description and each candidate's profile using sentence embeddings and cosine similarity.
- **Deterministic Scoring**: Computes a transparent, reproducible candidate score using a fixed weighted formula.
- **Recruiter Reasoning**: Uses Google Gemini (primary), OpenAI (fallback), or Ollama (local fallback) to generate candidate summaries, strengths, gaps, and decisions. Falls back to a deterministic rule-based generator if no LLM is configured or the API call fails.
- **Multi-format Export**: Saves ranked results as JSON and CSV.
- **REST API**: FastAPI backend with endpoints for health checks, JSON screening, multipart file upload, and results retrieval.
- **Interactive Dashboard**: A React + TypeScript web frontend for uploading resumes, running screening, and reviewing ranked candidate profiles.
- **Failure Resilience**: Parsing errors on individual files are caught and logged without terminating the batch.

---

## Architecture

The system follows a modular, decoupled pipeline:

1. **Document Parser**: Routes each file by extension to format-specific extractors (PDF, DOCX, TXT/MD).
2. **Extraction Engine**: Extracts structured candidate data using a skills catalog, experience regex, and education degree checklist.
3. **Embedding Engine**: Encodes the Job Description and each candidate's meaningful text sections using `all-MiniLM-L6-v2`.
4. **Matching Engine**: Computes cosine similarity between the JD and candidate embeddings, normalized to a 0-100 scale.
5. **Scoring Engine**: Applies the deterministic weighted formula to produce a final candidate score.
6. **Reasoning Layer**: Sends the score breakdown and candidate data to the configured LLM to produce a human-readable recruiter explanation.
7. **Service Orchestrator**: Coordinates the full pipeline, sorts results, handles errors, and writes outputs.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Uvicorn) |
| PDF Parsing | PyMuPDF (`fitz`) |
| DOCX Parsing | python-docx |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Similarity | scikit-learn (cosine similarity) |
| LLM Integration | OpenAI Python SDK (routing to Gemini, OpenAI, or Ollama) |
| Validation | Pydantic v2 |
| Environment | python-dotenv |
| Testing | pytest |
| Frontend | React, TypeScript, Vite, Tailwind CSS v3, Lucide React |

---

## Project Structure

```text
rooman_resume_screening_agent/
├── app/                            # Backend application source
│   ├── main.py                     # FastAPI application and route definitions
│   ├── parsers/                    # PDF, DOCX, and TXT/MD parsers
│   ├── extraction/                 # Skills, experience, education, and JD extractors
│   ├── matching/                   # Embeddings, cosine similarity, and scoring logic
│   ├── reasoning/                  # LLM explainer and deterministic fallback
│   ├── models/                     # Pydantic schemas
│   └── services/                   # Screening pipeline orchestrator
├── data/
│   ├── resumes/                    # Input candidate resume files (sample set included)
│   ├── job_descriptions/           # Input Job Description files (sample included)
│   └── output/                     # Generated JSON and CSV results
├── frontend/                       # React web dashboard
│   ├── src/
│   │   ├── App.tsx                 # Main component (state, upload, table, sidebar)
│   │   ├── App.css                 # Component styles
│   │   └── index.css               # Global styles and Tailwind imports
│   ├── tailwind.config.js
│   └── package.json
├── tests/
│   ├── test_screening.py           # Unit and integration tests for extractors and scoring
│   └── test_api.py                 # FastAPI endpoint integration tests
├── scripts/
│   └── generate_mock_resumes.py    # Script used to generate the sample resume dataset
├── run.py                          # CLI entry point and environment verifier
├── requirements.txt                # Python backend dependencies
├── .env.example                    # Environment variable template
└── README.md
```

---

## Installation

### Backend

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify environment
python run.py
```

### Frontend

```bash
cd frontend
npm install
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values:

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Linux / macOS
```

`.env.example` content:

```env
# Server configuration
HOST=0.0.0.0
PORT=8000

# LLM Configuration
# Set the provider: gemini | openai | ollama
LLM_PROVIDER=gemini

# Google Gemini (primary)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (optional fallback)
OPENAI_API_KEY=your-openai-api-key-here

# Model name used by the selected provider
# For Gemini: gemini-1.5-flash, gemini-1.5-pro, etc.
# For OpenAI: gpt-4o-mini, gpt-4o, etc.
OPENAI_MODEL=gemini-1.5-flash

# Ollama (optional, no API key required)
# OLLAMA_MODEL=llama3

# Application settings
DEBUG=True
```

**The `.env` file is listed in `.gitignore` and is never committed to the repository.**

---

## Running Locally

### 1. Start the Backend API Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API docs (Swagger UI): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 2. Start the Frontend Dev Server

```bash
cd frontend
npm run dev
```

Open the URL shown in the terminal (typically http://localhost:5173).

---

## CLI Usage

Run the environment verification check (no arguments):
```bash
python run.py
```

Parse and inspect a single resume file:
```bash
python run.py --resume data/resumes/candidate_01.pdf
```

Evaluate a single candidate against a Job Description:
```bash
python run.py --resume data/resumes/candidate_01.pdf \
  --job-description data/job_descriptions/sample_jd.txt
```

List all candidates in a directory with a quick summary table:
```bash
python run.py --all-resumes data/resumes/
```

Calculate NLP similarity scores only (no full scoring):
```bash
python run.py --match data/job_descriptions/sample_jd.txt data/resumes/
```

Run full batch screening and export results:
```bash
python run.py --screen \
  --job-description data/job_descriptions/sample_jd.txt \
  --resumes data/resumes/ \
  --output data/output/
```

---

## API Usage

### GET /health

Returns system health status.

Response:
```json
{"status": "healthy", "timestamp": "2026-08-12T10:04:20.844709", "service": "Resume Screening AI Agent"}
```

### POST /api/screen

Screen resumes supplied as raw text in a JSON body.

Request body:
```json
{
  "job_description": "We need a Python engineer with FastAPI experience.",
  "resumes": [
    {
      "filename": "candidate.txt",
      "content": "John Doe. Skills: Python, FastAPI. 3 years experience."
    }
  ]
}
```

Response: `BatchScreeningResult` JSON.

### POST /api/screen/upload

Screen candidates using multipart form-data file uploads.

Form fields:
- `job_description` (text, optional): Raw JD text.
- `job_description_file` (file, optional): JD as an uploaded file.
- `resumes` (file list, required): One or more resume files.

Accepted file formats: `.pdf`, `.docx`, `.txt`, `.md`
Maximum file size: 5 MB per file.

Response: `BatchScreeningResult` JSON.

### GET /api/results

Returns the latest screening results (from the active session cache or the last exported `data/output/ranked_candidates.json`).

### GET /api/results/{candidate_id}

Returns the full score breakdown and recommendation for a specific candidate by their ID.

---

## Frontend Usage

1. Open http://localhost:5173 in your browser.
2. Paste or type the Job Description text in the left panel.
3. Click the upload area to select candidate resume files (PDF, DOCX, or TXT). MD files are also accepted.
4. Click **Start Screening**. A real-time log panel shows processing steps.
5. Once complete, the dashboard displays:
   - Summary metrics cards (total candidates, top score, average score).
   - A ranked candidates table sorted by final score.
6. Click any row to open the candidate detail sidebar showing:
   - Score breakdown (Skills, Semantic, Experience, Education).
   - Matched and missing required skills.
   - Recruiter reasoning (summary, strengths, gaps, recommendation).
7. Use **Export JSON** or **Export CSV** buttons to download results.

**Note on MD files**: The backend pipeline accepts `.md` files and passes them through the TXT parser. The frontend's file input dialog accepts them by file extension. However, if the uploaded `.md` content does not follow a resume-like structure, extraction quality may be low.

---

## Scoring Method

### Formula

```
Final Score = (Skills Score * 0.45)
            + (Semantic Score * 0.30)
            + (Experience Score * 0.15)
            + (Education Score * 0.10)
```

Scores are rounded to two decimal places.

### 1. Skills Matching (45%)

The skills block is itself subdivided:
- Required skills carry **80%** of the skills block weight.
- Preferred skills carry **20%** of the skills block weight.

```
Skills Score = (Required Match Rate * 0.80) + (Preferred Match Rate * 0.20)
```

Match rate is calculated as the proportion of JD skills found in the candidate's profile, using the centralized skills catalog.

### 2. Semantic Similarity (30%)

The NLP similarity score between the JD embedding and a curated section of the candidate's profile (summary, skills, experience, education text blocks). Scored 0-100.

### 3. Experience Match (15%)

- Candidate meets or exceeds the JD minimum: **100 points**
- Candidate is under-experienced: `(candidate_years / jd_minimum) * 100`
- JD specifies no minimum experience: **100 points**

### 4. Education Match (10%)

- Candidate's degree matches or overlaps JD education requirement: **100 points**
- Candidate has a degree but it does not match: **50 points**
- Candidate has no detected degree: **0 points**

### Design Rationale

The weights above are an **engineering choice made for transparency and reproducibility**, not scientifically optimized values. The challenge provides no labeled recruitment dataset to train or calibrate weights against. A deterministic weighted approach was selected because:

- Every score component is independently auditable.
- Results are reproducible: the same inputs always produce the same output.
- Recruiters can understand exactly why a candidate received a given score.
- The system does not rely on an LLM to determine rankings, eliminating non-determinism from the core evaluation.

---

## NLP Similarity Method

1. **Sentence Embeddings**: The system loads `all-MiniLM-L6-v2` via `sentence-transformers` as a local model. It maps text to a 384-dimensional vector space.
2. **Meaningful Text Selection**: Only the candidate's summary, skills list, work experience, and education sections are embedded. Contact information is excluded.
3. **Cosine Similarity**: The scikit-learn `cosine_similarity` function computes the cosine of the angle between the JD vector and the candidate vector.
4. **Normalization**: The raw cosine value (0 to 1 for text) is multiplied by 100 and rounded to one decimal place to produce the Semantic Score.

The model is cached in memory after first load via a singleton pattern, so subsequent candidates within a batch reuse the same loaded model instance.

---

## LLM Role

**The LLM does not calculate candidate scores and does not determine the numerical ranking.**

The deterministic scoring engine is the sole source of truth. The LLM is invoked only after scoring is complete, and receives the full score breakdown as part of its input.

The reasoning flow is:

```
Candidate profile data
+ Deterministic score breakdown
+ Matched required skills
+ Missing required skills
+ Experience comparison result
+ Education comparison result
        |
        v
  LLM reasoning call
        |
        v
  Structured output:
    - Summary
    - Strengths
    - Gaps
    - Suitability explanation
    - Recommendation (Strong Match / Good Match / Potential Match / Weak Match)
```

The LLM system prompt explicitly instructs the model:
- Use only the supplied candidate data.
- Do not infer or extrapolate missing qualifications.
- Do not hallucinate skills, companies, education, or experience.
- Do not change or recalculate the scores.

If no LLM provider is configured, or if the API call fails, the system automatically falls back to a deterministic rule-based reasoning generator that produces the same structured output without any external API dependency.

### LLM Provider Configuration

The system uses the **OpenAI Python SDK** as a unified client interface for all three providers:

| Provider | `LLM_PROVIDER` value | API Key Variable | Model Variable | Base URL |
|---|---|---|---|---|
| Google Gemini | `gemini` | `GEMINI_API_KEY` | `OPENAI_MODEL` | Google Generative Language API |
| OpenAI | `openai` | `OPENAI_API_KEY` | `OPENAI_MODEL` | OpenAI default |
| Ollama (local) | `ollama` | Not required | `OLLAMA_MODEL` | `http://localhost:11434/v1` |

If `LLM_PROVIDER` is not set, the system auto-detects the provider from the API keys present in `.env`.

---

## Demo

The typical recruiter workflow using the web dashboard:

1. Enter or paste the Job Description into the left panel.
2. Upload 10 or more candidate resumes (PDF, DOCX, or TXT).
3. Click **Start Screening**.
4. The system parses each resume and extracts structured candidate information.
5. Semantic embeddings are computed for the JD and each candidate profile.
6. The deterministic scoring engine calculates a final weighted score for each candidate.
7. Candidates are sorted by final score in descending order.
8. The LLM (or deterministic fallback) generates recruiter reasoning for each candidate.
9. The ranked table and sidebar detail view are displayed.
10. Results can be exported as JSON or CSV.

---

## Sample Input

**Job Description** (`data/job_descriptions/sample_jd.txt`):
```
Junior AI/ML Engineer

Requirements:
- Python, PyTorch, scikit-learn, SQL, PostgreSQL, Git
- Minimum 1 year of experience
- Bachelor or B.Tech in Computer Science

Preferred:
- Docker, Machine Learning, Deep Learning
```

---

## Sample Output

### CSV

Actual output from the included sample dataset (10 candidates against the sample JD):

```text
rank,candidate_id,candidate_name,filename,final_score,semantic_score,skills_score,experience_score,education_score,matched_skills,missing_required_skills,recommendation
1,candidate_01,John Doe,candidate_01.pdf,74.54,71.8,62.22,100.0,100.0,"Docker, Git, PostgreSQL, PyTorch, Python, SQL, scikit-learn","Deep Learning, Machine Learning",Good Match
2,candidate_02,Jane Smith,candidate_02.docx,70.72,72.4,53.33,100.0,100.0,"Deep Learning, Git, PyTorch, Python, SQL, scikit-learn","Docker, Machine Learning, PostgreSQL",Good Match
3,candidate_04,David Miller,candidate_04.pdf,64.95,66.5,44.44,100.0,100.0,"Deep Learning, Git, Machine Learning, Python, scikit-learn","Docker, PostgreSQL, PyTorch, SQL",Good Match
4,candidate_10,Olivia Taylor,candidate_10.pdf,61.68,60.6,52.22,100.0,50.0,"Docker, Git, PyTorch, Python","Deep Learning, Machine Learning, PostgreSQL, SQL, scikit-learn",Good Match
5,candidate_03,Alex Jones,candidate_03.txt,59.89,66.3,33.33,100.0,100.0,"Docker, Git, Python","Deep Learning, Machine Learning, PostgreSQL, PyTorch, SQL, scikit-learn",Potential Match
6,candidate_07,Sophia White,candidate_07.pdf,52.17,73.9,38.89,50.0,50.0,"Docker, Git, PyTorch, Python","Deep Learning, Machine Learning, PostgreSQL, SQL, scikit-learn",Potential Match
7,candidate_08,Robert Black,candidate_08.docx,51.29,59.3,30.0,100.0,50.0,"Docker, Git, SQL","Deep Learning, Machine Learning, PostgreSQL, PyTorch, Python, scikit-learn",Potential Match
8,candidate_09,William Grey,candidate_09.txt,50.85,59.5,17.78,100.0,100.0,"Git, Python","Deep Learning, Docker, Machine Learning, PostgreSQL, PyTorch, SQL, scikit-learn",Potential Match
9,candidate_05,Emily Brown,candidate_05.docx,49.53,55.1,17.78,100.0,100.0,"Git, SQL","Deep Learning, Docker, Machine Learning, PostgreSQL, PyTorch, Python, scikit-learn",Potential Match
10,candidate_06,Michael Green,candidate_06.txt,42.01,66.7,26.67,0.0,100.0,"Python, SQL, scikit-learn","Deep Learning, Docker, Git, Machine Learning, PostgreSQL, PyTorch",Potential Match
```

### CSV Column Descriptions

| Column | Description |
|---|---|
| `rank` | Candidate rank (1 = highest score) |
| `candidate_id` | Internal ID derived from filename stem |
| `candidate_name` | Extracted name or "N/A" |
| `filename` | Original resume filename |
| `final_score` | Weighted final score (0-100) |
| `semantic_score` | NLP cosine similarity score (0-100) |
| `skills_score` | Skills matching score (0-100) |
| `experience_score` | Experience match score (0-100) |
| `education_score` | Education match score (0, 50, or 100) |
| `matched_skills` | Comma-separated list of matched required skills |
| `missing_required_skills` | Comma-separated list of missing required skills |
| `recommendation` | Strong Match / Good Match / Potential Match / Weak Match |

---

## Testing

Run the full test suite:

```bash
python -m pytest
```

Expected output (last verified result):

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
collected 38 items

tests/test_api.py ........                                               [ 21%]
tests/test_screening.py ..............................                   [100%]

======================= 38 passed, 1 warning in 19.98s ========================
```

### Test Coverage

| Area | Tests |
|---|---|
| TXT parser | `test_txt_parser`, `test_empty_txt` |
| PDF parser | `test_pdf_parser`, `test_empty_pdf`, `test_corrupted_pdf` |
| DOCX parser | `test_docx_parser`, `test_empty_docx`, `test_corrupted_docx` |
| File validation | `test_missing_file`, `test_unsupported_extension` |
| Text normalization | `test_normalize_text` |
| Skills extraction | `test_skills_matching` |
| Experience extraction | `test_experience_extraction` |
| Education extraction | `test_education_extraction` |
| JD extraction | `test_job_description_extraction_end_to_end` |
| Candidate extraction | `test_candidate_profile_extraction_end_to_end`, `test_resume_name_extractor`, `test_resume_contact_extractor`, `test_resume_sections_extractor` |
| NLP similarity | `test_similarity_range_and_identical`, `test_multiple_candidates_similarity`, `test_model_loading_caching` |
| Scoring formula | `test_candidate_scoring_perfect`, `test_candidate_scoring_missing_skills`, `test_candidate_scoring_insufficient_exp`, `test_candidate_scoring_missing_education`, `test_candidate_scoring_no_requirements` |
| LLM reasoning | `test_llm_reasoning_success`, `test_llm_reasoning_fallback_on_error` |
| Batch pipeline | `test_screen_candidates_service` (3 resumes, 1 corrupted, verifies JSON/CSV export) |
| API endpoints | `test_api.py`: health, JSON screen, upload screen, results retrieval, candidate lookup, size limits, invalid formats |

---

## Design Tradeoffs

### 1. Local Embeddings vs. API Embeddings

`all-MiniLM-L6-v2` runs locally via `sentence-transformers`. This eliminates API costs and network latency for embedding calls but requires a PyTorch installation and increases initial memory footprint (~90 MB model load).

### 2. Rule-Based Extraction vs. LLM Extraction

Candidate profiles are extracted deterministically using regex and a centralized skills catalog. This is fast, auditable, and fully reproducible. The tradeoff is that non-standard formatting or uncommon skill terminology may not extract correctly. An LLM-based extractor would improve recall but introduce non-determinism into the scoring inputs.

### 3. Sequential Batch Processing

Resumes are processed in a sequential `for` loop. This was chosen for simplicity, debuggability, and to avoid thread-safety issues with the shared model cache. For the 10+ resume scale of this challenge, the processing overhead is minimal (under 8 seconds for 10 resumes). Concurrent processing would be a meaningful improvement at larger scales.

### 4. In-Memory Result Caching

The latest screening result is cached in memory in the FastAPI process. On server restart, the system falls back to loading the last exported `data/output/ranked_candidates.json`. This is sufficient for a single-session tool but would require a database for a multi-user or persistent service.

### 5. Deterministic Scoring Over LLM Scoring

The challenge provides no labeled recruitment dataset. A deterministic weighted formula was chosen over an LLM-scored system to ensure: transparency (every score component is explained), reproducibility (same inputs always produce the same output), and fairness (no LLM hallucination affects numerical ranking).

---

## Limitations

1. **Scanned PDFs**: The PDF parser extracts embedded text streams. Scanned resumes stored as images require an OCR engine (such as Tesseract), which is not included.
2. **Skill Catalog Vocabulary**: Extraction depends on a centralized catalog in `app/extraction/skills.py`. Skills that are not in the catalog will not be extracted or matched.
3. **Name Extraction**: The name extractor uses heuristics based on the first non-contact-info lines of the resume. Unusual formatting may cause incorrect or missing name extraction.
4. **Single Active Session**: The API result cache and the `data/output/` files represent the most recent screening session only. Prior results are overwritten on each run.

---

## Future Improvements

1. **OCR Support**: Integrate Tesseract or a cloud OCR API to handle scanned PDF resumes.
2. **Dynamic Skill Catalog**: Allow runtime skill catalog updates from the JD text or a user-editable file.
3. **Concurrent Processing**: Use `asyncio` or `ThreadPoolExecutor` to process multiple resumes in parallel for larger batches.
4. **Database Persistence**: Replace in-memory and file caching with SQLite or PostgreSQL to retain results across sessions.
5. **Configurable Scoring Weights**: Expose scoring weights as environment variables so recruiters can tune them per role type.

---

## Challenge Requirements Mapping

| Requirement | Implementation | Status |
|---|---|---|
| 1. Accept Job Description | Supported in CLI (`--job-description`), `POST /api/screen`, `POST /api/screen/upload`, and the React dashboard JD input. | Complete |
| 2. Accept 10+ Resumes | Processes 10+ resumes in a single sequential batch via CLI, API endpoints, and the React upload interface. | Complete |
| 3. Parse PDF, DOCX, TXT | Dedicated parsers in `app/parsers/` using PyMuPDF, python-docx, and native file reading. MD files are also accepted via the TXT parser. | Complete |
| 4. Extract Skills, Experience, Education | Extracted in `app/extraction/` via centralized catalog, regex patterns, and degree matching rules. | Complete |
| 5. Compare Resumes with JD via NLP | Implemented in `app/matching/` using `sentence-transformers` (all-MiniLM-L6-v2) and cosine similarity via scikit-learn. | Complete |
| 6. Produce Deterministic Scores | Fixed weighted formula (Skills 45%, Semantic 30%, Experience 15%, Education 10%) in `app/matching/scoring.py`. Same inputs always produce the same output. | Complete |
| 7. Rank Candidates | Sorted in descending order by final score in `app/services/screening_service.py`. | Complete |
| 8. Provide Reasoning | Structured LLM output (summary, strengths, gaps, decision) via Gemini/OpenAI/Ollama in `app/reasoning/explainer.py`, with deterministic fallback. | Complete |
| 9. Export JSON and CSV | Exported to `data/output/ranked_candidates.json` and `ranked_candidates.csv` per run. Also downloadable from the frontend. | Complete |
| 10. Runnable Application | CLI (`run.py`), REST API (`uvicorn app.main:app`), and React frontend (`npm run dev`) are all independently runnable. | Complete |
| 11. Sample Data | 10 synthetic candidate resumes (PDF, DOCX, TXT formats) and one sample JD are included in `data/`. | Complete |
| 12. Tests | 38 pytest tests covering parsers, extractors, similarity, scoring, reasoning fallback, API routes, and batch pipeline. | Complete |
| 13. Clear README | This document. | Complete |
| 14. Document Tradeoffs and Limitations | Covered in the Design Tradeoffs and Limitations sections above. | Complete |
