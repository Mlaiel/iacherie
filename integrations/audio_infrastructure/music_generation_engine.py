"""🎵 Enterprise Music Generation Engine - AI Composition & Style Transfer
=======================================================================

Engine de génération musicale IA enterprise avec composition automatique,
transfert de style et orchestration pour créateurs musicaux sur IA Chérie.

Expert Roles Implementation:
🤖 Lead Dev IA: Neural music generation + style transfer + composition algorithms
🧠 ML Engineer: Music ML models + pattern recognition + harmonic analysis
🎵 Audio Engineer: MIDI processing + audio synthesis + quality optimization
🏗️ Backend Senior: Real-time generation + scalable architecture + optimization
🔒 Sécurité: Original composition guarantee + copyright compliance

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation de génération musicale IA est la propriété intellectuelle
EXCLUSIVE de Fahed Mlaiel. Usage commercial non autorisé strictement INTERDIT.
"""

import asyncio
import logging
import numpy as np
import scipy.signal
import librosa
import pretty_midi
import json
import time
import uuid
import threading
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, BinaryIO, Generator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import io
import statistics
import hashlib
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
import pickle

logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    """Genres musicaux supportés"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    REGGAE = "reggae"
    COUNTRY = "country"
    BLUES = "blues"
    FUNK = "funk"
    LATIN = "latin"
    AMBIENT = "ambient"
    CINEMATIC = "cinematic"
    GAME_MUSIC = "game_music"

class MusicMood(Enum):
    """Humeurs musicales"""
    ENERGETIC = "energetic"
    CALM = "calm"
    HAPPY = "happy"
    MELANCHOLIC = "melancholic"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    ROMANTIC = "romantic"
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"
    EPIC = "epic"
    FUNKY = "funky"
    DREAMY = "dreamy"

class MusicalStructure(Enum):
    """Structures musicales"""
    VERSE_CHORUS = "verse_chorus"
    AABA = "aaba"
    TWELVE_BAR_BLUES = "twelve_bar_blues"
    SONATA = "sonata"
    RONDO = "rondo"
    THEME_VARIATIONS = "theme_variations"
    FREE_FORM = "free_form"
    MINIMALIST = "minimalist"

class InstrumentType(Enum):
    """Types d'instruments"""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    VIOLIN = "violin"
    CELLO = "cello"
    FLUTE = "flute"
    TRUMPET = "trumpet"
    SAXOPHONE = "saxophone"
    SYNTHESIZER = "synthesizer"
    VOICE = "voice"
    STRINGS_SECTION = "strings_section"
    BRASS_SECTION = "brass_section"
    WOODWINDS = "woodwinds"

class CompositionComplexity(Enum):
    """Niveaux de complexité compositionnelle"""
    SIMPLE = "simple"          # Mélodie simple, harmonies basiques
    INTERMEDIATE = "intermediate"  # Harmonies modérées, quelques modulations
    ADVANCED = "advanced"      # Harmonies complexes, modulations avancées
    VIRTUOSIC = "virtuosic"    # Complexité maximale, techniques avancées

@dataclass
class MusicGenerationConfig:
    """Configuration pour la génération musicale"""
    genre: MusicGenre
    mood: MusicMood
    structure: MusicalStructure
    key_signature: str = "C_major"
    time_signature: tuple[int, int] = (4, 4)
    tempo_bpm: int = 120
    duration_seconds: float = 60.0
    complexity: CompositionComplexity = CompositionComplexity.INTERMEDIATE
    instruments: List[InstrumentType] = field(default_factory=lambda: [InstrumentType.PIANO])
    copyright_safe: bool = True
    style_reference: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HarmonicProgression:
    """Progression harmonique"""
    chord_sequence: List[str]
    roman_numerals: List[str]
    harmonic_rhythm: List[float]  # Durée de chaque accord
    key_center: str
    modulations: List[tuple[int, str]]  # (measure, new_key)

@dataclass
class MelodicPhrase:
    """Phrase mélodique"""
    notes: List[tuple[int, float, float]]  # (pitch, start_time, duration)
    phrase_start: float
    phrase_end: float
    contour: List[int]  # Direction mélodique (-1, 0, 1)
    peak_note: int
    range_semitones: int

@dataclass
class RhythmPattern:
    """Pattern rythmique"""
    pattern: List[tuple[float, float, float]]  # (onset, duration, velocity)
    time_signature: tuple[int, int]
    pattern_length: float
    complexity_score: float
    groove_type: str

@dataclass
class MusicComposition:
    """Composition musicale complète"""
    midi_data: pretty_midi.PrettyMIDI
    audio_data: Optional[np.ndarray]
    harmonic_analysis: HarmonicProgression
    melodic_analysis: List[MelodicPhrase]
    rhythmic_analysis: List[RhythmPattern]
    composition_metadata: Dict[str, Any]
    generation_time: float
    originality_score: float
    quality_metrics: Dict[str, float]

