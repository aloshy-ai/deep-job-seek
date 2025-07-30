# Deep Job Seek

AI-powered REST API that generates tailored resumes from job descriptions using vector search and OpenAI-compatible models.

## Quick Start

### Development Setup (Recommended)
```bash
git clone https://github.com/aloshy-ai/deep-job-seek.git
cd deep-job-seek
docker-compose up --build -d
```
**That's it!** API runs at `http://localhost:8000`

### One-Line Run (Coming Soon)
*Note: Pre-built Docker images are not yet published. Use the development setup above for now.*
```bash
# This will work once Docker images are published to a registry
curl -sSL https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/run.sh | bash
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
    make run
    # or
    docker-compose up --build -d
    ```

    This will:
    - Build the application's Docker image
    - Pull the Qdrant Docker image
    - Start both services in detached mode
    - Automatically populate the Qdrant database with test data

3.  **Verify Services:**

    ```bash
    docker-compose ps
    ```

    You should see both `generator` and `qdrant` services as `Up`.

### Available Commands

```bash
make help              # Show all available commands
make build             # Build Docker images
make run               # Start all services  
make stop              # Stop all services
make test              # Run tests
make logs              # Follow container logs
make shell             # Open shell in generator container
make clean             # Clean up containers and volumes
make populate-data     # Populate test data
```

### Running Tests

```bash
# Run all tests
make test

# Or manually
docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest"

# Run specific test files
docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest tests/unit/"
```

### CI/CD Pipeline

The project uses GitHub Actions for automated testing and Docker image publishing:

- **Tests** run on every push and PR
- **Docker images** are built and published to `ghcr.io/aloshy-ai/deep-job-seek`
- **Multi-platform support** (AMD64 + ARM64)
- **Security scanning** with Trivy
- **Automated releases** when tags are pushed

See [.github/DEPLOYMENT.md](.github/DEPLOYMENT.md) for detailed CI/CD information.

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