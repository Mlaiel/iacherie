# =============================================================================
# AINFLUE COPYRIGHT MONITOR - REAL-TIME DOCKERFILE
# =============================================================================
# Multi-stage Docker build for real-time copyright violation monitoring
# across multiple platforms and content types.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS monitor-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Real-time copyright violation monitoring service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl wget git \
        ffmpeg libsndfile1-dev libopencv-dev \
        chromium-browser chromium-chromedriver \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r monitoruser && \
    useradd -r -g monitoruser -d /app monitoruser && \
    mkdir -p /app && chown -R monitoruser:monitoruser /app

FROM monitor-base AS monitor-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        requests aiohttp beautifulsoup4 selenium \
        scrapy playwright asyncio \
        numpy scipy librosa soundfile \
        opencv-python pillow imagehash \
        torch scikit-learn \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        schedule apscheduler

# Install Playwright browsers
RUN playwright install chromium

FROM monitor-deps AS monitor-app

WORKDIR /app
COPY ./copyright_monitor /app/copyright_monitor
COPY ./core /app/core

RUN mkdir -p /app/storage/monitoring/{scans,reports,evidence} \
             /app/logs /app/cache && \
    chown -R monitoruser:monitoruser /app

FROM monitor-app AS production

USER monitoruser

ENV MONITOR_SERVICE_PORT=8023
ENV SCAN_INTERVAL=300
ENV VIOLATION_THRESHOLD=0.9
ENV PLATFORMS=youtube,spotify,soundcloud,instagram
ENV MAX_CONCURRENT_SCANS=10

HEALTHCHECK --interval=30s --timeout=15s --retries=3 \
    CMD curl -f http://localhost:${MONITOR_SERVICE_PORT}/health || exit 1

EXPOSE ${MONITOR_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache"]

CMD ["python3.11", "-m", "copyright_monitor.main"]

LABEL org.opencontainers.image.title="Ainflue Copyright Monitor"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="copyright_monitor"
LABEL ainflue.service.port="8023"