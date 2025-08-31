"""Compression Processor Module
============================

Enterprise-grade content compression and optimization engine.
Intelligent compression algorithms for maximum efficiency with quality preservation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Features:
- Professional compression algorithms for all content types
- Quality-aware compression with perceptual optimization
- Multi-level compression strategies (lossless, near-lossless, lossy)
- Real-time compression performance analysis
- Adaptive compression based on content characteristics
- Bandwidth optimization for streaming and distribution
- Compression ratio optimization with quality preservation
- Platform-specific compression profiles
"""import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import os
from pathlib import Path
import gzip
import bz2
import lzma
import zlib
from concurrent.futures import ThreadPoolExecutor

# Compression libraries
try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image compression limited")

try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio libraries not available - audio compression limited")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning("FFmpeg not available - video compression limited")

try:
    import zipfile
    import tarfile
    ARCHIVE_AVAILABLE = True
except ImportError:
    ARCHIVE_AVAILABLE = False
    logging.warning("Archive libraries not available")

logger = logging.getLogger(__name__)

@dataclass
class CompressionSettings:
    """Compression configuration settings"""    algorithm: str
    quality_level: int  # 1-100, where 100 is best quality
    compression_level: int  # 1-9, where 9 is maximum compression
    preserve_metadata: bool = True
    use_progressive: bool = False
    use_lossless: bool = False
    target_size: Optional[int] = None  # Target file size in bytes
    target_bitrate: Optional[int] = None  # Target bitrate for video/audio

@dataclass
class CompressionResult:
    """Compression operation result"""    success: bool
    original_size: int
    compressed_size: int
    compression_ratio: float
    quality_score: float
    compression_time: float
    algorithm_used: str
    output_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class CompressionProfile:
    """Compression profile for different use cases"""    profile_name: str
    description: str
    image_settings: Optional[CompressionSettings] = None
    video_settings: Optional[CompressionSettings] = None
    audio_settings: Optional[CompressionSettings] = None
    text_settings: Optional[CompressionSettings] = None
    use_case: str = 'general'  # 'web', 'mobile', 'archive', 'streaming'

