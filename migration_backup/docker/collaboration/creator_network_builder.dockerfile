# Creator Network Builder Service
# Network expansion and community building tools
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Creator Network Builder - Community building service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r network && useradd -r -g network network

FROM base AS dependencies
COPY requirements.txt requirements-network.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-network.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/network/ ./network/
COPY ./collaboration/common/ ./common/
RUN mkdir -p /app/network_data /app/logs && chown -R network:network /app
USER network
ENV PYTHONPATH=/app SERVICE_NAME=creator_network_builder
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "network.main:app", "--host", "0.0.0.0", "--port", "8000"]