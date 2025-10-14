"""
Educational Chatroom with WebSocket support
Real-time communication with accessibility features
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set, Optional, List
import json
import logging
from datetime import datetime
from pydantic import BaseModel
import httpx
from eduverify_database import get_db, ChatroomModel, ChatMessageModel
import uuid as uuid_lib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eduverify", tags=["eduverify-chatroom"])


# ============= Schemas =============

class ChatRoomCreate(BaseModel):
    """Schema for creating a chat room"""
    name: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    language: str = "fr"
    max_participants: int = 50
    is_private: bool = False
    accessibility_enabled: bool = True


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    room_id: str
    message: str
    message_type: str = "text"  # text, image, file, code


class TranscriptionRequest(BaseModel):
    """Request for real-time transcription (deaf users)"""
    audio_data: str  # Base64 encoded audio
    language: str = "fr"


# ============= Connection Manager =============

class EducationalChatManager:
    """
    Manages WebSocket connections for educational chatrooms
    
    Features:
    - Multiple chat rooms (by subject, topic, or class)
    - Real-time transcription for deaf users
    - TTS support for blind users
    - Visual alerts and notifications
    - Typing indicators
    - User presence tracking
    """

    def __init__(self):
        # room_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # room_id -> Set[user_id]
        self.room_participants: Dict[str, Set[str]] = {}
        
        # websocket -> user_info
        self.user_info: Dict[WebSocket, Dict] = {}
        
        # Orchestrator URL for accessibility services
        self.orchestrator_url = "http://localhost:8003/orchestrator"
        
        logger.info("📚 EducationalChatManager initialized")

    async def connect(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: str,
        user_name: str,
        accessibility_prefs: Optional[Dict] = None,
    ):
        """Connect user to a chat room"""
        await websocket.accept()
        
        # Initialize room if needed
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            self.room_participants[room_id] = set()
        
        # Add connection
        self.active_connections[room_id].add(websocket)
        self.room_participants[room_id].add(user_id)
        
        # Store user info with accessibility preferences
        self.user_info[websocket] = {
            "user_id": user_id,
            "user_name": user_name,
            "room_id": room_id,
            "joined_at": datetime.now().isoformat(),
            "accessibility": accessibility_prefs or {},
        }
        
        logger.info(
            f"👤 User {user_name} joined room {room_id}. "
            f"Total in room: {len(self.active_connections[room_id])}"
        )

    def disconnect(self, websocket: WebSocket):
        """Disconnect user from chat room"""
        if websocket not in self.user_info:
            return
        
        user_info = self.user_info[websocket]
        room_id = user_info["room_id"]
        user_id = user_info["user_id"]
        
        # Remove connection
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        # Remove participant
        if room_id in self.room_participants:
            self.room_participants[room_id].discard(user_id)
            if not self.room_participants[room_id]:
                del self.room_participants[room_id]
        
        # Remove user info
        del self.user_info[websocket]
        
        logger.info(f"👤 User {user_info['user_name']} left room {room_id}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific user"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Error sending personal message: {e}")

    async def broadcast(
        self,
        message: Dict,
        room_id: str,
        exclude: Optional[WebSocket] = None,
        accessibility_enhanced: bool = True,
    ):
        """
        Broadcast message to all users in a room
        
        Args:
            message: Message to broadcast
            room_id: Chat room ID
            exclude: WebSocket to exclude (usually sender)
            accessibility_enhanced: Apply accessibility features
        """
        if room_id not in self.active_connections:
            return

        # Enhance message with accessibility features if needed
        if accessibility_enhanced:
            message = await self._enhance_with_accessibility(message, room_id)

        message_str = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections[room_id]:
            if exclude and connection == exclude:
                continue
            
            try:
                # Check user's accessibility preferences
                user_prefs = self.user_info.get(connection, {}).get("accessibility", {})
                
                # Customize message based on preferences
                custom_message = await self._customize_for_user(message, user_prefs)
                
                await connection.send_text(json.dumps(custom_message))
            except Exception as e:
                logger.error(f"❌ Error broadcasting: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def _enhance_with_accessibility(
        self, message: Dict, room_id: str
    ) -> Dict:
        """
        Enhance message with accessibility features
        
        - Generate TTS audio for blind users
        - Add visual indicators for deaf users
        - Provide text alternatives for media
        """
        message_type = message.get("type", "message")
        
        if message_type == "message":
            content = message.get("content", "")
            
            # Add TTS audio URL (for blind users)
            if content:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.orchestrator_url}/accessibility/tts",
                            json={
                                "text": content,
                                "language": message.get("language", "fr"),
                            },
                            timeout=5.0,
                        )
                        if response.status_code == 200:
                            tts_data = response.json()
                            message["tts_audio_url"] = tts_data.get("audio_url")
                except Exception as e:
                    logger.warning(f"⚠️ TTS generation failed: {e}")
            
            # Add visual indicator (for deaf users)
            message["visual_indicator"] = {
                "color": "#3B82F6",
                "icon": "message",
                "vibrate": False,
            }
        
        elif message_type == "alert":
            # Generate visual alert (for deaf users)
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.orchestrator_url}/accessibility/visual-alert",
                        json={
                            "alert_type": message.get("alert_type", "notification"),
                            "message": message.get("content", ""),
                            "priority": message.get("priority", "normal"),
                        },
                        timeout=5.0,
                    )
                    if response.status_code == 200:
                        alert_data = response.json()
                        message["visual_alert"] = alert_data
            except Exception as e:
                logger.warning(f"⚠️ Visual alert generation failed: {e}")
        
        return message

    async def _customize_for_user(
        self, message: Dict, user_prefs: Dict
    ) -> Dict:
        """
        Customize message based on user's accessibility preferences
        """
        customized = message.copy()
        
        # If user has screen reader enabled, ensure alt text is present
        if user_prefs.get("screen_reader"):
            if "image_url" in customized and "alt_text" not in customized:
                customized["alt_text"] = "Image partagée dans le chat"
        
        # If user prefers visual alerts only, enhance visual components
        if user_prefs.get("visual_alerts_only"):
            if "visual_indicator" in customized:
                customized["visual_indicator"]["emphasized"] = True
        
        # If user has captions enabled, add transcription
        if user_prefs.get("captions_enabled"):
            customized["show_captions"] = True
        
        return customized

    def get_room_participants(self, room_id: str) -> List[Dict]:
        """Get list of participants in a room"""
        participants = []
        
        if room_id not in self.active_connections:
            return participants
        
        for connection in self.active_connections[room_id]:
            if connection in self.user_info:
                user = self.user_info[connection]
                participants.append({
                    "user_id": user["user_id"],
                    "user_name": user["user_name"],
                    "joined_at": user["joined_at"],
                    "accessibility_enabled": bool(user.get("accessibility")),
                })
        
        return participants


# Singleton instance
chat_manager = EducationalChatManager()


# ============= WebSocket Endpoints =============

@router.websocket("/ws/chatroom")
async def websocket_chatroom_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str,
    user_name: str,
    screen_reader: bool = False,
    captions: bool = False,
    visual_alerts: bool = False,
):
    """
    WebSocket endpoint for educational chatroom
    
    **Query Parameters:**
    - room_id: Chat room identifier (e.g., "math_101", "science_advanced")
    - user_id: User identifier
    - user_name: Display name
    - screen_reader: Enable screen reader support (blind users)
    - captions: Enable real-time captions (deaf users)
    - visual_alerts: Enable visual alerts instead of audio (deaf users)
    
    **Message Types:**
    - message: Regular text message
    - typing: Typing indicator
    - voice: Voice message (auto-transcribed for deaf users)
    - image: Image with alt text for screen readers
    - code: Code snippet with syntax highlighting
    - question: Question from student
    - answer: Answer from teacher/peer
    """
    
    # Build accessibility preferences
    accessibility_prefs = {
        "screen_reader": screen_reader,
        "captions_enabled": captions,
        "visual_alerts_only": visual_alerts,
    }
    
    await chat_manager.connect(
        websocket, room_id, user_id, user_name, accessibility_prefs
    )

    # Send join notification
    join_message = {
        "type": "user_joined",
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": datetime.now().isoformat(),
        "accessibility_enabled": any(accessibility_prefs.values()),
    }
    await chat_manager.broadcast(join_message, room_id, exclude=websocket)

    # Send welcome message
    welcome_message = {
        "type": "system",
        "content": f"Bienvenue dans la salle {room_id}, {user_name}! 🎓",
        "timestamp": datetime.now().isoformat(),
        "participants_count": len(chat_manager.room_participants.get(room_id, [])),
    }
    await chat_manager.send_personal_message(welcome_message, websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Add metadata
            message_data["timestamp"] = datetime.now().isoformat()
            message_data["user_id"] = user_id
            message_data["user_name"] = user_name
            message_data["room_id"] = room_id

            message_type = message_data.get("type", "message")

            # Handle different message types
            if message_type == "typing":
                # Typing indicator (not stored, ephemeral)
                typing_msg = {
                    "type": "typing",
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": message_data.get("is_typing", True),
                }
                await chat_manager.broadcast(
                    typing_msg, room_id, exclude=websocket, accessibility_enhanced=False
                )

            elif message_type == "message":
                # Regular message
                chat_message = {
                    "type": "message",
                    "id": f"msg_{datetime.now().timestamp()}",
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": message_data.get("content", ""),
                    "message_type": message_data.get("message_type", "text"),
                    "language": message_data.get("language", "fr"),
                    "timestamp": message_data["timestamp"],
                }
                
                # TODO: Store in database
                
                # Broadcast with accessibility enhancements
                await chat_manager.broadcast(chat_message, room_id)

            elif message_type == "voice":
                # Voice message - auto-transcribe for deaf users
                voice_msg = {
                    "type": "message",
                    "id": f"msg_{datetime.now().timestamp()}",
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": message_data.get("content", ""),
                    "message_type": "voice",
                    "audio_url": message_data.get("audio_url"),
                    "transcription": message_data.get("transcription", ""),  # Auto-generated
                    "timestamp": message_data["timestamp"],
                }
                
                # TODO: Auto-generate transcription via orchestrator STT
                
                await chat_manager.broadcast(voice_msg, room_id)

            elif message_type == "question":
                # Student question (highlighted for teachers)
                question_msg = {
                    "type": "question",
                    "id": f"q_{datetime.now().timestamp()}",
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": message_data.get("content", ""),
                    "subject": message_data.get("subject"),
                    "priority": message_data.get("priority", "normal"),
                    "timestamp": message_data["timestamp"],
                }
                await chat_manager.broadcast(question_msg, room_id)

            elif message_type == "answer":
                # Answer to a question
                answer_msg = {
                    "type": "answer",
                    "id": f"a_{datetime.now().timestamp()}",
                    "user_id": user_id,
                    "user_name": user_name,
                    "content": message_data.get("content", ""),
                    "question_id": message_data.get("question_id"),
                    "is_teacher": message_data.get("is_teacher", False),
                    "timestamp": message_data["timestamp"],
                }
                await chat_manager.broadcast(answer_msg, room_id)

            else:
                logger.warning(f"⚠️ Unknown message type: {message_type}")

    except WebSocketDisconnect:
        chat_manager.disconnect(websocket)
        
        # Notify others
        leave_message = {
            "type": "user_left",
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.now().isoformat(),
        }
        await chat_manager.broadcast(
            leave_message, room_id, accessibility_enhanced=False
        )

    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        chat_manager.disconnect(websocket)


# ============= REST Endpoints =============

@router.post("/chatrooms", status_code=201)
async def create_chatroom(room: ChatRoomCreate):
    """
    Create a new educational chatroom
    
    **Example:**
    ```json
    {
        "name": "Mathématiques Avancées",
        "subject": "mathematics",
        "topic": "calculus",
        "language": "fr",
        "max_participants": 30,
        "is_private": false,
        "accessibility_enabled": true
    }
    ```
    """
    # TODO: Store in database
    from uuid import uuid4
    
    room_id = str(uuid4())
    
    return {
        "id": room_id,
        "name": room.name,
        "subject": room.subject,
        "topic": room.topic,
        "language": room.language,
        "max_participants": room.max_participants,
        "is_private": room.is_private,
        "accessibility_enabled": room.accessibility_enabled,
        "created_at": datetime.now().isoformat(),
        "websocket_url": f"/ws/chatroom?room_id={room_id}",
    }


@router.get("/chatrooms")
async def get_chatrooms(db: Session = Depends(get_db)):
    """
    Get list of all available chatrooms - REAL DATABASE QUERY
    """
    try:
        # REAL DATABASE QUERY
        rooms = db.query(ChatroomModel).filter(ChatroomModel.is_active == True).all()
        
        items = []
        for room in rooms:
            items.append({
                "id": str(room.id),
                "name": room.name,
                "description": f"{room.subject} - {room.topic}" if room.subject else room.name,
                "active_users": len(chat_manager.get_room_participants(room.room_id))
            })
        
        # If no rooms in DB, return default rooms
        if not items:
            items = [
                {
                    "id": "general",
                    "name": "Discussion Générale",
                    "description": "Salle de discussion générale pour tous les sujets",
                    "active_users": len(chat_manager.get_room_participants("general"))
                },
                {
                    "id": "mathematics",
                    "name": "Mathématiques",
                    "description": "Aide et discussions sur les mathématiques",
                    "active_users": len(chat_manager.get_room_participants("mathematics"))
                },
                {
                    "id": "science",
                    "name": "Sciences",
                    "description": "Physique, chimie, biologie",
                    "active_users": len(chat_manager.get_room_participants("science"))
                },
                {
                    "id": "languages",
                    "name": "Langues",
                    "description": "Apprentissage des langues étrangères",
                    "active_users": len(chat_manager.get_room_participants("languages"))
                }
            ]
        
        return {"items": items}
    except Exception as e:
        logger.error(f"Failed to fetch chatrooms: {e}")
        # Return default rooms as fallback
        return {
            "items": [
                {
                    "id": "general",
                    "name": "Discussion Générale",
                    "description": "Salle de discussion générale",
                    "active_users": 0
                }
            ]
        }


@router.get("/chatrooms/{room_id}/messages")
async def get_chatroom_messages(
    room_id: str,
    limit: int = 50,
    offset: int = 0,
):
    """
    Get chat message history for a room
    
    Includes accessibility metadata:
    - TTS audio URLs for blind users
    - Transcriptions for deaf users
    - Alt text for images
    """
    # TODO: Fetch from database
    return {
        "room_id": room_id,
        "messages": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@router.get("/chatrooms/{room_id}/participants")
async def get_chatroom_participants(room_id: str):
    """
    Get active participants in a chatroom
    """
    participants = chat_manager.get_room_participants(room_id)
    
    return {
        "room_id": room_id,
        "participants": participants,
        "count": len(participants),
    }


@router.post("/chatrooms/{room_id}/transcribe")
async def transcribe_voice_message(
    room_id: str,
    request: TranscriptionRequest,
):
    """
    Transcribe voice message for deaf users
    
    Sends audio to orchestrator STT service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8003/orchestrator/accessibility/stt",
                json={
                    "audio_url": request.audio_data,
                    "language": request.language,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Transcription service unavailable"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
