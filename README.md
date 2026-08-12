# Resume Screening AI Agent

## Overview
The Resume Screening AI Agent is a robust, pipeline-based system designed to parse, extract, match, rank, and explain candidates' resumes against a Job Description. This project was developed as a submission for the Rooman Technologies 24-Hour AI Agent Challenge. It combines a deterministic, transparent scoring engine with an LLM reasoning layer to assist recruiters in evaluating candidates at scale.

## Features
- Document Parsing: Extracts text from PDF, DOCX, and TXT resumes and normalizes whitespace.
- Information Extraction: Utilizes rule-based heuristics and regular expressions to extract name, email, phone number, skills, years of experience, and education history.
- Semantic Alignment: Calculates NLP similarity between the job description and candidate profiles using sentence embeddings.
- Deterministic Scoring: Computes transparent candidate scores based on weighted matching criteria.
- Recruiter Reasoning: Uses Google Gemini (primary) or OpenAI (fallback) to provide candidate summaries, strengths, gaps, and decisions.
- Multi-format Exports: Saves ranked screening results to JSON and CSV formats.
- Interactive Dashboard: Provides a web-based recruitment interface built with React, TypeScript, and Tailwind CSS.
- Failure Resilience: Traps parsing errors on corrupted files individual to ensure the pipeline completes successfully on healthy files.

## Architecture
The system follows a modular, decoupled architecture separating parsers, matchers, score calculation, and LLM text generation:
1. Document Parser Interface: Checks file extension and routes files to format-specific extractors.
2. Extraction Engine: Maps candidate skills against a centralized skills catalogue and runs regular expressions for contact details and experience blocks.
3. Matching Engine: Computes vector representations of candidate content and the job description to calculate cosine similarity.
4. Scoring Engine: Evaluates candidate alignment against minimum experience, skills, and education requirements.
5. Reasoning Layer: Feeds the candidate details and score breakdown to the LLM to generate recruiting explanations.
6. Service Orchestration: Integrates all components in a timed batch processing loop that writes outputs and handles errors.

## Tech Stack
- Backend Framework: FastAPI (Uvicorn server)
- Document Parsing: PyMuPDF (fitz) for PDF, python-docx for DOCX, native file tools for TXT
- Machine Learning & NLP: sentence-transformers (all-MiniLM-L6-v2) for sentence embeddings, scikit-learn for cosine similarity
- Validation & Types: Pydantic v2 and Python type hints
- LLM Integration: OpenAI Python SDK (routing to Google Generative Language API and Ollama)
- Testing: pytest
- Frontend: React, TypeScript, Vite, Tailwind CSS v3, Lucide React icons

## Project Structure
```text
resume-screening-agent/
├── app/                        # Backend source code
│   ├── main.py                 # FastAPI application router
│   ├── parsers/                # PDF, DOCX, and TXT parsers
│   ├── extraction/             # Skills, experience, and education extractors
│   ├── matching/               # NLP similarity and scoring logic
│   ├── reasoning/              # Gemini/OpenAI explainer layer
│   ├── models/                 # Pydantic schemas
│   └── services/               # Screening pipeline coordinator
├── data/                       # Candidate resumes and outputs
│   ├── resumes/                # Input resume files
│   ├── job_descriptions/       # Input Job Description files
│   └── output/                 # JSON and CSV reports
├── frontend/                   # React web application
│   ├── src/                    # React components and pages
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── package.json            # Frontend dependencies
├── tests/                      # Unit and integration test suite
├── run.py                      # CLI runner and environment check
└── requirements.txt            # Python dependencies
```

## Installation

### Backend Setup
1. Clone the repository and navigate to the project root.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Verify the environment setup:
   ```bash
   python run.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the frontend dependencies:
   ```bash
   npm install
   ```

## Environment Variables
Create a file named `.env` in the root directory. Copy the structure below and enter your credentials:
```env
# Server configuration
HOST=0.0.0.0
PORT=8000

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_MODEL=gemini-1.5-flash

