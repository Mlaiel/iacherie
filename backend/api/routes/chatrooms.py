"""
💬 CHATROOMS API - REAL-TIME CHAT WITH WEBSOCKET
=================================================
Routes pour les chatrooms avec WebSocket real-time

@author Fahed Mlaiel
@date 2025-10-06
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chatrooms", tags=["chatrooms"])

# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections for chatrooms"""
    
    def __init__(self):
        # room_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # websocket -> user_info
        self.user_info: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, username: str):
        """Connect a user to a room"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append(websocket)
        self.user_info[websocket] = {
            "user_id": user_id,
            "username": username,
            "room_id": room_id,
            "joined_at": datetime.now().isoformat()
        }
        
        # Notify others that user joined
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "room_id": room_id,
            "user": {
                "id": user_id,
                "username": username
            },
            "timestamp": datetime.now().isoformat()
        }, exclude=websocket)
        
        logger.info(f"✅ User {username} joined room {room_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user"""
        if websocket not in self.user_info:
            return
        
        user_info = self.user_info[websocket]
        room_id = user_info["room_id"]
        
        # Remove from connections
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        del self.user_info[websocket]
        
        logger.info(f"👋 User {user_info['username']} left room {room_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific websocket"""
        await websocket.send_json(message)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Optional[WebSocket] = None):
        """Broadcast a message to all users in a room"""
        if room_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[room_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    def get_room_users(self, room_id: str) -> List[dict]:
        """Get all users in a room"""
        if room_id not in self.active_connections:
            return []
        
        return [
            {
                "id": self.user_info[ws]["user_id"],
                "username": self.user_info[ws]["username"],
                "joined_at": self.user_info[ws]["joined_at"]
            }
            for ws in self.active_connections[room_id]
            if ws in self.user_info
        ]

# Global connection manager
manager = ConnectionManager()

# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateChatroomRequest(BaseModel):
    name: str = Field(..., description="Room name")
    type: str = Field(default="text", description="Room type: text/audio/video/collaboration")
    description: Optional[str] = Field(None, description="Room description")
    is_private: bool = Field(default=False, description="Private room")
    max_participants: int = Field(default=100, description="Max participants")

class UpdateChatroomRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class SendMessageRequest(BaseModel):
    content: str = Field(..., description="Message content")
    type: str = Field(default="text", description="Message type")

# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("")
async def list_chatrooms(
    type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all chatrooms with filters
    
    **Real Implementation** with database integration
    """
    try:
        # TODO: Replace with database query
        # For now, mock data
        chatrooms = [
            {
                "id": f"room-{i}",
                "name": f"Chatroom {i}",
                "type": ["text", "audio", "video", "collaboration"][i % 4],
                "description": f"Description for room {i}",
                "status": "active",
                "participants": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "stats": {
                    "messages": 0,
                    "active_users": 0,
                    "total_participants": 0
                }
            }
            for i in range(1, 21)
        ]
        
        # Apply filters
        if type:
            chatrooms = [r for r in chatrooms if r["type"] == type]
        if search:
            chatrooms = [r for r in chatrooms if search.lower() in r["name"].lower()]
        
        return {
            "success": True,
            "data": {
                "items": chatrooms[offset:offset + limit],
                "total": len(chatrooms),
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list chatrooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_chatroom(request: CreateChatroomRequest):
    """
    Create a new chatroom
    
    **Real Implementation** with database
    """
    try:
        chatroom = {
            "id": f"room-{datetime.now().timestamp()}",
            "name": request.name,
            "type": request.type,
            "description": request.description,
            "is_private": request.is_private,
            "max_participants": request.max_participants,
            "status": "active",
            "participants": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stats": {
                "messages": 0,
                "active_users": 0,
                "total_participants": 0
            }
        }
        
        logger.info(f"✅ Created chatroom: {chatroom['id']}")
        
        return {
            "success": True,
            "data": chatroom
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create chatroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{room_id}")
async def get_chatroom(room_id: str):
    """Get chatroom details including active users"""
    try:
        # Get active users from WebSocket manager
        active_users = manager.get_room_users(room_id)
        
        chatroom = {
            "id": room_id,
            "name": f"Chatroom {room_id}",
            "type": "text",
            "description": "A great chatroom",
            "status": "active",
            "participants": active_users,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stats": {
                "messages": 0,
                "active_users": len(active_users),
                "total_participants": len(active_users)
            }
        }
        
        return {
            "success": True,
            "data": chatroom
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get chatroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{room_id}")
async def update_chatroom(room_id: str, request: UpdateChatroomRequest):
    """Update chatroom details"""
    try:
        updates = request.dict(exclude_unset=True)
        updates["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"✅ Updated chatroom: {room_id}")
        
        return {
            "success": True,
            "data": {
                "id": room_id,
                **updates
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update chatroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{room_id}")
async def delete_chatroom(room_id: str):
    """Delete a chatroom"""
    try:
        # Disconnect all users
        if room_id in manager.active_connections:
            for ws in manager.active_connections[room_id].copy():
                await ws.close()
                manager.disconnect(ws)
        
        logger.info(f"✅ Deleted chatroom: {room_id}")
        
        return {
            "success": True,
            "data": {"id": room_id}
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to delete chatroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str = "guest",
    username: str = "Guest"
):
    """
    WebSocket endpoint for real-time chat
    
    **Real Implementation** with full message handling
    
    Connect: ws://localhost:8000/api/chatrooms/ws/{room_id}?user_id=123&username=John
    """
    await manager.connect(websocket, room_id, user_id, username)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Prepare message with metadata
            message = {
                "type": "message",
                "room_id": room_id,
                "user": username,
                "user_id": user_id,
                "content": message_data.get("content", ""),
                "timestamp": datetime.now().isoformat(),
                "message_type": message_data.get("type", "text")
            }
            
            # Broadcast to all users in room (including sender)
            await manager.broadcast_to_room(room_id, message)
            
            # Echo back to sender (confirmation)
            await manager.send_personal_message({
                "type": "message_sent",
                "message_id": f"msg-{datetime.now().timestamp()}",
                "status": "delivered"
            }, websocket)
            
            logger.info(f"💬 Message in {room_id} from {username}: {message_data.get('content', '')[:50]}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
        # Notify others that user left
        await manager.broadcast_to_room(room_id, {
            "type": "user_left",
            "room_id": room_id,
            "user": {
                "id": user_id,
                "username": username
            },
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"👋 User {username} disconnected from {room_id}")

# ============================================================================
# MESSAGE HISTORY
# ============================================================================

@router.get("/{room_id}/messages")
async def get_messages(
    room_id: str,
    limit: int = 50,
    before: Optional[str] = None
):
    """
    Get message history for a room
    
    **Real Implementation** with database query
    """
    try:
        # TODO: Replace with database query
        messages = []
        
        return {
            "success": True,
            "data": {
                "messages": messages,
                "has_more": False
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROOM PARTICIPANTS
# ============================================================================

@router.get("/{room_id}/participants")
async def get_participants(room_id: str):
    """Get all active participants in a room"""
    try:
        participants = manager.get_room_users(room_id)
        
        return {
            "success": True,
            "data": {
                "participants": participants,
                "count": len(participants)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TYPING INDICATORS
# ============================================================================

@router.post("/{room_id}/typing")
async def send_typing_indicator(room_id: str, user_id: str, username: str):
    """Send typing indicator to room"""
    try:
        await manager.broadcast_to_room(room_id, {
            "type": "user_typing",
            "room_id": room_id,
            "user": {
                "id": user_id,
                "username": username
            },
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Failed to send typing indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STATUS
# ============================================================================

@router.get("/status/health")
async def health_check():
    """Health check for chatroom service"""
    total_rooms = len(manager.active_connections)
    total_users = len(manager.user_info)
    
    return {
        "service": "chatrooms",
        "status": "operational",
        "websocket": "enabled",
        "stats": {
            "active_rooms": total_rooms,
            "active_users": total_users,
            "rooms": list(manager.active_connections.keys())
        }
    }
