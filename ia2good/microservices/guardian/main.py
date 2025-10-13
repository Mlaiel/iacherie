"""
Guardian Volunteer Platform - Main Application
Plateforme humanitaire pour volontaires et missions d'urgence

Author: Fahed Mlaiel
Created: 2025-10-12
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add shared services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared-services'))

# Import configuration
try:
    from config import Settings as GuardianSettings
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config import Settings as GuardianSettings
Settings = GuardianSettings

settings = Settings()

# Force IACherie URL
os.environ["IACHERIE_API_URL"] = settings.IACHERIE_API_URL

# Import routes
try:
    from routes.missions import router as missions_router
    from routes.volunteers import router as volunteers_router
    from routes.ai_routes import router as ai_router
    from routes.ai_learning_routes import router as ai_learning_router
    from routes.geo_routes import router as geo_router
    from routes.streaming_routes import router as streaming_router
    from routes.videochat_routes import router as videochat_router
    from routes.files_routes import router as files_router
    from routes.chat_routes import router as chat_router
    from routes.admin_routes import router as admin_router
    from routes.auth_routes import router as auth_router
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from routes.missions import router as missions_router
    from routes.volunteers import router as volunteers_router
    from routes.ai_routes import router as ai_router
    from routes.ai_learning_routes import router as ai_learning_router
    from routes.geo_routes import router as geo_router
    from routes.streaming_routes import router as streaming_router
    from routes.videochat_routes import router as videochat_router
    from routes.files_routes import router as files_router
    from routes.chat_routes import router as chat_router
    from routes.admin_routes import router as admin_router
    from routes.auth_routes import router as auth_router

# Database
try:
    from database import init_db
except ImportError:
    # Mock init_db if not available
    async def init_db():
        logger.warning("Database module not available, skipping initialization")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Guardian Volunteer Platform v1.0.0")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Start AI Learning Service (Few-Shot Learning & Continuous Improvement)
    try:
        from services import start_continuous_learning
        await start_continuous_learning()
        logger.info("✅ AI Self-Learning Service started (Few-Shot Learning active)")
    except Exception as e:
        logger.error(f"❌ AI Learning Service failed: {e}")
    
    # Check IACherie connection
    try:
        from iacherie_ai_client import get_ai_client
        client = get_ai_client()
        health_response = await client.client.get("/health")
        if health_response.status_code == 200:
            logger.info("✅ IACherie AI integration healthy")
        else:
            logger.warning(f"⚠️ IACherie health check returned: {health_response.status_code}")
    except Exception as e:
        logger.error(f"❌ IACherie connection failed: {e}")
    
    logger.info("Guardian microservice is ready")
    logger.info("🌍 Mission management: /guardian/missions")
    logger.info("👥 Volunteer registration: /guardian/volunteers")
    logger.info("🤖 AI assistance: /guardian/ai")
    logger.info("🧠 AI Self-Learning: /guardian/ai-learning")
    logger.info("🗺️ Real-time geo map: /guardian/geo")
    logger.info("📹 Live streaming: /guardian/live")
    logger.info("💬 Video chat: /guardian/videochat")
    logger.info("📁 File uploads: /guardian/files")
    logger.info("💭 Chat rooms: /guardian/chat")
    
    yield
    
    logger.info("Shutting down Guardian Volunteer Platform")

# Create FastAPI app
app = FastAPI(
    title="Guardian Volunteer Platform",
    description="Plateforme humanitaire IA2GOOD pour coordination de volontaires et missions d'urgence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/guardian", tags=["Authentication"])
app.include_router(missions_router, prefix="/api/guardian", tags=["Missions"])
app.include_router(volunteers_router, prefix="/api/guardian", tags=["Volunteers"])
app.include_router(ai_router, prefix="/api/guardian", tags=["Guardian AI"])
app.include_router(ai_learning_router, prefix="/api/guardian", tags=["AI Self-Learning"])
app.include_router(geo_router, prefix="/api/guardian/geo", tags=["Geographic & Real-time Map"])
app.include_router(streaming_router, prefix="/api/guardian/live", tags=["Live Streaming"])
app.include_router(videochat_router, prefix="/api/guardian/videochat", tags=["Video Chat"])
app.include_router(files_router, prefix="/api/guardian/files", tags=["File Uploads"])
app.include_router(chat_router, prefix="/api/guardian/chat", tags=["Chat Rooms"])
app.include_router(admin_router, prefix="/api/guardian", tags=["Admin & Moderation"])

# Mount static files for map interface
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Guardian Volunteer Platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Guardian Volunteer Platform",
        "description": "Plateforme humanitaire pour coordination de volontaires",
        "endpoints": {
            "missions": "/api/guardian/missions",
            "volunteers": "/api/guardian/volunteers",
            "ai_assistance": "/api/guardian/ai",
            "ai_learning": "/api/guardian/ai-learning",
            "geo_map": "/api/guardian/geo",
            "live_streaming": "/api/guardian/live",
            "video_chat": "/api/guardian/videochat",
            "file_uploads": "/api/guardian/files",
            "chat_rooms": "/api/guardian/chat",
            "real_time_map": "/static/map.html",
            "health": "/health"
        },
        "websockets": {
            "geo_realtime": "ws://localhost:8001/api/guardian/geo/ws/map",
            "live_stream": "ws://localhost:8001/api/guardian/live/stream/{stream_id}",
            "watch_stream": "ws://localhost:8001/api/guardian/live/watch/{stream_id}",
            "video_call": "ws://localhost:8001/api/guardian/videochat/room/{room_id}",
            "chat_room": "ws://localhost:8001/api/guardian/chat/room/{room_id}",
            "direct_message": "ws://localhost:8001/api/guardian/chat/dm/{user_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
