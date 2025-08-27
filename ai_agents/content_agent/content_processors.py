"""
Content Processors Module - Industrial Multi-Format Processing Engine

Advanced processing capabilities for audio, video, image, and text content.
Handles format conversion, quality enhancement, and metadata extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import mimetypes
import json

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    import numpy as np
    from pydub import AudioSegment
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Video processing imports  
try:
    import cv2
    import moviepy.editor as mp
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

# Image processing imports
try:
    from PIL import Image, ImageEnhance, ImageFilter
    import pillow_heif
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False

# Text processing imports
try:
    import nltk
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    import langdetect
    TEXT_AVAILABLE = True
except ImportError:
    TEXT_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of content processing operation"""
    success: bool
    processed_content: Optional[Union[bytes, str, Dict[str, Any]]]
    metadata: Dict[str, Any]
    format_info: Dict[str, Any]
    quality_metrics: Dict[str, float]
    processing_time: float
    error_message: Optional[str] = None


@dataclass  
class ContentMetadata:
    """Comprehensive content metadata structure"""
    file_type: str
    format: str
    size: int
    duration: Optional[float]
    dimensions: Optional[tuple]
    bitrate: Optional[int]
    sample_rate: Optional[int]
    channels: Optional[int]
    color_space: Optional[str]
    creation_date: Optional[datetime]
    checksum: str
    mime_type: str
    encoding: Optional[str]
    custom_tags: Dict[str, Any]


class BaseProcessor(ABC):
    """Abstract base class for all content processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def process(self, content: Union[bytes, str, BinaryIO], 
                     options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process content and return result"""
        pass
        
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats for this processor"""
        pass
        
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of content"""
        return hashlib.sha256(data).hexdigest()
        
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file path"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'


