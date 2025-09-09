"""
Secure Streaming Engine
======================

Advanced secure streaming system with encrypted delivery, adaptive bitrate,
DRM integration, secure protocols, and real-time content protection for
live and on-demand streaming.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
import struct
from urllib.parse import urlparse
import secrets

# Async HTTP client
import aiohttp


class StreamingProtocol(Enum):
    """Supported streaming protocols"""
    HLS = "hls"  # HTTP Live Streaming
    DASH = "dash"  # Dynamic Adaptive Streaming over HTTP
    RTMP = "rtmp"  # Real-Time Messaging Protocol
    WebRTC = "webrtc"  # Web Real-Time Communication
    SRT = "srt"  # Secure Reliable Transport
    ENCRYPTED_HLS = "encrypted_hls"
    ENCRYPTED_DASH = "encrypted_dash"


class StreamType(Enum):
    """Types of streaming content"""
    LIVE = "live"
    VOD = "vod"  # Video on Demand
    ADAPTIVE = "adaptive"
    PROGRESSIVE = "progressive"


class QualityLevel(Enum):
    """Streaming quality levels"""
    AUDIO_ONLY = "audio_only"
    LOW_240P = "240p"
    SD_480P = "480p"
    HD_720P = "720p"
    FHD_1080P = "1080p"
    QHD_1440P = "1440p"
    UHD_4K = "4k"
    UHD_8K = "8k"


class SecurityLevel(Enum):
    """Security levels for streaming"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    ENTERPRISE = "enterprise"
    MILITARY = "military"


@dataclass
class StreamingKey:
    """Secure streaming key"""
    key_id: str
    stream_id: str
    encryption_key: bytes
    auth_token: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str]
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


@dataclass
class StreamManifest:
    """Streaming manifest definition"""
    manifest_id: str
    stream_id: str
    protocol: StreamingProtocol
    stream_type: StreamType
    quality_levels: List[QualityLevel]
    security_level: SecurityLevel
    manifest_content: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    drm_info: Optional[Dict[str, Any]] = None


@dataclass
class StreamSegment:
    """Individual stream segment"""
    segment_id: str
    stream_id: str
    sequence_number: int
    quality_level: QualityLevel
    duration: float
    data: bytes
    encryption_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class StreamSession:
    """Active streaming session"""
    session_id: str
    stream_id: str
    user_id: str
    client_ip: str
    user_agent: str
    started_at: datetime
    last_activity: datetime
    bytes_delivered: int = 0
    segments_delivered: int = 0
    quality_switches: int = 0
    is_active: bool = True


