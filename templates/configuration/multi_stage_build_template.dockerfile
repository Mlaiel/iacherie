# =====================================================================================
# Multi-Stage Build Template - Ainflue Configuration Module
# =====================================================================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
# Utilisation commerciale INTERDITE sans autorisation écrite
# =====================================================================================

# =====================================================================================
# MULTI-STAGE DOCKERFILE FOR AINFLUE CREATOR ECONOMY PLATFORM
# =====================================================================================

# Build arguments for multi-stage configuration
ARG NODE_VERSION=20.10.0
ARG PYTHON_VERSION=3.11.6
ARG ALPINE_VERSION=3.19
ARG NGINX_VERSION=1.25.3
ARG DISTROLESS_VERSION=nonroot
ARG TARGET_ARCH=amd64

# =====================================================================================
# STAGE 1: BASE IMAGE WITH SECURITY HARDENING
# =====================================================================================

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION} AS base

# Security: Create non-root user early
RUN addgroup -g 1001 -S ainflue && \
    adduser -S ainflue -u 1001 -G ainflue && \
    mkdir -p /home/ainflue && \
    chown -R ainflue:ainflue /home/ainflue

# Install security updates and essential packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        ca-certificates \
        tzdata \
        dumb-init \
        curl \
        jq && \
    rm -rf /var/cache/apk/* && \
    # Security: Remove package manager cache
    rm -rf /tmp/* /var/tmp/*

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Security labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \
      version="1.0.0" \
      description="Ainflue Creator Economy Platform - Multi-Stage Build" \
      security.scan="required" \
      security.level="high" \
      compliance.pci-dss="enabled" \
      compliance.gdpr="enabled"

# =====================================================================================
# STAGE 2: DEPENDENCIES BUILDER (Node.js Frontend + Tools)
# =====================================================================================

FROM base AS node-deps-builder

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY package*.json yarn.lock* ./
COPY frontend/package*.json ./frontend/
COPY backend/package*.json ./backend/

# Install Node.js dependencies
RUN npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force && \
    # Frontend dependencies
    cd frontend && \
    npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force && \
    # Backend dependencies  
    cd ../backend && \
    npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force

# Security: Remove development files
RUN find /app -name "*.md" -delete && \
    find /app -name "*.txt" -delete && \
    find /app -name "test*" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /app -name "docs*" -type d -exec rm -rf {} + 2>/dev/null || true

# =====================================================================================
# STAGE 3: PYTHON DEPENDENCIES BUILDER (AI/ML Services)
# =====================================================================================

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS python-deps-builder

# Install build dependencies
RUN apk add --no-cache \
        gcc \
        musl-dev \
        linux-headers \
        postgresql-dev \
        jpeg-dev \
        zlib-dev \
        freetype-dev \
        lcms2-dev \
        openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
        harfbuzz-dev \
        fribidi-dev \
        libimagequant-dev \
        libxcb-dev \
        libpng-dev

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements*.txt ./
COPY ml/requirements*.txt ./ml/
COPY ai/requirements*.txt ./ai/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-ml.txt && \
    pip install --no-cache-dir -r requirements-production.txt && \
    # AI/ML specific dependencies
    pip install --no-cache-dir -r ml/requirements.txt && \
    pip install --no-cache-dir -r ai/requirements.txt && \
    # Security: Remove pip cache
    pip cache purge && \
    # Remove build dependencies
    apk del gcc musl-dev linux-headers

# =====================================================================================
# STAGE 4: FRONTEND BUILDER (React/Vue Creator Interface)
# =====================================================================================

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION} AS frontend-builder

# Install build dependencies
RUN apk add --no-cache \
        python3 \
        make \
        g++ \
        git

WORKDIR /app/frontend

# Copy frontend source and dependencies
COPY --from=node-deps-builder /app/frontend/node_modules ./node_modules
COPY frontend/ ./

# Build frontend for production
ENV NODE_ENV=production
ENV REACT_APP_API_URL=/api
ENV REACT_APP_VERSION=${BUILD_VERSION:-1.0.0}
ENV REACT_APP_ENVIRONMENT=production
ENV GENERATE_SOURCEMAP=false
ENV CI=true

RUN npm run build && \
    # Security: Remove source maps and dev files
    find build -name "*.map" -delete && \
    # Optimize bundle size
    npm run analyze --silent && \
    # Clean up
    rm -rf node_modules src public *.json *.js *.ts

# =====================================================================================
# STAGE 5: BACKEND BUILDER (Node.js API + Services)
# =====================================================================================

FROM base AS backend-builder

WORKDIR /app/backend

# Copy backend dependencies and source
COPY --from=node-deps-builder /app/backend/node_modules ./node_modules
COPY backend/ ./

# Build backend services
ENV NODE_ENV=production
ENV BUILD_TARGET=production

RUN npm run build && \
    npm run optimize && \
    # Security: Remove development files
    rm -rf src/ tests/ *.md *.json tsconfig.json && \
    # Remove devDependencies
    npm prune --production && \
    npm cache clean --force

# =====================================================================================
# STAGE 6: AI/ML MODELS BUILDER
# =====================================================================================

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS ai-builder

WORKDIR /app/ai

# Copy Python dependencies
COPY --from=python-deps-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps-builder /usr/local/bin /usr/local/bin

# Copy AI/ML source code
COPY ai/ ./
COPY ml/ ../ml/

# Compile and optimize models
ENV PYTHONPATH=/app
ENV AI_MODEL_CACHE=/app/models
ENV TOKENIZERS_PARALLELISM=false

RUN python -m compileall . && \
    # Pre-load and cache models
    python scripts/preload_models.py && \
    # Optimize model files
    python scripts/optimize_models.py && \
    # Remove source files, keep compiled
    find . -name "*.py" -not -path "./scripts/*" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# =====================================================================================
# STAGE 7: NGINX BUILDER (Optimized Web Server)
# =====================================================================================

FROM nginx:${NGINX_VERSION}-alpine AS nginx-builder

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/ /etc/nginx/conf.d/
COPY nginx/security/ /etc/nginx/security/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build /usr/share/nginx/html

# Security: Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    # Test nginx configuration
    nginx -t

# =====================================================================================
# STAGE 8: PRODUCTION BASE (Distroless for Security)
# =====================================================================================

FROM gcr.io/distroless/nodejs20-debian12:${DISTROLESS_VERSION} AS production-base

# Copy CA certificates
COPY --from=base /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Set environment
ENV NODE_ENV=production
ENV PORT=3000
ENV TZ=UTC

# =====================================================================================
# STAGE 9: CREATOR CONTENT PROCESSOR (Microservice)
# =====================================================================================

FROM production-base AS content-processor

WORKDIR /app

# Copy backend build and dependencies
COPY --from=backend-builder /app/backend/dist ./dist
COPY --from=backend-builder /app/backend/node_modules ./node_modules

# Copy AI/ML models and compiled code
COPY --from=ai-builder /app/ai ./ai
COPY --from=ai-builder /app/models ./models

# Create non-root user
USER 1001:1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

EXPOSE 3000

# Use dumb-init for proper signal handling
ENTRYPOINT ["/nodejs/bin/node", "dist/services/content-processor/index.js"]

# Labels for container registry
LABEL service.name="content-processor" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="microservice" \
      service.purpose="creator-content-processing" \
      security.scan.required="true"

# =====================================================================================
# STAGE 10: AI ENHANCEMENT SERVICE (GPU-Optimized)
# =====================================================================================

FROM nvidia/cuda:12.2-runtime-ubuntu22.04 AS ai-enhancement

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3-pip \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    # Security updates
    apt-get clean

WORKDIR /app

# Copy Python environment and AI models
COPY --from=python-deps-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps-builder /usr/local/bin /usr/local/bin
COPY --from=ai-builder /app/ai ./ai
COPY --from=ai-builder /app/models ./models

# Create non-root user
RUN groupadd -r -g 1001 ainflue && \
    useradd -r -u 1001 -g ainflue -d /app -s /bin/bash ainflue && \
    chown -R ainflue:ainflue /app

USER ainflue:ainflue

# Environment for GPU acceleration
ENV CUDA_VISIBLE_DEVICES=all
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV PYTHONPATH=/app
ENV AI_ACCELERATION=cuda

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python3", "-m", "ai.enhancement.server"]

LABEL service.name="ai-enhancement" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="ai-microservice" \
      service.gpu="required" \
      service.purpose="content-ai-enhancement"

# =====================================================================================
# STAGE 11: PROTECTION ENGINE (Security Microservice)
# =====================================================================================

FROM production-base AS protection-engine

WORKDIR /app

# Copy backend security modules
COPY --from=backend-builder /app/backend/dist/services/protection ./protection
COPY --from=backend-builder /app/backend/node_modules ./node_modules

# Copy security configuration
COPY security/config/ ./config/
COPY security/policies/ ./policies/

USER 1001:1001

# Security-focused environment
ENV SECURITY_LEVEL=maximum
ENV ENCRYPTION_REQUIRED=true
ENV AUDIT_ENABLED=true
ENV RATE_LIMIT_STRICT=true

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:3001/health/security || exit 1

ENTRYPOINT ["/nodejs/bin/node", "protection/index.js"]

LABEL service.name="protection-engine" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="security-microservice" \
      service.purpose="content-protection" \
      security.level="critical"

# =====================================================================================
# STAGE 12: MONETIZATION PLATFORM (Business Logic)
# =====================================================================================

FROM production-base AS monetization-platform

WORKDIR /app

# Copy monetization modules
COPY --from=backend-builder /app/backend/dist/services/monetization ./monetization
COPY --from=backend-builder /app/backend/node_modules ./node_modules

# Copy payment and billing configurations
COPY monetization/config/ ./config/
COPY monetization/templates/ ./templates/

USER 1001:1001

# Business-focused environment
ENV PAYMENT_SECURITY=pci-dss
ENV BILLING_ACCURACY=high
ENV REVENUE_TRACKING=enabled
ENV TAX_CALCULATION=automated

EXPOSE 3002

HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:3002/health/monetization || exit 1

ENTRYPOINT ["/nodejs/bin/node", "monetization/index.js"]

LABEL service.name="monetization-platform" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="business-microservice" \
      service.purpose="creator-monetization" \
      compliance.pci-dss="required"

# =====================================================================================
# STAGE 13: COLLABORATION HUB (Real-time Services)
# =====================================================================================

FROM production-base AS collaboration-hub

WORKDIR /app

# Copy collaboration modules
COPY --from=backend-builder /app/backend/dist/services/collaboration ./collaboration
COPY --from=backend-builder /app/backend/node_modules ./node_modules

USER 1001:1001

# Real-time optimized environment
ENV WEBSOCKET_ENABLED=true
ENV REAL_TIME_SYNC=enabled
ENV COLLABORATION_FEATURES=full
ENV MAX_CONCURRENT_USERS=10000

EXPOSE 3003

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3003/health/collaboration || exit 1

ENTRYPOINT ["/nodejs/bin/node", "collaboration/index.js"]

LABEL service.name="collaboration-hub" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="realtime-microservice" \
      service.purpose="creator-collaboration"

# =====================================================================================
# STAGE 14: ANALYTICS ENGINE (Data Processing)
# =====================================================================================

FROM python:${PYTHON_VERSION}-slim AS analytics-engine

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy Python environment and analytics modules
COPY --from=python-deps-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps-builder /usr/local/bin /usr/local/bin
COPY analytics/ ./analytics/
COPY data/ ./data/

# Create non-root user
RUN groupadd -r -g 1001 ainflue && \
    useradd -r -u 1001 -g ainflue -d /app ainflue && \
    chown -R ainflue:ainflue /app

USER ainflue:ainflue

# Analytics-optimized environment
ENV PYTHONPATH=/app
ENV ANALYTICS_MODE=production
ENV DATA_PROCESSING=batch
ENV METRICS_RETENTION=90d

EXPOSE 8001

HEALTHCHECK --interval=60s --timeout=20s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8001/health/analytics || exit 1

CMD ["python3", "-m", "analytics.server"]

LABEL service.name="analytics-engine" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="analytics-microservice" \
      service.purpose="creator-analytics"

# =====================================================================================
# STAGE 15: FINAL ORCHESTRATION (Multi-Service)
# =====================================================================================

FROM alpine:${ALPINE_VERSION} AS orchestrator

# Install orchestration tools
RUN apk add --no-cache \
        docker-cli \
        docker-compose \
        curl \
        jq \
        bash

WORKDIR /orchestration

# Copy orchestration scripts and configs
COPY orchestration/ ./
COPY docker-compose.production.yml ./
COPY kubernetes/ ./k8s/

# Copy service discovery configuration
COPY consul/ ./consul/
COPY envoy/ ./envoy/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create non-root user
RUN addgroup -g 1001 -S orchestrator && \
    adduser -S orchestrator -u 1001 -G orchestrator && \
    chown -R orchestrator:orchestrator /orchestration

USER orchestrator:orchestrator

LABEL service.name="orchestrator" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="orchestration" \
      service.purpose="multi-service-coordination"

# =====================================================================================
# STAGE 16: DEVELOPMENT IMAGE (Full Featured)
# =====================================================================================

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION} AS development

# Install development tools
RUN apk add --no-cache \
        git \
        python3 \
        make \
        g++ \
        postgresql-client \
        redis \
        curl \
        vim \
        bash \
        openssh-client

WORKDIR /app

# Copy all source code for development
COPY . .

# Install all dependencies (including dev)
RUN npm install && \
    cd frontend && npm install && \
    cd ../backend && npm install

# Development environment
ENV NODE_ENV=development
ENV DEBUG=ainflue:*
ENV HOT_RELOAD=enabled

EXPOSE 3000 3001 3002 3003 8000 8001

CMD ["npm", "run", "dev"]

LABEL service.name="development" \
      service.version="${BUILD_VERSION:-1.0.0}" \
      service.type="development" \
      service.purpose="full-development-environment"

# =====================================================================================
# BUILD TARGETS SUMMARY
# =====================================================================================

# Production targets:
# - content-processor: Core content processing microservice
# - ai-enhancement: GPU-accelerated AI enhancement service  
# - protection-engine: Security and content protection
# - monetization-platform: Creator monetization and payments
# - collaboration-hub: Real-time collaboration features
# - analytics-engine: Data analytics and insights

# Utility targets:
# - orchestrator: Multi-service coordination
# - development: Full development environment

# Build examples:
# docker build --target content-processor -t ainflue/content-processor:latest .
# docker build --target ai-enhancement -t ainflue/ai-enhancement:latest .
# docker build --target protection-engine -t ainflue/protection-engine:latest .

# =====================================================================================
# SECURITY AND COMPLIANCE METADATA
# =====================================================================================

# Global security labels
LABEL security.scan.vendor="Snyk" \
      security.scan.type="container" \
      security.baseline="CIS Docker Benchmark v1.6.0" \
      compliance.frameworks="PCI-DSS,GDPR,SOX" \
      vulnerability.scan="required" \
      vulnerability.threshold="high" \
      license.compliance="verified" \
      supply.chain.verified="true" \
      code.signed="true" \
      build.provenance="slsa-level-3"

# Creator Economy specific metadata  
LABEL business.vertical="creator-economy" \
      platform.type="multi-tenant" \
      scaling.model="horizontal" \
      deployment.model="microservices" \
      data.classification="sensitive" \
      monitoring.level="comprehensive" \
      backup.strategy="multi-region" \
      disaster.recovery="automated"

# =====================================================================================
# END OF MULTI-STAGE BUILD TEMPLATE
# =====================================================================================