# =============================================================================
# AINFLUE ROYALTY CALCULATOR - AUTOMATED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS royalty-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated royalty calculations and distributions"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r royaltyuser && \
    useradd -r -g royaltyuser -d /app royaltyuser && \
    mkdir -p /app && chown -R royaltyuser:royaltyuser /app

FROM royalty-base AS royalty-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas decimal \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        openpyxl xlsxwriter

FROM royalty-deps AS production

WORKDIR /app
COPY ./royalty_calculator /app/royalty_calculator
COPY ./core /app/core

RUN mkdir -p /app/storage/royalties/{calculations,reports} \
             /app/logs && \
    chown -R royaltyuser:royaltyuser /app

USER royaltyuser

ENV ROYALTY_SERVICE_PORT=8043
ENV CALCULATION_SCHEDULE=daily
ENV DEFAULT_ROYALTY_RATE=0.15

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${ROYALTY_SERVICE_PORT}/health || exit 1

EXPOSE ${ROYALTY_SERVICE_PORT}
CMD ["python3.11", "-m", "royalty_calculator.main"]

LABEL org.opencontainers.image.title="Ainflue Royalty Calculator"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="royalty_calculator"
LABEL ainflue.service.port="8043"