# =============================================================================
# AINFLUE PAYOUT SCHEDULER - AUTOMATED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS payout-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated payout scheduling and management"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r payoutuser && \
    useradd -r -g payoutuser -d /app payoutuser && \
    mkdir -p /app && chown -R payoutuser:payoutuser /app

FROM payout-base AS payout-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas stripe paypalrestsdk \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        schedule apscheduler

FROM payout-deps AS production

WORKDIR /app
COPY ./payout_scheduler /app/payout_scheduler
COPY ./core /app/core

RUN mkdir -p /app/storage/payouts /app/logs && \
    chown -R payoutuser:payoutuser /app

USER payoutuser

ENV PAYOUT_SERVICE_PORT=8046
ENV PAYOUT_SCHEDULE=weekly
ENV MIN_PAYOUT_AMOUNT=50

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PAYOUT_SERVICE_PORT}/health || exit 1

EXPOSE ${PAYOUT_SERVICE_PORT}
CMD ["python3.11", "-m", "payout_scheduler.main"]

LABEL org.opencontainers.image.title="Ainflue Payout Scheduler"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="payout_scheduler"
LABEL ainflue.service.port="8046"