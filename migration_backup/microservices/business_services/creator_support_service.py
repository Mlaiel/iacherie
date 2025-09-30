"""
Creator Support Service - Enterprise Microservice
===============================================

Advanced support management system for creators with intelligent ticket routing,
automated responses, multi-channel support, and comprehensive help desk integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import uuid
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupportTicketStatus(str, Enum):
    """Support ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class SupportTicketPriority(str, Enum):
    """Support ticket priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class SupportCategory(str, Enum):
    """Support categories."""
    TECHNICAL_ISSUE = "technical_issue"
    ACCOUNT_PROBLEM = "account_problem"
    PAYMENT_BILLING = "payment_billing"
    CONTENT_UPLOAD = "content_upload"
    COLLABORATION = "collaboration"
    PLATFORM_USAGE = "platform_usage"
    COPYRIGHT_DMCA = "copyright_dmca"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_CONCERN = "security_concern"
    API_SUPPORT = "api_support"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    GENERAL_INQUIRY = "general_inquiry"


class SupportChannel(str, Enum):
    """Support communication channels."""
    EMAIL = "email"
    LIVE_CHAT = "live_chat"
    PHONE = "phone"
    IN_APP = "in_app"
    COMMUNITY_FORUM = "community_forum"
    VIDEO_CALL = "video_call"
    REMOTE_ASSISTANCE = "remote_assistance"
    DISCORD = "discord"
    SLACK = "slack"


class AgentRole(str, Enum):
    """Support agent roles."""
    L1_SUPPORT = "l1_support"          # Level 1 - General support
    L2_TECHNICAL = "l2_technical"      # Level 2 - Technical specialists
    L3_EXPERT = "l3_expert"            # Level 3 - Expert specialists
    BILLING_SPECIALIST = "billing_specialist"
    SECURITY_SPECIALIST = "security_specialist"
    DEVELOPER_SUPPORT = "developer_support"
    COMMUNITY_MANAGER = "community_manager"
    SENIOR_ENGINEER = "senior_engineer"


class SatisfactionRating(str, Enum):
    """Customer satisfaction ratings."""
    VERY_DISSATISFIED = "very_dissatisfied"
    DISSATISFIED = "dissatisfied"
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    VERY_SATISFIED = "very_satisfied"


@dataclass
class SupportAgent:
    """Support agent information."""
    id: str
    name: str
    email: str
    role: AgentRole
    specializations: List[SupportCategory]
    languages: List[str]
    active: bool = True
    max_concurrent_tickets: int = 10
    current_ticket_count: int = 0
    average_response_time: float = 0.0  # in hours
    satisfaction_rating: float = 0.0
    total_tickets_handled: int = 0


@dataclass
class SupportMessage:
    """Support conversation message."""
    id: str
    ticket_id: str
    sender_id: str
    sender_type: str  # "creator", "agent", "system"
    content: str
    timestamp: datetime
    attachments: List[str] = field(default_factory=list)
    is_internal: bool = False
    auto_generated: bool = False


class SupportTicketRequest(BaseModel):
    """Support ticket creation request."""
    creator_id: str = Field(..., description="Creator requesting support")
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., description="Detailed description")
    category: SupportCategory = Field(..., description="Support category")
    priority: SupportTicketPriority = Field(default=SupportTicketPriority.NORMAL)
    preferred_channel: SupportChannel = Field(default=SupportChannel.EMAIL)
    attachments: List[str] = Field(default_factory=list, description="Attachment URLs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SupportTicket(BaseModel):
    """Complete support ticket."""
    id: str = Field(..., description="Ticket identifier")
    creator_id: str = Field(..., description="Creator ID")
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., description="Original description")
    category: SupportCategory = Field(..., description="Support category")
    priority: SupportTicketPriority = Field(..., description="Priority level")
    status: SupportTicketStatus = Field(default=SupportTicketStatus.OPEN)
    assigned_agent_id: Optional[str] = Field(None, description="Assigned agent ID")
    preferred_channel: SupportChannel = Field(..., description="Preferred communication channel")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    first_response_at: Optional[datetime] = Field(None, description="First agent response time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    closed_at: Optional[datetime] = Field(None, description="Closure time")
    satisfaction_rating: Optional[SatisfactionRating] = Field(None, description="Customer satisfaction")
    resolution_summary: Optional[str] = Field(None, description="Resolution summary")
    tags: List[str] = Field(default_factory=list, description="Ticket tags")
    escalation_count: int = Field(default=0, description="Number of escalations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SupportAnalytics(BaseModel):
    """Support analytics and metrics."""
    period_start: datetime
    period_end: datetime
    total_tickets: int
    tickets_by_status: Dict[SupportTicketStatus, int]
    tickets_by_category: Dict[SupportCategory, int]
    tickets_by_priority: Dict[SupportTicketPriority, int]
    average_response_time: float  # hours
    average_resolution_time: float  # hours
    customer_satisfaction_score: float
    first_response_rate: float  # percentage within SLA
    resolution_rate: float  # percentage resolved
    escalation_rate: float  # percentage escalated
    agent_performance: Dict[str, Dict[str, float]]


class CreatorSupportService:
    """
    Enterprise Creator Support Service
    
    Provides comprehensive support management with intelligent routing,
    automated responses, multi-channel communication, and detailed analytics.
    """
    
    def __init__(self):
        self.tickets: Dict[str, SupportTicket] = {}
        self.messages: Dict[str, List[SupportMessage]] = defaultdict(list)  # ticket_id -> messages
        self.agents: Dict[str, SupportAgent] = {}
        self.creator_tickets: Dict[str, List[str]] = defaultdict(list)  # creator_id -> ticket_ids
        self.knowledge_base: Dict[str, Dict[str, Any]] = {}
        self.auto_responses: Dict[SupportCategory, List[str]] = {}
        self.sla_targets: Dict[SupportPriority, Dict[str, float]] = {}
        self.escalation_rules: List[Dict[str, Any]] = []
        
        # Initialize system
        self._initialize_agents()
        self._initialize_knowledge_base()
        self._initialize_auto_responses()
        self._initialize_sla_targets()
        self._initialize_escalation_rules()
        
        logger.info("CreatorSupportService initialized successfully")
    
    def _initialize_agents(self):
        """Initialize support agents."""
        agents_data = [
            {
                "id": "agent_001",
                "name": "Alex Thompson",
                "email": "alex.thompson@ainflue.com",
                "role": AgentRole.L1_SUPPORT,
                "specializations": [SupportCategory.GENERAL_INQUIRY, SupportCategory.PLATFORM_USAGE],
                "languages": ["en", "es"],
                "max_concurrent_tickets": 15
            },
            {
                "id": "agent_002",
                "name": "Sarah Chen",
                "email": "sarah.chen@ainflue.com",
                "role": AgentRole.L2_TECHNICAL,
                "specializations": [SupportCategory.TECHNICAL_ISSUE, SupportCategory.BUG_REPORT],
                "languages": ["en", "zh"],
                "max_concurrent_tickets": 8
            },
            {
                "id": "agent_003",
                "name": "Marcus Johnson",
                "email": "marcus.johnson@ainflue.com",
                "role": AgentRole.BILLING_SPECIALIST,
                "specializations": [SupportCategory.PAYMENT_BILLING, SupportCategory.MONETIZATION],
                "languages": ["en"],
                "max_concurrent_tickets": 12
            },
            {
                "id": "agent_004",
                "name": "Dr. Emily Rodriguez",
                "email": "emily.rodriguez@ainflue.com",
                "role": AgentRole.L3_EXPERT,
                "specializations": [SupportCategory.SECURITY_CONCERN, SupportCategory.COPYRIGHT_DMCA],
                "languages": ["en", "es", "fr"],
                "max_concurrent_tickets": 5
            },
            {
                "id": "agent_005",
                "name": "David Kumar",
                "email": "david.kumar@ainflue.com",
                "role": AgentRole.DEVELOPER_SUPPORT,
                "specializations": [SupportCategory.API_SUPPORT, SupportCategory.TECHNICAL_ISSUE],
                "languages": ["en", "hi"],
                "max_concurrent_tickets": 6
            }
        ]
        
        for agent_data in agents_data:
            agent = SupportAgent(**agent_data)
            self.agents[agent.id] = agent
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base with common solutions."""
        self.knowledge_base = {
            "password_reset": {
                "title": "How to reset your password",
                "category": SupportCategory.ACCOUNT_PROBLEM,
                "solution": "Go to login page, click 'Forgot Password', enter your email, and follow the instructions.",
                "tags": ["password", "reset", "account", "login"],
                "views": 1250
            },
            "upload_failed": {
                "title": "Content upload failure troubleshooting",
                "category": SupportCategory.CONTENT_UPLOAD,
                "solution": "Check file format, size limits, and internet connection. Try uploading smaller chunks.",
                "tags": ["upload", "failure", "content", "troubleshoot"],
                "views": 890
            },
            "payment_declined": {
                "title": "Payment declined issues",
                "category": SupportCategory.PAYMENT_BILLING,
                "solution": "Verify card details, check bank balance, contact your bank, or try an alternative payment method.",
                "tags": ["payment", "declined", "billing", "card"],
                "views": 567
            },
            "api_rate_limit": {
                "title": "API rate limit exceeded",
                "category": SupportCategory.API_SUPPORT,
                "solution": "Implement exponential backoff, respect rate limits, consider upgrading your plan.",
                "tags": ["api", "rate_limit", "developer", "integration"],
                "views": 234
            }
        }
    
    def _initialize_auto_responses(self):
        """Initialize automated response templates."""
        self.auto_responses = {
            SupportCategory.TECHNICAL_ISSUE: [
                "Thank you for reporting this technical issue. Our team is investigating and will respond within 2 hours.",
                "We've received your technical support request. Please ensure you've tried clearing your browser cache."
            ],
            SupportCategory.ACCOUNT_PROBLEM: [
                "We're here to help with your account issue. Our specialists will review your case shortly.",
                "Account issues are our priority. We'll have someone look into this within 1 hour."
            ],
            SupportCategory.PAYMENT_BILLING: [
                "Thank you for contacting billing support. A specialist will review your payment concern immediately.",
                "We take payment issues seriously. Our billing team will respond within 30 minutes."
            ],
            SupportCategory.FEATURE_REQUEST: [
                "Thanks for your feature suggestion! We've forwarded it to our product team for evaluation.",
                "We appreciate your feedback. All feature requests are reviewed by our development team."
            ]
        }
    
    def _initialize_sla_targets(self):
        """Initialize SLA targets by priority."""
        self.sla_targets = {
            SupportTicketPriority.CRITICAL: {
                "first_response_hours": 0.25,  # 15 minutes
                "resolution_hours": 2.0
            },
            SupportTicketPriority.URGENT: {
                "first_response_hours": 1.0,  # 1 hour
                "resolution_hours": 4.0
            },
            SupportTicketPriority.HIGH: {
                "first_response_hours": 2.0,  # 2 hours
                "resolution_hours": 8.0
            },
            SupportTicketPriority.NORMAL: {
                "first_response_hours": 4.0,  # 4 hours
                "resolution_hours": 24.0
            },
            SupportTicketPriority.LOW: {
                "first_response_hours": 8.0,  # 8 hours
                "resolution_hours": 72.0
            }
        }
    
    def _initialize_escalation_rules(self):
        """Initialize escalation rules."""
        self.escalation_rules = [
            {
                "condition": "response_time_exceeded",
                "priority": SupportTicketPriority.CRITICAL,
                "threshold_hours": 0.5,
                "action": "escalate_to_l3"
            },
            {
                "condition": "resolution_time_exceeded", 
                "priority": SupportTicketPriority.URGENT,
                "threshold_hours": 6.0,
                "action": "escalate_to_senior"
            },
            {
                "condition": "multiple_escalations",
                "escalation_count": 2,
                "action": "escalate_to_management"
            },
            {
                "condition": "security_category",
                "category": SupportCategory.SECURITY_CONCERN,
                "action": "immediate_security_escalation"
            }
        ]
    
    async def create_ticket(self, request: SupportTicketRequest) -> str:
        """Create new support ticket."""
        try:
            ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
            
            # Auto-detect priority based on category and content
            priority = self._detect_priority(request.category, request.description)
            if request.priority != SupportTicketPriority.NORMAL:
                priority = request.priority  # Override if explicitly set
            
            # Create ticket
            ticket = SupportTicket(
                id=ticket_id,
                creator_id=request.creator_id,
                subject=request.subject,
                description=request.description,
                category=request.category,
                priority=priority,
                preferred_channel=request.preferred_channel,
                metadata=request.metadata
            )
            
            # Store ticket
            self.tickets[ticket_id] = ticket
            self.creator_tickets[request.creator_id].append(ticket_id)
            
            # Auto-assign agent
            assigned_agent = await self._auto_assign_agent(ticket)
            if assigned_agent:
                ticket.assigned_agent_id = assigned_agent.id
                assigned_agent.current_ticket_count += 1
            
            # Send auto-response
            await self._send_auto_response(ticket)
            
            # Check for knowledge base matches
            kb_suggestions = self._find_knowledge_base_matches(request.description)
            if kb_suggestions:
                await self._send_knowledge_base_suggestions(ticket_id, kb_suggestions)
            
            logger.info(f"Created support ticket {ticket_id} for creator {request.creator_id}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            raise
    
    def _detect_priority(self, category: SupportCategory, description: str) -> SupportTicketPriority:
        """Auto-detect ticket priority based on category and content."""
        description_lower = description.lower()
        
        # Critical keywords
        critical_keywords = ["urgent", "critical", "emergency", "down", "not working", "broken", "security breach"]
        if any(keyword in description_lower for keyword in critical_keywords):
            return SupportTicketPriority.CRITICAL
        
        # High priority categories
        high_priority_categories = [
            SupportCategory.SECURITY_CONCERN,
            SupportCategory.PAYMENT_BILLING,
            SupportCategory.COPYRIGHT_DMCA
        ]
        if category in high_priority_categories:
            return SupportTicketPriority.HIGH
        
        # Urgent keywords
        urgent_keywords = ["asap", "immediately", "quickly", "soon", "help me"]
        if any(keyword in description_lower for keyword in urgent_keywords):
            return SupportTicketPriority.URGENT
        
        # Default priority
        return SupportTicketPriority.NORMAL
    
    async def _auto_assign_agent(self, ticket: SupportTicket) -> Optional[SupportAgent]:
        """Auto-assign ticket to best available agent."""
        try:
            # Find agents with matching specializations
            specialized_agents = []
            for agent in self.agents.values():
                if (agent.active and 
                    ticket.category in agent.specializations and 
                    agent.current_ticket_count < agent.max_concurrent_tickets):
                    specialized_agents.append(agent)
            
            if not specialized_agents:
                # Find any available agent
                available_agents = [
                    agent for agent in self.agents.values()
                    if agent.active and agent.current_ticket_count < agent.max_concurrent_tickets
                ]
                if not available_agents:
                    return None
                specialized_agents = available_agents
            
            # Sort by workload and performance
            specialized_agents.sort(
                key=lambda a: (a.current_ticket_count, -a.satisfaction_rating, a.average_response_time)
            )
            
            return specialized_agents[0]
            
        except Exception as e:
            logger.error(f"Error auto-assigning agent: {e}")
            return None
    
    async def _send_auto_response(self, ticket: SupportTicket):
        """Send automated response for new ticket."""
        try:
            auto_responses = self.auto_responses.get(ticket.category, [])
            if auto_responses:
                response_content = auto_responses[0]  # Use first response
                
                message = SupportMessage(
                    id=f"msg_{uuid.uuid4().hex[:8]}",
                    ticket_id=ticket.id,
                    sender_id="system",
                    sender_type="system",
                    content=response_content,
                    timestamp=datetime.now(),
                    auto_generated=True
                )
                
                self.messages[ticket.id].append(message)
                logger.info(f"Sent auto-response for ticket {ticket.id}")
                
        except Exception as e:
            logger.error(f"Error sending auto-response: {e}")
    
    def _find_knowledge_base_matches(self, description: str) -> List[Dict[str, Any]]:
        """Find matching knowledge base articles."""
        description_lower = description.lower()
        matches = []
        
        for kb_id, kb_article in self.knowledge_base.items():
            # Check if any tags match the description
            for tag in kb_article["tags"]:
                if tag in description_lower:
                    matches.append({
                        "id": kb_id,
                        "title": kb_article["title"],
                        "solution": kb_article["solution"],
                        "relevance_score": description_lower.count(tag)
                    })
                    break
        
        # Sort by relevance score
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matches[:3]  # Return top 3 matches
    
    async def _send_knowledge_base_suggestions(self, ticket_id: str, suggestions: List[Dict[str, Any]]):
        """Send knowledge base suggestions to creator."""
        try:
            if not suggestions:
                return
            
            content = "Here are some articles that might help:\n\n"
            for suggestion in suggestions:
                content += f"• {suggestion['title']}: {suggestion['solution']}\n\n"
            content += "If these don't resolve your issue, we'll have an agent assist you shortly."
            
            message = SupportMessage(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                ticket_id=ticket_id,
                sender_id="system",
                sender_type="system",
                content=content,
                timestamp=datetime.now(),
                auto_generated=True
            )
            
            self.messages[ticket_id].append(message)
            logger.info(f"Sent knowledge base suggestions for ticket {ticket_id}")
            
        except Exception as e:
            logger.error(f"Error sending KB suggestions: {e}")
    
    async def add_message(
        self, 
        ticket_id: str, 
        sender_id: str, 
        sender_type: str, 
        content: str,
        attachments: Optional[List[str]] = None,
        is_internal: bool = False
    ) -> str:
        """Add message to ticket conversation."""
        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket {ticket_id} not found")
            
            message_id = f"msg_{uuid.uuid4().hex[:8]}"
            
            message = SupportMessage(
                id=message_id,
                ticket_id=ticket_id,
                sender_id=sender_id,
                sender_type=sender_type,
                content=content,
                timestamp=datetime.now(),
                attachments=attachments or [],
                is_internal=is_internal
            )
            
            self.messages[ticket_id].append(message)
            
            # Update ticket timestamps
            ticket = self.tickets[ticket_id]
            ticket.updated_at = datetime.now()
            
            # Set first response time if this is first agent response
            if (sender_type == "agent" and 
                ticket.first_response_at is None and 
                not is_internal):
                ticket.first_response_at = datetime.now()
            
            # Update ticket status if appropriate
            if sender_type == "agent" and ticket.status == SupportTicketStatus.OPEN:
                ticket.status = SupportTicketStatus.IN_PROGRESS
            elif sender_type == "creator" and ticket.status == SupportTicketStatus.WAITING_RESPONSE:
                ticket.status = SupportTicketStatus.IN_PROGRESS
            
            logger.info(f"Added message {message_id} to ticket {ticket_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    async def update_ticket_status(
        self, 
        ticket_id: str, 
        status: SupportTicketStatus,
        resolution_summary: Optional[str] = None
    ) -> bool:
        """Update ticket status."""
        try:
            if ticket_id not in self.tickets:
                return False
            
            ticket = self.tickets[ticket_id]
            old_status = ticket.status
            ticket.status = status
            ticket.updated_at = datetime.now()
            
            # Set resolution/closure timestamps
            if status == SupportTicketStatus.RESOLVED:
                ticket.resolved_at = datetime.now()
                if resolution_summary:
                    ticket.resolution_summary = resolution_summary
            elif status == SupportTicketStatus.CLOSED:
                ticket.closed_at = datetime.now()
                if not ticket.resolved_at:
                    ticket.resolved_at = datetime.now()
            
            # Update agent workload
            if ticket.assigned_agent_id and status in [SupportTicketStatus.RESOLVED, SupportTicketStatus.CLOSED]:
                agent = self.agents.get(ticket.assigned_agent_id)
                if agent:
                    agent.current_ticket_count = max(0, agent.current_ticket_count - 1)
                    agent.total_tickets_handled += 1
            
            logger.info(f"Updated ticket {ticket_id} status: {old_status} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            return False
    
    async def escalate_ticket(
        self, 
        ticket_id: str, 
        reason: str,
        escalate_to_role: Optional[AgentRole] = None
    ) -> bool:
        """Escalate ticket to higher level support."""
        try:
            if ticket_id not in self.tickets:
                return False
            
            ticket = self.tickets[ticket_id]
            ticket.escalation_count += 1
            ticket.status = SupportTicketStatus.ESCALATED
            ticket.updated_at = datetime.now()
            
            # Find appropriate escalation target
            if escalate_to_role:
                target_agents = [a for a in self.agents.values() if a.role == escalate_to_role and a.active]
            else:
                # Auto-determine escalation target
                if ticket.priority in [SupportTicketPriority.CRITICAL, SupportTicketPriority.URGENT]:
                    target_agents = [a for a in self.agents.values() if a.role == AgentRole.L3_EXPERT and a.active]
                else:
                    target_agents = [a for a in self.agents.values() if a.role == AgentRole.L2_TECHNICAL and a.active]
            
            # Reassign to best available agent
            if target_agents:
                # Sort by current workload
                target_agents.sort(key=lambda a: a.current_ticket_count)
                new_agent = target_agents[0]
                
                # Update agent assignments
                if ticket.assigned_agent_id:
                    old_agent = self.agents.get(ticket.assigned_agent_id)
                    if old_agent:
                        old_agent.current_ticket_count = max(0, old_agent.current_ticket_count - 1)
                
                ticket.assigned_agent_id = new_agent.id
                new_agent.current_ticket_count += 1
            
            # Add escalation message
            await self.add_message(
                ticket_id,
                "system",
                "system",
                f"Ticket escalated: {reason}",
                is_internal=True
            )
            
            logger.info(f"Escalated ticket {ticket_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating ticket: {e}")
            return False
    
    async def set_satisfaction_rating(
        self, 
        ticket_id: str, 
        rating: SatisfactionRating,
        feedback: Optional[str] = None
    ) -> bool:
        """Set customer satisfaction rating for resolved ticket."""
        try:
            if ticket_id not in self.tickets:
                return False
            
            ticket = self.tickets[ticket_id]
            ticket.satisfaction_rating = rating
            
            if feedback:
                await self.add_message(
                    ticket_id,
                    ticket.creator_id,
                    "creator",
                    f"Feedback: {feedback}",
                    is_internal=True
                )
            
            # Update agent satisfaction rating
            if ticket.assigned_agent_id:
                agent = self.agents.get(ticket.assigned_agent_id)
                if agent:
                    rating_values = {
                        SatisfactionRating.VERY_DISSATISFIED: 1,
                        SatisfactionRating.DISSATISFIED: 2,
                        SatisfactionRating.NEUTRAL: 3,
                        SatisfactionRating.SATISFIED: 4,
                        SatisfactionRating.VERY_SATISFIED: 5
                    }
                    
                    current_total = agent.satisfaction_rating * agent.total_tickets_handled
                    new_total = current_total + rating_values[rating]
                    agent.satisfaction_rating = new_total / (agent.total_tickets_handled + 1)
            
            logger.info(f"Set satisfaction rating for ticket {ticket_id}: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting satisfaction rating: {e}")
            return False
    
    async def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get ticket by ID."""
        return self.tickets.get(ticket_id)
    
    async def get_ticket_messages(self, ticket_id: str, include_internal: bool = False) -> List[SupportMessage]:
        """Get all messages for ticket."""
        messages = self.messages.get(ticket_id, [])
        
        if not include_internal:
            messages = [msg for msg in messages if not msg.is_internal]
        
        return sorted(messages, key=lambda m: m.timestamp)
    
    async def get_creator_tickets(
        self, 
        creator_id: str, 
        status_filter: Optional[SupportTicketStatus] = None
    ) -> List[SupportTicket]:
        """Get all tickets for creator."""
        ticket_ids = self.creator_tickets.get(creator_id, [])
        tickets = [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]
        
        if status_filter:
            tickets = [t for t in tickets if t.status == status_filter]
        
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)
    
    async def get_agent_tickets(
        self, 
        agent_id: str, 
        status_filter: Optional[SupportTicketStatus] = None
    ) -> List[SupportTicket]:
        """Get all tickets assigned to agent."""
        tickets = [t for t in self.tickets.values() if t.assigned_agent_id == agent_id]
        
        if status_filter:
            tickets = [t for t in tickets if t.status == status_filter]
        
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)
    
    async def search_tickets(
        self, 
        query: str, 
        category: Optional[SupportCategory] = None,
        status: Optional[SupportTicketStatus] = None,
        priority: Optional[SupportTicketPriority] = None
    ) -> List[SupportTicket]:
        """Search tickets by various criteria."""
        query_lower = query.lower()
        matching_tickets = []
        
        for ticket in self.tickets.values():
            # Text search in subject and description
            if (query_lower in ticket.subject.lower() or 
                query_lower in ticket.description.lower()):
                
                # Apply filters
                if category and ticket.category != category:
                    continue
                if status and ticket.status != status:
                    continue
                if priority and ticket.priority != priority:
                    continue
                
                matching_tickets.append(ticket)
        
        return sorted(matching_tickets, key=lambda t: t.created_at, reverse=True)
    
    async def check_escalation_rules(self):
        """Check and apply escalation rules to tickets."""
        current_time = datetime.now()
        escalated_count = 0
        
        for ticket in self.tickets.values():
            if ticket.status in [SupportTicketStatus.RESOLVED, SupportTicketStatus.CLOSED]:
                continue
            
            for rule in self.escalation_rules:
                should_escalate = False
                escalation_reason = ""
                
                if rule["condition"] == "response_time_exceeded":
                    if (ticket.priority == rule["priority"] and 
                        ticket.first_response_at is None):
                        hours_since_creation = (current_time - ticket.created_at).total_seconds() / 3600
                        if hours_since_creation > rule["threshold_hours"]:
                            should_escalate = True
                            escalation_reason = f"No response within {rule['threshold_hours']} hours"
                
                elif rule["condition"] == "resolution_time_exceeded":
                    if (ticket.priority == rule["priority"] and 
                        ticket.resolved_at is None):
                        hours_since_creation = (current_time - ticket.created_at).total_seconds() / 3600
                        if hours_since_creation > rule["threshold_hours"]:
                            should_escalate = True
                            escalation_reason = f"Not resolved within {rule['threshold_hours']} hours"
                
                elif rule["condition"] == "multiple_escalations":
                    if ticket.escalation_count >= rule["escalation_count"]:
                        should_escalate = True
                        escalation_reason = f"Multiple escalations ({ticket.escalation_count})"
                
                elif rule["condition"] == "security_category":
                    if (ticket.category == rule["category"] and 
                        ticket.status == SupportTicketStatus.OPEN):
                        should_escalate = True
                        escalation_reason = "Security issue requires immediate attention"
                
                if should_escalate:
                    await self.escalate_ticket(ticket.id, escalation_reason)
                    escalated_count += 1
                    break  # Only apply one rule per ticket per check
        
        return escalated_count
    
    async def get_support_analytics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> SupportAnalytics:
        """Get comprehensive support analytics."""
        try:
            # Filter tickets by date range
            period_tickets = [
                t for t in self.tickets.values()
                if start_date <= t.created_at <= end_date
            ]
            
            total_tickets = len(period_tickets)
            
            if total_tickets == 0:
                return SupportAnalytics(
                    period_start=start_date,
                    period_end=end_date,
                    total_tickets=0,
                    tickets_by_status={},
                    tickets_by_category={},
                    tickets_by_priority={},
                    average_response_time=0.0,
                    average_resolution_time=0.0,
                    customer_satisfaction_score=0.0,
                    first_response_rate=0.0,
                    resolution_rate=0.0,
                    escalation_rate=0.0,
                    agent_performance={}
                )
            
            # Calculate distributions
            status_dist = defaultdict(int)
            category_dist = defaultdict(int)
            priority_dist = defaultdict(int)
            
            for ticket in period_tickets:
                status_dist[ticket.status] += 1
                category_dist[ticket.category] += 1
                priority_dist[ticket.priority] += 1
            
            # Calculate response and resolution times
            response_times = []
            resolution_times = []
            satisfaction_ratings = []
            
            first_response_count = 0
            resolved_count = 0
            escalated_count = 0
            
            for ticket in period_tickets:
                # Response time
                if ticket.first_response_at:
                    response_time = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                    response_times.append(response_time)
                    first_response_count += 1
                
                # Resolution time
                if ticket.resolved_at:
                    resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                    resolution_times.append(resolution_time)
                    resolved_count += 1
                
                # Satisfaction rating
                if ticket.satisfaction_rating:
                    rating_values = {
                        SatisfactionRating.VERY_DISSATISFIED: 1,
                        SatisfactionRating.DISSATISFIED: 2,
                        SatisfactionRating.NEUTRAL: 3,
                        SatisfactionRating.SATISFIED: 4,
                        SatisfactionRating.VERY_SATISFIED: 5
                    }
                    satisfaction_ratings.append(rating_values[ticket.satisfaction_rating])
                
                # Escalations
                if ticket.escalation_count > 0:
                    escalated_count += 1
            
            # Calculate averages
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0
            avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else 0.0
            
            # Calculate rates
            first_response_rate = (first_response_count / total_tickets) * 100
            resolution_rate = (resolved_count / total_tickets) * 100
            escalation_rate = (escalated_count / total_tickets) * 100
            
            # Agent performance
            agent_performance = {}
            for agent_id, agent in self.agents.items():
                agent_tickets = [t for t in period_tickets if t.assigned_agent_id == agent_id]
                
                if agent_tickets:
                    agent_response_times = []
                    agent_satisfaction = []
                    
                    for ticket in agent_tickets:
                        if ticket.first_response_at:
                            response_time = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                            agent_response_times.append(response_time)
                        
                        if ticket.satisfaction_rating:
                            rating_values = {
                                SatisfactionRating.VERY_DISSATISFIED: 1,
                                SatisfactionRating.DISSATISFIED: 2,
                                SatisfactionRating.NEUTRAL: 3,
                                SatisfactionRating.SATISFIED: 4,
                                SatisfactionRating.VERY_SATISFIED: 5
                            }
                            agent_satisfaction.append(rating_values[ticket.satisfaction_rating])
                    
                    agent_performance[agent_id] = {
                        "tickets_handled": len(agent_tickets),
                        "average_response_time": sum(agent_response_times) / len(agent_response_times) if agent_response_times else 0.0,
                        "satisfaction_score": sum(agent_satisfaction) / len(agent_satisfaction) if agent_satisfaction else 0.0,
                        "resolution_rate": len([t for t in agent_tickets if t.resolved_at]) / len(agent_tickets) * 100
                    }
            
            return SupportAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_tickets=total_tickets,
                tickets_by_status=dict(status_dist),
                tickets_by_category=dict(category_dist),
                tickets_by_priority=dict(priority_dist),
                average_response_time=avg_response_time,
                average_resolution_time=avg_resolution_time,
                customer_satisfaction_score=avg_satisfaction,
                first_response_rate=first_response_rate,
                resolution_rate=resolution_rate,
                escalation_rate=escalation_rate,
                agent_performance=agent_performance
            )
            
        except Exception as e:
            logger.error(f"Error getting support analytics: {e}")
            return SupportAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_tickets=0,
                tickets_by_status={},
                tickets_by_category={},
                tickets_by_priority={},
                average_response_time=0.0,
                average_resolution_time=0.0,
                customer_satisfaction_score=0.0,
                first_response_rate=0.0,
                resolution_rate=0.0,
                escalation_rate=0.0,
                agent_performance={}
            )
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_tickets = len(self.tickets)
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.active])
        
        if total_tickets == 0:
            return {
                "total_tickets": 0,
                "total_agents": total_agents,
                "active_agents": active_agents,
                "knowledge_base_articles": len(self.knowledge_base),
                "open_tickets": 0,
                "average_satisfaction": 0.0
            }
        
        # Calculate distributions
        status_distribution = defaultdict(int)
        priority_distribution = defaultdict(int)
        category_distribution = defaultdict(int)
        
        satisfaction_ratings = []
        
        for ticket in self.tickets.values():
            status_distribution[ticket.status.value] += 1
            priority_distribution[ticket.priority.value] += 1
            category_distribution[ticket.category.value] += 1
            
            if ticket.satisfaction_rating:
                rating_values = {
                    SatisfactionRating.VERY_DISSATISFIED: 1,
                    SatisfactionRating.DISSATISFIED: 2,
                    SatisfactionRating.NEUTRAL: 3,
                    SatisfactionRating.SATISFIED: 4,
                    SatisfactionRating.VERY_SATISFIED: 5
                }
                satisfaction_ratings.append(rating_values[ticket.satisfaction_rating])
        
        average_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else 0.0
        
        return {
            "total_tickets": total_tickets,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "knowledge_base_articles": len(self.knowledge_base),
            "auto_response_categories": len(self.auto_responses),
            "status_distribution": dict(status_distribution),
            "priority_distribution": dict(priority_distribution),
            "category_distribution": dict(category_distribution),
            "average_satisfaction_rating": average_satisfaction,
            "total_messages": sum(len(messages) for messages in self.messages.values())
        }


# Global service instance
_support_service_instance = None

def get_creator_support_service() -> CreatorSupportService:
    """Get singleton instance of CreatorSupportService."""
    global _support_service_instance
    if _support_service_instance is None:
        _support_service_instance = CreatorSupportService()
    return _support_service_instance


# Example usage and testing
async def example_usage():
    """Example usage of Creator Support Service."""
    service = get_creator_support_service()
    
    # Create support ticket
    request = SupportTicketRequest(
        creator_id="creator_123",
        subject="Unable to upload video content",
        description="I'm getting an error when trying to upload my latest video. The upload fails at 50% consistently.",
        category=SupportCategory.CONTENT_UPLOAD,
        priority=SupportTicketPriority.HIGH,
        preferred_channel=SupportChannel.EMAIL
    )
    
    ticket_id = await service.create_ticket(request)
    print(f"Created ticket: {ticket_id}")
    
    # Agent responds
    await service.add_message(
        ticket_id,
        "agent_002",
        "agent",
        "Hi! I see you're having trouble with video uploads. Can you tell me the file size and format you're trying to upload?"
    )
    
    # Creator responds
    await service.add_message(
        ticket_id,
        "creator_123",
        "creator",
        "It's a 2GB MP4 file. I've tried multiple times with the same result."
    )
    
    # Agent provides solution
    await service.add_message(
        ticket_id,
        "agent_002",
        "agent",
        "The issue is likely due to the file size. Please try compressing the video to under 1GB or use our chunked upload feature."
    )
    
    # Resolve ticket
    await service.update_ticket_status(
        ticket_id,
        SupportTicketStatus.RESOLVED,
        "Provided solution for large file upload issue"
    )
    
    # Customer satisfaction
    await service.set_satisfaction_rating(
        ticket_id,
        SatisfactionRating.SATISFIED,
        "The solution worked perfectly, thank you!"
    )
    
    # Get ticket details
    ticket = await service.get_ticket(ticket_id)
    print(f"Ticket status: {ticket.status}")
    print(f"Satisfaction: {ticket.satisfaction_rating}")
    
    # Get messages
    messages = await service.get_ticket_messages(ticket_id)
    print(f"Total messages: {len(messages)}")
    
    # Get analytics
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    analytics = await service.get_support_analytics(start_date, end_date)
    print(f"Analytics: {analytics.total_tickets} tickets, "
          f"{analytics.average_response_time:.1f}h avg response time")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())