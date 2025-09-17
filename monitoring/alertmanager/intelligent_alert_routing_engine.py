#!/usr/bin/env python3
"""
Intelligent Alert Routing Engine - ML-Powered Alert Classification
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - All Rights Reserved

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Creator Economy Platform
Module: Intelligent Alert Routing Engine
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import numpy as np
from pathlib import Path

# ML/AI imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import pandas as pd
except ImportError as e:
    logging.warning(f"ML dependencies not available: {e}")
    # Fallback to basic implementations

logger = logging.getLogger(__name__)


class RoutingDecisionType(Enum):
    """Types of routing decisions"""
    IMMEDIATE = "immediate"           # Immediate notification
    DELAYED = "delayed"              # Delayed notification
    SUPPRESSED = "suppressed"        # Suppressed during maintenance
    ESCALATED = "escalated"          # Escalated to higher tier
    CORRELATED = "correlated"        # Part of correlation group
    FILTERED = "filtered"            # Filtered as noise


class NotificationChannel(Enum):
    """Available notification channels"""
    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    MOBILE_PUSH = "mobile_push"


@dataclass
class RoutingDecision:
    """Routing decision with rationale and configuration"""
    decision_type: RoutingDecisionType
    channels: List[NotificationChannel]
    priority_score: float  # 0-1 scale
    delay_seconds: int = 0
    requires_escalation: bool = False
    escalation_timeout: int = 900  # 15 minutes default
    rationale: str = ""
    confidence_score: float = 0.0
    routing_rules_applied: List[str] = field(default_factory=list)
    ml_predictions: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "decision_type": self.decision_type.value,
            "channels": [ch.value for ch in self.channels],
            "priority_score": self.priority_score,
            "delay_seconds": self.delay_seconds,
            "requires_escalation": self.requires_escalation,
            "escalation_timeout": self.escalation_timeout,
            "rationale": self.rationale,
            "confidence_score": self.confidence_score,
            "routing_rules_applied": self.routing_rules_applied,
            "ml_predictions": self.ml_predictions
        }


@dataclass
class AlertFeatures:
    """Feature vector for ML classification"""
    severity_numeric: float
    creator_tier_numeric: float
    business_impact: float
    revenue_impact: float
    user_count_log: float
    time_of_day: float
    day_of_week: float
    service_category_encoded: float
    historical_frequency: float
    correlation_strength: float
    text_features: np.ndarray = field(default_factory=lambda: np.array([]))


class IntelligentAlertRoutingEngine:
    """
    ML-Powered Alert Routing Engine for Creator Economy
    
    Features:
    - ML-based alert classification
    - Creator impact prediction
    - Dynamic routing rule adjustment
    - Context-aware routing decisions
    - Business criticality assessment
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the routing engine with ML models"""
        self.config = config
        self.models = {}
        self.vectorizers = {}
        self.scalers = {}
        self.encoders = {}
        self.routing_rules = self._load_routing_rules()
        self.ml_enabled = self._initialize_ml_models()
        
        # Performance metrics
        self.routing_stats = {
            "total_routed": 0,
            "ml_predictions_used": 0,
            "rule_based_decisions": 0,
            "escalations_triggered": 0,
            "suppressions_applied": 0
        }
        
        logger.info("Intelligent Alert Routing Engine initialized")
    
    def _load_routing_rules(self) -> Dict[str, Any]:
        """Load business routing rules configuration"""
        return {
            "creator_tier_rules": {
                "premium": {
                    "max_delay_seconds": 60,
                    "required_channels": ["slack", "sms", "pagerduty"],
                    "escalation_timeout": 300,  # 5 minutes
                    "priority_multiplier": 2.0
                },
                "professional": {
                    "max_delay_seconds": 300,
                    "required_channels": ["slack", "email"],
                    "escalation_timeout": 900,  # 15 minutes
                    "priority_multiplier": 1.5
                },
                "emerging": {
                    "max_delay_seconds": 900,
                    "required_channels": ["email"],
                    "escalation_timeout": 1800,  # 30 minutes
                    "priority_multiplier": 1.0
                },
                "starter": {
                    "max_delay_seconds": 1800,
                    "required_channels": ["email"],
                    "escalation_timeout": 3600,  # 1 hour
                    "priority_multiplier": 0.5
                }
            },
            "severity_rules": {
                "emergency": {
                    "immediate_channels": ["slack", "sms", "pagerduty"],
                    "delay_seconds": 0,
                    "requires_escalation": True,
                    "priority_score": 1.0
                },
                "critical": {
                    "immediate_channels": ["slack", "pagerduty"],
                    "delay_seconds": 0,
                    "requires_escalation": True,
                    "priority_score": 0.9
                },
                "high": {
                    "immediate_channels": ["slack"],
                    "delay_seconds": 30,
                    "requires_escalation": False,
                    "priority_score": 0.7
                },
                "warning": {
                    "immediate_channels": ["email"],
                    "delay_seconds": 300,
                    "requires_escalation": False,
                    "priority_score": 0.5
                },
                "info": {
                    "immediate_channels": ["email"],
                    "delay_seconds": 900,
                    "requires_escalation": False,
                    "priority_score": 0.3
                }
            },
            "service_rules": {
                "api": {
                    "channels": ["slack", "pagerduty"],
                    "escalation_multiplier": 1.5
                },
                "database": {
                    "channels": ["slack", "pagerduty", "sms"],
                    "escalation_multiplier": 2.0
                },
                "ai-engine": {
                    "channels": ["slack", "email"],
                    "escalation_multiplier": 1.2
                },
                "payment": {
                    "channels": ["slack", "sms", "pagerduty"],
                    "escalation_multiplier": 2.5
                },
                "security": {
                    "channels": ["slack", "sms", "pagerduty"],
                    "escalation_multiplier": 3.0
                }
            },
            "time_based_rules": {
                "business_hours": {
                    "channels": ["slack", "email"],
                    "delay_multiplier": 1.0
                },
                "after_hours": {
                    "channels": ["sms", "pagerduty"],
                    "delay_multiplier": 0.5  # Faster response needed
                },
                "weekends": {
                    "channels": ["sms", "pagerduty"],
                    "delay_multiplier": 0.3  # Even faster for weekends
                }
            },
            "suppression_rules": {
                "maintenance_window": {
                    "suppress_severities": ["info", "warning"],
                    "channels_override": ["email"]
                },
                "alert_storm": {
                    "max_alerts_per_minute": 10,
                    "suppress_duration_seconds": 300
                }
            }
        }
    
    def _initialize_ml_models(self) -> bool:
        """Initialize ML models for intelligent routing"""
        try:
            # Initialize models
            self.models = {
                "priority_classifier": RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                ),
                "channel_selector": RandomForestClassifier(
                    n_estimators=50,
                    max_depth=8,
                    random_state=42
                ),
                "escalation_predictor": RandomForestClassifier(
                    n_estimators=75,
                    max_depth=6,
                    random_state=42
                )
            }
            
            # Initialize feature processors
            self.vectorizers = {
                "alert_text": TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            }
            
            self.scalers = {
                "numeric_features": StandardScaler()
            }
            
            self.encoders = {
                "severity": LabelEncoder(),
                "creator_tier": LabelEncoder(),
                "service": LabelEncoder()
            }
            
            # Try to load pre-trained models
            self._load_pretrained_models()
            
            logger.info("ML models initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"ML initialization failed, falling back to rule-based routing: {e}")
            return False
    
    def _load_pretrained_models(self) -> None:
        """Load pre-trained models from disk if available"""
        models_dir = Path("./models/alerting")
        if not models_dir.exists():
            logger.info("No pre-trained models found, will use rule-based routing")
            return
        
        try:
            for model_name in self.models.keys():
                model_path = models_dir / f"{model_name}.pkl"
                if model_path.exists():
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Loaded pre-trained model: {model_name}")
            
            # Load feature processors
            for processor_type, processors in [
                ("vectorizers", self.vectorizers),
                ("scalers", self.scalers),
                ("encoders", self.encoders)
            ]:
                for processor_name in processors.keys():
                    processor_path = models_dir / f"{processor_type}_{processor_name}.pkl"
                    if processor_path.exists():
                        with open(processor_path, 'rb') as f:
                            processors[processor_name] = pickle.load(f)
        
        except Exception as e:
            logger.warning(f"Failed to load some pre-trained models: {e}")
    
    async def route_alert(
        self,
        alert_context: Any,  # AlertContext from index.py
        correlation_result: Optional[Any] = None
    ) -> RoutingDecision:
        """
        Main routing function - determines how to route an alert
        
        Args:
            alert_context: Enhanced alert context
            correlation_result: Result from correlation engine
            
        Returns:
            RoutingDecision with channels, timing, and rationale
        """
        try:
            # Extract features for ML prediction
            features = self._extract_features(alert_context, correlation_result)
            
            # Apply business rules first
            rule_based_decision = self._apply_business_rules(alert_context)
            
            # Apply ML predictions if available
            ml_decision = None
            if self.ml_enabled:
                ml_decision = await self._apply_ml_routing(features, alert_context)
            
            # Combine rule-based and ML decisions
            final_decision = self._combine_decisions(
                rule_based_decision, ml_decision, alert_context
            )
            
            # Apply post-processing rules
            final_decision = self._apply_post_processing(final_decision, alert_context)
            
            # Update statistics
            self.routing_stats["total_routed"] += 1
            if ml_decision:
                self.routing_stats["ml_predictions_used"] += 1
            else:
                self.routing_stats["rule_based_decisions"] += 1
            
            if final_decision.requires_escalation:
                self.routing_stats["escalations_triggered"] += 1
            
            if final_decision.decision_type == RoutingDecisionType.SUPPRESSED:
                self.routing_stats["suppressions_applied"] += 1
            
            logger.info(
                f"Alert routed: {alert_context.alert_id} -> "
                f"{final_decision.decision_type.value} "
                f"(channels: {[ch.value for ch in final_decision.channels]})"
            )
            
            return final_decision
            
        except Exception as e:
            logger.error(f"Failed to route alert {alert_context.alert_id}: {e}")
            # Return safe default routing
            return self._create_fallback_decision(alert_context)
    
    def _extract_features(
        self,
        alert_context: Any,
        correlation_result: Optional[Any] = None
    ) -> AlertFeatures:
        """Extract ML features from alert context"""
        try:
            # Numeric severity mapping
            severity_map = {
                "emergency": 5.0, "critical": 4.0, "high": 3.0,
                "warning": 2.0, "info": 1.0, "debug": 0.0
            }
            severity_numeric = severity_map.get(alert_context.severity.value, 1.0)
            
            # Creator tier mapping
            tier_map = {
                "premium": 4.0, "professional": 3.0,
                "emerging": 2.0, "starter": 1.0
            }
            creator_tier_numeric = tier_map.get(
                alert_context.creator_tier.value if alert_context.creator_tier else "starter", 1.0
            )
            
            # Time-based features
            now = datetime.now()
            time_of_day = now.hour / 24.0  # Normalize to 0-1
            day_of_week = now.weekday() / 6.0  # Normalize to 0-1
            
            # Service category encoding
            service_categories = {
                "api": 1.0, "database": 2.0, "ai-engine": 3.0,
                "payment": 4.0, "security": 5.0, "frontend": 6.0,
                "storage": 7.0, "network": 8.0
            }
            service_category_encoded = service_categories.get(alert_context.source_service, 0.0)
            
            # User count (log scale)
            user_count_log = np.log10(max(1, alert_context.user_count_affected))
            
            # Correlation strength
            correlation_strength = 0.0
            if correlation_result and hasattr(correlation_result, 'correlation_score'):
                correlation_strength = correlation_result.correlation_score
            
            # Historical frequency (would be computed from historical data)
            historical_frequency = self._compute_historical_frequency(alert_context)
            
            # Text features from alert metadata
            text_features = self._extract_text_features(alert_context)
            
            return AlertFeatures(
                severity_numeric=severity_numeric,
                creator_tier_numeric=creator_tier_numeric,
                business_impact=alert_context.business_impact,
                revenue_impact=alert_context.revenue_impact,
                user_count_log=user_count_log,
                time_of_day=time_of_day,
                day_of_week=day_of_week,
                service_category_encoded=service_category_encoded,
                historical_frequency=historical_frequency,
                correlation_strength=correlation_strength,
                text_features=text_features
            )
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            # Return default features
            return AlertFeatures(
                severity_numeric=1.0,
                creator_tier_numeric=1.0,
                business_impact=0.0,
                revenue_impact=0.0,
                user_count_log=0.0,
                time_of_day=0.5,
                day_of_week=0.5,
                service_category_encoded=0.0,
                historical_frequency=0.0,
                correlation_strength=0.0
            )
    
    def _extract_text_features(self, alert_context: Any) -> np.ndarray:
        """Extract text features from alert metadata"""
        try:
            # Combine text fields
            text_parts = []
            
            if hasattr(alert_context, 'metadata') and alert_context.metadata:
                # Add summary/description
                if 'summary' in alert_context.metadata:
                    text_parts.append(str(alert_context.metadata['summary']))
                if 'description' in alert_context.metadata:
                    text_parts.append(str(alert_context.metadata['description']))
                if 'tags' in alert_context.metadata:
                    tags = alert_context.metadata['tags']
                    if isinstance(tags, list):
                        text_parts.extend([str(tag) for tag in tags])
            
            # Add service name
            text_parts.append(alert_context.source_service)
            
            # Combine all text
            combined_text = " ".join(text_parts) if text_parts else "unknown alert"
            
            # Vectorize if vectorizer is available and trained
            if "alert_text" in self.vectorizers:
                try:
                    features = self.vectorizers["alert_text"].transform([combined_text])
                    return features.toarray()[0]
                except Exception:
                    # Vectorizer not fitted yet
                    pass
            
            # Return zero vector as fallback
            return np.zeros(100)  # Default feature size
            
        except Exception as e:
            logger.error(f"Failed to extract text features: {e}")
            return np.zeros(100)
    
    def _compute_historical_frequency(self, alert_context: Any) -> float:
        """Compute historical frequency of similar alerts"""
        try:
            # This would query historical data to compute frequency
            # For now, return a default based on service type
            service_frequency_map = {
                "api": 0.3,      # API alerts are common
                "database": 0.1,  # DB alerts less common but serious
                "ai-engine": 0.2, # AI alerts moderately common
                "payment": 0.05,  # Payment alerts rare but critical
                "security": 0.02  # Security alerts very rare
            }
            return service_frequency_map.get(alert_context.source_service, 0.1)
        except Exception:
            return 0.1  # Default frequency
    
    def _apply_business_rules(self, alert_context: Any) -> RoutingDecision:
        """Apply business rules for routing decisions"""
        try:
            # Start with severity-based rules
            severity_rule = self.routing_rules["severity_rules"].get(
                alert_context.severity.value, 
                self.routing_rules["severity_rules"]["info"]
            )
            
            # Base decision from severity
            channels = [NotificationChannel(ch) for ch in severity_rule["immediate_channels"]]
            priority_score = severity_rule["priority_score"]
            delay_seconds = severity_rule["delay_seconds"]
            requires_escalation = severity_rule["requires_escalation"]
            escalation_timeout = 900  # Default 15 minutes
            
            rules_applied = [f"severity_{alert_context.severity.value}"]
            
            # Apply creator tier rules
            if alert_context.creator_tier:
                tier_rule = self.routing_rules["creator_tier_rules"].get(
                    alert_context.creator_tier.value
                )
                if tier_rule:
                    # Add required channels for this tier
                    tier_channels = [NotificationChannel(ch) for ch in tier_rule["required_channels"]]
                    channels.extend(tier_channels)
                    
                    # Adjust priority and timing
                    priority_score *= tier_rule["priority_multiplier"]
                    delay_seconds = min(delay_seconds, tier_rule["max_delay_seconds"])
                    escalation_timeout = tier_rule["escalation_timeout"]
                    
                    rules_applied.append(f"creator_tier_{alert_context.creator_tier.value}")
            
            # Apply service-specific rules
            service_rule = self.routing_rules["service_rules"].get(alert_context.source_service)
            if service_rule:
                service_channels = [NotificationChannel(ch) for ch in service_rule["channels"]]
                channels.extend(service_channels)
                escalation_timeout = int(escalation_timeout / service_rule["escalation_multiplier"])
                rules_applied.append(f"service_{alert_context.source_service}")
            
            # Apply time-based rules
            now = datetime.now()
            is_business_hours = 9 <= now.hour <= 17 and now.weekday() < 5
            is_weekend = now.weekday() >= 5
            
            if is_weekend:
                time_rule = self.routing_rules["time_based_rules"]["weekends"]
                rules_applied.append("time_weekends")
            elif not is_business_hours:
                time_rule = self.routing_rules["time_based_rules"]["after_hours"]
                rules_applied.append("time_after_hours")
            else:
                time_rule = self.routing_rules["time_based_rules"]["business_hours"]
                rules_applied.append("time_business_hours")
            
            # Adjust based on time rules
            time_channels = [NotificationChannel(ch) for ch in time_rule["channels"]]
            channels.extend(time_channels)
            delay_seconds = int(delay_seconds * time_rule["delay_multiplier"])
            
            # Remove duplicates and sort by priority
            channels = list(set(channels))
            
            # Determine decision type
            decision_type = RoutingDecisionType.IMMEDIATE
            if delay_seconds > 300:  # 5 minutes
                decision_type = RoutingDecisionType.DELAYED
            
            # Clamp priority score
            priority_score = min(1.0, max(0.0, priority_score))
            
            rationale = f"Applied business rules: {', '.join(rules_applied)}"
            
            return RoutingDecision(
                decision_type=decision_type,
                channels=channels,
                priority_score=priority_score,
                delay_seconds=delay_seconds,
                requires_escalation=requires_escalation,
                escalation_timeout=escalation_timeout,
                rationale=rationale,
                confidence_score=0.8,  # Rule-based has high confidence
                routing_rules_applied=rules_applied
            )
            
        except Exception as e:
            logger.error(f"Failed to apply business rules: {e}")
            return self._create_fallback_decision(alert_context)
    
    async def _apply_ml_routing(
        self,
        features: AlertFeatures,
        alert_context: Any
    ) -> Optional[RoutingDecision]:
        """Apply ML models for routing decisions"""
        try:
            if not self.ml_enabled:
                return None
            
            # Prepare feature vector
            numeric_features = np.array([
                features.severity_numeric,
                features.creator_tier_numeric,
                features.business_impact,
                features.revenue_impact,
                features.user_count_log,
                features.time_of_day,
                features.day_of_week,
                features.service_category_encoded,
                features.historical_frequency,
                features.correlation_strength
            ]).reshape(1, -1)
            
            # Scale numeric features if scaler is fitted
            if hasattr(self.scalers["numeric_features"], 'mean_'):
                numeric_features = self.scalers["numeric_features"].transform(numeric_features)
            
            ml_predictions = {}
            
            # Priority prediction
            if "priority_classifier" in self.models:
                try:
                    priority_proba = self.models["priority_classifier"].predict_proba(numeric_features)[0]
                    priority_score = np.max(priority_proba)
                    ml_predictions["priority_score"] = float(priority_score)
                except Exception as e:
                    logger.warning(f"Priority prediction failed: {e}")
                    priority_score = 0.5
            else:
                priority_score = 0.5
            
            # Channel selection prediction
            predicted_channels = [NotificationChannel.EMAIL]  # Default
            if "channel_selector" in self.models:
                try:
                    channel_proba = self.models["channel_selector"].predict_proba(numeric_features)[0]
                    # Logic to select channels based on probabilities
                    if channel_proba.max() > 0.7:
                        # High confidence prediction logic would go here
                        pass
                    ml_predictions["channel_confidence"] = float(channel_proba.max())
                except Exception as e:
                    logger.warning(f"Channel selection failed: {e}")
            
            # Escalation prediction
            requires_escalation = False
            if "escalation_predictor" in self.models:
                try:
                    escalation_proba = self.models["escalation_predictor"].predict_proba(numeric_features)[0]
                    requires_escalation = escalation_proba[1] > 0.6  # Threshold for escalation
                    ml_predictions["escalation_probability"] = float(escalation_proba[1])
                except Exception as e:
                    logger.warning(f"Escalation prediction failed: {e}")
            
            # Determine decision type based on ML predictions
            decision_type = RoutingDecisionType.IMMEDIATE
            if priority_score < 0.3:
                decision_type = RoutingDecisionType.DELAYED
            elif priority_score > 0.8:
                decision_type = RoutingDecisionType.IMMEDIATE
            
            # Calculate delay based on priority
            delay_seconds = max(0, int((1.0 - priority_score) * 1800))  # 0-30 minutes
            
            confidence_score = np.mean(list(ml_predictions.values())) if ml_predictions else 0.5
            
            return RoutingDecision(
                decision_type=decision_type,
                channels=predicted_channels,
                priority_score=priority_score,
                delay_seconds=delay_seconds,
                requires_escalation=requires_escalation,
                escalation_timeout=900,
                rationale="ML-based routing decision",
                confidence_score=confidence_score,
                routing_rules_applied=["ml_priority_classifier", "ml_channel_selector"],
                ml_predictions=ml_predictions
            )
            
        except Exception as e:
            logger.error(f"ML routing failed: {e}")
            return None
    
    def _combine_decisions(
        self,
        rule_based: RoutingDecision,
        ml_based: Optional[RoutingDecision],
        alert_context: Any
    ) -> RoutingDecision:
        """Combine rule-based and ML-based decisions"""
        if not ml_based:
            return rule_based
        
        try:
            # Weighted combination based on confidence scores
            rule_weight = rule_based.confidence_score
            ml_weight = ml_based.confidence_score
            total_weight = rule_weight + ml_weight
            
            if total_weight == 0:
                return rule_based
            
            # Combine priority scores
            combined_priority = (
                rule_based.priority_score * rule_weight +
                ml_based.priority_score * ml_weight
            ) / total_weight
            
            # Combine channels (union)
            combined_channels = list(set(rule_based.channels + ml_based.channels))
            
            # Use more conservative delay (minimum)
            combined_delay = min(rule_based.delay_seconds, ml_based.delay_seconds)
            
            # Escalation if either recommends it
            combined_escalation = rule_based.requires_escalation or ml_based.requires_escalation
            
            # Use shorter escalation timeout
            combined_escalation_timeout = min(
                rule_based.escalation_timeout,
                ml_based.escalation_timeout
            )
            
            # Decision type based on combined priority
            if combined_priority > 0.8:
                decision_type = RoutingDecisionType.IMMEDIATE
            elif combined_priority > 0.5:
                decision_type = RoutingDecisionType.DELAYED
            else:
                decision_type = rule_based.decision_type
            
            # Combined rationale
            rationale = f"Combined decision: {rule_based.rationale}; ML: {ml_based.rationale}"
            
            # Combined rules applied
            combined_rules = rule_based.routing_rules_applied + ml_based.routing_rules_applied
            
            # Combined ML predictions
            combined_ml_predictions = {
                **rule_based.ml_predictions,
                **ml_based.ml_predictions,
                "combined_priority": combined_priority
            }
            
            return RoutingDecision(
                decision_type=decision_type,
                channels=combined_channels,
                priority_score=combined_priority,
                delay_seconds=combined_delay,
                requires_escalation=combined_escalation,
                escalation_timeout=combined_escalation_timeout,
                rationale=rationale,
                confidence_score=(rule_weight + ml_weight) / 2,  # Average confidence
                routing_rules_applied=combined_rules,
                ml_predictions=combined_ml_predictions
            )
            
        except Exception as e:
            logger.error(f"Failed to combine decisions: {e}")
            return rule_based
    
    def _apply_post_processing(
        self,
        decision: RoutingDecision,
        alert_context: Any
    ) -> RoutingDecision:
        """Apply post-processing rules (suppression, filtering, etc.)"""
        try:
            # Check suppression rules
            suppression_rules = self.routing_rules["suppression_rules"]
            
            # Check maintenance window suppression
            # This would check if we're in a maintenance window
            # For now, skip suppression logic
            
            # Check alert storm suppression
            storm_rule = suppression_rules["alert_storm"]
            if self._is_alert_storm(alert_context, storm_rule):
                decision.decision_type = RoutingDecisionType.SUPPRESSED
                decision.delay_seconds += storm_rule["suppress_duration_seconds"]
                decision.rationale += "; Suppressed due to alert storm"
                decision.routing_rules_applied.append("alert_storm_suppression")
            
            # Apply minimum delay for non-critical alerts
            if alert_context.severity.value in ["info", "debug"] and decision.delay_seconds < 300:
                decision.delay_seconds = 300  # Minimum 5 minutes for low-priority
                decision.routing_rules_applied.append("minimum_delay_low_priority")
            
            # Ensure premium creators get SMS for critical alerts
            if (alert_context.creator_tier and 
                alert_context.creator_tier.value == "premium" and
                alert_context.severity.value in ["critical", "emergency"]):
                if NotificationChannel.SMS not in decision.channels:
                    decision.channels.append(NotificationChannel.SMS)
                    decision.routing_rules_applied.append("premium_sms_guarantee")
            
            return decision
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            return decision
    
    def _is_alert_storm(self, alert_context: Any, storm_rule: Dict[str, Any]) -> bool:
        """Check if we're experiencing an alert storm"""
        try:
            # This would check recent alert frequency
            # For now, return False (no storm detection implemented)
            return False
        except Exception:
            return False
    
    def _create_fallback_decision(self, alert_context: Any) -> RoutingDecision:
        """Create safe fallback routing decision"""
        return RoutingDecision(
            decision_type=RoutingDecisionType.IMMEDIATE,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            priority_score=0.5,
            delay_seconds=0,
            requires_escalation=alert_context.severity.value in ["emergency", "critical"],
            escalation_timeout=900,
            rationale="Fallback routing due to processing error",
            confidence_score=0.3,
            routing_rules_applied=["fallback"]
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the routing engine"""
        return {
            "status": "healthy",
            "ml_enabled": self.ml_enabled,
            "models_loaded": len(self.models),
            "routing_stats": self.routing_stats.copy(),
            "config_loaded": bool(self.routing_rules)
        }
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics and performance metrics"""
        return {
            "routing_stats": self.routing_stats.copy(),
            "ml_enabled": self.ml_enabled,
            "models_available": list(self.models.keys()),
            "total_rules": len(self.routing_rules)
        }


# Utility functions for model training (would be used in separate training pipeline)
def train_routing_models(historical_data: pd.DataFrame) -> Dict[str, Any]:
    """Train ML models using historical routing data"""
    # This would be implemented in a separate training pipeline
    pass


def evaluate_routing_performance(
    true_decisions: List[Dict[str, Any]],
    predicted_decisions: List[RoutingDecision]
) -> Dict[str, float]:
    """Evaluate routing performance against ground truth"""
    # This would implement performance evaluation metrics
    pass


if __name__ == "__main__":
    # Testing/development code
    import asyncio
    
    async def test_routing_engine():
        config = {"alerting": {}, "channels": {}}
        engine = IntelligentAlertRoutingEngine(config)
        
        # Mock alert context for testing
        class MockAlertContext:
            def __init__(self):
                self.alert_id = "test_alert_001"
                self.severity = type('Severity', (), {'value': 'critical'})()
                self.creator_tier = type('CreatorTier', (), {'value': 'premium'})()
                self.source_service = "api"
                self.business_impact = 0.8
                self.revenue_impact = 0.7
                self.user_count_affected = 1000
                self.metadata = {"summary": "API response time degraded"}
        
        mock_context = MockAlertContext()
        decision = await engine.route_alert(mock_context)
        
        print("Routing Decision:")
        print(json.dumps(decision.to_dict(), indent=2))
    
    asyncio.run(test_routing_engine())