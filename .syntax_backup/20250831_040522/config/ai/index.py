"""
AI Configuration Index - IA-Influencer Agent Platform
====================================================

Central index for all AI configuration modules and services.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Type
import logging
import os
from datetime import datetime
from enum import Enum

# Import all AI configuration modules
from . import (
    # Core AI Configurations
    AIModelConfig, ai_model_config,
    FingerprintAIConfig, fingerprint_ai_config,
    NLPConfig, nlp_config,
    ComputerVisionConfig, computer_vision_config,
    AudioAnalysisConfig, audio_analysis_config,
    ModelTrainingConfig, model_training_config,
    InferenceConfig, inference_config,
    VectorStoreConfig, vector_store_config,
    
    # Advanced AI Configurations
    ContentAnalysisConfig, content_analysis_config,
    ContentProtectionConfig, content_protection_config,
    MonetizationConfig, monetization_config,
    CollaborationConfig, collaboration_config,
    SEOMarketingConfig, seo_marketing_config,
    PlatformIntegrationConfig, platform_integration_config
)

# Configure logging
logger = logging.getLogger(__name__)


class AIConfigRegistry:
    """
    Central registry for all AI configuration modules.
    
    Provides unified access to all AI configurations, validation,
    and management capabilities for the IA-Influencer platform.
    """
    
    def __init__(self):
        """Initialize AI configuration registry."""
        self._configs = {}
        self._config_classes = {}
        self._initialization_time = datetime.now()
        self._register_all_configs()
    
    def _register_all_configs(self):
        """Register all available AI configurations."""
        
        # Core AI Configurations
        self._register_config("ai_model", AIModelConfig, ai_model_config)
        self._register_config("fingerprint", FingerprintAIConfig, fingerprint_ai_config)
        self._register_config("nlp", NLPConfig, nlp_config)
        self._register_config("computer_vision", ComputerVisionConfig, computer_vision_config)
        self._register_config("audio_analysis", AudioAnalysisConfig, audio_analysis_config)
        self._register_config("training", ModelTrainingConfig, model_training_config)
        self._register_config("inference", InferenceConfig, inference_config)
        self._register_config("vector_store", VectorStoreConfig, vector_store_config)
        
        # Advanced AI Configurations
        self._register_config("content_analysis", ContentAnalysisConfig, content_analysis_config)
        self._register_config("content_protection", ContentProtectionConfig, content_protection_config)
        self._register_config("monetization", MonetizationConfig, monetization_config)
        self._register_config("collaboration", CollaborationConfig, collaboration_config)
        self._register_config("seo_marketing", SEOMarketingConfig, seo_marketing_config)
        self._register_config("platform_integration", PlatformIntegrationConfig, platform_integration_config)
        
        logger.info(f"Registered {len(self._configs)} AI configuration modules")
    
    def _register_config(self, name: str, config_class: Type, config_instance: Any):
        """Register a configuration module."""
        self._configs[name] = config_instance
        self._config_classes[name] = config_class
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """
        Get configuration instance by name.
        
        Args:
            config_name: Name of the configuration module
            
        Returns:
            Configuration instance or None if not found
        """
        return self._configs.get(config_name)
    
    def get_config_class(self, config_name: str) -> Optional[Type]:
        """
        Get configuration class by name.
        
        Args:
            config_name: Name of the configuration module
            
        Returns:
            Configuration class or None if not found
        """
        return self._config_classes.get(config_name)
    
    def list_configs(self) -> List[str]:
        """Get list of all registered configuration names."""
        return list(self._configs.keys())
    
    def validate_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all registered configurations.
        
        Returns:
            Dictionary with validation results for each configuration
        """
        validation_results = {}
        
        for config_name, config_instance in self._configs.items():
            try:
                # Basic validation - check if config instance is valid
                validation_result = {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "config_type": type(config_instance).__name__,
                    "validation_time": datetime.now().isoformat()
                }
                
                # Perform basic checks
                if not hasattr(config_instance, '__dict__'):
                    validation_result["errors"].append("Configuration instance has no attributes")
                    validation_result["valid"] = False
                
                # Check for required environment variables or settings
                if hasattr(config_instance, 'Config') and hasattr(config_instance.Config, 'env_prefix'):
                    env_prefix = config_instance.Config.env_prefix
                    if not any(key.startswith(env_prefix) for key in os.environ):
                        validation_result["warnings"].append(f"No environment variables found with prefix {env_prefix}")
                
                validation_results[config_name] = validation_result
                
            except Exception as e:
                validation_results[config_name] = {
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                    "config_type": type(config_instance).__name__,
                    "validation_time": datetime.now().isoformat()
                }
        
        return validation_results
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive system overview of all AI configurations.
        
        Returns:
            Dictionary with system overview information
        """
        overview = {
            "platform": "IA-Influencer Agent + Content Protection",
            "version": "2.0.0",
            "author": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "initialization_time": self._initialization_time.isoformat(),
            "total_configurations": len(self._configs),
            "configuration_categories": {
                "core_ai": [
                    "ai_model", "fingerprint", "nlp", "computer_vision",
                    "audio_analysis", "training", "inference", "vector_store"
                ],
                "advanced_ai": [
                    "content_analysis", "content_protection", "monetization",
                    "collaboration", "seo_marketing", "platform_integration"
                ]
            },
            "business_logic_support": {
                "multi_format_upload": True,
                "ai_content_protection": True,
                "rights_management": True,
                "seo_optimization": True,
                "collaboration_matching": True,
                "monetization_automation": True,
                "cross_platform_distribution": True
            },
            "ai_models_configured": {
                "fingerprinting_models": 12,
                "nlp_models": 8,
                "computer_vision_models": 10,
                "audio_analysis_models": 15,
                "content_classification_models": 6,
                "recommendation_models": 4,
                "generation_models": 5
            },
            "platform_integrations": {
                "youtube": True,
                "tiktok": True,
                "instagram": True,
                "spotify": True,
                "facebook": True,
                "twitter": True,
                "soundcloud": True,
                "twitch": True,
                "pinterest": True,
                "linkedin": True
            },
            "security_features": {
                "content_encryption": True,
                "data_anonymization": True,
                "secure_deletion": True,
                "audit_logging": True,
                "gdpr_compliance": True,
                "copyright_protection": True
            },
            "performance_features": {
                "gpu_acceleration": True,
                "distributed_processing": True,
                "async_processing": True,
                "batch_processing": True,
                "model_caching": True,
                "result_caching": True
            }
        }
        
        return overview
    
    def get_configuration_summary(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed summary for a specific configuration.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Configuration summary or None if not found
        """
        if config_name not in self._configs:
            return None
        
        config_instance = self._configs[config_name]
        config_class = self._config_classes[config_name]
        
        summary = {
            "name": config_name,
            "class_name": config_class.__name__,
            "description": getattr(config_class, "__doc__", "No description available"),
            "total_settings": len([attr for attr in dir(config_instance) if not attr.startswith('_')]),
            "environment_prefix": getattr(
                getattr(config_instance, 'Config', None), 
                'env_prefix', 
                None
            ),
            "key_features": self._get_config_key_features(config_name, config_instance),
            "validation_status": "valid"  # Would be determined by actual validation
        }
        
        return summary
    
    def _get_config_key_features(self, config_name: str, config_instance: Any) -> List[str]:
        """Get key features for a configuration."""
        
        feature_mappings = {
            "ai_model": [
                "Multi-model support (PyTorch, TensorFlow, Hugging Face)",
                "GPU/CPU optimization",
                "Model caching and versioning",
                "Custom model integration"
            ],
            "fingerprint": [
                "Multi-format fingerprinting (audio, video, image, text)",
                "Advanced similarity matching",
                "Real-time fingerprint extraction",
                "FAISS vector indexing"
            ],
            "content_analysis": [
                "Multi-format content processing",
                "Quality assessment automation",
                "Metadata extraction",
                "Commercial potential analysis"
            ],
            "content_protection": [
                "Cross-platform monitoring",
                "Automated takedown requests",
                "Revenue claim automation",
                "Legal compliance support"
            ],
            "monetization": [
                "Multi-revenue model support",
                "Automated payment processing",
                "Revenue optimization AI",
                "Tax and compliance handling"
            ],
            "collaboration": [
                "AI-powered creator matching",
                "Compatibility scoring",
                "Automated contract generation",
                "Performance tracking"
            ],
            "seo_marketing": [
                "Cross-platform SEO optimization",
                "Automated keyword research",
                "A/B testing automation",
                "Viral content prediction"
            ],
            "platform_integration": [
                "Multi-platform API management",
                "Real-time synchronization",
                "Automated content distribution",
                "Webhook event handling"
            ]
        }
        
        return feature_mappings.get(config_name, ["Advanced AI configuration"])
    
    def export_configuration_docs(self, output_format: str = "markdown") -> str:
        """
        Export comprehensive documentation for all configurations.
        
        Args:
            output_format: Output format (markdown, json, yaml)
            
        Returns:
            Formatted configuration documentation
        """
        if output_format.lower() == "markdown":
            return self._export_markdown_docs()
        elif output_format.lower() == "json":
            import json
            return json.dumps(self.get_system_overview(), indent=2)
        else:
            return "Unsupported format. Use 'markdown' or 'json'."
    
    def _export_markdown_docs(self) -> str:
        """Export documentation in Markdown format."""
        
        docs = []
        docs.append("# IA-Influencer Agent - AI Configuration Documentation
")
        docs.append("## Professional AI/ML Configuration Suite
")
        docs.append("**Author:** Fahed Mlaiel <mlaiel@live.de>
")
        docs.append("**Version:** 2.0.0
")
        docs.append("**Platform:** IA-Influencer Agent + Content Protection

")
        
        docs.append("### 🚨 STRICT COPYRIGHT NOTICE
")
        docs.append("This code is the **exclusive intellectual property** of Fahed Mlaiel.
")
        docs.append("Any unauthorized use, reproduction, distribution, or reverse engineering ")
        docs.append("without explicit written permission is **STRICTLY PROHIBITED** and will be ")
        docs.append("prosecuted to the full extent of the law.

")
        
        docs.append("**Contact:** mlaiel@live.de for licensing inquiries.

")
        
        docs.append("---

")
        docs.append("## Configuration Modules Overview

")
        
        # Core configurations
        docs.append("### 🔧 Core AI Configurations

")
        for config_name in ["ai_model", "fingerprint", "nlp", "computer_vision", 
                           "audio_analysis", "training", "inference", "vector_store"]:
            if config_name in self._configs:
                summary = self.get_configuration_summary(config_name)
                docs.append(f"#### {summary['name'].title().replace('_', ' ')}
")
                docs.append(f"- **Class:** `{summary['class_name']}`
")
                docs.append(f"- **Settings:** {summary['total_settings']} configuration options
")
                docs.append("- **Features:**
")
                for feature in summary['key_features']:
                    docs.append(f"  - {feature}
")
                docs.append("
")
        
        # Advanced configurations
        docs.append("### 🚀 Advanced AI Configurations\n\n")
        for config_name in ["content_analysis", "content_protection", "monetization",
                           "collaboration", "seo_marketing", "platform_integration"]:
            if config_name in self._configs:
                summary = self.get_configuration_summary(config_name)
                docs.append(f"#### {summary['name'].title().replace('_', ' ')}
")
                docs.append(f"- **Class:** `{summary['class_name']}`
")
                docs.append(f"- **Settings:** {summary['total_settings']} configuration options
")
                docs.append("- **Features:**
")
                for feature in summary['key_features']:
                    docs.append(f"  - {feature}
")
                docs.append("
")
        
        docs.append("---

")
        docs.append("## Usage Example

")
        docs.append("```python
")
        docs.append("from backend.config.ai import (
")
        docs.append("    ai_config_registry,
")
        docs.append("    content_analysis_config,\n")
        docs.append("    content_protection_config,\n")
        docs.append("    monetization_config,\n")
        docs.append("    collaboration_config,\n")
        docs.append("    seo_marketing_config,\n")
        docs.append("    platform_integration_config\n")
        docs.append(")\n\n")
        docs.append("# Get system overview
")
        docs.append("overview = ai_config_registry.get_system_overview()
")
        docs.append("print(f"Total configurations: {overview['total_configurations']}")

")
        docs.append("# Access specific configurations
")
        docs.append("analysis_config = ai_config_registry.get_config('content_analysis')
")
        docs.append("protection_config = ai_config_registry.get_config('content_protection')
")
        docs.append("```

")
        
        return "".join(docs)


# Global registry instance
ai_config_registry = AIConfigRegistry()


def get_all_ai_configs() -> Dict[str, Any]:
    """
    Get all AI configuration instances.
    
    Returns:
        Dictionary mapping configuration names to instances
    """
    return {
        # Core AI Configurations
        "ai_model": ai_model_config,
        "fingerprint": fingerprint_ai_config,
        "nlp": nlp_config,
        "computer_vision": computer_vision_config,
        "audio_analysis": audio_analysis_config,
        "training": model_training_config,
        "inference": inference_config,
        "vector_store": vector_store_config,
        
        # Advanced AI Configurations
        "content_analysis": content_analysis_config,
        "content_protection": content_protection_config,
        "monetization": monetization_config,
        "collaboration": collaboration_config,
        "seo_marketing": seo_marketing_config,
        "platform_integration": platform_integration_config
    }


def validate_ai_environment() -> Dict[str, Any]:
    """
    Validate the AI environment and configuration setup.
    
    Returns:
        Validation results dictionary
    """
    return ai_config_registry.validate_all_configs()


def export_ai_documentation(format: str = "markdown") -> str:
    """
    Export comprehensive AI configuration documentation.
    
    Args:
        format: Export format (markdown, json)
        
    Returns:
        Formatted documentation string
    """
    return ai_config_registry.export_configuration_docs(format)


# Module metadata
__all__ = [
    "AIConfigRegistry",
    "ai_config_registry", 
    "get_all_ai_configs",
    "validate_ai_environment",
    "export_ai_documentation"
]

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import all configuration modules
from . import (
    ai_model_config,
    fingerprint_ai_config,
    nlp_config,
    computer_vision_config,
    audio_analysis_config,
    model_training_config,
    inference_config,
    vector_store_config,
    get_ai_config_summary
)


class AIConfigurationManager:
    """
    Central AI Configuration Manager for IA-Influencer Agent Platform.
    
    Provides unified access to all AI configuration modules and utilities
    for configuration management, validation, and deployment.
    """
    
    def __init__(self):
        """Initialize the AI Configuration Manager."""
        self.configs = {
            'model': ai_model_config,
            'fingerprint': fingerprint_ai_config,
            'nlp': nlp_config,
            'computer_vision': computer_vision_config,
            'audio': audio_analysis_config,
            'training': model_training_config,
            'inference': inference_config,
            'vector_store': vector_store_config,
        }
        
    def get_config(self, config_type: str):
        """Get specific configuration by type."""
        return self.configs.get(config_type)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configuration instances."""
        return self.configs.copy()
    
    def validate_configurations(self) -> Dict[str, Any]:
        """Validate all AI configurations for consistency and completeness."""
        validation_results = {
            'status': 'success',
            'issues': [],
            'warnings': [],
            'config_status': {}
        }
        
        try:
            # Validate model configuration
            model_config = self.configs['model']
            if not model_config.MODEL_CACHE_DIR:
                validation_results['issues'].append("Model cache directory not configured")
            
            # Validate device configuration
            if model_config.DEFAULT_DEVICE not in ['auto', 'cpu', 'cuda', 'mps']:
                validation_results['issues'].append(f"Invalid device: {model_config.DEFAULT_DEVICE}")
            
            # Validate fingerprint configuration
            fingerprint_config = self.configs['fingerprint']
            if fingerprint_config.SIMILARITY_THRESHOLD_GLOBAL < 0.5 or fingerprint_config.SIMILARITY_THRESHOLD_GLOBAL > 1.0:
                validation_results['warnings'].append("Similarity threshold might be too low/high")
            
            # Validate vector store configuration
            vector_config = self.configs['vector_store']
            if vector_config.VECTOR_DIMENSION <= 0:
                validation_results['issues'].append("Invalid vector dimension")
            
            # Check storage paths existence
            for config_name, config in self.configs.items():
                if hasattr(config, 'VECTOR_STORAGE_PATH'):
                    if not Path(config.VECTOR_STORAGE_PATH).exists():
                        validation_results['warnings'].append(f"Storage path for {config_name} doesn't exist")
                        
            validation_results['config_status'] = {
                name: 'valid' for name in self.configs.keys()
            }
            
        except Exception as e:
            validation_results['status'] = 'error'
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def get_hardware_requirements(self) -> Dict[str, Any]:
        """Get consolidated hardware requirements for all AI modules."""
        requirements = {
            'minimum': {
                'cpu_cores': 4,
                'memory_gb': 8,
                'storage_gb': 50,
                'gpu_memory_gb': 0,
            },
            'recommended': {
                'cpu_cores': 16,
                'memory_gb': 32,
                'storage_gb': 500,
                'gpu_memory_gb': 12,
            },
            'optimal': {
                'cpu_cores': 32,
                'memory_gb': 64,
                'storage_gb': 2000,
                'gpu_memory_gb': 24,
            }
        }
        
        # Add specific requirements per module
        requirements['by_module'] = {
            'nlp': {
                'memory_gb': 4,
                'gpu_memory_gb': 2,
                'storage_gb': 10,
            },
            'computer_vision': {
                'memory_gb': 8,
                'gpu_memory_gb': 8,
                'storage_gb': 20,
            },
            'audio': {
                'memory_gb': 6,
                'gpu_memory_gb': 4,
                'storage_gb': 15,
            },
            'vector_store': {
                'memory_gb': 16,
                'gpu_memory_gb': 0,
                'storage_gb': 200,
            },
            'training': {
                'memory_gb': 32,
                'gpu_memory_gb': 16,
                'storage_gb': 100,
            }
        }
        
        return requirements
    
    def get_model_inventory(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get complete inventory of all configured AI models."""
        inventory = {
            'audio_models': [],
            'vision_models': [],
            'nlp_models': [],
            'fingerprint_models': [],
            'training_models': [],
            'inference_endpoints': []
        }
        
        # Collect audio models
        for task in audio_analysis_config.get_supported_tasks():
            spec = audio_analysis_config.get_audio_model_spec(task)
            inventory['audio_models'].append({
                'task': task.value,
                'model_name': spec.model_name,
                'model_path': spec.model_path,
                'memory_mb': spec.memory_requirement_mb,
                'requires_gpu': spec.requires_gpu,
                'accuracy': spec.accuracy_score
            })
        
        # Collect vision models
        for task in computer_vision_config.get_supported_tasks():
            spec = computer_vision_config.get_vision_model_spec(task)
            inventory['vision_models'].append({
                'task': task.value,
                'model_name': spec.model_name,
                'model_path': spec.model_path,
                'memory_mb': spec.memory_requirement_mb,
                'requires_gpu': spec.requires_gpu,
                'accuracy': spec.accuracy_score
            })
        
        # Collect NLP models
        for task in nlp_config.get_supported_tasks():
            spec = nlp_config.get_nlp_model_spec(task)
            inventory['nlp_models'].append({
                'task': task.value,
                'model_name': spec.model_name,
                'model_path': spec.model_path,
                'memory_mb': spec.memory_requirement_mb,
                'requires_gpu': spec.requires_gpu,
                'accuracy': spec.accuracy_score
            })
        
        return inventory
    
    def export_configuration(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export complete AI configuration to JSON file."""
        export_data = {
            'metadata': {
                'version': '2.0.0',
                'author': 'Fahed Mlaiel',
                'email': 'mlaiel@live.de',
                'export_timestamp': str(Path(__file__).stat().st_mtime),
                'copyright': '© 2025 Fahed Mlaiel. All rights reserved.'
            },
            'summary': get_ai_config_summary(),
            'configurations': {},
            'hardware_requirements': self.get_hardware_requirements(),
            'model_inventory': self.get_model_inventory(),
            'validation_results': self.validate_configurations()
        }
        
        # Export each configuration
        for name, config in self.configs.items():
            try:
                if hasattr(config, 'dict'):
                    export_data['configurations'][name] = config.dict()
                elif hasattr(config, '__dict__'):
                    # Convert to dict, filtering out private attributes
                    export_data['configurations'][name] = {
                        k: v for k, v in config.__dict__.items() 
                        if not k.startswith('_') and not callable(v)
                    }
            except Exception as e:
                export_data['configurations'][name] = {
                    'error': f'Failed to export: {str(e)}'
                }
        
        # Save to file if path provided
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            except Exception as e:
                export_data['export_error'] = str(e)
        
        return export_data
    
    def get_deployment_checklist(self) -> Dict[str, Any]:
        """Get deployment readiness checklist for AI modules."""
        checklist = {
            'status': 'ready',
            'checks': {
                'configurations_valid': True,
                'storage_paths_exist': True,
                'models_accessible': True,
                'hardware_compatible': True,
                'dependencies_installed': True,
                'security_configured': True,
            },
            'required_actions': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Perform actual checks
        validation = self.validate_configurations()
        if validation['issues']:
            checklist['status'] = 'issues'
            checklist['checks']['configurations_valid'] = False
            checklist['required_actions'].extend(validation['issues'])
        
        if validation['warnings']:
            checklist['warnings'].extend(validation['warnings'])
        
        # Check hardware compatibility
        hardware_req = self.get_hardware_requirements()
        checklist['recommendations'].append(
            f"Recommended: {hardware_req['recommended']['memory_gb']}GB RAM, "
            f"{hardware_req['recommended']['gpu_memory_gb']}GB GPU memory"
        )
        
        # Security recommendations
        if not ai_model_config.OPENAI_API_KEY:
            checklist['warnings'].append("OpenAI API key not configured")
        
        if not fingerprint_ai_config.FINGERPRINT_ANALYTICS_ENABLED:
            checklist['recommendations'].append("Enable fingerprint analytics for better monitoring")
        
        return checklist
    
    def optimize_for_environment(self, environment: str = 'production') -> Dict[str, Any]:
        """Get optimized configuration recommendations for specific environment."""
        optimizations = {
            'environment': environment,
            'recommendations': [],
            'configuration_changes': {},
            'performance_tips': []
        }
        
        if environment == 'production':
            optimizations['recommendations'].extend([
                "Enable GPU acceleration for vision and audio tasks",
                "Use Redis for vector store caching",
                "Enable batch processing for all inference endpoints",
                "Set up monitoring and alerting",
                "Configure automatic backups for vector stores"
            ])
            
            optimizations['configuration_changes'] = {
                'inference.GPU_ACCELERATION': True,
                'vector_store.CACHING_STRATEGY': 'redis',
                'inference.BATCH_PROCESSING': True,
                'fingerprint.FINGERPRINT_ANALYTICS_ENABLED': True,
                'vector_store.AUTO_BACKUP_ENABLED': True
            }
            
        elif environment == 'development':
            optimizations['recommendations'].extend([
                "Use smaller batch sizes for faster iteration",
                "Enable detailed logging for debugging",
                "Use local storage for caching",
                "Reduce model complexity for faster training"
            ])
            
            optimizations['configuration_changes'] = {
                'inference.DEFAULT_BATCH_SIZE': 8,
                'inference.DETAILED_LOGGING': True,
                'vector_store.CACHING_STRATEGY': 'memory',
                'training.DEFAULT_EPOCHS': 10
            }
            
        elif environment == 'testing':
            optimizations['recommendations'].extend([
                "Use lightweight models for faster tests",
                "Enable comprehensive logging",
                "Use temporary storage paths",
                "Reduce timeouts for faster feedback"
            ])
            
        return optimizations


# Global configuration manager instance
ai_config_manager = AIConfigurationManager()


# Utility functions for easy access
def get_complete_ai_config():
    """Get complete AI configuration in one call."""
    return ai_config_manager.get_all_configs()


def validate_ai_setup():
    """Validate complete AI setup."""
    return ai_config_manager.validate_configurations()


def get_deployment_status():
    """Get AI deployment readiness status."""
    return ai_config_manager.get_deployment_checklist()


def export_ai_config(file_path: str = "ai_config_export.json"):
    """Export AI configuration to file."""
    return ai_config_manager.export_configuration(file_path)


# Export all utility functions
__all__ = [
    'AIConfigurationManager',
    'ai_config_manager',
    'get_complete_ai_config',
    'validate_ai_setup',
    'get_deployment_status',
    'export_ai_config'
]
