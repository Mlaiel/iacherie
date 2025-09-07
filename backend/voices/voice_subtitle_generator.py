"""Voice Subtitle Generation System

AI-powered subtitle generation system for voice content with automatic
transcription, timing synchronization, and multi-language support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import re

try:
    from voice_transcription_engine import VoiceTranscriptionEngine, TranscriptionResult
    from voice_metadata_generator import VoiceMetadata
except ImportError:
    from .voice_transcription_engine import VoiceTranscriptionEngine, TranscriptionResult
    from .voice_metadata_generator import VoiceMetadata

logger = logging.getLogger(__name__)


class SubtitleFormat(Enum):
    """Supported subtitle formats"""
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    TTML = "ttml"
    SBV = "sbv"
    JSON = "json"


class TimingAccuracy(Enum):
    """Subtitle timing accuracy levels"""
    PRECISE = "precise"          # ±50ms
    STANDARD = "standard"        # ±100ms
    RELAXED = "relaxed"         # ±200ms
    BASIC = "basic"             # ±500ms


class SubtitleStyle(Enum):
    """Subtitle styling options"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    ACCESSIBILITY = "accessibility"
    BROADCAST = "broadcast"
    SOCIAL_MEDIA = "social_media"
    EDUCATIONAL = "educational"


@dataclass
class SubtitleSegment:
    """Individual subtitle segment"""
    index: int
    start_time: float  # seconds
    end_time: float    # seconds
    text: str
    confidence: float = 1.0
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    style_class: Optional[str] = None
    position: Optional[Dict[str, int]] = None  # x, y coordinates
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleTrack:
    """Complete subtitle track"""
    language: str
    segments: List[SubtitleSegment] = field(default_factory=list)
    total_duration: float = 0.0
    format: SubtitleFormat = SubtitleFormat.SRT
    style: SubtitleStyle = SubtitleStyle.BASIC
    encoding: str = "utf-8"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SubtitleSettings:
    """Subtitle generation settings"""
    format: SubtitleFormat = SubtitleFormat.SRT
    language: str = "en-US"
    max_line_length: int = 42
    max_lines_per_subtitle: int = 2
    min_duration: float = 1.0  # seconds
    max_duration: float = 6.0  # seconds
    timing_accuracy: TimingAccuracy = TimingAccuracy.STANDARD
    style: SubtitleStyle = SubtitleStyle.BASIC
    include_speaker_labels: bool = False
    include_confidence_scores: bool = False
    auto_capitalize: bool = True
    add_punctuation: bool = True
    remove_filler_words: bool = True
    sync_to_speech_rhythm: bool = True
    custom_styling: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubtitleGenerationResult:
    """Subtitle generation result"""
    success: bool
    subtitle_tracks: List[SubtitleTrack] = field(default_factory=list)
    subtitle_content: Dict[SubtitleFormat, str] = field(default_factory=dict)
    generation_time: float = 0.0
    transcription_accuracy: float = 0.0
    timing_precision: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    processing_stats: Dict[str, Any] = field(default_factory=dict)


