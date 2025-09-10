"""Ainflue Core Business - Content Moderation Core
===============================================

Enterprise-grade content moderation system providing automated content analysis,
toxicity detection, NSFW filtering, spam detection, community guidelines enforcement,
and human moderation workflows for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib
import time
import numpy as np

# Setup logger
logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    """Content types for moderation"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LINK = "link"
    USER_PROFILE = "user_profile"
    COMMENT = "comment"
    POST = "post"
    MESSAGE = "message"

class ModerationAction(str, Enum):
    """Moderation actions"""
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    REMOVE = "remove"
    QUARANTINE = "quarantine"
    SHADOW_BAN = "shadow_ban"
    WARN_USER = "warn_user"
    SUSPEND_USER = "suspend_user"
    BAN_USER = "ban_user"
    REQUEST_REVIEW = "request_review"

class ModerationStatus(str, Enum):
    """Moderation status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    APPEALED = "appealed"
    FINAL = "final"

class ViolationType(str, Enum):
    """Types of content violations"""
    TOXIC_LANGUAGE = "toxic_language"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    NSFW_CONTENT = "nsfw_content"
    SPAM = "spam"
    SCAM = "scam"
    MISINFORMATION = "misinformation"
    COPYRIGHT_VIOLATION = "copyright_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    SELF_HARM = "self_harm"
    VIOLENCE = "violence"
    ILLEGAL_CONTENT = "illegal_content"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    COMMERCIAL_SPAM = "commercial_spam"
    IMPERSONATION = "impersonation"

class SeverityLevel(str, Enum):
    """Severity levels for violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"

@dataclass
class ModerationRule:
    """Content moderation rule"""
    id: str
    name: str
    description: str
    violation_type: ViolationType
    severity: SeverityLevel
    patterns: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    regex_patterns: List[str] = field(default_factory=list)
    ml_model_threshold: float = 0.8
    action: ModerationAction = ModerationAction.FLAG
    auto_apply: bool = False
    requires_human_review: bool = True
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentSubmission:
    """Content submission for moderation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_type: ContentType = ContentType.TEXT
    content_data: Dict[str, Any] = field(default_factory=dict)
    text_content: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    video_urls: List[str] = field(default_factory=list)
    audio_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    platform: str = "ainflue"
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 5  # 1-10, 10 being highest priority

@dataclass
class ModerationResult:
    """Result of content moderation"""
    submission_id: str
    status: ModerationStatus
    action: ModerationAction
    violations: List[ViolationType] = field(default_factory=list)
    severity: SeverityLevel = SeverityLevel.LOW
    confidence_score: float = 0.0
    rule_matches: List[str] = field(default_factory=list)
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    human_review_notes: Optional[str] = None
    moderator_id: Optional[str] = None
    processed_at: datetime = field(default_factory=datetime.utcnow)
    appeal_deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModerationQueue:
    """Moderation queue for human review"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    submission_ids: List[str] = field(default_factory=list)
    assigned_moderators: List[str] = field(default_factory=list)
    priority_threshold: int = 7
    auto_assignment: bool = True
    max_queue_size: int = 1000
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True

