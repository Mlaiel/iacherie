#!/usr/bin/env python3
"""
Alert Correlation Intelligence - Smart Alert Correlation and Root Cause Analysis
===============================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - All Rights Reserved

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie - AI-Powered Creator Economy Platform
Module: Alert Correlation Intelligence Engine
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import networkx as nx

logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of alert correlations"""
    CAUSAL = "causal"                    # One alert causes another
    TEMPORAL = "temporal"                # Alerts occurring in sequence
    SPATIAL = "spatial"                  # Alerts from related services/components
    PATTERN = "pattern"                  # Alerts following known patterns
    STORM = "storm"                      # Alert storm detection
    DEPENDENCY = "dependency"            # Service dependency correlation
    USER_JOURNEY = "user_journey"        # Creator journey impact correlation


class CorrelationStrength(Enum):
    """Correlation strength levels"""
    VERY_HIGH = "very_high"      # > 0.9
    HIGH = "high"                # 0.7 - 0.9
    MEDIUM = "medium"            # 0.5 - 0.7
    LOW = "low"                  # 0.3 - 0.5
    VERY_LOW = "very_low"        # < 0.3


@dataclass
class CorrelationRule:
    """Rule for correlating alerts"""
    rule_id: str
    name: str
    correlation_type: CorrelationType
    source_patterns: List[str]  # Service/alert patterns to match
    target_patterns: List[str]  # Related patterns to correlate
    time_window_seconds: int
    strength_threshold: float
    confidence_threshold: float
    creator_context_aware: bool = True
    enabled: bool = True


@dataclass
class AlertNode:
    """Node in the correlation graph"""
    alert_id: str
    timestamp: datetime
    service: str
    severity: str
    creator_id: Optional[str] = None
    creator_tier: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_fingerprint: str = ""


@dataclass
class CorrelationEdge:
    """Edge connecting correlated alerts"""
    source_alert_id: str
    target_alert_id: str
    correlation_type: CorrelationType
    strength: float
    confidence: float
    time_delta_seconds: int
    rationale: str


@dataclass
class CorrelationCluster:
    """Cluster of correlated alerts"""
    cluster_id: str
    alerts: List[AlertNode]
    root_cause_candidates: List[str]
    correlation_score: float
    cluster_type: CorrelationType
    impact_assessment: Dict[str, Any]
    creation_time: datetime
    last_updated: datetime


@dataclass
class CorrelationResult:
    """Result of correlation analysis"""
    correlation_id: str
    primary_alert_id: str
    correlated_alerts: List[str]
    correlation_type: CorrelationType
    correlation_score: float
    confidence_level: float
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[str]
    suppression_recommendations: List[str]
    escalation_priority: float
    creator_impact_correlation: Dict[str, Any]
    rationale: str


