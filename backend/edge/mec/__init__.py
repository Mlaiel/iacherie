"""Mobile Edge Computing (MEC) Module
===================================

Mobile Edge Computing services for edge infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Device manager
from .device_manager import (
    MobileDeviceManager,
    DeviceType,
    DeviceCapability,
    DeviceStatus,
    create_device_manager
)

# Handover controller
from .handover_controller import (
    HandoverController,
    HandoverType,
    HandoverPolicy,
    create_handover_controller
)

# Location services
from .location_services import (
    LocationService,
    LocationMethod,
    LocationAccuracy,
    create_location_service
)

# Proximity detection
from .proximity_detection import (
    ProximityDetector,
    ProximityZone,
    DetectionMethod,
    create_proximity_detector
)

# Mobility prediction
from .mobility_prediction import (
    MobilityPredictor,
    MovementPattern,
    PredictionModel,
    create_mobility_predictor
)

# Session continuity
from .session_continuity import (
    SessionManager,
    SessionType,
    ContinuityPolicy,
    create_session_manager
)

# Context awareness
from .context_awareness import (
    ContextEngine,
    ContextType,
    ContextRule,
    create_context_engine
)

__all__ = [
    # Device management
    "MobileDeviceManager",
    "DeviceType",
    "DeviceCapability", 
    "DeviceStatus",
    "create_device_manager",
    
    # Handover control
    "HandoverController",
    "HandoverType",
    "HandoverPolicy",
    "create_handover_controller",
    
    # Location services
    "LocationService",
    "LocationMethod",
    "LocationAccuracy",
    "create_location_service",
    
    # Proximity detection
    "ProximityDetector",
    "ProximityZone",
    "DetectionMethod",
    "create_proximity_detector",
    
    # Mobility prediction
    "MobilityPredictor",
    "MovementPattern",
    "PredictionModel",
    "create_mobility_predictor",
    
    # Session continuity
    "SessionManager",
    "SessionType",
    "ContinuityPolicy",
    "create_session_manager",
    
    # Context awareness
    "ContextEngine",
    "ContextType",
    "ContextRule",
    "create_context_engine"
]