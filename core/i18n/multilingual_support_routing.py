"""Multilingual Customer Support Routing Engine - Ainflue Platform
================================================================================
Module: core/i18n/multilingual_support_routing.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Multilingual Support Routing Engine - Customer Service Optimization
Responsibility: Intelligent routing, agent matching, real-time translation, support analytics
Technologies: Python, NLP, ML routing, Real-time translation, Support optimization
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Request analysis → Language detection → Agent matching → Skill assessment → 
Workload balancing → Real-time routing → Translation support → Performance tracking
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import random
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class SupportChannel(Enum):
    """Customer support channels"""
    LIVE_CHAT = "live_chat"
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    SOCIAL_MEDIA = "social_media"
    TICKET_SYSTEM = "ticket_system"
    MOBILE_APP = "mobile_app"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    FACEBOOK_MESSENGER = "facebook_messenger"


class Priority(Enum):
    """Support request priority levels"""
    CRITICAL = "critical"        # System down, security issues
    HIGH = "high"               # Payment issues, account access
    MEDIUM = "medium"           # Feature requests, general questions
    LOW = "low"                 # Documentation, non-urgent


class SupportCategory(Enum):
    """Support request categories"""
    TECHNICAL_ISSUE = "technical"
    BILLING_PAYMENT = "billing"
    ACCOUNT_ACCESS = "account"
    FEATURE_REQUEST = "feature"
    BUG_REPORT = "bug"
    SALES_INQUIRY = "sales"
    INTEGRATION_HELP = "integration"
    COMPLIANCE_LEGAL = "compliance"
    DATA_PROTECTION = "data_protection"
    PLATFORM_TRAINING = "training"


class AgentStatus(Enum):
    """Agent availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    OFFLINE = "offline"
    IN_TRAINING = "training"
    ON_BREAK = "break"


