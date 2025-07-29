#!/usr/bin/env python3
"""Script to populate Qdrant with test resume data for debugging"""
import sys
import os

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from resume_generator.config import QDRANT_URL, QDRANT_COLLECTION_NAME

def create_test_resume_data():
    """Create sample resume data for testing"""
    return [
        {
            "id": 1,
            "section": "basics",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "summary": "Full-stack software engineer with 5 years of experience in Python, Flask, and API development",
            "text": "John Doe software engineer Python Flask API development full-stack developer"
        },
        {
            "id": 2,
            "section": "work",
            "company": "Tech Corp",
            "position": "Senior Software Engineer",
            "startDate": "2021-01-01",
            "endDate": "2024-01-01",
            "summary": "Developed REST APIs using Flask and Python, implemented vector search with Qdrant",
            "highlights": ["Built scalable APIs", "Implemented vector search", "Led team of 3 developers"],
            "text": "Senior Software Engineer Tech Corp Flask Python REST APIs vector search Qdrant scalable team lead"
        },
        {
            "id": 3,
            "section": "work",
            "company": "StartupXYZ",
            "position": "Python Developer",
            "startDate": "2019-06-01",
            "endDate": "2020-12-31",
            "summary": "Developed machine learning pipelines and data processing systems",
            "highlights": ["Built ML pipelines", "Data processing", "API integration"],
            "text": "Python Developer StartupXYZ machine learning pipelines data processing API integration"
        },
        {
            "id": 4,
            "section": "skills",
            "name": "Programming Languages",
            "keywords": ["Python", "JavaScript", "SQL", "Bash"],
            "text": "Programming Languages Python JavaScript SQL Bash"
        },
        {
            "id": 5,
            "section": "skills",
            "name": "Frameworks & Tools",
            "keywords": ["Flask", "FastAPI", "Docker", "Qdrant", "PostgreSQL"],
            "text": "Frameworks Tools Flask FastAPI Docker Qdrant PostgreSQL"
        },
        {
            "id": 6,
            "section": "projects",
            "name": "Resume Generator API",
            "description": "Built an AI-powered resume generation system using Flask, Qdrant, and LM Studio",
            "highlights": ["Flask API", "Vector search", "LM Studio integration"],
            "url": "https://github.com/example/resume-generator",
            "text": "Resume Generator API AI-powered Flask Qdrant LM Studio vector search"
        }
    ]

def populate_qdrant():
    """Populate Qdrant with test resume data"""
    print("🔄 Populating Qdrant with test resume data...")
    
    try:
        # Initialize clients
        qdrant_client = QdrantClient(url=QDRANT_URL)
        embedding_model = TextEmbedding()
        
        # Get test data
        test_data = create_test_resume_data()
        
        # Prepare points for insertion
        points = []
        for item in test_data:
            # Generate embedding for the text
            text = item.pop("text")  # Remove text field, use for embedding
            embedding = list(embedding_model.embed([text]))[0].tolist()
            
            points.append({
                "id": item["id"],
                "vector": embedding,
                "payload": item
            })
        
        # Insert points into collection
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        
        print(f"✅ Successfully added {len(points)} points to collection '{QDRANT_COLLECTION_NAME}'")
        
        # Verify insertion
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        print(f"📊 Collection now has {collection_info.points_count} points")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to populate Qdrant: {str(e)}")
        return False

def main():
    """Main function"""
    print("🧪 Test Data Population Script\n")
    
    if populate_qdrant():
        print("\n🎉 Test data population completed successfully!")
        print("💡 You can now run: python healthcheck.py")
    else:
        print("\n❌ Test data population failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()