"""DevOps Templates Module for IA Chérie Platform
Enterprise-grade Infrastructure as Code and DevOps automation templates.

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE
© 2025 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés - Utilisation commerciale interdite sans autorisation écrite explicite

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2024-09-18
"""

from .terraform_infrastructure_template import (
    TerraformInfrastructureTemplate,
    TerraformConfig,
    CloudProvider,
    EnvironmentType as TerraformEnvironmentType,
    create_production_config as create_terraform_prod_config,
    create_development_config as create_terraform_dev_config
)

from .ansible_playbook_template import (
    AnsiblePlaybookTemplate,
    AnsibleConfig,
    DeploymentTarget,
    ServiceType as AnsibleServiceType,
    create_production_config as create_ansible_prod_config,
    create_development_config as create_ansible_dev_config
)

from .github_actions_template import (
    GitHubActionsTemplate,
    GitHubActionsConfig,
    PipelineType,
    EnvironmentType as GitHubEnvironmentType,
    create_production_config as create_github_prod_config
)

from .kubernetes_deployment_template import (
    KubernetesDeploymentTemplate,
    KubernetesConfig,
    ResourceType,
    ServiceType as KubernetesServiceType,
    create_production_config as create_k8s_prod_config,
    create_development_config as create_k8s_dev_config
)

from .docker_compose_template import (
    DockerComposeTemplate,
    DockerComposeConfig,
    EnvironmentType as DockerEnvironmentType,
    create_development_config as create_docker_dev_config,
    create_testing_config as create_docker_test_config
)

from .deployment_automation_template import (
    DeploymentAutomationTemplate,
    DeploymentStage,
    DeploymentStrategy,
    Environment
)

from .security_scanning_template import (
    SecurityScanningTemplate,
    SecurityScanConfig,
    ScanType,
    SeverityLevel,
    create_production_security_config
)

from .secret_management_template import (
    SecretManagementTemplate,
    SecretManagementConfig,
    SecretBackend,
    SecretType,
    create_production_secret_config
)

from .prometheus_config_template import (
    PrometheusConfigTemplate,
    PrometheusConfig,
    MetricType,
    ServiceType as PrometheusServiceType,
    create_production_prometheus_config
)

from .creator_content_pipeline_template import (
    CreatorContentPipelineTemplate,
    CreatorPipelineConfig,
    ContentType,
    ProcessingStage,
    QualityPreset,
    create_production_pipeline_config
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export all template classes
__all__ = [
    # Infrastructure as Code
    "TerraformInfrastructureTemplate",
    "TerraformConfig", 
    "CloudProvider",
    "create_terraform_prod_config",
    "create_terraform_dev_config",
    
    # Configuration Management
    "AnsiblePlaybookTemplate",
    "AnsibleConfig",
    "DeploymentTarget",
    "create_ansible_prod_config", 
    "create_ansible_dev_config",
    
    # CI/CD Pipelines
    "GitHubActionsTemplate",
    "GitHubActionsConfig",
    "PipelineType",
    "create_github_prod_config",
    
    # Container Orchestration
    "KubernetesDeploymentTemplate",
    "KubernetesConfig",
    "ResourceType",
    "create_k8s_prod_config",
    "create_k8s_dev_config",
    
    # Development Environment
    "DockerComposeTemplate",
    "DockerComposeConfig", 
    "create_docker_dev_config",
    "create_docker_test_config",
    
    # Deployment Automation
    "DeploymentAutomationTemplate",
    "DeploymentStage",
    "DeploymentStrategy",
    "Environment",
    
    # Security DevOps
    "SecurityScanningTemplate",
    "SecurityScanConfig",
    "ScanType",
    "SeverityLevel",
    "create_production_security_config",
    
    "SecretManagementTemplate",
    "SecretManagementConfig",
    "SecretBackend",
    "SecretType",
    "create_production_secret_config",
    
    # Monitoring & Observability
    "PrometheusConfigTemplate",
    "PrometheusConfig",
    "MetricType",
    "create_production_prometheus_config",
    
    # Creator Economy DevOps
    "CreatorContentPipelineTemplate",
    "CreatorPipelineConfig",
    "ContentType",
    "ProcessingStage",
    "QualityPreset",
    "create_production_pipeline_config"
]


def get_template_info():
    """Get information about available DevOps templates"""
    return {
        "module": "iacherie.templates.devops",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "templates": {
            "infrastructure": {
                "terraform": "Enterprise Terraform Infrastructure as Code templates",
                "ansible": "Enterprise Ansible configuration management playbooks"
            },
            "cicd": {
                "github_actions": "GitHub Actions CI/CD pipeline templates",
                "gitlab_ci": "GitLab CI/CD pipeline templates (coming soon)",
                "jenkins": "Jenkins pipeline templates (coming soon)"
            },
            "containers": {
                "kubernetes": "Kubernetes deployment and orchestration templates",
                "docker_compose": "Docker Compose development environment templates",
                "helm": "Helm chart templates (coming soon)"
            },
            "monitoring": {
                "prometheus": "Prometheus monitoring templates (coming soon)",
                "grafana": "Grafana dashboard templates (coming soon)",
                "alertmanager": "Alertmanager configuration templates (coming soon)"
            },
            "security": {
                "vault": "HashiCorp Vault security templates (coming soon)",
                "rbac": "Kubernetes RBAC security templates (coming soon)",
                "network_policies": "Network security policy templates (coming soon)"
            }
        },
        "creator_economy_features": [
            "AI/ML model deployment automation",
            "Multi-format content processing pipelines", 
            "Creator collaboration infrastructure",
            "Revenue optimization deployments",
            "SEO-optimized content delivery",
            "Analytics and monitoring for creators",
            "Scalable media storage and CDN",
            "Real-time collaboration systems"
        ]
    }


def create_complete_devops_stack(environment: str = "development"):
    """Create a complete DevOps stack for IA Chérie platform"""
    if environment == "production":
        terraform_config = create_terraform_prod_config()
        ansible_config = create_ansible_prod_config()
        github_config = create_github_prod_config()
        k8s_config = create_k8s_prod_config()
    else:
        terraform_config = create_terraform_dev_config()
        ansible_config = create_ansible_dev_config()
        github_config = create_github_prod_config()  # Same config for all envs
        k8s_config = create_k8s_dev_config()
    
    docker_config = create_docker_dev_config()
    
    return {
        "terraform": TerraformInfrastructureTemplate(terraform_config),
        "ansible": AnsiblePlaybookTemplate(ansible_config),
        "github_actions": GitHubActionsTemplate(github_config),
        "kubernetes": KubernetesDeploymentTemplate(k8s_config),
        "docker_compose": DockerComposeTemplate(docker_config)
    }
