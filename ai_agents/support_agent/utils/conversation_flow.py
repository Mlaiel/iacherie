"""Conversation Flow Manager - Ultra-Advanced Conversation State Management

Enterprise-grade conversation flow management system providing dynamic conversation
routing, context preservation, multi-turn dialogue handling, and intelligent
conversation orchestration for customer support interactions.

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
from collections import deque

# Graph and state management
import networkx as nx
from transitions import Machine
import redis.asyncio as aioredis

# AI libraries for conversation understanding
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """
Conversation flow states"""

    IDLE = "idle"
    GREETING = "greeting"
    PROBLEM_GATHERING = "problem_gathering"
    SOLUTION_PROVIDING = "solution_providing"
    TROUBLESHOOTING = "troubleshooting"
    ESCALATION = "escalation"
    FEEDBACK_COLLECTION = "feedback_collection"
    CLOSING = "closing"
    TERMINATED = "terminated"

class FlowDirection(Enum):
    """Flow direction types"""

    FORWARD = "forward"
    BACKWARD = "backward"
    BRANCH = "branch"
    LOOP = "loop"
    TERMINATE = "terminate"

class ConversationIntent(Enum):
    """Conversation intent categories"""

    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_HELP = "account_help"
    BILLING_INQUIRY = "billing_inquiry"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL_INFO = "general_info"
    COLLABORATION_HELP = "collaboration_help"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION_SUPPORT = "monetization_support"
    PLATFORM_INTEGRATION = "platform_integration"

@dataclass
class ConversationContext:
    """Comprehensive conversation context"""
    conversation_id: str
    user_id: str
    session_id: str
    current_state: ConversationState
    intent: Optional[ConversationIntent]
    
    # Context data
    collected_data: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Flow management
    state_history: List[ConversationState] = field(default_factory=list)
    branch_points: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_times: List[float] = field(default_factory=list)
    
    # Sentiment and emotion tracking
    sentiment_scores: List[Dict[str, float]] = field(default_factory=list)
    emotion_states: List[str] = field(default_factory=list)
    
    # Quality metrics
    understanding_confidence: List[float] = field(default_factory=list)
    solution_effectiveness: List[float] = field(default_factory=list)

@dataclass
class FlowTransition:
    """
Flow transition definition"""
    from_state: ConversationState
    to_state: ConversationState
    trigger: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    priority: int = 1

@dataclass
class FlowNode:
    """
Conversation flow node"""
    state: ConversationState
    name: str
    description: str
    
    # Node behavior
    entry_actions: List[str] = field(default_factory=list)
    exit_actions: List[str] = field(default_factory=list)
    
    # Content generation
    response_templates: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    
    # Flow control
    timeout_seconds: int = 300  # 5 minutes default
    max_attempts: int = 3
    fallback_state: Optional[ConversationState] = None

class ConversationFlowManager:
    """
