"""Session Content Manager - IA Influencer Agent

Enterprise-grade session content management with content protection integration,
media session state handling, and intelligent content analysis for multi-format
content creators across platforms with advanced session-based workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copy, modification, or distribution without 
explicit written permission is strictly prohibited.
Contact: mlaiel@live.de

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced Content Management Architecture  
- ML Engineer: Content Intelligence & Analysis
- DBA: High-Performance Content Storage
- Security Expert: Content Protection Integration
- Microservices Architect: Distributed Content Management
- Audio Engineer: Audio Content Session Management
- DevOps: Content Scalability & Performance
- IA Prompt Engineer: Content-Aware Conversational Experience
"""

import asyncio
import logging
import hashlib
import mimetypes
import math
import uuid
import os
import shutil
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Content processing imports
from PIL import Image
import cv2
import numpy as np
import librosa
import magic
import boto3
from botocore.exceptions import BotoCoreError

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, ContentModel
from ...models.user import UserModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher
from ...utils.content_analyzer import ContentAnalyzer
from ...utils.file_validator import FileValidator
from ...content_protection.fingerprinting.audio_fingerprint import AudioFingerprintEngine
from ...content_protection.fingerprinting.video_fingerprint import VideoFingerprintEngine
from ...content_protection.fingerprinting.image_fingerprint import ImageFingerprintEngine
from ...content_protection.fingerprinting.text_fingerprint import TextFingerprintEngine

logger = get_logger(__name__)


class ContentType(Enum):
    """
Content type classifications"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    CODE = "code"
    UNKNOWN = "unknown"


class ContentFormat(Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    MKV = "mkv"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    TIFF = "tiff"
    
    # Text/Document formats
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    RTF = "rtf"
    HTML = "html"
    
    # Archive formats
    ZIP = "zip"
    RAR = "rar"
    TAR = "tar"
    GZIP = "gzip"


class ContentState(Enum):
    """Content processing state"""

    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    PROTECTING = "protecting"
    PROTECTED = "protected"
    MONETIZING = "monetizing"
    MONETIZED = "monetized"
    PROCESSING_ERROR = "processing_error"
    READY = "ready"


class ProtectionLevel(Enum):
    """Content protection levels"""

    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class SessionContentInfo(BaseModel):
    """Session content information"""
    content_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    content_type: ContentType
    content_format: ContentFormat
    filename: str
    file_size: int
    file_hash: str
    mime_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_state: ContentState = ContentState.UPLOADED
    protection_level: ProtectionLevel = ProtectionLevel.NONE
    fingerprint_data: Dict[str, Any] = Field(default_factory=dict)
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    monetization_data: Dict[str, Any] = Field(default_factory=dict)
    storage_location: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MediaSessionState(BaseModel):
    """Media-specific session state"""
    session_id: str
    active_content: List[str] = Field(default_factory=list)  # content_ids
    recording_state: Dict[str, Any] = Field(default_factory=dict)
    playback_state: Dict[str, Any] = Field(default_factory=dict)
    editing_state: Dict[str, Any] = Field(default_factory=dict)
    processing_queue: List[str] = Field(default_factory=list)
    collaboration_content: Dict[str, List[str]] = Field(default_factory=dict)
    content_history: List[Dict[str, Any]] = Field(default_factory=list)
    protection_status: Dict[str, str] = Field(default_factory=dict)
    monetization_status: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentAnalysisResult(BaseModel):
    """
Content analysis result"""
    content_id: str
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float
    processing_time: float
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class ContentManagerConfig:
    """
Content manager configuration"""
    max_file_size_mb: int = 500
    allowed_content_types: List[str] = field(default_factory=lambda: [
        "audio", "video", "image", "text", "document"
    ])
    storage_backend: str = "s3"  # s3, gcs, azure, local
    enable_auto_protection: bool = True
    enable_auto_analysis: bool = True
    enable_content_optimization: bool = True
    protection_threshold: float = 0.8
    analysis_timeout: int = 300  # seconds
    max_concurrent_uploads: int = 10
    content_retention_days: int = 365


class ContentProtectionSessionHandler:
    """Handles content protection within session context"""
    
    def __init__(self, config: ContentManagerConfig):
        self.config = config
        self.audio_fingerprint = AudioFingerprintEngine()
        self.video_fingerprint = VideoFingerprintEngine()
        self.image_fingerprint = ImageFingerprintEngine()
        self.text_fingerprint = TextFingerprintEngine()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
    
    async def protect_content(
        self,
        content_info: SessionContentInfo,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    ) -> bool:
        """
