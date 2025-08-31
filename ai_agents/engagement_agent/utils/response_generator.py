"""
Response Generator - Advanced Automated Response & Conversation System

Industrial-grade automated response generation with AI-powered personalization,
contextual understanding, and multi-platform conversation management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import spacy

from ...ai.core.config import settings
from ...ml.models.conversation_models import ConversationAI
from ...ml.models.intent_classification import IntentClassifier
from ...security.content_safety import ContentSafetyChecker
from ...utils.performance_monitor import performance_monitor
from ...utils.cache_manager import CacheManager
from ...utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Types of automated responses"""
    APPRECIATION = "appreciation"
    QUESTION_ANSWER = "question_answer"
    COLLABORATION = "collaboration"
    SUPPORT = "support"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    COMMUNITY_BUILDING = "community_building"
    FEEDBACK_REQUEST = "feedback_request"
    CALL_TO_ACTION = "call_to_action"

class ConversationContext(Enum):
    """Conversation context types"""
    FIRST_TIME_INTERACTION = "first_time"
    RETURNING_USER = "returning"
    VIP_MEMBER = "vip"
    INFLUENCER = "influencer"
    BUSINESS_INQUIRY = "business"
    CASUAL_CHAT = "casual"
    TECHNICAL_QUESTION = "technical"
    COMPLAINT = "complaint"
    PRAISE = "praise"

