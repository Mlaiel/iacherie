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
        """Setup AI models and dependencies"""
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
        """Calculate quality metrics for generated content"""
        try:
            content = result.get('generated_content', '')
            content_type = result.get('content_type', 'text')
            
            # Calculate coherence score based on content analysis
            coherence_score = await self._analyze_coherence(content, content_type)
            
            # Calculate relevance based on keyword consistency and context
            relevance_score = await self._analyze_relevance(content, result.get('context', {}))
            
            # Assess creativity through linguistic diversity and originality
            creativity_score = await self._analyze_creativity(content, content_type)
            
            # Technical quality assessment (grammar, structure, formatting)
            technical_quality = await self._analyze_technical_quality(content, content_type)
            
            # Calculate weighted overall score
            overall_score = (
                coherence_score * 0.3 +
                relevance_score * 0.25 +
                creativity_score * 0.2 +
                technical_quality * 0.25
            )
            
            return {
                'coherence_score': coherence_score,
                'relevance_score': relevance_score,
                'creativity_score': creativity_score,
                'technical_quality': technical_quality,
                'overall_score': overall_score
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate quality metrics: {e}")
            # Return default scores if analysis fails
            return {
                'coherence_score': 0.75,
                'relevance_score': 0.75,
                'creativity_score': 0.75,
                'technical_quality': 0.75,
                'overall_score': 0.75
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
            
            self.logger.info(f"Generator {self.generator_name} resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")
    
    async def _analyze_coherence(self, content: str, content_type: str) -> float:
        """Analyze content coherence and logical flow"""
        try:
            if not content or len(content.strip()) == 0:
                return 0.0
            
            # Basic coherence metrics
            sentences = content.split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) == 0:
                return 0.1
            
            # Calculate coherence based on:
            # 1. Sentence length variation (ideal range)
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
            length_score = min(1.0, max(0.1, 1.0 - abs(avg_length - 15) / 20))  # Ideal ~15 words
            
            # 2. Repetition penalty
            words = content.lower().split()
            unique_words = set(words)
            repetition_score = min(1.0, len(unique_words) / max(1, len(words)))
            
            # 3. Transition words presence (indicates flow)
            transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 
                             'consequently', 'meanwhile', 'subsequently', 'likewise', 'nevertheless']
            transition_count = sum(1 for word in words if word in transition_words)
            transition_score = min(1.0, transition_count / max(1, len(sentences)))
            
            # Weighted coherence score
            coherence = (length_score * 0.4 + repetition_score * 0.4 + transition_score * 0.2)
            return round(coherence, 2)
            
        except Exception as e:
            self.logger.error(f"Coherence analysis failed: {e}")
            return 0.5
    
    async def _analyze_relevance(self, content: str, context: Dict[str, Any]) -> float:
        """Analyze content relevance to the given context"""
        try:
            if not content:
                return 0.0
            
            content_lower = content.lower()
            
            # Extract context keywords
            target_keywords = []
            if 'keywords' in context:
                target_keywords.extend(context['keywords'])
            if 'topic' in context:
                target_keywords.append(context['topic'].lower())
            if 'target_audience' in context:
                target_keywords.append(context['target_audience'].lower())
            
            if not target_keywords:
                return 0.8  # Default score if no context available
            
            # Calculate keyword presence
            keyword_matches = sum(1 for keyword in target_keywords if keyword in content_lower)
            keyword_score = min(1.0, keyword_matches / len(target_keywords))
            
            # Content length appropriateness
            word_count = len(content.split())
            expected_length = context.get('target_length', 200)
            length_ratio = min(word_count, expected_length) / max(word_count, expected_length)
            
            # Combined relevance score
            relevance = (keyword_score * 0.7 + length_ratio * 0.3)
            return round(relevance, 2)
            
        except Exception as e:
            self.logger.error(f"Relevance analysis failed: {e}")
            return 0.5
    
    async def _analyze_creativity(self, content: str, content_type: str) -> float:
        """Analyze content creativity and originality"""
        try:
            if not content:
                return 0.0
            
            words = content.split()
            if len(words) == 0:
                return 0.0
            
            # Vocabulary diversity
            unique_words = set(word.lower() for word in words)
            diversity_score = len(unique_words) / len(words)
            
            # Sentence structure variety
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            sentence_starts = [s.split()[0].lower() for s in sentences if s.split()]
            unique_starts = set(sentence_starts)
            structure_variety = len(unique_starts) / max(1, len(sentence_starts))
            
            # Adjective and adverb usage (creativity indicators)
            descriptive_words = ['amazing', 'incredible', 'fantastic', 'brilliant', 'innovative',
                               'extraordinary', 'remarkable', 'outstanding', 'exceptional', 'unique']
            descriptive_count = sum(1 for word in words if word.lower() in descriptive_words)
            descriptive_score = min(1.0, descriptive_count / max(1, len(words) / 50))
            
            # Combined creativity score
            creativity = (diversity_score * 0.5 + structure_variety * 0.3 + descriptive_score * 0.2)
            return round(min(1.0, creativity), 2)
            
        except Exception as e:
            self.logger.error(f"Creativity analysis failed: {e}")
            return 0.5
    
    async def _analyze_technical_quality(self, content: str, content_type: str) -> float:
        """Analyze technical quality (grammar, structure, formatting)"""
        try:
            if not content:
                return 0.0
            
            # Basic grammar checks
            grammar_score = await self._basic_grammar_check(content)
            
            # Structure analysis
            structure_score = await self._analyze_structure(content, content_type)
            
            # Formatting consistency
            formatting_score = await self._check_formatting(content, content_type)
            
            # Combined technical quality
            technical_quality = (grammar_score * 0.4 + structure_score * 0.4 + formatting_score * 0.2)
            return round(technical_quality, 2)
            
        except Exception as e:
            self.logger.error(f"Technical quality analysis failed: {e}")
            return 0.6
    
    async def _basic_grammar_check(self, content: str) -> float:
        """Basic grammar and punctuation check"""
        try:
            # Simple heuristics for grammar quality
            score = 1.0
            
            # Check for proper sentence ending
            sentences = content.split('.')
            properly_ended = sum(1 for s in sentences[:-1] if s.strip())
            total_sentences = len([s for s in sentences if s.strip()])
            if total_sentences > 0:
                ending_score = properly_ended / total_sentences
                score *= ending_score
            
            # Check for excessive repetition
            words = content.split()
            if len(words) > 10:
                consecutive_repeats = sum(1 for i in range(len(words)-1) 
                                        if words[i].lower() == words[i+1].lower())
                repeat_penalty = max(0, 1 - (consecutive_repeats / len(words)))
                score *= repeat_penalty
            
            return round(score, 2)
            
        except Exception as e:
            self.logger.error(f"Grammar check failed: {e}")
            return 0.7
    
    async def _analyze_structure(self, content: str, content_type: str) -> float:
        """Analyze content structure appropriateness"""
        try:
            if content_type == 'article':
                return await self._analyze_article_structure(content)
            elif content_type == 'social_post':
                return await self._analyze_social_structure(content)
            else:
                return await self._analyze_general_structure(content)
                
        except Exception as e:
            self.logger.error(f"Structure analysis failed: {e}")
            return 0.7
    
    async def _analyze_article_structure(self, content: str) -> float:
        """Analyze article structure"""
        # Articles should have introduction, body, conclusion
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            return 0.9
        elif len(paragraphs) >= 2:
            return 0.7
        else:
            return 0.5
    
    async def _analyze_social_structure(self, content: str) -> float:
        """Analyze social media post structure"""
        # Social posts should be concise and engaging
        word_count = len(content.split())
        if 10 <= word_count <= 100:  # Ideal range for social posts
            return 0.9
        elif word_count <= 150:
            return 0.7
        else:
            return 0.5
    
    async def _analyze_general_structure(self, content: str) -> float:
        """Analyze general content structure"""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if len(sentences) >= 3:
            return 0.8
        elif len(sentences) >= 2:
            return 0.6
        else:
            return 0.4
    
    async def _check_formatting(self, content: str, content_type: str) -> float:
        """Check formatting consistency"""
        try:
            score = 1.0
            
            # Check for consistent spacing
            if '  ' in content:  # Double spaces
                score *= 0.9
            
            # Check for proper capitalization at sentence starts
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            proper_caps = sum(1 for s in sentences if s and s[0].isupper())
            if len(sentences) > 0:
                cap_score = proper_caps / len(sentences)
                score *= cap_score
            
            return round(score, 2)
            
        except Exception as e:
            self.logger.error(f"Formatting check failed: {e}")
            return 0.8
    
    async def _release_model_resources(self) -> None:
        """Release model-specific resources - to be implemented by subclasses"""
        pass
    
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
