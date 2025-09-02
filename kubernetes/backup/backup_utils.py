"""Backup Utilities and Helper Functions for IA Influencer Agent Platform.

Provides utility functions, helpers, and common operations for backup
management, validation, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution is strictly prohibited and will result
in immediate legal action under German and international law.
"""

import asyncio
import logging
import hashlib
import shutil
import tempfile
import gzip
import bz2
import lzma
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Generator
from pathlib import Path
from dataclasses import asdict
import mimetypes
import magic
import psutil

from .backup_config import BackupConfig, CompressionAlgorithm
from .backup_metrics import BackupMetrics, BackupOperationType
from ...core.exceptions import BackupError, ValidationError
from ...core.utils import format_bytes, calculate_checksum


class BackupUtils:
    """
    Utility class providing helper functions for backup operations.
    
    Contains common operations, validation helpers, and optimization
    utilities used across the backup system.
    """
    def __init__(self, config: Optional[BackupConfig] = None):
        """
        Initialize backup utilities.
        
        Args:
            config: Backup configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or BackupConfig()

    @staticmethod
    def calculate_file_checksum(
        file_path: Union[str, Path],
        algorithm: str = "SHA-256"
    ) -> str:
        """
        Calculate file checksum.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (SHA-256, SHA-1, MD5)
            
        Returns:
            File checksum
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        hash_algorithms = {
            "SHA-256": hashlib.sha256,
            "SHA-1": hashlib.sha1,
            "MD5": hashlib.md5
        }
        
        if algorithm not in hash_algorithms:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hasher = hash_algorithms[algorithm]()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            raise BackupError(f"Failed to calculate checksum for {file_path}: {e}")

    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = file_path.stat()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            try:
                mime_type = magic.from_file(str(file_path), mime=True)
            except:
                mime_type = "application/octet-stream"
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size_bytes": stat.st_size,
            "size_formatted": format_bytes(stat.st_size),
            "mime_type": mime_type,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "accessed_at": datetime.fromtimestamp(stat.st_atime),
            "permissions": oct(stat.st_mode)[-3:],
            "is_file": file_path.is_file(),
            "is_directory": file_path.is_dir(),
            "is_symlink": file_path.is_symlink()
        }

    @staticmethod
    def compress_data(
        data: bytes,
        algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP,
        compression_level: int = 6
    ) -> Tuple[bytes, float]:
        """
        Compress data using specified algorithm.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm
            compression_level: Compression level (1-9)
            
        Returns:
            Tuple of (compressed_data, compression_ratio)
        """
        original_size = len(data)
        
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                compressed_data = gzip.compress(data, compresslevel=compression_level)
            elif algorithm == CompressionAlgorithm.BZIP2:
                compressed_data = bz2.compress(data, compresslevel=compression_level)
            elif algorithm == CompressionAlgorithm.LZMA:
                compressed_data = lzma.compress(
                    data, 
                    preset=compression_level,
                    format=lzma.FORMAT_XZ
                )
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")
            
            compressed_size = len(compressed_data)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            return compressed_data, compression_ratio
            
        except Exception as e:
            raise BackupError(f"Compression failed with {algorithm.value}: {e}")

    @staticmethod
    def decompress_data(
        compressed_data: bytes,
        algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP
    ) -> bytes:
        """
        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data
            algorithm: Compression algorithm
            
        Returns:
            Decompressed data
        """
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.decompress(compressed_data)
            elif algorithm == CompressionAlgorithm.BZIP2:
                return bz2.decompress(compressed_data)
            elif algorithm == CompressionAlgorithm.LZMA:
                return lzma.decompress(compressed_data)
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")
                
        except Exception as e:
            raise BackupError(f"Decompression failed with {algorithm.value}: {e}")

    @staticmethod
    def validate_backup_file(backup_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate backup file structure and integrity.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Validation results
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            return {
                "valid": False,
                "errors": [f"Backup file not found: {backup_path}"]
            }
        
        errors = []
        warnings = []
        
        try:
            # Check file size
            file_size = backup_path.stat().st_size
            if file_size == 0:
                errors.append("Backup file is empty")
            elif file_size < 1024:  # Less than 1KB
                warnings.append("Backup file is very small")
            
            # Try to read and parse backup metadata
            try:
                with open(backup_path, 'rb') as f:
                    # Read first few bytes to determine format
                    header = f.read(16)
                    f.seek(0)
                    
                    # Check if it's compressed
                    if header.startswith(b'\x1f\x8b'):  # GZIP
                        data = gzip.decompress(f.read())
                    elif header.startswith(b'BZ'):  # BZIP2
                        data = bz2.decompress(f.read())
                    elif header.startswith(b'\xfd7zXZ'):  # XZ/LZMA
                        data = lzma.decompress(f.read())
                    else:
                        data = f.read()
                
                # Try to parse as JSON
                try:
                    backup_data = json.loads(data.decode('utf-8'))
                    
                    # Validate backup structure
                    required_fields = ["metadata", "backup_timestamp"]
                    for field in required_fields:
                        if field not in backup_data:
                            errors.append(f"Missing required field: {field}")
                    
                    # Check metadata
                    if "metadata" in backup_data:
                        metadata = backup_data["metadata"]
                        if "backup_version" not in metadata:
                            warnings.append("Missing backup version in metadata")
                        if "total_records" not in metadata:
                            warnings.append("Missing total records in metadata")
                
                except json.JSONDecodeError:
                    errors.append("Backup file is not valid JSON")
                
            except Exception as e:
                errors.append(f"Failed to read backup file: {e}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "file_size": file_size,
                "file_path": str(backup_path)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {e}"],
                "warnings": warnings
            }

    @staticmethod
    def estimate_backup_size(
        source_paths: List[Union[str, Path]],
        compression_ratio: float = 0.7
    ) -> Dict[str, Any]:
        """
        Estimate backup size for given source paths.
        
        Args:
            source_paths: List of source paths to backup
            compression_ratio: Expected compression ratio
            
        Returns:
            Size estimation information
        """
        total_size = 0
        file_count = 0
        directory_count = 0
        errors = []
        
        for source_path in source_paths:
            source_path = Path(source_path)
            
            try:
                if source_path.is_file():
                    total_size += source_path.stat().st_size
                    file_count += 1
                elif source_path.is_dir():
                    directory_count += 1
                    for file_path in source_path.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                            file_count += 1
                        elif file_path.is_dir():
                            directory_count += 1
                else:
                    errors.append(f"Path not found or invalid: {source_path}")
                    
            except Exception as e:
                errors.append(f"Error processing {source_path}: {e}")
        
        estimated_compressed_size = int(total_size * compression_ratio)
        
        return {
            "original_size_bytes": total_size,
            "original_size_formatted": format_bytes(total_size),
            "estimated_compressed_size_bytes": estimated_compressed_size,
            "estimated_compressed_size_formatted": format_bytes(estimated_compressed_size),
            "compression_ratio": compression_ratio,
            "file_count": file_count,
            "directory_count": directory_count,
            "errors": errors
        }

    @staticmethod
    def get_system_resources() -> Dict[str, Any]:
        """
        Get current system resource usage.
        
        Returns:
            System resource information
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            
            # Network stats
            network_stats = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": cpu_count
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_bytes": disk_usage.total,
                    "free_bytes": disk_usage.free,
                    "used_bytes": disk_usage.used,
                    "usage_percent": (disk_usage.used / disk_usage.total) * 100
                },
                "network": {
                    "bytes_sent": network_stats.bytes_sent,
                    "bytes_received": network_stats.bytes_recv,
                    "packets_sent": network_stats.packets_sent,
                    "packets_received": network_stats.packets_recv
                }
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get system resources: {e}"
            }

    @staticmethod
    def optimize_backup_schedule(
        historical_data: List[Dict[str, Any]],
        resource_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize backup schedule based on historical data and constraints.
        
        Args:
            historical_data: Historical backup performance data
            resource_constraints: System resource constraints
            
        Returns:
            Optimized schedule recommendations
        """
        if not historical_data:
            return {
                "recommendations": [],
                "reason": "No historical data available"
            }
        
        recommendations = []
        
        # Analyze historical performance
        durations = [item.get("duration_seconds", 0) for item in historical_data]
        throughputs = [item.get("throughput_mbps", 0) for item in historical_data]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            # Recommend based on duration patterns
            if avg_duration > 3600:  # More than 1 hour
                recommendations.append({
                    "type": "schedule_adjustment",
                    "suggestion": "Consider running backups during off-peak hours",
                    "reason": f"Average backup duration is {avg_duration/3600:.1f} hours"
                })
            
            if max_duration > avg_duration * 2:
                recommendations.append({
                    "type": "performance_optimization",
                    "suggestion": "Investigate performance bottlenecks",
                    "reason": "High variance in backup durations detected"
                })
        
        if throughputs:
            avg_throughput = sum(throughputs) / len(throughputs)
            
            if avg_throughput < 5.0:  # Less than 5 MB/s
                recommendations.append({
                    "type": "throughput_optimization",
                    "suggestion": "Consider optimizing network or storage performance",
                    "reason": f"Low average throughput: {avg_throughput:.1f} MB/s"
                })
        
        # Resource-based recommendations
        memory_limit = resource_constraints.get("memory_limit_gb", 8)
        if memory_limit < 4:
            recommendations.append({
                "type": "resource_optimization",
                "suggestion": "Increase memory allocation for backup operations",
                "reason": f"Current memory limit ({memory_limit}GB) may be insufficient"
            })
        
        return {
            "recommendations": recommendations,
            "analysis": {
                "avg_duration_minutes": sum(durations) / len(durations) / 60 if durations else 0,
                "avg_throughput_mbps": sum(throughputs) / len(throughputs) if throughputs else 0,
                "data_points_analyzed": len(historical_data)
            }
        }

    @staticmethod
    def create_backup_manifest(
        backup_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create comprehensive backup manifest.
        
        Args:
            backup_data: Backup data dictionary
            metadata: Backup metadata
            
        Returns:
            Backup manifest
        """
        manifest = {
            "manifest_version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            "backup_id": metadata.get("backup_id", "unknown"),
            "backup_type": metadata.get("backup_type", "unknown"),
            "metadata": metadata,
            "contents": {},
            "checksums": {},
            "statistics": {
                "total_size_bytes": 0,
                "file_count": 0,
                "component_count": 0
            }
        }
        
        # Analyze backup contents
        total_size = 0
        file_count = 0
        component_count = len(backup_data)
        
        for component_name, component_data in backup_data.items():
            if isinstance(component_data, dict):
                component_info = {
                    "type": "component",
                    "size_bytes": len(json.dumps(component_data, default=str).encode()),
                    "record_count": len(component_data) if isinstance(component_data, dict) else 1,
                    "checksum": hashlib.sha256(
                        json.dumps(component_data, sort_keys=True, default=str).encode()
                    ).hexdigest()
                }
                
                manifest["contents"][component_name] = component_info
                manifest["checksums"][component_name] = component_info["checksum"]
                
                total_size += component_info["size_bytes"]
                if "record_count" in component_info:
                    file_count += component_info["record_count"]
        
        # Update statistics
        manifest["statistics"].update({
            "total_size_bytes": total_size,
            "total_size_formatted": format_bytes(total_size),
            "file_count": file_count,
            "component_count": component_count
        })
        
        return manifest

    def cleanup_temporary_files(self, temp_dir: Optional[str] = None) -> int:
        """
        Clean up temporary backup files.
        
        Args:
            temp_dir: Temporary directory to clean (optional)
            
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        
        # Default temp directory
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        temp_path = Path(temp_dir)
        
        try:
            # Look for backup-related temp files
            patterns = [
                "backup_temp_*",
                "ia_backup_*",
                "restore_temp_*",
                "*.backup.tmp"
            ]
            
            for pattern in patterns:
                for temp_file in temp_path.glob(pattern):
                    try:
                        # Check if file is older than 1 hour
                        if temp_file.stat().st_mtime < (datetime.now() - timedelta(hours=1)).timestamp():
                            if temp_file.is_file():
                                temp_file.unlink()
                                cleaned_count += 1
                            elif temp_file.is_dir():
                                shutil.rmtree(temp_file)
                                cleaned_count += 1
                                
                    except Exception as e:
                        self.logger.warning(f"Failed to clean temp file {temp_file}: {e}")
            
            self.logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Temp file cleanup failed: {e}")
            return 0

    @staticmethod
    def validate_backup_chain(backup_chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate backup chain consistency.
        
        Args:
            backup_chain: List of backup metadata in chronological order
            
        Returns:
            Validation results
        """
        if not backup_chain:
            return {
                "valid": False,
                "errors": ["Empty backup chain"]
            }
        
        errors = []
        warnings = []
        
        # Sort by creation time
        sorted_chain = sorted(backup_chain, key=lambda x: x.get("created_at", ""))
        
        # Validate chain structure
        full_backups = [b for b in sorted_chain if b.get("backup_type") == "full"]
        incremental_backups = [b for b in sorted_chain if b.get("backup_type") == "incremental"]
        
        if not full_backups:
            errors.append("No full backup found in chain")
        
        # Check incremental backup dependencies
        for backup in incremental_backups:
            base_backup_id = None
            for tag in backup.get("tags", []):
                if tag.startswith("base:"):
                    base_backup_id = tag.split("base:")[1]
                    break
            
            if base_backup_id:
                base_exists = any(
                    b.get("backup_id") == base_backup_id for b in sorted_chain
                )
                if not base_exists:
                    errors.append(f"Base backup {base_backup_id} not found for incremental backup {backup.get('backup_id')}")
        
        # Check for gaps in timeline
        if len(sorted_chain) > 1:
            for i in range(1, len(sorted_chain)):
                prev_backup = sorted_chain[i-1]
                curr_backup = sorted_chain[i]
                
                try:
                    prev_time = datetime.fromisoformat(prev_backup.get("created_at", ""))
                    curr_time = datetime.fromisoformat(curr_backup.get("created_at", ""))
                    
                    gap_hours = (curr_time - prev_time).total_seconds() / 3600
                    
                    if gap_hours > 168:  # More than 1 week gap
                        warnings.append(f"Large time gap ({gap_hours:.1f} hours) between backups")
                        
                except Exception:
                    warnings.append("Invalid timestamp format in backup metadata")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "chain_length": len(sorted_chain),
            "full_backups": len(full_backups),
            "incremental_backups": len(incremental_backups),
            "date_range": {
                "earliest": sorted_chain[0].get("created_at") if sorted_chain else None,
                "latest": sorted_chain[-1].get("created_at") if sorted_chain else None
            }
        }


# Utility functions for common operations
def format_backup_size(size_bytes: int) -> str:
    """Format backup size in human-readable format."""
    return format_bytes(size_bytes)


def generate_backup_id(operation_type: str = "backup") -> str:
    """Generate unique backup identifier."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{operation_type}_{timestamp}"


def parse_backup_id(backup_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"Executing parse_backup_id")
            
            # Implementation for parse_backup_id
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"parse_backup_id completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"parse_backup_id failed: {e}")
            raise
        "operation_type": "unknown",
        "timestamp": None,
        "date": None,
        "time": None
    }


async def async_file_copy(
    source_path: Union[str, Path],
    target_path: Union[str, Path],
    chunk_size: int = 64 * 1024
) -> None:
    """
    Asynchronous file copy with progress tracking.
    
    Args:
        source_path: Source file path
        target_path: Target file path
        chunk_size: Copy chunk size in bytes
    """
    source_path = Path(source_path)
    target_path = Path(target_path)
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    def copy_chunks():
        with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                dst.write(chunk)
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, copy_chunks)


def validate_backup_path(path: Union[str, Path]) -> bool:
        try:
            logger.info(f"Executing copy_chunks")
            
            # Implementation for copy_chunks
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"copy_chunks completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"copy_chunks failed: {e}")
            raise
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, copy_chunks)


def validate_backup_path(path: Union[str, Path]) -> bool:
    """
Validate backup file path."""
    path = Path(path)
    
    # Check if path is valid
    try:
        path.resolve()
    except Exception:
        return False
    
    # Check parent directory exists or can be created
    parent = path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            return False
    
    return True


def get_backup_file_extension(compression_algorithm: CompressionAlgorithm) -> str:
    """
Get appropriate file extension for backup file."""
    extensions = {
        CompressionAlgorithm.GZIP: ".backup.gz",
        CompressionAlgorithm.BZIP2: ".backup.bz2",
        CompressionAlgorithm.LZMA: ".backup.xz",
        CompressionAlgorithm.ZSTD: ".backup.zst",
        CompressionAlgorithm.LZ4: ".backup.lz4"
    }
    
    return extensions.get(compression_algorithm, ".backup")


# Export utility functions and classes
__all__ = [
    "BackupUtils",
    "format_backup_size",
    "generate_backup_id", 
    "parse_backup_id",
    "async_file_copy",
    "validate_backup_path",
    "get_backup_file_extension"
]
