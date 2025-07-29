# Resume Generator API - Development Tasks

.PHONY: help install install-dev test test-unit test-integration test-streaming lint format clean health run

# Default target
help:
	@echo "Available targets:"
	@echo "  install         - Install production dependencies"
	@echo "  install-dev     - Install development and test dependencies"
	@echo "  test            - Run all tests with pytest"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-streaming  - Run standalone streaming test"
	@echo "  lint            - Run code linting"
	@echo "  format          - Format code with black"
	@echo "  clean           - Clean up temporary files"
	@echo "  health          - Run health checks"
	@echo "  run             - Start the server"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-test.txt

# Test targets
test:
	@echo "Checking test environment..."
	PYTHONPATH=src python scripts/check_test_env.py

	@echo "Ensuring no Flask server is running..."
	-@lsof -t -i:$${API_PORT:-8080} | xargs -r kill

	@echo "Starting Flask server for integration tests..."
	mkdir -p logs
	PYTHONPATH=src python -m resume_generator.server > logs/server.log 2>&1 & echo $$! > .server.pid
	@echo "Waiting for server to start..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:$${API_PORT:-8080}/health >/dev/null; then \
			echo "Server is up!"; \
			break; \
		fi; \
		if [ $$i -eq 30 ]; then \
			echo "Error: Server failed to start" >&2; \
			cat logs/server.log; \
			exit 1; \
		fi; \
		echo "Waiting... ($$i/30)"; \
		sleep 1; \
	done

	# Trap to ensure Flask server is killed on exit or interrupt
	trap "kill $(FLASK_PID) || true" EXIT

	@echo "Waiting for Flask server to become available..."
	@for i in $$(seq 1 60); do \
		if curl -s http://localhost:$${API_PORT:-8080}/health >/dev/null; then \
			echo "Flask server is up!"; \
			break; \
		fi; \
		if [ $$i -eq 60 ]; then \
			echo "Error: Flask server failed to start" >&2; \
			kill $(FLASK_PID) || true; \
			exit 1; \
		fi; \
		echo "Waiting... ($$i/60)"; \
		sleep 1; \
	done

	PYTHONPATH=src pytest tests/ -v

	@echo "Stopping Flask server..."
	-@cat .server.pid | xargs kill
	@rm -f .server.pid
	@echo "Server stopped."

test-unit:
	pytest tests/unit/ -v -m "unit or not slow"

test-integration:
	pytest tests/test_*.py -v -m "not unit"

test-streaming:
	python tests/test_streaming.py

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

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete"
	@echo "Run 'make health' to verify dependencies"
	@echo "Run 'make run' to start the server"