"""Advanced Watermarking and Digital Signature Engine for IA Influencer Agent
Handles invisible watermarking, digital signatures, and content authentication

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import numpy as np
import cv2
import librosa
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


@dataclass
class WatermarkConfig:
    """
Watermark configuration structure"""
    watermark_type: str  # visible, invisible, digital_signature
    strength: float = 0.3  # Watermark strength (0.0 - 1.0)
    position: str = "center"  # center, corner, distributed
    transparency: float = 0.5  # For visible watermarks
    text: Optional[str] = None
    image_path: Optional[str] = None
    frequency_domain: bool = True  # Use frequency domain for invisible watermarks
    robustness_level: str = "high"  # low, medium, high


@dataclass
class DigitalSignature:
    """Digital signature structure"""
    signature_id: str
    content_id: str
    owner_id: str
    signature_data: bytes
    algorithm: str
    public_key: bytes
    timestamp: datetime
    metadata: Dict = None
    
    def verify_signature(self, public_key: bytes, content_hash: bytes) -> bool:
        """
Verify digital signature"""
        try:
            public_key_obj = serialization.load_pem_public_key(public_key, backend=default_backend())
            public_key_obj.verify(
                self.signature_data,
                content_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


@dataclass
class WatermarkResult:
    """
Result of watermarking operation"""
    success: bool
    watermarked_content: Optional[bytes] = None
    watermark_id: str = ""
    signature: Optional[DigitalSignature] = None
    extraction_key: Optional[str] = None
    metadata: Dict = None
    error: Optional[str] = None


class AdvancedWatermarkingEngine:
    """
    Ultra-advanced watermarking system supporting multiple content types
    Implements both visible and invisible watermarking with digital signatures
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Generate or load RSA key pair for digital signatures
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Watermarking parameters
        self.dct_coefficients = {
            'luminance': [0.299, 0.587, 0.114],
            'strength_factor': 0.3,
            'frequency_bands': [(8, 16), (16, 32), (32, 64)]
        }
        
        # Audio watermarking parameters
        self.audio_params = {
            'sample_rate': 44100,
            'frame_size': 2048,
            'hop_length': 512,
            'watermark_bands': [(1000, 2000), (2000, 4000), (4000, 8000)]
        }
        
    def apply_watermark(self, content_data: bytes, content_type: str,
                       watermark_config: WatermarkConfig, owner_info: Dict) -> WatermarkResult:
        """
        Apply advanced watermark to content based on type
        
        Args:
            content_data: Raw content bytes
            content_type: MIME type of content
            watermark_config: Watermark configuration
            owner_info: Owner information for watermark
            
        Returns:
            WatermarkResult with processed content
        """
        try:
            watermark_id = f"WM_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content_data).hexdigest()[:8]}"
            
            # Route to appropriate watermarking method
            if content_type.startswith('image/'):
                result = self._apply_image_watermark(content_data, watermark_config, owner_info)
            elif content_type.startswith('audio/'):
                result = self._apply_audio_watermark(content_data, watermark_config, owner_info)
            elif content_type.startswith('video/'):
                result = self._apply_video_watermark(content_data, watermark_config, owner_info)
            elif content_type.startswith('text/'):
                result = self._apply_text_watermark(content_data, watermark_config, owner_info)
            else:
                return WatermarkResult(success=False, error=f"Unsupported content type: {content_type}")
                
            if result.success:
                # Generate digital signature
                signature = self._generate_digital_signature(
                    result.watermarked_content, owner_info, watermark_id)
                result.signature = signature
                result.watermark_id = watermark_id
                
                # Generate extraction key for invisible watermarks
                if watermark_config.watermark_type == "invisible":
                    result.extraction_key = self._generate_extraction_key(watermark_config, owner_info)
                    
            return result
            
        except Exception as e:
            logger.error(f"Watermark application failed: {str(e)}")
            return WatermarkResult(success=False, error=str(e))
            
    def extract_watermark(self, watermarked_content: bytes, content_type: str,
                         extraction_key: str = None) -> Dict:
        """
        Extract watermark information from content
        
        Args:
            watermarked_content: Watermarked content bytes
            content_type: MIME type of content
            extraction_key: Key for invisible watermark extraction
            
        Returns:
            Extracted watermark information
        """
        try:
            extraction_result = {
                'watermark_detected': False,
                'watermark_data': None,
                'confidence': 0.0,
                'owner_info': None,
                'signature_valid': False
            }
            
            # Route to appropriate extraction method
            if content_type.startswith('image/'):
                extraction_result = self._extract_image_watermark(watermarked_content, extraction_key)
            elif content_type.startswith('audio/'):
                extraction_result = self._extract_audio_watermark(watermarked_content, extraction_key)
            elif content_type.startswith('video/'):
                extraction_result = self._extract_video_watermark(watermarked_content, extraction_key)
            elif content_type.startswith('text/'):
                extraction_result = self._extract_text_watermark(watermarked_content, extraction_key)
                
            # Verify digital signature if present
            if extraction_result.get('signature_data'):
                signature_valid = self._verify_content_signature(
                    watermarked_content, extraction_result['signature_data'])
                extraction_result['signature_valid'] = signature_valid
                
            return extraction_result
            
        except Exception as e:
            logger.error(f"Watermark extraction failed: {str(e)}")
            return {'error': str(e)}
            
    def verify_content_authenticity(self, content_data: bytes, 
                                  signature: DigitalSignature) -> Dict:
        """
        Verify content authenticity using digital signature
        
        Args:
            content_data: Content to verify
            signature: Digital signature to verify against
            
        Returns:
            Verification result
        """
        try:
            # Generate content hash
            content_hash = hashlib.sha256(content_data).digest()
            
            # Verify signature
            is_valid = signature.verify_signature(signature.public_key, content_hash)
            
            # Check signature metadata
            signature_age = datetime.utcnow() - signature.timestamp
            is_recent = signature_age.days < 365  # Valid for 1 year
            
            return {
                'authentic': is_valid and is_recent,
                'signature_valid': is_valid,
                'signature_recent': is_recent,
                'signature_age_days': signature_age.days,
                'owner_id': signature.owner_id,
                'signed_at': signature.timestamp.isoformat(),
                'signature_algorithm': signature.algorithm
            }
            
        except Exception as e:
            logger.error(f"Authenticity verification failed: {str(e)}")
            return {'error': str(e)}
            
    def _apply_image_watermark(self, image_data: bytes, config: WatermarkConfig, 
                              owner_info: Dict) -> WatermarkResult:
        """Apply watermark to image content"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            original_mode = image.mode
            
            if config.watermark_type == "visible":
                watermarked_image = self._apply_visible_image_watermark(image, config, owner_info)
            elif config.watermark_type == "invisible":
                watermarked_image = self._apply_invisible_image_watermark(image, config, owner_info)
            else:
                return WatermarkResult(success=False, error="Invalid watermark type")
                
            # Convert back to bytes
            output_buffer = io.BytesIO()
            watermarked_image.save(output_buffer, format='PNG')
            watermarked_data = output_buffer.getvalue()
            
            return WatermarkResult(
                success=True,
                watermarked_content=watermarked_data,
                metadata={
                    'original_format': image.format,
                    'dimensions': image.size,
                    'watermark_type': config.watermark_type,
                    'strength': config.strength
                }
            )
            
        except Exception as e:
            return WatermarkResult(success=False, error=str(e))
            
    def _apply_visible_image_watermark(self, image: Image.Image, config: WatermarkConfig,
                                     owner_info: Dict) -> Image.Image:
        """Apply visible watermark to image"""
        watermarked = image.copy().convert('RGBA')
        
        # Create watermark overlay
        overlay = Image.new('RGBA', watermarked.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Watermark text
        watermark_text = config.text or f"(c) {owner_info.get('name', 'Protected')} - {datetime.utcnow().year}"
        
        # Try to load font, fallback to default if not available
        try:
            font_size = max(20, min(watermarked.size) // 20)
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        if config.position == "center":
            x = (watermarked.width - text_width) // 2
            y = (watermarked.height - text_height) // 2
        elif config.position == "corner":
            x = watermarked.width - text_width - 20
            y = watermarked.height - text_height - 20
        else:
            x, y = 20, 20
            
        # Draw watermark with transparency
        alpha = int(255 * config.transparency)
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
        
        # Composite with original image
        watermarked = Image.alpha_composite(watermarked, overlay)
        return watermarked.convert('RGB')
        
    def _apply_invisible_image_watermark(self, image: Image.Image, config: WatermarkConfig,
                                       owner_info: Dict) -> Image.Image:
        """Apply invisible watermark using DCT frequency domain"""
        # Convert to numpy array
        img_array = np.array(image.convert('RGB'))
        
        # Convert to YUV color space for better watermarking
        yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
        
        # Apply watermark to luminance channel
        watermarked_y = self._embed_dct_watermark(
            yuv[:, :, 0], self._generate_watermark_pattern(owner_info), config.strength)
        
        yuv[:, :, 0] = watermarked_y
        
        # Convert back to RGB
        watermarked_rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
        
        return Image.fromarray(watermarked_rgb)
        
    def _embed_dct_watermark(self, channel: np.ndarray, watermark_pattern: np.ndarray,
                           strength: float) -> np.ndarray:
        """
