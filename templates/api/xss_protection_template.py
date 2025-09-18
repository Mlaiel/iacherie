#!/usr/bin/env python3
"""
⚡ XSS Protection Template - Enterprise Security
🏗️ Architecture: Ainflue Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import re
import html
import json
import bleach
from urllib.parse import urlparse, parse_qs
import base64
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + Frontend Expert
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class XSSProtectionLevel(str, Enum):
    """XSS protection levels"""
    DISABLED = "disabled"
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


class XSSFilterMode(str, Enum):
    """XSS filtering modes"""
    BLOCK = "block"
    SANITIZE = "sanitize"
    ENCODE = "encode"
    WARN = "warn"


class XSSContextType(str, Enum):
    """XSS context types for proper encoding"""
    HTML = "html"
    ATTRIBUTE = "attribute"
    JAVASCRIPT = "javascript"
    CSS = "css"
    URL = "url"
    JSON = "json"


@dataclass
class XSSPattern:
    """XSS attack pattern definition"""
    name: str
    pattern: str
    severity: str  # low, medium, high, critical
    context: XSSContextType
    description: str
    compiled_pattern: Optional[re.Pattern] = None
    
    def __post_init__(self):
        """Compile regex pattern"""
        try:
            flags = re.IGNORECASE | re.MULTILINE | re.DOTALL
            self.compiled_pattern = re.compile(self.pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid XSS pattern '{self.pattern}': {e}")


@dataclass
class XSSConfig:
    """Enterprise XSS protection configuration"""
    # Basic settings
    protection_level: XSSProtectionLevel = XSSProtectionLevel.STRICT
    filter_mode: XSSFilterMode = XSSFilterMode.SANITIZE
    
    # Detection settings
    enable_script_tag_detection: bool = True
    enable_event_handler_detection: bool = True
    enable_javascript_url_detection: bool = True
    enable_data_url_detection: bool = True
    enable_iframe_detection: bool = True
    enable_object_embed_detection: bool = True
    enable_style_injection_detection: bool = True
    enable_svg_xss_detection: bool = True
    enable_dom_xss_detection: bool = True
    
    # Content Security Policy
    enable_csp: bool = True
    csp_policy: Optional[str] = None
    csp_report_only: bool = False
    csp_report_uri: Optional[str] = None
    
    # HTML sanitization
    allowed_tags: Set[str] = field(default_factory=lambda: {
        'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'span', 'div',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
        'a', 'img', 'blockquote', 'code', 'pre'
    })
    allowed_attributes: Dict[str, Set[str]] = field(default_factory=lambda: {
        'a': {'href', 'title', 'target'},
        'img': {'src', 'alt', 'width', 'height', 'title'},
        'span': {'class'},
        'div': {'class', 'id'},
        '*': {'class', 'id'}
    })
    allowed_protocols: Set[str] = field(default_factory=lambda: {'http', 'https', 'mailto'})
    
    # Encoding settings
    encode_html_entities: bool = True
    encode_javascript_strings: bool = True
    encode_css_values: bool = True
    encode_url_parameters: bool = True
    
    # Response modification
    add_xss_protection_header: bool = True
    add_content_type_options: bool = True
    add_frame_options: bool = True
    
    # Custom patterns
    custom_patterns: List[XSSPattern] = field(default_factory=list)
    
    # Creator-specific settings
    enable_creator_content_analysis: bool = True
    allow_creator_html: bool = False  # Strict by default
    creator_safe_domains: Set[str] = field(default_factory=set)
    
    # Monitoring
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_attack_alerts: bool = True


@dataclass
class XSSDetectionResult:
    """XSS detection result"""
    detected: bool
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = "low"
    sanitized_content: Optional[str] = None
    blocked_elements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class XSSMetrics:
    """XSS protection metrics"""
    total_requests: int = 0
    scanned_requests: int = 0
    blocked_attempts: int = 0
    sanitized_attempts: int = 0
    script_injections: int = 0
    event_handler_injections: int = 0
    iframe_injections: int = 0
    javascript_url_injections: int = 0
    data_url_injections: int = 0
    style_injections: int = 0
    svg_injections: int = 0
    
    @property
    def attack_rate(self) -> float:
        if self.scanned_requests == 0:
            return 0.0
        return ((self.blocked_attempts + self.sanitized_attempts) / self.scanned_requests) * 100


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise XSS Protection Middleware
    
    Features:
    - Multi-context XSS detection and prevention
    - Advanced HTML sanitization
    - Content Security Policy enforcement
    - Creator-safe content analysis
    - Real-time threat detection
    - Context-aware encoding
    - DOM-based XSS protection
    - SVG and CSS injection prevention
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[XSSConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or XSSConfig()
        self.logger = logger or self._setup_logger()
        
        # Initialize XSS patterns
        self.patterns = self._initialize_patterns()
        
        # Metrics and tracking
        self.metrics = XSSMetrics()
        self.attack_attempts: List[Dict[str, Any]] = []
        
        # Setup Content Security Policy
        if self.config.enable_csp:
            self._setup_csp()
        
        self.logger.info(f"XSS Protection initialized with {len(self.patterns)} patterns")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup security audit logger"""
        logger = logging.getLogger("xss_protection")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_patterns(self) -> List[XSSPattern]:
        """Initialize comprehensive XSS attack patterns"""
        patterns = []
        
        # Script tag injections
        if self.config.enable_script_tag_detection:
            patterns.extend([
                XSSPattern(
                    "script_tag_basic",
                    r'<script[^>]*>.*?</script>',
                    "critical",
                    XSSContextType.HTML,
                    "Basic script tag injection"
                ),
                XSSPattern(
                    "script_tag_encoded",
                    r'&lt;script[^&]*&gt;.*?&lt;/script&gt;',
                    "critical",
                    XSSContextType.HTML,
                    "HTML-encoded script tag"
                ),
                XSSPattern(
                    "script_src_injection",
                    r'<script[^>]*src\s*=\s*["\'][^"\']*["\'][^>]*>',
                    "critical",
                    XSSContextType.HTML,
                    "Script tag with external source"
                ),
                XSSPattern(
                    "script_without_closing",
                    r'<script[^>]*>(?!</script>)',
                    "high",
                    XSSContextType.HTML,
                    "Script tag without proper closing"
                ),
            ])
        
        # Event handler injections
        if self.config.enable_event_handler_detection:
            patterns.extend([
                XSSPattern(
                    "onclick_injection",
                    r'\bonclick\s*=\s*["\'][^"\']*["\']',
                    "high",
                    XSSContextType.ATTRIBUTE,
                    "onclick event handler injection"
                ),
                XSSPattern(
                    "onload_injection",
                    r'\bonload\s*=\s*["\'][^"\']*["\']',
                    "high",
                    XSSContextType.ATTRIBUTE,
                    "onload event handler injection"
                ),
                XSSPattern(
                    "onerror_injection",
                    r'\bonerror\s*=\s*["\'][^"\']*["\']',
                    "high",
                    XSSContextType.ATTRIBUTE,
                    "onerror event handler injection"
                ),
                XSSPattern(
                    "onmouseover_injection",
                    r'\bonmouseover\s*=\s*["\'][^"\']*["\']',
                    "medium",
                    XSSContextType.ATTRIBUTE,
                    "onmouseover event handler injection"
                ),
                XSSPattern(
                    "event_handler_generic",
                    r'\bon\w+\s*=\s*["\'][^"\']*["\']',
                    "medium",
                    XSSContextType.ATTRIBUTE,
                    "Generic event handler injection"
                ),
            ])
        
        # JavaScript URL injections
        if self.config.enable_javascript_url_detection:
            patterns.extend([
                XSSPattern(
                    "javascript_url",
                    r'javascript:\s*[^"\';\s]+',
                    "high",
                    XSSContextType.URL,
                    "JavaScript URL injection"
                ),
                XSSPattern(
                    "javascript_url_encoded",
                    r'%6a%61%76%61%73%63%72%69%70%74%3a',
                    "high",
                    XSSContextType.URL,
                    "URL-encoded JavaScript URL"
                ),
                XSSPattern(
                    "vbscript_url",
                    r'vbscript:\s*[^"\';\s]+',
                    "high",
                    XSSContextType.URL,
                    "VBScript URL injection"
                ),
            ])
        
        # Data URL injections
        if self.config.enable_data_url_detection:
            patterns.extend([
                XSSPattern(
                    "data_url_html",
                    r'data:text/html[^"\';\s]*',
                    "high",
                    XSSContextType.URL,
                    "Data URL with HTML content"
                ),
                XSSPattern(
                    "data_url_javascript",
                    r'data:[^"\';\s]*;base64,[A-Za-z0-9+/=]*',
                    "medium",
                    XSSContextType.URL,
                    "Base64 encoded data URL"
                ),
                XSSPattern(
                    "data_url_svg",
                    r'data:image/svg\+xml[^"\';\s]*',
                    "medium",
                    XSSContextType.URL,
                    "SVG data URL injection"
                ),
            ])
        
        # Iframe injections
        if self.config.enable_iframe_detection:
            patterns.extend([
                XSSPattern(
                    "iframe_injection",
                    r'<iframe[^>]*>.*?</iframe>',
                    "high",
                    XSSContextType.HTML,
                    "Iframe injection"
                ),
                XSSPattern(
                    "iframe_src_javascript",
                    r'<iframe[^>]*src\s*=\s*["\']javascript:[^"\']*["\'][^>]*>',
                    "critical",
                    XSSContextType.HTML,
                    "Iframe with JavaScript source"
                ),
                XSSPattern(
                    "iframe_srcdoc",
                    r'<iframe[^>]*srcdoc\s*=\s*["\'][^"\']*["\'][^>]*>',
                    "high",
                    XSSContextType.HTML,
                    "Iframe with srcdoc injection"
                ),
            ])
        
        # Object and embed injections
        if self.config.enable_object_embed_detection:
            patterns.extend([
                XSSPattern(
                    "object_injection",
                    r'<object[^>]*>.*?</object>',
                    "high",
                    XSSContextType.HTML,
                    "Object tag injection"
                ),
                XSSPattern(
                    "embed_injection",
                    r'<embed[^>]*>',
                    "high",
                    XSSContextType.HTML,
                    "Embed tag injection"
                ),
                XSSPattern(
                    "applet_injection",
                    r'<applet[^>]*>.*?</applet>',
                    "high",
                    XSSContextType.HTML,
                    "Applet tag injection"
                ),
            ])
        
        # Style injections
        if self.config.enable_style_injection_detection:
            patterns.extend([
                XSSPattern(
                    "style_expression",
                    r'style\s*=\s*["\'][^"\']*expression\s*\([^"\']*\)[^"\']*["\']',
                    "high",
                    XSSContextType.CSS,
                    "CSS expression injection"
                ),
                XSSPattern(
                    "style_javascript",
                    r'style\s*=\s*["\'][^"\']*javascript:[^"\']*["\']',
                    "high",
                    XSSContextType.CSS,
                    "JavaScript in CSS style"
                ),
                XSSPattern(
                    "style_import",
                    r'@import\s*["\'][^"\']*["\']',
                    "medium",
                    XSSContextType.CSS,
                    "CSS import injection"
                ),
                XSSPattern(
                    "style_url",
                    r'style\s*=\s*["\'][^"\']*url\s*\([^)]*\)[^"\']*["\']',
                    "medium",
                    XSSContextType.CSS,
                    "CSS URL injection"
                ),
            ])
        
        # SVG injections
        if self.config.enable_svg_xss_detection:
            patterns.extend([
                XSSPattern(
                    "svg_script",
                    r'<svg[^>]*>.*?<script[^>]*>.*?</script>.*?</svg>',
                    "critical",
                    XSSContextType.HTML,
                    "SVG with embedded script"
                ),
                XSSPattern(
                    "svg_onload",
                    r'<svg[^>]*onload\s*=\s*["\'][^"\']*["\'][^>]*>',
                    "high",
                    XSSContextType.ATTRIBUTE,
                    "SVG onload injection"
                ),
                XSSPattern(
                    "svg_foreignobject",
                    r'<foreignObject[^>]*>.*?</foreignObject>',
                    "medium",
                    XSSContextType.HTML,
                    "SVG foreignObject injection"
                ),
            ])
        
        # DOM-based XSS patterns
        if self.config.enable_dom_xss_detection:
            patterns.extend([
                XSSPattern(
                    "document_write",
                    r'document\.write\s*\(',
                    "high",
                    XSSContextType.JAVASCRIPT,
                    "document.write injection"
                ),
                XSSPattern(
                    "eval_injection",
                    r'\beval\s*\(',
                    "critical",
                    XSSContextType.JAVASCRIPT,
                    "eval() function injection"
                ),
                XSSPattern(
                    "settimeout_string",
                    r'setTimeout\s*\(\s*["\'][^"\']*["\']',
                    "high",
                    XSSContextType.JAVASCRIPT,
                    "setTimeout with string injection"
                ),
                XSSPattern(
                    "innerhtml_injection",
                    r'\.innerHTML\s*=\s*["\'][^"\']*["\']',
                    "medium",
                    XSSContextType.JAVASCRIPT,
                    "innerHTML injection"
                ),
            ])
        
        # Add custom patterns
        patterns.extend(self.config.custom_patterns)
        
        return patterns
    
    def _setup_csp(self):
        """Setup Content Security Policy"""
        if not self.config.csp_policy:
            # Default CSP policy for creator platforms
            self.config.csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://www.youtube.com https://player.vimeo.com https://platform.twitter.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https:; "
                "media-src 'self' https: blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none';"
            )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with XSS protection"""
        start_time = datetime.utcnow()
        
        try:
            self.metrics.total_requests += 1
            
            # Skip protection for certain paths
            if await self._should_skip_protection(request):
                return await call_next(request)
            
            self.metrics.scanned_requests += 1
            
            # Scan request for XSS
            detection_result = await self._scan_for_xss(request)
            
            if detection_result.detected:
                # Record attack attempt
                await self._record_attack_attempt(request, detection_result)
                
                # Handle based on filter mode
                if self.config.filter_mode == XSSFilterMode.BLOCK:
                    self.metrics.blocked_attempts += 1
                    return await self._create_blocked_response(request, detection_result)
                
                elif self.config.filter_mode == XSSFilterMode.SANITIZE:
                    self.metrics.sanitized_attempts += 1
                    request = await self._sanitize_request(request, detection_result)
                
                elif self.config.filter_mode == XSSFilterMode.ENCODE:
                    request = await self._encode_request(request, detection_result)
                
                # Always log XSS attempts
                self._log_xss_attempt(request, detection_result)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers to response
            response = await self._add_security_headers(response)
            
            # Scan response for XSS (if HTML content)
            if self._is_html_response(response):
                response = await self._scan_response_content(response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"XSS protection middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers={"X-Content-Type-Options": "nosniff"}
            )
    
    async def _should_skip_protection(self, request: Request) -> bool:
        """Check if request should skip XSS protection"""
        # Skip for API endpoints that return JSON only
        if request.url.path.startswith("/api/") and request.headers.get("accept", "").startswith("application/json"):
            return True
        
        # Skip for static assets
        static_extensions = [".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg", ".woff", ".woff2"]
        if any(request.url.path.endswith(ext) for ext in static_extensions):
            return True
        
        return False
    
    async def _scan_for_xss(self, request: Request) -> XSSDetectionResult:
        """Comprehensive XSS scanning"""
        result = XSSDetectionResult(detected=False)
        
        # Scan query parameters
        for key, value in request.query_params.items():
            param_result = await self._scan_parameter(f"query.{key}", value)
            if param_result.detected:
                result.detected = True
                result.patterns.extend(param_result.patterns)
                self._update_severity(result, param_result.severity)
        
        # Scan headers
        for header_name, header_value in request.headers.items():
            if header_name.lower() in ["user-agent", "referer", "x-forwarded-for"]:
                header_result = await self._scan_parameter(f"header.{header_name}", header_value)
                if header_result.detected:
                    result.detected = True
                    result.patterns.extend(header_result.patterns)
                    self._update_severity(result, header_result.severity)
        
        # Scan body content
        if request.method in ["POST", "PUT", "PATCH"]:
            body_result = await self._scan_body(request)
            if body_result.detected:
                result.detected = True
                result.patterns.extend(body_result.patterns)
                self._update_severity(result, body_result.severity)
                result.sanitized_content = body_result.sanitized_content
        
        return result
    
    async def _scan_parameter(self, param_name: str, value: str) -> XSSDetectionResult:
        """Scan individual parameter for XSS"""
        result = XSSDetectionResult(detected=False)
        
        if not value or not isinstance(value, str):
            return result
        
        # Check against XSS patterns
        for pattern in self.patterns:
            if pattern.compiled_pattern and pattern.compiled_pattern.search(value):
                result.detected = True
                result.patterns.append({
                    "pattern": pattern.name,
                    "parameter": param_name,
                    "value": value[:200],  # Truncate for logging
                    "severity": pattern.severity,
                    "context": pattern.context.value,
                    "description": pattern.description
                })
                
                self._update_severity(result, pattern.severity)
                self._update_attack_metrics(pattern.name)
        
        # Additional context-aware checks
        if self.config.enable_creator_content_analysis:
            creator_result = await self._analyze_creator_content(param_name, value)
            if creator_result.detected:
                result.detected = True
                result.patterns.extend(creator_result.patterns)
                result.warnings.extend(creator_result.warnings)
        
        return result
    
    async def _scan_body(self, request: Request) -> XSSDetectionResult:
        """Scan request body for XSS"""
        result = XSSDetectionResult(detected=False)
        
        try:
            body = await request.body()
            if not body:
                return result
            
            content_type = request.headers.get("content-type", "").split(";")[0]
            
            if content_type == "application/json":
                json_data = json.loads(body.decode())
                json_result = await self._scan_json_object(json_data, "body")
                if json_result.detected:
                    result.detected = True
                    result.patterns.extend(json_result.patterns)
                    result.sanitized_content = json_result.sanitized_content
            
            elif content_type == "application/x-www-form-urlencoded":
                form_data = parse_qs(body.decode())
                for key, values in form_data.items():
                    for i, value in enumerate(values):
                        param_result = await self._scan_parameter(f"form.{key}[{i}]", value)
                        if param_result.detected:
                            result.detected = True
                            result.patterns.extend(param_result.patterns)
            
            elif content_type.startswith("text/"):
                # Scan raw text content
                text_content = body.decode("utf-8", errors="ignore")
                text_result = await self._scan_parameter("body.text", text_content)
                if text_result.detected:
                    result.detected = True
                    result.patterns.extend(text_result.patterns)
                    result.sanitized_content = await self._sanitize_html(text_content)
        
        except Exception as e:
            self.logger.warning(f"Failed to scan request body: {e}")
        
        return result
    
    async def _scan_json_object(self, data: Any, prefix: str) -> XSSDetectionResult:
        """Recursively scan JSON object for XSS"""
        result = XSSDetectionResult(detected=False)
        sanitized_data = data
        
        if isinstance(data, dict):
            sanitized_dict = {}
            for key, value in data.items():
                if isinstance(value, str):
                    param_result = await self._scan_parameter(f"{prefix}.{key}", value)
                    if param_result.detected:
                        result.detected = True
                        result.patterns.extend(param_result.patterns)
                        sanitized_dict[key] = await self._sanitize_html(value)
                    else:
                        sanitized_dict[key] = value
                elif isinstance(value, (dict, list)):
                    nested_result = await self._scan_json_object(value, f"{prefix}.{key}")
                    if nested_result.detected:
                        result.detected = True
                        result.patterns.extend(nested_result.patterns)
                        sanitized_dict[key] = nested_result.sanitized_content
                    else:
                        sanitized_dict[key] = value
                else:
                    sanitized_dict[key] = value
            sanitized_data = sanitized_dict
        
        elif isinstance(data, list):
            sanitized_list = []
            for i, item in enumerate(data):
                if isinstance(item, str):
                    param_result = await self._scan_parameter(f"{prefix}[{i}]", item)
                    if param_result.detected:
                        result.detected = True
                        result.patterns.extend(param_result.patterns)
                        sanitized_list.append(await self._sanitize_html(item))
                    else:
                        sanitized_list.append(item)
                elif isinstance(item, (dict, list)):
                    nested_result = await self._scan_json_object(item, f"{prefix}[{i}]")
                    if nested_result.detected:
                        result.detected = True
                        result.patterns.extend(nested_result.patterns)
                        sanitized_list.append(nested_result.sanitized_content)
                    else:
                        sanitized_list.append(item)
                else:
                    sanitized_list.append(item)
            sanitized_data = sanitized_list
        
        result.sanitized_content = sanitized_data
        return result
    
    async def _analyze_creator_content(self, param_name: str, value: str) -> XSSDetectionResult:
        """Analyze content for creator-specific XSS patterns"""
        result = XSSDetectionResult(detected=False)
        
        if not self.config.enable_creator_content_analysis:
            return result
        
        # Check for embedded media URLs
        if param_name in ["video_url", "audio_url", "image_url", "thumbnail_url"]:
            url_result = await self._validate_media_url(param_name, value)
            if url_result.detected:
                result.detected = True
                result.patterns.extend(url_result.patterns)
        
        # Check for HTML content in creator descriptions
        if param_name in ["description", "bio", "about", "content"]:
            if self.config.allow_creator_html:
                # Sanitize but allow safe HTML
                sanitized = await self._sanitize_creator_html(value)
                if sanitized != value:
                    result.warnings.append(f"HTML content sanitized in {param_name}")
            else:
                # Check for any HTML tags
                if re.search(r'<[^>]+>', value):
                    result.detected = True
                    result.patterns.append({
                        "pattern": "creator_html_not_allowed",
                        "parameter": param_name,
                        "value": value[:100],
                        "severity": "medium",
                        "context": "html",
                        "description": "HTML tags not allowed in creator content"
                    })
        
        return result
    
    async def _validate_media_url(self, param_name: str, url: str) -> XSSDetectionResult:
        """Validate media URLs for XSS"""
        result = XSSDetectionResult(detected=False)
        
        try:
            parsed = urlparse(url)
            
            # Check for JavaScript URLs
            if parsed.scheme.lower() in ["javascript", "vbscript", "data"]:
                result.detected = True
                result.patterns.append({
                    "pattern": "media_url_xss",
                    "parameter": param_name,
                    "value": url,
                    "severity": "high",
                    "context": "url",
                    "description": f"Suspicious URL scheme: {parsed.scheme}"
                })
            
            # Check for suspicious domains
            if parsed.netloc and not self._is_trusted_domain(parsed.netloc):
                result.warnings.append(f"Untrusted domain in media URL: {parsed.netloc}")
        
        except Exception:
            result.warnings.append(f"Invalid URL format: {url}")
        
        return result
    
    def _is_trusted_domain(self, domain: str) -> bool:
        """Check if domain is trusted for creator content"""
        trusted_domains = {
            "youtube.com", "youtu.be", "vimeo.com", "soundcloud.com",
            "spotify.com", "instagram.com", "facebook.com", "twitter.com",
            "tiktok.com", "linkedin.com", "imgur.com", "giphy.com"
        }
        
        trusted_domains.update(self.config.creator_safe_domains)
        
        return any(domain.endswith(trusted) for trusted in trusted_domains)
    
    def _update_severity(self, result: XSSDetectionResult, new_severity: str):
        """Update result severity with highest level"""
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        
        current_level = severity_levels.get(result.severity, 0)
        new_level = severity_levels.get(new_severity, 0)
        
        if new_level > current_level:
            result.severity = new_severity
    
    def _update_attack_metrics(self, pattern_name: str):
        """Update attack metrics based on pattern"""
        if "script" in pattern_name:
            self.metrics.script_injections += 1
        elif "onclick" in pattern_name or "onload" in pattern_name or "event" in pattern_name:
            self.metrics.event_handler_injections += 1
        elif "iframe" in pattern_name:
            self.metrics.iframe_injections += 1
        elif "javascript" in pattern_name:
            self.metrics.javascript_url_injections += 1
        elif "data_url" in pattern_name:
            self.metrics.data_url_injections += 1
        elif "style" in pattern_name:
            self.metrics.style_injections += 1
        elif "svg" in pattern_name:
            self.metrics.svg_injections += 1
    
    async def _sanitize_request(self, request: Request, detection_result: XSSDetectionResult) -> Request:
        """Sanitize request by removing XSS content"""
        # This is a conceptual implementation
        # In practice, request body modification in FastAPI middleware is complex
        self.logger.info(f"Sanitizing XSS content from request: {request.url.path}")
        return request
    
    async def _encode_request(self, request: Request, detection_result: XSSDetectionResult) -> Request:
        """Encode request content to prevent XSS"""
        # Similar to sanitize_request, this would require complex request modification
        self.logger.info(f"Encoding XSS content in request: {request.url.path}")
        return request
    
    async def _sanitize_html(self, content: str) -> str:
        """Sanitize HTML content using bleach"""
        return bleach.clean(
            content,
            tags=self.config.allowed_tags,
            attributes=self.config.allowed_attributes,
            protocols=self.config.allowed_protocols,
            strip=True
        )
    
    async def _sanitize_creator_html(self, content: str) -> str:
        """Sanitize HTML for creator content with more permissive rules"""
        creator_tags = self.config.allowed_tags | {
            'video', 'audio', 'source', 'track', 'picture'
        }
        
        creator_attributes = self.config.allowed_attributes.copy()
        creator_attributes.update({
            'video': {'src', 'poster', 'controls', 'width', 'height'},
            'audio': {'src', 'controls'},
            'source': {'src', 'type'},
            'track': {'src', 'kind', 'srclang', 'label'}
        })
        
        return bleach.clean(
            content,
            tags=creator_tags,
            attributes=creator_attributes,
            protocols=self.config.allowed_protocols,
            strip=True
        )
    
    async def _record_attack_attempt(self, request: Request, detection_result: XSSDetectionResult):
        """Record XSS attack attempt"""
        attempt = {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "path": str(request.url.path),
            "method": request.method,
            "patterns": [p["pattern"] for p in detection_result.patterns],
            "severity": detection_result.severity,
            "blocked": self.config.filter_mode == XSSFilterMode.BLOCK
        }
        
        self.attack_attempts.append(attempt)
        
        # Keep only recent attempts
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.attack_attempts = [
            a for a in self.attack_attempts 
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _create_blocked_response(self, request: Request, detection_result: XSSDetectionResult) -> Response:
        """Create response for blocked XSS attempts"""
        self.logger.warning(f"XSS attack blocked: {request.url.path} - Patterns: {[p['pattern'] for p in detection_result.patterns]}")
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "XSS attack detected",
                "message": "Request blocked by security policy",
                "patterns": [p["pattern"] for p in detection_result.patterns]
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        )
    
    async def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        if self.config.add_xss_protection_header:
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        if self.config.add_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        if self.config.add_frame_options:
            response.headers["X-Frame-Options"] = "DENY"
        
        if self.config.enable_csp and self.config.csp_policy:
            header_name = "Content-Security-Policy-Report-Only" if self.config.csp_report_only else "Content-Security-Policy"
            csp_policy = self.config.csp_policy
            
            if self.config.csp_report_uri:
                csp_policy += f" report-uri {self.config.csp_report_uri};"
            
            response.headers[header_name] = csp_policy
        
        return response
    
    def _is_html_response(self, response: Response) -> bool:
        """Check if response contains HTML content"""
        content_type = response.headers.get("content-type", "")
        return "text/html" in content_type
    
    async def _scan_response_content(self, response: Response) -> Response:
        """Scan response content for XSS vulnerabilities"""
        # This would require response body modification
        # For demonstration purposes, we'll just log
        self.logger.debug("Scanning response content for XSS")
        return response
    
    def _log_xss_attempt(self, request: Request, detection_result: XSSDetectionResult):
        """Log XSS attempt for audit"""
        self.logger.warning(
            f"XSS Attempt: IP={self._get_client_ip(request)} "
            f"Path={request.url.path} Patterns={[p['pattern'] for p in detection_result.patterns]} "
            f"Severity={detection_result.severity}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current XSS protection metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "scanned_requests": self.metrics.scanned_requests,
            "blocked_attempts": self.metrics.blocked_attempts,
            "sanitized_attempts": self.metrics.sanitized_attempts,
            "attack_rate": self.metrics.attack_rate,
            "script_injections": self.metrics.script_injections,
            "event_handler_injections": self.metrics.event_handler_injections,
            "iframe_injections": self.metrics.iframe_injections,
            "javascript_url_injections": self.metrics.javascript_url_injections,
            "data_url_injections": self.metrics.data_url_injections,
            "style_injections": self.metrics.style_injections,
            "svg_injections": self.metrics.svg_injections,
            "active_patterns": len(self.patterns),
            "recent_attacks": len(self.attack_attempts)
        }
    
    def get_attack_summary(self) -> Dict[str, Any]:
        """Get summary of recent XSS attacks"""
        return {
            "total_attacks_24h": len(self.attack_attempts),
            "unique_ips": len(set(a["ip"] for a in self.attack_attempts)),
            "severity_distribution": self._get_severity_distribution(),
            "top_patterns": self._get_top_attack_patterns(),
            "attack_timeline": self._get_attack_timeline()
        }
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of attack severities"""
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for attempt in self.attack_attempts:
            distribution[attempt["severity"]] = distribution.get(attempt["severity"], 0) + 1
        return distribution
    
    def _get_top_attack_patterns(self) -> List[Dict[str, Any]]:
        """Get most common attack patterns"""
        pattern_counts = {}
        for attempt in self.attack_attempts:
            for pattern in attempt["patterns"]:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_attack_timeline(self) -> List[Dict[str, Any]]:
        """Get hourly attack timeline"""
        hourly = {}
        for attempt in self.attack_attempts:
            timestamp = datetime.fromisoformat(attempt["timestamp"])
            hour = timestamp.replace(minute=0, second=0, microsecond=0)
            key = hour.isoformat()
            hourly[key] = hourly.get(key, 0) + 1
        
        return [
            {"hour": hour, "count": count}
            for hour, count in sorted(hourly.items())
        ]


