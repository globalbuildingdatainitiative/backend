# Install uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

# Copy project files
COPY ./pyproject.toml ./uv.lock /app/

# Copy the project into the intermediate image
COPY . /app

# Install dependencies including the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

FROM python:3.12-slim

# Set environment
ENV PATH="/app/.venv/bin/:${PATH}"
ENV PYTHONPATH="/app/src"

# Create fastapi user
RUN useradd --home-dir /app --create-home fastapi
USER fastapi
WORKDIR /app

# Copy the environment, but not the source code
COPY --from=builder --chown=fastapi:fastapi /app/.venv /app/.venv

# Copy source files into container
COPY --chown=fastapi:fastapi ./entrypoint.sh /app/
COPY --chown=fastapi:fastapi ./src /app/src/
COPY --chown=fastapi:fastapi ./graphql /app/graphql/
COPY --chown=fastapi:fastapi ./export_schema.sh /app/

ENTRYPOINT ["bash", "/app/entrypoint.sh"]


