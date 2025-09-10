# Chaos Engineering Service
# Fault injection and resilience testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Chaos Engineering - Fault injection and resilience testing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        docker.io \
        iptables \
        tc \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r chaostester && useradd -r -g chaostester chaostester
RUN usermod -aG docker chaostester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-chaos.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-chaos.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/chaos_engineering/ ./chaos_engineering/
COPY ./testing/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs && \
    chown -R chaostester:chaostester /app

USER chaostester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=chaos_engineering
ENV LOG_LEVEL=INFO
ENV DOCKER_HOST=unix:///var/run/docker.sock

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

EXPOSE 8006

CMD ["chaos", "run", "experiments/"]