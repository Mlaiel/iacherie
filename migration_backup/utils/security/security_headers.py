"""
Security Headers - Security Utilities Level 2
============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade security headers management for Ainflue creator economy platform.
CSP, HSTS, and advanced header security with < 1ms operations.

Performance: < 1ms header operations
Standards: OWASP, web security headers, creator economy protection
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
import secrets
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class HeaderType(Enum):
    """Security header types."""
    CSP = "content_security_policy"
    HSTS = "strict_transport_security"
    REFERRER_POLICY = "referrer_policy"
    X_FRAME_OPTIONS = "x_frame_options"
    X_CONTENT_TYPE_OPTIONS = "x_content_type_options"
    X_XSS_PROTECTION = "x_xss_protection"
    PERMISSIONS_POLICY = "permissions_policy"
    CROSS_ORIGIN_EMBEDDER_POLICY = "cross_origin_embedder_policy"
    CROSS_ORIGIN_OPENER_POLICY = "cross_origin_opener_policy"
    CROSS_ORIGIN_RESOURCE_POLICY = "cross_origin_resource_policy"

class SecurityLevel(Enum):
    """Security levels for header configuration."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CREATOR_FOCUSED = "creator_focused"

@dataclass
class SecurityHeader:
    """Security header definition."""
    header_type: HeaderType
    name: str
    value: str
    description: str
    security_level: SecurityLevel
    creator_specific: bool = False
    nonce_required: bool = False
    dynamic_value: bool = False

@dataclass
class CSPDirective:
    """Content Security Policy directive."""
    directive: str
    sources: List[str]
    nonce_required: bool = False
    hash_required: bool = False
    creator_content_allowed: bool = False

@dataclass
class HeaderValidationResult:
    """Header validation result."""
    success: bool
    header_name: str
    is_secure: bool
    security_score: float
    vulnerabilities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0

