import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.schemas import BatchScreeningResult

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_screen_json_validation_errors():
    # Empty JD
    response = client.post("/api/screen", json={"job_description": "", "resumes": []})
    assert response.status_code == 400
    
    # Missing resumes
    response = client.post("/api/screen", json={"job_description": "We need python devs.", "resumes": []})
    assert response.status_code == 400

@patch("app.main.screen_candidates")
def test_screen_json_endpoint_success(mock_screen):
    mock_result = BatchScreeningResult(
        job_title="Mock Python Developer",
        total_candidates=1,
        processed_candidates=1,
        failed_candidates=[],
        ranked_candidates=[{
            "rank": 1,
            "candidate_id": "c1",
            "candidate_name": "Test Name",
            "filename": "c1.txt",
            "final_score": 90.0,
            "semantic_score": 90.0,
            "skills_score": 90.0,
            "experience_score": 90.0,
            "education_score": 90.0,
            "matched_skills": ["Python"],
            "missing_required_skills": [],
            "recommendation": "Strong Match"
        }],
        processing_time=0.5
    )
    mock_screen.return_value = mock_result
    
    payload = {
        "job_description": "Need a python coder.",
        "resumes": [
            {"filename": "c1.txt", "content": "I am a Python developer."}
        ]
    }
    
    response = client.post("/api/screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Mock Python Developer"
    assert data["ranked_candidates"][0]["candidate_name"] == "Test Name"
    mock_screen.assert_called_once()

@patch("app.main.screen_candidates")
def test_screen_upload_endpoint_success(mock_screen):
    mock_result = BatchScreeningResult(
        job_title="Mock Python Developer",
        total_candidates=1,
        processed_candidates=1,
        failed_candidates=[],
        ranked_candidates=[{
            "rank": 1,
            "candidate_id": "candidate_01",
            "candidate_name": "John Doe",
            "filename": "candidate_01.txt",
            "final_score": 85.0,
            "semantic_score": 85.0,
            "skills_score": 85.0,
            "experience_score": 85.0,
            "education_score": 85.0,
            "matched_skills": ["Python"],
            "missing_required_skills": [],
            "recommendation": "Good Match"
        }],
        processing_time=0.5
    )
    mock_screen.return_value = mock_result
    
    form_data = {
        "job_description": "We need a python engineer."
    }
    files = [
        ("resumes", ("candidate_01.txt", b"John Doe resume python developer content", "text/plain"))
    ]
    
    response = client.post("/api/screen/upload", data=form_data, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Mock Python Developer"
    assert len(data["ranked_candidates"]) == 1
    mock_screen.assert_called_once()

def test_screen_upload_invalid_extension():
    form_data = {
        "job_description": "Needs dev."
    }
    files = [
        ("resumes", ("virus.exe", b"malicious content", "application/x-msdownload"))
    ]
    response = client.post("/api/screen/upload", data=form_data, files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_screen_upload_empty_file():
    form_data = {
        "job_description": "Needs dev."
    }
    files = [
        ("resumes", ("candidate.txt", b"", "text/plain"))
    ]
    response = client.post("/api/screen/upload", data=form_data, files=files)
    assert response.status_code == 400
    assert "is empty" in response.json()["detail"]

def test_screen_upload_too_large():
    form_data = {
        "job_description": "Needs dev."
    }
    large_content = b"a" * (6 * 1024 * 1024)
    files = [
        ("resumes", ("candidate.txt", large_content, "text/plain"))
    ]
    response = client.post("/api/screen/upload", data=form_data, files=files)
    assert response.status_code == 400
    assert "exceeds maximum size limit" in response.json()["detail"]

@patch("app.main.get_active_results")
def test_results_retrieval(mock_get):
    # Test 404 when no results
    mock_get.return_value = None
    response = client.get("/api/results")
    assert response.status_code == 404
    
    # Test details 404 when no results
    response = client.get("/api/results/c1")
    assert response.status_code == 404
    
    # Setup mock active results
    mock_result = BatchScreeningResult(
        job_title="QA Engineer",
        total_candidates=1,
        processed_candidates=1,
        failed_candidates=[],
        ranked_candidates=[{
            "rank": 1,
            "candidate_id": "cand_qa",
            "candidate_name": "QA tester",
            "filename": "qa.txt",
            "final_score": 90.0,
            "semantic_score": 90.0,
            "skills_score": 90.0,
            "experience_score": 90.0,
            "education_score": 90.0,
            "matched_skills": ["QA"],
            "missing_required_skills": [],
            "recommendation": "Strong Match"
        }],
        processing_time=0.1
    )
    mock_get.return_value = mock_result
    
    # Test results retrieval success
    response = client.get("/api/results")
    assert response.status_code == 200
    assert response.json()["job_title"] == "QA Engineer"
    
    # Test candidate detail success
    response = client.get("/api/results/cand_qa")
    assert response.status_code == 200
    assert response.json()["candidate_name"] == "QA tester"
    
    # Test candidate detail not found
    response = client.get("/api/results/missing_id")
    assert response.status_code == 404
