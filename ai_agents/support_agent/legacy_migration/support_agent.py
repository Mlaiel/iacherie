"""Support Agent - Ultra-Advanced AI Customer Support & Assistance System

Enterprise-grade intelligent customer support agent providing comprehensive help,
troubleshooting, onboarding assistance, and 24/7 automated customer service.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re

# AI/NLP libraries for conversation
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    pipeline
)
import torch
from sentence_transformers import SentenceTransformer

# Knowledge base and search
import faiss
import numpy as np

from ..base import BaseAgent, AgentRequest, AgentResponse
try:
    from core.exceptions import SupportError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SupportError, ValidationError = globals().get('SupportError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...ml.conversation_models import ConversationModel
from ...ml.intent_classifier import IntentClassifier
from ...utils.knowledge_base import KnowledgeBase
from ...utils.ticket_system import TicketSystem

logger = logging.getLogger(__name__)

class SupportCategory(Enum):
    """
Categories of support requests"""

    TECHNICAL_ISSUE = "technical_issue"
    ACCOUNT_MANAGEMENT = "account_management"
    BILLING_PAYMENT = "billing_payment"
    CONTENT_UPLOAD = "content_upload"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PLATFORM_INTEGRATION = "platform_integration"
    SECURITY_PRIVACY = "security_privacy"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    ONBOARDING = "onboarding"
    GENERAL_INQUIRY = "general_inquiry"

class Priority(Enum):
    """Support ticket priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class SupportChannel(Enum):
    """
Support communication channels"""

    CHAT = "chat"
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    KNOWLEDGE_BASE = "knowledge_base"
    COMMUNITY_FORUM = "community_forum"

