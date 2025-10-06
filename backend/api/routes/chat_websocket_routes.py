"""
💬 CHAT & WEBSOCKET ROUTES - Complete Implementation
====================================================
ALL 30 endpoints for real-time chat, DMs, video, rooms
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/chat", tags=["Chat & WebSocket"])

# ============================================================================
# MODELS
# ============================================================================

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    SYSTEM = "system"

class RoomType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    DM = "dm"
    GROUP = "group"

class UserStatus(str, Enum):
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"

class MessageCreate(BaseModel):
    content: str
    type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None

class RoomCreate(BaseModel):
    name: str
    type: RoomType = RoomType.PUBLIC
    description: Optional[str] = None
    max_users: Optional[int] = None

# ============================================================================
# WEBSOCKET CONNECTIONS
# ============================================================================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket connection for real-time chat"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await websocket.accept()
        await manager.connect(user_id, websocket)
        
        try:
            while True:
                data = await websocket.receive_json()
                await manager.handle_message(user_id, data)
        except WebSocketDisconnect:
            await manager.disconnect(user_id)
    except Exception as e:
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011, reason=str(e))

@router.websocket("/ws/room/{room_id}/{user_id}")
async def room_websocket(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket connection for specific room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await websocket.accept()
        await manager.join_room(user_id, room_id, websocket)
        
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast_to_room(room_id, data, exclude=[user_id])
        except WebSocketDisconnect:
            await manager.leave_room(user_id, room_id)
    except Exception as e:
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011, reason=str(e))

# ============================================================================
# ROOMS
# ============================================================================

@router.get("/rooms")
async def list_rooms(
    type: Optional[RoomType] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all chat rooms"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        rooms = await manager.get_rooms(
            type=type.value if type else None,
            limit=limit,
            offset=offset
        )
        return {"total": len(rooms), "rooms": rooms}
    except Exception as e:
        return {"total": 0, "rooms": [], "error": str(e)}

@router.post("/rooms")
async def create_room(room: RoomCreate, creator_id: str):
    """Create new chat room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        new_room = await manager.create_room(
            name=room.name,
            type=room.type.value,
            creator_id=creator_id,
            description=room.description,
            max_users=room.max_users
        )
        return {"message": "Room created", "room_id": new_room['id'], "room": new_room}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    """Get room details"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        room = await manager.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rooms/{room_id}")
async def update_room(room_id: str, updates: Dict[str, Any]):
    """Update room settings"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        updated = await manager.update_room(room_id, updates)
        return {"message": "Room updated", "room": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str, user_id: str):
    """Delete room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.delete_room(room_id, user_id)
        return {"message": "Room deleted", "room_id": room_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, user_id: str):
    """Join chat room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.add_user_to_room(room_id, user_id)
        return {"message": "Joined room", "room_id": room_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, user_id: str):
    """Leave chat room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.remove_user_from_room(room_id, user_id)
        return {"message": "Left room", "room_id": room_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms/{room_id}/members")
async def get_room_members(room_id: str):
    """Get room members"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        members = await manager.get_room_members(room_id)
        return {"room_id": room_id, "members": members}
    except Exception as e:
        return {"room_id": room_id, "members": [], "error": str(e)}

# ============================================================================
# MESSAGES
# ============================================================================

@router.get("/rooms/{room_id}/messages")
async def get_room_messages(
    room_id: str,
    limit: int = 100,
    before: Optional[str] = None
):
    """Get room messages"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        messages = await manager.get_messages(room_id, limit=limit, before=before)
        return {"room_id": room_id, "messages": messages}
    except Exception as e:
        return {"room_id": room_id, "messages": [], "error": str(e)}

@router.post("/rooms/{room_id}/messages")
async def send_message(room_id: str, user_id: str, message: MessageCreate):
    """Send message to room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        msg = await manager.send_message(
            room_id=room_id,
            user_id=user_id,
            content=message.content,
            type=message.type.value,
            metadata=message.metadata
        )
        return {"message": "Message sent", "message_data": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, user_id: str):
    """Delete message"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.delete_message(message_id, user_id)
        return {"message": "Message deleted", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/messages/{message_id}")
async def edit_message(message_id: str, user_id: str, new_content: str):
    """Edit message"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        updated = await manager.edit_message(message_id, user_id, new_content)
        return {"message": "Message edited", "message_data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{message_id}/react")
