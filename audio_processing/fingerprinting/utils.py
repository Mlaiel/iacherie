"""
Utility functions and helper classes for audio fingerprinting system.
Professional utility collection for common operations and data transformations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.
"""

import os
import hashlib
import mimetypes
import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import librosa
from concurrent.futures import ThreadPoolExecutor
import json
import base64
import zlib
from functools import wraps
import inspect
from datetime import datetime, timezone
import tempfile
import shutil

logger = logging.getLogger(__name__)


@dataclass
class AudioMetadata:
    """Container for comprehensive audio metadata."""
    
    filename: str
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    bit_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None
    checksum_md5: Optional[str] = None
    checksum_sha256: Optional[str] = None


class FileValidator:
    """
    Advanced file validation and security checking.
    Ensures safe processing of uploaded audio files.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the file validator."""
        self.config = config or self._default_config()
        
        # Supported MIME types
        self.supported_mime_types = {
            'audio/mpeg': ['mp3'],
            'audio/wav': ['wav'],
            'audio/x-wav': ['wav'],
            'audio/flac': ['flac'],
            'audio/mp4': ['m4a', 'mp4'],
            'audio/aac': ['aac'],
            'audio/ogg': ['ogg'],
            'audio/x-ms-wma': ['wma'],
            'audio/vorbis': ['ogg']
        }
        
        logger.debug("FileValidator initialized")
    
    def _default_config(self) -> Dict:
        """Default validation configuration."""



        return {
            'max_file_size_mb': 100.0,
            'min_file_size_bytes': 1024,  # 1KB minimum
            'max_duration_seconds': 1800,  # 30 minutes
            'min_duration_seconds': 0.5,   # 0.5 seconds
            'require_metadata_validation': True,
            'enable_malware_scanning': False,  # Would require additional tools
            'allowed_extensions': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg', 'wma'],
            'blocked_extensions': ['exe', 'bat', 'sh', 'scr', 'com', 'pif']
        }
    
    async def validate_file(self, file_path: str) -> Tuple[bool, List[str], Optional[AudioMetadata]]:
        """
        Comprehensive file validation.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (is_valid, error_messages, metadata)
        """
        errors = []
        metadata = None
        
        try:
            file_path_obj = Path(file_path)
            
            # Basic file existence check
            if not file_path_obj.exists():
                errors.append("File does not exist")
                return False, errors, None
            
            # File size validation
            file_size = file_path_obj.stat().st_size
            max_size_bytes = self.config['max_file_size_mb'] * 1024 * 1024
            
            if file_size > max_size_bytes:
                errors.append(f"File size {file_size} exceeds maximum {max_size_bytes} bytes")
            
            if file_size < self.config['min_file_size_bytes']:
                errors.append(f"File size {file_size} below minimum {self.config['min_file_size_bytes']} bytes")
            
            # Extension validation
            extension = file_path_obj.suffix.lower().lstrip('.')
            
            if extension in self.config['blocked_extensions']:
                errors.append(f"File extension '{extension}' is blocked for security")
                return False, errors, None
            
            if extension not in self.config['allowed_extensions']:
                errors.append(f"File extension '{extension}' is not supported")
            
            # MIME type validation
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type and mime_type not in self.supported_mime_types:
                errors.append(f"MIME type '{mime_type}' is not supported")
            
            # Audio file validation
            try:
                metadata = await self._extract_audio_metadata(file_path)
                
                # Duration validation
                if metadata.duration_seconds > self.config['max_duration_seconds']:
                    errors.append(f"Duration {metadata.duration_seconds}s exceeds maximum {self.config['max_duration_seconds']}s")
                
                if metadata.duration_seconds < self.config['min_duration_seconds']:
                    errors.append(f"Duration {metadata.duration_seconds}s below minimum {self.config['min_duration_seconds']}s")
                
                # Audio quality checks
                if metadata.sample_rate < 8000:
                    errors.append("Sample rate too low (minimum 8kHz)")
                
                if metadata.channels < 1 or metadata.channels > 8:
                    errors.append(f"Invalid number of channels: {metadata.channels}")
                
            except Exception as e:
                errors.append(f"Failed to read audio metadata: {str(e)}")
            
            # Security scanning (if enabled)
            if self.config['enable_malware_scanning']:
                security_issues = await self._scan_for_security_issues(file_path)
                errors.extend(security_issues)
            
            is_valid = len(errors) == 0
            return is_valid, errors, metadata
            
        except Exception as e:
            logger.error("Error validating file %s: %s", file_path, str(e))
            errors.append(f"Validation error: {str(e)}")
            return False, errors, None
    
    async def _extract_audio_metadata(self, file_path: str) -> AudioMetadata:
        """Extract comprehensive audio metadata."""
        loop = asyncio.get_event_loop()
        
        def _extract_sync():
            # Use librosa to get audio properties
            try:
                y, sr = librosa.load(file_path, sr=None, mono=False)
                
                # Handle mono vs stereo
                if y.ndim == 1:
                    duration = len(y) / sr
                    channels = 1
                else:
                    duration = y.shape[1] / sr
                    channels = y.shape[0]
                
                # File system metadata
                file_path_obj = Path(file_path)
                file_stats = file_path_obj.stat()
                
                # Calculate checksums
                md5_hash = self._calculate_file_hash(file_path, 'md5')
                sha256_hash = self._calculate_file_hash(file_path, 'sha256')
                
                metadata = AudioMetadata(
                    filename=file_path_obj.name,
                    file_path=str(file_path_obj.absolute()),
                    file_size_bytes=file_stats.st_size,
                    duration_seconds=duration,
                    sample_rate=sr,
                    channels=channels,
                    format=file_path_obj.suffix.lower().lstrip('.'),
                    creation_time=datetime.fromtimestamp(file_stats.st_ctime, tz=timezone.utc),
                    modification_time=datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc),
                    checksum_md5=md5_hash,
                    checksum_sha256=sha256_hash
                )
                
                return metadata
                
            except Exception as e:
                logger.error("Error extracting audio metadata: %s", str(e))
                raise
        
        return await loop.run_in_executor(None, _extract_sync)
    
    def _calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash using specified algorithm."""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    async def _scan_for_security_issues(self, file_path: str) -> List[str]:
        """Basic security scanning for malicious content."""
        issues = []
        
        try:
            # Check for embedded scripts or executables in metadata
            # This is a simplified check - production would use dedicated tools
            
            with open(file_path, 'rb') as f:
                # Read first 1KB for magic number checks
                header = f.read(1024)
                
                # Look for suspicious patterns
                suspicious_patterns = [
                    b'MZ',  # Windows executable
                    b'\x7fELF',  # Linux executable
                    b'#!/bin/',  # Script shebang
                    b'<script',  # HTML script tag
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in header:
                        issues.append(f"Suspicious pattern detected: {pattern}")
            
        except Exception as e:
            logger.warning("Security scan error: %s", str(e))
        
        return issues


class DataSerializer:
    """
    Advanced data serialization utilities for fingerprinting data.
    Handles compression, encoding, and secure data transformation.
    """
    
    def __init__(self, compression_level: int = 6):
        """Initialize the data serializer."""
        self.compression_level = compression_level
        
    def serialize_features(self, features: np.ndarray, compress: bool = True) -> str:
        """
        Serialize numpy array features to string.
        
        Args:
            features: Numpy array to serialize
            compress: Whether to apply compression
            
        Returns:
            Base64-encoded string representation
        """



        try:
            # Convert to bytes
            features_bytes = features.tobytes()
            
            # Add metadata for reconstruction
            metadata = {
                'shape': features.shape,
                'dtype': str(features.dtype),
                'compressed': compress
            }
            
            # Combine metadata and data
            data_package = {
                'metadata': metadata,
                'data': features_bytes
            }
            
            # Serialize to JSON then to bytes
            json_data = json.dumps(data_package, default=self._json_serializer).encode('utf-8')
            
            # Apply compression if requested
            if compress:
                json_data = zlib.compress(json_data, self.compression_level)
            
            # Encode to base64 for safe string storage
            encoded_data = base64.b64encode(json_data).decode('ascii')
            
            return encoded_data
            
        except Exception as e:
            logger.error("Error serializing features: %s", str(e))
            raise
    
    def deserialize_features(self, serialized_data: str) -> np.ndarray:
        """
        Deserialize string back to numpy array.
        
        Args:
            serialized_data: Base64-encoded serialized features
            
        Returns:
            Reconstructed numpy array
        """



        try:
            # Decode from base64
            json_data = base64.b64decode(serialized_data.encode('ascii'))
            
            # Decompress if needed (detect automatically)
            try:
                decompressed = zlib.decompress(json_data)
                json_data = decompressed
            except zlib.error:
                # Data wasn't compressed
                pass
            
            # Parse JSON
            data_package = json.loads(json_data.decode('utf-8'))
            
            metadata = data_package['metadata']
            features_bytes = data_package['data']
            
            # Convert bytes back to numpy array
            if isinstance(features_bytes, str):
                features_bytes = features_bytes.encode('latin1')
            
            features = np.frombuffer(features_bytes, dtype=metadata['dtype'])
            features = features.reshape(metadata['shape'])
            
            return features
            
        except Exception as e:
            logger.error("Error deserializing features: %s", str(e))
            raise
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for numpy and other objects."""
        if isinstance(obj, bytes):
            return obj.decode('latin1')
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class PerformanceMonitor:
    """
    Performance monitoring and profiling utilities.
    Tracks execution time, memory usage, and system resources.
    """
    
    def __init__(self, enable_detailed_profiling: bool = False):
        """Initialize the performance monitor."""
        self.enable_detailed_profiling = enable_detailed_profiling
        self.metrics = {}
        self.operation_counts = {}
        
    def measure_execution_time(self, operation_name: str = None):
        """Decorator to measure function execution time."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    
                    op_name = operation_name or func.__name__
                    self._record_metric(op_name, 'execution_time', execution_time)
                    
                    logger.debug("Operation %s completed in %.3fs", op_name, execution_time)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    
                    op_name = operation_name or func.__name__
                    self._record_metric(op_name, 'execution_time', execution_time)
                    
                    logger.debug("Operation %s completed in %.3fs", op_name, execution_time)
            
            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def _record_metric(self, operation: str, metric_type: str, value: float):
        """Record a performance metric."""
        if operation not in self.metrics:
            self.metrics[operation] = {}
        
        if metric_type not in self.metrics[operation]:
            self.metrics[operation][metric_type] = []
        
        self.metrics[operation][metric_type].append(value)
        
        # Track operation counts
        if operation not in self.operation_counts:
            self.operation_counts[operation] = 0
        self.operation_counts[operation] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {}
        
        for operation, metrics in self.metrics.items():
            op_summary = {
                'count': self.operation_counts.get(operation, 0)
            }
            
            for metric_type, values in metrics.items():
                if values:
                    op_summary[metric_type] = {
                        'avg': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'total': sum(values) if metric_type == 'execution_time' else None
                    }
            
            summary[operation] = op_summary
        
        return summary
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        self.metrics.clear()
        self.operation_counts.clear()


class TemporaryFileManager:
    """
    Safe temporary file management for audio processing.
    Handles cleanup and secure temporary file operations.
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the temporary file manager."""
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.temp_files = []
        
    def create_temp_file(self, suffix: str = '.tmp', prefix: str = 'audio_') -> str:
        """
        Create a temporary file with automatic cleanup tracking.
        
        Args:
            suffix: File suffix/extension
            prefix: File name prefix
            
        Returns:
            Path to the temporary file
        """



        try:
            # Create temporary file
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix, 
                prefix=prefix, 
                dir=self.temp_dir
            )
            os.close(fd)  # Close the file descriptor
            
            # Track for cleanup
            self.temp_files.append(temp_path)
            
            logger.debug("Created temporary file: %s", temp_path)
            return temp_path
            
        except Exception as e:
            logger.error("Error creating temporary file: %s", str(e))
            raise
    
    def create_temp_directory(self, prefix: str = 'audio_processing_') -> str:
        """
        Create a temporary directory.
        
        Args:
            prefix: Directory name prefix
            
        Returns:
            Path to the temporary directory
        """



        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir)
            self.temp_files.append(temp_dir)
            
            logger.debug("Created temporary directory: %s", temp_dir)
            return temp_dir
            
        except Exception as e:
            logger.error("Error creating temporary directory: %s", str(e))
            raise
    
    def cleanup(self):
        """Clean up all temporary files and directories."""
        for temp_path in self.temp_files:
            try:
                if os.path.isfile(temp_path):
                    os.unlink(temp_path)
                    logger.debug("Removed temporary file: %s", temp_path)
                elif os.path.isdir(temp_path):
                    shutil.rmtree(temp_path)
                    logger.debug("Removed temporary directory: %s", temp_path)
            except Exception as e:
                logger.warning("Error removing temporary file %s: %s", temp_path, str(e))
        
        self.temp_files.clear()
    
    def __enter__(self):
        """Context manager entry."""



        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {minutes}m {remaining_seconds:.1f}s"


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create a safe filename by removing/replacing dangerous characters.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename string
    """
    # Remove dangerous characters
    safe_chars = []
    dangerous_chars = '<>:"/\\|?*'
    
    for char in filename:
        if char in dangerous_chars:
            safe_chars.append('_')
        elif ord(char) < 32:  # Control characters
            safe_chars.append('_')
        else:
            safe_chars.append(char)
    
    safe_name = ''.join(safe_chars)
    
    # Trim to max length
    if len(safe_name) > max_length:
        name_part, ext_part = os.path.splitext(safe_name)
        max_name_len = max_length - len(ext_part)
        safe_name = name_part[:max_name_len] + ext_part
    
    return safe_name


