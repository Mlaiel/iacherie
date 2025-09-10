# Revenue Distribution Service - Automated revenue sharing and tracking
# Manages revenue distribution and payment processing for creators
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/revenue-distribution.txt .
RUN pip install --no-cache-dir -r revenue-distribution.txt

FROM base AS production

# Create non-root user
RUN groupadd -r revenue && useradd -r -g revenue revenue

# Copy application code
COPY src/distribution/revenue_distribution/ ./revenue_distribution/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/reports /app/payments /var/log/revenue
RUN chown -R revenue:revenue /app /var/log/revenue

USER revenue

EXPOSE 8007

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8007/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8007
ENV REVENUE_SHARE_PERCENTAGE=70
ENV ENABLE_AUTOMATIC_PAYOUTS=false

CMD ["python", "-m", "uvicorn", "revenue_distribution.main:app", "--host", "0.0.0.0", "--port", "8007", "--workers", "2"]