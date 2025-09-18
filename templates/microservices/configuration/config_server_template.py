#!/usr/bin/env python3
"""
⚙️ CONFIG SERVER TEMPLATE - CENTRALIZED CONFIGURATION
=====================================================

Centralized configuration server for distributed microservices
with hot reloading and environment-specific configurations.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import json
from typing import Dict, Any

class ConfigServerTemplate:
    """Centralized configuration server"""
    
    def __init__(self):
        self.configurations: Dict[str, Dict[str, Any]] = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default configurations"""
        self.configurations = {
            "api-gateway": {
                "port": 8080,
                "timeout": 30,
                "rate_limit": 1000
            },
            "user-service": {
                "port": 8081,
                "database_pool_size": 10,
                "cache_ttl": 300
            },
            "payment-service": {
                "port": 8082,
                "encryption_enabled": True,
                "audit_logging": True
            }
        }
    
    def get_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for service"""
        return self.configurations.get(service_name, {})
    
    def update_config(self, service_name: str, config: Dict[str, Any]):
        """Update service configuration"""
        self.configurations[service_name] = config
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all service configurations"""
        return self.configurations