"""
Adaptive Streaming AI Controller

Copyright (c) 2025 Fahed Mlaiel
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class AdaptiveStreamingAIMode(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class ProcessingStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AdaptationMode(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"


class NetworkCondition(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class StreamingQuality(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    AUTO = "auto"


class ControllerStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ADAPTING = "adapting"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class AdaptiveStreamingAIConfig:
    config_id: str
    enabled: bool = True
    priority: PriorityLevel = PriorityLevel.MEDIUM
    max_concurrent: int = 10
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptiveStreamingAIResult:
    result_id: str
    status: ProcessingStatus
    data: Dict[str, Any]
    confidence: float = 0.0
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptiveStreamingAIMetrics:
    adaptation_count: int = 0
    quality_score: float = 0.0
    latency_ms: float = 0.0
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptiveStreamingConfig:
    mode: AdaptationMode
    target_quality: StreamingQuality
    adaptation_threshold: float = 0.3
    enable_auto_adaptation: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkMetrics:
    bandwidth_mbps: float
    latency_ms: float
    packet_loss_pct: float
    jitter_ms: float
    condition: NetworkCondition
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StreamingMetrics:
    bitrate_kbps: float
    resolution: str
    framerate: int
    quality: StreamingQuality
    buffer_health_pct: float
    dropped_frames: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptationDecision:
    decision_id: str
    network_condition: NetworkCondition
    target_quality: StreamingQuality
    target_bitrate: float
    adaptation_reason: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceOptimization:
    optimization_id: str
    optimization_type: str
    current_performance: float
    target_performance: float
    actions_taken: List[str]
    improvement_pct: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptiveStreamingAIRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    stream_id: str = ""
    config: Optional[AdaptiveStreamingConfig] = None
    network_metrics: List[NetworkMetrics] = field(default_factory=list)
    streaming_metrics: List[StreamingMetrics] = field(default_factory=list)
    adaptation_decisions: List[AdaptationDecision] = field(default_factory=list)
    optimizations: List[PerformanceOptimization] = field(default_factory=list)
    status: ControllerStatus = ControllerStatus.ACTIVE
    total_adaptations: int = 0
    average_quality_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptiveStreamingAIControllerRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    controller_id: str = ""
    total_adaptations: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class AdaptiveStreamingAIController:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_processes: Dict[str, Dict[str, Any]] = {}
        self.completed_processes: Dict[str, Dict[str, Any]] = {}
        self.total_processed = 0
        self.logger = logging.getLogger(__name__)
    
    async def start_processing(self, input_data: Dict[str, Any]) -> str:
        process_id = str(uuid4())
        self.active_processes[process_id] = {
            "status": ProcessingStatus.PROCESSING,
            "data": input_data,
            "started_at": datetime.utcnow()
        }
        asyncio.create_task(self._process_async(process_id, input_data))
        return process_id
    
    async def get_status(self, process_id: str) -> Optional[ProcessingStatus]:
        process = self.active_processes.get(process_id)
        return process["status"] if process else None
    
    async def _process_async(self, process_id: str, input_data: Dict[str, Any]) -> None:
        try:
            await asyncio.sleep(0.1)
            result = {"status": "success", "data": input_data}
            self.active_processes[process_id]["status"] = ProcessingStatus.COMPLETED
            self.completed_processes[process_id] = {"results": [result]}
            self.total_processed += 1
        except Exception as e:
            self.active_processes[process_id]["status"] = ProcessingStatus.FAILED
            self.active_processes[process_id]["error"] = str(e)


def create_adaptivestreamingai_controller(config: Optional[Dict[str, Any]] = None) -> AdaptiveStreamingAIController:
    return AdaptiveStreamingAIController(config=config)


create_adaptive_streaming_ai_controller = create_adaptivestreamingai_controller


__all__ = [
    "AdaptiveStreamingAIController",
    "AdaptiveStreamingAIMode",
    "ProcessingStatus",
    "PriorityLevel",
    "AdaptationMode",
    "NetworkCondition",
    "StreamingQuality",
    "ControllerStatus",
    "AdaptiveStreamingAIConfig",
    "AdaptiveStreamingAIResult",
    "AdaptiveStreamingAIMetrics",
    "AdaptiveStreamingConfig",
    "NetworkMetrics",
    "StreamingMetrics",
    "AdaptationDecision",
    "PerformanceOptimization",
    "AdaptiveStreamingAIRecord",
    "AdaptiveStreamingAIControllerRecord",
    "create_adaptivestreamingai_controller",
    "create_adaptive_streaming_ai_controller"
]