Protect content with fingerprinting and registration"""
        
        try:
            content_info.processing_state = ContentState.PROTECTING
            content_info.protection_level = protection_level
            
            # Generate fingerprints based on content type
            fingerprint_data = await self._generate_fingerprints(content_info)
            
            if fingerprint_data:
                content_info.fingerprint_data = fingerprint_data
                content_info.processing_state = ContentState.PROTECTED
                
                # Register protection
                await self._register_content_protection(content_info)
                
                # Publish protection event
                await self.event_publisher.publish(
                    "content.protected",
                    {
                        "content_id": content_info.content_id,
                        "session_id": content_info.session_id,
                        "user_id": content_info.user_id,
                        "content_type": content_info.content_type.value,
                        "protection_level": protection_level.value,
                        "fingerprint_types": list(fingerprint_data.keys())
                    }
                )
                
                await self.metrics_collector.increment("content_protection.protections_created")
                self.logger.info(f"Content protected: {content_info.content_id}")
                
                return True
            else:
                content_info.processing_state = ContentState.PROCESSING_ERROR
                return False
                
        except Exception as e:
            self.logger.error(f"Content protection failed: {str(e)}")
            content_info.processing_state = ContentState.PROCESSING_ERROR
            await self.metrics_collector.increment("content_protection.protection_errors")
            return False
    
    async def _generate_fingerprints(
        self,
        content_info: SessionContentInfo
    ) -> Dict[str, Any]:
        """Generate fingerprints based on content type"""
        
        fingerprints = {}
        
        try:
            storage_path = content_info.storage_location
            
            if content_info.content_type == ContentType.AUDIO:
                fingerprints["audio"] = await self.audio_fingerprint.generate_fingerprint(storage_path)
            
            elif content_info.content_type == ContentType.VIDEO:
                # Generate both video and audio fingerprints
                fingerprints["video"] = await self.video_fingerprint.generate_fingerprint(storage_path)
                fingerprints["audio"] = await self.audio_fingerprint.extract_audio_and_fingerprint(storage_path)
            
            elif content_info.content_type == ContentType.IMAGE:
                fingerprints["image"] = await self.image_fingerprint.generate_fingerprint(storage_path)
            
            elif content_info.content_type == ContentType.TEXT:
                # Read text content
                with open(storage_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                fingerprints["text"] = await self.text_fingerprint.generate_fingerprint(text_content)
            
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {str(e)}")
            return {}
    
    async def _register_content_protection(self, content_info: SessionContentInfo):
        """Register content protection in database"""
        
        try:
            async with get_async_session() as session:
                # Create content protection record
                protection_record = ContentModel(
                    content_id=content_info.content_id,
                    session_id=content_info.session_id,
                    user_id=content_info.user_id,
                    content_type=content_info.content_type.value,
                    filename=content_info.filename,
                    file_hash=content_info.file_hash,
                    fingerprint_data=content_info.fingerprint_data,
                    protection_level=content_info.protection_level.value,
                    created_at=content_info.upload_timestamp
                )
                
                session.add(protection_record)
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Protection registration failed: {str(e)}")
    
    async def check_content_violations(
        self,
        content_info: SessionContentInfo
    ) -> List[Dict[str, Any]]:
        """Check for content violations using fingerprints"""
        
        violations = []
        
        try:
            fingerprints = content_info.fingerprint_data
            
            for fingerprint_type, fingerprint_data in fingerprints.items():
                if fingerprint_type == "audio":
                    matches = await self.audio_fingerprint.search_matches(fingerprint_data)
                elif fingerprint_type == "video":
                    matches = await self.video_fingerprint.search_matches(fingerprint_data)
                elif fingerprint_type == "image":
                    matches = await self.image_fingerprint.search_matches(fingerprint_data)
                elif fingerprint_type == "text":
                    matches = await self.text_fingerprint.search_matches(fingerprint_data)
                else:
                    continue
                
                # Process matches
                for match in matches:
                    if match.get("similarity", 0) > self.config.protection_threshold:
                        violations.append({
                            "content_id": content_info.content_id,
                            "fingerprint_type": fingerprint_type,
                            "matched_content_id": match.get("content_id"),
                            "similarity": match.get("similarity"),
                            "match_details": match,
                            "violation_timestamp": datetime.utcnow().isoformat()
                        })
            
            if violations:
                await self.metrics_collector.increment(
                    "content_protection.violations_detected",
                    value=len(violations)
                )
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Content violation check failed: {str(e)}")
            return []
    
    async def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get content protection status"""
        
        try:
            # Get from cache first
            cache_key = f"protection_status:{content_id}"
            cached_status = await self.cache_manager.get(cache_key)
            
            if cached_status:
                return json.loads(cached_status)
            
            # Load from database
            async with get_async_session() as session:
                query = select(ContentModel).where(ContentModel.content_id == content_id)
                result = await session.execute(query)
                content_record = result.scalar_one_or_none()
                
                if content_record:
                    status = {
                        "content_id": content_id,
                        "protected": True,
                        "protection_level": content_record.protection_level,
                        "fingerprint_types": list(content_record.fingerprint_data.keys()) if content_record.fingerprint_data else [],
                        "created_at": content_record.created_at.isoformat(),
                        "violations_count": 0  # Would be calculated from violations table
                    }
                    
                    # Cache status
                    await self.cache_manager.set(
                        cache_key,
                        json.dumps(status, default=str),
                        ttl=3600
                    )
                    
                    return status
            
            return {"content_id": content_id, "protected": False}
            
        except Exception as e:
            self.logger.error(f"Protection status retrieval failed: {str(e)}")
            return {"content_id": content_id, "protected": False, "error": str(e)}


