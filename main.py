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
    
    # Show branding on startup
    import subprocess
    try:
        result = subprocess.run(['bash', '-c', 'curl -fsSL https://raw.githubusercontent.com/aloshy-ai/branding/main/ascii.sh | bash'], 
                               capture_output=True, text=True, timeout=5)
        if result.stdout:
            print(result.stdout)
    except:
        pass  # Silently fail if branding unavailable
    
    # Health checks are run when importing the server module
    print(f"\n🚀 Starting Deep Job Seek API on http://{API_HOST}:{API_PORT}")
    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)