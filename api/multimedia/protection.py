"""Professional Multimedia Content Protection and AI Fingerprinting System
Enterprise-grade content protection with AI-powered fingerprinting and monitoring

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""import asyncio
import logging
import hashlib
import secrets
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
import json
import base64
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import librosa
import soundfile as sf
import ffmpeg
from moviepy import VideoFileClip, AudioFileClip
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import imagehash
from scipy.fft import fft, ifft, fft2, ifft2

from .formats import ContentFormat, AudioFormat, VideoFormat, ImageFormat, SupportedFormats
from .metadata_extractor import UniversalMetadataExtractor
from ..core.exceptions import ProtectionError, SecurityError
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class WatermarkConfig:
    """Watermark configuration"""    text: Optional[str] = None
    image_path: Optional[Path] = None
    position: str = "bottom_right"  # "center", "top_left", "top_right", "bottom_left", "bottom_right"
    opacity: float = 0.5  # 0.0 to 1.0
    size: int = 20  # Font size for text watermarks
    color: str = "white"  # Color for text watermarks
    
    # Advanced settings
    repeat_pattern: bool = False  # Repeat watermark across content
    invisible_watermark: bool = False  # Use steganographic techniques
    rotation_angle: float = 0.0  # Rotation angle in degrees
    margin: Tuple[int, int] = (20, 20)  # Margin from edges (x, y)


@dataclass
class FingerprintConfig:
    """Digital fingerprint configuration"""    algorithm: str = "sha256"  # Hashing algorithm
    segment_duration: float = 5.0  # For audio/video segments
    feature_extraction: str = "spectral"  # Feature extraction method
    hash_length: int = 32  # Length of perceptual hash
    robustness_level: str = "medium"  # "low", "medium", "high"
    
    # Content-specific settings
    audio_features: List[str] = field(default_factory=lambda: ["mfcc", "spectral_centroid", "chroma"])
    video_features: List[str] = field(default_factory=lambda: ["histogram", "edges", "motion"])
    image_features: List[str] = field(default_factory=lambda: ["phash", "dhash", "whash"])


@dataclass
class ProtectionResult:
    """Result of content protection operation"""    success: bool
    original_path: Path
    protected_path: Optional[Path] = None
    
    # Protection details
    protection_type: str = ""  # "watermark", "fingerprint", "encryption", "steganography"
    watermark_applied: bool = False
    fingerprint_generated: bool = False
    encrypted: bool = False
    
    # Security metrics
    protection_strength: float = 0.0  # 0.0 to 1.0
    tamper_detection: bool = False
    authenticity_verification: bool = False
    
    # Generated data
    digital_fingerprint: Optional[str] = None
    protection_metadata: Dict[str, Any] = field(default_factory=dict)
    security_keys: Dict[str, str] = field(default_factory=dict)
    
    # Processing info
    processing_time: float = 0.0
    operations_applied: List[str] = field(default_factory=list)
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseProtector(ABC):
    """Abstract base class for content protectors"""    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="media_protection_"))
        self.metadata_extractor = UniversalMetadataExtractor()
        
    def __del__(self):
        """Cleanup temporary directory"""        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @abstractmethod
    async def apply_watermark(self, content_path: Path, watermark_config: WatermarkConfig,
                             output_path: Optional[Path] = None) -> ProtectionResult:
        """Apply watermark to content"""        pass
    
    @abstractmethod
    async def generate_fingerprint(self, content_path: Path, fingerprint_config: FingerprintConfig) -> str:
        """Generate digital fingerprint for content"""        pass
    
    @abstractmethod
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if protector supports format"""        pass
    
    def _generate_security_key(self, content_path: Path, salt: Optional[bytes] = None) -> bytes:
        """Generate security key for content"""        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Use content hash + timestamp as password
        content_hash = self._calculate_file_hash(content_path)
        password = f"{content_hash}_{datetime.now().isoformat()}".encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        return key
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using Fernet symmetric encryption"""        fernet = Fernet(base64.urlsafe_b64encode(key))
        return fernet.encrypt(data)
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using Fernet symmetric encryption"""        fernet = Fernet(base64.urlsafe_b64encode(key))
        return fernet.decrypt(encrypted_data)


