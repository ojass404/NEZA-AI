.PHONY: help setup dev build prod clean test

help:
	@echo "NEZA AI - Available Commands:"
	@echo "  setup    - Install dependencies"
	@echo "  dev      - Start development environment"
	@echo "  build    - Build production images"
	@echo "  prod     - Start production environment"
	@echo "  test     - Run all tests"
	@echo "  clean    - Clean all temporary files"

setup:
	@echo "Setting up NEZA AI..."
	@cp .env.example .env
	@cd backend && pip install -r requirements/dev.txt
	@cd frontend && flutter pub get
	@cd ml_pipeline && pip install -r requirements.txt
	@echo "Setup complete!"

dev:
	@echo "Starting development environment..."
	@docker-compose up --build

build:
	@echo "Building production images..."
	@docker-compose build

prod:
	@echo "Starting production environment..."
	@docker-compose up -d

test:
	@echo "Running tests..."
	@cd backend && pytest tests/ -v
	@cd frontend && flutter test

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".dart_tool" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@docker-compose down -v 2>/dev/null || true
	@echo "Cleanup complete!"