class TextAnalyzer:
    """Text content analyzer"""
    
    def __init__(self):
        self.toxic_keywords = self._load_toxic_keywords()
        self.spam_patterns = self._load_spam_patterns()
        self.compiled_regex = {}
        
    def _load_toxic_keywords(self) -> Set[str]:
        """Load toxic keywords database"""
        # In a real implementation, this would load from a comprehensive database
        return {
            "hate", "kill", "die", "stupid", "idiot", "moron", "retard",
            "nazi", "terrorist", "violence", "abuse", "harassment"
        }
    
    def _load_spam_patterns(self) -> List[str]:
        """Load spam detection patterns"""
        return [
            r"(?i)(buy now|click here|limited time|act fast|special offer)",
            r"(?i)(make money|work from home|get rich|easy money)",
            r"(?i)(viagra|casino|lottery|winner|congratulations)",
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            r"(?i)(follow me|subscribe|like and share|check my profile)"
        ]
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content for violations"""
        if not text:
            return {"violations": [], "confidence": 0.0, "details": {}}
        
        violations = []
        confidence_scores = {}
        details = {}
        
        # Toxicity analysis
        toxic_score = self._analyze_toxicity(text)
        if toxic_score > 0.7:
            violations.append(ViolationType.TOXIC_LANGUAGE)
            confidence_scores[ViolationType.TOXIC_LANGUAGE.value] = toxic_score
        
        # Hate speech detection
        hate_score = self._analyze_hate_speech(text)
        if hate_score > 0.8:
            violations.append(ViolationType.HATE_SPEECH)
            confidence_scores[ViolationType.HATE_SPEECH.value] = hate_score
        
        # Spam detection
        spam_score = self._analyze_spam(text)
        if spam_score > 0.6:
            violations.append(ViolationType.SPAM)
            confidence_scores[ViolationType.SPAM.value] = spam_score
        
        # NSFW content detection
        nsfw_score = self._analyze_nsfw_text(text)
        if nsfw_score > 0.7:
            violations.append(ViolationType.NSFW_CONTENT)
            confidence_scores[ViolationType.NSFW_CONTENT.value] = nsfw_score
        
        details = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "toxicity_score": toxic_score,
            "hate_speech_score": hate_score,
            "spam_score": spam_score,
            "nsfw_score": nsfw_score,
            "detected_patterns": self._get_detected_patterns(text)
        }
        
        overall_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
        
        return {
            "violations": violations,
            "confidence": overall_confidence,
            "confidence_scores": confidence_scores,
            "details": details
        }
    
    def _analyze_toxicity(self, text: str) -> float:
        """Analyze text for toxic language"""
        text_lower = text.lower()
        toxic_words_found = sum(1 for word in self.toxic_keywords if word in text_lower)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # Simple toxicity score based on ratio of toxic words
        base_score = min(toxic_words_found / total_words * 5, 1.0)
        
        # Boost score for explicit profanity patterns
        profanity_patterns = [r"\b(f[*!@#$%^&*()_+]ck|sh[*!@#$%^&*()_+]t|b[*!@#$%^&*()_+]tch)\b"]
        for pattern in profanity_patterns:
            if re.search(pattern, text_lower):
                base_score = min(base_score + 0.3, 1.0)
        
        return base_score
    
    def _analyze_hate_speech(self, text: str) -> float:
        """Analyze text for hate speech"""
        hate_indicators = [
            r"(?i)\b(kill|murder|die|suicide)\s+(all|every)?\s*(jews|muslims|christians|blacks|whites|gays|women|men)",
            r"(?i)\b(hitler|nazi|genocide|holocaust)\s+(was|is)\s+(right|good|justified)",
            r"(?i)\b(rape|sexual assault)\s+(is|was)\s+(funny|deserved|justified)",
            r"(?i)\b(go back to|deport all|ban all)\s+[a-z]+s?\b"
        ]
        
        score = 0.0
        for pattern in hate_indicators:
            if re.search(pattern, text):
                score = min(score + 0.4, 1.0)
        
        return score
    
    def _analyze_spam(self, text: str) -> float:
        """Analyze text for spam content"""
        spam_score = 0.0
        
        for pattern in self.spam_patterns:
            matches = len(re.findall(pattern, text))
            spam_score += matches * 0.2
        
        # Check for excessive capitalization
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                spam_score += 0.3
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if c in "!?@#$%^&*()") / len(text) if text else 0
        if punct_ratio > 0.3:
            spam_score += 0.2
        
        # Check for repeated characters
        if re.search(r"(.)\1{4,}", text):
            spam_score += 0.2
        
        return min(spam_score, 1.0)
    
    def _analyze_nsfw_text(self, text: str) -> float:
        """Analyze text for NSFW content"""
        nsfw_keywords = {
            "sex", "sexual", "porn", "pornography", "nude", "naked", "masturbate",
            "orgasm", "erotic", "xxx", "adult", "fetish", "kinky", "horny"
        }
        
        text_lower = text.lower()
        nsfw_count = sum(1 for keyword in nsfw_keywords if keyword in text_lower)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        return min(nsfw_count / total_words * 3, 1.0)
    
    def _get_detected_patterns(self, text: str) -> List[str]:
        """Get list of detected violation patterns"""
        detected = []
        
        for i, pattern in enumerate(self.spam_patterns):
            if re.search(pattern, text):
                detected.append(f"spam_pattern_{i}")
        
        return detected

class ImageAnalyzer:
    """Image content analyzer"""
    
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """Analyze image content for violations"""
        # Placeholder for image analysis
        # In a real implementation, this would use computer vision models
        
        # Simulate analysis
        await asyncio.sleep(0.1)
        
        violations = []
        confidence_scores = {}
        
        # Simulate NSFW detection
        nsfw_score = np.random.random() * 0.3  # Low random score for demo
        if nsfw_score > 0.8:
            violations.append(ViolationType.NSFW_CONTENT)
            confidence_scores[ViolationType.NSFW_CONTENT.value] = nsfw_score
        
        details = {
            "image_url": image_url,
            "nsfw_score": nsfw_score,
            "detected_objects": ["person", "text"],  # Placeholder
            "inappropriate_objects": []
        }
        
        return {
            "violations": violations,
            "confidence": max(confidence_scores.values()) if confidence_scores else 0.0,
            "confidence_scores": confidence_scores,
            "details": details
        }

class ContentModerationCore:
    """Core content moderation system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.rules: Dict[str, ModerationRule] = {}
        self.queues: Dict[str, ModerationQueue] = {}
        self.pending_submissions: Dict[str, ContentSubmission] = {}
        self.moderation_results: Dict[str, ModerationResult] = {}
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.auto_moderation_enabled = True
        self.human_review_threshold = 0.7
        self.metrics = {
            'total_submissions': 0,
            'auto_approved': 0,
            'auto_rejected': 0,
            'human_reviewed': 0,
            'violations_detected': 0,
            'false_positives': 0
        }
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info(f"Content Moderation Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize content moderation system"""
        try:
            # Create default moderation queues
            await self._create_default_queues()
            
            logger.info("Content Moderation Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Content Moderation Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start content moderation system"""
        try:
            logger.info("Content Moderation Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Content Moderation Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop content moderation system"""
        try:
            logger.info("Content Moderation Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Content Moderation Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if analyzers are working
            test_result = await self.text_analyzer.analyze_text("test content")
            if 'violations' not in test_result:
                return False
            
            # Check queue sizes
            for queue in self.queues.values():
                if len(queue.submission_ids) > queue.max_queue_size:
                    logger.warning(f"Queue {queue.name} is at capacity")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _initialize_default_rules(self):
        """Initialize default moderation rules"""
        default_rules = [
            ModerationRule(
                id="toxic_language",
                name="Toxic Language Detection",
                description="Detect toxic and offensive language",
                violation_type=ViolationType.TOXIC_LANGUAGE,
                severity=SeverityLevel.HIGH,
                keywords=["hate", "kill", "die", "stupid"],
                action=ModerationAction.FLAG,
                auto_apply=True,
                requires_human_review=False
            ),
            ModerationRule(
                id="hate_speech",
                name="Hate Speech Detection",
                description="Detect hate speech and discrimination",
                violation_type=ViolationType.HATE_SPEECH,
                severity=SeverityLevel.EXTREME,
                action=ModerationAction.REMOVE,
                auto_apply=True,
                requires_human_review=True
            ),
            ModerationRule(
                id="spam_detection",
                name="Spam Detection",
                description="Detect spam and promotional content",
                violation_type=ViolationType.SPAM,
                severity=SeverityLevel.MEDIUM,
                action=ModerationAction.QUARANTINE,
                auto_apply=True,
                requires_human_review=False
            ),
            ModerationRule(
                id="nsfw_content",
                name="NSFW Content Detection",
                description="Detect not safe for work content",
                violation_type=ViolationType.NSFW_CONTENT,
                severity=SeverityLevel.HIGH,
                action=ModerationAction.FLAG,
                auto_apply=False,
                requires_human_review=True
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    async def _create_default_queues(self):
        """Create default moderation queues"""
        queues = [
            ModerationQueue(
                id="high_priority",
                name="High Priority Review",
                description="High priority content requiring immediate review",
                priority_threshold=8
            ),
            ModerationQueue(
                id="standard_review",
                name="Standard Review",
                description="Standard content moderation queue",
                priority_threshold=5
            ),
            ModerationQueue(
                id="appeals",
                name="Appeals Review",
                description="Appeals and disputed moderation decisions",
                priority_threshold=7
            )
        ]
        
        for queue in queues:
            self.queues[queue.id] = queue
    
    async def submit_content(self, submission: ContentSubmission) -> str:
        """Submit content for moderation"""
        try:
            # Store submission
            self.pending_submissions[submission.id] = submission
            self.metrics['total_submissions'] += 1
            
            # Process immediately if auto-moderation is enabled
            if self.auto_moderation_enabled:
                result = await self._process_submission(submission)
                
                # Apply automatic action if confidence is high enough
                if result.confidence_score >= 0.9 and not self._requires_human_review(result):
                    await self._apply_moderation_action(submission, result)
                else:
                    # Add to human review queue
                    await self._add_to_review_queue(submission, result)
            else:
                # Add directly to human review queue
                await self._add_to_review_queue(submission, None)
            
            logger.info(f"Content submission {submission.id} processed")
            return submission.id
            
        except Exception as e:
            logger.error(f"Failed to submit content: {str(e)}")
            raise
    
    async def _process_submission(self, submission: ContentSubmission) -> ModerationResult:
        """Process content submission through AI analysis"""
        violations = []
        confidence_scores = {}
        ai_analysis = {}
        rule_matches = []
        
        try:
            # Analyze text content
            if submission.text_content:
                text_result = await self.text_analyzer.analyze_text(submission.text_content)
                violations.extend(text_result['violations'])
                confidence_scores.update(text_result['confidence_scores'])
                ai_analysis['text_analysis'] = text_result['details']
            
            # Analyze images
            if submission.image_urls:
                for image_url in submission.image_urls:
                    image_result = await self.image_analyzer.analyze_image(image_url)
                    violations.extend(image_result['violations'])
                    confidence_scores.update(image_result['confidence_scores'])
                    ai_analysis[f'image_analysis_{image_url}'] = image_result['details']
            
            # Check against rules
            for rule_id, rule in self.rules.items():
                if rule.active and self._rule_matches(submission, rule):
                    violations.append(rule.violation_type)
                    rule_matches.append(rule_id)
                    confidence_scores[rule.violation_type.value] = rule.ml_model_threshold
            
            # Determine overall severity and action
            severity = self._calculate_severity(violations)
            action = self._determine_action(violations, confidence_scores)
            status = ModerationStatus.PENDING
            
            # Overall confidence score
            overall_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
            
            result = ModerationResult(
                submission_id=submission.id,
                status=status,
                action=action,
                violations=list(set(violations)),  # Remove duplicates
                severity=severity,
                confidence_score=overall_confidence,
                rule_matches=rule_matches,
                ai_analysis=ai_analysis
            )
            
            self.moderation_results[submission.id] = result
            
            if violations:
                self.metrics['violations_detected'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process submission {submission.id}: {str(e)}")
            # Return default rejection result
            return ModerationResult(
                submission_id=submission.id,
                status=ModerationStatus.REJECTED,
                action=ModerationAction.REJECT,
                violations=[ViolationType.INAPPROPRIATE_CONTENT],
                severity=SeverityLevel.MEDIUM,
                confidence_score=0.5
            )
    
    def _rule_matches(self, submission: ContentSubmission, rule: ModerationRule) -> bool:
        """Check if submission matches a moderation rule"""
        if not submission.text_content:
            return False
        
        text_lower = submission.text_content.lower()
        
        # Check keywords
        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                return True
        
        # Check regex patterns
        for pattern in rule.regex_patterns:
            if re.search(pattern, submission.text_content, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_severity(self, violations: List[ViolationType]) -> SeverityLevel:
        """Calculate overall severity based on violations"""
        if not violations:
            return SeverityLevel.LOW
        
        severity_map = {
            ViolationType.HATE_SPEECH: SeverityLevel.EXTREME,
            ViolationType.HARASSMENT: SeverityLevel.HIGH,
            ViolationType.NSFW_CONTENT: SeverityLevel.HIGH,
            ViolationType.TOXIC_LANGUAGE: SeverityLevel.HIGH,
            ViolationType.VIOLENCE: SeverityLevel.EXTREME,
            ViolationType.ILLEGAL_CONTENT: SeverityLevel.EXTREME,
            ViolationType.SELF_HARM: SeverityLevel.CRITICAL,
            ViolationType.SPAM: SeverityLevel.MEDIUM,
            ViolationType.MISINFORMATION: SeverityLevel.HIGH,
            ViolationType.COPYRIGHT_VIOLATION: SeverityLevel.MEDIUM,
            ViolationType.PRIVACY_VIOLATION: SeverityLevel.HIGH,
            ViolationType.SCAM: SeverityLevel.HIGH,
            ViolationType.COMMERCIAL_SPAM: SeverityLevel.LOW,
            ViolationType.IMPERSONATION: SeverityLevel.HIGH,
            ViolationType.INAPPROPRIATE_CONTENT: SeverityLevel.MEDIUM
        }
        
        max_severity = SeverityLevel.LOW
        severity_order = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, 
                         SeverityLevel.CRITICAL, SeverityLevel.EXTREME]
        
        for violation in violations:
            violation_severity = severity_map.get(violation, SeverityLevel.LOW)
            if severity_order.index(violation_severity) > severity_order.index(max_severity):
                max_severity = violation_severity
        
        return max_severity
    
    def _determine_action(self, violations: List[ViolationType], confidence_scores: Dict[str, float]) -> ModerationAction:
        """Determine moderation action based on violations and confidence"""
        if not violations:
            return ModerationAction.APPROVE
        
        action_map = {
            ViolationType.HATE_SPEECH: ModerationAction.REMOVE,
            ViolationType.HARASSMENT: ModerationAction.REMOVE,
            ViolationType.VIOLENCE: ModerationAction.REMOVE,
            ViolationType.ILLEGAL_CONTENT: ModerationAction.REMOVE,
            ViolationType.SELF_HARM: ModerationAction.REMOVE,
            ViolationType.NSFW_CONTENT: ModerationAction.FLAG,
            ViolationType.TOXIC_LANGUAGE: ModerationAction.FLAG,
            ViolationType.SPAM: ModerationAction.QUARANTINE,
            ViolationType.SCAM: ModerationAction.REMOVE,
            ViolationType.MISINFORMATION: ModerationAction.FLAG,
            ViolationType.COPYRIGHT_VIOLATION: ModerationAction.REMOVE,
            ViolationType.PRIVACY_VIOLATION: ModerationAction.REMOVE,
            ViolationType.COMMERCIAL_SPAM: ModerationAction.QUARANTINE,
            ViolationType.IMPERSONATION: ModerationAction.REMOVE,
            ViolationType.INAPPROPRIATE_CONTENT: ModerationAction.FLAG
        }
        
        # Find the most severe action
        action_severity = {
            ModerationAction.APPROVE: 0,
            ModerationAction.FLAG: 1,
            ModerationAction.QUARANTINE: 2,
            ModerationAction.WARN_USER: 3,
            ModerationAction.REMOVE: 4,
            ModerationAction.SUSPEND_USER: 5,
            ModerationAction.BAN_USER: 6
        }
        
        max_action = ModerationAction.APPROVE
        for violation in violations:
            action = action_map.get(violation, ModerationAction.FLAG)
            if action_severity[action] > action_severity[max_action]:
                max_action = action
        
        return max_action
    
    def _requires_human_review(self, result: ModerationResult) -> bool:
        """Check if result requires human review"""
        # Always require human review for extreme violations
        if result.severity == SeverityLevel.EXTREME:
            return True
        
        # Require review for low confidence scores
        if result.confidence_score < self.human_review_threshold:
            return True
        
        # Check if any matched rules require human review
        for rule_id in result.rule_matches:
            rule = self.rules.get(rule_id)
            if rule and rule.requires_human_review:
                return True
        
        return False
    
    async def _apply_moderation_action(self, submission: ContentSubmission, result: ModerationResult):
        """Apply automatic moderation action"""
        try:
            result.status = ModerationStatus.FINAL
            
            if result.action == ModerationAction.APPROVE:
                self.metrics['auto_approved'] += 1
                logger.info(f"Auto-approved submission {submission.id}")
            elif result.action in [ModerationAction.REJECT, ModerationAction.REMOVE]:
                self.metrics['auto_rejected'] += 1
                logger.info(f"Auto-rejected submission {submission.id} for {result.violations}")
            else:
                logger.info(f"Applied action {result.action.value} to submission {submission.id}")
            
            # Update result
            self.moderation_results[submission.id] = result
            
        except Exception as e:
            logger.error(f"Failed to apply moderation action: {str(e)}")
    
    async def _add_to_review_queue(self, submission: ContentSubmission, result: Optional[ModerationResult]):
        """Add submission to human review queue"""
        try:
            # Determine appropriate queue based on priority
            queue_id = "standard_review"
            
            if submission.priority >= 8:
                queue_id = "high_priority"
            elif result and result.severity in [SeverityLevel.CRITICAL, SeverityLevel.EXTREME]:
                queue_id = "high_priority"
            
            queue = self.queues.get(queue_id)
            if queue and len(queue.submission_ids) < queue.max_queue_size:
                queue.submission_ids.append(submission.id)
                
                if result:
                    result.status = ModerationStatus.UNDER_REVIEW
                    self.moderation_results[submission.id] = result
                
                self.metrics['human_reviewed'] += 1
                logger.info(f"Added submission {submission.id} to queue {queue_id}")
            else:
                logger.warning(f"Queue {queue_id} is full, defaulting to standard review")
                # Try standard queue as fallback
                standard_queue = self.queues.get("standard_review")
                if standard_queue:
                    standard_queue.submission_ids.append(submission.id)
                    
        except Exception as e:
            logger.error(f"Failed to add to review queue: {str(e)}")
    
    async def moderate_submission(self, submission_id: str, moderator_id: str,
                                action: ModerationAction, notes: Optional[str] = None) -> bool:
        """Human moderator reviews and decides on submission"""
        try:
            if submission_id not in self.moderation_results:
                return False
            
            result = self.moderation_results[submission_id]
            result.action = action
            result.status = ModerationStatus.FINAL
            result.moderator_id = moderator_id
            result.human_review_notes = notes
            result.processed_at = datetime.utcnow()
            
            # Set appeal deadline for rejected content
            if action in [ModerationAction.REJECT, ModerationAction.REMOVE]:
                result.appeal_deadline = datetime.utcnow() + timedelta(days=7)
            
            # Remove from review queues
            for queue in self.queues.values():
                if submission_id in queue.submission_ids:
                    queue.submission_ids.remove(submission_id)
            
            logger.info(f"Submission {submission_id} moderated by {moderator_id}: {action.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to moderate submission {submission_id}: {str(e)}")
            return False
    
    async def appeal_decision(self, submission_id: str, user_id: str, appeal_reason: str) -> bool:
        """Submit appeal for moderation decision"""
        try:
            if submission_id not in self.moderation_results:
                return False
            
            result = self.moderation_results[submission_id]
            
            # Check if appeal deadline has passed
            if result.appeal_deadline and datetime.utcnow() > result.appeal_deadline:
                return False
            
            # Update status and add to appeals queue
            result.status = ModerationStatus.APPEALED
            result.metadata['appeal'] = {
                'user_id': user_id,
                'reason': appeal_reason,
                'submitted_at': datetime.utcnow().isoformat()
            }
            
            appeals_queue = self.queues.get("appeals")
            if appeals_queue:
                appeals_queue.submission_ids.append(submission_id)
            
            logger.info(f"Appeal submitted for submission {submission_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit appeal: {str(e)}")
            return False
    
    def add_moderation_rule(self, rule: ModerationRule) -> bool:
        """Add new moderation rule"""
        try:
            self.rules[rule.id] = rule
            logger.info(f"Added moderation rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add rule: {str(e)}")
            return False
    
    def update_moderation_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing moderation rule"""
        try:
            if rule_id not in self.rules:
                return False
            
            rule = self.rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.utcnow()
            logger.info(f"Updated moderation rule: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update rule: {str(e)}")
            return False
    
    def get_moderation_result(self, submission_id: str) -> Optional[ModerationResult]:
        """Get moderation result for submission"""
        return self.moderation_results.get(submission_id)
    
    def get_queue_status(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Get status of moderation queue"""
        queue = self.queues.get(queue_id)
        if not queue:
            return None
        
        return {
            'id': queue.id,
            'name': queue.name,
            'pending_submissions': len(queue.submission_ids),
            'assigned_moderators': len(queue.assigned_moderators),
            'max_capacity': queue.max_queue_size,
            'utilization': len(queue.submission_ids) / queue.max_queue_size,
            'active': queue.active
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        active_queues = sum(1 for queue in self.queues.values() if queue.active)
        total_pending = sum(len(queue.submission_ids) for queue in self.queues.values())
        
        return {
            'level': self.level,
            'total_submissions': self.metrics['total_submissions'],
            'auto_approved': self.metrics['auto_approved'],
            'auto_rejected': self.metrics['auto_rejected'],
            'human_reviewed': self.metrics['human_reviewed'],
            'violations_detected': self.metrics['violations_detected'],
            'false_positives': self.metrics['false_positives'],
            'active_rules': len([rule for rule in self.rules.values() if rule.active]),
            'total_rules': len(self.rules),
            'active_queues': active_queues,
            'total_pending_review': total_pending,
            'auto_moderation_enabled': self.auto_moderation_enabled,
            'human_review_threshold': self.human_review_threshold,
            'supported_content_types': [ct.value for ct in ContentType],
            'supported_violation_types': [vt.value for vt in ViolationType]
        }

# Global instance
content_moderation_core = ContentModerationCore()

# Convenience functions
async def submit_content_for_moderation(content_type: ContentType, content_data: Dict[str, Any],
                                       text_content: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """Submit content for moderation"""
    submission = ContentSubmission(
        content_type=content_type,
        content_data=content_data,
        text_content=text_content,
        user_id=user_id
    )
    return await content_moderation_core.submit_content(submission)

async def moderate_content(submission_id: str, moderator_id: str, action: ModerationAction,
                          notes: Optional[str] = None) -> bool:
    """Human moderator decision on content"""
    return await content_moderation_core.moderate_submission(submission_id, moderator_id, action, notes)

def get_moderation_status(submission_id: str) -> Optional[ModerationResult]:
    """Get moderation result"""
    return content_moderation_core.get_moderation_result(submission_id)

# Module exports
__all__ = [
    "ContentModerationCore", "ContentSubmission", "ModerationResult", "ModerationRule",
    "ModerationQueue", "TextAnalyzer", "ImageAnalyzer", "ContentType", "ModerationAction",
    "ModerationStatus", "ViolationType", "SeverityLevel", "content_moderation_core",
    "submit_content_for_moderation", "moderate_content", "get_moderation_status"
]

logger.info("Content Moderation Core module loaded")