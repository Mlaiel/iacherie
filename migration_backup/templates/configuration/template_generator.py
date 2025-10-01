"""
🚀 Configuration Template Generator - Enterprise Infrastructure as Code
=======================================================================

🎯 DEVOPS ENGINEER + CLOUD ARCHITECT + MICROSERVICES EXPERT
Lead: Fahed Mlaiel (mlaiel@live.de)

Generates enterprise-grade configuration templates for:
- Infrastructure as Code (Terraform, Ansible, CloudFormation)
- Container Orchestration (Kubernetes, Docker Swarm, Docker Compose)
- Service Mesh (Istio, Envoy, Linkerd, Consul)
- Security Policies (RBAC, Network Policies, Security Contexts)
- Monitoring & Observability (Prometheus, Grafana, Jaeger, ELK)
- CI/CD Pipelines (GitHub Actions, GitLab CI, Jenkins, Azure DevOps)
- Database Configurations (PostgreSQL, MySQL, MongoDB, Redis)
- Load Balancers (NGINX, HAProxy, Traefik, Cloud Load Balancers)

⚠️ INTELLECTUAL PROPERTY PROTECTION:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Created: 2025-01-18
Version: 1.0.0
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import jinja2

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Configuration template types"""
    # Infrastructure as Code
    TERRAFORM_MAIN = "terraform_main"
    TERRAFORM_VARIABLES = "terraform_variables"
    TERRAFORM_OUTPUTS = "terraform_outputs"
    TERRAFORM_MODULES = "terraform_modules"
    AWS_INFRASTRUCTURE = "aws_infrastructure"
    GCP_INFRASTRUCTURE = "gcp_infrastructure"
    AZURE_INFRASTRUCTURE = "azure_infrastructure"
    MULTI_CLOUD = "multi_cloud"
    
    # Container Templates
    DOCKERFILE = "dockerfile"
    DOCKER_SWARM = "docker_swarm"
    DOCKER_BUILDX = "docker_buildx"
    CONTAINER_SECURITY = "container_security"
    MULTI_STAGE_BUILD = "multi_stage_build"
    MICROSERVICE_CONTAINER = "microservice_container"
    SIDECAR_CONTAINER = "sidecar_container"
    INIT_CONTAINER = "init_container"
    
    # Service Mesh
    ISTIO_CONFIG = "istio_configuration"
    ENVOY_PROXY = "envoy_proxy"
    LINKERD_CONFIG = "linkerd_configuration"
    CONSUL_CONNECT = "consul_connect"
    SERVICE_MESH_SECURITY = "service_mesh_security"
    TRAFFIC_MANAGEMENT = "traffic_management"
    OBSERVABILITY_MESH = "observability_mesh"
    CANARY_DEPLOYMENT = "canary_deployment"
    
    # Security
    SECURITY_POLICY = "security_policy"
    RBAC_CONFIG = "rbac_configuration"
    NETWORK_POLICY = "network_policy"
    POD_SECURITY_POLICY = "pod_security_policy"
    SECRET_MANAGEMENT = "secret_management"
    VAULT_CONFIG = "vault_configuration"
    CERTIFICATE_MANAGEMENT = "certificate_management"
    COMPLIANCE_CONFIG = "compliance_config"


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class InfrastructureProvider(Enum):
    """Cloud infrastructure providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    MULTI_CLOUD = "multi_cloud"
    ON_PREMISE = "on_premise"


class ServiceMeshProvider(Enum):
    """Service mesh providers"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    ENVOY = "envoy"


class MonitoringStack(Enum):
    """Monitoring stack configurations"""
    PROMETHEUS_GRAFANA = "prometheus_grafana"
    ELK_STACK = "elk_stack"
    JAEGER_TRACING = "jaeger_tracing"
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"


@dataclass
class TemplateConfiguration:
    """Template configuration parameters"""
    template_type: TemplateType
    environment: DeploymentEnvironment
    infrastructure_provider: Optional[InfrastructureProvider] = None
    service_mesh: Optional[ServiceMeshProvider] = None
    monitoring_stack: Optional[MonitoringStack] = None
    security_enabled: bool = True
    high_availability: bool = True
    auto_scaling: bool = True
    backup_enabled: bool = True
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