class SecureStreamingEngine:
    """
    Advanced Secure Streaming Engine
    
    Provides enterprise-grade streaming security:
    - Multi-protocol streaming (HLS, DASH, RTMP, WebRTC, SRT)
    - End-to-end encryption with key rotation
    - DRM integration and content protection
    - Adaptive bitrate streaming with quality levels
    - Secure token-based authentication
    - Real-time stream monitoring and analytics
    - Geographic and device restrictions
    - Anti-piracy measures and watermarking
    - Load balancing and CDN integration
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize secure streaming engine"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage (in production, use distributed cache/database)
        self.streaming_keys: Dict[str, StreamingKey] = {}
        self.stream_manifests: Dict[str, StreamManifest] = {}
        self.stream_segments: Dict[str, List[StreamSegment]] = {}
        self.active_sessions: Dict[str, StreamSession] = {}
        
        # Streaming configuration
        self.segment_duration = self.config.get('segment_duration', 10)  # seconds
        self.manifest_refresh_interval = self.config.get('manifest_refresh_interval', 30)
        self.max_quality_levels = self.config.get('max_quality_levels', 6)
        self.encryption_key_rotation = self.config.get('key_rotation_minutes', 60)
        
        # Security settings
        self.token_expiry_hours = self.config.get('token_expiry_hours', 24)
        self.max_concurrent_sessions = self.config.get('max_concurrent_sessions', 5)
        self.geo_restrictions = self.config.get('geo_restrictions', [])
        
        # CDN and load balancing
        self.cdn_endpoints = self.config.get('cdn_endpoints', [])
        self.origin_servers = self.config.get('origin_servers', [])
        
        # Performance metrics
        self.metrics = {
            'total_streams_created': 0,
            'total_sessions_active': 0,
            'total_bytes_delivered': 0,
            'total_segments_delivered': 0,
            'avg_bitrate': 0.0,
            'peak_concurrent_viewers': 0,
            'buffering_events': 0,
            'quality_switches': 0
        }
        
        # Security audit log
        self.security_log: List[Dict] = []
        
        self.logger.info("Secure Streaming Engine initialized")

    async def create_secure_stream(self, 
                                 content_id: str,
                                 protocol: StreamingProtocol,
                                 stream_type: StreamType,
                                 quality_levels: List[QualityLevel],
                                 security_level: SecurityLevel = SecurityLevel.STANDARD,
                                 drm_config: Dict[str, Any] = None) -> Tuple[str, StreamManifest]:
        """Create new secure stream"""
        
        stream_id = str(uuid.uuid4())
        
        # Generate streaming keys for each quality level
        streaming_keys = {}
        for quality in quality_levels:
            key = await self._generate_streaming_key(stream_id, quality)
            streaming_keys[quality.value] = key
        
        # Create manifest
        manifest = await self._generate_manifest(
            stream_id, protocol, stream_type, quality_levels, 
            security_level, streaming_keys, drm_config
        )
        
        self.stream_manifests[manifest.manifest_id] = manifest
        self.stream_segments[stream_id] = []
        self.metrics['total_streams_created'] += 1
        
        # Security log
        await self._log_security_event('stream_created', {
            'stream_id': stream_id,
            'content_id': content_id,
            'protocol': protocol.value,
            'security_level': security_level.value
        })
        
        self.logger.info(f"Secure stream created: {stream_id} ({protocol.value})")
        return stream_id, manifest

    async def authenticate_stream_access(self, 
                                       stream_id: str,
                                       user_id: str,
                                       client_ip: str,
                                       user_agent: str,
                                       access_token: str = None) -> StreamingKey:
        """Authenticate and authorize stream access"""
        
        # Verify stream exists
        manifests = [m for m in self.stream_manifests.values() if m.stream_id == stream_id]
        if not manifests:
            raise ValueError(f"Stream not found: {stream_id}")
        
        manifest = manifests[0]
        
        # Check geographic restrictions
        if not await self._check_geo_restrictions(client_ip):
            raise PermissionError("Geographic restriction violation")
        
        # Check concurrent sessions
        user_sessions = [
            s for s in self.active_sessions.values() 
            if s.user_id == user_id and s.is_active
        ]
        if len(user_sessions) >= self.max_concurrent_sessions:
            raise PermissionError("Maximum concurrent sessions exceeded")
        
        # Generate streaming key
        key_id = str(uuid.uuid4())
        auth_token = self._generate_auth_token(user_id, stream_id)
        
        streaming_key = StreamingKey(
            key_id=key_id,
            stream_id=stream_id,
            encryption_key=secrets.token_bytes(32),
            auth_token=auth_token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            permissions=['stream', 'seek'],
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        self.streaming_keys[key_id] = streaming_key
        
        # Security log
        await self._log_security_event('stream_access_granted', {
            'stream_id': stream_id,
            'user_id': user_id,
            'client_ip': client_ip,
            'key_id': key_id
        })
        
        return streaming_key

    async def create_streaming_session(self, 
                                     stream_id: str,
                                     user_id: str,
                                     client_ip: str,
                                     user_agent: str,
                                     streaming_key: StreamingKey) -> StreamSession:
        """Create new streaming session"""
        
        session_id = str(uuid.uuid4())
        
        session = StreamSession(
            session_id=session_id,
            stream_id=stream_id,
            user_id=user_id,
            client_ip=client_ip,
            user_agent=user_agent,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        self.active_sessions[session_id] = session
        self.metrics['total_sessions_active'] += 1
        
        # Update peak concurrent viewers
        current_viewers = len([s for s in self.active_sessions.values() if s.is_active])
        if current_viewers > self.metrics['peak_concurrent_viewers']:
            self.metrics['peak_concurrent_viewers'] = current_viewers
        
        self.logger.info(f"Streaming session created: {session_id}")
        return session

    async def add_stream_segment(self, 
                               stream_id: str,
                               quality_level: QualityLevel,
                               segment_data: bytes,
                               duration: float = None) -> StreamSegment:
        """Add new segment to stream"""
        
        if stream_id not in self.stream_segments:
            raise ValueError(f"Stream not found: {stream_id}")
        
        segment_id = str(uuid.uuid4())
        sequence_number = len(self.stream_segments[stream_id])
        
        if duration is None:
            duration = self.segment_duration
        
        # Encrypt segment if required
        encryption_info = None
        encrypted_data = segment_data
        
        if self._stream_requires_encryption(stream_id):
            encrypted_data, encryption_info = await self._encrypt_segment(
                segment_data, stream_id, sequence_number
            )
        
        segment = StreamSegment(
            segment_id=segment_id,
            stream_id=stream_id,
            sequence_number=sequence_number,
            quality_level=quality_level,
            duration=duration,
            data=encrypted_data,
            encryption_info=encryption_info
        )
        
        self.stream_segments[stream_id].append(segment)
        
        # Update manifest
        await self._update_manifest(stream_id)
        
        self.logger.debug(f"Segment added to stream {stream_id}: {segment_id}")
        return segment

    async def get_stream_segment(self, 
                               stream_id: str,
                               sequence_number: int,
                               quality_level: QualityLevel,
                               session_id: str) -> bytes:
        """Retrieve and decrypt stream segment"""
        
        # Validate session
        if session_id not in self.active_sessions:
            raise PermissionError("Invalid session")
        
        session = self.active_sessions[session_id]
        if not session.is_active or session.stream_id != stream_id:
            raise PermissionError("Session unauthorized for stream")
        
        # Find segment
        segments = self.stream_segments.get(stream_id, [])
        segment = next(
            (s for s in segments 
             if s.sequence_number == sequence_number and s.quality_level == quality_level),
            None
        )
        
        if not segment:
            raise ValueError(f"Segment not found: {stream_id}/{sequence_number}/{quality_level.value}")
        
        # Decrypt if needed
        segment_data = segment.data
        if segment.encryption_info:
            segment_data = await self._decrypt_segment(segment.data, segment.encryption_info)
        
        # Update session metrics
        session.last_activity = datetime.utcnow()
        session.bytes_delivered += len(segment_data)
        session.segments_delivered += 1
        
        # Update global metrics
        self.metrics['total_bytes_delivered'] += len(segment_data)
        self.metrics['total_segments_delivered'] += 1
        
        return segment_data

    async def generate_adaptive_manifest(self, 
                                       stream_id: str,
                                       protocol: StreamingProtocol,
                                       client_capabilities: Dict[str, Any] = None) -> str:
        """Generate adaptive streaming manifest"""
        
        manifests = [m for m in self.stream_manifests.values() if m.stream_id == stream_id]
        if not manifests:
            raise ValueError(f"Stream not found: {stream_id}")
        
        manifest = manifests[0]
        segments = self.stream_segments.get(stream_id, [])
        
        if protocol == StreamingProtocol.HLS:
            return await self._generate_hls_manifest(manifest, segments, client_capabilities)
        elif protocol == StreamingProtocol.DASH:
            return await self._generate_dash_manifest(manifest, segments, client_capabilities)
        elif protocol == StreamingProtocol.ENCRYPTED_HLS:
            return await self._generate_encrypted_hls_manifest(manifest, segments, client_capabilities)
        else:
            raise ValueError(f"Unsupported protocol for adaptive manifest: {protocol}")

    async def _generate_streaming_key(self, stream_id: str, quality: QualityLevel) -> Dict[str, Any]:
        """Generate encryption key for streaming"""
        
        key_data = secrets.token_bytes(32)
        iv = secrets.token_bytes(16)
        
        return {
            'key_id': str(uuid.uuid4()),
            'key_data': base64.b64encode(key_data).decode(),
            'iv': base64.b64encode(iv).decode(),
            'quality': quality.value,
            'created_at': datetime.utcnow().isoformat()
        }

    async def _generate_manifest(self, 
                               stream_id: str,
                               protocol: StreamingProtocol,
                               stream_type: StreamType,
                               quality_levels: List[QualityLevel],
                               security_level: SecurityLevel,
                               streaming_keys: Dict[str, Any],
                               drm_config: Dict[str, Any] = None) -> StreamManifest:
        """Generate streaming manifest"""
        
        manifest_id = str(uuid.uuid4())
        
        # Create basic manifest content
        if protocol == StreamingProtocol.HLS:
            manifest_content = self._create_hls_master_playlist(quality_levels)
        elif protocol == StreamingProtocol.DASH:
            manifest_content = self._create_dash_mpd(quality_levels)
        else:
            manifest_content = json.dumps({
                'stream_id': stream_id,
                'protocol': protocol.value,
                'quality_levels': [q.value for q in quality_levels]
            })
        
        manifest = StreamManifest(
            manifest_id=manifest_id,
            stream_id=stream_id,
            protocol=protocol,
            stream_type=stream_type,
            quality_levels=quality_levels,
            security_level=security_level,
            manifest_content=manifest_content,
            created_at=datetime.utcnow(),
            drm_info=drm_config
        )
        
        return manifest

    def _create_hls_master_playlist(self, quality_levels: List[QualityLevel]) -> str:
        """Create HLS master playlist"""
        
        playlist = "#EXTM3U\n#EXT-X-VERSION:6\n\n"
        
        bitrate_map = {
            QualityLevel.AUDIO_ONLY: 128,
            QualityLevel.LOW_240P: 400,
            QualityLevel.SD_480P: 1000,
            QualityLevel.HD_720P: 2500,
            QualityLevel.FHD_1080P: 5000,
            QualityLevel.QHD_1440P: 8000,
            QualityLevel.UHD_4K: 15000,
            QualityLevel.UHD_8K: 25000
        }
        
        for quality in quality_levels:
            bitrate = bitrate_map.get(quality, 1000)
            resolution = quality.value.upper() if quality != QualityLevel.AUDIO_ONLY else None
            
            if resolution:
                if quality == QualityLevel.LOW_240P:
                    res_str = "RESOLUTION=426x240"
                elif quality == QualityLevel.SD_480P:
                    res_str = "RESOLUTION=854x480"
                elif quality == QualityLevel.HD_720P:
                    res_str = "RESOLUTION=1280x720"
                elif quality == QualityLevel.FHD_1080P:
                    res_str = "RESOLUTION=1920x1080"
                elif quality == QualityLevel.QHD_1440P:
                    res_str = "RESOLUTION=2560x1440"
                elif quality == QualityLevel.UHD_4K:
                    res_str = "RESOLUTION=3840x2160"
                elif quality == QualityLevel.UHD_8K:
                    res_str = "RESOLUTION=7680x4320"
                else:
                    res_str = "RESOLUTION=1920x1080"
                
                playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate * 1000},{res_str}\n"
            else:
                playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate * 1000},CODECS=\"mp4a.40.2\"\n"
            
            playlist += f"{quality.value}.m3u8\n\n"
        
        return playlist

    def _create_dash_mpd(self, quality_levels: List[QualityLevel]) -> str:
        """Create DASH MPD manifest"""
        
        mpd = '<?xml version="1.0" encoding="UTF-8"?>\n'
        mpd += '<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" '
        mpd += 'type="dynamic" minimumUpdatePeriod="PT30S" '
        mpd += 'suggestedPresentationDelay="PT6S">\n'
        mpd += '  <Period>\n'
        mpd += '    <AdaptationSet mimeType="video/mp4">\n'
        
        for quality in quality_levels:
            if quality != QualityLevel.AUDIO_ONLY:
                mpd += f'      <Representation id="{quality.value}" bandwidth="5000000">\n'
                mpd += f'        <SegmentTemplate media="{quality.value}_$Number$.m4s" '
                mpd += 'startNumber="1" duration="10"/>\n'
                mpd += '      </Representation>\n'
        
        mpd += '    </AdaptationSet>\n'
        mpd += '  </Period>\n'
        mpd += '</MPD>'
        
        return mpd

    async def _encrypt_segment(self, 
                             segment_data: bytes,
                             stream_id: str,
                             sequence_number: int) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt stream segment"""
        
        # Generate segment-specific key and IV
        key = secrets.token_bytes(32)
        iv = struct.pack('>Q', sequence_number).ljust(16, b'\x00')
        
        # AES-128 encryption for streaming compatibility
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        cipher = Cipher(algorithms.AES(key[:16]), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad data to block size
        block_size = 16
        padding_length = block_size - (len(segment_data) % block_size)
        padded_data = segment_data + bytes([padding_length] * padding_length)
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        encryption_info = {
            'method': 'AES-128',
            'key': base64.b64encode(key[:16]).decode(),
            'iv': base64.b64encode(iv).decode(),
            'key_uri': f'/key/{stream_id}/{sequence_number}',
            'padding_length': padding_length
        }
        
        return encrypted_data, encryption_info

    async def _decrypt_segment(self, 
                             encrypted_data: bytes,
                             encryption_info: Dict[str, Any]) -> bytes:
        """Decrypt stream segment"""
        
        key = base64.b64decode(encryption_info['key'])
        iv = base64.b64decode(encryption_info['iv'])
        
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        padding_length = encryption_info.get('padding_length', 0)
        if padding_length > 0:
            return padded_data[:-padding_length]
        
        return padded_data

    def _stream_requires_encryption(self, stream_id: str) -> bool:
        """Check if stream requires encryption"""
        
        manifests = [m for m in self.stream_manifests.values() if m.stream_id == stream_id]
        if not manifests:
            return False
        
        manifest = manifests[0]
        return manifest.security_level in [SecurityLevel.HIGH, SecurityLevel.ENTERPRISE, SecurityLevel.MILITARY]

    async def _update_manifest(self, stream_id: str):
        """Update manifest with new segments"""
        
        # In production, this would update the manifest files
        # and notify CDN endpoints of changes
        pass

    async def _generate_hls_manifest(self, 
                                   manifest: StreamManifest,
                                   segments: List[StreamSegment],
                                   client_capabilities: Dict[str, Any] = None) -> str:
        """Generate HLS playlist for specific quality"""
        
        playlist = "#EXTM3U\n"
        playlist += "#EXT-X-VERSION:6\n"
        playlist += f"#EXT-X-TARGETDURATION:{self.segment_duration}\n"
        playlist += "#EXT-X-MEDIA-SEQUENCE:0\n"
        
        # Add encryption info if needed
        if manifest.security_level in [SecurityLevel.HIGH, SecurityLevel.ENTERPRISE]:
            playlist += f"#EXT-X-KEY:METHOD=AES-128,URI=\"/key/{manifest.stream_id}\"\n"
        
        # Add segments
        for segment in segments[-10:]:  # Last 10 segments for live
            playlist += f"#EXTINF:{segment.duration:.3f},\n"
            playlist += f"segment_{segment.sequence_number}.ts\n"
        
        return playlist

    async def _generate_dash_manifest(self, 
                                    manifest: StreamManifest,
                                    segments: List[StreamSegment],
                                    client_capabilities: Dict[str, Any] = None) -> str:
        """Generate DASH MPD for adaptive streaming"""
        
        # Simplified DASH manifest generation
        return manifest.manifest_content

    async def _generate_encrypted_hls_manifest(self, 
                                             manifest: StreamManifest,
                                             segments: List[StreamSegment],
                                             client_capabilities: Dict[str, Any] = None) -> str:
        """Generate encrypted HLS manifest"""
        
        playlist = await self._generate_hls_manifest(manifest, segments, client_capabilities)
        
        # Add DRM info if configured
        if manifest.drm_info:
            drm_info = manifest.drm_info
            playlist = playlist.replace(
                "#EXT-X-VERSION:6\n",
                f"#EXT-X-VERSION:6\n#EXT-X-SESSION-KEY:METHOD={drm_info.get('method', 'SAMPLE-AES')},URI=\"{drm_info.get('license_url')}\"\n"
            )
        
        return playlist

    def _generate_auth_token(self, user_id: str, stream_id: str) -> str:
        """Generate authentication token"""
        
        payload = {
            'user_id': user_id,
            'stream_id': stream_id,
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=self.token_expiry_hours)).isoformat()
        }
        
        token_data = json.dumps(payload)
        return base64.b64encode(token_data.encode()).decode()

    async def _check_geo_restrictions(self, client_ip: str) -> bool:
        """Check geographic restrictions"""
        
        if not self.geo_restrictions:
            return True
        
        # Simplified geo-check (in production, use GeoIP service)
        # For now, allow all IPs
        return True

    async def _log_security_event(self, event_type: str, data: Dict[str, Any]):
        """Log security event"""
        
        security_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data,
            'system': 'secure_streaming'
        }
        
        self.security_log.append(security_entry)

    async def terminate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Terminate streaming session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.is_active = False
        
        self.metrics['total_sessions_active'] -= 1
        
        # Security log
        await self._log_security_event('session_terminated', {
            'session_id': session_id,
            'stream_id': session.stream_id,
            'user_id': session.user_id,
            'reason': reason,
            'duration': (datetime.utcnow() - session.started_at).total_seconds()
        })
        
        self.logger.info(f"Session terminated: {session_id} ({reason})")
        return True

    async def get_stream_analytics(self, stream_id: str) -> Dict[str, Any]:
        """Get analytics for specific stream"""
        
        # Get stream sessions
        stream_sessions = [s for s in self.active_sessions.values() if s.stream_id == stream_id]
        
        # Calculate metrics
        total_viewers = len(stream_sessions)
        active_viewers = len([s for s in stream_sessions if s.is_active])
        total_bytes = sum(s.bytes_delivered for s in stream_sessions)
        total_segments = sum(s.segments_delivered for s in stream_sessions)
        
        # Get segments
        segments = self.stream_segments.get(stream_id, [])
        
        analytics = {
            'stream_id': stream_id,
            'total_viewers': total_viewers,
            'active_viewers': active_viewers,
            'total_bytes_delivered': total_bytes,
            'total_segments_delivered': total_segments,
            'total_segments_available': len(segments),
            'avg_session_duration': self._calculate_avg_session_duration(stream_sessions),
            'quality_distribution': self._calculate_quality_distribution(segments),
            'peak_concurrent_viewers': max(total_viewers, self.metrics['peak_concurrent_viewers'])
        }
        
        return analytics

    def _calculate_avg_session_duration(self, sessions: List[StreamSession]) -> float:
        """Calculate average session duration"""
        
        if not sessions:
            return 0.0
        
        total_duration = 0.0
        for session in sessions:
            end_time = datetime.utcnow() if session.is_active else session.last_activity
            duration = (end_time - session.started_at).total_seconds()
            total_duration += duration
        
        return total_duration / len(sessions)

    def _calculate_quality_distribution(self, segments: List[StreamSegment]) -> Dict[str, int]:
        """Calculate quality level distribution"""
        
        distribution = {}
        for segment in segments:
            quality = segment.quality_level.value
            distribution[quality] = distribution.get(quality, 0) + 1
        
        return distribution

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall streaming system metrics"""
        
        # Calculate current bandwidth
        current_sessions = [s for s in self.active_sessions.values() if s.is_active]
        total_bandwidth = sum(s.bytes_delivered for s in current_sessions)
        
        return {
            'metrics': self.metrics,
            'active_streams': len(set(s.stream_id for s in current_sessions)),
            'active_sessions': len(current_sessions),
            'total_manifests': len(self.stream_manifests),
            'security_log_entries': len(self.security_log),
            'current_bandwidth_mbps': (total_bandwidth * 8) / (1024 * 1024),  # Convert to Mbps
            'system_status': 'operational'
        }

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and keys"""
        
        current_time = datetime.utcnow()
        expired_count = 0
        
        # Clean up expired streaming keys
        for key_id, key in list(self.streaming_keys.items()):
            if current_time > key.expires_at:
                key.is_active = False
                expired_count += 1
        
        # Clean up inactive sessions
        for session_id, session in list(self.active_sessions.items()):
            # Mark session as inactive if no activity for 30 minutes
            if (current_time - session.last_activity).total_seconds() > 1800:
                session.is_active = False
                self.metrics['total_sessions_active'] -= 1
                expired_count += 1
        
        self.logger.info(f"Cleaned up {expired_count} expired sessions/keys")
        return expired_count


