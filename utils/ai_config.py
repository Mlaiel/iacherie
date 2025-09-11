"""
AI Config - IA Prompt Engineer Expert Implementation
==================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise AI configuration management for multi-provider setups.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    GOOGLE = "google"
    AZURE = "azure"


@dataclass
class ModelConfig:
    """AI model configuration"""
    name: str
    provider: AIProvider
    max_tokens: int
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    timeout: int
    retry_attempts: int
    cost_per_1k_tokens: float


@dataclass
class ProviderConfig:
    """AI provider configuration"""
    provider: AIProvider
    api_key: str
    base_url: str
    rate_limit_rpm: int
    rate_limit_tpm: int
    enabled: bool
    priority: int


class AIConfig:
    """
    Enterprise AI configuration management system for:
    - Multi-provider configuration
    - Model parameter optimization
    - Cost management
    - Performance tuning
    - Fallback strategies
    """
    
    def __init__(self):
        """Initialize AI configuration manager"""
        self.providers: Dict[AIProvider, ProviderConfig] = {}
        self.models: Dict[str, ModelConfig] = {}
        self.default_configs = self._load_default_configs()
        
        # Configuration profiles
        self.profiles = {
            'development': {
                'temperature': 0.7,
                'max_tokens': 1000,
                'timeout': 30
            },
            'production': {
                'temperature': 0.3,
                'max_tokens': 2000,
                'timeout': 60
            },
            'creative': {
                'temperature': 0.9,
                'max_tokens': 1500,
                'timeout': 45
            }
        }
        
        # Current active profile
        self.active_profile = 'production'
        
        logger.info("AIConfig initialized with enterprise management")
    
    def _load_default_configs(self) -> Dict[str, Any]:
        """Load default configurations for AI providers"""
        return {
            'openai': {
                'models': {
                    'gpt-4': {
                        'max_tokens': 8192,
                        'temperature': 0.7,
                        'cost_per_1k_tokens': 0.03
                    },
                    'gpt-3.5-turbo': {
                        'max_tokens': 4096,
                        'temperature': 0.7,
                        'cost_per_1k_tokens': 0.002
                    }
                },
                'base_url': 'https://api.openai.com/v1',
                'rate_limit_rpm': 3500,
                'rate_limit_tpm': 90000
            },
            'anthropic': {
                'models': {
                    'claude-3-opus': {
                        'max_tokens': 4096,
                        'temperature': 0.7,
                        'cost_per_1k_tokens': 0.015
                    },
                    'claude-3-sonnet': {
                        'max_tokens': 4096,
                        'temperature': 0.7,
                        'cost_per_1k_tokens': 0.003
                    }
                },
                'base_url': 'https://api.anthropic.com/v1',
                'rate_limit_rpm': 1000,
                'rate_limit_tpm': 40000
            }
        }
    
    def configure_provider(self, provider: AIProvider, api_key: str,
                          custom_config: Dict[str, Any] = None) -> ProviderConfig:
        """Configure AI provider"""
        try:
            default_config = self.default_configs.get(provider.value, {})
            
            provider_config = ProviderConfig(
                provider=provider,
                api_key=api_key,
                base_url=custom_config.get('base_url', default_config.get('base_url', '')),
                rate_limit_rpm=custom_config.get('rate_limit_rpm', default_config.get('rate_limit_rpm', 1000)),
                rate_limit_tpm=custom_config.get('rate_limit_tpm', default_config.get('rate_limit_tpm', 10000)),
                enabled=custom_config.get('enabled', True),
                priority=custom_config.get('priority', 1)
            )
            
            self.providers[provider] = provider_config
            
            # Auto-configure models for this provider
            self._auto_configure_models(provider)
            
            logger.info(f"Provider configured: {provider.value}")
            return provider_config
            
        except Exception as e:
            logger.error(f"Provider configuration failed: {e}")
            raise
    
    def _auto_configure_models(self, provider: AIProvider):
        """Automatically configure models for provider"""
        default_config = self.default_configs.get(provider.value, {})
        models_config = default_config.get('models', {})
        
        for model_name, model_params in models_config.items():
            model_config = ModelConfig(
                name=model_name,
                provider=provider,
                max_tokens=model_params.get('max_tokens', 2048),
                temperature=model_params.get('temperature', 0.7),
                top_p=model_params.get('top_p', 1.0),
                frequency_penalty=model_params.get('frequency_penalty', 0.0),
                presence_penalty=model_params.get('presence_penalty', 0.0),
                timeout=model_params.get('timeout', 30),
                retry_attempts=model_params.get('retry_attempts', 3),
                cost_per_1k_tokens=model_params.get('cost_per_1k_tokens', 0.01)
            )
            
            self.models[f"{provider.value}:{model_name}"] = model_config
    
    def configure_model(self, model_key: str, config: Dict[str, Any]) -> ModelConfig:
        """Configure specific model parameters"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Model not found: {model_key}")
            
            model = self.models[model_key]
            
            # Update configuration
            if 'max_tokens' in config:
                model.max_tokens = config['max_tokens']
            if 'temperature' in config:
                model.temperature = config['temperature']
            if 'top_p' in config:
                model.top_p = config['top_p']
            if 'frequency_penalty' in config:
                model.frequency_penalty = config['frequency_penalty']
            if 'presence_penalty' in config:
                model.presence_penalty = config['presence_penalty']
            if 'timeout' in config:
                model.timeout = config['timeout']
            if 'retry_attempts' in config:
                model.retry_attempts = config['retry_attempts']
            
            logger.info(f"Model configured: {model_key}")
            return model
            
        except Exception as e:
            logger.error(f"Model configuration failed: {e}")
            raise
    
    def get_model_config(self, model_key: str) -> Optional[ModelConfig]:
        """Get model configuration"""
        return self.models.get(model_key)
    
    def get_provider_config(self, provider: AIProvider) -> Optional[ProviderConfig]:
        """Get provider configuration"""
        return self.providers.get(provider)
    
    def list_available_models(self, provider: AIProvider = None) -> List[str]:
        """List available models"""
        if provider:
            return [key for key in self.models.keys() if key.startswith(provider.value)]
        return list(self.models.keys())
    
    def get_optimal_model(self, task_type: str, budget_limit: float = None) -> Optional[str]:
        """Get optimal model for task type and budget"""
        try:
            # Define task-model mapping
            task_preferences = {
                'text_generation': ['gpt-4', 'claude-3-opus', 'gpt-3.5-turbo'],
                'code_generation': ['gpt-4', 'claude-3-opus'],
                'translation': ['gpt-3.5-turbo', 'claude-3-sonnet'],
                'summarization': ['gpt-3.5-turbo', 'claude-3-sonnet'],
                'analysis': ['gpt-4', 'claude-3-opus']
            }
            
            preferred_models = task_preferences.get(task_type, ['gpt-3.5-turbo'])
            
            # Find best available model within budget
            for model_name in preferred_models:
                for model_key, model_config in self.models.items():
                    if model_name in model_key:
                        # Check if provider is enabled
                        provider_config = self.providers.get(model_config.provider)
                        if provider_config and provider_config.enabled:
                            # Check budget constraint
                            if budget_limit is None or model_config.cost_per_1k_tokens <= budget_limit:
                                return model_key
            
            return None
            
        except Exception as e:
            logger.error(f"Optimal model selection failed: {e}")
            return None
    
    def apply_profile(self, profile_name: str):
        """Apply configuration profile to all models"""
        try:
            if profile_name not in self.profiles:
                raise ValueError(f"Profile not found: {profile_name}")
            
            profile_config = self.profiles[profile_name]
            self.active_profile = profile_name
            
            # Apply to all models
            for model in self.models.values():
                if 'temperature' in profile_config:
                    model.temperature = profile_config['temperature']
                if 'max_tokens' in profile_config:
                    model.max_tokens = profile_config['max_tokens']
                if 'timeout' in profile_config:
                    model.timeout = profile_config['timeout']
            
            logger.info(f"Profile applied: {profile_name}")
            
        except Exception as e:
            logger.error(f"Profile application failed: {e}")
            raise
    
    def create_profile(self, name: str, config: Dict[str, Any]):
        """Create new configuration profile"""
        self.profiles[name] = config
        logger.info(f"Profile created: {name}")
    
    def estimate_cost(self, model_key: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for model usage"""
        try:
            model = self.models.get(model_key)
            if not model:
                return 0.0
            
            total_tokens = input_tokens + output_tokens
            cost = (total_tokens / 1000) * model.cost_per_1k_tokens
            
            return cost
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return 0.0
    
    def get_fallback_models(self, primary_model_key: str) -> List[str]:
        """Get fallback models for primary model"""
        try:
            primary_model = self.models.get(primary_model_key)
            if not primary_model:
                return []
            
            # Find models from different providers with similar capabilities
            fallback_models = []
            
            for model_key, model in self.models.items():
                if (model_key != primary_model_key and 
                    model.provider != primary_model.provider and
                    model.max_tokens >= primary_model.max_tokens * 0.8):
                    
                    # Check if provider is enabled
                    provider_config = self.providers.get(model.provider)
                    if provider_config and provider_config.enabled:
                        fallback_models.append(model_key)
            
            # Sort by cost (cheapest first)
            fallback_models.sort(key=lambda x: self.models[x].cost_per_1k_tokens)
            
            return fallback_models[:3]  # Return top 3 fallback options
            
        except Exception as e:
            logger.error(f"Fallback model selection failed: {e}")
            return []
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Check provider configurations
            if not self.providers:
                validation_result['errors'].append("No providers configured")
                validation_result['valid'] = False
            
            enabled_providers = [p for p in self.providers.values() if p.enabled]
            if not enabled_providers:
                validation_result['errors'].append("No enabled providers")
                validation_result['valid'] = False
            
            # Check model configurations
            if not self.models:
                validation_result['errors'].append("No models configured")
                validation_result['valid'] = False
            
            # Check for missing API keys
            for provider, config in self.providers.items():
                if config.enabled and not config.api_key:
                    validation_result['warnings'].append(f"Missing API key for {provider.value}")
            
            # Check for cost optimization opportunities
            expensive_models = [
                model_key for model_key, model in self.models.items()
                if model.cost_per_1k_tokens > 0.01
            ]
            
            if expensive_models:
                validation_result['recommendations'].append(
                    f"Consider using cheaper alternatives for models: {', '.join(expensive_models)}"
                )
            
            # Check for redundant configurations
            providers_count = len(enabled_providers)
            if providers_count > 3:
                validation_result['warnings'].append(
                    f"Many providers enabled ({providers_count}). Consider consolidating."
                )
            
            return validation_result
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {e}")
            return validation_result
    
    def export_configuration(self) -> str:
        """Export configuration as JSON"""
        try:
            config_data = {
                'providers': {
                    provider.value: asdict(config) 
                    for provider, config in self.providers.items()
                },
                'models': {
                    key: asdict(model) 
                    for key, model in self.models.items()
                },
                'profiles': self.profiles,
                'active_profile': self.active_profile,
                'exported_at': datetime.now().isoformat()
            }
            
            # Convert enums to strings for JSON serialization
            for provider_data in config_data['providers'].values():
                provider_data['provider'] = provider_data['provider'].value
            
            for model_data in config_data['models'].values():
                model_data['provider'] = model_data['provider'].value
            
            return json.dumps(config_data, indent=2)
            
        except Exception as e:
            logger.error(f"Configuration export failed: {e}")
            raise
    
    def import_configuration(self, config_json: str):
        """Import configuration from JSON"""
        try:
            config_data = json.loads(config_json)
            
            # Import providers
            for provider_name, provider_data in config_data.get('providers', {}).items():
                provider_enum = AIProvider(provider_name)
                provider_data['provider'] = provider_enum
                
                provider_config = ProviderConfig(**provider_data)
                self.providers[provider_enum] = provider_config
            
            # Import models
            for model_key, model_data in config_data.get('models', {}).items():
                model_data['provider'] = AIProvider(model_data['provider'])
                
                model_config = ModelConfig(**model_data)
                self.models[model_key] = model_config
            
            # Import profiles
            if 'profiles' in config_data:
                self.profiles.update(config_data['profiles'])
            
            # Set active profile
            if 'active_profile' in config_data:
                self.active_profile = config_data['active_profile']
            
            logger.info("Configuration imported successfully")
            
        except Exception as e:
            logger.error(f"Configuration import failed: {e}")
            raise


# Global instance
ai_config = AIConfig()