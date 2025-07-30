"""Tests for resume replace functionality"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.resume_generator.services.resume_replace_service import ResumeReplaceService


class TestResumeReplaceService:
    """Test cases for ResumeReplaceService"""
    
    @pytest.fixture
    def replace_service(self):
        """Create replace service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_replace_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_replace_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_replace_service.APIClient'):
            service = ResumeReplaceService()
            return service
    
    def test_parse_content_to_json_resume_markdown(self, replace_service):
        """Test parsing markdown content to JSON Resume"""
        markdown_content = """
        # Alice Chen - Senior Full-Stack Developer
        
        ## Contact
        - Email: alice.chen@gmail.com
        - Phone: +1-555-0987
        
        ## Experience
        
        **TechCorp** (2021-2024)
        - Senior Full-Stack Developer
        - React/Node.js for scalable web apps
        - Team leadership in microservices architecture
        
        ## Skills
        - Languages: JavaScript, Python, TypeScript
        - Frontend: React, Vue.js, HTML5, CSS3
        
        ## Education
        - Bachelor in Computer Science, NYU (2015-2019)
        """
        
        # Mock AI response
        mock_ai_response = {
            "basics": {
                "name": "Alice Chen",
                "label": "Senior Full-Stack Developer",
                "email": "alice.chen@gmail.com",
                "phone": "+1-555-0987"
            },
            "work": [{
                "name": "TechCorp",
                "position": "Senior Full-Stack Developer",
                "startDate": "2021-01-01",
                "endDate": "2024-12-31",
                "highlights": ["React/Node.js for scalable web apps", "Team leadership in microservices architecture"]
            }],
            "skills": [{
                "name": "Languages",
                "keywords": ["JavaScript", "Python", "TypeScript"]
            }],
            "education": [{
                "institution": "NYU",
                "area": "Computer Science",
                "studyType": "Bachelor",
                "startDate": "2015-01-01",
                "endDate": "2019-12-31"
            }]
        }
        
        replace_service.ai_client.query.return_value = json.dumps(mock_ai_response)
        
        result = replace_service._parse_content_to_json_resume(markdown_content)
        
        assert result["basics"]["name"] == "Alice Chen"
        assert result["basics"]["email"] == "alice.chen@gmail.com"
        assert len(result["work"]) == 1
        assert result["work"][0]["name"] == "TechCorp"
        assert len(result["skills"]) == 1
        assert len(result["education"]) == 1
    
    def test_parse_content_to_json_resume_plaintext(self, replace_service):
        """Test parsing plain text content to JSON Resume"""
        text_content = """
        John Smith is a software engineer with 5 years of experience.
        He worked at Google from 2019 to 2024 as a Senior Software Engineer.
        His skills include Python, JavaScript, and React.
        He has a BS in Computer Science from MIT.
        Contact: john@gmail.com, +1-555-1234
        """
        
        mock_ai_response = {
            "basics": {
                "name": "John Smith",
                "email": "john@gmail.com",
                "phone": "+1-555-1234",
                "summary": "Software engineer with 5 years of experience"
            },
            "work": [{
                "name": "Google",
                "position": "Senior Software Engineer",
                "startDate": "2019-01-01",
                "endDate": "2024-12-31"
            }],
            "skills": [{
                "name": "Programming",
                "keywords": ["Python", "JavaScript", "React"]
            }],
            "education": [{
                "institution": "MIT",
                "area": "Computer Science",
                "studyType": "Bachelor"
            }]
        }
        
        replace_service.ai_client.query.return_value = json.dumps(mock_ai_response)
        
        result = replace_service._parse_content_to_json_resume(text_content)
        
        assert result["basics"]["name"] == "John Smith"
        assert result["work"][0]["name"] == "Google"
        assert "Python" in result["skills"][0]["keywords"]
    
    def test_parse_content_invalid_json_response(self, replace_service):
        """Test handling of invalid JSON from AI"""
        content = "Some resume content"
        
        # AI returns invalid JSON
        replace_service.ai_client.query.return_value = "This is not JSON"
        
        with pytest.raises(ValueError, match="AI could not generate valid JSON structure"):
            replace_service._parse_content_to_json_resume(content)
    
    def test_parse_content_malformed_json(self, replace_service):
        """Test handling of malformed JSON from AI"""
        content = "Some resume content"
        
        # AI returns malformed JSON
        replace_service.ai_client.query.return_value = '{"name": "John", invalid}'
        
        with pytest.raises(ValueError, match="AI generated invalid JSON"):
            replace_service._parse_content_to_json_resume(content)
    
    def test_validate_json_resume_schema_valid(self, replace_service):
        """Test validation of valid JSON Resume"""
        valid_resume = {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "work": [{
                "name": "Tech Corp",
                "position": "Engineer"
            }],
            "skills": [{
                "name": "Programming",
                "keywords": ["Python"]
            }]
        }
        
        # Should not raise any exception
        replace_service._validate_json_resume_schema(valid_resume)
        
        # Verify structure is preserved
        assert valid_resume["basics"]["name"] == "John Doe"
        assert len(valid_resume["work"]) == 1
        assert len(valid_resume["skills"]) == 1
    
    def test_validate_json_resume_schema_missing_basics(self, replace_service):
        """Test validation fails when basics section is missing"""
        invalid_resume = {
            "work": [{"name": "Tech Corp"}]
        }
        
        with pytest.raises(ValueError, match="Resume must contain a 'basics' section"):
            replace_service._validate_json_resume_schema(invalid_resume)
    
    def test_validate_json_resume_schema_missing_name(self, replace_service):
        """Test validation fails when name is missing from basics"""
        invalid_resume = {
            "basics": {
                "email": "john@example.com"
            }
        }
        
        with pytest.raises(ValueError, match="Resume must contain a name in basics section"):
            replace_service._validate_json_resume_schema(invalid_resume)
    
    def test_validate_json_resume_schema_invalid_work_structure(self, replace_service):
        """Test validation fails for invalid work structure"""
        invalid_resume = {
            "basics": {"name": "John Doe"},
            "work": "not an array"
        }
        
        with pytest.raises(ValueError, match="Section 'work' must be an array"):
            replace_service._validate_json_resume_schema(invalid_resume)
    
    def test_validate_json_resume_schema_work_missing_name(self, replace_service):
        """Test validation fails for work entry without name/company"""
        invalid_resume = {
            "basics": {"name": "John Doe"},
            "work": [{
                "position": "Engineer"
                # Missing name/company
            }]
        }
        
        with pytest.raises(ValueError, match="Work entry 0 must have a name or company"):
            replace_service._validate_json_resume_schema(invalid_resume)
    
    def test_validate_json_resume_schema_removes_empty_sections(self, replace_service):
        """Test validation removes empty sections"""
        resume_with_empty = {
            "basics": {"name": "John Doe"},
            "work": [],
            "skills": [{"name": "Programming", "keywords": ["Python"]}],
            "education": []
        }
        
        replace_service._validate_json_resume_schema(resume_with_empty)
        
        # Empty sections should be removed
        assert "work" not in resume_with_empty
        assert "education" not in resume_with_empty
        # Non-empty sections should remain
        assert "skills" in resume_with_empty
        assert len(resume_with_empty["skills"]) == 1
    
    def test_clear_existing_resume(self, replace_service):
        """Test clearing existing resume entries"""
        # Mock existing points
        mock_points = [Mock(id=1), Mock(id=2), Mock(id=3)]
        replace_service.qdrant_client.scroll.return_value = (mock_points, None)
        
        replace_service._clear_existing_resume()
        
        # Verify scroll was called to get existing points
        replace_service.qdrant_client.scroll.assert_called_once_with(
            collection_name=replace_service.collection_name,
            limit=10000
        )
        
        # Verify delete was called with correct IDs
        replace_service.qdrant_client.delete.assert_called_once_with(
            collection_name=replace_service.collection_name,
            points_selector=[1, 2, 3]
        )
    
    def test_clear_existing_resume_no_points(self, replace_service):
        """Test clearing when no existing points"""
        # Mock no existing points
        replace_service.qdrant_client.scroll.return_value = ([], None)
        
        replace_service._clear_existing_resume()
        
        # Verify scroll was called
        replace_service.qdrant_client.scroll.assert_called_once()
        
        # Verify delete was not called since no points exist
        replace_service.qdrant_client.delete.assert_not_called()
    
    def test_insert_new_resume(self, replace_service):
        """Test inserting new resume data"""
        resume_data = {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "work": [{
                "name": "Tech Corp",
                "position": "Engineer"
            }],
            "skills": [{
                "name": "Programming",
                "keywords": ["Python"]
            }]
        }
        
        # Mock vector client
        replace_service.vector_client.generate_embedding.return_value = [0.1] * 384
        
        entries_added = replace_service._insert_new_resume(resume_data)
        
        # Should add 3 entries: 1 basics + 1 work + 1 skills
        assert entries_added == 3
        
        # Verify upsert was called 3 times
        assert replace_service.qdrant_client.upsert.call_count == 3
    
    def test_entry_to_search_text(self, replace_service):
        """Test conversion of entry to searchable text"""
        entry = {
            "name": "TechCorp",
            "position": "Senior Engineer",
            "summary": "Built scalable APIs",
            "highlights": ["Python", "Flask", "API development"],
            "location": {
                "city": "San Francisco",
                "region": "CA"
            },
            "irrelevant_field": "should be ignored"
        }
        
        result = replace_service._entry_to_search_text(entry)
        
        assert "TechCorp" in result
        assert "Senior Engineer" in result
        assert "Built scalable APIs" in result
        assert "Python" in result
        assert "Flask" in result
        assert "San Francisco" in result
        assert "CA" in result
        assert "irrelevant_field" not in result
    
    def test_replace_resume_success(self, replace_service):
        """Test successful complete resume replacement"""
        content = "Alice Chen - Senior Developer at TechCorp"
        
        # Mock AI parsing
        mock_resume = {
            "basics": {
                "name": "Alice Chen",
                "label": "Senior Developer"
            },
            "work": [{
                "name": "TechCorp",
                "position": "Senior Developer"
            }]
        }
        
        with patch.object(replace_service, '_parse_content_to_json_resume') as mock_parse, \
             patch.object(replace_service, '_validate_json_resume_schema') as mock_validate, \
             patch.object(replace_service, '_clear_existing_resume') as mock_clear, \
             patch.object(replace_service, '_insert_new_resume') as mock_insert:
            
            mock_parse.return_value = mock_resume
            mock_insert.return_value = 2
            
            result = replace_service.replace_resume(content)
            
            assert result["success"]
            assert result["entries_added"] == 2
            assert result["resume"] == mock_resume
            assert "2 entries" in result["message"]
            
            # Verify all steps were called
            mock_parse.assert_called_once_with(content)
            mock_validate.assert_called_once_with(mock_resume)
            mock_clear.assert_called_once()
            mock_insert.assert_called_once_with(mock_resume)
    
    def test_replace_resume_validation_error(self, replace_service):
        """Test replace with validation error"""
        content = "Invalid content"
        
        with patch.object(replace_service, '_parse_content_to_json_resume') as mock_parse, \
             patch.object(replace_service, '_validate_json_resume_schema') as mock_validate:
            
            mock_parse.return_value = {"invalid": "resume"}
            mock_validate.side_effect = ValueError("Missing name")
            
            result = replace_service.replace_resume(content)
            
            assert not result["success"]
            assert result["error_type"] == "validation_error"
            assert "Missing name" in result["error"]
            assert "Invalid input" in result["message"]
    
    def test_replace_resume_internal_error(self, replace_service):
        """Test replace with internal error"""
        content = "Some content"
        
        with patch.object(replace_service, '_parse_content_to_json_resume') as mock_parse:
            mock_parse.side_effect = Exception("AI service error")
            
            result = replace_service.replace_resume(content)
            
            assert not result["success"]
            assert result["error_type"] == "internal_error"
            assert "AI service error" in result["error"]
            assert "Internal server error" in result["message"]


