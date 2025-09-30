# Cost Tracker Service - Cloud cost monitoring and optimization
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements/cost-tracker.txt .
RUN pip install --no-cache-dir -r cost-tracker.txt

FROM base AS production
RUN groupadd -r cost && useradd -r -g cost cost
COPY src/monitoring/cost_tracker/ ./cost_tracker/
RUN mkdir -p /app/reports && chown -R cost:cost /app
USER cost
EXPOSE 8205
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8205/health')" || exit 1
ENV PYTHONPATH=/app PORT=8205 CLOUD_PROVIDER=aws
CMD ["python", "-m", "uvicorn", "cost_tracker.main:app", "--host", "0.0.0.0", "--port", "8205"]