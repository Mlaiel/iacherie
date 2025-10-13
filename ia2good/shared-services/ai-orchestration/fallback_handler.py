"""
Fallback Handler
Handles AI service failures with automatic fallback to alternative providers
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class FallbackHandler:
    """Handle AI service failures with fallback strategies"""
    
    def __init__(self):
        self.fallback_model = os.getenv('AI_FALLBACK_MODEL', 'gpt-3.5-turbo')
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Track provider health
        self._provider_health: Dict[str, Dict[str, Any]] = {
            'openai': {'failures': 0, 'last_failure': None, 'healthy': True},
            'anthropic': {'failures': 0, 'last_failure': None, 'healthy': True},
            'google': {'failures': 0, 'last_failure': None, 'healthy': True}
        }
        
        # Fallback chain: primary -> secondary -> tertiary
        self.fallback_chains = {
            'gpt-4': ['gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-sonnet'],
            'gpt-4-turbo': ['gpt-3.5-turbo', 'claude-3-sonnet', 'gemini-pro'],
            'claude-3-opus': ['claude-3-sonnet', 'gpt-4', 'gemini-pro'],
            'claude-3-sonnet': ['claude-3-haiku', 'gpt-3.5-turbo', 'gemini-pro'],
            'gemini-ultra': ['gemini-pro', 'gpt-4', 'claude-3-sonnet']
        }
    
    def record_failure(self, provider: str) -> None:
        """
        Record a failure for a provider
        
        Args:
            provider: Provider name (openai, anthropic, google)
        """
        if provider in self._provider_health:
            health = self._provider_health[provider]
            health['failures'] += 1
            health['last_failure'] = datetime.utcnow()
            
            # Mark as unhealthy if too many failures
            if health['failures'] >= 5:
                health['healthy'] = False
                print(f"[AI Fallback] Provider {provider} marked as unhealthy")
    
    def record_success(self, provider: str) -> None:
        """
        Record a success for a provider
        
        Args:
            provider: Provider name
        """
        if provider in self._provider_health:
            health = self._provider_health[provider]
            health['failures'] = max(0, health['failures'] - 1)
            
            # Mark as healthy if recovered
            if health['failures'] == 0:
                health['healthy'] = True
    
    def is_provider_healthy(self, provider: str) -> bool:
        """
        Check if provider is healthy
        
        Args:
            provider: Provider name
            
        Returns:
            True if healthy
        """
        if provider not in self._provider_health:
            return True
        
        health = self._provider_health[provider]
        
        # Auto-recover after 5 minutes
        if not health['healthy'] and health['last_failure']:
            time_since_failure = datetime.utcnow() - health['last_failure']
            if time_since_failure > timedelta(minutes=5):
                health['healthy'] = True
                health['failures'] = 0
                print(f"[AI Fallback] Provider {provider} auto-recovered")
        
        return health['healthy']
    
    def get_fallback_models(self, primary_model: str) -> List[str]:
        """
        Get fallback models for a primary model
        
        Args:
            primary_model: Primary model name
            
        Returns:
            List of fallback models
        """
        return self.fallback_chains.get(primary_model, [self.fallback_model])
    
    async def execute_with_fallback(
        self,
        primary_fn,
        fallback_fns: Optional[List] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function with automatic fallback
        
        Args:
            primary_fn: Primary function to execute
            fallback_fns: List of fallback functions
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Result from successful execution
        """
        functions = [primary_fn] + (fallback_fns or [])
        
        last_error = None
        
        for i, fn in enumerate(functions):
            try:
                print(f"[AI Fallback] Attempting function #{i+1}")
                result = await fn(*args, **kwargs)
                
                if result.get('success'):
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
                    
            except Exception as e:
                last_error = str(e)
                print(f"[AI Fallback] Function #{i+1} failed: {e}")
                continue
        
        # All attempts failed
        return {
            'success': False,
            'error': f'All attempts failed. Last error: {last_error}',
            'text': ''
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all providers
        
        Returns:
            Dict with provider health status
        """
        return {
            provider: {
                'healthy': info['healthy'],
                'failures': info['failures'],
                'last_failure': info['last_failure'].isoformat() if info['last_failure'] else None
            }
            for provider, info in self._provider_health.items()
        }
    
    def reset_health(self, provider: Optional[str] = None) -> None:
        """
        Reset health status for provider(s)
        
        Args:
            provider: Specific provider or None for all
        """
        if provider:
            if provider in self._provider_health:
                self._provider_health[provider] = {
                    'failures': 0,
                    'last_failure': None,
                    'healthy': True
                }
                print(f"[AI Fallback] Reset health for {provider}")
        else:
            for p in self._provider_health:
                self._provider_health[p] = {
                    'failures': 0,
                    'last_failure': None,
                    'healthy': True
                }
            print("[AI Fallback] Reset health for all providers")
