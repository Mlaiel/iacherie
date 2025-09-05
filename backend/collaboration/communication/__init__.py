"""Communication Module - Advanced Collaboration Communication System
=====================================================================

Comprehensive communication system providing:
- Real-time messaging and chat
- Video conferencing integration
- File sharing and document collaboration
- Notification management
- Activity streams and feeds
- Voice notes and audio messages

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

from .messaging_system import (
    MessagingSystem,
    Message,
    Conversation,
    MessageType,
    MessageStatus,
    ChatRoom
)

from .video_call_integration import (
    VideoCallManager,
    VideoCall,
    CallStatus,
    CallQuality,
    CallRecording,
    ScreenShare
)

from .screen_sharing import (
    ScreenSharingManager,
    ScreenSession,
    SharePermission,
    AnnotationTool,
    SessionRecording
)

from .file_sharing import (
    FileSharingManager,
    SharedFile,
    FilePermission,
    FileVersion,
    ShareLink,
    UploadSession
)

from .notification_manager import (
    NotificationManager,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationPreference,
    AlertRule
)

from .collaboration_chat import (
    CollaborationChat,
    ProjectChannel,
    ThreadConversation,
    ChatBot,
    ChatAnalytics,
    MessageTemplate
)

from .meeting_scheduler import (
    MeetingScheduler,
    Meeting,
    MeetingType,
    Availability,
    CalendarIntegration,
    MeetingReminder
)

from .voice_notes import (
    VoiceNoteManager,
    VoiceNote,
    AudioTranscription,
    VoiceCommand,
    AudioQuality,
    PlaybackSession
)

from .feedback_system import (
    FeedbackManager,
    FeedbackRequest,
    FeedbackResponse,
    FeedbackType,
    ReviewWorkflow,
    FeedbackAnalytics
)

from .comment_engine import (
    CommentEngine,
    Comment,
    CommentThread,
    CommentType,
    Annotation,
    CommentAnalytics
)

from .activity_stream import (
    ActivityStreamManager,
    Activity,
    ActivityType,
    ActivityFeed,
    StreamFilter,
    ActivityNotification
)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Collaboration Communication System"

# Export all public classes and functions
__all__ = [
    # Messaging System
    "MessagingSystem",
    "Message",
    "Conversation",
    "MessageType",
    "MessageStatus",
    "ChatRoom",
    
    # Video Calls
    "VideoCallManager",
    "VideoCall",
    "CallStatus",
    "CallQuality",
    "CallRecording",
    "ScreenShare",
    
    # Screen Sharing
    "ScreenSharingManager",
    "ScreenSession",
    "SharePermission",
    "AnnotationTool",
    "SessionRecording",
    
    # File Sharing
    "FileSharingManager",
    "SharedFile",
    "FilePermission",
    "FileVersion",
    "ShareLink",
    "UploadSession",
    
    # Notifications
    "NotificationManager",
    "Notification",
    "NotificationType",
    "NotificationChannel",
    "NotificationPreference",
    "AlertRule",
    
    # Collaboration Chat
    "CollaborationChat",
    "ProjectChannel",
    "ThreadConversation",
    "ChatBot",
    "ChatAnalytics",
    "MessageTemplate",
    
    # Meeting Scheduler
    "MeetingScheduler",
    "Meeting",
    "MeetingType",
    "Availability",
    "CalendarIntegration",
    "MeetingReminder",
    
    # Voice Notes
    "VoiceNoteManager",
    "VoiceNote",
    "AudioTranscription",
    "VoiceCommand",
    "AudioQuality",
    "PlaybackSession",
    
    # Feedback System
    "FeedbackManager",
    "FeedbackRequest",
    "FeedbackResponse",
    "FeedbackType",
    "ReviewWorkflow",
    "FeedbackAnalytics",
    
    # Comment Engine
    "CommentEngine",
    "Comment",
    "CommentThread",
    "CommentType",
    "Annotation",
    "CommentAnalytics",
    
    # Activity Stream
    "ActivityStreamManager",
    "Activity",
    "ActivityType",
    "ActivityFeed",
    "StreamFilter",
    "ActivityNotification"
]

# Module initialization
import logging
logger = logging.getLogger(__name__)
logger.info(f"💬 Communication Module v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🚀 Real-time collaboration communication system initialized")