# Makefile for Auth module

# Variables
PYTHON := python3
UV := uv
PYTEST := pytest
RUFF := ruff

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	$(UV) sync --dev

.PHONY: install-prod
install-prod: ## Install production dependencies only
	$(UV) sync

.PHONY: lint
lint: ## Run linting with Ruff
	$(UV) run $(RUFF) check .

.PHONY: lint-fix
lint-fix: ## Run linting with Ruff and fix issues
	$(UV) run $(RUFF) check . --fix

.PHONY: format
format: ## Format code with Ruff
	$(UV) run $(RUFF) format .

.PHONY: check
check: lint ## Run all checks (linting, etc.)

.PHONY: type-check
type-check: ## Run type checking with mypy
	$(UV) run mypy src/

.PHONY: test
test: ## Run tests
	$(UV) run $(PYTEST) tests/

.PHONY: test-cov
test-cov: ## Run tests with coverage
	$(UV) run $(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

.PHONY: init
init: ## Initialize the service (wait for DB)
	@echo "Initializing projects service..."
	@$(UV) run --env-file=.env python ./src/initialize.py
	@echo "✓ Projects service initialized"

.PHONY: run
run: ## Run the application locally
	$(UV) run --env-file=.env uvicorn main:app --host 0.0.0.0 --port 7003 --reload --app-dir ./src

.PHONY: run-prod
run-prod: ## Run the application in production mode
	$(UV) run --env-file=.env uvicorn main:app --host 0.0.0.0 --port 7003 --app-dir ./src

.PHONY: schema
schema: ## Export GraphQL schema
	$(UV) run ./export_schema.sh

.PHONY: clean
clean: ## Clean up generated files
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
