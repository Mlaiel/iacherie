"""
Guardian Live Streaming Routes
Live video streaming for missions and events
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import asyncio
import base64

router = APIRouter()

# Models
class StreamConfig(BaseModel):
    stream_id: str
    mission_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    quality: str = "720p"  # 480p, 720p, 1080p
    is_public: bool = True

class StreamStatus(BaseModel):
    stream_id: str
    status: str  # live, paused, ended
    viewers: int
    started_at: datetime
    duration_seconds: int

# Storage
active_streams: Dict[str, StreamConfig] = {}
stream_viewers: Dict[str, List[WebSocket]] = {}
stream_status: Dict[str, StreamStatus] = {}

# ============================================================================
# STREAM MANAGEMENT
# ============================================================================

@router.post("/streams/create")
def create_stream(config: StreamConfig):
    """Créer un nouveau stream"""
    import uuid
    
    if not config.stream_id:
        config.stream_id = str(uuid.uuid4())
    
    active_streams[config.stream_id] = config
    stream_viewers[config.stream_id] = []
    stream_status[config.stream_id] = StreamStatus(
        stream_id=config.stream_id,
        status="ready",
        viewers=0,
        started_at=datetime.utcnow(),
        duration_seconds=0
    )
    
    return {
        "success": True,
        "stream_id": config.stream_id,
        "stream_url": f"ws://localhost:8001/api/guardian/live/stream/{config.stream_id}",
        "watch_url": f"ws://localhost:8001/api/guardian/live/watch/{config.stream_id}"
    }

@router.get("/streams")
def list_streams():
    """Lister tous les streams actifs"""
    streams_list = []
    for stream_id, config in active_streams.items():
        status = stream_status.get(stream_id)
        streams_list.append({
            "stream_id": stream_id,
            "title": config.title,
            "mission_id": config.mission_id,
            "status": status.status if status else "unknown",
            "viewers": len(stream_viewers.get(stream_id, []))
        })
    
    return {
        "success": True,
        "total": len(streams_list),
        "streams": streams_list
    }

@router.get("/streams/{stream_id}")
def get_stream_info(stream_id: str):
    """Obtenir les infos d'un stream"""
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    config = active_streams[stream_id]
    status = stream_status.get(stream_id)
    
    return {
        "success": True,
        "stream": {
            **config.dict(),
            "status": status.dict() if status else None,
            "viewers": len(stream_viewers.get(stream_id, []))
        }
    }

@router.delete("/streams/{stream_id}")
def end_stream(stream_id: str):
    """Terminer un stream"""
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    # Disconnect all viewers
    viewers = stream_viewers.get(stream_id, [])
    for viewer in viewers:
        try:
            asyncio.create_task(viewer.close())
        except:
            pass
    
    # Remove stream
    del active_streams[stream_id]
    if stream_id in stream_viewers:
        del stream_viewers[stream_id]
    if stream_id in stream_status:
        del stream_status[stream_id]
    
    return {
        "success": True,
        "message": "Stream ended"
    }

# ============================================================================
# STREAMING WebSocket (Broadcaster)
# ============================================================================

@router.websocket("/stream/{stream_id}")
async def stream_websocket(websocket: WebSocket, stream_id: str):
    """WebSocket pour le broadcaster (celui qui stream)"""
    await websocket.accept()
    
    if stream_id not in active_streams:
        await websocket.send_json({"error": "Stream not found"})
        await websocket.close()
        return
    
    # Update status to live
    if stream_id in stream_status:
        stream_status[stream_id].status = "live"
    
    try:
        while True:
            # Receive video frame from broadcaster
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "frame":
                # Broadcast frame to all viewers
                viewers = stream_viewers.get(stream_id, [])
                for viewer in viewers:
                    try:
                        await viewer.send_json({
                            "type": "frame",
                            "data": message.get("data"),
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except:
                        # Remove disconnected viewer
                        viewers.remove(viewer)
            
            elif message.get("type") == "end":
                # End stream
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        # Update status
        if stream_id in stream_status:
            stream_status[stream_id].status = "ended"

# ============================================================================
# WATCHING WebSocket (Viewers)
# ============================================================================

@router.websocket("/watch/{stream_id}")
async def watch_websocket(websocket: WebSocket, stream_id: str):
    """WebSocket pour les viewers (ceux qui regardent)"""
    await websocket.accept()
    
    if stream_id not in active_streams:
        await websocket.send_json({"error": "Stream not found"})
        await websocket.close()
        return
    
    # Add viewer
    if stream_id not in stream_viewers:
        stream_viewers[stream_id] = []
    stream_viewers[stream_id].append(websocket)
    
    # Send stream info
    config = active_streams[stream_id]
    await websocket.send_json({
        "type": "stream_info",
        "title": config.title,
        "description": config.description,
        "quality": config.quality
    })
    
    try:
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle viewer commands (like pause, etc.)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    finally:
        # Remove viewer
        if stream_id in stream_viewers and websocket in stream_viewers[stream_id]:
            stream_viewers[stream_id].remove(websocket)

# ============================================================================
# STREAM STATISTICS
# ============================================================================

@router.get("/streams/{stream_id}/stats")
def get_stream_stats(stream_id: str):
    """Obtenir les statistiques d'un stream"""
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    status = stream_status.get(stream_id)
    viewers_count = len(stream_viewers.get(stream_id, []))
    
    return {
        "success": True,
        "stream_id": stream_id,
        "viewers": viewers_count,
        "status": status.dict() if status else None,
        "timestamp": datetime.utcnow().isoformat()
    }