class AlertCorrelationIntelligence:
    """
    Intelligent Alert Correlation Engine for Creator Economy
    
    Features:
    - Cross-service alert correlation
    - Root cause analysis automation
    - Alert storm detection and grouping
    - Creator journey impact correlation
    - Dependency-based alert linking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the correlation engine"""
        self.config = config
        self.correlation_rules = self._initialize_correlation_rules()
        self.correlation_graph = nx.DiGraph()
        self.alert_buffer = deque(maxlen=10000)  # Keep recent alerts for correlation
        self.correlation_clusters = {}
        self.service_dependency_graph = self._build_service_dependency_graph()
        self.creator_journey_patterns = self._load_creator_journey_patterns()
        
        # Performance tracking
        self.correlation_stats = {
            "total_alerts_processed": 0,
            "correlations_found": 0,
            "clusters_created": 0,
            "root_causes_identified": 0,
            "alert_storms_detected": 0
        }
        
        logger.info("Alert Correlation Intelligence initialized")
    
    def _initialize_correlation_rules(self) -> List[CorrelationRule]:
        """Initialize correlation rules for different scenarios"""
        return [
            # Database-API correlation
            CorrelationRule(
                rule_id="db_api_correlation",
                name="Database to API Impact Correlation",
                correlation_type=CorrelationType.CAUSAL,
                source_patterns=["database", "postgresql", "mysql", "mongodb"],
                target_patterns=["api", "backend", "web-service"],
                time_window_seconds=300,  # 5 minutes
                strength_threshold=0.7,
                confidence_threshold=0.8,
                creator_context_aware=True
            ),
            
            # AI Engine correlation
            CorrelationRule(
                rule_id="ai_engine_correlation",
                name="AI Engine Processing Correlation",
                correlation_type=CorrelationType.CAUSAL,
                source_patterns=["ai-engine", "ml-service", "gpu-cluster"],
                target_patterns=["content-processing", "generation-api", "media-pipeline"],
                time_window_seconds=600,  # 10 minutes
                strength_threshold=0.6,
                confidence_threshold=0.7,
                creator_context_aware=True
            ),
            
            # Payment system correlation
            CorrelationRule(
                rule_id="payment_correlation",
                name="Payment System Impact Correlation",
                correlation_type=CorrelationType.CAUSAL,
                source_patterns=["payment", "billing", "stripe", "paypal"],
                target_patterns=["monetization", "creator-earnings", "payout"],
                time_window_seconds=180,  # 3 minutes
                strength_threshold=0.8,
                confidence_threshold=0.9,
                creator_context_aware=True
            ),
            
            # Security incident correlation
            CorrelationRule(
                rule_id="security_correlation",
                name="Security Incident Correlation",
                correlation_type=CorrelationType.PATTERN,
                source_patterns=["security", "auth", "firewall", "intrusion"],
                target_patterns=["access-denied", "suspicious-activity", "rate-limit"],
                time_window_seconds=900,  # 15 minutes
                strength_threshold=0.7,
                confidence_threshold=0.8,
                creator_context_aware=True
            ),
            
            # Infrastructure correlation
            CorrelationRule(
                rule_id="infrastructure_correlation",
                name="Infrastructure Component Correlation",
                correlation_type=CorrelationType.DEPENDENCY,
                source_patterns=["kubernetes", "docker", "load-balancer", "cdn"],
                target_patterns=["api", "frontend", "media-delivery"],
                time_window_seconds=300,
                strength_threshold=0.6,
                confidence_threshold=0.7,
                creator_context_aware=False
            ),
            
            # Alert storm detection
            CorrelationRule(
                rule_id="alert_storm_detection",
                name="Alert Storm Pattern Detection",
                correlation_type=CorrelationType.STORM,
                source_patterns=["*"],  # Any service
                target_patterns=["*"],  # Any service
                time_window_seconds=60,   # 1 minute
                strength_threshold=0.8,
                confidence_threshold=0.9,
                creator_context_aware=False
            ),
            
            # Creator journey correlation
            CorrelationRule(
                rule_id="creator_journey_correlation",
                name="Creator Journey Impact Correlation",
                correlation_type=CorrelationType.USER_JOURNEY,
                source_patterns=["upload", "processing", "publishing", "analytics"],
                target_patterns=["content-creation", "engagement", "monetization"],
                time_window_seconds=1800,  # 30 minutes
                strength_threshold=0.5,
                confidence_threshold=0.6,
                creator_context_aware=True
            )
        ]
    
    def _build_service_dependency_graph(self) -> nx.DiGraph:
        """Build service dependency graph for correlation"""
        graph = nx.DiGraph()
        
        # Define service dependencies for IA Chérie platform
        dependencies = {
            # Core services
            "api": ["database", "redis", "auth-service"],
            "frontend": ["api", "cdn", "media-service"],
            "database": ["storage", "backup-service"],
            
            # Creator-specific services
            "ai-engine": ["gpu-cluster", "model-storage", "queue-service"],
            "content-processing": ["ai-engine", "media-storage", "transcoding"],
            "media-service": ["storage", "cdn", "transcoding-service"],
            
            # Monetization services
            "payment": ["billing-service", "fraud-detection", "accounting"],
            "creator-earnings": ["payment", "analytics", "tax-service"],
            "subscription-service": ["payment", "user-management", "billing"],
            
            # Analytics and insights
            "analytics": ["database", "data-warehouse", "ml-pipeline"],
            "reporting": ["analytics", "data-processing", "visualization"],
            
            # Security services
            "auth-service": ["user-db", "session-store", "oauth-provider"],
            "security-monitoring": ["log-aggregator", "threat-detection", "firewall"],
            
            # Infrastructure
            "load-balancer": ["api-servers", "health-checker"],
            "cdn": ["origin-servers", "edge-cache"],
            "monitoring": ["prometheus", "grafana", "alertmanager"]
        }
        
        # Add nodes and edges
        for service, deps in dependencies.items():
            graph.add_node(service)
            for dep in deps:
                graph.add_node(dep)
                graph.add_edge(dep, service)  # Dependency points to dependent
        
        return graph
    
    def _load_creator_journey_patterns(self) -> Dict[str, List[str]]:
        """Load Creator journey patterns for correlation"""
        return {
            "content_creation_flow": [
                "content-upload", "ai-processing", "quality-check", 
                "metadata-extraction", "thumbnail-generation", "publishing"
            ],
            "monetization_flow": [
                "content-view", "engagement-tracking", "ad-placement",
                "revenue-calculation", "payment-processing", "payout"
            ],
            "collaboration_flow": [
                "invitation-sent", "collaboration-accepted", "shared-workspace",
                "joint-creation", "revenue-sharing", "performance-tracking"
            ],
            "analytics_flow": [
                "data-collection", "metrics-processing", "insight-generation",
                "report-creation", "dashboard-update", "notification"
            ]
        }
    
    async def correlate_alert(self, alert_context: Any) -> Optional[CorrelationResult]:
        """
        Main correlation function - finds related alerts and patterns
        
        Args:
            alert_context: Alert context from orchestrator
            
        Returns:
            CorrelationResult if correlations found, None otherwise
        """
        try:
            # Add alert to buffer and graph
            alert_node = self._create_alert_node(alert_context)
            self._add_alert_to_buffer(alert_node)
            
            # Find correlations using different methods
            correlations = []
            
            # 1. Rule-based correlation
            rule_correlations = await self._find_rule_based_correlations(alert_node)
            correlations.extend(rule_correlations)
            
            # 2. Dependency-based correlation
            dependency_correlations = await self._find_dependency_correlations(alert_node)
            correlations.extend(dependency_correlations)
            
            # 3. Pattern-based correlation
            pattern_correlations = await self._find_pattern_correlations(alert_node)
            correlations.extend(pattern_correlations)
            
            # 4. Creator journey correlation
            if alert_node.creator_id:
                journey_correlations = await self._find_creator_journey_correlations(alert_node)
                correlations.extend(journey_correlations)
            
            # 5. Alert storm detection
            storm_correlation = await self._detect_alert_storm(alert_node)
            if storm_correlation:
                correlations.append(storm_correlation)
            
            # Process correlations and create result
            if correlations:
                result = await self._process_correlations(alert_node, correlations)
                
                # Update statistics
                self.correlation_stats["correlations_found"] += 1
                if result.root_cause_analysis.get("root_cause_identified"):
                    self.correlation_stats["root_causes_identified"] += 1
                
                logger.info(
                    f"Alert correlation found: {alert_context.alert_id} -> "
                    f"{len(result.correlated_alerts)} related alerts, "
                    f"confidence: {result.confidence_level:.2f}"
                )
                
                return result
            
            # Update statistics
            self.correlation_stats["total_alerts_processed"] += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to correlate alert {alert_context.alert_id}: {e}")
            return None
    
    def _create_alert_node(self, alert_context: Any) -> AlertNode:
        """Create alert node from alert context"""
        # Create correlation fingerprint for similar alerts
        fingerprint_data = {
            "service": alert_context.source_service,
            "severity": alert_context.severity.value,
            "creator_tier": alert_context.creator_tier.value if alert_context.creator_tier else None
        }
        
        if hasattr(alert_context, 'metadata') and alert_context.metadata:
            if 'summary' in alert_context.metadata:
                fingerprint_data["summary"] = alert_context.metadata['summary']
            if 'error_type' in alert_context.metadata:
                fingerprint_data["error_type"] = alert_context.metadata['error_type']
        
        fingerprint = hashlib.md5(
            json.dumps(fingerprint_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        return AlertNode(
            alert_id=alert_context.alert_id,
            timestamp=alert_context.timestamp,
            service=alert_context.source_service,
            severity=alert_context.severity.value,
            creator_id=alert_context.creator_id,
            creator_tier=alert_context.creator_tier.value if alert_context.creator_tier else None,
            metadata=getattr(alert_context, 'metadata', {}),
            correlation_fingerprint=fingerprint
        )
    
    def _add_alert_to_buffer(self, alert_node: AlertNode) -> None:
        """Add alert to correlation buffer and graph"""
        self.alert_buffer.append(alert_node)
        self.correlation_graph.add_node(
            alert_node.alert_id,
            **alert_node.__dict__
        )
    
    async def _find_rule_based_correlations(self, alert_node: AlertNode) -> List[CorrelationEdge]:
        """Find correlations based on predefined rules"""
        correlations = []
        
        try:
            for rule in self.correlation_rules:
                if not rule.enabled:
                    continue
                
                # Check if alert matches source patterns
                if not self._matches_patterns(alert_node.service, rule.source_patterns):
                    continue
                
                # Look for alerts in time window that match target patterns
                time_window_start = alert_node.timestamp - timedelta(seconds=rule.time_window_seconds)
                
                for buffered_alert in self.alert_buffer:
                    if buffered_alert.alert_id == alert_node.alert_id:
                        continue
                    
                    if buffered_alert.timestamp < time_window_start:
                        continue
                    
                    if not self._matches_patterns(buffered_alert.service, rule.target_patterns):
                        continue
                    
                    # Calculate correlation strength
                    strength = self._calculate_correlation_strength(
                        alert_node, buffered_alert, rule
                    )
                    
                    if strength >= rule.strength_threshold:
                        time_delta = int((alert_node.timestamp - buffered_alert.timestamp).total_seconds())
                        
                        correlation = CorrelationEdge(
                            source_alert_id=buffered_alert.alert_id,
                            target_alert_id=alert_node.alert_id,
                            correlation_type=rule.correlation_type,
                            strength=strength,
                            confidence=min(1.0, strength * 1.1),  # Confidence slightly higher than strength
                            time_delta_seconds=time_delta,
                            rationale=f"Rule-based correlation: {rule.name}"
                        )
                        
                        correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Rule-based correlation failed: {e}")
            return []
    
    async def _find_dependency_correlations(self, alert_node: AlertNode) -> List[CorrelationEdge]:
        """Find correlations based on service dependencies"""
        correlations = []
        
        try:
            if alert_node.service not in self.service_dependency_graph:
                return correlations
            
            # Find upstream dependencies (services this service depends on)
            upstream_services = list(self.service_dependency_graph.predecessors(alert_node.service))
            
            # Find downstream dependents (services that depend on this service)
            downstream_services = list(self.service_dependency_graph.successors(alert_node.service))
            
            # Look for alerts from dependency services in time window
            time_window = timedelta(minutes=10)  # 10 minute window for dependency correlation
            time_window_start = alert_node.timestamp - time_window
            time_window_end = alert_node.timestamp + time_window
            
            for buffered_alert in self.alert_buffer:
                if buffered_alert.alert_id == alert_node.alert_id:
                    continue
                
                if not (time_window_start <= buffered_alert.timestamp <= time_window_end):
                    continue
                
                correlation_strength = 0.0
                correlation_type = CorrelationType.DEPENDENCY
                rationale = ""
                
                # Check upstream correlation (dependency failure causing this alert)
                if buffered_alert.service in upstream_services:
                    correlation_strength = 0.8
                    rationale = f"Upstream dependency: {buffered_alert.service} affects {alert_node.service}"
                
                # Check downstream correlation (this alert affecting dependent services)
                elif buffered_alert.service in downstream_services:
                    correlation_strength = 0.7
                    rationale = f"Downstream impact: {alert_node.service} affects {buffered_alert.service}"
                
                if correlation_strength > 0:
                    time_delta = int((alert_node.timestamp - buffered_alert.timestamp).total_seconds())
                    
                    correlation = CorrelationEdge(
                        source_alert_id=buffered_alert.alert_id,
                        target_alert_id=alert_node.alert_id,
                        correlation_type=correlation_type,
                        strength=correlation_strength,
                        confidence=correlation_strength,
                        time_delta_seconds=time_delta,
                        rationale=rationale
                    )
                    
                    correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Dependency correlation failed: {e}")
            return []
    
    async def _find_pattern_correlations(self, alert_node: AlertNode) -> List[CorrelationEdge]:
        """Find correlations based on historical patterns"""
        correlations = []
        
        try:
            # Look for alerts with similar fingerprints
            similar_threshold = 0.7
            time_window = timedelta(hours=1)  # Look back 1 hour
            time_window_start = alert_node.timestamp - time_window
            
            fingerprint_matches = []
            
            for buffered_alert in self.alert_buffer:
                if buffered_alert.alert_id == alert_node.alert_id:
                    continue
                
                if buffered_alert.timestamp < time_window_start:
                    continue
                
                # Calculate fingerprint similarity
                similarity = self._calculate_fingerprint_similarity(
                    alert_node.correlation_fingerprint,
                    buffered_alert.correlation_fingerprint
                )
                
                if similarity >= similar_threshold:
                    fingerprint_matches.append((buffered_alert, similarity))
            
            # Create correlations for similar alerts
            for buffered_alert, similarity in fingerprint_matches:
                time_delta = int((alert_node.timestamp - buffered_alert.timestamp).total_seconds())
                
                correlation = CorrelationEdge(
                    source_alert_id=buffered_alert.alert_id,
                    target_alert_id=alert_node.alert_id,
                    correlation_type=CorrelationType.PATTERN,
                    strength=similarity,
                    confidence=similarity * 0.9,  # Slightly lower confidence for pattern matching
                    time_delta_seconds=time_delta,
                    rationale=f"Pattern similarity: {similarity:.2f}"
                )
                
                correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Pattern correlation failed: {e}")
            return []
    
    async def _find_creator_journey_correlations(self, alert_node: AlertNode) -> List[CorrelationEdge]:
        """Find correlations based on Creator journey patterns"""
        correlations = []
        
        try:
            if not alert_node.creator_id:
                return correlations
            
            # Look for alerts from the same creator in journey patterns
            time_window = timedelta(minutes=30)  # 30 minute journey window
            time_window_start = alert_node.timestamp - time_window
            
            creator_alerts = [
                alert for alert in self.alert_buffer
                if (alert.creator_id == alert_node.creator_id and
                    alert.alert_id != alert_node.alert_id and
                    alert.timestamp >= time_window_start)
            ]
            
            # Check journey patterns
            for pattern_name, pattern_steps in self.creator_journey_patterns.items():
                journey_correlations = self._find_journey_pattern_correlations(
                    alert_node, creator_alerts, pattern_steps
                )
                correlations.extend(journey_correlations)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Creator journey correlation failed: {e}")
            return []
    
    def _find_journey_pattern_correlations(
        self,
        alert_node: AlertNode,
        creator_alerts: List[AlertNode],
        pattern_steps: List[str]
    ) -> List[CorrelationEdge]:
        """Find correlations within a specific journey pattern"""
        correlations = []
        
        try:
            # Find which step in the pattern this alert represents
            current_step_index = None
            for i, step in enumerate(pattern_steps):
                if step in alert_node.service or any(keyword in alert_node.service for keyword in step.split('-')):
                    current_step_index = i
                    break
            
            if current_step_index is None:
                return correlations
            
            # Look for alerts from previous or next steps
            for other_alert in creator_alerts:
                other_step_index = None
                for i, step in enumerate(pattern_steps):
                    if step in other_alert.service or any(keyword in other_alert.service for keyword in step.split('-')):
                        other_step_index = i
                        break
                
                if other_step_index is None:
                    continue
                
                # Calculate journey correlation strength
                step_distance = abs(current_step_index - other_step_index)
                if step_distance <= 2:  # Only correlate nearby steps
                    strength = max(0.3, 1.0 - (step_distance * 0.2))
                    
                    time_delta = int((alert_node.timestamp - other_alert.timestamp).total_seconds())
                    
                    correlation = CorrelationEdge(
                        source_alert_id=other_alert.alert_id,
                        target_alert_id=alert_node.alert_id,
                        correlation_type=CorrelationType.USER_JOURNEY,
                        strength=strength,
                        confidence=strength * 0.8,
                        time_delta_seconds=time_delta,
                        rationale=f"Creator journey correlation: steps {other_step_index} -> {current_step_index}"
                    )
                    
                    correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Journey pattern correlation failed: {e}")
            return []
    
    async def _detect_alert_storm(self, alert_node: AlertNode) -> Optional[CorrelationEdge]:
        """Detect if this alert is part of an alert storm"""
        try:
            # Count alerts in the last minute
            one_minute_ago = alert_node.timestamp - timedelta(minutes=1)
            recent_alerts = [
                alert for alert in self.alert_buffer
                if alert.timestamp >= one_minute_ago
            ]
            
            # Alert storm threshold: more than 10 alerts per minute
            storm_threshold = 10
            
            if len(recent_alerts) >= storm_threshold:
                # Check if alerts are from related services
                services = set(alert.service for alert in recent_alerts)
                
                # Calculate storm correlation strength
                storm_strength = min(1.0, len(recent_alerts) / (storm_threshold * 2))
                
                # Find the earliest alert in the storm as the potential root cause
                earliest_alert = min(recent_alerts, key=lambda a: a.timestamp)
                
                if earliest_alert.alert_id != alert_node.alert_id:
                    self.correlation_stats["alert_storms_detected"] += 1
                    
                    return CorrelationEdge(
                        source_alert_id=earliest_alert.alert_id,
                        target_alert_id=alert_node.alert_id,
                        correlation_type=CorrelationType.STORM,
                        strength=storm_strength,
                        confidence=0.9,
                        time_delta_seconds=int((alert_node.timestamp - earliest_alert.timestamp).total_seconds()),
                        rationale=f"Alert storm detected: {len(recent_alerts)} alerts in 1 minute across {len(services)} services"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Alert storm detection failed: {e}")
            return None
    
    def _matches_patterns(self, service: str, patterns: List[str]) -> bool:
        """Check if service matches any of the patterns"""
        if "*" in patterns:
            return True
        
        service_lower = service.lower()
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in service_lower or service_lower in pattern_lower:
                return True
        
        return False
    
    def _calculate_correlation_strength(
        self,
        alert1: AlertNode,
        alert2: AlertNode,
        rule: CorrelationRule
    ) -> float:
        """Calculate correlation strength between two alerts"""
        try:
            strength_factors = []
            
            # Time proximity factor
            time_delta = abs((alert1.timestamp - alert2.timestamp).total_seconds())
            time_factor = max(0.1, 1.0 - (time_delta / rule.time_window_seconds))
            strength_factors.append(time_factor)
            
            # Severity correlation factor
            severity_weights = {"emergency": 5, "critical": 4, "high": 3, "warning": 2, "info": 1}
            sev1 = severity_weights.get(alert1.severity, 1)
            sev2 = severity_weights.get(alert2.severity, 1)
            severity_factor = 1.0 - abs(sev1 - sev2) / 5.0
            strength_factors.append(severity_factor)
            
            # Creator context factor (if rule is creator-aware)
            if rule.creator_context_aware and alert1.creator_id and alert2.creator_id:
                if alert1.creator_id == alert2.creator_id:
                    strength_factors.append(1.0)  # Same creator
                elif alert1.creator_tier == alert2.creator_tier:
                    strength_factors.append(0.7)  # Same tier
                else:
                    strength_factors.append(0.3)  # Different creators/tiers
            else:
                strength_factors.append(0.6)  # Default creator factor
            
            # Service similarity factor
            if alert1.service == alert2.service:
                strength_factors.append(1.0)
            else:
                # Check if services are in same category
                service_categories = {
                    "backend": ["api", "backend", "web-service"],
                    "data": ["database", "postgresql", "mysql", "mongodb", "redis"],
                    "ai": ["ai-engine", "ml-service", "gpu-cluster"],
                    "media": ["media-service", "transcoding", "storage"],
                    "payment": ["payment", "billing", "stripe", "paypal"]
                }
                
                category_factor = 0.3  # Default
                for category, services in service_categories.items():
                    if alert1.service in services and alert2.service in services:
                        category_factor = 0.7
                        break
                
                strength_factors.append(category_factor)
            
            # Calculate weighted average
            correlation_strength = np.mean(strength_factors)
            
            return min(1.0, max(0.0, correlation_strength))
            
        except Exception as e:
            logger.error(f"Failed to calculate correlation strength: {e}")
            return 0.0
    
    def _calculate_fingerprint_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between two correlation fingerprints"""
        try:
            # Simple Hamming distance for hex fingerprints
            if len(fingerprint1) != len(fingerprint2):
                return 0.0
            
            matches = sum(c1 == c2 for c1, c2 in zip(fingerprint1, fingerprint2))
            similarity = matches / len(fingerprint1)
            
            return similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate fingerprint similarity: {e}")
            return 0.0
    
    async def _process_correlations(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge]
    ) -> CorrelationResult:
        """Process correlations and create comprehensive result"""
        try:
            # Sort correlations by strength
            correlations.sort(key=lambda c: c.strength, reverse=True)
            
            # Generate correlation ID
            correlation_id = f"corr_{alert_node.alert_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract correlated alert IDs
            correlated_alerts = list(set([c.source_alert_id for c in correlations]))
            
            # Determine primary correlation type
            correlation_types = [c.correlation_type for c in correlations]
            primary_correlation_type = max(set(correlation_types), key=correlation_types.count)
            
            # Calculate overall correlation score
            correlation_score = np.mean([c.strength for c in correlations]) if correlations else 0.0
            
            # Calculate confidence level
            confidence_level = np.mean([c.confidence for c in correlations]) if correlations else 0.0
            
            # Perform root cause analysis
            root_cause_analysis = await self._perform_root_cause_analysis(
                alert_node, correlations
            )
            
            # Generate recommendations
            recommended_actions = self._generate_recommended_actions(
                alert_node, correlations, root_cause_analysis
            )
            
            suppression_recommendations = self._generate_suppression_recommendations(
                alert_node, correlations
            )
            
            # Calculate escalation priority
            escalation_priority = self._calculate_escalation_priority(
                alert_node, correlations, root_cause_analysis
            )
            
            # Analyze Creator impact correlation
            creator_impact_correlation = self._analyze_creator_impact_correlation(
                alert_node, correlations
            )
            
            # Generate rationale
            rationale = self._generate_correlation_rationale(
                alert_node, correlations, primary_correlation_type
            )
            
            return CorrelationResult(
                correlation_id=correlation_id,
                primary_alert_id=alert_node.alert_id,
                correlated_alerts=correlated_alerts,
                correlation_type=primary_correlation_type,
                correlation_score=correlation_score,
                confidence_level=confidence_level,
                root_cause_analysis=root_cause_analysis,
                recommended_actions=recommended_actions,
                suppression_recommendations=suppression_recommendations,
                escalation_priority=escalation_priority,
                creator_impact_correlation=creator_impact_correlation,
                rationale=rationale
            )
            
        except Exception as e:
            logger.error(f"Failed to process correlations: {e}")
            # Return basic result
            return CorrelationResult(
                correlation_id=f"corr_{alert_node.alert_id}_error",
                primary_alert_id=alert_node.alert_id,
                correlated_alerts=[],
                correlation_type=CorrelationType.PATTERN,
                correlation_score=0.0,
                confidence_level=0.0,
                root_cause_analysis={"error": str(e)},
                recommended_actions=["Manual investigation required"],
                suppression_recommendations=[],
                escalation_priority=0.5,
                creator_impact_correlation={},
                rationale="Correlation processing failed"
            )
    
    async def _perform_root_cause_analysis(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge]
    ) -> Dict[str, Any]:
        """Perform automated root cause analysis"""
        try:
            root_cause_analysis = {
                "root_cause_identified": False,
                "confidence": 0.0,
                "candidate_alerts": [],
                "analysis_method": "correlation_based",
                "contributing_factors": []
            }
            
            if not correlations:
                return root_cause_analysis
            
            # Find potential root cause alerts (earliest with high correlation)
            causal_correlations = [c for c in correlations if c.correlation_type == CorrelationType.CAUSAL]
            dependency_correlations = [c for c in correlations if c.correlation_type == CorrelationType.DEPENDENCY]
            
            candidates = []
            
            # Prioritize causal correlations
            for correlation in causal_correlations:
                if correlation.strength > 0.7:
                    candidates.append({
                        "alert_id": correlation.source_alert_id,
                        "confidence": correlation.strength,
                        "reason": "Causal correlation detected",
                        "time_delta": correlation.time_delta_seconds
                    })
            
            # Add dependency-based candidates
            for correlation in dependency_correlations:
                if correlation.strength > 0.6:
                    candidates.append({
                        "alert_id": correlation.source_alert_id,
                        "confidence": correlation.strength * 0.9,  # Slightly lower confidence
                        "reason": "Dependency relationship",
                        "time_delta": correlation.time_delta_seconds
                    })
            
            # Sort candidates by confidence and time (earlier = more likely root cause)
            candidates.sort(key=lambda c: (c["confidence"], -c["time_delta"]), reverse=True)
            
            if candidates:
                root_cause_analysis.update({
                    "root_cause_identified": True,
                    "confidence": candidates[0]["confidence"],
                    "candidate_alerts": candidates[:3],  # Top 3 candidates
                    "primary_root_cause": candidates[0]["alert_id"]
                })
            
            # Identify contributing factors
            contributing_factors = []
            
            # Service dependency factors
            if alert_node.service in self.service_dependency_graph:
                upstream_count = len(list(self.service_dependency_graph.predecessors(alert_node.service)))
                if upstream_count > 0:
                    contributing_factors.append(f"Service has {upstream_count} dependencies")
            
            # Time-based factors
            hour = alert_node.timestamp.hour
            if 9 <= hour <= 17:
                contributing_factors.append("Occurred during business hours (high impact)")
            elif 22 <= hour or hour <= 6:
                contributing_factors.append("Occurred during off-hours (delayed detection possible)")
            
            # Creator-specific factors
            if alert_node.creator_tier == "premium":
                contributing_factors.append("Affects premium Creator (high priority)")
            
            root_cause_analysis["contributing_factors"] = contributing_factors
            
            return root_cause_analysis
            
        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return {"error": str(e), "root_cause_identified": False}
    
    def _generate_recommended_actions(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge],
        root_cause_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommended actions based on correlation analysis"""
        actions = []
        
        try:
            # Root cause based actions
            if root_cause_analysis.get("root_cause_identified"):
                actions.append(f"Investigate root cause alert: {root_cause_analysis.get('primary_root_cause')}")
                actions.append("Focus resolution efforts on root cause rather than symptoms")
            
            # Correlation type specific actions
            correlation_types = [c.correlation_type for c in correlations]
            
            if CorrelationType.STORM in correlation_types:
                actions.append("Implement alert suppression to reduce noise")
                actions.append("Investigate system-wide issue causing alert storm")
            
            if CorrelationType.DEPENDENCY in correlation_types:
                actions.append("Check service dependency health")
                actions.append("Consider circuit breaker activation if appropriate")
            
            if CorrelationType.USER_JOURNEY in correlation_types:
                actions.append("Review Creator journey for bottlenecks")
                actions.append("Consider Creator communication about service impact")
            
            if CorrelationType.CAUSAL in correlation_types:
                actions.append("Address upstream service issues first")
                actions.append("Monitor downstream services for cascading effects")
            
            # Service-specific actions
            service_actions = {
                "database": ["Check database performance metrics", "Review recent queries", "Verify backup status"],
                "api": ["Check API response times", "Review rate limiting", "Verify authentication service"],
                "ai-engine": ["Check GPU utilization", "Review model performance", "Verify queue status"],
                "payment": ["Verify payment processor status", "Check transaction logs", "Review fraud detection"],
                "security": ["Review security logs", "Check for intrusion attempts", "Verify firewall rules"]
            }
            
            if alert_node.service in service_actions:
                actions.extend(service_actions[alert_node.service])
            
            # Creator tier specific actions
            if alert_node.creator_tier == "premium":
                actions.append("Provide premium Creator with direct support")
                actions.append("Consider compensatory measures if appropriate")
            
            return actions[:10]  # Limit to top 10 actions
            
        except Exception as e:
            logger.error(f"Failed to generate recommended actions: {e}")
            return ["Manual investigation required"]
    
    def _generate_suppression_recommendations(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge]
    ) -> List[str]:
        """Generate alert suppression recommendations"""
        suppressions = []
        
        try:
            # Storm suppression
            storm_correlations = [c for c in correlations if c.correlation_type == CorrelationType.STORM]
            if storm_correlations:
                suppressions.append("Suppress similar alerts for 15 minutes to reduce storm")
                suppressions.append("Group related alerts into single notification")
            
            # Dependency suppression
            dependency_correlations = [c for c in correlations if c.correlation_type == CorrelationType.DEPENDENCY]
            if dependency_correlations:
                suppressions.append("Suppress downstream dependency alerts while root cause is active")
                suppressions.append("Focus notifications on upstream service issues")
            
            # Pattern suppression
            pattern_correlations = [c for c in correlations if c.correlation_type == CorrelationType.PATTERN]
            if len(pattern_correlations) > 3:  # Many similar alerts
                suppressions.append("Suppress duplicate pattern alerts for 30 minutes")
                suppressions.append("Consolidate similar alerts into summary notification")
            
            return suppressions
            
        except Exception as e:
            logger.error(f"Failed to generate suppression recommendations: {e}")
            return []
    
    def _calculate_escalation_priority(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge],
        root_cause_analysis: Dict[str, Any]
    ) -> float:
        """Calculate escalation priority based on correlation analysis"""
        try:
            priority_factors = []
            
            # Base priority from alert severity
            severity_priorities = {"emergency": 1.0, "critical": 0.9, "high": 0.7, "warning": 0.5, "info": 0.3}
            base_priority = severity_priorities.get(alert_node.severity, 0.5)
            priority_factors.append(base_priority)
            
            # Root cause factor
            if root_cause_analysis.get("root_cause_identified"):
                priority_factors.append(0.8)  # High priority for root cause identification
            else:
                priority_factors.append(0.5)
            
            # Correlation count factor
            correlation_count = len(correlations)
            if correlation_count > 5:
                priority_factors.append(0.9)  # Many correlations = high impact
            elif correlation_count > 2:
                priority_factors.append(0.7)
            else:
                priority_factors.append(0.5)
            
            # Creator tier factor
            tier_priorities = {"premium": 1.0, "professional": 0.8, "emerging": 0.6, "starter": 0.4}
            tier_priority = tier_priorities.get(alert_node.creator_tier, 0.5)
            priority_factors.append(tier_priority)
            
            # Storm factor
            storm_correlations = [c for c in correlations if c.correlation_type == CorrelationType.STORM]
            if storm_correlations:
                priority_factors.append(0.9)  # Alert storms need immediate attention
            
            escalation_priority = np.mean(priority_factors)
            return min(1.0, max(0.0, escalation_priority))
            
        except Exception as e:
            logger.error(f"Failed to calculate escalation priority: {e}")
            return 0.5
    
    def _analyze_creator_impact_correlation(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge]
    ) -> Dict[str, Any]:
        """Analyze Creator-specific impact correlations"""
        try:
            impact_analysis = {
                "creator_journey_affected": False,
                "journey_stage": None,
                "impacted_creator_count": 0,
                "creator_tier_distribution": {},
                "journey_correlations_found": 0
            }
            
            # Count journey correlations
            journey_correlations = [c for c in correlations if c.correlation_type == CorrelationType.USER_JOURNEY]
            impact_analysis["journey_correlations_found"] = len(journey_correlations)
            
            if journey_correlations:
                impact_analysis["creator_journey_affected"] = True
            
            # Analyze affected creators from correlations
            affected_creators = set()
            if alert_node.creator_id:
                affected_creators.add(alert_node.creator_id)
            
            # Get creator info from correlated alerts
            for correlation in correlations:
                for buffered_alert in self.alert_buffer:
                    if buffered_alert.alert_id == correlation.source_alert_id and buffered_alert.creator_id:
                        affected_creators.add(buffered_alert.creator_id)
            
            impact_analysis["impacted_creator_count"] = len(affected_creators)
            
            # Analyze creator tier distribution
            tier_distribution = defaultdict(int)
            for buffered_alert in self.alert_buffer:
                if buffered_alert.creator_id in affected_creators and buffered_alert.creator_tier:
                    tier_distribution[buffered_alert.creator_tier] += 1
            
            impact_analysis["creator_tier_distribution"] = dict(tier_distribution)
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze Creator impact correlation: {e}")
            return {}
    
    def _generate_correlation_rationale(
        self,
        alert_node: AlertNode,
        correlations: List[CorrelationEdge],
        primary_correlation_type: CorrelationType
    ) -> str:
        """Generate human-readable correlation rationale"""
        try:
            parts = []
            
            # Primary correlation summary
            correlation_summaries = {
                CorrelationType.CAUSAL: f"Found {len(correlations)} causal correlations indicating upstream issues",
                CorrelationType.DEPENDENCY: f"Identified {len(correlations)} dependency-related alerts",
                CorrelationType.STORM: f"Detected alert storm with {len(correlations)} related alerts",
                CorrelationType.PATTERN: f"Found {len(correlations)} alerts matching similar patterns",
                CorrelationType.USER_JOURNEY: f"Identified {len(correlations)} Creator journey correlations",
                CorrelationType.TEMPORAL: f"Found {len(correlations)} temporally related alerts",
                CorrelationType.SPATIAL: f"Identified {len(correlations)} spatially related alerts"
            }
            
            parts.append(correlation_summaries.get(
                primary_correlation_type,
                f"Found {len(correlations)} correlated alerts"
            ))
            
            # Strength summary
            if correlations:
                avg_strength = np.mean([c.strength for c in correlations])
                if avg_strength > 0.8:
                    parts.append("with very high correlation strength")
                elif avg_strength > 0.6:
                    parts.append("with high correlation strength")
                else:
                    parts.append("with moderate correlation strength")
            
            # Time range summary
            if correlations:
                time_deltas = [abs(c.time_delta_seconds) for c in correlations]
                max_time_delta = max(time_deltas)
                if max_time_delta < 300:  # 5 minutes
                    parts.append("occurring within 5 minutes")
                elif max_time_delta < 1800:  # 30 minutes
                    parts.append("occurring within 30 minutes")
                else:
                    parts.append("occurring within the correlation window")
            
            # Creator context
            if alert_node.creator_id:
                parts.append(f"affecting Creator {alert_node.creator_id}")
                if alert_node.creator_tier:
                    parts.append(f"({alert_node.creator_tier} tier)")
            
            return ". ".join(parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate correlation rationale: {e}")
            return f"Correlation analysis completed for alert {alert_node.alert_id}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the correlation engine"""
        return {
            "status": "healthy",
            "correlation_rules_loaded": len(self.correlation_rules),
            "alerts_in_buffer": len(self.alert_buffer),
            "correlation_graph_nodes": self.correlation_graph.number_of_nodes(),
            "correlation_graph_edges": self.correlation_graph.number_of_edges(),
            "service_dependencies": self.service_dependency_graph.number_of_nodes(),
            "creator_journey_patterns": len(self.creator_journey_patterns),
            "correlation_stats": self.correlation_stats.copy()
        }
    
    def get_correlation_statistics(self) -> Dict[str, Any]:
        """Get correlation statistics and performance metrics"""
        stats = self.correlation_stats.copy()
        
        if stats["total_alerts_processed"] > 0:
            stats["correlation_rate"] = stats["correlations_found"] / stats["total_alerts_processed"]
            stats["root_cause_identification_rate"] = stats["root_causes_identified"] / stats["correlations_found"] if stats["correlations_found"] > 0 else 0
        
        return stats


if __name__ == "__main__":
    # Testing/development code
    import asyncio
    
    async def test_correlation_engine():
        config = {}
        engine = AlertCorrelationIntelligence(config)
        
        # Mock alert context
        class MockAlertContext:
            def __init__(self, alert_id, service, severity="critical", creator_id=None):
                self.alert_id = alert_id
                self.timestamp = datetime.now()
                self.source_service = service
                self.severity = type('Severity', (), {'value': severity})()
                self.creator_id = creator_id
                self.creator_tier = type('CreatorTier', (), {'value': 'premium'})() if creator_id else None
                self.metadata = {"summary": f"Test alert from {service}"}
        
        # Simulate sequence of related alerts
        alerts = [
            MockAlertContext("alert_001", "database", "critical"),
            MockAlertContext("alert_002", "api", "critical"),
            MockAlertContext("alert_003", "frontend", "warning")
        ]
        
        # Process alerts and look for correlations
        for i, alert in enumerate(alerts):
            # Add small delay to simulate real timing
            if i > 0:
                await asyncio.sleep(0.1)
                alert.timestamp = datetime.now()
            
            result = await engine.correlate_alert(alert)
            if result:
                print(f"\nCorrelation found for {alert.alert_id}:")
                print(f"  Correlation ID: {result.correlation_id}")
                print(f"  Type: {result.correlation_type.value}")
                print(f"  Score: {result.correlation_score:.2f}")
                print(f"  Confidence: {result.confidence_level:.2f}")
                print(f"  Correlated Alerts: {result.correlated_alerts}")
                print(f"  Rationale: {result.rationale}")
            else:
                print(f"No correlations found for {alert.alert_id}")
        
        # Print final statistics
        print(f"\nFinal Statistics:")
        stats = engine.get_correlation_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test_correlation_engine())