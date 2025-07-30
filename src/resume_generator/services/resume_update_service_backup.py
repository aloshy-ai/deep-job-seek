"""Service for updating resume data in Qdrant collection"""
import json
import re
from datetime import datetime
from typing import Dict, List, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from ..config import QDRANT_URL, QDRANT_COLLECTION_NAME
from ..utils.vector_search import VectorSearchClient
from ..utils.api_client import APIClient
from .advanced_resume_parser import AdvancedResumeParser


class ResumeUpdateService:
    """Service for intelligently updating resume data"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.vector_client = VectorSearchClient()
        self.ai_client = APIClient()
        self.advanced_parser = AdvancedResumeParser()
        self.collection_name = QDRANT_COLLECTION_NAME
    
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
            # Step 1: Parse and structure the content
            parsed_data = self._parse_content(content, content_type, section_hint)
            
            # Step 2: Process each section based on update mode
            results = {
                "updated_sections": [],
                "new_entries": 0,
                "modified_entries": 0,
                "errors": []
            }
            
            for section, entries in parsed_data.items():
                section_result = self._update_section(section, entries, update_mode)
                results["updated_sections"].append({
                    "section": section,
                    "changes": section_result
                })
                results["new_entries"] += section_result["new_count"]
                results["modified_entries"] += section_result["modified_count"]
                
            return {
                "success": True,
                "message": f"Updated {results['new_entries']} new and {results['modified_entries']} existing entries",
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update resume"
            }
    
    def _parse_content(self, content: str, content_type: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Parse content into structured resume sections"""
        
        # First check if this is a natural language instruction
        if self._is_natural_language_instruction(content):
            return self._parse_instruction_content(content)
        
        # Detect content type if auto
        if content_type == "auto":
            content_type = self._detect_content_type(content)
        
        if content_type == "json":
            return self._parse_json_content(content)
        elif content_type == "markdown":
            return self._parse_markdown_content(content)  
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
        
        if re.search(r'^#{1,6}\s+', content_stripped, re.MULTILINE):
            return "markdown"
            
        return "text"
    
    def _parse_json_content(self, content: str) -> Dict[str, List[Dict]]:
        """Parse JSON resume content"""
        try:
            data = json.loads(content)
            sections = {}
            
            # Handle JSON Resume schema format
            if "basics" in data:
                sections["basics"] = [data["basics"]]
            
            if "work" in data:
                sections["work"] = data["work"] if isinstance(data["work"], list) else [data["work"]]
                
            if "skills" in data:
                sections["skills"] = data["skills"] if isinstance(data["skills"], list) else [data["skills"]]
                
            if "projects" in data:
                sections["projects"] = data["projects"] if isinstance(data["projects"], list) else [data["projects"]]
                
            if "education" in data:
                sections["education"] = data["education"] if isinstance(data["education"], list) else [data["education"]]
            
            return sections
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def _parse_markdown_content(self, content: str) -> Dict[str, List[Dict]]:
        """Parse markdown resume content using AI"""
        
        prompt = f"""
        Parse the following markdown resume content into structured JSON sections.
        Extract information for these sections: basics, work, skills, projects, education.
        
        For work experience, include: company, position, startDate, endDate, summary, highlights
        For skills, include: name, keywords
        For projects, include: name, description, highlights, url (if mentioned)
        For basics, include: name, email, phone, summary
        For education, include: institution, area, studyType, startDate, endDate
        
        Return valid JSON with sections as keys and arrays of objects as values.
        
        Markdown Content:
        {content}
        """
        
        try:
            response = self.ai_client.query(prompt)
            # Extract JSON from AI response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("AI could not parse markdown into valid JSON")
        except Exception as e:
            raise ValueError(f"Failed to parse markdown: {str(e)}")
    
    def _parse_text_content(self, content: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Parse plain text content using appropriate parser based on complexity"""
        
        # Determine if this is complex/messy text that needs advanced parsing
        if self._is_complex_text(content):
            return self._parse_complex_text_with_context(content, section_hint)
        else:
            return self._parse_simple_text(content, section_hint)
    
    def _is_complex_text(self, content: str) -> bool:
        """Determine if text requires advanced parsing due to complexity/messiness"""
        
        complexity_indicators = [
            # Informal/conversational language
            r'\b(btw|lol|oh\s+yeah|forgot\s+to\s+mention|anyway)\b',
            
            # Emojis present
            r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]',
            
            # Tech abbreviations
            r'\b(k8s|tf|aws|gcp|ddb|js|ts|py|nodejs|reactjs|ml|ai|nlp|cv|devops|ci/cd)\b',
            
            # Industry jargon
            r'\b(faang|unicorn|startup|yc|employee\s*#\d+|big\s+tech)\b',
            
            # Casual timeline references
            r'\b(pandemic|covid|recently|last\s+year|since\s+\d{4}|after\s+.+ing)\b',
            
            # Multiple contact formats mixed
            len(re.findall(r'[@📧🏢📱]', content)) > 1,
            
            # Mixed formatting (pipes, bullets, etc.)
            '|' in content and len(content.split('|')) > 2,
            
            # Mentions of levels/progression
            r'\b(l\d+|level\s+\d+|promoted|promotion|senior|staff|principal)\b',
            
            # Multiple companies mentioned
            len(re.findall(r'\b(google|meta|microsoft|amazon|apple|netflix|uber|airbnb|tesla)\b', content.lower())) > 1,
            
            # Fragmented sentences or thoughts
            content.count('...') > 0 or content.count(' - ') > 2,
            
            # Educational context mixed with work
            r'\b(bootcamp|cs\s+\d{2}|gpa|dean.?s\s+list|stanford|mit|berkeley)\b' in content.lower() and r'\b(engineer|developer|swe)\b' in content.lower(),
            
            # Length and complexity (long, run-on content)
            len(content) > 500 and len(content.split('.')) > 5
        ]
        
        # Count how many complexity indicators are present
        complexity_score = 0
        content_lower = content.lower()
        
        for indicator in complexity_indicators:
            if isinstance(indicator, str):  # regex pattern
                if re.search(indicator, content_lower, re.IGNORECASE):
                    complexity_score += 1
            elif isinstance(indicator, bool):  # boolean condition
                if indicator:
                    complexity_score += 1
        
        # If 1 or more complexity indicators, use advanced parsing
        return complexity_score >= 1
    
    def _parse_complex_text_with_context(self, content: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Parse complex text using advanced AI parser with existing resume context"""
        
        try:
            # Get existing resume data for context
            existing_data = self._get_existing_resume_context()
            
            # Use advanced parser
            parsed_data = self.advanced_parser.parse_complex_text(content, existing_data)
            
            # Convert to expected format (sections as keys, entries as lists)
            structured_data = {}
            for section, data in parsed_data.items():
                if isinstance(data, dict):
                    # Single entry (like basics)
                    structured_data[section] = [data]
                elif isinstance(data, list):
                    # Multiple entries
                    structured_data[section] = data
                else:
                    # Skip invalid data
                    continue
            
            return structured_data
            
        except Exception as e:
            # Fallback to simple parsing if advanced parsing fails
            print(f"Advanced parsing failed, falling back to simple: {str(e)}")
            return self._parse_simple_text(content, section_hint)
    
    def _parse_simple_text(self, content: str, section_hint: str) -> Dict[str, List[Dict]]:
        """Parse simple/clean text content using basic AI prompting"""
        
        section_context = f" Focus on {section_hint} information." if section_hint else ""
        
        prompt = f"""
        Parse the following text into structured resume information.{section_context}
        Extract relevant details and format as JSON with these sections: basics, work, skills, projects, education.
        
        For work experience: Extract company, position, dates, responsibilities, achievements
        For skills: Group related skills with descriptive names
        For projects: Extract project names, descriptions, technologies used
        For basics: Extract name, contact info, professional summary
        
        Return valid JSON format.
        
        Text Content:
        {content}
        """
        
        try:
            response = self.ai_client.query(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("AI could not parse text into valid JSON")
        except Exception as e:
            raise ValueError(f"Failed to parse text: {str(e)}")
    
    def _get_existing_resume_context(self) -> List[Dict]:
        """Get existing resume data from Qdrant for context"""
        
        try:
            # Get all points from the collection
            points, _ = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000  # Adjust if you have more entries
            )
            
            # Convert to list of payload dictionaries
            existing_data = []
            for point in points:
                if hasattr(point, 'payload') and point.payload:
                    existing_data.append(point.payload)
            
            return existing_data
            
        except Exception as e:
            print(f"Could not retrieve existing context: {str(e)}")
            return []
    
    def _is_natural_language_instruction(self, content: str) -> bool:
        """Detect if content is a natural language instruction rather than resume data"""
        content_lower = content.lower().strip()
        
        # Instruction patterns
        instruction_patterns = [
            r'change\s+.*\s+to\s+',
            r'update\s+.*\s+to\s+',
            r'replace\s+.*\s+with\s+',
            r'correct\s+.*\s+to\s+',
            r'fix\s+.*\s+to\s+',
            r'set\s+.*\s+to\s+',
            r'modify\s+.*\s+to\s+',
            r'edit\s+.*\s+to\s+',
            r'.*\s+is\s+not\s+.*,?\s+it.?s\s+',
            r'.*\s+should\s+be\s+',
            r'remove\s+',
            r'delete\s+',
            r'add\s+.*\s+to\s+',
            r'include\s+.*\s+in\s+',
        ]
        
        # Check for instruction patterns
        for pattern in instruction_patterns:
            if re.search(pattern, content_lower):
                return True
        
        # Check for imperative verbs at start
        imperative_starters = ['change', 'update', 'replace', 'correct', 'fix', 'set', 'modify', 'edit', 'remove', 'delete', 'add', 'include']
        first_word = content_lower.split()[0] if content_lower.split() else ""
        
        return first_word in imperative_starters
    
    def _parse_instruction_content(self, instruction: str) -> Dict[str, List[Dict]]:
        """Parse natural language instructions into structured updates"""
        
        prompt = f"""
        Parse the following natural language instruction into a structured resume update.
        The instruction is asking to modify existing resume data.
        
        Identify:
        1. What field/section needs to be updated (email, phone, company name, position, skill, etc.)
        2. The old value (if mentioned)
        3. The new value
        4. Which resume section this belongs to (basics, work, skills, projects, education)
        
        Return JSON in this format:
        {{
            "instruction_type": "field_update|correction|addition|removal",
            "section": "basics|work|skills|projects|education", 
            "field": "email|phone|company|position|name|etc",
            "old_value": "current value to find and replace",
            "new_value": "new value to set",
            "search_context": "additional context to help find the right entry"
        }}
        
        For corrections like "Google not Gogle", set instruction_type to "correction".
        For field changes like "change email to...", set instruction_type to "field_update".
        
        Instruction: "{instruction}"
        """
        
        try:
            response = self.ai_client.query(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_instruction = json.loads(json_match.group())
                return self._convert_instruction_to_update(parsed_instruction)
            else:
                raise ValueError("AI could not parse instruction into valid JSON")
        except Exception as e:
            raise ValueError(f"Failed to parse instruction: {str(e)}")
    
    def _convert_instruction_to_update(self, instruction: Dict) -> Dict[str, List[Dict]]:
        """Convert parsed instruction into update format"""
        
        section = instruction.get("section", "basics")
        field = instruction.get("field")
        new_value = instruction.get("new_value")
        old_value = instruction.get("old_value")
        instruction_type = instruction.get("instruction_type")
        
        # Create update entry
        update_entry = {
            "_instruction_type": instruction_type,
            "_field": field,
            "_old_value": old_value,
            "_search_context": instruction.get("search_context", "")
        }
        
        # Set the new value in appropriate field
        if field:
            update_entry[field] = new_value
        
        return {section: [update_entry]}
    
    def _apply_instruction_update(self, section: str, instruction_entry: Dict) -> Dict[str, Any]:
        """Apply instruction-based update to existing resume data"""
        
        instruction_type = instruction_entry.get("_instruction_type")
        field = instruction_entry.get("_field")
        old_value = instruction_entry.get("_old_value")
        new_value = instruction_entry.get(field) if field else None
        search_context = instruction_entry.get("_search_context", "")
        
        try:
            # Find the target entry to update
            target_entries = self._find_instruction_target(section, field, old_value, search_context)
            
            if not target_entries:
                # If no target found, this might be an addition
                if instruction_type == "addition":
                    return self._add_new_entry(section, {field: new_value})
                else:
                    return {
                        "is_new": False,
                        "action": "no_match_found",
                        "error": f"Could not find entry to update in {section} section"
                    }
            
            # Update the best matching entry
            best_match = target_entries[0]
            updated_entry = best_match["payload"].copy()
            
            if instruction_type == "removal":
                # Remove field or entry
                if field in updated_entry:
                    del updated_entry[field]
            else:
                # Update/correct field value
                if field:
                    updated_entry[field] = new_value
            
            # Update in Qdrant
            self._update_qdrant_entry(best_match["id"], section, updated_entry)
            
            return {
                "is_new": False,
                "entry_id": best_match["id"],
                "action": f"{instruction_type}_applied",
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
                "updated": updated_entry
            }
            
        except Exception as e:
            return {
                "is_new": False,
                "action": "instruction_failed",
                "error": str(e)
            }
    
    def _find_instruction_target(self, section: str, field: str, old_value: str, search_context: str) -> List[Dict]:
        """Find the target entry for instruction-based update"""
        
        # Build search query
        search_parts = []
        if old_value:
            search_parts.append(old_value)
        if search_context:
            search_parts.append(search_context)
        if field:
            search_parts.append(field)
        
        search_text = " ".join(search_parts) if search_parts else section
        
        # Search with section filter
        filter_condition = Filter(
            must=[FieldCondition(key="section", match=MatchValue(value=section))]
        )
        
        results = self.vector_client.search_with_filter(
            query_text=search_text,
            filter_conditions=filter_condition,
            limit=5
        )
        
        # If we have old_value, prefer exact matches
        if old_value and results:
            exact_matches = []
            for result in results:
                payload = result.payload
                # Check if any field contains the old value
                for value in payload.values():
                    if isinstance(value, str) and old_value.lower() in value.lower():
                        exact_matches.append(result)
                        break
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and old_value.lower() in item.lower():
                                exact_matches.append(result)
                                break
            
            if exact_matches:
                return exact_matches
        
        return results
    
    def _update_section(self, section: str, new_entries: List[Dict], 
                       update_mode: str) -> Dict[str, Any]:
        """Update a specific resume section"""
        
        result = {"new_count": 0, "modified_count": 0, "entries": []}
        
        for entry in new_entries:
            # Check if this is an instruction-based update
            if "_instruction_type" in entry:
                entry_result = self._apply_instruction_update(section, entry)
            elif update_mode == "replace":
                # Replace entire section
                entry_result = self._replace_entry(section, entry)
            elif update_mode == "append":
                # Always add as new entry
                entry_result = self._add_new_entry(section, entry)
            else:  # merge mode (default)
                # Intelligent merge - check for duplicates/similarities
                entry_result = self._merge_entry(section, entry)
            
            if entry_result["is_new"]:
                result["new_count"] += 1
            else:
                result["modified_count"] += 1
                
            result["entries"].append(entry_result)
        
        return result
    
    def _merge_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Intelligently merge entry with existing data"""
        
        # Find similar existing entries
        similar_entries = self._find_similar_entries(section, entry)
        
        if similar_entries:
            # Merge with most similar entry
            best_match = similar_entries[0]
            merged_entry = self._merge_entries(best_match["payload"], entry)
            
            # Update the existing entry
            self._update_qdrant_entry(best_match["id"], section, merged_entry)
            
            return {
                "is_new": False,
                "entry_id": best_match["id"],
                "action": "merged",
                "original": best_match["payload"],
                "updated": merged_entry
            }
        else:
            # Add as new entry
            return self._add_new_entry(section, entry)
    
    def _find_similar_entries(self, section: str, entry: Dict, threshold: float = 0.7) -> List[Dict]:
        """Find similar entries in the specified section"""
        
        # Create search text from entry
        search_text = self._entry_to_search_text(entry)
        
        # Search with section filter
        filter_condition = Filter(
            must=[FieldCondition(key="section", match=MatchValue(value=section))]
        )
        
        results = self.vector_client.search_with_filter(
            query_text=search_text,
            filter_conditions=filter_condition,
            limit=3
        )
        
        # Filter by similarity threshold
        return [r for r in results if r.score >= threshold]
    
    def _merge_entries(self, existing: Dict, new: Dict) -> Dict:
        """Merge two entries intelligently"""
        merged = existing.copy()
        
        # Merge highlights/keywords arrays
        if "highlights" in new and "highlights" in existing:
            merged["highlights"] = list(set(existing["highlights"] + new["highlights"]))
        elif "highlights" in new:
            merged["highlights"] = new["highlights"]
            
        if "keywords" in new and "keywords" in existing:
            merged["keywords"] = list(set(existing["keywords"] + new["keywords"]))
        elif "keywords" in new:
            merged["keywords"] = new["keywords"]
        
        # Update other fields with new values if they exist
        for key, value in new.items():
            if key not in ["highlights", "keywords"] and value:
                if key in merged:
                    # For text fields, prefer longer/more detailed version
                    if isinstance(value, str) and isinstance(merged[key], str):
                        if len(value) > len(merged[key]):
                            merged[key] = value
                else:
                    merged[key] = value
        
        return merged
    
    def _add_new_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Add a completely new entry"""
        
        # Get next available ID
        next_id = self._get_next_id()
        
        # Add to Qdrant
        self._add_qdrant_entry(next_id, section, entry)
        
        return {
            "is_new": True,
            "entry_id": next_id,
            "action": "added",
            "entry": entry
        }
    
    def _replace_entry(self, section: str, entry: Dict) -> Dict[str, Any]:
        """Replace entries in a section (used in replace mode)"""
        # For replace mode, we'd need to identify which entry to replace
        # This is a simplified implementation - in practice, you might want
        # more sophisticated matching logic
        return self._add_new_entry(section, entry)
    
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
    
    def _get_next_id(self) -> int:
        """Get the next available ID for new entries"""
        # Get collection info to find highest ID
        try:
            # Scroll through all points to find max ID
            points, _ = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust if you have more entries
            )
            
            if not points:
                return 1
                
            max_id = max([point.id for point in points])
            return max_id + 1
            
        except Exception:
            # Fallback to timestamp-based ID
            return int(datetime.now().timestamp())
    
    def _add_qdrant_entry(self, entry_id: int, section: str, entry: Dict):
        """Add new entry to Qdrant"""
        
        # Prepare payload
        payload = entry.copy()
        payload["section"] = section
        
        # Generate embedding
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
    
    def _update_qdrant_entry(self, entry_id: int, section: str, entry: Dict):
        """Update existing entry in Qdrant"""
        
        # Prepare payload
        payload = entry.copy()
        payload["section"] = section
        
        # Generate new embedding
        search_text = self._entry_to_search_text(entry)
        embedding = self.vector_client.generate_embedding(search_text)
        
        # Update in Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": entry_id,
                "vector": embedding,
                "payload": payload
            }]
        )