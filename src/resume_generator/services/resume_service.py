"""Resume generation service"""
from ..utils.api_client import query_model
from ..utils.vector_search import search_resume_content
from ..utils.resume_builder import ResumeBuilder
from ..utils.file_utils import save_resume_files
from ..utils.reasoning_generator import create_reasoning_generator
from ..constants import KEYWORD_EXTRACTION_PROMPT
from ..config import SAVE_REASONING_FILES


class ResumeService:
    """Service for resume generation operations"""
    
    @staticmethod
    def extract_keywords(job_description):
        """
        Extract keywords from job description using AI.
        
        Args:
            job_description (str): Job description text
            
        Returns:
            str or dict: Extracted keywords (may include reasoning)
        """
        prompt = KEYWORD_EXTRACTION_PROMPT.format(job_description=job_description)
        return query_model(prompt)
    
    @staticmethod
    def extract_keywords_streaming(job_description):
        """
        Extract keywords from job description using streaming AI.
        
        Args:
            job_description (str): Job description text
            
        Returns:
            str or dict: Extracted keywords with potential reasoning
        """
        prompt = KEYWORD_EXTRACTION_PROMPT.format(job_description=job_description)
        return query_model(prompt, stream=True)
    
    @staticmethod
    def search_relevant_content(keywords):
        """
        Search for relevant resume content using keywords.
        
        Args:
            keywords (str): Search keywords
            
        Returns:
            list: Search results from vector database
        """
        # Handle both string keywords and dict with content
        if isinstance(keywords, dict):
            search_text = keywords.get("content", "")
        else:
            search_text = keywords
        
        return search_resume_content(search_text.strip())
    
    @staticmethod
    def build_tailored_resume(search_results):
        """
        Build a tailored resume from search results.
        
        Args:
            search_results (list): Search results from vector database
            
        Returns:
            dict: Built resume object
        """
        builder = ResumeBuilder()
        builder.add_search_results(search_results)
        return builder.build()
    
    @staticmethod
    def generate_resume(job_description):
        """
        Generate a complete tailored resume with optional reasoning.
        
        Args:
            job_description (str): Job description to tailor for
            
        Returns:
            dict: Complete resume with metadata
        """
        # Create reasoning generator if enabled
        reasoning = create_reasoning_generator() if SAVE_REASONING_FILES else None
        
        # Extract keywords
        keywords_result = ResumeService.extract_keywords(job_description)
        keywords = keywords_result.get("content", keywords_result) if isinstance(keywords_result, dict) else keywords_result
        ai_reasoning = keywords_result.get("reasoning", "") if isinstance(keywords_result, dict) else ""
        
        # Set job analysis in reasoning
        if reasoning:
            reasoning.set_job_analysis(job_description, keywords, ai_reasoning)
        
        # Search relevant content
        search_results = ResumeService.search_relevant_content(keywords)
        
        # Set search results in reasoning
        if reasoning:
            reasoning.set_search_results(search_results)
        
        # Build resume with reasoning tracking
        builder = ResumeBuilder()
        selected_content = {}
        omitted_content = {}
        
        # Track content selection
        for result in search_results:
            content = result.payload if hasattr(result, 'payload') else result
            section = content.get('section', 'unknown')
            
            if builder.add_content(content):
                # Content was added
                if section not in selected_content:
                    selected_content[section] = []
                selected_content[section].append({
                    **content,
                    '_relevance_score': getattr(result, 'score', 'N/A')
                })
            else:
                # Content was omitted
                if section not in omitted_content:
                    omitted_content[section] = []
                omitted_content[section].append({
                    **content,
                    '_relevance_score': getattr(result, 'score', 'N/A')
                })
        
        resume = builder.build()
        
        # Set content selection in reasoning
        if reasoning:
            reasoning.set_content_selection(selected_content, omitted_content)
        
        # Generate reasoning markdown
        reasoning_content = None
        if reasoning:
            reasoning.set_metadata({
                "generated_at": builder.get_stats().get("generation_time", "N/A"),
                "output_file": "TBD"  # Will be set after file save
            })
            reasoning_content = reasoning.generate_reasoning_markdown()
        
        # Save to files and add metadata
        file_info = save_resume_files(resume, job_description[:50], reasoning_content)
        if file_info:
            resume["_metadata"] = {
                "generated_at": file_info["timestamp"],
                "output_file": file_info["json_file"]
            }
            if "reasoning_file" in file_info:
                resume["_metadata"]["reasoning_file"] = file_info["reasoning_file"]
        
        return resume
    
    @staticmethod
    def generate_resume_streaming(job_description):
        """
        Generate a resume with streaming keyword extraction and reasoning.
        
        Args:
            job_description (str): Job description to tailor for
            
        Returns:
            tuple: (keywords_result, final_resume)
        """
        # Create reasoning generator if enabled
        reasoning = create_reasoning_generator() if SAVE_REASONING_FILES else None
        
        # Extract keywords with streaming
        keywords_result = ResumeService.extract_keywords_streaming(job_description)
        keywords = keywords_result.get("content", keywords_result) if isinstance(keywords_result, dict) else keywords_result
        ai_reasoning = keywords_result.get("reasoning", "") if isinstance(keywords_result, dict) else ""
        
        # Set job analysis in reasoning
        if reasoning:
            reasoning.set_job_analysis(job_description, keywords, ai_reasoning)
        
        # Search and build resume with reasoning tracking
        search_results = ResumeService.search_relevant_content(keywords_result)
        
        if reasoning:
            reasoning.set_search_results(search_results)
        
        # Build resume with content tracking
        builder = ResumeBuilder()
        selected_content = {}
        omitted_content = {}
        
        for result in search_results:
            content = result.payload if hasattr(result, 'payload') else result
            section = content.get('section', 'unknown')
            
            if builder.add_content(content):
                if section not in selected_content:
                    selected_content[section] = []
                selected_content[section].append({
                    **content,
                    '_relevance_score': getattr(result, 'score', 'N/A')
                })
            else:
                if section not in omitted_content:
                    omitted_content[section] = []
                omitted_content[section].append({
                    **content,
                    '_relevance_score': getattr(result, 'score', 'N/A')
                })
        
        resume = builder.build()
        
        # Generate reasoning if enabled
        reasoning_content = None
        if reasoning:
            reasoning.set_content_selection(selected_content, omitted_content)
            reasoning.set_metadata({
                "generated_at": "TBD",
                "output_file": "TBD"
            })
            reasoning_content = reasoning.generate_reasoning_markdown()
        
        # Save to files and add metadata
        file_info = save_resume_files(resume, job_description[:50], reasoning_content)
        if file_info:
            resume["_metadata"] = {
                "generated_at": file_info["timestamp"],
                "output_file": file_info["json_file"]
            }
            if "reasoning_file" in file_info:
                resume["_metadata"]["reasoning_file"] = file_info["reasoning_file"]
        
        return keywords_result, resume