"""Simplified and working resume update service"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from ..config import QDRANT_URL, QDRANT_COLLECTION_NAME
from ..utils.vector_search import VectorSearchClient

# Configure logging to use logs folder
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/resume_update.log'
)
logger = logging.getLogger(__name__)


class ResumeUpdateService:
    """Simplified service for updating resume data in Qdrant"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.vector_client = VectorSearchClient()
        self.collection_name = QDRANT_COLLECTION_NAME
        logger.info("ResumeUpdateService initialized")
    
    def update_resume(self, content: str, update_mode: str = "merge", 
                     content_type: str = "auto", section_hint: str = None) -> Dict[str, Any]:
        """
        Main method to update resume data
        
        Args:
            content: Raw text, JSON, or markdown content
            update_mode: 'merge', 'replace', or 'append'
            content_type: 'auto', 'json', 'markdown', or 'text'
            section_hint: Optional hint about which section this updates
            
        Returns:
            Dict with update results and statistics
        """
        try:
            logger.info(f"Starting resume update: mode={update_mode}, type={content_type}, hint={section_hint}")
            
            # Step 1: Parse content
            parsed_data = self._parse_content(content, content_type, section_hint)
            logger.info(f"Parsed data into {len(parsed_data)} sections: {list(parsed_data.keys())}")
            
            # Step 2: Process each section
            results = {
                "updated_sections": [],
                "new_entries": 0,
                "modified_entries": 0,
                "errors": []
            }
            
            for section, entries in parsed_data.items():
                logger.info(f"Processing section '{section}' with {len(entries)} entries")
                section_result = self._update_section(section, entries, update_mode)
                
                results["updated_sections"].append({
                    "section": section,
                    "changes": section_result
                })
                results["new_entries"] += section_result["new_count"]
                results["modified_entries"] += section_result["modified_count"]
                
                if section_result.get("errors"):
                    results["errors"].extend(section_result["errors"])
            
            logger.info(f"Update completed: {results['new_entries']} new, {results['modified_entries']} modified")
            
            return {
                "success": True,
                "message": f"Updated {results['new_entries']} new and {results['modified_entries']} existing entries",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Resume update failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update resume"
            }
    
    def _parse_content(self, content: str, content_type: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Parse content into structured resume sections"""
        
        # Detect content type if auto
        if content_type == "auto":
            content_type = self._detect_content_type(content)
        
        logger.info(f"Parsing content as {content_type}")
        
        if content_type == "json":
            return self._parse_json_content(content)
        elif content_type == "markdown":
            return self._parse_markdown_content(content, section_hint)
        else:
            return self._parse_text_content(content, section_hint)
    
    def _detect_content_type(self, content: str) -> str:
        """Detect the format of input content"""
        content_stripped = content.strip()
        
        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                json.loads(content)
                return "json"
            except:
                pass
        
        if content_stripped.startswith('#') or '##' in content:
            return "markdown"
            
        return "text"
    
    def _parse_json_content(self, content: str) -> Dict[str, List[Dict]]:
        """Parse JSON resume content"""
        try:
            data = json.loads(content)
            sections = {}
            
            # Handle single entry (most common case)
            if "section" in data:
                section = data["section"]
                # Remove the section field from the entry itself
                entry = {k: v for k, v in data.items() if k != "section"}
                sections[section] = [entry]
            else:
                # Handle full resume format
                for section_name in ["basics", "work", "skills", "projects", "education"]:
                    if section_name in data:
                        section_data = data[section_name]
                        if isinstance(section_data, list):
                            sections[section_name] = section_data
                        else:
                            sections[section_name] = [section_data]
            
            logger.info(f"Parsed JSON into sections: {list(sections.keys())}")
            return sections
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def _parse_markdown_content(self, content: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Simple markdown parsing without AI dependency"""
        sections = {}
        
        # For now, create a basic entry based on section hint
        if section_hint:
            sections[section_hint] = [{
                "name": "Parsed from Markdown",
                "description": content.strip(),
                "source": "markdown_import"
            }]
        else:
            # Default to projects section for markdown content
            sections["projects"] = [{
                "name": "Imported Project",
                "description": content.strip(),
                "source": "markdown_import"
            }]
        
        logger.info(f"Parsed markdown into sections: {list(sections.keys())}")
        return sections
    
    def _parse_text_content(self, content: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Simple text parsing"""
        sections = {}
        
        # Create basic entry based on section hint
        if section_hint:
            if section_hint == "basics":
                sections["basics"] = [{
                    "summary": content.strip(),
                    "source": "text_import"
                }]
            elif section_hint == "work":
                sections["work"] = [{
                    "company": "Unknown Company",
                    "position": "Unknown Position", 
                    "summary": content.strip(),
                    "source": "text_import"
                }]
            elif section_hint == "skills":
                # Try to extract skills from text
                skills = [skill.strip() for skill in content.replace(',', '\n').split('\n') if skill.strip()]
                sections["skills"] = [{
                    "name": "Imported Skills",
                    "keywords": skills,
                    "source": "text_import"
                }]
            else:
                sections[section_hint] = [{
                    "description": content.strip(),
                    "source": "text_import"
                }]
        else:
            # Default to a general entry
            sections["projects"] = [{
                "name": "Imported Content",
                "description": content.strip(),
                "source": "text_import"
            }]
        
        logger.info(f"Parsed text into sections: {list(sections.keys())}")
        return sections
    
    def _update_section(self, section: str, new_entries: List[Dict], update_mode: str) -> Dict[str, Any]:
        """Update a specific resume section"""
        
        result = {
            "new_count": 0, 
            "modified_count": 0, 
            "entries": [],
            "errors": []
        }
        
        for entry in new_entries:
            try:
                if update_mode == "append":
                    # Always add as new entry
                    entry_result = self._add_new_entry(section, entry)
                    result["new_count"] += 1
                elif update_mode == "replace":
                    # Find and replace similar entry
                    entry_result = self._replace_entry(section, entry)
                    result["modified_count"] += 1
                else:  # merge mode (default)
                    # Intelligent merge
                    entry_result = self._merge_entry(section, entry)
                    if entry_result.get("is_new", True):
                        result["new_count"] += 1
                    else:
                        result["modified_count"] += 1
                
                result["entries"].append(entry_result)
                
            except Exception as e:
                error_msg = f"Failed to process entry in {section}: {str(e)}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
        
        return result
    
    def _add_new_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Add a completely new entry"""
        
        # Get next available ID
        next_id = self._get_next_id()
        
        # Add to Qdrant
        self._add_qdrant_entry(next_id, section, entry)
        
        logger.info(f"Added new entry {next_id} to section {section}")
        
        return {
            "is_new": True,
            "entry_id": next_id,
            "action": "added",
            "entry": entry
        }
    
    def _merge_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Simple merge logic - for now, just add as new"""
        # TODO: Implement similarity checking and merging
        return self._add_new_entry(section, entry)
    
    def _replace_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Replace logic - for now, just add as new"""
        # TODO: Implement finding and replacing existing entries
        return self._add_new_entry(section, entry)
    
    def _get_next_id(self) -> int:
        """Get the next available ID for new entries"""
        try:
            # Get all points to find max ID
            points, _ = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )
            
            if not points:
                return 1
                
            max_id = max([point.id for point in points])
            return max_id + 1
            
        except Exception as e:
            logger.warning(f"Could not get max ID, using timestamp: {str(e)}")
            # Fallback to timestamp-based ID
            return int(datetime.now().timestamp())
    
    def _add_qdrant_entry(self, entry_id: int, section: str, entry: Dict):
        """Add new entry to Qdrant"""
        
        # Prepare payload
        payload = entry.copy()
        payload["section"] = section
        payload["updated_at"] = datetime.now().isoformat()
        
        # Generate embedding from entry content
        search_text = self._entry_to_search_text(entry)
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
        
        logger.info(f"Upserted entry {entry_id} to Qdrant collection {self.collection_name}")
    
    def _entry_to_search_text(self, entry: Dict) -> str:
        """Convert entry to searchable text"""
        text_parts = []
        
        # Add key fields for searching
        for key in ["name", "company", "position", "summary", "description"]:
            if key in entry and entry[key]:
                text_parts.append(str(entry[key]))
        
        # Add array fields
        for key in ["highlights", "keywords"]:
            if key in entry and isinstance(entry[key], list):
                text_parts.extend([str(item) for item in entry[key]])
        
        return " ".join(text_parts)