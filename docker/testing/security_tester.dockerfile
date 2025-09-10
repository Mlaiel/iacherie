# Security Tester Service
# Vulnerability and penetration testing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Security Tester - Vulnerability scanning and pen testing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies and security tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq5 \
        libpq-dev \
        pkg-config \
        nmap \
        nikto \
        sqlmap \
        metasploit-framework \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r sectester && useradd -r -g sectester sectester

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-security.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-security.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./testing/security_tester/ ./security_tester/
COPY ./testing/common/ ./common/
COPY ./testing/security_tests/ ./security_tests/

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/scan_results && \
    chown -R sectester:sectester /app

# Switch to non-root user
USER sectester

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=security_tester
ENV LOG_LEVEL=INFO
ENV SECURITY_THRESHOLD=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Expose port
EXPOSE 8003

# Default command
CMD ["python", "-m", "pytest", "security_tests/", "-v", "--junit-xml=reports/security.xml"]