# =============================================================================
# AINFLUE DRM CONTROLLER - DIGITAL RIGHTS DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS drm-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Digital Rights Management controller"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r drmuser && \
    useradd -r -g drmuser -d /app drmuser && \
    mkdir -p /app && chown -R drmuser:drmuser /app

FROM drm-base AS drm-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        cryptography pycryptodome \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM drm-deps AS production

WORKDIR /app
COPY ./drm_controller /app/drm_controller
COPY ./core /app/core

RUN mkdir -p /app/storage/drm /app/logs /app/keys && \
    chmod 700 /app/keys && \
    chown -R drmuser:drmuser /app

USER drmuser

ENV DRM_SERVICE_PORT=8029
ENV ENCRYPTION_ALGORITHM=AES-256
ENV KEY_ROTATION_HOURS=24

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${DRM_SERVICE_PORT}/health || exit 1

EXPOSE ${DRM_SERVICE_PORT}
CMD ["python3.11", "-m", "drm_controller.main"]

LABEL org.opencontainers.image.title="Ainflue DRM Controller"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="drm_controller"
LABEL ainflue.service.port="8029"