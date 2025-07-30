# Deep Job Seek

AI-powered REST API that generates tailored resumes from job descriptions using vector search and OpenAI-compatible models.

## Quick Start

### One-Line Run (No Clone Required)
```bash
curl -sSL https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/run.sh | bash
```
**That's it!** API runs at `http://localhost:8000`

### Manual Docker Compose
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/docker-compose.yml
docker-compose up -d
```

## Prerequisites
- Docker (that's it!)
- OpenAI-compatible API (e.g., [LM Studio](https://lmstudio.ai/)) running locally

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

### Getting Started

1.  **Clone the repository and navigate to the project root**

2.  **Build and Start Services:**

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    - Build the application's Docker image.
    - Pull the Qdrant Docker image.
    - Start both the `generator` application and `qdrant` services in detached mode.
    - Automatically populate the Qdrant database with test data on first run.

3.  **Verify Services:**

    ```bash
    docker-compose ps
    ```

    You should see both `generator` and `qdrant` services listed as `Up`.

### Running Tests

Tests should be run inside the `generator` container to ensure a consistent environment.

```bash
# Install test dependencies and run all tests
docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest"

# Run specific test files or directories
docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest tests/unit/"
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