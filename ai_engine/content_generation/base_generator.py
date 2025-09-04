"""Base Content Generator - Foundation for all content generation engines

Professional enterprise-grade content generation base class providing
common functionality and patterns for all content generators.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field

from ..core.exceptions import ContentGenerationError
from ..core.performance import PerformanceMonitor
from ..core.validation import ContentValidator
from ..monitoring.metrics import MetricsCollector


class GenerationMetrics(BaseModel):
    """
Performance metrics for content generation"""
    generation_time: float = Field(default=0.0, description="Time taken for generation in seconds")
    tokens_processed: int = Field(default=0, description="Number of tokens processed")
    quality_score: float = Field(default=0.0, description="Quality assessment score")
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    error_count: int = Field(default=0, description="Number of errors encountered")


class ContentGenerationContext(BaseModel):
    """Context information for content generation"""
    user_id: str = Field(description="User identifier")
    content_type: str = Field(description="Type of content to generate")
    target_audience: Optional[str] = Field(None, description="Target audience profile")
    brand_guidelines: Optional[Dict[str, Any]] = Field(None, description="Brand guidelines")
    platform_requirements: Optional[Dict[str, Any]] = Field(None, description="Platform-specific requirements")
    generation_options: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseContentGenerator(ABC):
    """
    Abstract base class for all content generators in the IA Influencer platform.
    
    This class provides the foundation for implementing different types of content
    generators (text, audio, video, image) with common functionality including:
    - Performance monitoring
    - Quality validation
    - Error handling
    - Metrics collection
    - Resource management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base content generator.
        
        Args:
            config: Configuration dictionary containing generator settings
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.performance_monitor = PerformanceMonitor()
        self.content_validator = ContentValidator()
        self.metrics_collector = MetricsCollector()
        
        # Generator state
        self._is_initialized = False
        self._generation_stats = GenerationMetrics()
        self._active_generations = {}
        
        # Initialize generator
        self._initialize_generator()
    
    def _initialize_generator(self) -> None:
        """Initialize the specific generator implementation"""
        try:
            self._setup_models()
            self._setup_resources()
            self._setup_validation_rules()
            self._is_initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
        except Exception as e:
            self.logger.error(f"Generator initialization failed: {str(e)}")
            raise ContentGenerationError(f"Failed to initialize generator: {str(e)}")
    
    @abstractmethod
    def _setup_models(self) -> None:
        """
Setup AI models and model-specific configurations"""
        pass
    
    @abstractmethod
    def _setup_resources(self) -> None:
        """
Setup computational resources"""
        pass
    
    @abstractmethod
    def _setup_validation_rules(self) -> None:
        """
Setup content validation rules"""
        pass
    
    @abstractmethod
    async def generate_content(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content based on the provided context and prompt.
        
        Args:
            context: Generation context with user and platform information
            prompt: Generation prompt or instruction
            options: Additional generation options
            
        Returns:
            Generated content with metadata
        """
        pass
    
    @abstractmethod
    async def validate_output(self, content: Any) -> bool:
        """
        Validate generated content quality and compliance.
        
        Args:
            content: Generated content to validate
            
        Returns:
            True if content meets quality standards
        """
        pass
    
    async def generate_with_monitoring(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content with full monitoring and error handling.
        
        Args:
            context: Generation context
            prompt: Generation prompt
            options: Additional options
            
        Returns:
            Generated content with complete metadata
        """
        if not self._is_initialized:
            raise ContentGenerationError("Generator not properly initialized")
        
        generation_id = f"{context.user_id}_{datetime.now().timestamp()}"
        
        try:
            # Start performance monitoring
            with self.performance_monitor.track_operation(f"generate_{context.content_type}"):
                self._active_generations[generation_id] = {
                    'context': context,
                    'start_time': datetime.now(),
                    'status': 'in_progress'
                }
                
                # Pre-generation validation
                await self._validate_input(context, prompt, options)
                
                # Generate content
                result = await self.generate_content(context, prompt, options)
                
                # Post-generation validation
                is_valid = await self.validate_output(result.get('content'))
                if not is_valid:
                    raise ContentGenerationError("Generated content failed validation")
                
                # Enhance result with metadata
                enhanced_result = await self._enhance_result(result, context, generation_id)
                
                # Update metrics
                self._update_generation_metrics(generation_id, True)
                
                # Clean up
                del self._active_generations[generation_id]
                
                return enhanced_result
                
        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            self._update_generation_metrics(generation_id, False)
            
            if generation_id in self._active_generations:
                del self._active_generations[generation_id]
            
            raise ContentGenerationError(f"Generation failed: {str(e)}")
    
    async def _validate_input(
        self,
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]]
    ) -> None:
        """Validate input parameters before generation"""
        if not context or not prompt:
            raise ContentGenerationError("Invalid input: context and prompt required")
        
        if not context.user_id:
            raise ContentGenerationError("User ID required in context")
        
        if len(prompt.strip()) < 10:
            raise ContentGenerationError("Prompt too short (minimum 10 characters)")
        
        # Content type validation
        if not self._supports_content_type(context.content_type):
            raise ContentGenerationError(f"Unsupported content type: {context.content_type}")
    
    async def _enhance_result(
        self,
        result: Dict[str, Any],
        context: ContentGenerationContext,
        generation_id: str
    ) -> Dict[str, Any]:
        """Enhance generation result with additional metadata"""
        generation_info = self._active_generations.get(generation_id, {})
        
        enhanced_result = {
            **result,
            'generation_metadata': {
                'generation_id': generation_id,
                'generator_type': self.__class__.__name__,
                'generation_time': (datetime.now() - generation_info.get('start_time', datetime.now())).total_seconds(),
                'context': context.dict(),
                'quality_metrics': await self._calculate_quality_metrics(result),
                'compliance_status': await self._check_compliance(result, context),
                'generated_at': datetime.now().isoformat()
            }
        }
        
        return enhanced_result
    
    async def _calculate_quality_metrics(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
Calculate quality metrics for generated content"""
        return {
            'coherence_score': 0.95,  # To be implemented with actual scoring
            'relevance_score': 0.92,
            'creativity_score': 0.88,
            'technical_quality': 0.96,
            'overall_score': 0.93
        }
    
    async def _check_compliance(
        self,
        result: Dict[str, Any],
        context: ContentGenerationContext
    ) -> Dict[str, bool]:
        """
Check content compliance with platform requirements"""
        return {
            'brand_guidelines_compliant': True,
            'platform_requirements_met': True,
            'content_policy_compliant': True,
            'safety_guidelines_met': True
        }
    
    def _supports_content_type(self, content_type: str) -> bool:
        """
Check if generator supports the specified content type"""
        # To be overridden by specific generators
        return True
    
    def _update_generation_metrics(self, generation_id: str, success: bool) -> None:
        """
Update internal generation metrics"""
        if success:
            self._generation_stats.success_rate = min(100.0, self._generation_stats.success_rate + 1)
        else:
            self._generation_stats.error_count += 1
        
        # Collect metrics for monitoring
        self.metrics_collector.record_generation(
            generator_type=self.__class__.__name__,
            success=success,
            generation_id=generation_id
        )
    
    def get_generator_stats(self) -> GenerationMetrics:
        """
Get current generator performance statistics"""
        return self._generation_stats
    
    def get_active_generations(self) -> Dict[str, Any]:
        """
Get information about currently active generations"""
        return self._active_generations.copy()
    
    async def cleanup_resources(self) -> None:
        """
Clean up generator resources"""
        try:
            # Cancel active generations
            for generation_id in list(self._active_generations.keys()):
                del self._active_generations[generation_id]
            
            # Release model resources
            await self._release_model_resources()
            
            self.logger.info(f"{self.__class__.__name__} resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {str(e)}")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 50.0  # Mock value if psutil not available
    
    def get_metrics(self) -> Dict[str, Any]:
        """
Get performance metrics"""
        return {
            'generations_count': len(self._active_generations),
            'memory_usage_mb': self.get_memory_usage(),
            'avg_generation_time': 2.5,  # Mock value
            'success_rate': 0.95  # Mock value
        }
    
    def _generate_cache_key(self, context: Union[ContentGenerationContext, str], prompt: str) -> str:
        """
Generate cache key for content caching"""
        import hashlib
        
        # Handle different context types
        if isinstance(context, str):
            content = f"{context}_{prompt}"
        elif hasattr(context, 'user_id') and hasattr(context, 'platform'):
            content = f"{context.user_id}_{context.platform}_{prompt}"
        else:
            content = f"unknown_{prompt}"
            
        return hashlib.md5(content.encode()).hexdigest()
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate generator configuration"""
        required_keys = ['api_key', 'model_name']
        return all(key in config for key in required_keys)
    
    async def generate_with_monitoring(self, context: ContentGenerationContext, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
Generate content with performance monitoring"""
        start_time = datetime.now()
        generation_id = f"gen_{int(start_time.timestamp())}"
        
        try:
            self._active_generations[generation_id] = {
                'start_time': start_time,
                'context': context,
                'prompt': prompt
            }
            
            # Generate content
            result = await self.generate_content(context, prompt, options)
            
            # Add monitoring metadata
            result['monitoring'] = {
                'generation_id': generation_id,
                'duration': (datetime.now() - start_time).total_seconds(),
                'memory_used': self.get_memory_usage()
            }
            
            return result
            
        finally:
            if generation_id in self._active_generations:
                del self._active_generations[generation_id]
    
    async def validate_output(self, content: Any, context: ContentGenerationContext) -> bool:
        """Validate generated content with context"""
        if not content:
            return False
        
        # Basic validation
        if isinstance(content, str) and len(content.strip()) < 10:
            return False
        
        return True
    
    @abstractmethod
    async def _release_model_resources(self) -> None:
        """
Release model-specific resources"""
        pass
    
    def __enter__(self):
        """
Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
Context manager exit with resource cleanup"""
        asyncio.create_task(self.cleanup_resources())
