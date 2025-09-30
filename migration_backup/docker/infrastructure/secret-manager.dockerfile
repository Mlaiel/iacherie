# Secret Manager Service
# HashiCorp Vault-based secret management for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM vault:1.15 AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Secret Manager - HashiCorp Vault-based secret management"
LABEL version="1.0.0"

# Create vault user for security
RUN addgroup -g 1000 vault_user && \
    adduser -D -s /bin/sh -u 1000 -G vault_user vault_user

# Install additional tools
RUN apk add --no-cache \
    curl \
    wget \
    jq \
    bash \
    openssl \
    ca-certificates

# Create necessary directories
RUN mkdir -p /vault/data \
             /vault/config \
             /vault/logs \
             /vault/policies \
             /vault/scripts && \
    chown -R vault_user:vault_user /vault

# Copy Vault configuration
COPY ./config/vault/ /vault/config/
COPY ./scripts/vault/ /vault/scripts/
COPY ./policies/vault/ /vault/policies/

# Copy custom vault configuration
COPY ./config/vault.hcl /vault/config/vault.hcl
COPY ./config/vault-dev.hcl /vault/config/vault-dev.hcl

# Copy startup script
COPY ./scripts/start-vault.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-vault.sh

# Copy initialization script
COPY ./scripts/init-vault.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init-vault.sh

# Set environment variables
ENV VAULT_DATA_DIR=/vault/data
ENV VAULT_CONFIG_DIR=/vault/config
ENV VAULT_LOG_LEVEL=INFO
ENV VAULT_API_ADDR=http://0.0.0.0:8200
ENV VAULT_CLUSTER_ADDR=http://0.0.0.0:8201
ENV VAULT_UI=true
ENV VAULT_DEV_ROOT_TOKEN_ID=""
ENV VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8200/v1/sys/health || exit 1

# Expose ports
EXPOSE 8200 8201

# Switch to non-root user
USER vault_user

# Default command
CMD ["start-vault.sh"]