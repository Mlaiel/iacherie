"""Threat Detection Engine for Events Security

Advanced ML-powered threat detection for Ainflue business events.
Detects sophisticated threats targeting content, collaboration, and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThreatIndicator:
    """Represents a detected threat indicator"""
    indicator_type: str
    severity: str
    description: str
    business_context: str
    confidence_score: float = 0.0
    detected_at: datetime = None
    source_event_id: str = None
    
    def __post_init__(self) -> None:
        if self.detected_at is None:
            self.detected_at = datetime.utcnow()


@dataclass
class ThreatAnalysisResult:
    """Result of threat analysis for an event"""
    event_id: str
    threat_level: ThreatLevel
    indicators: List[ThreatIndicator]
    risk_score: float
    business_impact: str
    recommended_actions: List[str]
    analysis_timestamp: datetime = None
    
    def __post_init__(self) -> None:
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.utcnow()


@dataclass
class PatternAnalysis:
    """Analysis results for behavioral patterns"""
    frequency_anomaly_score: float = 0.0
    format_diversity_score: float = 0.0
    uploads_per_hour: int = 0
    network_expansion_rate: float = 0.0
    velocity_anomaly_score: float = 0.0
    transactions_per_minute: int = 0


class ThreatDetectionEngine:
    """
    Advanced threat detection engine for Ainflue business events.
    Uses ML-powered analysis with business context awareness.
    """
    
    def __init__(self) -> None:
        self.enabled = True
        self.threat_signatures = self._load_threat_signatures()
        self.behavior_baselines = {}
        self.detection_history = []
        self.max_history_size = 10000
        logger.info("ThreatDetectionEngine initialized")
    
    async def analyze_event_security(self, event: Any) -> ThreatAnalysisResult:
        """
        Comprehensive security analysis of a domain event.
        
        Args:
            event: Domain event to analyze
            
        Returns:
            ThreatAnalysisResult with detailed analysis
        """
        if not self.enabled:
            return self._create_safe_result(event)
        
        try:
            # Extract event details
            event_id = getattr(event, 'event_id', 'unknown')
            event_type = getattr(event, 'event_type', 'unknown')
            event_data = getattr(event, 'data', {})
            
            # Multi-layer threat analysis
            threat_indicators = await self._perform_multi_layer_analysis(
                event_id, event_type, event_data
            )
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(threat_indicators)
            
            # Classify threat level
            threat_level = self._classify_threat_level(risk_score)
            
            # Assess business impact
            business_impact = await self._assess_business_impact(event_type, risk_score)
            
            # Generate recommendations
            recommended_actions = self._generate_response_recommendations(
                threat_level, threat_indicators
            )
            
            result = ThreatAnalysisResult(
                event_id=event_id,
                threat_level=threat_level,
                indicators=threat_indicators,
                risk_score=risk_score,
                business_impact=business_impact,
                recommended_actions=recommended_actions
            )
            
            # Store analysis in history
            self._store_analysis_history(result)
            
            logger.debug(f"Threat analysis complete for event {event_id}: {threat_level.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error in threat analysis: {str(e)}")
            return self._create_error_result(event, str(e))
    
    async def _perform_multi_layer_analysis(self, 
                                          event_id: str, 
                                          event_type: str, 
                                          event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Perform multi-layer threat analysis"""
        
        indicators = []
        
        # Pattern anomaly analysis
        pattern_indicators = await self._analyze_pattern_anomalies(
            event_id, event_type, event_data
        )
        indicators.extend(pattern_indicators)
        
        # Signature-based detection
        signature_indicators = await self._check_signature_threats(
            event_id, event_type, event_data
        )
        indicators.extend(signature_indicators)
        
        # Behavioral analysis
        behavioral_indicators = await self._analyze_behavioral_deviations(
            event_id, event_type, event_data
        )
        indicators.extend(behavioral_indicators)
        
        # Business logic validation
        business_indicators = await self._validate_business_logic_integrity(
            event_id, event_type, event_data
        )
        indicators.extend(business_indicators)
        
        return indicators
    
    async def _analyze_pattern_anomalies(self, 
                                       event_id: str, 
                                       event_type: str, 
                                       event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze event patterns for anomalies based on Ainflue business logic"""
        
        indicators = []
        
        try:
            # Content upload pattern analysis
            if event_type.startswith("content.upload"):
                indicators.extend(await self._analyze_upload_patterns(event_data))
            
            # Collaboration pattern analysis
            elif event_type.startswith("collaboration."):
                indicators.extend(await self._analyze_collaboration_patterns(event_data))
            
            # Monetization pattern analysis
            elif event_type.startswith("monetization."):
                indicators.extend(await self._analyze_monetization_patterns(event_data))
            
            # User authentication patterns
            elif event_type.startswith("user.auth"):
                indicators.extend(await self._analyze_auth_patterns(event_data))
                
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
        
        return indicators
    
    async def _analyze_upload_patterns(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze content upload patterns for threats"""
        
        indicators = []
        
        # Simulate upload frequency analysis
        upload_count = event_data.get('upload_count_last_hour', 0)
        file_size = event_data.get('file_size', 0)
        file_type = event_data.get('file_type', '')
        
        # Mass upload detection
        if upload_count > 50:  # More than 50 uploads per hour
            indicators.append(ThreatIndicator(
                indicator_type="mass_upload_anomaly",
                severity="high",
                description=f"Excessive upload activity: {upload_count} uploads/hour",
                business_context="Potential content spam or account compromise",
                confidence_score=0.85,
                source_event_id=event_data.get('event_id')
            ))
        
        # Large file anomaly
        if file_size > 500_000_000:  # 500MB+
            indicators.append(ThreatIndicator(
                indicator_type="large_file_anomaly",
                severity="medium",
                description=f"Unusually large file: {file_size} bytes",
                business_context="Potential data exfiltration or storage abuse",
                confidence_score=0.65,
                source_event_id=event_data.get('event_id')
            ))
        
        # Suspicious file type
        suspicious_types = ['.exe', '.bat', '.cmd', '.scr', '.pif']
        if any(file_type.endswith(ext) for ext in suspicious_types):
            indicators.append(ThreatIndicator(
                indicator_type="suspicious_file_type",
                severity="critical",
                description=f"Potentially malicious file type: {file_type}",
                business_context="Potential malware distribution attempt",
                confidence_score=0.95,
                source_event_id=event_data.get('event_id')
            ))
        
        return indicators
    
    async def _analyze_collaboration_patterns(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze collaboration patterns for threats"""
        
        indicators = []
        
        # Network expansion rate analysis
        new_connections = event_data.get('new_connections_last_day', 0)
        collaboration_requests = event_data.get('collaboration_requests_sent', 0)
        
        # Rapid network expansion
        if new_connections > 100:  # More than 100 new connections per day
            indicators.append(ThreatIndicator(
                indicator_type="rapid_network_expansion",
                severity="high",
                description=f"Rapid collaboration network growth: {new_connections} connections/day",
                business_context="Potential platform gaming or fraud ring formation",
                confidence_score=0.80,
                source_event_id=event_data.get('event_id')
            ))
        
        # Collaboration spam
        if collaboration_requests > 20:  # More than 20 requests per day
            indicators.append(ThreatIndicator(
                indicator_type="collaboration_spam",
                severity="medium",
                description=f"High collaboration request volume: {collaboration_requests} requests",
                business_context="Potential spam or unsolicited collaboration attempts",
                confidence_score=0.70,
                source_event_id=event_data.get('event_id')
            ))
        
        return indicators
    
    async def _analyze_monetization_patterns(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze monetization patterns for threats"""
        
        indicators = []
        
        # Transaction velocity analysis
        transaction_amount = event_data.get('amount', 0)
        transactions_per_hour = event_data.get('transactions_last_hour', 0)
        
        # High-value transaction anomaly
        if transaction_amount > 50000:  # $50,000+
            indicators.append(ThreatIndicator(
                indicator_type="high_value_transaction",
                severity="critical",
                description=f"High-value transaction: ${transaction_amount}",
                business_context="Potential money laundering or fraud attempt",
                confidence_score=0.90,
                source_event_id=event_data.get('event_id')
            ))
        
        # Transaction velocity anomaly
        if transactions_per_hour > 10:
            indicators.append(ThreatIndicator(
                indicator_type="transaction_velocity_anomaly",
                severity="high",
                description=f"High transaction velocity: {transactions_per_hour}/hour",
                business_context="Potential automated fraud or money laundering",
                confidence_score=0.75,
                source_event_id=event_data.get('event_id')
            ))
        
        return indicators
    
    async def _analyze_auth_patterns(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze authentication patterns for threats"""
        
        indicators = []
        
        # Failed login attempts
        failed_attempts = event_data.get('failed_attempts_last_hour', 0)
        login_locations = event_data.get('unique_locations_last_day', 0)
        
        # Brute force detection
        if failed_attempts > 10:
            indicators.append(ThreatIndicator(
                indicator_type="brute_force_attempt",
                severity="critical",
                description=f"Multiple failed login attempts: {failed_attempts}",
                business_context="Potential account takeover attempt",
                confidence_score=0.95,
                source_event_id=event_data.get('event_id')
            ))
        
        # Geographical anomaly
        if login_locations > 5:  # More than 5 different locations in a day
            indicators.append(ThreatIndicator(
                indicator_type="geographical_anomaly",
                severity="medium",
                description=f"Login from multiple locations: {login_locations} locations",
                business_context="Potential account sharing or compromise",
                confidence_score=0.60,
                source_event_id=event_data.get('event_id')
            ))
        
        return indicators
    
    async def _check_signature_threats(self, 
                                     event_id: str, 
                                     event_type: str, 
                                     event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Check against known threat signatures"""
        
        indicators = []
        
        # Check against threat signatures
        for signature in self.threat_signatures:
            if self._matches_signature(event_type, event_data, signature):
                indicators.append(ThreatIndicator(
                    indicator_type=f"signature_match_{signature['name']}",
                    severity=signature['severity'],
                    description=f"Matches threat signature: {signature['description']}",
                    business_context=signature['business_impact'],
                    confidence_score=signature['confidence'],
                    source_event_id=event_id
                ))
        
        return indicators
    
    async def _analyze_behavioral_deviations(self, 
                                           event_id: str, 
                                           event_type: str, 
                                           event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze behavioral deviations from baseline"""
        
        indicators = []
        
        user_id = event_data.get('user_id')
        if not user_id:
            return indicators
        
        # Get user baseline (simplified simulation)
        baseline = self.behavior_baselines.get(user_id, {
            'avg_daily_events': 10,
            'typical_event_types': ['content.upload', 'user.auth'],
            'avg_file_size': 10_000_000,
            'typical_hours': list(range(9, 18))  # 9 AM to 6 PM
        })
        
        # Check for unusual activity timing
        current_hour = datetime.utcnow().hour
        if current_hour not in baseline['typical_hours']:
            indicators.append(ThreatIndicator(
                indicator_type="unusual_timing",
                severity="low",
                description=f"Activity outside typical hours: {current_hour}:00",
                business_context="Potential account compromise or unusual behavior",
                confidence_score=0.30,
                source_event_id=event_id
            ))
        
        # Check for unusual event types
        if event_type not in baseline['typical_event_types']:
            indicators.append(ThreatIndicator(
                indicator_type="unusual_event_type",
                severity="medium",
                description=f"Unusual event type for user: {event_type}",
                business_context="Potential privilege escalation or account misuse",
                confidence_score=0.50,
                source_event_id=event_id
            ))
        
        return indicators
    
    async def _validate_business_logic_integrity(self, 
                                               event_id: str, 
                                               event_type: str, 
                                               event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Validate business logic integrity"""
        
        indicators = []
        
        # Validate workflow sequence
        if not await self._validate_workflow_sequence(event_type, event_data):
            indicators.append(ThreatIndicator(
                indicator_type="workflow_sequence_violation",
                severity="high",
                description="Event violates expected business workflow sequence",
                business_context="Potential business logic bypass attempt",
                confidence_score=0.85,
                source_event_id=event_id
            ))
        
        # Validate business limits
        if not await self._validate_business_limits(event_type, event_data):
            indicators.append(ThreatIndicator(
                indicator_type="business_limit_violation",
                severity="medium",
                description="Event violates business limits or constraints",
                business_context="Potential abuse or premium feature circumvention",
                confidence_score=0.70,
                source_event_id=event_id
            ))
        
        return indicators
    
    async def _validate_workflow_sequence(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Validate expected workflow sequence (simplified)"""
        
        # Simple validation examples
        if event_type == "content.processing.complete":
            # Should have a preceding upload event
            return event_data.get('upload_event_id') is not None
        
        if event_type == "monetization.payment.complete":
            # Should have a preceding payment initiation
            return event_data.get('payment_initiation_id') is not None
        
        return True  # Default to valid
    
    async def _validate_business_limits(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Validate business limits and constraints (simplified)"""
        
        user_id = event_data.get('user_id')
        if not user_id:
            return True
        
        # Example business limit validations
        if event_type.startswith("content.upload"):
            daily_upload_limit = 100  # Example limit
            current_uploads = event_data.get('daily_uploads', 0)
            return current_uploads <= daily_upload_limit
        
        if event_type.startswith("monetization."):
            daily_transaction_limit = 10000  # $10,000 daily limit
            current_amount = event_data.get('daily_transaction_total', 0)
            transaction_amount = event_data.get('amount', 0)
            return (current_amount + transaction_amount) <= daily_transaction_limit
        
        return True  # Default to valid
    
    def _calculate_risk_score(self, indicators: List[ThreatIndicator]) -> float:
        """Calculate overall risk score from threat indicators"""
        
        if not indicators:
            return 0.0
        
        # Weight scores by severity
        severity_weights = {
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "critical": 1.0
        }
        
        total_score = 0.0
        for indicator in indicators:
            severity_weight = severity_weights.get(indicator.severity, 0.5)
            total_score += indicator.confidence_score * severity_weight
        
        # Normalize to 0-1 scale
        max_possible_score = len(indicators) * 1.0  # Max if all critical with 1.0 confidence
        normalized_score = min(total_score / max_possible_score if max_possible_score > 0 else 0.0, 1.0)
        
        return normalized_score
    
    def _classify_threat_level(self, risk_score: float) -> ThreatLevel:
        """Classify threat level based on risk score"""
        
        if risk_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif risk_score >= 0.6:
            return ThreatLevel.HIGH
        elif risk_score >= 0.3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _assess_business_impact(self, event_type: str, risk_score: float) -> str:
        """Assess potential business impact"""
        
        base_impacts = {
            "content.": "Content integrity and platform trust",
            "collaboration.": "Creator network and partnerships",
            "monetization.": "Financial security and revenue",
            "user.": "User accounts and data protection",
            "distribution.": "Content distribution and platform reputation"
        }
        
        # Find matching event type prefix
        impact_area = "Platform operations"
        for prefix, impact in base_impacts.items():
            if event_type.startswith(prefix):
                impact_area = impact
                break
        
        # Scale impact by risk score
        if risk_score >= 0.8:
            return f"Critical impact to {impact_area.lower()}"
        elif risk_score >= 0.6:
            return f"High impact to {impact_area.lower()}"
        elif risk_score >= 0.3:
            return f"Medium impact to {impact_area.lower()}"
        else:
            return f"Low impact to {impact_area.lower()}"
    
    def _generate_response_recommendations(self, 
                                         threat_level: ThreatLevel, 
                                         indicators: List[ThreatIndicator]) -> List[str]:
        """Generate response recommendations based on threat analysis"""
        
        recommendations = []
        
        if threat_level == ThreatLevel.CRITICAL:
            recommendations.extend([
                "Immediately block user account and quarantine related content",
                "Escalate to security team for manual investigation",
                "Review and potentially block related user accounts",
                "Preserve audit trail for forensic analysis"
            ])
        elif threat_level == ThreatLevel.HIGH:
            recommendations.extend([
                "Temporarily suspend user privileges",
                "Require additional authentication for future actions",
                "Monitor user activity closely for 24-48 hours",
                "Review transaction history for anomalies"
            ])
        elif threat_level == ThreatLevel.MEDIUM:
            recommendations.extend([
                "Increase monitoring frequency for this user",
                "Require email verification for sensitive actions",
                "Log additional details for future analysis"
            ])
        else:
            recommendations.append("Continue normal monitoring")
        
        # Add specific recommendations based on threat types
        threat_types = [indicator.indicator_type for indicator in indicators]
        
        if any("brute_force" in t for t in threat_types):
            recommendations.append("Implement progressive delay for login attempts")
        
        if any("high_value" in t for t in threat_types):
            recommendations.append("Require manual approval for large transactions")
        
        if any("mass_upload" in t for t in threat_types):
            recommendations.append("Throttle upload rates for this user")
        
        return recommendations
    
    def _matches_signature(self, event_type: str, event_data: Dict[str, Any], signature: Dict[str, Any]) -> bool:
        """Check if event matches a threat signature"""
        
        # Simple signature matching (can be enhanced with regex, ML, etc.)
        if signature.get('event_type_pattern'):
            if signature['event_type_pattern'] not in event_type:
                return False
        
        if signature.get('data_patterns'):
            for key, pattern in signature['data_patterns'].items():
                if key in event_data:
                    if pattern not in str(event_data[key]):
                        return False
        
        return True
    
    def _load_threat_signatures(self) -> List[Dict[str, Any]]:
        """Load known threat signatures"""
        
        return [
            {
                'name': 'sql_injection_attempt',
                'event_type_pattern': 'user.input',
                'data_patterns': {'content': 'SELECT'},
                'severity': 'critical',
                'description': 'Potential SQL injection attempt',
                'business_impact': 'Database security compromise',
                'confidence': 0.90
            },
            {
                'name': 'xss_attempt',
                'event_type_pattern': 'content.upload',
                'data_patterns': {'content': '<script>'},
                'severity': 'high',
                'description': 'Potential cross-site scripting attempt',
                'business_impact': 'User data exposure risk',
                'confidence': 0.85
            },
            {
                'name': 'credential_stuffing',
                'event_type_pattern': 'user.auth.failed',
                'data_patterns': {},
                'severity': 'high',
                'description': 'Potential credential stuffing attack',
                'business_impact': 'Account takeover risk',
                'confidence': 0.80
            }
        ]
    
    def _create_safe_result(self, event: Any) -> ThreatAnalysisResult:
        """Create safe result when detection is disabled"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return ThreatAnalysisResult(
            event_id=event_id,
            threat_level=ThreatLevel.LOW,
            indicators=[],
            risk_score=0.0,
            business_impact="No analysis performed (detection disabled)",
            recommended_actions=["Enable threat detection for security analysis"]
        )
    
    def _create_error_result(self, event: Any, error_message: str) -> ThreatAnalysisResult:
        """Create error result when analysis fails"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return ThreatAnalysisResult(
            event_id=event_id,
            threat_level=ThreatLevel.MEDIUM,  # Conservative approach
            indicators=[
                ThreatIndicator(
                    indicator_type="analysis_error",
                    severity="medium",
                    description=f"Threat analysis failed: {error_message}",
                    business_context="Security analysis incomplete - manual review recommended",
                    confidence_score=0.0
                )
            ],
            risk_score=0.5,  # Conservative approach
            business_impact="Unknown - analysis failed",
            recommended_actions=["Manual security review required", "Check threat detection system"]
        )
    
    def _store_analysis_history(self, result -> None: ThreatAnalysisResult) -> None:
        """Store analysis result in history for learning"""
        
        self.detection_history.append({
            'timestamp': result.analysis_timestamp,
            'event_id': result.event_id,
            'threat_level': result.threat_level.value,
            'risk_score': result.risk_score,
            'indicator_count': len(result.indicators)
        })
        
        # Maintain maximum history size
        if len(self.detection_history) > self.max_history_size:
            self.detection_history = self.detection_history[-self.max_history_size:]
    
    def enable_detection(self) -> None:
        """Enable threat detection"""
        self.enabled = True
        logger.info("Threat detection enabled")
    
    def disable_detection(self) -> None:
        """Disable threat detection"""
        self.enabled = False
        logger.info("Threat detection disabled")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        
        if not self.detection_history:
            return {
                'total_analyses': 0,
                'threat_levels': {},
                'avg_risk_score': 0.0,
                'last_analysis': None
            }
        
        threat_levels = {}
        risk_scores = []
        
        for analysis in self.detection_history:
            level = analysis['threat_level']
            threat_levels[level] = threat_levels.get(level, 0) + 1
            risk_scores.append(analysis['risk_score'])
        
        return {
            'total_analyses': len(self.detection_history),
            'threat_levels': threat_levels,
            'avg_risk_score': sum(risk_scores) / len(risk_scores),
            'last_analysis': self.detection_history[-1]['timestamp']
        }


# Export for module use
__all__ = ['ThreatDetectionEngine', 'ThreatLevel', 'ThreatIndicator', 'ThreatAnalysisResult']