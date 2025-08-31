"""🎯 Quality Control Index - Entry Point & System Orchestration

Main entry point for the Quality Control System providing unified access
to all quality management components with intelligent routing and coordination.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import uuid

# Import all quality control components
from .controller import QualityController
from .validator import AudioQualityValidator, ValidationResult
from .monitor import QualityMonitor, QualityAlert
from .standards import QualityStandardsManager, QualityProfile, QualityLevel
from .metrics import QualityMetrics, QualityReport
from .gates import QualityGateManager, QualityGateResult
from .optimization import QualityOptimizer, OptimizationResult
from .compliance import PlatformComplianceManager, ComplianceReport
from .dashboard import RealTimeDashboard, DashboardData

logger = logging.getLogger(__name__)


@dataclass
class QualityControlConfig:
    """Quality Control System Configuration"""    enable_real_time_monitoring: bool = True
    enable_optimization: bool = True
    enable_compliance_checking: bool = True
    enable_dashboard: bool = True
    default_quality_level: QualityLevel = QualityLevel.HIGH
    processing_timeout: int = 300  # seconds
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    max_concurrent_processes: int = 10
    log_level: str = "INFO"
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "quality_score": 0.6,
        "processing_time": 60.0,
        "error_rate": 0.1
    })


@dataclass
class ProcessingRequest:
    """Audio processing request"""    request_id: str
    audio_file: str
    quality_profile: Optional[str] = None
    platforms: List[str] = field(default_factory=list)
    enable_optimization: bool = True
    enable_compliance: bool = True
    priority: int = 1  # 1 = highest
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingResult:
    """Complete processing result"""    request_id: str
    success: bool
    audio_file: str
    quality_report: Optional[QualityReport] = None
    optimization_results: List[OptimizationResult] = field(default_factory=list)
    compliance_reports: Dict[str, ComplianceReport] = field(default_factory=dict)
    gate_results: List[QualityGateResult] = field(default_factory=list)
    alerts: List[QualityAlert] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: str = ""
    processed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityControlSystem:
    """    🎯 Quality Control System - Master Orchestrator
    
    Complete audio quality management system providing:
    - Unified quality assessment and optimization
    - Real-time monitoring and alerting
    - Multi-platform compliance management
    - Interactive dashboard and reporting
    - Intelligent routing and decision making
    """    def __init__(self, config: Optional[QualityControlConfig] = None):
        self.config = config or QualityControlConfig()
        self.system_id = str(uuid.uuid4())
        
        # Core components
        self.controller: Optional[QualityController] = None
        self.validator: Optional[AudioQualityValidator] = None
        self.monitor: Optional[QualityMonitor] = None
        self.standards_manager: Optional[QualityStandardsManager] = None
        self.metrics: Optional[QualityMetrics] = None
        self.gate_manager: Optional[QualityGateManager] = None
        self.optimizer: Optional[QualityOptimizer] = None
        self.compliance_manager: Optional[PlatformComplianceManager] = None
        self.dashboard: Optional[RealTimeDashboard] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.processing_queue: List[ProcessingRequest] = []
        self.active_processes: Dict[str, ProcessingRequest] = {}
        self.processing_history: List[ProcessingResult] = []
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_processed = 0
        self.total_errors = 0
        
        logger.info(f"QualityControlSystem created with ID: {self.system_id}")

    async def initialize(self) -> bool:
        """Initialize all system components"""        
        if self.is_initialized:
            logger.warning("System already initialized")
            return True
        
        try:
            logger.info("Initializing Quality Control System...")
            
            # Configure logging
            logging.getLogger().setLevel(getattr(logging, self.config.log_level))
            
            # Initialize core components in dependency order
            await self._initialize_standards_manager()
            await self._initialize_validator()
            await self._initialize_metrics()
            await self._initialize_gate_manager()
            await self._initialize_monitor()
            await self._initialize_controller()
            
            # Initialize optional components
            if self.config.enable_optimization:
                await self._initialize_optimizer()
            
            if self.config.enable_compliance_checking:
                await self._initialize_compliance_manager()
            
            if self.config.enable_dashboard:
                await self._initialize_dashboard()
            
            self.is_initialized = True
            logger.info("Quality Control System initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Quality Control System: {e}")
            return False

    async def _initialize_standards_manager(self):
        """Initialize quality standards manager"""        self.standards_manager = QualityStandardsManager()
        logger.debug("Quality Standards Manager initialized")

    async def _initialize_validator(self):
        """Initialize audio quality validator"""        self.validator = AudioQualityValidator(self.standards_manager)
        logger.debug("Audio Quality Validator initialized")

    async def _initialize_metrics(self):
        """Initialize quality metrics system"""        self.metrics = QualityMetrics()
        logger.debug("Quality Metrics system initialized")

    async def _initialize_gate_manager(self):
        """Initialize quality gate manager"""        self.gate_manager = QualityGateManager()
        logger.debug("Quality Gate Manager initialized")

    async def _initialize_monitor(self):
        """Initialize quality monitor"""        if self.config.enable_real_time_monitoring:
            self.monitor = QualityMonitor()
            # Configure alert thresholds
            for metric, threshold in self.config.alert_thresholds.items():
                await self.monitor.set_alert_threshold(metric, threshold)
            logger.debug("Quality Monitor initialized")

    async def _initialize_controller(self):
        """Initialize quality controller"""        self.controller = QualityController(
            validator=self.validator,
            standards_manager=self.standards_manager,
            metrics=self.metrics,
            gate_manager=self.gate_manager,
            monitor=self.monitor
        )
        logger.debug("Quality Controller initialized")

    async def _initialize_optimizer(self):
        """Initialize quality optimizer"""        self.optimizer = QualityOptimizer()
        logger.debug("Quality Optimizer initialized")

    async def _initialize_compliance_manager(self):
        """Initialize compliance manager"""        self.compliance_manager = PlatformComplianceManager()
        logger.debug("Platform Compliance Manager initialized")

    async def _initialize_dashboard(self):
        """Initialize real-time dashboard"""        if all([self.controller, self.monitor, self.compliance_manager, self.optimizer]):
            self.dashboard = RealTimeDashboard(
                quality_controller=self.controller,
                quality_monitor=self.monitor,
                compliance_manager=self.compliance_manager,
                quality_optimizer=self.optimizer
            )
            logger.debug("Real-time Dashboard initialized")
        else:
            logger.warning("Cannot initialize dashboard - missing required components")

    async def start(self) -> bool:
        """Start the quality control system"""        
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                return False
        
        if self.is_running:
            logger.warning("System already running")
            return True
        
        try:
            logger.info("Starting Quality Control System...")
            
            # Start monitoring if enabled
            if self.monitor and self.config.enable_real_time_monitoring:
                await self.monitor.start_monitoring()
            
            # Start processing queue handler
            asyncio.create_task(self._process_queue_handler())
            
            self.is_running = True
            logger.info("Quality Control System started successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Quality Control System: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the quality control system"""        
        if not self.is_running:
            logger.warning("System not running")
            return True
        
        try:
            logger.info("Stopping Quality Control System...")
            
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            # Wait for active processes to complete
            while self.active_processes:
                await asyncio.sleep(1)
                logger.info(f"Waiting for {len(self.active_processes)} active processes to complete...")
            
            self.is_running = False
            logger.info("Quality Control System stopped successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Quality Control System: {e}")
            return False

    async def process_audio(
        self,
        audio_file: str,
        quality_profile: Optional[str] = None,
        platforms: List[str] = None,
        enable_optimization: bool = None,
        enable_compliance: bool = None,
        priority: int = 1
    ) -> ProcessingResult:
        """Process audio file through complete quality control pipeline"""        
        if not self.is_running:
            return ProcessingResult(
                request_id="",
                success=False,
                audio_file=audio_file,
                error_message="Quality Control System not running"
            )
        
        # Create processing request
        request = ProcessingRequest(
            request_id=str(uuid.uuid4()),
            audio_file=audio_file,
            quality_profile=quality_profile,
            platforms=platforms or [],
            enable_optimization=enable_optimization if enable_optimization is not None else self.config.enable_optimization,
            enable_compliance=enable_compliance if enable_compliance is not None else self.config.enable_compliance_checking,
            priority=priority
        )
        
        logger.info(f"Processing audio: {audio_file} (Request ID: {request.request_id})")
        
        return await self._process_request(request)

    async def _process_request(self, request: ProcessingRequest) -> ProcessingResult:
        """Process individual request"""        
        start_time = datetime.now()
        self.active_processes[request.request_id] = request
        
        try:
            result = ProcessingResult(
                request_id=request.request_id,
                success=False,
                audio_file=request.audio_file
            )
            
            # Step 1: Quality Assessment
            quality_report = await self._assess_quality(request)
            if quality_report:
                result.quality_report = quality_report
                logger.debug(f"Quality assessment completed for {request.audio_file}")
            else:
                result.error_message = "Quality assessment failed"
                return result
            
            # Step 2: Quality Gates
            gate_results = await self._check_quality_gates(quality_report, request)
            result.gate_results = gate_results
            
            # Step 3: Optimization (if enabled and needed)
            if request.enable_optimization and self.optimizer:
                optimization_results = await self._optimize_audio(request, quality_report)
                result.optimization_results = optimization_results
                logger.debug(f"Optimization completed for {request.audio_file}")
            
            # Step 4: Compliance Checking (if enabled)
            if request.enable_compliance and self.compliance_manager and request.platforms:
                compliance_reports = await self._check_compliance(request, quality_report)
                result.compliance_reports = compliance_reports
                logger.debug(f"Compliance checking completed for {request.audio_file}")
            
            # Step 5: Alert Generation
            alerts = await self._generate_alerts(quality_report, gate_results)
            result.alerts = alerts
            
            result.success = True
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self.total_processed += 1
            
            logger.info(f"Successfully processed {request.audio_file} in {result.processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing {request.audio_file}: {e}")
            result = ProcessingResult(
                request_id=request.request_id,
                success=False,
                audio_file=request.audio_file,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            self.total_errors += 1
        
        finally:
            # Cleanup
            if request.request_id in self.active_processes:
                del self.active_processes[request.request_id]
            
            # Store in history
            self.processing_history.append(result)
            
            # Limit history size
            if len(self.processing_history) > 1000:
                self.processing_history = self.processing_history[-1000:]
        
        return result

    async def _assess_quality(self, request: ProcessingRequest) -> Optional[QualityReport]:
        """Assess audio quality"""        
        if not self.controller:
            return None
        
        # Get quality profile
        profile = None
        if request.quality_profile and self.standards_manager:
            profile = self.standards_manager.get_profile(request.quality_profile)
        
        if not profile and self.standards_manager:
            profile = self.standards_manager.get_profile_by_level(self.config.default_quality_level)
        
        # Perform quality assessment
        return await self.controller.assess_quality(
            request.audio_file,
            profile
        )

    async def _check_quality_gates(
        self,
        quality_report: QualityReport,
        request: ProcessingRequest
    ) -> List[QualityGateResult]:
        """Check quality gates"""        
        if not self.gate_manager:
            return []
        
        return await self.gate_manager.check_all_gates(quality_report)

    async def _optimize_audio(
        self,
        request: ProcessingRequest,
        quality_report: QualityReport
    ) -> List[OptimizationResult]:
        """Optimize audio quality"""        
        if not self.optimizer:
            return []
        
        try:
            # Load audio data (simplified - would need actual audio loading)
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Audio optimization failed for {request.audio_file}: {e}")
            return []

    async def _check_compliance(
        self,
        request: ProcessingRequest,
        quality_report: QualityReport
    ) -> Dict[str, ComplianceReport]:
        """Check platform compliance"""        
        if not self.compliance_manager:
            return {}
        
        compliance_reports = {}
        
        for platform in request.platforms:
            try:
                report = await self.compliance_manager.check_compliance(
                    platform,
                    quality_report,
                    request.audio_file
                )
                compliance_reports[platform] = report
                
            except Exception as e:
                logger.error(f"Compliance check failed for platform {platform}: {e}")
                continue
        
        return compliance_reports

    async def _generate_alerts(
        self,
        quality_report: QualityReport,
        gate_results: List[QualityGateResult]
    ) -> List[QualityAlert]:
        """Generate quality alerts"""        
        if not self.monitor:
            return []
        
        alerts = []
        
        # Check for failed gates
        for gate_result in gate_results:
            if not gate_result.passed:
                alert = QualityAlert(
                    alert_id=str(uuid.uuid4()),
                    source="quality_gate",
                    severity="warning" if gate_result.gate.gate_type == "threshold" else "critical",
                    message=f"Quality gate failed: {gate_result.gate.name}",
                    details={
                        "gate_name": gate_result.gate.name,
                        "expected": gate_result.gate.threshold,
                        "actual": gate_result.actual_value,
                        "difference": gate_result.difference
                    }
                )
                alerts.append(alert)
        
        return alerts

    async def _process_queue_handler(self):
        """Background task to process queued requests"""        
        while self.is_running:
            try:
                if self.processing_queue and len(self.active_processes) < self.config.max_concurrent_processes:
                    # Sort by priority
                    self.processing_queue.sort(key=lambda x: x.priority)
                    request = self.processing_queue.pop(0)
                    
                    # Process in background
                    asyncio.create_task(self._process_request(request))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in queue handler: {e}")
                await asyncio.sleep(1)

    def queue_request(self, request: ProcessingRequest):
        """Add request to processing queue"""        self.processing_queue.append(request)
        logger.info(f"Queued request {request.request_id} for {request.audio_file}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "system_id": self.system_id,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "total_processed": self.total_processed,
            "total_errors": self.total_errors,
            "success_rate": (self.total_processed - self.total_errors) / max(self.total_processed, 1),
            "active_processes": len(self.active_processes),
            "queued_requests": len(self.processing_queue),
            "components": {
                "controller": self.controller is not None,
                "validator": self.validator is not None,
                "monitor": self.monitor is not None,
                "standards_manager": self.standards_manager is not None,
                "metrics": self.metrics is not None,
                "gate_manager": self.gate_manager is not None,
                "optimizer": self.optimizer is not None,
                "compliance_manager": self.compliance_manager is not None,
                "dashboard": self.dashboard is not None
            },
            "config": {
                "enable_real_time_monitoring": self.config.enable_real_time_monitoring,
                "enable_optimization": self.config.enable_optimization,
                "enable_compliance_checking": self.config.enable_compliance_checking,
                "enable_dashboard": self.config.enable_dashboard,
                "max_concurrent_processes": self.config.max_concurrent_processes
            }
        }

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing performance statistics"""        
        if not self.processing_history:
            return {"no_data": True}
        
        successful_processes = [p for p in self.processing_history if p.success]
        failed_processes = [p for p in self.processing_history if not p.success]
        
        processing_times = [p.processing_time for p in successful_processes]
        
        stats = {
            "total_processed": len(self.processing_history),
            "successful": len(successful_processes),
            "failed": len(failed_processes),
            "success_rate": len(successful_processes) / max(len(self.processing_history), 1),
            "average_processing_time": sum(processing_times) / max(len(processing_times), 1),
            "min_processing_time": min(processing_times) if processing_times else 0.0,
            "max_processing_time": max(processing_times) if processing_times else 0.0,
            "files_per_hour": len(successful_processes) / max((datetime.now() - self.start_time).total_seconds() / 3600, 0.001)
        }
        
        return stats

    async def get_dashboard_data(self) -> Optional[DashboardData]:
        """Get dashboard data if dashboard is enabled"""        
        if not self.dashboard:
            return None
        
        return await self.dashboard.get_dashboard_data()

    def get_active_alerts(self) -> List[QualityAlert]:
        """Get all active quality alerts"""        
        if not self.monitor:
            return []
        
        return self.monitor.get_active_alerts()

    async def shutdown(self):
        """Graceful system shutdown"""        
        logger.info("Initiating Quality Control System shutdown...")
        
        # Stop the system
        await self.stop()
        
        # Clear resources
        self.processing_queue.clear()
        self.active_processes.clear()
        
        logger.info("Quality Control System shutdown completed")


# Convenience functions for quick system access

async def create_quality_control_system(config: Optional[QualityControlConfig] = None) -> QualityControlSystem:
    """Create and initialize a Quality Control System"""    
    system = QualityControlSystem(config)
    success = await system.initialize()
    
    if not success:
        raise RuntimeError("Failed to initialize Quality Control System")
    
    return system


async def quick_quality_check(
    audio_file: str,
    quality_level: QualityLevel = QualityLevel.HIGH,
    platforms: List[str] = None
) -> ProcessingResult:
    """Quick quality check for single audio file"""    
    config = QualityControlConfig(
        enable_real_time_monitoring=False,
        enable_dashboard=False,
        default_quality_level=quality_level
    )
    
    system = await create_quality_control_system(config)
    
    try:
        await system.start()
        result = await system.process_audio(
            audio_file=audio_file,
            platforms=platforms or []
        )
        return result
        
    finally:
        await system.shutdown()


# System factory for different use cases

class QualityControlFactory:
    """Factory for creating pre-configured Quality Control Systems"""    
    @staticmethod
    async def create_streaming_system() -> QualityControlSystem:
        """Create system optimized for streaming platforms"""        
        config = QualityControlConfig(
            enable_real_time_monitoring=True,
            enable_optimization=True,
            enable_compliance_checking=True,
            enable_dashboard=True,
            default_quality_level=QualityLevel.HIGH,
            max_concurrent_processes=20,
            alert_thresholds={
                "quality_score": 0.8,
                "processing_time": 30.0,
                "error_rate": 0.05
            }
        )
        
        return await create_quality_control_system(config)
    
    @staticmethod
    async def create_broadcast_system() -> QualityControlSystem:
        """Create system optimized for broadcast quality"""        
        config = QualityControlConfig(
            enable_real_time_monitoring=True,
            enable_optimization=True,
            enable_compliance_checking=True,
            enable_dashboard=True,
            default_quality_level=QualityLevel.PREMIUM,
            max_concurrent_processes=10,
            alert_thresholds={
                "quality_score": 0.9,
                "processing_time": 60.0,
                "error_rate": 0.01
            }
        )
        
        return await create_quality_control_system(config)
    
    @staticmethod
    async def create_mastering_system() -> QualityControlSystem:
        """Create system optimized for mastering quality"""        
        config = QualityControlConfig(
            enable_real_time_monitoring=True,
            enable_optimization=True,
            enable_compliance_checking=True,
            enable_dashboard=True,
            default_quality_level=QualityLevel.MASTERED,
            max_concurrent_processes=5,
            processing_timeout=600,  # 10 minutes for mastering
            alert_thresholds={
                "quality_score": 0.95,
                "processing_time": 120.0,
                "error_rate": 0.001
            }
        )
        
        return await create_quality_control_system(config)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create system
        system = await QualityControlFactory.create_streaming_system()
        
        try:
            # Start system
            await system.start()
            
            # Process audio
            result = await system.process_audio(
                audio_file="example.wav",
                platforms=["spotify", "youtube", "tiktok"]
            )
            
            print(f"Processing result: {result.success}")
            print(f"Quality score: {result.quality_report.overall_score if result.quality_report else 'N/A'}")
            
        finally:
            # Shutdown
            await system.shutdown()
    
    # Run example
    asyncio.run(main())
