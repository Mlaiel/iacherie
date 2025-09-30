# E2E Tester Service
# End-to-end testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue E2E Tester - End-to-end testing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        chromium \
        chromium-driver \
        firefox-esr \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r e2etester && useradd -r -g e2etester e2etester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-e2e.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-e2e.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/e2e_tester/ ./e2e_tester/
COPY ./testing/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/screenshots && \
    chown -R e2etester:e2etester /app

USER e2etester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=e2e_tester
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

EXPOSE 8007

CMD ["python", "-m", "pytest", "e2e_tests/", "-v", "--browser=chromium"]