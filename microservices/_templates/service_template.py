#!/usr/bin/env python3
"""
🔧 Enterprise Microservice Template
==================================

Template for creating new enterprise-grade microservices.
Provides standardized structure, logging, health checks, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


@dataclass
class ServiceConfig:
    """Configuration for enterprise microservice."""
    service_name: str
    service_version: str = "1.0.0"
    description: str = ""
    port: int = 8000
    health_check_interval: int = 30
    max_retries: int = 3
    timeout: int = 30
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class EnterpriseServiceBase(ABC):
    """
    🏗️ Base class for all enterprise microservices.
    
    Provides standard functionality for:
    - Service lifecycle management
    - Health checks and monitoring
    - Configuration management
    - Error handling and resilience
    - Logging and observability
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize the enterprise service."""
        self.config = config
        self.service_id = str(uuid.uuid4())
        self.status = "initializing"
        self.health_status = "unknown"
        self.start_time: Optional[datetime] = None
        self.metrics: Dict[str, Any] = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'last_health_check': None,
            'uptime_seconds': 0
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"{config.service_name}.{self.service_id[:8]}")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"🏗️ Initializing enterprise service: {config.service_name}")
    
    async def start(self) -> bool:
        """Start the enterprise service."""
        try:
            self.logger.info(f"🚀 Starting service: {self.config.service_name}")
            self.start_time = datetime.now()
            self.status = "starting"
            
            # Initialize service-specific components
            await self._initialize()
            
            # Start health check loop
            asyncio.create_task(self._health_check_loop())
            
            self.status = "running"
            self.health_status = "healthy"
            
            self.logger.info(f"✅ Service started successfully: {self.config.service_name}")
            return True
            
        except Exception as e:
            self.status = "failed"
            self.health_status = "unhealthy"
            self.logger.error(f"❌ Failed to start service {self.config.service_name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the enterprise service."""
        try:
            self.logger.info(f"🛑 Stopping service: {self.config.service_name}")
            self.status = "stopping"
            
            # Cleanup service-specific resources
            await self._cleanup()
            
            self.status = "stopped"
            self.health_status = "stopped"
            
            self.logger.info(f"✅ Service stopped successfully: {self.config.service_name}")
            return True
            
        except Exception as e:
            self.status = "error"
            self.logger.error(f"❌ Error stopping service {self.config.service_name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Update uptime
            if self.start_time:
                self.metrics['uptime_seconds'] = (datetime.now() - self.start_time).total_seconds()
            
            # Perform service-specific health checks
            service_health = await self._service_health_check()
            
            health_data = {
                'service_name': self.config.service_name,
                'service_id': self.service_id,
                'service_version': self.config.service_version,
                'status': self.status,
                'health_status': self.health_status,
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': self.metrics['uptime_seconds'],
                'metrics': self.metrics.copy(),
                'service_specific': service_health
            }
            
            self.metrics['last_health_check'] = datetime.now().isoformat()
            return health_data
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            self.health_status = "unhealthy"
            return {
                'service_name': self.config.service_name,
                'service_id': self.service_id,
                'status': self.status,
                'health_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while self.status in ['running', 'starting']:
            try:
                await self.health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"⚠️ Health check loop error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    # Abstract methods that must be implemented by concrete services
    @abstractmethod
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        pass
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        pass
    
    @abstractmethod
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform service-specific health checks."""
        pass


if __name__ == "__main__":
    print("🔧 Enterprise Microservice Template")
    print("Use this template to create enterprise-grade microservices")