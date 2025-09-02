"""IA Influencer Agent - Let's Encrypt Certificate Manager
Automated SSL certificate provisioning with ACME protocol

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
import json
import time
import logging
import hashlib
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import requests
import dns.resolver
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

try:
    import acme
    from acme import client, messages, challenges, crypto_util
    from acme.client import ClientV2
    import josepy as jose
except ImportError:
    acme = None
    print("Warning: ACME library not installed. Install with: pip install acme")


class ChallengeType(Enum):
    """ACME challenge types"""

    HTTP_01 = "http-01"
    DNS_01 = "dns-01"
    TLS_ALPN_01 = "tls-alpn-01"


class CertificateError(Exception):
    """Certificate provisioning exception"""
    pass


@dataclass
class LetsEncryptConfig:
    """
Let's Encrypt configuration"""
    email: str
    staging: bool = True
    key_size: int = 2048
    challenge_type: ChallengeType = ChallengeType.HTTP_01
    webroot_path: str = "/var/www/html"
    dns_provider: Optional[str] = None
    dns_credentials: Optional[Dict[str, str]] = None
    renewal_days: int = 30
    max_attempts: int = 3
    attempt_delay: int = 5


@dataclass
class CertificateRequest:
    """Certificate request information"""
    domains: List[str]
    email: str
    challenge_type: ChallengeType
    webroot_path: Optional[str] = None
    key_size: int = 2048


class LetsEncryptManager:
    """
    Let's Encrypt certificate management with ACME v2 protocol
    Supports HTTP-01, DNS-01, and TLS-ALPN-01 challenges
    """
    
    def __init__(self, config: LetsEncryptConfig):
        """
        Initialize Let's Encrypt manager
        
        Args:
            config: Let's Encrypt configuration
        """
        if acme is None:
            raise ImportError("ACME library is required. Install with: pip install acme")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ACME directory URLs
        if config.staging:
            self.directory_url = "https://acme-staging-v02.api.letsencrypt.org/directory"
        else:
            self.directory_url = "https://acme-v02.api.letsencrypt.org/directory"
        
        # Account key and client
        self.account_key = None
        self.acme_client = None
        
        # Storage paths
        self.account_path = Path("/etc/letsencrypt/accounts")
        self.cert_path = Path("/etc/letsencrypt/live")
        self.work_path = Path("/etc/letsencrypt/work")
        
        # Initialize directories
        self._init_directories()
        
        # Initialize ACME client
        self._init_acme_client()
        
        self.logger.info("Let's Encrypt manager initialized")
    
    def _init_directories(self) -> None:
        """Initialize Let's Encrypt directories"""
        try:
            for directory in [self.account_path, self.cert_path, self.work_path]:
                directory.mkdir(parents=True, exist_ok=True)
                os.chmod(directory, 0o755)
            
            # Webroot directory for HTTP-01 challenges
            if self.config.challenge_type == ChallengeType.HTTP_01:
                webroot = Path(self.config.webroot_path)
                webroot.mkdir(parents=True, exist_ok=True)
                
                # Create .well-known/acme-challenge directory
                acme_challenge_dir = webroot / ".well-known" / "acme-challenge"
                acme_challenge_dir.mkdir(parents=True, exist_ok=True)
                os.chmod(acme_challenge_dir, 0o755)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize directories: {e}")
            raise
    
    def _init_acme_client(self) -> None:
        """Initialize ACME client with account key"""
        try:
            # Load or generate account key
            account_key_path = self.account_path / "account.key"
            
            if account_key_path.exists():
                self.account_key = self._load_account_key(account_key_path)
                self.logger.info("Loaded existing account key")
            else:
                self.account_key = self._generate_account_key()
                self._save_account_key(account_key_path, self.account_key)
                self.logger.info("Generated new account key")
            
            # Create ACME client
            net = client.ClientNetwork(self.account_key, user_agent="IA-Influencer-Agent/1.0")
            directory = client.ClientV2.get_directory(self.directory_url, net)
            self.acme_client = client.ClientV2(directory, net=net)
            
            # Register account if needed
            self._register_account()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ACME client: {e}")
            raise
    
    def _generate_account_key(self) -> jose.JWKRSA:
        """Generate new account key"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.key_size,
            backend=default_backend()
        )
        return jose.JWKRSA(key=private_key)
    
    def _load_account_key(self, key_path: Path) -> jose.JWKRSA:
        try:
            logger.info(f"Executing _load_account_key")
            
            # Implementation for _load_account_key
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_load_account_key completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_load_account_key failed: {e}")
            raise
    def _save_account_key(self, key_path: Path, account_key: jose.JWKRSA) -> None:
        """
