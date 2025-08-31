"""IA Influencer Agent - Fingerprinting Utilities
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Common utilities and helper functions for fingerprinting operations
"""
import hashlib
import mimetypes
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import numpy as np
from datetime import datetime, timezone
import json
import base64
from functools import wraps

logger = logging.getLogger(__name__)

class FingerprintUtils:
    """    Professional utility class for fingerprinting operations
    Provides common functions and helpers
    """    
    @staticmethod
    def generate_file_hash(file_path: Path) -> str:
        """Generate SHA-256 hash of file content"""        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash for {file_path}: {str(e)}")
            return ""
    
    @staticmethod
    def generate_content_hash(content: Union[str, bytes, np.ndarray]) -> str:
        """Generate SHA-256 hash of content"""        try:
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, np.ndarray):
                content_bytes = content.tobytes()
            else:
                content_bytes = content
            
            return hashlib.sha256(content_bytes).hexdigest()
        except Exception as e:
            logger.error(f"Error generating content hash: {str(e)}")
            return ""
    
    @staticmethod
    def get_file_type(file_path: Path) -> Optional[str]:
        """Determine file type from path and MIME type"""        # File extension mapping
        extension_mapping = {
            # Audio
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.ogg': 'audio',
            '.aac': 'audio', '.m4a': 'audio', '.wma': 'audio',
            
            # Video
            '.mp4': 'video', '.avi': 'video', '.mkv': 'video', '.mov': 'video',
            '.wmv': 'video', '.flv': 'video', '.webm': 'video', '.m4v': 'video',
            
            # Image
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.bmp': 'image', '.tiff': 'image', '.webp': 'image', '.svg': 'image',
            
            # Text
            '.txt': 'text', '.md': 'text', '.rtf': 'text', '.doc': 'text',
            '.docx': 'text', '.pdf': 'text'
        }
        
        # Check extension first
        extension = file_path.suffix.lower()
        if extension in extension_mapping:
            return extension_mapping[extension]
        
        # Fallback to MIME type
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                if mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('text/'):
                    return 'text'
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def normalize_array(array: np.ndarray) -> np.ndarray:
        """Normalize array to [0, 1] range"""        try:
            if array.size == 0:
                return array
            
            min_val = np.min(array)
            max_val = np.max(array)
            
            if max_val == min_val:
                return np.zeros_like(array)
            
            return (array - min_val) / (max_val - min_val)
        except Exception as e:
            logger.error(f"Error normalizing array: {str(e)}")
            return array
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Handle zero vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(np.clip(similarity, 0.0, 1.0))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    @staticmethod
    def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate Euclidean distance between two vectors"""        try:
            if len(vec1) != len(vec2):
                return float('inf')
            
            return float(np.linalg.norm(vec1 - vec2))
        except Exception as e:
            logger.error(f"Error calculating Euclidean distance: {str(e)}")
            return float('inf')
    
    @staticmethod
    def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate Manhattan distance between two vectors"""        try:
            if len(vec1) != len(vec2):
                return float('inf')
            
            return float(np.sum(np.abs(vec1 - vec2)))
        except Exception as e:
            logger.error(f"Error calculating Manhattan distance: {str(e)}")
            return float('inf')
    
    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets"""        try:
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            if union == 0:
                return 1.0 if len(set1) == 0 and len(set2) == 0 else 0.0
            
            return intersection / union
        except Exception as e:
            logger.error(f"Error calculating Jaccard similarity: {str(e)}")
            return 0.0
    
    @staticmethod
    def hamming_distance(str1: str, str2: str) -> int:
        """Calculate Hamming distance between two strings"""        try:
            if len(str1) != len(str2):
                return max(len(str1), len(str2))
            
            return sum(c1 != c2 for c1, c2 in zip(str1, str2))
        except Exception as e:
            logger.error(f"Error calculating Hamming distance: {str(e)}")
            return max(len(str1), len(str2))
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safely divide two numbers, returning default if division by zero"""        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except Exception:
            return default
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            size = float(size_bytes)
            
            while size >= 1024.0 and i < len(size_names) - 1:
                size /= 1024.0
                i += 1
            
            return f"{size:.1f} {size_names[i]}"
        except Exception:
            return f"{size_bytes} B"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""        try:
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = int(seconds // 60)
                seconds = seconds % 60
                return f"{minutes}m {seconds:.1f}s"
            else:
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds = seconds % 60
                return f"{hours}h {minutes}m {seconds:.1f}s"
        except Exception:
            return f"{seconds}s"
    
    @staticmethod
    def serialize_numpy_array(array: np.ndarray) -> str:
        """Serialize numpy array to base64 string"""        try:
            array_bytes = array.tobytes()
            return base64.b64encode(array_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error serializing numpy array: {str(e)}")
            return ""
    
    @staticmethod
    def deserialize_numpy_array(data: str, dtype=np.float64, shape=None) -> Optional[np.ndarray]:
        """Deserialize base64 string to numpy array"""        try:
            array_bytes = base64.b64decode(data.encode('utf-8'))
            array = np.frombuffer(array_bytes, dtype=dtype)
            
            if shape:
                array = array.reshape(shape)
            
            return array
        except Exception as e:
            logger.error(f"Error deserializing numpy array: {str(e)}")
            return None
    
    @staticmethod
    def create_fingerprint_id() -> str:
        """Create unique fingerprint identifier"""        timestamp = int(time.time() * 1000000)  # microseconds
        return f"fp_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}"
    
    @staticmethod
    def validate_threshold(threshold: float) -> bool:
        """Validate threshold value is between 0 and 1"""        return 0.0 <= threshold <= 1.0
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp value between min and max"""        return max(min_value, min(value, max_value))

def timer_decorator(func):
    """Decorator to time function execution"""    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        return sync_wrapper

def retry_decorator(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function execution on failure"""    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
                
                raise last_exception
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
                
                raise last_exception
            return sync_wrapper
    return decorator

class FileTypeDetector:
    """Advanced file type detection"""    
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
    TEXT_EXTENSIONS = {'.txt', '.md', '.rtf', '.doc', '.docx', '.pdf'}
    
    @classmethod
    def is_audio_file(cls, file_path: Path) -> bool:
        """Check if file is audio format"""        return file_path.suffix.lower() in cls.AUDIO_EXTENSIONS
    
    @classmethod
    def is_video_file(cls, file_path: Path) -> bool:
        """Check if file is video format"""        return file_path.suffix.lower() in cls.VIDEO_EXTENSIONS
    
    @classmethod
    def is_image_file(cls, file_path: Path) -> bool:
        """Check if file is image format"""        return file_path.suffix.lower() in cls.IMAGE_EXTENSIONS
    
    @classmethod
    def is_text_file(cls, file_path: Path) -> bool:
        """Check if file is text format"""        return file_path.suffix.lower() in cls.TEXT_EXTENSIONS
    
    @classmethod
    def get_all_supported_extensions(cls) -> set:
        """Get all supported file extensions"""        return cls.AUDIO_EXTENSIONS | cls.VIDEO_EXTENSIONS | cls.IMAGE_EXTENSIONS | cls.TEXT_EXTENSIONS

class DataValidator:
    """Data validation utilities"""    
    @staticmethod
    def validate_similarity_score(score: float) -> bool:
        """Validate similarity score is between 0 and 1"""        return isinstance(score, (int, float)) and 0.0 <= score <= 1.0
    
    @staticmethod
    def validate_file_path(file_path: Path) -> bool:
        """Validate file path exists and is a file"""        try:
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
    
    @staticmethod
    def validate_directory_path(dir_path: Path) -> bool:
        """Validate directory path exists and is a directory"""        try:
            return dir_path.exists() and dir_path.is_dir()
        except Exception:
            return False
    
    @staticmethod
    def validate_numpy_array(array: np.ndarray, min_size: int = 1) -> bool:
        """Validate numpy array is not empty and has minimum size"""        try:
            return isinstance(array, np.ndarray) and array.size >= min_size
        except Exception:
            return False
    
    @staticmethod
    def validate_config_dict(config: Dict[str, Any], required_keys: List[str]) -> bool:
        """Validate configuration dictionary has required keys"""        try:
            return all(key in config for key in required_keys)
        except Exception:
            return False

# Global utility instances
utils = FingerprintUtils()
file_detector = FileTypeDetector()
validator = DataValidator()

# Convenience functions
def hash_content(content: Union[str, bytes, np.ndarray]) -> str:
    """Generate hash of content"""    return utils.generate_content_hash(content)

def get_file_type(file_path: Path) -> Optional[str]:
    """Get file type from path"""    return utils.get_file_type(file_path)

def calculate_similarity(vec1: np.ndarray, vec2: np.ndarray, method: str = 'cosine') -> float:
    """Calculate similarity between vectors using specified method"""    if method == 'cosine':
        return utils.cosine_similarity(vec1, vec2)
    elif method == 'euclidean':
        distance = utils.euclidean_distance(vec1, vec2)
        # Convert distance to similarity (0-1 range)
        return 1.0 / (1.0 + distance)
    elif method == 'manhattan':
        distance = utils.manhattan_distance(vec1, vec2)
        # Convert distance to similarity (0-1 range)
        return 1.0 / (1.0 + distance)
    else:
        raise ValueError(f"Unsupported similarity method: {method}")

def format_results(results: List[Dict[str, Any]]) -> str:
    """Format processing results for display"""    try:
        total = len(results)
        successful = sum(1 for r in results if 'error' not in r)
        duplicates = sum(1 for r in results if r.get('is_duplicate', False))
        
        summary = f"""Processing Summary:
==================
Total files processed: {total}
Successful: {successful}
Failed: {total - successful}
Duplicates found: {duplicates}
Unique content: {successful - duplicates}
        """        
        return summary.strip()
    except Exception as e:
        logger.error(f"Error formatting results: {str(e)}")
        return "Error formatting results"
