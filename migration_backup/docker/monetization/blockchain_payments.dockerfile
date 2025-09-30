# Blockchain Payments Service
# Cryptocurrency and blockchain payments for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Blockchain Payments - Cryptocurrency payment processing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        pkg-config \
        libssl-dev \
        libffi-dev \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r blockchain && useradd -r -g blockchain blockchain

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-blockchain.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-blockchain.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./monetization/blockchain_payments/ ./blockchain_payments/
COPY ./monetization/common/ ./common/
COPY ./config/blockchain/ ./config/

# Create necessary directories
RUN mkdir -p /app/storage/blockchain/wallets \
             /app/storage/blockchain/transactions \
             /app/storage/blockchain/contracts \
             /app/logs \
             /app/cache && \
    chown -R blockchain:blockchain /app

# Switch to non-root user
USER blockchain

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=blockchain_payments
ENV LOG_LEVEL=INFO
ENV SUPPORTED_CRYPTOCURRENCIES="BTC,ETH,USDT,USDC,BNB"
ENV NETWORK_ENVIRONMENT=mainnet
ENV TRANSACTION_CONFIRMATIONS=3
ENV GAS_PRICE_STRATEGY=medium

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8030/health || exit 1

# Expose port
EXPOSE 8030

# Default command
CMD ["python", "-m", "blockchain_payments.main"]