"""Composition Analyzer - Advanced Music Composition Analysis Engine
================================================================

Enterprise-grade music composition analysis system providing deep insights
into musical structure, harmony, rhythm, and creative patterns for content creators.

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
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pathlib import Path

from ...ai.ml.music_intelligence import (
    MusicStyleAnalyzer, BeatDetector, HarmonyAnalyzer,
    MusicGenre, MusicKey, TimeSignature, ChordType
)
from ...ai.ml.audio_intelligence import MusicAnalyzer, MusicAnalysisResult
try:
    from core.exceptions import CompositionAnalysisError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    CompositionAnalysisError = globals().get('CompositionAnalysisError', Exception)
from ...core.logging import get_logger
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class CompositionComplexity(Enum):
    """
Musical composition complexity levels"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VIRTUOSIC = "virtuosic"


class StructuralElement(Enum):
    """Musical structural elements"""

    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    PRE_CHORUS = "pre_chorus"
    POST_CHORUS = "post_chorus"
    SOLO = "solo"
    BREAKDOWN = "breakdown"
    BUILD_UP = "build_up"
    OUTRO = "outro"


@dataclass
class HarmonyAnalysis:
    """Comprehensive harmony analysis results"""
    chord_progressions: List[List[str]] = field(default_factory=list)
    key_signatures: List[str] = field(default_factory=list)
    modulations: List[Dict[str, Any]] = field(default_factory=list)
    harmonic_complexity: float = 0.0
    dominant_progressions: List[str] = field(default_factory=list)
    tension_resolution_points: List[float] = field(default_factory=list)
    harmonic_rhythm: Dict[str, float] = field(default_factory=dict)


@dataclass
class RhythmAnalysis:
    """
Advanced rhythm pattern analysis"""
    time_signatures: List[str] = field(default_factory=list)
    rhythmic_patterns: List[Dict[str, Any]] = field(default_factory=list)
    syncopation_levels: List[float] = field(default_factory=list)
    groove_characteristics: Dict[str, float] = field(default_factory=dict)
    polyrhythmic_elements: List[Dict[str, Any]] = field(default_factory=list)
    rhythmic_complexity: float = 0.0


@dataclass
class MelodyAnalysis:
    """
Melodic content analysis"""
    melodic_contours: List[List[float]] = field(default_factory=list)
    phrase_structures: List[Dict[str, Any]] = field(default_factory=list)
    intervallic_patterns: List[str] = field(default_factory=list)
    melodic_range: Dict[str, float] = field(default_factory=dict)
    motivic_development: List[Dict[str, Any]] = field(default_factory=list)
    melodic_complexity: float = 0.0


@dataclass
class StructuralAnalysis:
    """
Musical structure analysis"""
    form_type: str = "unknown"
    sections: List[Dict[str, Any]] = field(default_factory=list)
    section_durations: List[float] = field(default_factory=list)
    repetition_patterns: Dict[str, int] = field(default_factory=dict)
    developmental_techniques: List[str] = field(default_factory=list)
    structural_coherence: float = 0.0


@dataclass
class CompositionAnalysisResult:
    """Complete composition analysis results"""
    composition_id: str
    file_path: Optional[str] = None
    
    # Core analyses
    harmony_analysis: HarmonyAnalysis = field(default_factory=HarmonyAnalysis)
    rhythm_analysis: RhythmAnalysis = field(default_factory=RhythmAnalysis)
    melody_analysis: MelodyAnalysis = field(default_factory=MelodyAnalysis)
    structural_analysis: StructuralAnalysis = field(default_factory=StructuralAnalysis)
    
    # Overall metrics
    overall_complexity: CompositionComplexity = CompositionComplexity.MODERATE
    creativity_score: float = 0.0
    commercial_potential: float = 0.0
    uniqueness_score: float = 0.0
    
    # Professional insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    collaboration_opportunities: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    confidence_score: float = 0.0


