# Dockerfile for IA2GOOD Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including GEOS for Shapely/PostGIS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    libgeos-dev \
    libgeos-c1v5 \
    libgeos++-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    libmagic1 \
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
EXPOSE 8001

# Run the application (port 8001 for Guardian API)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
