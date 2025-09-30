# Communication Hub Service
# Centralized communication and messaging services
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Communication Hub - Real-time messaging service"
LABEL version="1.0.0"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl libpq5 libpq-dev pkg-config \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r comms && useradd -r -g comms comms

FROM base AS dependencies
COPY requirements.txt requirements-communications.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-communications.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY ./collaboration/communications/ ./communications/
COPY ./collaboration/common/ ./common/

RUN mkdir -p /app/messages /app/logs && \
    chown -R comms:comms /app

USER comms

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=communication_hub

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000 8001

CMD ["uvicorn", "communications.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]