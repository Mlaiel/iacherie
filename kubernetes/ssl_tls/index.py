"""IA Influencer Agent - SSL/TLS Management Index
Industrial-grade SSL/TLS certificate management system main entry point

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

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure module-level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import all SSL/TLS components
from .cert_manager import (
    CertificateManager, 
    create_certificate_manager,
    CertificateInfo,
    CertificateStatus
)
from .letsencrypt_manager import (
    LetsEncryptManager, 
    LetsEncryptConfig, 
    CertificateRequest, 
    ChallengeType,
    LetsEncryptResult
)
from .tls_config import (
    TLSConfigManager, 
    TLSConfig, 
    create_tls_config_manager,
    TLSValidationResult
)
from .cert_monitor import (
    CertificateMonitor, 
    CertificateEndpoint, 
    create_certificate_monitor,
    MonitoringStatus,
    AlertLevel
)
from .ssl_utils import (
    SSLScanner, 
    SSLValidator, 
    CertificateConverter, 
    SSLTestServer,
    SSLScanResult,
    SSLValidationResult,
    validate_ssl_configuration,
    generate_csr,
    create_self_signed_cert,
    OpenSSLWrapper
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "All rights reserved - Unauthorized use prohibited"

# Module exports
__all__ = [
    # Core managers
    'CertificateManager',
    'LetsEncryptManager', 
    'TLSConfigManager',
    'CertificateMonitor',
    
    # SSL/TLS utilities
    'SSLScanner',
    'SSLValidator', 
    'CertificateConverter',
    'SSLTestServer',
    'OpenSSLWrapper',
    
    # Configuration classes
    'TLSConfig',
    'LetsEncryptConfig',
    'CertificateRequest',
    'CertificateEndpoint',
    
    # Result classes
    'CertificateInfo',
    'CertificateStatus',
    'LetsEncryptResult',
    'TLSValidationResult',
    'MonitoringStatus',
    'SSLScanResult',
    'SSLValidationResult',
    
    # Enums
    'ChallengeType',
    'AlertLevel',
    
    # Factory functions
    'create_certificate_manager',
    'create_tls_config_manager',
    'create_certificate_monitor',
    
    # Utility functions
    'validate_ssl_configuration',
    'generate_csr',
    'create_self_signed_cert',
    
    # Main SSL manager
    'SSLTLSManager',
    
    # Version info
    '__version__',
    '__author__',
    '__copyright__'
]


class SSLTLSManager:
    """
    Industrial-grade SSL/TLS Management System
    
    This is the main entry point for all SSL/TLS operations in the IA Influencer Agent.
    It provides a unified interface to all SSL/TLS functionality including:
    - Certificate lifecycle management
    - Let's Encrypt automated certificate issuance
    - TLS configuration management
    - Real-time certificate monitoring
    - SSL security scanning and validation
    - Certificate format conversion
    - SSL testing capabilities
    
    Example:
        >>> ssl_manager = SSLTLSManager()
        >>> ssl_manager.initialize()
        >>> 
        >>> # Issue a certificate
        >>> result = ssl_manager.issue_certificate("example.com", "admin@example.com")
        >>> 
        >>> # Monitor certificates
        >>> ssl_manager.start_monitoring()
        >>> 
        >>> # Scan SSL configuration
        >>> scan_result = ssl_manager.scan_host("example.com", 443)
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
        Initialize SSL/TLS manager with configuration
        
        Args:
            config: SSL/TLS configuration dictionary
        """
        self.config = config or {}
        self.cert_manager = None
        self.letsencrypt_manager = None
        self.tls_config_manager = None
        self.monitor = None
        
        logger.info("SSL/TLS Manager initialized")
    
    def init_certificate_manager(self, cert_config: Dict[str, Any]) -> CertificateManager:
        """Initialize certificate manager"""
        self.cert_manager = create_certificate_manager(cert_config)
        return self.cert_manager
    
    def init_letsencrypt_manager(self, le_config: Dict[str, Any]) -> LetsEncryptManager:
        """
Initialize Let's Encrypt manager"""
        from .letsencrypt_manager import LetsEncryptConfig
        config_obj = LetsEncryptConfig(**le_config)
        self.letsencrypt_manager = LetsEncryptManager(config_obj)
        return self.letsencrypt_manager
    
    def init_tls_config_manager(self, config_path: Optional[Path] = None) -> TLSConfigManager:
        """
Initialize TLS configuration manager"""
        self.tls_config_manager = create_tls_config_manager(config_path)
        return self.tls_config_manager
    
    def init_monitor(self, monitor_config_path: Optional[Path] = None) -> CertificateMonitor:
        """
Initialize certificate monitor"""
        self.monitor = create_certificate_monitor(monitor_config_path)
        return self.monitor
    
    def validate_configuration(
        self, 
        cert_path: Path, 
        key_path: Path, 
        key_password: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
Validate SSL configuration"""
        return validate_ssl_configuration(cert_path, key_path, key_password)
    
    def get_status(self) -> Dict[str, Any]:
        """
Get overall SSL/TLS management status"""
        return {
            'certificate_manager': self.cert_manager is not None,
            'letsencrypt_manager': self.letsencrypt_manager is not None,
            'tls_config_manager': self.tls_config_manager is not None,
            'monitor': self.monitor is not None,
            'config': self.config
        }


def create_ssl_manager(config: Optional[Dict[str, Any]] = None) -> SSLTLSManager:
    """
    Factory function to create SSL/TLS manager
    
    Args:
        config: SSL/TLS configuration
        
    Returns:
        SSL/TLS manager instance
    """
    return SSLTLSManager(config)


def main() -> None:
    """
    Main entry point for SSL/TLS operations
    Can be called directly or via CLI
    """
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Import and run CLI
        from .cli import main as cli_main
        sys.argv = sys.argv[1:]  # Remove 'cli' argument
        cli_main()
    else:
        # Show usage information
        print("IA Influencer Agent SSL/TLS Management")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python -m ssl_tls cli <command>     # Run CLI commands")
        print("  python -m ssl_tls                   # Show this help")
        print()
        print("Available CLI commands:")
        print("  validate-cert    - Validate certificate file")
        print("  validate-config  - Validate SSL configuration")
        print("  scan            - Scan remote host SSL configuration")
        print("  generate-csr    - Generate Certificate Signing Request")
        print("  letsencrypt     - Request Let's Encrypt certificate")
        print("  monitor         - Monitor certificates")
        print("  generate-config - Generate web server configuration")
        print()
        print("Examples:")
        print("  python -m ssl_tls cli validate-cert /etc/ssl/cert.pem")
        print("  python -m ssl_tls cli scan example.com")
        print("  python -m ssl_tls cli monitor --check-now")
        print()
        print("For detailed help on any command:")
        print("  python -m ssl_tls cli <command> --help")


if __name__ == "__main__":
    main()
