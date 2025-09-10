# Comedian Tools Service - Comedy performance and audience analysis tools
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/comedian-tools.txt .
RUN pip install --no-cache-dir -r comedian-tools.txt

FROM base AS production
RUN groupadd -r comedian && useradd -r -g comedian comedian
COPY src/creator_services/comedian_tools/ ./comedian_tools/
RUN mkdir -p /app/models /app/performances /app/feedback && chown -R comedian:comedian /app
USER comedian
EXPOSE 8304
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8304/health || exit 1
ENV PYTHONPATH=/app PORT=8304
CMD ["python", "-m", "uvicorn", "comedian_tools.main:app", "--host", "0.0.0.0", "--port", "8304"]