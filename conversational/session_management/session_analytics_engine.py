"""Session Analytics Engine - IA Influencer Agent

Enterprise-grade session analytics with behavioral tracking, conversation insights,
performance monitoring, and AI-powered session optimization for multi-format
content creators with advanced metrics and business intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

from pydantic import BaseModel, Field, validator
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import redis.asyncio as redis

from ...core.database import get_async_session
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, SessionState
from ...models.analytics import SessionAnalyticsModel, ConversationMetricsModel
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher
from ...ml.predictive_models import SessionPredictionModel

logger = get_logger(__name__)


class AnalyticsMetric(Enum):
    """Analytics metric types"""    SESSION_DURATION = "session_duration"
    MESSAGE_COUNT = "message_count"
    ENGAGEMENT_RATE = "engagement_rate"
    RESPONSE_TIME = "response_time"
    USER_SATISFACTION = "user_satisfaction"
    CONVERSION_RATE = "conversion_rate"
    PLATFORM_USAGE = "platform_usage"
    COLLABORATION_SUCCESS = "collaboration_success"
    CONTENT_PROTECTION_ALERTS = "content_protection_alerts"
    MONETIZATION_METRICS = "monetization_metrics"


class SessionPhase(Enum):
    """Session lifecycle phases"""    ONBOARDING = "onboarding"
    EXPLORATION = "exploration"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    RETENTION = "retention"
    CHURN = "churn"


class BehaviorPattern(Enum):
    """User behavior patterns"""    ACTIVE_CREATOR = "active_creator"
    PASSIVE_BROWSER = "passive_browser"
    COLLABORATION_SEEKER = "collaboration_seeker"
    PROTECTION_FOCUSED = "protection_focused"
    MONETIZATION_ORIENTED = "monetization_oriented"
    TECHNICAL_USER = "technical_user"
    CASUAL_USER = "casual_user"


@dataclass
class SessionMetrics:
    """Session-level metrics structure"""    session_id: str
    user_id: str
    platform: str
    duration_seconds: float
    message_count: int
    user_messages: int
    ai_responses: int
    avg_response_time: float
    engagement_score: float
    satisfaction_score: Optional[float] = None
    conversion_events: List[str] = field(default_factory=list)
    collaboration_attempts: int = 0
    protection_alerts: int = 0
    business_actions: int = 0
    errors_encountered: int = 0
    feature_usage: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationInsight:
    """Conversation-level insights"""    session_id: str
    primary_intent: str
    intent_confidence: float
    sentiment_trend: List[float]
    topics_discussed: List[str]
    entities_extracted: Dict[str, List[str]]
    conversation_flow: List[str]
    bottlenecks_detected: List[str]
    success_indicators: List[str]
    improvement_suggestions: List[str]
    business_value_score: float


class SessionBehaviorTracker:
    """Advanced session behavior tracking and analysis"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
        
        # Behavior tracking buffers
        self.user_behaviors: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.session_events: Dict[str, List[Dict]] = defaultdict(list)
    
    async def track_session_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Track individual session event"""        
        try:
            event = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": event_data
            }
            
            # Store in memory buffer
            self.session_events[session_id].append(event)
            
            # Store in cache for persistence
            events_key = f"session_events:{session_id}"
            current_events = await self.cache_manager.get(events_key) or []
            current_events.append(event)
            
            # Keep only last 1000 events per session
            if len(current_events) > 1000:
                current_events = current_events[-1000:]
            
            await self.cache_manager.set(events_key, current_events, ttl=86400)
            
            # Update real-time metrics
            await self._update_realtime_metrics(session_id, event)
            
            # Detect behavior patterns
            await self._detect_behavior_patterns(session_id, event)
            
        except Exception as e:
            self.logger.error(f"Event tracking error: {str(e)}")
    
    async def _update_realtime_metrics(self, session_id: str, event: Dict[str, Any]):
        """Update real-time session metrics"""        
        try:
            metrics_key = f"session_metrics:{session_id}"
            current_metrics = await self.cache_manager.get(metrics_key) or {}
            
            event_type = event["event_type"]
            
            # Update counters based on event type
            if event_type == "message_sent":
                current_metrics["message_count"] = current_metrics.get("message_count", 0) + 1
                if event["data"].get("sender") == "user":
                    current_metrics["user_messages"] = current_metrics.get("user_messages", 0) + 1
                elif event["data"].get("sender") == "ai":
                    current_metrics["ai_responses"] = current_metrics.get("ai_responses", 0) + 1
            
            elif event_type == "feature_used":
                feature = event["data"].get("feature")
                if feature:
                    feature_usage = current_metrics.get("feature_usage", {})
                    feature_usage[feature] = feature_usage.get(feature, 0) + 1
                    current_metrics["feature_usage"] = feature_usage
            
            elif event_type == "collaboration_attempt":
                current_metrics["collaboration_attempts"] = current_metrics.get("collaboration_attempts", 0) + 1
            
            elif event_type == "protection_alert":
                current_metrics["protection_alerts"] = current_metrics.get("protection_alerts", 0) + 1
            
            elif event_type == "business_action":
                current_metrics["business_actions"] = current_metrics.get("business_actions", 0) + 1
            
            elif event_type == "error_encountered":
                current_metrics["errors_encountered"] = current_metrics.get("errors_encountered", 0) + 1
            
            # Update timestamp
            current_metrics["last_updated"] = datetime.utcnow().isoformat()
            
            await self.cache_manager.set(metrics_key, current_metrics, ttl=86400)
            
        except Exception as e:
            self.logger.error(f"Real-time metrics update error: {str(e)}")
    
    async def _detect_behavior_patterns(self, session_id: str, event: Dict[str, Any]):
        """Detect user behavior patterns from events"""        
        try:
            # Get recent events for pattern detection
            events_key = f"session_events:{session_id}"
            recent_events = await self.cache_manager.get(events_key) or []
            
            if len(recent_events) < 10:
                return  # Need more events for pattern detection
            
            # Analyze event patterns
            event_types = [e["event_type"] for e in recent_events[-20:]]
            
            # Detect specific patterns
            patterns = []
            
            # Active creator pattern
            if event_types.count("content_upload") > 3 and event_types.count("protection_setup") > 1:
                patterns.append(BehaviorPattern.ACTIVE_CREATOR)
            
            # Collaboration seeker pattern
            if event_types.count("collaboration_attempt") > 2 and event_types.count("profile_view") > 5:
                patterns.append(BehaviorPattern.COLLABORATION_SEEKER)
            
            # Protection focused pattern
            if event_types.count("protection_alert") > 3 and event_types.count("security_settings") > 1:
                patterns.append(BehaviorPattern.PROTECTION_FOCUSED)
            
            # Monetization oriented pattern
            if event_types.count("revenue_check") > 3 and event_types.count("payment_setup") > 0:
                patterns.append(BehaviorPattern.MONETIZATION_ORIENTED)
            
            # Store detected patterns
            if patterns:
                patterns_key = f"behavior_patterns:{session_id}"
                await self.cache_manager.set(patterns_key, [p.value for p in patterns], ttl=86400)
                
                # Publish pattern detection event
                await self.event_publisher.publish_event(
                    "session.behavior_pattern_detected",
                    {
                        "session_id": session_id,
                        "patterns": [p.value for p in patterns],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Behavior pattern detection error: {str(e)}")
    
    async def calculate_engagement_score(self, session_id: str) -> float:
        """Calculate session engagement score"""        
        try:
            events = await self.cache_manager.get(f"session_events:{session_id}") or []
            metrics = await self.cache_manager.get(f"session_metrics:{session_id}") or {}
            
            if not events:
                return 0.0
            
            # Engagement factors
            message_count = metrics.get("message_count", 0)
            session_duration = self._calculate_session_duration(events)
            feature_usage_count = sum(metrics.get("feature_usage", {}).values())
            business_actions = metrics.get("business_actions", 0)
            collaboration_attempts = metrics.get("collaboration_attempts", 0)
            
            # Calculate engagement score (0-100)
            engagement_score = 0.0
            
            # Message frequency (30% weight)
            if session_duration > 0:
                messages_per_minute = message_count / (session_duration / 60)
                engagement_score += min(messages_per_minute * 5, 30)
            
            # Feature usage diversity (25% weight)
            unique_features = len(metrics.get("feature_usage", {}))
            engagement_score += min(unique_features * 5, 25)
            
            # Business action engagement (25% weight)
            engagement_score += min(business_actions * 10, 25)
            
            # Collaboration engagement (20% weight)
            engagement_score += min(collaboration_attempts * 10, 20)
            
            return min(engagement_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Engagement score calculation error: {str(e)}")
            return 0.0
    
    def _calculate_session_duration(self, events: List[Dict]) -> float:
        """Calculate session duration from events"""        
        if len(events) < 2:
            return 0.0
        
        try:
            start_time = datetime.fromisoformat(events[0]["timestamp"])
            end_time = datetime.fromisoformat(events[-1]["timestamp"])
            return (end_time - start_time).total_seconds()
        except Exception:
            return 0.0
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session behavior summary"""        
        try:
            events = await self.cache_manager.get(f"session_events:{session_id}") or []
            metrics = await self.cache_manager.get(f"session_metrics:{session_id}") or {}
            patterns = await self.cache_manager.get(f"behavior_patterns:{session_id}") or []
            
            engagement_score = await self.calculate_engagement_score(session_id)
            
            return {
                "session_id": session_id,
                "total_events": len(events),
                "duration_seconds": self._calculate_session_duration(events),
                "engagement_score": engagement_score,
                "behavior_patterns": patterns,
                "metrics": metrics,
                "event_timeline": events[-10:],  # Last 10 events
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Session summary generation error: {str(e)}")
            return {}


class ConversationInsightsGenerator:
    """AI-powered conversation insights and optimization"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.prediction_model = SessionPredictionModel()
        self.logger = get_logger(self.__class__.__name__)
    
    async def analyze_conversation(self, session_id: str) -> ConversationInsight:
        """Generate comprehensive conversation insights"""        
        try:
            # Get conversation history
            conversation_data = await self._get_conversation_data(session_id)
            
            if not conversation_data:
                return self._empty_insight(session_id)
            
            # Extract conversation features
            features = await self._extract_conversation_features(conversation_data)
            
            # Analyze conversation flow
            flow_analysis = await self._analyze_conversation_flow(conversation_data)
            
            # Detect bottlenecks and issues
            bottlenecks = await self._detect_conversation_bottlenecks(conversation_data)
            
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(features, bottlenecks)
            
            # Calculate business value score
            business_value = await self._calculate_business_value_score(conversation_data, features)
            
            insight = ConversationInsight(
                session_id=session_id,
                primary_intent=features.get("primary_intent", "unknown"),
                intent_confidence=features.get("intent_confidence", 0.0),
                sentiment_trend=features.get("sentiment_trend", []),
                topics_discussed=features.get("topics", []),
                entities_extracted=features.get("entities", {}),
                conversation_flow=flow_analysis.get("phases", []),
                bottlenecks_detected=bottlenecks,
                success_indicators=flow_analysis.get("success_indicators", []),
                improvement_suggestions=suggestions,
                business_value_score=business_value
            )
            
            # Cache insights
            insights_key = f"conversation_insights:{session_id}"
            await self.cache_manager.set(insights_key, insight.__dict__, ttl=86400)
            
            return insight
            
        except Exception as e:
            self.logger.error(f"Conversation analysis error: {str(e)}")
            return self._empty_insight(session_id)
    
    async def _get_conversation_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation data for analysis"""        
        try:
            # Get from session store
            session_data_key = f"session_data:{session_id}"
            session_data = await self.cache_manager.get(session_data_key)
            
            if session_data and "conversation_history" in session_data:
                return {
                    "messages": session_data["conversation_history"],
                    "context": session_data.get("context_stack", []),
                    "entities": session_data.get("entity_repository", {}),
                    "metadata": session_data.get("metadata", {})
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Conversation data retrieval error: {str(e)}")
            return None
    
    async def _extract_conversation_features(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from conversation for analysis"""        
        try:
            messages = conversation_data.get("messages", [])
            
            if not messages:
                return {}
            
            # Intent analysis
            intents = [msg.get("intent", "unknown") for msg in messages if msg.get("intent")]
            primary_intent = max(set(intents), key=intents.count) if intents else "unknown"
            intent_confidence = intents.count(primary_intent) / len(intents) if intents else 0.0
            
            # Sentiment analysis
            sentiments = [msg.get("sentiment", 0.0) for msg in messages if "sentiment" in msg]
            sentiment_trend = sentiments[-10:] if sentiments else []  # Last 10 sentiments
            
            # Topic extraction
            topics = []
            for msg in messages:
                msg_topics = msg.get("topics", [])
                topics.extend(msg_topics)
            unique_topics = list(set(topics))
            
            # Entity extraction
            entities = {}
            for msg in messages:
                msg_entities = msg.get("entities", {})
                for entity_type, entity_list in msg_entities.items():
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].extend(entity_list)
            
            # Clean up entities
            for entity_type in entities:
                entities[entity_type] = list(set(entities[entity_type]))
            
            return {
                "primary_intent": primary_intent,
                "intent_confidence": intent_confidence,
                "sentiment_trend": sentiment_trend,
                "topics": unique_topics[:10],  # Top 10 topics
                "entities": entities,
                "message_count": len(messages),
                "avg_message_length": statistics.mean([len(msg.get("content", "")) for msg in messages]) if messages else 0
            }
            
        except Exception as e:
            self.logger.error(f"Feature extraction error: {str(e)}")
            return {}
    
    async def _analyze_conversation_flow(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation flow and phases"""        
        try:
            messages = conversation_data.get("messages", [])
            
            if not messages:
                return {"phases": [], "success_indicators": []}
            
            # Identify conversation phases
            phases = []
            current_phase = None
            
            for msg in messages:
                intent = msg.get("intent", "unknown")
                
                # Map intents to phases
                if intent in ["greeting", "help", "introduction"]:
                    phase = SessionPhase.ONBOARDING
                elif intent in ["explore", "browse", "search"]:
                    phase = SessionPhase.EXPLORATION
                elif intent in ["collaborate", "create", "upload"]:
                    phase = SessionPhase.ENGAGEMENT
                elif intent in ["purchase", "subscribe", "monetize"]:
                    phase = SessionPhase.CONVERSION
                else:
                    phase = SessionPhase.ENGAGEMENT  # Default
                
                if phase != current_phase:
                    phases.append(phase.value)
                    current_phase = phase
            
            # Identify success indicators
            success_indicators = []
            
            # Check for completion of key actions
            user_messages = [msg for msg in messages if msg.get("sender") == "user"]
            
            if any("upload" in msg.get("content", "").lower() for msg in user_messages):
                success_indicators.append("content_uploaded")
            
            if any("collaborate" in msg.get("content", "").lower() for msg in user_messages):
                success_indicators.append("collaboration_initiated")
            
            if any("protect" in msg.get("content", "").lower() for msg in user_messages):
                success_indicators.append("protection_enabled")
            
            # Check sentiment progression
            sentiments = [msg.get("sentiment", 0.0) for msg in messages if "sentiment" in msg]
            if sentiments and len(sentiments) > 1:
                if sentiments[-1] > sentiments[0]:
                    success_indicators.append("positive_sentiment_trend")
            
            return {
                "phases": phases,
                "success_indicators": success_indicators,
                "total_phase_transitions": len(phases) - 1 if phases else 0
            }
            
        except Exception as e:
            self.logger.error(f"Conversation flow analysis error: {str(e)}")
            return {"phases": [], "success_indicators": []}
    
    async def _detect_conversation_bottlenecks(self, conversation_data: Dict[str, Any]) -> List[str]:
        """Detect conversation bottlenecks and issues"""        
        try:
            messages = conversation_data.get("messages", [])
            bottlenecks = []
            
            if not messages:
                return bottlenecks
            
            # Check for repeated questions
            user_messages = [msg.get("content", "") for msg in messages if msg.get("sender") == "user"]
            
            if len(user_messages) > len(set(user_messages)) * 1.5:
                bottlenecks.append("repeated_questions")
            
            # Check for error messages
            error_count = sum(1 for msg in messages if "error" in msg.get("content", "").lower())
            if error_count > 2:
                bottlenecks.append("frequent_errors")
            
            # Check for long response times
            response_times = []
            for i in range(1, len(messages)):
                prev_msg = messages[i-1]
                curr_msg = messages[i]
                
                if (prev_msg.get("sender") == "user" and 
                    curr_msg.get("sender") == "ai" and 
                    "timestamp" in prev_msg and "timestamp" in curr_msg):
                    
                    prev_time = datetime.fromisoformat(prev_msg["timestamp"])
                    curr_time = datetime.fromisoformat(curr_msg["timestamp"])
                    response_time = (curr_time - prev_time).total_seconds()
                    response_times.append(response_time)
            
            if response_times and statistics.mean(response_times) > 5.0:
                bottlenecks.append("slow_response_times")
            
            # Check for conversation stalling
            if len(messages) > 10:
                recent_messages = messages[-5:]
                unique_intents = set(msg.get("intent", "unknown") for msg in recent_messages)
                if len(unique_intents) == 1:
                    bottlenecks.append("conversation_stalling")
            
            # Check for sentiment decline
            sentiments = [msg.get("sentiment", 0.0) for msg in messages if "sentiment" in msg]
            if len(sentiments) >= 5:
                recent_avg = statistics.mean(sentiments[-3:])
                early_avg = statistics.mean(sentiments[:3])
                if recent_avg < early_avg - 0.3:
                    bottlenecks.append("sentiment_decline")
            
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Bottleneck detection error: {str(e)}")
            return []
    
    async def _generate_improvement_suggestions(
        self,
        features: Dict[str, Any],
        bottlenecks: List[str]
    ) -> List[str]:
        """Generate AI-powered improvement suggestions"""        
        suggestions = []
        
        try:
            # Address specific bottlenecks
            if "repeated_questions" in bottlenecks:
                suggestions.append("Provide clearer initial guidance and FAQ section")
            
            if "frequent_errors" in bottlenecks:
                suggestions.append("Improve error handling and user guidance")
            
            if "slow_response_times" in bottlenecks:
                suggestions.append("Optimize AI response generation for faster replies")
            
            if "conversation_stalling" in bottlenecks:
                suggestions.append("Introduce proactive conversation prompts and suggestions")
            
            if "sentiment_decline" in bottlenecks:
                suggestions.append("Implement sentiment monitoring and recovery strategies")
            
            # Feature-based suggestions
            primary_intent = features.get("primary_intent", "unknown")
            
            if primary_intent == "collaboration":
                suggestions.append("Enhance collaboration matching algorithms")
            elif primary_intent == "protection":
                suggestions.append("Streamline content protection setup process")
            elif primary_intent == "monetization":
                suggestions.append("Provide clearer monetization guidance and tools")
            
            # Engagement-based suggestions
            message_count = features.get("message_count", 0)
            if message_count < 5:
                suggestions.append("Encourage deeper engagement with interactive features")
            
            # Topic-based suggestions
            topics = features.get("topics", [])
            if "technical_issues" in topics:
                suggestions.append("Improve technical documentation and support")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Suggestion generation error: {str(e)}")
            return []
    
    async def _calculate_business_value_score(
        self,
        conversation_data: Dict[str, Any],
        features: Dict[str, Any]
    ) -> float:
        """Calculate business value score for conversation"""        
        try:
            score = 0.0
            messages = conversation_data.get("messages", [])
            
            # Content upload value (30 points)
            if any("upload" in msg.get("content", "").lower() for msg in messages):
                score += 30
            
            # Collaboration value (25 points)
            if any("collaborate" in msg.get("content", "").lower() for msg in messages):
                score += 25
            
            # Protection setup value (20 points)
            if any("protect" in msg.get("content", "").lower() for msg in messages):
                score += 20
            
            # Monetization engagement (15 points)
            if any("monetize" in msg.get("content", "").lower() for msg in messages):
                score += 15
            
            # Engagement depth (10 points)
            message_count = features.get("message_count", 0)
            if message_count > 10:
                score += 10
            elif message_count > 5:
                score += 5
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Business value calculation error: {str(e)}")
            return 0.0
    
    def _empty_insight(self, session_id: str) -> ConversationInsight:
        """Return empty insight object"""        
        return ConversationInsight(
            session_id=session_id,
            primary_intent="unknown",
            intent_confidence=0.0,
            sentiment_trend=[],
            topics_discussed=[],
            entities_extracted={},
            conversation_flow=[],
            bottlenecks_detected=[],
            success_indicators=[],
            improvement_suggestions=[],
            business_value_score=0.0
        )


class SessionPerformanceMonitor:
    """Real-time session performance monitoring"""    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 2000,
            "error_rate_percent": 5.0,
            "engagement_score_min": 30.0,
            "session_duration_min": 300,  # 5 minutes
            "message_rate_max": 10  # messages per minute
        }
    
    async def monitor_session_performance(self, session_id: str) -> Dict[str, Any]:
        """Monitor real-time session performance"""        
        try:
            # Get current session metrics
            metrics = await self.cache_manager.get(f"session_metrics:{session_id}") or {}
            events = await self.cache_manager.get(f"session_events:{session_id}") or []
            
            performance_report = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "alerts": [],
                "metrics": {},
                "recommendations": []
            }
            
            # Check response times
            response_times = await self._calculate_response_times(events)
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            performance_report["metrics"]["avg_response_time_ms"] = avg_response_time * 1000
            
            if avg_response_time * 1000 > self.thresholds["response_time_ms"]:
                performance_report["alerts"].append("High response times detected")
                performance_report["status"] = "warning"
            
            # Check error rate
            error_events = [e for e in events if e.get("event_type") == "error_encountered"]
            error_rate = (len(error_events) / len(events)) * 100 if events else 0
            
            performance_report["metrics"]["error_rate_percent"] = error_rate
            
            if error_rate > self.thresholds["error_rate_percent"]:
                performance_report["alerts"].append("High error rate detected")
                performance_report["status"] = "critical"
            
            # Check engagement
            engagement_score = await self._get_current_engagement_score(session_id)
            performance_report["metrics"]["engagement_score"] = engagement_score
            
            if engagement_score < self.thresholds["engagement_score_min"]:
                performance_report["alerts"].append("Low engagement detected")
                performance_report["recommendations"].append("Introduce interactive elements")
            
            # Check session duration
            session_duration = await self._get_session_duration(events)
            performance_report["metrics"]["session_duration_seconds"] = session_duration
            
            if session_duration < self.thresholds["session_duration_min"]:
                performance_report["recommendations"].append("Encourage longer engagement")
            
            # Check message rate
            message_rate = await self._calculate_message_rate(events)
            performance_report["metrics"]["message_rate_per_minute"] = message_rate
            
            if message_rate > self.thresholds["message_rate_max"]:
                performance_report["alerts"].append("Unusually high message rate")
                performance_report["recommendations"].append("Consider rate limiting")
            
            # Store performance report
            report_key = f"performance_report:{session_id}"
            await self.cache_manager.set(report_key, performance_report, ttl=3600)
            
            return performance_report
            
        except Exception as e:
            self.logger.error(f"Performance monitoring error: {str(e)}")
            return {"session_id": session_id, "status": "error", "error": str(e)}
    
    async def _calculate_response_times(self, events: List[Dict]) -> List[float]:
        """Calculate AI response times from events"""        
        response_times = []
        
        try:
            user_message_time = None
            
            for event in events:
                if event.get("event_type") == "message_sent":
                    sender = event.get("data", {}).get("sender")
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    
                    if sender == "user":
                        user_message_time = timestamp
                    elif sender == "ai" and user_message_time:
                        response_time = (timestamp - user_message_time).total_seconds()
                        response_times.append(response_time)
                        user_message_time = None
            
            return response_times
            
        except Exception as e:
            self.logger.error(f"Response time calculation error: {str(e)}")
            return []
    
    async def _get_current_engagement_score(self, session_id: str) -> float:
        """Get current engagement score"""        
        try:
            # This would typically call the behavior tracker
            behavior_tracker = SessionBehaviorTracker()
            return await behavior_tracker.calculate_engagement_score(session_id)
        except Exception:
            return 0.0
    
    async def _get_session_duration(self, events: List[Dict]) -> float:
        """Calculate current session duration"""        
        if not events:
            return 0.0
        
        try:
            start_time = datetime.fromisoformat(events[0]["timestamp"])
            end_time = datetime.fromisoformat(events[-1]["timestamp"])
            return (end_time - start_time).total_seconds()
        except Exception:
            return 0.0
    
    async def _calculate_message_rate(self, events: List[Dict]) -> float:
        """Calculate messages per minute"""        
        try:
            message_events = [e for e in events if e.get("event_type") == "message_sent"]
            
            if len(message_events) < 2:
                return 0.0
            
            duration_minutes = self._get_session_duration(events) / 60
            
            if duration_minutes == 0:
                return 0.0
            
            return len(message_events) / duration_minutes
            
        except Exception:
            return 0.0


class SessionAnalyticsEngine:
    """Main session analytics orchestrator"""    
    def __init__(self):
        self.behavior_tracker = SessionBehaviorTracker()
        self.insights_generator = ConversationInsightsGenerator()
        self.performance_monitor = SessionPerformanceMonitor()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        self.logger = get_logger(self.__class__.__name__)
    
    async def track_session_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Track session event and trigger analytics"""        
        await self.behavior_tracker.track_session_event(session_id, event_type, event_data)
        
        # Trigger real-time monitoring for critical events
        if event_type in ["error_encountered", "slow_response", "user_frustration"]:
            await self.performance_monitor.monitor_session_performance(session_id)
    
    async def generate_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive session analytics"""        
        try:
            # Get behavior summary
            behavior_summary = await self.behavior_tracker.get_session_summary(session_id)
            
            # Generate conversation insights
            conversation_insights = await self.insights_generator.analyze_conversation(session_id)
            
            # Get performance metrics
            performance_report = await self.performance_monitor.monitor_session_performance(session_id)
            
            # Combine all analytics
            analytics_report = {
                "session_id": session_id,
                "generated_at": datetime.utcnow().isoformat(),
                "behavior_analysis": behavior_summary,
                "conversation_insights": conversation_insights.__dict__,
                "performance_metrics": performance_report,
                "summary": {
                    "overall_score": await self._calculate_overall_score(
                        behavior_summary,
                        conversation_insights,
                        performance_report
                    ),
                    "key_achievements": await self._identify_key_achievements(conversation_insights),
                    "improvement_areas": await self._identify_improvement_areas(
                        conversation_insights,
                        performance_report
                    ),
                    "business_impact": conversation_insights.business_value_score
                }
            }
            
            # Cache analytics report
            analytics_key = f"session_analytics:{session_id}"
            await self.cache_manager.set(analytics_key, analytics_report, ttl=86400)
            
            # Update metrics
            await self.metrics_collector.increment("session_analytics.generated")
            
            return analytics_report
            
        except Exception as e:
            self.logger.error(f"Session analytics generation error: {str(e)}")
            return {"session_id": session_id, "error": str(e)}
    
    async def _calculate_overall_score(
        self,
        behavior_summary: Dict[str, Any],
        conversation_insights: ConversationInsight,
        performance_report: Dict[str, Any]
    ) -> float:
        """Calculate overall session score"""        
        try:
            # Weighted scoring
            engagement_score = behavior_summary.get("engagement_score", 0) * 0.4
            business_value = conversation_insights.business_value_score * 0.3
            
            # Performance score (inverted - lower is better for some metrics)
            performance_metrics = performance_report.get("metrics", {})
            performance_score = 100  # Start with perfect score
            
            # Deduct for poor performance
            if performance_metrics.get("error_rate_percent", 0) > 5:
                performance_score -= 20
            
            if performance_metrics.get("avg_response_time_ms", 0) > 2000:
                performance_score -= 15
            
            performance_score = max(performance_score, 0) * 0.3
            
            overall_score = engagement_score + business_value + performance_score
            
            return min(overall_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"Overall score calculation error: {str(e)}")
            return 0.0
    
    async def _identify_key_achievements(self, insights: ConversationInsight) -> List[str]:
        """Identify key session achievements"""        
        achievements = []
        
        if "content_uploaded" in insights.success_indicators:
            achievements.append("Successfully uploaded content")
        
        if "collaboration_initiated" in insights.success_indicators:
            achievements.append("Initiated collaboration")
        
        if "protection_enabled" in insights.success_indicators:
            achievements.append("Enabled content protection")
        
        if "positive_sentiment_trend" in insights.success_indicators:
            achievements.append("Maintained positive user experience")
        
        if insights.business_value_score > 70:
            achievements.append("High business value conversation")
        
        if insights.intent_confidence > 0.8:
            achievements.append("Clear intent understanding")
        
        return achievements
    
    async def _identify_improvement_areas(
        self,
        insights: ConversationInsight,
        performance_report: Dict[str, Any]
    ) -> List[str]:
        """Identify areas for improvement"""        
        improvements = []
        
        # From conversation insights
        improvements.extend(insights.improvement_suggestions)
        
        # From performance issues
        if "High response times detected" in performance_report.get("alerts", []):
            improvements.append("Optimize response generation speed")
        
        if "High error rate detected" in performance_report.get("alerts", []):
            improvements.append("Improve error handling and recovery")
        
        if "Low engagement detected" in performance_report.get("alerts", []):
            improvements.append("Enhance user engagement strategies")
        
        # From bottlenecks
        if insights.bottlenecks_detected:
            improvements.append(f"Address conversation bottlenecks: {', '.join(insights.bottlenecks_detected)}")
        
        return list(set(improvements))  # Remove duplicates
    
    async def get_analytics_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get analytics dashboard for user"""        
        try:
            # Get user's recent sessions
            user_sessions = await self._get_user_recent_sessions(user_id)
            
            if not user_sessions:
                return {"user_id": user_id, "message": "No recent sessions found"}
            
            # Aggregate analytics
            dashboard = {
                "user_id": user_id,
                "period": "last_30_days",
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_sessions": len(user_sessions),
                    "total_duration": 0,
                    "avg_engagement": 0,
                    "avg_business_value": 0
                },
                "trends": {
                    "engagement_over_time": [],
                    "session_duration_trend": [],
                    "popular_features": {},
                    "behavior_patterns": {}
                },
                "insights": {
                    "top_achievements": [],
                    "common_improvements": [],
                    "platform_usage": {}
                }
            }
            
            # Process each session
            total_engagement = 0
            total_business_value = 0
            total_duration = 0
            
            for session_id in user_sessions:
                analytics = await self.cache_manager.get(f"session_analytics:{session_id}")
                
                if analytics:
                    behavior = analytics.get("behavior_analysis", {})
                    insights = analytics.get("conversation_insights", {})
                    
                    total_engagement += behavior.get("engagement_score", 0)
                    total_business_value += insights.get("business_value_score", 0)
                    total_duration += behavior.get("duration_seconds", 0)
            
            # Calculate averages
            session_count = len(user_sessions)
            dashboard["summary"]["total_duration"] = total_duration
            dashboard["summary"]["avg_engagement"] = total_engagement / session_count if session_count > 0 else 0
            dashboard["summary"]["avg_business_value"] = total_business_value / session_count if session_count > 0 else 0
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Analytics dashboard generation error: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _get_user_recent_sessions(self, user_id: str, days: int = 30) -> List[str]:
        """Get user's recent session IDs"""        
        try:
            # This would typically query the database
            # For now, check cache for user sessions
            user_sessions_key = f"user_sessions:{user_id}"
            sessions = await self.cache_manager.get(user_sessions_key) or []
            
            return sessions[-50:]  # Return last 50 sessions
            
        except Exception as e:
            self.logger.error(f"User sessions retrieval error: {str(e)}")
            return []
