"""Health check utilities for verifying system dependencies on startup"""
import requests
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from .config import (
    OPENAI_API_BASE_URL, OPENAI_API_KEY, 
    QDRANT_URL, QDRANT_COLLECTION_NAME
)

def check_openai_api():
    """Verify OpenAI-compatible API is accessible"""
    print("🔍 Checking OpenAI-compatible API...")
    
    headers = {"Content-Type": "application/json"}
    if OPENAI_API_KEY:
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"
    
    # Test with a minimal request
    test_data = {
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1,
        "temperature": 0
    }
    
    try:
        response = requests.post(
            f"{OPENAI_API_BASE_URL}/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 401:
            print("❌ API authentication failed. Please check your OPENAI_API_KEY.")
            return False
        elif response.status_code == 403:
            print("❌ API access forbidden. Please check your API key permissions.")
            return False
        elif response.status_code >= 400:
            print(f"❌ API request failed with status {response.status_code}: {response.text}")
            return False
        
        print(f"✅ OpenAI-compatible API accessible at {OPENAI_API_BASE_URL}")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {OPENAI_API_BASE_URL}")
        print("   Make sure your API server is running (e.g., LM Studio)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ API request timed out at {OPENAI_API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ API check failed: {str(e)}")
        return False

def check_qdrant_db():
    """Verify Qdrant database is accessible and has required collection"""
    print("🔍 Checking Qdrant database...")
    
    try:
        client = QdrantClient(url=QDRANT_URL)
        
        # Check if server is accessible
        collections = client.get_collections()
        print(f"✅ Qdrant server accessible at {QDRANT_URL}")
        
        # Check if required collection exists
        collection_names = [col.name for col in collections.collections]
        if QDRANT_COLLECTION_NAME not in collection_names:
            print(f"❌ Collection '{QDRANT_COLLECTION_NAME}' not found in Qdrant")
            print(f"   Available collections: {collection_names}")
            print("   Please create and populate the resume collection")
            return False
        
        # Check if collection has data
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        point_count = collection_info.points_count
        
        if point_count == 0:
            print(f"⚠️  Collection '{QDRANT_COLLECTION_NAME}' exists but is empty")
            print("   Please populate the collection with resume data")
            return False
        
        print(f"✅ Collection '{QDRANT_COLLECTION_NAME}' found with {point_count} points")
        return True
        
    except UnexpectedResponse as e:
        print(f"❌ Qdrant server error: {str(e)}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Qdrant at {QDRANT_URL}")
        print("   Make sure Qdrant server is running")
        return False
    except Exception as e:
        print(f"❌ Qdrant check failed: {str(e)}")
        return False

def check_fastembed_model():
    """Verify FastEmbed model is available for embeddings"""
    print("🔍 Checking FastEmbed model...")
    
    try:
        from fastembed import TextEmbedding
        # Try to initialize the model (should be cached from Docker build)
        model = TextEmbedding()
        print("✅ FastEmbed model is available and cached")
        return True
    except ImportError:
        print("❌ FastEmbed not installed. Run: pip install fastembed")
        return False
    except Exception as e:
        print(f"⚠️  FastEmbed model check failed: {str(e)}")
        print("   This may cause slower first request as model downloads")
        return True  # Non-critical, will work but be slower

def run_startup_checks():
    """Run all startup health checks"""
    print("🚀 Running startup health checks...\n")
    
    checks = [
        ("OpenAI API", check_openai_api),
        ("Qdrant Database", check_qdrant_db),
        ("FastEmbed Model", check_fastembed_model)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check crashed: {str(e)}")
            failed_checks.append(check_name)
        print()  # Add spacing between checks
    
    if failed_checks:
        print("❌ Startup checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        print("\n🛠️  Please fix the above issues before starting the server.")
        return False
    
    print("✅ All startup checks passed! Server is ready to start.")
    return True

def run_startup_checks_or_exit():
    """Run startup checks and exit if any fail"""
    if not run_startup_checks():
        print("\n💡 Check the troubleshooting section in README.md for help.")
        sys.exit(1)


if __name__ == "__main__":
    print("🔍 Manual Health Check\n")
    
    if run_startup_checks():
        print("\n🎉 All systems operational! You can now run: python main.py")
    else:
        print("\n❌ Health checks failed. Please fix the issues above.")
        sys.exit(1)