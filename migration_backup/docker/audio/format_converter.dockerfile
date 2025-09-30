# =============================================================================
# AINFLUE FORMAT CONVERTER - MULTI-FORMAT DOCKERFILE
# =============================================================================
# Multi-stage Docker build for professional audio format conversion
# supporting WAV, FLAC, MP3, OPUS, DSD, and high-resolution formats.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS converter-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Multi-format audio conversion service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget \
        ffmpeg sox libsox-fmt-all libsndfile1-dev \
        libmp3lame-dev libvorbis-dev libflac-dev libopus-dev \
        libaac-dev libfdk-aac-dev sacd-ripper \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r convertuser && \
    useradd -r -g convertuser -d /app convertuser && \
    mkdir -p /app && chown -R convertuser:convertuser /app

FROM converter-base AS converter-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        librosa soundfile pydub mutagen numpy \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM converter-deps AS converter-app

WORKDIR /app
COPY ./format_converter /app/format_converter
COPY ./core /app/core

RUN mkdir -p /app/storage/converter/{input,output,temp} \
             /app/logs /app/cache && \
    chown -R convertuser:convertuser /app

FROM converter-app AS production

USER convertuser

ENV CONVERTER_SERVICE_PORT=8016
ENV MAX_FILE_SIZE=5GB
ENV SUPPORTED_FORMATS=wav,flac,mp3,opus,aac,ogg,dsd

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${CONVERTER_SERVICE_PORT}/health || exit 1

EXPOSE ${CONVERTER_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs"]

CMD ["python3.11", "-m", "format_converter.main"]

LABEL org.opencontainers.image.title="Ainflue Format Converter"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="format_converter"
LABEL ainflue.service.port="8016"