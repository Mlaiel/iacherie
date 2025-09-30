# =============================================================================
# AINFLUE RIGHTS MANAGER - COMPREHENSIVE DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS rights-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Comprehensive rights management service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r rightsuser && \
    useradd -r -g rightsuser -d /app rightsuser && \
    mkdir -p /app && chown -R rightsuser:rightsuser /app

FROM rights-base AS rights-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy alembic \
        cryptography passlib python-jose \
        prometheus-client structlog

FROM rights-deps AS production

WORKDIR /app
COPY ./rights_manager /app/rights_manager
COPY ./core /app/core

RUN mkdir -p /app/storage/rights/{licenses,contracts} \
             /app/logs /app/keys && \
    chown -R rightsuser:rightsuser /app

USER rightsuser

ENV RIGHTS_SERVICE_PORT=8027
ENV LICENSE_VALIDITY_DAYS=365
ENV ENCRYPTION_ENABLED=true

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${RIGHTS_SERVICE_PORT}/health || exit 1

EXPOSE ${RIGHTS_SERVICE_PORT}
CMD ["python3.11", "-m", "rights_manager.main"]

LABEL org.opencontainers.image.title="Ainflue Rights Manager"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="rights_manager"
LABEL ainflue.service.port="8027"