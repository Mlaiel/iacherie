# Content Security Service - DRM and content protection for distribution
# Ensures content security across all distribution platforms
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for security
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/content-security.txt .
RUN pip install --no-cache-dir -r content-security.txt

FROM base AS production

# Create non-root user
RUN groupadd -r security && useradd -r -g security security

# Copy application code
COPY src/distribution/content_security/ ./content_security/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories
RUN mkdir -p /app/keys /app/watermarks /app/encrypted
RUN chown -R security:security /app

USER security

EXPOSE 8008

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8008
ENV ENABLE_WATERMARKING=true
ENV ENABLE_DRM=true

CMD ["python", "-m", "uvicorn", "content_security.main:app", "--host", "0.0.0.0", "--port", "8008", "--workers", "2"]