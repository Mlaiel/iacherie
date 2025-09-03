"""Virtual DAW Session Manager
Real-time collaborative Digital Audio Workstation session sharing.

Provides:
- Real-time DAW project synchronization
- Multi-track collaboration
- MIDI and audio synchronization
- Plugin state sharing
- Timeline synchronization
- Remote control capabilities
- Audio streaming and latency compensation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import base64

from fastapi import WebSocket
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DAWType(Enum):
    """Supported DAW types"""
    ABLETON_LIVE = "ableton_live"
    LOGIC_PRO = "logic_pro"
    PRO_TOOLS = "pro_tools"
    CUBASE = "cubase"
    FL_STUDIO = "fl_studio"
    REAPER = "reaper"
    STUDIO_ONE = "studio_one"
    BITWIG = "bitwig"
    REASON = "reason"
    GARAGE_BAND = "garage_band"


class TrackType(Enum):
    """Audio track types"""
    AUDIO = "audio"
    MIDI = "midi"
    INSTRUMENT = "instrument"
    AUXILIARY = "auxiliary"
    MASTER = "master"
    GROUP = "group"


class SessionState(Enum):
    """DAW session states"""
    STOPPED = "stopped"
    PLAYING = "playing"
    RECORDING = "recording"
    PAUSED = "paused"
    REWINDING = "rewinding"
    FAST_FORWARD = "fast_forward"


class PermissionLevel(Enum):
    """DAW session permissions"""
    LISTEN_ONLY = "listen_only"
    PARTICIPANT = "participant"
    COLLABORATOR = "collaborator"
    PRODUCER = "producer"
    ADMIN = "admin"


@dataclass
class AudioSettings:
    """Audio configuration settings"""
    sample_rate: int = 44100
    bit_depth: int = 24
    buffer_size: int = 256
    latency_compensation: float = 0.0
    master_volume: float = 0.8
    metronome_enabled: bool = True
    click_track_volume: float = 0.5


@dataclass
class TimelinePosition:
    """Timeline position representation"""
    bars: int
    beats: int
    ticks: int
    samples: int
    time_signature_numerator: int = 4
    time_signature_denominator: int = 4
    tempo: float = 120.0


@dataclass
class MIDIEvent:
    """MIDI event data"""
    event_id: str
    timestamp: float
    channel: int
    note_number: Optional[int] = None
    velocity: Optional[int] = None
    controller_number: Optional[int] = None
    controller_value: Optional[int] = None
    event_type: str = "note_on"  # note_on, note_off, control_change, etc.


@dataclass
class AudioRegion:
    """Audio region in timeline"""
    region_id: str
    track_id: str
    start_position: TimelinePosition
    end_position: TimelinePosition
    audio_file_id: str
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    soloed: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MIDIRegion:
    """MIDI region in timeline"""
    region_id: str
    track_id: str
    start_position: TimelinePosition
    end_position: TimelinePosition
    midi_events: List[MIDIEvent] = field(default_factory=list)
    velocity_scaling: float = 1.0
    timing_offset: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginState:
    """Plugin/Effect state"""
    plugin_id: str
    plugin_name: str
    plugin_type: str  # instrument, effect, etc.
    parameters: Dict[str, float] = field(default_factory=dict)
    preset_name: Optional[str] = None
    enabled: bool = True
    automation_data: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)


@dataclass
class DAWTrack:
    """DAW track representation"""
    track_id: str
    track_name: str
    track_type: TrackType
    track_number: int
    volume: float = 0.8
    pan: float = 0.0
    muted: bool = False
    soloed: bool = False
    record_enabled: bool = False
    monitor_enabled: bool = False
    input_source: str = "none"
    output_destination: str = "master"
    audio_regions: List[AudioRegion] = field(default_factory=list)
    midi_regions: List[MIDIRegion] = field(default_factory=list)
    plugins: List[PluginState] = field(default_factory=list)
    automation_data: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)
    color: str = "#808080"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAWProject:
    """Complete DAW project state"""
    project_id: str
    project_name: str
    daw_type: DAWType
    audio_settings: AudioSettings
    timeline_position: TimelinePosition
    session_state: SessionState
    tracks: Dict[str, DAWTrack] = field(default_factory=dict)
    markers: List[Dict[str, Any]] = field(default_factory=list)
    arrangement_loop_start: Optional[TimelinePosition] = None
    arrangement_loop_end: Optional[TimelinePosition] = None
    loop_enabled: bool = False
    punch_in_enabled: bool = False
    punch_in_start: Optional[TimelinePosition] = None
    punch_in_end: Optional[TimelinePosition] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SessionParticipant:
    """DAW session participant"""
    user_id: str
    username: str
    permission_level: PermissionLevel
    daw_type: DAWType
    daw_version: str
    latency_compensation: float
    audio_interface: str
    joined_at: datetime
    last_activity: datetime
    is_connected: bool = True
    controlled_tracks: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAWSession:
    """Virtual DAW collaboration session"""
    session_id: str
    project_id: str
    host_id: str
    project: DAWProject
    participants: Dict[str, SessionParticipant] = field(default_factory=dict)
    shared_audio_streams: Dict[str, str] = field(default_factory=dict)
    sync_enabled: bool = True
    latency_compensation_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_sync: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)


class VirtualDAWSessionManager:
    """
    Real-time collaborative DAW session management
    """
    
    def __init__(self):
        self.daw_sessions: Dict[str, DAWSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.audio_streams: Dict[str, bytes] = {}
        self.sync_intervals: Dict[str, float] = {}
        
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """Setup DAW message handlers"""
        self.message_handlers = {
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "transport_control": self._handle_transport_control,
            "timeline_position": self._handle_timeline_position,
            "track_update": self._handle_track_update,
            "plugin_update": self._handle_plugin_update,
            "audio_stream": self._handle_audio_stream,
            "midi_event": self._handle_midi_event,
            "automation_update": self._handle_automation_update,
            "project_save": self._handle_project_save,
            "sync_request": self._handle_sync_request,
            "latency_report": self._handle_latency_report,
            "track_lock": self._handle_track_lock,
            "track_unlock": self._handle_track_unlock
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection for DAW collaboration"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"DAW session connection established for user {user_id}")
            
            # Send connection confirmation
            await self._send_to_user(user_id, {
                "type": "connection_established",
                "user_id": user_id,
                "supported_daws": [daw.value for daw in DAWType],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_daw_message(user_id, message)
                    
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
                    await self._send_error(user_id, str(e))
        
        except Exception as e:
            logger.error(f"WebSocket connection error for {user_id}: {e}")
        
        finally:
            await self._cleanup_user_connection(user_id)
    
    async def _handle_daw_message(self, user_id: str, message: Dict[str, Any]):
        """Route DAW messages to appropriate handlers"""
        message_type = message.get("type")
        handler = self.message_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def create_daw_session(self, project_id: str, project_name: str,
                               host_id: str, daw_type: str,
                               audio_settings: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Create new DAW collaboration session"""
        try:
            session_id = f"daw_{uuid.uuid4().hex[:12]}"
            
            # Create audio settings
            settings = AudioSettings(
                sample_rate=audio_settings.get("sample_rate", 44100),
                bit_depth=audio_settings.get("bit_depth", 24),
                buffer_size=audio_settings.get("buffer_size", 256),
                latency_compensation=audio_settings.get("latency_compensation", 0.0),
                master_volume=audio_settings.get("master_volume", 0.8),
                metronome_enabled=audio_settings.get("metronome_enabled", True),
                click_track_volume=audio_settings.get("click_track_volume", 0.5)
            )
            
            # Create initial timeline position
            timeline_pos = TimelinePosition(
                bars=1, beats=1, ticks=0, samples=0,
                tempo=audio_settings.get("tempo", 120.0)
            )
            
            # Create DAW project
            project = DAWProject(
                project_id=project_id,
                project_name=project_name,
                daw_type=DAWType(daw_type),
                audio_settings=settings,
                timeline_position=timeline_pos,
                session_state=SessionState.STOPPED
            )
            
            # Create session
            session = DAWSession(
                session_id=session_id,
                project_id=project_id,
                host_id=host_id,
                project=project
            )
            
            self.daw_sessions[session_id] = session
            
            logger.info(f"DAW session {session_id} created for project {project_id}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "project_id": project_id,
                "daw_type": daw_type,
                "audio_settings": audio_settings,
                "message": "DAW session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating DAW session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_join_session(self, user_id: str, message: Dict[str, Any]):
        """Join DAW session"""
        try:
            session_id = message.get("session_id")
            username = message.get("username", f"User_{user_id}")
            daw_type = message.get("daw_type", "reaper")
            daw_version = message.get("daw_version", "1.0")
            audio_interface = message.get("audio_interface", "default")
            latency_compensation = message.get("latency_compensation", 0.0)
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "DAW session not found")
                return
            
            # Determine permission level
            permission = PermissionLevel.ADMIN if user_id == session.host_id else PermissionLevel.PARTICIPANT
            
            # Create participant
            participant = SessionParticipant(
                user_id=user_id,
                username=username,
                permission_level=permission,
                daw_type=DAWType(daw_type),
                daw_version=daw_version,
                latency_compensation=latency_compensation,
                audio_interface=audio_interface,
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            session.participants[user_id] = participant
            session.last_sync = datetime.utcnow()
            
            # Send session data to user
            await self._send_to_user(user_id, {
                "type": "session_joined",
                "session": await self._serialize_session(session),
                "your_permission": permission.value,
                "participants": [
                    {
                        "user_id": p.user_id,
                        "username": p.username,
                        "daw_type": p.daw_type.value,
                        "permission_level": p.permission_level.value,
                        "is_connected": p.is_connected
                    }
                    for p in session.participants.values()
                ]
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_joined",
                "participant": {
                    "user_id": user_id,
                    "username": username,
                    "daw_type": daw_type,
                    "permission_level": permission.value,
                    "joined_at": participant.joined_at.isoformat()
                }
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} joined DAW session {session_id}")
            
        except Exception as e:
            logger.error(f"Error joining DAW session: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_leave_session(self, user_id: str, message: Dict[str, Any]):
        """Leave DAW session"""
        try:
            session_id = message.get("session_id")
            session = self.daw_sessions.get(session_id)
            
            if session and user_id in session.participants:
                participant = session.participants.pop(user_id)
                
                # Release any locked tracks
                for track_id in participant.controlled_tracks:
                    await self._release_track_lock(session_id, track_id)
                
                # Notify other participants
                await self._broadcast_to_session(session_id, {
                    "type": "participant_left",
                    "user_id": user_id,
                    "username": participant.username,
                    "left_at": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
                
                logger.info(f"User {user_id} left DAW session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving DAW session: {e}")
    
    async def _handle_transport_control(self, user_id: str, message: Dict[str, Any]):
        """Handle transport controls (play, stop, record, etc.)"""
        try:
            session_id = message.get("session_id")
            action = message.get("action")  # play, stop, record, pause
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant or participant.permission_level == PermissionLevel.LISTEN_ONLY:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            # Update session state
            if action == "play":
                session.project.session_state = SessionState.PLAYING
            elif action == "stop":
                session.project.session_state = SessionState.STOPPED
            elif action == "record":
                session.project.session_state = SessionState.RECORDING
            elif action == "pause":
                session.project.session_state = SessionState.PAUSED
            
            session.project.modified_at = datetime.utcnow()
            session.last_sync = datetime.utcnow()
            
            # Broadcast transport change
            await self._broadcast_to_session(session_id, {
                "type": "transport_changed",
                "action": action,
                "session_state": session.project.session_state.value,
                "timeline_position": self._serialize_timeline_position(session.project.timeline_position),
                "triggered_by": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Transport {action} triggered by {user_id} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling transport control: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_timeline_position(self, user_id: str, message: Dict[str, Any]):
        """Handle timeline position updates"""
        try:
            session_id = message.get("session_id")
            position_data = message.get("position")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                return
            
            # Update timeline position
            session.project.timeline_position = TimelinePosition(
                bars=position_data.get("bars", 1),
                beats=position_data.get("beats", 1),
                ticks=position_data.get("ticks", 0),
                samples=position_data.get("samples", 0),
                tempo=position_data.get("tempo", 120.0)
            )
            
            session.last_sync = datetime.utcnow()
            
            # Broadcast position update
            await self._broadcast_to_session(session_id, {
                "type": "timeline_position_updated",
                "position": self._serialize_timeline_position(session.project.timeline_position),
                "updated_by": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling timeline position: {e}")
    
    async def _handle_track_update(self, user_id: str, message: Dict[str, Any]):
        """Handle track updates"""
        try:
            session_id = message.get("session_id")
            track_data = message.get("track")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant or participant.permission_level == PermissionLevel.LISTEN_ONLY:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            track_id = track_data.get("track_id")
            
            # Check if user has control of this track
            if track_id not in participant.controlled_tracks and participant.permission_level not in [PermissionLevel.PRODUCER, PermissionLevel.ADMIN]:
                await self._send_error(user_id, "Track is locked by another user")
                return
            
            # Update track
            if track_id in session.project.tracks:
                track = session.project.tracks[track_id]
                
                # Update track properties
                if "volume" in track_data:
                    track.volume = track_data["volume"]
                if "pan" in track_data:
                    track.pan = track_data["pan"]
                if "muted" in track_data:
                    track.muted = track_data["muted"]
                if "soloed" in track_data:
                    track.soloed = track_data["soloed"]
                if "record_enabled" in track_data:
                    track.record_enabled = track_data["record_enabled"]
                
                session.project.modified_at = datetime.utcnow()
                session.last_sync = datetime.utcnow()
                
                # Broadcast track update
                await self._broadcast_to_session(session_id, {
                    "type": "track_updated",
                    "track": await self._serialize_track(track),
                    "updated_by": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
                
                logger.info(f"Track {track_id} updated by {user_id} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling track update: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_plugin_update(self, user_id: str, message: Dict[str, Any]):
        """Handle plugin parameter updates"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            plugin_id = message.get("plugin_id")
            parameters = message.get("parameters", {})
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                return
            
            # Find and update plugin
            if track_id in session.project.tracks:
                track = session.project.tracks[track_id]
                
                for plugin in track.plugins:
                    if plugin.plugin_id == plugin_id:
                        plugin.parameters.update(parameters)
                        break
                
                session.last_sync = datetime.utcnow()
                
                # Broadcast plugin update
                await self._broadcast_to_session(session_id, {
                    "type": "plugin_updated",
                    "track_id": track_id,
                    "plugin_id": plugin_id,
                    "parameters": parameters,
                    "updated_by": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling plugin update: {e}")
    
    async def _handle_audio_stream(self, user_id: str, message: Dict[str, Any]):
        """Handle audio stream data"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            audio_data = message.get("audio_data")  # Base64 encoded
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            # Store audio stream data
            stream_key = f"{session_id}:{track_id}:{user_id}"
            self.audio_streams[stream_key] = base64.b64decode(audio_data)
            
            # Broadcast audio stream to other participants
            await self._broadcast_to_session(session_id, {
                "type": "audio_stream_received",
                "track_id": track_id,
                "from_user": user_id,
                "audio_data": audio_data,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling audio stream: {e}")
    
    async def _handle_midi_event(self, user_id: str, message: Dict[str, Any]):
        """Handle MIDI events"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            midi_data = message.get("midi_event")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            # Create MIDI event
            midi_event = MIDIEvent(
                event_id=f"midi_{uuid.uuid4().hex[:8]}",
                timestamp=midi_data.get("timestamp", time.time()),
                channel=midi_data.get("channel", 1),
                note_number=midi_data.get("note_number"),
                velocity=midi_data.get("velocity"),
                controller_number=midi_data.get("controller_number"),
                controller_value=midi_data.get("controller_value"),
                event_type=midi_data.get("event_type", "note_on")
            )
            
            # Broadcast MIDI event
            await self._broadcast_to_session(session_id, {
                "type": "midi_event_received",
                "track_id": track_id,
                "from_user": user_id,
                "midi_event": {
                    "timestamp": midi_event.timestamp,
                    "channel": midi_event.channel,
                    "note_number": midi_event.note_number,
                    "velocity": midi_event.velocity,
                    "event_type": midi_event.event_type
                },
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling MIDI event: {e}")
    
    async def _handle_automation_update(self, user_id: str, message: Dict[str, Any]):
        """Handle automation data updates"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            parameter_name = message.get("parameter")
            automation_points = message.get("automation_points", [])
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            # Update automation data
            if track_id in session.project.tracks:
                track = session.project.tracks[track_id]
                track.automation_data[parameter_name] = [
                    (point["time"], point["value"]) for point in automation_points
                ]
                
                session.last_sync = datetime.utcnow()
                
                # Broadcast automation update
                await self._broadcast_to_session(session_id, {
                    "type": "automation_updated",
                    "track_id": track_id,
                    "parameter": parameter_name,
                    "automation_points": automation_points,
                    "updated_by": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling automation update: {e}")
    
    async def _handle_project_save(self, user_id: str, message: Dict[str, Any]):
        """Handle project save request"""
        try:
            session_id = message.get("session_id")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant or participant.permission_level not in [PermissionLevel.PRODUCER, PermissionLevel.ADMIN]:
                await self._send_error(user_id, "Insufficient permissions to save")
                return
            
            # Save project state (in production, would save to database)
            session.project.modified_at = datetime.utcnow()
            
            # Notify all participants
            await self._broadcast_to_session(session_id, {
                "type": "project_saved",
                "saved_by": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Project saved by {user_id} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling project save: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_sync_request(self, user_id: str, message: Dict[str, Any]):
        """Handle synchronization request"""
        try:
            session_id = message.get("session_id")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Send full session state
            await self._send_to_user(user_id, {
                "type": "full_sync",
                "session": await self._serialize_session(session),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling sync request: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_latency_report(self, user_id: str, message: Dict[str, Any]):
        """Handle latency compensation reports"""
        try:
            session_id = message.get("session_id")
            latency_ms = message.get("latency_ms", 0.0)
            
            session = self.daw_sessions.get(session_id)
            if not session:
                return
            
            participant = session.participants.get(user_id)
            if participant:
                participant.latency_compensation = latency_ms
                participant.last_activity = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error handling latency report: {e}")
    
    async def _handle_track_lock(self, user_id: str, message: Dict[str, Any]):
        """Handle track locking for exclusive control"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            
            session = self.daw_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant:
                await self._send_error(user_id, "Not a participant")
                return
            
            # Check if track is already locked
            for p in session.participants.values():
                if track_id in p.controlled_tracks and p.user_id != user_id:
                    await self._send_error(user_id, f"Track locked by {p.username}")
                    return
            
            # Lock track
            participant.controlled_tracks.add(track_id)
            
            # Notify others
            await self._broadcast_to_session(session_id, {
                "type": "track_locked",
                "track_id": track_id,
                "locked_by": user_id,
                "username": participant.username,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
            # Confirm to user
            await self._send_to_user(user_id, {
                "type": "track_lock_acquired",
                "track_id": track_id
            })
            
        except Exception as e:
            logger.error(f"Error handling track lock: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_track_unlock(self, user_id: str, message: Dict[str, Any]):
        """Handle track unlocking"""
        try:
            session_id = message.get("session_id")
            track_id = message.get("track_id")
            
            await self._release_track_lock(session_id, track_id, user_id)
            
        except Exception as e:
            logger.error(f"Error handling track unlock: {e}")
            await self._send_error(user_id, str(e))
    
    async def _release_track_lock(self, session_id: str, track_id: str, user_id: str = None):
        """Release track lock"""
        session = self.daw_sessions.get(session_id)
        if not session:
            return
        
        for participant in session.participants.values():
            if track_id in participant.controlled_tracks:
                if user_id is None or participant.user_id == user_id:
                    participant.controlled_tracks.remove(track_id)
                    
                    # Notify others
                    await self._broadcast_to_session(session_id, {
                        "type": "track_unlocked",
                        "track_id": track_id,
                        "unlocked_by": participant.user_id,
                        "username": participant.username,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    break
    
    async def _serialize_session(self, session: DAWSession) -> Dict[str, Any]:
        """Serialize session for transmission"""
        return {
            "session_id": session.session_id,
            "project_id": session.project_id,
            "host_id": session.host_id,
            "project": {
                "project_name": session.project.project_name,
                "daw_type": session.project.daw_type.value,
                "session_state": session.project.session_state.value,
                "audio_settings": {
                    "sample_rate": session.project.audio_settings.sample_rate,
                    "bit_depth": session.project.audio_settings.bit_depth,
                    "buffer_size": session.project.audio_settings.buffer_size,
                    "master_volume": session.project.audio_settings.master_volume,
                    "tempo": session.project.timeline_position.tempo
                },
                "timeline_position": self._serialize_timeline_position(session.project.timeline_position),
                "tracks": {
                    track_id: await self._serialize_track(track)
                    for track_id, track in session.project.tracks.items()
                }
            },
            "sync_enabled": session.sync_enabled,
            "created_at": session.created_at.isoformat(),
            "last_sync": session.last_sync.isoformat()
        }
    
    def _serialize_timeline_position(self, position: TimelinePosition) -> Dict[str, Any]:
        """Serialize timeline position"""
        return {
            "bars": position.bars,
            "beats": position.beats,
            "ticks": position.ticks,
            "samples": position.samples,
            "tempo": position.tempo,
            "time_signature": f"{position.time_signature_numerator}/{position.time_signature_denominator}"
        }
    
    async def _serialize_track(self, track: DAWTrack) -> Dict[str, Any]:
        """Serialize track for transmission"""
        return {
            "track_id": track.track_id,
            "track_name": track.track_name,
            "track_type": track.track_type.value,
            "track_number": track.track_number,
            "volume": track.volume,
            "pan": track.pan,
            "muted": track.muted,
            "soloed": track.soloed,
            "record_enabled": track.record_enabled,
            "monitor_enabled": track.monitor_enabled,
            "input_source": track.input_source,
            "output_destination": track.output_destination,
            "color": track.color,
            "plugins": [
                {
                    "plugin_id": plugin.plugin_id,
                    "plugin_name": plugin.plugin_name,
                    "plugin_type": plugin.plugin_type,
                    "parameters": plugin.parameters,
                    "enabled": plugin.enabled
                }
                for plugin in track.plugins
            ],
            "audio_regions_count": len(track.audio_regions),
            "midi_regions_count": len(track.midi_regions)
        }
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        websocket = self.websocket_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                await self._cleanup_user_connection(user_id)
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                   exclude_user: Optional[str] = None):
        """Broadcast message to all users in session"""
        session = self.daw_sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.participants:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _send_error(self, user_id: str, error_message: str):
        """Send error message to user"""
        await self._send_to_user(user_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _cleanup_user_connection(self, user_id: str):
        """Cleanup user connection"""
        try:
            # Remove WebSocket connection
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
            
            # Remove from all DAW sessions
            for session_id, session in self.daw_sessions.items():
                if user_id in session.participants:
                    await self._handle_leave_session(user_id, {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = self.daw_sessions.get(session_id)
        if not session:
            return None
        
        return await self._serialize_session(session)
    
    async def export_project(self, session_id: str, format_type: str = "json") -> Dict[str, Any]:
        """Export DAW project"""
        session = self.daw_sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        if format_type == "json":
            return {
                "status": "success",
                "format": "json",
                "data": await self._serialize_session(session)
            }
        
        return {"status": "error", "message": f"Unsupported format: {format_type}"}


# Export the manager
__all__ = ['VirtualDAWSessionManager', 'DAWType', 'TrackType', 'SessionState',
           'PermissionLevel', 'AudioSettings', 'TimelinePosition', 'MIDIEvent',
           'AudioRegion', 'MIDIRegion', 'PluginState', 'DAWTrack', 'DAWProject',
           'SessionParticipant', 'DAWSession']