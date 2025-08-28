# =============================================================================
# AINFLUE ANALYTICS SERVICE - OPTIMIZED PRODUCTION DOCKERFILE
# =============================================================================
# Specialized container for high-performance data analytics, reporting,
# and business intelligence with enterprise security features.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG DEBIAN_VERSION=slim
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: BASE WITH ANALYTICS DEPENDENCIES
# =============================================================================
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS analytics-base

LABEL stage=analytics-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Analytics service base with data processing capabilities"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for analytics
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Build essentials (removed later)
        build-essential \
        pkg-config \
        # Database connectivity
        libpq5 \
        libpq-dev \
        # SSL and security
        ca-certificates \
        libssl-dev \
        libffi-dev \
        # Data processing libraries
        libhdf5-dev \
        libnetcdf-dev \
        libopenblas-dev \
        liblapack-dev \
        libatlas-base-dev \
        # Graphics and visualization
        libfreetype6-dev \
        libpng-dev \
        libjpeg-dev \
        # Network tools
        curl \
        wget \
        netcat-openbsd \
        # Clean up
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean \
        && apt-get autoremove -y

# Security: Create non-root user
RUN groupadd --gid 10001 analytics && \
    useradd --uid 10001 --gid analytics \
            --home-dir /home/analytics \
            --create-home \
            --shell /bin/bash \
            analytics

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM analytics-base AS analytics-dependencies

LABEL stage=analytics-dependencies
LABEL description="Analytics-specific Python dependencies"

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade \
    pip==23.3.1 \
    setuptools==68.2.2 \
    wheel==0.41.2

# Copy requirements
WORKDIR /build
COPY requirements.txt ./
COPY requirements-analytics.txt ./

# Install analytics-specific dependencies
RUN pip install --no-cache-dir \
    # Data processing and analysis
    pandas==2.1.1 \
    numpy==1.24.3 \
    scipy==1.11.3 \
    scikit-learn==1.3.0 \
    # Database connectivity
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.7 \
    pymongo==4.5.0 \
    redis==5.0.1 \
    # Time series analysis
    statsmodels==0.14.0 \
    prophet==1.1.4 \
    # Visualization
    matplotlib==3.7.2 \
    seaborn==0.12.2 \
    plotly==5.17.0 \
    bokeh==3.2.2 \
    # High-performance computing
    numba==0.58.1 \
    dask==2023.10.1 \
    vaex==4.17.0 \
    # Business intelligence
    openpyxl==3.1.2 \
    xlsxwriter==3.1.9 \
    # Machine learning for analytics
    xgboost==2.0.0 \
    lightgbm==4.1.0 \
    # API framework
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    # Async processing
    celery==5.3.4 \
    aiofiles==23.2.1

# Install main requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install analytics-specific requirements if they exist
RUN if [ -f requirements-analytics.txt ]; then \
        pip install --no-cache-dir -r requirements-analytics.txt; \
    fi

# Clean up pip cache
RUN pip cache purge

# =============================================================================
# STAGE 3: PRODUCTION
# =============================================================================
FROM analytics-base AS production

LABEL stage=production
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Analytics Service - Production Runtime"
LABEL service="analytics-service"
LABEL capabilities="data-analysis,reporting,business-intelligence"

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Analytics service specific
    ANALYTICS_SERVICE=true \
    SERVICE_PORT=8003 \
    # Performance settings
    ANALYTICS_WORKERS=4 \
    ANALYTICS_BATCH_SIZE=1000 \
    MAX_MEMORY_USAGE=4GB \
    # Processing settings
    ENABLE_PARALLEL_PROCESSING=true \
    MAX_CONCURRENT_REPORTS=10 \
    REPORT_CACHE_TTL=3600 \
    # Data settings
    DATA_RETENTION_DAYS=90 \
    ENABLE_DATA_COMPRESSION=true

# Remove build dependencies, keep runtime
RUN apt-get remove -y \
        build-essential \
        pkg-config \
        libpq-dev \
        libhdf5-dev \
        libnetcdf-dev \
        libfreetype6-dev \
        libpng-dev \
        libjpeg-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from dependencies stage
COPY --from=analytics-dependencies /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=analytics:analytics . .

# Create analytics directories with proper permissions
RUN mkdir -p \
        /app/reports \
        /app/reports/generated \
        /app/reports/templates \
        /app/data \
        /app/data/cache \
        /app/data/processed \
        /app/logs \
        /app/temp \
        /app/exports \
    && chown -R analytics:analytics /app \
    && chmod -R 755 /app \
    && chmod -R 777 /app/reports /app/data /app/logs /app/temp /app/exports

# Create analytics service startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Analytics Service Starting ==="\n\
echo "Service Port: ${SERVICE_PORT}"\n\
echo "Workers: ${ANALYTICS_WORKERS}"\n\
echo "Batch Size: ${ANALYTICS_BATCH_SIZE}"\n\
echo "Max Memory: ${MAX_MEMORY_USAGE}"\n\
echo "Parallel Processing: ${ENABLE_PARALLEL_PROCESSING}"\n\
echo "==================================="\n\
\n\
# Validate data processing capabilities\n\
echo "Validating analytics capabilities..."\n\
python -c "\n\
import pandas as pd\n\
import numpy as np\n\
import matplotlib\n\
matplotlib.use(\"Agg\")  # Use non-interactive backend\n\
import matplotlib.pyplot as plt\n\
print(\"Data processing libraries loaded successfully\")\n\
"\n\
\n\
# Check database connectivity\n\
python -c "\n\
try:\n\
    import psycopg2\n\
    import pymongo\n\
    import redis\n\
    print(\"Database connectors available\")\n\
except ImportError as e:\n\
    print(f\"Database connector warning: {e}\")\n\
"\n\
\n\
# Start analytics service\n\
exec python -m uvicorn analytics.service:app \\\n\
    --host 0.0.0.0 \\\n\
    --port ${SERVICE_PORT} \\\n\
    --workers 1 \\\n\
    --worker-class uvicorn.workers.UvicornWorker \\\n\
    --log-level info \\\n\
    --access-log\n\
' > /app/start-analytics.sh && chmod +x /app/start-analytics.sh

# Switch to non-root user
USER analytics

# Expose service port
EXPOSE 8003

# Health check with analytics validation
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=60s \
            --retries=3 \
            CMD curl -f http://localhost:8003/health \
                && python -c "
import psutil
import sys

# Check memory usage
memory_percent = psutil.virtual_memory().percent
print(f'Memory usage: {memory_percent}%')

# Check CPU usage
cpu_percent = psutil.cpu_percent(interval=1)
print(f'CPU usage: {cpu_percent}%')

# Exit with error if resource usage is too high
if memory_percent > 90 or cpu_percent > 95:
    sys.exit(1)
sys.exit(0)
" || exit 1

# Start analytics service
CMD ["/app/start-analytics.sh"]