# Analytics Aggregator Service - Cross-platform analytics and insights
# Aggregates performance data from all distribution platforms
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/analytics-aggregator.txt .
RUN pip install --no-cache-dir -r analytics-aggregator.txt

# Multi-stage build for production
FROM base AS production

# Create non-root user
RUN groupadd -r analytics && useradd -r -g analytics analytics

# Copy application code
COPY src/distribution/analytics_aggregator/ ./analytics_aggregator/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/reports /app/cache /var/log/analytics
RUN chown -R analytics:analytics /app /var/log/analytics

# Switch to non-root user
USER analytics

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8003
ENV METRICS_RETENTION_DAYS=90
ENV ENABLE_REAL_TIME_ANALYTICS=true

# Run the application
CMD ["python", "-m", "uvicorn", "analytics_aggregator.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "3"]