# Application settings
DEBUG=True
```

## Running Locally

### 1. Start the Backend API Server
Launch the FastAPI server from the root directory:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs will be available at http://127.0.0.1:8000/docs and health check at http://127.0.0.1:8000/health.

### 2. Start the Frontend Dev Server
In a separate terminal, navigate to the frontend directory and run:
```bash
cd frontend
npm run dev
```
Open http://localhost:5173 (or the terminal-assigned port) in your web browser.

## CLI Usage

### Parse a Single Resume
```bash
python run.py --resume data/resumes/candidate_01.pdf
```

### Summarize Directory of Resumes
```bash
python run.py --all-resumes data/resumes/
```

### Match Resumes via NLP Semantic Similarity
```bash
python run.py --match data/job_descriptions/sample_jd.txt data/resumes/
```

### Full Batch Screening and Output Export
Run screening against a job description, print the ranked table, and write results to JSON/CSV:
```bash
python run.py --screen \
  --job-description data/job_descriptions/sample_jd.txt \
  --resumes data/resumes/ \
  --output data/output/
```

### Detailed Single Candidate Evaluation Report
Runs screening and prints score breakdowns alongside the recruiter reasoning output:
```bash
python run.py --resume data/resumes/candidate_01.pdf \
  --job-description data/job_descriptions/sample_jd.txt
