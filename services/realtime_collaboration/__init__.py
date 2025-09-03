"""Real-time Collaboration Service
Advanced WebRTC-powered collaboration platform with AI-driven features.

This module provides:
- WebRTC audio/video collaboration
- Project versioning and branching 
- Collaborative media annotations
- Integrated chat with automatic translation
- Virtual DAW session sharing
- Conflict resolution for simultaneous edits

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT INTELLECTUAL PROPERTY WARNING ⚠️
This software and all associated intellectual property are the EXCLUSIVE PROPERTY
of Fahed Mlaiel. UNAUTHORIZED ACCESS, COPYING, MODIFICATION, DISTRIBUTION, 
REVERSE ENGINEERING, OR COMMERCIALIZATION without explicit written permission 
is STRICTLY PROHIBITED and will result in immediate legal action.

For licensing inquiries: mlaiel@live.de
"""

from .webrtc_service import (
    WebRTCCollaborationService, 
    ConnectionType, 
    StreamType, 
    SessionStatus,
    Participant,
    CollaborationSession
)
from .project_versioning import (
    ProjectVersioningSystem, 
    BranchStatus, 
    ChangeType, 
    MergeStrategy,
    ProjectFile, 
    ProjectChange, 
    ProjectCommit, 
    ProjectBranch,
    MergeConflict, 
    MergeRequest, 
    ConflictResolver
)
from .media_annotations import (
    CollaborativeAnnotationEngine, 
    AnnotationType, 
    MediaType,
    AnnotationStatus, 
    PermissionLevel, 
    Annotation, 
    MediaSession,
    AnnotationPosition, 
    AnnotationStyle, 
    UserCursor
)
from .translation_chat import (
    TranslationChatService, 
    MessageType, 
    TranslationMode, 
    MessageStatus,
    Language, 
    TranslationResult, 
    ChatMessage, 
    ChatParticipant, 
    ChatSession, 
    AITranslationEngine
)
from .daw_sharing import (
    VirtualDAWSessionManager, 
    DAWType, 
    TrackType, 
    SessionState,
    PermissionLevel as DAWPermissionLevel, 
    AudioSettings, 
    TimelinePosition, 
    MIDIEvent,
    AudioRegion, 
    MIDIRegion, 
    PluginState, 
    DAWTrack, 
    DAWProject,
    SessionParticipant as DAWParticipant, 
    DAWSession
)
from .conflict_resolution import (
    CollaborationConflictResolver, 
    ConflictType, 
    ConflictSeverity,
    ResolutionStrategy, 
    OperationType, 
    Operation, 
    ConflictEvent,
    VectorClock, 
    ResourceState, 
    CollaborationSession as ConflictSession, 
    OperationalTransformer
)
from .realtime_engine import (
    RealtimeCollaborationEngine, 
    ServiceType, 
    SessionType,
    CollaborationMetrics, 
    UnifiedSession
)

# Main collaboration engine instance
collaboration_engine = None

def get_collaboration_engine(redis_client=None):
    """Get or create the main collaboration engine instance"""
    global collaboration_engine
    if collaboration_engine is None:
        collaboration_engine = RealtimeCollaborationEngine(redis_client)
    return collaboration_engine

# Service factory functions
def create_webrtc_service(redis_client=None):
    """Create WebRTC collaboration service"""
    return WebRTCCollaborationService(redis_client)

def create_versioning_system():
    """Create project versioning system"""
    return ProjectVersioningSystem()

def create_annotation_engine():
    """Create collaborative annotation engine"""
    return CollaborativeAnnotationEngine()

def create_chat_service():
    """Create translation chat service"""
    return TranslationChatService()

def create_daw_manager():
    """Create virtual DAW session manager"""
    return VirtualDAWSessionManager()

def create_conflict_resolver():
    """Create collaboration conflict resolver"""
    return CollaborationConflictResolver()

__all__ = [
    # Main engine
    'RealtimeCollaborationEngine',
    'get_collaboration_engine',
    
    # Service classes
    'WebRTCCollaborationService',
    'ProjectVersioningSystem',
    'CollaborativeAnnotationEngine', 
    'TranslationChatService',
    'VirtualDAWSessionManager',
    'CollaborationConflictResolver',
    
    # Factory functions
    'create_webrtc_service',
    'create_versioning_system',
    'create_annotation_engine',
    'create_chat_service',
    'create_daw_manager',
    'create_conflict_resolver',
    
    # Service enums and types
    'ServiceType',
    'SessionType',
    'ConnectionType',
    'StreamType',
    'SessionStatus',
    'BranchStatus',
    'ChangeType',
    'MergeStrategy',
    'AnnotationType',
    'MediaType',
    'AnnotationStatus',
    'PermissionLevel',
    'DAWPermissionLevel',
    'MessageType',
    'TranslationMode',
    'MessageStatus',
    'DAWType',
    'TrackType',
    'ConflictType',
    'ConflictSeverity',
    'ResolutionStrategy',
    'OperationType',
    
    # Data classes
    'CollaborationMetrics',
    'UnifiedSession',
    'Participant',
    'CollaborationSession',
    'ProjectFile',
    'ProjectChange',
    'ProjectCommit',
    'ProjectBranch',
    'MergeConflict',
    'MergeRequest',
    'Annotation',
    'MediaSession',
    'AnnotationPosition',
    'AnnotationStyle',
    'UserCursor',
    'Language',
    'TranslationResult',
    'ChatMessage',
    'ChatParticipant',
    'ChatSession',
    'AudioSettings',
    'TimelinePosition',
    'MIDIEvent',
    'AudioRegion',
    'MIDIRegion',
    'PluginState',
    'DAWTrack',
    'DAWProject',
    'DAWParticipant',
    'DAWSession',
    'Operation',
    'ConflictEvent',
    'VectorClock',
    'ResourceState',
    'ConflictSession',
    
    # Helper classes
    'ConflictResolver',
    'AITranslationEngine',
    'OperationalTransformer'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"