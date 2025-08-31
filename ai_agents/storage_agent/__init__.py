"""Storage Agent - Enterprise Multi-Backend Storage System
=======================================================

Intelligent storage management system supporting AWS S3, MinIO, local storage,
with automatic file processing, compression, and content optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This storage agent technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices Architect & DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer & Content Protection Specialist: Fahed Mlaiel
"""
from .storage_orchestrator import (
    StorageOrchestrator, StorageStrategy, FileCategory, 
    StorageRequest, StorageResponse
)
from .backend_manager import (
    BackendManager, StorageBackend, StorageConfig, 
    BackendStatus, BackendHealth
)
from .file_processor import (
    FileProcessor, ProcessingType, ProcessingOptions, 
    ProcessingResult, AudioFormat, VideoFormat, ImageFormat
)
from .content_optimizer import (
    ContentOptimizer, OptimizationType, ContentType,
    OptimizationOptions, OptimizationResult
)
from .backup_manager import (
    BackupManager, BackupType, BackupStatus, RestoreStatus,
    BackupConfig, BackupMetadata, RestoreOperation
)
from .index import (
    StorageAgentIndex, create_storage_agent_index, DEFAULT_CONFIG
)

__all__ = [
    # Main orchestrator
    "StorageOrchestrator",
    "StorageStrategy", 
    "FileCategory",
    "StorageRequest",
    "StorageResponse",
    
    # Backend management
    "BackendManager",
    "StorageBackend",
    "StorageConfig", 
    "BackendStatus",
    "BackendHealth",
    
    # File processing
    "FileProcessor",
    "ProcessingType",
    "ProcessingOptions",
    "ProcessingResult",
    "AudioFormat",
    "VideoFormat", 
    "ImageFormat",
    
    # Content optimization
    "ContentOptimizer",
    "OptimizationType",
    "ContentType",
    "OptimizationOptions", 
    "OptimizationResult",
    
    # Backup management
    "BackupManager",
    "BackupType",
    "BackupStatus",
    "RestoreStatus",
    "BackupConfig",
    "BackupMetadata",
    "RestoreOperation",
    
    # Main Index
    "StorageAgentIndex",
    "create_storage_agent_index",
    "DEFAULT_CONFIG"
]

def create_storage_agent(config=None):
    """
    Factory function to create configured storage agent
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        StorageOrchestrator: Configured storage orchestrator instance
    """
    return StorageOrchestrator(config)

def create_backend_manager(config=None):
    """
    Factory function to create backend manager
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        BackendManager: Configured backend manager instance
    """
    return BackendManager(config or {})

def create_file_processor(config=None):
    """
    Factory function to create file processor
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        FileProcessor: Configured file processor instance
    """
    return FileProcessor(config)

def create_content_optimizer(config=None):
    """
    Factory function to create content optimizer
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ContentOptimizer: Configured content optimizer instance
    """
    return ContentOptimizer(config)

def create_backup_manager(config=None):
    """
    Factory function to create backup manager
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        BackupManager: Configured backup manager instance
    """
    return BackupManager(config)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"
