#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent Rhythm Pattern AI
================================================================================
Module: ai_engine/remix_generation/rhythm_pattern_ai.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Rhythm Generation AI (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Générateur de patterns rythmiques IA ultra-avancé avec deep learning
TECHNOLOGIES: Neural Networks, Rhythmic Analysis, Pattern Recognition, Temporal Modeling
LOGIQUE MÉTIER: Musical context → Rhythm analysis → Pattern generation → Groove optimization → Quality validation
"""
import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import librosa
import scipy.signal as signal
from scipy.stats import entropy
import mido

# Configure logging
logger = logging.getLogger(__name__)

class RhythmStyle(Enum):
    """Rhythm generation styles"""
    ROCK = "rock"
    JAZZ = "jazz"
    POP = "pop"
    ELECTRONIC = "electronic"
    LATIN = "latin"
    FUNK = "funk"
    REGGAE = "reggae"
    BLUES = "blues"
    COUNTRY = "country"
    AFROBEAT = "afrobeat"
    BREAKBEAT = "breakbeat"
    TRAP = "trap"
    TECHNO = "techno"
    HOUSE = "house"

class RhythmComplexity(Enum):
    """Rhythm complexity levels"""
    SIMPLE = "simple"        # Basic patterns
    MODERATE = "moderate"    # Standard complexity
    COMPLEX = "complex"      # Advanced patterns
    POLYRHYTHMIC = "polyrhythmic"  # Multiple rhythms

class TimeSignature(Enum):
    """Time signatures"""
    FOUR_FOUR = "4/4"
    THREE_FOUR = "3/4"
    TWO_FOUR = "2/4"
    SIX_EIGHT = "6/8"
    FIVE_FOUR = "5/4"
    SEVEN_EIGHT = "7/8"
    NINE_EIGHT = "9/8"

class DrumVoice(Enum):
    """Drum voices/instruments"""
    KICK = "kick"
    SNARE = "snare"
    HIHAT_CLOSED = "hihat_closed"
    HIHAT_OPEN = "hihat_open"
    CRASH = "crash"
    RIDE = "ride"
    TOM_HIGH = "tom_high"
    TOM_MID = "tom_mid"
    TOM_LOW = "tom_low"
    COWBELL = "cowbell"
    CLAP = "clap"
    SHAKER = "shaker"

@dataclass
class RhythmParameters:
    """Parameters for rhythm generation"""
    tempo_bpm: int = 120
    time_signature: TimeSignature = TimeSignature.FOUR_FOUR
    pattern_length_bars: int = 4
    subdivision: int = 16  # 16th notes
    swing_factor: float = 0.0  # 0.0 = straight, 1.0 = full swing
    groove_intensity: float = 0.5  # Micro-timing variations
    accent_strength: float = 0.5  # Dynamic accent emphasis
    polyrhythm_enabled: bool = False
    fills_enabled: bool = True
    ghost_notes_enabled: bool = True
    humanization_level: float = 0.3  # Timing/velocity humanization

@dataclass
class RhythmPattern:
    """Generated rhythm pattern"""
    pattern_id: str
    drum_patterns: Dict[DrumVoice, List[float]]  # Velocity per subdivision
    timing_grid: List[float]  # Timing for each subdivision
    pattern_length: int
    tempo_bpm: int
    time_signature: TimeSignature
    style: RhythmStyle
    complexity_score: float
    groove_score: float
    generation_parameters: RhythmParameters
    audio_synthesis: Optional[np.ndarray] = None
    midi_data: Optional[bytes] = None

class RhythmConvNet(nn.Module):
    """Convolutional Neural Network for rhythm pattern generation"""
    
    def __init__(self, num_voices: int = 12, pattern_length: int = 64, 
                 hidden_dim: int = 128):
        super(RhythmConvNet, self).__init__()
        
        self.num_voices = num_voices
        self.pattern_length = pattern_length
        
        # Encoder: Pattern to latent space
        self.encoder = nn.Sequential(
            nn.Conv1d(num_voices, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(hidden_dim)
        )
        
        # Style conditioning
        self.style_embedding = nn.Embedding(len(RhythmStyle), hidden_dim)
        
        # Parameter conditioning
        self.param_projection = nn.Linear(8, hidden_dim)  # 8 rhythm parameters
        
        # Decoder: Latent space to pattern
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim * 3, 256),  # encoded + style + params
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_voices * pattern_length),
            nn.Sigmoid()  # Output velocities 0-1
        )
        
        # Groove enhancement network
        self.groove_enhancer = nn.Sequential(
            nn.Conv1d(num_voices, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(64, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(32, num_voices, kernel_size=3, padding=1),
            nn.Tanh()  # Output timing adjustments
        )
    
    def forward(self, input_pattern=None, style_token=None, parameters=None,
                generate_mode=False):
        
        if generate_mode:
            # Generation mode: create pattern from style and parameters
            batch_size = 1
            
            # Random latent vector if no input pattern
            if input_pattern is None:
                latent = torch.randn(batch_size, self.num_voices, self.pattern_length)
            else:
                latent = input_pattern
            
            # Encode input
            encoded = self.encoder(latent)
            encoded_flat = encoded.mean(dim=2)  # Global average pooling
            
        else:
            # Training mode: encode input pattern
            encoded = self.encoder(input_pattern)
            encoded_flat = encoded.mean(dim=2)
        
        # Style conditioning
        style_embed = self.style_embedding(style_token) if style_token is not None else torch.zeros_like(encoded_flat)
        
        # Parameter conditioning
        param_embed = self.param_projection(parameters) if parameters is not None else torch.zeros_like(encoded_flat)
        
        # Combine features
        combined = torch.cat([encoded_flat, style_embed, param_embed], dim=1)
        
        # Decode to pattern
        output = self.decoder(combined)
        output = output.view(-1, self.num_voices, self.pattern_length)
        
        # Apply groove enhancement
        groove_adjustment = self.groove_enhancer(output)
        
        return output, groove_adjustment

class RhythmLSTM(nn.Module):
    """LSTM-based rhythm sequence generator"""
    
    def __init__(self, num_voices: int = 12, hidden_size: int = 256, 
                 num_layers: int = 3):
        super(RhythmLSTM, self).__init__()
        
        self.num_voices = num_voices
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Input projection
        self.input_projection = nn.Linear(num_voices, hidden_size)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            hidden_size, hidden_size, num_layers,
            batch_first=True, dropout=0.2
        )
        
        # Output projection
        self.output_projection = nn.Linear(hidden_size, num_voices)
        
        # Attention mechanism for long-term dependencies
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
        
    def forward(self, x, hidden=None):
        batch_size, seq_len, _ = x.shape
        
        # Project input
        projected = self.input_projection(x)
        
        # LSTM forward pass
        lstm_out, hidden = self.lstm(projected, hidden)
        
        # Apply attention
        # Reshape for attention: (seq_len, batch, hidden_size)
        lstm_out_t = lstm_out.transpose(0, 1)
        attended, _ = self.attention(lstm_out_t, lstm_out_t, lstm_out_t)
        attended = attended.transpose(0, 1)
        
        # Output projection
        output = self.output_projection(attended)
        
        return torch.sigmoid(output), hidden

class GrooveAnalyzer:
    """Analyze and quantify groove characteristics"""
    
    def __init__(self):
        self.groove_templates = self._initialize_groove_templates()
    
    def _initialize_groove_templates(self) -> Dict[RhythmStyle, Dict[str, Any]]:
        """Initialize style-specific groove templates"""
        return {
            RhythmStyle.ROCK: {
                "kick_pattern": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                "hihat_pattern": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                "swing_factor": 0.0,
                "accent_beats": [1, 3]
            },
            RhythmStyle.JAZZ: {
                "kick_pattern": [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                "hihat_pattern": [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
                "swing_factor": 0.67,
                "accent_beats": [1, 3]
            },
            RhythmStyle.FUNK: {
                "kick_pattern": [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
                "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                "hihat_pattern": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "swing_factor": 0.1,
                "accent_beats": [1, 2.5, 4]
            },
            RhythmStyle.LATIN: {
                "kick_pattern": [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
                "snare_pattern": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
                "hihat_pattern": [1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1],
                "swing_factor": 0.0,
                "accent_beats": [1, 2.5, 4, 4.5]
            },
            RhythmStyle.ELECTRONIC: {
                "kick_pattern": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                "hihat_pattern": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                "swing_factor": 0.0,
                "accent_beats": [1, 3]
            }
        }
    
    async def analyze_groove(self, pattern: Dict[DrumVoice, List[float]],
                           timing_grid: List[float]) -> Dict[str, float]:
        """Analyze groove characteristics of a rhythm pattern"""
        try:
            analysis = {}
            
            # Syncopation analysis
            analysis["syncopation"] = await self._analyze_syncopation(pattern)
            
            # Groove tightness (timing consistency)
            analysis["tightness"] = await self._analyze_tightness(timing_grid)
            
            # Polyrhythmic complexity
            analysis["polyrhythm"] = await self._analyze_polyrhythm(pattern)
            
            # Dynamic variation
            analysis["dynamics"] = await self._analyze_dynamics(pattern)
            
            # Pocket (rhythmic feel)
            analysis["pocket"] = await self._analyze_pocket(pattern, timing_grid)
            
            # Overall groove score
            analysis["groove_score"] = await self._calculate_groove_score(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing groove: {e}")
            return {"groove_score": 0.5}
    
    async def _analyze_syncopation(self, pattern: Dict[DrumVoice, List[float]]) -> float:
        """Analyze syncopation level in the pattern"""
        try:
            # Focus on kick and snare patterns
            kick_pattern = pattern.get(DrumVoice.KICK, [])
            snare_pattern = pattern.get(DrumVoice.SNARE, [])
            
            if not kick_pattern and not snare_pattern:
                return 0.0
            
            syncopation_score = 0.0
            total_positions = len(kick_pattern) if kick_pattern else len(snare_pattern)
            
            # Strong beats (1 and 3 in 4/4) should have less syncopation
            strong_beats = [0, 8] if total_positions >= 16 else [0]
            weak_beats = [i for i in range(total_positions) if i not in strong_beats]
            
            # Check for notes on weak beats
            for voice_pattern in [kick_pattern, snare_pattern]:
                if voice_pattern:
                    for i in weak_beats:
                        if i < len(voice_pattern) and voice_pattern[i] > 0.3:
                            syncopation_score += voice_pattern[i]
            
            # Normalize
            syncopation_score = syncopation_score / (len(weak_beats) * 2)  # 2 voices max
            
            return min(1.0, syncopation_score)
            
        except Exception as e:
            logger.error(f"Error analyzing syncopation: {e}")
            return 0.0
    
    async def _analyze_tightness(self, timing_grid: List[float]) -> float:
        """Analyze timing tightness (deviation from grid)"""
        try:
            if len(timing_grid) < 2:
                return 1.0
            
            # Calculate expected timing (perfect grid)
            expected_intervals = [timing_grid[i+1] - timing_grid[i] 
                                for i in range(len(timing_grid)-1)]
            avg_interval = np.mean(expected_intervals)
            
            # Calculate actual deviations
            deviations = []
            for i, interval in enumerate(expected_intervals):
                deviation = abs(interval - avg_interval) / avg_interval
                deviations.append(deviation)
            
            # Tightness is inverse of average deviation
            avg_deviation = np.mean(deviations)
            tightness = max(0.0, 1.0 - avg_deviation * 10)  # Scale factor
            
            return tightness
            
        except Exception as e:
            logger.error(f"Error analyzing tightness: {e}")
            return 0.5
    
    async def _analyze_polyrhythm(self, pattern: Dict[DrumVoice, List[float]]) -> float:
        """Analyze polyrhythmic complexity"""
        try:
            if len(pattern) < 2:
                return 0.0
            
            patterns = list(pattern.values())
            polyrhythm_score = 0.0
            
            # Compare patterns pairwise
            for i in range(len(patterns)):
                for j in range(i+1, len(patterns)):
                    pattern1 = patterns[i]
                    pattern2 = patterns[j]
                    
                    if len(pattern1) == len(pattern2):
                        # Calculate cross-correlation
                        correlation = np.corrcoef(pattern1, pattern2)[0, 1]
                        if not np.isnan(correlation):
                            # Low correlation indicates polyrhythm
                            polyrhythm_score += (1.0 - abs(correlation))
            
            # Normalize by number of comparisons
            num_comparisons = len(patterns) * (len(patterns) - 1) / 2
            if num_comparisons > 0:
                polyrhythm_score /= num_comparisons
            
            return min(1.0, polyrhythm_score)
            
        except Exception as e:
            logger.error(f"Error analyzing polyrhythm: {e}")
            return 0.0
    
    async def _analyze_dynamics(self, pattern: Dict[DrumVoice, List[float]]) -> float:
        """Analyze dynamic variation in the pattern"""
        try:
            all_velocities = []
            for voice_pattern in pattern.values():
                all_velocities.extend([v for v in voice_pattern if v > 0])
            
            if len(all_velocities) < 2:
                return 0.0
            
            # Calculate coefficient of variation
            mean_velocity = np.mean(all_velocities)
            std_velocity = np.std(all_velocities)
            
            if mean_velocity > 0:
                cv = std_velocity / mean_velocity
                dynamics_score = min(1.0, cv * 2)  # Scale factor
            else:
                dynamics_score = 0.0
            
            return dynamics_score
            
        except Exception as e:
            logger.error(f"Error analyzing dynamics: {e}")
            return 0.0
    
    async def _analyze_pocket(self, pattern: Dict[DrumVoice, List[float]],
                            timing_grid: List[float]) -> float:
        """Analyze the 'pocket' (rhythmic feel and groove)"""
        try:
            # Simplified pocket analysis based on kick-snare relationship
            kick_pattern = pattern.get(DrumVoice.KICK, [])
            snare_pattern = pattern.get(DrumVoice.SNARE, [])
            
            if not kick_pattern or not snare_pattern:
                return 0.5
            
            pocket_score = 0.0
            
            # Check for strong kick-snare relationship
            for i in range(min(len(kick_pattern), len(snare_pattern))):
                if kick_pattern[i] > 0.3 and snare_pattern[i] > 0.3:
                    # Simultaneous kick and snare reduces pocket
                    pocket_score -= 0.2
                elif kick_pattern[i] > 0.5 and i % 4 == 0:
                    # Strong kicks on beats increase pocket
                    pocket_score += 0.3
                elif snare_pattern[i] > 0.5 and i % 8 == 4:
                    # Strong snares on backbeats increase pocket
                    pocket_score += 0.3
            
            # Normalize
            pocket_score = max(0.0, min(1.0, (pocket_score + 1.0) / 2.0))
            
            return pocket_score
            
        except Exception as e:
            logger.error(f"Error analyzing pocket: {e}")
            return 0.5
    
    async def _calculate_groove_score(self, analysis: Dict[str, float]) -> float:
        """Calculate overall groove score"""
        try:
            weights = {
                "syncopation": 0.2,
                "tightness": 0.3,
                "polyrhythm": 0.15,
                "dynamics": 0.15,
                "pocket": 0.2
            }
            
            groove_score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in analysis:
                    groove_score += analysis[metric] * weight
                    total_weight += weight
            
            if total_weight > 0:
                groove_score /= total_weight
            
            return groove_score
            
        except Exception as e:
            logger.error(f"Error calculating groove score: {e}")
            return 0.5

class RhythmPatternAI:
    """Main rhythm pattern generation AI"""
    
    def __init__(self):
        # Neural networks
        self.conv_model = RhythmConvNet()
        self.lstm_model = RhythmLSTM()
        
        # Analysis components
        self.groove_analyzer = GrooveAnalyzer()
        
        # Style-specific generators
        self.style_generators = {}
        
        # Generation history
        self.generation_history = []
        
        logger.info("RhythmPatternAI initialized successfully")
    
    async def generate_rhythm_pattern(self, style: RhythmStyle,
                                    parameters: RhythmParameters,
                                    complexity: RhythmComplexity = RhythmComplexity.MODERATE,
                                    use_neural_network: bool = True) -> RhythmPattern:
        """Generate rhythm pattern with specified style and parameters"""
        try:
            start_time = datetime.now()
            pattern_id = f"rhythm_{int(start_time.timestamp())}"
            
            # Generate drum patterns
            if use_neural_network:
                drum_patterns = await self._generate_with_neural_network(style, parameters, complexity)
            else:
                drum_patterns = await self._generate_with_templates(style, parameters, complexity)
            
            # Generate timing grid with groove
            timing_grid = await self._generate_timing_grid(parameters, drum_patterns)
            
            # Apply humanization
            if parameters.humanization_level > 0:
                drum_patterns, timing_grid = await self._apply_humanization(
                    drum_patterns, timing_grid, parameters.humanization_level
                )
            
            # Analyze groove
            groove_analysis = await self.groove_analyzer.analyze_groove(drum_patterns, timing_grid)
            
            # Calculate complexity score
            complexity_score = await self._calculate_complexity_score(drum_patterns)
            
            # Generate audio synthesis
            audio_synthesis = await self._synthesize_audio(drum_patterns, timing_grid, parameters)
            
            # Generate MIDI data
            midi_data = await self._generate_midi(drum_patterns, timing_grid, parameters)
            
            # Create result
            result = RhythmPattern(
                pattern_id=pattern_id,
                drum_patterns=drum_patterns,
                timing_grid=timing_grid,
                pattern_length=len(timing_grid),
                tempo_bpm=parameters.tempo_bpm,
                time_signature=parameters.time_signature,
                style=style,
                complexity_score=complexity_score,
                groove_score=groove_analysis.get("groove_score", 0.5),
                generation_parameters=parameters,
                audio_synthesis=audio_synthesis,
                midi_data=midi_data
            )
            
            # Store in history
            self.generation_history.append({
                "timestamp": start_time.isoformat(),
                "pattern_id": pattern_id,
                "style": style.value,
                "complexity": complexity.value,
                "groove_score": result.groove_score,
                "complexity_score": result.complexity_score
            })
            
            logger.info(f"Generated rhythm pattern {pattern_id}: style={style.value}, groove={result.groove_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating rhythm pattern: {e}")
            raise
    
    async def _generate_with_neural_network(self, style: RhythmStyle,
                                          parameters: RhythmParameters,
                                          complexity: RhythmComplexity) -> Dict[DrumVoice, List[float]]:
        """Generate rhythm using neural network"""
        try:
            # Convert parameters to tensor
            param_tensor = await self._parameters_to_tensor(parameters, complexity)
            
            # Style token
            style_token = torch.tensor([list(RhythmStyle).index(style)])
            
            # Generate with CNN model
            with torch.no_grad():
                pattern_output, groove_adjustment = self.conv_model(
                    generate_mode=True,
                    style_token=style_token,
                    parameters=param_tensor
                )
                
                # Apply groove adjustments
                pattern_output = pattern_output + groove_adjustment * 0.1
                pattern_output = torch.clamp(pattern_output, 0, 1)
            
            # Convert to drum patterns
            drum_patterns = {}
            pattern_array = pattern_output[0].numpy()
            
            drum_voices = list(DrumVoice)
            for i, voice in enumerate(drum_voices[:pattern_array.shape[0]]):
                drum_patterns[voice] = pattern_array[i].tolist()
            
            return drum_patterns
            
        except Exception as e:
            logger.error(f"Error in neural network generation: {e}")
            # Fallback to template generation
            return await self._generate_with_templates(style, parameters, complexity)
    
    async def _generate_with_templates(self, style: RhythmStyle,
                                     parameters: RhythmParameters,
                                     complexity: RhythmComplexity) -> Dict[DrumVoice, List[float]]:
        """Generate rhythm using style templates"""
        try:
            # Get base template
            template = self.groove_analyzer.groove_templates.get(style)
            if not template:
                template = self.groove_analyzer.groove_templates[RhythmStyle.ROCK]
            
            # Calculate pattern length
            beats_per_bar = int(parameters.time_signature.value.split('/')[0])
            total_beats = parameters.pattern_length_bars * beats_per_bar
            pattern_length = total_beats * (parameters.subdivision // 4)
            
            # Generate base patterns
            drum_patterns = {}
            
            # Kick pattern
            base_kick = template["kick_pattern"]
            kick_pattern = await self._extend_pattern(base_kick, pattern_length)
            kick_pattern = await self._apply_complexity(kick_pattern, complexity, 0.8)
            drum_patterns[DrumVoice.KICK] = kick_pattern
            
            # Snare pattern
            base_snare = template["snare_pattern"]
            snare_pattern = await self._extend_pattern(base_snare, pattern_length)
            snare_pattern = await self._apply_complexity(snare_pattern, complexity, 0.9)
            drum_patterns[DrumVoice.SNARE] = snare_pattern
            
            # Hi-hat pattern
            base_hihat = template["hihat_pattern"]
            hihat_pattern = await self._extend_pattern(base_hihat, pattern_length)
            hihat_pattern = await self._apply_complexity(hihat_pattern, complexity, 0.6)
            drum_patterns[DrumVoice.HIHAT_CLOSED] = hihat_pattern
            
            # Add additional voices based on complexity
            if complexity in [RhythmComplexity.COMPLEX, RhythmComplexity.POLYRHYTHMIC]:
                # Add ride cymbal
                ride_pattern = await self._generate_secondary_voice(hihat_pattern, 0.4)
                drum_patterns[DrumVoice.RIDE] = ride_pattern
                
                # Add percussion
                if style in [RhythmStyle.LATIN, RhythmStyle.AFROBEAT]:
                    shaker_pattern = await self._generate_latin_percussion(pattern_length)
                    drum_patterns[DrumVoice.SHAKER] = shaker_pattern
            
            # Add fills if enabled
            if parameters.fills_enabled:
                drum_patterns = await self._add_fills(drum_patterns, parameters)
            
            # Add ghost notes if enabled
            if parameters.ghost_notes_enabled:
                drum_patterns = await self._add_ghost_notes(drum_patterns)
            
            return drum_patterns
            
        except Exception as e:
            logger.error(f"Error in template generation: {e}")
            # Return basic 4/4 pattern
            pattern_length = 16
            return {
                DrumVoice.KICK: [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0],
                DrumVoice.SNARE: [0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0],
                DrumVoice.HIHAT_CLOSED: [0.8, 0.4, 0.8, 0.4, 0.8, 0.4, 0.8, 0.4, 0.8, 0.4, 0.8, 0.4, 0.8, 0.4, 0.8, 0.4]
            }
    
    async def _extend_pattern(self, base_pattern: List[int], target_length: int) -> List[float]:
        """Extend a base pattern to target length"""
        try:
            if not base_pattern:
                return [0.0] * target_length
            
            extended = []
            for i in range(target_length):
                base_index = i % len(base_pattern)
                extended.append(float(base_pattern[base_index]))
            
            return extended
            
        except Exception as e:
            logger.error(f"Error extending pattern: {e}")
            return [0.0] * target_length
    
    async def _apply_complexity(self, pattern: List[float], 
                              complexity: RhythmComplexity,
                              base_velocity: float) -> List[float]:
        """Apply complexity variations to pattern"""
        try:
            complexity_multipliers = {
                RhythmComplexity.SIMPLE: 0.5,
                RhythmComplexity.MODERATE: 1.0,
                RhythmComplexity.COMPLEX: 1.5,
                RhythmComplexity.POLYRHYTHMIC: 2.0
            }
            
            multiplier = complexity_multipliers[complexity]
            
            # Add variations based on complexity
            varied_pattern = []
            for i, velocity in enumerate(pattern):
                if velocity > 0:
                    # Add some random variation
                    variation = np.random.normal(0, 0.1 * multiplier)
                    new_velocity = min(1.0, max(0.0, velocity * base_velocity + variation))
                    varied_pattern.append(new_velocity)
                else:
                    # Sometimes add notes in complex patterns
                    if complexity == RhythmComplexity.COMPLEX and np.random.random() < 0.1:
                        varied_pattern.append(0.3)
                    elif complexity == RhythmComplexity.POLYRHYTHMIC and np.random.random() < 0.15:
                        varied_pattern.append(0.4)
                    else:
                        varied_pattern.append(0.0)
            
            return varied_pattern
            
        except Exception as e:
            logger.error(f"Error applying complexity: {e}")
            return pattern
    
    async def _generate_secondary_voice(self, reference_pattern: List[float],
                                      correlation: float) -> List[float]:
        """Generate secondary voice with specified correlation to reference"""
        try:
            secondary = []
            
            for i, ref_velocity in enumerate(reference_pattern):
                if np.random.random() < correlation:
                    # Correlated with reference
                    if ref_velocity > 0.5:
                        secondary.append(ref_velocity * 0.8)
                    else:
                        secondary.append(0.0)
                else:
                    # Independent
                    if np.random.random() < 0.3:
                        secondary.append(np.random.uniform(0.3, 0.7))
                    else:
                        secondary.append(0.0)
            
            return secondary
            
        except Exception as e:
            logger.error(f"Error generating secondary voice: {e}")
            return [0.0] * len(reference_pattern)
    
    async def _generate_latin_percussion(self, pattern_length: int) -> List[float]:
        """Generate Latin percussion pattern"""
        try:
            # Create clave-inspired pattern
            pattern = [0.0] * pattern_length
            
            # 3-2 clave pattern
            clave_positions = [0, 3, 6, 10, 12]  # Simplified
            
            for pos in clave_positions:
                if pos < pattern_length:
                    pattern[pos] = np.random.uniform(0.4, 0.8)
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error generating Latin percussion: {e}")
            return [0.0] * pattern_length
    
    async def _add_fills(self, drum_patterns: Dict[DrumVoice, List[float]],
                        parameters: RhythmParameters) -> Dict[DrumVoice, List[float]]:
        """Add fills to drum patterns"""
        try:
            pattern_length = len(next(iter(drum_patterns.values())))
            beats_per_bar = int(parameters.time_signature.value.split('/')[0])
            subdivisions_per_bar = beats_per_bar * (parameters.subdivision // 4)
            
            # Add fills at end of bars
            for bar in range(parameters.pattern_length_bars):
                fill_start = (bar + 1) * subdivisions_per_bar - 4  # Last beat of bar
                
                if fill_start < pattern_length - 4:
                    # Add tom fills
                    if DrumVoice.TOM_HIGH not in drum_patterns:
                        drum_patterns[DrumVoice.TOM_HIGH] = [0.0] * pattern_length
                    if DrumVoice.TOM_MID not in drum_patterns:
                        drum_patterns[DrumVoice.TOM_MID] = [0.0] * pattern_length
                    
                    # Simple fill pattern
                    drum_patterns[DrumVoice.TOM_HIGH][fill_start] = 0.8
                    drum_patterns[DrumVoice.TOM_MID][fill_start + 1] = 0.7
                    drum_patterns[DrumVoice.TOM_HIGH][fill_start + 2] = 0.6
            
            return drum_patterns
            
        except Exception as e:
            logger.error(f"Error adding fills: {e}")
            return drum_patterns
    
    async def _add_ghost_notes(self, drum_patterns: Dict[DrumVoice, List[float]]) -> Dict[DrumVoice, List[float]]:
        """Add ghost notes to snare pattern"""
        try:
            if DrumVoice.SNARE in drum_patterns:
                snare_pattern = drum_patterns[DrumVoice.SNARE]
                
                for i, velocity in enumerate(snare_pattern):
                    if velocity == 0.0 and np.random.random() < 0.2:
                        # Add ghost note
                        snare_pattern[i] = np.random.uniform(0.1, 0.3)
                
                drum_patterns[DrumVoice.SNARE] = snare_pattern
            
            return drum_patterns
            
        except Exception as e:
            logger.error(f"Error adding ghost notes: {e}")
            return drum_patterns
    
    async def _generate_timing_grid(self, parameters: RhythmParameters,
                                  drum_patterns: Dict[DrumVoice, List[float]]) -> List[float]:
        """Generate timing grid with swing and groove"""
        try:
            pattern_length = len(next(iter(drum_patterns.values())))
            
            # Base timing (straight)
            beat_duration = 60.0 / parameters.tempo_bpm
            subdivision_duration = beat_duration / (parameters.subdivision / 4)
            
            timing_grid = []
            for i in range(pattern_length):
                base_time = i * subdivision_duration
                
                # Apply swing
                if parameters.swing_factor > 0 and i % 2 == 1:
                    swing_adjustment = subdivision_duration * parameters.swing_factor * 0.1
                    base_time += swing_adjustment
                
                # Apply groove (micro-timing)
                if parameters.groove_intensity > 0:
                    groove_adjustment = np.random.normal(0, subdivision_duration * parameters.groove_intensity * 0.05)
                    base_time += groove_adjustment
                
                timing_grid.append(base_time)
            
            return timing_grid
            
        except Exception as e:
            logger.error(f"Error generating timing grid: {e}")
            return [i * 0.125 for i in range(pattern_length)]  # Fallback
    
    async def _apply_humanization(self, drum_patterns: Dict[DrumVoice, List[float]],
                                timing_grid: List[float], 
                                humanization_level: float) -> Tuple[Dict[DrumVoice, List[float]], List[float]]:
        """Apply humanization to patterns and timing"""
        try:
            # Humanize velocities
            humanized_patterns = {}
            for voice, pattern in drum_patterns.items():
                humanized_pattern = []
                for velocity in pattern:
                    if velocity > 0:
                        # Add random velocity variation
                        variation = np.random.normal(0, humanization_level * 0.2)
                        new_velocity = min(1.0, max(0.1, velocity + variation))
                        humanized_pattern.append(new_velocity)
                    else:
                        humanized_pattern.append(0.0)
                humanized_patterns[voice] = humanized_pattern
            
            # Humanize timing
            humanized_timing = []
            for timing in timing_grid:
                # Add random timing variation
                variation = np.random.normal(0, humanization_level * 0.01)  # Small timing variations
                humanized_timing.append(timing + variation)
            
            return humanized_patterns, humanized_timing
            
        except Exception as e:
            logger.error(f"Error applying humanization: {e}")
            return drum_patterns, timing_grid
    
    async def _calculate_complexity_score(self, drum_patterns: Dict[DrumVoice, List[float]]) -> float:
        """Calculate complexity score of the pattern"""
        try:
            complexity_factors = []
            
            # Number of active voices
            active_voices = len([p for p in drum_patterns.values() if any(v > 0 for v in p)])
            voice_complexity = min(1.0, active_voices / 8.0)
            complexity_factors.append(voice_complexity)
            
            # Note density
            total_notes = sum(sum(1 for v in pattern if v > 0.3) for pattern in drum_patterns.values())
            total_positions = sum(len(pattern) for pattern in drum_patterns.values())
            density = total_notes / total_positions if total_positions > 0 else 0
            complexity_factors.append(density)
            
            # Velocity variation
            all_velocities = [v for pattern in drum_patterns.values() for v in pattern if v > 0]
            if all_velocities:
                velocity_std = np.std(all_velocities)
                velocity_complexity = min(1.0, velocity_std * 3)
                complexity_factors.append(velocity_complexity)
            
            # Pattern entropy
            for pattern in drum_patterns.values():
                if pattern:
                    # Discretize velocities for entropy calculation
                    discrete_pattern = [int(v * 4) for v in pattern]
                    if len(set(discrete_pattern)) > 1:
                        pattern_entropy = entropy(np.bincount(discrete_pattern))
                        entropy_normalized = min(1.0, pattern_entropy / 2.0)
                        complexity_factors.append(entropy_normalized)
            
            # Overall complexity
            return np.mean(complexity_factors) if complexity_factors else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating complexity score: {e}")
            return 0.5
    
    async def _synthesize_audio(self, drum_patterns: Dict[DrumVoice, List[float]],
                              timing_grid: List[float],
                              parameters: RhythmParameters,
                              sample_rate: int = 44100) -> np.ndarray:
        """Synthesize audio from drum patterns"""
        try:
            # Calculate total duration
            total_duration = timing_grid[-1] + 0.5 if timing_grid else 4.0
            total_samples = int(total_duration * sample_rate)
            
            # Initialize audio
            audio = np.zeros(total_samples)
            
            # Drum sound generators
            drum_sounds = await self._generate_drum_sounds(sample_rate)
            
            # Place drum hits
            for voice, pattern in drum_patterns.items():
                if voice in drum_sounds:
                    drum_sound = drum_sounds[voice]
                    
                    for i, velocity in enumerate(pattern):
                        if velocity > 0.1 and i < len(timing_grid):
                            # Calculate sample position
                            hit_time = timing_grid[i]
                            sample_pos = int(hit_time * sample_rate)
                            
                            # Apply velocity scaling
                            scaled_sound = drum_sound * velocity
                            
                            # Add to audio
                            end_pos = min(sample_pos + len(scaled_sound), total_samples)
                            if sample_pos < total_samples:
                                audio_segment = scaled_sound[:end_pos - sample_pos]
                                audio[sample_pos:end_pos] += audio_segment
            
            # Normalize to prevent clipping
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.9
            
            return audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error synthesizing audio: {e}")
            return np.array([])
    
    async def _generate_drum_sounds(self, sample_rate: int) -> Dict[DrumVoice, np.ndarray]:
        """Generate synthetic drum sounds"""
        try:
            drum_sounds = {}
            
            # Kick drum: Low frequency sine wave with envelope
            kick_duration = 0.3
            kick_samples = int(kick_duration * sample_rate)
            t = np.linspace(0, kick_duration, kick_samples)
            kick_freq = 60  # Hz
            kick_sound = np.sin(2 * np.pi * kick_freq * t * np.exp(-t * 3))
            kick_sound *= np.exp(-t * 5)  # Envelope
            drum_sounds[DrumVoice.KICK] = kick_sound
            
            # Snare drum: Noise burst with tone
            snare_duration = 0.2
            snare_samples = int(snare_duration * sample_rate)
            t = np.linspace(0, snare_duration, snare_samples)
            noise = np.random.normal(0, 1, snare_samples)
            tone = np.sin(2 * np.pi * 200 * t)  # 200 Hz tone
            snare_sound = (noise * 0.7 + tone * 0.3) * np.exp(-t * 10)
            drum_sounds[DrumVoice.SNARE] = snare_sound
            
            # Hi-hat: High frequency noise
            hihat_duration = 0.1
            hihat_samples = int(hihat_duration * sample_rate)
            t = np.linspace(0, hihat_duration, hihat_samples)
            hihat_noise = np.random.normal(0, 1, hihat_samples)
            # High-pass filter effect
            hihat_sound = hihat_noise * np.exp(-t * 20)
            drum_sounds[DrumVoice.HIHAT_CLOSED] = hihat_sound
            
            # Add more drum sounds as needed
            drum_sounds[DrumVoice.HIHAT_OPEN] = hihat_sound * 2  # Longer decay
            drum_sounds[DrumVoice.TOM_HIGH] = kick_sound * 0.8  # Higher pitch kick
            drum_sounds[DrumVoice.TOM_MID] = kick_sound * 0.6
            drum_sounds[DrumVoice.TOM_LOW] = kick_sound * 0.4
            drum_sounds[DrumVoice.RIDE] = hihat_sound * 1.5
            drum_sounds[DrumVoice.CRASH] = hihat_sound * 3
            drum_sounds[DrumVoice.SHAKER] = hihat_sound * 0.5
            
            return drum_sounds
            
        except Exception as e:
            logger.error(f"Error generating drum sounds: {e}")
            return {}
    
    async def _generate_midi(self, drum_patterns: Dict[DrumVoice, List[float]],
                           timing_grid: List[float],
                           parameters: RhythmParameters) -> bytes:
        """Generate MIDI data from drum patterns"""
        try:
            # Create MIDI file
            mid = mido.MidiFile()
            track = mido.MidiTrack()
            mid.tracks.append(track)
            
            # Set tempo
            tempo = mido.bpm2tempo(parameters.tempo_bpm)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
            
            # MIDI note mapping for drums (General MIDI)
            drum_midi_map = {
                DrumVoice.KICK: 36,
                DrumVoice.SNARE: 38,
                DrumVoice.HIHAT_CLOSED: 42,
                DrumVoice.HIHAT_OPEN: 46,
                DrumVoice.TOM_LOW: 41,
                DrumVoice.TOM_MID: 45,
                DrumVoice.TOM_HIGH: 48,
                DrumVoice.CRASH: 49,
                DrumVoice.RIDE: 51,
                DrumVoice.SHAKER: 69,
                DrumVoice.CLAP: 39,
                DrumVoice.COWBELL: 56
            }
            
            # Convert patterns to MIDI events
            events = []
            
            for voice, pattern in drum_patterns.items():
                if voice in drum_midi_map:
                    midi_note = drum_midi_map[voice]
                    
                    for i, velocity in enumerate(pattern):
                        if velocity > 0.1 and i < len(timing_grid):
                            # Convert velocity to MIDI velocity (0-127)
                            midi_velocity = int(velocity * 127)
                            midi_velocity = max(1, min(127, midi_velocity))
                            
                            # Calculate timing in ticks
                            time_seconds = timing_grid[i]
                            time_ticks = int(time_seconds * mid.ticks_per_beat * parameters.tempo_bpm / 60)
                            
                            events.append((time_ticks, 'note_on', midi_note, midi_velocity))
                            # Note off after short duration
                            events.append((time_ticks + 10, 'note_off', midi_note, 0))
            
            # Sort events by time
            events.sort(key=lambda x: x[0])
            
            # Add events to track with proper timing
            current_time = 0
            for event_time, event_type, note, velocity in events:
                delta_time = event_time - current_time
                track.append(mido.Message(event_type, note=note, velocity=velocity, time=delta_time))
                current_time = event_time
            
            return mid.to_bytes()
            
        except Exception as e:
            logger.error(f"Error generating MIDI: {e}")
            return b''
    
    async def _parameters_to_tensor(self, parameters: RhythmParameters,
                                   complexity: RhythmComplexity) -> torch.Tensor:
        """Convert parameters to tensor for neural network"""
        try:
            param_values = [
                (parameters.tempo_bpm - 60) / 140.0,  # Normalize 60-200 BPM
                list(TimeSignature).index(parameters.time_signature) / len(TimeSignature),
                parameters.pattern_length_bars / 8.0,  # Normalize up to 8 bars
                parameters.subdivision / 32.0,  # Normalize up to 32nd notes
                parameters.swing_factor,
                parameters.groove_intensity,
                parameters.accent_strength,
                list(RhythmComplexity).index(complexity) / len(RhythmComplexity)
            ]
            
            return torch.tensor(param_values, dtype=torch.float32).unsqueeze(0)
            
        except Exception as e:
            logger.error(f"Error converting parameters to tensor: {e}")
            return torch.zeros(1, 8)
    
    async def analyze_rhythm_similarity(self, pattern1: RhythmPattern,
                                      pattern2: RhythmPattern) -> Dict[str, float]:
        """Analyze similarity between two rhythm patterns"""
        try:
            similarity_metrics = {}
            
            # Voice correlation analysis
            voice_correlations = []
            for voice in pattern1.drum_patterns:
                if voice in pattern2.drum_patterns:
                    p1 = pattern1.drum_patterns[voice]
                    p2 = pattern2.drum_patterns[voice]
                    
                    if len(p1) == len(p2):
                        correlation = np.corrcoef(p1, p2)[0, 1]
                        if not np.isnan(correlation):
                            voice_correlations.append(abs(correlation))
            
            similarity_metrics["voice_correlation"] = np.mean(voice_correlations) if voice_correlations else 0.0
            
            # Rhythm complexity similarity
            complexity_diff = abs(pattern1.complexity_score - pattern2.complexity_score)
            similarity_metrics["complexity_similarity"] = 1.0 - complexity_diff
            
            # Groove similarity
            groove_diff = abs(pattern1.groove_score - pattern2.groove_score)
            similarity_metrics["groove_similarity"] = 1.0 - groove_diff
            
            # Style compatibility
            style_similarity = 1.0 if pattern1.style == pattern2.style else 0.5
            similarity_metrics["style_similarity"] = style_similarity
            
            # Overall similarity
            similarity_metrics["overall_similarity"] = np.mean([
                similarity_metrics["voice_correlation"],
                similarity_metrics["complexity_similarity"],
                similarity_metrics["groove_similarity"],
                similarity_metrics["style_similarity"]
            ])
            
            return similarity_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing rhythm similarity: {e}")
            return {"overall_similarity": 0.0}
    
    async def evolve_rhythm_pattern(self, base_pattern: RhythmPattern,
                                  evolution_strength: float = 0.3) -> RhythmPattern:
        """Evolve an existing rhythm pattern"""
        try:
            # Create evolved parameters
            evolved_params = base_pattern.generation_parameters
            
            # Mutate some parameters
            if np.random.random() < evolution_strength:
                evolved_params.groove_intensity += np.random.normal(0, 0.1)
                evolved_params.groove_intensity = max(0.0, min(1.0, evolved_params.groove_intensity))
            
            if np.random.random() < evolution_strength:
                evolved_params.swing_factor += np.random.normal(0, 0.1)
                evolved_params.swing_factor = max(0.0, min(1.0, evolved_params.swing_factor))
            
            # Generate evolved pattern
            evolved_pattern = await self.generate_rhythm_pattern(
                style=base_pattern.style,
                parameters=evolved_params,
                complexity=RhythmComplexity.MODERATE,
                use_neural_network=True
            )
            
            logger.info(f"Evolved pattern {base_pattern.pattern_id} -> {evolved_pattern.pattern_id}")
            
            return evolved_pattern
            
        except Exception as e:
            logger.error(f"Error evolving rhythm pattern: {e}")
            raise
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get generation performance statistics"""
        try:
            if not self.generation_history:
                return {"total_generated": 0}
            
            recent_history = self.generation_history[-50:]  # Last 50 generations
            
            return {
                "total_generated": len(self.generation_history),
                "recent_average_groove_score": np.mean([h["groove_score"] for h in recent_history]),
                "recent_average_complexity": np.mean([h["complexity_score"] for h in recent_history]),
                "style_distribution": {
                    style: sum(1 for h in recent_history if h["style"] == style)
                    for style in set(h["style"] for h in recent_history)
                },
                "last_generation": recent_history[-1] if recent_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_generated": 0}

# Processing classes for export
RhythmGenerator = RhythmPatternAI
RhythmAnalyzer = GrooveAnalyzer
RhythmOptimizer = RhythmPatternAI

# Export classes
__all__ = [
    "RhythmPatternAI",
    "RhythmGenerator",
    "RhythmAnalyzer", 
    "RhythmOptimizer",
    "RhythmStyle",
    "RhythmComplexity",
    "TimeSignature",
    "DrumVoice",
    "RhythmParameters",
    "RhythmPattern",
    "GrooveAnalyzer",
    "RhythmConvNet",
    "RhythmLSTM"
]