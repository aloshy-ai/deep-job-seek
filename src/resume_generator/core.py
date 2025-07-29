"""Core resume generation functionality - simplified entry points"""
from .services.resume_service import ResumeService
from .utils.api_client import query_model



def create_tailored_resume(job_description):
    """
    Create a tailored resume based on a job description.
    
    Args:
        job_description (str): The job description to tailor the resume for
        
    Returns:
        dict: A JSON resume following the JSON Resume schema
    """
    return ResumeService.generate_resume(job_description)