# =============================================================================
# AINFLUE DMCA AUTOMATION - AUTOMATED DOCKERFILE
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS dmca-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated DMCA takedown processing service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl wget \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r dmcauser && \
    useradd -r -g dmcauser -d /app dmcauser && \
    mkdir -p /app && chown -R dmcauser:dmcauser /app

FROM dmca-base AS dmca-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        requests aiohttp jinja2 \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        email-validator python-multipart

FROM dmca-deps AS production

WORKDIR /app
COPY ./dmca_automation /app/dmca_automation
COPY ./core /app/core

RUN mkdir -p /app/storage/dmca/{templates,notices,responses} \
             /app/logs && \
    chown -R dmcauser:dmcauser /app

USER dmcauser

ENV DMCA_SERVICE_PORT=8024
ENV NOTICE_TEMPLATE_PATH=/app/storage/dmca/templates
ENV AUTO_SEND_NOTICES=false

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${DMCA_SERVICE_PORT}/health || exit 1

EXPOSE ${DMCA_SERVICE_PORT}
CMD ["python3.11", "-m", "dmca_automation.main"]

LABEL org.opencontainers.image.title="Ainflue DMCA Automation"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="dmca_automation"
LABEL ainflue.service.port="8024"