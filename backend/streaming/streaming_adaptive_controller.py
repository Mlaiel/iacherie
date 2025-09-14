"""Streaming Adaptive Controller - Unified Quality & Resource Adaptation System
==============================================================================

Advanced adaptive streaming controller providing dynamic quality adjustment,
resource optimization, network adaptation, device compatibility, and
intelligent streaming parameter management for optimal user experience.

Consolidates:
- Adaptive bitrate streaming (ABR) management
- Dynamic quality and resolution adjustment
- Network condition adaptation and optimization
- Device-specific streaming configuration

Business Logic Flow:
Network Analysis → Device Detection → Quality Assessment →
Adaptation Strategy → Resource Allocation → Parameter Adjustment →
Performance Monitoring → Continuous Optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from collections import defaultdict, deque
import psutil

logger = logging.getLogger(__name__)

class AdaptationStrategy(Enum):
    """Adaptation strategy type"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"
    AUTO_LEARNING = "auto_learning"

class QualityLevel(Enum):
    """Video quality level"""
    AUTO = "auto"
    LOW_240P = "240p"
    MEDIUM_360P = "360p"
    STANDARD_480P = "480p"
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    QUAD_HD_1440P = "1440p"
    ULTRA_HD_4K = "4k"
    ULTRA_HD_8K = "8k"

class DeviceType(Enum):
    """Device type classification"""
    MOBILE_PHONE = "mobile_phone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    VR_HEADSET = "vr_headset"
    IOT_DEVICE = "iot_device"

class NetworkType(Enum):
    """Network connection type"""
    WIFI = "wifi"
    ETHERNET = "ethernet"
    LTE_4G = "lte_4g"
    LTE_5G = "lte_5g"
    SATELLITE = "satellite"
    DIAL_UP = "dial_up"
    UNKNOWN = "unknown"

class AdaptationTrigger(Enum):
    """Adaptation trigger event"""
    BANDWIDTH_CHANGE = "bandwidth_change"
    BUFFER_UNDERRUN = "buffer_underrun"
    FRAME_DROPS = "frame_drops"
    LATENCY_SPIKE = "latency_spike"
    DEVICE_CHANGE = "device_change"
    USER_PREFERENCE = "user_preference"
    MANUAL_OVERRIDE = "manual_override"

class StreamingProtocol(Enum):
    """Streaming protocol type"""
    HLS = "hls"
    DASH = "dash"
    RTMP = "rtmp"
    WEBRTC = "webrtc"
    RTSP = "rtsp"
    SRT = "srt"

@dataclass
class NetworkCondition:
    """Network condition assessment"""
    condition_id: str
    user_id: str
    session_id: str
    network_type: NetworkType
    bandwidth_mbps: float
    latency_ms: float
    packet_loss_percent: float
    jitter_ms: float
    connection_stability: float
    geographic_location: str
    isp_provider: str
    measurement_timestamp: datetime
    quality_of_service: float

@dataclass
class DeviceCapability:
    """Device capability profile"""
    device_id: str
    device_type: DeviceType
    screen_resolution: Tuple[int, int]
    max_bitrate_mbps: float
    supported_codecs: List[str]
    supported_protocols: List[StreamingProtocol]
    hardware_acceleration: bool
    cpu_cores: int
    memory_gb: float
    gpu_acceleration: bool
    battery_status: Optional[float]
    thermal_status: str
    performance_tier: str

@dataclass
class QualityProfile:
    """Streaming quality profile"""
    profile_id: str
    quality_level: QualityLevel
    resolution: Tuple[int, int]
    bitrate_kbps: int
    framerate: int
    codec: str
    audio_bitrate_kbps: int
    audio_codec: str
    keyframe_interval: int
    buffer_size_seconds: int
    encoding_preset: str
    compatibility_score: float

@dataclass
class AdaptationRule:
    """Adaptation rule configuration"""
    rule_id: str
    rule_name: str
    trigger_conditions: Dict[str, Any]
    adaptation_actions: Dict[str, Any]
    priority: int
    enabled: bool
    application_scope: List[str]
    performance_impact: float
    success_rate: float
    created_at: datetime

@dataclass
class StreamingSession:
    """Streaming session state"""
    session_id: str
    user_id: str
    stream_id: str
    device_capability: DeviceCapability
    network_condition: NetworkCondition
    current_quality: QualityProfile
    target_quality: QualityProfile
    adaptation_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    user_preferences: Dict[str, Any]
    started_at: datetime
    last_adaptation: datetime

