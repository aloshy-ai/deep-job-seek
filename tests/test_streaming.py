#!/usr/bin/env python3
"""Standalone streaming test script

This is a manual test script for streaming functionality.
For comprehensive automated testing, use: pytest tests/test_streaming.py
"""
import requests
import json
import pytest
from resume_generator.config import API_HOST, API_PORT

def test_streaming():
    """Test the streaming endpoint"""
    base_url = f"http://{API_HOST}:{API_PORT}"
    url = f"{base_url}/generate/stream"
    
    # Sample job descriptions for testing
    SAMPLE_JOBS = {
        "ml_engineer": "Machine Learning Engineer position requiring Python, TensorFlow, and MLOps experience",
        "backend_dev": "Backend Developer role with Node.js, Express, and MongoDB experience",
        "devops": "DevOps Engineer position requiring Docker, Kubernetes, and AWS experience"
    }
    
    data = {
        "job_description": SAMPLE_JOBS["ml_engineer"]
    }
    
    response = requests.post(url, json=data, stream=True)
    assert response.status_code == 200, f"Error: {response.status_code} - {response.text}"
    print("=" * 50)
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
        
        print("📡 Streaming response:")
        print("-" * 30)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str.strip() == '[DONE]':
                        print("✅ Stream completed!")
                        break
                    
                    try:
                        data = json.loads(data_str)
                        step = data.get('step', 'unknown')
                        
                        if step == 'analyzing':
                            print(f"🔍 {data.get('message', '')}")
                        elif step == 'reasoning':
                            print(f"🧠 Reasoning: {data.get('content', '')[:100]}...")
                        elif step == 'keywords':
                            print(f"🔑 Keywords: {data.get('content', '')}")
                        elif step == 'searching':
                            print(f"🔎 {data.get('message', '')}")
                        elif step == 'complete':
                            resume = data.get('resume', {})
                            print(f"📄 Resume generated with {len(resume.get('work', []))} work entries")
                            print(f"📊 Skills: {len(resume.get('skills', []))} categories")
                        elif step == 'error':
                            print(f"❌ Error: {data.get('message', '')}")
                            return False
                            
                    except json.JSONDecodeError:
                        print(f"📝 Raw: {data_str}")
        
        assert True
        
    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to API. Is the server running?")
    except requests.exceptions.Timeout:
        pytest.fail("Request timed out")
    except Exception as e:
        pytest.fail(f"Error: {e}")