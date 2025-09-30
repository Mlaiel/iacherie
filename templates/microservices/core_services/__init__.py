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

Core Services Module for IA Chérie Microservices Platform
======================================================

Enterprise-grade core service templates providing:
- RESTful API services
- GraphQL API services  
- gRPC services
- WebSocket services
- Background worker services
- Cron job services
- Event processor services
- Data pipeline services

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Microservices Architect
"""

from .rest_api_template import RestApiTemplate
from .graphql_api_template import GraphqlApiTemplate
from .grpc_service_template import GrpcServiceTemplate
from .websocket_service_template import WebsocketServiceTemplate
from .background_worker_template import BackgroundWorkerTemplate
from .cron_job_template import CronJobTemplate
from .event_processor_template import EventProcessorTemplate
from .data_pipeline_template import DataPipelineTemplate

__all__ = [
    "RestApiTemplate",
    "GraphqlApiTemplate",
    "GrpcServiceTemplate", 
    "WebsocketServiceTemplate",
    "BackgroundWorkerTemplate",
    "CronJobTemplate",
    "EventProcessorTemplate",
    "DataPipelineTemplate"
]