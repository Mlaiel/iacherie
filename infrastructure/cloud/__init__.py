"""
Cloud Providers Infrastructure Orchestration Module
© 2025 Fahed Mlaiel. All rights reserved.

Multi-cloud provider management and orchestration for Ainflue infrastructure.
Handles AWS, GCP, and Azure integration with intelligent workload distribution.
"""

# Core cloud functionality (from moved files)
try:
    from .cost_management import (
        CostManager, BudgetManager, CostOptimizer, BillingAnalyzer,
        cost_manager, budget_manager, cost_optimizer, billing_analyzer
    )
except ImportError:
    CostManager = BudgetManager = CostOptimizer = BillingAnalyzer = None
    cost_manager = budget_manager = cost_optimizer = billing_analyzer = None

try:
    from .multi_cloud_manager import (
        MultiCloudManager, CloudOrchestrator, WorkloadDistributor, CloudSynchronizer,
        multi_cloud_manager, cloud_orchestrator, workload_distributor, cloud_synchronizer
    )
except ImportError:
    MultiCloudManager = CloudOrchestrator = WorkloadDistributor = CloudSynchronizer = None
    multi_cloud_manager = cloud_orchestrator = workload_distributor = cloud_synchronizer = None

# Cloud provider modules
try:
    from .aws_provider import AWSProvider
except ImportError:
    AWSProvider = None

try:
    from .gcp_provider import GCPProvider
except ImportError:
    GCPProvider = None

try:
    from .azure_provider import AzureProvider
except ImportError:
    AzureProvider = None

try:
    from .multi_cloud_orchestrator import MultiCloudOrchestrator
except ImportError:
    MultiCloudOrchestrator = None

# Other cloud modules
try:
    from .hybrid_cloud_manager import HybridCloudManager
except ImportError:
    HybridCloudManager = None

try:
    from .cloud_cost_optimizer import CloudCostOptimizer
except ImportError:
    CloudCostOptimizer = None

try:
    from .cloud_security_manager import CloudSecurityManager
except ImportError:
    CloudSecurityManager = None

try:
    from .cloud_migration_tool import CloudMigrationTool
except ImportError:
    CloudMigrationTool = None

try:
    from .resource_provisioner import ResourceProvisioner
except ImportError:
    ResourceProvisioner = None

__all__ = [
    # Core cloud functionality
    'CostManager', 'BudgetManager', 'CostOptimizer', 'BillingAnalyzer',
    'MultiCloudManager', 'CloudOrchestrator', 'WorkloadDistributor', 'CloudSynchronizer',
    # Cloud providers
    'AWSProvider', 'GCPProvider', 'AzureProvider', 'MultiCloudOrchestrator',
    # Advanced cloud modules
    'HybridCloudManager', 'CloudCostOptimizer', 'CloudSecurityManager',
    'CloudMigrationTool', 'ResourceProvisioner'
]

# Cloud provider capabilities
PROVIDER_CAPABILITIES = {
    'aws': {
        'compute': ['EC2', 'ECS', 'EKS', 'Fargate', 'Lambda'],
        'storage': ['S3', 'EBS', 'EFS', 'FSx'],
        'database': ['RDS', 'DynamoDB', 'ElastiCache', 'Aurora'],
        'ai_ml': ['SageMaker', 'Bedrock', 'Comprehend', 'Rekognition'],
        'networking': ['VPC', 'ALB', 'NLB', 'CloudFront', 'Route53'],
        'security': ['IAM', 'KMS', 'Secrets Manager', 'WAF'],
        'monitoring': ['CloudWatch', 'X-Ray', 'CloudTrail']
    },
    'gcp': {
        'compute': ['Compute Engine', 'GKE', 'Cloud Run', 'Cloud Functions'],
        'storage': ['Cloud Storage', 'Persistent Disk', 'Filestore'],
        'database': ['Cloud SQL', 'Firestore', 'Bigtable', 'Spanner'],
        'ai_ml': ['Vertex AI', 'AutoML', 'Vision API', 'Natural Language API'],
        'networking': ['VPC', 'Load Balancer', 'Cloud CDN', 'Cloud DNS'],
        'security': ['IAM', 'KMS', 'Secret Manager', 'Cloud Armor'],
        'monitoring': ['Cloud Monitoring', 'Cloud Trace', 'Cloud Logging']
    },
    'azure': {
        'compute': ['Virtual Machines', 'AKS', 'Container Instances', 'Functions'],
        'storage': ['Blob Storage', 'Disk Storage', 'Files'],
        'database': ['SQL Database', 'Cosmos DB', 'Cache for Redis'],
        'ai_ml': ['Machine Learning', 'Cognitive Services', 'Bot Service'],
        'networking': ['Virtual Network', 'Load Balancer', 'CDN', 'DNS'],
        'security': ['Active Directory', 'Key Vault', 'Security Center'],
        'monitoring': ['Monitor', 'Application Insights', 'Log Analytics']
    }
}

