"""🔧 Utility Functions for Content Fingerprinting System
======================================================

Comprehensive utility functions for multi-modal content fingerprinting,
including file handling, data processing, similarity calculations, and optimization tools.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""
import os
import hashlib
import mimetypes
import tempfile
import shutil
import pickle
import json
import gzip
import base64
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from functools import wraps, lru_cache
from contextlib import contextmanager
from datetime import datetime, timedelta
import warnings

import numpy as np
import cv2
import librosa
import PIL.Image as PILImage
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import normalize
import torch
import torch.nn.functional as F
from scipy.spatial.distance import hamming, jaccard
from scipy import signal
import faiss

from .models import ContentType, ProcessingMetrics, QualityMetrics

# Configure logging
logger = logging.getLogger(__name__)

class FileHandler:
    """Advanced file handling utilities for content fingerprinting."""
    
    SUPPORTED_AUDIO_FORMATS = {
        '.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.opus'
    }
    
    SUPPORTED_VIDEO_FORMATS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'
    }
    
    SUPPORTED_IMAGE_FORMATS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'
    }
    
    SUPPORTED_TEXT_FORMATS = {
        '.txt', '.doc', '.docx', '.pdf', '.rtf', '.md', '.html', '.xml', '.json'
    }
    
    @staticmethod
    def detect_content_type(file_path: str) -> ContentType:
        """Detect content type from file extension and MIME type."""
        ext = Path(file_path).suffix.lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if ext in FileHandler.SUPPORTED_AUDIO_FORMATS:
            return ContentType.AUDIO
        elif ext in FileHandler.SUPPORTED_VIDEO_FORMATS:
            return ContentType.VIDEO
        elif ext in FileHandler.SUPPORTED_IMAGE_FORMATS:
            return ContentType.IMAGE
        elif ext in FileHandler.SUPPORTED_TEXT_FORMATS:
            return ContentType.TEXT
        elif mime_type:
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                return ContentType.TEXT
        
        raise ValueError(f"Unsupported file type: {ext} (MIME: {mime_type})")
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'filename': path.name,
            'extension': path.suffix.lower(),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'mime_type': mimetypes.guess_type(file_path)[0],
            'content_type': FileHandler.detect_content_type(file_path),
            'checksum': FileHandler.calculate_checksum(file_path)
        }
    
    @staticmethod
    def calculate_checksum(file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file checksum."""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def validate_file(file_path: str, max_size_mb: int = 500) -> bool:
        """Validate file exists and meets size requirements."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File too large: {size_mb:.1f}MB > {max_size_mb}MB")
        
        return True
    
    @staticmethod
    @contextmanager
    def temp_file(suffix: str = '', prefix: str = 'fingerprint_'):
        """Create temporary file context manager."""
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        try:
            os.close(fd)
            yield temp_path
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

class DataProcessor:
    """Data processing utilities for different content types."""
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_sr: int = 22050) -> np.ndarray:
        """Normalize audio data."""
        # Normalize amplitude
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)
        
        # Normalize to [-1, 1]
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        return audio_data
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Resize image while maintaining aspect ratio."""
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center image
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        start_x = (target_w - new_w) // 2
        start_y = (target_h - new_h) // 2
        canvas[start_y:start_y + new_h, start_x:start_x + new_w] = resized
        
        return canvas
    
    @staticmethod
    def extract_video_frames(video_path: str, max_frames: int = 100) -> List[np.ndarray]:
        """Extract representative frames from video."""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= max_frames:
            frame_indices = list(range(total_frames))
        else:
            # Sample frames evenly
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
        
        frames = []
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        cap.release()
        return frames
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text data."""
        import re
        import unicodedata
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        
        # Strip and return
        return text.strip()
    
    @staticmethod
    def split_text_chunks(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for processing."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks

class SimilarityCalculator:
    """Advanced similarity calculation utilities."""
    
    @staticmethod
    def cosine_similarity_np(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        return np.dot(vec1_norm, vec2_norm)
    
    @staticmethod
    def euclidean_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate normalized euclidean similarity."""
        distance = np.linalg.norm(vec1 - vec2)
        # Normalize to [0, 1] range
        max_distance = np.linalg.norm(vec1) + np.linalg.norm(vec2)
        return 1 - (distance / (max_distance + 1e-8))
    
    @staticmethod
    def hamming_similarity(hash1: str, hash2: str) -> float:
        """Calculate Hamming similarity for hash strings."""
        if len(hash1) != len(hash2):
            return 0.0
        
        diff_count = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        return 1 - (diff_count / len(hash1))
    
    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def weighted_similarity(similarities: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted average of multiple similarities."""
        if not similarities or not weights:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for method, similarity in similarities.items():
            weight = weights.get(method, 1.0)
            weighted_sum += similarity * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to measure function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = wrapper(*args, **kwargs)
            end_time = time.time()
            
            logger.debug(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
            return result
        
        return wrapper
    
    @staticmethod
    def memory_efficient_batch_process(items: List[Any], batch_size: int = 32) -> List[List[Any]]:
        """Split items into memory-efficient batches."""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    @staticmethod
    def optimize_numpy_operations():
        """Optimize NumPy operations for performance."""
        # Enable Intel MKL optimizations if available
        try:
            import mkl
            mkl.set_num_threads(os.cpu_count())
        except ImportError:
            pass
        
        # Set NumPy thread count
        os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())
        os.environ['NUMEXPR_NUM_THREADS'] = str(os.cpu_count())

class VectorDatabase:
    """FAISS-based vector database for efficient similarity search."""
    
    def __init__(self, dimension: int, index_type: str = 'IndexFlatIP'):
        self.dimension = dimension
        self.index_type = index_type
        self.index = self._create_index()
        self.id_map = {}  # Map FAISS indices to fingerprint IDs
        self.metadata = {}  # Store metadata for each vector
    
    def _create_index(self) -> faiss.Index:
        """Create FAISS index based on type."""
        if self.index_type == 'IndexFlatIP':
            return faiss.IndexFlatIP(self.dimension)
        elif self.index_type == 'IndexFlatL2':
            return faiss.IndexFlatL2(self.dimension)
        elif self.index_type == 'IndexIVFFlat':
            quantizer = faiss.IndexFlatL2(self.dimension)
            return faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == 'IndexHNSWFlat':
            return faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
    
    def add_vector(self, vector: np.ndarray, fingerprint_id: str, metadata: Dict[str, Any] = None):
        """Add vector to the database."""
        if vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension {vector.shape[0]} != {self.dimension}")
        
        # Normalize vector for cosine similarity
        if self.index_type == 'IndexFlatIP':
            vector = normalize(vector.reshape(1, -1), norm='l2')[0]
        
        # Add to index
        current_idx = self.index.ntotal
        self.index.add(vector.reshape(1, -1).astype(np.float32))
        
        # Store mappings
        self.id_map[current_idx] = fingerprint_id
        if metadata:
            self.metadata[fingerprint_id] = metadata
    
    def search(self, query_vector: np.ndarray, k: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if query_vector.shape[0] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[0]} != {self.dimension}")
        
        # Normalize query vector
        if self.index_type == 'IndexFlatIP':
            query_vector = normalize(query_vector.reshape(1, -1), norm='l2')[0]
        
        # Search
        scores, indices = self.index.search(query_vector.reshape(1, -1).astype(np.float32), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # No more results
                break
            
            if score >= threshold:
                fingerprint_id = self.id_map.get(idx)
                if fingerprint_id:
                    result = {
                        'fingerprint_id': fingerprint_id,
                        'similarity_score': float(score),
                        'metadata': self.metadata.get(fingerprint_id, {})
                    }
                    results.append(result)
        
        return results
    
    def save(self, filepath: str):
        """Save index to disk."""
        faiss.write_index(self.index, filepath)
        
        # Save metadata separately
        metadata_file = filepath + '.metadata'
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'id_map': self.id_map,
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)
    
    def load(self, filepath: str):
        """Load index from disk."""
        self.index = faiss.read_index(filepath)
        
        # Load metadata
        metadata_file = filepath + '.metadata'
        with open(metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.id_map = data['id_map']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']

class ConfigManager:
    """Configuration management for fingerprinting system."""
    
    DEFAULT_CONFIG = {
        'audio': {
            'sample_rate': 22050,
            'n_mfcc': 13,
            'n_chroma': 12,
            'n_fft': 2048,
            'hop_length': 512,
            'chromaprint_duration': 120
        },
        'video': {
            'max_frames': 100,
            'frame_size': (224, 224),
            'motion_threshold': 0.1,
            'scene_threshold': 0.3
        },
        'image': {
            'hash_size': 8,
            'target_size': (224, 224),
            'clip_model': 'ViT-B/32'
        },
        'text': {
            'max_length': 512,
            'chunk_size': 512,
            'chunk_overlap': 50,
            'bert_model': 'sentence-transformers/all-MiniLM-L6-v2'
        },
        'similarity': {
            'default_threshold': 0.8,
            'algorithm_weights': {
                'perceptual_hash': 0.3,
                'neural_embedding': 0.4,
                'traditional_features': 0.3
            }
        },
        'performance': {
            'batch_size': 32,
            'max_workers': 4,
            'gpu_memory_fraction': 0.8,
            'cache_size': 1000
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load configuration from file."""
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            self._merge_config(self.config, user_config)
    
    def save_config(self, config_path: str):
        """Save configuration to file."""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _merge_config(self, base_config: Dict, user_config: Dict):
        """Recursively merge user config into base config."""
        for key, value in user_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

class CacheManager:
    """Intelligent caching system for fingerprinting operations."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.creation_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.creation_times[key] > self.ttl_seconds:
            self._remove(key)
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        current_time = time.time()
        self.cache[key] = value
        self.access_times[key] = current_time
        self.creation_times[key] = current_time
    
    def _remove(self, key: str):
        """Remove key from cache."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.creation_times.pop(key, None)
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times, key=self.access_times.get)
        self._remove(lru_key)
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.access_times.clear()
        self.creation_times.clear()

