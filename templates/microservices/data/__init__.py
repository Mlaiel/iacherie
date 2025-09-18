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

Ainflue Data Templates Module
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

__all__ = [
    "DatabaseServiceTemplate",
    "CacheServiceTemplate",
    "SearchServiceTemplate",
    "FileStorageTemplate",
    "BackupServiceTemplate",
    "DataSyncTemplate",
    "MigrationServiceTemplate",
    "ReplicationTemplate"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"