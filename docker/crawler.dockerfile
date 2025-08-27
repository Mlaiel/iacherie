# Crawler Service Dockerfile
# Specialized container for web crawling and content monitoring

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with crawler-specific packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
    selenium==4.15.0 \
    scrapy==2.11.0 \
    beautifulsoup4==4.12.2 \
    undetected-chromedriver==3.5.3

# Copy application code
COPY . .

# Create crawler data directory
RUN mkdir -p /app/crawled_data

# Set environment variables
ENV PYTHONPATH=/app
ENV CRAWLER_SERVICE=true

# Expose port for crawler management API
EXPOSE 8001

# Run crawler service
CMD ["python", "-m", "crawlers.crawler_manager"]