# Cross-Platform Sync Service - Synchronization across all platforms
# Ensures content consistency and metadata sync across platforms
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/cross-platform-sync.txt .
RUN pip install --no-cache-dir -r cross-platform-sync.txt

FROM base AS production

# Create non-root user
RUN groupadd -r syncuser && useradd -r -g syncuser syncuser

# Copy application code
COPY src/distribution/cross_platform_sync/ ./cross_platform_sync/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/sync_logs /app/conflicts /var/log/sync
RUN chown -R syncuser:syncuser /app /var/log/sync

USER syncuser

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8010/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8010
ENV SYNC_INTERVAL_MINUTES=15
ENV ENABLE_CONFLICT_RESOLUTION=true

CMD ["python", "-m", "uvicorn", "cross_platform_sync.main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "2"]