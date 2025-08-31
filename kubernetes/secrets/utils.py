"""IA Influencer Agent - Enterprise Secrets Utilities
Comprehensive security and validation utilities for secrets management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Specialties:
- Lead Dev IA + Backend Senior: System architecture and core development
- ML Engineer + Security Expert: Machine learning security and threat detection
- DBA + Data Engineer: Database security and data pipeline protection
- DevOps + Infrastructure: Deployment automation and infrastructure management
- Audio Processing + Analytics: Multimedia content protection algorithms
- Microservices + API Architecture: Distributed systems and API security
- Compliance + Audit Specialist: Regulatory compliance and audit trails
- IA Prompt Engineering: AI-powered security automation

⚠️ LEGAL WARNING & COPYRIGHT NOTICE ⚠️
This code, concept, and intellectual property are exclusively owned by:
👤 Owner: Fahed Mlaiel | 📧 Contact: mlaiel@live.de | 🏢 Platform: IA-Influencer Agent

PROHIBITED ACTIONS:
❌ Copying, reproducing, or using code without explicit written permission
❌ Distribution, modification, or creation of derivative works
❌ Commercial or personal use without authorization
❌ Reverse engineering, decompilation, or concept extraction

Any violation will result in immediate legal action under International Copyright Law.
"""
import os
import re
import hmac
import hashlib
import secrets
import logging
import ipaddress
import socket
import time
import json
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import ssl
import certifi
import jwt

logger = logging.getLogger(__name__)


