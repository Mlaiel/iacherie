"""Index Module - Communication System Entry Point
==============================================

Centralized entry point for the collaboration communication system
providing quick access to all communication tools and utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import (
    MessagingSystem,
    # VideoCallManager,
    # ScreenSharingManager,
    # FileSharingManager,
    # NotificationManager,
    # CollaborationChat,
    # MeetingScheduler,
    # VoiceNoteManager,
    # FeedbackManager,
    # CommentEngine,
    # ActivityStreamManager
)

def get_communication_system(config=None):
    """Get unified communication system with all components"""
    return {
        'messaging': MessagingSystem(config),
        # 'video_calls': VideoCallManager(config),
        # 'screen_sharing': ScreenSharingManager(config),
        # 'file_sharing': FileSharingManager(config),
        # 'notifications': NotificationManager(config),
        # 'collaboration_chat': CollaborationChat(config),
        # 'meeting_scheduler': MeetingScheduler(config),
        # 'voice_notes': VoiceNoteManager(config),
        # 'feedback': FeedbackManager(config),
        # 'comments': CommentEngine(config),
        # 'activity_stream': ActivityStreamManager(config)
    }

async def setup_collaboration_communication(project_id, participants, config=None):
    """Set up complete communication infrastructure for a project"""
    system = get_communication_system(config)
    
    # Create main project conversation
    main_conversation = await system['messaging'].create_conversation(
        name=f"Project {project_id}",
        conversation_type="PROJECT",
        creator_id=participants[0] if participants else "system",
        participants=participants
    )
    
    # Create project chat room
    chat_room = await system['messaging'].create_chat_room(
        project_id=project_id,
        name="General",
        creator_id=participants[0] if participants else "system"
    )
    
    # Add participants to room
    for participant in participants[1:]:
        await system['messaging'].join_chat_room(chat_room.room_id, participant)
    
    return {
        'main_conversation': main_conversation,
        'chat_room': chat_room,
        'communication_system': system
    }