Save account key to file"""
        key_data = account_key.key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(key_path, 'wb') as key_file:
            key_file.write(key_data)
        
        os.chmod(key_path, 0o600)
    
    def _register_account(self) -> None:
        """
Register account with Let's Encrypt"""
        try:
            # Check if account already exists
            account_file = self.account_path / "account.json"
            
            if account_file.exists():
                with open(account_file, 'r') as f:
                    account_data = json.load(f)
                    # Existing account found
                    self.logger.info("Using existing Let's Encrypt account")
                    return
            
            # Create new account registration
            new_account = messages.NewRegistration.from_data(
                email=self.config.email,
                terms_of_service_agreed=True
            )
            
            account = self.acme_client.new_account(new_account)
            
            # Save account information
            account_data = {
                'email': self.config.email,
                'uri': account.uri,
                'created': datetime.utcnow().isoformat()
            }
            
            with open(account_file, 'w') as f:
                json.dump(account_data, f, indent=2)
            
            self.logger.info(f"Registered new account for {self.config.email}")
            
        except Exception as e:
            self.logger.error(f"Account registration failed: {e}")
            raise
    
    def request_certificate(self, cert_request: CertificateRequest) -> Tuple[str, str, str]:
        """
        Request SSL certificate from Let's Encrypt
        
        Args:
            cert_request: Certificate request details
            
        Returns:
            Tuple of (certificate_pem, private_key_pem, chain_pem)
        """
        try:
            self.logger.info(f"Requesting certificate for domains: {cert_request.domains}")
            
            # Generate private key for certificate
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=cert_request.key_size,
                backend=default_backend()
            )
            
            # Create CSR
            csr_pem = crypto_util.make_csr(
                private_key,
                cert_request.domains
            )
            
            # Request certificate
            order = self.acme_client.new_order(csr_pem)
            
            # Process authorizations
            for authorization in order.authorizations:
                domain = authorization.body.identifier.value
                self.logger.info(f"Processing authorization for {domain}")
                
                # Complete challenge
                self._complete_challenge(authorization, cert_request)
            
            # Finalize order
            finalized_order = self.acme_client.finalize_order(order, csr_pem)
            
            # Get certificate
            certificate_response = self.acme_client.fullchain_pem(finalized_order)
            
            # Split fullchain into certificate and chain
            certs = certificate_response.split('\n\n')
            certificate_pem = certs[0] + '\n'
            chain_pem = '\n\n'.join(certs[1:]) if len(certs) > 1 else ''
            
            # Convert private key to PEM
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            self.logger.info("Certificate issued successfully")
            
            # Save certificate files
            self._save_certificate_files(
                cert_request.domains[0],
                certificate_pem,
                private_key_pem,
                chain_pem
            )
            
            return certificate_pem, private_key_pem, chain_pem
            
        except Exception as e:
            self.logger.error(f"Certificate request failed: {e}")
            raise CertificateError(f"Failed to request certificate: {e}")
    
    def _complete_challenge(
        self, 
        authorization: messages.Authorization,
        cert_request: CertificateRequest
    ) -> None:
        """Complete ACME challenge for domain authorization"""
        domain = authorization.body.identifier.value
        
        # Find appropriate challenge
        challenge = None
        for ch in authorization.body.challenges:
            if ch.chall.typ == cert_request.challenge_type.value:
                challenge = ch
                break
        
        if not challenge:
            raise CertificateError(f"No {cert_request.challenge_type.value} challenge found")
        
        # Complete challenge based on type
        if cert_request.challenge_type == ChallengeType.HTTP_01:
            self._complete_http_challenge(challenge, domain)
        elif cert_request.challenge_type == ChallengeType.DNS_01:
            self._complete_dns_challenge(challenge, domain)
        else:
            raise CertificateError(f"Unsupported challenge type: {cert_request.challenge_type}")
        
        # Wait for challenge validation
        self._wait_for_challenge_validation(challenge)
    
    def _complete_http_challenge(self, challenge: messages.ChallengeBody, domain: str) -> None:
        """Complete HTTP-01 challenge"""
        try:
            # Get challenge response
            response, validation = challenge.chall.response_and_validation(self.account_key)
            
            # Create challenge file
            token = challenge.chall.token
            challenge_path = Path(self.config.webroot_path) / ".well-known" / "acme-challenge" / token
            
            with open(challenge_path, 'w') as f:
                f.write(validation)
            
            os.chmod(challenge_path, 0o644)
            
            self.logger.info(f"HTTP challenge file created for {domain}")
            
            # Verify challenge is accessible
            challenge_url = f"http://{domain}/.well-known/acme-challenge/{token}"
            
            try:
                resp = requests.get(challenge_url, timeout=10)
                if resp.text.strip() != validation:
                    raise CertificateError(f"Challenge validation failed for {domain}")
            except requests.RequestException as e:
                self.logger.warning(f"Could not verify challenge URL {challenge_url}: {e}")
            
            # Submit challenge response
            self.acme_client.answer_challenge(challenge, response)
            
        except Exception as e:
            self.logger.error(f"HTTP challenge failed for {domain}: {e}")
            raise
    
    def _complete_dns_challenge(self, challenge: messages.ChallengeBody, domain: str) -> None:
        """Complete DNS-01 challenge"""
        try:
            # Get challenge response
            response, validation = challenge.chall.response_and_validation(self.account_key)
            
            # Calculate DNS record value
            validation_hash = hashlib.sha256(validation.encode()).digest()
            dns_value = jose.b64encode(validation_hash).decode().rstrip('=')
            
            # DNS record name
            dns_name = f"_acme-challenge.{domain}"
            
            self.logger.info(f"DNS challenge for {domain}")
            self.logger.info(f"Create TXT record: {dns_name} = {dns_value}")
            
            # Create DNS record using provider API
            if self.config.dns_provider and self.config.dns_credentials:
                self._create_dns_record(dns_name, dns_value, domain)
            else:
                # Manual DNS setup
                input(f"Create DNS TXT record:\nName: {dns_name}\nValue: {dns_value}\nPress Enter when ready...")
            
            # Verify DNS record
            self._verify_dns_record(dns_name, dns_value)
            
            # Submit challenge response
            self.acme_client.answer_challenge(challenge, response)
            
        except Exception as e:
            self.logger.error(f"DNS challenge failed for {domain}: {e}")
            raise
    
    def _create_dns_record(self, name: str, value: str, domain: str) -> None:
        """Create DNS TXT record using provider API"""
        if self.config.dns_provider == "cloudflare":
            self._create_cloudflare_dns_record(name, value, domain)
        elif self.config.dns_provider == "route53":
            self._create_route53_dns_record(name, value, domain)
        else:
            raise CertificateError(f"Unsupported DNS provider: {self.config.dns_provider}")
    
    def _create_cloudflare_dns_record(self, name: str, value: str, domain: str) -> None:
        """Create DNS record using Cloudflare API"""
        try:
            api_token = self.config.dns_credentials.get('api_token')
            zone_id = self.config.dns_credentials.get('zone_id')
            
            if not api_token or not zone_id:
                raise CertificateError("Cloudflare API token and zone ID required")
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'type': 'TXT',
                'name': name,
                'content': value,
                'ttl': 60
            }
            
            response = requests.post(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Cloudflare DNS record created: {name}")
            else:
                raise CertificateError(f"Cloudflare API error: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Cloudflare DNS record creation failed: {e}")
            raise
    
    def _create_route53_dns_record(self, name: str, value: str, domain: str) -> None:
        """Create DNS record using AWS Route53"""
        try:
            import boto3
            
            aws_access_key = self.config.dns_credentials.get('aws_access_key_id')
            aws_secret_key = self.config.dns_credentials.get('aws_secret_access_key')
            hosted_zone_id = self.config.dns_credentials.get('hosted_zone_id')
            
            if not all([aws_access_key, aws_secret_key, hosted_zone_id]):
                raise CertificateError("AWS credentials and hosted zone ID required")
            
            route53 = boto3.client(
                'route53',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            change_batch = {
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': 'TXT',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': f'"{value}"'}]
                    }
                }]
            }
            
            response = route53.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch
            )
            
            self.logger.info(f"Route53 DNS record created: {name}")
            
        except Exception as e:
            self.logger.error(f"Route53 DNS record creation failed: {e}")
            raise
    
    def _verify_dns_record(self, name: str, value: str) -> None:
        """Verify DNS TXT record exists"""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                answers = dns.resolver.resolve(name, 'TXT')
                for answer in answers:
                    txt_value = answer.to_text().strip('"')
                    if txt_value == value:
                        self.logger.info(f"DNS record verified: {name}")
                        return
                
                attempt += 1
                if attempt < max_attempts:
                    self.logger.info(f"DNS record not found, retrying in 30 seconds... ({attempt}/{max_attempts})")
                    time.sleep(30)
                    
            except Exception as e:
                attempt += 1
                if attempt < max_attempts:
                    self.logger.warning(f"DNS lookup failed, retrying... ({attempt}/{max_attempts}): {e}")
                    time.sleep(30)
                else:
                    raise CertificateError(f"DNS record verification failed: {e}")
        
        raise CertificateError(f"DNS record {name} not found after {max_attempts} attempts")
    
    def _wait_for_challenge_validation(self, challenge: messages.ChallengeBody) -> None:
        """Wait for challenge to be validated by Let's Encrypt"""
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Poll challenge status
                challenge_response = self.acme_client.poll(challenge)
                
                if challenge_response.body.status == messages.STATUS_VALID:
                    self.logger.info("Challenge validation successful")
                    return
                elif challenge_response.body.status == messages.STATUS_INVALID:
                    error_detail = getattr(challenge_response.body, 'error', 'Unknown error')
                    raise CertificateError(f"Challenge validation failed: {error_detail}")
                elif challenge_response.body.status == messages.STATUS_PENDING:
                    attempt += 1
                    self.logger.info(f"Challenge pending, waiting... ({attempt}/{max_attempts})")
                    time.sleep(5)
                else:
                    attempt += 1
                    time.sleep(5)
                    
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise CertificateError(f"Challenge validation timeout: {e}")
                time.sleep(5)
        
        raise CertificateError("Challenge validation timeout")
    
    def _save_certificate_files(
        self,
        domain: str,
        certificate_pem: str,
        private_key_pem: str,
        chain_pem: str
    ) -> None:
        """Save certificate files to disk"""
        try:
            # Create domain directory
            domain_path = self.cert_path / domain
            domain_path.mkdir(parents=True, exist_ok=True)
            
            # Save certificate files
            files = {
                'cert.pem': certificate_pem,
                'privkey.pem': private_key_pem,
                'chain.pem': chain_pem,
                'fullchain.pem': certificate_pem + chain_pem
            }
            
            for filename, content in files.items():
                file_path = domain_path / filename
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Set appropriate permissions
                if 'privkey' in filename:
                    os.chmod(file_path, 0o600)
                else:
                    os.chmod(file_path, 0o644)
            
            self.logger.info(f"Certificate files saved to {domain_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save certificate files: {e}")
            raise
    
    def renew_certificate(self, domain: str) -> bool:
        """
        Renew certificate for domain
        
        Args:
            domain: Domain to renew certificate for
            
        Returns:
            True if renewal successful
        """
        try:
            domain_path = self.cert_path / domain
            cert_file = domain_path / "cert.pem"
            
            if not cert_file.exists():
                self.logger.error(f"Certificate file not found: {cert_file}")
                return False
            
            # Load existing certificate
            with open(cert_file, 'rb') as f:
                cert_data = f.read()
            
            certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Check if renewal is needed
            now = datetime.utcnow()
            renewal_date = certificate.not_valid_after - timedelta(days=self.config.renewal_days)
            
            if now < renewal_date:
                self.logger.info(f"Certificate for {domain} does not need renewal yet")
                return True
            
            # Extract domains from certificate
            domains = [domain]
            try:
                san_extension = certificate.extensions.get_extension_for_oid(
                    x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                for name in san_extension.value:
                    if isinstance(name, x509.DNSName) and name.value not in domains:
                        domains.append(name.value)
            except x509.ExtensionNotFound:
                pass
            
            # Create renewal request
            cert_request = CertificateRequest(
                domains=domains,
                email=self.config.email,
                challenge_type=self.config.challenge_type,
                webroot_path=self.config.webroot_path,
                key_size=self.config.key_size
            )
            
            # Request new certificate
            self.request_certificate(cert_request)
            
            self.logger.info(f"Certificate renewed successfully for {domain}")
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate renewal failed for {domain}: {e}")
            return False
    
    def list_certificates(self) -> List[Dict[str, Any]]:
        """List all managed certificates"""
        certificates = []
        
        try:
            for domain_path in self.cert_path.iterdir():
                if domain_path.is_dir():
                    cert_file = domain_path / "cert.pem"
                    if cert_file.exists():
                        try:
                            with open(cert_file, 'rb') as f:
                                cert_data = f.read()
                            
                            certificate = x509.load_pem_x509_certificate(
                                cert_data, default_backend()
                            )
                            
                            # Calculate days until expiry
                            now = datetime.utcnow()
                            days_until_expiry = (certificate.not_valid_after - now).days
                            
                            certificates.append({
                                'domain': domain_path.name,
                                'path': str(domain_path),
                                'expires': certificate.not_valid_after,
                                'days_until_expiry': days_until_expiry,
                                'needs_renewal': days_until_expiry <= self.config.renewal_days
                            })
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to read certificate {cert_file}: {e}")
            
            return certificates
            
        except Exception as e:
            self.logger.error(f"Failed to list certificates: {e}")
            return []
    
    def cleanup_challenge_files(self, domain: str) -> None:
        """Clean up challenge files after validation"""
        try:
            if self.config.challenge_type == ChallengeType.HTTP_01:
                challenge_dir = Path(self.config.webroot_path) / ".well-known" / "acme-challenge"
                if challenge_dir.exists():
                    for challenge_file in challenge_dir.glob("*"):
                        try:
                            challenge_file.unlink()
                        except Exception as e:
                            self.logger.warning(f"Failed to remove challenge file {challenge_file}: {e}")
            
            self.logger.info(f"Challenge cleanup completed for {domain}")
            
        except Exception as e:
            self.logger.warning(f"Challenge cleanup failed for {domain}: {e}")


def create_letsencrypt_manager(config: LetsEncryptConfig) -> LetsEncryptManager:
    """
    Factory function to create Let's Encrypt manager
    
    Args:
        config: Let's Encrypt configuration
        
    Returns:
        Configured Let's Encrypt manager
    """
    return LetsEncryptManager(config)
