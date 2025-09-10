# Capacity Planner Service - ML-based capacity planning
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/capacity-planner.txt .
RUN pip install --no-cache-dir -r capacity-planner.txt

FROM base AS production
RUN groupadd -r capacity && useradd -r -g capacity capacity
COPY src/monitoring/capacity_planner/ ./capacity_planner/
RUN mkdir -p /app/models /app/reports && chown -R capacity:capacity /app
USER capacity
EXPOSE 8202
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8202/health')" || exit 1
ENV PYTHONPATH=/app PORT=8202
CMD ["python", "-m", "uvicorn", "capacity_planner.main:app", "--host", "0.0.0.0", "--port", "8202"]