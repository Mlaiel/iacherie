"""IA Influencer Agent - SSL/TLS Deployment Module
Enterprise SSL/TLS certificate management and deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Expertise:
- Lead Dev IA + Backend Senior + ML Engineer
- DBA + Security Expert + Microservices Architect
- Audio Processing + DevOps + Prompt Engineering

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized copying, distribution, or use without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Core SSL/TLS management components
from .cert_manager import CertificateManager, create_certificate_manager
from .letsencrypt_manager import (
    LetsEncryptManager, 
    LetsEncryptConfig, 
    CertificateRequest, 
    ChallengeType,
    create_letsencrypt_manager
)
from .tls_config import (
    TLSConfigManager, 
    TLSConfig, 
    TLSVersion, 
    SecurityLevel, 
    CipherSuite,
    NginxTLSConfig,
    ApacheTLSConfig,
    create_tls_config_manager
)
from .cert_monitor import (
    CertificateMonitor, 
    CertificateEndpoint, 
    AlertConfig,
    MonitoringStatus,
    AlertLevel,
    create_certificate_monitor
)
from .ssl_utils import (
    SSLValidator,
    SSLScanner,
    CertificateConverter,
    SSLTestServer,
    OpenSSLWrapper,
    create_ssl_scanner,
    validate_ssl_configuration
)

__all__ = [
    # Core managers
    "CertificateManager",
    "LetsEncryptManager", 
    "TLSConfigManager",
    "CertificateMonitor",
    
    # Factory functions
    "create_certificate_manager",
    "create_letsencrypt_manager",
    "create_tls_config_manager", 
    "create_certificate_monitor",
    "create_ssl_scanner",
    
    # Configuration classes
    "TLSConfig",
    "LetsEncryptConfig",
    "CertificateRequest",
    "CertificateEndpoint",
    "AlertConfig",
    "NginxTLSConfig",
    "ApacheTLSConfig",
    
    # Enums
    "TLSVersion",
    "SecurityLevel",
    "CipherSuite", 
    "ChallengeType",
    "MonitoringStatus",
    "AlertLevel",
    
    # Utilities
    "SSLValidator",
    "SSLScanner",
    "CertificateConverter",
    "SSLTestServer", 
    "OpenSSLWrapper",
    "validate_ssl_configuration"
]

# Module metadata
__title__ = "IA Influencer Agent SSL/TLS Module"
__description__ = "Enterprise SSL/TLS certificate management and deployment"
__url__ = "https://github.com/Mlaiel/IA-influencer"
__license__ = "Proprietary"
__copyright__ = "Copyright 2025 Fahed Mlaiel"