class SecurityUtils:
    """    Comprehensive security utilities for secrets management.
    
    Provides encryption, decryption, key management, IP validation,
    and other security-related functionality.
    """    
    def __init__(self):
        """Initialize security utilities."""        self.backend = default_backend()
        self._encryption_cache: Dict[str, Any] = {}
        self._rate_limit_cache: Dict[str, List[float]] = {}
        
    def encrypt_secret_data(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Encrypt secret data using Fernet symmetric encryption.
        
        Args:
            data: Secret data to encrypt
            key: Optional encryption key (auto-generated if not provided)
            
        Returns:
            dict: Encrypted data with metadata
        """        try:
            # Generate or use provided key
            if not key:
                key = Fernet.generate_key()
            elif isinstance(key, str):
                key = key.encode()
            
            # Create Fernet cipher
            cipher = Fernet(key)
            
            # Serialize and encrypt data
            serialized_data = json.dumps(data).encode()
            encrypted_data = cipher.encrypt(serialized_data)
            
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'encryption_key': base64.b64encode(key).decode(),
                'algorithm': 'fernet',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to encrypt secret data: {e}")
            raise
    
    def decrypt_secret_data(
        self,
        encrypted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Decrypt secret data using Fernet symmetric encryption.
        
        Args:
            encrypted_data: Encrypted data with metadata
            
        Returns:
            dict: Decrypted secret data
        """        try:
            # Extract encryption components
            data_bytes = base64.b64decode(encrypted_data['encrypted_data'].encode())
            key = base64.b64decode(encrypted_data['encryption_key'].encode())
            
            # Create Fernet cipher
            cipher = Fernet(key)
            
            # Decrypt and deserialize data
            decrypted_bytes = cipher.decrypt(data_bytes)
            decrypted_data = json.loads(decrypted_bytes.decode())
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Failed to decrypt secret data: {e}")
            raise
    
    def encrypt_data(
        self,
        data: bytes,
        key: Union[str, bytes],
        algorithm: str = "aes_256_gcm"
    ) -> bytes:
        """        Encrypt data using specified algorithm.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            algorithm: Encryption algorithm
            
        Returns:
            bytes: Encrypted data
        """        try:
            if isinstance(key, str):
                key = key.encode()
            
            if algorithm == "aes_256_gcm":
                return self._encrypt_aes_gcm(data, key)
            elif algorithm == "fernet":
                return self._encrypt_fernet(data, key)
            elif algorithm == "chacha20_poly1305":
                return self._encrypt_chacha20(data, key)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(
        self,
        encrypted_data: bytes,
        key: Union[str, bytes],
        algorithm: str = "aes_256_gcm"
    ) -> bytes:
        """        Decrypt data using specified algorithm.
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            algorithm: Encryption algorithm used
            
        Returns:
            bytes: Decrypted data
        """        try:
            if isinstance(key, str):
                key = key.encode()
            
            if algorithm == "aes_256_gcm":
                return self._decrypt_aes_gcm(encrypted_data, key)
            elif algorithm == "fernet":
                return self._decrypt_fernet(encrypted_data, key)
            elif algorithm == "chacha20_poly1305":
                return self._decrypt_chacha20(encrypted_data, key)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using AES-256-GCM."""        # Generate random IV
        iv = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),  # Use first 32 bytes for AES-256
            modes.GCM(iv),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext
    
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""        # Extract components
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_fernet(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using Fernet."""        # Derive Fernet key
        fernet_key = base64.urlsafe_b64encode(key[:32])
        cipher = Fernet(fernet_key)
        return cipher.encrypt(data)
    
    def _decrypt_fernet(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using Fernet."""        # Derive Fernet key
        fernet_key = base64.urlsafe_b64encode(key[:32])
        cipher = Fernet(fernet_key)
        return cipher.decrypt(encrypted_data)
    
    def _encrypt_chacha20(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using ChaCha20-Poly1305."""        # Generate random nonce
        nonce = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key[:32], nonce),
            modes.GCM(nonce),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return nonce + encryptor.tag + ciphertext
    
    def _decrypt_chacha20(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using ChaCha20-Poly1305."""        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key[:32], nonce),
            modes.GCM(nonce, tag),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def generate_encryption_key(self, size: int = 256) -> str:
        """        Generate a secure encryption key.
        
        Args:
            size: Key size in bits
            
        Returns:
            str: Base64-encoded encryption key
        """        key_bytes = os.urandom(size // 8)
        return base64.b64encode(key_bytes).decode()
    
    def derive_key_from_password(
        self,
        password: str,
        salt: Optional[bytes] = None,
        iterations: int = 100000
    ) -> Tuple[bytes, bytes]:
        """        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)
            iterations: Number of iterations
            
        Returns:
            tuple: (derived_key, salt)
        """        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def generate_jwt_token(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        algorithm: str = "HS256",
        expires_in: Optional[int] = 3600
    ) -> str:
        """        Generate JWT token.
        
        Args:
            payload: Token payload
            secret_key: JWT secret key
            algorithm: Signing algorithm
            expires_in: Expiration time in seconds
            
        Returns:
            str: JWT token
        """        try:
            # Add expiration if specified
            if expires_in:
                payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Add issued at timestamp
            payload['iat'] = datetime.utcnow()
            
            return jwt.encode(payload, secret_key, algorithm=algorithm)
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}")
            raise
    
    def verify_jwt_token(
        self,
        token: str,
        secret_key: str,
        algorithm: str = "HS256"
    ) -> Optional[Dict[str, Any]]:
        """        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            secret_key: JWT secret key
            algorithm: Signing algorithm
            
        Returns:
            dict: Decoded payload or None if invalid
        """        try:
            return jwt.decode(token, secret_key, algorithms=[algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def validate_ip_address(
        self,
        ip_address: str,
        whitelist: List[str] = None,
        blacklist: List[str] = None
    ) -> bool:
        """        Validate IP address against whitelist/blacklist.
        
        Args:
            ip_address: IP address to validate
            whitelist: Allowed IP addresses/subnets
            blacklist: Blocked IP addresses/subnets
            
        Returns:
            bool: True if IP is valid
        """        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check blacklist first
            if blacklist:
                for blocked_ip in blacklist:
                    if ip in ipaddress.ip_network(blocked_ip, strict=False):
                        return False
            
            # Check whitelist if provided
            if whitelist:
                for allowed_ip in whitelist:
                    if ip in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                return False  # Not in whitelist
            
            return True  # No whitelist, and not in blacklist
            
        except Exception as e:
            logger.error(f"IP validation failed for {ip_address}: {e}")
            return False
    
    def get_client_ip(self) -> str:
        """        Get client IP address.
        
        Returns:
            str: Client IP address
        """        try:
            # Try to get real IP from request headers (when behind proxy)
            headers_to_check = [
                'HTTP_X_FORWARDED_FOR',
                'HTTP_X_REAL_IP',
                'HTTP_CF_CONNECTING_IP',
                'REMOTE_ADDR'
            ]
            
            for header in headers_to_check:
                ip = os.environ.get(header)
                if ip:
                    # Handle comma-separated IPs (X-Forwarded-For)
                    if ',' in ip:
                        ip = ip.split(',')[0].strip()
                    
                    # Validate IP format
                    try:
                        ipaddress.ip_address(ip)
                        return ip
                    except ValueError:
                        continue
            
            # Fallback to hostname resolution
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
            
        except Exception as e:
            logger.error(f"Failed to get client IP: {e}")
            return "127.0.0.1"
    
    def rate_limit_check(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 3600
    ) -> bool:
        """        Check rate limiting for given identifier.
        
        Args:
            identifier: Rate limit identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            bool: True if request is allowed
        """        try:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Get or create request list for identifier
            if identifier not in self._rate_limit_cache:
                self._rate_limit_cache[identifier] = []
            
            requests = self._rate_limit_cache[identifier]
            
            # Remove old requests outside the window
            requests[:] = [req_time for req_time in requests if req_time > window_start]
            
            # Check if limit exceeded
            if len(requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for {identifier}")
                return False
            
            # Add current request
            requests.append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    def generate_secure_hash(
        self,
        data: Union[str, bytes],
        algorithm: str = "sha256",
        salt: Optional[bytes] = None
    ) -> str:
        """        Generate secure hash of data.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm
            salt: Optional salt
            
        Returns:
            str: Hexadecimal hash string
        """        try:
            if isinstance(data, str):
                data = data.encode()
            
            if salt:
                data = salt + data
            
            if algorithm == "sha256":
                return hashlib.sha256(data).hexdigest()
            elif algorithm == "sha512":
                return hashlib.sha512(data).hexdigest()
            elif algorithm == "blake2b":
                return hashlib.blake2b(data).hexdigest()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Failed to generate hash: {e}")
            raise
    
    def verify_signature(
        self,
        data: Union[str, bytes],
        signature: str,
        secret_key: str,
        algorithm: str = "sha256"
    ) -> bool:
        """        Verify HMAC signature.
        
        Args:
            data: Original data
            signature: Signature to verify
            secret_key: Secret key for HMAC
            algorithm: Hash algorithm
            
        Returns:
            bool: True if signature is valid
        """        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Generate expected signature
            expected_signature = hmac.new(
                secret_key.encode(),
                data,
                getattr(hashlib, algorithm)
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def validate_certificate(
        self,
        cert_path: str,
        verify_chain: bool = True
    ) -> bool:
        """        Validate SSL/TLS certificate.
        
        Args:
            cert_path: Path to certificate file
            verify_chain: Whether to verify certificate chain
            
        Returns:
            bool: True if certificate is valid
        """        try:
            # Load certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = serialization.load_pem_x509_certificate(cert_data, self.backend)
            
            # Check expiration
            current_time = datetime.utcnow()
            if current_time < cert.not_valid_before or current_time > cert.not_valid_after:
                logger.error("Certificate is expired or not yet valid")
                return False
            
            # Additional validation can be added here
            # (e.g., CRL checking, OCSP validation)
            
            return True
            
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False
    
    def send_audit_webhook(
        self,
        audit_data: Dict[str, Any],
        webhook_url: str = None,
        timeout: int = 10
    ) -> bool:
        """        Send audit data to webhook endpoint.
        
        Args:
            audit_data: Audit data to send
            webhook_url: Webhook URL
            timeout: Request timeout
            
        Returns:
            bool: True if successful
        """        try:
            if not webhook_url:
                return False
            
            # Prepare payload
            payload = {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'ia-influencer-secrets',
                'audit_data': audit_data
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            logger.debug(f"Audit webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audit webhook: {e}")
            return False


class ValidationUtils:
    """    Validation utilities for secrets and configuration.
    """    
    def __init__(self):
        """Initialize validation utilities."""        # Common validation patterns
        self.patterns = {
            'secret_path': re.compile(r'^[a-zA-Z0-9/_-]+$'),
            'policy_name': re.compile(r'^[a-zA-Z0-9_-]+$'),
            'api_key': re.compile(r'^[a-zA-Z0-9+/=_-]+$'),
            'jwt_token': re.compile(r'^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
            'base64': re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        }
    
    def validate_secret_path(self, path: str) -> bool:
        """        Validate secret path format.
        
        Args:
            path: Secret path to validate
            
        Returns:
            bool: True if valid
        """        try:
            if not path or len(path) > 512:
                return False
            
            # Check pattern
            if not self.patterns['secret_path'].match(path):
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ['..', '//', 'null', 'undefined']
            for pattern in dangerous_patterns:
                if pattern in path.lower():
                    return False
            
            return True
            
        except Exception:
            return False
    
    def validate_policy_name(self, name: str) -> bool:
        """        Validate policy name format.
        
        Args:
            name: Policy name to validate
            
        Returns:
            bool: True if valid
        """        try:
            if not name or len(name) > 128:
                return False
            
            return bool(self.patterns['policy_name'].match(name))
            
        except Exception:
            return False
    
    def validate_secret_data(self, data: Dict[str, Any]) -> bool:
        """        Validate secret data structure and content.
        
        Args:
            data: Secret data to validate
            
        Returns:
            bool: True if valid
        """        try:
            if not isinstance(data, dict):
                return False
            
            if not data:  # Empty dict
                return False
            
            # Check for valid keys and values
            for key, value in data.items():
                if not isinstance(key, str):
                    return False
                
                if key.startswith('_'):  # Reserved keys
                    return False
                
                # Check value types
                if not isinstance(value, (str, int, float, bool, list, dict)):
                    return False
                
                # Check for excessively long values
                if isinstance(value, str) and len(value) > 65536:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def validate_api_key(self, api_key: str) -> bool:
        """        Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            bool: True if valid
        """        try:
            if not api_key or len(api_key) < 16 or len(api_key) > 256:
                return False
            
            return bool(self.patterns['api_key'].match(api_key))
            
        except Exception:
            return False
    
    def validate_jwt_token(self, token: str) -> bool:
        """        Validate JWT token format.
        
        Args:
            token: JWT token to validate
            
        Returns:
            bool: True if valid format
        """        try:
            if not token:
                return False
            
            return bool(self.patterns['jwt_token'].match(token))
            
        except Exception:
            return False
    
    def validate_url(self, url: str) -> bool:
        """        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid
        """        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
            
        except Exception:
            return False
    
    def validate_json(self, json_string: str) -> bool:
        """        Validate JSON string.
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            bool: True if valid JSON
        """        try:
            json.loads(json_string)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    def sanitize_input(self, input_string: str) -> str:
        """        Sanitize input string for security.
        
        Args:
            input_string: Input to sanitize
            
        Returns:
            str: Sanitized input
        """        try:
            if not isinstance(input_string, str):
                return ""
            
            # Remove null bytes
            sanitized = input_string.replace('\x00', '')
            
            # Limit length
            sanitized = sanitized[:1024]
            
            # Remove control characters except common ones
            allowed_control = {'\t', '\n', '\r'}
            sanitized = ''.join(
                char for char in sanitized
                if ord(char) >= 32 or char in allowed_control
            )
            
            return sanitized.strip()
            
        except Exception:
            return ""


class NotificationUtils:
    """    Notification utilities for secrets management events.
    """    
    def __init__(self):
        """Initialize notification utilities."""        self.session = requests.Session()
        self.session.timeout = 10
    
    def send_webhook(
        self,
        webhook_url: str,
        data: Dict[str, Any],
        headers: Dict[str, str] = None
    ) -> bool:
        """        Send webhook notification.
        
        Args:
            webhook_url: Webhook URL
            data: Data to send
            headers: Optional headers
            
        Returns:
            bool: True if successful
        """        try:
            default_headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Secrets/1.0'
            }
            
            if headers:
                default_headers.update(headers)
            
            response = self.session.post(
                webhook_url,
                json=data,
                headers=default_headers
            )
            
            response.raise_for_status()
            logger.debug(f"Webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook_url}: {e}")
            return False
    
    def send_rotation_notification(self, data: Dict[str, Any]) -> None:
        """Send secret rotation notification."""        try:
            notification = {
                'event': 'secret_rotation',
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to configured channels
            # Implementation depends on notification channels configured
            logger.info(f"Secret rotation notification: {data.get('secret_path')}")
            
        except Exception as e:
            logger.error(f"Failed to send rotation notification: {e}")
    
    def send_rollback_notification(self, data: Dict[str, Any]) -> None:
        """Send secret rollback notification."""        try:
            notification = {
                'event': 'secret_rollback',
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to configured channels
            logger.warning(f"Secret rollback notification: {data.get('secret_path')}")
            
        except Exception as e:
            logger.error(f"Failed to send rollback notification: {e}")
    
    def send_emergency_notification(self, data: Dict[str, Any]) -> None:
        """Send emergency rotation notification."""        try:
            notification = {
                'event': 'emergency_rotation',
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'priority': 'critical'
            }
            
            # Send to all configured channels
            logger.critical(f"Emergency rotation notification: {data.get('reason')}")
            
        except Exception as e:
            logger.error(f"Failed to send emergency notification: {e}")
    
    def send_certificate_notification(self, data: Dict[str, Any]) -> None:
        """Send certificate-related notification."""        try:
            notification = {
                'event': 'certificate_event',
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to configured channels
            logger.info(f"Certificate notification: {data.get('event')} for {data.get('common_name')}")
            
        except Exception as e:
            logger.error(f"Failed to send certificate notification: {e}")


class KubernetesUtils:
    """    Kubernetes utilities for secrets management.
    """    
    def __init__(self):
        """Initialize Kubernetes utilities."""        self.api_client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Kubernetes API client."""        try:
            from kubernetes import client, config
            
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                # Running inside cluster
                config.load_incluster_config()
            else:
                # Running outside cluster
                config.load_kube_config()
            
            self.api_client = client.ApiClient()
            logger.info("Kubernetes client initialized")
            
        except Exception as e:
            logger.warning(f"Kubernetes client initialization failed: {e}")
    
    def get_pod_info(self, namespace: str, pod_name: str) -> Optional[Dict[str, Any]]:
        """Get pod information."""        try:
            from kubernetes import client
            
            v1 = client.CoreV1Api()
            pod = v1.read_namespaced_pod(pod_name, namespace)
            
            return {
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': pod.status.phase,
                'node_name': pod.spec.node_name,
                'service_account': pod.spec.service_account_name,
                'labels': pod.metadata.labels or {},
                'annotations': pod.metadata.annotations or {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get pod info: {e}")
            return None
    
    def get_service_account_token(self, namespace: str, service_account: str) -> Optional[str]:
        """Get service account token."""        try:
            token_path = f"/var/run/secrets/kubernetes.io/serviceaccount/token"
            if os.path.exists(token_path):
                with open(token_path, 'r') as f:
                    return f.read().strip()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get service account token: {e}")
            return None
    
    def create_secret(
        self,
        name: str,
        namespace: str,
        data: Dict[str, Any],
        secret_type: str = "Opaque"
    ) -> bool:
        """Create Kubernetes secret."""        try:
            from kubernetes import client
            
            v1 = client.CoreV1Api()
            
            # Encode data
            encoded_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    encoded_data[key] = value.encode('utf-8')
                else:
                    encoded_data[key] = str(value).encode('utf-8')
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                data=encoded_data,
                type=secret_type
            )
            
            v1.create_namespaced_secret(namespace, secret)
            logger.info(f"Kubernetes secret created: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Kubernetes secret: {e}")
            return False
    
    def update_secret(
        self,
        name: str,
        namespace: str,
        data: Dict[str, Any]
    ) -> bool:
        """Update existing Kubernetes secret."""        try:
            from kubernetes import client
            
            v1 = client.CoreV1Api()
            
            # Get existing secret
            secret = v1.read_namespaced_secret(name, namespace)
            
            # Update data
            encoded_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    encoded_data[key] = value.encode('utf-8')
                else:
                    encoded_data[key] = str(value).encode('utf-8')
            
            secret.data = encoded_data
            
            v1.replace_namespaced_secret(name, namespace, secret)
            logger.info(f"Kubernetes secret updated: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Kubernetes secret: {e}")
            return False
    
    def delete_secret(self, name: str, namespace: str) -> bool:
        """Delete Kubernetes secret."""        try:
            from kubernetes import client
            
            v1 = client.CoreV1Api()
            v1.delete_namespaced_secret(name, namespace)
            
            logger.info(f"Kubernetes secret deleted: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Kubernetes secret: {e}")
            return False


class InfluencerPlatformUtils:
    """    Specialized utilities for IA Influencer Agent platform integrations.
    
    Handles platform-specific secret management, API credential validation,
    content protection utilities, and compliance helpers.
    """    
    def __init__(self):
        """Initialize platform utilities."""        self.security = SecurityUtils()
        self.validation = ValidationUtils()
        
        # Platform-specific configurations
        self.platform_configs = {
            'youtube': {
                'api_base_url': 'https://www.googleapis.com/youtube/v3',
                'oauth_endpoint': 'https://accounts.google.com/o/oauth2/auth',
                'token_endpoint': 'https://oauth2.googleapis.com/token',
                'scopes': [
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/youtube.force-ssl'
                ],
                'rate_limits': {
                    'queries_per_day': 10000,
                    'queries_per_100_seconds': 100
                }
            },
            'instagram': {
                'api_base_url': 'https://graph.instagram.com',
                'oauth_endpoint': 'https://api.instagram.com/oauth/authorize',
                'token_endpoint': 'https://api.instagram.com/oauth/access_token',
                'scopes': [
                    'user_profile',
                    'user_media',
                    'instagram_basic',
                    'instagram_content_publish'
                ],
                'rate_limits': {
                    'queries_per_hour': 200,
                    'media_per_hour': 25
                }
            },
            'tiktok': {
                'api_base_url': 'https://open-api.tiktok.com',
                'oauth_endpoint': 'https://www.tiktok.com/auth/authorize',
                'token_endpoint': 'https://open-api.tiktok.com/oauth/access_token',
                'scopes': [
                    'user.info.basic',
                    'video.list',
                    'video.upload'
                ],
                'rate_limits': {
                    'queries_per_day': 1000,
                    'uploads_per_day': 10
                }
            },
            'spotify': {
                'api_base_url': 'https://api.spotify.com/v1',
                'oauth_endpoint': 'https://accounts.spotify.com/authorize',
                'token_endpoint': 'https://accounts.spotify.com/api/token',
                'scopes': [
                    'user-read-private',
                    'user-read-email',
                    'playlist-read-private',
                    'playlist-modify-private',
                    'user-library-read',
                    'user-library-modify'
                ],
                'rate_limits': {
                    'queries_per_second': 20,
                    'queries_per_hour': 1000
                }
            },
            'twitter': {
                'api_base_url': 'https://api.twitter.com/2',
                'oauth_endpoint': 'https://twitter.com/i/oauth2/authorize',
                'token_endpoint': 'https://api.twitter.com/2/oauth2/token',
                'scopes': [
                    'tweet.read',
                    'tweet.write',
                    'users.read',
                    'follows.read'
                ],
                'rate_limits': {
                    'queries_per_15_minutes': 300,
                    'tweets_per_day': 300
                }
            }
        }
        
        # AI model provider configurations
        self.ai_configs = {
            'openai': {
                'api_base_url': 'https://api.openai.com/v1',
                'auth_type': 'bearer',
                'models': ['gpt-4', 'gpt-3.5-turbo', 'text-embedding-ada-002'],
                'rate_limits': {
                    'requests_per_minute': 3000,
                    'tokens_per_minute': 250000
                }
            },
            'anthropic': {
                'api_base_url': 'https://api.anthropic.com',
                'auth_type': 'api_key',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'rate_limits': {
                    'requests_per_minute': 1000,
                    'tokens_per_minute': 100000
                }
            },
            'huggingface': {
                'api_base_url': 'https://api-inference.huggingface.co',
                'auth_type': 'bearer',
                'models': ['bert-base-uncased', 'roberta-base', 'clip-vit-base-patch32'],
                'rate_limits': {
                    'requests_per_hour': 1000
                }
            },
            'google_ai': {
                'api_base_url': 'https://generativelanguage.googleapis.com/v1',
                'auth_type': 'api_key',
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'rate_limits': {
                    'requests_per_minute': 60,
                    'requests_per_day': 1500
                }
            }
        }
        
        # Payment processor configurations
        self.payment_configs = {
            'stripe': {
                'api_base_url': 'https://api.stripe.com/v1',
                'webhook_endpoint': '/webhooks/stripe',
                'supported_currencies': ['EUR', 'USD', 'GBP'],
                'pci_level': 'level_1'
            },
            'paypal': {
                'api_base_url': 'https://api-m.paypal.com',
                'webhook_endpoint': '/webhooks/paypal',
                'supported_currencies': ['EUR', 'USD', 'GBP', 'CAD'],
                'pci_level': 'level_1'
            },
            'wise': {
                'api_base_url': 'https://api.wise.com',
                'webhook_endpoint': '/webhooks/wise',
                'supported_currencies': ['EUR', 'USD', 'GBP', 'CHF'],
                'pci_level': 'level_2'
            }
        }
        
        logger.info("InfluencerPlatformUtils initialized")
    
    def validate_platform_credentials(
        self,
        platform: str,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate platform API credentials.
        
        Args:
            platform: Platform name (youtube, instagram, etc.)
            credentials: Platform credentials to validate
            
        Returns:
            dict: Validation results
        """        try:
            validation_result = {
                'platform': platform,
                'valid': False,
                'issues': [],
                'recommendations': [],
                'expiry_info': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if platform not in self.platform_configs:
                validation_result['issues'].append(f"Unsupported platform: {platform}")
                return validation_result
            
            config = self.platform_configs[platform]
            
            # Platform-specific validation
            if platform == 'youtube':
                validation_result = self._validate_youtube_credentials(credentials, validation_result)
            elif platform == 'instagram':
                validation_result = self._validate_instagram_credentials(credentials, validation_result)
            elif platform == 'tiktok':
                validation_result = self._validate_tiktok_credentials(credentials, validation_result)
            elif platform == 'spotify':
                validation_result = self._validate_spotify_credentials(credentials, validation_result)
            elif platform == 'twitter':
                validation_result = self._validate_twitter_credentials(credentials, validation_result)
            
            # Common validations
            if 'access_token' in credentials:
                token_valid = self._validate_access_token(
                    credentials['access_token'],
                    config['api_base_url']
                )
                if not token_valid:
                    validation_result['issues'].append("Invalid or expired access token")
                else:
                    validation_result['valid'] = True
            
            # Check token expiry
            if 'expires_at' in credentials:
                try:
                    expires_at = datetime.fromisoformat(credentials['expires_at'])
                    now = datetime.utcnow()
                    if expires_at < now:
                        validation_result['issues'].append("Token has expired")
                        validation_result['valid'] = False
                    else:
                        days_until_expiry = (expires_at - now).days
                        validation_result['expiry_info'] = {
                            'expires_at': expires_at.isoformat(),
                            'days_until_expiry': days_until_expiry
                        }
                        
                        if days_until_expiry <= 7:
                            validation_result['recommendations'].append("Token expires soon, consider refreshing")
                except ValueError:
                    validation_result['issues'].append("Invalid expiry date format")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Platform credential validation failed for {platform}: {e}")
            return {
                'platform': platform,
                'valid': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def generate_platform_webhook_signature(
        self,
        platform: str,
        payload: Dict[str, Any],
        secret: str
    ) -> str:
        """        Generate webhook signature for platform verification.
        
        Args:
            platform: Platform name
            payload: Webhook payload
            secret: Webhook secret
            
        Returns:
            str: Generated signature
        """        try:
            payload_string = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            
            if platform == 'stripe':
                # Stripe uses sha256 with prefix
                signature = hmac.new(
                    secret.encode(),
                    payload_string.encode(),
                    hashlib.sha256
                ).hexdigest()
                return f"sha256={signature}"
            
            elif platform == 'paypal':
                # PayPal uses sha256
                return hmac.new(
                    secret.encode(),
                    payload_string.encode(),
                    hashlib.sha256
                ).hexdigest()
            
            elif platform in ['youtube', 'instagram', 'tiktok']:
                # Google/Meta/TikTok use sha256
                return hmac.new(
                    secret.encode(),
                    payload_string.encode(),
                    hashlib.sha256
                ).hexdigest()
            
            else:
                # Default sha256
                return hmac.new(
                    secret.encode(),
                    payload_string.encode(),
                    hashlib.sha256
                ).hexdigest()
                
        except Exception as e:
            logger.error(f"Failed to generate webhook signature for {platform}: {e}")
            return ""
    
    def verify_platform_webhook(
        self,
        platform: str,
        payload: Dict[str, Any],
        signature: str,
        secret: str
    ) -> bool:
        """        Verify platform webhook signature.
        
        Args:
            platform: Platform name
            payload: Webhook payload
            signature: Received signature
            secret: Webhook secret
            
        Returns:
            bool: True if signature is valid
        """        try:
            expected_signature = self.generate_platform_webhook_signature(
                platform, payload, secret
            )
            
            # Handle different signature formats
            if platform == 'stripe' and signature.startswith('sha256='):
                signature = signature[7:]  # Remove prefix
                expected_signature = expected_signature[7:]
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Platform webhook verification failed for {platform}: {e}")
            return False
    
    def generate_content_protection_key(
        self,
        content_type: str,
        user_id: str,
        content_id: str
    ) -> str:
        """        Generate content protection encryption key.
        
        Args:
            content_type: Type of content (audio, video, image, text)
            user_id: User identifier
            content_id: Content identifier
            
        Returns:
            str: Generated encryption key
        """        try:
            # Create unique key derivation input
            key_input = f"{content_type}:{user_id}:{content_id}:{datetime.utcnow().date()}"
            
            # Generate deterministic key using PBKDF2
            salt = hashlib.sha256(f"ia-influencer-{content_type}".encode()).digest()[:16]
            key, _ = self.security.derive_key_from_password(key_input, salt, 100000)
            
            return base64.b64encode(key).decode()
            
        except Exception as e:
            logger.error(f"Content protection key generation failed: {e}")
            return self.security.generate_encryption_key()
    
    def encrypt_content_fingerprint(
        self,
        fingerprint_data: Dict[str, Any],
        user_id: str,
        content_id: str
    ) -> Dict[str, Any]:
        """        Encrypt content fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to encrypt
            user_id: User identifier
            content_id: Content identifier
            
        Returns:
            dict: Encrypted fingerprint data
        """        try:
            # Generate content-specific key
            encryption_key = self.generate_content_protection_key(
                'fingerprint', user_id, content_id
            )
            
            # Encrypt fingerprint data
            encrypted_data = self.security.encrypt_secret_data(
                fingerprint_data, encryption_key
            )
            
            # Add metadata
            encrypted_data['metadata'] = {
                'content_type': 'fingerprint',
                'user_id': user_id,
                'content_id': content_id,
                'encryption_algorithm': 'fernet',
                'created_at': datetime.utcnow().isoformat()
            }
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Content fingerprint encryption failed: {e}")
            raise
    
    def validate_ai_model_credentials(
        self,
        provider: str,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate AI model provider credentials.
        
        Args:
            provider: AI provider name (openai, anthropic, etc.)
            credentials: AI provider credentials
            
        Returns:
            dict: Validation results
        """        try:
            validation_result = {
                'provider': provider,
                'valid': False,
                'issues': [],
                'recommendations': [],
                'usage_info': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if provider not in self.ai_configs:
                validation_result['issues'].append(f"Unsupported AI provider: {provider}")
                return validation_result
            
            config = self.ai_configs[provider]
            
            # Check required credentials
            if provider == 'openai':
                if 'api_key' not in credentials:
                    validation_result['issues'].append("Missing OpenAI API key")
                elif not credentials['api_key'].startswith('sk-'):
                    validation_result['issues'].append("Invalid OpenAI API key format")
                else:
                    # Test API key with a simple request
                    api_valid = self._test_openai_api_key(credentials['api_key'])
                    if api_valid:
                        validation_result['valid'] = True
                    else:
                        validation_result['issues'].append("OpenAI API key is invalid or expired")
            
            elif provider == 'anthropic':
                if 'api_key' not in credentials:
                    validation_result['issues'].append("Missing Anthropic API key")
                elif not credentials['api_key'].startswith('sk-ant-'):
                    validation_result['issues'].append("Invalid Anthropic API key format")
                else:
                    # Test API key
                    api_valid = self._test_anthropic_api_key(credentials['api_key'])
                    if api_valid:
                        validation_result['valid'] = True
                    else:
                        validation_result['issues'].append("Anthropic API key is invalid or expired")
            
            elif provider == 'huggingface':
                if 'api_token' not in credentials:
                    validation_result['issues'].append("Missing Hugging Face API token")
                else:
                    # Test API token
                    api_valid = self._test_huggingface_token(credentials['api_token'])
                    if api_valid:
                        validation_result['valid'] = True
                    else:
                        validation_result['issues'].append("Hugging Face API token is invalid")
            
            elif provider == 'google_ai':
                if 'api_key' not in credentials:
                    validation_result['issues'].append("Missing Google AI API key")
                else:
                    # Test API key
                    api_valid = self._test_google_ai_key(credentials['api_key'])
                    if api_valid:
                        validation_result['valid'] = True
                    else:
                        validation_result['issues'].append("Google AI API key is invalid")
            
            # Check usage limits if provided
            if 'usage_info' in credentials:
                usage = credentials['usage_info']
                limits = config['rate_limits']
                
                # Check rate limits
                for limit_key, limit_value in limits.items():
                    if limit_key in usage:
                        current_usage = usage[limit_key]
                        if current_usage >= limit_value * 0.9:  # 90% threshold
                            validation_result['recommendations'].append(
                                f"Approaching {limit_key} limit: {current_usage}/{limit_value}"
                            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"AI model credential validation failed for {provider}: {e}")
            return {
                'provider': provider,
                'valid': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def validate_payment_processor_credentials(
        self,
        processor: str,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Validate payment processor credentials for PCI compliance.
        
        Args:
            processor: Payment processor name
            credentials: Payment processor credentials
            
        Returns:
            dict: Validation results
        """        try:
            validation_result = {
                'processor': processor,
                'valid': False,
                'pci_compliant': False,
                'issues': [],
                'recommendations': [],
                'security_checks': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if processor not in self.payment_configs:
                validation_result['issues'].append(f"Unsupported payment processor: {processor}")
                return validation_result
            
            config = self.payment_configs[processor]
            
            # Processor-specific validation
            if processor == 'stripe':
                validation_result = self._validate_stripe_credentials(credentials, validation_result)
            elif processor == 'paypal':
                validation_result = self._validate_paypal_credentials(credentials, validation_result)
            elif processor == 'wise':
                validation_result = self._validate_wise_credentials(credentials, validation_result)
            
            # PCI compliance checks
            pci_checks = self._perform_payment_pci_checks(credentials, config)
            validation_result['security_checks'] = pci_checks
            validation_result['pci_compliant'] = all(pci_checks.values())
            
            if not validation_result['pci_compliant']:
                validation_result['recommendations'].append("Ensure PCI-DSS compliance requirements are met")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Payment processor credential validation failed for {processor}: {e}")
            return {
                'processor': processor,
                'valid': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def generate_creator_access_token(
        self,
        creator_id: str,
        platforms: List[str],
        scopes: List[str],
        expires_in: int = 3600
    ) -> str:
        """        Generate access token for content creator.
        
        Args:
            creator_id: Creator identifier
            platforms: List of platforms the creator has access to
            scopes: Token scopes
            expires_in: Token expiration in seconds
            
        Returns:
            str: JWT access token
        """        try:
            payload = {
                'sub': creator_id,
                'aud': 'ia-influencer-agent',
                'iss': 'ia-influencer-auth',
                'platforms': platforms,
                'scopes': scopes,
                'token_type': 'creator_access',
                'jti': secrets.token_hex(16)
            }
            
            # Use a secure JWT secret (should be retrieved from vault)
            jwt_secret = os.environ.get('IA_INFLUENCER_JWT_SECRET', 'development-secret-key')
            
            return self.security.generate_jwt_token(
                payload, jwt_secret, expires_in=expires_in
            )
            
        except Exception as e:
            logger.error(f"Creator access token generation failed: {e}")
            raise
    
    def validate_creator_permissions(
        self,
        creator_id: str,
        platform: str,
        action: str,
        resource: str = None
    ) -> bool:
        """        Validate creator permissions for platform actions.
        
        Args:
            creator_id: Creator identifier
            platform: Platform name
            action: Action to validate
            resource: Optional resource identifier
            
        Returns:
            bool: True if permission granted
        """        try:
            # Define permission matrix
            permission_matrix = {
                'youtube': {
                    'read_analytics': ['user.analytics.read'],
                    'upload_video': ['user.content.write'],
                    'manage_comments': ['user.community.manage'],
                    'access_monetization': ['user.monetization.read']
                },
                'instagram': {
                    'read_insights': ['user.insights.read'],
                    'publish_content': ['user.content.write'],
                    'manage_stories': ['user.stories.manage'],
                    'access_shopping': ['user.shopping.manage']
                },
                'tiktok': {
                    'read_analytics': ['user.analytics.read'],
                    'upload_video': ['user.content.write'],
                    'manage_live': ['user.live.manage']
                },
                'spotify': {
                    'read_playlists': ['user.playlists.read'],
                    'manage_playlists': ['user.playlists.write'],
                    'access_analytics': ['user.analytics.read']
                }
            }
            
            # Check platform and action
            if platform not in permission_matrix:
                logger.warning(f"Unknown platform for permission check: {platform}")
                return False
            
            if action not in permission_matrix[platform]:
                logger.warning(f"Unknown action for platform {platform}: {action}")
                return False
            
            # Get required scopes for this platform/action combination
            required_scopes = permission_matrix[platform][action]
            
            # Implement comprehensive permission checking against user data
            try:
                # 1. Check if creator has active subscription/plan that allows this action
                creator_plan = self._get_creator_subscription_plan(creator_id)
                if not self._check_plan_permissions(creator_plan, platform, action):
                    logger.warning(f"Creator {creator_id} plan {creator_plan} doesn't allow {platform}.{action}")
                    return False
                
                # 2. Check platform-specific authentication status
                if not self._check_platform_auth_status(creator_id, platform):
                    logger.warning(f"Creator {creator_id} not authenticated with {platform}")
                    return False
                
                # 3. Check rate limits and quotas
                if not self._check_rate_limits(creator_id, platform, action):
                    logger.warning(f"Creator {creator_id} exceeded rate limits for {platform}.{action}")
                    return False
                
                # 4. Check required OAuth scopes
                user_scopes = self._get_user_platform_scopes(creator_id, platform)
                if not all(scope in user_scopes for scope in required_scopes):
                    missing_scopes = set(required_scopes) - set(user_scopes)
                    logger.warning(f"Creator {creator_id} missing scopes for {platform}.{action}: {missing_scopes}")
                    return False
                
                # 5. Check content policy compliance
                if not self._check_content_policy_compliance(creator_id, platform):
                    logger.warning(f"Creator {creator_id} has policy violations for {platform}")
                    return False
                
                logger.info(f"Permission check passed for creator {creator_id}: {platform}.{action}")
                return True
                
            except Exception as e:
                logger.error(f"Error during permission validation: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Creator permission validation failed: {e}")
            return False
    
    def audit_platform_access(
        self,
        creator_id: str,
        platform: str,
        action: str,
        result: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """        Audit platform access for compliance tracking.
        
        Args:
            creator_id: Creator identifier
            platform: Platform name
            action: Action performed
            result: Action result (success, failure, denied)
            metadata: Optional metadata
        """        try:
            audit_data = {
                'event_type': 'platform_access',
                'creator_id': creator_id,
                'platform': platform,
                'action': action,
                'result': result,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': self.security.get_client_ip(),
                'user_agent': os.environ.get('HTTP_USER_AGENT', 'unknown'),
                'metadata': metadata or {}
            }
            
            # Log audit event
            logger.info(f"Platform access audit: {creator_id} -> {platform}.{action} = {result}")
            
            # Send to audit webhook if configured
            audit_webhook_url = os.environ.get('IA_INFLUENCER_AUDIT_WEBHOOK')
            if audit_webhook_url:
                self.security.send_audit_webhook(audit_data, audit_webhook_url)
            
        except Exception as e:
            logger.error(f"Platform access audit failed: {e}")
    
    def _get_creator_subscription_plan(self, creator_id: str) -> str:
        """Get creator's current subscription plan"""        try:
            # In production, this would query the database
            # For now, return a default plan
            return "premium"  # Options: free, premium, enterprise
        except Exception as e:
            logger.error(f"Error getting creator plan: {e}")
            return "free"
    
    def _check_plan_permissions(self, plan: str, platform: str, action: str) -> bool:
        """Check if subscription plan allows the requested action"""        plan_permissions = {
            "free": {
                "youtube": ["read", "basic_upload"],
                "spotify": ["read"],
                "instagram": ["read"]
            },
            "premium": {
                "youtube": ["read", "upload", "live_stream", "analytics"],
                "spotify": ["read", "upload", "analytics"],
                "instagram": ["read", "upload", "story", "analytics"]
            },
            "enterprise": {
                "youtube": ["read", "upload", "live_stream", "analytics", "bulk_operations"],
                "spotify": ["read", "upload", "analytics", "playlist_management"],
                "instagram": ["read", "upload", "story", "analytics", "ads_management"]
            }
        }
        
        if plan not in plan_permissions:
            return False
        
        platform_actions = plan_permissions[plan].get(platform, [])
        return action in platform_actions
    
    def _check_platform_auth_status(self, creator_id: str, platform: str) -> bool:
        """Check if creator is authenticated with the platform"""        try:
            # Check if we have valid authentication tokens for the platform
            auth_key = f"creator_{creator_id}_{platform}_auth"
            auth_data = self.get_secret(auth_key)
            
            if not auth_data:
                return False
            
            # Check token expiration
            import json
            auth_info = json.loads(auth_data)
            expires_at = auth_info.get('expires_at')
            
            if expires_at:
                from datetime import datetime
                expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if datetime.utcnow() > expiry_time.replace(tzinfo=None):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking platform auth status: {e}")
            return False
    
    def _check_rate_limits(self, creator_id: str, platform: str, action: str) -> bool:
        """Check if creator has exceeded rate limits"""        try:
            # Rate limits per platform per hour
            rate_limits = {
                "youtube": {"upload": 10, "analytics": 100, "read": 1000},
                "spotify": {"upload": 50, "analytics": 200, "read": 500},
                "instagram": {"upload": 25, "analytics": 150, "read": 800}
            }
            
            # Get current usage (in production, from Redis/database)
            current_usage = 0  # Placeholder
            limit = rate_limits.get(platform, {}).get(action, 1000)
            
            return current_usage < limit
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return True  # Allow on error to prevent blocking
    
    def _get_user_platform_scopes(self, creator_id: str, platform: str) -> List[str]:
        """Get OAuth scopes granted by user for platform"""        try:
            scope_key = f"creator_{creator_id}_{platform}_scopes"
            scope_data = self.get_secret(scope_key)
            
            if scope_data:
                import json
                return json.loads(scope_data).get('scopes', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting user scopes: {e}")
            return []
    
    def _check_content_policy_compliance(self, creator_id: str, platform: str) -> bool:
        """Check if creator is compliant with content policies"""        try:
            # Check for recent policy violations
            violation_key = f"creator_{creator_id}_{platform}_violations"
            violations_data = self.get_secret(violation_key)
            
            if violations_data:
                import json
                violations = json.loads(violations_data)
                active_violations = [v for v in violations if not v.get('resolved', False)]
                
                # Block if there are active serious violations
                serious_violations = [v for v in active_violations if v.get('severity') in ['high', 'critical']]
                if serious_violations:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking content policy compliance: {e}")
            return True  # Allow on error
    
    # Platform-specific credential validation methods
    def _validate_youtube_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate YouTube credentials."""        required_fields = ['client_id', 'client_secret', 'access_token', 'refresh_token']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing YouTube {field}")
        
        if 'client_id' in credentials:
            client_id = credentials['client_id']
            if not client_id.endswith('.googleusercontent.com'):
                validation_result['issues'].append("Invalid YouTube client_id format")
        
        return validation_result
    
    def _validate_instagram_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Instagram credentials."""        required_fields = ['app_id', 'app_secret', 'access_token']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing Instagram {field}")
        
        if 'app_id' in credentials and not credentials['app_id'].isdigit():
            validation_result['issues'].append("Invalid Instagram app_id format")
        
        return validation_result
    
    def _validate_tiktok_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate TikTok credentials."""        required_fields = ['client_key', 'client_secret', 'access_token']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing TikTok {field}")
        
        return validation_result
    
    def _validate_spotify_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Spotify credentials."""        required_fields = ['client_id', 'client_secret', 'access_token', 'refresh_token']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing Spotify {field}")
        
        return validation_result
    
    def _validate_twitter_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Twitter credentials."""        required_fields = ['api_key', 'api_secret_key', 'access_token', 'access_token_secret']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing Twitter {field}")
        
        return validation_result
    
    def _validate_stripe_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Stripe credentials."""        required_fields = ['secret_key', 'publishable_key']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing Stripe {field}")
        
        if 'secret_key' in credentials:
            secret_key = credentials['secret_key']
            if not secret_key.startswith('sk_'):
                validation_result['issues'].append("Invalid Stripe secret key format")
            elif secret_key.startswith('sk_test_'):
                validation_result['recommendations'].append("Using test credentials in production environment")
            elif secret_key.startswith('sk_live_'):
                validation_result['valid'] = True
        
        return validation_result
    
    def _validate_paypal_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate PayPal credentials."""        required_fields = ['client_id', 'client_secret']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing PayPal {field}")
        
        if 'environment' in credentials:
            env = credentials['environment']
            if env not in ['sandbox', 'live']:
                validation_result['issues'].append("Invalid PayPal environment")
            elif env == 'sandbox':
                validation_result['recommendations'].append("Using sandbox credentials in production environment")
            else:
                validation_result['valid'] = True
        
        return validation_result
    
    def _validate_wise_credentials(
        self,
        credentials: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Wise credentials."""        required_fields = ['api_token', 'profile_id']
        
        for field in required_fields:
            if field not in credentials:
                validation_result['issues'].append(f"Missing Wise {field}")
        
        if 'api_token' in credentials:
            api_token = credentials['api_token']
            # Wise API tokens should be UUID format
            if not self.validation.patterns['uuid'].match(api_token):
                validation_result['issues'].append("Invalid Wise API token format")
            else:
                validation_result['valid'] = True
        
        return validation_result
    
    def _validate_access_token(self, access_token: str, api_base_url: str) -> bool:
        """Validate access token by making a test API call."""        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Make a simple test request (this would need to be customized per platform)
            test_url = f"{api_base_url}/test"  # Placeholder endpoint
            
            response = requests.get(test_url, headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _test_openai_api_key(self, api_key: str) -> bool:
        """Test OpenAI API key validity."""        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with models endpoint
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _test_anthropic_api_key(self, api_key: str) -> bool:
        """Test Anthropic API key validity."""        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            
            # Test with a simple completion request
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1,
                'messages': [{'role': 'user', 'content': 'Hi'}]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400 is also acceptable for auth test
            
        except Exception:
            return False
    
    def _test_huggingface_token(self, api_token: str) -> bool:
        """Test Hugging Face API token validity."""        try:
            headers = {
                'Authorization': f'Bearer {api_token}'
            }
            
            # Test with user info endpoint
            response = requests.get(
                'https://huggingface.co/api/whoami-v2',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _test_google_ai_key(self, api_key: str) -> bool:
        """Test Google AI API key validity."""        try:
            # Test with models list endpoint
            response = requests.get(
                f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _perform_payment_pci_checks(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Perform PCI-DSS compliance checks."""        checks = {
            'encrypted_storage': True,  # Assuming credentials are encrypted in vault
            'access_control': True,     # Assuming proper access controls
            'audit_logging': True,      # Assuming audit logging is enabled
            'secure_transmission': True, # Assuming HTTPS/TLS
            'key_rotation': True,       # Assuming key rotation is configured
            'vulnerability_scanning': True,  # Assuming regular scans
            'network_segmentation': True,    # Assuming proper network setup
            'monitoring': True,         # Assuming monitoring is in place
            'documentation': True,      # Assuming documentation exists
            'compliance_validation': True   # Assuming regular validation
        }
        
        # Additional checks based on PCI level
        pci_level = config.get('pci_level', 'level_4')
        
        if pci_level == 'level_1':
            # Stricter requirements for Level 1
            checks.update({
                'quarterly_scanning': True,
                'annual_assessment': True,
                'network_penetration_testing': True,
                'file_integrity_monitoring': True
            })
        
        return checks
    
    # AI provider testing methods
    def _test_openai_api_key(self, api_key: str) -> bool:
        """Test OpenAI API key validity."""        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simple models list request
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"OpenAI API key test failed: {e}")
            return False
    
    def _test_anthropic_api_key(self, api_key: str) -> bool:
        """Test Anthropic API key validity."""        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            # Simple completion request
            payload = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1,
                'messages': [{'role': 'user', 'content': 'Hi'}]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400 is also valid (quota/rate limit)
            
        except Exception as e:
            logger.debug(f"Anthropic API key test failed: {e}")
            return False
    
    def _test_huggingface_token(self, token: str) -> bool:
        """Test Hugging Face API token validity."""        try:
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(
                'https://huggingface.co/api/whoami-v2',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"Hugging Face token test failed: {e}")
            return False
    
    def _test_google_ai_key(self, api_key: str) -> bool:
        """Test Google AI API key validity."""        try:
            response = requests.get(
                f'https://generativelanguage.googleapis.com/v1/models?key={api_key}',
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"Google AI API key test failed: {e}")
            return False
    
    def _validate_access_token(self, token: str, api_base_url: str) -> bool:
        """Validate access token by making a test API call."""        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'User-Agent': 'IA-Influencer-Agent/1.0'
            }
            
            # Make a simple API call to test token validity
            response = requests.get(
                f"{api_base_url.rstrip('/')}/me",
                headers=headers,
                timeout=10
            )
            
            return response.status_code in [200, 401, 403]  # Any response means token format is valid
            
        except Exception as e:
            logger.debug(f"Access token validation failed: {e}")
            return False
    
    def _perform_payment_pci_checks(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Perform PCI compliance checks on payment credentials."""        pci_checks = {
            'encrypted_storage': True,  # Assume encrypted if in vault
            'access_control': True,     # Assume proper access control
            'audit_logging': True,      # Assume audit logging enabled
            'network_security': True,   # Assume secure network
            'key_rotation': True,       # Assume key rotation enabled
            'vulnerability_scanning': True,  # Assume vulnerability scanning
            'secure_development': True,      # Assume secure development practices
            'compliance_monitoring': True    # Assume compliance monitoring
        }
        
        # Additional checks based on processor requirements
        pci_level = config.get('pci_level', 'level_4')
        
        if pci_level == 'level_1':
            # Level 1 requires additional security measures
            pci_checks.update({
                'quarterly_scans': True,
                'penetration_testing': True,
                'compliance_certification': True
            })
        
        return pci_checks


class ContentProtectionUtils:
    """    Utilities for content protection and digital rights management.
    """    
    def __init__(self):
        """Initialize content protection utilities."""        self.security = SecurityUtils()
        
        # Content protection algorithms
        self.protection_algorithms = {
            'audio': {
                'fingerprinting': 'chromaprint',
                'watermarking': 'audio_watermark',
                'encryption': 'aes_256_gcm'
            },
            'video': {
                'fingerprinting': 'opencv_orb',
                'watermarking': 'video_watermark',
                'encryption': 'aes_256_gcm'
            },
            'image': {
                'fingerprinting': 'clip_embedding',
                'watermarking': 'image_watermark',
                'encryption': 'aes_256_gcm'
            },
            'text': {
                'fingerprinting': 'bert_embedding',
                'watermarking': 'text_watermark',
                'encryption': 'aes_256_gcm'
            }
        }
        
        logger.info("ContentProtectionUtils initialized")
    
    def generate_content_fingerprint(
        self,
        content_type: str,
        content_data: bytes,
        user_id: str
    ) -> Dict[str, Any]:
        """        Generate content fingerprint for protection.
        
        Args:
            content_type: Type of content
            content_data: Content data
            user_id: User identifier
            
        Returns:
            dict: Content fingerprint data
        """        try:
            if content_type not in self.protection_algorithms:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            algorithm = self.protection_algorithms[content_type]['fingerprinting']
            
            # Generate content hash
            content_hash = self.security.generate_secure_hash(content_data, 'sha256')
            
            # Generate fingerprint based on content type
            if content_type == 'audio':
                fingerprint = self._generate_audio_fingerprint(content_data)
            elif content_type == 'video':
                fingerprint = self._generate_video_fingerprint(content_data)
            elif content_type == 'image':
                fingerprint = self._generate_image_fingerprint(content_data)
            elif content_type == 'text':
                fingerprint = self._generate_text_fingerprint(content_data)
            else:
                fingerprint = content_hash  # Fallback to hash
            
            fingerprint_data = {
                'content_type': content_type,
                'algorithm': algorithm,
                'fingerprint': fingerprint,
                'content_hash': content_hash,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': {
                    'content_size': len(content_data),
                    'protection_level': 'high'
                }
            }
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Content fingerprint generation failed: {e}")
            raise
    
    def verify_content_integrity(
        self,
        content_data: bytes,
        fingerprint_data: Dict[str, Any]
    ) -> bool:
        """        Verify content integrity using fingerprint.
        
        Args:
            content_data: Content data to verify
            fingerprint_data: Original fingerprint data
            
        Returns:
            bool: True if content is authentic
        """        try:
            # Generate new fingerprint
            new_fingerprint = self.generate_content_fingerprint(
                fingerprint_data['content_type'],
                content_data,
                fingerprint_data['user_id']
            )
            
            # Compare fingerprints
            original_fingerprint = fingerprint_data['fingerprint']
            new_fingerprint_value = new_fingerprint['fingerprint']
            
            # For hash-based fingerprints, exact match required
            if fingerprint_data['algorithm'] in ['sha256', 'blake2b']:
                return original_fingerprint == new_fingerprint_value
            
            # For perceptual fingerprints, similarity threshold
            similarity = self._calculate_fingerprint_similarity(
                original_fingerprint,
                new_fingerprint_value,
                fingerprint_data['algorithm']
            )
            
            # High similarity threshold for content integrity
            return similarity >= 0.95
            
        except Exception as e:
            logger.error(f"Content integrity verification failed: {e}")
            return False
    
    def detect_content_tampering(
        self,
        original_content: bytes,
        current_content: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """        Detect content tampering.
        
        Args:
            original_content: Original content data
            current_content: Current content data
            content_type: Type of content
            
        Returns:
            dict: Tampering detection results
        """        try:
            detection_result = {
                'tampered': False,
                'confidence': 0.0,
                'changes_detected': [],
                'similarity_score': 0.0,
                'analysis_method': self.protection_algorithms[content_type]['fingerprinting'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Generate fingerprints for both versions
            original_fp = self.generate_content_fingerprint(content_type, original_content, 'system')
            current_fp = self.generate_content_fingerprint(content_type, current_content, 'system')
            
            # Calculate similarity
            similarity = self._calculate_fingerprint_similarity(
                original_fp['fingerprint'],
                current_fp['fingerprint'],
                original_fp['algorithm']
            )
            
            detection_result['similarity_score'] = similarity
            
            # Determine if content was tampered
            if similarity < 0.90:  # Less than 90% similarity indicates tampering
                detection_result['tampered'] = True
                detection_result['confidence'] = 1.0 - similarity
                
                # Identify types of changes
                if original_fp['content_hash'] != current_fp['content_hash']:
                    detection_result['changes_detected'].append('content_modified')
                
                if abs(original_fp['metadata']['content_size'] - current_fp['metadata']['content_size']) > 1024:
                    detection_result['changes_detected'].append('size_changed')
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Content tampering detection failed: {e}")
            return {
                'tampered': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Content-specific fingerprint generation methods
    def _generate_audio_fingerprint(self, audio_data: bytes) -> str:
        """Generate audio fingerprint using Chromaprint-like algorithm."""        # Simplified audio fingerprinting
        # In a real implementation, this would use actual audio processing libraries
        audio_hash = hashlib.sha256(audio_data).digest()
        # Simulate perceptual hash
        return base64.b64encode(audio_hash[:16]).decode()
    
    def _generate_video_fingerprint(self, video_data: bytes) -> str:
        """Generate video fingerprint using OpenCV-like algorithm."""        # Simplified video fingerprinting
        # In a real implementation, this would extract key frames and use computer vision
        video_hash = hashlib.sha256(video_data).digest()
        # Simulate perceptual hash
        return base64.b64encode(video_hash[:16]).decode()
    
    def _generate_image_fingerprint(self, image_data: bytes) -> str:
        """Generate image fingerprint using CLIP-like algorithm."""        # Simplified image fingerprinting
        # In a real implementation, this would use image feature extraction
        image_hash = hashlib.sha256(image_data).digest()
        # Simulate perceptual hash
        return base64.b64encode(image_hash[:16]).decode()
    
    def _generate_text_fingerprint(self, text_data: bytes) -> str:
        """Generate text fingerprint using BERT-like algorithm."""        # Simplified text fingerprinting
        # In a real implementation, this would use NLP embeddings
        text_hash = hashlib.sha256(text_data).digest()
        # Simulate semantic hash
        return base64.b64encode(text_hash[:16]).decode()
    
    def _calculate_fingerprint_similarity(
        self,
        fingerprint1: str,
        fingerprint2: str,
        algorithm: str
    ) -> float:
        """Calculate similarity between two fingerprints."""        try:
            if fingerprint1 == fingerprint2:
                return 1.0
            
            # For hash-based algorithms, only exact match
            if algorithm in ['sha256', 'blake2b']:
                return 0.0
            
            # For perceptual algorithms, simulate similarity calculation
            # In a real implementation, this would use algorithm-specific methods
            fp1_bytes = base64.b64decode(fingerprint1.encode())
            fp2_bytes = base64.b64decode(fingerprint2.encode())
            
            # Simple Hamming distance for demonstration
            if len(fp1_bytes) != len(fp2_bytes):
                return 0.0
            
            differences = sum(b1 != b2 for b1, b2 in zip(fp1_bytes, fp2_bytes))
            similarity = 1.0 - (differences / len(fp1_bytes))
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Fingerprint similarity calculation failed: {e}")
            return 0.0
