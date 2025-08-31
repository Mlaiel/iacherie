"""Advanced Priority Handler - Intelligent Priority-Based Notification Management

This module provides sophisticated priority-based notification management for the IA Influencer Agent platform,
handling intelligent priority classification, urgency detection, and priority-based delivery optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
from collections import defaultdict, deque
import heapq

from ...models.notification_models import (
    NotificationModel, NotificationPriority, NotificationChannel,
    PriorityRule, UrgencyScore
)
from ...ai.priority.priority_classifier import PriorityClassificationEngine
from ...business.priority_business import PriorityBusinessLogic
from ...monitoring.priority_monitoring import PriorityMonitoringService


class UrgencyLevel(Enum):
    """Extended urgency levels for fine-grained priority control"""    CRITICAL = "critical"          # Immediate action required (security, legal)
    URGENT = "urgent"              # Action required within minutes
    HIGH = "high"                  # Action required within hours
    MEDIUM = "medium"              # Action required within day
    LOW = "low"                    # Action required within week
    INFORMATIONAL = "informational" # No specific time requirement


class PriorityContext(Enum):
    """Context categories that influence priority scoring"""    CONTENT_PROTECTION = "content_protection"
    SECURITY_INCIDENT = "security_incident"
    COLLABORATION_OPPORTUNITY = "collaboration_opportunity"
    MONETIZATION_ALERT = "monetization_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    USER_ENGAGEMENT = "user_engagement"
    PLATFORM_UPDATE = "platform_update"
    BUSINESS_CRITICAL = "business_critical"


@dataclass
class PriorityFactors:
    """Comprehensive factors that influence notification priority"""    urgency_score: float = 0.0
    business_impact: float = 0.0
    user_preference_weight: float = 0.0
    time_sensitivity: float = 0.0
    content_type_weight: float = 0.0
    collaboration_value: float = 0.0
    security_relevance: float = 0.0
    revenue_impact: float = 0.0
    engagement_potential: float = 0.0
    ai_confidence: float = 0.0


@dataclass
class PriorityDecision:
    """Priority decision with detailed reasoning"""    final_priority: NotificationPriority
    urgency_level: UrgencyLevel
    priority_score: float
    factors: PriorityFactors
    reasoning: List[str]
    confidence: float
    processing_hints: Dict[str, Any]
    escalation_rules: Dict[str, Any]
    delivery_constraints: Dict[str, Any]


@dataclass
class PriorityQueue:
    """Advanced priority queue with time-aware scheduling"""    queue_id: str
    priority_level: NotificationPriority
    notifications: List[Tuple[float, NotificationModel]]  # (priority_score, notification)
    max_size: int = 1000
    processing_rate: float = 10.0  # notifications per second
    last_processed: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        # Ensure heap property is maintained
        heapq.heapify(self.notifications)
        
    def add_notification(self, priority_score: float, notification: NotificationModel):
        """Add notification to priority queue"""        if len(self.notifications) >= self.max_size:
            # Remove lowest priority notification if queue is full
            heapq.heappushpop(self.notifications, (priority_score, notification))
        else:
            heapq.heappush(self.notifications, (priority_score, notification))
            
    def get_next_notification(self) -> Optional[NotificationModel]:
        """Get next highest priority notification"""        if self.notifications:
            priority_score, notification = heapq.heappop(self.notifications)
            self.last_processed = datetime.utcnow()
            return notification
        return None
        
    def peek_next(self) -> Optional[Tuple[float, NotificationModel]]:
        """Peek at next notification without removing it"""        return self.notifications[0] if self.notifications else None
        
    def size(self) -> int:
        """Get current queue size"""        return len(self.notifications)
        
    def is_empty(self) -> bool:
        """Check if queue is empty"""        return len(self.notifications) == 0


class UrgencyClassifier:
    """    Advanced AI-powered urgency classification system
    
    Uses machine learning to classify notification urgency based on multiple factors
    including content analysis, user context, business rules, and historical patterns
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # AI classification engine
        self.classification_engine = PriorityClassificationEngine(
            config.get('ai_classification', {})
        )
        
        # Business logic integration
        self.business_logic = PriorityBusinessLogic(
            config.get('business_rules', {})
        )
        
        # Historical analysis
        self.historical_patterns = self._initialize_historical_analyzer()
        
        # Real-time context analyzer
        self.context_analyzer = self._initialize_context_analyzer()
        
        # Performance tracking
        self.classification_metrics = {
            'total_classifications': 0,
            'accuracy_score': 0.95,
            'processing_time_avg': 0.05,
            'model_confidence_avg': 0.88
        }
        
    def _initialize_historical_analyzer(self):
        """Initialize historical pattern analysis"""        from ...ai.analytics.historical_analyzer import HistoricalPatternAnalyzer
        return HistoricalPatternAnalyzer(self.config.get('historical_analysis', {}))
        
    def _initialize_context_analyzer(self):
        """Initialize real-time context analysis"""        from ...ai.context.context_analyzer import RealTimeContextAnalyzer
        return RealTimeContextAnalyzer(self.config.get('context_analysis', {}))
        
    async def classify_urgency(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[UrgencyLevel, float]:
        """        Classify notification urgency using advanced AI analysis
        
        Args:
            notification: Notification to classify
            context: Additional context information
            
        Returns:
            Tuple of (urgency_level, confidence_score)
        """        try:
            start_time = datetime.utcnow()
            
            # Extract features for classification
            features = await self._extract_urgency_features(notification, context)
            
            # Apply AI classification
            ai_prediction = await self.classification_engine.predict_urgency(features)
            
            # Apply business rule validation
            business_validation = await self.business_logic.validate_urgency(
                notification, ai_prediction
            )
            
            # Historical pattern analysis
            historical_insights = await self.historical_patterns.analyze_similar_patterns(
                notification.type, features
            )
            
            # Real-time context adjustment
            context_adjustment = await self.context_analyzer.adjust_urgency(
                ai_prediction, context or {}
            )
            
            # Combine predictions with weighted ensemble
            final_urgency, confidence = await self._ensemble_predictions(
                ai_prediction, business_validation, historical_insights, context_adjustment
            )
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_classification_metrics(processing_time, confidence)
            
            self.logger.debug(
                f"Urgency classified: {final_urgency.value} "
                f"(confidence: {confidence:.3f}, time: {processing_time:.3f}s)"
            )
            
            return final_urgency, confidence
            
        except Exception as e:
            self.logger.error(f"Urgency classification failed: {str(e)}")
            # Return safe default
            return UrgencyLevel.MEDIUM, 0.5
            
    async def _extract_urgency_features(
        self, 
        notification: NotificationModel, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract comprehensive features for urgency classification"""        try:
            features = {
                # Content features
                'notification_type': notification.type,
                'content_length': len(str(notification.content)),
                'has_attachments': bool(notification.content.get('attachments')),
                'contains_keywords': await self._extract_urgency_keywords(notification.content),
                
                # User features
                'user_id': notification.user_id,
                'user_tier': context.get('user_tier', 'standard') if context else 'standard',
                'user_engagement_score': context.get('engagement_score', 0.5) if context else 0.5,
                
                # Temporal features
                'hour_of_day': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday(),
                'is_weekend': datetime.utcnow().weekday() >= 5,
                
                # Business context features
                'business_context': context.get('business_context', {}) if context else {},
                'revenue_impact': context.get('revenue_impact', 0.0) if context else 0.0,
                'collaboration_value': context.get('collaboration_value', 0.0) if context else 0.0,
                
                # System features
                'system_load': context.get('system_load', 0.5) if context else 0.5,
                'queue_depth': context.get('queue_depth', 0) if context else 0
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            return {}
            
    async def _extract_urgency_keywords(self, content: Dict[str, Any]) -> List[str]:
        """Extract urgency-indicating keywords from content"""        try:
            urgency_keywords = [
                'urgent', 'critical', 'immediate', 'emergency', 'asap',
                'security', 'breach', 'violation', 'copyright', 'infringement',
                'deadline', 'expires', 'limited', 'opportunity', 'collaboration'
            ]
            
            content_text = ' '.join(str(v).lower() for v in content.values() if isinstance(v, str))
            found_keywords = [keyword for keyword in urgency_keywords if keyword in content_text]
            
            return found_keywords
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {str(e)}")
            return []
            
    async def _ensemble_predictions(
        self,
        ai_prediction: Tuple[UrgencyLevel, float],
        business_validation: Tuple[UrgencyLevel, float],
        historical_insights: Tuple[UrgencyLevel, float],
        context_adjustment: Tuple[UrgencyLevel, float]
    ) -> Tuple[UrgencyLevel, float]:
        """Combine multiple predictions using weighted ensemble"""        try:
            # Define weights for different prediction sources
            weights = {
                'ai': 0.4,
                'business': 0.3,
                'historical': 0.2,
                'context': 0.1
            }
            
            # Convert urgency levels to numerical scores
            urgency_to_score = {
                UrgencyLevel.CRITICAL: 1.0,
                UrgencyLevel.URGENT: 0.8,
                UrgencyLevel.HIGH: 0.6,
                UrgencyLevel.MEDIUM: 0.4,
                UrgencyLevel.LOW: 0.2,
                UrgencyLevel.INFORMATIONAL: 0.0
            }
            
            score_to_urgency = {v: k for k, v in urgency_to_score.items()}
            
            # Calculate weighted score
            weighted_score = (
                weights['ai'] * urgency_to_score[ai_prediction[0]] +
                weights['business'] * urgency_to_score[business_validation[0]] +
                weights['historical'] * urgency_to_score[historical_insights[0]] +
                weights['context'] * urgency_to_score[context_adjustment[0]]
            )
            
            # Calculate weighted confidence
            weighted_confidence = (
                weights['ai'] * ai_prediction[1] +
                weights['business'] * business_validation[1] +
                weights['historical'] * historical_insights[1] +
                weights['context'] * context_adjustment[1]
            )
            
            # Convert back to urgency level
            final_urgency = min(score_to_urgency.keys(), key=lambda x: abs(x - weighted_score))
            final_urgency_level = score_to_urgency[final_urgency]
            
            return final_urgency_level, min(1.0, max(0.0, weighted_confidence))
            
        except Exception as e:
            self.logger.error(f"Ensemble prediction failed: {str(e)}")
            return UrgencyLevel.MEDIUM, 0.5
            
    async def _update_classification_metrics(self, processing_time: float, confidence: float):
        """Update classification performance metrics"""        try:
            self.classification_metrics['total_classifications'] += 1
            
            # Update average processing time
            current_avg = self.classification_metrics['processing_time_avg']
            total = self.classification_metrics['total_classifications']
            new_avg = ((current_avg * (total - 1)) + processing_time) / total
            self.classification_metrics['processing_time_avg'] = new_avg
            
            # Update average confidence
            current_confidence_avg = self.classification_metrics['model_confidence_avg']
            new_confidence_avg = ((current_confidence_avg * (total - 1)) + confidence) / total
            self.classification_metrics['model_confidence_avg'] = new_confidence_avg
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {str(e)}")


class PriorityHandler:
    """    Advanced priority-based notification management system
    
    Features:
    - AI-driven priority classification and urgency detection
    - Multi-queue priority management with intelligent scheduling
    - Dynamic priority adjustment based on real-time conditions
    - Performance optimization and queue balancing
    - Business rule integration and compliance
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.urgency_classifier = UrgencyClassifier(config.get('urgency_classifier', {}))
        self.business_logic = PriorityBusinessLogic(config.get('business_logic', {}))
        self.monitoring = PriorityMonitoringService(config.get('monitoring', {}))
        
        # Priority queues for different levels
        self.priority_queues = self._initialize_priority_queues()
        
        # Processing control
        self.processing_scheduler = self._initialize_processing_scheduler()
        self.queue_balancer = self._initialize_queue_balancer()
        
        # Priority rules and policies
        self.priority_rules = self._load_priority_rules()
        self.escalation_policies = self._load_escalation_policies()
        
        # Performance metrics
        self.performance_metrics = {
            'total_processed': 0,
            'processing_rates': {},
            'queue_sizes': {},
            'average_wait_time': 0.0,
            'priority_accuracy': 0.95
        }
        
        # Processing tasks
        self.processing_tasks = []
        self.is_running = False
        
    def _initialize_priority_queues(self) -> Dict[NotificationPriority, PriorityQueue]:
        """Initialize priority queues for different levels"""        queues = {}
        
        for priority in NotificationPriority:
            queue_config = self.config.get('queues', {}).get(priority.value, {})
            
            queues[priority] = PriorityQueue(
                queue_id=f"queue_{priority.value}",
                priority_level=priority,
                max_size=queue_config.get('max_size', 1000),
                processing_rate=queue_config.get('processing_rate', 10.0)
            )
            
        return queues
        
    def _initialize_processing_scheduler(self):
        """Initialize intelligent processing scheduler"""        from ...infrastructure.priority_scheduler import PriorityProcessingScheduler
        return PriorityProcessingScheduler(self.config.get('scheduler', {}))
        
    def _initialize_queue_balancer(self):
        """Initialize queue balancing system"""        from ...infrastructure.queue_balancer import QueueBalancer
        return QueueBalancer(self.config.get('queue_balancer', {}))
        
    def _load_priority_rules(self) -> List[PriorityRule]:
        """Load priority rules from configuration"""        try:
            rules_config = self.config.get('priority_rules', [])
            rules = []
            
            for rule_config in rules_config:
                rule = PriorityRule(
                    rule_id=rule_config['id'],
                    conditions=rule_config['conditions'],
                    priority_adjustment=rule_config['priority_adjustment'],
                    weight=rule_config.get('weight', 1.0)
                )
                rules.append(rule)
                
            return rules
            
        except Exception as e:
            self.logger.error(f"Failed to load priority rules: {str(e)}")
            return []
            
    def _load_escalation_policies(self) -> Dict[str, Any]:
        """Load escalation policies configuration"""        return self.config.get('escalation_policies', {
            'max_wait_time_urgent': 300,  # 5 minutes
            'max_wait_time_high': 900,    # 15 minutes
            'max_wait_time_medium': 3600, # 1 hour
            'escalation_channels': ['email', 'sms', 'slack']
        })
        
    async def start_processing(self):
        """Start priority-based notification processing"""        try:
            self.logger.info("Starting PriorityHandler processing")
            self.is_running = True
            
            # Start processing tasks for each priority level
            for priority in NotificationPriority:
                task = asyncio.create_task(
                    self._process_priority_queue(priority)
                )
                self.processing_tasks.append(task)
                
            # Start queue balancing task
            balance_task = asyncio.create_task(self._balance_queues())
            self.processing_tasks.append(balance_task)
            
            # Start escalation monitoring
            escalation_task = asyncio.create_task(self._monitor_escalations())
            self.processing_tasks.append(escalation_task)
            
            # Start performance monitoring
            monitoring_task = asyncio.create_task(self._monitor_performance())
            self.processing_tasks.append(monitoring_task)
            
            self.logger.info("PriorityHandler processing started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start priority processing: {str(e)}")
            
    async def stop_processing(self):
        """Stop priority processing gracefully"""        try:
            self.logger.info("Stopping PriorityHandler processing")
            self.is_running = False
            
            # Cancel all processing tasks
            for task in self.processing_tasks:
                task.cancel()
                
            # Process remaining notifications
            await self._process_remaining_notifications()
            
            self.logger.info("PriorityHandler processing stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping priority processing: {str(e)}")
            
    async def add_notification(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]] = None
    ) -> PriorityDecision:
        """        Add notification to appropriate priority queue with intelligent classification
        
        Args:
            notification: Notification to add
            context: Additional context for priority determination
            
        Returns:
            Priority decision with detailed reasoning
        """        try:
            # Classify urgency using AI
            urgency_level, confidence = await self.urgency_classifier.classify_urgency(
                notification, context
            )
            
            # Calculate comprehensive priority factors
            factors = await self._calculate_priority_factors(
                notification, urgency_level, context
            )
            
            # Apply business rules
            business_adjusted_priority = await self.business_logic.apply_priority_rules(
                notification, factors, self.priority_rules
            )
            
            # Create priority decision
            decision = PriorityDecision(
                final_priority=business_adjusted_priority,
                urgency_level=urgency_level,
                priority_score=await self._calculate_final_priority_score(factors),
                factors=factors,
                reasoning=await self._generate_priority_reasoning(factors, urgency_level),
                confidence=confidence,
                processing_hints=await self._generate_processing_hints(urgency_level),
                escalation_rules=await self._generate_escalation_rules(urgency_level),
                delivery_constraints=await self._generate_delivery_constraints(urgency_level)
            )
            
            # Add to appropriate priority queue
            priority_queue = self.priority_queues[decision.final_priority]
            priority_queue.add_notification(decision.priority_score, notification)
            
            # Update metrics
            await self._update_queue_metrics()
            
            # Log priority decision
            self.logger.debug(
                f"Notification prioritized: {notification.id} -> "
                f"{decision.final_priority.value} (score: {decision.priority_score:.3f})"
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Failed to add notification to priority queue: {str(e)}")
            # Add to medium priority as fallback
            fallback_queue = self.priority_queues[NotificationPriority.MEDIUM]
            fallback_queue.add_notification(0.5, notification)
            
            return PriorityDecision(
                final_priority=NotificationPriority.MEDIUM,
                urgency_level=UrgencyLevel.MEDIUM,
                priority_score=0.5,
                factors=PriorityFactors(),
                reasoning=["Fallback priority due to processing error"],
                confidence=0.0,
                processing_hints={},
                escalation_rules={},
                delivery_constraints={}
            )
            
    async def get_next_notification(self) -> Optional[Tuple[NotificationModel, PriorityDecision]]:
        """Get next highest priority notification for processing"""        try:
            # Check queues in priority order
            for priority in [
                NotificationPriority.URGENT,
                NotificationPriority.HIGH,
                NotificationPriority.MEDIUM,
                NotificationPriority.LOW
            ]:
                queue = self.priority_queues[priority]
                notification = queue.get_next_notification()
                
                if notification:
                    # Reconstruct priority decision (simplified)
                    decision = PriorityDecision(
                        final_priority=priority,
                        urgency_level=self._priority_to_urgency(priority),
                        priority_score=0.8,  # Placeholder
                        factors=PriorityFactors(),
                        reasoning=[],
                        confidence=0.8,
                        processing_hints={},
                        escalation_rules={},
                        delivery_constraints={}
                    )
                    
                    return notification, decision
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get next notification: {str(e)}")
            return None
            
    def _priority_to_urgency(self, priority: NotificationPriority) -> UrgencyLevel:
        """Convert priority level to urgency level"""        mapping = {
            NotificationPriority.URGENT: UrgencyLevel.URGENT,
            NotificationPriority.HIGH: UrgencyLevel.HIGH,
            NotificationPriority.MEDIUM: UrgencyLevel.MEDIUM,
            NotificationPriority.LOW: UrgencyLevel.LOW
        }
        return mapping.get(priority, UrgencyLevel.MEDIUM)
        
    async def _calculate_priority_factors(
        self,
        notification: NotificationModel,
        urgency_level: UrgencyLevel,
        context: Optional[Dict[str, Any]]
    ) -> PriorityFactors:
        """Calculate comprehensive priority factors"""        try:
            # Base urgency score
            urgency_score = self._urgency_level_to_score(urgency_level)
            
            # Business impact assessment
            business_impact = await self._assess_business_impact(notification, context)
            
            # User preference weight
            user_preference_weight = await self._get_user_preference_weight(
                notification.user_id, context
            )
            
            # Time sensitivity
            time_sensitivity = await self._calculate_time_sensitivity(notification, context)
            
            # Content type weight
            content_type_weight = self._get_content_type_weight(notification.type)
            
            # Collaboration value
            collaboration_value = await self._assess_collaboration_value(notification, context)
            
            # Security relevance
            security_relevance = await self._assess_security_relevance(notification, context)
            
            # Revenue impact
            revenue_impact = await self._assess_revenue_impact(notification, context)
            
            # Engagement potential
            engagement_potential = await self._assess_engagement_potential(notification, context)
            
            return PriorityFactors(
                urgency_score=urgency_score,
                business_impact=business_impact,
                user_preference_weight=user_preference_weight,
                time_sensitivity=time_sensitivity,
                content_type_weight=content_type_weight,
                collaboration_value=collaboration_value,
                security_relevance=security_relevance,
                revenue_impact=revenue_impact,
                engagement_potential=engagement_potential,
                ai_confidence=0.8  # Placeholder
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate priority factors: {str(e)}")
            return PriorityFactors()
            
    def _urgency_level_to_score(self, urgency_level: UrgencyLevel) -> float:
        """Convert urgency level to numerical score"""        mapping = {
            UrgencyLevel.CRITICAL: 1.0,
            UrgencyLevel.URGENT: 0.8,
            UrgencyLevel.HIGH: 0.6,
            UrgencyLevel.MEDIUM: 0.4,
            UrgencyLevel.LOW: 0.2,
            UrgencyLevel.INFORMATIONAL: 0.1
        }
        return mapping.get(urgency_level, 0.4)
        
    async def _assess_business_impact(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess business impact of notification"""        try:
            impact_score = 0.5  # Default
            
            # Content protection impact
            if 'protection' in notification.type:
                impact_score += 0.3
                
            # Revenue-related impact
            if context and context.get('revenue_impact', 0) > 0:
                impact_score += min(0.4, context['revenue_impact'] / 1000)
                
            # User tier impact
            if context and context.get('user_tier') == 'premium':
                impact_score += 0.2
                
            return min(1.0, impact_score)
            
        except Exception as e:
            self.logger.error(f"Business impact assessment failed: {str(e)}")
            return 0.5
            
    async def _get_user_preference_weight(self, user_id: str, context: Optional[Dict[str, Any]]) -> float:
        """Get user preference weight for notification priority"""        try:
            # Default weight
            weight = 0.5
            
            # Premium users get higher weight
            if context and context.get('user_tier') == 'premium':
                weight += 0.3
                
            # Active users get higher weight
            if context and context.get('user_activity_score', 0) > 0.7:
                weight += 0.2
                
            return min(1.0, weight)
            
        except Exception as e:
            self.logger.error(f"User preference weight calculation failed: {str(e)}")
            return 0.5
            
    async def _calculate_time_sensitivity(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate time sensitivity of notification"""        try:
            sensitivity = 0.5  # Default
            
            # Security notifications are highly time-sensitive
            if 'security' in notification.type.lower():
                sensitivity = 1.0
                
            # Copyright infringement is time-sensitive
            elif 'copyright' in notification.type.lower():
                sensitivity = 0.9
                
            # Collaboration opportunities have moderate time sensitivity
            elif 'collaboration' in notification.type.lower():
                sensitivity = 0.7
                
            # Business hours adjustment
            current_hour = datetime.utcnow().hour
            if 9 <= current_hour <= 17:  # Business hours
                sensitivity += 0.1
                
            return min(1.0, sensitivity)
            
        except Exception as e:
            self.logger.error(f"Time sensitivity calculation failed: {str(e)}")
            return 0.5
            
    def _get_content_type_weight(self, notification_type: str) -> float:
        """Get weight based on notification content type"""        type_weights = {
            'security_alert': 1.0,
            'copyright_infringement': 0.9,
            'collaboration_match': 0.7,
            'monetization_opportunity': 0.6,
            'seo_optimization': 0.5,
            'analytics_report': 0.3,
            'user_engagement': 0.4,
            'platform_update': 0.2
        }
        
        return type_weights.get(notification_type, 0.5)
        
    async def _assess_collaboration_value(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess collaboration value of notification"""        try:
            if 'collaboration' not in notification.type.lower():
                return 0.0
                
            value = 0.5  # Base collaboration value
            
            # High-value collaborations
            if context and context.get('collaboration_tier') == 'high':
                value = 0.9
            elif context and context.get('collaboration_tier') == 'medium':
                value = 0.7
                
            # Mutual connections boost value
            if context and context.get('mutual_connections', 0) > 5:
                value += 0.2
                
            return min(1.0, value)
            
        except Exception as e:
            self.logger.error(f"Collaboration value assessment failed: {str(e)}")
            return 0.0
            
    async def _assess_security_relevance(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess security relevance of notification"""        try:
            if 'security' not in notification.type.lower():
                return 0.0
                
            # All security notifications are highly relevant
            relevance = 1.0
            
            # Adjust based on severity
            if context and 'severity' in context:
                severity = context['severity']
                if severity == 'critical':
                    relevance = 1.0
                elif severity == 'high':
                    relevance = 0.8
                elif severity == 'medium':
                    relevance = 0.6
                else:
                    relevance = 0.4
                    
            return relevance
            
        except Exception as e:
            self.logger.error(f"Security relevance assessment failed: {str(e)}")
            return 0.0
            
    async def _assess_revenue_impact(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess revenue impact of notification"""        try:
            if not context or 'revenue_impact' not in context:
                return 0.0
                
            revenue_impact = context['revenue_impact']
            
            # Normalize revenue impact to 0-1 scale
            if revenue_impact > 1000:  # High revenue impact
                return 1.0
            elif revenue_impact > 500:  # Medium revenue impact
                return 0.7
            elif revenue_impact > 100:  # Low revenue impact
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            self.logger.error(f"Revenue impact assessment failed: {str(e)}")
            return 0.0
            
    async def _assess_engagement_potential(
        self,
        notification: NotificationModel,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess engagement potential of notification"""        try:
            potential = 0.5  # Default
            
            # Interactive notifications have higher engagement potential
            if notification.content.get('interactive_elements'):
                potential += 0.3
                
            # Personalized content has higher engagement
            if context and context.get('personalization_score', 0) > 0.7:
                potential += 0.2
                
            # Trending topics have higher engagement
            if context and context.get('trending_score', 0) > 0.8:
                potential += 0.3
                
            return min(1.0, potential)
            
        except Exception as e:
            self.logger.error(f"Engagement potential assessment failed: {str(e)}")
            return 0.5
            
    async def _calculate_final_priority_score(self, factors: PriorityFactors) -> float:
        """Calculate final priority score from all factors"""        try:
            # Weighted combination of factors
            weights = {
                'urgency': 0.25,
                'business_impact': 0.20,
                'security': 0.15,
                'revenue': 0.15,
                'time_sensitivity': 0.10,
                'collaboration': 0.05,
                'engagement': 0.05,
                'user_preference': 0.05
            }
            
            score = (
                weights['urgency'] * factors.urgency_score +
                weights['business_impact'] * factors.business_impact +
                weights['security'] * factors.security_relevance +
                weights['revenue'] * factors.revenue_impact +
                weights['time_sensitivity'] * factors.time_sensitivity +
                weights['collaboration'] * factors.collaboration_value +
                weights['engagement'] * factors.engagement_potential +
                weights['user_preference'] * factors.user_preference_weight
            )
            
            # Apply AI confidence factor
            score *= (0.5 + 0.5 * factors.ai_confidence)
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Final priority score calculation failed: {str(e)}")
            return 0.5
            
    async def _generate_priority_reasoning(
        self,
        factors: PriorityFactors,
        urgency_level: UrgencyLevel
    ) -> List[str]:
        """Generate human-readable reasoning for priority decision"""        reasoning = []
        
        try:
            # Urgency reasoning
            if factors.urgency_score > 0.8:
                reasoning.append(f"High urgency level: {urgency_level.value}")
            elif factors.urgency_score < 0.3:
                reasoning.append(f"Low urgency level: {urgency_level.value}")
                
            # Business impact reasoning
            if factors.business_impact > 0.7:
                reasoning.append("High business impact detected")
            elif factors.business_impact < 0.3:
                reasoning.append("Low business impact")
                
            # Security reasoning
            if factors.security_relevance > 0.8:
                reasoning.append("Critical security relevance")
                
            # Revenue reasoning
            if factors.revenue_impact > 0.7:
                reasoning.append("Significant revenue impact")
                
            # Time sensitivity reasoning
            if factors.time_sensitivity > 0.8:
                reasoning.append("Time-sensitive notification")
                
            # Collaboration reasoning
            if factors.collaboration_value > 0.7:
                reasoning.append("High-value collaboration opportunity")
                
            # Default reasoning if none specific
            if not reasoning:
                reasoning.append("Standard priority assessment applied")
                
        except Exception as e:
            self.logger.error(f"Priority reasoning generation failed: {str(e)}")
            reasoning.append("Priority determined by system defaults")
            
        return reasoning
        
    async def _generate_processing_hints(self, urgency_level: UrgencyLevel) -> Dict[str, Any]:
        """Generate processing hints based on urgency level"""        try:
            hints = {
                'preferred_channels': [],
                'max_retry_attempts': 3,
                'retry_delay': 60,
                'batch_processing': True
            }
            
            if urgency_level in [UrgencyLevel.CRITICAL, UrgencyLevel.URGENT]:
                hints.update({
                    'preferred_channels': ['sms', 'push_notification', 'email'],
                    'max_retry_attempts': 5,
                    'retry_delay': 30,
                    'batch_processing': False,
                    'immediate_delivery': True
                })
            elif urgency_level == UrgencyLevel.HIGH:
                hints.update({
                    'preferred_channels': ['push_notification', 'email'],
                    'max_retry_attempts': 4,
                    'retry_delay': 45,
                    'batch_processing': False
                })
            elif urgency_level == UrgencyLevel.LOW:
                hints.update({
                    'preferred_channels': ['email'],
                    'max_retry_attempts': 2,
                    'retry_delay': 120,
                    'batch_processing': True
                })
                
            return hints
            
        except Exception as e:
            self.logger.error(f"Processing hints generation failed: {str(e)}")
            return {}
            
    async def _generate_escalation_rules(self, urgency_level: UrgencyLevel) -> Dict[str, Any]:
        """Generate escalation rules based on urgency level"""        try:
            rules = {
                'enabled': False,
                'max_wait_time': 3600,
                'escalation_channels': [],
                'escalation_targets': []
            }
            
            if urgency_level == UrgencyLevel.CRITICAL:
                rules.update({
                    'enabled': True,
                    'max_wait_time': 300,  # 5 minutes
                    'escalation_channels': ['sms', 'phone_call', 'slack'],
                    'escalation_targets': ['admin', 'security_team']
                })
            elif urgency_level == UrgencyLevel.URGENT:
                rules.update({
                    'enabled': True,
                    'max_wait_time': 900,  # 15 minutes
                    'escalation_channels': ['sms', 'slack'],
                    'escalation_targets': ['admin']
                })
            elif urgency_level == UrgencyLevel.HIGH:
                rules.update({
                    'enabled': True,
                    'max_wait_time': 1800,  # 30 minutes
                    'escalation_channels': ['email', 'slack'],
                    'escalation_targets': ['support_team']
                })
                
            return rules
            
        except Exception as e:
            self.logger.error(f"Escalation rules generation failed: {str(e)}")
            return {}
            
    async def _generate_delivery_constraints(self, urgency_level: UrgencyLevel) -> Dict[str, Any]:
        """Generate delivery constraints based on urgency level"""        try:
            constraints = {
                'respect_quiet_hours': True,
                'respect_user_preferences': True,
                'max_daily_notifications': 10,
                'cooldown_period': 300
            }
            
            if urgency_level in [UrgencyLevel.CRITICAL, UrgencyLevel.URGENT]:
                constraints.update({
                    'respect_quiet_hours': False,
                    'respect_user_preferences': False,
                    'max_daily_notifications': 50,
                    'cooldown_period': 0
                })
            elif urgency_level == UrgencyLevel.HIGH:
                constraints.update({
                    'respect_quiet_hours': False,
                    'max_daily_notifications': 25,
                    'cooldown_period': 60
                })
                
            return constraints
            
        except Exception as e:
            self.logger.error(f"Delivery constraints generation failed: {str(e)}")
            return {}
            
    async def _process_priority_queue(self, priority: NotificationPriority):
        """Process notifications from a specific priority queue"""        while self.is_running:
            try:
                queue = self.priority_queues[priority]
                
                # Get processing rate for this priority level
                processing_rate = queue.processing_rate
                processing_interval = 1.0 / processing_rate
                
                # Get next notification
                notification = queue.get_next_notification()
                
                if notification:
                    # Process notification (delegate to notification agent)
                    await self._delegate_notification_processing(notification, priority)
                    
                    # Update metrics
                    self.performance_metrics['total_processed'] += 1
                    
                    # Maintain processing rate
                    await asyncio.sleep(processing_interval)
                else:
                    # No notifications, sleep briefly
                    await asyncio.sleep(0.5)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing {priority.value} queue: {str(e)}")
                await asyncio.sleep(1)
                
    async def _delegate_notification_processing(
        self,
        notification: NotificationModel,
        priority: NotificationPriority
    ):
        """Delegate notification processing to notification agent"""        try:
            # Import here to avoid circular imports
            from .notification_agent import NotificationAgent
            
            # This would normally get the agent from a registry or factory
            # For now, we'll just log the processing
            self.logger.info(
                f"Processing notification {notification.id} with priority {priority.value}"
            )
            
            # Update processing metrics
            if priority.value not in self.performance_metrics['processing_rates']:
                self.performance_metrics['processing_rates'][priority.value] = 0
                
            self.performance_metrics['processing_rates'][priority.value] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to delegate notification processing: {str(e)}")
            
    async def _balance_queues(self):
        """Balance queue processing based on load and performance"""        while self.is_running:
            try:
                # Analyze queue sizes and adjust processing rates
                for priority, queue in self.priority_queues.items():
                    queue_size = queue.size()
                    
                    # Adjust processing rate based on queue size
                    if queue_size > queue.max_size * 0.8:  # Queue is 80% full
                        # Increase processing rate
                        queue.processing_rate = min(50.0, queue.processing_rate * 1.2)
                    elif queue_size < queue.max_size * 0.2:  # Queue is 20% full
                        # Decrease processing rate to conserve resources
                        queue.processing_rate = max(1.0, queue.processing_rate * 0.9)
                        
                # Sleep for 30 seconds before next balancing
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Queue balancing error: {str(e)}")
                await asyncio.sleep(30)
                
    async def _monitor_escalations(self):
        """Monitor notifications for escalation requirements"""        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                # Check each queue for notifications that need escalation
                for priority, queue in self.priority_queues.items():
                    # Check if any notifications have been waiting too long
                    max_wait_time = self.escalation_policies.get(
                        f'max_wait_time_{priority.value.lower()}', 3600
                    )
                    
                    # In a real implementation, we would track notification timestamps
                    # and escalate those that have exceeded wait time
                    
                # Sleep for 60 seconds before next check
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Escalation monitoring error: {str(e)}")
                await asyncio.sleep(60)
                
    async def _monitor_performance(self):
        """Monitor performance metrics and optimization opportunities"""        while self.is_running:
            try:
                # Update queue size metrics
                for priority, queue in self.priority_queues.items():
                    self.performance_metrics['queue_sizes'][priority.value] = queue.size()
                    
                # Calculate average wait time (placeholder calculation)
                total_notifications = sum(self.performance_metrics['queue_sizes'].values())
                if total_notifications > 0:
                    # Simplified wait time calculation
                    self.performance_metrics['average_wait_time'] = total_notifications * 0.1
                    
                # Log performance metrics periodically
                self.logger.info(f"Priority handler performance: {self.performance_metrics}")
                
                # Sleep for 5 minutes before next performance check
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(300)
                
    async def _update_queue_metrics(self):
        """Update queue size metrics"""        try:
            for priority, queue in self.priority_queues.items():
                self.performance_metrics['queue_sizes'][priority.value] = queue.size()
                
        except Exception as e:
            self.logger.error(f"Queue metrics update failed: {str(e)}")
            
    async def _process_remaining_notifications(self):
        """Process any remaining notifications during shutdown"""        try:
            total_remaining = 0
            
            for priority, queue in self.priority_queues.items():
                remaining = queue.size()
                total_remaining += remaining
                
                # Process a limited number of remaining notifications
                processed = 0
                max_process = min(remaining, 10)  # Limit to prevent long shutdown
                
                while processed < max_process and not queue.is_empty():
                    notification = queue.get_next_notification()
                    if notification:
                        await self._delegate_notification_processing(notification, priority)
                        processed += 1
                        
            self.logger.info(f"Processed {total_remaining} remaining notifications during shutdown")
            
        except Exception as e:
            self.logger.error(f"Error processing remaining notifications: {str(e)}")
            
    async def get_queue_statistics(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""        try:
            statistics = {
                'queue_sizes': {},
                'processing_rates': {},
                'performance_metrics': self.performance_metrics.copy(),
                'queue_health': {}
            }
            
            for priority, queue in self.priority_queues.items():
                priority_name = priority.value
                
                statistics['queue_sizes'][priority_name] = queue.size()
                statistics['processing_rates'][priority_name] = queue.processing_rate
                
                # Calculate queue health score
                queue_utilization = queue.size() / queue.max_size
                if queue_utilization < 0.5:
                    health_score = 'healthy'
                elif queue_utilization < 0.8:
                    health_score = 'moderate'
                else:
                    health_score = 'overloaded'
                    
                statistics['queue_health'][priority_name] = {
                    'status': health_score,
                    'utilization': queue_utilization,
                    'last_processed': queue.last_processed.isoformat()
                }
                
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get queue statistics: {str(e)}")
            return {}
    max_size: int = 1000
    processing_rate: float = 1.0  # notifications per second
    last_processed: datetime = field(default_factory=datetime.utcnow)
    queue_metrics: Dict[str, Any] = field(default_factory=dict)


class PriorityHandler:
    """    Advanced priority-based notification management system
    
    Features:
    - AI-driven priority classification and scoring
    - Multi-factor priority analysis with business context
    - Dynamic priority adjustment based on real-time conditions
    - Priority-based queue management and processing optimization
    - Escalation and de-escalation based on priority evolution
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.priority_classifier = PriorityClassificationEngine(
            config.get('classifier_config', {})
        )
        self.business_logic = PriorityBusinessLogic(
            config.get('business_config', {})
        )
        self.monitoring = PriorityMonitoringService(
            config.get('monitoring_config', {})
        )
        
        # Priority queues management
        self.priority_queues: Dict[NotificationPriority, PriorityQueue] = {}
        self.processing_order: List[NotificationPriority] = [
            NotificationPriority.URGENT,
            NotificationPriority.HIGH,
            NotificationPriority.MEDIUM,
            NotificationPriority.LOW
        ]
        
        # Priority rules and configuration
        self.priority_rules: Dict[str, PriorityRule] = {}
        self.context_weights: Dict[PriorityContext, float] = {}
        self.user_priority_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Dynamic priority adjustment
        self.priority_adjustments: Dict[str, float] = {}
        self.escalation_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.performance_metrics = {
            'total_processed': 0,
            'average_priority_score': 0.0,
            'escalations_triggered': 0,
            'queue_efficiency': {},
            'classification_accuracy': 0.0
        }
        
        # Real-time priority monitoring
        self.priority_trends = defaultdict(deque)
        self.system_load_factor = 1.0
        
    async def initialize_handler(self):
        """Initialize the priority handler with all components"""        try:
            self.logger.info("Initializing PriorityHandler with AI-driven classification")
            
            # Initialize AI classifier
            await self.priority_classifier.initialize()
            
            # Initialize priority queues
            await self._initialize_priority_queues()
            
            # Load priority rules and configurations
            await self._load_priority_configurations()
            
            # Start monitoring
            await self.monitoring.start_monitoring()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._process_priority_queues()),
                asyncio.create_task(self._monitor_priority_trends()),
                asyncio.create_task(self._adjust_dynamic_priorities()),
                asyncio.create_task(self._optimize_queue_performance()),
                asyncio.create_task(self._cleanup_expired_data())
            ]
            
            self.logger.info("PriorityHandler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PriorityHandler: {str(e)}")
            return False
            
    async def classify_notification_priority(
        self,
        notification: NotificationModel,
        context: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> PriorityDecision:
        """        Classify notification priority using advanced AI-driven analysis
        
        Args:
            notification: Notification to classify
            context: Rich context information
            user_preferences: User's priority preferences
            
        Returns:
            Comprehensive priority decision with reasoning
        """        try:
            # Extract priority factors from notification and context
            factors = await self._extract_priority_factors(
                notification, context, user_preferences
            )
            
            # Apply AI classification
            ai_priority = await self.priority_classifier.classify_priority(
                notification, context, factors
            )
            
            # Apply business logic rules
            business_priority = await self.business_logic.apply_priority_rules(
                notification, context, factors
            )
            
            # Combine AI and business rule results
            combined_priority = await self._combine_priority_scores(
                ai_priority, business_priority, factors
            )
            
            # Apply dynamic adjustments
            adjusted_priority = await self._apply_dynamic_adjustments(
                combined_priority, notification, context
            )
            
            # Generate priority decision
            priority_decision = await self._generate_priority_decision(
                adjusted_priority, factors, notification, context
            )
            
            # Record for monitoring and learning
            await self.monitoring.record_priority_classification(
                notification.id, priority_decision
            )
            
            # Update trends
            self._update_priority_trends(priority_decision)
            
            return priority_decision
            
        except Exception as e:
            self.logger.error(f"Priority classification failed: {str(e)}")
            # Fallback to default priority
            return PriorityDecision(
                final_priority=NotificationPriority.MEDIUM,
                urgency_level=UrgencyLevel.MEDIUM,
                priority_score=50.0,
                factors=PriorityFactors(),
                reasoning=["Error in classification, using default priority"],
                confidence=0.0,
                processing_hints={},
                escalation_rules={},
                delivery_constraints={}
            )
            
    async def queue_notification(
        self,
        notification: NotificationModel,
        priority_decision: PriorityDecision
    ) -> str:
        """        Queue notification based on priority decision
        
        Args:
            notification: Notification to queue
            priority_decision: Priority decision from classification
            
        Returns:
            queue_position_id: Unique identifier for queue position
        """        try:
            priority_level = priority_decision.final_priority
            
            # Get appropriate priority queue
            queue = self.priority_queues.get(priority_level)
            if not queue:
                raise ValueError(f"No queue configured for priority: {priority_level}")
                
            # Calculate queue position score (higher score = higher priority)
            position_score = await self._calculate_queue_position_score(
                priority_decision, notification
            )
            
            # Add to priority queue
            heapq.heappush(
                queue.notifications,
                (-position_score, notification)  # Negative for max heap behavior
            )
            
            # Update queue metrics
            queue.queue_metrics['total_queued'] = queue.queue_metrics.get('total_queued', 0) + 1
            queue.queue_metrics['last_queued'] = datetime.utcnow().isoformat()
            
            # Check queue size limits
            if len(queue.notifications) > queue.max_size:
                await self._handle_queue_overflow(queue)
                
            queue_position_id = f"{priority_level.value}_{uuid.uuid4()}"
            
            self.logger.info(
                f"Notification queued: {notification.id} in {priority_level.value} "
                f"queue with score {position_score:.2f}"
            )
            
            return queue_position_id
            
        except Exception as e:
            self.logger.error(f"Failed to queue notification: {str(e)}")
            raise
            
    async def escalate_notification(
        self,
        notification_id: str,
        escalation_reason: str,
        new_priority: Optional[NotificationPriority] = None
    ) -> bool:
        """        Escalate notification priority with detailed tracking
        
        Args:
            notification_id: ID of notification to escalate
            escalation_reason: Reason for escalation
            new_priority: New priority level (auto-determined if not provided)
            
        Returns:
            success: Whether escalation was successful
        """        try:
            # Find notification in queues
            current_queue, notification = await self._find_notification_in_queues(
                notification_id
            )
            
            if not notification:
                self.logger.warning(f"Notification not found for escalation: {notification_id}")
                return False
                
            # Determine new priority
            if not new_priority:
                new_priority = await self._calculate_escalated_priority(
                    notification, escalation_reason
                )
                
            # Remove from current queue
            await self._remove_from_queue(current_queue, notification)
            
            # Re-classify with escalation context
            escalation_context = {
                'escalation_reason': escalation_reason,
                'previous_priority': current_queue.priority_level.value,
                'escalation_timestamp': datetime.utcnow().isoformat()
            }
            
            # Update notification priority
            notification.priority = new_priority
            
            # Re-queue with new priority
            priority_decision = PriorityDecision(
                final_priority=new_priority,
                urgency_level=UrgencyLevel.URGENT,  # Escalated notifications are urgent
                priority_score=90.0,  # High score for escalated items
                factors=PriorityFactors(urgency_score=90.0),
                reasoning=[f"Escalated: {escalation_reason}"],
                confidence=1.0,
                processing_hints={'escalated': True},
                escalation_rules={},
                delivery_constraints={}
            )
            
            await self.queue_notification(notification, priority_decision)
            
            # Record escalation
            escalation_record = {
                'notification_id': notification_id,
                'escalated_at': datetime.utcnow().isoformat(),
                'escalation_reason': escalation_reason,
                'from_priority': current_queue.priority_level.value,
                'to_priority': new_priority.value
            }
            
            self.escalation_history.append(escalation_record)
            self.performance_metrics['escalations_triggered'] += 1
            
            # Monitor escalation
            await self.monitoring.record_priority_escalation(escalation_record)
            
            self.logger.info(f"Notification escalated: {notification_id} to {new_priority.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Escalation failed for notification {notification_id}: {str(e)}")
            return False
            
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all priority queues"""        try:
            queue_status = {
                'queues': {},
                'processing_metrics': {},
                'system_health': {},
                'performance_summary': self.performance_metrics.copy()
            }
            
            # Queue details
            for priority, queue in self.priority_queues.items():
                queue_status['queues'][priority.value] = {
                    'queue_size': len(queue.notifications),
                    'max_size': queue.max_size,
                    'processing_rate': queue.processing_rate,
                    'last_processed': queue.last_processed.isoformat(),
                    'metrics': queue.queue_metrics.copy(),
                    'utilization': len(queue.notifications) / queue.max_size
                }
                
            # Processing metrics
            total_queued = sum(
                len(queue.notifications) for queue in self.priority_queues.values()
            )
            
            queue_status['processing_metrics'] = {
                'total_queued_notifications': total_queued,
                'system_load_factor': self.system_load_factor,
                'average_processing_time': await self._calculate_average_processing_time(),
                'queue_efficiency': await self._calculate_queue_efficiency()
            }
            
            # System health
            queue_status['system_health'] = {
                'healthy_queues': sum(
                    1 for queue in self.priority_queues.values()
                    if len(queue.notifications) < queue.max_size * 0.8
                ),
                'total_queues': len(self.priority_queues),
                'escalations_last_hour': await self._count_recent_escalations(3600),
                'classification_accuracy': self.performance_metrics['classification_accuracy']
            }
            
            return queue_status
            
        except Exception as e:
            self.logger.error(f"Failed to get queue status: {str(e)}")
            return {}
            
    async def update_user_priority_profile(
        self,
        user_id: str,
        priority_preferences: Dict[str, Any]
    ) -> bool:
        """Update user's priority preferences and profile"""        try:
            # Validate priority preferences
            if not await self._validate_priority_preferences(priority_preferences):
                return False
                
            # Update user profile
            self.user_priority_profiles[user_id] = {
                **priority_preferences,
                'updated_at': datetime.utcnow().isoformat(),
                'profile_version': self.user_priority_profiles.get(user_id, {}).get('profile_version', 0) + 1
            }
            
            # Update AI classifier with user preferences
            await self.priority_classifier.update_user_profile(
                user_id, priority_preferences
            )
            
            self.logger.info(f"Updated priority profile for user: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update user priority profile: {str(e)}")
            return False
            
    async def _initialize_priority_queues(self):
        """Initialize priority queues for each priority level"""        try:
            queue_configs = self.config.get('queue_configs', {})
            
            for priority in NotificationPriority:
                queue_config = queue_configs.get(priority.value, {})
                
                self.priority_queues[priority] = PriorityQueue(
                    queue_id=f"queue_{priority.value}",
                    priority_level=priority,
                    notifications=[],
                    max_size=queue_config.get('max_size', 1000),
                    processing_rate=queue_config.get('processing_rate', 1.0)
                )
                
            self.logger.info(f"Initialized {len(self.priority_queues)} priority queues")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize priority queues: {str(e)}")
            raise
            
    async def _load_priority_configurations(self):
        """Load priority rules and context weights"""        try:
            # Load priority rules
            rules_config = self.config.get('priority_rules', {})
            for rule_name, rule_data in rules_config.items():
                self.priority_rules[rule_name] = PriorityRule(**rule_data)
                
            # Load context weights
            context_config = self.config.get('context_weights', {})
            for context_name, weight in context_config.items():
                if hasattr(PriorityContext, context_name.upper()):
                    context = PriorityContext(context_name)
                    self.context_weights[context] = weight
                    
            # Set default context weights if not configured
            if not self.context_weights:
                self.context_weights = {
                    PriorityContext.SECURITY_INCIDENT: 1.0,
                    PriorityContext.CONTENT_PROTECTION: 0.9,
                    PriorityContext.BUSINESS_CRITICAL: 0.8,
                    PriorityContext.COLLABORATION_OPPORTUNITY: 0.7,
                    PriorityContext.MONETIZATION_ALERT: 0.6,
                    PriorityContext.USER_ENGAGEMENT: 0.5,
                    PriorityContext.PLATFORM_UPDATE: 0.4,
                    PriorityContext.SYSTEM_MAINTENANCE: 0.3
                }
                
            self.logger.info("Priority configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load priority configurations: {str(e)}")
            
    async def _extract_priority_factors(
        self,
        notification: NotificationModel,
        context: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> PriorityFactors:
        """Extract comprehensive priority factors from notification data"""        try:
            factors = PriorityFactors()
            
            # Base urgency from notification type
            notification_type = context.get('notification_type', '')
            factors.urgency_score = await self._calculate_type_urgency(notification_type)
            
            # Business impact analysis
            factors.business_impact = await self._analyze_business_impact(notification, context)
            
            # User preference weighting
            if user_preferences:
                factors.user_preference_weight = await self._calculate_user_preference_weight(
                    notification, user_preferences
                )
                
            # Time sensitivity
            factors.time_sensitivity = await self._analyze_time_sensitivity(notification, context)
            
            # Content type weighting
            factors.content_type_weight = await self._calculate_content_type_weight(context)
            
            # Collaboration value (specific to IA Influencer platform)
            factors.collaboration_value = await self._analyze_collaboration_value(context)
            
            # Security relevance
            factors.security_relevance = await self._analyze_security_relevance(context)
            
            # Revenue impact
            factors.revenue_impact = await self._analyze_revenue_impact(context)
            
            # Engagement potential
            factors.engagement_potential = await self._analyze_engagement_potential(context)
            
            # AI confidence in analysis
            factors.ai_confidence = await self.priority_classifier.get_confidence_score(
                notification, context
            )
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Failed to extract priority factors: {str(e)}")
            return PriorityFactors()  # Return empty factors on error
            
    async def _calculate_type_urgency(self, notification_type: str) -> float:
        """Calculate urgency score based on notification type"""        type_urgency_map = {
            'security_alert': 95.0,
            'content_protection_violation': 90.0,
            'copyright_infringement': 85.0,
            'collaboration_opportunity': 70.0,
            'monetization_opportunity': 65.0,
            'seo_optimization': 50.0,
            'content_upload': 45.0,
            'user_engagement': 40.0,
            'platform_update': 30.0,
            'analytics_report': 20.0
        }
        
        return type_urgency_map.get(notification_type, 40.0)  # Default medium urgency
        
    async def _analyze_business_impact(
        self,
        notification: NotificationModel,
        context: Dict[str, Any]
    ) -> float:
        """Analyze business impact of the notification"""        try:
            business_impact = 50.0  # Base impact
            
            # Revenue-related notifications have higher impact
            if 'monetization' in context.get('notification_type', '').lower():
                revenue_amount = context.get('revenue_amount', 0)
                if revenue_amount > 1000:
                    business_impact += 30.0
                elif revenue_amount > 100:
                    business_impact += 15.0
                    
            # Content protection has high business impact
            if 'protection' in context.get('notification_type', '').lower():
                business_impact += 25.0
                
            # Collaboration opportunities
            if 'collaboration' in context.get('notification_type', '').lower():
                collaboration_value = context.get('collaboration_score', 0)
                business_impact += min(collaboration_value * 20, 40)
                
            # User count affects impact
            user_count = context.get('affected_users', 1)
            if user_count > 1000:
                business_impact += 20.0
            elif user_count > 100:
                business_impact += 10.0
                
            return min(business_impact, 100.0)
            
        except Exception as e:
            self.logger.error(f"Business impact analysis failed: {str(e)}")
            return 50.0
            
    async def _calculate_user_preference_weight(
        self,
        notification: NotificationModel,
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate weighting based on user preferences"""        try:
            # Get user's priority preferences
            channel_preferences = user_preferences.get('channel_preferences', {})
            type_preferences = user_preferences.get('type_preferences', {})
            
            weight = 50.0  # Base weight
            
            # Channel preference weighting
            for channel in notification.channels:
                channel_weight = channel_preferences.get(channel.value, 50.0)
                weight = max(weight, channel_weight)
                
            # Type preference weighting
            notification_type = notification.type
            type_weight = type_preferences.get(notification_type, 50.0)
            weight = (weight + type_weight) / 2
            
            return min(weight, 100.0)
            
        except Exception as e:
            self.logger.error(f"User preference weight calculation failed: {str(e)}")
            return 50.0
            
    async def _analyze_time_sensitivity(
        self,
        notification: NotificationModel,
        context: Dict[str, Any]
    ) -> float:
        """Analyze time sensitivity of notification"""        try:
            sensitivity = 50.0
            
            # Check for time-sensitive keywords
            time_sensitive_keywords = [
                'urgent', 'immediate', 'deadline', 'expires', 'limited time',
                'breaking', 'critical', 'emergency'
            ]
            
            content_text = str(notification.content).lower()
            for keyword in time_sensitive_keywords:
                if keyword in content_text:
                    sensitivity += 20.0
                    break
                    
            # Check for specific deadlines
            deadline = context.get('deadline')
            if deadline:
                try:
                    deadline_dt = datetime.fromisoformat(deadline)
                    time_until_deadline = (deadline_dt - datetime.utcnow()).total_seconds()
                    
                    if time_until_deadline < 3600:  # Less than 1 hour
                        sensitivity += 40.0
                    elif time_until_deadline < 86400:  # Less than 1 day
                        sensitivity += 20.0
                    elif time_until_deadline < 604800:  # Less than 1 week
                        sensitivity += 10.0
                        
                except Exception:
                    pass  # Invalid deadline format
                    
            return min(sensitivity, 100.0)
            
        except Exception as e:
            self.logger.error(f"Time sensitivity analysis failed: {str(e)}")
            return 50.0
            
    async def _process_priority_queues(self):
        """Main queue processing loop"""        while True:
            try:
                # Process queues in priority order
                for priority in self.processing_order:
                    queue = self.priority_queues.get(priority)
                    if queue and queue.notifications:
                        await self._process_queue_batch(queue)
                        
                # Brief pause between processing cycles
                await asyncio.sleep(1.0 / self.system_load_factor)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Queue processing error: {str(e)}")
                await asyncio.sleep(5)
                
    async def _process_queue_batch(self, queue: PriorityQueue):
        """Process a batch of notifications from a priority queue"""        try:
            batch_size = min(
                int(queue.processing_rate * self.system_load_factor),
                len(queue.notifications),
                10  # Maximum batch size
            )
            
            if batch_size == 0:
                return
                
            # Extract batch of highest priority notifications
            batch = []
            for _ in range(batch_size):
                if queue.notifications:
                    priority_score, notification = heapq.heappop(queue.notifications)
                    batch.append((priority_score, notification))
                    
            # Process batch
            for priority_score, notification in batch:
                await self._process_single_notification(notification, -priority_score)
                
            # Update queue metrics
            queue.queue_metrics['total_processed'] = queue.queue_metrics.get('total_processed', 0) + len(batch)
            queue.last_processed = datetime.utcnow()
            
            self.performance_metrics['total_processed'] += len(batch)
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            
    async def _process_single_notification(
        self,
        notification: NotificationModel,
        priority_score: float
    ):
        """Process individual notification"""        try:
            # This would integrate with the main notification delivery system
            # For now, we'll just log the processing
            self.logger.info(
                f"Processing notification {notification.id} with priority score {priority_score:.2f}"
            )
            
            # Update performance metrics
            current_avg = self.performance_metrics['average_priority_score']
            total_processed = self.performance_metrics['total_processed']
            
            new_avg = ((current_avg * (total_processed - 1)) + priority_score) / total_processed
            self.performance_metrics['average_priority_score'] = new_avg
            
        except Exception as e:
            self.logger.error(f"Single notification processing failed: {str(e)}")


class UrgencyClassifier:
    """    Advanced urgency classification system with machine learning capabilities
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.classification_model = None
        self.feature_extractors = []
        self.training_data = deque(maxlen=10000)
        
    async def initialize_classifier(self):
        """Initialize the urgency classification system"""        try:
            # Load pre-trained model if available
            await self._load_classification_model()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            # Load historical training data
            await self._load_training_data()
            
            self.logger.info("UrgencyClassifier initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize UrgencyClassifier: {str(e)}")
            return False
            
    async def classify_urgency(
        self,
        notification: NotificationModel,
        context: Dict[str, Any]
    ) -> Tuple[UrgencyLevel, float]:
        """        Classify notification urgency using machine learning
        
        Args:
            notification: Notification to classify
            context: Rich context information
            
        Returns:
            Tuple of (urgency_level, confidence_score)
        """        try:
            # Extract features
            features = await self._extract_urgency_features(notification, context)
            
            # Apply ML classification if model is available
            if self.classification_model:
                urgency_level, confidence = await self._ml_classify_urgency(features)
            else:
                # Fallback to rule-based classification
                urgency_level, confidence = await self._rule_based_classify_urgency(
                    notification, context, features
                )
                
            # Record classification for training
            self.training_data.append({
                'features': features,
                'urgency_level': urgency_level.value,
                'confidence': confidence,
                'timestamp': datetime.utcnow().isoformat(),
                'notification_id': notification.id
            })
            
            return urgency_level, confidence
            
        except Exception as e:
            self.logger.error(f"Urgency classification failed: {str(e)}")
            return UrgencyLevel.MEDIUM, 0.5
            
    async def _extract_urgency_features(
        self,
        notification: NotificationModel,
        context: Dict[str, Any]
    ) -> np.ndarray:
        """Extract feature vector for urgency classification"""        try:
            features = []
            
            # Basic notification features
            features.extend([
                len(str(notification.content)),  # Content length
                len(notification.channels),      # Number of channels
                int(notification.priority.value == 'urgent'),  # Is already marked urgent
            ])
            
            # Context features
            features.extend([
                context.get('user_count', 0),
                context.get('revenue_impact', 0),
                int('security' in context.get('notification_type', '').lower()),
                int('protection' in context.get('notification_type', '').lower()),
                int('collaboration' in context.get('notification_type', '').lower()),
            ])
            
            # Time-based features
            created_hour = notification.created_at.hour
            features.extend([
                created_hour,
                int(created_hour < 9 or created_hour > 17),  # Outside business hours
                notification.created_at.weekday(),  # Day of week
            ])
            
            # Text analysis features
            content_text = str(notification.content).lower()
            urgent_keywords = ['urgent', 'critical', 'immediate', 'emergency', 'breaking']
            features.append(
                sum(1 for keyword in urgent_keywords if keyword in content_text)
            )
            
            return np.array(features, dtype=float)
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            return np.zeros(10)  # Return zero vector on error
            
    async def _rule_based_classify_urgency(
        self,
        notification: NotificationModel,
        context: Dict[str, Any],
        features: np.ndarray
    ) -> Tuple[UrgencyLevel, float]:
        """Rule-based urgency classification as fallback"""        try:
            score = 0.0
            confidence = 0.7  # Rule-based has moderate confidence
            
            notification_type = context.get('notification_type', '').lower()
            
            # Security and protection get highest urgency
            if any(keyword in notification_type for keyword in ['security', 'protection', 'violation']):
                score += 40.0
                
            # Business-critical notifications
            if any(keyword in notification_type for keyword in ['critical', 'urgent', 'emergency']):
                score += 35.0
                
            # Revenue impact
            revenue_impact = context.get('revenue_impact', 0)
            if revenue_impact > 1000:
                score += 25.0
            elif revenue_impact > 100:
                score += 15.0
                
            # User impact
            user_count = context.get('user_count', 0)
            if user_count > 1000:
                score += 20.0
            elif user_count > 100:
                score += 10.0
                
            # Time sensitivity
            content_text = str(notification.content).lower()
            urgent_keywords = ['urgent', 'immediate', 'deadline', 'expires']
            if any(keyword in content_text for keyword in urgent_keywords):
                score += 15.0
                
            # Determine urgency level based on score
            if score >= 80:
                return UrgencyLevel.CRITICAL, confidence
            elif score >= 60:
                return UrgencyLevel.URGENT, confidence
            elif score >= 40:
                return UrgencyLevel.HIGH, confidence
            elif score >= 20:
                return UrgencyLevel.MEDIUM, confidence
            else:
                return UrgencyLevel.LOW, confidence
                
        except Exception as e:
            self.logger.error(f"Rule-based classification failed: {str(e)}")
            return UrgencyLevel.MEDIUM, 0.5
            
    async def update_classification_feedback(
        self,
        notification_id: str,
        actual_urgency: UrgencyLevel,
        feedback_context: Dict[str, Any]
    ) -> bool:
        """Update classifier with feedback for improved accuracy"""        try:
            # Find the original classification
            for record in self.training_data:
                if record['notification_id'] == notification_id:
                    record['actual_urgency'] = actual_urgency.value
                    record['feedback_context'] = feedback_context
                    record['feedback_timestamp'] = datetime.utcnow().isoformat()
                    break
                    
            # Trigger model retraining if enough feedback accumulated
            feedback_count = sum(
                1 for record in self.training_data 
                if 'actual_urgency' in record
            )
            
            if feedback_count >= 100 and feedback_count % 50 == 0:
                await self._retrain_model()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update classification feedback: {str(e)}")
            return False
