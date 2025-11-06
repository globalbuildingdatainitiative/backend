# Root Makefile for GBDI Back

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
	@echo "Installing git hooks with lefthook..."
	uv tool install lefthook
	lefthook install
	@echo "✓ Setup complete!"

.PHONY: db-up
db-up: ## Start all database services (postgres, supertokens, mongo)
	@echo "Starting database services..."
	docker compose up -d
	@echo "✓ Services started"
	@echo "  - PostgreSQL (auth): psql://localhost:5434"
	@echo "  - SuperTokens: http://localhost:3567"
	@echo "  - MongoDB (projects): mongodb://localhost:27017"
	@echo "  - MongoDB (organization): mongodb://localhost:27018"
	@echo "  - pgadmin: http://localhost:5050 (user: admin@admin.com, password: admin) cf docker-compose.yml for username passwords"

.PHONY: db-down
db-down: ## Stop all database services
	@echo "Stopping database services..."
	docker compose down
	@echo "✓ Database services stopped"

.PHONY: db-clean
db-clean: ## Stop database services and remove volumes (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "✓ Database services stopped and volumes removed"; \
	else \
		echo "Cancelled."; \
	fi

.PHONY: db-logs
db-logs: ## Show logs from database services
	docker compose logs -f

.PHONY: init
init: ## Initialize all modules (wait for databases, run migrations)
	@echo "Initializing all modules..."
	@echo "Waiting for databases to be ready..."
# 	@until docker exec -it postgres-auth pg_isready -U postgres > /dev/null 2>&1; do \
# 		echo "Waiting for PostgreSQL (auth) to be ready..."; \
# 		sleep 2; \
# 	done; \
# 	@until docker exec -it mongo-projects mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do \
# 		echo "Waiting for MongoDB (projects) to be ready..."; \
# 		sleep 2; \
# 	done; \
# 	@until docker exec -it mongo-organization mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do \
# 		echo "Waiting for MongoDB (organization) to be ready..."; \
# 		sleep 2; \
# 	done; \
# 	@echo "Databases are ready."
	@echo "Running initialization for each module..."
	@cd modules/auth && $(MAKE) init
	@cd modules/organization && $(MAKE) init
	@cd modules/projects && $(MAKE) init
	@echo "✓ All modules initialized"

.PHONY: run
run: db-up init ## Start all services (databases + router + all backend modules)
	@echo "Starting all backend services..."
	@echo "Waiting for databases to be ready..."
	@sleep 2
	@echo ""
	@echo "Starting backend services in parallel..."
	@echo "  - Auth service will run on http://localhost:7001"
	@echo "  - Organization service will run on http://localhost:7002"
	@echo "  - Projects service will run on http://localhost:7003"
	@echo "  - Router service will run on http://localhost:4000"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@$(MAKE) run-services

.PHONY: run-services
run-services: ## Run all backend services in parallel (internal target)
	@trap 'kill 0' SIGINT; \
	cd modules/auth && $(MAKE) run & \
	cd modules/organization && $(MAKE) run & \
	cd modules/projects && $(MAKE) run & \
	cd modules/router && $(MAKE) run & \
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

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo "Running type checking for all modules..."
	@cd modules/auth && $(MAKE) type-check
	@cd modules/organization && $(MAKE) type-check
	@cd modules/projects && $(MAKE) type-check
	@echo "✓ All type checking completed"

.PHONY: clean
clean: ## Clean up generated files in all modules
	@echo "Cleaning up generated files..."
	@cd modules/auth && $(MAKE) clean
	@cd modules/organization && $(MAKE) clean
	@cd modules/projects && $(MAKE) clean
	@echo "✓ All modules cleaned"

.PHONY: status
status: ## Show status of database services
	@docker compose ps


ARGS = $(filter-out $@,$(MAKECMDGOALS))

.PHONY: admin
admin: ## make user admin using ARGS
	@if [ -n "$(ARGS)" ]; then \
		curl --location --request PUT 'http://localhost:3567/recipe/user/role' \
			--header 'Content-Type: application/json; charset=utf-8' \
			--data-raw '{"userId":"$(firstword $(ARGS))","role":"admin"}'; \
	else \
		echo "No userId specified. Usage: make admin <userId>"; \
	fi

.PHONY: run-except-auth
run-except-auth: ## Run organization and projects services (for debugging auth)
	@echo "Starting organization and projects services..."
	@trap 'kill 0' SIGINT; \
	cd modules/organization && $(MAKE) run & \
	cd modules/projects && $(MAKE) run & \
	cd modules/router && $(MAKE) run & \
	wait

.PHONY: run-except-organization
run-except-organization: ## Run auth and projects services (for debugging organization)
	@echo "Starting auth and projects services..."
	@trap 'kill 0' SIGINT; \
	cd modules/auth && $(MAKE) run & \
	cd modules/projects && $(MAKE) run & \
	cd modules/router && $(MAKE) run & \
	wait

.PHONY: run-except-projects
run-except-projects: ## Run auth and organization services (for debugging projects)
	@echo "Starting auth and organization services..."
	@trap 'kill 0' SIGINT; \
	cd modules/auth && $(MAKE) run & \
	cd modules/organization && $(MAKE) run & \
	cd modules/router && $(MAKE) run & \
	wait

# Catch-all target to prevent "No rule to make target" errors
%:
	@: