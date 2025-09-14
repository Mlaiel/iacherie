"""
Backup Module - Enterprise Backup and Archive Infrastructure
================================================================================

Expert Team: DBA + Security + DevOps + Backend Senior
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🗄️ DBA: Database backup strategies, point-in-time recovery
🔒 Security: Encrypted backup, compliance, audit trails
⚙️ DevOps: Automated backup scheduling, monitoring
🏗️ Backend Senior: Multi-cloud backup orchestration

Enterprise backup infrastructure for Ainflue platform supporting:
- Database backup with point-in-time recovery
- File system and media backup management
- Cross-region and multi-cloud backup strategies
- Real-time backup for critical data
- Encrypted backup with key management
- Automated backup scheduling and monitoring
- Creator content protection and archiving
"""

from .database_backup_manager import DatabaseBackupManager
from .file_backup_manager import FileBackupManager
from .media_backup_manager import MediaBackupManager
from .configuration_backup import ConfigurationBackup
from .incremental_backup import IncrementalBackup
from .cross_region_backup import CrossRegionBackup
from .backup_monitoring import BackupMonitoring
from .encrypted_backup import EncryptedBackup
from .real_time_backup import RealTimeBackup
from .backup_analytics import BackupAnalytics
from .backup_alerting import BackupAlerting
from .automated_backup_scheduling import AutomatedBackupScheduling

__all__ = [
    'DatabaseBackupManager',
    'FileBackupManager',
    'MediaBackupManager',
    'ConfigurationBackup',
    'IncrementalBackup',
    'CrossRegionBackup',
    'BackupMonitoring',
    'EncryptedBackup',
    'RealTimeBackup',
    'BackupAnalytics',
    'BackupAlerting',
    'AutomatedBackupScheduling'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise backup infrastructure for data protection and compliance"