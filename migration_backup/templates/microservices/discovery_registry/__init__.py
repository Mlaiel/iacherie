"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Discovery & Registry Templates for Ainflue Platform
==================================================

Production-ready service discovery and registry templates with:
- Service registry with health monitoring
- Dynamic service discovery
- Multi-backend support (Consul, etcd, Eureka)
- Kubernetes native discovery
- DNS-based discovery
- Health check orchestration

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices & Service Mesh Expert
"""

from .service_registry_template import ServiceRegistryTemplate
from .service_discovery_template import ServiceDiscoveryTemplate
from .consul_integration_template import ConsulIntegrationTemplate
from .etcd_integration_template import EtcdIntegrationTemplate
from .eureka_integration_template import EurekaIntegrationTemplate
from .kubernetes_discovery_template import KubernetesDiscoveryTemplate
from .dns_discovery_template import DnsDiscoveryTemplate
from .health_check_template import HealthCheckTemplate

__all__ = [
    "ServiceRegistryTemplate",
    "ServiceDiscoveryTemplate", 
    "ConsulIntegrationTemplate",
    "EtcdIntegrationTemplate",
    "EurekaIntegrationTemplate",
    "KubernetesDiscoveryTemplate",
    "DnsDiscoveryTemplate",
    "HealthCheckTemplate"
]