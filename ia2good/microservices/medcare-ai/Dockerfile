# MedCare-AI Microservice Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy shared services requirements and install if exists
COPY ../../shared-services /tmp/shared-services
RUN if [ -f /tmp/shared-services/requirements.txt ]; then \
    pip install --no-cache-dir --user -r /tmp/shared-services/requirements.txt; \
    fi

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 medcare && \
    mkdir -p /app /app/ml_models /app/uploads && \
    chown -R medcare:medcare /app

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/medcare/.local

# Copy application code
COPY --chown=medcare:medcare . .

# Copy shared services into container
RUN cp -r /tmp/shared-services /app/shared_services && \
    chown -R medcare:medcare /app/shared_services

# Switch to non-root user
USER medcare

# Add local bin to PATH
ENV PATH=/home/medcare/.local/bin:$PATH

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/shared_services

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run application (port 8003 for MedCare API)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
