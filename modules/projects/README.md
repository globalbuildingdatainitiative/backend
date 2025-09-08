# Projects

This is the Projects module for [GBDI](https://gbdi.io).
It is a Python service with a GraphQL API, using the async capabilities of [FastAPI](https://fastapi.tiangolo.com/)
and [Strawberry](https://strawberry.rocks).

## Description

The Projects module handles CRUD operations related to contributions and projects in the GBDI app.

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
├── Pipfile            # Project dependencies
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
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

### Linux/MacOS

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.12
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

### Install dependencies

```shell
# Install packages
pipenv install --dev
```

## Local Development

### Run Tests Locally

```shell
pytest tests/
```

### Export GraphQL schema

```shell
./export_schema.sh
```

## Running

The module should be run using Skaffold and the configuration file in the root directory.

# Access API

When the containers are running the API can be accessed
at [http://localhost:7003/api/graphql](http://localhost:7003/api/graphql)
