# =============================================================================
# AINFLUE SPECTRUM ANALYZER - REAL-TIME DOCKERFILE
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS spectrum-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Real-time spectrum analysis service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip build-essential \
        ffmpeg libsndfile1-dev libfftw3-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r specuser && \
    useradd -r -g specuser -d /app specuser && \
    mkdir -p /app && chown -R specuser:specuser /app

FROM spectrum-base AS spectrum-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        librosa soundfile numpy scipy matplotlib \
        plotly essentia fastapi uvicorn pydantic

FROM spectrum-deps AS production

WORKDIR /app
COPY ./spectrum_analyzer /app/spectrum_analyzer
COPY ./core /app/core

RUN mkdir -p /app/storage/spectrum /app/logs && \
    chown -R specuser:specuser /app

USER specuser

ENV SPECTRUM_SERVICE_PORT=8018
ENV FFT_SIZE=2048
ENV HOP_LENGTH=512

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${SPECTRUM_SERVICE_PORT}/health || exit 1

EXPOSE ${SPECTRUM_SERVICE_PORT}
CMD ["python3.11", "-m", "spectrum_analyzer.main"]

LABEL org.opencontainers.image.title="Ainflue Spectrum Analyzer"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="spectrum_analyzer"
LABEL ainflue.service.port="8018"