"""Tests for resume update functionality"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.resume_generator.services.resume_update_service import ResumeUpdateService


class TestResumeUpdateService:
    """Test cases for ResumeUpdateService"""
    
    @pytest.fixture
    def update_service(self):
        """Create update service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_update_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_update_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_update_service.APIClient'):
            service = ResumeUpdateService()
            return service
    
    def test_detect_content_type_json(self, update_service):
        """Test JSON content type detection"""
        json_content = '{"name": "John Doe", "email": "john@example.com"}'
        result = update_service._detect_content_type(json_content)
        assert result == "json"
    
    def test_detect_content_type_markdown(self, update_service):
        """Test markdown content type detection"""
        markdown_content = """
        # John Doe
        ## Experience
        - Software Engineer at Tech Corp
        """
        result = update_service._detect_content_type(markdown_content)
        assert result == "markdown"
    
    def test_detect_content_type_text(self, update_service):
        """Test plain text content type detection"""
        text_content = "John Doe, Software Engineer with 5 years experience in Python"
        result = update_service._detect_content_type(text_content)
        assert result == "text"
    
    def test_parse_json_content_basic(self, update_service):
        """Test parsing basic JSON resume content"""
        json_content = """
        {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0123"
            },
            "work": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Engineer",
                    "startDate": "2021-01-01",
                    "endDate": "2024-01-01"
                }
            ]
        }
        """
        
        result = update_service._parse_json_content(json_content)
        
        assert "basics" in result
        assert "work" in result
        assert result["basics"][0]["name"] == "John Doe"
        assert result["work"][0]["company"] == "Tech Corp"
    
    def test_parse_json_content_invalid(self, update_service):
        """Test handling of invalid JSON"""
        invalid_json = '{"name": "John Doe", invalid}'
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            update_service._parse_json_content(invalid_json)
    
    def test_entry_to_search_text(self, update_service):
        """Test conversion of entry to search text"""
        entry = {
            "company": "Tech Corp",
            "position": "Senior Engineer",
            "summary": "Built scalable APIs",
            "highlights": ["Python", "Flask", "API development"],
            "irrelevant_field": "should be ignored"
        }
        
        result = update_service._entry_to_search_text(entry)
        
        assert "Tech Corp" in result
        assert "Senior Engineer" in result
        assert "Built scalable APIs" in result
        assert "Python" in result
        assert "Flask" in result
    
    def test_merge_entries_highlights(self, update_service):
        """Test merging entries with highlights"""
        existing = {
            "company": "Tech Corp",
            "position": "Engineer",
            "highlights": ["Python", "Flask"]
        }
        
        new = {
            "company": "Tech Corp",
            "position": "Senior Engineer",
            "highlights": ["API development", "Python"]  # Python is duplicate
        }
        
        result = update_service._merge_entries(existing, new)
        
        assert result["position"] == "Senior Engineer"  # Updated with new value
        assert set(result["highlights"]) == {"Python", "Flask", "API development"}  # Merged without duplicates
    
    def test_merge_entries_text_fields(self, update_service):
        """Test merging text fields with length preference"""
        existing = {
            "summary": "Built APIs"
        }
        
        new = {
            "summary": "Built scalable and maintainable REST APIs using Flask and Python"
        }
        
        result = update_service._merge_entries(existing, new)
        
        # Should prefer longer, more detailed summary
        assert result["summary"] == "Built scalable and maintainable REST APIs using Flask and Python"
    
    @patch.object(ResumeUpdateService, '_find_similar_entries')
    @patch.object(ResumeUpdateService, '_merge_entries')
    @patch.object(ResumeUpdateService, '_update_qdrant_entry')
    def test_merge_entry_with_similar(self, mock_update, mock_merge, mock_find, update_service):
        """Test merging entry when similar entry exists"""
        # Mock similar entry found
        similar_entry = {
            "id": 123,
            "score": 0.8,
            "payload": {"company": "Tech Corp", "position": "Engineer"}
        }
        mock_find.return_value = [similar_entry]
        
        # Mock merge result
        merged_entry = {"company": "Tech Corp", "position": "Senior Engineer"}
        mock_merge.return_value = merged_entry
        
        new_entry = {"company": "Tech Corp", "position": "Senior Engineer"}
        
        result = update_service._merge_entry("work", new_entry)
        
        assert not result["is_new"]
        assert result["action"] == "merged"
        assert result["entry_id"] == 123
        
        mock_merge.assert_called_once_with(similar_entry["payload"], new_entry)
        mock_update.assert_called_once_with(123, "work", merged_entry)
    
    @patch.object(ResumeUpdateService, '_find_similar_entries')
    @patch.object(ResumeUpdateService, '_add_new_entry')
    def test_merge_entry_no_similar(self, mock_add, mock_find, update_service):
        """Test merging entry when no similar entry exists"""
        # No similar entries found
        mock_find.return_value = []
        
        # Mock add new entry
        add_result = {"is_new": True, "entry_id": 456, "action": "added"}
        mock_add.return_value = add_result
        
        new_entry = {"company": "New Corp", "position": "Engineer"}
        
        result = update_service._merge_entry("work", new_entry)
        
        assert result == add_result
        mock_add.assert_called_once_with("work", new_entry)
    
    @patch.object(ResumeUpdateService, '_get_next_id')
    @patch.object(ResumeUpdateService, '_add_qdrant_entry')
    def test_add_new_entry(self, mock_add_qdrant, mock_next_id, update_service):
        """Test adding a new entry"""
        mock_next_id.return_value = 789
        
        entry = {"company": "New Corp", "position": "Engineer"}
        
        result = update_service._add_new_entry("work", entry)
        
        assert result["is_new"]
        assert result["entry_id"] == 789
        assert result["action"] == "added"
        assert result["entry"] == entry
        
        mock_add_qdrant.assert_called_once_with(789, "work", entry)
    
    def test_get_next_id_with_existing_points(self, update_service):
        """Test getting next ID when points exist"""
        # Mock existing points with IDs
        mock_points = [
            Mock(id=1),
            Mock(id=5),
            Mock(id=3)
        ]
        
        update_service.qdrant_client.scroll.return_value = (mock_points, None)
        
        result = update_service._get_next_id()
        
        assert result == 6  # max(1,5,3) + 1
    
    def test_get_next_id_no_points(self, update_service):
        """Test getting next ID when no points exist"""
        update_service.qdrant_client.scroll.return_value = ([], None)
        
        result = update_service._get_next_id()
        
        assert result == 1  # Default first ID


