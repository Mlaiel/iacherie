"""Cloud Providers Integration Module
===================================

Enterprise cloud infrastructure integrations for Ainflue platform.
Supports multiple cloud providers for scalable content delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .aws_integration import AWSIntegration

try:
    from .gcp_integration import GCPIntegration
except ImportError:
    GCPIntegration = None

try:
    from .azure_integration import AzureIntegration
except ImportError:
    AzureIntegration = None

try:
    from .digitalocean_integration import DigitalOceanIntegration
except ImportError:
    DigitalOceanIntegration = None

try:
    from .cloudflare_integration import CloudflareIntegration
except ImportError:
    CloudflareIntegration = None

try:
    from .vercel_integration import VercelIntegration
except ImportError:
    VercelIntegration = None

try:
    from .firebase_integration import FirebaseIntegration
except ImportError:
    FirebaseIntegration = None

try:
    from .cloud_storage_manager import CloudStorageManager
except ImportError:
    CloudStorageManager = None

__all__ = [
    'AWSIntegration',
    'GCPIntegration',
    'AzureIntegration',
    'DigitalOceanIntegration',
    'CloudflareIntegration',
    'VercelIntegration',
    'FirebaseIntegration',
    'CloudStorageManager'
]

# Cloud provider registry
CLOUD_PROVIDERS = {
    'aws': AWSIntegration,
}

if GCPIntegration:
    CLOUD_PROVIDERS['gcp'] = GCPIntegration
if AzureIntegration:
    CLOUD_PROVIDERS['azure'] = AzureIntegration
if DigitalOceanIntegration:
    CLOUD_PROVIDERS['digitalocean'] = DigitalOceanIntegration
if CloudflareIntegration:
    CLOUD_PROVIDERS['cloudflare'] = CloudflareIntegration
if VercelIntegration:
    CLOUD_PROVIDERS['vercel'] = VercelIntegration
if FirebaseIntegration:
    CLOUD_PROVIDERS['firebase'] = FirebaseIntegration
