"""Advanced Violation Analysis Engine - AI-Powered Content Rights Violation Detection

Sophisticated violation detection and analysis system with legal assessment,
evidence collection, and automated response capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
import uuid

from .content_detector import ContentFingerprint, SimilarityMatch, ContentSimilarity
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ViolationAnalysisError, ProcessingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ViolationAnalysisError, ProcessingError = globals().get('ViolationAnalysisError, ProcessingError', Exception)
from ...legal.copyright_analyzer import CopyrightAnalyzer
from ...legal.dmca_generator import DMCAGenerator
from ...legal.fair_use_analyzer import FairUseAnalyzer
from ...utils.evidence_collector import EvidenceCollector
from ...utils.screenshot_generator import ScreenshotGenerator
from ...integrations.legal_databases import LegalDatabaseConnector

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of content violations"""    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    PLAGIARISM = "plagiarism"
    DERIVATIVE_WORK = "derivative_work"
    COMMERCIAL_USE = "commercial_use"
    FAIR_USE_VIOLATION = "fair_use_violation"
    ATTRIBUTION_MISSING = "attribution_missing"

class ViolationSeverity(Enum):
    """Severity levels for violations"""    CRITICAL = "critical"        # Immediate legal action required
    HIGH = "high"               # Legal action recommended
    MEDIUM = "medium"           # Monitoring and warning
    LOW = "low"                 # Educational notice
    NEGLIGIBLE = "negligible"   # No action needed

class ViolationStatus(Enum):
    """Status of violation handling"""    DETECTED = "detected"
    ANALYZED = "analyzed"
    EVIDENCE_COLLECTED = "evidence_collected"
    NOTICE_SENT = "notice_sent"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class ActionType(Enum):
    """Types of actions that can be taken"""    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_STRIKE = "copyright_strike"
    PLATFORM_REPORT = "platform_report"
    LEGAL_NOTICE = "legal_notice"
    MONITORING = "monitoring"
    WARNING = "warning"
    NO_ACTION = "no_action"

@dataclass
class ViolationEvidence:
    """Evidence collected for a violation"""    evidence_id: str
    violation_id: str
    evidence_type: str
    file_path: str
    metadata: Dict[str, Any]
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    hash_value: Optional[str] = None

@dataclass
class LegalAssessment:
    """Legal assessment of a violation"""    assessment_id: str
    violation_id: str
    copyright_strength: float  # 0.0 - 1.0
    fair_use_likelihood: float  # 0.0 - 1.0
    commercial_impact: float  # 0.0 - 1.0
    jurisdictional_factors: Dict[str, Any]
    recommended_actions: List[ActionType]
    legal_precedents: List[Dict[str, Any]]
    assessed_by: str
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.0

@dataclass
class ViolationAnalysis:
    """Comprehensive violation analysis result"""    analysis_id: str
    target_fingerprint_id: str
    violating_content_url: str
    platform: str
    violation_types: List[ViolationType]
    severity: ViolationSeverity
    similarity_match: SimilarityMatch
    legal_assessment: LegalAssessment
    evidence: List[ViolationEvidence]
    recommended_actions: List[ActionType]
    estimated_damages: Optional[float] = None
    priority_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ViolationStatus = ViolationStatus.DETECTED

