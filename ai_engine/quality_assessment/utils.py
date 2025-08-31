"""Quality Assessment Utilities

Utility functions and helpers for the quality assessment module.
Provides common functionality, data processing, and helper methods.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""import os
import re
import hashlib
import mimetypes
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from datetime import datetime, timedelta
import json
import logging
import numpy as np
import cv2
from PIL import Image, ExifTags
import magic
import hashlib

from .exceptions import (
    UnsupportedFormatError,
    ContentValidationError,
    ResourceError
)

logger = logging.getLogger(__name__)


class FileValidator:
    """    File validation utilities
    
    Provides comprehensive file validation, format detection, and integrity checking.
    """    
    # Supported MIME types by category
    SUPPORTED_MIME_TYPES = {
        'audio': {
            'audio/wav', 'audio/wave', 'audio/x-wav',
            'audio/mpeg', 'audio/mp3',
            'audio/flac',
            'audio/aac', 'audio/x-aac',
            'audio/ogg', 'audio/x-ogg',
            'audio/mp4', 'audio/x-m4a'
        },
        'video': {
            'video/mp4', 'video/x-mp4',
            'video/avi', 'video/x-msvideo',
            'video/quicktime', 'video/x-quicktime',
            'video/x-ms-wmv',
            'video/x-flv',
            'video/webm',
            'video/x-matroska'
        },
        'image': {
            'image/jpeg', 'image/jpg',
            'image/png',
            'image/gif',
            'image/bmp', 'image/x-ms-bmp',
            'image/tiff', 'image/x-tiff',
            'image/webp',
            'image/svg+xml'
        },
        'text': {
            'text/plain',
            'text/html',
            'text/markdown',
            'text/csv',
            'application/json',
            'application/xml'
        }
    }
    
    @staticmethod
    def detect_file_type(file_path: Union[str, Path]) -> str:
        """        Detect file type using multiple methods
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected content type (audio, video, image, text)
            
        Raises:
            UnsupportedFormatError: If format is not supported
        """        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ContentValidationError(
                f"File not found: {file_path}",
                error_code="FILE_NOT_FOUND",
                file_path=str(file_path)
            )
        
        # Method 1: MIME type detection using python-magic
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
        except Exception:
            # Fallback to mimetypes module
            mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if not mime_type:
            raise UnsupportedFormatError(
                f"Could not detect MIME type for file: {file_path}",
                file_path=str(file_path),
                detected_format="unknown",
                supported_formats=list(FileValidator.get_all_supported_formats())
            )
        
        # Find content type from MIME type
        for content_type, mime_types in FileValidator.SUPPORTED_MIME_TYPES.items():
            if mime_type in mime_types:
                return content_type
        
        raise UnsupportedFormatError(
            f"Unsupported MIME type: {mime_type}",
            file_path=str(file_path),
            detected_format=mime_type,
            supported_formats=list(FileValidator.get_all_supported_formats())
        )
    
    @staticmethod
    def get_all_supported_formats() -> Set[str]:
        """Get all supported MIME types"""        all_formats = set()
        for mime_types in FileValidator.SUPPORTED_MIME_TYPES.values():
            all_formats.update(mime_types)
        return all_formats
    
    @staticmethod
    def validate_file_integrity(file_path: Union[str, Path]) -> bool:
        """        Validate file integrity
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid
            
        Raises:
            ContentValidationError: If file is corrupted
        """        file_path = Path(file_path)
        
        try:
            # Basic file existence and readability check
            if not file_path.exists():
                raise ContentValidationError(
                    f"File does not exist: {file_path}",
                    error_code="FILE_NOT_FOUND"
                )
            
            if file_path.stat().st_size == 0:
                raise ContentValidationError(
                    f"File is empty: {file_path}",
                    error_code="EMPTY_FILE"
                )
            
            # Try to read the file
            with open(file_path, 'rb') as f:
                # Read first 1KB to check basic integrity
                chunk = f.read(1024)
                if not chunk:
                    raise ContentValidationError(
                        f"Cannot read file content: {file_path}",
                        error_code="UNREADABLE_FILE"
                    )
            
            return True
            
        except Exception as e:
            if isinstance(e, ContentValidationError):
                raise
            else:
                raise ContentValidationError(
                    f"File integrity validation failed: {str(e)}",
                    error_code="INTEGRITY_CHECK_FAILED",
                    file_path=str(file_path)
                )
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """        Calculate file hash for integrity checking
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
            
        Returns:
            Hexadecimal hash string
        """        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
        """        Extract comprehensive file metadata
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """        file_path = Path(file_path)
        stat = file_path.stat()
        
        metadata = {
            'file_name': file_path.name,
            'file_path': str(file_path.absolute()),
            'file_size': stat.st_size,
            'file_extension': file_path.suffix.lower(),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'accessed_time': datetime.fromtimestamp(stat.st_atime),
            'mime_type': None,
            'content_type': None,
            'file_hash': None
        }
        
        # Detect MIME type and content type
        try:
            metadata['content_type'] = FileValidator.detect_file_type(file_path)
            metadata['mime_type'] = magic.from_file(str(file_path), mime=True)
        except Exception as e:
            logger.warning(f"Could not detect file type for {file_path}: {e}")
        
        # Calculate file hash
        try:
            metadata['file_hash'] = FileValidator.get_file_hash(file_path)
        except Exception as e:
            logger.warning(f"Could not calculate hash for {file_path}: {e}")
        
        return metadata


class DataProcessor:
    """    Data processing utilities
    
    Provides data transformation, normalization, and processing functions.
    """    
    @staticmethod
    def normalize_score(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """        Normalize a score to 0-100 range
        
        Args:
            value: Input value
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            Normalized score (0-100)
        """        if max_val == min_val:
            return 50.0  # Default middle value
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))
    
    @staticmethod
    def calculate_weighted_score(
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """        Calculate weighted average score
        
        Args:
            scores: Dictionary of metric names and scores
            weights: Dictionary of metric names and weights
            
        Returns:
            Weighted average score
        """        if not scores or not weights:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric, score in scores.items():
            weight = weights.get(metric, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_weighted_score / total_weight
    
    @staticmethod
    def percentile_rank(value: float, values: List[float]) -> float:
        """        Calculate percentile rank of a value
        
        Args:
            value: Target value
            values: List of all values for comparison
            
        Returns:
            Percentile rank (0-100)
        """        if not values:
            return 50.0
        
        values_sorted = sorted(values)
        rank = sum(1 for v in values_sorted if v <= value)
        return (rank / len(values_sorted)) * 100
    
    @staticmethod
    def smooth_values(values: List[float], window_size: int = 3) -> List[float]:
        """        Apply moving average smoothing to values
        
        Args:
            values: List of values to smooth
            window_size: Size of the smoothing window
            
        Returns:
            List of smoothed values
        """        if len(values) < window_size:
            return values.copy()
        
        smoothed = []
        half_window = window_size // 2
        
        for i in range(len(values)):
            start_idx = max(0, i - half_window)
            end_idx = min(len(values), i + half_window + 1)
            window_values = values[start_idx:end_idx]
            smoothed.append(sum(window_values) / len(window_values))
        
        return smoothed
    
    @staticmethod
    def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
        """        Detect outliers using z-score method
        
        Args:
            values: List of values
            threshold: Z-score threshold for outlier detection
            
        Returns:
            List of indices of outlier values
        """        if len(values) < 3:
            return []
        
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return []
        
        outlier_indices = []
        for i, value in enumerate(values):
            z_score = abs((value - mean_val) / std_val)
            if z_score > threshold:
                outlier_indices.append(i)
        
        return outlier_indices


class TextProcessor:
    """    Text processing utilities
    
    Provides text analysis, cleaning, and processing functions.
    """    
    @staticmethod
    def clean_text(text: str, remove_html: bool = True, remove_urls: bool = True) -> str:
        """        Clean and normalize text
        
        Args:
            text: Input text
            remove_html: Remove HTML tags
            remove_urls: Remove URLs
            
        Returns:
            Cleaned text
        """        if not text:
            return ""
        
        # Remove HTML tags
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        if remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_keywords(text: str, top_k: int = 10) -> List[str]:
        """        Extract keywords from text
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of keywords
        """        # Simple keyword extraction using word frequency
        # In production, use more sophisticated NLP libraries
        
        # Clean text
        cleaned_text = TextProcessor.clean_text(text.lower())
        
        # Remove common stop words (simplified)
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'a', 'an'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text)
        
        # Count word frequencies (excluding stop words)
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:top_k]]
    
    @staticmethod
    def calculate_readability_score(text: str) -> Dict[str, float]:
        """        Calculate various readability scores
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of readability scores
        """        if not text or len(text.strip()) < 10:
            return {
                'flesch_kincaid_grade': 0.0,
                'flesch_reading_ease': 0.0,
                'avg_sentence_length': 0.0,
                'avg_syllables_per_word': 0.0
            }
        
        # Count sentences (simplified)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            sentence_count = 1
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        if word_count == 0:
            return {
                'flesch_kincaid_grade': 0.0,
                'flesch_reading_ease': 0.0,
                'avg_sentence_length': 0.0,
                'avg_syllables_per_word': 0.0
            }
        
        # Count syllables (simplified estimation)
        syllable_count = 0
        for word in words:
            word = word.lower()
            syllable_count += max(1, len(re.findall(r'[aeiouAEIOU]', word)))
        
        # Calculate metrics
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        
        # Flesch Reading Ease
        fre_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return {
            'flesch_kincaid_grade': max(0.0, fk_grade),
            'flesch_reading_ease': max(0.0, min(100.0, fre_score)),
            'avg_sentence_length': avg_sentence_length,
            'avg_syllables_per_word': avg_syllables_per_word
        }


class MediaProcessor:
    """    Media processing utilities
    
    Provides image and video processing helper functions.
    """    
    @staticmethod
    def get_image_info(image_path: Union[str, Path]) -> Dict[str, Any]:
        """        Extract comprehensive image information
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary containing image information
        """        try:
            with Image.open(image_path) as img:
                info = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P'),
                    'exif_data': {},
                    'color_profile': None
                }
                
                # Extract EXIF data
                try:
                    if hasattr(img, '_getexif') and img._getexif():
                        exif_data = img._getexif()
                        for tag_id, value in exif_data.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            info['exif_data'][tag] = str(value)
                except Exception:
                    pass
                
                # Get color profile info
                try:
                    if hasattr(img, 'info') and 'icc_profile' in img.info:
                        info['color_profile'] = 'embedded'
                except Exception:
                    pass
                
                return info
                
        except Exception as e:
            logger.error(f"Error extracting image info: {e}")
            return {}
    
    @staticmethod
    def calculate_image_sharpness(image_path: Union[str, Path]) -> float:
        """        Calculate image sharpness using Laplacian variance
        
        Args:
            image_path: Path to the image
            
        Returns:
            Sharpness score (higher = sharper)
        """        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                return 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return float(laplacian_var)
            
        except Exception as e:
            logger.error(f"Error calculating image sharpness: {e}")
            return 0.0
    
    @staticmethod
    def detect_faces(image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """        Detect faces in image
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of face detection results
        """        try:
            # Load OpenCV's face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Convert to list of dictionaries
            face_results = []
            for (x, y, w, h) in faces:
                face_results.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 1.0  # OpenCV cascade doesn't provide confidence
                })
            
            return face_results
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []


class SystemUtils:
    """    System utilities
    
    Provides system information and resource monitoring functions.
    """    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """        Get system information
        
        Returns:
            Dictionary containing system information
        """        import psutil
        
        try:
            info = {
                'cpu_count': os.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {}
            }
            
            # Get disk usage for current directory
            disk_usage = psutil.disk_usage('.')
            info['disk_usage'] = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': (disk_usage.used / disk_usage.total) * 100
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    @staticmethod
    def check_available_memory(required_mb: int = 1024) -> bool:
        """        Check if sufficient memory is available
        
        Args:
            required_mb: Required memory in MB
            
        Returns:
            True if sufficient memory is available
        """        try:
            import psutil
            available_mb = psutil.virtual_memory().available / (1024 * 1024)
            return available_mb >= required_mb
        except Exception:
            return True  # Assume sufficient memory if check fails
    
    @staticmethod
    def check_gpu_availability() -> Dict[str, Any]:
        """        Check GPU availability and information
        
        Returns:
            Dictionary containing GPU information
        """        gpu_info = {
            'available': False,
            'count': 0,
            'devices': []
        }
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info['available'] = True
                gpu_info['count'] = torch.cuda.device_count()
                
                for i in range(gpu_info['count']):
                    device_info = {
                        'id': i,
                        'name': torch.cuda.get_device_name(i),
                        'memory_total': torch.cuda.get_device_properties(i).total_memory,
                        'memory_allocated': torch.cuda.memory_allocated(i),
                        'memory_cached': torch.cuda.memory_reserved(i)
                    }
                    gpu_info['devices'].append(device_info)
        except ImportError:
            pass
        
        return gpu_info


# Utility function shortcuts
def detect_content_type(file_path: Union[str, Path]) -> str:
    """Shortcut for FileValidator.detect_file_type"""    return FileValidator.detect_file_type(file_path)


def validate_file(file_path: Union[str, Path]) -> bool:
    """Shortcut for FileValidator.validate_file_integrity"""    return FileValidator.validate_file_integrity(file_path)


def normalize_score(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Shortcut for DataProcessor.normalize_score"""    return DataProcessor.normalize_score(value, min_val, max_val)


def clean_text(text: str) -> str:
    """Shortcut for TextProcessor.clean_text"""    return TextProcessor.clean_text(text)


# Export all utility classes and functions
__all__ = [
    'FileValidator',
    'DataProcessor',
    'TextProcessor',
    'MediaProcessor',
    'SystemUtils',
    'detect_content_type',
    'validate_file',
    'normalize_score',
    'clean_text'
]
