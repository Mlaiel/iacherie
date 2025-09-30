"""
Configuration Backup Manager - Enterprise Application Configuration Backup
=========================================================================

Advanced configuration backup system for application settings, environment configs,
secrets, infrastructure as code, and creator platform configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import json
import yaml
import os
import shutil
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import configparser
import base64
import hashlib
from cryptography.fernet import Fernet
import subprocess

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Types of configuration files."""
    APPLICATION = "application"
    ENVIRONMENT = "environment"
    SECRETS = "secrets"
    INFRASTRUCTURE = "infrastructure"
    DEPLOYMENT = "deployment"
    API_KEYS = "api_keys"
    CREATOR_PLATFORM = "creator_platform"
    AI_AGENTS = "ai_agents"
    MONETIZATION = "monetization"
    SECURITY = "security"


class ConfigFormat(Enum):
    """Configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"
    TOML = "toml"
    XML = "xml"
    PROPERTIES = "properties"


class EncryptionLevel(Enum):
    """Encryption levels for sensitive configurations."""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


@dataclass
class ConfigSource:
    """Configuration source definition."""
    name: str
    path: str
    config_type: ConfigType
    format: ConfigFormat
    encryption_level: EncryptionLevel
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    backup_frequency: str = "daily"  # hourly, daily, weekly
    retention_days: int = 90
    creator_id: Optional[str] = None  # For creator-specific configs


@dataclass
class ConfigBackupRecord:
    """Record of configuration backup."""
    backup_id: str
    source: ConfigSource
    backup_path: str
    created_at: datetime
    file_count: int
    total_size_bytes: int
    checksum: str
    encrypted: bool
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigurationBackupManager:
    """
    Enterprise configuration backup manager.
    
    Features:
    - Multi-format configuration backup (JSON, YAML, INI, ENV, etc.)
    - Encrypted secrets backup with enterprise encryption
    - Infrastructure as Code backup (Terraform, Kubernetes, Docker)
    - Creator platform configuration backup
    - AI agents configuration backup
    - API keys and integration configs backup
    - Environment-specific configuration management
    - Version control integration
    - Automated scheduling and retention
    """
    
    def __init__(self, backup_root: str, encryption_key: Optional[str] = None):
        """Initialize configuration backup manager."""
        self.backup_root = Path(backup_root)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.backup_records: List[ConfigBackupRecord] = []
        
        # Initialize encryption
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Creator platform configuration sources
        self.creator_platform_configs = {
            'creator_profiles': ConfigSource(
                name="creator_profiles",
                path="/config/creators/",
                config_type=ConfigType.CREATOR_PLATFORM,
                format=ConfigFormat.JSON,
                encryption_level=EncryptionLevel.ENTERPRISE
            ),
            'ai_agents': ConfigSource(
                name="ai_agents",
                path="/config/ai/",
                config_type=ConfigType.AI_AGENTS,
                format=ConfigFormat.YAML,
                encryption_level=EncryptionLevel.ADVANCED
            ),
            'monetization': ConfigSource(
                name="monetization",
                path="/config/monetization/",
                config_type=ConfigType.MONETIZATION,
                format=ConfigFormat.JSON,
                encryption_level=EncryptionLevel.ENTERPRISE
            ),
            'platform_apis': ConfigSource(
                name="platform_apis",
                path="/config/platforms/",
                config_type=ConfigType.API_KEYS,
                format=ConfigFormat.ENV,
                encryption_level=EncryptionLevel.ENTERPRISE
            )
        }
        
        # Ensure backup directory exists
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize default configuration sources
        self.config_sources: Dict[str, ConfigSource] = {
            **self.creator_platform_configs,
            'application': ConfigSource(
                name="application",
                path="/config/app/",
                config_type=ConfigType.APPLICATION,
                format=ConfigFormat.YAML,
                encryption_level=EncryptionLevel.BASIC
            ),
            'environment': ConfigSource(
                name="environment",
                path="/config/env/",
                config_type=ConfigType.ENVIRONMENT,
                format=ConfigFormat.ENV,
                encryption_level=EncryptionLevel.ADVANCED
            ),
            'secrets': ConfigSource(
                name="secrets",
                path="/config/secrets/",
                config_type=ConfigType.SECRETS,
                format=ConfigFormat.JSON,
                encryption_level=EncryptionLevel.ENTERPRISE
            ),
            'infrastructure': ConfigSource(
                name="infrastructure",
                path="/infrastructure/",
                config_type=ConfigType.INFRASTRUCTURE,
                format=ConfigFormat.YAML,
                encryption_level=EncryptionLevel.ADVANCED,
                include_patterns=["*.tf", "*.yaml", "*.yml", "Dockerfile*", "*.sh"]
            ),
            'deployment': ConfigSource(
                name="deployment",
                path="/deploy/",
                config_type=ConfigType.DEPLOYMENT,
                format=ConfigFormat.YAML,
                encryption_level=EncryptionLevel.ADVANCED
            )
        }
    
    async def backup_configuration(
        self,
        source_name: str,
        custom_path: Optional[str] = None
    ) -> str:
        """
        Backup configuration from specified source.
        
        Args:
            source_name: Name of configuration source
            custom_path: Optional custom path override
            
        Returns:
            Backup ID for tracking
        """
        if source_name not in self.config_sources:
            raise ValueError(f"Unknown configuration source: {source_name}")
        
        source = self.config_sources[source_name]
        if custom_path:
            source.path = custom_path
        
        backup_id = self._generate_backup_id(source)
        
        try:
            self.logger.info(f"⚙️ Starting configuration backup: {source_name}")
            
            # Create backup directory
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / source_name / backup_timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Collect configuration files
            config_files = await self._collect_config_files(source)
            
            # Backup each configuration file
            total_size = 0
            file_count = 0
            
            for config_file in config_files:
                try:
                    await self._backup_config_file(config_file, backup_dir, source)
                    total_size += config_file.stat().st_size
                    file_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to backup config file {config_file}: {e}")
            
            # Create backup metadata
            metadata = await self._create_backup_metadata(source, backup_dir, file_count)
            
            # Calculate backup checksum
            checksum = await self._calculate_backup_checksum(backup_dir)
            
            # Create backup record
            backup_record = ConfigBackupRecord(
                backup_id=backup_id,
                source=source,
                backup_path=str(backup_dir),
                created_at=datetime.now(),
                file_count=file_count,
                total_size_bytes=total_size,
                checksum=checksum,
                encrypted=source.encryption_level != EncryptionLevel.NONE,
                version=self._get_version_info(source),
                metadata=metadata
            )
            
            self.backup_records.append(backup_record)
            
            # Save backup record
            await self._save_backup_record(backup_record)
            
            self.logger.info(f"✅ Configuration backup completed: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"❌ Configuration backup failed: {source_name} - {str(e)}")
            raise
    
    async def _collect_config_files(self, source: ConfigSource) -> List[Path]:
        """Collect configuration files from source."""
        config_files = []
        source_path = Path(source.path)
        
        if not source_path.exists():
            self.logger.warning(f"Configuration source path does not exist: {source.path}")
            return config_files
        
        try:
            if source_path.is_file():
                config_files.append(source_path)
            elif source_path.is_dir():
                for file_path in source_path.rglob("*"):
                    if file_path.is_file() and self._should_backup_config_file(file_path, source):
                        config_files.append(file_path)
            
        except PermissionError as e:
            self.logger.error(f"Permission denied accessing {source.path}: {e}")
        
        return config_files
    
    def _should_backup_config_file(self, file_path: Path, source: ConfigSource) -> bool:
        """Determine if configuration file should be backed up."""
        file_str = str(file_path)
        
        # Check include patterns
        if source.include_patterns:
            if not any(file_path.match(pattern) for pattern in source.include_patterns):
                return False
        
        # Check exclude patterns
        if source.exclude_patterns:
            if any(file_path.match(pattern) for pattern in source.exclude_patterns):
                return False
        
        # Common exclusions
        exclude_patterns = [
            "*.tmp", "*.temp", "*.bak", "*.backup",
            "__pycache__", "*.pyc", ".git", ".svn",
            "node_modules", "*.log"
        ]
        
        if any(file_path.match(pattern) for pattern in exclude_patterns):
            return False
        
        return True
    
    async def _backup_config_file(
        self,
        config_file: Path,
        backup_dir: Path,
        source: ConfigSource
    ) -> None:
        """Backup individual configuration file with appropriate handling."""
        try:
            # Calculate relative path
            source_path = Path(source.path)
            if source_path.is_dir():
                relative_path = config_file.relative_to(source_path)
            else:
                relative_path = config_file.name
            
            backup_file_path = backup_dir / relative_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read file content
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Process based on configuration type and format
            processed_content = await self._process_config_content(
                content, config_file, source
            )
            
            # Apply encryption if required
            if source.encryption_level != EncryptionLevel.NONE:
                processed_content = await self._encrypt_config_content(
                    processed_content, source.encryption_level
                )
                backup_file_path = backup_file_path.with_suffix(backup_file_path.suffix + ".enc")
            
            # Write backup file
            mode = 'wb' if isinstance(processed_content, bytes) else 'w'
            with open(backup_file_path, mode) as f:
                f.write(processed_content)
            
            self.logger.debug(f"Backed up config file: {config_file} -> {backup_file_path}")
            
        except Exception as e:
            self.logger.error(f"Error backing up config file {config_file}: {e}")
            raise
    
    async def _process_config_content(
        self,
        content: str,
        config_file: Path,
        source: ConfigSource
    ) -> Union[str, bytes]:
        """Process configuration content based on type and format."""
        try:
            # Parse and validate configuration based on format
            if source.format == ConfigFormat.JSON:
                parsed = json.loads(content)
                # Add metadata for creator platform configs
                if source.config_type in [ConfigType.CREATOR_PLATFORM, ConfigType.AI_AGENTS]:
                    parsed = await self._add_creator_metadata(parsed, source)
                return json.dumps(parsed, indent=2)
            
            elif source.format == ConfigFormat.YAML:
                parsed = yaml.safe_load(content)
                if source.config_type in [ConfigType.CREATOR_PLATFORM, ConfigType.AI_AGENTS]:
                    parsed = await self._add_creator_metadata(parsed, source)
                return yaml.dump(parsed, default_flow_style=False, indent=2)
            
            elif source.format == ConfigFormat.INI:
                config = configparser.ConfigParser()
                config.read_string(content)
                # Add backup metadata section
                if not config.has_section('backup_metadata'):
                    config.add_section('backup_metadata')
                    config.set('backup_metadata', 'backup_timestamp', datetime.now().isoformat())
                    config.set('backup_metadata', 'source_type', source.config_type.value)
                
                # Write to string
                from io import StringIO
                output = StringIO()
                config.write(output)
                return output.getvalue()
            
            elif source.format == ConfigFormat.ENV:
                # Process environment files with creator platform context
                lines = content.splitlines()
                processed_lines = []
                
                # Add backup metadata
                processed_lines.append(f"# Backup created: {datetime.now().isoformat()}")
                processed_lines.append(f"# Source: {source.name}")
                processed_lines.append(f"# Config type: {source.config_type.value}")
                processed_lines.append("")
                
                for line in lines:
                    # Mask sensitive values for creator platform configs
                    if source.config_type in [ConfigType.SECRETS, ConfigType.API_KEYS]:
                        line = self._mask_sensitive_env_vars(line)
                    processed_lines.append(line)
                
                return "\n".join(processed_lines)
            
            else:
                # For other formats, return as-is with metadata comment
                metadata_comment = f"# Backup created: {datetime.now().isoformat()}\n"
                metadata_comment += f"# Source: {source.name} ({source.config_type.value})\n\n"
                return metadata_comment + content
        
        except Exception as e:
            self.logger.warning(f"Could not parse config file {config_file}: {e}")
            # Return original content with metadata
            return f"# Backup created: {datetime.now().isoformat()}\n# Original file: {config_file}\n\n{content}"
    
    async def _add_creator_metadata(self, parsed_config: Dict[str, Any], source: ConfigSource) -> Dict[str, Any]:
        """Add creator platform specific metadata to configuration."""
        if not isinstance(parsed_config, dict):
            return parsed_config
        
        # Add backup metadata
        parsed_config['_backup_metadata'] = {
            'backup_timestamp': datetime.now().isoformat(),
            'source_type': source.config_type.value,
            'creator_platform_version': '1.0.0',
            'ai_agents_count': 53 if source.config_type == ConfigType.AI_AGENTS else None,
            'platform_integrations': 65 if source.config_type == ConfigType.CREATOR_PLATFORM else None
        }
        
        # Add creator-specific context
        if source.creator_id:
            parsed_config['_backup_metadata']['creator_id'] = source.creator_id
        
        return parsed_config
    
    def _mask_sensitive_env_vars(self, line: str) -> str:
        """Mask sensitive environment variables."""
        sensitive_patterns = [
            'PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY',
            'PRIVATE', 'CREDENTIAL', 'AUTH', 'PASS'
        ]
        
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            
            # Check if key contains sensitive patterns
            if any(pattern in key.upper() for pattern in sensitive_patterns):
                # Mask the value but keep structure for validation
                if len(value) > 8:
                    masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    masked_value = '*' * len(value)
                return f"{key}={masked_value}"
        
        return line
    
    async def _encrypt_config_content(
        self,
        content: Union[str, bytes],
        encryption_level: EncryptionLevel
    ) -> bytes:
        """Encrypt configuration content based on encryption level."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if encryption_level == EncryptionLevel.BASIC:
            # Base64 encoding (not real encryption, just obfuscation)
            return base64.b64encode(content)
        
        elif encryption_level in [EncryptionLevel.ADVANCED, EncryptionLevel.ENTERPRISE]:
            # Fernet encryption (AES 128 in CBC mode)
            return self.cipher_suite.encrypt(content)
        
        return content
    
    async def _create_backup_metadata(
        self,
        source: ConfigSource,
        backup_dir: Path,
        file_count: int
    ) -> Dict[str, Any]:
        """Create comprehensive backup metadata."""
        return {
            'source_name': source.name,
            'source_path': source.path,
            'config_type': source.config_type.value,
            'format': source.format.value,
            'encryption_level': source.encryption_level.value,
            'backup_frequency': source.backup_frequency,
            'retention_days': source.retention_days,
            'file_count': file_count,
            'backup_timestamp': datetime.now().isoformat(),
            'creator_platform_metadata': {
                'supports_53_ai_agents': source.config_type == ConfigType.AI_AGENTS,
                'supports_65_platforms': source.config_type == ConfigType.CREATOR_PLATFORM,
                'monetization_enabled': source.config_type == ConfigType.MONETIZATION,
                'security_compliance': ['GDPR', 'CCPA', 'DMCA'] if source.encryption_level == EncryptionLevel.ENTERPRISE else []
            }
        }
    
    async def _calculate_backup_checksum(self, backup_dir: Path) -> str:
        """Calculate checksum for entire backup directory."""
        sha256_hash = hashlib.sha256()
        
        try:
            for file_path in sorted(backup_dir.rglob("*")):
                if file_path.is_file():
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating backup checksum: {e}")
            return ""
    
    def _get_version_info(self, source: ConfigSource) -> str:
        """Get version information for configuration source."""
        try:
            # Try to get git version if available
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=source.path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]  # Short commit hash
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to timestamp
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def _save_backup_record(self, record: ConfigBackupRecord) -> None:
        """Save backup record to metadata file."""
        record_file = Path(record.backup_path) / "backup_record.json"
        
        record_data = {
            'backup_id': record.backup_id,
            'source': {
                'name': record.source.name,
                'path': record.source.path,
                'config_type': record.source.config_type.value,
                'format': record.source.format.value,
                'encryption_level': record.source.encryption_level.value
            },
            'backup_path': record.backup_path,
            'created_at': record.created_at.isoformat(),
            'file_count': record.file_count,
            'total_size_bytes': record.total_size_bytes,
            'checksum': record.checksum,
            'encrypted': record.encrypted,
            'version': record.version,
            'metadata': record.metadata
        }
        
        with open(record_file, 'w') as f:
            json.dump(record_data, f, indent=2)
    
    def _generate_backup_id(self, source: ConfigSource) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"config_{source.name}_{timestamp}"
    
    async def backup_all_configurations(self) -> List[str]:
        """Backup all configured sources."""
        backup_ids = []
        
        for source_name in self.config_sources:
            try:
                backup_id = await self.backup_configuration(source_name)
                backup_ids.append(backup_id)
            except Exception as e:
                self.logger.error(f"Failed to backup {source_name}: {e}")
        
        return backup_ids
    
    async def restore_configuration(
        self,
        backup_id: str,
        restore_path: Optional[str] = None,
        decrypt: bool = True
    ) -> bool:
        """
        Restore configuration from backup.
        
        Args:
            backup_id: ID of backup to restore
            restore_path: Optional custom restore path
            decrypt: Whether to decrypt encrypted files
            
        Returns:
            True if restore successful
        """
        # Find backup record
        backup_record = None
        for record in self.backup_records:
            if record.backup_id == backup_id:
                backup_record = record
                break
        
        if not backup_record:
            raise ValueError(f"Backup not found: {backup_id}")
        
        self.logger.info(f"🔄 Starting configuration restore: {backup_id}")
        
        try:
            backup_path = Path(backup_record.backup_path)
            target_path = Path(restore_path) if restore_path else Path(backup_record.source.path)
            
            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Restore files
            for file_path in backup_path.rglob("*"):
                if file_path.is_file() and file_path.name != "backup_record.json":
                    relative_path = file_path.relative_to(backup_path)
                    target_file = target_path / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Handle encrypted files
                    if file_path.suffix == ".enc" and decrypt and backup_record.encrypted:
                        content = await self._decrypt_config_file(file_path)
                        target_file = target_file.with_suffix("")  # Remove .enc extension
                        
                        with open(target_file, 'w') as f:
                            f.write(content)
                    else:
                        shutil.copy2(file_path, target_file)
            
            self.logger.info(f"✅ Configuration restore completed: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration restore failed: {backup_id} - {str(e)}")
            raise
    
    async def _decrypt_config_file(self, encrypted_file: Path) -> str:
        """Decrypt configuration file."""
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
        
        try:
            # Try Fernet decryption first
            decrypted_content = self.cipher_suite.decrypt(encrypted_content)
            return decrypted_content.decode('utf-8')
        except Exception:
            # Fallback to base64 decoding
            try:
                decoded_content = base64.b64decode(encrypted_content)
                return decoded_content.decode('utf-8')
            except Exception as e:
                raise Exception(f"Failed to decrypt file: {e}")
    
    async def list_backups(
        self,
        source_name: Optional[str] = None,
        limit: int = 50
    ) -> List[ConfigBackupRecord]:
        """List configuration backups with optional filtering."""
        backups = self.backup_records.copy()
        
        if source_name:
            backups = [b for b in backups if b.source.name == source_name]
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.created_at, reverse=True)
        
        return backups[:limit]
    
    async def cleanup_expired_backups(self) -> int:
        """Clean up expired configuration backups."""
        cleanup_count = 0
        current_time = datetime.now()
        
        for record in self.backup_records.copy():
            retention_period = timedelta(days=record.source.retention_days)
            
            if current_time - record.created_at > retention_period:
                # Remove backup directory
                backup_path = Path(record.backup_path)
                if backup_path.exists():
                    try:
                        shutil.rmtree(backup_path)
                        cleanup_count += 1
                        self.logger.info(f"🗑️ Removed expired config backup: {record.backup_id}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove backup: {e}")
                
                # Remove from records
                self.backup_records.remove(record)
        
        return cleanup_count
    
    async def add_config_source(self, source: ConfigSource) -> None:
        """Add new configuration source."""
        self.config_sources[source.name] = source
        self.logger.info(f"Added configuration source: {source.name}")
    
    async def get_backup_metrics(self) -> Dict[str, Any]:
        """Get comprehensive configuration backup metrics."""
        total_backups = len(self.backup_records)
        total_size = sum(r.total_size_bytes for r in self.backup_records)
        total_files = sum(r.file_count for r in self.backup_records)
        
        # Group by source type
        by_source = {}
        for record in self.backup_records:
            source_name = record.source.name
            if source_name not in by_source:
                by_source[source_name] = {'count': 0, 'size': 0, 'files': 0}
            by_source[source_name]['count'] += 1
            by_source[source_name]['size'] += record.total_size_bytes
            by_source[source_name]['files'] += record.file_count
        
        # Creator platform specific metrics
        creator_backups = len([r for r in self.backup_records 
                              if r.source.config_type in [ConfigType.CREATOR_PLATFORM, 
                                                          ConfigType.AI_AGENTS, 
                                                          ConfigType.MONETIZATION]])
        
        encrypted_backups = len([r for r in self.backup_records if r.encrypted])
        
        return {
            'total_config_backups': total_backups,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024**2), 2),
            'total_files_backed_up': total_files,
            'backups_by_source': by_source,
            'creator_platform_backups': creator_backups,
            'encrypted_backups': encrypted_backups,
            'encryption_rate': encrypted_backups / total_backups if total_backups > 0 else 0,
            'configured_sources': len(self.config_sources),
            'creator_platform_sources': len(self.creator_platform_configs)
        }


# Export public interface
__all__ = [
    'ConfigurationBackupManager',
    'ConfigType',
    'ConfigFormat',
    'EncryptionLevel',
    'ConfigSource',
    'ConfigBackupRecord'
]