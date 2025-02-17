FROM python:3.12-slim as builder

ARG BUILD_STAGE
RUN python -m pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /tmp/pip
WORKDIR /tmp/pip

COPY ./Pipfile* /tmp/pip/

RUN bash -c "if [ $BUILD_STAGE = 'DEV' ]; \
    then pipenv requirements --dev > requirements.txt; \
    else pipenv requirements > requirements.txt; \
    fi"

RUN pip wheel -r requirements.txt -w /tmp/wheels

FROM python:3.12-slim

# Copy from previous stage
COPY --from=builder /tmp /tmp

# Make sure we have the latest version of pip
RUN python -m pip install --upgrade pip

# Set environment
ARG BUILD_VERSION
ENV PATH=/app/.local/bin:$PATH
ENV PYTHONPATH "${PYTHONPATH}:/app/src"
ENV BUILD_VERSION $BUILD_VERSION

# Create fastapi user
RUN useradd --home-dir /app --create-home fastapi
USER fastapi
WORKDIR /app

RUN ls /tmp/wheels
RUN apt update && apt install -y curl

# Install pip packages
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels $(ls /tmp/wheels -1 | awk -F - '{ gsub("_", "-", $1); print $1 }' | uniq)

# Delete pip wheels
USER root
RUN rm -rf /tmp/wheels

# Copy source files into container
USER fastapi
COPY --chown=fastapi:fastapi ./entrypoint.sh /app
COPY --chown=fastapi:fastapi ./src /app/src
COPY --chown=fastapi:fastapi ./export_schema.sh /app
COPY --chown=fastapi:fastapi ./graphql /app/graphql

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
