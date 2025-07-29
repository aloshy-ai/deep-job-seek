"""Health endpoint tests"""
import pytest
import requests
from .conftest import build_health_url
from tests.config import TestConfig


class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_endpoint_responds(self, client):
        """Test that health endpoint responds successfully"""
        response = client.get('/health')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.get_json()
        assert "status" in data, "Response missing 'status' field"
        assert "message" in data, "Response missing 'message' field"
        assert data["status"] == "healthy", f"Expected healthy status, got {data['status']}"
    
    def test_health_endpoint_with_client(self, client):
        """Test health endpoint using test client"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "message" in data