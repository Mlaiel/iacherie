"""
IA Influencer Agent - Certificate Manager
PKI and certificate management with automated renewal

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import logging
import json
import threading
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import ssl
import socket
import requests
import subprocess
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
import acme
from acme import client, messages, challenges, crypto_util
from josepy import JWKRSA

from .vault_manager import VaultManager
from .config import SecretsConfig
from .utils import SecurityUtils, NotificationUtils

logger = logging.getLogger(__name__)


class CertificateType(Enum):
    """Certificate types."""
    SSL_TLS = "ssl_tls"
    CLIENT_AUTH = "client_auth"
    CODE_SIGNING = "code_signing"
    EMAIL = "email"
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"


class CertificateStatus(Enum):
    """Certificate status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    RENEWAL_NEEDED = "renewal_needed"


class KeyType(Enum):
    """Key types."""
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ECDSA_P384 = "ecdsa_p384"


@dataclass
class CertificateInfo:
    """Certificate information."""
    cert_id: str
    common_name: str
    certificate_type: CertificateType
    key_type: KeyType
    status: CertificateStatus
    subject: Dict[str, str]
    san_list: List[str] = field(default_factory=list)
    issuer: str = ""
    serial_number: str = ""
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    fingerprint: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    vault_path: str = ""
    auto_renew: bool = True
    renewal_threshold_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CertificateRequest:
    """Certificate request configuration."""
    common_name: str
    certificate_type: CertificateType = CertificateType.SSL_TLS
    key_type: KeyType = KeyType.RSA_2048
    subject: Dict[str, str] = field(default_factory=dict)
    san_list: List[str] = field(default_factory=list)
    validity_days: int = 365
    auto_renew: bool = True
    renewal_threshold_days: int = 30
    vault_path: str = ""
    ca_cert_path: str = ""
    ca_key_path: str = ""
    use_lets_encrypt: bool = False
    lets_encrypt_email: str = ""
    lets_encrypt_staging: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class CertificateManager:
    """
    Enterprise certificate manager with automated PKI operations,
    Let's Encrypt integration, and certificate lifecycle management.
    """
    
    def __init__(
        self,
        vault_manager: VaultManager,
        config: SecretsConfig = None
    ):
        """
        Initialize certificate manager.
        
        Args:
            vault_manager: Configured VaultManager instance
            config: Optional secrets configuration
        """
        self.vault = vault_manager
        self.config = config or SecretsConfig()
        self.security = SecurityUtils()
        self.notifications = NotificationUtils()
        
        # Certificate state
        self.certificates: Dict[str, CertificateInfo] = {}
        self.renewal_threads: Dict[str, threading.Thread] = {}
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Let's Encrypt client
        self.acme_client: Optional[acme.client.ClientV2] = None
        
        # Load existing certificates
        self._load_certificates()
        
        logger.info("CertificateManager initialized")
    
    def start_monitoring(self) -> None:
        """Start certificate monitoring and auto-renewal."""
        if self.is_monitoring:
            logger.warning("Certificate monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Certificate monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop certificate monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=30)
        
        # Stop renewal threads
        for thread in self.renewal_threads.values():
            thread.join(timeout=5)
        self.renewal_threads.clear()
        
        logger.info("Certificate monitoring stopped")
    
    def generate_certificate(
        self,
        request: CertificateRequest
    ) -> Optional[str]:
        """
        Generate new certificate.
        
        Args:
            request: Certificate request configuration
            
        Returns:
            str: Certificate ID if successful
        """
        try:
            cert_id = self._generate_cert_id()
            logger.info(f"Generating certificate {cert_id} for {request.common_name}")
            
            if request.use_lets_encrypt:
                # Use Let's Encrypt
                cert_data = self._generate_lets_encrypt_certificate(request)
            elif request.ca_cert_path and request.ca_key_path:
                # Use custom CA
                cert_data = self._generate_ca_signed_certificate(request)
            else:
                # Self-signed certificate
                cert_data = self._generate_self_signed_certificate(request)
            
            if not cert_data:
                logger.error(f"Failed to generate certificate for {request.common_name}")
                return None
            
            # Parse certificate for metadata
            cert = x509.load_pem_x509_certificate(cert_data['certificate'].encode())
            
            # Create certificate info
            cert_info = CertificateInfo(
                cert_id=cert_id,
                common_name=request.common_name,
                certificate_type=request.certificate_type,
                key_type=request.key_type,
                status=CertificateStatus.ACTIVE,
                subject={
                    'CN': request.common_name,
                    **request.subject
                },
                san_list=request.san_list,
                issuer=cert.issuer.rfc4514_string(),
                serial_number=str(cert.serial_number),
                not_before=cert.not_valid_before,
                not_after=cert.not_valid_after,
                fingerprint=cert.fingerprint(hashes.SHA256()).hex(),
                vault_path=request.vault_path or f"certificates/{cert_id}",
                auto_renew=request.auto_renew,
                renewal_threshold_days=request.renewal_threshold_days,
                metadata=request.metadata
            )
            
            # Store certificate in Vault
            vault_data = {
                'certificate': cert_data['certificate'],
                'private_key': cert_data['private_key'],
                'certificate_chain': cert_data.get('certificate_chain', ''),
                'cert_info': {
                    'common_name': cert_info.common_name,
                    'type': cert_info.certificate_type.value,
                    'status': cert_info.status.value,
                    'not_before': cert_info.not_before.isoformat(),
                    'not_after': cert_info.not_after.isoformat(),
                    'fingerprint': cert_info.fingerprint,
                    'san_list': cert_info.san_list
                }
            }
            
            success = self.vault.store_secret(
                path=cert_info.vault_path,
                secret_data=vault_data,
                metadata={'certificate_id': cert_id}
            )
            
            if not success:
                logger.error(f"Failed to store certificate {cert_id} in Vault")
                return None
            
            # Store certificate info
            self.certificates[cert_id] = cert_info
            self._save_certificates()
            
            logger.info(f"Certificate {cert_id} generated and stored successfully")
            return cert_id
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            return None
    
    def renew_certificate(
        self,
        cert_id: str,
        force: bool = False
    ) -> bool:
        """
        Renew certificate.
        
        Args:
            cert_id: Certificate ID to renew
            force: Force renewal even if not due
            
        Returns:
            bool: True if renewal successful
        """
        try:
            cert_info = self.certificates.get(cert_id)
            if not cert_info:
                logger.error(f"Certificate not found: {cert_id}")
                return False
            
            # Check if renewal is needed
            if not force:
                days_until_expiry = (cert_info.not_after - datetime.utcnow()).days
                if days_until_expiry > cert_info.renewal_threshold_days:
                    logger.info(f"Certificate {cert_id} renewal not yet needed")
                    return True
            
            logger.info(f"Renewing certificate {cert_id}")
            
            # Get existing certificate data
            cert_data = self.vault.get_secret(cert_info.vault_path)
            if not cert_data:
                logger.error(f"Certificate data not found in Vault: {cert_info.vault_path}")
                return False
            
            # Create renewal request
            renewal_request = CertificateRequest(
                common_name=cert_info.common_name,
                certificate_type=cert_info.certificate_type,
                key_type=cert_info.key_type,
                subject=cert_info.subject,
                san_list=cert_info.san_list,
                auto_renew=cert_info.auto_renew,
                renewal_threshold_days=cert_info.renewal_threshold_days,
                vault_path=cert_info.vault_path,
                metadata=cert_info.metadata
            )
            
            # Check if Let's Encrypt was used
            if 'lets_encrypt' in cert_info.metadata:
                renewal_request.use_lets_encrypt = True
                renewal_request.lets_encrypt_email = cert_info.metadata.get('lets_encrypt_email', '')
                renewal_request.lets_encrypt_staging = cert_info.metadata.get('lets_encrypt_staging', False)
            
            # Generate new certificate
            if renewal_request.use_lets_encrypt:
                new_cert_data = self._generate_lets_encrypt_certificate(renewal_request)
            else:
                new_cert_data = self._generate_self_signed_certificate(renewal_request)
            
            if not new_cert_data:
                logger.error(f"Failed to generate renewed certificate for {cert_id}")
                return False
            
            # Update certificate info
            new_cert = x509.load_pem_x509_certificate(new_cert_data['certificate'].encode())
            cert_info.status = CertificateStatus.ACTIVE
            cert_info.not_before = new_cert.not_valid_before
            cert_info.not_after = new_cert.not_valid_after
            cert_info.fingerprint = new_cert.fingerprint(hashes.SHA256()).hex()
            cert_info.serial_number = str(new_cert.serial_number)
            
            # Update Vault data
            vault_data = cert_data['data'].copy()
            vault_data.update({
                'certificate': new_cert_data['certificate'],
                'private_key': new_cert_data['private_key'],
                'certificate_chain': new_cert_data.get('certificate_chain', ''),
                'cert_info': {
                    'common_name': cert_info.common_name,
                    'type': cert_info.certificate_type.value,
                    'status': cert_info.status.value,
                    'not_before': cert_info.not_before.isoformat(),
                    'not_after': cert_info.not_after.isoformat(),
                    'fingerprint': cert_info.fingerprint,
                    'san_list': cert_info.san_list
                }
            })
            
            success = self.vault.store_secret(
                path=cert_info.vault_path,
                secret_data=vault_data,
                metadata={'certificate_id': cert_id, 'renewed_at': datetime.utcnow().isoformat()}
            )
            
            if not success:
                logger.error(f"Failed to store renewed certificate {cert_id}")
                return False
            
            self._save_certificates()
            
            # Send renewal notification
            self._send_renewal_notification(cert_id, success=True)
            
            logger.info(f"Certificate {cert_id} renewed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Certificate renewal failed for {cert_id}: {e}")
            self._send_renewal_notification(cert_id, success=False, error=str(e))
            return False
    
    def revoke_certificate(
        self,
        cert_id: str,
        reason: str = "unspecified"
    ) -> bool:
        """
        Revoke certificate.
        
        Args:
            cert_id: Certificate ID to revoke
            reason: Revocation reason
            
        Returns:
            bool: True if revocation successful
        """
        try:
            cert_info = self.certificates.get(cert_id)
            if not cert_info:
                logger.error(f"Certificate not found: {cert_id}")
                return False
            
            # Update status
            cert_info.status = CertificateStatus.REVOKED
            cert_info.metadata['revoked_at'] = datetime.utcnow().isoformat()
            cert_info.metadata['revocation_reason'] = reason
            
            # If Let's Encrypt certificate, revoke with ACME
            if 'lets_encrypt' in cert_info.metadata and self.acme_client:
                try:
                    cert_data = self.vault.get_secret(cert_info.vault_path)
                    if cert_data:
                        cert_pem = cert_data['data']['certificate']
                        cert = x509.load_pem_x509_certificate(cert_pem.encode())
                        
                        # Revoke with ACME
                        self.acme_client.revoke(
                            crypto_util.cert_der_to_pem(cert.public_bytes(serialization.Encoding.DER)),
                            reason=0  # Unspecified
                        )
                        logger.info(f"Certificate {cert_id} revoked with Let's Encrypt")
                        
                except Exception as e:
                    logger.warning(f"Failed to revoke with Let's Encrypt: {e}")
            
            self._save_certificates()
            
            # Send revocation notification
            self._send_revocation_notification(cert_id, reason)
            
            logger.info(f"Certificate {cert_id} revoked")
            return True
            
        except Exception as e:
            logger.error(f"Certificate revocation failed for {cert_id}: {e}")
            return False
    
    def get_certificate(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get certificate data.
        
        Args:
            cert_id: Certificate ID
            
        Returns:
            dict: Certificate data
        """
        try:
            cert_info = self.certificates.get(cert_id)
            if not cert_info:
                return None
            
            # Get certificate from Vault
            cert_data = self.vault.get_secret(cert_info.vault_path)
            if not cert_data:
                return None
            
            return {
                'cert_id': cert_info.cert_id,
                'certificate': cert_data['data']['certificate'],
                'private_key': cert_data['data']['private_key'],
                'certificate_chain': cert_data['data'].get('certificate_chain', ''),
                'cert_info': cert_data['data']['cert_info']
            }
            
        except Exception as e:
            logger.error(f"Failed to get certificate {cert_id}: {e}")
            return None
    
    def list_certificates(
        self,
        status_filter: CertificateStatus = None
    ) -> List[Dict[str, Any]]:
        """
        List certificates.
        
        Args:
            status_filter: Optional status filter
            
        Returns:
            list: List of certificate information
        """
        certificates = []
        
        for cert_info in self.certificates.values():
            if status_filter and cert_info.status != status_filter:
                continue
            
            certificates.append({
                'cert_id': cert_info.cert_id,
                'common_name': cert_info.common_name,
                'type': cert_info.certificate_type.value,
                'status': cert_info.status.value,
                'not_before': cert_info.not_before.isoformat() if cert_info.not_before else None,
                'not_after': cert_info.not_after.isoformat() if cert_info.not_after else None,
                'days_until_expiry': (cert_info.not_after - datetime.utcnow()).days if cert_info.not_after else None,
                'fingerprint': cert_info.fingerprint,
                'san_list': cert_info.san_list,
                'auto_renew': cert_info.auto_renew
            })
        
        return sorted(certificates, key=lambda x: x['not_after'] or '')
    
    def check_certificate_expiry(self, cert_id: str) -> Dict[str, Any]:
        """
        Check certificate expiry status.
        
        Args:
            cert_id: Certificate ID
            
        Returns:
            dict: Expiry status information
        """
        cert_info = self.certificates.get(cert_id)
        if not cert_info:
            return {'error': 'Certificate not found'}
        
        if not cert_info.not_after:
            return {'error': 'Certificate expiry date not available'}
        
        now = datetime.utcnow()
        days_until_expiry = (cert_info.not_after - now).days
        
        status = 'valid'
        if days_until_expiry < 0:
            status = 'expired'
        elif days_until_expiry <= cert_info.renewal_threshold_days:
            status = 'renewal_needed'
        
        return {
            'cert_id': cert_id,
            'common_name': cert_info.common_name,
            'status': status,
            'not_after': cert_info.not_after.isoformat(),
            'days_until_expiry': days_until_expiry,
            'renewal_threshold_days': cert_info.renewal_threshold_days,
            'auto_renew': cert_info.auto_renew
        }
    
    def validate_certificate_chain(self, cert_id: str) -> Dict[str, Any]:
        """
        Validate certificate chain.
        
        Args:
            cert_id: Certificate ID
            
        Returns:
            dict: Validation results
        """
        try:
            cert_data = self.get_certificate(cert_id)
            if not cert_data:
                return {'valid': False, 'error': 'Certificate not found'}
            
            cert_pem = cert_data['certificate']
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
            
            validation_results = {
                'valid': True,
                'cert_id': cert_id,
                'common_name': cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
                'issuer': cert.issuer.rfc4514_string(),
                'serial_number': str(cert.serial_number),
                'not_before': cert.not_valid_before.isoformat(),
                'not_after': cert.not_valid_after.isoformat(),
                'signature_algorithm': cert.signature_algorithm_oid._name,
                'key_size': cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
                'san_list': [],
                'key_usage': [],
                'extended_key_usage': [],
                'issues': []
            }
            
            # Extract SAN
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                validation_results['san_list'] = [name.value for name in san_ext.value]
            except x509.ExtensionNotFound:
                pass
            
            # Extract key usage
            try:
                key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
                usage_list = []
                if key_usage.value.digital_signature:
                    usage_list.append('digital_signature')
                if key_usage.value.key_encipherment:
                    usage_list.append('key_encipherment')
                if key_usage.value.key_agreement:
                    usage_list.append('key_agreement')
                validation_results['key_usage'] = usage_list
            except x509.ExtensionNotFound:
                pass
            
            # Extract extended key usage
            try:
                ext_key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.EXTENDED_KEY_USAGE)
                ext_usage_list = []
                for usage in ext_key_usage.value:
                    if usage == ExtendedKeyUsageOID.SERVER_AUTH:
                        ext_usage_list.append('server_auth')
                    elif usage == ExtendedKeyUsageOID.CLIENT_AUTH:
                        ext_usage_list.append('client_auth')
                validation_results['extended_key_usage'] = ext_usage_list
            except x509.ExtensionNotFound:
                pass
            
            # Check for issues
            now = datetime.utcnow()
            if cert.not_valid_after < now:
                validation_results['issues'].append('Certificate has expired')
                validation_results['valid'] = False
            elif cert.not_valid_before > now:
                validation_results['issues'].append('Certificate is not yet valid')
                validation_results['valid'] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Certificate validation failed for {cert_id}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def export_certificate(
        self,
        cert_id: str,
        format: str = "pem",
        include_chain: bool = True,
        include_private_key: bool = False
    ) -> Optional[Dict[str, str]]:
        """
        Export certificate in various formats.
        
        Args:
            cert_id: Certificate ID
            format: Export format (pem, der, p12)
            include_chain: Include certificate chain
            include_private_key: Include private key
            
        Returns:
            dict: Exported certificate data
        """
        try:
            cert_data = self.get_certificate(cert_id)
            if not cert_data:
                return None
            
            cert_pem = cert_data['certificate']
            key_pem = cert_data['private_key']
            chain_pem = cert_data.get('certificate_chain', '')
            
            if format == "pem":
                result = {'certificate': cert_pem}
                
                if include_chain and chain_pem:
                    result['certificate_chain'] = chain_pem
                    result['full_chain'] = cert_pem + '\n' + chain_pem
                
                if include_private_key:
                    result['private_key'] = key_pem
                
                return result
                
            elif format == "der":
                cert = x509.load_pem_x509_certificate(cert_pem.encode())
                result = {'certificate': cert.public_bytes(serialization.Encoding.DER).hex()}
                
                if include_private_key:
                    private_key = serialization.load_pem_private_key(key_pem.encode(), password=None)
                    result['private_key'] = private_key.private_bytes(
                        encoding=serialization.Encoding.DER,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ).hex()
                
                return result
                
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Certificate export failed for {cert_id}: {e}")
            return None
    
    def _generate_self_signed_certificate(
        self,
        request: CertificateRequest
    ) -> Optional[Dict[str, str]]:
        """Generate self-signed certificate."""
        try:
            # Generate private key
            if request.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                key_size = 2048 if request.key_type == KeyType.RSA_2048 else 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
            else:
                # ECDSA
                if request.key_type == KeyType.ECDSA_P256:
                    private_key = ec.generate_private_key(ec.SECP256R1())
                else:
                    private_key = ec.generate_private_key(ec.SECP384R1())
            
            # Build subject
            subject_components = []
            if 'C' in request.subject:
                subject_components.append(x509.NameAttribute(NameOID.COUNTRY_NAME, request.subject['C']))
            if 'ST' in request.subject:
                subject_components.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, request.subject['ST']))
            if 'L' in request.subject:
                subject_components.append(x509.NameAttribute(NameOID.LOCALITY_NAME, request.subject['L']))
            if 'O' in request.subject:
                subject_components.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, request.subject['O']))
            if 'OU' in request.subject:
                subject_components.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, request.subject['OU']))
            
            subject_components.append(x509.NameAttribute(NameOID.COMMON_NAME, request.common_name))
            subject = x509.Name(subject_components)
            
            # Build certificate
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(subject)
            cert_builder = cert_builder.issuer_name(subject)  # Self-signed
            cert_builder = cert_builder.public_key(private_key.public_key())
            cert_builder = cert_builder.serial_number(x509.random_serial_number())
            cert_builder = cert_builder.not_valid_before(datetime.utcnow())
            cert_builder = cert_builder.not_valid_after(
                datetime.utcnow() + timedelta(days=request.validity_days)
            )
            
            # Add SAN extension
            if request.san_list:
                san_list = [x509.DNSName(name) for name in request.san_list]
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False
                )
            
            # Add key usage extension
            if request.certificate_type == CertificateType.SSL_TLS:
                cert_builder = cert_builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=True,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        content_commitment=False,
                        data_encipherment=False,
                        encipher_only=False,
                        decipher_only=False
                    ),
                    critical=True
                )
                
                cert_builder = cert_builder.add_extension(
                    x509.ExtendedKeyUsage([
                        ExtendedKeyUsageOID.SERVER_AUTH,
                        ExtendedKeyUsageOID.CLIENT_AUTH
                    ]),
                    critical=True
                )
            
            # Sign certificate
            certificate = cert_builder.sign(private_key, hashes.SHA256())
            
            # Serialize to PEM
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode()
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            return {
                'certificate': cert_pem,
                'private_key': key_pem
            }
            
        except Exception as e:
            logger.error(f"Self-signed certificate generation failed: {e}")
            return None
    
    def _generate_ca_signed_certificate(
        self,
        request: CertificateRequest
    ) -> Optional[Dict[str, str]]:
        """Generate CA-signed certificate."""
        try:
            # Load CA certificate and key
            with open(request.ca_cert_path, 'rb') as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            
            with open(request.ca_key_path, 'rb') as f:
                ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Generate private key for certificate
            if request.key_type in [KeyType.RSA_2048, KeyType.RSA_4096]:
                key_size = 2048 if request.key_type == KeyType.RSA_2048 else 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
            else:
                # ECDSA
                if request.key_type == KeyType.ECDSA_P256:
                    private_key = ec.generate_private_key(ec.SECP256R1())
                else:
                    private_key = ec.generate_private_key(ec.SECP384R1())
            
            # Build subject
            subject_components = []
            for attr_name, attr_value in request.subject.items():
                if attr_name == 'C':
                    subject_components.append(x509.NameAttribute(NameOID.COUNTRY_NAME, attr_value))
                elif attr_name == 'ST':
                    subject_components.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, attr_value))
                elif attr_name == 'L':
                    subject_components.append(x509.NameAttribute(NameOID.LOCALITY_NAME, attr_value))
                elif attr_name == 'O':
                    subject_components.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, attr_value))
                elif attr_name == 'OU':
                    subject_components.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, attr_value))
            
            subject_components.append(x509.NameAttribute(NameOID.COMMON_NAME, request.common_name))
            subject = x509.Name(subject_components)
            
            # Build certificate signed by CA
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(subject)
            cert_builder = cert_builder.issuer_name(ca_cert.subject)
            cert_builder = cert_builder.public_key(private_key.public_key())
            cert_builder = cert_builder.serial_number(x509.random_serial_number())
            cert_builder = cert_builder.not_valid_before(datetime.utcnow())
            cert_builder = cert_builder.not_valid_after(
                datetime.utcnow() + timedelta(days=request.validity_days)
            )
            
            # Add extensions
            if request.san_list:
                san_list = [x509.DNSName(name) for name in request.san_list]
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False
                )
            
            # Sign with CA key
            certificate = cert_builder.sign(ca_key, hashes.SHA256())
            
            # Serialize to PEM
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode()
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM).decode()
            
            return {
                'certificate': cert_pem,
                'private_key': key_pem,
                'certificate_chain': ca_cert_pem
            }
            
        except Exception as e:
            logger.error(f"CA-signed certificate generation failed: {e}")
            return None
    
    def _generate_lets_encrypt_certificate(
        self,
        request: CertificateRequest
    ) -> Optional[Dict[str, str]]:
        """Generate Let's Encrypt certificate."""
        try:
            # Initialize ACME client if needed
            if not self.acme_client:
                self._initialize_acme_client(
                    request.lets_encrypt_email,
                    request.lets_encrypt_staging
                )
            
            if not self.acme_client:
                raise RuntimeError("ACME client initialization failed")
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create CSR
            csr_builder = x509.CertificateSigningRequestBuilder()
            csr_builder = csr_builder.subject_name(x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, request.common_name)
            ]))
            
            # Add SAN
            san_list = [x509.DNSName(request.common_name)]
            san_list.extend([x509.DNSName(name) for name in request.san_list])
            csr_builder = csr_builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False
            )
            
            csr = csr_builder.sign(private_key, hashes.SHA256())
            
            # Request certificate from Let's Encrypt
            order = self.acme_client.new_order(csr)
            
            # Complete challenges
            for authz in order.authorizations:
                self._complete_challenge(authz)
            
            # Finalize order
            order = self.acme_client.poll_and_finalize(order)
            
            # Get certificate
            fullchain_pem = order.fullchain_pem
            
            # Split certificate and chain
            cert_lines = []
            chain_lines = []
            current_cert = cert_lines
            
            for line in fullchain_pem.split('\n'):
                if line == '-----BEGIN CERTIFICATE-----':
                    if cert_lines and cert_lines != current_cert:
                        current_cert = chain_lines
                    current_cert.append(line)
                elif line == '-----END CERTIFICATE-----':
                    current_cert.append(line)
                    if current_cert == cert_lines:
                        current_cert = chain_lines
                else:
                    current_cert.append(line)
            
            cert_pem = '\n'.join(cert_lines)
            chain_pem = '\n'.join(chain_lines) if chain_lines else ''
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            return {
                'certificate': cert_pem,
                'private_key': key_pem,
                'certificate_chain': chain_pem
            }
            
        except Exception as e:
            logger.error(f"Let's Encrypt certificate generation failed: {e}")
            return None
    
    def _initialize_acme_client(
        self,
        email: str,
        staging: bool = False
    ) -> None:
        """Initialize ACME client for Let's Encrypt."""
        try:
            # ACME directory URL
            if staging:
                directory_url = "https://acme-staging-v02.api.letsencrypt.org/directory"
            else:
                directory_url = "https://acme-v02.api.letsencrypt.org/directory"
            
            # Generate account key
            account_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create ACME client
            net = client.ClientNetwork(account_key, user_agent="IA-Influencer-Agent")
            directory = messages.Directory.from_json(net.get(directory_url).json())
            self.acme_client = client.ClientV2(directory, net=net)
            
            # Register account
            account = messages.NewRegistration.from_data(
                email=email,
                terms_of_service_agreed=True
            )
            
            try:
                self.acme_client.new_account(account)
            except Exception as e:
                # Account might already exist
                logger.warning(f"ACME account registration warning: {e}")
            
            logger.info("ACME client initialized")
            
        except Exception as e:
            logger.error(f"ACME client initialization failed: {e}")
            self.acme_client = None
    
    def _complete_challenge(self, authz) -> None:
        """Complete ACME challenge."""
        # This is a simplified implementation
        # In a real implementation, you would need to:
        # 1. Set up HTTP challenge response
        # 2. Or configure DNS challenge
        # 3. Verify challenge completion
        
        for challenge in authz.body.challenges:
            if isinstance(challenge.chall, challenges.HTTP01):
                # HTTP-01 challenge
                response, validation = challenge.response_and_validation(
                    self.acme_client.net.key
                )
                
                # Set up HTTP challenge response
                # This would require setting up a web server
                # or modifying existing web server configuration
                
                self.acme_client.answer_challenge(challenge, response)
                break
    
    def _monitoring_loop(self) -> None:
        """Certificate monitoring loop."""
        while self.is_monitoring:
            try:
                # Check all certificates for renewal needs
                for cert_id, cert_info in self.certificates.items():
                    if not cert_info.auto_renew:
                        continue
                    
                    if cert_info.status != CertificateStatus.ACTIVE:
                        continue
                    
                    if not cert_info.not_after:
                        continue
                    
                    days_until_expiry = (cert_info.not_after - datetime.utcnow()).days
                    
                    if days_until_expiry <= cert_info.renewal_threshold_days:
                        # Start renewal in separate thread
                        if cert_id not in self.renewal_threads:
                            thread = threading.Thread(
                                target=self._renewal_worker,
                                args=(cert_id,),
                                daemon=True
                            )
                            thread.start()
                            self.renewal_threads[cert_id] = thread
                
                # Clean up completed renewal threads
                completed_threads = []
                for cert_id, thread in self.renewal_threads.items():
                    if not thread.is_alive():
                        completed_threads.append(cert_id)
                
                for cert_id in completed_threads:
                    del self.renewal_threads[cert_id]
                
                # Sleep for monitoring interval
                time.sleep(self.config.certificate_monitor_interval)
                
            except Exception as e:
                logger.error(f"Certificate monitoring error: {e}")
                time.sleep(60)  # Short sleep on error
    
    def _renewal_worker(self, cert_id: str) -> None:
        """Certificate renewal worker."""
        try:
            logger.info(f"Starting automatic renewal for certificate {cert_id}")
            success = self.renew_certificate(cert_id)
            
            if success:
                logger.info(f"Automatic renewal completed for certificate {cert_id}")
            else:
                logger.error(f"Automatic renewal failed for certificate {cert_id}")
                
        except Exception as e:
            logger.error(f"Renewal worker error for {cert_id}: {e}")
    
    def _send_renewal_notification(
        self,
        cert_id: str,
        success: bool,
        error: str = None
    ) -> None:
        """Send certificate renewal notification."""
        try:
            cert_info = self.certificates.get(cert_id)
            if not cert_info:
                return
            
            notification_data = {
                'event': 'certificate_renewal',
                'cert_id': cert_id,
                'common_name': cert_info.common_name,
                'success': success,
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.notifications.send_certificate_notification(notification_data)
            
        except Exception as e:
            logger.error(f"Failed to send renewal notification: {e}")
    
    def _send_revocation_notification(
        self,
        cert_id: str,
        reason: str
    ) -> None:
        """Send certificate revocation notification."""
        try:
            cert_info = self.certificates.get(cert_id)
            if not cert_info:
                return
            
            notification_data = {
                'event': 'certificate_revocation',
                'cert_id': cert_id,
                'common_name': cert_info.common_name,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.notifications.send_certificate_notification(notification_data)
            
        except Exception as e:
            logger.error(f"Failed to send revocation notification: {e}")
    
    def _generate_cert_id(self) -> str:
        """Generate unique certificate ID."""
        import secrets
        return f"cert_{secrets.token_hex(8)}_{int(datetime.utcnow().timestamp())}"
    
    def _load_certificates(self) -> None:
        """Load certificates from storage."""
        try:
            certs_file = Path(self.config.certificates_file)
            if not certs_file.exists():
                return
            
            with open(certs_file, 'r') as f:
                certs_data = json.load(f)
            
            for cert_data in certs_data:
                cert_info = CertificateInfo(
                    cert_id=cert_data['cert_id'],
                    common_name=cert_data['common_name'],
                    certificate_type=CertificateType(cert_data['certificate_type']),
                    key_type=KeyType(cert_data['key_type']),
                    status=CertificateStatus(cert_data['status']),
                    subject=cert_data['subject'],
                    san_list=cert_data.get('san_list', []),
                    issuer=cert_data.get('issuer', ''),
                    serial_number=cert_data.get('serial_number', ''),
                    not_before=datetime.fromisoformat(cert_data['not_before']) if cert_data.get('not_before') else None,
                    not_after=datetime.fromisoformat(cert_data['not_after']) if cert_data.get('not_after') else None,
                    fingerprint=cert_data.get('fingerprint', ''),
                    created_at=datetime.fromisoformat(cert_data['created_at']),
                    vault_path=cert_data['vault_path'],
                    auto_renew=cert_data.get('auto_renew', True),
                    renewal_threshold_days=cert_data.get('renewal_threshold_days', 30),
                    metadata=cert_data.get('metadata', {})
                )
                self.certificates[cert_info.cert_id] = cert_info
            
            logger.info(f"Loaded {len(self.certificates)} certificates")
            
        except Exception as e:
            logger.error(f"Failed to load certificates: {e}")
    
    def _save_certificates(self) -> None:
        """Save certificates to storage."""
        try:
            certs_data = []
            
            for cert_info in self.certificates.values():
                certs_data.append({
                    'cert_id': cert_info.cert_id,
                    'common_name': cert_info.common_name,
                    'certificate_type': cert_info.certificate_type.value,
                    'key_type': cert_info.key_type.value,
                    'status': cert_info.status.value,
                    'subject': cert_info.subject,
                    'san_list': cert_info.san_list,
                    'issuer': cert_info.issuer,
                    'serial_number': cert_info.serial_number,
                    'not_before': cert_info.not_before.isoformat() if cert_info.not_before else None,
                    'not_after': cert_info.not_after.isoformat() if cert_info.not_after else None,
                    'fingerprint': cert_info.fingerprint,
                    'created_at': cert_info.created_at.isoformat(),
                    'vault_path': cert_info.vault_path,
                    'auto_renew': cert_info.auto_renew,
                    'renewal_threshold_days': cert_info.renewal_threshold_days,
                    'metadata': cert_info.metadata
                })
            
            certs_file = Path(self.config.certificates_file)
            certs_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(certs_file, 'w') as f:
                json.dump(certs_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save certificates: {e}")


class InfluencerCertificateManager(CertificateManager):
    """
    Specialized certificate manager for IA Influencer Agent platform.
    
    Handles certificates for:
    - Platform API endpoints (YouTube, Instagram, TikTok, Spotify, etc.)
    - Content delivery networks (CDN)
    - Payment processing endpoints (PCI-DSS compliant)
    - AI model API endpoints (OpenAI, Anthropic, Hugging Face)
    - Microservices communication
    - Admin dashboard and user interfaces
    """
    
    def __init__(
        self,
        vault_manager: VaultManager,
        config: SecretsConfig = None
    ):
        super().__init__(vault_manager, config)
        
        # IA Influencer platform-specific certificate templates
        self.platform_templates = {
            'api_gateway': {
                'certificate_type': CertificateType.SSL_TLS,
                'key_type': KeyType.RSA_2048,
                'validity_days': 365,
                'auto_renew': True,
                'renewal_threshold_days': 30,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'API Gateway',
                    'C': 'DE'
                }
            },
            'platform_endpoints': {
                'certificate_type': CertificateType.SSL_TLS,
                'key_type': KeyType.RSA_2048,
                'validity_days': 180,
                'auto_renew': True,
                'renewal_threshold_days': 14,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'Platform Integration',
                    'C': 'DE'
                }
            },
            'payment_endpoints': {
                'certificate_type': CertificateType.SSL_TLS,
                'key_type': KeyType.RSA_4096,  # Higher security for payments
                'validity_days': 90,  # Shorter validity for PCI compliance
                'auto_renew': True,
                'renewal_threshold_days': 7,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'Payment Processing',
                    'C': 'DE'
                }
            },
            'ai_model_endpoints': {
                'certificate_type': CertificateType.SSL_TLS,
                'key_type': KeyType.RSA_2048,
                'validity_days': 365,
                'auto_renew': True,
                'renewal_threshold_days': 21,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'AI Model Integration',
                    'C': 'DE'
                }
            },
            'cdn_endpoints': {
                'certificate_type': CertificateType.SSL_TLS,
                'key_type': KeyType.ECDSA_P256,  # ECDSA for better performance
                'validity_days': 365,
                'auto_renew': True,
                'renewal_threshold_days': 30,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'Content Delivery',
                    'C': 'DE'
                }
            },
            'microservices': {
                'certificate_type': CertificateType.CLIENT_AUTH,
                'key_type': KeyType.RSA_2048,
                'validity_days': 180,
                'auto_renew': True,
                'renewal_threshold_days': 14,
                'subject': {
                    'O': 'IA Influencer Agent',
                    'OU': 'Microservices',
                    'C': 'DE'
                }
            }
        }
        
        # Platform-specific domain mappings
        self.platform_domains = {
            'api_gateway': [
                'api.ia-influencer.com',
                'gateway.ia-influencer.com',
                'api-staging.ia-influencer.com'
            ],
            'youtube_integration': [
                'youtube-api.ia-influencer.com',
                'yt-webhook.ia-influencer.com'
            ],
            'instagram_integration': [
                'instagram-api.ia-influencer.com',
                'ig-webhook.ia-influencer.com'
            ],
            'tiktok_integration': [
                'tiktok-api.ia-influencer.com',
                'tt-webhook.ia-influencer.com'
            ],
            'spotify_integration': [
                'spotify-api.ia-influencer.com',
                'spotify-webhook.ia-influencer.com'
            ],
            'payment_processing': [
                'payments.ia-influencer.com',
                'secure-pay.ia-influencer.com',
                'pci.ia-influencer.com'
            ],
            'ai_models': [
                'ai-api.ia-influencer.com',
                'ml-models.ia-influencer.com',
                'inference.ia-influencer.com'
            ],
            'cdn': [
                'cdn.ia-influencer.com',
                'assets.ia-influencer.com',
                'media.ia-influencer.com'
            ],
            'admin_dashboard': [
                'admin.ia-influencer.com',
                'dashboard.ia-influencer.com'
            ],
            'user_interface': [
                'app.ia-influencer.com',
                'portal.ia-influencer.com'
            ]
        }
        
        logger.info("InfluencerCertificateManager initialized")
    
    def setup_platform_certificates(
        self,
        environment: str = "production",
        use_lets_encrypt: bool = True,
        lets_encrypt_email: str = "admin@ia-influencer.com"
    ) -> Dict[str, Any]:
        """
        Setup all platform certificates for IA Influencer Agent.
        
        Args:
            environment: Environment (production, staging, development)
            use_lets_encrypt: Use Let's Encrypt for certificate generation
            lets_encrypt_email: Email for Let's Encrypt registration
            
        Returns:
            dict: Setup results
        """
        try:
            setup_results = {
                'environment': environment,
                'timestamp': datetime.utcnow().isoformat(),
                'certificates_created': {},
                'failed_certificates': {},
                'total_certificates': 0,
                'successful_certificates': 0
            }
            
            # Adjust domains based on environment
            domain_suffix = {
                'production': '',
                'staging': '-staging',
                'development': '-dev'
            }.get(environment, '-dev')
            
            # Setup API Gateway certificates
            api_gateway_result = self._setup_api_gateway_certificates(
                environment, domain_suffix, use_lets_encrypt, lets_encrypt_email
            )
            setup_results['certificates_created']['api_gateway'] = api_gateway_result
            
            # Setup platform integration certificates
            platform_results = self._setup_platform_integration_certificates(
                environment, domain_suffix, use_lets_encrypt, lets_encrypt_email
            )
            setup_results['certificates_created']['platform_integrations'] = platform_results
            
            # Setup payment processing certificates
            payment_result = self._setup_payment_processing_certificates(
                environment, domain_suffix, use_lets_encrypt, lets_encrypt_email
            )
            setup_results['certificates_created']['payment_processing'] = payment_result
            
            # Setup AI model certificates
            ai_model_result = self._setup_ai_model_certificates(
                environment, domain_suffix, use_lets_encrypt, lets_encrypt_email
            )
            setup_results['certificates_created']['ai_models'] = ai_model_result
            
            # Setup CDN certificates
            cdn_result = self._setup_cdn_certificates(
                environment, domain_suffix, use_lets_encrypt, lets_encrypt_email
            )
            setup_results['certificates_created']['cdn'] = cdn_result
            
            # Setup microservices certificates
            microservices_result = self._setup_microservices_certificates(
                environment, domain_suffix
            )
            setup_results['certificates_created']['microservices'] = microservices_result
            
            # Calculate totals
            for category_results in setup_results['certificates_created'].values():
                if isinstance(category_results, dict):
                    for result in category_results.values():
                        setup_results['total_certificates'] += 1
                        if result.get('success', False):
                            setup_results['successful_certificates'] += 1
                        else:
                            setup_results['failed_certificates'][result.get('domain', 'unknown')] = result.get('error', 'Unknown error')
            
            logger.info(f"Platform certificate setup completed: {setup_results['successful_certificates']}/{setup_results['total_certificates']} successful")
            return setup_results
            
        except Exception as e:
            logger.error(f"Platform certificate setup failed: {e}")
            return {
                'environment': environment,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def setup_payment_pci_certificates(
        self,
        compliance_level: str = "level_1",
        validity_days: int = 90
    ) -> Dict[str, Any]:
        """
        Setup PCI-DSS compliant certificates for payment processing.
        
        Args:
            compliance_level: PCI compliance level (level_1, level_2, level_3, level_4)
            validity_days: Certificate validity in days
            
        Returns:
            dict: PCI certificate setup results
        """
        try:
            pci_results = {
                'compliance_level': compliance_level,
                'validity_days': validity_days,
                'timestamp': datetime.utcnow().isoformat(),
                'certificates': {},
                'compliance_checks': {}
            }
            
            # PCI compliance requirements based on level
            pci_requirements = {
                'level_1': {
                    'key_size': 4096,
                    'validity_days': 90,
                    'renewal_threshold': 7,
                    'encryption_algorithm': 'RSA',
                    'certificate_transparency': True
                },
                'level_2': {
                    'key_size': 2048,
                    'validity_days': 180,
                    'renewal_threshold': 14,
                    'encryption_algorithm': 'RSA',
                    'certificate_transparency': True
                },
                'level_3': {
                    'key_size': 2048,
                    'validity_days': 365,
                    'renewal_threshold': 30,
                    'encryption_algorithm': 'RSA',
                    'certificate_transparency': False
                },
                'level_4': {
                    'key_size': 2048,
                    'validity_days': 365,
                    'renewal_threshold': 30,
                    'encryption_algorithm': 'RSA',
                    'certificate_transparency': False
                }
            }
            
            requirements = pci_requirements.get(compliance_level, pci_requirements['level_1'])
            
            # Payment endpoint domains
            payment_domains = [
                'payments.ia-influencer.com',
                'secure-pay.ia-influencer.com',
                'pci-gateway.ia-influencer.com',
                'stripe-webhook.ia-influencer.com',
                'paypal-webhook.ia-influencer.com',
                'payment-api.ia-influencer.com'
            ]
            
            for domain in payment_domains:
                cert_request = CertificateRequest(
                    common_name=domain,
                    certificate_type=CertificateType.SSL_TLS,
                    key_type=KeyType.RSA_4096 if requirements['key_size'] == 4096 else KeyType.RSA_2048,
                    subject={
                        'O': 'IA Influencer Agent',
                        'OU': 'PCI Payment Processing',
                        'C': 'DE',
                        'ST': 'Berlin',
                        'L': 'Berlin'
                    },
                    san_list=[domain],
                    validity_days=requirements['validity_days'],
                    auto_renew=True,
                    renewal_threshold_days=requirements['renewal_threshold'],
                    use_lets_encrypt=True,
                    lets_encrypt_email="security@ia-influencer.com",
                    metadata={
                        'pci_compliance_level': compliance_level,
                        'certificate_transparency': requirements['certificate_transparency'],
                        'encryption_algorithm': requirements['encryption_algorithm'],
                        'purpose': 'payment_processing'
                    }
                )
                
                cert_id = self.generate_certificate(cert_request)
                
                if cert_id:
                    pci_results['certificates'][domain] = {
                        'cert_id': cert_id,
                        'success': True,
                        'compliance_level': compliance_level,
                        'key_size': requirements['key_size'],
                        'validity_days': requirements['validity_days']
                    }
                    logger.info(f"PCI certificate generated for {domain}: {cert_id}")
                else:
                    pci_results['certificates'][domain] = {
                        'success': False,
                        'error': 'Certificate generation failed'
                    }
                    logger.error(f"Failed to generate PCI certificate for {domain}")
            
            # Perform compliance checks
            pci_results['compliance_checks'] = self._perform_pci_compliance_checks(pci_results['certificates'])
            
            return pci_results
            
        except Exception as e:
            logger.error(f"PCI certificate setup failed: {e}")
            return {
                'compliance_level': compliance_level,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def setup_ai_model_certificates(
        self,
        ai_providers: List[str] = None
    ) -> Dict[str, Any]:
        """
        Setup certificates for AI model API integrations.
        
        Args:
            ai_providers: List of AI providers (openai, anthropic, huggingface, etc.)
            
        Returns:
            dict: AI model certificate setup results
        """
        try:
            if ai_providers is None:
                ai_providers = ['openai', 'anthropic', 'huggingface', 'google_ai', 'aws_bedrock']
            
            ai_results = {
                'providers': ai_providers,
                'timestamp': datetime.utcnow().isoformat(),
                'certificates': {},
                'webhook_certificates': {}
            }
            
            for provider in ai_providers:
                # API endpoint certificates
                api_domain = f"{provider}-api.ia-influencer.com"
                webhook_domain = f"{provider}-webhook.ia-influencer.com"
                
                # API certificate
                api_cert_request = CertificateRequest(
                    common_name=api_domain,
                    certificate_type=CertificateType.SSL_TLS,
                    key_type=KeyType.RSA_2048,
                    subject={
                        'O': 'IA Influencer Agent',
                        'OU': f'AI Integration - {provider.title()}',
                        'C': 'DE'
                    },
                    san_list=[api_domain],
                    validity_days=365,
                    auto_renew=True,
                    renewal_threshold_days=21,
                    use_lets_encrypt=True,
                    lets_encrypt_email="ai-team@ia-influencer.com",
                    metadata={
                        'ai_provider': provider,
                        'certificate_type': 'api_endpoint',
                        'high_security': True
                    }
                )
                
                api_cert_id = self.generate_certificate(api_cert_request)
                
                if api_cert_id:
                    ai_results['certificates'][provider] = {
                        'api_cert_id': api_cert_id,
                        'api_domain': api_domain,
                        'success': True
                    }
                else:
                    ai_results['certificates'][provider] = {
                        'api_domain': api_domain,
                        'success': False,
                        'error': 'API certificate generation failed'
                    }
                
                # Webhook certificate
                webhook_cert_request = CertificateRequest(
                    common_name=webhook_domain,
                    certificate_type=CertificateType.SSL_TLS,
                    key_type=KeyType.RSA_2048,
                    subject={
                        'O': 'IA Influencer Agent',
                        'OU': f'AI Webhooks - {provider.title()}',
                        'C': 'DE'
                    },
                    san_list=[webhook_domain],
                    validity_days=180,
                    auto_renew=True,
                    renewal_threshold_days=14,
                    use_lets_encrypt=True,
                    lets_encrypt_email="ai-team@ia-influencer.com",
                    metadata={
                        'ai_provider': provider,
                        'certificate_type': 'webhook_endpoint',
                        'webhook_security': True
                    }
                )
                
                webhook_cert_id = self.generate_certificate(webhook_cert_request)
                
                if webhook_cert_id:
                    if provider in ai_results['certificates']:
                        ai_results['certificates'][provider]['webhook_cert_id'] = webhook_cert_id
                        ai_results['certificates'][provider]['webhook_domain'] = webhook_domain
                    else:
                        ai_results['webhook_certificates'][provider] = {
                            'webhook_cert_id': webhook_cert_id,
                            'webhook_domain': webhook_domain,
                            'success': True
                        }
                else:
                    ai_results['webhook_certificates'][provider] = {
                        'webhook_domain': webhook_domain,
                        'success': False,
                        'error': 'Webhook certificate generation failed'
                    }
            
            logger.info(f"AI model certificates setup completed for {len(ai_providers)} providers")
            return ai_results
            
        except Exception as e:
            logger.error(f"AI model certificate setup failed: {e}")
            return {
                'providers': ai_providers or [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def setup_content_delivery_certificates(
        self,
        cdn_regions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Setup certificates for content delivery network endpoints.
        
        Args:
            cdn_regions: List of CDN regions (us-east, eu-west, asia-pacific, etc.)
            
        Returns:
            dict: CDN certificate setup results
        """
        try:
            if cdn_regions is None:
                cdn_regions = ['us-east', 'eu-west', 'asia-pacific', 'global']
            
            cdn_results = {
                'regions': cdn_regions,
                'timestamp': datetime.utcnow().isoformat(),
                'certificates': {},
                'performance_optimized': True
            }
            
            for region in cdn_regions:
                # CDN endpoint domains
                domains = [
                    f"cdn-{region}.ia-influencer.com",
                    f"assets-{region}.ia-influencer.com",
                    f"media-{region}.ia-influencer.com",
                    f"static-{region}.ia-influencer.com"
                ]
                
                # Use ECDSA for better performance
                cert_request = CertificateRequest(
                    common_name=f"cdn-{region}.ia-influencer.com",
                    certificate_type=CertificateType.SSL_TLS,
                    key_type=KeyType.ECDSA_P256,  # Better performance for CDN
                    subject={
                        'O': 'IA Influencer Agent',
                        'OU': f'CDN - {region.upper()}',
                        'C': 'DE'
                    },
                    san_list=domains,
                    validity_days=365,
                    auto_renew=True,
                    renewal_threshold_days=30,
                    use_lets_encrypt=True,
                    lets_encrypt_email="cdn-team@ia-influencer.com",
                    metadata={
                        'cdn_region': region,
                        'performance_optimized': True,
                        'compression_enabled': True,
                        'http2_enabled': True,
                        'certificate_type': 'cdn_endpoint'
                    }
                )
                
                cert_id = self.generate_certificate(cert_request)
                
                if cert_id:
                    cdn_results['certificates'][region] = {
                        'cert_id': cert_id,
                        'domains': domains,
                        'key_type': 'ECDSA-P256',
                        'success': True
                    }
                    logger.info(f"CDN certificate generated for region {region}: {cert_id}")
                else:
                    cdn_results['certificates'][region] = {
                        'domains': domains,
                        'success': False,
                        'error': 'CDN certificate generation failed'
                    }
                    logger.error(f"Failed to generate CDN certificate for region {region}")
            
            return cdn_results
            
        except Exception as e:
            logger.error(f"CDN certificate setup failed: {e}")
            return {
                'regions': cdn_regions or [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def generate_microservice_client_certificates(
        self,
        services: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate client certificates for microservice authentication.
        
        Args:
            services: List of microservice names
            
        Returns:
            dict: Microservice certificate generation results
        """
        try:
            if services is None:
                services = [
                    'user-service',
                    'content-service',
                    'analytics-service',
                    'payment-service',
                    'notification-service',
                    'ai-service',
                    'monitoring-service',
                    'security-service'
                ]
            
            microservice_results = {
                'services': services,
                'timestamp': datetime.utcnow().isoformat(),
                'certificates': {},
                'ca_certificate': None
            }
            
            # Generate or use existing CA certificate for microservices
            ca_cert_id = self._setup_microservices_ca()
            if ca_cert_id:
                microservice_results['ca_certificate'] = ca_cert_id
            
            for service in services:
                # Client certificate for service-to-service communication
                cert_request = CertificateRequest(
                    common_name=f"{service}.ia-influencer.internal",
                    certificate_type=CertificateType.CLIENT_AUTH,
                    key_type=KeyType.RSA_2048,
                    subject={
                        'O': 'IA Influencer Agent',
                        'OU': 'Microservices',
                        'CN': f"{service}.ia-influencer.internal"
                    },
                    san_list=[
                        f"{service}.ia-influencer.internal",
                        f"{service}.default.svc.cluster.local",
                        f"{service}-svc.default.svc.cluster.local"
                    ],
                    validity_days=180,
                    auto_renew=True,
                    renewal_threshold_days=14,
                    metadata={
                        'service_name': service,
                        'certificate_type': 'microservice_client',
                        'internal_communication': True,
                        'kubernetes_service': True
                    }
                )
                
                cert_id = self.generate_certificate(cert_request)
                
                if cert_id:
                    microservice_results['certificates'][service] = {
                        'cert_id': cert_id,
                        'service_name': service,
                        'internal_domain': f"{service}.ia-influencer.internal",
                        'kubernetes_domains': [
                            f"{service}.default.svc.cluster.local",
                            f"{service}-svc.default.svc.cluster.local"
                        ],
                        'success': True
                    }
                    logger.info(f"Microservice certificate generated for {service}: {cert_id}")
                else:
                    microservice_results['certificates'][service] = {
                        'service_name': service,
                        'success': False,
                        'error': 'Microservice certificate generation failed'
                    }
                    logger.error(f"Failed to generate microservice certificate for {service}")
            
            return microservice_results
            
        except Exception as e:
            logger.error(f"Microservice certificate generation failed: {e}")
            return {
                'services': services or [],
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def audit_platform_certificates(self) -> Dict[str, Any]:
        """
        Audit all platform certificates for compliance and security.
        
        Returns:
            dict: Certificate audit results
        """
        try:
            audit_results = {
                'audit_id': f"platform_cert_audit_{int(datetime.utcnow().timestamp())}",
                'timestamp': datetime.utcnow().isoformat(),
                'total_certificates': len(self.certificates),
                'certificate_audits': {},
                'compliance_summary': {
                    'pci_compliant_certs': 0,
                    'expired_certs': 0,
                    'expiring_soon_certs': 0,
                    'weak_key_certs': 0,
                    'non_compliant_certs': 0
                },
                'security_issues': [],
                'recommendations': []
            }
            
            for cert_id, cert_info in self.certificates.items():
                cert_audit = {
                    'cert_id': cert_id,
                    'common_name': cert_info.common_name,
                    'certificate_type': cert_info.certificate_type.value,
                    'key_type': cert_info.key_type.value,
                    'status': cert_info.status.value,
                    'compliance_checks': {},
                    'security_checks': {},
                    'issues': [],
                    'recommendations': []
                }
                
                # Expiry check
                if cert_info.not_after:
                    days_until_expiry = (cert_info.not_after - datetime.utcnow()).days
                    cert_audit['days_until_expiry'] = days_until_expiry
                    
                    if days_until_expiry < 0:
                        cert_audit['issues'].append('Certificate has expired')
                        audit_results['compliance_summary']['expired_certs'] += 1
                    elif days_until_expiry <= 30:
                        cert_audit['issues'].append('Certificate expires within 30 days')
                        audit_results['compliance_summary']['expiring_soon_certs'] += 1
                
                # Key strength check
                if cert_info.key_type in [KeyType.RSA_2048, KeyType.ECDSA_P256]:
                    cert_audit['security_checks']['key_strength'] = 'adequate'
                elif cert_info.key_type == KeyType.RSA_4096:
                    cert_audit['security_checks']['key_strength'] = 'strong'
                else:
                    cert_audit['security_checks']['key_strength'] = 'weak'
                    cert_audit['issues'].append('Weak key strength')
                    audit_results['compliance_summary']['weak_key_certs'] += 1
                
                # PCI compliance check for payment certificates
                if 'payment' in cert_info.common_name.lower() or 'pci' in cert_info.metadata.get('purpose', ''):
                    pci_compliant = self._check_pci_certificate_compliance(cert_info)
                    cert_audit['compliance_checks']['pci_dss'] = pci_compliant
                    if pci_compliant:
                        audit_results['compliance_summary']['pci_compliant_certs'] += 1
                    else:
                        cert_audit['issues'].append('PCI-DSS compliance issues')
                        audit_results['compliance_summary']['non_compliant_certs'] += 1
                
                # SAN check
                if not cert_info.san_list and cert_info.certificate_type == CertificateType.SSL_TLS:
                    cert_audit['issues'].append('Missing Subject Alternative Names')
                
                # Auto-renewal check
                if not cert_info.auto_renew:
                    cert_audit['recommendations'].append('Enable auto-renewal')
                
                audit_results['certificate_audits'][cert_id] = cert_audit
            
            # Generate overall security issues and recommendations
            audit_results['security_issues'] = self._generate_security_issues(audit_results)
            audit_results['recommendations'] = self._generate_audit_recommendations(audit_results)
            
            logger.info(f"Platform certificate audit completed: {audit_results['audit_id']}")
            return audit_results
            
        except Exception as e:
            logger.error(f"Platform certificate audit failed: {e}")
            return {
                'audit_id': f"failed_audit_{int(datetime.utcnow().timestamp())}",
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def rotate_platform_certificates(
        self,
        certificate_category: str = "all",
        emergency_rotation: bool = False
    ) -> Dict[str, Any]:
        """
        Rotate platform certificates by category.
        
        Args:
            certificate_category: Category to rotate (payment, api, cdn, microservices, all)
            emergency_rotation: Perform emergency rotation (immediate)
            
        Returns:
            dict: Certificate rotation results
        """
        try:
            rotation_results = {
                'rotation_id': f"platform_rotation_{int(datetime.utcnow().timestamp())}",
                'category': certificate_category,
                'emergency_rotation': emergency_rotation,
                'timestamp': datetime.utcnow().isoformat(),
                'rotated_certificates': {},
                'failed_rotations': {},
                'total_rotations': 0,
                'successful_rotations': 0
            }
            
            # Filter certificates by category
            certificates_to_rotate = self._filter_certificates_by_category(certificate_category)
            
            for cert_id, cert_info in certificates_to_rotate.items():
                try:
                    # Check if rotation is needed
                    if not emergency_rotation:
                        days_until_expiry = (cert_info.not_after - datetime.utcnow()).days
                        if days_until_expiry > cert_info.renewal_threshold_days:
                            continue
                    
                    # Perform rotation
                    rotation_success = self.renew_certificate(cert_id, force=emergency_rotation)
                    
                    rotation_results['total_rotations'] += 1
                    
                    if rotation_success:
                        rotation_results['rotated_certificates'][cert_id] = {
                            'cert_id': cert_id,
                            'common_name': cert_info.common_name,
                            'category': self._get_certificate_category(cert_info),
                            'rotation_time': datetime.utcnow().isoformat(),
                            'success': True
                        }
                        rotation_results['successful_rotations'] += 1
                        logger.info(f"Certificate rotated successfully: {cert_id}")
                    else:
                        rotation_results['failed_rotations'][cert_id] = {
                            'cert_id': cert_id,
                            'common_name': cert_info.common_name,
                            'error': 'Rotation failed',
                            'category': self._get_certificate_category(cert_info)
                        }
                        logger.error(f"Certificate rotation failed: {cert_id}")
                        
                except Exception as cert_error:
                    rotation_results['failed_rotations'][cert_id] = {
                        'cert_id': cert_id,
                        'common_name': cert_info.common_name,
                        'error': str(cert_error),
                        'category': self._get_certificate_category(cert_info)
                    }
                    logger.error(f"Certificate rotation error for {cert_id}: {cert_error}")
            
            logger.info(f"Platform certificate rotation completed: {rotation_results['successful_rotations']}/{rotation_results['total_rotations']} successful")
            return rotation_results
            
        except Exception as e:
            logger.error(f"Platform certificate rotation failed: {e}")
            return {
                'rotation_id': f"failed_rotation_{int(datetime.utcnow().timestamp())}",
                'category': certificate_category,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Helper methods for InfluencerCertificateManager
    
    def _setup_api_gateway_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup API Gateway certificates."""
        api_domains = [
            f"api{domain_suffix}.ia-influencer.com",
            f"gateway{domain_suffix}.ia-influencer.com",
            f"api-v1{domain_suffix}.ia-influencer.com",
            f"api-v2{domain_suffix}.ia-influencer.com"
        ]
        
        results = {}
        
        for domain in api_domains:
            template = self.platform_templates['api_gateway'].copy()
            
            cert_request = CertificateRequest(
                common_name=domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'].copy(),
                san_list=[domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'certificate_category': 'api_gateway',
                    'high_availability': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            if cert_id:
                results[domain] = {
                    'cert_id': cert_id,
                    'domain': domain,
                    'success': True,
                    'category': 'api_gateway'
                }
            else:
                results[domain] = {
                    'domain': domain,
                    'success': False,
                    'error': 'Certificate generation failed',
                    'category': 'api_gateway'
                }
        
        return results
    
    def _setup_platform_integration_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup platform integration certificates."""
        platforms = ['youtube', 'instagram', 'tiktok', 'spotify', 'twitter', 'linkedin', 'twitch']
        results = {}
        
        for platform in platforms:
            platform_domains = [
                f"{platform}-api{domain_suffix}.ia-influencer.com",
                f"{platform}-webhook{domain_suffix}.ia-influencer.com",
                f"{platform}-auth{domain_suffix}.ia-influencer.com"
            ]
            
            for domain in platform_domains:
                template = self.platform_templates['platform_endpoints'].copy()
                
                cert_request = CertificateRequest(
                    common_name=domain,
                    certificate_type=template['certificate_type'],
                    key_type=template['key_type'],
                    subject=template['subject'].copy(),
                    san_list=[domain],
                    validity_days=template['validity_days'],
                    auto_renew=template['auto_renew'],
                    renewal_threshold_days=template['renewal_threshold_days'],
                    use_lets_encrypt=use_lets_encrypt,
                    lets_encrypt_email=lets_encrypt_email,
                    metadata={
                        'environment': environment,
                        'platform': platform,
                        'certificate_category': 'platform_integration',
                        'api_integration': True
                    }
                )
                
                cert_id = self.generate_certificate(cert_request)
                
                if cert_id:
                    results[domain] = {
                        'cert_id': cert_id,
                        'domain': domain,
                        'platform': platform,
                        'success': True,
                        'category': 'platform_integration'
                    }
                else:
                    results[domain] = {
                        'domain': domain,
                        'platform': platform,
                        'success': False,
                        'error': 'Certificate generation failed',
                        'category': 'platform_integration'
                    }
        
        return results
    
    def _setup_payment_processing_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup payment processing certificates."""
        payment_domains = [
            f"payments{domain_suffix}.ia-influencer.com",
            f"secure-pay{domain_suffix}.ia-influencer.com",
            f"pci-gateway{domain_suffix}.ia-influencer.com",
            f"stripe-webhook{domain_suffix}.ia-influencer.com",
            f"paypal-webhook{domain_suffix}.ia-influencer.com",
            f"wise-webhook{domain_suffix}.ia-influencer.com"
        ]
        
        results = {}
        
        for domain in payment_domains:
            template = self.platform_templates['payment_endpoints'].copy()
            
            cert_request = CertificateRequest(
                common_name=domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'].copy(),
                san_list=[domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email="security@ia-influencer.com",  # Use security email for payments
                metadata={
                    'environment': environment,
                    'certificate_category': 'payment_processing',
                    'pci_dss_compliant': True,
                    'high_security': True,
                    'audit_required': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            if cert_id:
                results[domain] = {
                    'cert_id': cert_id,
                    'domain': domain,
                    'success': True,
                    'category': 'payment_processing',
                    'pci_compliant': True
                }
            else:
                results[domain] = {
                    'domain': domain,
                    'success': False,
                    'error': 'Certificate generation failed',
                    'category': 'payment_processing'
                }
        
        return results
    
    def _setup_ai_model_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup AI model certificates."""
        ai_domains = [
            f"ai-api{domain_suffix}.ia-influencer.com",
            f"ml-models{domain_suffix}.ia-influencer.com",
            f"inference{domain_suffix}.ia-influencer.com",
            f"openai-proxy{domain_suffix}.ia-influencer.com",
            f"anthropic-proxy{domain_suffix}.ia-influencer.com",
            f"huggingface-proxy{domain_suffix}.ia-influencer.com"
        ]
        
        results = {}
        
        for domain in ai_domains:
            template = self.platform_templates['ai_model_endpoints'].copy()
            
            cert_request = CertificateRequest(
                common_name=domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'].copy(),
                san_list=[domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'certificate_category': 'ai_models',
                    'ai_integration': True,
                    'rate_limiting': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            if cert_id:
                results[domain] = {
                    'cert_id': cert_id,
                    'domain': domain,
                    'success': True,
                    'category': 'ai_models'
                }
            else:
                results[domain] = {
                    'domain': domain,
                    'success': False,
                    'error': 'Certificate generation failed',
                    'category': 'ai_models'
                }
        
        return results
    
    def _setup_cdn_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup CDN certificates."""
        cdn_domains = [
            f"cdn{domain_suffix}.ia-influencer.com",
            f"assets{domain_suffix}.ia-influencer.com",
            f"media{domain_suffix}.ia-influencer.com",
            f"static{domain_suffix}.ia-influencer.com"
        ]
        
        results = {}
        
        for domain in cdn_domains:
            template = self.platform_templates['cdn_endpoints'].copy()
            
            cert_request = CertificateRequest(
                common_name=domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'].copy(),
                san_list=[domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'certificate_category': 'cdn',
                    'content_delivery': True,
                    'performance_optimized': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            if cert_id:
                results[domain] = {
                    'cert_id': cert_id,
                    'domain': domain,
                    'success': True,
                    'category': 'cdn'
                }
            else:
                results[domain] = {
                    'domain': domain,
                    'success': False,
                    'error': 'Certificate generation failed',
                    'category': 'cdn'
                }
        
        return results
    
    def _setup_microservices_certificates(
        self,
        environment: str,
        domain_suffix: str
    ) -> Dict[str, Any]:
        """Setup microservices certificates."""
        services = [
            'user-service',
            'content-service',
            'analytics-service',
            'payment-service',
            'notification-service',
            'ai-service',
            'monitoring-service',
            'security-service'
        ]
        
        results = {}
        
        for service in services:
            service_domain = f"{service}{domain_suffix}.ia-influencer.internal"
            template = self.platform_templates['microservices'].copy()
            
            cert_request = CertificateRequest(
                common_name=service_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'].copy(),
                san_list=[
                    service_domain,
                    f"{service}.default.svc.cluster.local",
                    f"{service}-svc.default.svc.cluster.local"
                ],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=False,  # Internal certificates
                metadata={
                    'environment': environment,
                    'service_name': service,
                    'certificate_category': 'microservices',
                    'internal_communication': True,
                    'kubernetes_service': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            if cert_id:
                results[service] = {
                    'cert_id': cert_id,
                    'service': service,
                    'domain': service_domain,
                    'success': True,
                    'category': 'microservices'
                }
            else:
                results[service] = {
                    'service': service,
                    'domain': service_domain,
                    'success': False,
                    'error': 'Certificate generation failed',
                    'category': 'microservices'
                }
        
        return results
    
    def _setup_microservices_ca(self) -> Optional[str]:
        """Setup or retrieve microservices CA certificate."""
        try:
            # Check if CA already exists
            ca_path = "ia-influencer/ca/microservices"
            existing_ca = self.vault.get_secret(ca_path)
            
            if existing_ca:
                return existing_ca.get('metadata', {}).get('certificate_id')
            
            # Generate new CA certificate
            ca_request = CertificateRequest(
                common_name="IA Influencer Microservices CA",
                certificate_type=CertificateType.ROOT_CA,
                key_type=KeyType.RSA_4096,
                subject={
                    'O': 'IA Influencer Agent',
                    'OU': 'Internal Certificate Authority',
                    'C': 'DE',
                    'CN': 'IA Influencer Microservices CA'
                },
                validity_days=3650,  # 10 years for CA
                auto_renew=True,
                renewal_threshold_days=365,
                vault_path=ca_path,
                metadata={
                    'certificate_type': 'root_ca',
                    'purpose': 'microservices_authentication',
                    'internal_ca': True
                }
            )
            
            ca_cert_id = self.generate_certificate(ca_request)
            logger.info(f"Microservices CA certificate created: {ca_cert_id}")
            return ca_cert_id
            
        except Exception as e:
            logger.error(f"Failed to setup microservices CA: {e}")
            return None
    
    def _perform_pci_compliance_checks(self, certificates: Dict[str, Any]) -> Dict[str, Any]:
        """Perform PCI compliance checks on payment certificates."""
        compliance_results = {
            'total_certificates': len(certificates),
            'compliant_certificates': 0,
            'non_compliant_certificates': 0,
            'compliance_issues': [],
            'recommendations': []
        }
        
        for domain, cert_info in certificates.items():
            if cert_info.get('success', False):
                cert_id = cert_info['cert_id']
                cert_details = self.certificates.get(cert_id)
                
                if cert_details:
                    # Check key size
                    if cert_details.key_type != KeyType.RSA_4096:
                        compliance_results['compliance_issues'].append(
                            f"{domain}: Key size should be 4096 bits for PCI Level 1"
                        )
                        compliance_results['non_compliant_certificates'] += 1
                    else:
                        compliance_results['compliant_certificates'] += 1
                    
                    # Check validity period
                    validity_days = (cert_details.not_after - cert_details.not_before).days
                    if validity_days > 90:
                        compliance_results['compliance_issues'].append(
                            f"{domain}: Certificate validity should not exceed 90 days for PCI compliance"
                        )
                    
                    # Check renewal threshold
                    if cert_details.renewal_threshold_days > 7:
                        compliance_results['recommendations'].append(
                            f"{domain}: Consider reducing renewal threshold to 7 days for PCI compliance"
                        )
        
        return compliance_results
    
    def _check_pci_certificate_compliance(self, cert_info: CertificateInfo) -> bool:
        """Check if certificate meets PCI-DSS requirements."""
        try:
            # Key size check
            if cert_info.key_type != KeyType.RSA_4096:
                return False
            
            # Validity period check
            if cert_info.not_before and cert_info.not_after:
                validity_days = (cert_info.not_after - cert_info.not_before).days
                if validity_days > 90:
                    return False
            
            # Auto-renewal check
            if not cert_info.auto_renew:
                return False
            
            # Renewal threshold check
            if cert_info.renewal_threshold_days > 7:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"PCI compliance check failed: {e}")
            return False
    
    def _filter_certificates_by_category(self, category: str) -> Dict[str, CertificateInfo]:
        """Filter certificates by category."""
        filtered_certs = {}
        
        for cert_id, cert_info in self.certificates.items():
            cert_category = self._get_certificate_category(cert_info)
            
            if category == "all" or cert_category == category:
                filtered_certs[cert_id] = cert_info
        
        return filtered_certs
    
    def _get_certificate_category(self, cert_info: CertificateInfo) -> str:
        """Get certificate category based on metadata and domain."""
        # Check metadata first
        if 'certificate_category' in cert_info.metadata:
            return cert_info.metadata['certificate_category']
        
        # Check domain patterns
        domain = cert_info.common_name.lower()
        
        if any(keyword in domain for keyword in ['payment', 'pay', 'pci']):
            return 'payment'
        elif any(keyword in domain for keyword in ['api', 'gateway']):
            return 'api'
        elif any(keyword in domain for keyword in ['cdn', 'assets', 'media', 'static']):
            return 'cdn'
        elif any(keyword in domain for keyword in ['ai', 'ml', 'inference']):
            return 'ai'
        elif 'internal' in domain or cert_info.certificate_type == CertificateType.CLIENT_AUTH:
            return 'microservices'
        else:
            return 'general'
    
    def _generate_security_issues(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate security issues from audit results."""
        issues = []
        
        # High-level issues
        if audit_results['compliance_summary']['expired_certs'] > 0:
            issues.append(f"{audit_results['compliance_summary']['expired_certs']} certificates have expired")
        
        if audit_results['compliance_summary']['expiring_soon_certs'] > 0:
            issues.append(f"{audit_results['compliance_summary']['expiring_soon_certs']} certificates expire within 30 days")
        
        if audit_results['compliance_summary']['weak_key_certs'] > 0:
            issues.append(f"{audit_results['compliance_summary']['weak_key_certs']} certificates use weak keys")
        
        if audit_results['compliance_summary']['non_compliant_certs'] > 0:
            issues.append(f"{audit_results['compliance_summary']['non_compliant_certs']} certificates are not PCI-DSS compliant")
        
        return issues
    
    def _generate_audit_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations from audit results."""
        recommendations = []
        
        # Certificate-specific recommendations
        expired_count = audit_results['compliance_summary']['expired_certs']
        expiring_count = audit_results['compliance_summary']['expiring_soon_certs']
        weak_key_count = audit_results['compliance_summary']['weak_key_certs']
        
        if expired_count > 0:
            recommendations.append(f"Immediately renew {expired_count} expired certificates")
        
        if expiring_count > 0:
            recommendations.append(f"Schedule renewal for {expiring_count} certificates expiring soon")
        
        if weak_key_count > 0:
            recommendations.append(f"Upgrade {weak_key_count} certificates to stronger key algorithms")
        
        # General recommendations
        recommendations.extend([
            "Enable automated certificate monitoring",
            "Implement certificate transparency logging",
            "Regular security audits of certificate infrastructure",
            "Consider using ECDSA certificates for better performance",
            "Implement certificate pinning for critical services"
        ])
        
        return recommendations
                    
                    rotation_results['total_rotations'] += 1
                    
                    if rotation_success:
                        rotation_results['rotated_certificates'][cert_id] = {
                            'cert_id': cert_id,
                            'common_name': cert_info.common_name,
                            'category': certificate_category,
                            'success': True,
                            'rotation_time': datetime.utcnow().isoformat()
                        }
                        rotation_results['successful_rotations'] += 1
                        logger.info(f"Certificate rotated successfully: {cert_id}")
                    else:
                        rotation_results['failed_rotations'][cert_id] = {
                            'cert_id': cert_id,
                            'common_name': cert_info.common_name,
                            'error': 'Rotation failed'
                        }
                        logger.error(f"Certificate rotation failed: {cert_id}")
                        
                except Exception as cert_error:
                    rotation_results['failed_rotations'][cert_id] = {
                        'cert_id': cert_id,
                        'common_name': cert_info.common_name,
                        'error': str(cert_error)
                    }
                    logger.error(f"Certificate rotation error for {cert_id}: {cert_error}")
            
            logger.info(f"Platform certificate rotation completed: {rotation_results['successful_rotations']}/{rotation_results['total_rotations']} successful")
            return rotation_results
            
        except Exception as e:
            logger.error(f"Platform certificate rotation failed: {e}")
            return {
                'rotation_id': f"failed_rotation_{int(datetime.utcnow().timestamp())}",
                'category': certificate_category,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Helper methods for platform certificate management
    def _setup_api_gateway_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup API gateway certificates."""
        results = {}
        
        for domain in self.platform_domains['api_gateway']:
            full_domain = f"{domain.replace('.ia-influencer.com', '')}{domain_suffix}.ia-influencer.com"
            
            template = self.platform_templates['api_gateway']
            cert_request = CertificateRequest(
                common_name=full_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'],
                san_list=[full_domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'category': 'api_gateway',
                    'high_availability': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            results[full_domain] = {
                'cert_id': cert_id,
                'success': cert_id is not None,
                'domain': full_domain,
                'category': 'api_gateway'
            }
            
            if not cert_id:
                results[full_domain]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_platform_integration_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup platform integration certificates."""
        results = {}
        
        platforms = ['youtube_integration', 'instagram_integration', 'tiktok_integration', 'spotify_integration']
        
        for platform in platforms:
            for domain in self.platform_domains[platform]:
                full_domain = f"{domain.replace('.ia-influencer.com', '')}{domain_suffix}.ia-influencer.com"
                
                template = self.platform_templates['platform_endpoints']
                cert_request = CertificateRequest(
                    common_name=full_domain,
                    certificate_type=template['certificate_type'],
                    key_type=template['key_type'],
                    subject={
                        **template['subject'],
                        'OU': f"Platform Integration - {platform.replace('_integration', '').title()}"
                    },
                    san_list=[full_domain],
                    validity_days=template['validity_days'],
                    auto_renew=template['auto_renew'],
                    renewal_threshold_days=template['renewal_threshold_days'],
                    use_lets_encrypt=use_lets_encrypt,
                    lets_encrypt_email=lets_encrypt_email,
                    metadata={
                        'environment': environment,
                        'category': 'platform_integration',
                        'platform': platform.replace('_integration', '')
                    }
                )
                
                cert_id = self.generate_certificate(cert_request)
                
                results[full_domain] = {
                    'cert_id': cert_id,
                    'success': cert_id is not None,
                    'domain': full_domain,
                    'platform': platform.replace('_integration', ''),
                    'category': 'platform_integration'
                }
                
                if not cert_id:
                    results[full_domain]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_payment_processing_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup payment processing certificates."""
        results = {}
        
        for domain in self.platform_domains['payment_processing']:
            full_domain = f"{domain.replace('.ia-influencer.com', '')}{domain_suffix}.ia-influencer.com"
            
            template = self.platform_templates['payment_endpoints']
            cert_request = CertificateRequest(
                common_name=full_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'],
                san_list=[full_domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'category': 'payment_processing',
                    'pci_compliant': True,
                    'high_security': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            results[full_domain] = {
                'cert_id': cert_id,
                'success': cert_id is not None,
                'domain': full_domain,
                'category': 'payment_processing',
                'pci_compliant': True
            }
            
            if not cert_id:
                results[full_domain]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_ai_model_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup AI model certificates."""
        results = {}
        
        for domain in self.platform_domains['ai_models']:
            full_domain = f"{domain.replace('.ia-influencer.com', '')}{domain_suffix}.ia-influencer.com"
            
            template = self.platform_templates['ai_model_endpoints']
            cert_request = CertificateRequest(
                common_name=full_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'],
                san_list=[full_domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'category': 'ai_models',
                    'ai_integration': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            results[full_domain] = {
                'cert_id': cert_id,
                'success': cert_id is not None,
                'domain': full_domain,
                'category': 'ai_models'
            }
            
            if not cert_id:
                results[full_domain]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_cdn_certificates(
        self,
        environment: str,
        domain_suffix: str,
        use_lets_encrypt: bool,
        lets_encrypt_email: str
    ) -> Dict[str, Any]:
        """Setup CDN certificates."""
        results = {}
        
        for domain in self.platform_domains['cdn']:
            full_domain = f"{domain.replace('.ia-influencer.com', '')}{domain_suffix}.ia-influencer.com"
            
            template = self.platform_templates['cdn_endpoints']
            cert_request = CertificateRequest(
                common_name=full_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject=template['subject'],
                san_list=[full_domain],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                use_lets_encrypt=use_lets_encrypt,
                lets_encrypt_email=lets_encrypt_email,
                metadata={
                    'environment': environment,
                    'category': 'cdn',
                    'performance_optimized': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            results[full_domain] = {
                'cert_id': cert_id,
                'success': cert_id is not None,
                'domain': full_domain,
                'category': 'cdn'
            }
            
            if not cert_id:
                results[full_domain]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_microservices_certificates(
        self,
        environment: str,
        domain_suffix: str
    ) -> Dict[str, Any]:
        """Setup microservice certificates."""
        results = {}
        
        services = [
            'user-service',
            'content-service',
            'analytics-service',
            'payment-service',
            'notification-service',
            'ai-service'
        ]
        
        for service in services:
            service_domain = f"{service}{domain_suffix}.ia-influencer.internal"
            
            template = self.platform_templates['microservices']
            cert_request = CertificateRequest(
                common_name=service_domain,
                certificate_type=template['certificate_type'],
                key_type=template['key_type'],
                subject={
                    **template['subject'],
                    'CN': service_domain
                },
                san_list=[
                    service_domain,
                    f"{service}.default.svc.cluster.local",
                    f"{service}-svc.default.svc.cluster.local"
                ],
                validity_days=template['validity_days'],
                auto_renew=template['auto_renew'],
                renewal_threshold_days=template['renewal_threshold_days'],
                metadata={
                    'environment': environment,
                    'category': 'microservices',
                    'service_name': service,
                    'internal_communication': True
                }
            )
            
            cert_id = self.generate_certificate(cert_request)
            
            results[service] = {
                'cert_id': cert_id,
                'success': cert_id is not None,
                'service_domain': service_domain,
                'category': 'microservices'
            }
            
            if not cert_id:
                results[service]['error'] = 'Certificate generation failed'
        
        return results
    
    def _setup_microservices_ca(self) -> Optional[str]:
        """Setup Certificate Authority for microservices."""
        try:
            # Check if CA already exists
            ca_cert_path = "certificates/microservices_ca"
            ca_data = self.vault.get_secret(ca_cert_path)
            
            if ca_data:
                # CA already exists
                return ca_data.get('metadata', {}).get('certificate_id')
            
            # Generate new CA
            ca_cert_request = CertificateRequest(
                common_name="IA Influencer Agent Microservices CA",
                certificate_type=CertificateType.ROOT_CA,
                key_type=KeyType.RSA_4096,
                subject={
                    'O': 'IA Influencer Agent',
                    'OU': 'Microservices Certificate Authority',
                    'C': 'DE'
                },
                validity_days=3650,  # 10 years for CA
                auto_renew=False,
                vault_path=ca_cert_path,
                metadata={
                    'certificate_authority': True,
                    'microservices_ca': True
                }
            )
            
            ca_cert_id = self.generate_certificate(ca_cert_request)
            return ca_cert_id
            
        except Exception as e:
            logger.error(f"Microservices CA setup failed: {e}")
            return None
    
    def _perform_pci_compliance_checks(self, certificates: Dict[str, Any]) -> Dict[str, Any]:
        """Perform PCI compliance checks on certificates."""
        compliance_results = {
            'total_certificates': len(certificates),
            'compliant_certificates': 0,
            'non_compliant_certificates': 0,
            'compliance_details': {}
        }
        
        for domain, cert_info in certificates.items():
            if cert_info.get('success', False):
                # Check PCI compliance requirements
                compliant = True
                issues = []
                
                # Check key size (minimum 2048 for PCI)
                if 'key_size' in cert_info and cert_info['key_size'] < 2048:
                    compliant = False
                    issues.append('Key size below PCI minimum (2048 bits)')
                
                # Check validity period (maximum 2 years for PCI)
                if 'validity_days' in cert_info and cert_info['validity_days'] > 730:
                    compliant = False
                    issues.append('Validity period exceeds PCI maximum (2 years)')
                
                compliance_results['compliance_details'][domain] = {
                    'compliant': compliant,
                    'issues': issues
                }
                
                if compliant:
                    compliance_results['compliant_certificates'] += 1
                else:
                    compliance_results['non_compliant_certificates'] += 1
        
        return compliance_results
    
    def _check_pci_certificate_compliance(self, cert_info: CertificateInfo) -> bool:
        """Check if certificate meets PCI-DSS requirements."""
        try:
            # Key strength check
            if cert_info.key_type == KeyType.RSA_2048:
                key_compliant = True
            elif cert_info.key_type == KeyType.RSA_4096:
                key_compliant = True
            else:
                key_compliant = False
            
            # Validity period check (max 2 years for PCI)
            if cert_info.not_before and cert_info.not_after:
                validity_days = (cert_info.not_after - cert_info.not_before).days
                validity_compliant = validity_days <= 730
            else:
                validity_compliant = False
            
            # Auto-renewal check
            renewal_compliant = cert_info.auto_renew
            
            # Renewal threshold check (should be reasonable for PCI)
            threshold_compliant = cert_info.renewal_threshold_days <= 30
            
            return key_compliant and validity_compliant and renewal_compliant and threshold_compliant
            
        except Exception as e:
            logger.error(f"PCI compliance check failed for {cert_info.cert_id}: {e}")
            return False
    
    def _filter_certificates_by_category(self, category: str) -> Dict[str, CertificateInfo]:
        """Filter certificates by category."""
        if category == "all":
            return self.certificates
        
        filtered_certs = {}
        
        for cert_id, cert_info in self.certificates.items():
            cert_category = cert_info.metadata.get('category', '')
            
            if category == "payment" and ('payment' in cert_category or 'pci' in cert_info.common_name.lower()):
                filtered_certs[cert_id] = cert_info
            elif category == "api" and ('api' in cert_category or 'gateway' in cert_info.common_name.lower()):
                filtered_certs[cert_id] = cert_info
            elif category == "cdn" and ('cdn' in cert_category or 'cdn' in cert_info.common_name.lower()):
                filtered_certs[cert_id] = cert_info
            elif category == "microservices" and ('microservices' in cert_category or 'internal' in cert_info.common_name.lower()):
                filtered_certs[cert_id] = cert_info
            elif category == "platform" and 'platform' in cert_category:
                filtered_certs[cert_id] = cert_info
        
        return filtered_certs
    
    def _generate_security_issues(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate list of security issues from audit results."""
        issues = []
        
        summary = audit_results['compliance_summary']
        
        if summary['expired_certs'] > 0:
            issues.append(f"{summary['expired_certs']} certificates have expired")
        
        if summary['expiring_soon_certs'] > 0:
            issues.append(f"{summary['expiring_soon_certs']} certificates expire within 30 days")
        
        if summary['weak_key_certs'] > 0:
            issues.append(f"{summary['weak_key_certs']} certificates use weak key algorithms")
        
        if summary['non_compliant_certs'] > 0:
            issues.append(f"{summary['non_compliant_certs']} certificates are not PCI compliant")
        
        return issues
    
    def _generate_audit_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate audit recommendations."""
        recommendations = []
        
        summary = audit_results['compliance_summary']
        
        if summary['expired_certs'] > 0:
            recommendations.append("Immediately renew all expired certificates")
        
        if summary['expiring_soon_certs'] > 0:
            recommendations.append("Schedule renewal for certificates expiring soon")
        
        if summary['weak_key_certs'] > 0:
            recommendations.append("Upgrade certificates with weak key algorithms")
        
        if summary['non_compliant_certs'] > 0:
            recommendations.append("Update non-compliant certificates to meet PCI-DSS requirements")
        
        recommendations.append("Enable monitoring and alerting for certificate expiry")
        recommendations.append("Implement automated certificate rotation")
        recommendations.append("Regular security audits of certificate infrastructure")
        
        return recommendations
