# Service Mesh Orchestrator
# Advanced microservices communication and orchestration
# Author: Fahed Mlaiel (mlaiel@live.de) - Microservices Architect Role

FROM envoyproxy/envoy:v1.28-latest AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Service Mesh Orchestrator - Advanced microservices communication"
LABEL version="1.0.0"

# Switch to root for installations
USER root

# Install additional tools for service mesh management
RUN apt-get update && apt-get install -y \
    # Service mesh tools
    curl \
    wget \
    jq \
    # Python for orchestration scripts
    python3 \
    python3-pip \
    # Network tools
    netcat-openbsd \
    iputils-ping \
    # Monitoring tools
    prometheus-node-exporter \
    && rm -rf /var/lib/apt/lists/*

# Install Python service mesh libraries
RUN pip3 install --no-cache-dir \
    # Service discovery
    consul-python \
    etcd3 \
    # API gateway
    flask \
    fastapi \
    uvicorn \
    # Circuit breakers
    pybreaker \
    # Monitoring
    prometheus-client \
    # Async processing
    aiohttp \
    asyncio \
    # Configuration management
    pyyaml \
    toml

WORKDIR /app

# Copy service mesh configuration
COPY ./service_mesh/envoy/ ./envoy/
COPY ./service_mesh/orchestrator/ ./orchestrator/
COPY ./service_mesh/discovery/ ./discovery/
COPY ./service_mesh/common/ ./common/

# Copy Envoy configuration files
COPY ./service_mesh/configs/envoy.yaml /etc/envoy/envoy.yaml
COPY ./service_mesh/configs/service_discovery.yaml /etc/envoy/service_discovery.yaml

# Security: Create service mesh user
RUN groupadd --gid 1000 servicemesh && \
    useradd --uid 1000 --gid servicemesh --shell /bin/bash --create-home servicemesh

# Create service mesh directories
RUN mkdir -p \
    /app/configs \
    /app/logs \
    /app/certificates \
    /app/discovery \
    /app/routing \
    /app/policies \
    && chown -R servicemesh:servicemesh /app \
    && chmod 755 /app \
    && chmod 700 /app/certificates

# Setup service mesh scripts
COPY ./service_mesh/scripts/start_mesh.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start_mesh.sh && \
    chown servicemesh:servicemesh /usr/local/bin/start_mesh.sh

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to service mesh user
USER servicemesh

# Service mesh environment variables
ENV SERVICE_NAME=service_mesh_orchestrator \
    ENVOY_ADMIN_PORT=9901 \
    ORCHESTRATOR_PORT=8000 \
    SERVICE_DISCOVERY_INTERVAL=30 \
    CIRCUIT_BREAKER_ENABLED=true \
    LOAD_BALANCING_STRATEGY=round_robin \
    TLS_ENABLED=true

# Health check for service mesh
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9901/ready || exit 1

# Expose ports for Envoy proxy and orchestrator
EXPOSE 8000 8080 9901 10000

# Start service mesh orchestrator
CMD ["/usr/local/bin/start_mesh.sh"]