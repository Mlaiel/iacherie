"""Ainflue AI System Configuration
================================

AI and Machine Learning configurations for model deployment,
processing pipelines, neural networks, and intelligent analysis.

Enterprise-grade AI configuration management for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# AI system imports
from .ai_model_config import AIModelConfiguration
from .ia_processing_config import IAProcessingConfiguration
from .ml_pipeline_config import MLPipelineConfiguration
from .intelligent_analysis_config import IntelligentAnalysisConfiguration

logger = logging.getLogger(__name__)

class AIConfigurationLevel(str, Enum):
    """AI configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class AISystemConfigurationManager:
    """AI system configuration manager"""
    
    def __init__(self, level: AIConfigurationLevel = AIConfigurationLevel.ENTERPRISE):
        self.level = level
        self.configurations = {}
        self._initialize_ai_configs()
    
    def _initialize_ai_configs(self):
        """Initialize all AI configurations"""
        self.configurations = {
            "ai_models": AIModelConfiguration(level=self.level),
            "ia_processing": IAProcessingConfiguration(level=self.level),
            "ml_pipeline": MLPipelineConfiguration(level=self.level),
            "intelligent_analysis": IntelligentAnalysisConfiguration(level=self.level)
        }
        
        logger.info(f"🤖 AI configurations initialized - Level: {self.level.value}")
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """Get specific AI configuration"""
        return self.configurations.get(config_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all AI configurations"""
        return self.configurations.copy()
    
    def get_model_config(self) -> Optional[Any]:
        """Get AI model configuration"""
        return self.get_config("ai_models")
    
    def get_processing_config(self) -> Optional[Any]:
        """Get IA processing configuration"""
        return self.get_config("ia_processing")
    
    def get_pipeline_config(self) -> Optional[Any]:
        """Get ML pipeline configuration"""
        return self.get_config("ml_pipeline")
    
    def get_analysis_config(self) -> Optional[Any]:
        """Get intelligent analysis configuration"""
        return self.get_config("intelligent_analysis")

# Global AI configuration manager
ai_config_manager = AISystemConfigurationManager()

# Module exports
__all__ = [
    "AIModelConfiguration",
    "IAProcessingConfiguration",
    "MLPipelineConfiguration", 
    "IntelligentAnalysisConfiguration",
    "AISystemConfigurationManager",
    "AIConfigurationLevel",
    "ai_config_manager"
]

logger.info("🤖 Ainflue AI System Configuration Module loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