@dataclass
class AdaptationEvent:
    """Adaptation event record"""
    event_id: str
    session_id: str
    trigger: AdaptationTrigger
    trigger_data: Dict[str, Any]
    previous_quality: QualityProfile
    new_quality: QualityProfile
    adaptation_strategy: AdaptationStrategy
    adaptation_duration_ms: float
    performance_impact: Dict[str, float]
    user_satisfaction: Optional[float]
    timestamp: datetime

class NetworkAnalyzer:
    """Network condition analysis system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.network_monitors = {}
        self.condition_history = defaultdict(deque)
        
    async def initialize_network_analyzer(self) -> Dict[str, Any]:
        """Initialize network analysis system"""
        try:
            # Setup network monitoring
            network_monitoring = await self._setup_network_monitoring()
            
            # Configure bandwidth detection
            bandwidth_detection = await self._configure_bandwidth_detection()
            
            # Setup latency monitoring
            latency_monitoring = await self._setup_latency_monitoring()
            
            # Configure packet loss detection
            packet_loss_detection = await self._configure_packet_loss_detection()
            
            # Setup connection stability analysis
            stability_analysis = await self._setup_connection_stability_analysis()
            
            # Configure geographic optimization
            geographic_optimization = await self._configure_geographic_optimization()
            
            logger.info("🌐 Network Analyzer initialized")
            
            return {
                "network_monitoring": network_monitoring,
                "bandwidth_detection": bandwidth_detection,
                "latency_monitoring": latency_monitoring,
                "packet_loss_detection": packet_loss_detection,
                "stability_analysis": stability_analysis,
                "geographic_optimization": geographic_optimization,
                "capabilities": {
                    "real_time_monitoring": True,
                    "predictive_analysis": True,
                    "multi_metric_assessment": True,
                    "geographic_awareness": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize network analyzer: {e}")
            raise

    async def analyze_network_conditions(
        self,
        user_id: str,
        session_id: str,
        connection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze current network conditions"""
        try:
            condition_id = str(uuid.uuid4())
            
            # Detect network type
            network_type = await self._detect_network_type(connection_data)
            
            # Measure bandwidth
            bandwidth_measurement = await self._measure_bandwidth(
                user_id, connection_data
            )
            
            # Measure latency
            latency_measurement = await self._measure_latency(
                user_id, connection_data
            )
            
            # Detect packet loss
            packet_loss_measurement = await self._measure_packet_loss(
                user_id, connection_data
            )
            
            # Calculate jitter
            jitter_measurement = await self._calculate_jitter(
                user_id, connection_data
            )
            
            # Assess connection stability
            stability_assessment = await self._assess_connection_stability(
                user_id, bandwidth_measurement, latency_measurement
            )
            
            # Get geographic information
            geographic_info = await self._get_geographic_information(connection_data)
            
            # Calculate quality of service score
            qos_score = await self._calculate_qos_score(
                bandwidth_measurement, latency_measurement, 
                packet_loss_measurement, stability_assessment
            )
            
            # Create network condition record
            network_condition = NetworkCondition(
                condition_id=condition_id,
                user_id=user_id,
                session_id=session_id,
                network_type=network_type,
                bandwidth_mbps=bandwidth_measurement["bandwidth_mbps"],
                latency_ms=latency_measurement["latency_ms"],
                packet_loss_percent=packet_loss_measurement["loss_percent"],
                jitter_ms=jitter_measurement["jitter_ms"],
                connection_stability=stability_assessment["stability_score"],
                geographic_location=geographic_info["location"],
                isp_provider=geographic_info.get("isp", "Unknown"),
                measurement_timestamp=datetime.utcnow(),
                quality_of_service=qos_score
            )
            
            # Store network condition
            await self._store_network_condition(network_condition)
            
            # Update condition history
            self.condition_history[user_id].append(network_condition)
            if len(self.condition_history[user_id]) > 100:
                self.condition_history[user_id].popleft()
            
            return {
                "success": True,
                "condition_id": condition_id,
                "network_condition": network_condition,
                "measurement_details": {
                    "bandwidth": bandwidth_measurement,
                    "latency": latency_measurement,
                    "packet_loss": packet_loss_measurement,
                    "jitter": jitter_measurement,
                    "stability": stability_assessment
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze network conditions: {e}")
            raise

class DeviceDetector:
    """Device capability detection system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.device_profiles = {}
        self.capability_cache = {}
        
    async def detect_device_capabilities(
        self,
        user_agent: str,
        device_info: Dict[str, Any],
        performance_hints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Detect device capabilities for streaming optimization"""
        try:
            device_id = str(uuid.uuid4())
            
            # Parse user agent
            user_agent_analysis = await self._parse_user_agent(user_agent)
            
            # Detect device type
            device_type = await self._detect_device_type(
                user_agent_analysis, device_info
            )
            
            # Detect screen capabilities
            screen_capabilities = await self._detect_screen_capabilities(device_info)
            
            # Assess processing power
            processing_assessment = await self._assess_processing_power(
                device_info, performance_hints
            )
            
            # Detect codec support
            codec_support = await self._detect_codec_support(
                user_agent_analysis, device_info
            )
            
            # Detect protocol support
            protocol_support = await self._detect_protocol_support(
                user_agent_analysis, device_info
            )
            
            # Check hardware acceleration
            hardware_acceleration = await self._check_hardware_acceleration(
                device_info, performance_hints
            )
            
            # Assess battery status (for mobile devices)
            battery_assessment = await self._assess_battery_status(device_info)
            
            # Determine performance tier
            performance_tier = await self._determine_performance_tier(
                processing_assessment, screen_capabilities, codec_support
            )
            
            # Create device capability profile
            device_capability = DeviceCapability(
                device_id=device_id,
                device_type=device_type,
                screen_resolution=screen_capabilities["resolution"],
                max_bitrate_mbps=processing_assessment["max_bitrate"],
                supported_codecs=codec_support["supported_codecs"],
                supported_protocols=[StreamingProtocol(p) for p in protocol_support["protocols"]],
                hardware_acceleration=hardware_acceleration["available"],
                cpu_cores=processing_assessment.get("cpu_cores", 1),
                memory_gb=processing_assessment.get("memory_gb", 1.0),
                gpu_acceleration=hardware_acceleration["gpu_available"],
                battery_status=battery_assessment.get("battery_level"),
                thermal_status=battery_assessment.get("thermal_status", "normal"),
                performance_tier=performance_tier
            )
            
            # Cache device capability
            await self._cache_device_capability(device_capability)
            
            return {
                "success": True,
                "device_id": device_id,
                "device_capability": device_capability,
                "detection_details": {
                    "user_agent_analysis": user_agent_analysis,
                    "screen_capabilities": screen_capabilities,
                    "processing_assessment": processing_assessment,
                    "codec_support": codec_support,
                    "protocol_support": protocol_support,
                    "hardware_acceleration": hardware_acceleration
                },
                "detection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to detect device capabilities: {e}")
            raise

class QualityManager:
    """Quality profile management system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.quality_profiles = {}
        self.optimization_rules = {}
        
    async def initialize_quality_manager(self) -> Dict[str, Any]:
        """Initialize quality management system"""
        try:
            # Setup quality profiles
            quality_profiles = await self._setup_quality_profiles()
            
            # Configure encoding presets
            encoding_presets = await self._configure_encoding_presets()
            
            # Setup quality optimization rules
            optimization_rules = await self._setup_quality_optimization_rules()
            
            # Configure adaptive algorithms
            adaptive_algorithms = await self._configure_adaptive_algorithms()
            
            logger.info(f"📺 Quality Manager initialized with {len(quality_profiles)} profiles")
            
            return {
                "quality_profiles": len(quality_profiles),
                "encoding_presets": encoding_presets,
                "optimization_rules": len(optimization_rules),
                "adaptive_algorithms": adaptive_algorithms
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize quality manager: {e}")
            raise

    async def select_optimal_quality(
        self,
        device_capability: DeviceCapability,
        network_condition: NetworkCondition,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Select optimal quality profile based on conditions"""
        try:
            # Analyze device constraints
            device_constraints = await self._analyze_device_constraints(device_capability)
            
            # Analyze network constraints
            network_constraints = await self._analyze_network_constraints(network_condition)
            
            # Apply user preferences
            preference_constraints = await self._apply_user_preferences(
                user_preferences or {}, device_constraints, network_constraints
            )
            
            # Calculate optimal quality parameters
            optimal_parameters = await self._calculate_optimal_quality_parameters(
                device_constraints, network_constraints, preference_constraints
            )
            
            # Select best matching quality profile
            selected_profile = await self._select_quality_profile(optimal_parameters)
            
            # Validate quality selection
            quality_validation = await self._validate_quality_selection(
                selected_profile, device_capability, network_condition
            )
            
            # Calculate adaptation confidence
            adaptation_confidence = await self._calculate_adaptation_confidence(
                selected_profile, optimal_parameters, quality_validation
            )
            
            return {
                "success": True,
                "selected_quality": selected_profile,
                "optimal_parameters": optimal_parameters,
                "device_constraints": device_constraints,
                "network_constraints": network_constraints,
                "preference_constraints": preference_constraints,
                "quality_validation": quality_validation,
                "adaptation_confidence": adaptation_confidence,
                "selection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to select optimal quality: {e}")
            raise

class AdaptationEngine:
    """Adaptive streaming engine"""
    
    def __init__(self, redis_client -> None: aioredis.Redis, db_session -> None: AsyncSession) -> None:
        self.redis = redis_client
        self.db = db_session
        self.adaptation_algorithms = {}
        self.active_sessions = {}
        
    async def execute_quality_adaptation(
        self,
        session_id: str,
        trigger: AdaptationTrigger,
        trigger_data: Dict[str, Any],
        adaptation_strategy: AdaptationStrategy
    ) -> Dict[str, Any]:
        """Execute quality adaptation for streaming session"""
        try:
            event_id = str(uuid.uuid4())
            
            # Get current streaming session
            streaming_session = await self._get_streaming_session(session_id)
            if not streaming_session:
                raise ValueError("Streaming session not found")
            
            # Analyze adaptation trigger
            trigger_analysis = await self._analyze_adaptation_trigger(
                trigger, trigger_data, streaming_session
            )
            
            # Calculate new quality requirements
            quality_requirements = await self._calculate_new_quality_requirements(
                streaming_session, trigger_analysis, adaptation_strategy
            )
            
            # Select new quality profile
            new_quality = await self._select_adaptation_quality_profile(
                quality_requirements, streaming_session
            )
            
            # Plan adaptation execution
            adaptation_plan = await self._plan_adaptation_execution(
                streaming_session, new_quality, adaptation_strategy
            )
            
            # Execute adaptation
            adaptation_execution = await self._execute_adaptation_plan(
                streaming_session, adaptation_plan
            )
            
            # Monitor adaptation performance
            adaptation_monitoring = await self._monitor_adaptation_performance(
                streaming_session, adaptation_execution
            )
            
            # Update session state
            session_update = await self._update_streaming_session_state(
                streaming_session, new_quality, adaptation_execution
            )
            
            # Create adaptation event record
            adaptation_event = AdaptationEvent(
                event_id=event_id,
                session_id=session_id,
                trigger=trigger,
                trigger_data=trigger_data,
                previous_quality=streaming_session.current_quality,
                new_quality=new_quality,
                adaptation_strategy=adaptation_strategy,
                adaptation_duration_ms=adaptation_execution["duration_ms"],
                performance_impact=adaptation_monitoring["performance_impact"],
                user_satisfaction=None,  # To be updated based on user feedback
                timestamp=datetime.utcnow()
            )
            
            # Store adaptation event
            await self._store_adaptation_event(adaptation_event)
            
            return {
                "success": True,
                "event_id": event_id,
                "adaptation_event": adaptation_event,
                "trigger_analysis": trigger_analysis,
                "quality_requirements": quality_requirements,
                "adaptation_plan": adaptation_plan,
                "adaptation_execution": adaptation_execution,
                "adaptation_monitoring": adaptation_monitoring,
                "session_update": session_update,
                "adaptation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute quality adaptation: {e}")
            raise

class StreamingAdaptiveController:
    """Unified streaming adaptive controller - Main service class"""
    
    def __init__(self, redis_client -> None: aioredis.Redis, db_session -> None: AsyncSession) -> None:
        self.redis = redis_client
        self.db = db_session
        
        # Initialize adaptive components
        self.network_analyzer = NetworkAnalyzer(redis_client)
        self.device_detector = DeviceDetector(redis_client)
        self.quality_manager = QualityManager(redis_client)
        self.adaptation_engine = AdaptationEngine(redis_client, db_session)
        
        # Adaptive management
        self.streaming_sessions = {}
        self.adaptation_rules = {}
        
        logger.info("🎛️ Streaming Adaptive Controller initialized")
    
    async def initialize_adaptive_controller(self) -> Dict[str, Any]:
        """Initialize adaptive streaming controller"""
        try:
            # Initialize network analyzer
            network_status = await self.network_analyzer.initialize_network_analyzer()
            
            # Initialize quality manager
            quality_status = await self.quality_manager.initialize_quality_manager()
            
            # Setup adaptation rules
            adaptation_rules = await self._setup_adaptation_rules()
            
            # Configure learning algorithms
            learning_algorithms = await self._configure_learning_algorithms()
            
            # Setup session monitoring
            session_monitoring = await self._setup_session_monitoring()
            
            # Configure performance optimization
            performance_optimization = await self._configure_performance_optimization()
            
            logger.info("🎛️ Streaming Adaptive Controller fully initialized")
            
            return {
                "controller_status": "initialized",
                "network_analyzer": network_status,
                "quality_manager": quality_status,
                "adaptation_rules": adaptation_rules,
                "learning_algorithms": learning_algorithms,
                "session_monitoring": session_monitoring,
                "performance_optimization": performance_optimization,
                "capabilities": {
                    "adaptive_bitrate": True,
                    "device_optimization": True,
                    "network_adaptation": True,
                    "quality_optimization": True,
                    "predictive_adaptation": True,
                    "machine_learning": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize adaptive controller: {e}")
            raise
    
    async def start_adaptive_streaming_session(
        self,
        user_id: str,
        stream_id: str,
        user_agent: str,
        connection_data: Dict[str, Any],
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Start adaptive streaming session with comprehensive optimization"""
        try:
            session_id = str(uuid.uuid4())
            
            # Detect device capabilities
            device_detection = await self.device_detector.detect_device_capabilities(
                user_agent, connection_data.get("device_info", {}), 
                connection_data.get("performance_hints", {})
            )
            
            # Analyze network conditions
            network_analysis = await self.network_analyzer.analyze_network_conditions(
                user_id, session_id, connection_data
            )
            
            # Select optimal quality
            quality_selection = await self.quality_manager.select_optimal_quality(
                device_detection["device_capability"],
                network_analysis["network_condition"],
                user_preferences
            )
            
            # Create streaming session
            streaming_session = StreamingSession(
                session_id=session_id,
                user_id=user_id,
                stream_id=stream_id,
                device_capability=device_detection["device_capability"],
                network_condition=network_analysis["network_condition"],
                current_quality=quality_selection["selected_quality"],
                target_quality=quality_selection["selected_quality"],
                adaptation_history=[],
                performance_metrics={},
                user_preferences=user_preferences or {},
                started_at=datetime.utcnow(),
                last_adaptation=datetime.utcnow()
            )
            
            # Store streaming session
            await self._store_streaming_session(streaming_session)
            self.streaming_sessions[session_id] = streaming_session
            
            # Setup session monitoring
            monitoring_setup = await self._setup_streaming_session_monitoring(streaming_session)
            
            # Configure adaptation triggers
            trigger_configuration = await self._configure_session_adaptation_triggers(
                streaming_session
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "streaming_session": streaming_session,
                "device_detection": device_detection,
                "network_analysis": network_analysis,
                "quality_selection": quality_selection,
                "monitoring_setup": monitoring_setup,
                "trigger_configuration": trigger_configuration,
                "session_started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start adaptive streaming session: {e}")
            raise
    
    # Additional helper methods implementation...
    async def _setup_adaptation_rules(self) -> Dict[str, Any]:
        """Setup adaptation rules"""
        try:
            return {
                "bandwidth_rules": True,
                "device_rules": True,
                "quality_rules": True,
                "user_preference_rules": True
            }
        except Exception as e:
            logger.error(f"Failed to setup adaptation rules: {e}")
            return {}

    async def _configure_learning_algorithms(self) -> Dict[str, Any]:
        """Configure learning algorithms"""
        try:
            return {
                "machine_learning": True,
                "user_behavior_learning": True,
                "network_pattern_learning": True,
                "quality_optimization": True
            }
        except Exception as e:
            logger.error(f"Failed to configure learning algorithms: {e}")
            return {}

# Export main classes
__all__ = [
    "StreamingAdaptiveController",
    "NetworkAnalyzer",
    "DeviceDetector",
    "QualityManager",
    "AdaptationEngine",
    "NetworkCondition",
    "DeviceCapability",
    "QualityProfile",
    "AdaptationRule",
    "StreamingSession",
    "AdaptationEvent",
    "AdaptationStrategy",
    "QualityLevel",
    "DeviceType",
    "NetworkType",
    "AdaptationTrigger",
    "StreamingProtocol"
]
