# Distribution Intelligence Service - AI-powered distribution optimization
# Uses ML models to predict optimal distribution strategies
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for ML
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/distribution-intelligence.txt .
RUN pip install --no-cache-dir -r distribution-intelligence.txt

FROM base AS production

# Create non-root user
RUN groupadd -r aiuser && useradd -r -g aiuser aiuser

# Copy application code
COPY src/distribution/distribution_intelligence/ ./distribution_intelligence/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/models /app/predictions /app/cache
RUN chown -R aiuser:aiuser /app

USER aiuser

EXPOSE 8006

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8006/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8006
ENV ENABLE_PREDICTIVE_SCHEDULING=true

# Increase memory for ML models
CMD ["python", "-m", "uvicorn", "distribution_intelligence.main:app", "--host", "0.0.0.0", "--port", "8006", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]