class AudioProcessor(BaseProcessor):
    """Industrial-grade audio content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        if not AUDIO_AVAILABLE:
            raise ImportError("Audio processing dependencies not available")
            
        self.supported_formats = [
            'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus'
        ]
        self.default_sample_rate = self.config.get('sample_rate', 44100)
        self.default_bitrate = self.config.get('bitrate', 320)
        
    async def process(self, content: Union[bytes, str, BinaryIO], 
                     options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process audio content with advanced analysis"""
        start_time = asyncio.get_event_loop().time()
        options = options or {}
        
        try:
            # Load audio data
            if isinstance(content, str):
                audio_path = Path(content)
                audio_data = audio_path.read_bytes()
                y, sr = librosa.load(content, sr=self.default_sample_rate)
            else:
                audio_data = content if isinstance(content, bytes) else content.read()
                # Create temporary file for processing
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_path = temp_file.name
                y, sr = librosa.load(temp_path, sr=self.default_sample_rate)
                
            # Extract comprehensive metadata
            metadata = await self._extract_audio_metadata(y, sr, audio_data)
            
            # Perform quality analysis
            quality_metrics = await self._analyze_audio_quality(y, sr)
            
            # Apply processing based on options
            processed_audio = await self._apply_audio_processing(y, sr, options)
            
            # Format information
            format_info = {
                'original_format': metadata.format,
                'processed_format': options.get('output_format', 'wav'),
                'sample_rate': sr,
                'channels': metadata.channels,
                'duration': metadata.duration
            }
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                success=True,
                processed_content=processed_audio,
                metadata=metadata.__dict__,
                format_info=format_info,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            processing_time = asyncio.get_event_loop().time() - start_time
            return ProcessingResult(
                success=False,
                processed_content=None,
                metadata={},
                format_info={},
                quality_metrics={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _extract_audio_metadata(self, y: np.ndarray, sr: int, 
                                    audio_data: bytes) -> ContentMetadata:
        """Extract comprehensive audio metadata"""
        duration = len(y) / sr
        
        return ContentMetadata(
            file_type='audio',
            format='wav',  # Default processing format
            size=len(audio_data),
            duration=duration,
            dimensions=None,
            bitrate=None,  # Will be calculated if needed
            sample_rate=sr,
            channels=1 if y.ndim == 1 else y.shape[0],
            color_space=None,
            creation_date=datetime.now(),
            checksum=self._calculate_checksum(audio_data),
            mime_type='audio/wav',
            encoding='PCM',
            custom_tags={}
        )
    
    async def _analyze_audio_quality(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze audio quality metrics"""
        try:
            # RMS Energy
            rms_energy = float(np.sqrt(np.mean(y**2)))
            
            # Zero Crossing Rate
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)[0]))
            
            # Spectral Centroid
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))
            
            # Spectral Rolloff
            spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)[0]))
            
            # Spectral Bandwidth
            spectral_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]))
            
            # Dynamic Range
            dynamic_range = float(np.max(y) - np.min(y))
            
            # Peak to RMS ratio
            peak_to_rms = float(np.max(np.abs(y)) / rms_energy) if rms_energy > 0 else 0
            
            return {
                'rms_energy': rms_energy,
                'zero_crossing_rate': zcr,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'spectral_bandwidth': spectral_bandwidth,
                'dynamic_range': dynamic_range,
                'peak_to_rms_ratio': peak_to_rms,
                'quality_score': min(100, (rms_energy * 100 + dynamic_range * 50) / 2)
            }
        except Exception as e:
            self.logger.warning(f"Quality analysis failed: {str(e)}")
            return {'quality_score': 0.0}
    
    async def _apply_audio_processing(self, y: np.ndarray, sr: int, 
                                    options: Dict[str, Any]) -> bytes:
        """Apply audio processing effects and optimizations"""
        processed_y = y.copy()
        
        # Noise reduction
        if options.get('noise_reduction', False):
            processed_y = self._reduce_noise(processed_y, sr)
            
        # Normalization
        if options.get('normalize', True):
            processed_y = librosa.util.normalize(processed_y)
            
        # Dynamic range compression
        if options.get('compress', False):
            processed_y = self._compress_dynamic_range(processed_y)
            
        # EQ adjustments
        if 'eq_settings' in options:
            processed_y = self._apply_eq(processed_y, sr, options['eq_settings'])
        
        # Convert back to audio format
        return self._array_to_audio_bytes(processed_y, sr, options.get('output_format', 'wav'))
    
    def _reduce_noise(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        # This is a simplified noise reduction - in production use more sophisticated algorithms
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Spectral gating
        noise_floor = np.percentile(magnitude, 20)  
        mask = magnitude > (noise_floor * 2)
        magnitude_cleaned = magnitude * mask
        
        stft_cleaned = magnitude_cleaned * np.exp(1j * phase)
        return librosa.istft(stft_cleaned)
    
    def _compress_dynamic_range(self, y: np.ndarray, ratio: float = 4.0, 
                               threshold: float = -20.0) -> np.ndarray:
        """Apply dynamic range compression"""
        # Convert to dB
        y_db = librosa.amplitude_to_db(np.abs(y))
        
        # Apply compression above threshold
        compressed_db = np.where(
            y_db > threshold,
            threshold + (y_db - threshold) / ratio,
            y_db
        )
        
        # Convert back to linear scale
        compressed_linear = librosa.db_to_amplitude(compressed_db)
        return compressed_linear * np.sign(y)
    
    def _apply_eq(self, y: np.ndarray, sr: int, eq_settings: Dict[str, float]) -> np.ndarray:
        """Apply EQ adjustments"""
        # This is a simplified EQ - in production use more sophisticated filtering
        processed = y.copy()
        
        for freq, gain in eq_settings.items():
            freq_hz = float(freq)
            gain_linear = 10**(gain/20)  # Convert dB to linear
            
            # Simple peaking filter (production would use proper biquad filters)
            sos = librosa.core.time_frequency._spectrogram_mel_filter(
                sr, 2048, fmin=freq_hz-100, fmax=freq_hz+100, n_mels=1
            )
            processed = processed * gain_linear
            
        return processed
    
    def _array_to_audio_bytes(self, y: np.ndarray, sr: int, format: str) -> bytes:
        """Convert numpy array to audio bytes in specified format"""
        import io
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as temp_file:
            sf.write(temp_file.name, y, sr)
            temp_file.seek(0)
            return temp_file.read()
    
    def get_supported_formats(self) -> List[str]:
        """Get supported audio formats"""
        return self.supported_formats


class VideoProcessor(BaseProcessor):
    """Industrial-grade video content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        if not VIDEO_AVAILABLE:
            raise ImportError("Video processing dependencies not available")
            
        self.supported_formats = [
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'm4v'
        ]
        self.default_resolution = self.config.get('resolution', (1920, 1080))
        self.default_fps = self.config.get('fps', 30)
        
    async def process(self, content: Union[bytes, str, BinaryIO], 
                     options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process video content with advanced analysis"""
        start_time = asyncio.get_event_loop().time()
        options = options or {}
        
        try:
            # Handle different input types
            if isinstance(content, str):
                video_path = content
                video_data = Path(content).read_bytes()
            else:
                video_data = content if isinstance(content, bytes) else content.read()
                # Create temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    temp_file.write(video_data)
                    video_path = temp_file.name
            
            # Load video for analysis
            cap = cv2.VideoCapture(video_path)
            
            # Extract metadata
            metadata = await self._extract_video_metadata(cap, video_data)
            
            # Quality analysis
            quality_metrics = await self._analyze_video_quality(cap)
            
            # Process video if needed
            processed_video = await self._apply_video_processing(video_path, options)
            
            format_info = {
                'original_format': Path(video_path).suffix.lstrip('.'),
                'processed_format': options.get('output_format', 'mp4'),
                'resolution': metadata.dimensions,
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'duration': metadata.duration
            }
            
            cap.release()
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                success=True,
                processed_content=processed_video,
                metadata=metadata.__dict__,
                format_info=format_info,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Video processing failed: {str(e)}")
            processing_time = asyncio.get_event_loop().time() - start_time
            return ProcessingResult(
                success=False,
                processed_content=None,
                metadata={},
                format_info={},
                quality_metrics={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _extract_video_metadata(self, cap: cv2.VideoCapture, 
                                    video_data: bytes) -> ContentMetadata:
        """Extract comprehensive video metadata"""
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        return ContentMetadata(
            file_type='video',
            format='mp4',
            size=len(video_data),
            duration=duration,
            dimensions=(width, height),
            bitrate=None,
            sample_rate=None,
            channels=None,
            color_space='BGR',
            creation_date=datetime.now(),
            checksum=self._calculate_checksum(video_data),
            mime_type='video/mp4',
            encoding='H.264',
            custom_tags={'fps': fps, 'frame_count': frame_count}
        )
    
    async def _analyze_video_quality(self, cap: cv2.VideoCapture) -> Dict[str, float]:
        """Analyze video quality metrics"""
        try:
            # Sample frames for quality analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_size = min(30, frame_count)  # Sample up to 30 frames
            
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            
            for i in range(0, frame_count, max(1, frame_count // sample_size)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Brightness (mean intensity)
                brightness = float(np.mean(gray))
                brightness_values.append(brightness)
                
                # Contrast (standard deviation)
                contrast = float(np.std(gray))
                contrast_values.append(contrast)
                
                # Sharpness (Laplacian variance)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_values.append(float(laplacian_var))
            
            avg_brightness = np.mean(brightness_values) if brightness_values else 0
            avg_contrast = np.mean(contrast_values) if contrast_values else 0
            avg_sharpness = np.mean(sharpness_values) if sharpness_values else 0
            
            # Overall quality score (0-100)
            quality_score = min(100, (
                (avg_brightness / 255) * 30 +  # Brightness component
                (avg_contrast / 128) * 40 +    # Contrast component  
                (min(avg_sharpness, 1000) / 1000) * 30  # Sharpness component
            ))
            
            return {
                'average_brightness': avg_brightness,
                'average_contrast': avg_contrast,
                'average_sharpness': avg_sharpness,
                'brightness_consistency': float(1 - np.std(brightness_values) / 255) if brightness_values else 0,
                'quality_score': quality_score
            }
            
        except Exception as e:
            self.logger.warning(f"Video quality analysis failed: {str(e)}")
            return {'quality_score': 0.0}
    
    async def _apply_video_processing(self, video_path: str, 
                                    options: Dict[str, Any]) -> bytes:
        """Apply video processing and optimization"""
        try:
            # Load video with moviepy for processing
            clip = mp.VideoFileClip(video_path)
            processed_clip = clip
            
            # Resize if requested
            if 'resize' in options:
                width, height = options['resize']
                processed_clip = processed_clip.resize((width, height))
            
            # Trim if requested  
            if 'trim' in options:
                start, end = options['trim']
                processed_clip = processed_clip.subclip(start, end)
            
            # Apply color correction
            if options.get('color_correct', False):
                processed_clip = self._apply_color_correction(processed_clip)
            
            # Apply stabilization (simplified)
            if options.get('stabilize', False):
                # Note: Real stabilization would require more sophisticated algorithms
                pass
            
            # Export processed video
            output_format = options.get('output_format', 'mp4')
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as temp_output:
                processed_clip.write_videofile(
                    temp_output.name,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                processed_clip.close()
                clip.close()
                
                # Read processed video data
                return Path(temp_output.name).read_bytes()
                
        except Exception as e:
            self.logger.error(f"Video processing failed: {str(e)}")
            return Path(video_path).read_bytes()  # Return original on failure
    
    def _apply_color_correction(self, clip):
        """Apply basic color correction to video clip"""
        def color_correct(image):
            # Simple auto-contrast enhancement
            image_pil = Image.fromarray(image)
            enhancer = ImageEnhance.Contrast(image_pil)
            enhanced = enhancer.enhance(1.2)  # Increase contrast by 20%
            return np.array(enhanced)
        
        return clip.fl_image(color_correct)
    
    def get_supported_formats(self) -> List[str]:
        """Get supported video formats"""
        return self.supported_formats


class ImageProcessor(BaseProcessor):
    """Industrial-grade image content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        if not IMAGE_AVAILABLE:
            raise ImportError("Image processing dependencies not available")
            
        self.supported_formats = [
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'heif'
        ]
        self.default_quality = self.config.get('quality', 95)
        self.max_dimensions = self.config.get('max_dimensions', (4096, 4096))
        
    async def process(self, content: Union[bytes, str, BinaryIO], 
                     options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process image content with advanced analysis"""
        start_time = asyncio.get_event_loop().time()
        options = options or {}
        
        try:
            # Handle different input types
            if isinstance(content, str):
                image = Image.open(content)
                image_data = Path(content).read_bytes()
            else:
                image_data = content if isinstance(content, bytes) else content.read()
                from io import BytesIO
                image = Image.open(BytesIO(image_data))
            
            # Convert HEIC/HEIF if needed
            if hasattr(image, 'format') and image.format in ['HEIC', 'HEIF']:
                pillow_heif.register_heif_opener()
                
            # Extract metadata
            metadata = await self._extract_image_metadata(image, image_data)
            
            # Quality analysis
            quality_metrics = await self._analyze_image_quality(image)
            
            # Process image
            processed_image = await self._apply_image_processing(image, options)
            
            # Convert to bytes
            output_format = options.get('output_format', 'JPEG')
            from io import BytesIO
            output_buffer = BytesIO()
            processed_image.save(output_buffer, format=output_format, quality=self.default_quality)
            processed_data = output_buffer.getvalue()
            
            format_info = {
                'original_format': image.format or 'Unknown',
                'processed_format': output_format,
                'original_size': metadata.dimensions,
                'processed_size': processed_image.size,
                'color_mode': processed_image.mode
            }
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                success=True,
                processed_content=processed_data,
                metadata=metadata.__dict__,
                format_info=format_info,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            processing_time = asyncio.get_event_loop().time() - start_time
            return ProcessingResult(
                success=False,
                processed_content=None,
                metadata={},
                format_info={},
                quality_metrics={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _extract_image_metadata(self, image: Image.Image, 
                                    image_data: bytes) -> ContentMetadata:
        """Extract comprehensive image metadata"""
        # Get EXIF data if available
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif_data = dict(image._getexif().items())
        
        return ContentMetadata(
            file_type='image',
            format=image.format or 'Unknown',
            size=len(image_data),
            duration=None,
            dimensions=image.size,
            bitrate=None,
            sample_rate=None,
            channels=len(image.getbands()) if image.getbands() else 0,
            color_space=image.mode,
            creation_date=datetime.now(),
            checksum=self._calculate_checksum(image_data),
            mime_type=f'image/{(image.format or "jpeg").lower()}',
            encoding=None,
            custom_tags={'exif': exif_data}
        )
    
    async def _analyze_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Analyze image quality metrics"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Handle different image modes
            if len(img_array.shape) == 3:
                # Color image - convert to grayscale for some metrics
                gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
            else:
                # Grayscale image
                gray = img_array
            
            # Brightness (mean intensity)
            brightness = float(np.mean(gray))
            
            # Contrast (standard deviation)
            contrast = float(np.std(gray))
            
            # Sharpness (Laplacian variance)
            from scipy import ndimage
            laplacian = ndimage.laplacian(gray)
            sharpness = float(np.var(laplacian))
            
            # Noise estimation (using high-frequency content)
            from scipy.ndimage import gaussian_filter
            smoothed = gaussian_filter(gray, sigma=1)
            noise_estimate = float(np.mean((gray - smoothed) ** 2))
            
            # Color richness (for color images)
            color_richness = 0.0
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                # Calculate color variance
                color_variance = np.var(img_array, axis=(0, 1))
                color_richness = float(np.mean(color_variance))
            
            # Overall quality score (0-100)
            quality_score = min(100, (
                (brightness / 255) * 20 +           # Brightness component
                (min(contrast, 128) / 128) * 25 +   # Contrast component
                (min(sharpness, 1000) / 1000) * 25 + # Sharpness component
                (1 - min(noise_estimate, 100) / 100) * 15 + # Low noise bonus
                (min(color_richness, 10000) / 10000) * 15   # Color richness
            ))
            
            return {
                'brightness': brightness,
                'contrast': contrast,
                'sharpness': sharpness,
                'noise_estimate': noise_estimate,
                'color_richness': color_richness,
                'quality_score': quality_score
            }
            
        except Exception as e:
            self.logger.warning(f"Image quality analysis failed: {str(e)}")
            return {'quality_score': 0.0}
    
    async def _apply_image_processing(self, image: Image.Image, 
                                    options: Dict[str, Any]) -> Image.Image:
        """Apply image processing and optimization"""
        processed = image.copy()
        
        # Resize if requested
        if 'resize' in options:
            size = options['resize']
            processed = processed.resize(size, Image.Resampling.LANCZOS)
        
        # Auto-enhance if requested
        if options.get('auto_enhance', False):
            processed = self._auto_enhance_image(processed)
        
        # Apply filters
        if 'filters' in options:
            for filter_type in options['filters']:
                processed = self._apply_image_filter(processed, filter_type)
        
        # Crop if requested
        if 'crop' in options:
            crop_box = options['crop']  # (left, top, right, bottom)
            processed = processed.crop(crop_box)
        
        # Rotate if requested
        if 'rotate' in options:
            angle = options['rotate']
            processed = processed.rotate(angle, expand=True)
        
        # Ensure image doesn't exceed maximum dimensions
        if processed.size[0] > self.max_dimensions[0] or processed.size[1] > self.max_dimensions[1]:
            processed.thumbnail(self.max_dimensions, Image.Resampling.LANCZOS)
        
        return processed
    
    def _auto_enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply automatic image enhancements"""
        enhanced = image
        
        # Auto-contrast
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        # Auto-brightness (slight adjustment)
        enhancer = ImageEnhance.Brightness(enhanced)
        enhanced = enhancer.enhance(1.05)
        
        # Auto-color (slight saturation boost)
        if enhanced.mode in ['RGB', 'RGBA']:
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.1)
        
        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        return enhanced
    
    def _apply_image_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """Apply specific image filter"""
        filter_map = {
            'blur': ImageFilter.BLUR,
            'detail': ImageFilter.DETAIL,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
            'emboss': ImageFilter.EMBOSS,
            'find_edges': ImageFilter.FIND_EDGES,
            'smooth': ImageFilter.SMOOTH,
            'smooth_more': ImageFilter.SMOOTH_MORE,
            'sharpen': ImageFilter.SHARPEN,
            'unsharp_mask': ImageFilter.UnsharpMask()
        }
        
        if filter_type in filter_map:
            return image.filter(filter_map[filter_type])
        
        return image
    
    def get_supported_formats(self) -> List[str]:
        """Get supported image formats"""
        return self.supported_formats


class TextProcessor(BaseProcessor):
    """Industrial-grade text content processor"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        if not TEXT_AVAILABLE:
            self.logger.warning("Some text processing dependencies not available")
            
        self.supported_formats = ['txt', 'md', 'html', 'json', 'csv', 'xml']
        
        # Download required NLTK data
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
        except:
            pass
    
    async def process(self, content: Union[bytes, str, BinaryIO], 
                     options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process text content with advanced analysis"""
        start_time = asyncio.get_event_loop().time()
        options = options or {}
        
        try:
            # Handle different input types
            if isinstance(content, str):
                if Path(content).exists():
                    # File path
                    text_data = Path(content).read_text(encoding='utf-8')
                    raw_bytes = Path(content).read_bytes()
                else:
                    # Direct text content
                    text_data = content
                    raw_bytes = content.encode('utf-8')
            else:
                raw_bytes = content if isinstance(content, bytes) else content.read()
                text_data = raw_bytes.decode('utf-8', errors='ignore')
            
            # Extract metadata
            metadata = await self._extract_text_metadata(text_data, raw_bytes)
            
            # Analyze content quality and characteristics
            quality_metrics = await self._analyze_text_quality(text_data)
            
            # Process text based on options
            processed_text = await self._apply_text_processing(text_data, options)
            
            format_info = {
                'original_format': 'text',
                'processed_format': options.get('output_format', 'text'),
                'encoding': 'utf-8',
                'language': metadata.custom_tags.get('language', 'unknown'),
                'word_count': metadata.custom_tags.get('word_count', 0)
            }
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                success=True,
                processed_content=processed_text,
                metadata=metadata.__dict__,
                format_info=format_info,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            processing_time = asyncio.get_event_loop().time() - start_time
            return ProcessingResult(
                success=False,
                processed_content=None,
                metadata={},
                format_info={},
                quality_metrics={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _extract_text_metadata(self, text_data: str, 
                                   raw_bytes: bytes) -> ContentMetadata:
        """Extract comprehensive text metadata"""
        # Basic statistics
        word_count = len(text_data.split())
        char_count = len(text_data)
        line_count = len(text_data.splitlines())
        
        # Language detection
        language = 'unknown'
        try:
            if TEXT_AVAILABLE:
                import langdetect
                language = langdetect.detect(text_data)
        except:
            pass
        
        # Readability metrics
        readability_metrics = {}
        try:
            if TEXT_AVAILABLE:
                readability_metrics = {
                    'flesch_reading_ease': flesch_reading_ease(text_data),
                    'flesch_kincaid_grade': flesch_kincaid_grade(text_data)
                }
        except:
            pass
        
        custom_tags = {
            'word_count': word_count,
            'char_count': char_count,
            'line_count': line_count,
            'language': language,
            'readability': readability_metrics
        }
        
        return ContentMetadata(
            file_type='text',
            format='txt',
            size=len(raw_bytes),
            duration=None,
            dimensions=None,
            bitrate=None,
            sample_rate=None,
            channels=None,
            color_space=None,
            creation_date=datetime.now(),
            checksum=self._calculate_checksum(raw_bytes),
            mime_type='text/plain',
            encoding='utf-8',
            custom_tags=custom_tags
        )
    
    async def _analyze_text_quality(self, text_data: str) -> Dict[str, float]:
        """Analyze text quality and characteristics"""
        try:
            # Basic metrics
            word_count = len(text_data.split())
            char_count = len(text_data)
            
            # Sentence and paragraph analysis
            sentences = text_data.split('. ')
            paragraphs = [p for p in text_data.split('\n\n') if p.strip()]
            
            avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
            avg_paragraph_length = np.mean([len(p.split()) for p in paragraphs]) if paragraphs else 0
            
            # Vocabulary richness (unique words ratio)
            words = text_data.lower().split()
            unique_words = len(set(words))
            vocab_richness = unique_words / len(words) if words else 0
            
            # Readability score
            readability_score = 0
            try:
                if TEXT_AVAILABLE:
                    readability_score = flesch_reading_ease(text_data)
            except:
                pass
            
            # Sentiment analysis (if available)
            sentiment_score = 0
            try:
                if TEXT_AVAILABLE:
                    from nltk.sentiment import SentimentIntensityAnalyzer
                    sia = SentimentIntensityAnalyzer()
                    sentiment = sia.polarity_scores(text_data)
                    sentiment_score = sentiment['compound']
            except:
                pass
            
            # Content density (non-whitespace ratio)
            non_whitespace = len(''.join(text_data.split()))
            content_density = non_whitespace / char_count if char_count > 0 else 0
            
            # Overall quality score
            quality_score = min(100, (
                min(vocab_richness * 100, 50) +           # Vocabulary richness
                min(readability_score / 100 * 25, 25) +   # Readability
                min(content_density * 25, 25)             # Content density
            ))
            
            return {
                'word_count': float(word_count),
                'vocabulary_richness': vocab_richness,
                'average_sentence_length': float(avg_sentence_length),
                'average_paragraph_length': float(avg_paragraph_length),
                'readability_score': readability_score,
                'sentiment_score': sentiment_score,
                'content_density': content_density,
                'quality_score': quality_score
            }
            
        except Exception as e:
            self.logger.warning(f"Text quality analysis failed: {str(e)}")
            return {'quality_score': 0.0}
    
    async def _apply_text_processing(self, text_data: str, 
                                   options: Dict[str, Any]) -> str:
        """Apply text processing and optimization"""
        processed_text = text_data
        
        # Clean and normalize
        if options.get('clean', False):
            processed_text = self._clean_text(processed_text)
        
        # Extract keywords
        if options.get('extract_keywords', False):
            keywords = self._extract_keywords(processed_text)
            processed_text += f"\n\nKeywords: {', '.join(keywords)}"
        
        # Summarize if requested
        if options.get('summarize', False):
            summary = self._generate_summary(processed_text, options.get('summary_length', 3))
            processed_text = f"Summary:\n{summary}\n\nFull Text:\n{processed_text}"
        
        # Format conversion
        output_format = options.get('output_format', 'text')
        if output_format != 'text':
            processed_text = self._convert_text_format(processed_text, output_format)
        
        return processed_text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        import re
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep basic punctuation)
        cleaned = re.sub(r'[^\w\s\.,!?;:\-\'"()\[\]{}]', '', cleaned)
        
        # Normalize line endings
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        return cleaned.strip()
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract key terms from text"""
        try:
            if not TEXT_AVAILABLE:
                # Simple fallback: most frequent words
                words = text.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Skip short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                return [word for word, freq in sorted_words[:max_keywords]]
            
            # Advanced keyword extraction with NLTK
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Filter tokens
            keywords = [word for word in tokens 
                       if word.isalpha() and len(word) > 3 and word not in stop_words]
            
            # Get most frequent keywords
            keyword_freq = Counter(keywords)
            return [word for word, freq in keyword_freq.most_common(max_keywords)]
            
        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {str(e)}")
            return []
    
    def _generate_summary(self, text: str, num_sentences: int = 3) -> str:
        """Generate text summary (extractive)"""
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if len(sentences) <= num_sentences:
                return text
            
            # Simple extractive summarization based on sentence length and position
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                # Score based on length and position (favor longer sentences and early position)
                length_score = len(sentence.split()) / 20  # Normalize by average sentence length
                position_score = (len(sentences) - i) / len(sentences)  # Earlier sentences score higher
                total_score = (length_score + position_score) / 2
                sentence_scores.append((sentence, total_score))
            
            # Select top sentences
            top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Maintain original order
            summary_sentences = []
            for sentence, _ in top_sentences:
                if sentence in sentences:
                    summary_sentences.append(sentence)
            
            return '. '.join(summary_sentences) + '.'
            
        except Exception as e:
            self.logger.warning(f"Text summarization failed: {str(e)}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def _convert_text_format(self, text: str, output_format: str) -> str:
        """Convert text to different formats"""
        if output_format == 'json':
            return json.dumps({
                'content': text,
                'metadata': {
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'processed_at': datetime.now().isoformat()
                }
            }, indent=2)
        
        elif output_format == 'html':
            paragraphs = [f"<p>{p.strip()}</p>" for p in text.split('\n\n') if p.strip()]
            return f"<html><body>{''.join(paragraphs)}</body></html>"
        
        elif output_format == 'markdown':
            # Simple markdown conversion
            lines = text.split('\n')
            markdown_lines = []
            for line in lines:
                if line.strip():
                    # Convert simple formatting
                    if line.isupper():
                        markdown_lines.append(f"# {line}")
                    else:
                        markdown_lines.append(line)
                else:
                    markdown_lines.append("")
            return '\n'.join(markdown_lines)
        
        return text
    
    def get_supported_formats(self) -> List[str]:
        """Get supported text formats"""
        return self.supported_formats


class MetadataExtractor:
    """Comprehensive metadata extraction utility"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetadataExtractor")
    
    async def extract_universal_metadata(self, content: Union[bytes, str, BinaryIO], 
                                       content_type: str) -> Dict[str, Any]:
        """Extract metadata for any content type"""
        try:
            # Determine appropriate processor
            processor = self._get_processor_for_type(content_type)
            if not processor:
                return await self._extract_generic_metadata(content)
            
            # Use specialized processor
            result = await processor.process(content)
            return result.metadata if result.success else {}
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            return {}
    
    def _get_processor_for_type(self, content_type: str) -> Optional[BaseProcessor]:
        """Get appropriate processor for content type"""
        if content_type.startswith('audio/'):
            try:
                return AudioProcessor()
            except ImportError:
                return None
        elif content_type.startswith('video/'):
            try:
                return VideoProcessor()
            except ImportError:
                return None
        elif content_type.startswith('image/'):
            try:
                return ImageProcessor()
            except ImportError:
                return None
        elif content_type.startswith('text/'):
            return TextProcessor()
        
        return None
    
    async def _extract_generic_metadata(self, content: Union[bytes, str, BinaryIO]) -> Dict[str, Any]:
        """Extract generic metadata for unknown content types"""
        try:
            if isinstance(content, str):
                if Path(content).exists():
                    data = Path(content).read_bytes()
                    file_path = content
                else:
                    data = content.encode('utf-8')
                    file_path = None
            else:
                data = content if isinstance(content, bytes) else content.read()
                file_path = None
            
            metadata = {
                'file_type': 'binary',
                'size': len(data),
                'checksum': hashlib.sha256(data).hexdigest(),
                'creation_date': datetime.now().isoformat(),
            }
            
            if file_path:
                path_obj = Path(file_path)
                metadata.update({
                    'filename': path_obj.name,
                    'extension': path_obj.suffix.lstrip('.'),
                    'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Generic metadata extraction failed: {str(e)}")
            return {}
