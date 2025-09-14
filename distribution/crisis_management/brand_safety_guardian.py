"""Brand Safety Guardian - Advanced Brand Protection System

Comprehensive brand safety monitoring and protection system with AI-powered
threat detection and automated response capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

# Core imports
from ..config.crisis_configs import CrisisConfiguration


class ThreatLevel(Enum):
    """Brand threat levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyProtocolType(Enum):
    """Safety protocol types"""
    CONTENT_FILTER = "content_filter"
    REPUTATION_MONITOR = "reputation_monitor"
    ASSOCIATION_CHECK = "association_check"
    COMPLIANCE_VERIFY = "compliance_verify"
    CRISIS_RESPONSE = "crisis_response"


@dataclass
class BrandThreat:
    """Brand safety threat detection"""
    threat_id: str
    threat_type: str
    description: str
    level: ThreatLevel
    platform: str
    source: str
    detected_at: datetime
    confidence: float
    impact_score: float
    evidence: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
    status: str = "active"


@dataclass
class SafetyProtocol:
    """Brand safety protocol definition"""
    protocol_id: str
    name: str
    protocol_type: SafetyProtocolType
    description: str
    rules: List[Dict[str, Any]]
    automated_actions: List[str]
    escalation_criteria: Dict[str, Any]
    effectiveness_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class BrandSafetyGuardian:
    """Advanced brand safety monitoring and protection system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Safety configuration
        self.crisis_config = CrisisConfiguration()
        
        # Brand safety settings
        self.brand_keywords = self.config.get('brand_keywords', [])
        self.protected_assets = self.config.get('protected_assets', [])
        self.safety_threshold = self.config.get('safety_threshold', 0.7)
        
        # Monitoring systems
        self.active_threats: Dict[str, BrandThreat] = {}
        self.safety_protocols: Dict[str, SafetyProtocol] = {}
        self.threat_history: List[BrandThreat] = []
        
        # Safety metrics
        self.safety_metrics = {
            'threats_detected': 0,
            'threats_mitigated': 0,
            'false_positives': 0,
            'response_time_avg': timedelta(minutes=0),
            'safety_score': 100.0
        }
        
        # Initialize default protocols
        self._initialize_default_protocols()
        
        self.logger.info("BrandSafetyGuardian initialized")
    
    def _initialize_default_protocols(self) -> None:
        """Initialize default brand safety protocols"""
        
        # Content Safety Protocol
        content_protocol = SafetyProtocol(
            protocol_id="content_safety_001",
            name="Content Safety Filter",
            protocol_type=SafetyProtocolType.CONTENT_FILTER,
            description="Monitors and filters potentially harmful content",
            rules=[
                {
                    'rule_type': 'keyword_blacklist',
                    'keywords': ['hate', 'violence', 'discrimination', 'illegal'],
                    'action': 'flag_for_review'
                },
                {
                    'rule_type': 'sentiment_threshold',
                    'threshold': -0.8,
                    'action': 'escalate'
                },
                {
                    'rule_type': 'brand_association',
                    'negative_associations': ['scandal', 'controversy', 'lawsuit'],
                    'action': 'immediate_alert'
                }
            ],
            automated_actions=[
                'pause_content_distribution',
                'notify_safety_team',
                'flag_for_manual_review'
            ],
            escalation_criteria={
                'threat_level': 'high',
                'impact_score': 7.0,
                'confidence': 0.8
            }
        )
        
        # Reputation Monitoring Protocol
        reputation_protocol = SafetyProtocol(
            protocol_id="reputation_monitor_001",
            name="Reputation Monitoring",
            protocol_type=SafetyProtocolType.REPUTATION_MONITOR,
            description="Monitors brand reputation across platforms",
            rules=[
                {
                    'rule_type': 'sentiment_trend',
                    'decline_threshold': 0.3,
                    'time_window': '24h',
                    'action': 'investigate'
                },
                {
                    'rule_type': 'mention_volume',
                    'spike_threshold': 200,
                    'action': 'analyze_sentiment'
                }
            ],
            automated_actions=[
                'increase_monitoring_frequency',
                'generate_reputation_report',
                'alert_communications_team'
            ],
            escalation_criteria={
                'sentiment_decline': 0.5,
                'mention_spike': 500
            }
        )
        
        # Store protocols
        self.safety_protocols[content_protocol.protocol_id] = content_protocol
        self.safety_protocols[reputation_protocol.protocol_id] = reputation_protocol
    
    async def detect_brand_threats(self, content: str, platform: str, 
                                 source: str, metadata: Dict[str, Any] = None) -> List[BrandThreat]:
        """Detect potential brand safety threats in content"""
        try:
            threats = []
            metadata = metadata or {}
            
            # Analyze content for various threat types
            
            # 1. Keyword-based threats
            keyword_threats = await self._detect_keyword_threats(content, platform, source)
            threats.extend(keyword_threats)
            
            # 2. Sentiment-based threats  
            sentiment_threats = await self._detect_sentiment_threats(content, platform, source)
            threats.extend(sentiment_threats)
            
            # 3. Association-based threats
            association_threats = await self._detect_association_threats(content, platform, source, metadata)
            threats.extend(association_threats)
            
            # 4. Compliance threats
            compliance_threats = await self._detect_compliance_threats(content, platform, source)
            threats.extend(compliance_threats)
            
            # Store detected threats
            for threat in threats:
                self.active_threats[threat.threat_id] = threat
                self.threat_history.append(threat)
            
            # Update metrics
            self.safety_metrics['threats_detected'] += len(threats)
            
            # Trigger automated responses
            for threat in threats:
                if threat.level.value in ['high', 'critical']:
                    await self._trigger_automated_response(threat)
            
            return threats
            
        except Exception as e:
            self.logger.error(f"Brand threat detection failed: {e}")
            raise
    
    async def _detect_keyword_threats(self, content: str, platform: str, source: str) -> List[BrandThreat]:
        """Detect keyword-based brand threats"""
        threats = []
        
        # Define harmful keyword categories
        harmful_keywords = {
            'hate_speech': ['hate', 'racism', 'discrimination', 'bigotry'],
            'violence': ['violence', 'attack', 'harm', 'threat'],
            'illegal_content': ['illegal', 'drugs', 'fraud', 'scam'],
            'adult_content': ['explicit', 'pornographic', 'sexual'],
            'brand_negative': ['terrible', 'worst', 'awful', 'scam', 'fraud']
        }
        
        content_lower = content.lower()
        
        for category, keywords in harmful_keywords.items():
            found_keywords = [kw for kw in keywords if kw in content_lower]
            
            if found_keywords:
                # Calculate threat level based on keyword severity and count
                threat_level = self._calculate_keyword_threat_level(category, len(found_keywords))
                
                threat = BrandThreat(
                    threat_id=f"kw_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                    threat_type=f"keyword_{category}",
                    description=f"Detected {category} keywords: {', '.join(found_keywords)}",
                    level=threat_level,
                    platform=platform,
                    source=source,
                    detected_at=datetime.utcnow(),
                    confidence=0.8,  # High confidence for keyword detection
                    impact_score=self._calculate_keyword_impact(category),
                    evidence=[f"Keywords found: {found_keywords}"],
                    mitigation_actions=[
                        'review_content',
                        'consider_content_modification',
                        'escalate_if_severe'
                    ]
                )
                threats.append(threat)
        
        return threats
    
    def _calculate_keyword_threat_level(self, category: str, keyword_count: int) -> ThreatLevel:
        """Calculate threat level based on keyword category and count"""
        severity_map = {
            'hate_speech': ThreatLevel.CRITICAL,
            'violence': ThreatLevel.HIGH,
            'illegal_content': ThreatLevel.HIGH,
            'adult_content': ThreatLevel.MEDIUM,
            'brand_negative': ThreatLevel.LOW
        }
        
        base_level = severity_map.get(category, ThreatLevel.LOW)
        
        # Increase threat level based on keyword count
        if keyword_count >= 3:
            if base_level == ThreatLevel.LOW:
                return ThreatLevel.MEDIUM
            elif base_level == ThreatLevel.MEDIUM:
                return ThreatLevel.HIGH
            elif base_level == ThreatLevel.HIGH:
                return ThreatLevel.CRITICAL
        
        return base_level
    
    def _calculate_keyword_impact(self, category: str) -> float:
        """Calculate impact score for keyword-based threats"""
        impact_scores = {
            'hate_speech': 9.5,
            'violence': 8.5,
            'illegal_content': 9.0,
            'adult_content': 6.0,
            'brand_negative': 4.0
        }
        return impact_scores.get(category, 3.0)
    
    async def _detect_sentiment_threats(self, content: str, platform: str, source: str) -> List[BrandThreat]:
        """Detect sentiment-based brand threats"""
        threats = []
        
        try:
            # Simple sentiment analysis (can be enhanced with advanced models)
            from textblob import TextBlob
            
            blob = TextBlob(content)
            sentiment_score = blob.sentiment.polarity
            confidence = abs(sentiment_score)
            
            # Check for extremely negative sentiment
            if sentiment_score <= -0.7:
                threat_level = ThreatLevel.HIGH if sentiment_score <= -0.9 else ThreatLevel.MEDIUM
                
                threat = BrandThreat(
                    threat_id=f"sent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                    threat_type="negative_sentiment",
                    description=f"Extremely negative sentiment detected (score: {sentiment_score:.3f})",
                    level=threat_level,
                    platform=platform,
                    source=source,
                    detected_at=datetime.utcnow(),
                    confidence=confidence,
                    impact_score=abs(sentiment_score) * 8,
                    evidence=[f"Sentiment score: {sentiment_score}"],
                    mitigation_actions=[
                        'analyze_sentiment_context',
                        'consider_response_strategy',
                        'monitor_sentiment_trend'
                    ]
                )
                threats.append(threat)
        
        except ImportError:
            self.logger.warning("TextBlob not available for sentiment analysis")
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
        
        return threats
    
    async def _detect_association_threats(self, content: str, platform: str, source: str, 
                                        metadata: Dict[str, Any]) -> List[BrandThreat]:
        """Detect threats based on harmful associations"""
        threats = []
        
        # Define harmful associations
        harmful_associations = {
            'scandal': ['scandal', 'controversy', 'exposed', 'leaked'],
            'legal_issues': ['lawsuit', 'sued', 'court', 'legal action'],
            'financial_problems': ['bankrupt', 'debt', 'financial crisis', 'losses'],
            'ethical_violations': ['unethical', 'violation', 'breach', 'misconduct']
        }
        
        content_lower = content.lower()
        
        for association_type, keywords in harmful_associations.items():
            found_associations = [kw for kw in keywords if kw in content_lower]
            
            if found_associations:
                # Check if brand is mentioned in association context
                brand_mentioned = any(brand in content_lower for brand in self.brand_keywords)
                
                if brand_mentioned:
                    threat_level = ThreatLevel.HIGH if association_type in ['scandal', 'legal_issues'] else ThreatLevel.MEDIUM
                    
                    threat = BrandThreat(
                        threat_id=f"assoc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        threat_type=f"harmful_association_{association_type}",
                        description=f"Brand associated with {association_type}: {', '.join(found_associations)}",
                        level=threat_level,
                        platform=platform,
                        source=source,
                        detected_at=datetime.utcnow(),
                        confidence=0.7,
                        impact_score=self._calculate_association_impact(association_type),
                        evidence=[f"Harmful associations: {found_associations}", f"Brand mentioned: {brand_mentioned}"],
                        mitigation_actions=[
                            'verify_association_accuracy',
                            'prepare_clarification_statement',
                            'engage_crisis_team'
                        ]
                    )
                    threats.append(threat)
        
        return threats
    
    def _calculate_association_impact(self, association_type: str) -> float:
        """Calculate impact score for association-based threats"""
        impact_scores = {
            'scandal': 9.0,
            'legal_issues': 8.5,
            'financial_problems': 7.0,
            'ethical_violations': 8.0
        }
        return impact_scores.get(association_type, 5.0)
    
    async def _detect_compliance_threats(self, content: str, platform: str, source: str) -> List[BrandThreat]:
        """Detect compliance-related brand threats"""
        threats = []
        
        # Define compliance risk indicators
        compliance_risks = {
            'data_privacy': ['personal data', 'privacy violation', 'gdpr', 'data breach'],
            'advertising_standards': ['false advertising', 'misleading', 'deceptive'],
            'regulatory_compliance': ['regulation violation', 'non-compliant', 'regulatory action'],
            'industry_standards': ['safety violation', 'standards breach', 'certification loss']
        }
        
        content_lower = content.lower()
        
        for risk_type, indicators in compliance_risks.items():
            found_indicators = [ind for ind in indicators if ind in content_lower]
            
            if found_indicators:
                threat_level = ThreatLevel.HIGH  # Compliance issues are always high priority
                
                threat = BrandThreat(
                    threat_id=f"comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                    threat_type=f"compliance_{risk_type}",
                    description=f"Compliance risk detected: {risk_type} - {', '.join(found_indicators)}",
                    level=threat_level,
                    platform=platform,
                    source=source,
                    detected_at=datetime.utcnow(),
                    confidence=0.8,
                    impact_score=8.5,  # High impact for compliance issues
                    evidence=[f"Compliance indicators: {found_indicators}"],
                    mitigation_actions=[
                        'immediate_legal_review',
                        'assess_compliance_status',
                        'prepare_corrective_actions'
                    ]
                )
                threats.append(threat)
        
        return threats
    
    async def _trigger_automated_response(self, threat -> None: BrandThreat) -> None:
        """Trigger automated response to high-priority threats"""
        try:
            self.logger.warning(f"Triggering automated response for threat: {threat.threat_id}")
            
            # Determine appropriate protocol
            protocol = self._select_response_protocol(threat)
            
            if protocol:
                # Execute automated actions
                for action in protocol.automated_actions:
                    await self._execute_safety_action(action, threat)
                
                # Check escalation criteria
                if self._should_escalate(threat, protocol):
                    await self._escalate_threat(threat)
            
        except Exception as e:
            self.logger.error(f"Automated response failed for threat {threat.threat_id}: {e}")
    
    def _select_response_protocol(self, threat: BrandThreat) -> Optional[SafetyProtocol]:
        """Select appropriate safety protocol for threat"""
        
        # Protocol selection based on threat type
        protocol_mapping = {
            'keyword_': SafetyProtocolType.CONTENT_FILTER,
            'negative_sentiment': SafetyProtocolType.REPUTATION_MONITOR,
            'harmful_association': SafetyProtocolType.ASSOCIATION_CHECK,
            'compliance_': SafetyProtocolType.COMPLIANCE_VERIFY
        }
        
        for threat_prefix, protocol_type in protocol_mapping.items():
            if threat.threat_type.startswith(threat_prefix):
                # Find protocol of this type
                for protocol in self.safety_protocols.values():
                    if protocol.protocol_type == protocol_type:
                        return protocol
        
        return None
    
    async def _execute_safety_action(self, action -> None: str, threat -> None: BrandThreat) -> None:
        """Execute a specific safety action"""
        try:
            if action == 'pause_content_distribution':
                self.logger.info(f"Pausing content distribution due to threat: {threat.threat_id}")
                # In real implementation, this would pause content distribution
            
            elif action == 'notify_safety_team':
                self.logger.info(f"Notifying safety team about threat: {threat.threat_id}")
                # In real implementation, this would send notifications
            
            elif action == 'flag_for_manual_review':
                self.logger.info(f"Flagging for manual review: {threat.threat_id}")
                threat.status = "pending_review"
            
            elif action == 'increase_monitoring_frequency':
                self.logger.info(f"Increasing monitoring frequency due to threat: {threat.threat_id}")
                # In real implementation, this would adjust monitoring settings
            
            elif action == 'generate_reputation_report':
                self.logger.info(f"Generating reputation report for threat: {threat.threat_id}")
                # In real implementation, this would generate reports
            
            else:
                self.logger.info(f"Executing safety action '{action}' for threat: {threat.threat_id}")
            
        except Exception as e:
            self.logger.error(f"Safety action execution failed: {e}")
    
    def _should_escalate(self, threat: BrandThreat, protocol: SafetyProtocol) -> bool:
        """Determine if threat should be escalated"""
        criteria = protocol.escalation_criteria
        
        # Check threat level
        if 'threat_level' in criteria:
            required_level = criteria['threat_level']
            if threat.level.value == 'critical' or (required_level == 'high' and threat.level.value in ['high', 'critical']):
                return True
        
        # Check impact score
        if 'impact_score' in criteria and threat.impact_score >= criteria['impact_score']:
            return True
        
        # Check confidence
        if 'confidence' in criteria and threat.confidence >= criteria['confidence']:
            return True
        
        return False
    
    async def _escalate_threat(self, threat -> None: BrandThreat) -> None:
        """Escalate threat to higher authorities"""
        try:
            self.logger.critical(f"ESCALATING THREAT: {threat.threat_id} - {threat.description}")
            
            # Mark threat as escalated
            threat.status = "escalated"
            
            # In real implementation, this would:
            # - Send notifications to management
            # - Trigger crisis response protocols
            # - Activate emergency procedures
            
        except Exception as e:
            self.logger.error(f"Threat escalation failed: {e}")
    
    async def get_brand_safety_status(self) -> Dict[str, Any]:
        """Get current brand safety status"""
        try:
            active_threat_count = len(self.active_threats)
            critical_threats = [t for t in self.active_threats.values() if t.level == ThreatLevel.CRITICAL]
            high_threats = [t for t in self.active_threats.values() if t.level == ThreatLevel.HIGH]
            
            # Calculate safety score
            safety_score = self._calculate_safety_score()
            
            status = {
                'timestamp': datetime.utcnow().isoformat(),
                'safety_score': safety_score,
                'safety_status': self._get_safety_status_label(safety_score),
                'active_threats': active_threat_count,
                'critical_threats': len(critical_threats),
                'high_threats': len(high_threats),
                'threat_breakdown': self._get_threat_breakdown(),
                'recent_threats': [
                    {
                        'threat_id': t.threat_id,
                        'type': t.threat_type,
                        'level': t.level.value,
                        'platform': t.platform,
                        'detected_at': t.detected_at.isoformat()
                    }
                    for t in sorted(self.threat_history[-10:], key=lambda x: x.detected_at, reverse=True)
                ],
                'safety_metrics': self.safety_metrics
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Safety status retrieval failed: {e}")
            raise
    
    def _calculate_safety_score(self) -> float:
        """Calculate overall brand safety score"""
        base_score = 100.0
        
        # Deduct points for active threats
        for threat in self.active_threats.values():
            if threat.level == ThreatLevel.CRITICAL:
                base_score -= 20
            elif threat.level == ThreatLevel.HIGH:
                base_score -= 10
            elif threat.level == ThreatLevel.MEDIUM:
                base_score -= 5
            elif threat.level == ThreatLevel.LOW:
                base_score -= 2
        
        return max(0.0, base_score)
    
    def _get_safety_status_label(self, score: float) -> str:
        """Get safety status label based on score"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good" 
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "critical"
    
    def _get_threat_breakdown(self) -> Dict[str, int]:
        """Get breakdown of threats by type"""
        breakdown = {}
        
        for threat in self.active_threats.values():
            threat_category = threat.threat_type.split('_')[0]
            breakdown[threat_category] = breakdown.get(threat_category, 0) + 1
        
        return breakdown


# Export classes
__all__ = [
    'BrandSafetyGuardian',
    'SafetyProtocol',
    'BrandThreat',
    'ThreatLevel',
    'SafetyProtocolType'
]