class CompositionAnalyzer:
    """
    Advanced composition analysis engine for professional music evaluation.
    
    Provides comprehensive analysis of musical compositions including harmony,
    rhythm, melody, and structure with AI-powered insights and recommendations.
    """
    def __init__(self):
        """
Initialize composition analyzer with ML models"""
        self.music_analyzer = MusicAnalyzer()
        self.style_analyzer = MusicStyleAnalyzer()
        self.beat_detector = BeatDetector()
        self.harmony_analyzer = HarmonyAnalyzer()
        
        # Analysis cache
        self._analysis_cache: Dict[str, CompositionAnalysisResult] = {}
        
        logger.info("Composition Analyzer initialized successfully")

    async def analyze_composition(
        self, 
        audio_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> CompositionAnalysisResult:
        """
        Perform comprehensive composition analysis.
        
        Args:
            audio_path: Path to audio file
            metadata: Optional composition metadata
            
        Returns:
            Complete composition analysis results
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not Path(audio_path).exists():
                raise CompositionAnalysisError(f"Audio file not found: {audio_path}")
            
            composition_id = self._generate_composition_id(audio_path)
            
            # Check cache
            if composition_id in self._analysis_cache:
                logger.info(f"Returning cached analysis for {composition_id}")
                return self._analysis_cache[composition_id]
            
            logger.info(f"Starting composition analysis for: {audio_path}")
            
            # Perform base music analysis
            base_analysis = await self.music_analyzer.analyze_music(audio_path, metadata)
            
            # Initialize result
            result = CompositionAnalysisResult(
                composition_id=composition_id,
                file_path=audio_path
            )
            
            # Parallel analysis execution
            tasks = [
                self._analyze_harmony(audio_path, base_analysis),
                self._analyze_rhythm(audio_path, base_analysis),
                self._analyze_melody(audio_path, base_analysis),
                self._analyze_structure(audio_path, base_analysis)
            ]
            
            harmony_analysis, rhythm_analysis, melody_analysis, structural_analysis = \
                await asyncio.gather(*tasks)
            
            # Assign results
            result.harmony_analysis = harmony_analysis
            result.rhythm_analysis = rhythm_analysis
            result.melody_analysis = melody_analysis
            result.structural_analysis = structural_analysis
            
            # Calculate overall metrics
            result = await self._calculate_overall_metrics(result, base_analysis)
            
            # Generate insights
            result = await self._generate_professional_insights(result, base_analysis)
            
            # Set metadata
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.confidence_score = await self._calculate_confidence_score(result)
            
            # Cache result
            self._analysis_cache[composition_id] = result
            
            logger.info(f"Composition analysis completed: {composition_id}")
            return result
            
        except Exception as e:
            logger.error(f"Composition analysis failed: {str(e)}")
            raise CompositionAnalysisError(f"Analysis failed: {str(e)}")

    async def _analyze_harmony(
        self, 
        audio_path: str, 
        base_analysis: MusicAnalysisResult
    ) -> HarmonyAnalysis:
        """Analyze harmonic content and progressions"""
        try:
            # Use harmony analyzer from ML module
            harmony_result = await self.harmony_analyzer.analyze_harmony(audio_path)
            
            harmony_analysis = HarmonyAnalysis()
            
            # Extract chord progressions
            if hasattr(harmony_result, 'chord_progression'):
                harmony_analysis.chord_progressions = [
                    [chord.chord_name for chord in harmony_result.chord_progression]
                ]
            
            # Key signatures
            if hasattr(harmony_result, 'key'):
                harmony_analysis.key_signatures = [harmony_result.key.name]
            
            # Modulations
            if hasattr(harmony_result, 'modulations'):
                harmony_analysis.modulations = [
                    {
                        'from_key': mod.from_key.name,
                        'to_key': mod.to_key.name,
                        'timestamp': mod.timestamp
                    }
                    for mod in harmony_result.modulations
                ]
            
            # Harmonic complexity
            harmony_analysis.harmonic_complexity = getattr(
                harmony_result, 'harmonic_complexity', 0.5
            )
            
            # Identify dominant progressions
            harmony_analysis.dominant_progressions = self._identify_dominant_progressions(
                harmony_analysis.chord_progressions
            )
            
            # Tension and resolution analysis
            harmony_analysis.tension_resolution_points = \
                await self._analyze_tension_resolution(harmony_result)
            
            return harmony_analysis
            
        except Exception as e:
            logger.warning(f"Harmony analysis failed: {str(e)}")
            return HarmonyAnalysis()

    async def _analyze_rhythm(
        self, 
        audio_path: str, 
        base_analysis: MusicAnalysisResult
    ) -> RhythmAnalysis:
        """Analyze rhythmic patterns and characteristics"""
        try:
            # Use beat detector from ML module
            beat_result = await self.beat_detector.analyze_beat(audio_path)
            
            rhythm_analysis = RhythmAnalysis()
            
            # Time signatures
            if hasattr(beat_result, 'time_signature'):
                rhythm_analysis.time_signatures = [beat_result.time_signature.name]
            
            # Rhythmic patterns
            if hasattr(beat_result, 'beat_pattern'):
                rhythm_analysis.rhythmic_patterns = [
                    {
                        'pattern': beat_result.beat_pattern,
                        'strength': beat_result.beat_strength,
                        'regularity': beat_result.regularity_score
                    }
                ]
            
            # Syncopation levels
            rhythm_analysis.syncopation_levels = getattr(
                beat_result, 'syncopation_levels', [0.0]
            )
            
            # Groove characteristics
            rhythm_analysis.groove_characteristics = {
                'swing_factor': getattr(beat_result, 'swing_factor', 0.0),
                'rhythmic_density': getattr(beat_result, 'rhythmic_density', 0.5),
                'pulse_clarity': getattr(beat_result, 'pulse_clarity', 0.5)
            }
            
            # Calculate rhythmic complexity
            rhythm_analysis.rhythmic_complexity = self._calculate_rhythmic_complexity(
                rhythm_analysis
            )
            
            return rhythm_analysis
            
        except Exception as e:
            logger.warning(f"Rhythm analysis failed: {str(e)}")
            return RhythmAnalysis()

    async def _analyze_melody(
        self, 
        audio_path: str, 
        base_analysis: MusicAnalysisResult
    ) -> MelodyAnalysis:
        """Analyze melodic content and patterns"""
        try:
            melody_analysis = MelodyAnalysis()
            
            # Extract melodic contours using pitch tracking
            contours = await self._extract_melodic_contours(audio_path)
            melody_analysis.melodic_contours = contours
            
            # Phrase structure analysis
            melody_analysis.phrase_structures = await self._analyze_phrase_structures(contours)
            
            # Intervallic patterns
            melody_analysis.intervallic_patterns = self._analyze_intervallic_patterns(contours)
            
            # Melodic range
            if contours:
                flat_contour = [note for contour in contours for note in contour if note > 0]
                if flat_contour:
                    melody_analysis.melodic_range = {
                        'lowest': min(flat_contour),
                        'highest': max(flat_contour),
                        'range': max(flat_contour) - min(flat_contour)
                    }
            
            # Motivic development
            melody_analysis.motivic_development = await self._analyze_motivic_development(
                contours
            )
            
            # Calculate melodic complexity
            melody_analysis.melodic_complexity = self._calculate_melodic_complexity(
                melody_analysis
            )
            
            return melody_analysis
            
        except Exception as e:
            logger.warning(f"Melody analysis failed: {str(e)}")
            return MelodyAnalysis()

    async def _analyze_structure(
        self, 
        audio_path: str, 
        base_analysis: MusicAnalysisResult
    ) -> StructuralAnalysis:
        """Analyze musical structure and form"""
        try:
            structural_analysis = StructuralAnalysis()
            
            # Segment the audio into sections
            sections = await self._segment_audio_structure(audio_path)
            structural_analysis.sections = sections
            
            # Calculate section durations
            structural_analysis.section_durations = [
                section.get('duration', 0.0) for section in sections
            ]
            
            # Identify form type
            structural_analysis.form_type = self._identify_form_type(sections)
            
            # Repetition patterns
            structural_analysis.repetition_patterns = self._analyze_repetition_patterns(
                sections
            )
            
            # Developmental techniques
            structural_analysis.developmental_techniques = \
                self._identify_developmental_techniques(sections)
            
            # Structural coherence
            structural_analysis.structural_coherence = self._calculate_structural_coherence(
                sections
            )
            
            return structural_analysis
            
        except Exception as e:
            logger.warning(f"Structure analysis failed: {str(e)}")
            return StructuralAnalysis()

    async def _calculate_overall_metrics(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> CompositionAnalysisResult:
        """Calculate overall composition metrics"""
        try:
            # Overall complexity
            complexity_scores = [
                result.harmony_analysis.harmonic_complexity,
                result.rhythm_analysis.rhythmic_complexity,
                result.melody_analysis.melodic_complexity
            ]
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            
            if avg_complexity >= 0.8:
                result.overall_complexity = CompositionComplexity.VIRTUOSIC
            elif avg_complexity >= 0.6:
                result.overall_complexity = CompositionComplexity.COMPLEX
            elif avg_complexity >= 0.4:
                result.overall_complexity = CompositionComplexity.MODERATE
            else:
                result.overall_complexity = CompositionComplexity.SIMPLE
            
            # Creativity score
            result.creativity_score = self._calculate_creativity_score(result, base_analysis)
            
            # Commercial potential
            result.commercial_potential = self._calculate_commercial_potential(
                result, base_analysis
            )
            
            # Uniqueness score
            result.uniqueness_score = self._calculate_uniqueness_score(result)
            
            return result
            
        except Exception as e:
            logger.warning(f"Overall metrics calculation failed: {str(e)}")
            return result

    async def _generate_professional_insights(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> CompositionAnalysisResult:
        """Generate professional insights and recommendations"""
        try:
            # Analyze strengths
            result.strengths = self._identify_composition_strengths(result, base_analysis)
            
            # Identify weaknesses
            result.weaknesses = self._identify_composition_weaknesses(result, base_analysis)
            
            # Improvement suggestions
            result.improvement_suggestions = self._generate_improvement_suggestions(
                result, base_analysis
            )
            
            # Collaboration opportunities
            result.collaboration_opportunities = self._suggest_collaboration_opportunities(
                result, base_analysis
            )
            
            return result
            
        except Exception as e:
            logger.warning(f"Professional insights generation failed: {str(e)}")
            return result

    def _generate_composition_id(self, audio_path: str) -> str:
        """Generate unique composition ID"""
        import hashlib
        
        path_hash = hashlib.md5(audio_path.encode()).hexdigest()
        timestamp = int(datetime.now().timestamp())
        return f"comp_{path_hash[:8]}_{timestamp}"

    def _identify_dominant_progressions(
        self, 
        chord_progressions: List[List[str]]
    ) -> List[str]:
        """Identify dominant chord progressions"""
        common_progressions = {
            ('I', 'V', 'vi', 'IV'): "vi-V-vi-IV (Pop progression)",
            ('vi', 'IV', 'I', 'V'): "vi-IV-I-V (Axis progression)",
            ('I', 'IV', 'V', 'I'): "I-IV-V-I (Classical cadence)",
            ('ii', 'V', 'I'): "ii-V-I (Jazz turnaround)",
            ('I', 'vi', 'ii', 'V'): "I-vi-ii-V (Circle of fifths)"
        }
        
        dominant = []
        for progression in chord_progressions:
            for pattern, name in common_progressions.items():
                if len(progression) >= len(pattern):
                    for i in range(len(progression) - len(pattern) + 1):
                        if tuple(progression[i:i+len(pattern)]) == pattern:
                            dominant.append(name)
                            break
        
        return list(set(dominant))

    async def _analyze_tension_resolution(
        self, 
        harmony_result: Any
    ) -> List[float]:
        """Analyze tension and resolution points"""
        # Simplified tension analysis based on chord stability
        tension_points = []
        
        try:
            if hasattr(harmony_result, 'chord_progression'):
                for i, chord in enumerate(harmony_result.chord_progression):
                    # Calculate tension based on chord type and position
                    tension = 0.0
                    
                    # Dominant chords create tension
                    if 'dom' in chord.chord_name.lower() or '7' in chord.chord_name:
                        tension += 0.8
                    
                    # Diminished chords create high tension
                    if 'dim' in chord.chord_name.lower():
                        tension += 0.9
                    
                    # Minor chords moderate tension
                    if 'm' in chord.chord_name and 'maj' not in chord.chord_name:
                        tension += 0.3
                    
                    tension_points.append(min(tension, 1.0))
        
        except Exception as e:
            logger.warning(f"Tension analysis failed: {str(e)}")
        
        return tension_points

    def _calculate_rhythmic_complexity(self, rhythm_analysis: RhythmAnalysis) -> float:
        """Calculate overall rhythmic complexity score"""
        complexity = 0.0
        
        # Syncopation contribution
        if rhythm_analysis.syncopation_levels:
            complexity += np.mean(rhythm_analysis.syncopation_levels) * 0.4
        
        # Polyrhythmic elements
        if rhythm_analysis.polyrhythmic_elements:
            complexity += len(rhythm_analysis.polyrhythmic_elements) * 0.1
        
        # Groove characteristics
        if rhythm_analysis.groove_characteristics:
            groove = rhythm_analysis.groove_characteristics
            complexity += groove.get('rhythmic_density', 0.0) * 0.3
            complexity += (1 - groove.get('pulse_clarity', 1.0)) * 0.2
        
        return min(complexity, 1.0)

    async def _extract_melodic_contours(self, audio_path: str) -> List[List[float]]:
        """
Extract melodic contours using pitch tracking"""
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Extract fundamental frequency
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
            
            # Convert to melodic contour
            contour = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    contour.append(librosa.hz_to_midi(pitch))
                else:
                    contour.append(0.0)
            
            # Segment into phrases (simplified)
            phrases = []
            current_phrase = []
            
            for pitch in contour:
                if pitch > 0:
                    current_phrase.append(pitch)
                else:
                    if current_phrase:
                        phrases.append(current_phrase)
                        current_phrase = []
            
            if current_phrase:
                phrases.append(current_phrase)
            
            return phrases
            
        except Exception as e:
            logger.warning(f"Melodic contour extraction failed: {str(e)}")
            return []

    async def _analyze_phrase_structures(
        self, 
        contours: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """Analyze phrase structures from melodic contours"""
        phrase_structures = []
        
        for i, contour in enumerate(contours):
            if len(contour) < 3:
                continue
                
            structure = {
                'phrase_id': i,
                'length': len(contour),
                'direction': self._analyze_melodic_direction(contour),
                'arc_type': self._identify_melodic_arc(contour),
                'peak_position': self._find_melodic_peak_position(contour)
            }
            
            phrase_structures.append(structure)
        
        return phrase_structures

    def _analyze_intervallic_patterns(self, contours: List[List[float]]) -> List[str]:
        """
Analyze intervallic patterns in melodies"""
        patterns = []
        
        for contour in contours:
            if len(contour) < 2:
                continue
                
            intervals = []
            for i in range(len(contour) - 1):
                interval = abs(contour[i+1] - contour[i])
                if interval <= 2:
                    intervals.append('step')
                elif interval <= 4:
                    intervals.append('skip')
                else:
                    intervals.append('leap')
            
            # Identify common patterns
            if intervals.count('step') > len(intervals) * 0.7:
                patterns.append('stepwise_motion')
            elif intervals.count('leap') > len(intervals) * 0.3:
                patterns.append('leaping_melody')
            else:
                patterns.append('mixed_motion')
        
        return list(set(patterns))

    async def _analyze_motivic_development(
        self, 
        contours: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """
Analyze motivic development and variation techniques"""
        developments = []
        
        if len(contours) < 2:
            return developments
        
        # Compare phrases for motivic relationships
        for i in range(len(contours)):
            for j in range(i + 1, len(contours)):
                similarity = self._calculate_phrase_similarity(contours[i], contours[j])
                
                if similarity > 0.7:
                    developments.append({
                        'type': 'repetition',
                        'phrases': [i, j],
                        'similarity': similarity
                    })
                elif similarity > 0.4:
                    developments.append({
                        'type': 'variation',
                        'phrases': [i, j],
                        'similarity': similarity
                    })
        
        return developments

    def _calculate_melodic_complexity(self, melody_analysis: MelodyAnalysis) -> float:
        """
Calculate melodic complexity score"""
        complexity = 0.0
        
        # Range contribution
        if melody_analysis.melodic_range:
            range_size = melody_analysis.melodic_range.get('range', 0)
            complexity += min(range_size / 24.0, 0.3)  # Normalize to 2 octaves max
        
        # Intervallic diversity
        if melody_analysis.intervallic_patterns:
            pattern_diversity = len(set(melody_analysis.intervallic_patterns))
            complexity += pattern_diversity * 0.1
        
        # Motivic development
        if melody_analysis.motivic_development:
            development_count = len(melody_analysis.motivic_development)
            complexity += min(development_count * 0.05, 0.3)
        
        # Phrase structure complexity
        if melody_analysis.phrase_structures:
            avg_phrase_length = np.mean([
                phrase.get('length', 0) for phrase in melody_analysis.phrase_structures
            ])
            complexity += min(avg_phrase_length / 20.0, 0.2)
        
        return min(complexity, 1.0)

    async def _segment_audio_structure(self, audio_path: str) -> List[Dict[str, Any]]:
        """
Segment audio into structural sections"""
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Compute chromagram for harmonic analysis
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Compute tempogram for rhythmic analysis
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Simple segmentation based on harmonic change
            # This is a simplified approach - real implementation would be more sophisticated
            segment_boundaries = librosa.segment.agglomerative(chroma, k=8)
            
            sections = []
            for i, boundary in enumerate(segment_boundaries):
                start_time = boundary
                end_time = segment_boundaries[i+1] if i+1 < len(segment_boundaries) else len(y)/sr
                
                sections.append({
                    'section_id': i,
                    'type': self._classify_section_type(i, len(segment_boundaries)),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time
                })
            
            return sections
            
        except Exception as e:
            logger.warning(f"Audio structure segmentation failed: {str(e)}")
            return []

    def _classify_section_type(self, section_index: int, total_sections: int) -> str:
        """Classify section type based on position"""
        if section_index == 0:
            return StructuralElement.INTRO.value
        elif section_index == total_sections - 1:
            return StructuralElement.OUTRO.value
        elif section_index % 2 == 1:
            return StructuralElement.VERSE.value
        else:
            return StructuralElement.CHORUS.value

    def _identify_form_type(self, sections: List[Dict[str, Any]]) -> str:
        """
Identify musical form type"""
        if not sections:
            return "unknown"
        
        section_types = [section.get('type', '') for section in sections]
        
        # Simple form identification
        if len(sections) <= 3:
            return "simple_binary"
        elif 'verse' in section_types and 'chorus' in section_types:
            return "verse_chorus"
        elif section_types.count('verse') >= 2:
            return "verse_form"
        else:
            return "through_composed"

    def _analyze_repetition_patterns(self, sections: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze repetition patterns in structure"""
        patterns = {}
        
        section_types = [section.get('type', '') for section in sections]
        
        for section_type in set(section_types):
            patterns[section_type] = section_types.count(section_type)
        
        return patterns

    def _identify_developmental_techniques(self, sections: List[Dict[str, Any]]) -> List[str]:
        """
Identify developmental techniques used"""
        techniques = []
        
        if not sections:
            return techniques
        
        section_types = [section.get('type', '') for section in sections]
        
        # Check for common techniques
        if len(set(section_types)) > len(section_types) * 0.5:
            techniques.append("through_composition")
        
        if any(section_types.count(t) > 1 for t in set(section_types)):
            techniques.append("repetition")
        
        if 'bridge' in section_types:
            techniques.append("contrasting_middle")
        
        if len(sections) > 6:
            techniques.append("extended_form")
        
        return techniques

    def _calculate_structural_coherence(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate structural coherence score"""
        if not sections:
            return 0.0
        
        coherence = 0.0
        
        # Duration balance
        durations = [section.get('duration', 0) for section in sections]
        if durations:
            duration_variance = np.var(durations)
            duration_mean = np.mean(durations)
            if duration_mean > 0:
                coherence += max(0, 1 - (duration_variance / duration_mean)) * 0.5
        
        # Structural logic
        section_types = [section.get('type', '') for section in sections]
        
        # Check for logical intro/outro
        if section_types[0] in ['intro', 'verse'] and section_types[-1] in ['outro', 'chorus']:
            coherence += 0.3
        
        # Check for balanced repetition
        unique_sections = len(set(section_types))
        total_sections = len(section_types)
        
        if total_sections > 0:
            balance_score = min(unique_sections / total_sections * 2, 1.0)
            coherence += balance_score * 0.2
        
        return min(coherence, 1.0)

    def _calculate_creativity_score(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> float:
        """
Calculate creativity score based on various factors"""
        creativity = 0.0
        
        # Harmonic creativity
        if result.harmony_analysis.modulations:
            creativity += len(result.harmony_analysis.modulations) * 0.1
        
        # Rhythmic innovation
        if result.rhythm_analysis.polyrhythmic_elements:
            creativity += len(result.rhythm_analysis.polyrhythmic_elements) * 0.05
        
        # Structural innovation
        if result.structural_analysis.developmental_techniques:
            creativity += len(result.structural_analysis.developmental_techniques) * 0.1
        
        # Melodic sophistication
        if result.melody_analysis.motivic_development:
            creativity += len(result.melody_analysis.motivic_development) * 0.05
        
        # Overall complexity bonus
        if result.overall_complexity in [CompositionComplexity.COMPLEX, CompositionComplexity.VIRTUOSIC]:
            creativity += 0.2
        
        return min(creativity, 1.0)

    def _calculate_commercial_potential(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> float:
        """
Calculate commercial potential score"""
        commercial = 0.0
        
        # Structural familiarity
        if result.structural_analysis.form_type in ['verse_chorus', 'verse_form']:
            commercial += 0.3
        
        # Appropriate complexity
        if result.overall_complexity in [CompositionComplexity.MODERATE, CompositionComplexity.COMPLEX]:
            commercial += 0.2
        
        # Harmonic accessibility
        if result.harmony_analysis.dominant_progressions:
            familiar_progressions = [p for p in result.harmony_analysis.dominant_progressions 
                                   if 'Pop' in p or 'vi-V' in p]
            if familiar_progressions:
                commercial += 0.2
        
        # Rhythmic engagement
        if result.rhythm_analysis.groove_characteristics:
            groove = result.rhythm_analysis.groove_characteristics
            if groove.get('rhythmic_density', 0) > 0.4:
                commercial += 0.15
        
        # Melodic memorability
        if result.melody_analysis.phrase_structures:
            avg_phrase_length = np.mean([
                phrase.get('length', 0) for phrase in result.melody_analysis.phrase_structures
            ])
            if 4 <= avg_phrase_length <= 8:  # Optimal for memorability
                commercial += 0.15
        
        return min(commercial, 1.0)

    def _calculate_uniqueness_score(self, result: CompositionAnalysisResult) -> float:
        """
Calculate uniqueness score"""
        uniqueness = 0.0
        
        # Harmonic uniqueness
        if result.harmony_analysis.harmonic_complexity > 0.7:
            uniqueness += 0.25
        
        # Rhythmic uniqueness
        if result.rhythm_analysis.rhythmic_complexity > 0.6:
            uniqueness += 0.25
        
        # Structural uniqueness
        uncommon_forms = ['through_composed', 'extended_form']
        if result.structural_analysis.form_type in uncommon_forms:
            uniqueness += 0.25
        
        # Melodic uniqueness
        if result.melody_analysis.melodic_complexity > 0.6:
            uniqueness += 0.25
        
        return min(uniqueness, 1.0)

    def _identify_composition_strengths(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> List[str]:
        """
Identify composition strengths"""
        strengths = []
        
        # Harmonic strengths
        if result.harmony_analysis.harmonic_complexity > 0.7:
            strengths.append("Sophisticated harmonic language")
        
        if result.harmony_analysis.modulations:
            strengths.append("Effective use of modulation")
        
        # Rhythmic strengths
        if result.rhythm_analysis.rhythmic_complexity > 0.6:
            strengths.append("Complex and engaging rhythmic patterns")
        
        if result.rhythm_analysis.groove_characteristics.get('pulse_clarity', 0) > 0.8:
            strengths.append("Strong rhythmic foundation")
        
        # Melodic strengths
        if result.melody_analysis.melodic_complexity > 0.6:
            strengths.append("Sophisticated melodic development")
        
        if result.melody_analysis.motivic_development:
            strengths.append("Effective motivic development")
        
        # Structural strengths
        if result.structural_analysis.structural_coherence > 0.7:
            strengths.append("Well-organized musical structure")
        
        # Overall strengths
        if result.creativity_score > 0.7:
            strengths.append("High creative originality")
        
        if result.commercial_potential > 0.7:
            strengths.append("Strong commercial appeal")
        
        return strengths

    def _identify_composition_weaknesses(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> List[str]:
        """Identify composition weaknesses"""
        weaknesses = []
        
        # Harmonic weaknesses
        if result.harmony_analysis.harmonic_complexity < 0.3:
            weaknesses.append("Limited harmonic vocabulary")
        
        # Rhythmic weaknesses
        if result.rhythm_analysis.rhythmic_complexity < 0.3:
            weaknesses.append("Predictable rhythmic patterns")
        
        if result.rhythm_analysis.groove_characteristics.get('pulse_clarity', 0) < 0.4:
            weaknesses.append("Weak rhythmic foundation")
        
        # Melodic weaknesses
        if result.melody_analysis.melodic_complexity < 0.3:
            weaknesses.append("Simple melodic content")
        
        if not result.melody_analysis.motivic_development:
            weaknesses.append("Lack of melodic development")
        
        # Structural weaknesses
        if result.structural_analysis.structural_coherence < 0.5:
            weaknesses.append("Unclear musical structure")
        
        if len(result.structural_analysis.sections) < 3:
            weaknesses.append("Overly simple form")
        
        # Overall weaknesses
        if result.creativity_score < 0.4:
            weaknesses.append("Limited creative innovation")
        
        if result.commercial_potential < 0.4:
            weaknesses.append("Limited commercial appeal")
        
        return weaknesses

    def _generate_improvement_suggestions(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Harmonic improvements
        if result.harmony_analysis.harmonic_complexity < 0.5:
            suggestions.append("Consider adding secondary dominants or extended chords")
            suggestions.append("Experiment with chord substitutions and voice leading")
        
        # Rhythmic improvements
        if result.rhythm_analysis.rhythmic_complexity < 0.5:
            suggestions.append("Add syncopation and rhythmic variation")
            suggestions.append("Experiment with polyrhythmic elements")
        
        # Melodic improvements
        if result.melody_analysis.melodic_complexity < 0.5:
            suggestions.append("Develop melodic motifs through variation techniques")
            suggestions.append("Expand melodic range and intervallic variety")
        
        # Structural improvements
        if result.structural_analysis.structural_coherence < 0.6:
            suggestions.append("Clarify section boundaries and transitions")
            suggestions.append("Balance section lengths for better flow")
        
        # Commercial improvements
        if result.commercial_potential < 0.6:
            suggestions.append("Consider more accessible harmonic progressions")
            suggestions.append("Strengthen melodic hooks and memorable phrases")
        
        # Creative improvements
        if result.creativity_score < 0.6:
            suggestions.append("Explore unconventional structural approaches")
            suggestions.append("Experiment with unique timbral combinations")
        
        return suggestions

    def _suggest_collaboration_opportunities(
        self, 
        result: CompositionAnalysisResult, 
        base_analysis: MusicAnalysisResult
    ) -> List[str]:
        """Suggest collaboration opportunities based on analysis"""
        opportunities = []
        
        # Based on strengths and weaknesses
        if "Limited harmonic vocabulary" in result.weaknesses:
            opportunities.append("Collaborate with a jazz harmonicist or composer")
        
        if "Weak rhythmic foundation" in result.weaknesses:
            opportunities.append("Work with a percussionist or rhythm programmer")
        
        if "Limited melodic content" in result.weaknesses:
            opportunities.append("Partner with a melodic specialist or vocalist")
        
        # Based on genre and style
        if hasattr(base_analysis, 'genre'):
            genre = base_analysis.genre.value if hasattr(base_analysis.genre, 'value') else str(base_analysis.genre)
            
            if 'electronic' in genre.lower():
                opportunities.append("Collaborate with sound designers for unique textures")
            elif 'jazz' in genre.lower():
                opportunities.append("Partner with improvisational musicians")
            elif 'classical' in genre.lower():
                opportunities.append("Work with orchestrators or chamber musicians")
        
        # Based on commercial potential
        if result.commercial_potential > 0.7:
            opportunities.append("Consider working with music producers for commercial release")
            opportunities.append("Partner with lyricists for vocal versions")
        
        return opportunities

    def _analyze_melodic_direction(self, contour: List[float]) -> str:
        """Analyze overall melodic direction"""
        if len(contour) < 3:
            return "static"
        
        start_avg = np.mean(contour[:len(contour)//3])
        end_avg = np.mean(contour[-len(contour)//3:])
        
        if end_avg > start_avg + 2:
            return "ascending"
        elif end_avg < start_avg - 2:
            return "descending"
        else:
            return "stable"

    def _identify_melodic_arc(self, contour: List[float]) -> str:
        """Identify melodic arc type"""
        if len(contour) < 5:
            return "simple"
        
        peak_pos = contour.index(max(contour)) / len(contour)
        
        if peak_pos < 0.3:
            return "front_loaded"
        elif peak_pos > 0.7:
            return "back_loaded"
        else:
            return "balanced"

    def _find_melodic_peak_position(self, contour: List[float]) -> float:
        """Find relative position of melodic peak"""
        if not contour:
            return 0.0
        
        peak_index = contour.index(max(contour))
        return peak_index / len(contour)

    def _calculate_phrase_similarity(self, phrase1: List[float], phrase2: List[float]) -> float:
        """
Calculate similarity between two melodic phrases"""
        if not phrase1 or not phrase2:
            return 0.0
        
        # Simple correlation-based similarity
        try:
            # Normalize lengths
            min_len = min(len(phrase1), len(phrase2))
            p1 = phrase1[:min_len]
            p2 = phrase2[:min_len]
            
            # Calculate correlation
            correlation = np.corrcoef(p1, p2)[0, 1]
            return abs(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception:
            return 0.0

    async def _calculate_confidence_score(self, result: CompositionAnalysisResult) -> float:
        """
Calculate overall confidence in the analysis"""
        confidence_factors = []
        
        # Data quality factors
        if result.harmony_analysis.chord_progressions:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.3)
        
        if result.rhythm_analysis.rhythmic_patterns:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)
        
        if result.melody_analysis.melodic_contours:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)
        
        if result.structural_analysis.sections:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.3)
        
        # Processing factors
        if result.processing_time < 30.0:  # Fast processing usually means good data
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        return np.mean(confidence_factors) if confidence_factors else 0.5

    def get_analysis_summary(self, result: CompositionAnalysisResult) -> Dict[str, Any]:
        """
Get a concise summary of the analysis"""
        return {
            'composition_id': result.composition_id,
            'overall_complexity': result.overall_complexity.value,
            'scores': {
                'creativity': result.creativity_score,
                'commercial_potential': result.commercial_potential,
                'uniqueness': result.uniqueness_score,
                'confidence': result.confidence_score
            },
            'structure': {
                'form_type': result.structural_analysis.form_type,
                'section_count': len(result.structural_analysis.sections),
                'coherence': result.structural_analysis.structural_coherence
            },
            'key_insights': {
                'strengths': result.strengths[:3],  # Top 3 strengths
                'improvements': result.improvement_suggestions[:3],  # Top 3 suggestions
                'collaboration_opportunities': result.collaboration_opportunities[:2]
            }
        }

    async def batch_analyze_compositions(
        self, 
        audio_paths: List[str], 
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[CompositionAnalysisResult]:
        """
Analyze multiple compositions in batch"""
        if metadata_list is None:
            metadata_list = [None] * len(audio_paths)
        
        tasks = [
            self.analyze_composition(path, metadata) 
            for path, metadata in zip(audio_paths, metadata_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        successful_results = [
            result for result in results 
            if isinstance(result, CompositionAnalysisResult)
        ]
        
        logger.info(f"Batch analysis completed: {len(successful_results)}/{len(audio_paths)} successful")
        
        return successful_results

    def clear_cache(self):
        """Clear the analysis cache"""
        self._analysis_cache.clear()
        logger.info("Analysis cache cleared")
