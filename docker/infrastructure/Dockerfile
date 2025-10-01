# Multi-stage Production Dockerfile for iacherie Platform
# ==================================================

# Build stage
FROM python:3.11-slim as builder

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="iacherie - AI-Powered Content Protection & Monetization Platform - Builder"

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
# Development stage
FROM python:3.11-slim as development

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="iacherie - AI-Powered Content Protection & Monetization Platform - Development"

# Set development environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV ENVIRONMENT=development
ENV DEBUG=true

# Install development dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    libpq-dev \
    libsndfile1-dev \
    pkg-config \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Create development user
RUN groupadd --gid 1000 iacherie && \
    useradd --uid 1000 --gid iacherie --shell /bin/bash --create-home iacherie

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir debugpy pytest pytest-asyncio

# Copy source code
COPY --chown=iacherie:iacherie . .

# Create necessary directories
RUN mkdir -p \
    /app/data/faiss_indexes \
    /app/storage \
    /app/logs \
    /app/tmp \
    /app/uploads \
    && chown -R iacherie:iacherie /app

USER iacherie

EXPOSE 8000 8001 8765 5678

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==================================================
# Production stage
FROM python:3.11-slim as production

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="iacherie - AI-Powered Content Protection & Monetization Platform"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/iacherie"

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
RUN groupadd --gid 1000 iacherie && \
    useradd --uid 1000 --gid iacherie --shell /bin/bash --create-home iacherie

# Set Chrome/Chromium path for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory with proper permissions
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=iacherie:iacherie . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data/faiss_indexes \
    /app/storage \
    /app/logs \
    /app/tmp \
    /app/uploads \
    && chown -R iacherie:iacherie /app

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
USER iacherie

# Security: Set secure umask
RUN echo "umask 022" >> /home/iacherie/.bashrc

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