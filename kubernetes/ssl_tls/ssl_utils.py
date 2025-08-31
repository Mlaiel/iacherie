"""
IA Influencer Agent - SSL/TLS Utilities and Validation
Advanced SSL/TLS utilities, validation, and security analysis

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
import socket
import logging
import hashlib
import tempfile
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import OpenSSL
from OpenSSL import crypto


class SSLGrade(Enum):
    """SSL security grade enumeration"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
    T = "T"  # Trust issues
    M = "M"  # Certificate name mismatch


class VulnerabilityType(Enum):
    """SSL vulnerability types"""
    HEARTBLEED = "heartbleed"
    CCS_INJECTION = "ccs_injection"
    POODLE = "poodle"
    BEAST = "beast"
    CRIME = "crime"
    BREACH = "breach"
    FREAK = "freak"
    LOGJAM = "logjam"
    DROWN = "drown"
    SWEET32 = "sweet32"
    ROBOT = "robot"
    TLS_FALLBACK_SCSV = "tls_fallback_scsv"


@dataclass
class SSLScanResult:
    """SSL scan result structure"""
    hostname: str
    port: int
    scan_time: datetime
    
    # Certificate information
    certificate_valid: bool
    certificate_issues: List[str]
    certificate_grade: SSLGrade
    certificate_info: Dict[str, Any]
    
    # Protocol support
    supported_protocols: List[str]
    deprecated_protocols: List[str]
    
    # Cipher suites
    supported_ciphers: List[Dict[str, Any]]
    weak_ciphers: List[str]
    cipher_grade: SSLGrade
    
    # Security features
    hsts_enabled: bool
    hsts_details: Dict[str, Any]
    ocsp_stapling: bool
    compression_enabled: bool
    secure_renegotiation: bool
    
    # Vulnerabilities
    vulnerabilities: List[Dict[str, Any]]
    vulnerability_grade: SSLGrade
    
    # Overall assessment
    overall_grade: SSLGrade
    recommendations: List[str]
    
    # Performance metrics
    handshake_time: float
    connection_time: float


@dataclass
class CertificateValidationResult:
    """Certificate validation result"""
    valid: bool
    issues: List[str]
    warnings: List[str]
    certificate_info: Dict[str, Any]
    chain_valid: bool
    hostname_match: bool
    expiry_status: str
    days_until_expiry: int


class SSLValidationError(Exception):
    """SSL validation exception"""
    pass


