"""
Fallback Manager - Handles API failures and fallback strategies
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIProvider:
    """
        Represents an external API provider"""
    
    def __init__(
        self,
        name: str,
        capability_type: str,
        priority: int = 1,
        cost_per_request: float = 0.0
    ):
        self.name = name
        self.capability_type = capability_type
        self.priority = priority
        self.cost_per_request = cost_per_request
        
        # Health tracking
        self.is_available = True
        self.last_failure: Optional[datetime] = None
        self.failure_count = 0
        self.success_count = 0
        self.avg_response_time_ms = 0.0


class FallbackManager:
    """
    Manages fallback strategies when APIs fail
    Automatically switches to backup providers
    """
    
    def __init__(self):
        self.providers: Dict[str, List[APIProvider]] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """
        Initialize available API providers for each capability"""
        
        # Text generation providers
        self.providers['text_generation'] = [
            APIProvider('OpenAI GPT-4', 'text_generation', priority=1, cost_per_request=0.03),
            APIProvider('Anthropic Claude', 'text_generation', priority=2, cost_per_request=0.02),
            APIProvider('Google Gemini', 'text_generation', priority=3, cost_per_request=0.01)
        ]
        
        # Image generation providers
        self.providers['image_generation'] = [
            APIProvider('DALL-E 3', 'image_generation', priority=1, cost_per_request=0.04),
            APIProvider('Midjourney', 'image_generation', priority=2, cost_per_request=0.05),
            APIProvider('Stable Diffusion', 'image_generation', priority=3, cost_per_request=0.01)
        ]
        
        # Video generation providers
        self.providers['video_generation'] = [
            APIProvider('RunwayML', 'video_generation', priority=1, cost_per_request=1.0),
            APIProvider('Pexels', 'video_generation', priority=2, cost_per_request=0.0)
        ]
        
        # Audio generation providers
        self.providers['audio_generation'] = [
            APIProvider('ElevenLabs', 'audio_generation', priority=1, cost_per_request=0.10),
            APIProvider('Google TTS', 'audio_generation', priority=2, cost_per_request=0.01)
        ]
    
    def execute_with_fallback(
        self,
        capability_type: str,
        input_data: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute API call with automatic fallback to backup providers
        
        Args:
            capability_type: Type of capability to execute
            input_data: Input parameters
            max_retries: Maximum number of providers to try
        
        Returns:
            Dict with result or error
        """
        
        providers = self._get_available_providers(capability_type)

        
        if not providers:
            return {
                'success': False,
                'error': f'No available providers for {capability_type}',
                'provider': None
            }
        
        # Try providers in order of priority
        for i, provider in enumerate(providers[:max_retries]):
            try:
                logger.info(f"Trying provider {provider.name} (attempt {i+1}/{max_retries})")


                
                result = self._call_provider(provider, input_data)

                
                if result['success']:
                    # Update provider stats
                    provider.success_count += 1
                    provider.is_available = True
                    
                    result['provider'] = provider.name
                    result['cost'] = provider.cost_per_request
                    result['fallback_used'] = i > 0
                    
                    return result
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")

                provider.failure_count += 1
                provider.last_failure = datetime.now()
                
                # Mark as unavailable if too many failures
                if provider.failure_count > 5:
                    provider.is_available = False
                
                continue
        
        # All providers failed
        return {
            'success': False,
            'error': 'All providers failed',
            'provider': None,
            'attempts': max_retries
        }
    
    def _get_available_providers(self, capability_type: str) -> List[APIProvider]:
        """Get list of available providers sorted by priority"""
        
        providers = self.providers.get(capability_type, [])
        
        # Filter available and sort by priority

        available = [p for p in providers if self._is_provider_available(p)]
        available.sort(key=lambda p: p.priority)

        
        return available
    
    def _is_provider_available(self, provider: APIProvider) -> bool:
        """
        Check if provider is available for use"""
        
        if not provider.is_available:
            # Check if enough time has passed to retry
            if provider.last_failure:
                time_since_failure = datetime.now() - provider.last_failure
                if time_since_failure > timedelta(minutes=5):
                    provider.is_available = True
                    provider.failure_count = 0
                    return True
            return False
        
        return True
    
    def _call_provider(
        self,
        provider: APIProvider,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call external API provider
        This is a placeholder - actual implementation would call real APIs
        """        # In real system, this would make actual API calls
        
        import random
        
        # Simulate API call with 80% success rate
        if random.random() < 0.8:
            return {
                'success': True,
                'data': {
                    'result': f'Result from {provider.name}',
                    'input': input_data
                },
                'response_time_ms': random.uniform(100, 500)
            }
        else:
            raise Exception(f'{provider.name} temporarily unavailable')
    
    def get_provider_health(self) -> Dict[str, Any]:
        """
        Get health status of all providers"""
        
        health_status = {}
        
        for capability_type, providers in self.providers.items():
            health_status[capability_type] = [
                {
                    'name': p.name,
                    'available': p.is_available,
                    'priority': p.priority,
                    'success_rate': (
                        p.success_count / (p.success_count + p.failure_count)

                        if (p.success_count + p.failure_count) > 0 else 0
                    ),
                    'total_requests': p.success_count + p.failure_count,
                    'cost_per_request': p.cost_per_request
                }
                for p in providers
            ]
        
        return health_status
