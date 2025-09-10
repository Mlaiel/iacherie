# Project Templates Service
# Pre-built project templates and scaffolding
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Project Templates - Project scaffolding service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config git \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r templates && useradd -r -g templates templates

FROM base AS dependencies
COPY requirements.txt requirements-templates.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-templates.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/templates/ ./templates/
COPY ./collaboration/common/ ./common/
RUN mkdir -p /app/generated_projects /app/logs && chown -R templates:templates /app
USER templates
ENV PYTHONPATH=/app SERVICE_NAME=project_templates
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "templates.main:app", "--host", "0.0.0.0", "--port", "8000"]