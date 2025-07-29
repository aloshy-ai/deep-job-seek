"""Flask server for the Resume Generator API"""
from flask import Flask
from .config import API_HOST, API_PORT, DEBUG
from .healthcheck import run_startup_checks_or_exit
from .api.routes import setup_routes


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Run startup checks before defining routes
    run_startup_checks_or_exit()
    
    # Setup API routes
    setup_routes(app)
    
    return app


# Create app instance
app = create_app()


# Entry point moved to main.py