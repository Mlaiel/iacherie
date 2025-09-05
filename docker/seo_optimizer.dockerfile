# =============================================================================
# AINFLUE SEO OPTIMIZATION SERVICE - INTELLIGENT DOCKERFILE
# =============================================================================
# AI-powered SEO optimization with keyword analysis, metadata enrichment,
# and viral prediction capabilities for content creators.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: SEO ANALYSIS BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS seo-base

LABEL stage=seo-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="AI-powered SEO optimization and content intelligence"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install SEO analysis dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Python runtime
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        # Text processing
        libxml2-dev \
        libxslt1-dev \
        # Image processing for metadata
        libimage-exiftool-perl \
        # Build tools
        build-essential \
        pkg-config \
        git \
        wget \
        curl \
        # Database support
        libpq-dev \
        # System utilities
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r -g 10001 ainflue && \
    useradd -r -u 10001 -g ainflue -d /app -s /bin/bash ainflue

# =============================================================================
# STAGE 2: AI/NLP DEPENDENCIES
# =============================================================================
FROM seo-base AS ai-nlp-deps

# Set up Python environment
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install SEO and AI packages
RUN pip install --no-cache-dir \
    # Web framework
    fastapi>=0.104.1 \
    uvicorn[standard]>=0.24.0 \
    # AI/ML for content analysis
    transformers>=4.35.0 \
    torch>=2.0.0 \
    scikit-learn>=1.3.0 \
    # NLP processing
    spacy>=3.7.0 \
    nltk>=3.8.0 \
    textblob>=0.17.0 \
    # Web scraping for trend analysis
    beautifulsoup4>=4.12.0 \
    selenium>=4.15.0 \
    scrapy>=2.11.0 \
    # Text analysis
    yake>=0.4.8 \
    keybert>=0.8.0 \
    # Social media APIs
    tweepy>=4.14.0 \
    # Data processing
    pandas>=2.1.0 \
    numpy>=1.24.0 \
    # Database
    asyncpg>=0.29.0 \
    redis>=5.0.0 \
    # HTTP client for API calls
    httpx>=0.25.0 \
    aiohttp>=3.9.0 \
    # Image processing for metadata
    Pillow>=10.0.0 \
    exifread>=3.0.0 \
    # Async support
    asyncio \
    aiofiles>=23.0.0 \
    # Monitoring
    prometheus-client>=0.19.0 \
    structlog>=23.0.0

# Download spaCy model
RUN python3.11 -m spacy download en_core_web_sm

# =============================================================================
# STAGE 3: APPLICATION LAYER
# =============================================================================
FROM ai-nlp-deps AS application

WORKDIR /app

# Copy application code
COPY seo/ /app/seo/
COPY core/ /app/core/
COPY analytics/ /app/analytics/
COPY requirements.txt /app/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp /app/seo_analysis \
             /app/keywords /app/trends /app/metadata \
    && chown -R ainflue:ainflue /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/health-check.sh \
    && chmod +x /app/health-check.sh \
    && chown ainflue:ainflue /app/health-check.sh

# Create SEO service script
COPY <<EOF /app/seo_service.py
"""
Ainflue SEO Optimization Service
AI-powered SEO optimization and content intelligence platform
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from seo.optimization.keyword_optimizer import KeywordOptimizer
from seo.optimization.metadata_optimizer import MetadataOptimizer
from seo.automation_service import SEOAutomationService
from analytics.seo_intelligence_engine import SEOIntelligenceEngine
from core import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ainflue SEO Optimization Service",
    description="AI-powered SEO optimization and content intelligence",
    version="2.1.0"
)

# Initialize SEO services
keyword_optimizer = KeywordOptimizer()
metadata_optimizer = MetadataOptimizer()
seo_automation = SEOAutomationService()
seo_intelligence = SEOIntelligenceEngine()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "seo_optimizer",
        "components": {
            "keyword_analysis": "active",
            "metadata_optimization": "active",
            "trend_monitoring": "active",
            "intelligence_engine": "active"
        }
    }

@app.post("/analyze/keywords")
async def analyze_keywords(content: str, target_audience: str = "general"):
    """Analyze and optimize keywords for content."""
    try:
        analysis = await keyword_optimizer.analyze_content(content, target_audience)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"Keyword analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/metadata")
async def optimize_metadata(
    content_type: str,
    title: str,
    description: str,
    tags: List[str] = []
):
    """Optimize metadata for better SEO performance."""
    try:
        optimized = await metadata_optimizer.optimize(
            content_type, title, description, tags
        )
        return {"status": "success", "optimized_metadata": optimized}
    except Exception as e:
        logger.error(f"Metadata optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/analyze")
async def analyze_trends(category: str = "general", timeframe: str = "24h"):
    """Analyze current trends for content optimization."""
    try:
        trends = await seo_intelligence.analyze_trends(category, timeframe)
        return {"status": "success", "trends": trends}
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/viral")
async def predict_viral_potential(content_data: Dict[str, Any]):
    """Predict viral potential of content based on SEO factors."""
    try:
        prediction = await seo_intelligence.predict_viral_potential(content_data)
        return {"status": "success", "prediction": prediction}
    except Exception as e:
        logger.error(f"Viral prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/platform")
async def optimize_for_platform(
    platform: str,
    content_data: Dict[str, Any]
):
    """Optimize content for specific platform requirements."""
    try:
        optimized = await seo_automation.optimize_for_platform(platform, content_data)
        return {"status": "success", "optimized_content": optimized}
    except Exception as e:
        logger.error(f"Platform optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords/trending")
async def get_trending_keywords(category: str = "general", count: int = 20):
    """Get trending keywords for content category."""
    try:
        keywords = await keyword_optimizer.get_trending_keywords(category, count)
        return {"status": "success", "trending_keywords": keywords}
    except Exception as e:
        logger.error(f"Trending keywords failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/score")
async def score_content_seo(content_data: Dict[str, Any]):
    """Score content SEO quality and provide recommendations."""
    try:
        score = await seo_intelligence.score_content(content_data)
        recommendations = await seo_intelligence.get_recommendations(content_data)
        
        return {
            "status": "success",
            "seo_score": score,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Content scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation/schedule")
async def schedule_seo_automation(
    background_tasks: BackgroundTasks,
    creator_id: str,
    automation_config: Dict[str, Any]
):
    """Schedule automated SEO optimization tasks."""
    try:
        background_tasks.add_task(
            seo_automation.schedule_optimization,
            creator_id,
            automation_config
        )
        return {"status": "success", "message": "SEO automation scheduled"}
    except Exception as e:
        logger.error(f"SEO automation scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/seo")
async def get_seo_stats():
    """Get SEO optimization service statistics."""
    try:
        stats = {
            "keywords_analyzed": await keyword_optimizer.get_analysis_count(),
            "metadata_optimized": await metadata_optimizer.get_optimization_count(),
            "trends_tracked": await seo_intelligence.get_trends_count(),
            "viral_predictions": await seo_intelligence.get_predictions_count()
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
EOF

# Set proper permissions
RUN chown ainflue:ainflue /app/seo_service.py

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM application AS production

# Switch to non-root user
USER ainflue

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh

# Environment variables
ENV PYTHONPATH=/app
ENV SERVICE_NAME=seo_optimizer
ENV SERVICE_CATEGORY=seo
ENV LOG_LEVEL=INFO

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/seo_analysis", "/app/keywords", "/app/trends"]

# Set resource limits
LABEL memory="1g"
LABEL cpus="1.0"

# Entry point
CMD ["python3.11", "/app/seo_service.py"]