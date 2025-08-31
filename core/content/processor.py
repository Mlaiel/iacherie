"""Content Processor - Multi-Format Content Processing Engine
==========================================================

The ContentProcessor handles the technical processing of various content formats
including audio, video, image, and text content according to the business
specifications for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import mimetypes
import hashlib
import io
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import uuid

import aiofiles
import aiofiles.os
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from scipy.io import wavfile
import librosa
import moviepy.editor as mp
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache.redis_client import RedisClient
from ..storage.file_manager import FileManager
from ..ml.audio_analysis import AudioAnalyzer
from ..ml.video_analysis import VideoAnalyzer
from ..ml.image_analysis import ImageAnalyzer
from ..ml.text_analysis import TextAnalyzer


@dataclass
class ProcessingResult:
    """Content processing result container"""    success: bool
    content_id: str
    processed_files: List[str]
    metadata: Dict[str, Any]
    fingerprint: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


@dataclass
class ProcessingConfig:
    """Content processing configuration"""    enable_thumbnails: bool = True
    enable_previews: bool = True
    enable_compression: bool = True
    enable_format_conversion: bool = True
    enable_quality_enhancement: bool = True
    enable_metadata_extraction: bool = True
    target_quality: float = 0.8
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    thumbnail_sizes: List[Tuple[int, int]] = None
    preview_duration: int = 30  # seconds for video/audio previews


class ContentProcessor:
    """    Multi-Format Content Processing Engine
    
    Handles processing of audio, video, image, and text content with
    advanced features like enhancement, compression, format conversion,
    and metadata extraction.
    
    Supported Formats:
    - Audio: MP3, WAV, FLAC, AAC, OGG, M4A
    - Video: MP4, AVI, MOV, WMV, FLV, MKV, WEBM
    - Image: JPG, PNG, GIF, BMP, TIFF, WEBP
    - Text: TXT, MD, DOC, DOCX, PDF, RTF
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: RedisClient,
        file_manager: FileManager = None,
        config: ProcessingConfig = None
    ):
        self.db = db_session
        self.redis = redis_client
        self.file_manager = file_manager or FileManager()
        self.config = config or ProcessingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.audio_analyzer = AudioAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.text_analyzer = TextAnalyzer()
        
        # Supported MIME types
        self.supported_types = {
            "audio": [
                "audio/mpeg", "audio/wav", "audio/flac", "audio/aac",
                "audio/ogg", "audio/mp4", "audio/x-m4a"
            ],
            "video": [
                "video/mp4", "video/avi", "video/quicktime", "video/x-msvideo",
                "video/x-flv", "video/x-matroska", "video/webm"
            ],
            "image": [
                "image/jpeg", "image/png", "image/gif", "image/bmp",
                "image/tiff", "image/webp"
            ],
            "text": [
                "text/plain", "text/markdown", "application/pdf",
                "application/msword", "application/rtf"
            ]
        }

    async def process_content(
        self,
        content_id: str,
        file_path: str,
        content_type: str,
        user_id: int,
        custom_config: ProcessingConfig = None
    ) -> ProcessingResult:
        """        Process content file according to type and configuration
        
        Args:
            content_id: Unique content identifier
            file_path: Path to the content file
            content_type: Type of content (audio, video, image, text)
            user_id: Owner user ID
            custom_config: Custom processing configuration
            
        Returns:
            ProcessingResult with operation status and metadata
        """        start_time = datetime.utcnow()
        config = custom_config or self.config
        
        try:
            self.logger.info(f"Processing content {content_id} of type {content_type}")
            
            # Validate file existence and accessibility
            if not await aiofiles.os.path.exists(file_path):
                return ProcessingResult(
                    success=False,
                    content_id=content_id,
                    processed_files=[],
                    metadata={},
                    error="File not found"
                )
            
            # Detect and validate MIME type
            mime_type, encoding = mimetypes.guess_type(file_path)
            if not self._validate_mime_type(mime_type, content_type):
                return ProcessingResult(
                    success=False,
                    content_id=content_id,
                    processed_files=[],
                    metadata={},
                    error=f"Invalid MIME type {mime_type} for content type {content_type}"
                )
            
            # Route to appropriate processor
            if content_type == "audio":
                result = await self._process_audio(content_id, file_path, config)
            elif content_type == "video":
                result = await self._process_video(content_id, file_path, config)
            elif content_type == "image":
                result = await self._process_image(content_id, file_path, config)
            elif content_type == "text":
                result = await self._process_text(content_id, file_path, config)
            else:
                return ProcessingResult(
                    success=False,
                    content_id=content_id,
                    processed_files=[],
                    metadata={},
                    error=f"Unsupported content type: {content_type}"
                )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Cache processing result
            await self._cache_processing_result(content_id, result)
            
            self.logger.info(f"Content {content_id} processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Processing failed for {content_id}: {str(e)}"
            self.logger.error(error_msg)
            
            return ProcessingResult(
                success=False,
                content_id=content_id,
                processed_files=[],
                metadata={},
                error=error_msg,
                processing_time=processing_time
            )

    async def _process_audio(
        self,
        content_id: str,
        file_path: str,
        config: ProcessingConfig
    ) -> ProcessingResult:
        """        Process audio content with analysis, enhancement, and format conversion
        
        Args:
            content_id: Content identifier
            file_path: Audio file path
            config: Processing configuration
            
        Returns:
            ProcessingResult for audio processing
        """        try:
            processed_files = []
            metadata = {}
            
            # Load audio file
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            
            # Extract basic metadata
            metadata.update({
                "duration": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
                "channels": 1 if len(audio_data.shape) == 1 else audio_data.shape[0],
                "file_size": (await aiofiles.os.path.getsize(file_path)),
                "format": Path(file_path).suffix.lower()
            })
            
            # Perform audio analysis
            if config.enable_metadata_extraction:
                analysis_result = await self.audio_analyzer.analyze_audio(file_path)
                metadata.update(analysis_result)
            
            # Generate audio fingerprint
            fingerprint = await self._generate_audio_fingerprint(audio_data, sample_rate)
            
            # Audio enhancement (if enabled)
            enhanced_audio = audio_data
            if config.enable_quality_enhancement:
                enhanced_audio = await self._enhance_audio(audio_data, sample_rate)
                
                # Save enhanced version
                enhanced_path = self._get_processed_file_path(content_id, "enhanced.wav")
                wavfile.write(enhanced_path, sample_rate, enhanced_audio)
                processed_files.append(enhanced_path)
            
            # Generate preview (first 30 seconds)
            if config.enable_previews:
                preview_duration = min(config.preview_duration, metadata["duration"])
                preview_samples = int(preview_duration * sample_rate)
                preview_audio = enhanced_audio[:preview_samples]
                
                preview_path = self._get_processed_file_path(content_id, "preview.wav")
                wavfile.write(preview_path, sample_rate, preview_audio)
                processed_files.append(preview_path)
            
            # Format conversion (if enabled)
            if config.enable_format_conversion:
                # Convert to standard formats
                for format_ext in [".mp3", ".flac"]:
                    if not file_path.endswith(format_ext):
                        converted_path = await self._convert_audio_format(
                            enhanced_audio, sample_rate, content_id, format_ext
                        )
                        processed_files.append(converted_path)
            
            # Generate waveform visualization
            waveform_path = await self._generate_waveform_image(
                enhanced_audio, sample_rate, content_id
            )
            processed_files.append(waveform_path)
            
            return ProcessingResult(
                success=True,
                content_id=content_id,
                processed_files=processed_files,
                metadata=metadata,
                fingerprint=fingerprint
            )
            
        except Exception as e:
            raise Exception(f"Audio processing failed: {str(e)}")

    async def _process_video(
        self,
        content_id: str,
        file_path: str,
        config: ProcessingConfig
    ) -> ProcessingResult:
        """        Process video content with analysis, thumbnail generation, and compression
        
        Args:
            content_id: Content identifier
            file_path: Video file path
            config: Processing configuration
            
        Returns:
            ProcessingResult for video processing
        """        try:
            processed_files = []
            metadata = {}
            
            # Load video file
            video = mp.VideoFileClip(file_path)
            
            # Extract basic metadata
            metadata.update({
                "duration": video.duration,
                "fps": video.fps,
                "width": video.w,
                "height": video.h,
                "file_size": await aiofiles.os.path.getsize(file_path),
                "format": Path(file_path).suffix.lower(),
                "aspect_ratio": video.w / video.h if video.h > 0 else 1.0
            })
            
            # Perform video analysis
            if config.enable_metadata_extraction:
                analysis_result = await self.video_analyzer.analyze_video(file_path)
                metadata.update(analysis_result)
            
            # Generate video fingerprint
            fingerprint = await self._generate_video_fingerprint(file_path)
            
            # Generate thumbnails
            if config.enable_thumbnails:
                thumbnail_times = [
                    video.duration * 0.1,  # 10%
                    video.duration * 0.5,  # 50% (middle)
                    video.duration * 0.9   # 90%
                ]
                
                for i, time_point in enumerate(thumbnail_times):
                    if time_point < video.duration:
                        thumbnail_path = self._get_processed_file_path(
                            content_id, f"thumbnail_{i+1}.jpg"
                        )
                        video.save_frame(thumbnail_path, t=time_point)
                        processed_files.append(thumbnail_path)
            
            # Generate preview clip
            if config.enable_previews:
                preview_duration = min(config.preview_duration, video.duration)
                preview_clip = video.subclip(0, preview_duration)
                
                preview_path = self._get_processed_file_path(content_id, "preview.mp4")
                preview_clip.write_videofile(
                    preview_path,
                    verbose=False,
                    logger=None,
                    temp_audiofile_path=f"/tmp/{content_id}_temp_audio.wav"
                )
                processed_files.append(preview_path)
                preview_clip.close()
            
            # Video compression (if enabled)
            if config.enable_compression:
                compressed_path = await self._compress_video(video, content_id, config)
                processed_files.append(compressed_path)
            
            # Extract keyframes for similarity matching
            keyframes_path = await self._extract_keyframes(video, content_id)
            processed_files.append(keyframes_path)
            
            video.close()
            
            return ProcessingResult(
                success=True,
                content_id=content_id,
                processed_files=processed_files,
                metadata=metadata,
                fingerprint=fingerprint
            )
            
        except Exception as e:
            raise Exception(f"Video processing failed: {str(e)}")

    async def _process_image(
        self,
        content_id: str,
        file_path: str,
        config: ProcessingConfig
    ) -> ProcessingResult:
        """        Process image content with analysis, enhancement, and format conversion
        
        Args:
            content_id: Content identifier
            file_path: Image file path
            config: Processing configuration
            
        Returns:
            ProcessingResult for image processing
        """        try:
            processed_files = []
            metadata = {}
            
            # Load image
            with Image.open(file_path) as img:
                # Extract basic metadata
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                    "file_size": await aiofiles.os.path.getsize(file_path),
                    "aspect_ratio": img.width / img.height if img.height > 0 else 1.0
                })
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    metadata["exif"] = {k: v for k, v in exif_data.items() if isinstance(v, (str, int, float))}
                
                # Perform image analysis
                if config.enable_metadata_extraction:
                    analysis_result = await self.image_analyzer.analyze_image(file_path)
                    metadata.update(analysis_result)
                
                # Generate image fingerprint
                fingerprint = await self._generate_image_fingerprint(img)
                
                # Image enhancement (if enabled)
                enhanced_img = img.copy()
                if config.enable_quality_enhancement:
                    enhanced_img = await self._enhance_image(img)
                    
                    enhanced_path = self._get_processed_file_path(content_id, "enhanced.png")
                    enhanced_img.save(enhanced_path, "PNG", optimize=True)
                    processed_files.append(enhanced_path)
                
                # Generate thumbnails
                if config.enable_thumbnails:
                    thumbnail_sizes = config.thumbnail_sizes or [(150, 150), (300, 300), (600, 600)]
                    
                    for i, (width, height) in enumerate(thumbnail_sizes):
                        thumbnail = enhanced_img.copy()
                        thumbnail.thumbnail((width, height), Image.Resampling.LANCZOS)
                        
                        thumbnail_path = self._get_processed_file_path(
                            content_id, f"thumbnail_{width}x{height}.jpg"
                        )
                        thumbnail.save(thumbnail_path, "JPEG", quality=85, optimize=True)
                        processed_files.append(thumbnail_path)
                
                # Format conversion (if enabled)
                if config.enable_format_conversion:
                    # Convert to web-optimized formats
                    for format_name, ext in [("WEBP", ".webp"), ("JPEG", ".jpg")]:
                        if not file_path.lower().endswith(ext):
                            converted_path = self._get_processed_file_path(content_id, f"optimized{ext}")
                            enhanced_img.save(converted_path, format_name, quality=85, optimize=True)
                            processed_files.append(converted_path)
                
                # Generate image analysis visualization
                if metadata.get("faces_detected", 0) > 0 or metadata.get("objects_detected", 0) > 0:
                    visualization_path = await self._generate_image_analysis_visualization(
                        enhanced_img, metadata, content_id
                    )
                    processed_files.append(visualization_path)
            
            return ProcessingResult(
                success=True,
                content_id=content_id,
                processed_files=processed_files,
                metadata=metadata,
                fingerprint=fingerprint
            )
            
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")

    async def _process_text(
        self,
        content_id: str,
        file_path: str,
        config: ProcessingConfig
    ) -> ProcessingResult:
        """        Process text content with analysis, extraction, and formatting
        
        Args:
            content_id: Content identifier
            file_path: Text file path
            config: Processing configuration
            
        Returns:
            ProcessingResult for text processing
        """        try:
            processed_files = []
            metadata = {}
            
            # Read text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Extract basic metadata
            metadata.update({
                "character_count": len(content),
                "word_count": len(content.split()),
                "line_count": content.count('\n') + 1,
                "file_size": await aiofiles.os.path.getsize(file_path),
                "encoding": "utf-8",
                "format": Path(file_path).suffix.lower()
            })
            
            # Perform text analysis
            if config.enable_metadata_extraction:
                analysis_result = await self.text_analyzer.analyze_text(content)
                metadata.update(analysis_result)
            
            # Generate text fingerprint
            fingerprint = await self._generate_text_fingerprint(content)
            
            # Extract and clean text
            cleaned_text = await self._clean_and_extract_text(content)
            
            # Save cleaned version
            cleaned_path = self._get_processed_file_path(content_id, "cleaned.txt")
            async with aiofiles.open(cleaned_path, 'w', encoding='utf-8') as f:
                await f.write(cleaned_text)
            processed_files.append(cleaned_path)
            
            # Generate summary (if text is long enough)
            if metadata["word_count"] > 100:
                summary = await self._generate_text_summary(cleaned_text)
                summary_path = self._get_processed_file_path(content_id, "summary.txt")
                async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
                    await f.write(summary)
                processed_files.append(summary_path)
            
            # Extract keywords and entities
            if config.enable_metadata_extraction:
                keywords_path = await self._extract_keywords_and_entities(
                    cleaned_text, content_id
                )
                processed_files.append(keywords_path)
            
            # Format conversion (if enabled)
            if config.enable_format_conversion:
                # Convert to different formats
                for format_name in ["markdown", "html"]:
                    formatted_content = await self._convert_text_format(
                        cleaned_text, format_name
                    )
                    formatted_path = self._get_processed_file_path(
                        content_id, f"formatted.{format_name[:2]}"
                    )
                    async with aiofiles.open(formatted_path, 'w', encoding='utf-8') as f:
                        await f.write(formatted_content)
                    processed_files.append(formatted_path)
            
            return ProcessingResult(
                success=True,
                content_id=content_id,
                processed_files=processed_files,
                metadata=metadata,
                fingerprint=fingerprint
            )
            
        except Exception as e:
            raise Exception(f"Text processing failed: {str(e)}")

    # Helper methods for processing operations

    def _validate_mime_type(self, mime_type: str, content_type: str) -> bool:
        """Validate MIME type against expected content type"""        if not mime_type:
            return False
        return mime_type in self.supported_types.get(content_type, [])

    def _get_processed_file_path(self, content_id: str, filename: str) -> str:
        """Generate path for processed file"""        processed_dir = f"/tmp/processed/{content_id}"
        Path(processed_dir).mkdir(parents=True, exist_ok=True)
        return f"{processed_dir}/{filename}"

    async def _generate_audio_fingerprint(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate audio fingerprint for similarity matching"""        # Simplified fingerprint generation - in production, use Chromaprint
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        fingerprint_hash = hashlib.sha256(mfcc.tobytes()).hexdigest()
        return fingerprint_hash

    async def _generate_video_fingerprint(self, file_path: str) -> str:
        """Generate video fingerprint for similarity matching"""        # Simplified fingerprint generation - in production, use perceptual hashing
        cap = cv2.VideoCapture(file_path)
        frames_hash = []
        
        # Sample frames at regular intervals
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(0, frame_count, max(1, frame_count // 10)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert to grayscale and resize
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (8, 8))
                frames_hash.append(resized.flatten())
        
        cap.release()
        
        if frames_hash:
            combined_hash = np.concatenate(frames_hash)
            fingerprint_hash = hashlib.sha256(combined_hash.tobytes()).hexdigest()
            return fingerprint_hash
        
        return hashlib.sha256(b"empty_video").hexdigest()

    async def _generate_image_fingerprint(self, img: Image.Image) -> str:
        """Generate image fingerprint for similarity matching"""        # Create perceptual hash
        resized = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        pixels = list(resized.getdata())
        avg = sum(pixels) / len(pixels)
        
        # Create binary hash
        hash_bits = []
        for pixel in pixels:
            hash_bits.append('1' if pixel > avg else '0')
        
        binary_string = ''.join(hash_bits)
        fingerprint_hash = hashlib.sha256(binary_string.encode()).hexdigest()
        return fingerprint_hash

    async def _generate_text_fingerprint(self, content: str) -> str:
        """Generate text fingerprint for similarity matching"""        # Normalize text for fingerprinting
        normalized = ' '.join(content.lower().split())
        fingerprint_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        return fingerprint_hash

    async def _enhance_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply audio enhancement algorithms"""        # Noise reduction (simplified)
        enhanced = audio_data.copy()
        
        # Normalize audio levels
        max_val = np.max(np.abs(enhanced))
        if max_val > 0:
            enhanced = enhanced / max_val * 0.8
        
        return enhanced

    async def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply image enhancement algorithms"""        enhanced = img.copy()
        
        # Auto contrast enhancement
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.2)
        
        # Sharpness enhancement
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.1)
        
        # Color enhancement
        if enhanced.mode in ['RGB', 'RGBA']:
            enhanced = ImageEnhance.Color(enhanced).enhance(1.1)
        
        return enhanced

    async def _cache_processing_result(self, content_id: str, result: ProcessingResult) -> None:
        """Cache processing result for quick retrieval"""        cache_data = {
            "success": result.success,
            "processed_files": result.processed_files,
            "metadata": result.metadata,
            "fingerprint": result.fingerprint,
            "processing_time": result.processing_time,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.set(
            f"processing_result:{content_id}",
            cache_data,
            expire=3600  # Cache for 1 hour
        )

    # Additional helper methods would be implemented here for:
    # - _convert_audio_format
    # - _generate_waveform_image
    # - _compress_video
    # - _extract_keyframes
    # - _generate_image_analysis_visualization
    # - _clean_and_extract_text
    # - _generate_text_summary
    # - _extract_keywords_and_entities
    # - _convert_text_format