@dataclass
class SupportAgent:
    """Customer support agent profile"""
    agent_id: str
    name: str
    languages: List[str]  # Language codes with proficiency
    language_proficiency: Dict[str, float]  # Language -> proficiency score (0-1)
    specializations: List[SupportCategory]
    channels: List[SupportChannel]
    timezone: str
    working_hours: Dict[str, Tuple[str, str]]  # day -> (start, end)
    status: AgentStatus = AgentStatus.OFFLINE
    current_workload: int = 0
    max_concurrent_tickets: int = 5
    average_resolution_time: int = 1800  # seconds
    customer_satisfaction_score: float = 4.5  # 1-5 scale
    total_tickets_resolved: int = 0
    escalation_rate: float = 0.05
    first_response_time: int = 300  # seconds
    availability_score: float = 0.95
    skill_ratings: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SupportRequest:
    """Customer support request"""
    request_id: str
    customer_id: str
    channel: SupportChannel
    language: str
    detected_language_confidence: float
    category: SupportCategory
    priority: Priority
    subject: str
    description: str
    metadata: Dict[str, Any]
    timestamp: datetime
    customer_timezone: str = "UTC"
    requires_real_time: bool = False
    sensitive_data: bool = False
    technical_level: str = "basic"  # basic, intermediate, advanced
    customer_tier: str = "standard"  # free, standard, premium, enterprise
    previous_interactions: int = 0
    estimated_complexity: float = 0.5  # 0-1 scale
    attachments: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class RoutingResult:
    """Support routing result"""
    assigned_agent: Optional[SupportAgent]
    routing_score: float
    estimated_wait_time: int  # seconds
    alternative_agents: List[Tuple[SupportAgent, float]]  # (agent, score)
    routing_reason: str
    requires_translation: bool
    translation_direction: Tuple[str, str]  # (from_lang, to_lang)
    escalation_path: List[str]
    sla_target: int  # response time target in seconds
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class MultilingualSupportRouter:
    """Advanced multilingual customer support routing engine"""
    
    def __init__(self):
        self.agents = {}
        self.active_tickets = {}
        self.routing_queue = deque()
        self.language_capabilities = {}
        self.routing_algorithms = {}
        self.performance_analytics = {}
        self.escalation_rules = {}
        self.sla_targets = {}
        self.translation_engine = None
        
        # Initialize routing components
        self._initialize_routing_algorithms()
        self._initialize_sla_targets()
        self._initialize_escalation_rules()
        self._initialize_performance_tracking()
    
    def _initialize_routing_algorithms(self):
        """Initialize intelligent routing algorithms"""
        
        self.routing_algorithms = {
            "language_match": {
                "weight": 0.3,
                "function": self._calculate_language_score
            },
            "specialization_match": {
                "weight": 0.25,
                "function": self._calculate_specialization_score
            },
            "workload_balance": {
                "weight": 0.2,
                "function": self._calculate_workload_score
            },
            "performance_rating": {
                "weight": 0.15,
                "function": self._calculate_performance_score
            },
            "availability": {
                "weight": 0.1,
                "function": self._calculate_availability_score
            }
        }
    
    def _initialize_sla_targets(self):
        """Initialize SLA targets by priority and channel"""
        
        self.sla_targets = {
            Priority.CRITICAL: {
                SupportChannel.LIVE_CHAT: 60,      # 1 minute
                SupportChannel.PHONE: 30,          # 30 seconds
                SupportChannel.EMAIL: 3600,        # 1 hour
                SupportChannel.TICKET_SYSTEM: 1800  # 30 minutes
            },
            Priority.HIGH: {
                SupportChannel.LIVE_CHAT: 300,     # 5 minutes
                SupportChannel.PHONE: 120,         # 2 minutes
                SupportChannel.EMAIL: 14400,       # 4 hours
                SupportChannel.TICKET_SYSTEM: 7200  # 2 hours
            },
            Priority.MEDIUM: {
                SupportChannel.LIVE_CHAT: 600,     # 10 minutes
                SupportChannel.PHONE: 300,         # 5 minutes
                SupportChannel.EMAIL: 86400,       # 24 hours
                SupportChannel.TICKET_SYSTEM: 43200 # 12 hours
            },
            Priority.LOW: {
                SupportChannel.LIVE_CHAT: 1800,    # 30 minutes
                SupportChannel.PHONE: 900,         # 15 minutes
                SupportChannel.EMAIL: 172800,      # 48 hours
                SupportChannel.TICKET_SYSTEM: 86400 # 24 hours
            }
        }
    
    def _initialize_escalation_rules(self):
        """Initialize escalation rules and paths"""
        
        self.escalation_rules = {
            SupportCategory.TECHNICAL_ISSUE: {
                "levels": ["L1_Support", "L2_Technical", "L3_Engineering", "Senior_Architect"],
                "auto_escalate_after": 3600,  # 1 hour
                "escalate_on_keywords": ["bug", "error", "crash", "outage", "performance"]
            },
            SupportCategory.BILLING_PAYMENT: {
                "levels": ["Billing_Specialist", "Billing_Manager", "Finance_Team"],
                "auto_escalate_after": 1800,  # 30 minutes
                "escalate_on_keywords": ["refund", "charge", "payment failed", "billing error"]
            },
            SupportCategory.COMPLIANCE_LEGAL: {
                "levels": ["Compliance_Officer", "Legal_Team", "Data_Protection_Officer"],
                "auto_escalate_after": 900,   # 15 minutes
                "escalate_on_keywords": ["gdpr", "privacy", "legal", "compliance", "audit"]
            },
            SupportCategory.SALES_INQUIRY: {
                "levels": ["Sales_Rep", "Sales_Manager", "Enterprise_Sales"],
                "auto_escalate_after": 7200,  # 2 hours
                "escalate_on_keywords": ["enterprise", "custom", "bulk", "partnership"]
            }
        }
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking and analytics"""
        
        self.performance_analytics = {
            "routing_accuracy": deque(maxlen=1000),
            "response_times": defaultdict(list),
            "resolution_times": defaultdict(list),
            "customer_satisfaction": defaultdict(list),
            "language_coverage": defaultdict(int),
            "escalation_rates": defaultdict(list),
            "agent_utilization": defaultdict(list),
            "sla_compliance": defaultdict(list)
        }
    
    async def add_agent(self, agent: SupportAgent):
        """Add support agent to the routing system"""
        self.agents[agent.agent_id] = agent
        
        # Update language capabilities
        for lang in agent.languages:
            if lang not in self.language_capabilities:
                self.language_capabilities[lang] = []
            self.language_capabilities[lang].append(agent.agent_id)
        
        logger.info(f"Added agent {agent.name} with languages: {agent.languages}")
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent availability status"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            logger.info(f"Updated agent {agent_id} status to {status.value}")
    
    async def route_support_request(self, request: SupportRequest) -> RoutingResult:
        """Route support request to the best available agent"""
        
        try:
            # Get available agents
            available_agents = self._get_available_agents(request)
            
            if not available_agents:
                return await self._handle_no_agents_available(request)
            
            # Calculate routing scores for each agent
            agent_scores = []
            for agent in available_agents:
                score = await self._calculate_routing_score(request, agent)
                agent_scores.append((agent, score))
            
            # Sort by score (highest first)
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best agent
            best_agent, best_score = agent_scores[0]
            
            # Assign ticket to agent
            await self._assign_ticket(request, best_agent)
            
            # Determine if translation is needed
            requires_translation = self._requires_translation(request, best_agent)
            translation_direction = self._get_translation_direction(request, best_agent)
            
            # Get SLA target
            sla_target = self.sla_targets.get(request.priority, {}).get(request.channel, 3600)
            
            # Calculate estimated wait time
            wait_time = self._calculate_wait_time(best_agent, request)
            
            # Create escalation path
            escalation_path = self._create_escalation_path(request)
            
            result = RoutingResult(
                assigned_agent=best_agent,
                routing_score=best_score,
                estimated_wait_time=wait_time,
                alternative_agents=agent_scores[1:4],  # Top 3 alternatives
                routing_reason=self._generate_routing_reason(request, best_agent, best_score),
                requires_translation=requires_translation,
                translation_direction=translation_direction,
                escalation_path=escalation_path,
                sla_target=sla_target,
                routing_metadata={
                    "algorithm_scores": self._get_algorithm_breakdown(request, best_agent),
                    "queue_position": len(self.routing_queue),
                    "peak_hours": self._is_peak_hours(request.customer_timezone),
                    "customer_history": request.previous_interactions
                }
            )
            
            # Track routing analytics
            await self._track_routing_analytics(request, result)
            
            logger.info(f"Routed request {request.request_id} to agent {best_agent.name} (score: {best_score:.3f})")
            
            return result
        
        except Exception as e:
            logger.error(f"Error routing support request: {e}")
            return await self._handle_routing_error(request, str(e))
    
    def _get_available_agents(self, request: SupportRequest) -> List[SupportAgent]:
        """Get available agents for the request"""
        available = []
        
        for agent in self.agents.values():
            # Check basic availability
            if agent.status not in [AgentStatus.AVAILABLE, AgentStatus.AWAY]:
                continue
            
            # Check workload capacity
            if agent.current_workload >= agent.max_concurrent_tickets:
                continue
            
            # Check channel support
            if request.channel not in agent.channels:
                continue
            
            # Check working hours
            if not self._is_agent_in_working_hours(agent, request.timestamp):
                continue
            
            available.append(agent)
        
        return available
    
    async def _calculate_routing_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate comprehensive routing score for agent-request pair"""
        
        total_score = 0.0
        
        for algorithm_name, config in self.routing_algorithms.items():
            algorithm_score = config["function"](request, agent)
            weighted_score = algorithm_score * config["weight"]
            total_score += weighted_score
        
        # Apply penalty factors
        total_score = self._apply_penalty_factors(total_score, request, agent)
        
        return min(max(total_score, 0.0), 1.0)  # Clamp to [0, 1]
    
    def _calculate_language_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate language matching score"""
        
        # Perfect match
        if request.language in agent.language_proficiency:
            return agent.language_proficiency[request.language]
        
        # Check for language family matches (simplified)
        language_families = {
            "en": ["en-US", "en-GB", "en-CA", "en-AU"],
            "es": ["es-ES", "es-MX", "es-AR", "es-CO"],
            "fr": ["fr-FR", "fr-CA", "fr-BE", "fr-CH"],
            "ar": ["ar-SA", "ar-EG", "ar-MA", "ar-AE"],
            "zh": ["zh-CN", "zh-TW", "zh-HK"]
        }
        
        for base_lang, variants in language_families.items():
            if request.language in variants and base_lang in agent.language_proficiency:
                return agent.language_proficiency[base_lang] * 0.9  # Slight penalty for variant
        
        # Check if agent has English as fallback
        if "en" in agent.language_proficiency and request.language != "en":
            return agent.language_proficiency["en"] * 0.3  # Heavy penalty for translation
        
        return 0.1  # Minimal score if no language match
    
    def _calculate_specialization_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate specialization matching score"""
        
        if request.category in agent.specializations:
            # Check skill rating for specific category
            skill_key = request.category.value
            if skill_key in agent.skill_ratings:
                return agent.skill_ratings[skill_key]
            return 0.8  # Default high score for specialization
        
        # Check for related specializations
        related_categories = {
            SupportCategory.TECHNICAL_ISSUE: [SupportCategory.BUG_REPORT, SupportCategory.INTEGRATION_HELP],
            SupportCategory.BILLING_PAYMENT: [SupportCategory.ACCOUNT_ACCESS],
            SupportCategory.COMPLIANCE_LEGAL: [SupportCategory.DATA_PROTECTION]
        }
        
        if request.category in related_categories:
            for related in related_categories[request.category]:
                if related in agent.specializations:
                    return 0.6  # Moderate score for related specialization
        
        return 0.2  # Low score for no specialization match
    
    def _calculate_workload_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate workload balancing score"""
        
        utilization = agent.current_workload / agent.max_concurrent_tickets
        
        # Prefer agents with lower utilization
        if utilization <= 0.3:
            return 1.0
        elif utilization <= 0.6:
            return 0.8
        elif utilization <= 0.8:
            return 0.5
        else:
            return 0.2
    
    def _calculate_performance_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate performance-based score"""
        
        # Normalize performance metrics to [0, 1]
        csat_score = min(agent.customer_satisfaction_score / 5.0, 1.0)
        availability_score = agent.availability_score
        escalation_penalty = max(0, 1.0 - (agent.escalation_rate * 10))  # Penalty for high escalation
        
        # Weighted combination
        performance_score = (
            csat_score * 0.4 +
            availability_score * 0.3 +
            escalation_penalty * 0.3
        )
        
        return performance_score
    
    def _calculate_availability_score(self, request: SupportRequest, agent: SupportAgent) -> float:
        """Calculate availability-based score"""
        
        if agent.status == AgentStatus.AVAILABLE:
            return 1.0
        elif agent.status == AgentStatus.AWAY:
            return 0.7
        else:
            return 0.0
    
    def _apply_penalty_factors(self, score: float, request: SupportRequest, agent: SupportAgent) -> float:
        """Apply penalty factors to routing score"""
        
        # Timezone mismatch penalty
        if not self._is_timezone_compatible(request.customer_timezone, agent.timezone):
            score *= 0.9
        
        # Customer tier preference
        if request.customer_tier == "enterprise" and "enterprise" not in agent.specializations:
            score *= 0.8
        
        # Technical level mismatch
        if request.technical_level == "advanced" and agent.skill_ratings.get("technical_expertise", 0.5) < 0.7:
            score *= 0.7
        
        # Real-time requirement
        if request.requires_real_time and request.channel not in [SupportChannel.LIVE_CHAT, SupportChannel.PHONE]:
            score *= 0.6
        
        return score
    
    async def _assign_ticket(self, request: SupportRequest, agent: SupportAgent):
        """Assign ticket to agent"""
        
        # Update agent workload
        agent.current_workload += 1
        
        # Add to active tickets
        self.active_tickets[request.request_id] = {
            "agent_id": agent.agent_id,
            "start_time": datetime.now(),
            "request": request,
            "status": "assigned"
        }
        
        logger.info(f"Assigned ticket {request.request_id} to agent {agent.name}")
    
    def _requires_translation(self, request: SupportRequest, agent: SupportAgent) -> bool:
        """Check if translation is required"""
        
        # Direct language match
        if request.language in agent.language_proficiency:
            return False
        
        # Agent doesn't speak customer's language well enough
        if request.language not in agent.language_proficiency:
            return True
        
        # Low proficiency requires translation assistance
        if agent.language_proficiency.get(request.language, 0) < 0.7:
            return True
        
        return False
    
    def _get_translation_direction(self, request: SupportRequest, agent: SupportAgent) -> Tuple[str, str]:
        """Get translation direction (from_lang, to_lang)"""
        
        # Find agent's best language
        best_agent_lang = max(agent.language_proficiency.items(), key=lambda x: x[1])[0]
        
        return (request.language, best_agent_lang)
    
    def _calculate_wait_time(self, agent: SupportAgent, request: SupportRequest) -> int:
        """Calculate estimated wait time"""
        
        base_time = agent.first_response_time
        
        # Adjust for workload
        workload_multiplier = 1 + (agent.current_workload * 0.2)
        
        # Adjust for priority
        priority_multipliers = {
            Priority.CRITICAL: 0.5,
            Priority.HIGH: 0.7,
            Priority.MEDIUM: 1.0,
            Priority.LOW: 1.5
        }
        
        priority_multiplier = priority_multipliers.get(request.priority, 1.0)
        
        estimated_time = int(base_time * workload_multiplier * priority_multiplier)
        
        return estimated_time
    
    def _create_escalation_path(self, request: SupportRequest) -> List[str]:
        """Create escalation path for the request"""
        
        rules = self.escalation_rules.get(request.category)
        if not rules:
            return ["Supervisor", "Manager"]
        
        return rules["levels"]
    
    def _generate_routing_reason(self, request: SupportRequest, agent: SupportAgent, score: float) -> str:
        """Generate human-readable routing reason"""
        
        reasons = []
        
        # Language match
        if request.language in agent.language_proficiency:
            proficiency = agent.language_proficiency[request.language]
            if proficiency >= 0.9:
                reasons.append(f"Native {request.language} speaker")
            else:
                reasons.append(f"Fluent in {request.language}")
        
        # Specialization
        if request.category in agent.specializations:
            reasons.append(f"Specialized in {request.category.value}")
        
        # Performance
        if agent.customer_satisfaction_score >= 4.5:
            reasons.append("High customer satisfaction rating")
        
        # Availability
        if agent.current_workload < agent.max_concurrent_tickets * 0.5:
            reasons.append("Available capacity")
        
        if not reasons:
            reasons.append("Best available match")
        
        return "; ".join(reasons)
    
    def _get_algorithm_breakdown(self, request: SupportRequest, agent: SupportAgent) -> Dict[str, float]:
        """Get breakdown of algorithm scores"""
        
        breakdown = {}
        for algorithm_name, config in self.routing_algorithms.items():
            score = config["function"](request, agent)
            breakdown[algorithm_name] = score
        
        return breakdown
    
    def _is_agent_in_working_hours(self, agent: SupportAgent, timestamp: datetime) -> bool:
        """Check if agent is in working hours"""
        
        # Simplified check - in production, use proper timezone handling
        day_name = timestamp.strftime("%A").lower()
        
        if day_name not in agent.working_hours:
            return False
        
        start_time, end_time = agent.working_hours[day_name]
        current_time = timestamp.strftime("%H:%M")
        
        return start_time <= current_time <= end_time
    
    def _is_timezone_compatible(self, customer_tz: str, agent_tz: str) -> bool:
        """Check timezone compatibility"""
        
        # Simplified compatibility check
        # In production, use proper timezone libraries
        compatible_zones = {
            "US/Eastern": ["US/Central", "US/Pacific"],
            "Europe/London": ["Europe/Paris", "Europe/Berlin"],
            "Asia/Tokyo": ["Asia/Shanghai", "Asia/Seoul"]
        }
        
        if customer_tz == agent_tz:
            return True
        
        return agent_tz in compatible_zones.get(customer_tz, [])
    
    def _is_peak_hours(self, timezone: str) -> bool:
        """Check if current time is peak hours for timezone"""
        
        # Simplified peak hours check (9 AM - 5 PM)
        current_hour = datetime.now().hour
        return 9 <= current_hour <= 17
    
    async def _handle_no_agents_available(self, request: SupportRequest) -> RoutingResult:
        """Handle case when no agents are available"""
        
        # Add to queue
        self.routing_queue.append(request)
        
        # Estimate wait time based on queue length
        estimated_wait = len(self.routing_queue) * 300  # 5 minutes per request in queue
        
        return RoutingResult(
            assigned_agent=None,
            routing_score=0.0,
            estimated_wait_time=estimated_wait,
            alternative_agents=[],
            routing_reason="No agents currently available - added to priority queue",
            requires_translation=False,
            translation_direction=("", ""),
            escalation_path=self._create_escalation_path(request),
            sla_target=self.sla_targets.get(request.priority, {}).get(request.channel, 3600),
            routing_metadata={
                "queue_position": len(self.routing_queue),
                "queue_length": len(self.routing_queue)
            }
        )
    
    async def _handle_routing_error(self, request: SupportRequest, error: str) -> RoutingResult:
        """Handle routing errors"""
        
        logger.error(f"Routing error for request {request.request_id}: {error}")
        
        return RoutingResult(
            assigned_agent=None,
            routing_score=0.0,
            estimated_wait_time=0,
            alternative_agents=[],
            routing_reason=f"Routing error: {error}",
            requires_translation=False,
            translation_direction=("", ""),
            escalation_path=["Technical_Support", "Engineering"],
            sla_target=3600,
            routing_metadata={"error": error}
        )
    
    async def _track_routing_analytics(self, request: SupportRequest, result: RoutingResult):
        """Track routing analytics and performance"""
        
        # Track routing accuracy
        self.performance_analytics["routing_accuracy"].append(result.routing_score)
        
        # Track language coverage
        self.performance_analytics["language_coverage"][request.language] += 1
        
        # Track response times by priority
        self.performance_analytics["response_times"][request.priority.value].append(result.estimated_wait_time)
        
        # Track SLA targets
        sla_met = result.estimated_wait_time <= result.sla_target
        self.performance_analytics["sla_compliance"][request.priority.value].append(sla_met)
    
    async def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive routing analytics"""
        
        analytics = {}
        
        # Average routing score
        if self.performance_analytics["routing_accuracy"]:
            analytics["average_routing_score"] = sum(self.performance_analytics["routing_accuracy"]) / len(self.performance_analytics["routing_accuracy"])
        else:
            analytics["average_routing_score"] = 0.0
        
        # Language coverage
        analytics["language_coverage"] = dict(self.performance_analytics["language_coverage"])
        
        # SLA compliance rates
        sla_compliance = {}
        for priority, compliance_list in self.performance_analytics["sla_compliance"].items():
            if compliance_list:
                sla_compliance[priority] = sum(compliance_list) / len(compliance_list)
            else:
                sla_compliance[priority] = 0.0
        analytics["sla_compliance_rates"] = sla_compliance
        
        # Agent utilization
        agent_utilization = {}
        for agent_id, agent in self.agents.items():
            utilization = agent.current_workload / agent.max_concurrent_tickets
            agent_utilization[agent_id] = {
                "name": agent.name,
                "utilization": utilization,
                "status": agent.status.value,
                "languages": agent.languages
            }
        analytics["agent_utilization"] = agent_utilization
        
        # Queue statistics
        analytics["queue_statistics"] = {
            "current_queue_length": len(self.routing_queue),
            "active_tickets": len(self.active_tickets),
            "total_agents": len(self.agents),
            "available_agents": len([a for a in self.agents.values() if a.status == AgentStatus.AVAILABLE])
        }
        
        return analytics
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages by agents"""
        return list(self.language_capabilities.keys())
    
    def get_language_coverage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed language coverage statistics"""
        
        coverage_stats = {}
        
        for language, agent_ids in self.language_capabilities.items():
            agents = [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
            
            coverage_stats[language] = {
                "total_agents": len(agents),
                "available_agents": len([a for a in agents if a.status == AgentStatus.AVAILABLE]),
                "average_proficiency": sum(a.language_proficiency.get(language, 0) for a in agents) / len(agents) if agents else 0,
                "specializations_covered": list(set().union(*[a.specializations for a in agents])),
                "channels_supported": list(set().union(*[a.channels for a in agents]))
            }
        
        return coverage_stats