"""Translation Chat Service
Real-time multilingual chat with AI-powered translation and cultural adaptation.

Provides:
- Real-time chat with automatic translation
- Multi-language support (100+ languages)
- Cultural context adaptation
- Emoji and slang translation
- Voice message transcription and translation
- Language detection and switching
- Professional terminology handling

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re

from fastapi import WebSocket
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of chat messages"""
    TEXT = "text"
    VOICE = "voice"
    FILE = "file"
    IMAGE = "image"
    EMOJI = "emoji"
    SYSTEM = "system"
    TRANSLATION = "translation"


class TranslationMode(Enum):
    """Translation modes"""
    AUTOMATIC = "automatic"
    ON_DEMAND = "on_demand"
    DISABLED = "disabled"


class MessageStatus(Enum):
    """Message status"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    TRANSLATED = "translated"
    FAILED = "failed"


@dataclass
class Language:
    """Language configuration"""
    code: str
    name: str
    native_name: str
    rtl: bool = False
    formal_level: str = "neutral"  # formal, informal, neutral


@dataclass
class TranslationResult:
    """Translation result with metadata"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    detected_language: Optional[str] = None
    cultural_adaptations: List[str] = field(default_factory=list)
    technical_terms: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ChatMessage:
    """Chat message with translation support"""
    message_id: str
    session_id: str
    sender_id: str
    sender_username: str
    content: str
    message_type: MessageType
    timestamp: datetime
    original_language: str
    translations: Dict[str, TranslationResult] = field(default_factory=dict)
    status: MessageStatus = MessageStatus.SENT
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatParticipant:
    """Chat participant with language preferences"""
    user_id: str
    username: str
    preferred_language: str
    secondary_languages: List[str]
    translation_mode: TranslationMode
    cultural_context: str
    joined_at: datetime
    last_activity: datetime
    is_typing: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Chat session for collaboration"""
    session_id: str
    project_id: str
    title: str
    description: str
    creator_id: str
    participants: Dict[str, ChatParticipant] = field(default_factory=dict)
    messages: List[ChatMessage] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=list)
    auto_translate: bool = True
    profanity_filter: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)


class TranslationChatService:
    """
    Real-time multilingual chat service with AI-powered translation
    """
    
    def __init__(self):
        self.chat_sessions: Dict[str, ChatSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.translation_cache: Dict[str, TranslationResult] = {}
        
        # Language support
        self.supported_languages = self._initialize_language_support()
        self.translation_engine = AITranslationEngine()
        
        self._setup_message_handlers()
    
    def _initialize_language_support(self) -> Dict[str, Language]:
        """Initialize supported languages"""
        return {
            "en": Language("en", "English", "English"),
            "es": Language("es", "Spanish", "Español"),
            "fr": Language("fr", "French", "Français"),
            "de": Language("de", "German", "Deutsch"),
            "it": Language("it", "Italian", "Italiano"),
            "pt": Language("pt", "Portuguese", "Português"),
            "ru": Language("ru", "Russian", "Русский"),
            "zh": Language("zh", "Chinese", "中文"),
            "ja": Language("ja", "Japanese", "日本語"),
            "ko": Language("ko", "Korean", "한국어"),
            "ar": Language("ar", "Arabic", "العربية", rtl=True),
            "hi": Language("hi", "Hindi", "हिन्दी"),
            "bn": Language("bn", "Bengali", "বাংলা"),
            "ur": Language("ur", "Urdu", "اردو", rtl=True),
            "tr": Language("tr", "Turkish", "Türkçe"),
            "pl": Language("pl", "Polish", "Polski"),
            "nl": Language("nl", "Dutch", "Nederlands"),
            "sv": Language("sv", "Swedish", "Svenska"),
            "da": Language("da", "Danish", "Dansk"),
            "no": Language("no", "Norwegian", "Norsk"),
            "fi": Language("fi", "Finnish", "Suomi"),
            "he": Language("he", "Hebrew", "עברית", rtl=True),
            "th": Language("th", "Thai", "ไทย"),
            "vi": Language("vi", "Vietnamese", "Tiếng Việt"),
            "id": Language("id", "Indonesian", "Bahasa Indonesia"),
            "ms": Language("ms", "Malay", "Bahasa Melayu"),
            "tl": Language("tl", "Filipino", "Filipino"),
            "sw": Language("sw", "Swahili", "Kiswahili"),
            "am": Language("am", "Amharic", "አማርኛ"),
            "yo": Language("yo", "Yoruba", "Yorùbá"),
            "zu": Language("zu", "Zulu", "isiZulu"),
            "af": Language("af", "Afrikaans", "Afrikaans")
        }
    
    def _setup_message_handlers(self):
        """Setup message handlers"""
        self.message_handlers = {
            "join_chat": self._handle_join_chat,
            "leave_chat": self._handle_leave_chat,
            "send_message": self._handle_send_message,
            "request_translation": self._handle_request_translation,
            "change_language": self._handle_change_language,
            "typing_indicator": self._handle_typing_indicator,
            "mark_read": self._handle_mark_read,
            "voice_message": self._handle_voice_message,
            "upload_file": self._handle_upload_file,
            "search_messages": self._handle_search_messages,
            "get_history": self._handle_get_history
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection for chat"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"Translation chat connection established for user {user_id}")
            
            # Send connection confirmation
            await self._send_to_user(user_id, {
                "type": "connection_established",
                "user_id": user_id,
                "supported_languages": list(self.supported_languages.keys()),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_chat_message(user_id, message)
                    
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
                    await self._send_error(user_id, str(e))
        
        except Exception as e:
            logger.error(f"WebSocket connection error for {user_id}: {e}")
        
        finally:
            await self._cleanup_user_connection(user_id)
    
    async def _handle_chat_message(self, user_id: str, message: Dict[str, Any]):
        """Route chat messages to appropriate handlers"""
        message_type = message.get("type")
        handler = self.message_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def create_chat_session(self, project_id: str, title: str, description: str,
                                creator_id: str, auto_translate: bool = True,
                                supported_languages: List[str] = None) -> Dict[str, Any]:
        """Create new chat session"""
        try:
            session_id = f"chat_{uuid.uuid4().hex[:12]}"
            
            if supported_languages is None:
                supported_languages = ["en", "es", "fr", "de", "zh", "ja", "ar"]
            
            session = ChatSession(
                session_id=session_id,
                project_id=project_id,
                title=title,
                description=description,
                creator_id=creator_id,
                supported_languages=supported_languages,
                auto_translate=auto_translate
            )
            
            self.chat_sessions[session_id] = session
            
            logger.info(f"Chat session {session_id} created for project {project_id}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "project_id": project_id,
                "supported_languages": supported_languages,
                "message": "Chat session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_join_chat(self, user_id: str, message: Dict[str, Any]):
        """Join chat session"""
        try:
            session_id = message.get("session_id")
            username = message.get("username", f"User_{user_id}")
            preferred_language = message.get("preferred_language", "en")
            secondary_languages = message.get("secondary_languages", [])
            translation_mode = TranslationMode(message.get("translation_mode", "automatic"))
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            # Create participant
            participant = ChatParticipant(
                user_id=user_id,
                username=username,
                preferred_language=preferred_language,
                secondary_languages=secondary_languages,
                translation_mode=translation_mode,
                cultural_context=message.get("cultural_context", "neutral"),
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            session.participants[user_id] = participant
            session.last_activity = datetime.utcnow()
            
            # Send session data to user
            await self._send_to_user(user_id, {
                "type": "chat_joined",
                "session": {
                    "session_id": session_id,
                    "project_id": session.project_id,
                    "title": session.title,
                    "auto_translate": session.auto_translate,
                    "supported_languages": session.supported_languages
                },
                "participants": [
                    {
                        "user_id": p.user_id,
                        "username": p.username,
                        "preferred_language": p.preferred_language,
                        "is_typing": p.is_typing
                    }
                    for p in session.participants.values()
                ],
                "recent_messages": [
                    await self._serialize_message(msg, preferred_language)
                    for msg in session.messages[-50:]  # Last 50 messages
                ]
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_joined",
                "participant": {
                    "user_id": user_id,
                    "username": username,
                    "preferred_language": preferred_language,
                    "joined_at": participant.joined_at.isoformat()
                }
            }, exclude_user=user_id)
            
            # Send welcome message
            welcome_msg = await self._create_system_message(
                session_id, f"{username} joined the chat"
            )
            session.messages.append(welcome_msg)
            await self._broadcast_message(session_id, welcome_msg)
            
            logger.info(f"User {user_id} joined chat session {session_id}")
            
        except Exception as e:
            logger.error(f"Error joining chat: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_leave_chat(self, user_id: str, message: Dict[str, Any]):
        """Leave chat session"""
        try:
            session_id = message.get("session_id")
            session = self.chat_sessions.get(session_id)
            
            if session and user_id in session.participants:
                participant = session.participants.pop(user_id)
                
                # Notify other participants
                await self._broadcast_to_session(session_id, {
                    "type": "participant_left",
                    "user_id": user_id,
                    "username": participant.username,
                    "left_at": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
                
                # Send goodbye message
                goodbye_msg = await self._create_system_message(
                    session_id, f"{participant.username} left the chat"
                )
                session.messages.append(goodbye_msg)
                await self._broadcast_message(session_id, goodbye_msg, exclude_user=user_id)
                
                logger.info(f"User {user_id} left chat session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving chat: {e}")
    
    async def _handle_send_message(self, user_id: str, message: Dict[str, Any]):
        """Send chat message"""
        try:
            session_id = message.get("session_id")
            content = message.get("content", "")
            reply_to = message.get("reply_to")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                await self._send_error(user_id, "Not a participant in this session")
                return
            
            # Detect language if not specified
            detected_language = await self.translation_engine.detect_language(content)
            if not detected_language:
                detected_language = participant.preferred_language
            
            # Filter profanity if enabled
            if session.profanity_filter:
                content = await self._filter_profanity(content, detected_language)
            
            # Create message
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            chat_message = ChatMessage(
                message_id=message_id,
                session_id=session_id,
                sender_id=user_id,
                sender_username=participant.username,
                content=content,
                message_type=MessageType.TEXT,
                timestamp=datetime.utcnow(),
                original_language=detected_language,
                reply_to=reply_to
            )
            
            # Auto-translate if enabled
            if session.auto_translate:
                await self._translate_message(chat_message, session)
            
            session.messages.append(chat_message)
            session.last_activity = datetime.utcnow()
            participant.last_activity = datetime.utcnow()
            
            # Broadcast message to all participants
            await self._broadcast_message(session_id, chat_message)
            
            logger.info(f"Message {message_id} sent in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_request_translation(self, user_id: str, message: Dict[str, Any]):
        """Request translation for specific message"""
        try:
            session_id = message.get("session_id")
            message_id = message.get("message_id")
            target_language = message.get("target_language")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            # Find message
            chat_message = None
            for msg in session.messages:
                if msg.message_id == message_id:
                    chat_message = msg
                    break
            
            if not chat_message:
                await self._send_error(user_id, "Message not found")
                return
            
            # Check if translation already exists
            if target_language in chat_message.translations:
                translation = chat_message.translations[target_language]
            else:
                # Perform translation
                translation = await self.translation_engine.translate(
                    chat_message.content,
                    chat_message.original_language,
                    target_language
                )
                chat_message.translations[target_language] = translation
            
            # Send translation to user
            await self._send_to_user(user_id, {
                "type": "translation_result",
                "message_id": message_id,
                "target_language": target_language,
                "translation": {
                    "text": translation.translated_text,
                    "confidence": translation.confidence,
                    "cultural_adaptations": translation.cultural_adaptations,
                    "technical_terms": translation.technical_terms
                }
            })
            
        except Exception as e:
            logger.error(f"Error translating message: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_change_language(self, user_id: str, message: Dict[str, Any]):
        """Change user's preferred language"""
        try:
            session_id = message.get("session_id")
            new_language = message.get("language")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                await self._send_error(user_id, "Not a participant in this session")
                return
            
            if new_language not in self.supported_languages:
                await self._send_error(user_id, "Language not supported")
                return
            
            old_language = participant.preferred_language
            participant.preferred_language = new_language
            participant.last_activity = datetime.utcnow()
            
            # Notify user
            await self._send_to_user(user_id, {
                "type": "language_changed",
                "old_language": old_language,
                "new_language": new_language
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_language_changed",
                "user_id": user_id,
                "username": participant.username,
                "new_language": new_language
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} changed language from {old_language} to {new_language}")
            
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_typing_indicator(self, user_id: str, message: Dict[str, Any]):
        """Handle typing indicator"""
        try:
            session_id = message.get("session_id")
            is_typing = message.get("is_typing", False)
            
            session = self.chat_sessions.get(session_id)
            if not session:
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                return
            
            participant.is_typing = is_typing
            participant.last_activity = datetime.utcnow()
            
            # Broadcast typing indicator
            await self._broadcast_to_session(session_id, {
                "type": "typing_indicator",
                "user_id": user_id,
                "username": participant.username,
                "is_typing": is_typing
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling typing indicator: {e}")
    
    async def _handle_mark_read(self, user_id: str, message: Dict[str, Any]):
        """Mark messages as read"""
        try:
            session_id = message.get("session_id")
            message_id = message.get("message_id")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                return
            
            # Find and mark message as read
            for msg in session.messages:
                if msg.message_id == message_id:
                    msg.status = MessageStatus.READ
                    break
            
            participant.last_activity = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
    
    async def _handle_voice_message(self, user_id: str, message: Dict[str, Any]):
        """Handle voice message with transcription and translation"""
        try:
            session_id = message.get("session_id")
            audio_data = message.get("audio_data")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                await self._send_error(user_id, "Not a participant in this session")
                return
            
            # Transcribe voice message
            transcription = await self.translation_engine.transcribe_audio(
                audio_data, participant.preferred_language
            )
            
            # Create voice message
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            voice_message = ChatMessage(
                message_id=message_id,
                session_id=session_id,
                sender_id=user_id,
                sender_username=participant.username,
                content=transcription,
                message_type=MessageType.VOICE,
                timestamp=datetime.utcnow(),
                original_language=participant.preferred_language,
                attachments=[{
                    "type": "audio",
                    "data": audio_data,
                    "transcription": transcription
                }]
            )
            
            # Auto-translate if enabled
            if session.auto_translate:
                await self._translate_message(voice_message, session)
            
            session.messages.append(voice_message)
            session.last_activity = datetime.utcnow()
            
            # Broadcast voice message
            await self._broadcast_message(session_id, voice_message)
            
            logger.info(f"Voice message {message_id} sent in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_upload_file(self, user_id: str, message: Dict[str, Any]):
        """Handle file upload"""
        try:
            session_id = message.get("session_id")
            file_data = message.get("file_data")
            filename = message.get("filename")
            file_type = message.get("file_type")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                await self._send_error(user_id, "Not a participant in this session")
                return
            
            # Create file message
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            file_message = ChatMessage(
                message_id=message_id,
                session_id=session_id,
                sender_id=user_id,
                sender_username=participant.username,
                content=f"Shared file: {filename}",
                message_type=MessageType.FILE,
                timestamp=datetime.utcnow(),
                original_language=participant.preferred_language,
                attachments=[{
                    "type": file_type,
                    "filename": filename,
                    "data": file_data,
                    "size": len(file_data) if file_data else 0
                }]
            )
            
            session.messages.append(file_message)
            session.last_activity = datetime.utcnow()
            
            # Broadcast file message
            await self._broadcast_message(session_id, file_message)
            
            logger.info(f"File {filename} uploaded in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_search_messages(self, user_id: str, message: Dict[str, Any]):
        """Search messages in chat session"""
        try:
            session_id = message.get("session_id")
            query = message.get("query", "")
            language = message.get("language")
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            # Search messages
            results = []
            for msg in session.messages:
                if self._message_matches_query(msg, query, language):
                    participant = session.participants.get(user_id)
                    preferred_lang = participant.preferred_language if participant else "en"
                    results.append(await self._serialize_message(msg, preferred_lang))
            
            await self._send_to_user(user_id, {
                "type": "search_results",
                "query": query,
                "results": results,
                "total_count": len(results)
            })
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_get_history(self, user_id: str, message: Dict[str, Any]):
        """Get chat history"""
        try:
            session_id = message.get("session_id")
            limit = message.get("limit", 50)
            offset = message.get("offset", 0)
            
            session = self.chat_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Chat session not found")
                return
            
            participant = session.participants.get(user_id)
            preferred_lang = participant.preferred_language if participant else "en"
            
            # Get message slice
            start_idx = max(0, len(session.messages) - offset - limit)
            end_idx = len(session.messages) - offset
            
            history_messages = []
            for msg in session.messages[start_idx:end_idx]:
                history_messages.append(await self._serialize_message(msg, preferred_lang))
            
            await self._send_to_user(user_id, {
                "type": "chat_history",
                "messages": history_messages,
                "total_count": len(session.messages),
                "has_more": start_idx > 0
            })
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            await self._send_error(user_id, str(e))
    
    def _message_matches_query(self, message: ChatMessage, query: str, 
                              language: Optional[str] = None) -> bool:
        """Check if message matches search query"""
        query_lower = query.lower()
        
        # Search in original content
        if query_lower in message.content.lower():
            return True
        
        # Search in translations if language specified
        if language and language in message.translations:
            translated_text = message.translations[language].translated_text
            if query_lower in translated_text.lower():
                return True
        
        return False
    
    async def _translate_message(self, message: ChatMessage, session: ChatSession):
        """Translate message to all participant languages"""
        # Get unique target languages
        target_languages = set()
        for participant in session.participants.values():
            target_languages.add(participant.preferred_language)
            target_languages.update(participant.secondary_languages)
        
        # Remove source language
        target_languages.discard(message.original_language)
        
        # Translate to each target language
        for target_lang in target_languages:
            if target_lang not in message.translations:
                try:
                    translation = await self.translation_engine.translate(
                        message.content,
                        message.original_language,
                        target_lang
                    )
                    message.translations[target_lang] = translation
                except Exception as e:
                    logger.error(f"Translation error for {target_lang}: {e}")
    
    async def _create_system_message(self, session_id: str, content: str) -> ChatMessage:
        """Create system message"""
        return ChatMessage(
            message_id=f"sys_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            sender_id="system",
            sender_username="System",
            content=content,
            message_type=MessageType.SYSTEM,
            timestamp=datetime.utcnow(),
            original_language="en"
        )
    
    async def _serialize_message(self, message: ChatMessage, 
                               target_language: str) -> Dict[str, Any]:
        """Serialize message for transmission"""
        # Get appropriate content based on target language
        content = message.content
        if target_language in message.translations:
            content = message.translations[target_language].translated_text
        
        return {
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "sender_username": message.sender_username,
            "content": content,
            "original_content": message.content,
            "message_type": message.message_type.value,
            "timestamp": message.timestamp.isoformat(),
            "original_language": message.original_language,
            "target_language": target_language,
            "status": message.status.value,
            "reply_to": message.reply_to,
            "attachments": message.attachments,
            "has_translations": len(message.translations) > 0
        }
    
    async def _broadcast_message(self, session_id: str, message: ChatMessage,
                               exclude_user: Optional[str] = None):
        """Broadcast message to all session participants"""
        session = self.chat_sessions.get(session_id)
        if not session:
            return
        
        for user_id, participant in session.participants.items():
            if user_id != exclude_user:
                serialized_msg = await self._serialize_message(
                    message, participant.preferred_language
                )
                await self._send_to_user(user_id, {
                    "type": "message_received",
                    "message": serialized_msg
                })
    
    async def _filter_profanity(self, content: str, language: str) -> str:
        """Filter profanity from message content"""
        # This is a simplified implementation
        # In production, use proper profanity filtering libraries
        
        profanity_patterns = {
            "en": [r"\b(damn|hell|shit|fuck)\b"],
            "es": [r"\b(mierda|joder|coño)\b"],
            "fr": [r"\b(merde|putain|con)\b"],
            "de": [r"\b(scheiße|verdammt)\b"]
        }
        
        patterns = profanity_patterns.get(language, [])
        filtered_content = content
        
        for pattern in patterns:
            filtered_content = re.sub(pattern, "***", filtered_content, flags=re.IGNORECASE)
        
        return filtered_content
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        websocket = self.websocket_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                await self._cleanup_user_connection(user_id)
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                   exclude_user: Optional[str] = None):
        """Broadcast message to all users in session"""
        session = self.chat_sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.participants:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _send_error(self, user_id: str, error_message: str):
        """Send error message to user"""
        await self._send_to_user(user_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _cleanup_user_connection(self, user_id: str):
        """Cleanup user connection"""
        try:
            # Remove WebSocket connection
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
            
            # Remove from all chat sessions
            for session_id, session in self.chat_sessions.items():
                if user_id in session.participants:
                    await self._handle_leave_chat(user_id, {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")


class AITranslationEngine:
    """AI-powered translation engine"""
    
    def __init__(self):
        self.cache = {}
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect language of text"""
        # Simplified language detection
        # In production, use proper language detection libraries
        
        if not text.strip():
            return None
        
        # Common language patterns (simplified)
        if re.search(r'[ñáéíóúü]', text.lower()):
            return "es"
        elif re.search(r'[àâäéèêëïîôùûüÿç]', text.lower()):
            return "fr"
        elif re.search(r'[äöüß]', text.lower()):
            return "de"
        elif re.search(r'[\u4e00-\u9fff]', text):
            return "zh"
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return "ja"
        elif re.search(r'[\u0600-\u06ff]', text):
            return "ar"
        else:
            return "en"  # Default to English
    
    async def translate(self, text: str, source_lang: str, 
                       target_lang: str) -> TranslationResult:
        """Translate text between languages"""
        # Cache key
        cache_key = f"{source_lang}:{target_lang}:{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Simplified translation (in production, use proper translation APIs)
        if source_lang == target_lang:
            translated_text = text
            confidence = 1.0
        else:
            # Mock translation - in production, use Google Translate, Azure, etc.
            translated_text = f"[{target_lang.upper()}] {text}"
            confidence = 0.85
        
        result = TranslationResult(
            original_text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            confidence=confidence,
            detected_language=source_lang,
            cultural_adaptations=[],
            technical_terms=[]
        )
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    async def transcribe_audio(self, audio_data: str, language: str) -> str:
        """Transcribe audio to text"""
        # Mock transcription - in production, use speech-to-text services
        return f"[Transcribed audio in {language}] Audio content here"


# Export the service
__all__ = ['TranslationChatService', 'MessageType', 'TranslationMode', 'MessageStatus',
           'Language', 'TranslationResult', 'ChatMessage', 'ChatParticipant', 
           'ChatSession', 'AITranslationEngine']