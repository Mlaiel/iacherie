"""
Advanced Queue Configuration System - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_config.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Configuration Management System
Responsibility: Advanced configuration, environment detection, adaptive settings
Technologies: Dynamic Configuration, Environment Adaptation, Performance Tuning
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Environment detection → Resource analysis → Performance profiling → Configuration generation →
Security assessment → Optimization tuning → Monitoring setup → Dynamic adaptation
"""

import os
import psutil
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Types of deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class ResourceTier(Enum):
    """Resource availability tiers"""
    MINIMAL = "minimal"      # < 4GB RAM, < 2 CPU cores
    STANDARD = "standard"    # 4-16GB RAM, 2-8 CPU cores
    HIGH = "high"           # 16-64GB RAM, 8-32 CPU cores
    EXTREME = "extreme"      # > 64GB RAM, > 32 CPU cores


class SecurityProfile(Enum):
    """Security configuration profiles"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


@dataclass
class SystemResources:
    """System resource information"""
    total_memory_gb: float
    available_memory_gb: float
    cpu_cores: int
    cpu_threads: int
    cpu_frequency_mhz: float
    disk_space_gb: float
    network_speed_mbps: Optional[float] = None
    gpu_available: bool = False
    gpu_memory_gb: Optional[float] = None


@dataclass
class QueueConfiguration:
    """Complete queue system configuration"""
    
    # Basic settings
    max_workers: int
    max_queue_size: int
    worker_timeout_seconds: int
    queue_timeout_seconds: int
    
    # Performance settings
    batch_size: int
    prefetch_count: int
    retry_count: int
    retry_delay_seconds: float
    heartbeat_interval_seconds: int
    
    # Memory settings
    memory_limit_mb: int
    memory_threshold_percent: float
    garbage_collection_interval: int
    
    # Security settings
    encryption_enabled: bool
    auth_required: bool
    ssl_enabled: bool
    token_expiry_hours: int
    
    # Monitoring settings
    monitoring_enabled: bool
    metrics_retention_days: int
    alert_threshold_percent: float
    health_check_interval_seconds: int
    
    # Analytics settings
    analytics_enabled: bool
    analytics_batch_size: int
    analytics_flush_interval_seconds: int
    
    # Advanced features
    ml_optimization_enabled: bool
    predictive_scaling_enabled: bool
    auto_recovery_enabled: bool
    adaptive_priority_enabled: bool


class QueueConfigurationManager:
    """Advanced configuration manager for queue systems"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.system_resources = self._detect_system_resources()
        self.environment_type = self._detect_environment_type()
        self.resource_tier = self._determine_resource_tier()
        
        self.base_config_file = self.config_dir / "queue_base_config.yaml"
        self.override_config_file = self.config_dir / "queue_override_config.yaml"
        self.generated_config_file = self.config_dir / "queue_generated_config.yaml"
    
    def generate_optimal_configuration(
        self,
        security_profile: SecurityProfile = SecurityProfile.STANDARD,
        performance_priority: str = "balanced",  # "speed", "memory", "balanced"
        custom_overrides: Optional[Dict[str, Any]] = None
    ) -> QueueConfiguration:
        """Generate optimal configuration based on system resources and requirements"""
        
        logger.info("🎯 Generating optimal queue configuration")
        logger.info(f"Environment: {self.environment_type.value}")
        logger.info(f"Resource Tier: {self.resource_tier.value}")
        logger.info(f"Security Profile: {security_profile.value}")
        logger.info(f"Performance Priority: {performance_priority}")
        
        # Start with base configuration
        config = self._get_base_configuration()
        
        # Apply resource tier optimizations
        config = self._apply_resource_tier_optimizations(config)
        
        # Apply environment-specific settings
        config = self._apply_environment_settings(config)
        
        # Apply security profile
        config = self._apply_security_profile(config, security_profile)
        
        # Apply performance optimizations
        config = self._apply_performance_optimizations(config, performance_priority)
        
        # Apply custom overrides
        if custom_overrides:
            config = self._apply_custom_overrides(config, custom_overrides)
        
        # Save generated configuration
        self._save_configuration(config)
        
        logger.info("✅ Optimal configuration generated successfully")
        self._log_configuration_summary(config)
        
        return config
    
    def load_configuration(self) -> Optional[QueueConfiguration]:
        """Load existing configuration from file"""
        
        try:
            if self.generated_config_file.exists():
                config_data = self._load_yaml_file(self.generated_config_file)
                return QueueConfiguration(**config_data)
            
            logger.info("No existing configuration found, generating new one")
            return None
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
    
    def validate_configuration(self, config: QueueConfiguration) -> Dict[str, Any]:
        """Validate configuration against system capabilities"""
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Check memory requirements
        required_memory_mb = config.max_workers * config.memory_limit_mb
        available_memory_mb = self.system_resources.available_memory_gb * 1024
        
        if required_memory_mb > available_memory_mb * 0.8:
            validation_results['warnings'].append(
                f"High memory usage: {required_memory_mb}MB required, "
                f"{available_memory_mb:.0f}MB available"
            )
        
        if required_memory_mb > available_memory_mb:
            validation_results['errors'].append(
                f"Insufficient memory: {required_memory_mb}MB required, "
                f"{available_memory_mb:.0f}MB available"
            )
            validation_results['valid'] = False
        
        # Check CPU requirements
        if config.max_workers > self.system_resources.cpu_threads * 2:
            validation_results['warnings'].append(
                f"High worker count: {config.max_workers} workers for "
                f"{self.system_resources.cpu_threads} CPU threads"
            )
        
        # Check disk space for analytics
        if config.analytics_enabled:
            estimated_daily_data_gb = (config.analytics_batch_size * 1000) / (1024**3)
            required_disk_gb = estimated_daily_data_gb * config.metrics_retention_days
            
            if required_disk_gb > self.system_resources.disk_space_gb * 0.1:
                validation_results['warnings'].append(
                    f"High disk usage for analytics: {required_disk_gb:.2f}GB estimated"
                )
        
        # Performance recommendations
        if config.batch_size < 10:
            validation_results['recommendations'].append(
                "Consider increasing batch_size for better throughput"
            )
        
        if config.prefetch_count < config.max_workers:
            validation_results['recommendations'].append(
                "Consider setting prefetch_count >= max_workers"
            )
        
        return validation_results
    
    def get_performance_tuning_recommendations(
        self, 
        current_metrics: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Get performance tuning recommendations based on current metrics"""
        
        recommendations = []
        
        if current_metrics:
            # Analyze current performance
            success_rate = current_metrics.get('success_rate', 1.0)
            avg_response_time = current_metrics.get('avg_response_time_ms', 0)
            memory_usage = current_metrics.get('memory_usage_percent', 0)
            cpu_usage = current_metrics.get('cpu_usage_percent', 0)
            
            if success_rate < 0.95:
                recommendations.append(
                    "Low success rate detected. Consider increasing retry_count or worker_timeout_seconds"
                )
            
            if avg_response_time > 5000:
                recommendations.append(
                    "High response time. Consider increasing max_workers or batch_size"
                )
            
            if memory_usage > 80:
                recommendations.append(
                    "High memory usage. Consider reducing memory_limit_mb or max_workers"
                )
            
            if cpu_usage > 90:
                recommendations.append(
                    "High CPU usage. Consider reducing max_workers or increasing worker_timeout_seconds"
                )
        
        # General recommendations based on system resources
        if self.resource_tier == ResourceTier.EXTREME:
            recommendations.append(
                "High-end system detected. Consider enabling ML optimization and predictive scaling"
            )
        
        if self.system_resources.gpu_available:
            recommendations.append(
                "GPU detected. Consider enabling GPU-accelerated processing for ML workloads"
            )
        
        if self.environment_type == EnvironmentType.PRODUCTION:
            recommendations.append(
                "Production environment. Ensure monitoring, analytics, and auto-recovery are enabled"
            )
        
        return recommendations
    
    def export_configuration_template(
        self, 
        output_file: Optional[str] = None
    ) -> str:
        """Export configuration template with comments"""
        
        template = {
            'queue_configuration': {
                'description': 'Complete queue system configuration template',
                'author': 'Fahed Mlaiel (mlaiel@live.de)',
                'generated_for': {
                    'environment': self.environment_type.value,
                    'resource_tier': self.resource_tier.value,
                    'system_info': {
                        'memory_gb': self.system_resources.total_memory_gb,
                        'cpu_cores': self.system_resources.cpu_cores,
                        'cpu_threads': self.system_resources.cpu_threads
                    }
                },
                
                'basic_settings': {
                    'max_workers': {
                        'value': 50,
                        'description': 'Maximum number of concurrent workers',
                        'min': 1,
                        'max': self.system_resources.cpu_threads * 4,
                        'recommendation': self.system_resources.cpu_threads * 2
                    },
                    'max_queue_size': {
                        'value': 10000,
                        'description': 'Maximum size of the task queue',
                        'min': 100,
                        'max': 1000000,
                        'recommendation': 'Based on expected workload'
                    }
                },
                
                'performance_settings': {
                    'batch_size': {
                        'value': 50,
                        'description': 'Number of tasks processed in each batch',
                        'recommendation': 'Optimize based on task complexity'
                    },
                    'prefetch_count': {
                        'value': 100,
                        'description': 'Number of tasks to prefetch',
                        'recommendation': 'Should be >= max_workers'
                    }
                },
                
                'security_settings': {
                    'encryption_enabled': {
                        'value': True,
                        'description': 'Enable encryption for queue data',
                        'recommendation': 'Always enable in production'
                    },
                    'auth_required': {
                        'value': True,
                        'description': 'Require authentication for queue access',
                        'recommendation': 'Enable for production environments'
                    }
                },
                
                'monitoring_settings': {
                    'monitoring_enabled': {
                        'value': True,
                        'description': 'Enable comprehensive monitoring',
                        'recommendation': 'Essential for production systems'
                    },
                    'metrics_retention_days': {
                        'value': 90,
                        'description': 'Number of days to retain metrics',
                        'recommendation': 'Balance storage costs with analysis needs'
                    }
                }
            }
        }
        
        output_path = output_file or str(self.config_dir / "queue_config_template.yaml")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.info(f"Configuration template exported to: {output_path}")
        return output_path
    
    # Private methods
    
    def _detect_system_resources(self) -> SystemResources:
        """Detect available system resources"""
        
        memory = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()
        disk = psutil.disk_usage('/')
        
        # Try to detect GPU
        gpu_available = False
        gpu_memory_gb = None
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_available = True
                gpu_memory_gb = gpus[0].memoryTotal / 1024  # Convert MB to GB
        except ImportError:
            pass
        
        return SystemResources(
            total_memory_gb=memory.total / (1024**3),
            available_memory_gb=memory.available / (1024**3),
            cpu_cores=psutil.cpu_count(logical=False),
            cpu_threads=psutil.cpu_count(logical=True),
            cpu_frequency_mhz=cpu_freq.current if cpu_freq else 0,
            disk_space_gb=disk.free / (1024**3),
            gpu_available=gpu_available,
            gpu_memory_gb=gpu_memory_gb
        )
    
    def _detect_environment_type(self) -> EnvironmentType:
        """Detect deployment environment type"""
        
        # Check environment variables
        env_type = os.getenv('ENVIRONMENT', '').lower()
        app_env = os.getenv('APP_ENV', '').lower()
        
        if env_type in ['prod', 'production'] or app_env in ['prod', 'production']:
            return EnvironmentType.PRODUCTION
        elif env_type in ['staging', 'stage'] or app_env in ['staging', 'stage']:
            return EnvironmentType.STAGING
        elif env_type in ['test', 'testing'] or app_env in ['test', 'testing']:
            return EnvironmentType.TESTING
        elif env_type in ['enterprise'] or app_env in ['enterprise']:
            return EnvironmentType.ENTERPRISE
        else:
            return EnvironmentType.DEVELOPMENT
    
    def _determine_resource_tier(self) -> ResourceTier:
        """Determine resource availability tier"""
        
        memory_gb = self.system_resources.total_memory_gb
        cpu_cores = self.system_resources.cpu_cores
        
        if memory_gb >= 64 and cpu_cores >= 32:
            return ResourceTier.EXTREME
        elif memory_gb >= 16 and cpu_cores >= 8:
            return ResourceTier.HIGH
        elif memory_gb >= 4 and cpu_cores >= 2:
            return ResourceTier.STANDARD
        else:
            return ResourceTier.MINIMAL
    
    def _get_base_configuration(self) -> Dict[str, Any]:
        """Get base configuration template"""
        
        return {
            'max_workers': 10,
            'max_queue_size': 1000,
            'worker_timeout_seconds': 60,
            'queue_timeout_seconds': 30,
            'batch_size': 10,
            'prefetch_count': 20,
            'retry_count': 3,
            'retry_delay_seconds': 1.0,
            'heartbeat_interval_seconds': 30,
            'memory_limit_mb': 512,
            'memory_threshold_percent': 80.0,
            'garbage_collection_interval': 300,
            'encryption_enabled': False,
            'auth_required': False,
            'ssl_enabled': False,
            'token_expiry_hours': 24,
            'monitoring_enabled': True,
            'metrics_retention_days': 30,
            'alert_threshold_percent': 80.0,
            'health_check_interval_seconds': 60,
            'analytics_enabled': False,
            'analytics_batch_size': 1000,
            'analytics_flush_interval_seconds': 300,
            'ml_optimization_enabled': False,
            'predictive_scaling_enabled': False,
            'auto_recovery_enabled': True,
            'adaptive_priority_enabled': False
        }
    
    def _apply_resource_tier_optimizations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on resource tier"""
        
        if self.resource_tier == ResourceTier.EXTREME:
            config.update({
                'max_workers': min(200, self.system_resources.cpu_threads * 4),
                'max_queue_size': 100000,
                'batch_size': 100,
                'prefetch_count': 500,
                'memory_limit_mb': 2048,
                'analytics_enabled': True,
                'analytics_batch_size': 10000,
                'ml_optimization_enabled': True,
                'predictive_scaling_enabled': True,
                'adaptive_priority_enabled': True
            })
            
        elif self.resource_tier == ResourceTier.HIGH:
            config.update({
                'max_workers': min(100, self.system_resources.cpu_threads * 3),
                'max_queue_size': 50000,
                'batch_size': 50,
                'prefetch_count': 200,
                'memory_limit_mb': 1024,
                'analytics_enabled': True,
                'analytics_batch_size': 5000,
                'ml_optimization_enabled': True,
                'adaptive_priority_enabled': True
            })
            
        elif self.resource_tier == ResourceTier.STANDARD:
            config.update({
                'max_workers': min(50, self.system_resources.cpu_threads * 2),
                'max_queue_size': 10000,
                'batch_size': 25,
                'prefetch_count': 100,
                'memory_limit_mb': 512,
                'analytics_enabled': True,
                'analytics_batch_size': 2000
            })
            
        else:  # MINIMAL
            config.update({
                'max_workers': min(10, self.system_resources.cpu_threads),
                'max_queue_size': 1000,
                'batch_size': 10,
                'prefetch_count': 20,
                'memory_limit_mb': 256,
                'analytics_enabled': False,
                'ml_optimization_enabled': False
            })
        
        return config
    
    def _apply_environment_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment-specific settings"""
        
        if self.environment_type in [EnvironmentType.PRODUCTION, EnvironmentType.ENTERPRISE]:
            config.update({
                'encryption_enabled': True,
                'auth_required': True,
                'ssl_enabled': True,
                'monitoring_enabled': True,
                'analytics_enabled': True,
                'metrics_retention_days': 90,
                'auto_recovery_enabled': True,
                'health_check_interval_seconds': 30
            })
            
        elif self.environment_type == EnvironmentType.STAGING:
            config.update({
                'encryption_enabled': True,
                'auth_required': True,
                'monitoring_enabled': True,
                'analytics_enabled': True,
                'metrics_retention_days': 30,
                'health_check_interval_seconds': 60
            })
            
        elif self.environment_type == EnvironmentType.TESTING:
            config.update({
                'encryption_enabled': False,
                'auth_required': False,
                'monitoring_enabled': True,
                'analytics_enabled': False,
                'metrics_retention_days': 7,
                'health_check_interval_seconds': 120
            })
            
        else:  # DEVELOPMENT
            config.update({
                'encryption_enabled': False,
                'auth_required': False,
                'ssl_enabled': False,
                'monitoring_enabled': True,
                'analytics_enabled': False,
                'metrics_retention_days': 3,
                'health_check_interval_seconds': 300
            })
        
        return config
    
    def _apply_security_profile(
        self, 
        config: Dict[str, Any], 
        security_profile: SecurityProfile
    ) -> Dict[str, Any]:
        """Apply security profile settings"""
        
        if security_profile == SecurityProfile.MAXIMUM:
            config.update({
                'encryption_enabled': True,
                'auth_required': True,
                'ssl_enabled': True,
                'token_expiry_hours': 4
            })
            
        elif security_profile == SecurityProfile.ENHANCED:
            config.update({
                'encryption_enabled': True,
                'auth_required': True,
                'ssl_enabled': True,
                'token_expiry_hours': 8
            })
            
        elif security_profile == SecurityProfile.STANDARD:
            config.update({
                'encryption_enabled': True,
                'auth_required': True,
                'token_expiry_hours': 24
            })
            
        # BASIC uses default settings
        
        return config
    
    def _apply_performance_optimizations(
        self, 
        config: Dict[str, Any], 
        performance_priority: str
    ) -> Dict[str, Any]:
        """Apply performance-focused optimizations"""
        
        if performance_priority == "speed":
            # Optimize for maximum throughput
            config.update({
                'max_workers': min(config['max_workers'] * 2, self.system_resources.cpu_threads * 4),
                'batch_size': max(config['batch_size'] * 2, 100),
                'prefetch_count': config['max_workers'] * 3,
                'worker_timeout_seconds': config['worker_timeout_seconds'] * 2,
                'memory_limit_mb': min(config['memory_limit_mb'] * 2, 
                                     int(self.system_resources.available_memory_gb * 1024 * 0.1))
            })
            
        elif performance_priority == "memory":
            # Optimize for low memory usage
            config.update({
                'max_workers': max(config['max_workers'] // 2, 1),
                'batch_size': max(config['batch_size'] // 2, 5),
                'prefetch_count': max(config['prefetch_count'] // 2, 10),
                'memory_limit_mb': max(config['memory_limit_mb'] // 2, 128),
                'garbage_collection_interval': 60  # More frequent GC
            })
        
        # "balanced" uses default optimizations
        
        return config
    
    def _apply_custom_overrides(
        self, 
        config: Dict[str, Any], 
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply custom configuration overrides"""
        
        config.update(overrides)
        return config
    
    def _save_configuration(self, config_dict: Dict[str, Any]):
        """Save configuration to file"""
        
        config_with_metadata = {
            'metadata': {
                'generated_by': 'QueueConfigurationManager',
                'author': 'Fahed Mlaiel (mlaiel@live.de)',
                'generated_at': datetime.now().isoformat(),
                'environment': self.environment_type.value,
                'resource_tier': self.resource_tier.value,
                'system_resources': asdict(self.system_resources)
            },
            'configuration': config_dict
        }
        
        with open(self.generated_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_with_metadata, f, default_flow_style=False, sort_keys=False)
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Return just the configuration part if metadata exists
        if 'configuration' in data:
            return data['configuration']
        
        return data
    
    def _log_configuration_summary(self, config: QueueConfiguration):
        """Log configuration summary"""
        
        logger.info("📋 Generated Configuration Summary:")
        logger.info(f"  Workers: {config.max_workers}")
        logger.info(f"  Queue Size: {config.max_queue_size}")
        logger.info(f"  Batch Size: {config.batch_size}")
        logger.info(f"  Memory Limit: {config.memory_limit_mb}MB per worker")
        logger.info(f"  Security: {'Enabled' if config.encryption_enabled else 'Disabled'}")
        logger.info(f"  Monitoring: {'Enabled' if config.monitoring_enabled else 'Disabled'}")
        logger.info(f"  Analytics: {'Enabled' if config.analytics_enabled else 'Disabled'}")
        logger.info(f"  ML Optimization: {'Enabled' if config.ml_optimization_enabled else 'Disabled'}")


# Factory function
def create_queue_configuration_manager(config_dir: Optional[str] = None) -> QueueConfigurationManager:
    """Create queue configuration manager instance"""
    return QueueConfigurationManager(config_dir)


# Export classes and functions
__all__ = [
    'EnvironmentType',
    'ResourceTier', 
    'SecurityProfile',
    'SystemResources',
    'QueueConfiguration',
    'QueueConfigurationManager',
    'create_queue_configuration_manager'
]
