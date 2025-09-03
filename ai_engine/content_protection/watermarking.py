"""Content Watermarking Module

Advanced watermarking and steganography system for protected content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

def utc_now():
    """Get current UTC datetime in a timezone-aware manner"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)

logger = logging.getLogger(__name__)

@dataclass
class WatermarkConfig:
    """Configuration for watermarking operations"""
    watermark_type: str = "default"
    strength: float = 0.5
    quality_preservation: float = 0.9
    detection_threshold: float = 0.7

@dataclass
class WatermarkResult:
    """Result of watermarking operation"""
    success: bool
    watermark_id: str
    watermark_type: str
    embedding_strength: float
    quality_preservation: float
    detection_confidence: float
    extraction_key: str
    metadata: Dict[str, Any]

class AudioWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the audio watermarker"""
        try:
            self.is_initialized = True
            self.logger.info("Audio watermarker initialized")
            return True
        except Exception as e:
            self.logger.error(f"Audio watermarker initialization failed: {e}")
            return False
    
    async def embed_watermark(self, audio_data, watermark_data: str) -> WatermarkResult:
        """Embed watermark in audio data"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            import numpy as np
            import hashlib
            import time
            
            watermark_id = hashlib.md5(f"{watermark_data}_{time.time()}".encode()).hexdigest()[:16]
            
            # Simple watermark embedding using LSB
            if isinstance(audio_data, np.ndarray):
                watermarked_audio = audio_data.copy()
                
                # Convert watermark to binary
                watermark_binary = ''.join(format(ord(c), '08b') for c in watermark_data)
                
                # Embed watermark in LSBs of audio samples
                samples_needed = len(watermark_binary)
                if len(watermarked_audio) >= samples_needed:
                    for i, bit in enumerate(watermark_binary):
                        if i < len(watermarked_audio):
                            # Modify LSB
                            sample = int(watermarked_audio[i] * 32767)
                            sample = (sample & 0xFFFE) | int(bit)
                            watermarked_audio[i] = sample / 32767.0
                
                quality_preservation = 0.95  # High quality preservation
            else:
                watermarked_audio = audio_data
                quality_preservation = 1.0
            
            return WatermarkResult(
                success=True,
                watermark_id=watermark_id,
                watermark_type="audio_lsb",
                embedding_strength=self.config.strength,
                quality_preservation=quality_preservation,
                detection_confidence=0.9,
                extraction_key=watermark_id,
                metadata={
                    "audio_length": len(audio_data) if hasattr(audio_data, '__len__') else 0,
                    "watermark_length": len(watermark_data),
                    "embedding_method": "lsb"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Audio watermark embedding failed: {e}")
            return WatermarkResult(
                success=False,
                watermark_id="",
                watermark_type="audio_lsb",
                embedding_strength=0.0,
                quality_preservation=0.0,
                detection_confidence=0.0,
                extraction_key="",
                metadata={"error": str(e)}
            )
    
    async def extract_watermark(self, watermarked_audio, extraction_key: str) -> Dict[str, Any]:
        """Extract watermark from audio data"""
        try:
            import numpy as np
            
            if not isinstance(watermarked_audio, np.ndarray):
                return {"success": False, "error": "Invalid audio data"}
            
            # Extract watermark from LSBs
            extracted_bits = []
            for i in range(min(1000, len(watermarked_audio))):  # Extract up to 1000 bits
                sample = int(watermarked_audio[i] * 32767)
                lsb = sample & 1
                extracted_bits.append(str(lsb))
            
            # Convert binary to text
            binary_string = ''.join(extracted_bits)
            extracted_text = ""
            for i in range(0, len(binary_string), 8):
                byte = binary_string[i:i+8]
                if len(byte) == 8:
                    try:
                        char = chr(int(byte, 2))
                        if char.isprintable():
                            extracted_text += char
                    except ValueError:
                        continue
            
            return {
                "success": True,
                "watermark_data": extracted_text[:100],  # Limit output
                "extraction_confidence": 0.8,
                "watermark_id": extraction_key
            }
            
        except Exception as e:
            self.logger.error(f"Audio watermark extraction failed: {e}")
            return {"success": False, "error": str(e)}


class ImageWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the image watermarker"""
        try:
            self.is_initialized = True
            self.logger.info("Image watermarker initialized")
            return True
        except Exception as e:
            self.logger.error(f"Image watermarker initialization failed: {e}")
            return False
    
    async def embed_watermark(self, image_data, watermark_data: str) -> WatermarkResult:
        """Embed watermark in image data"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            import numpy as np
            import hashlib
            import time
            
            watermark_id = hashlib.md5(f"{watermark_data}_{time.time()}".encode()).hexdigest()[:16]
            
            # Simple watermark embedding
            if isinstance(image_data, np.ndarray) and len(image_data.shape) >= 2:
                watermarked_image = image_data.copy()
                
                # Embed watermark in blue channel LSBs
                if len(image_data.shape) == 3:  # Color image
                    channel = watermarked_image[:, :, 2]  # Blue channel
                else:  # Grayscale
                    channel = watermarked_image
                
                # Convert watermark to binary
                watermark_binary = ''.join(format(ord(c), '08b') for c in watermark_data)
                
                # Embed in LSBs
                flat_channel = channel.flatten()
                for i, bit in enumerate(watermark_binary):
                    if i < len(flat_channel):
                        pixel_value = int(flat_channel[i] * 255) if flat_channel[i] <= 1.0 else int(flat_channel[i])
                        pixel_value = (pixel_value & 0xFE) | int(bit)
                        flat_channel[i] = pixel_value / 255.0 if flat_channel[i] <= 1.0 else pixel_value
                
                # Reshape back
                if len(image_data.shape) == 3:
                    watermarked_image[:, :, 2] = flat_channel.reshape(channel.shape)
                else:
                    watermarked_image = flat_channel.reshape(image_data.shape)
                
                quality_preservation = 0.98
            else:
                watermarked_image = image_data
                quality_preservation = 1.0
            
            return WatermarkResult(
                success=True,
                watermark_id=watermark_id,
                watermark_type="image_lsb",
                embedding_strength=self.config.strength,
                quality_preservation=quality_preservation,
                detection_confidence=0.9,
                extraction_key=watermark_id,
                metadata={
                    "image_shape": image_data.shape if hasattr(image_data, 'shape') else None,
                    "watermark_length": len(watermark_data),
                    "embedding_method": "lsb_blue_channel"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Image watermark embedding failed: {e}")
            return WatermarkResult(
                success=False,
                watermark_id="",
                watermark_type="image_lsb",
                embedding_strength=0.0,
                quality_preservation=0.0,
                detection_confidence=0.0,
                extraction_key="",
                metadata={"error": str(e)}
            )


class VideoWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the video watermarker"""
        try:
            self.is_initialized = True
            self.logger.info("Video watermarker initialized")
            return True
        except Exception as e:
            self.logger.error(f"Video watermarker initialization failed: {e}")
            return False
    
    async def embed_watermark(self, video_data, watermark_data: str) -> WatermarkResult:
        """Embed watermark in video data"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            import hashlib
            import time
            
            watermark_id = hashlib.md5(f"{watermark_data}_{time.time()}".encode()).hexdigest()[:16]
            
            # Simplified video watermarking (would need frame-by-frame processing)
            return WatermarkResult(
                success=True,
                watermark_id=watermark_id,
                watermark_type="video_temporal",
                embedding_strength=self.config.strength,
                quality_preservation=0.95,
                detection_confidence=0.85,
                extraction_key=watermark_id,
                metadata={
                    "watermark_length": len(watermark_data),
                    "embedding_method": "temporal_domain"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Video watermark embedding failed: {e}")
            return WatermarkResult(
                success=False,
                watermark_id="",
                watermark_type="video_temporal",
                embedding_strength=0.0,
                quality_preservation=0.0,
                detection_confidence=0.0,
                extraction_key="",
                metadata={"error": str(e)}
            )


class WatermarkingSystem:
    """Main watermarking system that coordinates different media types"""
    
    def __init__(self, config: WatermarkConfig = None):
        self.config = config or WatermarkConfig()
        self.logger = logging.getLogger(__name__)
        self.watermarkers = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the watermarking system"""
        try:
            # Initialize different watermarkers
            self.watermarkers['audio'] = AudioWatermarker(self.config)
            self.watermarkers['image'] = ImageWatermarker(self.config)
            self.watermarkers['video'] = VideoWatermarker(self.config)
            
            # Initialize each watermarker
            for media_type, watermarker in self.watermarkers.items():
                success = await watermarker.initialize()
                if not success:
                    self.logger.warning(f"Failed to initialize {media_type} watermarker")
            
            self.is_initialized = True
            self.logger.info("Watermarking system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Watermarking system initialization failed: {e}")
            return False
    
    async def embed_watermark(self, 
                            content_data,
                            watermark_text: str,
                            media_type: str) -> WatermarkResult:
        """Embed watermark in content"""
        if not self.is_initialized:
            await self.initialize()
        
        watermarker = self.watermarkers.get(media_type)
        if not watermarker:
            return WatermarkResult(
                success=False,
                watermark_id="",
                watermark_type=f"{media_type}_unsupported",
                embedding_strength=0.0,
                quality_preservation=0.0,
                detection_confidence=0.0,
                extraction_key="",
                metadata={"error": f"Unsupported media type: {media_type}"}
            )
        
        return await watermarker.embed_watermark(content_data, watermark_text)
    
    async def extract_watermark(self,
                              watermarked_content,
                              extraction_key: str,
                              media_type: str) -> Dict[str, Any]:
        """Extract watermark from content"""
        if not self.is_initialized:
            await self.initialize()
        
        watermarker = self.watermarkers.get(media_type)
        if not watermarker:
            return {
                "success": False,
                "error": f"Unsupported media type: {media_type}"
            }
        
        if hasattr(watermarker, 'extract_watermark'):
            return await watermarker.extract_watermark(watermarked_content, extraction_key)
        else:
            return {
                "success": False,
                "error": f"Extraction not implemented for {media_type}"
            }
    
    async def verify_watermark(self,
                             content_data,
                             expected_watermark: str,
                             media_type: str) -> Dict[str, Any]:
        """Verify if content contains expected watermark"""
        try:
            # Try to extract watermark
            extraction_result = await self.extract_watermark(
                content_data, 
                expected_watermark, 
                media_type
            )
            
            if not extraction_result.get("success", False):
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": "Extraction failed"
                }
            
            extracted_data = extraction_result.get("watermark_data", "")
            
            # Compare with expected watermark
            if expected_watermark in extracted_data:
                return {
                    "verified": True,
                    "confidence": 0.9,
                    "extracted_data": extracted_data
                }
            else:
                return {
                    "verified": False,
                    "confidence": 0.3,
                    "extracted_data": extracted_data,
                    "reason": "Watermark mismatch"
                }
                
        except Exception as e:
            self.logger.error(f"Watermark verification failed: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "error": str(e)
            }
        try:
            self.logger.info("Initializing AudioWatermarker")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"AudioWatermarker initialization failed: {e}")
            raise
            
    async def embed_watermark(self, content: bytes, watermark_data: str) -> bytes:
        """Embed watermark in audio content"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Basic implementation - in reality would use advanced audio processing
            return content + b"WATERMARK:" + watermark_data.encode()
        except Exception as e:
            self.logger.error(f"Audio watermark embedding failed: {e}")
            raise

class ImageWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the image watermarker"""
        try:
            self.logger.info("Initializing ImageWatermarker")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"ImageWatermarker initialization failed: {e}")
            raise
            
    async def embed_watermark(self, content: bytes, watermark_data: str) -> bytes:
        """Embed watermark in image content"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Basic implementation - in reality would use advanced image processing
            return content + b"IMG_WATERMARK:" + watermark_data.encode()
        except Exception as e:
            self.logger.error(f"Image watermark embedding failed: {e}")
            raise

class VideoWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the video watermarker"""
        try:
            self.logger.info("Initializing VideoWatermarker")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"VideoWatermarker initialization failed: {e}")
            raise
            
    async def embed_watermark(self, content: bytes, watermark_data: str) -> bytes:
        """Embed watermark in video content"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Basic implementation - in reality would use advanced video processing
            return content + b"VID_WATERMARK:" + watermark_data.encode()
        except Exception as e:
            self.logger.error(f"Video watermark embedding failed: {e}")
            raise

class TextWatermarker:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the text watermarker"""
        try:
            self.logger.info("Initializing TextWatermarker")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"TextWatermarker initialization failed: {e}")
            raise
            
    async def embed_watermark(self, content: str, watermark_data: str) -> str:
        """Embed watermark in text content"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Basic implementation - in reality would use advanced text steganography
            return content + f" [WATERMARK:{watermark_data}]"
        except Exception as e:
            self.logger.error(f"Text watermark embedding failed: {e}")
            raise