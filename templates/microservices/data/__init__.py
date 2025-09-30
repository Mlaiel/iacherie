"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

IA Chérie Data Templates Module
Enterprise data management microservices templates for creator economy platform
"""

from .database_service_template import DatabaseServiceTemplate
from .cache_service_template import CacheServiceTemplate
from .search_service_template import SearchServiceTemplate
from .file_storage_template import FileStorageTemplate
from .backup_service_template import BackupServiceTemplate
from .data_sync_template import DataSyncTemplate
from .migration_service_template import MigrationServiceTemplate
from .replication_template import ReplicationTemplate

# New advanced data management templates
from .data_management_template import (
    DataModelTemplate,
    DataPipelineTemplate,
    DataValidationTemplate,
    DataStreamingTemplate,
    DataWarehouseTemplate,
    GDPRComplianceTemplate,
    DataTemplateFactory,
    DEFAULT_DATA_CONFIG,
    create_data_service_app
)

from .pipeline_template import (
    DataPipelineTemplate as AdvancedDataPipelineTemplate,
    ETLPipelineTemplate,
    StreamingPipelineTemplate,
    DataPipelineOrchestrator,
    PipelineStatus,
    ProcessingMode,
    PipelineConfig,
    DataSource,
    DataTransformation,
    DataDestination,
    create_data_pipeline_app
)

__all__ = [
    # Original templates
    "DatabaseServiceTemplate",
    "CacheServiceTemplate", 
    "SearchServiceTemplate",
    "FileStorageTemplate",
    "BackupServiceTemplate",
    "DataSyncTemplate",
    "MigrationServiceTemplate",
    "ReplicationTemplate",
    
    # Advanced data management
    "DataModelTemplate",
    "DataPipelineTemplate",
    "DataValidationTemplate",
    "DataStreamingTemplate",
    "DataWarehouseTemplate",
    "GDPRComplianceTemplate",
    "DataTemplateFactory",
    "create_data_service_app",
    
    # Advanced pipelines
    "AdvancedDataPipelineTemplate",
    "ETLPipelineTemplate",
    "StreamingPipelineTemplate",
    "DataPipelineOrchestrator",
    "PipelineStatus",
    "ProcessingMode",
    "PipelineConfig",
    "DataSource",
    "DataTransformation",
    "DataDestination",
    "create_data_pipeline_app",
    
    # Configuration
    "DEFAULT_DATA_CONFIG"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"