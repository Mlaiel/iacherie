"""Middleware Index Module
======================

Central index for all middleware components in the IA Influencer Agent crawler system.
Provides easy access to all middleware functionality with optimized imports.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Usage:
    from crawlers.middleware.index import MiddlewareRegistry
    
    # Get specific middleware
    auth_middleware = MiddlewareRegistry.get_authentication()
    rate_limiter = MiddlewareRegistry.get_rate_limiter()
    
    # Create configured pipeline
    pipeline = MiddlewareRegistry.create_enterprise_pipeline()
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from . import (
    MiddlewarePipeline,
    create_full_pipeline,
    create_basic_pipeline,
    create_content_pipeline,
    get_authentication_middleware,
    get_rate_limiting_middleware,
    get_security_middleware,
    get_content_processing_middleware,
    get_fingerprinting_middleware,
    get_monitoring_middleware,
    get_error_handling_middleware,
    get_validation_middleware
)

logger = logging.getLogger(__name__)


class MiddlewareRegistry:
    """    Central registry for all middleware components
    
    Provides singleton access to middleware instances and factory methods
    for creating pre-configured pipelines optimized for different use cases.
    """    
    _instances = {}
    _pipelines = {}
    
    @classmethod
    def get_authentication(cls):
        """Get authentication middleware instance"""        if 'auth' not in cls._instances:
            cls._instances['auth'] = get_authentication_middleware()
        return cls._instances['auth']
    
    @classmethod
    def get_rate_limiter(cls):
        """Get rate limiting middleware instance"""        if 'rate_limit' not in cls._instances:
            cls._instances['rate_limit'] = get_rate_limiting_middleware()
        return cls._instances['rate_limit']
    
    @classmethod
    def get_security(cls):
        """Get security middleware instance"""        if 'security' not in cls._instances:
            cls._instances['security'] = get_security_middleware()
        return cls._instances['security']
    
    @classmethod
    def get_content_processor(cls):
        """Get content processing middleware instance"""        if 'processing' not in cls._instances:
            cls._instances['processing'] = get_content_processing_middleware()
        return cls._instances['processing']
    
    @classmethod
    def get_fingerprinter(cls):
        """Get fingerprinting middleware instance"""        if 'fingerprinting' not in cls._instances:
            cls._instances['fingerprinting'] = get_fingerprinting_middleware()
        return cls._instances['fingerprinting']
    
    @classmethod
    def get_monitor(cls):
        """Get monitoring middleware instance"""        if 'monitoring' not in cls._instances:
            cls._instances['monitoring'] = get_monitoring_middleware()
        return cls._instances['monitoring']
    
    @classmethod
    def get_error_handler(cls):
        """Get error handling middleware instance"""        if 'error_handling' not in cls._instances:
            cls._instances['error_handling'] = get_error_handling_middleware()
        return cls._instances['error_handling']
    
    @classmethod
    def get_validator(cls):
        """Get validation middleware instance"""        if 'validation' not in cls._instances:
            cls._instances['validation'] = get_validation_middleware()
        return cls._instances['validation']
    
    @classmethod
    def create_enterprise_pipeline(cls) -> MiddlewarePipeline:
        """Create enterprise-grade pipeline with all features enabled"""        if 'enterprise' not in cls._pipelines:
            cls._pipelines['enterprise'] = create_full_pipeline()
        return cls._pipelines['enterprise']
    
    @classmethod
    def create_music_pipeline(cls) -> MiddlewarePipeline:
        """Create optimized pipeline for music content processing"""        if 'music' not in cls._pipelines:
            cls._pipelines['music'] = MiddlewarePipeline(
                enable_authentication=True,
                enable_rate_limiting=True,
                enable_security=True,
                enable_validation=True,
                enable_processing=True,  # Essential for audio processing
                enable_fingerprinting=True,  # Critical for music protection
                enable_monitoring=True,
                enable_error_handling=True
            )
        return cls._pipelines['music']
    
    @classmethod
    def create_social_media_pipeline(cls) -> MiddlewarePipeline:
        """Create optimized pipeline for social media content"""        if 'social' not in cls._pipelines:
            cls._pipelines['social'] = MiddlewarePipeline(
                enable_authentication=True,
                enable_rate_limiting=True,  # Critical for API limits
                enable_security=True,  # Important for public content
                enable_validation=True,
                enable_processing=True,
                enable_fingerprinting=True,
                enable_monitoring=True,
                enable_error_handling=True
            )
        return cls._pipelines['social']
    
    @classmethod
    def create_high_volume_pipeline(cls) -> MiddlewarePipeline:
        """Create optimized pipeline for high-volume processing"""        if 'high_volume' not in cls._pipelines:
            cls._pipelines['high_volume'] = MiddlewarePipeline(
                enable_authentication=True,
                enable_rate_limiting=False,  # Disabled for internal high-volume
                enable_security=False,  # Basic security only
                enable_validation=True,
                enable_processing=True,
                enable_fingerprinting=False,  # Disabled for performance
                enable_monitoring=True,  # Essential for high-volume
                enable_error_handling=True
            )
        return cls._pipelines['high_volume']
    
    @classmethod
    def create_api_gateway_pipeline(cls) -> MiddlewarePipeline:
        """Create pipeline optimized for API gateway usage"""        if 'api_gateway' not in cls._pipelines:
            cls._pipelines['api_gateway'] = MiddlewarePipeline(
                enable_authentication=True,  # Critical for API access
                enable_rate_limiting=True,  # Essential for API protection
                enable_security=True,  # Important for external access
                enable_validation=True,  # Critical for API data
                enable_processing=False,  # Defer to downstream services
                enable_fingerprinting=False,  # Not needed at gateway
                enable_monitoring=True,  # Essential for API metrics
                enable_error_handling=True  # Critical for API reliability
            )
        return cls._pipelines['api_gateway']
    
    @classmethod
    def get_pipeline_for_content_type(cls, content_type: str) -> MiddlewarePipeline:
        """Get optimized pipeline based on content type"""        
        content_type = content_type.lower()
        
        if content_type in ['audio', 'music', 'sound']:
            return cls.create_music_pipeline()
        elif content_type in ['video', 'movie', 'film']:
            return cls.create_content_pipeline()
        elif content_type in ['image', 'photo', 'picture']:
            return cls.create_content_pipeline()
        elif content_type in ['text', 'blog', 'article']:
            return cls.create_social_media_pipeline()
        elif content_type in ['social', 'post', 'tweet']:
            return cls.create_social_media_pipeline()
        else:
            return cls.create_enterprise_pipeline()
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached instances and pipelines"""        cls._instances.clear()
        cls._pipelines.clear()
        logger.info("Middleware registry cache cleared")
    
    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        """Get health status of all middleware components"""        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        try:
            # Check each component
            components = {
                "authentication": cls.get_authentication(),
                "rate_limiter": cls.get_rate_limiter(),
                "security": cls.get_security(),
                "content_processor": cls.get_content_processor(),
                "fingerprinter": cls.get_fingerprinter(),
                "monitor": cls.get_monitor(),
                "error_handler": cls.get_error_handler(),
                "validator": cls.get_validator()
            }
            
            for name, component in components.items():
                try:
                    # Try to call a basic method if available
                    if hasattr(component, 'health_check'):
                        health = component.health_check()
                        status["components"][name] = health
                    else:
                        status["components"][name] = {
                            "status": "available",
                            "initialized": True
                        }
                except Exception as e:
                    status["components"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    status["overall_status"] = "degraded"
            
        except Exception as e:
            status["overall_status"] = "error"
            status["error"] = str(e)
        
        return status


class MiddlewareUtils:
    """Utility functions for middleware operations"""    
    @staticmethod
    def validate_request_format(request_data: Dict[str, Any]) -> bool:
        """Validate if request data has required format for middleware processing"""        required_fields = ['request_id', 'timestamp']
        return all(field in request_data for field in required_fields)
    
    @staticmethod
    def add_request_metadata(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add standard metadata to request"""        if 'metadata' not in request_data:
            request_data['metadata'] = {}
        
        request_data['metadata'].update({
            'middleware_version': '2.0.0',
            'processing_timestamp': datetime.utcnow().isoformat(),
            'pipeline_id': f"pipe_{int(datetime.utcnow().timestamp())}"
        })
        
        return request_data
    
    @staticmethod
    def extract_business_context(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business context from request for optimization"""        context = {}
        
        # Extract user tier for rate limiting
        if 'user_tier' in request_data:
            context['user_tier'] = request_data['user_tier']
        
        # Extract content type for processing optimization
        if 'content_type' in request_data:
            context['content_type'] = request_data['content_type']
        
        # Extract geographic context
        if 'geolocation' in request_data:
            context['region'] = request_data['geolocation'].get('region')
        
        # Extract business priority
        if 'priority' in request_data:
            context['priority'] = request_data['priority']
        
        return context


# Export all components for easy access
__all__ = [
    'MiddlewareRegistry',
    'MiddlewareUtils'
]
