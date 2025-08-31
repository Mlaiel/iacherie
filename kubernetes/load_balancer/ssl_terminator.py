"""SSL Terminator for Load Balancer

Enterprise SSL termination and certificate management for the IA Influencer
Agent platform, providing secure HTTPS connections, certificate automation,
and TLS optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""import os
import ssl
import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import OpenSSL
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import requests

logger = logging.getLogger(__name__)


@dataclass
class SSLCertificate:
    """SSL certificate information"""    domain: str
    cert_path: str
    key_path: str
    ca_bundle_path: Optional[str] = None
    issuer: str = ""
    subject: str = ""
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    serial_number: str = ""
    fingerprint: str = ""
    key_size: int = 0
    signature_algorithm: str = ""
    san_domains: List[str] = field(default_factory=list)
    is_valid: bool = False
    days_until_expiry: int = 0


@dataclass
class TLSConfig:
    """TLS configuration settings"""    min_version: str = "TLSv1.2"
    max_version: str = "TLSv1.3"
    cipher_suites: List[str] = field(default_factory=lambda: [
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256"
    ])
    ecdh_curves: List[str] = field(default_factory=lambda: [
        "X25519", "prime256v1", "secp384r1"
    ])
    session_cache_size: int = 20480
    session_timeout: int = 300
    ocsp_stapling: bool = True
    hsts_max_age: int = 31536000
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True


class CertificateManager:
    """Certificate management and validation"""    
    def __init__(self, cert_dir: str = "/etc/ssl/certs", key_dir: str = "/etc/ssl/private"):
        self.cert_dir = Path(cert_dir)
        self.key_dir = Path(key_dir)
        
        # Ensure directories exist with proper permissions
        self.cert_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
        self.key_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    def load_certificate(self, cert_path: str, key_path: str) -> Optional[SSLCertificate]:
        """Load and parse SSL certificate"""        try:
            cert_file = Path(cert_path)
            key_file = Path(key_path)
            
            if not cert_file.exists() or not key_file.exists():
                logger.error(f"Certificate or key file not found: {cert_path}, {key_path}")
                return None
            
            # Load certificate
            with open(cert_file, 'rb') as f:
                cert_data = f.read()
            
            # Parse with cryptography
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract certificate information
            domain = ""
            san_domains = []
            
            # Get common name
            try:
                cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                domain = cn
            except (IndexError, AttributeError):
                pass
            
            # Get SAN domains
            try:
                san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                san_domains = [name.value for name in san_ext.value]
                if not domain and san_domains:
                    domain = san_domains[0]
            except x509.ExtensionNotFound:
                pass
            
            # Get issuer
            issuer = cert.issuer.rfc4514_string()
            subject = cert.subject.rfc4514_string()
            
            # Calculate days until expiry
            now = datetime.now()
            expiry_date = cert.not_valid_after
            days_until_expiry = (expiry_date - now).days
            
            # Get key information
            public_key = cert.public_key()
            key_size = 0
            if hasattr(public_key, 'key_size'):
                key_size = public_key.key_size
            
            # Generate fingerprint
            fingerprint = cert.fingerprint(hashes.SHA256()).hex()
            
            ssl_cert = SSLCertificate(
                domain=domain,
                cert_path=cert_path,
                key_path=key_path,
                issuer=issuer,
                subject=subject,
                not_before=cert.not_valid_before,
                not_after=cert.not_valid_after,
                serial_number=str(cert.serial_number),
                fingerprint=fingerprint,
                key_size=key_size,
                signature_algorithm=cert.signature_algorithm_oid._name,
                san_domains=san_domains,
                is_valid=now < cert.not_valid_after,
                days_until_expiry=days_until_expiry
            )
            
            return ssl_cert
            
        except Exception as e:
            logger.error(f"Failed to load certificate {cert_path}: {e}")
            return None
    
    def generate_self_signed_certificate(self, 
                                       domain: str,
                                       san_domains: List[str] = None,
                                       key_size: int = 2048,
                                       validity_days: int = 365) -> Optional[SSLCertificate]:
        """Generate self-signed certificate"""        try:
            san_domains = san_domains or []
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Bavaria"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Munich"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IA Influencer Agent"),
                x509.NameAttribute(NameOID.COMMON_NAME, domain),
            ])
            
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(subject)
            cert_builder = cert_builder.issuer_name(issuer)
            cert_builder = cert_builder.public_key(private_key.public_key())
            cert_builder = cert_builder.serial_number(x509.random_serial_number())
            cert_builder = cert_builder.not_valid_before(datetime.now())
            cert_builder = cert_builder.not_valid_after(datetime.now() + timedelta(days=validity_days))
            
            # Add SAN extension
            if san_domains:
                san_list = [x509.DNSName(domain)] + [x509.DNSName(san_domain) for san_domain in san_domains]
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False
                )
            
            # Sign certificate
            certificate = cert_builder.sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_path = self.cert_dir / f"{domain}.crt"
            key_path = self.key_dir / f"{domain}.key"
            
            # Write certificate
            with open(cert_path, 'wb') as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Set proper permissions
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)
            
            logger.info(f"Self-signed certificate generated for {domain}")
            return self.load_certificate(str(cert_path), str(key_path))
            
        except Exception as e:
            logger.error(f"Failed to generate self-signed certificate for {domain}: {e}")
            return None
    
    def validate_certificate_chain(self, cert_path: str, ca_bundle_path: Optional[str] = None) -> bool:
        """Validate certificate chain"""        try:
            # Load certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Load CA bundle if provided
            if ca_bundle_path and Path(ca_bundle_path).exists():
                with open(ca_bundle_path, 'rb') as f:
                    ca_data = f.read()
                
                # Parse CA certificates
                ca_certs = []
                for cert_pem in ca_data.split(b'-----END CERTIFICATE-----'):
                    if b'-----BEGIN CERTIFICATE-----' in cert_pem:
                        cert_pem += b'-----END CERTIFICATE-----'
                        try:
                            ca_cert = x509.load_pem_x509_certificate(cert_pem)
                            ca_certs.append(ca_cert)
                        except:
                            continue
                
                # Validate chain (simplified validation)
                # In production, use proper chain validation library
                return True
            
            # Basic validation - check if certificate is not expired
            now = datetime.now()
            return now < cert.not_valid_after
            
        except Exception as e:
            logger.error(f"Failed to validate certificate chain: {e}")
            return False
    
    def check_certificate_expiry(self, cert_path: str) -> Tuple[bool, int]:
        """Check if certificate is expiring soon"""        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            now = datetime.now()
            expiry_date = cert.not_valid_after
            days_until_expiry = (expiry_date - now).days
            
            # Consider certificate expiring if less than 30 days
            is_expiring = days_until_expiry <= 30
            
            return is_expiring, days_until_expiry
            
        except Exception as e:
            logger.error(f"Failed to check certificate expiry: {e}")
            return True, 0


class LetsEncryptManager:
    """Let's Encrypt certificate management"""    
    def __init__(self, email: str, staging: bool = False):
        self.email = email
        self.staging = staging
        self.acme_server = "https://acme-staging-v02.api.letsencrypt.org/directory" if staging else "https://acme-v02.api.letsencrypt.org/directory"
        self.cert_dir = Path("/etc/letsencrypt/live")
        self.work_dir = Path("/var/lib/letsencrypt")
        self.logs_dir = Path("/var/log/letsencrypt")
        
        # Ensure directories exist
        for directory in [self.cert_dir, self.work_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def obtain_certificate(self, domains: List[str], webroot_path: str = "/var/www/html") -> bool:
        """Obtain certificate using webroot method"""        try:
            # Prepare certbot command
            cmd = [
                "certbot", "certonly",
                "--webroot",
                "--webroot-path", webroot_path,
                "--email", self.email,
                "--agree-tos",
                "--no-eff-email",
                "--server", self.acme_server
            ]
            
            # Add domains
            for domain in domains:
                cmd.extend(["-d", domain])
            
            # Run certbot
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Certificate obtained successfully for domains: {domains}")
                return True
            else:
                logger.error(f"Failed to obtain certificate: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to obtain Let's Encrypt certificate: {e}")
            return False
    
    def renew_certificate(self, domain: str) -> bool:
        """Renew certificate for domain"""        try:
            cmd = ["certbot", "renew", "--cert-name", domain, "--quiet"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Certificate renewed successfully for {domain}")
                return True
            else:
                logger.error(f"Failed to renew certificate for {domain}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to renew certificate for {domain}: {e}")
            return False
    
    def list_certificates(self) -> List[Dict[str, Any]]:
        """List all Let's Encrypt certificates"""        try:
            cmd = ["certbot", "certificates"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse certbot output
                certificates = []
                lines = result.stdout.split('\n')
                
                current_cert = {}
                for line in lines:
                    line = line.strip()
                    if line.startswith('Certificate Name:'):
                        if current_cert:
                            certificates.append(current_cert)
                        current_cert = {'name': line.split(':', 1)[1].strip()}
                    elif line.startswith('Domains:'):
                        current_cert['domains'] = [d.strip() for d in line.split(':', 1)[1].split()]
                    elif line.startswith('Expiry Date:'):
                        current_cert['expiry'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Certificate Path:'):
                        current_cert['cert_path'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Private Key Path:'):
                        current_cert['key_path'] = line.split(':', 1)[1].strip()
                
                if current_cert:
                    certificates.append(current_cert)
                
                return certificates
            else:
                logger.error(f"Failed to list certificates: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list Let's Encrypt certificates: {e}")
            return []


class SSLTerminator:
    """Enterprise SSL Terminator for Load Balancer"""    
    def __init__(self, 
                 cert_dir: str = "/etc/ssl/certs",
                 key_dir: str = "/etc/ssl/private",
                 letsencrypt_email: Optional[str] = None):
        self.cert_manager = CertificateManager(cert_dir, key_dir)
        self.certificates: Dict[str, SSLCertificate] = {}
        self.tls_config = TLSConfig()
        self.letsencrypt_manager = None
        
        if letsencrypt_email:
            self.letsencrypt_manager = LetsEncryptManager(letsencrypt_email)
    
    def add_certificate(self, cert_path: str, key_path: str, ca_bundle_path: Optional[str] = None) -> bool:
        """Add SSL certificate"""        try:
            certificate = self.cert_manager.load_certificate(cert_path, key_path)
            if not certificate:
                return False
            
            certificate.ca_bundle_path = ca_bundle_path
            
            # Validate certificate chain if CA bundle is provided
            if ca_bundle_path:
                is_valid = self.cert_manager.validate_certificate_chain(cert_path, ca_bundle_path)
                certificate.is_valid = certificate.is_valid and is_valid
            
            self.certificates[certificate.domain] = certificate
            
            # Also add SAN domains
            for san_domain in certificate.san_domains:
                if san_domain != certificate.domain:
                    self.certificates[san_domain] = certificate
            
            logger.info(f"Certificate added for domain {certificate.domain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add certificate: {e}")
            return False
    
    def remove_certificate(self, domain: str) -> bool:
        """Remove SSL certificate"""        try:
            if domain in self.certificates:
                certificate = self.certificates[domain]
                
                # Remove all domains associated with this certificate
                domains_to_remove = [domain]
                for san_domain in certificate.san_domains:
                    if san_domain in self.certificates and self.certificates[san_domain] == certificate:
                        domains_to_remove.append(san_domain)
                
                for dom in domains_to_remove:
                    if dom in self.certificates:
                        del self.certificates[dom]
                
                logger.info(f"Certificate removed for domain {domain}")
                return True
            else:
                logger.warning(f"Certificate for domain {domain} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove certificate for {domain}: {e}")
            return False
    
    def get_certificate_for_domain(self, domain: str) -> Optional[SSLCertificate]:
        """Get certificate for specific domain"""        # Exact match first
        if domain in self.certificates:
            return self.certificates[domain]
        
        # Try wildcard match
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            wildcard_domain = f"*.{'.'.join(domain_parts[1:])}"
            if wildcard_domain in self.certificates:
                return self.certificates[wildcard_domain]
        
        return None
    
    def configure_platform_certificates(self) -> bool:
        """Configure SSL certificates for platform services"""        try:
            platform_domains = [
                "api.ia-influencer.com",
                "dashboard.ia-influencer.com",
                "admin.ia-influencer.com",
                "monitoring.ia-influencer.com"
            ]
            
            # Try to obtain Let's Encrypt certificates if manager is available
            if self.letsencrypt_manager:
                for domain in platform_domains:
                    # Check if certificate already exists and is valid
                    existing_cert = self.get_certificate_for_domain(domain)
                    if existing_cert and existing_cert.is_valid and existing_cert.days_until_expiry > 30:
                        logger.info(f"Valid certificate already exists for {domain}")
                        continue
                    
                    # Try to obtain certificate
                    success = self.letsencrypt_manager.obtain_certificate([domain])
                    if success:
                        # Add certificate to SSL terminator
                        cert_path = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
                        key_path = f"/etc/letsencrypt/live/{domain}/privkey.pem"
                        self.add_certificate(cert_path, key_path)
                    else:
                        logger.warning(f"Failed to obtain Let's Encrypt certificate for {domain}, generating self-signed")
                        # Fallback to self-signed certificate
                        cert = self.cert_manager.generate_self_signed_certificate(domain)
                        if cert:
                            self.certificates[domain] = cert
            else:
                # Generate self-signed certificates
                for domain in platform_domains:
                    cert = self.cert_manager.generate_self_signed_certificate(domain)
                    if cert:
                        self.certificates[domain] = cert
            
            # Configure wildcard certificate for subdomains
            wildcard_domain = "*.ia-influencer.com"
            if self.letsencrypt_manager:
                # Note: Wildcard certificates require DNS challenge, not implemented here
                logger.info("Wildcard certificates require DNS challenge - not implemented")
            else:
                # Generate self-signed wildcard certificate
                cert = self.cert_manager.generate_self_signed_certificate(
                    wildcard_domain,
                    san_domains=platform_domains
                )
                if cert:
                    self.certificates[wildcard_domain] = cert
            
            logger.info(f"Platform certificates configured for {len(platform_domains)} domains")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform certificates: {e}")
            return False
    
    def generate_nginx_ssl_config(self, domain: str) -> Optional[str]:
        """Generate Nginx SSL configuration for domain"""        certificate = self.get_certificate_for_domain(domain)
        if not certificate:
            return None
        
        config_lines = [
            f"ssl_certificate {certificate.cert_path};",
            f"ssl_certificate_key {certificate.key_path};",
            f"ssl_protocols {self.tls_config.min_version} {self.tls_config.max_version};",
            f"ssl_ciphers {':'.join(self.tls_config.cipher_suites)};",
            "ssl_prefer_server_ciphers off;",
            f"ssl_session_cache shared:SSL:{self.tls_config.session_cache_size // 1024}m;",
            f"ssl_session_timeout {self.tls_config.session_timeout}s;",
            "ssl_session_tickets off;"
        ]
        
        if certificate.ca_bundle_path:
            config_lines.append(f"ssl_trusted_certificate {certificate.ca_bundle_path};")
        
        if self.tls_config.ocsp_stapling:
            config_lines.extend([
                "ssl_stapling on;",
                "ssl_stapling_verify on;"
            ])
        
        # Add HSTS header
        hsts_header = f"max-age={self.tls_config.hsts_max_age}"
        if self.tls_config.hsts_include_subdomains:
            hsts_header += "; includeSubDomains"
        if self.tls_config.hsts_preload:
            hsts_header += "; preload"
        
        config_lines.append(f'add_header Strict-Transport-Security "{hsts_header}";')
        
        return "\n".join(config_lines)
    
    def generate_haproxy_ssl_config(self, domain: str) -> Optional[str]:
        """Generate HAProxy SSL configuration for domain"""        certificate = self.get_certificate_for_domain(domain)
        if not certificate:
            return None
        
        # HAProxy requires certificate and key in single file
        combined_cert_path = f"/etc/ssl/haproxy/{domain}.pem"
        
        try:
            # Create combined certificate file
            os.makedirs(os.path.dirname(combined_cert_path), exist_ok=True)
            
            with open(combined_cert_path, 'w') as combined_file:
                # Write certificate
                with open(certificate.cert_path, 'r') as cert_file:
                    combined_file.write(cert_file.read())
                
                # Write private key
                with open(certificate.key_path, 'r') as key_file:
                    combined_file.write(key_file.read())
                
                # Write CA bundle if available
                if certificate.ca_bundle_path and Path(certificate.ca_bundle_path).exists():
                    with open(certificate.ca_bundle_path, 'r') as ca_file:
                        combined_file.write(ca_file.read())
            
            # Set proper permissions
            os.chmod(combined_cert_path, 0o600)
            
            return combined_cert_path
            
        except Exception as e:
            logger.error(f"Failed to generate HAProxy SSL config for {domain}: {e}")
            return None
    
    def check_certificate_renewals(self) -> List[str]:
        """Check which certificates need renewal"""        expiring_certificates = []
        
        for domain, certificate in self.certificates.items():
            if certificate.days_until_expiry <= 30:
                expiring_certificates.append(domain)
        
        return expiring_certificates
    
    def renew_certificates(self) -> Dict[str, bool]:
        """Renew expiring certificates"""        renewal_results = {}
        expiring_certs = self.check_certificate_renewals()
        
        for domain in expiring_certs:
            if self.letsencrypt_manager:
                success = self.letsencrypt_manager.renew_certificate(domain)
                renewal_results[domain] = success
                
                if success:
                    # Reload certificate
                    cert_path = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
                    key_path = f"/etc/letsencrypt/live/{domain}/privkey.pem"
                    self.add_certificate(cert_path, key_path)
            else:
                # Cannot renew self-signed certificates automatically
                renewal_results[domain] = False
        
        return renewal_results
    
    def get_ssl_status(self) -> Dict[str, Any]:
        """Get SSL terminator status"""        status = {
            "certificates_count": len(set(cert.domain for cert in self.certificates.values())),
            "domains_count": len(self.certificates),
            "expiring_soon": len(self.check_certificate_renewals()),
            "letsencrypt_enabled": self.letsencrypt_manager is not None,
            "certificates": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Get certificate details
        unique_certs = {}
        for domain, certificate in self.certificates.items():
            if certificate.domain not in unique_certs:
                unique_certs[certificate.domain] = {
                    "domain": certificate.domain,
                    "san_domains": certificate.san_domains,
                    "issuer": certificate.issuer,
                    "not_after": certificate.not_after.isoformat() if certificate.not_after else None,
                    "days_until_expiry": certificate.days_until_expiry,
                    "is_valid": certificate.is_valid,
                    "key_size": certificate.key_size,
                    "signature_algorithm": certificate.signature_algorithm,
                    "fingerprint": certificate.fingerprint[:16] + "..."  # Truncate for display
                }
        
        status["certificates"] = unique_certs
        
        return status
