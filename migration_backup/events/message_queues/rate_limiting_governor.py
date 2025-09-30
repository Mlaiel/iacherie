"""Rate Limiting Governor Module

Advanced rate limiting and throttling with intelligent quota management
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Rate Limiting Governor architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import math

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    ADAPTIVE = "adaptive"


class QuotaTimeframe(Enum):
    """Quota timeframes"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"


class RateLimitAction(Enum):
    """Actions to take when rate limit is exceeded"""
    REJECT = "reject"
    QUEUE = "queue"
    THROTTLE = "throttle"
    ESCALATE = "escalate"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    
    # Rate limits
    requests_per_second: float = 100.0
    requests_per_minute: float = 1000.0
    requests_per_hour: float = 10000.0
    requests_per_day: float = 100000.0
    
    # Burst handling
    burst_capacity: int = 200
    burst_refill_rate: float = 10.0  # tokens per second
    
    # Quota management
    quota_timeframe: QuotaTimeframe = QuotaTimeframe.MINUTE
    quota_limit: int = 1000
    
    # Actions
    action_on_limit: RateLimitAction = RateLimitAction.QUEUE
    backoff_duration: float = 60.0  # seconds
    
    # Priority handling
    priority_multiplier: Dict[str, float] = field(default_factory=lambda: {
        "critical": 2.0,
        "high": 1.5,
        "normal": 1.0,
        "low": 0.5
    })
    
    # Business context
    applies_to: List[str] = field(default_factory=list)  # Event types or user tiers
    exemptions: List[str] = field(default_factory=list)  # Exempt identifiers
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class RateLimitState:
    """Current state of rate limiting for an entity"""
    entity_id: str
    rule_id: str
    
    # Token bucket state
    tokens: float = 0.0
    last_refill: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Window tracking
    current_window_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_window_count: int = 0
    
    # Sliding window (for more precise tracking)
    request_timestamps: deque = field(default_factory=lambda: deque(maxlen=10000))
    
    # Quota tracking
    quota_usage: Dict[str, int] = field(default_factory=dict)  # timeframe -> count
    quota_reset_times: Dict[str, datetime] = field(default_factory=dict)
    
    # Statistics
    total_requests: int = 0
    total_allowed: int = 0
    total_rejected: int = 0
    total_queued: int = 0
    
    last_request_time: Optional[datetime] = None
    last_rejected_time: Optional[datetime] = None


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    total_requests: int = 0
    total_allowed: int = 0
    total_rejected: int = 0
    total_queued: int = 0
    avg_response_time: float = 0.0
    rejection_rate: float = 0.0
    queue_depth: int = 0
    active_entities: int = 0


