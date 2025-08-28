# =============================================================================
# AINFLUE CRAWLER SERVICE - OPTIMIZED PRODUCTION DOCKERFILE
# =============================================================================
# Specialized container for enterprise web crawling with browser automation,
# anti-bot detection evasion, and high-performance content monitoring.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG DEBIAN_VERSION=slim
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: BASE WITH BROWSER SUPPORT
# =============================================================================
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS crawler-base

LABEL stage=crawler-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Crawler service base with browser automation support"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for web crawling
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Browser automation
        chromium \
        chromium-driver \
        firefox-esr \
        # Network tools
        wget \
        curl \
        netcat-openbsd \
        # Development tools (removed in production)
        build-essential \
        pkg-config \
        # SSL and security
        ca-certificates \
        gnupg \
        # System libraries
        libpq5 \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        # Media processing for content analysis
        ffmpeg \
        libsndfile1 \
        # X11 and display (for headless browsers)
        xvfb \
        x11vnc \
        fluxbox \
        # Font support for better rendering
        fonts-liberation \
        fonts-dejavu-core \
        # Proxy and networking
        tor \
        proxychains4 \
        # Clean up
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean \
        && apt-get autoremove -y

# Security: Create non-root user for crawler
RUN groupadd --gid 10001 crawler && \
    useradd --uid 10001 --gid crawler \
            --home-dir /home/crawler \
            --create-home \
            --shell /bin/bash \
            crawler

# Browser configuration
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    FIREFOX_BIN=/usr/bin/firefox \
    DISPLAY=:99

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM crawler-base AS crawler-dependencies

LABEL stage=crawler-dependencies
LABEL description="Crawler-specific Python dependencies"

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
COPY requirements-crawler.txt ./

# Install crawler-specific dependencies
RUN pip install --no-cache-dir \
    # Web scraping frameworks
    scrapy==2.11.0 \
    scrapy-playwright==0.0.27 \
    scrapy-splash==0.8.0 \
    # Browser automation
    selenium==4.15.0 \
    undetected-chromedriver==3.5.4 \
    playwright==1.40.0 \
    # HTTP clients and parsing
    requests==2.31.0 \
    httpx==0.25.0 \
    aiohttp==3.9.0 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3 \
    # Anti-bot detection evasion
    fake-useragent==1.4.0 \
    user-agent==0.1.10 \
    requests-html==0.10.0 \
    # Proxy and rotation
    rotating-proxies==0.6.2 \
    proxy-randomizer==0.3.0 \
    # Social media APIs
    tweepy==4.14.0 \
    python-instagram==1.3.2 \
    youtube-dl==2021.12.17 \
    yt-dlp==2023.10.13 \
    # Content processing
    python-magic==0.4.27 \
    pillow==10.0.1 \
    # Data handling
    pandas==2.1.1 \
    numpy==1.24.3 \
    # Async and concurrency
    asyncio-throttle==1.0.2 \
    aiofiles==23.2.1 \
    # API framework
    fastapi==0.104.1 \
    uvicorn==0.24.0

# Install main requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install crawler-specific requirements if they exist
RUN if [ -f requirements-crawler.txt ]; then \
        pip install --no-cache-dir -r requirements-crawler.txt; \
    fi

# Install Playwright browsers
RUN playwright install chromium firefox webkit

# Clean up pip cache
RUN pip cache purge

# =============================================================================
# STAGE 3: BROWSER SECURITY SETUP
# =============================================================================
FROM crawler-dependencies AS browser-security

LABEL stage=browser-security
LABEL description="Browser security and anti-detection setup"

ENV PATH="/opt/venv/bin:$PATH"

# Configure Tor for proxy rotation
RUN echo "SocksPort 9050" >> /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C" >> /etc/tor/torrc