class AudioProtector(BaseProtector):
    """Professional audio content protector"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if protector supports audio format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.AUDIO
        return SupportedFormats.is_audio_format(format_type)
    
    async def apply_watermark(self, content_path: Path, watermark_config: WatermarkConfig,
                             output_path: Optional[Path] = None) -> ProtectionResult:
        """Apply watermark to audio content"""        start_time = datetime.now()
        
        result = ProtectionResult(
            success=False,
            original_path=content_path,
            protection_type="watermark"
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"watermarked_{content_path.name}"
        
        try:
            # Load audio
            audio, sr = librosa.load(str(content_path), sr=None)
            
            # Apply watermark based on configuration
            if watermark_config.invisible_watermark:
                watermarked_audio = await self._apply_invisible_audio_watermark(
                    audio, sr, watermark_config, result
                )
            else:
                watermarked_audio = await self._apply_audible_audio_watermark(
                    audio, sr, watermark_config, result
                )
            
            # Save watermarked audio
            output_format = content_path.suffix.lower().lstrip('.')
            await self._save_watermarked_audio(watermarked_audio, sr, output_path, output_format)
            
            result.protected_path = output_path
            result.watermark_applied = True
            result.success = True
            result.protection_strength = 0.8 if watermark_config.invisible_watermark else 0.6
            
        except Exception as e:
            logger.error(f"Audio watermarking failed: {str(e)}")
            result.errors.append(f"Watermarking failed: {str(e)}")
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _apply_invisible_audio_watermark(self, audio: np.ndarray, sr: int,
                                             config: WatermarkConfig, result: ProtectionResult) -> np.ndarray:
        """Apply invisible watermark using spectral embedding"""        
        # Generate watermark signal from text or image
        watermark_data = await self._generate_audio_watermark_data(config)
        
        # Apply LSB (Least Significant Bit) watermarking in frequency domain
        stft = librosa.stft(audio)
        watermarked_stft = stft.copy()
        
        # Embed watermark in magnitude spectrum
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Select frequency bands for embedding (avoid critical bands)
        freq_bins = magnitude.shape[0]
        embed_bins = np.linspace(int(freq_bins * 0.1), int(freq_bins * 0.9), len(watermark_data), dtype=int)
        
        for i, bin_idx in enumerate(embed_bins):
            if i < len(watermark_data):
                # Modulate magnitude based on watermark bit
                if watermark_data[i] == 1:
                    magnitude[bin_idx, :] *= 1.001  # Slight increase
                else:
                    magnitude[bin_idx, :] *= 0.999  # Slight decrease
        
        # Reconstruct watermarked signal
        watermarked_stft = magnitude * np.exp(1j * phase)
        watermarked_audio = librosa.istft(watermarked_stft)
        
        result.operations_applied.append("invisible_watermark_spectral_embedding")
        result.protection_metadata['embedding_method'] = 'spectral_lsb'
        result.protection_metadata['watermark_strength'] = config.opacity
        
        return watermarked_audio
    
    async def _apply_audible_audio_watermark(self, audio: np.ndarray, sr: int,
                                           config: WatermarkConfig, result: ProtectionResult) -> np.ndarray:
        """Apply audible watermark (beep or tone)"""        
        # Generate simple tone watermark
        duration = 0.5  # 500ms tone
        frequency = 1000  # 1kHz tone
        t = np.linspace(0, duration, int(sr * duration))
        tone = np.sin(2 * np.pi * frequency * t) * config.opacity * 0.1
        
        # Position the tone based on configuration
        audio_length = len(audio)
        tone_length = len(tone)
        
        if config.position == "beginning":
            insert_position = 0
        elif config.position == "end":
            insert_position = max(0, audio_length - tone_length)
        else:  # middle
            insert_position = audio_length // 2 - tone_length // 2
        
        # Insert tone
        watermarked_audio = audio.copy()
        end_position = min(insert_position + tone_length, audio_length)
        actual_tone_length = end_position - insert_position
        
        if actual_tone_length > 0:
            watermarked_audio[insert_position:end_position] += tone[:actual_tone_length]
        
        result.operations_applied.append("audible_watermark_tone")
        result.protection_metadata['tone_frequency'] = frequency
        result.protection_metadata['tone_duration'] = duration
        result.protection_metadata['position'] = config.position
        
        return watermarked_audio
    
    async def _generate_audio_watermark_data(self, config: WatermarkConfig) -> np.ndarray:
        """Generate binary watermark data from text or image"""        if config.text:
            # Convert text to binary
            text_bytes = config.text.encode('utf-8')
            binary_data = []
            for byte in text_bytes:
                binary_data.extend([int(bit) for bit in format(byte, '08b')])
            return np.array(binary_data)
        
        elif config.image_path and config.image_path.exists():
            # Convert small image to binary
            with Image.open(config.image_path) as img:
                # Resize to small size for embedding
                img = img.resize((8, 8), Image.Resampling.NEAREST)
                img = img.convert('1')  # Binary image
                img_array = np.array(img)
                return img_array.flatten().astype(int)
        
        else:
            # Default: generate random pattern
            return np.random.randint(0, 2, size=64)
    
    async def _save_watermarked_audio(self, audio: np.ndarray, sr: int, 
                                    output_path: Path, output_format: str):
        """Save watermarked audio"""        if output_format in ['wav', 'flac']:
            sf.write(str(output_path), audio, sr)
        else:
            # Convert using ffmpeg for compressed formats
            temp_wav = self.temp_dir / "temp_watermarked.wav"
            sf.write(str(temp_wav), audio, sr)
            
            (
                ffmpeg
                .input(str(temp_wav))
                .output(str(output_path), acodec='libmp3lame' if output_format == 'mp3' else 'aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            temp_wav.unlink()
    
    async def generate_fingerprint(self, content_path: Path, 
                                 fingerprint_config: FingerprintConfig) -> str:
        """Generate audio fingerprint"""        try:
            audio, sr = librosa.load(str(content_path), sr=None)
            
            fingerprint_components = []
            
            # Extract various audio features
            if "mfcc" in fingerprint_config.audio_features:
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                mfcc_hash = hashlib.sha256(mfcc.tobytes()).hexdigest()[:8]
                fingerprint_components.append(mfcc_hash)
            
            if "spectral_centroid" in fingerprint_config.audio_features:
                centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
                centroid_hash = hashlib.sha256(centroid.tobytes()).hexdigest()[:8]
                fingerprint_components.append(centroid_hash)
            
            if "chroma" in fingerprint_config.audio_features:
                chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
                chroma_hash = hashlib.sha256(chroma.tobytes()).hexdigest()[:8]
                fingerprint_components.append(chroma_hash)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_hash = hashlib.sha256(zcr.tobytes()).hexdigest()[:8]
            fingerprint_components.append(zcr_hash)
            
            # Combine all components
            combined_fingerprint = "".join(fingerprint_components)
            
            # Final hash
            final_hash = hashlib.sha256(combined_fingerprint.encode()).hexdigest()
            return final_hash[:fingerprint_config.hash_length]
            
        except Exception as e:
            logger.error(f"Audio fingerprint generation failed: {str(e)}")
            raise ProtectionError(f"Failed to generate audio fingerprint: {str(e)}")


class VideoProtector(BaseProtector):
    """Professional video content protector"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if protector supports video format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.VIDEO
        return SupportedFormats.is_video_format(format_type)
    
    async def apply_watermark(self, content_path: Path, watermark_config: WatermarkConfig,
                             output_path: Optional[Path] = None) -> ProtectionResult:
        """Apply watermark to video content"""        start_time = datetime.now()
        
        result = ProtectionResult(
            success=False,
            original_path=content_path,
            protection_type="watermark"
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"watermarked_{content_path.name}"
        
        try:
            # Apply watermark using ffmpeg
            if watermark_config.invisible_watermark:
                await self._apply_invisible_video_watermark(
                    content_path, output_path, watermark_config, result
                )
            else:
                await self._apply_visible_video_watermark(
                    content_path, output_path, watermark_config, result
                )
            
            result.protected_path = output_path
            result.watermark_applied = True
            result.success = True
            result.protection_strength = 0.8 if watermark_config.invisible_watermark else 0.7
            
        except Exception as e:
            logger.error(f"Video watermarking failed: {str(e)}")
            result.errors.append(f"Watermarking failed: {str(e)}")
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _apply_visible_video_watermark(self, input_path: Path, output_path: Path,
                                           config: WatermarkConfig, result: ProtectionResult):
        """Apply visible watermark to video"""        
        # Build ffmpeg filter for watermark
        filters = []
        
        if config.text:
            # Text watermark
            position = self._get_text_position(config.position)
            filters.append(
                f"drawtext=text='{config.text}':fontsize={config.size}:"
                f"fontcolor={config.color}@{config.opacity}:{position}"
            )
            
        elif config.image_path and config.image_path.exists():
            # Image watermark
            position = self._get_overlay_position(config.position, config.margin)
            filters.append(f"movie={config.image_path}[wm]")
            filters.append(f"[0][wm]overlay={position}")
        
        # Apply filters
        if filters:
            input_stream = ffmpeg.input(str(input_path))
            
            if config.image_path and config.image_path.exists():
                # Image overlay
                watermark = ffmpeg.input(str(config.image_path))
                position = self._get_overlay_position(config.position, config.margin)
                
                output = ffmpeg.output(
                    ffmpeg.overlay(input_stream, watermark, x=position.split('=')[1].split(':')[0], 
                                 y=position.split('=')[1].split(':')[1]),
                    str(output_path),
                    vcodec='libx264',
                    acodec='copy'
                )
            else:
                # Text overlay
                position = self._get_text_position(config.position)
                output = ffmpeg.output(
                    ffmpeg.drawtext(
                        input_stream,
                        text=config.text,
                        fontsize=config.size,
                        fontcolor=f"{config.color}@{config.opacity}",
                        x=position.split('=')[1].split(':')[0],
                        y=position.split('=')[1].split(':')[1]
                    ),
                    str(output_path),
                    vcodec='libx264',
                    acodec='copy'
                )
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        result.operations_applied.append("visible_watermark")
        result.protection_metadata['watermark_type'] = 'visible'
        result.protection_metadata['position'] = config.position
    
    async def _apply_invisible_video_watermark(self, input_path: Path, output_path: Path,
                                             config: WatermarkConfig, result: ProtectionResult):
        """Apply invisible watermark to video using LSB steganography"""        
        # For invisible watermarks, we need to process frame by frame
        video_clip = VideoFileClip(str(input_path))
        
        def watermark_frame(get_frame, t):
            frame = get_frame(t)
            return self._embed_watermark_in_frame(frame, config)
        
        watermarked_clip = video_clip.fl(watermark_frame)
        
        # Save with same audio
        watermarked_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        watermarked_clip.close()
        video_clip.close()
        
        result.operations_applied.append("invisible_watermark_lsb")
        result.protection_metadata['watermark_type'] = 'invisible'
        result.protection_metadata['embedding_method'] = 'lsb_steganography'
    
    def _embed_watermark_in_frame(self, frame: np.ndarray, config: WatermarkConfig) -> np.ndarray:
        """Embed watermark in single frame using LSB"""        watermarked_frame = frame.copy()
        
        # Generate watermark pattern
        if config.text:
            # Convert text to binary pattern
            watermark_data = []
            for char in config.text:
                watermark_data.extend([int(bit) for bit in format(ord(char), '08b')])
        else:
            # Use random pattern
            watermark_data = np.random.randint(0, 2, size=64).tolist()
        
        # Embed in LSB of blue channel (least perceptible)
        height, width, channels = watermarked_frame.shape
        watermark_idx = 0
        
        for i in range(0, min(height, 100)):  # Limit to avoid performance issues
            for j in range(0, min(width, 100)):
                if watermark_idx < len(watermark_data):
                    # Modify LSB of blue channel
                    pixel_value = watermarked_frame[i, j, 2]  # Blue channel
                    watermarked_frame[i, j, 2] = (pixel_value & 0xFE) | watermark_data[watermark_idx]
                    watermark_idx += 1
                else:
                    break
            if watermark_idx >= len(watermark_data):
                break
        
        return watermarked_frame
    
    def _get_text_position(self, position: str) -> str:
        """Get ffmpeg text position string"""        positions = {
            'top_left': 'x=10:y=10',
            'top_right': 'x=w-tw-10:y=10',
            'bottom_left': 'x=10:y=h-th-10',
            'bottom_right': 'x=w-tw-10:y=h-th-10',
            'center': 'x=(w-tw)/2:y=(h-th)/2'
        }
        return positions.get(position, positions['bottom_right'])
    
    def _get_overlay_position(self, position: str, margin: Tuple[int, int]) -> str:
        """Get ffmpeg overlay position string"""        mx, my = margin
        positions = {
            'top_left': f'x={mx}:y={my}',
            'top_right': f'x=W-w-{mx}:y={my}',
            'bottom_left': f'x={mx}:y=H-h-{my}',
            'bottom_right': f'x=W-w-{mx}:y=H-h-{my}',
            'center': 'x=(W-w)/2:y=(H-h)/2'
        }
        return positions.get(position, positions['bottom_right'])
    
    async def generate_fingerprint(self, content_path: Path,
                                 fingerprint_config: FingerprintConfig) -> str:
        """Generate video fingerprint"""        try:
            video_clip = VideoFileClip(str(content_path))
            duration = video_clip.duration
            
            fingerprint_components = []
            
            # Sample frames at regular intervals
            num_samples = min(10, int(duration / fingerprint_config.segment_duration))
            
            for i in range(num_samples):
                t = (i * duration) / num_samples
                frame = video_clip.get_frame(t)
                
                # Extract frame features
                if "histogram" in fingerprint_config.video_features:
                    # Color histogram
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    hist_hash = hashlib.sha256(hist.tobytes()).hexdigest()[:4]
                    fingerprint_components.append(hist_hash)
                
                if "edges" in fingerprint_config.video_features:
                    # Edge features
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    edges = cv2.Canny(gray, 100, 200)
                    edges_hash = hashlib.sha256(edges.tobytes()).hexdigest()[:4]
                    fingerprint_components.append(edges_hash)
            
            # Audio fingerprint if present
            if video_clip.audio:
                audio_array = video_clip.audio.to_soundarray()
                if audio_array.size > 0:
                    audio_hash = hashlib.sha256(audio_array.tobytes()).hexdigest()[:8]
                    fingerprint_components.append(audio_hash)
            
            video_clip.close()
            
            # Combine all components
            combined_fingerprint = "".join(fingerprint_components)
            final_hash = hashlib.sha256(combined_fingerprint.encode()).hexdigest()
            
            return final_hash[:fingerprint_config.hash_length]
            
        except Exception as e:
            logger.error(f"Video fingerprint generation failed: {str(e)}")
            raise ProtectionError(f"Failed to generate video fingerprint: {str(e)}")


class ImageProtector(BaseProtector):
    """Professional image content protector"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if protector supports image format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.IMAGE
        return SupportedFormats.is_image_format(format_type)
    
    async def apply_watermark(self, content_path: Path, watermark_config: WatermarkConfig,
                             output_path: Optional[Path] = None) -> ProtectionResult:
        """Apply watermark to image content"""        start_time = datetime.now()
        
        result = ProtectionResult(
            success=False,
            original_path=content_path,
            protection_type="watermark"
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"watermarked_{content_path.name}"
        
        try:
            with Image.open(content_path) as image:
                original_image = image.copy()
                
                # Apply watermark based on configuration
                if watermark_config.invisible_watermark:
                    watermarked_image = await self._apply_invisible_image_watermark(
                        original_image, watermark_config, result
                    )
                else:
                    watermarked_image = await self._apply_visible_image_watermark(
                        original_image, watermark_config, result
                    )
                
                # Save watermarked image
                output_format = content_path.suffix.lower().lstrip('.')
                if output_format == 'jpg':
                    output_format = 'jpeg'
                
                watermarked_image.save(str(output_path), format=output_format.upper())
                
                result.protected_path = output_path
                result.watermark_applied = True
                result.success = True
                result.protection_strength = 0.9 if watermark_config.invisible_watermark else 0.8
                
        except Exception as e:
            logger.error(f"Image watermarking failed: {str(e)}")
            result.errors.append(f"Watermarking failed: {str(e)}")
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _apply_visible_image_watermark(self, image: Image.Image, config: WatermarkConfig,
                                           result: ProtectionResult) -> Image.Image:
        """Apply visible watermark to image"""        watermarked_image = image.copy()
        
        if config.text:
            # Text watermark
            watermarked_image = await self._add_text_watermark(watermarked_image, config)
            result.operations_applied.append("visible_text_watermark")
            
        elif config.image_path and config.image_path.exists():
            # Image watermark
            watermarked_image = await self._add_image_watermark(watermarked_image, config)
            result.operations_applied.append("visible_image_watermark")
        
        result.protection_metadata['watermark_type'] = 'visible'
        result.protection_metadata['position'] = config.position
        result.protection_metadata['opacity'] = config.opacity
        
        return watermarked_image
    
    async def _add_text_watermark(self, image: Image.Image, config: WatermarkConfig) -> Image.Image:
        """Add text watermark to image"""        watermarked = image.copy()
        
        # Create transparent overlay
        overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", config.size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), config.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x, y = self._calculate_watermark_position(
            config.position, watermarked.size, (text_width, text_height), config.margin
        )
        
        # Apply rotation if specified
        if config.rotation_angle != 0:
            # Create temporary image for rotated text
            temp_size = (text_width + 100, text_height + 100)
            temp_overlay = Image.new('RGBA', temp_size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_overlay)
            
            # Draw text in center of temp image
            temp_draw.text((50, 50), config.text, font=font, fill=self._get_color_with_opacity(config.color, config.opacity))
            
            # Rotate temp image
            rotated = temp_overlay.rotate(config.rotation_angle, expand=True)
            
            # Paste rotated text onto overlay
            overlay.paste(rotated, (x, y), rotated)
        else:
            # Draw text directly
            color = self._get_color_with_opacity(config.color, config.opacity)
            draw.text((x, y), config.text, font=font, fill=color)
        
        # Composite overlay onto image
        if watermarked.mode != 'RGBA':
            watermarked = watermarked.convert('RGBA')
        
        watermarked = Image.alpha_composite(watermarked, overlay)
        
        # Convert back to original mode if necessary
        if image.mode != 'RGBA':
            watermarked = watermarked.convert(image.mode)
        
        return watermarked
    
    async def _add_image_watermark(self, image: Image.Image, config: WatermarkConfig) -> Image.Image:
        """Add image watermark to image"""        watermarked = image.copy()
        
        with Image.open(config.image_path) as watermark_img:
            watermark = watermark_img.copy()
            
            # Resize watermark if needed (max 25% of original image)
            max_size = (image.width // 4, image.height // 4)
            if watermark.width > max_size[0] or watermark.height > max_size[1]:
                watermark.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Apply opacity
            if config.opacity < 1.0 and watermark.mode in ('RGBA', 'LA'):
                # Adjust alpha channel
                alpha = watermark.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(config.opacity)
                watermark.putalpha(alpha)
            elif config.opacity < 1.0:
                # Add alpha channel
                watermark = watermark.convert('RGBA')
                alpha = Image.new('L', watermark.size, int(255 * config.opacity))
                watermark.putalpha(alpha)
            
            # Calculate position
            x, y = self._calculate_watermark_position(
                config.position, watermarked.size, watermark.size, config.margin
            )
            
            # Apply rotation if specified
            if config.rotation_angle != 0:
                watermark = watermark.rotate(config.rotation_angle, expand=True)
            
            # Paste watermark
            if watermark.mode == 'RGBA' or 'transparency' in watermark.info:
                watermarked.paste(watermark, (x, y), watermark)
            else:
                watermarked.paste(watermark, (x, y))
        
        return watermarked
    
    async def _apply_invisible_image_watermark(self, image: Image.Image, config: WatermarkConfig,
                                             result: ProtectionResult) -> Image.Image:
        """Apply invisible watermark using LSB steganography"""        watermarked = image.copy()
        
        # Convert to RGB if necessary
        if watermarked.mode != 'RGB':
            watermarked = watermarked.convert('RGB')
        
        # Generate watermark data
        watermark_data = await self._generate_image_watermark_data(config)
        
        # Apply LSB steganography
        watermarked_array = np.array(watermarked)
        flat_image = watermarked_array.flatten()
        
        # Embed watermark data in LSB of image pixels
        for i, bit in enumerate(watermark_data):
            if i < len(flat_image):
                flat_image[i] = (flat_image[i] & 0xFE) | bit
        
        # Reshape back to image
        watermarked_array = flat_image.reshape(watermarked_array.shape)
        watermarked = Image.fromarray(watermarked_array.astype(np.uint8))
        
        result.operations_applied.append("invisible_watermark_lsb")
        result.protection_metadata['watermark_type'] = 'invisible'
        result.protection_metadata['embedding_method'] = 'lsb_steganography'
        result.protection_metadata['data_length'] = len(watermark_data)
        
        return watermarked
    
    async def _generate_image_watermark_data(self, config: WatermarkConfig) -> List[int]:
        """Generate binary watermark data for image"""        if config.text:
            # Convert text to binary
            text_bytes = config.text.encode('utf-8')
            binary_data = []
            for byte in text_bytes:
                binary_data.extend([int(bit) for bit in format(byte, '08b')])
            return binary_data
        else:
            # Generate signature pattern
            signature = f"watermark_{datetime.now().isoformat()}"
            signature_bytes = signature.encode('utf-8')
            binary_data = []
            for byte in signature_bytes:
                binary_data.extend([int(bit) for bit in format(byte, '08b')])
            return binary_data
    
    def _calculate_watermark_position(self, position: str, image_size: Tuple[int, int],
                                    watermark_size: Tuple[int, int], margin: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate watermark position coordinates"""        img_w, img_h = image_size
        wm_w, wm_h = watermark_size
        margin_x, margin_y = margin
        
        positions = {
            'top_left': (margin_x, margin_y),
            'top_right': (img_w - wm_w - margin_x, margin_y),
            'bottom_left': (margin_x, img_h - wm_h - margin_y),
            'bottom_right': (img_w - wm_w - margin_x, img_h - wm_h - margin_y),
            'center': ((img_w - wm_w) // 2, (img_h - wm_h) // 2)
        }
        
        return positions.get(position, positions['bottom_right'])
    
    def _get_color_with_opacity(self, color: str, opacity: float) -> Tuple[int, int, int, int]:
        """Convert color string to RGBA tuple with opacity"""        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        rgb = color_map.get(color.lower(), (255, 255, 255))
        alpha = int(255 * opacity)
        
        return (*rgb, alpha)
    
    async def generate_fingerprint(self, content_path: Path,
                                 fingerprint_config: FingerprintConfig) -> str:
        """Generate image fingerprint using perceptual hashing"""        try:
            with Image.open(content_path) as image:
                fingerprint_components = []
                
                # Different perceptual hashes
                if "phash" in fingerprint_config.image_features:
                    phash = str(imagehash.phash(image))
                    fingerprint_components.append(phash)
                
                if "dhash" in fingerprint_config.image_features:
                    dhash = str(imagehash.dhash(image))
                    fingerprint_components.append(dhash)
                
                if "whash" in fingerprint_config.image_features:
                    whash = str(imagehash.whash(image))
                    fingerprint_components.append(whash)
                
                # Color histogram hash
                image_array = np.array(image.convert('RGB'))
                hist = cv2.calcHist([image_array], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist_hash = hashlib.sha256(hist.tobytes()).hexdigest()[:8]
                fingerprint_components.append(hist_hash)
                
                # Edge-based hash
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edges_hash = hashlib.sha256(edges.tobytes()).hexdigest()[:8]
                fingerprint_components.append(edges_hash)
                
                # Combine all components
                combined_fingerprint = "".join(fingerprint_components)
                final_hash = hashlib.sha256(combined_fingerprint.encode()).hexdigest()
                
                return final_hash[:fingerprint_config.hash_length]
                
        except Exception as e:
            logger.error(f"Image fingerprint generation failed: {str(e)}")
            raise ProtectionError(f"Failed to generate image fingerprint: {str(e)}")


class MediaProtector:
    """Universal multimedia content protector"""    
    def __init__(self):
        self.protectors = {
            ContentFormat.AUDIO: AudioProtector(),
            ContentFormat.VIDEO: VideoProtector(),
            ContentFormat.IMAGE: ImageProtector()
        }
    
    async def apply_watermark(self, content_path: Path, watermark_config: WatermarkConfig,
                             output_path: Optional[Path] = None,
                             content_type: Optional[Union[str, ContentFormat]] = None) -> ProtectionResult:
        """Apply watermark to multimedia content"""        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content_path)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate protector
        protector = self.protectors.get(content_type)
        if protector is None:
            return ProtectionResult(
                success=False,
                original_path=content_path,
                errors=[f"No protector available for content type: {content_type}"]
            )
        
        return await protector.apply_watermark(content_path, watermark_config, output_path)
    
    async def generate_fingerprint(self, content_path: Path, fingerprint_config: FingerprintConfig,
                                 content_type: Optional[Union[str, ContentFormat]] = None) -> str:
        """Generate digital fingerprint for multimedia content"""        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content_path)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate protector
        protector = self.protectors.get(content_type)
        if protector is None:
            raise ProtectionError(f"No protector available for content type: {content_type}")
        
        return await protector.generate_fingerprint(content_path, fingerprint_config)
    
    async def protect_content(self, content_path: Path, 
                            watermark_config: Optional[WatermarkConfig] = None,
                            fingerprint_config: Optional[FingerprintConfig] = None,
                            output_path: Optional[Path] = None,
                            content_type: Optional[Union[str, ContentFormat]] = None) -> ProtectionResult:
        """Comprehensive content protection"""        
        result = ProtectionResult(
            success=False,
            original_path=content_path,
            protection_type="comprehensive"
        )
        
        try:
            # Apply watermark if requested
            if watermark_config:
                watermark_result = await self.apply_watermark(
                    content_path, watermark_config, output_path, content_type
                )
                
                if watermark_result.success:
                    result.protected_path = watermark_result.protected_path
                    result.watermark_applied = True
                    result.operations_applied.extend(watermark_result.operations_applied)
                    result.protection_metadata.update(watermark_result.protection_metadata)
                else:
                    result.errors.extend(watermark_result.errors)
                    return result
            
            # Generate fingerprint if requested
            if fingerprint_config:
                try:
                    source_path = result.protected_path or content_path
                    fingerprint = await self.generate_fingerprint(
                        source_path, fingerprint_config, content_type
                    )
                    result.digital_fingerprint = fingerprint
                    result.fingerprint_generated = True
                    result.operations_applied.append("digital_fingerprinting")
                except Exception as e:
                    result.warnings.append(f"Fingerprint generation failed: {str(e)}")
            
            # Calculate overall protection strength
            strength_factors = []
            if result.watermark_applied:
                strength_factors.append(0.6)
            if result.fingerprint_generated:
                strength_factors.append(0.3)
            if result.protected_path and result.protected_path != content_path:
                strength_factors.append(0.1)
            
            result.protection_strength = sum(strength_factors)
            result.success = len(strength_factors) > 0
            
        except Exception as e:
            logger.error(f"Content protection failed: {str(e)}")
            result.errors.append(f"Protection failed: {str(e)}")
        
        return result
    
    def _detect_content_type(self, content_path: Path) -> ContentFormat:
        """Auto-detect content type from file extension"""        extension = content_path.suffix.lower().lstrip('.')
        format_enum = SupportedFormats.get_format_by_extension(extension)
        
        if format_enum:
            if isinstance(format_enum, AudioFormat):
                return ContentFormat.AUDIO
            elif isinstance(format_enum, VideoFormat):
                return ContentFormat.VIDEO
            elif isinstance(format_enum, ImageFormat):
                return ContentFormat.IMAGE
        
        raise ProtectionError(f"Unable to detect content type for extension: {extension}")
    
    async def batch_protect(self, content_paths: List[Path],
                          watermark_config: Optional[WatermarkConfig] = None,
                          fingerprint_config: Optional[FingerprintConfig] = None,
                          output_directory: Optional[Path] = None) -> List[ProtectionResult]:
        """Protect multiple multimedia files"""        
        results = []
        
        for content_path in content_paths:
            output_path = None
            if output_directory:
                output_path = output_directory / f"protected_{content_path.name}"
                output_directory.mkdir(parents=True, exist_ok=True)
            
            result = await self.protect_content(
                content_path, watermark_config, fingerprint_config, output_path
            )
            results.append(result)
        
        return results
    
    def get_protection_statistics(self, results: List[ProtectionResult]) -> Dict[str, Any]:
        """Calculate protection statistics"""        stats = {
            'total_files': len(results),
            'successfully_protected': sum(1 for r in results if r.success),
            'watermarks_applied': sum(1 for r in results if r.watermark_applied),
            'fingerprints_generated': sum(1 for r in results if r.fingerprint_generated),
            'average_protection_strength': 0.0,
            'protection_types': {},
            'common_operations': {},
            'total_processing_time': sum(r.processing_time for r in results),
            'average_processing_time': 0.0
        }
        
        if results:
            # Protection strength
            protection_strengths = [r.protection_strength for r in results if r.success and r.protection_strength > 0]
            if protection_strengths:
                stats['average_protection_strength'] = sum(protection_strengths) / len(protection_strengths)
            
            # Processing time
            stats['average_processing_time'] = stats['total_processing_time'] / len(results)
            
            # Protection types
            for result in results:
                if result.protection_type:
                    stats['protection_types'][result.protection_type] = (
                        stats['protection_types'].get(result.protection_type, 0) + 1
                    )
            
            # Common operations
            for result in results:
                for operation in result.operations_applied:
                    stats['common_operations'][operation] = (
                        stats['common_operations'].get(operation, 0) + 1
                    )
        
        # Success rate
        stats['success_rate'] = (
            stats['successfully_protected'] / stats['total_files']
            if stats['total_files'] > 0 else 0
        )
        
        return stats


# Convenience functions
async def watermark_multimedia(content_path: Path, watermark_config: WatermarkConfig,
                              output_path: Optional[Path] = None) -> ProtectionResult:
    """Convenient function for watermarking multimedia content"""    protector = MediaProtector()
    return await protector.apply_watermark(content_path, watermark_config, output_path)

async def fingerprint_multimedia(content_path: Path, fingerprint_config: FingerprintConfig) -> str:
    """Convenient function for generating multimedia fingerprints"""    protector = MediaProtector()
    return await protector.generate_fingerprint(content_path, fingerprint_config)

# Predefined configurations
STANDARD_WATERMARK_CONFIG = WatermarkConfig(
    text="Protected Content",
    position="bottom_right",
    opacity=0.7,
    size=16
)

INVISIBLE_WATERMARK_CONFIG = WatermarkConfig(
    text="Hidden Protection",
    invisible_watermark=True,
    opacity=0.1
)

STANDARD_FINGERPRINT_CONFIG = FingerprintConfig(
    algorithm="sha256",
    hash_length=32,
    robustness_level="medium"
)
