"""Test configuration and shared fixtures"""
import pytest
import sys
import os

# Add src to Python path
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from resume_generator.config import API_HOST, API_PORT
from resume_generator.server import create_app
from tests.config import TestConfig


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return TestConfig


@pytest.fixture(scope="session") 
def app():
    """Create and configure a new app instance for each test session"""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """A test runner for the app's Click commands"""
    return app.test_cli_runner()


# URL builders
def build_url(endpoint: str, base_url: str = None) -> str:
    """Build full URL for endpoint"""
    base = base_url or TestConfig.BASE_URL
    return f"{base}{endpoint}"


def build_health_url(base_url: str = None) -> str:
    """Build health check URL"""
    return build_url("/health", base_url)


def build_generate_url(base_url: str = None) -> str:
    """Build generate endpoint URL"""
    return build_url("/generate", base_url)


def build_generate_stream_url(base_url: str = None) -> str:
    """Build streaming generate endpoint URL"""
    return build_url("/generate/stream", base_url)