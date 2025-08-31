"""Security Quality Assessor - Enterprise Security Assessment System

Advanced security assessment system for content safety, threat detection,
and security compliance validation with comprehensive security metrics.

Business Logic:
Content security scan → Threat detection → Vulnerability assessment →
Security scoring → Risk analysis → Security recommendations

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import re
import hashlib
import base64
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
import urllib.parse
import json

logger = logging.getLogger(__name__)


class SecurityThreatLevel(Enum):
    """Security threat severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityCategory(Enum):
    """Security assessment categories"""    MALWARE = "malware"
    PHISHING = "phishing"
    SPAM = "spam"
    HARMFUL_CONTENT = "harmful_content"
    DATA_EXPOSURE = "data_exposure"
    INJECTION = "injection"
    XSS = "xss"
    SOCIAL_ENGINEERING = "social_engineering"
    PRIVACY_VIOLATION = "privacy_violation"
    COPYRIGHT_VIOLATION = "copyright_violation"


class ContentType(Enum):
    """Content types for security assessment"""    TEXT = "text"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    FINANCIAL = "financial"
    PERSONAL_DATA = "personal_data"
    CODE = "code"
    MEDIA = "media"


@dataclass
class SecurityThreat:
    """Individual security threat detection"""    threat_id: str
    category: SecurityCategory
    threat_level: SecurityThreatLevel
    confidence: float  # 0.0 to 1.0
    message: str
    
    # Threat details
    detected_content: Optional[str] = None
    content_type: Optional[ContentType] = None
    position: Optional[int] = None
    pattern_matched: Optional[str] = None
    
    # Risk assessment
    risk_score: float = 0.0  # 0-100
    impact_description: str = ""
    likelihood: str = ""  # low, medium, high
    
    # Remediation
    recommendations: List[str] = field(default_factory=list)
    mitigation_steps: List[str] = field(default_factory=list)
    
    # Metadata
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'threat_id': self.threat_id,
            'category': self.category.value,
            'threat_level': self.threat_level.value,
            'confidence': self.confidence,
            'message': self.message,
            'detected_content': self.detected_content,
            'content_type': self.content_type.value if self.content_type else None,
            'position': self.position,
            'pattern_matched': self.pattern_matched,
            'risk_score': self.risk_score,
            'impact_description': self.impact_description,
            'likelihood': self.likelihood,
            'recommendations': self.recommendations,
            'mitigation_steps': self.mitigation_steps,
            'detection_timestamp': self.detection_timestamp.isoformat(),
            'source_rules': self.source_rules
        }


@dataclass
class SecurityAssessmentResult:
    """Comprehensive security assessment result"""    content_id: str
    overall_security_score: float  # 0-100
    security_level: str  # secure, warning, unsafe, critical
    
    # Threat breakdown
    total_threats: int = 0
    critical_threats: int = 0
    high_threats: int = 0
    medium_threats: int = 0
    low_threats: int = 0
    
    # Category analysis
    threats_by_category: Dict[SecurityCategory, int] = field(default_factory=dict)
    
    # Detected threats
    threats: List[SecurityThreat] = field(default_factory=list)
    
    # Security recommendations
    security_recommendations: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    
    # Analysis metadata
    assessment_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    scanned_content_types: List[ContentType] = field(default_factory=list)
    
    def add_threat(self, threat: SecurityThreat):
        """Add a security threat"""        self.threats.append(threat)
        self.total_threats += 1
        
        # Update counts by threat level
        if threat.threat_level == SecurityThreatLevel.CRITICAL:
            self.critical_threats += 1
        elif threat.threat_level == SecurityThreatLevel.HIGH:
            self.high_threats += 1
        elif threat.threat_level == SecurityThreatLevel.MEDIUM:
            self.medium_threats += 1
        elif threat.threat_level == SecurityThreatLevel.LOW:
            self.low_threats += 1
        
        # Update category counts
        if threat.category not in self.threats_by_category:
            self.threats_by_category[threat.category] = 0
        self.threats_by_category[threat.category] += 1
    
    def get_threats_by_level(self, level: SecurityThreatLevel) -> List[SecurityThreat]:
        """Get threats by threat level"""        return [t for t in self.threats if t.threat_level == level]
    
    def get_critical_threats(self) -> List[SecurityThreat]:
        """Get critical threats"""        return self.get_threats_by_level(SecurityThreatLevel.CRITICAL)
    
    def has_blocking_threats(self) -> bool:
        """Check if there are blocking security threats"""        return self.critical_threats > 0 or self.high_threats > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'overall_security_score': self.overall_security_score,
            'security_level': self.security_level,
            'threat_counts': {
                'total': self.total_threats,
                'critical': self.critical_threats,
                'high': self.high_threats,
                'medium': self.medium_threats,
                'low': self.low_threats
            },
            'threats_by_category': {cat.value: count for cat, count in self.threats_by_category.items()},
            'threats': [threat.to_dict() for threat in self.threats],
            'security_recommendations': self.security_recommendations,
            'immediate_actions': self.immediate_actions,
            'assessment_timestamp': self.assessment_timestamp.isoformat(),
            'processing_time_ms': self.processing_time_ms,
            'scanned_content_types': [ct.value for ct in self.scanned_content_types]
        }


