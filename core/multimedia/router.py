"""
Multimedia Router - Advanced Content Routing Engine

Enterprise-grade routing system for multimedia content with intelligent distribution logic.
Manages content flow between different processing stages and destinations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import uuid
import time
from pathlib import Path

from ..monitoring.metrics import MetricsCollector
from ..events.dispatcher import EventDispatcher
from .metadata import MultimediaMetadata
from .analyzer import MultimediaAnalyzer

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Content routing strategies"""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"
    CONTENT_AWARE = "content_aware"
    GEOGRAPHIC = "geographic"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"


class DestinationType(Enum):
    """Types of routing destinations"""
    PROCESSING_PIPELINE = "processing_pipeline"
    STORAGE_SYSTEM = "storage_system"
    CDN_ENDPOINT = "cdn_endpoint"
    STREAMING_SERVER = "streaming_server"
    API_ENDPOINT = "api_endpoint"
    MICROSERVICE = "microservice"
    EXTERNAL_SERVICE = "external_service"


class RoutingPriority(Enum):
    """Routing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class RoutingDestination:
    """Routing destination configuration"""
    destination_id: str
    name: str
    destination_type: DestinationType
    endpoint_url: str
    max_concurrent: int = 10
    weight: float = 1.0
    health_check_url: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingRule:
    """Content routing rule"""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    destination_ids: List[str]
    strategy: RoutingStrategy
    priority: RoutingPriority
    max_retries: int = 3
    timeout_seconds: int = 30
    failover_destinations: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class RoutingRequest:
    """Content routing request"""
    request_id: str
    content_path: str
    content_metadata: Dict[str, Any]
    target_destinations: Optional[List[str]] = None
    priority: RoutingPriority = RoutingPriority.NORMAL
    callback: Optional[Callable] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    routing_hints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RoutingResult:
    """Routing operation result"""
    request_id: str
    success: bool
    destination_id: str
    routing_time: float
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    final_url: Optional[str] = None


class MultimediaRouter:
    """
    Advanced multimedia content routing engine with intelligent distribution.
    
    Features:
    - Multiple routing strategies
    - Load balancing and failover
    - Health monitoring of destinations
    - Content-aware routing decisions
    - Geographic distribution
    - Performance optimization
    - Real-time metrics and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize multimedia router"""
        self.config = config or {}
        self.metrics = MetricsCollector()
        self.events = EventDispatcher()
        self.metadata_analyzer = MultimediaMetadata()
        self.content_analyzer = MultimediaAnalyzer()
        
        # Routing configuration
        self.destinations: Dict[str, RoutingDestination] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        
        # Active routing requests
        self.active_requests: Dict[str, RoutingRequest] = {}
        self.completed_requests: Dict[str, RoutingResult] = {}
        
        # Load balancing state
        self.load_balancer_state = {
            'round_robin_counters': {},
            'destination_loads': {},
            'destination_health': {}
        }
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_routing_time': 0.0,
            'destination_usage': {},
            'strategy_usage': {}
        }
        
        # Initialize default destinations and rules
        self._initialize_default_configuration()
        
        # Start health monitoring
        self._start_health_monitoring()
        
        logger.info("Multimedia router initialized successfully")
    
    def _initialize_default_configuration(self):
        """Initialize default routing configuration"""
        # Default destinations
        self.add_destination(RoutingDestination(
            destination_id="local_storage",
            name="Local Storage",
            destination_type=DestinationType.STORAGE_SYSTEM,
            endpoint_url="file:///var/multimedia/storage",
            max_concurrent=20
        ))
        
        self.add_destination(RoutingDestination(
            destination_id="cdn_primary",
            name="Primary CDN",
            destination_type=DestinationType.CDN_ENDPOINT,
            endpoint_url="https://cdn-primary.example.com/upload",
            max_concurrent=15,
            weight=2.0
        ))
        
        self.add_destination(RoutingDestination(
            destination_id="processing_pipeline",
            name="Processing Pipeline",
            destination_type=DestinationType.PROCESSING_PIPELINE,
            endpoint_url="http://processing.internal:8080/process",
            max_concurrent=5
        ))
        
        # Default routing rules
        self.add_routing_rule(RoutingRule(
            rule_id="high_quality_video",
            name="High Quality Video Processing",
            conditions={
                'content_type': 'video',
                'file_size_mb': {'min': 100},
                'resolution': {'min_width': 1920}
            },
            destination_ids=["processing_pipeline"],
            strategy=RoutingStrategy.PRIORITY_BASED,
            priority=RoutingPriority.HIGH
        ))
        
        self.add_routing_rule(RoutingRule(
            rule_id="general_content",
            name="General Content Distribution",
            conditions={},  # Match all
            destination_ids=["cdn_primary", "local_storage"],
            strategy=RoutingStrategy.LOAD_BALANCED,
            priority=RoutingPriority.NORMAL
        ))
    
    def add_destination(self, destination: RoutingDestination):
        """Add routing destination"""
        self.destinations[destination.destination_id] = destination
        self.load_balancer_state['round_robin_counters'][destination.destination_id] = 0
        self.load_balancer_state['destination_loads'][destination.destination_id] = 0
        self.load_balancer_state['destination_health'][destination.destination_id] = True
        
        logger.info(f"Added routing destination: {destination.name}")
    
    def add_routing_rule(self, rule: RoutingRule):
        """Add routing rule"""
        self.routing_rules[rule.rule_id] = rule
        logger.info(f"Added routing rule: {rule.name}")
    
    async def route_content(
        self,
        content_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        target_destinations: Optional[List[str]] = None,
        priority: RoutingPriority = RoutingPriority.NORMAL
    ) -> str:
        """
        Route content to appropriate destinations
        
        Args:
            content_path: Path to content file
            metadata: Content metadata (optional)
            target_destinations: Specific destinations to route to
            priority: Routing priority
            
        Returns:
            str: Request ID
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Extract metadata if not provided
        if metadata is None:
            metadata = await self.content_analyzer.analyze_content(content_path)
        
        # Create routing request
        request = RoutingRequest(
            request_id=request_id,
            content_path=content_path,
            content_metadata=metadata,
            target_destinations=target_destinations,
            priority=priority
        )
        
        # Add to active requests
        self.active_requests[request_id] = request
        
        # Start routing process
        asyncio.create_task(self._execute_routing(request))
        
        # Emit event
        await self.events.emit('routing_request_created', {
            'request_id': request_id,
            'content_path': content_path,
            'priority': priority.value
        })
        
        logger.info(f"Content routing request created: {request_id}")
        return request_id
    
    async def _execute_routing(self, request: RoutingRequest) -> List[RoutingResult]:
        """Execute content routing for a request"""
        start_time = time.time()
        results = []
        
        try:
            # Determine routing destinations
            if request.target_destinations:
                destination_ids = request.target_destinations
            else:
                destination_ids = await self._select_destinations(request)
            
            # Route to each destination
            for destination_id in destination_ids:
                if destination_id not in self.destinations:
                    logger.warning(f"Unknown destination: {destination_id}")
                    continue
                
                destination = self.destinations[destination_id]
                
                # Check destination health and capacity
                if not await self._check_destination_availability(destination):
                    logger.warning(f"Destination unavailable: {destination_id}")
                    continue
                
                # Execute routing to destination
                result = await self._route_to_destination(request, destination)
                results.append(result)
                
                # Update load balancing state
                self.load_balancer_state['destination_loads'][destination_id] += 1
            
            # Update statistics
            self.stats['total_requests'] += 1
            if any(r.success for r in results):
                self.stats['successful_routes'] += 1
            else:
                self.stats['failed_routes'] += 1
            
            routing_time = time.time() - start_time
            self.stats['average_routing_time'] = (
                (self.stats['average_routing_time'] * (self.stats['total_requests'] - 1) + routing_time) /
                self.stats['total_requests']
            )
            
            # Move to completed requests
            if results:
                self.completed_requests[request.request_id] = results[0]  # Store first result
            
            # Remove from active requests
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
            
            # Execute callback if provided
            if request.callback:
                try:
                    await request.callback(results)
                except Exception as e:
                    logger.error(f"Routing callback failed: {str(e)}")
            
            # Emit completion event
            await self.events.emit('routing_completed', {
                'request_id': request.request_id,
                'results': len(results),
                'success': any(r.success for r in results)
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Routing execution failed: {str(e)}")
            
            # Create error result
            error_result = RoutingResult(
                request_id=request.request_id,
                success=False,
                destination_id="",
                routing_time=time.time() - start_time,
                error_message=str(e)
            )
            
            self.completed_requests[request.request_id] = error_result
            self.stats['failed_routes'] += 1
            
            return [error_result]
    
    async def _select_destinations(self, request: RoutingRequest) -> List[str]:
        """Select appropriate destinations for routing request"""
        selected_destinations = []
        
        # Find matching routing rules
        matching_rules = []
        for rule in self.routing_rules.values():
            if rule.is_active and await self._evaluate_rule_conditions(request, rule):
                matching_rules.append(rule)
        
        # Sort by priority
        matching_rules.sort(key=lambda r: r.priority.value)
        
        # Select destinations from highest priority rule
        if matching_rules:
            best_rule = matching_rules[0]
            selected_destinations = best_rule.destination_ids.copy()
            
            # Apply routing strategy
            if best_rule.strategy == RoutingStrategy.ROUND_ROBIN:
                selected_destinations = [await self._select_round_robin(selected_destinations)]
            elif best_rule.strategy == RoutingStrategy.LOAD_BALANCED:
                selected_destinations = [await self._select_load_balanced(selected_destinations)]
            elif best_rule.strategy == RoutingStrategy.CONTENT_AWARE:
                selected_destinations = await self._select_content_aware(request, selected_destinations)
            
            # Update strategy usage statistics
            strategy_name = best_rule.strategy.value
            self.stats['strategy_usage'][strategy_name] = self.stats['strategy_usage'].get(strategy_name, 0) + 1
        
        return selected_destinations
    
    async def _evaluate_rule_conditions(
        self,
        request: RoutingRequest,
        rule: RoutingRule
    ) -> bool:
        """Evaluate if request matches rule conditions"""
        if not rule.conditions:
            return True  # Empty conditions match all
        
        metadata = request.content_metadata
        
        for condition_key, condition_value in rule.conditions.items():
            if condition_key not in metadata:
                return False
            
            metadata_value = metadata[condition_key]
            
            # Handle different condition types
            if isinstance(condition_value, dict):
                # Range conditions
                if 'min' in condition_value and metadata_value < condition_value['min']:
                    return False
                if 'max' in condition_value and metadata_value > condition_value['max']:
                    return False
                if 'min_width' in condition_value and isinstance(metadata_value, (list, tuple)):
                    if len(metadata_value) > 0 and metadata_value[0] < condition_value['min_width']:
                        return False
            elif isinstance(condition_value, list):
                # Must be in list
                if metadata_value not in condition_value:
                    return False
            else:
                # Exact match
                if metadata_value != condition_value:
                    return False
        
        return True
    
    async def _select_round_robin(self, destination_ids: List[str]) -> str:
        """Select destination using round-robin strategy"""
        active_destinations = [d for d in destination_ids if self.destinations[d].is_active]
        
        if not active_destinations:
            return destination_ids[0] if destination_ids else ""
        
        # Find destination with lowest round-robin counter
        selected = min(active_destinations, 
                      key=lambda d: self.load_balancer_state['round_robin_counters'][d])
        
        # Increment counter
        self.load_balancer_state['round_robin_counters'][selected] += 1
        
        return selected
    
    async def _select_load_balanced(self, destination_ids: List[str]) -> str:
        """Select destination using load-balanced strategy"""
        active_destinations = [d for d in destination_ids if self.destinations[d].is_active]
        
        if not active_destinations:
            return destination_ids[0] if destination_ids else ""
        
        # Calculate weighted loads
        weighted_loads = {}
        for dest_id in active_destinations:
            destination = self.destinations[dest_id]
            current_load = self.load_balancer_state['destination_loads'][dest_id]
            weighted_load = current_load / (destination.weight * destination.max_concurrent)
            weighted_loads[dest_id] = weighted_load
        
        # Select destination with lowest weighted load
        selected = min(weighted_loads.keys(), key=lambda d: weighted_loads[d])
        
        return selected
    
    async def _select_content_aware(
        self,
        request: RoutingRequest,
        destination_ids: List[str]
    ) -> List[str]:
        """Select destinations using content-aware strategy"""
        metadata = request.content_metadata
        content_type = metadata.get('content_type', 'unknown')
        file_size = metadata.get('file_size', 0)
        
        selected = []
        
        for dest_id in destination_ids:
            destination = self.destinations[dest_id]
            
            # Content type matching
            if destination.destination_type == DestinationType.PROCESSING_PIPELINE:
                if content_type in ['video', 'audio']:
                    selected.append(dest_id)
            elif destination.destination_type == DestinationType.CDN_ENDPOINT:
                if file_size < 100 * 1024 * 1024:  # < 100MB
                    selected.append(dest_id)
            else:
                selected.append(dest_id)
        
        return selected if selected else destination_ids
    
    async def _check_destination_availability(self, destination: RoutingDestination) -> bool:
        """Check if destination is available for routing"""
        if not destination.is_active:
            return False
        
        # Check current load
        current_load = self.load_balancer_state['destination_loads'][destination.destination_id]
        if current_load >= destination.max_concurrent:
            return False
        
        # Check health status
        health_status = self.load_balancer_state['destination_health'][destination.destination_id]
        if not health_status:
            return False
        
        return True
    
    async def _route_to_destination(
        self,
        request: RoutingRequest,
        destination: RoutingDestination
    ) -> RoutingResult:
        """Route content to specific destination"""
        start_time = time.time()
        
        try:
            # Prepare routing data
            routing_data = {
                'content_path': request.content_path,
                'metadata': request.content_metadata,
                'destination': destination.destination_id,
                'priority': request.priority.value
            }
            
            # Execute routing based on destination type
            if destination.destination_type == DestinationType.STORAGE_SYSTEM:
                result_data = await self._route_to_storage(routing_data, destination)
            elif destination.destination_type == DestinationType.CDN_ENDPOINT:
                result_data = await self._route_to_cdn(routing_data, destination)
            elif destination.destination_type == DestinationType.PROCESSING_PIPELINE:
                result_data = await self._route_to_processor(routing_data, destination)
            else:
                result_data = await self._route_to_generic_endpoint(routing_data, destination)
            
            # Update destination usage statistics
            dest_id = destination.destination_id
            self.stats['destination_usage'][dest_id] = self.stats['destination_usage'].get(dest_id, 0) + 1
            
            return RoutingResult(
                request_id=request.request_id,
                success=True,
                destination_id=destination.destination_id,
                routing_time=time.time() - start_time,
                response_data=result_data,
                final_url=destination.endpoint_url
            )
            
        except Exception as e:
            logger.error(f"Routing to destination failed: {str(e)}")
            
            return RoutingResult(
                request_id=request.request_id,
                success=False,
                destination_id=destination.destination_id,
                routing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _route_to_storage(
        self,
        routing_data: Dict[str, Any],
        destination: RoutingDestination
    ) -> Dict[str, Any]:
        """Route content to storage system"""
        # This would implement actual storage routing
        content_path = routing_data['content_path']
        
        # Simulate storage operation
        await asyncio.sleep(0.1)
        
        return {
            'stored_path': f"{destination.endpoint_url}/{Path(content_path).name}",
            'storage_id': str(uuid.uuid4()),
            'stored_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def _route_to_cdn(
        self,
        routing_data: Dict[str, Any],
        destination: RoutingDestination
    ) -> Dict[str, Any]:
        """Route content to CDN endpoint"""
        # This would implement actual CDN upload
        content_path = routing_data['content_path']
        
        # Simulate CDN upload
        await asyncio.sleep(0.2)
        
        return {
            'cdn_url': f"{destination.endpoint_url}/{Path(content_path).name}",
            'edge_locations': ['us-east-1', 'eu-west-1'],
            'cache_status': 'cached'
        }
    
    async def _route_to_processor(
        self,
        routing_data: Dict[str, Any],
        destination: RoutingDestination
    ) -> Dict[str, Any]:
        """Route content to processing pipeline"""
        # This would implement actual processing pipeline routing
        
        # Simulate processing submission
        await asyncio.sleep(0.05)
        
        return {
            'processing_job_id': str(uuid.uuid4()),
            'pipeline_stage': 'queued',
            'estimated_completion': (datetime.now(timezone.utc).timestamp() + 300)  # 5 minutes
        }
    
    async def _route_to_generic_endpoint(
        self,
        routing_data: Dict[str, Any],
        destination: RoutingDestination
    ) -> Dict[str, Any]:
        """Route content to generic API endpoint"""
        # This would implement actual HTTP API call
        
        # Simulate API call
        await asyncio.sleep(0.1)
        
        return {
            'endpoint_response': 'success',
            'response_code': 200,
            'response_time_ms': 100
        }
    
    def _start_health_monitoring(self):
        """Start health monitoring for destinations"""
        asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while True:
            try:
                for destination in self.destinations.values():
                    health_status = await self._check_destination_health(destination)
                    self.load_balancer_state['destination_health'][destination.destination_id] = health_status
                
                # Reset load counters periodically
                for dest_id in self.load_balancer_state['destination_loads']:
                    self.load_balancer_state['destination_loads'][dest_id] = max(
                        0, self.load_balancer_state['destination_loads'][dest_id] - 1
                    )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_destination_health(self, destination: RoutingDestination) -> bool:
        """Check health of a specific destination"""
        if not destination.health_check_url:
            return True  # Assume healthy if no health check configured
        
        try:
            # This would implement actual health check HTTP request
            # For now, simulate health check
            await asyncio.sleep(0.01)
            return True  # Assume healthy
            
        except Exception as e:
            logger.warning(f"Health check failed for {destination.name}: {str(e)}")
            return False
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get routing request status"""
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            return {
                'request_id': request_id,
                'status': 'active',
                'content_path': request.content_path,
                'priority': request.priority.value,
                'created_at': request.created_at
            }
        
        if request_id in self.completed_requests:
            result = self.completed_requests[request_id]
            return {
                'request_id': request_id,
                'status': 'completed',
                'success': result.success,
                'destination': result.destination_id,
                'routing_time': result.routing_time
            }
        
        return None
    
    def get_destination_status(self) -> Dict[str, Any]:
        """Get status of all destinations"""
        status = {}
        
        for dest_id, destination in self.destinations.items():
            status[dest_id] = {
                'name': destination.name,
                'type': destination.destination_type.value,
                'is_active': destination.is_active,
                'current_load': self.load_balancer_state['destination_loads'][dest_id],
                'max_concurrent': destination.max_concurrent,
                'health_status': self.load_balancer_state['destination_health'][dest_id],
                'weight': destination.weight
            }
        
        return status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""
        stats = self.stats.copy()
        stats.update({
            'active_requests': len(self.active_requests),
            'completed_requests': len(self.completed_requests),
            'total_destinations': len(self.destinations),
            'active_destinations': sum(1 for d in self.destinations.values() if d.is_active)
        })
        return stats
    
    def update_destination(self, destination_id: str, updates: Dict[str, Any]):
        """Update destination configuration"""
        if destination_id not in self.destinations:
            raise ValueError(f"Unknown destination: {destination_id}")
        
        destination = self.destinations[destination_id]
        
        for key, value in updates.items():
            if hasattr(destination, key):
                setattr(destination, key, value)
        
        logger.info(f"Updated destination {destination_id}: {updates}")
    
    def remove_destination(self, destination_id: str):
        """Remove routing destination"""
        if destination_id in self.destinations:
            del self.destinations[destination_id]
            del self.load_balancer_state['round_robin_counters'][destination_id]
            del self.load_balancer_state['destination_loads'][destination_id]
            del self.load_balancer_state['destination_health'][destination_id]
            
            logger.info(f"Removed destination: {destination_id}")
    
    def remove_routing_rule(self, rule_id: str):
        """Remove routing rule"""
        if rule_id in self.routing_rules:
            del self.routing_rules[rule_id]
            logger.info(f"Removed routing rule: {rule_id}")
