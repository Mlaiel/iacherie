# ===============================================
# Achievement Tracker Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Achievement Tracking Service
# Handles achievement unlocking, progress tracking, and milestone detection
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r achievementuser && useradd -r -g achievementuser achievementuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/achievementuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=achievementuser:achievementuser src/gamification/achievement_tracker/ ./
COPY --chown=achievementuser:achievementuser config/gamification/ ./config/

USER achievementuser

ENV PATH="/home/achievementuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV ACHIEVEMENT_PORT=8083
ENV ACHIEVEMENT_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8083/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Achievement Tracker Service for Ainflue Gamification"

EXPOSE 8083
CMD ["python", "-m", "achievement_tracker.main"]