# ===============================================
# Challenge Engine Dockerfile - Ainflue Platform
# ===============================================
# Multi-stage Docker build for Challenge Management Service
# Handles challenge creation, tracking, and completion logic
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 3.0.0
# Security: Hardened, non-root, minimal attack surface
# ===============================================

# ===== STAGE 1: Dependencies =====
FROM python:3.11-slim AS dependencies

# Security: Create non-root user early
RUN groupadd -r challengeuser && useradd -r -g challengeuser challengeuser

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements/gamification.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

# ===== STAGE 2: Application Build =====
FROM python:3.11-slim AS application

# Security: Copy user from dependencies stage
COPY --from=dependencies /etc/passwd /etc/passwd
COPY --from=dependencies /etc/group /etc/group

# Copy Python packages from dependencies stage
COPY --from=dependencies /root/.local /home/challengeuser/.local

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy application code
COPY --chown=challengeuser:challengeuser src/gamification/challenge_engine/ ./
COPY --chown=challengeuser:challengeuser config/gamification/ ./config/

# Security: Switch to non-root user
USER challengeuser

# Update PATH to include user packages
ENV PATH="/home/challengeuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# ===== STAGE 3: Production =====
FROM application AS production

# Application configuration
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV CHALLENGE_ENGINE_PORT=8080
ENV CHALLENGE_ENGINE_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Performance: Pre-compile Python files
RUN python -m compileall .

# Security: Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8080/health || exit 1

# Resource limits (will be overridden by docker-compose)
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="3.0.0"
LABEL description="Challenge Engine Service for Ainflue Gamification"
LABEL security.scan="trivy,clair"

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "-m", "challenge_engine.main"]