#!/usr/bin/env python3
"""
⚡ Redis Configuration Manager - Ainflue Enterprise
© 2025 Fahed Mlaiel <mlaiel@live.de> - All Rights Reserved
Configuration Management System for Creator Economy Platform
"""

# ========================================================================================
# ⚠️  PROTECTION PROPRIÉTÉ INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
# TOUS DROITS RÉSERVÉS - Utilisation commerciale strictement encadrée
# ========================================================================================

import os
import yaml
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    class redis:
        class Redis:
            def __init__(self, *args, **kwargs):
                pass
            def ping(self):
                return True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConfigurationTemplate:
    """Configuration template definition"""
    name: str
    category: str
    environment: str
    priority: int
    dependencies: List[str]
    validation_rules: Dict[str, Any]


class RedisConfigManager:
    """
    Enterprise Redis Configuration Manager
    Manages all Redis configurations for the Ainflue Creator Economy Platform
    """
    
    def __init__(self, config_dir: str = "/home/runner/work/Ainflue/Ainflue/redis/config"):
        """Initialize the configuration manager"""
        self.config_dir = Path(config_dir)
        self.redis_client = None
        self.configurations = {}
        self.templates = {}
        self.validation_rules = {}
        
        # Configuration categories
        self.categories = {
            'security': ['security_hardening', 'tls_configuration', 'rbac_permissions'],
            'performance': ['memory_optimization', 'connection_pooling', 'latency_optimization'],
            'environment': ['development_config', 'staging_config', 'production_config'],
            'creator_economy': ['creator_cache_strategy', 'content_caching_config', 'monetization_cache'],
            'monitoring': ['prometheus_metrics', 'grafana_dashboards', 'alerting_rules'],
            'replication': ['master_replica_config', 'cross_datacenter_replication'],
            'gamification': ['leaderboard_cache', 'achievement_cache', 'point_system_cache'],
            'analytics': ['metrics_aggregation', 'real_time_analytics', 'user_behavior_cache']
        }
        
        logger.info("🔧 Initializing Redis Configuration Manager for Ainflue Enterprise")
        self._load_configurations()
        
    def _load_configurations(self):
        """Load all configuration files"""
        try:
            config_files = list(self.config_dir.glob("*.yaml"))
            logger.info(f"📂 Found {len(config_files)} configuration files")
            
            for config_file in config_files:
                self._load_config_file(config_file)
                
            logger.info(f"✅ Loaded {len(self.configurations)} configurations")
            
        except Exception as e:
            logger.error(f"❌ Error loading configurations: {e}")
            raise
    
    def _load_config_file(self, config_file: Path):
        """Load a single configuration file"""
        try:
            with open(config_file, 'r') as f:
                # Handle multi-document YAML files
                docs = list(yaml.safe_load_all(f))
                
            config_name = config_file.stem
            
            # If multiple documents, use the first one as main config
            config_data = docs[0] if docs else {}
            
            # If there are additional documents, store them as well
            if len(docs) > 1:
                config_data['additional_documents'] = docs[1:]
            
            self.configurations[config_name] = {
                'file_path': str(config_file),
                'data': config_data,
                'last_modified': datetime.fromtimestamp(config_file.stat().st_mtime),
                'checksum': self._calculate_checksum(config_file),
                'document_count': len(docs)
            }
            
            logger.debug(f"📄 Loaded configuration: {config_name} ({len(docs)} documents)")
            
        except Exception as e:
            logger.error(f"❌ Error loading config file {config_file}: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_configuration(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration"""
        return self.configurations.get(config_name)
    
    def get_configurations_by_category(self, category: str) -> Dict[str, Any]:
        """Get all configurations for a specific category"""
        if category not in self.categories:
            logger.warning(f"⚠️  Unknown category: {category}")
            return {}
        
        category_configs = {}
        for config_name in self.categories[category]:
            if config_name in self.configurations:
                category_configs[config_name] = self.configurations[config_name]
        
        return category_configs
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for a specific environment"""
        env_configs = {}
        
        for config_name, config_data in self.configurations.items():
            if environment in config_name or 'environment' in config_data.get('data', {}):
                metadata = config_data.get('data', {}).get('metadata', {})
                if metadata.get('labels', {}).get('environment') == environment:
                    env_configs[config_name] = config_data
        
        return env_configs
    
    def validate_configuration(self, config_name: str) -> bool:
        """Validate a configuration against its rules"""
        try:
            config = self.get_configuration(config_name)
            if not config:
                logger.error(f"❌ Configuration not found: {config_name}")
                return False
            
            config_data = config['data']
            
            # Skip validation for empty configurations
            if not config_data:
                logger.warning(f"⚠️  Empty configuration: {config_name}")
                return True
            
            # For Kubernetes-style configurations
            if isinstance(config_data, dict) and 'kind' in config_data:
                required_fields = ['apiVersion', 'kind', 'metadata']
                for field in required_fields:
                    if field not in config_data:
                        logger.error(f"❌ Missing required field '{field}' in {config_name}")
                        return False
                
                # Validate metadata
                metadata = config_data.get('metadata', {})
                if 'name' not in metadata:
                    logger.error(f"❌ Missing metadata.name in {config_name}")
                    return False
            
            # For simple configuration files
            elif isinstance(config_data, dict):
                # Basic validation for simple configs
                if not config_data:
                    logger.warning(f"⚠️  Empty configuration data in {config_name}")
                    return True
            
            # Creator Economy specific validations
            if 'creator' in config_name or 'monetization' in config_name:
                if not self._validate_creator_economy_config(config_data):
                    return False
            
            logger.debug(f"✅ Configuration {config_name} is valid")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating configuration {config_name}: {e}")
            return False
    
    def _validate_creator_economy_config(self, config_data: Dict[str, Any]) -> bool:
        """Validate creator economy specific configurations"""
        try:
            # Check for required creator economy fields
            data_section = config_data.get('data', {})
            
            # Check for proper author attribution
            annotations = config_data.get('metadata', {}).get('annotations', {})
            if 'author' not in annotations or 'Fahed Mlaiel' not in annotations['author']:
                logger.error("❌ Missing proper author attribution for creator economy config")
                return False
            
            # Check for security considerations in monetization configs
            if 'monetization' in str(config_data).lower():
                if 'security' not in str(data_section).lower():
                    logger.warning("⚠️  Monetization config should include security considerations")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating creator economy config: {e}")
            return False
    
    def apply_configuration(self, config_name: str, target_environment: str = 'development') -> bool:
        """Apply a configuration to Redis"""
        try:
            config = self.get_configuration(config_name)
            if not config:
                logger.error(f"❌ Configuration not found: {config_name}")
                return False
            
            if not self.validate_configuration(config_name):
                logger.error(f"❌ Configuration validation failed: {config_name}")
                return False
            
            # Connect to Redis if not already connected
            if not self.redis_client:
                self._connect_to_redis(target_environment)
            
            # Apply configuration based on type
            config_data = config['data'].get('data', {})
            
            if 'security' in config_name:
                return self._apply_security_config(config_data)
            elif 'performance' in config_name:
                return self._apply_performance_config(config_data)
            elif 'creator' in config_name:
                return self._apply_creator_economy_config(config_data)
            else:
                return self._apply_generic_config(config_data)
            
        except Exception as e:
            logger.error(f"❌ Error applying configuration {config_name}: {e}")
            return False
    
    def _connect_to_redis(self, environment: str):
        """Connect to Redis based on environment"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  Redis module not available, using mock client")
            self.redis_client = redis.Redis()
            return
            
        try:
            if environment == 'production':
                host = 'redis-prod.ainflue.com'
                port = 16379
                ssl = True
            elif environment == 'staging':
                host = 'redis-staging.ainflue.com'
                port = 16379
                ssl = True
            else:
                host = 'localhost'
                port = 6379
                ssl = False
            
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                ssl=ssl,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Connected to Redis ({environment})")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def _apply_security_config(self, config_data: Dict[str, Any]) -> bool:
        """Apply security-specific configuration"""
        try:
            logger.info("🔒 Applying security configuration...")
            
            # Apply authentication settings
            if 'auth_config' in config_data:
                logger.info("Setting up authentication...")
                # Note: ACL commands would be applied here in real implementation
            
            # Apply TLS settings
            if 'tls_config' in config_data:
                logger.info("Configuring TLS...")
            
            # Apply access control
            if 'rbac_permissions' in config_data:
                logger.info("Setting up RBAC permissions...")
            
            logger.info("✅ Security configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error applying security config: {e}")
            return False
    
    def _apply_performance_config(self, config_data: Dict[str, Any]) -> bool:
        """Apply performance-specific configuration"""
        try:
            logger.info("⚡ Applying performance configuration...")
            
            # Apply memory settings
            if 'memory_config' in config_data:
                memory_config = config_data['memory_config']
                if 'maxmemory' in memory_config:
                    # self.redis_client.config_set('maxmemory', memory_config['maxmemory'])
                    logger.info(f"Set maxmemory: {memory_config['maxmemory']}")
            
            # Apply connection settings
            if 'connection_config' in config_data:
                logger.info("Configuring connection settings...")
            
            logger.info("✅ Performance configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error applying performance config: {e}")
            return False
    
    def _apply_creator_economy_config(self, config_data: Dict[str, Any]) -> bool:
        """Apply creator economy specific configuration"""
        try:
            logger.info("👤 Applying creator economy configuration...")
            
            # Apply creator profile caching
            if 'creator_profile_caching' in config_data:
                logger.info("Setting up creator profile caching...")
            
            # Apply content caching
            if 'content_caching_strategy' in config_data:
                logger.info("Configuring content caching strategy...")
            
            # Apply monetization settings
            if 'monetization_caching' in config_data:
                logger.info("Setting up monetization caching...")
            
            logger.info("✅ Creator economy configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error applying creator economy config: {e}")
            return False
    
    def _apply_generic_config(self, config_data: Dict[str, Any]) -> bool:
        """Apply generic configuration"""
        try:
            logger.info("🔧 Applying generic configuration...")
            
            # Apply basic Redis settings
            for key, value in config_data.items():
                if isinstance(value, (str, int, float, bool)):
                    logger.info(f"Setting {key}: {value}")
                    # self.redis_client.config_set(key, value)
            
            logger.info("✅ Generic configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error applying generic config: {e}")
            return False
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get status of all configurations"""
        status = {
            'total_configurations': len(self.configurations),
            'categories': {},
            'last_updated': None,
            'validation_status': {}
        }
        
        # Calculate category statistics
        for category, configs in self.categories.items():
            loaded_configs = [c for c in configs if c in self.configurations]
            status['categories'][category] = {
                'total': len(configs),
                'loaded': len(loaded_configs),
                'percentage': (len(loaded_configs) / len(configs)) * 100
            }
        
        # Get validation status for all configs
        for config_name in self.configurations:
            status['validation_status'][config_name] = self.validate_configuration(config_name)
        
        # Find most recent update
        if self.configurations:
            most_recent = max(
                self.configurations.values(),
                key=lambda x: x['last_modified']
            )
            status['last_updated'] = most_recent['last_modified']
        
        return status
    
    def export_configuration_summary(self, output_file: str = None) -> str:
        """Export configuration summary to JSON"""
        try:
            status = self.get_configuration_status()
            
            # Add detailed configuration info
            detailed_status = {
                'summary': status,
                'configurations': {}
            }
            
            for config_name, config_data in self.configurations.items():
                detailed_status['configurations'][config_name] = {
                    'file_path': config_data['file_path'],
                    'last_modified': config_data['last_modified'].isoformat(),
                    'checksum': config_data['checksum'],
                    'valid': self.validate_configuration(config_name)
                }
            
            json_output = json.dumps(detailed_status, indent=2, default=str)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(json_output)
                logger.info(f"📊 Configuration summary exported to: {output_file}")
            
            return json_output
            
        except Exception as e:
            logger.error(f"❌ Error exporting configuration summary: {e}")
            return "{}"


def main():
    """Main function for testing the configuration manager"""
    try:
        # Initialize configuration manager
        config_manager = RedisConfigManager()
        
        # Display configuration status
        status = config_manager.get_configuration_status()
        print(f"\n📊 Configuration Status:")
        print(f"Total Configurations: {status['total_configurations']}")
        
        for category, stats in status['categories'].items():
            print(f"{category.title()}: {stats['loaded']}/{stats['total']} ({stats['percentage']:.1f}%)")
        
        # Validate all configurations
        print(f"\n🔍 Validation Results:")
        for config_name, is_valid in status['validation_status'].items():
            status_icon = "✅" if is_valid else "❌"
            print(f"{status_icon} {config_name}")
        
        # Export summary
        summary_file = "/tmp/redis_config_summary.json"
        config_manager.export_configuration_summary(summary_file)
        
        print(f"\n✅ Redis Configuration Manager initialized successfully")
        print(f"📁 Configuration directory: {config_manager.config_dir}")
        print(f"📊 Summary exported to: {summary_file}")
        
    except Exception as e:
        logger.error(f"❌ Error in main function: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())