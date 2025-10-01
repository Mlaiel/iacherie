"""Webhook Security Template for IA Chéries Platform
Advanced security features for webhook processing and protection

⚠️  AVERTISSEMENT LÉGAL:
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

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
import hmac
import hashlib
import secrets
import ipaddress
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
import re

from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel, validator, Field
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

from core.config import get_settings
from core.database import get_db_session, Base
from core.rate_limiting import RateLimiter
from utils.exceptions import SecurityException, WebhookSecurityException
from monitoring.security_metrics import SecurityMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class SecurityLevel(str, Enum):
    """Security levels for webhook endpoints"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms"""
    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA512 = "hmac-sha512"
    RSA_SHA256 = "rsa-sha256"
    ECDSA_SHA256 = "ecdsa-sha256"


class ThreatType(str, Enum):
    """Types of security threats"""
    REPLAY_ATTACK = "replay_attack"
    SIGNATURE_TAMPERING = "signature_tampering"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_IP = "invalid_ip"
    SUSPICIOUS_PAYLOAD = "suspicious_payload"
    MALFORMED_REQUEST = "malformed_request"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


@dataclass
class SecurityConfig:
    """Webhook security configuration"""
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    timestamp_tolerance_seconds: int = 300
    enable_ip_filtering: bool = True
    enable_rate_limiting: bool = True
    enable_payload_validation: bool = True
    enable_replay_protection: bool = True
    max_payload_size_mb: int = 10
    encryption_enabled: bool = True
    audit_enabled: bool = True


class WebhookSecurityAudit(Base):
    """Database model for webhook security audit logs"""
    __tablename__ = "webhook_security_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    request_id = Column(String(255), nullable=False, index=True)
    ip_address = Column(INET, nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    threat_type = Column(String(100), nullable=True, index=True)
    security_level = Column(String(50), nullable=False, index=True)
    blocked = Column(Boolean, default=False, nullable=False)
    payload_hash = Column(String(255), nullable=True)
    headers = Column(JSONB, nullable=True)
    meta_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IPAllowlist(Base):
    """Database model for IP allowlist"""
    __tablename__ = "webhook_ip_allowlist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(INET, nullable=False, index=True)
    cidr_block = Column(String(45), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)


class SecurityKey(Base):
    """Database model for webhook security keys"""
    __tablename__ = "webhook_security_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    key_type = Column(String(50), nullable=False)  # signing, encryption
    algorithm = Column(String(50), nullable=False)
    public_key = Column(Text, nullable=True)
    private_key_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)


