# A/B Testing Engine Service - Statistical testing for content optimization
# Manages A/B tests for publication strategies and content variants
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
COPY requirements/ab-testing-engine.txt .
RUN pip install --no-cache-dir -r ab-testing-engine.txt

FROM base AS production

# Create non-root user
RUN groupadd -r abtesting && useradd -r -g abtesting abtesting

# Copy application code
COPY src/distribution/ab_testing_engine/ ./ab_testing_engine/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/reports /app/experiments
RUN chown -R abtesting:abtesting /app

USER abtesting

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8005/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8005
ENV MIN_SAMPLE_SIZE=1000
ENV CONFIDENCE_LEVEL=0.95

CMD ["python", "-m", "uvicorn", "ab_testing_engine.main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "2"]