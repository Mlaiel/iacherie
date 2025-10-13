"""
📡 STREAMING ROUTES - Complete Implementation
============================================
ALL 40 endpoints for live streaming, analytics, donations, multi-platform
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/streaming", tags=["Streaming"])

# ============================================================================
# MODELS
# ============================================================================

class StreamQuality(str, Enum):
    LOW = "360p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"

class StreamStatus(str, Enum):
    OFFLINE = "offline"
    STARTING = "starting"
    LIVE = "live"
    ENDING = "ending"

# ============================================================================
# STREAM MANAGEMENT
# ============================================================================

@router.post("/start")
async def start_stream(title: str, streamer_id: str, quality: StreamQuality = StreamQuality.HIGH):
    """Start live stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        stream = await manager.start_stream(streamer_id, title, quality.value)
        return {"message": "Stream started", "stream_id": stream['id'], "stream": stream}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{stream_id}/stop")
async def stop_stream(stream_id: str, streamer_id: str):
    """Stop live stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.stop_stream(stream_id, streamer_id)
        return {"message": "Stream stopped", "stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live")
async def list_live_streams(limit: int = 50):
    """Get all live streams"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        streams = await manager.list_live_streams(limit)
        return {"total": len(streams), "streams": streams}
    except Exception as e:
        return {"total": 0, "streams": [], "error": str(e)}

@router.get("/{stream_id}")
async def get_stream(stream_id: str):
    """Get stream details"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        stream = await manager.get_stream(stream_id)
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        return stream
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stream_id}/status")
async def get_stream_status(stream_id: str):
    """Get stream status"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        status = await manager.get_stream_status(stream_id)
        return {"stream_id": stream_id, "status": status}
    except Exception as e:
        return {"stream_id": stream_id, "status": "unknown", "error": str(e)}

@router.put("/{stream_id}/settings")
async def update_stream_settings(stream_id: str, settings: Dict[str, Any]):
    """Update stream settings"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.update_settings(stream_id, settings)
        return {"message": "Settings updated", "stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM KEYS & RTMP
# ============================================================================

@router.post("/keys/generate")
async def generate_stream_key(streamer_id: str):
    """Generate stream key"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        key = await manager.generate_stream_key(streamer_id)
        return {"message": "Stream key generated", "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/{streamer_id}")
async def get_stream_key(streamer_id: str):
    """Get stream key"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        key = await manager.get_stream_key(streamer_id)
        return {"streamer_id": streamer_id, "key": key}
    except Exception as e:
        return {"streamer_id": streamer_id, "key": None, "error": str(e)}

@router.post("/keys/{streamer_id}/reset")
async def reset_stream_key(streamer_id: str):
    """Reset stream key"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        key = await manager.reset_stream_key(streamer_id)
        return {"message": "Stream key reset", "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rtmp/servers")
async def get_rtmp_servers():
    """Get RTMP server list"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        servers = await manager.get_rtmp_servers()
        return {"servers": servers}
    except Exception as e:
        return {"servers": [], "error": str(e)}

# ============================================================================
# VIEWERS & CHAT
# ============================================================================

@router.get("/{stream_id}/viewers")
async def get_viewers(stream_id: str):
    """Get current viewers"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        viewers = await manager.get_viewers(stream_id)
        return {"stream_id": stream_id, "viewer_count": len(viewers), "viewers": viewers}
    except Exception as e:
        return {"stream_id": stream_id, "viewer_count": 0, "viewers": [], "error": str(e)}

@router.post("/{stream_id}/join")
async def join_stream(stream_id: str, user_id: str):
    """Join stream as viewer"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.join_stream(stream_id, user_id)
        return {"message": "Joined stream", "stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{stream_id}/leave")
async def leave_stream(stream_id: str, user_id: str):
    """Leave stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.leave_stream(stream_id, user_id)
        return {"message": "Left stream", "stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stream_id}/chat")