class ViolationAnalyzer:
    """    Advanced violation analysis engine with AI-powered legal assessment
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Legal analysis components
        self.copyright_analyzer = CopyrightAnalyzer()
        self.dmca_generator = DMCAGenerator()
        self.fair_use_analyzer = FairUseAnalyzer()
        
        # Evidence collection
        self.evidence_collector = EvidenceCollector()
        self.screenshot_generator = ScreenshotGenerator()
        
        # Legal database integration
        self.legal_db_connector = LegalDatabaseConnector()
        
        # Analysis thresholds
        self.violation_thresholds = {
            ViolationSeverity.CRITICAL: 0.95,
            ViolationSeverity.HIGH: 0.80,
            ViolationSeverity.MEDIUM: 0.65,
            ViolationSeverity.LOW: 0.45,
            ViolationSeverity.NEGLIGIBLE: 0.0
        }
        
        # Platform-specific violation patterns
        self.platform_patterns = {
            'youtube': {
                'commercial_indicators': ['monetized', 'ads', 'sponsor', 'affiliate'],
                'fair_use_indicators': ['review', 'commentary', 'parody', 'education'],
                'violation_weight': 1.2  # YouTube has strong copyright enforcement
            },
            'tiktok': {
                'commercial_indicators': ['brand', 'promotion', 'shop', 'link'],
                'fair_use_indicators': ['dance', 'challenge', 'remix'],
                'violation_weight': 1.0
            },
            'instagram': {
                'commercial_indicators': ['sponsored', 'ad', '#paid', 'shop'],
                'fair_use_indicators': ['art', 'inspiration', 'tribute'],
                'violation_weight': 1.1
            },
            'twitter': {
                'commercial_indicators': ['promoted', 'sponsored', 'ad'],
                'fair_use_indicators': ['news', 'commentary', 'criticism'],
                'violation_weight': 0.9
            }
        }
        
        # Cache for analysis results
        self.analysis_cache: Dict[str, ViolationAnalysis] = {}
        self.max_cache_size = 5000
        
        # Performance tracking
        self.analysis_stats = {
            'total_analyses': 0,
            'violations_detected': 0,
            'false_positives': 0,
            'average_processing_time': 0.0,
            'action_success_rate': {}
        }
    
    async def initialize(self):
        """Initialize violation analyzer components"""        try:
            start_time = time.time()
            
            # Initialize legal analysis components
            await self.copyright_analyzer.initialize()
            await self.dmca_generator.initialize()
            await self.fair_use_analyzer.initialize()
            
            # Initialize evidence collection
            await self.evidence_collector.initialize()
            await self.screenshot_generator.initialize()
            
            # Initialize legal database
            await self.legal_db_connector.initialize()
            
            initialization_time = time.time() - start_time
            logger.info(f"Violation Analyzer initialized successfully in {initialization_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize Violation Analyzer: {e}")
            raise ViolationAnalysisError(f"Initialization failed: {e}")
    
    async def analyze_violation(self, 
                              target_fingerprint: ContentFingerprint,
                              similarity_match: SimilarityMatch,
                              violating_content_url: str,
                              platform: str,
                              content_metadata: Dict[str, Any] = None) -> ViolationAnalysis:
        """        Perform comprehensive violation analysis
        """        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Create initial analysis object
            analysis = ViolationAnalysis(
                analysis_id=analysis_id,
                target_fingerprint_id=target_fingerprint.fingerprint_id,
                violating_content_url=violating_content_url,
                platform=platform,
                violation_types=[],
                severity=ViolationSeverity.NEGLIGIBLE,
                similarity_match=similarity_match,
                legal_assessment=None,
                evidence=[],
                recommended_actions=[]
            )
            
            # Step 1: Classify violation types
            violation_types = await self._classify_violation_types(
                target_fingerprint, similarity_match, content_metadata or {}
            )
            analysis.violation_types = violation_types
            
            # Step 2: Assess violation severity
            severity = await self._assess_violation_severity(
                target_fingerprint, similarity_match, violation_types, platform
            )
            analysis.severity = severity
            
            # Step 3: Collect evidence
            evidence = await self._collect_violation_evidence(
                violating_content_url, platform, analysis_id
            )
            analysis.evidence = evidence
            
            # Step 4: Perform legal assessment
            legal_assessment = await self._perform_legal_assessment(
                target_fingerprint, similarity_match, violation_types, 
                content_metadata or {}, platform
            )
            analysis.legal_assessment = legal_assessment
            
            # Step 5: Determine recommended actions
            recommended_actions = await self._determine_recommended_actions(
                severity, legal_assessment, platform, violation_types
            )
            analysis.recommended_actions = recommended_actions
            
            # Step 6: Calculate priority score
            priority_score = await self._calculate_priority_score(
                severity, legal_assessment, similarity_match, platform
            )
            analysis.priority_score = priority_score
            
            # Step 7: Estimate potential damages
            estimated_damages = await self._estimate_damages(
                target_fingerprint, content_metadata or {}, platform, violation_types
            )
            analysis.estimated_damages = estimated_damages
            
            # Update analysis status
            analysis.status = ViolationStatus.ANALYZED
            
            # Cache the analysis
            self.analysis_cache[analysis_id] = analysis
            
            # Update statistics
            self.analysis_stats['total_analyses'] += 1
            if severity != ViolationSeverity.NEGLIGIBLE:
                self.analysis_stats['violations_detected'] += 1
            
            processing_time = time.time() - start_time
            self.analysis_stats['average_processing_time'] = (
                (self.analysis_stats['average_processing_time'] * 
                 (self.analysis_stats['total_analyses'] - 1) + processing_time) / 
                self.analysis_stats['total_analyses']
            )
            
            logger.info(f"Violation analysis completed in {processing_time:.2f}s: {severity.value}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Violation analysis failed: {e}")
            raise ViolationAnalysisError(f"Analysis failed: {e}")
    
    async def _classify_violation_types(self, 
                                      target_fingerprint: ContentFingerprint,
                                      similarity_match: SimilarityMatch,
                                      content_metadata: Dict[str, Any]) -> List[ViolationType]:
        """Classify the types of violations present"""        violation_types = []
        
        try:
            # Check for exact copying (copyright infringement)
            if similarity_match.similarity_level == ContentSimilarity.EXACT:
                violation_types.append(ViolationType.COPYRIGHT_INFRINGEMENT)
            
            # Check for high similarity (unauthorized use)
            elif similarity_match.similarity_level == ContentSimilarity.HIGH:
                violation_types.append(ViolationType.UNAUTHORIZED_USE)
            
            # Check for derivative work
            elif similarity_match.similarity_level == ContentSimilarity.MEDIUM:
                violation_types.append(ViolationType.DERIVATIVE_WORK)
            
            # Check for commercial use indicators
            commercial_indicators = content_metadata.get('commercial_indicators', [])
            if commercial_indicators or content_metadata.get('monetized', False):
                violation_types.append(ViolationType.COMMERCIAL_USE)
            
            # Check for missing attribution
            if not content_metadata.get('attribution') and not content_metadata.get('source_credit'):
                violation_types.append(ViolationType.ATTRIBUTION_MISSING)
            
            # Check for plagiarism (text content)
            if target_fingerprint.text_fingerprint and similarity_match.similarity_score > 0.8:
                violation_types.append(ViolationType.PLAGIARISM)
            
            # Platform-specific checks
            platform_specific_violations = await self._check_platform_specific_violations(
                content_metadata
            )
            violation_types.extend(platform_specific_violations)
            
            return list(set(violation_types))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Violation type classification failed: {e}")
            return []
    
    async def _assess_violation_severity(self,
                                       target_fingerprint: ContentFingerprint,
                                       similarity_match: SimilarityMatch,
                                       violation_types: List[ViolationType],
                                       platform: str) -> ViolationSeverity:
        """Assess the severity of the violation"""        try:
            # Base severity from similarity score
            base_score = similarity_match.similarity_score
            
            # Apply violation type multipliers
            type_multipliers = {
                ViolationType.COPYRIGHT_INFRINGEMENT: 1.5,
                ViolationType.COMMERCIAL_USE: 1.3,
                ViolationType.UNAUTHORIZED_USE: 1.2,
                ViolationType.DERIVATIVE_WORK: 1.0,
                ViolationType.PLAGIARISM: 1.1,
                ViolationType.ATTRIBUTION_MISSING: 0.8,
                ViolationType.TRADEMARK_VIOLATION: 1.4,
                ViolationType.FAIR_USE_VIOLATION: 0.9
            }
            
            # Calculate weighted score
            total_multiplier = 1.0
            for violation_type in violation_types:
                multiplier = type_multipliers.get(violation_type, 1.0)
                total_multiplier *= multiplier
            
            # Apply platform-specific weight
            platform_weight = self.platform_patterns.get(platform, {}).get('violation_weight', 1.0)
            
            final_score = min(1.0, base_score * total_multiplier * platform_weight)
            
            # Determine severity level
            for severity, threshold in sorted(self.violation_thresholds.items(), 
                                            key=lambda x: x[1], reverse=True):
                if final_score >= threshold:
                    return severity
            
            return ViolationSeverity.NEGLIGIBLE
            
        except Exception as e:
            logger.error(f"Severity assessment failed: {e}")
            return ViolationSeverity.LOW
    
    async def _collect_violation_evidence(self,
                                        violating_content_url: str,
                                        platform: str,
                                        analysis_id: str) -> List[ViolationEvidence]:
        """Collect evidence for the violation"""        evidence_list = []
        
        try:
            # Take screenshot of the violating content
            screenshot_path = await self.screenshot_generator.capture_url(
                violating_content_url, f"violation_{analysis_id}_screenshot.png"
            )
            
            if screenshot_path:
                evidence_list.append(ViolationEvidence(
                    evidence_id=str(uuid.uuid4()),
                    violation_id=analysis_id,
                    evidence_type="screenshot",
                    file_path=screenshot_path,
                    metadata={"url": violating_content_url, "platform": platform},
                    verified=True
                ))
            
            # Collect metadata evidence
            metadata_evidence = await self.evidence_collector.collect_metadata(
                violating_content_url, platform
            )
            
            if metadata_evidence:
                evidence_list.append(ViolationEvidence(
                    evidence_id=str(uuid.uuid4()),
                    violation_id=analysis_id,
                    evidence_type="metadata",
                    file_path="",  # Metadata stored in database
                    metadata=metadata_evidence,
                    verified=True
                ))
            
            # Collect network evidence (WHOIS, DNS, etc.)
            network_evidence = await self.evidence_collector.collect_network_info(
                violating_content_url
            )
            
            if network_evidence:
                evidence_list.append(ViolationEvidence(
                    evidence_id=str(uuid.uuid4()),
                    violation_id=analysis_id,
                    evidence_type="network_info",
                    file_path="",
                    metadata=network_evidence,
                    verified=True
                ))
            
            # Archive the violating content
            archived_content = await self.evidence_collector.archive_content(
                violating_content_url, f"violation_{analysis_id}_archive"
            )
            
            if archived_content:
                evidence_list.append(ViolationEvidence(
                    evidence_id=str(uuid.uuid4()),
                    violation_id=analysis_id,
                    evidence_type="archived_content",
                    file_path=archived_content,
                    metadata={"original_url": violating_content_url},
                    verified=True
                ))
            
            logger.info(f"Collected {len(evidence_list)} pieces of evidence for {analysis_id}")
            return evidence_list
            
        except Exception as e:
            logger.error(f"Evidence collection failed: {e}")
            return evidence_list
    
    async def _perform_legal_assessment(self,
                                      target_fingerprint: ContentFingerprint,
                                      similarity_match: SimilarityMatch,
                                      violation_types: List[ViolationType],
                                      content_metadata: Dict[str, Any],
                                      platform: str) -> LegalAssessment:
        """Perform comprehensive legal assessment"""        assessment_id = str(uuid.uuid4())
        
        try:
            # Analyze copyright strength
            copyright_strength = await self.copyright_analyzer.assess_copyright_strength(
                target_fingerprint, content_metadata
            )
            
            # Analyze fair use likelihood
            fair_use_likelihood = await self.fair_use_analyzer.assess_fair_use(
                target_fingerprint, similarity_match, content_metadata, platform
            )
            
            # Assess commercial impact
            commercial_impact = await self._assess_commercial_impact(
                target_fingerprint, content_metadata, violation_types
            )
            
            # Analyze jurisdictional factors
            jurisdictional_factors = await self._analyze_jurisdictional_factors(
                target_fingerprint, content_metadata, platform
            )
            
            # Find legal precedents
            legal_precedents = await self.legal_db_connector.find_precedents(
                violation_types, platform, target_fingerprint.content_type
            )
            
            # Determine recommended legal actions
            recommended_actions = await self._determine_legal_actions(
                copyright_strength, fair_use_likelihood, commercial_impact, 
                violation_types, platform
            )
            
            # Calculate confidence score
            confidence = await self._calculate_legal_confidence(
                copyright_strength, fair_use_likelihood, len(legal_precedents)
            )
            
            return LegalAssessment(
                assessment_id=assessment_id,
                violation_id="",  # Will be set by caller
                copyright_strength=copyright_strength,
                fair_use_likelihood=fair_use_likelihood,
                commercial_impact=commercial_impact,
                jurisdictional_factors=jurisdictional_factors,
                recommended_actions=recommended_actions,
                legal_precedents=legal_precedents,
                assessed_by="AI_Legal_Analyzer",
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Legal assessment failed: {e}")
            # Return minimal assessment on failure
            return LegalAssessment(
                assessment_id=assessment_id,
                violation_id="",
                copyright_strength=0.5,
                fair_use_likelihood=0.5,
                commercial_impact=0.5,
                jurisdictional_factors={},
                recommended_actions=[],
                legal_precedents=[],
                assessed_by="AI_Legal_Analyzer",
                confidence=0.1
            )
    
    async def _determine_recommended_actions(self,
                                           severity: ViolationSeverity,
                                           legal_assessment: LegalAssessment,
                                           platform: str,
                                           violation_types: List[ViolationType]) -> List[ActionType]:
        """Determine recommended actions based on analysis"""        actions = []
        
        try:
            # Critical violations - immediate action
            if severity == ViolationSeverity.CRITICAL:
                if legal_assessment.copyright_strength > 0.8:
                    actions.append(ActionType.DMCA_TAKEDOWN)
                    actions.append(ActionType.CEASE_DESIST)
                
                if ViolationType.COMMERCIAL_USE in violation_types:
                    actions.append(ActionType.LEGAL_NOTICE)
            
            # High severity violations
            elif severity == ViolationSeverity.HIGH:
                if legal_assessment.fair_use_likelihood < 0.3:
                    actions.append(ActionType.DMCA_TAKEDOWN)
                    actions.append(ActionType.PLATFORM_REPORT)
                else:
                    actions.append(ActionType.COPYRIGHT_STRIKE)
            
            # Medium severity violations
            elif severity == ViolationSeverity.MEDIUM:
                if legal_assessment.copyright_strength > 0.6:
                    actions.append(ActionType.PLATFORM_REPORT)
                    actions.append(ActionType.WARNING)
                else:
                    actions.append(ActionType.MONITORING)
            
            # Low severity violations
            elif severity == ViolationSeverity.LOW:
                actions.append(ActionType.WARNING)
                actions.append(ActionType.MONITORING)
            
            # Negligible violations
            else:
                actions.append(ActionType.NO_ACTION)
            
            # Platform-specific recommendations
            platform_actions = await self._get_platform_specific_actions(
                platform, severity, violation_types
            )
            actions.extend(platform_actions)
            
            return list(set(actions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Action determination failed: {e}")
            return [ActionType.MONITORING]  # Safe fallback
    
    async def _calculate_priority_score(self,
                                      severity: ViolationSeverity,
                                      legal_assessment: LegalAssessment,
                                      similarity_match: SimilarityMatch,
                                      platform: str) -> float:
        """Calculate priority score for violation handling"""        try:
            # Base score from severity
            severity_scores = {
                ViolationSeverity.CRITICAL: 1.0,
                ViolationSeverity.HIGH: 0.8,
                ViolationSeverity.MEDIUM: 0.6,
                ViolationSeverity.LOW: 0.4,
                ViolationSeverity.NEGLIGIBLE: 0.1
            }
            
            base_score = severity_scores.get(severity, 0.1)
            
            # Apply legal factors
            legal_factor = (
                legal_assessment.copyright_strength * 0.4 +
                (1.0 - legal_assessment.fair_use_likelihood) * 0.3 +
                legal_assessment.commercial_impact * 0.3
            )
            
            # Apply similarity confidence
            similarity_factor = similarity_match.confidence
            
            # Apply platform urgency factor
            platform_urgency = {
                'youtube': 0.9,  # Fast spreading
                'tiktok': 1.0,   # Viral potential
                'instagram': 0.8,
                'twitter': 0.7,
                'generic': 0.5
            }
            
            urgency_factor = platform_urgency.get(platform, 0.5)
            
            # Calculate final priority score
            priority_score = (
                base_score * 0.4 +
                legal_factor * 0.3 +
                similarity_factor * 0.2 +
                urgency_factor * 0.1
            )
            
            return min(1.0, priority_score)
            
        except Exception as e:
            logger.error(f"Priority score calculation failed: {e}")
            return 0.5
    
    async def _estimate_damages(self,
                              target_fingerprint: ContentFingerprint,
                              content_metadata: Dict[str, Any],
                              platform: str,
                              violation_types: List[ViolationType]) -> Optional[float]:
        """Estimate potential financial damages"""        try:
            base_damage = 0.0
            
            # Base damages by content type
            content_type_damages = {
                'audio': 5000.0,   # Music industry standard
                'video': 10000.0,  # Video content value
                'image': 2000.0,   # Stock photo equivalent
                'text': 1000.0     # Written content
            }
            
            content_type = target_fingerprint.content_type.split('/')[0]
            base_damage = content_type_damages.get(content_type, 1000.0)
            
            # Commercial use multiplier
            if ViolationType.COMMERCIAL_USE in violation_types:
                commercial_multiplier = 3.0
                
                # Try to estimate revenue from metadata
                views = content_metadata.get('views', 0)
                engagement = content_metadata.get('likes', 0) + content_metadata.get('comments', 0)
                
                if views > 100000:  # Viral content
                    commercial_multiplier = 5.0
                elif views > 10000:
                    commercial_multiplier = 4.0
                
                base_damage *= commercial_multiplier
            
            # Platform-specific factors
            platform_multipliers = {
                'youtube': 2.0,    # Strong monetization
                'instagram': 1.5,  # Influencer economy
                'tiktok': 1.8,     # Viral potential
                'twitter': 1.2,    # Professional network
                'generic': 1.0
            }
            
            platform_multiplier = platform_multipliers.get(platform, 1.0)
            base_damage *= platform_multiplier
            
            # Violation type adjustments
            if ViolationType.COPYRIGHT_INFRINGEMENT in violation_types:
                base_damage *= 2.0  # Statutory damages
            
            if ViolationType.TRADEMARK_VIOLATION in violation_types:
                base_damage *= 1.5
            
            return round(base_damage, 2)
            
        except Exception as e:
            logger.error(f"Damage estimation failed: {e}")
            return None
    
    async def _check_platform_specific_violations(self,
                                                content_metadata: Dict[str, Any]) -> List[ViolationType]:
        """Check for platform-specific violation patterns"""        violations = []
        
        try:
            # Check content description for commercial indicators
            description = content_metadata.get('description', '').lower()
            title = content_metadata.get('title', '').lower()
            content_text = f"{title} {description}"
            
            # Commercial use indicators
            commercial_keywords = [
                'buy', 'purchase', 'shop', 'sale', 'discount', 'promo',
                'sponsored', 'affiliate', 'ad', 'advertisement'
            ]
            
            if any(keyword in content_text for keyword in commercial_keywords):
                violations.append(ViolationType.COMMERCIAL_USE)
            
            # Fair use violation indicators
            fair_use_violations = [
                'full song', 'complete track', 'entire video', 'whole movie'
            ]
            
            if any(indicator in content_text for indicator in fair_use_violations):
                violations.append(ViolationType.FAIR_USE_VIOLATION)
            
            return violations
            
        except Exception as e:
            logger.error(f"Platform-specific violation check failed: {e}")
            return []
    
    async def _assess_commercial_impact(self,
                                      target_fingerprint: ContentFingerprint,
                                      content_metadata: Dict[str, Any],
                                      violation_types: List[ViolationType]) -> float:
        """Assess the commercial impact of the violation"""        try:
            impact_score = 0.0
            
            # Base impact from violation types
            if ViolationType.COMMERCIAL_USE in violation_types:
                impact_score += 0.4
            
            if ViolationType.COPYRIGHT_INFRINGEMENT in violation_types:
                impact_score += 0.3
            
            # Engagement-based impact
            views = content_metadata.get('views', 0)
            likes = content_metadata.get('likes', 0)
            
            if views > 1000000:  # Viral content
                impact_score += 0.3
            elif views > 100000:
                impact_score += 0.2
            elif views > 10000:
                impact_score += 0.1
            
            # Monetization indicators
            if content_metadata.get('monetized', False):
                impact_score += 0.2
            
            # Channel/creator size impact
            subscriber_count = content_metadata.get('subscriber_count', 0)
            if subscriber_count > 1000000:
                impact_score += 0.1
            
            return min(1.0, impact_score)
            
        except Exception as e:
            logger.error(f"Commercial impact assessment failed: {e}")
            return 0.5
    
    async def _analyze_jurisdictional_factors(self,
                                            target_fingerprint: ContentFingerprint,
                                            content_metadata: Dict[str, Any],
                                            platform: str) -> Dict[str, Any]:
        """Analyze jurisdictional factors for legal action"""        try:
            factors = {
                'target_jurisdiction': 'unknown',
                'violator_jurisdiction': 'unknown',
                'platform_jurisdiction': 'unknown',
                'applicable_laws': [],
                'enforcement_difficulty': 0.5
            }
            
            # Platform jurisdiction mapping
            platform_jurisdictions = {
                'youtube': 'US',
                'tiktok': 'CN/US',  # Complex jurisdiction
                'instagram': 'US',
                'twitter': 'US',
                'facebook': 'US'
            }
            
            factors['platform_jurisdiction'] = platform_jurisdictions.get(platform, 'unknown')
            
            # Try to determine violator jurisdiction from metadata
            creator_info = content_metadata.get('creator_info', {})
            location = creator_info.get('location', '')
            
            if location:
                # Simple location to jurisdiction mapping
                # In production, use a proper geolocation service
                factors['violator_jurisdiction'] = location
            
            # Determine applicable laws
            if factors['platform_jurisdiction'] == 'US':
                factors['applicable_laws'].append('DMCA')
                factors['applicable_laws'].append('US_Copyright_Act')
            
            if factors['violator_jurisdiction'] in ['US', 'CA', 'UK', 'AU']:
                factors['enforcement_difficulty'] = 0.3  # Easier enforcement
            elif factors['violator_jurisdiction'] in ['DE', 'FR', 'ES', 'IT']:
                factors['enforcement_difficulty'] = 0.4  # EU laws
            else:
                factors['enforcement_difficulty'] = 0.8  # Difficult enforcement
            
            return factors
            
        except Exception as e:
            logger.error(f"Jurisdictional analysis failed: {e}")
            return {'enforcement_difficulty': 0.5}
    
    async def _determine_legal_actions(self,
                                     copyright_strength: float,
                                     fair_use_likelihood: float,
                                     commercial_impact: float,
                                     violation_types: List[ViolationType],
                                     platform: str) -> List[ActionType]:
        """Determine specific legal actions to recommend"""        actions = []
        
        try:
            # Strong copyright case
            if copyright_strength > 0.8 and fair_use_likelihood < 0.3:
                actions.append(ActionType.DMCA_TAKEDOWN)
                
                if commercial_impact > 0.6:
                    actions.append(ActionType.CEASE_DESIST)
            
            # Moderate copyright case
            elif copyright_strength > 0.6 and fair_use_likelihood < 0.5:
                actions.append(ActionType.PLATFORM_REPORT)
                actions.append(ActionType.COPYRIGHT_STRIKE)
            
            # Weak copyright case
            elif copyright_strength > 0.4:
                actions.append(ActionType.WARNING)
                actions.append(ActionType.MONITORING)
            
            # Commercial violations
            if ViolationType.COMMERCIAL_USE in violation_types and commercial_impact > 0.5:
                actions.append(ActionType.LEGAL_NOTICE)
            
            return actions
            
        except Exception as e:
            logger.error(f"Legal action determination failed: {e}")
            return []
    
    async def _calculate_legal_confidence(self,
                                        copyright_strength: float,
                                        fair_use_likelihood: float,
                                        precedent_count: int) -> float:
        """Calculate confidence in legal assessment"""        try:
            # Base confidence from copyright strength
            confidence = copyright_strength * 0.4
            
            # Fair use clarity adds confidence
            fair_use_clarity = abs(0.5 - fair_use_likelihood) * 2  # Distance from uncertain middle
            confidence += fair_use_clarity * 0.3
            
            # Legal precedents add confidence
            precedent_factor = min(1.0, precedent_count / 10.0)  # Max benefit at 10 precedents
            confidence += precedent_factor * 0.3
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Legal confidence calculation failed: {e}")
            return 0.5
    
    async def _get_platform_specific_actions(self,
                                           platform: str,
                                           severity: ViolationSeverity,
                                           violation_types: List[ViolationType]) -> List[ActionType]:
        """Get platform-specific recommended actions"""        actions = []
        
        try:
            platform_actions = {
                'youtube': {
                    ViolationSeverity.CRITICAL: [ActionType.COPYRIGHT_STRIKE, ActionType.DMCA_TAKEDOWN],
                    ViolationSeverity.HIGH: [ActionType.COPYRIGHT_STRIKE, ActionType.PLATFORM_REPORT],
                    ViolationSeverity.MEDIUM: [ActionType.PLATFORM_REPORT]
                },
                'tiktok': {
                    ViolationSeverity.CRITICAL: [ActionType.PLATFORM_REPORT, ActionType.DMCA_TAKEDOWN],
                    ViolationSeverity.HIGH: [ActionType.PLATFORM_REPORT],
                    ViolationSeverity.MEDIUM: [ActionType.WARNING]
                },
                'instagram': {
                    ViolationSeverity.CRITICAL: [ActionType.PLATFORM_REPORT, ActionType.DMCA_TAKEDOWN],
                    ViolationSeverity.HIGH: [ActionType.PLATFORM_REPORT],
                    ViolationSeverity.MEDIUM: [ActionType.WARNING]
                },
                'twitter': {
                    ViolationSeverity.CRITICAL: [ActionType.PLATFORM_REPORT, ActionType.DMCA_TAKEDOWN],
                    ViolationSeverity.HIGH: [ActionType.PLATFORM_REPORT],
                    ViolationSeverity.MEDIUM: [ActionType.WARNING]
                }
            }
            
            platform_specific = platform_actions.get(platform, {})
            return platform_specific.get(severity, [])
            
        except Exception as e:
            logger.error(f"Platform-specific action lookup failed: {e}")
            return []
    
    async def generate_takedown_notice(self, analysis: ViolationAnalysis) -> Dict[str, Any]:
        """Generate DMCA takedown notice for the violation"""        try:
            if ActionType.DMCA_TAKEDOWN in analysis.recommended_actions:
                notice = await self.dmca_generator.generate_notice(
                    violation_analysis=analysis,
                    copyright_holder_info=self.config.get('copyright_holder', {}),
                    legal_contact_info=self.config.get('legal_contact', {})
                )
                return notice
            else:
                return {'error': 'DMCA takedown not recommended for this violation'}
                
        except Exception as e:
            logger.error(f"Takedown notice generation failed: {e}")
            return {'error': str(e)}
    
    async def update_analysis_status(self, analysis_id: str, 
                                   new_status: ViolationStatus,
                                   action_taken: Optional[str] = None):
        """Update the status of a violation analysis"""        try:
            if analysis_id in self.analysis_cache:
                analysis = self.analysis_cache[analysis_id]
                analysis.status = new_status
                
                if action_taken:
                    if not hasattr(analysis, 'actions_taken'):
                        analysis.actions_taken = []
                    analysis.actions_taken.append({
                        'action': action_taken,
                        'timestamp': datetime.now(timezone.utc)
                    })
                
                logger.info(f"Updated analysis {analysis_id} status to {new_status.value}")
            else:
                logger.warning(f"Analysis {analysis_id} not found in cache")
                
        except Exception as e:
            logger.error(f"Analysis status update failed: {e}")
    
    async def get_violation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive violation analysis statistics"""        try:
            stats = self.analysis_stats.copy()
            
            # Add cache statistics
            stats['cache_size'] = len(self.analysis_cache)
            
            # Calculate violation rate
            stats['violation_rate'] = (
                stats['violations_detected'] / stats['total_analyses'] 
                if stats['total_analyses'] > 0 else 0
            )
            
            # Severity distribution
            severity_counts = {}
            status_counts = {}
            
            for analysis in self.analysis_cache.values():
                severity = analysis.severity.value
                status = analysis.status.value
                
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                status_counts[status] = status_counts.get(status, 0) + 1
            
            stats['severity_distribution'] = severity_counts
            stats['status_distribution'] = status_counts
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics generation failed: {e}")
            return self.analysis_stats.copy()
    
    async def cleanup(self):
        """Cleanup analyzer resources"""        try:
            # Clear cache
            self.analysis_cache.clear()
            
            # Cleanup components
            await self.evidence_collector.cleanup()
            await self.screenshot_generator.cleanup()
            
            logger.info("Violation Analyzer cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Violation Analyzer cleanup failed: {e}")

# Export main classes
__all__ = [
    'ViolationAnalyzer',
    'ViolationAnalysis',
    'ViolationEvidence',
    'LegalAssessment',
    'ViolationType',
    'ViolationSeverity',
    'ViolationStatus',
    'ActionType'
]
