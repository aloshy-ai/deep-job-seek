"""Configuration settings for the Resume Generator API"""
import os

# --- OpenAI API Configuration ---
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "http://localhost:1234/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional for local APIs like LM Studio

# --- Qdrant Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "resume")

# --- API Configuration ---
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8080"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# --- Model Configuration ---
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "15"))

# --- Resume Section Limits ---
MAX_WORK_ENTRIES = int(os.getenv("MAX_WORK_ENTRIES", "3"))
MAX_SKILLS_ENTRIES = int(os.getenv("MAX_SKILLS_ENTRIES", "5"))
MAX_PROJECTS_ENTRIES = int(os.getenv("MAX_PROJECTS_ENTRIES", "2"))

# --- JSON Resume Schema ---
RESUME_SCHEMA_URL = os.getenv("RESUME_SCHEMA_URL", "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json")

# --- Output Configuration ---
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
SAVE_OUTPUT_FILES = os.getenv("SAVE_OUTPUT_FILES", "true").lower() == "true"

# --- Streaming Configuration ---
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"

# --- Reasoning Output Configuration ---
SAVE_REASONING_FILES = os.getenv("SAVE_REASONING_FILES", "true").lower() == "true"