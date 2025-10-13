# Anomaly Detector Service - ML-based anomaly detection
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/anomaly-detector.txt .
RUN pip install --no-cache-dir -r anomaly-detector.txt

FROM base AS production
RUN groupadd -r anomaly && useradd -r -g anomaly anomaly
COPY src/monitoring/anomaly_detector/ ./anomaly_detector/
RUN mkdir -p /app/models /app/reports && chown -R anomaly:anomaly /app
USER anomaly
EXPOSE 8203
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8203/health')" || exit 1
ENV PYTHONPATH=/app PORT=8203 SENSITIVITY_THRESHOLD=0.8
CMD ["python", "-m", "uvicorn", "anomaly_detector.main:app", "--host", "0.0.0.0", "--port", "8203"]