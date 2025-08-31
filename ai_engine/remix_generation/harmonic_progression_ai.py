#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent Harmonic Progression AI
================================================================================
Module: ai_engine/remix_generation/harmonic_progression_ai.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Harmonic Analysis AI (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Analyseur et générateur de progressions harmoniques IA ultra-avancé
TECHNOLOGIES: Deep Learning, Music Theory, Harmonic Analysis, Chord Progression Generation
LOGIQUE MÉTIER: Musical context → Harmonic analysis → Progression generation → Voice leading → Quality validation
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
import music21
from music21 import chord, key, roman, stream, pitch, interval, scale
import librosa
from scipy import signal

# Configure logging
logger = logging.getLogger(__name__)

class HarmonicStyle(Enum):
    """Harmonic progression styles"""
    CLASSICAL = "classical"
    JAZZ = "jazz"
    POP = "pop"
    ROCK = "rock"
    BLUES = "blues"
    FOLK = "folk"
    ELECTRONIC = "electronic"
    MODAL = "modal"
    CONTEMPORARY = "contemporary"
    GOSPEL = "gospel"
    LATIN = "latin"
    AMBIENT = "ambient"

class ChordQuality(Enum):
    """Chord quality types"""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    MAJOR_SEVENTH = "major_seventh"
    MINOR_SEVENTH = "minor_seventh"
    DOMINANT_SEVENTH = "dominant_seventh"
    HALF_DIMINISHED = "half_diminished"
    FULLY_DIMINISHED = "fully_diminished"
    SUSPENDED_SECOND = "suspended_second"
    SUSPENDED_FOURTH = "suspended_fourth"
    ADD_NINE = "add_nine"
    MAJOR_NINTH = "major_ninth"
    MINOR_NINTH = "minor_ninth"

class HarmonicFunction(Enum):
    """Harmonic function analysis"""
    TONIC = "tonic"
    SUBDOMINANT = "subdominant"
    DOMINANT = "dominant"
    PREDOMINANT = "predominant"
    SECONDARY_DOMINANT = "secondary_dominant"
    CHROMATIC_MEDIANT = "chromatic_mediant"
    NEAPOLITAN = "neapolitan"
    AUGMENTED_SIXTH = "augmented_sixth"

class VoiceLeadingType(Enum):
    """Voice leading movement types"""
    STEPWISE = "stepwise"
    LEAP = "leap"
    STATIC = "static"
    CONTRARY = "contrary"
    PARALLEL = "parallel"
    OBLIQUE = "oblique"

@dataclass
class ChordData:
    """Comprehensive chord data structure"""
    root_note: str
    quality: ChordQuality
    inversion: int = 0
    bass_note: Optional[str] = None
    extensions: List[str] = field(default_factory=list)
    alterations: List[str] = field(default_factory=list)
    chord_tones: List[str] = field(default_factory=list)
    midi_notes: List[int] = field(default_factory=list)
    harmonic_function: Optional[HarmonicFunction] = None
    roman_numeral: Optional[str] = None
    voice_leading_score: float = 0.0

@dataclass
class HarmonicProgression:
    """Generated harmonic progression"""
    progression_id: str
    chords: List[ChordData]
    key_center: str
    mode: str
    progression_length: int
    harmonic_rhythm: List[float]  # Duration of each chord
    voice_leading_analysis: Dict[str, Any]
    tension_curve: List[float]
    modulations: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]
    generation_style: HarmonicStyle
    processing_time_seconds: float
    success: bool

@dataclass
class HarmonicParameters:
    """Parameters for harmonic progression generation"""
    key_signature: str = "C"
    mode: str = "major"
    progression_length: int = 8
    chord_rhythm: str = "whole_notes"  # whole_notes, half_notes, mixed
    voice_leading_smoothness: float = 0.8
    harmonic_complexity: float = 0.5
    use_extensions: bool = True
    allow_inversions: bool = True
    modulation_frequency: float = 0.1
    tension_profile: str = "classical"  # classical, modern, jazz
    avoid_parallel_fifths: bool = True
    prefer_common_tones: bool = True

