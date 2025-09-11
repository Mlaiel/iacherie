# Security Hardening Service
# Enterprise-grade security scanner and hardening automation
# Author: Fahed Mlaiel (mlaiel@live.de) - Security Specialist Role

FROM alpine:3.19 AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Security Hardening - Enterprise security automation"
LABEL version="1.0.0"
LABEL security.scan.enabled=true

# Security: Install only essential packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    wget \
    openssl \
    ca-certificates \
    bash \
    jq \
    && rm -rf /var/cache/apk/*

# Security: Create dedicated user with minimal privileges
RUN addgroup -g 1000 security && \
    adduser -D -u 1000 -G security -s /bin/bash security

WORKDIR /app

# Install security tools and dependencies
COPY requirements-security.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements-security.txt

# Copy security hardening scripts
COPY ./security/hardening/ ./hardening/
COPY ./security/common/ ./common/

# Create security directories with proper permissions
RUN mkdir -p /app/scans /app/reports /app/configs /app/logs && \
    chown -R security:security /app && \
    chmod 755 /app && \
    chmod 700 /app/scans /app/reports

# Security: Remove unnecessary packages and files
RUN apk del wget && \
    rm -rf /var/cache/apk/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to non-root user
USER security

# Security environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=security_hardening \
    SECURITY_LEVEL=enterprise \
    SCAN_INTERVAL=3600

# Health check with security validation
HEALTHCHECK --interval=60s --timeout=30s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/security/health').raise_for_status()" || exit 1

EXPOSE 8000

# Start security hardening service
CMD ["python3", "-m", "uvicorn", "hardening.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-level", "info"]