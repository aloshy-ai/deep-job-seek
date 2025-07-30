# Deep Job Seek - Development Tasks

.PHONY: help install install-dev test test-unit lint format clean health run

# Default target
help:
	@echo "Available targets:"
	@echo "  install         - Install production dependencies"
	@echo "  install-dev     - Install development and test dependencies"
	@echo "  test            - Run all tests with pytest (local or containerized)"
	@echo "  test-unit       - Run unit tests only (local)"
	@echo "  lint            - Run code linting (local)"
	@echo "  format          - Format code with black (local)"
	@echo "  clean           - Clean up temporary files"
	@echo "  health          - Run health checks (local)"
	@echo "  run             - Start the server (local)"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-test.txt

# Test targets
test:
	@echo "Running tests..."
	@if docker-compose ps -q generator >/dev/null 2>&1; then \
		echo "Running tests inside Docker container..."; \
		docker-compose exec generator pytest; \
	else \
		echo "Running tests locally..."; \
		pytest; \
	fi

test-unit:
	pytest tests/unit/ -v -m "unit or not slow"

# Code quality targets
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

# Utility targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf coverage/
	rm -f .coverage*
	rm -f logs/*.log
	rm -f *.log

health:
	PYTHONPATH=src python -m src.resume_generator.healthcheck

run:
	python main.py