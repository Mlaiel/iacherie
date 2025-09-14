"""Cloud Providers Integration Module
===================================

Enterprise cloud infrastructure integrations for Ainflue platform.
Supports 14+ cloud providers for scalable multi-cloud content delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import all cloud provider integrations
try:
    from .aws_integration import AWSIntegration
except ImportError:
    AWSIntegration = None

try:
    from .azure_integration import AzureIntegration
except ImportError:
    AzureIntegration = None

try:
    from .gcp_integration import GCPIntegration
except ImportError:
    GCPIntegration = None

try:
    from .cloudflare_integration import CloudflareIntegration
except ImportError:
    CloudflareIntegration = None

try:
    from .digitalocean_integration import DigitalOceanIntegration
except ImportError:
    DigitalOceanIntegration = None

try:
    from .firebase_integration import FirebaseIntegration
except ImportError:
    FirebaseIntegration = None

try:
    from .heroku_integration import HerokuIntegration
except ImportError:
    HerokuIntegration = None

try:
    from .netlify_integration import NetlifyIntegration
except ImportError:
    NetlifyIntegration = None

try:
    from .supabase_integration import SupabaseIntegration
except ImportError:
    SupabaseIntegration = None

try:
    from .vercel_integration import VercelIntegration
except ImportError:
    VercelIntegration = None

# Import cloud management services
try:
    from .cloud_compute_manager import CloudComputeManager
except ImportError:
    CloudComputeManager = None

try:
    from .cloud_database_manager import CloudDatabaseManager
except ImportError:
    CloudDatabaseManager = None

try:
    from .cloud_monitoring import CloudMonitoring
except ImportError:
    CloudMonitoring = None

try:
    from .cloud_storage_manager import CloudStorageManager
except ImportError:
    CloudStorageManager = None

__all__ = [
    'AWSIntegration',
    'AzureIntegration', 
    'GCPIntegration',
    'CloudflareIntegration',
    'DigitalOceanIntegration',
    'FirebaseIntegration',
    'HerokuIntegration',
    'NetlifyIntegration',
    'SupabaseIntegration',
    'VercelIntegration',
    'CloudComputeManager',
    'CloudDatabaseManager',
    'CloudMonitoring',
    'CloudStorageManager'
]

# Cloud provider registry for dynamic loading
CLOUD_PROVIDERS = {}

if AWSIntegration:
    CLOUD_PROVIDERS['aws'] = AWSIntegration
if AzureIntegration:
    CLOUD_PROVIDERS['azure'] = AzureIntegration
if GCPIntegration:
    CLOUD_PROVIDERS['gcp'] = GCPIntegration
if CloudflareIntegration:
    CLOUD_PROVIDERS['cloudflare'] = CloudflareIntegration
if DigitalOceanIntegration:
    CLOUD_PROVIDERS['digitalocean'] = DigitalOceanIntegration
if FirebaseIntegration:
    CLOUD_PROVIDERS['firebase'] = FirebaseIntegration
if HerokuIntegration:
    CLOUD_PROVIDERS['heroku'] = HerokuIntegration
if NetlifyIntegration:
    CLOUD_PROVIDERS['netlify'] = NetlifyIntegration
if SupabaseIntegration:
    CLOUD_PROVIDERS['supabase'] = SupabaseIntegration
if VercelIntegration:
    CLOUD_PROVIDERS['vercel'] = VercelIntegration

# Configuration logique métier Ainflue
AINFLUE_CLOUD_CONFIG = {
    'total_providers': len(CLOUD_PROVIDERS),
    'ecosystems': ['AWS', 'Azure', 'GCP'],
    'specialized_platforms': ['Cloudflare', 'Vercel', 'Netlify', 'Firebase', 'Supabase'],
    'workflow': 'connect→auth→deploy→monitor→optimize'
}
