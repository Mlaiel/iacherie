"""
Vector Database Utilities and Helper Functions
==============================================

Comprehensive utility functions for the vector database system including
validation, optimization, data processing, and system maintenance helpers.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Developer + Backend Senior Engineer: Fahed Mlaiel
- ML Engineer + Data Scientist: Advanced algorithms & optimization
- Database Administrator + Performance Specialist: Scalability & efficiency  
- Security Engineer + DevOps Engineer: System security & deployment
- Audio Processing Specialist: Audio fingerprinting & analysis
- Computer Vision Engineer: Image/video processing & recognition
- Microservices Architect: Distributed systems & API design
"""

import os
import json
import hashlib
import asyncio
import logging
import pickle
import gzip
import tempfile
import shutil
import time
import psutil
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


@dataclass
class SystemResourceInfo:
    """System resource information."""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    gpu_available: bool
    gpu_memory_gb: Optional[float] = None


@dataclass
class DataProcessingStats:
    """Statistics for data processing operations."""
    total_items: int
    processed_items: int
    failed_items: int
    processing_time_seconds: float
    throughput_items_per_second: float
    error_rate_percent: float


@dataclass
class ValidationResult:
    """Result of data validation operations."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_score: float


class ContentHashGenerator:
    """
    Generates consistent hashes for different content types.
    Used for deduplication and content identification.
    """
    
    @staticmethod
    def hash_text(text: str, algorithm: str = 'sha256') -> str:
        """Generate hash for text content."""
        if not text:
            return ""
        
        # Normalize text (lowercase, strip whitespace)
        normalized_text = text.lower().strip()
        
        # Create hash
        hasher = hashlib.new(algorithm)
        hasher.update(normalized_text.encode('utf-8'))
        
        return hasher.hexdigest()
    
    @staticmethod
    def hash_audio(audio_data: np.ndarray, sample_rate: int = 22050, algorithm: str = 'sha256') -> str:
        """Generate hash for audio content."""
        if audio_data is None or len(audio_data) == 0:
            return ""
        
        # Normalize audio data
        normalized_audio = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
        
        # Convert to bytes for hashing
        audio_bytes = normalized_audio.astype(np.float32).tobytes()
        
        # Include sample rate in hash
        hasher = hashlib.new(algorithm)
        hasher.update(str(sample_rate).encode('utf-8'))
        hasher.update(audio_bytes)
        
        return hasher.hexdigest()
    
    @staticmethod
    def hash_image(image: Union[Image.Image, np.ndarray], algorithm: str = 'sha256') -> str:
        """Generate hash for image content."""
        if image is None:
            return ""
        
        try:
            # Convert PIL Image to array if needed
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image
            
            # Normalize to standard size for consistent hashing
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB image
                image_resized = np.array(Image.fromarray(image_array).resize((64, 64)))
            else:
                # Grayscale or other format
                if len(image_array.shape) == 3:
                    image_array = np.mean(image_array, axis=2)
                image_resized = np.array(Image.fromarray(image_array.astype(np.uint8)).resize((64, 64)))
            
            # Convert to bytes
            image_bytes = image_resized.astype(np.uint8).tobytes()
            
            hasher = hashlib.new(algorithm)
            hasher.update(image_bytes)
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"Error hashing image: {str(e)}")
            return ""
    
    @staticmethod
    def hash_metadata(metadata: Dict[str, Any], algorithm: str = 'sha256') -> str:
        """Generate hash for metadata."""
        if not metadata:
            return ""
        
        # Sort keys for consistent hashing
        sorted_metadata = dict(sorted(metadata.items()))
        metadata_string = json.dumps(sorted_metadata, sort_keys=True, default=str)
        
        hasher = hashlib.new(algorithm)
        hasher.update(metadata_string.encode('utf-8'))
        
        return hasher.hexdigest()


class DataValidator:
    """
    Validates data integrity and format for vector database operations.
    """
    
    @staticmethod
    def validate_text_content(text: str, max_length: Optional[int] = None) -> ValidationResult:
        """Validate text content."""
        errors = []
        warnings = []
        
        # Check if text exists
        if not text or not isinstance(text, str):
            errors.append("Text content is required and must be a string")
            return ValidationResult(False, errors, warnings, 0.0)
        
        # Check length
        if max_length and len(text) > max_length:
            errors.append(f"Text length ({len(text)}) exceeds maximum ({max_length})")
        
        # Check for suspicious content
        if len(text.strip()) < 3:
            warnings.append("Text content is very short")
        
        # Check encoding
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            errors.append("Text contains invalid UTF-8 characters")
        
        # Calculate validation score
        score = 1.0
        if errors:
            score = 0.0
        elif warnings:
            score = 0.7
        
        return ValidationResult(len(errors) == 0, errors, warnings, score)
    
    @staticmethod
    def validate_audio_data(audio_data: np.ndarray, sample_rate: int) -> ValidationResult:
        """Validate audio data."""
        errors = []
        warnings = []
        
        # Check if audio data exists
        if audio_data is None or not isinstance(audio_data, np.ndarray):
            errors.append("Audio data is required and must be numpy array")
            return ValidationResult(False, errors, warnings, 0.0)
        
        # Check shape
        if len(audio_data.shape) not in [1, 2]:
            errors.append("Audio data must be 1D or 2D array")
        
        # Check data type
        if not np.issubdtype(audio_data.dtype, np.floating):
            warnings.append("Audio data should be floating point")
        
        # Check for NaN or inf values
        if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
            errors.append("Audio data contains NaN or infinite values")
        
        # Check sample rate
        if sample_rate <= 0 or sample_rate > 192000:
            errors.append(f"Invalid sample rate: {sample_rate}")
        
        # Check duration
        duration = len(audio_data) / sample_rate
        if duration > 600:  # 10 minutes
            warnings.append(f"Audio duration is very long: {duration:.1f} seconds")
        elif duration < 0.1:
            warnings.append(f"Audio duration is very short: {duration:.3f} seconds")
        
        # Calculate validation score
        score = 1.0
        if errors:
            score = 0.0
        elif warnings:
            score = 0.8
        
        return ValidationResult(len(errors) == 0, errors, warnings, score)
    
    @staticmethod
    def validate_image_data(image: Union[Image.Image, np.ndarray]) -> ValidationResult:
        """Validate image data."""
        errors = []
        warnings = []
        
        # Check if image exists
        if image is None:
            errors.append("Image data is required")
            return ValidationResult(False, errors, warnings, 0.0)
        
        try:
            # Convert to PIL Image for validation
            if isinstance(image, np.ndarray):
                if len(image.shape) not in [2, 3]:
                    errors.append("Image array must be 2D or 3D")
                    return ValidationResult(False, errors, warnings, 0.0)
                
                if len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]:
                    errors.append("Image must have 1, 3, or 4 channels")
                
                # Convert to PIL Image
                if image.dtype != np.uint8:
                    if np.max(image) <= 1.0:
                        image = (image * 255).astype(np.uint8)
                    else:
                        image = image.astype(np.uint8)
                
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Check image properties
            width, height = pil_image.size
            
            if width < 32 or height < 32:
                warnings.append(f"Image is very small: {width}x{height}")
            elif width > 4096 or height > 4096:
                warnings.append(f"Image is very large: {width}x{height}")
            
            # Check format
            if hasattr(pil_image, 'format'):
                if pil_image.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'TIFF']:
                    warnings.append(f"Unusual image format: {pil_image.format}")
            
        except Exception as e:
            errors.append(f"Error processing image: {str(e)}")
        
        # Calculate validation score
        score = 1.0
        if errors:
            score = 0.0
        elif warnings:
            score = 0.8
        
        return ValidationResult(len(errors) == 0, errors, warnings, score)
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> ValidationResult:
        """Validate metadata."""
        errors = []
        warnings = []
        
        if not isinstance(metadata, dict):
            errors.append("Metadata must be a dictionary")
            return ValidationResult(False, errors, warnings, 0.0)
        
        # Check for required fields
        if 'content_id' not in metadata:
            warnings.append("Missing content_id in metadata")
        
        # Check for suspicious keys
        for key in metadata.keys():
            if not isinstance(key, str):
                errors.append(f"Metadata key must be string: {type(key)}")
            elif len(key) > 100:
                warnings.append(f"Very long metadata key: {key[:50]}...")
        
        # Check values
        for key, value in metadata.items():
            if value is None:
                warnings.append(f"Null value for key: {key}")
            elif isinstance(value, (list, dict)) and len(str(value)) > 1000:
                warnings.append(f"Very large metadata value for key: {key}")
        
        # Calculate validation score
        score = 1.0
        if errors:
            score = 0.0
        elif warnings:
            score = 0.9
        
        return ValidationResult(len(errors) == 0, errors, warnings, score)


class PerformanceProfiler:
    """
    Performance profiling utilities for vector database operations.
    """
    
    def __init__(self):
        self.operation_times = {}
        self.memory_snapshots = {}
        self.active_operations = {}
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation."""
        operation_id = f"{operation_name}_{time.time()}"
        self.active_operations[operation_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'start_memory': psutil.virtual_memory().percent
        }
        return operation_id
    
    def end_operation(self, operation_id: str) -> Dict[str, Any]:
        """End timing an operation and return metrics."""
        if operation_id not in self.active_operations:
            return {}
        
        operation = self.active_operations[operation_id]
        end_time = time.time()
        end_memory = psutil.virtual_memory().percent
        
        metrics = {
            'operation_name': operation['name'],
            'duration_seconds': end_time - operation['start_time'],
            'memory_change_percent': end_memory - operation['start_memory'],
            'start_memory_percent': operation['start_memory'],
            'end_memory_percent': end_memory
        }
        
        # Store metrics
        if operation['name'] not in self.operation_times:
            self.operation_times[operation['name']] = []
        
        self.operation_times[operation['name']].append(metrics)
        
        # Clean up
        del self.active_operations[operation_id]
        
        return metrics
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        if operation_name not in self.operation_times:
            return {}
        
        times = [op['duration_seconds'] for op in self.operation_times[operation_name]]
        memory_changes = [op['memory_change_percent'] for op in self.operation_times[operation_name]]
        
        return {
            'operation_name': operation_name,
            'total_calls': len(times),
            'avg_duration': np.mean(times),
            'min_duration': np.min(times),
            'max_duration': np.max(times),
            'std_duration': np.std(times),
            'avg_memory_change': np.mean(memory_changes),
            'total_duration': np.sum(times)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations."""
        return {
            operation_name: self.get_operation_stats(operation_name)
            for operation_name in self.operation_times.keys()
        }


class FileSystemUtils:
    """
    File system utilities for vector database storage and management.
    """
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> bool:
        """Ensure a directory exists, creating it if necessary."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {str(e)}")
            return False
    
    @staticmethod
    def safe_file_write(filepath: Union[str, Path], data: Union[str, bytes], backup: bool = True) -> bool:
        """Safely write data to a file with optional backup."""
        try:
            filepath = Path(filepath)
            
            # Create backup if requested and file exists
            if backup and filepath.exists():
                backup_path = filepath.with_suffix(filepath.suffix + '.backup')
                shutil.copy2(filepath, backup_path)
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_file = filepath.with_suffix(filepath.suffix + '.tmp')
            
            if isinstance(data, str):
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(data)
            else:
                with open(temp_file, 'wb') as f:
                    f.write(data)
            
            # Atomic move
            shutil.move(temp_file, filepath)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def get_directory_size(path: Union[str, Path]) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error calculating directory size: {str(e)}")
        
        return total_size
    
    @staticmethod
    def cleanup_old_files(directory: Union[str, Path], max_age_days: int = 7) -> int:
        """Remove files older than specified age."""
        removed_count = 0
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        try:
            for filepath in Path(directory).rglob('*'):
                if filepath.is_file() and filepath.stat().st_mtime < cutoff_time:
                    filepath.unlink()
                    removed_count += 1
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
        
        return removed_count


