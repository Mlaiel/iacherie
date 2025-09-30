# Test Runner Service
# Enterprise-grade test execution engine for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Test Runner - Enterprise test execution engine"
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
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r testrunner && useradd -r -g testrunner testrunner

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-testing.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-testing.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/test_runner/ ./test_runner/
COPY ./testing/common/ ./common/
COPY ./testing/tests/ ./tests/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/coverage && \
    chown -R testrunner:testrunner /app

# Switch to non-root user
USER testrunner

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=test_runner
ENV LOG_LEVEL=INFO
ENV COVERAGE_THRESHOLD=95.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "pytest", "--cov", "--cov-report=html", "--cov-report=term", "--junit-xml=reports/junit.xml"]