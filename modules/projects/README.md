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
├── pyproject.toml     # Project dependencies
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

## Running

The module should be run using Skaffold and the configuration file in the root directory.

# Access API

When the containers are running the API can be accessed
at [http://localhost:7003/api/graphql](http://localhost:7003/api/graphql)

# New API Endpoints

## Mutations

### submitForReview
Submit a project for review (Contributor action)
Transitions: DRAFT → IN_REVIEW

### approveProject
Approve a project for publication (Reviewer action)
Transitions: IN_REVIEW → TO_PUBLISH

### rejectProject
Reject a project and send it back to draft (Reviewer action)
Transitions: IN_REVIEW → DRAFT

### publishProject
Publish a project (Administrator action)
Transitions: TO_PUBLISH → DRAFT (published)

### unpublishProject
Mark a project for unpublishing (Administrator action)
Transitions: DRAFT → TO_UNPUBLISH

### deleteProject
Delete a project (Administrator action)
Transitions: TO_DELETE → deleted

### lockProject
Lock a project (Administrator action)
Transitions: any state → LOCKED

### unlockProject
Unlock a project (Administrator action)
Transitions: LOCKED → previous state

### assignProject
Assign a project to a user (Administrator action)

## Queries

### projectsByState
Get projects by state

### projectsForReview
Get projects that are in review (IN_REVIEW state)

### projectsToPublish
Get projects that are ready to publish (TO_PUBLISH state)

### projectsToUnpublish
Get projects that are marked for unpublishing (TO_UNPUBLISH state)

### projectsToDelete
Get projects that are marked for deletion (TO_DELETE state)

### myProjects
Get projects created by the current user

### assignedProjects
Get projects assigned to the current reviewer

# Project States

- DRAFT: The project is being added or edited and is not yet ready for review
- IN_REVIEW: The project is ready for review by a reviewer
- TO_PUBLISH: The project has been reviewed and approved for publication by a reviewer
- TO_UNPUBLISH: The project is currently published and needs to be unpublished by an administrator
- TO_DELETE: The project is marked for deletion by an administrator
- LOCKED: The project is locked by an administrator and cannot be edited, (un)published or deleted

# User Roles

- CONTRIBUTOR: Can add and edit their own project contributions
- REVIEWER: Can add and edit all project contributions but cannot (un)publish, or delete them
- ADMINISTRATOR: Can perform all operations, including project (un)publication and deletion
