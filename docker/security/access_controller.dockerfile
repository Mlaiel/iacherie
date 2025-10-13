# Access Controller Service - RBAC, MFA, and authentication management
# Manages user authentication, authorization, and access control
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/access-controller.txt .
RUN pip install --no-cache-dir -r access-controller.txt

FROM base AS production

# Create non-root user
RUN groupadd -r access && useradd -r -g access access

# Copy application code
COPY src/security/access_controller/ ./access_controller/
COPY src/security/common/ ./common/
COPY src/security/config/ ./config/

# Create directories
RUN mkdir -p /app/sessions /app/tokens /var/log/access
RUN chown -R access:access /app /var/log/access

USER access

EXPOSE 8102

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8102/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8102
ENV MFA_PROVIDER=totp
ENV SESSION_TIMEOUT=3600

CMD ["python", "-m", "uvicorn", "access_controller.main:app", "--host", "0.0.0.0", "--port", "8102", "--workers", "3"]