class SSLValidator:
    """
    Advanced SSL/TLS certificate and configuration validator
    Provides comprehensive security analysis and recommendations
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize SSL validator
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Security thresholds
        self.min_key_size = 2048
        self.warn_expiry_days = 30
        self.critical_expiry_days = 7
        
        self.logger.info("SSL validator initialized")
    
    def validate_certificate_file(self, cert_path: Path) -> CertificateValidationResult:
        """
        Validate certificate from file
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Validation result
        """



        try:
            # Load certificate
            with open(cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
            
            # Try PEM format first
            try:
                certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
            except ValueError:
                # Try DER format
                certificate = x509.load_der_x509_certificate(cert_data, default_backend())
            
            return self._validate_certificate(certificate)
            
        except Exception as e:
            self.logger.error(f"Failed to validate certificate file {cert_path}: {e}")
            return CertificateValidationResult(
                valid=False,
                issues=[f"Failed to load certificate: {e}"],
                warnings=[],
                certificate_info={},
                chain_valid=False,
                hostname_match=False,
                expiry_status="unknown",
                days_until_expiry=0
            )
    
    def validate_certificate_chain(
        self, 
        cert_path: Path, 
        chain_path: Optional[Path] = None,
        ca_path: Optional[Path] = None
    ) -> CertificateValidationResult:
        """
        Validate certificate chain
        
        Args:
            cert_path: Path to certificate file
            chain_path: Path to intermediate certificates
            ca_path: Path to CA certificates
            
        Returns:
            Validation result
        """



        try:
            # Load certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Load intermediate certificates
            intermediate_certs = []
            if chain_path and chain_path.exists():
                with open(chain_path, 'rb') as f:
                    chain_data = f.read()
                
                # Split multiple certificates
                chain_pems = chain_data.split(b'-----END CERTIFICATE-----')
                for chain_pem in chain_pems:
                    if b'-----BEGIN CERTIFICATE-----' in chain_pem:
                        chain_cert_data = chain_pem + b'-----END CERTIFICATE-----'
                        try:
                            intermediate_cert = x509.load_pem_x509_certificate(
                                chain_cert_data, default_backend()
                            )
                            intermediate_certs.append(intermediate_cert)
                        except Exception:
                            continue
            
            # Validate certificate
            result = self._validate_certificate(certificate)
            
            # Validate chain using OpenSSL
            if intermediate_certs or ca_path:
                chain_valid = self._verify_certificate_chain_openssl(
                    certificate, intermediate_certs, ca_path
                )
                result.chain_valid = chain_valid
                
                if not chain_valid:
                    result.issues.append("Certificate chain validation failed")
                    result.valid = False
            
            return result
            
        except Exception as e:
            self.logger.error(f"Certificate chain validation failed: {e}")
            return CertificateValidationResult(
                valid=False,
                issues=[f"Chain validation failed: {e}"],
                warnings=[],
                certificate_info={},
                chain_valid=False,
                hostname_match=False,
                expiry_status="unknown",
                days_until_expiry=0
            )
    
    def _validate_certificate(self, certificate: x509.Certificate) -> CertificateValidationResult:
        """Internal certificate validation"""
        issues = []
        warnings = []
        
        # Extract certificate information
        cert_info = self._extract_certificate_info(certificate)
        
        # Check expiry
        now = datetime.utcnow()
        not_after = certificate.not_valid_after
        not_before = certificate.not_valid_before
        
        if now < not_before:
            issues.append("Certificate is not yet valid")
        
        days_until_expiry = (not_after - now).days
        
        if days_until_expiry < 0:
            expiry_status = "expired"
            issues.append("Certificate has expired")
        elif days_until_expiry <= self.critical_expiry_days:
            expiry_status = "critical"
            issues.append(f"Certificate expires in {days_until_expiry} days")
        elif days_until_expiry <= self.warn_expiry_days:
            expiry_status = "warning"
            warnings.append(f"Certificate expires in {days_until_expiry} days")
        else:
            expiry_status = "valid"
        
        # Check key size
        public_key = certificate.public_key()
        if hasattr(public_key, 'key_size'):
            key_size = public_key.key_size
            if key_size < self.min_key_size:
                issues.append(f"Key size ({key_size}) below minimum ({self.min_key_size})")
            cert_info['key_size'] = key_size
        
        # Check signature algorithm
        sig_alg = certificate.signature_algorithm_oid._name
        weak_algorithms = ['sha1', 'md5', 'md2']
        if any(weak_alg in sig_alg.lower() for weak_alg in weak_algorithms):
            issues.append(f"Weak signature algorithm: {sig_alg}")
        
        # Check basic constraints
        try:
            basic_constraints = certificate.extensions.get_extension_for_oid(
                x509.ExtensionOID.BASIC_CONSTRAINTS
            )
            if basic_constraints.value.ca:
                warnings.append("Certificate is marked as CA certificate")
        except x509.ExtensionNotFound:
            pass
        
        # Check key usage
        try:
            key_usage = certificate.extensions.get_extension_for_oid(
                x509.ExtensionOID.KEY_USAGE
            )
            if not key_usage.value.digital_signature:
                warnings.append("Digital signature not enabled")
            if not key_usage.value.key_encipherment:
                warnings.append("Key encipherment not enabled")
        except x509.ExtensionNotFound:
            warnings.append("Key usage extension not found")
        
        # Determine overall validity
        valid = len(issues) == 0
        
        return CertificateValidationResult(
            valid=valid,
            issues=issues,
            warnings=warnings,
            certificate_info=cert_info,
            chain_valid=True,  # Will be updated by chain validation
            hostname_match=True,  # Will be updated by hostname validation
            expiry_status=expiry_status,
            days_until_expiry=days_until_expiry
        )
    
    def _extract_certificate_info(self, certificate: x509.Certificate) -> Dict[str, Any]:
        """Extract detailed certificate information"""
        subject = certificate.subject
        issuer = certificate.issuer
        
        # Get common name
        common_name = None
        for attribute in subject:
            if attribute.oid == x509.NameOID.COMMON_NAME:
                common_name = attribute.value
                break
        
        # Get organization
        organization = None
        for attribute in subject:
            if attribute.oid == x509.NameOID.ORGANIZATION_NAME:
                organization = attribute.value
                break
        
        # Get Subject Alternative Names
        san_list = []
        try:
            san_extension = certificate.extensions.get_extension_for_oid(
                x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            for name in san_extension.value:
                if isinstance(name, x509.DNSName):
                    san_list.append(name.value)
                elif isinstance(name, x509.IPAddress):
                    san_list.append(str(name.value))
        except x509.ExtensionNotFound:
            pass
        
        # Calculate fingerprints
        cert_der = certificate.public_bytes(x509.Encoding.DER)
        sha1_fingerprint = hashlib.sha1(cert_der).hexdigest()
        sha256_fingerprint = hashlib.sha256(cert_der).hexdigest()
        
        return {
            'common_name': common_name,
            'organization': organization,
            'subject': subject.rfc4514_string(),
            'issuer': issuer.rfc4514_string(),
            'serial_number': str(certificate.serial_number),
            'not_before': certificate.not_valid_before.isoformat(),
            'not_after': certificate.not_valid_after.isoformat(),
            'subject_alt_names': san_list,
            'signature_algorithm': certificate.signature_algorithm_oid._name,
            'version': certificate.version.name,
            'sha1_fingerprint': sha1_fingerprint,
            'sha256_fingerprint': sha256_fingerprint
        }
    
    def _verify_certificate_chain_openssl(
        self,
        certificate: x509.Certificate,
        intermediate_certs: List[x509.Certificate],
        ca_path: Optional[Path]
    ) -> bool:
        """Verify certificate chain using OpenSSL"""



        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save certificate
                cert_file = temp_path / "cert.pem"
                cert_pem = certificate.public_bytes(x509.Encoding.PEM)
                cert_file.write_bytes(cert_pem)
                
                # Save intermediate certificates
                chain_file = None
                if intermediate_certs:
                    chain_file = temp_path / "chain.pem"
                    chain_data = b""
                    for cert in intermediate_certs:
                        chain_data += cert.public_bytes(x509.Encoding.PEM)
                    chain_file.write_bytes(chain_data)
                
                # Build OpenSSL verify command
                cmd = ["openssl", "verify"]
                
                if ca_path:
                    cmd.extend(["-CAfile", str(ca_path)])
                else:
                    cmd.append("-CApath")
                    cmd.append("/etc/ssl/certs")
                
                if chain_file:
                    cmd.extend(["-untrusted", str(chain_file)])
                
                cmd.append(str(cert_file))
                
                # Run verification
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                return result.returncode == 0
                
        except Exception as e:
            self.logger.warning(f"OpenSSL chain verification failed: {e}")
            return False


class SSLScanner:
    """
    Comprehensive SSL/TLS security scanner
    Performs deep security analysis and vulnerability assessment
    """
    
    def __init__(self, timeout: int = 10, threads: int = 5):
        """
        Initialize SSL scanner
        
        Args:
            timeout: Connection timeout in seconds
            threads: Number of concurrent scan threads
        """
        self.timeout = timeout
        self.threads = threads
        self.logger = logging.getLogger(__name__)
        
        # Protocol versions to test
        self.protocols_to_test = [
            ('SSLv2', ssl.PROTOCOL_SSLv23),
            ('SSLv3', ssl.PROTOCOL_SSLv23),
            ('TLSv1.0', ssl.PROTOCOL_TLSv1),
            ('TLSv1.1', ssl.PROTOCOL_TLSv1_1),
            ('TLSv1.2', ssl.PROTOCOL_TLSv1_2),
        ]
        
        # Add TLSv1.3 if available
        if hasattr(ssl, 'PROTOCOL_TLSv1_3'):
            self.protocols_to_test.append(('TLSv1.3', ssl.PROTOCOL_TLSv1_3))
        
        self.logger.info("SSL scanner initialized")
    
    def scan_host(self, hostname: str, port: int = 443) -> SSLScanResult:
        """
        Perform comprehensive SSL scan of host
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            Scan result
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting SSL scan of {hostname}:{port}")
            
            # Test connectivity
            connection_time = self._test_connectivity(hostname, port)
            
            # Scan certificate
            cert_result = self._scan_certificate(hostname, port)
            
            # Scan protocols
            protocol_result = self._scan_protocols(hostname, port)
            
            # Scan cipher suites
            cipher_result = self._scan_cipher_suites(hostname, port)
            
            # Check security features
            security_result = self._check_security_features(hostname, port)
            
            # Test vulnerabilities
            vuln_result = self._test_vulnerabilities(hostname, port)
            
            # Calculate grades
            cert_grade = self._calculate_certificate_grade(cert_result)
            cipher_grade = self._calculate_cipher_grade(cipher_result)
            vuln_grade = self._calculate_vulnerability_grade(vuln_result)
            overall_grade = self._calculate_overall_grade(cert_grade, cipher_grade, vuln_grade)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                cert_result, protocol_result, cipher_result, security_result, vuln_result
            )
            
            # Calculate handshake time
            handshake_time = self._measure_handshake_time(hostname, port)
            
            scan_result = SSLScanResult(
                hostname=hostname,
                port=port,
                scan_time=datetime.utcnow(),
                certificate_valid=cert_result.get('valid', False),
                certificate_issues=cert_result.get('issues', []),
                certificate_grade=cert_grade,
                certificate_info=cert_result.get('info', {}),
                supported_protocols=protocol_result.get('supported', []),
                deprecated_protocols=protocol_result.get('deprecated', []),
                supported_ciphers=cipher_result.get('supported', []),
                weak_ciphers=cipher_result.get('weak', []),
                cipher_grade=cipher_grade,
                hsts_enabled=security_result.get('hsts_enabled', False),
                hsts_details=security_result.get('hsts_details', {}),
                ocsp_stapling=security_result.get('ocsp_stapling', False),
                compression_enabled=security_result.get('compression_enabled', False),
                secure_renegotiation=security_result.get('secure_renegotiation', False),
                vulnerabilities=vuln_result,
                vulnerability_grade=vuln_grade,
                overall_grade=overall_grade,
                recommendations=recommendations,
                handshake_time=handshake_time,
                connection_time=connection_time
            )
            
            scan_duration = time.time() - start_time
            self.logger.info(f"SSL scan completed in {scan_duration:.2f}s - Grade: {overall_grade.value}")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"SSL scan failed for {hostname}:{port}: {e}")
            raise SSLValidationError(f"SSL scan failed: {e}")
    
    def _test_connectivity(self, hostname: str, port: int) -> float:
        """Test basic connectivity"""
        start_time = time.time()
        try:
            sock = socket.create_connection((hostname, port), timeout=self.timeout)
            sock.close()
            return time.time() - start_time
        except Exception as e:
            raise SSLValidationError(f"Connection failed: {e}")
    
    def _scan_certificate(self, hostname: str, port: int) -> Dict[str, Any]:
        """Scan SSL certificate"""



        try:
            context = ssl.create_default_context()
            
            with ssl.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    der_cert = ssock.getpeercert_raw()
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    
                    # Validate certificate
                    validator = SSLValidator(timeout=self.timeout)
                    validation_result = validator._validate_certificate(cert)
                    
                    return {
                        'valid': validation_result.valid,
                        'issues': validation_result.issues,
                        'warnings': validation_result.warnings,
                        'info': validation_result.certificate_info,
                        'days_until_expiry': validation_result.days_until_expiry
                    }
                    
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Certificate scan failed: {e}"],
                'warnings': [],
                'info': {},
                'days_until_expiry': 0
            }
    
    def _scan_protocols(self, hostname: str, port: int) -> Dict[str, List[str]]:
        """Scan supported SSL/TLS protocols"""
        supported = []
        deprecated = []
        
        def test_protocol(protocol_name: str, protocol_version: int) -> bool:
            try:
                context = ssl.SSLContext(protocol_version)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock) as ssock:
                        version = ssock.version()
                        return version is not None
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(test_protocol, name, version): name 
                for name, version in self.protocols_to_test
            }
            
            for future in as_completed(futures):
                protocol_name = futures[future]
                try:
                    if future.result():
                        supported.append(protocol_name)
                        if protocol_name in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']:
                            deprecated.append(protocol_name)
                except Exception:
                    pass
        
        return {
            'supported': supported,
            'deprecated': deprecated
        }
    
    def _scan_cipher_suites(self, hostname: str, port: int) -> Dict[str, Any]:
        """Scan supported cipher suites"""
        supported_ciphers = []
        weak_ciphers = []
        
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with ssl.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()
                    if cipher:
                        cipher_info = {
                            'name': cipher[0],
                            'protocol': cipher[1],
                            'bits': cipher[2]
                        }
                        supported_ciphers.append(cipher_info)
                        
                        # Check for weak ciphers
                        if self._is_weak_cipher(cipher[0]):
                            weak_ciphers.append(cipher[0])
                            
        except Exception as e:
            self.logger.warning(f"Cipher scan failed: {e}")
        
        return {
            'supported': supported_ciphers,
            'weak': weak_ciphers
        }
    
    def _is_weak_cipher(self, cipher_name: str) -> bool:
        """Check if cipher is considered weak"""
        weak_patterns = [
            'NULL', 'EXPORT', 'DES-CBC', 'RC4', 'RC2', 'MD5',
            'ADH', 'AECDH', 'aNULL', 'eNULL'
        ]
        
        return any(pattern in cipher_name.upper() for pattern in weak_patterns)
    
    def _check_security_features(self, hostname: str, port: int) -> Dict[str, Any]:
        """Check SSL security features"""
        security_features = {
            'hsts_enabled': False,
            'hsts_details': {},
            'ocsp_stapling': False,
            'compression_enabled': False,
            'secure_renegotiation': False
        }
        
        try:
            # Check HSTS via HTTP headers
            try:
                response = requests.get(
                    f"https://{hostname}:{port}/",
                    timeout=self.timeout,
                    verify=False,
                    allow_redirects=False
                )
                
                hsts_header = response.headers.get('Strict-Transport-Security')
                if hsts_header:
                    security_features['hsts_enabled'] = True
                    security_features['hsts_details'] = self._parse_hsts_header(hsts_header)
                    
            except Exception:
                pass
            
            # Check OCSP stapling and other features
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with ssl.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Check compression
                    if hasattr(ssock, 'compression'):
                        security_features['compression_enabled'] = ssock.compression() is not None
                    
                    # Note: OCSP stapling check would require more complex implementation
                    
        except Exception as e:
            self.logger.warning(f"Security features check failed: {e}")
        
        return security_features
    
    def _parse_hsts_header(self, hsts_header: str) -> Dict[str, Any]:
        """Parse HSTS header"""
        details = {
            'max_age': 0,
            'include_subdomains': False,
            'preload': False
        }
        
        parts = hsts_header.split(';')
        for part in parts:
            part = part.strip()
            if part.startswith('max-age='):
                try:
                    details['max_age'] = int(part.split('=')[1])
                except ValueError:
                    pass
            elif part == 'includeSubDomains':
                details['include_subdomains'] = True
            elif part == 'preload':
                details['preload'] = True
        
        return details
    
    def _test_vulnerabilities(self, hostname: str, port: int) -> List[Dict[str, Any]]:
        """Test for known SSL vulnerabilities"""
        vulnerabilities = []
        
        # Test for Heartbleed
        if self._test_heartbleed(hostname, port):
            vulnerabilities.append({
                'type': VulnerabilityType.HEARTBLEED.value,
                'severity': 'critical',
                'description': 'Server is vulnerable to Heartbleed (CVE-2014-0160)'
            })
        
        # Test for POODLE
        if self._test_poodle(hostname, port):
            vulnerabilities.append({
                'type': VulnerabilityType.POODLE.value,
                'severity': 'high',
                'description': 'Server is vulnerable to POODLE attack'
            })
        
        # Additional vulnerability tests can be added here
        
        return vulnerabilities
    
    def _test_heartbleed(self, hostname: str, port: int) -> bool:
        """Test for Heartbleed vulnerability"""
        # Simplified Heartbleed test
        # In production, use specialized libraries like testssl.sh
        try:
            protocols_to_test = [ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_2]
            
            for protocol in protocols_to_test:
                try:
                    context = ssl.SSLContext(protocol)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with context.wrap_socket(sock) as ssock:
                            # Simple check - if we can connect with old TLS versions
                            # and the server responds normally, it might be vulnerable
                            # This is a very basic check and should be enhanced
                            pass
                except:
                    continue
                    
        except Exception:
            pass
        
        return False  # Conservative default
    
    def _test_poodle(self, hostname: str, port: int) -> bool:
        """Test for POODLE vulnerability"""
        # Test if SSLv3 is supported (basic POODLE indicator)
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.set_ciphers('ALL:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
            context.options |= ssl.OP_NO_TLSv1_2
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_NO_TLSv1
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock) as ssock:
                    version = ssock.version()
                    return version == 'SSLv3'
                    
        except Exception:
            pass
        
        return False
    
    def _measure_handshake_time(self, hostname: str, port: int) -> float:
        """Measure SSL handshake time"""



        try:
            start_time = time.time()
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with ssl.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    handshake_time = time.time() - start_time
                    return handshake_time
                    
        except Exception:
            return 0.0
    
    def _calculate_certificate_grade(self, cert_result: Dict[str, Any]) -> SSLGrade:
        """Calculate certificate grade"""
        if not cert_result.get('valid', False):
            return SSLGrade.F
        
        issues = cert_result.get('issues', [])
        warnings = cert_result.get('warnings', [])
        days_until_expiry = cert_result.get('days_until_expiry', 0)
        
        if any('expired' in issue.lower() for issue in issues):
            return SSLGrade.F
        
        if days_until_expiry <= 7:
            return SSLGrade.C
        
        if days_until_expiry <= 30:
            return SSLGrade.B
        
        if warnings:
            return SSLGrade.A_MINUS
        
        return SSLGrade.A
    
    def _calculate_cipher_grade(self, cipher_result: Dict[str, Any]) -> SSLGrade:
        """Calculate cipher grade"""
        weak_ciphers = cipher_result.get('weak', [])
        supported_ciphers = cipher_result.get('supported', [])
        
        if not supported_ciphers:
            return SSLGrade.F
        
        if weak_ciphers:
            if len(weak_ciphers) >= len(supported_ciphers) / 2:
                return SSLGrade.F
            else:
                return SSLGrade.C
        
        # Check for modern cipher suites
        has_modern_ciphers = any(
            'ECDHE' in cipher.get('name', '') or 'DHE' in cipher.get('name', '')
            for cipher in supported_ciphers
        )
        
        if has_modern_ciphers:
            return SSLGrade.A
        else:
            return SSLGrade.B
    
    def _calculate_vulnerability_grade(self, vulnerabilities: List[Dict[str, Any]]) -> SSLGrade:
        """Calculate vulnerability grade"""
        if not vulnerabilities:
            return SSLGrade.A
        
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'critical']
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'high']
        
        if critical_vulns:
            return SSLGrade.F
        elif high_vulns:
            return SSLGrade.C
        else:
            return SSLGrade.B
    
    def _calculate_overall_grade(
        self, 
        cert_grade: SSLGrade, 
        cipher_grade: SSLGrade, 
        vuln_grade: SSLGrade
    ) -> SSLGrade:
        """Calculate overall SSL grade"""
        # Use worst grade as overall grade
        grades = [cert_grade, cipher_grade, vuln_grade]
        grade_values = {
            SSLGrade.A_PLUS: 6,
            SSLGrade.A: 5,
            SSLGrade.A_MINUS: 4,
            SSLGrade.B: 3,
            SSLGrade.C: 2,
            SSLGrade.D: 1,
            SSLGrade.F: 0
        }
        
        min_value = min(grade_values[grade] for grade in grades)
        
        for grade, value in grade_values.items():
            if value == min_value:
                return grade
        
        return SSLGrade.F
    
    def _generate_recommendations(
        self,
        cert_result: Dict[str, Any],
        protocol_result: Dict[str, List[str]],
        cipher_result: Dict[str, Any],
        security_result: Dict[str, Any],
        vuln_result: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Certificate recommendations
        if not cert_result.get('valid', False):
            recommendations.append("Fix certificate validation issues")
        
        days_until_expiry = cert_result.get('days_until_expiry', 0)
        if days_until_expiry <= 30:
            recommendations.append("Renew certificate before expiration")
        
        # Protocol recommendations
        deprecated_protocols = protocol_result.get('deprecated', [])
        if deprecated_protocols:
            recommendations.append(f"Disable deprecated protocols: {', '.join(deprecated_protocols)}")
        
        supported_protocols = protocol_result.get('supported', [])
        if 'TLSv1.3' not in supported_protocols:
            recommendations.append("Enable TLS 1.3 for better security and performance")
        
        # Cipher recommendations
        weak_ciphers = cipher_result.get('weak', [])
        if weak_ciphers:
            recommendations.append("Remove weak cipher suites from configuration")
        
        # Security feature recommendations
        if not security_result.get('hsts_enabled', False):
            recommendations.append("Enable HTTP Strict Transport Security (HSTS)")
        
        if not security_result.get('ocsp_stapling', False):
            recommendations.append("Enable OCSP stapling")
        
        if security_result.get('compression_enabled', False):
            recommendations.append("Disable SSL/TLS compression to prevent CRIME attacks")
        
        # Vulnerability recommendations
        for vuln in vuln_result:
            vuln_type = vuln.get('type', '')
            if vuln_type == VulnerabilityType.HEARTBLEED.value:
                recommendations.append("Update OpenSSL to fix Heartbleed vulnerability")
            elif vuln_type == VulnerabilityType.POODLE.value:
                recommendations.append("Disable SSLv3 to prevent POODLE attacks")
        
        return recommendations


class CertificateConverter:
    """
    SSL/TLS certificate format converter
    Supports conversion between PEM, DER, PKCS#12, and other formats
    """
    
    def __init__(self):
        """Initialize certificate converter"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Certificate converter initialized")
    
    def convert_format(
        self,
        input_path: Path,
        output_path: Path,
        input_format: str,
        output_format: str,
        password: Optional[str] = None
    ) -> bool:
        """
        Convert certificate format
        
        Args:
            input_path: Input file path
            output_path: Output file path
            input_format: Input format (PEM, DER, PKCS12)
            output_format: Output format (PEM, DER, PKCS12)
            password: Password for PKCS#12 files
            
        Returns:
            True if conversion successful
        """



        try:
            # Load certificate based on input format
            if input_format.upper() == "PEM":
                with open(input_path, 'rb') as f:
                    cert_data = f.read()
                certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
            elif input_format.upper() == "DER":
                with open(input_path, 'rb') as f:
                    cert_data = f.read()
                certificate = x509.load_der_x509_certificate(cert_data, default_backend())
            elif input_format.upper() == "PKCS12":
                # PKCS#12 conversion requires additional handling
                return self._convert_pkcs12(input_path, output_path, output_format, password)
            else:
                raise ValueError(f"Unsupported input format: {input_format}")
            
            # Convert to output format
            if output_format.upper() == "PEM":
                output_data = certificate.public_bytes(x509.Encoding.PEM)
            elif output_format.upper() == "DER":
                output_data = certificate.public_bytes(x509.Encoding.DER)
            elif output_format.upper() == "PKCS12":
                # PKCS#12 requires private key as well
                raise ValueError("PKCS#12 output requires private key")
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Write output
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            self.logger.info(f"Converted {input_format} to {output_format}: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Certificate conversion failed: {e}")
            return False
    
    def _convert_pkcs12(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        password: Optional[str] = None
    ) -> bool:
        """Convert PKCS#12 certificate"""



        try:
            # Use OpenSSL for PKCS#12 conversion
            cmd = ["openssl", "pkcs12", "-in", str(input_path)]
            
            if password:
                cmd.extend(["-passin", f"pass:{password}"])
            else:
                cmd.extend(["-passin", "pass:"])
            
            if output_format.upper() == "PEM":
                cmd.extend(["-out", str(output_path), "-nodes"])
            elif output_format.upper() == "DER":
                cmd.extend(["-out", str(output_path), "-outform", "DER", "-nodes"])
            else:
                raise ValueError(f"Unsupported output format for PKCS#12: {output_format}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"PKCS#12 conversion successful: {output_path}")
                return True
            else:
                self.logger.error(f"PKCS#12 conversion failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"PKCS#12 conversion error: {e}")
            return False
    
    def extract_private_key(
        self,
        pkcs12_path: Path,
        key_output_path: Path,
        password: Optional[str] = None
    ) -> bool:
        """
        Extract private key from PKCS#12 file
        
        Args:
            pkcs12_path: PKCS#12 file path
            key_output_path: Private key output path
            password: PKCS#12 password
            
        Returns:
            True if extraction successful
        """



        try:
            cmd = [
                "openssl", "pkcs12", "-in", str(pkcs12_path),
                "-nocerts", "-out", str(key_output_path), "-nodes"
            ]
            
            if password:
                cmd.extend(["-passin", f"pass:{password}"])
            else:
                cmd.extend(["-passin", "pass:"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Set secure permissions for private key
                os.chmod(key_output_path, 0o600)
                self.logger.info(f"Private key extracted: {key_output_path}")
                return True
            else:
                self.logger.error(f"Private key extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Private key extraction error: {e}")
            return False


class SSLTestServer:
    """
    SSL test server for certificate validation and testing
    """
    
    def __init__(self, cert_path: Path, key_path: Path, port: int = 8443):
        """
        Initialize SSL test server
        
        Args:
            cert_path: SSL certificate path
            key_path: Private key path
            port: Server port
        """
        self.cert_path = cert_path
        self.key_path = key_path
        self.port = port
        self.server = None
        self.server_thread = None
        self.logger = logging.getLogger(__name__)
    
    def start_server(self) -> bool:
        """
        Start SSL test server
        
        Returns:
            True if server started successfully
        """



        try:
            import http.server
            import socketserver
            
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(self.cert_path, self.key_path)
            
            # Create HTTP handler
            handler = http.server.SimpleHTTPRequestHandler
            
            # Create server
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                
                self.logger.info(f"SSL test server started on port {self.port}")
                
                # Start server in thread
                def run_server():
                    httpd.serve_forever()
                
                self.server = httpd
                self.server_thread = threading.Thread(target=run_server, daemon=True)
                self.server_thread.start()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start SSL test server: {e}")
            return False
    
    def stop_server(self) -> None:
        """Stop SSL test server"""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.logger.info("SSL test server stopped")


class OpenSSLWrapper:
    """
    Wrapper for OpenSSL command-line operations
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize OpenSSL wrapper
        
        Args:
            timeout: Command timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def generate_private_key(
        self,
        output_path: Path,
        key_size: int = 2048,
        algorithm: str = "RSA"
    ) -> bool:
        """
        Generate private key using OpenSSL
        
        Args:
            output_path: Output key file path
            key_size: Key size in bits
            algorithm: Key algorithm (RSA, EC)
            
        Returns:
            True if generation successful
        """



        try:
            if algorithm.upper() == "RSA":
                cmd = ["openssl", "genrsa", "-out", str(output_path), str(key_size)]
            elif algorithm.upper() == "EC":
                cmd = ["openssl", "ecparam", "-genkey", "-name", "secp256r1", "-out", str(output_path)]
            else:
                raise ValueError(f"Unsupported key algorithm: {algorithm}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                os.chmod(output_path, 0o600)
                self.logger.info(f"Private key generated: {output_path}")
                return True
            else:
                self.logger.error(f"Key generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"OpenSSL key generation error: {e}")
            return False
    
    def generate_csr(
        self,
        key_path: Path,
        csr_path: Path,
        subject: str,
        san_list: Optional[List[str]] = None
    ) -> bool:
        """
        Generate Certificate Signing Request
        
        Args:
            key_path: Private key path
            csr_path: Output CSR path
            subject: Certificate subject
            san_list: Subject Alternative Names
            
        Returns:
            True if generation successful
        """



        try:
            cmd = [
                "openssl", "req", "-new",
                "-key", str(key_path),
                "-out", str(csr_path),
                "-subj", subject
            ]
            
            # Add SAN extension if provided
            if san_list:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
                    f.write("[req]\n")
                    f.write("distinguished_name = req_distinguished_name\n")
                    f.write("req_extensions = v3_req\n")
                    f.write("[req_distinguished_name]\n")
                    f.write("[v3_req]\n")
                    f.write("subjectAltName = @alt_names\n")
                    f.write("[alt_names]\n")
                    
                    for i, san in enumerate(san_list, 1):
                        if san.startswith("IP:"):
                            f.write(f"IP.{i} = {san[3:]}\n")
                        else:
                            f.write(f"DNS.{i} = {san}\n")
                    
                    config_path = f.name
                
                cmd.extend(["-config", config_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Clean up config file
            if san_list:
                try:
                    os.unlink(config_path)
                except:
                    pass
            
            if result.returncode == 0:
                self.logger.info(f"CSR generated: {csr_path}")
                return True
            else:
                self.logger.error(f"CSR generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"OpenSSL CSR generation error: {e}")
            return False
    
    def verify_certificate(
        self,
        cert_path: Path,
        ca_path: Optional[Path] = None,
        chain_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Verify certificate using OpenSSL
        
        Args:
            cert_path: Certificate path
            ca_path: CA certificate path
            chain_path: Certificate chain path
            
        Returns:
            Tuple of (success, output)
        """



        try:
            cmd = ["openssl", "verify"]
            
            if ca_path:
                cmd.extend(["-CAfile", str(ca_path)])
            
            if chain_path:
                cmd.extend(["-untrusted", str(chain_path)])
            
            cmd.append(str(cert_path))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            return success, output
            
        except Exception as e:
            self.logger.error(f"OpenSSL verification error: {e}")
            return False, str(e)


# Factory functions
def create_ssl_scanner(timeout: int = 10, threads: int = 5) -> SSLScanner:
    """
    Factory function to create SSL scanner
    
    Args:
        timeout: Connection timeout
        threads: Number of scan threads
        
    Returns:
        Configured SSL scanner
    """



    return SSLScanner(timeout=timeout, threads=threads)


def validate_ssl_configuration(
    cert_path: Path,
    key_path: Path,
    ca_path: Optional[Path] = None,
    chain_path: Optional[Path] = None
) -> CertificateValidationResult:
    """
    Validate complete SSL configuration
    
    Args:
        cert_path: Certificate file path
        key_path: Private key file path
        ca_path: CA certificate path
        chain_path: Certificate chain path
        
    Returns:
        Validation result
    """
    validator = SSLValidator()
    
    # Validate certificate
    result = validator.validate_certificate_file(cert_path)
    
    # Validate chain if provided
    if chain_path or ca_path:
        chain_result = validator.validate_certificate_chain(cert_path, chain_path, ca_path)
        result.chain_valid = chain_result.chain_valid
        if not chain_result.chain_valid:
            result.issues.extend(chain_result.issues)
            result.valid = False
    
    # Verify key matches certificate
    try:
        # Load certificate
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
        
        # Load private key
        with open(key_path, 'rb') as f:
            key_data = f.read()
        
        try:
            private_key = serialization.load_pem_private_key(
                key_data, password=None, backend=default_backend()
            )
        except TypeError:
            # Try with password prompt
            import getpass
            password = getpass.getpass("Enter private key password: ").encode()
            private_key = serialization.load_pem_private_key(
                key_data, password=password, backend=default_backend()
            )
        
        # Verify key matches certificate
        cert_public_key = certificate.public_key()
        key_public_key = private_key.public_key()
        
        # Compare public key numbers
        cert_numbers = cert_public_key.public_numbers()
        key_numbers = key_public_key.public_numbers()
        
        if cert_numbers != key_numbers:
            result.issues.append("Private key does not match certificate")
            result.valid = False
        
    except Exception as e:
        result.issues.append(f"Key validation failed: {e}")
        result.valid = False
    
    return result
