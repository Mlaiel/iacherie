"""API Manager - Central API Configuration & Management System
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides centralized management for all API configurations,
validation, health checking, and dynamic configuration loading.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import os

from .platform_apis import PlatformAPIConfig, PLATFORM_CONFIGS
from .payment_apis import PaymentAPIConfig, PAYMENT_CONFIGS
from .protection_apis import ProtectionAPIConfig, PROTECTION_CONFIGS
from .cloud_apis import CloudAPIConfig, CLOUD_CONFIGS
from .analytics_apis import AnalyticsAPIConfig, ANALYTICS_CONFIGS
from .communication_apis import CommunicationAPIConfig, COMMUNICATION_CONFIGS

logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """
API status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class ConfigurationSource(Enum):
    """Configuration source types"""

    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    REMOTE = "remote"

@dataclass
class APIHealthCheck:
    """API health check result"""
    api_name: str
    status: APIStatus
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    status_code: Optional[int] = None

@dataclass
class APIUsageMetrics:
    """
API usage metrics"""
    api_name: str
    requests_count: int
    success_rate: float
    average_response_time: float
    error_count: int
    last_reset: datetime

class APIConfigValidator:
    """
Validates API configurations"""
    
    def __init__(self):
        self.required_fields = {
            'platform': ['platform_name', 'base_url', 'api_version'],
            'payment': ['provider_name', 'base_url', 'api_version'],
            'protection': ['service_name', 'base_url', 'api_version'],
            'cloud': ['service_name', 'base_url', 'region'],
            'analytics': ['service_name', 'base_url', 'api_version'],
            'communication': ['service_name', 'base_url', 'api_version']
        }
    
    def validate_config(self, config: Any, config_type: str = "unknown") -> bool:
        """
        Validate API configuration
        
        Args:
            config: Configuration object to validate
            config_type: Type of configuration (platform, payment, etc.)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not config:
                logger.error("Configuration is None or empty")
                return False
            
            # Check required fields based on config type
            required = self.required_fields.get(config_type, [])
            for field in required:
                if not hasattr(config, field) or not getattr(config, field):
                    logger.error(f"Missing required field: {field} in {config_type} config")
                    return False
            
            # Validate URLs
            if hasattr(config, 'base_url') and config.base_url:
                if not self._validate_url(config.base_url):
                    logger.error(f"Invalid base_url: {config.base_url}")
                    return False
            
            # Validate rate limits
            if hasattr(config, 'rate_limit_per_minute'):
                if not isinstance(config.rate_limit_per_minute, int) or config.rate_limit_per_minute <= 0:
                    logger.error("Invalid rate_limit_per_minute")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

class APIManager:
    """