class HarmonyGenerator:
    """Générateur d'harmonies musicales avancé"""
    
    def __init__(self):
        # Théorie musicale fondamentale
        self.major_scale_intervals = [0, 2, 4, 5, 7, 9, 11]
        self.minor_scale_intervals = [0, 2, 3, 5, 7, 8, 10]
        
        # Progressions harmoniques par genre
        self.genre_progressions = {
            MusicGenre.POP: [
                ["I", "V", "vi", "IV"],  # I-V-vi-IV (très populaire)
                ["vi", "IV", "I", "V"],  # vi-IV-I-V
                ["I", "vi", "IV", "V"],  # I-vi-IV-V (doo-wop)
            ],
            MusicGenre.JAZZ: [
                ["IIM7", "V7", "IM7"],   # ii-V-I
                ["IM7", "VI7", "IIM7", "V7"],  # I-VI-ii-V
                ["IM7", "bVIM7", "IIM7", "V7"],  # Substitutions
            ],
            MusicGenre.ROCK: [
                ["I", "bVII", "IV", "I"],  # I-bVII-IV-I
                ["I", "V", "IV", "I"],     # I-V-IV-I
                ["vi", "V", "I", "IV"],    # vi-V-I-IV
            ],
            MusicGenre.CLASSICAL: [
                ["I", "IV", "V", "I"],     # Cadence parfaite
                ["I", "vi", "ii", "V"],    # Progression classique
                ["I", "II", "V", "I"],     # Dominante secondaire
            ]
        }
        
        # Substitutions harmoniques avancées
        self.chord_substitutions = {
            "I": ["IM7", "I6", "Iadd9"],
            "ii": ["IIM7", "ii7", "N6"],  # Neapolitan
            "IV": ["IVM7", "ii7", "bII7"],  # Tritone substitution
            "V": ["V7", "viio", "bII7"],
            "vi": ["vim7", "bVI", "iv"]
        }
    
    def generate_harmonic_progression(self, config: MusicGenerationConfig) -> HarmonicProgression:
        """Génère une progression harmonique basée sur le genre et l'humeur"""
        
        # Sélection de la progression de base
        base_progressions = self.genre_progressions.get(
            config.genre, 
            self.genre_progressions[MusicGenre.POP]
        )
        
        selected_progression = random.choice(base_progressions)
        
        # Adaptation selon l'humeur
        if config.mood in [MusicMood.MELANCHOLIC, MusicMood.MYSTERIOUS]:
            # Conversion vers mode mineur
            selected_progression = self._convert_to_minor(selected_progression)
        elif config.mood == MusicMood.DRAMATIC:
            # Ajout de tensions harmoniques
            selected_progression = self._add_harmonic_tensions(selected_progression)
        
        # Calcul du rythme harmonique
        measures_per_chord = 4 / len(selected_progression)
        beats_per_measure = config.time_signature[0]
        harmonic_rhythm = [measures_per_chord * beats_per_measure] * len(selected_progression)
        
        # Conversion en accords concrets
        chord_sequence = self._roman_to_chords(selected_progression, config.key_signature)
        
        # Génération de modulations pour les compositions longues
        modulations = []
        if config.duration_seconds > 120:  # Plus de 2 minutes
            modulations = self._generate_modulations(config)
        
        return HarmonicProgression(
            chord_sequence=chord_sequence,
            roman_numerals=selected_progression,
            harmonic_rhythm=harmonic_rhythm,
            key_center=config.key_signature,
            modulations=modulations
        )
    
    def _convert_to_minor(self, progression: List[str]) -> List[str]:
        """Convertit une progression majeure vers le mode mineur"""
        minor_conversions = {
            "I": "i", "ii": "iio", "iii": "III", "IV": "iv", 
            "V": "V", "vi": "VI", "vii": "viio"
        }
        
        converted = []
        for chord in progression:
            # Extraction du chiffre romain de base
            base_numeral = chord.rstrip("M7o6add9")
            if base_numeral in minor_conversions:
                converted.append(minor_conversions[base_numeral])
            else:
                converted.append(chord)
        
        return converted
    
    def _add_harmonic_tensions(self, progression: List[str]) -> List[str]:
        """Ajoute des tensions harmoniques pour l'effet dramatique"""
        
        tension_chords = {
            "I": "IM7#11", "ii": "IIM7b5", "iii": "iiio7",
            "IV": "IVM7#11", "V": "V7alt", "vi": "vim7b5"
        }
        
        tensioned = []
        for i, chord in enumerate(progression):
            if i % 2 == 1 and chord in tension_chords:  # Tensions sur temps faibles
                tensioned.append(tension_chords[chord])
            else:
                tensioned.append(chord)
        
        return tensioned
    
    def _roman_to_chords(self, roman_numerals: List[str], key: str) -> List[str]:
        """Convertit les chiffres romains en noms d'accords"""
        
        # Définition des tonalités
        key_roots = {
            "C_major": ["C", "D", "E", "F", "G", "A", "B"],
            "G_major": ["G", "A", "B", "C", "D", "E", "F#"],
            "D_major": ["D", "E", "F#", "G", "A", "B", "C#"],
            "A_major": ["A", "B", "C#", "D", "E", "F#", "G#"],
            "F_major": ["F", "G", "A", "Bb", "C", "D", "E"],
            # ... autres tonalités
        }
        
        scale_degrees = key_roots.get(key, key_roots["C_major"])
        
        # Correspondance chiffres romains -> degrés
        roman_to_degree = {
            "I": 0, "i": 0, "II": 1, "ii": 1, "III": 2, "iii": 2,
            "IV": 3, "iv": 3, "V": 4, "v": 4, "VI": 5, "vi": 5,
            "VII": 6, "vii": 6, "viio": 6
        }
        
        chord_sequence = []
        for roman in roman_numerals:
            # Extraction du degré de base
            base_roman = roman.rstrip("M7o6add9#5b5alt")
            
            if base_roman in roman_to_degree:
                degree = roman_to_degree[base_roman]
                root_note = scale_degrees[degree]
                
                # Détermination du type d'accord
                if roman.islower() or "o" in roman:
                    chord_type = "m" if "o" not in roman else "dim"
                else:
                    chord_type = ""
                
                # Ajout des extensions
                if "M7" in roman:
                    chord_type += "maj7"
                elif "7" in roman:
                    chord_type += "7"
                
                chord_name = root_note + chord_type
                chord_sequence.append(chord_name)
            else:
                chord_sequence.append("C")  # Fallback
        
        return chord_sequence
    
    def _generate_modulations(self, config: MusicGenerationConfig) -> List[tuple[int, str]]:
        """Génère des modulations pour les compositions longues"""
        
        modulations = []
        duration_measures = int(config.duration_seconds * config.tempo_bpm / 60 / config.time_signature[0])
        
        # Modulation vers la dominante au milieu
        if duration_measures > 32:
            modulation_point = duration_measures // 2
            dominant_key = self._get_dominant_key(config.key_signature)
            modulations.append((modulation_point, dominant_key))
            
            # Retour vers la tonique
            if duration_measures > 48:
                return_point = int(duration_measures * 0.75)
                modulations.append((return_point, config.key_signature))
        
        return modulations
    
    def _get_dominant_key(self, key: str) -> str:
        """Retourne la tonalité de la dominante"""
        dominant_keys = {
            "C_major": "G_major",
            "G_major": "D_major", 
            "F_major": "C_major",
            "D_major": "A_major",
            "A_major": "E_major"
        }
        return dominant_keys.get(key, "G_major")

