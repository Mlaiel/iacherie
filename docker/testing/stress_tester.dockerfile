# Stress Tester Service
# System stress and breaking point testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Stress Tester - System breaking point testing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        stress-ng \
        htop \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r stresstester && useradd -r -g stresstester stresstester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-stress.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-stress.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/stress_tester/ ./stress_tester/
COPY ./testing/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs && \
    chown -R stresstester:stresstester /app

USER stresstester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=stress_tester
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

EXPOSE 8005

CMD ["python", "-m", "pytest", "stress_tests/", "-v"]