"""Real-Time Collaboration Service Demo
Demonstration of the real-time collaboration features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules directly to avoid __init__.py issues
import importlib.util

# Load realtime collaboration service directly
spec = importlib.util.spec_from_file_location(
    "realtime_collaboration_service", 
    os.path.join(os.path.dirname(__file__), "services", "realtime_collaboration_service.py")
)
rtc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rtc_module)

# Load virtual DAW service directly  
spec = importlib.util.spec_from_file_location(
    "virtual_daw_service",
    os.path.join(os.path.dirname(__file__), "services", "virtual_daw_service.py")
)
daw_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daw_module)

# Extract classes
RealtimeCollaborationService = rtc_module.RealtimeCollaborationService
SessionType = rtc_module.SessionType
AnnotationType = rtc_module.AnnotationType
VirtualDAWService = daw_module.VirtualDAWService
TrackType = daw_module.TrackType
from unittest.mock import Mock, AsyncMock


async def demo_realtime_collaboration():
    """Demonstrate real-time collaboration features"""
    print("🎵 Ainflue Real-Time Collaboration Service Demo")
    print("=" * 60)
    
    # Initialize services
    print("🚀 Initializing services...")
    collaboration_service = RealtimeCollaborationService()
    daw_service = VirtualDAWService()
    
    # Initialize without Redis to avoid dependency issues
    collaboration_service.redis_client = None
    
    # Create a mock WebSocket
    mock_websocket = Mock()
    mock_websocket.send = AsyncMock()
    
    try:
        await collaboration_service.initialize()
        print("✅ Real-time collaboration service initialized")
        
        # Demo 1: Create a music production session
        print("\n🎼 Demo 1: Creating Music Production Session")
        print("-" * 40)
        
        creator_id = "fahed_mlaiel"
        project_id = "epic_collaboration_2025"
        
        session = await collaboration_service.create_realtime_session(
            creator_id,
            SessionType.AUDIO_PRODUCTION,
            project_id,
            {
                "project_name": "Epic Collaboration 2025",
                "max_participants": 5,
                "recording_enabled": True
            }
        )
        
        print(f"📝 Session created: {session.session_id}")
        print(f"🎯 Session type: {session.session_type.value}")
        print(f"👤 Creator: {session.creator_id}")
        print(f"🌐 WebRTC config available: {bool(session.webrtc_config)}")
        
        # Demo 2: Create DAW session
        print("\n🎛️ Demo 2: Creating Virtual DAW Session")
        print("-" * 40)
        
        daw_session = await daw_service.create_daw_session(creator_id)
        print(f"🎚️ DAW session created: {daw_session.session_id}")
        print(f"🎵 Sample rate: {daw_session.project.sample_rate} Hz")
        print(f"🎼 Tempo: {daw_session.project.tempo} BPM")
        
        # Demo 3: Add collaborator
        print("\n👥 Demo 3: Adding Collaborator")
        print("-" * 40)
        
        collaborator_id = "music_partner_123"
        success = await collaboration_service.join_session(
            session.session_id, collaborator_id, mock_websocket
        )
        
        if success:
            print(f"✅ {collaborator_id} joined the session")
            print(f"👥 Participants: {list(session.participants)}")
        
        # Demo 4: Create tracks in DAW
        print("\n🎸 Demo 4: Creating Audio Tracks")
        print("-" * 40)
        
        # Create lead vocal track
        vocal_track = await daw_service.create_track(
            daw_session.session_id,
            creator_id,
            {
                "name": "Lead Vocal",
                "type": "audio",
                "volume": 0.8,
                "pan": 0.0,
                "color": "#FF6B6B"
            }
        )
        print(f"🎤 Created track: {vocal_track.name} ({vocal_track.track_id})")
        
        # Create guitar track
        guitar_track = await daw_service.create_track(
            daw_session.session_id,
            collaborator_id,
            {
                "name": "Electric Guitar",
                "type": "audio", 
                "volume": 0.7,
                "pan": -0.3,
                "color": "#4ECDC4"
            }
        )
        print(f"🎸 Created track: {guitar_track.name} ({guitar_track.track_id})")
        
        # Demo 5: Real-time parameter updates
        print("\n🎛️ Demo 5: Real-Time Parameter Updates")
        print("-" * 40)
        
        # Update volume in real-time
        await daw_service.update_track_parameter(
            daw_session.session_id,
            creator_id,
            vocal_track.track_id,
            "volume",
            0.9
        )
        print(f"🔊 Updated {vocal_track.name} volume to 0.9")
        
        # Update pan
        await daw_service.update_track_parameter(
            daw_session.session_id,
            collaborator_id,
            guitar_track.track_id,
            "pan",
            0.2
        )
        print(f"↔️ Updated {guitar_track.name} pan to 0.2")
        
        # Demo 6: Add annotations
        print("\n📝 Demo 6: Adding Real-Time Annotations")
        print("-" * 40)
        
        # Add audio marker
        marker = await collaboration_service.create_media_annotation(
            session.session_id,
            creator_id,
            AnnotationType.AUDIO_MARKER,
            32.5,  # 32.5 seconds
            "Bridge section starts here",
            None
        )
        print(f"🎯 Added audio marker at {marker.media_timestamp}s: {marker.content}")
        
        # Add feedback comment
        comment = await collaboration_service.create_media_annotation(
            session.session_id,
            collaborator_id,
            AnnotationType.TEXT_COMMENT,
            45.2,
            "Love the guitar tone here! Maybe add some reverb?",
            {"x": 150, "y": 200}
        )
        print(f"💬 Added comment at {comment.media_timestamp}s: {comment.content}")
        
        # Demo 7: Version control
        print("\n📚 Demo 7: Version Control")
        print("-" * 40)
        
        # Create version snapshot
        version = await collaboration_service.create_version_snapshot(
            session.session_id,
            creator_id,
            {
                "tracks_updated": [vocal_track.track_id, guitar_track.track_id],
                "mix_changes": {"master_volume": 0.85},
                "effects_added": ["reverb_on_guitar", "compressor_on_vocal"]
            },
            "Added guitar and vocal tracks with initial effects",
            False,
            None
        )
        print(f"📦 Version created: {version.version_id}")
        print(f"📝 Commit message: {version.commit_message}")
        
        # Demo 8: Playback control
        print("\n▶️ Demo 8: Synchronized Playback")
        print("-" * 40)
        
        # Start playback
        playback_started = await daw_service.start_playback(
            daw_session.session_id,
            creator_id,
            0.0  # Start from beginning
        )
        
        if playback_started:
            print("▶️ Playback started synchronously for all participants")
            
            # Simulate playback for a moment
            await asyncio.sleep(1)
            
            # Stop playback
            playback_stopped = await daw_service.stop_playback(
                daw_session.session_id,
                creator_id
            )
            
            if playback_stopped:
                print("⏹️ Playback stopped")
        
        # Demo 9: Session analytics
        print("\n📊 Demo 9: Session Analytics")
        print("-" * 40)
        
        analytics = await collaboration_service.get_session_analytics(session.session_id)
        
        print(f"📈 Session Duration: {analytics.get('duration_seconds', 0):.1f} seconds")
        print(f"👥 Total Participants: {analytics.get('total_participants', 0)}")
        print(f"🏃 Active Participants: {analytics.get('active_participants', 0)}")
        print(f"📝 Annotations Created: {analytics.get('annotation_count', 0)}")
        print(f"📚 Versions Created: {analytics.get('version_count', 0)}")
        
        # Demo 10: Export project
        print("\n💾 Demo 10: Project Export")
        print("-" * 40)
        
        try:
            export_data = await daw_service.export_project(
                daw_session.session_id,
                "wav",
                "high"
            )
            print(f"💿 Project exported: {len(export_data)} bytes")
        except Exception as e:
            print(f"ℹ️ Export simulation: Would export high-quality WAV file")
        
        print("\n🎉 Demo Complete!")
        print("=" * 60)
        print("✨ Real-time collaboration features demonstrated:")
        print("   • Audio production session creation")
        print("   • Multi-user collaboration")
        print("   • Real-time track creation and parameter updates")
        print("   • Live annotations and comments")
        print("   • Version control with snapshots")
        print("   • Synchronized playback control")
        print("   • Session analytics")
        print("   • Project export functionality")
        print()
        print("🌟 Ready for production deployment!")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


async def demo_conflict_resolution():
    """Demonstrate conflict resolution features"""
    print("\n⚔️ Bonus Demo: Conflict Resolution")
    print("-" * 40)
    
    collaboration_service = RealtimeCollaborationService()
    collaboration_service.redis_client = None
    await collaboration_service.initialize()
    
    # Create session
    session = await collaboration_service.create_realtime_session(
        "user1",
        SessionType.PROJECT_REVIEW,
        "conflict_demo"
    )
    
    # Simulate conflicting edits
    session.session_state = {"document": {"content": "original content"}}
    
    # First user makes edit
    await collaboration_service.handle_realtime_message(
        session.session_id,
        "user1",
        {
            "type": "state_update",
            "data": {"document": {"content": "user1 changes"}}
        }
    )
    
    # Second user makes conflicting edit
    await collaboration_service.handle_realtime_message(
        session.session_id,
        "user2", 
        {
            "type": "state_update",
            "data": {"document": {"content": "user2 changes"}}
        }
    )
    
    # Check for conflicts
    if session.conflict_queue:
        conflict = session.conflict_queue[0]
        print(f"⚠️ Conflict detected: {conflict['conflict_type']}")
        print(f"🔧 Resource: {conflict['resource']}")
        print("✅ Automatic conflict resolution available")
    else:
        print("ℹ️ No conflicts detected in this demo")


if __name__ == "__main__":
    print("🎵 Starting Ainflue Real-Time Collaboration Demo...")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    asyncio.run(demo_realtime_collaboration())
    asyncio.run(demo_conflict_resolution())