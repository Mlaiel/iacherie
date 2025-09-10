# Encryption Manager Service - Key management and data encryption
# Manages encryption keys, data encryption/decryption, and secure storage
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for encryption
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/encryption-manager.txt .
RUN pip install --no-cache-dir -r encryption-manager.txt

FROM base AS production

# Create non-root user
RUN groupadd -r crypto && useradd -r -g crypto crypto

# Copy application code
COPY src/security/encryption_manager/ ./encryption_manager/
COPY src/security/common/ ./common/
COPY src/security/config/ ./config/

# Create directories
RUN mkdir -p /app/keys /app/backups /var/log/crypto
RUN chown -R crypto:crypto /app /var/log/crypto

USER crypto

EXPOSE 8104

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8104/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8104
ENV KMS_PROVIDER=vault

CMD ["python", "-m", "uvicorn", "encryption_manager.main:app", "--host", "0.0.0.0", "--port", "8104", "--workers", "2"]