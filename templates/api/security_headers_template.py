#!/usr/bin/env python3
"""
⚡ Security Headers Template - Enterprise Security
🏗️ Architecture: iacherie Creator Economy Platform
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
from fastapi.responses import JSONResponse
import re
import base64
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
from dataclasses import dataclass, field
from enum import Enum

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + DevOps Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class SecurityLevel(str, Enum):
    """Security header enforcement levels"""
    PERMISSIVE = "permissive"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


class CSPDirective(str, Enum):
    """Content Security Policy directives"""
    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    FONT_SRC = "font-src"
    CONNECT_SRC = "connect-src"
    MEDIA_SRC = "media-src"
    OBJECT_SRC = "object-src"
    FRAME_SRC = "frame-src"
    FRAME_ANCESTORS = "frame-ancestors"
    BASE_URI = "base-uri"
    FORM_ACTION = "form-action"
    UPGRADE_INSECURE_REQUESTS = "upgrade-insecure-requests"
    BLOCK_ALL_MIXED_CONTENT = "block-all-mixed-content"


class HSTSMode(str, Enum):
    """HSTS enforcement modes"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    PRELOAD = "preload"


@dataclass
class CSPPolicy:
    """Content Security Policy configuration"""
    directives: Dict[CSPDirective, List[str]] = field(default_factory=dict)
    report_only: bool = False
    report_uri: Optional[str] = None
    nonce_enabled: bool = True
    
    def __post_init__(self):
        """Set default directives if not provided"""
        if not self.directives:
            self.directives = {
                CSPDirective.DEFAULT_SRC: ["'self'"],
                CSPDirective.SCRIPT_SRC: ["'self'"],
                CSPDirective.STYLE_SRC: ["'self'", "'unsafe-inline'"],
                CSPDirective.IMG_SRC: ["'self'", "data:", "https:"],
                CSPDirective.FONT_SRC: ["'self'"],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.MEDIA_SRC: ["'self'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.FRAME_SRC: ["'none'"],
                CSPDirective.FRAME_ANCESTORS: ["'none'"],
                CSPDirective.BASE_URI: ["'self'"],
                CSPDirective.FORM_ACTION: ["'self'"],
            }
    
    def to_string(self, nonce: Optional[str] = None) -> str:
        """Convert CSP policy to header string"""
        policy_parts = []
        
        for directive, sources in self.directives.items():
            if directive in [CSPDirective.UPGRADE_INSECURE_REQUESTS, CSPDirective.BLOCK_ALL_MIXED_CONTENT]:
                if sources:  # Only add if enabled
                    policy_parts.append(directive.value)
            else:
                sources_str = " ".join(sources)
                
                # Add nonce to script-src and style-src if enabled
                if (nonce and self.nonce_enabled and 
                    directive in [CSPDirective.SCRIPT_SRC, CSPDirective.STYLE_SRC]):
                    sources_str += f" 'nonce-{nonce}'"
                
                policy_parts.append(f"{directive.value} {sources_str}")
        
        # Add report-uri if specified
        if self.report_uri:
            policy_parts.append(f"report-uri {self.report_uri}")
        
        return "; ".join(policy_parts) + ";"


@dataclass
class HSTSConfig:
    """HTTP Strict Transport Security configuration"""
    enabled: bool = True
    max_age: int = 31536000  # 1 year
    include_subdomains: bool = True
    preload: bool = False
    mode: HSTSMode = HSTSMode.ENABLED
    
    def to_string(self) -> str:
        """Convert HSTS config to header string"""
        if not self.enabled:
            return ""
        
        parts = [f"max-age={self.max_age}"]
        
        if self.include_subdomains:
            parts.append("includeSubDomains")
        
        if self.preload and self.mode == HSTSMode.PRELOAD:
            parts.append("preload")
        
        return "; ".join(parts)


@dataclass
class SecurityHeadersConfig:
    """Enterprise security headers configuration"""
    # Security level
    security_level: SecurityLevel = SecurityLevel.STRICT
    
    # Content Security Policy
    csp_policy: Optional[CSPPolicy] = None
    enable_csp: bool = True
    
    # HTTP Strict Transport Security
    hsts_config: Optional[HSTSConfig] = None
    enable_hsts: bool = True
    
    # X-Frame-Options
    enable_frame_options: bool = True
    frame_options_value: str = "DENY"  # DENY, SAMEORIGIN, ALLOW-FROM uri
    
    # X-Content-Type-Options
    enable_content_type_options: bool = True
    
    # X-XSS-Protection (deprecated but still useful for older browsers)
    enable_xss_protection: bool = True
    xss_protection_value: str = "1; mode=block"
    
    # Referrer Policy
    enable_referrer_policy: bool = True
    referrer_policy_value: str = "strict-origin-when-cross-origin"
    
    # Permissions Policy (Feature Policy successor)
    enable_permissions_policy: bool = True
    permissions_policy: Dict[str, List[str]] = field(default_factory=dict)
    
    # Cross-Origin Embedder Policy
    enable_coep: bool = True
    coep_value: str = "require-corp"
    
    # Cross-Origin Opener Policy
    enable_coop: bool = True
    coop_value: str = "same-origin"
    
    # Cross-Origin Resource Policy
    enable_corp: bool = True
    corp_value: str = "same-origin"
    
    # Expect-CT (deprecated but useful for monitoring)
    enable_expect_ct: bool = False
    expect_ct_max_age: int = 86400
    expect_ct_enforce: bool = False
    expect_ct_report_uri: Optional[str] = None
    
    # Custom headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Creator-specific settings
    enable_creator_optimizations: bool = True
    creator_trusted_domains: Set[str] = field(default_factory=set)
    
    # Conditional headers based on request
    conditional_headers: bool = True
    
    # Security headers for specific content types
    api_only_headers: Dict[str, str] = field(default_factory=dict)
    html_only_headers: Dict[str, str] = field(default_factory=dict)
    
    # Monitoring and reporting
    enable_security_monitoring: bool = True
    enable_csp_reporting: bool = True
    
    def __post_init__(self):
        """Initialize default configurations"""
        if self.csp_policy is None:
            self.csp_policy = CSPPolicy()
        
        if self.hsts_config is None:
            self.hsts_config = HSTSConfig()
        
        if not self.permissions_policy:
            self.permissions_policy = {
                "camera": ["'none'"],
                "microphone": ["'none'"],
                "geolocation": ["'none'"],
                "gyroscope": ["'none'"],
                "magnetometer": ["'none'"],
                "payment": ["'none'"],
                "usb": ["'none'"],
            }
        
        # Set creator-specific trusted domains
        if self.enable_creator_optimizations and not self.creator_trusted_domains:
            self.creator_trusted_domains = {
                "youtube.com", "youtu.be", "vimeo.com", "dailymotion.com",
                "soundcloud.com", "spotify.com", "bandcamp.com",
                "instagram.com", "facebook.com", "twitter.com", "tiktok.com",
                "linkedin.com", "github.com", "behance.net", "dribbble.com",
                "imgur.com", "giphy.com", "unsplash.com"
            }


@dataclass
class SecurityMetrics:
    """Security headers metrics"""
    total_requests: int = 0
    headers_applied: int = 0
    csp_violations: int = 0
    hsts_violations: int = 0
    mixed_content_blocked: int = 0
    frame_blocking: int = 0
    content_type_sniffing_blocked: int = 0
    
    # Per-header metrics
    header_metrics: Dict[str, int] = field(default_factory=dict)
    
    @property
    def security_coverage(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.headers_applied / self.total_requests) * 100


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise Security Headers Middleware
    
    Features:
    - Comprehensive security headers suite
    - Content Security Policy with nonce support
    - HTTP Strict Transport Security
    - Creator platform optimizations
    - Conditional header application
    - Real-time security monitoring
    - CSP violation reporting
    - Adaptive security policies
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[SecurityHeadersConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or SecurityHeadersConfig()
        self.logger = logger or self._setup_logger()
        
        # Metrics
        self.metrics = SecurityMetrics()
        
        # Nonce generation for CSP
        self.nonce_store: Dict[str, str] = {}
        
        # Setup security level-specific configurations
        self._configure_security_level()
        
        # Setup creator optimizations
        if self.config.enable_creator_optimizations:
            self._setup_creator_optimizations()
        
        self.logger.info(f"Security Headers initialized with level: {self.config.security_level}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup security audit logger"""
        logger = logging.getLogger("security_headers")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _configure_security_level(self):
        """Configure headers based on security level"""
        if self.config.security_level == SecurityLevel.PERMISSIVE:
            self.config.frame_options_value = "SAMEORIGIN"
            self.config.coep_value = "unsafe-none"
            self.config.coop_value = "unsafe-none"
            self.config.corp_value = "cross-origin"
            
        elif self.config.security_level == SecurityLevel.STANDARD:
            self.config.frame_options_value = "SAMEORIGIN"
            self.config.coep_value = "credentialless"
            
        elif self.config.security_level == SecurityLevel.STRICT:
            self.config.frame_options_value = "DENY"
            self.config.coep_value = "require-corp"
            self.config.coop_value = "same-origin"
            
        elif self.config.security_level == SecurityLevel.PARANOID:
            self.config.frame_options_value = "DENY"
            self.config.coep_value = "require-corp"
            self.config.coop_value = "same-origin-allow-popups"
            self.config.enable_expect_ct = True
            self.config.expect_ct_enforce = True
    
    def _setup_creator_optimizations(self):
        """Setup creator-specific security optimizations"""
        if not self.config.csp_policy:
            self.config.csp_policy = CSPPolicy()
        
        # Add creator-friendly CSP directives
        creator_domains = ["https://" + domain for domain in self.config.creator_trusted_domains]
        
        # Allow embedding of creator content
        self.config.csp_policy.directives[CSPDirective.FRAME_SRC] = [
            "'self'",
            "https://www.youtube.com",
            "https://player.vimeo.com",
            "https://www.instagram.com",
            "https://platform.twitter.com"
        ]
        
        # Allow loading images from creator platforms
        self.config.csp_policy.directives[CSPDirective.IMG_SRC].extend([
            "https://*.youtube.com",
            "https://*.instagram.com",
            "https://*.twitter.com",
            "https://*.tiktok.com"
        ])
        
        # Allow connecting to creator APIs
        self.config.csp_policy.directives[CSPDirective.CONNECT_SRC].extend(creator_domains)
        
        # Adjust permissions policy for creator features
        self.config.permissions_policy.update({
            "camera": ["'self'"],  # Allow camera for content creation
            "microphone": ["'self'"],  # Allow microphone for content creation
            "fullscreen": ["'self'"] + creator_domains,
            "autoplay": ["'self'"] + creator_domains,
        })
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with security headers"""
        start_time = datetime.utcnow()
        
        try:
            self.metrics.total_requests += 1
            
            # Generate CSP nonce if needed
            nonce = None
            if self.config.enable_csp and self.config.csp_policy.nonce_enabled:
                nonce = self._generate_nonce()
                self.nonce_store[id(request)] = nonce
            
            # Process request
            response = await call_next(request)
            
            # Apply security headers
            response = await self._apply_security_headers(response, request, nonce)
            
            # Update metrics
            self.metrics.headers_applied += 1
            
            # Clean up nonce
            if nonce and id(request) in self.nonce_store:
                del self.nonce_store[id(request)]
            
            return response
            
        except Exception as e:
            self.logger.error(f"Security headers middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers={"X-Content-Type-Options": "nosniff"}
            )
    
    def _generate_nonce(self) -> str:
        """Generate cryptographically secure nonce for CSP"""
        return base64.b64encode(secrets.token_bytes(16)).decode('ascii')
    
    async def _apply_security_headers(
        self, 
        response: Response, 
        request: Request, 
        nonce: Optional[str]
    ) -> Response:
        """Apply comprehensive security headers"""
        content_type = response.headers.get("content-type", "")
        is_html = "text/html" in content_type
        is_api = request.url.path.startswith("/api/")
        
        # Content Security Policy
        if self.config.enable_csp:
            csp_header = self._build_csp_header(nonce, is_html, is_api)
            if csp_header:
                header_name = (
                    "Content-Security-Policy-Report-Only" 
                    if self.config.csp_policy.report_only 
                    else "Content-Security-Policy"
                )
                response.headers[header_name] = csp_header
                self._update_header_metric("CSP")
        
        # HTTP Strict Transport Security
        if self.config.enable_hsts and request.url.scheme == "https":
            hsts_header = self.config.hsts_config.to_string()
            if hsts_header:
                response.headers["Strict-Transport-Security"] = hsts_header
                self._update_header_metric("HSTS")
        
        # X-Frame-Options
        if self.config.enable_frame_options:
            response.headers["X-Frame-Options"] = self.config.frame_options_value
            self._update_header_metric("X-Frame-Options")
        
        # X-Content-Type-Options
        if self.config.enable_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
            self._update_header_metric("X-Content-Type-Options")
        
        # X-XSS-Protection (for older browsers)
        if self.config.enable_xss_protection:
            response.headers["X-XSS-Protection"] = self.config.xss_protection_value
            self._update_header_metric("X-XSS-Protection")
        
        # Referrer Policy
        if self.config.enable_referrer_policy:
            response.headers["Referrer-Policy"] = self.config.referrer_policy_value
            self._update_header_metric("Referrer-Policy")
        
        # Permissions Policy
        if self.config.enable_permissions_policy:
            permissions_header = self._build_permissions_policy_header()
            if permissions_header:
                response.headers["Permissions-Policy"] = permissions_header
                self._update_header_metric("Permissions-Policy")
        
        # Cross-Origin Embedder Policy
        if self.config.enable_coep:
            response.headers["Cross-Origin-Embedder-Policy"] = self.config.coep_value
            self._update_header_metric("COEP")
        
        # Cross-Origin Opener Policy
        if self.config.enable_coop:
            response.headers["Cross-Origin-Opener-Policy"] = self.config.coop_value
            self._update_header_metric("COOP")
        
        # Cross-Origin Resource Policy
        if self.config.enable_corp:
            response.headers["Cross-Origin-Resource-Policy"] = self.config.corp_value
            self._update_header_metric("CORP")
        
        # Expect-CT (if enabled)
        if self.config.enable_expect_ct:
            expect_ct_header = self._build_expect_ct_header()
            if expect_ct_header:
                response.headers["Expect-CT"] = expect_ct_header
                self._update_header_metric("Expect-CT")
        
        # Custom headers
        for header_name, header_value in self.config.custom_headers.items():
            response.headers[header_name] = header_value
            self._update_header_metric(f"Custom-{header_name}")
        
        # Conditional headers
        if self.config.conditional_headers:
            if is_api and self.config.api_only_headers:
                for header_name, header_value in self.config.api_only_headers.items():
                    response.headers[header_name] = header_value
            
            if is_html and self.config.html_only_headers:
                for header_name, header_value in self.config.html_only_headers.items():
                    response.headers[header_name] = header_value
        
        return response
    
    def _build_csp_header(self, nonce: Optional[str], is_html: bool, is_api: bool) -> str:
        """Build Content Security Policy header"""
        if not self.config.csp_policy:
            return ""
        
        # Adjust CSP based on content type
        if is_api:
            # Simplified CSP for API endpoints
            api_policy = CSPPolicy(
                directives={
                    CSPDirective.DEFAULT_SRC: ["'none'"],
                    CSPDirective.FRAME_ANCESTORS: ["'none'"],
                },
                nonce_enabled=False
            )
            return api_policy.to_string()
        
        # Use full CSP for HTML content
        return self.config.csp_policy.to_string(nonce)
    
    def _build_permissions_policy_header(self) -> str:
        """Build Permissions Policy header"""
        if not self.config.permissions_policy:
            return ""
        
        policy_parts = []
        for feature, allowlist in self.config.permissions_policy.items():
            allowlist_str = " ".join(allowlist)
            policy_parts.append(f"{feature}=({allowlist_str})")
        
        return ", ".join(policy_parts)
    
    def _build_expect_ct_header(self) -> str:
        """Build Expect-CT header"""
        parts = [f"max-age={self.config.expect_ct_max_age}"]
        
        if self.config.expect_ct_enforce:
            parts.append("enforce")
        
        if self.config.expect_ct_report_uri:
            parts.append(f'report-uri="{self.config.expect_ct_report_uri}"')
        
        return ", ".join(parts)
    
    def _update_header_metric(self, header_name: str):
        """Update metrics for applied header"""
        if header_name not in self.metrics.header_metrics:
            self.metrics.header_metrics[header_name] = 0
        self.metrics.header_metrics[header_name] += 1
    
    def get_nonce(self, request: Request) -> Optional[str]:
        """Get CSP nonce for current request"""
        return self.nonce_store.get(id(request))
    
    def report_csp_violation(self, violation_data: Dict[str, Any]):
        """Report CSP violation"""
        self.metrics.csp_violations += 1
        
        self.logger.warning(
            f"CSP Violation: {violation_data.get('blocked-uri', 'unknown')} "
            f"violated {violation_data.get('violated-directive', 'unknown')}"
        )
        
        # Send to monitoring system if enabled
        if self.config.enable_security_monitoring:
            self._send_security_alert("CSP_VIOLATION", violation_data)
    
    def report_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Report general security event"""
        self.logger.info(f"Security Event: {event_type} - {event_data}")
        
        # Update relevant metrics
        if event_type == "MIXED_CONTENT_BLOCKED":
            self.metrics.mixed_content_blocked += 1
        elif event_type == "FRAME_BLOCKED":
            self.metrics.frame_blocking += 1
        elif event_type == "CONTENT_TYPE_SNIFFING_BLOCKED":
            self.metrics.content_type_sniffing_blocked += 1
        
        if self.config.enable_security_monitoring:
            self._send_security_alert(event_type, event_data)
    
    def _send_security_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """Send security alert to monitoring system"""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": alert_type,
            "data": alert_data,
            "source": "security_headers_middleware"
        }
        
        # TODO: Implement your alerting mechanism
        self.logger.error(f"Security Alert: {alert}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current security metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "headers_applied": self.metrics.headers_applied,
            "security_coverage": self.metrics.security_coverage,
            "csp_violations": self.metrics.csp_violations,
            "hsts_violations": self.metrics.hsts_violations,
            "mixed_content_blocked": self.metrics.mixed_content_blocked,
            "frame_blocking": self.metrics.frame_blocking,
            "content_type_sniffing_blocked": self.metrics.content_type_sniffing_blocked,
            "header_metrics": self.metrics.header_metrics,
            "security_level": self.config.security_level.value,
            "csp_enabled": self.config.enable_csp,
            "hsts_enabled": self.config.enable_hsts
        }
    
    def get_security_policy_summary(self) -> Dict[str, Any]:
        """Get summary of current security policies"""
        return {
            "security_level": self.config.security_level.value,
            "csp_policy": {
                "enabled": self.config.enable_csp,
                "report_only": self.config.csp_policy.report_only if self.config.csp_policy else False,
                "nonce_enabled": self.config.csp_policy.nonce_enabled if self.config.csp_policy else False,
                "directive_count": len(self.config.csp_policy.directives) if self.config.csp_policy else 0
            },
            "hsts_policy": {
                "enabled": self.config.enable_hsts,
                "max_age": self.config.hsts_config.max_age if self.config.hsts_config else 0,
                "include_subdomains": self.config.hsts_config.include_subdomains if self.config.hsts_config else False,
                "preload": self.config.hsts_config.preload if self.config.hsts_config else False
            },
            "frame_options": {
                "enabled": self.config.enable_frame_options,
                "value": self.config.frame_options_value
            },
            "permissions_policy": {
                "enabled": self.config.enable_permissions_policy,
                "feature_count": len(self.config.permissions_policy)
            },
            "cross_origin_policies": {
                "coep_enabled": self.config.enable_coep,
                "coop_enabled": self.config.enable_coop,
                "corp_enabled": self.config.enable_corp,
                "coep_value": self.config.coep_value,
                "coop_value": self.config.coop_value,
                "corp_value": self.config.corp_value
            },
            "creator_optimizations": self.config.enable_creator_optimizations
        }
    
    def update_csp_policy(self, new_policy: CSPPolicy):
        """Update CSP policy at runtime"""
        self.config.csp_policy = new_policy
        self.logger.info("CSP policy updated")
    
    def add_trusted_domain(self, domain: str, directive: CSPDirective):
        """Add trusted domain to CSP directive"""
        if not self.config.csp_policy:
            self.config.csp_policy = CSPPolicy()
        
        if directive not in self.config.csp_policy.directives:
            self.config.csp_policy.directives[directive] = []
        
        domain_url = f"https://{domain}" if not domain.startswith("http") else domain
        if domain_url not in self.config.csp_policy.directives[directive]:
            self.config.csp_policy.directives[directive].append(domain_url)
            self.logger.info(f"Added trusted domain {domain_url} to {directive.value}")
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = SecurityMetrics()
        self.logger.info("Security headers metrics reset")


# Factory function for easy integration
def create_security_headers_middleware(
    app: FastAPI,
    security_level: SecurityLevel = SecurityLevel.STRICT,
    **kwargs
) -> SecurityHeadersMiddleware:
    """
    🏭 Factory function to create security headers middleware
    
    Args:
        app: FastAPI application
        security_level: Security enforcement level
        **kwargs: Additional configuration options
    
    Returns:
        Configured security headers middleware instance
    """
    config = SecurityHeadersConfig(
        security_level=security_level,
        **kwargs
    )
    
    return SecurityHeadersMiddleware(app, config)


def setup_creator_security_headers(app: FastAPI) -> SecurityHeadersMiddleware:
    """
    🎯 Creator-specific security headers setup
    Optimized for content creation platforms
    """
    # Creator-optimized CSP policy
    creator_csp = CSPPolicy(
        directives={
            CSPDirective.DEFAULT_SRC: ["'self'"],
            CSPDirective.SCRIPT_SRC: [
                "'self'", "'unsafe-inline'", "'unsafe-eval'",
                "https://www.youtube.com", "https://s.ytimg.com",
                "https://platform.twitter.com", "https://connect.facebook.net",
                "https://www.instagram.com", "https://player.vimeo.com"
            ],
            CSPDirective.STYLE_SRC: [
                "'self'", "'unsafe-inline'",
                "https://fonts.googleapis.com", "https://use.fontawesome.com"
            ],
            CSPDirective.IMG_SRC: [
                "'self'", "data:", "blob:", "https:",
                "https://*.youtube.com", "https://*.ytimg.com",
                "https://*.instagram.com", "https://*.twitter.com",
                "https://*.tiktok.com", "https://*.giphy.com"
            ],
            CSPDirective.FONT_SRC: [
                "'self'", "https://fonts.gstatic.com", "https://use.fontawesome.com"
            ],
            CSPDirective.CONNECT_SRC: [
                "'self'", "https:", "wss:",
                "https://api.youtube.com", "https://api.instagram.com",
                "https://api.twitter.com", "https://api.tiktok.com"
            ],
            CSPDirective.MEDIA_SRC: [
                "'self'", "blob:", "https:",
                "https://*.youtube.com", "https://*.vimeo.com",
                "https://*.soundcloud.com", "https://*.spotify.com"
            ],
            CSPDirective.FRAME_SRC: [
                "'self'",
                "https://www.youtube.com", "https://player.vimeo.com",
                "https://www.instagram.com", "https://platform.twitter.com",
                "https://open.spotify.com", "https://w.soundcloud.com"
            ],
            CSPDirective.OBJECT_SRC: ["'none'"],
            CSPDirective.FRAME_ANCESTORS: ["'none'"],
            CSPDirective.BASE_URI: ["'self'"],
            CSPDirective.FORM_ACTION: ["'self'"],
            CSPDirective.UPGRADE_INSECURE_REQUESTS: [""],
        },
        nonce_enabled=True,
        report_uri="/api/v1/security/csp-report"
    )
    
    # Creator-friendly permissions policy
    creator_permissions = {
        "camera": ["'self'"],
        "microphone": ["'self'"],
        "geolocation": ["'none'"],
        "gyroscope": ["'none'"],
        "magnetometer": ["'none'"],
        "payment": ["'self'"],
        "usb": ["'none'"],
        "fullscreen": [
            "'self'", "https://www.youtube.com", "https://player.vimeo.com",
            "https://open.spotify.com"
        ],
        "autoplay": [
            "'self'", "https://www.youtube.com", "https://player.vimeo.com",
            "https://w.soundcloud.com", "https://open.spotify.com"
        ],
        "picture-in-picture": [
            "'self'", "https://www.youtube.com", "https://player.vimeo.com"
        ]
    }
    
    config = SecurityHeadersConfig(
        security_level=SecurityLevel.STANDARD,  # Balanced for creator needs
        
        # CSP configuration
        csp_policy=creator_csp,
        enable_csp=True,
        
        # HSTS configuration
        hsts_config=HSTSConfig(
            enabled=True,
            max_age=31536000,  # 1 year
            include_subdomains=True,
            preload=False  # Don't force preload for creator domains
        ),
        
        # Frame options - allow same origin for embed functionality
        frame_options_value="SAMEORIGIN",
        
        # Permissions policy
        permissions_policy=creator_permissions,
        
        # Cross-origin policies - more permissive for creator content
        coep_value="credentialless",  # Allow cross-origin resources
        coop_value="same-origin-allow-popups",  # Allow social media popups
        corp_value="cross-origin",  # Allow cross-origin resource sharing
        
        # Creator optimizations
        enable_creator_optimizations=True,
        creator_trusted_domains={
            "youtube.com", "youtu.be", "vimeo.com", "dailymotion.com",
            "soundcloud.com", "spotify.com", "bandcamp.com",
            "instagram.com", "facebook.com", "twitter.com", "tiktok.com",
            "linkedin.com", "github.com", "behance.net", "dribbble.com",
            "imgur.com", "giphy.com", "unsplash.com", "pexels.com"
        },
        
        # Custom headers for creators
        custom_headers={
            "X-Creator-Platform": "iacherie",
            "X-Content-Creator-Friendly": "true"
        },
        
        # Conditional headers
        api_only_headers={
            "X-API-Security-Level": "creator-optimized"
        },
        
        # Enhanced monitoring for creator security
        enable_security_monitoring=True,
        enable_csp_reporting=True
    )
    
    return SecurityHeadersMiddleware(app, config)


# CSP reporting endpoint helper
def create_csp_report_endpoint(app: FastAPI, security_middleware: SecurityHeadersMiddleware):
    """
    🛡️ Create CSP violation reporting endpoint
    """
    
    @app.post("/api/v1/security/csp-report")
    async def csp_report(request: Request):
        """Handle CSP violation reports"""
        try:
            body = await request.body()
            if body:
                report_data = await request.json()
                csp_report_data = report_data.get("csp-report", {})
                security_middleware.report_csp_violation(csp_report_data)
            
            return {"status": "received"}
        except Exception as e:
            security_middleware.logger.error(f"CSP report processing error: {e}")
            return {"status": "error"}


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="Security Headers Demo")
    
    # Setup security headers
    security_headers = create_security_headers_middleware(
        app,
        security_level=SecurityLevel.STRICT
    )
    
    app.add_middleware(SecurityHeadersMiddleware, middleware=security_headers)
    
    # Add CSP reporting endpoint
    create_csp_report_endpoint(app, security_headers)
    
    @app.get("/")
    async def root():
        return {"message": "Security Headers Template Active"}
    
    @app.get("/api/data")
    async def get_data():
        return {"data": "secure API response"}
    
    @app.get("/metrics")
    async def get_metrics():
        return security_headers.get_metrics()
    
    @app.get("/security-policy")
    async def get_security_policy():
        return security_headers.get_security_policy_summary()