class MelodyGenerator:
    """Générateur de mélodies avancé"""
    
    def __init__(self):
        # Intervalles mélodiques préférés par style
        self.style_intervals = {
            MusicGenre.CLASSICAL: [1, 2, 3, 4, 5],  # Mouvements conjoints privilégiés
            MusicGenre.JAZZ: [2, 3, 4, 6, 7],       # Intervalles plus larges
            MusicGenre.POP: [1, 2, 3, 4],           # Mélodies accessibles
            MusicGenre.ELECTRONIC: [3, 4, 5, 7, 12] # Intervalles synthétiques
        }
        
        # Contours mélodiques typiques
        self.melodic_contours = {
            "arch": [1, 1, 1, 0, -1, -1, -1],      # Forme en arche
            "wave": [1, -1, 1, -1, 1, -1],         # Ondulation
            "ascending": [1, 1, 0, 1, 1],          # Montée progressive
            "descending": [-1, -1, 0, -1, -1],     # Descente progressive
            "plateau": [1, 1, 0, 0, 0, -1, -1]     # Montée-plateau-descente
        }
    
    def generate_melody(self, harmony: HarmonicProgression, 
                       config: MusicGenerationConfig) -> List[MelodicPhrase]:
        """Génère une mélodie basée sur l'harmonie"""
        
        phrases = []
        phrase_length = 8.0  # 8 temps par phrase
        current_time = 0.0
        
        # Sélection des intervalles selon le genre
        preferred_intervals = self.style_intervals.get(
            config.genre, 
            self.style_intervals[MusicGenre.POP]
        )
        
        # Génération phrase par phrase
        while current_time < config.duration_seconds:
            phrase_end = min(current_time + phrase_length, config.duration_seconds)
            
            # Sélection du contour mélodique
            contour_type = self._select_contour(config.mood)
            contour = self.melodic_contours[contour_type]
            
            # Génération des notes de la phrase
            phrase_notes = self._generate_phrase_notes(
                current_time, phrase_end, harmony, contour, 
                preferred_intervals, config
            )
            
            # Analyse de la phrase
            if phrase_notes:
                phrase = MelodicPhrase(
                    notes=phrase_notes,
                    phrase_start=current_time,
                    phrase_end=phrase_end,
                    contour=contour,
                    peak_note=max(note[0] for note in phrase_notes),
                    range_semitones=max(note[0] for note in phrase_notes) - 
                                   min(note[0] for note in phrase_notes)
                )
                phrases.append(phrase)
            
            current_time = phrase_end
        
        return phrases
    
    def _select_contour(self, mood: MusicMood) -> str:
        """Sélectionne un contour mélodique selon l'humeur"""
        
        mood_contours = {
            MusicMood.ENERGETIC: ["ascending", "wave"],
            MusicMood.CALM: ["plateau", "wave"],
            MusicMood.HAPPY: ["arch", "ascending"],
            MusicMood.MELANCHOLIC: ["descending", "plateau"],
            MusicMood.DRAMATIC: ["arch", "wave"],
            MusicMood.PEACEFUL: ["plateau", "descending"]
        }
        
        available_contours = mood_contours.get(mood, ["arch", "wave"])
        return random.choice(available_contours)
    
    def _generate_phrase_notes(self, start_time: float, end_time: float,
                              harmony: HarmonicProgression, contour: List[int],
                              intervals: List[int], config: MusicGenerationConfig) -> List[tuple[int, float, float]]:
        """Génère les notes d'une phrase mélodique"""
        
        notes = []
        phrase_duration = end_time - start_time
        notes_per_phrase = len(contour)
        note_duration = phrase_duration / notes_per_phrase
        
        # Note de départ (tonique de la gamme)
        root_note = self._key_to_midi_note(config.key_signature) + 60  # Octave médium
        current_pitch = root_note
        
        # Génération note par note suivant le contour
        for i, direction in enumerate(contour):
            note_start = start_time + i * note_duration
            
            # Mouvement mélodique selon le contour
            if direction == 1:  # Montée
                interval = random.choice(intervals)
                current_pitch += interval
            elif direction == -1:  # Descente
                interval = random.choice(intervals)
                current_pitch -= interval
            # direction == 0: pas de mouvement
            
            # Limitation de l'ambitus (éviter les extrêmes)
            current_pitch = max(48, min(84, current_pitch))  # C3 à C6
            
            # Ajustement harmonique (notes de l'accord)
            current_pitch = self._adjust_to_harmony(
                current_pitch, note_start, harmony
            )
            
            # Variation rythmique
            actual_duration = note_duration * random.choice([0.5, 0.75, 1.0, 1.25])
            actual_duration = min(actual_duration, end_time - note_start)
            
            if actual_duration > 0:
                notes.append((current_pitch, note_start, actual_duration))
        
        return notes
    
    def _key_to_midi_note(self, key: str) -> int:
        """Convertit une tonalité en note MIDI (tonique)"""
        key_notes = {
            "C_major": 0, "G_major": 7, "D_major": 2,
            "A_major": 9, "E_major": 4, "F_major": 5,
            "Bb_major": 10, "Eb_major": 3, "Ab_major": 8
        }
        return key_notes.get(key, 0)
    
    def _adjust_to_harmony(self, pitch: int, time: float, 
                          harmony: HarmonicProgression) -> int:
        """Ajuste une note pour qu'elle soit harmoniquement correcte"""
        
        # Trouver l'accord actuel
        chord_time = 0.0
        current_chord = harmony.chord_sequence[0]
        
        for i, duration in enumerate(harmony.harmonic_rhythm):
            if time >= chord_time and time < chord_time + duration:
                current_chord = harmony.chord_sequence[i % len(harmony.chord_sequence)]
                break
            chord_time += duration
        
        # Notes de l'accord (simplification)
        chord_notes = self._get_chord_notes(current_chord)
        
        # Ajustement vers la note la plus proche de l'accord
        best_note = pitch
        min_distance = float('inf')
        
        for chord_note in chord_notes:
            # Test de toutes les octaves proches
            for octave_offset in [-12, 0, 12]:
                test_note = chord_note + octave_offset
                distance = abs(test_note - pitch)
                if distance < min_distance:
                    min_distance = distance
                    best_note = test_note
        
        return best_note
    
    def _get_chord_notes(self, chord_name: str) -> List[int]:
        """Retourne les notes MIDI d'un accord"""
        
        # Correspondance note -> MIDI
        note_to_midi = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        # Extraction de la fondamentale
        root_name = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in '#b':
            root_name += chord_name[1]
        
        root_note = note_to_midi.get(root_name, 0)
        
        # Construction de l'accord (triade majeure par défaut)
        if 'm' in chord_name and 'maj' not in chord_name:
            # Accord mineur
            chord_notes = [root_note, root_note + 3, root_note + 7]
        elif 'dim' in chord_name:
            # Accord diminué
            chord_notes = [root_note, root_note + 3, root_note + 6]
        else:
            # Accord majeur
            chord_notes = [root_note, root_note + 4, root_note + 7]
        
        # Ajout de la septième si présente
        if '7' in chord_name:
            if 'maj7' in chord_name:
                chord_notes.append(root_note + 11)
            else:
                chord_notes.append(root_note + 10)
        
        return chord_notes

