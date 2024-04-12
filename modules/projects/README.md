# Projects

This is the Projects module for [GBDI](https://gbdi.io).
It is a Python service with a GraphQL API, using the async capabilities of [FastAPI](https://fastapi.tiangolo.com/) and [Strawberry](https://strawberry.rocks).

For the database connection we use [Beanie](https://beanie-odm.dev/) as an ODM and [MongoDB](https://www.mongodb.com/) as the database.

The deployment is done with [Kubernetes](https://kubernetes.io/), [Helm](https://helm.sh/) and [Skaffold](https://skaffold.dev/).

# Folder Structure

```
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

## Software dependencies

### Windows

- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [Docker](https://docs.docker.com/desktop/windows/install/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.12
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
- [pre-commit](https://pre-commit.com/#installation)

### Linux/MacOS

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
- Python 3.12
- [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
- [pre-commit](https://pre-commit.com/#installation)

**Install dependencies**
```shell
# Install packages
pipenv install --dev

# Install pre-commit hooks
pre-commit install
```

**Run tests locally**

```shell
pytest tests/
```

**Export GraphQL schema**

```shell
./export_schema.sh
```

# Access API

When the containers are running (see steps below) the API can be accessed
at [http://localhost:8000/api/graphql](http://localhost:8000/api/graphql)