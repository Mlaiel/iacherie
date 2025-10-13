# Hashtag Optimizer Service - AI-powered hashtag generation and optimization
# Uses ML models to generate trending and effective hashtags
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
COPY requirements/hashtag-optimizer.txt .
RUN pip install --no-cache-dir -r hashtag-optimizer.txt

FROM base AS production

# Create non-root user
RUN groupadd -r hashtaguser && useradd -r -g hashtaguser hashtaguser

# Copy application code
COPY src/distribution/hashtag_optimizer/ ./hashtag_optimizer/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/models /app/cache
RUN chown -R hashtaguser:hashtaguser /app

USER hashtaguser

EXPOSE 8004

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8004

CMD ["python", "-m", "uvicorn", "hashtag_optimizer.main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "2"]