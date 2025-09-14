"""Priority Queue Manager Module

Intelligent priority queue management with fair scheduling and SLA enforcement
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Priority Queue Manager architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import heapq
from collections import defaultdict, deque

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class SchedulingAlgorithm(Enum):
    """Queue scheduling algorithms"""
    PRIORITY_STRICT = "priority_strict"
    WEIGHTED_FAIR = "weighted_fair"
    ROUND_ROBIN = "round_robin"
    DEADLINE_AWARE = "deadline_aware"


class SLALevel(Enum):
    """Service Level Agreement levels"""
    PLATINUM = "platinum"  # < 1s processing
    GOLD = "gold"         # < 5s processing
    SILVER = "silver"     # < 30s processing
    BRONZE = "bronze"     # < 300s processing


@dataclass
class PriorityMessage:
    """Message with priority and scheduling metadata"""
    id: str = field(default_factory=lambda: str(uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    queue_name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = None
    sla_level: SLALevel = SLALevel.BRONZE
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling metadata
    enqueue_time: float = field(default_factory=time.time)
    wait_time: float = 0.0
    processing_time: float = 0.0
    retry_count: int = 0
    aging_factor: float = 1.0
    
    def __lt__(self, other) -> None:
        """Comparison for heap operations"""
        # Lower priority value = higher priority
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        
        # Then by deadline if available
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        elif self.deadline:
            return True
        elif other.deadline:
            return False
        
        # Finally by creation time (FIFO within same priority)
        return self.created_at < other.created_at


@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    queue_name: str
    total_messages: int = 0
    processed_messages: int = 0
    failed_messages: int = 0
    avg_wait_time: float = 0.0
    avg_processing_time: float = 0.0
    throughput_per_minute: float = 0.0
    sla_compliance: Dict[str, float] = field(default_factory=dict)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AinflueBusiness:
    """Ainflue Business Priority Rules"""
    
    # Priority rules by event type
    PRIORITY_RULES = {
        # Critical business events
        "payment_processing": MessagePriority.CRITICAL,
        "security_alerts": MessagePriority.CRITICAL,
        "content_copyright_violation": MessagePriority.CRITICAL,
        "system_health_critical": MessagePriority.CRITICAL,
        
        # High priority events
        "premium_content_upload": MessagePriority.HIGH,
        "collaboration_urgent_match": MessagePriority.HIGH,
        "seo_trending_optimization": MessagePriority.HIGH,
        "revenue_calculation_urgent": MessagePriority.HIGH,
        "live_stream_processing": MessagePriority.HIGH,
        
        # Normal priority events
        "content_upload": MessagePriority.NORMAL,
        "collaboration_match": MessagePriority.NORMAL,
        "analytics_processing": MessagePriority.NORMAL,
        "seo_optimization": MessagePriority.NORMAL,
        "user_notification": MessagePriority.NORMAL,
        
        # Low priority events
        "background_analytics": MessagePriority.LOW,
        "cleanup_tasks": MessagePriority.LOW,
        "archive_old_content": MessagePriority.LOW,
        "batch_reporting": MessagePriority.LOW,
        "maintenance_tasks": MessagePriority.LOW
    }
    
    # SLA requirements by priority
    SLA_REQUIREMENTS = {
        MessagePriority.CRITICAL: SLALevel.PLATINUM,  # < 1s
        MessagePriority.HIGH: SLALevel.GOLD,         # < 5s
        MessagePriority.NORMAL: SLALevel.SILVER,     # < 30s
        MessagePriority.LOW: SLALevel.BRONZE         # < 300s
    }
    
    # Priority weights for weighted fair scheduling
    PRIORITY_WEIGHTS = {
        MessagePriority.CRITICAL: 10,
        MessagePriority.HIGH: 5,
        MessagePriority.NORMAL: 2,
        MessagePriority.LOW: 1
    }
    
    # Aging factors to prevent starvation
    AGING_THRESHOLDS = {
        MessagePriority.HIGH: 300,    # 5 minutes
        MessagePriority.NORMAL: 900,  # 15 minutes
        MessagePriority.LOW: 3600     # 1 hour
    }


class PriorityQueueManager:
    """
    Intelligent priority queue management with fair scheduling and SLA enforcement
    Prevents starvation while maintaining priority guarantees
    """
    
    def __init__(self,
                 algorithm -> None: SchedulingAlgorithm = SchedulingAlgorithm.WEIGHTED_FAIR,
                 metrics_collector -> None: Optional[MetricsCollector] = None,
                 encryption_manager -> None: Optional[EncryptionManager] = None) -> None:
        self.algorithm = algorithm
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Priority queues per level
        self.priority_queues = {
            priority: [] for priority in MessagePriority
        }
        
        # Queue metrics
        self.queue_metrics = {}
        self.global_metrics = QueueMetrics("global")
        
        # Scheduling state
        self.round_robin_state = {priority: 0 for priority in MessagePriority}
        self.weight_counters = {priority: 0 for priority in MessagePriority}
        
        # SLA monitoring
        self.sla_violations = defaultdict(list)
        self.sla_stats = {}
        
        # Aging mechanism
        self.aging_enabled = True
        self.last_aging_check = time.time()
        
        logger.info(f"Initialized Priority Queue Manager with {algorithm.value} algorithm")
    
    async def enqueue_message(self, message: PriorityMessage) -> bool:
        """Enqueue message with dynamic priority calculation"""
        try:
            # Calculate dynamic priority
            dynamic_priority = await self._calculate_dynamic_priority(message)
            message.priority = dynamic_priority
            
            # Apply business context
            await self._apply_business_context(message)
            
            # Encrypt if needed
            if self.encryption:
                message.payload = await self._encrypt_payload(message.payload)
            
            # Add to appropriate priority queue
            heapq.heappush(self.priority_queues[message.priority], message)
            
            # Update metrics
            await self._update_enqueue_metrics(message)
            
            logger.debug(f"Enqueued message {message.id} with priority {message.priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error enqueuing message: {str(e)}")
            raise MessageQueueError(f"Failed to enqueue message: {str(e)}")
    
    async def dequeue_message(self, queue_name: str = "") -> Optional[PriorityMessage]:
        """Dequeue message using configured scheduling algorithm"""
        try:
            # Apply aging if enabled
            if self.aging_enabled:
                await self._apply_aging_mechanism()
            
            # Select message based on algorithm
            message = None
            if self.algorithm == SchedulingAlgorithm.PRIORITY_STRICT:
                message = await self._dequeue_strict_priority()
            elif self.algorithm == SchedulingAlgorithm.WEIGHTED_FAIR:
                message = await self._dequeue_weighted_fair()
            elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
                message = await self._dequeue_round_robin()
            elif self.algorithm == SchedulingAlgorithm.DEADLINE_AWARE:
                message = await self._dequeue_deadline_aware()
            
            if message:
                # Calculate wait time
                message.wait_time = time.time() - message.enqueue_time
                
                # Decrypt if needed
                if self.encryption:
                    message.payload = await self._decrypt_payload(message.payload)
                
                # Update metrics
                await self._update_dequeue_metrics(message)
                
                logger.debug(f"Dequeued message {message.id} with wait time {message.wait_time:.2f}s")
            
            return message
            
        except Exception as e:
            logger.error(f"Error dequeuing message: {str(e)}")
            raise MessageQueueError(f"Failed to dequeue message: {str(e)}")
    
    async def acknowledge_message(self, message: PriorityMessage, processing_time: float) -> bool:
        """Acknowledge successful message processing"""
        try:
            message.processing_time = processing_time
            
            # Check SLA compliance
            await self._check_sla_compliance(message)
            
            # Update metrics
            await self._update_ack_metrics(message)
            
            logger.debug(f"Acknowledged message {message.id} with processing time {processing_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging message: {str(e)}")
            return False
    
    async def nack_message(self, message: PriorityMessage, reason: str = "") -> bool:
        """Negative acknowledge - handle retry or DLQ"""
        try:
            message.retry_count += 1
            
            # Apply retry penalty (lower priority)
            if message.retry_count > 0:
                penalty_priority = min(message.priority.value + 1, 3)
                message.priority = MessagePriority(penalty_priority)
            
            # Re-enqueue if under retry limit
            max_retries = 3
            if message.retry_count <= max_retries:
                # Add back to queue with lower priority
                heapq.heappush(self.priority_queues[message.priority], message)
                logger.info(f"Re-queued message {message.id} for retry {message.retry_count}")
            else:
                # Move to DLQ
                await self._move_to_dlq(message, reason)
                logger.warning(f"Message {message.id} moved to DLQ after {message.retry_count} retries")
            
            # Update metrics
            await self._update_nack_metrics(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error negative acknowledging message: {str(e)}")
            return False
    
    async def get_queue_statistics(self, queue_name: str = "") -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        try:
            stats = {
                "queue_name": queue_name or "all",
                "scheduling_algorithm": self.algorithm.value,
                "priority_distribution": await self._get_priority_distribution(),
                "queue_depths": await self._get_queue_depths(),
                "average_wait_times": await self._get_average_wait_times(),
                "throughput_metrics": await self._get_throughput_metrics(),
                "sla_compliance": await self._get_sla_compliance(),
                "aging_statistics": await self._get_aging_statistics(),
                "performance_summary": await self._get_performance_summary()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting queue statistics: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_queue_performance(self) -> Dict[str, Any]:
        """Analyze and optimize queue performance"""
        try:
            optimization_results = {}
            
            # Analyze queue balance
            balance_analysis = await self._analyze_queue_balance()
            optimization_results["queue_balance"] = balance_analysis
            
            # Detect bottlenecks
            bottlenecks = await self._detect_bottlenecks()
            optimization_results["bottlenecks"] = bottlenecks
            
            # Suggest algorithm adjustments
            algorithm_suggestions = await self._suggest_algorithm_adjustments()
            optimization_results["algorithm_suggestions"] = algorithm_suggestions
            
            # Apply automatic optimizations
            auto_optimizations = await self._apply_auto_optimizations()
            optimization_results["auto_optimizations"] = auto_optimizations
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing queue performance: {str(e)}")
            return {"error": str(e)}
    
    # Scheduling algorithm implementations
    
    async def _dequeue_strict_priority(self) -> Optional[PriorityMessage]:
        """Strict priority scheduling - highest priority first"""
        for priority in MessagePriority:
            if self.priority_queues[priority]:
                return heapq.heappop(self.priority_queues[priority])
        return None
    
    async def _dequeue_weighted_fair(self) -> Optional[PriorityMessage]:
        """Weighted fair scheduling with priority weights"""
        # Find priority with highest weight counter that has messages
        best_priority = None
        best_weight = -1
        
        for priority in MessagePriority:
            if self.priority_queues[priority]:
                weight = AinflueBusiness.PRIORITY_WEIGHTS[priority]
                current_weight = self.weight_counters[priority] + weight
                
                if current_weight > best_weight:
                    best_weight = current_weight
                    best_priority = priority
        
        if best_priority:
            # Dequeue from selected priority
            message = heapq.heappop(self.priority_queues[best_priority])
            
            # Reset counter for selected priority, increment others
            self.weight_counters[best_priority] = 0
            for priority in MessagePriority:
                if priority != best_priority and self.priority_queues[priority]:
                    self.weight_counters[priority] += AinflueBusiness.PRIORITY_WEIGHTS[priority]
            
            return message
        
        return None
    
    async def _dequeue_round_robin(self) -> Optional[PriorityMessage]:
        """Round robin scheduling across priority levels"""
        # Try each priority starting from current position
        priorities = list(MessagePriority)
        start_index = self.round_robin_state[MessagePriority.CRITICAL]
        
        for i in range(len(priorities)):
            priority_index = (start_index + i) % len(priorities)
            priority = priorities[priority_index]
            
            if self.priority_queues[priority]:
                message = heapq.heappop(self.priority_queues[priority])
                
                # Update round robin state
                self.round_robin_state[MessagePriority.CRITICAL] = (priority_index + 1) % len(priorities)
                
                return message
        
        return None
    
    async def _dequeue_deadline_aware(self) -> Optional[PriorityMessage]:
        """Deadline-aware scheduling considering message deadlines"""
        current_time = datetime.now(timezone.utc)
        candidates = []
        
        # Collect all messages with deadlines
        for priority in MessagePriority:
            for message in self.priority_queues[priority]:
                if message.deadline:
                    time_to_deadline = (message.deadline - current_time).total_seconds()
                    candidates.append((time_to_deadline, message, priority))
        
        # If we have deadline messages, prioritize by urgency
        if candidates:
            candidates.sort(key=lambda x: x[0])  # Sort by time to deadline
            
            # Take most urgent message
            _, message, priority = candidates[0]
            self.priority_queues[priority].remove(message)
            heapq.heapify(self.priority_queues[priority])  # Re-heapify
            
            return message
        
        # Fall back to strict priority if no deadlines
        return await self._dequeue_strict_priority()
    
    # Helper methods
    
    async def _calculate_dynamic_priority(self, message: PriorityMessage) -> MessagePriority:
        """Calculate dynamic priority based on business context"""
        event_type = message.payload.get("event_type", "")
        business_context = message.business_context
        
        # Get base priority from business rules
        base_priority = AinflueBusiness.PRIORITY_RULES.get(event_type, MessagePriority.NORMAL)
        
        # Apply business context adjustments
        priority_value = base_priority.value
        
        # Premium creators get priority boost
        if business_context.get("creator_tier") == "premium":
            priority_value = max(priority_value - 1, 0)
        
        # Urgent events get priority boost
        if business_context.get("urgency") == "urgent":
            priority_value = max(priority_value - 1, 0)
        
        # Events with deadlines get priority boost based on urgency
        if message.deadline:
            time_to_deadline = (message.deadline - datetime.now(timezone.utc)).total_seconds()
            if time_to_deadline < 300:  # 5 minutes
                priority_value = max(priority_value - 1, 0)
        
        # Retry penalty
        if message.retry_count > 0:
            priority_value = min(priority_value + 1, 3)
        
        return MessagePriority(priority_value)
    
    async def _apply_business_context(self, message -> None: PriorityMessage) -> None:
        """Apply Ainflue business context to message"""
        event_type = message.payload.get("event_type", "")
        
        # Set SLA level based on priority
        message.sla_level = AinflueBusiness.SLA_REQUIREMENTS.get(
            message.priority, SLALevel.BRONZE
        )
        
        # Set deadline for time-sensitive events
        if event_type in ["payment_processing", "live_stream_processing"]:
            message.deadline = datetime.now(timezone.utc) + timedelta(minutes=5)
        elif event_type.startswith("collaboration_urgent"):
            message.deadline = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    async def _apply_aging_mechanism(self) -> None:
        """Apply aging to prevent starvation of lower priority messages"""
        current_time = time.time()
        
        # Only check aging periodically
        if current_time - self.last_aging_check < 60:  # Check every minute
            return
        
        self.last_aging_check = current_time
        
        for priority in [MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]:
            threshold = AinflueBusiness.AGING_THRESHOLDS.get(priority, 3600)
            
            # Check messages in this priority queue
            aged_messages = []
            remaining_messages = []
            
            for message in self.priority_queues[priority]:
                wait_time = current_time - message.enqueue_time
                
                if wait_time > threshold:
                    # Promote to higher priority
                    if priority.value > 0:
                        message.priority = MessagePriority(priority.value - 1)
                        message.aging_factor *= 1.5
                        aged_messages.append(message)
                    else:
                        remaining_messages.append(message)
                else:
                    remaining_messages.append(message)
            
            # Update queue
            self.priority_queues[priority] = remaining_messages
            heapq.heapify(self.priority_queues[priority])
            
            # Add aged messages to higher priority queue
            for message in aged_messages:
                heapq.heappush(self.priority_queues[message.priority], message)
                logger.debug(f"Aged message {message.id} from {priority.name} to {message.priority.name}")
    
    async def _check_sla_compliance(self, message -> None: PriorityMessage) -> None:
        """Check SLA compliance for processed message"""
        total_time = message.wait_time + message.processing_time
        
        # SLA thresholds in seconds
        sla_thresholds = {
            SLALevel.PLATINUM: 1.0,
            SLALevel.GOLD: 5.0,
            SLALevel.SILVER: 30.0,
            SLALevel.BRONZE: 300.0
        }
        
        threshold = sla_thresholds.get(message.sla_level, 300.0)
        
        if total_time > threshold:
            # SLA violation
            violation = {
                "message_id": message.id,
                "sla_level": message.sla_level.value,
                "threshold": threshold,
                "actual_time": total_time,
                "violation_time": datetime.now(timezone.utc),
                "priority": message.priority.name
            }
            
            self.sla_violations[message.sla_level].append(violation)
            logger.warning(f"SLA violation: {violation}")
    
    async def _encrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt message payload"""
        # Placeholder for encryption
        return payload
    
    async def _decrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt message payload"""
        # Placeholder for decryption
        return payload
    
    async def _move_to_dlq(self, message -> None: PriorityMessage, reason -> None: str) -> None:
        """Move message to dead letter queue"""
        dlq_entry = {
            "message_id": message.id,
            "original_priority": message.priority.name,
            "retry_count": message.retry_count,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.warning(f"Message moved to DLQ: {dlq_entry}")
    
    # Metrics and statistics methods
    
    async def _update_enqueue_metrics(self, message -> None: PriorityMessage) -> None:
        """Update enqueue metrics"""
        self.global_metrics.total_messages += 1
        
        priority_name = message.priority.name
        if priority_name not in self.global_metrics.priority_distribution:
            self.global_metrics.priority_distribution[priority_name] = 0
        self.global_metrics.priority_distribution[priority_name] += 1
    
    async def _update_dequeue_metrics(self, message -> None: PriorityMessage) -> None:
        """Update dequeue metrics"""
        # Update wait time average
        total_wait = self.global_metrics.avg_wait_time * self.global_metrics.processed_messages
        total_wait += message.wait_time
        self.global_metrics.processed_messages += 1
        self.global_metrics.avg_wait_time = total_wait / self.global_metrics.processed_messages
    
    async def _update_ack_metrics(self, message -> None: PriorityMessage) -> None:
        """Update acknowledge metrics"""
        # Update processing time average
        total_processing = self.global_metrics.avg_processing_time * (self.global_metrics.processed_messages - 1)
        total_processing += message.processing_time
        self.global_metrics.avg_processing_time = total_processing / self.global_metrics.processed_messages
    
    async def _update_nack_metrics(self, message -> None: PriorityMessage) -> None:
        """Update negative acknowledge metrics"""
        self.global_metrics.failed_messages += 1
    
    async def _get_priority_distribution(self) -> Dict[str, int]:
        """Get current priority distribution"""
        distribution = {}
        for priority in MessagePriority:
            distribution[priority.name] = len(self.priority_queues[priority])
        return distribution
    
    async def _get_queue_depths(self) -> Dict[str, int]:
        """Get queue depths by priority"""
        return await self._get_priority_distribution()
    
    async def _get_average_wait_times(self) -> Dict[str, float]:
        """Get average wait times by priority"""
        # Placeholder - would calculate from recent history
        return {priority.name: 0.0 for priority in MessagePriority}
    
    async def _get_throughput_metrics(self) -> Dict[str, float]:
        """Get throughput metrics"""
        return {
            "messages_per_minute": self.global_metrics.throughput_per_minute,
            "total_processed": self.global_metrics.processed_messages,
            "total_failed": self.global_metrics.failed_messages
        }
    
    async def _get_sla_compliance(self) -> Dict[str, Any]:
        """Get SLA compliance statistics"""
        compliance_stats = {}
        
        for sla_level in SLALevel:
            violations = len(self.sla_violations.get(sla_level, []))
            total_messages = self.global_metrics.processed_messages
            
            if total_messages > 0:
                compliance_rate = ((total_messages - violations) / total_messages) * 100
            else:
                compliance_rate = 100.0
            
            compliance_stats[sla_level.value] = {
                "compliance_rate": round(compliance_rate, 2),
                "violations": violations,
                "total_messages": total_messages
            }
        
        return compliance_stats
    
    async def _get_aging_statistics(self) -> Dict[str, Any]:
        """Get aging mechanism statistics"""
        current_time = time.time()
        aging_stats = {}
        
        for priority in MessagePriority:
            aged_count = 0
            total_wait = 0
            
            for message in self.priority_queues[priority]:
                wait_time = current_time - message.enqueue_time
                total_wait += wait_time
                
                threshold = AinflueBusiness.AGING_THRESHOLDS.get(priority, 3600)
                if wait_time > threshold:
                    aged_count += 1
            
            queue_size = len(self.priority_queues[priority])
            avg_wait = total_wait / queue_size if queue_size > 0 else 0
            
            aging_stats[priority.name] = {
                "eligible_for_aging": aged_count,
                "average_wait_time": round(avg_wait, 2),
                "queue_size": queue_size
            }
        
        return aging_stats
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        return {
            "total_queued": sum(len(q) for q in self.priority_queues.values()),
            "total_processed": self.global_metrics.processed_messages,
            "success_rate": (
                (self.global_metrics.processed_messages - self.global_metrics.failed_messages) /
                max(self.global_metrics.processed_messages, 1)
            ) * 100,
            "average_wait_time": round(self.global_metrics.avg_wait_time, 2),
            "average_processing_time": round(self.global_metrics.avg_processing_time, 2)
        }
    
    # Optimization methods
    
    async def _analyze_queue_balance(self) -> Dict[str, Any]:
        """Analyze queue balance across priorities"""
        depths = await self._get_queue_depths()
        total_depth = sum(depths.values())
        
        if total_depth == 0:
            return {"balanced": True, "analysis": "All queues empty"}
        
        # Check for imbalance
        high_priority_ratio = (depths["CRITICAL"] + depths["HIGH"]) / total_depth
        low_priority_ratio = depths["LOW"] / total_depth
        
        analysis = {
            "balanced": 0.1 <= high_priority_ratio <= 0.5 and low_priority_ratio <= 0.4,
            "high_priority_ratio": round(high_priority_ratio, 2),
            "low_priority_ratio": round(low_priority_ratio, 2),
            "recommendations": []
        }
        
        if high_priority_ratio > 0.7:
            analysis["recommendations"].append("Consider increasing worker capacity for high priority queues")
        
        if low_priority_ratio > 0.5:
            analysis["recommendations"].append("Low priority queue backlog detected - consider aging adjustment")
        
        return analysis
    
    async def _detect_bottlenecks(self) -> List[str]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        # Check queue depths
        depths = await self._get_queue_depths()
        for priority, depth in depths.items():
            if depth > 1000:  # Threshold for bottleneck
                bottlenecks.append(f"High queue depth in {priority} priority: {depth} messages")
        
        # Check SLA violations
        violations = self.sla_violations
        for sla_level, violation_list in violations.items():
            if len(violation_list) > 10:  # Threshold for concern
                bottlenecks.append(f"Excessive SLA violations in {sla_level.value}: {len(violation_list)}")
        
        # Check average wait times
        if self.global_metrics.avg_wait_time > 60:  # 1 minute threshold
            bottlenecks.append(f"High average wait time: {self.global_metrics.avg_wait_time:.2f}s")
        
        return bottlenecks
    
    async def _suggest_algorithm_adjustments(self) -> List[str]:
        """Suggest algorithm adjustments based on performance"""
        suggestions = []
        
        # Analyze current algorithm performance
        if self.algorithm == SchedulingAlgorithm.PRIORITY_STRICT:
            low_priority_depth = len(self.priority_queues[MessagePriority.LOW])
            if low_priority_depth > 500:
                suggestions.append("Consider switching to WEIGHTED_FAIR to prevent low priority starvation")
        
        elif self.algorithm == SchedulingAlgorithm.WEIGHTED_FAIR:
            sla_violations = sum(len(v) for v in self.sla_violations.values())
            if sla_violations > 50:
                suggestions.append("Consider switching to PRIORITY_STRICT for better SLA compliance")
        
        # Check aging effectiveness
        if self.aging_enabled:
            aging_stats = await self._get_aging_statistics()
            total_eligible = sum(stats["eligible_for_aging"] for stats in aging_stats.values())
            if total_eligible > 100:
                suggestions.append("Consider reducing aging thresholds to prevent message starvation")
        
        return suggestions
    
    async def _apply_auto_optimizations(self) -> List[str]:
        """Apply automatic optimizations"""
        optimizations = []
        
        # Auto-adjust aging thresholds
        aging_stats = await self._get_aging_statistics()
        for priority_name, stats in aging_stats.items():
            if stats["eligible_for_aging"] > 50:
                priority = MessagePriority[priority_name]
                if priority in AinflueBusiness.AGING_THRESHOLDS:
                    # Reduce threshold by 20%
                    current_threshold = AinflueBusiness.AGING_THRESHOLDS[priority]
                    new_threshold = int(current_threshold * 0.8)
                    AinflueBusiness.AGING_THRESHOLDS[priority] = new_threshold
                    optimizations.append(f"Reduced aging threshold for {priority_name} to {new_threshold}s")
        
        # Auto-adjust priority weights
        depths = await self._get_queue_depths()
        if depths["LOW"] > 1000 and self.algorithm == SchedulingAlgorithm.WEIGHTED_FAIR:
            # Increase low priority weight
            AinflueBusiness.PRIORITY_WEIGHTS[MessagePriority.LOW] = 2
            optimizations.append("Increased LOW priority weight to reduce backlog")
        
        return optimizations


# Export for public API
__all__ = [
    "PriorityQueueManager",
    "PriorityMessage",
    "QueueMetrics",
    "MessagePriority",
    "SchedulingAlgorithm",
    "SLALevel",
    "AinflueBusiness"
]