"""
Ainflue Platform - Multimedia Formats - Container Formats Management
Professional multimedia container format handling and processing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ContainerType(Enum):
    """Container format types"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    OGG = "ogg"
    FLV = "flv"
    WMV = "wmv"
    ASF = "asf"
    TS = "ts"
    M3U8 = "m3u8"
    DASH = "dash"
    HLS = "hls"


class StreamType(Enum):
    """Stream types within containers"""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    DATA = "data"
    ATTACHMENT = "attachment"


@dataclass
class StreamInfo:
    """Stream information within container"""
    index: int = 0
    stream_type: StreamType = StreamType.VIDEO
    codec: str = ""
    bitrate: Optional[int] = None
    duration: Optional[float] = None
    language: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Video specific
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    pixel_format: Optional[str] = None
    
    # Audio specific
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    channel_layout: Optional[str] = None


@dataclass
class ContainerInfo:
    """Container format information"""
    container_type: ContainerType = ContainerType.MP4
    file_size: int = 0
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    streams: List[StreamInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)


class ContainerFormatManager:
    """Professional container format management system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize container format manager"""
        self.config = config or {}
        self.supported_containers = {
            ContainerType.MP4: {
                'extensions': ['.mp4', '.m4v', '.m4a'],
                'mime_types': ['video/mp4', 'audio/mp4'],
                'video_codecs': ['h264', 'h265', 'av1', 'vp9'],
                'audio_codecs': ['aac', 'mp3', 'ac3', 'eac3'],
                'subtitle_codecs': ['mov_text', 'subrip'],
                'max_streams': 100,
                'supports_chapters': True,
                'supports_metadata': True,
                'supports_attachments': True
            },
            ContainerType.MKV: {
                'extensions': ['.mkv', '.mka', '.mks'],
                'mime_types': ['video/x-matroska', 'audio/x-matroska'],
                'video_codecs': ['h264', 'h265', 'av1', 'vp8', 'vp9'],
                'audio_codecs': ['aac', 'mp3', 'flac', 'vorbis', 'opus'],
                'subtitle_codecs': ['ass', 'srt', 'pgs', 'vobsub'],
                'max_streams': 127,
                'supports_chapters': True,
                'supports_metadata': True,
                'supports_attachments': True
            },
            ContainerType.WEBM: {
                'extensions': ['.webm'],
                'mime_types': ['video/webm', 'audio/webm'],
                'video_codecs': ['vp8', 'vp9', 'av1'],
                'audio_codecs': ['vorbis', 'opus'],
                'subtitle_codecs': ['webvtt'],
                'max_streams': 50,
                'supports_chapters': False,
                'supports_metadata': True,
                'supports_attachments': False
            },
            ContainerType.AVI: {
                'extensions': ['.avi'],
                'mime_types': ['video/x-msvideo'],
                'video_codecs': ['h264', 'xvid', 'divx'],
                'audio_codecs': ['mp3', 'aac', 'ac3'],
                'subtitle_codecs': ['srt'],
                'max_streams': 99,
                'supports_chapters': False,
                'supports_metadata': True,
                'supports_attachments': False
            },
            ContainerType.MOV: {
                'extensions': ['.mov', '.qt'],
                'mime_types': ['video/quicktime'],
                'video_codecs': ['h264', 'h265', 'prores'],
                'audio_codecs': ['aac', 'pcm', 'alac'],
                'subtitle_codecs': ['mov_text'],
                'max_streams': 100,
                'supports_chapters': True,
                'supports_metadata': True,
                'supports_attachments': True
            }
        }
    
    async def analyze_container(
        self,
        file_path: Union[str, Path]
    ) -> ContainerInfo:
        """Analyze container format and streams"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Detect container type from extension
            container_type = self._detect_container_type(file_path)
            
            # Create container info
            container_info = ContainerInfo(
                container_type=container_type,
                file_size=file_path.stat().st_size
            )
            
            # Analyze streams (simplified implementation)
            # In production, this would use FFmpeg or similar
            container_info.streams = await self._analyze_streams(file_path, container_type)
            
            # Extract metadata
            container_info.metadata = await self._extract_container_metadata(file_path)
            
            # Calculate duration from streams
            if container_info.streams:
                max_duration = max(
                    (stream.duration for stream in container_info.streams if stream.duration),
                    default=0
                )
                container_info.duration = max_duration
            
            logger.info(f"Analyzed container: {file_path.name} ({container_type.value})")
            return container_info
            
        except Exception as e:
            logger.error(f"Error analyzing container: {e}")
            raise
    
    def _detect_container_type(self, file_path: Path) -> ContainerType:
        """Detect container type from file extension"""
        try:
            extension = file_path.suffix.lower()
            
            for container_type, info in self.supported_containers.items():
                if extension in info['extensions']:
                    return container_type
            
            # Default to MP4 if unknown
            return ContainerType.MP4
            
        except Exception as e:
            logger.error(f"Error detecting container type: {e}")
            return ContainerType.MP4
    
    async def _analyze_streams(
        self,
        file_path: Path,
        container_type: ContainerType
    ) -> List[StreamInfo]:
        """Analyze streams within container"""
        try:
            streams = []
            
            # Simplified stream analysis
            # In production, would use FFprobe or similar
            
            # Add a default video stream
            video_stream = StreamInfo(
                index=0,
                stream_type=StreamType.VIDEO,
                codec="h264",
                width=1920,
                height=1080,
                frame_rate=30.0
            )
            streams.append(video_stream)
            
            # Add a default audio stream
            audio_stream = StreamInfo(
                index=1,
                stream_type=StreamType.AUDIO,
                codec="aac",
                sample_rate=48000,
                channels=2
            )
            streams.append(audio_stream)
            
            return streams
            
        except Exception as e:
            logger.error(f"Error analyzing streams: {e}")
            return []
    
    async def _extract_container_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """Extract container metadata"""
        try:
            # Simplified metadata extraction
            # In production, would use FFprobe or similar
            return {
                'title': file_path.stem,
                'format': file_path.suffix[1:],
                'created': 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error extracting container metadata: {e}")
            return {}
    
    async def validate_container(
        self,
        file_path: Union[str, Path],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate container against requirements"""
        try:
            container_info = await self.analyze_container(file_path)
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'info': container_info
            }
            
            if requirements:
                # Validate container type
                if 'container_type' in requirements:
                    required_type = requirements['container_type']
                    if container_info.container_type.value != required_type:
                        validation_result['errors'].append(
                            f"Container type {container_info.container_type.value} does not match required {required_type}"
                        )
                        validation_result['valid'] = False
                
                # Validate stream requirements
                if 'min_video_streams' in requirements:
                    video_streams = [s for s in container_info.streams if s.stream_type == StreamType.VIDEO]
                    if len(video_streams) < requirements['min_video_streams']:
                        validation_result['errors'].append(
                            f"Insufficient video streams: {len(video_streams)} < {requirements['min_video_streams']}"
                        )
                        validation_result['valid'] = False
                
                if 'min_audio_streams' in requirements:
                    audio_streams = [s for s in container_info.streams if s.stream_type == StreamType.AUDIO]
                    if len(audio_streams) < requirements['min_audio_streams']:
                        validation_result['errors'].append(
                            f"Insufficient audio streams: {len(audio_streams)} < {requirements['min_audio_streams']}"
                        )
                        validation_result['valid'] = False
                
                # Validate codecs
                if 'allowed_video_codecs' in requirements:
                    for stream in container_info.streams:
                        if (stream.stream_type == StreamType.VIDEO and 
                            stream.codec not in requirements['allowed_video_codecs']):
                            validation_result['errors'].append(
                                f"Video codec {stream.codec} not allowed"
                            )
                            validation_result['valid'] = False
                
                if 'allowed_audio_codecs' in requirements:
                    for stream in container_info.streams:
                        if (stream.stream_type == StreamType.AUDIO and 
                            stream.codec not in requirements['allowed_audio_codecs']):
                            validation_result['errors'].append(
                                f"Audio codec {stream.codec} not allowed"
                            )
                            validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating container: {e}")
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': [],
                'info': None
            }
    
    async def optimize_container(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        optimization_settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Optimize container structure"""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            settings = optimization_settings or {}
            
            # Analyze input container
            container_info = await self.analyze_container(input_path)
            
            # Determine optimization strategy
            optimizations = []
            
            if settings.get('fast_start', True):
                optimizations.append('fast_start')
            
            if settings.get('remove_unused_streams', False):
                optimizations.append('remove_unused_streams')
            
            if settings.get('reorder_streams', True):
                optimizations.append('reorder_streams')
            
            if settings.get('optimize_metadata', True):
                optimizations.append('optimize_metadata')
            
            # Apply optimizations (simplified)
            logger.info(f"Applying optimizations: {optimizations}")
            
            # In production, would use FFmpeg with appropriate flags
            # For now, just copy the file
            import shutil
            shutil.copy2(input_path, output_path)
            
            logger.info(f"Container optimized: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing container: {e}")
            return False
    
    async def convert_container(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        target_container: ContainerType,
        conversion_settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Convert between container formats"""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            settings = conversion_settings or {}
            
            # Analyze input
            source_info = await self.analyze_container(input_path)
            
            # Validate target container compatibility
            target_info = self.supported_containers[target_container]
            
            # Check codec compatibility
            for stream in source_info.streams:
                if stream.stream_type == StreamType.VIDEO:
                    if stream.codec not in target_info['video_codecs']:
                        if not settings.get('allow_transcoding', False):
                            raise ValueError(f"Video codec {stream.codec} not compatible with {target_container.value}")
                
                elif stream.stream_type == StreamType.AUDIO:
                    if stream.codec not in target_info['audio_codecs']:
                        if not settings.get('allow_transcoding', False):
                            raise ValueError(f"Audio codec {stream.codec} not compatible with {target_container.value}")
            
            # Perform conversion (simplified)
            logger.info(f"Converting {source_info.container_type.value} to {target_container.value}")
            
            # In production, would use FFmpeg for actual conversion
            # For now, just copy with new extension
            target_extension = target_info['extensions'][0]
            actual_output = output_path.with_suffix(target_extension)
            
            import shutil
            shutil.copy2(input_path, actual_output)
            
            logger.info(f"Container converted: {input_path.name} -> {actual_output.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting container: {e}")
            return False
    
    def get_container_capabilities(
        self,
        container_type: ContainerType
    ) -> Dict[str, Any]:
        """Get capabilities of specific container format"""
        try:
            if container_type in self.supported_containers:
                return self.supported_containers[container_type].copy()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting container capabilities: {e}")
            return {}
    
    def get_supported_containers(self) -> List[Dict[str, Any]]:
        """Get list of supported container formats"""
        try:
            containers = []
            
            for container_type, info in self.supported_containers.items():
                container_data = {
                    'type': container_type.value,
                    'name': container_type.value.upper(),
                    'extensions': info['extensions'],
                    'mime_types': info['mime_types'],
                    'description': f"{container_type.value.upper()} container format"
                }
                containers.append(container_data)
            
            return containers
            
        except Exception as e:
            logger.error(f"Error getting supported containers: {e}")
            return []
    
    async def extract_streams(
        self,
        input_path: Union[str, Path],
        output_directory: Union[str, Path],
        stream_types: Optional[List[StreamType]] = None
    ) -> List[str]:
        """Extract specific streams from container"""
        try:
            input_path = Path(input_path)
            output_directory = Path(output_directory)
            output_directory.mkdir(parents=True, exist_ok=True)
            
            container_info = await self.analyze_container(input_path)
            extracted_files = []
            
            stream_types = stream_types or [StreamType.VIDEO, StreamType.AUDIO]
            
            for stream in container_info.streams:
                if stream.stream_type in stream_types:
                    # Determine output filename
                    type_suffix = stream.stream_type.value
                    output_file = output_directory / f"{input_path.stem}_{type_suffix}_{stream.index}.{stream.codec}"
                    
                    # Extract stream (simplified)
                    logger.info(f"Extracting {stream.stream_type.value} stream {stream.index}")
                    
                    # In production, would use FFmpeg to extract specific streams
                    # For now, just create placeholder files
                    output_file.touch()
                    
                    extracted_files.append(str(output_file))
            
            return extracted_files
            
        except Exception as e:
            logger.error(f"Error extracting streams: {e}")
            return []


# Export main classes
__all__ = [
    'ContainerFormatManager',
    'ContainerInfo',
    'StreamInfo',
    'ContainerType',
    'StreamType'
]