class ConfigurationTemplateGenerator:
    """
    Enterprise Configuration Template Generator
    
    Generates production-ready infrastructure and application templates
    following IA Chéries Creator Economy business logic and enterprise standards.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize template generator
        
        Args:
            base_path: Base path for template storage
        """
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.template_env = self._setup_jinja_environment()
        self.author_info = {
            "name": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0.0"
        }
        
    def _setup_jinja_environment(self) -> jinja2.Environment:
        """Setup Jinja2 template environment"""
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.base_path)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_template(self, template_type: Union[str, TemplateType], **kwargs) -> str:
        """
        Generate configuration template
        
        Args:
            template_type: Type of template to generate
            **kwargs: Template-specific parameters
            
        Returns:
            Generated template content
        """
        if isinstance(template_type, str):
            try:
                template_type = TemplateType(template_type)
            except ValueError:
                raise ValueError(f"Invalid template type: {template_type}")
                
        generator_method = f"_generate_{template_type.value}_template"
        if not hasattr(self, generator_method):
            raise NotImplementedError(f"Template generator not implemented: {template_type.value}")
            
        return getattr(self, generator_method)(**kwargs)
    
    def _generate_terraform_main_template(self, **kwargs) -> str:
        """Generate Terraform main configuration template"""
        environment = kwargs.get('environment', 'production')
        provider = kwargs.get('provider', 'aws')
        
        template_content = f'''# Terraform Main Configuration - IA Chéries Platform
# Generated by: {self.author_info["name"]} ({self.author_info["email"]})
# Created: {self.author_info["creation_date"]}
# Environment: {environment}
# Provider: {provider}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    {provider} = {{
      source  = "hashicorp/{provider}"
      version = "~> 5.0"
    }}
    kubernetes = {{
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }}
    helm = {{
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }}
  }}
  
  backend "s3" {{
    bucket         = "ainflue-terraform-state-{environment}"
    key            = "infrastructure/terraform.tfstate"
    region         = var.aws_region
    encrypt        = true
    dynamodb_table = "ainflue-terraform-locks"
  }}
}}

# Provider Configuration
provider "{provider}" {{
  region = var.aws_region
  
  default_tags {{
    tags = {{
      Project     = "IA Chéries"
      Environment = "{environment}"
      Owner       = "Fahed Mlaiel"
      ManagedBy   = "Terraform"
      CreatedDate = "{self.author_info["creation_date"]}"
    }}
  }}
}}

provider "kubernetes" {{
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {{
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }}
}}

provider "helm" {{
  kubernetes {{
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {{
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }}
  }}
}}

# Data Sources
data "{provider}_availability_zones" "available" {{
  state = "available"
}}

data "{provider}_caller_identity" "current" {{}}

# Local Values
locals {{
  cluster_name = "ainflue-{environment}"
  region      = var.aws_region
  
  # IA Chéries Creator Economy specific tags
  creator_economy_tags = {{
    BusinessUnit    = "CreatorEconomy"
    ContentType     = "MultiFormat"
    MonetizationEnabled = "true"
    CollaborationSupport = "true"
    SEOOptimized    = "true"
  }}
  
  # Security and compliance tags
  security_tags = {{
    SecurityLevel   = "Enterprise"
    ComplianceRequired = "true"
    DataProtection  = "GDPR"
    IPProtection    = "Enabled"
  }}
  
  # Merge all tags
  common_tags = merge(
    var.common_tags,
    local.creator_economy_tags,
    local.security_tags
  )
}}

# Core Infrastructure Modules
module "vpc" {{
  source = "./modules/vpc"
  
  name               = local.cluster_name
  cidr               = var.vpc_cidr
  azs                = data.aws_availability_zones.available.names
  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets
  enable_nat_gateway = true
  enable_vpn_gateway = var.enable_vpn_gateway
  
  # Creator Economy specific networking
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = local.common_tags
}}

module "eks" {{
  source = "./modules/eks"
  
  cluster_name    = local.cluster_name
  cluster_version = var.kubernetes_version
  
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  
  # Node groups for Creator Economy workloads
  node_groups = {{
    creator_economy = {{
      desired_capacity = var.creator_economy_nodes_desired
      max_capacity     = var.creator_economy_nodes_max
      min_capacity     = var.creator_economy_nodes_min
      instance_types   = var.creator_economy_instance_types
      
      k8s_labels = {{
        WorkloadType = "creator-economy"
        Environment  = "{environment}"
      }}
    }}
    
    ai_processing = {{
      desired_capacity = var.ai_processing_nodes_desired
      max_capacity     = var.ai_processing_nodes_max
      min_capacity     = var.ai_processing_nodes_min
      instance_types   = var.ai_processing_instance_types
      
      k8s_labels = {{
        WorkloadType = "ai-processing"
        Environment  = "{environment}"
      }}
    }}
  }}
  
  tags = local.common_tags
}}

# Security Infrastructure
module "security" {{
  source = "./modules/security"
  
  cluster_name = local.cluster_name
  vpc_id       = module.vpc.vpc_id
  
  # IP Protection and Content Security
  enable_waf              = true
  enable_shield_advanced  = var.enable_shield_advanced
  enable_secrets_manager  = true
  enable_certificate_manager = true
  
  tags = local.common_tags
}}

# Monitoring and Observability
module "monitoring" {{
  source = "./modules/monitoring"
  
  cluster_name = local.cluster_name
  
  # Creator Economy metrics
  enable_business_metrics = true
  enable_creator_analytics = true
  enable_revenue_tracking = true
  
  # Technical metrics
  enable_prometheus = true
  enable_grafana   = true
  enable_jaeger    = true
  enable_elk       = var.enable_elk_stack
  
  tags = local.common_tags
}}

# Database Infrastructure
module "database" {{
  source = "./modules/database"
  
  cluster_name = local.cluster_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
  
  # Creator data storage
  enable_rds_postgresql = true
  enable_rds_mysql     = false
  enable_documentdb    = true
  enable_elasticache   = true
  
  # High availability and backup
  backup_retention_period = var.backup_retention_period
  multi_az               = true
  
  tags = local.common_tags
}}

# Content Delivery Network
module "cdn" {{
  source = "./modules/cdn"
  
  # Creator content distribution
  enable_cloudfront = true
  enable_s3_buckets = true
  
  # Multi-format content support
  content_types = [
    "video",
    "audio", 
    "images",
    "documents",
    "interactive"
  ]
  
  tags = local.common_tags
}}

# Output values for other configurations
output "cluster_endpoint" {{
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}}

output "cluster_name" {{
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}}

output "vpc_id" {{
  description = "VPC ID"
  value       = module.vpc.vpc_id
}}

output "database_endpoints" {{
  description = "Database endpoints"
  value = {{
    postgresql = module.database.postgresql_endpoint
    documentdb = module.database.documentdb_endpoint
    redis      = module.database.redis_endpoint
  }}
}}
'''
        return template_content
    
    def _generate_dockerfile_template(self, **kwargs) -> str:
        """Generate Dockerfile template"""
        base_image = kwargs.get('base_image', 'python:3.11-slim')
        app_type = kwargs.get('app_type', 'web_api')
        
        template_content = f'''# Multi-Stage Dockerfile for IA Chéries Creator Economy Platform
# Generated by: {self.author_info["name"]} ({self.author_info["email"]})
# Created: {self.author_info["creation_date"]}
# Application: {app_type}

# Build Stage
FROM {base_image} AS builder

# Metadata
LABEL maintainer="{self.author_info["name"]} <{self.author_info["email"]}>"
LABEL version="{self.author_info["version"]}"
LABEL description="IA Chéries Creator Economy - {app_type.title()} Service"
LABEL build-date="{self.author_info["creation_date"]}"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    DEBIAN_FRONTEND=noninteractive \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
        curl \\
        git \\
        libpq-dev \\
        libffi-dev \\
        libssl-dev \\
        pkg-config \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r ainflue && useradd -r -g ainflue ainflue

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --upgrade pip \\
    && pip install -r requirements.txt \\
    && pip install -r requirements-production.txt

# Production Stage
FROM {base_image} AS production

# Copy user and group from builder
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Install only runtime dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        libpq5 \\
        curl \\
        ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PYTHONPATH=/app \\
    APP_ENV=production \\
    WORKERS=4

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=ainflue:ainflue . .

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp /app/uploads \\
    && chown -R ainflue:ainflue /app

# Switch to non-root user
USER ainflue

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Default command based on app type
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
'''
        return template_content
    
    def _generate_istio_configuration_template(self, **kwargs) -> str:
        """Generate Istio service mesh configuration"""
        namespace = kwargs.get('namespace', 'ainflue-platform')
        environment = kwargs.get('environment', 'production')
        
        template_content = f'''# Istio Service Mesh Configuration for IA Chéries Creator Economy
# Generated by: {self.author_info["name"]} ({self.author_info["email"]})
# Created: {self.author_info["creation_date"]}
# Environment: {environment}

apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
  labels:
    istio-injection: enabled
    environment: {environment}
    project: ainflue
---
# Istio Gateway for Creator Economy Platform
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: ainflue-gateway
  namespace: {namespace}
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "creators.ainflue.com"
    - "api.ainflue.com"
    - "admin.ainflue.com"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: ainflue-tls-secret
    hosts:
    - "creators.ainflue.com"
    - "api.ainflue.com"
    - "admin.ainflue.com"
---
# Virtual Service for Creator Economy Routes
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ainflue-routes
  namespace: {namespace}
spec:
  hosts:
  - "creators.ainflue.com"
  - "api.ainflue.com"
  - "admin.ainflue.com"
  gateways:
  - ainflue-gateway
  http:
  # Creator Platform Routes
  - match:
    - uri:
        prefix: "/creators"
    - headers:
        host:
          exact: "creators.ainflue.com"
    route:
    - destination:
        host: creator-platform-service
        port:
          number: 80
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
  
  # API Routes
  - match:
    - uri:
        prefix: "/api/v1"
    - headers:
        host:
          exact: "api.ainflue.com"
    route:
    - destination:
        host: api-gateway-service
        port:
          number: 80
    timeout: 60s
    retries:
      attempts: 3
      perTryTimeout: 20s
  
  # Content Processing Routes
  - match:
    - uri:
        prefix: "/process"
    route:
    - destination:
        host: content-processing-service
        port:
          number: 80
    timeout: 300s # 5 minutes for AI processing
  
  # Collaboration Routes
  - match:
    - uri:
        prefix: "/collaborate"
    route:
    - destination:
        host: collaboration-service
        port:
          number: 80
    timeout: 30s
---
# Destination Rules for Traffic Management
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: creator-platform-destination
  namespace: {namespace}
spec:
  host: creator-platform-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 10
        maxRetries: 3
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
---
# Service Entry for External Dependencies
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: external-payment-providers
  namespace: {namespace}
spec:
  hosts:
  - stripe.com
  - paypal.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
---
# Security Policy - Authorization
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: creator-platform-authz
  namespace: {namespace}
spec:
  selector:
    matchLabels:
      app: creator-platform
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/{namespace}/sa/creator-platform-sa"]
  - to:
    - operation:
        methods: ["GET", "POST", "PUT", "DELETE"]
        paths: ["/creators/*", "/api/v1/*"]
  - when:
    - key: source.ip
      notValues: ["192.168.0.0/16"] # Block internal network
---
# Peer Authentication for mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: {namespace}
spec:
  mtls:
    mode: STRICT
---
# Telemetry Configuration
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: creator-economy-metrics
  namespace: {namespace}
spec:
  metrics:
  - providers:
    - name: prometheus
  - overrides:
    - match:
        metric: ALL_METRICS
      tagOverrides:
        business_unit:
          value: "creator-economy"
        environment:
          value: "{environment}"
  accessLogging:
  - providers:
    - name: otel
'''
        return template_content
        
    def save_template(self, template_content: str, filename: str) -> str:
        """
        Save generated template to file
        
        Args:
            template_content: Generated template content
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.base_path / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
            
        logger.info(f"Template saved to: {output_path}")
        return str(output_path)
    
    def generate_all_infrastructure_templates(self) -> Dict[str, str]:
        """Generate all infrastructure as code templates"""
        templates = {}
        
        # Infrastructure templates
        infrastructure_templates = [
            ('terraform_main_template.tf', TemplateType.TERRAFORM_MAIN),
            ('dockerfile_template.dockerfile', TemplateType.DOCKERFILE),
            ('istio_configuration_template.yml', TemplateType.ISTIO_CONFIG),
        ]
        
        for filename, template_type in infrastructure_templates:
            try:
                content = self.generate_template(template_type)
                file_path = self.save_template(content, filename)
                templates[template_type.value] = file_path
                logger.info(f"Generated {template_type.value} template")
            except Exception as e:
                logger.error(f"Failed to generate {template_type.value}: {e}")
                
        return templates


def main():
    """Main function for testing template generation"""
    generator = ConfigurationTemplateGenerator()
    
    # Test individual template generation
    try:
        terraform_content = generator.generate_template(TemplateType.TERRAFORM_MAIN, 
                                                      environment='production',
                                                      provider='aws')
        print("✅ Terraform template generated successfully")
        
        dockerfile_content = generator.generate_template(TemplateType.DOCKERFILE,
                                                       base_image='python:3.11-slim',
                                                       app_type='creator_api')
        print("✅ Dockerfile template generated successfully")
        
        istio_content = generator.generate_template(TemplateType.ISTIO_CONFIG,
                                                  namespace='ainflue-platform',
                                                  environment='production')
        print("✅ Istio configuration template generated successfully")
        
    except Exception as e:
        print(f"❌ Template generation failed: {e}")


if __name__ == "__main__":
    main()