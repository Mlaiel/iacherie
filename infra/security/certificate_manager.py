"""
Certificate Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Certificate Manager

Enterprise certificate management system for infrastructure security.
Handles SSL/TLS certificates, automatic renewal, and PKI infrastructure.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ssl
import cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CertificateType(Enum):
    """Certificate type options."""
    SSL_TLS = "ssl_tls"
    CLIENT_AUTH = "client_auth"
    CODE_SIGNING = "code_signing"
    EMAIL = "email"
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"

class CertificateStatus(Enum):
    """Certificate status options."""
    VALID = "valid"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    REVOKED = "revoked"
    INVALID = "invalid"

@dataclass
class CertificateInfo:
    """Certificate information."""
    name: str
    type: CertificateType
    subject: str
    issuer: str
    serial_number: str
    not_before: datetime
    not_after: datetime
    fingerprint: str
    key_size: int
    algorithm: str
    san_domains: List[str] = field(default_factory=list)
    status: CertificateStatus = CertificateStatus.VALID
    auto_renew: bool = True
    renewal_threshold_days: int = 30

@dataclass
class CertificateRequest:
    """Certificate signing request."""
    common_name: str
    organization: str
    organizational_unit: str
    locality: str
    state: str
    country: str
    san_domains: List[str] = field(default_factory=list)
    key_size: int = 2048
    validity_days: int = 365
    certificate_type: CertificateType = CertificateType.SSL_TLS

class CertificateManager:
    """
    Enterprise certificate management system.
    
    Provides comprehensive SSL/TLS certificate management, automatic renewal,
    PKI infrastructure, and certificate lifecycle management.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize certificate manager."""
        self.config = config or {}
        self.certificates: Dict[str, CertificateInfo] = {}
        self.certificate_files: Dict[str, Dict[str, str]] = {}
        
        # Configuration paths
        self.cert_dir = Path(self.config.get("cert_dir", "./certificates"))
        self.ca_dir = self.cert_dir / "ca"
        self.certs_dir = self.cert_dir / "certs"
        self.keys_dir = self.cert_dir / "private"
        
        # Certificate authority settings
        self.ca_config = self.config.get("ca", {
            "organization": "Ainflue Platform",
            "organizational_unit": "Infrastructure",
            "locality": "San Francisco",
            "state": "California",
            "country": "US"
        })
        
        # Auto-renewal settings
        self.enable_auto_renewal = self.config.get("enable_auto_renewal", True)
        self.renewal_check_interval = self.config.get("renewal_check_interval", 3600)  # 1 hour
        self.default_renewal_threshold = self.config.get("default_renewal_threshold", 30)  # 30 days
        
        # ACME/Let's Encrypt settings
        self.acme_config = self.config.get("acme", {
            "directory_url": "https://acme-v02.api.letsencrypt.org/directory",
            "contact_email": "admin@ainflue.com",
            "key_size": 2048
        })
        
        # Certificate transparency logging
        self.enable_ct_logging = self.config.get("enable_ct_logging", True)
        
        # Create directories
        self._create_directories()
        
        # Start auto-renewal task
        if self.enable_auto_renewal:
            asyncio.create_task(self._auto_renewal_loop())
        
        logger.info("CertificateManager initialized")
    
    def _create_directories(self) -> None:
        """Create certificate directories."""
        try:
            self.cert_dir.mkdir(parents=True, exist_ok=True)
            self.ca_dir.mkdir(parents=True, exist_ok=True)
            self.certs_dir.mkdir(parents=True, exist_ok=True)
            self.keys_dir.mkdir(parents=True, exist_ok=True)
            
            # Set restrictive permissions on private key directory
            self.keys_dir.chmod(0o700)
            
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            raise
    
    async def create_root_ca(self, ca_name: str = "Ainflue Root CA") -> bool:
        """Create root certificate authority."""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, self.ca_config["country"]),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.ca_config["state"]),
                x509.NameAttribute(NameOID.LOCALITY_NAME, self.ca_config["locality"]),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.ca_config["organization"]),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.ca_config["organizational_unit"]),
                x509.NameAttribute(NameOID.COMMON_NAME, ca_name),
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
                x509.SubjectAlternativeName([]),
                critical=False,
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            ca_cert_path = self.ca_dir / f"{ca_name.lower().replace(' ', '_')}.crt"
            ca_key_path = self.keys_dir / f"{ca_name.lower().replace(' ', '_')}.key"
            
            with open(ca_cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(ca_key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Set restrictive permissions
            ca_key_path.chmod(0o600)
            
            # Store certificate info
            cert_info = CertificateInfo(
                name=ca_name,
                type=CertificateType.ROOT_CA,
                subject=str(subject),
                issuer=str(issuer),
                serial_number=str(cert.serial_number),
                not_before=cert.not_valid_before,
                not_after=cert.not_valid_after,
                fingerprint=cert.fingerprint(hashes.SHA256()).hex(),
                key_size=4096,
                algorithm="RSA",
                auto_renew=False  # Root CA typically doesn't auto-renew
            )
            
            self.certificates[ca_name] = cert_info
            self.certificate_files[ca_name] = {
                "cert_path": str(ca_cert_path),
                "key_path": str(ca_key_path)
            }
            
            logger.info(f"Created root CA: {ca_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create root CA: {str(e)}")
            return False
    
    async def generate_certificate(self, cert_request: CertificateRequest) -> Optional[str]:
        """Generate a new certificate."""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=cert_request.key_size,
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, cert_request.country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, cert_request.state),
                x509.NameAttribute(NameOID.LOCALITY_NAME, cert_request.locality),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_request.organization),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, cert_request.organizational_unit),
                x509.NameAttribute(NameOID.COMMON_NAME, cert_request.common_name),
            ])
            
            # For self-signed certificates (in absence of CA)
            issuer = subject
            
            # Create certificate builder
            builder = x509.CertificateBuilder().subject_name(
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
                datetime.utcnow() + timedelta(days=cert_request.validity_days)
            )
            
            # Add Subject Alternative Names
            san_list = []
            for domain in cert_request.san_domains:
                san_list.append(x509.DNSName(domain))
            
            if san_list:
                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )
            
            # Add appropriate extensions based on certificate type
            if cert_request.certificate_type == CertificateType.SSL_TLS:
                builder = builder.add_extension(
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
                )
            
            # Sign the certificate
            cert = builder.sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_name = cert_request.common_name.replace("*", "wildcard").replace(".", "_")
            cert_path = self.certs_dir / f"{cert_name}.crt"
            key_path = self.keys_dir / f"{cert_name}.key"
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Set restrictive permissions
            key_path.chmod(0o600)
            
            # Store certificate info
            cert_info = CertificateInfo(
                name=cert_request.common_name,
                type=cert_request.certificate_type,
                subject=str(subject),
                issuer=str(issuer),
                serial_number=str(cert.serial_number),
                not_before=cert.not_valid_before,
                not_after=cert.not_valid_after,
                fingerprint=cert.fingerprint(hashes.SHA256()).hex(),
                key_size=cert_request.key_size,
                algorithm="RSA",
                san_domains=cert_request.san_domains,
                auto_renew=True,
                renewal_threshold_days=self.default_renewal_threshold
            )
            
            self.certificates[cert_request.common_name] = cert_info
            self.certificate_files[cert_request.common_name] = {
                "cert_path": str(cert_path),
                "key_path": str(key_path)
            }
            
            logger.info(f"Generated certificate: {cert_request.common_name}")
            return cert_request.common_name
            
        except Exception as e:
            logger.error(f"Failed to generate certificate: {str(e)}")
            return None
    
    async def import_certificate(self, name: str, cert_path: str, key_path: str = None) -> bool:
        """Import an existing certificate."""
        try:
            # Read certificate
            with open(cert_path, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract certificate information
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            
            # Extract SAN domains
            san_domains = []
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                san_domains = [name.value for name in san_ext.value if isinstance(name, x509.DNSName)]
            except x509.ExtensionNotFound:
                pass
            
            # Determine certificate type
            cert_type = CertificateType.SSL_TLS  # Default
            try:
                key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
                if key_usage.value.key_cert_sign:
                    cert_type = CertificateType.ROOT_CA if cert.subject == cert.issuer else CertificateType.INTERMEDIATE_CA
            except x509.ExtensionNotFound:
                pass
            
            # Store certificate info
            cert_info = CertificateInfo(
                name=name,
                type=cert_type,
                subject=subject,
                issuer=issuer,
                serial_number=str(cert.serial_number),
                not_before=cert.not_valid_before,
                not_after=cert.not_valid_after,
                fingerprint=cert.fingerprint(hashes.SHA256()).hex(),
                key_size=cert.public_key().key_size,
                algorithm="RSA",  # Assume RSA for now
                san_domains=san_domains,
                auto_renew=False  # Imported certificates don't auto-renew by default
            )
            
            self.certificates[name] = cert_info
            self.certificate_files[name] = {
                "cert_path": cert_path,
                "key_path": key_path if key_path else None
            }
            
            logger.info(f"Imported certificate: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import certificate: {str(e)}")
            return False
    
    async def check_certificate_expiry(self, cert_name: str) -> Dict[str, Any]:
        """Check certificate expiry status."""
        try:
            if cert_name not in self.certificates:
                return {"error": "Certificate not found"}
            
            cert_info = self.certificates[cert_name]
            now = datetime.utcnow()
            
            # Calculate days until expiry
            days_until_expiry = (cert_info.not_after - now).days
            
            # Determine status
            if now > cert_info.not_after:
                status = CertificateStatus.EXPIRED
            elif days_until_expiry <= cert_info.renewal_threshold_days:
                status = CertificateStatus.EXPIRING_SOON
            else:
                status = CertificateStatus.VALID
            
            # Update certificate status
            cert_info.status = status
            
            return {
                "certificate": cert_name,
                "status": status.value,
                "expires_on": cert_info.not_after.isoformat(),
                "days_until_expiry": days_until_expiry,
                "needs_renewal": status in [CertificateStatus.EXPIRED, CertificateStatus.EXPIRING_SOON]
            }
            
        except Exception as e:
            logger.error(f"Failed to check certificate expiry: {str(e)}")
            return {"error": str(e)}
    
    async def renew_certificate(self, cert_name: str) -> bool:
        """Renew a certificate."""
        try:
            if cert_name not in self.certificates:
                logger.error(f"Certificate not found: {cert_name}")
                return False
            
            cert_info = self.certificates[cert_name]
            
            if not cert_info.auto_renew:
                logger.info(f"Auto-renewal disabled for certificate: {cert_name}")
                return False
            
            # Create renewal request based on existing certificate
            renewal_request = CertificateRequest(
                common_name=cert_name,
                organization=self.ca_config["organization"],
                organizational_unit=self.ca_config["organizational_unit"],
                locality=self.ca_config["locality"],
                state=self.ca_config["state"],
                country=self.ca_config["country"],
                san_domains=cert_info.san_domains,
                key_size=cert_info.key_size,
                validity_days=365,
                certificate_type=cert_info.type
            )
            
            # Generate new certificate
            new_cert_name = await self.generate_certificate(renewal_request)
            
            if new_cert_name:
                logger.info(f"Successfully renewed certificate: {cert_name}")
                return True
            else:
                logger.error(f"Failed to renew certificate: {cert_name}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to renew certificate {cert_name}: {str(e)}")
            return False
    
    async def _auto_renewal_loop(self) -> None:
        """Automatic certificate renewal loop."""
        while True:
            try:
                logger.debug("Checking certificates for renewal")
                
                for cert_name in list(self.certificates.keys()):
                    expiry_check = await self.check_certificate_expiry(cert_name)
                    
                    if expiry_check.get("needs_renewal", False):
                        logger.info(f"Certificate needs renewal: {cert_name}")
                        await self.renew_certificate(cert_name)
                
                await asyncio.sleep(self.renewal_check_interval)
                
            except Exception as e:
                logger.error(f"Auto-renewal loop error: {str(e)}")
                await asyncio.sleep(self.renewal_check_interval)
    
    async def create_default_certificates(self) -> None:
        """Create default certificates for Ainflue infrastructure."""
        try:
            # Create root CA if it doesn't exist
            if not any(cert.type == CertificateType.ROOT_CA for cert in self.certificates.values()):
                await self.create_root_ca()
            
            # Ainflue API certificate
            api_request = CertificateRequest(
                common_name="api.ainflue.com",
                organization="Ainflue Platform",
                organizational_unit="API Services",
                locality="San Francisco",
                state="California",
                country="US",
                san_domains=["api.ainflue.com", "*.api.ainflue.com"],
                validity_days=365
            )
            await self.generate_certificate(api_request)
            
            # Ainflue AI Engine certificate
            ai_request = CertificateRequest(
                common_name="ai.ainflue.com",
                organization="Ainflue Platform",
                organizational_unit="AI Services",
                locality="San Francisco",
                state="California",
                country="US",
                san_domains=["ai.ainflue.com", "*.ai.ainflue.com"],
                validity_days=365
            )
            await self.generate_certificate(ai_request)
            
            # Ainflue Mobile API certificate
            mobile_request = CertificateRequest(
                common_name="mobile.ainflue.com",
                organization="Ainflue Platform",
                organizational_unit="Mobile Services",
                locality="San Francisco",
                state="California",
                country="US",
                san_domains=["mobile.ainflue.com", "*.mobile.ainflue.com"],
                validity_days=365
            )
            await self.generate_certificate(mobile_request)
            
            # Wildcard certificate for subdomains
            wildcard_request = CertificateRequest(
                common_name="*.ainflue.com",
                organization="Ainflue Platform",
                organizational_unit="Infrastructure",
                locality="San Francisco",
                state="California",
                country="US",
                san_domains=["*.ainflue.com", "ainflue.com"],
                validity_days=365
            )
            await self.generate_certificate(wildcard_request)
            
            logger.info("Created default certificates")
            
        except Exception as e:
            logger.error(f"Failed to create default certificates: {str(e)}")
    
    def list_certificates(self) -> List[Dict[str, Any]]:
        """List all managed certificates."""
        certificates = []
        for cert_info in self.certificates.values():
            certificates.append({
                "name": cert_info.name,
                "type": cert_info.type.value,
                "subject": cert_info.subject,
                "issuer": cert_info.issuer,
                "not_before": cert_info.not_before.isoformat(),
                "not_after": cert_info.not_after.isoformat(),
                "status": cert_info.status.value,
                "fingerprint": cert_info.fingerprint,
                "san_domains": cert_info.san_domains,
                "auto_renew": cert_info.auto_renew
            })
        return certificates
    
    def get_certificate_info(self, cert_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a certificate."""
        if cert_name not in self.certificates:
            return None
        
        cert_info = self.certificates[cert_name]
        files = self.certificate_files.get(cert_name, {})
        
        return {
            "name": cert_info.name,
            "type": cert_info.type.value,
            "subject": cert_info.subject,
            "issuer": cert_info.issuer,
            "serial_number": cert_info.serial_number,
            "not_before": cert_info.not_before.isoformat(),
            "not_after": cert_info.not_after.isoformat(),
            "fingerprint": cert_info.fingerprint,
            "key_size": cert_info.key_size,
            "algorithm": cert_info.algorithm,
            "san_domains": cert_info.san_domains,
            "status": cert_info.status.value,
            "auto_renew": cert_info.auto_renew,
            "renewal_threshold_days": cert_info.renewal_threshold_days,
            "certificate_path": files.get("cert_path"),
            "key_path": files.get("key_path")
        }
    
    async def validate_certificate(self, cert_name: str) -> Dict[str, Any]:
        """Validate a certificate."""
        try:
            if cert_name not in self.certificate_files:
                return {"valid": False, "error": "Certificate not found"}
            
            cert_path = self.certificate_files[cert_name].get("cert_path")
            if not cert_path:
                return {"valid": False, "error": "Certificate file not found"}
            
            # Read and parse certificate
            with open(cert_path, "rb") as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            validation_result = {
                "valid": True,
                "issues": [],
                "warnings": []
            }
            
            # Check if certificate is expired
            now = datetime.utcnow()
            if now > cert.not_valid_after:
                validation_result["valid"] = False
                validation_result["issues"].append("Certificate has expired")
            elif now < cert.not_valid_before:
                validation_result["valid"] = False
                validation_result["issues"].append("Certificate is not yet valid")
            
            # Check if certificate will expire soon
            days_until_expiry = (cert.not_valid_after - now).days
            if days_until_expiry <= 30:
                validation_result["warnings"].append(f"Certificate expires in {days_until_expiry} days")
            
            # Check certificate chain (if applicable)
            # In a real implementation, would validate the full chain
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate certificate {cert_name}: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def get_certificate_summary(self) -> Dict[str, Any]:
        """Get certificate management summary."""
        total_certs = len(self.certificates)
        expired_count = sum(1 for cert in self.certificates.values() if cert.status == CertificateStatus.EXPIRED)
        expiring_soon_count = sum(1 for cert in self.certificates.values() if cert.status == CertificateStatus.EXPIRING_SOON)
        auto_renew_count = sum(1 for cert in self.certificates.values() if cert.auto_renew)
        
        return {
            "total_certificates": total_certs,
            "expired_certificates": expired_count,
            "expiring_soon_certificates": expiring_soon_count,
            "auto_renewable_certificates": auto_renew_count,
            "auto_renewal_enabled": self.enable_auto_renewal,
            "certificate_directory": str(self.cert_dir),
            "next_renewal_check": datetime.now() + timedelta(seconds=self.renewal_check_interval)
        }


# Export the main class
__all__ = ["CertificateManager", "CertificateInfo", "CertificateRequest", "CertificateType", "CertificateStatus"]