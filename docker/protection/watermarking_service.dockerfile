# =============================================================================
# AINFLUE WATERMARKING SERVICE - ADVANCED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced watermarking with invisible/visible
# watermarks for audio, video, and image content.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS watermark-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced watermarking service for content protection"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget git \
        ffmpeg imagemagick libopencv-dev \
        libsndfile1-dev libavcodec-dev libavformat-dev \
        libjpeg-dev libpng-dev libmagickwand-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r watermarkuser && \
    useradd -r -g watermarkuser -d /app watermarkuser && \
    mkdir -p /app && chown -R watermarkuser:watermarkuser /app

FROM watermark-base AS watermark-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy scipy pillow opencv-python matplotlib \
        librosa soundfile pydub \
        torch torchvision scikit-image \
        cryptography pycryptodome \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM watermark-deps AS watermark-app

WORKDIR /app
COPY ./watermarking_service /app/watermarking_service
COPY ./core /app/core

RUN mkdir -p /app/storage/watermarks/{input,output,templates} \
             /app/logs /app/cache /app/keys && \
    chown -R watermarkuser:watermarkuser /app

FROM watermark-app AS production

USER watermarkuser

ENV WATERMARK_SERVICE_PORT=8022
ENV WATERMARK_STRENGTH=0.1
ENV WATERMARK_TYPE=invisible
ENV SUPPORTED_FORMATS=audio,video,image

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${WATERMARK_SERVICE_PORT}/health || exit 1

EXPOSE ${WATERMARK_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/keys"]

CMD ["python3.11", "-m", "watermarking_service.main"]

LABEL org.opencontainers.image.title="Ainflue Watermarking Service"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="watermarking_service"
LABEL ainflue.service.port="8022"