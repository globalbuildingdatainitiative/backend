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

To get started please make sure that the following pieces of software are installed on your machine.

## Windows

* [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
* [Docker](https://docs.docker.com/desktop/windows/install/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
* Python 3.12
* [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

## Linux

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
* Python 3.12
* [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

### Initial Setup

Copy `template.skaffold.env` to `skaffold.env` and populate the env vars

### Environment Variables

For local development, each service requires specific environment variables to be set. These will be automatically loaded from `.env` files when running locally. Please refer to the [Environment Setup Guide](../ENVIRONMENT_SETUP.md) for detailed instructions on configuring these variables.

Each module also contains its own `.env.example` file with the required variables:
* [auth .env.example](./modules/auth/.env.example)
* [organization .env.example](./modules/organization/.env.example)
* [projects .env.example](./modules/projects/.env.example)

# Folder Structure

```
├── .github           # GitHub Actions workflows
├── modules
│   ├── auth          # Auth module for authentication and user management.
│   ├── organization  # Organization module for organization management.
│   ├── projects      # Projects module for contribution management
│   └── router        # Router module for GraphQL supergraph and API gateway.
├── skaffold.yaml     # Skaffold config for running all services
├── LICENSE           # Project license
└── README.md         # Project documentation
```

# Running the Services

```shell
# Make sure Minikube is running
minikube start

# Start Skaffold
skaffold dev
```

## Test

Running tests should be in each individual module. See README there.

* [auth](./modules/auth/README.md)
* [organization](./modules/organization/README.md)
* [projects](./modules/projects/README.md)
* [router](./modules/router/README.md)
