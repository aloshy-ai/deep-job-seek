"""API route definitions"""
from flask import request, jsonify, Response, stream_with_context
from ..core import create_tailored_resume
from ..services.resume_service import ResumeService
from ..constants import STREAMING_EVENTS
import json


def setup_routes(app):
    """Setup all API routes for the Flask app"""
    
    @app.route('/generate', methods=['POST'])
    def generate():
        """Generate a tailored resume based on job description"""
        job_description = request.json.get('job_description')
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        try:
            tailored_resume_json = create_tailored_resume(job_description)
            return jsonify(tailored_resume_json)
        except Exception as e:
            return jsonify({"error": f"Failed to generate resume: {str(e)}"}), 500

    @app.route('/generate/stream', methods=['POST'])
    def generate_stream():
        """Generate a tailored resume with streaming analysis"""
        job_description = request.json.get('job_description')
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        def generate_stream_response():
            try:
                # Stream the keyword extraction process
                yield f"data: {json.dumps({'step': STREAMING_EVENTS['ANALYZING'], 'message': 'Analyzing job description...'})}\n\n"
                
                # Use service for streaming generation
                keywords_result, final_resume = ResumeService.generate_resume_streaming(job_description)
                
                # Handle reasoning content if available
                if isinstance(keywords_result, dict):
                    keywords = keywords_result.get("content", "")
                    reasoning = keywords_result.get("reasoning", "")
                    if reasoning:
                        yield f"data: {json.dumps({'step': STREAMING_EVENTS['REASONING'], 'content': reasoning})}\n\n"
                else:
                    keywords = keywords_result
                
                yield f"data: {json.dumps({'step': STREAMING_EVENTS['KEYWORDS'], 'content': keywords})}\n\n"
                
                # Continue with vector search and assembly
                yield f"data: {json.dumps({'step': STREAMING_EVENTS['SEARCHING'], 'message': 'Searching resume database...'})}\n\n"
                
                yield f"data: {json.dumps({'step': STREAMING_EVENTS['COMPLETE'], 'resume': final_resume})}\n\n"
                yield f"data: {STREAMING_EVENTS['DONE']}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'step': STREAMING_EVENTS['ERROR'], 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate_stream_response()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "message": "Resume Generator API is running"})