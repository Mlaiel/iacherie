"""
TLS 1.3 Configuration Module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced TLS 1.3 configuration for secure data transmission.
"""

import os
import ssl
import uvicorn
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TLS13Config:
    """
    TLS 1.3 configuration for secure data transmission.
    Implements modern cryptographic standards for maximum security.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cert_path = self.config.get('cert_path', './certs')
        self.ensure_cert_directory()
    
    def ensure_cert_directory(self):
        """Ensure certificate directory exists."""
        Path(self.cert_path).mkdir(parents=True, exist_ok=True)
    
    def generate_self_signed_cert(self, 
                                  hostname: str = "localhost",
                                  days_valid: int = 365) -> tuple[str, str]:
        """
        Generate self-signed certificate for development/testing.
        
        Args:
            hostname: Hostname for certificate
            days_valid: Number of days certificate is valid
            
        Returns:
            Tuple of (cert_file_path, key_file_path)
        """
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ainflue Platform"),
                x509.NameAttribute(NameOID.COMMON_NAME, hostname),
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
                datetime.utcnow() + timedelta(days=days_valid)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(hostname),
                    x509.DNSName("localhost"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write certificate and key files
            cert_file = os.path.join(self.cert_path, "server.crt")
            key_file = os.path.join(self.cert_path, "server.key")
            
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"Generated self-signed certificate: {cert_file}")
            return cert_file, key_file
            
        except Exception as e:
            logger.error(f"Failed to generate self-signed certificate: {str(e)}")
            raise
    
    def get_ssl_context(self, 
                       cert_file: Optional[str] = None,
                       key_file: Optional[str] = None) -> ssl.SSLContext:
        """
        Create SSL context with TLS 1.3 configuration.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            
        Returns:
            Configured SSL context
        """
        try:
            # Create SSL context with TLS 1.3
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            
            # Set minimum TLS version to 1.3
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            # Configure cipher suites for TLS 1.3
            # TLS 1.3 has predefined cipher suites
            context.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256')
            
            # Security options
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_NO_TLSv1_2  # Force TLS 1.3 only
            context.options |= ssl.OP_SINGLE_DH_USE
            context.options |= ssl.OP_SINGLE_ECDH_USE
            context.options |= ssl.OP_NO_COMPRESSION
            
            # Load certificate and key
            if cert_file and key_file:
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    context.load_cert_chain(cert_file, key_file)
                else:
                    logger.warning("Certificate files not found, generating self-signed certificate")
                    cert_file, key_file = self.generate_self_signed_cert()
                    context.load_cert_chain(cert_file, key_file)
            else:
                # Generate self-signed certificate if none provided
                cert_file, key_file = self.generate_self_signed_cert()
                context.load_cert_chain(cert_file, key_file)
            
            # Set verification mode
            context.check_hostname = False  # Disabled for self-signed certs
            context.verify_mode = ssl.CERT_NONE
            
            logger.info("SSL context configured for TLS 1.3")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context: {str(e)}")
            raise
    
    def get_uvicorn_ssl_config(self, 
                              cert_file: Optional[str] = None,
                              key_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Get SSL configuration for uvicorn server.
        
        Args:
            cert_file: Path to certificate file
            key_file: Path to private key file
            
        Returns:
            Dictionary with SSL configuration for uvicorn
        """
        try:
            # Use provided certificates or generate/find defaults
            if not cert_file or not key_file:
                default_cert = os.path.join(self.cert_path, "server.crt")
                default_key = os.path.join(self.cert_path, "server.key")
                
                if os.path.exists(default_cert) and os.path.exists(default_key):
                    cert_file = default_cert
                    key_file = default_key
                else:
                    cert_file, key_file = self.generate_self_signed_cert()
            
            ssl_config = {
                "ssl_certfile": cert_file,
                "ssl_keyfile": key_file,
                "ssl_version": ssl.PROTOCOL_TLS_SERVER,
                "ssl_cert_reqs": ssl.CERT_NONE,
                "ssl_ca_certs": None,
                "ssl_ciphers": "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"
            }
            
            logger.info(f"Uvicorn SSL config: cert={cert_file}, key={key_file}")
            return ssl_config
            
        except Exception as e:
            logger.error(f"Failed to create uvicorn SSL config: {str(e)}")
            raise


class SecureHeaders:
    """
    Security headers configuration for HTTPS responses.
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get security headers for HTTP responses.
        
        Returns:
            Dictionary of security headers
        """
        return {
            # HTTPS and TLS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content security
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' wss: https:; "
                "media-src 'self' https:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            ),
            
            # XSS protection
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
            
            # Cache control for sensitive content
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            
            # Server information hiding
            "Server": "Ainflue-Platform"
        }


class HTTPSRedirect:
    """
    HTTPS redirect configuration for forcing secure connections.
    """
    
    def __init__(self, enabled: bool = True, permanent: bool = True):
        self.enabled = enabled
        self.permanent = permanent
    
    def should_redirect(self, request_scheme: str, request_host: str) -> bool:
        """
        Check if request should be redirected to HTTPS.
        
        Args:
            request_scheme: Request scheme (http/https)
            request_host: Request host
            
        Returns:
            True if should redirect to HTTPS
        """
        if not self.enabled:
            return False
        
        # Don't redirect localhost in development
        if request_host.startswith("localhost") or request_host.startswith("127.0.0.1"):
            return False
        
        return request_scheme == "http"
    
    def get_redirect_url(self, request_url: str) -> str:
        """
        Get HTTPS redirect URL.
        
        Args:
            request_url: Original HTTP URL
            
        Returns:
            HTTPS URL
        """
        return request_url.replace("http://", "https://", 1)


# Global configuration instances
tls13_config = TLS13Config()
secure_headers = SecureHeaders()
https_redirect = HTTPSRedirect()


def get_tls13_config() -> TLS13Config:
    """Get TLS 1.3 configuration instance."""
    return tls13_config


def get_secure_headers() -> SecureHeaders:
    """Get secure headers configuration."""
    return secure_headers


def get_https_redirect() -> HTTPSRedirect:
    """Get HTTPS redirect configuration."""
    return https_redirect


def configure_secure_server(app, host: str = "0.0.0.0", port: int = 8000, 
                          cert_file: Optional[str] = None,
                          key_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Configure uvicorn server with TLS 1.3 and security features.
    
    Args:
        app: FastAPI application instance
        host: Server host
        port: Server port
        cert_file: Path to certificate file
        key_file: Path to private key file
        
    Returns:
        Server configuration dictionary
    """
    try:
        # Get SSL configuration
        ssl_config = tls13_config.get_uvicorn_ssl_config(cert_file, key_file)
        
        # Configure server
        server_config = {
            "app": app,
            "host": host,
            "port": port,
            "log_level": "info",
            "access_log": True,
            "server_header": False,  # Hide server version
            "date_header": False,    # Hide date header
            **ssl_config
        }
        
        logger.info(f"Configured secure server on {host}:{port} with TLS 1.3")
        return server_config
        
    except Exception as e:
        logger.error(f"Failed to configure secure server: {str(e)}")
        raise