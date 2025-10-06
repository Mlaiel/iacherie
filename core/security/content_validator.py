#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Validator Module
Provides comprehensive content validation and security checking services
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
import html
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """
Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    """
Content validation categories"""
    SECURITY = "security"
    CONTENT = "content"
    FORMAT = "format"
    POLICY = "policy"
    SYNTAX = "syntax"

@dataclass
class ValidationIssue:
    """
Validation issue data structure"""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    code: Optional[str] = None

@dataclass
class ValidationResult:
    """
Content validation result"""
    is_valid: bool
    issues: List[ValidationIssue]
    score: float
    metadata: Dict[str, Any] = None

class ContentValidator:
    """
    Enterprise-grade content validation service
    Provides security, format, and policy validation
    """
    
    def __init__(self):
        """
Initialize content validator"""
        self.security_patterns = {}
        self.content_policies = {}
        self.format_validators = {}
        self.syntax_checkers = {}
        
        # Initialize validation rules
        self._setup_security_patterns()
        self._setup_content_policies()
        self._setup_format_validators()
        self._setup_syntax_checkers()
        
        logger.info("🛡️ Content Validator initialized successfully")
    
    def _setup_security_patterns(self):
        """
Setup security validation patterns"""
        self.security_patterns = {
            'xss': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>'
            ],
            'sql_injection': [
                r'(union|select|insert|update|delete|drop|create|alter)\s+',
                r'(\;|\-\-|\#)',
                r'(\bor\b|\band\b)\s+\d+\s*=\s*\d+',
                r'\'.*?\bor\b.*?\'',
                r'\".*?\bor\b.*?\"'
            ],
            'code_injection': [
                r'eval\s*\(',
                r'exec\s*\(',
                r'system\s*\(',
                r'shell_exec\s*\(',
                r'passthru\s*\(',
                r'file_get_contents\s*\(',
                r'include\s*\(',
                r'require\s*\('
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'/etc/passwd',
                r'/etc/shadow',
                r'\\windows\\system32',
                r'%2e%2e%2f',
                r'%2e%2e%5c'
            ],
            'malicious_urls': [
                r'https?://\d+\.\d+\.\d+\.\d+',  # IP addresses
                r'bit\.ly|tinyurl|t\.co',  # URL shorteners
                r'[a-z0-9]+\.tk|\.ml|\.ga|\.cf',  # Suspicious TLDs
                r'data:text/html',
                r'javascript:'
            ]
        }
    
    def _setup_content_policies(self):
        """
Setup content policy rules"""
        self.content_policies = {
            'profanity': [
                # Basic profanity patterns (family-friendly list)
                r'\b(spam|scam|fake|fraud)\b',
                r'\b(hate|violence|illegal)\b'
            ],
            'spam': [
                r'(click here|click now|act now)',
                r'(free money|easy money|get rich)',
                r'(limited time|urgent|immediate)',
                r'(\$\$\$|!!!|amazing deal)',
                r'(viagra|cialis|pharmacy)',
                r'(lottery|winner|congratulations)'
            ],
            'personal_info': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # IP address
            ],
            'inappropriate_content': [
                r'\b(adult|explicit|mature)\b',
                r'\b(gambling|casino|betting)\b',
                r'\b(drugs|alcohol|smoking)\b'
            ]
        }
    
    def _setup_format_validators(self):
        """
Setup format validation rules"""
        self.format_validators = {
            'html': {
                'allowed_tags': ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'img'],
                'required_attributes': {'a': ['href'], 'img': ['src', 'alt']},
                'max_nesting': 5
            },
            'json': {
                'max_depth': 10,
                'max_size': 1024 * 1024,  # 1MB
                'required_fields': []
            },
            'url': {
                'allowed_schemes': ['http', 'https', 'ftp'],
                'max_length': 2048,
                'require_tld': True
            },
            'text': {
                'max_length': 10000,
                'min_length': 1,
                'allowed_chars': r'[a-zA-Z0-9\s\.,;:!?\-_@#$%^&*()+=\[\]{}|\\<>/"\'`~]'
            }
        }
    
    def _setup_syntax_checkers(self):
        """
