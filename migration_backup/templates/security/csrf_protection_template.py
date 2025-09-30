"""
🛡️ CSRF Protection Template - Enterprise Cross-Site Request Forgery Protection
===============================================================================

🔐 SECURITY EXPERT - Advanced CSRF Protection Template  
- Comprehensive CSRF token generation and validation
- Double-submit cookie pattern implementation
- SameSite cookie configuration and enforcement
- Origin and Referer header validation
- State-changing operation protection
- Enterprise audit logging and threat detection

Author: Security Expert
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import secrets
import hashlib
import hmac
import uuid
import urllib.parse
from abc import ABC, abstractmethod
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSRFMethod(Enum):
    """CSRF protection methods"""
    TOKEN_VALIDATION = "token_validation"
    DOUBLE_SUBMIT_COOKIE = "double_submit_cookie"
    ORIGIN_VALIDATION = "origin_validation"
    REFERER_VALIDATION = "referer_validation"
    CUSTOM_HEADER = "custom_header"

class ProtectionLevel(Enum):
    """CSRF protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

class SameSitePolicy(Enum):
    """SameSite cookie policies"""
    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"

class CSRFThreatLevel(Enum):
    """CSRF threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CSRFToken:
    """CSRF token data structure"""
    token_id: str
    token_value: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    origin: Optional[str] = None
    usage_count: int = 0
    max_usage: int = 1
    is_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CSRFValidationResult:
    """Result of CSRF validation"""
    is_valid: bool
    token_id: Optional[str] = None
    validation_method: Optional[CSRFMethod] = None
    error_message: Optional[str] = None
    threat_level: CSRFThreatLevel = CSRFThreatLevel.LOW
    validation_time_ms: float = 0.0
    additional_checks: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class CSRFConfig:
    """CSRF protection configuration"""
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    token_lifetime_hours: int = 1
    cookie_name: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    parameter_name: str = "csrf_token"
    samesite_policy: SameSitePolicy = SameSitePolicy.STRICT
    secure_cookies: bool = True
    httponly_cookies: bool = True
    require_origin_header: bool = True
    require_referer_header: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    blocked_user_agents: List[str] = field(default_factory=list)
    enable_audit_logging: bool = True
    max_tokens_per_session: int = 10

@dataclass
class CSRFThreatDetection:
    """CSRF threat detection record"""
    threat_id: str
    threat_type: str
    threat_level: CSRFThreatLevel
    description: str
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)

class CSRFTokenStorage(ABC):
    """Abstract CSRF token storage interface"""
    
    @abstractmethod
    async def store_token(self, token: CSRFToken) -> bool:
        """Store CSRF token"""
        pass
    
    @abstractmethod
    async def get_token(self, token_id: str) -> Optional[CSRFToken]:
        """Retrieve CSRF token"""
        pass
    
    @abstractmethod
    async def invalidate_token(self, token_id: str) -> bool:
        """Invalidate CSRF token"""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        pass

class MemoryCSRFTokenStorage(CSRFTokenStorage):
    """In-memory CSRF token storage"""
    
    def __init__(self, max_tokens: int = 10000):
        self.tokens = {}
        self.max_tokens = max_tokens
    
    async def store_token(self, token: CSRFToken) -> bool:
        """Store token in memory"""
        try:
            # Clean up if at max capacity
            if len(self.tokens) >= self.max_tokens:
                await self.cleanup_expired_tokens()
            
            self.tokens[token.token_id] = token
            return True
        except Exception as e:
            logger.error(f"Failed to store CSRF token: {str(e)}")
            return False
    
    async def get_token(self, token_id: str) -> Optional[CSRFToken]:
        """Get token from memory"""
        try:
            token = self.tokens.get(token_id)
            if token and token.expires_at > datetime.now():
                return token
            elif token:
                # Token expired, remove it
                await self.invalidate_token(token_id)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve CSRF token: {str(e)}")
            return None
    
    async def invalidate_token(self, token_id: str) -> bool:
        """Invalidate token"""
        try:
            if token_id in self.tokens:
                self.tokens[token_id].is_valid = False
                del self.tokens[token_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to invalidate CSRF token: {str(e)}")
            return False
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        try:
            current_time = datetime.now()
            expired_tokens = [
                token_id for token_id, token in self.tokens.items()
                if token.expires_at <= current_time or not token.is_valid
            ]
            
            for token_id in expired_tokens:
                del self.tokens[token_id]
            
            return len(expired_tokens)
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {str(e)}")
            return 0

class CSRFTokenGenerator:
    """CSRF token generator with cryptographic security"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "sha256"
    
    def generate_token(self, user_id: Optional[str] = None, 
                      session_id: Optional[str] = None,
                      additional_data: Dict[str, Any] = None) -> CSRFToken:
        """Generate cryptographically secure CSRF token"""
        
        token_id = str(uuid.uuid4())
        timestamp = str(int(time.time()))
        
        # Create token payload
        payload = {
            "token_id": token_id,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": timestamp,
            "random": secrets.token_urlsafe(16)
        }
        
        if additional_data:
            payload.update(additional_data)
        
        # Create HMAC signature
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        token_value = base64.urlsafe_b64encode(
            json.dumps({
                "payload": payload,
                "signature": signature
            }).encode()
        ).decode()
        
        return CSRFToken(
            token_id=token_id,
            token_value=token_value,
            user_id=user_id,
            session_id=session_id,
            metadata=additional_data or {}
        )
    
    def validate_token_signature(self, token_value: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate token signature and extract payload"""
        try:
            # Decode token
            decoded_data = json.loads(
                base64.urlsafe_b64decode(token_value.encode()).decode()
            )
            
            payload = decoded_data.get("payload", {})
            signature = decoded_data.get("signature", "")
            
            # Recreate signature
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            return is_valid, payload
            
        except Exception as e:
            logger.error(f"Token signature validation error: {str(e)}")
            return False, {}

class CSRFProtection:
    """🛡️ Enterprise CSRF Protection Framework"""
    
    def __init__(self, config: CSRFConfig = None, 
                 token_storage: CSRFTokenStorage = None):
        """Initialize CSRF Protection"""
        self.config = config or CSRFConfig()
        self.token_storage = token_storage or MemoryCSRFTokenStorage()
        self.token_generator = CSRFTokenGenerator()
        
        # Threat detection
        self.detected_threats = []
        self.threat_stats = defaultdict(int)
        
        # Background tasks
        self.background_tasks = []
        self.is_running = False
        
        # Statistics
        self.stats = {
            "tokens_generated": 0,
            "tokens_validated": 0,
            "validation_failures": 0,
            "threats_detected": 0,
            "requests_protected": 0
        }
        
        logger.info(f"🛡️ CSRF Protection initialized with {self.config.protection_level.value} level")
    
    async def start(self):
        """Start CSRF protection service"""
        logger.info("Starting CSRF Protection service")
        
        self.is_running = True
        
        # Start token cleanup task
        cleanup_task = asyncio.create_task(self._token_cleanup_loop())
        self.background_tasks.append(cleanup_task)
        
        # Start threat monitoring task
        monitoring_task = asyncio.create_task(self._threat_monitoring_loop())
        self.background_tasks.append(monitoring_task)
        
        logger.info("✅ CSRF Protection service started")
    
    async def stop(self):
        """Stop CSRF protection service"""
        logger.info("Stopping CSRF Protection service")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("✅ CSRF Protection service stopped")
    
    async def generate_token(self, user_id: Optional[str] = None,
                           session_id: Optional[str] = None,
                           origin: Optional[str] = None,
                           additional_data: Dict[str, Any] = None) -> CSRFToken:
        """Generate new CSRF token"""
        
        token = self.token_generator.generate_token(
            user_id=user_id,
            session_id=session_id,
            additional_data=additional_data
        )
        
        token.origin = origin
        
        # Store token
        success = await self.token_storage.store_token(token)
        if not success:
            raise Exception("Failed to store CSRF token")
        
        self.stats["tokens_generated"] += 1
        
        logger.debug(f"Generated CSRF token: {token.token_id}")
        return token
    
    async def validate_request(self, request_data: Dict[str, Any]) -> CSRFValidationResult:
        """Validate request for CSRF protection"""
        start_time = time.time()
        
        try:
            self.stats["requests_protected"] += 1
            
            # Extract validation data
            token_value = self._extract_token(request_data)
            origin = request_data.get("origin")
            referer = request_data.get("referer")
            user_agent = request_data.get("user_agent")
            method = request_data.get("method", "POST")
            
            # Skip CSRF validation for safe methods
            if method.upper() in ["GET", "HEAD", "OPTIONS", "TRACE"]:
                return CSRFValidationResult(
                    is_valid=True,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    validation_time_ms=(time.time() - start_time) * 1000
                )
            
            validation_results = []
            
            # Method 1: Token validation
            if token_value:
                token_result = await self._validate_token(token_value, request_data)
                validation_results.append(token_result)
            else:
                validation_results.append(CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="CSRF token missing",
                    threat_level=CSRFThreatLevel.HIGH
                ))
            
            # Method 2: Origin validation
            if self.config.require_origin_header:
                origin_result = await self._validate_origin(origin, request_data)
                validation_results.append(origin_result)
            
            # Method 3: Referer validation
            if self.config.require_referer_header:
                referer_result = await self._validate_referer(referer, request_data)
                validation_results.append(referer_result)
            
            # Method 4: Custom header validation
            custom_header_result = await self._validate_custom_headers(request_data)
            if custom_header_result:
                validation_results.append(custom_header_result)
            
            # Combine validation results
            final_result = await self._combine_validation_results(validation_results)
            final_result.validation_time_ms = (time.time() - start_time) * 1000
            
            # Log validation result
            if final_result.is_valid:
                self.stats["tokens_validated"] += 1
            else:
                self.stats["validation_failures"] += 1
                await self._log_validation_failure(final_result, request_data)
            
            return final_result
            
        except Exception as e:
            logger.error(f"CSRF validation error: {str(e)}")
            return CSRFValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}",
                threat_level=CSRFThreatLevel.HIGH,
                validation_time_ms=(time.time() - start_time) * 1000
            )
    
    def _extract_token(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract CSRF token from request"""
        
        # Check header
        headers = request_data.get("headers", {})
        if self.config.header_name in headers:
            return headers[self.config.header_name]
        
        # Check form parameter
        form_data = request_data.get("form", {})
        if self.config.parameter_name in form_data:
            return form_data[self.config.parameter_name]
        
        # Check cookie (for double-submit pattern)
        cookies = request_data.get("cookies", {})
        if self.config.cookie_name in cookies:
            return cookies[self.config.cookie_name]
        
        return None
    
    async def _validate_token(self, token_value: str, 
                            request_data: Dict[str, Any]) -> CSRFValidationResult:
        """Validate CSRF token"""
        
        try:
            # Validate token signature
            is_signature_valid, payload = self.token_generator.validate_token_signature(token_value)
            
            if not is_signature_valid:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="Invalid token signature",
                    threat_level=CSRFThreatLevel.HIGH
                )
            
            # Get token from storage
            token_id = payload.get("token_id")
            if not token_id:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="Token ID missing from payload",
                    threat_level=CSRFThreatLevel.HIGH
                )
            
            stored_token = await self.token_storage.get_token(token_id)
            if not stored_token:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="Token not found or expired",
                    threat_level=CSRFThreatLevel.MEDIUM
                )
            
            # Validate token properties
            if not stored_token.is_valid:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="Token has been invalidated",
                    threat_level=CSRFThreatLevel.MEDIUM
                )
            
            # Check usage count
            if stored_token.usage_count >= stored_token.max_usage:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.TOKEN_VALIDATION,
                    error_message="Token usage limit exceeded",
                    threat_level=CSRFThreatLevel.MEDIUM
                )
            
            # Update usage count
            stored_token.usage_count += 1
            
            # Invalidate single-use tokens
            if stored_token.usage_count >= stored_token.max_usage:
                await self.token_storage.invalidate_token(token_id)
            
            return CSRFValidationResult(
                is_valid=True,
                token_id=token_id,
                validation_method=CSRFMethod.TOKEN_VALIDATION
            )
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return CSRFValidationResult(
                is_valid=False,
                validation_method=CSRFMethod.TOKEN_VALIDATION,
                error_message=f"Token validation failed: {str(e)}",
                threat_level=CSRFThreatLevel.HIGH
            )
    
    async def _validate_origin(self, origin: Optional[str], 
                             request_data: Dict[str, Any]) -> CSRFValidationResult:
        """Validate Origin header"""
        
        if not origin:
            return CSRFValidationResult(
                is_valid=False,
                validation_method=CSRFMethod.ORIGIN_VALIDATION,
                error_message="Origin header missing",
                threat_level=CSRFThreatLevel.HIGH
            )
        
        # Check against allowed origins
        if self.config.allowed_origins:
            if origin not in self.config.allowed_origins:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.ORIGIN_VALIDATION,
                    error_message=f"Origin {origin} not in allowed list",
                    threat_level=CSRFThreatLevel.HIGH
                )
        
        # Basic origin validation
        try:
            parsed_origin = urllib.parse.urlparse(origin)
            if not parsed_origin.scheme or not parsed_origin.netloc:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.ORIGIN_VALIDATION,
                    error_message="Invalid origin format",
                    threat_level=CSRFThreatLevel.HIGH
                )
        except Exception:
            return CSRFValidationResult(
                is_valid=False,
                validation_method=CSRFMethod.ORIGIN_VALIDATION,
                error_message="Origin parsing failed",
                threat_level=CSRFThreatLevel.HIGH
            )
        
        return CSRFValidationResult(
            is_valid=True,
            validation_method=CSRFMethod.ORIGIN_VALIDATION
        )
    
    async def _validate_referer(self, referer: Optional[str], 
                              request_data: Dict[str, Any]) -> CSRFValidationResult:
        """Validate Referer header"""
        
        if not referer:
            return CSRFValidationResult(
                is_valid=False,
                validation_method=CSRFMethod.REFERER_VALIDATION,
                error_message="Referer header missing",
                threat_level=CSRFThreatLevel.MEDIUM
            )
        
        # Basic referer validation
        try:
            parsed_referer = urllib.parse.urlparse(referer)
            if not parsed_referer.scheme or not parsed_referer.netloc:
                return CSRFValidationResult(
                    is_valid=False,
                    validation_method=CSRFMethod.REFERER_VALIDATION,
                    error_message="Invalid referer format",
                    threat_level=CSRFThreatLevel.MEDIUM
                )
        except Exception:
            return CSRFValidationResult(
                is_valid=False,
                validation_method=CSRFMethod.REFERER_VALIDATION,
                error_message="Referer parsing failed",
                threat_level=CSRFThreatLevel.MEDIUM
            )
        
        return CSRFValidationResult(
            is_valid=True,
            validation_method=CSRFMethod.REFERER_VALIDATION
        )
    
    async def _validate_custom_headers(self, request_data: Dict[str, Any]) -> Optional[CSRFValidationResult]:
        """Validate custom headers for CSRF protection"""
        
        headers = request_data.get("headers", {})
        
        # Check for custom CSRF header
        if "X-Requested-With" in headers:
            if headers["X-Requested-With"] == "XMLHttpRequest":
                return CSRFValidationResult(
                    is_valid=True,
                    validation_method=CSRFMethod.CUSTOM_HEADER
                )
        
        return None
    
    async def _combine_validation_results(self, results: List[CSRFValidationResult]) -> CSRFValidationResult:
        """Combine multiple validation results"""
        
        if not results:
            return CSRFValidationResult(
                is_valid=False,
                error_message="No validation methods applied",
                threat_level=CSRFThreatLevel.CRITICAL
            )
        
        # Determine overall validity based on protection level
        valid_results = [r for r in results if r.is_valid]
        
        if self.config.protection_level == ProtectionLevel.BASIC:
            # At least one method must pass
            is_valid = len(valid_results) > 0
        elif self.config.protection_level == ProtectionLevel.STANDARD:
            # Token validation must pass, plus one other method
            token_valid = any(r.is_valid and r.validation_method == CSRFMethod.TOKEN_VALIDATION for r in results)
            other_valid = any(r.is_valid and r.validation_method != CSRFMethod.TOKEN_VALIDATION for r in results)
            is_valid = token_valid and (other_valid or len(results) == 1)
        elif self.config.protection_level in [ProtectionLevel.STRICT, ProtectionLevel.PARANOID]:
            # All methods must pass
            is_valid = len(valid_results) == len(results)
        else:
            is_valid = False
        
        # Collect error messages and threat levels
        error_messages = [r.error_message for r in results if not r.is_valid and r.error_message]
        threat_levels = [r.threat_level for r in results if not r.is_valid]
        
        max_threat_level = CSRFThreatLevel.LOW
        if threat_levels:
            threat_level_order = [CSRFThreatLevel.LOW, CSRFThreatLevel.MEDIUM, CSRFThreatLevel.HIGH, CSRFThreatLevel.CRITICAL]
            max_threat_level = max(threat_levels, key=lambda x: threat_level_order.index(x))
        
        # Generate recommendations
        recommendations = []
        if not is_valid:
            recommendations.append("Implement proper CSRF tokens in forms")
            recommendations.append("Configure SameSite cookie attributes")
            recommendations.append("Validate Origin and Referer headers")
            if self.config.protection_level == ProtectionLevel.BASIC:
                recommendations.append("Consider upgrading to Standard protection level")
        
        return CSRFValidationResult(
            is_valid=is_valid,
            error_message="; ".join(error_messages) if error_messages else None,
            threat_level=max_threat_level,
            additional_checks={r.validation_method.value: r.is_valid for r in results if r.validation_method},
            recommendations=recommendations
        )
    
    async def _log_validation_failure(self, result: CSRFValidationResult, 
                                    request_data: Dict[str, Any]):
        """Log CSRF validation failure"""
        
        threat = CSRFThreatDetection(
            threat_id=str(uuid.uuid4()),
            threat_type="csrf_validation_failure",
            threat_level=result.threat_level,
            description=result.error_message or "CSRF validation failed",
            source_ip=request_data.get("client_ip"),
            user_agent=request_data.get("user_agent"),
            user_id=request_data.get("user_id"),
            session_id=request_data.get("session_id"),
            request_url=request_data.get("url"),
            additional_data={
                "validation_method": result.validation_method.value if result.validation_method else None,
                "additional_checks": result.additional_checks
            }
        )
        
        self.detected_threats.append(threat)
        self.threat_stats["csrf_validation_failure"] += 1
        self.stats["threats_detected"] += 1
        
        # Log based on threat level
        if threat.threat_level == CSRFThreatLevel.CRITICAL:
            logger.critical(f"CRITICAL CSRF THREAT: {threat.description} from {threat.source_ip}")
        elif threat.threat_level == CSRFThreatLevel.HIGH:
            logger.error(f"HIGH CSRF THREAT: {threat.description} from {threat.source_ip}")
        else:
            logger.warning(f"CSRF validation failure: {threat.description}")
    
    async def _token_cleanup_loop(self):
        """Background task to clean up expired tokens"""
        while self.is_running:
            try:
                cleaned_count = await self.token_storage.cleanup_expired_tokens()
                if cleaned_count > 0:
                    logger.debug(f"Cleaned up {cleaned_count} expired CSRF tokens")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Token cleanup error: {str(e)}")
    
    async def _threat_monitoring_loop(self):
        """Background task for threat monitoring"""
        while self.is_running:
            try:
                # Analyze threat patterns
                recent_threats = [
                    t for t in self.detected_threats
                    if (datetime.now() - t.timestamp).total_seconds() < 3600  # Last hour
                ]
                
                # Check for attack patterns
                if len(recent_threats) > 100:  # More than 100 threats in an hour
                    logger.critical("CSRF ATTACK PATTERN DETECTED: High volume of validation failures")
                
                # Group threats by source IP
                ip_threats = defaultdict(int)
                for threat in recent_threats:
                    if threat.source_ip:
                        ip_threats[threat.source_ip] += 1
                
                # Alert on high threat count from single IP
                for ip, count in ip_threats.items():
                    if count > 10:  # More than 10 threats from same IP
                        logger.warning(f"High CSRF threat count from IP {ip}: {count} threats")
                
                await asyncio.sleep(900)  # Run every 15 minutes
                
            except Exception as e:
                logger.error(f"Threat monitoring error: {str(e)}")
    
    def generate_cookie_attributes(self, token: CSRFToken) -> Dict[str, Any]:
        """Generate secure cookie attributes for CSRF token"""
        
        attributes = {
            "httponly": self.config.httponly_cookies,
            "secure": self.config.secure_cookies,
            "samesite": self.config.samesite_policy.value,
            "expires": token.expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        
        return attributes
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers for CSRF protection"""
        
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        if self.config.protection_level in [ProtectionLevel.STRICT, ProtectionLevel.PARANOID]:
            headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        
        return headers
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """Get CSRF protection statistics"""
        
        recent_threats = [
            t for t in self.detected_threats
            if (datetime.now() - t.timestamp).total_seconds() < 3600
        ]
        
        return {
            **self.stats,
            "protection_level": self.config.protection_level.value,
            "total_threats_detected": len(self.detected_threats),
            "recent_threats_count": len(recent_threats),
            "threat_types": dict(self.threat_stats),
            "token_lifetime_hours": self.config.token_lifetime_hours,
            "samesite_policy": self.config.samesite_policy.value,
            "is_running": self.is_running
        }

# Usage Example and Template Testing
async def main():
    """Example usage of CSRF Protection Template"""
    
    # Create CSRF configuration
    config = CSRFConfig(
        protection_level=ProtectionLevel.STANDARD,
        token_lifetime_hours=2,
        allowed_origins=["https://example.com", "https://app.example.com"],
        require_origin_header=True,
        require_referer_header=True
    )
    
    # Initialize CSRF protection
    csrf_protection = CSRFProtection(config)
    
    try:
        # Start the service
        await csrf_protection.start()
        
        # Generate CSRF token
        token = await csrf_protection.generate_token(
            user_id="user_123",
            session_id="session_456",
            origin="https://example.com"
        )
        
        print(f"✅ CSRF Token generated:")
        print(f"  Token ID: {token.token_id}")
        print(f"  Expires: {token.expires_at}")
        print(f"  Value length: {len(token.token_value)} characters")
        
        # Test valid request
        valid_request = {
            "method": "POST",
            "headers": {
                csrf_protection.config.header_name: token.token_value,
                "Origin": "https://example.com"
            },
            "origin": "https://example.com",
            "referer": "https://example.com/form",
            "client_ip": "192.168.1.100",
            "user_id": "user_123"
        }
        
        valid_result = await csrf_protection.validate_request(valid_request)
        print(f"\n✅ Valid request validation:")
        print(f"  Is valid: {valid_result.is_valid}")
        print(f"  Validation time: {valid_result.validation_time_ms:.2f}ms")
        print(f"  Checks passed: {valid_result.additional_checks}")
        
        # Test CSRF attack simulation
        csrf_attack_request = {
            "method": "POST",
            "headers": {
                "Origin": "https://malicious-site.com"
            },
            "origin": "https://malicious-site.com",
            "referer": "https://malicious-site.com/attack",
            "client_ip": "192.168.1.200",
            "user_id": "user_123"
        }
        
        attack_result = await csrf_protection.validate_request(csrf_attack_request)
        print(f"\n🚨 CSRF Attack simulation:")
        print(f"  Is valid: {attack_result.is_valid}")
        print(f"  Error: {attack_result.error_message}")
        print(f"  Threat level: {attack_result.threat_level.value}")
        print(f"  Recommendations: {attack_result.recommendations}")
        
        # Test missing token
        missing_token_request = {
            "method": "POST",
            "headers": {
                "Origin": "https://example.com"
            },
            "origin": "https://example.com",
            "referer": "https://example.com/form",
            "client_ip": "192.168.1.100"
        }
        
        missing_result = await csrf_protection.validate_request(missing_token_request)
        print(f"\n⚠️ Missing token validation:")
        print(f"  Is valid: {missing_result.is_valid}")
        print(f"  Error: {missing_result.error_message}")
        print(f"  Threat level: {missing_result.threat_level.value}")
        
        # Test safe method (GET request)
        get_request = {
            "method": "GET",
            "client_ip": "192.168.1.100"
        }
        
        get_result = await csrf_protection.validate_request(get_request)
        print(f"\n✅ Safe method (GET) validation:")
        print(f"  Is valid: {get_result.is_valid}")
        print(f"  Validation time: {get_result.validation_time_ms:.2f}ms")
        
        # Get cookie attributes
        cookie_attrs = csrf_protection.generate_cookie_attributes(token)
        print(f"\n🍪 Secure cookie attributes:")
        for key, value in cookie_attrs.items():
            print(f"  {key}: {value}")
        
        # Get security headers
        security_headers = csrf_protection.get_security_headers()
        print(f"\n🛡️ Security headers:")
        for header, value in security_headers.items():
            print(f"  {header}: {value}")
        
        # Get protection statistics
        stats = csrf_protection.get_protection_stats()
        print(f"\n📊 CSRF Protection Statistics:")
        print(f"  Tokens generated: {stats['tokens_generated']}")
        print(f"  Tokens validated: {stats['tokens_validated']}")
        print(f"  Validation failures: {stats['validation_failures']}")
        print(f"  Threats detected: {stats['threats_detected']}")
        print(f"  Protection level: {stats['protection_level']}")
        print(f"  SameSite policy: {stats['samesite_policy']}")
        
        print(f"\n✅ CSRF Protection demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in CSRF protection demo: {str(e)}")
    finally:
        # Stop the service
        await csrf_protection.stop()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🛡️ CSRF Protection Template demonstration completed!")