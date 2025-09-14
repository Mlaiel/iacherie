"""
mTLS Service Communication Manager - Enterprise Security
=======================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Security Engineer + Microservices Architect  
**Module**: Enterprise Security & Service Mesh
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Zero-trust service-to-service communication with mutual TLS authentication,
certificate management, and secure service mesh integration.
"""

import asyncio
import ssl
import aiohttp
import certifi
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import base64


class CertificateStatus(Enum):
    """Certificate status states"""
    VALID = "valid"
    EXPIRING = "expiring" 
    EXPIRED = "expired"
    REVOKED = "revoked"


class ServiceTrustLevel(Enum):
    """Service trust levels for mTLS"""
    UNTRUSTED = 0
    BASIC = 1
    VERIFIED = 2
    ENTERPRISE = 3


@dataclass
class ServiceCertificate:
    """Service certificate information"""
    service_name: str
    certificate_pem: str
    private_key_pem: str
    ca_certificate_pem: str
    expiry_date: datetime
    status: CertificateStatus = CertificateStatus.VALID
    trust_level: ServiceTrustLevel = ServiceTrustLevel.BASIC
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_rotated: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class mTLSConnection:
    """mTLS connection information"""
    connection_id: str
    source_service: str
    target_service: str
    established_at: datetime
    last_used: datetime
    request_count: int = 0
    error_count: int = 0
    status: str = "active"
    ssl_context: Optional[ssl.SSLContext] = None