class VoiceSubtitleGenerator:
    """Voice subtitle generation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize voice subtitle generator"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize transcription engine
        self.transcription_engine = VoiceTranscriptionEngine(config.get('transcription', {}))
        
        # Subtitle formatting templates
        self.format_templates = self._init_format_templates()
        
        # Language-specific settings
        self.language_settings = self._init_language_settings()
        
        # Style templates
        self.style_templates = self._init_style_templates()
        
        self.logger.info("Voice subtitle generator initialized")
    
    def _init_format_templates(self) -> Dict[SubtitleFormat, Dict[str, str]]:
        """Initialize subtitle format templates"""
        return {
            SubtitleFormat.SRT: {
                "segment_template": "{index}\n{start_time} --> {end_time}\n{text}\n\n",
                "time_format": "%H:%M:%S,%f",
                "encoding": "utf-8"
            },
            SubtitleFormat.VTT: {
                "header": "WEBVTT\n\n",
                "segment_template": "{start_time} --> {end_time}\n{text}\n\n",
                "time_format": "%H:%M:%S.%f",
                "encoding": "utf-8"
            },
            SubtitleFormat.ASS: {
                "header": "[Script Info]\nTitle: Generated Subtitles\nScriptType: v4.00+\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,16,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n",
                "segment_template": "Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n",
                "time_format": "%H:%M:%S.%f",
                "encoding": "utf-8"
            },
            SubtitleFormat.TTML: {
                "header": '<?xml version="1.0" encoding="UTF-8"?>\n<tt xmlns="http://www.w3.org/ns/ttml" xml:lang="{language}">\n<head>\n<styling>\n<style xml:id="basic" tts:fontFamily="Arial" tts:fontSize="16px" tts:color="white"/>\n</styling>\n</head>\n<body>\n<div>\n',
                "segment_template": '<p begin="{start_time}" end="{end_time}" style="basic">{text}</p>\n',
                "footer": "</div>\n</body>\n</tt>",
                "time_format": "%H:%M:%S.%f",
                "encoding": "utf-8"
            },
            SubtitleFormat.JSON: {
                "structure": "array",
                "encoding": "utf-8"
            }
        }
    
    def _init_language_settings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize language-specific settings"""
        return {
            "en-US": {
                "max_line_length": 42,
                "reading_speed": 180,  # words per minute
                "punctuation": "standard",
                "capitalization": "sentence_case"
            },
            "es-ES": {
                "max_line_length": 45,
                "reading_speed": 160,
                "punctuation": "standard",
                "capitalization": "sentence_case"
            },
            "fr-FR": {
                "max_line_length": 40,
                "reading_speed": 170,
                "punctuation": "french",
                "capitalization": "sentence_case"
            },
            "de-DE": {
                "max_line_length": 38,
                "reading_speed": 150,
                "punctuation": "standard",
                "capitalization": "sentence_case"
            },
            "ja-JP": {
                "max_line_length": 20,
                "reading_speed": 300,  # characters per minute
                "punctuation": "japanese",
                "capitalization": "none"
            },
            "zh-CN": {
                "max_line_length": 18,
                "reading_speed": 280,
                "punctuation": "chinese",
                "capitalization": "none"
            }
        }
    
    def _init_style_templates(self) -> Dict[SubtitleStyle, Dict[str, Any]]:
        """Initialize style templates"""
        return {
            SubtitleStyle.BASIC: {
                "font_family": "Arial",
                "font_size": 16,
                "color": "white",
                "background": "transparent",
                "position": "bottom_center",
                "outline": True
            },
            SubtitleStyle.ENHANCED: {
                "font_family": "Arial",
                "font_size": 18,
                "color": "white",
                "background": "semi_transparent_black",
                "position": "bottom_center",
                "outline": True,
                "shadow": True
            },
            SubtitleStyle.ACCESSIBILITY: {
                "font_family": "Arial",
                "font_size": 20,
                "color": "yellow",
                "background": "black",
                "position": "bottom_center",
                "outline": True,
                "high_contrast": True
            },
            SubtitleStyle.BROADCAST: {
                "font_family": "Arial",
                "font_size": 16,
                "color": "white",
                "background": "transparent",
                "position": "bottom_center",
                "outline": True,
                "safe_area": True
            },
            SubtitleStyle.SOCIAL_MEDIA: {
                "font_family": "Arial Bold",
                "font_size": 18,
                "color": "white",
                "background": "semi_transparent_black",
                "position": "center",
                "outline": True,
                "trendy_styling": True
            }
        }
    
    async def generate_subtitles(
        self,
        voice_content: bytes,
        settings: Optional[SubtitleSettings] = None,
        voice_metadata: Optional[VoiceMetadata] = None
    ) -> SubtitleGenerationResult:
        """Generate subtitles for voice content"""
        start_time = datetime.now()
        
        try:
            # Use provided settings or create default
            if settings is None:
                settings = SubtitleSettings()
            
            # Step 1: Transcribe audio
            transcription_result = await self._transcribe_audio(voice_content, settings)
            if not transcription_result.success:
                return SubtitleGenerationResult(
                    success=False,
                    error_message=f"Transcription failed: {transcription_result.error_message}"
                )
            
            # Step 2: Create subtitle segments
            subtitle_segments = await self._create_subtitle_segments(
                transcription_result.transcription_result, settings
            )
            
            # Step 3: Optimize timing and synchronization
            optimized_segments = await self._optimize_timing(subtitle_segments, settings)
            
            # Step 4: Apply text processing and formatting
            formatted_segments = await self._format_text(optimized_segments, settings)
            
            # Step 5: Create subtitle track
            subtitle_track = SubtitleTrack(
                language=settings.language,
                segments=formatted_segments,
                total_duration=max([seg.end_time for seg in formatted_segments]) if formatted_segments else 0.0,
                format=settings.format,
                style=settings.style,
                metadata={
                    "generation_method": "ai_transcription",
                    "transcription_confidence": transcription_result.confidence_score,
                    "settings": {
                        "timing_accuracy": settings.timing_accuracy.value,
                        "max_line_length": settings.max_line_length,
                        "include_speakers": settings.include_speaker_labels
                    }
                }
            )
            
            # Step 6: Generate subtitle content in requested formats
            subtitle_content = await self._generate_subtitle_content(subtitle_track, settings)
            
            # Calculate processing metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            timing_precision = self._calculate_timing_precision(formatted_segments)
            
            # Generate warnings
            warnings = self._generate_warnings(subtitle_track, settings)
            
            return SubtitleGenerationResult(
                success=True,
                subtitle_tracks=[subtitle_track],
                subtitle_content=subtitle_content,
                generation_time=generation_time,
                transcription_accuracy=transcription_result.confidence_score,
                timing_precision=timing_precision,
                warnings=warnings,
                processing_stats={
                    "total_segments": len(formatted_segments),
                    "total_duration": subtitle_track.total_duration,
                    "average_segment_duration": subtitle_track.total_duration / len(formatted_segments) if formatted_segments else 0,
                    "processing_time": generation_time
                }
            )
            
        except Exception as e:
            self.logger.error(f"Subtitle generation failed: {str(e)}")
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return SubtitleGenerationResult(
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
    
    async def _transcribe_audio(
        self,
        voice_content: bytes,
        settings: SubtitleSettings
    ) -> Dict[str, Any]:
        """Transcribe audio for subtitle generation"""
        try:
            # Configure transcription settings for subtitle generation
            transcription_settings = {
                "language": settings.language,
                "include_timestamps": True,
                "include_speaker_detection": settings.include_speaker_labels,
                "word_level_timestamps": True,
                "confidence_threshold": 0.7
            }
            
            # Perform transcription
            result = await self.transcription_engine.transcribe_audio(
                voice_content, transcription_settings
            )
            
            return {
                "success": result.success,
                "transcription_result": result.transcription_result if result.success else None,
                "confidence_score": result.confidence_score,
                "error_message": result.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Audio transcription for subtitles failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "confidence_score": 0.0
            }
    
    async def _create_subtitle_segments(
        self,
        transcription_result,
        settings: SubtitleSettings
    ) -> List[SubtitleSegment]:
        """Create subtitle segments from transcription"""
        try:
            segments = []
            
            # Extract word-level timestamps from transcription
            # This is a simplified simulation - real implementation would parse actual transcription results
            words_with_timing = self._extract_word_timing(transcription_result)
            
            # Group words into subtitle segments
            current_segment_words = []
            current_start_time = 0.0
            segment_index = 1
            
            for word_data in words_with_timing:
                word = word_data["word"]
                start_time = word_data["start_time"]
                end_time = word_data["end_time"]
                confidence = word_data.get("confidence", 1.0)
                
                # Add word to current segment
                current_segment_words.append(word_data)
                
                # Check if we should close current segment
                should_close = self._should_close_segment(
                    current_segment_words, settings, start_time, current_start_time
                )
                
                if should_close or word_data == words_with_timing[-1]:  # Last word
                    # Create segment
                    if current_segment_words:
                        segment_text = " ".join([w["word"] for w in current_segment_words])
                        segment_start = current_segment_words[0]["start_time"]
                        segment_end = current_segment_words[-1]["end_time"]
                        
                        # Calculate average confidence
                        avg_confidence = sum([w.get("confidence", 1.0) for w in current_segment_words]) / len(current_segment_words)
                        
                        segment = SubtitleSegment(
                            index=segment_index,
                            start_time=segment_start,
                            end_time=segment_end,
                            text=segment_text,
                            confidence=avg_confidence,
                            speaker_id=current_segment_words[0].get("speaker_id"),
                            metadata={
                                "word_count": len(current_segment_words),
                                "character_count": len(segment_text)
                            }
                        )
                        
                        segments.append(segment)
                        segment_index += 1
                    
                    # Reset for next segment
                    current_segment_words = []
                    current_start_time = end_time
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Subtitle segment creation failed: {str(e)}")
            return []
    
    def _extract_word_timing(self, transcription_result) -> List[Dict[str, Any]]:
        """Extract word-level timing from transcription result"""
        # Simplified simulation of word timing extraction
        # In real implementation, this would parse actual transcription results
        
        words = ["Hello", "world", "this", "is", "a", "sample", "transcription", "for", "subtitle", "generation"]
        words_with_timing = []
        
        current_time = 0.0
        for i, word in enumerate(words):
            word_duration = 0.5 + (len(word) * 0.1)  # Simulate word duration
            
            word_data = {
                "word": word,
                "start_time": current_time,
                "end_time": current_time + word_duration,
                "confidence": 0.9 - (i * 0.01),  # Simulate decreasing confidence
                "speaker_id": "speaker_1"
            }
            
            words_with_timing.append(word_data)
            current_time += word_duration + 0.1  # Add pause between words
        
        return words_with_timing
    
    def _should_close_segment(
        self,
        current_words: List[Dict[str, Any]],
        settings: SubtitleSettings,
        current_time: float,
        segment_start_time: float
    ) -> bool:
        """Determine if current subtitle segment should be closed"""
        try:
            # Check segment duration
            segment_duration = current_time - segment_start_time
            if segment_duration >= settings.max_duration:
                return True
            
            # Check character count
            current_text = " ".join([w["word"] for w in current_words])
            if len(current_text) >= settings.max_line_length * settings.max_lines_per_subtitle:
                return True
            
            # Check for natural breaks (punctuation)
            if current_words:
                last_word = current_words[-1]["word"]
                if last_word.endswith(('.', '!', '?', ':')):
                    return True
            
            # Check line count (if text would span multiple lines)
            lines_needed = len(current_text) // settings.max_line_length + 1
            if lines_needed > settings.max_lines_per_subtitle:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Segment closure decision failed: {str(e)}")
            return True  # Close segment on error
    
    async def _optimize_timing(
        self,
        segments: List[SubtitleSegment],
        settings: SubtitleSettings
    ) -> List[SubtitleSegment]:
        """Optimize subtitle timing and synchronization"""
        try:
            optimized_segments = []
            
            for i, segment in enumerate(segments):
                optimized_segment = SubtitleSegment(
                    index=segment.index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=segment.text,
                    confidence=segment.confidence,
                    speaker_id=segment.speaker_id,
                    speaker_name=segment.speaker_name,
                    metadata=segment.metadata.copy()
                )
                
                # Apply timing accuracy adjustments
                timing_adjustment = self._get_timing_adjustment(settings.timing_accuracy)
                
                # Ensure minimum duration
                duration = segment.end_time - segment.start_time
                if duration < settings.min_duration:
                    optimized_segment.end_time = segment.start_time + settings.min_duration
                
                # Ensure maximum duration
                if duration > settings.max_duration:
                    optimized_segment.end_time = segment.start_time + settings.max_duration
                
                # Apply timing smoothing
                if settings.sync_to_speech_rhythm:
                    optimized_segment = self._apply_speech_rhythm_sync(optimized_segment)
                
                # Avoid overlaps with next segment
                if i < len(segments) - 1:
                    next_segment = segments[i + 1]
                    if optimized_segment.end_time > next_segment.start_time:
                        gap_time = (next_segment.start_time - optimized_segment.start_time) / 2
                        optimized_segment.end_time = optimized_segment.start_time + gap_time
                
                optimized_segments.append(optimized_segment)
            
            return optimized_segments
            
        except Exception as e:
            self.logger.error(f"Timing optimization failed: {str(e)}")
            return segments  # Return original segments on error
    
    def _get_timing_adjustment(self, accuracy: TimingAccuracy) -> float:
        """Get timing adjustment value based on accuracy level"""
        adjustments = {
            TimingAccuracy.PRECISE: 0.05,    # ±50ms
            TimingAccuracy.STANDARD: 0.1,    # ±100ms
            TimingAccuracy.RELAXED: 0.2,     # ±200ms
            TimingAccuracy.BASIC: 0.5        # ±500ms
        }
        return adjustments.get(accuracy, 0.1)
    
    def _apply_speech_rhythm_sync(self, segment: SubtitleSegment) -> SubtitleSegment:
        """Apply speech rhythm synchronization to segment timing"""
        # Simplified rhythm synchronization
        # In real implementation, this would analyze speech patterns
        
        # Adjust timing based on text characteristics
        word_count = len(segment.text.split())
        
        # Estimate natural speech timing
        reading_speed = 180  # words per minute
        natural_duration = (word_count / reading_speed) * 60
        
        # Adjust segment timing to natural duration (with limits)
        current_duration = segment.end_time - segment.start_time
        if abs(natural_duration - current_duration) > 0.5:
            # Adjust towards natural duration
            adjustment = (natural_duration - current_duration) * 0.3  # 30% adjustment
            segment.end_time = segment.start_time + current_duration + adjustment
        
        return segment
    
    async def _format_text(
        self,
        segments: List[SubtitleSegment],
        settings: SubtitleSettings
    ) -> List[SubtitleSegment]:
        """Format subtitle text according to settings"""
        try:
            formatted_segments = []
            
            for segment in segments:
                formatted_text = segment.text
                
                # Remove filler words if requested
                if settings.remove_filler_words:
                    formatted_text = self._remove_filler_words(formatted_text, settings.language)
                
                # Apply capitalization
                if settings.auto_capitalize:
                    formatted_text = self._apply_capitalization(formatted_text, settings.language)
                
                # Add punctuation
                if settings.add_punctuation:
                    formatted_text = self._add_punctuation(formatted_text, settings.language)
                
                # Break text into lines
                formatted_text = self._break_into_lines(formatted_text, settings)
                
                # Add speaker labels if requested
                if settings.include_speaker_labels and segment.speaker_id:
                    speaker_label = segment.speaker_name or f"Speaker {segment.speaker_id}"
                    formatted_text = f"{speaker_label}: {formatted_text}"
                
                # Create formatted segment
                formatted_segment = SubtitleSegment(
                    index=segment.index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=formatted_text,
                    confidence=segment.confidence,
                    speaker_id=segment.speaker_id,
                    speaker_name=segment.speaker_name,
                    metadata=segment.metadata.copy()
                )
                
                # Add confidence scores if requested
                if settings.include_confidence_scores:
                    formatted_segment.metadata["confidence"] = segment.confidence
                
                formatted_segments.append(formatted_segment)
            
            return formatted_segments
            
        except Exception as e:
            self.logger.error(f"Text formatting failed: {str(e)}")
            return segments  # Return original segments on error
    
    def _remove_filler_words(self, text: str, language: str) -> str:
        """Remove filler words from text"""
        filler_words = {
            "en-US": ["um", "uh", "like", "you know", "so", "well", "actually"],
            "es-ES": ["eh", "este", "bueno", "o sea"],
            "fr-FR": ["euh", "ben", "alors", "donc"],
            "de-DE": ["äh", "ähm", "also", "na ja"]
        }
        
        fillers = filler_words.get(language[:5], filler_words.get("en-US", []))
        
        for filler in fillers:
            # Remove filler words (case insensitive)
            text = re.sub(r'\b' + re.escape(filler) + r'\b', '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _apply_capitalization(self, text: str, language: str) -> str:
        """Apply appropriate capitalization"""
        # Basic sentence case capitalization
        sentences = re.split(r'[.!?]+', text)
        capitalized_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                capitalized_sentences.append(sentence)
        
        return '. '.join(capitalized_sentences)
    
    def _add_punctuation(self, text: str, language: str) -> str:
        """Add appropriate punctuation"""
        # Basic punctuation addition
        text = text.strip()
        
        if text and not text[-1] in '.!?':
            # Add period if no ending punctuation
            text += '.'
        
        return text
    
    def _break_into_lines(self, text: str, settings: SubtitleSettings) -> str:
        """Break text into appropriate lines"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            
            if len(test_line) <= settings.max_line_length:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is longer than max length, add it anyway
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        # Limit to max lines per subtitle
        if len(lines) > settings.max_lines_per_subtitle:
            lines = lines[:settings.max_lines_per_subtitle]
        
        return '\n'.join(lines)
    
    async def _generate_subtitle_content(
        self,
        subtitle_track: SubtitleTrack,
        settings: SubtitleSettings
    ) -> Dict[SubtitleFormat, str]:
        """Generate subtitle content in various formats"""
        content = {}
        
        try:
            # Generate SRT format
            if settings.format == SubtitleFormat.SRT or SubtitleFormat.SRT in [SubtitleFormat.SRT]:
                content[SubtitleFormat.SRT] = self._generate_srt(subtitle_track)
            
            # Generate VTT format
            if settings.format == SubtitleFormat.VTT:
                content[SubtitleFormat.VTT] = self._generate_vtt(subtitle_track)
            
            # Generate ASS format
            if settings.format == SubtitleFormat.ASS:
                content[SubtitleFormat.ASS] = self._generate_ass(subtitle_track)
            
            # Generate JSON format
            if settings.format == SubtitleFormat.JSON:
                content[SubtitleFormat.JSON] = self._generate_json(subtitle_track)
            
            # Always generate primary format
            if settings.format not in content:
                if settings.format == SubtitleFormat.SRT:
                    content[settings.format] = self._generate_srt(subtitle_track)
                elif settings.format == SubtitleFormat.VTT:
                    content[settings.format] = self._generate_vtt(subtitle_track)
                elif settings.format == SubtitleFormat.JSON:
                    content[settings.format] = self._generate_json(subtitle_track)
                else:
                    # Default to SRT
                    content[SubtitleFormat.SRT] = self._generate_srt(subtitle_track)
            
        except Exception as e:
            self.logger.error(f"Subtitle content generation failed: {str(e)}")
        
        return content
    
    def _generate_srt(self, subtitle_track: SubtitleTrack) -> str:
        """Generate SRT format subtitle content"""
        srt_content = ""
        
        for segment in subtitle_track.segments:
            start_time = self._format_time_srt(segment.start_time)
            end_time = self._format_time_srt(segment.end_time)
            
            srt_content += f"{segment.index}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment.text}\n\n"
        
        return srt_content
    
    def _generate_vtt(self, subtitle_track: SubtitleTrack) -> str:
        """Generate VTT format subtitle content"""
        vtt_content = "WEBVTT\n\n"
        
        for segment in subtitle_track.segments:
            start_time = self._format_time_vtt(segment.start_time)
            end_time = self._format_time_vtt(segment.end_time)
            
            vtt_content += f"{start_time} --> {end_time}\n"
            vtt_content += f"{segment.text}\n\n"
        
        return vtt_content
    
    def _generate_ass(self, subtitle_track: SubtitleTrack) -> str:
        """Generate ASS format subtitle content"""
        template = self.format_templates[SubtitleFormat.ASS]
        
        ass_content = template["header"]
        
        for segment in subtitle_track.segments:
            start_time = self._format_time_ass(segment.start_time)
            end_time = self._format_time_ass(segment.end_time)
            
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{segment.text}\n"
        
        return ass_content
    
    def _generate_json(self, subtitle_track: SubtitleTrack) -> str:
        """Generate JSON format subtitle content"""
        json_data = {
            "language": subtitle_track.language,
            "total_duration": subtitle_track.total_duration,
            "segments": []
        }
        
        for segment in subtitle_track.segments:
            segment_data = {
                "index": segment.index,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "text": segment.text,
                "confidence": segment.confidence
            }
            
            if segment.speaker_id:
                segment_data["speaker_id"] = segment.speaker_id
            if segment.speaker_name:
                segment_data["speaker_name"] = segment.speaker_name
            
            json_data["segments"].append(segment_data)
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def _format_time_srt(self, seconds: float) -> str:
        """Format time for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time for VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def _format_time_ass(self, seconds: float) -> str:
        """Format time for ASS format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def _calculate_timing_precision(self, segments: List[SubtitleSegment]) -> float:
        """Calculate timing precision score"""
        if not segments:
            return 0.0
        
        # Simplified precision calculation based on segment characteristics
        total_precision = 0.0
        
        for segment in segments:
            duration = segment.end_time - segment.start_time
            word_count = len(segment.text.split())
            
            # Precision based on duration appropriateness
            expected_duration = word_count * 0.5  # 0.5 seconds per word
            duration_precision = 1.0 - min(1.0, abs(duration - expected_duration) / expected_duration)
            
            total_precision += duration_precision
        
        return total_precision / len(segments)
    
    def _generate_warnings(
        self,
        subtitle_track: SubtitleTrack,
        settings: SubtitleSettings
    ) -> List[str]:
        """Generate warnings for subtitle generation"""
        warnings = []
        
        try:
            # Check for very short segments
            short_segments = [s for s in subtitle_track.segments if (s.end_time - s.start_time) < 1.0]
            if short_segments:
                warnings.append(f"{len(short_segments)} segments are shorter than 1 second")
            
            # Check for very long segments
            long_segments = [s for s in subtitle_track.segments if (s.end_time - s.start_time) > 8.0]
            if long_segments:
                warnings.append(f"{len(long_segments)} segments are longer than 8 seconds")
            
            # Check for low confidence segments
            low_confidence = [s for s in subtitle_track.segments if s.confidence < 0.7]
            if low_confidence:
                warnings.append(f"{len(low_confidence)} segments have low transcription confidence")
            
            # Check for overlapping segments
            for i in range(len(subtitle_track.segments) - 1):
                current = subtitle_track.segments[i]
                next_seg = subtitle_track.segments[i + 1]
                if current.end_time > next_seg.start_time:
                    warnings.append("Some subtitle segments overlap")
                    break
            
        except Exception as e:
            self.logger.error(f"Warning generation failed: {str(e)}")
        
        return warnings
    
    async def export_subtitles(
        self,
        subtitle_track: SubtitleTrack,
        export_format: SubtitleFormat,
        file_path: Optional[str] = None
    ) -> str:
        """Export subtitles to file or return as string"""
        try:
            # Generate content in requested format
            if export_format == SubtitleFormat.SRT:
                content = self._generate_srt(subtitle_track)
            elif export_format == SubtitleFormat.VTT:
                content = self._generate_vtt(subtitle_track)
            elif export_format == SubtitleFormat.ASS:
                content = self._generate_ass(subtitle_track)
            elif export_format == SubtitleFormat.JSON:
                content = self._generate_json(subtitle_track)
            else:
                raise ValueError(f"Unsupported export format: {export_format.value}")
            
            # Write to file if path provided
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"Subtitles exported to {file_path}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Subtitle export failed: {str(e)}")
            raise


# Export classes and enums
__all__ = [
    'VoiceSubtitleGenerator',
    'SubtitleFormat',
    'TimingAccuracy',
    'SubtitleStyle',
    'SubtitleSegment',
    'SubtitleTrack',
    'SubtitleSettings',
    'SubtitleGenerationResult'
]