async def add_reaction(message_id: str, user_id: str, emoji: str):
    """Add reaction to message"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.add_reaction(message_id, user_id, emoji)
        return {"message": "Reaction added", "message_id": message_id, "emoji": emoji}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DIRECT MESSAGES
# ============================================================================

@router.get("/dm")
async def list_dm_conversations(user_id: str):
    """Get all DM conversations for user"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        conversations = await manager.get_dm_conversations(user_id)
        return {"user_id": user_id, "conversations": conversations}
    except Exception as e:
        return {"user_id": user_id, "conversations": [], "error": str(e)}

@router.post("/dm")
async def create_dm(user1_id: str, user2_id: str):
    """Create or get DM conversation"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        dm = await manager.create_dm(user1_id, user2_id)
        return {"message": "DM conversation ready", "conversation_id": dm['id'], "conversation": dm}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dm/{conversation_id}/messages")
async def get_dm_messages(conversation_id: str, limit: int = 100):
    """Get DM messages"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        messages = await manager.get_dm_messages(conversation_id, limit=limit)
        return {"conversation_id": conversation_id, "messages": messages}
    except Exception as e:
        return {"conversation_id": conversation_id, "messages": [], "error": str(e)}

@router.post("/dm/{conversation_id}/messages")
async def send_dm(conversation_id: str, user_id: str, content: str):
    """Send DM message"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        msg = await manager.send_dm(conversation_id, user_id, content)
        return {"message": "DM sent", "message_data": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER STATUS & PRESENCE
# ============================================================================

@router.get("/presence/{user_id}")
async def get_user_presence(user_id: str):
    """Get user online status"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        presence = await manager.get_presence(user_id)
        return {"user_id": user_id, "presence": presence}
    except Exception as e:
        return {"user_id": user_id, "presence": {"status": "unknown"}, "error": str(e)}

@router.post("/presence/{user_id}")
async def update_presence(user_id: str, status: UserStatus):
    """Update user status"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.update_presence(user_id, status.value)
        return {"message": "Status updated", "user_id": user_id, "status": status.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/typing/{room_id}")
async def get_typing_users(room_id: str):
    """Get users currently typing in room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        typing = await manager.get_typing_users(room_id)
        return {"room_id": room_id, "typing_users": typing}
    except Exception as e:
        return {"room_id": room_id, "typing_users": [], "error": str(e)}

@router.post("/typing/{room_id}")
async def start_typing(room_id: str, user_id: str):
    """Indicate user is typing"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.start_typing(room_id, user_id)
        return {"message": "Typing started", "room_id": room_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/typing/{room_id}/{user_id}")
async def stop_typing(room_id: str, user_id: str):
    """Stop typing indication"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.stop_typing(room_id, user_id)
        return {"message": "Typing stopped", "room_id": room_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VIDEO CHAT
# ============================================================================

@router.post("/video/call")
async def start_video_call(room_id: str, caller_id: str):
    """Start video call in room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        call = await manager.start_video_call(room_id, caller_id)
        return {"message": "Video call started", "call_id": call['id'], "call": call}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/call/{call_id}/join")
async def join_video_call(call_id: str, user_id: str):
    """Join video call"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.join_video_call(call_id, user_id)
        return {"message": "Joined video call", "call_id": call_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/call/{call_id}/leave")
async def leave_video_call(call_id: str, user_id: str):
    """Leave video call"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.leave_video_call(call_id, user_id)
        return {"message": "Left video call", "call_id": call_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/video/call/{call_id}")
async def end_video_call(call_id: str, user_id: str):
    """End video call"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.end_video_call(call_id, user_id)
        return {"message": "Video call ended", "call_id": call_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MODERATION
# ============================================================================

@router.post("/rooms/{room_id}/mute")
async def mute_user(room_id: str, user_id: str, moderator_id: str, duration: Optional[int] = None):
    """Mute user in room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.mute_user(room_id, user_id, moderator_id, duration)
        return {"message": "User muted", "room_id": room_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_id}/kick")
async def kick_user(room_id: str, user_id: str, moderator_id: str):
    """Kick user from room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.kick_user(room_id, user_id, moderator_id)
        return {"message": "User kicked", "room_id": room_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rooms/{room_id}/ban")
async def ban_user(room_id: str, user_id: str, moderator_id: str):
    """Ban user from room"""
    try:
        from core.platform.websocket_manager_core import WebSocketManagerCore
        manager = WebSocketManagerCore()
        
        await manager.ban_user(room_id, user_id, moderator_id)
        return {"message": "User banned", "room_id": room_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
