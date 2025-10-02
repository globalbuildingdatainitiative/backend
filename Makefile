# Root Makefile for GBDI Backend

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies for all modules
	@echo "Installing dependencies for all modules..."
	@cd modules/auth && $(MAKE) install
	@cd modules/organization && $(MAKE) install
	@cd modules/projects && $(MAKE) install
	@echo "✓ All dependencies installed"

.PHONY: db-up
db-up: ## Start all database services (postgres, supertokens, mongo) and router
	@echo "Starting database services and router..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "  - PostgreSQL (auth): localhost:5434"
	@echo "  - SuperTokens: localhost:3567"
	@echo "  - MongoDB (projects): localhost:27017"
	@echo "  - MongoDB (organization): localhost:27018"
	@echo "  - Apollo Router: localhost:4000"

.PHONY: db-down
db-down: ## Stop all database services
	@echo "Stopping database services..."
	docker-compose down
	@echo "✓ Database services stopped"

.PHONY: db-clean
db-clean: ## Stop database services and remove volumes (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✓ Database services stopped and volumes removed"; \
	else \
		echo "Cancelled."; \
	fi

.PHONY: db-logs
db-logs: ## Show logs from database services
	docker-compose logs -f

.PHONY: run
run: db-up ## Start all services (databases + router + all backend modules)
	@echo "Starting all backend services..."
	@echo "Waiting for databases and router to be ready..."
	@sleep 5
	@echo ""
	@echo "Starting backend services in parallel..."
	@echo "  - Auth service will run on http://localhost:7001"
	@echo "  - Organization service will run on http://localhost:7002"
	@echo "  - Projects service will run on http://localhost:7003"
	@echo "  - Router service is running on http://localhost:4000 (via docker-compose)"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@$(MAKE) run-services

.PHONY: run-services
run-services:
	@trap 'kill 0' SIGINT; \
	cd modules/auth && $(MAKE) run & \
	cd modules/organization && $(MAKE) run & \
	cd modules/projects && $(MAKE) run & \
	wait

.PHONY: run-auth
run-auth: ## Run only the auth service
	@cd modules/auth && $(MAKE) run

.PHONY: run-organization
run-organization: ## Run only the organization service
	@cd modules/organization && $(MAKE) run

.PHONY: run-projects
run-projects: ## Run only the projects service
	@cd modules/projects && $(MAKE) run

.PHONY: run-router
run-router: ## Run only the router service
	@cd modules/router && $(MAKE) run

.PHONY: test
test: ## Run tests for all modules
	@echo "Running tests for all modules..."
	@cd modules/auth && $(MAKE) test
	@cd modules/organization && $(MAKE) test
	@cd modules/projects && $(MAKE) test
	@echo "✓ All tests completed"

.PHONY: lint
lint: ## Run linting for all modules
	@echo "Running linting for all modules..."
	@cd modules/auth && $(MAKE) lint
	@cd modules/organization && $(MAKE) lint
	@cd modules/projects && $(MAKE) lint
	@echo "✓ All linting completed"

.PHONY: format
format: ## Format code for all modules
	@echo "Formatting code for all modules..."
	@cd modules/auth && $(MAKE) format
	@cd modules/organization && $(MAKE) format
	@cd modules/projects && $(MAKE) format
	@echo "✓ All code formatted"

.PHONY: clean
clean: ## Clean up generated files in all modules
	@echo "Cleaning up generated files..."
	@cd modules/auth && $(MAKE) clean
	@cd modules/organization && $(MAKE) clean
	@cd modules/projects && $(MAKE) clean
	@echo "✓ All modules cleaned"

.PHONY: status
status: ## Show status of database services
	@docker-compose ps
