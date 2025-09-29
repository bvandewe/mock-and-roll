# Mock-and-Roll Development Makefile
# A comprehensive Makefile for common development tasks

.DEFAULT_GOAL := help
SHELL := /bin/bash
.PHONY: help install clean test lint format docs serve-docs build-docs docker-up docker-down docker-logs pre-commit setup dev-setup

# Project configuration
PYTHON := python3
POETRY := poetry
DOCKER_COMPOSE := docker-compose
MKDOCS := mkdocs
PROJECT_NAME := mock-and-roll
DOCS_PORT := 8080
DEV_PORT := 8000

# Simple, reliable output functions
define print_header
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║                     Mock-and-Roll Development                    ║"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
endef

## Help & Information
help: ## Display this help message
	$(call print_header)
	@echo "Available targets:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make setup          # Initial project setup"
	@echo "  make dev            # Start development environment"
	@echo "  make test           # Run all tests"
	@echo "  make docs-live      # Live documentation server"
	@echo "  make docker-dev     # Docker development environment"
	@echo ""

info: ## Show project information
	@echo "Project Information:"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Python: $(shell $(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "  Poetry: $(shell $(POETRY) --version 2>/dev/null || echo 'Not installed')"
	@echo "  Docker: $(shell docker --version 2>/dev/null || echo 'Not installed')"
	@echo "  MkDocs: $(shell $(MKDOCS) --version 2>/dev/null || echo 'Not installed')"
	@echo ""

## Installation & Setup
install: ## Install dependencies using Poetry
	@echo "Installing dependencies..."
	$(POETRY) install --with test
	@echo "✓ Dependencies installed"

setup: install setup-pre-commit ## Complete project setup (install + pre-commit)
	@echo "✓ Project setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make dev            # Start development server"
	@echo "  make test           # Run tests"
	@echo "  make docs-live      # Start documentation server"

setup-pre-commit: ## Install and setup pre-commit hooks
	@echo "Setting up pre-commit hooks..."
	$(POETRY) run pre-commit install
	@echo "✓ Pre-commit hooks installed"

dev-setup: ## Setup development environment with example config
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env file"; fi
	@mkdir -p logs
	@echo "✓ Development environment ready"

## Development
dev: dev-setup ## Start development server (mockctl)
	@echo "Starting Mock-and-Roll development server..."
	@echo "Available at: http://localhost:$(DEV_PORT)"
	$(POETRY) run python src/main.py

dev-basic: dev-setup ## Start basic config server
	@echo "Starting Mock-and-Roll with basic config..."
	./mockctl start basic --port $(DEV_PORT)

dev-persistence: dev-setup ## Start persistence config server (requires Redis)
	@echo "Starting Mock-and-Roll with persistence config..."
	@echo "Note: Ensure Redis is running (make redis-up)"
	./mockctl start persistence --port $(DEV_PORT)

dev-vmanage: dev-setup ## Start vManage simulation server
	@echo "Starting vManage simulation server..."
	./mockctl start vmanage --port $(DEV_PORT)

stop: ## Stop all running servers
	@echo "Stopping all Mock-and-Roll servers..."
	./mockctl stop all || true
	./mockctl cleanup || true
	@echo "✓ All servers stopped"

status: ## Show status of running servers
	@echo "Mock-and-Roll Server Status:"
	./mockctl list

logs: ## Show server logs
	@echo "Recent server logs:"
	./mockctl logs --lines 50

## Testing & Quality
test: ## Run all tests
	@echo "Running tests..."
	$(POETRY) run pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(POETRY) run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	$(POETRY) run pytest tests/ -k integration -v

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	$(POETRY) run pytest tests/ -k "not integration" -v

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode (press Ctrl+C to stop)..."
	$(POETRY) run pytest-watch tests/ -- -v

## Code Quality
lint: ## Run all linters
	@echo "Running linters..."
	$(POETRY) run flake8 src tests
	$(POETRY) run black --check src tests
	@echo "✓ Linting complete"

format: ## Format code with Black and other formatters
	@echo "Formatting code..."
	$(POETRY) run black src tests
	$(POETRY) run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place src tests
	@echo "✓ Code formatted"

type-check: ## Run type checking with mypy
	@echo "Running type checks..."
	$(POETRY) run mypy src --ignore-missing-imports || echo "Note: mypy not configured, skipping"

pre-commit: ## Run pre-commit hooks on all files
	@echo "Running pre-commit hooks..."
	$(POETRY) run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "Updating pre-commit hooks..."
	$(POETRY) run pre-commit autoupdate

quality: lint type-check test ## Run all quality checks (lint, type-check, test)

## Documentation
docs-install: ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	$(POETRY) install
	@echo "✓ Documentation dependencies installed"

docs-build: docs-install ## Build documentation
	@echo "Building documentation..."
	$(POETRY) run $(MKDOCS) build --clean
	@echo "✓ Documentation built in site/"

docs-serve: docs-install ## Serve documentation locally
	@echo "Starting documentation server..."
	@echo "Available at: http://localhost:$(DOCS_PORT)"
	@echo "Press Ctrl+C to stop"
	$(POETRY) run $(MKDOCS) serve --dev-addr 0.0.0.0:$(DOCS_PORT)

docs-live: docs-serve ## Alias for docs-serve (live documentation)

docs-deploy: docs-build ## Deploy documentation (requires proper git setup)
	@echo "Deploying documentation..."
	$(POETRY) run $(MKDOCS) gh-deploy --clean
	@echo "✓ Documentation deployed"

## Docker Operations
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(PROJECT_NAME):latest .
	@echo "✓ Docker image built"

docker-build-alpine: ## Build Alpine Docker image
	@echo "Building Alpine Docker image..."
	docker build -f Dockerfile.alpine -t $(PROJECT_NAME):alpine .
	@echo "✓ Alpine Docker image built"

docker-dev: ## Start development environment with Docker Compose
	@echo "Starting Docker development environment..."
	@echo "API available at: http://localhost:$(DEV_PORT)"
	@echo "Redis will be available on localhost:6379"
	$(DOCKER_COMPOSE) up --build

docker-up: ## Start Docker services in background
	@echo "Starting Docker services..."
	$(DOCKER_COMPOSE) up -d --build
	@echo "✓ Docker services started"
	@echo "API: http://localhost:$(DEV_PORT)"
	@echo "Logs: make docker-logs"

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	$(DOCKER_COMPOSE) down
	@echo "✓ Docker services stopped"

docker-logs: ## Show Docker logs
	@echo "Docker service logs:"
	$(DOCKER_COMPOSE) logs --follow

docker-restart: docker-down docker-up ## Restart Docker services

docker-test: ## Run tests in Docker environment
	@echo "Running tests in Docker..."
	$(DOCKER_COMPOSE) -f docker-compose_test.yml up --build --abort-on-container-exit
	$(DOCKER_COMPOSE) -f docker-compose_test.yml down

redis-up: ## Start only Redis service
	@echo "Starting Redis service..."
	$(DOCKER_COMPOSE) up redis -d
	@echo "✓ Redis started on localhost:6379"

redis-down: ## Stop Redis service
	@echo "Stopping Redis service..."
	$(DOCKER_COMPOSE) stop redis
	@echo "✓ Redis stopped"

## Utilities
clean: ## Clean up temporary files and caches
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf site/
	rm -rf dist/
	rm -rf build/
	@echo "✓ Cleanup complete"

clean-logs: ## Clean up log files
	@echo "Cleaning up log files..."
	rm -rf logs/*.logs
	@echo "✓ Log files cleaned"

clean-all: clean clean-logs docker-down ## Deep clean (files, logs, Docker)
	@echo "Performing deep clean..."
	docker system prune -f --volumes 2>/dev/null || true
	@echo "✓ Deep clean complete"

check-deps: ## Check for dependency updates
	@echo "Checking for dependency updates..."
	$(POETRY) show --outdated

update-deps: ## Update dependencies
	@echo "Updating dependencies..."
	$(POETRY) update
	@echo "✓ Dependencies updated"

## CLI Tools
mockctl-help: ## Show mockctl help
	@echo "MockCTL Command Help:"
	./mockctl --help

search-logs: ## Search server logs (usage: make search-logs PATTERN="your-pattern" CONFIG="basic")
	@echo "Searching logs..."
	./mockctl search ${CONFIG:-basic} "${PATTERN:-.*}"

## Comprehensive Tasks
all-tests: test-unit test-integration test-coverage ## Run all types of tests

full-check: quality docs-build docker-build ## Complete project validation

ci: install lint test docs-build ## Continuous Integration tasks

release-check: full-check ## Pre-release validation
	@echo "✓ Release validation complete"
	@echo ""
	@echo "Release Checklist:"
	@echo "  ☐ Update version in pyproject.toml"
	@echo "  ☐ Update CHANGELOG.md"
	@echo "  ☐ Tag release: git tag v<version>"
	@echo "  ☐ Push tags: git push --tags"

## Development Workflows
workflow-setup: setup dev-setup ## Complete development workflow setup
	@echo "Development workflow ready!"

workflow-dev: stop dev-basic docs-live ## Start full development workflow

workflow-test: format lint test ## Quick test workflow

# Validation targets
validate-poetry:
	@$(POETRY) check || (echo "Poetry configuration invalid" && exit 1)

validate-docker:
	@docker info >/dev/null 2>&1 || (echo "Docker not running" && exit 1)

# Safety checks
check-git:
	@git status >/dev/null 2>&1 || (echo "Not in a git repository" && exit 1)

# Include custom targets if they exist
-include Makefile.local

# Debug target
debug: ## Show debug information
	@echo "Debug Information:"
	@echo "Python: $(PYTHON)"
	@echo "Poetry: $(POETRY)"
	@echo "Working Directory: $(PWD)"
	@echo "Available Python: $(shell which python3 python 2>/dev/null | head -1)"
	@echo "Git Branch: $(shell git branch --show-current 2>/dev/null || echo 'Not in git repo')"
	@echo "Docker Status: $(shell docker info >/dev/null 2>&1 && echo 'Running' || echo 'Not running')"