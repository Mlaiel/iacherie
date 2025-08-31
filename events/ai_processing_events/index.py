"""AI Processing Events Module Index

Main entry point for the AI Processing Events module providing easy access
to all event handlers and processing pipelines.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.

Copyright © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import all handlers and components
from . import (
    AIProcessingEventType,
    AIProcessingEventData,
    AIProcessingEvent,
    EventPriority,
    EventStatus,
    ContentAnalysisHandler,
    AIEnhancementHandler,
    ContentProtectionHandler,
    SEOOptimizationHandler,
    CollaborationMatchingHandler,
    DistributionPreparationHandler,
    EventProcessingPipeline,
    create_event_processing_pipeline,
    get_handler_class,
    HANDLER_REGISTRY
)

logger = logging.getLogger(__name__)

class AIProcessingEventsManager:
    """    Central manager for AI Processing Events
    
    Provides unified interface for managing all event processing operations
    including handler initialization, pipeline execution, and system monitoring.
    """    
    def __init__(self, ai_engine: Any):
        """Initialize the events manager with AI engine"""        self.ai_engine = ai_engine
        self.handlers = {}
        self.pipeline = None
        self.active_events = {}
        self.processing_stats = {
            'total_events_processed': 0,
            'successful_events': 0,
            'failed_events': 0,
            'average_processing_time': 0.0
        }
        
        # Initialize all handlers
        self._initialize_handlers()
        
        # Initialize processing pipeline
        self._initialize_pipeline()
        
        logger.info("AI Processing Events Manager initialized successfully")
    
    def _initialize_handlers(self):
        """Initialize all event handlers"""        try:
            self.handlers = {
                'content_analysis': ContentAnalysisHandler(self.ai_engine),
                'ai_enhancement': AIEnhancementHandler(self.ai_engine),
                'content_protection': ContentProtectionHandler(self.ai_engine),
                'seo_optimization': SEOOptimizationHandler(self.ai_engine),
                'collaboration_matching': CollaborationMatchingHandler(self.ai_engine),
                'distribution_preparation': DistributionPreparationHandler(self.ai_engine)
            }
            logger.info(f"Initialized {len(self.handlers)} event handlers")
            
        except Exception as e:
            logger.error(f"Failed to initialize handlers: {e}")
            raise
    
    def _initialize_pipeline(self):
        """Initialize the processing pipeline"""        try:
            self.pipeline = create_event_processing_pipeline(self.ai_engine)
            if self.pipeline:
                logger.info("Processing pipeline initialized successfully")
            else:
                logger.warning("Pipeline initialization returned None")
                
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            # Create manual pipeline as fallback
            self.pipeline = EventProcessingPipeline(self.ai_engine)
    
    async def process_content(self, content_data: Dict[str, Any], 
                            processing_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """        Process content through the complete AI processing pipeline
        
        Args:
            content_data: Content information and metadata
            processing_options: Optional processing configuration
            
        Returns:
            Dict containing processing results and metrics
        """        start_time = datetime.now()
        event_id = f"event_{start_time.timestamp()}"
        
        try:
            logger.info(f"Starting content processing for event {event_id}")
            
            # Create processing configuration
            config = self._create_processing_config(content_data, processing_options)
            
            # Track active event
            self.active_events[event_id] = {
                'start_time': start_time,
                'content_id': content_data.get('content_id'),
                'status': 'processing'
            }
            
            # Execute pipeline
            if self.pipeline:
                result = await self.pipeline.execute_pipeline(config)
                
                # Update processing statistics
                processing_time = (datetime.now() - start_time).total_seconds()
                self._update_processing_stats(True, processing_time)
                
                # Clean up active event
                self.active_events[event_id]['status'] = 'completed'
                self.active_events[event_id]['end_time'] = datetime.now()
                
                logger.info(f"Content processing completed for event {event_id} in {processing_time:.2f}s")
                
                return {
                    'event_id': event_id,
                    'success': True,
                    'processing_time': processing_time,
                    'pipeline_result': result,
                    'business_metrics': self._extract_business_metrics(result)
                }
            else:
                raise Exception("Pipeline not available")
                
        except Exception as e:
            logger.error(f"Content processing failed for event {event_id}: {e}")
            
            # Update failure statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_processing_stats(False, processing_time)
            
            # Mark event as failed
            if event_id in self.active_events:
                self.active_events[event_id]['status'] = 'failed'
                self.active_events[event_id]['error'] = str(e)
            
            return {
                'event_id': event_id,
                'success': False,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def _create_processing_config(self, content_data: Dict[str, Any], 
                                processing_options: Optional[Dict[str, Any]] = None) -> Any:
        """Create processing configuration from content data and options"""        from .event_processing_pipeline import PipelineConfiguration, PipelineStage
        
        options = processing_options or {}
        
        return PipelineConfiguration(
            pipeline_id=f"pipeline_{datetime.now().timestamp()}",
            content_id=content_data.get('content_id', 'unknown'),
            content_type=content_data.get('content_type', 'unknown'),
            creator_id=content_data.get('creator_id', 'unknown'),
            processing_priority=EventPriority.MEDIUM,
            target_quality=options.get('target_quality', 0.8),
            enable_parallel_processing=options.get('enable_parallel', True),
            max_retry_attempts=options.get('max_retries', 3),
            timeout_seconds=options.get('timeout', 300),
            skip_stages=options.get('skip_stages', []),
            stage_configurations=options.get('stage_configs', {})
        )
    
    def _update_processing_stats(self, success: bool, processing_time: float):
        """Update processing statistics"""        self.processing_stats['total_events_processed'] += 1
        
        if success:
            self.processing_stats['successful_events'] += 1
        else:
            self.processing_stats['failed_events'] += 1
        
        # Update average processing time
        total_events = self.processing_stats['total_events_processed']
        current_avg = self.processing_stats['average_processing_time']
        new_avg = ((current_avg * (total_events - 1)) + processing_time) / total_events
        self.processing_stats['average_processing_time'] = new_avg
    
    def _extract_business_metrics(self, pipeline_result: Any) -> Dict[str, Any]:
        """Extract business-relevant metrics from pipeline result"""        if not pipeline_result or not hasattr(pipeline_result, 'final_quality_score'):
            return {}
        
        return {
            'quality_improvement': pipeline_result.final_quality_score,
            'processing_efficiency': pipeline_result.calculate_success_rate(),
            'business_roi': pipeline_result.get_business_roi(),
            'content_optimization_score': pipeline_result.pipeline_metrics.content_optimization_score,
            'estimated_performance_boost': pipeline_result.final_quality_score * 100
        }
    
    async def analyze_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content using ContentAnalysisHandler"""        handler = self.handlers.get('content_analysis')
        if handler:
            return await handler.handle_event({'content_data': content_data})
        raise ValueError("Content analysis handler not available")
    
    async def enhance_content(self, content_data: Dict[str, Any], 
                            enhancement_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhance content using AIEnhancementHandler"""        handler = self.handlers.get('ai_enhancement')
        if handler:
            event_data = {'content_data': content_data}
            if enhancement_options:
                event_data.update(enhancement_options)
            return await handler.handle_event(event_data)
        raise ValueError("AI enhancement handler not available")
    
    async def protect_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Protect content using ContentProtectionHandler"""        handler = self.handlers.get('content_protection')
        if handler:
            return await handler.handle_event({'content_data': content_data})
        raise ValueError("Content protection handler not available")
    
    async def optimize_seo(self, content_data: Dict[str, Any], 
                          target_platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Optimize content for SEO using SEOOptimizationHandler"""        handler = self.handlers.get('seo_optimization')
        if handler:
            event_data = {
                'content_data': content_data,
                'target_platforms': target_platforms or ['youtube', 'spotify']
            }
            return await handler.handle_event(event_data)
        raise ValueError("SEO optimization handler not available")
    
    async def find_collaborations(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find collaboration opportunities using CollaborationMatchingHandler"""        handler = self.handlers.get('collaboration_matching')
        if handler:
            return await handler.handle_event({'creator_data': creator_data})
        raise ValueError("Collaboration matching handler not available")
    
    async def prepare_distribution(self, content_data: Dict[str, Any], 
                                 target_platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Prepare content for distribution using DistributionPreparationHandler"""        handler = self.handlers.get('distribution_preparation')
        if handler:
            event_data = {
                'content_data': content_data,
                'target_platforms': target_platforms or ['spotify', 'youtube']
            }
            return await handler.handle_event(event_data)
        raise ValueError("Distribution preparation handler not available")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""        return {
            'handlers_status': {name: 'active' for name in self.handlers.keys()},
            'pipeline_status': 'active' if self.pipeline else 'inactive',
            'active_events': len(self.active_events),
            'processing_stats': self.processing_stats.copy(),
            'uptime': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    def get_handler_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics from all handlers"""        stats = {}
        
        for name, handler in self.handlers.items():
            if hasattr(handler, 'get_statistics'):
                stats[name] = handler.get_statistics()
            elif hasattr(handler, 'get_processing_statistics'):
                stats[name] = handler.get_processing_statistics()
            elif hasattr(handler, 'get_optimization_statistics'):
                stats[name] = handler.get_optimization_statistics()
            elif hasattr(handler, 'get_matching_statistics'):
                stats[name] = handler.get_matching_statistics()
            elif hasattr(handler, 'get_distribution_statistics'):
                stats[name] = handler.get_distribution_statistics()
            else:
                stats[name] = {'status': 'active', 'statistics': 'not_available'}
        
        return stats
    
    async def cleanup(self):
        """Cleanup all handlers and resources"""        logger.info("Starting cleanup of AI Processing Events Manager")
        
        # Cleanup all handlers
        for name, handler in self.handlers.items():
            try:
                if hasattr(handler, 'cleanup'):
                    await handler.cleanup()
                logger.info(f"Cleaned up {name} handler")
            except Exception as e:
                logger.error(f"Failed to cleanup {name} handler: {e}")
        
        # Cleanup pipeline
        if self.pipeline and hasattr(self.pipeline, 'cleanup'):
            try:
                await self.pipeline.cleanup()
                logger.info("Cleaned up processing pipeline")
            except Exception as e:
                logger.error(f"Failed to cleanup pipeline: {e}")
        
        # Clear tracking data
        self.active_events.clear()
        self.handlers.clear()
        
        logger.info("AI Processing Events Manager cleanup completed")

# Factory function for easy initialization
def create_ai_processing_manager(ai_engine: Any) -> AIProcessingEventsManager:
    """    Factory function to create AI Processing Events Manager
    
    Args:
        ai_engine: AI engine instance for processing
        
    Returns:
        AIProcessingEventsManager: Configured manager instance
    """    return AIProcessingEventsManager(ai_engine)

# Export main classes and functions
__all__ = [
    'AIProcessingEventsManager',
    'create_ai_processing_manager',
    'AIProcessingEventType',
    'AIProcessingEventData',
    'AIProcessingEvent',
    'EventPriority',
    'EventStatus'
]
