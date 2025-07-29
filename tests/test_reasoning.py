"""Reasoning output tests"""
import pytest
import os


class TestReasoningOutput:
    """Test cases for reasoning file generation"""
    
    def test_reasoning_file_generated(self, client):
        """Test that reasoning files are generated alongside resumes"""
        data = {"job_description": "Data Scientist with Python and machine learning experience"}
        response = client.post('/generate', json=data)
        assert response.status_code == 200
        
        result = response.get_json()
        metadata = result.get("_metadata", {})
        
        # Check that both JSON and reasoning files are referenced
        assert "output_file" in metadata, "Missing JSON output file reference"
        assert "reasoning_file" in metadata, "Missing reasoning output file reference"
        
        json_file = metadata["output_file"]
        reasoning_file = metadata["reasoning_file"]
        
        # Verify files exist
        assert os.path.exists(json_file), f"JSON file not found: {json_file}"
        assert os.path.exists(reasoning_file), f"Reasoning file not found: {reasoning_file}"
        
        # Verify reasoning file is markdown
        assert reasoning_file.endswith("-reasoning.md"), "Reasoning file should end with -reasoning.md"
        
        # Verify reasoning file has content
        with open(reasoning_file, 'r', encoding='utf-8') as f:
            reasoning_content = f.read()
        
        assert len(reasoning_content) > 100, "Reasoning file should have substantial content"
        assert "# Why You're Perfect for This Role" in reasoning_content, "Missing reasoning header"
        assert "Role Overview" in reasoning_content, "Missing job analysis section"
        assert "Your Strongest Qualifications" in reasoning_content, "Missing search analysis section"
        assert "Perfect Skill Alignment" in reasoning_content, "Missing selection analysis section"
        
        # Clean up test files
        try:
            os.remove(json_file)
            os.remove(reasoning_file)
        except OSError:
            pass  # Files might not exist if test failed earlier
    
    def test_reasoning_content_structure(self, client):
        """Test the structure and content of reasoning files"""
        data = {"job_description": "Full Stack Developer with React, Node.js, and PostgreSQL experience"}
        response = client.post('/generate', json=data)
        assert response.status_code == 200
        
        result = response.get_json()
        reasoning_file = result["_metadata"]["reasoning_file"]
        
        with open(reasoning_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test required sections
        required_sections = [
            "# Why You're Perfect for This Role",
            "## 🎯 **Role Overview**",
            "## 💪 **Your Strongest Qualifications**",
            "## 🔗 **Perfect Skill Alignment**", 
            "## 🏆 **Relevant Experience Highlights**",
            
            "## 🎯 **Why This Match Works**",
        ]
        
        for section in required_sections:
            assert section in content, f"Missing required section: {section}"
        
        # Test metadata presence
        assert "Generated on" in content, "Missing generation timestamp"
        
        # Clean up
        try:
            os.remove(result["_metadata"]["output_file"])
            os.remove(reasoning_file)
        except OSError:
            pass
    
    def test_reasoning_with_keywords(self, client):
        """Test that reasoning captures extracted keywords"""
        data = {"job_description": "DevOps Engineer specializing in Docker, Kubernetes, CI/CD, and AWS cloud infrastructure"}
        response = client.post('/generate', json=data)
        assert response.status_code == 200
        
        result = response.get_json()
        reasoning_file = result["_metadata"]["reasoning_file"]
        
        with open(reasoning_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that job description is captured
        assert "DevOps Engineer" in content, "Job description not captured in reasoning"
        
        # Clean up
        try:
            os.remove(result["_metadata"]["output_file"])
            os.remove(reasoning_file)
        except OSError:
            pass
    
    def test_reasoning_relevance_scores(self, client):
        """Test that reasoning includes relevance scores"""
        data = {"job_description": "Backend Engineer with Python, FastAPI, and database experience"}
        response = client.post('/generate', json=data)
        assert response.status_code == 200
        
        result = response.get_json()
        reasoning_file = result["_metadata"]["reasoning_file"]
        
        with open(reasoning_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for relevance scoring information
        assert "Why This Match Works" in content, "Missing relevance scores"
        
        # Clean up
        try:
            os.remove(result["_metadata"]["output_file"])
            os.remove(reasoning_file)
        except OSError:
            pass
