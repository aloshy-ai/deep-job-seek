# Deep Job Seek

[![CI/CD Pipeline](https://github.com/aloshy-ai/deep-job-seek/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/aloshy-ai/deep-job-seek/actions/workflows/ci-cd.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/aloshy-ai/deep-job-seek/pkgs/container/deep-job-seek)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

AI-powered REST API that generates tailored resumes from job descriptions using vector search and OpenAI-compatible models.

## Quick Start

### 🚀 One-Line Installation (Recommended)
Set your OpenAI API key and run:
```bash
export OPENAI_API_KEY=your_api_key_here
curl -sSL https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/run.sh | bash
```
**That's it!** API runs at `http://localhost:8000`

### 🎮 Try the Live Demo
**[▶️ Launch Deep Job Seek Mini on HuggingFace Spaces](https://huggingface.co/spaces/aloshy-ai/deep-job-seek-mini)**

Experience the AI-powered resume generation instantly in your browser - no installation required!

### 🛠️ Development Setup
```bash
git clone https://github.com/aloshy-ai/deep-job-seek.git
cd deep-job-seek
export OPENAI_API_KEY=your_api_key_here  # Required
docker-compose up --build -d
```

## Prerequisites
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **OpenAI API Key** - Get yours from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Or use compatible APIs like [LM Studio](https://lmstudio.ai/) for local models

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

## Configuration Options

### For OpenAI API (Default)
```bash
export OPENAI_API_KEY=your_api_key_here
# Uses https://api.openai.com/v1 by default
```

### For Local LM Studio
```bash
export OPENAI_API_BASE_URL=http://host.docker.internal:1234/v1
export OPENAI_API_KEY=not-needed
```
> **Note**: Use `host.docker.internal` instead of `localhost` when running in Docker containers to access services on your host machine.

## Development

### Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aloshy-ai/deep-job-seek.git
    cd deep-job-seek
    ```

2.  **Set your API configuration:**
    ```bash
    # For OpenAI API
    export OPENAI_API_KEY=your_api_key_here
    
    # OR for LM Studio  
    export OPENAI_API_BASE_URL=http://host.docker.internal:1234/v1
    export OPENAI_API_KEY=not-needed
    ```

3.  **Start services:**
    ```bash
    make run
    # or
    docker-compose up --build -d
    ```

4.  **Verify services:**
    ```bash
    curl http://localhost:8000/health
    ```

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

### 🔄 CI/CD Pipeline

Automated GitHub Actions pipeline ensures code quality and seamless deployment:

- ✅ **Automated Testing** - Full test suite on every push and PR
- 🐳 **Docker Publishing** - Multi-platform images published to [GitHub Container Registry](https://github.com/aloshy-ai/deep-job-seek/pkgs/container/deep-job-seek)
- 🏗️ **Multi-Platform Support** - Native AMD64 and ARM64 builds
- 🔒 **Security Scanning** - Vulnerability scanning with Trivy
- 📦 **Automated Releases** - Tagged releases trigger production builds

All Docker images are available at: `ghcr.io/aloshy-ai/deep-job-seek:latest`

## 🧠 How It Works
1. **🔍 AI Analysis** - Job description analyzed for key requirements and skills
2. **⚡ Vector Search** - Relevant experience found using Qdrant similarity search  
3. **🔧 Smart Assembly** - Resume sections assembled into JSON Resume format
4. **📄 Tailored Output** - Customized resume optimized for the specific role

## 🛠️ Tech Stack
- **Backend**: Python Flask with clean service layer architecture
- **Database**: Qdrant vector database for semantic search
- **AI Models**: OpenAI-compatible APIs (LM Studio, OpenAI, etc.)
- **Embeddings**: BAAI/bge-small-en-v1.5 via FastEmbed
- **Deployment**: Docker with multi-platform support
- **CI/CD**: GitHub Actions with automated testing and publishing

## 🔧 Troubleshooting

### Common Issues

#### API Connection Issues
- **OpenAI API errors**: Verify your `OPENAI_API_KEY` is correct and has sufficient credits
- **LM Studio connection**: 
  - Ensure LM Studio is running on `localhost:1234`
  - Use `http://host.docker.internal:1234/v1` as the base URL for Docker
  - Check that LM Studio is accepting connections from all interfaces

#### Docker Issues  
- **Port conflicts**: Change ports in `docker-compose.yml` or use `-p` flag
- **Container startup failures**: Check logs with `docker-compose logs generator`
- **Empty database**: Restart services to auto-populate test data
- **Permission errors**: Ensure Docker daemon is running and accessible

#### Environment Variables
- **Missing API key**: The application will exit with clear error messages
- **Wrong base URL**: Use `host.docker.internal` instead of `localhost` for Docker
- **Configuration not applied**: Restart containers after changing environment variables

### Getting Help
- 📋 Check [Issues](https://github.com/aloshy-ai/deep-job-seek/issues) for common problems
- 🐛 [Report a bug](https://github.com/aloshy-ai/deep-job-seek/issues/new) if you find one
- 💡 [Request a feature](https://github.com/aloshy-ai/deep-job-seek/issues/new) for enhancements

## License
MIT

```
▄▀█ █░░ █▀█ █▀ █░█ █▄█ ░ ▄▀█ █
█▀█ █▄▄ █▄█ ▄█ █▀█ ░█░ ▄ █▀█ █
```