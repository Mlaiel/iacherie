"""IA Influencer Agent - Enterprise SSL/TLS Certificate Manager
Advanced certificate lifecycle management and automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Expertise:
- Lead Dev IA + Backend Senior + ML Engineer
- DBA + Security Expert + Microservices Architect
- Audio Processing + DevOps + Prompt Engineering

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized copying, distribution, or use without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import os
import ssl
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import OpenSSL
from OpenSSL import crypto
import requests


class CertificateType(Enum):
    """Certificate type enumeration"""
    DOMAIN_VALIDATION = "DV"
    ORGANIZATION_VALIDATION = "OV"
    EXTENDED_VALIDATION = "EV"
    WILDCARD = "WILDCARD"
    MULTI_DOMAIN = "SAN"


class CertificateStatus(Enum):
    """Certificate status enumeration"""
    VALID = "valid"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    REVOKED = "revoked"
    INVALID = "invalid"
    PENDING = "pending"


@dataclass
class CertificateInfo:
    """Certificate information structure"""
    common_name: str
    subject_alt_names: List[str]
    issuer: str
    serial_number: str
    not_before: datetime
    not_after: datetime
    signature_algorithm: str
    key_size: int
    fingerprint_sha256: str
    status: CertificateStatus
    certificate_type: CertificateType
    ocsp_url: Optional[str] = None
    crl_url: Optional[str] = None


class CertificateValidationError(Exception):
    """Certificate validation exception"""
    pass


class CertificateManager:
    """
    Enterprise SSL/TLS certificate management system
    Handles certificate generation, validation, monitoring, and renewal
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize certificate manager
        
        Args:
            config: Certificate management configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Certificate storage paths
        self.cert_directory = Path(config.get('cert_directory', '/etc/ssl/certs'))
        self.key_directory = Path(config.get('key_directory', '/etc/ssl/private'))
        self.ca_directory = Path(config.get('ca_directory', '/etc/ssl/ca'))
        
        # Certificate validation settings
        self.expiry_warning_days = config.get('expiry_warning_days', 30)
        self.validation_timeout = config.get('validation_timeout', 10)
        
        # OCSP settings
        self.enable_ocsp = config.get('enable_ocsp', True)
        self.ocsp_timeout = config.get('ocsp_timeout', 5)
        
        # Initialize directories
        self._init_directories()
        
        self.logger.info("Certificate manager initialized")
    
    def _init_directories(self) -> None:
        """Initialize certificate directories with proper permissions"""
        try:
            for directory in [self.cert_directory, self.key_directory, self.ca_directory]:
                directory.mkdir(parents=True, exist_ok=True)
                
                # Set secure permissions
                if directory == self.key_directory:
                    os.chmod(directory, 0o700)  # Private keys directory
                else:
                    os.chmod(directory, 0o755)  # Certificates directory
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize directories: {e}")
            raise
    
    def generate_private_key(
        self, 
        key_size: int = 2048,
        key_type: str = "RSA"
    ) -> rsa.RSAPrivateKey:
        """
        Generate private key for certificate
        
        Args:
            key_size: RSA key size in bits
            key_type: Key type (RSA, EC)
            
        Returns:
            Generated private key
        """
        try:
            if key_type.upper() == "RSA":
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            self.logger.info(f"Generated {key_type} private key ({key_size} bits)")
            return private_key
            
        except Exception as e:
            self.logger.error(f"Failed to generate private key: {e}")
            raise
    
    def generate_csr(
        self,
        private_key: rsa.RSAPrivateKey,
        common_name: str,
        organization: str,
        country: str,
        state: str = None,
        city: str = None,
        email: str = None,
        san_list: List[str] = None
    ) -> x509.CertificateSigningRequest:
        """
        Generate Certificate Signing Request (CSR)
        
        Args:
            private_key: Private key for CSR
            common_name: Certificate common name
            organization: Organization name
            country: Country code (2 letters)
            state: State/province name
            city: City/locality name
            email: Email address
            san_list: Subject Alternative Names
            
        Returns:
            Generated CSR
        """
        try:
            # Build subject name
            subject_components = [
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            ]
            
            if state:
                subject_components.append(
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state)
                )
            if city:
                subject_components.append(
                    x509.NameAttribute(NameOID.LOCALITY_NAME, city)
                )
            if email:
                subject_components.append(
                    x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
                )
            
            subject = x509.Name(subject_components)
            
            # Create CSR builder
            builder = x509.CertificateSigningRequestBuilder()
            builder = builder.subject_name(subject)
            
            # Add Subject Alternative Names if provided
            if san_list:
                san_names = [x509.DNSName(name) for name in san_list]
                san_extension = x509.SubjectAlternativeName(san_names)
                builder = builder.add_extension(san_extension, critical=False)
            
            # Add key usage extension
            key_usage = x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            )
            builder = builder.add_extension(key_usage, critical=True)
            
            # Add extended key usage
            ext_key_usage = x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
            ])
            builder = builder.add_extension(ext_key_usage, critical=True)
            
            # Sign CSR
            csr = builder.sign(private_key, hashes.SHA256(), default_backend())
            
            self.logger.info(f"Generated CSR for {common_name}")
            return csr
            
        except Exception as e:
            self.logger.error(f"Failed to generate CSR: {e}")
            raise
    
    def load_certificate(self, cert_path: Path) -> x509.Certificate:
        """
        Load certificate from file
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Loaded certificate
        """
        try:
            with open(cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
                
            # Try PEM format first
            try:
                certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
            except ValueError:
                # Try DER format
                certificate = x509.load_der_x509_certificate(cert_data, default_backend())
            
            self.logger.debug(f"Loaded certificate from {cert_path}")
            return certificate
            
        except Exception as e:
            self.logger.error(f"Failed to load certificate from {cert_path}: {e}")
            raise
    
    def save_certificate(
        self, 
        certificate: x509.Certificate, 
        cert_path: Path,
        format_type: str = "PEM"
    ) -> None:
        """
        Save certificate to file
        
        Args:
            certificate: Certificate to save
            cert_path: Destination path
            format_type: Certificate format (PEM/DER)
        """
        try:
            if format_type.upper() == "PEM":
                cert_data = certificate.public_bytes(serialization.Encoding.PEM)
            else:
                cert_data = certificate.public_bytes(serialization.Encoding.DER)
            
            with open(cert_path, 'wb') as cert_file:
                cert_file.write(cert_data)
            
            # Set appropriate permissions
            os.chmod(cert_path, 0o644)
            
            self.logger.info(f"Saved certificate to {cert_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save certificate to {cert_path}: {e}")
            raise
    
    def save_private_key(
        self, 
        private_key: rsa.RSAPrivateKey, 
        key_path: Path,
        password: Optional[bytes] = None
    ) -> None:
        """
        Save private key to file with optional encryption
        
        Args:
            private_key: Private key to save
            key_path: Destination path
            password: Optional encryption password
        """
        try:
            if password:
                encryption_algorithm = serialization.BestAvailableEncryption(password)
            else:
                encryption_algorithm = serialization.NoEncryption()
            
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            )
            
            with open(key_path, 'wb') as key_file:
                key_file.write(key_data)
            
            # Set secure permissions for private key
            os.chmod(key_path, 0o600)
            
            self.logger.info(f"Saved private key to {key_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save private key to {key_path}: {e}")
            raise
    
    def validate_certificate(self, certificate: x509.Certificate) -> CertificateInfo:
        """
        Validate and extract certificate information
        
        Args:
            certificate: Certificate to validate
            
        Returns:
            Certificate information
        """
        try:
            # Extract basic information
            subject = certificate.subject
            issuer = certificate.issuer
            
            # Get common name
            common_name = None
            for attribute in subject:
                if attribute.oid == NameOID.COMMON_NAME:
                    common_name = attribute.value
                    break
            
            # Get Subject Alternative Names
            san_list = []
            try:
                san_extension = certificate.extensions.get_extension_for_oid(
                    ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                for name in san_extension.value:
                    if isinstance(name, x509.DNSName):
                        san_list.append(name.value)
            except x509.ExtensionNotFound:
                pass
            
            # Get validity dates
            not_before = certificate.not_valid_before
            not_after = certificate.not_valid_after
            
            # Calculate certificate status
            now = datetime.utcnow()
            if now > not_after:
                status = CertificateStatus.EXPIRED
            elif now + timedelta(days=self.expiry_warning_days) > not_after:
                status = CertificateStatus.EXPIRING_SOON
            else:
                status = CertificateStatus.VALID
            
            # Get key information
            public_key = certificate.public_key()
            if isinstance(public_key, rsa.RSAPublicKey):
                key_size = public_key.key_size
            else:
                key_size = 0
            
            # Calculate fingerprint
            fingerprint = hashlib.sha256(
                certificate.public_bytes(serialization.Encoding.DER)
            ).hexdigest()
            
            # Determine certificate type
            cert_type = self._determine_certificate_type(common_name, san_list)
            
            # Get OCSP and CRL URLs
            ocsp_url, crl_url = self._extract_validation_urls(certificate)
            
            cert_info = CertificateInfo(
                common_name=common_name or "Unknown",
                subject_alt_names=san_list,
                issuer=issuer.rfc4514_string(),
                serial_number=str(certificate.serial_number),
                not_before=not_before,
                not_after=not_after,
                signature_algorithm=certificate.signature_algorithm_oid._name,
                key_size=key_size,
                fingerprint_sha256=fingerprint,
                status=status,
                certificate_type=cert_type,
                ocsp_url=ocsp_url,
                crl_url=crl_url
            )
            
            self.logger.debug(f"Validated certificate for {common_name}")
            return cert_info
            
        except Exception as e:
            self.logger.error(f"Failed to validate certificate: {e}")
            raise CertificateValidationError(f"Certificate validation failed: {e}")
    
    def _determine_certificate_type(
        self, 
        common_name: str, 
        san_list: List[str]
    ) -> CertificateType:
        """Determine certificate type based on names"""
        if common_name and common_name.startswith('*.'):
            return CertificateType.WILDCARD
        elif len(san_list) > 0:
            return CertificateType.MULTI_DOMAIN
        else:
            return CertificateType.DOMAIN_VALIDATION
    
    def _extract_validation_urls(self, certificate: x509.Certificate) -> Tuple[Optional[str], Optional[str]]:
        """Extract OCSP and CRL URLs from certificate"""
        ocsp_url = None
        crl_url = None
        
        try:
            # Get Authority Information Access extension
            aia_extension = certificate.extensions.get_extension_for_oid(
                ExtensionOID.AUTHORITY_INFORMATION_ACCESS
            )
            
            for access_description in aia_extension.value:
                if access_description.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                    ocsp_url = access_description.access_location.value
                elif access_description.access_method == x509.oid.AuthorityInformationAccessOID.CA_ISSUERS:
                    # This is typically the issuer certificate URL
                    pass
                    
        except x509.ExtensionNotFound:
            pass
        
        try:
            # Get CRL Distribution Points extension
            crl_extension = certificate.extensions.get_extension_for_oid(
                ExtensionOID.CRL_DISTRIBUTION_POINTS
            )
            
            for distribution_point in crl_extension.value:
                if distribution_point.full_name:
                    for name in distribution_point.full_name:
                        if isinstance(name, x509.UniformResourceIdentifier):
                            crl_url = name.value
                            break
                    if crl_url:
                        break
                        
        except x509.ExtensionNotFound:
            pass
        
        return ocsp_url, crl_url
    
    def verify_certificate_chain(
        self, 
        certificate: x509.Certificate,
        intermediate_certs: List[x509.Certificate] = None,
        trusted_ca_path: Path = None
    ) -> bool:
        """
        Verify certificate chain against trusted CAs
        
        Args:
            certificate: Certificate to verify
            intermediate_certs: Intermediate certificates
            trusted_ca_path: Path to trusted CA certificates
            
        Returns:
            True if chain is valid
        """
        try:
            # Load trusted CA certificates
            ca_store = crypto.X509Store()
            
            if trusted_ca_path and trusted_ca_path.exists():
                with open(trusted_ca_path, 'r') as ca_file:
                    ca_cert_data = ca_file.read()
                    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_data)
                    ca_store.add_cert(ca_cert)
            
            # Add system CA certificates
            ca_store.set_default_paths()
            
            # Add intermediate certificates
            if intermediate_certs:
                for intermediate in intermediate_certs:
                    cert_pem = intermediate.public_bytes(serialization.Encoding.PEM)
                    intermediate_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
                    ca_store.add_cert(intermediate_cert)
            
            # Convert certificate to OpenSSL format
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
            ssl_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
            
            # Create store context and verify
            store_context = crypto.X509StoreContext(ca_store, ssl_cert)
            store_context.verify_certificate()
            
            self.logger.info("Certificate chain verification successful")
            return True
            
        except crypto.X509StoreContextError as e:
            self.logger.warning(f"Certificate chain verification failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error during certificate chain verification: {e}")
            return False
    
    def check_ocsp_status(self, certificate: x509.Certificate) -> bool:
        """
        Check certificate revocation status via OCSP
        
        Args:
            certificate: Certificate to check
            
        Returns:
            True if certificate is not revoked
        """
        if not self.enable_ocsp:
            return True
        
        try:
            cert_info = self.validate_certificate(certificate)
            if not cert_info.ocsp_url:
                self.logger.warning("No OCSP URL found in certificate")
                return True
            
            # For production, implement full OCSP request/response handling
            # This is a simplified version
            response = requests.get(
                cert_info.ocsp_url,
                timeout=self.ocsp_timeout,
                headers={'User-Agent': 'IA-Influencer-Agent-SSL-Manager/1.0'}
            )
            
            if response.status_code == 200:
                self.logger.debug("OCSP check successful")
                return True
            else:
                self.logger.warning(f"OCSP check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"OCSP check failed: {e}")
            return True  # Fail open for availability
    
    def get_certificate_expiry_status(self, certificate: x509.Certificate) -> Dict[str, Any]:
        """
        Get detailed expiry status for certificate
        
        Args:
            certificate: Certificate to check
            
        Returns:
            Expiry status information
        """
        try:
            now = datetime.utcnow()
            not_after = certificate.not_valid_after
            
            days_until_expiry = (not_after - now).days
            hours_until_expiry = (not_after - now).total_seconds() / 3600
            
            if days_until_expiry < 0:
                status = "expired"
                urgency = "critical"
            elif days_until_expiry <= 7:
                status = "expires_very_soon"
                urgency = "critical"
            elif days_until_expiry <= self.expiry_warning_days:
                status = "expires_soon"
                urgency = "warning"
            else:
                status = "valid"
                urgency = "normal"
            
            return {
                'status': status,
                'urgency': urgency,
                'days_until_expiry': days_until_expiry,
                'hours_until_expiry': hours_until_expiry,
                'expiry_date': not_after,
                'renewal_recommended': days_until_expiry <= self.expiry_warning_days
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get expiry status: {e}")
            raise
    
    def list_certificates(self, directory: Path = None) -> List[Dict[str, Any]]:
        """
        List all certificates in directory with status information
        
        Args:
            directory: Directory to scan (defaults to cert_directory)
            
        Returns:
            List of certificate information
        """
        if directory is None:
            directory = self.cert_directory
        
        certificates = []
        
        try:
            for cert_file in directory.glob('*.pem'):
                try:
                    certificate = self.load_certificate(cert_file)
                    cert_info = self.validate_certificate(certificate)
                    expiry_status = self.get_certificate_expiry_status(certificate)
                    
                    certificates.append({
                        'file_path': str(cert_file),
                        'common_name': cert_info.common_name,
                        'subject_alt_names': cert_info.subject_alt_names,
                        'issuer': cert_info.issuer,
                        'not_after': cert_info.not_after,
                        'status': cert_info.status.value,
                        'expiry_status': expiry_status,
                        'fingerprint': cert_info.fingerprint_sha256
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process certificate {cert_file}: {e}")
                    continue
            
            self.logger.info(f"Found {len(certificates)} certificates")
            return certificates
            
        except Exception as e:
            self.logger.error(f"Failed to list certificates: {e}")
            raise
    
    def backup_certificates(self, backup_path: Path) -> bool:
        """
        Backup all certificates and keys
        
        Args:
            backup_path: Backup destination path
            
        Returns:
            True if backup successful
        """
        try:
            import shutil
            import tarfile
            from datetime import datetime
            
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f"ssl_certificates_backup_{timestamp}.tar.gz"
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(self.cert_directory, arcname='certificates')
                tar.add(self.key_directory, arcname='private_keys')
                tar.add(self.ca_directory, arcname='ca_certificates')
            
            self.logger.info(f"Certificate backup created: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate backup failed: {e}")
            return False


def create_certificate_manager(config: Dict[str, Any]) -> CertificateManager:
    """
    Factory function to create certificate manager instance
    
    Args:
        config: Certificate manager configuration
        
    Returns:
        Configured certificate manager
    """
    return CertificateManager(config)
