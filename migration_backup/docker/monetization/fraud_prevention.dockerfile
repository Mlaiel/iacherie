# Fraud Prevention Service
# Advanced fraud detection and prevention for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Fraud Prevention - Advanced fraud detection and prevention"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # ML libraries system deps
        libhdf5-dev \
        libatlas-base-dev \
        libopenblas-dev \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r fraudprev && useradd -r -g fraudprev fraudprev

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-fraud.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-fraud.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./monetization/fraud_prevention/ ./fraud_prevention/
COPY ./monetization/common/ ./common/
COPY ./models/fraud/ ./models/

# Create necessary directories
RUN mkdir -p /app/storage/fraud/analysis \
             /app/storage/fraud/reports \
             /app/storage/fraud/patterns \
             /app/logs \
             /app/cache && \
    chown -R fraudprev:fraudprev /app

# Switch to non-root user
USER fraudprev

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=fraud_prevention
ENV LOG_LEVEL=INFO
ENV FRAUD_THRESHOLD=0.75
ENV REAL_TIME_MONITORING=true
ENV BLOCK_SUSPICIOUS_TRANSACTIONS=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8032/health || exit 1

# Expose port
EXPOSE 8032

# Default command
CMD ["python", "-m", "fraud_prevention.main"]