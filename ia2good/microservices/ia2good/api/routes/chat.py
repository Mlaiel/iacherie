"""
WebSocket chat endpoint for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import logging
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.case import Case

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    case_id: str
    message: str


# Store active WebSocket connections by case ID
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, case_id: str):
        await websocket.accept()
        if case_id not in self.active_connections:
            self.active_connections[case_id] = set()
        self.active_connections[case_id].add(websocket)
        logger.info(f"Client connected to case {case_id}. Total connections: {len(self.active_connections[case_id])}")

    def disconnect(self, websocket: WebSocket, case_id: str):
        if case_id in self.active_connections:
            self.active_connections[case_id].discard(websocket)
            if not self.active_connections[case_id]:
                del self.active_connections[case_id]
        logger.info(f"Client disconnected from case {case_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict, case_id: str, exclude: WebSocket = None):
        """Broadcast message to all connections in a case room except the sender"""
        if case_id not in self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections[case_id]:
            if exclude and connection == exclude:
                continue
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, case_id)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    case_id: str = None,
    user_id: str = None,
    user_name: str = None,
):
    """
    WebSocket endpoint for real-time chat
    
    Query Parameters:
    - case_id: ID of the case to join chat for
    - user_id: ID of the current user
    - user_name: Name of the current user
    """
    if not case_id:
        await websocket.close(code=1008, reason="case_id is required")
        return

    if not user_id or not user_name:
        await websocket.close(code=1008, reason="user_id and user_name are required")
        return

    await manager.connect(websocket, case_id)

    # Send join notification to other users
    join_message = {
        "type": "user_joined",
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(join_message, case_id, exclude=websocket)

    # Send welcome message to the connecting user
    welcome_message = {
        "type": "system",
        "message": f"Welcome to case {case_id} chat",
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.send_personal_message(json.dumps(welcome_message), websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Add metadata
            message_data["timestamp"] = datetime.utcnow().isoformat()
            message_data["user_id"] = user_id
            message_data["user_name"] = user_name

            # Handle different message types
            message_type = message_data.get("type", "message")

            if message_type == "typing":
                # Broadcast typing indicator (not stored)
                typing_message = {
                    "type": "typing",
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": message_data.get("is_typing", True),
                }
                await manager.broadcast(typing_message, case_id, exclude=websocket)

            elif message_type == "message":
                # Broadcast regular message to all users
                chat_message = {
                    "type": "message",
                    "id": f"msg_{datetime.utcnow().timestamp()}",
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": message_data.get("content", ""),
                    "message_type": message_data.get("message_type", "text"),
                    "timestamp": message_data["timestamp"],
                }
                
                # TODO: Store message in database
                # await store_message(case_id, chat_message)

                await manager.broadcast(chat_message, case_id)

            elif message_type == "read_receipt":
                # Broadcast read receipt
                read_message = {
                    "type": "read_receipt",
                    "message_id": message_data.get("message_id"),
                    "user_id": user_id,
                    "timestamp": message_data["timestamp"],
                }
                await manager.broadcast(read_message, case_id, exclude=websocket)

            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, case_id)
        
        # Notify other users
        leave_message = {
            "type": "user_left",
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await manager.broadcast(leave_message, case_id)
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, case_id)


@router.get("/chat/rooms/{case_id}/messages")
async def get_chat_messages(
    case_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get chat message history for a case
    
    TODO: Implement database storage for messages
    """
    # For now, return empty list
    # In production, query messages from database
    return {
        "case_id": case_id,
        "messages": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@router.post("/chat/messages")
async def send_chat_message(
    payload: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a chat message to a case (REST endpoint)
    
    For clients that can't use WebSocket - no auth required for testing
    """
    # Verify case exists
    case = db.query(Case).filter(Case.id == payload.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Create message object
    message_data = {
        "case_id": payload.case_id,
        "user_id": "test_user",
        "user_name": "Test User",
        "message": payload.message,
        "timestamp": datetime.utcnow().isoformat(),
        "type": "text"
    }
    
    # Broadcast to WebSocket connections if manager exists
    try:
        await manager.broadcast(message_data, payload.case_id)
    except:
        pass  # No active connections
    
    return {
        "id": f"msg_{datetime.utcnow().timestamp()}",
        "case_id": payload.case_id,
        "message": payload.message,
        "timestamp": message_data["timestamp"],
        "status": "sent"
    }


@router.get("/chat/rooms/{case_id}/participants")
async def get_chat_participants(case_id: str):
    """
    Get active participants in a chat room
    """
    if case_id not in manager.active_connections:
        return {"case_id": case_id, "participants": [], "count": 0}

    return {
        "case_id": case_id,
        "count": len(manager.active_connections[case_id]),
        "participants": [],  # TODO: Track participant info
    }
