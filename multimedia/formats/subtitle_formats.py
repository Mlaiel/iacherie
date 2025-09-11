"""
Subtitle Formats Management System
Comprehensive subtitle format support and conversion for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)


class SubtitleFormat(Enum):
    """Supported subtitle formats"""
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    SUB = "sub"
    SBV = "sbv"
    TTML = "ttml"
    DFXP = "dfxp"
    SCC = "scc"
    STL = "stl"
    SMI = "smi"
    LRC = "lrc"


class TimingFormat(Enum):
    """Timing format types"""
    TIMESTAMP = "timestamp"
    FRAME_NUMBER = "frame_number"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"


@dataclass
class SubtitleEntry:
    """Individual subtitle entry"""
    start_time: float  # seconds
    end_time: float  # seconds
    text: str
    style: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleTrack:
    """Complete subtitle track"""
    entries: List[SubtitleEntry]
    language: str = "und"  # undefined
    title: str = ""
    format_type: SubtitleFormat = SubtitleFormat.SRT
    encoding: str = "utf-8"
    framerate: float = 25.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleFormatSpec:
    """Subtitle format specification"""
    name: str
    format_type: SubtitleFormat
    file_extension: str
    mime_type: str
    supports_styling: bool
    supports_positioning: bool
    supports_metadata: bool
    supports_chapters: bool
    timing_format: TimingFormat
    text_encoding: str
    max_line_length: int
    max_lines_per_entry: int
    web_compatible: bool
    streaming_optimized: bool
    description: str


class SubtitleFormatRegistry:
    """Registry for subtitle formats and conversion capabilities"""
    
    def __init__(self):
        self.formats: Dict[SubtitleFormat, SubtitleFormatSpec] = {}
        self.converters: Dict[Tuple[SubtitleFormat, SubtitleFormat], callable] = {}
        self._initialize_formats()
        self._initialize_converters()
    
    def _initialize_formats(self):
        """Initialize subtitle format specifications"""
        
        # SRT (SubRip Text)
        self.formats[SubtitleFormat.SRT] = SubtitleFormatSpec(
            name="SubRip Text",
            format_type=SubtitleFormat.SRT,
            file_extension="srt",
            mime_type="text/srt",
            supports_styling=False,
            supports_positioning=False,
            supports_metadata=False,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=42,
            max_lines_per_entry=2,
            web_compatible=True,
            streaming_optimized=True,
            description="Simple, widely-supported subtitle format"
        )
        
        # WebVTT (Web Video Text Tracks)
        self.formats[SubtitleFormat.VTT] = SubtitleFormatSpec(
            name="Web Video Text Tracks",
            format_type=SubtitleFormat.VTT,
            file_extension="vtt",
            mime_type="text/vtt",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=True,
            supports_chapters=True,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,  # No limit
            max_lines_per_entry=0,  # No limit
            web_compatible=True,
            streaming_optimized=True,
            description="HTML5 standard subtitle format with advanced features"
        )
        
        # ASS (Advanced SubStation Alpha)
        self.formats[SubtitleFormat.ASS] = SubtitleFormatSpec(
            name="Advanced SubStation Alpha",
            format_type=SubtitleFormat.ASS,
            file_extension="ass",
            mime_type="text/ass",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=True,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=0,
            web_compatible=False,
            streaming_optimized=False,
            description="Advanced subtitle format with extensive styling"
        )
        
        # SSA (SubStation Alpha)
        self.formats[SubtitleFormat.SSA] = SubtitleFormatSpec(
            name="SubStation Alpha",
            format_type=SubtitleFormat.SSA,
            file_extension="ssa",
            mime_type="text/ssa",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=True,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=0,
            web_compatible=False,
            streaming_optimized=False,
            description="Predecessor to ASS with styling capabilities"
        )
        
        # SUB (MicroDVD)
        self.formats[SubtitleFormat.SUB] = SubtitleFormatSpec(
            name="MicroDVD SUB",
            format_type=SubtitleFormat.SUB,
            file_extension="sub",
            mime_type="text/sub",
            supports_styling=True,
            supports_positioning=False,
            supports_metadata=False,
            supports_chapters=False,
            timing_format=TimingFormat.FRAME_NUMBER,
            text_encoding="utf-8",
            max_line_length=60,
            max_lines_per_entry=2,
            web_compatible=False,
            streaming_optimized=False,
            description="Frame-based subtitle format with basic styling"
        )
        
        # SBV (YouTube SubViewer)
        self.formats[SubtitleFormat.SBV] = SubtitleFormatSpec(
            name="YouTube SubViewer",
            format_type=SubtitleFormat.SBV,
            file_extension="sbv",
            mime_type="text/sbv",
            supports_styling=False,
            supports_positioning=False,
            supports_metadata=False,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=0,
            web_compatible=True,
            streaming_optimized=True,
            description="YouTube's simple subtitle format"
        )
        
        # TTML (Timed Text Markup Language)
        self.formats[SubtitleFormat.TTML] = SubtitleFormatSpec(
            name="Timed Text Markup Language",
            format_type=SubtitleFormat.TTML,
            file_extension="ttml",
            mime_type="application/ttml+xml",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=True,
            supports_chapters=True,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=0,
            web_compatible=True,
            streaming_optimized=True,
            description="W3C standard XML-based subtitle format"
        )
        
        # SCC (Scenarist Closed Captions)
        self.formats[SubtitleFormat.SCC] = SubtitleFormatSpec(
            name="Scenarist Closed Captions",
            format_type=SubtitleFormat.SCC,
            file_extension="scc",
            mime_type="text/scc",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=False,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="ascii",
            max_line_length=32,
            max_lines_per_entry=4,
            web_compatible=False,
            streaming_optimized=False,
            description="Professional closed captioning format for broadcast"
        )
        
        # STL (Spruce Subtitle File)
        self.formats[SubtitleFormat.STL] = SubtitleFormatSpec(
            name="Spruce Subtitle File",
            format_type=SubtitleFormat.STL,
            file_extension="stl",
            mime_type="text/stl",
            supports_styling=False,
            supports_positioning=False,
            supports_metadata=False,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=40,
            max_lines_per_entry=2,
            web_compatible=False,
            streaming_optimized=False,
            description="DVD authoring subtitle format"
        )
        
        # SMI (SAMI)
        self.formats[SubtitleFormat.SMI] = SubtitleFormatSpec(
            name="Synchronized Accessible Media Interchange",
            format_type=SubtitleFormat.SMI,
            file_extension="smi",
            mime_type="application/smil",
            supports_styling=True,
            supports_positioning=True,
            supports_metadata=True,
            supports_chapters=False,
            timing_format=TimingFormat.MILLISECONDS,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=0,
            web_compatible=True,
            streaming_optimized=False,
            description="Microsoft's HTML-like subtitle format"
        )
        
        # LRC (Lyrics)
        self.formats[SubtitleFormat.LRC] = SubtitleFormatSpec(
            name="LRC Lyrics Format",
            format_type=SubtitleFormat.LRC,
            file_extension="lrc",
            mime_type="text/lrc",
            supports_styling=False,
            supports_positioning=False,
            supports_metadata=True,
            supports_chapters=False,
            timing_format=TimingFormat.TIMESTAMP,
            text_encoding="utf-8",
            max_line_length=0,
            max_lines_per_entry=1,
            web_compatible=False,
            streaming_optimized=False,
            description="Synchronized lyrics format for music"
        )
    
    def _initialize_converters(self):
        """Initialize format conversion functions"""
        # Register conversion functions
        self.converters[(SubtitleFormat.SRT, SubtitleFormat.VTT)] = self._convert_srt_to_vtt
        self.converters[(SubtitleFormat.VTT, SubtitleFormat.SRT)] = self._convert_vtt_to_srt
        self.converters[(SubtitleFormat.ASS, SubtitleFormat.SRT)] = self._convert_ass_to_srt
        self.converters[(SubtitleFormat.SRT, SubtitleFormat.SBV)] = self._convert_srt_to_sbv
        self.converters[(SubtitleFormat.VTT, SubtitleFormat.TTML)] = self._convert_vtt_to_ttml
    
    def get_format(self, format_type: SubtitleFormat) -> Optional[SubtitleFormatSpec]:
        """Get format specification"""
        return self.formats.get(format_type)
    
    def get_web_compatible_formats(self) -> List[SubtitleFormatSpec]:
        """Get web-compatible subtitle formats"""
        return [fmt for fmt in self.formats.values() if fmt.web_compatible]
    
    def get_streaming_optimized_formats(self) -> List[SubtitleFormatSpec]:
        """Get streaming-optimized formats"""
        return [fmt for fmt in self.formats.values() if fmt.streaming_optimized]
    
    def can_convert(self, source: SubtitleFormat, target: SubtitleFormat) -> bool:
        """Check if conversion is supported"""
        return (source, target) in self.converters
    
    def convert_format(self, 
                      track: SubtitleTrack, 
                      target_format: SubtitleFormat,
                      options: Dict[str, Any] = None) -> SubtitleTrack:
        """Convert subtitle track to target format"""
        if track.format_type == target_format:
            return track
        
        converter = self.converters.get((track.format_type, target_format))
        if not converter:
            # Try indirect conversion through SRT
            if track.format_type != SubtitleFormat.SRT:
                intermediate = self.convert_format(track, SubtitleFormat.SRT, options)
                return self.convert_format(intermediate, target_format, options)
            else:
                raise ValueError(f"No converter available from {track.format_type} to {target_format}")
        
        return converter(track, options or {})
    
    def _convert_srt_to_vtt(self, track: SubtitleTrack, options: Dict[str, Any]) -> SubtitleTrack:
        """Convert SRT to WebVTT"""
        converted_entries = []
        
        for entry in track.entries:
            converted_entry = SubtitleEntry(
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=entry.text,
                style=entry.style.copy(),
                position=entry.position.copy(),
                metadata=entry.metadata.copy()
            )
            converted_entries.append(converted_entry)
        
        return SubtitleTrack(
            entries=converted_entries,
            language=track.language,
            title=track.title,
            format_type=SubtitleFormat.VTT,
            encoding=track.encoding,
            framerate=track.framerate,
            metadata=track.metadata.copy()
        )
    
    def _convert_vtt_to_srt(self, track: SubtitleTrack, options: Dict[str, Any]) -> SubtitleTrack:
        """Convert WebVTT to SRT"""
        converted_entries = []
        
        for entry in track.entries:
            # Strip VTT-specific styling and positioning
            text = self._strip_vtt_markup(entry.text)
            
            converted_entry = SubtitleEntry(
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=text,
                style={},  # SRT doesn't support styling
                position={},  # SRT doesn't support positioning
                metadata={}
            )
            converted_entries.append(converted_entry)
        
        return SubtitleTrack(
            entries=converted_entries,
            language=track.language,
            title=track.title,
            format_type=SubtitleFormat.SRT,
            encoding=track.encoding,
            framerate=track.framerate,
            metadata={}
        )
    
    def _convert_ass_to_srt(self, track: SubtitleTrack, options: Dict[str, Any]) -> SubtitleTrack:
        """Convert ASS to SRT"""
        converted_entries = []
        
        for entry in track.entries:
            # Strip ASS styling codes
            text = self._strip_ass_markup(entry.text)
            
            converted_entry = SubtitleEntry(
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=text,
                style={},
                position={},
                metadata={}
            )
            converted_entries.append(converted_entry)
        
        return SubtitleTrack(
            entries=converted_entries,
            language=track.language,
            title=track.title,
            format_type=SubtitleFormat.SRT,
            encoding=track.encoding,
            framerate=track.framerate,
            metadata={}
        )
    
    def _convert_srt_to_sbv(self, track: SubtitleTrack, options: Dict[str, Any]) -> SubtitleTrack:
        """Convert SRT to SBV (YouTube)"""
        converted_entries = []
        
        for entry in track.entries:
            converted_entry = SubtitleEntry(
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=entry.text,
                style={},
                position={},
                metadata={}
            )
            converted_entries.append(converted_entry)
        
        return SubtitleTrack(
            entries=converted_entries,
            language=track.language,
            title=track.title,
            format_type=SubtitleFormat.SBV,
            encoding=track.encoding,
            framerate=track.framerate,
            metadata={}
        )
    
    def _convert_vtt_to_ttml(self, track: SubtitleTrack, options: Dict[str, Any]) -> SubtitleTrack:
        """Convert WebVTT to TTML"""
        converted_entries = []
        
        for entry in track.entries:
            # Convert VTT styling to TTML
            ttml_text = self._convert_vtt_to_ttml_markup(entry.text)
            
            converted_entry = SubtitleEntry(
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=ttml_text,
                style=self._convert_vtt_style_to_ttml(entry.style),
                position=self._convert_vtt_position_to_ttml(entry.position),
                metadata=entry.metadata.copy()
            )
            converted_entries.append(converted_entry)
        
        return SubtitleTrack(
            entries=converted_entries,
            language=track.language,
            title=track.title,
            format_type=SubtitleFormat.TTML,
            encoding=track.encoding,
            framerate=track.framerate,
            metadata=track.metadata.copy()
        )
    
    def _strip_vtt_markup(self, text: str) -> str:
        """Strip WebVTT markup from text"""
        # Remove VTT tags like <c.classname>, <i>, <b>, etc.
        text = re.sub(r'<[^>]+>', '', text)
        # Remove voice tags like <v Speaker>
        text = re.sub(r'<v[^>]*>', '', text)
        return text.strip()
    
    def _strip_ass_markup(self, text: str) -> str:
        """Strip ASS styling codes from text"""
        # Remove ASS override tags like {\b1}, {\i1}, etc.
        text = re.sub(r'\{[^}]*\}', '', text)
        # Remove drawing commands
        text = re.sub(r'\{\\p[^}]*\}.*?\{\\p0\}', '', text)
        return text.strip()
    
    def _convert_vtt_to_ttml_markup(self, text: str) -> str:
        """Convert VTT markup to TTML markup"""
        # Convert basic tags
        conversions = {
            r'<i>': '<span tts:fontStyle="italic">',
            r'</i>': '</span>',
            r'<b>': '<span tts:fontWeight="bold">',
            r'</b>': '</span>',
            r'<u>': '<span tts:textDecoration="underline">',
            r'</u>': '</span>'
        }
        
        for vtt_tag, ttml_tag in conversions.items():
            text = re.sub(vtt_tag, ttml_tag, text, flags=re.IGNORECASE)
        
        return text
    
    def _convert_vtt_style_to_ttml(self, vtt_style: Dict[str, Any]) -> Dict[str, Any]:
        """Convert VTT style to TTML style"""
        ttml_style = {}
        
        style_mappings = {
            'color': 'tts:color',
            'background-color': 'tts:backgroundColor',
            'font-size': 'tts:fontSize',
            'font-family': 'tts:fontFamily',
            'font-weight': 'tts:fontWeight',
            'font-style': 'tts:fontStyle',
            'text-decoration': 'tts:textDecoration'
        }
        
        for vtt_prop, ttml_prop in style_mappings.items():
            if vtt_prop in vtt_style:
                ttml_style[ttml_prop] = vtt_style[vtt_prop]
        
        return ttml_style
    
    def _convert_vtt_position_to_ttml(self, vtt_position: Dict[str, Any]) -> Dict[str, Any]:
        """Convert VTT position to TTML position"""
        ttml_position = {}
        
        position_mappings = {
            'line': 'tts:origin',
            'position': 'tts:extent',
            'align': 'tts:textAlign'
        }
        
        for vtt_prop, ttml_prop in position_mappings.items():
            if vtt_prop in vtt_position:
                ttml_position[ttml_prop] = vtt_position[vtt_prop]
        
        return ttml_position
    
    def parse_subtitle_file(self, content: str, format_type: SubtitleFormat) -> SubtitleTrack:
        """Parse subtitle file content"""
        if format_type == SubtitleFormat.SRT:
            return self._parse_srt(content)
        elif format_type == SubtitleFormat.VTT:
            return self._parse_vtt(content)
        elif format_type == SubtitleFormat.ASS:
            return self._parse_ass(content)
        elif format_type == SubtitleFormat.SBV:
            return self._parse_sbv(content)
        else:
            raise ValueError(f"Parser not implemented for format: {format_type}")
    
    def _parse_srt(self, content: str) -> SubtitleTrack:
        """Parse SRT subtitle content"""
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # Parse timing line
                timing_line = lines[1]
                timing_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', timing_line)
                if not timing_match:
                    continue
                
                start_time = self._parse_srt_timestamp(timing_match.group(1))
                end_time = self._parse_srt_timestamp(timing_match.group(2))
                
                # Parse text
                text = '\n'.join(lines[2:])
                
                entry = SubtitleEntry(
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                )
                entries.append(entry)
                
            except (ValueError, IndexError):
                continue
        
        return SubtitleTrack(
            entries=entries,
            format_type=SubtitleFormat.SRT
        )
    
    def _parse_vtt(self, content: str) -> SubtitleTrack:
        """Parse WebVTT subtitle content"""
        lines = content.split('\n')
        entries = []
        
        # Skip header
        start_index = 0
        for i, line in enumerate(lines):
            if line.strip() == 'WEBVTT':
                start_index = i + 1
                break
        
        # Parse cues
        i = start_index
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and notes
            if not line or line.startswith('NOTE'):
                i += 1
                continue
            
            # Check for timing line
            timing_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
            if timing_match:
                start_time = self._parse_vtt_timestamp(timing_match.group(1))
                end_time = self._parse_vtt_timestamp(timing_match.group(2))
                
                # Parse cue text
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i])
                    i += 1
                
                text = '\n'.join(text_lines)
                
                entry = SubtitleEntry(
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                )
                entries.append(entry)
            
            i += 1
        
        return SubtitleTrack(
            entries=entries,
            format_type=SubtitleFormat.VTT
        )
    
    def _parse_ass(self, content: str) -> SubtitleTrack:
        """Parse ASS subtitle content"""
        entries = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    try:
                        start_time = self._parse_ass_timestamp(parts[1])
                        end_time = self._parse_ass_timestamp(parts[2])
                        text = parts[9]
                        
                        entry = SubtitleEntry(
                            start_time=start_time,
                            end_time=end_time,
                            text=text
                        )
                        entries.append(entry)
                    except (ValueError, IndexError):
                        continue
        
        return SubtitleTrack(
            entries=entries,
            format_type=SubtitleFormat.ASS
        )
    
    def _parse_sbv(self, content: str) -> SubtitleTrack:
        """Parse SBV subtitle content"""
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 2:
                continue
            
            try:
                # Parse timing line
                timing_line = lines[0]
                timing_match = re.match(r'(\d+:\d{2}:\d{2}\.\d{3}),(\d+:\d{2}:\d{2}\.\d{3})', timing_line)
                if not timing_match:
                    continue
                
                start_time = self._parse_sbv_timestamp(timing_match.group(1))
                end_time = self._parse_sbv_timestamp(timing_match.group(2))
                
                # Parse text
                text = '\n'.join(lines[1:])
                
                entry = SubtitleEntry(
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                )
                entries.append(entry)
                
            except (ValueError, IndexError):
                continue
        
        return SubtitleTrack(
            entries=entries,
            format_type=SubtitleFormat.SBV
        )
    
    def _parse_srt_timestamp(self, timestamp: str) -> float:
        """Parse SRT timestamp to seconds"""
        match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp)
        if not match:
            raise ValueError(f"Invalid SRT timestamp: {timestamp}")
        
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def _parse_vtt_timestamp(self, timestamp: str) -> float:
        """Parse WebVTT timestamp to seconds"""
        match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', timestamp)
        if not match:
            raise ValueError(f"Invalid VTT timestamp: {timestamp}")
        
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def _parse_ass_timestamp(self, timestamp: str) -> float:
        """Parse ASS timestamp to seconds"""
        match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', timestamp)
        if not match:
            raise ValueError(f"Invalid ASS timestamp: {timestamp}")
        
        hours, minutes, seconds, centiseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
    
    def _parse_sbv_timestamp(self, timestamp: str) -> float:
        """Parse SBV timestamp to seconds"""
        match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{3})', timestamp)
        if not match:
            raise ValueError(f"Invalid SBV timestamp: {timestamp}")
        
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    
    def export_format_capabilities(self) -> Dict[str, Any]:
        """Export format capabilities matrix"""
        capabilities = {}
        
        for format_type, spec in self.formats.items():
            capabilities[format_type.value] = {
                "name": spec.name,
                "file_extension": spec.file_extension,
                "mime_type": spec.mime_type,
                "features": {
                    "styling": spec.supports_styling,
                    "positioning": spec.supports_positioning,
                    "metadata": spec.supports_metadata,
                    "chapters": spec.supports_chapters
                },
                "compatibility": {
                    "web": spec.web_compatible,
                    "streaming": spec.streaming_optimized
                },
                "timing_format": spec.timing_format.value,
                "constraints": {
                    "max_line_length": spec.max_line_length,
                    "max_lines_per_entry": spec.max_lines_per_entry
                }
            }
        
        return capabilities


# Global registry instance
subtitle_formats = SubtitleFormatRegistry()


# Export main classes and functions
__all__ = [
    'SubtitleFormat',
    'TimingFormat',
    'SubtitleEntry',
    'SubtitleTrack',
    'SubtitleFormatSpec',
    'SubtitleFormatRegistry',
    'subtitle_formats'
]