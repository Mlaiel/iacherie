# ===============================================
# Engagement Optimizer Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Engagement Optimization Service
# Handles engagement analysis, optimization recommendations, and user retention
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r engagementuser && useradd -r -g engagementuser engagementuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/engagementuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=engagementuser:engagementuser src/gamification/engagement_optimizer/ ./
COPY --chown=engagementuser:engagementuser config/gamification/ ./config/

USER engagementuser

ENV PATH="/home/engagementuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV ENGAGEMENT_PORT=8087
ENV ENGAGEMENT_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8087/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Engagement Optimizer Service for Ainflue Gamification"

EXPOSE 8087
CMD ["python", "-m", "engagement_optimizer.main"]