"""Local Storage Configuration for IA-Influencer Agent Platform
===========================================================

Professional local file system storage configuration for development and self-hosted deployments.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import hashlib
import json

@dataclass
class LocalDirectoryConfig:
    """Local directory configuration for specific content types."""
    
    path: str
    permissions: int = 0o755
    max_size_gb: Optional[float] = None
    auto_cleanup: bool = False
    cleanup_days: int = 30
    encryption_enabled: bool = False

@dataclass
class LocalStorageConfig:
    """
    Comprehensive Local Storage configuration for IA-Influencer Agent platform.
    Provides enterprise-grade local file system management with security and optimization.
    """
    
    # Base storage settings
    base_path: str = os.getenv('LOCAL_STORAGE_PATH', '/var/lib/ia-influencer')
    temp_path: str = os.getenv('TEMP_STORAGE_PATH', '/tmp/ia-influencer')
    
    # Directory configurations
    directories: Dict[str, LocalDirectoryConfig] = None
    
    # Security settings
    enable_encryption: bool = True
    encryption_key: Optional[str] = os.getenv('LOCAL_STORAGE_ENCRYPTION_KEY')
    file_permissions: int = 0o644
    directory_permissions: int = 0o755
    
    # Performance settings
    enable_compression: bool = True
    compression_level: int = 6  # gzip compression level
    chunk_size: int = 64 * 1024  # 64KB chunks for file operations
    
    # Monitoring settings
    enable_checksums: bool = True
    checksum_algorithm: str = 'sha256'
    enable_file_watching: bool = True
    
    # Cleanup settings
    enable_auto_cleanup: bool = True
    default_cleanup_days: int = 30
    max_storage_size_gb: float = 100.0
    
    def __post_init__(self):
        """Initialize directory configurations if not provided."""
        if self.directories is None:
            self.directories = self._get_default_directory_config()
        
        # Ensure base paths exist
        self._ensure_base_directories()
    
    def _get_default_directory_config(self) -> Dict[str, LocalDirectoryConfig]:
        """Default directory configuration for different content types."""
        env = os.getenv('ENVIRONMENT', 'development')
        
        return {
            'audio_files': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'audio'),
                permissions=0o755,
                max_size_gb=20.0,
                auto_cleanup=True,
                cleanup_days=90,
                encryption_enabled=self.enable_encryption
            ),
            'video_files': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'video'),
                permissions=0o755,
                max_size_gb=50.0,
                auto_cleanup=True,
                cleanup_days=180,
                encryption_enabled=self.enable_encryption
            ),
            'image_files': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'images'),
                permissions=0o755,
                max_size_gb=10.0,
                auto_cleanup=False,
                encryption_enabled=False  # Images often served directly
            ),
            'document_files': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'documents'),
                permissions=0o750,  # More restrictive
                max_size_gb=5.0,
                auto_cleanup=False,
                encryption_enabled=self.enable_encryption
            ),
            'ml_models': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'models'),
                permissions=0o755,
                max_size_gb=15.0,
                auto_cleanup=False,  # Models are permanent
                encryption_enabled=True  # Always encrypt models
            ),
            'fingerprint_data': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'fingerprints'),
                permissions=0o750,
                max_size_gb=5.0,
                auto_cleanup=True,
                cleanup_days=365,  # Keep for 1 year
                encryption_enabled=True
            ),
            'user_uploads': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'uploads'),
                permissions=0o755,
                max_size_gb=10.0,
                auto_cleanup=True,
                cleanup_days=7,  # Temporary uploads
                encryption_enabled=self.enable_encryption
            ),
            'processed_content': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'processed'),
                permissions=0o755,
                max_size_gb=30.0,
                auto_cleanup=True,
                cleanup_days=60,
                encryption_enabled=self.enable_encryption
            ),
            'backup_data': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'backups'),
                permissions=0o700,  # Highly restrictive
                max_size_gb=20.0,
                auto_cleanup=True,
                cleanup_days=2555,  # 7 years
                encryption_enabled=True
            ),
            'temp_files': LocalDirectoryConfig(
                path=self.temp_path,
                permissions=0o755,
                max_size_gb=5.0,
                auto_cleanup=True,
                cleanup_days=1,  # Daily cleanup
                encryption_enabled=False  # Temp files
            ),
            'logs': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'logs'),
                permissions=0o750,
                max_size_gb=2.0,
                auto_cleanup=True,
                cleanup_days=90,
                encryption_enabled=False
            ),
            'cache': LocalDirectoryConfig(
                path=os.path.join(self.base_path, 'cache'),
                permissions=0o755,
                max_size_gb=5.0,
                auto_cleanup=True,
                cleanup_days=7,
                encryption_enabled=False
            )
        }
    
    def _ensure_base_directories(self):
        """Ensure all base directories exist with proper permissions."""
        for dir_config in self.directories.values():
            path = Path(dir_config.path)
            path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            path.chmod(dir_config.permissions)
    
    def get_directory_path(self, content_type: str) -> str:
        """Get directory path for specific content type."""
        # Map content types to directory keys
        content_mapping = {
            'audio': 'audio_files',
            'video': 'video_files',
            'image': 'image_files',
            'document': 'document_files',
            'model': 'ml_models',
            'fingerprint': 'fingerprint_data',
            'upload': 'user_uploads',
            'processed': 'processed_content',
            'backup': 'backup_data',
            'temp': 'temp_files',
            'log': 'logs',
            'cache': 'cache'
        }
        
        dir_key = content_mapping.get(content_type, 'user_uploads')
        return self.directories[dir_key].path
    
    def get_content_types(self) -> List[str]:
        """Get list of supported content types."""
        return ['audio', 'video', 'image', 'document', 'model', 
                'fingerprint', 'upload', 'processed', 'backup', 
                'temp', 'log', 'cache']
    
    def validate_configuration(self) -> bool:
        """Validate local storage configuration and accessibility."""
        try:
            for content_type, dir_config in self.directories.items():
                path = Path(dir_config.path)
                
                # Check if directory exists and is writable
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                
                if not os.access(path, os.W_OK):
                    print(f"Directory not writable: {path}")
                    return False
                
                # Check available space
                if dir_config.max_size_gb:
                    free_space_gb = shutil.disk_usage(path).free / (1024**3)
                    if free_space_gb < dir_config.max_size_gb * 0.1:  # 10% margin
                        print(f"Insufficient disk space for {content_type}")
                        return False
            
            return True
        except Exception as e:
            print(f"Local storage validation failed: {e}")
            return False
    
    def get_file_path(self, content_type: str, filename: str, 
                      user_id: Optional[str] = None) -> str:
        """Generate full file path with optional user segregation."""
        base_dir = self.get_directory_path(content_type)
        
        if user_id:
            # Create user-specific subdirectory
            user_dir = os.path.join(base_dir, user_id)
            Path(user_dir).mkdir(parents=True, exist_ok=True)
            return os.path.join(user_dir, filename)
        
        return os.path.join(base_dir, filename)
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate file checksum for integrity verification."""
        hash_func = hashlib.new(self.checksum_algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def get_directory_size(self, directory_path: str) -> float:
        """Get directory size in GB."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        return total_size / (1024**3)  # Convert to GB
    
    def cleanup_old_files(self, content_type: str, force: bool = False):
        """Clean up old files based on directory configuration."""
        dir_config = self.directories.get(f"{content_type}_files")
        if not dir_config or (not dir_config.auto_cleanup and not force):
            return
        
        directory_path = dir_config.path
        cleanup_days = dir_config.cleanup_days
        
        import time
        current_time = time.time()
        cutoff_time = current_time - (cleanup_days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up old file: {file_path}")
                    except OSError as e:
                        print(f"Error cleaning up {file_path}: {e}")
    
    def get_storage_statistics(self) -> Dict[str, Dict[str, Union[float, int]]]:
        """Get storage statistics for all directories."""
        stats = {}
        
        for content_type, dir_config in self.directories.items():
            directory_path = dir_config.path
            
            if os.path.exists(directory_path):
                # Calculate directory size
                size_gb = self.get_directory_size(directory_path)
                
                # Count files
                file_count = sum(len(files) for _, _, files in os.walk(directory_path))
                
                # Calculate usage percentage
                usage_pct = 0
                if dir_config.max_size_gb:
                    usage_pct = (size_gb / dir_config.max_size_gb) * 100
                
                stats[content_type] = {
                    'size_gb': round(size_gb, 2),
                    'file_count': file_count,
                    'max_size_gb': dir_config.max_size_gb or 0,
                    'usage_percentage': round(usage_pct, 1),
                    'auto_cleanup': dir_config.auto_cleanup,
                    'cleanup_days': dir_config.cleanup_days
                }
        
        return stats
    
    def export_configuration(self) -> Dict:
        """Export configuration to JSON-serializable format."""
        return {
            'base_path': self.base_path,
            'temp_path': self.temp_path,
            'enable_encryption': self.enable_encryption,
            'enable_compression': self.enable_compression,
            'compression_level': self.compression_level,
            'chunk_size': self.chunk_size,
            'enable_checksums': self.enable_checksums,
            'checksum_algorithm': self.checksum_algorithm,
            'directories': {
                name: {
                    'path': config.path,
                    'permissions': oct(config.permissions),
                    'max_size_gb': config.max_size_gb,
                    'auto_cleanup': config.auto_cleanup,
                    'cleanup_days': config.cleanup_days,
                    'encryption_enabled': config.encryption_enabled
                }
                for name, config in self.directories.items()
            }
        }

# Global local storage configuration instance
local_storage_config = LocalStorageConfig()
