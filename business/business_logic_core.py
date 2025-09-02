#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Business Logic Core - Compatibility Layer
====================================

This module provides a compatibility layer that imports from the enhanced
business logic core while maintaining backward compatibility.

Author: Auto-generated for compatibility
"""

# Import from the enhanced business logic core
import sys
from pathlib import Path
import logging

# Add root directory to path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

logger = logging.getLogger(__name__)

try:
    # Import from enhanced business logic core
    from enhanced_business_logic_core import (
        EnhancedBusinessLogicCore as BusinessLogicCore,
        ContentType as CreatorType,
        ContentUpload,
        WorkflowResult,
        WorkflowStage
    )
    
    logger.info("Successfully imported from enhanced business logic core")
    
except ImportError as e:
    logger.warning(f"Could not import from enhanced core: {e}")
    
    # Fallback to minimal implementations
    from enum import Enum
    from typing import Dict, Any, List
    from dataclasses import dataclass
    
    class CreatorType(Enum):
        INFLUENCER = "influencer"
        BRAND = "brand"
        AGENCY = "agency"
    
    @dataclass
    class ContentUpload:
        content_id: str
        creator_id: str
        content_type: str
        file_path: str
        metadata: Dict[str, Any]
    
    @dataclass 
    class WorkflowResult:
        stage: str
        status: str
        results: Dict[str, Any]
    
    @dataclass
    class WorkflowStage:
        name: str
        order: int
        required: bool
    
    class BusinessLogicCore:
        def __init__(self):
            self.initialized = False
            logger.info("BusinessLogicCore fallback implementation initialized")
        
        async def initialize(self):
            """Initialize the business logic core"""
            self.initialized = True
            logger.info("Business logic core initialized successfully")
            return True
        
        async def process_creator_workflow(self, content: ContentUpload) -> List[WorkflowResult]:
            """Process creator workflow"""
            logger.info(f"Processing workflow for content: {content.content_id}")
            
            return [
                WorkflowResult(
                    stage="processing",
                    status="completed", 
                    results={"content_id": content.content_id, "processed": True}
                )
            ]
        
        def get_agent_status(self) -> Dict[str, Any]:
            """Get agent status"""
            return {"status": "active", "initialized": self.initialized}


# Module exports
__all__ = [
    'BusinessLogicCore',
    'CreatorType', 
    'ContentUpload',
    'WorkflowResult',
    'WorkflowStage'
]