Central API management system"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.configs: Dict[str, Any] = {}
        self.health_checks: Dict[str, APIHealthCheck] = {}
        self.usage_metrics: Dict[str, APIUsageMetrics] = {}
        self.validator = APIConfigValidator()
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all API configurations"""
        try:
            # Load platform configurations
            for name, config in PLATFORM_CONFIGS.items():
                self.register_api_config(f"platform_{name}", config, "platform")
            
            # Load payment configurations
            for name, config in PAYMENT_CONFIGS.items():
                self.register_api_config(f"payment_{name}", config, "payment")
            
            # Load protection configurations
            for name, config in PROTECTION_CONFIGS.items():
                self.register_api_config(f"protection_{name}", config, "protection")
            
            # Load cloud configurations
            for name, config in CLOUD_CONFIGS.items():
                self.register_api_config(f"cloud_{name}", config, "cloud")
            
            # Load analytics configurations
            for name, config in ANALYTICS_CONFIGS.items():
                self.register_api_config(f"analytics_{name}", config, "analytics")
            
            # Load communication configurations
            for name, config in COMMUNICATION_CONFIGS.items():
                self.register_api_config(f"communication_{name}", config, "communication")
            
            logger.info(f"Loaded {len(self.configs)} API configurations for {self.environment} environment")
            
        except Exception as e:
            logger.error(f"Failed to load API configurations: {e}")
            raise
    
    def register_api_config(self, api_name: str, config: Any, config_type: str = "unknown"):
        """
        Register API configuration
        
        Args:
            api_name: Unique API identifier
            config: Configuration object
            config_type: Type of configuration
        """
        try:
            # Validate configuration
            if not self.validator.validate_config(config, config_type):
                raise ValueError(f"Invalid configuration for {api_name}")
            
            # Get environment-specific configuration
            env_config = config.get_environment_config(self.environment) if hasattr(config, 'get_environment_config') else config
            
            self.configs[api_name] = {
                'config': env_config,
                'type': config_type,
                'registered_at': datetime.utcnow(),
                'status': APIStatus.ACTIVE
            }
            
            # Initialize usage metrics
            self.usage_metrics[api_name] = APIUsageMetrics(
                api_name=api_name,
                requests_count=0,
                success_rate=0.0,
                average_response_time=0.0,
                error_count=0,
                last_reset=datetime.utcnow()
            )
            
            logger.info(f"Registered API configuration: {api_name}")
            
        except Exception as e:
            logger.error(f"Failed to register API configuration {api_name}: {e}")
            raise
    
    def get_api_config(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Get API configuration by name"""
        return self.configs.get(api_name, {}).get('config')
    
    def get_all_configs(self) -> Dict[str, Any]:
        """
Get all API configurations"""
        return {name: data['config'] for name, data in self.configs.items()}
    
    def get_configs_by_type(self, config_type: str) -> Dict[str, Any]:
        """
Get configurations by type"""
        return {
            name: data['config'] 
            for name, data in self.configs.items() 
            if data['type'] == config_type
        }
    
    def get_active_configs(self) -> Dict[str, Any]:
        """
Get only active configurations"""
        return {
            name: data['config'] 
            for name, data in self.configs.items() 
            if data['status'] == APIStatus.ACTIVE
        }
    
    async def check_api_health(self, api_name: str) -> APIHealthCheck:
        """
        Check health of specific API
        
        Args:
            api_name: API to check
            
        Returns:
            APIHealthCheck result
        """
        try:
            config = self.get_api_config(api_name)
            if not config:
                return APIHealthCheck(
                    api_name=api_name,
                    status=APIStatus.ERROR,
                    response_time_ms=0.0,
                    last_check=datetime.utcnow(),
                    error_message="Configuration not found"
                )
            
            # Extract base URL for health check
            base_url = config.get('base_url')
            if not base_url:
                return APIHealthCheck(
                    api_name=api_name,
                    status=APIStatus.ERROR,
                    response_time_ms=0.0,
                    last_check=datetime.utcnow(),
                    error_message="Base URL not configured"
                )
            
            # Perform health check
            start_time = datetime.utcnow()
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                try:
                    # Try a simple HEAD request to check if API is reachable
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with session.head(base_url, timeout=timeout) as response:
                        end_time = datetime.utcnow()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        
                        if response.status < 400:
                            status = APIStatus.ACTIVE
                            error_message = None
                        else:
                            status = APIStatus.ERROR
                            error_message = f"HTTP {response.status}"
                        
                        health_check = APIHealthCheck(
                            api_name=api_name,
                            status=status,
                            response_time_ms=response_time,
                            last_check=datetime.utcnow(),
                            error_message=error_message,
                            status_code=response.status
                        )
                        
                except asyncio.TimeoutError:
                    health_check = APIHealthCheck(
                        api_name=api_name,
                        status=APIStatus.ERROR,
                        response_time_ms=10000.0,
                        last_check=datetime.utcnow(),
                        error_message="Request timeout"
                    )
                except Exception as e:
                    health_check = APIHealthCheck(
                        api_name=api_name,
                        status=APIStatus.ERROR,
                        response_time_ms=0.0,
                        last_check=datetime.utcnow(),
                        error_message=str(e)
                    )
            
            # Store health check result
            self.health_checks[api_name] = health_check
            return health_check
            
        except Exception as e:
            logger.error(f"Health check failed for {api_name}: {e}")
            return APIHealthCheck(
                api_name=api_name,
                status=APIStatus.ERROR,
                response_time_ms=0.0,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_all_apis_health(self) -> Dict[str, APIHealthCheck]:
        """Check health of all APIs"""
        tasks = []
        for api_name in self.configs.keys():
            tasks.append(self.check_api_health(api_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            api_name = list(self.configs.keys())[i]
            if isinstance(result, Exception):
                health_results[api_name] = APIHealthCheck(
                    api_name=api_name,
                    status=APIStatus.ERROR,
                    response_time_ms=0.0,
                    last_check=datetime.utcnow(),
                    error_message=str(result)
                )
            else:
                health_results[api_name] = result
        
        return health_results
    
    def update_usage_metrics(self, api_name: str, success: bool, response_time: float):
        """
Update API usage metrics"""
        if api_name not in self.usage_metrics:
            return
        
        metrics = self.usage_metrics[api_name]
        metrics.requests_count += 1
        
        if not success:
            metrics.error_count += 1
        
        # Update success rate
        metrics.success_rate = ((metrics.requests_count - metrics.error_count) / metrics.requests_count) * 100
        
        # Update average response time (simple moving average)
        if metrics.requests_count == 1:
            metrics.average_response_time = response_time
        else:
            metrics.average_response_time = (metrics.average_response_time + response_time) / 2
    
    def get_usage_metrics(self, api_name: str) -> Optional[APIUsageMetrics]:
        """
Get usage metrics for specific API"""
        return self.usage_metrics.get(api_name)
    
    def get_all_usage_metrics(self) -> Dict[str, APIUsageMetrics]:
        """
Get usage metrics for all APIs"""
        return self.usage_metrics.copy()
    
    def reset_usage_metrics(self, api_name: Optional[str] = None):
        """
Reset usage metrics for specific API or all APIs"""
        if api_name:
            if api_name in self.usage_metrics:
                metrics = self.usage_metrics[api_name]
                metrics.requests_count = 0
                metrics.success_rate = 0.0
                metrics.average_response_time = 0.0
                metrics.error_count = 0
                metrics.last_reset = datetime.utcnow()
        else:
            for metrics in self.usage_metrics.values():
                metrics.requests_count = 0
                metrics.success_rate = 0.0
                metrics.average_response_time = 0.0
                metrics.error_count = 0
                metrics.last_reset = datetime.utcnow()
    
    def set_api_status(self, api_name: str, status: APIStatus):
        """
Set API status"""
        if api_name in self.configs:
            self.configs[api_name]['status'] = status
            logger.info(f"API {api_name} status changed to {status.value}")
    
    def get_api_status(self, api_name: str) -> Optional[APIStatus]:
        """Get API status"""
        return self.configs.get(api_name, {}).get('status')
    
    def export_configuration(self, file_path: str):
        """
Export current configuration to file"""
        try:
            export_data = {
                'environment': self.environment,
                'exported_at': datetime.utcnow().isoformat(),
                'configurations': {}
            }
            
            for api_name, data in self.configs.items():
                config = data['config']
                # Convert config object to dict if needed
                if hasattr(config, '__dict__'):
                    config_dict = config.__dict__
                else:
                    config_dict = config
                
                export_data['configurations'][api_name] = {
                    'config': config_dict,
                    'type': data['type'],
                    'status': data['status'].value
                }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Configuration exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise
    
    def get_summary(self) -> Dict[str, Any]:
        """Get API manager summary"""
        active_count = sum(1 for data in self.configs.values() if data['status'] == APIStatus.ACTIVE)
        inactive_count = len(self.configs) - active_count
        
        return {
            'environment': self.environment,
            'total_apis': len(self.configs),
            'active_apis': active_count,
            'inactive_apis': inactive_count,
            'last_health_check': max([hc.last_check for hc in self.health_checks.values()]) if self.health_checks else None,
            'total_requests': sum(metrics.requests_count for metrics in self.usage_metrics.values()),
            'overall_success_rate': sum(metrics.success_rate for metrics in self.usage_metrics.values()) / len(self.usage_metrics) if self.usage_metrics else 0
        }