class TestResumeReplaceAPI:
    """Test cases for resume replace API endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.resume_generator.server import create_app
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_replace_resume_missing_content(self, client):
        """Test API with missing content"""
        response = client.post('/resume/replace', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Content is required" in data["error"]
    
    def test_replace_resume_empty_content(self, client):
        """Test API with empty content"""
        response = client.post('/resume/replace', json={"content": ""})
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Content cannot be empty" in data["error"]
    
    def test_replace_resume_whitespace_only_content(self, client):
        """Test API with whitespace-only content"""
        response = client.post('/resume/replace', json={"content": "   \n\t  "})
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Content cannot be empty" in data["error"]
    
    @patch('src.resume_generator.services.resume_replace_service.ResumeReplaceService')
    def test_replace_resume_success(self, mock_service_class, client):
        """Test successful resume replacement"""
        # Mock service instance and response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.replace_resume.return_value = {
            "success": True,
            "message": "Resume completely replaced with 5 entries",
            "entries_added": 5,
            "resume": {
                "basics": {"name": "Alice Chen"},
                "work": [{"name": "TechCorp"}]
            }
        }
        
        response = client.post('/resume/replace', json={
            "content": "Alice Chen - Senior Developer at TechCorp with 5 years experience"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["entries_added"] == 5
        assert "Alice Chen" in data["resume"]["basics"]["name"]
        
        # Verify service was called with correct content
        mock_service.replace_resume.assert_called_once_with(
            "Alice Chen - Senior Developer at TechCorp with 5 years experience"
        )
    
    @patch('src.resume_generator.services.resume_replace_service.ResumeReplaceService')
    def test_replace_resume_validation_error(self, mock_service_class, client):
        """Test API with validation error (422)"""
        # Mock service instance and validation error response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.replace_resume.return_value = {
            "success": False,
            "error": "Resume must contain a name in basics section",
            "error_type": "validation_error",
            "message": "Invalid input - could not parse into valid resume"
        }
        
        response = client.post('/resume/replace', json={
            "content": "Invalid resume content without name"
        })
        
        assert response.status_code == 422  # Unprocessable Entity
        data = response.get_json()
        assert not data["success"]
        assert "Resume must contain a name" in data["error"]
        assert data["error_type"] == "validation_error"
    
    @patch('src.resume_generator.services.resume_replace_service.ResumeReplaceService')
    def test_replace_resume_internal_error(self, mock_service_class, client):
        """Test API with internal error (400)"""
        # Mock service instance and internal error response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.replace_resume.return_value = {
            "success": False,
            "error": "AI service unavailable",
            "error_type": "internal_error",
            "message": "Internal server error during resume replacement"
        }
        
        response = client.post('/resume/replace', json={
            "content": "Some content"
        })
        
        assert response.status_code == 400  # Bad Request
        data = response.get_json()
        assert not data["success"]
        assert "AI service unavailable" in data["error"]
        assert data["error_type"] == "internal_error"
    
    @patch('src.resume_generator.services.resume_replace_service.ResumeReplaceService')
    def test_replace_resume_service_exception(self, mock_service_class, client):
        """Test API when service raises exception"""
        # Mock service to raise exception
        mock_service_class.side_effect = Exception("Service initialization failed")
        
        response = client.post('/resume/replace', json={
            "content": "Some content"
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert not data["success"]
        assert "Service initialization failed" in data["error"]
        assert data["error_type"] == "internal_error"


class TestComplexReplaceScenarios:
    """Test complex real-world replacement scenarios"""
    
    @pytest.fixture
    def replace_service(self):
        """Create replace service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_replace_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_replace_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_replace_service.APIClient'):
            service = ResumeReplaceService()
            return service
    
    def test_comprehensive_markdown_resume(self, replace_service):
        """Test replacing with comprehensive markdown resume"""
        markdown_resume = """
        # Sarah Johnson
        **Senior Data Scientist** | sarah.johnson@email.com | +1-555-0199
        
        ## Summary
        Experienced data scientist with 8+ years in machine learning and analytics
        
        ## Experience
        
        ### Meta (2020-2024)
        **Senior Data Scientist**
        - Led ML initiatives for recommendation systems
        - Improved user engagement by 25% through A/B testing
        - Managed team of 6 data scientists
        
        ### Google (2018-2020)
        **Data Scientist**
        - Built predictive models for ad targeting
        - Reduced computation costs by 40%
        
        ## Skills
        - **Programming**: Python, R, SQL, Scala
        - **ML/AI**: TensorFlow, PyTorch, Scikit-learn
        - **Big Data**: Spark, Hadoop, Kafka
        - **Cloud**: AWS, GCP, Azure
        
        ## Education
        - **PhD Computer Science**, Stanford University (2014-2018)
        - **MS Statistics**, UC Berkeley (2012-2014)
        
        ## Projects
        - **RecSys 2023**: Published paper on neural collaborative filtering
        - **DataCorp**: Consulting project for fraud detection system
        """
        
        expected_response = {
            "basics": {
                "name": "Sarah Johnson",
                "label": "Senior Data Scientist",
                "email": "sarah.johnson@email.com",
                "phone": "+1-555-0199",
                "summary": "Experienced data scientist with 8+ years in machine learning and analytics"
            },
            "work": [
                {
                    "name": "Meta",
                    "position": "Senior Data Scientist",
                    "startDate": "2020-01-01",
                    "endDate": "2024-12-31",
                    "highlights": [
                        "Led ML initiatives for recommendation systems",
                        "Improved user engagement by 25% through A/B testing",
                        "Managed team of 6 data scientists"
                    ]
                },
                {
                    "name": "Google",
                    "position": "Data Scientist",
                    "startDate": "2018-01-01",
                    "endDate": "2020-12-31",
                    "highlights": [
                        "Built predictive models for ad targeting",
                        "Reduced computation costs by 40%"
                    ]
                }
            ],
            "skills": [
                {"name": "Programming", "keywords": ["Python", "R", "SQL", "Scala"]},
                {"name": "ML/AI", "keywords": ["TensorFlow", "PyTorch", "Scikit-learn"]},
                {"name": "Big Data", "keywords": ["Spark", "Hadoop", "Kafka"]},
                {"name": "Cloud", "keywords": ["AWS", "GCP", "Azure"]}
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "area": "Computer Science",
                    "studyType": "PhD",
                    "startDate": "2014-01-01",
                    "endDate": "2018-12-31"
                },
                {
                    "institution": "UC Berkeley",
                    "area": "Statistics",
                    "studyType": "MS",
                    "startDate": "2012-01-01",
                    "endDate": "2014-12-31"
                }
            ],
            "projects": [
                {
                    "name": "RecSys 2023",
                    "description": "Published paper on neural collaborative filtering"
                },
                {
                    "name": "DataCorp",
                    "description": "Consulting project for fraud detection system"
                }
            ]
        }
        
        replace_service.ai_client.query.return_value = json.dumps(expected_response)
        replace_service.vector_client.generate_embedding.return_value = [0.1] * 384
        replace_service.qdrant_client.scroll.return_value = ([], None)
        
        result = replace_service.replace_resume(markdown_resume)
        
        assert result["success"]
        assert result["resume"]["basics"]["name"] == "Sarah Johnson"
        assert len(result["resume"]["work"]) == 2
        assert len(result["resume"]["skills"]) == 4
        assert len(result["resume"]["education"]) == 2
        assert len(result["resume"]["projects"]) == 2
    
    def test_minimal_text_resume(self, replace_service):
        """Test replacing with minimal text resume"""
        minimal_text = "John Doe, software engineer at Apple, john@apple.com"
        
        minimal_response = {
            "basics": {
                "name": "John Doe",
                "email": "john@apple.com",
                "label": "Software Engineer"
            },
            "work": [{
                "name": "Apple",
                "position": "Software Engineer"
            }]
        }
        
        replace_service.ai_client.query.return_value = json.dumps(minimal_response)
        replace_service.vector_client.generate_embedding.return_value = [0.1] * 384
        replace_service.qdrant_client.scroll.return_value = ([], None)
        
        result = replace_service.replace_resume(minimal_text)
        
        assert result["success"]
        assert result["resume"]["basics"]["name"] == "John Doe"
        assert result["resume"]["work"][0]["name"] == "Apple"
    
    def test_json_resume_input(self, replace_service):
        """Test replacing with JSON Resume input"""
        json_resume = {
            "basics": {
                "name": "Maria Garcia",
                "email": "maria@example.com",
                "label": "UX Designer"
            },
            "work": [{
                "name": "Design Studio",
                "position": "Senior UX Designer",
                "startDate": "2022-01-01"
            }],
            "skills": [{
                "name": "Design Tools",
                "keywords": ["Figma", "Sketch", "Adobe XD"]
            }]
        }
        
        # AI should parse and potentially clean/validate the JSON
        replace_service.ai_client.query.return_value = json.dumps(json_resume)
        replace_service.vector_client.generate_embedding.return_value = [0.1] * 384
        replace_service.qdrant_client.scroll.return_value = ([], None)
        
        result = replace_service.replace_resume(json.dumps(json_resume))
        
        assert result["success"]
        assert result["resume"]["basics"]["name"] == "Maria Garcia"
        assert result["resume"]["work"][0]["name"] == "Design Studio"
        assert "Figma" in result["resume"]["skills"][0]["keywords"]