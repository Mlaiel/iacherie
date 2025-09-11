# ML Pipeline Orchestrator Service
# Advanced ML pipeline management and orchestration
# Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer Role

FROM python:3.11-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue ML Pipeline Orchestrator - Advanced ML workflow management"
LABEL version="1.0.0"

# Install system dependencies for ML
RUN apt-get update && apt-get install -y \
    # Core dependencies
    build-essential \
    curl \
    wget \
    git \
    # ML libraries dependencies
    libgomp1 \
    libomp-dev \
    libopenblas-dev \
    liblapack-dev \
    # GPU support (optional)
    ocl-icd-opencl-dev \
    # Audio/Video processing
    ffmpeg \
    libsndfile1-dev \
    # Image processing
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ML requirements
COPY requirements-ml.txt requirements-pipeline.txt ./

# Install Python ML dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    # Core ML libraries
    torch torchvision torchaudio \
    tensorflow \
    scikit-learn \
    pandas \
    numpy \
    # Pipeline orchestration
    mlflow \
    airflow \
    kedro \
    # Model serving
    bentoml \
    # Monitoring
    evidently \
    # Requirements files
    -r requirements-ml.txt \
    -r requirements-pipeline.txt

# Copy ML pipeline source code
COPY ./ml_pipeline/ ./pipeline/
COPY ./ml/common/ ./common/

# Security: Create ML user
RUN groupadd --gid 1000 mlpipeline && \
    useradd --uid 1000 --gid mlpipeline --shell /bin/bash --create-home mlpipeline

# Create ML directories
RUN mkdir -p \
    /app/models \
    /app/datasets \
    /app/experiments \
    /app/artifacts \
    /app/logs \
    /app/cache \
    && chown -R mlpipeline:mlpipeline /app \
    && chmod 755 /app

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to ML user
USER mlpipeline

# ML Pipeline environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=ml_pipeline_orchestrator \
    MLFLOW_TRACKING_URI=http://mlflow:5000 \
    CUDA_VISIBLE_DEVICES=0 \
    OMP_NUM_THREADS=4

# Health check for ML service
HEALTHCHECK --interval=60s --timeout=30s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()" || exit 1

EXPOSE 8000

# Start ML Pipeline Orchestrator
CMD ["python3", "-m", "uvicorn", "pipeline.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-level", "info"]