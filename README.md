# GBDI Backend

This repository contains the backend services for the [GBDI](https://app.gbdi.io) (Global Building Data Initiative)
application.
The backend is composed of multiple modules, each responsible for a specific domain within the application.
The primary technologies used include Python, FastAPI, Strawberry for GraphQL, and MongoDB for data storage.
The deployment is managed using Kubernetes, Helm, and Skaffold.

## Key Features

- Modular Architecture: The backend is divided into several modules, each handling a distinct aspect of the application,
  such as authentication, organization management, and project management. This modular approach ensures code
  reusability and maintainability.
- GraphQL API: The backend services expose a GraphQL API using Strawberry, allowing for efficient data querying and
  manipulation.
- Authentication: The Auth module handles user authentication and management using Supertokens, ensuring secure access
  to the application.
- Scalability: The use of Kubernetes and Helm for deployment ensures that the backend services can scale efficiently to
  handle increased load.
- Local Development: The repository includes configuration files and scripts to facilitate local development and testing
  using Minikube and Skaffold.

# Getting Started

To get started, please make sure that the following pieces of software are installed on your machine.

## Prerequisites

### All Platforms

* [Docker](https://docs.docker.com/get-docker/) and Docker Compose
* Python 3.12+
* [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
* [Apollo Rover](https://www.apollographql.com/docs/rover/getting-started) - GraphQL CLI tool

### Installing Rover

**macOS/Linux:**
```bash
curl -sSL https://rover.apollo.dev/nix/latest | sh
```

**Windows (PowerShell):**
```powershell
iwr 'https://rover.apollo.dev/win/latest' | iex
```

**Alternative (npm):**
```bash
npm install -g @apollo/rover
```

Verify installation:
```bash
rover --version
```

### Windows-Specific

* [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install) (recommended for running Docker)

## Quick Start

1. **Clone the repository and install dependencies:**
   ```bash
   make install
   ```

2. **Set up environment variables:**
   
   Copy the example env files and configure them:
   ```bash
   cp modules/auth/.env.example modules/auth/.env
   cp modules/organization/.env.example modules/organization/.env
   cp modules/projects/.env.example modules/projects/.env
   ```

3. **Start all services:**
   ```bash
   make run
   ```

   This will:
   - Start databases (PostgreSQL, MongoDB, SuperTokens) in Docker
   - Initialize databases and run migrations
   - Start all backend services (auth, organization, projects, router)

4. **Access the services:**
   - Auth API: http://localhost:7001
   - Organization API: http://localhost:7002
   - Projects API: http://localhost:7003
   - **GraphQL Router: http://localhost:4000/graphql** ← Main entry point
   - Health Check: http://localhost:8088

## Development Commands

```bash
make help           # Show all available commands
make db-up          # Start only database services
make db-down        # Stop database services
make run-auth       # Run only auth service
make run-organization  # Run only organization service
make run-projects   # Run only projects service
make run-router     # Run only router service
make test           # Run tests for all modules
make lint           # Run linting for all modules
make format         # Format code for all modules
make clean          # Clean up generated files
```

# Folder Structure

```
├── .github           # GitHub Actions workflows
├── modules
│   ├── auth          # Auth module for authentication and user management
│   ├── organization  # Organization module for organization management
│   ├── projects      # Projects module for contribution management
│   └── router        # Router module for GraphQL supergraph (Apollo Router)
├── docker-compose.yml  # Docker Compose config for databases
├── Makefile          # Root Makefile with common commands
├── LICENSE           # Project license
└── README.md         # Project documentation
```

# Architecture

This backend uses a **federated GraphQL architecture** with Apollo Router:

- **Microservices**: Each module (auth, organization, projects) is an independent FastAPI service with its own GraphQL schema
- **Apollo Router**: Composes all subgraph schemas into a unified supergraph accessible at `localhost:4000/graphql`
- **Local Development**: Services run on your host machine, databases run in Docker
- **Hot Reload**: Changes to schemas or code automatically reload the services

# Running the Services

## Local Development (Recommended)

```bash
# Start all services (databases + backend services + router)
make run
```

## Running Individual Components

```bash
# Start only databases
make db-up

# Run a specific service (after db-up)
make run-auth
make run-organization  
make run-projects
make run-router
```

## Test

Running tests should be in each individual module. See README there.

* [auth](./modules/auth/README.md)
* [organization](./modules/organization/README.md)
* [projects](./modules/projects/README.md)
* [router](./modules/router/README.md)
