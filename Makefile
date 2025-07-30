# Deep Job Seek - Resume Generator API
# Development and deployment automation

.PHONY: help build run stop test clean logs shell populate-data release-test docker-login quickstart-test

# Default target
help:
	@echo "🚀 Deep Job Seek - Resume Generator API"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build Docker images"
	@echo "  make run           - Start all services"
	@echo "  make stop          - Stop all services" 
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up containers and volumes"
	@echo "  make logs          - Follow container logs"
	@echo "  make shell         - Open shell in generator container"
	@echo "  make populate-data - Populate test data"
	@echo "  make release-test  - Test release process locally"
	@echo "  make quickstart-test - Test Quick Start method"
	@echo "  make docker-login  - Login to GitHub Container Registry"

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start all services (alias for legacy compatibility)
up: run

# Start all services
run:
	@echo "🚀 Starting Deep Job Seek services..."
	docker-compose up -d
	@echo "✅ Services started. API available at http://localhost:8000"

# Stop all services (alias for legacy compatibility)  
down: stop

# Stop all services
stop:
	@echo "🛑 Stopping services..."
	docker-compose down

# Run tests
test:
	@echo "🧪 Running tests..."
	docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest"

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Follow logs
logs:
	docker-compose logs -f

# Open shell in generator container
shell:
	docker-compose exec generator bash

# Populate test data
populate-data:
	@echo "📊 Populating test data..."
	docker-compose exec generator python scripts/populate_test_data.py

# Test release process locally
release-test:
	@echo "🧪 Testing release process..."
	@echo "Building multi-platform image..."
	docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/aloshy-ai/deep-job-seek:test .
	@echo "✅ Multi-platform build successful"

# Test Quick Start method
quickstart-test:
	@echo "🧪 Testing Quick Start method..."
	@mkdir -p /tmp/quickstart-test-$(shell date +%s)
	@cd /tmp/quickstart-test-$(shell date +%s) && \
		curl -sSL -o run.sh https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/run.sh && \
		chmod +x run.sh && \
		bash -n run.sh && \
		echo "✅ Quick Start script is valid"

# Login to GitHub Container Registry
docker-login:
	@echo "🔐 Logging into GitHub Container Registry..."
	@echo "Please provide your GitHub personal access token with packages:write permission"
	@read -s -p "GitHub Token: " token; \
	echo $$token | docker login ghcr.io -u $(shell git config user.name) --password-stdin
