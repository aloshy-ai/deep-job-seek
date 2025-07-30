"""Resume generation endpoint tests"""
import pytest
import requests
import json
from unittest.mock import patch
from .conftest import build_generate_url, TestConfig


class TestGenerateEndpoint:
    """Test cases for resume generation endpoint"""
    
    @patch('src.resume_generator.core.create_tailored_resume')
    def test_generate_endpoint_success(self, mock_create_resume, client, test_config):
        """Test successful resume generation"""
        # Mock the resume generation to return a valid JSON Resume
        mock_resume = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0123"
            },
            "work": [{
                "name": "Tech Company",
                "position": "Software Engineer",
                "startDate": "2020-01-01"
            }],
            "skills": [{
                "name": "Programming Languages",
                "keywords": ["Python", "JavaScript"]
            }],
            "projects": [{
                "name": "Sample Project",
                "description": "A test project"
            }],
            "education": [{
                "institution": "University",
                "area": "Computer Science",
                "studyType": "Bachelor"
            }],
            "_metadata": {
                "generated_at": "2024-01-01T00:00:00Z",
                "output_file": "test_resume.json"
            }
        }
        mock_create_resume.return_value = mock_resume
        
        data = {"job_description": test_config.SAMPLE_JOB_DESCRIPTION}
        response = client.post('/generate', json=data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        result = response.get_json()
        
        # Validate JSON Resume schema structure
        assert "$schema" in result, "Missing JSON Resume schema"
        assert "basics" in result, "Missing basics section"
        assert "work" in result, "Missing work section"
        assert "skills" in result, "Missing skills section"
        assert "projects" in result, "Missing projects section"
        assert "education" in result, "Missing education section"
        
        # Validate metadata
        if "_metadata" in result:
            metadata = result["_metadata"]
            assert "generated_at" in metadata, "Missing generation timestamp"
            assert "output_file" in metadata, "Missing output file path"
        
        # Verify the mock was called with correct argument
        mock_create_resume.assert_called_once_with(test_config.SAMPLE_JOB_DESCRIPTION)
    
    def test_generate_endpoint_missing_job_description(self, client):
        """Test error handling for missing job description"""
        data = {}  # Missing job_description
        response = client.post('/generate', json=data)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        result = response.get_json()
        assert "error" in result, "Missing error message"
        assert "required" in result["error"].lower(), "Error should mention required field"
    
    def test_generate_endpoint_empty_job_description(self, client):
        """Test error handling for empty job description"""
        data = {"job_description": ""}
        response = client.post('/generate', json=data)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    @patch('src.resume_generator.core.create_tailored_resume')
    def test_generate_endpoint_with_client(self, mock_create_resume, client, test_config):
        """Test generate endpoint using test client"""
        # Mock the resume generation
        mock_resume = {
            "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
            "basics": {"name": "Test User"}
        }
        mock_create_resume.return_value = mock_resume
        
        data = {"job_description": test_config.SAMPLE_JOB_DESCRIPTION}
        response = client.post('/generate', json=data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert "$schema" in result
        assert "basics" in result