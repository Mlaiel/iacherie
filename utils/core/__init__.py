"""
Core Utilities Module - Enterprise Architecture Level 1
======================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic utilities for the IA Chérie platform.
This module provides fundamental data processing, file management, 
text processing, media handling, and workflow orchestration.

Enterprise Standards:
- Async/await throughout
- Type hints 100%
- Performance < 10ms per operation
- Clean architecture patterns
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_processor import DataProcessor
    from .file_manager import FileManager
    from .datetime_handler import DateTimeHandler
    from .text_processor import TextProcessor
    from .media_handler import MediaHandler
    from .workflow_engine import WorkflowEngine
    from .cache_manager import CacheManager
    from .security_manager import SecurityManager
    from .performance_monitor import PerformanceMonitor
    from .api_client import APIClient
    from .validator import Validator
    from .event_manager import EventManager
    from .config_manager import ConfigManager

__all__ = [
    "DataProcessor",
    "FileManager", 
    "DateTimeHandler",
    "TextProcessor",
    "MediaHandler",
    "WorkflowEngine",
    "CacheManager",
    "SecurityManager", 
    "PerformanceMonitor",
    "APIClient",
    "Validator",
    "EventManager",
    "ConfigManager",
    "DataProcessorFactory",
    "FileManagerFactory",
    "DateTimeHandlerFactory", 
    "TextProcessorFactory",
    "MediaHandlerFactory",
    "WorkflowEngineFactory",
    "CacheManagerFactory",
    "SecurityManagerFactory",
    "PerformanceMonitorFactory",
    "APIClientFactory",
    "ValidatorFactory",
    "EventManagerFactory",
    "ConfigManagerFactory"
]

# Lazy loading for enterprise performance
def __getattr__(name: str):
    if name == "DataProcessor":
        from .data_processor import DataProcessor
        return DataProcessor
    elif name == "FileManager":
        from .file_manager import FileManager
        return FileManager
    elif name == "DateTimeHandler":
        from .datetime_handler import DateTimeHandler
        return DateTimeHandler
    elif name == "TextProcessor":
        from .text_processor import TextProcessor
        return TextProcessor
    elif name == "MediaHandler":
        from .media_handler import MediaHandler
        return MediaHandler
    elif name == "WorkflowEngine":
        from .workflow_engine import WorkflowEngine
        return WorkflowEngine
    elif name == "CacheManager":
        from .cache_manager import CacheManager
        return CacheManager
    elif name == "SecurityManager":
        from .security_manager import SecurityManager
        return SecurityManager
    elif name == "PerformanceMonitor":
        from .performance_monitor import PerformanceMonitor
        return PerformanceMonitor
    elif name == "APIClient":
        from .api_client import APIClient
        return APIClient
    elif name == "Validator":
        from .validator import Validator
        return Validator
    elif name == "EventManager":
        from .event_manager import EventManager
        return EventManager
    elif name == "ConfigManager":
        from .config_manager import ConfigManager
        return ConfigManager
    elif name == "DataProcessorFactory":
        from .data_processor import DataProcessorFactory
        return DataProcessorFactory
    elif name == "FileManagerFactory":
        from .file_manager import FileManagerFactory
        return FileManagerFactory
    elif name == "DateTimeHandlerFactory":
        from .datetime_handler import DateTimeHandlerFactory
        return DateTimeHandlerFactory
    elif name == "TextProcessorFactory":
        from .text_processor import TextProcessorFactory
        return TextProcessorFactory
    elif name == "MediaHandlerFactory":
        from .media_handler import MediaHandlerFactory
        return MediaHandlerFactory
    elif name == "WorkflowEngineFactory":
        from .workflow_engine import WorkflowEngineFactory
        return WorkflowEngineFactory
    elif name == "CacheManagerFactory":
        from .cache_manager import CacheManagerFactory
        return CacheManagerFactory
    elif name == "SecurityManagerFactory":
        from .security_manager import SecurityManagerFactory
        return SecurityManagerFactory
    elif name == "PerformanceMonitorFactory":
        from .performance_monitor import PerformanceMonitorFactory
        return PerformanceMonitorFactory
    elif name == "APIClientFactory":
        from .api_client import APIClientFactory
        return APIClientFactory
    elif name == "ValidatorFactory":
        from .validator import ValidatorFactory
        return ValidatorFactory
    elif name == "EventManagerFactory":
        from .event_manager import EventManagerFactory
        return EventManagerFactory
    elif name == "ConfigManagerFactory":
        from .config_manager import ConfigManagerFactory
        return ConfigManagerFactory
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")