# Makefile for Router module

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build-graph
build-graph: ## Build the supergraph schema
	@echo "Building supergraph schema..."
	@mkdir -p ./config/generated
	@rover supergraph compose --elv2-license accept --config config/supergraph-config-local.yaml > ./config/generated/supergraph.graphql
	@echo "✓ Supergraph schema built"

.PHONY: run
run: build-graph ## Run the router locally
	@echo "Starting Apollo Router..."
	@AUTH_URL=http://localhost:7001/api/graphql \
	ORGANIZATION_URL=http://localhost:7002/api/graphql \
	PROJECTS_URL=http://localhost:7003/api/graphql \
	CLIENT_ORIGIN=http://localhost:8000 \
	ENABLE_INTROSPECTION=true \
	rover dev --supergraph-config config/supergraph-config-local.yaml --router-config config/router-local.yaml --supergraph-port 4000

.PHONY: clean
clean: ## Clean up generated files
	@rm -rf config/generated
	@echo "✓ Router cleaned"