Ultra-advanced conversation flow management system"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.flow_graph = nx.DiGraph()
        self.contexts: Dict[str, ConversationContext] = {}
        
        # AI pipelines for conversation understanding
        self.intent_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Initialize flow states
        self._initialize_flow_graph()
        self._setup_state_machines()
    
    def _initialize_flow_graph(self):
        """Initialize the conversation flow graph"""
        # Define flow nodes
        nodes = [
            FlowNode(
                state=ConversationState.IDLE,
                name="Idle",
                description="Waiting for user interaction",
                response_templates=[
                    "Hello! How can I help you today?",
                    "Welcome to IA-Influencer support! What can I assist you with?",
                    "Hi there! I'm here to help with any questions you have."
                ]
            ),
            FlowNode(
                state=ConversationState.GREETING,
                name="Greeting",
                description="Initial greeting and intent detection",
                questions=[
                    "What brings you here today?",
                    "Are you experiencing any specific issues?",
                    "How can I make your experience better?"
                ],
                timeout_seconds=60
            ),
            FlowNode(
                state=ConversationState.PROBLEM_GATHERING,
                name="Problem Gathering",
                description="Collecting detailed problem information",
                questions=[
                    "Can you describe the issue in more detail?",
                    "When did this problem first occur?",
                    "What steps have you already tried?",
                    "Are there any error messages you're seeing?"
                ],
                max_attempts=5
            ),
            FlowNode(
                state=ConversationState.SOLUTION_PROVIDING,
                name="Solution Providing",
                description="Offering solutions and guidance",
                response_templates=[
                    "Based on your description, I think I can help you with this.",
                    "Let me provide you with a step-by-step solution.",
                    "Here's what I recommend trying first:"
                ]
            ),
            FlowNode(
                state=ConversationState.TROUBLESHOOTING,
                name="Troubleshooting",
                description="Interactive troubleshooting process",
                questions=[
                    "Did that solution work for you?",
                    "Are you seeing any changes now?",
                    "Should we try a different approach?"
                ],
                max_attempts=3
            ),
            FlowNode(
                state=ConversationState.ESCALATION,
                name="Escalation",
                description="Escalating to human agent",
                response_templates=[
                    "Let me connect you with one of our human specialists.",
                    "I'll escalate this to our technical team.",
                    "A human agent will be with you shortly."
                ]
            ),
            FlowNode(
                state=ConversationState.FEEDBACK_COLLECTION,
                name="Feedback Collection",
                description="Collecting user satisfaction feedback",
                questions=[
                    "How would you rate the help you received today?",
                    "Was I able to resolve your issue?",
                    "Is there anything else I can help you with?"
                ]
            ),
            FlowNode(
                state=ConversationState.CLOSING,
                name="Closing",
                description="Conversation conclusion",
                response_templates=[
                    "Thank you for using IA-Influencer support!",
                    "Have a great day! Feel free to reach out anytime.",
                    "Glad I could help! Take care!"
                ]
            )
        ]
        
        # Add nodes to graph
        for node in nodes:
            self.flow_graph.add_node(node.state, data=node)
        
        # Define transitions
        transitions = [
            FlowTransition(ConversationState.IDLE, ConversationState.GREETING, "user_message"),
            FlowTransition(ConversationState.GREETING, ConversationState.PROBLEM_GATHERING, "problem_identified"),
            FlowTransition(ConversationState.PROBLEM_GATHERING, ConversationState.SOLUTION_PROVIDING, "problem_understood"),
            FlowTransition(ConversationState.SOLUTION_PROVIDING, ConversationState.TROUBLESHOOTING, "solution_provided"),
            FlowTransition(ConversationState.TROUBLESHOOTING, ConversationState.FEEDBACK_COLLECTION, "problem_resolved"),
            FlowTransition(ConversationState.TROUBLESHOOTING, ConversationState.ESCALATION, "needs_escalation"),
            FlowTransition(ConversationState.ESCALATION, ConversationState.FEEDBACK_COLLECTION, "escalated"),
            FlowTransition(ConversationState.FEEDBACK_COLLECTION, ConversationState.CLOSING, "feedback_collected"),
            FlowTransition(ConversationState.CLOSING, ConversationState.TERMINATED, "conversation_ended"),
            # Backward transitions
            FlowTransition(ConversationState.SOLUTION_PROVIDING, ConversationState.PROBLEM_GATHERING, "need_more_info"),
            FlowTransition(ConversationState.TROUBLESHOOTING, ConversationState.SOLUTION_PROVIDING, "try_different_solution")
        ]
        
        # Add transitions to graph
        for transition in transitions:
            self.flow_graph.add_edge(
                transition.from_state,
                transition.to_state,
                trigger=transition.trigger,
                conditions=transition.conditions,
                actions=transition.actions,
                priority=transition.priority
            )
    
    def _setup_state_machines(self):
        """Setup state machines for conversation flow"""
        self.state_transitions = {
            'trigger': 'user_message',
            'source': list(ConversationState),
            'dest': list(ConversationState),
            'conditions': ['_validate_transition'],
            'after': ['_update_context', '_log_transition']
        }
    
    async def create_conversation(
        self,
        user_id: str,
        session_id: str,
        initial_message: Optional[str] = None
    ) -> ConversationContext:
        """
Create new conversation context"""
        conversation_id = str(uuid.uuid4())
        
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id,
            current_state=ConversationState.IDLE
        )
        
        # Analyze initial message if provided
        if initial_message:
            intent = await self._classify_intent(initial_message)
            context.intent = intent
            
            sentiment = await self._analyze_sentiment(initial_message)
            context.sentiment_scores.append(sentiment)
        
        # Store context
        self.contexts[conversation_id] = context
        await self._persist_context(context)
        
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return context
    
    async def process_message(
        self,
        conversation_id: str,
        message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Process incoming message and manage conversation flow"""
        start_time = datetime.now(timezone.utc)
        
        # Get or create context
        if conversation_id not in self.contexts:
            context = await self._load_context(conversation_id)
            if not context:
                context = await self.create_conversation(user_id, conversation_id, message)
            self.contexts[conversation_id] = context
        else:
            context = self.contexts[conversation_id]
        
        try:
            # Update conversation history
            context.conversation_history.append({
                "timestamp": start_time.isoformat(),
                "speaker": "user",
                "message": message,
                "message_id": str(uuid.uuid4())
            })
            
            # Analyze message
            intent = await self._classify_intent(message)
            sentiment = await self._analyze_sentiment(message)
            
            context.sentiment_scores.append(sentiment)
            if not context.intent:
                context.intent = intent
            
            # Determine next state
            next_state = await self._determine_next_state(context, message, intent, sentiment)
            
            # Execute state transition
            response = await self._execute_state_transition(context, next_state, message)
            
            # Update metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            context.response_times.append(processing_time)
            context.last_updated = datetime.now(timezone.utc)
            
            # Persist context
            await self._persist_context(context)
            
            return {
                "conversation_id": conversation_id,
                "response": response,
                "current_state": context.current_state.value,
                "intent": context.intent.value if context.intent else None,
                "sentiment": sentiment,
                "processing_time": processing_time,
                "confidence": response.get("confidence", 0.8)
            }
            
        except Exception as e:
            logger.error(f"Error processing message in conversation {conversation_id}: {str(e)}")
            return await self._handle_error(context, str(e))
    
    async def _classify_intent(self, message: str) -> ConversationIntent:
        """Classify message intent using AI"""
        candidate_labels = [intent.value for intent in ConversationIntent]
        
        result = self.intent_classifier(message, candidate_labels)
        
        # Get highest scoring intent
        top_intent = result['labels'][0]
        confidence = result['scores'][0]
        
        # Map to enum
        for intent in ConversationIntent:
            if intent.value == top_intent:
                logger.debug(f"Classified intent: {intent.value} (confidence: {confidence:.3f})")
                return intent
        
        return ConversationIntent.GENERAL_INFO
    
    async def _analyze_sentiment(self, message: str) -> Dict[str, float]:
        """Analyze message sentiment"""
        result = self.sentiment_analyzer(message)
        
        sentiment_data = {
            "label": result[0]['label'],
            "score": result[0]['score'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.debug(f"Sentiment analysis: {sentiment_data}")
        return sentiment_data
    
    async def _determine_next_state(
        self,
        context: ConversationContext,
        message: str,
        intent: ConversationIntent,
        sentiment: Dict[str, float]
    ) -> ConversationState:
        """Determine next conversation state based on context"""
        current_state = context.current_state
        
        # State transition logic
        if current_state == ConversationState.IDLE:
            return ConversationState.GREETING
        
        elif current_state == ConversationState.GREETING:
            # Check if user has expressed a problem
            problem_keywords = ["problem", "issue", "error", "bug", "help", "trouble", "not working"]
            if any(keyword in message.lower() for keyword in problem_keywords):
                return ConversationState.PROBLEM_GATHERING
            return ConversationState.PROBLEM_GATHERING  # Default flow
        
        elif current_state == ConversationState.PROBLEM_GATHERING:
            # Check if we have enough information
            if len(context.conversation_history) >= 3:  # Enough info gathered
                return ConversationState.SOLUTION_PROVIDING
            return ConversationState.PROBLEM_GATHERING  # Continue gathering
        
        elif current_state == ConversationState.SOLUTION_PROVIDING:
            return ConversationState.TROUBLESHOOTING
        
        elif current_state == ConversationState.TROUBLESHOOTING:
            # Check if problem is resolved
            positive_keywords = ["works", "fixed", "solved", "good", "thanks", "resolved"]
            negative_keywords = ["still", "not working", "doesn't work", "same problem"]
            
            if any(keyword in message.lower() for keyword in positive_keywords):
                return ConversationState.FEEDBACK_COLLECTION
            elif any(keyword in message.lower() for keyword in negative_keywords):
                # Try different solution or escalate
                if len([h for h in context.state_history if h == ConversationState.TROUBLESHOOTING]) >= 3:
                    return ConversationState.ESCALATION
                return ConversationState.SOLUTION_PROVIDING
            return ConversationState.TROUBLESHOOTING
        
        elif current_state == ConversationState.ESCALATION:
            return ConversationState.FEEDBACK_COLLECTION
        
        elif current_state == ConversationState.FEEDBACK_COLLECTION:
            return ConversationState.CLOSING
        
        elif current_state == ConversationState.CLOSING:
            return ConversationState.TERMINATED
        
        # Default: stay in current state
        return current_state
    
    async def _execute_state_transition(
        self,
        context: ConversationContext,
        next_state: ConversationState,
        user_message: str
    ) -> Dict[str, Any]:
        """Execute state transition and generate response"""
        # Update state
        context.state_history.append(context.current_state)
        context.current_state = next_state
        
        # Get node data
        node_data = self.flow_graph.nodes[next_state]['data']
        
        # Generate response based on state
        if next_state == ConversationState.GREETING:
            response = await self._generate_greeting_response(context)
        elif next_state == ConversationState.PROBLEM_GATHERING:
            response = await self._generate_problem_gathering_response(context)
        elif next_state == ConversationState.SOLUTION_PROVIDING:
            response = await self._generate_solution_response(context, user_message)
        elif next_state == ConversationState.TROUBLESHOOTING:
            response = await self._generate_troubleshooting_response(context)
        elif next_state == ConversationState.ESCALATION:
            response = await self._generate_escalation_response(context)
        elif next_state == ConversationState.FEEDBACK_COLLECTION:
            response = await self._generate_feedback_response(context)
        elif next_state == ConversationState.CLOSING:
            response = await self._generate_closing_response(context)
        else:
            response = await self._generate_default_response(context)
        
        # Add response to history
        context.conversation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speaker": "agent",
            "message": response["message"],
            "state": next_state.value,
            "message_id": str(uuid.uuid4())
        })
        
        return response
    
    async def _generate_greeting_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate greeting response"""
        node_data = self.flow_graph.nodes[ConversationState.GREETING]['data']
        
        # Personalize greeting based on user history
        greeting = "Hello! I'm your AI support assistant for the IA-Influencer platform."
        
        if context.intent:
            if context.intent == ConversationIntent.TECHNICAL_SUPPORT:
                greeting += " I see you might need technical help - I'm here to assist!"
            elif context.intent == ConversationIntent.BILLING_INQUIRY:
                greeting += " I can help you with billing and account questions."
            elif context.intent == ConversationIntent.CONTENT_PROTECTION:
                greeting += " I'm here to help with content protection and copyright issues."
        
        question = "What specific issue can I help you resolve today?"
        
        return {
            "message": f"{greeting}\n\n{question}",
            "suggestions": [
                "I'm having technical problems",
                "I need help with my account",
                "Questions about billing",
                "Content protection issues",
                "Collaboration features"
            ],
            "confidence": 0.9,
            "response_type": "greeting"
        }
    
    async def _generate_problem_gathering_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate problem gathering response"""
        questions = [
            "Can you provide more details about the issue you're experiencing?",
            "When did this problem first start?",
            "What were you trying to do when this happened?",
            "Are you seeing any specific error messages?",
            "Have you tried any troubleshooting steps already?"
        ]
        
        # Select appropriate question based on conversation history
        question_index = min(len([h for h in context.conversation_history if h.get("speaker") == "agent"]), len(questions) - 1)
        selected_question = questions[question_index]
        
        return {
            "message": selected_question,
            "suggestions": [
                "Upload error",
                "Login problems", 
                "Audio processing issues",
                "Copyright detection not working",
                "Collaboration invites not sending"
            ],
            "confidence": 0.8,
            "response_type": "information_gathering"
        }
    
    async def _generate_solution_response(self, context: ConversationContext, user_message: str) -> Dict[str, Any]:
        """Generate solution response based on problem description"""
        # Analyze problem and provide specific solution
        problem_type = await self._analyze_problem_type(user_message, context)
        
        solutions = {
            "upload_error": {
                "message": "For upload issues, let's try these steps:\n\n1. Check your internet connection\n2. Verify file format is supported (MP3, WAV, MP4, JPG, PNG)\n3. Ensure file size is under 100MB\n4. Clear your browser cache and try again",
                "steps": ["Check connection", "Verify format", "Check size", "Clear cache"]
            },
            "login_problem": {
                "message": "For login problems, here's what to try:\n\n1. Reset your password using 'Forgot Password'\n2. Clear browser cookies and cache\n3. Try a different browser or incognito mode\n4. Check if your account is verified",
                "steps": ["Reset password", "Clear cache", "Try different browser", "Check verification"]
            },
            "audio_processing": {
                "message": "For audio processing issues:\n\n1. Ensure audio file is in supported format (MP3, WAV, FLAC)\n2. Check file quality (minimum 128kbps)\n3. Verify file isn't corrupted\n4. Try processing a smaller file first",
                "steps": ["Check format", "Verify quality", "Test corruption", "Try smaller file"]
            },
            "default": {
                "message": "Based on your description, let me provide some general troubleshooting steps:\n\n1. Refresh the page and try again\n2. Clear your browser cache\n3. Check our status page for known issues\n4. Try using a different browser",
                "steps": ["Refresh page", "Clear cache", "Check status", "Different browser"]
            }
        }
        
        solution = solutions.get(problem_type, solutions["default"])
        
        return {
            "message": solution["message"] + "\n\nPlease try these steps and let me know if any of them resolve the issue.",
            "steps": solution["steps"],
            "confidence": 0.85,
            "response_type": "solution",
            "problem_type": problem_type
        }
    
    async def _generate_troubleshooting_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate troubleshooting follow-up response"""
        return {
            "message": "How did that work for you? Did any of those steps help resolve the issue?",
            "suggestions": [
                "Yes, it's working now!",
                "Partially fixed",
                "Still not working",
                "I need to try something else",
                "I need human help"
            ],
            "confidence": 0.8,
            "response_type": "troubleshooting_followup"
        }
    
    async def _generate_escalation_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate escalation response"""
        return {
            "message": "I understand this issue needs more specialized help. Let me connect you with one of our human support specialists who can provide more detailed assistance.\n\nThey'll be able to access your account and provide personalized troubleshooting.\n\nExpected wait time: 5-10 minutes.",
            "escalation_ticket_id": str(uuid.uuid4()),
            "estimated_wait_time": "5-10 minutes",
            "confidence": 1.0,
            "response_type": "escalation"
        }
    
    async def _generate_feedback_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate feedback collection response"""
        return {
            "message": "Before we wrap up, I'd love to get your feedback:\n\nHow would you rate the help you received today? Was I able to resolve your issue to your satisfaction?",
            "rating_options": ["Excellent", "Good", "Fair", "Poor"],
            "suggestions": [
                "Very helpful, thank you!",
                "Issue resolved completely",
                "Partially resolved",
                "Still need help",
                "Want to speak to human"
            ],
            "confidence": 0.9,
            "response_type": "feedback_collection"
        }
    
    async def _generate_closing_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate closing response"""
        return {
            "message": "Thank you for using IA-Influencer support! I'm glad I could help you today.\n\nFeel free to reach out anytime if you have more questions. Have a great day creating amazing content!",
            "session_summary": {
                "duration": (datetime.now(timezone.utc) - context.created_at).total_seconds(),
                "messages_exchanged": len(context.conversation_history),
                "issue_resolved": True,
                "satisfaction_rating": "pending"
            },
            "confidence": 1.0,
            "response_type": "closing"
        }
    
    async def _generate_default_response(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate default response for unknown states"""
        return {
            "message": "I'm here to help! Could you please let me know what specific issue you're facing with the IA-Influencer platform?",
            "confidence": 0.6,
            "response_type": "default"
        }
    
    async def _analyze_problem_type(self, message: str, context: ConversationContext) -> str:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__analyze_problem_type_input(message)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__analyze_problem_type_result(result)
            
                    logger.info(f"AI processing _analyze_problem_type completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _analyze_problem_type failed: {e}")
                    raise
    async def _persist_context(self, context: ConversationContext):
        """Persist conversation context to Redis"""
        try:
            context_data = {
                "conversation_id": context.conversation_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "current_state": context.current_state.value,
                "intent": context.intent.value if context.intent else None,
                "collected_data": context.collected_data,
                "conversation_history": context.conversation_history[-50:],  # Keep last 50 messages
                "state_history": [s.value for s in context.state_history[-20:]],  # Keep last 20 states
                "created_at": context.created_at.isoformat(),
                "last_updated": context.last_updated.isoformat(),
                "sentiment_scores": context.sentiment_scores[-10:],  # Keep last 10
                "response_times": context.response_times[-20:]  # Keep last 20
            }
            
            await self.redis_client.setex(
                f"conversation:{context.conversation_id}",
                3600,  # 1 hour TTL
                json.dumps(context_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to persist context: {str(e)}")
    
    async def _load_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Load conversation context from Redis"""
        try:
            data = await self.redis_client.get(f"conversation:{conversation_id}")
            if not data:
                return None
            
            context_data = json.loads(data)
            
            # Reconstruct context object
            context = ConversationContext(
                conversation_id=context_data["conversation_id"],
                user_id=context_data["user_id"],
                session_id=context_data["session_id"],
                current_state=ConversationState(context_data["current_state"]),
                intent=ConversationIntent(context_data["intent"]) if context_data.get("intent") else None,
                collected_data=context_data.get("collected_data", {}),
                conversation_history=context_data.get("conversation_history", []),
                created_at=datetime.fromisoformat(context_data["created_at"]),
                last_updated=datetime.fromisoformat(context_data["last_updated"]),
                sentiment_scores=context_data.get("sentiment_scores", []),
                response_times=context_data.get("response_times", [])
            )
            
            # Reconstruct state history
            if context_data.get("state_history"):
                context.state_history = [ConversationState(s) for s in context_data["state_history"]]
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to load context: {str(e)}")
            return None
    
    async def _handle_error(self, context: ConversationContext, error: str) -> Dict[str, Any]:
        """Handle conversation errors"""
        logger.error(f"Conversation error in {context.conversation_id}: {error}")
        
        return {
            "conversation_id": context.conversation_id,
            "response": {
                "message": "I apologize, but I encountered an issue processing your request. Let me connect you with a human agent who can help you better.",
                "error": True,
                "escalation_required": True
            },
            "current_state": ConversationState.ESCALATION.value,
            "error": error
        }
    
    async def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation analytics and metrics"""
        context = self.contexts.get(conversation_id)
        if not context:
            context = await self._load_context(conversation_id)
        
        if not context:
            return {}
        
        return {
            "conversation_id": conversation_id,
            "duration_seconds": (context.last_updated - context.created_at).total_seconds(),
            "message_count": len(context.conversation_history),
            "state_changes": len(context.state_history),
            "average_response_time": sum(context.response_times) / len(context.response_times) if context.response_times else 0,
            "intent": context.intent.value if context.intent else None,
            "resolution_path": [s.value for s in context.state_history],
            "sentiment_progression": context.sentiment_scores,
            "current_state": context.current_state.value,
            "completion_status": "completed" if context.current_state == ConversationState.TERMINATED else "active"
        }
    
    async def cleanup_expired_conversations(self):
        """Clean up expired conversation contexts"""
        current_time = datetime.now(timezone.utc)
        expired_conversations = []
        
        for conv_id, context in self.contexts.items():
            # Clean up conversations older than 2 hours of inactivity
            if (current_time - context.last_updated).total_seconds() > 7200:
                expired_conversations.append(conv_id)
        
        # Remove expired conversations
        for conv_id in expired_conversations:
            del self.contexts[conv_id]
            logger.info(f"Cleaned up expired conversation: {conv_id}")
        
        return len(expired_conversations)
