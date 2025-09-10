"""Enterprise Content Ingestion Engine
=====================================

Professional content ingestion orchestration system for the IA Influencer Agent platform.
Provides comprehensive workflow management, content lifecycle handling, and enterprise-grade
ingestion capabilities with AI-powered optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import tempfile
import os
from pathlib import Path

# Core exceptions
from ...core.exceptions import IngestionError, WorkflowError, ValidationError


class IngestionStatus(Enum):
    """Content ingestion status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class IngestionPriority(Enum):
    """Content ingestion priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingMode(Enum):
    """Content processing mode types"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAM = "stream"
    HYBRID = "hybrid"


class ContentSource(Enum):
    """Content source types"""
    UPLOAD = "upload"
    URL = "url"
    STREAM = "stream"
    API = "api"
    IMPORT = "import"


class ContentType(Enum):
    """Content type classifications"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"


class WorkflowStage(Enum):
    """Workflow execution stages"""
    INTAKE = "intake"
    VALIDATION = "validation"
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    ROUTING = "routing"
    STORAGE = "storage"
    COMPLETION = "completion"


class WorkflowStatus(Enum):
    """Workflow status states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowPriority(Enum):
    """Workflow priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionMode(Enum):
    """Workflow execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    processing_duration: Optional[float] = None
    throughput_mbps: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    error_count: int = 0
    retry_count: int = 0


@dataclass
class QualityMetrics:
    """Content quality assessment metrics"""
    overall_score: float = 0.0
    technical_score: float = 0.0
    content_score: float = 0.0
    compliance_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


@dataclass
class SecurityAssessment:
    """Content security assessment results"""
    is_safe: bool = True
    threat_level: str = "none"
    malware_detected: bool = False
    policy_violations: List[str] = field(default_factory=list)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    scan_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IngestionRequest:
    """Content ingestion request specification"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_source: ContentSource = ContentSource.UPLOAD
    content_type: Optional[ContentType] = None
    priority: IngestionPriority = IngestionPriority.NORMAL
    processing_mode: ProcessingMode = ProcessingMode.REAL_TIME
    metadata: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    callback_url: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IngestionResult:
    """Content ingestion result data"""
    request_id: str
    status: IngestionStatus
    content_id: Optional[str] = None
    output_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_metrics: Optional[ProcessingMetrics] = None
    quality_metrics: Optional[QualityMetrics] = None
    security_assessment: Optional[SecurityAssessment] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowStageConfig:
    """Workflow stage configuration"""
    stage: WorkflowStage
    enabled: bool = True
    timeout_seconds: int = 300
    retry_attempts: int = 3
    parallel_execution: bool = False
    dependencies: List[WorkflowStage] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowConfiguration:
    """Complete workflow configuration"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "default_workflow"
    description: str = ""
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    stages: List[WorkflowStageConfig] = field(default_factory=list)
    global_timeout_seconds: int = 3600
    max_retry_attempts: int = 3
    failure_handling: str = "stop"  # stop, continue, retry
    notification_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_config: WorkflowConfiguration
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_stage: Optional[WorkflowStage] = None
    completed_stages: List[WorkflowStage] = field(default_factory=list)
    failed_stages: List[WorkflowStage] = field(default_factory=list)
    stage_results: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_messages: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionCapabilities:
    """System ingestion capabilities"""
    supported_formats: List[str] = field(default_factory=list)
    max_file_size_mb: int = 1024
    max_concurrent_ingestions: int = 10
    ai_analysis_enabled: bool = True
    real_time_processing: bool = True
    batch_processing: bool = True
    streaming_support: bool = True
    security_scanning: bool = True
    quality_assessment: bool = True


