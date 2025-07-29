"""Unit tests for utility modules"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from resume_generator.utils.file_utils import (
    sanitize_filename, 
    generate_timestamped_filename,
    save_json_file
)
from resume_generator.utils.resume_builder import ResumeBuilder


class TestFileUtils:
    """Test file utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Basic sanitization
        assert sanitize_filename("Hello World!") == "hello-world"
        assert sanitize_filename("Python/Flask & API") == "pythonflask-api"  # Special chars removed first
        assert sanitize_filename("   spaces   ") == "spaces"
        
        # Length limiting
        long_text = "a" * 50
        result = sanitize_filename(long_text, max_length=20)
        assert len(result) == 20
        
        # Empty/None handling
        assert sanitize_filename("") == "resume"
        assert sanitize_filename(None) == "resume"
        assert sanitize_filename("!!!") == "resume"
    
    def test_generate_timestamped_filename(self):
        """Test timestamped filename generation"""
        filename = generate_timestamped_filename("Test Job", "json")
        
        # Should contain timestamp and sanitized job snippet
        assert "test-job" in filename
        assert filename.endswith(".json")
        assert len(filename.split("-")) >= 3  # timestamp parts + job snippet
    
    def test_save_json_file(self):
        """Test JSON file saving"""
        test_data = {"test": "data", "number": 42}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock OUTPUT_DIR to use temp directory
            with patch('resume_generator.utils.file_utils.OUTPUT_DIR', temp_dir):
                filename = "test.json"
                result_path = save_json_file(test_data, filename)
                
                # Verify file was created
                assert os.path.exists(result_path)
                
                # Verify content
                with open(result_path, 'r') as f:
                    loaded_data = json.load(f)
                assert loaded_data == test_data


class TestResumeBuilder:
    """Test resume builder functionality"""
    
    def test_resume_builder_initialization(self):
        """Test ResumeBuilder initialization"""
        builder = ResumeBuilder()
        resume = builder.build()
        
        # Should have all required sections
        required_sections = ["$schema", "basics", "work", "skills", "projects", "education"]
        for section in required_sections:
            assert section in resume
    
    def test_add_content_basics(self):
        """Test adding basics content"""
        builder = ResumeBuilder()
        basics_content = {
            "section": "basics",
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        result = builder.add_content(basics_content)
        assert result is True
        
        resume = builder.build()
        assert resume["basics"] == basics_content
    
    def test_add_content_work(self):
        """Test adding work content"""
        builder = ResumeBuilder()
        work_content = {
            "section": "work",
            "company": "Test Corp",
            "position": "Developer"
        }
        
        result = builder.add_content(work_content)
        assert result is True
        
        resume = builder.build()
        assert len(resume["work"]) == 1
        assert resume["work"][0] == work_content
    
    def test_duplicate_prevention(self):
        """Test duplicate content prevention"""
        builder = ResumeBuilder()
        work_content = {
            "section": "work",
            "company": "Test Corp",
            "position": "Developer"
        }
        
        # Add same content twice
        result1 = builder.add_content(work_content)
        result2 = builder.add_content(work_content)
        
        assert result1 is True
        assert result2 is False  # Should be rejected as duplicate
        
        resume = builder.build()
        assert len(resume["work"]) == 1  # Only one entry
    
    def test_section_limits(self):
        """Test section entry limits"""
        builder = ResumeBuilder()
        
        # Add work entries up to limit
        for i in range(5):  # Assuming MAX_WORK_ENTRIES is 3
            work_content = {
                "section": "work",
                "company": f"Company {i}",
                "position": "Developer"
            }
            builder.add_content(work_content)
        
        resume = builder.build()
        # Should be limited by MAX_WORK_ENTRIES (3)
        assert len(resume["work"]) <= 3
    
    def test_get_stats(self):
        """Test resume statistics"""
        builder = ResumeBuilder()
        
        # Add some content
        builder.add_content({"section": "basics", "name": "John"})
        builder.add_content({"section": "work", "company": "Corp"})
        builder.add_content({"section": "skills", "name": "Python"})
        
        stats = builder.get_stats()
        
        assert stats["has_basics"] is True
        assert stats["work_entries"] == 1
        assert stats["skills_entries"] == 1
        assert stats["total_unique_items"] == 3
    
    def test_add_search_results(self):
        """Test adding search results"""
        builder = ResumeBuilder()
        
        # Mock search results
        mock_results = [
            Mock(payload={"section": "work", "company": "Test Corp"}),
            Mock(payload={"section": "skills", "name": "Python"}),
        ]
        
        added_count = builder.add_search_results(mock_results)
        
        assert added_count == 2
        resume = builder.build()
        assert len(resume["work"]) == 1
        assert len(resume["skills"]) == 1