class WebhookSecurityManager:
    """Comprehensive webhook security management system"""

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.redis = None
        self.metrics = SecurityMetrics()
        self.rate_limiter = RateLimiter()
        self._encryption_key = None
        self._signing_keys: Dict[str, bytes] = {}

    async def initialize(self):
        """Initialize security manager"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize encryption key
            if self.config.encryption_enabled:
                self._encryption_key = Fernet.generate_key()
            
            logger.info("Webhook security manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize webhook security manager: {e}")
            raise

    async def generate_signing_key(
        self,
        endpoint_id: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    ) -> str:
        """Generate a secure signing key for webhook endpoint"""
        try:
            if algorithm in [SignatureAlgorithm.HMAC_SHA256, SignatureAlgorithm.HMAC_SHA512]:
                # Generate HMAC key
                key = secrets.token_urlsafe(32)
                self._signing_keys[endpoint_id] = key.encode('utf-8')
                return key
            
            elif algorithm == SignatureAlgorithm.RSA_SHA256:
                # Generate RSA key pair
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                public_key = private_key.public_key()
                
                # Serialize keys
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                self._signing_keys[endpoint_id] = private_pem
                return public_pem.decode('utf-8')
            
            else:
                raise SecurityException(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Failed to generate signing key: {e}")
            raise SecurityException(f"Key generation failed: {e}")

    async def create_signature(
        self,
        payload: str,
        endpoint_id: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
        timestamp: Optional[str] = None
    ) -> str:
        """Create secure signature for webhook payload"""
        try:
            if endpoint_id not in self._signing_keys:
                raise SecurityException(f"No signing key found for endpoint: {endpoint_id}")
            
            key = self._signing_keys[endpoint_id]
            
            # Add timestamp to payload if provided
            if timestamp:
                payload = f"{timestamp}.{payload}"
            
            if algorithm == SignatureAlgorithm.HMAC_SHA256:
                signature = hmac.new(
                    key,
                    payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                return f"sha256={signature}"
            
            elif algorithm == SignatureAlgorithm.HMAC_SHA512:
                signature = hmac.new(
                    key,
                    payload.encode('utf-8'),
                    hashlib.sha512
                ).hexdigest()
                return f"sha512={signature}"
            
            elif algorithm == SignatureAlgorithm.RSA_SHA256:
                # RSA signature
                private_key = serialization.load_pem_private_key(key, password=None)
                signature = private_key.sign(
                    payload.encode('utf-8'),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return base64.b64encode(signature).decode('utf-8')
            
            else:
                raise SecurityException(f"Unsupported signature algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Failed to create signature: {e}")
            raise SecurityException(f"Signature creation failed: {e}")

    async def verify_signature(
        self,
        payload: str,
        signature: str,
        endpoint_id: str,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify webhook signature securely"""
        try:
            if endpoint_id not in self._signing_keys:
                logger.warning(f"No signing key found for endpoint: {endpoint_id}")
                return False
            
            expected_signature = await self.create_signature(
                payload, endpoint_id, algorithm, timestamp
            )
            
            # Secure comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    async def validate_timestamp(self, timestamp: str) -> bool:
        """Validate webhook timestamp to prevent replay attacks"""
        try:
            timestamp_dt = datetime.fromtimestamp(int(timestamp))
            current_time = datetime.utcnow()
            time_diff = abs((current_time - timestamp_dt).total_seconds())
            
            if time_diff > self.config.timestamp_tolerance_seconds:
                logger.warning(f"Timestamp validation failed: {time_diff}s difference")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid timestamp format: {e}")
            return False

    async def check_replay_attack(
        self,
        request_id: str,
        signature: str,
        timestamp: str
    ) -> bool:
        """Check for replay attacks using Redis"""
        try:
            if not self.config.enable_replay_protection:
                return True
            
            # Create unique key for this request
            replay_key = f"webhook_replay:{hashlib.sha256(f'{request_id}:{signature}:{timestamp}'.encode()).hexdigest()}"
            
            # Check if we've seen this exact request before
            exists = await self.redis.exists(replay_key)
            if exists:
                logger.warning(f"Potential replay attack detected: {request_id}")
                return False
            
            # Store this request signature for replay detection
            await self.redis.setex(
                replay_key,
                self.config.timestamp_tolerance_seconds + 60,
                "1"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Replay attack check failed: {e}")
            return False

    async def validate_ip_address(
        self,
        ip_address: str,
        endpoint_id: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """Validate IP address against allowlist"""
        try:
            if not self.config.enable_ip_filtering:
                return True
            
            if not session:
                return True  # Skip validation if no session
            
            # Check IP allowlist
            from sqlalchemy import select, or_
            
            query = select(IPAllowlist).where(
                IPAllowlist.is_active == True,
                or_(
                    IPAllowlist.endpoint_id == endpoint_id,
                    IPAllowlist.endpoint_id.is_(None)  # Global allowlist
                )
            )
            
            result = await session.execute(query)
            allowlist_entries = result.scalars().all()
            
            if not allowlist_entries:
                # No allowlist configured, allow all
                return True
            
            # Check if IP is in allowlist
            client_ip = ipaddress.ip_address(ip_address)
            
            for entry in allowlist_entries:
                if entry.cidr_block:
                    # Check CIDR block
                    network = ipaddress.ip_network(entry.cidr_block, strict=False)
                    if client_ip in network:
                        return True
                else:
                    # Check exact IP match
                    if str(client_ip) == str(entry.ip_address):
                        return True
            
            logger.warning(f"IP address not in allowlist: {ip_address}")
            return False
            
        except Exception as e:
            logger.error(f"IP validation failed: {e}")
            return False

    async def validate_payload_size(self, payload: bytes) -> bool:
        """Validate webhook payload size"""
        try:
            size_mb = len(payload) / (1024 * 1024)
            
            if size_mb > self.config.max_payload_size_mb:
                logger.warning(f"Payload too large: {size_mb:.2f}MB > {self.config.max_payload_size_mb}MB")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Payload size validation failed: {e}")
            return False

    async def scan_payload_for_threats(self, payload: str) -> List[ThreatType]:
        """Scan webhook payload for security threats"""
        threats = []
        
        try:
            # Check for common injection patterns
            injection_patterns = [
                r'<script[^>]*>.*?</script>',  # XSS
                r'(union|select|insert|update|delete|drop)\s+',  # SQL injection
                r'javascript\s*:',  # JavaScript protocol
                r'data\s*:\s*text/html',  # Data URL HTML
                r'eval\s*\(',  # JavaScript eval
                r'setTimeout\s*\(',  # JavaScript setTimeout
                r'setInterval\s*\(',  # JavaScript setInterval
            ]
            
            for pattern in injection_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    threats.append(ThreatType.SUSPICIOUS_PAYLOAD)
                    break
            
            # Check payload structure
            try:
                import json
                json.loads(payload)
            except json.JSONDecodeError:
                threats.append(ThreatType.MALFORMED_REQUEST)
            
            return threats
            
        except Exception as e:
            logger.error(f"Payload threat scan failed: {e}")
            return [ThreatType.SUSPICIOUS_PAYLOAD]

    async def encrypt_payload(self, payload: str) -> str:
        """Encrypt webhook payload for secure storage"""
        try:
            if not self.config.encryption_enabled or not self._encryption_key:
                return payload
            
            fernet = Fernet(self._encryption_key)
            encrypted = fernet.encrypt(payload.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Payload encryption failed: {e}")
            return payload

    async def decrypt_payload(self, encrypted_payload: str) -> str:
        """Decrypt webhook payload"""
        try:
            if not self.config.encryption_enabled or not self._encryption_key:
                return encrypted_payload
            
            fernet = Fernet(self._encryption_key)
            encrypted_bytes = base64.b64decode(encrypted_payload.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Payload decryption failed: {e}")
            return encrypted_payload

    async def log_security_event(
        self,
        request: Request,
        endpoint_id: Optional[str] = None,
        threat_type: Optional[ThreatType] = None,
        blocked: bool = False,
        session: Optional[AsyncSession] = None
    ):
        """Log security event for audit trail"""
        try:
            if not self.config.audit_enabled or not session:
                return
            
            # Calculate payload hash if available
            payload_hash = None
            try:
                body = await request.body()
                if body:
                    payload_hash = hashlib.sha256(body).hexdigest()
            except:
                pass
            
            audit_log = WebhookSecurityAudit(
                endpoint_id=endpoint_id,
                request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
                ip_address=request.client.host if request.client else '0.0.0.0',
                user_agent=request.headers.get('User-Agent'),
                threat_type=threat_type.value if threat_type else None,
                security_level=SecurityLevel.HIGH.value,
                blocked=blocked,
                payload_hash=payload_hash,
                headers=dict(request.headers),
                metadata={}
            )
            
            session.add(audit_log)
            await session.commit()
            
            # Update metrics
            await self.metrics.increment_security_events(
                threat_type.value if threat_type else "normal",
                blocked
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def comprehensive_security_check(
        self,
        request: Request,
        payload: str,
        signature: str,
        endpoint_id: str,
        timestamp: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive security validation"""
        security_result = {
            "valid": True,
            "threats": [],
            "blocked": False,
            "details": {}
        }
        
        try:
            # 1. Validate payload size
            payload_bytes = payload.encode('utf-8')
            if not await self.validate_payload_size(payload_bytes):
                security_result["valid"] = False
                security_result["threats"].append(ThreatType.SUSPICIOUS_PAYLOAD)
                security_result["details"]["payload_size"] = "exceeded"
            
            # 2. Validate IP address
            client_ip = request.client.host if request.client else '0.0.0.0'
            if not await self.validate_ip_address(client_ip, endpoint_id, session):
                security_result["valid"] = False
                security_result["threats"].append(ThreatType.INVALID_IP)
                security_result["details"]["ip_validation"] = "failed"
            
            # 3. Validate timestamp
            if timestamp and not await self.validate_timestamp(timestamp):
                security_result["valid"] = False
                security_result["threats"].append(ThreatType.REPLAY_ATTACK)
                security_result["details"]["timestamp"] = "invalid"
            
            # 4. Check for replay attacks
            request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
            if not await self.check_replay_attack(request_id, signature, timestamp or ""):
                security_result["valid"] = False
                security_result["threats"].append(ThreatType.REPLAY_ATTACK)
                security_result["details"]["replay_check"] = "failed"
            
            # 5. Verify signature
            if not await self.verify_signature(payload, signature, endpoint_id, timestamp=timestamp):
                security_result["valid"] = False
                security_result["threats"].append(ThreatType.SIGNATURE_TAMPERING)
                security_result["details"]["signature"] = "invalid"
            
            # 6. Scan payload for threats
            if self.config.enable_payload_validation:
                payload_threats = await self.scan_payload_for_threats(payload)
                security_result["threats"].extend(payload_threats)
                if payload_threats:
                    security_result["valid"] = False
                    security_result["details"]["payload_threats"] = [t.value for t in payload_threats]
            
            # 7. Rate limiting check
            if self.config.enable_rate_limiting:
                rate_limit_key = f"webhook_rate:{client_ip}:{endpoint_id}"
                if not await self.rate_limiter.check_rate_limit(rate_limit_key, 100, 300):  # 100 requests per 5 minutes
                    security_result["valid"] = False
                    security_result["threats"].append(ThreatType.RATE_LIMIT_EXCEEDED)
                    security_result["details"]["rate_limit"] = "exceeded"
            
            # Determine if request should be blocked
            security_result["blocked"] = not security_result["valid"]
            
            # Log security event
            threat_type = security_result["threats"][0] if security_result["threats"] else None
            await self.log_security_event(
                request, endpoint_id, threat_type, security_result["blocked"], session
            )
            
            return security_result
            
        except Exception as e:
            logger.error(f"Comprehensive security check failed: {e}")
            security_result["valid"] = False
            security_result["blocked"] = True
            security_result["details"]["error"] = str(e)
            return security_result


# FastAPI Security Middleware
class WebhookSecurityMiddleware:
    """Security middleware for webhook endpoints"""
    
    def __init__(self, security_manager: WebhookSecurityManager):
        self.security_manager = security_manager
    
    async def __call__(self, request: Request, call_next):
        """Process request through security middleware"""
        try:
            # Skip security for health checks
            if request.url.path.endswith('/health'):
                return await call_next(request)
            
            # Get required headers
            signature = request.headers.get('X-IA Chéries-Signature')
            timestamp = request.headers.get('X-IA Chéries-Timestamp')
            endpoint_id = request.headers.get('X-Endpoint-ID')
            
            if not signature:
                raise HTTPException(status_code=401, detail="Missing signature header")
            
            if not endpoint_id:
                raise HTTPException(status_code=400, detail="Missing endpoint ID header")
            
            # Get request payload
            body = await request.body()
            payload = body.decode('utf-8')
            
            # Perform security check
            async with get_db_session() as session:
                security_result = await self.security_manager.comprehensive_security_check(
                    request, payload, signature, endpoint_id, timestamp, session
                )
            
            if security_result["blocked"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Security validation failed",
                        "threats": [t.value for t in security_result["threats"]],
                        "details": security_result["details"]
                    }
                )
            
            # Continue processing if security check passed
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(status_code=500, detail="Security validation error")


# Dependency for getting security manager
security_manager = WebhookSecurityManager()

async def get_security_manager() -> WebhookSecurityManager:
    """Dependency to get security manager instance"""
    return security_manager


# Example usage in FastAPI app
def create_secure_webhook_app() -> FastAPI:
    """Create FastAPI app with webhook security"""
    from fastapi import FastAPI
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    
    app = FastAPI(
        title="Secure Webhook Handler",
        description="Enterprise webhook handler with advanced security",
        version="1.0.0"
    )
    
    # Add security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.middleware("http")(WebhookSecurityMiddleware(security_manager))
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_secure_webhook_app()
    uvicorn.run(app, host="0.0.0.0", port=8002)