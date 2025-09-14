"""Security Compliance Validator - Consolidated Security & Compliance Validation
==============================================================================

Industrial-grade security and compliance validation system combining threat detection,
legal compliance (GDPR, CCPA, DMCA), and platform policy enforcement for the
IA Influencer Agent Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Consolidated Validation Capabilities:
- Advanced threat detection and malware scanning
- GDPR/CCPA/DMCA compliance validation
- Platform-specific policy enforcement
- Content security assessment
- Legal compliance verification
- Audit trail and reporting
- Real-time threat intelligence integration
"""

import asyncio
import logging
import hashlib
import json
import re
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import mimetypes
import tempfile

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats."""
    MALWARE = "malware"
    PHISHING = "phishing"
    SPAM = "spam"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    COPYRIGHT_VIOLATION = "copyright_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    ILLEGAL_CONTENT = "illegal_content"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    DATA_BREACH = "data_breach"

class ComplianceFramework(Enum):
    """Legal compliance frameworks."""
    GDPR = "gdpr"              # General Data Protection Regulation (EU)
    CCPA = "ccpa"              # California Consumer Privacy Act (US)
    COPPA = "coppa"            # Children's Online Privacy Protection Act (US)
    DMCA = "dmca"              # Digital Millennium Copyright Act (US)
    HIPAA = "hipaa"            # Health Insurance Portability and Accountability Act (US)
    PCI_DSS = "pci_dss"        # Payment Card Industry Data Security Standard
    SOX = "sox"                # Sarbanes-Oxley Act (US)
    ISO27001 = "iso27001"      # Information Security Management Standard
    PIPEDA = "pipeda"          # Personal Information Protection (Canada)
    LGPD = "lgpd"              # Lei Geral de Proteção de Dados (Brazil)

class PlatformPolicy(Enum):
    """Platform-specific policies."""
    YOUTUBE_COMMUNITY = "youtube_community"
    INSTAGRAM_TERMS = "instagram_terms"
    TIKTOK_GUIDELINES = "tiktok_guidelines"
    SPOTIFY_CONTENT = "spotify_content"
    LINKEDIN_PROFESSIONAL = "linkedin_professional"
    TWITTER_RULES = "twitter_rules"
    FACEBOOK_STANDARDS = "facebook_standards"
    DISCORD_GUIDELINES = "discord_guidelines"
    CUSTOM_POLICY = "custom_policy"

class ComplianceStatus(Enum):
    """Compliance validation status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    REQUIRES_REVIEW = "requires_review"
    UNKNOWN = "unknown"

@dataclass
class SecurityThreat:
    """Security threat detection result."""
    threat_type: ThreatType
    severity: SecurityLevel
    confidence: float
    description: str
    evidence: List[str] = field(default_factory=list)
    remediation: Optional[str] = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    threat_indicators: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityValidationResult:
    """Security validation result."""
    is_secure: bool
    security_score: float
    threats: List[SecurityThreat] = field(default_factory=list)
    risk_level: SecurityLevel = SecurityLevel.LOW
    recommendations: List[str] = field(default_factory=list)
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scan_duration_ms: int = 0
    signature_hash: Optional[str] = None

@dataclass
class ComplianceViolation:
    """Compliance violation details."""
    framework: ComplianceFramework
    violation_type: str
    severity: SecurityLevel
    description: str
    article_reference: Optional[str] = None
    remediation_required: bool = True
    remediation_steps: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    violation_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceValidationResult:
    """Compliance validation result."""
    is_compliant: bool
    compliance_score: float
    status: ComplianceStatus
    violations: List[ComplianceViolation] = field(default_factory=list)
    frameworks_checked: List[ComplianceFramework] = field(default_factory=list)
    policy_violations: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_duration_ms: int = 0

