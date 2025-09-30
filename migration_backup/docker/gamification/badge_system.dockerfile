# ===============================================
# Badge System Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Badge Management Service
# Handles badge creation, awarding, and verification systems
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r badgeuser && useradd -r -g badgeuser badgeuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/badgeuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=badgeuser:badgeuser src/gamification/badge_system/ ./
COPY --chown=badgeuser:badgeuser config/gamification/ ./config/

USER badgeuser

ENV PATH="/home/badgeuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV BADGE_PORT=8086
ENV BADGE_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8086/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Badge System Service for Ainflue Gamification"

EXPOSE 8086
CMD ["python", "-m", "badge_system.main"]