class MalwareDetector:
    """Malware and suspicious content detection"""    
    def __init__(self):
        self.suspicious_patterns = self._initialize_malware_patterns()
        self.file_extensions = self._initialize_dangerous_extensions()
        
    def _initialize_malware_patterns(self) -> Dict[str, Tuple[str, SecurityThreatLevel]]:
        """Initialize malware detection patterns"""        return {
            # Suspicious URLs
            r'bit\.ly/[a-zA-Z0-9]+': ("Suspicious short URL", SecurityThreatLevel.MEDIUM),
            r'tinyurl\.com/[a-zA-Z0-9]+': ("Suspicious short URL", SecurityThreatLevel.MEDIUM),
            r'[a-zA-Z0-9]+\.tk/': ("Suspicious domain (.tk)", SecurityThreatLevel.HIGH),
            r'[a-zA-Z0-9]+\.ml/': ("Suspicious domain (.ml)", SecurityThreatLevel.HIGH),
            
            # Suspicious file references
            r'\.exe\b': ("Executable file reference", SecurityThreatLevel.HIGH),
            r'\.scr\b': ("Screen saver executable", SecurityThreatLevel.HIGH),
            r'\.bat\b': ("Batch file reference", SecurityThreatLevel.MEDIUM),
            r'\.cmd\b': ("Command file reference", SecurityThreatLevel.MEDIUM),
            
            # Suspicious code patterns
            r'eval\s*\(': ("Potential code injection", SecurityThreatLevel.HIGH),
            r'exec\s*\(': ("Potential code execution", SecurityThreatLevel.HIGH),
            r'<script[^>]*>': ("Script tag detected", SecurityThreatLevel.MEDIUM),
            r'javascript:': ("JavaScript protocol", SecurityThreatLevel.MEDIUM),
            
            # Encoded content (potential obfuscation)
            r'base64[,:]': ("Base64 encoded content", SecurityThreatLevel.MEDIUM),
            r'%[0-9a-fA-F]{2}': ("URL encoded content", SecurityThreatLevel.LOW),
            
            # Suspicious commands
            r'powershell.*-encodedcommand': ("PowerShell encoded command", SecurityThreatLevel.CRITICAL),
            r'cmd\.exe.*\/c': ("Command execution", SecurityThreatLevel.HIGH),
            r'wget\s+http': ("File download command", SecurityThreatLevel.MEDIUM),
            r'curl\s+http': ("File download command", SecurityThreatLevel.MEDIUM)
        }
    
    def _initialize_dangerous_extensions(self) -> Set[str]:
        """Initialize dangerous file extensions"""        return {
            '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js',
            '.jar', '.app', '.deb', '.pkg', '.dmg', '.msi', '.reg'
        }
    
    def detect_malware_indicators(self, content: str) -> List[SecurityThreat]:
        """Detect malware indicators in content"""        threats = []
        
        for pattern, (description, threat_level) in self.suspicious_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                threat_id = hashlib.md5(f"{pattern}_{match.group()}".encode()).hexdigest()[:8]
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.MALWARE,
                    threat_level=threat_level,
                    confidence=0.7,  # Pattern-based detection has moderate confidence
                    message=f"Malware indicator detected: {description}",
                    detected_content=match.group(),
                    content_type=ContentType.TEXT,
                    position=match.start(),
                    pattern_matched=pattern,
                    risk_score=self._calculate_malware_risk_score(threat_level),
                    impact_description=f"Potential {description.lower()} could compromise security",
                    likelihood="medium",
                    recommendations=[
                        "Remove or verify the suspicious content",
                        "Scan for additional malware indicators",
                        "Implement content filtering"
                    ],
                    source_rules=[f"malware_pattern_{pattern}"]
                )
                
                threats.append(threat)
        
        return threats
    
    def _calculate_malware_risk_score(self, threat_level: SecurityThreatLevel) -> float:
        """Calculate risk score for malware threats"""        scores = {
            SecurityThreatLevel.LOW: 25.0,
            SecurityThreatLevel.MEDIUM: 50.0,
            SecurityThreatLevel.HIGH: 75.0,
            SecurityThreatLevel.CRITICAL: 95.0
        }
        return scores.get(threat_level, 50.0)


