"""
RhythmGenerator - Advanced Rhythm Pattern Generation Engine
==========================================================

Professional AI system for creating sophisticated rhythm patterns, percussion maps,
and groove templates with adaptive complexity and synchronization optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
Contact: mlaiel@live.de for licensing, partnerships, and OEM opportunities.
"""

import asyncio
import logging
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import json

logger = logging.getLogger(__name__)

class RhythmComplexity(Enum):
    """Rhythm complexity levels"""
    MINIMAL = "minimal"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    POLYRHYTHMIC = "polyrhythmic"

class SynchrPatterns(Enum):
    """Synchronization pattern types"""
    LOCKED = "locked"
    TIGHT = "tight"
    LOOSE = "loose"
    POLYRHYTHMIC = "polyrhythmic"
    IRREGULAR = "irregular"

@dataclass
class RhythmPattern:
    """Generated rhythm pattern"""
    pattern_id: str
    name: str
    time_signature: str = "4/4"
    resolution: int = 16  # 16th note resolution
    pattern: List[float] = field(default_factory=list)  # Velocity values 0.0-1.0
    complexity: RhythmComplexity = RhythmComplexity.MODERATE
    swing_factor: float = 0.0
    accents: List[int] = field(default_factory=list)
    fills: List[Dict[str, Any]] = field(default_factory=list)
    style_tags: List[str] = field(default_factory=list)

@dataclass
class PercussionMap:
    """Percussion instrument mapping and patterns"""
    map_id: str
    instruments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    layering_rules: Dict[str, List[str]] = field(default_factory=dict)
    velocity_curves: Dict[str, List[float]] = field(default_factory=dict)
    interaction_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class GrooveTemplate:
    """Complete groove template with multiple patterns"""
    template_id: str
    name: str
    tempo_range: Tuple[int, int] = (120, 130)
    main_pattern: RhythmPattern = None
    variation_patterns: List[RhythmPattern] = field(default_factory=list)
    percussion_map: PercussionMap = None
    arrangement_suggestions: List[str] = field(default_factory=list)
    genre_associations: List[str] = field(default_factory=list)

