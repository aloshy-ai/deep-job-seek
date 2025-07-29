"""API route definitions"""
from flask import request, jsonify, Response, stream_with_context
from ..core import create_tailored_resume
from ..services.resume_service import ResumeService
from ..services.resume_update_service import ResumeUpdateService
from ..services.resume_retrieval_service import ResumeRetrievalService
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

    @app.route('/resume/update', methods=['POST'])
    def update_resume():
        """Update resume data in Qdrant collection"""
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
        
        content = data['content']
        update_mode = data.get('update_mode', 'merge')
        content_type = data.get('content_type', 'auto')
        section_hint = data.get('section_hint')
        
        # Validate update_mode
        if update_mode not in ['merge', 'replace', 'append']:
            return jsonify({"error": "Invalid update_mode. Must be 'merge', 'replace', or 'append'"}), 400
        
        # Validate content_type
        if content_type not in ['auto', 'json', 'markdown', 'text']:
            return jsonify({"error": "Invalid content_type. Must be 'auto', 'json', 'markdown', or 'text'"}), 400
        
        try:
            update_service = ResumeUpdateService()
            result = update_service.update_resume(
                content=content,
                update_mode=update_mode,
                content_type=content_type,
                section_hint=section_hint
            )
            
            if result["success"]:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Internal server error during resume update"
            }), 500

    @app.route('/resume', methods=['GET'])
    def get_resume():
        """Retrieve the complete JSON resume from Qdrant collection"""
        format_type = request.args.get('format', 'json')  # json or pretty
        
        # Validate format parameter
        if format_type not in ['json', 'pretty']:
            return jsonify({"error": "Invalid format. Must be 'json' or 'pretty'"}), 400
        
        try:
            retrieval_service = ResumeRetrievalService()
            result = retrieval_service.get_complete_resume(format_type=format_type)
            
            if result["success"]:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Internal server error during resume retrieval"
            }), 500

    @app.route('/resume/summary', methods=['GET'])
    def get_resume_summary():
        """Get a summary of the current resume without full content"""
        try:
            retrieval_service = ResumeRetrievalService()
            result = retrieval_service.get_resume_summary()
            
            if result["success"]:
                return jsonify(result), 200
            else:
                return jsonify(result), 404
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Internal server error during summary retrieval"
            }), 500

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "message": "Resume Generator API is running"})