Setup syntax validation checkers"""
        self.syntax_checkers = {
            'html': {
                'unclosed_tags': r'<(\w+)[^>]*>(?!.*</\1>)',
                'malformed_tags': r'<[^>]*[^/]>$',
                'invalid_attributes': r'<\w+[^>]*\s(\w+)(?!\s*=)[^>]*>'
            },
            'json': {
                'trailing_comma': r',\s*[}\]]',
                'unquoted_keys': r'{\s*(\w+)\s*:',
                'single_quotes': r"'[^']*'"
            },
            'css': {
                'unclosed_braces': r'{[^}]*$',
                'invalid_properties': r'[a-zA-Z-]+\s*:\s*[^;]*[^;}]\s*$',
                'missing_semicolon': r'[^;}]\s*}'
            }
        }
    
    def validate_content(self, content: str, content_type: str = "text", 
                        strict_mode: bool = False) -> ValidationResult:
        """
        Validate content for security, format, and policy compliance
        
        Args:
            content: Content to validate
            content_type: Type of content (text, html, json, etc.)
            strict_mode: Whether to apply strict validation rules
            
        Returns:
            ValidationResult with issues and validation score
        """
        try:
            issues = []
            
            # Security validation
            security_issues = self._validate_security(content)
            issues.extend(security_issues)
            
            # Content policy validation
            policy_issues = self._validate_content_policies(content)
            issues.extend(policy_issues)
            
            # Format validation
            format_issues = self._validate_format(content, content_type)
            issues.extend(format_issues)
            
            # Syntax validation
            syntax_issues = self._validate_syntax(content, content_type)
            issues.extend(syntax_issues)
            
            # Calculate validation score
            score = self._calculate_validation_score(issues, len(content))
            
            # Determine if content is valid
            critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
            error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
            
            is_valid = len(critical_issues) == 0 and (not strict_mode or len(error_issues) == 0)
            
            return ValidationResult(
                is_valid=is_valid,
                issues=issues,
                score=score,
                metadata={
                    'content_type': content_type,
                    'content_length': len(content),
                    'strict_mode': strict_mode,
                    'total_issues': len(issues),
                    'critical_issues': len(critical_issues),
                    'error_issues': len(error_issues)
                }
            )
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    category=ValidationCategory.SECURITY,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation error: {str(e)}",
                    code="VALIDATION_ERROR"
                )],
                score=0.0,
                metadata={"error": str(e)}
            )
    
    def _validate_security(self, content: str) -> List[ValidationIssue]:
        """
Validate content for security issues"""
        issues = []
        content_lower = content.lower()
        
        for security_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.SECURITY,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Potential {security_type.replace('_', ' ')} detected",
                        location=f"Position {match.start()}-{match.end()}",
                        suggestion=f"Remove or sanitize suspicious {security_type.replace('_', ' ')} pattern",
                        code=f"SEC_{security_type.upper()}"
                    ))
        
        return issues
    
    def _validate_content_policies(self, content: str) -> List[ValidationIssue]:
        """
Validate content against content policies"""
        issues = []
        content_lower = content.lower()
        
        for policy_type, patterns in self.content_policies.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    severity = ValidationSeverity.ERROR if policy_type == 'personal_info' else ValidationSeverity.WARNING
                    issues.append(ValidationIssue(
                        category=ValidationCategory.POLICY,
                        severity=severity,
                        message=f"Policy violation: {policy_type.replace('_', ' ')} detected",
                        location=f"Position {match.start()}-{match.end()}",
                        suggestion=f"Review and remove inappropriate {policy_type.replace('_', ' ')} content",
                        code=f"POL_{policy_type.upper()}"
                    ))
        
        return issues
    
    def _validate_format(self, content: str, content_type: str) -> List[ValidationIssue]:
        """