class PhishingDetector:
    """Phishing and social engineering detection"""    
    def __init__(self):
        self.phishing_patterns = self._initialize_phishing_patterns()
        self.social_engineering_keywords = self._initialize_social_engineering_keywords()
        
    def _initialize_phishing_patterns(self) -> Dict[str, Tuple[str, SecurityThreatLevel]]:
        """Initialize phishing detection patterns"""        return {
            # Urgency indicators
            r'urgent[ly]*\s+act': ("Urgency manipulation", SecurityThreatLevel.HIGH),
            r'limited\s+time\s+offer': ("Time pressure tactic", SecurityThreatLevel.MEDIUM),
            r'expires?\s+(?:today|soon|in|within)': ("Expiration pressure", SecurityThreatLevel.MEDIUM),
            r'immediate[ly]*\s+(?:action|response)': ("Immediate action required", SecurityThreatLevel.HIGH),
            
            # Credential requests
            r'(?:verify|confirm|update).*(?:password|account|login)': ("Credential verification request", SecurityThreatLevel.HIGH),
            r'click\s+here\s+to\s+(?:login|verify|confirm)': ("Suspicious login request", SecurityThreatLevel.HIGH),
            r'suspended.*account': ("Account suspension threat", SecurityThreatLevel.HIGH),
            
            # Reward/prize scams
            r'congratulations.*(?:won|winner|prize)': ("Prize/lottery scam", SecurityThreatLevel.MEDIUM),
            r'claim\s+your.*(?:prize|reward|gift)': ("Reward claim scam", SecurityThreatLevel.MEDIUM),
            r'you\'ve\s+been\s+selected': ("Selection scam", SecurityThreatLevel.MEDIUM),
            
            # Authority impersonation
            r'(?:bank|paypal|amazon|microsoft|google).*security': ("Authority impersonation", SecurityThreatLevel.HIGH),
            r'(?:irs|tax|government).*(?:refund|payment)': ("Government impersonation", SecurityThreatLevel.HIGH),
            
            # Suspicious links
            r'bit\.ly|tinyurl|t\.co': ("Shortened URL", SecurityThreatLevel.MEDIUM),
            r'https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+': ("IP address URL", SecurityThreatLevel.HIGH)
        }
    
    def _initialize_social_engineering_keywords(self) -> Dict[str, SecurityThreatLevel]:
        """Initialize social engineering keywords"""        return {
            'free money': SecurityThreatLevel.HIGH,
            'get rich quick': SecurityThreatLevel.HIGH,
            'work from home': SecurityThreatLevel.MEDIUM,
            'no experience required': SecurityThreatLevel.MEDIUM,
            'guaranteed income': SecurityThreatLevel.HIGH,
            'act now': SecurityThreatLevel.MEDIUM,
            'limited time': SecurityThreatLevel.MEDIUM,
            'risk free': SecurityThreatLevel.MEDIUM,
            'secret method': SecurityThreatLevel.HIGH,
            'banks hate this': SecurityThreatLevel.HIGH
        }
    
    def detect_phishing_indicators(self, content: str) -> List[SecurityThreat]:
        """Detect phishing indicators in content"""        threats = []
        
        # Pattern-based detection
        for pattern, (description, threat_level) in self.phishing_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                threat_id = hashlib.md5(f"phishing_{pattern}_{match.group()}".encode()).hexdigest()[:8]
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.PHISHING,
                    threat_level=threat_level,
                    confidence=0.6,
                    message=f"Phishing indicator: {description}",
                    detected_content=match.group(),
                    content_type=ContentType.TEXT,
                    position=match.start(),
                    pattern_matched=pattern,
                    risk_score=self._calculate_phishing_risk_score(threat_level),
                    impact_description=f"Potential phishing attempt using {description.lower()}",
                    likelihood="medium",
                    recommendations=[
                        "Verify the legitimacy of requests",
                        "Remove suspicious content",
                        "Implement phishing protection measures"
                    ],
                    source_rules=[f"phishing_pattern_{pattern}"]
                )
                
                threats.append(threat)
        
        # Keyword-based detection
        for keyword, threat_level in self.social_engineering_keywords.items():
            if keyword.lower() in content.lower():
                position = content.lower().find(keyword.lower())
                threat_id = hashlib.md5(f"social_eng_{keyword}".encode()).hexdigest()[:8]
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.SOCIAL_ENGINEERING,
                    threat_level=threat_level,
                    confidence=0.5,
                    message=f"Social engineering keyword detected: {keyword}",
                    detected_content=keyword,
                    content_type=ContentType.TEXT,
                    position=position,
                    risk_score=self._calculate_phishing_risk_score(threat_level),
                    impact_description=f"Social engineering tactic: {keyword}",
                    likelihood="medium",
                    recommendations=[
                        "Review content for misleading claims",
                        "Ensure compliance with advertising standards",
                        "Add appropriate disclaimers"
                    ],
                    source_rules=[f"social_engineering_{keyword}"]
                )
                
                threats.append(threat)
        
        return threats
    
    def _calculate_phishing_risk_score(self, threat_level: SecurityThreatLevel) -> float:
        """Calculate risk score for phishing threats"""        scores = {
            SecurityThreatLevel.LOW: 20.0,
            SecurityThreatLevel.MEDIUM: 45.0,
            SecurityThreatLevel.HIGH: 70.0,
            SecurityThreatLevel.CRITICAL: 90.0
        }
        return scores.get(threat_level, 40.0)


