# Enterprise API Gateway Service
# High-performance API gateway with advanced routing and security
# Author: Fahed Mlaiel (mlaiel@live.de) - Backend Senior Engineer Role

FROM node:20-alpine AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Enterprise API Gateway - Advanced routing and security"
LABEL version="1.0.0"

# Install system dependencies
RUN apk add --no-cache \
    curl \
    wget \
    openssl \
    ca-certificates \
    bash \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy API gateway source code
COPY ./api_gateway/ ./

# Security: Create dedicated user
RUN addgroup -g 1000 apigateway && \
    adduser -D -u 1000 -G apigateway -s /bin/bash apigateway

# Create necessary directories
RUN mkdir -p \
    /app/logs \
    /app/configs \
    /app/certificates \
    /app/cache \
    && chown -R apigateway:apigateway /app \
    && chmod 755 /app \
    && chmod 700 /app/certificates

# Security cleanup
RUN rm -rf /tmp/* /var/tmp/* && \
    apk del wget

# Switch to non-root user
USER apigateway

# Environment variables for API Gateway
ENV NODE_ENV=production \
    SERVICE_NAME=api_gateway \
    PORT=8080 \
    CORS_ENABLED=true \
    RATE_LIMIT_ENABLED=true \
    JWT_ENABLED=true \
    SWAGGER_ENABLED=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Start API Gateway
CMD ["node", "src/server.js"]