# =============================================================================
# AINFLUE LICENSING ENGINE - AUTOMATED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS licensing-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated licensing and rights monetization"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r licenseuser && \
    useradd -r -g licenseuser -d /app licenseuser && \
    mkdir -p /app && chown -R licenseuser:licenseuser /app

FROM licensing-base AS licensing-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        jinja2 python-multipart

FROM licensing-deps AS production

WORKDIR /app
COPY ./licensing_engine /app/licensing_engine
COPY ./core /app/core

RUN mkdir -p /app/storage/licensing/{contracts,templates} \
             /app/logs && \
    chown -R licenseuser:licenseuser /app

USER licenseuser

ENV LICENSING_SERVICE_PORT=8045
ENV AUTO_APPROVE_THRESHOLD=1000
ENV LICENSE_TERM_YEARS=5

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${LICENSING_SERVICE_PORT}/health || exit 1

EXPOSE ${LICENSING_SERVICE_PORT}
CMD ["python3.11", "-m", "licensing_engine.main"]

LABEL org.opencontainers.image.title="Ainflue Licensing Engine"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="licensing_engine"
LABEL ainflue.service.port="8045"