"""
 Mood Analyzer - AI-Powered Musical Mood Detection

Advanced mood and emotion analysis engine for identifying emotional
characteristics and affective content in audio signals.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List
from enum import Enum
import librosa


class MoodCategory(Enum):
    """Musical mood categories"""
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    AGGRESSIVE = "aggressive"
    ROMANTIC = "romantic"
    MYSTERIOUS = "mysterious"
    UPLIFTING = "uplifting"


class MoodAnalyzer:
    """Professional musical mood analysis engine"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Mood characteristics (simplified mapping)
        self.mood_characteristics = {
            MoodCategory.HAPPY: {'tempo_range': (120, 160), 'energy_min': 0.6, 'valence': 0.8},
            MoodCategory.SAD: {'tempo_range': (60, 100), 'energy_min': 0.2, 'valence': 0.2},
            MoodCategory.ENERGETIC: {'tempo_range': (140, 200), 'energy_min': 0.8, 'valence': 0.7},
            MoodCategory.CALM: {'tempo_range': (60, 90), 'energy_min': 0.1, 'valence': 0.5},
            MoodCategory.AGGRESSIVE: {'tempo_range': (130, 180), 'energy_min': 0.9, 'valence': 0.3}
        }
        
        self.logger.info("MoodAnalyzer initialized")
    
    async def analyze_mood(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze musical mood and emotion"""



        try:
            # Extract mood-relevant features
            features = await self._extract_mood_features(audio_data)
            
            # Compute mood scores
            mood_scores = {}
            for mood, characteristics in self.mood_characteristics.items():
                score = self._compute_mood_score(features, characteristics)
                mood_scores[mood.value] = float(score)
            
            # Primary mood
            primary_mood = max(mood_scores.keys(), key=lambda x: mood_scores[x])
            
            # Emotional dimensions
            valence = self._compute_valence(features)  # Positive/negative
            arousal = self._compute_arousal(features)  # Energy/calm
            dominance = self._compute_dominance(features)  # Strong/weak
            
            analysis = {
                'primary_mood': primary_mood,
                'mood_confidence': mood_scores[primary_mood],
                'mood_scores': mood_scores,
                'emotional_dimensions': {
                    'valence': float(valence),
                    'arousal': float(arousal), 
                    'dominance': float(dominance)
                },
                'mood_intensity': float(max(mood_scores.values())),
                'emotional_complexity': float(np.std(list(mood_scores.values())))
            }
            
            self.logger.info(f"Analyzed mood: {primary_mood} (confidence: {mood_scores[primary_mood]:.2f})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Mood analysis failed: {e}")
            return {'primary_mood': 'neutral', 'mood_confidence': 0.0}
    
    async def _extract_mood_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract features relevant for mood analysis"""
        features = {}
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        features['tempo'] = float(tempo)
        
        # Energy (RMS)
        rms = librosa.feature.rms(y=audio_data)
        features['energy'] = float(np.mean(rms))
        
        # Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
        features['brightness'] = float(np.mean(centroid))
        
        # Chroma (harmony)
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        features['harmony_variance'] = float(np.var(chroma))
        features['harmony_mean'] = float(np.mean(chroma))
        
        # Zero crossing rate (roughness)
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        features['roughness'] = float(np.mean(zcr))
        
        # MFCC for timbral characteristics
        mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=5)
        for i in range(5):
            features[f'mfcc_{i}'] = float(np.mean(mfccs[i]))
        
        return features
    
    def _compute_mood_score(self, features: Dict[str, float], characteristics: Dict) -> float:
        """Compute mood score based on characteristics"""
        score = 0.0
        
        # Tempo score
        tempo = features.get('tempo', 120)
        tempo_min, tempo_max = characteristics['tempo_range']
        if tempo_min <= tempo <= tempo_max:
            score += 0.4
        else:
            distance = min(abs(tempo - tempo_min), abs(tempo - tempo_max))
            score += max(0, 0.4 - distance / 50.0)
        
        # Energy score
        energy = features.get('energy', 0.5)
        energy_min = characteristics['energy_min']
        if energy >= energy_min:
            score += 0.3
        else:
            score += 0.3 * (energy / energy_min)
        
        # Brightness influence
        brightness = features.get('brightness', 1000)
        normalized_brightness = min(1.0, brightness / 5000.0)
        score += normalized_brightness * 0.2
        
        # Harmony influence
        harmony_var = features.get('harmony_variance', 0.1)
        score += min(0.1, harmony_var * 10)
        
        return min(1.0, score)
    
    def _compute_valence(self, features: Dict[str, float]) -> float:
        """Compute valence (positive/negative emotion)"""
        # Higher tempo, energy, and brightness = more positive
        tempo_valence = min(1.0, features.get('tempo', 120) / 150.0)
        energy_valence = features.get('energy', 0.5)
        brightness_valence = min(1.0, features.get('brightness', 1000) / 3000.0)
        
        valence = (tempo_valence + energy_valence + brightness_valence) / 3.0
        return valence
    
    def _compute_arousal(self, features: Dict[str, float]) -> float:
        """Compute arousal (energy/activation level)"""
        # Energy and tempo contribute to arousal
        energy_arousal = features.get('energy', 0.5)
        tempo_arousal = min(1.0, features.get('tempo', 120) / 180.0)
        roughness_arousal = features.get('roughness', 0.1) * 10
        
        arousal = (energy_arousal + tempo_arousal + roughness_arousal) / 3.0
        return min(1.0, arousal)
    
    def _compute_dominance(self, features: Dict[str, float]) -> float:
        """Compute dominance (control/power)"""
        # Energy and low-frequency content contribute to dominance
        energy_dominance = features.get('energy', 0.5)
        bass_dominance = 1.0 - min(1.0, features.get('brightness', 1000) / 2000.0)
        
        dominance = (energy_dominance + bass_dominance) / 2.0
        return dominance
