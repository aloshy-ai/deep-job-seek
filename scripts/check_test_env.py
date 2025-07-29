#!/usr/bin/env python3
"""Test environment setup and verification"""
import sys
import time
import requests
import subprocess
from pathlib import Path

def check_service(url, name):
    """Check if a service is running"""
    try:
        requests.get(url, timeout=5)
        print(f"✅ {name} is running")
        return True
    except requests.RequestException:
        print(f"❌ {name} is not running")
        return False

def main():
    """Main function"""
    print("🔍 Checking test environment...")
    
    # Check required services
    services_ok = True
    if not check_service("http://localhost:1234/v1/models", "LM Studio"):
        print("ℹ️  Start LM Studio and ensure it's running on port 1234")
        services_ok = False
    
    if not check_service("http://localhost:6333/collections", "Qdrant"):
        print("ℹ️  Start Qdrant and ensure it's running on port 6333")
        services_ok = False
    
    # Check test data
    print("\n🔍 Checking test data...")
    try:
        from resume_generator.utils.vector_search import VectorSearchClient
        client = VectorSearchClient()
        collection_info = client.client.get_collection("resume")
        if collection_info.points_count < 1:
            print("ℹ️  Populating test data...")
            subprocess.run([sys.executable, "scripts/populate_test_data.py"], check=True)
        else:
            print(f"✅ Test data exists ({collection_info.points_count} points)")
    except Exception as e:
        print(f"❌ Error checking test data: {e}")
        services_ok = False
    
    if not services_ok:
        print("\n❌ Test environment is not ready")
        sys.exit(1)
    
    print("\n✅ Test environment is ready")
