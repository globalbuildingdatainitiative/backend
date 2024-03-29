# Strawberry Template

This repo is a template for setting up a project as a GraphQL API, using the async capabilities of FastAPI and Strawberry.

For the database connection we use SQLModel as an ORM and PostgreSQL as the database.

This template is for an async setup. If you wish to create a sync API please refer to this [template](https://github.com/ocni-dtu/strawberry_template)  

The deployment is done with Kubernetes, Helm and Skaffold.

# Folder Structure

```
alembic/
    # Contains migrations
graphql/
    # Contains graphql schema for the gateway
helm/
    # helm chart for deployment
src/
    # source code
    core/
        # code related to FastAPI/webserver
    exceptions/
        # custom exceptions
    graphql_types/
        # GraphQL types for Strawberry
    routes/
        # api routes. We only have one /api/graphql
    schema/
        # graphql schema definitions
tests/
    # test code 
```

# Get Started

After cloning this template, please replace all instances of `ASYNC_STRAWBERRY` in the files, with your own project name.

To get started please make sure that the following pieces of software are installed on your machine.

## Software dependencies

### Windows

- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [Docker](https://docs.docker.com/desktop/windows/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.11
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
- [pre-commit](https://pre-commit.com/#installation)

### Linux

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.11
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
- [pre-commit](https://pre-commit.com/#installation)

**Install dependencies**
```shell
# Install packages
pipenv install --dev

# Install pre-commit hooks
pre-commit install
```

**Start dev server**

```shell
# Start Minikube to run a local Kubernetes cluster
minikube start
# Run Skaffold
skaffold dev
```

**Run tests locally**

```shell
pytest tests/
```

**Make migration**
Skaffold should be running!

```shell
./local_migration.sh
```

**Export GraphQL schema**

```shell
./export_schema.sh
```

# Access API

When the containers are running (see steps below) the API can be accessed
at [http://localhost:8000/api/graphql](http://localhost:8000/api/graphql)