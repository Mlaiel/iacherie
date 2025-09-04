"""Media Generator Orchestrator - Main Factory and Coordination System

Central orchestrator for all media generation types including:
- Avatar generation (8 types)
- Voice synthesis (6 types)
- Image generation (10 types)
- Video generation (7 types)
- Text generation (4 types)

Provides unified interface, workflow management, and cross-media coordination.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .avatar_generator import AvatarGenerator
from .voice_generator import VoiceGenerator
from .image_generator import MediaImageGenerator
from .video_generator import MediaVideoGenerator
from .text_generator import MediaTextGenerator
from ai_engine.content_generation.base_generator import BaseContentGenerator, ContentGenerationContext


class MediaType(Enum):
    """Media generation types"""
    AVATAR = "avatar"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"


class GenerationWorkflow(Enum):
    """Generation workflow types"""
    SINGLE = "single"          # Generate one media type
    SEQUENCE = "sequence"      # Generate multiple types in sequence
    PARALLEL = "parallel"     # Generate multiple types in parallel
    MULTI_MODAL = "multi_modal"  # Generate coordinated multi-media content


class WorkflowConfig:
    """Configuration for generation workflows"""
    
    def __init__(self, **kwargs):
        self.workflow_type = kwargs.get('workflow_type', GenerationWorkflow.SINGLE)
        self.media_types = kwargs.get('media_types', [MediaType.TEXT])
        self.coordination_enabled = kwargs.get('coordination_enabled', True)
        self.quality_check_enabled = kwargs.get('quality_check_enabled', True)
        self.batch_processing = kwargs.get('batch_processing', False)
        self.cache_enabled = kwargs.get('cache_enabled', True)
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.timeout_seconds = kwargs.get('timeout_seconds', 300)


class MediaGeneratorOrchestrator:
    """
    Main orchestrator for all media generation types.
    Provides unified interface and coordinates complex multi-media workflows.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the media generator orchestrator.
        
        Args:
            config: Configuration dictionary for all generators
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize individual generators
        self.generators = {}
        self._initialize_generators()
        
        # Workflow management
        self.active_workflows = {}
        self.generation_cache = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_generation_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.logger.info("Media Generator Orchestrator initialized successfully")

    def _initialize_generators(self) -> None:
        """Initialize all media generators"""
        try:
            # Avatar generator
            avatar_config = self.config.get('avatar', {})
            self.generators[MediaType.AVATAR] = AvatarGenerator(avatar_config)
            
            # Voice generator
            voice_config = self.config.get('voice', {})
            self.generators[MediaType.VOICE] = VoiceGenerator(voice_config)
            
            # Image generator
            image_config = self.config.get('image', {})
            self.generators[MediaType.IMAGE] = MediaImageGenerator(image_config)
            
            # Video generator
            video_config = self.config.get('video', {})
            self.generators[MediaType.VIDEO] = MediaVideoGenerator(video_config)
            
            # Text generator
            text_config = self.config.get('text', {})
            self.generators[MediaType.TEXT] = MediaTextGenerator(text_config)
            
            self.logger.info("All media generators initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize generators: {str(e)}")
            raise

    async def generate_content(
        self,
        media_type: Union[MediaType, str],
        context: ContentGenerationContext,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific media type.
        
        Args:
            media_type: Type of media to generate
            context: Generation context
            prompt: Content prompt
            options: Generation options
            
        Returns:
            Generated content with metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Convert string to enum if needed
            if isinstance(media_type, str):
                media_type = MediaType(media_type.lower())
            
            # Check cache first
            cache_key = self._generate_cache_key(media_type, prompt, options)
            if self.config.get('cache_enabled', True) and cache_key in self.generation_cache:
                self.performance_metrics['cache_hits'] += 1
                self.logger.info(f"Cache hit for {media_type.value} generation")
                return self.generation_cache[cache_key]
            
            self.performance_metrics['cache_misses'] += 1
            
            # Get appropriate generator
            generator = self.generators.get(media_type)
            if not generator:
                raise ValueError(f"No generator available for media type: {media_type.value}")
            
            # Generate content
            self.logger.info(f"Starting {media_type.value} generation")
            result = await generator.generate_content(context, prompt, options)
            
            # Add orchestrator metadata
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            result['orchestrator_metadata'] = {
                'media_type': media_type.value,
                'generation_time_seconds': generation_time,
                'generator_version': generator.__class__.__name__,
                'cache_hit': False,
                'workflow_id': None
            }
            
            # Cache result
            if self.config.get('cache_enabled', True):
                self.generation_cache[cache_key] = result
            
            # Update metrics
            self.performance_metrics['total_generations'] += 1
            self.performance_metrics['successful_generations'] += 1
            self._update_average_generation_time(generation_time)
            
            self.logger.info(f"Successfully generated {media_type.value} content in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self.performance_metrics['total_generations'] += 1
            self.performance_metrics['failed_generations'] += 1
            self.logger.error(f"Failed to generate {media_type.value} content: {str(e)}")
            raise

    async def generate_multi_modal_content(
        self,
        workflow_config: WorkflowConfig,
        context: ContentGenerationContext,
        prompts: Dict[str, str],
        options: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate coordinated multi-modal content.
        
        Args:
            workflow_config: Workflow configuration
            context: Generation context
            prompts: Dictionary of prompts for each media type
            options: Options for each media type
            
        Returns:
            Dictionary of generated content for each media type
        """
        workflow_id = f"workflow_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting multi-modal workflow {workflow_id}")
            
            # Track workflow
            self.active_workflows[workflow_id] = {
                'config': workflow_config,
                'start_time': start_time,
                'status': 'running',
                'media_types': workflow_config.media_types,
                'results': {}
            }
            
            # Generate content based on workflow type
            if workflow_config.workflow_type == GenerationWorkflow.PARALLEL:
                results = await self._generate_parallel(workflow_config, context, prompts, options)
            elif workflow_config.workflow_type == GenerationWorkflow.SEQUENCE:
                results = await self._generate_sequence(workflow_config, context, prompts, options)
            elif workflow_config.workflow_type == GenerationWorkflow.MULTI_MODAL:
                results = await self._generate_coordinated(workflow_config, context, prompts, options)
            else:
                # Single media type
                media_type = workflow_config.media_types[0]
                prompt = prompts.get(media_type.value, prompts.get('default', ''))
                media_options = options.get(media_type.value) if options else None
                
                result = await self.generate_content(media_type, context, prompt, media_options)
                results = {media_type.value: result}
            
            # Add workflow metadata
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            workflow_metadata = {
                'workflow_id': workflow_id,
                'workflow_type': workflow_config.workflow_type.value,
                'total_generation_time': generation_time,
                'media_types_generated': list(results.keys()),
                'coordination_applied': workflow_config.coordination_enabled,
                'quality_checked': workflow_config.quality_check_enabled
            }
            
            # Update workflow status
            self.active_workflows[workflow_id]['status'] = 'completed'
            self.active_workflows[workflow_id]['results'] = results
            self.active_workflows[workflow_id]['metadata'] = workflow_metadata
            
            self.logger.info(f"Completed multi-modal workflow {workflow_id} in {generation_time:.2f}s")
            
            return {
                'results': results,
                'workflow_metadata': workflow_metadata
            }
            
        except Exception as e:
            self.active_workflows[workflow_id]['status'] = 'failed'
            self.active_workflows[workflow_id]['error'] = str(e)
            self.logger.error(f"Multi-modal workflow {workflow_id} failed: {str(e)}")
            raise

    async def _generate_parallel(
        self,
        config: WorkflowConfig,
        context: ContentGenerationContext,
        prompts: Dict[str, str],
        options: Optional[Dict[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate multiple media types in parallel"""
        
        tasks = []
        media_types = []
        
        for media_type in config.media_types:
            prompt = prompts.get(media_type.value, prompts.get('default', ''))
            media_options = options.get(media_type.value) if options else None
            
            task = self.generate_content(media_type, context, prompt, media_options)
            tasks.append(task)
            media_types.append(media_type.value)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = {}
        for i, result in enumerate(results):
            media_type = media_types[i]
            if isinstance(result, Exception):
                self.logger.error(f"Parallel generation failed for {media_type}: {result}")
                final_results[media_type] = {'error': str(result)}
            else:
                final_results[media_type] = result
        
        return final_results

    async def _generate_sequence(
        self,
        config: WorkflowConfig,
        context: ContentGenerationContext,
        prompts: Dict[str, str],
        options: Optional[Dict[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate multiple media types in sequence"""
        
        results = {}
        
        for media_type in config.media_types:
            try:
                prompt = prompts.get(media_type.value, prompts.get('default', ''))
                media_options = options.get(media_type.value) if options else None
                
                # Use previous results to enhance context if coordination is enabled
                if config.coordination_enabled and results:
                    media_options = self._enhance_context_with_previous_results(
                        media_options, results, media_type
                    )
                
                result = await self.generate_content(media_type, context, prompt, media_options)
                results[media_type.value] = result
                
            except Exception as e:
                self.logger.error(f"Sequential generation failed for {media_type.value}: {e}")
                results[media_type.value] = {'error': str(e)}
        
        return results

    async def _generate_coordinated(
        self,
        config: WorkflowConfig,
        context: ContentGenerationContext,
        prompts: Dict[str, str],
        options: Optional[Dict[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate coordinated multi-modal content with cross-references"""
        
        # First, generate a content plan
        content_plan = await self._create_content_plan(config, context, prompts)
        
        # Generate content in optimal order
        generation_order = self._determine_generation_order(config.media_types)
        results = {}
        
        for media_type in generation_order:
            try:
                # Build coordinated prompt and options
                coordinated_prompt = self._build_coordinated_prompt(
                    prompts.get(media_type.value, ''), content_plan, results
                )
                
                coordinated_options = self._build_coordinated_options(
                    options.get(media_type.value) if options else {}, 
                    content_plan, 
                    results
                )
                
                result = await self.generate_content(
                    media_type, context, coordinated_prompt, coordinated_options
                )
                results[media_type.value] = result
                
            except Exception as e:
                self.logger.error(f"Coordinated generation failed for {media_type.value}: {e}")
                results[media_type.value] = {'error': str(e)}
        
        return results

    async def _create_content_plan(
        self,
        config: WorkflowConfig,
        context: ContentGenerationContext,
        prompts: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create a coordinated content plan"""
        
        # Extract common themes and elements
        all_prompts = ' '.join(prompts.values())
        
        plan = {
            'theme': self._extract_theme(all_prompts),
            'style': self._extract_style(context),
            'color_scheme': self._extract_color_scheme(context),
            'tone': self._extract_tone(all_prompts),
            'target_audience': context.target_audience if context.target_audience else 'general',
            'brand_elements': context.brand_guidelines if context.brand_guidelines else {},
            'cross_references': self._plan_cross_references(config.media_types)
        }
        
        return plan

    def _determine_generation_order(self, media_types: List[MediaType]) -> List[MediaType]:
        """Determine optimal generation order for coordination"""
        
        # Preferred order for coordination (text first, then visual, then audio/video)
        priority_order = [
            MediaType.TEXT,
            MediaType.IMAGE,
            MediaType.AVATAR,
            MediaType.VOICE,
            MediaType.VIDEO
        ]
        
        # Sort media types by priority
        ordered_types = []
        for priority_type in priority_order:
            if priority_type in media_types:
                ordered_types.append(priority_type)
        
        # Add any remaining types
        for media_type in media_types:
            if media_type not in ordered_types:
                ordered_types.append(media_type)
        
        return ordered_types

    def _build_coordinated_prompt(
        self,
        base_prompt: str,
        content_plan: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> str:
        """Build coordinated prompt using content plan and previous results"""
        
        coordinated_prompt = base_prompt
        
        # Add theme consistency
        if content_plan.get('theme'):
            coordinated_prompt += f" Theme: {content_plan['theme']}."
        
        # Add style consistency
        if content_plan.get('style'):
            coordinated_prompt += f" Style: {content_plan['style']}."
        
        # Add cross-references to previous results
        if previous_results:
            coordinated_prompt += " Ensure consistency with previously generated content."
        
        return coordinated_prompt

    def _build_coordinated_options(
        self,
        base_options: Dict[str, Any],
        content_plan: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build coordinated options using content plan and previous results"""
        
        coordinated_options = base_options.copy()
        
        # Apply color scheme consistency
        if content_plan.get('color_scheme'):
            coordinated_options['color_scheme'] = content_plan['color_scheme']
        
        # Apply tone consistency
        if content_plan.get('tone'):
            coordinated_options['tone'] = content_plan['tone']
        
        # Apply style consistency
        if content_plan.get('style'):
            coordinated_options['style'] = content_plan['style']
        
        return coordinated_options

    def _enhance_context_with_previous_results(
        self,
        options: Optional[Dict[str, Any]],
        previous_results: Dict[str, Any],
        current_media_type: MediaType
    ) -> Dict[str, Any]:
        """Enhance generation options with information from previous results"""
        
        if options is None:
            options = {}
        
        enhanced_options = options.copy()
        
        # Extract relevant information from previous results
        for media_type, result in previous_results.items():
            if isinstance(result, dict) and 'configuration' in result:
                config = result['configuration']
                
                # Apply consistent styling
                if 'color_scheme' in config:
                    enhanced_options['color_scheme'] = config['color_scheme']
                
                if 'mood' in config:
                    enhanced_options['mood'] = config['mood']
                
                if 'style' in config:
                    enhanced_options['style'] = config['style']
        
        return enhanced_options

    def _extract_theme(self, text: str) -> str:
        """Extract main theme from text"""
        # Simple theme extraction (in production would use NLP)
        text_lower = text.lower()
        
        themes = {
            'business': ['business', 'professional', 'corporate', 'company'],
            'creative': ['creative', 'artistic', 'design', 'imagination'],
            'educational': ['learn', 'teach', 'education', 'tutorial'],
            'lifestyle': ['lifestyle', 'life', 'personal', 'daily'],
            'technology': ['tech', 'technology', 'digital', 'innovation']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return 'general'

    def _extract_style(self, context: ContentGenerationContext) -> str:
        """Extract style from context"""
        if context.brand_guidelines:
            return context.brand_guidelines.get('style', 'modern')
        return 'modern'

    def _extract_color_scheme(self, context: ContentGenerationContext) -> str:
        """Extract color scheme from context"""
        if context.brand_guidelines:
            return context.brand_guidelines.get('color_scheme', 'vibrant')
        return 'vibrant'

    def _extract_tone(self, text: str) -> str:
        """Extract tone from text"""
        # Simple tone extraction
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['exciting', 'amazing', 'awesome']):
            return 'enthusiastic'
        elif any(word in text_lower for word in ['professional', 'business', 'corporate']):
            return 'professional'
        elif any(word in text_lower for word in ['fun', 'funny', 'humor']):
            return 'humorous'
        else:
            return 'friendly'

    def _plan_cross_references(self, media_types: List[MediaType]) -> Dict[str, List[str]]:
        """Plan cross-references between media types"""
        cross_refs = {}
        
        for media_type in media_types:
            cross_refs[media_type.value] = []
            
            # Define which media types should reference each other
            if media_type == MediaType.VIDEO and MediaType.VOICE in media_types:
                cross_refs[media_type.value].append(MediaType.VOICE.value)
            
            if media_type == MediaType.IMAGE and MediaType.TEXT in media_types:
                cross_refs[media_type.value].append(MediaType.TEXT.value)
            
            if media_type == MediaType.AVATAR and MediaType.IMAGE in media_types:
                cross_refs[media_type.value].append(MediaType.IMAGE.value)
        
        return cross_refs

    def _generate_cache_key(
        self,
        media_type: MediaType,
        prompt: str,
        options: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for content"""
        import hashlib
        
        key_data = f"{media_type.value}:{prompt}:{str(options)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _update_average_generation_time(self, generation_time: float) -> None:
        """Update average generation time metric"""
        total_gens = self.performance_metrics['successful_generations']
        current_avg = self.performance_metrics['average_generation_time']
        
        # Calculate new average
        new_avg = ((current_avg * (total_gens - 1)) + generation_time) / total_gens
        self.performance_metrics['average_generation_time'] = new_avg

    # Utility and management methods

    def get_supported_media_types(self) -> List[str]:
        """Get list of supported media types"""
        return [media_type.value for media_type in MediaType]

    def get_generator_capabilities(self, media_type: Union[MediaType, str]) -> Dict[str, Any]:
        """Get capabilities of a specific generator"""
        if isinstance(media_type, str):
            media_type = MediaType(media_type.lower())
        
        generator = self.generators.get(media_type)
        if not generator:
            return {}
        
        capabilities = {
            'media_type': media_type.value,
            'generator_class': generator.__class__.__name__,
            'supported_formats': getattr(generator, 'supported_formats', []),
            'max_concurrent': getattr(generator, 'max_concurrent_generations', 1)
        }
        
        # Add type-specific capabilities
        if media_type == MediaType.AVATAR:
            capabilities['avatar_types'] = generator.get_supported_avatar_types()
        elif media_type == MediaType.VOICE:
            capabilities['voice_types'] = generator.get_supported_voice_types()
            capabilities['languages'] = generator.get_supported_languages()
        elif media_type == MediaType.IMAGE:
            capabilities['image_types'] = generator.get_supported_image_types()
        elif media_type == MediaType.VIDEO:
            capabilities['video_types'] = generator.get_supported_video_types()
        elif media_type == MediaType.TEXT:
            capabilities['text_types'] = generator.get_supported_text_types()
            capabilities['writing_styles'] = generator.get_writing_styles()
        
        return capabilities

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()

    def get_active_workflows(self) -> Dict[str, Any]:
        """Get information about active workflows"""
        return {
            workflow_id: {
                'status': workflow['status'],
                'start_time': workflow['start_time'].isoformat(),
                'media_types': [mt.value for mt in workflow['media_types']],
                'results_count': len(workflow.get('results', {}))
            }
            for workflow_id, workflow in self.active_workflows.items()
        }

    def clear_cache(self) -> None:
        """Clear generation cache"""
        self.generation_cache.clear()
        self.logger.info("Generation cache cleared")

    async def validate_all_generators(self) -> Dict[str, bool]:
        """Validate all generators are working"""
        validation_results = {}
        
        for media_type, generator in self.generators.items():
            try:
                # Perform basic validation test
                test_context = ContentGenerationContext()
                test_result = await generator.generate_content(
                    test_context, 
                    "test content", 
                    {'test': True}
                )
                
                is_valid = await generator.validate_output(test_result)
                validation_results[media_type.value] = is_valid
                
            except Exception as e:
                self.logger.error(f"Validation failed for {media_type.value}: {e}")
                validation_results[media_type.value] = False
        
        return validation_results

    async def cleanup_resources(self) -> None:
        """Clean up all generator resources"""
        for generator in self.generators.values():
            try:
                await generator.cleanup_resources()
            except Exception as e:
                self.logger.error(f"Failed to cleanup generator: {e}")
        
        self.generation_cache.clear()
        self.active_workflows.clear()
        self.logger.info("All resources cleaned up")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        asyncio.create_task(self.cleanup_resources())