# =============================================================================
# AINFLUE CONTENT SCANNER - AUTOMATED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS scanner-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated content scanning service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        ffmpeg libsndfile1-dev libopencv-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r scanuser && \
    useradd -r -g scanuser -d /app scanuser && \
    mkdir -p /app && chown -R scanuser:scanuser /app

FROM scanner-base AS scanner-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy opencv-python librosa soundfile \
        torch scikit-learn \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM scanner-deps AS production

WORKDIR /app
COPY ./content_scanner /app/content_scanner
COPY ./core /app/core

RUN mkdir -p /app/storage/scans /app/logs && \
    chown -R scanuser:scanuser /app

USER scanuser

ENV SCANNER_SERVICE_PORT=8030
ENV SCAN_BATCH_SIZE=100
ENV SCAN_INTERVAL=600

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${SCANNER_SERVICE_PORT}/health || exit 1

EXPOSE ${SCANNER_SERVICE_PORT}
CMD ["python3.11", "-m", "content_scanner.main"]

LABEL org.opencontainers.image.title="Ainflue Content Scanner"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="content_scanner"
LABEL ainflue.service.port="8030"