# Utility decorators and functions

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator to retry function on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator

@lru_cache(maxsize=128)
def get_optimal_batch_size(content_type: ContentType, available_memory_gb: float = 8.0) -> int:
    """Calculate optimal batch size based on content type and available memory."""
    base_sizes = {
        ContentType.AUDIO: 16,
        ContentType.VIDEO: 4,
        ContentType.IMAGE: 32,
        ContentType.TEXT: 64
    }
    
    base_size = base_sizes.get(content_type, 16)
    memory_factor = min(available_memory_gb / 4.0, 4.0)  # Scale based on memory
    
    return int(base_size * memory_factor)

def setup_gpu_environment():
    """Setup optimal GPU environment for fingerprinting."""
    if torch.cuda.is_available():
        # Set memory fraction
        torch.cuda.set_per_process_memory_fraction(0.8)
        
        # Enable cuDNN benchmarking
        torch.backends.cudnn.benchmark = True
        
        logger.info(f"GPU setup complete. Using {torch.cuda.get_device_name(0)}")
        return True
    
    logger.warning("No GPU available. Using CPU.")
    return False

def validate_fingerprint_quality(fingerprint_data: Dict[str, Any], 
                                content_type: ContentType) -> QualityMetrics:
    """Validate and assess fingerprint quality."""
    quality_scores = {}
    quality_flags = []
    
    # Check data completeness
    required_fields = {
        ContentType.AUDIO: ['chromaprint', 'essentia', 'spectral'],
        ContentType.VIDEO: ['perceptual_frames', 'motion_analysis'],
        ContentType.IMAGE: ['perceptual_hash', 'clip_embedding'],
        ContentType.TEXT: ['bert_embedding', 'tfidf_vector']
    }
    
    required = required_fields.get(content_type, [])
    present = [field for field in required if fingerprint_data.get(field) is not None]
    completeness = len(present) / len(required) if required else 1.0
    
    # Check data validity
    confidence = 0.8  # Base confidence
    reliability = 0.9  # Base reliability
    uniqueness = 0.7   # Base uniqueness
    
    # Adjust based on data quality
    if completeness < 0.5:
        quality_flags.append("low_completeness")
        confidence *= 0.7
    
    if completeness < 0.8:
        quality_flags.append("missing_algorithms")
        reliability *= 0.8
    
    return QualityMetrics(
        confidence_score=confidence,
        reliability_score=reliability,
        completeness_score=completeness,
        uniqueness_score=uniqueness,
        algorithm_scores=quality_scores,
        quality_flags=quality_flags
    )

# Export all utilities
__all__ = [
    'FileHandler', 'DataProcessor', 'SimilarityCalculator', 'PerformanceOptimizer',
    'VectorDatabase', 'ConfigManager', 'CacheManager',
    'retry_on_failure', 'get_optimal_batch_size', 'setup_gpu_environment',
    'validate_fingerprint_quality'
]