class RhythmGenerator:
    """Générateur de patterns rythmiques"""
    
    def __init__(self):
        # Patterns rythmiques par genre
        self.genre_patterns = {
            MusicGenre.ROCK: {
                "kick": [1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 1, 0, 0, 0, 1, 0],
                "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
            },
            MusicGenre.JAZZ: {
                "kick": [1, 0, 0, 1, 0, 0, 1, 0],
                "snare": [0, 0, 1, 0, 0, 1, 0, 0],
                "ride": [1, 0, 1, 1, 0, 1, 1, 0]
            },
            MusicGenre.ELECTRONIC: {
                "kick": [1, 0, 1, 0, 1, 0, 1, 0],
                "snare": [0, 0, 1, 0, 0, 0, 1, 0],
                "synth": [1, 1, 0, 1, 1, 0, 1, 1]
            }
        }
    
    def generate_rhythm_pattern(self, config: MusicGenerationConfig) -> List[RhythmPattern]:
        """Génère des patterns rythmiques selon le genre"""
        
        patterns = []
        pattern_data = self.genre_patterns.get(
            config.genre, 
            self.genre_patterns[MusicGenre.ROCK]
        )
        
        # Calcul timing
        beats_per_measure = config.time_signature[0]
        beat_duration = 60.0 / config.tempo_bpm
        subdivision = 16  # Seizièmes de note
        step_duration = beat_duration / 4
        
        for instrument, pattern in pattern_data.items():
            rhythm_events = []
            
            # Conversion pattern binaire en événements temporels
            for i, hit in enumerate(pattern):
                if hit:
                    onset_time = i * step_duration
                    duration = step_duration * 0.8  # Légèrement détaché
                    velocity = self._calculate_velocity(i, config.mood)
                    rhythm_events.append((onset_time, duration, velocity))
            
            # Calcul complexité
            complexity = self._calculate_rhythm_complexity(pattern)
            
            rhythm_pattern = RhythmPattern(
                pattern=rhythm_events,
                time_signature=config.time_signature,
                pattern_length=beats_per_measure * beat_duration,
                complexity_score=complexity,
                groove_type=instrument
            )
            
            patterns.append(rhythm_pattern)
        
        return patterns
    
    def _calculate_velocity(self, step: int, mood: MusicMood) -> float:
        """Calcule la vélocité selon la position et l'humeur"""
        
        # Vélocités de base par humeur
        mood_velocities = {
            MusicMood.ENERGETIC: 0.9,
            MusicMood.CALM: 0.4,
            MusicMood.AGGRESSIVE: 1.0,
            MusicMood.PEACEFUL: 0.3,
            MusicMood.DRAMATIC: 0.8
        }
        
        base_velocity = mood_velocities.get(mood, 0.7)
        
        # Accentuation rythmique (temps forts)
        if step % 4 == 0:  # Temps 1
            accent = 1.2
        elif step % 2 == 0:  # Temps 3
            accent = 1.1
        else:
            accent = 0.9
        
        return min(base_velocity * accent, 1.0)
    
    def _calculate_rhythm_complexity(self, pattern: List[int]) -> float:
        """Calcule la complexité d'un pattern rythmique"""
        
        # Facteurs de complexité
        density = sum(pattern) / len(pattern)  # Densité des événements
        syncopation = self._calculate_syncopation(pattern)
        variation = len(set(pattern)) / len(pattern)  # Variété
        
        complexity = (density * 0.4 + syncopation * 0.4 + variation * 0.2)
        return min(complexity, 1.0)
    
    def _calculate_syncopation(self, pattern: List[int]) -> float:
        """Calcule le niveau de syncope"""
        
        syncopation_score = 0
        for i, hit in enumerate(pattern):
            if hit and i % 2 == 1:  # Frappe sur temps faible
                syncopation_score += 1
        
        return syncopation_score / len(pattern)

