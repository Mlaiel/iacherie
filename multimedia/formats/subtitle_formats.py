"""
Ainflue Platform - Multimedia Formats - Subtitle Formats Management
Professional subtitle format handling and processing for multimedia content

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SubtitleFormat(Enum):
    """Supported subtitle formats"""
    SRT = "srt"                # SubRip Text
    VTT = "vtt"                # WebVTT
    ASS = "ass"                # Advanced SubStation Alpha
    SSA = "ssa"                # SubStation Alpha
    TTML = "ttml"              # Timed Text Markup Language
    SCC = "scc"                # Scenarist Closed Caption
    DFXP = "dfxp"              # Distribution Format Exchange Profile
    STL = "stl"                # Spruce Subtitle Format
    SUB = "sub"                # MicroDVD subtitle format
    SMI = "smi"                # SAMI (Synchronized Accessible Media Interchange)
    LRC = "lrc"                # LRC (LyRiCs) format
    PGS = "pgs"                # Presentation Graphics Stream (Blu-ray)
    VOBSUB = "vobsub"          # VOBsub (DVD subtitles)


class SubtitleType(Enum):
    """Types of subtitle content"""
    DIALOGUE = "dialogue"      # Speech and dialogue
    CAPTION = "caption"        # Closed captions (includes sound effects)
    FORCED = "forced"          # Forced subtitles (foreign language only)
    COMMENTARY = "commentary"  # Director/actor commentary
    LYRICS = "lyrics"          # Song lyrics
    KARAOKE = "karaoke"        # Karaoke timing
    SIGN = "sign"              # Sign language interpretation
    DESCRIPTION = "description" # Audio description for visually impaired


@dataclass
class TimingInfo:
    """Subtitle timing information"""
    start_time: float = 0.0    # Start time in seconds
    end_time: float = 0.0      # End time in seconds
    duration: float = 0.0      # Duration in seconds
    
    def __post_init__(self) -> None:
        if self.duration == 0.0 and self.end_time > self.start_time:
            self.duration = self.end_time - self.start_time


@dataclass
class SubtitleStyle:
    """Subtitle styling information"""
    font_name: str = "Arial"
    font_size: int = 20
    font_color: str = "#FFFFFF"
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    alignment: str = "center"   # left, center, right
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    margin_left: int = 0
    margin_right: int = 0
    margin_vertical: int = 0
    outline_width: int = 0
    shadow_depth: int = 0
    opacity: float = 1.0


@dataclass
class SubtitleEntry:
    """Individual subtitle entry"""
    index: int = 0
    timing: TimingInfo = field(default_factory=TimingInfo)
    text: str = ""
    style: Optional[SubtitleStyle] = None
    speaker: Optional[str] = None
    language: Optional[str] = None
    subtitle_type: SubtitleType = SubtitleType.DIALOGUE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleTrack:
    """Complete subtitle track"""
    entries: List[SubtitleEntry] = field(default_factory=list)
    format: SubtitleFormat = SubtitleFormat.SRT
    language: str = "en"
    title: Optional[str] = None
    default_style: Optional[SubtitleStyle] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[float] = None
    modified_at: Optional[float] = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()
        if self.modified_at is None:
            self.modified_at = self.created_at


class SubtitleFormatsManager:
    """Professional subtitle formats management system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize subtitle formats manager"""
        self.config = config or {}
        self.format_parsers: Dict[SubtitleFormat, callable] = {}
        self.format_writers: Dict[SubtitleFormat, callable] = {}
        
        # Initialize format handlers
        self._initialize_format_handlers()
    
    def _initialize_format_handlers(self) -> None:
        """Initialize format-specific parsers and writers"""
        try:
            # Register parsers
            self.format_parsers[SubtitleFormat.SRT] = self._parse_srt
            self.format_parsers[SubtitleFormat.VTT] = self._parse_vtt
            self.format_parsers[SubtitleFormat.ASS] = self._parse_ass
            self.format_parsers[SubtitleFormat.SSA] = self._parse_ssa
            self.format_parsers[SubtitleFormat.TTML] = self._parse_ttml
            
            # Register writers
            self.format_writers[SubtitleFormat.SRT] = self._write_srt
            self.format_writers[SubtitleFormat.VTT] = self._write_vtt
            self.format_writers[SubtitleFormat.ASS] = self._write_ass
            self.format_writers[SubtitleFormat.SSA] = self._write_ssa
            self.format_writers[SubtitleFormat.TTML] = self._write_ttml
            
        except Exception as e:
            logger.error(f"Error initializing format handlers: {e}")
    
    def _detect_subtitle_format(self, file_path: Path) -> SubtitleFormat:
        """Auto-detect subtitle format from file extension and content"""
        try:
            extension = file_path.suffix.lower()
            
            format_mapping = {
                '.srt': SubtitleFormat.SRT,
                '.vtt': SubtitleFormat.VTT,
                '.webvtt': SubtitleFormat.VTT,
                '.ass': SubtitleFormat.ASS,
                '.ssa': SubtitleFormat.SSA,
                '.ttml': SubtitleFormat.TTML,
                '.xml': SubtitleFormat.TTML,
                '.scc': SubtitleFormat.SCC,
                '.dfxp': SubtitleFormat.DFXP,
                '.stl': SubtitleFormat.STL,
                '.sub': SubtitleFormat.SUB,
                '.smi': SubtitleFormat.SMI,
                '.lrc': SubtitleFormat.LRC
            }
            
            if extension in format_mapping:
                return format_mapping[extension]
            
            # Try to detect from content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 characters
                    
                    if 'WEBVTT' in content:
                        return SubtitleFormat.VTT
                    elif '[Script Info]' in content:
                        return SubtitleFormat.ASS if extension == '.ass' else SubtitleFormat.SSA
                    elif '<?xml' in content and 'ttml' in content.lower():
                        return SubtitleFormat.TTML
                    elif re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3}', content):
                        return SubtitleFormat.SRT
            except Exception:
                pass
            
            # Default fallback
            return SubtitleFormat.SRT
            
        except Exception as e:
            logger.error(f"Error detecting subtitle format: {e}")
            return SubtitleFormat.SRT
    
    async def parse_subtitle_file(
        self,
        file_path: Union[str, Path],
        subtitle_format: Optional[SubtitleFormat] = None,
        encoding: str = 'utf-8'
    ) -> SubtitleTrack:
        """Parse subtitle file into SubtitleTrack object"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Subtitle file not found: {file_path}")
            
            # Auto-detect format if not specified
            if subtitle_format is None:
                subtitle_format = self._detect_subtitle_format(file_path)
            
            # Read file content
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try different encodings
                for enc in ['utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=enc) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Unable to decode subtitle file with any encoding")
            
            # Parse using format-specific parser
            if subtitle_format in self.format_parsers:
                parser = self.format_parsers[subtitle_format]
                track = await parser(content, file_path)
                track.format = subtitle_format
                logger.info(f"Parsed {subtitle_format.value} subtitle file: {file_path.name}")
                return track
            else:
                raise ValueError(f"No parser available for format {subtitle_format.value}")
                
        except Exception as e:
            logger.error(f"Error parsing subtitle file: {e}")
            # Return empty track on error
            return SubtitleTrack(format=subtitle_format or SubtitleFormat.SRT)
    
    async def _parse_srt(self, content: str, file_path: Path) -> SubtitleTrack:
        """Parse SRT format subtitles"""
        try:
            track = SubtitleTrack()
            entries = []
            
            # Split into subtitle blocks
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for i, block in enumerate(blocks):
                if not block.strip():
                    continue
                
                lines = block.strip().split('\n')
                if len(lines) < 3:
                    continue
                
                try:
                    # Parse index
                    index = int(lines[0].strip())
                    
                    # Parse timing
                    timing_line = lines[1].strip()
                    timing_match = re.match(
                        r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})',
                        timing_line
                    )
                    
                    if not timing_match:
                        continue
                    
                    start_h, start_m, start_s, start_ms = map(int, timing_match.groups()[:4])
                    end_h, end_m, end_s, end_ms = map(int, timing_match.groups()[4:])
                    
                    start_time = start_h * 3600 + start_m * 60 + start_s + start_ms / 1000
                    end_time = end_h * 3600 + end_m * 60 + end_s + end_ms / 1000
                    
                    # Parse text (remaining lines)
                    text = '\n'.join(lines[2:])
                    
                    entry = SubtitleEntry(
                        index=index,
                        timing=TimingInfo(start_time=start_time, end_time=end_time),
                        text=text
                    )
                    
                    entries.append(entry)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping malformed SRT entry at block {i}: {e}")
                    continue
            
            track.entries = entries
            return track
            
        except Exception as e:
            logger.error(f"Error parsing SRT: {e}")
            return SubtitleTrack()
    
    async def _parse_vtt(self, content: str, file_path: Path) -> SubtitleTrack:
        """Parse WebVTT format subtitles"""
        try:
            track = SubtitleTrack()
            entries = []
            
            lines = content.split('\n')
            current_entry = None
            index = 0
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip WebVTT header and empty lines
                if line == 'WEBVTT' or line == '' or line.startswith('NOTE'):
                    i += 1
                    continue
                
                # Check if this is a timing line
                timing_match = re.match(
                    r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})',
                    line
                )
                
                if timing_match:
                    start_h, start_m, start_s, start_ms = map(int, timing_match.groups()[:4])
                    end_h, end_m, end_s, end_ms = map(int, timing_match.groups()[4:])
                    
                    start_time = start_h * 3600 + start_m * 60 + start_s + start_ms / 1000
                    end_time = end_h * 3600 + end_m * 60 + end_s + end_ms / 1000
                    
                    # Collect text lines until next entry or end
                    text_lines = []
                    i += 1
                    while i < len(lines) and lines[i].strip() != '':
                        text_lines.append(lines[i])
                        i += 1
                    
                    text = '\n'.join(text_lines).strip()
                    
                    if text:  # Only add if there's actual text
                        entry = SubtitleEntry(
                            index=index,
                            timing=TimingInfo(start_time=start_time, end_time=end_time),
                            text=text
                        )
                        entries.append(entry)
                        index += 1
                else:
                    i += 1
            
            track.entries = entries
            return track
            
        except Exception as e:
            logger.error(f"Error parsing VTT: {e}")
            return SubtitleTrack()
    
    async def _parse_ass(self, content: str, file_path: Path) -> SubtitleTrack:
        """Parse ASS/SSA format subtitles"""
        try:
            track = SubtitleTrack()
            entries = []
            
            lines = content.split('\n')
            in_events_section = False
            format_line = None
            index = 0
            
            for line in lines:
                line = line.strip()
                
                if line == '[Events]':
                    in_events_section = True
                    continue
                elif line.startswith('[') and line.endswith(']'):
                    in_events_section = False
                    continue
                
                if in_events_section:
                    if line.startswith('Format:'):
                        format_line = line[7:].strip()
                        continue
                    elif line.startswith('Dialogue:') and format_line:
                        try:
                            # Parse dialogue line
                            dialogue_data = line[9:].strip()
                            fields = dialogue_data.split(',', 9)  # Split into max 10 parts
                            
                            if len(fields) >= 10:
                                start_time_str = fields[1].strip()
                                end_time_str = fields[2].strip()
                                text = fields[9].strip()
                                
                                # Convert ASS time format (H:MM:SS.cc) to seconds
                                start_time = self._ass_time_to_seconds(start_time_str)
                                end_time = self._ass_time_to_seconds(end_time_str)
                                
                                # Remove ASS formatting tags (simplified)
                                clean_text = re.sub(r'\{[^}]*\}', '', text)
                                
                                entry = SubtitleEntry(
                                    index=index,
                                    timing=TimingInfo(start_time=start_time, end_time=end_time),
                                    text=clean_text
                                )
                                entries.append(entry)
                                index += 1
                                
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Skipping malformed ASS dialogue line: {e}")
                            continue
            
            track.entries = entries
            return track
            
        except Exception as e:
            logger.error(f"Error parsing ASS: {e}")
            return SubtitleTrack()
    
    def _ass_time_to_seconds(self, time_str: str) -> float:
        """Convert ASS time format to seconds"""
        try:
            # Format: H:MM:SS.cc (centiseconds)
            parts = time_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                sec_parts = parts[2].split('.')
                seconds = int(sec_parts[0])
                centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
                
                return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
            return 0.0
            
        except (ValueError, IndexError):
            return 0.0
    
    async def _parse_ssa(self, content: str, file_path: Path) -> SubtitleTrack:
        """Parse SSA format subtitles (similar to ASS)"""
        # SSA is very similar to ASS, so we can reuse the ASS parser
        return await self._parse_ass(content, file_path)
    
    async def _parse_ttml(self, content: str, file_path: Path) -> SubtitleTrack:
        """Parse TTML format subtitles"""
        try:
            track = SubtitleTrack()
            entries = []
            
            # Simplified TTML parsing (would use XML parser in production)
            # Extract <p> elements with timing attributes
            p_pattern = r'<p\s+[^>]*begin="([^"]*)"[^>]*end="([^"]*)"[^>]*>(.*?)</p>'
            matches = re.finditer(p_pattern, content, re.DOTALL)
            
            index = 0
            for match in matches:
                try:
                    begin_str, end_str, text_content = match.groups()
                    
                    # Parse TTML time format (simplified)
                    start_time = self._ttml_time_to_seconds(begin_str)
                    end_time = self._ttml_time_to_seconds(end_str)
                    
                    # Clean HTML tags from text
                    clean_text = re.sub(r'<[^>]+>', '', text_content).strip()
                    
                    if clean_text:
                        entry = SubtitleEntry(
                            index=index,
                            timing=TimingInfo(start_time=start_time, end_time=end_time),
                            text=clean_text
                        )
                        entries.append(entry)
                        index += 1
                        
                except Exception as e:
                    logger.warning(f"Skipping malformed TTML entry: {e}")
                    continue
            
            track.entries = entries
            return track
            
        except Exception as e:
            logger.error(f"Error parsing TTML: {e}")
            return SubtitleTrack()
    
    def _ttml_time_to_seconds(self, time_str: str) -> float:
        """Convert TTML time format to seconds"""
        try:
            # TTML supports various time formats
            if 's' in time_str:
                # Format: XXXs or XXX.XXXs
                return float(time_str.rstrip('s'))
            elif ':' in time_str:
                # Format: HH:MM:SS.mmm
                parts = time_str.split(':')
                if len(parts) == 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
            
            return 0.0
            
        except (ValueError, IndexError):
            return 0.0
    
    async def write_subtitle_file(
        self,
        track: SubtitleTrack,
        file_path: Union[str, Path],
        subtitle_format: Optional[SubtitleFormat] = None,
        encoding: str = 'utf-8'
    ) -> bool:
        """Write SubtitleTrack to file"""
        try:
            file_path = Path(file_path)
            
            # Use track format if not specified
            if subtitle_format is None:
                subtitle_format = track.format
            
            # Generate content using format-specific writer
            if subtitle_format in self.format_writers:
                writer = self.format_writers[subtitle_format]
                content = await writer(track)
                
                # Write to file
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
                
                logger.info(f"Written {subtitle_format.value} subtitle file: {file_path.name}")
                return True
            else:
                raise ValueError(f"No writer available for format {subtitle_format.value}")
                
        except Exception as e:
            logger.error(f"Error writing subtitle file: {e}")
            return False
    
    async def _write_srt(self, track: SubtitleTrack) -> str:
        """Write SRT format"""
        try:
            lines = []
            
            for entry in track.entries:
                # Format timing
                start_h = int(entry.timing.start_time // 3600)
                start_m = int((entry.timing.start_time % 3600) // 60)
                start_s = int(entry.timing.start_time % 60)
                start_ms = int((entry.timing.start_time % 1) * 1000)
                
                end_h = int(entry.timing.end_time // 3600)
                end_m = int((entry.timing.end_time % 3600) // 60)
                end_s = int(entry.timing.end_time % 60)
                end_ms = int((entry.timing.end_time % 1) * 1000)
                
                timing_line = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"
                
                # Add entry
                lines.append(str(entry.index))
                lines.append(timing_line)
                lines.append(entry.text)
                lines.append('')  # Empty line between entries
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error writing SRT: {e}")
            return ""
    
    async def _write_vtt(self, track: SubtitleTrack) -> str:
        """Write WebVTT format"""
        try:
            lines = ['WEBVTT', '']
            
            for entry in track.entries:
                # Format timing
                start_h = int(entry.timing.start_time // 3600)
                start_m = int((entry.timing.start_time % 3600) // 60)
                start_s = int(entry.timing.start_time % 60)
                start_ms = int((entry.timing.start_time % 1) * 1000)
                
                end_h = int(entry.timing.end_time // 3600)
                end_m = int((entry.timing.end_time % 3600) // 60)
                end_s = int(entry.timing.end_time % 60)
                end_ms = int((entry.timing.end_time % 1) * 1000)
                
                timing_line = f"{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:03d}"
                
                # Add entry
                lines.append(timing_line)
                lines.append(entry.text)
                lines.append('')  # Empty line between entries
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error writing VTT: {e}")
            return ""
    
    async def _write_ass(self, track: SubtitleTrack) -> str:
        """Write ASS format"""
        try:
            lines = [
                '[Script Info]',
                'Title: Generated by Ainflue',
                'ScriptType: v4.00+',
                '',
                '[V4+ Styles]',
                'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
                'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1',
                '',
                '[Events]',
                'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'
            ]
            
            for entry in track.entries:
                # Format timing for ASS
                start_time = self._seconds_to_ass_time(entry.timing.start_time)
                end_time = self._seconds_to_ass_time(entry.timing.end_time)
                
                dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{entry.text}"
                lines.append(dialogue_line)
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error writing ASS: {e}")
            return ""
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        try:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            centiseconds = int((seconds % 1) * 100)
            
            return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"
            
        except Exception:
            return "0:00:00.00"
    
    async def _write_ssa(self, track: SubtitleTrack) -> str:
        """Write SSA format (similar to ASS)"""
        # SSA is similar to ASS but with different header
        content = await self._write_ass(track)
        # Replace ASS-specific elements with SSA equivalents
        content = content.replace('ScriptType: v4.00+', 'ScriptType: v4.00')
        content = content.replace('[V4+ Styles]', '[V4 Styles]')
        return content
    
    async def _write_ttml(self, track: SubtitleTrack) -> str:
        """Write TTML format"""
        try:
            lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<tt xmlns="http://www.w3.org/ns/ttml" xml:lang="en">',
                '  <head>',
                '    <styling>',
                '      <style xml:id="defaultStyle" tts:fontFamily="Arial" tts:fontSize="20px" tts:color="white"/>',
                '    </styling>',
                '  </head>',
                '  <body>',
                '    <div>'
            ]
            
            for entry in track.entries:
                start_time = self._seconds_to_ttml_time(entry.timing.start_time)
                end_time = self._seconds_to_ttml_time(entry.timing.end_time)
                
                # Escape XML characters
                text = entry.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                p_line = f'      <p begin="{start_time}" end="{end_time}" style="defaultStyle">{text}</p>'
                lines.append(p_line)
            
            lines.extend([
                '    </div>',
                '  </body>',
                '</tt>'
            ])
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error writing TTML: {e}")
            return ""
    
    def _seconds_to_ttml_time(self, seconds: float) -> str:
        """Convert seconds to TTML time format"""
        try:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
            
        except Exception:
            return "00:00:00.000"
    
    async def convert_subtitle_format(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        target_format: SubtitleFormat,
        source_format: Optional[SubtitleFormat] = None
    ) -> bool:
        """Convert subtitle between formats"""
        try:
            # Parse source file
            track = await self.parse_subtitle_file(input_path, source_format)
            
            if not track.entries:
                logger.warning(f"No subtitle entries found in {input_path}")
                return False
            
            # Write in target format
            success = await self.write_subtitle_file(track, output_path, target_format)
            
            if success:
                logger.info(f"Converted subtitle from {track.format.value} to {target_format.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting subtitle format: {e}")
            return False
    
    def validate_subtitle_timing(self, track: SubtitleTrack) -> Dict[str, Any]:
        """Validate subtitle timing and detect issues"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "statistics": {}
            }
            
            overlaps = 0
            gaps = 0
            too_short = 0
            too_long = 0
            reading_speed_issues = 0
            
            min_duration = 0.5  # Minimum 0.5 seconds
            max_duration = 7.0   # Maximum 7 seconds
            max_reading_speed = 20  # Characters per second
            
            for i, entry in enumerate(track.entries):
                # Check duration
                if entry.timing.duration < min_duration:
                    too_short += 1
                    validation_result["warnings"].append(
                        f"Entry {entry.index}: Duration too short ({entry.timing.duration:.2f}s)"
                    )
                
                if entry.timing.duration > max_duration:
                    too_long += 1
                    validation_result["warnings"].append(
                        f"Entry {entry.index}: Duration too long ({entry.timing.duration:.2f}s)"
                    )
                
                # Check reading speed
                char_count = len(entry.text.replace('\n', ''))
                reading_speed = char_count / entry.timing.duration if entry.timing.duration > 0 else 0
                
                if reading_speed > max_reading_speed:
                    reading_speed_issues += 1
                    validation_result["warnings"].append(
                        f"Entry {entry.index}: Reading speed too fast ({reading_speed:.1f} chars/sec)"
                    )
                
                # Check overlaps and gaps with next entry
                if i < len(track.entries) - 1:
                    next_entry = track.entries[i + 1]
                    
                    if entry.timing.end_time > next_entry.timing.start_time:
                        overlaps += 1
                        overlap_duration = entry.timing.end_time - next_entry.timing.start_time
                        validation_result["errors"].append(
                            f"Entries {entry.index}-{next_entry.index}: Overlap of {overlap_duration:.2f}s"
                        )
                        validation_result["valid"] = False
                    
                    gap = next_entry.timing.start_time - entry.timing.end_time
                    if gap > 2.0:  # Gap longer than 2 seconds
                        gaps += 1
                        validation_result["warnings"].append(
                            f"Entries {entry.index}-{next_entry.index}: Long gap of {gap:.2f}s"
                        )
            
            validation_result["statistics"] = {
                "total_entries": len(track.entries),
                "overlaps": overlaps,
                "long_gaps": gaps,
                "too_short": too_short,
                "too_long": too_long,
                "reading_speed_issues": reading_speed_issues,
                "total_duration": track.entries[-1].timing.end_time if track.entries else 0
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating subtitle timing: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "statistics": {}
            }
    
    def get_format_capabilities(self, subtitle_format: SubtitleFormat) -> Dict[str, Any]:
        """Get capabilities of specific subtitle format"""
        try:
            capabilities = {
                SubtitleFormat.SRT: {
                    "supports_styling": False,
                    "supports_positioning": False,
                    "supports_colors": False,
                    "supports_fonts": False,
                    "supports_multiple_languages": False,
                    "web_compatible": True,
                    "player_support": "universal",
                    "file_size": "small"
                },
                SubtitleFormat.VTT: {
                    "supports_styling": True,
                    "supports_positioning": True,
                    "supports_colors": True,
                    "supports_fonts": True,
                    "supports_multiple_languages": True,
                    "web_compatible": True,
                    "player_support": "good",
                    "file_size": "small"
                },
                SubtitleFormat.ASS: {
                    "supports_styling": True,
                    "supports_positioning": True,
                    "supports_colors": True,
                    "supports_fonts": True,
                    "supports_multiple_languages": True,
                    "supports_effects": True,
                    "supports_karaoke": True,
                    "web_compatible": False,
                    "player_support": "limited",
                    "file_size": "medium"
                },
                SubtitleFormat.TTML: {
                    "supports_styling": True,
                    "supports_positioning": True,
                    "supports_colors": True,
                    "supports_fonts": True,
                    "supports_multiple_languages": True,
                    "xml_based": True,
                    "web_compatible": True,
                    "player_support": "good",
                    "file_size": "large"
                }
            }
            
            return capabilities.get(subtitle_format, {})
            
        except Exception as e:
            logger.error(f"Error getting format capabilities: {e}")
            return {}


# Export main classes
__all__ = [
    'SubtitleFormatsManager',
    'SubtitleTrack',
    'SubtitleEntry',
    'TimingInfo',
    'SubtitleStyle',
    'SubtitleFormat',
    'SubtitleType'
]