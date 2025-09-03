# Services module initialization
from .realtime_collaboration_service import (
    RealtimeCollaborationService,
    SessionType,
    AnnotationType,
    ConflictType
)
from .virtual_daw_service import (
    VirtualDAWService,
    TrackType,
    PluginType,
    DAWProject,
    DAWTrack
)
from .realtime_websocket_server import (
    RealtimeWebSocketServer,
    WebSocketConnectionManager
)

# Import existing services that are available
try:
    from .collaboration_engine import CollaborationEngine
except ImportError:
    CollaborationEngine = None

try:
    from .gamification_system import GamificationSystem
except ImportError:
    GamificationSystem = None

try:
    from .recommendation_engine import RecommendationEngine
except ImportError:
    RecommendationEngine = None

__all__ = [
    "RealtimeCollaborationService",
    "SessionType", 
    "AnnotationType",
    "ConflictType",
    "VirtualDAWService",
    "TrackType",
    "PluginType",
    "DAWProject",
    "DAWTrack",
    "RealtimeWebSocketServer",
    "WebSocketConnectionManager"
]

# Add existing services if available
if CollaborationEngine:
    __all__.append("CollaborationEngine")
if GamificationSystem:
    __all__.append("GamificationSystem") 
if RecommendationEngine:
    __all__.append("RecommendationEngine")