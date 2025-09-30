# =============================================================================
# AINFLUE ENFORCEMENT ENGINE - AUTOMATION DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS enforcement-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Rights enforcement automation service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r enforceuser && \
    useradd -r -g enforceuser -d /app enforceuser && \
    mkdir -p /app && chown -R enforceuser:enforceuser /app

FROM enforcement-base AS enforcement-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        requests aiohttp \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM enforcement-deps AS production

WORKDIR /app
COPY ./enforcement_engine /app/enforcement_engine
COPY ./core /app/core

RUN mkdir -p /app/storage/enforcement /app/logs && \
    chown -R enforceuser:enforceuser /app

USER enforceuser

ENV ENFORCEMENT_SERVICE_PORT=8028
ENV AUTO_ENFORCEMENT=false
ENV ESCALATION_ENABLED=true

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${ENFORCEMENT_SERVICE_PORT}/health || exit 1

EXPOSE ${ENFORCEMENT_SERVICE_PORT}
CMD ["python3.11", "-m", "enforcement_engine.main"]

LABEL org.opencontainers.image.title="Ainflue Enforcement Engine"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="enforcement_engine"
LABEL ainflue.service.port="8028"