class DataPrivacyScanner:
    """Data privacy and sensitive information scanner"""    
    def __init__(self):
        self.privacy_patterns = self._initialize_privacy_patterns()
        
    def _initialize_privacy_patterns(self) -> Dict[str, Tuple[str, SecurityThreatLevel, ContentType]]:
        """Initialize privacy-sensitive data patterns"""        return {
            # Email addresses
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': (
                "Email address detected", SecurityThreatLevel.MEDIUM, ContentType.EMAIL
            ),
            
            # Phone numbers
            r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b': (
                "Phone number detected", SecurityThreatLevel.MEDIUM, ContentType.PHONE
            ),
            
            # Social Security Numbers (US)
            r'\b\d{3}-\d{2}-\d{4}\b': (
                "Social Security Number detected", SecurityThreatLevel.CRITICAL, ContentType.PERSONAL_DATA
            ),
            
            # Credit card patterns
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b': (
                "Credit card number detected", SecurityThreatLevel.CRITICAL, ContentType.FINANCIAL
            ),
            
            # IP addresses (private ranges)
            r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b': (
                "Private IP address detected", SecurityThreatLevel.MEDIUM, ContentType.TEXT
            ),
            
            # API keys and tokens
            r'(?:api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]\s*[\'"]?[a-zA-Z0-9]{16,}[\'"]?': (
                "API key/token detected", SecurityThreatLevel.HIGH, ContentType.TEXT
            ),
            
            # Database connection strings
            r'(?:mongodb|mysql|postgresql|oracle)://[^\s]+': (
                "Database connection string", SecurityThreatLevel.HIGH, ContentType.TEXT
            ),
            
            # AWS credentials
            r'AKIA[0-9A-Z]{16}': (
                "AWS access key detected", SecurityThreatLevel.CRITICAL, ContentType.TEXT
            )
        }
    
    def scan_privacy_violations(self, content: str) -> List[SecurityThreat]:
        """Scan for privacy violations and sensitive data"""        threats = []
        
        for pattern, (description, threat_level, content_type) in self.privacy_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                threat_id = hashlib.md5(f"privacy_{pattern}_{match.group()}".encode()).hexdigest()[:8]
                
                # Mask sensitive data in detected content
                detected_content = self._mask_sensitive_data(match.group(), content_type)
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.DATA_EXPOSURE,
                    threat_level=threat_level,
                    confidence=0.8,
                    message=f"Privacy violation: {description}",
                    detected_content=detected_content,
                    content_type=content_type,
                    position=match.start(),
                    pattern_matched=pattern,
                    risk_score=self._calculate_privacy_risk_score(threat_level, content_type),
                    impact_description=f"Potential privacy violation: exposed {description.lower()}",
                    likelihood="high",
                    recommendations=self._get_privacy_recommendations(content_type),
                    mitigation_steps=self._get_privacy_mitigation_steps(content_type),
                    source_rules=[f"privacy_pattern_{content_type.value}"]
                )
                
                threats.append(threat)
        
        return threats
    
    def _mask_sensitive_data(self, data: str, content_type: ContentType) -> str:
        """Mask sensitive data for logging/reporting"""        if content_type == ContentType.EMAIL:
            parts = data.split('@')
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        elif content_type == ContentType.PHONE:
            return f"***-***-{data[-4:]}" if len(data) >= 4 else "***"
        elif content_type == ContentType.FINANCIAL:
            return f"****-****-****-{data[-4:]}" if len(data) >= 4 else "****"
        elif content_type == ContentType.PERSONAL_DATA:
            return "***-**-****"
        
        return data[:4] + "*" * (len(data) - 4) if len(data) > 4 else "****"
    
    def _calculate_privacy_risk_score(self, threat_level: SecurityThreatLevel, 
                                    content_type: ContentType) -> float:
        """Calculate risk score for privacy violations"""        base_scores = {
            SecurityThreatLevel.LOW: 20.0,
            SecurityThreatLevel.MEDIUM: 50.0,
            SecurityThreatLevel.HIGH: 80.0,
            SecurityThreatLevel.CRITICAL: 95.0
        }
        
        # Adjust based on content type sensitivity
        content_multipliers = {
            ContentType.FINANCIAL: 1.2,
            ContentType.PERSONAL_DATA: 1.15,
            ContentType.EMAIL: 1.0,
            ContentType.PHONE: 1.0,
            ContentType.TEXT: 0.9
        }
        
        base_score = base_scores.get(threat_level, 50.0)
        multiplier = content_multipliers.get(content_type, 1.0)
        
        return min(100.0, base_score * multiplier)
    
    def _get_privacy_recommendations(self, content_type: ContentType) -> List[str]:
        """Get privacy-specific recommendations"""        recommendations = {
            ContentType.EMAIL: [
                "Remove or mask email addresses",
                "Use contact forms instead of direct email exposure",
                "Implement email obfuscation techniques"
            ],
            ContentType.PHONE: [
                "Remove or mask phone numbers",
                "Use contact forms for inquiries",
                "Consider using business phone numbers only"
            ],
            ContentType.FINANCIAL: [
                "Remove all financial information immediately",
                "Never expose credit card or account numbers",
                "Use secure payment processors"
            ],
            ContentType.PERSONAL_DATA: [
                "Remove all personal identifying information",
                "Comply with GDPR and privacy regulations",
                "Implement data anonymization"
            ]
        }
        
        return recommendations.get(content_type, ["Remove sensitive information"])
    
    def _get_privacy_mitigation_steps(self, content_type: ContentType) -> List[str]:
        """Get privacy mitigation steps"""        steps = {
            ContentType.FINANCIAL: [
                "Immediately remove financial data",
                "Notify affected parties if already published",
                "Review content approval processes"
            ],
            ContentType.PERSONAL_DATA: [
                "Remove personal data immediately",
                "Check legal compliance requirements",
                "Implement data protection measures"
            ]
        }
        
        return steps.get(content_type, ["Review and remove sensitive content"])


