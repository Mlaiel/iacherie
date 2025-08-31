"""IA Influencer Agent - Base Deployment Manager
Base class for all orchestration managers

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Common orchestration functionality
- Logging and error handling
- Metrics collection base
- Health monitoring utilities
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


class BaseDeploymentManager(ABC):
    """
    Base class for all deployment managers.
    
    Provides common functionality for orchestration operations
    including logging, error handling, and metrics collection.
    """
    def __init__(self):
        """Initialize base deployment manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Manager state
        self.initialized = False
        self.start_time = datetime.now()
        self.error_count = 0
        self.warning_count = 0
        
        # Configuration
        self.config: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    async def initialize(self) -> bool:
        """
        Initialize the deployment manager.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing {self.__class__.__name__}")
            
            # Override in child classes
            initialization_result = await self._perform_initialization()
            
            if initialization_result:
                self.initialized = True
                self.logger.info(f"{self.__class__.__name__} initialized successfully")
            else:
                self.logger.error(f"Failed to initialize {self.__class__.__name__}")
            
            return initialization_result
            
        except Exception as e:
            self.logger.error(f"Initialization error in {self.__class__.__name__}: {e}")
            return False

    async def _perform_initialization(self) -> bool:
        """
        Perform manager-specific initialization.
        Override in child classes.
        
        Returns:
            True if successful, False otherwise
        """
        return True

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status information
        """
        try:
            uptime = datetime.now() - self.start_time
            
            health_info = {
                "status": "healthy" if self.initialized else "unhealthy",
                "manager": self.__class__.__name__,
                "uptime_seconds": uptime.total_seconds(),
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "last_check": datetime.now().isoformat(),
                "initialized": self.initialized
            }
            
            # Get manager-specific health info
            specific_health = await self._get_specific_health()
            health_info.update(specific_health)
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"Health check failed for {self.__class__.__name__}: {e}")
            return {
                "status": "unhealthy",
                "manager": self.__class__.__name__,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    async def _get_specific_health(self) -> Dict[str, Any]:
        """
        Get manager-specific health information.
        Override in child classes.
        
        Returns:
            Manager-specific health data
        """
        return {}

    def increment_error_count(self) -> None:
        """Increment error counter."""
        self.error_count += 1

    def increment_warning_count(self) -> None:
        """Increment warning counter."""
        self.warning_count += 1

    def log_operation(self, operation: str, success: bool, details: Optional[str] = None) -> None:
        """
        Log operation result.
        
        Args:
            operation: Operation name
            success: Whether operation was successful
            details: Optional operation details
        """
        level = logging.INFO if success else logging.ERROR
        status = "succeeded" if success else "failed"
        
        message = f"Operation '{operation}' {status}"
        if details:
            message += f": {details}"
        
        self.logger.log(level, message)
        
        if not success:
            self.increment_error_count()

    async def cleanup(self) -> bool:
        """
        Cleanup resources and connections.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            self.logger.info(f"Cleaning up {self.__class__.__name__}")
            
            # Perform manager-specific cleanup
            cleanup_result = await self._perform_cleanup()
            
            if cleanup_result:
                self.initialized = False
                self.logger.info(f"{self.__class__.__name__} cleaned up successfully")
            else:
                self.logger.error(f"Failed to cleanup {self.__class__.__name__}")
            
            return cleanup_result
            
        except Exception as e:
            self.logger.error(f"Cleanup error in {self.__class__.__name__}: {e}")
            return False

    async def _perform_cleanup(self) -> bool:
        """
        Perform manager-specific cleanup.
        Override in child classes.
        
        Returns:
            True if successful, False otherwise
        """
        return True

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if not isinstance(config, dict):
                self.logger.error("Configuration must be a dictionary")
                return False
            
            # Perform manager-specific validation
            return self._validate_specific_config(config)
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False

    def _validate_specific_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate manager-specific configuration.
        Override in child classes.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True

    async def get_status(self) -> Dict[str, Any]:
        """
        Get manager status.
        
        Returns:
            Manager status information
        """
        try:
            uptime = datetime.now() - self.start_time
            
            status = {
                "manager": self.__class__.__name__,
                "initialized": self.initialized,
                "uptime_seconds": uptime.total_seconds(),
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "last_updated": datetime.now().isoformat(),
                "config": self.config,
                "metadata": self.metadata
            }
            
            # Get manager-specific status
            specific_status = await self._get_specific_status()
            status.update(specific_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status for {self.__class__.__name__}: {e}")
            return {
                "manager": self.__class__.__name__,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }

    async def _get_specific_status(self) -> Dict[str, Any]:
        """
        Get manager-specific status information.
        Override in child classes.
        
        Returns:
            Manager-specific status data
        """
        return {}

    def set_config(self, config: Dict[str, Any]) -> bool:
        """
        Set manager configuration.
        
        Args:
            config: Configuration to set
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            if self.validate_config(config):
                self.config = config.copy()
                self.logger.info("Configuration updated successfully")
                return True
            else:
                self.logger.error("Invalid configuration provided")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set configuration: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        Get manager configuration.
        
        Returns:
            Manager configuration
        """
        return self.config.copy()

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    async def wait_for_condition(
        self,
        condition_func,
        timeout: int = 300,
        interval: int = 5,
        *args,
        **kwargs
    ) -> bool:
        """
        Wait for a condition to be met.
        
        Args:
            condition_func: Function to check condition
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds
            *args: Arguments for condition function
            **kwargs: Keyword arguments for condition function
            
        Returns:
            True if condition met, False if timeout
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                if await condition_func(*args, **kwargs):
                    return True
            except Exception as e:
                self.logger.warning(f"Condition check error: {e}")
            
            await asyncio.sleep(interval)
        
        return False

    def format_resource_name(self, base_name: str, suffix: Optional[str] = None) -> str:
        """
        Format resource name with consistent naming convention.
        
        Args:
            base_name: Base resource name
            suffix: Optional suffix
            
        Returns:
            Formatted resource name
        """
        # Normalize base name
        normalized = base_name.lower().replace("_", "-")
        
        # Add suffix if provided
        if suffix:
            normalized = f"{normalized}-{suffix.lower()}"
        
        # Ensure valid Kubernetes name
        normalized = normalized[:63]  # Max length for Kubernetes names
        normalized = normalized.strip("-")
        
        return normalized

    def parse_resource_requirements(self, requirements: Dict[str, str]) -> Dict[str, str]:
        """
        Parse and validate resource requirements.
        
        Args:
            requirements: Resource requirements dict
            
        Returns:
            Validated resource requirements
        """
        validated = {}
        
        for resource, value in requirements.items():
            if resource in ["cpu", "memory"]:
                validated[resource] = value
            else:
                self.logger.warning(f"Unknown resource type: {resource}")
        
        return validated

    def generate_labels(self, base_labels: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Generate standard labels for resources.
        
        Args:
            base_labels: Base labels to include
            
        Returns:
            Generated labels
        """
        labels = {
            "app.kubernetes.io/name": "ia-influencer-agent",
            "app.kubernetes.io/managed-by": self.__class__.__name__.lower(),
            "app.kubernetes.io/version": "2.0.0",
            "app.kubernetes.io/component": "platform"
        }
        
        if base_labels:
            labels.update(base_labels)
        
        return labels

    def generate_annotations(self, base_annotations: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Generate standard annotations for resources.
        
        Args:
            base_annotations: Base annotations to include
            
        Returns:
            Generated annotations
        """
        annotations = {
            "deployment.kubernetes.io/revision": "1",
            "meta.helm.sh/release-name": "ia-influencer-agent",
            "meta.helm.sh/release-namespace": "default"
        }
        
        if base_annotations:
            annotations.update(base_annotations)
        
        return annotations