class AinflueBusiness:
    """Ainflue Business Rate Limiting Rules"""
    
    # Rate limiting rules by context
    RATE_LIMIT_RULES = {
        # Content upload limits
        "content_upload": RateLimitRule(
            name="Content Upload Rate Limit",
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_second=2.0,
            requests_per_minute=50.0,
            requests_per_hour=500.0,
            requests_per_day=2000.0,
            burst_capacity=10,
            burst_refill_rate=2.0,
            action_on_limit=RateLimitAction.QUEUE,
            applies_to=["content_upload", "video_upload", "audio_upload"]
        ),
        
        # AI processing limits
        "ai_processing": RateLimitRule(
            name="AI Processing Rate Limit",
            algorithm=RateLimitAlgorithm.ADAPTIVE,
            requests_per_second=1.0,
            requests_per_minute=20.0,
            requests_per_hour=200.0,
            requests_per_day=1000.0,
            burst_capacity=5,
            action_on_limit=RateLimitAction.THROTTLE,
            applies_to=["ai_content_analysis", "ai_generation", "ml_inference"]
        ),
        
        # Payment processing limits (strict)
        "payment_processing": RateLimitRule(
            name="Payment Processing Rate Limit",
            algorithm=RateLimitAlgorithm.LEAKY_BUCKET,
            requests_per_second=0.5,
            requests_per_minute=10.0,
            requests_per_hour=100.0,
            requests_per_day=500.0,
            burst_capacity=2,
            action_on_limit=RateLimitAction.REJECT,
            applies_to=["payment_process", "payout_request", "refund_process"]
        ),
        
        # Collaboration matching limits
        "collaboration": RateLimitRule(
            name="Collaboration Rate Limit",
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            requests_per_second=5.0,
            requests_per_minute=100.0,
            requests_per_hour=1000.0,
            burst_capacity=20,
            action_on_limit=RateLimitAction.QUEUE,
            applies_to=["collaboration_match", "collaboration_request"]
        ),
        
        # API access limits by user tier
        "api_standard": RateLimitRule(
            name="Standard API Rate Limit",
            algorithm=RateLimitAlgorithm.FIXED_WINDOW,
            requests_per_second=10.0,
            requests_per_minute=300.0,
            requests_per_hour=5000.0,
            requests_per_day=50000.0,
            burst_capacity=50,
            action_on_limit=RateLimitAction.THROTTLE,
            applies_to=["api_request"]
        ),
        
        "api_premium": RateLimitRule(
            name="Premium API Rate Limit",
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_second=50.0,
            requests_per_minute=1500.0,
            requests_per_hour=25000.0,
            requests_per_day=500000.0,
            burst_capacity=200,
            action_on_limit=RateLimitAction.QUEUE,
            applies_to=["api_request"],
            priority_multiplier={
                "critical": 3.0,
                "high": 2.0,
                "normal": 1.0,
                "low": 0.8
            }
        ),
        
        # Analytics processing limits
        "analytics": RateLimitRule(
            name="Analytics Processing Rate Limit",
            algorithm=RateLimitAlgorithm.ADAPTIVE,
            requests_per_second=20.0,
            requests_per_minute=600.0,
            requests_per_hour=10000.0,
            burst_capacity=100,
            action_on_limit=RateLimitAction.QUEUE,
            applies_to=["analytics_request", "report_generation"]
        )
    }
    
    # Entity identification rules
    ENTITY_IDENTIFICATION = {
        "user_id": lambda context: context.get("user_id", "anonymous"),
        "creator_id": lambda context: context.get("creator_id", "unknown"),
        "ip_address": lambda context: context.get("ip_address", "0.0.0.0"),
        "api_key": lambda context: context.get("api_key", "default"),
        "session_id": lambda context: context.get("session_id", "default")
    }
    
    # Priority detection rules
    PRIORITY_DETECTION = {
        "payment_processing": "critical",
        "security_alert": "critical",
        "content_copyright_violation": "critical",
        "premium_content_upload": "high",
        "collaboration_urgent": "high",
        "ai_content_analysis": "normal",
        "analytics_request": "low",
        "background_task": "low"
    }
    
    # Exemption rules
    EXEMPTIONS = {
        "system_internal": ["system", "admin", "monitoring"],
        "premium_users": [],  # Populated from database
        "api_partners": []    # Populated from configuration
    }


