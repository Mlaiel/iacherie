"""🗄️ Data Management Module - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Data Management - Enterprise Production-Ready
Responsibility: Gestion avancée des données multi-format et protection contenu
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER DATA MANAGEMENT:
Upload Multi-Format → Validation Avancée → Transformation Intelligente → 
Indexation Vectorielle → Stockage Optimisé → Analytics Real-time → 
Protection IA → Archivage Automatique → Gouvernance Compliance

SUPPORTS FORMATS:
🎵 Audio: MP3, WAV, FLAC, OGG, M4A, AIFF (Musiciens)
🎬 Vidéo: MP4, AVI, MOV, MKV, WEBM, FLV (Influenceurs/Comédiens)
📸 Images: JPG, PNG, GIF, SVG, WEBP, TIFF (Photographes)
📝 Texte: TXT, MD, HTML, PDF, DOCX (Blogueurs)
📊 Données: JSON, CSV, XML, YAML (Analytics)
"""__version__ = "3.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices"

from typing import Dict, List, Any, Optional, Union, Type
import logging
from pathlib import Path

# Core Data Management Components
from .models import *
from .repositories import *
from .processors import *
from .transformers import *
from .validation import *
from .storage import *
from .analytics import *
from .indexing import *
from .pipeline import *
from .quality import *
from .archiving import *
from .backups import *
from .governance import *
from .migrations import *
from .seeds import *

# Data Management Configuration
logger = logging.getLogger(__name__)

class DataManagementConfig:
    """Configuration avancée du module data management"""
    
    # Formats supportés par type de créateur
    CREATOR_FORMATS = {
        "musician": {
            "audio": ["mp3", "wav", "flac", "ogg", "m4a", "aiff", "wma"],
            "video": ["mp4", "mov", "avi", "mkv"],
            "image": ["jpg", "jpeg", "png", "gif", "webp"],
            "metadata": ["json", "xml", "yaml"]
        },
        "influencer": {
            "video": ["mp4", "mov", "webm", "avi", "mkv", "flv"],
            "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
            "audio": ["mp3", "wav", "m4a"],
            "document": ["pdf", "txt", "md"]
        },
        "photographer": {
            "image": ["jpg", "jpeg", "png", "gif", "webp", "tiff", "raw", "svg"],
            "video": ["mp4", "mov", "avi"],
            "metadata": ["xmp", "json", "xml"]
        },
        "blogger": {
            "document": ["txt", "md", "html", "pdf", "docx", "rtf"],
            "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
            "data": ["json", "csv", "xml", "yaml"]
        },
        "comedian": {
            "video": ["mp4", "mov", "webm", "avi", "mkv", "flv"],
            "audio": ["mp3", "wav", "m4a", "ogg"],
            "image": ["jpg", "jpeg", "png", "gif", "webp"]
        }
    }
    
    # Tailles maximales par format
    MAX_FILE_SIZES = {
        "audio": 500 * 1024 * 1024,  # 500MB
        "video": 2 * 1024 * 1024 * 1024,  # 2GB
        "image": 50 * 1024 * 1024,  # 50MB
        "document": 100 * 1024 * 1024,  # 100MB
        "data": 10 * 1024 * 1024  # 10MB
    }
    
    # Stratégies de stockage par format
    STORAGE_STRATEGIES = {
        "hot": ["image", "document", "data"],  # Accès fréquent
        "warm": ["audio", "video"],  # Accès moyen
        "cold": ["archive", "backup"]  # Accès rare
    }
    
    # Configuration de la pipeline de traitement
    PROCESSING_PIPELINE = {
        "validation": True,
        "transformation": True,
        "fingerprinting": True,
        "indexing": True,
        "analytics": True,
        "quality_check": True,
        "archiving": True
    }

# Export des classes principales
__all__ = [
    # Configuration
    "DataManagementConfig",
    
    # Models
    "ContentModel", "CreatorModel", "FingerPrintModel", "AnalyticsModel",
    
    # Repositories
    "ContentRepository", "CreatorRepository", "AnalyticsRepository",
    
    # Processors
    "AudioProcessor", "VideoProcessor", "ImageProcessor", "DocumentProcessor",
    
    # Transformers
    "ContentTransformer", "MetadataTransformer", "FormatTransformer",
    
    # Validation
    "ContentValidator", "SchemaValidator", "SecurityValidator",
    
    # Storage
    "StorageManager", "CloudStorage", "LocalStorage", "CacheStorage",
    
    # Analytics
    "DataAnalytics", "MetricsCollector", "ReportGenerator",
    
    # Indexing
    "VectorIndexer", "SearchIndexer", "ContentIndexer",
    
    # Pipeline
    "DataPipeline", "ProcessingPipeline", "ETLPipeline",
    
    # Quality
    "QualityAssurance", "DataQuality", "ContentQuality",
    
    # Archiving
    "ArchiveManager", "CompressionEngine", "RetentionPolicy",
    
    # Backups
    "BackupManager", "RecoveryManager", "SnapshotManager",
    
    # Governance
    "DataGovernance", "ComplianceManager", "AuditTrail",
    
    # Migrations
    "MigrationManager", "SchemaEvolution", "DataMigrator",
    
    # Seeds
    "DataSeeder", "TestDataGenerator", "SampleDataCreator"
]

def get_data_management_info() -> Dict[str, Any]:
    """Retourne les informations du module data management"""
    return {
        "version": __version__,
        "author": __author__,
        "team": __team__,
        "supported_formats": len([fmt for creator in DataManagementConfig.CREATOR_FORMATS.values() 
                                 for formats in creator.values() for fmt in formats]),
        "creator_types": list(DataManagementConfig.CREATOR_FORMATS.keys()),
        "processing_stages": len(DataManagementConfig.PROCESSING_PIPELINE),
        "storage_strategies": list(DataManagementConfig.STORAGE_STRATEGIES.keys()),
        "max_file_sizes": DataManagementConfig.MAX_FILE_SIZES
    }

# Initialisation du logger
logger.info(f"Data Management Module v{__version__} initialized by {__author__}")
logger.info(f"Supporting {len(DataManagementConfig.CREATOR_FORMATS)} creator types with enterprise-grade data management")