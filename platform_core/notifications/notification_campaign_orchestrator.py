"""🚀 Notification Campaign Orchestrator - Marketing Automation Enterprise
=========================================================================
Module: platform_core/notifications/notification_campaign_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 NOTIFICATION CAMPAIGN ORCHESTRATOR - MARKETING AUTOMATION
- Campagnes multi-étapes avec workflows complexes
- Trigger conditions basées sur comportement
- Segmentation avancée créateurs
- ROI tracking et optimization automatique
- Multi-channel orchestration intelligente
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import croniter
import redis.asyncio as redis
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class CampaignType(Enum):
    """Campaign types."""
    WELCOME_SERIES = "welcome_series"
    ONBOARDING = "onboarding"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    MILESTONE = "milestone"
    BEHAVIORAL = "behavioral"
    TRANSACTIONAL = "transactional"
    SEASONAL = "seasonal"


class CampaignStatus(Enum):
    """Campaign status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TriggerType(Enum):
    """Campaign trigger types."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    USER_ACTION = "user_action"
    TIME_BASED = "time_based"
    BEHAVIORAL = "behavioral"
    API_TRIGGER = "api_trigger"
    MILESTONE = "milestone"


class ChannelType(Enum):
    """Notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class ConditionOperator(Enum):
    """Condition operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


@dataclass
class CampaignCondition:
    """Campaign trigger condition."""
    field: str
    operator: ConditionOperator
    value: Any
    condition_type: str = "user_property"  # user_property, event, time, custom


@dataclass
class CampaignTrigger:
    """Campaign trigger configuration."""
    id: str
    name: str
    type: TriggerType
    conditions: List[CampaignCondition] = field(default_factory=list)
    delay_minutes: int = 0
    max_triggers_per_user: int = 1
    cooldown_hours: int = 24
    enabled: bool = True


@dataclass
class CampaignStep:
    """Individual step in campaign workflow."""
    id: str
    name: str
    order: int
    template_id: str
    channel: ChannelType
    delay_hours: int = 0
    conditions: List[CampaignCondition] = field(default_factory=list)
    a_b_test_enabled: bool = False
    a_b_test_split: float = 0.5
    alternative_template_id: Optional[str] = None
    enabled: bool = True


@dataclass
class CampaignSegment:
    """Campaign audience segment."""
    id: str
    name: str
    description: str
    conditions: List[CampaignCondition] = field(default_factory=list)
    size_estimate: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CampaignMetrics:
    """Campaign performance metrics."""
    campaign_id: str
    total_targeted: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_converted: int = 0
    total_revenue: float = 0.0
    step_metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    channel_metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Campaign:
    """Marketing campaign configuration."""
    id: str
    name: str
    description: str
    type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    trigger: CampaignTrigger = None
    steps: List[CampaignStep] = field(default_factory=list)
    segments: List[CampaignSegment] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    goals: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metrics: Optional[CampaignMetrics] = None


@dataclass
class CampaignExecution:
    """Campaign execution instance for a user."""
    id: str
    campaign_id: str
    user_id: str
    status: str = "pending"
    current_step: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    step_executions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SegmentBuilder:
    """Dynamic audience segmentation builder."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def build_segment(self, segment: CampaignSegment) -> List[str]:
        """Build user list for segment."""
        try:
            # In production, this would query user database
            # For now, return sample user IDs based on conditions
            
            user_ids = []
            
            # Simulate segment building logic
            for condition in segment.conditions:
                if condition.field == "user_type" and condition.operator == ConditionOperator.EQUALS:
                    if condition.value == "creator":
                        user_ids.extend([f"creator_{i}" for i in range(1000, 1500)])
                    elif condition.value == "brand":
                        user_ids.extend([f"brand_{i}" for i in range(2000, 2200)])
                
                elif condition.field == "signup_date" and condition.operator == ConditionOperator.GREATER_THAN:
                    # Users who signed up after specific date
                    cutoff_date = datetime.fromisoformat(condition.value)
                    if cutoff_date > datetime.utcnow() - timedelta(days=30):
                        user_ids.extend([f"new_user_{i}" for i in range(3000, 3300)])
                
                elif condition.field == "engagement_score" and condition.operator == ConditionOperator.GREATER_THAN:
                    score_threshold = float(condition.value)
                    if score_threshold > 0.7:
                        user_ids.extend([f"engaged_user_{i}" for i in range(4000, 4100)])
                    elif score_threshold > 0.3:
                        user_ids.extend([f"engaged_user_{i}" for i in range(4000, 4300)])
            
            # Remove duplicates and cache segment
            unique_users = list(set(user_ids))
            await self._cache_segment(segment.id, unique_users)
            
            return unique_users
            
        except Exception as e:
            logger.error(f"Segment building failed: {e}")
            return []
    
    async def _cache_segment(self, segment_id: str, user_ids: List[str]) -> None:
        """Cache segment user list."""
        try:
            await self.redis.delete(f"segment:{segment_id}")
            if user_ids:
                await self.redis.sadd(f"segment:{segment_id}", *user_ids)
                await self.redis.expire(f"segment:{segment_id}", 3600)  # 1 hour cache
        except Exception as e:
            logger.error(f"Failed to cache segment: {e}")
    
    async def get_segment_size(self, segment: CampaignSegment) -> int:
        """Get estimated segment size."""
        try:
            # Check cache first
            cached_size = await self.redis.scard(f"segment:{segment.id}")
            if cached_size > 0:
                return cached_size
            
            # Build segment and return size
            user_ids = await self.build_segment(segment)
            return len(user_ids)
            
        except Exception as e:
            logger.error(f"Failed to get segment size: {e}")
            return 0


