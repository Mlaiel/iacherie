# =============================================================================
# AINFLUE WAVEFORM GENERATOR - VISUALIZATION DOCKERFILE
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS waveform-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced waveform generation and visualization"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip build-essential \
        ffmpeg libsndfile1-dev libcairo2-dev pkg-config \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r waveuser && \
    useradd -r -g waveuser -d /app waveuser && \
    mkdir -p /app && chown -R waveuser:waveuser /app

FROM waveform-base AS waveform-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        librosa soundfile numpy matplotlib plotly \
        pillow cairo-python fastapi uvicorn pydantic

FROM waveform-deps AS production

WORKDIR /app
COPY ./waveform_generator /app/waveform_generator
COPY ./core /app/core

RUN mkdir -p /app/storage/waveforms /app/logs && \
    chown -R waveuser:waveuser /app

USER waveuser

ENV WAVEFORM_SERVICE_PORT=8017

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${WAVEFORM_SERVICE_PORT}/health || exit 1

EXPOSE ${WAVEFORM_SERVICE_PORT}
CMD ["python3.11", "-m", "waveform_generator.main"]

LABEL org.opencontainers.image.title="Ainflue Waveform Generator"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="waveform_generator"
LABEL ainflue.service.port="8017"