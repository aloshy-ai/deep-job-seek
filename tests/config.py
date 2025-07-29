from resume_generator.config import API_HOST, API_PORT

class TestConfig:
    """Test configuration constants"""
    BASE_URL = f"http://{API_HOST}:{API_PORT}"
    TIMEOUT = 60
    
    # Test data
    SAMPLE_JOB_DESCRIPTION = (
        "Software Engineer position requiring Python, Flask, and API development experience. "
        "Experience with vector databases and machine learning preferred."
    )
    
    SAMPLE_ML_JOB_DESCRIPTION = (
        "Machine Learning Engineer position requiring Python, TensorFlow, and MLOps experience"
    )