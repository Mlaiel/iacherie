# Integration Tester Service
# Multi-service integration testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Integration Tester - Multi-service validation"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq5 \
        libpq-dev \
        pkg-config \
        docker.io \
        docker-compose \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r integrationtester && useradd -r -g integrationtester integrationtester
RUN usermod -aG docker integrationtester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-integration.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-integration.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/integration_tester/ ./integration_tester/
COPY ./testing/common/ ./common/
COPY ./testing/integration_tests/ ./integration_tests/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/docker_logs && \
    chown -R integrationtester:integrationtester /app

# Switch to non-root user
USER integrationtester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=integration_tester
ENV LOG_LEVEL=INFO
ENV DOCKER_HOST=unix:///var/run/docker.sock

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Default command
CMD ["python", "-m", "pytest", "integration_tests/", "-v", "--junit-xml=reports/integration.xml"]