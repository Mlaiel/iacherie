"""Escalation Manager - Ultra-Advanced Human Agent Escalation System

Enterprise-grade escalation management providing intelligent routing to human agents,
priority assessment, workload distribution, and seamless handoff between AI and
human support representatives.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import deque, defaultdict
import math

# Queue and priority management
import heapq
from asyncio import Queue, Lock
import redis.asyncio as aioredis

# Communication and notifications
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import asyncio_mqtt as mqtt

# AI for escalation decision making
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class EscalationTrigger(Enum):
    """Escalation trigger types"""    USER_REQUEST = "user_request"
    AI_CONFIDENCE_LOW = "ai_confidence_low"
    COMPLEX_ISSUE = "complex_issue"
    TECHNICAL_LIMITATION = "technical_limitation"
    BILLING_DISPUTE = "billing_dispute"
    LEGAL_CONCERN = "legal_concern"
    SECURITY_ISSUE = "security_issue"
    VIP_CUSTOMER = "vip_customer"
    REPEATED_FAILURE = "repeated_failure"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    EMERGENCY = "emergency"

class EscalationPriority(Enum):
    """Escalation priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5
    EMERGENCY = 6

class AgentStatus(Enum):
    """Human agent status"""    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    BREAK = "break"
    OFFLINE = "offline"
    IN_TRAINING = "in_training"

class AgentSpecialty(Enum):
    """Human agent specialties"""    TECHNICAL_SUPPORT = "technical_support"
    BILLING_SPECIALIST = "billing_specialist"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_EXPERT = "collaboration_expert"
    AUDIO_ENGINEER = "audio_engineer"
    LEGAL_ADVISOR = "legal_advisor"
    CUSTOMER_SUCCESS = "customer_success"
    PLATFORM_INTEGRATION = "platform_integration"
    SECURITY_SPECIALIST = "security_specialist"
    GENERAL_SUPPORT = "general_support"

@dataclass
class HumanAgent:
    """Human agent profile"""    agent_id: str
    name: str
    email: str
    specialties: List[AgentSpecialty]
    
    # Status and availability
    status: AgentStatus = AgentStatus.OFFLINE
    current_workload: int = 0
    max_concurrent_cases: int = 5
    
    # Performance metrics
    average_response_time: float = 300.0  # 5 minutes
    resolution_rate: float = 0.85
    satisfaction_rating: float = 4.2
    cases_resolved_today: int = 0
    
    # Availability schedule
    work_hours_start: str = "09:00"
    work_hours_end: str = "17:00"
    timezone: str = "UTC"
    break_until: Optional[datetime] = None
    
    # Language capabilities
    languages: List[str] = field(default_factory=lambda: ["en"])
    
    # Contact preferences
    preferred_contact_method: str = "internal_chat"  # internal_chat, email, phone
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    hire_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_cases_resolved: int = 0

@dataclass
class EscalationRequest:
    """Escalation request structure"""    escalation_id: str
    conversation_id: str
    user_id: str
    
    # Escalation details
    trigger: EscalationTrigger
    priority: EscalationPriority
    reason: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Request metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    requested_specialty: Optional[AgentSpecialty] = None
    estimated_complexity: float = 0.5  # 0.0 to 1.0
    
    # AI analysis
    sentiment_score: Optional[float] = None
    urgency_score: float = 0.5
    technical_complexity: float = 0.5
    
    # Customer information
    customer_tier: str = "free"  # free, pro, enterprise
    customer_satisfaction: Optional[float] = None
    previous_escalations: int = 0
    
    # Assignment tracking
    assigned_agent: Optional[str] = None
    assigned_at: Optional[datetime] = None
    estimated_wait_time: Optional[int] = None
    
    # Resolution tracking
    resolved_at: Optional[datetime] = None
    resolution_time: Optional[float] = None
    resolution_rating: Optional[float] = None

