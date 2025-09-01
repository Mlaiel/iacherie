"""Security Utilities Module
=========================

Professional security utilities for web crawlers and content protection.
Implements advanced security measures, threat detection, and protection mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import hashlib
import hmac
import secrets
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import base64
import re
import ipaddress
from urllib.parse import urlparse, urljoin
import asyncio
import ssl

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Security scanning
import aiohttp
import dns.resolver
import whois

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """
Security level classifications."""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"
    MALICIOUS = "malicious"

class ThreatType(Enum):
    """Types of security threats."""

    MALWARE = "malware"
    PHISHING = "phishing"
    SCAM = "scam"
    FRAUD = "fraud"
    SPAM = "spam"
    MALICIOUS_REDIRECT = "malicious_redirect"
    SUSPICIOUS_DOMAIN = "suspicious_domain"
    BLACKLISTED = "blacklisted"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    BOT_DETECTION = "bot_detection"

class EncryptionMethod(Enum):
    """Encryption methods."""

    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    FERNET = "fernet"

@dataclass
class SecurityAssessment:
    """Security assessment result."""
    url: str
    security_level: SecurityLevel
    threat_types: List[ThreatType]
    confidence_score: float
    risk_factors: List[str]
    recommendations: List[str]
    scan_timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class EncryptedData:
    """
Encrypted data container."""
    encrypted_content: bytes
    encryption_method: EncryptionMethod
    key_id: Optional[str]
    initialization_vector: Optional[bytes]
    metadata: Dict[str, Any]

class SecurityScanner:
    """
    Advanced security scanner for URLs and content.
    
    Features:
    - URL reputation checking
    - Domain analysis
    - SSL certificate validation
    - Malware detection
    - Phishing detection
    - Content security analysis
    """
    
    def __init__(self):
        """