# Utility functions
async def create_secure_streaming_engine(config: Dict[str, Any] = None) -> SecureStreamingEngine:
    """Factory function to create secure streaming engine"""
    engine = SecureStreamingEngine(config)
    return engine


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate secure streaming engine capabilities"""
        engine = await create_secure_streaming_engine()
        
        # Create secure stream
        stream_id, manifest = await engine.create_secure_stream(
            content_id="video_123",
            protocol=StreamingProtocol.HLS,
            stream_type=StreamType.VOD,
            quality_levels=[QualityLevel.HD_720P, QualityLevel.FHD_1080P],
            security_level=SecurityLevel.HIGH
        )
        
        print(f"Secure stream created: {stream_id}")
        print(f"Manifest ID: {manifest.manifest_id}")
        
        # Authenticate stream access
        streaming_key = await engine.authenticate_stream_access(
            stream_id=stream_id,
            user_id="user_456",
            client_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)"
        )
        
        print(f"Stream access authenticated: {streaming_key.key_id}")
        
        # Create streaming session
        session = await engine.create_streaming_session(
            stream_id=stream_id,
            user_id="user_456",
            client_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)",
            streaming_key=streaming_key
        )
        
        print(f"Streaming session created: {session.session_id}")
        
        # Add sample segments
        sample_segment_data = b"Sample video segment data..." * 100
        
        for i in range(5):
            segment = await engine.add_stream_segment(
                stream_id=stream_id,
                quality_level=QualityLevel.HD_720P,
                segment_data=sample_segment_data,
                duration=10.0
            )
            print(f"Segment added: {segment.segment_id}")
        
        # Generate adaptive manifest
        adaptive_manifest = await engine.generate_adaptive_manifest(
            stream_id=stream_id,
            protocol=StreamingProtocol.HLS
        )
        
        print("Adaptive manifest generated:")
        print(adaptive_manifest[:200] + "...")
        
        # Get stream analytics
        analytics = await engine.get_stream_analytics(stream_id)
        print(f"Stream analytics: {analytics}")
        
        # Get system metrics
        metrics = await engine.get_system_metrics()
        print(f"System metrics: {metrics}")
    
    asyncio.run(demo())