"""Advanced AI-powered resume parser for complex, messy text scenarios"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from ..utils.api_client import APIClient


class AdvancedResumeParser:
    """
    Intelligent parser that handles crazy, messy, real-world text dumps
    and converts them into perfect JSON Resume format
    """
    
    def __init__(self):
        self.ai_client = APIClient()
        
        # Entity normalization mappings
        self.company_aliases = {
            'google': ['google', 'alphabet inc', 'alphabet', 'google llc', 'google inc'],
            'meta': ['meta', 'facebook', 'fb', 'meta platforms'],
            'microsoft': ['microsoft', 'msft', 'ms'],
            'amazon': ['amazon', 'amzn', 'aws'],
            'apple': ['apple', 'apple inc', 'cupertino'],
            'netflix': ['netflix', 'nflx'],
            'tesla': ['tesla', 'tesla motors'],
            'openai': ['openai', 'open ai', 'chatgpt company'],
            'anthropic': ['anthropic', 'claude company']
        }
        
        self.location_aliases = {
            'san francisco': ['sf', 'san francisco', 'san francisco, ca', 'bay area'],
            'new york': ['nyc', 'new york', 'new york city', 'manhattan', 'brooklyn'],
            'seattle': ['seattle', 'seattle, wa', 'amazon hq', 'microsoft area'],
            'austin': ['austin', 'austin, tx', 'atx'],
            'los angeles': ['la', 'los angeles', 'los angeles, ca', 'hollywood']
        }
        
        # Tech abbreviation mappings
        self.tech_mappings = {
            'k8s': 'Kubernetes',
            'tf': 'Terraform', 
            'aws': 'Amazon Web Services',
            'gcp': 'Google Cloud Platform',
            'ddb': 'DynamoDB',
            'rds': 'Amazon RDS',
            's3': 'Amazon S3',
            'ec2': 'Amazon EC2',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'golang': 'Go',
            'reactjs': 'React',
            'nodejs': 'Node.js',
            'ml': 'Machine Learning',
            'ai': 'Artificial Intelligence',
            'nlp': 'Natural Language Processing',
            'cv': 'Computer Vision',
            'devops': 'DevOps',
            'ci/cd': 'CI/CD',
            'rest': 'REST API',
            'graphql': 'GraphQL'
        }
    
    def parse_complex_text(self, text: str, existing_resume_data: List[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Main method to parse complex, messy text into structured resume data
        
        Args:
            text: Raw, messy text input
            existing_resume_data: Current resume data from Qdrant for context
            
        Returns:
            Structured resume sections
        """
        try:
            # Step 1: Pre-process and normalize the text
            cleaned_text = self._preprocess_text(text)
            
            # Step 2: Extract entities and normalize them
            entities = self._extract_and_normalize_entities(cleaned_text)
            
            # Step 3: Use advanced AI parsing with context
            parsed_data = self._ai_parse_with_context(cleaned_text, entities, existing_resume_data)
            
            # Step 4: Reconstruct timeline and resolve conflicts
            structured_data = self._reconstruct_timeline_and_resolve_conflicts(parsed_data, existing_resume_data)
            
            # Step 5: Apply domain knowledge and inferences
            final_data = self._apply_domain_knowledge(structured_data)
            
            return final_data
            
        except Exception as e:
            raise ValueError(f"Failed to parse complex text: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize messy text input"""
        
        # Remove emojis but preserve their meaning
        emoji_replacements = {
            '📧': 'email:',
            '📱': 'phone:',
            '🐍': '',  # Python snake emoji
            '⚡': '',
            '🚀': '',
            '💼': '',
            '🏢': 'company:',
            '📅': 'date:',
            '🎓': 'education:',
            '💻': '',
            '🔧': 'tools:',
            '🌟': ''
        }
        
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
        
        # Normalize common separators
        text = re.sub(r'\s*\|\s*', ' | ', text)  # Standardize pipe separators
        text = re.sub(r'\s*/\s*', '/', text)     # Clean slashes
        text = re.sub(r'\s+', ' ', text)         # Multiple spaces to single
        
        # Fix common OCR/copy-paste errors
        ocr_fixes = {
            r'\bl\b': 'I',           # lowercase l to uppercase I
            r'\b0\b': 'O',           # zero to O in contexts
            r'(\d),(\d)': r'\1,\2',  # Fix comma spacing in numbers
            r'@\s+': '@',            # Fix email spacing
            r'\(\s+': '(',           # Fix parenthesis spacing
            r'\s+\)': ')'
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)
        
        return text.strip()
    
    def _extract_and_normalize_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract and normalize key entities like companies, locations, technologies"""
        
        entities = {
            'companies': [],
            'locations': [],
            'technologies': [],
            'universities': [],
            'dates': [],
            'emails': [],
            'phones': []
        }
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        entities['emails'] = emails
        
        # Extract phone numbers
        phones = re.findall(r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', text)
        entities['phones'] = phones
        
        # Extract years and dates
        dates = re.findall(r'\b(19|20)\d{2}\b', text)
        date_ranges = re.findall(r'\b(19|20)\d{2}[-–—]\s*(19|20)\d{2}\b', text)
        entities['dates'] = dates + [d[0] for d in date_ranges]
        
        # Normalize company names
        text_lower = text.lower()
        for canonical, aliases in self.company_aliases.items():
            for alias in aliases:
                if alias in text_lower:
                    entities['companies'].append(canonical.title())
                    break
        
        # Normalize locations  
        for canonical, aliases in self.location_aliases.items():
            for alias in aliases:
                if alias in text_lower:
                    entities['locations'].append(canonical.title())
                    break
        
        # Normalize technologies
        for abbrev, full_name in self.tech_mappings.items():
            if re.search(r'\b' + re.escape(abbrev) + r'\b', text_lower):
                entities['technologies'].append(full_name)
        
        # Extract university patterns
        university_patterns = [
            r'\b(Stanford|MIT|Harvard|Berkeley|CMU|Caltech|Princeton|Yale)\b',
            r'\b([A-Z][a-z]+\s+(?:University|Institute|College))\b',
            r'\b(University\s+of\s+[A-Z][a-z]+)\b'
        ]
        
        for pattern in university_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['universities'].extend([match if isinstance(match, str) else match[0] for match in matches])
        
        return entities
    
    def _ai_parse_with_context(self, text: str, entities: Dict, existing_data: List[Dict]) -> Dict:
        """Use advanced AI prompting with extracted entities and existing context"""
        
        # Build context from existing resume data
        context_summary = self._build_context_summary(existing_data) if existing_data else "No existing resume data."
        
        # Create comprehensive prompt
        prompt = f"""
        You are an expert resume parser with deep understanding of tech industry context, career progression, and implicit information. Parse the following messy, real-world text dump into perfect JSON Resume schema format.

        EXISTING RESUME CONTEXT:
        {context_summary}

        EXTRACTED ENTITIES:
        - Companies: {entities.get('companies', [])}
        - Locations: {entities.get('locations', [])}
        - Technologies: {entities.get('technologies', [])}
        - Universities: {entities.get('universities', [])}
        - Dates: {entities.get('dates', [])}
        - Emails: {entities.get('emails', [])}
        - Phones: {entities.get('phones', [])}

        TEXT TO PARSE:
        "{text}"

        INTELLIGENCE REQUIREMENTS:
        1. **Timeline Reconstruction**: Infer logical job progression and fill gaps
        2. **Context Inference**: Understand implicit information (e.g., "pandemic started" = ~2020)
        3. **Entity Resolution**: Use canonical company names, normalize locations
        4. **Contradiction Handling**: Resolve conflicts with existing data intelligently
        5. **Gap Analysis**: Identify and logically fill missing information
        6. **Career Logic**: Apply tech career progression understanding (L4→L5→L6, SDE→Senior→Staff)
        7. **Cultural Context**: Understand tech industry jargon, abbreviations, slang
        8. **Casual Language**: Parse conversational, informal descriptions

        SPECIFIC CHALLENGES TO HANDLE:
        - Informal language: "btw", "lol", "some ML stuff"
        - Abbreviations: "K8s", "FAANG", "YC startup"  
        - Implicit dates: "since pandemic", "last year", "recently"
        - Vague descriptions: "unicorn startup", "big tech", "some cloud stuff"
        - Career progression: Infer levels, promotions, logical advancement
        - Context clues: "employee #45" = early startup employee
        - Salary mentions: Extract but don't include in resume
        - Side projects: Include if substantial

        OUTPUT FORMAT - JSON Resume Schema:
        {{
            "basics": {{
                "name": "Full Name",
                "email": "normalized@email.com",
                "phone": "+1-555-0123",
                "location": {{"city": "City", "region": "State"}},
                "summary": "Professional summary synthesized from context"
            }},
            "work": [{{
                "company": "Canonical Company Name",
                "position": "Normalized Title",
                "startDate": "YYYY-MM-DD",
                "endDate": "YYYY-MM-DD or null if current",
                "summary": "Clear, professional description",
                "highlights": ["Specific achievements", "Technologies used"],
                "location": "City, State"
            }}],
            "education": [{{
                "institution": "Full University Name",
                "area": "Major/Field",
                "studyType": "Degree Type",
                "startDate": "YYYY-MM-DD",
                "endDate": "YYYY-MM-DD",
                "gpa": "X.X if mentioned"
            }}],
            "skills": [{{
                "name": "Category Name",
                "keywords": ["Normalized", "Technology", "Names"]
            }}],
            "projects": [{{
                "name": "Project Name",
                "description": "Clear description",
                "highlights": ["Key technologies", "Scale/impact"],
                "url": "URL if mentioned"
            }}]
        }}

        RETURN ONLY VALID JSON. No explanations, no markdown formatting.
        """
        
        try:
            response = self.ai_client.query(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("AI could not generate valid JSON")
                
        except Exception as e:
            raise ValueError(f"AI parsing failed: {str(e)}")
    
    def _build_context_summary(self, existing_data: List[Dict]) -> str:
        """Build a summary of existing resume data for AI context"""
        
        if not existing_data:
            return "No existing resume data."
        
        summary_parts = []
        
        # Group by section
        sections = {}
        for entry in existing_data:
            section = entry.get('section', 'unknown')
            if section not in sections:
                sections[section] = []
            sections[section].append(entry)
        
        # Summarize each section
        for section, entries in sections.items():
            if section == 'basics':
                basics = entries[0] if entries else {}
                summary_parts.append(f"Current contact: {basics.get('name', 'Unknown')} <{basics.get('email', 'no email')}>")
                
            elif section == 'work':
                companies = [e.get('company', 'Unknown') for e in entries]
                positions = [e.get('position', 'Unknown') for e in entries]
                summary_parts.append(f"Work history: {len(entries)} positions at {', '.join(set(companies))}")
                summary_parts.append(f"Recent positions: {', '.join(positions[:3])}")
                
            elif section == 'skills':
                all_keywords = []
                for entry in entries:
                    keywords = entry.get('keywords', [])
                    if isinstance(keywords, list):
                        all_keywords.extend(keywords)
                summary_parts.append(f"Current skills: {', '.join(all_keywords[:10])}")
                
            elif section == 'education':
                schools = [e.get('institution', 'Unknown') for e in entries]
                summary_parts.append(f"Education: {', '.join(schools)}")
        
        return "; ".join(summary_parts)
    
    def _reconstruct_timeline_and_resolve_conflicts(self, parsed_data: Dict, existing_data: List[Dict]) -> Dict:
        """Reconstruct logical timeline and resolve any conflicts"""
        
        if 'work' not in parsed_data:
            return parsed_data
        
        work_entries = parsed_data['work']
        
        # Sort by start date, handling missing dates
        def get_sort_date(entry):
            start_date = entry.get('startDate')
            if start_date:
                try:
                    return datetime.strptime(start_date, '%Y-%m-%d')
                except:
                    # Try year-only format
                    try:
                        return datetime.strptime(start_date, '%Y')
                    except:
                        return datetime.now()
            return datetime.now()
        
        work_entries.sort(key=get_sort_date)
        
        # Fill in missing end dates based on next job start dates
        for i, entry in enumerate(work_entries):
            if entry.get('endDate') is None and i < len(work_entries) - 1:
                next_start = work_entries[i + 1].get('startDate')
                if next_start:
                    try:
                        next_date = datetime.strptime(next_start, '%Y-%m-%d')
                        # Set end date to one day before next job
                        end_date = next_date - timedelta(days=1)
                        entry['endDate'] = end_date.strftime('%Y-%m-%d')
                    except:
                        pass
        
        # Resolve conflicts with existing data
        if existing_data:
            parsed_data = self._resolve_conflicts_with_existing(parsed_data, existing_data)
        
        return parsed_data
    
    def _resolve_conflicts_with_existing(self, new_data: Dict, existing_data: List[Dict]) -> Dict:
        """Intelligently resolve conflicts between new and existing data"""
        
        # This is a simplified version - in practice, you'd want more sophisticated logic
        # For now, we'll prefer newer information but preserve unique existing entries
        
        existing_by_section = {}
        for entry in existing_data:
            section = entry.get('section', 'unknown')
            if section not in existing_by_section:
                existing_by_section[section] = []
            existing_by_section[section].append(entry)
        
        # For work experience, merge based on company+position similarity
        if 'work' in new_data and 'work' in existing_by_section:
            new_work = new_data['work']
            existing_work = existing_by_section['work']
            
            # Simple conflict resolution: prefer new data but keep unique existing entries
            merged_work = new_work.copy()
            
            for existing_entry in existing_work:
                existing_company = existing_entry.get('company', '').lower()
                existing_position = existing_entry.get('position', '').lower()
                
                # Check if this entry is already covered by new data
                is_duplicate = False
                for new_entry in new_work:
                    new_company = new_entry.get('company', '').lower()
                    new_position = new_entry.get('position', '').lower()
                    
                    if existing_company in new_company or new_company in existing_company:
                        if existing_position in new_position or new_position in existing_position:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    merged_work.append(existing_entry)
            
            new_data['work'] = merged_work
        
        return new_data
    
    def _apply_domain_knowledge(self, data: Dict) -> Dict:
        """Apply tech industry domain knowledge and intelligent inferences"""
        
        # Infer missing information based on context
        if 'work' in data:
            for entry in data['work']:
                # Infer seniority levels
                position = entry.get('position', '').lower()
                if 'staff' in position and 'senior' not in position:
                    entry['seniority_level'] = 'Staff'
                elif 'principal' in position:
                    entry['seniority_level'] = 'Principal'
                elif 'senior' in position:
                    entry['seniority_level'] = 'Senior'
                elif any(x in position for x in ['lead', 'tech lead']):
                    entry['seniority_level'] = 'Lead'
                
                # Infer company stage
                company = entry.get('company', '').lower()
                if any(x in company for x in ['google', 'meta', 'microsoft', 'amazon', 'apple']):
                    entry['company_stage'] = 'Big Tech'
                elif 'startup' in entry.get('summary', '').lower():
                    entry['company_stage'] = 'Startup'
                
                # Enhance highlights with inferred information
                highlights = entry.get('highlights', [])
                summary = entry.get('summary', '').lower()
                
                # Infer scale from context
                if any(x in summary for x in ['million', 'scale', 'high traffic']):
                    if 'Scale' not in str(highlights):
                        highlights.append('Large-scale systems')
                
                # Infer leadership from context
                if any(x in summary for x in ['team', 'lead', 'manage', 'mentor']):
                    if not any('lead' in str(h).lower() for h in highlights):
                        highlights.append('Technical leadership')
                
                entry['highlights'] = highlights
        
        return data