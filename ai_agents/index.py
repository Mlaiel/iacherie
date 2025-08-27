"""
IA-Influencer-Agent — AI Agents Root Index

Ultra-advanced industrial-grade AI agents system providing unified access to all agent operations.
Main entry point for content creators protection, monetization, and collaboration platform.

Architecture Flow:
Creator Upload → AI Content Processing → Rights Protection → SEO Optimization → 
Collaboration Matching → Multi-Platform Distribution → Revenue Analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code, architecture, and product concept are exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization without 
explicit written permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.

Project Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

from . import (
    agent_manager,
    initialize_agent_system,
    shutdown_agent_system,
    AgentFactory,
    get_available_agent_types,
    get_agent_info,
)
from .base import AgentRequest, AgentResponse
from .content_agent.business_workflow import (
    BusinessWorkflowOrchestrator,
    WorkflowConfig,
    CreatorType,
    ContentUpload,
    workflow_orchestrator,
)

logger = logging.getLogger(__name__)

# High-level bootstrap/shutdown
async def bootstrap(config: Optional[Dict[str, Any]] = None) -> bool:
    """Start the global agent manager and register all agent pools."""
    # config reserved for future extensions; initialize_agent_system handles pools/classes
    ok = await initialize_agent_system()
    if ok:
        logger.info("AI Agents system bootstrapped successfully")
    else:
        logger.error("AI Agents system bootstrap failed")
    return ok

async def shutdown() -> None:
    """Gracefully stop the agent manager and agents."""
    await shutdown_agent_system()

# Request routing convenience
async def route_request(request: AgentRequest) -> AgentResponse:
    """Route an AgentRequest through the global manager with load balancing."""
    return await agent_manager.process_request(request)

async def get_system_status() -> Dict[str, Any]:
    """Return a comprehensive snapshot of the agent system status."""
    return await agent_manager.get_system_status()

# Agent utilities
def list_agent_types() -> List[str]:
    """List all available agent types registered in the system."""
    return get_available_agent_types()

def describe_agent(agent_type: str) -> Optional[Dict[str, Any]]:
    """Describe a specific agent type (class name, module, description)."""
    return get_agent_info(agent_type)

async def create_agent_instance(agent_type: str, agent_id: str, config: Optional[Dict[str, Any]] = None):
    """Create and initialize a single agent instance via the factory."""
    return await AgentFactory.create_agent(agent_type=agent_type, agent_id=agent_id, config=config)

# Business workflow shortcuts
async def get_workflow_orchestrator() -> BusinessWorkflowOrchestrator:
    """Return the singleton business workflow orchestrator (initialized on demand)."""
    # The module exports a singleton; ensure dependencies are initialized by caller if needed
    return workflow_orchestrator

async def process_upload(
    *,
    content_id: str,
    creator_id: str,
    creator_type: CreatorType,
    content_type: str,
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[WorkflowConfig] = None,
) -> str:
    """End-to-end content processing entry point using the business orchestrator."""
    orchestrator = await get_workflow_orchestrator()
    if getattr(orchestrator, "protection_agent", None) is None:
        await orchestrator.initialize()
    upload = ContentUpload(
        content_id=content_id,
        creator_id=creator_id,
        creator_type=creator_type,
        content_type=content_type,
        file_path=file_path,
        metadata=metadata or {},
        upload_timestamp=__import__("datetime").datetime.utcnow(),
        processing_config=config or WorkflowConfig(creator_type=creator_type),
    )
    return await orchestrator.process_content_upload(upload)

__all__ = [
    # lifecycle
    "bootstrap",
    "shutdown",
    # routing and status
    "route_request",
    "get_system_status",
    # agent utils
    "list_agent_types",
    "describe_agent",
    "create_agent_instance",
    # workflow
    "get_workflow_orchestrator",
    "process_upload",
    # types
    "AgentRequest",
    "AgentResponse",
    "BusinessWorkflowOrchestrator",
    "WorkflowConfig",
    "CreatorType",
    "ContentUpload",
]
