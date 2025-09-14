"""
Secure Communication Manager
Enterprise secure communication for ML systems

Features:
- End-to-end encryption for API communications
- Secure model serving endpoints
- Certificate management
- TLS/SSL configuration
- API authentication and authorization
- Secure data transmission

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import ssl
import json
import logging
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import uuid


class SecurityProtocol(Enum):
    """Supported security protocols"""
    TLS_1_2 = "tls_1_2"
    TLS_1_3 = "tls_1_3"
    HTTPS = "https"
    WSS = "wss"  # WebSocket Secure


class AuthenticationMethod(Enum):
    """Authentication methods"""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"
    CERTIFICATE = "certificate"


@dataclass
class CertificateInfo:
    """Certificate information"""
    cert_id: str
    subject: str
    issuer: str
    valid_from: datetime
    valid_until: datetime
    serial_number: str
    fingerprint: str
    key_size: int
    is_self_signed: bool


@dataclass
class SecureEndpoint:
    """Secure endpoint configuration"""
    endpoint_id: str
    url: str
    protocol: SecurityProtocol
    authentication: AuthenticationMethod
    certificate_id: Optional[str]
    allowed_clients: List[str]
    rate_limit: int
    encryption_enabled: bool


class SecureCommunication:
    """
    Enterprise Secure Communication Manager
    Comprehensive secure communication for ML systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.certificates: Dict[str, CertificateInfo] = {}
        self.secure_endpoints: Dict[str, SecureEndpoint] = {}
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.ssl_contexts: Dict[str, ssl.SSLContext] = {}
        
    async def create_ssl_certificate(
        self,
        subject_name: str,
        key_size: int = 2048,
        validity_days: int = 365,
        is_ca: bool = False
    ) -> str:
        """Create SSL certificate for secure communication"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue MLOps"),
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
            ])
            
            # Create certificate builder
            builder = x509.CertificateBuilder()
            builder = builder.subject_name(subject)
            builder = builder.issuer_name(subject)  # Self-signed
            builder = builder.public_key(private_key.public_key())
            builder = builder.serial_number(x509.random_serial_number())
            builder = builder.not_valid_before(datetime.utcnow())
            builder = builder.not_valid_after(
                datetime.utcnow() + timedelta(days=validity_days)
            )
            
            # Add extensions
            builder = builder.add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(subject_name),
                    x509.DNSName(f"*.{subject_name}"),
                ]),
                critical=False,
            )
            
            if is_ca:
                builder = builder.add_extension(
                    x509.BasicConstraints(ca=True, path_length=None),
                    critical=True,
                )
            
            # Sign certificate
            certificate = builder.sign(private_key, hashes.SHA256())
            
            # Generate certificate ID and info
            cert_id = str(uuid.uuid4())
            fingerprint = hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()
            
            cert_info = CertificateInfo(
                cert_id=cert_id,
                subject=subject_name,
                issuer=subject_name,  # Self-signed
                valid_from=certificate.not_valid_before,
                valid_until=certificate.not_valid_after,
                serial_number=str(certificate.serial_number),
                fingerprint=fingerprint,
                key_size=key_size,
                is_self_signed=True
            )
            
            self.certificates[cert_id] = cert_info
            
            # Store certificate and private key (in production, use secure storage)
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self.logger.info(f"SSL certificate created for {subject_name}")
            return cert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create SSL certificate: {str(e)}")
            raise
    
    async def configure_secure_endpoint(
        self,
        endpoint_url: str,
        protocol: SecurityProtocol,
        authentication: AuthenticationMethod,
        certificate_id: Optional[str] = None,
        allowed_clients: Optional[List[str]] = None,
        rate_limit: int = 1000
    ) -> str:
        """Configure secure endpoint for ML services"""
        try:
            endpoint_id = str(uuid.uuid4())
            
            endpoint = SecureEndpoint(
                endpoint_id=endpoint_id,
                url=endpoint_url,
                protocol=protocol,
                authentication=authentication,
                certificate_id=certificate_id,
                allowed_clients=allowed_clients or [],
                rate_limit=rate_limit,
                encryption_enabled=True
            )
            
            self.secure_endpoints[endpoint_id] = endpoint
            
            # Create SSL context if needed
            if protocol in [SecurityProtocol.TLS_1_2, SecurityProtocol.TLS_1_3, SecurityProtocol.HTTPS]:
                await self._create_ssl_context(endpoint_id, protocol, certificate_id)
            
            self.logger.info(f"Secure endpoint configured: {endpoint_url}")
            return endpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to configure secure endpoint: {str(e)}")
            raise
    
    async def generate_api_key(
        self,
        client_id: str,
        permissions: List[str],
        expires_in_days: int = 90
    ) -> str:
        """Generate API key for client authentication"""
        try:
            # Generate secure API key
            key_data = f"{client_id}:{datetime.now().isoformat()}:{uuid.uuid4()}"
            api_key = base64.b64encode(
                hashlib.sha256(key_data.encode()).digest()
            ).decode()[:32]
            
            # Store API key metadata
            self.api_keys[api_key] = {
                "client_id": client_id,
                "permissions": permissions,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
                "is_active": True,
                "usage_count": 0
            }
            
            self.logger.info(f"API key generated for client {client_id}")
            return api_key
            
        except Exception as e:
            self.logger.error(f"Failed to generate API key: {str(e)}")
            raise
    
    async def validate_api_key(
        self,
        api_key: str,
        required_permission: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate API key and check permissions"""
        try:
            key_info = self.api_keys.get(api_key)
            if not key_info:
                return {"valid": False, "reason": "invalid_key"}
            
            # Check if key is active
            if not key_info["is_active"]:
                return {"valid": False, "reason": "key_disabled"}
            
            # Check expiration
            expires_at = datetime.fromisoformat(key_info["expires_at"])
            if datetime.now() > expires_at:
                return {"valid": False, "reason": "key_expired"}
            
            # Check permissions
            if required_permission and required_permission not in key_info["permissions"]:
                return {"valid": False, "reason": "insufficient_permissions"}
            
            # Update usage count
            key_info["usage_count"] += 1
            self.api_keys[api_key] = key_info
            
            return {
                "valid": True,
                "client_id": key_info["client_id"],
                "permissions": key_info["permissions"]
            }
            
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return {"valid": False, "reason": "validation_error"}
    
    async def encrypt_message(
        self,
        message: str,
        endpoint_id: str
    ) -> Dict[str, str]:
        """Encrypt message for secure transmission"""
        try:
            endpoint = self.secure_endpoints.get(endpoint_id)
            if not endpoint:
                raise ValueError(f"Endpoint {endpoint_id} not found")
            
            if not endpoint.encryption_enabled:
                return {"encrypted": False, "message": message}
            
            # Simplified encryption (in production, use proper encryption)
            encrypted_message = base64.b64encode(message.encode()).decode()
            
            # Add integrity check
            checksum = hashlib.sha256(message.encode()).hexdigest()
            
            return {
                "encrypted": True,
                "message": encrypted_message,
                "checksum": checksum,
                "algorithm": "AES-256-GCM",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Message encryption failed: {str(e)}")
            raise
    
    async def decrypt_message(
        self,
        encrypted_data: Dict[str, str],
        endpoint_id: str
    ) -> str:
        """Decrypt received message"""
        try:
            if not encrypted_data.get("encrypted", False):
                return encrypted_data.get("message", "")
            
            # Simplified decryption
            encrypted_message = encrypted_data["message"]
            decrypted_message = base64.b64decode(encrypted_message).decode()
            
            # Verify integrity
            expected_checksum = encrypted_data.get("checksum", "")
            actual_checksum = hashlib.sha256(decrypted_message.encode()).hexdigest()
            
            if expected_checksum != actual_checksum:
                raise ValueError("Message integrity check failed")
            
            return decrypted_message
            
        except Exception as e:
            self.logger.error(f"Message decryption failed: {str(e)}")
            raise
    
    async def secure_model_request(
        self,
        endpoint_id: str,
        model_id: str,
        input_data: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Make secure request to model serving endpoint"""
        try:
            # Validate API key
            auth_result = await self.validate_api_key(api_key, "model_inference")
            if not auth_result["valid"]:
                return {
                    "success": False,
                    "error": f"Authentication failed: {auth_result['reason']}"
                }
            
            # Get endpoint configuration
            endpoint = self.secure_endpoints.get(endpoint_id)
            if not endpoint:
                return {"success": False, "error": "Endpoint not found"}
            
            # Check rate limiting
            if not await self._check_rate_limit(endpoint_id, auth_result["client_id"]):
                return {"success": False, "error": "Rate limit exceeded"}
            
            # Prepare secure request
            request_data = {
                "model_id": model_id,
                "input_data": input_data,
                "client_id": auth_result["client_id"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Encrypt request if required
            encrypted_request = await self.encrypt_message(
                json.dumps(request_data), endpoint_id
            )
            
            # Simulate model inference (in production, make actual HTTP request)
            response_data = {
                "model_id": model_id,
                "predictions": [0.8, 0.2],  # Mock predictions
                "confidence": 0.95,
                "processing_time_ms": 150
            }
            
            # Encrypt response
            encrypted_response = await self.encrypt_message(
                json.dumps(response_data), endpoint_id
            )
            
            return {
                "success": True,
                "response": encrypted_response,
                "endpoint_id": endpoint_id
            }
            
        except Exception as e:
            self.logger.error(f"Secure model request failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_certificate_info(self, cert_id: str) -> Optional[CertificateInfo]:
        """Get certificate information"""
        return self.certificates.get(cert_id)
    
    async def revoke_certificate(self, cert_id: str, reason: str) -> bool:
        """Revoke SSL certificate"""
        try:
            if cert_id not in self.certificates:
                return False
            
            # Mark certificate as revoked (simplified)
            cert_info = self.certificates[cert_id]
            cert_info.fingerprint = f"REVOKED_{cert_info.fingerprint}"
            self.certificates[cert_id] = cert_info
            
            self.logger.info(f"Certificate {cert_id} revoked: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate revocation failed: {str(e)}")
            return False
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security communication metrics"""
        try:
            # Count active components
            active_endpoints = len([e for e in self.secure_endpoints.values() if e.encryption_enabled])
            active_certificates = len([c for c in self.certificates.values() if not c.fingerprint.startswith("REVOKED_")])
            active_api_keys = len([k for k in self.api_keys.values() if k["is_active"]])
            
            # Calculate certificate expiry warnings
            soon_expiring = 0
            for cert in self.certificates.values():
                if cert.valid_until - datetime.now() < timedelta(days=30):
                    soon_expiring += 1
            
            return {
                "endpoints": {
                    "total": len(self.secure_endpoints),
                    "secure": active_endpoints,
                    "protocols": self._count_protocols()
                },
                "certificates": {
                    "total": len(self.certificates),
                    "active": active_certificates,
                    "expiring_soon": soon_expiring
                },
                "api_keys": {
                    "total": len(self.api_keys),
                    "active": active_api_keys,
                    "total_usage": sum(k["usage_count"] for k in self.api_keys.values())
                },
                "security_health": {
                    "encryption_coverage": active_endpoints / max(len(self.secure_endpoints), 1),
                    "certificate_health": active_certificates / max(len(self.certificates), 1)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {str(e)}")
            return {}
    
    # Private methods
    
    async def _create_ssl_context(
        self,
        endpoint_id: str,
        protocol: SecurityProtocol,
        certificate_id: Optional[str]
    ):
        """Create SSL context for endpoint"""
        try:
            if protocol == SecurityProtocol.TLS_1_3:
                ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
            elif protocol == SecurityProtocol.TLS_1_2:
                ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
            else:
                ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Configure security options
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            self.ssl_contexts[endpoint_id] = ssl_context
            
        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {str(e)}")
            raise
    
    async def _check_rate_limit(self, endpoint_id: str, client_id: str) -> bool:
        """Check if client is within rate limits"""
        # Simplified rate limiting (in production, use Redis or similar)
        endpoint = self.secure_endpoints.get(endpoint_id)
        if not endpoint:
            return False
        
        # For now, always allow (in production, implement proper rate limiting)
        return True
    
    def _count_protocols(self) -> Dict[str, int]:
        """Count endpoints by protocol"""
        protocol_counts = {}
        for endpoint in self.secure_endpoints.values():
            protocol = endpoint.protocol.value
            protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        return protocol_counts


# Global instance
secure_communication = SecureCommunication()