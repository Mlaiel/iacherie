"""Content Watermarking Template for IA Chéries Creator Protection

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Enterprise Content Protection Expert
"""

import hashlib
import hmac
import base64
import json
import logging
from typing import Dict, Any, Optional, List, Union, Tuple, BinaryIO
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field, validator
import cv2
import librosa
import soundfile as sf

from core.config import get_settings
from utils.exceptions import WatermarkError, ContentProtectionError
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class WatermarkType(Enum):
    """Types of watermarks supported"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    DIGITAL = "digital"
    STEGANOGRAPHIC = "steganographic"
    FREQUENCY_DOMAIN = "frequency_domain"
    BLOCKCHAIN = "blockchain"


class ContentType(Enum):
    """Content types for watermarking"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    TEXT = "text"
    NFT = "nft"


class WatermarkStrength(Enum):
    """Watermark strength levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class WatermarkConfig(BaseModel):
    """Watermark configuration model"""
    content_type: ContentType
    watermark_type: WatermarkType
    strength: WatermarkStrength = WatermarkStrength.MEDIUM
    creator_id: str = Field(..., min_length=1)
    content_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    signature_key: Optional[str] = None
    visibility: float = Field(default=0.5, ge=0.0, le=1.0)
    position: Tuple[float, float] = Field(default=(0.95, 0.95))
    
    @validator('position')
    def validate_position(cls, v):
        if not (0.0 <= v[0] <= 1.0 and 0.0 <= v[1] <= 1.0):
            raise ValueError("Position coordinates must be between 0.0 and 1.0")
        return v


class WatermarkMetadata(BaseModel):
    """Watermark metadata structure"""
    creator_info: Dict[str, str]
    content_info: Dict[str, Any]
    protection_level: str
    creation_timestamp: datetime
    expiration_timestamp: Optional[datetime] = None
    usage_rights: Dict[str, Any] = Field(default_factory=dict)
    distribution_tracking: List[str] = Field(default_factory=list)


class ContentWatermarkingTemplate:
    """Enterprise-grade content watermarking system for creator protection"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content watermarking template
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = SecurityMetricsCollector()
        self._initialize_watermarking_system()
        
    def _initialize_watermarking_system(self) -> None:
        """Initialize watermarking system components"""
        try:
            # Initialize encryption for invisible watermarks
            self.secret_key = self.config.get('secret_key', settings.WATERMARK_SECRET_KEY)
            
            # Initialize font for visible watermarks
            self.font_path = self.config.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
            
            # Initialize algorithm parameters
            self.dct_coefficients = self.config.get('dct_coefficients', 8)
            self.embedding_strength = self.config.get('embedding_strength', 0.1)
            
            # Initialize blockchain integration if available
            self.blockchain_enabled = self.config.get('blockchain_enabled', False)
            
            self.logger.info("Content watermarking system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize watermarking system: {e}")
            raise ContentProtectionError(f"Watermarking initialization failed: {e}")
    
    def add_watermark(self, content: Union[bytes, str, np.ndarray], 
                     config: WatermarkConfig) -> Tuple[Union[bytes, str, np.ndarray], Dict[str, Any]]:
        """Add watermark to content
        
        Args:
            content: Content to watermark
            config: Watermark configuration
            
        Returns:
            Tuple of (watermarked_content, watermark_metadata)
        """
        try:
            self.logger.info(f"Adding {config.watermark_type.value} watermark to {config.content_type.value} content")
            
            # Generate watermark metadata
            metadata = self._generate_watermark_metadata(config)
            
            # Apply watermark based on content type
            if config.content_type == ContentType.IMAGE:
                watermarked_content = self._watermark_image(content, config, metadata)
            elif config.content_type == ContentType.VIDEO:
                watermarked_content = self._watermark_video(content, config, metadata)
            elif config.content_type == ContentType.AUDIO:
                watermarked_content = self._watermark_audio(content, config, metadata)
            elif config.content_type == ContentType.TEXT:
                watermarked_content = self._watermark_text(content, config, metadata)
            elif config.content_type == ContentType.DOCUMENT:
                watermarked_content = self._watermark_document(content, config, metadata)
            elif config.content_type == ContentType.NFT:
                watermarked_content = self._watermark_nft(content, config, metadata)
            else:
                raise WatermarkError(f"Unsupported content type: {config.content_type}")
            
            # Log watermarking metrics
            self.metrics.increment_counter('watermarks_applied', {
                'type': config.watermark_type.value,
                'content_type': config.content_type.value,
                'strength': config.strength.value
            })
            
            return watermarked_content, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to add watermark: {e}")
            self.metrics.increment_counter('watermark_errors')
            raise WatermarkError(f"Watermark application failed: {e}")
    
    def _generate_watermark_metadata(self, config: WatermarkConfig) -> Dict[str, Any]:
        """Generate comprehensive watermark metadata
        
        Args:
            config: Watermark configuration
            
        Returns:
            Watermark metadata dictionary
        """
        metadata = {
            'watermark_id': self._generate_watermark_id(config),
            'creator_id': config.creator_id,
            'content_id': config.content_id,
            'watermark_type': config.watermark_type.value,
            'content_type': config.content_type.value,
            'strength': config.strength.value,
            'timestamp': config.timestamp.isoformat(),
            'signature': self._generate_watermark_signature(config),
            'protection_level': self._calculate_protection_level(config),
            'tracking_code': self._generate_tracking_code(config),
            'distribution_policy': self._get_distribution_policy(config),
            'usage_rights': self._get_usage_rights(config),
            'verification_hash': None  # Will be set after watermarking
        }
        
        return metadata
    
    def _watermark_image(self, image_data: Union[bytes, np.ndarray], 
                        config: WatermarkConfig, metadata: Dict[str, Any]) -> bytes:
        """Apply watermark to image content
        
        Args:
            image_data: Image data (bytes or numpy array)
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked image as bytes
        """
        try:
            # Convert to PIL Image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.fromarray(image_data)
            
            if config.watermark_type == WatermarkType.VISIBLE:
                watermarked_image = self._add_visible_image_watermark(image, config, metadata)
            elif config.watermark_type == WatermarkType.INVISIBLE:
                watermarked_image = self._add_invisible_image_watermark(image, config, metadata)
            elif config.watermark_type == WatermarkType.STEGANOGRAPHIC:
                watermarked_image = self._add_steganographic_watermark(image, config, metadata)
            elif config.watermark_type == WatermarkType.FREQUENCY_DOMAIN:
                watermarked_image = self._add_frequency_domain_watermark(image, config, metadata)
            else:
                raise WatermarkError(f"Unsupported watermark type for images: {config.watermark_type}")
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            watermarked_image.save(output_buffer, format='PNG', quality=95)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to watermark image: {e}")
            raise WatermarkError(f"Image watermarking failed: {e}")
    
    def _add_visible_image_watermark(self, image: Image.Image, 
                                   config: WatermarkConfig, metadata: Dict[str, Any]) -> Image.Image:
        """Add visible watermark to image
        
        Args:
            image: PIL Image object
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked PIL Image
        """
        # Create watermark text
        watermark_text = f"© {config.creator_id} | {config.content_id}"
        
        # Create transparent overlay
        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Load font
        try:
            font_size = max(20, min(image.size) // 20)
            font = ImageFont.truetype(self.font_path, font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        # Calculate position
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = int((image.size[0] - text_width) * config.position[0])
        y = int((image.size[1] - text_height) * config.position[1])
        
        # Add text with transparency
        alpha = int(255 * config.visibility)
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
        
        # Composite with original image
        watermarked = Image.alpha_composite(image.convert('RGBA'), overlay)
        
        return watermarked.convert('RGB')
    
    def _add_invisible_image_watermark(self, image: Image.Image, 
                                     config: WatermarkConfig, metadata: Dict[str, Any]) -> Image.Image:
        """Add invisible watermark using LSB steganography
        
        Args:
            image: PIL Image object
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Generate watermark data
        watermark_data = json.dumps(metadata).encode('utf-8')
        watermark_bits = ''.join(format(byte, '08b') for byte in watermark_data)
        
        # Embed watermark in least significant bits
        flat_img = img_array.flatten()
        
        if len(watermark_bits) > len(flat_img):
            raise WatermarkError("Watermark data too large for image")
        
        for i, bit in enumerate(watermark_bits):
            flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
        
        # Reshape back to original dimensions
        watermarked_array = flat_img.reshape(img_array.shape)
        
        return Image.fromarray(watermarked_array)
    
    def _add_steganographic_watermark(self, image: Image.Image, 
                                    config: WatermarkConfig, metadata: Dict[str, Any]) -> Image.Image:
        """Add steganographic watermark using DCT
        
        Args:
            image: PIL Image object
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked PIL Image
        """
        # Convert to YUV color space for better embedding
        img_yuv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2YUV)
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        
        # Apply DCT-based watermarking
        watermark_sequence = self._generate_watermark_sequence(metadata, y_channel.shape)
        
        # Embed watermark in DCT coefficients
        watermarked_y = self._embed_in_dct(y_channel, watermark_sequence, config.strength.value)
        
        # Reconstruct image
        img_yuv[:, :, 0] = np.clip(watermarked_y, 0, 255).astype(np.uint8)
        watermarked_rgb = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        
        return Image.fromarray(watermarked_rgb)
    
    def _add_frequency_domain_watermark(self, image: Image.Image, 
                                      config: WatermarkConfig, metadata: Dict[str, Any]) -> Image.Image:
        """Add frequency domain watermark using DFT
        
        Args:
            image: PIL Image object
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked PIL Image
        """
        # Convert to grayscale for frequency domain processing
        gray_image = image.convert('L')
        img_array = np.array(gray_image, dtype=np.float32)
        
        # Apply 2D FFT
        fft_img = np.fft.fft2(img_array)
        fft_shifted = np.fft.fftshift(fft_img)
        
        # Generate watermark pattern
        watermark_pattern = self._generate_frequency_watermark(metadata, img_array.shape)
        
        # Embed watermark in frequency domain
        strength_factor = self._get_strength_factor(config.strength)
        fft_watermarked = fft_shifted + strength_factor * watermark_pattern
        
        # Convert back to spatial domain
        ifft_shifted = np.fft.ifftshift(fft_watermarked)
        watermarked_img = np.real(np.fft.ifft2(ifft_shifted))
        watermarked_img = np.clip(watermarked_img, 0, 255).astype(np.uint8)
        
        # Convert back to RGB if original was RGB
        if image.mode == 'RGB':
            watermarked_rgb = cv2.cvtColor(watermarked_img, cv2.COLOR_GRAY2RGB)
            return Image.fromarray(watermarked_rgb)
        else:
            return Image.fromarray(watermarked_img)
    
    def _watermark_audio(self, audio_data: Union[bytes, np.ndarray], 
                        config: WatermarkConfig, metadata: Dict[str, Any]) -> bytes:
        """Apply watermark to audio content
        
        Args:
            audio_data: Audio data
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked audio as bytes
        """
        try:
            # Load audio data
            if isinstance(audio_data, bytes):
                audio, sr = librosa.load(io.BytesIO(audio_data), sr=None)
            else:
                audio = audio_data
                sr = self.config.get('sample_rate', 44100)
            
            if config.watermark_type == WatermarkType.INVISIBLE:
                watermarked_audio = self._add_invisible_audio_watermark(audio, sr, config, metadata)
            elif config.watermark_type == WatermarkType.FREQUENCY_DOMAIN:
                watermarked_audio = self._add_frequency_audio_watermark(audio, sr, config, metadata)
            elif config.watermark_type == WatermarkType.STEGANOGRAPHIC:
                watermarked_audio = self._add_steganographic_audio_watermark(audio, sr, config, metadata)
            else:
                raise WatermarkError(f"Unsupported watermark type for audio: {config.watermark_type}")
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(output_buffer, watermarked_audio, sr, format='WAV')
            output_buffer.seek(0)
            
            return output_buffer.read()
            
        except Exception as e:
            self.logger.error(f"Failed to watermark audio: {e}")
            raise WatermarkError(f"Audio watermarking failed: {e}")
    
    def _add_invisible_audio_watermark(self, audio: np.ndarray, sr: int,
                                     config: WatermarkConfig, metadata: Dict[str, Any]) -> np.ndarray:
        """Add invisible watermark to audio using spread spectrum
        
        Args:
            audio: Audio signal array
            sr: Sample rate
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked audio array
        """
        # Generate pseudo-random watermark sequence
        watermark_sequence = self._generate_audio_watermark_sequence(metadata, len(audio))
        
        # Apply spread spectrum watermarking
        strength_factor = self._get_strength_factor(config.strength) * 0.01  # Lower for audio
        watermarked_audio = audio + strength_factor * watermark_sequence
        
        # Ensure audio stays within valid range
        watermarked_audio = np.clip(watermarked_audio, -1.0, 1.0)
        
        return watermarked_audio
    
    def _add_frequency_audio_watermark(self, audio: np.ndarray, sr: int,
                                     config: WatermarkConfig, metadata: Dict[str, Any]) -> np.ndarray:
        """Add frequency domain watermark to audio
        
        Args:
            audio: Audio signal array
            sr: Sample rate
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked audio array
        """
        # Apply STFT for time-frequency analysis
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude, phase = np.abs(stft), np.angle(stft)
        
        # Generate watermark in frequency domain
        watermark_pattern = self._generate_audio_frequency_watermark(metadata, magnitude.shape)
        
        # Embed watermark in magnitude spectrum
        strength_factor = self._get_strength_factor(config.strength) * 0.05
        watermarked_magnitude = magnitude + strength_factor * watermark_pattern
        
        # Reconstruct audio
        watermarked_stft = watermarked_magnitude * np.exp(1j * phase)
        watermarked_audio = librosa.istft(watermarked_stft, hop_length=512)
        
        return watermarked_audio
    
    def _watermark_text(self, text_content: str, 
                       config: WatermarkConfig, metadata: Dict[str, Any]) -> str:
        """Apply watermark to text content
        
        Args:
            text_content: Text to watermark
            config: Watermark configuration
            metadata: Watermark metadata
            
        Returns:
            Watermarked text
        """
        try:
            if config.watermark_type == WatermarkType.VISIBLE:
                return self._add_visible_text_watermark(text_content, config, metadata)
            elif config.watermark_type == WatermarkType.INVISIBLE:
                return self._add_invisible_text_watermark(text_content, config, metadata)
            elif config.watermark_type == WatermarkType.STEGANOGRAPHIC:
                return self._add_steganographic_text_watermark(text_content, config, metadata)
            else:
                raise WatermarkError(f"Unsupported watermark type for text: {config.watermark_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to watermark text: {e}")
            raise WatermarkError(f"Text watermarking failed: {e}")
    
    def verify_watermark(self, watermarked_content: Union[bytes, str, np.ndarray],
                        config: WatermarkConfig) -> Tuple[bool, Dict[str, Any]]:
        """Verify watermark in content
        
        Args:
            watermarked_content: Content to verify
            config: Watermark configuration used for embedding
            
        Returns:
            Tuple of (verification_result, extracted_metadata)
        """
        try:
            self.logger.info(f"Verifying {config.watermark_type.value} watermark in {config.content_type.value} content")
            
            if config.content_type == ContentType.IMAGE:
                result, metadata = self._verify_image_watermark(watermarked_content, config)
            elif config.content_type == ContentType.AUDIO:
                result, metadata = self._verify_audio_watermark(watermarked_content, config)
            elif config.content_type == ContentType.TEXT:
                result, metadata = self._verify_text_watermark(watermarked_content, config)
            else:
                raise WatermarkError(f"Watermark verification not supported for: {config.content_type}")
            
            # Log verification metrics
            self.metrics.increment_counter('watermark_verifications', {
                'success': str(result),
                'content_type': config.content_type.value,
                'watermark_type': config.watermark_type.value
            })
            
            return result, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to verify watermark: {e}")
            self.metrics.increment_counter('watermark_verification_errors')
            raise WatermarkError(f"Watermark verification failed: {e}")
    
    def remove_watermark(self, watermarked_content: Union[bytes, str, np.ndarray],
                        config: WatermarkConfig, 
                        authorization_key: str) -> Union[bytes, str, np.ndarray]:
        """Remove watermark from content (authorized removal only)
        
        Args:
            watermarked_content: Watermarked content
            config: Watermark configuration
            authorization_key: Authorization key for removal
            
        Returns:
            Content with watermark removed
        """
        try:
            # Verify authorization
            if not self._verify_removal_authorization(authorization_key, config):
                raise WatermarkError("Unauthorized watermark removal attempt")
            
            self.logger.info(f"Authorized watermark removal for content {config.content_id}")
            
            # Remove watermark based on content type
            if config.content_type == ContentType.IMAGE:
                clean_content = self._remove_image_watermark(watermarked_content, config)
            elif config.content_type == ContentType.AUDIO:
                clean_content = self._remove_audio_watermark(watermarked_content, config)
            elif config.content_type == ContentType.TEXT:
                clean_content = self._remove_text_watermark(watermarked_content, config)
            else:
                raise WatermarkError(f"Watermark removal not supported for: {config.content_type}")
            
            # Log removal activity
            self.metrics.increment_counter('watermark_removals', {
                'content_type': config.content_type.value,
                'creator_id': config.creator_id
            })
            
            return clean_content
            
        except Exception as e:
            self.logger.error(f"Failed to remove watermark: {e}")
            self.metrics.increment_counter('watermark_removal_errors')
            raise WatermarkError(f"Watermark removal failed: {e}")
    
    # Helper methods
    def _generate_watermark_id(self, config: WatermarkConfig) -> str:
        """Generate unique watermark ID"""
        data = f"{config.creator_id}:{config.content_id}:{config.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_watermark_signature(self, config: WatermarkConfig) -> str:
        """Generate watermark signature for integrity verification"""
        data = f"{config.creator_id}:{config.content_id}:{config.timestamp.isoformat()}"
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_strength_factor(self, strength: WatermarkStrength) -> float:
        """Get numerical strength factor"""
        strength_map = {
            WatermarkStrength.LOW: 0.1,
            WatermarkStrength.MEDIUM: 0.3,
            WatermarkStrength.HIGH: 0.5,
            WatermarkStrength.MAXIMUM: 0.8
        }
        return strength_map.get(strength, 0.3)
    
    def _calculate_protection_level(self, config: WatermarkConfig) -> str:
        """Calculate content protection level"""
        if config.watermark_type == WatermarkType.BLOCKCHAIN:
            return "MAXIMUM"
        elif config.strength == WatermarkStrength.MAXIMUM:
            return "HIGH"
        elif config.strength == WatermarkStrength.HIGH:
            return "MEDIUM"
        else:
            return "STANDARD"
    
    def _generate_tracking_code(self, config: WatermarkConfig) -> str:
        """Generate unique tracking code for distribution monitoring"""
        data = f"TRACK:{config.creator_id}:{config.content_id}:{datetime.utcnow().timestamp()}"
        return base64.b64encode(hashlib.md5(data.encode()).digest()).decode()[:12]
    
    def _get_distribution_policy(self, config: WatermarkConfig) -> Dict[str, Any]:
        """Get distribution policy for content"""
        return {
            'allow_sharing': config.metadata.get('allow_sharing', True),
            'allow_modification': config.metadata.get('allow_modification', False),
            'commercial_use': config.metadata.get('commercial_use', False),
            'attribution_required': True,
            'geographic_restrictions': config.metadata.get('geographic_restrictions', [])
        }
    
    def _get_usage_rights(self, config: WatermarkConfig) -> Dict[str, Any]:
        """Get usage rights for content"""
        return {
            'creator_rights': ['attribution', 'integrity', 'withdrawal'],
            'user_rights': config.metadata.get('user_rights', ['view', 'share']),
            'license_type': config.metadata.get('license_type', 'standard'),
            'expiration_date': config.metadata.get('expiration_date'),
            'revenue_sharing': config.metadata.get('revenue_sharing', {})
        }
    
    # Additional helper methods would be implemented here...
    # (Continuing with specific watermarking algorithms, verification methods, etc.)


class WatermarkVerificationEngine:
    """Advanced watermark verification and analysis engine"""
    
    def __init__(self, template: ContentWatermarkingTemplate):
        """Initialize verification engine
        
        Args:
            template: Content watermarking template instance
        """
        self.template = template
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def batch_verify_watermarks(self, content_list: List[Tuple[Any, WatermarkConfig]]) -> List[Dict[str, Any]]:
        """Verify watermarks in batch for efficiency
        
        Args:
            content_list: List of (content, config) tuples
            
        Returns:
            List of verification results
        """
        results = []
        for content, config in content_list:
            try:
                verified, metadata = self.template.verify_watermark(content, config)
                results.append({
                    'content_id': config.content_id,
                    'verified': verified,
                    'metadata': metadata,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'content_id': config.content_id,
                    'verified': False,
                    'metadata': {},
                    'error': str(e)
                })
        
        return results
    
    def analyze_watermark_integrity(self, watermarked_content: Any,
                                  original_config: WatermarkConfig) -> Dict[str, Any]:
        """Analyze watermark integrity and tampering detection
        
        Args:
            watermarked_content: Content to analyze
            original_config: Original watermark configuration
            
        Returns:
            Integrity analysis results
        """
        analysis = {
            'integrity_score': 0.0,
            'tampering_detected': False,
            'degradation_level': 'none',
            'recommendations': []
        }
        
        try:
            # Verify watermark presence
            verified, metadata = self.template.verify_watermark(watermarked_content, original_config)
            
            if verified:
                analysis['integrity_score'] = 1.0
                analysis['degradation_level'] = 'none'
            else:
                analysis['integrity_score'] = 0.0
                analysis['tampering_detected'] = True
                analysis['degradation_level'] = 'high'
                analysis['recommendations'].append('Re-watermark content')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze watermark integrity: {e}")
            analysis['tampering_detected'] = True
            analysis['degradation_level'] = 'unknown'
            analysis['recommendations'].append('Manual inspection required')
            return analysis


# Export main components
__all__ = [
    'ContentWatermarkingTemplate',
    'WatermarkVerificationEngine',
    'WatermarkType',
    'ContentType', 
    'WatermarkStrength',
    'WatermarkConfig',
    'WatermarkMetadata'
]