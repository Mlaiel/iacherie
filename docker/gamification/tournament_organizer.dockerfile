# ===============================================
# Tournament Organizer Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Tournament Management Service
# Handles tournament creation, management, and competitive events
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

RUN groupadd -r tournamentuser && useradd -r -g tournamentuser tournamentuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

FROM python:3.11-slim AS production

COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/tournamentuser/.local

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=tournamentuser:tournamentuser src/gamification/tournament_organizer/ ./
COPY --chown=tournamentuser:tournamentuser config/gamification/ ./config/

USER tournamentuser

ENV PATH="/home/tournamentuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV TOURNAMENT_PORT=8085
ENV TOURNAMENT_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8085/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Tournament Organizer Service for Ainflue Gamification"

EXPOSE 8085
CMD ["python", "-m", "tournament_organizer.main"]