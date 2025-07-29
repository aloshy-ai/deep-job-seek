"""Resume building utilities"""
import json
from ..config import (
    MAX_WORK_ENTRIES, MAX_SKILLS_ENTRIES, MAX_PROJECTS_ENTRIES,
    RESUME_SCHEMA_URL
)


class ResumeBuilder:
    """Builder class for constructing resume objects"""
    
    def __init__(self, schema_url=None):
        self.schema_url = schema_url or RESUME_SCHEMA_URL
        self.resume = {
            "$schema": self.schema_url,
            "basics": {},
            "work": [],
            "skills": [],
            "projects": [],
            "education": []
        }
        self.added_ids = set()
    
    def add_content(self, content):
        """
        Add content to the appropriate resume section.
        
        Args:
            content (dict): Content with 'section' field indicating destination
            
        Returns:
            bool: True if content was added, False if skipped (duplicate or limit reached)
        """
        section = content.get('section')
        if not section:
            return False
        
        # Create unique ID to prevent duplicates
        content_id = json.dumps(content, sort_keys=True)
        if content_id in self.added_ids:
            return False
        
        added = False
        
        if section == 'basics':
            self.resume['basics'] = content
            added = True
        elif section == 'work' and len(self.resume['work']) < MAX_WORK_ENTRIES:
            self.resume['work'].append(content)
            added = True
        elif section == 'skills' and len(self.resume['skills']) < MAX_SKILLS_ENTRIES:
            self.resume['skills'].append(content)
            added = True
        elif section == 'projects' and len(self.resume['projects']) < MAX_PROJECTS_ENTRIES:
            self.resume['projects'].append(content)
            added = True
        elif section == 'education':
            # Handle education content
            if not self.resume['education']:
                self.resume['education'] = content if isinstance(content, list) else [content]
                added = True
        elif section == 'other':
            # Parse 'other' content for additional sections
            if 'education' in content and not self.resume['education']:
                self.resume['education'] = content['education']
                added = True
        
        if added:
            self.added_ids.add(content_id)
        
        return added
    
    def add_search_results(self, search_results):
        """
        Add multiple search results to the resume.
        
        Args:
            search_results (list): List of search result objects with payload
            
        Returns:
            int: Number of items successfully added
        """
        added_count = 0
        
        for result in search_results:
            content = result.payload if hasattr(result, 'payload') else result
            if self.add_content(content):
                added_count += 1
        
        return added_count
    
    def add_metadata(self, metadata):
        """
        Add metadata to the resume.
        
        Args:
            metadata (dict): Metadata to add
        """
        self.resume["_metadata"] = metadata
    
    def build(self):
        """
        Build and return the final resume object.
        
        Returns:
            dict: Complete resume object
        """
        return self.resume.copy()
    
    def get_stats(self):
        """
        Get statistics about the current resume.
        
        Returns:
            dict: Resume statistics
        """
        return {
            "work_entries": len(self.resume.get('work', [])),
            "skills_entries": len(self.resume.get('skills', [])),
            "projects_entries": len(self.resume.get('projects', [])),
            "education_entries": len(self.resume.get('education', [])),
            "has_basics": bool(self.resume.get('basics')),
            "total_unique_items": len(self.added_ids)
        }


# Unused utility functions removed - use ResumeBuilder class directly