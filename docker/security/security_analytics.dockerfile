# Security Analytics Service - Advanced security analytics and reporting
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements/security-analytics.txt .
RUN pip install --no-cache-dir -r security-analytics.txt

FROM base AS production
RUN groupadd -r secanalytics && useradd -r -g secanalytics secanalytics
COPY src/security/security_analytics/ ./security_analytics/
COPY src/security/common/ ./common/
RUN mkdir -p /app/models /app/reports && chown -R secanalytics:secanalytics /app
USER secanalytics
EXPOSE 8109
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8109/health')" || exit 1
ENV PYTHONPATH=/app PORT=8109 ENABLE_ML_ANALYTICS=true
CMD ["python", "-m", "uvicorn", "security_analytics.main:app", "--host", "0.0.0.0", "--port", "8109"]