class WorkflowEngine:
    """Campaign workflow execution engine."""
    
    def __init__(self, redis_client: redis.Redis, notification_services: Dict[str, Any]):
        self.redis = redis_client
        self.notification_services = notification_services
        
    async def execute_campaign_step(self, execution: CampaignExecution, 
                                  step: CampaignStep, campaign: Campaign) -> bool:
        """Execute individual campaign step."""
        try:
            # Check step conditions
            if not await self._check_step_conditions(step, execution.user_id):
                logger.info(f"Step {step.id} conditions not met for user {execution.user_id}")
                return False
            
            # Determine template to use (A/B testing)
            template_id = step.template_id
            if step.a_b_test_enabled and step.alternative_template_id:
                # Simple A/B test logic
                import hashlib
                user_hash = int(hashlib.md5(execution.user_id.encode()).hexdigest(), 16)
                if (user_hash % 100) < (step.a_b_test_split * 100):
                    template_id = step.alternative_template_id
            
            # Send notification
            notification_sent = await self._send_notification(
                execution.user_id,
                step.channel,
                template_id,
                campaign.id,
                step.id
            )
            
            # Record step execution
            step_execution = {
                'step_id': step.id,
                'template_id': template_id,
                'channel': step.channel.value,
                'status': 'sent' if notification_sent else 'failed',
                'executed_at': datetime.utcnow().isoformat(),
                'metadata': {}
            }
            
            execution.step_executions.append(step_execution)
            
            # Update campaign metrics
            await self._update_campaign_metrics(campaign.id, step.id, step.channel, 'sent' if notification_sent else 'failed')
            
            return notification_sent
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False
    
    async def _check_step_conditions(self, step: CampaignStep, user_id: str) -> bool:
        """Check if step conditions are met."""
        try:
            if not step.conditions:
                return True
            
            # Get user data
            user_data = await self._get_user_data(user_id)
            
            for condition in step.conditions:
                if not self._evaluate_condition(condition, user_data):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Step condition check failed: {e}")
            return True  # Default to allow
    
    def _evaluate_condition(self, condition: CampaignCondition, user_data: Dict[str, Any]) -> bool:
        """Evaluate single condition."""
        try:
            field_value = user_data.get(condition.field)
            
            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return float(field_value or 0) > float(condition.value)
            elif condition.operator == ConditionOperator.LESS_THAN:
                return float(field_value or 0) < float(condition.value)
            elif condition.operator == ConditionOperator.CONTAINS:
                return condition.value in str(field_value or "")
            elif condition.operator == ConditionOperator.NOT_CONTAINS:
                return condition.value not in str(field_value or "")
            elif condition.operator == ConditionOperator.IN:
                return field_value in condition.value if isinstance(condition.value, list) else False
            elif condition.operator == ConditionOperator.NOT_IN:
                return field_value not in condition.value if isinstance(condition.value, list) else True
            elif condition.operator == ConditionOperator.EXISTS:
                return field_value is not None
            elif condition.operator == ConditionOperator.NOT_EXISTS:
                return field_value is None
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    async def _send_notification(self, user_id: str, channel: ChannelType,
                               template_id: str, campaign_id: str, step_id: str) -> bool:
        """Send notification through appropriate service."""
        try:
            # In production, this would call the actual notification services
            # For now, simulate sending
            
            logger.info(f"Sending {channel.value} notification to {user_id} using template {template_id}")
            
            # Simulate random success/failure
            import random
            success = random.random() > 0.05  # 95% success rate
            
            if success:
                # Record notification sent
                notification_data = {
                    'user_id': user_id,
                    'channel': channel.value,
                    'template_id': template_id,
                    'campaign_id': campaign_id,
                    'step_id': step_id,
                    'sent_at': datetime.utcnow().isoformat()
                }
                
                await self.redis.lpush(f"campaign_notifications:{campaign_id}", json.dumps(notification_data))
            
            return success
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return False
    
    async def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data for condition evaluation."""
        try:
            # In production, this would fetch from user database
            # For now, return sample data
            
            return {
                'user_type': 'creator' if 'creator' in user_id else 'brand',
                'signup_date': '2024-01-15',
                'engagement_score': 0.75,
                'last_login': '2024-12-01',
                'subscription_status': 'active',
                'total_content': 25,
                'followers_count': 1500
            }
            
        except Exception as e:
            logger.error(f"Failed to get user data: {e}")
            return {}
    
    async def _update_campaign_metrics(self, campaign_id: str, step_id: str,
                                     channel: ChannelType, status: str) -> None:
        """Update campaign performance metrics."""
        try:
            # Update step metrics
            step_key = f"campaign_metrics:{campaign_id}:step:{step_id}:{status}"
            await self.redis.incr(step_key)
            
            # Update channel metrics
            channel_key = f"campaign_metrics:{campaign_id}:channel:{channel.value}:{status}"
            await self.redis.incr(channel_key)
            
            # Update total metrics
            total_key = f"campaign_metrics:{campaign_id}:total:{status}"
            await self.redis.incr(total_key)
            
        except Exception as e:
            logger.error(f"Failed to update campaign metrics: {e}")


class NotificationCampaignOrchestrator:
    """Enterprise notification campaign orchestrator."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        
        # Initialize engines
        self.segment_builder = SegmentBuilder(self.redis)
        self.workflow_engine = WorkflowEngine(self.redis, config.get('notification_services', {}))
        
        # Campaign storage
        self.campaigns: Dict[str, Campaign] = {}
        self.executions: Dict[str, CampaignExecution] = {}
        
        # Background task management
        self.running_campaigns: set = set()
        
        # Start background processors
        asyncio.create_task(self._process_campaign_triggers())
        asyncio.create_task(self._process_campaign_steps())
        asyncio.create_task(self._update_campaign_metrics())
    
    async def create_campaign(self, campaign: Campaign) -> bool:
        """Create new campaign."""
        try:
            # Validate campaign
            if not await self._validate_campaign(campaign):
                return False
            
            # Store campaign
            await self._store_campaign(campaign)
            
            # Cache in memory
            self.campaigns[campaign.id] = campaign
            
            logger.info(f"Campaign {campaign.id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Campaign creation failed: {e}")
            return False
    
    async def start_campaign(self, campaign_id: str) -> bool:
        """Start campaign execution."""
        try:
            campaign = await self._load_campaign(campaign_id)
            if not campaign:
                return False
            
            # Update status
            campaign.status = CampaignStatus.ACTIVE
            campaign.updated_at = datetime.utcnow()
            
            await self._store_campaign(campaign)
            
            # Add to running campaigns
            self.running_campaigns.add(campaign_id)
            
            # If immediate trigger, execute for target segments
            if campaign.trigger and campaign.trigger.type == TriggerType.IMMEDIATE:
                await self._execute_immediate_campaign(campaign)
            
            logger.info(f"Campaign {campaign_id} started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start campaign: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause campaign execution."""
        try:
            campaign = await self._load_campaign(campaign_id)
            if not campaign:
                return False
            
            campaign.status = CampaignStatus.PAUSED
            campaign.updated_at = datetime.utcnow()
            
            await self._store_campaign(campaign)
            
            # Remove from running campaigns
            self.running_campaigns.discard(campaign_id)
            
            logger.info(f"Campaign {campaign_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False
    
    async def stop_campaign(self, campaign_id: str) -> bool:
        """Stop campaign execution."""
        try:
            campaign = await self._load_campaign(campaign_id)
            if not campaign:
                return False
            
            campaign.status = CampaignStatus.COMPLETED
            campaign.updated_at = datetime.utcnow()
            
            await self._store_campaign(campaign)
            
            # Remove from running campaigns
            self.running_campaigns.discard(campaign_id)
            
            logger.info(f"Campaign {campaign_id} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop campaign: {e}")
            return False
    
    async def trigger_campaign_for_user(self, campaign_id: str, user_id: str,
                                      trigger_data: Dict[str, Any] = None) -> bool:
        """Trigger campaign for specific user."""
        try:
            campaign = await self._load_campaign(campaign_id)
            if not campaign or campaign.status != CampaignStatus.ACTIVE:
                return False
            
            # Check if user can receive campaign
            if not await self._can_user_receive_campaign(user_id, campaign):
                return False
            
            # Create campaign execution
            execution = CampaignExecution(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                user_id=user_id,
                metadata=trigger_data or {}
            )
            
            # Store execution
            await self._store_execution(execution)
            
            # Queue first step
            if campaign.steps:
                first_step = min(campaign.steps, key=lambda s: s.order)
                await self._queue_campaign_step(execution.id, first_step.id, first_step.delay_hours)
            
            logger.info(f"Campaign {campaign_id} triggered for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger campaign: {e}")
            return False
    
    async def get_campaign_performance(self, campaign_id: str) -> Optional[CampaignMetrics]:
        """Get campaign performance metrics."""
        try:
            # Load metrics from Redis
            metrics = CampaignMetrics(campaign_id=campaign_id)
            
            # Get total metrics
            for status in ['sent', 'delivered', 'opened', 'clicked', 'converted']:
                count = await self.redis.get(f"campaign_metrics:{campaign_id}:total:{status}") or 0
                setattr(metrics, f"total_{status}", int(count))
            
            # Get step metrics
            campaign = await self._load_campaign(campaign_id)
            if campaign:
                for step in campaign.steps:
                    step_metrics = {}
                    for status in ['sent', 'delivered', 'opened', 'clicked', 'converted']:
                        count = await self.redis.get(f"campaign_metrics:{campaign_id}:step:{step.id}:{status}") or 0
                        step_metrics[status] = int(count)
                    metrics.step_metrics[step.id] = step_metrics
                
                # Get channel metrics
                for step in campaign.steps:
                    channel = step.channel.value
                    if channel not in metrics.channel_metrics:
                        metrics.channel_metrics[channel] = {}
                    
                    for status in ['sent', 'delivered', 'opened', 'clicked', 'converted']:
                        count = await self.redis.get(f"campaign_metrics:{campaign_id}:channel:{channel}:{status}") or 0
                        metrics.channel_metrics[channel][status] = int(count)
            
            metrics.last_updated = datetime.utcnow()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {e}")
            return None
    
    async def create_segment(self, segment: CampaignSegment) -> bool:
        """Create audience segment."""
        try:
            # Build segment
            user_ids = await self.segment_builder.build_segment(segment)
            segment.size_estimate = len(user_ids)
            segment.last_updated = datetime.utcnow()
            
            # Store segment
            await self._store_segment(segment)
            
            logger.info(f"Segment {segment.id} created with {len(user_ids)} users")
            return True
            
        except Exception as e:
            logger.error(f"Segment creation failed: {e}")
            return False
    
    async def get_campaign_executions(self, campaign_id: str, 
                                    limit: int = 100) -> List[CampaignExecution]:
        """Get campaign executions."""
        try:
            execution_ids = await self.redis.lrange(f"campaign_executions:{campaign_id}", 0, limit - 1)
            
            executions = []
            for execution_id in execution_ids:
                execution = await self._load_execution(execution_id)
                if execution:
                    executions.append(execution)
            
            return executions
            
        except Exception as e:
            logger.error(f"Failed to get campaign executions: {e}")
            return []
    
    async def get_user_campaigns(self, user_id: str) -> List[Campaign]:
        """Get campaigns user is eligible for."""
        try:
            # Get all active campaigns
            campaign_ids = await self.redis.smembers("active_campaigns")
            
            eligible_campaigns = []
            for campaign_id in campaign_ids:
                campaign = await self._load_campaign(campaign_id)
                if campaign and await self._can_user_receive_campaign(user_id, campaign):
                    eligible_campaigns.append(campaign)
            
            return eligible_campaigns
            
        except Exception as e:
            logger.error(f"Failed to get user campaigns: {e}")
            return []
    
    async def _validate_campaign(self, campaign: Campaign) -> bool:
        """Validate campaign configuration."""
        try:
            # Basic validation
            if not campaign.name or not campaign.type:
                return False
            
            # Validate steps
            if not campaign.steps:
                logger.warning("Campaign has no steps")
                return False
            
            # Check step order
            orders = [step.order for step in campaign.steps]
            if len(orders) != len(set(orders)):
                logger.error("Duplicate step orders found")
                return False
            
            # Validate trigger
            if campaign.trigger:
                if not campaign.trigger.type:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Campaign validation failed: {e}")
            return False
    
    async def _execute_immediate_campaign(self, campaign: Campaign) -> None:
        """Execute campaign immediately for all eligible users."""
        try:
            # Get all users from campaign segments
            all_user_ids = set()
            
            for segment in campaign.segments:
                user_ids = await self.segment_builder.build_segment(segment)
                all_user_ids.update(user_ids)
            
            # Trigger campaign for each user
            for user_id in all_user_ids:
                await self.trigger_campaign_for_user(campaign.id, user_id)
                
        except Exception as e:
            logger.error(f"Immediate campaign execution failed: {e}")
    
    async def _can_user_receive_campaign(self, user_id: str, campaign: Campaign) -> bool:
        """Check if user can receive campaign."""
        try:
            # Check if user is in any campaign segment
            if campaign.segments:
                user_in_segment = False
                for segment in campaign.segments:
                    if await self.redis.sismember(f"segment:{segment.id}", user_id):
                        user_in_segment = True
                        break
                
                if not user_in_segment:
                    return False
            
            # Check if user already received this campaign
            if campaign.trigger and campaign.trigger.max_triggers_per_user == 1:
                existing_execution = await self.redis.get(f"user_campaign:{user_id}:{campaign.id}")
                if existing_execution:
                    return False
            
            # Check trigger conditions
            if campaign.trigger and campaign.trigger.conditions:
                user_data = await self.workflow_engine._get_user_data(user_id)
                for condition in campaign.trigger.conditions:
                    if not self.workflow_engine._evaluate_condition(condition, user_data):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"User eligibility check failed: {e}")
            return False
    
    async def _queue_campaign_step(self, execution_id: str, step_id: str, delay_hours: int = 0) -> None:
        """Queue campaign step for execution."""
        try:
            execute_at = datetime.utcnow() + timedelta(hours=delay_hours)
            
            step_data = {
                'execution_id': execution_id,
                'step_id': step_id,
                'scheduled_at': execute_at.isoformat()
            }
            
            # Add to scheduled queue
            await self.redis.zadd("campaign_step_queue", {json.dumps(step_data): execute_at.timestamp()})
            
        except Exception as e:
            logger.error(f"Failed to queue campaign step: {e}")
    
    async def _store_campaign(self, campaign: Campaign) -> None:
        """Store campaign in Redis."""
        try:
            campaign_data = self._serialize_campaign(campaign)
            await self.redis.hset(f"campaign:{campaign.id}", mapping=campaign_data)
            
            # Add to indexes
            await self.redis.sadd("all_campaigns", campaign.id)
            if campaign.status == CampaignStatus.ACTIVE:
                await self.redis.sadd("active_campaigns", campaign.id)
            
        except Exception as e:
            logger.error(f"Failed to store campaign: {e}")
            raise
    
    async def _load_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Load campaign from Redis."""
        try:
            # Check memory cache
            if campaign_id in self.campaigns:
                return self.campaigns[campaign_id]
            
            # Load from Redis
            campaign_data = await self.redis.hgetall(f"campaign:{campaign_id}")
            if not campaign_data:
                return None
            
            campaign = self._deserialize_campaign(campaign_data)
            self.campaigns[campaign_id] = campaign
            return campaign
            
        except Exception as e:
            logger.error(f"Failed to load campaign: {e}")
            return None
    
    def _serialize_campaign(self, campaign: Campaign) -> Dict[str, str]:
        """Serialize campaign for storage."""
        try:
            data = {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'type': campaign.type.value,
                'status': campaign.status.value,
                'start_date': campaign.start_date.isoformat() if campaign.start_date else '',
                'end_date': campaign.end_date.isoformat() if campaign.end_date else '',
                'timezone': campaign.timezone,
                'created_by': campaign.created_by,
                'created_at': campaign.created_at.isoformat(),
                'updated_at': campaign.updated_at.isoformat(),
                'goals': json.dumps(campaign.goals),
                'tags': json.dumps(campaign.tags),
                'metadata': json.dumps(campaign.metadata)
            }
            
            # Serialize trigger
            if campaign.trigger:
                data['trigger'] = json.dumps({
                    'id': campaign.trigger.id,
                    'name': campaign.trigger.name,
                    'type': campaign.trigger.type.value,
                    'conditions': [{
                        'field': c.field,
                        'operator': c.operator.value,
                        'value': c.value,
                        'condition_type': c.condition_type
                    } for c in campaign.trigger.conditions],
                    'delay_minutes': campaign.trigger.delay_minutes,
                    'max_triggers_per_user': campaign.trigger.max_triggers_per_user,
                    'cooldown_hours': campaign.trigger.cooldown_hours,
                    'enabled': campaign.trigger.enabled
                })
            else:
                data['trigger'] = ''
            
            # Serialize steps
            data['steps'] = json.dumps([{
                'id': step.id,
                'name': step.name,
                'order': step.order,
                'template_id': step.template_id,
                'channel': step.channel.value,
                'delay_hours': step.delay_hours,
                'conditions': [{
                    'field': c.field,
                    'operator': c.operator.value,
                    'value': c.value,
                    'condition_type': c.condition_type
                } for c in step.conditions],
                'a_b_test_enabled': step.a_b_test_enabled,
                'a_b_test_split': step.a_b_test_split,
                'alternative_template_id': step.alternative_template_id,
                'enabled': step.enabled
            } for step in campaign.steps])
            
            # Serialize segments
            data['segments'] = json.dumps([{
                'id': segment.id,
                'name': segment.name,
                'description': segment.description,
                'conditions': [{
                    'field': c.field,
                    'operator': c.operator.value,
                    'value': c.value,
                    'condition_type': c.condition_type
                } for c in segment.conditions],
                'size_estimate': segment.size_estimate,
                'last_updated': segment.last_updated.isoformat()
            } for segment in campaign.segments])
            
            return {k: str(v) for k, v in data.items()}
            
        except Exception as e:
            logger.error(f"Campaign serialization failed: {e}")
            return {}
    
    def _deserialize_campaign(self, data: Dict[str, str]) -> Campaign:
        """Deserialize campaign from storage."""
        try:
            # Parse basic fields
            campaign = Campaign(
                id=data['id'],
                name=data['name'],
                description=data['description'],
                type=CampaignType(data['type']),
                status=CampaignStatus(data['status']),
                start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
                end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
                timezone=data['timezone'],
                created_by=data['created_by'],
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at']),
                goals=json.loads(data.get('goals', '{}')),
                tags=json.loads(data.get('tags', '[]')),
                metadata=json.loads(data.get('metadata', '{}'))
            )
            
            # Parse trigger
            if data.get('trigger'):
                trigger_data = json.loads(data['trigger'])
                conditions = [
                    CampaignCondition(
                        field=c['field'],
                        operator=ConditionOperator(c['operator']),
                        value=c['value'],
                        condition_type=c['condition_type']
                    ) for c in trigger_data['conditions']
                ]
                
                campaign.trigger = CampaignTrigger(
                    id=trigger_data['id'],
                    name=trigger_data['name'],
                    type=TriggerType(trigger_data['type']),
                    conditions=conditions,
                    delay_minutes=trigger_data['delay_minutes'],
                    max_triggers_per_user=trigger_data['max_triggers_per_user'],
                    cooldown_hours=trigger_data['cooldown_hours'],
                    enabled=trigger_data['enabled']
                )
            
            # Parse steps
            if data.get('steps'):
                steps_data = json.loads(data['steps'])
                campaign.steps = []
                for step_data in steps_data:
                    conditions = [
                        CampaignCondition(
                            field=c['field'],
                            operator=ConditionOperator(c['operator']),
                            value=c['value'],
                            condition_type=c['condition_type']
                        ) for c in step_data['conditions']
                    ]
                    
                    step = CampaignStep(
                        id=step_data['id'],
                        name=step_data['name'],
                        order=step_data['order'],
                        template_id=step_data['template_id'],
                        channel=ChannelType(step_data['channel']),
                        delay_hours=step_data['delay_hours'],
                        conditions=conditions,
                        a_b_test_enabled=step_data['a_b_test_enabled'],
                        a_b_test_split=step_data['a_b_test_split'],
                        alternative_template_id=step_data.get('alternative_template_id'),
                        enabled=step_data['enabled']
                    )
                    campaign.steps.append(step)
            
            # Parse segments
            if data.get('segments'):
                segments_data = json.loads(data['segments'])
                campaign.segments = []
                for segment_data in segments_data:
                    conditions = [
                        CampaignCondition(
                            field=c['field'],
                            operator=ConditionOperator(c['operator']),
                            value=c['value'],
                            condition_type=c['condition_type']
                        ) for c in segment_data['conditions']
                    ]
                    
                    segment = CampaignSegment(
                        id=segment_data['id'],
                        name=segment_data['name'],
                        description=segment_data['description'],
                        conditions=conditions,
                        size_estimate=segment_data['size_estimate'],
                        last_updated=datetime.fromisoformat(segment_data['last_updated'])
                    )
                    campaign.segments.append(segment)
            
            return campaign
            
        except Exception as e:
            logger.error(f"Campaign deserialization failed: {e}")
            raise
    
    async def _store_execution(self, execution: CampaignExecution) -> None:
        """Store campaign execution."""
        try:
            execution_data = {
                'id': execution.id,
                'campaign_id': execution.campaign_id,
                'user_id': execution.user_id,
                'status': execution.status,
                'current_step': str(execution.current_step),
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else '',
                'step_executions': json.dumps(execution.step_executions),
                'metadata': json.dumps(execution.metadata)
            }
            
            await self.redis.hset(f"execution:{execution.id}", mapping=execution_data)
            await self.redis.lpush(f"campaign_executions:{execution.campaign_id}", execution.id)
            await self.redis.set(f"user_campaign:{execution.user_id}:{execution.campaign_id}", execution.id)
            
        except Exception as e:
            logger.error(f"Failed to store execution: {e}")
    
    async def _load_execution(self, execution_id: str) -> Optional[CampaignExecution]:
        """Load campaign execution."""
        try:
            execution_data = await self.redis.hgetall(f"execution:{execution_id}")
            if not execution_data:
                return None
            
            return CampaignExecution(
                id=execution_data['id'],
                campaign_id=execution_data['campaign_id'],
                user_id=execution_data['user_id'],
                status=execution_data['status'],
                current_step=int(execution_data['current_step']),
                started_at=datetime.fromisoformat(execution_data['started_at']),
                completed_at=datetime.fromisoformat(execution_data['completed_at']) if execution_data.get('completed_at') else None,
                step_executions=json.loads(execution_data.get('step_executions', '[]')),
                metadata=json.loads(execution_data.get('metadata', '{}'))
            )
            
        except Exception as e:
            logger.error(f"Failed to load execution: {e}")
            return None
    
    async def _store_segment(self, segment: CampaignSegment) -> None:
        """Store campaign segment."""
        try:
            segment_data = {
                'id': segment.id,
                'name': segment.name,
                'description': segment.description,
                'conditions': json.dumps([{
                    'field': c.field,
                    'operator': c.operator.value,
                    'value': c.value,
                    'condition_type': c.condition_type
                } for c in segment.conditions]),
                'size_estimate': str(segment.size_estimate),
                'last_updated': segment.last_updated.isoformat()
            }
            
            await self.redis.hset(f"segment:{segment.id}", mapping=segment_data)
            await self.redis.sadd("all_segments", segment.id)
            
        except Exception as e:
            logger.error(f"Failed to store segment: {e}")
    
    async def _process_campaign_triggers(self) -> None:
        """Background task to process campaign triggers."""
        while True:
            try:
                # Check for triggered campaigns
                # This would monitor events and trigger campaigns accordingly
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Campaign trigger processing error: {e}")
                await asyncio.sleep(60)
    
    async def _process_campaign_steps(self) -> None:
        """Background task to process scheduled campaign steps."""
        while True:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Get steps ready for execution
                ready_steps = await self.redis.zrangebyscore(
                    "campaign_step_queue", 0, current_time, withscores=True
                )
                
                for step_data_str, _ in ready_steps:
                    try:
                        step_data = json.loads(step_data_str)
                        execution_id = step_data['execution_id']
                        step_id = step_data['step_id']
                        
                        # Load execution and campaign
                        execution = await self._load_execution(execution_id)
                        if not execution:
                            continue
                        
                        campaign = await self._load_campaign(execution.campaign_id)
                        if not campaign:
                            continue
                        
                        # Find step
                        step = next((s for s in campaign.steps if s.id == step_id), None)
                        if not step:
                            continue
                        
                        # Execute step
                        success = await self.workflow_engine.execute_campaign_step(execution, step, campaign)
                        
                        if success:
                            # Update execution
                            execution.current_step += 1
                            await self._store_execution(execution)
                            
                            # Queue next step if exists
                            next_steps = [s for s in campaign.steps if s.order > step.order]
                            if next_steps:
                                next_step = min(next_steps, key=lambda s: s.order)
                                await self._queue_campaign_step(execution.id, next_step.id, next_step.delay_hours)
                            else:
                                # Campaign completed for this user
                                execution.status = "completed"
                                execution.completed_at = datetime.utcnow()
                                await self._store_execution(execution)
                        
                        # Remove from queue
                        await self.redis.zrem("campaign_step_queue", step_data_str)
                        
                    except Exception as e:
                        logger.error(f"Step processing failed: {e}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Campaign step processing error: {e}")
                await asyncio.sleep(30)
    
    async def _update_campaign_metrics(self) -> None:
        """Background task to update campaign metrics."""
        while True:
            try:
                # Update aggregated metrics for all campaigns
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Metrics update error: {e}")
                await asyncio.sleep(300)


# Factory function for creating service instance
def create_campaign_orchestrator(config: Dict[str, Any]) -> NotificationCampaignOrchestrator:
    """Create and configure notification campaign orchestrator."""
    return NotificationCampaignOrchestrator(config)


# Export main classes and functions
__all__ = [
    'NotificationCampaignOrchestrator',
    'Campaign',
    'CampaignStep',
    'CampaignTrigger',
    'CampaignSegment',
    'CampaignExecution',
    'CampaignMetrics',
    'CampaignCondition',
    'CampaignType',
    'CampaignStatus',
    'TriggerType',
    'ChannelType',
    'ConditionOperator',
    'SegmentBuilder',
    'WorkflowEngine',
    'create_campaign_orchestrator'
]