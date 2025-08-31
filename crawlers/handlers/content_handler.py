"""Content Handler Module
=====================

Professional content handling system for multi-format content processing.
Manages content extraction, validation, transformation, and preparation for fingerprinting.

Supported Content Types:
- Audio (MP3, WAV, FLAC, M4A, OGG)
- Video (MP4, AVI, MOV, MKV, WebM)
- Image (JPEG, PNG, GIF, WebP, TIFF)
- Text (TXT, MD, DOC, PDF, HTML)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""
import asyncio
import logging
import mimetypes
import os
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import magic
import cv2
import numpy as np
from PIL import Image, ExifTags
import librosa
import soundfile as sf
from pydub import AudioSegment
import textract
from bs4 import BeautifulSoup
import chardet
import aiofiles
import tempfile
from concurrent.futures import ThreadPoolExecutor

from backend.core.exceptions import (
    ContentProcessingError,
    UnsupportedContentTypeError,
    ContentValidationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.utils.file_utils import FileValidator, FileManager
from backend.utils.security_utils import SecurityScanner

logger = get_logger(__name__)


class ContentTypeDetector:
    """Professional content type detection and validation system."""
    
    SUPPORTED_FORMATS = {
        'audio': {
            'extensions': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'],
            'mime_types': [
                'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4',
                'audio/ogg', 'audio/aac', 'audio/x-ms-wma'
            ]
        },
        'video': {
            'extensions': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
            'mime_types': [
                'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
                'video/x-matroska', 'video/webm', 'video/x-flv', 'video/x-ms-wmv'
            ]
        },
        'image': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.bmp'],
            'mime_types': [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'image/tiff', 'image/bmp', 'image/x-icon'
            ]
        },
        'text': {
            'extensions': ['.txt', '.md', '.doc', '.docx', '.pdf', '.html', '.htm'],
            'mime_types': [
                'text/plain', 'text/markdown', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/pdf', 'text/html'
            ]
        }
    }
    
    def __init__(self):
        self.magic_mime = magic.Magic(mime=True)
        self.magic_desc = magic.Magic()
    
    def detect_content_type(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Detect content type with comprehensive analysis.
        
        Args:
            file_path: Path to the content file
            
        Returns:
            Tuple of (content_type, metadata)
        """
        try:
            # Get file information
            file_stat = os.stat(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            # MIME type detection
            mime_type = self.magic_mime.from_file(file_path)
            file_description = self.magic_desc.from_file(file_path)
            
            # Determine content type
            content_type = self._classify_content_type(file_ext, mime_type)
            
            metadata = {
                'file_path': file_path,
                'file_size': file_stat.st_size,
                'file_extension': file_ext,
                'mime_type': mime_type,
                'file_description': file_description,
                'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                'modified_at': datetime.fromtimestamp(file_stat.st_mtime),
                'md5_hash': self._calculate_md5(file_path)
            }
            
            # Type-specific metadata
            if content_type == 'audio':
                metadata.update(self._get_audio_metadata(file_path))
            elif content_type == 'video':
                metadata.update(self._get_video_metadata(file_path))
            elif content_type == 'image':
                metadata.update(self._get_image_metadata(file_path))
            elif content_type == 'text':
                metadata.update(self._get_text_metadata(file_path))
            
            return content_type, metadata
            
        except Exception as e:
            logger.error(f"Content type detection failed: {e}")
            raise ContentProcessingError(f"Failed to detect content type: {e}")
    
    def _classify_content_type(self, file_ext: str, mime_type: str) -> str:
        """Classify content type based on extension and MIME type."""
        for content_type, config in self.SUPPORTED_FORMATS.items():
            if (file_ext in config['extensions'] or 
                any(mime_type.startswith(mt) for mt in config['mime_types'])):
                return content_type
        
        raise UnsupportedContentTypeError(
            f"Unsupported content type: {file_ext}, {mime_type}"
        )
    
    def _calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract audio-specific metadata."""
        try:
            y, sr = librosa.load(file_path)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Audio segment for additional info
            audio = AudioSegment.from_file(file_path)
            
            return {
                'duration_seconds': duration,
                'sample_rate': sr,
                'channels': audio.channels,
                'bit_depth': audio.sample_width * 8,
                'frame_rate': audio.frame_rate,
                'tempo': librosa.tempo(y=y, sr=sr)[0],
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y)))
            }
        except Exception as e:
            logger.warning(f"Audio metadata extraction failed: {e}")
            return {'duration_seconds': 0}
    
    def _get_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract video-specific metadata."""
        try:
            cap = cv2.VideoCapture(file_path)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'duration_seconds': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'resolution': f"{width}x{height}",
                'aspect_ratio': width / height if height > 0 else 0
            }
        except Exception as e:
            logger.warning(f"Video metadata extraction failed: {e}")
            return {'duration_seconds': 0}
    
    def _get_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image-specific metadata."""
        try:
            with Image.open(file_path) as img:
                metadata = {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'resolution': f"{img.width}x{img.height}",
                    'aspect_ratio': img.width / img.height if img.height > 0 else 0
                }
                
                # EXIF data
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        exif_data = {}
                        for tag, value in exif.items():
                            tag_name = ExifTags.TAGS.get(tag, tag)
                            exif_data[tag_name] = str(value)
                        metadata['exif'] = exif_data
                
                return metadata
                
        except Exception as e:
            logger.warning(f"Image metadata extraction failed: {e}")
            return {'width': 0, 'height': 0}
    
    def _get_text_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract text-specific metadata."""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result.get('encoding', 'utf-8')
            
            # Extract text
            if file_path.endswith('.pdf'):
                text = textract.process(file_path).decode('utf-8')
            elif file_path.endswith(('.html', '.htm')):
                with open(file_path, 'r', encoding=encoding) as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text = soup.get_text()
            else:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
            
            words = len(text.split())
            lines = len(text.splitlines())
            
            return {
                'encoding': encoding,
                'character_count': len(text),
                'word_count': words,
                'line_count': lines,
                'language_confidence': encoding_result.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.warning(f"Text metadata extraction failed: {e}")
            return {'character_count': 0}


class ContentProcessor:
    """Professional content processing system with industry-grade capabilities."""
    
    def __init__(self):
        self.detector = ContentTypeDetector()
        self.file_validator = FileValidator()
        self.file_manager = FileManager()
        self.security_scanner = SecurityScanner()
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKER_THREADS)
    
    async def process_content(
        self,
        content_data: Union[str, bytes],
        filename: str,
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process content with comprehensive validation and preparation.
        
        Args:
            content_data: Raw content data or file path
            filename: Original filename
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Processed content information
        """
        try:
            # Security validation
            await self._validate_security(content_data, filename)
            
            # Save content temporarily
            temp_file_path = await self._save_temporary_file(content_data, filename)
            
            try:
                # Content type detection
                content_type, content_metadata = self.detector.detect_content_type(temp_file_path)
                
                # Process based on content type
                processed_data = await self._process_by_type(
                    temp_file_path, content_type, content_metadata
                )
                
                # Prepare for fingerprinting
                fingerprint_ready = await self._prepare_for_fingerprinting(
                    temp_file_path, content_type, processed_data
                )
                
                # Create final result
                result = {
                    'user_id': user_id,
                    'original_filename': filename,
                    'content_type': content_type,
                    'metadata': content_metadata,
                    'processed_data': processed_data,
                    'fingerprint_ready': fingerprint_ready,
                    'processing_timestamp': datetime.utcnow().isoformat(),
                    'temp_file_path': temp_file_path
                }
                
                if metadata:
                    result['additional_metadata'] = metadata
                
                logger.info(f"Content processed successfully: {filename}")
                return result
                
            finally:
                # Cleanup handled by calling code
                pass
                
        except Exception as e:
            logger.error(f"Content processing failed: {e}")
            raise ContentProcessingError(f"Failed to process content: {e}")
    
    async def _validate_security(self, content_data: Union[str, bytes], filename: str):
        """Validate content security and safety."""
        try:
            # File extension validation
            if not self.file_validator.is_allowed_extension(filename):
                raise ContentValidationError(f"File extension not allowed: {filename}")
            
            # Size validation
            if isinstance(content_data, bytes):
                if len(content_data) > settings.MAX_FILE_SIZE:
                    raise ContentValidationError("File size exceeds maximum limit")
            
            # Malware scanning would be implemented here
            # await self.security_scanner.scan_content(content_data)
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            raise
    
    async def _save_temporary_file(
        self, 
        content_data: Union[str, bytes], 
        filename: str
    ) -> str:
        """Save content to temporary file for processing."""
        try:
            # Generate unique temporary filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = hashlib.md5(filename.encode()).hexdigest()[:8]
            temp_filename = f"{timestamp}_{unique_id}_{filename}"
            
            temp_dir = Path(settings.TEMP_DIRECTORY)
            temp_dir.mkdir(exist_ok=True)
            temp_file_path = temp_dir / temp_filename
            
            if isinstance(content_data, str):
                # Assume it's a file path
                async with aiofiles.open(content_data, 'rb') as src:
                    content = await src.read()
                async with aiofiles.open(temp_file_path, 'wb') as dst:
                    await dst.write(content)
            else:
                # Raw bytes
                async with aiofiles.open(temp_file_path, 'wb') as f:
                    await f.write(content_data)
            
            return str(temp_file_path)
            
        except Exception as e:
            logger.error(f"Temporary file creation failed: {e}")
            raise ContentProcessingError(f"Failed to create temporary file: {e}")
    
    async def _process_by_type(
        self, 
        file_path: str, 
        content_type: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process content based on its type."""
        try:
            if content_type == 'audio':
                return await self._process_audio(file_path, metadata)
            elif content_type == 'video':
                return await self._process_video(file_path, metadata)
            elif content_type == 'image':
                return await self._process_image(file_path, metadata)
            elif content_type == 'text':
                return await self._process_text(file_path, metadata)
            else:
                raise UnsupportedContentTypeError(f"Unknown content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Type-specific processing failed: {e}")
            raise ContentProcessingError(f"Failed to process {content_type}: {e}")
    
    async def _process_audio(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio content for fingerprinting."""
        loop = asyncio.get_event_loop()
        
        def extract_features():
            y, sr = librosa.load(file_path)
            
            # Extract features for fingerprinting
            features = {
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).tolist(),
                'chroma': librosa.feature.chroma(y=y, sr=sr).tolist(),
                'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr).tolist(),
                'tonnetz': librosa.feature.tonnetz(y=y, sr=sr).tolist(),
                'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr).tolist()
            }
            
            return {
                'audio_features': features,
                'waveform_shape': y.shape,
                'sample_rate': sr,
                'processing_method': 'librosa_extraction'
            }
        
        return await loop.run_in_executor(self.executor, extract_features)
    
    async def _process_video(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process video content for fingerprinting."""
        loop = asyncio.get_event_loop()
        
        def extract_frames():
            cap = cv2.VideoCapture(file_path)
            
            # Extract key frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Sample frames at regular intervals
            sample_interval = max(1, frame_count // 10)  # 10 sample frames
            frames = []
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Convert to RGB and resize for processing
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (224, 224))
                    frames.append(frame_resized.tolist())
            
            cap.release()
            
            return {
                'sample_frames': frames,
                'frame_extraction_method': 'uniform_sampling',
                'total_frames': frame_count,
                'sample_count': len(frames)
            }
        
        return await loop.run_in_executor(self.executor, extract_frames)
    
    async def _process_image(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process image content for fingerprinting."""
        loop = asyncio.get_event_loop()
        
        def extract_image_features():
            img = cv2.imread(file_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize for consistent processing
            img_resized = cv2.resize(img_rgb, (224, 224))
            
            # Extract basic features
            hist_r = cv2.calcHist([img_resized], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_resized], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_resized], [2], None, [256], [0, 256])
            
            return {
                'image_array': img_resized.tolist(),
                'color_histogram': {
                    'red': hist_r.flatten().tolist(),
                    'green': hist_g.flatten().tolist(),
                    'blue': hist_b.flatten().tolist()
                },
                'processing_method': 'opencv_extraction'
            }
        
        return await loop.run_in_executor(self.executor, extract_image_features)
    
    async def _process_text(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text content for fingerprinting."""
        try:
            # Read text content
            encoding = metadata.get('encoding', 'utf-8')
            
            if file_path.endswith('.pdf'):
                text = textract.process(file_path).decode('utf-8')
            elif file_path.endswith(('.html', '.htm')):
                with open(file_path, 'r', encoding=encoding) as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text = soup.get_text()
            else:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
            
            # Extract features for fingerprinting
            words = text.split()
            sentences = text.split('.')
            
            # Character n-grams for similarity
            char_3grams = [text[i:i+3] for i in range(len(text)-2)]
            word_2grams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            
            return {
                'full_text': text,
                'text_features': {
                    'character_3grams': char_3grams[:1000],  # Limit for performance
                    'word_2grams': word_2grams[:500],
                    'word_count': len(words),
                    'sentence_count': len(sentences),
                    'unique_words': len(set(words))
                },
                'processing_method': 'ngram_extraction'
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            raise ContentProcessingError(f"Failed to process text: {e}")
    
    async def _prepare_for_fingerprinting(
        self, 
        file_path: str, 
        content_type: str, 
        processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare processed content for fingerprinting systems."""
        try:
            fingerprint_data = {
                'content_type': content_type,
                'file_path': file_path,
                'fingerprint_ready': True,
                'preparation_timestamp': datetime.utcnow().isoformat()
            }
            
            # Add type-specific fingerprint preparation
            if content_type == 'audio':
                fingerprint_data['audio_fingerprint_data'] = {
                    'features': processed_data.get('audio_features', {}),
                    'chromaprint_ready': True
                }
            elif content_type == 'video':
                fingerprint_data['video_fingerprint_data'] = {
                    'frames': processed_data.get('sample_frames', []),
                    'frame_hashing_ready': True
                }
            elif content_type == 'image':
                fingerprint_data['image_fingerprint_data'] = {
                    'image_array': processed_data.get('image_array', []),
                    'perceptual_hash_ready': True
                }
            elif content_type == 'text':
                fingerprint_data['text_fingerprint_data'] = {
                    'text_features': processed_data.get('text_features', {}),
                    'vector_embedding_ready': True
                }
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Fingerprint preparation failed: {e}")
            raise ContentProcessingError(f"Failed to prepare for fingerprinting: {e}")
    
    async def cleanup_temporary_file(self, file_path: str):
        """Clean up temporary files after processing."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temporary file cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {e}")


class ContentHandler:
    """Main content handler orchestrating all content processing operations."""
    
    def __init__(self):
        self.processor = ContentProcessor()
        logger.info("Content Handler initialized successfully")
    
    async def handle_content(
        self,
        content_data: Union[str, bytes],
        filename: str,
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for content handling.
        
        Args:
            content_data: Raw content data or file path
            filename: Original filename
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Complete processing result
        """
        try:
            logger.info(f"Processing content: {filename} for user {user_id}")
            
            # Process content
            result = await self.processor.process_content(
                content_data, filename, user_id, metadata
            )
            
            logger.info(f"Content handling completed successfully: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Content handling failed for {filename}: {e}")
            raise
    
    async def cleanup_content(self, file_path: str):
        """Clean up processed content."""
        await self.processor.cleanup_temporary_file(file_path)


# Factory function for easy instantiation
def create_content_handler() -> ContentHandler:
    """Create and return a ContentHandler instance."""
    return ContentHandler()