class EscalationQueue:
    """Priority-based escalation queue"""    
    def __init__(self):
        self._queue: List[Tuple[int, float, EscalationRequest]] = []
        self._entry_finder = {}
        self._counter = 0
        self._lock = Lock()
    
    async def add_request(self, request: EscalationRequest):
        """Add escalation request to priority queue"""        async with self._lock:
            # Calculate priority score (lower is higher priority)
            priority_score = await self._calculate_priority_score(request)
            
            entry = [priority_score, self._counter, request]
            self._entry_finder[request.escalation_id] = entry
            heapq.heappush(self._queue, entry)
            self._counter += 1
    
    async def get_next_request(self) -> Optional[EscalationRequest]:
        """Get next highest priority request"""        async with self._lock:
            while self._queue:
                priority_score, counter, request = heapq.heappop(self._queue)
                
                if request.escalation_id not in self._entry_finder:
                    continue  # Request was removed
                
                del self._entry_finder[request.escalation_id]
                return request
        
        return None
    
    async def remove_request(self, escalation_id: str) -> bool:
        """Remove request from queue"""        async with self._lock:
            if escalation_id in self._entry_finder:
                entry = self._entry_finder.pop(escalation_id)
                entry[2] = None  # Mark as removed
                return True
        return False
    
    async def update_priority(self, escalation_id: str, new_priority: EscalationPriority):
        """Update request priority"""        async with self._lock:
            if escalation_id in self._entry_finder:
                # Remove old entry
                old_entry = self._entry_finder.pop(escalation_id)
                old_entry[2] = None
                
                # Add new entry with updated priority
                request = old_entry[2]
                if request:
                    request.priority = new_priority
                    await self.add_request(request)
                    return True
        return False
    
    async def _calculate_priority_score(self, request: EscalationRequest) -> float:
        """Calculate priority score for queue ordering"""        # Base priority from enum (inverted: lower value = higher priority)
        base_score = 7 - request.priority.value
        
        # Urgency multiplier
        urgency_multiplier = 1 + request.urgency_score
        
        # Customer tier bonus
        tier_bonus = {
            "enterprise": -2.0,
            "pro": -1.0,
            "free": 0.0
        }.get(request.customer_tier, 0.0)
        
        # Wait time penalty (increases priority over time)
        wait_minutes = (datetime.now(timezone.utc) - request.created_at).total_seconds() / 60
        wait_penalty = -math.log(1 + wait_minutes / 10) * 0.1
        
        # Previous escalations penalty
        escalation_penalty = request.previous_escalations * 0.2
        
        # Calculate final score
        final_score = (base_score * urgency_multiplier) + tier_bonus + wait_penalty - escalation_penalty
        
        return max(0.1, final_score)  # Ensure positive score
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""        async with self._lock:
            active_requests = [req for _, _, req in self._queue if req is not None]
            
            return {
                "total_requests": len(active_requests),
                "priority_breakdown": {
                    priority.name: len([r for r in active_requests if r.priority == priority])
                    for priority in EscalationPriority
                },
                "average_wait_time": sum([
                    (datetime.now(timezone.utc) - r.created_at).total_seconds() / 60
                    for r in active_requests
                ]) / len(active_requests) if active_requests else 0,
                "oldest_request_age": max([
                    (datetime.now(timezone.utc) - r.created_at).total_seconds() / 60
                    for r in active_requests
                ]) if active_requests else 0
            }

