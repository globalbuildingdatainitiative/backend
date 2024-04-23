FROM debian:bookworm-slim

# Download curl
RUN apt-get update && apt-get install curl -y && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd --home-dir /app --create-home rover
USER rover
WORKDIR /app

# Download Rover binary

RUN curl -sSL https://rover.apollo.dev/nix/latest | sh

# Copy Router config files
COPY --chown=rover:rover ./config /app/config
COPY --chown=rover:rover ./build_graph.sh /app/build_graph.sh
RUN chmod +x /app/build_graph.sh

# Copy GraphQL schemas from services
COPY --chown=rover:rover ./schemas/projects/schema.graphql /app/schemas/projects.graphql
#COPY --chown=rover:rover ./schemas/organization/schema.graphql /app/schemas/organization.graphql

# Add Rover to PATH
ENV PATH=/app/.rover/bin:$PATH

RUN rover install --elv2-license accept --plugin 'supergraph@2'

CMD ["bash", "/app/build_graph.sh"]