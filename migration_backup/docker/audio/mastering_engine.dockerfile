# =============================================================================
# AINFLUE MASTERING ENGINE - PROFESSIONAL DOCKERFILE
# =============================================================================
# Multi-stage Docker build for automated mastering with EQ, compression,
# limiting, stereo enhancement, and loudness optimization.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

FROM ubuntu:${UBUNTU_VERSION} AS mastering-base

LABEL stage=mastering-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional automated mastering service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget git \
        ffmpeg sox libsox-fmt-all libsndfile1-dev \
        libsamplerate0-dev libavcodec-dev libavformat-dev \
        libfftw3-dev libblas-dev liblapack-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r masteruser && \
    useradd -r -g masteruser -d /app masteruser && \
    mkdir -p /app && chown -R masteruser:masteruser /app

FROM mastering-base AS mastering-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        librosa soundfile numpy scipy matplotlib \
        pyloudnorm essentia pedalboard resampy \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client structlog

FROM mastering-deps AS mastering-app

WORKDIR /app
COPY ./mastering_engine /app/mastering_engine
COPY ./core /app/core
COPY ./config /app/config

RUN mkdir -p /app/storage/mastering/{input,output,presets} \
             /app/logs /app/cache && \
    chown -R masteruser:masteruser /app

FROM mastering-app AS production

RUN rm -rf /tmp/* /var/tmp/* && \
    find /app -type d -exec chmod 755 {} \; && \
    find /app -type f -exec chmod 644 {} \;

USER masteruser

ENV MASTERING_SERVICE_PORT=8015
ENV MASTERING_WORKERS=2
ENV TARGET_LUFS=-14.0
ENV TRUE_PEAK_LIMIT=-1.0
ENV STEREO_WIDTH=1.2

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${MASTERING_SERVICE_PORT}/health || exit 1

EXPOSE ${MASTERING_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache"]

CMD ["python3.11", "-m", "mastering_engine.main"]

LABEL org.opencontainers.image.title="Ainflue Mastering Engine"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="mastering_engine"
LABEL ainflue.service.port="8015"