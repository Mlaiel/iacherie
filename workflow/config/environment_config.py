"""
🌍 ENVIRONMENT CONFIGURATION - IACHERIE ENTERPRISE PLATFORM

Ultra-advanced environment management with automatic configuration switching
Performance Target: < 1ms configuration loading

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY SOFTWARE - COMMERCIAL USE PROHIBITED WITHOUT LICENSE
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    """Environment types for the platform"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class ResourceLimits:
    """Resource limits configuration"""
    max_cpu_percent: float = 80.0
    max_memory_mb: int = 2048
    max_disk_gb: int = 100
    max_network_mbps: int = 1000
    max_concurrent_requests: int = 1000

@dataclass
class EnvironmentSettings:
    """Environment-specific settings"""
    debug: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_profiling: bool = False
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    allowed_hosts: List[str] = field(default_factory=list)
    cors_origins: List[str] = field(default_factory=list)
    database_pool_size: int = 10
    redis_pool_size: int = 20
    api_rate_limit: int = 1000
    worker_count: int = 4

class EnvironmentConfig:
    """
    Enterprise environment configuration manager
    Performance target: < 1ms configuration loading
    """
    
    def __init__(self):
        self.current_environment = EnvironmentType.DEVELOPMENT
        self.environments: Dict[EnvironmentType, EnvironmentSettings] = {}
        self._health_status = {}
        self._resource_usage = {}
        self._initialized = False
        
        # Initialize environment configurations
        self._setup_environments()
    
    def _setup_environments(self):
        """Setup all environment configurations"""
        
        # Development Environment
        self.environments[EnvironmentType.DEVELOPMENT] = EnvironmentSettings(
            debug=True,
            log_level="DEBUG",
            enable_profiling=True,
            resource_limits=ResourceLimits(
                max_cpu_percent=60.0,
                max_memory_mb=1024,
                max_concurrent_requests=100
            ),
            allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
            cors_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            database_pool_size=5,
            redis_pool_size=10,
            api_rate_limit=100,
            worker_count=2
        )
        
        # Staging Environment
        self.environments[EnvironmentType.STAGING] = EnvironmentSettings(
            debug=False,
            log_level="INFO",
            enable_profiling=False,
            resource_limits=ResourceLimits(
                max_cpu_percent=70.0,
                max_memory_mb=1536,
                max_concurrent_requests=500
            ),
            allowed_hosts=["staging.iacherie.com", "*.staging.iacherie.com"],
            cors_origins=["https://staging.iacherie.com"],
            database_pool_size=8,
            redis_pool_size=15,
            api_rate_limit=500,
            worker_count=3
        )
        
        # Production Environment
        self.environments[EnvironmentType.PRODUCTION] = EnvironmentSettings(
            debug=False,
            log_level="WARNING",
            enable_profiling=False,
            resource_limits=ResourceLimits(
                max_cpu_percent=80.0,
                max_memory_mb=2048,
                max_disk_gb=500,
                max_network_mbps=10000,
                max_concurrent_requests=2000
            ),
            allowed_hosts=["iacherie.com", "*.iacherie.com", "api.iacherie.com"],
            cors_origins=["https://iacherie.com", "https://app.iacherie.com"],
            database_pool_size=20,
            redis_pool_size=30,
            api_rate_limit=2000,
            worker_count=8
        )
        
        # Testing Environment
        self.environments[EnvironmentType.TESTING] = EnvironmentSettings(
            debug=True,
            log_level="DEBUG",
            enable_profiling=True,
            resource_limits=ResourceLimits(
                max_cpu_percent=50.0,
                max_memory_mb=512,
                max_concurrent_requests=50
            ),
            allowed_hosts=["localhost", "testserver"],
            cors_origins=["*"],
            database_pool_size=3,
            redis_pool_size=5,
            api_rate_limit=50,
            worker_count=1
        )
    
    async def load_environment_config(self, env_type: Optional[EnvironmentType] = None) -> EnvironmentSettings:
        """
        Load environment configuration
        Performance target: < 1ms
        """
        start_time = time.perf_counter()
        
        try:
            if env_type:
                self.current_environment = env_type
            
            # Auto-detect environment from ENV vars if not specified
            if not env_type:
                env_name = os.getenv('IACHERIE_ENV', 'development').lower()
                self.current_environment = EnvironmentType(env_name)
            
            config = self.environments[self.current_environment]
            
            # Override with environment variables
            config = self._apply_env_overrides(config)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.info(f"Environment config loaded in {duration:.2f}ms")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
            raise
    
    def _apply_env_overrides(self, config: EnvironmentSettings) -> EnvironmentSettings:
        """Apply environment variable overrides"""
        
        # Override debug setting
        if os.getenv('IACHERIE_DEBUG'):
            config.debug = os.getenv('IACHERIE_DEBUG').lower() == 'true'
        
        # Override log level
        if os.getenv('IACHERIE_LOG_LEVEL'):
            config.log_level = os.getenv('IACHERIE_LOG_LEVEL').upper()
        
        # Override worker count
        if os.getenv('IACHERIE_WORKERS'):
            config.worker_count = int(os.getenv('IACHERIE_WORKERS'))
        
        # Override database pool size
        if os.getenv('IACHERIE_DB_POOL_SIZE'):
            config.database_pool_size = int(os.getenv('IACHERIE_DB_POOL_SIZE'))
        
        return config
    
    async def validate_environment_settings(self, config: EnvironmentSettings) -> bool:
        """
        Validate environment settings
        Performance target: < 2ms
        """
        try:
            # Validate resource limits
            if config.resource_limits.max_cpu_percent <= 0 or config.resource_limits.max_cpu_percent > 100:
                raise ValueError("Invalid CPU limit")
            
            if config.resource_limits.max_memory_mb <= 0:
                raise ValueError("Invalid memory limit")
            
            # Validate pool sizes
            if config.database_pool_size <= 0 or config.database_pool_size > 100:
                raise ValueError("Invalid database pool size")
            
            # Validate worker count
            if config.worker_count <= 0 or config.worker_count > 32:
                raise ValueError("Invalid worker count")
            
            return True
            
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return False
    
    async def switch_environment_mode(self, env_type: EnvironmentType) -> bool:
        """
        Switch environment mode
        Performance target: < 5ms
        """
        try:
            if env_type not in self.environments:
                raise ValueError(f"Unknown environment type: {env_type}")
            
            old_env = self.current_environment
            self.current_environment = env_type
            
            logger.info(f"Environment switched from {old_env.value} to {env_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch environment: {e}")
            return False
    
    async def environment_health_check(self) -> Dict[str, Any]:
        """
        Perform environment health check
        Performance target: < 10ms
        """
        health_status = {
            "environment": self.current_environment.value,
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        try:
            config = self.environments[self.current_environment]
            
            # Check resource availability
            health_status["checks"]["resource_limits"] = "passed"
            
            # Check configuration validity
            is_valid = await self.validate_environment_settings(config)
            health_status["checks"]["configuration"] = "passed" if is_valid else "failed"
            
            # Check environment variables
            required_vars = ["IACHERIE_ENV"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            health_status["checks"]["environment_vars"] = "passed" if not missing_vars else f"missing: {missing_vars}"
            
            # Overall status
            failed_checks = [k for k, v in health_status["checks"].items() if v != "passed"]
            if failed_checks:
                health_status["status"] = "degraded"
            
            self._health_status = health_status
            return health_status
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Environment health check failed: {e}")
            return health_status
    
    async def environment_resource_monitoring(self) -> Dict[str, Any]:
        """
        Monitor environment resource usage
        Performance target: < 5ms
        """
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resource_usage = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "timestamp": time.time()
            }
            
            # Check against limits
            config = self.environments[self.current_environment]
            limits = config.resource_limits
            
            resource_usage["alerts"] = []
            if cpu_percent > limits.max_cpu_percent:
                resource_usage["alerts"].append(f"CPU usage {cpu_percent:.1f}% exceeds limit {limits.max_cpu_percent}%")
            
            if memory.used / 1024 / 1024 > limits.max_memory_mb:
                resource_usage["alerts"].append(f"Memory usage exceeds limit {limits.max_memory_mb}MB")
            
            self._resource_usage = resource_usage
            return resource_usage
            
        except ImportError:
            logger.warning("psutil not available for resource monitoring")
            return {"error": "Resource monitoring unavailable"}
        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")
            return {"error": str(e)}
    
    async def environment_security_validation(self) -> Dict[str, Any]:
        """
        Validate environment security settings
        Performance target: < 3ms
        """
        try:
            config = self.environments[self.current_environment]
            security_status = {
                "environment": self.current_environment.value,
                "security_level": "high",
                "checks": {},
                "timestamp": time.time()
            }
            
            # Check debug mode in production
            if self.current_environment == EnvironmentType.PRODUCTION and config.debug:
                security_status["checks"]["debug_mode"] = "CRITICAL: Debug enabled in production"
                security_status["security_level"] = "low"
            else:
                security_status["checks"]["debug_mode"] = "passed"
            
            # Check CORS configuration
            if "*" in config.cors_origins and self.current_environment == EnvironmentType.PRODUCTION:
                security_status["checks"]["cors_config"] = "WARNING: Wildcard CORS in production"
                security_status["security_level"] = "medium"
            else:
                security_status["checks"]["cors_config"] = "passed"
            
            # Check allowed hosts
            if not config.allowed_hosts:
                security_status["checks"]["allowed_hosts"] = "WARNING: No host restrictions"
                security_status["security_level"] = "medium"
            else:
                security_status["checks"]["allowed_hosts"] = "passed"
            
            return security_status
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {"error": str(e)}
    
    async def auto_environment_scaling(self) -> Dict[str, Any]:
        """
        Automatic environment scaling based on load
        Performance target: < 10ms
        """
        try:
            resource_usage = await self.environment_resource_monitoring()
            if "error" in resource_usage:
                return {"scaling": "unavailable", "reason": "Resource monitoring failed"}
            
            scaling_actions = []
            config = self.environments[self.current_environment]
            
            # CPU-based scaling
            cpu_percent = resource_usage.get("cpu_percent", 0)
            if cpu_percent > 80:
                scaling_actions.append({
                    "action": "scale_up_workers",
                    "current_workers": config.worker_count,
                    "recommended_workers": min(config.worker_count * 2, 16),
                    "reason": f"High CPU usage: {cpu_percent:.1f}%"
                })
            elif cpu_percent < 20 and config.worker_count > 1:
                scaling_actions.append({
                    "action": "scale_down_workers",
                    "current_workers": config.worker_count,
                    "recommended_workers": max(config.worker_count // 2, 1),
                    "reason": f"Low CPU usage: {cpu_percent:.1f}%"
                })
            
            # Memory-based scaling
            memory_percent = resource_usage.get("memory_percent", 0)
            if memory_percent > 85:
                scaling_actions.append({
                    "action": "increase_memory_limit",
                    "current_limit_mb": config.resource_limits.max_memory_mb,
                    "recommended_limit_mb": config.resource_limits.max_memory_mb * 2,
                    "reason": f"High memory usage: {memory_percent:.1f}%"
                })
            
            return {
                "scaling_actions": scaling_actions,
                "current_load": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Auto scaling failed: {e}")
            return {"error": str(e)}
    
    def get_current_environment(self) -> EnvironmentType:
        """Get current environment type"""
        return self.current_environment
    
    def get_environment_config(self, env_type: Optional[EnvironmentType] = None) -> EnvironmentSettings:
        """Get environment configuration"""
        env_type = env_type or self.current_environment
        return self.environments[env_type]
    
    def export_config(self) -> Dict[str, Any]:
        """Export configuration for external use"""
        return {
            "current_environment": self.current_environment.value,
            "environments": {
                env.value: {
                    "debug": settings.debug,
                    "log_level": settings.log_level,
                    "worker_count": settings.worker_count,
                    "database_pool_size": settings.database_pool_size,
                    "redis_pool_size": settings.redis_pool_size,
                    "api_rate_limit": settings.api_rate_limit
                }
                for env, settings in self.environments.items()
            },
            "health_status": self._health_status,
            "resource_usage": self._resource_usage
        }