class TestResumeUpdateAPI:
    """Test cases for resume update API endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.resume_generator.server import create_app
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_update_resume_missing_content(self, client):
        """Test API with missing content"""
        response = client.post('/resume/update', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Content is required" in data["error"]
    
    def test_update_resume_invalid_update_mode(self, client):
        """Test API with invalid update mode"""
        response = client.post('/resume/update', json={
            "content": "Some content",
            "update_mode": "invalid_mode"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid update_mode" in data["error"]
    
    def test_update_resume_invalid_content_type(self, client):
        """Test API with invalid content type"""
        response = client.post('/resume/update', json={
            "content": "Some content",
            "content_type": "invalid_type"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid content_type" in data["error"]
    
    @patch('src.resume_generator.services.resume_update_service.ResumeUpdateService')
    def test_update_resume_success(self, mock_service_class, client):
        """Test successful resume update"""
        # Mock service instance and response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.update_resume.return_value = {
            "success": True,
            "message": "Updated 1 new and 2 existing entries",
            "results": {
                "updated_sections": ["work"],
                "new_entries": 1,
                "modified_entries": 2
            }
        }
        
        response = client.post('/resume/update', json={
            "content": "New job experience at Amazing Corp",
            "update_mode": "merge",
            "content_type": "text",
            "section_hint": "work"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert "Updated 1 new and 2 existing entries" in data["message"]
        
        # Verify service was called with correct parameters
        mock_service.update_resume.assert_called_once_with(
            content="New job experience at Amazing Corp",
            update_mode="merge",
            content_type="text",
            section_hint="work"
        )
    
    @patch('src.resume_generator.services.resume_update_service.ResumeUpdateService')
    def test_update_resume_service_error(self, mock_service_class, client):
        """Test API when service returns error"""
        # Mock service instance and error response
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.update_resume.return_value = {
            "success": False,
            "error": "Failed to parse content",
            "message": "Failed to update resume"
        }
        
        response = client.post('/resume/update', json={
            "content": "Invalid content"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]
        assert "Failed to parse content" in data["error"]
    
    @patch('src.resume_generator.services.resume_update_service.ResumeUpdateService')
    def test_update_resume_internal_error(self, mock_service_class, client):
        """Test API when service raises exception"""
        # Mock service to raise exception
        mock_service_class.side_effect = Exception("Internal error")
        
        response = client.post('/resume/update', json={
            "content": "Some content"
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert not data["success"]
        assert "Internal error" in data["error"]


class TestComplexScenarios:
    """Test complex real-world update scenarios"""
    
    @pytest.fixture
    def update_service(self):
        """Create update service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_update_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_update_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_update_service.APIClient'):
            service = ResumeUpdateService()
            return service
    
    def test_full_resume_json_update(self, update_service):
        """Test updating with complete JSON resume"""
        json_resume = {
            "basics": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1-555-9876",
                "summary": "Experienced data scientist"
            },
            "work": [
                {
                    "company": "Data Corp",
                    "position": "Data Scientist",
                    "startDate": "2022-01-01",
                    "summary": "Built ML models for customer prediction"
                }
            ],
            "skills": [
                {
                    "name": "Programming",
                    "keywords": ["Python", "R", "SQL"]
                }
            ]
        }
        
        with patch.object(update_service, '_update_section') as mock_update:
            mock_update.return_value = {"new_count": 1, "modified_count": 0, "entries": []}
            
            result = update_service.update_resume(
                content=json.dumps(json_resume),
                update_mode="merge",
                content_type="json"
            )
            
            assert result["success"]
            # Should call _update_section for each section
            assert mock_update.call_count == 3  # basics, work, skills
    
    def test_partial_experience_text_update(self, update_service):
        """Test updating with partial text experience"""
        text_content = """
        I recently started working at Innovation Labs as a Senior ML Engineer
        since March 2024. My main responsibilities include developing deep learning
        models for computer vision and leading a team of 4 junior engineers.
        """
        
        # Mock AI parsing to return structured data
        with patch.object(update_service, '_parse_text_content') as mock_parse:
            mock_parse.return_value = {
                "work": [{
                    "company": "Innovation Labs",
                    "position": "Senior ML Engineer",
                    "startDate": "2024-03-01",
                    "summary": "Developing deep learning models for computer vision",
                    "highlights": ["Deep learning", "Computer vision", "Team leadership"]
                }]
            }
            
            with patch.object(update_service, '_update_section') as mock_update:
                mock_update.return_value = {"new_count": 1, "modified_count": 0, "entries": []}
                
                result = update_service.update_resume(
                    content=text_content,
                    update_mode="merge",
                    content_type="text",
                    section_hint="work"
                )
                
                assert result["success"]
                mock_parse.assert_called_once_with(text_content, "work")
    
    def test_skill_addition_append_mode(self, update_service):
        """Test adding new skills in append mode"""
        skills_content = {
            "skills": [{
                "name": "Cloud Platforms",
                "keywords": ["AWS", "Azure", "GCP", "Kubernetes"]
            }]
        }
        
        with patch.object(update_service, '_add_new_entry') as mock_add:
            mock_add.return_value = {"is_new": True, "entry_id": 100, "action": "added"}
            
            result = update_service.update_resume(
                content=json.dumps(skills_content),
                update_mode="append",
                content_type="json"
            )
            
            assert result["success"]
            mock_add.assert_called_once()


