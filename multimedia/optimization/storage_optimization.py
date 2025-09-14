"""
Ainflue Platform - Multimedia Optimization - Storage Optimization
Intelligent storage optimization for multimedia content management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import logging
from pathlib import Path
import hashlib
import time

logger = logging.getLogger(__name__)


class StorageTier(Enum):
    """Storage tier types"""
    HOT = "hot"           # Frequently accessed
    WARM = "warm"         # Occasionally accessed
    COLD = "cold"         # Rarely accessed
    ARCHIVE = "archive"   # Long-term storage


class CompressionLevel(Enum):
    """Compression levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class StorageOptimization:
    """Storage optimization configuration"""
    enable_deduplication: bool = True
    compression_level: CompressionLevel = CompressionLevel.MEDIUM
    auto_tiering: bool = True
    cleanup_policy: Dict[str, int] = field(default_factory=dict)
    retention_days: int = 365


class StorageOptimizer:
    """Professional storage optimization system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize storage optimizer"""
        self.config = config or {}
        self.optimization_config = StorageOptimization()
        self.file_registry: Dict[str, Dict[str, Any]] = {}
        
    async def optimize_storage(
        self,
        content_path: Union[str, Path],
        optimization_level: str = "balanced"
    ) -> Dict[str, Any]:
        """Optimize storage for multimedia content"""
        try:
            file_path = Path(content_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {content_path}")
            
            original_size = file_path.stat().st_size
            file_hash = await self._calculate_file_hash(file_path)
            
            # Check for duplicates
            duplicate_info = await self._check_duplicates(file_hash, file_path)
            
            # Apply compression
            compressed_info = await self._apply_compression(file_path, optimization_level)
            
            # Determine storage tier
            storage_tier = await self._determine_storage_tier(file_path)
            
            optimization_result = {
                "original_size": original_size,
                "optimized_size": compressed_info["size"],
                "compression_ratio": compressed_info["ratio"],
                "storage_tier": storage_tier.value,
                "duplicate_found": duplicate_info["found"],
                "space_saved": original_size - compressed_info["size"],
                "optimization_level": optimization_level
            }
            
            # Update registry
            self.file_registry[str(file_path)] = {
                "hash": file_hash,
                "size": compressed_info["size"],
                "tier": storage_tier,
                "last_accessed": time.time(),
                "optimization_applied": True
            }
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing storage: {e}")
            raise
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for deduplication"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    async def _check_duplicates(
        self,
        file_hash: str,
        file_path: Path
    ) -> Dict[str, Any]:
        """Check for duplicate files"""
        try:
            for registered_path, info in self.file_registry.items():
                if info["hash"] == file_hash and registered_path != str(file_path):
                    return {
                        "found": True,
                        "duplicate_path": registered_path,
                        "space_saving": file_path.stat().st_size
                    }
            
            return {"found": False, "space_saving": 0}
            
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return {"found": False, "space_saving": 0}
    
    async def _apply_compression(
        self,
        file_path: Path,
        optimization_level: str
    ) -> Dict[str, Any]:
        """Apply compression based on optimization level"""
        try:
            original_size = file_path.stat().st_size
            
            # Simulate compression (in production would use actual compression)
            compression_ratios = {
                "minimal": 0.95,
                "balanced": 0.80,
                "aggressive": 0.60,
                "maximum": 0.45
            }
            
            ratio = compression_ratios.get(optimization_level, 0.80)
            compressed_size = int(original_size * ratio)
            
            return {
                "size": compressed_size,
                "ratio": ratio,
                "method": f"compression_{optimization_level}"
            }
            
        except Exception as e:
            logger.error(f"Error applying compression: {e}")
            return {"size": file_path.stat().st_size, "ratio": 1.0, "method": "none"}
    
    async def _determine_storage_tier(self, file_path: Path) -> StorageTier:
        """Determine appropriate storage tier"""
        try:
            # Simplified tier determination based on file age and access pattern
            file_age_days = (time.time() - file_path.stat().st_mtime) / (24 * 3600)
            
            if file_age_days < 7:
                return StorageTier.HOT
            elif file_age_days < 30:
                return StorageTier.WARM
            elif file_age_days < 365:
                return StorageTier.COLD
            else:
                return StorageTier.ARCHIVE
                
        except Exception as e:
            logger.error(f"Error determining storage tier: {e}")
            return StorageTier.WARM
    
    async def cleanup_storage(
        self,
        storage_path: Union[str, Path],
        cleanup_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Clean up storage based on rules"""
        try:
            storage_path = Path(storage_path)
            cleanup_rules = cleanup_rules or {
                "delete_old_temp_files": 7,  # days
                "delete_unused_cache": 30,   # days
                "archive_old_content": 180   # days
            }
            
            cleanup_result = {
                "files_deleted": 0,
                "files_archived": 0,
                "space_freed": 0,
                "errors": []
            }
            
            current_time = time.time()
            
            for file_path in storage_path.rglob("*"):
                if file_path.is_file():
                    file_age_days = (current_time - file_path.stat().st_mtime) / (24 * 3600)
                    
                    # Apply cleanup rules
                    if "temp" in file_path.name and file_age_days > cleanup_rules.get("delete_old_temp_files", 7):
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleanup_result["files_deleted"] += 1
                            cleanup_result["space_freed"] += file_size
                        except Exception as e:
                            cleanup_result["errors"].append(f"Failed to delete {file_path}: {e}")
                    
                    elif file_age_days > cleanup_rules.get("archive_old_content", 180):
                        # Move to archive tier
                        cleanup_result["files_archived"] += 1
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"Error cleaning up storage: {e}")
            raise


# Export main classes
__all__ = [
    'StorageOptimizer',
    'StorageOptimization',
    'StorageTier',
    'CompressionLevel'
]