class DataSerialization:
    """
    Data serialization utilities with compression and validation.
    """
    
    @staticmethod
    def serialize_with_compression(data: Any, compression_level: int = 6) -> bytes:
        """Serialize data with gzip compression."""
        try:
            # Pickle the data
            pickled_data = pickle.dumps(data)
            
            # Compress with gzip
            compressed_data = gzip.compress(pickled_data, compresslevel=compression_level)
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Serialization failed: {str(e)}")
            raise
    
    @staticmethod
    def deserialize_with_compression(data: bytes) -> Any:
        """Deserialize compressed data."""
        try:
            # Decompress
            decompressed_data = gzip.decompress(data)
            
            # Unpickle
            original_data = pickle.loads(decompressed_data)
            
            return original_data
            
        except Exception as e:
            logger.error(f"Deserialization failed: {str(e)}")
            raise
    
    @staticmethod
    def serialize_to_json(data: Any, indent: Optional[int] = None) -> str:
        """Serialize data to JSON with custom handling for numpy arrays."""
        def json_serializer(obj):
            if isinstance(obj, np.ndarray):
                return {
                    '__numpy_array__': True,
                    'data': obj.tolist(),
                    'dtype': str(obj.dtype),
                    'shape': obj.shape
                }
            elif isinstance(obj, (datetime, np.datetime64)):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
        
        return json.dumps(data, default=json_serializer, indent=indent)
    
    @staticmethod
    def deserialize_from_json(json_str: str) -> Any:
        """Deserialize JSON with custom handling for numpy arrays."""
        def json_deserializer(obj):
            if isinstance(obj, dict) and obj.get('__numpy_array__', False):
                return np.array(obj['data'], dtype=obj['dtype']).reshape(obj['shape'])
            return obj
        
        data = json.loads(json_str)
        
        # Recursively process the data
        def process_dict(d):
            if isinstance(d, dict):
                if d.get('__numpy_array__', False):
                    return np.array(d['data'], dtype=d['dtype']).reshape(d['shape'])
                else:
                    return {k: process_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [process_dict(item) for item in d]
            else:
                return d
        
        return process_dict(data)


class SystemResourceMonitor:
    """
    Monitor system resources for optimal vector database performance.
    """
    
    @staticmethod
    def get_system_info() -> SystemResourceInfo:
        """Get current system resource information."""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        disk_free = disk.free / (1024**3)  # GB
        
        # GPU check (basic)
        gpu_available = False
        gpu_memory = None
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        except ImportError:
            pass
        
        return SystemResourceInfo(
            cpu_usage_percent=cpu_usage,
            memory_usage_percent=memory_usage,
            memory_available_gb=memory_available,
            disk_usage_percent=disk_usage,
            disk_free_gb=disk_free,
            gpu_available=gpu_available,
            gpu_memory_gb=gpu_memory
        )
    
    @staticmethod
    def check_resource_constraints(min_memory_gb: float = 1.0, max_cpu_percent: float = 90.0) -> Tuple[bool, List[str]]:
        """Check if system meets resource constraints."""
        info = SystemResourceMonitor.get_system_info()
        issues = []
        
        if info.memory_available_gb < min_memory_gb:
            issues.append(f"Low memory: {info.memory_available_gb:.1f}GB available, need {min_memory_gb}GB")
        
        if info.cpu_usage_percent > max_cpu_percent:
            issues.append(f"High CPU usage: {info.cpu_usage_percent:.1f}%")
        
        if info.disk_free_gb < 1.0:
            issues.append(f"Low disk space: {info.disk_free_gb:.1f}GB free")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def suggest_optimizations(info: SystemResourceInfo) -> List[str]:
        """Suggest optimizations based on system resources."""
        suggestions = []
        
        if info.memory_usage_percent > 80:
            suggestions.append("Consider reducing batch size or enabling memory optimization")
        
        if info.cpu_usage_percent > 70:
            suggestions.append("Consider reducing parallel processing threads")
        
        if info.disk_free_gb < 5:
            suggestions.append("Clean up old backups and temporary files")
        
        if not info.gpu_available:
            suggestions.append("Consider using GPU acceleration for better performance")
        elif info.gpu_memory_gb and info.gpu_memory_gb < 4:
            suggestions.append("GPU memory is limited - reduce model size if using GPU acceleration")
        
        return suggestions


# Utility Functions

def generate_unique_id(prefix: str = "", timestamp: bool = True) -> str:
    """Generate a unique identifier."""
    import uuid
    
    unique_part = str(uuid.uuid4())[:8]
    
    if timestamp:
        timestamp_part = str(int(time.time()))
        unique_id = f"{prefix}_{timestamp_part}_{unique_part}" if prefix else f"{timestamp_part}_{unique_part}"
    else:
        unique_id = f"{prefix}_{unique_part}" if prefix else unique_part
    
    return unique_id


def normalize_similarity_score(score: float, method: str = 'minmax') -> float:
    """Normalize similarity score to [0, 1] range."""
    if method == 'minmax':
        # Assume input is cosine similarity [-1, 1]
        return (score + 1) / 2
    elif method == 'sigmoid':
        return 1 / (1 + np.exp(-score))
    else:
        return max(0, min(1, score))


def calculate_content_diversity(embeddings: List[np.ndarray]) -> float:
    """Calculate diversity score for a collection of embeddings."""
    if len(embeddings) < 2:
        return 0.0
    
    # Calculate pairwise distances
    distances = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Cosine distance
            cosine_sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            distance = 1 - cosine_sim
            distances.append(distance)
    
    # Return average distance as diversity score
    return np.mean(distances)


def estimate_storage_requirements(vector_count: int, dimension: int, metadata_size_kb: float = 1.0) -> Dict[str, float]:
    """Estimate storage requirements for vector database."""
    # Vector storage (float32)
    vector_size_mb = (vector_count * dimension * 4) / (1024 * 1024)
    
    # Metadata storage
    metadata_size_mb = (vector_count * metadata_size_kb) / 1024
    
    # Index overhead (estimated 20% for FAISS)
    index_overhead_mb = vector_size_mb * 0.2
    
    total_size_mb = vector_size_mb + metadata_size_mb + index_overhead_mb
    
    return {
        'vector_data_mb': vector_size_mb,
        'metadata_mb': metadata_size_mb,
        'index_overhead_mb': index_overhead_mb,
        'total_mb': total_size_mb,
        'total_gb': total_size_mb / 1024
    }


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


# Export utilities
__all__ = [
    'SystemResourceInfo',
    'DataProcessingStats',
    'ValidationResult',
    'ContentHashGenerator',
    'DataValidator',
    'PerformanceProfiler',
    'FileSystemUtils',
    'DataSerialization',
    'SystemResourceMonitor',
    'generate_unique_id',
    'normalize_similarity_score',
    'calculate_content_diversity',
    'estimate_storage_requirements',
    'format_bytes',
    'format_duration'
]
