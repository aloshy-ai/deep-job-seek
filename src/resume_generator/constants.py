"""Application constants and enums"""

# Resume section types
RESUME_SECTIONS = {
    'BASICS': 'basics',
    'WORK': 'work',
    'SKILLS': 'skills',
    'PROJECTS': 'projects',
    'EDUCATION': 'education',
    'OTHER': 'other'
}

# API response types
API_RESPONSE_TYPES = {
    'SUCCESS': 'success',
    'ERROR': 'error',
    'VALIDATION_ERROR': 'validation_error'
}

# Streaming event types
STREAMING_EVENTS = {
    'ANALYZING': 'analyzing',
    'REASONING': 'reasoning',
    'KEYWORDS': 'keywords',
    'SEARCHING': 'searching',
    'COMPLETE': 'complete',
    'ERROR': 'error',
    'DONE': '[DONE]'
}

# Health check status types
HEALTH_STATUS = {
    'HEALTHY': 'healthy',
    'UNHEALTHY': 'unhealthy',
    'WARNING': 'warning'
}

# Default prompts
KEYWORD_EXTRACTION_PROMPT = """
Analyze the following job description and extract the most critical skills,
technologies, and responsibilities. Return them as a single, dense,
comma-separated string of keywords.

Job Description:
{job_description}
"""

# File patterns
FILENAME_PATTERNS = {
    'RESUME_JSON': '{timestamp}-{job_snippet}.json',
    'TIMESTAMP_FORMAT': '%Y%m%d-%H%M%S',
    'JOB_SNIPPET_LENGTH': 30
}