# Resume Generator API - Development Tasks

.PHONY: help up down logs test

# Default target
help:
	@echo "Available targets:"
	@echo "  up    - Build and start Docker Compose services"
	@echo "  down  - Stop and remove Docker Compose services"
	@echo "  logs  - View Docker Compose logs"
	@echo "  test  - Run tests inside the generator container"

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec generator bash -c "pip install -r requirements-test.txt && pytest"
