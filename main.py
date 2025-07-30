#!/usr/bin/env python3
"""Main entry point for Deep Job Seek"""
import sys
import os

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from resume_generator.server import app

if __name__ == '__main__':
    from resume_generator.config import API_HOST, API_PORT, DEBUG
    # Health checks are run when importing the server module
    print(f"\n🚀 Starting Deep Job Seek API on http://{API_HOST}:{API_PORT}")
    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)