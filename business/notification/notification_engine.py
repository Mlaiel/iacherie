"""
Notification Engine - Advanced Multi-Channel Notification Processing Engine

Core processing engine for IA Influencer Agent notification system.
Handles intelligent routing, AI-powered optimization, template processing,
channel management, workflow orchestration, and comprehensive analytics.

Key Features:
- AI-powered priority classification and urgency detection
- Intelligent channel selection and delivery optimization
- Advanced template processing with personalization
- Multi-step workflow orchestration and automation
- Real-time analytics and performance monitoring
- Comprehensive failover and redundancy mechanisms

Processing Pipeline:
1. Request Validation → Priority Classification → Template Processing
2. Channel Selection → Personalization → Delivery Optimization
3. Multi-Channel Dispatch → Delivery Tracking → Analytics Collection
4. Workflow Orchestration → Business Logic Integration → Performance Monitoring

Architecture Components:
- ChannelManager: Multi-channel delivery optimization
- TemplateProcessor: AI-powered template personalization
- PriorityClassifier: Intelligent priority and urgency detection
- PersonalizationEngine: Advanced content personalization
- WorkflowOrchestrator: Complex workflow automation
- AnalyticsEngine: Real-time performance monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json

from .channel_manager import ChannelManager
from .template_processor import TemplateProcessor
from .priority_classifier import PriorityClassifier
from .personalization_engine import PersonalizationEngine
from .workflow_orchestrator import WorkflowOrchestrator
from .analytics_engine import AnalyticsEngine
from .notification_models import (
    NotificationRequest,
    NotificationResponse,
    NotificationTemplate,
    DeliveryStatus,
    ProcessingStage
)
from .config import NotificationConfig
from .constants import PRIORITY_LEVELS, CHANNEL_TYPES, PROCESSING_STAGES

logger = logging.getLogger(__name__)


class NotificationEngineError(Exception):
    """Custom exception for notification engine errors."""
    pass


class ProcessingResult:
    """Result container for notification processing stages."""
    
    def __init__(
        self,
        stage: ProcessingStage,
        success: bool,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        processing_time: float = 0.0
    ):
        self.stage = stage
        self.success = success
        self.data = data
        self.error = error
        self.processing_time = processing_time
        self.timestamp = datetime.now(timezone.utc)


class NotificationEngine:
    """
    Advanced notification processing engine with AI-powered optimization.
    
    Provides comprehensive notification processing including intelligent routing,
    template personalization, workflow orchestration, and analytics collection.
    """
    
    def __init__(
        self,
        channel_manager: ChannelManager,
        template_processor: TemplateProcessor,
        priority_classifier: Optional[PriorityClassifier] = None,
        personalization_engine: Optional[PersonalizationEngine] = None,
        workflow_orchestrator: Optional[WorkflowOrchestrator] = None,
        analytics_engine: Optional[AnalyticsEngine] = None,
        config: Optional[NotificationConfig] = None
    ):
        """
        Initialize notification engine with processing components.
        
        Args:
            channel_manager: Multi-channel delivery management
            template_processor: Template processing and optimization
            priority_classifier: AI-powered priority classification
            personalization_engine: Content personalization engine
            workflow_orchestrator: Workflow automation and orchestration
            analytics_engine: Performance monitoring and analytics
            config: Engine configuration
        """
        self.channel_manager = channel_manager
        self.template_processor = template_processor
        self.priority_classifier = priority_classifier
        self.personalization_engine = personalization_engine
        self.workflow_orchestrator = workflow_orchestrator
        self.analytics_engine = analytics_engine
        self.config = config or NotificationConfig()
        
        # Engine state
        self._processing_queue: List[NotificationRequest] = []
        self._active_deliveries: Dict[str, Dict[str, Any]] = {}
        self._processing_metrics = {
            "total_processed": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "average_processing_time": 0.0,
            "stage_performance": {stage.value: 0.0 for stage in ProcessingStage}
        }
        
        # Performance optimization
        self._template_cache: Dict[str, NotificationTemplate] = {}
        self._channel_performance_cache: Dict[str, Dict[str, float]] = {}
        
        logger.info("NotificationEngine initialized with advanced processing components")
    
    async def process_notification(
        self,
        request: NotificationRequest,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> NotificationResponse:
        """
        Process notification through complete pipeline with AI optimization.
        
        Args:
            request: Notification request to process
            processing_options: Optional processing configuration
        
        Returns:
            Notification response with delivery status and metadata
        
        Raises:
            NotificationEngineError: If processing fails
        """



        try:
            start_time = datetime.now(timezone.utc)
            processing_results = []
            
            logger.info(f"Starting notification processing: {request.notification_id}")
            
            # Stage 1: Request Validation and Preparation
            validation_result = await self._validate_and_prepare_request(request)
            processing_results.append(validation_result)
            
            if not validation_result.success:
                raise NotificationEngineError(f"Request validation failed: {validation_result.error}")
            
            # Stage 2: Priority Classification
            if self.priority_classifier:
                priority_result = await self._classify_priority(request)
                processing_results.append(priority_result)
                
                if priority_result.success and priority_result.data:
                    request.priority = priority_result.data.get("priority", request.priority)
                    request.urgency_score = priority_result.data.get("urgency_score", 0.0)
            
            # Stage 3: Template Processing and Optimization
            template_result = await self._process_template(request)
            processing_results.append(template_result)
            
            if not template_result.success:
                raise NotificationEngineError(f"Template processing failed: {template_result.error}")
            
            processed_template = template_result.data
            
            # Stage 4: Content Personalization
            if self.personalization_engine:
                personalization_result = await self._personalize_content(request, processed_template)
                processing_results.append(personalization_result)
                
                if personalization_result.success and personalization_result.data:
                    processed_template = personalization_result.data
            
            # Stage 5: Channel Selection and Optimization
            channel_result = await self._select_and_optimize_channels(request)
            processing_results.append(channel_result)
            
            if not channel_result.success:
                raise NotificationEngineError(f"Channel selection failed: {channel_result.error}")
            
            optimized_channels = channel_result.data
            
            # Stage 6: Multi-Channel Delivery
            delivery_result = await self._execute_delivery(
                request, processed_template, optimized_channels
            )
            processing_results.append(delivery_result)
            
            # Stage 7: Analytics Collection
            if self.analytics_engine:
                analytics_result = await self._collect_analytics(request, processing_results)
                processing_results.append(analytics_result)
            
            # Calculate total processing time
            total_processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create response
            response = self._create_response(
                request, delivery_result, processing_results, total_processing_time
            )
            
            # Update metrics
            await self._update_processing_metrics(processing_results, total_processing_time)
            
            logger.info(
                f"Notification processing completed: {request.notification_id} "
                f"in {total_processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Notification processing failed for {request.notification_id}: {e}")
            self._processing_metrics["failed_deliveries"] += 1
            
            # Create error response
            return NotificationResponse(
                notification_id=request.notification_id,
                status=DeliveryStatus.FAILED,
                message=f"Processing failed: {str(e)}",
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "error": str(e),
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
            )
    
    async def process_batch_notifications(
        self,
        requests: List[NotificationRequest],
        batch_options: Optional[Dict[str, Any]] = None
    ) -> List[NotificationResponse]:
        """
        Process multiple notifications with intelligent batching and optimization.
        
        Args:
            requests: List of notification requests
            batch_options: Optional batch processing configuration
        
        Returns:
            List of notification responses
        """



        try:
            batch_size = batch_options.get("batch_size", 50) if batch_options else 50
            concurrent_limit = batch_options.get("concurrent_limit", 10) if batch_options else 10
            
            responses = []
            
            # Process in optimized batches
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i + batch_size]
                
                # Create semaphore for concurrency control
                semaphore = asyncio.Semaphore(concurrent_limit)
                
                async def process_with_semaphore(request):
                    async with semaphore:
                        return await self.process_notification(request)
                
                # Process batch concurrently
                batch_tasks = [process_with_semaphore(req) for req in batch]
                batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Handle exceptions and collect responses
                for response in batch_responses:
                    if isinstance(response, Exception):
                        logger.error(f"Batch processing error: {response}")
                        responses.append(NotificationResponse(
                            notification_id="batch_error",
                            status=DeliveryStatus.FAILED,
                            message=str(response),
                            timestamp=datetime.now(timezone.utc)
                        ))
                    else:
                        responses.append(response)
            
            logger.info(f"Batch processing completed: {len(responses)} notifications")
            return responses
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise NotificationEngineError(f"Batch processing error: {e}")
    
    async def get_processing_queue_status(self) -> Dict[str, Any]:
        """
        Get current processing queue status and metrics.
        
        Returns:
            Queue status information
        """



        try:
            return {
                "queue_length": len(self._processing_queue),
                "active_deliveries": len(self._active_deliveries),
                "processing_metrics": self._processing_metrics.copy(),
                "engine_health": await self._get_engine_health(),
                "component_status": {
                    "channel_manager": "active" if self.channel_manager else "disabled",
                    "template_processor": "active" if self.template_processor else "disabled",
                    "priority_classifier": "active" if self.priority_classifier else "disabled",
                    "personalization_engine": "active" if self.personalization_engine else "disabled",
                    "workflow_orchestrator": "active" if self.workflow_orchestrator else "disabled",
                    "analytics_engine": "active" if self.analytics_engine else "disabled"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {"error": str(e)}
    
    async def optimize_performance(self, optimization_config: Dict[str, Any]) -> bool:
        """
        Optimize engine performance based on analytics and configuration.
        
        Args:
            optimization_config: Performance optimization parameters
        
        Returns:
            True if optimization successful, False otherwise
        """



        try:
            # Optimize channel performance
            if "channel_optimization" in optimization_config:
                await self.channel_manager.optimize_channels(
                    optimization_config["channel_optimization"]
                )
            
            # Optimize template processing
            if "template_optimization" in optimization_config:
                await self.template_processor.optimize_processing(
                    optimization_config["template_optimization"]
                )
            
            # Update cache strategies
            if "cache_optimization" in optimization_config:
                self._optimize_caching(optimization_config["cache_optimization"])
            
            # Optimize concurrent processing
            if "concurrency_optimization" in optimization_config:
                self._optimize_concurrency(optimization_config["concurrency_optimization"])
            
            logger.info("Engine performance optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return False
    
    # Private processing methods
    
    async def _validate_and_prepare_request(
        self, request: NotificationRequest
    ) -> ProcessingResult:
        """Validate and prepare notification request."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Basic validation
            if not request.notification_id:
                request.notification_id = f"notif_{int(datetime.now().timestamp())}"
            
            if not request.recipient:
                return ProcessingResult(
                    ProcessingStage.VALIDATION,
                    False,
                    error="Missing recipient"
                )
            
            if not request.content:
                return ProcessingResult(
                    ProcessingStage.VALIDATION,
                    False,
                    error="Missing content"
                )
            
            # Prepare metadata
            if not request.metadata:
                request.metadata = {}
            
            request.metadata["engine_version"] = "2.0.0"
            request.metadata["processing_start"] = start_time.isoformat()
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.VALIDATION,
                True,
                data={"validated": True},
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.VALIDATION,
                False,
                error=str(e)
            )
    
    async def _classify_priority(
        self, request: NotificationRequest
    ) -> ProcessingResult:
        """Classify notification priority using AI."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Get priority classification
            classification = await self.priority_classifier.classify_priority(request)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.PRIORITY_CLASSIFICATION,
                True,
                data=classification,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.PRIORITY_CLASSIFICATION,
                False,
                error=str(e)
            )
    
    async def _process_template(
        self, request: NotificationRequest
    ) -> ProcessingResult:
        """Process and optimize notification template."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Check template cache
            cache_key = f"{request.notification_type}_{request.priority}"
            if cache_key in self._template_cache:
                template = self._template_cache[cache_key]
            else:
                # Process template
                template = await self.template_processor.process_template(request)
                self._template_cache[cache_key] = template
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.TEMPLATE_PROCESSING,
                True,
                data=template,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.TEMPLATE_PROCESSING,
                False,
                error=str(e)
            )
    
    async def _personalize_content(
        self, request: NotificationRequest, template: NotificationTemplate
    ) -> ProcessingResult:
        """Personalize notification content."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Personalize content
            personalized_template = await self.personalization_engine.personalize_template(
                request, template
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.PERSONALIZATION,
                True,
                data=personalized_template,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.PERSONALIZATION,
                False,
                error=str(e)
            )
    
    async def _select_and_optimize_channels(
        self, request: NotificationRequest
    ) -> ProcessingResult:
        """Select and optimize delivery channels."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Select optimal channels
            channels = await self.channel_manager.select_optimal_channels(request)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.CHANNEL_SELECTION,
                True,
                data=channels,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.CHANNEL_SELECTION,
                False,
                error=str(e)
            )
    
    async def _execute_delivery(
        self,
        request: NotificationRequest,
        template: NotificationTemplate,
        channels: List[str]
    ) -> ProcessingResult:
        """Execute multi-channel delivery."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Track active delivery
            self._active_deliveries[request.notification_id] = {
                "start_time": start_time,
                "channels": channels,
                "status": "delivering"
            }
            
            # Execute delivery
            delivery_results = await self.channel_manager.deliver_notification(
                request, template, channels
            )
            
            # Update delivery status
            self._active_deliveries[request.notification_id]["status"] = "completed"
            self._active_deliveries[request.notification_id]["results"] = delivery_results
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Determine overall delivery status
            successful_deliveries = sum(1 for result in delivery_results if result.get("success", False))
            overall_success = successful_deliveries > 0
            
            return ProcessingResult(
                ProcessingStage.DELIVERY,
                overall_success,
                data=delivery_results,
                processing_time=processing_time
            )
            
        except Exception as e:
            # Update delivery status on error
            if request.notification_id in self._active_deliveries:
                self._active_deliveries[request.notification_id]["status"] = "failed"
                self._active_deliveries[request.notification_id]["error"] = str(e)
            
            return ProcessingResult(
                ProcessingStage.DELIVERY,
                False,
                error=str(e)
            )
    
    async def _collect_analytics(
        self, request: NotificationRequest, processing_results: List[ProcessingResult]
    ) -> ProcessingResult:
        """Collect and record analytics data."""



        try:
            start_time = datetime.now(timezone.utc)
            
            # Prepare analytics data
            analytics_data = {
                "notification_id": request.notification_id,
                "notification_type": request.notification_type,
                "priority": request.priority,
                "processing_stages": [
                    {
                        "stage": result.stage.value,
                        "success": result.success,
                        "processing_time": result.processing_time,
                        "error": result.error
                    }
                    for result in processing_results
                ],
                "total_processing_time": sum(r.processing_time for r in processing_results),
                "timestamp": start_time.isoformat()
            }
            
            # Record analytics
            await self.analytics_engine.record_notification_analytics(analytics_data)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                ProcessingStage.ANALYTICS,
                True,
                data=analytics_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                ProcessingStage.ANALYTICS,
                False,
                error=str(e)
            )
    
    def _create_response(
        self,
        request: NotificationRequest,
        delivery_result: ProcessingResult,
        processing_results: List[ProcessingResult],
        total_processing_time: float
    ) -> NotificationResponse:
        """Create notification response from processing results."""



        try:
            # Determine overall status
            if delivery_result.success:
                if all(result.success for result in processing_results):
                    status = DeliveryStatus.DELIVERED
                else:
                    status = DeliveryStatus.PARTIALLY_DELIVERED
            else:
                status = DeliveryStatus.FAILED
            
            # Create response metadata
            metadata = {
                "processing_time": total_processing_time,
                "stages_completed": len([r for r in processing_results if r.success]),
                "total_stages": len(processing_results),
                "delivery_channels": delivery_result.data if delivery_result.data else [],
                "engine_version": "2.0.0"
            }
            
            # Add error information if any stage failed
            failed_stages = [r for r in processing_results if not r.success]
            if failed_stages:
                metadata["failed_stages"] = [
                    {"stage": r.stage.value, "error": r.error} for r in failed_stages
                ]
            
            return NotificationResponse(
                notification_id=request.notification_id,
                status=status,
                message=f"Notification processed in {total_processing_time:.3f}s",
                timestamp=datetime.now(timezone.utc),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to create response: {e}")
            return NotificationResponse(
                notification_id=request.notification_id,
                status=DeliveryStatus.FAILED,
                message=f"Response creation failed: {str(e)}",
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _update_processing_metrics(
        self, processing_results: List[ProcessingResult], total_processing_time: float
    ):
        """Update processing metrics."""



        try:
            # Update counters
            self._processing_metrics["total_processed"] += 1
            
            # Update success/failure counts
            overall_success = all(result.success for result in processing_results)
            if overall_success:
                self._processing_metrics["successful_deliveries"] += 1
            else:
                self._processing_metrics["failed_deliveries"] += 1
            
            # Update average processing time
            total = self._processing_metrics["total_processed"]
            current_avg = self._processing_metrics["average_processing_time"]
            self._processing_metrics["average_processing_time"] = (
                (current_avg * (total - 1) + total_processing_time) / total
            )
            
            # Update stage performance metrics
            for result in processing_results:
                stage_key = result.stage.value
                if stage_key in self._processing_metrics["stage_performance"]:
                    current_stage_avg = self._processing_metrics["stage_performance"][stage_key]
                    self._processing_metrics["stage_performance"][stage_key] = (
                        (current_stage_avg * (total - 1) + result.processing_time) / total
                    )
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    async def _get_engine_health(self) -> Dict[str, Any]:
        """Get comprehensive engine health status."""



        try:
            total_processed = self._processing_metrics["total_processed"]
            successful = self._processing_metrics["successful_deliveries"]
            
            success_rate = (successful / total_processed * 100) if total_processed > 0 else 100.0
            
            return {
                "status": "healthy" if success_rate >= 95 else "warning" if success_rate >= 90 else "critical",
                "success_rate": success_rate,
                "average_processing_time": self._processing_metrics["average_processing_time"],
                "queue_length": len(self._processing_queue),
                "active_deliveries": len(self._active_deliveries),
                "cache_hit_rate": len(self._template_cache) / max(total_processed, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _optimize_caching(self, cache_config: Dict[str, Any]):
        """Optimize caching strategies."""



        try:
            # Template cache optimization
            max_template_cache = cache_config.get("template_cache_size", 1000)
            if len(self._template_cache) > max_template_cache:
                # Remove oldest entries
                cache_items = list(self._template_cache.items())
                self._template_cache = dict(cache_items[-max_template_cache:])
            
            logger.info("Cache optimization completed")
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
    
    def _optimize_concurrency(self, concurrency_config: Dict[str, Any]):
        """Optimize concurrent processing."""



        try:
            # Update processing limits based on performance
            max_concurrent = concurrency_config.get("max_concurrent_deliveries", 50)
            batch_size = concurrency_config.get("optimal_batch_size", 25)
            
            # Store optimization parameters for future use
            self.config.processing_config = {
                "max_concurrent_deliveries": max_concurrent,
                "optimal_batch_size": batch_size
            }
            
            logger.info("Concurrency optimization completed")
            
        except Exception as e:
            logger.error(f"Concurrency optimization failed: {e}")
