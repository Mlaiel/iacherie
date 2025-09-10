# ===============================================
# Point Calculator Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Point Calculation Service
# Handles complex point calculations, bonuses, and scoring algorithms
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r pointuser && useradd -r -g pointuser pointuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/pointuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=pointuser:pointuser src/gamification/point_calculator/ ./
COPY --chown=pointuser:pointuser config/gamification/ ./config/

USER pointuser

ENV PATH="/home/pointuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV POINT_PORT=8089
ENV POINT_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8089/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Point Calculator Service for Ainflue Gamification"

EXPOSE 8089
CMD ["python", "-m", "point_calculator.main"]