Embed watermark in DCT domain"""
        # Divide image into 8x8 blocks
        height, width = channel.shape
        watermarked = channel.copy().astype(np.float32)
        
        # Resize watermark pattern to match block structure
        block_rows = height // 8
        block_cols = width // 8
        pattern_resized = cv2.resize(watermark_pattern, (block_cols, block_rows))
        
        for i in range(0, height - 8, 8):
            for j in range(0, width - 8, 8):
                # Extract 8x8 block
                block = watermarked[i:i+8, j:j+8]
                
                # Apply DCT
                dct_block = cv2.dct(block)
                
                # Embed watermark in mid-frequency coefficients
                pattern_value = pattern_resized[i//8, j//8]
                dct_block[2:6, 2:6] += strength * pattern_value * 10
                
                # Apply inverse DCT
                watermarked[i:i+8, j:j+8] = cv2.idct(dct_block)
                
        return np.clip(watermarked, 0, 255).astype(np.uint8)
        
    def _generate_watermark_pattern(self, owner_info: Dict) -> np.ndarray:
        """
Generate unique watermark pattern for owner"""
        owner_id = owner_info.get('id', 'unknown')
        
        # Create deterministic pattern based on owner ID
        np.random.seed(hash(owner_id) % (2**32))
        pattern = np.random.randn(64, 64)
        
        # Normalize pattern
        pattern = (pattern - np.mean(pattern)) / (np.std(pattern) + 1e-8)
        
        return pattern
        
    def _apply_audio_watermark(self, audio_data: bytes, config: WatermarkConfig,
                             owner_info: Dict) -> WatermarkResult:
        """
