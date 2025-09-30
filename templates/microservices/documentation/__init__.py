#!/usr/bin/env python3
"""
📚 Documentation Templates - IA Chérie Microservices Enterprise

API documentation, OpenAPI specs, runbooks, and automated
documentation generation for microservices architecture.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

from .api_documentation_template import APIDocumentationTemplate
from .swagger_generator_template import SwaggerGeneratorTemplate
from .openapi_spec_template import OpenAPISpecTemplate
from .service_catalog_template import ServiceCatalogTemplate
from .architecture_diagram_template import ArchitectureDiagramTemplate
from .runbook_template import RunbookTemplate
from .troubleshooting_guide_template import TroubleshootingGuideTemplate
from .deployment_guide_template import DeploymentGuideTemplate

__all__ = [
    "APIDocumentationTemplate",
    "SwaggerGeneratorTemplate",
    "OpenAPISpecTemplate",
    "ServiceCatalogTemplate",
    "ArchitectureDiagramTemplate", 
    "RunbookTemplate",
    "TroubleshootingGuideTemplate",
    "DeploymentGuideTemplate"
]