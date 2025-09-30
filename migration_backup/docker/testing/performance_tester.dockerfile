# Performance Tester Service
# Load and performance testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Performance Tester - Load and stress testing"
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
        apache2-utils \
        siege \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r perftester && useradd -r -g perftester perftester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-performance.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-performance.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/performance_tester/ ./performance_tester/
COPY ./testing/common/ ./common/
COPY ./testing/performance_tests/ ./performance_tests/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/metrics && \
    chown -R perftester:perftester /app

# Switch to non-root user
USER perftester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=performance_tester
ENV LOG_LEVEL=INFO
ENV MAX_RESPONSE_TIME=1000
ENV MIN_THROUGHPUT=1000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Default command
CMD ["python", "-m", "locust", "--host=http://localhost", "--users=100", "--spawn-rate=10", "--run-time=300s"]