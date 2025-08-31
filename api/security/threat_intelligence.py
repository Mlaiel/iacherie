"""
Threat Intelligence Module
Advanced threat detection and security intelligence for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform

Team Specialties:
- Lead AI Developer: Advanced machine learning and neural networks
- Senior Backend Developer: Enterprise-grade Python architecture
- ML Engineer: Deep learning and content analysis algorithms  
- Database Administrator: High-performance data management
- Security Expert: Cybersecurity and content protection
- Microservices Architect: Scalable distributed systems
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: CI/CD and cloud infrastructure deployment
- AI Prompt Engineer: LLM integration and optimization

  COPYRIGHT NOTICE - STRICTLY PROTECTED 
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
ANY UNAUTHORIZED USE, REPRODUCTION, DISTRIBUTION, OR THEFT OF THIS CODE
OR CONCEPT WITHOUT EXPLICIT WRITTEN PERMISSION IS STRICTLY FORBIDDEN.

Violators will face:
- Legal action under German and international copyright laws
- Criminal charges for intellectual property theft
- Financial penalties and damages claims
- Immediate cease and desist enforcement

Contact: mlaiel@live.de for any authorization requests.
"""

import asyncio
import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import numpy as np
from urllib.parse import urlparse
import re
import ipaddress

from ..core.config import get_settings
from ..utils.cache import CacheManager
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ThreatSeverity(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"


class ThreatCategory(Enum):
    """Threat categories"""
    PIRACY = "content_piracy"
    UNAUTHORIZED_USE = "unauthorized_use"
    COPYRIGHT_VIOLATION = "copyright_violation"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    BRAND_ABUSE = "brand_abuse"
    DEEPFAKE = "deepfake_manipulation"
    MALICIOUS_REDISTRIBUTION = "malicious_redistribution"
    DDOS_ATTACK = "ddos_attack"
    DATA_BREACH = "data_breach"
    SOCIAL_ENGINEERING = "social_engineering"


class ThreatSource(Enum):
    """Threat source types"""
    WEB_CRAWLER = "web_crawler"
    API_MONITORING = "api_monitoring"
    USER_REPORT = "user_report"
    AUTOMATED_DETECTION = "automated_detection"
    SOCIAL_MEDIA = "social_media_monitoring"
    DARK_WEB = "dark_web_surveillance"
    INTELLIGENCE_FEED = "intelligence_feed"


class ActionStatus(Enum):
    """Mitigation action status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ThreatIndicator:
    """Threat indicator for pattern matching"""
    indicator_id: str = field(default_factory=lambda: secrets.token_hex(8))
    indicator_type: str = "url_pattern"
    pattern: str = ""
    threat_category: ThreatCategory = ThreatCategory.PIRACY
    confidence_score: float = 0.0
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityThreat:
    """Comprehensive security threat record"""
    threat_id: str = field(default_factory=lambda: secrets.token_hex(16))
    threat_type: ThreatCategory = ThreatCategory.UNAUTHORIZED_USE
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    
    # Detection details
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: ThreatSource = ThreatSource.AUTOMATED_DETECTION
    source_url: Optional[str] = None
    source_ip: Optional[str] = None
    
    # Content details
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    affected_assets: List[str] = field(default_factory=list)
    
    # Analysis results
    confidence_score: float = 0.0
    risk_score: float = 0.0
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence and context
    evidence: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    indicators: List[ThreatIndicator] = field(default_factory=list)
    
    # Response actions
    mitigation_actions: List[Dict[str, Any]] = field(default_factory=list)
    response_status: ActionStatus = ActionStatus.PENDING
    
    # Timeline
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "threat_id": self.threat_id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
            "source": self.source.value,
            "source_url": self.source_url,
            "source_ip": self.source_ip,
            "content_id": self.content_id,
            "creator_id": self.creator_id,
            "affected_assets": self.affected_assets,
            "confidence_score": self.confidence_score,
            "risk_score": self.risk_score,
            "impact_assessment": self.impact_assessment,
            "evidence": self.evidence,
            "context": self.context,
            "indicators": [
                {
                    "indicator_id": ind.indicator_id,
                    "type": ind.indicator_type,
                    "pattern": ind.pattern,
                    "category": ind.threat_category.value,
                    "confidence": ind.confidence_score
                } for ind in self.indicators
            ],
            "mitigation_actions": self.mitigation_actions,
            "response_status": self.response_status.value,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class ThreatIntelligenceReport:
    """Comprehensive threat intelligence report"""
    report_id: str = field(default_factory=lambda: secrets.token_hex(12))
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc) - timedelta(days=7))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Threat statistics
    total_threats: int = 0
    threats_by_severity: Dict[str, int] = field(default_factory=dict)
    threats_by_category: Dict[str, int] = field(default_factory=dict)
    threats_by_source: Dict[str, int] = field(default_factory=dict)
    
    # Trend analysis
    threat_trends: Dict[str, Any] = field(default_factory=dict)
    emerging_threats: List[Dict[str, Any]] = field(default_factory=list)
    
    # Protection effectiveness
    mitigation_success_rate: float = 0.0
    average_response_time: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatIntelligenceEngine:
    """Advanced threat intelligence and detection engine"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.threats: Dict[str, SecurityThreat] = {}
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.blacklisted_ips: Set[str] = set()
        self.blacklisted_domains: Set[str] = set()
        self._setup_threat_patterns()
        self._setup_monitoring_systems()
    
    def _setup_threat_patterns(self):
        """Initialize threat detection patterns"""
        self.threat_patterns = {
            ThreatCategory.PIRACY: [
                r'pirate.*download',
                r'free.*mp3.*download',
                r'torrent.*music',
                r'illegal.*streaming'
            ],
            ThreatCategory.UNAUTHORIZED_USE: [
                r'unauthorized.*use',
                r'stolen.*content',
                r'copied.*without.*permission'
            ],
            ThreatCategory.COPYRIGHT_VIOLATION: [
                r'copyright.*violation',
                r'dmca.*takedown',
                r'infringement.*notice'
            ],
            ThreatCategory.DEEPFAKE: [
                r'deepfake',
                r'ai.*generated.*fake',
                r'synthetic.*media'
            ]
        }
        
        self.suspicious_domains = {
            'torrent', 'pirate', 'free-download', 'mp3skull',
            'fakeyou', 'deepfake', 'clone-voice'
        }
    
    def _setup_monitoring_systems(self):
        """Initialize monitoring and detection systems"""
        self.monitoring_platforms = [
            'youtube.com', 'instagram.com', 'tiktok.com', 'twitter.com',
            'facebook.com', 'spotify.com', 'soundcloud.com', 'reddit.com'
        ]
        
        self.crawl_patterns = {
            'piracy_sites': [
                r'https?://.*pirate.*\..*/',
                r'https?://.*torrent.*\..*/',
                r'https?://.*free-music.*\..*/'
            ],
            'content_farms': [
                r'https?://.*content-farm.*\..*/',
                r'https?://.*auto-generated.*\..*/'
            ]
        }
    
    async def analyze_threat(
        self,
        content_url: str,
        content_data: Optional[bytes] = None,
        context: Dict[str, Any] = None
    ) -> SecurityThreat:
        """Analyze potential security threat"""



        try:
            context = context or {}
            
            # Parse URL for analysis
            parsed_url = urlparse(content_url)
            domain = parsed_url.netloc.lower()
            
            # Initialize threat
            threat = SecurityThreat(
                source_url=content_url,
                context=context
            )
            
            # Domain analysis
            domain_analysis = await self._analyze_domain(domain)
            threat.evidence['domain_analysis'] = domain_analysis
            
            # URL pattern analysis
            url_analysis = await self._analyze_url_patterns(content_url)
            threat.evidence['url_analysis'] = url_analysis
            
            # Content analysis (if available)
            if content_data:
                content_analysis = await self._analyze_content(content_data)
                threat.evidence['content_analysis'] = content_analysis
            
            # Calculate threat scores
            threat.confidence_score = self._calculate_confidence_score(threat.evidence)
            threat.risk_score = self._calculate_risk_score(threat.evidence, domain_analysis)
            
            # Determine threat category and severity
            threat.threat_type = self._classify_threat_category(threat.evidence)
            threat.severity = self._assess_threat_severity(threat.risk_score)
            
            # Generate indicators
            threat.indicators = await self._extract_threat_indicators(
                content_url, threat.evidence
            )
            
            # Impact assessment
            threat.impact_assessment = await self._assess_threat_impact(threat)
            
            # Generate mitigation actions
            threat.mitigation_actions = await self._generate_mitigation_actions(threat)
            
            # Store threat
            self.threats[threat.threat_id] = threat
            await self.cache.set(
                f"threat:{threat.threat_id}",
                threat.to_dict(),
                ttl=86400
            )
            
            logger.info(f"Threat analyzed: {threat.threat_id} - {threat.severity.value}")
            return threat
            
        except Exception as e:
            logger.error(f"Error analyzing threat: {str(e)}")
            raise
    
    async def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain for threat indicators"""



        try:
            analysis = {
                "domain": domain,
                "is_suspicious": False,
                "risk_factors": [],
                "reputation_score": 0.0
            }
            
            # Check against suspicious domain patterns
            for suspicious_pattern in self.suspicious_domains:
                if suspicious_pattern in domain:
                    analysis["is_suspicious"] = True
                    analysis["risk_factors"].append(f"suspicious_pattern: {suspicious_pattern}")
            
            # Check domain age (mock implementation)
            analysis["domain_age"] = "unknown"  # Would use WHOIS lookup
            analysis["registrar"] = "unknown"
            
            # Check if domain is blacklisted
            if domain in self.blacklisted_domains:
                analysis["is_blacklisted"] = True
                analysis["risk_factors"].append("domain_blacklisted")
            
            # Calculate reputation score
            risk_factor_count = len(analysis["risk_factors"])
            analysis["reputation_score"] = max(0.0, 1.0 - (risk_factor_count * 0.3))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing domain: {str(e)}")
            return {"domain": domain, "error": str(e)}
    
    async def _analyze_url_patterns(self, url: str) -> Dict[str, Any]:
        """Analyze URL for threat patterns"""



        try:
            analysis = {
                "url": url,
                "matched_patterns": [],
                "threat_indicators": [],
                "risk_score": 0.0
            }
            
            url_lower = url.lower()
            
            # Check against threat patterns
            for category, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, url_lower):
                        analysis["matched_patterns"].append({
                            "pattern": pattern,
                            "category": category.value
                        })
                        analysis["threat_indicators"].append(category.value)
            
            # Check for suspicious keywords
            suspicious_keywords = [
                'download', 'free', 'crack', 'hack', 'pirate',
                'torrent', 'leak', 'stolen', 'bootleg'
            ]
            
            for keyword in suspicious_keywords:
                if keyword in url_lower:
                    analysis["threat_indicators"].append(f"suspicious_keyword: {keyword}")
            
            # Calculate risk score
            indicator_count = len(analysis["threat_indicators"])
            analysis["risk_score"] = min(1.0, indicator_count * 0.2)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing URL patterns: {str(e)}")
            return {"url": url, "error": str(e)}
    
    async def _analyze_content(self, content_data: bytes) -> Dict[str, Any]:
        """Analyze content for threat indicators"""



        try:
            analysis = {
                "size": len(content_data),
                "content_hash": hashlib.sha256(content_data).hexdigest(),
                "threat_indicators": [],
                "content_type": "unknown"
            }
            
            # Basic content type detection
            if content_data.startswith(b'\x89PNG'):
                analysis["content_type"] = "image/png"
            elif content_data.startswith(b'\xff\xd8\xff'):
                analysis["content_type"] = "image/jpeg"
            elif content_data.startswith(b'ID3') or content_data.startswith(b'\xff\xfb'):
                analysis["content_type"] = "audio/mp3"
            
            # Check for suspicious content patterns
            try:
                # Try to decode as text
                text_content = content_data.decode('utf-8', errors='ignore').lower()
                
                # Check for piracy-related text
                piracy_keywords = [
                    'torrent', 'download free', 'pirate', 'crack',
                    'keygen', 'serial', 'unauthorized copy'
                ]
                
                for keyword in piracy_keywords:
                    if keyword in text_content:
                        analysis["threat_indicators"].append(f"piracy_keyword: {keyword}")
                        
            except Exception:
                pass  # Not text content
            
            # Check content size for anomalies
            if len(content_data) > 100 * 1024 * 1024:  # 100MB
                analysis["threat_indicators"].append("suspicious_large_size")
            elif len(content_data) < 100:  # Very small
                analysis["threat_indicators"].append("suspicious_small_size")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_confidence_score(self, evidence: Dict[str, Any]) -> float:
        """Calculate confidence score for threat detection"""



        try:
            confidence = 0.0
            
            # Domain analysis confidence
            domain_analysis = evidence.get('domain_analysis', {})
            if domain_analysis.get('is_suspicious'):
                confidence += 0.4
            if domain_analysis.get('is_blacklisted'):
                confidence += 0.6
            
            # URL pattern confidence
            url_analysis = evidence.get('url_analysis', {})
            matched_patterns = len(url_analysis.get('matched_patterns', []))
            confidence += min(0.5, matched_patterns * 0.1)
            
            # Content analysis confidence
            content_analysis = evidence.get('content_analysis', {})
            threat_indicators = len(content_analysis.get('threat_indicators', []))
            confidence += min(0.3, threat_indicators * 0.05)
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.0
    
    def _calculate_risk_score(
        self,
        evidence: Dict[str, Any],
        domain_analysis: Dict[str, Any]
    ) -> float:
        """Calculate risk score for threat"""



        try:
            risk = 0.0
            
            # Domain risk factors
            risk_factors = domain_analysis.get('risk_factors', [])
            risk += len(risk_factors) * 0.15
            
            # Reputation score impact
            reputation = domain_analysis.get('reputation_score', 1.0)
            risk += (1.0 - reputation) * 0.3
            
            # URL pattern risk
            url_analysis = evidence.get('url_analysis', {})
            url_risk = url_analysis.get('risk_score', 0.0)
            risk += url_risk * 0.4
            
            # Content indicators
            content_analysis = evidence.get('content_analysis', {})
            content_indicators = len(content_analysis.get('threat_indicators', []))
            risk += content_indicators * 0.1
            
            return min(1.0, risk)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 0.0
    
    def _classify_threat_category(self, evidence: Dict[str, Any]) -> ThreatCategory:
        """Classify threat category based on evidence"""



        try:
            # Check URL patterns
            url_analysis = evidence.get('url_analysis', {})
            matched_patterns = url_analysis.get('matched_patterns', [])
            
            category_scores = {}
            for pattern_match in matched_patterns:
                category = pattern_match.get('category')
                if category:
                    category_scores[category] = category_scores.get(category, 0) + 1
            
            # Return most likely category
            if category_scores:
                top_category = max(category_scores.keys(), key=lambda k: category_scores[k])
                try:
                    return ThreatCategory(top_category)
                except ValueError:
                    return ThreatCategory.UNAUTHORIZED_USE
            
            # Check domain analysis
            domain_analysis = evidence.get('domain_analysis', {})
            if domain_analysis.get('is_suspicious'):
                return ThreatCategory.PIRACY
            
            return ThreatCategory.UNAUTHORIZED_USE
            
        except Exception as e:
            logger.error(f"Error classifying threat category: {str(e)}")
            return ThreatCategory.UNAUTHORIZED_USE
    
    def _assess_threat_severity(self, risk_score: float) -> ThreatSeverity:
        """Assess threat severity based on risk score"""
        if risk_score >= 0.9:
            return ThreatSeverity.EXTREME
        elif risk_score >= 0.75:
            return ThreatSeverity.CRITICAL
        elif risk_score >= 0.5:
            return ThreatSeverity.HIGH
        elif risk_score >= 0.25:
            return ThreatSeverity.MEDIUM
        elif risk_score >= 0.1:
            return ThreatSeverity.LOW
        else:
            return ThreatSeverity.INFO
    
    async def _extract_threat_indicators(
        self,
        url: str,
        evidence: Dict[str, Any]
    ) -> List[ThreatIndicator]:
        """Extract threat indicators from analysis"""



        try:
            indicators = []
            
            # Domain indicators
            domain_analysis = evidence.get('domain_analysis', {})
            domain = urlparse(url).netloc
            
            if domain_analysis.get('is_suspicious'):
                indicator = ThreatIndicator(
                    indicator_type="suspicious_domain",
                    pattern=domain,
                    threat_category=ThreatCategory.PIRACY,
                    confidence_score=0.7
                )
                indicators.append(indicator)
            
            # URL pattern indicators
            url_analysis = evidence.get('url_analysis', {})
            for pattern_match in url_analysis.get('matched_patterns', []):
                indicator = ThreatIndicator(
                    indicator_type="url_pattern",
                    pattern=pattern_match['pattern'],
                    threat_category=ThreatCategory(pattern_match['category']),
                    confidence_score=0.8
                )
                indicators.append(indicator)
            
            # Store indicators
            for indicator in indicators:
                self.indicators[indicator.indicator_id] = indicator
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error extracting threat indicators: {str(e)}")
            return []
    
    async def _assess_threat_impact(self, threat: SecurityThreat) -> Dict[str, Any]:
        """Assess potential impact of threat"""



        try:
            impact_assessment = {
                "financial_impact": "medium",
                "reputational_impact": "medium",
                "legal_impact": "low",
                "operational_impact": "low"
            }
            
            # Adjust based on threat severity
            if threat.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXTREME]:
                impact_assessment["financial_impact"] = "high"
                impact_assessment["reputational_impact"] = "high"
                impact_assessment["legal_impact"] = "medium"
            
            # Adjust based on threat category
            if threat.threat_type == ThreatCategory.COPYRIGHT_VIOLATION:
                impact_assessment["legal_impact"] = "high"
            elif threat.threat_type == ThreatCategory.BRAND_ABUSE:
                impact_assessment["reputational_impact"] = "high"
            
            # Estimate potential losses
            if threat.severity == ThreatSeverity.EXTREME:
                impact_assessment["estimated_loss_range"] = "$10,000 - $100,000"
            elif threat.severity == ThreatSeverity.CRITICAL:
                impact_assessment["estimated_loss_range"] = "$1,000 - $10,000"
            else:
                impact_assessment["estimated_loss_range"] = "$0 - $1,000"
            
            return impact_assessment
            
        except Exception as e:
            logger.error(f"Error assessing threat impact: {str(e)}")
            return {}
    
    async def _generate_mitigation_actions(self, threat: SecurityThreat) -> List[Dict[str, Any]]:
        """Generate appropriate mitigation actions for threat"""



        try:
            actions = []
            
            # Standard actions based on threat type
            if threat.threat_type == ThreatCategory.PIRACY:
                actions.extend([
                    {
                        "action_id": secrets.token_hex(6),
                        "action_type": "dmca_takedown",
                        "description": "Send DMCA takedown notice to hosting provider",
                        "priority": "high",
                        "estimated_time": "24 hours",
                        "status": ActionStatus.PENDING.value
                    },
                    {
                        "action_id": secrets.token_hex(6),
                        "action_type": "document_evidence",
                        "description": "Collect and document evidence for legal action",
                        "priority": "medium",
                        "estimated_time": "2 hours",
                        "status": ActionStatus.PENDING.value
                    }
                ])
            
            elif threat.threat_type == ThreatCategory.UNAUTHORIZED_USE:
                actions.extend([
                    {
                        "action_id": secrets.token_hex(6),
                        "action_type": "cease_desist",
                        "description": "Send cease and desist notice",
                        "priority": "medium",
                        "estimated_time": "48 hours",
                        "status": ActionStatus.PENDING.value
                    },
                    {
                        "action_id": secrets.token_hex(6),
                        "action_type": "contact_platform",
                        "description": "Report violation to platform administrators",
                        "priority": "high",
                        "estimated_time": "4 hours",
                        "status": ActionStatus.PENDING.value
                    }
                ])
            
            # High severity additional actions
            if threat.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXTREME]:
                actions.append({
                    "action_id": secrets.token_hex(6),
                    "action_type": "legal_consultation",
                    "description": "Consult with legal team for potential litigation",
                    "priority": "high",
                    "estimated_time": "24 hours",
                    "status": ActionStatus.PENDING.value
                })
            
            # Always include monitoring action
            actions.append({
                "action_id": secrets.token_hex(6),
                "action_type": "enhanced_monitoring",
                "description": "Increase monitoring frequency for similar threats",
                "priority": "low",
                "estimated_time": "1 hour",
                "status": ActionStatus.PENDING.value
            })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating mitigation actions: {str(e)}")
            return []
    
    async def monitor_platforms(
        self,
        content_fingerprints: List[str],
        monitoring_duration: int = 3600
    ) -> List[SecurityThreat]:
        """Monitor platforms for threats related to content fingerprints"""
        detected_threats = []
        
        try:
            # Simulate platform monitoring
            for platform in self.monitoring_platforms:
                logger.info(f"Monitoring {platform} for content violations")
                
                # Mock threat detection
                if secrets.randbelow(10) < 3:  # 30% chance of finding threat
                    mock_url = f"https://{platform}/suspicious-content-{secrets.token_hex(4)}"
                    
                    threat = await self.analyze_threat(
                        mock_url,
                        context={
                            "platform": platform,
                            "monitoring_session": True,
                            "content_fingerprints": content_fingerprints
                        }
                    )
                    
                    detected_threats.append(threat)
            
            logger.info(f"Platform monitoring completed. Found {len(detected_threats)} threats")
            return detected_threats
            
        except Exception as e:
            logger.error(f"Error monitoring platforms: {str(e)}")
            return []
    
    async def generate_intelligence_report(
        self,
        period_days: int = 7
    ) -> ThreatIntelligenceReport:
        """Generate comprehensive threat intelligence report"""



        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=period_days)
            
            # Filter threats for period
            period_threats = [
                threat for threat in self.threats.values()
                if start_date <= threat.detected_at <= end_date
            ]
            
            # Generate statistics
            report = ThreatIntelligenceReport(
                period_start=start_date,
                period_end=end_date,
                total_threats=len(period_threats)
            )
            
            # Severity breakdown
            for severity in ThreatSeverity:
                count = len([t for t in period_threats if t.severity == severity])
                report.threats_by_severity[severity.value] = count
            
            # Category breakdown
            for category in ThreatCategory:
                count = len([t for t in period_threats if t.threat_type == category])
                report.threats_by_category[category.value] = count
            
            # Source breakdown
            for source in ThreatSource:
                count = len([t for t in period_threats if t.source == source])
                report.threats_by_source[source.value] = count
            
            # Calculate metrics
            if period_threats:
                resolved_threats = len([t for t in period_threats if t.resolved_at])
                report.mitigation_success_rate = resolved_threats / len(period_threats)
                
                response_times = [
                    (t.resolved_at - t.detected_at).total_seconds()
                    for t in period_threats if t.resolved_at
                ]
                
                if response_times:
                    report.average_response_time = sum(response_times) / len(response_times)
            
            # Generate recommendations
            report.recommendations = self._generate_security_recommendations(period_threats)
            
            logger.info(f"Threat intelligence report generated: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating intelligence report: {str(e)}")
            raise
    
    def _generate_security_recommendations(
        self,
        threats: List[SecurityThreat]
    ) -> List[str]:
        """Generate security recommendations based on threat analysis"""
        recommendations = []
        
        try:
            if not threats:
                recommendations.append("Continue monitoring with current security measures")
                return recommendations
            
            # High severity threats
            critical_threats = [t for t in threats if t.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXTREME]]
            if critical_threats:
                recommendations.append("Implement additional security measures for critical threat protection")
                recommendations.append("Consider legal action for severe copyright violations")
            
            # Category-specific recommendations
            piracy_threats = [t for t in threats if t.threat_type == ThreatCategory.PIRACY]
            if len(piracy_threats) > 5:
                recommendations.append("Increase piracy monitoring frequency")
                recommendations.append("Implement automated DMCA takedown system")
            
            # Platform-specific recommendations
            platform_counts = {}
            for threat in threats:
                if threat.source_url:
                    domain = urlparse(threat.source_url).netloc
                    platform_counts[domain] = platform_counts.get(domain, 0) + 1
            
            for platform, count in platform_counts.items():
                if count > 3:
                    recommendations.append(f"Enhanced monitoring recommended for {platform}")
            
            # General recommendations
            if len(threats) > 20:
                recommendations.append("Consider implementing automated threat response system")
            
            recommendations.append("Regular security awareness training for content creators")
            recommendations.append("Maintain up-to-date content fingerprint database")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations - manual review required"]


# Global threat intelligence engine
threat_intelligence = ThreatIntelligenceEngine()

# Export functions for easy import
async def analyze_security_threat(
    content_url: str,
    content_data: Optional[bytes] = None,
    context: Dict[str, Any] = None
) -> SecurityThreat:
    """Analyze security threat from URL and content"""



    return await threat_intelligence.analyze_threat(content_url, content_data, context)

async def monitor_content_platforms(
    content_fingerprints: List[str],
    duration: int = 3600
) -> List[SecurityThreat]:
    """Monitor platforms for content threats"""



    return await threat_intelligence.monitor_platforms(content_fingerprints, duration)

async def generate_threat_report(period_days: int = 7) -> ThreatIntelligenceReport:
    """Generate threat intelligence report"""



    return await threat_intelligence.generate_intelligence_report(period_days)