Validate content format"""
        issues = []
        
        if content_type not in self.format_validators:
            return issues
        
        validator_config = self.format_validators[content_type]
        
        if content_type == 'html':
            issues.extend(self._validate_html_format(content, validator_config))
        elif content_type == 'json':
            issues.extend(self._validate_json_format(content, validator_config))
        elif content_type == 'url':
            issues.extend(self._validate_url_format(content, validator_config))
        elif content_type == 'text':
            issues.extend(self._validate_text_format(content, validator_config))
        
        return issues
    
    def _validate_html_format(self, content: str, config: Dict) -> List[ValidationIssue]:
        """
Validate HTML format"""
        issues = []
        
        # Check for allowed tags
        tag_pattern = r'<(\w+)[^>]*>'
        tags = re.findall(tag_pattern, content, re.IGNORECASE)
        
        for tag in tags:
            if tag.lower() not in config['allowed_tags']:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FORMAT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Disallowed HTML tag: {tag}",
                    suggestion=f"Use only allowed tags: {', '.join(config['allowed_tags'])}",
                    code="FMT_HTML_TAG"
                ))
        
        return issues
    
    def _validate_json_format(self, content: str, config: Dict) -> List[ValidationIssue]:
        """
Validate JSON format"""
        issues = []
        
        try:
            data = json.loads(content)
            
            # Check JSON depth
            depth = self._get_json_depth(data)
            if depth > config['max_depth']:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FORMAT,
                    severity=ValidationSeverity.ERROR,
                    message=f"JSON depth {depth} exceeds maximum {config['max_depth']}",
                    suggestion="Reduce JSON nesting depth",
                    code="FMT_JSON_DEPTH"
                ))
                
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                category=ValidationCategory.SYNTAX,
                severity=ValidationSeverity.ERROR,
                message=f"Invalid JSON syntax: {str(e)}",
                suggestion="Fix JSON syntax errors",
                code="SYN_JSON_INVALID"
            ))
        
        return issues
    
    def _validate_url_format(self, content: str, config: Dict) -> List[ValidationIssue]:
        """
Validate URL format"""
        issues = []
        
        # Check URL length
        if len(content) > config['max_length']:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT,
                severity=ValidationSeverity.WARNING,
                message=f"URL length {len(content)} exceeds maximum {config['max_length']}",
                suggestion="Use shorter URLs or URL shortening service",
                code="FMT_URL_LENGTH"
            ))
        
        # Check URL scheme
        parsed = urllib.parse.urlparse(content)
        if parsed.scheme and parsed.scheme not in config['allowed_schemes']:
            issues.append(ValidationIssue(
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.ERROR,
                message=f"Disallowed URL scheme: {parsed.scheme}",
                suggestion=f"Use allowed schemes: {', '.join(config['allowed_schemes'])}",
                code="SEC_URL_SCHEME"
            ))
        
        return issues
    
    def _validate_text_format(self, content: str, config: Dict) -> List[ValidationIssue]:
        """
Validate text format"""
        issues = []
        
        # Check text length
        if len(content) > config['max_length']:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT,
                severity=ValidationSeverity.WARNING,
                message=f"Text length {len(content)} exceeds maximum {config['max_length']}",
                suggestion="Reduce text length",
                code="FMT_TEXT_LENGTH"
            ))
        
        if len(content) < config['min_length']:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT,
                severity=ValidationSeverity.INFO,
                message=f"Text length {len(content)} below minimum {config['min_length']}",
                suggestion="Add more content",
                code="FMT_TEXT_SHORT"
            ))
        
        return issues
    
    def _validate_syntax(self, content: str, content_type: str) -> List[ValidationIssue]:
        """
