# ML Inference Engine Service
# High-performance ML model inference and prediction service
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue ML Inference Engine - High-performance ML inference service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    libgomp1 libomp-dev && rm -rf /var/lib/apt/lists/*
RUN groupadd -r mlinfer && useradd -r -g mlinfer mlinfer

FROM base AS dependencies
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-ml.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/inference/ ./inference/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/inference_data /app/logs && chown -R mlinfer:mlinfer /app
USER mlinfer
ENV PYTHONPATH=/app SERVICE_NAME=ml_inference_engine CUDA_VISIBLE_DEVICES=0
HEALTHCHECK --interval=30s --timeout=15s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "inference.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]