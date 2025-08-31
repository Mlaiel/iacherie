"""Extraction Coordinator - Industrial IA Extraction Management System
===================================================================

Ultra-advanced professional extraction coordinator for managing multiple extraction types and workflows.
Implements enterprise-grade routing, optimization, and coordination capabilities with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq
from pathlib import Path

# Import core extraction components
from .extraction_engine import (
    BaseExtractor, ExtractionRequest, ExtractionResult, 
    ExtractionStatus, ExtractionPriority, ContentType
)

# Import specialized extractors
from .content_extractors import (
    AudioContentExtractor, VideoContentExtractor, 
    ImageContentExtractor, TextContentExtractor,
    MetadataExtractor, ThumbnailExtractor
)

from .platform_extractors import (
    PlatformExtractorFactory, register_default_extractors
)

from .data_extractors import (
    DataExtractorFactory, register_default_data_extractors
)

from .web_extractors import (
    WebExtractorFactory, register_default_web_extractors
)

from .stream_extractors import (
    StreamManager, register_default_stream_extractors
)

logger = logging.getLogger(__name__)


class ExtractionStrategy(Enum):
    """Extraction strategy enumeration"""    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    PRIORITY_BASED = "priority_based"
    INTELLIGENT = "intelligent"


class CoordinationMode(Enum):
    """Coordination mode enumeration"""    SINGLE_EXTRACTOR = "single_extractor"
    MULTI_EXTRACTOR = "multi_extractor"
    CASCADING = "cascading"
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"


@dataclass
class ExtractionPlan:
    """Extraction execution plan"""    
    plan_id: str
    request: ExtractionRequest
    strategy: ExtractionStrategy
    coordination_mode: CoordinationMode
    extractors: List[BaseExtractor] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    timeout: int = 300
    retry_count: int = 3
    priority_override: Optional[ExtractionPriority] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_duration: Optional[float] = None
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionMetrics:
    """Extraction performance metrics"""    
    total_requests: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    extractor_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    resource_utilization: Dict[str, float] = field(default_factory=dict)


class ExtractionQueue:
    """Priority-based extraction queue"""    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_index = 0
        
    def put(self, plan: ExtractionPlan, priority: Optional[int] = None):
        """Add extraction plan to queue"""        with self.condition:
            if len(self.queue) >= self.max_size:
                # Remove lowest priority item
                self.queue.sort(key=lambda x: x[0])
                self.queue.pop(0)
            
            # Determine priority
            if priority is None:
                if plan.priority_override:
                    priority = plan.priority_override.value
                else:
                    priority = plan.request.priority.value
            
            # Add to queue with priority and timestamp
            heapq.heappush(self.queue, (-priority, time.time(), plan))
            self.condition.notify()
    
    def get(self, timeout: Optional[float] = None) -> Optional[ExtractionPlan]:
        """Get highest priority extraction plan"""        with self.condition:
            if not self.queue:
                if timeout:
                    self.condition.wait(timeout)
                else:
                    self.condition.wait()
            
            if self.queue:
                _, _, plan = heapq.heappop(self.queue)
                return plan
            
            return None
    
    def size(self) -> int:
        """Get queue size"""        with self.lock:
            return len(self.queue)
    
    def clear(self):
        """Clear queue"""        with self.condition:
            self.queue.clear()
            self.condition.notify_all()


class ExtractionRouter:
    """Intelligent extraction router"""    
    def __init__(self):
        self.content_extractors = [
            AudioContentExtractor(),
            VideoContentExtractor(),
            ImageContentExtractor(),
            TextContentExtractor(),
            MetadataExtractor(),
            ThumbnailExtractor()
        ]
        
        self.platform_factory = PlatformExtractorFactory
        self.data_factory = DataExtractorFactory
        self.web_factory = WebExtractorFactory
        self.stream_manager = register_default_stream_extractors()
        
        # Performance tracking
        self.extractor_metrics: Dict[str, Dict[str, float]] = {}
        
    async def route_request(self, request: ExtractionRequest) -> List[BaseExtractor]:
        """Route extraction request to appropriate extractors"""        extractors = []
        
        # Route based on source type
        if request.source_url:
            extractors.extend(await self._route_url_request(request))
        elif request.source_path:
            extractors.extend(await self._route_file_request(request))
        elif request.source_data:
            extractors.extend(await self._route_data_request(request))
        
        # Filter based on capability and performance
        filtered_extractors = await self._filter_extractors(extractors, request)
        
        # Sort by performance metrics
        return await self._rank_extractors(filtered_extractors, request)
    
    async def _route_url_request(self, request: ExtractionRequest) -> List[BaseExtractor]:
        """Route URL-based requests"""        extractors = []
        
        # Check platform extractors
        platform_extractor = self.platform_factory.get_extractor_for_url(request.source_url)
        if platform_extractor:
            extractors.append(platform_extractor)
        
        # Check web extractors
        web_extractors = self.web_factory.get_extractors_for_url(request.source_url)
        extractors.extend(web_extractors)
        
        # Check stream extractors
        stream_id = await self.stream_manager.start_stream(request)
        if stream_id:
            # Stream extractors are handled differently
            pass
        
        return extractors
    
    async def _route_file_request(self, request: ExtractionRequest) -> List[BaseExtractor]:
        """Route file-based requests"""        extractors = []
        
        # Check data extractors
        data_extractor = self.data_factory.get_extractor(request)
        if data_extractor:
            extractors.append(data_extractor)
        
        # Check content extractors
        for extractor in self.content_extractors:
            if await extractor.can_handle(request):
                extractors.append(extractor)
        
        return extractors
    
    async def _route_data_request(self, request: ExtractionRequest) -> List[BaseExtractor]:
        """Route data-based requests"""        extractors = []
        
        # Check data extractors
        data_extractor = self.data_factory.get_extractor(request)
        if data_extractor:
            extractors.append(data_extractor)
        
        # Check content extractors
        for extractor in self.content_extractors:
            if await extractor.can_handle(request):
                extractors.append(extractor)
        
        return extractors
    
    async def _filter_extractors(self, extractors: List[BaseExtractor], request: ExtractionRequest) -> List[BaseExtractor]:
        """Filter extractors based on capabilities"""        filtered = []
        
        for extractor in extractors:
            try:
                if await extractor.can_handle(request):
                    filtered.append(extractor)
            except Exception as e:
                logger.warning(f"Extractor {extractor.name} capability check failed: {str(e)}")
        
        return filtered
    
    async def _rank_extractors(self, extractors: List[BaseExtractor], request: ExtractionRequest) -> List[BaseExtractor]:
        """Rank extractors by performance and suitability"""        if not extractors:
            return []
        
        scored_extractors = []
        
        for extractor in extractors:
            score = await self._calculate_extractor_score(extractor, request)
            scored_extractors.append((score, extractor))
        
        # Sort by score (descending)
        scored_extractors.sort(key=lambda x: x[0], reverse=True)
        
        return [extractor for _, extractor in scored_extractors]
    
    async def _calculate_extractor_score(self, extractor: BaseExtractor, request: ExtractionRequest) -> float:
        """Calculate extractor suitability score"""        score = 50.0  # Base score
        
        # Performance metrics
        if extractor.name in self.extractor_metrics:
            metrics = self.extractor_metrics[extractor.name]
            
            # Success rate
            success_rate = metrics.get('success_rate', 0.5)
            score += success_rate * 30
            
            # Average processing time (lower is better)
            avg_time = metrics.get('avg_processing_time', 10.0)
            score += max(0, 20 - avg_time)
            
            # Reliability score
            reliability = metrics.get('reliability', 0.5)
            score += reliability * 20
        
        # Content type matching
        if request.content_type and hasattr(extractor, 'content_type'):
            if extractor.content_type == request.content_type:
                score += 15
        
        # Platform matching
        if request.platform and hasattr(extractor, 'platform'):
            if extractor.platform == request.platform:
                score += 25
        
        return score
    
    def update_extractor_metrics(self, extractor_name: str, processing_time: float, success: bool):
        """Update extractor performance metrics"""        if extractor_name not in self.extractor_metrics:
            self.extractor_metrics[extractor_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_time': 0.0,
                'avg_processing_time': 0.0,
                'success_rate': 0.0,
                'reliability': 0.5
            }
        
        metrics = self.extractor_metrics[extractor_name]
        metrics['total_requests'] += 1
        metrics['total_time'] += processing_time
        
        if success:
            metrics['successful_requests'] += 1
        
        # Update calculated metrics
        metrics['avg_processing_time'] = metrics['total_time'] / metrics['total_requests']
        metrics['success_rate'] = metrics['successful_requests'] / metrics['total_requests']
        
        # Update reliability (weighted average)
        current_reliability = 1.0 if success else 0.0
        metrics['reliability'] = 0.9 * metrics['reliability'] + 0.1 * current_reliability


class ExtractionOrchestrator:
    """Orchestrates complex extraction workflows"""    
    def __init__(self):
        self.router = ExtractionRouter()
        self.queue = ExtractionQueue()
        self.metrics = ExtractionMetrics()
        self.active_extractions: Dict[str, ExtractionPlan] = {}
        self.completed_extractions: Dict[str, ExtractionResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False
        
    async def start(self):
        """Start the orchestrator"""        self.is_running = True
        
        # Start worker tasks
        for i in range(5):  # 5 worker tasks
            asyncio.create_task(self._worker_task(f"worker_{i}"))
        
        logger.info("Extraction orchestrator started")
    
    async def stop(self):
        """Stop the orchestrator"""        self.is_running = False
        self.queue.clear()
        self.executor.shutdown(wait=True)
        logger.info("Extraction orchestrator stopped")
    
    async def submit_extraction(self, request: ExtractionRequest, strategy: ExtractionStrategy = ExtractionStrategy.INTELLIGENT) -> str:
        """Submit extraction request"""        # Create extraction plan
        plan = await self._create_extraction_plan(request, strategy)
        
        # Add to queue
        self.queue.put(plan)
        
        # Track metrics
        self.metrics.total_requests += 1
        
        return plan.plan_id
    
    async def get_extraction_result(self, plan_id: str) -> Optional[ExtractionResult]:
        """Get extraction result"""        return self.completed_extractions.get(plan_id)
    
    async def get_extraction_status(self, plan_id: str) -> Optional[ExtractionStatus]:
        """Get extraction status"""        if plan_id in self.completed_extractions:
            return self.completed_extractions[plan_id].status
        elif plan_id in self.active_extractions:
            return ExtractionStatus.RUNNING
        else:
            return None
    
    async def cancel_extraction(self, plan_id: str) -> bool:
        """Cancel extraction"""        if plan_id in self.active_extractions:
            # Mark for cancellation
            plan = self.active_extractions[plan_id]
            plan.request.metadata['cancelled'] = True
            return True
        return False
    
    async def _create_extraction_plan(self, request: ExtractionRequest, strategy: ExtractionStrategy) -> ExtractionPlan:
        """Create extraction execution plan"""        import uuid
        plan_id = str(uuid.uuid4())
        
        # Route to appropriate extractors
        extractors = await self.router.route_request(request)
        
        # Determine coordination mode
        coordination_mode = await self._determine_coordination_mode(extractors, strategy)
        
        # Estimate duration
        estimated_duration = await self._estimate_duration(extractors, request)
        
        plan = ExtractionPlan(
            plan_id=plan_id,
            request=request,
            strategy=strategy,
            coordination_mode=coordination_mode,
            extractors=extractors,
            estimated_duration=estimated_duration
        )
        
        return plan
    
    async def _determine_coordination_mode(self, extractors: List[BaseExtractor], strategy: ExtractionStrategy) -> CoordinationMode:
        """Determine appropriate coordination mode"""        if len(extractors) == 0:
            return CoordinationMode.SINGLE_EXTRACTOR
        elif len(extractors) == 1:
            return CoordinationMode.SINGLE_EXTRACTOR
        elif strategy == ExtractionStrategy.SEQUENTIAL:
            return CoordinationMode.CASCADING
        elif strategy == ExtractionStrategy.PARALLEL:
            return CoordinationMode.COMPETITIVE
        elif strategy == ExtractionStrategy.INTELLIGENT:
            # Use collaborative mode for intelligent strategy
            return CoordinationMode.COLLABORATIVE
        else:
            return CoordinationMode.MULTI_EXTRACTOR
    
    async def _estimate_duration(self, extractors: List[BaseExtractor], request: ExtractionRequest) -> float:
        """Estimate extraction duration"""        if not extractors:
            return 0.0
        
        total_estimate = 0.0
        
        for extractor in extractors:
            if extractor.name in self.router.extractor_metrics:
                avg_time = self.router.extractor_metrics[extractor.name]['avg_processing_time']
                total_estimate += avg_time
            else:
                # Default estimate
                total_estimate += 5.0
        
        # Adjust for coordination mode
        if len(extractors) > 1:
            total_estimate *= 0.7  # Parallel execution benefit
        
        return total_estimate
    
    async def _worker_task(self, worker_name: str):
        """Worker task for processing extractions"""        logger.info(f"Worker {worker_name} started")
        
        while self.is_running:
            try:
                # Get next plan from queue
                plan = self.queue.get(timeout=1.0)
                
                if plan is None:
                    continue
                
                # Check if cancelled
                if plan.request.metadata.get('cancelled'):
                    continue
                
                # Execute plan
                self.active_extractions[plan.plan_id] = plan
                
                logger.info(f"Worker {worker_name} executing plan {plan.plan_id}")
                
                result = await self._execute_plan(plan)
                
                # Store result
                self.completed_extractions[plan.plan_id] = result
                
                # Remove from active
                if plan.plan_id in self.active_extractions:
                    del self.active_extractions[plan.plan_id]
                
                # Update metrics
                await self._update_metrics(plan, result)
                
                logger.info(f"Worker {worker_name} completed plan {plan.plan_id}")
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {str(e)}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _execute_plan(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute extraction plan"""        start_time = time.time()
        
        try:
            if plan.coordination_mode == CoordinationMode.SINGLE_EXTRACTOR:
                result = await self._execute_single_extractor(plan)
            elif plan.coordination_mode == CoordinationMode.CASCADING:
                result = await self._execute_cascading(plan)
            elif plan.coordination_mode == CoordinationMode.COMPETITIVE:
                result = await self._execute_competitive(plan)
            elif plan.coordination_mode == CoordinationMode.COLLABORATIVE:
                result = await self._execute_collaborative(plan)
            else:
                result = await self._execute_multi_extractor(plan)
            
            # Set processing time
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Plan execution failed: {str(e)}")
            return ExtractionResult(
                request_id=plan.request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _execute_single_extractor(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute with single extractor"""        if not plan.extractors:
            return ExtractionResult(
                request_id=plan.request.request_id,
                status=ExtractionStatus.FAILED,
                error="No extractors available"
            )
        
        extractor = plan.extractors[0]
        
        try:
            result = await extractor.extract(plan.request)
            
            # Update extractor metrics
            self.router.update_extractor_metrics(
                extractor.name,
                result.processing_time or 0.0,
                result.status == ExtractionStatus.COMPLETED
            )
            
            return result
            
        except Exception as e:
            return ExtractionResult(
                request_id=plan.request.request_id,
                status=ExtractionStatus.FAILED,
                error=f"Extractor {extractor.name} failed: {str(e)}"
            )
    
    async def _execute_cascading(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute extractors in sequence (cascading)"""        combined_result = ExtractionResult(
            request_id=plan.request.request_id,
            status=ExtractionStatus.COMPLETED,
            extracted_data={},
            metadata={}
        )
        
        for i, extractor in enumerate(plan.extractors):
            try:
                result = await extractor.extract(plan.request)
                
                # Update extractor metrics
                self.router.update_extractor_metrics(
                    extractor.name,
                    result.processing_time or 0.0,
                    result.status == ExtractionStatus.COMPLETED
                )
                
                if result.status == ExtractionStatus.COMPLETED:
                    # Merge results
                    combined_result.extracted_data[f"extractor_{i}_{extractor.name}"] = result.extracted_data
                    combined_result.metadata[f"extractor_{i}_{extractor.name}"] = result.metadata
                else:
                    # Continue with next extractor
                    combined_result.metadata[f"extractor_{i}_{extractor.name}_error"] = result.error
                
            except Exception as e:
                combined_result.metadata[f"extractor_{i}_{extractor.name}_exception"] = str(e)
        
        return combined_result
    
    async def _execute_competitive(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute extractors in parallel (competitive)"""        if not plan.extractors:
            return ExtractionResult(
                request_id=plan.request.request_id,
                status=ExtractionStatus.FAILED,
                error="No extractors available"
            )
        
        # Create tasks for all extractors
        tasks = []
        for extractor in plan.extractors:
            task = asyncio.create_task(extractor.extract(plan.request))
            tasks.append((extractor, task))
        
        # Wait for first successful result
        best_result = None
        completed_tasks = []
        
        try:
            # Wait for tasks to complete
            for extractor, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=plan.timeout)
                    completed_tasks.append((extractor, result))
                    
                    # Update metrics
                    self.router.update_extractor_metrics(
                        extractor.name,
                        result.processing_time or 0.0,
                        result.status == ExtractionStatus.COMPLETED
                    )
                    
                    # Select best result
                    if result.status == ExtractionStatus.COMPLETED:
                        if best_result is None or await self._is_better_result(result, best_result):
                            best_result = result
                    
                except asyncio.TimeoutError:
                    self.router.update_extractor_metrics(extractor.name, plan.timeout, False)
                except Exception as e:
                    logger.error(f"Extractor {extractor.name} failed: {str(e)}")
                    self.router.update_extractor_metrics(extractor.name, 0.0, False)
            
            if best_result:
                return best_result
            else:
                return ExtractionResult(
                    request_id=plan.request.request_id,
                    status=ExtractionStatus.FAILED,
                    error="All extractors failed"
                )
        
        finally:
            # Cancel remaining tasks
            for _, task in tasks:
                if not task.done():
                    task.cancel()
    
    async def _execute_collaborative(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute extractors collaboratively"""        if not plan.extractors:
            return ExtractionResult(
                request_id=plan.request.request_id,
                status=ExtractionStatus.FAILED,
                error="No extractors available"
            )
        
        # Execute all extractors in parallel
        tasks = []
        for extractor in plan.extractors:
            task = asyncio.create_task(extractor.extract(plan.request))
            tasks.append((extractor, task))
        
        # Collect all results
        results = []
        
        for extractor, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=plan.timeout)
                results.append((extractor, result))
                
                # Update metrics
                self.router.update_extractor_metrics(
                    extractor.name,
                    result.processing_time or 0.0,
                    result.status == ExtractionStatus.COMPLETED
                )
                
            except asyncio.TimeoutError:
                self.router.update_extractor_metrics(extractor.name, plan.timeout, False)
            except Exception as e:
                logger.error(f"Extractor {extractor.name} failed: {str(e)}")
                self.router.update_extractor_metrics(extractor.name, 0.0, False)
        
        # Combine results intelligently
        return await self._combine_results(plan.request.request_id, results)
    
    async def _execute_multi_extractor(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute multiple extractors with default strategy"""        return await self._execute_collaborative(plan)
    
    async def _is_better_result(self, result1: ExtractionResult, result2: ExtractionResult) -> bool:
        """Compare extraction results to determine which is better"""        # Simple scoring based on data completeness
        score1 = await self._calculate_result_score(result1)
        score2 = await self._calculate_result_score(result2)
        
        return score1 > score2
    
    async def _calculate_result_score(self, result: ExtractionResult) -> float:
        """Calculate result quality score"""        score = 0.0
        
        if result.status == ExtractionStatus.COMPLETED:
            score += 50.0
        elif result.status == ExtractionStatus.RUNNING:
            score += 25.0
        
        # Data completeness
        if result.extracted_data:
            score += len(str(result.extracted_data)) / 100.0
        
        # Metadata completeness
        if result.metadata:
            score += len(str(result.metadata)) / 200.0
        
        # Processing time (lower is better)
        if result.processing_time:
            score += max(0, 25 - result.processing_time)
        
        return score
    
    async def _combine_results(self, request_id: str, results: List[Tuple[BaseExtractor, ExtractionResult]]) -> ExtractionResult:
        """Intelligently combine multiple extraction results"""        combined_result = ExtractionResult(
            request_id=request_id,
            status=ExtractionStatus.COMPLETED,
            extracted_data={},
            metadata={'combination_info': {'extractor_count': len(results)}}
        )
        
        successful_results = [
            (extractor, result) for extractor, result in results
            if result.status == ExtractionStatus.COMPLETED
        ]
        
        if not successful_results:
            combined_result.status = ExtractionStatus.FAILED
            combined_result.error = "No successful extractions"
            return combined_result
        
        # Combine data from all successful extractions
        for extractor, result in successful_results:
            extractor_key = f"{extractor.name}_data"
            combined_result.extracted_data[extractor_key] = result.extracted_data
            combined_result.metadata[f"{extractor.name}_metadata"] = result.metadata
        
        # Create consensus data where possible
        combined_result.extracted_data['consensus'] = await self._create_consensus_data(successful_results)
        
        # Calculate combined processing time
        total_time = sum(result.processing_time or 0.0 for _, result in results)
        combined_result.processing_time = total_time / len(results) if results else 0.0
        
        return combined_result
    
    async def _create_consensus_data(self, results: List[Tuple[BaseExtractor, ExtractionResult]]) -> Dict[str, Any]:
        """Create consensus data from multiple extraction results"""        consensus = {}
        
        # Simple consensus for common fields
        common_fields = ['title', 'description', 'author', 'content', 'url']
        
        for field in common_fields:
            values = []
            for extractor, result in results:
                if isinstance(result.extracted_data, dict) and field in result.extracted_data:
                    values.append(result.extracted_data[field])
            
            if values:
                # Use most common value or longest value for text fields
                if isinstance(values[0], str):
                    consensus[field] = max(values, key=len) if values else None
                else:
                    # For non-string values, use first available
                    consensus[field] = values[0]
        
        return consensus
    
    async def _update_metrics(self, plan: ExtractionPlan, result: ExtractionResult):
        """Update orchestrator metrics"""        if result.status == ExtractionStatus.COMPLETED:
            self.metrics.successful_extractions += 1
        else:
            self.metrics.failed_extractions += 1
        
        if result.processing_time:
            self.metrics.total_processing_time += result.processing_time
            self.metrics.average_processing_time = (
                self.metrics.total_processing_time / self.metrics.total_requests
            )
        
        self.metrics.error_rate = (
            self.metrics.failed_extractions / self.metrics.total_requests
        ) if self.metrics.total_requests > 0 else 0.0
        
        # Calculate throughput (extractions per second)
        if self.metrics.total_processing_time > 0:
            self.metrics.throughput = (
                self.metrics.total_requests / self.metrics.total_processing_time
            )
    
    def get_metrics(self) -> ExtractionMetrics:
        """Get current metrics"""        return self.metrics
    
    def get_active_extractions(self) -> Dict[str, ExtractionPlan]:
        """Get currently active extractions"""        return self.active_extractions.copy()


# Global orchestrator instance
orchestrator = ExtractionOrchestrator()


__all__ = [
    'ExtractionStrategy',
    'CoordinationMode', 
    'ExtractionPlan',
    'ExtractionMetrics',
    'ExtractionQueue',
    'ExtractionRouter',
    'ExtractionOrchestrator',
    'orchestrator'
]