class SecurityHeaders:
    """
    Enterprise-grade security headers management for creator economy platform.
    
    Features:
    - Content Security Policy (CSP) implementation
    - HTTP Strict Transport Security (HSTS) configuration
    - Comprehensive security header suite
    - Creator-specific header policies
    - Performance: < 1ms header operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security headers with enterprise configuration."""
        self.config = config or {}
        
        # Configuration
        self.security_level = SecurityLevel(self.config.get("security_level", "standard"))
        self.creator_content_domains = self.config.get("creator_content_domains", [])
        self.cdn_domains = self.config.get("cdn_domains", [])
        self.enable_nonce = self.config.get("enable_nonce", True)
        
        # Security headers storage
        self.security_headers: Dict[str, SecurityHeader] = {}
        self.csp_policies: Dict[str, List[CSPDirective]] = {}
        self.nonce_cache: Dict[str, str] = {}
        
        # Initialize default headers
        self._initialize_default_headers()
        self._initialize_csp_policies()
        
        logger.info("SecurityHeaders initialized with enterprise configuration")

    def _initialize_default_headers(self) -> None:
        """Initialize default security headers."""
        headers = [
            SecurityHeader(
                header_type=HeaderType.HSTS,
                name="Strict-Transport-Security",
                value="max-age=31536000; includeSubDomains; preload",
                description="Enforce HTTPS connections",
                security_level=SecurityLevel.STANDARD
            ),
            SecurityHeader(
                header_type=HeaderType.X_FRAME_OPTIONS,
                name="X-Frame-Options",
                value="DENY",
                description="Prevent clickjacking attacks",
                security_level=SecurityLevel.BASIC
            ),
            SecurityHeader(
                header_type=HeaderType.X_CONTENT_TYPE_OPTIONS,
                name="X-Content-Type-Options",
                value="nosniff",
                description="Prevent MIME type sniffing",
                security_level=SecurityLevel.BASIC
            ),
            SecurityHeader(
                header_type=HeaderType.X_XSS_PROTECTION,
                name="X-XSS-Protection",
                value="1; mode=block",
                description="Enable XSS protection",
                security_level=SecurityLevel.BASIC
            ),
            SecurityHeader(
                header_type=HeaderType.REFERRER_POLICY,
                name="Referrer-Policy",
                value="strict-origin-when-cross-origin",
                description="Control referrer information",
                security_level=SecurityLevel.STANDARD
            ),
            SecurityHeader(
                header_type=HeaderType.PERMISSIONS_POLICY,
                name="Permissions-Policy",
                value="geolocation=(), microphone=(), camera=()",
                description="Control browser feature permissions",
                security_level=SecurityLevel.STANDARD,
                creator_specific=True
            ),
            SecurityHeader(
                header_type=HeaderType.CROSS_ORIGIN_EMBEDDER_POLICY,
                name="Cross-Origin-Embedder-Policy",
                value="require-corp",
                description="Isolate cross-origin resources",
                security_level=SecurityLevel.STRICT
            ),
            SecurityHeader(
                header_type=HeaderType.CROSS_ORIGIN_OPENER_POLICY,
                name="Cross-Origin-Opener-Policy",
                value="same-origin",
                description="Isolate browsing context group",
                security_level=SecurityLevel.STRICT
            ),
            SecurityHeader(
                header_type=HeaderType.CROSS_ORIGIN_RESOURCE_POLICY,
                name="Cross-Origin-Resource-Policy",
                value="cross-origin",
                description="Control cross-origin resource sharing",
                security_level=SecurityLevel.STANDARD,
                creator_specific=True
            )
        ]
        
        for header in headers:
            self.security_headers[header.name] = header

    def _initialize_csp_policies(self) -> None:
        """Initialize Content Security Policy directives."""
        # Basic CSP policy
        basic_csp = [
            CSPDirective("default-src", ["'self'"]),
            CSPDirective("script-src", ["'self'", "'unsafe-inline'"]),
            CSPDirective("style-src", ["'self'", "'unsafe-inline'"]),
            CSPDirective("img-src", ["'self'", "data:", "https:"]),
            CSPDirective("font-src", ["'self'", "https:"]),
            CSPDirective("connect-src", ["'self'"])
        ]
        
        # Creator-focused CSP policy
        creator_csp = [
            CSPDirective("default-src", ["'self'"]),
            CSPDirective("script-src", ["'self'"], nonce_required=True),
            CSPDirective("style-src", ["'self'"], nonce_required=True),
            CSPDirective("img-src", ["'self'", "data:", "https:"], creator_content_allowed=True),
            CSPDirective("media-src", ["'self'", "blob:"], creator_content_allowed=True),
            CSPDirective("font-src", ["'self'", "https:"]),
            CSPDirective("connect-src", ["'self'", "https:"]),
            CSPDirective("frame-src", ["'none'"]),
            CSPDirective("object-src", ["'none'"]),
            CSPDirective("base-uri", ["'self'"]),
            CSPDirective("form-action", ["'self'"]),
            CSPDirective("worker-src", ["'self'", "blob:"])
        ]
        
        # Strict CSP policy
        strict_csp = [
            CSPDirective("default-src", ["'none'"]),
            CSPDirective("script-src", ["'self'"], nonce_required=True, hash_required=True),
            CSPDirective("style-src", ["'self'"], nonce_required=True, hash_required=True),
            CSPDirective("img-src", ["'self'", "data:"]),
            CSPDirective("font-src", ["'self'"]),
            CSPDirective("connect-src", ["'self'"]),
            CSPDirective("frame-src", ["'none'"]),
            CSPDirective("object-src", ["'none'"]),
            CSPDirective("base-uri", ["'none'"]),
            CSPDirective("form-action", ["'self'"]),
            CSPDirective("frame-ancestors", ["'none'"]),
            CSPDirective("worker-src", ["'none'"])
        ]
        
        self.csp_policies["basic"] = basic_csp
        self.csp_policies["creator_focused"] = creator_csp
        self.csp_policies["strict"] = strict_csp

    async def implement_csp_policies(self, policy_type: str = "creator_focused", 
                                   custom_directives: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """
        Implement Content Security Policy with creator-specific directives.
        
        Args:
            policy_type: Type of CSP policy to implement
            custom_directives: Custom CSP directives
            
        Returns:
            CSP implementation results
        """
        start_time = time.perf_counter()
        
        try:
            # Get base policy
            base_policy = self.csp_policies.get(policy_type, self.csp_policies["creator_focused"])
            
            # Apply custom directives
            if custom_directives:
                for directive_name, sources in custom_directives.items():
                    # Find existing directive or create new one
                    existing_directive = next(
                        (d for d in base_policy if d.directive == directive_name), None
                    )
                    if existing_directive:
                        existing_directive.sources.extend(sources)
                    else:
                        base_policy.append(CSPDirective(directive_name, sources))
            
            # Add creator content domains
            if self.creator_content_domains:
                for directive in base_policy:
                    if directive.creator_content_allowed:
                        directive.sources.extend(self.creator_content_domains)
            
            # Add CDN domains
            if self.cdn_domains:
                for directive in base_policy:
                    if directive.directive in ["img-src", "media-src", "font-src"]:
                        directive.sources.extend(self.cdn_domains)
            
            # Generate nonces if required
            nonces = {}
            if self.enable_nonce:
                for directive in base_policy:
                    if directive.nonce_required:
                        nonce = self._generate_nonce()
                        nonces[directive.directive] = nonce
                        directive.sources.append(f"'nonce-{nonce}'")
            
            # Build CSP header value
            csp_value = self._build_csp_header(base_policy)
            
            # Create CSP header
            csp_header = SecurityHeader(
                header_type=HeaderType.CSP,
                name="Content-Security-Policy",
                value=csp_value,
                description="Content Security Policy for creator platform",
                security_level=SecurityLevel.CREATOR_FOCUSED,
                creator_specific=True,
                nonce_required=bool(nonces),
                dynamic_value=True
            )
            
            self.security_headers["Content-Security-Policy"] = csp_header
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"CSP policy implemented in {execution_time:.2f}ms")
            
            return {
                "success": True,
                "implementation_time_ms": execution_time,
                "policy_type": policy_type,
                "csp_header": csp_value,
                "nonces": nonces,
                "directives_count": len(base_policy)
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"CSP policy implementation failed in {execution_time:.2f}ms: {str(e)}")
            return {"success": False, "error": str(e)}

    def _build_csp_header(self, directives: List[CSPDirective]) -> str:
        """Build CSP header value from directives."""
        csp_parts = []
        
        for directive in directives:
            sources_str = " ".join(directive.sources)
            csp_parts.append(f"{directive.directive} {sources_str}")
        
        return "; ".join(csp_parts)

    def _generate_nonce(self) -> str:
        """Generate cryptographically secure nonce."""
        nonce_bytes = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_bytes).decode('utf-8')
        
        # Cache nonce with timestamp
        self.nonce_cache[nonce] = datetime.now(timezone.utc).isoformat()
        
        return nonce

    async def configure_hsts_headers(self, max_age: int = 31536000, 
                                   include_subdomains: bool = True,
                                   preload: bool = True) -> Dict[str, Any]:
        """
        Configure HTTP Strict Transport Security headers.
        
        Args:
            max_age: HSTS max age in seconds
            include_subdomains: Include subdomains in HSTS
            preload: Enable HSTS preload
            
        Returns:
            HSTS configuration results
        """
        start_time = time.perf_counter()
        
        try:
            # Build HSTS value
            hsts_parts = [f"max-age={max_age}"]
            
            if include_subdomains:
                hsts_parts.append("includeSubDomains")
            
            if preload:
                hsts_parts.append("preload")
            
            hsts_value = "; ".join(hsts_parts)
            
            # Update HSTS header
            hsts_header = SecurityHeader(
                header_type=HeaderType.HSTS,
                name="Strict-Transport-Security",
                value=hsts_value,
                description="HTTP Strict Transport Security configuration",
                security_level=SecurityLevel.STANDARD
            )
            
            self.security_headers["Strict-Transport-Security"] = hsts_header
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"HSTS headers configured in {execution_time:.2f}ms")
            
            return {
                "success": True,
                "configuration_time_ms": execution_time,
                "hsts_value": hsts_value,
                "max_age": max_age,
                "subdomains_included": include_subdomains,
                "preload_enabled": preload
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"HSTS header configuration failed in {execution_time:.2f}ms: {str(e)}")
            return {"success": False, "error": str(e)}

    async def set_security_headers(self, request_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Set comprehensive security headers for request.
        
        Args:
            request_context: Request context information
            
        Returns:
            Dictionary of security headers
        """
        start_time = time.perf_counter()
        
        try:
            headers = {}
            
            # Get request-specific information
            is_creator_content = request_context.get("is_creator_content", False)
            content_type = request_context.get("content_type", "")
            user_agent = request_context.get("user_agent", "")
            
            # Add all applicable headers
            for header_name, header_config in self.security_headers.items():
                # Check if header applies to current context
                if self._header_applies_to_context(header_config, request_context):
                    # Generate dynamic value if needed
                    if header_config.dynamic_value:
                        header_value = await self._generate_dynamic_header_value(header_config, request_context)
                    else:
                        header_value = header_config.value
                    
                    headers[header_name] = header_value
            
            # Add creator-specific headers
            if is_creator_content:
                creator_headers = await self._get_creator_specific_headers(request_context)
                headers.update(creator_headers)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.debug(f"Security headers set in {execution_time:.2f}ms")
            
            return headers
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Setting security headers failed in {execution_time:.2f}ms: {str(e)}")
            return {}

    def _header_applies_to_context(self, header: SecurityHeader, context: Dict[str, Any]) -> bool:
        """Check if header applies to current request context."""
        # Check security level
        if header.security_level == SecurityLevel.STRICT and self.security_level != SecurityLevel.STRICT:
            return False
        
        # Check creator-specific headers
        if header.creator_specific and not context.get("involves_creator_content", False):
            return False
        
        return True

    async def _generate_dynamic_header_value(self, header: SecurityHeader, 
                                          context: Dict[str, Any]) -> str:
        """Generate dynamic header value based on context."""
        if header.header_type == HeaderType.CSP and header.nonce_required:
            # Refresh nonces for CSP
            return await self._refresh_csp_nonces(header.value)
        
        return header.value

    async def _refresh_csp_nonces(self, csp_value: str) -> str:
        """Refresh nonces in CSP header."""
        # Find and replace nonces
        import re
        
        def replace_nonce(match):
            new_nonce = self._generate_nonce()
            return f"'nonce-{new_nonce}'"
        
        # Replace existing nonces with new ones
        updated_csp = re.sub(r"'nonce-[^']*'", replace_nonce, csp_value)
        return updated_csp

    async def _get_creator_specific_headers(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Get headers specific to creator content."""
        creator_headers = {}
        
        content_type = context.get("content_type", "")
        
        # Creator content protection headers
        if "image" in content_type:
            creator_headers["X-Creator-Content-Type"] = "image"
            creator_headers["X-Creator-Protection"] = "watermark-enabled"
        elif "audio" in content_type:
            creator_headers["X-Creator-Content-Type"] = "audio"
            creator_headers["X-Creator-Protection"] = "fingerprint-enabled"
        elif "video" in content_type:
            creator_headers["X-Creator-Content-Type"] = "video"
            creator_headers["X-Creator-Protection"] = "drm-enabled"
        
        # Creator rights headers
        creator_headers["X-Creator-Rights"] = "protected"
        creator_headers["X-Content-Attribution"] = "required"
        
        return creator_headers

    async def validate_header_configuration(self, headers: Dict[str, str]) -> List[HeaderValidationResult]:
        """
        Validate security header configuration.
        
        Args:
            headers: Headers to validate
            
        Returns:
            List of validation results
        """
        start_time = time.perf_counter()
        
        try:
            validation_results = []
            
            for header_name, header_value in headers.items():
                result = await self._validate_individual_header(header_name, header_value)
                validation_results.append(result)
            
            # Check for missing critical headers
            critical_headers = [
                "Content-Security-Policy",
                "Strict-Transport-Security", 
                "X-Frame-Options",
                "X-Content-Type-Options"
            ]
            
            for critical_header in critical_headers:
                if critical_header not in headers:
                    missing_result = HeaderValidationResult(
                        success=False,
                        header_name=critical_header,
                        is_secure=False,
                        security_score=0.0,
                        vulnerabilities=[f"Missing critical header: {critical_header}"],
                        recommendations=[f"Add {critical_header} header"],
                        validation_time_ms=0.0
                    )
                    validation_results.append(missing_result)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"Header validation completed in {execution_time:.2f}ms")
            
            return validation_results
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Header validation failed in {execution_time:.2f}ms: {str(e)}")
            return []

    async def _validate_individual_header(self, header_name: str, header_value: str) -> HeaderValidationResult:
        """Validate individual security header."""
        start_time = time.perf_counter()
        
        try:
            vulnerabilities = []
            recommendations = []
            security_score = 1.0
            
            if header_name == "Content-Security-Policy":
                # Validate CSP
                if "'unsafe-inline'" in header_value:
                    vulnerabilities.append("CSP allows unsafe-inline")
                    security_score -= 0.3
                    recommendations.append("Remove 'unsafe-inline' and use nonces or hashes")
                
                if "'unsafe-eval'" in header_value:
                    vulnerabilities.append("CSP allows unsafe-eval")
                    security_score -= 0.4
                    recommendations.append("Remove 'unsafe-eval'")
                
                if "default-src" not in header_value:
                    vulnerabilities.append("CSP missing default-src directive")
                    security_score -= 0.2
                    recommendations.append("Add default-src directive")
            
            elif header_name == "Strict-Transport-Security":
                # Validate HSTS
                if "max-age=" not in header_value:
                    vulnerabilities.append("HSTS missing max-age")
                    security_score -= 0.5
                
                if "includeSubDomains" not in header_value:
                    recommendations.append("Consider adding includeSubDomains")
                    security_score -= 0.1
                
                if "preload" not in header_value:
                    recommendations.append("Consider adding preload")
                    security_score -= 0.1
            
            elif header_name == "X-Frame-Options":
                # Validate X-Frame-Options
                if header_value.upper() not in ["DENY", "SAMEORIGIN"]:
                    vulnerabilities.append("X-Frame-Options has weak value")
                    security_score -= 0.3
                    recommendations.append("Use DENY or SAMEORIGIN")
            
            elif header_name == "Referrer-Policy":
                # Validate Referrer Policy
                weak_policies = ["unsafe-url", "origin", "origin-when-cross-origin"]
                if header_value in weak_policies:
                    vulnerabilities.append("Weak referrer policy")
                    security_score -= 0.2
                    recommendations.append("Use strict-origin-when-cross-origin or stricter")
            
            security_score = max(0.0, security_score)
            is_secure = len(vulnerabilities) == 0 and security_score >= 0.8
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return HeaderValidationResult(
                success=True,
                header_name=header_name,
                is_secure=is_secure,
                security_score=security_score,
                vulnerabilities=vulnerabilities,
                recommendations=recommendations,
                validation_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            return HeaderValidationResult(
                success=False,
                header_name=header_name,
                is_secure=False,
                security_score=0.0,
                vulnerabilities=[f"Validation error: {str(e)}"],
                validation_time_ms=execution_time
            )

    async def dynamic_header_adjustment(self, request_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Dynamically adjust headers based on request characteristics.
        
        Args:
            request_info: Request information for adjustment
            
        Returns:
            Adjusted security headers
        """
        start_time = time.perf_counter()
        
        try:
            adjusted_headers = {}
            
            # Get base headers
            base_headers = await self.set_security_headers(request_info)
            adjusted_headers.update(base_headers)
            
            # Adjust based on user agent
            user_agent = request_info.get("user_agent", "")
            if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
                # Stricter headers for bots
                adjusted_headers["X-Robots-Tag"] = "noindex, nofollow"
                adjusted_headers["Cache-Control"] = "no-cache, no-store"
            
            # Adjust based on content type
            content_type = request_info.get("content_type", "")
            if "application/json" in content_type:
                adjusted_headers["X-Content-Type-Options"] = "nosniff"
                adjusted_headers["Content-Type"] = "application/json; charset=utf-8"
            
            # Adjust for creator content
            if request_info.get("is_creator_content"):
                creator_id = request_info.get("creator_id")
                if creator_id:
                    adjusted_headers["X-Creator-ID"] = hashlib.sha256(creator_id.encode()).hexdigest()[:16]
                
                # Add content protection headers
                adjusted_headers["X-Content-Protection"] = "enabled"
                adjusted_headers["X-Download-Options"] = "noopen"
            
            # Adjust based on geography
            country = request_info.get("country")
            if country in ["EU", "UK"]:  # GDPR regions
                adjusted_headers["X-Privacy-Policy"] = "gdpr-compliant"
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.debug(f"Dynamic header adjustment completed in {execution_time:.2f}ms")
            
            return adjusted_headers
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Dynamic header adjustment failed in {execution_time:.2f}ms: {str(e)}")
            return {}

    async def header_security_analysis(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis of headers.
        
        Args:
            headers: Headers to analyze
            
        Returns:
            Security analysis results
        """
        start_time = time.perf_counter()
        
        try:
            analysis_results = {
                "overall_score": 0.0,
                "security_level": "unknown",
                "vulnerabilities": [],
                "strengths": [],
                "missing_headers": [],
                "recommendations": []
            }
            
            # Validate headers
            validation_results = await self.validate_header_configuration(headers)
            
            # Calculate overall score
            total_score = 0.0
            valid_headers = 0
            
            for result in validation_results:
                if result.success:
                    total_score += result.security_score
                    valid_headers += 1
                    
                    if result.vulnerabilities:
                        analysis_results["vulnerabilities"].extend(result.vulnerabilities)
                    
                    if result.recommendations:
                        analysis_results["recommendations"].extend(result.recommendations)
                    
                    if result.is_secure:
                        analysis_results["strengths"].append(f"Secure {result.header_name}")
                else:
                    analysis_results["missing_headers"].append(result.header_name)
            
            # Calculate overall score
            if valid_headers > 0:
                analysis_results["overall_score"] = total_score / valid_headers
            
            # Determine security level
            score = analysis_results["overall_score"]
            if score >= 0.9:
                analysis_results["security_level"] = "excellent"
            elif score >= 0.8:
                analysis_results["security_level"] = "good"
            elif score >= 0.6:
                analysis_results["security_level"] = "fair"
            else:
                analysis_results["security_level"] = "poor"
            
            # Creator-specific analysis
            creator_analysis = self._analyze_creator_security(headers)
            analysis_results["creator_protection"] = creator_analysis
            
            execution_time = (time.perf_counter() - start_time) * 1000
            analysis_results["analysis_time_ms"] = execution_time
            
            logger.info(f"Header security analysis completed in {execution_time:.2f}ms")
            
            return analysis_results
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Header security analysis failed in {execution_time:.2f}ms: {str(e)}")
            return {"error": str(e)}

    def _analyze_creator_security(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze creator-specific security in headers."""
        creator_analysis = {
            "content_protection": False,
            "attribution_required": False,
            "watermark_detection": False,
            "download_protection": False
        }
        
        # Check for creator protection headers
        if "X-Creator-Protection" in headers:
            creator_analysis["content_protection"] = True
        
        if "X-Content-Attribution" in headers:
            creator_analysis["attribution_required"] = True
        
        if "watermark" in headers.get("X-Creator-Protection", ""):
            creator_analysis["watermark_detection"] = True
        
        if "X-Download-Options" in headers:
            creator_analysis["download_protection"] = True
        
        return creator_analysis

    async def prevent_clickjacking(self, frame_options: str = "DENY") -> Dict[str, Any]:
        """
        Implement clickjacking prevention headers.
        
        Args:
            frame_options: Frame options policy
            
        Returns:
            Clickjacking prevention results
        """
        start_time = time.perf_counter()
        
        try:
            # Set X-Frame-Options
            frame_header = SecurityHeader(
                header_type=HeaderType.X_FRAME_OPTIONS,
                name="X-Frame-Options",
                value=frame_options,
                description="Prevent clickjacking attacks",
                security_level=SecurityLevel.BASIC
            )
            
            self.security_headers["X-Frame-Options"] = frame_header
            
            # Also update CSP frame-ancestors if CSP exists
            if "Content-Security-Policy" in self.security_headers:
                csp_value = self.security_headers["Content-Security-Policy"].value
                
                if "frame-ancestors" not in csp_value:
                    if frame_options.upper() == "DENY":
                        csp_value += "; frame-ancestors 'none'"
                    elif frame_options.upper() == "SAMEORIGIN":
                        csp_value += "; frame-ancestors 'self'"
                    
                    self.security_headers["Content-Security-Policy"].value = csp_value
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            logger.info(f"Clickjacking prevention implemented in {execution_time:.2f}ms")
            
            return {
                "success": True,
                "implementation_time_ms": execution_time,
                "frame_options": frame_options,
                "csp_updated": "Content-Security-Policy" in self.security_headers
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Clickjacking prevention failed in {execution_time:.2f}ms: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_security_headers_statistics(self) -> Dict[str, Any]:
        """Get comprehensive security headers statistics."""
        try:
            # Header statistics
            total_headers = len(self.security_headers)
            creator_specific_headers = len([
                h for h in self.security_headers.values() if h.creator_specific
            ])
            dynamic_headers = len([
                h for h in self.security_headers.values() if h.dynamic_value
            ])
            nonce_headers = len([
                h for h in self.security_headers.values() if h.nonce_required
            ])
            
            # Security level distribution
            level_distribution = {}
            for header in self.security_headers.values():
                level = header.security_level.value
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            # CSP statistics
            csp_policies_count = len(self.csp_policies)
            active_nonces = len(self.nonce_cache)
            
            return {
                "total_headers": total_headers,
                "creator_specific_headers": creator_specific_headers,
                "dynamic_headers": dynamic_headers,
                "nonce_enabled_headers": nonce_headers,
                "security_level_distribution": level_distribution,
                "csp_policies": csp_policies_count,
                "active_nonces": active_nonces,
                "configured_security_level": self.security_level.value,
                "creator_domains_configured": len(self.creator_content_domains),
                "cdn_domains_configured": len(self.cdn_domains)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate security headers statistics: {str(e)}")
            return {"error": str(e)}

    async def cleanup_expired_nonces(self, max_age_minutes: int = 60) -> Dict[str, Any]:
        """
        Clean up expired nonces.
        
        Args:
            max_age_minutes: Maximum age for nonces in minutes
            
        Returns:
            Cleanup results
        """
        start_time = time.perf_counter()
        
        try:
            current_time = datetime.now(timezone.utc)
            expired_nonces = []
            
            for nonce, timestamp_str in list(self.nonce_cache.items()):
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age = (current_time - timestamp).total_seconds() / 60
                    
                    if age > max_age_minutes:
                        expired_nonces.append(nonce)
                        del self.nonce_cache[nonce]
                        
                except Exception:
                    # Remove invalid entries
                    expired_nonces.append(nonce)
                    del self.nonce_cache[nonce]
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return {
                "success": True,
                "cleanup_time_ms": execution_time,
                "expired_nonces_removed": len(expired_nonces),
                "active_nonces_remaining": len(self.nonce_cache)
            }
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Nonce cleanup failed in {execution_time:.2f}ms: {str(e)}")
            return {"success": False, "error": str(e)}

# Factory for enterprise deployment
class SecurityHeadersFactory:
    """Factory for creating SecurityHeaders instances with different configurations."""
    
    @staticmethod
    def create_production_headers() -> SecurityHeaders:
        """Create production-ready security headers."""
        config = {
            "security_level": "creator_focused",
            "enable_nonce": True,
            "creator_content_domains": ["*.ainflue-content.com", "creator-cdn.ainflue.com"],
            "cdn_domains": ["cdn.ainflue.com", "static.ainflue.com"],
            "log_level": "INFO"
        }
        return SecurityHeaders(config)
    
    @staticmethod
    def create_development_headers() -> SecurityHeaders:
        """Create development security headers."""
        config = {
            "security_level": "standard",
            "enable_nonce": False,
            "creator_content_domains": ["localhost:3000", "dev.ainflue.com"],
            "cdn_domains": ["localhost:8080"],
            "log_level": "DEBUG"
        }
        return SecurityHeaders(config)
    
    @staticmethod
    def create_strict_security_headers() -> SecurityHeaders:
        """Create strict security headers for high-security environments."""
        config = {
            "security_level": "strict",
            "enable_nonce": True,
            "creator_content_domains": [],  # No external domains
            "cdn_domains": [],
            "log_level": "WARNING"
        }
        return SecurityHeaders(config)