# Skill Analyzer Service
# Advanced skill assessment and compatibility analysis
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Skill Analyzer - AI-powered skill assessment service"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl libpq5 libpq-dev pkg-config \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r skills && useradd -r -g skills skills

FROM base AS dependencies
COPY requirements.txt requirements-skills.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-skills.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/skills/ ./skills/
COPY ./collaboration/common/ ./common/

RUN mkdir -p /app/skill_data /app/logs /app/models && \
    chown -R skills:skills /app

USER skills
ENV PYTHONPATH=/app SERVICE_NAME=skill_analyzer

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "skills.main:app", "--host", "0.0.0.0", "--port", "8000"]