class EscalationManager:
    """Ultra-advanced escalation management system"""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.escalation_queue = EscalationQueue()
        
        # Agent management
        self.human_agents: Dict[str, HumanAgent] = {}
        self.agent_assignments: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> escalation_ids
        
        # AI models for escalation decisions
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.complexity_classifier = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Statistics and monitoring
        self.escalation_stats = defaultdict(int)
        self.performance_metrics = defaultdict(list)
        
        # Notification system
        self.notification_queue = Queue()
        
        # Initialize with default agents
        asyncio.create_task(self._initialize_default_agents())
        asyncio.create_task(self._start_notification_processor())
    
    async def _initialize_default_agents(self):
        """Initialize default human agents"""        default_agents = [
            HumanAgent(
                agent_id="agent_tech_001",
                name="Sarah Chen",
                email="sarah.chen@ia-influencer.com",
                specialties=[AgentSpecialty.TECHNICAL_SUPPORT, AgentSpecialty.AUDIO_ENGINEER],
                max_concurrent_cases=8,
                average_response_time=180.0,
                resolution_rate=0.92,
                satisfaction_rating=4.6,
                languages=["en", "zh"],
                work_hours_start="08:00",
                work_hours_end="16:00",
                timezone="America/Los_Angeles"
            ),
            HumanAgent(
                agent_id="agent_billing_001",
                name="Michael Rodriguez",
                email="michael.rodriguez@ia-influencer.com",
                specialties=[AgentSpecialty.BILLING_SPECIALIST, AgentSpecialty.CUSTOMER_SUCCESS],
                max_concurrent_cases=6,
                average_response_time=240.0,
                resolution_rate=0.88,
                satisfaction_rating=4.4,
                languages=["en", "es"],
                work_hours_start="09:00",
                work_hours_end="17:00",
                timezone="America/New_York"
            ),
            HumanAgent(
                agent_id="agent_content_001",
                name="Emma Thompson",
                email="emma.thompson@ia-influencer.com",
                specialties=[AgentSpecialty.CONTENT_PROTECTION, AgentSpecialty.LEGAL_ADVISOR],
                max_concurrent_cases=4,
                average_response_time=300.0,
                resolution_rate=0.85,
                satisfaction_rating=4.5,
                languages=["en", "fr"],
                work_hours_start="10:00",
                work_hours_end="18:00",
                timezone="Europe/London"
            ),
            HumanAgent(
                agent_id="agent_collab_001",
                name="David Kim",
                email="david.kim@ia-influencer.com",
                specialties=[AgentSpecialty.COLLABORATION_EXPERT, AgentSpecialty.PLATFORM_INTEGRATION],
                max_concurrent_cases=7,
                average_response_time=200.0,
                resolution_rate=0.90,
                satisfaction_rating=4.3,
                languages=["en", "ko"],
                work_hours_start="07:00",
                work_hours_end="15:00",
                timezone="Asia/Seoul"
            ),
            HumanAgent(
                agent_id="agent_security_001",
                name="Lisa Anderson",
                email="lisa.anderson@ia-influencer.com",
                specialties=[AgentSpecialty.SECURITY_SPECIALIST, AgentSpecialty.LEGAL_ADVISOR],
                max_concurrent_cases=3,
                average_response_time=150.0,
                resolution_rate=0.95,
                satisfaction_rating=4.7,
                languages=["en", "de"],
                work_hours_start="09:00",
                work_hours_end="17:00",
                timezone="Europe/Berlin"
            ),
            HumanAgent(
                agent_id="agent_general_001",
                name="James Wilson",
                email="james.wilson@ia-influencer.com",
                specialties=[AgentSpecialty.GENERAL_SUPPORT, AgentSpecialty.CUSTOMER_SUCCESS],
                max_concurrent_cases=10,
                average_response_time=360.0,
                resolution_rate=0.82,
                satisfaction_rating=4.1,
                languages=["en"],
                work_hours_start="12:00",
                work_hours_end="20:00",
                timezone="UTC"
            )
        ]
        
        for agent in default_agents:
            self.human_agents[agent.agent_id] = agent
            await self._cache_agent(agent)
        
        logger.info(f"Initialized {len(default_agents)} default human agents")
    
    async def create_escalation(
        self,
        conversation_id: str,
        user_id: str,
        trigger: EscalationTrigger,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
        priority: Optional[EscalationPriority] = None,
        requested_specialty: Optional[AgentSpecialty] = None
    ) -> EscalationRequest:
        """Create new escalation request"""        try:
            escalation_id = str(uuid.uuid4())
            
            # Analyze conversation context for priority and complexity
            ai_analysis = await self._analyze_escalation_context(context or {}, reason)
            
            # Determine priority if not specified
            if priority is None:
                priority = await self._determine_priority(trigger, ai_analysis, context)
            
            # Create escalation request
            escalation = EscalationRequest(
                escalation_id=escalation_id,
                conversation_id=conversation_id,
                user_id=user_id,
                trigger=trigger,
                priority=priority,
                reason=reason,
                context=context or {},
                requested_specialty=requested_specialty,
                sentiment_score=ai_analysis.get("sentiment_score"),
                urgency_score=ai_analysis.get("urgency_score", 0.5),
                technical_complexity=ai_analysis.get("technical_complexity", 0.5),
                customer_tier=await self._get_customer_tier(user_id),
                previous_escalations=await self._count_previous_escalations(user_id)
            )
            
            # Add to queue
            await self.escalation_queue.add_request(escalation)
            
            # Cache escalation
            await self._cache_escalation(escalation)
            
            # Update statistics
            self.escalation_stats[f"trigger_{trigger.value}"] += 1
            self.escalation_stats[f"priority_{priority.value}"] += 1
            
            # Estimate wait time
            escalation.estimated_wait_time = await self._estimate_wait_time(escalation)
            
            # Send notifications
            await self._notify_escalation_created(escalation)
            
            logger.info(f"Created escalation {escalation_id} for user {user_id}")
            return escalation
            
        except Exception as e:
            logger.error(f"Failed to create escalation: {str(e)}")
            raise
    
    async def assign_to_agent(self, escalation_id: str) -> Optional[Tuple[str, HumanAgent]]:
        """Assign escalation to best available agent"""        try:
            # Get escalation from cache
            escalation = await self._get_escalation(escalation_id)
            if not escalation:
                return None
            
            # Find best available agent
            best_agent = await self._find_best_agent(escalation)
            if not best_agent:
                logger.warning(f"No available agent for escalation {escalation_id}")
                return None
            
            # Assign escalation
            escalation.assigned_agent = best_agent.agent_id
            escalation.assigned_at = datetime.now(timezone.utc)
            
            # Update agent workload
            best_agent.current_workload += 1
            self.agent_assignments[best_agent.agent_id].add(escalation_id)
            
            # Remove from queue
            await self.escalation_queue.remove_request(escalation_id)
            
            # Update caches
            await self._cache_escalation(escalation)
            await self._cache_agent(best_agent)
            
            # Notify agent
            await self._notify_agent_assignment(best_agent, escalation)
            
            logger.info(f"Assigned escalation {escalation_id} to agent {best_agent.agent_id}")
            return best_agent.agent_id, best_agent
            
        except Exception as e:
            logger.error(f"Failed to assign escalation {escalation_id}: {str(e)}")
            return None
    
    async def resolve_escalation(
        self,
        escalation_id: str,
        resolution_notes: str,
        customer_rating: Optional[float] = None
    ) -> bool:
        """Mark escalation as resolved"""        try:
            escalation = await self._get_escalation(escalation_id)
            if not escalation:
                return False
            
            # Update escalation
            escalation.resolved_at = datetime.now(timezone.utc)
            escalation.resolution_time = (
                escalation.resolved_at - escalation.created_at
            ).total_seconds()
            escalation.resolution_rating = customer_rating
            
            # Update agent workload and metrics
            if escalation.assigned_agent:
                agent = self.human_agents.get(escalation.assigned_agent)
                if agent:
                    agent.current_workload = max(0, agent.current_workload - 1)
                    agent.cases_resolved_today += 1
                    agent.total_cases_resolved += 1
                    
                    # Update performance metrics
                    if customer_rating:
                        current_total = agent.satisfaction_rating * agent.total_cases_resolved
                        agent.satisfaction_rating = (
                            (current_total + customer_rating) / (agent.total_cases_resolved + 1)
                        )
                    
                    # Remove from assignments
                    self.agent_assignments[agent.agent_id].discard(escalation_id)
                    
                    await self._cache_agent(agent)
            
            # Update escalation cache
            await self._cache_escalation(escalation)
            
            # Update statistics
            self.escalation_stats["resolved"] += 1
            resolution_time_minutes = escalation.resolution_time / 60
            self.performance_metrics["resolution_times"].append(resolution_time_minutes)
            
            # Notify stakeholders
            await self._notify_escalation_resolved(escalation)
            
            logger.info(f"Resolved escalation {escalation_id} in {resolution_time_minutes:.1f} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve escalation {escalation_id}: {str(e)}")
            return False
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""        if agent_id not in self.human_agents:
            return False
        
        agent = self.human_agents[agent_id]
        old_status = agent.status
        agent.status = status
        agent.last_active = datetime.now(timezone.utc)
        
        # Handle status-specific logic
        if status == AgentStatus.OFFLINE:
            # Reassign active cases if going offline
            active_cases = self.agent_assignments.get(agent_id, set())
            for escalation_id in list(active_cases):
                await self._reassign_escalation(escalation_id)
        
        elif status == AgentStatus.AVAILABLE and old_status != AgentStatus.AVAILABLE:
            # Try to assign pending escalations
            asyncio.create_task(self._process_pending_assignments())
        
        await self._cache_agent(agent)
        logger.info(f"Updated agent {agent_id} status from {old_status.value} to {status.value}")
        return True
    
    async def _analyze_escalation_context(
        self,
        context: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """Analyze escalation context using AI"""        try:
            analysis = {}
            
            # Sentiment analysis
            if reason:
                sentiment_result = self.sentiment_analyzer(reason)
                sentiment_label = sentiment_result[0]['label']
                sentiment_score = sentiment_result[0]['score']
                
                # Convert to normalized scale
                if sentiment_label == 'NEGATIVE':
                    analysis['sentiment_score'] = -sentiment_score
                elif sentiment_label == 'POSITIVE':
                    analysis['sentiment_score'] = sentiment_score
                else:
                    analysis['sentiment_score'] = 0.0
            
            # Urgency analysis based on keywords
            urgency_keywords = {
                'emergency': 1.0,
                'urgent': 0.9,
                'critical': 0.9,
                'asap': 0.8,
                'immediately': 0.8,
                'broken': 0.7,
                'not working': 0.7,
                'error': 0.6,
                'problem': 0.5,
                'issue': 0.4,
                'question': 0.2
            }
            
            reason_lower = reason.lower()
            max_urgency = 0.3  # Default
            for keyword, urgency in urgency_keywords.items():
                if keyword in reason_lower:
                    max_urgency = max(max_urgency, urgency)
            
            analysis['urgency_score'] = max_urgency
            
            # Technical complexity estimation
            technical_keywords = [
                'api', 'integration', 'code', 'error', 'bug', 'database',
                'server', 'upload', 'processing', 'fingerprint', 'detection'
            ]
            
            technical_count = sum(1 for keyword in technical_keywords if keyword in reason_lower)
            analysis['technical_complexity'] = min(1.0, technical_count / 5.0)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze escalation context: {str(e)}")
            return {}
    
    async def _determine_priority(
        self,
        trigger: EscalationTrigger,
        ai_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> EscalationPriority:
        """Determine escalation priority based on multiple factors"""        # Base priority from trigger
        trigger_priorities = {
            EscalationTrigger.EMERGENCY: EscalationPriority.EMERGENCY,
            EscalationTrigger.SECURITY_ISSUE: EscalationPriority.CRITICAL,
            EscalationTrigger.LEGAL_CONCERN: EscalationPriority.CRITICAL,
            EscalationTrigger.VIP_CUSTOMER: EscalationPriority.HIGH,
            EscalationTrigger.BILLING_DISPUTE: EscalationPriority.HIGH,
            EscalationTrigger.TECHNICAL_LIMITATION: EscalationPriority.NORMAL,
            EscalationTrigger.COMPLEX_ISSUE: EscalationPriority.NORMAL,
            EscalationTrigger.USER_REQUEST: EscalationPriority.LOW,
            EscalationTrigger.AI_CONFIDENCE_LOW: EscalationPriority.LOW
        }
        
        base_priority = trigger_priorities.get(trigger, EscalationPriority.NORMAL)
        
        # Adjust based on AI analysis
        urgency_score = ai_analysis.get('urgency_score', 0.5)
        sentiment_score = ai_analysis.get('sentiment_score', 0.0)
        
        priority_value = base_priority.value
        
        # Boost for high urgency
        if urgency_score > 0.8:
            priority_value += 2
        elif urgency_score > 0.6:
            priority_value += 1
        
        # Boost for negative sentiment
        if sentiment_score < -0.7:
            priority_value += 1
        
        # Cap at maximum priority
        priority_value = min(priority_value, EscalationPriority.EMERGENCY.value)
        
        return EscalationPriority(priority_value)
    
    async def _find_best_agent(self, escalation: EscalationRequest) -> Optional[HumanAgent]:
        """Find best available agent for escalation"""        available_agents = []
        
        for agent in self.human_agents.values():
            # Check availability
            if agent.status != AgentStatus.AVAILABLE:
                continue
            
            # Check workload capacity
            if agent.current_workload >= agent.max_concurrent_cases:
                continue
            
            # Check working hours
            if not await self._is_agent_in_working_hours(agent):
                continue
            
            # Check specialty match
            specialty_match = False
            if escalation.requested_specialty:
                if escalation.requested_specialty in agent.specialties:
                    specialty_match = True
            else:
                # Auto-assign based on trigger
                trigger_specialties = {
                    EscalationTrigger.TECHNICAL_LIMITATION: AgentSpecialty.TECHNICAL_SUPPORT,
                    EscalationTrigger.BILLING_DISPUTE: AgentSpecialty.BILLING_SPECIALIST,
                    EscalationTrigger.SECURITY_ISSUE: AgentSpecialty.SECURITY_SPECIALIST,
                    EscalationTrigger.LEGAL_CONCERN: AgentSpecialty.LEGAL_ADVISOR
                }
                
                required_specialty = trigger_specialties.get(escalation.trigger)
                if required_specialty and required_specialty in agent.specialties:
                    specialty_match = True
                elif AgentSpecialty.GENERAL_SUPPORT in agent.specialties:
                    specialty_match = True
            
            if specialty_match:
                available_agents.append(agent)
        
        if not available_agents:
            return None
        
        # Score agents based on multiple factors
        scored_agents = []
        for agent in available_agents:
            score = 0.0
            
            # Workload factor (prefer less busy agents)
            workload_factor = 1.0 - (agent.current_workload / agent.max_concurrent_cases)
            score += workload_factor * 3.0
            
            # Performance factors
            score += agent.resolution_rate * 2.0
            score += (agent.satisfaction_rating / 5.0) * 2.0
            score += (1.0 - agent.average_response_time / 600.0) * 1.0  # Prefer faster response
            
            # Specialty match bonus
            if escalation.requested_specialty in agent.specialties:
                score += 2.0
            
            # Customer tier match
            if escalation.customer_tier == "enterprise" and agent.max_concurrent_cases <= 5:
                score += 1.0  # Prefer senior agents for enterprise
            
            scored_agents.append((score, agent))
        
        # Return highest scoring agent
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        return scored_agents[0][1]
    
    async def _is_agent_in_working_hours(self, agent: HumanAgent) -> bool:
        """Check if agent is in working hours"""        # Simplified check - in real implementation would use proper timezone handling
        current_hour = datetime.now().hour
        start_hour = int(agent.work_hours_start.split(':')[0])
        end_hour = int(agent.work_hours_end.split(':')[0])
        
        return start_hour <= current_hour <= end_hour
    
    async def _get_customer_tier(self, user_id: str) -> str:
        """Get customer subscription tier"""        # In real implementation, would query user database
        # For now, return default
        return "pro"
    
    async def _count_previous_escalations(self, user_id: str) -> int:
        """Count previous escalations for user"""        try:
            count = await self.redis_client.get(f"user_escalations:{user_id}")
            return int(count) if count else 0
        except:
            return 0
    
    async def _estimate_wait_time(self, escalation: EscalationRequest) -> int:
        """Estimate wait time in minutes"""        queue_stats = await self.escalation_queue.get_queue_stats()
        
        # Base estimate on queue size and priority
        queue_size = queue_stats["total_requests"]
        
        # Higher priority = shorter wait
        priority_multiplier = {
            EscalationPriority.EMERGENCY: 0.1,
            EscalationPriority.CRITICAL: 0.2,
            EscalationPriority.URGENT: 0.4,
            EscalationPriority.HIGH: 0.7,
            EscalationPriority.NORMAL: 1.0,
            EscalationPriority.LOW: 1.5
        }.get(escalation.priority, 1.0)
        
        # Available agents factor
        available_agents = len([
            a for a in self.human_agents.values()
            if a.status == AgentStatus.AVAILABLE and a.current_workload < a.max_concurrent_cases
        ])
        
        if available_agents == 0:
            base_wait = 30  # 30 minutes if no agents available
        else:
            base_wait = max(5, queue_size / available_agents * 10)
        
        estimated_wait = int(base_wait * priority_multiplier)
        return max(1, estimated_wait)  # Minimum 1 minute
    
    async def _reassign_escalation(self, escalation_id: str) -> bool:
        """Reassign escalation to different agent"""        try:
            escalation = await self._get_escalation(escalation_id)
            if not escalation:
                return False
            
            # Remove current assignment
            if escalation.assigned_agent:
                old_agent = self.human_agents.get(escalation.assigned_agent)
                if old_agent:
                    old_agent.current_workload = max(0, old_agent.current_workload - 1)
                    self.agent_assignments[old_agent.agent_id].discard(escalation_id)
                    await self._cache_agent(old_agent)
            
            # Reset assignment
            escalation.assigned_agent = None
            escalation.assigned_at = None
            
            # Add back to queue
            await self.escalation_queue.add_request(escalation)
            await self._cache_escalation(escalation)
            
            logger.info(f"Reassigned escalation {escalation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reassign escalation {escalation_id}: {str(e)}")
            return False
    
    async def _process_pending_assignments(self):
        """Process pending escalations and assign to available agents"""        try:
            while True:
                escalation = await self.escalation_queue.get_next_request()
                if not escalation:
                    break
                
                assignment_result = await self.assign_to_agent(escalation.escalation_id)
                if not assignment_result:
                    # No available agent, add back to queue
                    await self.escalation_queue.add_request(escalation)
                    break
        
        except Exception as e:
            logger.error(f"Error processing pending assignments: {str(e)}")
    
    async def _start_notification_processor(self):
        """Start notification processing background task"""        while True:
            try:
                # Process notifications from queue
                notification = await self.notification_queue.get()
                await self._send_notification(notification)
            except Exception as e:
                logger.error(f"Notification processing error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _notify_escalation_created(self, escalation: EscalationRequest):
        """Notify stakeholders of new escalation"""        notification = {
            "type": "escalation_created",
            "escalation_id": escalation.escalation_id,
            "priority": escalation.priority.value,
            "trigger": escalation.trigger.value,
            "user_id": escalation.user_id,
            "estimated_wait": escalation.estimated_wait_time
        }
        
        await self.notification_queue.put(notification)
    
    async def _notify_agent_assignment(self, agent: HumanAgent, escalation: EscalationRequest):
        """Notify agent of new assignment"""        notification = {
            "type": "agent_assignment",
            "agent_id": agent.agent_id,
            "agent_email": agent.email,
            "escalation_id": escalation.escalation_id,
            "priority": escalation.priority.value,
            "reason": escalation.reason,
            "customer_tier": escalation.customer_tier
        }
        
        await self.notification_queue.put(notification)
    
    async def _notify_escalation_resolved(self, escalation: EscalationRequest):
        """Notify stakeholders of escalation resolution"""        notification = {
            "type": "escalation_resolved",
            "escalation_id": escalation.escalation_id,
            "resolution_time": escalation.resolution_time,
            "rating": escalation.resolution_rating,
            "user_id": escalation.user_id
        }
        
        await self.notification_queue.put(notification)
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send notification via appropriate channel"""        try:
            notification_type = notification["type"]
            
            if notification_type == "agent_assignment":
                # Send email/internal message to agent
                agent_email = notification["agent_email"]
                subject = f"New Escalation Assignment - Priority {notification['priority']}"
                body = f"""                New escalation assigned to you:
                
                Escalation ID: {notification['escalation_id']}
                Priority: {notification['priority']}
                Customer Tier: {notification['customer_tier']}
                Reason: {notification['reason']}
                
                Please log into the support dashboard to handle this escalation.
                """                
                await self._send_email(agent_email, subject, body)
            
            # Log all notifications
            logger.info(f"Sent notification: {notification_type} - {notification.get('escalation_id')}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    async def _send_email(self, to_email: str, subject: str, body: str):
        """Send email notification"""        try:
            # In real implementation, would use proper email service
            logger.info(f"Email notification sent to {to_email}: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
    
    async def _cache_escalation(self, escalation: EscalationRequest):
        """Cache escalation in Redis"""        try:
            escalation_data = {
                "escalation_id": escalation.escalation_id,
                "conversation_id": escalation.conversation_id,
                "user_id": escalation.user_id,
                "trigger": escalation.trigger.value,
                "priority": escalation.priority.value,
                "reason": escalation.reason,
                "context": escalation.context,
                "created_at": escalation.created_at.isoformat(),
                "requested_specialty": escalation.requested_specialty.value if escalation.requested_specialty else None,
                "assigned_agent": escalation.assigned_agent,
                "assigned_at": escalation.assigned_at.isoformat() if escalation.assigned_at else None,
                "resolved_at": escalation.resolved_at.isoformat() if escalation.resolved_at else None,
                "resolution_time": escalation.resolution_time,
                "customer_tier": escalation.customer_tier,
                "estimated_wait_time": escalation.estimated_wait_time
            }
            
            await self.redis_client.setex(
                f"escalation:{escalation.escalation_id}",
                86400,  # 24 hours TTL
                json.dumps(escalation_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache escalation {escalation.escalation_id}: {str(e)}")
    
    async def _cache_agent(self, agent: HumanAgent):
        """Cache agent in Redis"""        try:
            agent_data = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "email": agent.email,
                "specialties": [s.value for s in agent.specialties],
                "status": agent.status.value,
                "current_workload": agent.current_workload,
                "max_concurrent_cases": agent.max_concurrent_cases,
                "resolution_rate": agent.resolution_rate,
                "satisfaction_rating": agent.satisfaction_rating,
                "cases_resolved_today": agent.cases_resolved_today,
                "languages": agent.languages,
                "last_active": agent.last_active.isoformat()
            }
            
            await self.redis_client.setex(
                f"agent:{agent.agent_id}",
                3600,  # 1 hour TTL
                json.dumps(agent_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache agent {agent.agent_id}: {str(e)}")
    
    async def _get_escalation(self, escalation_id: str) -> Optional[EscalationRequest]:
        """Get escalation from cache"""        try:
            data = await self.redis_client.get(f"escalation:{escalation_id}")
            if not data:
                return None
            
            escalation_data = json.loads(data)
            
            escalation = EscalationRequest(
                escalation_id=escalation_data["escalation_id"],
                conversation_id=escalation_data["conversation_id"],
                user_id=escalation_data["user_id"],
                trigger=EscalationTrigger(escalation_data["trigger"]),
                priority=EscalationPriority(escalation_data["priority"]),
                reason=escalation_data["reason"],
                context=escalation_data.get("context", {}),
                created_at=datetime.fromisoformat(escalation_data["created_at"]),
                requested_specialty=AgentSpecialty(escalation_data["requested_specialty"]) if escalation_data.get("requested_specialty") else None,
                assigned_agent=escalation_data.get("assigned_agent"),
                assigned_at=datetime.fromisoformat(escalation_data["assigned_at"]) if escalation_data.get("assigned_at") else None,
                resolved_at=datetime.fromisoformat(escalation_data["resolved_at"]) if escalation_data.get("resolved_at") else None,
                resolution_time=escalation_data.get("resolution_time"),
                customer_tier=escalation_data.get("customer_tier", "free"),
                estimated_wait_time=escalation_data.get("estimated_wait_time")
            )
            
            return escalation
            
        except Exception as e:
            logger.error(f"Failed to get escalation {escalation_id}: {str(e)}")
            return None
    
    async def get_escalation_analytics(self) -> Dict[str, Any]:
        """Get escalation analytics and metrics"""        queue_stats = await self.escalation_queue.get_queue_stats()
        
        # Agent performance metrics
        agent_metrics = {}
        for agent_id, agent in self.human_agents.items():
            agent_metrics[agent_id] = {
                "name": agent.name,
                "status": agent.status.value,
                "current_workload": agent.current_workload,
                "cases_resolved_today": agent.cases_resolved_today,
                "satisfaction_rating": agent.satisfaction_rating,
                "resolution_rate": agent.resolution_rate
            }
        
        return {
            "queue_statistics": queue_stats,
            "agent_metrics": agent_metrics,
            "escalation_stats": dict(self.escalation_stats),
            "average_resolution_time": sum(self.performance_metrics["resolution_times"]) / len(self.performance_metrics["resolution_times"]) if self.performance_metrics["resolution_times"] else 0,
            "total_agents": len(self.human_agents),
            "available_agents": len([a for a in self.human_agents.values() if a.status == AgentStatus.AVAILABLE])
        }
