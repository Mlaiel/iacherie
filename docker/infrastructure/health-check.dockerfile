# Health Check Service
# Centralized health monitoring for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Health Check - Centralized service health monitoring"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        wget \
        netcat-traditional \
        dnsutils \
        iputils-ping \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r healthcheck && useradd -r -g healthcheck healthcheck

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-healthcheck.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-healthcheck.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./infrastructure/health_check/ ./health_check/
COPY ./infrastructure/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/config && \
    chown -R healthcheck:healthcheck /app

# Copy health check scripts
COPY ./scripts/health_checks/ ./scripts/

# Switch to non-root user
USER healthcheck

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=health_check
ENV LOG_LEVEL=INFO
ENV HEALTH_CHECK_INTERVAL=30
ENV HEALTH_CHECK_TIMEOUT=10
ENV HEALTH_CHECK_RETRIES=3

# Health check for the health checker itself
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["python", "-m", "health_check.main"]