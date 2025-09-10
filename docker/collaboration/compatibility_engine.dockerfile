# Compatibility Engine Service
# Multi-dimensional compatibility scoring for collaborations
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Compatibility Engine - Advanced compatibility analysis"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl libpq5 libpq-dev pkg-config \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r compat && useradd -r -g compat compat

FROM base AS dependencies
COPY requirements.txt requirements-compatibility.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-compatibility.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/compatibility/ ./compatibility/
COPY ./collaboration/common/ ./common/

RUN mkdir -p /app/logs /app/models && \
    chown -R compat:compat /app

USER compat
ENV PYTHONPATH=/app SERVICE_NAME=compatibility_engine

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "compatibility.main:app", "--host", "0.0.0.0", "--port", "8000"]