# Ainflue-specific cloud service mappings
AINFLUE_SERVICE_MAPPINGS = {
    'creator_services': {
        'primary_provider': 'aws',
        'services': ['EC2', 'RDS', 'S3', 'CloudFront'],
        'regions': ['us-west-2', 'us-east-1', 'eu-west-1']
    },
    'ai_processing': {
        'primary_provider': 'gcp',
        'services': ['Vertex AI', 'GKE', 'Cloud Storage'],
        'regions': ['us-central1', 'europe-west1']
    },
    'content_storage': {
        'primary_provider': 'aws',
        'services': ['S3', 'CloudFront', 'EBS'],
        'regions': ['us-west-2', 'us-east-1', 'eu-west-1', 'ap-southeast-1']
    },
    'revenue_processing': {
        'primary_provider': 'aws',
        'services': ['RDS', 'ElastiCache', 'Lambda'],
        'regions': ['us-east-1', 'us-west-2']
    },
    'collaboration_platform': {
        'primary_provider': 'azure',
        'services': ['AKS', 'Cosmos DB', 'CDN'],
        'regions': ['eastus', 'westus2', 'westeurope']
    },
    'analytics_engine': {
        'primary_provider': 'gcp',
        'services': ['BigQuery', 'Dataflow', 'Cloud Storage'],
        'regions': ['us-central1', 'europe-west1']
    },
    'security_operations': {
        'primary_provider': 'aws',
        'services': ['WAF', 'GuardDuty', 'Security Hub'],
        'regions': ['us-west-2', 'us-east-1', 'eu-west-1']
    }
}

# Default cloud configurations for Ainflue
DEFAULT_CLOUD_CONFIGS = {
    'aws': {
        'default_region': 'us-west-2',
        'backup_regions': ['us-east-1', 'eu-west-1'],
        'instance_types': {
            'micro': 't3.micro',
            'small': 't3.small', 
            'medium': 't3.medium',
            'large': 't3.large',
            'gpu': 'p3.2xlarge'
        },
        'storage_classes': {
            'hot': 'STANDARD',
            'warm': 'STANDARD_IA',
            'cold': 'GLACIER',
            'archive': 'DEEP_ARCHIVE'
        }
    },
    'gcp': {
        'default_region': 'us-central1',
        'backup_regions': ['us-east1', 'europe-west1'],
        'machine_types': {
            'micro': 'e2-micro',
            'small': 'e2-small',
            'medium': 'e2-medium', 
            'large': 'e2-standard-4',
            'gpu': 'n1-standard-4'
        },
        'storage_classes': {
            'hot': 'STANDARD',
            'warm': 'NEARLINE',
            'cold': 'COLDLINE',
            'archive': 'ARCHIVE'
        }
    },
    'azure': {
        'default_region': 'eastus',
        'backup_regions': ['westus2', 'westeurope'],
        'vm_sizes': {
            'micro': 'Standard_B1s',
            'small': 'Standard_B2s',
            'medium': 'Standard_B4ms',
            'large': 'Standard_D4s_v3',
            'gpu': 'Standard_NC6'
        },
        'storage_tiers': {
            'hot': 'Hot',
            'warm': 'Cool',
            'cold': 'Archive'
        }
    }
}

def get_optimal_provider_for_service(service_name: str) -> str:
    """Get optimal cloud provider for an Ainflue service"""
    mapping = AINFLUE_SERVICE_MAPPINGS.get(service_name)
    if mapping:
        return mapping['primary_provider']
    return 'aws'  # Default to AWS

def get_provider_capabilities(provider: str) -> dict:
    """Get capabilities for a specific cloud provider"""
    return PROVIDER_CAPABILITIES.get(provider, {})

def get_default_config(provider: str) -> dict:
    """Get default configuration for a cloud provider"""
    return DEFAULT_CLOUD_CONFIGS.get(provider, {})

def list_supported_regions(provider: str) -> list:
    """List supported regions for a cloud provider"""
    configs = get_default_config(provider)
    regions = [configs.get('default_region')]
    regions.extend(configs.get('backup_regions', []))
    return [r for r in regions if r]  # Filter out None values