class SecurityComplianceValidator:
    """Consolidated security and compliance validation system."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the security compliance validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.threat_patterns = self._load_threat_patterns()
        self.compliance_rules = self._load_compliance_rules()
        self.platform_policies = self._load_platform_policies()
        
        # Security settings
        self.enable_malware_scan = self.config.get('enable_malware_scan', True)
        self.enable_content_analysis = self.config.get('enable_content_analysis', True)
        self.threat_confidence_threshold = self.config.get('threat_confidence_threshold', 0.7)
        self.compliance_threshold = self.config.get('compliance_threshold', 0.8)
        
        logger.info("SecurityComplianceValidator initialized")
    
    def _load_threat_patterns(self) -> Dict[ThreatType, List[Dict[str, Any]]]:
        """Load threat detection patterns.
        
        Returns:
            Dictionary of threat patterns by type
        """
        patterns = {
            ThreatType.MALWARE: [
                {'pattern': r'eval\s*\(', 'confidence': 0.8, 'description': 'Potential code injection'},
                {'pattern': r'<script[^>]*>', 'confidence': 0.7, 'description': 'Script injection attempt'},
                {'pattern': r'javascript:', 'confidence': 0.6, 'description': 'JavaScript URL scheme'},
            ],
            ThreatType.PHISHING: [
                {'pattern': r'urgent.*action.*required', 'confidence': 0.6, 'description': 'Phishing urgency tactic'},
                {'pattern': r'verify.*account.*immediately', 'confidence': 0.7, 'description': 'Account verification scam'},
                {'pattern': r'click.*here.*now', 'confidence': 0.5, 'description': 'Suspicious call-to-action'},
            ],
            ThreatType.INAPPROPRIATE_CONTENT: [
                {'pattern': r'\b(explicit|adult|nsfw)\b', 'confidence': 0.8, 'description': 'Adult content indicators'},
                {'pattern': r'\b(violence|weapons|drugs)\b', 'confidence': 0.7, 'description': 'Harmful content indicators'},
            ],
            ThreatType.HATE_SPEECH: [
                {'pattern': r'\b(hate|racist|discriminat)', 'confidence': 0.8, 'description': 'Hate speech patterns'},
                {'pattern': r'\b(terrorist|extremist)\b', 'confidence': 0.9, 'description': 'Extremist content'},
            ]
        }
        return patterns
    
    def _load_compliance_rules(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Load compliance validation rules.
        
        Returns:
            Dictionary of compliance rules by framework
        """
        rules = {
            ComplianceFramework.GDPR: {
                'data_processing_consent': {
                    'required': True,
                    'description': 'Explicit consent required for data processing'
                },
                'data_retention_limits': {
                    'max_days': 365,
                    'description': 'Personal data retention limits'
                },
                'right_to_deletion': {
                    'required': True,
                    'description': 'Support for data deletion requests'
                },
                'privacy_by_design': {
                    'required': True,
                    'description': 'Privacy protection by default'
                }
            },
            ComplianceFramework.CCPA: {
                'consumer_rights_notice': {
                    'required': True,
                    'description': 'Notice of consumer privacy rights'
                },
                'opt_out_mechanism': {
                    'required': True,
                    'description': 'Opt-out mechanism for data sales'
                },
                'data_categories_disclosure': {
                    'required': True,
                    'description': 'Disclosure of data categories collected'
                }
            },
            ComplianceFramework.DMCA: {
                'copyright_notice': {
                    'required': True,
                    'description': 'Copyright ownership notice'
                },
                'takedown_procedure': {
                    'required': True,
                    'description': 'DMCA takedown procedure compliance'
                },
                'safe_harbor_compliance': {
                    'required': True,
                    'description': 'Safe harbor provisions compliance'
                }
            },
            ComplianceFramework.COPPA: {
                'age_verification': {
                    'required': True,
                    'description': 'Age verification for users under 13'
                },
                'parental_consent': {
                    'required': True,
                    'description': 'Parental consent for minors'
                },
                'minimal_data_collection': {
                    'required': True,
                    'description': 'Minimal data collection from children'
                }
            }
        }
        return rules
    
    def _load_platform_policies(self) -> Dict[PlatformPolicy, Dict[str, Any]]:
        """Load platform-specific policy rules.
        
        Returns:
            Dictionary of platform policies
        """
        policies = {
            PlatformPolicy.YOUTUBE_COMMUNITY: {
                'spam_prevention': ['no_repetitive_content', 'no_misleading_metadata'],
                'harmful_content': ['no_violence', 'no_harassment', 'no_hate_speech'],
                'copyright_respect': ['original_content', 'fair_use_compliance'],
                'child_safety': ['coppa_compliance', 'age_appropriate_content']
            },
            PlatformPolicy.INSTAGRAM_TERMS: {
                'community_guidelines': ['authentic_content', 'respectful_interaction'],
                'intellectual_property': ['original_content', 'proper_attribution'],
                'commerce_policies': ['accurate_product_info', 'legal_business_practices']
            },
            PlatformPolicy.TIKTOK_GUIDELINES: {
                'community_safety': ['no_harmful_behavior', 'authentic_content'],
                'content_standards': ['age_appropriate', 'culturally_sensitive'],
                'platform_integrity': ['no_spam', 'no_artificial_engagement']
            },
            PlatformPolicy.SPOTIFY_CONTENT: {
                'content_quality': ['high_audio_quality', 'complete_metadata'],
                'copyright_compliance': ['licensing_verification', 'ownership_proof'],
                'content_guidelines': ['no_hate_speech', 'no_explicit_without_label']
            }
        }
        return policies
    
    async def validate_security(self, content: Union[str, bytes, Path], 
                               content_type: str = "text") -> SecurityValidationResult:
        """Validate content security and detect threats.
        
        Args:
            content: Content to validate (text, binary data, or file path)
            content_type: Type of content (text, audio, video, image, file)
            
        Returns:
            SecurityValidationResult with threat analysis
        """
        start_time = datetime.now()
        threats = []
        security_score = 1.0
        risk_level = SecurityLevel.LOW
        
        try:
            # Convert content to appropriate format for analysis
            if isinstance(content, Path):
                content_data = await self._read_file_safely(content)
                signature_hash = self._calculate_file_hash(content)
            elif isinstance(content, bytes):
                content_data = content.decode('utf-8', errors='ignore')
                signature_hash = hashlib.sha256(content).hexdigest()
            else:
                content_data = str(content)
                signature_hash = hashlib.sha256(content_data.encode()).hexdigest()
            
            # Perform threat detection scans
            if self.enable_content_analysis:
                content_threats = await self._scan_content_threats(content_data, content_type)
                threats.extend(content_threats)
            
            if self.enable_malware_scan and isinstance(content, (bytes, Path)):
                malware_threats = await self._scan_malware(content)
                threats.extend(malware_threats)
            
            # Additional security checks
            structural_threats = await self._scan_structural_threats(content_data, content_type)
            threats.extend(structural_threats)
            
            # Calculate security score and risk level
            if threats:
                # Reduce security score based on threats
                threat_impact = sum(threat.confidence * self._get_severity_weight(threat.severity) 
                                  for threat in threats)
                security_score = max(0.0, 1.0 - (threat_impact / len(threats)))
                
                # Determine overall risk level
                max_severity = max(threat.severity for threat in threats)
                risk_level = max_severity
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(threats, security_score)
            
            # Determine if content is secure
            is_secure = (security_score >= self.threat_confidence_threshold and 
                        risk_level in [SecurityLevel.LOW, SecurityLevel.MEDIUM])
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SecurityValidationResult(
                is_secure=is_secure,
                security_score=security_score,
                threats=threats,
                risk_level=risk_level,
                recommendations=recommendations,
                scanned_at=start_time,
                scan_duration_ms=duration_ms,
                signature_hash=signature_hash
            )
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return SecurityValidationResult(
                is_secure=False,
                security_score=0.0,
                threats=[SecurityThreat(
                    threat_type=ThreatType.SUSPICIOUS_BEHAVIOR,
                    severity=SecurityLevel.HIGH,
                    confidence=1.0,
                    description=f"Security validation error: {str(e)}"
                )],
                risk_level=SecurityLevel.HIGH,
                recommendations=["Manual security review required due to validation error"],
                scan_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def validate_compliance(self, content_metadata: Dict[str, Any],
                                 frameworks: Optional[List[ComplianceFramework]] = None,
                                 platform_policies: Optional[List[PlatformPolicy]] = None) -> ComplianceValidationResult:
        """Validate legal compliance and platform policies.
        
        Args:
            content_metadata: Content metadata and context information
            frameworks: Specific compliance frameworks to check
            platform_policies: Platform policies to validate against
            
        Returns:
            ComplianceValidationResult with compliance status
        """
        start_time = datetime.now()
        violations = []
        frameworks_checked = frameworks or list(ComplianceFramework)
        policy_violations = []
        
        try:
            # Check legal compliance frameworks
            for framework in frameworks_checked:
                framework_violations = await self._check_compliance_framework(
                    content_metadata, framework
                )
                violations.extend(framework_violations)
            
            # Check platform-specific policies
            if platform_policies:
                for policy in platform_policies:
                    policy_issues = await self._check_platform_policy(
                        content_metadata, policy
                    )
                    policy_violations.extend(policy_issues)
            
            # Calculate compliance score
            total_checks = len(frameworks_checked) + len(platform_policies or [])
            if total_checks > 0:
                violation_weight = len(violations) + len(policy_violations)
                compliance_score = max(0.0, 1.0 - (violation_weight / total_checks))
            else:
                compliance_score = 1.0
            
            # Determine compliance status
            if violations or policy_violations:
                if compliance_score >= 0.8:
                    status = ComplianceStatus.PARTIAL_COMPLIANCE
                elif compliance_score >= 0.5:
                    status = ComplianceStatus.REQUIRES_REVIEW
                else:
                    status = ComplianceStatus.NON_COMPLIANT
            else:
                status = ComplianceStatus.COMPLIANT
            
            is_compliant = status == ComplianceStatus.COMPLIANT
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ComplianceValidationResult(
                is_compliant=is_compliant,
                compliance_score=compliance_score,
                status=status,
                violations=violations,
                frameworks_checked=frameworks_checked,
                policy_violations=policy_violations,
                validated_at=start_time,
                validation_duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return ComplianceValidationResult(
                is_compliant=False,
                compliance_score=0.0,
                status=ComplianceStatus.UNKNOWN,
                violations=[ComplianceViolation(
                    framework=ComplianceFramework.GDPR,  # Default framework for error
                    violation_type="validation_error",
                    severity=SecurityLevel.HIGH,
                    description=f"Compliance validation error: {str(e)}",
                    remediation_required=True,
                    remediation_steps=["Manual compliance review required"]
                )],
                frameworks_checked=frameworks_checked,
                validation_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def _scan_content_threats(self, content: str, content_type: str) -> List[SecurityThreat]:
        """Scan content for security threats using pattern matching.
        
        Args:
            content: Content to scan
            content_type: Type of content
            
        Returns:
            List of detected threats
        """
        threats = []
        content_lower = content.lower()
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                confidence = pattern_info['confidence']
                description = pattern_info['description']
                
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    # Calculate severity based on number of matches and confidence
                    match_count = len(matches)
                    adjusted_confidence = min(1.0, confidence * (1 + match_count * 0.1))
                    
                    if adjusted_confidence >= 0.8:
                        severity = SecurityLevel.HIGH
                    elif adjusted_confidence >= 0.6:
                        severity = SecurityLevel.MEDIUM
                    else:
                        severity = SecurityLevel.LOW
                    
                    threat = SecurityThreat(
                        threat_type=threat_type,
                        severity=severity,
                        confidence=adjusted_confidence,
                        description=f"{description} (found {match_count} matches)",
                        evidence=[f"Pattern: {pattern}", f"Matches: {matches[:5]}"],  # Limit evidence
                        threat_indicators={
                            'pattern': pattern,
                            'match_count': match_count,
                            'content_type': content_type
                        }
                    )
                    threats.append(threat)
        
        return threats
    
    async def _scan_malware(self, content: Union[bytes, Path]) -> List[SecurityThreat]:
        """Scan for malware signatures (simplified implementation).
        
        Args:
            content: Binary content or file path to scan
            
        Returns:
            List of malware threats detected
        """
        threats = []
        
        try:
            # Read content if it's a file path
            if isinstance(content, Path):
                with open(content, 'rb') as f:
                    data = f.read(1024 * 1024)  # Read first 1MB for signature check
            else:
                data = content[:1024 * 1024]  # First 1MB of binary data
            
            # Simple malware signature patterns (hex strings)
            malware_signatures = [
                b'\x4d\x5a\x90\x00',  # PE executable header
                b'\x50\x4b\x03\x04',  # ZIP archive (potential trojan)
                b'\x7f\x45\x4c\x46',  # ELF executable
            ]
            
            suspicious_strings = [
                b'eval(',
                b'document.write',
                b'shell_exec',
                b'system(',
                b'exec(',
            ]
            
            for signature in malware_signatures:
                if signature in data:
                    threats.append(SecurityThreat(
                        threat_type=ThreatType.MALWARE,
                        severity=SecurityLevel.CRITICAL,
                        confidence=0.9,
                        description=f"Malware signature detected: {signature.hex()}",
                        evidence=[f"Signature: {signature.hex()}"],
                        threat_indicators={'signature_type': 'binary'}
                    ))
            
            for suspicious in suspicious_strings:
                if suspicious in data:
                    threats.append(SecurityThreat(
                        threat_type=ThreatType.MALWARE,
                        severity=SecurityLevel.HIGH,
                        confidence=0.7,
                        description=f"Suspicious code pattern: {suspicious.decode('utf-8', errors='ignore')}",
                        evidence=[f"Pattern: {suspicious.decode('utf-8', errors='ignore')}"],
                        threat_indicators={'signature_type': 'string_pattern'}
                    ))
            
        except Exception as e:
            logger.error(f"Malware scan failed: {e}")
            # Return a generic threat for scan failure
            threats.append(SecurityThreat(
                threat_type=ThreatType.SUSPICIOUS_BEHAVIOR,
                severity=SecurityLevel.MEDIUM,
                confidence=0.5,
                description=f"Malware scan failed: {str(e)}",
                threat_indicators={'scan_error': True}
            ))
        
        return threats
    
    async def _scan_structural_threats(self, content: str, content_type: str) -> List[SecurityThreat]:
        """Scan for structural security issues.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            
        Returns:
            List of structural threats
        """
        threats = []
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        
        for url in urls:
            if self._is_suspicious_url(url):
                threats.append(SecurityThreat(
                    threat_type=ThreatType.PHISHING,
                    severity=SecurityLevel.MEDIUM,
                    confidence=0.6,
                    description=f"Suspicious URL detected: {url}",
                    evidence=[f"URL: {url}"],
                    threat_indicators={'url': url, 'url_analysis': True}
                ))
        
        # Check for data exposure patterns
        sensitive_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN pattern'),  # Social Security Number
            (r'\b4[0-9]{12}(?:[0-9]{3})?\b', 'Credit card pattern'),  # Credit card
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email pattern'),
        ]
        
        for pattern, description in sensitive_patterns:
            matches = re.findall(pattern, content)
            if matches:
                threats.append(SecurityThreat(
                    threat_type=ThreatType.PRIVACY_VIOLATION,
                    severity=SecurityLevel.HIGH,
                    confidence=0.8,
                    description=f"Potential sensitive data exposure: {description}",
                    evidence=[f"Matches found: {len(matches)}"],
                    threat_indicators={'sensitive_data_type': description, 'match_count': len(matches)}
                ))
        
        return threats
    
    async def _check_compliance_framework(self, metadata: Dict[str, Any], 
                                        framework: ComplianceFramework) -> List[ComplianceViolation]:
        """Check compliance with specific framework.
        
        Args:
            metadata: Content metadata to check
            framework: Compliance framework to validate against
            
        Returns:
            List of compliance violations
        """
        violations = []
        rules = self.compliance_rules.get(framework, {})
        
        for rule_name, rule_config in rules.items():
            violation = await self._check_compliance_rule(metadata, framework, rule_name, rule_config)
            if violation:
                violations.append(violation)
        
        return violations
    
    async def _check_compliance_rule(self, metadata: Dict[str, Any], framework: ComplianceFramework,
                                   rule_name: str, rule_config: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check a specific compliance rule.
        
        Args:
            metadata: Content metadata
            framework: Compliance framework
            rule_name: Name of the rule
            rule_config: Rule configuration
            
        Returns:
            ComplianceViolation if rule is violated, None otherwise
        """
        # Example rule checking logic (simplified)
        if rule_config.get('required', False):
            # Check if required metadata is present
            if rule_name not in metadata:
                return ComplianceViolation(
                    framework=framework,
                    violation_type=rule_name,
                    severity=SecurityLevel.HIGH,
                    description=f"Required {rule_name} not found in metadata",
                    article_reference=rule_config.get('article'),
                    remediation_steps=[f"Add {rule_name} to content metadata"],
                    violation_context={'rule_name': rule_name, 'metadata_keys': list(metadata.keys())}
                )
        
        # Check retention limits
        if 'max_days' in rule_config:
            retention_days = metadata.get(f'{rule_name}_retention_days')
            if retention_days and retention_days > rule_config['max_days']:
                return ComplianceViolation(
                    framework=framework,
                    violation_type=f"{rule_name}_retention_violation",
                    severity=SecurityLevel.MEDIUM,
                    description=f"Data retention exceeds {rule_config['max_days']} days limit",
                    remediation_steps=[f"Reduce retention to {rule_config['max_days']} days or less"],
                    violation_context={'current_days': retention_days, 'max_days': rule_config['max_days']}
                )
        
        return None
    
    async def _check_platform_policy(self, metadata: Dict[str, Any], 
                                   policy: PlatformPolicy) -> List[str]:
        """Check platform-specific policy compliance.
        
        Args:
            metadata: Content metadata
            policy: Platform policy to check
            
        Returns:
            List of policy violation descriptions
        """
        violations = []
        policy_rules = self.platform_policies.get(policy, {})
        
        for category, rules in policy_rules.items():
            for rule in rules:
                # Simplified policy checking - in production, this would be more sophisticated
                if not metadata.get(f'{category}_{rule}_compliant', True):
                    violations.append(f"Platform policy violation: {category} - {rule}")
        
        return violations
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL appears suspicious.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is suspicious
        """
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl',  # URL shorteners
            'tempmail.org', '10minutemail.com',  # Temporary email
        ]
        
        suspicious_patterns = [
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
            r'[a-zA-Z0-9-]{20,}\.com',  # Very long domain names
        ]
        
        url_lower = url.lower()
        
        # Check against known suspicious domains
        for domain in suspicious_domains:
            if domain in url_lower:
                return True
        
        # Check against suspicious patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    def _get_severity_weight(self, severity: SecurityLevel) -> float:
        """Get numeric weight for security level.
        
        Args:
            severity: Security level
            
        Returns:
            Numeric weight (0.0 to 1.0)
        """
        weights = {
            SecurityLevel.LOW: 0.25,
            SecurityLevel.MEDIUM: 0.5,
            SecurityLevel.HIGH: 0.75,
            SecurityLevel.CRITICAL: 1.0
        }
        return weights.get(severity, 0.5)
    
    def _generate_security_recommendations(self, threats: List[SecurityThreat], 
                                         security_score: float) -> List[str]:
        """Generate security improvement recommendations.
        
        Args:
            threats: List of detected threats
            security_score: Overall security score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if security_score < 0.5:
            recommendations.append("Content requires immediate security review before publication")
        elif security_score < 0.7:
            recommendations.append("Consider additional security measures before publishing")
        
        # Threat-specific recommendations
        threat_types = {threat.threat_type for threat in threats}
        
        if ThreatType.MALWARE in threat_types:
            recommendations.append("Scan content with updated antivirus software")
            recommendations.append("Consider quarantining suspicious files")
        
        if ThreatType.PHISHING in threat_types:
            recommendations.append("Review and verify all URLs in content")
            recommendations.append("Add warnings for external links")
        
        if ThreatType.PRIVACY_VIOLATION in threat_types:
            recommendations.append("Remove or redact sensitive personal information")
            recommendations.append("Ensure compliance with data protection regulations")
        
        if ThreatType.INAPPROPRIATE_CONTENT in threat_types:
            recommendations.append("Review content for age-appropriateness")
            recommendations.append("Add content warnings if necessary")
        
        if not recommendations:
            recommendations.append("Content security appears acceptable")
        
        return recommendations
    
    async def _read_file_safely(self, file_path: Path, max_size: int = 10 * 1024 * 1024) -> str:
        """Safely read file content with size limits.
        
        Args:
            file_path: Path to file
            max_size: Maximum file size to read (default 10MB)
            
        Returns:
            File content as string
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try reading as binary and converting
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

# Convenience functions for direct validation
async def validate_security(content: Union[str, bytes, Path], 
                          content_type: str = "text",
                          config: Optional[Dict[str, Any]] = None) -> SecurityValidationResult:
    """Validate content security (convenience function).
    
    Args:
        content: Content to validate
        content_type: Type of content
        config: Optional validator configuration
        
    Returns:
        SecurityValidationResult
    """
    validator = SecurityComplianceValidator(config)
    return await validator.validate_security(content, content_type)

async def validate_compliance(content_metadata: Dict[str, Any],
                            frameworks: Optional[List[ComplianceFramework]] = None,
                            platform_policies: Optional[List[PlatformPolicy]] = None,
                            config: Optional[Dict[str, Any]] = None) -> ComplianceValidationResult:
    """Validate compliance (convenience function).
    
    Args:
        content_metadata: Content metadata
        frameworks: Compliance frameworks to check
        platform_policies: Platform policies to check
        config: Optional validator configuration
        
    Returns:
        ComplianceValidationResult
    """
    validator = SecurityComplianceValidator(config)
    return await validator.validate_compliance(content_metadata, frameworks, platform_policies)

# Export all classes and functions
__all__ = [
    'SecurityComplianceValidator',
    'SecurityLevel',
    'ThreatType',
    'ComplianceFramework',
    'PlatformPolicy',
    'ComplianceStatus',
    'SecurityThreat',
    'SecurityValidationResult',
    'ComplianceViolation',
    'ComplianceValidationResult',
    'validate_security',
    'validate_compliance'
]