# ===============================================
# Leaderboard Manager Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Leaderboard Management Service
# Handles ranking calculations, leaderboard updates, and competitive features
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

FROM python:3.11-slim AS dependencies

# Security: Create non-root user
RUN groupadd -r leaderboarduser && useradd -r -g leaderboarduser leaderboarduser

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

# ===== Production Stage =====
FROM python:3.11-slim AS production

# Copy user and packages
COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/leaderboarduser/.local

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /app
COPY --chown=leaderboarduser:leaderboarduser src/gamification/leaderboard_manager/ ./
COPY --chown=leaderboarduser:leaderboarduser config/gamification/ ./config/

# Security: Non-root user
USER leaderboarduser

# Environment
ENV PATH="/home/leaderboarduser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV LEADERBOARD_PORT=8082
ENV LEADERBOARD_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8082/health || exit 1

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Leaderboard Manager Service for Ainflue Gamification"

EXPOSE 8082
CMD ["python", "-m", "leaderboard_manager.main"]