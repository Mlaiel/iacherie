# Fraud Detector Service - ML-based fraud detection and prevention
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements/fraud-detector.txt .
RUN pip install --no-cache-dir -r fraud-detector.txt

FROM base AS production
RUN groupadd -r fraud && useradd -r -g fraud fraud
COPY src/security/fraud_detector/ ./fraud_detector/
COPY src/security/common/ ./common/
RUN mkdir -p /app/models /app/reports && chown -R fraud:fraud /app
USER fraud
EXPOSE 8106
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8106/health')" || exit 1
ENV PYTHONPATH=/app PORT=8106 RISK_THRESHOLD=0.7
CMD ["python", "-m", "uvicorn", "fraud_detector.main:app", "--host", "0.0.0.0", "--port", "8106"]