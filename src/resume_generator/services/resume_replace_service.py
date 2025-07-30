"""Complete resume replacement service with AI parsing and JSON Resume schema validation"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from ..config import QDRANT_URL, QDRANT_COLLECTION_NAME
from ..utils.vector_search import VectorSearchClient
from ..utils.api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/resume_replace.log'
)
logger = logging.getLogger(__name__)


class ResumeReplaceService:
    """Service for complete resume replacement with AI parsing"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.vector_client = VectorSearchClient()
        self.ai_client = APIClient()
        self.collection_name = QDRANT_COLLECTION_NAME
        logger.info("ResumeReplaceService initialized")
    
    def replace_resume(self, content: str) -> Dict[str, Any]:
        """
        Replace entire resume with new content parsed by AI
        
        Args:
            content: Any text input (markdown, plaintext, JSON, etc.)
            
        Returns:
            Dict with replacement results or error
        """
        try:
            logger.info(f"Starting complete resume replacement with {len(content)} characters of content")
            
            # Step 1: Parse content using AI to extract JSON Resume
            parsed_resume = self._parse_content_to_json_resume(content)
            
            # Step 2: Validate against JSON Resume schema
            self._validate_json_resume_schema(parsed_resume)
            
            # Step 3: Clear existing resume data
            self._clear_existing_resume()
            
            # Step 4: Insert new resume data
            entries_added = self._insert_new_resume(parsed_resume)
            
            logger.info(f"Resume replacement completed: {entries_added} entries added")
            
            return {
                "success": True,
                "message": f"Resume completely replaced with {entries_added} entries",
                "resume": parsed_resume,
                "entries_added": entries_added,
                "timestamp": datetime.now().isoformat()
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation_error",
                "message": "Invalid input - could not parse into valid resume"
            }
        except Exception as e:
            logger.error(f"Resume replacement failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "internal_error",
                "message": "Internal server error during resume replacement"
            }
    
    def _parse_content_to_json_resume(self, content: str) -> Dict[str, Any]:
        """Use AI to parse any content into JSON Resume format"""
        
        prompt = f"""
        Parse the following content into a complete JSON Resume following the JSON Resume schema.
        
        Requirements:
        1. Extract ALL available information from the content
        2. Structure it according to JSON Resume schema (https://jsonresume.org/schema/)
        3. Include these sections if data is available: basics, work, education, skills, projects, volunteer, awards, publications, languages, interests, references
        4. For basics section, extract: name, label, email, phone, url, summary, location (with address, postalCode, city, countryCode, region)
        5. For work section, extract: name, position, url, startDate, endDate, summary, highlights
        6. For education section, extract: institution, url, area, studyType, startDate, endDate, score, courses
        7. For skills section, extract: name, level, keywords
        8. For projects section, extract: name, description, highlights, keywords, startDate, endDate, url, roles, entity, type
        9. Use proper date formats (YYYY-MM-DD or YYYY-MM)
        10. Return ONLY valid JSON, no other text
        11. If critical information is missing (like name), indicate what's missing
        
        Content to parse:
        {content}
        
        JSON Resume:
        """
        
        try:
            # Use more tokens for resume parsing (JSON resumes can be long)
            response = self.ai_client.query(prompt, max_tokens=2000, temperature=0.3)
            logger.info(f"AI response length: {len(response)} characters")
            
            # Handle case where response might be a dict (from reasoning models)
            if isinstance(response, dict):
                response_text = response.get("content", str(response))
            else:
                response_text = response
            
            # Extract JSON from AI response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error(f"No JSON found in AI response: {response_text[:200]}...")
                raise ValueError("AI could not generate valid JSON structure")
            
            json_str = response_text[json_start:json_end]
            parsed_resume = json.loads(json_str)
            
            logger.info(f"Successfully parsed resume with sections: {list(parsed_resume.keys())}")
            return parsed_resume
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            raise ValueError(f"AI generated invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"AI parsing failed: {str(e)}")
            raise ValueError(f"Could not parse content into resume format: {str(e)}")
    
    def _validate_json_resume_schema(self, resume: Dict[str, Any]) -> None:
        """Validate that parsed resume meets minimum JSON Resume requirements"""
        
        # Check for required basics section
        if "basics" not in resume:
            raise ValueError("Resume must contain a 'basics' section")
        
        basics = resume["basics"]
        
        # Check for minimum required fields in basics
        if not basics.get("name"):
            raise ValueError("Resume must contain a name in basics section")
        
        # Validate structure of main sections (only if they exist and have content)
        array_sections = ["work", "education", "skills", "projects", "volunteer", "awards", "publications", "languages", "interests", "references"]
        
        for section in array_sections:
            if section in resume and resume[section]:  # Only validate if section exists and has content
                if not isinstance(resume[section], list):
                    raise ValueError(f"Section '{section}' must be an array")
                # Remove empty entries
                resume[section] = [entry for entry in resume[section] if entry]
        
        # Remove empty sections entirely
        sections_to_remove = [section for section in array_sections if section in resume and not resume[section]]
        for section in sections_to_remove:
            del resume[section]
        
        # Validate work experience structure if present
        if "work" in resume:
            for i, work in enumerate(resume["work"]):
                if not isinstance(work, dict):
                    raise ValueError(f"Work entry {i} must be an object")
                if not work.get("name") and not work.get("company"):
                    raise ValueError(f"Work entry {i} must have a name or company")
        
        # Validate skills structure if present
        if "skills" in resume:
            for i, skill in enumerate(resume["skills"]):
                if not isinstance(skill, dict):
                    raise ValueError(f"Skills entry {i} must be an object")
                if not skill.get("name"):
                    raise ValueError(f"Skills entry {i} must have a name")
        
        logger.info("Resume passed JSON Resume schema validation")
    
    def _clear_existing_resume(self) -> None:
        """Remove all existing resume entries from Qdrant collection"""
        
        try:
            # Get all existing points
            points, _ = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )
            
            if points:
                # Delete all existing points
                point_ids = [point.id for point in points]
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                logger.info(f"Cleared {len(point_ids)} existing resume entries")
            else:
                logger.info("No existing entries to clear")
                
        except Exception as e:
            logger.error(f"Failed to clear existing resume: {str(e)}")
            raise Exception(f"Could not clear existing resume data: {str(e)}")
    
    def _insert_new_resume(self, resume: Dict[str, Any]) -> int:
        """Insert new resume data into Qdrant collection"""
        
        entry_id = 1
        entries_added = 0
        
        try:
            # Insert basics (single entry)
            if "basics" in resume:
                self._add_entry(entry_id, "basics", resume["basics"])
                entry_id += 1
                entries_added += 1
            
            # Insert array sections
            array_sections = ["work", "education", "skills", "projects", "volunteer", "awards", "publications", "languages", "interests", "references"]
            
            for section_name in array_sections:
                if section_name in resume and resume[section_name]:
                    for entry in resume[section_name]:
                        self._add_entry(entry_id, section_name, entry)
                        entry_id += 1
                        entries_added += 1
            
            logger.info(f"Successfully inserted {entries_added} resume entries")
            return entries_added
            
        except Exception as e:
            logger.error(f"Failed to insert resume entries: {str(e)}")
            raise Exception(f"Could not insert new resume data: {str(e)}")
    
    def _add_entry(self, entry_id: int, section: str, entry_data: Dict[str, Any]) -> None:
        """Add a single entry to Qdrant collection"""
        
        # Prepare payload
        payload = entry_data.copy()
        payload["section"] = section
        payload["updated_at"] = datetime.now().isoformat()
        
        # Generate embedding from entry content
        search_text = self._entry_to_search_text(entry_data)
        embedding = self.vector_client.generate_embedding(search_text)
        
        # Add to Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": entry_id,
                "vector": embedding,
                "payload": payload
            }]
        )
        
        logger.debug(f"Added entry {entry_id} to section {section}")
    
    def _entry_to_search_text(self, entry: Dict[str, Any]) -> str:
        """Convert entry to searchable text"""
        text_parts = []
        
        # Common fields that should be searchable
        searchable_fields = [
            "name", "company", "position", "title", "label", "summary", "description", 
            "institution", "area", "studyType", "level", "entity", "type"
        ]
        
        for field in searchable_fields:
            if field in entry and entry[field]:
                text_parts.append(str(entry[field]))
        
        # Handle array fields
        array_fields = ["highlights", "keywords", "courses", "roles"]
        for field in array_fields:
            if field in entry and isinstance(entry[field], list):
                text_parts.extend([str(item) for item in entry[field] if item])
        
        # Handle nested location for basics
        if "location" in entry and isinstance(entry["location"], dict):
            location = entry["location"]
            for loc_field in ["address", "city", "region", "countryCode"]:
                if loc_field in location and location[loc_field]:
                    text_parts.append(str(location[loc_field]))
        
        return " ".join(text_parts)