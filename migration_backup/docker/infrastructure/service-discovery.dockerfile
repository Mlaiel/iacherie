# Service Discovery Service
# Consul-based service discovery for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM consul:1.16 AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Service Discovery - Consul-based service registry and discovery"
LABEL version="1.0.0"

# Create consul user for security
RUN addgroup -g 1000 consul_user && \
    adduser -D -s /bin/sh -u 1000 -G consul_user consul_user

# Install additional tools
RUN apk add --no-cache \
    curl \
    wget \
    jq \
    bash \
    openssl

# Create necessary directories
RUN mkdir -p /consul/data \
             /consul/config \
             /consul/logs \
             /opt/consul \
             /usr/local/bin && \
    chown -R consul_user:consul_user /consul \
                                     /opt/consul

# Copy Consul configuration
COPY ./config/consul/ /consul/config/
COPY ./scripts/consul/ /usr/local/bin/

# Copy custom consul configuration
COPY ./config/consul.json /consul/config/consul.json
COPY ./config/services.json /consul/config/services.json

# Copy startup script
COPY ./scripts/start-consul.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-consul.sh

# Set environment variables
ENV CONSUL_DATA_DIR=/consul/data
ENV CONSUL_CONFIG_DIR=/consul/config
ENV CONSUL_LOG_LEVEL=INFO
ENV CONSUL_BIND_INTERFACE=eth0
ENV CONSUL_CLIENT_INTERFACE=0.0.0.0
ENV CONSUL_DATACENTER=ainflue-dc1
ENV CONSUL_DOMAIN=consul
ENV CONSUL_ENCRYPT_KEY=""
ENV CONSUL_UI=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8500/v1/status/leader || exit 1

# Expose ports
EXPOSE 8300 8301 8302 8500 8600

# Switch to non-root user
USER consul_user

# Default command
CMD ["start-consul.sh"]