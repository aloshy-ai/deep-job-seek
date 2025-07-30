# Deep Job Seek

AI-powered REST API that generates tailored resumes from job descriptions using vector search and OpenAI-compatible models.

## Quick Start

### Option 1: Full Docker (Recommended)
```bash
git clone https://github.com/aloshy-ai/deep-job-seek.git
cd deep-job-seek
docker-compose up --build -d
```
API available at `http://localhost:8000`

### Option 2: Local Development
```bash
git clone https://github.com/aloshy-ai/deep-job-seek.git
cd deep-job-seek
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d qdrant
python scripts/populate_test_data.py
python main.py
```

## Prerequisites
- Docker & Docker Compose
- OpenAI-compatible API (e.g., [LM Studio](https://lmstudio.ai/)) 
- Python 3.8+ (for local development)

## API Endpoints

### Core Endpoints
- **POST `/generate`** - Generate tailored resume from job description
- **POST `/generate/stream`** - Stream generation with real-time updates  
- **POST `/resume/replace`** - Replace entire resume with AI parsing *(recommended)*
- **GET `/resume`** - Retrieve complete resume data
- **GET `/health`** - System status check

### Example Usage
```bash
# Generate resume from job description
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Senior Python Developer..."}'

# Replace resume with new content (any format: markdown, text, JSON)
curl -X POST http://localhost:8000/resume/replace \
  -H "Content-Type: application/json" \
  -d '{"content": "# John Doe\nSenior Developer at TechCorp..."}'
```

## Configuration
Key environment variables:
```bash
OPENAI_API_BASE_URL=http://localhost:1234/v1  # LM Studio default
QDRANT_HOST=qdrant                            # Docker service name
API_PORT=8000
```

## Development

### Testing
```bash
# Local testing
pytest

# Docker testing  
docker-compose exec generator pytest
```

### Docker Operations
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## How It Works
1. **AI Analysis** - Job description analyzed for key requirements
2. **Vector Search** - Relevant experience found using Qdrant similarity search  
3. **Smart Assembly** - Resume sections assembled into JSON Resume format
4. **Tailored Output** - Customized resume + cover letter talking points

## Tech Stack
- **Backend**: Python Flask with service layer architecture
- **Database**: Qdrant vector database for semantic search
- **AI**: OpenAI-compatible APIs (LM Studio, OpenAI, etc.)
- **Embeddings**: BAAI/bge-small-en-v1.5 via FastEmbed
- **Container**: Docker with docker-compose support

## Troubleshooting
- **Port conflicts**: Change ports in `docker-compose.yml`
- **LM Studio not found**: Ensure running on `localhost:1234`
- **Empty database**: Restart services to auto-populate data
- **Container issues**: Check `docker-compose logs <service>`

## License
MIT