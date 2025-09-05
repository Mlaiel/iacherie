"""Content Safety Index - AI-Powered Content Moderation Orchestration

Central orchestration system for AI-powered content safety and moderation,
providing real-time content analysis and automated safety enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import json

from .hate_speech_detector import HateSpeechDetector
from .violence_detector import ViolenceDetector
from .adult_content_filter import AdultContentFilter
from .spam_detector import SpamDetector
from .misinformation_detector import MisinformationDetector
from .harassment_detector import HarassmentDetector
from .cyberbullying_detector import CyberbullyingDetector
from .self_harm_detector import SelfHarmDetector
from .drug_content_detector import DrugContentDetector
from .terrorism_detector import TerrorismDetector
from .content_classifier import ContentClassifier

logger = logging.getLogger(__name__)


class SafetyAction(str, Enum):
    """Content safety actions"""
    ALLOW = "allow"
    WARN = "warn"
    RESTRICT = "restrict"
    REMOVE = "remove"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"


class ContentType(str, Enum):
    """Types of content for analysis"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class RiskLevel(str, Enum):
    """Content risk levels"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"


@dataclass
class SafetyAnalysisResult:
    """Comprehensive content safety analysis result"""
    content_id: str
    content_type: ContentType
    overall_risk_level: RiskLevel
    safety_score: float  # 0-100 (100 = completely safe)
    recommended_action: SafetyAction
    detection_results: Dict[str, Any]
    confidence_score: float
    analysis_timestamp: datetime
    processing_time_ms: float
    flags: List[str]
    metadata: Dict[str, Any]


@dataclass
class ModerationAlert:
    """High-priority moderation alert"""
    alert_id: str
    content_id: str
    alert_type: str
    severity: RiskLevel
    detected_issues: List[str]
    recommended_actions: List[str]
    created_at: datetime
    requires_human_review: bool
    escalation_tier: int


class ContentSafetyIndex:
    """Central content safety and moderation orchestrator"""
    
    def __init__(self):
        # Initialize all content safety detectors
        self.hate_speech_detector = HateSpeechDetector()
        self.violence_detector = ViolenceDetector()
        self.adult_content_filter = AdultContentFilter()
        self.spam_detector = SpamDetector()
        self.misinformation_detector = MisinformationDetector()
        self.harassment_detector = HarassmentDetector()
        self.cyberbullying_detector = CyberbullyingDetector()
        self.self_harm_detector = SelfHarmDetector()
        self.drug_content_detector = DrugContentDetector()
        self.terrorism_detector = TerrorismDetector()
        self.content_classifier = ContentClassifier()
        
        # Safety configuration
        self.safety_thresholds = self._initialize_safety_thresholds()
        self.moderation_alerts: List[ModerationAlert] = []
        self.real_time_monitoring = False
    
    def _initialize_safety_thresholds(self) -> Dict[str, float]:
        """Initialize safety detection thresholds"""
        return {
            "hate_speech": 0.8,      # 80% confidence threshold
            "violence": 0.85,        # 85% confidence threshold
            "adult_content": 0.9,    # 90% confidence threshold
            "spam": 0.7,             # 70% confidence threshold
            "misinformation": 0.75,  # 75% confidence threshold
            "harassment": 0.8,       # 80% confidence threshold
            "cyberbullying": 0.8,    # 80% confidence threshold
            "self_harm": 0.95,       # 95% confidence threshold (critical)
            "drug_content": 0.8,     # 80% confidence threshold
            "terrorism": 0.95        # 95% confidence threshold (critical)
        }
    
    async def analyze_content_safety(
        self, 
        content_id: str,
        content: str,
        content_type: ContentType,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SafetyAnalysisResult:
        """Comprehensive content safety analysis with parallel AI detection"""
        try:
            start_time = datetime.utcnow()
            logger.info(f"Starting comprehensive safety analysis for content {content_id}")
            
            # Parallel execution of all safety detectors
            detection_tasks = [
                self._detect_hate_speech(content, user_context),
                self._detect_violence(content, content_type),
                self._detect_adult_content(content, content_type),
                self._detect_spam(content, user_context),
                self._detect_misinformation(content),
                self._detect_harassment(content, user_context),
                self._detect_cyberbullying(content, user_context),
                self._detect_self_harm(content),
                self._detect_drug_content(content),
                self._detect_terrorism(content),
                self._classify_content(content, content_type)
            ]
            
            detection_results = await asyncio.gather(*detection_tasks, return_exceptions=True)
            
            # Process detection results
            processed_results = self._process_detection_results(detection_results)
            
            # Calculate overall risk and safety score
            overall_risk, safety_score = self._calculate_overall_risk(processed_results)
            
            # Determine recommended action
            recommended_action = self._determine_safety_action(overall_risk, safety_score, processed_results)
            
            # Extract flags and calculate confidence
            flags = self._extract_safety_flags(processed_results)
            confidence_score = self._calculate_confidence_score(processed_results)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create analysis result
            analysis_result = SafetyAnalysisResult(
                content_id=content_id,
                content_type=content_type,
                overall_risk_level=overall_risk,
                safety_score=safety_score,
                recommended_action=recommended_action,
                detection_results=processed_results,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.utcnow(),
                processing_time_ms=processing_time,
                flags=flags,
                metadata=metadata or {}
            )
            
            # Generate moderation alerts if necessary
            if overall_risk in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL_RISK]:
                await self._generate_moderation_alert(analysis_result)
            
            logger.info(f"Safety analysis completed for {content_id} - Risk: {overall_risk}, Score: {safety_score}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Content safety analysis failed for {content_id}: {e}")
            return SafetyAnalysisResult(
                content_id=content_id,
                content_type=content_type,
                overall_risk_level=RiskLevel.CRITICAL_RISK,
                safety_score=0.0,
                recommended_action=SafetyAction.ESCALATE,
                detection_results={"error": str(e)},
                confidence_score=0.0,
                analysis_timestamp=datetime.utcnow(),
                processing_time_ms=0.0,
                flags=["analysis_error"],
                metadata={}
            )
    
    async def _detect_hate_speech(self, content: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect hate speech with ML analysis"""
        try:
            result = await self.hate_speech_detector.analyze_hate_speech(content, user_context)
            return {"detector": "hate_speech", "result": result}
        except Exception as e:
            return {"detector": "hate_speech", "error": str(e)}
    
    async def _detect_violence(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Detect violent content with computer vision and NLP"""
        try:
            result = await self.violence_detector.analyze_violence(content, content_type)
            return {"detector": "violence", "result": result}
        except Exception as e:
            return {"detector": "violence", "error": str(e)}
    
    async def _detect_adult_content(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Detect adult/NSFW content"""
        try:
            result = await self.adult_content_filter.analyze_nsfw_content(content, content_type)
            return {"detector": "adult_content", "result": result}
        except Exception as e:
            return {"detector": "adult_content", "error": str(e)}
    
    async def _detect_spam(self, content: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect spam and phishing content"""
        try:
            result = await self.spam_detector.analyze_spam(content, user_context)
            return {"detector": "spam", "result": result}
        except Exception as e:
            return {"detector": "spam", "error": str(e)}
    
    async def _detect_misinformation(self, content: str) -> Dict[str, Any]:
        """Detect misinformation and fake news"""
        try:
            result = await self.misinformation_detector.analyze_misinformation(content)
            return {"detector": "misinformation", "result": result}
        except Exception as e:
            return {"detector": "misinformation", "error": str(e)}
    
    async def _detect_harassment(self, content: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect harassment and targeted abuse"""
        try:
            result = await self.harassment_detector.analyze_harassment(content, user_context)
            return {"detector": "harassment", "result": result}
        except Exception as e:
            return {"detector": "harassment", "error": str(e)}
    
    async def _detect_cyberbullying(self, content: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect cyberbullying patterns"""
        try:
            result = await self.cyberbullying_detector.analyze_cyberbullying(content, user_context)
            return {"detector": "cyberbullying", "result": result}
        except Exception as e:
            return {"detector": "cyberbullying", "error": str(e)}
    
    async def _detect_self_harm(self, content: str) -> Dict[str, Any]:
        """Detect self-harm and suicide content"""
        try:
            result = await self.self_harm_detector.analyze_self_harm(content)
            return {"detector": "self_harm", "result": result}
        except Exception as e:
            return {"detector": "self_harm", "error": str(e)}
    
    async def _detect_drug_content(self, content: str) -> Dict[str, Any]:
        """Detect drug-related content"""
        try:
            result = await self.drug_content_detector.analyze_drug_content(content)
            return {"detector": "drug_content", "result": result}
        except Exception as e:
            return {"detector": "drug_content", "error": str(e)}
    
    async def _detect_terrorism(self, content: str) -> Dict[str, Any]:
        """Detect terrorism and extremist content"""
        try:
            result = await self.terrorism_detector.analyze_terrorism(content)
            return {"detector": "terrorism", "result": result}
        except Exception as e:
            return {"detector": "terrorism", "error": str(e)}
    
    async def _classify_content(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Classify content into categories"""
        try:
            result = await self.content_classifier.classify_content(content, content_type)
            return {"detector": "classification", "result": result}
        except Exception as e:
            return {"detector": "classification", "error": str(e)}
    
    def _process_detection_results(self, detection_results: List[Any]) -> Dict[str, Any]:
        """Process and normalize detection results"""
        processed = {}
        
        for result in detection_results:
            if isinstance(result, dict) and "detector" in result:
                detector_name = result["detector"]
                if "error" in result:
                    processed[detector_name] = {"error": result["error"], "confidence": 0.0}
                else:
                    processed[detector_name] = result.get("result", {})
            elif isinstance(result, Exception):
                processed["unknown_detector"] = {"error": str(result), "confidence": 0.0}
        
        return processed
    
    def _calculate_overall_risk(self, detection_results: Dict[str, Any]) -> tuple[RiskLevel, float]:
        """Calculate overall risk level and safety score"""
        risk_scores = []
        
        for detector, result in detection_results.items():
            if "error" in result:
                continue
            
            confidence = result.get("confidence", 0.0)
            threshold = self.safety_thresholds.get(detector, 0.8)
            
            if confidence >= threshold:
                # High confidence detection of unsafe content
                risk_score = confidence * 100
                
                # Critical detectors get higher weight
                if detector in ["self_harm", "terrorism"]:
                    risk_score *= 1.5
                elif detector in ["violence", "hate_speech"]:
                    risk_score *= 1.2
                
                risk_scores.append(min(100, risk_score))
        
        if not risk_scores:
            return RiskLevel.SAFE, 100.0
        
        # Calculate weighted average risk
        max_risk = max(risk_scores)
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        # Safety score is inverse of risk
        safety_score = max(0, 100 - avg_risk)
        
        # Determine risk level
        if max_risk >= 95:
            risk_level = RiskLevel.CRITICAL_RISK
        elif max_risk >= 80:
            risk_level = RiskLevel.HIGH_RISK
        elif max_risk >= 60:
            risk_level = RiskLevel.MODERATE_RISK
        elif max_risk >= 30:
            risk_level = RiskLevel.LOW_RISK
        else:
            risk_level = RiskLevel.SAFE
        
        return risk_level, round(safety_score, 2)
    
    def _determine_safety_action(
        self, 
        risk_level: RiskLevel, 
        safety_score: float, 
        detection_results: Dict[str, Any]
    ) -> SafetyAction:
        """Determine recommended safety action"""
        
        # Critical risk requires immediate removal
        if risk_level == RiskLevel.CRITICAL_RISK:
            return SafetyAction.REMOVE
        
        # High risk requires restriction or escalation
        elif risk_level == RiskLevel.HIGH_RISK:
            # Check for specific critical detectors
            critical_detections = ["self_harm", "terrorism", "violence"]
            if any(detector in detection_results for detector in critical_detections):
                return SafetyAction.ESCALATE
            else:
                return SafetyAction.RESTRICT
        
        # Moderate risk gets quarantined for review
        elif risk_level == RiskLevel.MODERATE_RISK:
            return SafetyAction.QUARANTINE
        
        # Low risk gets warning
        elif risk_level == RiskLevel.LOW_RISK:
            return SafetyAction.WARN
        
        # Safe content is allowed
        else:
            return SafetyAction.ALLOW
    
    def _extract_safety_flags(self, detection_results: Dict[str, Any]) -> List[str]:
        """Extract safety flags from detection results"""
        flags = []
        
        for detector, result in detection_results.items():
            if "error" in result:
                flags.append(f"{detector}_error")
                continue
            
            confidence = result.get("confidence", 0.0)
            threshold = self.safety_thresholds.get(detector, 0.8)
            
            if confidence >= threshold:
                flags.append(f"{detector}_detected")
                
                # Add severity flags for critical detectors
                if detector in ["self_harm", "terrorism"] and confidence >= 0.95:
                    flags.append(f"{detector}_critical")
        
        return flags
    
    def _calculate_confidence_score(self, detection_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        confidences = []
        
        for detector, result in detection_results.items():
            if "error" not in result:
                confidence = result.get("confidence", 0.0)
                confidences.append(confidence)
        
        if not confidences:
            return 0.0
        
        return round(sum(confidences) / len(confidences), 3)
    
    async def _generate_moderation_alert(self, analysis_result: SafetyAnalysisResult) -> None:
        """Generate high-priority moderation alert"""
        try:
            alert_id = f"alert_{analysis_result.content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine escalation tier
            escalation_tier = 1
            if analysis_result.overall_risk_level == RiskLevel.CRITICAL_RISK:
                escalation_tier = 3
            elif analysis_result.overall_risk_level == RiskLevel.HIGH_RISK:
                escalation_tier = 2
            
            # Determine if human review is required
            requires_human_review = (
                analysis_result.overall_risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL_RISK] or
                any("critical" in flag for flag in analysis_result.flags)
            )
            
            # Create moderation alert
            alert = ModerationAlert(
                alert_id=alert_id,
                content_id=analysis_result.content_id,
                alert_type="content_safety_violation",
                severity=analysis_result.overall_risk_level,
                detected_issues=analysis_result.flags,
                recommended_actions=[analysis_result.recommended_action],
                created_at=datetime.utcnow(),
                requires_human_review=requires_human_review,
                escalation_tier=escalation_tier
            )
            
            self.moderation_alerts.append(alert)
            
            # Log high-priority alert
            logger.warning(f"Moderation alert generated: {alert_id} - {analysis_result.overall_risk_level}")
            
        except Exception as e:
            logger.error(f"Failed to generate moderation alert: {e}")
    
    async def get_moderation_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive moderation dashboard"""
        try:
            # Count alerts by severity
            severity_counts = {}
            for severity in RiskLevel:
                severity_counts[severity] = len([a for a in self.moderation_alerts if a.severity == severity])
            
            # Get recent alerts
            recent_alerts = sorted(
                self.moderation_alerts, 
                key=lambda x: x.created_at, 
                reverse=True
            )[:10]
            
            # Calculate safety metrics
            total_alerts = len(self.moderation_alerts)
            critical_alerts = severity_counts.get(RiskLevel.CRITICAL_RISK, 0)
            high_risk_alerts = severity_counts.get(RiskLevel.HIGH_RISK, 0)
            
            dashboard = {
                "summary": {
                    "total_alerts": total_alerts,
                    "critical_alerts": critical_alerts,
                    "high_risk_alerts": high_risk_alerts,
                    "safety_status": "critical" if critical_alerts > 0 else "normal"
                },
                "severity_breakdown": severity_counts,
                "recent_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "content_id": alert.content_id,
                        "severity": alert.severity,
                        "issues": alert.detected_issues,
                        "created_at": alert.created_at.isoformat(),
                        "requires_review": alert.requires_human_review
                    } for alert in recent_alerts
                ],
                "safety_thresholds": self.safety_thresholds,
                "monitoring_status": "active" if self.real_time_monitoring else "inactive",
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate moderation dashboard: {e}")
            return {"error": str(e)}
    
    async def start_real_time_monitoring(self) -> Dict[str, Any]:
        """Start real-time content safety monitoring"""
        try:
            logger.info("Starting real-time content safety monitoring")
            
            self.real_time_monitoring = True
            
            # Initialize monitoring tasks
            monitoring_tasks = [
                self._monitor_content_stream(),
                self._monitor_safety_alerts(),
                self._update_safety_models()
            ]
            
            # Start monitoring in background
            asyncio.create_task(asyncio.gather(*monitoring_tasks, return_exceptions=True))
            
            return {
                "status": "active",
                "started_at": datetime.utcnow().isoformat(),
                "monitoring_modules": 11,
                "safety_thresholds": self.safety_thresholds
            }
            
        except Exception as e:
            logger.error(f"Failed to start real-time monitoring: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _monitor_content_stream(self) -> None:
        """Monitor content stream for safety violations"""
        while self.real_time_monitoring:
            try:
                # This would integrate with actual content stream
                await asyncio.sleep(10)  # Check every 10 seconds
                logger.debug("Monitoring content stream for safety violations")
            except Exception as e:
                logger.error(f"Content stream monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_safety_alerts(self) -> None:
        """Monitor and process safety alerts"""
        while self.real_time_monitoring:
            try:
                # Process high-priority alerts
                critical_alerts = [a for a in self.moderation_alerts if a.severity == RiskLevel.CRITICAL_RISK]
                
                for alert in critical_alerts:
                    if alert.requires_human_review:
                        logger.warning(f"Critical alert requiring human review: {alert.alert_id}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Safety alerts monitoring error: {e}")
                await asyncio.sleep(15)
    
    async def _update_safety_models(self) -> None:
        """Update safety detection models"""
        while self.real_time_monitoring:
            try:
                # This would update ML models with new training data
                logger.debug("Checking for safety model updates")
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Model update error: {e}")
                await asyncio.sleep(1800)


# Singleton instance for global access
content_safety_index = ContentSafetyIndex()