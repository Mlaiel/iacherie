# ===============================================
# Reward System Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Reward Calculation Service
# Handles point calculation, bonus multipliers, and reward distribution
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

# ===== STAGE 1: Dependencies =====
FROM python:3.11-slim AS dependencies

# Security: Create non-root user
RUN groupadd -r rewarduser && useradd -r -g rewarduser rewarduser

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

# ===== STAGE 2: Production =====
FROM python:3.11-slim AS production

# Security: Copy user configuration
COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group
COPY --from=dependencies /root/.local /home/rewarduser/.local

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /app
COPY --chown=rewarduser:rewarduser src/gamification/reward_system/ ./
COPY --chown=rewarduser:rewarduser config/gamification/ ./config/

# Security: Switch to non-root user
USER rewarduser

# Environment configuration
ENV PATH="/home/rewarduser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV REWARD_SYSTEM_PORT=8081
ENV REWARD_SYSTEM_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8081/health || exit 1

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="3.0.0"
LABEL description="Reward System Service for Ainflue Gamification"

# Expose port
EXPOSE 8081

# Start service
CMD ["python", "-m", "reward_system.main"]