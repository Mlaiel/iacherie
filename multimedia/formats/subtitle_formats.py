"""
Subtitle Formats Module for Ainflue Platform
Comprehensive subtitle format handling and conversion

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SubtitleType(Enum):
    """Subtitle type classifications"""
    TEXT = "text"
    BITMAP = "bitmap"
    STYLED = "styled"
    TIMED_TEXT = "timed_text"


class CueType(Enum):
    """Subtitle cue types"""
    CAPTION = "caption"
    SUBTITLE = "subtitle"
    DESCRIPTION = "description"
    CHAPTER = "chapter"
    METADATA = "metadata"


@dataclass
class TimingInfo:
    """Subtitle timing information"""
    start: timedelta
    end: timedelta
    duration: Optional[timedelta] = None
    
    def __post_init__(self):
        if self.duration is None:
            self.duration = self.end - self.start


@dataclass
class StyleInfo:
    """Subtitle styling information"""
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_weight: Optional[str] = None  # normal, bold
    font_style: Optional[str] = None   # normal, italic
    color: Optional[str] = None
    background_color: Optional[str] = None
    text_align: Optional[str] = None   # left, center, right
    vertical_align: Optional[str] = None  # top, middle, bottom
    position_x: Optional[float] = None  # percentage
    position_y: Optional[float] = None  # percentage
    outline_color: Optional[str] = None
    outline_width: Optional[int] = None
    shadow_color: Optional[str] = None
    shadow_offset: Optional[Tuple[int, int]] = None


@dataclass
class SubtitleCue:
    """Individual subtitle cue/entry"""
    id: Optional[str] = None
    timing: Optional[TimingInfo] = None
    text: str = ""
    cue_type: CueType = CueType.SUBTITLE
    style: Optional[StyleInfo] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[str] = None


@dataclass
class SubtitleTrack:
    """Complete subtitle track"""
    language: Optional[str] = None
    label: Optional[str] = None
    cues: List[SubtitleCue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    format_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleFormat:
    """Subtitle format specification"""
    format_id: str
    name: str
    description: str
    subtitle_type: SubtitleType
    file_extensions: List[str]
    mime_types: List[str]
    
    # Format capabilities
    supports_styling: bool = False
    supports_positioning: bool = False
    supports_multiple_tracks: bool = False
    supports_metadata: bool = False
    supports_chapters: bool = False
    supports_karaoke: bool = False
    
    # Technical specifications
    encoding: str = "utf-8"
    line_separator: str = "\n"
    time_format: str = "hh:mm:ss,fff"
    max_line_length: Optional[int] = None
    max_lines_per_cue: Optional[int] = None
    
    # Platform support
    web_support: bool = False
    broadcast_support: bool = False
    streaming_support: bool = False
    mobile_support: bool = False
    
    # Implementation details
    parser_complexity: str = "simple"  # simple, medium, complex
    specification_url: str = ""
    standard_organization: str = ""
    
    created_at: str = ""
    updated_at: str = ""


class SubtitleFormatsRegistry:
    """
    Registry for subtitle format specifications and handlers
    Manages subtitle parsing, conversion, and validation
    """
    
    def __init__(self):
        self.formats: Dict[str, SubtitleFormat] = {}
        self.extension_mappings: Dict[str, str] = {}
        self.mime_mappings: Dict[str, str] = {}
        self._initialize_subtitle_formats()
    
    def _initialize_subtitle_formats(self):
        """Initialize registry with standard subtitle formats"""
        
        # SRT (SubRip Text)
        srt_format = SubtitleFormat(
            format_id="srt",
            name="SubRip Text",
            description="Simple and widely supported subtitle format",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".srt"],
            mime_types=["text/srt", "application/x-subrip"],
            supports_styling=False,
            supports_positioning=False,
            supports_multiple_tracks=False,
            supports_metadata=False,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="utf-8",
            line_separator="\n",
            time_format="hh:mm:ss,fff",
            max_line_length=None,
            max_lines_per_cue=2,
            web_support=True,
            broadcast_support=True,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="simple",
            specification_url="https://en.wikipedia.org/wiki/SubRip",
            standard_organization="Community",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(srt_format)
        
        # VTT (WebVTT)
        vtt_format = SubtitleFormat(
            format_id="vtt",
            name="Web Video Text Tracks",
            description="Web standard for subtitle and caption delivery",
            subtitle_type=SubtitleType.STYLED,
            file_extensions=[".vtt"],
            mime_types=["text/vtt"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=False,
            supports_metadata=True,
            supports_chapters=True,
            supports_karaoke=True,
            encoding="utf-8",
            line_separator="\n",
            time_format="hh:mm:ss.fff",
            max_line_length=None,
            max_lines_per_cue=None,
            web_support=True,
            broadcast_support=False,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="medium",
            specification_url="https://www.w3.org/TR/webvtt1/",
            standard_organization="W3C",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(vtt_format)
        
        # ASS/SSA (Advanced SubStation Alpha)
        ass_format = SubtitleFormat(
            format_id="ass",
            name="Advanced SubStation Alpha",
            description="Advanced subtitle format with extensive styling capabilities",
            subtitle_type=SubtitleType.STYLED,
            file_extensions=[".ass", ".ssa"],
            mime_types=["text/ass", "text/ssa"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=True,
            supports_metadata=True,
            supports_chapters=False,
            supports_karaoke=True,
            encoding="utf-8",
            line_separator="\n",
            time_format="h:mm:ss.ff",
            max_line_length=None,
            max_lines_per_cue=None,
            web_support=False,
            broadcast_support=False,
            streaming_support=False,
            mobile_support=False,
            parser_complexity="complex",
            specification_url="http://www.tcax.org/docs/ass-specs.htm",
            standard_organization="Community",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(ass_format)
        
        # TTML (Timed Text Markup Language)
        ttml_format = SubtitleFormat(
            format_id="ttml",
            name="Timed Text Markup Language",
            description="XML-based timed text format for broadcast and streaming",
            subtitle_type=SubtitleType.STYLED,
            file_extensions=[".ttml", ".dfxp"],
            mime_types=["application/ttml+xml"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=True,
            supports_metadata=True,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="utf-8",
            line_separator="\n",
            time_format="hh:mm:ss.fff",
            max_line_length=None,
            max_lines_per_cue=None,
            web_support=True,
            broadcast_support=True,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="complex",
            specification_url="https://www.w3.org/TR/ttml2/",
            standard_organization="W3C",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(ttml_format)
        
        # SCC (Scenarist Closed Caption)
        scc_format = SubtitleFormat(
            format_id="scc",
            name="Scenarist Closed Caption",
            description="Professional broadcast caption format",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".scc"],
            mime_types=["text/scc"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=False,
            supports_metadata=False,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="ascii",
            line_separator="\n",
            time_format="hh:mm:ss:ff",
            max_line_length=32,
            max_lines_per_cue=4,
            web_support=False,
            broadcast_support=True,
            streaming_support=False,
            mobile_support=False,
            parser_complexity="complex",
            specification_url="https://www.loc.gov/standards/mets/profiles/00000041.xml",
            standard_organization="SMPTE",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(scc_format)
        
        # STL (Spruce Subtitle File)
        stl_format = SubtitleFormat(
            format_id="stl",
            name="Spruce Subtitle File",
            description="DVD authoring subtitle format",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".stl"],
            mime_types=["text/stl"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=False,
            supports_metadata=True,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="utf-8",
            line_separator="\n",
            time_format="hh:mm:ss:ff",
            max_line_length=None,
            max_lines_per_cue=None,
            web_support=False,
            broadcast_support=True,
            streaming_support=False,
            mobile_support=False,
            parser_complexity="medium",
            specification_url="https://tech.ebu.ch/docs/tech/tech3264.pdf",
            standard_organization="EBU",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(stl_format)
        
        # SUB (MicroDVD)
        sub_format = SubtitleFormat(
            format_id="sub",
            name="MicroDVD Subtitle",
            description="Frame-based subtitle format",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".sub"],
            mime_types=["text/sub"],
            supports_styling=True,
            supports_positioning=False,
            supports_multiple_tracks=False,
            supports_metadata=False,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="utf-8",
            line_separator="\n",
            time_format="frame",
            max_line_length=None,
            max_lines_per_cue=2,
            web_support=False,
            broadcast_support=False,
            streaming_support=False,
            mobile_support=False,
            parser_complexity="simple",
            specification_url="https://en.wikipedia.org/wiki/MicroDVD",
            standard_organization="Community",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(sub_format)
        
        # LRC (LyRiCs)
        lrc_format = SubtitleFormat(
            format_id="lrc",
            name="LyRiCs Format",
            description="Synchronized lyrics format for music",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".lrc"],
            mime_types=["text/lrc"],
            supports_styling=False,
            supports_positioning=False,
            supports_multiple_tracks=False,
            supports_metadata=True,
            supports_chapters=False,
            supports_karaoke=True,
            encoding="utf-8",
            line_separator="\n",
            time_format="mm:ss.ff",
            max_line_length=None,
            max_lines_per_cue=1,
            web_support=False,
            broadcast_support=False,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="simple",
            specification_url="https://en.wikipedia.org/wiki/LRC_(file_format)",
            standard_organization="Community",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(lrc_format)
        
        # CEA-608 (Line 21 Closed Captions)
        cea608_format = SubtitleFormat(
            format_id="cea608",
            name="CEA-608 Closed Captions",
            description="Standard for closed captioning in North America",
            subtitle_type=SubtitleType.TEXT,
            file_extensions=[".cap"],
            mime_types=["text/cea608"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=True,
            supports_metadata=False,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="ascii",
            line_separator="\n",
            time_format="hh:mm:ss:ff",
            max_line_length=32,
            max_lines_per_cue=4,
            web_support=False,
            broadcast_support=True,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="complex",
            specification_url="https://www.fcc.gov/media/captioning-and-video-description-implementation",
            standard_organization="FCC/ATSC",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(cea608_format)
        
        # CEA-708 (Digital Television Closed Captions)
        cea708_format = SubtitleFormat(
            format_id="cea708",
            name="CEA-708 Digital Captions",
            description="Advanced closed captioning for digital television",
            subtitle_type=SubtitleType.STYLED,
            file_extensions=[".708"],
            mime_types=["text/cea708"],
            supports_styling=True,
            supports_positioning=True,
            supports_multiple_tracks=True,
            supports_metadata=True,
            supports_chapters=False,
            supports_karaoke=False,
            encoding="unicode",
            line_separator="\n",
            time_format="hh:mm:ss:ff",
            max_line_length=None,
            max_lines_per_cue=None,
            web_support=False,
            broadcast_support=True,
            streaming_support=True,
            mobile_support=True,
            parser_complexity="complex",
            specification_url="https://www.atsc.org/atsc-documents/a653-digital-television-dtv-closed-captioning/",
            standard_organization="ATSC",
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_format(cea708_format)
    
    def register_format(self, subtitle_format: SubtitleFormat):
        """Register a subtitle format"""
        self.formats[subtitle_format.format_id] = subtitle_format
        
        # Update extension mappings
        for extension in subtitle_format.file_extensions:
            self.extension_mappings[extension.lower()] = subtitle_format.format_id
        
        # Update MIME type mappings
        for mime_type in subtitle_format.mime_types:
            self.mime_mappings[mime_type.lower()] = subtitle_format.format_id
        
        logger.info(f"Registered subtitle format: {subtitle_format.name} ({subtitle_format.format_id})")
    
    def get_format(self, format_id: str) -> Optional[SubtitleFormat]:
        """Get subtitle format by ID"""
        return self.formats.get(format_id)
    
    def get_format_by_extension(self, extension: str) -> Optional[SubtitleFormat]:
        """Get subtitle format by file extension"""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        format_id = self.extension_mappings.get(extension.lower())
        return self.formats.get(format_id) if format_id else None
    
    def get_format_by_mime_type(self, mime_type: str) -> Optional[SubtitleFormat]:
        """Get subtitle format by MIME type"""
        format_id = self.mime_mappings.get(mime_type.lower())
        return self.formats.get(format_id) if format_id else None
    
    def get_formats_by_type(self, subtitle_type: SubtitleType) -> List[SubtitleFormat]:
        """Get all formats of specific type"""
        return [
            fmt for fmt in self.formats.values()
            if fmt.subtitle_type == subtitle_type
        ]
    
    def get_web_compatible_formats(self) -> List[SubtitleFormat]:
        """Get formats compatible with web browsers"""
        return [fmt for fmt in self.formats.values() if fmt.web_support]
    
    def get_streaming_compatible_formats(self) -> List[SubtitleFormat]:
        """Get formats compatible with streaming services"""
        return [fmt for fmt in self.formats.values() if fmt.streaming_support]
    
    def get_broadcast_compatible_formats(self) -> List[SubtitleFormat]:
        """Get formats compatible with broadcast television"""
        return [fmt for fmt in self.formats.values() if fmt.broadcast_support]
    
    def find_best_format(
        self,
        requirements: Dict[str, Any]
    ) -> Optional[SubtitleFormat]:
        """Find best subtitle format for requirements"""
        candidates = list(self.formats.values())
        
        # Filter by platform requirements
        if requirements.get("web", False):
            candidates = [f for f in candidates if f.web_support]
        
        if requirements.get("broadcast", False):
            candidates = [f for f in candidates if f.broadcast_support]
        
        if requirements.get("streaming", False):
            candidates = [f for f in candidates if f.streaming_support]
        
        if requirements.get("mobile", False):
            candidates = [f for f in candidates if f.mobile_support]
        
        # Filter by feature requirements
        if requirements.get("styling", False):
            candidates = [f for f in candidates if f.supports_styling]
        
        if requirements.get("positioning", False):
            candidates = [f for f in candidates if f.supports_positioning]
        
        if requirements.get("multiple_tracks", False):
            candidates = [f for f in candidates if f.supports_multiple_tracks]
        
        if requirements.get("metadata", False):
            candidates = [f for f in candidates if f.supports_metadata]
        
        if not candidates:
            return None
        
        # Prefer simpler formats for better compatibility
        complexity_priority = {"simple": 3, "medium": 2, "complex": 1}
        
        return max(
            candidates,
            key=lambda f: complexity_priority.get(f.parser_complexity, 0)
        )
    
    def parse_timecode(self, timecode: str, time_format: str) -> Optional[timedelta]:
        """Parse timecode string to timedelta"""
        try:
            if time_format == "hh:mm:ss,fff":
                # SRT format: 00:01:23,456
                match = re.match(r'(\d+):(\d+):(\d+),(\d+)', timecode)
                if match:
                    h, m, s, ms = map(int, match.groups())
                    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
            
            elif time_format == "hh:mm:ss.fff":
                # VTT format: 00:01:23.456
                match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timecode)
                if match:
                    h, m, s, ms = map(int, match.groups())
                    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
            
            elif time_format == "h:mm:ss.ff":
                # ASS format: 0:01:23.45
                match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timecode)
                if match:
                    h, m, s, cs = map(int, match.groups())
                    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=cs*10)
            
            elif time_format == "hh:mm:ss:ff":
                # SMPTE format: 00:01:23:15 (assuming 30fps)
                match = re.match(r'(\d+):(\d+):(\d+):(\d+)', timecode)
                if match:
                    h, m, s, f = map(int, match.groups())
                    ms = int((f / 30.0) * 1000)  # Convert frames to milliseconds
                    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
            
            elif time_format == "mm:ss.ff":
                # LRC format: 01:23.45
                match = re.match(r'(\d+):(\d+)\.(\d+)', timecode)
                if match:
                    m, s, cs = map(int, match.groups())
                    return timedelta(minutes=m, seconds=s, milliseconds=cs*10)
            
            elif time_format == "frame":
                # Frame-based timing (MicroDVD)
                frame_number = int(timecode)
                # Assuming 25fps (PAL standard)
                ms = int((frame_number / 25.0) * 1000)
                return timedelta(milliseconds=ms)
        
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def format_timecode(self, time_delta: timedelta, time_format: str) -> str:
        """Format timedelta to timecode string"""
        total_seconds = int(time_delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = int(time_delta.microseconds / 1000)
        
        if time_format == "hh:mm:ss,fff":
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        
        elif time_format == "hh:mm:ss.fff":
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
        elif time_format == "h:mm:ss.ff":
            centiseconds = milliseconds // 10
            return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        
        elif time_format == "hh:mm:ss:ff":
            frames = int((milliseconds / 1000.0) * 30)  # Assuming 30fps
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
        
        elif time_format == "mm:ss.ff":
            total_minutes = total_seconds // 60
            seconds_in_minute = total_seconds % 60
            centiseconds = milliseconds // 10
            return f"{total_minutes:02d}:{seconds_in_minute:02d}.{centiseconds:02d}"
        
        elif time_format == "frame":
            # Assuming 25fps
            frame_number = int(time_delta.total_seconds() * 25)
            return str(frame_number)
        
        return str(time_delta)
    
    def parse_srt(self, content: str) -> SubtitleTrack:
        """Parse SRT subtitle content"""
        track = SubtitleTrack()
        track.format_info = {"format": "srt"}
        
        # Split into subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # Parse subtitle number
                subtitle_id = lines[0].strip()
                
                # Parse timing
                timing_line = lines[1].strip()
                timing_match = re.match(
                    r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)',
                    timing_line
                )
                
                if not timing_match:
                    continue
                
                start_time = self.parse_timecode(timing_match.group(1), "hh:mm:ss,fff")
                end_time = self.parse_timecode(timing_match.group(2), "hh:mm:ss,fff")
                
                if not start_time or not end_time:
                    continue
                
                # Parse text content
                text_lines = lines[2:]
                text = '\n'.join(text_lines)
                
                # Create subtitle cue
                cue = SubtitleCue(
                    id=subtitle_id,
                    timing=TimingInfo(start=start_time, end=end_time),
                    text=text,
                    cue_type=CueType.SUBTITLE
                )
                
                track.cues.append(cue)
            
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse SRT block: {e}")
                continue
        
        return track
    
    def parse_vtt(self, content: str) -> SubtitleTrack:
        """Parse WebVTT subtitle content"""
        track = SubtitleTrack()
        track.format_info = {"format": "vtt"}
        
        lines = content.strip().split('\n')
        
        # Check for WebVTT header
        if not lines[0].startswith('WEBVTT'):
            logger.warning("Invalid WebVTT file - missing header")
            return track
        
        # Parse metadata and settings
        i = 1
        while i < len(lines) and lines[i].strip() == '':
            i += 1
        
        # Parse cues
        while i < len(lines):
            if lines[i].strip() == '':
                i += 1
                continue
            
            # Check for cue identifier
            cue_id = None
            if not re.match(r'\d+:\d+:\d+\.\d+\s*-->', lines[i]):
                cue_id = lines[i].strip()
                i += 1
                if i >= len(lines):
                    break
            
            # Parse timing line
            timing_line = lines[i].strip()
            timing_match = re.match(
                r'(\d+:\d+:\d+\.\d+)\s*-->\s*(\d+:\d+:\d+\.\d+)(.*)$',
                timing_line
            )
            
            if not timing_match:
                i += 1
                continue
            
            start_time = self.parse_timecode(timing_match.group(1), "hh:mm:ss.fff")
            end_time = self.parse_timecode(timing_match.group(2), "hh:mm:ss.fff")
            settings_str = timing_match.group(3).strip()
            
            if not start_time or not end_time:
                i += 1
                continue
            
            i += 1
            
            # Parse cue text
            text_lines = []
            while i < len(lines) and lines[i].strip() != '':
                text_lines.append(lines[i])
                i += 1
            
            text = '\n'.join(text_lines)
            
            # Parse settings
            settings = {}
            if settings_str:
                for setting in settings_str.split():
                    if ':' in setting:
                        key, value = setting.split(':', 1)
                        settings[key] = value
            
            # Create subtitle cue
            cue = SubtitleCue(
                id=cue_id,
                timing=TimingInfo(start=start_time, end=end_time),
                text=text,
                cue_type=CueType.SUBTITLE,
                settings=settings
            )
            
            track.cues.append(cue)
        
        return track
    
    def convert_subtitle_format(
        self,
        source_track: SubtitleTrack,
        target_format: str,
        conversion_options: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """Convert subtitle track to different format"""
        target_fmt = self.get_format(target_format)
        if not target_fmt:
            return "", [f"Unknown target format: {target_format}"]
        
        warnings = []
        
        if target_format == "srt":
            return self._convert_to_srt(source_track, target_fmt, warnings)
        elif target_format == "vtt":
            return self._convert_to_vtt(source_track, target_fmt, warnings)
        else:
            return "", [f"Conversion to {target_format} not yet implemented"]
    
    def _convert_to_srt(
        self,
        track: SubtitleTrack,
        target_fmt: SubtitleFormat,
        warnings: List[str]
    ) -> str:
        """Convert subtitle track to SRT format"""
        output_lines = []
        
        for i, cue in enumerate(track.cues, 1):
            if not cue.timing:
                warnings.append(f"Skipping cue {i} - no timing information")
                continue
            
            # Subtitle number
            output_lines.append(str(i))
            
            # Timing line
            start_str = self.format_timecode(cue.timing.start, "hh:mm:ss,fff")
            end_str = self.format_timecode(cue.timing.end, "hh:mm:ss,fff")
            output_lines.append(f"{start_str} --> {end_str}")
            
            # Text content (remove WebVTT tags if present)
            text = re.sub(r'<[^>]+>', '', cue.text)  # Remove HTML tags
            text = re.sub(r'\{[^}]+\}', '', text)    # Remove WebVTT styling
            
            output_lines.append(text)
            output_lines.append('')  # Empty line between subtitles
        
        return '\n'.join(output_lines)
    
    def _convert_to_vtt(
        self,
        track: SubtitleTrack,
        target_fmt: SubtitleFormat,
        warnings: List[str]
    ) -> str:
        """Convert subtitle track to WebVTT format"""
        output_lines = ["WEBVTT", ""]
        
        for cue in track.cues:
            if not cue.timing:
                warnings.append(f"Skipping cue - no timing information")
                continue
            
            # Optional cue identifier
            if cue.id:
                output_lines.append(cue.id)
            
            # Timing line
            start_str = self.format_timecode(cue.timing.start, "hh:mm:ss.fff")
            end_str = self.format_timecode(cue.timing.end, "hh:mm:ss.fff")
            
            timing_line = f"{start_str} --> {end_str}"
            
            # Add settings if present
            if cue.settings:
                settings_str = ' '.join(f"{k}:{v}" for k, v in cue.settings.items())
                timing_line += f" {settings_str}"
            
            output_lines.append(timing_line)
            
            # Text content
            output_lines.append(cue.text)
            output_lines.append('')  # Empty line between cues
        
        return '\n'.join(output_lines)
    
    def validate_subtitle_track(
        self,
        track: SubtitleTrack,
        format_id: str
    ) -> Tuple[bool, List[str]]:
        """Validate subtitle track against format specifications"""
        fmt = self.get_format(format_id)
        if not fmt:
            return False, [f"Unknown format: {format_id}"]
        
        errors = []
        
        for i, cue in enumerate(track.cues):
            # Check timing
            if not cue.timing:
                errors.append(f"Cue {i+1}: Missing timing information")
                continue
            
            if cue.timing.start >= cue.timing.end:
                errors.append(f"Cue {i+1}: Invalid timing - start >= end")
            
            # Check text length limitations
            if fmt.max_line_length:
                lines = cue.text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if len(line) > fmt.max_line_length:
                        errors.append(
                            f"Cue {i+1}, line {line_num}: "
                            f"Line too long ({len(line)} > {fmt.max_line_length})"
                        )
            
            # Check number of lines per cue
            if fmt.max_lines_per_cue:
                line_count = len(cue.text.split('\n'))
                if line_count > fmt.max_lines_per_cue:
                    errors.append(
                        f"Cue {i+1}: Too many lines "
                        f"({line_count} > {fmt.max_lines_per_cue})"
                    )
            
            # Check styling support
            if not fmt.supports_styling and cue.style:
                errors.append(f"Cue {i+1}: Styling not supported in {format_id}")
        
        return len(errors) == 0, errors
    
    def get_format_comparison(self, format_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare subtitle formats"""
        comparison = {}
        
        for format_id in format_ids:
            fmt = self.get_format(format_id)
            if not fmt:
                continue
            
            comparison[format_id] = {
                "name": fmt.name,
                "type": fmt.subtitle_type.value,
                "extensions": fmt.file_extensions,
                "supports_styling": fmt.supports_styling,
                "supports_positioning": fmt.supports_positioning,
                "supports_multiple_tracks": fmt.supports_multiple_tracks,
                "supports_metadata": fmt.supports_metadata,
                "web_support": fmt.web_support,
                "streaming_support": fmt.streaming_support,
                "broadcast_support": fmt.broadcast_support,
                "mobile_support": fmt.mobile_support,
                "complexity": fmt.parser_complexity
            }
        
        return comparison
    
    def export_registry(self, file_path: Path) -> bool:
        """Export subtitle formats registry to JSON"""
        try:
            registry_data = {
                "formats": {},
                "extension_mappings": self.extension_mappings,
                "mime_mappings": self.mime_mappings,
                "export_timestamp": datetime.now().isoformat(),
                "total_formats": len(self.formats)
            }
            
            for format_id, fmt in self.formats.items():
                format_data = {
                    "format_id": fmt.format_id,
                    "name": fmt.name,
                    "description": fmt.description,
                    "subtitle_type": fmt.subtitle_type.value,
                    "file_extensions": fmt.file_extensions,
                    "mime_types": fmt.mime_types,
                    "supports_styling": fmt.supports_styling,
                    "supports_positioning": fmt.supports_positioning,
                    "supports_multiple_tracks": fmt.supports_multiple_tracks,
                    "supports_metadata": fmt.supports_metadata,
                    "supports_chapters": fmt.supports_chapters,
                    "supports_karaoke": fmt.supports_karaoke,
                    "encoding": fmt.encoding,
                    "line_separator": fmt.line_separator,
                    "time_format": fmt.time_format,
                    "max_line_length": fmt.max_line_length,
                    "max_lines_per_cue": fmt.max_lines_per_cue,
                    "web_support": fmt.web_support,
                    "broadcast_support": fmt.broadcast_support,
                    "streaming_support": fmt.streaming_support,
                    "mobile_support": fmt.mobile_support,
                    "parser_complexity": fmt.parser_complexity,
                    "specification_url": fmt.specification_url,
                    "standard_organization": fmt.standard_organization,
                    "created_at": fmt.created_at,
                    "updated_at": fmt.updated_at
                }
                
                registry_data["formats"][format_id] = format_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Subtitle formats registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export subtitle formats registry: {e}")
            return False


