# Smart Contracts Service
# Ethereum smart contracts for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Smart Contracts - Ethereum smart contract management"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        nodejs \
        npm \
        pkg-config \
        libssl-dev \
        libffi-dev \
        && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler
RUN npm install -g solc truffle ganache-cli

# Create app user for security
RUN groupadd -r smartcontracts && useradd -r -g smartcontracts smartcontracts

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-contracts.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-contracts.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./monetization/smart_contracts/ ./smart_contracts/
COPY ./monetization/common/ ./common/
COPY ./contracts/ ./contracts/

# Create necessary directories
RUN mkdir -p /app/storage/contracts/deployed \
             /app/storage/contracts/abi \
             /app/storage/contracts/bytecode \
             /app/logs \
             /app/cache && \
    chown -R smartcontracts:smartcontracts /app

# Copy smart contract source files
COPY ./contracts/solidity/ ./contracts/solidity/
COPY ./contracts/vyper/ ./contracts/vyper/

# Switch to non-root user
USER smartcontracts

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=smart_contracts
ENV LOG_LEVEL=INFO
ENV ETHEREUM_NETWORK=mainnet
ENV GAS_LIMIT=8000000
ENV GAS_PRICE=20000000000
ENV CONTRACT_VERSION=1.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8031/health || exit 1

# Expose port
EXPOSE 8031

# Default command
CMD ["python", "-m", "smart_contracts.main"]