class CompressionProcessor:
    """Professional content compression engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize compression profiles and algorithms
        self._initialize_compression_profiles()
        self._initialize_compression_algorithms()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 4)
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default compression configuration"""        return {
            'default_quality': 85,
            'default_compression_level': 6,
            'preserve_metadata': True,
            'enable_progressive': True,
            'parallel_processing': True,
            'max_workers': 4,
            'temp_directory': 'temp_compression',
            'output_directory': 'compressed',
            'overwrite_existing': False,
            
            # Compression thresholds
            'min_compression_ratio': 1.1,  # Minimum 10% reduction
            'target_compression_ratio': 2.0,  # Target 50% reduction
            'max_quality_loss': 5,  # Maximum 5% quality loss
            
            # Algorithm preferences
            'image_algorithm_preference': ['webp', 'jpeg', 'png'],
            'video_algorithm_preference': ['h264', 'h265', 'vp9'],
            'audio_algorithm_preference': ['aac', 'mp3', 'ogg'],
            'text_algorithm_preference': ['lzma', 'bz2', 'gzip'],
            
            # Quality preservation
            'perceptual_optimization': True,
            'content_aware_compression': True,
            'adaptive_bitrate': True,
            
            # Performance settings
            'use_gpu_acceleration': False,
            'hardware_encoding': False,
            'multi_pass_encoding': False,
            'fast_start': True,  # For web optimized videos
            
            # Compression profiles
            'enable_web_optimization': True,
            'enable_mobile_optimization': True,
            'enable_streaming_optimization': True
        }
    
    def _initialize_compression_profiles(self):
        """Initialize predefined compression profiles"""        try:
            self.compression_profiles = {
                'web_optimized': CompressionProfile(
                    profile_name='Web Optimized',
                    description='Optimized for web delivery with fast loading',
                    image_settings=CompressionSettings(
                        algorithm='webp',
                        quality_level=80,
                        compression_level=6,
                        use_progressive=True
                    ),
                    video_settings=CompressionSettings(
                        algorithm='h264',
                        quality_level=75,
                        compression_level=6,
                        target_bitrate=2000  # 2 Mbps
                    ),
                    audio_settings=CompressionSettings(
                        algorithm='aac',
                        quality_level=80,
                        compression_level=5,
                        target_bitrate=128  # 128 kbps
                    ),
                    use_case='web'
                ),
                
                'mobile_optimized': CompressionProfile(
                    profile_name='Mobile Optimized',
                    description='Optimized for mobile devices and limited bandwidth',
                    image_settings=CompressionSettings(
                        algorithm='jpeg',
                        quality_level=70,
                        compression_level=7
                    ),
                    video_settings=CompressionSettings(
                        algorithm='h264',
                        quality_level=70,
                        compression_level=7,
                        target_bitrate=1000  # 1 Mbps
                    ),
                    audio_settings=CompressionSettings(
                        algorithm='aac',
                        quality_level=75,
                        compression_level=6,
                        target_bitrate=96  # 96 kbps
                    ),
                    use_case='mobile'
                ),
                
                'high_quality': CompressionProfile(
                    profile_name='High Quality',
                    description='Maximum quality with moderate compression',
                    image_settings=CompressionSettings(
                        algorithm='png',
                        quality_level=95,
                        compression_level=3,
                        use_lossless=True
                    ),
                    video_settings=CompressionSettings(
                        algorithm='h265',
                        quality_level=90,
                        compression_level=4,
                        target_bitrate=8000  # 8 Mbps
                    ),
                    audio_settings=CompressionSettings(
                        algorithm='flac',
                        quality_level=100,
                        compression_level=5,
                        use_lossless=True
                    ),
                    use_case='archive'
                ),
                
                'streaming_optimized': CompressionProfile(
                    profile_name='Streaming Optimized',
                    description='Optimized for real-time streaming',
                    video_settings=CompressionSettings(
                        algorithm='h264',
                        quality_level=75,
                        compression_level=8,
                        target_bitrate=3000  # 3 Mbps
                    ),
                    audio_settings=CompressionSettings(
                        algorithm='aac',
                        quality_level=85,
                        compression_level=5,
                        target_bitrate=160  # 160 kbps
                    ),
                    use_case='streaming'
                ),
                
                'maximum_compression': CompressionProfile(
                    profile_name='Maximum Compression',
                    description='Smallest file size with acceptable quality',
                    image_settings=CompressionSettings(
                        algorithm='webp',
                        quality_level=60,
                        compression_level=9
                    ),
                    video_settings=CompressionSettings(
                        algorithm='h265',
                        quality_level=60,
                        compression_level=9,
                        target_bitrate=500  # 500 kbps
                    ),
                    audio_settings=CompressionSettings(
                        algorithm='ogg',
                        quality_level=65,
                        compression_level=9,
                        target_bitrate=64  # 64 kbps
                    ),
                    use_case='archive'
                )
            }
            
            self.logger.info("Compression profiles initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing compression profiles: {str(e)}")
            raise
    
    def _initialize_compression_algorithms(self):
        """Initialize compression algorithms"""        try:
            self.compression_algorithms = {
                'image': {
                    'jpeg': self._compress_image_jpeg,
                    'webp': self._compress_image_webp,
                    'png': self._compress_image_png,
                    'avif': self._compress_image_avif
                },
                'video': {
                    'h264': self._compress_video_h264,
                    'h265': self._compress_video_h265,
                    'vp9': self._compress_video_vp9,
                    'av1': self._compress_video_av1
                },
                'audio': {
                    'aac': self._compress_audio_aac,
                    'mp3': self._compress_audio_mp3,
                    'ogg': self._compress_audio_ogg,
                    'flac': self._compress_audio_flac
                },
                'text': {
                    'gzip': self._compress_text_gzip,
                    'bz2': self._compress_text_bz2,
                    'lzma': self._compress_text_lzma,
                    'zip': self._compress_text_zip
                }
            }
            
            self.logger.info("Compression algorithms initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing compression algorithms: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        profile: Optional[str] = None,
        custom_settings: Optional[CompressionSettings] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main compression pipeline
        
        Args:
            content_data: Content data as bytes or file path
            content_type: Type of content (image, video, audio, text)
            profile: Compression profile name
            custom_settings: Custom compression settings
            config: Optional configuration override
        
        Returns:
            Dict containing compression results
        """        try:
            start_time = datetime.now()
            
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare content
            input_path, is_temp = await self._prepare_content(content_data)
            
            try:
                # Get compression settings
                compression_settings = await self._get_compression_settings(
                    content_type, profile, custom_settings
                )
                
                # Analyze content characteristics
                content_analysis = await self._analyze_content(input_path, content_type)
                
                # Optimize compression settings based on content
                if processing_config.get('content_aware_compression', True):
                    compression_settings = await self._optimize_compression_settings(
                        compression_settings, content_analysis
                    )
                
                # Perform compression
                compression_result = await self._perform_compression(
                    input_path,
                    content_type,
                    compression_settings,
                    processing_config
                )
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Compile result
                result = {
                    'success': True,
                    'content_type': content_type,
                    'profile_used': profile,
                    'compression_result': compression_result,
                    'content_analysis': content_analysis,
                    'compression_settings': compression_settings.__dict__,
                    'processing_time': processing_time,
                    'processing_config': processing_config,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"Compression completed for {content_type}")
                return result
                
            finally:
                # Cleanup temporary input file if created
                if is_temp and os.path.exists(input_path):
                    os.unlink(input_path)
            
        except Exception as e:
            self.logger.error(f"Compression failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content_type': content_type,
                'profile': profile,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_content(self, content_data: Union[bytes, str]) -> Tuple[str, bool]:
        """Prepare content for compression"""        try:
            if isinstance(content_data, str):
                # Already a file path
                if os.path.exists(content_data):
                    return content_data, False
                else:
                    raise FileNotFoundError(f"File not found: {content_data}")
                    
            elif isinstance(content_data, bytes):
                # Save bytes to temporary file
                temp_dir = self.config.get('temp_directory', 'temp_compression')
                os.makedirs(temp_dir, exist_ok=True)
                
                with tempfile.NamedTemporaryFile(
                    dir=temp_dir,
                    delete=False
                ) as tmp_file:
                    tmp_file.write(content_data)
                    return tmp_file.name, True
            else:
                raise ValueError(f"Unsupported content data type: {type(content_data)}")
                
        except Exception as e:
            self.logger.error(f"Error preparing content: {str(e)}")
            raise
    
    async def _get_compression_settings(
        self,
        content_type: str,
        profile: Optional[str],
        custom_settings: Optional[CompressionSettings]
    ) -> CompressionSettings:
        """Get compression settings for content type"""        try:
            if custom_settings:
                return custom_settings
            
            if profile and profile in self.compression_profiles:
                compression_profile = self.compression_profiles[profile]
                
                if content_type == 'image' and compression_profile.image_settings:
                    return compression_profile.image_settings
                elif content_type == 'video' and compression_profile.video_settings:
                    return compression_profile.video_settings
                elif content_type == 'audio' and compression_profile.audio_settings:
                    return compression_profile.audio_settings
                elif content_type == 'text' and compression_profile.text_settings:
                    return compression_profile.text_settings
            
            # Default settings
            algorithm_preferences = self.config.get(f'{content_type}_algorithm_preference', [])
            default_algorithm = algorithm_preferences[0] if algorithm_preferences else 'default'
            
            return CompressionSettings(
                algorithm=default_algorithm,
                quality_level=self.config.get('default_quality', 85),
                compression_level=self.config.get('default_compression_level', 6),
                preserve_metadata=self.config.get('preserve_metadata', True),
                use_progressive=self.config.get('enable_progressive', True)
            )
            
        except Exception as e:
            self.logger.error(f"Error getting compression settings: {str(e)}")
            raise
    
    async def _analyze_content(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """Analyze content characteristics for compression optimization"""        try:
            analysis = {
                'file_size': os.path.getsize(file_path),
                'content_type': content_type,
                'complexity_score': 0.5,  # Default medium complexity
                'compression_potential': 0.7  # Default good compression potential
            }
            
            if content_type == 'image':
                analysis.update(await self._analyze_image_content(file_path))
            elif content_type == 'video':
                analysis.update(await self._analyze_video_content(file_path))
            elif content_type == 'audio':
                analysis.update(await self._analyze_audio_content(file_path))
            elif content_type == 'text':
                analysis.update(await self._analyze_text_content(file_path))
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {'file_size': 0, 'complexity_score': 0.5, 'compression_potential': 0.5}
    
    async def _analyze_image_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze image content characteristics"""        try:
            if not PIL_AVAILABLE:
                return {}
            
            with Image.open(file_path) as img:
                # Standard image properties
                width, height = img.size
                mode = img.mode
                
                # Convert to numpy array for analysis
                img_array = np.array(img)
                
                # Calculate complexity metrics
                if len(img_array.shape) == 3:
                    # Color image
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img_array
                
                # Edge density (complexity indicator)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (width * height)
                
                # Color diversity
                unique_colors = len(np.unique(img_array.reshape(-1, img_array.shape[-1]), axis=0))
                color_diversity = min(unique_colors / (width * height), 1.0)
                
                # Texture complexity (using standard deviation)
                texture_complexity = np.std(gray) / 255.0
                
                # Overall complexity score
                complexity_score = (edge_density * 0.4 + color_diversity * 0.3 + texture_complexity * 0.3)
                
                # Compression potential (inverse of complexity)
                compression_potential = 1.0 - complexity_score
                
                return {
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'pixel_count': width * height,
                    'edge_density': edge_density,
                    'color_diversity': color_diversity,
                    'texture_complexity': texture_complexity,
                    'complexity_score': complexity_score,
                    'compression_potential': compression_potential
                }
                
        except Exception as e:
            self.logger.error(f"Image content analysis failed: {str(e)}")
            return {}
    
    async def _analyze_video_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze video content characteristics"""        try:
            if not FFMPEG_AVAILABLE:
                return {}
            
            # Get video information
            probe = ffmpeg.probe(file_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                return {}
            
            # Standard video properties
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(video_stream.get('duration', 0))
            fps_str = video_stream.get('r_frame_rate', '0/1')
            fps = eval(fps_str) if '/' in fps_str else float(fps_str)
            
            # Estimate motion complexity (simplified)
            # In a full implementation, you'd analyze frame differences
            motion_complexity = 0.5  # Placeholder
            
            # Compression potential based on content type
            compression_potential = 0.7  # Default for video
            
            return {
                'width': width,
                'height': height,
                'duration': duration,
                'fps': fps,
                'pixel_count': width * height,
                'total_frames': int(duration * fps) if fps > 0 else 0,
                'motion_complexity': motion_complexity,
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Video content analysis failed: {str(e)}")
            return {}
    
    async def _analyze_audio_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio content characteristics"""        try:
            if not AUDIO_LIBS_AVAILABLE:
                return {}
            
            # Load audio for analysis
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            # Dynamic range analysis
            rms = np.sqrt(np.mean(audio_data**2))
            peak = np.max(np.abs(audio_data))
            dynamic_range = 20 * np.log10(peak / max(rms, 1e-10))
            
            # Frequency content analysis
            if AUDIO_LIBS_AVAILABLE:
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
                avg_spectral_centroid = np.mean(spectral_centroid)
            else:
                avg_spectral_centroid = 0
            
            # Complexity based on dynamic range and spectral content
            complexity_score = min((dynamic_range / 60) * 0.6 + (avg_spectral_centroid / 8000) * 0.4, 1.0)
            compression_potential = 1.0 - complexity_score
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                'dynamic_range': dynamic_range,
                'spectral_centroid': avg_spectral_centroid,
                'complexity_score': complexity_score,
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Audio content analysis failed: {str(e)}")
            return {}
    
    async def _analyze_text_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze text content characteristics"""        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Standard text metrics
            char_count = len(content)
            word_count = len(content.split())
            line_count = len(content.split('
'))
            
            # Character frequency analysis for compression potential
            char_freq = {}
            for char in content:
                char_freq[char] = char_freq.get(char, 0) + 1
            
            # Calculate entropy (measure of randomness)
            entropy = 0
            for count in char_freq.values():
                probability = count / char_count
                if probability > 0:
                    entropy -= probability * np.log2(probability)
            
            # Compression potential (higher entropy = lower compression potential)
            max_entropy = 8  # Maximum entropy for 8-bit characters
            compression_potential = 1.0 - (entropy / max_entropy)
            
            # Repetition analysis
            unique_chars = len(char_freq)
            repetition_score = 1.0 - (unique_chars / char_count)
            
            return {
                'char_count': char_count,
                'word_count': word_count,
                'line_count': line_count,
                'unique_chars': unique_chars,
                'entropy': entropy,
                'repetition_score': repetition_score,
                'compression_potential': compression_potential
            }
            
        except Exception as e:
            self.logger.error(f"Text content analysis failed: {str(e)}")
            return {}
    
    async def _optimize_compression_settings(
        self,
        settings: CompressionSettings,
        content_analysis: Dict[str, Any]
    ) -> CompressionSettings:
        """Optimize compression settings based on content analysis"""        try:
            optimized_settings = CompressionSettings(
                algorithm=settings.algorithm,
                quality_level=settings.quality_level,
                compression_level=settings.compression_level,
                preserve_metadata=settings.preserve_metadata,
                use_progressive=settings.use_progressive,
                use_lossless=settings.use_lossless,
                target_size=settings.target_size,
                target_bitrate=settings.target_bitrate
            )
            
            # Adjust based on compression potential
            compression_potential = content_analysis.get('compression_potential', 0.5)
            
            if compression_potential > 0.8:
                # High compression potential - can use higher compression
                optimized_settings.compression_level = min(9, settings.compression_level + 2)
            elif compression_potential < 0.3:
                # Low compression potential - use lower compression to preserve quality
                optimized_settings.compression_level = max(1, settings.compression_level - 2)
                optimized_settings.quality_level = min(100, settings.quality_level + 10)
            
            # Adjust based on complexity
            complexity_score = content_analysis.get('complexity_score', 0.5)
            
            if complexity_score > 0.7:
                # High complexity content - prioritize quality
                optimized_settings.quality_level = min(100, settings.quality_level + 5)
            elif complexity_score < 0.3:
                # Low complexity content - can use more aggressive compression
                optimized_settings.compression_level = min(9, settings.compression_level + 1)
            
            return optimized_settings
            
        except Exception as e:
            self.logger.error(f"Error optimizing compression settings: {str(e)}")
            return settings
    
    async def _perform_compression(
        self,
        input_path: str,
        content_type: str,
        settings: CompressionSettings,
        config: Dict[str, Any]
    ) -> CompressionResult:
        """Perform the actual compression"""        try:
            start_time = datetime.now()
            
            # Get compression algorithm
            algorithms = self.compression_algorithms.get(content_type, {})
            compression_func = algorithms.get(settings.algorithm)
            
            if not compression_func:
                raise ValueError(f"Unsupported algorithm '{settings.algorithm}' for {content_type}")
            
            # Create output path
            output_path = await self._create_output_path(input_path, settings, config)
            
            # Perform compression
            result = await compression_func(input_path, output_path, settings)
            
            # Calculate compression metrics
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path) if result.success else 0
            compression_ratio = original_size / max(compressed_size, 1) if result.success else 1.0
            compression_time = (datetime.now() - start_time).total_seconds()
            
            # Update result with calculated metrics
            result.original_size = original_size
            result.compressed_size = compressed_size
            result.compression_ratio = compression_ratio
            result.compression_time = compression_time
            result.output_path = output_path
            
            return result
            
        except Exception as e:
            self.logger.error(f"Compression failed: {str(e)}")
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used=settings.algorithm,
                output_path='',
                error_message=str(e)
            )
    
    async def _create_output_path(
        self,
        input_path: str,
        settings: CompressionSettings,
        config: Dict[str, Any]
    ) -> str:
        """Create output file path for compressed content"""        try:
            input_file = Path(input_path)
            output_dir = config.get('output_directory', 'compressed')
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            base_name = input_file.stem
            extension = input_file.suffix
            
            # Add compression indicator to filename
            output_filename = f"{base_name}_compressed{extension}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Handle existing files
            if os.path.exists(output_path) and not config.get('overwrite_existing', False):
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_compressed_{counter}{extension}"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating output path: {str(e)}")
            raise
    
    # Compression algorithm implementations
    async def _compress_image_jpeg(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress image using JPEG algorithm"""        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL not available for JPEG compression")
            
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ['RGBA', 'LA']:
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save with JPEG compression
                save_kwargs = {
                    'quality': settings.quality_level,
                    'optimize': True,
                    'progressive': settings.use_progressive
                }
                
                img.save(output_path, 'JPEG', **save_kwargs)
            
            # Calculate quality score (simplified)
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,  # Will be filled by caller
                compressed_size=0,  # Will be filled by caller
                compression_ratio=0,  # Will be filled by caller
                quality_score=quality_score,
                compression_time=0,  # Will be filled by caller
                algorithm_used='jpeg',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='jpeg',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_image_webp(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress image using WebP algorithm"""        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL not available for WebP compression")
            
            with Image.open(input_path) as img:
                save_kwargs = {
                    'quality': settings.quality_level,
                    'method': 6,  # Good quality/speed tradeoff
                    'lossless': settings.use_lossless
                }
                
                img.save(output_path, 'WEBP', **save_kwargs)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='webp',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='webp',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_image_png(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress image using PNG algorithm"""        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL not available for PNG compression")
            
            with Image.open(input_path) as img:
                save_kwargs = {
                    'optimize': True,
                    'compress_level': settings.compression_level
                }
                
                img.save(output_path, 'PNG', **save_kwargs)
            
            quality_score = 1.0  # PNG is lossless
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='png',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='png',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_image_avif(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress image using AVIF algorithm (placeholder)"""        # AVIF support requires additional libraries
        # For now, fallback to WebP
        return await self._compress_image_webp(input_path, output_path, settings)
    
    # Video compression algorithms
    async def _compress_video_h264(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress video using H.264 algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for H.264 compression")
            
            # Build FFmpeg command
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'vcodec': 'libx264',
                'crf': max(0, min(51, 51 - (settings.quality_level * 51 // 100))),
                'preset': 'medium'
            }
            
            if settings.target_bitrate:
                output_options['b:v'] = f"{settings.target_bitrate}k"
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='h264',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='h264',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_video_h265(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress video using H.265 algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for H.265 compression")
            
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'vcodec': 'libx265',
                'crf': max(0, min(51, 51 - (settings.quality_level * 51 // 100))),
                'preset': 'medium'
            }
            
            if settings.target_bitrate:
                output_options['b:v'] = f"{settings.target_bitrate}k"
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='h265',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='h265',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_video_vp9(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress video using VP9 algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for VP9 compression")
            
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'vcodec': 'libvpx-vp9',
                'crf': max(0, min(63, 63 - (settings.quality_level * 63 // 100))),
                'speed': 2
            }
            
            if settings.target_bitrate:
                output_options['b:v'] = f"{settings.target_bitrate}k"
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='vp9',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='vp9',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_video_av1(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress video using AV1 algorithm (placeholder)"""        # AV1 encoding is very slow and requires specific builds
        # For now, fallback to H.265
        return await self._compress_video_h265(input_path, output_path, settings)
    
    # Audio compression algorithms
    async def _compress_audio_aac(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress audio using AAC algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for AAC compression")
            
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'acodec': 'aac',
                'b:a': f"{settings.target_bitrate or 128}k"
            }
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='aac',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='aac',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_audio_mp3(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress audio using MP3 algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for MP3 compression")
            
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'acodec': 'libmp3lame',
                'b:a': f"{settings.target_bitrate or 192}k"
            }
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='mp3',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='mp3',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_audio_ogg(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress audio using OGG algorithm"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for OGG compression")
            
            input_stream = ffmpeg.input(input_path)
            
            output_options = {
                'acodec': 'libvorbis',
                'b:a': f"{settings.target_bitrate or 128}k"
            }
            
            output_stream = input_stream.output(output_path, **output_options)
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            quality_score = settings.quality_level / 100.0
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='ogg',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='ogg',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_audio_flac(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress audio using FLAC algorithm (lossless)"""        try:
            if not AUDIO_LIBS_AVAILABLE:
                raise RuntimeError("Audio libraries not available for FLAC compression")
            
            # Load and save with FLAC compression
            audio_data, sample_rate = librosa.load(input_path, sr=None)
            
            sf.write(
                output_path,
                audio_data,
                sample_rate,
                format='FLAC',
                subtype='PCM_16'
            )
            
            quality_score = 1.0  # FLAC is lossless
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='flac',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='flac',
                output_path='',
                error_message=str(e)
            )
    
    # Text compression algorithms
    async def _compress_text_gzip(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress text using GZIP algorithm"""        try:
            with open(input_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb', compresslevel=settings.compression_level) as f_out:
                    f_out.writelines(f_in)
            
            quality_score = 1.0  # Lossless compression
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='gzip',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='gzip',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_text_bz2(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress text using BZ2 algorithm"""        try:
            with open(input_path, 'rb') as f_in:
                with bz2.open(output_path, 'wb', compresslevel=settings.compression_level) as f_out:
                    f_out.writelines(f_in)
            
            quality_score = 1.0  # Lossless compression
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='bz2',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='bz2',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_text_lzma(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress text using LZMA algorithm"""        try:
            with open(input_path, 'rb') as f_in:
                with lzma.open(output_path, 'wb', preset=settings.compression_level) as f_out:
                    f_out.writelines(f_in)
            
            quality_score = 1.0  # Lossless compression
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='lzma',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='lzma',
                output_path='',
                error_message=str(e)
            )
    
    async def _compress_text_zip(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ) -> CompressionResult:
        """Compress text using ZIP algorithm"""        try:
            if not ARCHIVE_AVAILABLE:
                raise RuntimeError("Archive libraries not available")
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=settings.compression_level) as zip_file:
                zip_file.write(input_path, Path(input_path).name)
            
            quality_score = 1.0  # Lossless compression
            
            return CompressionResult(
                success=True,
                original_size=0,
                compressed_size=0,
                compression_ratio=0,
                quality_score=quality_score,
                compression_time=0,
                algorithm_used='zip',
                output_path=output_path
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                quality_score=0.0,
                compression_time=0.0,
                algorithm_used='zip',
                output_path='',
                error_message=str(e)
            )
    
    async def batch_compress(
        self,
        file_list: List[Tuple[str, str]],  # (file_path, content_type)
        profile: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Compress multiple files in batch"""        if not self.config.get('parallel_processing', True):
            # Sequential processing
            results = []
            for file_path, content_type in file_list:
                result = await self.process(
                    file_path,
                    content_type,
                    profile=profile,
                    config=config
                )
                results.append(result)
            return results
        else:
            # Parallel processing
            tasks = []
            for file_path, content_type in file_list:
                task = self.process(
                    file_path,
                    content_type,
                    profile=profile,
                    config=config
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return [
                result if not isinstance(result, Exception) 
                else {
                    'success': False, 
                    'error': str(result), 
                    'file': file_list[i][0],
                    'content_type': file_list[i][1]
                }
                for i, result in enumerate(results)
            ]
    
    def __del__(self):
        """Cleanup resources"""        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

import asyncio
import logging
import os
import zlib
import gzip
import bz2
import lzma
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np
import json

logger = logging.getLogger(__name__)

@dataclass
class CompressionResult:
    """Compression operation result"""    success: bool
    compressed_data: Optional[bytes] = None
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    compression_time: float = 0.0
    algorithm: str = ""
    quality_score: float = 0.0
    error: Optional[str] = None

@dataclass
class CompressionProfile:
    """Compression profile configuration"""    name: str
    algorithm: str
    level: int = 6  # Compression level (1-9)
    target: str = 'balanced'  # size, speed, quality, balanced
    content_type: str = 'generic'
    
    # Professional settings
    chunk_size: int = 8192
    parallel_processing: bool = True
    quality_threshold: float = 80.0

class CompressionProcessor:
    """Professional content compression and optimization engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize compression engines
        self._initialize_engines()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default compression configuration"""        return {
            'default_algorithm': 'lzma',
            'quality_preservation': True,
            'parallel_processing': True,
            'chunk_size': 8192,
            'max_compression_time': 30.0,  # seconds
            
            'algorithms': {
                'zlib': {
                    'levels': list(range(1, 10)),
                    'speed': 'fast',
                    'ratio': 'medium',
                    'cpu_usage': 'low'
                },
                'gzip': {
                    'levels': list(range(1, 10)),
                    'speed': 'fast',
                    'ratio': 'medium',
                    'cpu_usage': 'low'
                },
                'bz2': {
                    'levels': list(range(1, 10)),
                    'speed': 'slow',
                    'ratio': 'high',
                    'cpu_usage': 'high'
                },
                'lzma': {
                    'levels': list(range(1, 10)),
                    'speed': 'very_slow',
                    'ratio': 'very_high',
                    'cpu_usage': 'very_high'
                }
            },
            
            'content_profiles': {
                'text': {
                    'preferred_algorithm': 'lzma',
                    'level': 6,
                    'expected_ratio': 0.3
                },
                'image': {
                    'preferred_algorithm': 'zlib',
                    'level': 6,
                    'expected_ratio': 0.8
                },
                'audio': {
                    'preferred_algorithm': 'gzip',
                    'level': 6,
                    'expected_ratio': 0.9
                },
                'video': {
                    'preferred_algorithm': 'gzip',
                    'level': 3,
                    'expected_ratio': 0.95
                }
            },
            
            'optimization_targets': {
                'size': {'level': 9, 'algorithm': 'lzma'},
                'speed': {'level': 1, 'algorithm': 'zlib'},
                'balanced': {'level': 6, 'algorithm': 'gzip'},
                'quality': {'level': 3, 'algorithm': 'zlib'}
            }
        }
    
    def _initialize_engines(self):
        """Initialize compression processing components"""        try:
            # Initialize algorithm-specific compressors
            self.compressors = {
                'zlib': ZlibCompressor(),
                'gzip': GzipCompressor(),
                'bz2': Bz2Compressor(),
                'lzma': LzmaCompressor()
            }
            
            # Initialize adaptive compression engine
            self.adaptive_compressor = AdaptiveCompressor(self.config)
            
            self.logger.info("Compression processor engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing compression engines: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        content_type: str = 'generic',
        algorithm: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main compression processing pipeline
        
        Args:
            content_data: Content data to compress
            content_type: Type of content for optimization
            algorithm: Specific algorithm to use (auto-select if None)
            config: Optional compression configuration
        
        Returns:
            Dict containing compression results and analytics
        """        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare data
            data_bytes = await self._prepare_data(content_data)
            if not data_bytes:
                return {
                    'success': False,
                    'error': 'Invalid input data'
                }
            
            # Select optimal compression strategy
            if algorithm:
                compression_strategy = await self._get_algorithm_strategy(algorithm, content_type)
            else:
                compression_strategy = await self._select_optimal_strategy(
                    data_bytes, content_type, processing_config
                )
            
            # Perform compression
            compression_result = await self._compress_data(
                data_bytes, compression_strategy, processing_config
            )
            
            # Analyze compression performance
            analytics = await self._analyze_compression(
                data_bytes, compression_result, content_type
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                compression_result, analytics, content_type
            )
            
            # Compile final result
            result = {
                'success': compression_result.success,
                'compression_result': compression_result,
                'analytics': analytics,
                'recommendations': recommendations,
                'strategy_used': compression_strategy,
                'content_type': content_type,
                'original_size': len(data_bytes),
                'processing_config': processing_config,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            if not compression_result.success:
                result['error'] = compression_result.error
            
            self.logger.info(f"Compression completed for {content_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"Compression processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content_type': content_type
            }
    
    async def _prepare_data(self, content_data: Union[bytes, str]) -> Optional[bytes]:
        """Prepare content data for compression"""        try:
            if isinstance(content_data, bytes):
                return content_data
            elif isinstance(content_data, str):
                if os.path.exists(content_data):
                    # File path
                    with open(content_data, 'rb') as f:
                        return f.read()
                else:
                    # String content
                    return content_data.encode('utf-8')
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Data preparation failed: {str(e)}")
            return None
    
    async def _select_optimal_strategy(
        self,
        data_bytes: bytes,
        content_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select optimal compression strategy based on content analysis"""        try:
            # Get content profile
            content_profile = config['content_profiles'].get(content_type, {})
            
            # Analyze data characteristics
            data_analysis = await self._analyze_data_characteristics(data_bytes)
            
            # Select algorithm based on content type and characteristics
            if data_analysis['entropy'] > 0.9:
                # High entropy data (already compressed/encrypted) - use fast compression
                algorithm = 'zlib'
                level = 1
            elif data_analysis['repetition_ratio'] > 0.3:
                # High repetition - use high compression
                algorithm = content_profile.get('preferred_algorithm', 'lzma')
                level = 8
            else:
                # Balanced approach
                algorithm = content_profile.get('preferred_algorithm', 'gzip')
                level = content_profile.get('level', 6)
            
            return {
                'algorithm': algorithm,
                'level': level,
                'reasoning': f"Selected based on entropy={data_analysis['entropy']:.2f}, repetition={data_analysis['repetition_ratio']:.2f}"
            }
            
        except Exception as e:
            self.logger.error(f"Strategy selection failed: {str(e)}")
            return {
                'algorithm': config['default_algorithm'],
                'level': 6,
                'reasoning': 'Default fallback'
            }
    
    async def _get_algorithm_strategy(self, algorithm: str, content_type: str) -> Dict[str, Any]:
        """Get strategy for specific algorithm"""        content_profile = self.config['content_profiles'].get(content_type, {})
        
        return {
            'algorithm': algorithm,
            'level': content_profile.get('level', 6),
            'reasoning': f'User-specified algorithm: {algorithm}'
        }
    
    async def _analyze_data_characteristics(self, data_bytes: bytes) -> Dict[str, Any]:
        """Analyze data characteristics for compression optimization"""        try:
            analysis = {}
            
            # Calculate entropy (measure of randomness)
            byte_counts = np.bincount(np.frombuffer(data_bytes, dtype=np.uint8), minlength=256)
            probabilities = byte_counts / len(data_bytes)
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            analysis['entropy'] = entropy / 8.0  # Normalize to 0-1
            
            # Calculate repetition ratio
            unique_bytes = len(np.unique(np.frombuffer(data_bytes, dtype=np.uint8)))
            analysis['repetition_ratio'] = 1 - (unique_bytes / 256)
            
            # Calculate pattern detection
            if len(data_bytes) > 1000:
                sample = data_bytes[:1000]
                patterns = {}
                for i in range(len(sample) - 3):
                    pattern = sample[i:i+4]
                    patterns[pattern] = patterns.get(pattern, 0) + 1
                
                if patterns:
                    max_pattern_count = max(patterns.values())
                    analysis['pattern_density'] = max_pattern_count / (len(sample) - 3)
                else:
                    analysis['pattern_density'] = 0.0
            else:
                analysis['pattern_density'] = 0.0
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Data analysis failed: {str(e)}")
            return {
                'entropy': 0.5,
                'repetition_ratio': 0.5,
                'pattern_density': 0.0
            }
    
    async def _compress_data(
        self,
        data_bytes: bytes,
        strategy: Dict[str, Any],
        config: Dict[str, Any]
    ) -> CompressionResult:
        """Compress data using specified strategy"""        try:
            start_time = asyncio.get_event_loop().time()
            
            algorithm = strategy['algorithm']
            level = strategy['level']
            
            # Get compressor
            compressor = self.compressors.get(algorithm)
            if not compressor:
                return CompressionResult(
                    success=False,
                    error=f"Compressor for algorithm '{algorithm}' not available"
                )
            
            # Perform compression
            compressed_data = await compressor.compress(data_bytes, level, config)
            
            compression_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate metrics
            original_size = len(data_bytes)
            compressed_size = len(compressed_data)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Estimate quality score (algorithm-dependent)
            quality_score = await self._estimate_quality_score(
                algorithm, level, compression_ratio
            )
            
            return CompressionResult(
                success=True,
                compressed_data=compressed_data,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                algorithm=algorithm,
                quality_score=quality_score
            )
            
        except Exception as e:
            self.logger.error(f"Data compression failed: {str(e)}")
            return CompressionResult(
                success=False,
                error=str(e)
            )
    
    async def _estimate_quality_score(
        self,
        algorithm: str,
        level: int,
        compression_ratio: float
    ) -> float:
        """Estimate quality score based on compression parameters"""        try:
            # Base score from compression ratio
            ratio_score = max(0, (1 - compression_ratio) * 100)
            
            # Algorithm quality factor
            algorithm_factors = {
                'lzma': 1.0,    # Highest quality
                'bz2': 0.95,
                'gzip': 0.9,
                'zlib': 0.85
            }
            
            algorithm_factor = algorithm_factors.get(algorithm, 0.8)
            
            # Level factor (higher levels generally mean better compression)
            level_factor = min(1.0, level / 9.0)
            
            quality_score = ratio_score * algorithm_factor * (0.5 + 0.5 * level_factor)
            
            return min(100.0, max(0.0, quality_score))
            
        except Exception:
            return 50.0  # Default score
    
    async def _analyze_compression(
        self,
        original_data: bytes,
        compression_result: CompressionResult,
        content_type: str
    ) -> Dict[str, Any]:
        """Analyze compression performance and results"""        try:
            analytics = {
                'performance': {},
                'efficiency': {},
                'quality': {},
                'recommendations': []
            }
            
            if not compression_result.success:
                return analytics
            
            # Performance analysis
            analytics['performance'] = {
                'compression_speed': len(original_data) / max(compression_result.compression_time, 0.001),  # bytes/second
                'time_per_mb': compression_result.compression_time / max(len(original_data) / (1024*1024), 0.001),
                'efficiency_rating': self._rate_performance(compression_result.compression_time, len(original_data))
            }
            
            # Efficiency analysis
            size_reduction_percent = (1 - compression_result.compression_ratio) * 100
            analytics['efficiency'] = {
                'size_reduction_percent': size_reduction_percent,
                'space_saved_bytes': compression_result.original_size - compression_result.compressed_size,
                'compression_effectiveness': self._rate_compression_effectiveness(compression_result.compression_ratio, content_type)
            }
            
            # Quality analysis
            analytics['quality'] = {
                'estimated_quality_score': compression_result.quality_score,
                'quality_rating': self._rate_quality(compression_result.quality_score),
                'reversibility': 'lossless' if compression_result.algorithm in ['zlib', 'gzip', 'bz2', 'lzma'] else 'lossy'
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Compression analysis failed: {str(e)}")
            return {
                'performance': {},
                'efficiency': {},
                'quality': {},
                'error': str(e)
            }
    
    def _rate_performance(self, compression_time: float, data_size: int) -> str:
        """Rate compression performance"""        speed = data_size / max(compression_time, 0.001)
        
        if speed > 10 * 1024 * 1024:  # > 10 MB/s
            return 'excellent'
        elif speed > 5 * 1024 * 1024:  # > 5 MB/s
            return 'good'
        elif speed > 1 * 1024 * 1024:  # > 1 MB/s
            return 'fair'
        else:
            return 'poor'
    
    def _rate_compression_effectiveness(self, ratio: float, content_type: str) -> str:
        """Rate compression effectiveness based on content type expectations"""        expected_ratios = {
            'text': 0.3,
            'image': 0.8,
            'audio': 0.9,
            'video': 0.95
        }
        
        expected = expected_ratios.get(content_type, 0.7)
        
        if ratio <= expected * 0.8:
            return 'excellent'
        elif ratio <= expected:
            return 'good'
        elif ratio <= expected * 1.2:
            return 'fair'
        else:
            return 'poor'
    
    def _rate_quality(self, quality_score: float) -> str:
        """Rate overall quality"""        if quality_score >= 90:
            return 'excellent'
        elif quality_score >= 80:
            return 'good'
        elif quality_score >= 70:
            return 'fair'
        else:
            return 'poor'
    
    async def _generate_recommendations(
        self,
        compression_result: CompressionResult,
        analytics: Dict[str, Any],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""        try:
            recommendations = []
            
            if not compression_result.success:
                return recommendations
            
            # Performance recommendations
            performance_rating = analytics.get('performance', {}).get('efficiency_rating', 'fair')
            if performance_rating == 'poor':
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'suggestion': 'Consider using a faster compression algorithm like zlib for better performance',
                    'expected_improvement': 'Faster compression speed'
                })
            
            # Compression effectiveness recommendations
            effectiveness = analytics.get('efficiency', {}).get('compression_effectiveness', 'fair')
            if effectiveness == 'poor':
                recommendations.append({
                    'type': 'efficiency',
                    'priority': 'high',
                    'suggestion': 'Try a higher compression level or different algorithm for better space savings',
                    'expected_improvement': 'Better compression ratio'
                })
            
            # Quality recommendations
            quality_rating = analytics.get('quality', {}).get('quality_rating', 'fair')
            if quality_rating == 'poor':
                recommendations.append({
                    'type': 'quality',
                    'priority': 'high',
                    'suggestion': 'Consider using lossless compression to preserve data integrity',
                    'expected_improvement': 'Higher quality preservation'
                })
            
            # Content-specific recommendations
            if content_type == 'text' and compression_result.compression_ratio > 0.5:
                recommendations.append({
                    'type': 'content_specific',
                    'priority': 'medium',
                    'suggestion': 'Text content should compress much better. Try LZMA or check for binary data',
                    'expected_improvement': 'Much better compression ratio'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {str(e)}")
            return []
    
    async def decompress(
        self,
        compressed_data: bytes,
        algorithm: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Decompress data"""        try:
            start_time = asyncio.get_event_loop().time()
            
            compressor = self.compressors.get(algorithm)
            if not compressor:
                return {
                    'success': False,
                    'error': f"Decompressor for algorithm '{algorithm}' not available"
                }
            
            decompressed_data = await compressor.decompress(compressed_data)
            decompression_time = asyncio.get_event_loop().time() - start_time
            
            return {
                'success': True,
                'decompressed_data': decompressed_data,
                'decompression_time': decompression_time,
                'algorithm': algorithm
            }
            
        except Exception as e:
            self.logger.error(f"Decompression failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def batch_compress(
        self,
        data_items: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Compress multiple data items in batch"""        tasks = []
        
        for item in data_items:
            task = self.process(
                item.get('data'),
                item.get('content_type', 'generic'),
                item.get('algorithm'),
                config
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'item_index': i}
            for i, result in enumerate(results)
        ]

# Algorithm-specific compressor classes
class ZlibCompressor:
    """Zlib compression implementation"""    
    async def compress(self, data: bytes, level: int, config: Dict[str, Any]) -> bytes:
        return zlib.compress(data, level)
    
    async def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)

class GzipCompressor:
    """Gzip compression implementation"""    
    async def compress(self, data: bytes, level: int, config: Dict[str, Any]) -> bytes:
        return gzip.compress(data, compresslevel=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)

class Bz2Compressor:
    """Bzip2 compression implementation"""    
    async def compress(self, data: bytes, level: int, config: Dict[str, Any]) -> bytes:
        return bz2.compress(data, compresslevel=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return bz2.decompress(data)

class LzmaCompressor:
    """LZMA compression implementation"""    
    async def compress(self, data: bytes, level: int, config: Dict[str, Any]) -> bytes:
        return lzma.compress(data, preset=level)
    
    async def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)

class AdaptiveCompressor:
    """Adaptive compression that selects optimal algorithm automatically"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AdaptiveCompressor")
    
    async def compress_adaptive(
        self,
        data: bytes,
        content_type: str,
        target: str = 'balanced'
    ) -> CompressionResult:
        """Adaptively compress data using optimal algorithm"""        # Implementation would test multiple algorithms and select best
        # This is a placeholder for the actual adaptive logic
        pass