Validate content syntax"""
        issues = []
        
        if content_type not in self.syntax_checkers:
            return issues
        
        checker_config = self.syntax_checkers[content_type]
        
        for check_name, pattern in checker_config.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                issues.append(ValidationIssue(
                    category=ValidationCategory.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    message=f"Syntax error: {check_name.replace('_', ' ')}",
                    location=f"Position {match.start()}-{match.end()}",
                    suggestion=f"Fix {check_name.replace('_', ' ')} syntax issue",
                    code=f"SYN_{check_name.upper()}"
                ))
        
        return issues
    
    def _calculate_validation_score(self, issues: List[ValidationIssue], content_length: int) -> float:
        """
Calculate validation score based on issues"""
        base_score = 100.0
        
        # Deduct points based on issue severity
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 25.0
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 10.0
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 5.0
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 1.0
        
        # Bonus for longer content with fewer issues
        if content_length > 100 and len(issues) == 0:
            base_score = min(base_score + 5.0, 100.0)
        
        return max(base_score, 0.0)
    
    def _get_json_depth(self, obj: Any, depth: int = 0) -> int:
        """
Calculate JSON object depth"""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        else:
            return depth
    
    def sanitize_content(self, content: str, content_type: str = "text") -> str:
        """
Sanitize content by removing/escaping dangerous elements"""
        sanitized = content
        
        if content_type == "html":
            # Basic HTML sanitization
            sanitized = html.escape(sanitized)
            # Allow some safe tags back
            safe_replacements = {
                '&lt;p&gt;': '<p>',
                '&lt;/p&gt;': '</p>',
                '&lt;br&gt;': '<br>',
                '&lt;strong&gt;': '<strong>',
                '&lt;/strong&gt;': '</strong>',
                '&lt;em&gt;': '<em>',
                '&lt;/em&gt;': '</em>'
            }
            for escaped, safe in safe_replacements.items():
                sanitized = sanitized.replace(escaped, safe)
        
        elif content_type == "url":
            # URL sanitization
            sanitized = urllib.parse.quote(sanitized, safe=':/?#[]@!$&\'()*+,;=')
        
        return sanitized
    
    def get_validation_summary(self, result: ValidationResult) -> Dict[str, Any]:
        """
Get summary of validation results"""
        issue_counts = {}
        for severity in ValidationSeverity:
            issue_counts[severity.value] = len([i for i in result.issues if i.severity == severity])
        
        category_counts = {}
        for category in ValidationCategory:
            category_counts[category.value] = len([i for i in result.issues if i.category == category])
        
        return {
            'is_valid': result.is_valid,
            'score': result.score,
            'total_issues': len(result.issues),
            'issues_by_severity': issue_counts,
            'issues_by_category': category_counts,
            'recommendations': self._get_recommendations(result.issues)
        }
    
    def _get_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """
Get recommendations based on validation issues"""
        recommendations = []
        
        if any(i.category == ValidationCategory.SECURITY for i in issues):
            recommendations.append("Review content for security vulnerabilities")
        
        if any(i.category == ValidationCategory.POLICY for i in issues):
            recommendations.append("Ensure content complies with content policies")
        
        if any(i.category == ValidationCategory.FORMAT for i in issues):
            recommendations.append("Check content formatting and structure")
        
        if any(i.category == ValidationCategory.SYNTAX for i in issues):
            recommendations.append("Fix syntax errors in content")
        
        return recommendations

# Create global instance
content_validator = ContentValidator()

# Create alias for backward compatibility
ValidationEngine = ContentValidator

# Export main classes and functions
__all__ = [
    'ContentValidator',
    'ValidationEngine',  # Alias for authentication modules
    'ValidationIssue',
    'ValidationResult',
    'ValidationSeverity',
    'ValidationCategory',
    'content_validator'
]

# Log module initialization
logger.info("🛡️ Content Validator module initialized successfully")
logger.info("✅ Ready for comprehensive content validation and security checking")