class ResponsePersonality(Enum):
    """Response personality styles"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    SUPPORTIVE = "supportive"
    EDUCATIONAL = "educational"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"

@dataclass
class ConversationHistory:
    """User conversation history tracking"""
    user_id: str
    platform: str
    first_interaction: datetime
    last_interaction: datetime
    total_interactions: int
    conversation_topics: List[str]
    user_preferences: Dict[str, Any]
    sentiment_history: List[float]
    response_satisfaction: List[float]

@dataclass
class ResponseTemplate:
    """Response template configuration"""
    template_id: str
    response_type: ResponseType
    template_text: str
    personality_style: ResponsePersonality
    required_context: List[str]
    optional_variables: List[str]
    platform_variations: Dict[str, str]
    personalization_level: float
    emoji_usage: bool
    hashtag_inclusion: bool

@dataclass
class ResponseContext:
    """Context information for response generation"""
    original_message: str
    user_id: str
    platform: str
    message_type: str
    conversation_history: Optional[ConversationHistory]
    user_profile: Dict[str, Any]
    content_context: Dict[str, Any]
    current_trends: List[str]
    creator_brand_voice: Dict[str, Any]

class ResponseGenerator:
    """
    Advanced Automated Response Generation System
    
    AI-powered response generation with contextual understanding,
    personality adaptation, and multi-platform optimization.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager(namespace="response_generator")
        self.conversation_ai = ConversationAI()
        self.intent_classifier = IntentClassifier()
        self.content_safety_checker = ContentSafetyChecker()
        self.text_processor = TextProcessor()
        
        # Load NLP models
        self.nlp = None  # Will be loaded in initialize()
        self.sentiment_analyzer = None
        self.tokenizer = None
        
        # Response templates and configurations
        self.response_templates: Dict[str, ResponseTemplate] = {}
        self.conversation_histories: Dict[str, ConversationHistory] = {}
        self.brand_voice_configs: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.response_metrics: Dict[str, Any] = {}
        
        logger.info("Response Generator initialized")

    async def initialize(self) -> bool:
        """Initialize response generator with AI models and templates"""



        try:
            # Load NLP models
            self.nlp = spacy.load("en_core_web_sm")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Initialize AI models
            await self.conversation_ai.load_model()
            await self.intent_classifier.load_model()
            
            # Load response templates
            await self._load_response_templates()
            
            # Load brand voice configurations
            await self._load_brand_voice_configurations()
            
            # Load conversation histories
            await self._load_conversation_histories()
            
            logger.info("Response Generator successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Response Generator: {str(e)}")
            return False

    @performance_monitor.track_execution_time
    async def generate_response(self,
                              context: ResponseContext,
                              response_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Generate contextual automated response
        
        Args:
            context: Response context information
            response_config: Optional response configuration
            
        Returns:
            Optional[Dict]: Generated response with metadata
        """



        try:
            # Analyze input message
            message_analysis = await self._analyze_input_message(context.original_message)
            
            # Classify intent and context
            intent = await self.intent_classifier.classify_intent(context.original_message)
            conversation_context = await self._determine_conversation_context(context)
            
            # Check if response is appropriate
            should_respond = await self._should_generate_response(
                message_analysis, intent, context
            )
            
            if not should_respond:
                return None
            
            # Select response strategy
            response_strategy = await self._select_response_strategy(
                intent, conversation_context, context
            )
            
            # Generate response content
            response_content = await self._generate_response_content(
                response_strategy, context, message_analysis, intent
            )
            
            # Personalize response
            personalized_response = await self._personalize_response(
                response_content, context, conversation_context
            )
            
            # Apply platform-specific formatting
            formatted_response = await self._format_response_for_platform(
                personalized_response, context.platform
            )
            
            # Validate response safety and quality
            validation_result = await self._validate_response(
                formatted_response, context
            )
            
            if not validation_result['valid']:
                logger.warning(f"Generated response failed validation: {validation_result['reason']}")
                return None
            
            # Create response object
            response = {
                'content': formatted_response,
                'response_type': response_strategy['type'],
                'confidence_score': validation_result['confidence'],
                'personalization_level': response_strategy['personalization_level'],
                'estimated_engagement': await self._estimate_response_engagement(
                    formatted_response, context
                ),
                'metadata': {
                    'intent': intent,
                    'context': conversation_context.value,
                    'strategy': response_strategy,
                    'generation_time': datetime.utcnow(),
                    'safety_score': validation_result['safety_score']
                }
            }
            
            # Update conversation history
            await self._update_conversation_history(context, response)
            
            # Cache response for learning
            await self._cache_response_for_learning(context, response)
            
            logger.info(f"Generated response for {context.user_id} on {context.platform}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return None

    async def generate_conversation_starter(self,
                                          creator_id: str,
                                          platform: str,
                                          audience_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate engaging conversation starter content
        
        Args:
            creator_id: Creator identifier
            platform: Target platform
            audience_context: Audience context and preferences
            
        Returns:
            Dict: Generated conversation starter with variants
        """



        try:
            # Analyze audience preferences
            audience_analysis = await self._analyze_audience_preferences(audience_context)
            
            # Generate conversation topics
            trending_topics = await self._get_trending_topics(platform)
            relevant_topics = await self._filter_relevant_topics(
                trending_topics, audience_analysis, creator_id
            )
            
            # Generate starter variants
            starter_variants = []
            
            for topic in relevant_topics[:5]:  # Top 5 topics
                variants = await self._generate_topic_starters(
                    topic, audience_analysis, creator_id, platform
                )
                starter_variants.extend(variants)
            
            # Score and rank starters
            scored_starters = await self._score_conversation_starters(
                starter_variants, audience_context
            )
            
            # Select best starters
            best_starters = sorted(
                scored_starters, 
                key=lambda x: x['score'], 
                reverse=True
            )[:10]
            
            result = {
                'creator_id': creator_id,
                'platform': platform,
                'conversation_starters': best_starters,
                'trending_topics': relevant_topics,
                'audience_insights': audience_analysis,
                'optimal_posting_times': await self._suggest_optimal_posting_times(
                    audience_context, platform
                ),
                'engagement_predictions': await self._predict_starter_engagement(
                    best_starters, audience_context
                )
            }
            
            # Cache results
            await self.cache_manager.set(
                f"conversation_starters_{creator_id}_{platform}",
                result,
                ttl=3600
            )
            
            logger.info(f"Generated {len(best_starters)} conversation starters")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate conversation starter: {str(e)}")
            raise ProcessingError(f"Conversation starter generation failed: {str(e)}")

    async def optimize_response_templates(self,
                                        creator_id: str,
                                        performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize response templates based on performance data
        
        Args:
            creator_id: Creator identifier
            performance_data: Historical response performance data
            
        Returns:
            Dict: Optimized templates and recommendations
        """



        try:
            # Analyze template performance
            template_analysis = await self._analyze_template_performance(performance_data)
            
            # Identify high and low performing patterns
            successful_patterns = await self._identify_successful_patterns(template_analysis)
            problematic_patterns = await self._identify_problematic_patterns(template_analysis)
            
            # Generate optimization recommendations
            optimization_recommendations = []
            
            # Optimize existing templates
            for template_id, template in self.response_templates.items():
                if template_id in template_analysis:
                    optimized_template = await self._optimize_template(
                        template, template_analysis[template_id], successful_patterns
                    )
                    if optimized_template != template:
                        optimization_recommendations.append({
                            'type': 'template_optimization',
                            'template_id': template_id,
                            'original': template,
                            'optimized': optimized_template,
                            'expected_improvement': await self._calculate_expected_improvement(
                                template, optimized_template, template_analysis[template_id]
                            )
                        })
            
            # Suggest new templates
            new_templates = await self._suggest_new_templates(
                successful_patterns, problematic_patterns
            )
            
            for new_template in new_templates:
                optimization_recommendations.append({
                    'type': 'new_template',
                    'template': new_template,
                    'use_case': new_template.response_type.value,
                    'expected_performance': await self._predict_template_performance(
                        new_template, performance_data
                    )
                })
            
            # Generate A/B testing recommendations
            ab_test_recommendations = await self._generate_ab_test_recommendations(
                optimization_recommendations, performance_data
            )
            
            result = {
                'creator_id': creator_id,
                'analysis_date': datetime.utcnow(),
                'template_analysis': template_analysis,
                'successful_patterns': successful_patterns,
                'problematic_patterns': problematic_patterns,
                'optimization_recommendations': optimization_recommendations,
                'ab_test_recommendations': ab_test_recommendations,
                'implementation_priority': await self._prioritize_optimizations(
                    optimization_recommendations
                )
            }
            
            logger.info(f"Generated {len(optimization_recommendations)} template optimizations")
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize response templates: {str(e)}")
            raise ProcessingError(f"Template optimization failed: {str(e)}")

    # Private helper methods
    
    async def _analyze_input_message(self, message: str) -> Dict[str, Any]:
        """Analyze input message for content, sentiment, and characteristics"""



        try:
            # Basic text analysis
            doc = self.nlp(message)
            
            # Extract entities and topics
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
            
            # Sentiment analysis
            sentiment_result = self.sentiment_analyzer(message)[0]
            sentiment_score = sentiment_result['score']
            if sentiment_result['label'] == 'LABEL_0':  # Negative
                sentiment_score = -sentiment_score
            elif sentiment_result['label'] == 'LABEL_2':  # Positive
                pass  # Keep positive
            else:  # Neutral
                sentiment_score = 0
            
            # Message characteristics
            analysis = {
                'length': len(message),
                'word_count': len(keywords),
                'entities': entities,
                'keywords': keywords,
                'sentiment': {
                    'score': sentiment_score,
                    'label': sentiment_result['label'],
                    'confidence': sentiment_result['score']
                },
                'language': await self._detect_language(message),
                'emotion': await self._detect_emotion(message),
                'urgency': await self._detect_urgency(message),
                'question_type': await self._classify_question_type(message),
                'contains_mention': '@' in message,
                'contains_hashtags': '#' in message,
                'contains_url': any(word.startswith('http') for word in message.split())
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze input message: {str(e)}")
            return {}

    async def _determine_conversation_context(self, 
                                            context: ResponseContext) -> ConversationContext:
        """Determine conversation context based on user history and current interaction"""



        try:
            user_history = context.conversation_history
            
            if not user_history:
                return ConversationContext.FIRST_TIME_INTERACTION
            
            # Check user profile characteristics
            user_profile = context.user_profile
            
            if user_profile.get('is_vip', False):
                return ConversationContext.VIP_MEMBER
            
            if user_profile.get('follower_count', 0) > 10000:
                return ConversationContext.INFLUENCER
            
            # Analyze message content
            message_lower = context.original_message.lower()
            
            if any(word in message_lower for word in ['business', 'collaboration', 'partnership', 'sponsor']):
                return ConversationContext.BUSINESS_INQUIRY
            
            if any(word in message_lower for word in ['complaint', 'issue', 'problem', 'wrong']):
                return ConversationContext.COMPLAINT
            
            if any(word in message_lower for word in ['love', 'amazing', 'great', 'awesome', 'fantastic']):
                return ConversationContext.PRAISE
            
            if any(word in message_lower for word in ['how', 'what', 'why', 'when', '?']):
                return ConversationContext.TECHNICAL_QUESTION
            
            # Check interaction frequency
            if user_history.total_interactions > 10:
                return ConversationContext.RETURNING_USER
            
            return ConversationContext.CASUAL_CHAT
            
        except Exception as e:
            logger.error(f"Failed to determine conversation context: {str(e)}")
            return ConversationContext.CASUAL_CHAT

    async def _should_generate_response(self,
                                      message_analysis: Dict[str, Any],
                                      intent: str,
                                      context: ResponseContext) -> bool:
        """Determine if automated response should be generated"""



        try:
            # Don't respond to spam or low-quality messages
            if message_analysis.get('length', 0) < 3:
                return False
            
            # Don't respond to toxic content
            toxicity_score = await self.content_safety_checker.check_toxicity(
                context.original_message
            )
            if toxicity_score > 0.8:
                return False
            
            # Check for response triggers
            message_lower = context.original_message.lower()
            
            # Always respond to direct questions
            if '?' in context.original_message:
                return True
            
            # Respond to mentions
            if context.original_message.startswith('@'):
                return True
            
            # Respond to specific intents
            response_intents = [
                'question', 'collaboration', 'appreciation', 
                'support_request', 'business_inquiry'
            ]
            
            if intent in response_intents:
                return True
            
            # Check conversation history for engagement patterns
            if context.conversation_history:
                if context.conversation_history.total_interactions > 0:
                    avg_satisfaction = statistics.mean(
                        context.conversation_history.response_satisfaction[-10:]
                    ) if context.conversation_history.response_satisfaction else 0.5
                    
                    if avg_satisfaction > 0.7:  # High satisfaction, continue engaging
                        return True
            
            # Random engagement for community building (10% chance)
            import random
            if random.random() < 0.1:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to determine response necessity: {str(e)}")
            return False

    async def _generate_response_content(self,
                                       response_strategy: Dict[str, Any],
                                       context: ResponseContext,
                                       message_analysis: Dict[str, Any],
                                       intent: str) -> str:
        """Generate response content using AI and templates"""



        try:
            response_type = response_strategy['type']
            
            # Try template-based response first
            template_response = await self._generate_template_response(
                response_type, context, message_analysis
            )
            
            if template_response and response_strategy['personalization_level'] < 0.7:
                return template_response
            
            # Generate AI-powered response
            ai_prompt = await self._create_ai_prompt(
                context, message_analysis, intent, response_strategy
            )
            
            ai_response = await self.conversation_ai.generate_response(
                prompt=ai_prompt,
                max_length=response_strategy.get('max_length', 200),
                temperature=response_strategy.get('temperature', 0.7),
                personality_style=response_strategy.get('personality', 'friendly')
            )
            
            # Fallback to template if AI fails
            if not ai_response or len(ai_response.strip()) < 10:
                return template_response or "Thank you for your message! I appreciate your engagement."
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to generate response content: {str(e)}")
            return "Thank you for your message! I appreciate your engagement."

    async def _personalize_response(self,
                                  response_content: str,
                                  context: ResponseContext,
                                  conversation_context: ConversationContext) -> str:
        """Personalize response based on user context and history"""



        try:
            personalized_content = response_content
            
            # Add user name if available
            user_name = context.user_profile.get('name', '').split()[0]
            if user_name and len(user_name) > 1:
                personalized_content = f"Hi {user_name}! {personalized_content}"
            
            # Add context-specific personalization
            if conversation_context == ConversationContext.VIP_MEMBER:
                personalized_content = f" {personalized_content}"
            
            elif conversation_context == ConversationContext.RETURNING_USER:
                personalized_content = f"Great to see you again! {personalized_content}"
            
            elif conversation_context == ConversationContext.FIRST_TIME_INTERACTION:
                personalized_content = f"Welcome! {personalized_content}"
            
            # Add relevant emojis based on sentiment
            sentiment_score = context.user_profile.get('sentiment_history', [0])[-1]
            if sentiment_score > 0.5:
                personalized_content += " "
            elif sentiment_score < -0.5:
                personalized_content += " "
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Failed to personalize response: {str(e)}")
            return response_content

    async def _format_response_for_platform(self,
                                          response: str,
                                          platform: str) -> str:
        """Apply platform-specific formatting"""



        try:
            formatted_response = response
            
            if platform == 'twitter':
                # Ensure under 280 characters
                if len(formatted_response) > 280:
                    formatted_response = formatted_response[:275] + "..."
                    
            elif platform == 'instagram':
                # Add relevant hashtags
                formatted_response += "\n\n#music #creator #community"
                
            elif platform == 'linkedin':
                # More professional tone
                formatted_response = formatted_response.replace("!", ".")
                formatted_response = formatted_response.replace("", "")
                
            elif platform == 'tiktok':
                # Add trending hashtags
                formatted_response += " #fyp #viral"
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Failed to format response for platform: {str(e)}")
            return response

    async def _validate_response(self,
                               response: str,
                               context: ResponseContext) -> Dict[str, Any]:
        """Validate response quality and safety"""



        try:
            validation_result = {
                'valid': True,
                'confidence': 1.0,
                'safety_score': 1.0,
                'reason': None
            }
            
            # Safety check
            safety_result = await self.content_safety_checker.check_content(response)
            validation_result['safety_score'] = safety_result['safety_score']
            
            if safety_result['safety_score'] < 0.8:
                validation_result['valid'] = False
                validation_result['reason'] = 'Safety threshold not met'
                return validation_result
            
            # Quality checks
            if len(response.strip()) < 5:
                validation_result['valid'] = False
                validation_result['reason'] = 'Response too short'
                return validation_result
            
            if len(response) > 1000:
                validation_result['valid'] = False
                validation_result['reason'] = 'Response too long'
                return validation_result
            
            # Check for repetitive patterns
            words = response.split()
            if len(set(words)) < len(words) * 0.5:
                validation_result['confidence'] *= 0.7
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate response: {str(e)}")
            return {'valid': False, 'confidence': 0.0, 'safety_score': 0.0, 'reason': 'Validation error'}


class AutoResponder:
    """
    Automated Response Management & Execution System
    
    Manages automated response workflows, scheduling, and execution
    across multiple platforms with intelligent timing and context awareness.
    """
    
    def __init__(self):
        self.response_generator = ResponseGenerator()
        self.cache_manager = CacheManager(namespace="auto_responder")
        
        # Response queues and scheduling
        self.response_queue: List[Dict[str, Any]] = []
        self.scheduled_responses: Dict[str, Dict[str, Any]] = {}
        self.response_rules: Dict[str, Any] = {}
        
        # Performance tracking
        self.response_analytics: Dict[str, Any] = {}
        
        logger.info("Auto Responder initialized")

    async def setup_automated_responses(self,
                                      creator_id: str,
                                      response_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup automated response rules and triggers
        
        Args:
            creator_id: Creator identifier
            response_rules: Response automation configuration
            
        Returns:
            Dict: Setup confirmation and active rules
        """



        try:
            # Validate response rules
            validation_result = await self._validate_response_rules(response_rules)
            if not validation_result['valid']:
                raise ValidationError(f"Invalid response rules: {validation_result['error']}")
            
            # Store rules
            self.response_rules[creator_id] = response_rules
            
            # Initialize response analytics
            self.response_analytics[creator_id] = {
                'total_responses': 0,
                'response_rate': 0.0,
                'avg_response_time': 0.0,
                'engagement_improvement': 0.0,
                'user_satisfaction': 0.0,
                'last_updated': datetime.utcnow()
            }
            
            # Setup monitoring
            monitoring_config = await self._setup_response_monitoring(creator_id)
            
            result = {
                'creator_id': creator_id,
                'rules_active': True,
                'total_rules': len(response_rules.get('rules', [])),
                'monitoring_config': monitoring_config,
                'estimated_daily_responses': await self._estimate_daily_responses(
                    creator_id, response_rules
                ),
                'setup_timestamp': datetime.utcnow()
            }
            
            logger.info(f"Setup automated responses for creator {creator_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to setup automated responses: {str(e)}")
            raise ProcessingError(f"Auto response setup failed: {str(e)}")

    async def process_incoming_messages(self,
                                      creator_id: str,
                                      messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process incoming messages and generate automated responses
        
        Args:
            creator_id: Creator identifier
            messages: Incoming messages to process
            
        Returns:
            Dict: Processing results and generated responses
        """



        try:
            processing_results = {
                'processed_count': len(messages),
                'responses_generated': 0,
                'responses_queued': 0,
                'responses_sent': 0,
                'skipped_messages': 0,
                'errors': []
            }
            
            for message in messages:
                try:
                    # Check if message should trigger response
                    should_respond = await self._should_respond_to_message(
                        creator_id, message
                    )
                    
                    if not should_respond:
                        processing_results['skipped_messages'] += 1
                        continue
                    
                    # Generate response context
                    response_context = await self._create_response_context(
                        creator_id, message
                    )
                    
                    # Generate response
                    response = await self.response_generator.generate_response(
                        response_context
                    )
                    
                    if response:
                        processing_results['responses_generated'] += 1
                        
                        # Check if immediate or scheduled response
                        send_time = await self._calculate_optimal_response_time(
                            creator_id, message, response
                        )
                        
                        if send_time <= datetime.utcnow():
                            # Send immediately
                            await self._send_response(message, response)
                            processing_results['responses_sent'] += 1
                        else:
                            # Queue for later
                            await self._queue_response(message, response, send_time)
                            processing_results['responses_queued'] += 1
                            
                except Exception as msg_error:
                    processing_results['errors'].append({
                        'message_id': message.get('id', 'unknown'),
                        'error': str(msg_error)
                    })
            
            # Update analytics
            await self._update_response_analytics(creator_id, processing_results)
            
            logger.info(f"Processed {len(messages)} messages for creator {creator_id}")
            return processing_results
            
        except Exception as e:
            logger.error(f"Failed to process incoming messages: {str(e)}")
            raise ProcessingError(f"Message processing failed: {str(e)}")

    async def execute_scheduled_responses(self) -> Dict[str, Any]:
        """Execute scheduled responses that are due"""



        try:
            execution_results = {
                'checked_responses': 0,
                'executed_responses': 0,
                'failed_responses': 0,
                'rescheduled_responses': 0
            }
            
            current_time = datetime.utcnow()
            due_responses = []
            
            # Find due responses
            for response_id, response_data in list(self.scheduled_responses.items()):
                execution_results['checked_responses'] += 1
                
                if response_data['scheduled_time'] <= current_time:
                    due_responses.append((response_id, response_data))
            
            # Execute due responses
            for response_id, response_data in due_responses:
                try:
                    await self._send_response(
                        response_data['original_message'],
                        response_data['response']
                    )
                    
                    # Remove from scheduled responses
                    del self.scheduled_responses[response_id]
                    execution_results['executed_responses'] += 1
                    
                except Exception as send_error:
                    logger.error(f"Failed to send scheduled response {response_id}: {send_error}")
                    
                    # Decide whether to retry or discard
                    if response_data.get('retry_count', 0) < 3:
                        response_data['retry_count'] = response_data.get('retry_count', 0) + 1
                        response_data['scheduled_time'] = current_time + timedelta(minutes=5)
                        execution_results['rescheduled_responses'] += 1
                    else:
                        del self.scheduled_responses[response_id]
                        execution_results['failed_responses'] += 1
            
            logger.info(f"Executed {execution_results['executed_responses']} scheduled responses")
            return execution_results
            
        except Exception as e:
            logger.error(f"Failed to execute scheduled responses: {str(e)}")
            raise ProcessingError(f"Scheduled response execution failed: {str(e)}")

    # Private helper methods
    
    async def _calculate_optimal_response_time(self,
                                             creator_id: str,
                                             message: Dict[str, Any],
                                             response: Dict[str, Any]) -> datetime:
        """Calculate optimal time to send response"""



        try:
            current_time = datetime.utcnow()
            
            # Immediate response for urgent messages
            if message.get('urgent', False) or '?' in message.get('text', ''):
                return current_time
            
            # Consider user's timezone and active hours
            user_timezone = message.get('user_timezone', 'UTC')
            user_active_hours = message.get('user_active_hours', [9, 17])  # 9 AM to 5 PM
            
            # Calculate delay to appear human-like (1-10 minutes)
            import random
            human_delay = random.randint(60, 600)  # 1-10 minutes in seconds
            
            optimal_time = current_time + timedelta(seconds=human_delay)
            
            # Adjust for user's active hours if needed
            user_hour = optimal_time.hour  # This would need proper timezone conversion
            if user_hour < user_active_hours[0] or user_hour > user_active_hours[1]:
                # Schedule for next active period
                if user_hour < user_active_hours[0]:
                    optimal_time = optimal_time.replace(hour=user_active_hours[0], minute=0)
                else:
                    optimal_time = optimal_time + timedelta(days=1)
                    optimal_time = optimal_time.replace(hour=user_active_hours[0], minute=0)
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal response time: {str(e)}")
            return datetime.utcnow() + timedelta(minutes=2)  # Default 2-minute delay
