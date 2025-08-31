"""Translation Configuration - Multi-Provider API Settings

Centralized configuration for translation service providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TranslationProviderConfig:
    """Configuration for a translation provider"""
    enabled: bool
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    region: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    max_text_length: int = 5000
    supported_languages: int = 0
    quality_score: float = 0.8


class TranslationConfig:
    """Multi-provider translation configuration"""
    
    def __init__(self):
        self.providers = self._load_provider_configs()
        
    def _load_provider_configs(self) -> Dict[str, TranslationProviderConfig]:
        """Load configuration for all translation providers"""
        return {
            "google": TranslationProviderConfig(
                enabled=True,
                api_key=os.getenv('GOOGLE_TRANSLATE_API_KEY'),
                rate_limit=1000,
                max_text_length=5000,
                supported_languages=100,
                quality_score=0.85
            ),
            
            "deepl": TranslationProviderConfig(
                enabled=True,
                api_key=os.getenv('DEEPL_API_KEY'),
                endpoint=os.getenv('DEEPL_ENDPOINT', 'https://api-free.deepl.com'),
                rate_limit=500,
                max_text_length=30000,
                supported_languages=31,
                quality_score=0.95  # Highest quality for EU languages
            ),
            
            "azure": TranslationProviderConfig(
                enabled=True,
                api_key=os.getenv('AZURE_TRANSLATOR_KEY'),
                endpoint=os.getenv('AZURE_TRANSLATOR_ENDPOINT', 'https://api.cognitive.microsofttranslator.com'),
                region=os.getenv('AZURE_TRANSLATOR_REGION', 'global'),
                rate_limit=1000,
                max_text_length=10000,
                supported_languages=100,
                quality_score=0.90
            ),
            
            "aws": TranslationProviderConfig(
                enabled=True,
                region=os.getenv('AWS_REGION', 'us-east-1'),
                rate_limit=1000,
                max_text_length=10000,
                supported_languages=75,
                quality_score=0.85
            ),
            
            "openai": TranslationProviderConfig(
                enabled=True,
                api_key=os.getenv('OPENAI_API_KEY'),
                rate_limit=60,  # Lower rate limit for cost control
                max_text_length=4000,
                supported_languages=200,  # GPT supports many languages
                quality_score=0.88
            ),
            
            "marian": TranslationProviderConfig(
                enabled=True,
                rate_limit=100,  # Local processing
                max_text_length=2000,
                supported_languages=50,
                quality_score=0.75
            )
        }
    
    def get_provider_config(self, provider: str) -> Optional[TranslationProviderConfig]:
        """Get configuration for a specific provider"""
        return self.providers.get(provider)
    
    def get_enabled_providers(self) -> Dict[str, TranslationProviderConfig]:
        """Get all enabled providers"""
        return {
            name: config for name, config in self.providers.items() 
            if config.enabled and self._is_provider_ready(name, config)
        }
    
    def _is_provider_ready(self, provider: str, config: TranslationProviderConfig) -> bool:
        """Check if provider is properly configured and ready"""
        if provider in ["google", "deepl", "azure", "openai"]:
            return config.api_key is not None
        elif provider == "aws":
            # AWS uses IAM roles or environment credentials
            return True
        elif provider == "marian":
            # Local processing, no API key needed
            return True
        return False
    
    def get_language_coverage(self) -> Dict[str, int]:
        """Get language coverage summary for all providers"""
        return {
            name: config.supported_languages 
            for name, config in self.providers.items()
            if config.enabled
        }


# Global configuration instance
translation_config = TranslationConfig()


# Environment template for API keys
ENV_TEMPLATE = """
# Translation API Configuration
# Add these to your .env file

# Google Translate API
GOOGLE_TRANSLATE_API_KEY=your_google_api_key_here

# DeepL API (Free or Pro)
DEEPL_API_KEY=your_deepl_api_key_here
DEEPL_ENDPOINT=https://api-free.deepl.com  # or https://api.deepl.com for Pro

# Microsoft Azure Translator
AZURE_TRANSLATOR_KEY=your_azure_translator_key_here
AZURE_TRANSLATOR_REGION=your_azure_region_here
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com

# AWS Translate (uses AWS credentials)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
"""


def print_configuration_status():
    """Print current configuration status"""
    config = translation_config
    enabled_providers = config.get_enabled_providers()
    
    print("🌍 Translation Providers Configuration Status:")
    print("=" * 50)
    
    for provider, details in config.providers.items():
        status = "✅ READY" if provider in enabled_providers else "❌ NOT CONFIGURED"
        languages = details.supported_languages
        quality = details.quality_score
        
        print(f"{provider.upper():12} | {status:15} | {languages:3} languages | Quality: {quality:.2f}")
    
    total_languages = max(details.supported_languages for details in enabled_providers.values()) if enabled_providers else 0
    print(f"\nTotal Language Coverage: {total_languages} languages")
    print(f"Active Providers: {len(enabled_providers)}")


if __name__ == "__main__":
    print_configuration_status()
    print("\n" + ENV_TEMPLATE)