FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared services requirements and install if exists
COPY ../../shared-services /tmp/shared-services
RUN if [ -f /tmp/shared-services/requirements.txt ]; then \
    pip install --no-cache-dir -r /tmp/shared-services/requirements.txt; \
    fi

# Copy application code
COPY . .

# Copy shared services into container
RUN cp -r /tmp/shared-services /app/shared_services

# Set PYTHONPATH to include the app directory and shared services
ENV PYTHONPATH=/app:/app/shared_services

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
