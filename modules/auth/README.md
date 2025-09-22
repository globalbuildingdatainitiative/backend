# Auth

This is the Auth module for [GBDI](https://gbdi.io).
It is a Python service with a GraphQL API, using the async capabilities of [FastAPI](https://fastapi.tiangolo.com/)
and [Strawberry](https://strawberry.rocks).

## Description

The Auth module handles users and authentication with [Supertokens](https://supertokens.com) in the GBDI app.

## Setup

For the database connection we use [Beanie](https://beanie-odm.dev/) as an ODM and [MongoDB](https://www.mongodb.com/)
as the database.

The deployment is done with [Kubernetes](https://kubernetes.io/), [Helm](https://helm.sh/)
and [Skaffold](https://skaffold.dev/).

# Module Structure

```
├── graphql            # GraphQL schema
├── helm               # Helm chart for deployment 
├── src                # Source code
│   ├── core           # Code related to FastAPI/webserver
│   ├── exceptions     # Custom exceptions
│   ├── logic          # Logic for data handling
│   ├── models         # GraphQL and database models
│   ├── routes         # API routes. We only have one /api/graphql
│   ├── schema         # GraphQL schema endpoints
│   └── main.py        # Entry point of the application
├── test               # Test code
│   ├── integration    # Integration tests
│   ├── unit           # Unit tests
│   └── conftest.py    # Pytest configuration
├── Dockerfile         # Dockerfile for the application
├── export_schema.sh   # Export GraphQL Schema
├── pyproject.toml     # Project dependencies
├── uv.lock            # Locked dependencies
└── README.md          # Project documentation
```

# Get Started

## Environment Variables

Before running the application locally, you need to set up the required environment variables:

1. Copy the example environment file:
   ```shell
   cp .env.example .env
   ```

2. Edit the `.env` file and update the values according to your local setup.

3. Run the application using the Makefile:
   ```shell
   make run
   ```
   
   This will automatically load the `.env` file and start the application.

## Software Dependencies

### Windows

- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [Docker](https://docs.docker.com/desktop/windows/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.12
- [uv](https://github.com/astral-sh/uv)

### Linux/MacOS

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.12
- [uv](https://github.com/astral-sh/uv)

### Install dependencies

```shell
# Install packages
uv sync --dev
```

## Local Development

### Run Tests Locally

```shell
uv run pytest tests/
```

### Export GraphQL schema

```shell
./export_schema.sh
```

### Create Database Migration
```shell
alembic revision --autogenerate
```

## Running

The module should be run using Skaffold and the configuration file in the root directory.

# Access API

When the containers are running the API can be accessed
at [http://localhost:7001/api/graphql](http://localhost:7002/api/graphql)
