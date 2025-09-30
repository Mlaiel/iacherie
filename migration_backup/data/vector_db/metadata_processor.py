"""
Metadata Processor - Intelligent Metadata Processing Engine
===========================================================

Enterprise-grade metadata processor with automatic extraction, semantic
enrichment, quality assessment, and intelligent indexing capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import json
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import mimetypes
import base64

# Optional imports for advanced processing
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for metadata processing."""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    VECTOR = "vector"
    UNKNOWN = "unknown"


class QualityLevel(Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # 30-49%
    VERY_POOR = "very_poor" # 0-29%


@dataclass
class ContentFeatures:
    """Extracted content features."""
    content_type: ContentType
    file_size: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    encoding: Optional[str] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    color_space: Optional[str] = None
    compression: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    overall_score: float
    level: QualityLevel
    technical_score: float
    content_score: float
    completeness_score: float
    consistency_score: float
    issues: List[str]
    recommendations: List[str]


@dataclass
class SemanticEnrichment:
    """Semantic enrichment data."""
    keywords: List[str]
    categories: List[str]
    entities: List[Dict[str, Any]]
    sentiment: Optional[str] = None
    language: Optional[str] = None
    topics: Optional[List[str]] = None
    summary: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class ProcessedMetadata:
    """Complete processed metadata."""
    content_id: str
    content_type: ContentType
    original_metadata: Dict[str, Any]
    features: ContentFeatures
    quality_metrics: QualityMetrics
    semantic_enrichment: Optional[SemanticEnrichment]
    copyright_info: Optional[Dict[str, Any]]
    technical_specs: Dict[str, Any]
    processing_timestamp: datetime
    processor_version: str


class ContentTypeDetector:
    """Detects content type from various inputs."""
    
    def __init__(self):
        """Initialize content type detector."""
        self.mime_to_content_type = {
            # Text
            'text/plain': ContentType.TEXT,
            'text/html': ContentType.TEXT,
            'text/markdown': ContentType.TEXT,
            'application/json': ContentType.TEXT,
            'application/xml': ContentType.TEXT,
            
            # Audio
            'audio/mpeg': ContentType.AUDIO,
            'audio/wav': ContentType.AUDIO,
            'audio/ogg': ContentType.AUDIO,
            'audio/flac': ContentType.AUDIO,
            'audio/aac': ContentType.AUDIO,
            
            # Image
            'image/jpeg': ContentType.IMAGE,
            'image/png': ContentType.IMAGE,
            'image/gif': ContentType.IMAGE,
            'image/webp': ContentType.IMAGE,
            'image/svg+xml': ContentType.IMAGE,
            
            # Video
            'video/mp4': ContentType.VIDEO,
            'video/avi': ContentType.VIDEO,
            'video/mkv': ContentType.VIDEO,
            'video/webm': ContentType.VIDEO,
            'video/quicktime': ContentType.VIDEO,
            
            # Documents
            'application/pdf': ContentType.DOCUMENT,
            'application/msword': ContentType.DOCUMENT,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ContentType.DOCUMENT,
            
            # Code
            'text/x-python': ContentType.CODE,
            'text/javascript': ContentType.CODE,
            'text/x-java-source': ContentType.CODE,
            'text/x-c': ContentType.CODE,
        }
        
        self.extension_to_content_type = {
            # Text
            '.txt': ContentType.TEXT,
            '.md': ContentType.TEXT,
            '.json': ContentType.TEXT,
            '.xml': ContentType.TEXT,
            '.html': ContentType.TEXT,
            
            # Audio
            '.mp3': ContentType.AUDIO,
            '.wav': ContentType.AUDIO,
            '.flac': ContentType.AUDIO,
            '.ogg': ContentType.AUDIO,
            '.aac': ContentType.AUDIO,
            
            # Image
            '.jpg': ContentType.IMAGE,
            '.jpeg': ContentType.IMAGE,
            '.png': ContentType.IMAGE,
            '.gif': ContentType.IMAGE,
            '.webp': ContentType.IMAGE,
            '.svg': ContentType.IMAGE,
            
            # Video
            '.mp4': ContentType.VIDEO,
            '.avi': ContentType.VIDEO,
            '.mkv': ContentType.VIDEO,
            '.webm': ContentType.VIDEO,
            '.mov': ContentType.VIDEO,
            
            # Documents
            '.pdf': ContentType.DOCUMENT,
            '.doc': ContentType.DOCUMENT,
            '.docx': ContentType.DOCUMENT,
            
            # Code
            '.py': ContentType.CODE,
            '.js': ContentType.CODE,
            '.java': ContentType.CODE,
            '.c': ContentType.CODE,
            '.cpp': ContentType.CODE,
        }
    
    def detect_from_filename(self, filename: str) -> ContentType:
        """Detect content type from filename."""
        try:
            extension = Path(filename).suffix.lower()
            return self.extension_to_content_type.get(extension, ContentType.UNKNOWN)
        except Exception:
            return ContentType.UNKNOWN
    
    def detect_from_mime_type(self, mime_type: str) -> ContentType:
        """Detect content type from MIME type."""
        try:
            return self.mime_to_content_type.get(mime_type.lower(), ContentType.UNKNOWN)
        except Exception:
            return ContentType.UNKNOWN
    
    def detect_from_content(self, content: Union[str, bytes]) -> ContentType:
        """Detect content type from content analysis."""
        try:
            if isinstance(content, str):
                # Text analysis
                if self._looks_like_json(content):
                    return ContentType.TEXT
                elif self._looks_like_xml(content):
                    return ContentType.TEXT
                elif self._looks_like_code(content):
                    return ContentType.CODE
                else:
                    return ContentType.TEXT
            
            elif isinstance(content, bytes):
                # Binary analysis
                if self._is_image_bytes(content):
                    return ContentType.IMAGE
                elif self._is_audio_bytes(content):
                    return ContentType.AUDIO
                elif self._is_video_bytes(content):
                    return ContentType.VIDEO
                else:
                    return ContentType.UNKNOWN
            
            elif NUMPY_AVAILABLE and isinstance(content, np.ndarray):
                return ContentType.VECTOR
            
            return ContentType.UNKNOWN
            
        except Exception:
            return ContentType.UNKNOWN
    
    def _looks_like_json(self, content: str) -> bool:
        """Check if content looks like JSON."""
        try:
            json.loads(content.strip())
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def _looks_like_xml(self, content: str) -> bool:
        """Check if content looks like XML."""
        content = content.strip()
        return content.startswith('<?xml') or (content.startswith('<') and content.endswith('>'))
    
    def _looks_like_code(self, content: str) -> bool:
        """Check if content looks like code."""
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ', '#include',
            'var ', 'let ', 'const ', 'if (', 'for (', 'while ('
        ]
        return any(indicator in content for indicator in code_indicators)
    
    def _is_image_bytes(self, content: bytes) -> bool:
        """Check if bytes represent an image."""
        # Common image file signatures
        image_signatures = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'GIF87a', b'GIF89a',  # GIF
            b'RIFF',  # WEBP (starts with RIFF)
        ]
        return any(content.startswith(sig) for sig in image_signatures)
    
    def _is_audio_bytes(self, content: bytes) -> bool:
        """Check if bytes represent audio."""
        audio_signatures = [
            b'ID3',  # MP3 with ID3
            b'\xff\xfb', b'\xff\xfa',  # MP3
            b'RIFF',  # WAV
            b'fLaC',  # FLAC
            b'OggS',  # OGG
        ]
        return any(content.startswith(sig) for sig in audio_signatures)
    
    def _is_video_bytes(self, content: bytes) -> bool:
        """Check if bytes represent video."""
        video_signatures = [
            b'\x00\x00\x00\x18ftypmp4',  # MP4
            b'\x00\x00\x00\x20ftypM4V',  # M4V
            b'RIFF',  # AVI
            b'\x1aE\xdf\xa3',  # MKV
        ]
        return any(content.startswith(sig) for sig in video_signatures)