class RateLimitingGovernor:
    """
    Advanced rate limiting and throttling with intelligent quota management
    Supports multiple algorithms and adaptive rate limiting
    """
    
    def __init__(self,
                 metrics_collector: Optional[MetricsCollector] = None,
                 encryption_manager: Optional[EncryptionManager] = None):
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Rate limiting state
        self.rate_limit_rules = {}  # rule_id -> RateLimitRule
        self.entity_states = {}     # entity_id -> {rule_id -> RateLimitState}
        self.queued_requests = defaultdict(deque)  # rule_id -> deque of queued requests
        
        # Global metrics
        self.global_metrics = RateLimitMetrics()
        
        # Adaptive algorithm state
        self.adaptive_states = {}  # rule_id -> adaptive parameters
        
        # Background tasks
        self.cleanup_task = None
        self.queue_processor_task = None
        self.is_running = False
        
        # Configuration
        self.cleanup_interval = 300.0  # 5 minutes
        self.queue_process_interval = 1.0  # 1 second
        
        logger.info("Initialized Rate Limiting Governor")
    
    async def start(self) -> bool:
        """Start the rate limiting governor"""
        try:
            if self.is_running:
                return True
            
            # Load business rules
            await self._load_business_rules()
            
            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.queue_processor_task = asyncio.create_task(self._queue_processor_loop())
            
            self.is_running = True
            logger.info("Rate Limiting Governor started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start rate limiting governor: {str(e)}")
            raise MessageQueueError(f"Rate limiter startup failed: {str(e)}")
    
    async def stop(self):
        """Stop the rate limiting governor"""
        try:
            self.is_running = False
            
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            if self.queue_processor_task:
                self.queue_processor_task.cancel()
            
            logger.info("Rate Limiting Governor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping rate limiting governor: {str(e)}")
    
    async def check_rate_limit(self,
                             entity_id: str,
                             event_type: str,
                             context: Dict[str, Any] = None) -> Tuple[bool, str, Optional[float]]:
        """Check if request is within rate limits"""
        try:
            context = context or {}
            
            # Find applicable rules
            applicable_rules = await self._find_applicable_rules(event_type, context)
            
            if not applicable_rules:
                # No rate limiting rules apply
                return True, "no_rules", None
            
            # Check each applicable rule
            for rule in applicable_rules:
                allowed, reason, wait_time = await self._check_rule(entity_id, rule, context)
                
                if not allowed:
                    # Rate limit exceeded
                    await self._handle_rate_limit_exceeded(entity_id, rule, reason, context)
                    return False, reason, wait_time
            
            # All rules passed
            await self._record_allowed_request(entity_id, applicable_rules, context)
            return True, "allowed", None
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return False, "error", None
    
    async def register_rate_limit_rule(self, rule: RateLimitRule) -> str:
        """Register a new rate limiting rule"""
        try:
            self.rate_limit_rules[rule.rule_id] = rule
            
            # Initialize adaptive state if needed
            if rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
                await self._initialize_adaptive_state(rule.rule_id)
            
            logger.info(f"Registered rate limit rule: {rule.name}")
            return rule.rule_id
            
        except Exception as e:
            logger.error(f"Error registering rate limit rule: {str(e)}")
            raise MessageQueueError(f"Failed to register rule: {str(e)}")
    
    async def update_rate_limit_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing rate limiting rule"""
        try:
            if rule_id not in self.rate_limit_rules:
                return False
            
            rule = self.rate_limit_rules[rule_id]
            
            # Update rule attributes
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            logger.info(f"Updated rate limit rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rate limit rule: {str(e)}")
            return False
    
    async def get_rate_limit_status(self, entity_id: str) -> Dict[str, Any]:
        """Get current rate limit status for an entity"""
        try:
            if entity_id not in self.entity_states:
                return {"entity_id": entity_id, "rules": {}, "status": "no_activity"}
            
            entity_rules = self.entity_states[entity_id]
            status = {}
            
            for rule_id, state in entity_rules.items():
                rule = self.rate_limit_rules.get(rule_id)
                if not rule:
                    continue
                
                # Calculate current status
                current_tokens = await self._calculate_current_tokens(state, rule)
                quota_status = await self._get_quota_status(state, rule)
                
                status[rule_id] = {
                    "rule_name": rule.name,
                    "algorithm": rule.algorithm.value,
                    "current_tokens": current_tokens,
                    "burst_capacity": rule.burst_capacity,
                    "quota_status": quota_status,
                    "total_requests": state.total_requests,
                    "total_allowed": state.total_allowed,
                    "total_rejected": state.total_rejected,
                    "last_request": state.last_request_time.isoformat() if state.last_request_time else None
                }
            
            return {
                "entity_id": entity_id,
                "rules": status,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            return {"error": str(e)}
    
    async def get_global_metrics(self) -> Dict[str, Any]:
        """Get global rate limiting metrics"""
        try:
            # Calculate additional metrics
            if self.global_metrics.total_requests > 0:
                self.global_metrics.rejection_rate = (
                    self.global_metrics.total_rejected / self.global_metrics.total_requests
                ) * 100
            
            # Count active entities
            self.global_metrics.active_entities = len(self.entity_states)
            
            # Count queue depth
            total_queued = sum(len(queue) for queue in self.queued_requests.values())
            self.global_metrics.queue_depth = total_queued
            
            return {
                "total_requests": self.global_metrics.total_requests,
                "total_allowed": self.global_metrics.total_allowed,
                "total_rejected": self.global_metrics.total_rejected,
                "total_queued": self.global_metrics.total_queued,
                "rejection_rate": round(self.global_metrics.rejection_rate, 2),
                "queue_depth": self.global_metrics.queue_depth,
                "active_entities": self.global_metrics.active_entities,
                "active_rules": len(self.rate_limit_rules),
                "avg_response_time": round(self.global_metrics.avg_response_time, 3)
            }
            
        except Exception as e:
            logger.error(f"Error getting global metrics: {str(e)}")
            return {"error": str(e)}
    
    async def get_rule_performance(self, rule_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for rules"""
        try:
            if rule_id:
                # Specific rule performance
                if rule_id not in self.rate_limit_rules:
                    return {"error": "Rule not found"}
                
                rule = self.rate_limit_rules[rule_id]
                
                # Aggregate stats across all entities for this rule
                total_requests = 0
                total_allowed = 0
                total_rejected = 0
                
                for entity_states in self.entity_states.values():
                    if rule_id in entity_states:
                        state = entity_states[rule_id]
                        total_requests += state.total_requests
                        total_allowed += state.total_allowed
                        total_rejected += state.total_rejected
                
                return {
                    "rule_id": rule_id,
                    "rule_name": rule.name,
                    "algorithm": rule.algorithm.value,
                    "total_requests": total_requests,
                    "total_allowed": total_allowed,
                    "total_rejected": total_rejected,
                    "rejection_rate": (total_rejected / max(total_requests, 1)) * 100,
                    "queue_depth": len(self.queued_requests.get(rule_id, [])),
                    "is_active": rule.is_active
                }
            else:
                # All rules performance
                performance = {}
                
                for rule_id, rule in self.rate_limit_rules.items():
                    rule_perf = await self.get_rule_performance(rule_id)
                    if "error" not in rule_perf:
                        performance[rule_id] = rule_perf
                
                return {"rules_performance": performance}
                
        except Exception as e:
            logger.error(f"Error getting rule performance: {str(e)}")
            return {"error": str(e)}
    
    async def clear_entity_state(self, entity_id: str) -> bool:
        """Clear rate limiting state for an entity"""
        try:
            if entity_id in self.entity_states:
                del self.entity_states[entity_id]
                logger.info(f"Cleared rate limit state for entity: {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clearing entity state: {str(e)}")
            return False
    
    # Core rate limiting logic
    
    async def _find_applicable_rules(self, event_type: str, context: Dict[str, Any]) -> List[RateLimitRule]:
        """Find rate limiting rules applicable to the request"""
        applicable_rules = []
        
        for rule in self.rate_limit_rules.values():
            if not rule.is_active:
                continue
            
            # Check if rule applies to this event type
            if rule.applies_to and event_type not in rule.applies_to:
                continue
            
            # Check exemptions
            entity_id = await self._identify_entity(context)
            if await self._is_exempt(entity_id, rule, context):
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _check_rule(self, entity_id: str, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check if request passes a specific rule"""
        # Get or create entity state for this rule
        state = await self._get_entity_state(entity_id, rule.rule_id)
        
        # Check based on algorithm
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._check_token_bucket(state, rule, context)
        elif rule.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            return await self._check_leaky_bucket(state, rule, context)
        elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._check_fixed_window(state, rule, context)
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._check_sliding_window(state, rule, context)
        elif rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return await self._check_adaptive(state, rule, context)
        else:
            return True, "unknown_algorithm", None
    
    async def _check_token_bucket(self, state: RateLimitState, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check token bucket rate limit"""
        current_time = datetime.now(timezone.utc)
        
        # Refill tokens
        time_passed = (current_time - state.last_refill).total_seconds()
        tokens_to_add = time_passed * rule.burst_refill_rate
        state.tokens = min(rule.burst_capacity, state.tokens + tokens_to_add)
        state.last_refill = current_time
        
        # Get priority multiplier
        priority = await self._get_request_priority(context)
        tokens_required = 1.0 / rule.priority_multiplier.get(priority, 1.0)
        
        if state.tokens >= tokens_required:
            state.tokens -= tokens_required
            return True, "allowed", None
        else:
            # Calculate wait time
            tokens_needed = tokens_required - state.tokens
            wait_time = tokens_needed / rule.burst_refill_rate
            return False, "token_bucket_exhausted", wait_time
    
    async def _check_leaky_bucket(self, state: RateLimitState, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check leaky bucket rate limit"""
        current_time = datetime.now(timezone.utc)
        
        # Calculate leak
        time_passed = (current_time - state.last_refill).total_seconds()
        leaked = time_passed * rule.burst_refill_rate
        state.tokens = max(0, state.tokens - leaked)
        state.last_refill = current_time
        
        # Check if bucket has capacity
        if state.tokens < rule.burst_capacity:
            state.tokens += 1
            return True, "allowed", None
        else:
            # Calculate wait time
            wait_time = (state.tokens - rule.burst_capacity + 1) / rule.burst_refill_rate
            return False, "leaky_bucket_full", wait_time
    
    async def _check_fixed_window(self, state: RateLimitState, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check fixed window rate limit"""
        current_time = datetime.now(timezone.utc)
        
        # Check if we need a new window
        window_duration = 60.0  # 1 minute windows
        if (current_time - state.current_window_start).total_seconds() >= window_duration:
            state.current_window_start = current_time
            state.current_window_count = 0
        
        # Check limit
        if state.current_window_count < rule.requests_per_minute:
            state.current_window_count += 1
            return True, "allowed", None
        else:
            # Calculate wait time to next window
            next_window = state.current_window_start + timedelta(seconds=window_duration)
            wait_time = (next_window - current_time).total_seconds()
            return False, "fixed_window_exceeded", wait_time
    
    async def _check_sliding_window(self, state: RateLimitState, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check sliding window rate limit"""
        current_time = datetime.now(timezone.utc)
        
        # Clean old timestamps
        window_duration = 60.0  # 1 minute
        cutoff_time = current_time - timedelta(seconds=window_duration)
        
        while state.request_timestamps and state.request_timestamps[0] < cutoff_time:
            state.request_timestamps.popleft()
        
        # Check limit
        if len(state.request_timestamps) < rule.requests_per_minute:
            state.request_timestamps.append(current_time)
            return True, "allowed", None
        else:
            # Calculate wait time
            oldest_request = state.request_timestamps[0]
            wait_time = (oldest_request + timedelta(seconds=window_duration) - current_time).total_seconds()
            return False, "sliding_window_exceeded", max(0, wait_time)
    
    async def _check_adaptive(self, state: RateLimitState, rule: RateLimitRule, context: Dict[str, Any]) -> Tuple[bool, str, Optional[float]]:
        """Check adaptive rate limit"""
        # Adaptive algorithm adjusts limits based on system load and performance
        adaptive_state = self.adaptive_states.get(rule.rule_id, {})
        
        # Get current system metrics
        current_load = await self._get_system_load()
        
        # Adjust rate limit based on load
        base_limit = rule.requests_per_minute
        if current_load > 0.8:  # High load
            adjusted_limit = base_limit * 0.5
        elif current_load > 0.6:  # Medium load
            adjusted_limit = base_limit * 0.75
        else:  # Low load
            adjusted_limit = base_limit * 1.2
        
        # Use sliding window with adjusted limit
        current_time = datetime.now(timezone.utc)
        window_duration = 60.0
        cutoff_time = current_time - timedelta(seconds=window_duration)
        
        while state.request_timestamps and state.request_timestamps[0] < cutoff_time:
            state.request_timestamps.popleft()
        
        if len(state.request_timestamps) < adjusted_limit:
            state.request_timestamps.append(current_time)
            return True, "allowed", None
        else:
            oldest_request = state.request_timestamps[0]
            wait_time = (oldest_request + timedelta(seconds=window_duration) - current_time).total_seconds()
            return False, "adaptive_limit_exceeded", max(0, wait_time)
    
    # Helper methods
    
    async def _load_business_rules(self):
        """Load Ainflue business rate limiting rules"""
        for rule_name, rule_config in AinflueBusiness.RATE_LIMIT_RULES.items():
            rule_config.rule_id = rule_name
            self.rate_limit_rules[rule_name] = rule_config
            
            if rule_config.algorithm == RateLimitAlgorithm.ADAPTIVE:
                await self._initialize_adaptive_state(rule_name)
        
        logger.info(f"Loaded {len(self.rate_limit_rules)} business rate limiting rules")
    
    async def _identify_entity(self, context: Dict[str, Any]) -> str:
        """Identify the entity for rate limiting"""
        # Try different identification methods
        for method, extractor in AinflueBusiness.ENTITY_IDENTIFICATION.items():
            entity_id = extractor(context)
            if entity_id and entity_id not in ["anonymous", "unknown", "default"]:
                return f"{method}:{entity_id}"
        
        # Fallback to IP address or anonymous
        return f"ip:{context.get('ip_address', 'anonymous')}"
    
    async def _is_exempt(self, entity_id: str, rule: RateLimitRule, context: Dict[str, Any]) -> bool:
        """Check if entity is exempt from rate limiting"""
        # Check rule-specific exemptions
        for exemption in rule.exemptions:
            if exemption in entity_id:
                return True
        
        # Check business exemptions
        for exemption_type, exemption_list in AinflueBusiness.EXEMPTIONS.items():
            for exempt_id in exemption_list:
                if exempt_id in entity_id:
                    return True
        
        return False
    
    async def _get_request_priority(self, context: Dict[str, Any]) -> str:
        """Get request priority from context"""
        event_type = context.get("event_type", "")
        
        # Check business priority rules
        for event_pattern, priority in AinflueBusiness.PRIORITY_DETECTION.items():
            if event_pattern in event_type:
                return priority
        
        # Check explicit priority in context
        return context.get("priority", "normal")
    
    async def _get_entity_state(self, entity_id: str, rule_id: str) -> RateLimitState:
        """Get or create entity state for a rule"""
        if entity_id not in self.entity_states:
            self.entity_states[entity_id] = {}
        
        if rule_id not in self.entity_states[entity_id]:
            rule = self.rate_limit_rules[rule_id]
            state = RateLimitState(
                entity_id=entity_id,
                rule_id=rule_id,
                tokens=rule.burst_capacity  # Start with full bucket
            )
            self.entity_states[entity_id][rule_id] = state
        
        return self.entity_states[entity_id][rule_id]
    
    async def _calculate_current_tokens(self, state: RateLimitState, rule: RateLimitRule) -> float:
        """Calculate current token count"""
        if rule.algorithm not in [RateLimitAlgorithm.TOKEN_BUCKET, RateLimitAlgorithm.LEAKY_BUCKET]:
            return 0.0
        
        current_time = datetime.now(timezone.utc)
        time_passed = (current_time - state.last_refill).total_seconds()
        
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            tokens_to_add = time_passed * rule.burst_refill_rate
            return min(rule.burst_capacity, state.tokens + tokens_to_add)
        else:  # LEAKY_BUCKET
            leaked = time_passed * rule.burst_refill_rate
            return max(0, state.tokens - leaked)
    
    async def _get_quota_status(self, state: RateLimitState, rule: RateLimitRule) -> Dict[str, Any]:
        """Get quota status for different timeframes"""
        current_time = datetime.now(timezone.utc)
        quota_status = {}
        
        for timeframe in QuotaTimeframe:
            # Calculate timeframe duration
            if timeframe == QuotaTimeframe.SECOND:
                duration = timedelta(seconds=1)
                limit = rule.requests_per_second
            elif timeframe == QuotaTimeframe.MINUTE:
                duration = timedelta(minutes=1)
                limit = rule.requests_per_minute
            elif timeframe == QuotaTimeframe.HOUR:
                duration = timedelta(hours=1)
                limit = rule.requests_per_hour
            elif timeframe == QuotaTimeframe.DAY:
                duration = timedelta(days=1)
                limit = rule.requests_per_day
            else:
                continue
            
            # Count requests in timeframe
            cutoff_time = current_time - duration
            count = sum(1 for ts in state.request_timestamps if ts >= cutoff_time)
            
            quota_status[timeframe.value] = {
                "used": count,
                "limit": int(limit),
                "remaining": max(0, int(limit) - count),
                "percentage": (count / max(limit, 1)) * 100
            }
        
        return quota_status
    
    async def _handle_rate_limit_exceeded(self, entity_id: str, rule: RateLimitRule, reason: str, context: Dict[str, Any]):
        """Handle rate limit exceeded based on rule action"""
        state = self.entity_states[entity_id][rule.rule_id]
        
        # Update statistics
        state.total_rejected += 1
        state.last_rejected_time = datetime.now(timezone.utc)
        self.global_metrics.total_rejected += 1
        
        if rule.action_on_limit == RateLimitAction.QUEUE:
            # Queue the request
            queued_request = {
                "entity_id": entity_id,
                "context": context,
                "queued_at": datetime.now(timezone.utc),
                "attempts": 0
            }
            
            self.queued_requests[rule.rule_id].append(queued_request)
            state.total_queued += 1
            self.global_metrics.total_queued += 1
            
            logger.debug(f"Queued request for {entity_id} due to rate limit")
        
        elif rule.action_on_limit == RateLimitAction.ESCALATE:
            # Log for escalation
            logger.warning(f"Rate limit exceeded for {entity_id}, rule: {rule.name}, reason: {reason}")
    
    async def _record_allowed_request(self, entity_id: str, rules: List[RateLimitRule], context: Dict[str, Any]):
        """Record allowed request in statistics"""
        current_time = datetime.now(timezone.utc)
        
        for rule in rules:
            if entity_id in self.entity_states and rule.rule_id in self.entity_states[entity_id]:
                state = self.entity_states[entity_id][rule.rule_id]
                state.total_requests += 1
                state.total_allowed += 1
                state.last_request_time = current_time
        
        self.global_metrics.total_requests += 1
        self.global_metrics.total_allowed += 1
    
    async def _initialize_adaptive_state(self, rule_id: str):
        """Initialize adaptive algorithm state"""
        self.adaptive_states[rule_id] = {
            "load_history": deque(maxlen=100),
            "adjustment_history": deque(maxlen=50),
            "last_adjustment": datetime.now(timezone.utc)
        }
    
    async def _get_system_load(self) -> float:
        """Get current system load (simplified)"""
        # In a real implementation, this would check:
        # - CPU usage
        # - Memory usage
        # - Queue depths
        # - Response times
        # For now, return a mock value
        return 0.5  # 50% load
    
    # Background tasks
    
    async def _cleanup_loop(self):
        """Background cleanup of old state"""
        while self.is_running:
            try:
                await self._cleanup_old_state()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _queue_processor_loop(self):
        """Background processing of queued requests"""
        while self.is_running:
            try:
                await self._process_queued_requests()
                await asyncio.sleep(self.queue_process_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue processor: {str(e)}")
                await asyncio.sleep(5)  # Back off on error
    
    async def _cleanup_old_state(self):
        """Clean up old entity states"""
        current_time = datetime.now(timezone.utc)
        cleanup_threshold = timedelta(hours=24)  # Remove state older than 24 hours
        
        entities_to_remove = []
        
        for entity_id, entity_rules in self.entity_states.items():
            # Check if any state is recent
            has_recent_activity = False
            
            for state in entity_rules.values():
                if (state.last_request_time and 
                    current_time - state.last_request_time < cleanup_threshold):
                    has_recent_activity = True
                    break
            
            if not has_recent_activity:
                entities_to_remove.append(entity_id)
        
        # Remove old entities
        for entity_id in entities_to_remove:
            del self.entity_states[entity_id]
        
        if entities_to_remove:
            logger.info(f"Cleaned up {len(entities_to_remove)} old entity states")
    
    async def _process_queued_requests(self):
        """Process queued requests that may now be allowed"""
        for rule_id, queue in self.queued_requests.items():
            if not queue:
                continue
            
            rule = self.rate_limit_rules.get(rule_id)
            if not rule:
                continue
            
            # Try to process queued requests
            processed = 0
            max_process = min(10, len(queue))  # Process max 10 per cycle
            
            for _ in range(max_process):
                if not queue:
                    break
                
                request = queue[0]  # Peek at first request
                entity_id = request["entity_id"]
                context = request["context"]
                
                # Check if request can now be processed
                allowed, reason, wait_time = await self._check_rule(entity_id, rule, context)
                
                if allowed:
                    # Remove from queue and mark as processed
                    queue.popleft()
                    processed += 1
                    
                    # Update statistics
                    state = self.entity_states[entity_id][rule_id]
                    state.total_allowed += 1
                    state.last_request_time = datetime.now(timezone.utc)
                    
                    # TODO: Actually process the request
                    logger.debug(f"Processed queued request for {entity_id}")
                else:
                    # Still rate limited, check for timeout
                    queued_duration = (datetime.now(timezone.utc) - request["queued_at"]).total_seconds()
                    
                    if queued_duration > rule.backoff_duration * 5:  # Timeout after 5x backoff
                        queue.popleft()  # Remove expired request
                        logger.warning(f"Dropped expired queued request for {entity_id}")
                    else:
                        break  # Stop processing if first request can't be processed
            
            if processed > 0:
                logger.debug(f"Processed {processed} queued requests for rule {rule_id}")


# Export for public API
__all__ = [
    "RateLimitingGovernor",
    "RateLimitRule",
    "RateLimitState",
    "RateLimitMetrics",
    "RateLimitAlgorithm",
    "QuotaTimeframe",
    "RateLimitAction",
    "AinflueBusiness"
]