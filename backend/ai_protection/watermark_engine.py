"""Watermark Engine

Advanced audio/video watermarking engine for content protection.
Integrates with existing watermarking functionality to provide comprehensive protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid
import numpy as np

try:
    import librosa
    import soundfile as sf
    import cv2
    from PIL import Image
    MEDIA_AVAILABLE = True
except ImportError:
    MEDIA_AVAILABLE = False

# Import existing watermarking engines
from protection.watermarking.audio_engine import AudioWatermarkEngine
from protection.watermarking.video_engine import VideoWatermarkEngine
from protection.watermarking.image_engine import ImageWatermarkEngine

logger = logging.getLogger(__name__)


class WatermarkType(Enum):
    """Types of watermarks"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    ROBUST = "robust"
    FRAGILE = "fragile"
    SEMI_FRAGILE = "semi_fragile"


class ContentType(Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


@dataclass
class WatermarkConfig:
    """Watermark configuration"""
    watermark_type: WatermarkType
    strength: float = 0.5
    redundancy: int = 3
    encryption_key: Optional[str] = None
    detection_threshold: float = 0.8
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WatermarkResult:
    """Watermark operation result"""
    success: bool
    watermark_id: str
    content_hash: str
    watermark_data: Dict[str, Any]
    processing_time: float
    quality_metrics: Dict[str, float]
    error: Optional[str] = None


class WatermarkEngine:
    """Advanced watermarking engine for multimedia content"""
    
    def __init__(self) -> None:
        """Initialize watermark engine"""
        self.audio_engine = None
        self.video_engine = None
        self.image_engine = None
        
        if MEDIA_AVAILABLE:
            try:
                self.audio_engine = AudioWatermarkEngine()
                self.video_engine = VideoWatermarkEngine()
                self.image_engine = ImageWatermarkEngine()
                logger.info("Watermark engines initialized successfully")
            except Exception as e:
                logger.warning(f"Some watermark engines failed to initialize: {e}")
        else:
            logger.warning("Media processing libraries not available")
            
        self._watermark_registry = {}
    
    async def embed_watermark(self,
                            content_data: Union[bytes, BinaryIO],
                            content_type: ContentType,
                            watermark_message: str,
                            owner_id: str,
                            config: Optional[WatermarkConfig] = None) -> WatermarkResult:
        """
        Embed watermark into content
        
        Args:
            content_data: Content to watermark
            content_type: Type of content
            watermark_message: Message to embed
            owner_id: Content owner identifier
            config: Watermark configuration
            
        Returns:
            Watermark embedding result
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            if config is None:
                config = WatermarkConfig(WatermarkType.INVISIBLE)
            
            # Generate watermark ID
            watermark_id = str(uuid.uuid4())
            
            # Calculate content hash
            if isinstance(content_data, bytes):
                content_bytes = content_data
            else:
                content_bytes = content_data.read()
                content_data.seek(0)
            
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Select appropriate engine and embed watermark
            if content_type == ContentType.AUDIO:
                result = await self._embed_audio_watermark(
                    content_bytes, watermark_message, watermark_id, config
                )
            elif content_type == ContentType.VIDEO:
                result = await self._embed_video_watermark(
                    content_bytes, watermark_message, watermark_id, config
                )
            elif content_type == ContentType.IMAGE:
                result = await self._embed_image_watermark(
                    content_bytes, watermark_message, watermark_id, config
                )
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Store watermark metadata
            watermark_metadata = {
                'watermark_id': watermark_id,
                'content_hash': content_hash,
                'owner_id': owner_id,
                'content_type': content_type.value,
                'watermark_message': watermark_message,
                'config': config.__dict__,
                'embedding_timestamp': start_time,
                'processing_time': processing_time
            }
            
            self._watermark_registry[watermark_id] = watermark_metadata
            
            return WatermarkResult(
                success=True,
                watermark_id=watermark_id,
                content_hash=content_hash,
                watermark_data=result,
                processing_time=processing_time,
                quality_metrics=result.get('quality_metrics', {})
            )
            
        except Exception as e:
            logger.error(f"Watermark embedding failed: {e}")
            return WatermarkResult(
                success=False,
                watermark_id="",
                content_hash="",
                watermark_data={},
                processing_time=0,
                quality_metrics={},
                error=str(e)
            )
    
    async def detect_watermark(self,
                             content_data: Union[bytes, BinaryIO],
                             content_type: ContentType,
                             watermark_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect watermark in content
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            watermark_id: Optional specific watermark to detect
            
        Returns:
            Detection result with watermark information
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Convert content to bytes
            if isinstance(content_data, bytes):
                content_bytes = content_data
            else:
                content_bytes = content_data.read()
                content_data.seek(0)
            
            # Select appropriate engine and detect watermark
            if content_type == ContentType.AUDIO:
                detection_result = await self._detect_audio_watermark(content_bytes)
            elif content_type == ContentType.VIDEO:
                detection_result = await self._detect_video_watermark(content_bytes)
            elif content_type == ContentType.IMAGE:
                detection_result = await self._detect_image_watermark(content_bytes)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Enhance detection result with metadata
            if detection_result.get('detected') and detection_result.get('watermark_id'):
                detected_id = detection_result['watermark_id']
                if detected_id in self._watermark_registry:
                    detection_result['metadata'] = self._watermark_registry[detected_id]
            
            detection_result['processing_time'] = processing_time
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Watermark detection failed: {e}")
            return {
                'detected': False,
                'error': str(e),
                'processing_time': 0
            }
    
    async def extract_watermark(self,
                              content_data: Union[bytes, BinaryIO],
                              content_type: ContentType,
                              watermark_id: str) -> Dict[str, Any]:
        """
        Extract watermark message from content
        
        Args:
            content_data: Content to extract from
            content_type: Type of content
            watermark_id: Watermark identifier
            
        Returns:
            Extraction result with watermark message
        """
        try:
            # First detect the watermark
            detection_result = await self.detect_watermark(content_data, content_type, watermark_id)
            
            if not detection_result.get('detected'):
                return {
                    'extracted': False,
                    'error': 'Watermark not detected'
                }
            
            # Extract the watermark message
            if isinstance(content_data, bytes):
                content_bytes = content_data
            else:
                content_bytes = content_data.read()
                content_data.seek(0)
            
            if content_type == ContentType.AUDIO:
                extraction_result = await self._extract_audio_watermark(content_bytes, watermark_id)
            elif content_type == ContentType.VIDEO:
                extraction_result = await self._extract_video_watermark(content_bytes, watermark_id)
            elif content_type == ContentType.IMAGE:
                extraction_result = await self._extract_image_watermark(content_bytes, watermark_id)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            return extraction_result
            
        except Exception as e:
            logger.error(f"Watermark extraction failed: {e}")
            return {
                'extracted': False,
                'error': str(e)
            }
    
    async def verify_integrity(self,
                             original_content: Union[bytes, BinaryIO],
                             modified_content: Union[bytes, BinaryIO],
                             content_type: ContentType) -> Dict[str, Any]:
        """
        Verify content integrity using watermarks
        
        Args:
            original_content: Original content
            modified_content: Modified content to verify
            content_type: Type of content
            
        Returns:
            Integrity verification result
        """
        try:
            # Detect watermarks in both versions
            original_detection = await self.detect_watermark(original_content, content_type)
            modified_detection = await self.detect_watermark(modified_content, content_type)
            
            integrity_score = 0.0
            
            if original_detection.get('detected') and modified_detection.get('detected'):
                # Compare watermark strength and quality
                original_strength = original_detection.get('strength', 0)
                modified_strength = modified_detection.get('strength', 0)
                
                if original_strength > 0:
                    integrity_score = min(modified_strength / original_strength, 1.0)
                
                # Check if watermark IDs match
                ids_match = (original_detection.get('watermark_id') == 
                           modified_detection.get('watermark_id'))
                
                return {
                    'integrity_verified': ids_match and integrity_score > 0.7,
                    'integrity_score': integrity_score,
                    'watermark_ids_match': ids_match,
                    'original_detection': original_detection,
                    'modified_detection': modified_detection,
                    'degradation_level': 1.0 - integrity_score
                }
            else:
                return {
                    'integrity_verified': False,
                    'integrity_score': 0.0,
                    'error': 'Watermark not detected in one or both versions'
                }
                
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return {
                'integrity_verified': False,
                'error': str(e)
            }
    
    async def _embed_audio_watermark(self,
                                   content_bytes: bytes,
                                   message: str,
                                   watermark_id: str,
                                   config: WatermarkConfig) -> Dict[str, Any]:
        """Embed watermark in audio content"""
        if not self.audio_engine:
            raise Exception("Audio watermarking not available")
        
        # Convert message to bits for embedding
        message_bits = [int(b) for b in ''.join(format(ord(c), '08b') for c in message)]
        
        try:
            # Use existing audio watermarking functionality
            result = await self.audio_engine.embed_watermark(
                content_bytes,
                message_bits,
                watermark_id=watermark_id,
                strength=config.strength
            )
            
            return {
                'watermarked_content': result.get('watermarked_audio', b''),
                'quality_metrics': result.get('quality_metrics', {}),
                'embedding_success': result.get('success', False)
            }
            
        except Exception as e:
            logger.error(f"Audio watermark embedding failed: {e}")
            return {
                'watermarked_content': b'',
                'quality_metrics': {},
                'embedding_success': False,
                'error': str(e)
            }
    
    async def _embed_video_watermark(self,
                                   content_bytes: bytes,
                                   message: str,
                                   watermark_id: str,
                                   config: WatermarkConfig) -> Dict[str, Any]:
        """Embed watermark in video content"""
        if not self.video_engine:
            raise Exception("Video watermarking not available")
        
        message_bits = [int(b) for b in ''.join(format(ord(c), '08b') for c in message)]
        
        try:
            result = await self.video_engine.embed_watermark(
                content_bytes,
                message_bits,
                watermark_id=watermark_id
            )
            
            return {
                'watermarked_content': result.get('watermarked_video', b''),
                'quality_metrics': result.get('quality_metrics', {}),
                'embedding_success': result.get('success', False)
            }
            
        except Exception as e:
            logger.error(f"Video watermark embedding failed: {e}")
            return {
                'watermarked_content': b'',
                'quality_metrics': {},
                'embedding_success': False,
                'error': str(e)
            }
    
    async def _embed_image_watermark(self,
                                   content_bytes: bytes,
                                   message: str,
                                   watermark_id: str,
                                   config: WatermarkConfig) -> Dict[str, Any]:
        """Embed watermark in image content"""
        if not self.image_engine:
            raise Exception("Image watermarking not available")
        
        try:
            result = await self.image_engine.embed_text_watermark(
                content_bytes,
                message,
                watermark_id=watermark_id,
                strength=config.strength
            )
            
            return {
                'watermarked_content': result.get('watermarked_image', b''),
                'quality_metrics': result.get('quality_metrics', {}),
                'embedding_success': result.get('success', False)
            }
            
        except Exception as e:
            logger.error(f"Image watermark embedding failed: {e}")
            return {
                'watermarked_content': b'',
                'quality_metrics': {},
                'embedding_success': False,
                'error': str(e)
            }
    
    async def _detect_audio_watermark(self, content_bytes: bytes) -> Dict[str, Any]:
        """Detect watermark in audio content"""
        if not self.audio_engine:
            return {'detected': False, 'error': 'Audio engine not available'}
        
        try:
            result = await self.audio_engine.detect_watermark(content_bytes)
            return {
                'detected': result.get('detected', False),
                'watermark_id': result.get('watermark_id'),
                'strength': result.get('strength', 0.0),
                'confidence': result.get('confidence', 0.0)
            }
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    async def _detect_video_watermark(self, content_bytes: bytes) -> Dict[str, Any]:
        """Detect watermark in video content"""
        if not self.video_engine:
            return {'detected': False, 'error': 'Video engine not available'}
        
        try:
            result = await self.video_engine.detect_watermark(content_bytes)
            return {
                'detected': result.get('detected', False),
                'watermark_id': result.get('watermark_id'),
                'strength': result.get('strength', 0.0),
                'confidence': result.get('confidence', 0.0)
            }
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    async def _detect_image_watermark(self, content_bytes: bytes) -> Dict[str, Any]:
        """Detect watermark in image content"""
        if not self.image_engine:
            return {'detected': False, 'error': 'Image engine not available'}
        
        try:
            result = await self.image_engine.detect_watermark(content_bytes)
            return {
                'detected': result.get('detected', False),
                'watermark_id': result.get('watermark_id'),
                'strength': result.get('strength', 0.0),
                'confidence': result.get('confidence', 0.0)
            }
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    async def _extract_audio_watermark(self, content_bytes: bytes, watermark_id: str) -> Dict[str, Any]:
        """Extract watermark message from audio"""
        if not self.audio_engine:
            return {'extracted': False, 'error': 'Audio engine not available'}
        
        try:
            result = await self.audio_engine.extract_watermark(content_bytes, watermark_id)
            return {
                'extracted': result.get('success', False),
                'message': result.get('message', ''),
                'quality': result.get('quality', 0.0)
            }
        except Exception as e:
            return {'extracted': False, 'error': str(e)}
    
    async def _extract_video_watermark(self, content_bytes: bytes, watermark_id: str) -> Dict[str, Any]:
        """Extract watermark message from video"""
        if not self.video_engine:
            return {'extracted': False, 'error': 'Video engine not available'}
        
        try:
            result = await self.video_engine.extract_watermark(content_bytes, watermark_id)
            return {
                'extracted': result.get('success', False),
                'message': result.get('message', ''),
                'quality': result.get('quality', 0.0)
            }
        except Exception as e:
            return {'extracted': False, 'error': str(e)}
    
    async def _extract_image_watermark(self, content_bytes: bytes, watermark_id: str) -> Dict[str, Any]:
        """Extract watermark message from image"""
        if not self.image_engine:
            return {'extracted': False, 'error': 'Image engine not available'}
        
        try:
            result = await self.image_engine.extract_watermark(content_bytes, watermark_id)
            return {
                'extracted': result.get('success', False),
                'message': result.get('message', ''),
                'quality': result.get('quality', 0.0)
            }
        except Exception as e:
            return {'extracted': False, 'error': str(e)}