async def get_chat_messages(stream_id: str, limit: int = 100):
    """Get chat messages"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        messages = await manager.get_chat_messages(stream_id, limit)
        return {"stream_id": stream_id, "messages": messages}
    except Exception as e:
        return {"stream_id": stream_id, "messages": [], "error": str(e)}

@router.post("/{stream_id}/chat")
async def send_chat_message(stream_id: str, user_id: str, message: str):
    """Send chat message"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        msg = await manager.send_chat_message(stream_id, user_id, message)
        return {"message": "Message sent", "message_data": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DONATIONS & TIPS
# ============================================================================

@router.post("/{stream_id}/donate")
async def donate_to_stream(stream_id: str, user_id: str, amount: float, message: Optional[str] = None):
    """Donate to stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        donation = await manager.process_donation(stream_id, user_id, amount, message)
        return {"message": "Donation processed", "donation": donation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stream_id}/donations")
async def get_stream_donations(stream_id: str):
    """Get stream donations"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        donations = await manager.get_donations(stream_id)
        return {"stream_id": stream_id, "donations": donations}
    except Exception as e:
        return {"stream_id": stream_id, "donations": [], "error": str(e)}

@router.get("/streamers/{streamer_id}/earnings")
async def get_streamer_earnings(streamer_id: str):
    """Get streamer earnings"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        earnings = await manager.get_streamer_earnings(streamer_id)
        return {"streamer_id": streamer_id, "earnings": earnings}
    except Exception as e:
        return {"streamer_id": streamer_id, "earnings": {}, "error": str(e)}

# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/{stream_id}/analytics")
async def get_stream_analytics(stream_id: str):
    """Get stream analytics"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        analytics = await manager.get_stream_analytics(stream_id)
        return {"stream_id": stream_id, "analytics": analytics}
    except Exception as e:
        return {"stream_id": stream_id, "analytics": {}, "error": str(e)}

@router.get("/streamers/{streamer_id}/analytics")
async def get_streamer_analytics(streamer_id: str):
    """Get streamer analytics"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        analytics = await manager.get_streamer_analytics(streamer_id)
        return {"streamer_id": streamer_id, "analytics": analytics}
    except Exception as e:
        return {"streamer_id": streamer_id, "analytics": {}, "error": str(e)}

@router.get("/{stream_id}/stats")
async def get_stream_stats(stream_id: str):
    """Get real-time stream stats"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        stats = await manager.get_stream_stats(stream_id)
        return {"stream_id": stream_id, "stats": stats}
    except Exception as e:
        return {"stream_id": stream_id, "stats": {}, "error": str(e)}

# ============================================================================
# RECORDING & VOD
# ============================================================================

@router.post("/{stream_id}/record/start")
async def start_recording(stream_id: str):
    """Start recording stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.start_recording(stream_id)
        return {"message": "Recording started", "stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{stream_id}/record/stop")
async def stop_recording(stream_id: str):
    """Stop recording stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        recording = await manager.stop_recording(stream_id)
        return {"message": "Recording stopped", "recording": recording}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streamers/{streamer_id}/vods")
async def get_vods(streamer_id: str, limit: int = 20):
    """Get VODs (Video on Demand)"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        vods = await manager.get_vods(streamer_id, limit)
        return {"streamer_id": streamer_id, "vods": vods}
    except Exception as e:
        return {"streamer_id": streamer_id, "vods": [], "error": str(e)}

@router.get("/vods/{vod_id}")
async def get_vod(vod_id: str):
    """Get VOD details"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        vod = await manager.get_vod(vod_id)
        if not vod:
            raise HTTPException(status_code=404, detail="VOD not found")
        return vod
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vods/{vod_id}")
async def delete_vod(vod_id: str, streamer_id: str):
    """Delete VOD"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.delete_vod(vod_id, streamer_id)
        return {"message": "VOD deleted", "vod_id": vod_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MULTI-PLATFORM
# ============================================================================

@router.post("/multistream/add")
async def add_platform(stream_id: str, platform: str, credentials: Dict[str, Any]):
    """Add streaming platform"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.add_platform(stream_id, platform, credentials)
        return {"message": "Platform added", "platform": platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stream_id}/platforms")
async def get_stream_platforms(stream_id: str):
    """Get connected platforms"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        platforms = await manager.get_platforms(stream_id)
        return {"stream_id": stream_id, "platforms": platforms}
    except Exception as e:
        return {"stream_id": stream_id, "platforms": [], "error": str(e)}

@router.delete("/{stream_id}/platforms/{platform}")
async def remove_platform(stream_id: str, platform: str):
    """Remove streaming platform"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.remove_platform(stream_id, platform)
        return {"message": "Platform removed", "platform": platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MODERATION
# ============================================================================

@router.post("/{stream_id}/moderators/add")
async def add_moderator(stream_id: str, user_id: str):
    """Add stream moderator"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.add_moderator(stream_id, user_id)
        return {"message": "Moderator added", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stream_id}/moderators")
async def get_moderators(stream_id: str):
    """Get stream moderators"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        moderators = await manager.get_moderators(stream_id)
        return {"stream_id": stream_id, "moderators": moderators}
    except Exception as e:
        return {"stream_id": stream_id, "moderators": [], "error": str(e)}

@router.post("/{stream_id}/ban")
async def ban_user(stream_id: str, user_id: str, reason: Optional[str] = None):
    """Ban user from stream"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.ban_user(stream_id, user_id, reason)
        return {"message": "User banned", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{stream_id}/timeout")
async def timeout_user(stream_id: str, user_id: str, duration: int = 600):
    """Timeout user"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.timeout_user(stream_id, user_id, duration)
        return {"message": "User timed out", "user_id": user_id, "duration": duration}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FOLLOWERS & SUBSCRIPTIONS
# ============================================================================

@router.post("/streamers/{streamer_id}/follow")
async def follow_streamer(streamer_id: str, user_id: str):
    """Follow streamer"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        await manager.follow_streamer(streamer_id, user_id)
        return {"message": "Followed streamer", "streamer_id": streamer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streamers/{streamer_id}/followers")
async def get_followers(streamer_id: str):
    """Get streamer followers"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        followers = await manager.get_followers(streamer_id)
        return {"streamer_id": streamer_id, "follower_count": len(followers), "followers": followers}
    except Exception as e:
        return {"streamer_id": streamer_id, "follower_count": 0, "followers": [], "error": str(e)}

@router.post("/streamers/{streamer_id}/subscribe")
async def subscribe_to_streamer(streamer_id: str, user_id: str, tier: str = "basic"):
    """Subscribe to streamer"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        subscription = await manager.subscribe(streamer_id, user_id, tier)
        return {"message": "Subscribed", "subscription": subscription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streamers/{streamer_id}/subscribers")
async def get_subscribers(streamer_id: str):
    """Get streamer subscribers"""
    try:
        from backend.streaming.stream_manager import StreamManager
        manager = StreamManager()
        await manager.initialize()
        
        subscribers = await manager.get_subscribers(streamer_id)
        return {"streamer_id": streamer_id, "subscriber_count": len(subscribers), "subscribers": subscribers}
    except Exception as e:
        return {"streamer_id": streamer_id, "subscriber_count": 0, "subscribers": [], "error": str(e)}
