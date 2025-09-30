# Partnership Optimizer Service
# Partnership recommendation and optimization engine
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Partnership Optimizer - Partnership optimization service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r partners && useradd -r -g partners partners

FROM base AS dependencies
COPY requirements.txt requirements-partnerships.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-partnerships.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/partnerships/ ./partnerships/
COPY ./collaboration/common/ ./common/
RUN mkdir -p /app/logs && chown -R partners:partners /app
USER partners
ENV PYTHONPATH=/app SERVICE_NAME=partnership_optimizer
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "partnerships.main:app", "--host", "0.0.0.0", "--port", "8000"]