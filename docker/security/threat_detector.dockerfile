# Threat Detector Service - Advanced threat detection and ML-based analysis
# Uses machine learning models for behavioral analysis and threat identification
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for ML and security analysis
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/threat-detector.txt .
RUN pip install --no-cache-dir -r threat-detector.txt

FROM base AS production

# Create non-root user
RUN groupadd -r threat && useradd -r -g threat threat

# Copy application code
COPY src/security/threat_detector/ ./threat_detector/
COPY src/security/common/ ./common/
COPY src/security/config/ ./config/

# Create directories
RUN mkdir -p /app/models /app/logs /app/cache /var/log/threat
RUN chown -R threat:threat /app /var/log/threat

USER threat

EXPOSE 8101

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8101/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8101
ENV ENABLE_BEHAVIORAL_ANALYSIS=true

# Run with increased memory for ML models
CMD ["python", "-m", "uvicorn", "threat_detector.main:app", "--host", "0.0.0.0", "--port", "8101", "--workers", "2"]