# Global subtitle formats registry instance
subtitle_formats_registry = SubtitleFormatsRegistry()


async def get_subtitle_formats_registry() -> SubtitleFormatsRegistry:
    """Get the global subtitle formats registry instance"""
    return subtitle_formats_registry


if __name__ == "__main__":
    # Test subtitle formats registry
    registry = SubtitleFormatsRegistry()
    
    print("Subtitle Formats Overview:")
    print(f"Total formats: {len(registry.formats)}")
    
    print("\nWeb-compatible formats:")
    web_formats = registry.get_web_compatible_formats()
    for fmt in web_formats:
        print(f"- {fmt.name}: {', '.join(fmt.file_extensions)}")
    
    print("\nStreaming-compatible formats:")
    streaming_formats = registry.get_streaming_compatible_formats()
    for fmt in streaming_formats:
        print(f"- {fmt.name}: {', '.join(fmt.file_extensions)}")
    
    # Test SRT parsing
    sample_srt = """1
00:00:01,000 --> 00:00:03,000
Hello, this is a test subtitle.

2
00:00:04,000 --> 00:00:06,000
This is the second subtitle line."""
    
    print("\nParsing sample SRT:")
    track = registry.parse_srt(sample_srt)
    print(f"Parsed {len(track.cues)} subtitle cues")
    
    if track.cues:
        first_cue = track.cues[0]
        print(f"First cue: '{first_cue.text}' ({first_cue.timing.start} - {first_cue.timing.end})")
    
    # Test format conversion
    print("\nConverting to WebVTT:")
    vtt_content, warnings = registry.convert_subtitle_format(track, "vtt")
    print(f"Converted content length: {len(vtt_content)} characters")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Test format finding
    print("\nFinding best format for web streaming with styling:")
    best_format = registry.find_best_format({
        "web": True,
        "streaming": True,
        "styling": True
    })
    if best_format:
        print(f"Best format: {best_format.name} ({best_format.format_id})")