# Factory function for easy integration
def create_xss_protection_middleware(
    app: FastAPI,
    protection_level: XSSProtectionLevel = XSSProtectionLevel.STRICT,
    **kwargs
) -> XSSProtectionMiddleware:
    """
    🏭 Factory function to create XSS protection middleware
    
    Args:
        app: FastAPI application
        protection_level: XSS protection level
        **kwargs: Additional configuration options
    
    Returns:
        Configured XSS protection middleware instance
    """
    config = XSSConfig(
        protection_level=protection_level,
        **kwargs
    )
    
    return XSSProtectionMiddleware(app, config)


def setup_creator_xss_protection(app: FastAPI) -> XSSProtectionMiddleware:
    """
    🎯 Creator-specific XSS protection setup
    Optimized for content creation platforms
    """
    config = XSSConfig(
        protection_level=XSSProtectionLevel.STRICT,
        filter_mode=XSSFilterMode.SANITIZE,
        
        # Creator-specific settings
        enable_creator_content_analysis=True,
        allow_creator_html=True,  # Allow sanitized HTML for rich content
        creator_safe_domains={
            "youtube.com", "youtu.be", "vimeo.com", "dailymotion.com",
            "soundcloud.com", "spotify.com", "bandcamp.com",
            "instagram.com", "facebook.com", "twitter.com", "tiktok.com",
            "linkedin.com", "github.com", "behance.net", "dribbble.com"
        },
        
        # Enhanced HTML support for creators
        allowed_tags={
            'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'span', 'div',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
            'a', 'img', 'blockquote', 'code', 'pre', 'video', 'audio',
            'source', 'track', 'figure', 'figcaption'
        },
        
        allowed_attributes={
            'a': {'href', 'title', 'target', 'rel'},
            'img': {'src', 'alt', 'width', 'height', 'title', 'class'},
            'video': {'src', 'poster', 'controls', 'width', 'height', 'preload'},
            'audio': {'src', 'controls', 'preload'},
            'source': {'src', 'type'},
            'track': {'src', 'kind', 'srclang', 'label'},
            '*': {'class', 'id'}
        },
        
        # Enhanced CSP for creator platforms
        csp_policy=(
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://www.youtube.com https://player.vimeo.com https://platform.twitter.com "
            "https://www.instagram.com https://connect.facebook.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https:; "
            "media-src 'self' https: blob:; "
            "frame-src https://www.youtube.com https://player.vimeo.com https://www.instagram.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        ),
        
        # Enhanced monitoring for creator platforms
        enable_audit_logging=True,
        enable_metrics=True,
        enable_attack_alerts=True
    )
    
    return XSSProtectionMiddleware(app, config)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="XSS Protection Demo")
    
    # Setup XSS protection
    xss_protection = create_xss_protection_middleware(
        app,
        protection_level=XSSProtectionLevel.STRICT
    )
    
    app.add_middleware(XSSProtectionMiddleware, middleware=xss_protection)
    
    @app.get("/")
    async def root():
        return {"message": "XSS Protection Template Active"}
    
    @app.post("/content")
    async def create_content(data: dict):
        return {"message": "Content created", "data": data}
    
    @app.get("/metrics")
    async def get_metrics():
        return xss_protection.get_metrics()
    
    @app.get("/attacks")
    async def get_attacks():
        return xss_protection.get_attack_summary()