```

## API Usage

### Health Check
- Method: GET
- Path: /health
- Response: `{"status": "healthy", "timestamp": "...", "service": "..."}`

### Screening (JSON Body)
- Method: POST
- Path: /api/screen
- Body:
  ```json
  {
    "job_description": "We need a python engineer.",
    "resumes": [
      {
        "filename": "candidate.txt",
        "content": "I am an engineer with python skills."
      }
    ]
  }
  ```

### Screening (File Upload)
- Method: POST
- Path: /api/screen/upload
- Content-Type: multipart/form-data
- Parameters:
  - `job_description`: Form text (or `job_description_file` upload)
  - `resumes`: List of multiple uploaded files

### Retrieve Latest Results
- Method: GET
- Path: /api/results

### Retrieve Candidate Detail
- Method: GET
- Path: /api/results/{candidate_id}

## Frontend Usage
1. Open http://localhost:5173 in your browser.
2. Paste the Job Description text in the left panel text area.
3. Click on the file area to upload candidate resumes (PDF, DOCX, TXT, or MD).
4. Click Start Screening. The processing overlay displays real-time execution steps.
5. Once completed, the dashboard displays metrics cards and the ranked candidates table.
6. Click any row in the table to display score breakdowns, matched/missing skills, and the recruiter reasoning panel.
7. Click Export JSON or Export CSV to download the screening reports.

## Scoring Method
The candidate score is calculated deterministically using the following weighted components:

### 1. Skills Matching (45%)
- Divides skills into Required Skills and Preferred Skills extracted from the Job Description.
- Required Skills hold higher weight. Missing a required skill reduces the skills score.
- Score is calculated by checking the presence of these skills in the candidate profile using the skill catalogue.

### 2. NLP Semantic Similarity (30%)
- Compares meaningful text sections of the candidate profile against the full Job Description.
- Focuses on summary, skills list, experience details, and education, ignoring contact information.

### 3. Experience Match (15%)
- Compares candidate's extracted years of experience against the Job Description minimum requirement.
- Full credit (100%) is awarded if the candidate meets or exceeds the minimum requirement. Partial credit is scaled for under-experienced candidates.

### 4. Education Match (10%)
- Checks candidate's degree qualifications against the Job Description education requirements.
- Full credit is awarded for exact match or higher degree. Partial credit is given for adjacent technical degrees.

### Exact Formula
```text
Final Score = (Skills Score * 0.45) + (Semantic Score * 0.30) + (Experience Score * 0.15) + (Education Score * 0.10)
```
Scores are rounded to two decimal places.

## NLP Similarity Method
To measure semantic alignment:
1. **Sentence Embeddings**: The system uses the local `sentence-transformers` model `all-MiniLM-L6-v2` to map text into a 384-dimensional vector space.
2. **Cosine Similarity**: Measures the cosine of the angle between the Job Description embedding vector and the candidate's resume embedding vector:
   ```text
   Similarity = (A . B) / (||A|| ||B||)
   ```
3. **Normalization**: The raw similarity score (usually between -1 and 1) is scaled to a `0-100` range to form the Semantic Similarity Score.

## LLM Role
**Important**: The LLM (Google Gemini or OpenAI) does not calculate candidate scores or determine their numerical ranking.
The scoring engine remains the source of truth, ensuring transparency and repeatability. The LLM is used only to synthesize candidate summaries, strengths, gaps, and decision logs based on the scoring details.

## Sample Input
A Job Description (e.g. Junior AI/ML Engineer) requiring:
- Skills: Python, PyTorch, scikit-learn, SQL, PostgreSQL, Git
- Experience: 1 year minimum
- Education: Bachelor or B.Tech in Computer Science

## Sample Output
CSV Row Format:
```text
rank,candidate_id,candidate_name,filename,final_score,semantic_score,skills_score,experience_score,education_score,matched_skills,missing_required_skills,recommendation
1,candidate_01,John Doe,candidate_01.pdf,74.54,71.80,62.22,100.00,100.00,"Docker, Git, PostgreSQL, PyTorch, Python, SQL, scikit-learn","Deep Learning, Machine Learning",Good Match
```

## Testing
Run backend unit and API integration tests:
```bash
python -m pytest
```
Output results:
- 38 passed tests checking parsers, info extraction, NLP matchers, scoring, reasoning template fallbacks, API routing, size limit validations, and session caching.

## Design Tradeoffs
1. **Local vs API Embeddings**: Using a local `sentence-transformers` model eliminates API costs and network latency for embeddings but increases initial memory usage and requires a PyTorch installation.
2. **Rule-Based Extraction vs LLM Extraction**: Extracting candidate profiles deterministically is extremely fast and auditable, but can fail to capture custom formatted contact details or custom-named skills compared to an LLM extractor.
3. **In-Memory Caching**: Caching latest screening results in-memory allows fast REST API queries but means screening state resets when the backend server restarts (mitigated by falling back to loading the last exported JSON file).

## Limitations
1. **Format Specifics**: Scanned PDF resumes (saved as images) cannot be parsed without an OCR engine (which is out of scope for the lightweight parser interface).
2. **Skill Catalog Limits**: Extraction depends on a centralized catalog. Highly customized or emerging skill names might not register unless added to the vocabulary.
3. **Single Line Resumes**: Extremely brief or single-line resumes might not contain enough context to produce a high semantic similarity score.

## Future Improvements
1. **OCR Integration**: Integrate Tesseract or PyPDF2 OCR module to parse scanned image resumes.
2. **Dynamic Skill Catalog**: Allow adding and extending skills directly from the frontend or job description context at runtime.
3. **Database Persistence**: Replace in-memory and JSON file caching with a SQL database (like SQLite or PostgreSQL) to persist candidate profiles and evaluation history.

## Challenge Requirements Mapping

The implementation maps to the Rooman Technologies challenge requirements as follows:

| Challenge Requirement | Implementation Detail | Status |
|---|---|---|
| 1. Accept Job Description | Supported in CLI (`--job-description`), FastAPI upload endpoint, and React dashboard JD input box. | Completed |
| 2. Accept 10+ Resumes | Processed 10+ resumes concurrently in CLI, API batch endpoints, and React drag-and-drop lists. | Completed |
| 3. Parse PDF, DOCX, TXT | Dedicated parsers in `app/parsers/` using PyMuPDF and python-docx. | Completed |
| 4. Extract Skills, Exp, Edu | Extracted in `app/extraction/` via centralized catalog, regex, and degree rules. | Completed |
| 5. Compare with JD | Handled in `app/matching/` using sentence-transformers and cosine similarity. | Completed |
| 6. Deterministic Score | Weighted scoring formula (Skills 45%, Semantic 30%, Exp 15%, Edu 10%) in `app/matching/scoring.py`. | Completed |
| 7. Rank Candidates | Sorted in descending order by final score in `screening_service.py`. | Completed |
| 8. Provide Reasoning | Structured LLM output (summary, strengths, gaps) using Gemini/OpenAI in `app/reasoning/explainer.py`. | Completed |
| 9. Export JSON/CSV | Standard exports saved to `data/output/` and downloadable on the frontend. | Completed |
| 10. Runnable README | Complete installation, environment setup, and verification guide documented. | Completed |