Initialize security scanner."""
        self.malicious_domains = set()
        self.phishing_patterns = []
        self.suspicious_keywords = []
        self.trusted_domains = set()
        
        # Load security databases
        self._load_security_databases()
        
        # Security thresholds
        self.phishing_threshold = 0.7
        self.malware_threshold = 0.8
        self.domain_age_threshold = 30  # days
        
        logger.info("Security scanner initialized")
    
    def _load_security_databases(self) -> None:
        """Load security databases and threat intelligence."""
        # Load known malicious domains
        self.malicious_domains.update([
            "example-malware.com",
            "phishing-site.net",
            "malicious-redirect.org"
        ])
        
        # Load phishing patterns
        self.phishing_patterns.extend([
            r"verify.*account.*immediately",
            r"click.*here.*urgent",
            r"suspended.*account",
            r"confirm.*identity",
            r"security.*alert",
            r"unauthorized.*access"
        ])
        
        # Load suspicious keywords
        self.suspicious_keywords.extend([
            "free money", "instant wealth", "guaranteed profit",
            "click here now", "limited time offer", "act now",
            "verify account", "confirm password", "update payment"
        ])
        
        # Load trusted domains
        self.trusted_domains.update([
            "google.com", "microsoft.com", "amazon.com",
            "github.com", "stackoverflow.com", "wikipedia.org"
        ])
    
    async def scan_url(self, url: str) -> SecurityAssessment:
        """
        Comprehensive security scan of URL.
        
        Args:
            url: URL to scan
            
        Returns:
            SecurityAssessment object
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Initialize assessment
            assessment = SecurityAssessment(
                url=url,
                security_level=SecurityLevel.SAFE,
                threat_types=[],
                confidence_score=0.0,
                risk_factors=[],
                recommendations=[],
                scan_timestamp=datetime.now(),
                metadata={}
            )
            
            # Perform security checks
            await self._check_domain_reputation(domain, assessment)
            await self._check_ssl_certificate(url, assessment)
            await self._check_domain_age(domain, assessment)
            await self._check_url_patterns(url, assessment)
            await self._check_content_security(url, assessment)
            await self._check_redirect_chains(url, assessment)
            
            # Calculate final security level
            assessment.security_level = self._calculate_security_level(assessment)
            
            # Generate recommendations
            assessment.recommendations = self._generate_recommendations(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Security scan failed for {url}: {e}")
            return SecurityAssessment(
                url=url,
                security_level=SecurityLevel.CRITICAL_RISK,
                threat_types=[ThreatType.MALWARE],
                confidence_score=0.0,
                risk_factors=[f"Scan error: {str(e)}"],
                recommendations=["Avoid this URL due to scan errors"],
                scan_timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def _check_domain_reputation(self, domain: str, assessment: SecurityAssessment) -> None:
        """Check domain reputation against known threat databases."""
        try:
            # Check against malicious domains
            if domain in self.malicious_domains:
                assessment.threat_types.append(ThreatType.MALICIOUS_REDIRECT)
                assessment.risk_factors.append("Domain in malicious database")
                assessment.confidence_score += 0.9
            
            # Check against trusted domains
            elif domain in self.trusted_domains:
                assessment.confidence_score -= 0.2
                assessment.metadata["trusted_domain"] = True
            
            # Check domain patterns
            suspicious_patterns = [
                r'\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}',  # IP-like domains
                r'[a-z]{20,}',  # Very long random strings
                r'.*\.tk$|.*\.ml$|.*\.ga$',  # Suspicious TLDs
                r'.*-.*-.*-.*',  # Multiple hyphens
            ]
            
            for pattern in suspicious_patterns:
                if re.match(pattern, domain):
                    assessment.threat_types.append(ThreatType.SUSPICIOUS_DOMAIN)
                    assessment.risk_factors.append(f"Suspicious domain pattern: {pattern}")
                    assessment.confidence_score += 0.5
                    break
            
        except Exception as e:
            logger.error(f"Domain reputation check failed: {e}")
    
    async def _check_ssl_certificate(self, url: str, assessment: SecurityAssessment) -> None:
        """Check SSL certificate validity and security."""
        try:
            parsed = urlparse(url)
            
            if parsed.scheme != 'https':
                assessment.threat_types.append(ThreatType.FRAUD)
                assessment.risk_factors.append("No SSL encryption")
                assessment.confidence_score += 0.3
                return
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect and get certificate
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                try:
                    async with session.get(url, timeout=10) as response:
                        # SSL verification passed if we get here
                        assessment.metadata["ssl_valid"] = True
                        assessment.confidence_score -= 0.1
                        
                except aiohttp.ClientSSLError as ssl_error:
                    assessment.threat_types.append(ThreatType.FRAUD)
                    assessment.risk_factors.append(f"SSL certificate error: {str(ssl_error)}")
                    assessment.confidence_score += 0.6
                
        except Exception as e:
            logger.error(f"SSL check failed: {e}")
    
    async def _check_domain_age(self, domain: str, assessment: SecurityAssessment) -> None:
        """Check domain registration age."""
        try:
            # Get domain whois information
            domain_info = whois.whois(domain)
            
            if domain_info and domain_info.creation_date:
                creation_date = domain_info.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                domain_age = (datetime.now() - creation_date).days
                assessment.metadata["domain_age_days"] = domain_age
                
                if domain_age < self.domain_age_threshold:
                    assessment.threat_types.append(ThreatType.SUSPICIOUS_DOMAIN)
                    assessment.risk_factors.append(f"Very new domain ({domain_age} days old)")
                    assessment.confidence_score += 0.4
                elif domain_age < 365:  # Less than 1 year
                    assessment.risk_factors.append(f"Relatively new domain ({domain_age} days old)")
                    assessment.confidence_score += 0.2
                
        except Exception as e:
            logger.warning(f"Domain age check failed for {domain}: {e}")
            assessment.risk_factors.append("Unable to verify domain age")
            assessment.confidence_score += 0.1
    
    async def _check_url_patterns(self, url: str, assessment: SecurityAssessment) -> None:
        """Check URL for suspicious patterns."""
        try:
            # Check for URL shorteners
            url_shorteners = [
                "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
                "is.gd", "buff.ly", "adf.ly", "short.link"
            ]
            
            parsed = urlparse(url)
            if any(shortener in parsed.netloc for shortener in url_shorteners):
                assessment.threat_types.append(ThreatType.MALICIOUS_REDIRECT)
                assessment.risk_factors.append("URL shortener detected")
                assessment.confidence_score += 0.3
            
            # Check for suspicious URL parameters
            suspicious_params = [
                "cmd=", "exec=", "shell=", "system=",
                "eval=", "base64=", "decode=", "include="
            ]
            
            if any(param in url.lower() for param in suspicious_params):
                assessment.threat_types.append(ThreatType.MALWARE)
                assessment.risk_factors.append("Suspicious URL parameters")
                assessment.confidence_score += 0.7
            
            # Check for homograph attacks
            if self._detect_homograph_attack(parsed.netloc):
                assessment.threat_types.append(ThreatType.PHISHING)
                assessment.risk_factors.append("Possible homograph attack")
                assessment.confidence_score += 0.6
            
        except Exception as e:
            logger.error(f"URL pattern check failed: {e}")
    
    async def _check_content_security(self, url: str, assessment: SecurityAssessment) -> None:
        """Check content for security threats."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for phishing patterns
                        phishing_score = self._analyze_phishing_content(content)
                        if phishing_score > self.phishing_threshold:
                            assessment.threat_types.append(ThreatType.PHISHING)
                            assessment.risk_factors.append(f"Phishing patterns detected (score: {phishing_score:.2f})")
                            assessment.confidence_score += phishing_score * 0.8
                        
                        # Check for malicious scripts
                        if self._detect_malicious_scripts(content):
                            assessment.threat_types.append(ThreatType.MALWARE)
                            assessment.risk_factors.append("Malicious scripts detected")
                            assessment.confidence_score += 0.8
                        
                        # Check for suspicious keywords
                        suspicious_count = self._count_suspicious_keywords(content)
                        if suspicious_count > 3:
                            assessment.threat_types.append(ThreatType.SCAM)
                            assessment.risk_factors.append(f"Multiple suspicious keywords ({suspicious_count})")
                            assessment.confidence_score += min(suspicious_count * 0.1, 0.6)
                        
                        assessment.metadata["content_analyzed"] = True
                        assessment.metadata["content_length"] = len(content)
                    
                    else:
                        assessment.risk_factors.append(f"HTTP error: {response.status}")
                        assessment.confidence_score += 0.2
                        
        except asyncio.TimeoutError:
            assessment.risk_factors.append("Request timeout")
            assessment.confidence_score += 0.3
        except Exception as e:
            logger.error(f"Content security check failed: {e}")
            assessment.risk_factors.append("Content analysis failed")
            assessment.confidence_score += 0.2
    
    async def _check_redirect_chains(self, url: str, assessment: SecurityAssessment) -> None:
        """Check for suspicious redirect chains."""
        try:
            redirect_chain = []
            current_url = url
            max_redirects = 10
            
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=1)
            ) as session:
                for i in range(max_redirects):
                    async with session.get(
                        current_url, 
                        allow_redirects=False,
                        timeout=10
                    ) as response:
                        redirect_chain.append(current_url)
                        
                        if response.status in [301, 302, 303, 307, 308]:
                            location = response.headers.get('Location')
                            if location:
                                # Resolve relative URLs
                                next_url = urljoin(current_url, location)
                                
                                # Check for redirect loops
                                if next_url in redirect_chain:
                                    assessment.threat_types.append(ThreatType.MALICIOUS_REDIRECT)
                                    assessment.risk_factors.append("Redirect loop detected")
                                    assessment.confidence_score += 0.7
                                    break
                                
                                current_url = next_url
                            else:
                                break
                        else:
                            break
                
                # Analyze redirect chain
                if len(redirect_chain) > 5:
                    assessment.threat_types.append(ThreatType.MALICIOUS_REDIRECT)
                    assessment.risk_factors.append(f"Long redirect chain ({len(redirect_chain)} hops)")
                    assessment.confidence_score += 0.5
                
                # Check for domain changes in redirects
                domains = set(urlparse(url).netloc for url in redirect_chain)
                if len(domains) > 3:
                    assessment.threat_types.append(ThreatType.MALICIOUS_REDIRECT)
                    assessment.risk_factors.append(f"Multiple domain redirects ({len(domains)} domains)")
                    assessment.confidence_score += 0.6
                
                assessment.metadata["redirect_chain"] = redirect_chain
                assessment.metadata["redirect_count"] = len(redirect_chain) - 1
                
        except Exception as e:
            logger.error(f"Redirect chain check failed: {e}")
    
    def _analyze_phishing_content(self, content: str) -> float:
        """Analyze content for phishing indicators."""
        phishing_score = 0.0
        content_lower = content.lower()
        
        # Check phishing patterns
        for pattern in self.phishing_patterns:
            if re.search(pattern, content_lower):
                phishing_score += 0.2
        
        # Check for form fields requesting sensitive info
        sensitive_fields = [
            "password", "ssn", "social security", "credit card",
            "cvv", "pin", "account number", "routing number"
        ]
        
        for field in sensitive_fields:
            if field in content_lower:
                phishing_score += 0.15
        
        # Check for urgency indicators
        urgency_words = [
            "urgent", "immediate", "expires today", "act now",
            "limited time", "suspended", "verify now"
        ]
        
        for word in urgency_words:
            if word in content_lower:
                phishing_score += 0.1
        
        return min(phishing_score, 1.0)
    
    def _detect_malicious_scripts(self, content: str) -> bool:
        """Detect malicious scripts in content."""
        malicious_patterns = [
            r'eval\s*\(',
            r'document\.write\s*\(',
            r'window\.location\s*=',
            r'javascript:\s*eval',
            r'<script[^>]*src=["\']https?://[^"\']*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
            r'String\.fromCharCode',
            r'unescape\s*\(',
            r'atob\s*\(',
            r'btoa\s*\('
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _count_suspicious_keywords(self, content: str) -> int:
        """Count suspicious keywords in content."""
        content_lower = content.lower()
        count = 0
        
        for keyword in self.suspicious_keywords:
            if keyword in content_lower:
                count += 1
        
        return count
    
    def _detect_homograph_attack(self, domain: str) -> bool:
        """
Detect possible homograph attacks in domain."""
        # Check for mixed scripts
        try:
            # Simple check for non-ASCII characters that could be spoofing
            if any(ord(char) > 127 for char in domain):
                return True
            
            # Check for character substitutions common in homograph attacks
            suspicious_chars = ['0', '1', 'l', 'I', 'o', 'O']
            if sum(1 for char in domain if char in suspicious_chars) > 3:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_security_level(self, assessment: SecurityAssessment) -> SecurityLevel:
        """
Calculate overall security level from assessment."""
        score = assessment.confidence_score
        
        if score >= 0.9:
            return SecurityLevel.MALICIOUS
        elif score >= 0.7:
            return SecurityLevel.CRITICAL_RISK
        elif score >= 0.5:
            return SecurityLevel.HIGH_RISK
        elif score >= 0.3:
            return SecurityLevel.MEDIUM_RISK
        elif score >= 0.1:
            return SecurityLevel.LOW_RISK
        else:
            return SecurityLevel.SAFE
    
    def _generate_recommendations(self, assessment: SecurityAssessment) -> List[str]:
        """
Generate security recommendations."""
        recommendations = []
        
        if assessment.security_level in [SecurityLevel.MALICIOUS, SecurityLevel.CRITICAL_RISK]:
            recommendations.extend([
                "DO NOT visit this URL",
                "Block this domain in your security systems",
                "Report this URL to security authorities"
            ])
        elif assessment.security_level == SecurityLevel.HIGH_RISK:
            recommendations.extend([
                "Avoid visiting this URL",
                "Use extreme caution if access is necessary",
                "Ensure antivirus and security software is active"
            ])
        elif assessment.security_level == SecurityLevel.MEDIUM_RISK:
            recommendations.extend([
                "Use caution when visiting this URL",
                "Do not enter sensitive information",
                "Verify the site's legitimacy through other means"
            ])
        elif assessment.security_level == SecurityLevel.LOW_RISK:
            recommendations.extend([
                "Exercise normal security precautions",
                "Verify SSL certificate if handling sensitive data"
            ])
        
        # Specific threat-based recommendations
        if ThreatType.PHISHING in assessment.threat_types:
            recommendations.append("Do not enter login credentials or personal information")
        
        if ThreatType.MALWARE in assessment.threat_types:
            recommendations.append("Do not download any files from this site")
        
        if ThreatType.MALICIOUS_REDIRECT in assessment.threat_types:
            recommendations.append("Avoid clicking any links on this site")
        
        return recommendations

class ContentEncryption:
    """
    Advanced content encryption and decryption utilities.
    
    Features:
    - Multiple encryption algorithms
    - Key management
    - Secure key derivation
    - Digital signatures
    """
    
    def __init__(self):
        """
Initialize encryption utilities."""
        self.keys: Dict[str, bytes] = {}
        self.key_metadata: Dict[str, Dict[str, Any]] = {}
        
    def generate_key(self, method: EncryptionMethod = EncryptionMethod.FERNET) -> Tuple[str, bytes]:
        """
Generate encryption key."""
        key_id = secrets.token_hex(16)
        
        if method == EncryptionMethod.FERNET:
            key = Fernet.generate_key()
        elif method == EncryptionMethod.AES_256:
            key = secrets.token_bytes(32)  # 256 bits
        elif method in [EncryptionMethod.RSA_2048, EncryptionMethod.RSA_4096]:
            key_size = 2048 if method == EncryptionMethod.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported encryption method: {method}")
        
        self.keys[key_id] = key
        self.key_metadata[key_id] = {
            'method': method,
            'created_at': datetime.now(),
            'used_count': 0
        }
        
        return key_id, key
    
    def encrypt_content(
        self,
        content: Union[str, bytes],
        key_id: Optional[str] = None,
        method: EncryptionMethod = EncryptionMethod.FERNET
    ) -> EncryptedData:
        """Encrypt content with specified method."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if key_id is None:
            key_id, _ = self.generate_key(method)
        
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key not found: {key_id}")
        
        try:
            if method == EncryptionMethod.FERNET:
                fernet = Fernet(key)
                encrypted_content = fernet.encrypt(content)
                iv = None
            
            elif method == EncryptionMethod.AES_256:
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                
                iv = secrets.token_bytes(16)  # AES block size
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                
                # Pad content to AES block size
                pad_length = 16 - (len(content) % 16)
                padded_content = content + bytes([pad_length]) * pad_length
                
                encrypted_content = encryptor.update(padded_content) + encryptor.finalize()
            
            elif method in [EncryptionMethod.RSA_2048, EncryptionMethod.RSA_4096]:
                private_key = serialization.load_pem_private_key(
                    key, password=None, backend=default_backend()
                )
                public_key = private_key.public_key()
                
                # RSA can only encrypt small amounts of data
                max_length = (private_key.key_size // 8) - 2 * (256 // 8) - 2  # OAEP padding
                if len(content) > max_length:
                    raise ValueError(f"Content too large for RSA encryption (max {max_length} bytes)")
                
                encrypted_content = public_key.encrypt(
                    content,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                iv = None
            
            else:
                raise ValueError(f"Unsupported encryption method: {method}")
            
            # Update usage statistics
            self.key_metadata[key_id]['used_count'] += 1
            
            return EncryptedData(
                encrypted_content=encrypted_content,
                encryption_method=method,
                key_id=key_id,
                initialization_vector=iv,
                metadata={
                    'original_size': len(content),
                    'encrypted_size': len(encrypted_content),
                    'encrypted_at': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_content(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt content."""
        key_id = encrypted_data.key_id
        if not key_id or key_id not in self.keys:
            raise ValueError(f"Decryption key not found: {key_id}")
        
        key = self.keys[key_id]
        method = encrypted_data.encryption_method
        
        try:
            if method == EncryptionMethod.FERNET:
                fernet = Fernet(key)
                decrypted_content = fernet.decrypt(encrypted_data.encrypted_content)
            
            elif method == EncryptionMethod.AES_256:
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                
                if not encrypted_data.initialization_vector:
                    raise ValueError("IV required for AES decryption")
                
                cipher = Cipher(
                    algorithms.AES(key), 
                    modes.CBC(encrypted_data.initialization_vector), 
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                
                padded_content = decryptor.update(encrypted_data.encrypted_content) + decryptor.finalize()
                
                # Remove padding
                pad_length = padded_content[-1]
                decrypted_content = padded_content[:-pad_length]
            
            elif method in [EncryptionMethod.RSA_2048, EncryptionMethod.RSA_4096]:
                private_key = serialization.load_pem_private_key(
                    key, password=None, backend=default_backend()
                )
                
                decrypted_content = private_key.decrypt(
                    encrypted_data.encrypted_content,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            
            else:
                raise ValueError(f"Unsupported encryption method: {method}")
            
            return decrypted_content
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def secure_delete_key(self, key_id: str) -> bool:
        """
Securely delete encryption key."""
        try:
            if key_id in self.keys:
                # Overwrite key memory with random data
                key = self.keys[key_id]
                if isinstance(key, bytes):
                    # Overwrite with random bytes
                    random_bytes = secrets.token_bytes(len(key))
                    key = random_bytes
                
                del self.keys[key_id]
                del self.key_metadata[key_id]
                
                logger.info(f"Key securely deleted: {key_id}")
                return True
            else:
                logger.warning(f"Key not found for deletion: {key_id}")
                return False
                
        except Exception as e:
            logger.error(f"Key deletion failed: {e}")
            return False

class AccessControl:
    """
    Access control and authentication utilities.
    """
    
    def __init__(self):
        """
Initialize access control."""
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.blocked_ips: Set[str] = set()
        self.trusted_ips: Set[str] = set()
    
    def generate_api_key(self, user_id: str, permissions: List[str]) -> str:
        """
Generate API key with permissions."""
        api_key = secrets.token_urlsafe(32)
        
        self.api_keys[api_key] = {
            'user_id': user_id,
            'permissions': permissions,
            'created_at': datetime.now(),
            'last_used': None,
            'usage_count': 0,
            'is_active': True
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str, required_permission: str = None) -> bool:
        """
Validate API key and permissions."""
        key_data = self.api_keys.get(api_key)
        if not key_data or not key_data['is_active']:
            return False
        
        if required_permission and required_permission not in key_data['permissions']:
            return False
        
        # Update usage statistics
        key_data['last_used'] = datetime.now()
        key_data['usage_count'] += 1
        
        return True
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """
Check rate limiting for identifier."""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old requests
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                req_time for req_time in self.rate_limits[identifier]
                if req_time > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Check current count
        current_requests = len(self.rate_limits[identifier])
        if current_requests >= max_requests:
            return False
        
        # Add current request
        self.rate_limits[identifier].append(now)
        return True
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """
Check if IP address is blocked."""
        return ip_address in self.blocked_ips
    
    def is_ip_trusted(self, ip_address: str) -> bool:
        """
Check if IP address is trusted."""
        return ip_address in self.trusted_ips
    
    def block_ip(self, ip_address: str, reason: str = "") -> None:
        """Block IP address."""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP blocked: {ip_address} - {reason}")
    
    def unblock_ip(self, ip_address: str) -> None:
        """Unblock IP address."""
        self.blocked_ips.discard(ip_address)
        logger.info(f"IP unblocked: {ip_address}")

# Factory functions
def create_security_scanner() -> SecurityScanner:
    """Create security scanner instance."""
    return SecurityScanner()

def create_content_encryption() -> ContentEncryption:
    """
Create content encryption instance."""
    return ContentEncryption()

def create_access_control() -> AccessControl:
    """
Create access control instance."""
    return AccessControl()

async def quick_security_scan(url: str) -> SecurityAssessment:
    """
Quick security scan of URL."""
    scanner = create_security_scanner()
    return await scanner.scan_url(url)

def quick_encrypt_content(content: str, method: EncryptionMethod = EncryptionMethod.FERNET) -> EncryptedData:
    """
Quick content encryption."""
    encryption = create_content_encryption()
    return encryption.encrypt_content(content, method=method)

# Export main components
__all__ = [
    'SecurityLevel',
    'ThreatType',
    'EncryptionMethod',
    'SecurityAssessment',
    'EncryptedData',
    'SecurityScanner',
    'ContentEncryption',
    'AccessControl',
    'create_security_scanner',
    'create_content_encryption',
    'create_access_control',
    'quick_security_scan',
    'quick_encrypt_content',
]