class FeatureExtractor:
    """Extracts technical features from content."""
    
    def __init__(self):
        """Initialize feature extractor."""
        self.content_type_detector = ContentTypeDetector()
    
    async def extract_features(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: Optional[ContentType] = None,
        filename: Optional[str] = None
    ) -> ContentFeatures:
        """
        Extract features from content.
        
        Args:
            content: Content to analyze
            content_type: Known content type
            filename: Original filename
        
        Returns:
            Extracted features
        """
        try:
            # Detect content type if not provided
            if content_type is None:
                content_type = self._detect_content_type(content, filename)
            
            # Extract features based on type
            if content_type == ContentType.TEXT:
                return await self._extract_text_features(content, filename)
            elif content_type == ContentType.IMAGE:
                return await self._extract_image_features(content, filename)
            elif content_type == ContentType.AUDIO:
                return await self._extract_audio_features(content, filename)
            elif content_type == ContentType.VIDEO:
                return await self._extract_video_features(content, filename)
            elif content_type == ContentType.VECTOR:
                return await self._extract_vector_features(content)
            else:
                return await self._extract_generic_features(content, content_type, filename)
                
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return ContentFeatures(content_type=content_type or ContentType.UNKNOWN)
    
    def _detect_content_type(
        self,
        content: Union[str, bytes, np.ndarray],
        filename: Optional[str]
    ) -> ContentType:
        """Detect content type using multiple methods."""
        # Try filename first
        if filename:
            content_type = self.content_type_detector.detect_from_filename(filename)
            if content_type != ContentType.UNKNOWN:
                return content_type
        
        # Try content analysis
        return self.content_type_detector.detect_from_content(content)
    
    async def _extract_text_features(
        self,
        content: Union[str, bytes],
        filename: Optional[str]
    ) -> ContentFeatures:
        """Extract features from text content."""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            features = ContentFeatures(
                content_type=ContentType.TEXT,
                file_size=len(content.encode('utf-8')),
                encoding='utf-8'
            )
            
            # Detect format from content or filename
            if filename:
                ext = Path(filename).suffix.lower()
                format_map = {
                    '.txt': 'plain_text',
                    '.md': 'markdown',
                    '.html': 'html',
                    '.json': 'json',
                    '.xml': 'xml'
                }
                features.format = format_map.get(ext, 'plain_text')
            else:
                # Simple format detection
                if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                    features.format = 'html'
                elif self.content_type_detector._looks_like_json(content):
                    features.format = 'json'
                elif self.content_type_detector._looks_like_xml(content):
                    features.format = 'xml'
                elif '# ' in content or '## ' in content:
                    features.format = 'markdown'
                else:
                    features.format = 'plain_text'
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract text features: {e}")
            return ContentFeatures(content_type=ContentType.TEXT)
    
    async def _extract_image_features(
        self,
        content: Union[str, bytes],
        filename: Optional[str]
    ) -> ContentFeatures:
        """Extract features from image content."""
        try:
            features = ContentFeatures(content_type=ContentType.IMAGE)
            
            if isinstance(content, str):
                # Assume base64 encoded
                try:
                    content = base64.b64decode(content)
                except Exception:
                    return features
            
            features.file_size = len(content)
            
            # Extract image metadata using PIL if available
            if PIL_AVAILABLE:
                try:
                    image = Image.open(io.BytesIO(content))
                    features.dimensions = image.size
                    features.format = image.format.lower() if image.format else None
                    features.color_space = image.mode
                    
                    # Check for compression
                    if hasattr(image, 'info'):
                        if 'compression' in image.info:
                            features.compression = str(image.info['compression'])
                        if 'dpi' in image.info:
                            features.resolution = f"{image.info['dpi'][0]}x{image.info['dpi'][1]} DPI"
                    
                except Exception as e:
                    logger.debug(f"PIL image analysis failed: {e}")
            
            # Fallback: detect format from file signature
            if not features.format:
                if content.startswith(b'\xff\xd8\xff'):
                    features.format = 'jpeg'
                elif content.startswith(b'\x89PNG\r\n\x1a\n'):
                    features.format = 'png'
                elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
                    features.format = 'gif'
                elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
                    features.format = 'webp'
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract image features: {e}")
            return ContentFeatures(content_type=ContentType.IMAGE)
    
    async def _extract_audio_features(
        self,
        content: Union[str, bytes],
        filename: Optional[str]
    ) -> ContentFeatures:
        """Extract features from audio content."""
        try:
            features = ContentFeatures(content_type=ContentType.AUDIO)
            
            if isinstance(content, str):
                # Assume base64 encoded
                try:
                    content = base64.b64decode(content)
                except Exception:
                    return features
            
            features.file_size = len(content)
            
            # Basic format detection from file signature
            if content.startswith(b'ID3') or content.startswith(b'\xff\xfb') or content.startswith(b'\xff\xfa'):
                features.format = 'mp3'
            elif content.startswith(b'RIFF') and b'WAVE' in content[:12]:
                features.format = 'wav'
            elif content.startswith(b'fLaC'):
                features.format = 'flac'
            elif content.startswith(b'OggS'):
                features.format = 'ogg'
            elif filename:
                ext = Path(filename).suffix.lower()
                features.format = ext[1:] if ext else None
            
            # Note: More detailed audio analysis would require librosa or similar
            # For now, we provide basic format detection
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract audio features: {e}")
            return ContentFeatures(content_type=ContentType.AUDIO)
    
    async def _extract_video_features(
        self,
        content: Union[str, bytes],
        filename: Optional[str]
    ) -> ContentFeatures:
        """Extract features from video content."""
        try:
            features = ContentFeatures(content_type=ContentType.VIDEO)
            
            if isinstance(content, str):
                # Assume base64 encoded
                try:
                    content = base64.b64decode(content)
                except Exception:
                    return features
            
            features.file_size = len(content)
            
            # Basic format detection
            if b'ftyp' in content[:20]:
                features.format = 'mp4'
            elif content.startswith(b'RIFF') and b'AVI ' in content[:12]:
                features.format = 'avi'
            elif content.startswith(b'\x1aE\xdf\xa3'):
                features.format = 'mkv'
            elif filename:
                ext = Path(filename).suffix.lower()
                features.format = ext[1:] if ext else None
            
            # Note: Detailed video analysis would require opencv or ffmpeg
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract video features: {e}")
            return ContentFeatures(content_type=ContentType.VIDEO)
    
    async def _extract_vector_features(self, content: np.ndarray) -> ContentFeatures:
        """Extract features from vector content."""
        try:
            features = ContentFeatures(
                content_type=ContentType.VECTOR,
                dimensions=(content.shape[0], content.shape[1] if content.ndim > 1 else 1),
                file_size=content.nbytes,
                format=str(content.dtype),
                encoding=f"{content.ndim}D_array"
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract vector features: {e}")
            return ContentFeatures(content_type=ContentType.VECTOR)
    
    async def _extract_generic_features(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: ContentType,
        filename: Optional[str]
    ) -> ContentFeatures:
        """Extract generic features from unknown content."""
        try:
            features = ContentFeatures(content_type=content_type)
            
            if isinstance(content, (str, bytes)):
                if isinstance(content, str):
                    features.file_size = len(content.encode('utf-8'))
                    features.encoding = 'utf-8'
                else:
                    features.file_size = len(content)
                    features.encoding = 'binary'
            
            if filename:
                ext = Path(filename).suffix.lower()
                features.format = ext[1:] if ext else None
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract generic features: {e}")
            return ContentFeatures(content_type=content_type)


class QualityAssessor:
    """Assesses content quality using various metrics."""
    
    def __init__(self):
        """Initialize quality assessor."""
        pass
    
    async def assess_quality(
        self,
        content: Union[str, bytes, np.ndarray],
        features: ContentFeatures,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityMetrics:
        """
        Assess content quality.
        
        Args:
            content: Content to assess
            features: Extracted features
            metadata: Additional metadata
        
        Returns:
            Quality assessment metrics
        """
        try:
            # Assess different quality dimensions
            technical_score = await self._assess_technical_quality(content, features)
            content_score = await self._assess_content_quality(content, features)
            completeness_score = await self._assess_completeness(features, metadata)
            consistency_score = await self._assess_consistency(features, metadata)
            
            # Calculate overall score
            overall_score = (
                technical_score * 0.3 +
                content_score * 0.4 +
                completeness_score * 0.2 +
                consistency_score * 0.1
            )
            
            # Determine quality level
            level = self._determine_quality_level(overall_score)
            
            # Identify issues and recommendations
            issues, recommendations = await self._analyze_issues_and_recommendations(
                overall_score, technical_score, content_score, completeness_score, 
                consistency_score, features
            )
            
            return QualityMetrics(
                overall_score=overall_score,
                level=level,
                technical_score=technical_score,
                content_score=content_score,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to assess quality: {e}")
            return QualityMetrics(
                overall_score=0.0,
                level=QualityLevel.VERY_POOR,
                technical_score=0.0,
                content_score=0.0,
                completeness_score=0.0,
                consistency_score=0.0,
                issues=[f"Quality assessment failed: {e}"],
                recommendations=["Review content and try again"]
            )
    
    async def _assess_technical_quality(
        self,
        content: Union[str, bytes, np.ndarray],
        features: ContentFeatures
    ) -> float:
        """Assess technical quality (encoding, format, resolution, etc.)."""
        try:
            score = 70.0  # Base score
            
            # Check file size reasonableness
            if features.file_size:
                if features.content_type == ContentType.TEXT:
                    # Text should not be too large or too small
                    if 10 <= features.file_size <= 1024 * 1024:  # 10 bytes to 1MB
                        score += 10
                elif features.content_type == ContentType.IMAGE:
                    # Images should have reasonable size
                    if 1024 <= features.file_size <= 10 * 1024 * 1024:  # 1KB to 10MB
                        score += 10
                elif features.content_type == ContentType.VECTOR:
                    # Vectors should have reasonable dimensions
                    if features.dimensions and features.dimensions[0] > 0:
                        score += 10
            
            # Check format validity
            if features.format:
                score += 10  # Has valid format
            
            # Check encoding
            if features.encoding:
                if features.encoding in ['utf-8', 'ascii']:
                    score += 5  # Good text encoding
                elif features.encoding == 'binary':
                    score += 3  # Binary is ok
            
            # Check dimensions for images/videos
            if features.dimensions and features.content_type in [ContentType.IMAGE, ContentType.VIDEO]:
                width, height = features.dimensions
                if width >= 100 and height >= 100:  # Reasonable resolution
                    score += 5
                if width >= 1920 or height >= 1080:  # High resolution
                    score += 5
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Technical quality assessment failed: {e}")
            return 0.0
    
    async def _assess_content_quality(
        self,
        content: Union[str, bytes, np.ndarray],
        features: ContentFeatures
    ) -> float:
        """Assess content quality (readability, completeness, structure, etc.)."""
        try:
            score = 60.0  # Base score
            
            if features.content_type == ContentType.TEXT and isinstance(content, str):
                # Text-specific quality checks
                
                # Check length
                if 50 <= len(content) <= 10000:  # Reasonable length
                    score += 15
                
                # Check for basic structure
                if any(char in content for char in '.!?'):  # Has punctuation
                    score += 10
                
                # Check for varied vocabulary (simple metric)
                words = re.findall(r'\w+', content.lower())
                if words:
                    unique_ratio = len(set(words)) / len(words)
                    if unique_ratio > 0.5:  # Good vocabulary variety
                        score += 10
                
                # Check for readability indicators
                sentences = re.split(r'[.!?]+', content)
                if sentences:
                    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                    if 10 <= avg_sentence_length <= 25:  # Good sentence length
                        score += 5
            
            elif features.content_type == ContentType.VECTOR and NUMPY_AVAILABLE:
                # Vector-specific quality checks
                if isinstance(content, np.ndarray):
                    # Check for reasonable value ranges
                    if np.isfinite(content).all():  # No inf or nan
                        score += 15
                    
                    # Check for normalized vectors (common in embeddings)
                    norm = np.linalg.norm(content)
                    if 0.8 <= norm <= 1.2:  # Approximately normalized
                        score += 10
                    
                    # Check for variance (not all zeros or constants)
                    if np.var(content) > 1e-6:
                        score += 10
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Content quality assessment failed: {e}")
            return 0.0
    
    async def _assess_completeness(
        self,
        features: ContentFeatures,
        metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Assess completeness of content and metadata."""
        try:
            score = 50.0  # Base score
            
            # Check feature completeness
            if features.file_size is not None:
                score += 10
            if features.format is not None:
                score += 10
            if features.encoding is not None:
                score += 5
            
            # Content type specific checks
            if features.content_type == ContentType.IMAGE:
                if features.dimensions is not None:
                    score += 15
                if features.color_space is not None:
                    score += 5
            elif features.content_type == ContentType.AUDIO:
                if features.duration is not None:
                    score += 10
                if features.sample_rate is not None:
                    score += 5
            elif features.content_type == ContentType.VECTOR:
                if features.dimensions is not None:
                    score += 15
            
            # Metadata completeness
            if metadata:
                score += 5  # Has metadata
                if len(metadata) > 3:  # Rich metadata
                    score += 5
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Completeness assessment failed: {e}")
            return 0.0
    
    async def _assess_consistency(
        self,
        features: ContentFeatures,
        metadata: Optional[Dict[str, Any]]
    ) -> float:
        """Assess consistency between features and metadata."""
        try:
            score = 80.0  # Base score (assume consistent unless proven otherwise)
            
            if metadata:
                # Check consistency between features and metadata
                if 'content_type' in metadata:
                    metadata_type = metadata['content_type']
                    if metadata_type != features.content_type.value:
                        score -= 20  # Inconsistent content type
                
                if 'file_size' in metadata and features.file_size:
                    metadata_size = metadata['file_size']
                    size_diff = abs(metadata_size - features.file_size) / max(metadata_size, features.file_size)
                    if size_diff > 0.1:  # More than 10% difference
                        score -= 10
                
                if 'format' in metadata and features.format:
                    if metadata['format'].lower() != features.format.lower():
                        score -= 15
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Consistency assessment failed: {e}")
            return 80.0  # Default to consistent
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score."""
        if overall_score >= 90:
            return QualityLevel.EXCELLENT
        elif overall_score >= 70:
            return QualityLevel.GOOD
        elif overall_score >= 50:
            return QualityLevel.FAIR
        elif overall_score >= 30:
            return QualityLevel.POOR
        else:
            return QualityLevel.VERY_POOR
    
    async def _analyze_issues_and_recommendations(
        self,
        overall_score: float,
        technical_score: float,
        content_score: float,
        completeness_score: float,
        consistency_score: float,
        features: ContentFeatures
    ) -> Tuple[List[str], List[str]]:
        """Analyze issues and generate recommendations."""
        issues = []
        recommendations = []
        
        try:
            # Technical issues
            if technical_score < 70:
                issues.append("Technical quality issues detected")
                recommendations.append("Check file format, encoding, and technical specifications")
            
            # Content issues
            if content_score < 60:
                issues.append("Content quality below standards")
                if features.content_type == ContentType.TEXT:
                    recommendations.append("Improve text structure, grammar, and readability")
                elif features.content_type == ContentType.VECTOR:
                    recommendations.append("Check vector normalization and value ranges")
            
            # Completeness issues
            if completeness_score < 60:
                issues.append("Incomplete metadata or features")
                recommendations.append("Provide more complete metadata and content information")
            
            # Consistency issues
            if consistency_score < 70:
                issues.append("Inconsistencies between metadata and content")
                recommendations.append("Verify metadata accuracy and consistency with content")
            
            # Overall quality
            if overall_score < 50:
                issues.append("Overall quality is below acceptable standards")
                recommendations.append("Consider content revision or re-processing")
            
            # Specific feature-based recommendations
            if not features.format:
                recommendations.append("Specify content format for better processing")
            
            if features.content_type == ContentType.UNKNOWN:
                recommendations.append("Provide content type information for optimal processing")
            
        except Exception as e:
            logger.error(f"Issue analysis failed: {e}")
            issues.append("Quality analysis incomplete")
            recommendations.append("Retry quality assessment")
        
        return issues, recommendations


class MetadataProcessor:
    """
    Enterprise-grade metadata processor for Vector Database Module.
    
    Features:
    - Automatic content type detection
    - Feature extraction for all content types
    - Quality assessment with scoring
    - Semantic enrichment with NLP
    - Copyright information extraction
    - Technical specifications analysis
    - Intelligent indexing optimization
    - Metadata validation and cleanup
    - Real-time processing capabilities
    - Batch processing support
    """
    
    def __init__(self, config: Any):
        """
        Initialize metadata processor.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Configuration
        self.enable_quality_assessment = config.get('metadata.enable_quality_assessment', True)
        self.enable_semantic_enrichment = config.get('metadata.enable_semantic_enrichment', False)
        self.enable_copyright_detection = config.get('metadata.enable_copyright_detection', True)
        self.batch_size = config.get('metadata.batch_size', 100)
        self.processor_version = "1.0.0"
        
        # Core components
        self.content_type_detector = ContentTypeDetector()
        self.feature_extractor = FeatureExtractor()
        self.quality_assessor = QualityAssessor()
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'by_content_type': {},
            'avg_quality_score': 0.0,
            'processing_errors': 0
        }
        
        logger.info("MetadataProcessor initialized")
    
    async def initialize(self) -> bool:
        """Initialize the metadata processor."""
        try:
            logger.info("MetadataProcessor initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MetadataProcessor: {e}")
            return False
    
    async def process_metadata(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[str] = None
    ) -> ProcessedMetadata:
        """
        Process metadata for content.
        
        Args:
            content: Content to process
            content_type: Content type hint
            custom_metadata: Additional custom metadata
            content_id: Content identifier
        
        Returns:
            Processed metadata
        """
        try:
            content_id = content_id or hashlib.md5(str(content).encode()).hexdigest()
            
            # Detect content type
            detected_type = ContentType.UNKNOWN
            if content_type:
                try:
                    detected_type = ContentType(content_type)
                except ValueError:
                    detected_type = self.content_type_detector.detect_from_content(content)
            else:
                detected_type = self.content_type_detector.detect_from_content(content)
            
            # Extract features
            features = await self.feature_extractor.extract_features(
                content, detected_type
            )
            
            # Assess quality
            quality_metrics = None
            if self.enable_quality_assessment:
                quality_metrics = await self.quality_assessor.assess_quality(
                    content, features, custom_metadata
                )
            else:
                # Default quality metrics
                quality_metrics = QualityMetrics(
                    overall_score=75.0,
                    level=QualityLevel.GOOD,
                    technical_score=75.0,
                    content_score=75.0,
                    completeness_score=75.0,
                    consistency_score=75.0,
                    issues=[],
                    recommendations=[]
                )
            
            # Semantic enrichment (placeholder - would integrate with NLP services)
            semantic_enrichment = None
            if self.enable_semantic_enrichment:
                semantic_enrichment = await self._perform_semantic_enrichment(content, detected_type)
            
            # Copyright detection (placeholder)
            copyright_info = None
            if self.enable_copyright_detection:
                copyright_info = await self._detect_copyright_info(content, custom_metadata)
            
            # Technical specifications
            technical_specs = await self._extract_technical_specs(content, features)
            
            # Create processed metadata
            processed_metadata = ProcessedMetadata(
                content_id=content_id,
                content_type=detected_type,
                original_metadata=custom_metadata or {},
                features=features,
                quality_metrics=quality_metrics,
                semantic_enrichment=semantic_enrichment,
                copyright_info=copyright_info,
                technical_specs=technical_specs,
                processing_timestamp=datetime.utcnow(),
                processor_version=self.processor_version
            )
            
            # Update statistics
            self._update_statistics(detected_type, quality_metrics.overall_score)
            
            return processed_metadata
            
        except Exception as e:
            logger.error(f"Failed to process metadata: {e}")
            self.stats['processing_errors'] += 1
            
            # Return minimal metadata on error
            return ProcessedMetadata(
                content_id=content_id or "unknown",
                content_type=ContentType.UNKNOWN,
                original_metadata=custom_metadata or {},
                features=ContentFeatures(content_type=ContentType.UNKNOWN),
                quality_metrics=QualityMetrics(
                    overall_score=0.0,
                    level=QualityLevel.VERY_POOR,
                    technical_score=0.0,
                    content_score=0.0,
                    completeness_score=0.0,
                    consistency_score=0.0,
                    issues=[f"Processing failed: {e}"],
                    recommendations=["Review content and retry processing"]
                ),
                semantic_enrichment=None,
                copyright_info=None,
                technical_specs={},
                processing_timestamp=datetime.utcnow(),
                processor_version=self.processor_version
            )
    
    async def process_batch(
        self,
        content_list: List[Tuple[Union[str, bytes, np.ndarray], Optional[str], Optional[Dict[str, Any]]]]
    ) -> List[ProcessedMetadata]:
        """
        Process metadata for a batch of content.
        
        Args:
            content_list: List of (content, content_type, custom_metadata) tuples
        
        Returns:
            List of processed metadata
        """
        try:
            results = []
            
            # Process in chunks
            for i in range(0, len(content_list), self.batch_size):
                batch = content_list[i:i + self.batch_size]
                
                # Process batch
                batch_tasks = [
                    self.process_metadata(content, content_type, custom_metadata)
                    for content, content_type, custom_metadata in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Handle exceptions
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error for item {i+j}: {result}")
                        # Create error metadata
                        error_metadata = ProcessedMetadata(
                            content_id=f"error_{i+j}",
                            content_type=ContentType.UNKNOWN,
                            original_metadata={},
                            features=ContentFeatures(content_type=ContentType.UNKNOWN),
                            quality_metrics=QualityMetrics(
                                overall_score=0.0,
                                level=QualityLevel.VERY_POOR,
                                technical_score=0.0,
                                content_score=0.0,
                                completeness_score=0.0,
                                consistency_score=0.0,
                                issues=[f"Batch processing failed: {result}"],
                                recommendations=["Review content and retry"]
                            ),
                            semantic_enrichment=None,
                            copyright_info=None,
                            technical_specs={},
                            processing_timestamp=datetime.utcnow(),
                            processor_version=self.processor_version
                        )
                        results.append(error_metadata)
                    else:
                        results.append(result)
            
            logger.info(f"Batch processed {len(results)} items")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []
    
    async def _perform_semantic_enrichment(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: ContentType
    ) -> Optional[SemanticEnrichment]:
        """Perform semantic enrichment (placeholder for NLP integration)."""
        try:
            # This would integrate with NLP services like spaCy, NLTK, or cloud APIs
            # For now, provide basic analysis for text content
            
            if content_type == ContentType.TEXT and isinstance(content, str):
                # Simple keyword extraction
                words = re.findall(r'\w+', content.lower())
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Skip short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get top keywords
                keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                keywords = [word for word, freq in keywords]
                
                # Simple category detection
                categories = []
                if any(word in content.lower() for word in ['technology', 'computer', 'software']):
                    categories.append('technology')
                if any(word in content.lower() for word in ['business', 'company', 'market']):
                    categories.append('business')
                
                return SemanticEnrichment(
                    keywords=keywords,
                    categories=categories,
                    entities=[],  # Would extract with NER
                    language='en',  # Would detect with language detection
                    confidence_score=0.7
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Semantic enrichment failed: {e}")
            return None
    
    async def _detect_copyright_info(
        self,
        content: Union[str, bytes, np.ndarray],
        metadata: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Detect copyright information."""
        try:
            copyright_info = {}
            
            # Check metadata for copyright info
            if metadata:
                for key in ['copyright', 'license', 'author', 'creator']:
                    if key in metadata:
                        copyright_info[key] = metadata[key]
            
            # Check content for copyright notices
            if isinstance(content, str):
                # Look for copyright notices
                copyright_patterns = [
                    r'©\s*(\d{4})',
                    r'copyright\s*(\d{4})',
                    r'all rights reserved',
                    r'proprietary'
                ]
                
                for pattern in copyright_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        copyright_info['detected_years'] = matches
                        copyright_info['has_copyright_notice'] = True
                        break
                else:
                    copyright_info['has_copyright_notice'] = False
            
            return copyright_info if copyright_info else None
            
        except Exception as e:
            logger.error(f"Copyright detection failed: {e}")
            return None
    
    async def _extract_technical_specs(
        self,
        content: Union[str, bytes, np.ndarray],
        features: ContentFeatures
    ) -> Dict[str, Any]:
        """Extract technical specifications."""
        try:
            specs = {
                'content_type': features.content_type.value,
                'format': features.format,
                'encoding': features.encoding,
                'file_size': features.file_size
            }
            
            if features.dimensions:
                specs['dimensions'] = features.dimensions
            
            if features.duration:
                specs['duration'] = features.duration
            
            if features.resolution:
                specs['resolution'] = features.resolution
            
            if features.bitrate:
                specs['bitrate'] = features.bitrate
            
            if features.sample_rate:
                specs['sample_rate'] = features.sample_rate
            
            if features.channels:
                specs['channels'] = features.channels
            
            if features.color_space:
                specs['color_space'] = features.color_space
            
            if features.compression:
                specs['compression'] = features.compression
            
            # Add processing metadata
            specs['processed_at'] = datetime.utcnow().isoformat()
            specs['processor_version'] = self.processor_version
            
            return specs
            
        except Exception as e:
            logger.error(f"Technical specs extraction failed: {e}")
            return {}
    
    def _update_statistics(self, content_type: ContentType, quality_score: float) -> None:
        """Update processing statistics."""
        try:
            self.stats['total_processed'] += 1
            
            # Update by content type
            type_key = content_type.value
            if type_key not in self.stats['by_content_type']:
                self.stats['by_content_type'][type_key] = 0
            self.stats['by_content_type'][type_key] += 1
            
            # Update average quality score
            total = self.stats['total_processed']
            current_avg = self.stats['avg_quality_score']
            self.stats['avg_quality_score'] = ((current_avg * (total - 1)) + quality_score) / total
            
        except Exception as e:
            logger.error(f"Statistics update failed: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
    
    async def health_check(self) -> bool:
        """Perform health check on metadata processor."""
        try:
            # Test with simple content
            test_content = "This is a test content for health check."
            test_metadata = await self.process_metadata(test_content, "text")
            
            # Check if processing completed without errors
            return test_metadata.content_type == ContentType.TEXT
            
        except Exception as e:
            logger.error(f"Metadata processor health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the metadata processor."""
        logger.info("Shutting down MetadataProcessor...")
        
        # Log final statistics
        logger.info(f"Final processing statistics: {self.stats}")
        
        logger.info("MetadataProcessor shutdown completed")


# Export main classes
__all__ = [
    'MetadataProcessor',
    'ContentTypeDetector',
    'FeatureExtractor',
    'QualityAssessor',
    'ContentType',
    'QualityLevel',
    'ContentFeatures',
    'QualityMetrics',
    'SemanticEnrichment',
    'ProcessedMetadata'
]