# =============================================================================
# AINFLUE REVENUE TRACKER - MULTI-PLATFORM DOCKERFILE
# =============================================================================
# Multi-stage Docker build for comprehensive revenue tracking across
# multiple platforms with real-time analytics and automated reporting.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: REVENUE TRACKING BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS revenue-base

LABEL stage=revenue-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Multi-platform revenue tracking service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for revenue tracking
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        build-essential \
        pkg-config \
        curl \
        wget \
        git \
        # Data processing dependencies
        sqlite3 \
        postgresql-client \
        # System utilities
        cron \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r revenueuser && \
    useradd -r -g revenueuser -d /app -s /bin/bash revenueuser && \
    mkdir -p /app && \
    chown -R revenueuser:revenueuser /app

# =============================================================================
# STAGE 2: REVENUE TRACKING DEPENDENCIES
# =============================================================================
FROM revenue-base AS revenue-deps

# Install Python dependencies for revenue tracking
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        # Core libraries
        numpy \
        pandas \
        matplotlib \
        seaborn \
        plotly \
        # Database connectivity
        psycopg2-binary \
        SQLAlchemy \
        alembic \
        redis \
        # API integrations
        requests \
        aiohttp \
        httpx \
        # Payment processors
        stripe \
        paypalrestsdk \
        # Platform APIs
        spotipy \
        google-api-python-client \
        # Data analysis
        scikit-learn \
        # Web framework
        fastapi \
        uvicorn \
        pydantic \
        celery \
        # Monitoring
        prometheus-client \
        structlog \
        # Scheduling
        schedule \
        apscheduler \
        # File handling
        openpyxl \
        xlsxwriter \
        # Time series
        influxdb-client

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM revenue-deps AS revenue-app

WORKDIR /app

# Copy application code
COPY ./revenue_tracker /app/revenue_tracker
COPY ./core /app/core
COPY ./config /app/config

# Create revenue tracking directories
RUN mkdir -p /app/storage/revenue/reports \
             /app/storage/revenue/exports \
             /app/storage/revenue/archives \
             /app/storage/revenue/temp \
             /app/logs \
             /app/cache \
             /app/data/platforms \
             /app/data/analytics && \
    chown -R revenueuser:revenueuser /app

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM revenue-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/revenue_tracker/start.sh

USER revenueuser

# Revenue tracking environment variables
ENV REVENUE_SERVICE_PORT=8040
ENV REVENUE_WORKERS=3
ENV TRACKING_INTERVAL=3600
ENV REPORT_GENERATION_HOUR=6
# Platform configurations
ENV SPOTIFY_CLIENT_ID=""
ENV SPOTIFY_CLIENT_SECRET=""
ENV YOUTUBE_API_KEY=""
ENV APPLE_MUSIC_KEY=""
ENV SOUNDCLOUD_CLIENT_ID=""
# Payment processor settings
ENV STRIPE_SECRET_KEY=""
ENV PAYPAL_CLIENT_ID=""
ENV PAYPAL_CLIENT_SECRET=""
# Database settings
ENV REVENUE_DB_POOL_SIZE=20
ENV REVENUE_DB_TIMEOUT=30
# Analytics settings
ENV ANALYTICS_RETENTION_DAYS=365
ENV REAL_TIME_UPDATES=true
ENV CACHE_TTL=1800

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${REVENUE_SERVICE_PORT}/health || exit 1

EXPOSE ${REVENUE_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/data"]

CMD ["python3.11", "-m", "revenue_tracker.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM revenue-app AS development

RUN python3.11 -m pip install --no-cache-dir \
        pytest \
        pytest-asyncio \
        pytest-cov \
        black \
        isort \
        flake8 \
        mypy \
        ipython \
        jupyter \
        debugpy \
        # Additional dev tools
        streamlit \
        dash \
        bokeh

ENV REVENUE_SERVICE_PORT=8040
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER revenueuser

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${REVENUE_SERVICE_PORT}/health || exit 1

EXPOSE ${REVENUE_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/data"]

CMD ["python3.11", "-m", "revenue_tracker.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Revenue Tracker"
LABEL org.opencontainers.image.description="Multi-platform revenue tracking and analytics service"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="revenue_tracker"
LABEL ainflue.service.port="8040"
LABEL ainflue.monetization.platforms="spotify,youtube,apple_music,soundcloud"
LABEL ainflue.security.non-root="true"