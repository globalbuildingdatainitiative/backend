# GBDI Backend

# Getting Started

To get started please make sure that the following pieces of software are installed on your machine.

## Windows

* [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
* [Docker](https://docs.docker.com/desktop/windows/install/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
* Python 3.11
* [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
* [pre-commit](https://pre-commit.com/#installation)

## Linux

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [Skaffold](https://skaffold.dev/docs/install/#standalone-binary)
* Python 3.11
* [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
* [pre-commit](https://pre-commit.com/#installation)

### Initial Setup
Copy `template.skaffold.env` to `skaffold.env` and populate the env vars

# Folder Structure

```plaintext
modules/  # Contains our modules
    auth/  # authentication module/service
    organization/  # Organization module/service
    router/  # API Gateway implemented with Apollo Router
skaffold.yaml  # Skaffold config for running all services
```


## Run

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
* [Router](./modules/router/README.md)