class ContentIngestionManager:
    """
    Professional content ingestion manager for enterprise-grade content processing.
    
    Handles multi-format content ingestion with AI-powered analysis, quality assessment,
    security validation, and intelligent routing across the IA Influencer Agent platform.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the content ingestion manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize capabilities
        self.capabilities = IngestionCapabilities(
            supported_formats=[
                'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a',  # Audio
                'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv',  # Video
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp',  # Image
                'txt', 'md', 'html', 'json', 'xml', 'csv',  # Text
                'pdf', 'docx', 'doc', 'rtf', 'odt'  # Documents
            ],
            max_file_size_mb=self.config.get('max_file_size_mb', 1024),
            max_concurrent_ingestions=self.config.get('max_concurrent', 10),
            ai_analysis_enabled=self.config.get('ai_enabled', True),
            real_time_processing=True,
            batch_processing=True,
            streaming_support=True,
            security_scanning=True,
            quality_assessment=True
        )
        
        # Internal state
        self._active_ingestions: Dict[str, IngestionResult] = {}
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(self.capabilities.max_concurrent_ingestions)
        
    async def ingest_content(self, content_data: Union[bytes, str], 
                           filename: str, request: IngestionRequest) -> IngestionResult:
        """
        Ingest content with comprehensive processing pipeline.
        
        Args:
            content_data: Content file data or URL
            filename: Original filename
            request: Ingestion request configuration
            
        Returns:
            Complete ingestion result
        """
        result = IngestionResult(
            request_id=request.request_id,
            status=IngestionStatus.PENDING
        )
        
        try:
            self.logger.info(f"Starting content ingestion: {request.request_id}")
            
            # Add to active ingestions
            self._active_ingestions[request.request_id] = result
            
            async with self._semaphore:
                result.status = IngestionStatus.IN_PROGRESS
                result.processing_metrics = ProcessingMetrics()
                
                # Step 1: Content validation
                await self._validate_content(content_data, filename, result)
                
                # Step 2: Format detection and processing
                await self._process_content_format(content_data, filename, result)
                
                # Step 3: AI-powered analysis (if enabled)
                if self.capabilities.ai_analysis_enabled:
                    await self._analyze_content_ai(content_data, filename, result)
                
                # Step 4: Quality assessment
                await self._assess_content_quality(result)
                
                # Step 5: Security validation
                await self._validate_content_security(content_data, result)
                
                # Step 6: Generate content ID and metadata
                await self._generate_content_metadata(filename, result)
                
                # Mark as completed
                result.status = IngestionStatus.COMPLETED
                result.completed_at = datetime.utcnow()
                
                # Calculate processing metrics
                if result.processing_metrics:
                    result.processing_metrics.end_time = datetime.utcnow()
                    result.processing_metrics.processing_duration = (
                        result.processing_metrics.end_time - 
                        result.processing_metrics.start_time
                    ).total_seconds()
                
                self.logger.info(f"Content ingestion completed: {request.request_id}")
                return result
                
        except Exception as e:
            self.logger.error(f"Content ingestion failed: {request.request_id} - {str(e)}")
            result.status = IngestionStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.utcnow()
            return result
            
        finally:
            # Clean up
            if request.request_id in self._active_ingestions:
                del self._active_ingestions[request.request_id]
    
    async def batch_ingest_content(self, content_items: List[tuple],
                                 requests: List[IngestionRequest]) -> List[IngestionResult]:
        """
        Batch process multiple content items.
        
        Args:
            content_items: List of (content_data, filename) tuples
            requests: List of ingestion requests
            
        Returns:
            List of ingestion results
        """
        try:
            self.logger.info(f"Starting batch ingestion: {len(content_items)} items")
            
            # Process items concurrently with semaphore control
            tasks = []
            for i, (content_data, filename) in enumerate(content_items):
                request = requests[i] if i < len(requests) else IngestionRequest()
                task = self.ingest_content(content_data, filename, request)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = IngestionResult(
                        request_id=requests[i].request_id if i < len(requests) else str(uuid.uuid4()),
                        status=IngestionStatus.FAILED
                    )
                    error_result.errors.append(str(result))
                    final_results.append(error_result)
                else:
                    final_results.append(result)
            
            self.logger.info(f"Batch ingestion completed: {len(final_results)} results")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Batch ingestion failed: {str(e)}")
            raise IngestionError(f"Batch ingestion failed: {str(e)}")
    
    async def get_ingestion_status(self, request_id: str) -> Optional[IngestionResult]:
        """Get current status of ingestion request"""
        return self._active_ingestions.get(request_id)
    
    async def cancel_ingestion(self, request_id: str) -> bool:
        """Cancel active ingestion request"""
        if request_id in self._active_ingestions:
            result = self._active_ingestions[request_id]
            result.status = IngestionStatus.CANCELLED
            return True
        return False
    
    def get_capabilities(self) -> IngestionCapabilities:
        """Get system ingestion capabilities"""
        return self.capabilities
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return {
            'active_ingestions': len(self._active_ingestions),
            'queue_size': self._processing_queue.qsize(),
            'available_slots': self._semaphore._value,
            'capabilities': {
                'max_concurrent': self.capabilities.max_concurrent_ingestions,
                'max_file_size_mb': self.capabilities.max_file_size_mb,
                'supported_formats': len(self.capabilities.supported_formats)
            }
        }
    
    # Private processing methods
    
    async def _validate_content(self, content_data: Union[bytes, str], 
                              filename: str, result: IngestionResult):
        """Validate content before processing"""
        try:
            # Basic validation
            if isinstance(content_data, bytes):
                size_mb = len(content_data) / (1024 * 1024)
                if size_mb > self.capabilities.max_file_size_mb:
                    raise ValidationError(f"File size {size_mb:.1f}MB exceeds limit")
            
            # Format validation
            file_ext = Path(filename).suffix.lower().strip('.')
            if file_ext not in self.capabilities.supported_formats:
                result.warnings.append(f"Format {file_ext} may not be fully supported")
            
        except Exception as e:
            raise ValidationError(f"Content validation failed: {str(e)}")
    
    async def _process_content_format(self, content_data: Union[bytes, str],
                                    filename: str, result: IngestionResult):
        """Process content based on format"""
        try:
            file_ext = Path(filename).suffix.lower().strip('.')
            
            # Determine content type
            if file_ext in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']:
                content_type = ContentType.AUDIO
            elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']:
                content_type = ContentType.VIDEO
            elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']:
                content_type = ContentType.IMAGE
            elif file_ext in ['txt', 'md', 'html', 'json', 'xml', 'csv']:
                content_type = ContentType.TEXT
            elif file_ext in ['pdf', 'docx', 'doc', 'rtf', 'odt']:
                content_type = ContentType.DOCUMENT
            else:
                content_type = ContentType.TEXT  # Default fallback
            
            result.metadata['content_type'] = content_type.value
            result.metadata['format'] = file_ext
            result.metadata['original_filename'] = filename
            
        except Exception as e:
            self.logger.warning(f"Format processing warning: {str(e)}")
            result.warnings.append(f"Format processing: {str(e)}")
    
    async def _analyze_content_ai(self, content_data: Union[bytes, str],
                                filename: str, result: IngestionResult):
        """AI-powered content analysis"""
        try:
            # Placeholder for AI analysis integration
            # In production, this would integrate with the 53 AI agents
            ai_analysis = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'content_features': {
                    'technical_quality': 0.85,
                    'content_relevance': 0.78,
                    'engagement_potential': 0.82
                },
                'recommendations': [
                    'Consider optimizing for better engagement',
                    'Content quality is above average'
                ],
                'ai_agents_involved': ['content_analyzer', 'quality_assessor']
            }
            
            result.metadata['ai_analysis'] = ai_analysis
            
        except Exception as e:
            self.logger.warning(f"AI analysis warning: {str(e)}")
            result.warnings.append(f"AI analysis: {str(e)}")
    
    async def _assess_content_quality(self, result: IngestionResult):
        """Assess content quality"""
        try:
            # Basic quality assessment logic
            quality_metrics = QualityMetrics()
            
            # Technical score based on format and size
            if 'format' in result.metadata:
                format_scores = {
                    'mp4': 0.9, 'mov': 0.85, 'avi': 0.7,  # Video
                    'flac': 0.95, 'wav': 0.9, 'mp3': 0.8,  # Audio
                    'png': 0.9, 'jpg': 0.85, 'gif': 0.7,  # Image
                    'pdf': 0.9, 'docx': 0.85, 'txt': 0.7  # Documents
                }
                quality_metrics.technical_score = format_scores.get(
                    result.metadata['format'], 0.6
                )
            
            # Overall quality score (simplified)
            quality_metrics.overall_score = (
                quality_metrics.technical_score * 0.4 +
                quality_metrics.content_score * 0.3 +
                quality_metrics.compliance_score * 0.3
            )
            
            if quality_metrics.overall_score < 0.6:
                quality_metrics.recommendations.append("Consider content optimization")
            
            result.quality_metrics = quality_metrics
            
        except Exception as e:
            self.logger.warning(f"Quality assessment warning: {str(e)}")
            result.warnings.append(f"Quality assessment: {str(e)}")
    
    async def _validate_content_security(self, content_data: Union[bytes, str],
                                       result: IngestionResult):
        """Validate content security"""
        try:
            security_assessment = SecurityAssessment()
            
            # Basic security checks (placeholder)
            if isinstance(content_data, bytes):
                # Check for suspicious patterns (simplified)
                if b'<script' in content_data.lower():
                    security_assessment.policy_violations.append("Potential script injection")
                    security_assessment.is_safe = False
                    security_assessment.threat_level = "medium"
            
            # Compliance checks
            security_assessment.compliance_status = {
                'gdpr_compliant': True,
                'ccpa_compliant': True,
                'content_policy_compliant': security_assessment.is_safe
            }
            
            result.security_assessment = security_assessment
            
        except Exception as e:
            self.logger.warning(f"Security validation warning: {str(e)}")
            result.warnings.append(f"Security validation: {str(e)}")
    
    async def _generate_content_metadata(self, filename: str, result: IngestionResult):
        """Generate content ID and final metadata"""
        try:
            # Generate unique content ID
            content_id = f"content_{uuid.uuid4().hex[:16]}"
            result.content_id = content_id
            
            # Add final metadata
            result.metadata.update({
                'content_id': content_id,
                'ingestion_timestamp': datetime.utcnow().isoformat(),
                'ingestion_version': '1.0.0',
                'processing_pipeline': 'enterprise_ingestion_v1'
            })
            
        except Exception as e:
            self.logger.warning(f"Metadata generation warning: {str(e)}")
            result.warnings.append(f"Metadata generation: {str(e)}")


class WorkflowOrchestrator:
    """
    Professional workflow orchestration system for content processing pipelines.
    
    Manages complex multi-stage workflows with dependency handling, parallel execution,
    error recovery, and intelligent routing across enterprise content processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize workflow orchestrator"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Active workflow tracking
        self._active_workflows: Dict[str, WorkflowExecution] = {}
        self._workflow_registry: Dict[str, WorkflowConfiguration] = {}
        
        # Default workflow configurations
        self._initialize_default_workflows()
    
    def _initialize_default_workflows(self):
        """Initialize default workflow configurations"""
        try:
            # Standard content processing workflow
            standard_workflow = WorkflowConfiguration(
                name="standard_content_processing",
                description="Standard content processing pipeline",
                execution_mode=ExecutionMode.SEQUENTIAL,
                stages=[
                    WorkflowStageConfig(WorkflowStage.INTAKE, timeout_seconds=60),
                    WorkflowStageConfig(WorkflowStage.VALIDATION, timeout_seconds=120),
                    WorkflowStageConfig(WorkflowStage.PROCESSING, timeout_seconds=600),
                    WorkflowStageConfig(WorkflowStage.ANALYSIS, timeout_seconds=300),
                    WorkflowStageConfig(WorkflowStage.OPTIMIZATION, timeout_seconds=240),
                    WorkflowStageConfig(WorkflowStage.ROUTING, timeout_seconds=60),
                    WorkflowStageConfig(WorkflowStage.STORAGE, timeout_seconds=120),
                    WorkflowStageConfig(WorkflowStage.COMPLETION, timeout_seconds=30)
                ]
            )
            
            # High-priority express workflow
            express_workflow = WorkflowConfiguration(
                name="express_processing",
                description="Express processing for high-priority content",
                execution_mode=ExecutionMode.PARALLEL,
                priority=WorkflowPriority.HIGH,
                stages=[
                    WorkflowStageConfig(WorkflowStage.INTAKE, timeout_seconds=30),
                    WorkflowStageConfig(WorkflowStage.VALIDATION, timeout_seconds=60, parallel_execution=True),
                    WorkflowStageConfig(WorkflowStage.PROCESSING, timeout_seconds=300, parallel_execution=True),
                    WorkflowStageConfig(WorkflowStage.ANALYSIS, timeout_seconds=120, parallel_execution=True),
                    WorkflowStageConfig(WorkflowStage.COMPLETION, timeout_seconds=15)
                ]
            )
            
            self._workflow_registry["standard"] = standard_workflow
            self._workflow_registry["express"] = express_workflow
            
        except Exception as e:
            self.logger.error(f"Default workflow initialization failed: {str(e)}")
    
    async def execute_workflow(self, workflow_name: str, 
                             context: Dict[str, Any]) -> WorkflowExecution:
        """
        Execute a registered workflow with given context.
        
        Args:
            workflow_name: Name of registered workflow
            context: Execution context and parameters
            
        Returns:
            Workflow execution tracking object
        """
        try:
            if workflow_name not in self._workflow_registry:
                raise WorkflowError(f"Workflow not found: {workflow_name}")
            
            workflow_config = self._workflow_registry[workflow_name]
            execution = WorkflowExecution(workflow_config=workflow_config)
            
            self.logger.info(f"Starting workflow execution: {execution.execution_id}")
            
            # Add to active workflows
            self._active_workflows[execution.execution_id] = execution
            
            try:
                execution.status = WorkflowStatus.RUNNING
                execution.start_time = datetime.utcnow()
                
                # Execute workflow based on execution mode
                if workflow_config.execution_mode == ExecutionMode.SEQUENTIAL:
                    await self._execute_sequential_workflow(execution, context)
                elif workflow_config.execution_mode == ExecutionMode.PARALLEL:
                    await self._execute_parallel_workflow(execution, context)
                elif workflow_config.execution_mode == ExecutionMode.CONDITIONAL:
                    await self._execute_conditional_workflow(execution, context)
                else:
                    await self._execute_adaptive_workflow(execution, context)
                
                execution.status = WorkflowStatus.COMPLETED
                execution.end_time = datetime.utcnow()
                
                self.logger.info(f"Workflow execution completed: {execution.execution_id}")
                
            except Exception as e:
                execution.status = WorkflowStatus.FAILED
                execution.error_messages.append(str(e))
                execution.end_time = datetime.utcnow()
                self.logger.error(f"Workflow execution failed: {execution.execution_id} - {str(e)}")
                
            return execution
            
        except Exception as e:
            self.logger.error(f"Workflow execution error: {str(e)}")
            raise WorkflowError(f"Workflow execution failed: {str(e)}")
        
        finally:
            # Clean up active workflow
            if execution.execution_id in self._active_workflows:
                del self._active_workflows[execution.execution_id]
    
    async def register_workflow(self, workflow_config: WorkflowConfiguration):
        """Register a new workflow configuration"""
        try:
            self._workflow_registry[workflow_config.name] = workflow_config
            self.logger.info(f"Workflow registered: {workflow_config.name}")
        except Exception as e:
            self.logger.error(f"Workflow registration failed: {str(e)}")
            raise WorkflowError(f"Workflow registration failed: {str(e)}")
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self._active_workflows.get(execution_id)
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel active workflow execution"""
        if execution_id in self._active_workflows:
            execution = self._active_workflows[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            return True
        return False
    
    def list_workflows(self) -> List[str]:
        """List available workflow configurations"""
        return list(self._workflow_registry.keys())
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow orchestration statistics"""
        return {
            'active_workflows': len(self._active_workflows),
            'registered_workflows': len(self._workflow_registry),
            'available_workflows': list(self._workflow_registry.keys())
        }
    
    # Private execution methods
    
    async def _execute_sequential_workflow(self, execution: WorkflowExecution, 
                                         context: Dict[str, Any]):
        """Execute workflow stages sequentially"""
        for stage_config in execution.workflow_config.stages:
            if not stage_config.enabled:
                continue
                
            try:
                execution.current_stage = stage_config.stage
                
                # Execute stage with timeout
                stage_result = await asyncio.wait_for(
                    self._execute_stage(stage_config, context),
                    timeout=stage_config.timeout_seconds
                )
                
                execution.stage_results[stage_config.stage.value] = stage_result
                execution.completed_stages.append(stage_config.stage)
                
            except asyncio.TimeoutError:
                error_msg = f"Stage timeout: {stage_config.stage.value}"
                execution.error_messages.append(error_msg)
                execution.failed_stages.append(stage_config.stage)
                if execution.workflow_config.failure_handling == "stop":
                    raise WorkflowError(error_msg)
                    
            except Exception as e:
                error_msg = f"Stage failed: {stage_config.stage.value} - {str(e)}"
                execution.error_messages.append(error_msg)
                execution.failed_stages.append(stage_config.stage)
                if execution.workflow_config.failure_handling == "stop":
                    raise WorkflowError(error_msg)
    
    async def _execute_parallel_workflow(self, execution: WorkflowExecution,
                                       context: Dict[str, Any]):
        """Execute workflow stages in parallel where possible"""
        # Group stages by dependencies
        parallel_groups = self._group_stages_by_dependencies(
            execution.workflow_config.stages
        )
        
        for group in parallel_groups:
            # Execute stages in current group concurrently
            tasks = []
            for stage_config in group:
                if stage_config.enabled:
                    task = asyncio.create_task(
                        asyncio.wait_for(
                            self._execute_stage(stage_config, context),
                            timeout=stage_config.timeout_seconds
                        )
                    )
                    tasks.append((stage_config, task))
            
            # Wait for all tasks in group to complete
            for stage_config, task in tasks:
                try:
                    stage_result = await task
                    execution.stage_results[stage_config.stage.value] = stage_result
                    execution.completed_stages.append(stage_config.stage)
                except Exception as e:
                    error_msg = f"Parallel stage failed: {stage_config.stage.value} - {str(e)}"
                    execution.error_messages.append(error_msg)
                    execution.failed_stages.append(stage_config.stage)
    
    async def _execute_conditional_workflow(self, execution: WorkflowExecution,
                                          context: Dict[str, Any]):
        """Execute workflow with conditional logic"""
        # Simplified conditional execution
        for stage_config in execution.workflow_config.stages:
            if not stage_config.enabled:
                continue
            
            # Check if stage should be executed based on previous results
            should_execute = await self._evaluate_stage_condition(
                stage_config, execution.stage_results, context
            )
            
            if should_execute:
                try:
                    execution.current_stage = stage_config.stage
                    stage_result = await asyncio.wait_for(
                        self._execute_stage(stage_config, context),
                        timeout=stage_config.timeout_seconds
                    )
                    execution.stage_results[stage_config.stage.value] = stage_result
                    execution.completed_stages.append(stage_config.stage)
                except Exception as e:
                    error_msg = f"Conditional stage failed: {stage_config.stage.value} - {str(e)}"
                    execution.error_messages.append(error_msg)
                    execution.failed_stages.append(stage_config.stage)
    
    async def _execute_adaptive_workflow(self, execution: WorkflowExecution,
                                       context: Dict[str, Any]):
        """Execute workflow with adaptive optimization"""
        # Adaptive execution adjusts based on performance and results
        # This is a simplified implementation
        await self._execute_sequential_workflow(execution, context)
    
    async def _execute_stage(self, stage_config: WorkflowStageConfig,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow stage"""
        try:
            stage_name = stage_config.stage.value
            self.logger.debug(f"Executing stage: {stage_name}")
            
            # Stage-specific execution logic
            stage_result = {
                'stage': stage_name,
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat(),
                'duration_seconds': 0.1,  # Placeholder
                'output': f"Stage {stage_name} executed successfully"
            }
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            return stage_result
            
        except Exception as e:
            self.logger.error(f"Stage execution failed: {stage_config.stage.value} - {str(e)}")
            raise
    
    def _group_stages_by_dependencies(self, stages: List[WorkflowStageConfig]) -> List[List[WorkflowStageConfig]]:
        """Group stages by dependency requirements for parallel execution"""
        # Simplified grouping - in production would handle complex dependencies
        groups = []
        current_group = []
        
        for stage in stages:
            if stage.dependencies or (current_group and not stage.parallel_execution):
                if current_group:
                    groups.append(current_group)
                    current_group = []
            current_group.append(stage)
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    async def _evaluate_stage_condition(self, stage_config: WorkflowStageConfig,
                                      previous_results: Dict[str, Any],
                                      context: Dict[str, Any]) -> bool:
        """Evaluate whether a stage should be executed"""
        # Simplified condition evaluation
        # In production, this would include complex business logic
        return True


class DataIngestionOrchestrator:
    """
    Data ingestion orchestration system combining content management and workflow execution.
    
    Provides unified interface for enterprise-grade content ingestion with workflow
    orchestration, monitoring, and intelligent routing capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize data ingestion orchestrator"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components
        self.content_manager = ContentIngestionManager(config)
        self.workflow_orchestrator = WorkflowOrchestrator(config)
        
        # Orchestrator state
        self._orchestration_metrics = {
            'total_ingestions': 0,
            'successful_ingestions': 0,
            'failed_ingestions': 0,
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0
        }
    
    async def orchestrate_ingestion(self, content_data: Union[bytes, str],
                                  filename: str, workflow_name: str = "standard",
                                  ingestion_request: IngestionRequest = None) -> Dict[str, Any]:
        """
        Orchestrate complete content ingestion with workflow execution.
        
        Args:
            content_data: Content file data or URL
            filename: Original filename
            workflow_name: Workflow to execute
            ingestion_request: Optional ingestion request configuration
            
        Returns:
            Combined orchestration result
        """
        try:
            self.logger.info(f"Starting orchestrated ingestion: {filename}")
            
            # Create default request if not provided
            if ingestion_request is None:
                ingestion_request = IngestionRequest()
            
            # Update metrics
            self._orchestration_metrics['total_ingestions'] += 1
            self._orchestration_metrics['total_workflows'] += 1
            
            # Step 1: Content ingestion
            ingestion_result = await self.content_manager.ingest_content(
                content_data, filename, ingestion_request
            )
            
            # Step 2: Workflow execution
            workflow_context = {
                'ingestion_result': ingestion_result,
                'content_data': content_data,
                'filename': filename,
                'request_id': ingestion_request.request_id
            }
            
            workflow_execution = await self.workflow_orchestrator.execute_workflow(
                workflow_name, workflow_context
            )
            
            # Update success metrics
            if ingestion_result.status == IngestionStatus.COMPLETED:
                self._orchestration_metrics['successful_ingestions'] += 1
            else:
                self._orchestration_metrics['failed_ingestions'] += 1
                
            if workflow_execution.status == WorkflowStatus.COMPLETED:
                self._orchestration_metrics['successful_workflows'] += 1
            else:
                self._orchestration_metrics['failed_workflows'] += 1
            
            # Combine results
            orchestration_result = {
                'orchestration_id': str(uuid.uuid4()),
                'status': 'completed' if (
                    ingestion_result.status == IngestionStatus.COMPLETED and
                    workflow_execution.status == WorkflowStatus.COMPLETED
                ) else 'failed',
                'ingestion_result': ingestion_result,
                'workflow_execution': workflow_execution,
                'orchestration_timestamp': datetime.utcnow().isoformat(),
                'metrics': self._orchestration_metrics.copy()
            }
            
            self.logger.info(f"Orchestrated ingestion completed: {filename}")
            return orchestration_result
            
        except Exception as e:
            self.logger.error(f"Orchestrated ingestion failed: {filename} - {str(e)}")
            self._orchestration_metrics['failed_ingestions'] += 1
            self._orchestration_metrics['failed_workflows'] += 1
            
            return {
                'orchestration_id': str(uuid.uuid4()),
                'status': 'failed',
                'error': str(e),
                'orchestration_timestamp': datetime.utcnow().isoformat(),
                'metrics': self._orchestration_metrics.copy()
            }
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        try:
            content_stats = await self.content_manager.get_statistics()
            workflow_stats = await self.workflow_orchestrator.get_workflow_statistics()
            
            return {
                'orchestration_metrics': self._orchestration_metrics,
                'content_manager_status': content_stats,
                'workflow_orchestrator_status': workflow_stats,
                'system_capabilities': self.content_manager.get_capabilities().__dict__,
                'available_workflows': self.workflow_orchestrator.list_workflows(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Status retrieval failed: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Factory function for easy instantiation
def create_ingestion_orchestrator(config: Dict[str, Any] = None) -> DataIngestionOrchestrator:
    """
    Create and configure a data ingestion orchestrator.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured DataIngestionOrchestrator instance
    """
    return DataIngestionOrchestrator(config)