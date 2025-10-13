"""
Guardian Chat Routes
Text chat rooms and direct messaging for volunteers
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from moderation import get_moderator, ModerationResult
from rate_limiting import get_rate_limiter, RateLimitExceeded, check_rate_limit
from audit import get_audit_logger, AuditAction, AuditLevel

router = APIRouter()

# Models
class ChatRoom(BaseModel):
    room_id: str
    name: str
    description: Optional[str] = None
    mission_id: Optional[int] = None
    is_public: bool = True
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None

class ChatMessage(BaseModel):
    message_id: str
    room_id: str
    user_id: str
    username: str
    message: str
    timestamp: datetime
    edited: bool = False

class DirectMessage(BaseModel):
    message_id: str
    from_user: str
    to_user: str
    message: str
    timestamp: datetime
    read: bool = False

# Storage
chat_rooms: Dict[str, ChatRoom] = {}
room_messages: Dict[str, List[ChatMessage]] = {}  # room_id -> messages
room_connections: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> {user_id -> websocket}
direct_messages: Dict[str, List[DirectMessage]] = {}  # user_id -> messages
dm_connections: Dict[str, WebSocket] = {}  # user_id -> websocket

# ============================================================================
# CHAT ROOMS MANAGEMENT
# ============================================================================

@router.post("/rooms/create")
def create_chat_room(room: ChatRoom):
    """Créer une salle de chat"""
    if not room.room_id:
        room.room_id = str(uuid.uuid4())
    
    room.created_at = datetime.utcnow()
    chat_rooms[room.room_id] = room
    room_messages[room.room_id] = []
    room_connections[room.room_id] = {}
    
    return {
        "success": True,
        "room": room.dict()
    }

@router.get("/rooms")
def list_chat_rooms(mission_id: Optional[int] = None):
    """Lister toutes les salles de chat"""
    rooms_list = list(chat_rooms.values())
    
    if mission_id is not None:
        rooms_list = [r for r in rooms_list if r.mission_id == mission_id]
    
    # Add participant count
    rooms_with_info = []
    for room in rooms_list:
        room_dict = room.dict()
        room_dict["participants"] = len(room_connections.get(room.room_id, {}))
        room_dict["messages_count"] = len(room_messages.get(room.room_id, []))
        rooms_with_info.append(room_dict)
    
    return {
        "success": True,
        "total": len(rooms_with_info),
        "rooms": rooms_with_info
    }

@router.get("/rooms/{room_id}")
def get_chat_room(room_id: str):
    """Obtenir les infos d'une salle"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = chat_rooms[room_id]
    messages = room_messages.get(room_id, [])
    participants = len(room_connections.get(room_id, {}))
    
    return {
        "success": True,
        "room": room.dict(),
        "messages_count": len(messages),
        "participants": participants
    }

