# ===============================================
# Level Progression Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Level Progression Service
# Handles experience tracking, level advancement, and progression rewards
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r leveluser && useradd -r -g leveluser leveluser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/leveluser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=leveluser:leveluser src/gamification/level_progression/ ./
COPY --chown=leveluser:leveluser config/gamification/ ./config/

USER leveluser

ENV PATH="/home/leveluser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV LEVEL_PORT=8090
ENV LEVEL_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8090/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Level Progression Service for Ainflue Gamification"

EXPOSE 8090
CMD ["python", "-m", "level_progression.main"]