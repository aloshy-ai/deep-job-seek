# Deep Job Seek

Generate tailored resumes automatically using AI analysis and vector search.

## Description

A REST API that analyzes job descriptions and generates tailored resumes by:

- Extracting key requirements using AI (OpenAI-compatible)
- Finding relevant experience using vector search (Qdrant)
- Generating JSON Resume format output
- Creating human-friendly reasoning for cover letters

## Prerequisites

- Python 3.8+
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) (for running the Qdrant database and optional containerized deployment)
- OpenAI-compatible API (e.g., [LM Studio](https://lmstudio.ai/))

## Installation & Setup (Local Development)

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/aloshy-ai/deep-job-seek.git
    cd deep-job-seek
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    ```

4.  **Start Qdrant (using Docker Compose):**

    ```bash
    docker-compose up -d qdrant
    ```

    This will start the Qdrant database in a Docker container.

5.  **Populate test data:**

    ```bash
    python scripts/populate_test_data.py
    ```

## Installation & Setup (Containerized Deployment)

For a fully containerized deployment of both the application and Qdrant:

1.  **Build and Start Services:**

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    - Build the application's Docker image.
    - Pull the Qdrant Docker image.
    - Start both the `generator` application and `qdrant` services in detached mode.
    - Automatically populate the Qdrant database with test data on first run.

2.  **Verify Services:**

    ```bash
    docker-compose ps
    ```

    You should see both `generator` and `qdrant` services listed as `Up`.

## Usage

### Local Development

Once Qdrant is running and test data is populated:

```bash
python main.py
```

Your application will be accessible at `http://localhost:8000`.

### Containerized Deployment

Once the Docker Compose services are running:

-   **Application API:** Accessible at `http://localhost:8000`
-   **Qdrant API:** Accessible at `http://localhost:6333` (HTTP) and `http://localhost:6334` (gRPC)

### Logs

For local development, logs are typically printed to the console or to files in the `logs/` directory.

For containerized deployment, to view logs from all running services:

```bash
docker-compose logs -f
```

To view logs from a specific service (e.g., `generator`):

```bash
docker-compose logs -f generator
```

### Stopping Services

For local development, you can stop the Python application with `Ctrl+C`.

For containerized deployment, to stop and remove all services, networks, and volumes created by Docker Compose:

```bash
docker-compose down
```

### API Endpoints

1.  **Generate Resume** (POST `/generate`)

    ```bash
    curl -X POST http://localhost:8000/generate \
      -H "Content-Type: application/json" \
      -d '{"job_description": "Software Engineer position..."}'
    ```

2.  **Stream Generation** (POST `/generate/stream`)

    - Real-time updates via Server-Sent Events (SSE)
    - Status updates for analysis, search, and completion

3.  **Replace Resume** (POST `/resume/replace`) - **Recommended**

    Complete resume replacement with AI parsing - replaces entire resume with new content:

    ```bash
    # Replace with comprehensive resume data (any format)
    curl -X POST http://localhost:8000/resume/replace \
      -H "Content-Type: application/json" \
      -d '{
        "content": "# Alice Chen - Senior Full-Stack Developer\n\n## Experience\n\n**TechCorp** (2021-2024)\n- Senior Full-Stack Developer\n- React/Node.js for scalable web apps\n- Team leadership in microservices architecture\n\n## Skills\n- Languages: JavaScript, Python, TypeScript\n- Frontend: React, Vue.js, HTML5, CSS3\n- Backend: Node.js, Flask, FastAPI\n\n## Education\n- Bachelor in Computer Science, NYU (2015-2019)"
      }'
    ```

    The AI will intelligently parse any input format (markdown, plaintext, JSON) and structure it according to JSON Resume schema. This approach:
    - Eliminates edge cases from complex merging logic
    - Ensures clean, consistent resume structure
    - Validates against JSON Resume schema
    - Returns appropriate HTTP status codes (400/422 for validation errors)

4.  **Update Resume** (POST `/resume/update`) - **Legacy**

    ```bash
    # Add new work experience (JSON format)
    curl -X POST http://localhost:8000/resume/update \
      -H "Content-Type: application/json" \
      -d '{
        "content": "{\"section\": \"work\", \"company\": \"Tech Corp\", \"position\": \"Engineer\", \"summary\": \"Built APIs\"}",
        "update_mode": "append",
        "content_type": "json"
      }'

    # Add skills from text
    curl -X POST http://localhost:8000/resume/update \
      -H "Content-Type: application/json" \
      -d '{
        "content": "Python, Flask, Docker, Kubernetes",
        "update_mode": "append",
        "content_type": "text",
        "section_hint": "skills"
      }'
    ```

    **Parameters:**
    - `content`: Resume data (JSON, markdown, or text)
    - `update_mode`: `merge`, `replace`, or `append` (default: merge)
    - `content_type`: `auto`, `json`, `markdown`, or `text` (default: auto)
    - `section_hint`: Target section (basics, work, skills, projects, education)

5.  **Get Resume** (GET `/resume`)
    - Retrieve complete resume data
    - Optional `?format=pretty` for human-readable output

6.  **Get Resume Summary** (GET `/resume/summary`)
    - Get overview without full content

7.  **Health Check** (GET `/health`)
    - Verify API and dependencies status

### Output

The API generates two files per request:

1.  JSON Resume data (`output/*.json`)
2.  Fitness assessment for cover letters (`output/*.md`)

Example fitness assessment:

```markdown
# Why You're Perfect for This Role

...

## 💪 Your Strongest Qualifications

Your experience aligns with key requirements...

## 📝 Cover Letter Points

Ready-to-use statements for your application...
```

## Configuration

Main environment variables (can be set in `.env` file or directly in `docker-compose.yml`):

```bash
# API Settings (defaults shown)
OPENAI_API_BASE_URL=http://localhost:1234/v1
QDRANT_HOST=qdrant
QDRANT_PORT=6333
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
API_PORT=8000

# Output Settings
SAVE_OUTPUT_FILES=true
SAVE_REASONING_FILES=true
OUTPUT_DIR=output
```

## Development

### Setup Development Environment (Local)

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/aloshy-ai/deep-job-seek.git
    cd deep-job-seek
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    ```

4.  **Start Qdrant (using Docker Compose):**

    ```bash
    docker-compose up -d qdrant
    ```

    This will start the Qdrant database in a Docker container.

5.  **Populate test data:**

    ```bash
    python scripts/populate_test_data.py
    ```

### Running Tests (Local)

Ensure your virtual environment is activated and Qdrant is running (as per setup instructions).

```bash
pytest
```

To run specific test files or directories:

```bash
pytest tests/unit/
pytest tests/test_health.py
```

### Running Tests (Containerized)

If you have the full Docker Compose stack running:

```bash
docker-compose exec generator pytest
```

### Test Structure

The test suite focuses on core functionality with essential tests:

-   **Unit Tests** (`tests/unit/`): Fast, isolated tests for utilities
-   **Health Tests** (`test_health.py`): API health check validation
-   **Generate Tests** (`test_generate.py`): Resume generation functionality
-   **Replace Tests** (`test_resume_replace.py`): Resume replacement (recommended approach)
-   **Retrieval Tests** (`test_resume_retrieval.py`): Resume data fetching

### Test Prerequisites

When running tests locally, ensure your OpenAI-compatible API (e.g., LM Studio) is running and accessible. When running tests via `docker-compose exec`, the Qdrant service will be automatically available. Ensure your OpenAI-compatible API is accessible from the `generator` container (if it's not also containerized).

### Coverage Reports

Test coverage reports are generated in the `coverage` directory:

-   HTML report: `coverage/html/index.html`
-   XML report: `coverage/coverage.xml`

## Architecture

### Component Overview

1.  **Job Analysis**: OpenAI-compatible API analyzes job description and extracts keywords
2.  **Vector Search**: Keywords are used to search resume content in Qdrant
3.  **Resume Assembly**: Relevant resume sections are assembled into JSON format
4.  **Response**: Tailored resume is returned following JSON Resume schema

### Detailed Structure

```
src/resume_generator/
├── api/                        # API layer
│   ├── routes.py              # Route definitions and handlers
├── services/                   # Business logic layer
│   └── resume_service.py       # Resume generation service
└── utils/                     # Utility modules
    ├── api_client.py          # OpenAI-compatible API client
    ├── file_utils.py          # File handling utilities
    ├── resume_builder.py      # Resume construction utilities
    └── vector_search.py       # Vector database operations
```

### Architecture Layers

1.  **API Layer** (`api/`): Handles HTTP requests/responses, input validation, and response formatting
2.  **Service Layer** (`services/`): Contains core business logic and orchestration
3.  **Utility Layer** (`utils/`) : Provides reusable helpers and external service clients
4.  **Configuration Layer**: Manages environment variables and constants
5.  **Health Check Layer**: Verifies dependencies and system health

### Design Patterns

-   **Service Layer Pattern**: Encapsulates business logic in service classes
-   **Client Pattern**: Dedicated classes for external services
-   **Builder Pattern**: Step-by-step resume assembly
-   **Application Factory Pattern**: Clean Flask app creation and configuration

## Troubleshooting

### Common Issues

-   **`port is already allocated` error when running `docker-compose up`**: Another process on your host machine is using one of the ports (e.g., 8000, 6333, 6334) that Docker Compose is trying to map. Identify and stop the conflicting process, or change the port mapping in `docker-compose.yml`.
-   **Container fails to start**: Check `docker-compose logs <service_name>` for error messages.
-   **`Qdrant is not ready` (from `docker-entrypoint.sh`)**: Ensure the Qdrant container is starting correctly. Check `docker-compose logs qdrant`.
-   **Cannot connect to API / API authentication failed**: Ensure your OpenAI-compatible API (e.g., LM Studio) is running and accessible from within the Docker network (if it's also containerized) or from your host machine if it's running locally.
-   **Empty collection / Missing collection**: The `docker-entrypoint.sh` script should populate the Qdrant collection automatically. If you've manually cleared Qdrant data, you might need to restart the `generator` service or manually run the population script inside the container.

## License

MIT

## Contributing

1.  Fork the repository
2.  Create your feature branch
3.  Submit a pull request