@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50):
    """Obtenir les messages d'une salle"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = room_messages.get(room_id, [])
    # Return last N messages
    recent_messages = messages[-limit:] if len(messages) > limit else messages
    
    return {
        "success": True,
        "room_id": room_id,
        "total": len(messages),
        "messages": [m.dict() for m in recent_messages]
    }

@router.delete("/rooms/{room_id}")
def delete_chat_room(room_id: str):
    """Supprimer une salle de chat"""
    if room_id not in chat_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Disconnect all users
    connections = room_connections.get(room_id, {})
    for ws in connections.values():
        try:
            import asyncio
            asyncio.create_task(ws.close())
        except:
            pass
    
    # Delete room data
    del chat_rooms[room_id]
    if room_id in room_messages:
        del room_messages[room_id]
    if room_id in room_connections:
        del room_connections[room_id]
    
    return {
        "success": True,
        "message": "Room deleted"
    }

# ============================================================================
# CHAT ROOM WebSocket
# ============================================================================

@router.websocket("/room/{room_id}")
async def chat_room_websocket(websocket: WebSocket, room_id: str):
    """WebSocket pour chat en temps réel"""
    await websocket.accept()
    
    # Check if room exists
    if room_id not in chat_rooms:
        await websocket.send_json({"error": "Room not found"})
        await websocket.close()
        return
    
    user_id = None
    
    try:
        # Wait for user identification
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") != "join":
            await websocket.send_json({"error": "Must send join message first"})
            await websocket.close()
            return
        
        user_id = message.get("user_id") or str(uuid.uuid4())
        username = message.get("username") or f"User_{user_id[:8]}"
        
        # Rate limit: WebSocket connections
        rate_limiter = get_rate_limiter()
        if not rate_limiter.check_rate_limit(f"ws_connect:{user_id}", 20, 60):
            await websocket.send_json({"error": "Too many connections. Please try again later."})
            await websocket.close()
            return
        
        # Add user to room
        if room_id not in room_connections:
            room_connections[room_id] = {}
        room_connections[room_id][user_id] = websocket
        
        # Audit log
        audit_logger = get_audit_logger()
        audit_logger.log(
            AuditAction.ROOM_JOINED,
            user_id=user_id,
            username=username,
            resource_type="chat_room",
            resource_id=room_id
        )
        
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "room_id": room_id,
            "user_id": user_id,
            "room_name": chat_rooms[room_id].name
        })
        
        # Notify others
        await broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=user_id)
        
        # Main message loop
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "message":
                msg_text = message.get("message", "")
                
                # Rate limit: Messages
                rate_limiter = get_rate_limiter()
                if not rate_limiter.check_rate_limit(f"chat_msg:{user_id}", 100, 60):
                    await websocket.send_json({
                        "type": "error",
                        "message": "Too many messages. Please slow down."
                    })
                    continue
                
                # Moderate content
                moderator = get_moderator()
                moderation_result = moderator.moderate_text(msg_text, strict=False)
                
                if moderation_result.suggested_action == "block":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message blocked by moderation",
                        "reasons": moderation_result.reasons
                    })
                    
                    # Audit log
                    audit_logger = get_audit_logger()
                    audit_logger.log(
                        AuditAction.CONTENT_BLOCKED,
                        level=AuditLevel.WARNING,
                        user_id=user_id,
                        username=username,
                        resource_type="chat_message",
                        details={
                            "room_id": room_id,
                            "reasons": moderation_result.reasons,
                            "flagged_words": moderation_result.flagged_words
                        }
                    )
                    continue
                
                # Filter profanity if warned
                if moderation_result.suggested_action == "warn":
                    msg_text = moderator.filter_text(msg_text)
                
                # Create message
                chat_message = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    room_id=room_id,
                    user_id=user_id,
                    username=username,
                    message=msg_text,
                    timestamp=datetime.utcnow()
                )
                
                # Store message
                if room_id not in room_messages:
                    room_messages[room_id] = []
                room_messages[room_id].append(chat_message)
                
                # Audit log
                audit_logger = get_audit_logger()
                audit_logger.log(
                    AuditAction.MESSAGE_SENT,
                    user_id=user_id,
                    username=username,
                    resource_type="chat_message",
                    resource_id=chat_message.message_id,
                    details={"room_id": room_id}
                )
                
                # Broadcast to room
                await broadcast_to_room(room_id, {
                    "type": "message",
                    **chat_message.dict()
                })
            
            elif msg_type == "typing":
                # Broadcast typing indicator
                await broadcast_to_room(room_id, {
                    "type": "typing",
                    "user_id": user_id,
                    "username": username
                }, exclude=user_id)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Chat WebSocket error: {e}")
    finally:
        # Remove user from room
        if user_id and room_id in room_connections and user_id in room_connections[room_id]:
            del room_connections[room_id][user_id]
            
            # Notify others
            await broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })

# ============================================================================
# DIRECT MESSAGES
# ============================================================================

@router.websocket("/dm/{user_id}")
async def direct_message_websocket(websocket: WebSocket, user_id: str):
    """WebSocket pour messages directs"""
    await websocket.accept()
    
    # Register connection
    dm_connections[user_id] = websocket
    
    # Send welcome
    await websocket.send_json({
        "type": "dm_ready",
        "user_id": user_id
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "dm":
                to_user = message.get("to_user")
                msg_text = message.get("message")
                
                # Create DM
                dm = DirectMessage(
                    message_id=str(uuid.uuid4()),
                    from_user=user_id,
                    to_user=to_user,
                    message=msg_text,
                    timestamp=datetime.utcnow()
                )
                
                # Store for both users
                if user_id not in direct_messages:
                    direct_messages[user_id] = []
                if to_user not in direct_messages:
                    direct_messages[to_user] = []
                
                direct_messages[user_id].append(dm)
                direct_messages[to_user].append(dm)
                
                # Send to recipient if online
                if to_user in dm_connections:
                    await dm_connections[to_user].send_json({
                        "type": "dm",
                        **dm.dict()
                    })
                
                # Confirm to sender
                await websocket.send_json({
                    "type": "dm_sent",
                    "message_id": dm.message_id
                })
    
    except WebSocketDisconnect:
        pass
    finally:
        if user_id in dm_connections:
            del dm_connections[user_id]

@router.get("/dm/{user_id}/messages")
def get_direct_messages(user_id: str, with_user: Optional[str] = None):
    """Obtenir les messages directs d'un utilisateur"""
    messages = direct_messages.get(user_id, [])
    
    if with_user:
        # Filter messages with specific user
        messages = [
            m for m in messages 
            if (m.from_user == with_user or m.to_user == with_user)
        ]
    
    return {
        "success": True,
        "user_id": user_id,
        "total": len(messages),
        "messages": [m.dict() for m in messages]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def broadcast_to_room(room_id: str, message: dict, exclude: Optional[str] = None):
    """Envoyer un message à tous les utilisateurs d'une salle"""
    if room_id not in room_connections:
        return
    
    for uid, ws in room_connections[room_id].items():
        if uid != exclude:
            try:
                await ws.send_json(message)
            except:
                pass

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats")
def get_chat_stats():
    """Obtenir les statistiques du chat"""
    total_rooms = len(chat_rooms)
    total_messages = sum(len(messages) for messages in room_messages.values())
    total_connections = sum(len(connections) for connections in room_connections.values())
    total_dms = sum(len(messages) for messages in direct_messages.values())
    
    return {
        "success": True,
        "total_rooms": total_rooms,
        "total_messages": total_messages,
        "active_connections": total_connections,
        "total_direct_messages": total_dms,
        "timestamp": datetime.utcnow().isoformat()
    }
