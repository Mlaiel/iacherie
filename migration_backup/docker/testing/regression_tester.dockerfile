# Regression Tester Service
# Regression testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Regression Tester - Automated regression testing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r regressiontester && useradd -r -g regressiontester regressiontester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-regression.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-regression.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/regression_tester/ ./regression_tester/
COPY ./testing/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/baselines && \
    chown -R regressiontester:regressiontester /app

USER regressiontester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=regression_tester
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8009/health || exit 1

EXPOSE 8009

CMD ["python", "-m", "pytest", "regression_tests/", "-v", "--tb=line"]