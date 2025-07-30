"""Flask server for Deep Job Seek"""
import os
from flask import Flask
from .config import API_HOST, API_PORT, DEBUG
from .healthcheck import run_startup_checks_or_exit
from .api.routes import setup_routes


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Run startup checks before defining routes (unless skipped for testing)
    if not os.environ.get('SKIP_STARTUP_CHECKS'):
        run_startup_checks_or_exit()
    
    # Setup API routes
    setup_routes(app)
    
    return app


# Create app instance
app = create_app()


# Entry point moved to main.py

if __name__ == '__main__':
    print(f"\n🚀 Starting Deep Job Seek API on http://{API_HOST}:{API_PORT}")
    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)