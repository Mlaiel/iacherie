# Revenue Sharing Calculator Service
# Automated revenue distribution calculations
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Revenue Sharing Calculator - Automated revenue distribution"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r revenue && useradd -r -g revenue revenue

FROM base AS dependencies
COPY requirements.txt requirements-revenue.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-revenue.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/revenue/ ./revenue/
COPY ./collaboration/common/ ./common/
RUN mkdir -p /app/revenue_data /app/logs && chown -R revenue:revenue /app
USER revenue
ENV PYTHONPATH=/app SERVICE_NAME=revenue_sharing_calculator
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "revenue.main:app", "--host", "0.0.0.0", "--port", "8000"]