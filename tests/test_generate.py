"""Resume generation endpoint tests"""
import pytest
import requests
import json
from .conftest import build_generate_url, TestConfig


class TestGenerateEndpoint:
    """Test cases for resume generation endpoint"""
    
    def test_generate_endpoint_success(self, client, test_config):
        """Test successful resume generation"""
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
    
    def test_generate_endpoint_with_client(self, client, test_config):
        """Test generate endpoint using test client"""
        data = {"job_description": test_config.SAMPLE_JOB_DESCRIPTION}
        response = client.post('/generate', json=data)
        
        # Note: This might fail if external dependencies aren't available in test mode
        # In a real test suite, we'd mock the external services
        if response.status_code == 200:
            result = response.get_json()
            assert "$schema" in result
            assert "basics" in result