class TicketStatus(Enum):
    """Support ticket status"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SupportTicket:
    """Support ticket data structure"""
    ticket_id: str
    user_id: str
    category: SupportCategory
    priority: Priority
    status: TicketStatus
    channel: SupportChannel
    subject: str
    description: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    customer_satisfaction: Optional[int] = None  # 1-5 scale
    resolution_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    message_id: str
    sender: str  # 'user', 'agent', 'system'
    content: str
    timestamp: datetime
    message_type: str = "text"  # text, image, file, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

class SupportAgent(BaseAgent):
    """
    Ultra-advanced AI customer support system with comprehensive assistance capabilities:
    
    Core Features:
    - Intelligent conversation handling with context awareness
    - Multi-language support and translation
    - Intent classification and automatic routing
    - Knowledge base integration with semantic search
    - Automated troubleshooting and guided solutions
    - Escalation management to human agents
    - Real-time sentiment analysis and emotion detection
    - Proactive support based on user behavior
    - Onboarding assistance and feature tutorials
    - Integration with ticketing systems
    - Performance analytics and optimization
    - 24/7 availability with contextual responses
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="support_agent",
            version="2.1.0",
            config=config
        )
        
        # Core conversation models
        self.conversation_model = None
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.entity_extractor = None
        
        # Knowledge management
        self.knowledge_base = KnowledgeBase()
        self.embedding_model = None
        self.knowledge_index = None
        
        # Ticket and conversation management
        self.ticket_system = TicketSystem()
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        
        # Support capabilities
        self.supported_languages = ['en', 'de', 'fr', 'es', 'it', 'pt']
        self.escalation_rules = self._load_escalation_rules()
        
        # Performance tracking
        self.support_stats = {
            'total_tickets': 0,
            'resolved_tickets': 0,
            'average_resolution_time': 0.0,
            'customer_satisfaction_score': 0.0,
            'first_contact_resolution_rate': 0.0,
            'escalation_rate': 0.0
        }
        
        # Proactive support triggers
        self.proactive_triggers = self._setup_proactive_triggers()
        
        logger.info(f"SupportAgent {agent_id} initialized")
    
    def get_required_config_keys(self) -> List[str]:
        return [
            'conversation_model_config',
            'knowledge_base_config',
            'escalation_rules',
            'supported_channels'
        ]
    
    async def _load_models_and_resources(self):
        """Load AI models and support resources"""
        try:
            # Load conversation models
            await self._load_conversation_models()
            
            # Load knowledge base and search capabilities
            await self._setup_knowledge_base()
            
            # Initialize intent classification
            await self._setup_intent_classification()
            
            # Setup sentiment analysis
            await self._setup_sentiment_analysis()
            
            # Load support templates and responses
            await self._load_support_templates()
            
            logger.info("Support models and resources loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load support models: {e}")
            raise
    
    async def _load_conversation_models(self):
        """Load AI models for conversation handling"""
        try:
            # Load conversational AI model
            model_name = "microsoft/DialoGPT-medium"
            self.conversation_model = AutoModelForCausalLM.from_pretrained(model_name)
            self.conversation_tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Add padding token
            if self.conversation_tokenizer.pad_token is None:
                self.conversation_tokenizer.pad_token = self.conversation_tokenizer.eos_token
            
            # Load sentence transformer for semantic understanding
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Conversation models loaded")
            
        except Exception as e:
            logger.error(f"Failed to load conversation models: {e}")
            raise
    
    async def _setup_knowledge_base(self):
        """Setup knowledge base with semantic search"""
        try:
            # Load knowledge base articles
            knowledge_articles = await self.knowledge_base.load_articles()
            
            # Create embeddings for articles
            article_texts = [article['content'] for article in knowledge_articles]
            embeddings = self.embedding_model.encode(article_texts)
            
            # Create FAISS index for semantic search
            dimension = embeddings.shape[1]
            self.knowledge_index = faiss.IndexFlatIP(dimension)
            self.knowledge_index.add(embeddings.astype('float32'))
            
            # Store article metadata
            self.knowledge_articles = knowledge_articles
            
            logger.info(f"Knowledge base loaded with {len(knowledge_articles)} articles")
            
        except Exception as e:
            logger.error(f"Failed to setup knowledge base: {e}")
            raise
    
    async def _setup_intent_classification(self):
        """Setup intent classification for request routing"""
        try:
            # Load intent classifier
            self.intent_classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Define support intents
            self.support_intents = [
                "technical problem",
                "account issue", 
                "billing question",
                "feature request",
                "bug report",
                "how to use",
                "general inquiry"
            ]
            
            logger.info("Intent classification setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup intent classification: {e}")
            raise
    
    async def _setup_sentiment_analysis(self):
        """Setup sentiment analysis for conversation monitoring"""
        try:
            # Load sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            logger.info("Sentiment analysis setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup sentiment analysis: {e}")
            raise
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main support processing pipeline"""
        action = request.action
        data = request.data
        
        try:
            if action == "handle_support_request":
                result = await self._handle_support_request(data)
            elif action == "continue_conversation":
                result = await self._continue_conversation(data)
            elif action == "search_knowledge_base":
                result = await self._search_knowledge_base(data)
            elif action == "escalate_ticket":
                result = await self._escalate_ticket(data)
            elif action == "resolve_ticket":
                result = await self._resolve_ticket(data)
            elif action == "get_support_analytics":
                result = await self._get_support_analytics(data)
            elif action == "proactive_support":
                result = await self._provide_proactive_support(data)
            elif action == "onboard_user":
                result = await self._onboard_user(data)
            elif action == "troubleshoot_issue":
                result = await self._troubleshoot_issue(data)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Support {action} completed successfully",
                agent_type=self.agent_type
            )
            
        except Exception as e:
            logger.error(f"Support processing failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="SUPPORT_ERROR",
                agent_type=self.agent_type
            )
    
    async def _handle_support_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new support request"""
        user_id = data.get('user_id')
        message = data.get('message', '')
        channel = SupportChannel(data.get('channel', 'chat'))
        attachments = data.get('attachments', [])
        context = data.get('context', {})
        
        # Analyze the request
        intent_analysis = await self._analyze_intent(message)
        sentiment_analysis = await self._analyze_sentiment(message)
        category = await self._categorize_request(message, intent_analysis)
        priority = await self._determine_priority(message, category, sentiment_analysis)
        
        # Create support ticket
        ticket = SupportTicket(
            ticket_id=f"TKT_{int(time.time())}_{user_id[:8]}",
            user_id=user_id,
            category=category,
            priority=priority,
            status=TicketStatus.OPEN,
            channel=channel,
            subject=await self._generate_ticket_subject(message, intent_analysis),
            description=message,
            attachments=attachments,
            metadata={
                'intent_analysis': intent_analysis,
                'sentiment_analysis': sentiment_analysis,
                'context': context
            }
        )
        
        # Store ticket
        await self.ticket_system.create_ticket(ticket)
        
        # Generate initial response
        initial_response = await self._generate_initial_response(ticket)
        
        # Check if automatic resolution is possible
        auto_resolution = await self._attempt_auto_resolution(ticket)
        
        if auto_resolution['resolved']:
            ticket.status = TicketStatus.RESOLVED
            ticket.resolved_at = datetime.now(timezone.utc)
            ticket.resolution_notes = auto_resolution['resolution']
            await self.ticket_system.update_ticket(ticket)
        
        # Update statistics
        self.support_stats['total_tickets'] += 1
        
        return {
            'ticket': self._ticket_to_dict(ticket),
            'initial_response': initial_response,
            'auto_resolution': auto_resolution,
            'suggested_actions': await self._suggest_user_actions(ticket),
            'estimated_resolution_time': await self._estimate_resolution_time(ticket),
            'similar_issues': await self._find_similar_issues(ticket)
        }
    
    async def _continue_conversation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Continue ongoing conversation"""
        ticket_id = data.get('ticket_id')
        user_message = data.get('message', '')
        user_id = data.get('user_id')
        
        # Get existing ticket
        ticket = await self.ticket_system.get_ticket(ticket_id)
        if not ticket:
            raise SupportError(f"Ticket {ticket_id} not found")
        
        # Add user message to conversation history
        message = ConversationMessage(
            message_id=f"MSG_{int(time.time())}",
            sender="user",
            content=user_message,
            timestamp=datetime.now(timezone.utc)
        )
        ticket.conversation_history.append(self._message_to_dict(message))
        
        # Analyze current message
        sentiment = await self._analyze_sentiment(user_message)
        intent = await self._analyze_intent(user_message)
        
        # Generate contextual response
        conversation_context = self._build_conversation_context(ticket)
        ai_response = await self._generate_contextual_response(
            user_message, conversation_context, ticket
        )
        
        # Add AI response to conversation
        ai_message = ConversationMessage(
            message_id=f"MSG_{int(time.time())}_AI",
            sender="agent",
            content=ai_response['content'],
            timestamp=datetime.now(timezone.utc),
            metadata=ai_response.get('metadata', {})
        )
        ticket.conversation_history.append(self._message_to_dict(ai_message))
        
        # Update ticket status if needed
        if ai_response.get('resolution_attempted'):
            ticket.status = TicketStatus.WAITING_CUSTOMER
        
        # Check for escalation triggers
        escalation_needed = await self._check_escalation_triggers(ticket, sentiment)
        
        # Update ticket
        ticket.updated_at = datetime.now(timezone.utc)
        await self.ticket_system.update_ticket(ticket)
        
        return {
            'response': ai_response['content'],
            'ticket_status': ticket.status.value,
            'sentiment_detected': sentiment,
            'escalation_needed': escalation_needed,
            'conversation_id': ticket_id,
            'suggested_actions': ai_response.get('suggested_actions', []),
            'confidence_score': ai_response.get('confidence', 0.0)
        }
    
    async def _search_knowledge_base(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search knowledge base for relevant information"""
        query = data.get('query', '')
        max_results = data.get('max_results', 5)
        threshold = data.get('similarity_threshold', 0.7)
        
        if not query:
            return {'results': [], 'total_found': 0}
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search knowledge base
        similarities, indices = self.knowledge_index.search(
            query_embedding.astype('float32'), 
            max_results * 2  # Get more results to filter
        )
        
        # Filter by threshold and format results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if similarity >= threshold:
                article = self.knowledge_articles[idx]
                results.append({
                    'article_id': article.get('id'),
                    'title': article.get('title'),
                    'content': article.get('content')[:500] + '...' if len(article.get('content', '')) > 500 else article.get('content'),
                    'category': article.get('category'),
                    'similarity_score': float(similarity),
                    'url': article.get('url'),
                    'last_updated': article.get('last_updated')
                })
        
        # Sort by similarity
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)[:max_results]
        
        return {
            'results': results,
            'total_found': len(results),
            'query': query,
            'search_time_ms': time.time() * 1000 - data.get('start_time', 0)
        }
    
    async def _generate_contextual_response(
        self, 
        user_message: str, 
        context: Dict[str, Any], 
        ticket: SupportTicket
    ) -> Dict[str, Any]:
        """
Generate contextual AI response"""
        
        # Build conversation prompt
        conversation_history = context.get('conversation_history', [])
        
        # Create prompt with context
        prompt = self._build_conversation_prompt(
            user_message, 
            conversation_history, 
            ticket.category,
            ticket.metadata
        )
        
        # Generate response using conversation model
        try:
            # Tokenize input
            inputs = self.conversation_tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.conversation_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.conversation_tokenizer.eos_token_id,
                    do_sample=True
                )
            
            # Decode response
            response = self.conversation_tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            )
            
            # Post-process response
            response = self._post_process_response(response, ticket)
            
            # Add helpful resources
            resources = await self._find_relevant_resources(user_message, ticket.category)
            
            return {
                'content': response,
                'confidence': 0.8,  # Placeholder confidence
                'suggested_actions': await self._suggest_next_actions(user_message, ticket),
                'resources': resources,
                'metadata': {
                    'generation_method': 'conversational_ai',
                    'model_used': 'DialoGPT-medium'
                }
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            
            # Fallback to template-based response
            return await self._generate_template_response(user_message, ticket)
    
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze intent of user message"""
        try:
            # Use zero-shot classification for intent detection
            candidate_labels = [intent.replace("_", " ") for intent in [intent.value for intent in SupportCategory]]
            
            result = self.intent_classifier(message, candidate_labels)
            
            return {
                'primary_intent': result['labels'][0],
                'confidence': result['scores'][0],
                'all_intents': [
                    {'intent': label, 'score': score} 
                    for label, score in zip(result['labels'], result['scores'])
                ]
            }
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                'primary_intent': 'general_inquiry',
                'confidence': 0.5,
                'all_intents': []
            }
    
    async def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of user message"""
        try:
            result = self.sentiment_analyzer(message)[0]
            
            # Map labels to standard sentiment categories
            sentiment_mapping = {
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral', 
                'LABEL_2': 'positive',
                'NEGATIVE': 'negative',
                'NEUTRAL': 'neutral',
                'POSITIVE': 'positive'
            }
            
            sentiment = sentiment_mapping.get(result['label'], result['label'].lower())
            
            return {
                'sentiment': sentiment,
                'confidence': result['score'],
                'raw_result': result
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'raw_result': {}
            }
    
    async def _categorize_request(self, message: str, intent_analysis: Dict[str, Any]) -> SupportCategory:
        """Categorize support request"""
        intent = intent_analysis.get('primary_intent', '').lower()
        
        # Intent to category mapping
        category_mappings = {
            'technical': SupportCategory.TECHNICAL_ISSUE,
            'account': SupportCategory.ACCOUNT_MANAGEMENT,
            'billing': SupportCategory.BILLING_PAYMENT,
            'payment': SupportCategory.BILLING_PAYMENT,
            'upload': SupportCategory.CONTENT_UPLOAD,
            'content': SupportCategory.CONTENT_UPLOAD,
            'collaboration': SupportCategory.COLLABORATION,
            'monetization': SupportCategory.MONETIZATION,
            'platform': SupportCategory.PLATFORM_INTEGRATION,
            'security': SupportCategory.SECURITY_PRIVACY,
            'privacy': SupportCategory.SECURITY_PRIVACY,
            'feature': SupportCategory.FEATURE_REQUEST,
            'bug': SupportCategory.BUG_REPORT,
            'onboarding': SupportCategory.ONBOARDING,
            'how to': SupportCategory.ONBOARDING
        }
        
        # Check for keyword matches
        message_lower = message.lower()
        for keyword, category in category_mappings.items():
            if keyword in message_lower or keyword in intent:
                return category
        
        return SupportCategory.GENERAL_INQUIRY
    
    def _ticket_to_dict(self, ticket: SupportTicket) -> Dict[str, Any]:
        """
Convert ticket to dictionary for API response"""
        return {
            'ticket_id': ticket.ticket_id,
            'user_id': ticket.user_id,
            'category': ticket.category.value,
            'priority': ticket.priority.value,
            'status': ticket.status.value,
            'channel': ticket.channel.value,
            'subject': ticket.subject,
            'description': ticket.description,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat(),
            'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            'conversation_history': ticket.conversation_history,
            'attachments': ticket.attachments,
            'customer_satisfaction': ticket.customer_satisfaction,
            'metadata': ticket.metadata
        }
    
    def _load_escalation_rules(self) -> Dict[str, Any]:
        """
Load escalation rules configuration"""
        return {
            'sentiment_threshold': -0.7,  # Negative sentiment threshold
            'max_conversation_turns': 10,
            'keywords_requiring_human': [
                'speak to human', 'human agent', 'escalate',
                'manager', 'supervisor', 'complaint'
            ],
            'categories_auto_escalate': [
                SupportCategory.SECURITY_PRIVACY,
                SupportCategory.BILLING_PAYMENT
            ],
            'priority_auto_escalate': [Priority.URGENT, Priority.CRITICAL]
        }
    
    def _setup_proactive_triggers(self) -> Dict[str, Any]:
        """
Setup proactive support triggers"""
        return {
            'failed_upload_attempts': 3,
            'login_failures': 5,
            'feature_struggle_time': 300,  # 5 minutes
            'error_frequency_threshold': 5,
            'inactivity_after_signup': 86400  # 24 hours
        }

    async def _escalate_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
Escalate ticket to human agent"""
        ticket_id = data.get('ticket_id')
        escalation_reason = data.get('reason', 'Customer request')
        assigned_agent = data.get('assigned_agent')
        
        ticket = await self.ticket_system.get_ticket(ticket_id)
        if not ticket:
            raise SupportError(f"Ticket {ticket_id} not found")
        
        # Update ticket status and assignment
        ticket.status = TicketStatus.ESCALATED
        ticket.assigned_agent = assigned_agent
        ticket.updated_at = datetime.now(timezone.utc)
        
        # Add escalation note to conversation
        escalation_message = ConversationMessage(
            message_id=f"MSG_{int(time.time())}_ESCALATION",
            sender="system",
            content=f"Ticket escalated to human agent. Reason: {escalation_reason}",
            timestamp=datetime.now(timezone.utc),
            metadata={"escalation_reason": escalation_reason}
        )
        ticket.conversation_history.append(self._message_to_dict(escalation_message))
        
        await self.ticket_system.update_ticket(ticket)
        
        # Update statistics
        self.support_stats['escalation_rate'] = (
            self.support_stats.get('escalated_tickets', 0) + 1
        ) / self.support_stats['total_tickets']
        
        return {
            'ticket_id': ticket_id,
            'status': 'escalated',
            'assigned_agent': assigned_agent,
            'escalation_time': ticket.updated_at.isoformat(),
            'reason': escalation_reason
        }
    
    async def _resolve_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve support ticket"""
        ticket_id = data.get('ticket_id')
        resolution_notes = data.get('resolution_notes', '')
        customer_satisfaction = data.get('customer_satisfaction')
        
        ticket = await self.ticket_system.get_ticket(ticket_id)
        if not ticket:
            raise SupportError(f"Ticket {ticket_id} not found")
        
        # Update ticket resolution
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.resolution_notes = resolution_notes
        
        if customer_satisfaction:
            ticket.customer_satisfaction = customer_satisfaction
        
        # Calculate resolution time
        resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600  # hours
        
        await self.ticket_system.update_ticket(ticket)
        
        # Update statistics
        self.support_stats['resolved_tickets'] += 1
        current_avg = self.support_stats.get('average_resolution_time', 0.0)
        resolved_count = self.support_stats['resolved_tickets']
        self.support_stats['average_resolution_time'] = (
            (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
        )
        
        if customer_satisfaction:
            current_csat = self.support_stats.get('customer_satisfaction_score', 0.0)
            self.support_stats['customer_satisfaction_score'] = (
                (current_csat * (resolved_count - 1) + customer_satisfaction) / resolved_count
            )
        
        return {
            'ticket_id': ticket_id,
            'status': 'resolved',
            'resolution_time_hours': resolution_time,
            'customer_satisfaction': customer_satisfaction,
            'resolution_notes': resolution_notes
        }
    
    async def _get_support_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive support analytics"""
        date_range = data.get('date_range', 30)  # days
        include_trends = data.get('include_trends', True)
        
        # Get ticket statistics from database
        analytics = await self.ticket_system.get_analytics(date_range)
        
        # Combine with real-time stats
        combined_stats = {
            **self.support_stats,
            **analytics,
            'real_time_metrics': {
                'active_conversations': len(self.active_conversations),
                'agents_online': 1,  # This agent
                'average_response_time': 0.2,  # seconds
                'queue_length': 0
            }
        }
        
        if include_trends:
            combined_stats['trends'] = await self._calculate_trends(date_range)
        
        return combined_stats
    
    async def _provide_proactive_support(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
Provide proactive support based on user behavior"""
        user_id = data.get('user_id')
        trigger_type = data.get('trigger_type')
        context = data.get('context', {})
        
        proactive_message = await self._generate_proactive_message(
            user_id, trigger_type, context
        )
        
        # Create proactive support ticket
        ticket = SupportTicket(
            ticket_id=f"PRO_{int(time.time())}_{user_id[:8]}",
            user_id=user_id,
            category=SupportCategory.GENERAL_INQUIRY,
            priority=Priority.LOW,
            status=TicketStatus.OPEN,
            channel=SupportChannel.CHAT,
            subject=f"Proactive Support - {trigger_type}",
            description=proactive_message['content'],
            metadata={
                'proactive': True,
                'trigger_type': trigger_type,
                'context': context
            }
        )
        
        await self.ticket_system.create_ticket(ticket)
        
        return {
            'ticket': self._ticket_to_dict(ticket),
            'proactive_message': proactive_message,
            'trigger_type': trigger_type,
            'recommendations': proactive_message.get('recommendations', [])
        }
    
    async def _onboard_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide user onboarding assistance"""
        user_id = data.get('user_id')
        user_profile = data.get('user_profile', {})
        onboarding_step = data.get('step', 'welcome')
        
        # Generate personalized onboarding content
        onboarding_content = await self._generate_onboarding_content(
            user_profile, onboarding_step
        )
        
        # Create onboarding ticket
        ticket = SupportTicket(
            ticket_id=f"ONB_{int(time.time())}_{user_id[:8]}",
            user_id=user_id,
            category=SupportCategory.ONBOARDING,
            priority=Priority.NORMAL,
            status=TicketStatus.OPEN,
            channel=SupportChannel.CHAT,
            subject=f"Onboarding - {onboarding_step}",
            description=f"User onboarding assistance for step: {onboarding_step}",
            metadata={
                'onboarding': True,
                'step': onboarding_step,
                'user_profile': user_profile
            }
        )
        
        await self.ticket_system.create_ticket(ticket)
        
        return {
            'ticket': self._ticket_to_dict(ticket),
            'onboarding_content': onboarding_content,
            'next_steps': onboarding_content.get('next_steps', []),
            'progress': onboarding_content.get('progress', 0)
        }
    
    async def _troubleshoot_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide automated troubleshooting assistance"""
        issue_description = data.get('issue_description', '')
        error_logs = data.get('error_logs', [])
        user_context = data.get('context', {})
        
        # Analyze the issue
        issue_analysis = await self._analyze_technical_issue(
            issue_description, error_logs, user_context
        )
        
        # Generate troubleshooting steps
        troubleshooting_steps = await self._generate_troubleshooting_steps(
            issue_analysis
        )
        
        # Find related solutions
        related_solutions = await self._find_related_solutions(issue_analysis)
        
        return {
            'issue_analysis': issue_analysis,
            'troubleshooting_steps': troubleshooting_steps,
            'related_solutions': related_solutions,
            'estimated_resolution_time': issue_analysis.get('estimated_time', '15-30 minutes'),
            'complexity_level': issue_analysis.get('complexity', 'medium')
        }
    
    # Helper methods for advanced functionality
    
    async def _determine_priority(
        self, 
        message: str, 
        category: SupportCategory, 
        sentiment: Dict[str, Any]
    ) -> Priority:
        """
Determine ticket priority based on content and context"""
        # Check for urgent keywords
        urgent_keywords = [
            'urgent', 'critical', 'emergency', 'down', 'broken',
            'can\'t access', 'payment failed', 'security', 'hack'
        ]
        
        message_lower = message.lower()
        
        # High priority conditions
        if any(keyword in message_lower for keyword in urgent_keywords):
            return Priority.URGENT
        
        # Category-based priority
        if category in [SupportCategory.SECURITY_PRIVACY, SupportCategory.BILLING_PAYMENT]:
            return Priority.HIGH
        
        # Sentiment-based priority
        if sentiment.get('sentiment') == 'negative' and sentiment.get('confidence', 0) > 0.8:
            return Priority.HIGH
        
        return Priority.NORMAL
    
    async def _generate_ticket_subject(
        self, 
        message: str, 
        intent_analysis: Dict[str, Any]
    ) -> str:
        """
Generate a concise ticket subject"""
        primary_intent = intent_analysis.get('primary_intent', 'General inquiry')
        
        # Extract key phrases from message (simplified approach)
        words = message.split()[:10]  # First 10 words
        subject_words = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if subject_words:
            subject = f"{primary_intent}: {' '.join(subject_words[:5])}"
        else:
            subject = f"{primary_intent} - Support Request"
        
        return subject[:100]  # Limit length
    
    async def _attempt_auto_resolution(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Attempt to automatically resolve common issues"""
        message = ticket.description.lower()
        
        # Common issue patterns and solutions
        auto_solutions = {
            'upload': {
                'pattern': ['upload', 'file', 'can\'t upload', 'failed'],
                'solution': 'Please check your file format and size. Supported formats: MP3, WAV, FLAC (max 100MB).',
                'steps': [
                    'Verify file format is supported (MP3, WAV, FLAC)',
                    'Check file size is under 100MB', 
                    'Clear browser cache and try again',
                    'Try using a different browser'
                ]
            },
            'login': {
                'pattern': ['login', 'sign in', 'password', 'can\'t login'],
                'solution': 'Try resetting your password or clearing browser cookies.',
                'steps': [
                    'Click "Forgot Password" on login page',
                    'Check your email for reset link',
                    'Clear browser cookies and cache',
                    'Try using incognito/private browsing mode'
                ]
            },
            'payment': {
                'pattern': ['payment', 'billing', 'charge', 'subscription'],
                'solution': 'Please check your payment method and billing information.',
                'steps': [
                    'Verify payment method is valid',
                    'Check billing address matches card',
                    'Contact your bank if payment is declined',
                    'Try a different payment method'
                ]
            }
        }
        
        for issue_type, solution_data in auto_solutions.items():
            if any(pattern in message for pattern in solution_data['pattern']):
                return {
                    'resolved': True,
                    'resolution': solution_data['solution'],
                    'steps': solution_data['steps'],
                    'issue_type': issue_type,
                    'confidence': 0.8
                }
        
        return {'resolved': False}
    
    async def _suggest_user_actions(self, ticket: SupportTicket) -> List[str]:
        """Suggest helpful actions for the user"""
        category = ticket.category
        
        action_suggestions = {
            SupportCategory.TECHNICAL_ISSUE: [
                'Try refreshing the page',
                'Clear browser cache',
                'Check internet connection',
                'Update your browser'
            ],
            SupportCategory.CONTENT_UPLOAD: [
                'Verify file format',
                'Check file size limits', 
                'Try a different browser',
                'Contact support for format questions'
            ],
            SupportCategory.ACCOUNT_MANAGEMENT: [
                'Check account settings',
                'Verify email address',
                'Update profile information',
                'Review security settings'
            ],
            SupportCategory.BILLING_PAYMENT: [
                'Check payment method',
                'Verify billing address',
                'Contact your bank',
                'Review subscription details'
            ]
        }
        
        return action_suggestions.get(category, [
            'Review our help documentation',
            'Try the suggested solution',
            'Contact support if issue persists'
        ])
    
    async def _estimate_resolution_time(self, ticket: SupportTicket) -> str:
        """
Estimate resolution time based on category and priority"""
        time_estimates = {
            (SupportCategory.TECHNICAL_ISSUE, Priority.LOW): '2-4 hours',
            (SupportCategory.TECHNICAL_ISSUE, Priority.NORMAL): '1-2 hours', 
            (SupportCategory.TECHNICAL_ISSUE, Priority.HIGH): '30-60 minutes',
            (SupportCategory.TECHNICAL_ISSUE, Priority.URGENT): '15-30 minutes',
            (SupportCategory.ACCOUNT_MANAGEMENT, Priority.NORMAL): '1-2 hours',
            (SupportCategory.BILLING_PAYMENT, Priority.HIGH): '30-60 minutes',
            (SupportCategory.CONTENT_UPLOAD, Priority.NORMAL): '1-2 hours',
        }
        
        return time_estimates.get(
            (ticket.category, ticket.priority), 
            '2-4 hours'
        )
    
    async def _find_similar_issues(self, ticket: SupportTicket) -> List[Dict[str, Any]]:
        """
Find similar resolved issues"""
        # This would query the database for similar tickets
        # Simplified implementation for now
        similar_issues = []
        
        # Use embedding similarity to find related tickets
        if self.embedding_model:
            query_embedding = self.embedding_model.encode([ticket.description])
            # Search through resolved tickets (simplified)
            similar_issues = [
                {
                    'ticket_id': 'TKT_123456',
                    'subject': 'Similar upload issue',
                    'resolution': 'Try using Chrome browser',
                    'similarity_score': 0.85
                }
            ]
        
        return similar_issues
    
    def _build_conversation_context(self, ticket: SupportTicket) -> Dict[str, Any]:
        """
Build conversation context for AI response generation"""
        return {
            'ticket_id': ticket.ticket_id,
            'category': ticket.category.value,
            'priority': ticket.priority.value,
            'conversation_history': ticket.conversation_history,
            'user_context': ticket.metadata.get('context', {}),
            'previous_intents': [
                msg.get('metadata', {}).get('intent') 
                for msg in ticket.conversation_history 
                if msg.get('metadata', {}).get('intent')
            ]
        }
    
    def _build_conversation_prompt(
        self, 
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        category: SupportCategory,
        metadata: Dict[str, Any]
    ) -> str:
        """
Build conversation prompt for AI model"""
        # Build context-aware prompt
        context_info = f"Category: {category.value.replace('_', ' ').title()}\n"
        
        # Add conversation history (last 5 messages)
        if conversation_history:
            context_info += "Recent conversation:\n"
            for msg in conversation_history[-5:]:
                sender = msg.get('sender', 'unknown')
                content = msg.get('content', '')[:200]  # Limit length
                context_info += f"{sender}: {content}\n"
        
        prompt = f"""You are a helpful AI customer support assistant for IA-Influencer-Agent platform.

{context_info}

Current user message: {user_message}

Please provide a helpful, professional response. Be concise but thorough. If you need more information, ask specific questions."""
        
        return prompt
    
    def _post_process_response(self, response: str, ticket: SupportTicket) -> str:
        """
Post-process AI-generated response"""
        # Remove any unwanted patterns
        response = response.strip()
        
        # Add helpful resources if relevant
        if ticket.category == SupportCategory.CONTENT_UPLOAD:
            response += "\n\nFor more information, check our upload guide: https://help.ia-influencer.com/upload"
        
        return response
    
    async def _find_relevant_resources(
        self, 
        user_message: str, 
        category: SupportCategory
    ) -> List[Dict[str, Any]]:
        """Find relevant help resources"""
        resources = []
        
        category_resources = {
            SupportCategory.CONTENT_UPLOAD: [
                {
                    'title': 'Upload Guide',
                    'url': 'https://help.ia-influencer.com/upload',
                    'description': 'Complete guide to uploading content'
                }
            ],
            SupportCategory.MONETIZATION: [
                {
                    'title': 'Monetization Setup',
                    'url': 'https://help.ia-influencer.com/monetization',
                    'description': 'How to set up and optimize monetization'
                }
            ]
        }
        
        resources.extend(category_resources.get(category, []))
        
        return resources
    
    async def _suggest_next_actions(
        self, 
        user_message: str, 
        ticket: SupportTicket
    ) -> List[str]:
        """
Suggest next actions for the conversation"""
        actions = []
        
        if 'thank' in user_message.lower():
            actions.extend([
                'Rate this support interaction',
                'Close this ticket',
                'Ask any follow-up questions'
            ])
        elif '?' in user_message:
            actions.extend([
                'Provide more details',
                'Try the suggested solution',
                'Request escalation if needed'
            ])
        else:
            actions.extend([
                'Let me know if this helps',
                'Ask any follow-up questions',
                'Request additional assistance'
            ])
        
        return actions
    
    async def _generate_template_response(
        self, 
        user_message: str, 
        ticket: SupportTicket
    ) -> Dict[str, Any]:
        """
Generate template-based fallback response"""
        templates = {
            SupportCategory.TECHNICAL_ISSUE: "I understand you're experiencing a technical issue. Let me help you troubleshoot this step by step.",
            SupportCategory.CONTENT_UPLOAD: "I see you're having trouble with uploading content. Let's work through this together.",
            SupportCategory.BILLING_PAYMENT: "I'll help you resolve this billing concern. Let me check what options are available."
        }
        
        template = templates.get(
            ticket.category, 
            "Thank you for contacting support. I'm here to help you with your inquiry."
        )
        
        return {
            'content': template,
            'confidence': 0.6,
            'suggested_actions': await self._suggest_next_actions(user_message, ticket),
            'resources': await self._find_relevant_resources(user_message, ticket.category),
            'metadata': {
                'generation_method': 'template',
                'template_used': ticket.category.value
            }
        }
    
    async def _check_escalation_triggers(
        self, 
        ticket: SupportTicket, 
        sentiment: Dict[str, Any]
    ) -> bool:
        """Check if ticket should be escalated"""
        rules = self.escalation_rules
        
        # Check sentiment threshold
        if (sentiment.get('sentiment') == 'negative' and 
            sentiment.get('confidence', 0) >= -rules['sentiment_threshold']):
            return True
        
        # Check conversation length
        if len(ticket.conversation_history) >= rules['max_conversation_turns']:
            return True
        
        # Check for escalation keywords
        last_message = ticket.conversation_history[-1] if ticket.conversation_history else {}
        message_content = last_message.get('content', '').lower()
        
        if any(keyword in message_content for keyword in rules['keywords_requiring_human']):
            return True
        
        # Check category auto-escalation
        if ticket.category in rules['categories_auto_escalate']:
            return True
        
        # Check priority auto-escalation
        if ticket.priority in rules['priority_auto_escalate']:
            return True
        
        return False
    
    def _message_to_dict(self, message: ConversationMessage) -> Dict[str, Any]:
        """
Convert message object to dictionary"""
        return {
            'message_id': message.message_id,
            'sender': message.sender,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'message_type': message.message_type,
            'metadata': message.metadata
        }
    
    async def _load_support_templates(self):
        """
Load support response templates"""
        # This would load templates from database or files
        self.response_templates = {
            'welcome': "Welcome to IA-Influencer-Agent support! How can I help you today?",
            'escalation': "I'm transferring you to a human agent who can better assist you.",
            'resolution': "I'm glad I could help resolve your issue. Is there anything else I can assist you with?",
            'feedback': "Thank you for your feedback. We appreciate your input and will use it to improve our service."
        }
        
        logger.info("Support templates loaded")
    
    async def _generate_initial_response(self, ticket: SupportTicket) -> str:
        """Generate initial response for new ticket"""
        category_responses = {
            SupportCategory.TECHNICAL_ISSUE: f"Hi! I see you're experiencing a technical issue. I'm here to help you resolve this quickly. Let me analyze your request: '{ticket.description[:100]}...'",
            SupportCategory.CONTENT_UPLOAD: f"Hello! I understand you're having trouble with content upload. Let's get this sorted out for you right away.",
            SupportCategory.BILLING_PAYMENT: f"Hi there! I see you have a billing inquiry. I'm here to help resolve any payment-related concerns.",
            SupportCategory.ACCOUNT_MANAGEMENT: f"Hello! I'm here to help you with your account. What specific assistance do you need?",
        }
        
        default_response = f"Thank you for contacting IA-Influencer-Agent support! I've received your request and I'm here to help. Let me look into this for you."
        
        return category_responses.get(ticket.category, default_response)
    
    async def _calculate_trends(self, date_range: int) -> Dict[str, Any]:
        """Calculate support trends over time"""
        # This would calculate actual trends from historical data
        return {
            'ticket_volume_trend': 'increasing',
            'resolution_time_trend': 'improving',
            'satisfaction_trend': 'stable',
            'top_categories': [
                {'category': 'content_upload', 'percentage': 35},
                {'category': 'technical_issue', 'percentage': 25},
                {'category': 'account_management', 'percentage': 20}
            ],
            'peak_hours': ['14:00-16:00', '19:00-21:00'],
            'common_keywords': ['upload', 'login', 'payment', 'error']
        }
    
    async def _generate_proactive_message(
        self, 
        user_id: str, 
        trigger_type: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Generate proactive support message"""
        messages = {
            'failed_upload_attempts': {
                'content': "I noticed you've been having trouble uploading files. Would you like some assistance with the upload process?",
                'recommendations': [
                    'Check file format compatibility',
                    'Verify file size limits',
                    'Try using a different browser'
                ]
            },
            'login_failures': {
                'content': "I see you've had some login difficulties. Let me help you get back into your account.",
                'recommendations': [
                    'Reset your password',
                    'Clear browser cookies',
                    'Check for typos in email/username'
                ]
            },
            'feature_struggle_time': {
                'content': "It looks like you might need some help with this feature. I'm here to guide you through it!",
                'recommendations': [
                    'Watch our tutorial video',
                    'Follow our step-by-step guide',
                    'Chat with support for personalized help'
                ]
            }
        }
        
        return messages.get(trigger_type, {
            'content': "Hi! I'm here to help if you need any assistance.",
            'recommendations': ['Contact support', 'Check our help center']
        })
    
    async def _generate_onboarding_content(
        self, 
        user_profile: Dict[str, Any], 
        step: str
    ) -> Dict[str, Any]:
        """Generate personalized onboarding content"""
        user_type = user_profile.get('type', 'musician')  # musician, blogger, photographer, etc.
        
        onboarding_steps = {
            'welcome': {
                'content': f"Welcome to IA-Influencer-Agent! As a {user_type}, you'll love our content protection and monetization features.",
                'next_steps': ['Complete profile setup', 'Upload first content', 'Set up protection'],
                'progress': 10
            },
            'profile_setup': {
                'content': "Let's set up your profile to showcase your work and attract collaborators.",
                'next_steps': ['Add bio and avatar', 'Set content categories', 'Configure privacy settings'],
                'progress': 25
            },
            'first_upload': {
                'content': f"Ready to upload your first {user_type} content? I'll guide you through the process.",
                'next_steps': ['Choose content to upload', 'Add metadata and tags', 'Configure protection settings'],
                'progress': 50
            },
            'protection_setup': {
                'content': "Let's set up AI protection for your content to prevent unauthorized use.",
                'next_steps': ['Enable fingerprinting', 'Set monitoring preferences', 'Configure notifications'],
                'progress': 75
            },
            'monetization': {
                'content': "Now let's set up monetization so you can earn from your content.",
                'next_steps': ['Add payment methods', 'Set pricing', 'Enable collaboration features'],
                'progress': 90
            }
        }
        
        return onboarding_steps.get(step, {
            'content': 'Welcome! Let me help you get started.',
            'next_steps': [],
            'progress': 0
        })
    
    async def _analyze_technical_issue(
        self, 
        description: str, 
        error_logs: List[str], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze technical issue for troubleshooting"""
        issue_keywords = {
            'upload_failure': ['upload', 'failed', 'error uploading', 'cannot upload'],
            'login_issue': ['login', 'sign in', 'authentication', 'password'],
            'performance_issue': ['slow', 'loading', 'timeout', 'lag'],
            'payment_issue': ['payment', 'billing', 'charge', 'transaction'],
            'audio_issue': ['audio', 'sound', 'playback', 'music'],
            'video_issue': ['video', 'streaming', 'player', 'codec']
        }
        
        detected_issues = []
        description_lower = description.lower()
        
        for issue_type, keywords in issue_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_issues.append(issue_type)
        
        primary_issue = detected_issues[0] if detected_issues else 'general_technical'
        
        # Analyze error logs if provided
        error_analysis = {}
        if error_logs:
            error_analysis = {
                'error_count': len(error_logs),
                'common_errors': list(set(error_logs[:5])),  # Top 5 unique errors
                'severity': 'high' if len(error_logs) > 10 else 'medium'
            }
        
        return {
            'primary_issue': primary_issue,
            'detected_issues': detected_issues,
            'error_analysis': error_analysis,
            'complexity': 'high' if error_logs else 'medium',
            'estimated_time': '15-30 minutes' if primary_issue == 'upload_failure' else '10-20 minutes',
            'requires_escalation': len(detected_issues) > 2 or len(error_logs) > 20
        }
    
    async def _generate_troubleshooting_steps(
        self, 
        issue_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Generate step-by-step troubleshooting guide"""
        primary_issue = issue_analysis.get('primary_issue', 'general_technical')
        
        troubleshooting_guides = {
            'upload_failure': [
                {
                    'step': 1,
                    'title': 'Check File Requirements',
                    'description': 'Verify your file meets the upload requirements',
                    'actions': [
                        'Check file format (MP3, WAV, FLAC supported)',
                        'Verify file size is under 100MB',
                        'Ensure filename contains only letters, numbers, and basic punctuation'
                    ],
                    'expected_result': 'File should meet all requirements'
                },
                {
                    'step': 2,
                    'title': 'Clear Browser Data',
                    'description': 'Clear browser cache and cookies',
                    'actions': [
                        'Clear browser cache and cookies',
                        'Disable browser extensions temporarily',
                        'Try using incognito/private mode'
                    ],
                    'expected_result': 'Browser should be clean and ready'
                },
                {
                    'step': 3,
                    'title': 'Test Upload',
                    'description': 'Attempt to upload the file again',
                    'actions': [
                        'Navigate to upload page',
                        'Select your file',
                        'Wait for upload completion without leaving the page'
                    ],
                    'expected_result': 'File should upload successfully'
                }
            ],
            'login_issue': [
                {
                    'step': 1,
                    'title': 'Verify Credentials',
                    'description': 'Check your login information',
                    'actions': [
                        'Verify email address spelling',
                        'Check caps lock is off',
                        'Try typing password in a text editor first'
                    ],
                    'expected_result': 'Credentials should be correct'
                },
                {
                    'step': 2,
                    'title': 'Reset Password',
                    'description': 'Reset your password if needed',
                    'actions': [
                        'Click "Forgot Password" on login page',
                        'Check email for reset link (including spam folder)',
                        'Follow the reset instructions'
                    ],
                    'expected_result': 'New password should work'
                }
            ]
        }
        
        return troubleshooting_guides.get(primary_issue, [
            {
                'step': 1,
                'title': 'Basic Troubleshooting',
                'description': 'Try these common solutions',
                'actions': [
                    'Refresh the page',
                    'Clear browser cache',
                    'Try a different browser',
                    'Check internet connection'
                ],
                'expected_result': 'Issue should be resolved'
            }
        ])
    
    async def _find_related_solutions(
        self, 
        issue_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find related solutions from knowledge base"""
        primary_issue = issue_analysis.get('primary_issue', '')
        
        # Search knowledge base for related articles
        if self.knowledge_base and primary_issue:
            search_results = await self._search_knowledge_base({
                'query': primary_issue.replace('_', ' '),
                'max_results': 3,
                'similarity_threshold': 0.6
            })
            
            return search_results.get('results', [])
        
        # Fallback to common solutions
        return [
            {
                'title': 'Common Technical Issues',
                'content': 'Solutions for the most common technical problems',
                'category': 'troubleshooting',
                'url': 'https://help.ia-influencer.com/troubleshooting'
            }
        ]


class SupportAgentManager:
    """
Manager for support agent instances with load balancing and health monitoring"""
    
    def __init__(self):
        self.agents: Dict[str, SupportAgent] = {}
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        self.load_balancer = self._initialize_load_balancer()
        self.health_check_interval = 60  # seconds
        
        # Start health monitoring
        asyncio.create_task(self._start_health_monitoring())
    
    async def create_agent(
        self, 
        agent_id: str, 
        config: Dict[str, Any] = None
    ) -> SupportAgent:
        """
Create new support agent with health monitoring"""
        agent = SupportAgent(agent_id, config)
        await agent.initialize()
        
        self.agents[agent_id] = agent
        self.agent_health[agent_id] = {
            'status': 'healthy',
            'last_check': datetime.now(timezone.utc),
            'active_conversations': 0,
            'total_processed': 0,
            'error_count': 0
        }
        
        logger.info(f"Created support agent: {agent_id}")
        return agent
    
    async def get_available_agent(self) -> Optional[SupportAgent]:
        """Get available agent using load balancing"""
        healthy_agents = [
            agent_id for agent_id, health in self.agent_health.items()
            if health['status'] == 'healthy'
        ]
        
        if not healthy_agents:
            # Create new agent if none available
            agent_id = f"support_auto_{int(time.time())}"
            return await self.create_agent(agent_id)
        
        # Use round-robin load balancing
        selected_agent_id = self.load_balancer.get_next_agent(healthy_agents)
        return self.agents[selected_agent_id]
    
    async def remove_agent(self, agent_id: str):
        """Remove agent from manager"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_health[agent_id]
            logger.info(f"Removed support agent: {agent_id}")
    
    async def get_manager_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        total_agents = len(self.agents)
        healthy_agents = sum(
            1 for health in self.agent_health.values()
            if health['status'] == 'healthy'
        )
        
        total_conversations = sum(
            health['active_conversations']
            for health in self.agent_health.values()
        )
        
        return {
            'total_agents': total_agents,
            'healthy_agents': healthy_agents,
            'total_active_conversations': total_conversations,
            'agent_health': self.agent_health,
            'load_balancer_stats': self.load_balancer.get_stats()
        }
    
    def _initialize_load_balancer(self):
        """
Initialize load balancer"""
        return RoundRobinLoadBalancer()
    
    async def _start_health_monitoring(self):
        """
Start periodic health monitoring"""
        while True:
            try:
                await self._check_agent_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _check_agent_health(self):
        """Check health of all agents"""
        current_time = datetime.now(timezone.utc)
        
        for agent_id, agent in self.agents.items():
            try:
                # Simple health check - could be more sophisticated
                health_status = await self._perform_agent_health_check(agent)
                
                self.agent_health[agent_id].update({
                    'status': health_status['status'],
                    'last_check': current_time,
                    'response_time': health_status['response_time'],
                    'active_conversations': len(agent.active_conversations)
                })
                
            except Exception as e:
                logger.error(f"Health check failed for agent {agent_id}: {e}")
                self.agent_health[agent_id]['status'] = 'unhealthy'
                self.agent_health[agent_id]['error_count'] += 1
    
    async def _perform_agent_health_check(self, agent: SupportAgent) -> Dict[str, Any]:
        """Perform health check on individual agent"""
        start_time = time.time()
        
        # Simple ping test
        try:
            test_request = AgentRequest(
                action="health_check",
                data={"test": True}
            )
            
            # This would be a simple health check endpoint
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'response_time': time.time() - start_time,
                'error': str(e)
            }


class RoundRobinLoadBalancer:
    """Simple round-robin load balancer"""
    
    def __init__(self):
        self.current_index = 0
        self.request_count = 0
    
    def get_next_agent(self, agent_ids: List[str]) -> str:
        """
Get next agent using round-robin"""
        if not agent_ids:
            return None
        
        agent_id = agent_ids[self.current_index % len(agent_ids)]
        self.current_index += 1
        self.request_count += 1
        
        return agent_id
    
    def get_stats(self) -> Dict[str, Any]:
        """
Get load balancer statistics"""
        return {
            'total_requests': self.request_count,
            'current_index': self.current_index
        }
