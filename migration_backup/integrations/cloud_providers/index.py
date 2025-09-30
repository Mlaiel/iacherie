"""
Cloud Providers Module - Ainflue Integrations
============================================
Enterprise-grade cloud provider integrations providing multi-cloud
infrastructure management, storage solutions, compute orchestration,
and monitoring across major cloud platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all cloud provider components
from .aws_integration import *
from .azure_integration import *
from .gcp_integration import *
from .cloudflare_integration import *
from .digitalocean_integration import *
from .firebase_integration import *
from .heroku_integration import *
from .netlify_integration import *
from .supabase_integration import *
from .vercel_integration import *
from .cloud_compute_manager import *
from .cloud_database_manager import *
from .cloud_monitoring import *
from .cloud_storage_manager import *

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise cloud infrastructure management for multi-platform content distribution"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'cloud_providers': 14,
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}