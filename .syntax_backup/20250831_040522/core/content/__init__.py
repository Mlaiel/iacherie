"""Core Content Management Module - IA Influencer Agent Platform
================================================================

This module provides the core content management functionality for the IA Influencer Agent platform,
implementing multi-format content processing, protection, and monetization according to the unified
business requirements specification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited.

Expert Team Specialties:
- Lead AI Developer & Architect
- Senior Backend Engineer  
- ML/AI Engineer
- Audio Processing Specialist
- DevOps Engineer
- Database Administrator
- Security Engineer
- Microservices Architect

Business Logic Flow:
User (Creator) → Upload Multi-Format → IA Protection & Rights → SEO Optimization → 
Matching & Collaboration → Distribution Multi-Platforms → Monetization Tracking
"""
from .manager import ContentManager
from .processor import ContentProcessor
from .validator import ContentValidator
from .analyzer import ContentAnalyzer
from .optimizer import ContentOptimizer
from .distributor import ContentDistributor
from .tracker import ContentTracker
from .indexer import ContentIndexer
from .classifier import ContentClassifier
from .transformer import ContentTransformer
from .aggregator import ContentAggregator
from .synchronizer import ContentSynchronizer
from .composer import ContentComposer
from .scheduler import ContentScheduler
from .monitor import ContentMonitor
from .auditor import ContentAuditor
from .enhancer import ContentEnhancer
from .migrator import ContentMigrator
from .deployer import ContentDeployer
from .versioner import ContentVersioner

# Import the main system interface
from .index import ContentManagementSystem, ContentSystemStatus, create_content_system

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    "ContentManager",
    "ContentProcessor", 
    "ContentValidator",
    "ContentAnalyzer",
    "ContentOptimizer",
    "ContentDistributor",
    "ContentTracker",
    "ContentIndexer",
    "ContentClassifier",
    "ContentTransformer",
    "ContentAggregator", 
    "ContentSynchronizer",
    "ContentComposer",
    "ContentScheduler",
    "ContentMonitor",
    "ContentAuditor",
    "ContentEnhancer",
    "ContentMigrator",
    "ContentDeployer",
    "ContentVersioner"
]

# Core Content Types
SUPPORTED_CONTENT_TYPES = {
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "text": [".txt", ".md", ".doc", ".docx", ".pdf", ".rtf"],
    "document": [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"]
}

# Business Logic Configuration
CONTENT_WORKFLOW_STAGES = [
    "upload",
    "validation", 
    "analysis",
    "protection",
    "optimization",
    "classification",
    "distribution",
    "monetization",
    "tracking"
]

# Performance Metrics
PERFORMANCE_TARGETS = {
    "processing_time": 500,  # milliseconds
    "accuracy_threshold": 0.95,
    "availability_sla": 0.9999,
    "throughput_min": 1000  # requests per minute
}

# Export all public interfaces
__all__ = [
    # Core components
    "ContentManager",
    "ContentProcessor", 
    "ContentValidator",
    "ContentAnalyzer",
    "ContentOptimizer",
    "ContentDistributor",
    "ContentTracker",
    "ContentIndexer",
    "ContentClassifier",
    "ContentTransformer",
    "ContentAggregator",
    "ContentSynchronizer",
    
    # Main system interface
    "ContentManagementSystem",
    "ContentSystemStatus",
    "create_content_system",
    
    # Constants
    "SUPPORTED_CONTENT_TYPES",
    "CONTENT_WORKFLOW_STAGES",
    "PERFORMANCE_TARGETS"
]
    "throughput_limit": 10000  # items per minute
}
