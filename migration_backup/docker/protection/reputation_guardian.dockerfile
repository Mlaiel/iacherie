# =============================================================================
# AINFLUE REPUTATION GUARDIAN - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for reputation protection and monitoring
# supporting social media monitoring, sentiment analysis, and reputation management.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: REPUTATION GUARDIAN BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS reputation-base

LABEL stage=reputation-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced reputation protection and monitoring engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install reputation monitoring dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        libxml2-dev \
        libxslt1-dev \
        libssl-dev \
        curl \
        wget \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM reputation-base AS reputation-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install reputation monitoring packages
RUN pip3 install --no-cache-dir \
        tweepy>=4.14.0 \
        facebook-sdk>=3.1.0 \
        instagram-private-api>=1.6.0 \
        youtube-dl>=2021.12.17 \
        beautifulsoup4>=4.12.0 \
        scrapy>=2.11.0 \
        selenium>=4.15.0 \
        nltk>=3.8.0 \
        textblob>=0.17.1 \
        vaderSentiment>=3.3.2 \
        transformers>=4.35.0 \
        torch>=2.0.0 \
        scikit-learn>=1.3.0 \
        pandas>=2.1.0 \
        numpy>=1.24.0 \
        requests>=2.31.0 \
        aiohttp>=3.9.0 \
        asyncio \
        celery>=5.3.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM reputation-deps AS reputation-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./protection/reputation_guardian/ /app/
COPY --chown=appuser:appuser ./core/social_utils.py /app/core/
COPY --chown=appuser:appuser ./config/protection_config.py /app/config/

# Create directories for monitoring data
RUN mkdir -p /app/monitoring /app/reports /app/alerts /app/cache && \
    chown -R appuser:appuser /app/monitoring /app/reports /app/alerts /app/cache

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Environment variables
ENV MONITORING_INTERVAL=300
ENV SENTIMENT_THRESHOLD=-0.5
ENV ENABLE_REAL_TIME_ALERTS=true
ENV MAX_PLATFORMS=10

# Expose port for API
EXPOSE 8042

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8042/health || exit 1

# Switch to non-root user
USER appuser

# Start reputation guardian service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8042", "--workers", "2"]