# Configure proxy chains
RUN echo "strict_chain" > /etc/proxychains4.conf && \
    echo "proxy_dns" >> /etc/proxychains4.conf && \
    echo "tcp_read_time_out 15000" >> /etc/proxychains4.conf && \
    echo "tcp_connect_time_out 8000" >> /etc/proxychains4.conf && \
    echo "[ProxyList]" >> /etc/proxychains4.conf && \
    echo "socks5 127.0.0.1 9050" >> /etc/proxychains4.conf

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM crawler-base AS production

LABEL stage=production
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Crawler Service - Production Runtime"
LABEL service="crawler-service"
LABEL capabilities="web-scraping,browser-automation,content-monitoring"

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Crawler service specific
    CRAWLER_SERVICE=true \
    SERVICE_PORT=8001 \
    # Browser settings
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99 \
    # Concurrency settings
    CRAWLER_WORKERS=8 \
    MAX_CONCURRENT_CRAWLS=20 \
    REQUEST_DELAY=1 \
    # Anti-detection settings
    ROTATE_USER_AGENTS=true \
    USE_PROXY_ROTATION=true \
    ENABLE_STEALTH_MODE=true \
    # Performance settings
    DOWNLOAD_TIMEOUT=30 \
    DOWNLOAD_DELAY=2 \
    AUTOTHROTTLE_ENABLED=true

# Copy browser security configuration
COPY --from=browser-security /etc/tor/torrc /etc/tor/torrc
COPY --from=browser-security /etc/proxychains4.conf /etc/proxychains4.conf

# Remove build dependencies, keep runtime
RUN apt-get remove -y \
        build-essential \
        pkg-config \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from dependencies stage
COPY --from=crawler-dependencies /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=crawler:crawler . .

# Create crawler data directories with proper permissions
RUN mkdir -p \
        /app/crawled_data \
        /app/crawled_data/raw \
        /app/crawled_data/processed \
        /app/crawled_data/media \
        /app/logs \
        /app/temp \
        /app/cache \
        /app/proxies \
        /app/user_agents \
    && chown -R crawler:crawler /app \
    && chmod -R 755 /app \
    && chmod -R 777 /app/crawled_data /app/logs /app/temp /app/cache /app/proxies /app/user_agents

# Create crawler service startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Crawler Service Starting ==="\n\
echo "Service Port: ${SERVICE_PORT}"\n\
echo "Workers: ${CRAWLER_WORKERS}"\n\
echo "Max Concurrent: ${MAX_CONCURRENT_CRAWLS}"\n\
echo "Stealth Mode: ${ENABLE_STEALTH_MODE}"\n\
echo "================================"\n\
\n\
# Start virtual display for headless browsers\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
export DISPLAY=:99\n\
\n\
# Start Tor for proxy rotation (if enabled)\n\
if [ "$USE_PROXY_ROTATION" = "true" ]; then\n\
    echo "Starting Tor for proxy rotation..."\n\
    tor > /dev/null 2>&1 &\n\
    sleep 5\n\
fi\n\
\n\
# Validate browser installations\n\
echo "Validating browser installations..."\n\
chromium --version || echo "Chromium not available"\n\
firefox --version || echo "Firefox not available"\n\
\n\
# Start crawler management service\n\
exec python -m uvicorn crawlers.service:app \\\n\
    --host 0.0.0.0 \\\n\
    --port ${SERVICE_PORT} \\\n\
    --workers 1 \\\n\
    --worker-class uvicorn.workers.UvicornWorker \\\n\
    --log-level info \\\n\
    --access-log\n\
' > /app/start-crawler.sh && chmod +x /app/start-crawler.sh

# Switch to non-root user
USER crawler

# Expose service port
EXPOSE 8001

# Health check with browser validation
HEALTHCHECK --interval=30s \
            --timeout=15s \
            --start-period=60s \
            --retries=3 \
            CMD curl -f http://localhost:8001/health \
                && python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.quit()
    print('Browser validation successful')
    sys.exit(0)
except Exception as e:
    print(f'Browser validation failed: {e}')
    sys.exit(1)
" || exit 1

# Start crawler service
CMD ["/app/start-crawler.sh"]