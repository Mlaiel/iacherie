# Performance Monitor Service - Performance metrics monitoring
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements/performance-monitor.txt .
RUN pip install --no-cache-dir -r performance-monitor.txt

FROM base AS production
RUN groupadd -r perfmon && useradd -r -g perfmon perfmon
COPY src/monitoring/performance_monitor/ ./performance_monitor/
RUN chown -R perfmon:perfmon /app
USER perfmon
EXPOSE 8201
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8201/health')" || exit 1
ENV PYTHONPATH=/app PORT=8201
CMD ["python", "-m", "uvicorn", "performance_monitor.main:app", "--host", "0.0.0.0", "--port", "8201"]