class HarmonicTransformerNetwork(nn.Module):
    """Transformer network for harmonic progression generation"""
    
    def __init__(self, vocab_size: int = 256, d_model: int = 256, 
                 nhead: int = 8, num_layers: int = 6):
        super(HarmonicTransformerNetwork, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # Chord embeddings
        self.chord_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(1000, d_model)  # Max sequence length
        
        # Style conditioning
        self.style_embedding = nn.Embedding(len(HarmonicStyle), d_model)
        
        # Parameter conditioning
        self.param_projection = nn.Linear(10, d_model)  # 10 harmonic parameters
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output layers
        self.chord_predictor = nn.Linear(d_model, vocab_size)
        self.function_predictor = nn.Linear(d_model, len(HarmonicFunction))
        self.tension_predictor = nn.Linear(d_model, 1)
        
        # Voice leading network
        self.voice_leading_net = nn.Sequential(
            nn.Linear(d_model * 2, 128),  # Two consecutive chords
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Voice leading quality score
        )
    
    def forward(self, chord_sequence, style_token=None, parameters=None):
        batch_size, seq_len = chord_sequence.shape
        
        # Chord embeddings
        chord_embeds = self.chord_embedding(chord_sequence)
        
        # Position embeddings
        positions = torch.arange(seq_len).unsqueeze(0).expand(batch_size, -1)
        pos_embeds = self.position_embedding(positions)
        
        # Combine embeddings
        embeddings = chord_embeds + pos_embeds
        
        # Add style conditioning
        if style_token is not None:
            style_embeds = self.style_embedding(style_token).unsqueeze(1)
            embeddings = embeddings + style_embeds
        
        # Add parameter conditioning
        if parameters is not None:
            param_embeds = self.param_projection(parameters).unsqueeze(1)
            embeddings = embeddings + param_embeds
        
        # Transformer processing
        embeddings = embeddings.transpose(0, 1)  # (seq_len, batch, d_model)
        
        # Causal mask for autoregressive generation
        mask = self._generate_square_subsequent_mask(seq_len)
        if chord_sequence.is_cuda:
            mask = mask.cuda()
        
        transformer_output = self.transformer(embeddings, mask=mask)
        transformer_output = transformer_output.transpose(0, 1)  # (batch, seq_len, d_model)
        
        # Predictions
        chord_logits = self.chord_predictor(transformer_output)
        function_logits = self.function_predictor(transformer_output)
        tension_scores = self.tension_predictor(transformer_output).squeeze(-1)
        
        # Voice leading analysis for consecutive chords
        voice_leading_scores = []
        for i in range(seq_len - 1):
            chord_pair = torch.cat([transformer_output[:, i], transformer_output[:, i+1]], dim=1)
            vl_score = self.voice_leading_net(chord_pair)
            voice_leading_scores.append(vl_score)
        
        if voice_leading_scores:
            voice_leading_scores = torch.stack(voice_leading_scores, dim=1)
        else:
            voice_leading_scores = torch.zeros(batch_size, 0, 1)
        
        return chord_logits, function_logits, tension_scores, voice_leading_scores
    
    def _generate_square_subsequent_mask(self, sz):
        """Generate causal mask"""
        mask = torch.triu(torch.ones(sz, sz)) == 1
        mask = mask.transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

class ChordVocabulary:
    """Chord vocabulary for neural network"""
    
    def __init__(self):
        self.chord_to_token = {}
        self.token_to_chord = {}
        self._build_vocabulary()
    
    def _build_vocabulary(self):
        """Build comprehensive chord vocabulary"""
        token_id = 0
        
        # Special tokens
        special_tokens = ["<PAD>", "<START>", "<END>", "<UNK>"]
        for token in special_tokens:
            self.chord_to_token[token] = token_id
            self.token_to_chord[token_id] = token
            token_id += 1
        
        # Note names
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        # Basic triads
        for root in notes:
            for quality in ["", "m", "dim", "aug"]:
                chord_symbol = f"{root}{quality}"
                self.chord_to_token[chord_symbol] = token_id
                self.token_to_chord[token_id] = chord_symbol
                token_id += 1
        
        # Seventh chords
        for root in notes:
            for quality in ["maj7", "m7", "7", "m7b5", "dim7", "mMaj7"]:
                chord_symbol = f"{root}{quality}"
                self.chord_to_token[chord_symbol] = token_id
                self.token_to_chord[token_id] = chord_symbol
                token_id += 1
        
        # Extended chords
        for root in notes:
            for ext in ["add9", "sus2", "sus4", "9", "m9", "maj9", "11", "13"]:
                chord_symbol = f"{root}{ext}"
                self.chord_to_token[chord_symbol] = token_id
                self.token_to_chord[token_id] = chord_symbol
                token_id += 1
    
    def encode_chord(self, chord_symbol: str) -> int:
        """Encode chord symbol to token"""
        return self.chord_to_token.get(chord_symbol, self.chord_to_token["<UNK>"])
    
    def decode_token(self, token: int) -> str:
        """Decode token to chord symbol"""
        return self.token_to_chord.get(token, "<UNK>")

class HarmonyAnalyzer:
    """Advanced harmonic analysis engine"""
    
    def __init__(self):
        self.chord_vocab = ChordVocabulary()
        self.functional_harmony_rules = self._initialize_functional_rules()
        self.voice_leading_rules = self._initialize_voice_leading_rules()
    
    def _initialize_functional_rules(self) -> Dict[str, Any]:
        """Initialize functional harmony rules"""
        return {
            "major_key_functions": {
                "I": HarmonicFunction.TONIC,
                "ii": HarmonicFunction.SUBDOMINANT,
                "iii": HarmonicFunction.TONIC,
                "IV": HarmonicFunction.SUBDOMINANT,
                "V": HarmonicFunction.DOMINANT,
                "vi": HarmonicFunction.TONIC,
                "vii°": HarmonicFunction.DOMINANT
            },
            "minor_key_functions": {
                "i": HarmonicFunction.TONIC,
                "ii°": HarmonicFunction.SUBDOMINANT,
                "III": HarmonicFunction.TONIC,
                "iv": HarmonicFunction.SUBDOMINANT,
                "V": HarmonicFunction.DOMINANT,
                "VI": HarmonicFunction.SUBDOMINANT,
                "vii°": HarmonicFunction.DOMINANT
            },
            "common_progressions": {
                "classical": ["I", "vi", "IV", "V"],
                "pop": ["I", "V", "vi", "IV"],
                "jazz": ["ii", "V", "I", "vi"],
                "blues": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]
            }
        }
    
    def _initialize_voice_leading_rules(self) -> Dict[str, Any]:
        """Initialize voice leading rules"""
        return {
            "smooth_voice_leading": {
                "max_leap_semitones": 7,
                "prefer_stepwise": True,
                "prefer_common_tones": True
            },
            "forbidden_parallels": {
                "parallel_fifths": True,
                "parallel_octaves": True,
                "parallel_unisons": True
            },
            "resolution_tendencies": {
                "leading_tone_up": True,
                "seventh_down": True,
                "augmented_intervals_resolve_outward": True,
                "diminished_intervals_resolve_inward": True
            }
        }
    
    async def analyze_chord_from_audio(self, audio: np.ndarray, 
                                     sample_rate: int = 44100) -> ChordData:
        """Analyze chord from audio signal"""
        try:
            # Chromagram analysis
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Find dominant pitch classes
            dominant_pitches = np.argsort(chroma_mean)[-4:]  # Top 4 pitch classes
            
            # Map to note names
            note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            chord_notes = [note_names[i] for i in dominant_pitches]
            
            # Determine root and quality
            root_note, quality = await self._determine_chord_quality(chord_notes)
            
            # Convert to MIDI notes
            midi_notes = await self._notes_to_midi(chord_notes)
            
            return ChordData(
                root_note=root_note,
                quality=quality,
                chord_tones=chord_notes,
                midi_notes=midi_notes
            )
            
        except Exception as e:
            logger.error(f"Error analyzing chord from audio: {e}")
            return ChordData(root_note="C", quality=ChordQuality.MAJOR)
    
    async def _determine_chord_quality(self, notes: List[str]) -> Tuple[str, ChordQuality]:
        """Determine chord root and quality from notes"""
        try:
            if len(notes) < 3:
                return notes[0] if notes else "C", ChordQuality.MAJOR
            
            # Convert notes to pitch class integers
            note_to_pc = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
                         "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
            
            pitch_classes = [note_to_pc[note] for note in notes if note in note_to_pc]
            
            # Try each note as potential root
            best_root = notes[0]
            best_quality = ChordQuality.MAJOR
            best_score = 0
            
            for root_note in notes:
                if root_note not in note_to_pc:
                    continue
                    
                root_pc = note_to_pc[root_note]
                intervals = [(pc - root_pc) % 12 for pc in pitch_classes]
                intervals.sort()
                
                # Check for chord patterns
                quality, score = await self._match_chord_pattern(intervals)
                
                if score > best_score:
                    best_root = root_note
                    best_quality = quality
                    best_score = score
            
            return best_root, best_quality
            
        except Exception as e:
            logger.error(f"Error determining chord quality: {e}")
            return "C", ChordQuality.MAJOR
    
    async def _match_chord_pattern(self, intervals: List[int]) -> Tuple[ChordQuality, float]:
        """Match interval pattern to chord quality"""
        try:
            # Chord patterns (intervals from root)
            patterns = {
                ChordQuality.MAJOR: [0, 4, 7],
                ChordQuality.MINOR: [0, 3, 7],
                ChordQuality.DIMINISHED: [0, 3, 6],
                ChordQuality.AUGMENTED: [0, 4, 8],
                ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
                ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
                ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
                ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
                ChordQuality.FULLY_DIMINISHED: [0, 3, 6, 9]
            }
            
            best_quality = ChordQuality.MAJOR
            best_score = 0
            
            for quality, pattern in patterns.items():
                # Calculate match score
                matches = sum(1 for interval in pattern if interval in intervals)
                score = matches / len(pattern)
                
                # Bonus for exact match
                if set(pattern).issubset(set(intervals)):
                    score += 0.5
                
                if score > best_score:
                    best_quality = quality
                    best_score = score
            
            return best_quality, best_score
            
        except Exception as e:
            logger.error(f"Error matching chord pattern: {e}")
            return ChordQuality.MAJOR, 0.5
    
    async def _notes_to_midi(self, notes: List[str]) -> List[int]:
        """Convert note names to MIDI numbers"""
        try:
            note_to_midi = {"C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65,
                           "F#": 66, "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71}
            
            return [note_to_midi.get(note, 60) for note in notes]
            
        except Exception as e:
            logger.error(f"Error converting notes to MIDI: {e}")
            return [60, 64, 67]  # C major triad
    
    async def analyze_harmonic_function(self, chord: ChordData, 
                                      key_center: str, mode: str) -> HarmonicFunction:
        """Analyze harmonic function of chord in key"""
        try:
            # Convert to roman numeral analysis
            roman_numeral = await self._chord_to_roman(chord, key_center, mode)
            
            # Look up function
            if mode == "major":
                functions = self.functional_harmony_rules["major_key_functions"]
            else:
                functions = self.functional_harmony_rules["minor_key_functions"]
            
            return functions.get(roman_numeral, HarmonicFunction.TONIC)
            
        except Exception as e:
            logger.error(f"Error analyzing harmonic function: {e}")
            return HarmonicFunction.TONIC
    
    async def _chord_to_roman(self, chord: ChordData, key_center: str, mode: str) -> str:
        """Convert chord to roman numeral in key"""
        try:
            # Simplified roman numeral conversion
            note_to_scale_degree = {
                "C": 1, "C#": 1, "D": 2, "D#": 2, "E": 3, "F": 4,
                "F#": 4, "G": 5, "G#": 5, "A": 6, "A#": 6, "B": 7
            }
            
            # Get scale degree of chord root
            key_offset = note_to_scale_degree.get(key_center, 1)
            chord_offset = note_to_scale_degree.get(chord.root_note, 1)
            scale_degree = ((chord_offset - key_offset) % 7) + 1
            
            # Convert to roman numeral
            roman_numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
            
            if scale_degree <= len(roman_numerals):
                roman = roman_numerals[scale_degree - 1]
                
                # Adjust for minor chords
                if chord.quality == ChordQuality.MINOR:
                    roman = roman.lower()
                elif chord.quality == ChordQuality.DIMINISHED:
                    roman = roman.lower() + "°"
                elif chord.quality == ChordQuality.AUGMENTED:
                    roman = roman + "+"
                
                return roman
            
            return "I"
            
        except Exception as e:
            logger.error(f"Error converting to roman numeral: {e}")
            return "I"
    
    async def analyze_voice_leading(self, chord1: ChordData, 
                                  chord2: ChordData) -> Dict[str, Any]:
        """Analyze voice leading between two chords"""
        try:
            analysis = {}
            
            # Calculate voice movements
            movements = []
            for i, note1 in enumerate(chord1.midi_notes):
                if i < len(chord2.midi_notes):
                    note2 = chord2.midi_notes[i]
                    movement = note2 - note1
                    movements.append(movement)
            
            # Analyze movement types
            stepwise_count = sum(1 for m in movements if abs(m) <= 2)
            leap_count = sum(1 for m in movements if abs(m) > 2)
            static_count = sum(1 for m in movements if m == 0)
            
            analysis["stepwise_motion"] = stepwise_count / len(movements) if movements else 0
            analysis["leap_motion"] = leap_count / len(movements) if movements else 0
            analysis["static_motion"] = static_count / len(movements) if movements else 0
            
            # Check for parallel motion
            analysis["parallel_motion"] = await self._check_parallel_motion(chord1, chord2)
            
            # Calculate smoothness score
            if movements:
                avg_movement = np.mean([abs(m) for m in movements])
                analysis["smoothness_score"] = max(0, 1 - avg_movement / 12)  # Normalize by octave
            else:
                analysis["smoothness_score"] = 1.0
            
            # Overall voice leading quality
            analysis["voice_leading_quality"] = (
                analysis["smoothness_score"] * 0.4 +
                analysis["stepwise_motion"] * 0.3 +
                (1 - analysis["parallel_motion"]) * 0.3
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing voice leading: {e}")
            return {"voice_leading_quality": 0.5}
    
    async def _check_parallel_motion(self, chord1: ChordData, chord2: ChordData) -> float:
        """Check for parallel motion between chords"""
        try:
            if len(chord1.midi_notes) < 2 or len(chord2.midi_notes) < 2:
                return 0.0
            
            parallel_count = 0
            total_pairs = 0
            
            # Check all voice pairs
            for i in range(len(chord1.midi_notes)):
                for j in range(i + 1, len(chord1.midi_notes)):
                    if i < len(chord2.midi_notes) and j < len(chord2.midi_notes):
                        # Calculate intervals
                        interval1 = chord1.midi_notes[j] - chord1.midi_notes[i]
                        interval2 = chord2.midi_notes[j] - chord2.midi_notes[i]
                        
                        # Movement in same direction with same interval = parallel
                        if interval1 == interval2 and abs(interval1) in [7, 12]:  # Fifths or octaves
                            parallel_count += 1
                        
                        total_pairs += 1
            
            return parallel_count / total_pairs if total_pairs > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error checking parallel motion: {e}")
            return 0.0

class HarmonicProgressionAI:
    """Main harmonic progression generation AI"""
    
    def __init__(self):
        # Neural networks
        self.transformer_model = HarmonicTransformerNetwork()
        self.harmony_analyzer = HarmonyAnalyzer()
        
        # Style templates
        self.progression_templates = self._initialize_progression_templates()
        
        # Generation history
        self.generation_history = []
        
        logger.info("HarmonicProgressionAI initialized successfully")
    
    def _initialize_progression_templates(self) -> Dict[HarmonicStyle, Dict[str, Any]]:
        """Initialize style-specific progression templates"""
        return {
            HarmonicStyle.CLASSICAL: {
                "common_progressions": [
                    ["I", "vi", "IV", "V"],
                    ["I", "IV", "V", "I"],
                    ["vi", "IV", "I", "V"],
                    ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]
                ],
                "chord_qualities": {
                    "seventh_frequency": 0.3,
                    "extensions_frequency": 0.1,
                    "inversions_frequency": 0.4
                },
                "voice_leading_strictness": 0.9
            },
            HarmonicStyle.JAZZ: {
                "common_progressions": [
                    ["ii", "V", "I", "vi"],
                    ["I", "vi", "ii", "V"],
                    ["iii", "vi", "ii", "V"],
                    ["I", "I7", "IV", "iv", "I", "V", "I"]
                ],
                "chord_qualities": {
                    "seventh_frequency": 0.8,
                    "extensions_frequency": 0.6,
                    "inversions_frequency": 0.5
                },
                "voice_leading_strictness": 0.6
            },
            HarmonicStyle.POP: {
                "common_progressions": [
                    ["I", "V", "vi", "IV"],
                    ["vi", "IV", "I", "V"],
                    ["I", "vi", "IV", "V"],
                    ["I", "iii", "vi", "IV"]
                ],
                "chord_qualities": {
                    "seventh_frequency": 0.2,
                    "extensions_frequency": 0.1,
                    "inversions_frequency": 0.3
                },
                "voice_leading_strictness": 0.5
            },
            HarmonicStyle.BLUES: {
                "common_progressions": [
                    ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
                    ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "I7"]
                ],
                "chord_qualities": {
                    "seventh_frequency": 0.9,
                    "extensions_frequency": 0.3,
                    "inversions_frequency": 0.2
                },
                "voice_leading_strictness": 0.3
            }
        }
    
    async def generate_harmonic_progression(self, style: HarmonicStyle,
                                          parameters: HarmonicParameters,
                                          use_neural_network: bool = True) -> HarmonicProgression:
        """Generate harmonic progression with specified style and parameters"""
        try:
            start_time = datetime.now()
            progression_id = f"harmony_{int(start_time.timestamp())}"
            
            # Generate chord progression
            if use_neural_network:
                chords = await self._generate_with_neural_network(style, parameters)
            else:
                chords = await self._generate_with_templates(style, parameters)
            
            # Analyze harmonic functions
            for chord in chords:
                chord.harmonic_function = await self.harmony_analyzer.analyze_harmonic_function(
                    chord, parameters.key_signature, parameters.mode
                )
            
            # Generate harmonic rhythm
            harmonic_rhythm = await self._generate_harmonic_rhythm(parameters)
            
            # Voice leading analysis
            voice_leading_analysis = await self._analyze_progression_voice_leading(chords)
            
            # Calculate tension curve
            tension_curve = await self._calculate_tension_curve(chords, parameters)
            
            # Detect modulations
            modulations = await self._detect_modulations(chords, parameters.key_signature)
            
            # Quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                chords, voice_leading_analysis, parameters
            )
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = HarmonicProgression(
                progression_id=progression_id,
                chords=chords,
                key_center=parameters.key_signature,
                mode=parameters.mode,
                progression_length=len(chords),
                harmonic_rhythm=harmonic_rhythm,
                voice_leading_analysis=voice_leading_analysis,
                tension_curve=tension_curve,
                modulations=modulations,
                quality_metrics=quality_metrics,
                generation_style=style,
                processing_time_seconds=processing_time,
                success=quality_metrics.get("overall_quality", 0.0) >= 0.6
            )
            
            # Store in history
            self.generation_history.append({
                "timestamp": start_time.isoformat(),
                "progression_id": progression_id,
                "style": style.value,
                "key": parameters.key_signature,
                "mode": parameters.mode,
                "quality": quality_metrics.get("overall_quality", 0.0)
            })
            
            logger.info(f"Generated harmonic progression {progression_id}: quality={quality_metrics.get('overall_quality', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating harmonic progression: {e}")
            raise
    
    async def _generate_with_neural_network(self, style: HarmonicStyle,
                                          parameters: HarmonicParameters) -> List[ChordData]:
        """Generate progression using neural network"""
        try:
            # Convert parameters to tensor
            param_tensor = await self._parameters_to_tensor(parameters)
            
            # Style token
            style_token = torch.tensor([list(HarmonicStyle).index(style)])
            
            # Start with tonic chord
            start_chord = self.harmony_analyzer.chord_vocab.encode_chord(f"{parameters.key_signature}")
            chord_sequence = torch.tensor([[start_chord]])
            
            # Generate progression
            with torch.no_grad():
                for _ in range(parameters.progression_length - 1):
                    chord_logits, function_logits, tension_scores, vl_scores = self.transformer_model(
                        chord_sequence, style_token, param_tensor
                    )
                    
                    # Sample next chord
                    next_chord_probs = F.softmax(chord_logits[:, -1, :], dim=-1)
                    next_chord = torch.multinomial(next_chord_probs, 1)
                    
                    # Append to sequence
                    chord_sequence = torch.cat([chord_sequence, next_chord], dim=1)
            
            # Convert tokens to chord data
            chords = []
            for token in chord_sequence[0]:
                chord_symbol = self.harmony_analyzer.chord_vocab.decode_token(token.item())
                if chord_symbol not in ["<PAD>", "<START>", "<END>", "<UNK>"]:
                    chord_data = await self._symbol_to_chord_data(chord_symbol)
                    chords.append(chord_data)
            
            return chords[:parameters.progression_length]
            
        except Exception as e:
            logger.error(f"Error in neural network generation: {e}")
            # Fallback to template generation
            return await self._generate_with_templates(style, parameters)
    
    async def _generate_with_templates(self, style: HarmonicStyle,
                                     parameters: HarmonicParameters) -> List[ChordData]:
        """Generate progression using style templates"""
        try:
            # Get style template
            template = self.progression_templates.get(style, self.progression_templates[HarmonicStyle.POP])
            
            # Choose progression pattern
            progressions = template["common_progressions"]
            pattern = progressions[np.random.randint(len(progressions))]
            
            # Extend or truncate to desired length
            if len(pattern) < parameters.progression_length:
                # Repeat pattern
                pattern = (pattern * ((parameters.progression_length // len(pattern)) + 1))[:parameters.progression_length]
            else:
                pattern = pattern[:parameters.progression_length]
            
            # Convert roman numerals to chords
            chords = []
            for roman in pattern:
                chord_data = await self._roman_to_chord_data(
                    roman, parameters.key_signature, parameters.mode, template
                )
                chords.append(chord_data)
            
            # Apply inversions and extensions
            chords = await self._apply_chord_modifications(chords, template, parameters)
            
            return chords
            
        except Exception as e:
            logger.error(f"Error in template generation: {e}")
            # Return basic I-V-vi-IV progression
            return await self._generate_basic_progression(parameters)
    
    async def _roman_to_chord_data(self, roman: str, key: str, mode: str,
                                 template: Dict[str, Any]) -> ChordData:
        """Convert roman numeral to chord data"""
        try:
            # Roman numeral to scale degree mapping
            roman_to_degree = {
                "I": 1, "ii": 2, "iii": 3, "IV": 4, "V": 5, "vi": 6, "vii": 7,
                "i": 1, "II": 2, "III": 3, "iv": 4, "v": 5, "VI": 6, "VII": 7
            }
            
            # Parse roman numeral
            base_roman = roman.rstrip("7°+")
            degree = roman_to_degree.get(base_roman, 1)
            
            # Calculate root note
            key_notes = ["C", "D", "E", "F", "G", "A", "B"]
            key_index = key_notes.index(key) if key in key_notes else 0
            root_index = (key_index + degree - 1) % 7
            root_note = key_notes[root_index]
            
            # Handle accidentals
            if key.endswith("#"):
                # Apply sharp to scale degrees as needed
                sharp_degrees = [1, 3, 6, 7] if mode == "major" else [2, 5, 7]
                if degree in sharp_degrees:
                    root_note += "#"
            
            # Determine chord quality
            if roman.islower():
                quality = ChordQuality.MINOR
            elif "°" in roman:
                quality = ChordQuality.DIMINISHED
            elif "+" in roman:
                quality = ChordQuality.AUGMENTED
            else:
                quality = ChordQuality.MAJOR
            
            # Add seventh if specified
            if "7" in roman:
                if quality == ChordQuality.MAJOR:
                    quality = ChordQuality.DOMINANT_SEVENTH
                elif quality == ChordQuality.MINOR:
                    quality = ChordQuality.MINOR_SEVENTH
                elif quality == ChordQuality.DIMINISHED:
                    quality = ChordQuality.HALF_DIMINISHED
            
            # Generate chord tones
            chord_tones = await self._generate_chord_tones(root_note, quality)
            
            # Convert to MIDI
            midi_notes = await self.harmony_analyzer._notes_to_midi(chord_tones)
            
            return ChordData(
                root_note=root_note,
                quality=quality,
                chord_tones=chord_tones,
                midi_notes=midi_notes,
                roman_numeral=roman
            )
            
        except Exception as e:
            logger.error(f"Error converting roman to chord: {e}")
            return ChordData(root_note="C", quality=ChordQuality.MAJOR)
    
    async def _generate_chord_tones(self, root: str, quality: ChordQuality) -> List[str]:
        """Generate chord tones for given root and quality"""
        try:
            # Chromatic scale
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            root_index = notes.index(root) if root in notes else 0
            
            # Interval patterns for chord qualities
            patterns = {
                ChordQuality.MAJOR: [0, 4, 7],
                ChordQuality.MINOR: [0, 3, 7],
                ChordQuality.DIMINISHED: [0, 3, 6],
                ChordQuality.AUGMENTED: [0, 4, 8],
                ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
                ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
                ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
                ChordQuality.HALF_DIMINISHED: [0, 3, 6, 10],
                ChordQuality.FULLY_DIMINISHED: [0, 3, 6, 9]
            }
            
            pattern = patterns.get(quality, [0, 4, 7])
            chord_tones = []
            
            for interval in pattern:
                note_index = (root_index + interval) % 12
                chord_tones.append(notes[note_index])
            
            return chord_tones
            
        except Exception as e:
            logger.error(f"Error generating chord tones: {e}")
            return [root, "E", "G"]  # Default major triad
    
    async def _apply_chord_modifications(self, chords: List[ChordData],
                                       template: Dict[str, Any],
                                       parameters: HarmonicParameters) -> List[ChordData]:
        """Apply inversions, extensions, and other modifications"""
        try:
            modified_chords = []
            qualities = template["chord_qualities"]
            
            for chord in chords:
                modified_chord = chord
                
                # Add seventh
                if (np.random.random() < qualities["seventh_frequency"] and
                    chord.quality in [ChordQuality.MAJOR, ChordQuality.MINOR]):
                    
                    if chord.quality == ChordQuality.MAJOR:
                        modified_chord.quality = ChordQuality.MAJOR_SEVENTH
                    else:
                        modified_chord.quality = ChordQuality.MINOR_SEVENTH
                    
                    # Regenerate chord tones
                    modified_chord.chord_tones = await self._generate_chord_tones(
                        chord.root_note, modified_chord.quality
                    )
                    modified_chord.midi_notes = await self.harmony_analyzer._notes_to_midi(
                        modified_chord.chord_tones
                    )
                
                # Apply inversion
                if (parameters.allow_inversions and 
                    np.random.random() < qualities["inversions_frequency"]):
                    
                    inversion = np.random.randint(1, min(3, len(modified_chord.chord_tones)))
                    modified_chord.inversion = inversion
                    
                    # Rotate chord tones
                    chord_tones = modified_chord.chord_tones[inversion:] + modified_chord.chord_tones[:inversion]
                    modified_chord.chord_tones = chord_tones
                    modified_chord.bass_note = chord_tones[0]
                
                modified_chords.append(modified_chord)
            
            return modified_chords
            
        except Exception as e:
            logger.error(f"Error applying chord modifications: {e}")
            return chords
    
    async def _generate_basic_progression(self, parameters: HarmonicParameters) -> List[ChordData]:
        """Generate basic I-V-vi-IV progression as fallback"""
        try:
            pattern = ["I", "V", "vi", "IV"]
            progression_pattern = (pattern * ((parameters.progression_length // 4) + 1))[:parameters.progression_length]
            
            chords = []
            for roman in progression_pattern:
                chord_data = await self._roman_to_chord_data(
                    roman, parameters.key_signature, parameters.mode, {}
                )
                chords.append(chord_data)
            
            return chords
            
        except Exception as e:
            logger.error(f"Error generating basic progression: {e}")
            # Ultimate fallback: single chord
            return [ChordData(root_note=parameters.key_signature, quality=ChordQuality.MAJOR)]
    
    async def _symbol_to_chord_data(self, symbol: str) -> ChordData:
        """Convert chord symbol to chord data"""
        try:
            # Parse chord symbol
            root = symbol[0]
            if len(symbol) > 1 and symbol[1] in ["#", "b"]:
                root += symbol[1]
                quality_part = symbol[2:]
            else:
                quality_part = symbol[1:]
            
            # Determine quality
            if quality_part == "":
                quality = ChordQuality.MAJOR
            elif quality_part == "m":
                quality = ChordQuality.MINOR
            elif quality_part == "dim":
                quality = ChordQuality.DIMINISHED
            elif quality_part == "aug":
                quality = ChordQuality.AUGMENTED
            elif quality_part == "7":
                quality = ChordQuality.DOMINANT_SEVENTH
            elif quality_part == "maj7":
                quality = ChordQuality.MAJOR_SEVENTH
            elif quality_part == "m7":
                quality = ChordQuality.MINOR_SEVENTH
            else:
                quality = ChordQuality.MAJOR
            
            # Generate chord tones
            chord_tones = await self._generate_chord_tones(root, quality)
            midi_notes = await self.harmony_analyzer._notes_to_midi(chord_tones)
            
            return ChordData(
                root_note=root,
                quality=quality,
                chord_tones=chord_tones,
                midi_notes=midi_notes
            )
            
        except Exception as e:
            logger.error(f"Error converting symbol to chord data: {e}")
            return ChordData(root_note="C", quality=ChordQuality.MAJOR)
    
    async def _generate_harmonic_rhythm(self, parameters: HarmonicParameters) -> List[float]:
        """Generate harmonic rhythm (duration of each chord)"""
        try:
            if parameters.chord_rhythm == "whole_notes":
                return [1.0] * parameters.progression_length
            elif parameters.chord_rhythm == "half_notes":
                return [0.5] * parameters.progression_length
            else:  # mixed
                rhythms = []
                for _ in range(parameters.progression_length):
                    # Random choice between whole, half, and quarter notes
                    rhythm = np.random.choice([1.0, 0.5, 0.25], p=[0.5, 0.3, 0.2])
                    rhythms.append(rhythm)
                return rhythms
                
        except Exception as e:
            logger.error(f"Error generating harmonic rhythm: {e}")
            return [1.0] * parameters.progression_length
    
    async def _analyze_progression_voice_leading(self, chords: List[ChordData]) -> Dict[str, Any]:
        """Analyze voice leading for entire progression"""
        try:
            if len(chords) < 2:
                return {"overall_quality": 1.0}
            
            voice_leading_scores = []
            movement_analysis = []
            
            for i in range(len(chords) - 1):
                vl_analysis = await self.harmony_analyzer.analyze_voice_leading(chords[i], chords[i+1])
                voice_leading_scores.append(vl_analysis["voice_leading_quality"])
                movement_analysis.append(vl_analysis)
            
            # Overall analysis
            analysis = {
                "overall_quality": np.mean(voice_leading_scores) if voice_leading_scores else 1.0,
                "individual_scores": voice_leading_scores,
                "movement_details": movement_analysis,
                "smoothest_transition": max(voice_leading_scores) if voice_leading_scores else 1.0,
                "roughest_transition": min(voice_leading_scores) if voice_leading_scores else 1.0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing progression voice leading: {e}")
            return {"overall_quality": 0.5}
    
    async def _calculate_tension_curve(self, chords: List[ChordData], 
                                     parameters: HarmonicParameters) -> List[float]:
        """Calculate harmonic tension curve"""
        try:
            tension_scores = []
            
            for chord in chords:
                # Base tension from chord quality
                quality_tensions = {
                    ChordQuality.MAJOR: 0.2,
                    ChordQuality.MINOR: 0.4,
                    ChordQuality.DOMINANT_SEVENTH: 0.8,
                    ChordQuality.MINOR_SEVENTH: 0.6,
                    ChordQuality.MAJOR_SEVENTH: 0.5,
                    ChordQuality.DIMINISHED: 0.9,
                    ChordQuality.AUGMENTED: 0.8,
                    ChordQuality.HALF_DIMINISHED: 0.7
                }
                
                base_tension = quality_tensions.get(chord.quality, 0.3)
                
                # Modify based on harmonic function
                if chord.harmonic_function == HarmonicFunction.DOMINANT:
                    base_tension += 0.3
                elif chord.harmonic_function == HarmonicFunction.TONIC:
                    base_tension -= 0.2
                
                # Clamp to 0-1 range
                tension = max(0.0, min(1.0, base_tension))
                tension_scores.append(tension)
            
            return tension_scores
            
        except Exception as e:
            logger.error(f"Error calculating tension curve: {e}")
            return [0.5] * len(chords)
    
    async def _detect_modulations(self, chords: List[ChordData], 
                                key_center: str) -> List[Dict[str, Any]]:
        """Detect key modulations in progression"""
        try:
            modulations = []
            current_key = key_center
            
            # Simplified modulation detection
            for i, chord in enumerate(chords):
                # Check for secondary dominants or chromatic chords
                if chord.root_note not in self._get_diatonic_notes(current_key):
                    # Potential modulation
                    possible_keys = await self._analyze_possible_keys(chords[i:i+3])
                    
                    if possible_keys and possible_keys[0] != current_key:
                        modulations.append({
                            "position": i,
                            "from_key": current_key,
                            "to_key": possible_keys[0],
                            "type": "direct",
                            "confidence": 0.7
                        })
                        current_key = possible_keys[0]
            
            return modulations
            
        except Exception as e:
            logger.error(f"Error detecting modulations: {e}")
            return []
    
    def _get_diatonic_notes(self, key: str) -> List[str]:
        """Get diatonic notes for a key"""
        # Simplified - returns C major scale for any key
        return ["C", "D", "E", "F", "G", "A", "B"]
    
    async def _analyze_possible_keys(self, chord_segment: List[ChordData]) -> List[str]:
        """Analyze possible keys for chord segment"""
        try:
            # Simplified key analysis
            root_notes = [chord.root_note for chord in chord_segment]
            
            # Count occurrences and suggest most likely key
            from collections import Counter
            note_counts = Counter(root_notes)
            most_common = note_counts.most_common(1)
            
            if most_common:
                return [most_common[0][0]]
            
            return []
            
        except Exception as e:
            logger.error(f"Error analyzing possible keys: {e}")
            return []
    
    async def _calculate_quality_metrics(self, chords: List[ChordData],
                                       voice_leading_analysis: Dict[str, Any],
                                       parameters: HarmonicParameters) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        try:
            metrics = {}
            
            # Voice leading quality
            metrics["voice_leading_quality"] = voice_leading_analysis.get("overall_quality", 0.5)
            
            # Harmonic variety
            unique_qualities = len(set(chord.quality for chord in chords))
            max_possible = min(len(chords), len(ChordQuality))
            metrics["harmonic_variety"] = unique_qualities / max_possible if max_possible > 0 else 0
            
            # Functional coherence
            tonic_count = sum(1 for chord in chords 
                            if chord.harmonic_function == HarmonicFunction.TONIC)
            metrics["functional_coherence"] = tonic_count / len(chords) if chords else 0
            
            # Complexity appropriateness
            seventh_count = sum(1 for chord in chords 
                              if "SEVENTH" in chord.quality.value.upper())
            complexity_ratio = seventh_count / len(chords) if chords else 0
            target_complexity = parameters.harmonic_complexity
            complexity_diff = abs(complexity_ratio - target_complexity)
            metrics["complexity_appropriateness"] = 1.0 - complexity_diff
            
            # Overall quality
            metrics["overall_quality"] = np.mean([
                metrics["voice_leading_quality"],
                metrics["harmonic_variety"],
                metrics["functional_coherence"],
                metrics["complexity_appropriateness"]
            ])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return {"overall_quality": 0.5}
    
    async def _parameters_to_tensor(self, parameters: HarmonicParameters) -> torch.Tensor:
        """Convert parameters to tensor for neural network"""
        try:
            # Normalize parameters to 0-1 range
            key_offset = ord(parameters.key_signature[0]) - ord('C')
            key_normalized = key_offset / 11.0
            
            param_values = [
                key_normalized,
                1.0 if parameters.mode == "major" else 0.0,
                parameters.progression_length / 16.0,  # Normalize to max 16 chords
                parameters.voice_leading_smoothness,
                parameters.harmonic_complexity,
                1.0 if parameters.use_extensions else 0.0,
                1.0 if parameters.allow_inversions else 0.0,
                parameters.modulation_frequency,
                1.0 if parameters.avoid_parallel_fifths else 0.0,
                1.0 if parameters.prefer_common_tones else 0.0
            ]
            
            return torch.tensor(param_values, dtype=torch.float32).unsqueeze(0)
            
        except Exception as e:
            logger.error(f"Error converting parameters to tensor: {e}")
            return torch.zeros(1, 10)
    
    async def reharmonize_melody(self, melody_notes: List[int],
                               style: HarmonicStyle,
                               parameters: HarmonicParameters) -> HarmonicProgression:
        """Generate harmonization for existing melody"""
        try:
            # Analyze melody for implied harmony
            chord_suggestions = await self._analyze_melody_harmony(melody_notes, parameters)
            
            # Generate progression based on analysis
            chords = await self._generate_from_melody_analysis(chord_suggestions, style, parameters)
            
            # Create full progression result
            progression = await self.generate_harmonic_progression(style, parameters, use_neural_network=False)
            progression.chords = chords
            
            # Recalculate metrics
            progression.voice_leading_analysis = await self._analyze_progression_voice_leading(chords)
            progression.quality_metrics = await self._calculate_quality_metrics(
                chords, progression.voice_leading_analysis, parameters
            )
            
            return progression
            
        except Exception as e:
            logger.error(f"Error reharmonizing melody: {e}")
            raise
    
    async def _analyze_melody_harmony(self, melody_notes: List[int],
                                    parameters: HarmonicParameters) -> List[str]:
        """Analyze melody for harmonic implications"""
        try:
            chord_suggestions = []
            
            # Group melody notes (simplified - every 4 notes = 1 chord)
            chunk_size = 4
            for i in range(0, len(melody_notes), chunk_size):
                chunk = melody_notes[i:i + chunk_size]
                
                # Find most prominent note (highest occurrence or longest duration)
                from collections import Counter
                note_counts = Counter(chunk)
                prominent_note = note_counts.most_common(1)[0][0]
                
                # Convert MIDI to note name
                note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                note_name = note_names[prominent_note % 12]
                
                # Simple chord suggestion based on note
                chord_suggestions.append(note_name)
            
            return chord_suggestions
            
        except Exception as e:
            logger.error(f"Error analyzing melody harmony: {e}")
            return ["C"] * (len(melody_notes) // 4)
    
    async def _generate_from_melody_analysis(self, chord_suggestions: List[str],
                                           style: HarmonicStyle,
                                           parameters: HarmonicParameters) -> List[ChordData]:
        """Generate chords from melody analysis"""
        try:
            chords = []
            
            for suggestion in chord_suggestions:
                # Create chord based on suggestion and style
                quality = ChordQuality.MAJOR  # Default
                
                if style == HarmonicStyle.JAZZ:
                    quality = ChordQuality.MAJOR_SEVENTH
                elif style == HarmonicStyle.BLUES:
                    quality = ChordQuality.DOMINANT_SEVENTH
                
                chord_tones = await self._generate_chord_tones(suggestion, quality)
                midi_notes = await self.harmony_analyzer._notes_to_midi(chord_tones)
                
                chord_data = ChordData(
                    root_note=suggestion,
                    quality=quality,
                    chord_tones=chord_tones,
                    midi_notes=midi_notes
                )
                
                chords.append(chord_data)
            
            return chords
            
        except Exception as e:
            logger.error(f"Error generating from melody analysis: {e}")
            return []
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get generation performance statistics"""
        try:
            if not self.generation_history:
                return {"total_generated": 0}
            
            recent_history = self.generation_history[-30:]  # Last 30 generations
            
            return {
                "total_generated": len(self.generation_history),
                "recent_average_quality": np.mean([h["quality"] for h in recent_history]),
                "style_distribution": {
                    style: sum(1 for h in recent_history if h["style"] == style)
                    for style in set(h["style"] for h in recent_history)
                },
                "key_distribution": {
                    key: sum(1 for h in recent_history if h["key"] == key)
                    for key in set(h["key"] for h in recent_history)
                },
                "last_generation": recent_history[-1] if recent_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_generated": 0}

# Processing classes for export
HarmonyGenerator = HarmonicProgressionAI
ChordProgressionAnalyzer = HarmonyAnalyzer
HarmonyOptimizer = HarmonicProgressionAI

# Export classes
__all__ = [
    "HarmonicProgressionAI",
    "HarmonyGenerator",
    "ChordProgressionAnalyzer",
    "HarmonyOptimizer", 
    "HarmonicStyle",
    "ChordQuality",
    "HarmonicFunction",
    "VoiceLeadingType",
    "ChordData",
    "HarmonicProgression",
    "HarmonicParameters",
    "HarmonyAnalyzer",
    "HarmonicTransformerNetwork",
    "ChordVocabulary"
]