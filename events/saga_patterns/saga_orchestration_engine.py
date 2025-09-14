"""
Saga Orchestration Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Saga Orchestration Engine - Enterprise Distributed Transaction Management
============================================================================

Central orchestration engine for managing complex business sagas across
the Ainflue platform. Provides centralized saga execution, step coordination,
and compensation handling for distributed transactions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    """Saga execution status enumeration"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    ABORTED = "aborted"


class SagaStepStatus(Enum):
    """Individual saga step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"
    SKIPPED = "skipped"


@dataclass
class SagaStepResult:
    """Result of saga step execution"""
    step_id: str
    status: SagaStepStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    compensation_data: Optional[Dict[str, Any]] = None


@dataclass
class SagaResult:
    """Overall saga execution result"""
    saga_id: str
    status: SagaStatus
    results: Dict[str, SagaStepResult] = field(default_factory=dict)
    error_message: Optional[str] = None
    total_execution_time: float = 0.0
    completed_at: Optional[datetime] = None
    
    @classmethod
    def SUCCESS(cls, saga_id: str, results: Dict[str, SagaStepResult]) -> 'SagaResult':
        return cls(saga_id=saga_id, status=SagaStatus.COMPLETED, results=results)
    
    @classmethod
    def FAILED(cls, saga_id: str, error: str) -> 'SagaResult':
        return cls(saga_id=saga_id, status=SagaStatus.FAILED, error_message=error)


class SagaStepException(Exception):
    """Exception raised during saga step execution"""
    pass


class SagaStep(ABC):
    """Abstract base class for saga steps"""
    
    def __init__(self, step_id -> None: str, step_name -> None: str) -> None:
        self.step_id = step_id
        self.step_name = step_name
        self.dependencies: List[str] = []
        self.compensation_data: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> SagaStepResult:
        """Execute the saga step"""
        pass
    
    @abstractmethod
    async def compensate(self, context: Dict[str, Any]) -> bool:
        """Compensate the saga step"""
        pass


class ContentProcessingSaga:
    """Business saga for content processing workflow"""
    
    def __init__(self, saga_id -> None: str, creator_id -> None: str, content_data -> None: Dict[str, Any]) -> None:
        self.saga_id = saga_id
        self.creator_id = creator_id
        self.content_data = content_data
        self.content_id: Optional[str] = None
        self.ai_analysis_result: Optional[Dict[str, Any]] = None
        self.protection_applied = False
        self.seo_optimized = False
        self.compensation_actions: List[Callable] = []
    
    async def execute_saga(self) -> SagaResult:
        """Execute complete content processing workflow"""
        start_time = time.time()
        results = {}
        
        try:
            # Step 1: Upload content
            upload_result = await self._upload_content_step()
            results["upload"] = upload_result
            if upload_result.status == SagaStepStatus.FAILED:
                raise SagaStepException(upload_result.error_message)
            
            # Step 2: AI Analysis (parallel with protection)
            ai_task = self._ai_analysis_step()
            protection_task = self._content_protection_step()
            
            ai_result, protection_result = await asyncio.gather(
                ai_task, protection_task, return_exceptions=True
            )
            
            if isinstance(ai_result, Exception):
                raise SagaStepException(f"AI analysis failed: {ai_result}")
            if isinstance(protection_result, Exception):
                raise SagaStepException(f"Protection failed: {protection_result}")
            
            results["ai_analysis"] = ai_result
            results["protection"] = protection_result
            
            # Step 3: SEO optimization
            seo_result = await self._seo_optimization_step()
            results["seo"] = seo_result
            if seo_result.status == SagaStepStatus.FAILED:
                raise SagaStepException(seo_result.error_message)
            
            # Step 4: Distribution
            distribution_result = await self._content_distribution_step()
            results["distribution"] = distribution_result
            if distribution_result.status == SagaStepStatus.FAILED:
                raise SagaStepException(distribution_result.error_message)
            
            total_time = time.time() - start_time
            return SagaResult(
                saga_id=self.saga_id,
                status=SagaStatus.COMPLETED,
                results=results,
                total_execution_time=total_time,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Saga {self.saga_id} failed: {e}")
            await self._compensate_saga()
            total_time = time.time() - start_time
            return SagaResult(
                saga_id=self.saga_id,
                status=SagaStatus.FAILED,
                error_message=str(e),
                results=results,
                total_execution_time=total_time
            )
    
    async def _upload_content_step(self) -> SagaStepResult:
        """Execute content upload step"""
        try:
            # Simulate content upload
            await asyncio.sleep(0.1)  # Simulate I/O
            self.content_id = f"content_{uuid.uuid4().hex[:8]}"
            
            # Register compensation
            self.compensation_actions.append(
                lambda: self._delete_uploaded_content(self.content_id)
            )
            
            return SagaStepResult(
                step_id="upload",
                status=SagaStepStatus.COMPLETED,
                output_data={"content_id": self.content_id}
            )
            
        except Exception as e:
            return SagaStepResult(
                step_id="upload",
                status=SagaStepStatus.FAILED,
                error_message=str(e)
            )
    
    async def _ai_analysis_step(self) -> SagaStepResult:
        """Execute AI analysis step"""
        try:
            await asyncio.sleep(0.2)  # Simulate AI processing
            self.ai_analysis_result = {
                "sentiment": "positive",
                "quality_score": 0.85,
                "content_type": "video"
            }
            
            self.compensation_actions.append(
                lambda: self._cleanup_ai_analysis(self.content_id)
            )
            
            return SagaStepResult(
                step_id="ai_analysis",
                status=SagaStepStatus.COMPLETED,
                output_data=self.ai_analysis_result
            )
            
        except Exception as e:
            return SagaStepResult(
                step_id="ai_analysis",
                status=SagaStepStatus.FAILED,
                error_message=str(e)
            )
    
    async def _content_protection_step(self) -> SagaStepResult:
        """Execute content protection step"""
        try:
            await asyncio.sleep(0.1)  # Simulate protection
            self.protection_applied = True
            
            return SagaStepResult(
                step_id="protection",
                status=SagaStepStatus.COMPLETED,
                output_data={"protected": True}
            )
            
        except Exception as e:
            return SagaStepResult(
                step_id="protection",
                status=SagaStepStatus.FAILED,
                error_message=str(e)
            )
    
    async def _seo_optimization_step(self) -> SagaStepResult:
        """Execute SEO optimization step"""
        try:
            await asyncio.sleep(0.15)  # Simulate SEO processing
            self.seo_optimized = True
            
            return SagaStepResult(
                step_id="seo",
                status=SagaStepStatus.COMPLETED,
                output_data={"seo_score": 0.92}
            )
            
        except Exception as e:
            return SagaStepResult(
                step_id="seo",
                status=SagaStepStatus.FAILED,
                error_message=str(e)
            )
    
    async def _content_distribution_step(self) -> SagaStepResult:
        """Execute content distribution step"""
        try:
            await asyncio.sleep(0.1)  # Simulate distribution
            
            return SagaStepResult(
                step_id="distribution",
                status=SagaStepStatus.COMPLETED,
                output_data={"platforms": ["youtube", "spotify"]}
            )
            
        except Exception as e:
            return SagaStepResult(
                step_id="distribution",
                status=SagaStepStatus.FAILED,
                error_message=str(e)
            )
    
    async def _compensate_saga(self) -> None:
        """Execute compensation for failed saga"""
        logger.info(f"Starting compensation for saga {self.saga_id}")
        
        # Execute compensation actions in reverse order
        for compensation_action in reversed(self.compensation_actions):
            try:
                await compensation_action()
            except Exception as e:
                logger.error(f"Compensation action failed: {e}")
    
    async def _delete_uploaded_content(self, content_id -> None: str) -> None:
        """Compensation: delete uploaded content"""
        logger.info(f"Compensating: deleting content {content_id}")
        await asyncio.sleep(0.05)  # Simulate cleanup
    
    async def _cleanup_ai_analysis(self, content_id -> None: str) -> None:
        """Compensation: cleanup AI analysis data"""
        logger.info(f"Compensating: cleaning up AI analysis for {content_id}")
        await asyncio.sleep(0.05)  # Simulate cleanup


class SagaOrchestrationEngine:
    """Central orchestration engine for managing sagas"""
    
    def __init__(self) -> None:
        self.active_sagas: Dict[str, Any] = {}
        self.saga_definitions: Dict[str, Callable] = {}
        self.execution_metrics: Dict[str, Any] = {}
    
    def register_saga_definition(self, saga_type -> None: str, saga_factory -> None: Callable) -> None:
        """Register a saga definition"""
        self.saga_definitions[saga_type] = saga_factory
        logger.info(f"Registered saga definition: {saga_type}")
    
    async def start_saga(
        self, 
        saga_type: str, 
        saga_data: Dict[str, Any]
    ) -> str:
        """Start a new saga execution"""
        saga_id = str(uuid.uuid4())
        
        if saga_type not in self.saga_definitions:
            raise ValueError(f"Unknown saga type: {saga_type}")
        
        saga_factory = self.saga_definitions[saga_type]
        saga_instance = saga_factory(saga_id, **saga_data)
        
        self.active_sagas[saga_id] = {
            "instance": saga_instance,
            "type": saga_type,
            "started_at": datetime.now(timezone.utc),
            "status": SagaStatus.RUNNING
        }
        
        logger.info(f"Started saga {saga_id} of type {saga_type}")
        
        # Execute saga asynchronously
        asyncio.create_task(self._execute_saga(saga_id))
        
        return saga_id
    
    async def _execute_saga(self, saga_id -> None: str) -> None:
        """Execute saga and update status"""
        try:
            saga_info = self.active_sagas[saga_id]
            saga_instance = saga_info["instance"]
            
            result = await saga_instance.execute_saga()
            
            saga_info["status"] = result.status
            saga_info["completed_at"] = datetime.now(timezone.utc)
            saga_info["result"] = result
            
            # Update metrics
            self._update_execution_metrics(saga_info["type"], result.status)
            
            logger.info(f"Saga {saga_id} completed with status {result.status}")
            
        except Exception as e:
            logger.error(f"Saga execution failed for {saga_id}: {e}")
            if saga_id in self.active_sagas:
                self.active_sagas[saga_id]["status"] = SagaStatus.FAILED
                self.active_sagas[saga_id]["error"] = str(e)
    
    async def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a saga"""
        return self.active_sagas.get(saga_id)
    
    async def list_active_sagas(self) -> List[Dict[str, Any]]:
        """List all active sagas"""
        return [
            {
                "saga_id": saga_id,
                "type": info["type"],
                "status": info["status"],
                "started_at": info["started_at"]
            }
            for saga_id, info in self.active_sagas.items()
            if info["status"] in [SagaStatus.RUNNING, SagaStatus.COMPENSATING]
        ]
    
    def _update_execution_metrics(self, saga_type -> None: str, status -> None: SagaStatus) -> None:
        """Update execution metrics"""
        if saga_type not in self.execution_metrics:
            self.execution_metrics[saga_type] = {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "compensated": 0
            }
        
        metrics = self.execution_metrics[saga_type]
        metrics["total"] += 1
        
        if status == SagaStatus.COMPLETED:
            metrics["completed"] += 1
        elif status == SagaStatus.FAILED:
            metrics["failed"] += 1
        elif status == SagaStatus.COMPENSATED:
            metrics["compensated"] += 1
    
    async def get_execution_metrics(self) -> Dict[str, Any]:
        """Get saga execution metrics"""
        return self.execution_metrics.copy()


# Global orchestration engine instance
_orchestration_engine: Optional[SagaOrchestrationEngine] = None


def get_saga_orchestration_engine() -> SagaOrchestrationEngine:
    """Get global saga orchestration engine"""
    global _orchestration_engine
    if _orchestration_engine is None:
        _orchestration_engine = SagaOrchestrationEngine()
        
        # Register built-in saga definitions
        _orchestration_engine.register_saga_definition(
            "content_processing",
            lambda saga_id, creator_id, content_data: ContentProcessingSaga(
                saga_id, creator_id, content_data
            )
        )
    
    return _orchestration_engine


async def start_content_processing_saga(
    creator_id: str, 
    content_data: Dict[str, Any]
) -> str:
    """Convenience function to start content processing saga"""
    engine = get_saga_orchestration_engine()
    return await engine.start_saga(
        "content_processing",
        {"creator_id": creator_id, "content_data": content_data}
    )


__all__ = [
    "SagaOrchestrationEngine",
    "SagaStatus", 
    "SagaStepStatus",
    "SagaResult",
    "SagaStepResult",
    "SagaStep",
    "ContentProcessingSaga",
    "get_saga_orchestration_engine",
    "start_content_processing_saga"
]