class SecurityQualityAssessor:
    """Enterprise security quality assessment system"""    
    def __init__(self):
        self.malware_detector = MalwareDetector()
        self.phishing_detector = PhishingDetector()
        self.privacy_scanner = DataPrivacyScanner()
    
    def assess_security_quality(self, content_data: Dict[str, Any],
                               content_id: str = "unknown") -> SecurityAssessmentResult:
        """Perform comprehensive security assessment"""        start_time = datetime.now(timezone.utc)
        
        # Initialize result
        result = SecurityAssessmentResult(
            content_id=content_id,
            overall_security_score=0.0,
            security_level="unknown"
        )
        
        try:
            # Extract content for analysis
            content_text = self._extract_text_content(content_data)
            
            if content_text:
                result.scanned_content_types.append(ContentType.TEXT)
                
                # Malware detection
                malware_threats = self.malware_detector.detect_malware_indicators(content_text)
                for threat in malware_threats:
                    result.add_threat(threat)
                
                # Phishing detection
                phishing_threats = self.phishing_detector.detect_phishing_indicators(content_text)
                for threat in phishing_threats:
                    result.add_threat(threat)
                
                # Privacy scanning
                privacy_threats = self.privacy_scanner.scan_privacy_violations(content_text)
                for threat in privacy_threats:
                    result.add_threat(threat)
            
            # URL-specific analysis
            urls = self._extract_urls(content_data)
            if urls:
                result.scanned_content_types.append(ContentType.URL)
                url_threats = self._analyze_urls(urls)
                for threat in url_threats:
                    result.add_threat(threat)
            
            # Calculate overall security score
            result.overall_security_score = self._calculate_security_score(result)
            
            # Determine security level
            result.security_level = self._assess_security_level(result)
            
            # Generate recommendations
            result.security_recommendations = self._generate_security_recommendations(result)
            
            # Generate immediate actions
            result.immediate_actions = self._generate_immediate_actions(result)
            
        except Exception as e:
            logger.error(f"Security assessment error: {e}")
            result.add_threat(SecurityThreat(
                threat_id="system_error",
                category=SecurityCategory.MALWARE,
                threat_level=SecurityThreatLevel.HIGH,
                confidence=1.0,
                message=f"Security assessment failed: {str(e)}"
            ))
        
        # Finalize result
        end_time = datetime.now(timezone.utc)
        result.processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    def _extract_text_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content for analysis"""        text_parts = []
        
        # Standard text fields
        text_fields = ['title', 'description', 'content', 'caption', 'body', 'text']
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                text_parts.append(str(content_data[field]))
        
        # Metadata text
        if 'metadata' in content_data and isinstance(content_data['metadata'], dict):
            for key, value in content_data['metadata'].items():
                if isinstance(value, str):
                    text_parts.append(value)
        
        return ' '.join(text_parts)
    
    def _extract_urls(self, content_data: Dict[str, Any]) -> List[str]:
        """Extract URLs from content"""        urls = []
        
        # Direct URL fields
        url_fields = ['url', 'link', 'website', 'homepage']
        for field in url_fields:
            if field in content_data and content_data[field]:
                urls.append(str(content_data[field]))
        
        # Extract URLs from text content
        text_content = self._extract_text_content(content_data)
        url_pattern = r'https?://[^\s<>"\'{|}\\^`\[\]]+[^\s<>"\'{|}\\^`\[\].,;!?]'
        found_urls = re.findall(url_pattern, text_content)
        urls.extend(found_urls)
        
        return list(set(urls))  # Remove duplicates
    
    def _analyze_urls(self, urls: List[str]) -> List[SecurityThreat]:
        """Analyze URLs for security threats"""        threats = []
        
        for url in urls:
            try:
                parsed_url = urllib.parse.urlparse(url)
                
                # Check for suspicious domains
                domain_threats = self._check_suspicious_domain(parsed_url.netloc, url)
                threats.extend(domain_threats)
                
                # Check for URL manipulation
                manipulation_threats = self._check_url_manipulation(url)
                threats.extend(manipulation_threats)
                
                # Check for direct IP access
                ip_threats = self._check_ip_access(parsed_url.netloc, url)
                threats.extend(ip_threats)
                
            except Exception as e:
                logger.warning(f"Error analyzing URL {url}: {e}")
        
        return threats
    
    def _check_suspicious_domain(self, domain: str, full_url: str) -> List[SecurityThreat]:
        """Check for suspicious domains"""        threats = []
        
        # Suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.info', '.biz']
        
        for tld in suspicious_tlds:
            if domain.endswith(tld):
                threat_id = hashlib.md5(f"domain_{domain}".encode()).hexdigest()[:8]
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.PHISHING,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    confidence=0.6,
                    message=f"Suspicious domain with TLD: {tld}",
                    detected_content=domain,
                    content_type=ContentType.URL,
                    risk_score=60.0,
                    impact_description=f"Domain using suspicious TLD {tld}",
                    likelihood="medium",
                    recommendations=[
                        "Verify domain legitimacy",
                        "Use reputable domains only",
                        "Consider domain reputation checks"
                    ],
                    source_rules=[f"suspicious_tld_{tld}"]
                )
                
                threats.append(threat)
        
        return threats
    
    def _check_url_manipulation(self, url: str) -> List[SecurityThreat]:
        """Check for URL manipulation techniques"""        threats = []
        
        # Check for excessive redirects or URL shorteners
        shortener_domains = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly']
        
        for shortener in shortener_domains:
            if shortener in url:
                threat_id = hashlib.md5(f"shortener_{url}".encode()).hexdigest()[:8]
                
                threat = SecurityThreat(
                    threat_id=threat_id,
                    category=SecurityCategory.PHISHING,
                    threat_level=SecurityThreatLevel.MEDIUM,
                    confidence=0.7,
                    message=f"URL shortener detected: {shortener}",
                    detected_content=url,
                    content_type=ContentType.URL,
                    risk_score=50.0,
                    impact_description="URL shortener may hide malicious destination",
                    likelihood="medium",
                    recommendations=[
                        "Use full URLs instead of shortened ones",
                        "Verify destination URLs",
                        "Consider URL preview tools"
                    ],
                    source_rules=[f"url_shortener_{shortener}"]
                )
                
                threats.append(threat)
        
        return threats
    
    def _check_ip_access(self, domain: str, full_url: str) -> List[SecurityThreat]:
        """Check for direct IP address access"""        threats = []
        
        # Check if domain is an IP address
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        
        if re.match(ip_pattern, domain):
            threat_id = hashlib.md5(f"ip_access_{domain}".encode()).hexdigest()[:8]
            
            threat = SecurityThreat(
                threat_id=threat_id,
                category=SecurityCategory.PHISHING,
                threat_level=SecurityThreatLevel.HIGH,
                confidence=0.8,
                message="Direct IP address access detected",
                detected_content=domain,
                content_type=ContentType.URL,
                risk_score=75.0,
                impact_description="Direct IP access may indicate malicious content",
                likelihood="high",
                recommendations=[
                    "Use domain names instead of IP addresses",
                    "Verify the legitimacy of IP-based URLs",
                    "Implement domain validation"
                ],
                source_rules=["direct_ip_access"]
            )
            
            threats.append(threat)
        
        return threats
    
    def _calculate_security_score(self, result: SecurityAssessmentResult) -> float:
        """Calculate overall security score"""        base_score = 100.0
        
        # Deduct points based on threat levels
        for threat in result.threats:
            if threat.threat_level == SecurityThreatLevel.CRITICAL:
                base_score -= 25
            elif threat.threat_level == SecurityThreatLevel.HIGH:
                base_score -= 15
            elif threat.threat_level == SecurityThreatLevel.MEDIUM:
                base_score -= 8
            elif threat.threat_level == SecurityThreatLevel.LOW:
                base_score -= 3
        
        # Additional penalty for multiple threats of same category
        for category, count in result.threats_by_category.items():
            if count > 1:
                base_score -= (count - 1) * 2  # Penalty for multiple threats
        
        return max(0.0, base_score)
    
    def _assess_security_level(self, result: SecurityAssessmentResult) -> str:
        """Assess security level based on threats and score"""        if result.critical_threats > 0:
            return "critical"
        elif result.high_threats > 0:
            return "unsafe"
        elif result.medium_threats > 0 or result.overall_security_score < 70:
            return "warning"
        else:
            return "secure"
    
    def _generate_security_recommendations(self, result: SecurityAssessmentResult) -> List[str]:
        """Generate security recommendations"""        recommendations = []
        
        # General recommendations based on security level
        if result.security_level == "critical":
            recommendations.append("CRITICAL: Do not publish content - security threats detected")
        elif result.security_level == "unsafe":
            recommendations.append("Content has high security risks - review immediately")
        elif result.security_level == "warning":
            recommendations.append("Address security warnings before publication")
        else:
            recommendations.append("Content security is acceptable")
        
        # Category-specific recommendations
        if SecurityCategory.DATA_EXPOSURE in result.threats_by_category:
            recommendations.append("Remove all exposed sensitive data")
        
        if SecurityCategory.MALWARE in result.threats_by_category:
            recommendations.append("Scan for and remove malware indicators")
        
        if SecurityCategory.PHISHING in result.threats_by_category:
            recommendations.append("Review content for phishing/scam indicators")
        
        # Threat-specific recommendations
        unique_recommendations = set()
        for threat in result.threats:
            unique_recommendations.update(threat.recommendations)
        
        recommendations.extend(list(unique_recommendations))
        
        return recommendations
    
    def _generate_immediate_actions(self, result: SecurityAssessmentResult) -> List[str]:
        """Generate immediate actions required"""        actions = []
        
        # Critical and high threat actions
        critical_and_high = result.get_threats_by_level(SecurityThreatLevel.CRITICAL) + \
                           result.get_threats_by_level(SecurityThreatLevel.HIGH)
        
        for threat in critical_and_high:
            actions.extend(threat.mitigation_steps)
        
        # Remove duplicates
        return list(set(actions))
    
    def batch_assess_security(self, content_items: List[Dict[str, Any]]) -> List[SecurityAssessmentResult]:
        """Assess security for multiple content items"""        results = []
        
        for i, content_data in enumerate(content_items):
            content_id = content_data.get('id', f'content_{i}')
            result = self.assess_security_quality(content_data, content_id)
            results.append(result)
        
        return results
    
    def get_security_summary(self, results: List[SecurityAssessmentResult]) -> Dict[str, Any]:
        """Get security summary for multiple assessments"""        if not results:
            return {}
        
        total_assessments = len(results)
        secure_content = sum(1 for r in results if r.security_level == "secure")
        avg_score = sum(r.overall_security_score for r in results) / total_assessments
        
        # Threat statistics
        total_threats = sum(r.total_threats for r in results)
        critical_threats = sum(r.critical_threats for r in results)
        
        # Category breakdown
        category_threats = {}
        for result in results:
            for category, count in result.threats_by_category.items():
                category_name = category.value
                category_threats[category_name] = category_threats.get(category_name, 0) + count
        
        return {
            'total_assessments': total_assessments,
            'secure_content': secure_content,
            'security_rate_percent': (secure_content / total_assessments) * 100,
            'average_security_score': avg_score,
            'total_threats': total_threats,
            'critical_threats': critical_threats,
            'threats_by_category': category_threats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
