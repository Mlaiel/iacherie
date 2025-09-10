# ===============================================
# Community Builder Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Community Building Service
# Handles community creation, management, and social network features
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r communityuser && useradd -r -g communityuser communityuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/communityuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=communityuser:communityuser src/gamification/community_builder/ ./
COPY --chown=communityuser:communityuser config/gamification/ ./config/

USER communityuser

ENV PATH="/home/communityuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV COMMUNITY_PORT=8088
ENV COMMUNITY_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8088/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Community Builder Service for Ainflue Gamification"

EXPOSE 8088
CMD ["python", "-m", "community_builder.main"]