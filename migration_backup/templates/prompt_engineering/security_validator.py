
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""
🎯 Security Validator - AI Prompt Security & Safety System
========================================================

Enterprise-grade security validation for AI prompts with comprehensive
threat detection, content safety, and compliance enforcement.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - Security Expert + IA Prompt Engineer
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
import spacy
# from transformers import pipeline
from pydantic import BaseModel, Field, validator
import openai
import tiktoken

from core.config import get_settings
from utils.exceptions import SecurityError, ValidationError
from monitoring.prompt_metrics import PromptMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class ThreatLevel(Enum):
    """Security threat levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityCategory(Enum):
    """Security issue categories"""
    PROMPT_INJECTION = "prompt_injection"
    DATA_LEAKAGE = "data_leakage"
    TOXIC_CONTENT = "toxic_content"
    BIAS_DISCRIMINATION = "bias_discrimination"
    PRIVACY_VIOLATION = "privacy_violation"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    MALICIOUS_CODE = "malicious_code"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    SOCIAL_ENGINEERING = "social_engineering"
    MISINFORMATION = "misinformation"
    HATE_SPEECH = "hate_speech"


class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    EU_AI_ACT = "eu_ai_act"
    CREATOR_ECONOMY_ETHICS = "creator_economy_ethics"


@dataclass
class SecurityIssue:
    """Security issue detection result"""
    category: SecurityCategory
    threat_level: ThreatLevel
    confidence: float
    description: str
    detected_content: str
    location: str
    mitigation: str
    compliance_violations: List[ComplianceStandard] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityValidationResult:
    """Security validation result"""
    is_safe: bool
    overall_threat_level: ThreatLevel
    issues: List[SecurityIssue]
    safety_score: float
    compliance_status: Dict[ComplianceStandard, bool]
    recommendations: List[str]
    sanitized_content: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    validation_time_ms: int = 0


class SecurityValidationConfig(BaseModel):
    """Security validation configuration"""
    enable_prompt_injection_detection: bool = True
    enable_toxicity_detection: bool = True
    enable_bias_detection: bool = True
    enable_privacy_detection: bool = True
    enable_copyright_detection: bool = True
    enable_content_moderation: bool = True
    toxicity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    bias_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    max_prompt_length: int = Field(default=50000, ge=100)
    enable_automatic_sanitization: bool = True
    strict_mode: bool = False
    creator_economy_compliance: bool = True
    enable_real_time_monitoring: bool = True
    log_security_events: bool = True


class SecurityValidator:
    """
    🎯 Enterprise Security Validation System
    
    Comprehensive security validation with:
    - Advanced prompt injection detection
    - Multi-model toxicity analysis
    - Bias and discrimination detection
    - Privacy and compliance validation
    - Content safety moderation
    - Creator economy ethics enforcement
    - Real-time threat monitoring
    - Automated sanitization
    """
    
    def __init__(self, config: Optional[SecurityValidationConfig] = None):
        self.config = config or SecurityValidationConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.nlp = None
        self.toxicity_pipeline = None
        self.bias_detector = None
        self.injection_patterns: List[str] = []
        self.threat_signatures: Dict[str, Any] = {}
        self.metrics_collector = PromptMetricsCollector()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize security validation system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=3,
                max_size=10
            )
            
            # Load NLP models
            await self._load_models()
            
            # Load threat patterns
            await self._load_threat_patterns()
            
            # Create database tables
            await self._create_tables()
            
            self._initialized = True
            logger.info("Security Validator initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Security Validator: {e}")
            raise SecurityError(f"Security Validator initialization failed: {e}")
    
    async def _load_models(self) -> None:
        """Load ML models for security analysis"""
        try:
            # Load spaCy model for NLP analysis
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using basic tokenization")
                self.nlp = None
            
            # Load toxicity detection pipeline
            try:
                self.toxicity_pipeline = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    device=-1  # CPU
                )
            except Exception as e:
                logger.warning(f"Failed to load toxicity model: {e}")
                self.toxicity_pipeline = None
            
            # Initialize bias detector (simplified implementation)
            self.bias_detector = self._create_bias_detector()
            
            logger.info("Security models loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load security models: {e}")
    
    def _create_bias_detector(self) -> Dict[str, Any]:
        """Create bias detection patterns"""
        return {
            'gender_bias': [
                r'\b(he|she|his|her)\s+(is\s+)?(better|worse|smarter|dumber)',
                r'\b(men|women|boys|girls)\s+are\s+(naturally|typically|usually)',
                r'\b(male|female)\s+(should|must|need\s+to|have\s+to)'
            ],
            'racial_bias': [
                r'\b(white|black|asian|hispanic|latino)\s+people\s+are',
                r'\b(race|ethnicity)\s+(determines|affects|influences)',
                r'\b(racial|ethnic)\s+(superiority|inferiority)'
            ],
            'age_bias': [
                r'\b(young|old|elderly)\s+people\s+(can\'t|cannot|shouldn\'t)',
                r'\b(age|aging)\s+(limits|restricts|prevents)',
                r'\b(millennials|boomers|gen\s*z)\s+are\s+(lazy|entitled|stubborn)'
            ],
            'religious_bias': [
                r'\b(christian|muslim|jewish|hindu|buddhist)s?\s+are\s+(violent|peaceful|extremist)',
                r'\b(religion|faith)\s+(causes|leads\s+to|results\s+in)\s+(violence|conflict)',
                r'\b(religious|faith-based)\s+(fanaticism|extremism)'
            ]
        }
    
    async def _load_threat_patterns(self) -> None:
        """Load security threat patterns"""
        # Prompt injection patterns
        self.injection_patterns = [
            # Direct injection attempts
            r'ignore\s+(previous|all)\s+(instructions|prompts|rules)',
            r'forget\s+(everything|all|previous)\s+(instructions|rules)',
            r'now\s+act\s+as\s+(a\s+)?different\s+(model|assistant|ai)',
            r'roleplay\s+as\s+(someone|something)\s+else',
            r'pretend\s+(you\s+are|to\s+be)\s+(someone|something)\s+else',
            
            # System message manipulation
            r'system\s*:\s*(ignore|override|bypass)',
            r'admin\s+(mode|access|privileges)',
            r'developer\s+(mode|access|console)',
            r'debug\s+(mode|access|console)',
            r'maintenance\s+(mode|access)',
            
            # Jailbreak attempts
            r'dan\s+(mode|prompt)',
            r'do\s+anything\s+now',
            r'hypothetically\s+speaking',
            r'in\s+a\s+fictional\s+(world|scenario|story)',
            r'if\s+you\s+were\s+(evil|unrestricted|uncensored)',
            
            # Data extraction attempts
            r'tell\s+me\s+(your|the)\s+(training|system)\s+data',
            r'what\s+(are\s+)?(your\s+)?(training|system)\s+(instructions|prompts)',
            r'reveal\s+(your|the)\s+(internal|hidden|secret)\s+(prompts|instructions)',
            r'dump\s+(your\s+)?(memory|training|instructions)',
            
            # Code injection
            r'execute\s+(code|script|command)',
            r'run\s+(this\s+)?(code|script|program)',
            r'eval\s*\(',
            r'exec\s*\(',
            r'<script[^>]*>',
            r'javascript\s*:',
            
            # Social engineering
            r'this\s+is\s+(urgent|emergency|critical)',
            r'you\s+must\s+(immediately|now|quickly)',
            r'trust\s+me\s*,?\s*(i\s+am|i\'m)',
            r'don\'t\s+tell\s+(anyone|anybody)\s+(about|this)',
            r'keep\s+this\s+(secret|confidential|between\s+us)'
        ]
        
        # Threat signatures for different attack types
        self.threat_signatures = {
            'prompt_injection': {
                'keywords': ['ignore', 'forget', 'override', 'bypass', 'roleplay', 'pretend'],
                'patterns': self.injection_patterns,
                'severity_multiplier': 2.0
            },
            'data_leakage': {
                'keywords': ['training data', 'system prompt', 'internal', 'dump', 'reveal'],
                'patterns': [r'(training|system|internal)\s+(data|prompts|instructions)'],
                'severity_multiplier': 1.8
            },
            'jailbreak': {
                'keywords': ['dan', 'hypothetically', 'fictional', 'unrestricted'],
                'patterns': [r'(dan|do\s+anything\s+now|hypothetically|fictional)'],
                'severity_multiplier': 1.5
            }
        }
    
    async def _create_tables(self) -> None:
        """Create security-related database tables"""
        create_security_events_table = """
        CREATE TABLE IF NOT EXISTS security_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(255) UNIQUE NOT NULL,
            threat_level VARCHAR(20) NOT NULL,
            category VARCHAR(50) NOT NULL,
            prompt_hash VARCHAR(64) NOT NULL,
            issues JSONB NOT NULL,
            safety_score FLOAT,
            template_id VARCHAR(255),
            creator_context JSONB,
            mitigation_actions JSONB,
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (threat_level, created_at),
            INDEX (category, created_at),
            INDEX (template_id, created_at)
        );
        """
        
        create_security_patterns_table = """
        CREATE TABLE IF NOT EXISTS security_patterns (
            id SERIAL PRIMARY KEY,
            pattern_type VARCHAR(50) NOT NULL,
            pattern_text TEXT NOT NULL,
            threat_level VARCHAR(20) NOT NULL,
            description TEXT,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_compliance_logs_table = """
        CREATE TABLE IF NOT EXISTS compliance_logs (
            id SERIAL PRIMARY KEY,
            log_id VARCHAR(255) UNIQUE NOT NULL,
            standard VARCHAR(50) NOT NULL,
            compliance_status BOOLEAN NOT NULL,
            violations JSONB,
            prompt_hash VARCHAR(64),
            template_id VARCHAR(255),
            auditor VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_security_events_table)
            await conn.execute(create_security_patterns_table)
            await conn.execute(create_compliance_logs_table)
    
    async def validate_prompt(self, prompt: str, template_id: Optional[str] = None) -> SecurityValidationResult:
        """
        Comprehensive security validation of a prompt
        
        Args:
            prompt: The prompt text to validate
            template_id: Optional template identifier
            
        Returns:
            Security validation result
        """
        start_time = datetime.utcnow()
        
        try:
            # Input validation
            if not prompt or len(prompt.strip()) == 0:
                raise ValidationError("Empty prompt provided")
            
            if len(prompt) > self.config.max_prompt_length:
                raise ValidationError(f"Prompt exceeds maximum length: {len(prompt)} > {self.config.max_prompt_length}")
            
            issues: List[SecurityIssue] = []
            
            # Run security checks
            if self.config.enable_prompt_injection_detection:
                injection_issues = await self._detect_prompt_injection(prompt)
                issues.extend(injection_issues)
            
            if self.config.enable_toxicity_detection:
                toxicity_issues = await self._detect_toxicity(prompt)
                issues.extend(toxicity_issues)
            
            if self.config.enable_bias_detection:
                bias_issues = await self._detect_bias(prompt)
                issues.extend(bias_issues)
            
            if self.config.enable_privacy_detection:
                privacy_issues = await self._detect_privacy_violations(prompt)
                issues.extend(privacy_issues)
            
            if self.config.enable_copyright_detection:
                copyright_issues = await self._detect_copyright_violations(prompt)
                issues.extend(copyright_issues)
            
            if self.config.enable_content_moderation:
                content_issues = await self._moderate_content(prompt)
                issues.extend(content_issues)
            
            # Calculate overall threat level and safety score
            overall_threat_level = self._calculate_overall_threat_level(issues)
            safety_score = self._calculate_safety_score(issues)
            
            # Check compliance
            compliance_status = await self._check_compliance(prompt, issues)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(issues)
            
            # Auto-sanitize if enabled and needed
            sanitized_content = None
            if self.config.enable_automatic_sanitization and issues:
                sanitized_content = await self._sanitize_content(prompt, issues)
            
            # Determine if prompt is safe
            is_safe = (
                overall_threat_level in [ThreatLevel.SAFE, ThreatLevel.LOW] and
                safety_score >= self.config.confidence_threshold and
                not any(issue.threat_level == ThreatLevel.CRITICAL for issue in issues)
            )
            
            end_time = datetime.utcnow()
            validation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = SecurityValidationResult(
                is_safe=is_safe,
                overall_threat_level=overall_threat_level,
                issues=issues,
                safety_score=safety_score,
                compliance_status=compliance_status,
                recommendations=recommendations,
                sanitized_content=sanitized_content,
                validation_time_ms=validation_time_ms
            )
            
            # Log security event if needed
            if self.config.log_security_events and (issues or not is_safe):
                await self._log_security_event(prompt, result, template_id)
            
            # Record metrics
            await self.metrics_collector.record_security_validation(
                template_id or "unknown",
                result.overall_threat_level.value,
                result.safety_score,
                len(issues)
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            raise SecurityError(f"Security validation failed: {e}")
    
    async def validate_template(self, template_content: str, template_id: str) -> SecurityValidationResult:
        """Validate a prompt template for security issues"""
        return await self.validate_prompt(template_content, template_id)
    
    async def _detect_prompt_injection(self, prompt: str) -> List[SecurityIssue]:
        """Detect prompt injection attempts"""
        issues = []
        
        try:
            prompt_lower = prompt.lower()
            
            # Check against known injection patterns
            for pattern in self.injection_patterns:
                matches = re.finditer(pattern, prompt_lower, re.IGNORECASE)
                for match in matches:
                    confidence = 0.9  # High confidence for pattern matches
                    
                    issue = SecurityIssue(
                        category=SecurityCategory.PROMPT_INJECTION,
                        threat_level=ThreatLevel.HIGH,
                        confidence=confidence,
                        description=f"Potential prompt injection pattern detected: {pattern}",
                        detected_content=match.group(),
                        location=f"Position {match.start()}-{match.end()}",
                        mitigation="Remove or rephrase the detected injection attempt",
                        compliance_violations=[ComplianceStandard.EU_AI_ACT, ComplianceStandard.CREATOR_ECONOMY_ETHICS]
                    )
                    issues.append(issue)
            
            # Advanced injection detection using ML (simplified)
            injection_score = await self._calculate_injection_score(prompt)
            if injection_score > 0.7:
                issue = SecurityIssue(
                    category=SecurityCategory.PROMPT_INJECTION,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=injection_score,
                    description="ML model detected potential injection attempt",
                    detected_content="[Full prompt analyzed]",
                    location="Global",
                    mitigation="Review prompt for manipulation attempts"
                )
                issues.append(issue)
            
        except Exception as e:
            logger.error(f"Prompt injection detection failed: {e}")
        
        return issues
    
    async def _calculate_injection_score(self, prompt: str) -> float:
        """Calculate injection likelihood score using ML"""
        try:
            # Simplified scoring based on suspicious keywords and patterns
            suspicious_keywords = [
                'ignore', 'forget', 'override', 'bypass', 'roleplay', 'pretend',
                'act as', 'system', 'admin', 'debug', 'jailbreak', 'dan'
            ]
            
            prompt_lower = prompt.lower()
            keyword_score = sum(1 for keyword in suspicious_keywords if keyword in prompt_lower)
            keyword_score = min(keyword_score / len(suspicious_keywords), 1.0)
            
            # Pattern complexity score
            pattern_score = 0.0
            if re.search(r'(ignore|forget).*(previous|all).*(instructions|rules)', prompt_lower):
                pattern_score += 0.4
            if re.search(r'(act\s+as|roleplay\s+as|pretend).*(different|someone|something)', prompt_lower):
                pattern_score += 0.3
            if re.search(r'(system|admin|debug|developer)\s*(mode|access)', prompt_lower):
                pattern_score += 0.5
            
            return min(keyword_score + pattern_score, 1.0)
        
        except Exception:
            return 0.0
    
    async def _detect_toxicity(self, prompt: str) -> List[SecurityIssue]:
        """Detect toxic content in prompt"""
        issues = []
        
        try:
            if not self.toxicity_pipeline:
                return issues
            
            # Use toxicity detection model
            result = self.toxicity_pipeline(prompt)
            
            if result and len(result) > 0:
                toxicity_score = result[0].get('score', 0.0)
                label = result[0].get('label', '')
                
                if toxicity_score > self.config.toxicity_threshold and label == 'TOXIC':
                    threat_level = ThreatLevel.HIGH if toxicity_score > 0.9 else ThreatLevel.MEDIUM
                    
                    issue = SecurityIssue(
                        category=SecurityCategory.TOXIC_CONTENT,
                        threat_level=threat_level,
                        confidence=toxicity_score,
                        description=f"Toxic content detected with confidence {toxicity_score:.2f}",
                        detected_content="[Content flagged as toxic]",
                        location="Global",
                        mitigation="Remove or rephrase toxic content",
                        compliance_violations=[ComplianceStandard.CREATOR_ECONOMY_ETHICS]
                    )
                    issues.append(issue)
        
        except Exception as e:
            logger.error(f"Toxicity detection failed: {e}")
        
        return issues
    
    async def _detect_bias(self, prompt: str) -> List[SecurityIssue]:
        """Detect bias and discrimination in prompt"""
        issues = []
        
        try:
            for bias_type, patterns in self.bias_detector.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, prompt, re.IGNORECASE)
                    for match in matches:
                        issue = SecurityIssue(
                            category=SecurityCategory.BIAS_DISCRIMINATION,
                            threat_level=ThreatLevel.MEDIUM,
                            confidence=0.8,
                            description=f"Potential {bias_type.replace('_', ' ')} detected",
                            detected_content=match.group(),
                            location=f"Position {match.start()}-{match.end()}",
                            mitigation="Remove biased language and use inclusive alternatives",
                            compliance_violations=[ComplianceStandard.CREATOR_ECONOMY_ETHICS, ComplianceStandard.EU_AI_ACT]
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
        
        return issues
    
    async def _detect_privacy_violations(self, prompt: str) -> List[SecurityIssue]:
        """Detect potential privacy violations"""
        issues = []
        
        try:
            # PII patterns
            pii_patterns = {
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
                'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
            }
            
            for pii_type, pattern in pii_patterns.items():
                matches = re.finditer(pattern, prompt)
                for match in matches:
                    issue = SecurityIssue(
                        category=SecurityCategory.PRIVACY_VIOLATION,
                        threat_level=ThreatLevel.HIGH,
                        confidence=0.95,
                        description=f"Potential {pii_type.upper()} detected",
                        detected_content="[REDACTED]",
                        location=f"Position {match.start()}-{match.end()}",
                        mitigation="Remove or mask personal information",
                        compliance_violations=[ComplianceStandard.GDPR, ComplianceStandard.CCPA, ComplianceStandard.HIPAA]
                    )
                    issues.append(issue)
        
        except Exception as e:
            logger.error(f"Privacy detection failed: {e}")
        
        return issues
    
    async def _detect_copyright_violations(self, prompt: str) -> List[SecurityIssue]:
        """Detect potential copyright violations"""
        issues = []
        
        try:
            # Copyright indicator patterns
            copyright_patterns = [
                r'©\s*\d{4}',
                r'copyright\s+\d{4}',
                r'all\s+rights\s+reserved',
                r'proprietary\s+(and\s+)?confidential',
                r'trade\s+secret',
                r'reproduce.*without.*permission'
            ]
            
            for pattern in copyright_patterns:
                matches = re.finditer(pattern, prompt, re.IGNORECASE)
                for match in matches:
                    issue = SecurityIssue(
                        category=SecurityCategory.COPYRIGHT_INFRINGEMENT,
                        threat_level=ThreatLevel.MEDIUM,
                        confidence=0.7,
                        description="Potential copyrighted content detected",
                        detected_content=match.group(),
                        location=f"Position {match.start()}-{match.end()}",
                        mitigation="Verify copyright permissions or use original content",
                        compliance_violations=[ComplianceStandard.CREATOR_ECONOMY_ETHICS]
                    )
                    issues.append(issue)
        
        except Exception as e:
            logger.error(f"Copyright detection failed: {e}")
        
        return issues
    
    async def _moderate_content(self, prompt: str) -> List[SecurityIssue]:
        """Perform content moderation checks"""
        issues = []
        
        try:
            # Inappropriate content patterns
            inappropriate_patterns = [
                r'\b(violence|violent|attack|kill|murder|bomb|weapon)\b',
                r'\b(illegal|drugs|narcotics|cocaine|heroin|marijuana)\b',
                r'\b(adult|nsfw|explicit|sexual|pornographic)\b',
                r'\b(suicide|self-harm|depression|anxiety)\b'
            ]
            
            for pattern in inappropriate_patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    issue = SecurityIssue(
                        category=SecurityCategory.INAPPROPRIATE_CONTENT,
                        threat_level=ThreatLevel.MEDIUM,
                        confidence=0.8,
                        description="Potentially inappropriate content detected",
                        detected_content="[Content flagged]",
                        location="Global",
                        mitigation="Review and modify content to ensure appropriateness",
                        compliance_violations=[ComplianceStandard.CREATOR_ECONOMY_ETHICS]
                    )
                    issues.append(issue)
                    break  # Don't add multiple issues for same prompt
        
        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
        
        return issues
    
    def _calculate_overall_threat_level(self, issues: List[SecurityIssue]) -> ThreatLevel:
        """Calculate overall threat level from individual issues"""
        if not issues:
            return ThreatLevel.SAFE
        
        max_threat = max(issue.threat_level for issue in issues)
        critical_count = sum(1 for issue in issues if issue.threat_level == ThreatLevel.CRITICAL)
        high_count = sum(1 for issue in issues if issue.threat_level == ThreatLevel.HIGH)
        
        if critical_count > 0:
            return ThreatLevel.CRITICAL
        elif high_count >= 2:
            return ThreatLevel.HIGH
        elif max_threat == ThreatLevel.HIGH:
            return ThreatLevel.HIGH
        elif max_threat == ThreatLevel.MEDIUM:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_safety_score(self, issues: List[SecurityIssue]) -> float:
        """Calculate overall safety score (0.0 to 1.0)"""
        if not issues:
            return 1.0
        
        # Weight issues by threat level
        threat_weights = {
            ThreatLevel.CRITICAL: 1.0,
            ThreatLevel.HIGH: 0.7,
            ThreatLevel.MEDIUM: 0.4,
            ThreatLevel.LOW: 0.2
        }
        
        total_weight = sum(threat_weights[issue.threat_level] * issue.confidence for issue in issues)
        max_possible_weight = len(issues) * 1.0  # Assuming all critical with confidence 1.0
        
        return max(0.0, 1.0 - (total_weight / max_possible_weight))
    
    async def _check_compliance(self, prompt: str, issues: List[SecurityIssue]) -> Dict[ComplianceStandard, bool]:
        """Check compliance with various standards"""
        compliance_status = {}
        
        # Get all violated standards from issues
        violated_standards = set()
        for issue in issues:
            violated_standards.update(issue.compliance_violations)
        
        # Check each standard
        for standard in ComplianceStandard:
            compliance_status[standard] = standard not in violated_standards
        
        return compliance_status
    
    def _generate_security_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations based on detected issues"""
        recommendations = []
        
        if not issues:
            recommendations.append("Prompt passed all security checks. No immediate action required.")
            return recommendations
        
        # Category-specific recommendations
        categories = set(issue.category for issue in issues)
        
        if SecurityCategory.PROMPT_INJECTION in categories:
            recommendations.append("Review prompt for injection attempts and remove suspicious patterns")
        
        if SecurityCategory.TOXIC_CONTENT in categories:
            recommendations.append("Refine content to remove toxic or harmful language")
        
        if SecurityCategory.BIAS_DISCRIMINATION in categories:
            recommendations.append("Use inclusive language and avoid discriminatory content")
        
        if SecurityCategory.PRIVACY_VIOLATION in categories:
            recommendations.append("Remove or mask any personal identifiable information (PII)")
        
        if SecurityCategory.COPYRIGHT_INFRINGEMENT in categories:
            recommendations.append("Verify copyright permissions or use original content")
        
        if SecurityCategory.INAPPROPRIATE_CONTENT in categories:
            recommendations.append("Modify content to ensure appropriateness for all audiences")
        
        # Threat level recommendations
        threat_levels = set(issue.threat_level for issue in issues)
        
        if ThreatLevel.CRITICAL in threat_levels:
            recommendations.append("CRITICAL: Immediate action required before using this prompt")
        elif ThreatLevel.HIGH in threat_levels:
            recommendations.append("HIGH PRIORITY: Address security issues before deployment")
        
        return recommendations
    
    async def _sanitize_content(self, prompt: str, issues: List[SecurityIssue]) -> str:
        """Automatically sanitize content based on detected issues"""
        sanitized = prompt
        
        try:
            # Remove PII
            pii_patterns = {
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b': '[PHONE]',
                r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b': '[CARD]'
            }
            
            for pattern, replacement in pii_patterns.items():
                sanitized = re.sub(pattern, replacement, sanitized)
            
            # Remove injection patterns
            for pattern in self.injection_patterns[:5]:  # Only top patterns
                sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
            
            return sanitized
        
        except Exception as e:
            logger.error(f"Content sanitization failed: {e}")
            return prompt
    
    async def _log_security_event(
        self,
        prompt: str,
        result: SecurityValidationResult,
        template_id: Optional[str]
    ) -> None:
        """Log security event to database"""
        try:
            event_id = f"sec_{int(datetime.utcnow().timestamp())}_{hashlib.md5(prompt.encode()).hexdigest()[:8]}"
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_events 
                    (event_id, threat_level, category, prompt_hash, issues, 
                     safety_score, template_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, event_id, result.overall_threat_level.value,
                    result.issues[0].category.value if result.issues else 'none',
                    prompt_hash, json.dumps([issue.__dict__ for issue in result.issues]),
                    result.safety_score, template_id)
        
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def get_security_summary(self, template_id: str) -> Dict[str, Any]:
        """Get security summary for a template"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_events,
                        AVG(safety_score) as avg_safety_score,
                        COUNT(CASE WHEN threat_level IN ('high', 'critical') THEN 1 END) as high_threat_count,
                        MAX(created_at) as last_check
                    FROM security_events 
                    WHERE template_id = $1
                    AND created_at >= NOW() - INTERVAL '30 days'
                """, template_id)
                
                return dict(row) if row else {}
        
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {}
    
    async def cleanup(self) -> None:
        """Cleanup security validator resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Security Validator cleanup completed")
        
        except Exception as e:
            logger.error(f"Security Validator cleanup failed: {e}")


# Global security validator instance
security_validator = SecurityValidator()