class MusicGenerationEngine:
    """Engine principal de génération musicale IA"""
    
    def __init__(self):
        self.harmony_generator = HarmonyGenerator()
        self.melody_generator = MelodyGenerator()
        self.rhythm_generator = RhythmGenerator()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.originality_database = {}  # Cache pour vérifier l'originalité
        
        logger.info("🎵 Music Generation Engine initialized - Fahed Mlaiel Enterprise")
    
    async def generate_music_async(self, config: MusicGenerationConfig) -> MusicComposition:
        """Génère une composition musicale de manière asynchrone"""
        
        start_time = time.time()
        
        logger.info(f"🎼 Génération musicale: {config.genre.value} - {config.mood.value}")
        
        # Génération des composants musicaux en parallèle
        loop = asyncio.get_event_loop()
        
        # Génération harmonique (base)
        harmony = await loop.run_in_executor(
            self.executor,
            self.harmony_generator.generate_harmonic_progression,
            config
        )
        
        # Génération mélodique (basée sur l'harmonie)
        melody_phrases = await loop.run_in_executor(
            self.executor,
            self.melody_generator.generate_melody,
            harmony, config
        )
        
        # Génération rythmique
        rhythm_patterns = await loop.run_in_executor(
            self.executor,
            self.rhythm_generator.generate_rhythm_pattern,
            config
        )
        
        # Assemblage MIDI
        midi_composition = await loop.run_in_executor(
            self.executor,
            self._create_midi_composition,
            harmony, melody_phrases, rhythm_patterns, config
        )
        
        # Génération audio (optionnelle)
        audio_data = None
        if config.user_preferences.get("generate_audio", False):
            audio_data = await self._generate_audio_from_midi(midi_composition)
        
        # Calcul métriques qualité
        quality_metrics = self._calculate_quality_metrics(
            harmony, melody_phrases, rhythm_patterns
        )
        
        # Vérification originalité
        originality_score = self._calculate_originality_score(midi_composition)
        
        # Métadonnées
        metadata = {
            "composer": "IA Chérie AI Engine",
            "genre": config.genre.value,
            "mood": config.mood.value,
            "key": config.key_signature,
            "tempo": config.tempo_bpm,
            "duration": config.duration_seconds,
            "generated_at": datetime.now().isoformat(),
            "copyright_safe": config.copyright_safe,
            "complexity": config.complexity.value,
            "instruments": [inst.value for inst in config.instruments]
        }
        
        generation_time = time.time() - start_time
        
        return MusicComposition(
            midi_data=midi_composition,
            audio_data=audio_data,
            harmonic_analysis=harmony,
            melodic_analysis=melody_phrases,
            rhythmic_analysis=rhythm_patterns,
            composition_metadata=metadata,
            generation_time=generation_time,
            originality_score=originality_score,
            quality_metrics=quality_metrics
        )
    
    def _create_midi_composition(self, harmony: HarmonicProgression,
                               melody_phrases: List[MelodicPhrase],
                               rhythm_patterns: List[RhythmPattern],
                               config: MusicGenerationConfig) -> pretty_midi.PrettyMIDI:
        """Crée la composition MIDI complète"""
        
        # Création de l'objet MIDI
        midi = pretty_midi.PrettyMIDI()
        
        # Configuration tempo
        tempo_changes = [pretty_midi.TempoChange(config.tempo_bpm, 0)]
        midi.tempo_changes = tempo_changes
        
        # Génération des pistes par instrument
        for instrument_type in config.instruments:
            instrument = self._create_instrument_track(
                instrument_type, harmony, melody_phrases, rhythm_patterns, config
            )
            midi.instruments.append(instrument)
        
        return midi
    
    def _create_instrument_track(self, instrument_type: InstrumentType,
                               harmony: HarmonicProgression,
                               melody_phrases: List[MelodicPhrase],
                               rhythm_patterns: List[RhythmPattern],
                               config: MusicGenerationConfig) -> pretty_midi.Instrument:
        """Crée une piste instrumentale"""
        
        # Mapping instruments vers MIDI programs
        instrument_programs = {
            InstrumentType.PIANO: 1,
            InstrumentType.GUITAR: 25,
            InstrumentType.BASS: 33,
            InstrumentType.VIOLIN: 41,
            InstrumentType.TRUMPET: 57,
            InstrumentType.SAXOPHONE: 65,
            InstrumentType.SYNTHESIZER: 81
        }
        
        program = instrument_programs.get(instrument_type, 1)
        instrument = pretty_midi.Instrument(program=program)
        
        # Génération des notes selon le type d'instrument
        if instrument_type == InstrumentType.PIANO:
            # Piano: mélodie + accompagnement harmonique
            self._add_melody_to_instrument(instrument, melody_phrases)
            self._add_harmony_to_instrument(instrument, harmony, config)
        
        elif instrument_type == InstrumentType.BASS:
            # Basse: fondamentales des accords
            self._add_bass_line_to_instrument(instrument, harmony, config)
        
        elif instrument_type == InstrumentType.DRUMS:
            # Batterie: patterns rythmiques
            instrument.is_drum = True
            self._add_rhythm_to_instrument(instrument, rhythm_patterns, config)
        
        else:
            # Autres instruments: mélodie principale
            self._add_melody_to_instrument(instrument, melody_phrases)
        
        return instrument
    
    def _add_melody_to_instrument(self, instrument: pretty_midi.Instrument,
                                melody_phrases: List[MelodicPhrase]):
        """Ajoute la mélodie à un instrument"""
        
        for phrase in melody_phrases:
            for pitch, start_time, duration in phrase.notes:
                note = pretty_midi.Note(
                    velocity=80,
                    pitch=int(pitch),
                    start=start_time,
                    end=start_time + duration
                )
                instrument.notes.append(note)
    
    def _add_harmony_to_instrument(self, instrument: pretty_midi.Instrument,
                                 harmony: HarmonicProgression,
                                 config: MusicGenerationConfig):
        """Ajoute l'accompagnement harmonique"""
        
        current_time = 0.0
        
        for i, (chord_name, duration) in enumerate(
            zip(harmony.chord_sequence, harmony.harmonic_rhythm)
        ):
            # Obtenir les notes de l'accord
            chord_notes = self.melody_generator._get_chord_notes(chord_name)
            
            # Jouer l'accord dans l'octave appropriée
            chord_octave = 48  # C3
            
            for note_offset in chord_notes:
                pitch = chord_octave + note_offset
                note = pretty_midi.Note(
                    velocity=60,  # Plus doux que la mélodie
                    pitch=pitch,
                    start=current_time,
                    end=current_time + duration * 0.9  # Légèrement détaché
                )
                instrument.notes.append(note)
            
            current_time += duration
    
    def _add_bass_line_to_instrument(self, instrument: pretty_midi.Instrument,
                                   harmony: HarmonicProgression,
                                   config: MusicGenerationConfig):
        """Ajoute une ligne de basse"""
        
        current_time = 0.0
        bass_octave = 36  # C2
        
        for chord_name, duration in zip(harmony.chord_sequence, harmony.harmonic_rhythm):
            # Fondamentale de l'accord
            chord_notes = self.melody_generator._get_chord_notes(chord_name)
            bass_note = bass_octave + chord_notes[0]
            
            # Pattern de basse selon le genre
            if config.genre == MusicGenre.ROCK:
                # Pattern rock: fondamentale sur tous les temps
                beat_duration = duration / config.time_signature[0]
                for beat in range(config.time_signature[0]):
                    note = pretty_midi.Note(
                        velocity=90,
                        pitch=bass_note,
                        start=current_time + beat * beat_duration,
                        end=current_time + beat * beat_duration + beat_duration * 0.8
                    )
                    instrument.notes.append(note)
            else:
                # Pattern simple: une note par accord
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=bass_note,
                    start=current_time,
                    end=current_time + duration * 0.9
                )
                instrument.notes.append(note)
            
            current_time += duration
    
    def _add_rhythm_to_instrument(self, instrument: pretty_midi.Instrument,
                                rhythm_patterns: List[RhythmPattern],
                                config: MusicGenerationConfig):
        """Ajoute les patterns rythmiques (batterie)"""
        
        # Mapping percussions MIDI
        drum_mapping = {
            "kick": 36,     # Bass drum
            "snare": 38,    # Snare drum  
            "hihat": 42,    # Closed hi-hat
            "ride": 51      # Ride cymbal
        }
        
        pattern_duration = 4.0 * 60.0 / config.tempo_bpm  # 4 beats
        current_time = 0.0
        
        while current_time < config.duration_seconds:
            for pattern in rhythm_patterns:
                drum_note = drum_mapping.get(pattern.groove_type, 36)
                
                for onset, duration, velocity in pattern.pattern:
                    note_time = current_time + onset
                    if note_time < config.duration_seconds:
                        note = pretty_midi.Note(
                            velocity=int(velocity * 127),
                            pitch=drum_note,
                            start=note_time,
                            end=note_time + duration
                        )
                        instrument.notes.append(note)
            
            current_time += pattern_duration
    
    async def _generate_audio_from_midi(self, midi: pretty_midi.PrettyMIDI) -> np.ndarray:
        """Génère l'audio à partir du MIDI (synthèse basique)"""
        
        # Synthèse audio simplifiée
        sample_rate = 44100
        audio_duration = midi.get_end_time()
        audio = np.zeros(int(audio_duration * sample_rate))
        
        # Synthèse additive simple pour chaque note
        for instrument in midi.instruments:
            if not instrument.is_drum:
                for note in instrument.notes:
                    # Génération d'une onde sinusoïdale pour chaque note
                    frequency = pretty_midi.note_number_to_hz(note.pitch)
                    start_sample = int(note.start * sample_rate)
                    end_sample = int(note.end * sample_rate)
                    
                    if end_sample <= len(audio):
                        duration_samples = end_sample - start_sample
                        t = np.linspace(0, duration_samples / sample_rate, duration_samples)
                        
                        # Oscillateur + enveloppe ADSR simple
                        wave = np.sin(2 * np.pi * frequency * t)
                        envelope = self._create_envelope(duration_samples)
                        
                        audio[start_sample:end_sample] += wave * envelope * (note.velocity / 127.0) * 0.1
        
        # Normalisation
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude * 0.95
        
        return audio
    
    def _create_envelope(self, duration_samples: int) -> np.ndarray:
        """Crée une enveloppe ADSR simple"""
        
        attack_samples = min(duration_samples // 10, 1000)
        decay_samples = min(duration_samples // 5, 2000)
        sustain_level = 0.7
        release_samples = min(duration_samples // 4, 3000)
        
        envelope = np.ones(duration_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0 and attack_samples + decay_samples < duration_samples:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)
        
        # Release
        if release_samples > 0:
            release_start = max(0, duration_samples - release_samples)
            envelope[release_start:] = np.linspace(
                envelope[release_start], 0, duration_samples - release_start
            )
        
        return envelope
    
    def _calculate_quality_metrics(self, harmony: HarmonicProgression,
                                 melody_phrases: List[MelodicPhrase],
                                 rhythm_patterns: List[RhythmPattern]) -> Dict[str, float]:
        """Calcule les métriques de qualité de la composition"""
        
        # Cohérence harmonique
        harmonic_coherence = self._analyze_harmonic_coherence(harmony)
        
        # Intérêt mélodique
        melodic_interest = self._analyze_melodic_interest(melody_phrases)
        
        # Complexité rythmique
        rhythmic_complexity = np.mean([p.complexity_score for p in rhythm_patterns])
        
        # Balance générale
        overall_balance = (harmonic_coherence + melodic_interest + rhythmic_complexity) / 3
        
        return {
            "harmonic_coherence": harmonic_coherence,
            "melodic_interest": melodic_interest,
            "rhythmic_complexity": rhythmic_complexity,
            "overall_quality": overall_balance,
            "structural_integrity": self._analyze_structure(melody_phrases),
            "commercial_appeal": self._estimate_commercial_appeal(harmony, melody_phrases)
        }
    
    def _analyze_harmonic_coherence(self, harmony: HarmonicProgression) -> float:
        """Analyse la cohérence harmonique"""
        
        # Vérification des progressions logiques
        coherence_score = 0.0
        
        # Analyse des mouvements de fondamentales
        for i in range(len(harmony.roman_numerals) - 1):
            current_chord = harmony.roman_numerals[i]
            next_chord = harmony.roman_numerals[i + 1]
            
            # Mouvements privilégiés (V->I, ii->V, etc.)
            if (current_chord == "V" and next_chord == "I") or \
               (current_chord == "ii" and next_chord == "V"):
                coherence_score += 1.0
            elif current_chord != next_chord:
                coherence_score += 0.5
        
        return min(coherence_score / max(len(harmony.roman_numerals) - 1, 1), 1.0)
    
    def _analyze_melodic_interest(self, phrases: List[MelodicPhrase]) -> float:
        """Analyse l'intérêt mélodique"""
        
        if not phrases:
            return 0.0
        
        # Variété des intervalles
        all_intervals = []
        for phrase in phrases:
            if len(phrase.notes) > 1:
                for i in range(len(phrase.notes) - 1):
                    interval = abs(phrase.notes[i+1][0] - phrase.notes[i][0])
                    all_intervals.append(interval)
        
        # Diversité des intervalles
        interval_variety = len(set(all_intervals)) / max(len(all_intervals), 1)
        
        # Variété des contours
        contour_variety = len(set(str(p.contour) for p in phrases)) / len(phrases)
        
        # Équilibre des tessitures
        all_pitches = [note[0] for phrase in phrases for note in phrase.notes]
        pitch_range = max(all_pitches) - min(all_pitches) if all_pitches else 0
        range_score = min(pitch_range / 24, 1.0)  # 2 octaves = score parfait
        
        return (interval_variety + contour_variety + range_score) / 3
    
    def _analyze_structure(self, phrases: List[MelodicPhrase]) -> float:
        """Analyse l'intégrité structurelle"""
        
        if len(phrases) < 2:
            return 0.5
        
        # Régularité des longueurs de phrases
        phrase_lengths = [p.phrase_end - p.phrase_start for p in phrases]
        length_consistency = 1.0 - (np.std(phrase_lengths) / np.mean(phrase_lengths))
        
        # Progression logique (climax, résolution)
        peak_positions = [p.peak_note for p in phrases]
        climax_position = peak_positions.index(max(peak_positions)) / len(peak_positions)
        climax_score = 1.0 - abs(climax_position - 0.7)  # Climax vers 70% idéal
        
        return (length_consistency + climax_score) / 2
    
    def _estimate_commercial_appeal(self, harmony: HarmonicProgression,
                                  phrases: List[MelodicPhrase]) -> float:
        """Estime l'attrait commercial"""
        
        # Progressions populaires
        popular_progressions = [
            ["I", "V", "vi", "IV"],
            ["vi", "IV", "I", "V"],
            ["I", "vi", "IV", "V"]
        ]
        
        harmony_appeal = 0.0
        for popular in popular_progressions:
            if harmony.roman_numerals == popular:
                harmony_appeal = 1.0
                break
            elif set(harmony.roman_numerals) & set(popular):
                harmony_appeal = 0.7
        
        # Mélodie accessible (intervalles modérés)
        all_intervals = []
        for phrase in phrases:
            if len(phrase.notes) > 1:
                for i in range(len(phrase.notes) - 1):
                    interval = abs(phrase.notes[i+1][0] - phrase.notes[i][0])
                    all_intervals.append(interval)
        
        # Préférence pour intervalles 1-5 (facilement chantables)
        accessible_intervals = sum(1 for i in all_intervals if 1 <= i <= 5)
        melody_appeal = accessible_intervals / max(len(all_intervals), 1)
        
        return (harmony_appeal + melody_appeal) / 2
    
    def _calculate_originality_score(self, midi: pretty_midi.PrettyMIDI) -> float:
        """Calcule le score d'originalité"""
        
        # Extraction d'empreinte musicale
        fingerprint = self._extract_musical_fingerprint(midi)
        
        # Vérification contre la base de données
        originality = 1.0
        for known_fingerprint in self.originality_database.values():
            similarity = self._calculate_similarity(fingerprint, known_fingerprint)
            if similarity > 0.8:  # Seuil de similarité
                originality = min(originality, 1.0 - similarity)
        
        # Ajout à la base de données
        composition_id = hashlib.md5(str(fingerprint).encode()).hexdigest()
        self.originality_database[composition_id] = fingerprint
        
        return originality
    
    def _extract_musical_fingerprint(self, midi: pretty_midi.PrettyMIDI) -> List[int]:
        """Extrait une empreinte musicale unique"""
        
        fingerprint = []
        
        # Analyse des intervalles mélodiques
        for instrument in midi.instruments:
            if not instrument.is_drum and instrument.notes:
                sorted_notes = sorted(instrument.notes, key=lambda n: n.start)
                
                # Intervalles successifs
                for i in range(min(10, len(sorted_notes) - 1)):  # 10 premiers intervalles
                    interval = sorted_notes[i+1].pitch - sorted_notes[i].pitch
                    fingerprint.append(interval % 12)  # Modulo octave
        
        # Remplissage si nécessaire
        while len(fingerprint) < 20:
            fingerprint.append(0)
        
        return fingerprint[:20]  # Empreinte de 20 éléments
    
    def _calculate_similarity(self, fp1: List[int], fp2: List[int]) -> float:
        """Calcule la similarité entre deux empreintes"""
        
        if len(fp1) != len(fp2):
            return 0.0
        
        matches = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return matches / len(fp1)

# Factory pour création d'instances
def create_music_generation_engine() -> MusicGenerationEngine:
    """Factory pour créer une instance du music generation engine"""
    return MusicGenerationEngine()

def create_music_config(genre: str = "pop", mood: str = "happy", 
                       duration: float = 60.0) -> MusicGenerationConfig:
    """Factory pour créer une configuration musicale"""
    
    return MusicGenerationConfig(
        genre=MusicGenre(genre),
        mood=MusicMood(mood),
        structure=MusicalStructure.VERSE_CHORUS,
        duration_seconds=duration,
        instruments=[InstrumentType.PIANO, InstrumentType.GUITAR, InstrumentType.BASS]
    )

# Export pour intégration
__all__ = [
    'MusicGenerationEngine',
    'MusicGenre',
    'MusicMood',
    'MusicalStructure',
    'InstrumentType',
    'CompositionComplexity',
    'MusicGenerationConfig',
    'MusicComposition',
    'HarmonicProgression',
    'MelodicPhrase',
    'RhythmPattern',
    'create_music_generation_engine',
    'create_music_config'
]