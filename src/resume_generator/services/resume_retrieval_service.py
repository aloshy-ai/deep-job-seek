"""Service for retrieving and reconstructing complete JSON resume from Qdrant collection"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient

from ..config import QDRANT_URL, QDRANT_COLLECTION_NAME


class ResumeRetrievalService:
    """Service for retrieving complete JSON resume as single source of truth"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.collection_name = QDRANT_COLLECTION_NAME
    
    def get_complete_resume(self, format_type: str = "json") -> Dict[str, Any]:
        """
        Retrieve and reconstruct the complete JSON resume from all Qdrant entries
        
        Args:
            format_type: Output format ("json" for structured data, "pretty" for formatted)
            
        Returns:
            Complete JSON Resume following the JSON Resume schema
        """
        try:
            # Get all resume entries from Qdrant
            all_entries = self._get_all_resume_entries()
            
            if not all_entries:
                return {
                    "success": False,
                    "message": "No resume data found in collection",
                    "resume": self._get_empty_resume_template()
                }
            
            # Reconstruct complete resume
            complete_resume = self._reconstruct_json_resume(all_entries)
            
            # Validate and clean the resume
            validated_resume = self._validate_and_clean(complete_resume)
            
            return {
                "success": True,
                "message": f"Retrieved complete resume with {len(all_entries)} entries",
                "last_updated": datetime.now().isoformat(),
                "entry_count": len(all_entries),
                "resume": validated_resume if format_type == "json" else self._format_pretty(validated_resume)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve resume",
                "resume": self._get_empty_resume_template()
            }
    
    def get_resume_summary(self) -> Dict[str, Any]:
        """Get a summary of the current resume without full content"""
        try:
            all_entries = self._get_all_resume_entries()
            
            if not all_entries:
                return {
                    "success": False,
                    "message": "No resume data found",
                    "summary": {}
                }
            
            # Build summary by section
            summary = self._build_resume_summary(all_entries)
            
            return {
                "success": True,
                "message": "Resume summary retrieved successfully",
                "last_updated": datetime.now().isoformat(),
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve resume summary"
            }
    
    def _get_all_resume_entries(self) -> List[Dict]:
        """Retrieve all resume entries from Qdrant collection"""
        try:
            # Scroll through all points in the collection
            points, _ = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust if you expect more entries
                with_payload=True,
                with_vectors=False  # We don't need vectors for reconstruction
            )
            
            # Extract payloads
            entries = []
            for point in points:
                if hasattr(point, 'payload') and point.payload:
                    # Add the point ID for reference
                    entry = point.payload.copy()
                    entry['_point_id'] = point.id
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            raise Exception(f"Failed to retrieve entries from Qdrant: {str(e)}")
    
    def _reconstruct_json_resume(self, entries: List[Dict]) -> Dict[str, Any]:
        """Reconstruct complete JSON resume from individual entries"""
        
        # Initialize JSON Resume schema structure
        resume = {
            "basics": {},
            "work": [],
            "education": [],
            "skills": [],
            "projects": [],
            "volunteer": [],
            "awards": [],
            "publications": [],
            "languages": [],
            "interests": [],
            "references": []
        }
        
        # Group entries by section
        sections = {}
        for entry in entries:
            section = entry.get('section', 'unknown')
            if section not in sections:
                sections[section] = []
            sections[section].append(entry)
        
        # Process each section
        for section, section_entries in sections.items():
            if section == 'basics':
                resume['basics'] = self._process_basics_section(section_entries)
            elif section == 'work':
                resume['work'] = self._process_work_section(section_entries)
            elif section == 'education':
                resume['education'] = self._process_education_section(section_entries)
            elif section == 'skills':
                resume['skills'] = self._process_skills_section(section_entries)
            elif section == 'projects':
                resume['projects'] = self._process_projects_section(section_entries)
            elif section in ['volunteer', 'awards', 'publications', 'languages', 'interests', 'references']:
                resume[section] = self._process_generic_section(section_entries)
        
        return resume
    
    def _process_basics_section(self, entries: List[Dict]) -> Dict[str, Any]:
        """Process basics section - merge multiple entries into one"""
        basics = {}
        
        for entry in entries:
            # Standard JSON Resume basics fields
            for field in ['name', 'label', 'image', 'email', 'phone', 'url', 'summary']:
                if field in entry and entry[field]:
                    basics[field] = entry[field]
            
            # Location object
            if any(key in entry for key in ['address', 'postalCode', 'city', 'countryCode', 'region']):
                if 'location' not in basics:
                    basics['location'] = {}
                for loc_field in ['address', 'postalCode', 'city', 'countryCode', 'region']:
                    if loc_field in entry and entry[loc_field]:
                        basics['location'][loc_field] = entry[loc_field]
            
            # Profiles array (social media, etc.)
            if 'profiles' in entry and isinstance(entry['profiles'], list):
                if 'profiles' not in basics:
                    basics['profiles'] = []
                basics['profiles'].extend(entry['profiles'])
        
        # Remove duplicates from profiles
        if 'profiles' in basics:
            seen = set()
            unique_profiles = []
            for profile in basics['profiles']:
                profile_key = f"{profile.get('network', '')}-{profile.get('url', '')}"
                if profile_key not in seen:
                    seen.add(profile_key)
                    unique_profiles.append(profile)
            basics['profiles'] = unique_profiles
        
        return basics
    
    def _process_work_section(self, entries: List[Dict]) -> List[Dict]:
        """Process work experience entries"""
        work_entries = []
        
        for entry in entries:
            work_item = {}
            
            # Standard work fields
            for field in ['name', 'company', 'position', 'url', 'startDate', 'endDate', 'summary', 'highlights']:
                if field in entry and entry[field] is not None:
                    work_item[field] = entry[field]
            
            # Handle company vs name field (some entries might use either)
            if 'company' in work_item and 'name' not in work_item:
                work_item['name'] = work_item['company']
            elif 'name' in work_item and 'company' not in work_item:
                work_item['company'] = work_item['name']
            
            # Ensure highlights is a list
            if 'highlights' in work_item and not isinstance(work_item['highlights'], list):
                if isinstance(work_item['highlights'], str):
                    work_item['highlights'] = [work_item['highlights']]
                else:
                    work_item['highlights'] = []
            
            work_entries.append(work_item)
        
        # Sort by start date (most recent first)
        return self._sort_by_date(work_entries, 'startDate', reverse=True)
    
    def _process_education_section(self, entries: List[Dict]) -> List[Dict]:
        """Process education entries"""
        education_entries = []
        
        for entry in entries:
            edu_item = {}
            
            # Standard education fields
            for field in ['institution', 'url', 'area', 'studyType', 'startDate', 'endDate', 'score', 'gpa', 'courses']:
                if field in entry and entry[field] is not None:
                    edu_item[field] = entry[field]
            
            # Handle score/gpa normalization
            if 'gpa' in entry and 'score' not in edu_item:
                edu_item['score'] = str(entry['gpa'])
            
            # Ensure courses is a list
            if 'courses' in edu_item and not isinstance(edu_item['courses'], list):
                if isinstance(edu_item['courses'], str):
                    edu_item['courses'] = [edu_item['courses']]
                else:
                    edu_item['courses'] = []
            
            education_entries.append(edu_item)
        
        # Sort by end date (most recent first)
        return self._sort_by_date(education_entries, 'endDate', reverse=True)
    
    def _process_skills_section(self, entries: List[Dict]) -> List[Dict]:
        """Process skills entries"""
        skills_entries = []
        
        for entry in entries:
            skill_item = {}
            
            # Standard skills fields
            for field in ['name', 'level', 'keywords']:
                if field in entry and entry[field] is not None:
                    skill_item[field] = entry[field]
            
            # Ensure keywords is a list
            if 'keywords' in skill_item:
                if not isinstance(skill_item['keywords'], list):
                    if isinstance(skill_item['keywords'], str):
                        # Split comma-separated keywords
                        skill_item['keywords'] = [k.strip() for k in skill_item['keywords'].split(',')]
                    else:
                        skill_item['keywords'] = []
                
                # Remove duplicates while preserving order
                skill_item['keywords'] = list(dict.fromkeys(skill_item['keywords']))
            
            skills_entries.append(skill_item)
        
        return skills_entries
    
    def _process_projects_section(self, entries: List[Dict]) -> List[Dict]:
        """Process projects entries"""
        project_entries = []
        
        for entry in entries:
            project_item = {}
            
            # Standard project fields
            for field in ['name', 'description', 'highlights', 'keywords', 'startDate', 'endDate', 'url', 'roles', 'entity', 'type']:
                if field in entry and entry[field] is not None:
                    project_item[field] = entry[field]
            
            # Ensure list fields are lists
            for list_field in ['highlights', 'keywords', 'roles']:
                if list_field in project_item and not isinstance(project_item[list_field], list):
                    if isinstance(project_item[list_field], str):
                        project_item[list_field] = [project_item[list_field]]
                    else:
                        project_item[list_field] = []
            
            project_entries.append(project_item)
        
        # Sort by start date (most recent first)
        return self._sort_by_date(project_entries, 'startDate', reverse=True)
    
    def _process_generic_section(self, entries: List[Dict]) -> List[Dict]:
        """Process generic sections (volunteer, awards, etc.)"""
        processed_entries = []
        
        for entry in entries:
            # Remove internal fields
            clean_entry = {k: v for k, v in entry.items() 
                          if not k.startswith('_') and k != 'section'}
            processed_entries.append(clean_entry)
        
        return processed_entries
    
    def _sort_by_date(self, entries: List[Dict], date_field: str, reverse: bool = False) -> List[Dict]:
        """Sort entries by date field"""
        def get_sort_date(entry):
            date_str = entry.get(date_field)
            if not date_str:
                return datetime.min if not reverse else datetime.max
            
            try:
                # Try parsing various date formats
                for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                
                # If no format matches, return current date
                return datetime.now()
                
            except Exception:
                return datetime.min if not reverse else datetime.max
        
        return sorted(entries, key=get_sort_date, reverse=reverse)
    
    def _validate_and_clean(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the reconstructed resume"""
        
        # Remove empty sections
        cleaned_resume = {}
        for section, content in resume.items():
            if isinstance(content, list) and len(content) > 0:
                cleaned_resume[section] = content
            elif isinstance(content, dict) and len(content) > 0:
                cleaned_resume[section] = content
        
        # Ensure basics section exists even if empty
        if 'basics' not in cleaned_resume:
            cleaned_resume['basics'] = {}
        
        return cleaned_resume
    
    def _build_resume_summary(self, entries: List[Dict]) -> Dict[str, Any]:
        """Build a summary of resume content"""
        summary = {
            "total_entries": len(entries),
            "sections": {},
            "last_updated": datetime.now().isoformat()
        }
        
        # Count entries by section
        section_counts = {}
        for entry in entries:
            section = entry.get('section', 'unknown')
            section_counts[section] = section_counts.get(section, 0) + 1
        
        # Build section summaries
        for section, count in section_counts.items():
            if section == 'basics':
                # Extract basic info
                basics_entries = [e for e in entries if e.get('section') == 'basics']
                basics_info = {}
                for entry in basics_entries:
                    if 'name' in entry:
                        basics_info['name'] = entry['name']
                    if 'email' in entry:
                        basics_info['email'] = entry['email']
                    if 'phone' in entry:
                        basics_info['phone'] = entry['phone']
                
                summary['sections'][section] = {
                    "count": count,
                    "info": basics_info
                }
                
            elif section == 'work':
                # Work experience summary
                work_entries = [e for e in entries if e.get('section') == 'work']
                companies = list(set([e.get('company', 'Unknown') for e in work_entries]))
                positions = list(set([e.get('position', 'Unknown') for e in work_entries]))
                
                summary['sections'][section] = {
                    "count": count,
                    "companies": companies[:5],  # Top 5
                    "positions": positions[:5]   # Top 5
                }
                
            elif section == 'skills':
                # Skills summary
                skills_entries = [e for e in entries if e.get('section') == 'skills']
                all_keywords = []
                for entry in skills_entries:
                    keywords = entry.get('keywords', [])
                    if isinstance(keywords, list):
                        all_keywords.extend(keywords)
                
                top_skills = list(set(all_keywords))[:10]  # Top 10 unique skills
                
                summary['sections'][section] = {
                    "count": count,
                    "top_skills": top_skills
                }
                
            else:
                summary['sections'][section] = {"count": count}
        
        return summary
    
    def _format_pretty(self, resume: Dict[str, Any]) -> str:
        """Format resume as human-readable text"""
        lines = []
        
        # Basics section
        if 'basics' in resume and resume['basics']:
            basics = resume['basics']
            lines.append("=== RESUME ===\n")
            
            if 'name' in basics:
                lines.append(f"Name: {basics['name']}")
            if 'email' in basics:
                lines.append(f"Email: {basics['email']}")
            if 'phone' in basics:
                lines.append(f"Phone: {basics['phone']}")
            if 'summary' in basics:
                lines.append(f"Summary: {basics['summary']}")
            lines.append("")
        
        # Work experience
        if 'work' in resume and resume['work']:
            lines.append("=== WORK EXPERIENCE ===")
            for work in resume['work']:
                company = work.get('company', work.get('name', 'Unknown Company'))
                position = work.get('position', 'Unknown Position')
                start_date = work.get('startDate', '')
                end_date = work.get('endDate', 'Present')
                
                lines.append(f"{position} at {company}")
                lines.append(f"  {start_date} - {end_date}")
                
                if 'summary' in work:
                    lines.append(f"  {work['summary']}")
                
                if 'highlights' in work and isinstance(work['highlights'], list):
                    for highlight in work['highlights']:
                        lines.append(f"  • {highlight}")
                lines.append("")
        
        # Education
        if 'education' in resume and resume['education']:
            lines.append("=== EDUCATION ===")
            for edu in resume['education']:
                institution = edu.get('institution', 'Unknown Institution')
                area = edu.get('area', '')
                study_type = edu.get('studyType', '')
                
                lines.append(f"{study_type} in {area} from {institution}")
                if 'score' in edu:
                    lines.append(f"  GPA: {edu['score']}")
                lines.append("")
        
        # Skills
        if 'skills' in resume and resume['skills']:
            lines.append("=== SKILLS ===")
            for skill in resume['skills']:
                name = skill.get('name', 'Unknown Category')
                keywords = skill.get('keywords', [])
                if isinstance(keywords, list):
                    lines.append(f"{name}: {', '.join(keywords)}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_empty_resume_template(self) -> Dict[str, Any]:
        """Get empty JSON Resume template"""
        return {
            "basics": {
                "name": "",
                "label": "",
                "email": "",
                "phone": "",
                "summary": ""
            },
            "work": [],
            "education": [],
            "skills": [],
            "projects": []
        }