class MediaSessionStateManager:
    """Manages media-specific session state"""
    
    def __init__(self, config: ContentManagerConfig):
        self.config = config
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Active media sessions
        self.media_sessions: Dict[str, MediaSessionState] = {}
    
    async def initialize_media_session(self, session_id: str) -> MediaSessionState:
        """
Initialize media session state"""
        
        try:
            media_state = MediaSessionState(session_id=session_id)
            self.media_sessions[session_id] = media_state
            
            # Cache media state
            await self._cache_media_state(media_state)
            
            self.logger.info(f"Media session initialized: {session_id}")
            return media_state
            
        except Exception as e:
            self.logger.error(f"Media session initialization failed: {str(e)}")
            raise
    
    async def add_content_to_session(
        self,
        session_id: str,
        content_info: SessionContentInfo
    ) -> bool:
        """Add content to media session"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                media_state = await self.initialize_media_session(session_id)
            
            # Add content to active content list
            if content_info.content_id not in media_state.active_content:
                media_state.active_content.append(content_info.content_id)
            
            # Add to content history
            history_entry = {
                "content_id": content_info.content_id,
                "action": "added",
                "timestamp": datetime.utcnow().isoformat(),
                "content_type": content_info.content_type.value,
                "filename": content_info.filename
            }
            media_state.content_history.append(history_entry)
            
            # Update protection status
            if content_info.protection_level != ProtectionLevel.NONE:
                media_state.protection_status[content_info.content_id] = content_info.protection_level.value
            
            # Store updated state
            await self._store_media_state(media_state)
            
            await self.metrics_collector.increment("media_session.content_added")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add content to session: {str(e)}")
            return False
    
    async def start_recording(
        self,
        session_id: str,
        recording_type: str,
        recording_config: Dict[str, Any]
    ) -> str:
        """Start recording in session"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                media_state = await self.initialize_media_session(session_id)
            
            recording_id = str(uuid4())
            
            # Update recording state
            media_state.recording_state = {
                "recording_id": recording_id,
                "type": recording_type,
                "status": "recording",
                "start_time": datetime.utcnow().isoformat(),
                "config": recording_config
            }
            
            # Add to content history
            history_entry = {
                "action": "recording_started",
                "recording_id": recording_id,
                "recording_type": recording_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            media_state.content_history.append(history_entry)
            
            await self._store_media_state(media_state)
            
            await self.metrics_collector.increment("media_session.recordings_started")
            self.logger.info(f"Recording started: {recording_id} in session {session_id}")
            
            return recording_id
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {str(e)}")
            return ""
    
    async def stop_recording(self, session_id: str) -> Optional[str]:
        """Stop recording in session"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state or not media_state.recording_state:
                return None
            
            recording_id = media_state.recording_state.get("recording_id")
            
            # Update recording state
            media_state.recording_state.update({
                "status": "stopped",
                "end_time": datetime.utcnow().isoformat()
            })
            
            # Add to content history
            history_entry = {
                "action": "recording_stopped",
                "recording_id": recording_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            media_state.content_history.append(history_entry)
            
            await self._store_media_state(media_state)
            
            await self.metrics_collector.increment("media_session.recordings_stopped")
            self.logger.info(f"Recording stopped: {recording_id} in session {session_id}")
            
            return recording_id
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {str(e)}")
            return None
    
    async def update_playback_state(
        self,
        session_id: str,
        content_id: str,
        playback_data: Dict[str, Any]
    ) -> bool:
        """Update playback state for content"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                return False
            
            # Update playback state
            media_state.playback_state[content_id] = {
                **playback_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self._store_media_state(media_state)
            
            await self.metrics_collector.increment("media_session.playback_updates")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update playback state: {str(e)}")
            return False
    
    async def add_to_processing_queue(
        self,
        session_id: str,
        content_id: str
    ) -> bool:
        """Add content to processing queue"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                return False
            
            if content_id not in media_state.processing_queue:
                media_state.processing_queue.append(content_id)
                
                await self._store_media_state(media_state)
                
                await self.metrics_collector.increment("media_session.queue_additions")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add to processing queue: {str(e)}")
            return False
    
    async def remove_from_processing_queue(
        self,
        session_id: str,
        content_id: str
    ) -> bool:
        """Remove content from processing queue"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                return False
            
            if content_id in media_state.processing_queue:
                media_state.processing_queue.remove(content_id)
                
                await self._store_media_state(media_state)
                
                await self.metrics_collector.increment("media_session.queue_removals")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove from processing queue: {str(e)}")
            return False
    
    async def _get_media_state(self, session_id: str) -> Optional[MediaSessionState]:
        """Get media session state"""
        
        # Check memory first
        if session_id in self.media_sessions:
            return self.media_sessions[session_id]
        
        # Try cache
        cache_key = f"media_session:{session_id}"
        cached_data = await self.cache_manager.get(cache_key)
        
        if cached_data:
            state_dict = json.loads(cached_data)
            media_state = MediaSessionState(**state_dict)
            self.media_sessions[session_id] = media_state
            return media_state
        
        return None
    
    async def _store_media_state(self, media_state: MediaSessionState):
        """Store media session state"""
        
        # Update memory
        self.media_sessions[media_state.session_id] = media_state
        
        # Cache state
        await self._cache_media_state(media_state)
    
    async def _cache_media_state(self, media_state: MediaSessionState):
        """
Cache media session state"""
        
        try:
            cache_key = f"media_session:{media_state.session_id}"
            await self.cache_manager.set(
                cache_key,
                media_state.json(),
                ttl=3600
            )
            
        except Exception as e:
            self.logger.error(f"Media state caching failed: {str(e)}")
    
    async def get_session_content_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session content"""
        
        try:
            media_state = await self._get_media_state(session_id)
            
            if not media_state:
                return {"session_id": session_id, "content_count": 0}
            
            # Count content by type
            content_types = {}
            protected_count = 0
            
            for content_id in media_state.active_content:
                # Would typically fetch content info from database
                # For now, we'll use simplified counting
                if content_id in media_state.protection_status:
                    protected_count += 1
            
            return {
                "session_id": session_id,
                "total_content": len(media_state.active_content),
                "protected_content": protected_count,
                "recording_active": media_state.recording_state.get("status") == "recording",
                "processing_queue_size": len(media_state.processing_queue),
                "content_history_size": len(media_state.content_history),
                "collaboration_content": {
                    user_id: len(content_list)
                    for user_id, content_list in media_state.collaboration_content.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Session content summary failed: {str(e)}")
            return {"session_id": session_id, "error": str(e)}


class SessionContentAnalyzer:
    """Analyzes content within session context"""
    
    def __init__(self, config: ContentManagerConfig):
        self.config = config
        self.content_analyzer = ContentAnalyzer()
        self.file_validator = FileValidator()
        self.logger = get_logger(self.__class__.__name__)
    
    async def analyze_content(
        self,
        content_info: SessionContentInfo
    ) -> ContentAnalysisResult:
        """
Analyze content and extract metadata"""
        
        start_time = datetime.utcnow()
        
        try:
            content_info.processing_state = ContentState.ANALYZING
            
            # Perform content-specific analysis
            analysis_results = {}
            
            if content_info.content_type == ContentType.AUDIO:
                analysis_results = await self._analyze_audio_content(content_info)
            elif content_info.content_type == ContentType.VIDEO:
                analysis_results = await self._analyze_video_content(content_info)
            elif content_info.content_type == ContentType.IMAGE:
                analysis_results = await self._analyze_image_content(content_info)
            elif content_info.content_type == ContentType.TEXT:
                analysis_results = await self._analyze_text_content(content_info)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create analysis result
            result = ContentAnalysisResult(
                content_id=content_info.content_id,
                analysis_type=content_info.content_type.value,
                results=analysis_results,
                confidence_score=analysis_results.get("confidence", 0.8),
                processing_time=processing_time
            )
            
            # Update content info
            content_info.analysis_results = analysis_results
            content_info.processing_state = ContentState.ANALYZED
            
            self.logger.info(f"Content analyzed: {content_info.content_id} ({processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            content_info.processing_state = ContentState.PROCESSING_ERROR
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ContentAnalysisResult(
                content_id=content_info.content_id,
                analysis_type=content_info.content_type.value,
                results={"error": str(e)},
                confidence_score=0.0,
                processing_time=processing_time
            )
    
    async def _analyze_audio_content(self, content_info: SessionContentInfo) -> Dict[str, Any]:
        """Analyze audio content"""
        
        try:
            # Load audio file
            audio_path = content_info.storage_location
            y, sr = librosa.load(audio_path)
            
            # Extract audio features
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Audio quality metrics
            rms = librosa.feature.rms(y=y)[0]
            zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
            
            return {
                "duration_seconds": float(duration),
                "tempo_bpm": float(tempo),
                "sample_rate": int(sr),
                "channels": 1,  # Simplified
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "mfcc_features": mfccs.tolist(),
                "rms_energy_mean": float(np.mean(rms)),
                "zero_crossing_rate_mean": float(np.mean(zero_crossings)),
                "confidence": 0.9
            }
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_video_content(self, content_info: SessionContentInfo) -> Dict[str, Any]:
        """Analyze video content"""
        
        try:
            video_path = content_info.storage_location
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Analyze sample frames
            frame_analysis = []
            sample_frames = min(10, frame_count)
            
            for i in range(sample_frames):
                frame_pos = int(i * frame_count / sample_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if ret:
                    # Basic frame analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)
                    contrast = np.std(gray)
                    
                    frame_analysis.append({
                        "frame_number": frame_pos,
                        "brightness": float(brightness),
                        "contrast": float(contrast)
                    })
            
            cap.release()
            
            return {
                "duration_seconds": float(duration),
                "fps": float(fps),
                "frame_count": frame_count,
                "resolution": f"{width}x{height}",
                "width": width,
                "height": height,
                "frame_analysis": frame_analysis,
                "average_brightness": float(np.mean([f["brightness"] for f in frame_analysis])) if frame_analysis else 0,
                "average_contrast": float(np.mean([f["contrast"] for f in frame_analysis])) if frame_analysis else 0,
                "confidence": 0.85
            }
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_image_content(self, content_info: SessionContentInfo) -> Dict[str, Any]:
        """Analyze image content"""
        
        try:
            image_path = content_info.storage_location
            image = Image.open(image_path)
            
            # Basic image properties
            width, height = image.size
            mode = image.mode
            format_info = image.format
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Color analysis
            if len(img_array.shape) == 3:  # Color image
                # Average colors
                avg_colors = np.mean(img_array, axis=(0, 1))
                
                # Color distribution
                color_std = np.std(img_array, axis=(0, 1))
                
                color_analysis = {
                    "average_rgb": avg_colors.tolist(),
                    "color_std": color_std.tolist(),
                    "is_grayscale": False
                }
            else:  # Grayscale
                avg_brightness = np.mean(img_array)
                brightness_std = np.std(img_array)
                
                color_analysis = {
                    "average_brightness": float(avg_brightness),
                    "brightness_std": float(brightness_std),
                    "is_grayscale": True
                }
            
            # Image quality metrics
            sharpness = self._calculate_image_sharpness(img_array)
            
            return {
                "width": width,
                "height": height,
                "mode": mode,
                "format": format_info,
                "file_size": content_info.file_size,
                "aspect_ratio": float(width / height) if height > 0 else 0,
                "pixel_count": width * height,
                "color_analysis": color_analysis,
                "sharpness_score": float(sharpness),
                "confidence": 0.9
            }
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_text_content(self, content_info: SessionContentInfo) -> Dict[str, Any]:
        """Analyze text content"""
        
        try:
            text_path = content_info.storage_location
            
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Basic text metrics
            word_count = len(text_content.split())
            char_count = len(text_content)
            line_count = len(text_content.splitlines())
            paragraph_count = len([p for p in text_content.split('\n\n') if p.strip()])
            
            # Language detection (simplified)
            language = self._detect_language(text_content)
            
            # Content categorization (simplified)
            content_category = self._categorize_text_content(text_content)
            
            # Readability metrics (simplified)
            avg_word_length = np.mean([len(word) for word in text_content.split()])
            avg_sentence_length = char_count / max(text_content.count('.'), 1)
            
            return {
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "paragraph_count": paragraph_count,
                "language": language,
                "content_category": content_category,
                "average_word_length": float(avg_word_length),
                "average_sentence_length": float(avg_sentence_length),
                "encoding": "utf-8",
                "confidence": 0.8
            }
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    def _calculate_image_sharpness(self, img_array: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            return sharpness
            
        except Exception:
            return 0.0
    
    def _detect_language(self, text: str) -> str:
        """
Detect text language (simplified implementation)"""
        
        # This is a very simplified language detection
        # In production, you'd use libraries like langdetect or spacy
        
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
        french_words = ['le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de']
        german_words = ['der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'an', 'zu', 'für', 'von']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        german_count = sum(1 for word in german_words if word in text_lower)
        
        if english_count >= french_count and english_count >= german_count:
            return "en"
        elif french_count >= german_count:
            return "fr"
        else:
            return "de"
    
    def _categorize_text_content(self, text: str) -> str:
        """Categorize text content (simplified implementation)"""
        
        text_lower = text.lower()
        
        # Simple keyword-based categorization
        if any(word in text_lower for word in ['music', 'song', 'album', 'artist', 'band']):
            return "music"
        elif any(word in text_lower for word in ['video', 'film', 'movie', 'cinema']):
            return "video"
        elif any(word in text_lower for word in ['photo', 'image', 'picture', 'photography']):
            return "photography"
        elif any(word in text_lower for word in ['blog', 'post', 'article', 'story']):
            return "blog"
        else:
            return "general"


class SessionContentManager:
    """Main session content management controller"""
    
    def __init__(self, config: Optional[ContentManagerConfig] = None):
        self.config = config or ContentManagerConfig()
        self.protection_handler = ContentProtectionSessionHandler(self.config)
        self.media_state_manager = MediaSessionStateManager(self.config)
        self.content_analyzer = SessionContentAnalyzer(self.config)
        self.file_validator = FileValidator()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Content storage
        self.storage_client = self._initialize_storage()
        
        # Content tracking
        self.session_content: Dict[str, List[str]] = {}  # session_id -> [content_ids]
    
    def _initialize_storage(self):
        """
Initialize storage backend"""
        
        try:
            if self.config.storage_backend == "s3":
                return boto3.client('s3')
            # Add other storage backends as needed
            return None
            
        except Exception as e:
            self.logger.error(f"Storage initialization failed: {str(e)}")
            return None
    
    async def upload_content(
        self,
        session_id: str,
        user_id: str,
        file_data: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> Optional[SessionContentInfo]:
        """Upload and process content for session"""
        
        try:
            # Validate file
            validation_result = await self.file_validator.validate_file(
                file_data,
                filename,
                max_size_mb=self.config.max_file_size_mb
            )
            
            if not validation_result["valid"]:
                self.logger.warning(f"File validation failed: {validation_result['reason']}")
                return None
            
            # Determine content type and format
            detected_type = self._detect_content_type(filename, file_data)
            detected_format = self._detect_content_format(filename)
            
            # Extract metadata automatically
            extracted_metadata = await self._extract_metadata(file_data, filename, detected_type)
            
            # Generate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Create content info
            content_info = SessionContentInfo(
                session_id=session_id,
                user_id=user_id,
                content_type=detected_type,
                content_format=detected_format,
                filename=filename,
                file_size=len(file_data),
                file_hash=file_hash,
                mime_type=validation_result.get("mime_type", "application/octet-stream"),
                processing_state=ContentState.UPLOADING
            )
            
            # Store file
            storage_location = await self._store_file(content_info, file_data)
            
            if storage_location:
                content_info.storage_location = storage_location
                content_info.processing_state = ContentState.UPLOADED
                
                # CDN Integration - upload to CDN for optimized delivery
                cdn_integration = CDNIntegration(self.config.get('cdn_config', {}))
                cdn_result = await cdn_integration.upload_to_cdn(
                    content_info.content_id,
                    file_data,
                    filename,
                    content_info.content_type,
                    extracted_metadata
                )
                
                if cdn_result.get('success'):
                    content_info.cdn_urls = cdn_result.get('urls', {})
                    content_info.optimization_stats = cdn_result.get('optimization_stats', {})
                    self.logger.info(f"Content uploaded to CDN: {content_info.content_id}")
                
                # Add to session content tracking
                if session_id not in self.session_content:
                    self.session_content[session_id] = []
                self.session_content[session_id].append(content_info.content_id)
                
                # Add to media session
                await self.media_state_manager.add_content_to_session(session_id, content_info)
                
                # Start background processing
                asyncio.create_task(self._process_content_async(content_info))
                
                await self.metrics_collector.increment("content_manager.uploads_completed")
                self.logger.info(f"Content uploaded: {content_info.content_id}")
                
                return content_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Content upload failed: {str(e)}")
            await self.metrics_collector.increment("content_manager.upload_errors")
            return None
    
    async def _process_content_async(self, content_info: SessionContentInfo):
        """Background content processing"""
        
        try:
            # Analyze content
            if self.config.enable_auto_analysis:
                analysis_result = await self.content_analyzer.analyze_content(content_info)
                
                # Publish analysis result
                await self.event_publisher.publish(
                    "content.analyzed",
                    {
                        "content_id": content_info.content_id,
                        "session_id": content_info.session_id,
                        "analysis_results": analysis_result.dict()
                    }
                )
            
            # Auto-protect content if enabled
            if self.config.enable_auto_protection:
                protection_success = await self.protection_handler.protect_content(
                    content_info,
                    ProtectionLevel.STANDARD
                )
                
                if protection_success:
                    # Check for violations
                    violations = await self.protection_handler.check_content_violations(content_info)
                    
                    if violations:
                        await self.event_publisher.publish(
                            "content.violations_detected",
                            {
                                "content_id": content_info.content_id,
                                "session_id": content_info.session_id,
                                "violations": violations
                            }
                        )
            
            # Mark as ready
            content_info.processing_state = ContentState.READY
            
            # Publish completion event
            await self.event_publisher.publish(
                "content.processing_completed",
                {
                    "content_id": content_info.content_id,
                    "session_id": content_info.session_id,
                    "processing_state": content_info.processing_state.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {str(e)}")
            content_info.processing_state = ContentState.PROCESSING_ERROR
    
    def _detect_content_type(self, filename: str, file_data: bytes) -> ContentType:
        """Detect content type from filename and data"""
        
        try:
            # Use python-magic for MIME type detection
            mime_type = magic.from_buffer(file_data, mime=True)
            
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                return ContentType.TEXT
            elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return ContentType.DOCUMENT
            elif mime_type in ['application/zip', 'application/x-rar', 'application/x-tar']:
                return ContentType.ARCHIVE
            else:
                # Fallback to filename extension
                extension = Path(filename).suffix.lower()
                extension_map = {
                    '.mp3': ContentType.AUDIO, '.wav': ContentType.AUDIO, '.flac': ContentType.AUDIO,
                    '.mp4': ContentType.VIDEO, '.avi': ContentType.VIDEO, '.mov': ContentType.VIDEO,
                    '.jpg': ContentType.IMAGE, '.jpeg': ContentType.IMAGE, '.png': ContentType.IMAGE,
                    '.txt': ContentType.TEXT, '.md': ContentType.TEXT,
                    '.pdf': ContentType.DOCUMENT, '.docx': ContentType.DOCUMENT,
                    '.zip': ContentType.ARCHIVE, '.rar': ContentType.ARCHIVE
                }
                
                return extension_map.get(extension, ContentType.UNKNOWN)
                
        except Exception as e:
            self.logger.error(f"Content type detection failed: {str(e)}")
            return ContentType.UNKNOWN
    
    def _detect_content_format(self, filename: str) -> ContentFormat:
        """Detect content format from filename"""
        
        try:
            extension = Path(filename).suffix.lower().replace('.', '')
            
            # Try to map extension to ContentFormat enum
            for format_enum in ContentFormat:
                if format_enum.value == extension:
                    return format_enum
            
            # Fallback mapping for common variations
            format_map = {
                'jpg': ContentFormat.JPEG,
                'tif': ContentFormat.TIFF,
                'htm': ContentFormat.HTML
            }
            
            return format_map.get(extension, ContentFormat.TXT)  # Default fallback
            
        except Exception as e:
            self.logger.error(f"Content format detection failed: {str(e)}")
            return ContentFormat.TXT
    
    async def _store_file(self, content_info: SessionContentInfo, file_data: bytes) -> str:
        """Store file in configured storage backend"""
        
        try:
            if self.config.storage_backend == "s3" and self.storage_client:
                # Generate S3 key
                s3_key = f"sessions/{content_info.session_id}/content/{content_info.content_id}_{content_info.filename}"
                
                # Upload to S3
                self.storage_client.put_object(
                    Bucket=settings.S3_BUCKET,
                    Key=s3_key,
                    Body=file_data,
                    ContentType=content_info.mime_type
                )
                
                return f"s3://{settings.S3_BUCKET}/{s3_key}"
            
            else:
                # Local storage fallback
                local_dir = Path(settings.LOCAL_STORAGE_PATH) / "sessions" / content_info.session_id / "content"
                local_dir.mkdir(parents=True, exist_ok=True)
                
                local_path = local_dir / f"{content_info.content_id}_{content_info.filename}"
                
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                
                return str(local_path)
                
        except Exception as e:
            self.logger.error(f"File storage failed: {str(e)}")
            return ""
    
    async def get_session_content(self, session_id: str) -> List[SessionContentInfo]:
        """Get all content for session"""
        
        try:
            content_ids = self.session_content.get(session_id, [])
            content_list = []
            
            for content_id in content_ids:
                # Load content info from cache or database
                content_info = await self._get_content_info(content_id)
                if content_info:
                    content_list.append(content_info)
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Session content retrieval failed: {str(e)}")
            return []
    
    async def _get_content_info(self, content_id: str) -> Optional[SessionContentInfo]:
        """Get content information"""
        
        try:
            # Try cache first
            cache_key = f"content_info:{content_id}"
            cached_data = await self.cache_manager.get(cache_key)
            
            if cached_data:
                return SessionContentInfo.parse_raw(cached_data)
            
            # Load from database
            async with get_async_session() as session:
                query = select(ContentModel).where(ContentModel.content_id == content_id)
                result = await session.execute(query)
                content_record = result.scalar_one_or_none()
                
                if content_record:
                    content_info = SessionContentInfo(
                        content_id=content_id,
                        session_id=content_record.session_id,
                        user_id=content_record.user_id,
                        content_type=ContentType(content_record.content_type),
                        content_format=ContentFormat.TXT,  # Would be stored in DB
                        filename=content_record.filename,
                        file_size=0,  # Would be stored in DB
                        file_hash=content_record.file_hash,
                        mime_type="",  # Would be stored in DB
                        upload_timestamp=content_record.created_at,
                        protection_level=ProtectionLevel(content_record.protection_level),
                        fingerprint_data=content_record.fingerprint_data or {}
                    )
                    
                    # Cache for future access
                    await self.cache_manager.set(
                        cache_key,
                        content_info.json(),
                        ttl=3600
                    )
                    
                    return content_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Content info retrieval failed: {str(e)}")
            return None
    
    async def delete_content(self, content_id: str, session_id: str) -> bool:
        """Delete content from session"""
        
        try:
            # Remove from session tracking
            if session_id in self.session_content:
                if content_id in self.session_content[session_id]:
                    self.session_content[session_id].remove(content_id)
            
            # Remove from media session
            media_state = await self.media_state_manager._get_media_state(session_id)
            if media_state and content_id in media_state.active_content:
                media_state.active_content.remove(content_id)
                await self.media_state_manager._store_media_state(media_state)
            
            # Delete from storage and database would be implemented here
            
            await self.metrics_collector.increment("content_manager.deletions")
            return True
            
        except Exception as e:
            self.logger.error(f"Content deletion failed: {str(e)}")
            return False
    
    async def initiate_chunked_upload(
        self,
        session_id: str,
        user_id: str,
        filename: str,
        total_size: int,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate a chunked upload session"""
        try:
            # Generate upload session ID
            upload_id = f"upload_{uuid.uuid4().hex}"
            
            # Calculate total chunks
            total_chunks = math.ceil(total_size / chunk_size)
            
            # Create upload session metadata
            upload_session = {
                'upload_id': upload_id,
                'session_id': session_id,
                'user_id': user_id,
                'filename': filename,
                'total_size': total_size,
                'chunk_size': chunk_size,
                'total_chunks': total_chunks,
                'completed_chunks': set(),
                'content_type': content_type,
                'created_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=24),
                'status': 'active',
                'file_hash_parts': {},
                'resumable': True
            }
            
            # Store upload session (in production, use Redis or database)
            if not hasattr(self, '_upload_sessions'):
                self._upload_sessions = {}
            self._upload_sessions[upload_id] = upload_session
            
            self.logger.info(f"Chunked upload initiated: {upload_id}")
            
            return {
                'upload_id': upload_id,
                'chunk_size': chunk_size,
                'total_chunks': total_chunks,
                'expires_at': upload_session['expires_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Chunked upload initiation failed: {str(e)}")
            return None
    
    async def upload_chunk(
        self,
        upload_id: str,
        chunk_index: int,
        chunk_data: bytes
    ) -> Dict[str, Any]:
        """Upload a single chunk"""
        try:
            if not hasattr(self, '_upload_sessions'):
                self._upload_sessions = {}
                
            if upload_id not in self._upload_sessions:
                return {'success': False, 'error': 'Upload session not found'}
            
            upload_session = self._upload_sessions[upload_id]
            
            # Check if upload session is still valid
            if datetime.now(timezone.utc) > upload_session['expires_at']:
                return {'success': False, 'error': 'Upload session expired'}
            
            # Validate chunk index
            if chunk_index >= upload_session['total_chunks'] or chunk_index < 0:
                return {'success': False, 'error': 'Invalid chunk index'}
            
            # Check if chunk already uploaded
            if chunk_index in upload_session['completed_chunks']:
                return {'success': True, 'message': 'Chunk already uploaded'}
            
            # Store chunk (in production, store to file system or cloud storage)
            chunk_path = f"/tmp/chunks/{upload_id}/chunk_{chunk_index}"
            os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
            
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data)
            
            # Calculate chunk hash for integrity verification
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            upload_session['file_hash_parts'][chunk_index] = chunk_hash
            
            # Mark chunk as completed
            upload_session['completed_chunks'].add(chunk_index)
            
            # Update progress
            progress = len(upload_session['completed_chunks']) / upload_session['total_chunks'] * 100
            
            self.logger.debug(f"Chunk {chunk_index} uploaded for {upload_id}, progress: {progress:.1f}%")
            
            return {
                'success': True,
                'chunk_index': chunk_index,
                'progress': progress,
                'completed_chunks': len(upload_session['completed_chunks']),
                'total_chunks': upload_session['total_chunks']
            }
            
        except Exception as e:
            self.logger.error(f"Chunk upload failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def finalize_chunked_upload(self, upload_id: str) -> Optional[SessionContentInfo]:
        """Finalize chunked upload by combining all chunks"""
        try:
            if not hasattr(self, '_upload_sessions'):
                return None
                
            if upload_id not in self._upload_sessions:
                return None
            
            upload_session = self._upload_sessions[upload_id]
            
            # Check if all chunks are uploaded
            if len(upload_session['completed_chunks']) != upload_session['total_chunks']:
                missing_chunks = set(range(upload_session['total_chunks'])) - upload_session['completed_chunks']
                self.logger.warning(f"Missing chunks for {upload_id}: {missing_chunks}")
                return None
            
            # Combine chunks into final file
            final_data = b''
            for chunk_index in range(upload_session['total_chunks']):
                chunk_path = f"/tmp/chunks/{upload_id}/chunk_{chunk_index}"
                with open(chunk_path, 'rb') as f:
                    chunk_data = f.read()
                    final_data += chunk_data
                
                # Verify chunk integrity
                expected_hash = upload_session['file_hash_parts'][chunk_index]
                actual_hash = hashlib.sha256(chunk_data).hexdigest()
                if expected_hash != actual_hash:
                    self.logger.error(f"Chunk {chunk_index} integrity check failed")
                    return None
            
            # Verify total file size
            if len(final_data) != upload_session['total_size']:
                self.logger.error(f"File size mismatch: expected {upload_session['total_size']}, got {len(final_data)}")
                return None
            
            # Upload using existing upload_content method
            content_info = await self.upload_content(
                upload_session['session_id'],
                upload_session['user_id'],
                final_data,
                upload_session['filename'],
                upload_session['content_type']
            )
            
            if content_info:
                # Clean up temporary files
                chunk_dir = f"/tmp/chunks/{upload_id}"
                if os.path.exists(chunk_dir):
                    shutil.rmtree(chunk_dir)
                
                # Remove upload session
                del self._upload_sessions[upload_id]
                
                self.logger.info(f"Chunked upload finalized: {upload_id} -> {content_info.content_id}")
            
            return content_info
            
        except Exception as e:
            self.logger.error(f"Chunked upload finalization failed: {str(e)}")
            return None
    
    async def resume_upload(self, upload_id: str) -> Dict[str, Any]:
        """Get upload session status for resume capability"""
        try:
            if not hasattr(self, '_upload_sessions'):
                return {'success': False, 'error': 'No upload sessions found'}
                
            if upload_id not in self._upload_sessions:
                return {'success': False, 'error': 'Upload session not found'}
            
            upload_session = self._upload_sessions[upload_id]
            
            # Check if upload session is still valid
            if datetime.now(timezone.utc) > upload_session['expires_at']:
                return {'success': False, 'error': 'Upload session expired'}
            
            missing_chunks = set(range(upload_session['total_chunks'])) - upload_session['completed_chunks']
            
            return {
                'success': True,
                'upload_id': upload_id,
                'filename': upload_session['filename'],
                'total_chunks': upload_session['total_chunks'],
                'completed_chunks': len(upload_session['completed_chunks']),
                'missing_chunks': sorted(list(missing_chunks)),
                'progress': len(upload_session['completed_chunks']) / upload_session['total_chunks'] * 100,
                'expires_at': upload_session['expires_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Resume upload check failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_content_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive content manager statistics"""
        
        try:
            total_sessions = len(self.session_content)
            total_content = sum(len(content_list) for content_list in self.session_content.values())
            
            return {
                "total_sessions_with_content": total_sessions,
                "total_content_items": total_content,
                "active_media_sessions": len(self.media_state_manager.media_sessions),
                "configuration": {
                    "max_file_size_mb": self.config.max_file_size_mb,
                    "storage_backend": self.config.storage_backend,
                    "auto_protection_enabled": self.config.enable_auto_protection,
                    "auto_analysis_enabled": self.config.enable_auto_analysis,
                    "content_optimization_enabled": self.config.enable_content_optimization
                }
            }
            
        except Exception as e:
            self.logger.error(f"Statistics calculation failed: {str(e)}")
            return {}
    
    async def _extract_metadata(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Extract metadata from various file types automatically"""
        try:
            metadata = {
                'filename': filename,
                'file_size': len(file_data),
                'content_type': content_type,
                'extraction_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Get file extension
            file_ext = Path(filename).suffix.lower()
            
            # Image metadata extraction
            if content_type.startswith('image/'):
                metadata.update(await self._extract_image_metadata(file_data, file_ext))
            
            # Audio metadata extraction
            elif content_type.startswith('audio/'):
                metadata.update(await self._extract_audio_metadata(file_data, file_ext))
            
            # Video metadata extraction
            elif content_type.startswith('video/'):
                metadata.update(await self._extract_video_metadata(file_data, file_ext))
            
            # Document metadata extraction
            elif content_type in ['application/pdf', 'application/msword', 'text/plain']:
                metadata.update(await self._extract_document_metadata(file_data, file_ext))
            
            # Archive metadata extraction
            elif file_ext in ['.zip', '.rar', '.tar', '.gz']:
                metadata.update(await self._extract_archive_metadata(file_data, file_ext))
            
            # Basic file analysis for any type
            metadata.update(await self._extract_basic_metadata(file_data, filename))
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            return {'error': str(e)}
    
    async def _extract_image_metadata(self, file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Extract metadata from image files"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            import io
            
            metadata = {'type': 'image'}
            
            # Use PIL to extract image metadata
            with Image.open(io.BytesIO(file_data)) as img:
                metadata.update({
                    'dimensions': f"{img.width}x{img.height}",
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': 'transparency' in img.info
                })
                
                # Extract EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                if exif_data:
                    metadata['exif'] = exif_data
                    
                    # Extract common EXIF fields
                    if 'DateTime' in exif_data:
                        metadata['date_taken'] = exif_data['DateTime']
                    if 'Make' in exif_data:
                        metadata['camera_make'] = exif_data['Make']
                    if 'Model' in exif_data:
                        metadata['camera_model'] = exif_data['Model']
                    if 'GPSInfo' in exif_data:
                        metadata['has_gps'] = True
            
            return metadata
            
        except Exception as e:
            return {'image_extraction_error': str(e)}
    
    async def _extract_audio_metadata(self, file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Extract metadata from audio files"""
        try:
            import mutagen
            import io
            
            metadata = {'type': 'audio'}
            
            # Save to temporary file for mutagen processing
            temp_file = f"/tmp/temp_audio_{uuid.uuid4().hex}{file_ext}"
            with open(temp_file, 'wb') as f:
                f.write(file_data)
            
            try:
                audio_file = mutagen.File(temp_file)
                if audio_file:
                    metadata.update({
                        'duration': getattr(audio_file.info, 'length', 0),
                        'bitrate': getattr(audio_file.info, 'bitrate', 0),
                        'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
                        'channels': getattr(audio_file.info, 'channels', 0)
                    })
                    
                    # Extract tags
                    if audio_file.tags:
                        tags = {}
                        for key, value in audio_file.tags.items():
                            if isinstance(value, list):
                                tags[key] = str(value[0]) if value else ''
                            else:
                                tags[key] = str(value)
                        metadata['tags'] = tags
                        
                        # Common tag mappings
                        title = tags.get('TIT2') or tags.get('TITLE') or tags.get('\xa9nam')
                        artist = tags.get('TPE1') or tags.get('ARTIST') or tags.get('\xa9ART')
                        album = tags.get('TALB') or tags.get('ALBUM') or tags.get('\xa9alb')
                        
                        if title:
                            metadata['title'] = title
                        if artist:
                            metadata['artist'] = artist
                        if album:
                            metadata['album'] = album
                            
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return metadata
            
        except Exception as e:
            return {'audio_extraction_error': str(e)}
    
    async def _extract_video_metadata(self, file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Extract metadata from video files"""
        try:
            metadata = {'type': 'video'}
            
            # For video metadata extraction, we would typically use ffprobe or similar
            # For now, provide basic analysis
            metadata.update({
                'estimated_duration': 'unknown',
                'estimated_resolution': 'unknown',
                'estimated_codec': 'unknown'
            })
            
            # Basic video file format detection
            if file_ext in ['.mp4', '.mov']:
                metadata['container'] = 'mp4'
            elif file_ext in ['.avi']:
                metadata['container'] = 'avi'
            elif file_ext in ['.mkv']:
                metadata['container'] = 'matroska'
            elif file_ext in ['.webm']:
                metadata['container'] = 'webm'
            
            return metadata
            
        except Exception as e:
            return {'video_extraction_error': str(e)}
    
    async def _extract_document_metadata(self, file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Extract metadata from document files"""
        try:
            metadata = {'type': 'document'}
            
            if file_ext == '.pdf':
                # PDF metadata extraction
                try:
                    import PyPDF2
                    import io
                    
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
                    metadata.update({
                        'page_count': len(pdf_reader.pages),
                        'encrypted': pdf_reader.is_encrypted
                    })
                    
                    if pdf_reader.metadata:
                        pdf_metadata = pdf_reader.metadata
                        metadata['pdf_metadata'] = {
                            'title': pdf_metadata.get('/Title', ''),
                            'author': pdf_metadata.get('/Author', ''),
                            'subject': pdf_metadata.get('/Subject', ''),
                            'creator': pdf_metadata.get('/Creator', ''),
                            'producer': pdf_metadata.get('/Producer', ''),
                            'creation_date': str(pdf_metadata.get('/CreationDate', '')),
                            'modification_date': str(pdf_metadata.get('/ModDate', ''))
                        }
                except ImportError:
                    metadata['pdf_extraction_error'] = 'PyPDF2 not available'
                    
            elif file_ext == '.txt':
                # Text file analysis
                try:
                    text_content = file_data.decode('utf-8')
                    metadata.update({
                        'character_count': len(text_content),
                        'line_count': text_content.count('\n') + 1,
                        'word_count': len(text_content.split()),
                        'encoding': 'utf-8'
                    })
                except UnicodeDecodeError:
                    metadata['encoding_error'] = 'Cannot decode as UTF-8'
            
            return metadata
            
        except Exception as e:
            return {'document_extraction_error': str(e)}
    
    async def _extract_archive_metadata(self, file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Extract metadata from archive files"""
        try:
            metadata = {'type': 'archive', 'format': file_ext}
            
            if file_ext == '.zip':
                try:
                    import zipfile
                    import io
                    
                    with zipfile.ZipFile(io.BytesIO(file_data)) as zip_file:
                        file_list = zip_file.namelist()
                        metadata.update({
                            'file_count': len(file_list),
                            'compressed_size': len(file_data),
                            'has_directories': any('/' in name for name in file_list),
                            'file_extensions': list(set(Path(name).suffix.lower() for name in file_list if Path(name).suffix))
                        })
                        
                        # Calculate uncompressed size
                        uncompressed_size = sum(info.file_size for info in zip_file.infolist())
                        metadata['uncompressed_size'] = uncompressed_size
                        metadata['compression_ratio'] = len(file_data) / uncompressed_size if uncompressed_size > 0 else 0
                        
                except zipfile.BadZipFile:
                    metadata['archive_error'] = 'Invalid ZIP file'
            
            return metadata
            
        except Exception as e:
            return {'archive_extraction_error': str(e)}
    
    async def _extract_basic_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract basic metadata for any file type"""
        try:
            metadata = {}
            
            # File hash for deduplication
            metadata['md5_hash'] = hashlib.md5(file_data).hexdigest()
            metadata['sha1_hash'] = hashlib.sha1(file_data).hexdigest()
            
            # Basic file analysis
            metadata['entropy'] = self._calculate_entropy(file_data[:1024])  # First 1KB for performance
            metadata['is_binary'] = self._is_binary_file(file_data[:512])
            
            # File signature/magic number detection
            file_signature = file_data[:16].hex() if len(file_data) >= 16 else file_data.hex()
            metadata['file_signature'] = file_signature
            metadata['magic_number'] = self._detect_file_type_by_signature(file_data[:16])
            
            return metadata
            
        except Exception as e:
            return {'basic_extraction_error': str(e)}
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = [0] * 256
        for byte in data:
            frequencies[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for freq in frequencies:
            if freq > 0:
                probability = freq / data_len
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _is_binary_file(self, data: bytes) -> bool:
        """Detect if file is binary based on content"""
        if not data:
            return False
        
        # Check for null bytes (common in binary files)
        if b'\x00' in data:
            return True
        
        # Check for high entropy (random-looking data)
        entropy = self._calculate_entropy(data)
        return entropy > 7.0  # High entropy threshold
    
    def _detect_file_type_by_signature(self, data: bytes) -> str:
        """Detect file type by magic number/signature"""
        if not data:
            return 'unknown'
        
        signatures = {
            b'\xFF\xD8\xFF': 'jpeg',
            b'\x89PNG\r\n\x1a\n': 'png',
            b'GIF87a': 'gif87a',
            b'GIF89a': 'gif89a',
            b'RIFF': 'riff',  # Could be WAV, AVI, etc.
            b'%PDF': 'pdf',
            b'PK\x03\x04': 'zip',
            b'PK\x05\x06': 'zip_empty',
            b'Rar!': 'rar',
            b'\x7fELF': 'elf',
            b'MZ': 'exe',
            b'\xCA\xFE\xBA\xBE': 'java_class'
        }
        
        for signature, file_type in signatures.items():
            if data.startswith(signature):
                return file_type
        
        return 'unknown'


class CDNIntegration:
    """
    CDN Integration for content delivery optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # CDN providers configuration
        self.providers = {
            'cloudfront': {
                'enabled': self.config.get('cloudfront_enabled', False),
                'distribution_id': self.config.get('cloudfront_distribution_id'),
                'domain': self.config.get('cloudfront_domain'),
                'region': self.config.get('aws_region', 'us-east-1')
            },
            'fastly': {
                'enabled': self.config.get('fastly_enabled', False),
                'service_id': self.config.get('fastly_service_id'),
                'api_key': self.config.get('fastly_api_key'),
                'domain': self.config.get('fastly_domain')
            },
            'cloudflare': {
                'enabled': self.config.get('cloudflare_enabled', False),
                'zone_id': self.config.get('cloudflare_zone_id'),
                'api_token': self.config.get('cloudflare_api_token'),
                'domain': self.config.get('cloudflare_domain')
            }
        }
        
        # Content optimization settings
        self.optimization_config = {
            'auto_compression': self.config.get('auto_compression', True),
            'image_optimization': self.config.get('image_optimization', True),
            'cache_ttl': self.config.get('cache_ttl', 3600),
            'edge_locations': self.config.get('edge_locations', ['us-east-1', 'eu-west-1'])
        }
    
    async def upload_to_cdn(
        self,
        content_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Upload content to CDN with optimization"""
        try:
            result = {
                'success': False,
                'content_id': content_id,
                'urls': {},
                'cache_info': {}
            }
            
            # Optimize content before upload
            optimized_data = await self._optimize_content(file_data, content_type, filename)
            
            # Upload to enabled CDN providers
            for provider_name, provider_config in self.providers.items():
                if provider_config.get('enabled'):
                    upload_result = await self._upload_to_provider(
                        provider_name, content_id, optimized_data, filename, content_type, metadata
                    )
                    
                    if upload_result['success']:
                        result['urls'][provider_name] = upload_result['url']
                        result['cache_info'][provider_name] = upload_result.get('cache_info', {})
                        result['success'] = True
            
            # Set cache headers and optimization metadata
            if result['success']:
                result['cache_headers'] = {
                    'Cache-Control': f"public, max-age={self.optimization_config['cache_ttl']}",
                    'Content-Type': content_type,
                    'Content-Length': str(len(optimized_data)),
                    'ETag': hashlib.md5(optimized_data).hexdigest(),
                    'X-Content-Optimized': 'true' if optimized_data != file_data else 'false'
                }
                
                result['optimization_stats'] = {
                    'original_size': len(file_data),
                    'optimized_size': len(optimized_data),
                    'compression_ratio': len(optimized_data) / len(file_data) if file_data else 1.0,
                    'optimization_applied': optimized_data != file_data
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"CDN upload failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_cdn_status(self) -> Dict[str, Any]:
        """Get CDN integration status"""
        return {
            'providers': {
                name: {
                    'enabled': config.get('enabled', False),
                    'configured': bool(config.get('domain'))
                }
                for name, config in self.providers.items()
            },
            'optimization': self.optimization_config
        }
    
    async def _optimize_content(self, file_data: bytes, content_type: str, filename: str) -> bytes:
        """Optimize content for CDN delivery"""
        try:
            if not self.optimization_config.get('auto_compression'):
                return file_data
            
            # For demo purposes, return original data
            # In production, implement actual optimization
            return file_data
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return file_data
    
    async def _upload_to_provider(
        self,
        provider: str,
        content_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Upload to specific CDN provider"""
        try:
            # Simplified implementation for demo
            domain = self.providers[provider].get('domain', f'{provider}.example.com')
            cdn_url = f"https://{domain}/content/{content_id}/{filename}"
            
            return {
                'success': True,
                'url': cdn_url,
                'provider': provider,
                'cache_info': {
                    'ttl': self.optimization_config['cache_ttl']
                }
            }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
