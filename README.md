# Resume Generator API

Generate tailored resumes automatically using AI analysis and vector search.

## Description

A REST API that analyzes job descriptions and generates tailored resumes by:

- Extracting key requirements using AI (OpenAI-compatible)
- Finding relevant experience using vector search (Qdrant)
- Generating JSON Resume format output
- Creating human-friendly reasoning for cover letters

## Prerequisites

- Python 3.8+
- OpenAI-compatible API (e.g., [LM Studio](https://lmstudio.ai/))
- [Qdrant](https://qdrant.tech/) vector database
- Resume data in Qdrant collection

## Installation

```bash
# Install package and dependencies
python setup.py

# Verify setup
make health
```

For manual installation:

```bash
pip install -r requirements.txt
```

## Usage

Start the server:

```bash
# Start server
python main.py

# Server runs on http://localhost:8080
```

### API Endpoints

1. **Generate Resume** (POST `/generate`)

   ```bash
   curl -X POST http://localhost:8080/generate \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Software Engineer position..."}'
   ```

2. **Stream Generation** (POST `/generate/stream`)

   - Real-time updates via Server-Sent Events (SSE)
   - Status updates for analysis, search, and completion

3. **Health Check** (GET `/health`)
   - Verify API and dependencies status

### Output

The API generates two files per request:

1. JSON Resume data (`output/*.json`)
2. Fitness assessment for cover letters (`output/*.md`)

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

Main environment variables:

```bash
# API Settings (defaults shown)
OPENAI_API_BASE_URL=http://localhost:1234/v1
QDRANT_URL=http://localhost:6333
API_PORT=8080

# Output Settings
SAVE_OUTPUT_FILES=true
SAVE_REASONING_FILES=true
OUTPUT_DIR=output
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-test.txt

# Set up test data
python scripts/populate_test_data.py
```

### Running Tests

```bash
# Unit tests only (fast, no external dependencies)
make test-unit

# All tests (requires running services)
make test

# Individual test categories
pytest tests/unit/          # Unit tests
pytest tests/test_health.py # Health checks
```

### Test Prerequisites

Before running integration tests, ensure:

1. LM Studio is running on port 1234
2. Qdrant is running on port 6333
3. Test data is populated in Qdrant

### Coverage Reports

Test coverage reports are generated in the `coverage` directory:

- HTML report: `coverage/html/index.html`
- XML report: `coverage/coverage.xml`

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request
   | ------------------------ | -------------------------- | ------------------------------------------------------ |
   | `OPENAI_API_BASE_URL` | `http://localhost:1234/v1` | OpenAI-compatible API endpoint |
   | `OPENAI_API_KEY` | `None` | API key (optional for local APIs, required for remote) |
   | `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
   | `QDRANT_COLLECTION_NAME` | `resume` | Qdrant collection name |
   | `API_HOST` | `127.0.0.1` | API server host |
   | `API_PORT` | `8080` | API server port |
   | `DEBUG` | `True` | Enable debug mode |
   | `MAX_TOKENS` | `500` | Maximum tokens for LLM response |
   | `TEMPERATURE` | `0.7` | LLM temperature setting |
   | `SEARCH_LIMIT` | `15` | Number of search results to retrieve |
   | `OUTPUT_DIR` | `output` | Directory to save generated resume files |
   | `SAVE_OUTPUT_FILES` | `true` | Whether to save resume files to disk |
   | `SAVE_REASONING_FILES` | `true` | Whether to save reasoning markdown files |

## Architecture

### Component Overview

1. **Job Analysis**: OpenAI-compatible API analyzes job description and extracts keywords
2. **Vector Search**: Keywords are used to search resume content in Qdrant
3. **Resume Assembly**: Relevant resume sections are assembled into JSON format
4. **Response**: Tailored resume is returned following JSON Resume schema

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

1. **API Layer** (`api/`): Handles HTTP requests/responses, input validation, and response formatting
2. **Service Layer** (`services/`): Contains core business logic and orchestration
3. **Utility Layer** (`utils/`): Provides reusable helpers and external service clients
4. **Configuration Layer**: Manages environment variables and constants
5. **Health Check Layer**: Verifies dependencies and system health

### Design Patterns

- **Service Layer Pattern**: Encapsulates business logic in service classes
- **Client Pattern**: Dedicated classes for external services
- **Builder Pattern**: Step-by-step resume assembly
- **Application Factory Pattern**: Clean Flask app creation and configuration

## Development

The project follows a standard Python package structure with:

- Configuration management through `config.py`
- Core logic separated in `core.py`
- Flask server in `server.py`
- Comprehensive testing in `tests/`
- Automated setup with model predownloading

## Troubleshooting

### Common Issues

- **Health check failures**: Run `make health` to diagnose issues before starting
- **Slow first request**: Models are cached after first download via `setup.py`
- **Connection errors**: Ensure OpenAI-compatible API and Qdrant are running
- **API authentication failed**: Check your `OPENAI_API_KEY` is correctly set for remote APIs
- **API access forbidden**: Verify your API key has the necessary permissions
- **Empty collection**: The Qdrant 'resume' collection must be populated with resume data
- **Missing collection**: Create the 'resume' collection in Qdrant and index your resume content

### Health Check Messages

| Message                                    | Meaning                              | Solution                                            |
| ------------------------------------------ | ------------------------------------ | --------------------------------------------------- |
| ❌ Cannot connect to API                   | OpenAI-compatible server not running | Start LM Studio or your API provider                |
| ❌ API authentication failed               | Invalid API key                      | Check `OPENAI_API_KEY` environment variable         |
| ❌ Cannot connect to Qdrant                | Qdrant server not running            | Start Qdrant server                                 |
| ❌ Collection 'resume' not found           | Missing resume collection            | Create and populate the resume collection in Qdrant |
| ⚠️ Collection 'resume' exists but is empty | Collection has no data               | Add resume data to the collection                   |
