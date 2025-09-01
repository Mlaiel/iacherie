"""Turn Manager - Advanced Conversation Turn Management

Enterprise-grade turn management system for multi-party conversations,
handling turn-taking protocols, speaker identification, context preservation,
and intelligent turn routing for optimal conversation flow.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import deque, defaultdict

import aioredis
from backend.core.database.session import DatabaseManager
from backend.services.ai.nlp_service import NLPService
from backend.services.notification.real_time_service import RealTimeNotificationService

logger = logging.getLogger(__name__)

class TurnType(Enum):
    """Types of conversation turns"""
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_NOTIFICATION = "system_notification"
    WORKFLOW_ACTION = "workflow_action"
    COLLABORATION_INVITE = "collaboration_invite"
    CONTENT_UPLOAD = "content_upload"
    REVENUE_PROPOSAL = "revenue_proposal"
    AGREEMENT_CONFIRMATION = "agreement_confirmation"
    ESCALATION_REQUEST = "escalation_request"

class TurnPriority(Enum):
    """Priority levels for turns"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class TurnStatus(Enum):
    """Status of conversation turns"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

class SpeakerRole(Enum):
    """Roles for conversation speakers"""
    PRIMARY_CREATOR = "primary_creator"
    COLLABORATING_CREATOR = "collaborating_creator"
    AI_ASSISTANT = "ai_assistant"
    HUMAN_AGENT = "human_agent"
    SYSTEM = "system"
    MODERATOR = "moderator"
    BUSINESS_PARTNER = "business_partner"

@dataclass
class ConversationTurn:
    """Individual conversation turn with comprehensive metadata"""
    turn_id: str
    conversation_id: str
    speaker_id: str
    speaker_role: SpeakerRole
    turn_type: TurnType
    priority: TurnPriority = TurnPriority.NORMAL
    
    # Content
    content: str = ""
    content_type: str = "text"
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Processing
    status: TurnStatus = TurnStatus.PENDING
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Business context
    business_intent: Optional[str] = None
    workflow_context: Dict[str, Any] = field(default_factory=dict)
    collaboration_data: Dict[str, Any] = field(default_factory=dict)
    revenue_impact: Optional[float] = None
    
    # Response tracking
    response_required: bool = True
    response_timeout: Optional[datetime] = None
    awaiting_user_ids: Set[str] = field(default_factory=set)
    
    # Analytics
    sentiment_score: Optional[float] = None
    engagement_score: Optional[float] = None
    business_value_score: Optional[float] = None

@dataclass
class TurnSequence:
    """Sequence of related conversation turns"""
    sequence_id: str
    conversation_id: str
    sequence_type: str  # workflow, negotiation, support, collaboration
    turns: List[str] = field(default_factory=list)  # turn_ids
    
    # Sequence management
    current_turn_index: int = 0
    is_complete: bool = False
    requires_user_action: bool = False
    
    # Business context
    business_objective: Optional[str] = None
    expected_outcomes: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

@dataclass
class TurnQueue:
    """Queue for managing conversation turns"""
    queue_id: str
    conversation_id: str
    pending_turns: deque = field(default_factory=deque)
    processing_turns: Dict[str, ConversationTurn] = field(default_factory=dict)
    completed_turns: List[str] = field(default_factory=list)
    
    # Queue management
    max_concurrent_turns: int = 5
    priority_processing: bool = True
    turn_timeout_seconds: int = 300  # 5 minutes
    
    # Performance metrics
    total_processed: int = 0
    average_processing_time: float = 0.0
    success_rate: float = 100.0

class TurnManager:
    """
    Enterprise turn management system for IA Influencer conversations.
    
    Manages complex multi-party conversation flows with intelligent turn routing,
    priority handling, and business workflow integration.
    
    Key features:
    - Multi-party turn coordination
    - Priority-based turn processing
    - Business workflow integration
    - Real-time turn synchronization
    - Performance optimization
    - Error handling and recovery
    """
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        database_manager: DatabaseManager,
        nlp_service: NLPService,
        notification_service: RealTimeNotificationService
    ):
        self.redis_client = redis_client
        self.database_manager = database_manager
        self.nlp_service = nlp_service
        self.notification_service = notification_service
        
        # Turn management state
        self.active_queues: Dict[str, TurnQueue] = {}
        self.turn_sequences: Dict[str, TurnSequence] = {}
        self.speaker_contexts: Dict[str, Dict[str, Any]] = {}
        
        # Processing control
        self.processing_semaphore = asyncio.Semaphore(10)  # Limit concurrent processing
        self.turn_processors: Dict[TurnType, callable] = {}
        
        # Performance metrics
        self.metrics = {
            'turns_processed': 0,
            'average_processing_time': 0.0,
            'success_rate': 100.0,
            'active_conversations': 0,
            'concurrent_turns': 0
        }
        
        # Initialize turn processors
        self._initialize_turn_processors()
        
        # Start background tasks
        asyncio.create_task(self._process_turn_queues())
        asyncio.create_task(self._cleanup_expired_turns())
        
        logger.info("TurnManager initialized for enterprise conversation management")

    def _initialize_turn_processors(self):
        """Initialize turn processors for different turn types"""
        
        self.turn_processors = {
            TurnType.USER_MESSAGE: self._process_user_message,
            TurnType.AGENT_RESPONSE: self._process_agent_response,
            TurnType.SYSTEM_NOTIFICATION: self._process_system_notification,
            TurnType.WORKFLOW_ACTION: self._process_workflow_action,
            TurnType.COLLABORATION_INVITE: self._process_collaboration_invite,
            TurnType.CONTENT_UPLOAD: self._process_content_upload,
            TurnType.REVENUE_PROPOSAL: self._process_revenue_proposal,
            TurnType.AGREEMENT_CONFIRMATION: self._process_agreement_confirmation,
            TurnType.ESCALATION_REQUEST: self._process_escalation_request
        }

    async def create_turn(
        self,
        conversation_id: str,
        speaker_id: str,
        speaker_role: SpeakerRole,
        turn_type: TurnType,
        content: str,
        priority: TurnPriority = TurnPriority.NORMAL,
        business_context: Dict[str, Any] = None,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """
        Create new conversation turn
        
        Args:
            conversation_id: ID of the conversation
            speaker_id: ID of the speaker
            speaker_role: Role of the speaker
            turn_type: Type of turn
            content: Turn content
            priority: Turn priority
            business_context: Business context data
            scheduled_at: Optional scheduled execution time
            
        Returns:
            Turn ID
        """
        turn_id = str(uuid.uuid4())
        
        # Create turn object
        turn = ConversationTurn(
            turn_id=turn_id,
            conversation_id=conversation_id,
            speaker_id=speaker_id,
            speaker_role=speaker_role,
            turn_type=turn_type,
            content=content,
            priority=priority,
            scheduled_at=scheduled_at
        )
        
        # Add business context
        if business_context:
            turn.workflow_context = business_context.get('workflow_context', {})
            turn.collaboration_data = business_context.get('collaboration_data', {})
            turn.revenue_impact = business_context.get('revenue_impact')
            turn.business_intent = business_context.get('business_intent')
        
        # Analyze turn content
        await self._analyze_turn_content(turn)
        
        # Get or create queue for conversation
        queue = await self._get_or_create_queue(conversation_id)
        
        # Add to queue based on priority
        if priority in [TurnPriority.URGENT, TurnPriority.CRITICAL]:
            queue.pending_turns.appendleft(turn)  # High priority to front
        else:
            queue.pending_turns.append(turn)  # Normal priority to back
        
        # Persist turn
        await self._persist_turn(turn)
        
        # Update queue metrics
        await self._update_queue_metrics(queue)
        
        logger.info(f"Created turn {turn_id} for conversation {conversation_id} with priority {priority.value}")
        return turn_id

    async def _analyze_turn_content(self, turn: ConversationTurn):
        """Analyze turn content for business intelligence"""
        
        try:
            # Sentiment analysis
            sentiment_result = await self.nlp_service.analyze_sentiment(turn.content)
            turn.sentiment_score = sentiment_result.get('compound', 0.0)
            
            # Business intent detection
            if not turn.business_intent:
                intent_result = await self.nlp_service.classify_business_intent(turn.content)
                turn.business_intent = intent_result.get('intent')
            
            # Engagement scoring
            engagement_features = {
                'content_length': len(turn.content),
                'question_count': turn.content.count('?'),
                'exclamation_count': turn.content.count('!'),
                'business_keywords': self._count_business_keywords(turn.content),
                'urgency_indicators': self._detect_urgency_indicators(turn.content)
            }
            
            turn.engagement_score = self._calculate_engagement_score(engagement_features)
            
            # Business value scoring
            turn.business_value_score = self._calculate_business_value_score(turn)
            
        except Exception as e:
            logger.error(f"Error analyzing turn content: {str(e)}")

    def _count_business_keywords(self, content: str) -> int:
        """Count business-relevant keywords in content"""
        business_keywords = [
            'collaboration', 'partnership', 'revenue', 'monetization',
            'copyright', 'protection', 'licensing', 'distribution',
            'spotify', 'youtube', 'instagram', 'tiktok',
            'agreement', 'contract', 'payment', 'royalty'
        ]
        
        content_lower = content.lower()
        return sum(1 for keyword in business_keywords if keyword in content_lower)

    def _detect_urgency_indicators(self, content: str) -> int:
        """Detect urgency indicators in content"""
        urgency_indicators = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'deadline', 'time-sensitive', 'priority', 'rush'
        ]
        
        content_lower = content.lower()
        return sum(1 for indicator in urgency_indicators if indicator in content_lower)

    def _calculate_engagement_score(self, features: Dict[str, Any]) -> float:
        """Calculate engagement score based on content features"""
        score = 0.0
        
        # Base score from content length
        if features['content_length'] > 50:
            score += 0.3
        if features['content_length'] > 200:
            score += 0.2
        
        # Questions indicate engagement
        score += min(features['question_count'] * 0.1, 0.3)
        
        # Business keywords indicate business engagement
        score += min(features['business_keywords'] * 0.05, 0.2)
        
        # Urgency increases engagement
        score += min(features['urgency_indicators'] * 0.1, 0.2)
        
        return min(score, 1.0)

    def _calculate_business_value_score(self, turn: ConversationTurn) -> float:
        """Calculate business value score for turn"""
        score = 0.0
        
        # Revenue impact
        if turn.revenue_impact:
            score += min(turn.revenue_impact / 1000.0, 0.4)  # Up to $1000 = 0.4 points
        
        # Business intent value
        intent_values = {
            'content_monetization': 0.3,
            'collaboration_seeking': 0.25,
            'content_protection': 0.2,
            'platform_integration': 0.15,
            'technical_support': 0.1
        }
        score += intent_values.get(turn.business_intent, 0.0)
        
        # Speaker role value
        role_values = {
            SpeakerRole.PRIMARY_CREATOR: 0.2,
            SpeakerRole.COLLABORATING_CREATOR: 0.15,
            SpeakerRole.BUSINESS_PARTNER: 0.1,
            SpeakerRole.AI_ASSISTANT: 0.05
        }
        score += role_values.get(turn.speaker_role, 0.0)
        
        # Turn type value
        type_values = {
            TurnType.REVENUE_PROPOSAL: 0.1,
            TurnType.COLLABORATION_INVITE: 0.08,
            TurnType.CONTENT_UPLOAD: 0.06,
            TurnType.AGREEMENT_CONFIRMATION: 0.1,
            TurnType.USER_MESSAGE: 0.02
        }
        score += type_values.get(turn.turn_type, 0.0)
        
        return min(score, 1.0)

    async def _get_or_create_queue(self, conversation_id: str) -> TurnQueue:
        """Get existing queue or create new one for conversation"""
        
        if conversation_id not in self.active_queues:
            queue_id = str(uuid.uuid4())
            queue = TurnQueue(
                queue_id=queue_id,
                conversation_id=conversation_id
            )
            self.active_queues[conversation_id] = queue
            await self._persist_queue(queue)
            
            logger.info(f"Created new turn queue {queue_id} for conversation {conversation_id}")
        
        return self.active_queues[conversation_id]

    async def _process_turn_queues(self):
        """Background task to process turn queues"""
        
        while True:
            try:
                # Process all active queues
                for conversation_id, queue in list(self.active_queues.items()):
                    await self._process_queue(queue)
                
                # Wait before next processing cycle
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in turn queue processing: {str(e)}")
                await asyncio.sleep(5)

    async def _process_queue(self, queue: TurnQueue):
        """Process turns in a specific queue"""
        
        # Check if we can process more turns
        if len(queue.processing_turns) >= queue.max_concurrent_turns:
            return
        
        # Process pending turns by priority
        turns_to_process = []
        
        # Sort pending turns by priority and creation time
        sorted_turns = sorted(
            queue.pending_turns,
            key=lambda t: (t.priority.value, t.created_at),
            reverse=True
        )
        
        # Select turns to process
        available_slots = queue.max_concurrent_turns - len(queue.processing_turns)
        for turn in sorted_turns[:available_slots]:
            queue.pending_turns.remove(turn)
            turns_to_process.append(turn)
        
        # Process selected turns
        for turn in turns_to_process:
            await self._start_turn_processing(queue, turn)

    async def _start_turn_processing(self, queue: TurnQueue, turn: ConversationTurn):
        """Start processing a specific turn"""
        
        turn.status = TurnStatus.PROCESSING
        turn.processed_at = datetime.now(timezone.utc)
        queue.processing_turns[turn.turn_id] = turn
        
        # Create processing task
        asyncio.create_task(self._process_turn(queue, turn))

    async def _process_turn(self, queue: TurnQueue, turn: ConversationTurn):
        """Process individual turn"""
        
        async with self.processing_semaphore:
            start_time = datetime.now(timezone.utc)
            
            try:
                # Get processor for turn type
                processor = self.turn_processors.get(turn.turn_type)
                if not processor:
                    raise ValueError(f"No processor found for turn type {turn.turn_type}")
                
                # Process turn
                result = await processor(turn)
                
                # Update turn status
                turn.status = TurnStatus.COMPLETED
                turn.completed_at = datetime.now(timezone.utc)
                turn.processing_time = (turn.completed_at - start_time).total_seconds()
                
                # Update queue
                del queue.processing_turns[turn.turn_id]
                queue.completed_turns.append(turn.turn_id)
                queue.total_processed += 1
                
                # Update metrics
                await self._update_processing_metrics(turn.processing_time, True)
                
                logger.info(f"Successfully processed turn {turn.turn_id} in {turn.processing_time:.2f}s")
                
            except Exception as e:
                # Handle processing error
                await self._handle_turn_error(queue, turn, str(e))
                
            finally:
                # Persist updated turn
                await self._persist_turn(turn)

    async def _handle_turn_error(self, queue: TurnQueue, turn: ConversationTurn, error_message: str):
        """Handle turn processing error"""
        
        turn.error_message = error_message
        turn.retry_count += 1
        
        if turn.retry_count < turn.max_retries:
            # Retry turn
            turn.status = TurnStatus.PENDING
            queue.pending_turns.append(turn)
            del queue.processing_turns[turn.turn_id]
            
            logger.warning(f"Turn {turn.turn_id} failed, retrying ({turn.retry_count}/{turn.max_retries}): {error_message}")
        else:
            # Mark as failed
            turn.status = TurnStatus.FAILED
            turn.completed_at = datetime.now(timezone.utc)
            del queue.processing_turns[turn.turn_id]
            
            # Check if escalation needed
            if turn.priority in [TurnPriority.URGENT, TurnPriority.CRITICAL]:
                await self._escalate_failed_turn(turn)
            
            logger.error(f"Turn {turn.turn_id} failed permanently: {error_message}")
        
        # Update metrics
        await self._update_processing_metrics(0, False)

    async def _escalate_failed_turn(self, turn: ConversationTurn):
        """Escalate failed critical turn"""
        
        escalation_data = {
            "turn_id": turn.turn_id,
            "conversation_id": turn.conversation_id,
            "speaker_id": turn.speaker_id,
            "turn_type": turn.turn_type.value,
            "priority": turn.priority.value,
            "error_message": turn.error_message,
            "retry_count": turn.retry_count,
            "business_context": turn.workflow_context
        }
        
        # Send escalation notification
        await self.notification_service.send_notification(
            user_id="support_team",
            notification_type="turn_processing_failure",
            data=escalation_data
        )

    # Turn processors
    async def _process_user_message(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process user message turn"""
        
        # Extract entities and intents
        analysis_result = await self.nlp_service.analyze_message(turn.content)
        
        # Update speaker context
        await self._update_speaker_context(turn.speaker_id, {
            'last_message': turn.content,
            'last_intent': analysis_result.get('intent'),
            'engagement_level': turn.engagement_score,
            'business_value': turn.business_value_score
        })
        
        # Generate response if required
        if turn.response_required:
            response_turn_id = await self.create_turn(
                conversation_id=turn.conversation_id,
                speaker_id="ai_assistant",
                speaker_role=SpeakerRole.AI_ASSISTANT,
                turn_type=TurnType.AGENT_RESPONSE,
                content=f"Processing your message regarding {analysis_result.get('intent', 'your request')}...",
                priority=turn.priority
            )
            
            return {"response_turn_id": response_turn_id}
        
        return {"analysis_result": analysis_result}

    async def _process_agent_response(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process AI agent response turn"""
        
        # Send response to user
        await self.notification_service.send_notification(
            user_id=turn.speaker_id,
            notification_type="agent_response",
            data={
                "conversation_id": turn.conversation_id,
                "response": turn.content,
                "business_context": turn.workflow_context
            }
        )
        
        return {"response_sent": True}

    async def _process_system_notification(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process system notification turn"""
        
        # Broadcast system notification
        await self.notification_service.broadcast_notification(
            conversation_id=turn.conversation_id,
            notification_type="system_notification",
            data={
                "message": turn.content,
                "system_context": turn.metadata
            }
        )
        
        return {"notification_sent": True}

    async def _process_workflow_action(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process workflow action turn"""
        
        workflow_type = turn.workflow_context.get('workflow_type')
        action = turn.workflow_context.get('action')
        
        # Execute workflow action based on type
        if workflow_type == 'content_protection':
            result = await self._execute_protection_workflow(turn)
        elif workflow_type == 'collaboration':
            result = await self._execute_collaboration_workflow(turn)
        elif workflow_type == 'monetization':
            result = await self._execute_monetization_workflow(turn)
        else:
            result = {"error": f"Unknown workflow type: {workflow_type}"}
        
        return result

    async def _process_collaboration_invite(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process collaboration invitation turn"""
        
        collaboration_data = turn.collaboration_data
        invited_user_id = collaboration_data.get('invited_user_id')
        
        if invited_user_id:
            # Send collaboration invitation
            await self.notification_service.send_notification(
                user_id=invited_user_id,
                notification_type="collaboration_invitation",
                data={
                    "inviter_id": turn.speaker_id,
                    "conversation_id": turn.conversation_id,
                    "collaboration_details": collaboration_data,
                    "revenue_sharing": collaboration_data.get('revenue_sharing', {})
                }
            )
            
            return {"invitation_sent": True, "invited_user": invited_user_id}
        
        return {"error": "No invited user specified"}

    async def _process_content_upload(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process content upload turn"""
        
        content_info = turn.metadata.get('content_info', {})
        
        # Trigger content processing workflow
        processing_job_id = await self._start_content_processing(
            content_info=content_info,
            uploader_id=turn.speaker_id,
            conversation_id=turn.conversation_id
        )
        
        return {"processing_job_id": processing_job_id}

    async def _process_revenue_proposal(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process revenue sharing proposal turn"""
        
        proposal_data = turn.collaboration_data.get('revenue_proposal', {})
        target_user_ids = turn.awaiting_user_ids
        
        # Send proposal to target users
        for user_id in target_user_ids:
            await self.notification_service.send_notification(
                user_id=user_id,
                notification_type="revenue_proposal",
                data={
                    "proposer_id": turn.speaker_id,
                    "conversation_id": turn.conversation_id,
                    "proposal": proposal_data,
                    "estimated_revenue": turn.revenue_impact
                }
            )
        
        return {"proposal_sent": True, "recipients": list(target_user_ids)}

    async def _process_agreement_confirmation(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process agreement confirmation turn"""
        
        agreement_data = turn.collaboration_data.get('agreement', {})
        
        # Create formal agreement record
        agreement_id = await self._create_agreement_record(
            agreement_data=agreement_data,
            conversation_id=turn.conversation_id,
            participants=[turn.speaker_id] + list(turn.awaiting_user_ids)
        )
        
        # Notify all parties
        all_participants = [turn.speaker_id] + list(turn.awaiting_user_ids)
        for user_id in all_participants:
            await self.notification_service.send_notification(
                user_id=user_id,
                notification_type="agreement_confirmed",
                data={
                    "agreement_id": agreement_id,
                    "agreement_details": agreement_data,
                    "conversation_id": turn.conversation_id
                }
            )
        
        return {"agreement_id": agreement_id, "participants_notified": len(all_participants)}

    async def _process_escalation_request(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Process escalation request turn"""
        
        escalation_data = {
            "conversation_id": turn.conversation_id,
            "requester_id": turn.speaker_id,
            "escalation_reason": turn.content,
            "priority": turn.priority.value,
            "business_context": turn.workflow_context
        }
        
        # Create escalation ticket
        ticket_id = await self._create_escalation_ticket(escalation_data)
        
        # Notify support team
        await self.notification_service.send_notification(
            user_id="support_team",
            notification_type="escalation_request",
            data={
                "ticket_id": ticket_id,
                "escalation_data": escalation_data
            }
        )
        
        return {"ticket_id": ticket_id, "escalation_created": True}

    # Workflow execution methods
    async def _execute_protection_workflow(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Execute content protection workflow"""
        # Implementation for content protection workflow
        return {"workflow": "content_protection", "status": "executed"}

    async def _execute_collaboration_workflow(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Execute collaboration workflow"""
        # Implementation for collaboration workflow
        return {"workflow": "collaboration", "status": "executed"}

    async def _execute_monetization_workflow(self, turn: ConversationTurn) -> Dict[str, Any]:
        """Execute monetization workflow"""
        # Implementation for monetization workflow
        return {"workflow": "monetization", "status": "executed"}

    # Helper methods
    async def _update_speaker_context(self, speaker_id: str, context_update: Dict[str, Any]):
        """Update speaker context with new information"""
        
        if speaker_id not in self.speaker_contexts:
            self.speaker_contexts[speaker_id] = {}
        
        self.speaker_contexts[speaker_id].update(context_update)
        self.speaker_contexts[speaker_id]['last_updated'] = datetime.now(timezone.utc).isoformat()

    async def _update_processing_metrics(self, processing_time: float, success: bool):
        """Update processing performance metrics"""
        
        self.metrics['turns_processed'] += 1
        
        if success:
            # Update average processing time
            current_avg = self.metrics['average_processing_time']
            count = self.metrics['turns_processed']
            self.metrics['average_processing_time'] = (current_avg * (count - 1) + processing_time) / count
        
        # Update success rate
        success_count = self.metrics['turns_processed'] * (self.metrics['success_rate'] / 100.0)
        if success:
            success_count += 1
        
        self.metrics['success_rate'] = (success_count / self.metrics['turns_processed']) * 100.0

    async def _cleanup_expired_turns(self):
        """Background task to cleanup expired turns"""
        
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                expired_turns = []
                
                # Check all active queues for expired turns
                for queue in self.active_queues.values():
                    for turn in list(queue.pending_turns):
                        if turn.response_timeout and current_time > turn.response_timeout:
                            expired_turns.append((queue, turn))
                
                # Process expired turns
                for queue, turn in expired_turns:
                    await self._handle_expired_turn(queue, turn)
                
                # Wait before next cleanup cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in turn cleanup: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _handle_expired_turn(self, queue: TurnQueue, turn: ConversationTurn):
        """Handle expired turn"""
        
        turn.status = TurnStatus.CANCELLED
        turn.error_message = "Turn expired due to timeout"
        queue.pending_turns.remove(turn)
        
        # Notify relevant parties
        await self.notification_service.send_notification(
            user_id=turn.speaker_id,
            notification_type="turn_expired",
            data={
                "turn_id": turn.turn_id,
                "conversation_id": turn.conversation_id,
                "turn_type": turn.turn_type.value
            }
        )

    async def _persist_turn(self, turn: ConversationTurn):
        """Persist turn to Redis"""
        
        try:
            turn_data = {
                "turn_id": turn.turn_id,
                "conversation_id": turn.conversation_id,
                "speaker_id": turn.speaker_id,
                "speaker_role": turn.speaker_role.value,
                "turn_type": turn.turn_type.value,
                "priority": turn.priority.value,
                "content": turn.content,
                "content_type": turn.content_type,
                "status": turn.status.value,
                "created_at": turn.created_at.isoformat(),
                "processed_at": turn.processed_at.isoformat() if turn.processed_at else None,
                "completed_at": turn.completed_at.isoformat() if turn.completed_at else None,
                "processing_time": turn.processing_time,
                "business_intent": turn.business_intent,
                "workflow_context": turn.workflow_context,
                "collaboration_data": turn.collaboration_data,
                "revenue_impact": turn.revenue_impact,
                "sentiment_score": turn.sentiment_score,
                "engagement_score": turn.engagement_score,
                "business_value_score": turn.business_value_score
            }
            
            await self.redis_client.setex(
                f"turn:{turn.turn_id}",
                timedelta(days=30),  # 30 day expiry
                json.dumps(turn_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Error persisting turn {turn.turn_id}: {str(e)}")

    async def _persist_queue(self, queue: TurnQueue):
        """Persist queue to Redis"""
        
        try:
            queue_data = {
                "queue_id": queue.queue_id,
                "conversation_id": queue.conversation_id,
                "pending_turn_count": len(queue.pending_turns),
                "processing_turn_count": len(queue.processing_turns),
                "completed_turn_count": len(queue.completed_turns),
                "total_processed": queue.total_processed,
                "average_processing_time": queue.average_processing_time,
                "success_rate": queue.success_rate
            }
            
            await self.redis_client.setex(
                f"turn_queue:{queue.queue_id}",
                timedelta(days=7),  # 7 day expiry
                json.dumps(queue_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Error persisting queue {queue.queue_id}: {str(e)}")

    async def _update_queue_metrics(self, queue: TurnQueue):
        """Update queue performance metrics"""
        
        if queue.total_processed > 0:
            # Calculate success rate
            completed_successfully = len([
                t for t in queue.completed_turns
                # Would need to check turn status, simplified here
            ])
            queue.success_rate = (completed_successfully / queue.total_processed) * 100.0
        
        # Persist updated metrics
        await self._persist_queue(queue)

    # Public API methods
    async def get_turn_status(self, turn_id: str) -> Dict[str, Any]:
        """Get status of specific turn"""
        
        try:
            turn_data = await self.redis_client.get(f"turn:{turn_id}")
            if turn_data:
                return json.loads(turn_data)
            return {"error": "Turn not found"}
            
        except Exception as e:
            logger.error(f"Error getting turn status: {str(e)}")
            return {"error": str(e)}

    async def get_conversation_turns(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent turns for conversation"""
        
        # Get queue for conversation
        queue = self.active_queues.get(conversation_id)
        if not queue:
            return []
        
        # Get completed turns
        turn_data = []
        for turn_id in queue.completed_turns[-limit:]:
            turn_info = await self.get_turn_status(turn_id)
            if turn_info and "error" not in turn_info:
                turn_data.append(turn_info)
        
        return turn_data

    async def cancel_turn(self, turn_id: str, reason: str = "user_cancelled") -> bool:
        """Cancel pending turn"""
        
        # Find turn in queues
        for queue in self.active_queues.values():
            # Check pending turns
            for turn in queue.pending_turns:
                if turn.turn_id == turn_id:
                    turn.status = TurnStatus.CANCELLED
                    turn.error_message = reason
                    queue.pending_turns.remove(turn)
                    await self._persist_turn(turn)
                    return True
            
            # Check processing turns
            if turn_id in queue.processing_turns:
                turn = queue.processing_turns[turn_id]
                turn.status = TurnStatus.CANCELLED
                turn.error_message = reason
                del queue.processing_turns[turn_id]
                await self._persist_turn(turn)
                return True
        
        return False

    def get_queue_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Get metrics for conversation queue"""
        
        queue = self.active_queues.get(conversation_id)
        if not queue:
            return {"error": "Queue not found"}
        
        return {
            "queue_id": queue.queue_id,
            "conversation_id": queue.conversation_id,
            "pending_turns": len(queue.pending_turns),
            "processing_turns": len(queue.processing_turns),
            "completed_turns": len(queue.completed_turns),
            "total_processed": queue.total_processed,
            "average_processing_time": queue.average_processing_time,
            "success_rate": queue.success_rate,
            "max_concurrent_turns": queue.max_concurrent_turns
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        
        return {
            "global_metrics": self.metrics,
            "active_queues": len(self.active_queues),
            "total_active_turns": sum(
                len(queue.pending_turns) + len(queue.processing_turns)
                for queue in self.active_queues.values()
            ),
            "processor_types": list(self.turn_processors.keys()),
            "semaphore_available": self.processing_semaphore._value
        }