class mTLSServiceManager:
    """Enterprise mTLS Service Communication Manager"""
    
    def __init__(self, 
                 ca_cert_path: Optional[str] = None,
                 service_name: str = "ainflue-service",
                 environment: str = "production"):
        """Initialize mTLS Service Manager"""
        
        self.ca_cert_path = ca_cert_path or "/etc/ssl/certs/ainflue-ca.pem"
        self.service_name = service_name
        self.environment = environment
        
        # Certificate storage
        self.certificates: Dict[str, ServiceCertificate] = {}
        self.trusted_services: Dict[str, ServiceTrustLevel] = {}
        self.active_connections: Dict[str, mTLSConnection] = {}
        
        # Configuration
        self.cert_rotation_days = 30  # Rotate certificates every 30 days
        self.connection_timeout = 30
        self.trust_store_path = "/etc/ssl/certs/ainflue-trust-store"
        
        # Monitoring
        self.connection_metrics = {
            "successful_handshakes": 0,
            "failed_handshakes": 0,
            "certificate_validations": 0,
            "trust_violations": 0
        }
        
        # Logger setup
        self.logger = logging.getLogger(f"mtls_manager.{service_name}")
        self.logger.setLevel(logging.INFO)
        
        # SSL contexts cache
        self.ssl_contexts: Dict[str, ssl.SSLContext] = {}
        
        self.logger.info(f"mTLS Service Manager initialized for {service_name}")

    async def initialize(self):
        """Initialize mTLS manager with certificates and trust store"""
        
        try:
            # Load CA certificate
            await self._load_ca_certificate()
            
            # Generate service certificate if not exists
            await self._ensure_service_certificate()
            
            # Load trusted services configuration
            await self._load_trusted_services()
            
            # Start certificate monitoring
            asyncio.create_task(self._monitor_certificates())
            
            # Start connection cleanup
            asyncio.create_task(self._cleanup_connections())
            
            self.logger.info("mTLS Service Manager initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mTLS manager: {e}")
            raise

    async def _load_ca_certificate(self):
        """Load Certificate Authority certificate"""
        
        try:
            if os.path.exists(self.ca_cert_path):
                with open(self.ca_cert_path, 'r') as f:
                    self.ca_certificate = f.read()
                self.logger.info("CA certificate loaded successfully")
            else:
                # Generate self-signed CA for testing
                await self._generate_ca_certificate()
                
        except Exception as e:
            self.logger.error(f"Failed to load CA certificate: {e}")
            raise

    async def _generate_ca_certificate(self):
        """Generate self-signed CA certificate for testing"""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Enterprise"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Ainflue"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue Platform"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Ainflue Root CA"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Save CA certificate
        os.makedirs(os.path.dirname(self.ca_cert_path), exist_ok=True)
        
        with open(self.ca_cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Save CA private key securely
        ca_key_path = self.ca_cert_path.replace('.pem', '-key.pem')
        with open(ca_key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Set secure permissions
        os.chmod(self.ca_cert_path, 0o644)
        os.chmod(ca_key_path, 0o600)
        
        self.ca_certificate = cert.public_bytes(serialization.Encoding.PEM).decode()
        self.logger.info("Generated new CA certificate")

    async def _ensure_service_certificate(self):
        """Ensure service has valid certificate"""
        
        cert_path = f"/etc/ssl/certs/{self.service_name}.pem"
        key_path = f"/etc/ssl/private/{self.service_name}-key.pem"
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            # Load existing certificate
            with open(cert_path, 'r') as f:
                cert_pem = f.read()
            with open(key_path, 'r') as f:
                key_pem = f.read()
            
            # Validate certificate expiry
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
            if cert.not_valid_after > datetime.utcnow() + timedelta(days=7):
                # Certificate is valid for more than 7 days
                self.certificates[self.service_name] = ServiceCertificate(
                    service_name=self.service_name,
                    certificate_pem=cert_pem,
                    private_key_pem=key_pem,
                    ca_certificate_pem=self.ca_certificate,
                    expiry_date=cert.not_valid_after,
                    trust_level=ServiceTrustLevel.ENTERPRISE
                )
                return
        
        # Generate new certificate
        await self._generate_service_certificate()

    async def _generate_service_certificate(self):
        """Generate new service certificate"""
        
        # Load CA private key
        ca_key_path = self.ca_cert_path.replace('.pem', '-key.pem')
        with open(ca_key_path, 'rb') as f:
            ca_private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
        
        # Load CA certificate
        ca_cert = x509.load_pem_x509_certificate(self.ca_certificate.encode())
        
        # Generate service private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate service certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Enterprise"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Ainflue"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue Platform"),
            x509.NameAttribute(NameOID.COMMON_NAME, self.service_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.cert_rotation_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(self.service_name),
                x509.DNSName(f"{self.service_name}.{self.environment}"),
                x509.DNSName(f"{self.service_name}.ainflue.svc.cluster.local"),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).sign(ca_private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        os.makedirs("/etc/ssl/certs", exist_ok=True)
        os.makedirs("/etc/ssl/private", exist_ok=True)
        
        cert_path = f"/etc/ssl/certs/{self.service_name}.pem"
        key_path = f"/etc/ssl/private/{self.service_name}-key.pem"
        
        with open(cert_path, 'w') as f:
            f.write(cert_pem)
        with open(key_path, 'w') as f:
            f.write(key_pem)
        
        # Set secure permissions
        os.chmod(cert_path, 0o644)
        os.chmod(key_path, 0o600)
        
        # Store certificate info
        self.certificates[self.service_name] = ServiceCertificate(
            service_name=self.service_name,
            certificate_pem=cert_pem,
            private_key_pem=key_pem,
            ca_certificate_pem=self.ca_certificate,
            expiry_date=cert.not_valid_after,
            trust_level=ServiceTrustLevel.ENTERPRISE
        )
        
        self.logger.info(f"Generated new certificate for {self.service_name}")

    async def _load_trusted_services(self):
        """Load trusted services configuration"""
        
        trusted_services_config = {
            "ainflue-api": ServiceTrustLevel.ENTERPRISE,
            "ainflue-auth": ServiceTrustLevel.ENTERPRISE,
            "ainflue-content": ServiceTrustLevel.ENTERPRISE,
            "ainflue-media": ServiceTrustLevel.ENTERPRISE,
            "ainflue-analytics": ServiceTrustLevel.VERIFIED,
            "ainflue-notification": ServiceTrustLevel.VERIFIED,
            "ainflue-monitoring": ServiceTrustLevel.BASIC,
        }
        
        self.trusted_services.update(trusted_services_config)
        self.logger.info(f"Loaded {len(self.trusted_services)} trusted services")

    async def create_secure_client_session(self, target_service: str) -> aiohttp.ClientSession:
        """Create mTLS-enabled client session for service communication"""
        
        try:
            # Check if target service is trusted
            if target_service not in self.trusted_services:
                raise ValueError(f"Service {target_service} is not in trusted services list")
            
            # Get or create SSL context
            ssl_context = await self._get_ssl_context(target_service)
            
            # Create connector with mTLS
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                timeout=aiohttp.ClientTimeout(total=self.connection_timeout),
                limit=100,  # Connection pool limit
                limit_per_host=20
            )
            
            # Create session
            session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "User-Agent": f"Ainflue-mTLS-Client/{self.service_name}",
                    "X-Service-Name": self.service_name,
                    "X-Trust-Level": self.trusted_services[target_service].name
                }
            )
            
            # Track connection
            connection_id = f"{self.service_name}-{target_service}-{int(datetime.utcnow().timestamp())}"
            self.active_connections[connection_id] = mTLSConnection(
                connection_id=connection_id,
                source_service=self.service_name,
                target_service=target_service,
                established_at=datetime.utcnow(),
                last_used=datetime.utcnow(),
                ssl_context=ssl_context
            )
            
            self.connection_metrics["successful_handshakes"] += 1
            self.logger.info(f"Created secure mTLS session to {target_service}")
            
            return session
            
        except Exception as e:
            self.connection_metrics["failed_handshakes"] += 1
            self.logger.error(f"Failed to create secure session to {target_service}: {e}")
            raise

    async def _get_ssl_context(self, target_service: str) -> ssl.SSLContext:
        """Get or create SSL context for target service"""
        
        context_key = f"{self.service_name}-{target_service}"
        
        if context_key in self.ssl_contexts:
            return self.ssl_contexts[context_key]
        
        # Create new SSL context
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Load CA certificate
        context.load_verify_locations(cadata=self.ca_certificate)
        
        # Load client certificate and key
        service_cert = self.certificates[self.service_name]
        context.load_cert_chain(
            certfile=f"/etc/ssl/certs/{self.service_name}.pem",
            keyfile=f"/etc/ssl/private/{self.service_name}-key.pem"
        )
        
        # Configure security settings
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_3  # Force TLS 1.3
        
        # Cache context
        self.ssl_contexts[context_key] = context
        
        return context

    async def verify_peer_certificate(self, peer_cert_pem: str, service_name: str) -> bool:
        """Verify peer service certificate"""
        
        try:
            # Load peer certificate
            peer_cert = x509.load_pem_x509_certificate(peer_cert_pem.encode())
            
            # Load CA certificate
            ca_cert = x509.load_pem_x509_certificate(self.ca_certificate.encode())
            
            # Verify certificate chain
            try:
                # Basic validation
                if peer_cert.not_valid_after < datetime.utcnow():
                    self.logger.warning(f"Peer certificate for {service_name} has expired")
                    return False
                
                if peer_cert.not_valid_before > datetime.utcnow():
                    self.logger.warning(f"Peer certificate for {service_name} is not yet valid")
                    return False
                
                # Verify issuer
                if peer_cert.issuer != ca_cert.subject:
                    self.logger.warning(f"Peer certificate for {service_name} has invalid issuer")
                    return False
                
                # Verify service name in certificate
                san_extension = peer_cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                ).value
                
                dns_names = [name.value for name in san_extension if isinstance(name, x509.DNSName)]
                if service_name not in dns_names:
                    self.logger.warning(f"Service name {service_name} not found in certificate SAN")
                    return False
                
                self.connection_metrics["certificate_validations"] += 1
                self.logger.debug(f"Successfully verified certificate for {service_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Certificate verification failed for {service_name}: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying peer certificate: {e}")
            return False

    async def secure_request(self, 
                           target_service: str, 
                           method: str, 
                           endpoint: str, 
                           **kwargs) -> aiohttp.ClientResponse:
        """Make secure mTLS request to target service"""
        
        try:
            # Check trust level
            trust_level = self.trusted_services.get(target_service, ServiceTrustLevel.UNTRUSTED)
            if trust_level == ServiceTrustLevel.UNTRUSTED:
                raise ValueError(f"Cannot communicate with untrusted service: {target_service}")
            
            # Create secure session
            async with await self.create_secure_client_session(target_service) as session:
                
                # Construct URL
                url = f"https://{target_service}.{self.environment}:8443{endpoint}"
                
                # Add security headers
                headers = kwargs.get('headers', {})
                headers.update({
                    "X-Client-Certificate": base64.b64encode(
                        self.certificates[self.service_name].certificate_pem.encode()
                    ).decode(),
                    "X-Trust-Level": trust_level.name,
                    "X-Request-ID": f"{self.service_name}-{int(datetime.utcnow().timestamp())}"
                })
                kwargs['headers'] = headers
                
                # Make request
                start_time = datetime.utcnow()
                async with session.request(method, url, **kwargs) as response:
                    
                    # Update connection metrics
                    connection = next(
                        (conn for conn in self.active_connections.values() 
                         if conn.target_service == target_service), 
                        None
                    )
                    
                    if connection:
                        connection.last_used = datetime.utcnow()
                        connection.request_count += 1
                        
                        if response.status >= 400:
                            connection.error_count += 1
                    
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    self.logger.debug(
                        f"mTLS request to {target_service}{endpoint}: "
                        f"{response.status} in {duration:.3f}s"
                    )
                    
                    return response
                    
        except Exception as e:
            self.logger.error(f"mTLS request failed to {target_service}{endpoint}: {e}")
            raise

    async def _monitor_certificates(self):
        """Monitor certificate expiry and trigger rotation"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                for service_name, cert in self.certificates.items():
                    days_until_expiry = (cert.expiry_date - datetime.utcnow()).days
                    
                    if days_until_expiry <= 7:
                        cert.status = CertificateStatus.EXPIRING
                        self.logger.warning(
                            f"Certificate for {service_name} expires in {days_until_expiry} days"
                        )
                        
                        # Auto-rotate if less than 3 days
                        if days_until_expiry <= 3:
                            await self._rotate_certificate(service_name)
                    
                    elif days_until_expiry <= 0:
                        cert.status = CertificateStatus.EXPIRED
                        self.logger.error(f"Certificate for {service_name} has expired")
                
            except Exception as e:
                self.logger.error(f"Error monitoring certificates: {e}")

    async def _rotate_certificate(self, service_name: str):
        """Rotate service certificate"""
        
        try:
            self.logger.info(f"Starting certificate rotation for {service_name}")
            
            # Generate new certificate
            await self._generate_service_certificate()
            
            # Clear SSL context cache
            self.ssl_contexts.clear()
            
            # Update certificate info
            if service_name in self.certificates:
                self.certificates[service_name].last_rotated = datetime.utcnow()
                self.certificates[service_name].status = CertificateStatus.VALID
            
            self.logger.info(f"Certificate rotation completed for {service_name}")
            
        except Exception as e:
            self.logger.error(f"Certificate rotation failed for {service_name}: {e}")

    async def _cleanup_connections(self):
        """Clean up inactive connections"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                
                cutoff_time = datetime.utcnow() - timedelta(minutes=10)
                inactive_connections = [
                    conn_id for conn_id, conn in self.active_connections.items()
                    if conn.last_used < cutoff_time
                ]
                
                for conn_id in inactive_connections:
                    del self.active_connections[conn_id]
                
                if inactive_connections:
                    self.logger.debug(f"Cleaned up {len(inactive_connections)} inactive connections")
                
            except Exception as e:
                self.logger.error(f"Error cleaning up connections: {e}")

    async def get_certificate_status(self) -> Dict[str, Any]:
        """Get certificate status information"""
        
        status = {}
        for service_name, cert in self.certificates.items():
            days_until_expiry = (cert.expiry_date - datetime.utcnow()).days
            
            status[service_name] = {
                "status": cert.status.value,
                "trust_level": cert.trust_level.name,
                "days_until_expiry": days_until_expiry,
                "created_at": cert.created_at.isoformat(),
                "last_rotated": cert.last_rotated.isoformat() if cert.last_rotated else None
            }
        
        return status

    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Get connection metrics"""
        
        active_count = len(self.active_connections)
        total_requests = sum(conn.request_count for conn in self.active_connections.values())
        total_errors = sum(conn.error_count for conn in self.active_connections.values())
        
        return {
            "active_connections": active_count,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_requests, 1),
            "handshake_metrics": self.connection_metrics,
            "trusted_services": len(self.trusted_services)
        }

    async def shutdown(self):
        """Shutdown mTLS manager gracefully"""
        
        # Close all active connections
        for connection in self.active_connections.values():
            if connection.ssl_context:
                connection.status = "closed"
        
        self.active_connections.clear()
        self.ssl_contexts.clear()
        
        self.logger.info("mTLS Service Manager shutdown completed")


# Example usage
async def main():
    """Example usage of mTLS Service Manager"""
    
    manager = mTLSServiceManager(service_name="ainflue-api")
    await manager.initialize()
    
    try:
        # Make secure request to another service
        response = await manager.secure_request(
            target_service="ainflue-content",
            method="GET",
            endpoint="/api/v1/content/health"
        )
        
        print(f"Response status: {response.status}")
        
        # Get certificate status
        cert_status = await manager.get_certificate_status()
        print(f"Certificate status: {cert_status}")
        
        # Get connection metrics
        metrics = await manager.get_connection_metrics()
        print(f"Connection metrics: {metrics}")
        
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())