def generate_unique_id(prefix: str = '', suffix: str = '') -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix
        suffix: Optional suffix
        
    Returns:
        Unique identifier string
    """
    timestamp = str(int(time.time() * 1000000))  # Microseconds
    random_part = hashlib.sha256(os.urandom(32)).hexdigest()[:8]
    
    unique_id = f"{prefix}{timestamp}_{random_part}{suffix}"
    return unique_id


class BatchProcessor:
    """
    Utility for processing items in batches with progress tracking.
    Handles both synchronous and asynchronous batch operations.
    """
    
    def __init__(self, batch_size: int = 10, max_workers: int = 4):
        """Initialize the batch processor."""
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_async_batches(
        self, 
        items: List[Any], 
        processor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> List[Any]:
        """
        Process items in async batches.
        
        Args:
            items: List of items to process
            processor_func: Async function to process each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed results
        """
        results = []
        total_items = len(items)
        
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            
            # Process batch concurrently
            batch_tasks = [processor_func(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.warning("Batch processing error: %s", str(result))
                    results.append(None)
                else:
                    results.append(result)
            
            # Progress callback
            if progress_callback:
                progress = min(i + self.batch_size, total_items) / total_items
                await progress_callback(progress, i + len(batch), total_items)
        
        return results
    
    def cleanup(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
