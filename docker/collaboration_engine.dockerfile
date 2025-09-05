# =============================================================================
# AINFLUE COLLABORATION ENGINE - INTELLIGENT DOCKERFILE
# =============================================================================
# AI-powered creator collaboration platform with intelligent matching,
# gamification, and workflow management capabilities.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: COLLABORATION BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS collaboration-base

LABEL stage=collaboration-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="AI-powered creator collaboration and matching engine"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install collaboration platform dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Python runtime
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        # Graph database support
        libgraphviz-dev \
        graphviz \
        # Real-time communication
        redis-tools \
        # Database support
        libpq-dev \
        # Build tools
        build-essential \
        pkg-config \
        git \
        wget \
        curl \
        # System utilities
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r -g 10001 ainflue && \
    useradd -r -u 10001 -g ainflue -d /app -s /bin/bash ainflue

# =============================================================================
# STAGE 2: AI MATCHING DEPENDENCIES
# =============================================================================
FROM collaboration-base AS ai-deps

# Set up Python environment
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install AI and collaboration packages
RUN pip install --no-cache-dir \
    # Web framework
    fastapi>=0.104.1 \
    uvicorn[standard]>=0.24.0 \
    # AI/ML for matching
    scikit-learn>=1.3.0 \
    numpy>=1.24.0 \
    pandas>=2.1.0 \
    # Graph analysis
    networkx>=3.2.0 \
    pygraphviz>=1.11 \
    # Recommendation engines
    surprise>=1.1.3 \
    implicit>=0.7.0 \
    # Real-time communication
    redis>=5.0.0 \
    websockets>=12.0 \
    socketio>=5.9.0 \
    # Database
    asyncpg>=0.29.0 \
    # Machine Learning
    torch>=2.0.0 \
    transformers>=4.35.0 \
    # Gamification
    python-dateutil>=2.8.2 \
    # Content analysis
    pillow>=10.0.0 \
    # Async support
    asyncio \
    aiofiles>=23.0.0 \
    aioredis>=2.0.1 \
    # HTTP client
    httpx>=0.25.0 \
    # Monitoring
    prometheus-client>=0.19.0 \
    structlog>=23.0.0

# =============================================================================
# STAGE 3: APPLICATION LAYER
# =============================================================================
FROM ai-deps AS application

WORKDIR /app

# Copy application code
COPY services/ /app/services/
COPY core/ /app/core/
COPY analytics/ /app/analytics/
COPY requirements.txt /app/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp /app/collaboration \
             /app/projects /app/matches /app/gamification \
    && chown -R ainflue:ainflue /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/health-check.sh \
    && chmod +x /app/health-check.sh \
    && chown ainflue:ainflue /app/health-check.sh

# Create collaboration service script
COPY <<EOF /app/collaboration_service.py
"""
Ainflue Collaboration Engine Service
AI-powered creator matching and collaboration platform
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from services.collaboration_engine import CollaborationEngine
from services.content_matching_engine import ContentMatchingEngine
from services.gamification_system import GamificationSystem
from services.recommendation_engine import RecommendationEngine
from core import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ainflue Collaboration Engine",
    description="AI-powered creator collaboration and matching platform",
    version="2.1.0"
)

# Initialize collaboration services
collaboration_engine = CollaborationEngine()
matching_engine = ContentMatchingEngine()
gamification = GamificationSystem()
recommendation_engine = RecommendationEngine()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "collaboration_engine",
        "components": {
            "matching": "active",
            "gamification": "active",
            "recommendations": "active",
            "real_time": "active"
        }
    }

@app.post("/creators/match")
async def match_creators(creator_profile: Dict[str, Any]):
    """Find compatible creators for collaboration."""
    try:
        matches = await matching_engine.find_matches(creator_profile)
        return {"status": "success", "matches": matches}
    except Exception as e:
        logger.error(f"Creator matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/create")
async def create_collaboration_project(
    creator_id: str,
    project_data: Dict[str, Any]
):
    """Create new collaboration project."""
    try:
        project = await collaboration_engine.create_project(creator_id, project_data)
        return {"status": "success", "project": project}
    except Exception as e:
        logger.error(f"Project creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get collaboration project details."""
    try:
        project = await collaboration_engine.get_project(project_id)
        return {"status": "success", "project": project}
    except Exception as e:
        logger.error(f"Project retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/join")
async def join_project(project_id: str, creator_id: str):
    """Join collaboration project."""
    try:
        result = await collaboration_engine.join_project(project_id, creator_id)
        
        # Update gamification points
        await gamification.award_points(creator_id, "project_join", 50)
        
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Project join failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{creator_id}")
async def get_recommendations(creator_id: str, content_type: str = "all"):
    """Get personalized collaboration recommendations."""
    try:
        recommendations = await recommendation_engine.get_recommendations(
            creator_id, content_type
        )
        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gamification/{creator_id}")
async def get_gamification_status(creator_id: str):
    """Get creator's gamification status and achievements."""
    try:
        status = await gamification.get_creator_status(creator_id)
        return {"status": "success", "gamification": status}
    except Exception as e:
        logger.error(f"Gamification status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{creator_id}")
async def websocket_endpoint(websocket: WebSocket, creator_id: str):
    """WebSocket endpoint for real-time collaboration."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process real-time collaboration data
            response = await collaboration_engine.handle_realtime(creator_id, data)
            await websocket.send_text(response)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

@app.get("/stats/collaboration")
async def get_collaboration_stats():
    """Get collaboration platform statistics."""
    try:
        stats = {
            "active_projects": await collaboration_engine.get_active_projects_count(),
            "total_matches": await matching_engine.get_matches_count(),
            "gamification_users": await gamification.get_active_users_count(),
            "recommendations_served": await recommendation_engine.get_recommendations_count()
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
EOF

# Set proper permissions
RUN chown ainflue:ainflue /app/collaboration_service.py

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
ENV SERVICE_NAME=collaboration_engine
ENV SERVICE_CATEGORY=collaboration
ENV LOG_LEVEL=INFO

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/collaboration", "/app/projects"]

# Set resource limits
LABEL memory="1g"
LABEL cpus="1.0"

# Entry point
CMD ["python3.11", "/app/collaboration_service.py"]