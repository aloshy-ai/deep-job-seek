"""File handling utilities"""
import os
import json
import re
from datetime import datetime
from ..config import OUTPUT_DIR, SAVE_OUTPUT_FILES


def sanitize_filename(text, max_length=30):
    """
    Sanitize text for use in filenames.
    
    Args:
        text (str): Text to sanitize
        max_length (int): Maximum length of sanitized text
        
    Returns:
        str: Sanitized filename component
    """
    if not text:
        return "resume"
    
    # Clean filename: lowercase, replace spaces/special chars with hyphens
    sanitized = re.sub(r'[^\w\s-]', '', text[:max_length].lower())
    sanitized = re.sub(r'[-\s_]+', '-', sanitized).strip('-')
    return sanitized or "resume"


def generate_timestamped_filename(job_description_snippet="", extension="json"):
    """
    Generate a timestamped filename.
    
    Args:
        job_description_snippet (str): Job description snippet for filename
        extension (str): File extension (without dot)
        
    Returns:
        str: Timestamped filename
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    job_snippet = sanitize_filename(job_description_snippet)
    return f"{timestamp}-{job_snippet}.{extension}"


def ensure_output_directory():
    """Ensure the output directory exists."""
    if SAVE_OUTPUT_FILES:
        os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_json_file(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data (dict): Data to save
        filename (str): Filename (including path)
        
    Returns:
        str: Full path to saved file
    """
    ensure_output_directory()
    full_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return full_path


def save_resume_files(resume_data, job_description_snippet="", reasoning_content=None):
    """
    Save resume data to output files.
    
    Args:
        resume_data (dict): Resume data to save
        job_description_snippet (str): Job description snippet for filename
        reasoning_content (str): Optional reasoning markdown content
        
    Returns:
        dict or None: File information if saved, None if saving disabled
    """
    if not SAVE_OUTPUT_FILES:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_filename = generate_timestamped_filename(job_description_snippet, "json")
    
    # Save JSON file
    json_file = save_json_file(resume_data, base_filename)
    
    result = {
        "json_file": json_file,
        "timestamp": timestamp,
        "filename": base_filename
    }
    
    # Save reasoning markdown file if provided
    if reasoning_content:
        reasoning_filename = base_filename.replace('.json', '-reasoning.md')
        reasoning_file = save_text_file(reasoning_content, reasoning_filename)
        result["reasoning_file"] = reasoning_file
        result["reasoning_filename"] = reasoning_filename
    
    return result


def save_text_file(content, filename):
    """
    Save text content to a file.
    
    Args:
        content (str): Text content to save
        filename (str): Filename (including path)
        
    Returns:
        str: Full path to saved file
    """
    ensure_output_directory()
    full_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return full_path