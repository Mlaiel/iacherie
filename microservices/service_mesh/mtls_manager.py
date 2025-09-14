"""
mTLS Manager for Ainflue Microservices
Mutual TLS certificate management and rotation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import ssl
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dataclasses import dataclass
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class CertificateInfo:
    """Certificate information"""
    subject: str
    issuer: str
    serial_number: str
    not_before: datetime
    not_after: datetime
    fingerprint: str
    key_usage: List[str]
    san_dns: List[str]
    san_ip: List[str]


@dataclass
class TLSConfig:
    """TLS configuration for a service"""
    service_name: str
    namespace: str
    cert_path: str
    key_path: str
    ca_path: str
    verify_mode: str = "CERT_REQUIRED"  # CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
    cipher_suite: str = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
    protocol_version: str = "TLSv1.2"


class MTLSManager:
    """Mutual TLS certificate manager"""

    def __init__(self):
        self.certificates = {}
        self.tls_configs = {}
        self.ca_certificate = None
        self.ca_private_key = None
        self.cert_storage_path = os.getenv("MTLS_CERT_PATH", "/tmp/mtls_certs")
        self.rotation_interval = timedelta(days=90)  # Rotate every 90 days
        self.renewal_threshold = timedelta(days=30)  # Renew when 30 days left
        
        # Initialize CA if not exists
        asyncio.create_task(self._initialize_ca())

    async def _initialize_ca(self):
        """Initialize Certificate Authority"""
        try:
            ca_cert_path = os.path.join(self.cert_storage_path, "ca.crt")
            ca_key_path = os.path.join(self.cert_storage_path, "ca.key")
            
            os.makedirs(self.cert_storage_path, exist_ok=True)
            
            if os.path.exists(ca_cert_path) and os.path.exists(ca_key_path):
                # Load existing CA
                async with aiofiles.open(ca_cert_path, 'rb') as f:
                    ca_cert_data = await f.read()
                    self.ca_certificate = x509.load_pem_x509_certificate(ca_cert_data)
                
                async with aiofiles.open(ca_key_path, 'rb') as f:
                    ca_key_data = await f.read()
                    self.ca_private_key = serialization.load_pem_private_key(
                        ca_key_data, password=None
                    )
                
                logger.info("Loaded existing CA certificate")
            else:
                # Generate new CA
                await self._generate_ca_certificate()
                logger.info("Generated new CA certificate")
                
        except Exception as e:
            logger.error(f"Failed to initialize CA: {str(e)}")

    async def _generate_ca_certificate(self):
        """Generate Certificate Authority certificate"""
        try:
            # Generate CA private key
            self.ca_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
            
            # Create CA certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Microservices"),
                x509.NameAttribute(NameOID.COMMON_NAME, "Ainflue Root CA"),
            ])
            
            self.ca_certificate = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                self.ca_private_key.public_key()
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
            ).sign(self.ca_private_key, hashes.SHA256())
            
            # Save CA certificate and key
            ca_cert_path = os.path.join(self.cert_storage_path, "ca.crt")
            ca_key_path = os.path.join(self.cert_storage_path, "ca.key")
            
            async with aiofiles.open(ca_cert_path, 'wb') as f:
                await f.write(self.ca_certificate.public_bytes(serialization.Encoding.PEM))
            
            async with aiofiles.open(ca_key_path, 'wb') as f:
                await f.write(
                    self.ca_private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )
            
            logger.info("Generated and saved CA certificate")
            
        except Exception as e:
            logger.error(f"Failed to generate CA certificate: {str(e)}")
            raise

    async def generate_service_certificate(
        self, 
        service_name: str, 
        namespace: str = "default",
        dns_names: List[str] = None,
        ip_addresses: List[str] = None
    ) -> Tuple[str, str]:
        """Generate certificate for a service"""
        try:
            if not self.ca_certificate or not self.ca_private_key:
                raise ValueError("CA not initialized")
            
            # Generate service private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Prepare subject alternative names
            san_list = []
            
            # Add default DNS names
            default_dns_names = [
                service_name,
                f"{service_name}.{namespace}",
                f"{service_name}.{namespace}.svc",
                f"{service_name}.{namespace}.svc.cluster.local"
            ]
            
            if dns_names:
                default_dns_names.extend(dns_names)
            
            for dns_name in default_dns_names:
                san_list.append(x509.DNSName(dns_name))
            
            # Add IP addresses
            if ip_addresses:
                for ip_addr in ip_addresses:
                    try:
                        san_list.append(x509.IPAddress(ip_addr))
                    except ValueError:
                        logger.warning(f"Invalid IP address: {ip_addr}")
            
            # Create certificate
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Microservices"),
                x509.NameAttribute(NameOID.COMMON_NAME, f"{service_name}.{namespace}"),
            ])
            
            certificate = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.ca_certificate.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + self.rotation_interval
            ).add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
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
            ).sign(self.ca_private_key, hashes.SHA256())
            
            # Save certificate and key
            service_dir = os.path.join(self.cert_storage_path, namespace, service_name)
            os.makedirs(service_dir, exist_ok=True)
            
            cert_path = os.path.join(service_dir, "tls.crt")
            key_path = os.path.join(service_dir, "tls.key")
            
            async with aiofiles.open(cert_path, 'wb') as f:
                await f.write(certificate.public_bytes(serialization.Encoding.PEM))
            
            async with aiofiles.open(key_path, 'wb') as f:
                await f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )
            
            # Store certificate info
            cert_info = CertificateInfo(
                subject=str(certificate.subject),
                issuer=str(certificate.issuer),
                serial_number=str(certificate.serial_number),
                not_before=certificate.not_valid_before,
                not_after=certificate.not_valid_after,
                fingerprint=certificate.fingerprint(hashes.SHA256()).hex(),
                key_usage=[],
                san_dns=default_dns_names,
                san_ip=ip_addresses or []
            )
            
            service_key = f"{service_name}.{namespace}"
            self.certificates[service_key] = {
                "info": cert_info,
                "cert_path": cert_path,
                "key_path": key_path,
                "generated_at": datetime.utcnow()
            }
            
            logger.info(f"Generated certificate for service: {service_key}")
            return cert_path, key_path
            
        except Exception as e:
            logger.error(f"Failed to generate certificate for {service_name}: {str(e)}")
            raise

    async def configure_mtls(self, config: TLSConfig) -> bool:
        """Configure mTLS for a service"""
        try:
            service_key = f"{config.service_name}.{config.namespace}"
            
            # Validate certificate files exist
            if not all(os.path.exists(path) for path in [config.cert_path, config.key_path, config.ca_path]):
                logger.error(f"Certificate files missing for {service_key}")
                return False
            
            # Store TLS configuration
            self.tls_configs[service_key] = config
            
            logger.info(f"Configured mTLS for service: {service_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure mTLS for {config.service_name}: {str(e)}")
            return False

    async def verify_certificate(self, service_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Verify certificate validity"""
        try:
            service_key = f"{service_name}.{namespace}"
            
            if service_key not in self.certificates:
                return {"error": "Certificate not found"}
            
            cert_data = self.certificates[service_key]
            cert_info = cert_data["info"]
            
            # Check expiration
            now = datetime.utcnow()
            days_until_expiry = (cert_info.not_after - now).days
            
            is_valid = now >= cert_info.not_before and now <= cert_info.not_after
            needs_renewal = days_until_expiry <= self.renewal_threshold.days
            
            return {
                "service": service_key,
                "valid": is_valid,
                "expires_at": cert_info.not_after.isoformat(),
                "days_until_expiry": days_until_expiry,
                "needs_renewal": needs_renewal,
                "fingerprint": cert_info.fingerprint,
                "san_dns": cert_info.san_dns,
                "san_ip": cert_info.san_ip
            }
            
        except Exception as e:
            logger.error(f"Failed to verify certificate for {service_name}: {str(e)}")
            return {"error": str(e)}

    async def rotate_certificates(self) -> Dict[str, Any]:
        """Rotate certificates that need renewal"""
        try:
            rotation_results = {
                "started_at": datetime.utcnow().isoformat(),
                "rotated": [],
                "failed": [],
                "skipped": []
            }
            
            for service_key in list(self.certificates.keys()):
                cert_data = self.certificates[service_key]
                cert_info = cert_data["info"]
                
                # Check if renewal needed
                now = datetime.utcnow()
                days_until_expiry = (cert_info.not_after - now).days
                
                if days_until_expiry <= self.renewal_threshold.days:
                    try:
                        # Extract service name and namespace
                        service_name, namespace = service_key.split('.', 1)
                        
                        # Generate new certificate
                        await self.generate_service_certificate(
                            service_name, 
                            namespace,
                            cert_info.san_dns,
                            cert_info.san_ip
                        )
                        
                        rotation_results["rotated"].append(service_key)
                        logger.info(f"Rotated certificate for: {service_key}")
                        
                    except Exception as e:
                        rotation_results["failed"].append({
                            "service": service_key,
                            "error": str(e)
                        })
                        logger.error(f"Failed to rotate certificate for {service_key}: {str(e)}")
                else:
                    rotation_results["skipped"].append(service_key)
            
            rotation_results["completed_at"] = datetime.utcnow().isoformat()
            return rotation_results
            
        except Exception as e:
            logger.error(f"Certificate rotation failed: {str(e)}")
            return {"error": str(e)}

    async def get_certificate_status(self) -> Dict[str, Any]:
        """Get status of all certificates"""
        try:
            status = {
                "total_certificates": len(self.certificates),
                "valid_certificates": 0,
                "expired_certificates": 0,
                "expiring_soon": 0,
                "certificates": {},
                "ca_info": {
                    "subject": str(self.ca_certificate.subject) if self.ca_certificate else None,
                    "expires_at": self.ca_certificate.not_valid_after.isoformat() if self.ca_certificate else None
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            now = datetime.utcnow()
            
            for service_key, cert_data in self.certificates.items():
                cert_info = cert_data["info"]
                
                is_valid = now >= cert_info.not_before and now <= cert_info.not_after
                days_until_expiry = (cert_info.not_after - now).days
                
                if is_valid:
                    status["valid_certificates"] += 1
                else:
                    status["expired_certificates"] += 1
                
                if days_until_expiry <= self.renewal_threshold.days:
                    status["expiring_soon"] += 1
                
                status["certificates"][service_key] = {
                    "valid": is_valid,
                    "expires_at": cert_info.not_after.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "fingerprint": cert_info.fingerprint
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get certificate status: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """mTLS manager health check"""
        try:
            return {
                "status": "healthy",
                "ca_initialized": self.ca_certificate is not None,
                "certificates_managed": len(self.certificates),
                "tls_configs": len(self.tls_configs),
                "cert_storage_path": self.cert_storage_path,
                "rotation_interval_days": self.rotation_interval.days,
                "renewal_threshold_days": self.renewal_threshold.days,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"mTLS manager health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global mTLS manager instance
mtls_manager = MTLSManager()


async def generate_service_certificate(service_name: str, namespace: str = "default") -> Tuple[str, str]:
    """Generate certificate for service"""
    return await mtls_manager.generate_service_certificate(service_name, namespace)


async def verify_certificate(service_name: str, namespace: str = "default") -> Dict[str, Any]:
    """Verify certificate validity"""
    return await mtls_manager.verify_certificate(service_name, namespace)


if __name__ == "__main__":
    async def test_mtls_manager():
        """Test mTLS manager"""
        print("Testing mTLS Manager...")
        
        # Wait for CA initialization
        await asyncio.sleep(1)
        
        # Generate service certificate
        cert_path, key_path = await generate_service_certificate("test-service", "default")
        print(f"Generated certificate: {cert_path}")
        
        # Verify certificate
        verification = await verify_certificate("test-service", "default")
        print(f"Certificate verification: {verification}")
        
        # Get certificate status
        status = await mtls_manager.get_certificate_status()
        print(f"Certificate status: {json.dumps(status, indent=2)}")
        
        # Health check
        health = await mtls_manager.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_mtls_manager())