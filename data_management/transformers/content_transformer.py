"""
Advanced Multi-Format Data Transformers
Professional Industrial Content Processing Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Tuple, Any
from enum import Enum
from abc import ABC, abstractmethod
import cv2
import librosa
from PIL import Image
import io
import base64

from backend.core.database import get_database
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.utils.media import MediaProcessor
from backend.utils.storage import CloudStorageManager

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Content transformation types"""
    AUDIO_FORMAT = "audio_format"
    AUDIO_QUALITY = "audio_quality"
    AUDIO_EFFECTS = "audio_effects"
    IMAGE_FORMAT = "image_format"
    IMAGE_RESIZE = "image_resize"
    IMAGE_ENHANCEMENT = "image_enhancement"
    VIDEO_FORMAT = "video_format"
    VIDEO_COMPRESSION = "video_compression"
    VIDEO_EXTRACTION = "video_extraction"
    TEXT_CLEANUP = "text_cleanup"
    TEXT_TRANSLATION = "text_translation"
    TEXT_SUMMARIZATION = "text_summarization"
    METADATA_EXTRACTION = "metadata_extraction"
    METADATA_ENRICHMENT = "metadata_enrichment"
    DATA_NORMALIZATION = "data_normalization"


class QualityLevel(Enum):
    """Content quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"


class ContentTransformer(ABC):
    """Abstract base class for content transformers"""
    
    @abstractmethod
    async def transform(
        self,
        input_data: bytes,
        source_format: str,
        target_format: str,
        options: Dict[str, Any]
    ) -> bytes:
        """Transform content from source to target format"""
        pass
    
    @abstractmethod
    def supports_transformation(
        self,
        source_format: str,
        target_format: str
    ) -> bool:
        """Check if transformation is supported"""
        pass


class MultiFormatTransformer:
    """Advanced multi-format content transformation engine"""
    
    def __init__(self):
        self.db = get_database()
        self.security = SecurityManager()
        self.media_processor = MediaProcessor()
        self.storage = CloudStorageManager()
        
        # Transformation configurations
        self.audio_formats = {
            'mp3': {'quality': [128, 192, 256, 320], 'lossy': True},
            'wav': {'quality': [16, 24, 32], 'lossy': False},
            'flac': {'quality': [16, 24], 'lossy': False},
            'aac': {'quality': [128, 192, 256], 'lossy': True},
            'ogg': {'quality': [128, 192, 256], 'lossy': True},
            'm4a': {'quality': [128, 192, 256], 'lossy': True}
        }
        
        self.image_formats = {
            'jpeg': {'quality': [60, 80, 90, 95, 100], 'lossy': True},
            'png': {'compression': [0, 1, 6, 9], 'lossy': False},
            'webp': {'quality': [70, 80, 90, 100], 'lossy': True},
            'tiff': {'compression': ['none', 'lzw', 'zip'], 'lossy': False},
            'bmp': {'compression': ['none'], 'lossy': False}
        }
        
        self.video_formats = {
            'mp4': {'codecs': ['h264', 'h265'], 'quality': ['480p', '720p', '1080p', '4k']},
            'avi': {'codecs': ['xvid', 'h264'], 'quality': ['480p', '720p', '1080p']},
            'mov': {'codecs': ['h264', 'prores'], 'quality': ['720p', '1080p', '4k']},
            'webm': {'codecs': ['vp8', 'vp9'], 'quality': ['480p', '720p', '1080p']},
            'mkv': {'codecs': ['h264', 'h265'], 'quality': ['480p', '720p', '1080p', '4k']}
        }
        
        # Initialize transformers
        self.transformers = {
            'audio': AudioTransformer(),
            'image': ImageTransformer(),
            'video': VideoTransformer(),
            'text': TextTransformer(),
            'metadata': MetadataTransformer()
        }

    async def transform_content(
        self,
        content_id: str,
        user_id: str,
        transformation_type: TransformationType,
        source_data: Union[bytes, str, Dict],
        target_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform content with specified configuration"""
        try:
            logger.info(f"Transforming content {content_id} with type {transformation_type.value}")
            
            # Validate transformation request
            await self._validate_transformation_request(
                transformation_type,
                source_data,
                target_config,
                user_id
            )
            
            # Determine content type and transformer
            content_type = self._determine_content_type(transformation_type)
            transformer = self.transformers[content_type]
            
            # Perform transformation
            result = await self._execute_transformation(
                transformer,
                transformation_type,
                source_data,
                target_config
            )
            
            # Store transformation record
            transformation_record = await self._create_transformation_record(
                content_id,
                user_id,
                transformation_type,
                target_config,
                result
            )
            
            return {
                'transformation_id': transformation_record['id'],
                'content_id': content_id,
                'transformation_type': transformation_type.value,
                'status': 'completed',
                'output_data': result['output_data'],
                'metadata': result['metadata'],
                'created_at': transformation_record['created_at']
            }
            
        except Exception as e:
            logger.error(f"Error transforming content {content_id}: {str(e)}")
            raise ProcessingError(f"Content transformation failed: {str(e)}")

    async def _validate_transformation_request(
        self,
        transformation_type: TransformationType,
        source_data: Union[bytes, str, Dict],
        target_config: Dict[str, Any],
        user_id: str
    ) -> None:
        """Validate transformation request"""
        if not source_data:
            raise ValidationError("Source data cannot be empty")
        
        if not target_config:
            raise ValidationError("Target configuration is required")
        
        # Check user permissions
        if not await self.security.check_transformation_permission(user_id, transformation_type):
            raise ValidationError("User does not have permission for this transformation")
        
        # Validate configuration based on transformation type
        if transformation_type in [
            TransformationType.AUDIO_FORMAT,
            TransformationType.AUDIO_QUALITY,
            TransformationType.AUDIO_EFFECTS
        ]:
            await self._validate_audio_config(target_config)
        elif transformation_type in [
            TransformationType.IMAGE_FORMAT,
            TransformationType.IMAGE_RESIZE,
            TransformationType.IMAGE_ENHANCEMENT
        ]:
            await self._validate_image_config(target_config)
        elif transformation_type in [
            TransformationType.VIDEO_FORMAT,
            TransformationType.VIDEO_COMPRESSION,
            TransformationType.VIDEO_EXTRACTION
        ]:
            await self._validate_video_config(target_config)

    async def _validate_audio_config(self, config: Dict[str, Any]) -> None:
        """Validate audio transformation configuration"""
        required_fields = ['target_format']
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Required field '{field}' missing from audio config")
        
        target_format = config['target_format'].lower()
        if target_format not in self.audio_formats:
            raise ValidationError(f"Unsupported audio format: {target_format}")
        
        if 'quality' in config:
            format_info = self.audio_formats[target_format]
            if config['quality'] not in format_info['quality']:
                raise ValidationError(f"Invalid quality for {target_format}: {config['quality']}")

    async def _validate_image_config(self, config: Dict[str, Any]) -> None:
        """Validate image transformation configuration"""
        required_fields = ['target_format']
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Required field '{field}' missing from image config")
        
        target_format = config['target_format'].lower()
        if target_format not in self.image_formats:
            raise ValidationError(f"Unsupported image format: {target_format}")

    async def _validate_video_config(self, config: Dict[str, Any]) -> None:
        """Validate video transformation configuration"""
        required_fields = ['target_format']
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Required field '{field}' missing from video config")
        
        target_format = config['target_format'].lower()
        if target_format not in self.video_formats:
            raise ValidationError(f"Unsupported video format: {target_format}")

    def _determine_content_type(self, transformation_type: TransformationType) -> str:
        """Determine content type from transformation type"""
        type_mapping = {
            TransformationType.AUDIO_FORMAT: 'audio',
            TransformationType.AUDIO_QUALITY: 'audio',
            TransformationType.AUDIO_EFFECTS: 'audio',
            TransformationType.IMAGE_FORMAT: 'image',
            TransformationType.IMAGE_RESIZE: 'image',
            TransformationType.IMAGE_ENHANCEMENT: 'image',
            TransformationType.VIDEO_FORMAT: 'video',
            TransformationType.VIDEO_COMPRESSION: 'video',
            TransformationType.VIDEO_EXTRACTION: 'video',
            TransformationType.TEXT_CLEANUP: 'text',
            TransformationType.TEXT_TRANSLATION: 'text',
            TransformationType.TEXT_SUMMARIZATION: 'text',
            TransformationType.METADATA_EXTRACTION: 'metadata',
            TransformationType.METADATA_ENRICHMENT: 'metadata',
            TransformationType.DATA_NORMALIZATION: 'metadata'
        }
        
        return type_mapping.get(transformation_type, 'metadata')

    async def _execute_transformation(
        self,
        transformer: ContentTransformer,
        transformation_type: TransformationType,
        source_data: Union[bytes, str, Dict],
        target_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual transformation"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Prepare transformation parameters
            transform_params = {
                'transformation_type': transformation_type,
                'config': target_config,
                'start_time': start_time
            }
            
            # Execute transformation based on type
            if isinstance(transformer, AudioTransformer):
                result = await transformer.transform_audio(source_data, transform_params)
            elif isinstance(transformer, ImageTransformer):
                result = await transformer.transform_image(source_data, transform_params)
            elif isinstance(transformer, VideoTransformer):
                result = await transformer.transform_video(source_data, transform_params)
            elif isinstance(transformer, TextTransformer):
                result = await transformer.transform_text(source_data, transform_params)
            elif isinstance(transformer, MetadataTransformer):
                result = await transformer.transform_metadata(source_data, transform_params)
            else:
                raise ProcessingError(f"Unknown transformer type: {type(transformer)}")
            
            # Calculate processing metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            result['metadata']['processing_time_seconds'] = processing_time
            result['metadata']['processed_at'] = end_time.isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Transformation execution failed: {str(e)}")
            raise ProcessingError(f"Transformation failed: {str(e)}")

    async def _create_transformation_record(
        self,
        content_id: str,
        user_id: str,
        transformation_type: TransformationType,
        config: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create transformation record in database"""
        try:
            query = """
            INSERT INTO content_transformations (
                id, content_id, user_id, transformation_type,
                source_config, target_config, result_metadata,
                status, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, NOW(), NOW()
            ) RETURNING id, created_at
            """
            
            row = await self.db.fetchrow(
                query,
                content_id,
                user_id,
                transformation_type.value,
                json.dumps({}),  # source_config would come from input analysis
                json.dumps(config),
                json.dumps(result['metadata']),
                'completed'
            )
            
            return {
                'id': str(row['id']),
                'created_at': row['created_at'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating transformation record: {str(e)}")
            raise ProcessingError(f"Record creation failed: {str(e)}")

    async def batch_transform(
        self,
        transformations: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute multiple transformations in batch"""
        try:
            logger.info(f"Executing batch transformation for user {user_id}")
            
            results = []
            
            # Process transformations in parallel with limit
            semaphore = asyncio.Semaphore(5)  # Limit concurrent transformations
            
            async def process_single(transformation):
                async with semaphore:
                    return await self.transform_content(
                        transformation['content_id'],
                        user_id,
                        TransformationType(transformation['transformation_type']),
                        transformation['source_data'],
                        transformation['target_config']
                    )
            
            tasks = [process_single(t) for t in transformations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'content_id': transformations[i]['content_id'],
                        'status': 'failed',
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch transformation: {str(e)}")
            raise ProcessingError(f"Batch transformation failed: {str(e)}")

    async def get_transformation_history(
        self,
        content_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get transformation history"""
        try:
            conditions = []
            params = []
            param_count = 0
            
            if content_id:
                param_count += 1
                conditions.append(f"content_id = ${param_count}")
                params.append(content_id)
            
            if user_id:
                param_count += 1
                conditions.append(f"user_id = ${param_count}")
                params.append(user_id)
            
            param_count += 1
            params.append(limit)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
            SELECT id, content_id, user_id, transformation_type,
                   target_config, result_metadata, status,
                   created_at, updated_at
            FROM content_transformations
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count}
            """
            
            rows = await self.db.fetch(query, *params)
            
            transformations = []
            for row in rows:
                transformations.append({
                    'id': str(row['id']),
                    'content_id': row['content_id'],
                    'user_id': row['user_id'],
                    'transformation_type': row['transformation_type'],
                    'target_config': json.loads(row['target_config']),
                    'result_metadata': json.loads(row['result_metadata']),
                    'status': row['status'],
                    'created_at': row['created_at'].isoformat(),
                    'updated_at': row['updated_at'].isoformat()
                })
            
            return transformations
            
        except Exception as e:
            logger.error(f"Error getting transformation history: {str(e)}")
            raise ProcessingError(f"History retrieval failed: {str(e)}")


class AudioTransformer(ContentTransformer):
    """Advanced audio content transformer"""
    
    async def transform_audio(
        self,
        source_data: bytes,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform audio content"""
        try:
            config = params['config']
            transformation_type = params['transformation_type']
            
            # Load audio data
            audio_buffer = io.BytesIO(source_data)
            y, sr = librosa.load(audio_buffer, sr=None)
            
            # Apply transformation based on type
            if transformation_type == TransformationType.AUDIO_FORMAT:
                result_data = await self._convert_audio_format(y, sr, config)
            elif transformation_type == TransformationType.AUDIO_QUALITY:
                result_data = await self._adjust_audio_quality(y, sr, config)
            elif transformation_type == TransformationType.AUDIO_EFFECTS:
                result_data = await self._apply_audio_effects(y, sr, config)
            else:
                raise ProcessingError(f"Unsupported audio transformation: {transformation_type}")
            
            return {
                'output_data': result_data,
                'metadata': {
                    'original_sample_rate': int(sr),
                    'original_duration': float(len(y) / sr),
                    'target_format': config.get('target_format'),
                    'transformation_type': transformation_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Audio transformation error: {str(e)}")
            raise ProcessingError(f"Audio transformation failed: {str(e)}")

    async def _convert_audio_format(
        self,
        y: np.ndarray,
        sr: int,
        config: Dict[str, Any]
    ) -> bytes:
        """Convert audio to different format"""
        # This would use libraries like pydub or ffmpeg
        # For now, return a placeholder
        return b"converted_audio_data"

    async def _adjust_audio_quality(
        self,
        y: np.ndarray,
        sr: int,
        config: Dict[str, Any]
    ) -> bytes:
        """Adjust audio quality/bitrate"""
        # Implementation for quality adjustment
        return b"quality_adjusted_audio_data"

    async def _apply_audio_effects(
        self,
        y: np.ndarray,
        sr: int,
        config: Dict[str, Any]
    ) -> bytes:
        """Apply audio effects"""
        effects = config.get('effects', [])
        
        for effect in effects:
            if effect['type'] == 'normalize':
                y = librosa.util.normalize(y)
            elif effect['type'] == 'amplify':
                gain = effect.get('gain', 1.0)
                y = y * gain
            elif effect['type'] == 'eq':
                # Apply EQ (simplified)
                pass
        
        return b"processed_audio_data"

    def supports_transformation(self, source_format: str, target_format: str) -> bool:
        """Check if audio transformation is supported"""
        supported_formats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        return source_format.lower() in supported_formats and target_format.lower() in supported_formats


class ImageTransformer(ContentTransformer):
    """Advanced image content transformer"""
    
    async def transform_image(
        self,
        source_data: bytes,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform image content"""
        try:
            config = params['config']
            transformation_type = params['transformation_type']
            
            # Load image data
            image = Image.open(io.BytesIO(source_data))
            
            # Apply transformation based on type
            if transformation_type == TransformationType.IMAGE_FORMAT:
                result_data = await self._convert_image_format(image, config)
            elif transformation_type == TransformationType.IMAGE_RESIZE:
                result_data = await self._resize_image(image, config)
            elif transformation_type == TransformationType.IMAGE_ENHANCEMENT:
                result_data = await self._enhance_image(image, config)
            else:
                raise ProcessingError(f"Unsupported image transformation: {transformation_type}")
            
            return {
                'output_data': result_data,
                'metadata': {
                    'original_size': list(image.size),
                    'original_format': image.format,
                    'original_mode': image.mode,
                    'target_format': config.get('target_format'),
                    'transformation_type': transformation_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Image transformation error: {str(e)}")
            raise ProcessingError(f"Image transformation failed: {str(e)}")

    async def _convert_image_format(
        self,
        image: Image.Image,
        config: Dict[str, Any]
    ) -> bytes:
        """Convert image to different format"""
        target_format = config['target_format'].upper()
        quality = config.get('quality', 90)
        
        output_buffer = io.BytesIO()
        
        if target_format == 'JPEG':
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            image.save(output_buffer, format=target_format, quality=quality, optimize=True)
        elif target_format == 'PNG':
            image.save(output_buffer, format=target_format, optimize=True)
        elif target_format == 'WEBP':
            image.save(output_buffer, format=target_format, quality=quality, optimize=True)
        else:
            image.save(output_buffer, format=target_format)
        
        return output_buffer.getvalue()

    async def _resize_image(
        self,
        image: Image.Image,
        config: Dict[str, Any]
    ) -> bytes:
        """Resize image"""
        if 'width' in config and 'height' in config:
            new_size = (config['width'], config['height'])
        elif 'scale' in config:
            scale = config['scale']
            new_size = (int(image.width * scale), int(image.height * scale))
        else:
            raise ValidationError("Resize requires width/height or scale parameter")
        
        resample = getattr(Image, config.get('resample', 'LANCZOS'))
        resized_image = image.resize(new_size, resample)
        
        output_buffer = io.BytesIO()
        format_type = config.get('format', image.format or 'PNG')
        resized_image.save(output_buffer, format=format_type)
        
        return output_buffer.getvalue()

    async def _enhance_image(
        self,
        image: Image.Image,
        config: Dict[str, Any]
    ) -> bytes:
        """Enhance image quality"""
        from PIL import ImageEnhance
        
        enhanced_image = image.copy()
        
        # Apply enhancements
        if 'brightness' in config:
            enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = enhancer.enhance(config['brightness'])
        
        if 'contrast' in config:
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(config['contrast'])
        
        if 'saturation' in config:
            enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = enhancer.enhance(config['saturation'])
        
        if 'sharpness' in config:
            enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = enhancer.enhance(config['sharpness'])
        
        output_buffer = io.BytesIO()
        format_type = config.get('format', image.format or 'PNG')
        enhanced_image.save(output_buffer, format=format_type)
        
        return output_buffer.getvalue()

    def supports_transformation(self, source_format: str, target_format: str) -> bool:
        """Check if image transformation is supported"""
        supported_formats = ['jpeg', 'jpg', 'png', 'webp', 'tiff', 'bmp', 'gif']
        return source_format.lower() in supported_formats and target_format.lower() in supported_formats


class VideoTransformer(ContentTransformer):
    """Advanced video content transformer"""
    
    async def transform_video(
        self,
        source_data: bytes,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform video content"""
        try:
            config = params['config']
            transformation_type = params['transformation_type']
            
            # For video processing, we'd typically use ffmpeg
            # This is a simplified implementation
            
            if transformation_type == TransformationType.VIDEO_FORMAT:
                result_data = await self._convert_video_format(source_data, config)
            elif transformation_type == TransformationType.VIDEO_COMPRESSION:
                result_data = await self._compress_video(source_data, config)
            elif transformation_type == TransformationType.VIDEO_EXTRACTION:
                result_data = await self._extract_video_frames(source_data, config)
            else:
                raise ProcessingError(f"Unsupported video transformation: {transformation_type}")
            
            return {
                'output_data': result_data,
                'metadata': {
                    'target_format': config.get('target_format'),
                    'transformation_type': transformation_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Video transformation error: {str(e)}")
            raise ProcessingError(f"Video transformation failed: {str(e)}")

    async def _convert_video_format(self, source_data: bytes, config: Dict) -> bytes:
        """Convert video format"""
        # This would use ffmpeg via subprocess or python-ffmpeg
        return b"converted_video_data"

    async def _compress_video(self, source_data: bytes, config: Dict) -> bytes:
        """Compress video"""
        return b"compressed_video_data"

    async def _extract_video_frames(self, source_data: bytes, config: Dict) -> bytes:
        """Extract frames from video"""
        return b"extracted_frames_data"

    def supports_transformation(self, source_format: str, target_format: str) -> bool:
        """Check if video transformation is supported"""
        supported_formats = ['mp4', 'avi', 'mov', 'webm', 'mkv', 'flv']
        return source_format.lower() in supported_formats and target_format.lower() in supported_formats


class TextTransformer(ContentTransformer):
    """Advanced text content transformer"""
    
    async def transform_text(
        self,
        source_data: Union[str, bytes],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform text content"""
        try:
            config = params['config']
            transformation_type = params['transformation_type']
            
            # Convert bytes to string if needed
            if isinstance(source_data, bytes):
                text = source_data.decode('utf-8')
            else:
                text = source_data
            
            # Apply transformation based on type
            if transformation_type == TransformationType.TEXT_CLEANUP:
                result_text = await self._cleanup_text(text, config)
            elif transformation_type == TransformationType.TEXT_TRANSLATION:
                result_text = await self._translate_text(text, config)
            elif transformation_type == TransformationType.TEXT_SUMMARIZATION:
                result_text = await self._summarize_text(text, config)
            else:
                raise ProcessingError(f"Unsupported text transformation: {transformation_type}")
            
            return {
                'output_data': result_text.encode('utf-8'),
                'metadata': {
                    'original_length': len(text),
                    'result_length': len(result_text),
                    'transformation_type': transformation_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Text transformation error: {str(e)}")
            raise ProcessingError(f"Text transformation failed: {str(e)}")

    async def _cleanup_text(self, text: str, config: Dict) -> str:
        """Clean up text content"""
        import re
        
        cleaned_text = text
        
        # Remove extra whitespace
        if config.get('remove_extra_whitespace', True):
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove special characters
        if config.get('remove_special_chars', False):
            cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
        
        # Convert to lowercase
        if config.get('lowercase', False):
            cleaned_text = cleaned_text.lower()
        
        return cleaned_text.strip()

    async def _translate_text(self, text: str, config: Dict) -> str:
        """Translate text to target language"""
        # This would integrate with translation service
        target_language = config.get('target_language', 'en')
        
        # Placeholder implementation
        return f"[TRANSLATED TO {target_language.upper()}] {text}"

    async def _summarize_text(self, text: str, config: Dict) -> str:
        """Summarize text content"""
        max_length = config.get('max_length', 200)
        
        # Simple extractive summarization
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text
        
        # Take first and last sentences as summary
        summary = f"{sentences[0].strip()}. {sentences[-1].strip()}."
        
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary

    def supports_transformation(self, source_format: str, target_format: str) -> bool:
        """Check if text transformation is supported"""
        return True  # Text transformations are generally format-agnostic


class MetadataTransformer(ContentTransformer):
    """Advanced metadata content transformer"""
    
    async def transform_metadata(
        self,
        source_data: Union[Dict, str, bytes],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform metadata content"""
        try:
            config = params['config']
            transformation_type = params['transformation_type']
            
            # Parse source data
            if isinstance(source_data, (str, bytes)):
                if isinstance(source_data, bytes):
                    source_data = source_data.decode('utf-8')
                metadata = json.loads(source_data)
            else:
                metadata = source_data
            
            # Apply transformation based on type
            if transformation_type == TransformationType.METADATA_EXTRACTION:
                result_data = await self._extract_metadata(metadata, config)
            elif transformation_type == TransformationType.METADATA_ENRICHMENT:
                result_data = await self._enrich_metadata(metadata, config)
            elif transformation_type == TransformationType.DATA_NORMALIZATION:
                result_data = await self._normalize_metadata(metadata, config)
            else:
                raise ProcessingError(f"Unsupported metadata transformation: {transformation_type}")
            
            return {
                'output_data': json.dumps(result_data).encode('utf-8'),
                'metadata': {
                    'original_fields': len(metadata) if isinstance(metadata, dict) else 0,
                    'result_fields': len(result_data) if isinstance(result_data, dict) else 0,
                    'transformation_type': transformation_type.value
                }
            }
            
        except Exception as e:
            logger.error(f"Metadata transformation error: {str(e)}")
            raise ProcessingError(f"Metadata transformation failed: {str(e)}")

    async def _extract_metadata(self, metadata: Dict, config: Dict) -> Dict:
        """Extract specific metadata fields"""
        fields_to_extract = config.get('fields', [])
        
        if not fields_to_extract:
            return metadata
        
        extracted = {}
        for field in fields_to_extract:
            if field in metadata:
                extracted[field] = metadata[field]
        
        return extracted

    async def _enrich_metadata(self, metadata: Dict, config: Dict) -> Dict:
        """Enrich metadata with additional information"""
        enriched = metadata.copy()
        
        # Add timestamp if not present
        if 'enriched_at' not in enriched:
            enriched['enriched_at'] = datetime.now(timezone.utc).isoformat()
        
        # Add computed fields
        computed_fields = config.get('computed_fields', {})
        for field_name, field_config in computed_fields.items():
            enriched[field_name] = await self._compute_field_value(metadata, field_config)
        
        return enriched

    async def _normalize_metadata(self, metadata: Dict, config: Dict) -> Dict:
        """Normalize metadata structure and values"""
        normalized = {}
        
        # Apply field mappings
        field_mappings = config.get('field_mappings', {})
        for old_field, new_field in field_mappings.items():
            if old_field in metadata:
                normalized[new_field] = metadata[old_field]
        
        # Copy unmapped fields
        for field, value in metadata.items():
            if field not in field_mappings:
                normalized[field] = value
        
        # Apply value transformations
        value_transformations = config.get('value_transformations', {})
        for field, transformation in value_transformations.items():
            if field in normalized:
                normalized[field] = await self._transform_field_value(
                    normalized[field],
                    transformation
                )
        
        return normalized

    async def _compute_field_value(self, metadata: Dict, field_config: Dict) -> Any:
        """Compute value for a metadata field"""
        computation_type = field_config.get('type', 'static')
        
        if computation_type == 'static':
            return field_config.get('value')
        elif computation_type == 'concat':
            fields = field_config.get('fields', [])
            separator = field_config.get('separator', ' ')
            values = [str(metadata.get(field, '')) for field in fields]
            return separator.join(values)
        elif computation_type == 'sum':
            fields = field_config.get('fields', [])
            return sum(float(metadata.get(field, 0)) for field in fields)
        else:
            return None

    async def _transform_field_value(self, value: Any, transformation: Dict) -> Any:
        """Transform a field value"""
        transform_type = transformation.get('type', 'identity')
        
        if transform_type == 'identity':
            return value
        elif transform_type == 'lowercase':
            return str(value).lower()
        elif transform_type == 'uppercase':
            return str(value).upper()
        elif transform_type == 'strip':
            return str(value).strip()
        elif transform_type == 'replace':
            old_value = transformation.get('old', '')
            new_value = transformation.get('new', '')
            return str(value).replace(old_value, new_value)
        else:
            return value

    def supports_transformation(self, source_format: str, target_format: str) -> bool:
        """Check if metadata transformation is supported"""
        return True  # Metadata transformations are generally format-agnostic
