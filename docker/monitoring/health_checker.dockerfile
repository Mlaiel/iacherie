# Health Checker Service - Service health monitoring
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements/health-checker.txt .
RUN pip install --no-cache-dir -r health-checker.txt

FROM base AS production
RUN groupadd -r health && useradd -r -g health health
COPY src/monitoring/health_checker/ ./health_checker/
RUN chown -R health:health /app
USER health
EXPOSE 8200
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8200/health')" || exit 1
ENV PYTHONPATH=/app PORT=8200
CMD ["python", "-m", "uvicorn", "health_checker.main:app", "--host", "0.0.0.0", "--port", "8200"]