# Blogger Tools Service - Content writing and blogging tools
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/blogger-tools.txt .
RUN pip install --no-cache-dir -r blogger-tools.txt

FROM base AS production
RUN groupadd -r blogger && useradd -r -g blogger blogger
COPY src/creator_services/blogger_tools/ ./blogger_tools/
RUN mkdir -p /app/models /app/drafts /app/analytics && chown -R blogger:blogger /app
USER blogger
EXPOSE 8302
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8302/health || exit 1
ENV PYTHONPATH=/app PORT=8302
CMD ["python", "-m", "uvicorn", "blogger_tools.main:app", "--host", "0.0.0.0", "--port", "8302"]