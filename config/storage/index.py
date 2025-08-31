"""Storage Configuration Index - IA-Influencer Agent Platform
==========================================================

Central index and orchestration for all storage configurations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from . import (
    STORAGE_CONFIGS,
    validate_all_storage_configs,
    get_storage_statistics,
    s3_config,
    azure_blob_config,
    gcs_config,
    local_storage_config,
    cdn_config,
    file_processing_config,
    backup_storage_config,
    storage_security_config
)

class StorageOrchestrator:
    """    Central orchestrator for all storage operations and configurations.
    Provides unified interface for storage management across the platform.
    """    
    def __init__(self):
        self.configs = STORAGE_CONFIGS
        self.initialized = False
        self.health_status = {}
        
    def initialize(self) -> bool:
        """Initialize all storage configurations and validate connectivity."""        try:
            print("🚀 Initializing IA-Influencer Agent Storage System...")
            
            # Validate all configurations
            validation_result = validate_all_storage_configs()
            
            if validation_result:
                print("✅ All storage configurations validated successfully")
                self.initialized = True
                
                # Perform health checks
                self._perform_health_checks()
                
                # Log initialization
                self._log_initialization()
                
                return True
            else:
                print("❌ Storage configuration validation failed")
                return False
                
        except Exception as e:
            print(f"❌ Storage initialization failed: {e}")
            return False
    
    def _perform_health_checks(self):
        """Perform health checks on all storage services."""        print("🔍 Performing storage health checks...")
        
        health_checks = {
            's3': self._check_s3_health,
            'azure': self._check_azure_health,
            'gcs': self._check_gcs_health,
            'local': self._check_local_health,
            'cdn': self._check_cdn_health,
            'security': self._check_security_health
        }
        
        for service, check_func in health_checks.items():
            try:
                self.health_status[service] = check_func()
                status = "✅" if self.health_status[service] else "⚠️"
                print(f"  {status} {service.upper()}: {'Healthy' if self.health_status[service] else 'Warning'}")
            except Exception as e:
                self.health_status[service] = False
                print(f"  ❌ {service.upper()}: Error - {e}")
    
    def _check_s3_health(self) -> bool:
        """Check AWS S3 connectivity and configuration."""        return s3_config.validate_configuration()
    
    def _check_azure_health(self) -> bool:
        """Check Azure Blob Storage connectivity and configuration."""        return azure_blob_config.validate_configuration()
    
    def _check_gcs_health(self) -> bool:
        """Check Google Cloud Storage connectivity and configuration."""        return gcs_config.validate_configuration()
    
    def _check_local_health(self) -> bool:
        """Check local storage accessibility and configuration."""        return local_storage_config.validate_configuration()
    
    def _check_cdn_health(self) -> bool:
        """Check CDN configuration and endpoints."""        return cdn_config.validate_configuration()
    
    def _check_security_health(self) -> bool:
        """Check security configuration and policies."""        return storage_security_config.validate_configuration()
    
    def _log_initialization(self):
        """Log storage system initialization."""        storage_security_config.log_security_event(
            'storage_initialization',
            {
                'timestamp': datetime.now().isoformat(),
                'initialized_configs': list(self.configs.keys()),
                'health_status': self.health_status,
                'environment': os.getenv('ENVIRONMENT', 'development')
            }
        )
    
    def get_optimal_storage_for_content(self, content_type: str, 
                                      file_size_mb: float,
                                      access_pattern: str = 'frequent') -> Dict[str, Any]:
        """        Get optimal storage configuration for specific content.
        
        Args:
            content_type: Type of content (audio, video, image, etc.)
            file_size_mb: File size in megabytes
            access_pattern: 'frequent', 'infrequent', 'archive'
            
        Returns:
            Dictionary with optimal storage recommendations
        """        recommendations = {
            'primary_storage': None,
            'backup_storage': None,
            'cdn_endpoint': None,
            'processing_config': None,
            'security_policy': None,
            'estimated_cost': 0.0
        }
        
        # Determine primary storage based on file size and access pattern
        if file_size_mb > 100:  # Large files
            if access_pattern == 'frequent':
                recommendations['primary_storage'] = 's3'
            elif access_pattern == 'infrequent':
                recommendations['primary_storage'] = 'gcs'
            else:  # archive
                recommendations['primary_storage'] = 'azure'
        else:  # Small to medium files
            recommendations['primary_storage'] = 's3'
        
        # Set backup storage (different from primary)
        backup_options = ['s3', 'azure', 'gcs']
        backup_options.remove(recommendations['primary_storage'])
        recommendations['backup_storage'] = backup_options[0]
        
        # CDN endpoint
        if content_type in ['image', 'audio', 'video']:
            recommendations['cdn_endpoint'] = cdn_config.get_endpoint_url(content_type)
        
        # Processing configuration
        if file_processing_config.is_format_supported(content_type, 'any'):
            recommendations['processing_config'] = {
                'supported_formats': file_processing_config.get_output_formats(content_type),
                'priority': file_processing_config.get_processing_priority(content_type),
                'max_processing_time': file_processing_config.get_max_processing_time(
                    content_type, file_size_mb
                )
            }
        
        # Security policy
        recommendations['security_policy'] = storage_security_config.get_security_policy_for_content(
            content_type
        )
        
        # Estimate monthly cost (simplified calculation)
        recommendations['estimated_cost'] = self._estimate_storage_cost(
            recommendations['primary_storage'], 
            file_size_mb, 
            access_pattern
        )
        
        return recommendations
    
    def _estimate_storage_cost(self, storage_type: str, file_size_mb: float, 
                             access_pattern: str) -> float:
        """Estimate monthly storage cost in USD."""        # Simplified cost calculation (actual costs vary by region and usage)
        cost_per_gb_month = {
            's3': {'frequent': 0.023, 'infrequent': 0.0125, 'archive': 0.004},
            'azure': {'frequent': 0.021, 'infrequent': 0.01, 'archive': 0.002},
            'gcs': {'frequent': 0.020, 'infrequent': 0.01, 'archive': 0.0012},
            'local': {'frequent': 0.01, 'infrequent': 0.01, 'archive': 0.01}
        }
        
        file_size_gb = file_size_mb / 1024
        rate = cost_per_gb_month.get(storage_type, {}).get(access_pattern, 0.02)
        
        return round(file_size_gb * rate, 4)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""        return {
            'initialized': self.initialized,
            'health_status': self.health_status,
            'timestamp': datetime.now().isoformat(),
            'configurations': len(self.configs),
            'statistics': get_storage_statistics() if self.initialized else None,
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'version': '1.0.0'
        }
    
    def refresh_configurations(self) -> bool:
        """Refresh all storage configurations."""        try:
            # Re-validate configurations
            validation_result = validate_all_storage_configs()
            
            if validation_result:
                # Update health status
                self._perform_health_checks()
                
                print("✅ Storage configurations refreshed successfully")
                return True
            else:
                print("❌ Configuration refresh failed validation")
                return False
                
        except Exception as e:
            print(f"❌ Configuration refresh failed: {e}")
            return False
    
    def export_configuration_summary(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export comprehensive configuration summary."""        summary = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'author': 'Fahed Mlaiel',
                'project': 'IA-Influencer Agent Platform'
            },
            'system_status': self.get_system_status(),
            'configurations': {}
        }
        
        # Export individual configuration summaries
        for name, config in self.configs.items():
            if hasattr(config, 'export_configuration'):
                summary['configurations'][name] = config.export_configuration()
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                print(f"✅ Configuration summary exported to: {output_path}")
            except Exception as e:
                print(f"❌ Failed to export summary: {e}")
        
        return summary
    
    def get_recommended_backup_strategy(self) -> Dict[str, Any]:
        """Get recommended backup strategy based on current configuration."""        active_schedules = backup_storage_config.get_active_schedules()
        
        recommendations = {
            'current_schedules': len(active_schedules),
            'recommended_improvements': [],
            'estimated_recovery_time': backup_storage_config.rto_target_hours,
            'estimated_data_loss': backup_storage_config.rpo_target_hours,
            'compliance_status': 'compliant' if active_schedules else 'non-compliant'
        }
        
        # Check for missing critical backups
        critical_schedules = ['database_daily', 'config_daily', 'user_data_hourly']
        missing_schedules = [s for s in critical_schedules if s not in active_schedules]
        
        if missing_schedules:
            recommendations['recommended_improvements'].append(
                f"Enable missing critical schedules: {', '.join(missing_schedules)}"
            )
        
        # Check storage utilization
        storage_usage = backup_storage_config.get_storage_usage_summary()
        for dest_name, usage in storage_usage.items():
            if usage['usage_percentage'] > 80:
                recommendations['recommended_improvements'].append(
                    f"Storage {dest_name} is {usage['usage_percentage']}% full - consider expansion"
                )
        
        return recommendations

# Global storage orchestrator instance
storage_orchestrator = StorageOrchestrator()

def initialize_storage_system() -> bool:
    """Initialize the complete storage system."""    return storage_orchestrator.initialize()

def get_storage_orchestrator() -> StorageOrchestrator:
    """Get the global storage orchestrator instance."""    return storage_orchestrator

# Auto-initialize in production environments
if os.getenv('ENVIRONMENT') in ['production', 'staging']:
    initialize_storage_system()

__all__ = [
    'StorageOrchestrator',
    'storage_orchestrator',
    'initialize_storage_system',
    'get_storage_orchestrator'
]