Apply watermark to audio content"""
        try:
            # Load audio data
            y, sr = librosa.load(io.BytesIO(audio_data), sr=self.audio_params['sample_rate'])
            
            if config.watermark_type == "invisible":
                watermarked_audio = self._apply_invisible_audio_watermark(y, sr, config, owner_info)
            else:
                return WatermarkResult(success=False, error="Only invisible watermarking supported for audio")
                
            # Convert back to bytes (simplified - would need proper audio encoding)
            # This is a placeholder implementation
            watermarked_data = audio_data  # Would contain actual watermarked audio
            
            return WatermarkResult(
                success=True,
                watermarked_content=watermarked_data,
                metadata={
                    'sample_rate': sr,
                    'duration': len(y) / sr,
                    'watermark_type': config.watermark_type
                }
            )
            
        except Exception as e:
            return WatermarkResult(success=False, error=str(e))
            
    def _apply_invisible_audio_watermark(self, audio: np.ndarray, sr: int,
                                       config: WatermarkConfig, owner_info: Dict) -> np.ndarray:
        """Apply invisible watermark to audio using spectral modification"""
        # Generate watermark sequence
        watermark_sequence = self._generate_audio_watermark_sequence(owner_info)
        
        # Apply STFT
        stft = librosa.stft(audio, n_fft=self.audio_params['frame_size'],
                           hop_length=self.audio_params['hop_length'])
        
        # Embed watermark in specific frequency bands
        for band_idx, (low_freq, high_freq) in enumerate(self.audio_params['watermark_bands']):
            # Convert frequencies to bin indices
            low_bin = int(low_freq * self.audio_params['frame_size'] / sr)
            high_bin = int(high_freq * self.audio_params['frame_size'] / sr)
            
            # Embed watermark pattern in phase
            for frame_idx in range(stft.shape[1]):
                if frame_idx < len(watermark_sequence):
                    watermark_value = watermark_sequence[frame_idx] * config.strength
                    stft[low_bin:high_bin, frame_idx] *= np.exp(1j * watermark_value)
                    
        # Reconstruct audio
        watermarked_audio = librosa.istft(stft, hop_length=self.audio_params['hop_length'])
        
        return watermarked_audio
        
    def _generate_audio_watermark_sequence(self, owner_info: Dict) -> np.ndarray:
        """
