"""Support Agent Index - Ultra-Advanced AI Customer Support Entry Point

Main entry point and orchestrator for the Support Agent system, providing
unified access to all support agent capabilities including conversation
management, knowledge base integration, human agent escalation, multi-language
support, and performance analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
import json
import uuid
from dataclasses import asdict

# Core support agent components
from .support_agent import SupportAgent, SupportAgentManager, SupportCategory, Priority
from .conversation_flow import ConversationFlowManager, ConversationState
from .knowledge_base import KnowledgeBaseManager, SearchQuery, KnowledgeCategory
from .escalation_manager import EscalationManager, EscalationTrigger, EscalationPriority
from .performance_analytics import SupportAnalytics, PerformanceMetric, MetricType
from .multilanguage_manager import MultiLanguageManager, SupportedLanguage, TranslationRequest
from .config import SupportConfig
from .exceptions import SupportError

# External dependencies
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class SupportAgentIndex:
    """Ultra-advanced support agent system orchestrator and main entry point"""    
    def __init__(self, config: SupportConfig):
        self.config = config
        self.redis_client: Optional[aioredis.Redis] = None
        self.db_session: Optional[AsyncSession] = None
        
        # Core components
        self.agent_manager: Optional[SupportAgentManager] = None
        self.conversation_flow_manager: Optional[ConversationFlowManager] = None
        self.knowledge_base_manager: Optional[KnowledgeBaseManager] = None
        self.escalation_manager: Optional[EscalationManager] = None
        self.analytics: Optional[SupportAnalytics] = None
        self.multilanguage_manager: Optional[MultiLanguageManager] = None
        
        # System status
        self.is_initialized = False
        self.startup_time: Optional[datetime] = None
        self.component_health: Dict[str, bool] = {}
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        
        # Active conversations
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(
        self, 
        redis_client: aioredis.Redis, 
        db_session: AsyncSession,
        initialize_defaults: bool = True
    ):
        """Initialize all support agent system components"""        try:
            self.redis_client = redis_client
            self.db_session = db_session
            
            logger.info("Initializing Support Agent system components...")
            
            # Initialize components in dependency order
            components = []
            
            # 1. Analytics (foundational)
            self.analytics = SupportAnalytics(redis_client, db_session)
            components.append(("analytics", self.analytics))
            
            # 2. Multi-language support
            self.multilanguage_manager = MultiLanguageManager(redis_client)
            components.append(("multilanguage", self.multilanguage_manager))
            
            # 3. Knowledge base
            self.knowledge_base_manager = KnowledgeBaseManager(
                redis_client, db_session
            )
            components.append(("knowledge_base", self.knowledge_base_manager))
            
            # 4. Conversation flow manager
            self.conversation_flow_manager = ConversationFlowManager(redis_client)
            components.append(("conversation_flow", self.conversation_flow_manager))
            
            # 5. Escalation manager
            self.escalation_manager = EscalationManager(redis_client)
            components.append(("escalation", self.escalation_manager))
            
            # 6. Main agent manager
            self.agent_manager = SupportAgentManager(
                config=self.config,
                redis_client=redis_client,
                db_session=db_session,
                conversation_manager=self.conversation_flow_manager,
                knowledge_manager=self.knowledge_base_manager,
                escalation_manager=self.escalation_manager,
                analytics=self.analytics,
                language_manager=self.multilanguage_manager
            )
            components.append(("agent_manager", self.agent_manager))
            
            # Initialize each component and track health
            for component_name, component in components:
                try:
                    if hasattr(component, 'initialize'):
                        await component.initialize()
                    self.component_health[component_name] = True
                    logger.info(f"✅ {component_name} initialized successfully")
                except Exception as e:
                    self.component_health[component_name] = False
                    logger.error(f"❌ Failed to initialize {component_name}: {str(e)}")
                    if component_name == "agent_manager":
                        # Agent manager is critical
                        raise
            
            # Mark system as initialized
            self.is_initialized = True
            self.startup_time = datetime.now(timezone.utc)
            
            # Record initialization metrics
            await self._record_system_metric("system_startup", 1.0)
            
            logger.info("🚀 Support Agent system fully initialized and operational")
            
        except Exception as e:
            logger.error(f"💥 Critical failure during Support Agent initialization: {str(e)}")
            raise SupportError(f"System initialization failed: {str(e)}")
    
    async def process_support_request(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        language: Optional[str] = None,
        channel: str = "web_chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process comprehensive support request with full AI orchestration"""        if not self.is_initialized or not self.agent_manager:
            raise SupportError("Support Agent system not initialized")
        
        start_time = datetime.now(timezone.utc)
        request_id = str(uuid.uuid4())
        
        try:
            self.request_count += 1
            
            # Language detection and setup
            detected_language, confidence = await self._detect_and_setup_language(
                message, user_id, language
            )
            
            # Get or create conversation context
            if not conversation_id:
                conversation_context = await self.conversation_flow_manager.create_conversation(
                    user_id, request_id, message
                )
                conversation_id = conversation_context.conversation_id
            
            # Store active conversation
            self.active_conversations[conversation_id] = {
                "user_id": user_id,
                "start_time": start_time,
                "language": detected_language,
                "channel": channel,
                "last_activity": start_time
            }
            
            # Process through conversation flow
            conversation_response = await self.conversation_flow_manager.process_message(
                conversation_id, message, user_id
            )
            
            # Determine if knowledge base search is needed
            knowledge_results = []
            if conversation_response.get("current_state") in [
                ConversationState.PROBLEM_GATHERING.value,
                ConversationState.SOLUTION_PROVIDING.value
            ]:
                knowledge_results = await self._search_knowledge_base(
                    message, detected_language, conversation_response.get("intent")
                )
            
            # Check escalation triggers
            escalation_needed = await self._check_escalation_triggers(
                conversation_response, knowledge_results, user_id
            )
            
            escalation_info = None
            if escalation_needed:
                escalation_info = await self._handle_escalation(
                    conversation_id, user_id, conversation_response, message
                )
            
            # Generate final response
            final_response = await self._generate_comprehensive_response(
                conversation_response,
                knowledge_results,
                escalation_info,
                detected_language,
                user_id
            )
            
            # Record performance metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._record_request_metrics(processing_time, conversation_response, user_id)
            
            # Update conversation tracking
            self.active_conversations[conversation_id]["last_activity"] = datetime.now(timezone.utc)
            
            return {
                "request_id": request_id,
                "conversation_id": conversation_id,
                "response": final_response,
                "language": detected_language.value,
                "processing_time": processing_time,
                "knowledge_articles_found": len(knowledge_results),
                "escalation_triggered": escalation_needed,
                "escalation_info": escalation_info,
                "system_status": "operational",
                "confidence_score": conversation_response.get("confidence", 0.8)
            }
            
        except Exception as e:
            self.error_count += 1
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            await self._record_system_metric("request_error", 1.0)
            await self._record_system_metric("error_response_time", processing_time)
            
            logger.error(f"Support request processing failed for user {user_id}: {str(e)}")
            
            # Return error response with fallback support
            return await self._generate_error_response(
                request_id, user_id, str(e), detected_language if 'detected_language' in locals() else SupportedLanguage.ENGLISH
            )
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get comprehensive conversation history with analytics"""        try:
            # Get conversation analytics
            analytics = await self.conversation_flow_manager.get_conversation_analytics(conversation_id)
            
            # Get active conversation info
            active_info = self.active_conversations.get(conversation_id, {})
            
            return {
                "conversation_id": conversation_id,
                "analytics": analytics,
                "active_session": active_info,
                "system_insights": {
                    "total_system_requests": self.request_count,
                    "average_response_time": self.total_response_time / max(self.request_count, 1),
                    "error_rate": self.error_count / max(self.request_count, 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return {"error": str(e)}
    
    async def search_knowledge_base(
        self,
        query: str,
        language: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search knowledge base with multi-language support"""        try:
            # Detect language if not provided
            if language:
                search_language = SupportedLanguage(language)
            else:
                search_language, _ = await self.multilanguage_manager.detect_language(query, user_id)
            
            # Translate query to English for search if needed
            search_query = query
            if search_language != SupportedLanguage.ENGLISH:
                translation_request = TranslationRequest(
                    text=query,
                    source_language=search_language,
                    target_language=SupportedLanguage.ENGLISH,
                    domain="customer_support"
                )
                translation_result = await self.multilanguage_manager.translate_text(translation_request)
                search_query = translation_result.translated_text
            
            # Create search query
            kb_query = SearchQuery(
                query=search_query,
                user_id=user_id or "anonymous",
                session_id=str(uuid.uuid4()),
                category_filter=KnowledgeCategory(category) if category else None,
                language_filter=search_language.value
            )
            
            # Perform search
            results = await self.knowledge_base_manager.search(kb_query)
            
            # Translate results back to user language if needed
            if search_language != SupportedLanguage.ENGLISH:
                for result in results:
                    if result.snippet:
                        snippet_translation = await self.multilanguage_manager.translate_text(
                            TranslationRequest(
                                text=result.snippet,
                                source_language=SupportedLanguage.ENGLISH,
                                target_language=search_language
                            )
                        )
                        result.snippet = snippet_translation.translated_text
            
            # Record analytics
            await self._record_system_metric("knowledge_search", 1.0)
            await self._record_system_metric("knowledge_results_count", float(len(results)))
            
            return {
                "query": query,
                "results": [
                    {
                        "id": result.article.id,
                        "title": result.article.title,
                        "snippet": result.snippet,
                        "relevance_score": result.relevance_score,
                        "category": result.article.category.value,
                        "match_type": result.match_type
                    }
                    for result in results
                ],
                "total_found": len(results),
                "search_language": search_language.value,
                "processing_time": 0.0  # Would be calculated in real implementation
            }
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {str(e)}")
            return {"error": str(e)}
    
    async def create_escalation(
        self,
        conversation_id: str,
        user_id: str,
        reason: str,
        priority: Optional[str] = None,
        specialty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create manual escalation to human agent"""        try:
            escalation_request = await self.escalation_manager.create_escalation(
                conversation_id=conversation_id,
                user_id=user_id,
                trigger=EscalationTrigger.USER_REQUEST,
                reason=reason,
                priority=EscalationPriority(priority) if priority else None,
                requested_specialty=specialty
            )
            
            # Attempt immediate assignment
            assignment_result = await self.escalation_manager.assign_to_agent(
                escalation_request.escalation_id
            )
            
            return {
                "escalation_id": escalation_request.escalation_id,
                "priority": escalation_request.priority.value,
                "estimated_wait_time": escalation_request.estimated_wait_time,
                "assigned_agent": assignment_result[0] if assignment_result else None,
                "agent_info": {
                    "name": assignment_result[1].name,
                    "specialties": [s.value for s in assignment_result[1].specialties]
                } if assignment_result else None,
                "status": "assigned" if assignment_result else "queued"
            }
            
        except Exception as e:
            logger.error(f"Escalation creation failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_system_analytics(
        self,
        time_period: Optional[str] = "last_24h",
        include_detailed_metrics: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive system analytics and performance metrics"""        try:
            # Calculate time range
            if time_period == "last_24h":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=24)
            elif time_period == "last_7d":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=7)
            elif time_period == "last_30d":
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=30)
            else:
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=24)
            
            analytics = {
                "system_status": await self.get_system_status(),
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration": time_period
                },
                "performance_summary": {
                    "total_requests": self.request_count,
                    "error_rate": self.error_count / max(self.request_count, 1),
                    "average_response_time": self.total_response_time / max(self.request_count, 1),
                    "active_conversations": len(self.active_conversations)
                }
            }
            
            # Get component-specific analytics
            if self.analytics and include_detailed_metrics:
                performance_report = await self.analytics.generate_performance_report(
                    start_time, end_time,
                    include_trends=True,
                    include_recommendations=True,
                    include_visualizations=True
                )
                analytics["detailed_performance"] = asdict(performance_report)
            
            if self.knowledge_base_manager:
                kb_analytics = await self.knowledge_base_manager.get_knowledge_analytics()
                analytics["knowledge_base"] = kb_analytics
            
            if self.escalation_manager:
                escalation_analytics = await self.escalation_manager.get_escalation_analytics()
                analytics["escalations"] = escalation_analytics
            
            if self.multilanguage_manager:
                language_analytics = await self.multilanguage_manager.get_language_analytics()
                analytics["languages"] = language_analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get system analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and health metrics"""        if not self.is_initialized:
            return {"status": "not_initialized", "components": {}}
        
        try:
            uptime = (
                datetime.now(timezone.utc) - self.startup_time
            ).total_seconds() if self.startup_time else 0
            
            # Check component health
            component_status = {}
            for component_name, is_healthy in self.component_health.items():
                component_status[component_name] = {
                    "healthy": is_healthy,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate overall system health
            healthy_components = sum(1 for h in self.component_health.values() if h)
            total_components = len(self.component_health)
            health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0
            
            status = {
                "status": "operational" if health_percentage >= 80 else "degraded" if health_percentage >= 50 else "critical",
                "health_percentage": health_percentage,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "components": component_status,
                "performance": {
                    "requests_processed": self.request_count,
                    "error_count": self.error_count,
                    "error_rate_percent": (self.error_count / max(self.request_count, 1)) * 100,
                    "average_response_time_ms": (self.total_response_time / max(self.request_count, 1)) * 1000,
                    "active_conversations": len(self.active_conversations)
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components"""        health_results = {
            "overall_health": "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "recommendations": []
        }
        
        try:
            # Check each component
            components_to_check = [
                ("redis", self.redis_client),
                ("agent_manager", self.agent_manager),
                ("conversation_flow", self.conversation_flow_manager),
                ("knowledge_base", self.knowledge_base_manager),
                ("escalation_manager", self.escalation_manager),
                ("analytics", self.analytics),
                ("multilanguage", self.multilanguage_manager)
            ]
            
            healthy_count = 0
            total_count = len(components_to_check)
            
            for component_name, component in components_to_check:
                try:
                    # Basic connectivity/availability check
                    if component_name == "redis" and component:
                        await component.ping()
                        health_results["components"][component_name] = {"status": "healthy", "details": "Connection active"}
                        healthy_count += 1
                    elif component and hasattr(component, 'health_check'):
                        component_health = await component.health_check()
                        health_results["components"][component_name] = component_health
                        if component_health.get("status") == "healthy":
                            healthy_count += 1
                    elif component:
                        health_results["components"][component_name] = {"status": "healthy", "details": "Component loaded"}
                        healthy_count += 1
                    else:
                        health_results["components"][component_name] = {"status": "unavailable", "details": "Component not initialized"}
                
                except Exception as e:
                    health_results["components"][component_name] = {"status": "unhealthy", "error": str(e)}
            
            # Determine overall health
            health_percentage = (healthy_count / total_count) * 100
            if health_percentage >= 90:
                health_results["overall_health"] = "excellent"
            elif health_percentage >= 70:
                health_results["overall_health"] = "good"
            elif health_percentage >= 50:
                health_results["overall_health"] = "fair"
            else:
                health_results["overall_health"] = "poor"
            
            health_results["health_score"] = health_percentage
            
            # Generate recommendations
            if health_percentage < 100:
                unhealthy_components = [
                    name for name, status in health_results["components"].items()
                    if status.get("status") != "healthy"
                ]
                health_results["recommendations"].append(
                    f"Address issues with components: {', '.join(unhealthy_components)}"
                )
            
            if self.error_count > 0:
                error_rate = (self.error_count / max(self.request_count, 1)) * 100
                if error_rate > 5:
                    health_results["recommendations"].append(
                        f"High error rate detected: {error_rate:.1f}% - investigate error patterns"
                    )
            
            return health_results
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            health_results["overall_health"] = "error"
            health_results["error"] = str(e)
            return health_results
    
    async def shutdown(self):
        """Gracefully shutdown all support agent system components"""        try:
            logger.info("🔄 Initiating graceful shutdown of Support Agent system...")
            
            shutdown_tasks = []
            
            # Shutdown components in reverse order
            components_to_shutdown = [
                ("agent_manager", self.agent_manager),
                ("escalation_manager", self.escalation_manager),
                ("conversation_flow", self.conversation_flow_manager),
                ("knowledge_base", self.knowledge_base_manager),
                ("analytics", self.analytics),
                ("multilanguage", self.multilanguage_manager)
            ]
            
            for component_name, component in components_to_shutdown:
                if component and hasattr(component, 'shutdown'):
                    try:
                        await component.shutdown()
                        logger.info(f"✅ {component_name} shutdown complete")
                    except Exception as e:
                        logger.error(f"❌ Error shutting down {component_name}: {str(e)}")
            
            # Clear active conversations
            self.active_conversations.clear()
            
            # Record final metrics
            if self.analytics:
                await self._record_system_metric("system_shutdown", 1.0)
            
            # Mark as not initialized
            self.is_initialized = False
            
            logger.info("🛑 Support Agent system shutdown complete")
            
        except Exception as e:
            logger.error(f"💥 Error during shutdown: {str(e)}")
    
    # Private helper methods
    
    async def _detect_and_setup_language(
        self, 
        message: str, 
        user_id: str, 
        language_hint: Optional[str]
    ) -> Tuple[SupportedLanguage, float]:
        """Detect language and setup user language profile"""        if language_hint:
            try:
                return SupportedLanguage(language_hint), 1.0
            except ValueError:
                pass
        
        # Use multi-language manager for detection
        detected_language, confidence = await self.multilanguage_manager.detect_language(
            message, user_id
        )
        
        # Create or update language profile
        profile = await self.multilanguage_manager.get_language_profile(user_id)
        if not profile:
            await self.multilanguage_manager.create_language_profile(
                user_id, detected_language
            )
        
        return detected_language, confidence
    
    async def _search_knowledge_base(
        self, 
        message: str, 
        language: SupportedLanguage, 
        intent: Optional[str]
    ) -> List[Any]:
        """Search knowledge base with context"""        try:
            # Map conversation intent to knowledge category
            category_mapping = {
                "technical_support": KnowledgeCategory.TECHNICAL_SUPPORT,
                "billing_inquiry": KnowledgeCategory.BILLING_SUPPORT,
                "content_protection": KnowledgeCategory.CONTENT_PROTECTION,
                "collaboration_help": KnowledgeCategory.COLLABORATION,
            }
            
            search_query = SearchQuery(
                query=message,
                user_id="system_search",
                session_id=str(uuid.uuid4()),
                category_filter=category_mapping.get(intent),
                language_filter=language.value,
                max_results=5
            )
            
            return await self.knowledge_base_manager.search(search_query)
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {str(e)}")
            return []
    
    async def _check_escalation_triggers(
        self, 
        conversation_response: Dict[str, Any], 
        knowledge_results: List[Any], 
        user_id: str
    ) -> bool:
        """Check if escalation to human agent is needed"""        try:
            # Low AI confidence
            if conversation_response.get("confidence", 1.0) < 0.6:
                return True
            
            # No knowledge base results
            if len(knowledge_results) == 0 and conversation_response.get("current_state") == ConversationState.SOLUTION_PROVIDING.value:
                return True
            
            # User explicitly requested human help
            message_lower = conversation_response.get("user_message", "").lower()
            human_request_keywords = ["human", "agent", "person", "real person", "speak to someone"]
            if any(keyword in message_lower for keyword in human_request_keywords):
                return True
            
            # Multiple failed attempts
            conversation_state = conversation_response.get("current_state")
            if conversation_state == ConversationState.TROUBLESHOOTING.value:
                # Would check conversation history for repeated failures
                pass
            
            return False
            
        except Exception as e:
            logger.error(f"Escalation trigger check failed: {str(e)}")
            return False
    
    async def _handle_escalation(
        self, 
        conversation_id: str, 
        user_id: str, 
        conversation_response: Dict[str, Any], 
        message: str
    ) -> Dict[str, Any]:
        """Handle escalation to human agent"""        try:
            # Determine escalation reason and priority
            confidence = conversation_response.get("confidence", 1.0)
            if confidence < 0.3:
                reason = "Low AI confidence in solution"
                priority = EscalationPriority.HIGH
            elif "urgent" in message.lower() or "emergency" in message.lower():
                reason = "User indicated urgency"
                priority = EscalationPriority.URGENT
            else:
                reason = "AI unable to resolve issue"
                priority = EscalationPriority.NORMAL
            
            # Create escalation
            escalation_request = await self.escalation_manager.create_escalation(
                conversation_id=conversation_id,
                user_id=user_id,
                trigger=EscalationTrigger.AI_CONFIDENCE_LOW,
                reason=reason,
                priority=priority,
                context=conversation_response
            )
            
            # Attempt assignment
            assignment_result = await self.escalation_manager.assign_to_agent(
                escalation_request.escalation_id
            )
            
            return {
                "escalation_id": escalation_request.escalation_id,
                "priority": escalation_request.priority.value,
                "estimated_wait_time": escalation_request.estimated_wait_time,
                "assigned": assignment_result is not None,
                "agent_info": {
                    "name": assignment_result[1].name,
                    "specialties": [s.value for s in assignment_result[1].specialties]
                } if assignment_result else None
            }
            
        except Exception as e:
            logger.error(f"Escalation handling failed: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_comprehensive_response(
        self,
        conversation_response: Dict[str, Any],
        knowledge_results: List[Any],
        escalation_info: Optional[Dict[str, Any]],
        language: SupportedLanguage,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive response combining all AI capabilities"""        try:
            base_response = conversation_response.get("response", {})
            
            # Enhanced response with knowledge base results
            if knowledge_results:
                base_response["knowledge_articles"] = [
                    {
                        "title": result.article.title,
                        "snippet": result.snippet,
                        "relevance": result.relevance_score,
                        "article_id": result.article.id
                    }
                    for result in knowledge_results[:3]  # Top 3 results
                ]
            
            # Add escalation information
            if escalation_info:
                base_response["escalation"] = escalation_info
                if escalation_info.get("assigned"):
                    base_response["message"] += f"

I'm connecting you with {escalation_info['agent_info']['name']}, a human specialist who can provide more detailed assistance."
                else:
                    base_response["message"] += f"

I'm adding you to the queue for human assistance. Estimated wait time: {escalation_info.get('estimated_wait_time', 5)} minutes."
            
            # Translate response if needed
            if language != SupportedLanguage.ENGLISH:
                response_message = base_response.get("message", "")
                if response_message:
                    translation_request = TranslationRequest(
                        text=response_message,
                        source_language=SupportedLanguage.ENGLISH,
                        target_language=language,
                        domain="customer_support",
                        formality="neutral"
                    )
                    
                    translation_result = await self.multilanguage_manager.translate_text(translation_request)
                    base_response["message"] = translation_result.translated_text
                    base_response["translation_confidence"] = translation_result.confidence_score
            
            # Add system metadata
            base_response["system_info"] = {
                "ai_agent_version": "2.1.0",
                "response_language": language.value,
                "knowledge_base_searched": len(knowledge_results) > 0,
                "escalation_triggered": escalation_info is not None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return base_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return conversation_response.get("response", {"message": "I encountered an error processing your request."})
    
    async def _generate_error_response(
        self, 
        request_id: str, 
        user_id: str, 
        error_message: str, 
        language: SupportedLanguage
    ) -> Dict[str, Any]:
        """Generate user-friendly error response"""        error_response = {
            "request_id": request_id,
            "conversation_id": None,
            "response": {
                "message": "I apologize, but I'm experiencing technical difficulties. Let me connect you with a human agent who can assist you.",
                "error": True,
                "escalation_required": True,
                "suggestions": [
                    "Try rephrasing your question",
                    "Contact support via email",
                    "Try again in a few minutes"
                ]
            },
            "language": language.value,
            "system_status": "error",
            "error_details": error_message
        }
        
        # Translate error message if needed
        if language != SupportedLanguage.ENGLISH:
            try:
                translation_request = TranslationRequest(
                    text=error_response["response"]["message"],
                    source_language=SupportedLanguage.ENGLISH,
                    target_language=language
                )
                translation_result = await self.multilanguage_manager.translate_text(translation_request)
                error_response["response"]["message"] = translation_result.translated_text
            except:
                pass  # Keep English message if translation fails
        
        return error_response
    
    async def _record_system_metric(self, metric_name: str, value: float):
        """Record system performance metric"""        try:
            if self.analytics:
                metric = PerformanceMetric(
                    metric_type=MetricType.RESPONSE_TIME,  # Would map metric_name to appropriate type
                    value=value,
                    timestamp=datetime.now(timezone.utc),
                    metadata={"metric_name": metric_name}
                )
                await self.analytics.record_metric(metric)
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {str(e)}")
    
    async def _record_request_metrics(
        self, 
        processing_time: float, 
        conversation_response: Dict[str, Any], 
        user_id: str
    ):
        """Record comprehensive request metrics"""        try:
            self.total_response_time += processing_time
            
            if self.analytics:
                # Response time metric
                await self.analytics.record_metric(PerformanceMetric(
                    metric_type=MetricType.RESPONSE_TIME,
                    value=processing_time,
                    timestamp=datetime.now(timezone.utc),
                    user_id=user_id
                ))
                
                # Confidence metric
                confidence = conversation_response.get("confidence", 0.0)
                await self.analytics.record_metric(PerformanceMetric(
                    metric_type=MetricType.SUCCESS_RATE,
                    value=confidence,
                    timestamp=datetime.now(timezone.utc),
                    user_id=user_id
                ))
        except Exception as e:
            logger.error(f"Failed to record request metrics: {str(e)}")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            return f"{days}d {hours}h"

# Global support agent index instance
support_agent_index: Optional[SupportAgentIndex] = None

async def initialize_support_agent(
    config: SupportConfig,
    redis_client: aioredis.Redis,
    db_session: AsyncSession,
    initialize_defaults: bool = True
) -> SupportAgentIndex:
    """Initialize and return global support agent index"""    global support_agent_index
    
    if support_agent_index is None:
        support_agent_index = SupportAgentIndex(config)
        await support_agent_index.initialize(redis_client, db_session, initialize_defaults)
    
    return support_agent_index

async def get_support_agent() -> SupportAgentIndex:
    """Get the global support agent index"""    if support_agent_index is None:
        raise SupportError("Support Agent system not initialized")
    
    return support_agent_index

# Utility functions for external integration

async def quick_support_response(
    user_message: str,
    user_id: str,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Quick support response for simple integrations"""    try:
        agent = await get_support_agent()
        return await agent.process_support_request(
            user_id=user_id,
            message=user_message,
            language=language
        )
    except Exception as e:
        return {
            "error": str(e),
            "response": {
                "message": "I'm currently unavailable. Please contact support directly.",
                "error": True
            }
        }

async def batch_process_support_requests(
    requests: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Process multiple support requests in batch"""    try:
        agent = await get_support_agent()
        results = []
        
        for request in requests:
            result = await agent.process_support_request(
                user_id=request.get("user_id"),
                message=request.get("message"),
                language=request.get("language"),
                conversation_id=request.get("conversation_id"),
                metadata=request.get("metadata")
            )
            results.append(result)
        
        return results
    except Exception as e:
        return [{"error": str(e)} for _ in requests]

from .support_agent import (
    SupportAgent,
    SupportAgentManager,
    SupportCategory,
    Priority,
    SupportChannel,
    TicketStatus,
    SupportTicket,
    ConversationMessage
)

from ..base import AgentRequest, AgentResponse

# Version information
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

# Export all main classes and enums
__all__ = [
    # Core classes
    'SupportAgent',
    'SupportAgentManager',
    
    # Data structures
    'SupportTicket',
    'ConversationMessage',
    
    # Enums
    'SupportCategory',
    'Priority', 
    'SupportChannel',
    'TicketStatus',
    
    # Base classes
    'AgentRequest',
    'AgentResponse',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]

def get_support_agent(agent_id: str = None, config: dict = None) -> SupportAgent:
    """    Factory function to create a configured SupportAgent instance
    
    Args:
        agent_id: Unique identifier for the agent instance
        config: Configuration dictionary for the agent
        
    Returns:
        SupportAgent: Configured support agent instance
    """    if agent_id is None:
        import time
        agent_id = f"support_{int(time.time())}"
    
    return SupportAgent(agent_id=agent_id, config=config)

def get_default_config() -> dict:
    """    Get default configuration for SupportAgent
    
    Returns:
        dict: Default configuration dictionary
    """    return {
        "conversation_model_config": {
            "model_name": "microsoft/DialoGPT-medium",
            "max_length": 150,
            "temperature": 0.7,
            "do_sample": True
        },
        "knowledge_base_config": {
            "embedding_model": "all-MiniLM-L6-v2",
            "max_articles": 10000,
            "similarity_threshold": 0.7,
            "max_results": 5
        },
        "escalation_rules": {
            "sentiment_threshold": -0.7,
            "max_conversation_turns": 10,
            "keywords_requiring_human": [
                "speak to human", "human agent", "escalate",
                "manager", "supervisor", "complaint"
            ],
            "categories_auto_escalate": ["SECURITY_PRIVACY", "BILLING_PAYMENT"],
            "priority_auto_escalate": ["URGENT", "CRITICAL"]
        },
        "supported_channels": ["chat", "email", "phone", "video_call"],
        "supported_languages": ["en", "de", "fr", "es", "it", "pt"],
        "performance_settings": {
            "max_concurrent_conversations": 1000,
            "response_timeout": 30,
            "escalation_threshold": 0.3,
            "cache_ttl": 3600
        }
    }

# Quick access functions for common operations
async def create_support_ticket(
    user_id: str,
    message: str,
    channel: str = "chat",
    category: str = None,
    priority: str = "normal",
    agent_id: str = None
) -> dict:
    """    Quick function to create a support ticket
    
    Args:
        user_id: User identifier
        message: Support request message
        channel: Communication channel (chat, email, phone, etc.)
        category: Support category (optional, will be auto-detected)
        priority: Priority level (low, normal, high, urgent, critical)
        agent_id: Support agent identifier (optional)
        
    Returns:
        dict: Created ticket information and initial response
    """    agent = get_support_agent(agent_id)
    await agent.initialize()
    
    request = AgentRequest(
        action="handle_support_request",
        data={
            "user_id": user_id,
            "message": message,
            "channel": channel,
            "priority": priority
        }
    )
    
    response = await agent.process(request)
    return response.data

async def search_knowledge_base(
    query: str,
    max_results: int = 5,
    threshold: float = 0.7,
    agent_id: str = None
) -> dict:
    """    Quick function to search the knowledge base
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        threshold: Similarity threshold for results
        agent_id: Support agent identifier (optional)
        
    Returns:
        dict: Search results
    """    agent = get_support_agent(agent_id)
    await agent.initialize()
    
    request = AgentRequest(
        action="search_knowledge_base",
        data={
            "query": query,
            "max_results": max_results,
            "similarity_threshold": threshold
        }
    )
    
    response = await agent.process(request)
    return response.data

# Module initialization
def init_module():
    """Initialize the support agent module"""    import logging
    logging.getLogger(__name__).info(
        f"Support Agent module initialized - Version {__version__}"
    )

# Auto-initialize when imported
init_module()
