"""
Music Generator - Advanced AI Music Generation Engine
=====================================================

Professional-grade AI music generation system providing composition,
arrangement, and production capabilities for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
This software is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any attempt to copy, distribute, or reverse engineer this code without explicit
written permission is strictly forbidden and will result in legal prosecution
under German and International Copyright Law.

Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import json
from pathlib import Path
import uuid

from ...ai.audio_processing.music_generation import MusicGenerationEngine
from ...ai.engines.audio_engine import MusicGenerationEngine as AudioMusicEngine
from ...ai.ml.music_intelligence import MusicGenre, MusicKey, TimeSignature
try:
    from core.exceptions import MusicGenerationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    MusicGenerationError = globals().get('MusicGenerationError', Exception)
from ...core.logging import get_logger
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class GenerationMode(Enum):
    """Music generation modes"""
    COMPOSITION = "composition"
    ARRANGEMENT = "arrangement"
    ACCOMPANIMENT = "accompaniment"
    VARIATION = "variation"
    REMIX = "remix"


class InstrumentType(Enum):
    """Instrument types for generation"""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    STRINGS = "strings"
    BRASS = "brass"
    WOODWINDS = "woodwinds"
    SYNTHESIZER = "synthesizer"
    VOCALS = "vocals"
    PERCUSSION = "percussion"


class MusicStyle(Enum):
    """Musical styles for generation"""
    CLASSICAL = "classical"
    JAZZ = "jazz"
    ROCK = "rock"
    POP = "pop"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    LATIN = "latin"
    AMBIENT = "ambient"
    CINEMATIC = "cinematic"


class EmotionalArc(Enum):
    """Emotional arc patterns"""
    BUILDING = "building"
    DECLINING = "declining"
    STABLE = "stable"
    DRAMATIC = "dramatic"
    CYCLICAL = "cyclical"
    EXPLOSIVE = "explosive"


@dataclass
class GenerationParameters:
    """Music generation parameters"""
    # Basic parameters
    genre: MusicGenre = MusicGenre.ELECTRONIC
    style: MusicStyle = MusicStyle.ELECTRONIC
    key: MusicKey = MusicKey.C_MAJOR
    time_signature: TimeSignature = TimeSignature.FOUR_FOUR
    tempo: int = 120
    duration: int = 180  # seconds
    
    # Structural parameters
    mode: GenerationMode = GenerationMode.COMPOSITION
    emotional_arc: EmotionalArc = EmotionalArc.BUILDING
    complexity_level: float = 0.5  # 0.0 to 1.0
    
    # Instrumentation
    instruments: List[InstrumentType] = field(default_factory=lambda: [
        InstrumentType.PIANO, InstrumentType.DRUMS, InstrumentType.BASS
    ])
    lead_instrument: Optional[InstrumentType] = None
    
    # Musical elements
    chord_progressions: Optional[List[str]] = None
    melodic_seed: Optional[List[float]] = None
    rhythmic_pattern: Optional[str] = None
    
    # AI parameters
    creativity_level: float = 0.7  # 0.0 to 1.0
    variation_intensity: float = 0.5  # 0.0 to 1.0
    structure_strictness: float = 0.6  # 0.0 to 1.0


@dataclass
class MusicSection:
    """Generated music section"""
    section_id: str
    section_type: str
    start_time: float
    end_time: float
    duration: float
    
    # Musical content
    melody: List[Dict[str, Any]] = field(default_factory=list)
    harmony: List[Dict[str, Any]] = field(default_factory=list)
    rhythm: List[Dict[str, Any]] = field(default_factory=list)
    
    # Instrumentation
    active_instruments: List[InstrumentType] = field(default_factory=list)
    dynamics: float = 0.7
    tempo: Optional[int] = None
    
    # Metadata
    emotional_intensity: float = 0.5
    complexity_score: float = 0.5


@dataclass
class GeneratedTrack:
    """Complete generated music track"""
    track_id: str
    title: Optional[str] = None
    
    # Generation parameters
    parameters: Optional[GenerationParameters] = None
    
    # Musical structure
    sections: List[MusicSection] = field(default_factory=list)
    overall_structure: str = "verse-chorus"
    total_duration: float = 0.0
    
    # Audio data
    audio_data: Optional[np.ndarray] = None
    sample_rate: int = 44100
    
    # Export formats
    midi_data: Optional[bytes] = None
    audio_file_path: Optional[str] = None
    score_data: Optional[Dict[str, Any]] = None
    
    # Analysis metrics
    quality_score: float = 0.0
    originality_score: float = 0.0
    commercial_viability: float = 0.0
    
    # Metadata
    generation_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    model_version: str = "1.0.0"


@dataclass
class GenerationResult:
    """Music generation result with metadata"""
    success: bool
    track: Optional[GeneratedTrack] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    generation_stats: Dict[str, Any] = field(default_factory=dict)


class MusicGenerator:
    """
    Advanced AI music generation engine for professional content creation.
    
    Provides comprehensive music generation capabilities including composition,
    arrangement, and production with AI-powered creative assistance.
    """

    def __init__(self):
        """Initialize music generator with AI models"""
        self.generation_engine = MusicGenerationEngine()
        self.audio_engine = AudioMusicEngine()
        
        # Generation models (would be loaded from files in production)
        self.models = {
            'composition': None,
            'harmony': None,
            'rhythm': None,
            'orchestration': None
        }
        
        # Generation cache
        self._generation_cache: Dict[str, GeneratedTrack] = {}
        self._template_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load templates
        self._load_composition_templates()
        
        logger.info("Music Generator initialized successfully")

    async def generate_music(
        self, 
        parameters: GenerationParameters,
        reference_audio: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate music based on specified parameters.
        
        Args:
            parameters: Generation parameters
            reference_audio: Optional reference audio for style matching
            
        Returns:
            Complete music generation result
        """
        start_time = datetime.now()
        
        try:
            # Validate parameters
            self._validate_generation_parameters(parameters)
            
            # Generate unique track ID
            track_id = f"gen_{uuid.uuid4().hex[:8]}_{int(start_time.timestamp())}"
            
            logger.info(f"Starting music generation: {track_id}")
            
            # Initialize track
            track = GeneratedTrack(
                track_id=track_id,
                parameters=parameters,
                sample_rate=44100
            )
            
            # Generate musical structure
            structure = await self._generate_musical_structure(parameters)
            
            # Generate sections in parallel
            section_tasks = [
                self._generate_section(section_def, parameters, i)
                for i, section_def in enumerate(structure)
            ]
            
            sections = await asyncio.gather(*section_tasks)
            track.sections = sections
            
            # Calculate total duration
            track.total_duration = sum(section.duration for section in sections)
            track.overall_structure = self._identify_structure_type(structure)
            
            # Generate audio if requested
            if parameters.mode in [GenerationMode.COMPOSITION, GenerationMode.ARRANGEMENT]:
                track.audio_data = await self._generate_audio_data(track, parameters)
            
            # Generate MIDI data
            track.midi_data = await self._generate_midi_data(track, parameters)
            
            # Calculate quality metrics
            track = await self._calculate_generation_metrics(track, parameters)
            
            # Set processing time
            track.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Cache result
            self._generation_cache[track_id] = track
            
            result = GenerationResult(
                success=True,
                track=track,
                generation_stats={
                    'sections_generated': len(sections),
                    'total_duration': track.total_duration,
                    'processing_time': track.processing_time,
                    'instruments_used': len(parameters.instruments)
                }
            )
            
            logger.info(f"Music generation completed: {track_id}")
            return result
            
        except Exception as e:
            logger.error(f"Music generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e),
                generation_stats={'processing_time': (datetime.now() - start_time).total_seconds()}
            )

    async def generate_variation(
        self, 
        original_track: GeneratedTrack,
        variation_parameters: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Generate variation of existing track"""
        try:
            if not original_track.parameters:
                raise MusicGenerationError("Original track missing generation parameters")
            
            # Create variation parameters
            var_params = GenerationParameters(**original_track.parameters.__dict__)
            var_params.mode = GenerationMode.VARIATION
            
            # Apply variation modifications
            if variation_parameters:
                for key, value in variation_parameters.items():
                    if hasattr(var_params, key):
                        setattr(var_params, key, value)
            
            # Increase creativity for variation
            var_params.creativity_level = min(var_params.creativity_level + 0.2, 1.0)
            var_params.variation_intensity = variation_parameters.get('intensity', 0.7)
            
            # Generate variation
            result = await self.generate_music(var_params)
            
            if result.success and result.track:
                result.track.title = f"{original_track.title or 'Track'} - Variation"
            
            return result
            
        except Exception as e:
            logger.error(f"Variation generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e)
            )

    async def generate_accompaniment(
        self, 
        lead_audio_path: str,
        accompaniment_style: MusicStyle = MusicStyle.POP
    ) -> GenerationResult:
        """Generate accompaniment for existing audio"""
        try:
            # Analyze lead audio
            lead_analysis = await self._analyze_lead_audio(lead_audio_path)
            
            # Create accompaniment parameters
            params = GenerationParameters(
                mode=GenerationMode.ACCOMPANIMENT,
                style=accompaniment_style,
                key=lead_analysis.get('key', MusicKey.C_MAJOR),
                tempo=lead_analysis.get('tempo', 120),
                duration=lead_analysis.get('duration', 180),
                time_signature=lead_analysis.get('time_signature', TimeSignature.FOUR_FOUR)
            )
            
            # Select accompaniment instruments
            params.instruments = self._select_accompaniment_instruments(
                accompaniment_style, lead_analysis
            )
            
            # Generate accompaniment
            result = await self.generate_music(params, reference_audio=lead_audio_path)
            
            if result.success and result.track:
                result.track.title = f"Accompaniment - {accompaniment_style.value}"
            
            return result
            
        except Exception as e:
            logger.error(f"Accompaniment generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e)
            )

    async def generate_remix(
        self, 
        original_audio_path: str,
        remix_style: MusicStyle,
        intensity: float = 0.7
    ) -> GenerationResult:
        """Generate remix of existing track"""
        try:
            # Analyze original audio
            original_analysis = await self._analyze_lead_audio(original_audio_path)
            
            # Create remix parameters
            params = GenerationParameters(
                mode=GenerationMode.REMIX,
                style=remix_style,
                key=original_analysis.get('key', MusicKey.C_MAJOR),
                tempo=self._calculate_remix_tempo(
                    original_analysis.get('tempo', 120), remix_style
                ),
                duration=original_analysis.get('duration', 180),
                creativity_level=intensity,
                variation_intensity=intensity
            )
            
            # Select remix instrumentation
            params.instruments = self._select_remix_instruments(remix_style)
            
            # Generate remix
            result = await self.generate_music(params, reference_audio=original_audio_path)
            
            if result.success and result.track:
                result.track.title = f"Remix - {remix_style.value}"
            
            return result
            
        except Exception as e:
            logger.error(f"Remix generation failed: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e)
            )

    async def export_track(
        self, 
        track: GeneratedTrack,
        export_format: str = "wav",
        output_path: Optional[str] = None
    ) -> Dict[str, str]:
        """Export generated track to various formats"""
        try:
            exports = {}
            
            base_path = output_path or f"./exports/{track.track_id}"
            Path(base_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Export audio
            if track.audio_data is not None and export_format in ['wav', 'mp3', 'flac']:
                audio_path = await self._export_audio(
                    track, f"{base_path}.{export_format}", export_format
                )
                exports['audio'] = audio_path
            
            # Export MIDI
            if track.midi_data is not None:
                midi_path = f"{base_path}.mid"
                await self._export_midi(track, midi_path)
                exports['midi'] = midi_path
            
            # Export score (MusicXML/PDF)
            if track.score_data is not None:
                score_path = f"{base_path}.xml"
                await self._export_score(track, score_path)
                exports['score'] = score_path
            
            # Export metadata
            metadata_path = f"{base_path}_metadata.json"
            await self._export_metadata(track, metadata_path)
            exports['metadata'] = metadata_path
            
            logger.info(f"Track exported: {track.track_id}")
            return exports
            
        except Exception as e:
            logger.error(f"Track export failed: {str(e)}")
            raise MusicGenerationError(f"Export failed: {str(e)}")

    async def _generate_musical_structure(
        self, 
        parameters: GenerationParameters
    ) -> List[Dict[str, Any]]:
        """Generate overall musical structure"""
        try:
            # Get structure template based on style and genre
            template = self._get_structure_template(parameters.style, parameters.genre)
            
            # Calculate section durations
            total_duration = parameters.duration
            structure = []
            
            for i, section_type in enumerate(template):
                # Calculate relative duration
                section_weight = self._get_section_weight(section_type)
                duration = (total_duration * section_weight) / sum(
                    self._get_section_weight(s) for s in template
                )
                
                start_time = sum(s.get('duration', 0) for s in structure)
                
                structure.append({
                    'type': section_type,
                    'start_time': start_time,
                    'duration': duration,
                    'intensity': self._calculate_section_intensity(
                        i, len(template), parameters.emotional_arc
                    )
                })
            
            return structure
            
        except Exception as e:
            logger.error(f"Structure generation failed: {str(e)}")
            return self._get_default_structure(parameters.duration)

    async def _generate_section(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters,
        section_index: int
    ) -> MusicSection:
        """Generate individual music section"""
        try:
            section_id = f"sec_{section_index}_{section_def['type']}"
            
            section = MusicSection(
                section_id=section_id,
                section_type=section_def['type'],
                start_time=section_def['start_time'],
                end_time=section_def['start_time'] + section_def['duration'],
                duration=section_def['duration'],
                emotional_intensity=section_def['intensity']
            )
            
            # Generate musical elements in parallel
            melody_task = self._generate_melody(section_def, parameters)
            harmony_task = self._generate_harmony(section_def, parameters)
            rhythm_task = self._generate_rhythm(section_def, parameters)
            
            melody, harmony, rhythm = await asyncio.gather(
                melody_task, harmony_task, rhythm_task
            )
            
            section.melody = melody
            section.harmony = harmony
            section.rhythm = rhythm
            
            # Determine active instruments
            section.active_instruments = self._select_section_instruments(
                section_def, parameters
            )
            
            # Calculate section complexity
            section.complexity_score = self._calculate_section_complexity(section)
            
            # Set dynamics
            section.dynamics = self._calculate_section_dynamics(
                section_def['intensity'], parameters
            )
            
            return section
            
        except Exception as e:
            logger.error(f"Section generation failed: {str(e)}")
            return self._create_empty_section(section_def, section_index)

    async def _generate_melody(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters
    ) -> List[Dict[str, Any]]:
        """Generate melodic content for section"""
        try:
            melody = []
            
            # Use AI model for melody generation
            if hasattr(self.generation_engine, 'generate_melody'):
                ai_melody = await self.generation_engine.generate_melody(
                    style=parameters.style.value,
                    key=parameters.key.name,
                    duration=section_def['duration'],
                    complexity=parameters.complexity_level
                )
                
                # Convert AI melody to internal format
                melody = self._convert_ai_melody(ai_melody)
            
            else:
                # Fallback procedural melody generation
                melody = await self._generate_procedural_melody(section_def, parameters)
            
            return melody
            
        except Exception as e:
            logger.warning(f"Melody generation failed, using fallback: {str(e)}")
            return await self._generate_procedural_melody(section_def, parameters)

    async def _generate_harmony(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters
    ) -> List[Dict[str, Any]]:
        """Generate harmonic content for section"""
        try:
            # Use provided chord progressions or generate new ones
            if parameters.chord_progressions:
                progression = parameters.chord_progressions[0]  # Use first progression
            else:
                progression = self._generate_chord_progression(
                    parameters.style, parameters.key
                )
            
            harmony = []
            chord_duration = section_def['duration'] / len(progression)
            
            for i, chord in enumerate(progression):
                harmony.append({
                    'chord': chord,
                    'start_time': i * chord_duration,
                    'duration': chord_duration,
                    'velocity': self._calculate_chord_velocity(
                        section_def['intensity']
                    )
                })
            
            return harmony
            
        except Exception as e:
            logger.warning(f"Harmony generation failed: {str(e)}")
            return []

    async def _generate_rhythm(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters
    ) -> List[Dict[str, Any]]:
        """Generate rhythmic content for section"""
        try:
            rhythm = []
            
            # Get rhythm pattern for style
            pattern = self._get_rhythm_pattern(parameters.style, parameters.tempo)
            
            # Generate rhythm events
            beat_duration = 60.0 / parameters.tempo
            pattern_duration = len(pattern) * beat_duration
            repetitions = int(section_def['duration'] / pattern_duration) + 1
            
            for rep in range(repetitions):
                for i, beat_strength in enumerate(pattern):
                    if beat_strength > 0:
                        time = rep * pattern_duration + i * beat_duration
                        if time < section_def['duration']:
                            rhythm.append({
                                'instrument': 'kick' if i % 4 == 0 else 'snare' if i % 2 == 0 else 'hihat',
                                'time': time,
                                'velocity': beat_strength * section_def['intensity'],
                                'duration': beat_duration * 0.1
                            })
            
            return rhythm
            
        except Exception as e:
            logger.warning(f"Rhythm generation failed: {str(e)}")
            return []

    async def _generate_audio_data(
        self, 
        track: GeneratedTrack, 
        parameters: GenerationParameters
    ) -> np.ndarray:
        """Generate audio waveform from track data"""
        try:
            # Use audio engine for synthesis
            if hasattr(self.audio_engine, 'synthesize_track'):
                return await self.audio_engine.synthesize_track(track, parameters)
            
            else:
                # Fallback synthesis
                return await self._synthesize_track_fallback(track, parameters)
                
        except Exception as e:
            logger.error(f"Audio synthesis failed: {str(e)}")
            # Return silence as fallback
            duration_samples = int(track.total_duration * track.sample_rate)
            return np.zeros(duration_samples, dtype=np.float32)

    async def _generate_midi_data(
        self, 
        track: GeneratedTrack, 
        parameters: GenerationParameters
    ) -> bytes:
        """Generate MIDI data from track"""
        try:
            import mido
            
            # Create MIDI file
            mid = mido.MidiFile()
            track_midi = mido.MidiTrack()
            mid.tracks.append(track_midi)
            
            # Set tempo
            track_midi.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(parameters.tempo)))
            
            # Convert sections to MIDI
            for section in track.sections:
                # Add melody
                for note_data in section.melody:
                    note_on = mido.Message('note_on',
                        note=int(note_data.get('pitch', 60)),
                        velocity=int(note_data.get('velocity', 64)),
                        time=int(note_data.get('start_time', 0) * 480)
                    )
                    note_off = mido.Message('note_off',
                        note=int(note_data.get('pitch', 60)),
                        velocity=0,
                        time=int(note_data.get('duration', 0.5) * 480)
                    )
                    track_midi.append(note_on)
                    track_midi.append(note_off)
                
                # Add harmony
                for chord_data in section.harmony:
                    # Simplified chord to MIDI conversion
                    chord_notes = self._chord_to_midi_notes(chord_data['chord'])
                    for note in chord_notes:
                        note_on = mido.Message('note_on',
                            note=note,
                            velocity=int(chord_data.get('velocity', 64)),
                            time=int(chord_data.get('start_time', 0) * 480)
                        )
                        note_off = mido.Message('note_off',
                            note=note,
                            velocity=0,
                            time=int(chord_data.get('duration', 1.0) * 480)
                        )
                        track_midi.append(note_on)
                        track_midi.append(note_off)
            
            # Convert to bytes
            from io import BytesIO
            output = BytesIO()
            mid.save(file=output)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"MIDI generation failed: {str(e)}")
            return b''

    def _validate_generation_parameters(self, parameters: GenerationParameters):
        """Validate generation parameters"""
        if parameters.duration <= 0 or parameters.duration > 1800:  # Max 30 minutes
            raise MusicGenerationError("Duration must be between 1 and 1800 seconds")
        
        if parameters.tempo < 60 or parameters.tempo > 200:
            raise MusicGenerationError("Tempo must be between 60 and 200 BPM")
        
        if not 0.0 <= parameters.complexity_level <= 1.0:
            raise MusicGenerationError("Complexity level must be between 0.0 and 1.0")
        
        if not parameters.instruments:
            raise MusicGenerationError("At least one instrument must be specified")

    def _load_composition_templates(self):
        """Load composition templates for different styles"""
        self._template_cache = {
            'classical': {
                'structure': ['intro', 'theme_a', 'theme_b', 'development', 'recapitulation', 'coda'],
                'chord_progressions': [
                    ['I', 'IV', 'V', 'I'],
                    ['vi', 'IV', 'I', 'V'],
                    ['ii', 'V', 'I', 'vi']
                ]
            },
            'pop': {
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
                'chord_progressions': [
                    ['I', 'V', 'vi', 'IV'],
                    ['vi', 'IV', 'I', 'V'],
                    ['I', 'vi', 'IV', 'V']
                ]
            },
            'jazz': {
                'structure': ['head', 'improvisation', 'head'],
                'chord_progressions': [
                    ['ii7', 'V7', 'Imaj7', 'vi7'],
                    ['I7', 'VI7', 'ii7', 'V7'],
                    ['iii7', 'VI7', 'ii7', 'V7']
                ]
            },
            'electronic': {
                'structure': ['intro', 'build_up', 'drop', 'breakdown', 'build_up', 'drop', 'outro'],
                'chord_progressions': [
                    ['i', 'VII', 'VI', 'VII'],
                    ['i', 'iv', 'v', 'i'],
                    ['i', 'VI', 'III', 'VII']
                ]
            }
        }

    def _get_structure_template(self, style: MusicStyle, genre: MusicGenre) -> List[str]:
        """Get structure template for style/genre"""
        template_key = style.value.lower()
        
        if template_key in self._template_cache:
            return self._template_cache[template_key]['structure']
        
        # Default structure
        return ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro']

    def _get_section_weight(self, section_type: str) -> float:
        """Get relative weight of section type for duration calculation"""
        weights = {
            'intro': 0.5,
            'verse': 1.0,
            'chorus': 1.2,
            'bridge': 0.8,
            'outro': 0.5,
            'build_up': 0.6,
            'drop': 1.5,
            'breakdown': 0.8,
            'theme_a': 1.0,
            'theme_b': 1.0,
            'development': 1.5,
            'recapitulation': 1.0,
            'coda': 0.3,
            'head': 1.0,
            'improvisation': 2.0
        }
        return weights.get(section_type, 1.0)

    def _calculate_section_intensity(
        self, 
        index: int, 
        total_sections: int, 
        arc: EmotionalArc
    ) -> float:
        """Calculate emotional intensity for section"""
        progress = index / max(total_sections - 1, 1)
        
        if arc == EmotionalArc.BUILDING:
            return 0.3 + 0.7 * progress
        elif arc == EmotionalArc.DECLINING:
            return 1.0 - 0.7 * progress
        elif arc == EmotionalArc.DRAMATIC:
            return 0.3 + 0.7 * abs(0.5 - progress) * 2
        elif arc == EmotionalArc.CYCLICAL:
            return 0.5 + 0.5 * np.sin(progress * 2 * np.pi)
        elif arc == EmotionalArc.EXPLOSIVE:
            return 0.9 if progress > 0.7 else 0.4
        else:  # STABLE
            return 0.6

    def _get_default_structure(self, duration: int) -> List[Dict[str, Any]]:
        """Get default structure if generation fails"""
        sections = ['intro', 'verse', 'chorus', 'outro']
        section_duration = duration / len(sections)
        
        structure = []
        for i, section_type in enumerate(sections):
            structure.append({
                'type': section_type,
                'start_time': i * section_duration,
                'duration': section_duration,
                'intensity': 0.5
            })
        
        return structure

    async def _generate_procedural_melody(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters
    ) -> List[Dict[str, Any]]:
        """Generate melody using procedural algorithms"""
        melody = []
        
        # Simple procedural melody generation
        note_duration = 0.25  # Quarter note
        num_notes = int(section_def['duration'] / note_duration)
        
        # Get scale notes for the key
        scale_notes = self._get_scale_notes(parameters.key)
        
        for i in range(num_notes):
            # Simple random walk melody
            if i == 0:
                note = scale_notes[len(scale_notes) // 2]  # Start in middle
            else:
                # Move by step or small leap
                direction = np.random.choice([-1, 0, 1], p=[0.3, 0.2, 0.5])
                prev_note = melody[-1]['pitch']
                prev_index = scale_notes.index(prev_note) if prev_note in scale_notes else 0
                new_index = max(0, min(len(scale_notes) - 1, prev_index + direction))
                note = scale_notes[new_index]
            
            melody.append({
                'pitch': note,
                'start_time': i * note_duration,
                'duration': note_duration,
                'velocity': int(64 + 32 * section_def['intensity'])
            })
        
        return melody

    def _generate_chord_progression(self, style: MusicStyle, key: MusicKey) -> List[str]:
        """Generate chord progression for style and key"""
        template_key = style.value.lower()
        
        if template_key in self._template_cache:
            progressions = self._template_cache[template_key]['chord_progressions']
            return np.random.choice(progressions) if progressions else ['I', 'V', 'vi', 'IV']
        
        # Default progression
        return ['I', 'V', 'vi', 'IV']

    def _get_rhythm_pattern(self, style: MusicStyle, tempo: int) -> List[float]:
        """Get rhythm pattern for style"""
        patterns = {
            MusicStyle.ROCK: [1.0, 0.0, 0.7, 0.0, 1.0, 0.0, 0.7, 0.0],
            MusicStyle.POP: [1.0, 0.0, 0.8, 0.0, 1.0, 0.0, 0.8, 0.0],
            MusicStyle.ELECTRONIC: [1.0, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5],
            MusicStyle.JAZZ: [1.0, 0.0, 0.6, 0.8, 0.0, 0.6, 0.8, 0.0],
            MusicStyle.CLASSICAL: [1.0, 0.5, 0.7, 0.5, 0.8, 0.5, 0.7, 0.5]
        }
        
        return patterns.get(style, [1.0, 0.0, 0.5, 0.0])

    def _select_section_instruments(
        self, 
        section_def: Dict[str, Any], 
        parameters: GenerationParameters
    ) -> List[InstrumentType]:
        """Select active instruments for section"""
        # Start with base instruments
        active = parameters.instruments.copy()
        
        # Modify based on section type and intensity
        intensity = section_def['intensity']
        section_type = section_def['type']
        
        if section_type in ['intro', 'outro'] and intensity < 0.5:
            # Reduce instrumentation for quiet sections
            if len(active) > 2:
                active = active[:2]
        
        elif section_type in ['chorus', 'drop'] and intensity > 0.7:
            # Add instruments for intense sections
            additional = [InstrumentType.STRINGS, InstrumentType.BRASS, InstrumentType.PERCUSSION]
            for inst in additional:
                if inst not in active and len(active) < 6:
                    active.append(inst)
        
        return active

    def _calculate_section_complexity(self, section: MusicSection) -> float:
        """Calculate complexity score for section"""
        complexity = 0.0
        
        # Melody complexity
        if section.melody:
            note_count = len(section.melody)
            complexity += min(note_count / 20.0, 0.3)
        
        # Harmony complexity
        if section.harmony:
            chord_count = len(section.harmony)
            complexity += min(chord_count / 8.0, 0.3)
        
        # Rhythm complexity
        if section.rhythm:
            rhythm_density = len(section.rhythm) / section.duration
            complexity += min(rhythm_density / 4.0, 0.2)
        
        # Instrumentation complexity
        complexity += len(section.active_instruments) * 0.02
        
        return min(complexity, 1.0)

    def _calculate_section_dynamics(
        self, 
        intensity: float, 
        parameters: GenerationParameters
    ) -> float:
        """Calculate section dynamics level"""
        base_dynamics = 0.5
        intensity_boost = intensity * 0.4
        return min(base_dynamics + intensity_boost, 1.0)

    def _create_empty_section(
        self, 
        section_def: Dict[str, Any], 
        section_index: int
    ) -> MusicSection:
        """Create empty section as fallback"""
        return MusicSection(
            section_id=f"empty_{section_index}",
            section_type=section_def.get('type', 'unknown'),
            start_time=section_def.get('start_time', 0.0),
            end_time=section_def.get('start_time', 0.0) + section_def.get('duration', 4.0),
            duration=section_def.get('duration', 4.0),
            emotional_intensity=section_def.get('intensity', 0.5)
        )

    def _convert_ai_melody(self, ai_melody: Any) -> List[Dict[str, Any]]:
        """Convert AI model output to internal melody format"""
        # This would depend on the AI model output format
        # Placeholder implementation
        melody = []
        
        if hasattr(ai_melody, 'notes'):
            for note in ai_melody.notes:
                melody.append({
                    'pitch': getattr(note, 'pitch', 60),
                    'start_time': getattr(note, 'start_time', 0.0),
                    'duration': getattr(note, 'duration', 0.5),
                    'velocity': getattr(note, 'velocity', 64)
                })
        
        return melody

    def _calculate_chord_velocity(self, intensity: float) -> int:
        """Calculate chord velocity based on intensity"""
        base_velocity = 40
        intensity_boost = int(intensity * 60)
        return min(base_velocity + intensity_boost, 127)

    def _get_scale_notes(self, key: MusicKey) -> List[int]:
        """Get MIDI note numbers for scale"""
        # Simplified major scale starting from C4 (60)
        major_scale = [0, 2, 4, 5, 7, 9, 11]
        
        # Get root note (simplified - assumes C major for now)
        root = 60
        
        # Generate scale across two octaves
        notes = []
        for octave in range(2):
            for interval in major_scale:
                notes.append(root + octave * 12 + interval)
        
        return notes

    def _chord_to_midi_notes(self, chord_name: str) -> List[int]:
        """Convert chord name to MIDI note numbers"""
        # Very simplified chord mapping
        chord_mappings = {
            'I': [60, 64, 67],     # C major
            'ii': [62, 65, 69],    # D minor
            'iii': [64, 67, 71],   # E minor
            'IV': [65, 69, 72],    # F major
            'V': [67, 71, 74],     # G major
            'vi': [69, 72, 76],    # A minor
            'vii': [71, 74, 77],   # B diminished
        }
        
        return chord_mappings.get(chord_name, [60, 64, 67])

    def _identify_structure_type(self, structure: List[Dict[str, Any]]) -> str:
        """Identify overall structure type"""
        section_types = [s['type'] for s in structure]
        
        if 'verse' in section_types and 'chorus' in section_types:
            return "verse-chorus"
        elif 'theme_a' in section_types and 'theme_b' in section_types:
            return "binary"
        elif 'head' in section_types and 'improvisation' in section_types:
            return "jazz-standard"
        elif 'build_up' in section_types and 'drop' in section_types:
            return "electronic-dance"
        else:
            return "through-composed"

    async def _calculate_generation_metrics(
        self, 
        track: GeneratedTrack, 
        parameters: GenerationParameters
    ) -> GeneratedTrack:
        """Calculate quality and other metrics for generated track"""
        # Quality score based on completeness and coherence
        quality_factors = []
        
        # Structure completeness
        if track.sections:
            quality_factors.append(0.9)
        else:
            quality_factors.append(0.1)
        
        # Musical content richness
        total_notes = sum(len(section.melody) for section in track.sections)
        total_chords = sum(len(section.harmony) for section in track.sections)
        
        if total_notes > 0:
            quality_factors.append(0.8)
        if total_chords > 0:
            quality_factors.append(0.8)
        
        # Instrumentation diversity
        all_instruments = set()
        for section in track.sections:
            all_instruments.update(section.active_instruments)
        
        instrument_score = min(len(all_instruments) / 5.0, 1.0)
        quality_factors.append(0.5 + 0.5 * instrument_score)
        
        track.quality_score = np.mean(quality_factors) if quality_factors else 0.5
        
        # Originality score based on complexity and uniqueness
        avg_complexity = np.mean([
            section.complexity_score for section in track.sections
        ]) if track.sections else 0.5
        
        track.originality_score = min(
            avg_complexity * parameters.creativity_level * 1.2, 1.0
        )
        
        # Commercial viability
        track.commercial_viability = self._calculate_commercial_viability(
            track, parameters
        )
        
        return track

    def _calculate_commercial_viability(
        self, 
        track: GeneratedTrack, 
        parameters: GenerationParameters
    ) -> float:
        """Calculate commercial viability score"""
        viability = 0.0
        
        # Duration check
        if 120 <= track.total_duration <= 300:  # 2-5 minutes
            viability += 0.3
        
        # Structure familiarity
        if track.overall_structure in ['verse-chorus', 'binary']:
            viability += 0.2
        
        # Style popularity (simplified)
        popular_styles = [MusicStyle.POP, MusicStyle.ROCK, MusicStyle.ELECTRONIC]
        if parameters.style in popular_styles:
            viability += 0.2
        
        # Tempo appropriateness
        if 100 <= parameters.tempo <= 140:
            viability += 0.15
        
        # Complexity balance
        avg_complexity = np.mean([
            section.complexity_score for section in track.sections
        ]) if track.sections else 0.5
        
        if 0.4 <= avg_complexity <= 0.7:  # Not too simple, not too complex
            viability += 0.15
        
        return min(viability, 1.0)

    async def _analyze_lead_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze existing audio for accompaniment/remix generation"""
        try:
            from ...ai.ml.audio_intelligence import MusicAnalyzer
            
            analyzer = MusicAnalyzer()
            result = await analyzer.analyze_music(audio_path)
            
            return {
                'key': getattr(result, 'key', MusicKey.C_MAJOR),
                'tempo': int(getattr(result, 'tempo', 120)),
                'duration': int(getattr(result, 'duration', 180)),
                'time_signature': getattr(result, 'time_signature', TimeSignature.FOUR_FOUR),
                'genre': getattr(result, 'genre', MusicGenre.POP),
                'energy': getattr(result, 'energy', 0.5),
                'valence': getattr(result, 'valence', 0.5)
            }
            
        except Exception as e:
            logger.warning(f"Audio analysis failed, using defaults: {str(e)}")
            return {
                'key': MusicKey.C_MAJOR,
                'tempo': 120,
                'duration': 180,
                'time_signature': TimeSignature.FOUR_FOUR,
                'genre': MusicGenre.POP,
                'energy': 0.5,
                'valence': 0.5
            }

    def _select_accompaniment_instruments(
        self, 
        style: MusicStyle, 
        lead_analysis: Dict[str, Any]
    ) -> List[InstrumentType]:
        """Select appropriate instruments for accompaniment"""
        instruments = []
        
        # Always include rhythm section
        instruments.extend([InstrumentType.BASS, InstrumentType.DRUMS])
        
        # Add harmonic instruments based on style
        if style in [MusicStyle.POP, MusicStyle.ROCK]:
            instruments.extend([InstrumentType.PIANO, InstrumentType.GUITAR])
        elif style == MusicStyle.JAZZ:
            instruments.extend([InstrumentType.PIANO, InstrumentType.BASS])
        elif style == MusicStyle.CLASSICAL:
            instruments.extend([InstrumentType.STRINGS, InstrumentType.PIANO])
        elif style == MusicStyle.ELECTRONIC:
            instruments.extend([InstrumentType.SYNTHESIZER])
        
        # Add color instruments based on energy
        energy = lead_analysis.get('energy', 0.5)
        if energy > 0.7:
            instruments.append(InstrumentType.BRASS)
        if energy < 0.3:
            instruments.append(InstrumentType.STRINGS)
        
        return list(set(instruments))  # Remove duplicates

    def _select_remix_instruments(self, style: MusicStyle) -> List[InstrumentType]:
        """Select instruments for remix based on style"""
        style_instruments = {
            MusicStyle.ELECTRONIC: [
                InstrumentType.SYNTHESIZER, InstrumentType.DRUMS, 
                InstrumentType.BASS, InstrumentType.PERCUSSION
            ],
            MusicStyle.HIP_HOP: [
                InstrumentType.DRUMS, InstrumentType.BASS,
                InstrumentType.SYNTHESIZER, InstrumentType.VOCALS
            ],
            MusicStyle.ROCK: [
                InstrumentType.GUITAR, InstrumentType.BASS,
                InstrumentType.DRUMS, InstrumentType.VOCALS
            ],
            MusicStyle.JAZZ: [
                InstrumentType.PIANO, InstrumentType.BASS,
                InstrumentType.DRUMS, InstrumentType.BRASS
            ]
        }
        
        return style_instruments.get(style, [
            InstrumentType.PIANO, InstrumentType.BASS, InstrumentType.DRUMS
        ])

    def _calculate_remix_tempo(self, original_tempo: int, remix_style: MusicStyle) -> int:
        """Calculate appropriate tempo for remix"""
        style_tempo_ranges = {
            MusicStyle.ELECTRONIC: (128, 140),
            MusicStyle.HIP_HOP: (80, 100),
            MusicStyle.ROCK: (120, 140),
            MusicStyle.POP: (100, 120),
            MusicStyle.JAZZ: (100, 160)
        }
        
        min_tempo, max_tempo = style_tempo_ranges.get(remix_style, (100, 130))
        
        # Adjust original tempo to fit style range
        if original_tempo < min_tempo:
            return min_tempo
        elif original_tempo > max_tempo:
            return max_tempo
        else:
            return original_tempo

    async def _synthesize_track_fallback(
        self, 
        track: GeneratedTrack, 
        parameters: GenerationParameters
    ) -> np.ndarray:
        """Fallback audio synthesis"""
        # Simple sine wave synthesis as fallback
        sample_rate = track.sample_rate
        duration_samples = int(track.total_duration * sample_rate)
        audio = np.zeros(duration_samples, dtype=np.float32)
        
        for section in track.sections:
            start_sample = int(section.start_time * sample_rate)
            end_sample = int(section.end_time * sample_rate)
            
            # Generate simple tones for melody
            for note in section.melody:
                note_start = start_sample + int(note['start_time'] * sample_rate)
                note_duration = int(note['duration'] * sample_rate)
                note_end = min(note_start + note_duration, end_sample)
                
                if note_start < note_end:
                    # Convert MIDI note to frequency
                    frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
                    
                    # Generate sine wave
                    t = np.linspace(0, note['duration'], note_end - note_start)
                    wave = np.sin(2 * np.pi * frequency * t)
                    
                    # Apply velocity
                    amplitude = note['velocity'] / 127.0 * 0.3
                    wave *= amplitude
                    
                    # Add to audio
                    audio[note_start:note_end] += wave
        
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio

    async def _export_audio(
        self, 
        track: GeneratedTrack, 
        output_path: str, 
        format: str
    ) -> str:
        """Export audio to file"""
        try:
            import soundfile as sf
            
            if track.audio_data is not None:
                sf.write(output_path, track.audio_data, track.sample_rate, format=format.upper())
                track.audio_file_path = output_path
                return output_path
            else:
                raise MusicGenerationError("No audio data to export")
                
        except Exception as e:
            logger.error(f"Audio export failed: {str(e)}")
            raise MusicGenerationError(f"Audio export failed: {str(e)}")

    async def _export_midi(self, track: GeneratedTrack, output_path: str):
        """Export MIDI to file"""
        try:
            if track.midi_data:
                with open(output_path, 'wb') as f:
                    f.write(track.midi_data)
            else:
                raise MusicGenerationError("No MIDI data to export")
                
        except Exception as e:
            logger.error(f"MIDI export failed: {str(e)}")
            raise MusicGenerationError(f"MIDI export failed: {str(e)}")

    async def _export_score(self, track: GeneratedTrack, output_path: str):
        """Export musical score"""
        try:
            # Placeholder for score export
            # Would implement MusicXML export in production
            if track.score_data:
                with open(output_path, 'w') as f:
                    json.dump(track.score_data, f, indent=2)
            else:
                # Generate basic score data
                score = {
                    'title': track.title or 'Generated Track',
                    'sections': [
                        {
                            'type': section.section_type,
                            'start_time': section.start_time,
                            'duration': section.duration
                        }
                        for section in track.sections
                    ]
                }
                with open(output_path, 'w') as f:
                    json.dump(score, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Score export failed: {str(e)}")
            raise MusicGenerationError(f"Score export failed: {str(e)}")

    async def _export_metadata(self, track: GeneratedTrack, output_path: str):
        """Export track metadata"""
        try:
            metadata = {
                'track_id': track.track_id,
                'title': track.title,
                'generation_parameters': {
                    'genre': track.parameters.genre.value if track.parameters else 'unknown',
                    'style': track.parameters.style.value if track.parameters else 'unknown',
                    'tempo': track.parameters.tempo if track.parameters else 120,
                    'duration': track.total_duration,
                    'key': track.parameters.key.name if track.parameters else 'C Major'
                },
                'structure': {
                    'type': track.overall_structure,
                    'sections': [
                        {
                            'type': section.section_type,
                            'start_time': section.start_time,
                            'duration': section.duration,
                            'instruments': [inst.value for inst in section.active_instruments]
                        }
                        for section in track.sections
                    ]
                },
                'metrics': {
                    'quality_score': track.quality_score,
                    'originality_score': track.originality_score,
                    'commercial_viability': track.commercial_viability
                },
                'generation_info': {
                    'timestamp': track.generation_timestamp.isoformat(),
                    'processing_time': track.processing_time,
                    'model_version': track.model_version
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Metadata export failed: {str(e)}")
            raise MusicGenerationError(f"Metadata export failed: {str(e)}")

    def get_cached_generation(self, track_id: str) -> Optional[GeneratedTrack]:
        """Get cached generation result"""
        return self._generation_cache.get(track_id)

    def clear_cache(self):
        """Clear generation cache"""
        self._generation_cache.clear()
        logger.info("Generation cache cleared")

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        cached_tracks = list(self._generation_cache.values())
        
        if not cached_tracks:
            return {'total_tracks': 0}
        
        total_duration = sum(track.total_duration for track in cached_tracks)
        avg_quality = np.mean([track.quality_score for track in cached_tracks])
        avg_processing_time = np.mean([track.processing_time for track in cached_tracks])
        
        style_counts = {}
        for track in cached_tracks:
            if track.parameters:
                style = track.parameters.style.value
                style_counts[style] = style_counts.get(style, 0) + 1
        
        return {
            'total_tracks': len(cached_tracks),
            'total_duration': total_duration,
            'average_quality': avg_quality,
            'average_processing_time': avg_processing_time,
            'style_distribution': style_counts
        }