class TestNaturalLanguageInstructions:
    """Test natural language instruction processing"""
    
    @pytest.fixture
    def update_service(self):
        """Create update service with mocked dependencies"""
        with patch('src.resume_generator.services.resume_update_service.QdrantClient'), \
             patch('src.resume_generator.services.resume_update_service.VectorSearchClient'), \
             patch('src.resume_generator.services.resume_update_service.APIClient'):
            service = ResumeUpdateService()
            return service
    
    def test_is_natural_language_instruction_change_pattern(self, update_service):
        """Test detection of change instruction patterns"""
        instructions = [
            "Change my email to aloshy@gmail.com",
            "Update my phone number to +1-555-9999",
            "Replace Google with Alphabet Inc",
            "Correct my name to John Smith",
            "Fix the company name to Microsoft",
            "Set my position to Senior Engineer",
            "Modify the start date to 2023-01-01"
        ]
        
        for instruction in instructions:
            assert update_service._is_natural_language_instruction(instruction), f"Failed to detect: {instruction}"
    
    def test_is_natural_language_instruction_correction_pattern(self, update_service):
        """Test detection of correction patterns"""
        corrections = [
            "The organization name is not Gogle, it's Google",
            "My email is not john@old.com, it should be john@new.com",
            "The position should be Senior Engineer",
            "Company name is not Microsooft, it's Microsoft"
        ]
        
        for correction in corrections:
            assert update_service._is_natural_language_instruction(correction), f"Failed to detect: {correction}"
    
    def test_is_natural_language_instruction_false_positives(self, update_service):
        """Test that resume content is not detected as instructions"""
        resume_content = [
            "Senior Software Engineer with 5 years experience",
            "Built scalable APIs using Python and Flask",
            "Led a team of 4 developers at Tech Corp",
            '{"name": "John Doe", "email": "john@example.com"}',
            "# John Doe\n## Experience\n- Software Engineer"
        ]
        
        for content in resume_content:
            assert not update_service._is_natural_language_instruction(content), f"False positive: {content}"
    
    @patch.object(ResumeUpdateService, '_apply_instruction_update')
    def test_parse_instruction_content_integration(self, mock_apply, update_service):
        """Test integration of instruction parsing with update logic"""
        # Mock AI response for instruction parsing
        mock_ai_response = '''
        {
            "instruction_type": "field_update",
            "section": "basics",
            "field": "email",
            "old_value": "old@example.com",
            "new_value": "aloshy@gmail.com",
            "search_context": "contact information"
        }
        '''
        update_service.ai_client.complete.return_value = mock_ai_response
        
        # Mock apply instruction update
        mock_result = {
            "is_new": False,
            "action": "field_update_applied",
            "field": "email",
            "old_value": "old@example.com",
            "new_value": "aloshy@gmail.com"
        }
        mock_apply.return_value = mock_result
        
        result = update_service.update_resume(
            content="Change my email to aloshy@gmail.com",
            update_mode="merge"
        )
        
        assert result["success"]
        mock_apply.assert_called_once()
    
    def test_find_instruction_target_exact_match(self, update_service):
        """Test finding target entry with exact value match"""
        # Mock search results
        mock_results = [
            Mock(
                id=123,
                score=0.9,
                payload={"email": "old@example.com", "name": "John Doe", "section": "basics"}
            ),
            Mock(
                id=124, 
                score=0.7,
                payload={"email": "other@example.com", "name": "Jane Doe", "section": "basics"}
            )
        ]
        
        update_service.vector_client.search_with_filter.return_value = mock_results
        
        results = update_service._find_instruction_target(
            section="basics",
            field="email", 
            old_value="old@example.com",
            search_context=""
        )
        
        # Should return entry with exact email match first
        assert len(results) == 1
        assert results[0].payload["email"] == "old@example.com"
    
    def test_apply_instruction_update_field_change(self, update_service):
        """Test applying field update instruction"""
        # Mock finding target entry
        mock_target = Mock(
            id=123,
            payload={"email": "old@example.com", "name": "John Doe", "section": "basics"}
        )
        
        with patch.object(update_service, '_find_instruction_target') as mock_find:
            mock_find.return_value = [mock_target]
            
            with patch.object(update_service, '_update_qdrant_entry') as mock_update:
                instruction_entry = {
                    "_instruction_type": "field_update",
                    "_field": "email",
                    "_old_value": "old@example.com",
                    "email": "aloshy@gmail.com"
                }
                
                result = update_service._apply_instruction_update("basics", instruction_entry)
                
                assert not result["is_new"]
                assert result["action"] == "field_update_applied"
                assert result["field"] == "email"
                assert result["new_value"] == "aloshy@gmail.com"
                
                # Verify Qdrant update was called with updated entry
                mock_update.assert_called_once()
                updated_entry = mock_update.call_args[0][2]  # Third argument
                assert updated_entry["email"] == "aloshy@gmail.com"
    
    def test_apply_instruction_update_correction(self, update_service):
        """Test applying correction instruction"""
        mock_target = Mock(
            id=456,
            payload={"company": "Gogle", "position": "Engineer", "section": "work"}
        )
        
        with patch.object(update_service, '_find_instruction_target') as mock_find:
            mock_find.return_value = [mock_target]
            
            with patch.object(update_service, '_update_qdrant_entry') as mock_update:
                instruction_entry = {
                    "_instruction_type": "correction",
                    "_field": "company",
                    "_old_value": "Gogle",
                    "company": "Google"
                }
                
                result = update_service._apply_instruction_update("work", instruction_entry)
                
                assert result["action"] == "correction_applied"
                assert result["old_value"] == "Gogle"
                assert result["new_value"] == "Google"
                
                # Verify correction was applied
                updated_entry = mock_update.call_args[0][2]
                assert updated_entry["company"] == "Google"
    
    def test_apply_instruction_update_no_target_found(self, update_service):
        """Test instruction when no target entry is found"""
        with patch.object(update_service, '_find_instruction_target') as mock_find:
            mock_find.return_value = []  # No matches found
            
            instruction_entry = {
                "_instruction_type": "field_update",
                "_field": "email",
                "_old_value": "nonexistent@example.com",
                "email": "new@example.com"
            }
            
            result = update_service._apply_instruction_update("basics", instruction_entry)
            
            assert not result["is_new"]
            assert result["action"] == "no_match_found"
            assert "Could not find entry to update" in result["error"]