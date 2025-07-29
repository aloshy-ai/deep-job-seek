#!/usr/bin/env python3
"""Quick test for human-friendly reasoning output"""
import requests
import os
import pytest
from resume_generator.config import API_HOST, API_PORT

def test_human_reasoning():
    """Test the human-friendly reasoning output"""
    base_url = f"http://{API_HOST}:{API_PORT}"
    url = f"{base_url}/generate"
    
    # Test with a realistic job description
    data = {
        "job_description": "Senior Backend Engineer position requiring Python, Django, PostgreSQL, and AWS experience. Looking for someone with 5+ years experience who can mentor junior developers and lead architecture decisions."
    }
    
    print("🧪 Testing Human-Friendly Reasoning Output")
    print("=" * 50)
    print(f"📡 Connecting to: {base_url}")
    print()
    
    try:
        response = requests.post(url, json=data, timeout=60)
        
        assert response.status_code == 200, f"Error: {response.status_code} - {response.text}"
        result = response.json()
        metadata = result.get("_metadata", {})
        
        if "reasoning_file" not in metadata:
            print("❌ No reasoning file generated")
            return False
        
        reasoning_file = metadata["reasoning_file"]
        print(f"✅ Reasoning file generated: {reasoning_file}")
        
        # Read and analyze the reasoning content
        if os.path.exists(reasoning_file):
            with open(reasoning_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 File size: {len(content)} characters")
            
            # Check for human-friendly sections
            required_sections = [
                "# Why You're Perfect for This Role",
                "## 🎯 **Role Overview**",
                "## 💪 **Your Strongest Qualifications**",
                "## 🔗 **Perfect Skill Alignment**",
                "## 🏆 **Relevant Experience Highlights**",
                "## 🚀 **Unique Value You Bring**",
                "## 📝 **Cover Letter Talking Points**",
                "## 🎯 **Why This Match Works**"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections: {missing_sections}")
                return False
            
            print("✅ All required sections present")
            
            # Check for cover letter elements
            if '"I am excited to apply for' in content:
                print("✅ Cover letter opening statement found")
            else:
                print("⚠️  Cover letter opening not found")
            
            # Check for confidence assessment
            if any(conf in content for conf in ["excellent match", "strong match", "good match"]):
                print("✅ Confidence assessment found")
            else:
                print("⚠️  Confidence assessment not found")
            
            # Show a preview
            print("\n📋 Content Preview:")
            print("-" * 30)
            lines = content.split('\n')
            for line in lines[:15]:  # First 15 lines
                print(line)
            print("...")
            
            assert True
        else:
            pytest.fail(f"Reasoning file not found at: {reasoning_file}")
            
    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to API. Is the server running?")
    except requests.exceptions.Timeout:
        pytest.fail("Request timed out")
    except Exception as e:
        pytest.fail(f"Error: {e}")