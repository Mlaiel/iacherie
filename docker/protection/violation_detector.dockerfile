# =============================================================================
# AINFLUE VIOLATION DETECTOR - AI-POWERED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS detector-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="AI-powered violation detection service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        libopencv-dev libsndfile1-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r detectoruser && \
    useradd -r -g detectoruser -d /app detectoruser && \
    mkdir -p /app && chown -R detectoruser:detectoruser /app

FROM detector-base AS detector-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        torch torchvision scikit-learn \
        numpy opencv-python librosa \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM detector-deps AS production

WORKDIR /app
COPY ./violation_detector /app/violation_detector
COPY ./core /app/core

RUN mkdir -p /app/storage/violations /app/logs /app/models && \
    chown -R detectoruser:detectoruser /app

USER detectoruser

ENV DETECTOR_SERVICE_PORT=8026
ENV AI_MODEL_PATH=/app/models
ENV DETECTION_THRESHOLD=0.8

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${DETECTOR_SERVICE_PORT}/health || exit 1

EXPOSE ${DETECTOR_SERVICE_PORT}
CMD ["python3.11", "-m", "violation_detector.main"]

LABEL org.opencontainers.image.title="Ainflue Violation Detector"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="violation_detector"
LABEL ainflue.service.port="8026"