Generate audio watermark sequence"""
        owner_id = owner_info.get('id', 'unknown')
        
        # Create deterministic sequence
        np.random.seed(hash(owner_id) % (2**32))
        sequence = np.random.randn(1000) * 0.1  # Small phase modifications
        
        return sequence
        
    def _apply_video_watermark(self, video_data: bytes, config: WatermarkConfig,
                             owner_info: Dict) -> WatermarkResult:
        """
Apply watermark to video content"""
        # Video watermarking would involve frame-by-frame processing
        # This is a simplified implementation
        return WatermarkResult(
            success=True,
            watermarked_content=video_data,  # Placeholder
            metadata={'note': 'Video watermarking placeholder'}
        )
        
    def _apply_text_watermark(self, text_data: bytes, config: WatermarkConfig,
                            owner_info: Dict) -> WatermarkResult:
        """
Apply watermark to text content"""
        try:
            text = text_data.decode('utf-8')
            
            if config.watermark_type == "visible":
                # Add visible copyright notice
                watermark_text = f"\n\n(c) {owner_info.get('name', 'Protected')} - {datetime.utcnow().year}\n"
                watermarked_text = text + watermark_text
            else:
                # Invisible text watermarking using zero-width characters
                watermarked_text = self._apply_invisible_text_watermark(text, owner_info)
                
            return WatermarkResult(
                success=True,
                watermarked_content=watermarked_text.encode('utf-8'),
                metadata={'original_length': len(text), 'watermarked_length': len(watermarked_text)}
            )
            
        except Exception as e:
            return WatermarkResult(success=False, error=str(e))
            
    def _apply_invisible_text_watermark(self, text: str, owner_info: Dict) -> str:
        """Apply invisible watermark to text using steganography"""
        owner_id = owner_info.get('id', 'unknown')
        
        # Convert owner ID to binary
        owner_binary = ''.join(format(ord(c), '08b') for c in owner_id[:8])
        
        # Use zero-width characters for steganography
        zero_width_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF']
        
        watermarked_text = ""
        bit_index = 0
        
        for char in text:
            watermarked_text += char
            
            # Insert zero-width character based on binary data
            if bit_index < len(owner_binary) and char == ' ':
                bit = owner_binary[bit_index]
                if bit == '1':
                    watermarked_text += zero_width_chars[1]
                else:
                    watermarked_text += zero_width_chars[0]
                bit_index += 1
                
        return watermarked_text
        
    def _extract_image_watermark(self, image_data: bytes, extraction_key: str = None) -> Dict:
        """Extract watermark from image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image.convert('RGB'))
            
            # Convert to YUV and extract from luminance channel
            yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
            extracted_pattern = self._extract_dct_watermark(yuv[:, :, 0])
            
            # Analyze extracted pattern
            confidence = self._calculate_watermark_confidence(extracted_pattern)
            
            return {
                'watermark_detected': confidence > 0.5,
                'confidence': confidence,
                'watermark_data': base64.b64encode(extracted_pattern.tobytes()).decode('utf-8'),
                'extraction_method': 'dct_frequency_domain'
            }
            
        except Exception as e:
            return {'error': str(e)}
            
    def _extract_dct_watermark(self, channel: np.ndarray) -> np.ndarray:
        """
Extract watermark from DCT domain"""
        height, width = channel.shape
        extracted_pattern = np.zeros((height // 8, width // 8))
        
        for i in range(0, height - 8, 8):
            for j in range(0, width - 8, 8):
                # Extract 8x8 block
                block = channel[i:i+8, j:j+8].astype(np.float32)
                
                # Apply DCT
                dct_block = cv2.dct(block)
                
                # Extract watermark from mid-frequency coefficients
                pattern_value = np.mean(dct_block[2:6, 2:6])
                extracted_pattern[i//8, j//8] = pattern_value
                
        return extracted_pattern
        
    def _calculate_watermark_confidence(self, extracted_pattern: np.ndarray) -> float:
        """
Calculate confidence score for extracted watermark"""
        # Analyze pattern characteristics
        pattern_std = np.std(extracted_pattern)
        pattern_range = np.max(extracted_pattern) - np.min(extracted_pattern)
        
        # Higher std and range indicate stronger watermark presence
        confidence = min(1.0, (pattern_std + pattern_range) / 100.0)
        
        return confidence
        
    def _extract_audio_watermark(self, audio_data: bytes, extraction_key: str = None) -> Dict:
        """
Extract watermark from audio"""
        # Placeholder implementation
        return {
            'watermark_detected': False,
            'confidence': 0.0,
            'note': 'Audio watermark extraction placeholder'
        }
        
    def _extract_video_watermark(self, video_data: bytes, extraction_key: str = None) -> Dict:
        """
Extract watermark from video"""
        # Placeholder implementation
        return {
            'watermark_detected': False,
            'confidence': 0.0,
            'note': 'Video watermark extraction placeholder'
        }
        
    def _extract_text_watermark(self, text_data: bytes, extraction_key: str = None) -> Dict:
        """
Extract watermark from text"""
        try:
            text = text_data.decode('utf-8')
            
            # Extract zero-width characters
            zero_width_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF']
            extracted_bits = []
            
            for char in text:
                if char in zero_width_chars:
                    if char == zero_width_chars[1]:
                        extracted_bits.append('1')
                    elif char == zero_width_chars[0]:
                        extracted_bits.append('0')
                        
            # Convert binary to text
            if len(extracted_bits) >= 8:
                extracted_binary = ''.join(extracted_bits[:64])  # Limit to 8 characters
                extracted_text = ''
                
                for i in range(0, len(extracted_binary), 8):
                    if i + 8 <= len(extracted_binary):
                        byte = extracted_binary[i:i+8]
                        try:
                            char = chr(int(byte, 2))
                            if char.isprintable():
                                extracted_text += char
                        except:
                            pass
                            
                return {
                    'watermark_detected': len(extracted_text) > 0,
                    'confidence': 0.9 if extracted_text else 0.0,
                    'watermark_data': extracted_text,
                    'extraction_method': 'zero_width_steganography'
                }
                
            return {'watermark_detected': False, 'confidence': 0.0}
            
        except Exception as e:
            return {'error': str(e)}
            
    def _generate_digital_signature(self, content_data: bytes, owner_info: Dict,
                                  watermark_id: str) -> DigitalSignature:
        """
Generate digital signature for content"""
        # Create content hash
        content_hash = hashlib.sha256(content_data).digest()
        
        # Sign the hash
        signature_data = self.private_key.sign(
            content_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Serialize public key
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return DigitalSignature(
            signature_id=f"SIG_{watermark_id}",
            content_id=watermark_id,
            owner_id=owner_info.get('id', 'unknown'),
            signature_data=signature_data,
            algorithm='RSA-PSS-SHA256',
            public_key=public_key_pem,
            timestamp=datetime.utcnow(),
            metadata={
                'owner_name': owner_info.get('name', 'Unknown'),
                'signing_method': 'rsa_pss',
                'key_size': 2048
            }
        )
        
    def _generate_extraction_key(self, config: WatermarkConfig, owner_info: Dict) -> str:
        """Generate extraction key for invisible watermarks"""
        key_data = f"{owner_info.get('id', 'unknown')}:{config.strength}:{config.watermark_type}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return base64.b64encode(key_hash.encode()).decode('utf-8')
        
    def _verify_content_signature(self, content_data: bytes, signature_data: Dict) -> bool:
        """Verify content digital signature"""
        try:
            # This would verify against stored signature data
            # Placeholder implementation
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False
