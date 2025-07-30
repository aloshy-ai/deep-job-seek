"""Tests for resume retrieval functionality"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.resume_generator.services.resume_retrieval_service import ResumeRetrievalService


class TestResumeRetrievalService:
    """Test cases for ResumeRetrievalService"""
    
    @pytest.fixture
    def retrieval_service(self):
        """Create retrieval service with mocked Qdrant client"""
        with patch('src.resume_generator.services.resume_retrieval_service.QdrantClient'):
            service = ResumeRetrievalService()
            return service
    
    @pytest.fixture
    def sample_resume_entries(self):
        """Sample resume entries from Qdrant"""
        return [
            {
                "section": "basics",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "summary": "Senior Software Engineer with 5 years experience",
                "_point_id": 1
            },
            {
                "section": "work",
                "company": "Google",
                "position": "Senior Software Engineer",
                "startDate": "2021-01-01",
                "endDate": "2024-01-01",
                "summary": "Built scalable search infrastructure",
                "highlights": ["Python", "Kubernetes", "Search algorithms"],
                "_point_id": 2
            },
            {
                "section": "work",
                "company": "Meta",
                "position": "Software Engineer",
                "startDate": "2019-06-01",
                "endDate": "2020-12-31",
                "summary": "Developed social media features",
                "highlights": ["React", "GraphQL", "Mobile optimization"],
                "_point_id": 3
            },
            {
                "section": "education",
                "institution": "Stanford University",
                "area": "Computer Science",
                "studyType": "Bachelor",
                "endDate": "2019-05-01",
                "gpa": "3.8",
                "_point_id": 4
            },
            {
                "section": "skills",
                "name": "Programming Languages",
                "keywords": ["Python", "JavaScript", "Go"],
                "_point_id": 5
            },
            {
                "section": "skills",
                "name": "Technologies",
                "keywords": ["Kubernetes", "Docker", "React"],
                "_point_id": 6
            },
            {
                "section": "projects",
                "name": "Deep Job Seek",
                "description": "AI-powered resume generation system",
                "highlights": ["Flask", "Qdrant", "OpenAI"],
                "url": "https://github.com/example/resume-api",
                "_point_id": 7
            }
        ]
    
    def test_get_complete_resume_success(self, retrieval_service, sample_resume_entries):
        """Test successful retrieval of complete resume"""
        # Mock Qdrant scroll response
        mock_points = []
        for entry in sample_resume_entries:
            mock_point = Mock()
            mock_point.payload = {k: v for k, v in entry.items() if k != '_point_id'}
            mock_point.id = entry['_point_id']
            mock_points.append(mock_point)
        
        retrieval_service.qdrant_client.scroll.return_value = (mock_points, None)
        
        result = retrieval_service.get_complete_resume()
        
        assert result["success"] is True
        assert "Retrieved complete resume" in result["message"]
        assert result["entry_count"] == 7
        assert "resume" in result
        
        resume = result["resume"]
        
        # Check basics section
        assert "basics" in resume
        assert resume["basics"]["name"] == "John Doe"
        assert resume["basics"]["email"] == "john.doe@example.com"
        
        # Check work section
        assert "work" in resume
        assert len(resume["work"]) == 2
        # Should be sorted by start date (most recent first)
        assert resume["work"][0]["company"] == "Google"  # 2021 start
        assert resume["work"][1]["company"] == "Meta"    # 2019 start
        
        # Check education section
        assert "education" in resume
        assert len(resume["education"]) == 1
        assert resume["education"][0]["institution"] == "Stanford University"
        
        # Check skills section
        assert "skills" in resume
        assert len(resume["skills"]) == 2
        
        # Check projects section
        assert "projects" in resume
        assert len(resume["projects"]) == 1
        assert resume["projects"][0]["name"] == "Deep Job Seek"
    
    def test_get_complete_resume_empty_collection(self, retrieval_service):
        """Test retrieval when collection is empty"""
        retrieval_service.qdrant_client.scroll.return_value = ([], None)
        
        result = retrieval_service.get_complete_resume()
        
        assert result["success"] is False
        assert "No resume data found" in result["message"]
        assert "resume" in result
        assert "basics" in result["resume"]  # Should return empty template
    
    def test_process_work_section_sorting(self, retrieval_service):
        """Test that work entries are sorted by start date"""
        work_entries = [
            {
                "company": "Company A",
                "position": "Engineer",
                "startDate": "2020-01-01",
                "section": "work"
            },
            {
                "company": "Company B", 
                "position": "Senior Engineer",
                "startDate": "2022-06-01",
                "section": "work"
            },
            {
                "company": "Company C",
                "position": "Staff Engineer", 
                "startDate": "2021-03-01",
                "section": "work"
            }
        ]
        
        processed = retrieval_service._process_work_section(work_entries)
        
        # Should be sorted by start date, most recent first
        assert len(processed) == 3
        assert processed[0]["company"] == "Company B"  # 2022
        assert processed[1]["company"] == "Company C"  # 2021
        assert processed[2]["company"] == "Company A"  # 2020
    
    def test_process_skills_section_keyword_handling(self, retrieval_service):
        """Test skills section handles different keyword formats"""
        skills_entries = [
            {
                "name": "Programming",
                "keywords": ["Python", "JavaScript", "Python"],  # Has duplicate
                "section": "skills"
            },
            {
                "name": "Databases",
                "keywords": "PostgreSQL, MongoDB, Redis",  # Comma-separated string
                "section": "skills"
            }
        ]
        
        processed = retrieval_service._process_skills_section(skills_entries)
        
        assert len(processed) == 2
        
        # First skill should have duplicates removed
        programming_skill = processed[0]
        assert programming_skill["name"] == "Programming"
        assert len(programming_skill["keywords"]) == 2  # Duplicate removed
        assert "Python" in programming_skill["keywords"]
        assert "JavaScript" in programming_skill["keywords"]
        
        # Second skill should parse comma-separated string
        db_skill = processed[1]
        assert db_skill["name"] == "Databases"
        assert isinstance(db_skill["keywords"], list)
        assert len(db_skill["keywords"]) == 3
        assert "PostgreSQL" in db_skill["keywords"]
    
    def test_get_resume_summary(self, retrieval_service, sample_resume_entries):
        """Test resume summary generation"""
        # Mock Qdrant response
        mock_points = []
        for entry in sample_resume_entries:
            mock_point = Mock()
            mock_point.payload = {k: v for k, v in entry.items() if k != '_point_id'}
            mock_point.id = entry['_point_id']
            mock_points.append(mock_point)
        
        retrieval_service.qdrant_client.scroll.return_value = (mock_points, None)
        
        result = retrieval_service.get_resume_summary()
        
        assert result["success"] is True
        assert "summary" in result
        
        summary = result["summary"]
        assert summary["total_entries"] == 7
        assert "sections" in summary
        
        # Check section summaries
        sections = summary["sections"]
        
        # Basics section
        assert "basics" in sections
        assert sections["basics"]["count"] == 1
        assert sections["basics"]["info"]["name"] == "John Doe"
        
        # Work section
        assert "work" in sections
        assert sections["work"]["count"] == 2
        assert "Google" in sections["work"]["companies"]
        assert "Meta" in sections["work"]["companies"]
        
        # Skills section
        assert "skills" in sections
        assert sections["skills"]["count"] == 2
        assert len(sections["skills"]["top_skills"]) > 0
    
    def test_format_pretty(self, retrieval_service):
        """Test pretty formatting of resume"""
        resume = {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com",
                "summary": "Software Engineer"
            },
            "work": [
                {
                    "company": "Google",
                    "position": "Engineer",
                    "startDate": "2021-01-01",
                    "endDate": "2024-01-01",
                    "highlights": ["Python", "Kubernetes"]
                }
            ],
            "skills": [
                {
                    "name": "Programming",
                    "keywords": ["Python", "JavaScript"]
                }
            ]
        }
        
        formatted = retrieval_service._format_pretty(resume)
        
        assert "=== RESUME ===" in formatted
        assert "Name: John Doe" in formatted
        assert "Email: john@example.com" in formatted
        assert "=== WORK EXPERIENCE ===" in formatted
        assert "Engineer at Google" in formatted
        assert "=== SKILLS ===" in formatted
        assert "Programming: Python, JavaScript" in formatted


class TestResumeRetrievalAPI:
    """Test cases for resume retrieval API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.resume_generator.server import create_app
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @patch('src.resume_generator.api.routes.ResumeRetrievalService')
    def test_get_resume_success(self, mock_service_class, client):
        """Test successful resume retrieval via API"""
        # Mock service response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_complete_resume.return_value = {
            "success": True,
            "message": "Retrieved complete resume with 5 entries",
            "resume": {
                "basics": {"name": "John Doe"},
                "work": [],
                "skills": []
            }
        }
        
        response = client.get('/resume')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "resume" in data
        
        # Verify service was called with correct format
        mock_service.get_complete_resume.assert_called_once_with(format_type='json')
    
    @patch('src.resume_generator.api.routes.ResumeRetrievalService')
    def test_get_resume_pretty_format(self, mock_service_class, client):
        """Test resume retrieval with pretty format"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_complete_resume.return_value = {
            "success": True,
            "resume": "=== RESUME ===\nName: John Doe"
        }
        
        response = client.get('/resume?format=pretty')
        
        assert response.status_code == 200
        mock_service.get_complete_resume.assert_called_once_with(format_type='pretty')
    
    def test_get_resume_invalid_format(self, client):
        """Test resume retrieval with invalid format parameter"""
        response = client.get('/resume?format=invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid format" in data["error"]
    
    @patch('src.resume_generator.api.routes.ResumeRetrievalService')
    def test_get_resume_not_found(self, mock_service_class, client):
        """Test resume retrieval when no data exists"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_complete_resume.return_value = {
            "success": False,
            "message": "No resume data found"
        }
        
        response = client.get('/resume')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
    
    @patch('src.resume_generator.api.routes.ResumeRetrievalService')
    def test_get_resume_summary_success(self, mock_service_class, client):
        """Test successful resume summary retrieval"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_resume_summary.return_value = {
            "success": True,
            "summary": {
                "total_entries": 5,
                "sections": {
                    "work": {"count": 2},
                    "skills": {"count": 3}
                }
            }
        }
        
        response = client.get('/resume/summary')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "summary" in data
        assert data["summary"]["total_entries"] == 5
    
    @patch('src.resume_generator.api.routes.ResumeRetrievalService')
    def test_get_resume_internal_error(self, mock_service_class, client):
        """Test API when service raises exception"""
        mock_service_class.side_effect = Exception("Database error")
        
        response = client.get('/resume')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert "Database error" in data["error"]