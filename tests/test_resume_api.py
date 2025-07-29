#!/usr/bin/env python3
"""Integration test script for the Resume Generator API

This script provides a simple way to run integration tests against a running server.
For more comprehensive testing, use pytest with the organized test suite.
"""
import sys
import os

from tests.config import TestConfig
from .test_health import TestHealthEndpoint
from .test_generate import TestGenerateEndpoint
import requests


def run_integration_tests():
    """Run basic integration tests against running server"""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    config = TestConfig()
    health_tester = TestHealthEndpoint()
    generate_tester = TestGenerateEndpoint()
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        health_tester.test_health_endpoint_responds(config)
        print("✅ Health endpoint OK")
        
        # Test generate endpoint
        print("2. Testing generate endpoint...")
        generate_tester.test_generate_endpoint_success(config)
        print("✅ Generate endpoint OK")
        
        # Test error handling
        print("3. Testing error handling...")
        generate_tester.test_generate_endpoint_missing_job_description(config)
        print("✅ Error handling OK")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print(f"   Expected server at: {config.BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point"""
    print(f"Testing API at: {TestConfig.BASE_URL}")
    print("Note: Use 'pytest' for comprehensive testing with the full test suite")
    print()
    
    success = run_integration_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()