#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA-Influencer-Agent Melody Generator
================================================================================
Module: ai_engine/remix_generation/melody_generator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Melody Generation AI (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Générateur de mélodies IA ultra-avancé avec réseaux de neurones
TECHNOLOGIES: Deep Learning, RNN/LSTM, Transformer, Music Theory, Harmonic Analysis
LOGIQUE MÉTIER: Musical context → AI analysis → Melodic composition → Harmonic validation → Quality assessment
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import librosa
import music21
from music21 import stream, note, pitch, duration, key, scale, interval, chord
import mido
from scipy import signal

# Configure logging
logger = logging.getLogger(__name__)

class MelodyStyle(Enum):
    """Melody generation styles"""
    CLASSICAL = "classical"
    JAZZ = "jazz"
    POP = "pop"
    ELECTRONIC = "electronic"
    BLUES = "blues"
    ROCK = "rock"
    AMBIENT = "ambient"
    LATIN = "latin"
    FOLK = "folk"
    EXPERIMENTAL = "experimental"

class MelodyComplexity(Enum):
    """Melody complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VIRTUOSIC = "virtuosic"

class MelodyMode(Enum):
    """Musical modes for melody generation"""
    IONIAN = "ionian"          # Major
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"        # Natural minor
    LOCRIAN = "locrian"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"

@dataclass
class MelodyParameters:
    """Parameters for melody generation"""
    key_signature: str = "C"
    mode: MelodyMode = MelodyMode.IONIAN
    tempo_bpm: int = 120
    time_signature: str = "4/4"
    length_bars: int = 8
    note_density: float = 0.7  # 0.0 to 1.0
    melodic_range_semitones: int = 24
    rhythmic_complexity: float = 0.5
    harmonic_complexity: float = 0.5
    emotional_valence: float = 0.5  # -1.0 (sad) to 1.0 (happy)
    energy_level: float = 0.5  # 0.0 (calm) to 1.0 (energetic)
    chromaticism: float = 0.2  # Amount of chromatic notes
    phrase_structure: List[int] = None  # Phrase lengths in bars

@dataclass
class GeneratedMelody:
    """Generated melody result"""
    melody_notes: List[Dict[str, Any]]
    midi_data: bytes
    audio_synthesis: np.ndarray
    harmonic_analysis: Dict[str, Any]
    quality_metrics: Dict[str, float]
    generation_parameters: MelodyParameters
    processing_time_seconds: float
    melody_id: str
    success: bool

class MelodyTransformerNetwork(nn.Module):
    """Transformer-based melody generation network"""
    
    def __init__(self, vocab_size: int = 128, d_model: int = 256, 
                 nhead: int = 8, num_layers: int = 6, max_seq_length: int = 512):
        super(MelodyTransformerNetwork, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        
        # Token embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_length, d_model)
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            activation='relu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output layers
        self.output_projection = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(0.1)
        
        # Style and parameter conditioning
        self.style_embedding = nn.Embedding(10, d_model)  # 10 different styles
        self.parameter_projection = nn.Linear(12, d_model)  # 12 melody parameters
        
    def forward(self, input_tokens, style_token=None, parameters=None, 
                generate_length=None):
        seq_length = input_tokens.size(1)
        
        # Token embeddings
        token_embeds = self.token_embedding(input_tokens)
        
        # Position embeddings
        positions = torch.arange(seq_length).unsqueeze(0).to(input_tokens.device)
        pos_embeds = self.position_embedding(positions)
        
        # Combine embeddings
        embeddings = token_embeds + pos_embeds
        
        # Add style conditioning
        if style_token is not None:
            style_embeds = self.style_embedding(style_token).unsqueeze(1)
            embeddings = embeddings + style_embeds
        
        # Add parameter conditioning
        if parameters is not None:
            param_embeds = self.parameter_projection(parameters).unsqueeze(1)
            embeddings = embeddings + param_embeds
        
        # Apply dropout
        embeddings = self.dropout(embeddings)
        
        # Transformer processing
        # Need to transpose for transformer (seq_len, batch, d_model)
        embeddings = embeddings.transpose(0, 1)
        
        # Create causal mask for autoregressive generation
        mask = self._generate_square_subsequent_mask(seq_length).to(input_tokens.device)
        
        transformer_output = self.transformer(embeddings, mask=mask)
        
        # Transpose back (batch, seq_len, d_model)
        transformer_output = transformer_output.transpose(0, 1)
        
        # Output projection
        logits = self.output_projection(transformer_output)
        
        return logits
    
    def _generate_square_subsequent_mask(self, sz):
        """Generate causal mask for transformer"""
        mask = torch.triu(torch.ones(sz, sz)) == 1
        mask = mask.transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask
    
    @torch.no_grad()
    def generate(self, prompt_tokens, style_token=None, parameters=None, 
                 max_length=256, temperature=1.0, top_k=50, top_p=0.9):
        """Generate melody sequence"""
        self.eval()
        
        generated = prompt_tokens.clone()
        
        for _ in range(max_length - prompt_tokens.size(1)):
            # Get logits for current sequence
            logits = self.forward(generated, style_token, parameters)
            
            # Get logits for last position
            next_token_logits = logits[:, -1, :] / temperature
            
            # Apply top-k filtering
            if top_k > 0:
                indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                next_token_logits[indices_to_remove] = float('-inf')
            
            # Apply top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                # Remove tokens with cumulative probability above threshold
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                next_token_logits[indices_to_remove] = float('-inf')
            
            # Sample next token
            probs = F.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append to generated sequence
            generated = torch.cat([generated, next_token], dim=1)
            
            # Check for end token or other stopping criteria
            if next_token.item() == 0:  # Assuming 0 is end token
                break
        
        return generated

class MelodyLSTMNetwork(nn.Module):
    """LSTM-based melody generation network"""
    
    def __init__(self, vocab_size: int = 128, hidden_size: int = 256, 
                 num_layers: int = 3, dropout: float = 0.2):
        super(MelodyLSTMNetwork, self).__init__()
        
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        
        # Output layer
        self.output = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, hidden=None):
        # Embedding
        embedded = self.embedding(x)
        
        # LSTM
        lstm_out, hidden = self.lstm(embedded, hidden)
        
        # Dropout
        lstm_out = self.dropout(lstm_out)
        
        # Output projection
        output = self.output(lstm_out)
        
        return output, hidden
    
    def init_hidden(self, batch_size, device):
        """Initialize hidden state"""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)

class MusicTheoryEngine:
    """Music theory analysis and validation engine"""
    
    def __init__(self):
        self.scale_patterns = self._initialize_scale_patterns()
        self.chord_progressions = self._initialize_chord_progressions()
        self.interval_weights = self._initialize_interval_weights()
    
    def _initialize_scale_patterns(self) -> Dict[MelodyMode, List[int]]:
        """Initialize scale patterns in semitones"""
        return {
            MelodyMode.IONIAN: [0, 2, 4, 5, 7, 9, 11],
            MelodyMode.DORIAN: [0, 2, 3, 5, 7, 9, 10],
            MelodyMode.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
            MelodyMode.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
            MelodyMode.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
            MelodyMode.AEOLIAN: [0, 2, 3, 5, 7, 8, 10],
            MelodyMode.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
            MelodyMode.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
            MelodyMode.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11]
        }
    
    def _initialize_chord_progressions(self) -> Dict[str, List[str]]:
        """Initialize common chord progressions"""
        return {
            "pop": ["I", "V", "vi", "IV"],
            "jazz": ["ii", "V", "I", "vi"],
            "blues": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
            "classical": ["I", "vi", "IV", "V"],
            "rock": ["I", "bVII", "IV", "I"]
        }
    
    def _initialize_interval_weights(self) -> Dict[int, float]:
        """Initialize interval preference weights"""
        return {
            0: 0.1,   # Unison
            1: 0.3,   # Minor 2nd
            2: 0.8,   # Major 2nd
            3: 0.7,   # Minor 3rd
            4: 0.9,   # Major 3rd
            5: 0.8,   # Perfect 4th
            6: 0.4,   # Tritone
            7: 0.9,   # Perfect 5th
            8: 0.7,   # Minor 6th
            9: 0.8,   # Major 6th
            10: 0.6,  # Minor 7th
            11: 0.5,  # Major 7th
            12: 0.9   # Octave
        }
    
    async def get_scale_notes(self, key: str, mode: MelodyMode) -> List[int]:
        """Get scale notes for given key and mode"""
        try:
            # Convert key to root note number (C = 0)
            key_map = {
                'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
                'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
            }
            
            root = key_map.get(key, 0)
            pattern = self.scale_patterns[mode]
            
            # Transpose pattern to key
            scale_notes = [(root + interval) % 12 for interval in pattern]
            
            return scale_notes
            
        except Exception as e:
            logger.error(f"Error getting scale notes: {e}")
            return [0, 2, 4, 5, 7, 9, 11]  # Default to C major
    
    async def validate_melodic_intervals(self, melody_notes: List[int]) -> Dict[str, float]:
        """Validate melodic intervals for musicality"""
        try:
            if len(melody_notes) < 2:
                return {"interval_score": 1.0, "leap_ratio": 0.0, "direction_changes": 0}
            
            intervals = []
            direction_changes = 0
            large_leaps = 0
            
            for i in range(1, len(melody_notes)):
                interval = abs(melody_notes[i] - melody_notes[i-1])
                intervals.append(interval)
                
                # Count large leaps (> perfect 5th)
                if interval > 7:
                    large_leaps += 1
                
                # Count direction changes
                if i > 1:
                    prev_direction = melody_notes[i-1] - melody_notes[i-2]
                    current_direction = melody_notes[i] - melody_notes[i-1]
                    if (prev_direction > 0) != (current_direction > 0) and current_direction != 0:
                        direction_changes += 1
            
            # Calculate interval preference score
            interval_scores = [self.interval_weights.get(interval % 12, 0.5) for interval in intervals]
            avg_interval_score = np.mean(interval_scores) if interval_scores else 1.0
            
            # Calculate leap ratio
            leap_ratio = large_leaps / len(intervals) if intervals else 0.0
            
            # Calculate direction change ratio
            direction_change_ratio = direction_changes / max(1, len(melody_notes) - 2)
            
            return {
                "interval_score": avg_interval_score,
                "leap_ratio": leap_ratio,
                "direction_changes": direction_changes,
                "direction_change_ratio": direction_change_ratio,
                "avg_interval_size": np.mean(intervals) if intervals else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error validating melodic intervals: {e}")
            return {"interval_score": 0.5, "leap_ratio": 0.0, "direction_changes": 0}
    
    async def analyze_phrase_structure(self, melody_notes: List[int], 
                                     beats_per_measure: int = 4) -> Dict[str, Any]:
        """Analyze phrase structure of melody"""
        try:
            # Simplified phrase detection based on note patterns and rests
            phrase_boundaries = []
            current_phrase_start = 0
            
            # Look for natural phrase boundaries (rests, large leaps, repetitions)
            for i in range(1, len(melody_notes)):
                # Large leap might indicate phrase boundary
                if abs(melody_notes[i] - melody_notes[i-1]) > 7:
                    phrase_boundaries.append(i)
                
                # Every 8 beats (2 measures) is potential phrase boundary
                if i % (beats_per_measure * 2) == 0:
                    phrase_boundaries.append(i)
            
            # Ensure we have the end
            if phrase_boundaries[-1] != len(melody_notes):
                phrase_boundaries.append(len(melody_notes))
            
            # Calculate phrase lengths
            phrase_lengths = []
            start = 0
            for boundary in phrase_boundaries:
                phrase_lengths.append(boundary - start)
                start = boundary
            
            return {
                "phrase_count": len(phrase_lengths),
                "phrase_lengths": phrase_lengths,
                "phrase_boundaries": phrase_boundaries,
                "avg_phrase_length": np.mean(phrase_lengths) if phrase_lengths else 0,
                "phrase_regularity": np.std(phrase_lengths) if len(phrase_lengths) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing phrase structure: {e}")
            return {"phrase_count": 1, "phrase_lengths": [len(melody_notes)]}
    
    async def suggest_harmonization(self, melody_notes: List[int], 
                                  key: str, mode: MelodyMode) -> List[str]:
        """Suggest chord progression for melody harmonization"""
        try:
            scale_notes = await self.get_scale_notes(key, mode)
            
            # Simple harmonization: choose chords based on melody notes
            chords = []
            
            for note in melody_notes:
                note_in_scale = note % 12
                
                # Find which scale degree this is
                if note_in_scale in scale_notes:
                    scale_degree = scale_notes.index(note_in_scale)
                    
                    # Choose chord based on scale degree
                    if scale_degree == 0:    # Tonic
                        chords.append("I")
                    elif scale_degree == 1:  # Supertonic
                        chords.append("ii")
                    elif scale_degree == 2:  # Mediant
                        chords.append("iii")
                    elif scale_degree == 3:  # Subdominant
                        chords.append("IV")
                    elif scale_degree == 4:  # Dominant
                        chords.append("V")
                    elif scale_degree == 5:  # Submediant
                        chords.append("vi")
                    elif scale_degree == 6:  # Leading tone
                        chords.append("vii°")
                else:
                    # Chromatic note - use previous chord or tonic
                    chords.append(chords[-1] if chords else "I")
            
            return chords
            
        except Exception as e:
            logger.error(f"Error suggesting harmonization: {e}")
            return ["I"] * len(melody_notes)

class MelodyAnalyzer:
    """Melody quality analysis and metrics"""
    
    def __init__(self):
        self.theory_engine = MusicTheoryEngine()
    
    async def analyze_melody_quality(self, melody_notes: List[int], 
                                   parameters: MelodyParameters) -> Dict[str, float]:
        """Comprehensive melody quality analysis"""
        try:
            analysis = {}
            
            # Melodic contour analysis
            analysis.update(await self._analyze_contour(melody_notes))
            
            # Interval analysis
            interval_analysis = await self.theory_engine.validate_melodic_intervals(melody_notes)
            analysis.update(interval_analysis)
            
            # Phrase structure analysis
            phrase_analysis = await self.theory_engine.analyze_phrase_structure(melody_notes)
            analysis["phrase_regularity_score"] = 1.0 - min(1.0, phrase_analysis.get("phrase_regularity", 0) / 4.0)
            
            # Rhythmic variety (simplified)
            analysis["rhythmic_variety"] = await self._analyze_rhythmic_variety(melody_notes)
            
            # Scale adherence
            scale_notes = await self.theory_engine.get_scale_notes(parameters.key_signature, parameters.mode)
            analysis["scale_adherence"] = await self._analyze_scale_adherence(melody_notes, scale_notes)
            
            # Range utilization
            analysis["range_utilization"] = await self._analyze_range_utilization(melody_notes, parameters.melodic_range_semitones)
            
            # Overall quality score
            analysis["overall_quality"] = await self._calculate_overall_quality(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing melody quality: {e}")
            return {"overall_quality": 0.5}
    
    async def _analyze_contour(self, melody_notes: List[int]) -> Dict[str, float]:
        """Analyze melodic contour characteristics"""
        try:
            if len(melody_notes) < 3:
                return {"contour_smoothness": 1.0, "contour_variety": 0.0}
            
            # Calculate first and second derivatives
            first_diff = np.diff(melody_notes)
            second_diff = np.diff(first_diff)
            
            # Smoothness (low variance in differences)
            smoothness = 1.0 - min(1.0, np.var(first_diff) / 100.0)
            
            # Variety (presence of different contour shapes)
            up_movements = np.sum(first_diff > 0)
            down_movements = np.sum(first_diff < 0)
            static_movements = np.sum(first_diff == 0)
            
            total_movements = len(first_diff)
            if total_movements > 0:
                variety = 1.0 - abs(up_movements - down_movements) / total_movements
            else:
                variety = 0.0
            
            # Contour interest (presence of peaks and valleys)
            peaks = np.sum(np.logical_and(second_diff[:-1] > 0, second_diff[1:] < 0))
            valleys = np.sum(np.logical_and(second_diff[:-1] < 0, second_diff[1:] > 0))
            contour_interest = min(1.0, (peaks + valleys) / max(1, len(melody_notes) / 8))
            
            return {
                "contour_smoothness": smoothness,
                "contour_variety": variety,
                "contour_interest": contour_interest
            }
            
        except Exception as e:
            logger.error(f"Error analyzing contour: {e}")
            return {"contour_smoothness": 0.5, "contour_variety": 0.5, "contour_interest": 0.5}
    
    async def _analyze_rhythmic_variety(self, melody_notes: List[int]) -> float:
        """Analyze rhythmic variety (simplified analysis)"""
        try:
            # This is simplified - real implementation would analyze note durations
            # For now, we analyze note repetition patterns
            
            if len(melody_notes) < 4:
                return 0.5
            
            # Look for repeated patterns
            pattern_lengths = [2, 3, 4]
            repetition_score = 0.0
            
            for pattern_len in pattern_lengths:
                patterns = {}
                for i in range(len(melody_notes) - pattern_len + 1):
                    pattern = tuple(melody_notes[i:i + pattern_len])
                    patterns[pattern] = patterns.get(pattern, 0) + 1
                
                # Calculate repetition ratio
                if patterns:
                    max_repetitions = max(patterns.values())
                    repetition_ratio = max_repetitions / len(patterns)
                    repetition_score += (1.0 - repetition_ratio) / len(pattern_lengths)
            
            return max(0.0, min(1.0, repetition_score))
            
        except Exception as e:
            logger.error(f"Error analyzing rhythmic variety: {e}")
            return 0.5
    
    async def _analyze_scale_adherence(self, melody_notes: List[int], 
                                     scale_notes: List[int]) -> float:
        """Analyze how well melody adheres to scale"""
        try:
            if not melody_notes:
                return 1.0
            
            in_scale_count = 0
            for note in melody_notes:
                if (note % 12) in scale_notes:
                    in_scale_count += 1
            
            adherence = in_scale_count / len(melody_notes)
            return adherence
            
        except Exception as e:
            logger.error(f"Error analyzing scale adherence: {e}")
            return 0.5
    
    async def _analyze_range_utilization(self, melody_notes: List[int], 
                                       target_range: int) -> float:
        """Analyze how well melody utilizes the available range"""
        try:
            if not melody_notes:
                return 0.0
            
            actual_range = max(melody_notes) - min(melody_notes)
            utilization = min(1.0, actual_range / target_range)
            
            # Prefer moderate range utilization (not too compressed, not too wide)
            optimal_utilization = 0.7
            range_score = 1.0 - abs(utilization - optimal_utilization)
            
            return max(0.0, range_score)
            
        except Exception as e:
            logger.error(f"Error analyzing range utilization: {e}")
            return 0.5
    
    async def _calculate_overall_quality(self, analysis: Dict[str, float]) -> float:
        """Calculate overall quality score"""
        try:
            # Weights for different aspects
            weights = {
                "interval_score": 0.25,
                "contour_smoothness": 0.15,
                "contour_variety": 0.15,
                "contour_interest": 0.10,
                "scale_adherence": 0.15,
                "range_utilization": 0.10,
                "rhythmic_variety": 0.10
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in analysis:
                    weighted_score += analysis[metric] * weight
                    total_weight += weight
            
            if total_weight > 0:
                return weighted_score / total_weight
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating overall quality: {e}")
            return 0.5

class MelodyGenerator:
    """Main melody generation engine"""
    
    def __init__(self):
        # Neural networks
        self.transformer_model = MelodyTransformerNetwork()
        self.lstm_model = MelodyLSTMNetwork()
        
        # Analysis engines
        self.theory_engine = MusicTheoryEngine()
        self.analyzer = MelodyAnalyzer()
        
        # Generation templates
        self.style_templates = self._initialize_style_templates()
        
        # Vocabulary mapping
        self.note_to_token = self._create_note_vocabulary()
        self.token_to_note = {v: k for k, v in self.note_to_token.items()}
        
        logger.info("MelodyGenerator initialized successfully")
    
    def _initialize_style_templates(self) -> Dict[MelodyStyle, Dict[str, Any]]:
        """Initialize style-specific generation templates"""
        return {
            MelodyStyle.CLASSICAL: {
                "preferred_intervals": [2, 3, 4, 5, 7],
                "leap_probability": 0.2,
                "chromaticism": 0.1,
                "phrase_length_range": (4, 8),
                "rhythmic_complexity": 0.6
            },
            MelodyStyle.JAZZ: {
                "preferred_intervals": [2, 3, 4, 7, 9, 11],
                "leap_probability": 0.4,
                "chromaticism": 0.4,
                "phrase_length_range": (2, 6),
                "rhythmic_complexity": 0.8
            },
            MelodyStyle.POP: {
                "preferred_intervals": [2, 3, 4, 5],
                "leap_probability": 0.3,
                "chromaticism": 0.15,
                "phrase_length_range": (4, 8),
                "rhythmic_complexity": 0.4
            },
            MelodyStyle.ELECTRONIC: {
                "preferred_intervals": [1, 2, 7, 12],
                "leap_probability": 0.5,
                "chromaticism": 0.3,
                "phrase_length_range": (2, 4),
                "rhythmic_complexity": 0.3
            }
        }
    
    def _create_note_vocabulary(self) -> Dict[str, int]:
        """Create note vocabulary for neural network"""
        vocab = {"<PAD>": 0, "<START>": 1, "<END>": 2, "<REST>": 3}
        
        # Add MIDI notes (C0 to B8)
        for octave in range(9):
            for note_name in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
                midi_note = octave * 12 + ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].index(note_name)
                if midi_note <= 127:
                    vocab[f"{note_name}{octave}"] = len(vocab)
        
        return vocab
    
    async def generate_melody(self, parameters: MelodyParameters, 
                            style: MelodyStyle = MelodyStyle.POP,
                            complexity: MelodyComplexity = MelodyComplexity.MODERATE,
                            use_neural_network: bool = True) -> GeneratedMelody:
        """Generate melody with specified parameters"""
        try:
            start_time = datetime.now()
            melody_id = f"melody_{int(start_time.timestamp())}"
            
            # Generate melody notes
            if use_neural_network:
                melody_notes = await self._generate_with_neural_network(parameters, style, complexity)
            else:
                melody_notes = await self._generate_with_rules(parameters, style, complexity)
            
            # Convert to MIDI
            midi_data = await self._convert_to_midi(melody_notes, parameters)
            
            # Synthesize audio
            audio_synthesis = await self._synthesize_audio(melody_notes, parameters)
            
            # Harmonic analysis
            harmonic_analysis = await self._analyze_harmony(melody_notes, parameters)
            
            # Quality metrics
            quality_metrics = await self.analyzer.analyze_melody_quality(melody_notes, parameters)
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = GeneratedMelody(
                melody_notes=await self._format_melody_notes(melody_notes, parameters),
                midi_data=midi_data,
                audio_synthesis=audio_synthesis,
                harmonic_analysis=harmonic_analysis,
                quality_metrics=quality_metrics,
                generation_parameters=parameters,
                processing_time_seconds=processing_time,
                melody_id=melody_id,
                success=quality_metrics.get("overall_quality", 0.0) >= 0.6
            )
            
            logger.info(f"Generated melody {melody_id}: quality={quality_metrics.get('overall_quality', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating melody: {e}")
            raise
    
    async def _generate_with_neural_network(self, parameters: MelodyParameters,
                                          style: MelodyStyle, 
                                          complexity: MelodyComplexity) -> List[int]:
        """Generate melody using neural network"""
        try:
            # Convert parameters to tensor
            param_tensor = await self._parameters_to_tensor(parameters)
            
            # Style token
            style_map = {style: i for i, style in enumerate(MelodyStyle)}
            style_token = torch.tensor([style_map[style]])
            
            # Create prompt
            prompt_length = 4  # Start with 4 notes
            prompt_tokens = torch.tensor([[1] + [60, 62, 64, 65]])  # Start token + C, D, E, F
            
            # Calculate target length
            beats_per_bar = int(parameters.time_signature.split('/')[0])
            total_beats = parameters.length_bars * beats_per_bar
            target_length = int(total_beats * parameters.note_density)
            
            # Generate with transformer
            with torch.no_grad():
                generated_tokens = self.transformer_model.generate(
                    prompt_tokens=prompt_tokens,
                    style_token=style_token,
                    parameters=param_tensor,
                    max_length=target_length,
                    temperature=0.8,
                    top_k=40,
                    top_p=0.9
                )
            
            # Convert tokens back to notes
            melody_notes = []
            for token in generated_tokens[0]:
                if token.item() in self.token_to_note:
                    note_name = self.token_to_note[token.item()]
                    if note_name not in ["<PAD>", "<START>", "<END>", "<REST>"]:
                        # Extract MIDI note number from note name
                        midi_note = await self._note_name_to_midi(note_name)
                        melody_notes.append(midi_note)
            
            return melody_notes[:target_length]
            
        except Exception as e:
            logger.error(f"Error in neural network generation: {e}")
            # Fallback to rule-based generation
            return await self._generate_with_rules(parameters, style, complexity)
    
    async def _generate_with_rules(self, parameters: MelodyParameters,
                                 style: MelodyStyle,
                                 complexity: MelodyComplexity) -> List[int]:
        """Generate melody using music theory rules"""
        try:
            # Get scale notes
            scale_notes = await self.theory_engine.get_scale_notes(parameters.key_signature, parameters.mode)
            
            # Get style template
            style_template = self.style_templates.get(style, self.style_templates[MelodyStyle.POP])
            
            # Calculate melody length
            beats_per_bar = int(parameters.time_signature.split('/')[0])
            total_beats = parameters.length_bars * beats_per_bar
            melody_length = int(total_beats * parameters.note_density)
            
            # Starting note (tonic of the scale)
            root_note = 60  # Middle C
            key_offset = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].index(parameters.key_signature.replace("b", "#"))
            current_note = root_note + key_offset
            
            melody_notes = [current_note]
            
            # Generate subsequent notes
            for i in range(1, melody_length):
                # Choose next note based on style and theory
                next_note = await self._choose_next_note(
                    current_note, scale_notes, style_template, parameters, i, melody_length
                )
                
                melody_notes.append(next_note)
                current_note = next_note
            
            return melody_notes
            
        except Exception as e:
            logger.error(f"Error in rule-based generation: {e}")
            # Return simple scale
            return [60, 62, 64, 65, 67, 69, 71, 72]
    
    async def _choose_next_note(self, current_note: int, scale_notes: List[int],
                              style_template: Dict[str, Any], parameters: MelodyParameters,
                              position: int, total_length: int) -> int:
        """Choose next note based on music theory and style"""
        try:
            # Get preferred intervals for style
            preferred_intervals = style_template["preferred_intervals"]
            leap_probability = style_template["leap_probability"]
            chromaticism = min(style_template["chromaticism"], parameters.chromaticism)
            
            # Calculate position in phrase
            phrase_position = position % 8  # Assume 8-beat phrases
            
            # Tendency to resolve at phrase endings
            if phrase_position == 7:  # End of phrase
                # Prefer resolution to tonic or stable tones
                tonic_note = current_note - (current_note % 12) + scale_notes[0]
                return tonic_note
            
            # Random choice with weighted probabilities
            candidates = []
            weights = []
            
            for interval in range(-12, 13):  # One octave range
                candidate_note = current_note + interval
                
                # Check if within desired range
                if abs(candidate_note - current_note) > parameters.melodic_range_semitones // 2:
                    continue
                
                # Check if note is in scale (or chromatic)
                candidate_note_class = candidate_note % 12
                if candidate_note_class in scale_notes:
                    weight = 1.0
                elif np.random.random() < chromaticism:
                    weight = 0.3  # Lower weight for chromatic notes
                else:
                    continue
                
                # Adjust weight based on interval preference
                abs_interval = abs(interval)
                if abs_interval in preferred_intervals:
                    weight *= 2.0
                
                # Reduce weight for large leaps
                if abs_interval > 7:
                    weight *= leap_probability
                
                # Avoid staying on same note too often
                if interval == 0:
                    weight *= 0.3
                
                candidates.append(candidate_note)
                weights.append(weight)
            
            # Choose note based on weights
            if candidates and weights:
                weights = np.array(weights)
                weights = weights / np.sum(weights)  # Normalize
                chosen_note = np.random.choice(candidates, p=weights)
                return int(chosen_note)
            else:
                # Fallback: step-wise motion
                return current_note + np.random.choice([-2, -1, 1, 2])
                
        except Exception as e:
            logger.error(f"Error choosing next note: {e}")
            return current_note + 1
    
    async def _parameters_to_tensor(self, parameters: MelodyParameters) -> torch.Tensor:
        """Convert parameters to tensor for neural network"""
        try:
            # Normalize parameters to 0-1 range
            param_values = [
                ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].index(parameters.key_signature.replace("b", "#")) / 11.0,
                list(MelodyMode).index(parameters.mode) / len(MelodyMode),
                (parameters.tempo_bpm - 60) / 140.0,  # Normalize 60-200 BPM
                parameters.length_bars / 32.0,  # Normalize up to 32 bars
                parameters.note_density,
                parameters.melodic_range_semitones / 48.0,  # Normalize up to 4 octaves
                parameters.rhythmic_complexity,
                parameters.harmonic_complexity,
                (parameters.emotional_valence + 1) / 2.0,  # -1 to 1 -> 0 to 1
                parameters.energy_level,
                parameters.chromaticism,
                1.0 if parameters.time_signature == "4/4" else 0.5  # Simplified time sig encoding
            ]
            
            return torch.tensor(param_values, dtype=torch.float32).unsqueeze(0)
            
        except Exception as e:
            logger.error(f"Error converting parameters to tensor: {e}")
            return torch.zeros(1, 12)
    
    async def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI number"""
        try:
            if len(note_name) < 2:
                return 60  # Default to middle C
            
            note_part = note_name[:-1]  # Remove octave
            octave = int(note_name[-1])
            
            note_values = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, 
                          "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
            
            note_value = note_values.get(note_part, 0)
            midi_number = octave * 12 + note_value
            
            return max(0, min(127, midi_number))
            
        except Exception:
            return 60
    
    async def _convert_to_midi(self, melody_notes: List[int], 
                             parameters: MelodyParameters) -> bytes:
        """Convert melody notes to MIDI data"""
        try:
            # Create MIDI file
            mid = mido.MidiFile()
            track = mido.MidiTrack()
            mid.tracks.append(track)
            
            # Set tempo
            tempo = mido.bpm2tempo(parameters.tempo_bpm)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
            
            # Add notes
            ticks_per_beat = mid.ticks_per_beat
            note_duration = ticks_per_beat // 2  # Eighth notes
            
            for note in melody_notes:
                # Note on
                track.append(mido.Message('note_on', note=note, velocity=64, time=0))
                # Note off
                track.append(mido.Message('note_off', note=note, velocity=64, time=note_duration))
            
            # Convert to bytes
            return mid.to_bytes()
            
        except Exception as e:
            logger.error(f"Error converting to MIDI: {e}")
            return b''
    
    async def _synthesize_audio(self, melody_notes: List[int], 
                              parameters: MelodyParameters,
                              sample_rate: int = 44100) -> np.ndarray:
        """Synthesize audio from melody notes"""
        try:
            # Calculate note duration in samples
            note_duration_beats = 0.5  # Eighth note
            note_duration_seconds = (60.0 / parameters.tempo_bpm) * note_duration_beats
            note_duration_samples = int(note_duration_seconds * sample_rate)
            
            # Generate audio
            audio = np.array([])
            
            for note in melody_notes:
                # Convert MIDI note to frequency
                frequency = 440.0 * (2 ** ((note - 69) / 12.0))
                
                # Generate sine wave for note
                t = np.linspace(0, note_duration_seconds, note_duration_samples, False)
                
                # Simple envelope (attack, sustain, decay)
                envelope = np.ones_like(t)
                attack_samples = int(0.1 * note_duration_samples)
                decay_samples = int(0.2 * note_duration_samples)
                
                # Attack
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                # Decay
                envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
                
                # Generate tone
                tone = np.sin(2 * np.pi * frequency * t) * envelope * 0.3
                
                # Add to audio
                audio = np.concatenate([audio, tone])
            
            return audio.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error synthesizing audio: {e}")
            return np.array([])
    
    async def _analyze_harmony(self, melody_notes: List[int], 
                             parameters: MelodyParameters) -> Dict[str, Any]:
        """Analyze harmonic implications of melody"""
        try:
            # Get suggested chord progression
            chords = await self.theory_engine.suggest_harmonization(
                melody_notes, parameters.key_signature, parameters.mode
            )
            
            # Analyze harmonic rhythm
            chord_changes = len(set(chords))
            harmonic_rhythm = chord_changes / len(chords) if chords else 0.0
            
            # Analyze tonal stability
            scale_notes = await self.theory_engine.get_scale_notes(parameters.key_signature, parameters.mode)
            tonic_emphasis = sum(1 for note in melody_notes if (note % 12) == scale_notes[0]) / len(melody_notes)
            
            return {
                "suggested_chords": chords,
                "chord_changes": chord_changes,
                "harmonic_rhythm": harmonic_rhythm,
                "tonic_emphasis": tonic_emphasis,
                "key_center_stability": tonic_emphasis,
                "harmonic_complexity_score": min(1.0, chord_changes / (len(melody_notes) / 4))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing harmony: {e}")
            return {"suggested_chords": [], "harmonic_complexity_score": 0.5}
    
    async def _format_melody_notes(self, melody_notes: List[int], 
                                 parameters: MelodyParameters) -> List[Dict[str, Any]]:
        """Format melody notes with timing and musical information"""
        try:
            formatted_notes = []
            
            # Calculate timing
            beat_duration = 60.0 / parameters.tempo_bpm
            note_duration = beat_duration * 0.5  # Eighth notes
            
            for i, note in enumerate(melody_notes):
                # Convert MIDI to note name
                octave = note // 12
                note_class = note % 12
                note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                note_name = f"{note_names[note_class]}{octave}"
                
                formatted_note = {
                    "midi_note": note,
                    "note_name": note_name,
                    "frequency": 440.0 * (2 ** ((note - 69) / 12.0)),
                    "start_time": i * note_duration,
                    "duration": note_duration,
                    "velocity": 64,
                    "position_in_sequence": i
                }
                
                formatted_notes.append(formatted_note)
            
            return formatted_notes
            
        except Exception as e:
            logger.error(f"Error formatting melody notes: {e}")
            return []
    
    async def harmonize_melody(self, melody_notes: List[int], 
                             parameters: MelodyParameters) -> Dict[str, Any]:
        """Generate harmonization for melody"""
        try:
            # Get chord progression
            chord_progression = await self.theory_engine.suggest_harmonization(
                melody_notes, parameters.key_signature, parameters.mode
            )
            
            # Generate bass line
            bass_line = await self._generate_bass_line(chord_progression, parameters)
            
            # Generate inner voices (simplified)
            inner_voices = await self._generate_inner_voices(melody_notes, chord_progression, parameters)
            
            return {
                "chord_progression": chord_progression,
                "bass_line": bass_line,
                "inner_voices": inner_voices,
                "full_arrangement": {
                    "melody": melody_notes,
                    "bass": bass_line,
                    "harmony": inner_voices
                }
            }
            
        except Exception as e:
            logger.error(f"Error harmonizing melody: {e}")
            return {"chord_progression": [], "bass_line": [], "inner_voices": []}
    
    async def _generate_bass_line(self, chord_progression: List[str], 
                                parameters: MelodyParameters) -> List[int]:
        """Generate bass line from chord progression"""
        try:
            bass_line = []
            
            # Get root note of key
            key_offset = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"].index(parameters.key_signature.replace("b", "#"))
            bass_root = 36 + key_offset  # Bass clef C
            
            scale_notes = await self.theory_engine.get_scale_notes(parameters.key_signature, parameters.mode)
            
            for chord in chord_progression:
                # Simple bass note selection based on chord
                if chord == "I":
                    bass_note = bass_root + scale_notes[0]
                elif chord == "ii":
                    bass_note = bass_root + scale_notes[1]
                elif chord == "iii":
                    bass_note = bass_root + scale_notes[2]
                elif chord == "IV":
                    bass_note = bass_root + scale_notes[3]
                elif chord == "V":
                    bass_note = bass_root + scale_notes[4]
                elif chord == "vi":
                    bass_note = bass_root + scale_notes[5]
                else:
                    bass_note = bass_root + scale_notes[0]  # Default to tonic
                
                bass_line.append(bass_note)
            
            return bass_line
            
        except Exception as e:
            logger.error(f"Error generating bass line: {e}")
            return []
    
    async def _generate_inner_voices(self, melody: List[int], 
                                   chords: List[str], 
                                   parameters: MelodyParameters) -> List[List[int]]:
        """Generate inner harmony voices"""
        try:
            # Simplified two-voice harmony
            alto_voice = []
            tenor_voice = []
            
            scale_notes = await self.theory_engine.get_scale_notes(parameters.key_signature, parameters.mode)
            
            for i, (melody_note, chord) in enumerate(zip(melody, chords)):
                # Generate alto note (thirds below melody)
                alto_note = melody_note - 4  # Major/minor third below
                alto_voice.append(alto_note)
                
                # Generate tenor note (fifth below melody)
                tenor_note = melody_note - 7  # Perfect fifth below
                tenor_voice.append(tenor_note)
            
            return [alto_voice, tenor_voice]
            
        except Exception as e:
            logger.error(f"Error generating inner voices: {e}")
            return [[], []]

# Processing classes for export
MelodyAnalyzer = MelodyAnalyzer
MelodyComposer = MelodyGenerator
MelodyHarmonizer = MelodyGenerator

# Export classes
__all__ = [
    "MelodyGenerator",
    "MelodyAnalyzer",
    "MelodyComposer", 
    "MelodyHarmonizer",
    "MelodyStyle",
    "MelodyComplexity",
    "MelodyMode",
    "MelodyParameters",
    "GeneratedMelody",
    "MusicTheoryEngine",
    "MelodyTransformerNetwork",
    "MelodyLSTMNetwork"
]