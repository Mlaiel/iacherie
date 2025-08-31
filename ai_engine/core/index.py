"""AI Core Module Index

Quick access to all AI core components and utilities.
This module provides a centralized entry point for the AI core functionality.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""# Import all core components
from . import (
    exceptions,
    metrics,
    performance,
    validation,
    ai_engine,
    content_processor,
    config,
    setup,
    tests
)

# Core instances for easy access
from .exceptions import BaseAIException, EXCEPTION_REGISTRY
from .metrics import metrics_collector
from .performance import performance_monitor
from .validation import content_validator
from .ai_engine import ai_engine
from .content_processor import content_pipeline
from .config import config_manager
from .setup import setup_ai_core
from .tests import run_all_tests

# Version and metadata
from . import __version__, __author__, __email__, get_module_info, get_health_status

# Convenient aliases for easy access
validator = content_validator
metrics = metrics_collector
monitor = performance_monitor
engine = ai_engine
pipeline = content_pipeline
config = config_manager
setup = setup_ai_core
test = run_all_tests

# Core exception types
AIError = BaseAIException
ValidationError = exceptions.ContentValidationError
ModelError = exceptions.ModelConnectionError
ConfigError = exceptions.ConfigurationError

# Core enums and types
ContentType = validation.ContentType
ProcessingStage = content_processor.ProcessingStage
ModelType = ai_engine.AIModelType
DeviceType = ai_engine.DeviceType

__all__ = [
    # Modules
    "exceptions",
    "metrics", 
    "performance",
    "validation",
    "ai_engine",
    "content_processor",
    
    # Core instances
    "metrics_collector",
    "performance_monitor", 
    "content_validator",
    "ai_engine",
    "content_pipeline",
    
    # Aliases
    "validator",
    "metrics",
    "monitor", 
    "engine",
    "pipeline",
    
    # Exception types
    "AIError",
    "ValidationError",
    "ModelError", 
    "ConfigError",
    
    # Enums and types
    "ContentType",
    "ProcessingStage",
    "ModelType",
    "DeviceType",
    
    # Utilities
    "get_module_info",
    "get_health_status"
]