class RhythmGenerator:
    """
    Advanced Rhythm Pattern Generation Engine
    
    Professional AI system for creating sophisticated rhythm patterns with
    adaptive complexity, groove optimization, and multi-layer synchronization.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuration
        self.default_resolution = config.get("default_resolution", 16)
        self.complexity_level = config.get("complexity_level", "moderate")
        self.enable_polyrhythm = config.get("enable_polyrhythm", True)
        self.swing_detection = config.get("swing_detection", True)
        
        # Pattern databases
        self.groove_database = self._load_groove_database()
        self.percussion_library = self._load_percussion_library()
        self.style_templates = self._load_style_templates()
        
        # Generation algorithms
        self.generators = {
            "euclidean": "Euclidean_Rhythm_Algorithm",
            "markov_chain": "Markov_Pattern_Generation",
            "neural_network": "LSTM_Rhythm_Model",
            "genetic": "Genetic_Algorithm_Evolution"
        }
        
        # Performance metrics
        self.performance_metrics = {
            "patterns_generated": 0,
            "complexity_distribution": {},
            "style_preferences": {},
            "user_adoption_rate": 0.0
        }

    def _load_groove_database(self) -> Dict[str, Any]:
        """Load comprehensive groove pattern database"""
        return {
            "house": {
                "main_pattern": [1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0],
                "hi_hat_pattern": [0.0, 0.6, 0.0, 0.6, 0.0, 0.6, 0.0, 0.6, 0.0, 0.6, 0.0, 0.6, 0.0, 0.6, 0.0, 0.6],
                "characteristics": ["four_on_floor", "consistent_hi_hats", "minimal_snare"],
                "tempo_range": [120, 130]
            },
            "trap": {
                "main_pattern": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0],
                "hi_hat_pattern": [0.4, 0.6, 0.8, 0.4, 0.6, 0.8, 0.4, 0.6, 0.4, 0.6, 0.8, 0.4, 0.6, 0.8, 0.4, 0.6],
                "characteristics": ["syncopated_snare", "rolling_hi_hats", "sparse_kick"],
                "tempo_range": [130, 170]
            },
            "breakbeat": {
                "main_pattern": [1.0, 0.0, 0.0, 0.4, 0.8, 0.0, 0.6, 0.0, 0.0, 0.0, 0.4, 0.0, 0.8, 0.0, 0.0, 0.0],
                "characteristics": ["amen_break_style", "complex_snare", "funky_rhythm"],
                "tempo_range": [160, 180]
            },
            "latin": {
                "main_pattern": [1.0, 0.0, 0.6, 0.0, 0.8, 0.0, 0.4, 0.6, 1.0, 0.0, 0.6, 0.0, 0.8, 0.0, 0.4, 0.6],
                "characteristics": ["clave_rhythm", "syncopated_accents", "polyrhythmic"],
                "tempo_range": [100, 140]
            }
        }

    def _load_percussion_library(self) -> Dict[str, Any]:
        """Load percussion instrument library"""
        return {
            "kick": {
                "frequency_range": [20, 100],
                "velocity_curve": "exponential",
                "interaction_groups": ["low_end"],
                "common_patterns": ["four_on_floor", "syncopated", "sparse"]
            },
            "snare": {
                "frequency_range": [150, 300],
                "velocity_curve": "linear",
                "interaction_groups": ["mid_range", "accents"],
                "common_patterns": ["backbeat", "syncopated", "rolls"]
            },
            "hi_hat": {
                "frequency_range": [8000, 16000],
                "velocity_curve": "logarithmic",
                "interaction_groups": ["high_end", "texture"],
                "common_patterns": ["eighth_notes", "sixteenths", "off_beat"]
            },
            "crash": {
                "frequency_range": [3000, 16000],
                "velocity_curve": "exponential",
                "interaction_groups": ["accents", "transitions"],
                "common_patterns": ["downbeats", "phrase_endings", "fills"]
            },
            "ride": {
                "frequency_range": [2000, 10000],
                "velocity_curve": "linear",
                "interaction_groups": ["texture", "swing"],
                "common_patterns": ["jazz_pattern", "rock_pattern", "latin_pattern"]
            }
        }

    def _load_style_templates(self) -> Dict[str, Any]:
        """Load musical style rhythm templates"""
        return {
            "electronic_dance": {
                "primary_instruments": ["kick", "hi_hat", "snare"],
                "complexity_preference": "moderate",
                "swing_factor": 0.0,
                "polyrhythm_likelihood": 0.2
            },
            "hip_hop": {
                "primary_instruments": ["kick", "snare", "hi_hat"],
                "complexity_preference": "simple_to_moderate",
                "swing_factor": 0.1,
                "polyrhythm_likelihood": 0.3
            },
            "jazz": {
                "primary_instruments": ["ride", "hi_hat", "kick", "snare"],
                "complexity_preference": "complex",
                "swing_factor": 0.67,
                "polyrhythm_likelihood": 0.8
            },
            "rock": {
                "primary_instruments": ["kick", "snare", "hi_hat", "crash"],
                "complexity_preference": "moderate",
                "swing_factor": 0.0,
                "polyrhythm_likelihood": 0.1
            },
            "latin": {
                "primary_instruments": ["conga", "bongo", "timbale", "cowbell"],
                "complexity_preference": "complex",
                "swing_factor": 0.0,
                "polyrhythm_likelihood": 0.9
            }
        }

    async def generate_pattern(self,
                             style: str = "electronic_dance",
                             complexity: RhythmComplexity = RhythmComplexity.MODERATE,
                             tempo: int = 128,
                             time_signature: str = "4/4") -> RhythmPattern:
        """
        Generate a rhythm pattern based on style and parameters
        
        Args:
            style: Musical style for pattern generation
            complexity: Desired complexity level
            tempo: Target tempo in BPM
            time_signature: Time signature for the pattern
            
        Returns:
            RhythmPattern: Generated rhythm pattern
        """
        try:
            logger.info(f"Generating {complexity.value} {style} rhythm pattern at {tempo} BPM")
            
            pattern_id = f"pattern_{int(asyncio.get_event_loop().time() * 1000)}"
            
            # Get style template
            style_template = self.style_templates.get(style, self.style_templates["electronic_dance"])
            
            # Generate base pattern
            base_pattern = await self._generate_base_pattern(style, complexity, time_signature)
            
            # Apply swing if appropriate
            swing_factor = await self._calculate_swing_factor(style_template, complexity)
            
            # Add accents and dynamics
            accents = await self._generate_accents(base_pattern, complexity)
            
            # Generate fills
            fills = await self._generate_fills(base_pattern, complexity)
            
            # Determine style tags
            style_tags = await self._determine_style_tags(style, base_pattern, complexity)
            
            pattern = RhythmPattern(
                pattern_id=pattern_id,
                name=f"{style}_{complexity.value}_pattern",
                time_signature=time_signature,
                pattern=base_pattern,
                complexity=complexity,
                swing_factor=swing_factor,
                accents=accents,
                fills=fills,
                style_tags=style_tags
            )
            
            # Update performance metrics
            self._update_pattern_metrics(pattern)
            
            logger.info(f"Generated pattern {pattern_id} with {len(base_pattern)} steps")
            return pattern
            
        except Exception as e:
            logger.error(f"Pattern generation failed: {e}")
            raise

    async def _generate_base_pattern(self,
                                   style: str,
                                   complexity: RhythmComplexity,
                                   time_signature: str) -> List[float]:
        """Generate base rhythm pattern"""
        
        # Determine pattern length based on time signature
        if time_signature == "4/4":
            pattern_length = 16  # 16th note resolution
        elif time_signature == "3/4":
            pattern_length = 12
        elif time_signature == "6/8":
            pattern_length = 12
        else:
            pattern_length = 16  # Default
        
        pattern = [0.0] * pattern_length
        
        # Get style-specific base pattern
        if style in self.groove_database:
            style_data = self.groove_database[style]
            base_template = style_data.get("main_pattern", [])
            
            # Copy template pattern
            for i in range(min(len(base_template), pattern_length)):
                pattern[i] = base_template[i]
        else:
            # Generate default four-on-floor pattern
            for i in range(0, pattern_length, 4):
                pattern[i] = 1.0
        
        # Modify based on complexity
        pattern = await self._apply_complexity(pattern, complexity)
        
        return pattern

    async def _apply_complexity(self, pattern: List[float], complexity: RhythmComplexity) -> List[float]:
        """Apply complexity modifications to pattern"""
        
        if complexity == RhythmComplexity.MINIMAL:
            # Simplify pattern - only keep strongest beats
            for i in range(len(pattern)):
                if pattern[i] < 0.8:
                    pattern[i] = 0.0
        
        elif complexity == RhythmComplexity.SIMPLE:
            # Keep basic pattern as is
            pass
        
        elif complexity == RhythmComplexity.MODERATE:
            # Add some syncopation
            for i in range(1, len(pattern), 4):
                if pattern[i] == 0.0:
                    pattern[i] = 0.4  # Add light off-beat
        
        elif complexity == RhythmComplexity.COMPLEX:
            # Add more intricate rhythms
            for i in range(len(pattern)):
                if pattern[i] == 0.0 and i % 2 == 1:
                    pattern[i] = 0.3 + (i % 3) * 0.1  # Varied velocities
        
        elif complexity == RhythmComplexity.POLYRHYTHMIC:
            # Add polyrhythmic elements
            for i in range(len(pattern)):
                if i % 3 == 0 and pattern[i] == 0.0:
                    pattern[i] = 0.5  # Add triplet feel
        
        return pattern

    async def _calculate_swing_factor(self, style_template: Dict[str, Any], complexity: RhythmComplexity) -> float:
        """Calculate appropriate swing factor"""
        
        base_swing = style_template.get("swing_factor", 0.0)
        
        # Adjust based on complexity
        if complexity == RhythmComplexity.COMPLEX:
            return min(base_swing * 1.2, 1.0)
        elif complexity == RhythmComplexity.MINIMAL:
            return base_swing * 0.5
        else:
            return base_swing

    async def _generate_accents(self, pattern: List[float], complexity: RhythmComplexity) -> List[int]:
        """Generate accent positions"""
        
        accents = []
        
        # Primary accents on strong beats
        for i in range(0, len(pattern), 4):
            if pattern[i] > 0.5:
                accents.append(i)
        
        # Add secondary accents based on complexity
        if complexity in [RhythmComplexity.COMPLEX, RhythmComplexity.POLYRHYTHMIC]:
            for i in range(2, len(pattern), 4):
                if pattern[i] > 0.3:
                    accents.append(i)
        
        return accents

    async def _generate_fills(self, pattern: List[float], complexity: RhythmComplexity) -> List[Dict[str, Any]]:
        """Generate fill variations"""
        
        fills = []
        
        if complexity in [RhythmComplexity.MODERATE, RhythmComplexity.COMPLEX, RhythmComplexity.POLYRHYTHMIC]:
            # Generate basic fill
            fill_pattern = pattern.copy()
            
            # Add fill elements in last quarter
            fill_start = len(pattern) - 4
            for i in range(fill_start, len(pattern)):
                if fill_pattern[i] < 0.5:
                    fill_pattern[i] = 0.6 + (i - fill_start) * 0.1
            
            fills.append({
                "name": "basic_fill",
                "pattern": fill_pattern,
                "trigger_probability": 0.25,
                "position": "phrase_end"
            })
        
        return fills

    async def _determine_style_tags(self,
                                  style: str,
                                  pattern: List[float],
                                  complexity: RhythmComplexity) -> List[str]:
        """Determine style tags for the pattern"""
        
        tags = [style, complexity.value]
        
        # Analyze pattern characteristics
        strong_beats = sum(1 for i in range(0, len(pattern), 4) if pattern[i] > 0.7)
        off_beats = sum(1 for i in range(1, len(pattern), 2) if pattern[i] > 0.3)
        
        if strong_beats >= 3:
            tags.append("driving")
        if off_beats >= 4:
            tags.append("syncopated")
        
        # Style-specific tags
        if style == "electronic_dance":
            tags.extend(["four_on_floor", "club_ready"])
        elif style == "hip_hop":
            tags.extend(["urban", "groove_based"])
        elif style == "jazz":
            tags.extend(["swing", "sophisticated"])
        
        return tags

    async def create_percussion_map(self,
                                  instruments: List[str],
                                  style: str = "electronic_dance") -> PercussionMap:
        """Create comprehensive percussion mapping"""
        
        map_id = f"percmap_{int(asyncio.get_event_loop().time() * 1000)}"
        
        # Initialize percussion map
        percussion_map = PercussionMap(map_id=map_id)
        
        # Configure each instrument
        for instrument in instruments:
            if instrument in self.percussion_library:
                instrument_config = self.percussion_library[instrument].copy()
                
                # Generate patterns for this instrument
                instrument_patterns = await self._generate_instrument_patterns(instrument, style)
                instrument_config["patterns"] = instrument_patterns
                
                percussion_map.instruments[instrument] = instrument_config
        
        # Generate layering rules
        percussion_map.layering_rules = await self._generate_layering_rules(instruments, style)
        
        # Generate velocity curves
        percussion_map.velocity_curves = await self._generate_velocity_curves(instruments)
        
        # Generate interaction matrix
        percussion_map.interaction_matrix = await self._generate_interaction_matrix(instruments)
        
        return percussion_map

    async def _generate_instrument_patterns(self, instrument: str, style: str) -> List[List[float]]:
        """Generate patterns specific to an instrument"""
        
        patterns = []
        
        if style in self.groove_database:
            style_data = self.groove_database[style]
            
            # Get instrument-specific pattern if available
            pattern_key = f"{instrument}_pattern"
            if pattern_key in style_data:
                patterns.append(style_data[pattern_key])
            else:
                # Generate based on main pattern and instrument characteristics
                main_pattern = style_data.get("main_pattern", [1.0, 0.0, 0.0, 0.0] * 4)
                
                if instrument == "kick":
                    # Emphasize strong beats
                    pattern = [v if i % 4 == 0 else v * 0.3 for i, v in enumerate(main_pattern)]
                elif instrument == "snare":
                    # Emphasize backbeat
                    pattern = [v if i % 8 == 4 else v * 0.2 for i, v in enumerate(main_pattern)]
                elif instrument == "hi_hat":
                    # Create consistent pattern
                    pattern = [0.5 if i % 2 == 1 else 0.3 for i in range(len(main_pattern))]
                else:
                    pattern = main_pattern
                
                patterns.append(pattern)
        
        return patterns

    async def _generate_layering_rules(self, instruments: List[str], style: str) -> Dict[str, List[str]]:
        """Generate instrument layering rules"""
        
        rules = {}
        
        # Basic layering principles
        if "kick" in instruments:
            rules["kick"] = ["foundational", "low_frequency_priority"]
        
        if "snare" in instruments:
            rules["snare"] = ["accent_layer", "mid_frequency"]
        
        if "hi_hat" in instruments:
            rules["hi_hat"] = ["texture_layer", "high_frequency", "continuous"]
        
        # Style-specific rules
        if style == "electronic_dance":
            if "kick" in instruments and "hi_hat" in instruments:
                rules["combination_kick_hihat"] = ["interlocked", "complementary"]
        
        return rules

    async def _generate_velocity_curves(self, instruments: List[str]) -> Dict[str, List[float]]:
        """Generate velocity curves for instruments"""
        
        curves = {}
        
        for instrument in instruments:
            if instrument in self.percussion_library:
                curve_type = self.percussion_library[instrument].get("velocity_curve", "linear")
                
                if curve_type == "exponential":
                    curve = [i**2 / 256 for i in range(16)]  # Exponential curve
                elif curve_type == "logarithmic":
                    curve = [np.log(i + 1) / np.log(17) for i in range(16)]  # Logarithmic curve
                else:
                    curve = [i / 15 for i in range(16)]  # Linear curve
                
                curves[instrument] = curve
        
        return curves

    async def _generate_interaction_matrix(self, instruments: List[str]) -> Dict[str, Dict[str, float]]:
        """Generate instrument interaction matrix"""
        
        matrix = {}
        
        for instrument in instruments:
            matrix[instrument] = {}
            for other_instrument in instruments:
                if instrument == other_instrument:
                    matrix[instrument][other_instrument] = 1.0
                else:
                    # Calculate interaction strength based on frequency overlap and style
                    interaction_strength = await self._calculate_interaction_strength(instrument, other_instrument)
                    matrix[instrument][other_instrument] = interaction_strength
        
        return matrix

    async def _calculate_interaction_strength(self, inst1: str, inst2: str) -> float:
        """Calculate interaction strength between two instruments"""
        
        # Get frequency ranges
        inst1_data = self.percussion_library.get(inst1, {})
        inst2_data = self.percussion_library.get(inst2, {})
        
        range1 = inst1_data.get("frequency_range", [0, 20000])
        range2 = inst2_data.get("frequency_range", [0, 20000])
        
        # Calculate frequency overlap
        overlap_start = max(range1[0], range2[0])
        overlap_end = min(range1[1], range2[1])
        
        if overlap_start < overlap_end:
            overlap = overlap_end - overlap_start
            total_range = max(range1[1], range2[1]) - min(range1[0], range2[0])
            interaction_strength = overlap / total_range
        else:
            interaction_strength = 0.0
        
        return interaction_strength

    async def create_groove_template(self,
                                   style: str,
                                   tempo_range: Tuple[int, int] = (120, 130),
                                   complexity: RhythmComplexity = RhythmComplexity.MODERATE) -> GrooveTemplate:
        """Create complete groove template"""
        
        template_id = f"groove_{int(asyncio.get_event_loop().time() * 1000)}"
        
        # Generate main pattern
        main_pattern = await self.generate_pattern(style, complexity, tempo_range[0])
        
        # Generate variations
        variation_patterns = []
        for variation_type in ["simple", "complex", "fill"]:
            if variation_type == "simple":
                var_complexity = RhythmComplexity.SIMPLE
            elif variation_type == "complex":
                var_complexity = RhythmComplexity.COMPLEX
            else:
                var_complexity = complexity
            
            variation = await self.generate_pattern(style, var_complexity, tempo_range[0])
            variation.name = f"{main_pattern.name}_{variation_type}"
            variation_patterns.append(variation)
        
        # Create percussion map
        style_template = self.style_templates.get(style, {})
        instruments = style_template.get("primary_instruments", ["kick", "snare", "hi_hat"])
        percussion_map = await self.create_percussion_map(instruments, style)
        
        # Generate arrangement suggestions
        arrangement_suggestions = await self._generate_arrangement_suggestions(style, complexity)
        
        # Determine genre associations
        genre_associations = await self._determine_genre_associations(style, main_pattern)
        
        template = GrooveTemplate(
            template_id=template_id,
            name=f"{style}_{complexity.value}_groove",
            tempo_range=tempo_range,
            main_pattern=main_pattern,
            variation_patterns=variation_patterns,
            percussion_map=percussion_map,
            arrangement_suggestions=arrangement_suggestions,
            genre_associations=genre_associations
        )
        
        return template

    async def _generate_arrangement_suggestions(self, style: str, complexity: RhythmComplexity) -> List[str]:
        """Generate arrangement suggestions for the groove"""
        
        suggestions = []
        
        # Basic arrangement principles
        suggestions.append("Start with minimal elements and build layers gradually")
        suggestions.append("Use fills to transition between sections")
        
        # Style-specific suggestions
        if style == "electronic_dance":
            suggestions.extend([
                "Build energy through filter sweeps and percussion layers",
                "Use breakdown sections to create dynamic contrast",
                "Emphasize the drop with full rhythmic intensity"
            ])
        elif style == "hip_hop":
            suggestions.extend([
                "Leave space for vocal delivery",
                "Use ghost notes to add groove without cluttering",
                "Vary hi-hat patterns between verses and chorus"
            ])
        elif style == "jazz":
            suggestions.extend([
                "Allow for rhythmic interpretation and swing feel",
                "Use brush techniques for softer sections",
                "Trade solos between instruments and rhythm section"
            ])
        
        # Complexity-based suggestions
        if complexity == RhythmComplexity.COMPLEX:
            suggestions.append("Balance complexity with musical coherence")
        elif complexity == RhythmComplexity.MINIMAL:
            suggestions.append("Focus on groove and pocket over busyness")
        
        return suggestions

    async def _determine_genre_associations(self, style: str, pattern: RhythmPattern) -> List[str]:
        """Determine genre associations for the groove"""
        
        associations = [style]
        
        # Analyze pattern characteristics for additional associations
        pattern_data = pattern.pattern
        strong_beat_ratio = sum(1 for i in range(0, len(pattern_data), 4) if pattern_data[i] > 0.7) / (len(pattern_data) // 4)
        syncopation_ratio = sum(1 for i in range(1, len(pattern_data), 2) if pattern_data[i] > 0.3) / (len(pattern_data) // 2)
        
        # Add associations based on characteristics
        if strong_beat_ratio > 0.8:
            associations.append("dance")
        if syncopation_ratio > 0.5:
            associations.append("funk")
        if pattern.swing_factor > 0.3:
            associations.append("swing")
        
        # Style-specific associations
        if style == "electronic_dance":
            associations.extend(["club", "dj_friendly", "loop_based"])
        elif style == "hip_hop":
            associations.extend(["urban", "rap", "beat_making"])
        elif style == "jazz":
            associations.extend(["improvisation", "sophisticated", "acoustic"])
        
        return list(set(associations))  # Remove duplicates

    def _update_pattern_metrics(self, pattern: RhythmPattern):
        """Update generator performance metrics"""
        self.performance_metrics["patterns_generated"] += 1
        
        # Update complexity distribution
        complexity_key = pattern.complexity.value
        self.performance_metrics["complexity_distribution"][complexity_key] = (
            self.performance_metrics["complexity_distribution"].get(complexity_key, 0) + 1
        )
        
        # Update style preferences
        for tag in pattern.style_tags:
            self.performance_metrics["style_preferences"][tag] = (
                self.performance_metrics["style_preferences"].get(tag, 0) + 1
            )

    async def get_generator_status(self) -> Dict[str, Any]:
        """Get current generator status and performance metrics"""
        return {
            "generators": self.generators,
            "performance_metrics": self.performance_metrics,
            "configuration": {
                "default_resolution": self.default_resolution,
                "complexity_level": self.complexity_level,
                "enable_polyrhythm": self.enable_polyrhythm,
                "swing_detection": self.swing_detection
            },
            "database_info": {
                "groove_styles": len(self.groove_database),
                "percussion_instruments": len(self.percussion_library),
                "style_templates": len(self.style_templates)
            }
        }

# Factory function
def create_rhythm_generator(config: Optional[Dict[str, Any]] = None) -> RhythmGenerator:
    """Factory function to create a configured RhythmGenerator instance"""
    return RhythmGenerator(config)