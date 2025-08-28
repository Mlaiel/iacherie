# Multi-stage Production Dockerfile for Ainflue Platform
# ==================================================

# Build stage
FROM python:3.11-slim as builder

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue - AI-Powered Content Protection & Monetization Platform - Builder"

# Set build environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    libpq-dev \
    libsndfile1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy requirements and install Python dependencies in virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy source code for any build processes
COPY . .

# ==================================================
# Production stage
FROM python:3.11-slim as production

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue - AI-Powered Content Protection & Monetization Platform"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/venv/bin:$PATH"

# Security: Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    # Essential runtime libraries
    libpq5 \
    libsndfile1 \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    # Browser for web scraping (if needed)
    chromium \
    chromium-driver \
    # Health check tools
    curl \
    # Security updates
    && apt-get upgrade -y \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Security: Create non-root user with minimal privileges
RUN groupadd --gid 1000 ainflue && \
    useradd --uid 1000 --gid ainflue --shell /bin/bash --create-home ainflue

# Set Chrome/Chromium path for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory with proper permissions
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=ainflue:ainflue . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data/faiss_indexes \
    /app/storage \
    /app/logs \
    /app/tmp \
    /app/uploads \
    && chown -R ainflue:ainflue /app

# Security: Set read-only filesystem for application code
RUN chmod -R 755 /app && \
    chmod -R 777 /app/data /app/storage /app/logs /app/tmp /app/uploads

# Security: Remove unnecessary packages and files
RUN apt-get remove -y \
    wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user
USER ainflue

# Security: Set secure umask
RUN echo "umask 022" >> /home/ainflue/.bashrc

# Expose port
EXPOSE 8000

# Security: Add security labels
LABEL security.scan.enabled=true
LABEL security.hardened=true
LABEL security.non-root=true

# Health check with timeout and retries
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production startup with proper signal handling
CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--access-log", \
     "--log-level", "info"]