#!/usr/bin/env python3
"""
🚀 Deployment Templates - IA Chérie Microservices Enterprise

DevOps deployment automation templates for Kubernetes, Docker, Helm,
Terraform, CI/CD pipelines, and advanced deployment strategies.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de

⚠️ PROPRIETARY SOFTWARE - Unauthorized use prohibited
"""

from .kubernetes_deployment_template import KubernetesDeploymentTemplate
from .docker_compose_template import DockerComposeTemplate
from .helm_chart_template import HelmChartTemplate
from .terraform_template import TerraformTemplate
from .ansible_playbook_template import AnsiblePlaybookTemplate
from .ci_cd_pipeline_template import CICDPipelineTemplate
from .blue_green_deployment_template import BlueGreenDeploymentTemplate
from .canary_deployment_template import CanaryDeploymentTemplate

__all__ = [
    "KubernetesDeploymentTemplate",
    "DockerComposeTemplate",
    "HelmChartTemplate",
    "TerraformTemplate",
    "AnsiblePlaybookTemplate",
    "CICDPipelineTemplate",
    "BlueGreenDeploymentTemplate",
    "CanaryDeploymentTemplate"
]