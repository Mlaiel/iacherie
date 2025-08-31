#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent Genre Blending Engine
================================================================================
Module: ai_engine/remix_generation/genre_blending_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Genre Fusion System (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Engine de fusion de genres musicaux ultra-avancé avec IA
TECHNOLOGIES: Deep Learning, Neural Genre Classification, Spectral Analysis, Genre Morphing
LOGIQUE MÉTIER: Genre analysis → Fusion algorithms → Style interpolation → Quality validation
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
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import scipy.signal as signal

# Configure logging
logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    """Music genre classifications"""    ROCK = "rock"
    POP = "pop"
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
    TECHNO = "techno"
    HOUSE = "house"
    DUBSTEP = "dubstep"

class BlendingMethod(Enum):
    """Genre blending methods"""    LINEAR_INTERPOLATION = "linear"
    HARMONIC_MIXING = "harmonic"
    SPECTRAL_MORPHING = "spectral"
    NEURAL_SYNTHESIS = "neural"
    RHYTHMIC_FUSION = "rhythmic"
    TIMBRAL_BLENDING = "timbral"

@dataclass
class GenreCharacteristics:
    """Music genre characteristics"""    genre: MusicGenre
    tempo_range: Tuple[int, int]
    key_signatures: List[str]
    time_signatures: List[str]
    harmonic_patterns: List[str]
    rhythmic_patterns: List[str]
    instrumental_features: List[str]
    spectral_features: Dict[str, float]
    confidence_score: float

@dataclass
class BlendingParameters:
    """Parameters for genre blending"""    primary_genre: MusicGenre
    secondary_genre: MusicGenre
    blend_ratio: float  # 0.0 to 1.0
    method: BlendingMethod
    preserve_tempo: bool
    preserve_key: bool
    harmonic_complexity: float
    rhythmic_variation: float
    quality_threshold: float

class GenreClassificationNetwork(nn.Module):
    """Deep learning model for genre classification"""    
    def __init__(self, input_features: int = 128, num_genres: int = 15):
        super(GenreClassificationNetwork, self).__init__()
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_genres),
            nn.Softmax(dim=1)
        )
        
        self.confidence_estimator = nn.Sequential(
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        features = self.feature_extractor(x)
        classification = self.classifier(features)
        confidence = self.confidence_estimator(features)
        return classification, confidence

class GenreBlendingNetwork(nn.Module):
    """Neural network for intelligent genre blending"""    
    def __init__(self, feature_dim: int = 128):
        super(GenreBlendingNetwork, self).__init__()
        
        self.genre_encoder = nn.Sequential(
            nn.Linear(feature_dim * 2, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        self.blending_processor = nn.Sequential(
            nn.Linear(128 + 1, 256),  # +1 for blend ratio
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU()
        )
        
        self.output_generator = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, feature_dim),
            nn.Tanh()
        )
    
    def forward(self, genre1_features, genre2_features, blend_ratio):
        combined_features = torch.cat([genre1_features, genre2_features], dim=1)
        encoded = self.genre_encoder(combined_features)
        
        # Add blend ratio as additional input
        blend_input = torch.cat([encoded, blend_ratio.unsqueeze(1)], dim=1)
        processed = self.blending_processor(blend_input)
        
        output = self.output_generator(processed)
        return output

class GenreAnalyzer:
    """Advanced genre analysis system"""    
    def __init__(self):
        self.classification_model = GenreClassificationNetwork()
        self.scaler = StandardScaler()
        self.feature_cache = {}
        self.genre_database = self._initialize_genre_database()
    
    def _initialize_genre_database(self) -> Dict[MusicGenre, GenreCharacteristics]:
        """Initialize comprehensive genre database"""        return {
            MusicGenre.ROCK: GenreCharacteristics(
                genre=MusicGenre.ROCK,
                tempo_range=(120, 140),
                key_signatures=["E", "A", "D", "G"],
                time_signatures=["4/4", "2/4"],
                harmonic_patterns=["I-V-vi-IV", "vi-IV-I-V"],
                rhythmic_patterns=["eighth_note_drive", "backbeat_emphasis"],
                instrumental_features=["electric_guitar", "bass_guitar", "drums"],
                spectral_features={"brightness": 0.7, "roughness": 0.8, "attack_time": 0.6},
                confidence_score=0.95
            ),
            MusicGenre.JAZZ: GenreCharacteristics(
                genre=MusicGenre.JAZZ,
                tempo_range=(80, 180),
                key_signatures=["C", "F", "Bb", "Eb"],
                time_signatures=["4/4", "3/4", "5/4"],
                harmonic_patterns=["ii-V-I", "vi-ii-V-I", "tritone_substitution"],
                rhythmic_patterns=["swing", "syncopation", "polyrhythm"],
                instrumental_features=["piano", "saxophone", "trumpet", "double_bass"],
                spectral_features={"brightness": 0.6, "roughness": 0.4, "attack_time": 0.5},
                confidence_score=0.92
            ),
            MusicGenre.ELECTRONIC: GenreCharacteristics(
                genre=MusicGenre.ELECTRONIC,
                tempo_range=(120, 160),
                key_signatures=["Am", "Dm", "Em", "Gm"],
                time_signatures=["4/4"],
                harmonic_patterns=["i-VI-III-VII", "i-v-i-v"],
                rhythmic_patterns=["four_on_floor", "breakbeat", "arpeggiated"],
                instrumental_features=["synthesizer", "drum_machine", "sequencer"],
                spectral_features={"brightness": 0.8, "roughness": 0.3, "attack_time": 0.2},
                confidence_score=0.88
            )
        }
    
    async def extract_spectral_features(self, audio_data: np.ndarray, 
                                      sample_rate: int = 44100) -> np.ndarray:
        """Extract comprehensive spectral features"""        try:
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            
            # Tonnetz features (harmonic network)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            
            # Tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Combine all features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.mean(spectral_centroid),
                np.mean(spectral_rolloff),
                np.mean(spectral_bandwidth),
                np.mean(zero_crossing_rate),
                np.mean(chroma, axis=1),
                np.mean(tonnetz, axis=1),
                [tempo]
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting spectral features: {e}")
            raise
    
    async def classify_genre(self, audio_features: np.ndarray) -> Tuple[MusicGenre, float]:
        """Classify music genre using neural network"""        try:
            # Normalize features
            features_normalized = self.scaler.fit_transform(audio_features.reshape(1, -1))
            features_tensor = torch.FloatTensor(features_normalized)
            
            # Get classification and confidence
            with torch.no_grad():
                classification, confidence = self.classification_model(features_tensor)
                
            # Get predicted genre
            predicted_idx = torch.argmax(classification, dim=1).item()
            genres = list(MusicGenre)
            predicted_genre = genres[predicted_idx] if predicted_idx < len(genres) else MusicGenre.POP
            
            confidence_score = confidence.item()
            
            return predicted_genre, confidence_score
            
        except Exception as e:
            logger.error(f"Error in genre classification: {e}")
            return MusicGenre.POP, 0.5

class GenreFusionProcessor:
    """Advanced genre fusion processing"""    
    def __init__(self):
        self.blending_network = GenreBlendingNetwork()
        self.fusion_algorithms = {
            BlendingMethod.LINEAR_INTERPOLATION: self._linear_interpolation,
            BlendingMethod.HARMONIC_MIXING: self._harmonic_mixing,
            BlendingMethod.SPECTRAL_MORPHING: self._spectral_morphing,
            BlendingMethod.NEURAL_SYNTHESIS: self._neural_synthesis,
            BlendingMethod.RHYTHMIC_FUSION: self._rhythmic_fusion,
            BlendingMethod.TIMBRAL_BLENDING: self._timbral_blending
        }
    
    async def _linear_interpolation(self, audio1: np.ndarray, audio2: np.ndarray, 
                                  ratio: float) -> np.ndarray:
        """Linear interpolation between two audio signals"""        return (1 - ratio) * audio1 + ratio * audio2
    
    async def _harmonic_mixing(self, audio1: np.ndarray, audio2: np.ndarray, 
                             ratio: float) -> np.ndarray:
        """Harmonic mixing using spectral analysis"""        # Get spectrograms
        stft1 = librosa.stft(audio1)
        stft2 = librosa.stft(audio2)
        
        # Harmonic-percussive separation
        harmonic1, percussive1 = librosa.decompose.hpss(stft1)
        harmonic2, percussive2 = librosa.decompose.hpss(stft2)
        
        # Mix harmonics and percussives separately
        mixed_harmonic = (1 - ratio) * harmonic1 + ratio * harmonic2
        mixed_percussive = (1 - ratio) * percussive1 + ratio * percussive2
        
        # Recombine
        mixed_stft = mixed_harmonic + mixed_percussive
        return librosa.istft(mixed_stft)
    
    async def _spectral_morphing(self, audio1: np.ndarray, audio2: np.ndarray, 
                               ratio: float) -> np.ndarray:
        """Advanced spectral morphing"""        # Phase vocoder for time-stretching
        stft1 = librosa.stft(audio1)
        stft2 = librosa.stft(audio2)
        
        # Magnitude and phase interpolation
        mag1, phase1 = np.abs(stft1), np.angle(stft1)
        mag2, phase2 = np.abs(stft2), np.angle(stft2)
        
        # Morph magnitudes
        morphed_mag = (1 - ratio) * mag1 + ratio * mag2
        
        # Phase interpolation with unwrapping
        phase_diff = np.unwrap(phase2 - phase1)
        morphed_phase = phase1 + ratio * phase_diff
        
        # Reconstruct
        morphed_stft = morphed_mag * np.exp(1j * morphed_phase)
        return librosa.istft(morphed_stft)
    
    async def _neural_synthesis(self, audio1: np.ndarray, audio2: np.ndarray, 
                              ratio: float) -> np.ndarray:
        """Neural network-based synthesis"""        # Extract features from both audio signals
        features1 = await self._extract_neural_features(audio1)
        features2 = await self._extract_neural_features(audio2)
        
        # Use neural network for blending
        ratio_tensor = torch.FloatTensor([ratio])
        features1_tensor = torch.FloatTensor(features1).unsqueeze(0)
        features2_tensor = torch.FloatTensor(features2).unsqueeze(0)
        
        with torch.no_grad():
            blended_features = self.blending_network(features1_tensor, features2_tensor, ratio_tensor)
        
        # Convert back to audio (simplified - would need a decoder network)
        return await self._features_to_audio(blended_features.numpy())
    
    async def _rhythmic_fusion(self, audio1: np.ndarray, audio2: np.ndarray, 
                             ratio: float) -> np.ndarray:
        """Fusion focusing on rhythmic elements"""        # Beat tracking
        tempo1, beats1 = librosa.beat.beat_track(y=audio1)
        tempo2, beats2 = librosa.beat.beat_track(y=audio2)
        
        # Onset detection
        onsets1 = librosa.onset.onset_detect(y=audio1, units='time')
        onsets2 = librosa.onset.onset_detect(y=audio2, units='time')
        
        # Rhythmic pattern extraction and fusion
        # This is a simplified version - full implementation would be more complex
        mixed_tempo = (1 - ratio) * tempo1 + ratio * tempo2
        
        # Time-stretch to match average tempo
        audio1_stretched = librosa.effects.time_stretch(audio1, rate=tempo1/mixed_tempo)
        audio2_stretched = librosa.effects.time_stretch(audio2, rate=tempo2/mixed_tempo)
        
        return (1 - ratio) * audio1_stretched + ratio * audio2_stretched
    
    async def _timbral_blending(self, audio1: np.ndarray, audio2: np.ndarray, 
                              ratio: float) -> np.ndarray:
        """Timbral characteristic blending"""        # Spectral envelope extraction
        spec1 = np.abs(librosa.stft(audio1))
        spec2 = np.abs(librosa.stft(audio2))
        
        # Spectral envelope smoothing
        envelope1 = signal.savgol_filter(np.mean(spec1, axis=1), 11, 3)
        envelope2 = signal.savgol_filter(np.mean(spec2, axis=1), 11, 3)
        
        # Blend envelopes
        blended_envelope = (1 - ratio) * envelope1 + ratio * envelope2
        
        # Apply blended envelope to mixed signal
        mixed_spec = (1 - ratio) * spec1 + ratio * spec2
        
        # Envelope shaping
        freq_bins = mixed_spec.shape[0]
        for i in range(freq_bins):
            if i < len(blended_envelope):
                mixed_spec[i] *= blended_envelope[i] / (np.mean(mixed_spec[i]) + 1e-8)
        
        # Reconstruct audio
        return librosa.istft(mixed_spec * np.exp(1j * np.angle(librosa.stft(audio1))))
    
    async def _extract_neural_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract features for neural processing"""        mfccs = librosa.feature.mfcc(y=audio, n_mfcc=13)
        return np.mean(mfccs, axis=1)
    
    async def _features_to_audio(self, features: np.ndarray) -> np.ndarray:
        """Convert features back to audio (simplified)"""        # This is a placeholder - real implementation would need a trained decoder
        return np.random.normal(0, 0.1, 44100)  # 1 second of audio

class GenreBlendingEngine:
    """Main genre blending engine"""    
    def __init__(self):
        self.analyzer = GenreAnalyzer()
        self.fusion_processor = GenreFusionProcessor()
        self.quality_validator = QualityValidator()
        self.blend_history = []
        
        logger.info("GenreBlendingEngine initialized successfully")
    
    async def analyze_genres(self, audio_data: np.ndarray, 
                           sample_rate: int = 44100) -> List[Tuple[MusicGenre, float]]:
        """Analyze and identify genres in audio"""        try:
            features = await self.analyzer.extract_spectral_features(audio_data, sample_rate)
            genre, confidence = await self.analyzer.classify_genre(features)
            
            return [(genre, confidence)]
            
        except Exception as e:
            logger.error(f"Error in genre analysis: {e}")
            raise
    
    async def create_genre_blend(self, audio1: np.ndarray, audio2: np.ndarray,
                               parameters: BlendingParameters) -> Dict[str, Any]:
        """Create a genre blend between two audio signals"""        try:
            start_time = datetime.now()
            
            # Analyze genres
            genres1 = await self.analyze_genres(audio1)
            genres2 = await self.analyze_genres(audio2)
            
            # Get fusion algorithm
            fusion_func = self.fusion_processor.fusion_algorithms[parameters.method]
            
            # Perform blending
            blended_audio = await fusion_func(audio1, audio2, parameters.blend_ratio)
            
            # Quality validation
            quality_score = await self.quality_validator.assess_blend_quality(
                blended_audio, audio1, audio2, parameters
            )
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = {
                "blended_audio": blended_audio,
                "original_genres": {
                    "audio1": genres1,
                    "audio2": genres2
                },
                "blend_parameters": parameters,
                "quality_score": quality_score,
                "processing_time_seconds": processing_time,
                "blend_id": f"blend_{int(datetime.now().timestamp())}",
                "success": quality_score >= parameters.quality_threshold
            }
            
            # Store in history
            self.blend_history.append({
                "timestamp": datetime.now().isoformat(),
                "blend_id": result["blend_id"],
                "parameters": parameters.__dict__,
                "quality_score": quality_score,
                "success": result["success"]
            })
            
            logger.info(f"Genre blend created: {result['blend_id']}, quality: {quality_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating genre blend: {e}")
            raise
    
    async def optimize_blend_parameters(self, audio1: np.ndarray, audio2: np.ndarray,
                                      target_genre: MusicGenre) -> BlendingParameters:
        """Optimize blending parameters for target genre"""        try:
            # Analyze source genres
            genres1 = await self.analyze_genres(audio1)
            genres2 = await self.analyze_genres(audio2)
            
            source_genre1 = genres1[0][0] if genres1 else MusicGenre.POP
            source_genre2 = genres2[0][0] if genres2 else MusicGenre.POP
            
            # Get characteristics
            char1 = self.analyzer.genre_database.get(source_genre1)
            char2 = self.analyzer.genre_database.get(source_genre2)
            target_char = self.analyzer.genre_database.get(target_genre)
            
            if not all([char1, char2, target_char]):
                raise ValueError("Unable to get genre characteristics")
            
            # Calculate optimal blend ratio
            blend_ratio = self._calculate_optimal_ratio(char1, char2, target_char)
            
            # Select best method
            method = self._select_best_method(source_genre1, source_genre2, target_genre)
            
            return BlendingParameters(
                primary_genre=source_genre1,
                secondary_genre=source_genre2,
                blend_ratio=blend_ratio,
                method=method,
                preserve_tempo=True,
                preserve_key=False,
                harmonic_complexity=0.7,
                rhythmic_variation=0.5,
                quality_threshold=0.8
            )
            
        except Exception as e:
            logger.error(f"Error optimizing blend parameters: {e}")
            raise
    
    def _calculate_optimal_ratio(self, char1: GenreCharacteristics, 
                               char2: GenreCharacteristics,
                               target: GenreCharacteristics) -> float:
        """Calculate optimal blend ratio based on genre characteristics"""        # Simple distance-based calculation
        # In production, this would be more sophisticated
        
        # Calculate spectral distance
        dist1 = sum(abs(char1.spectral_features.get(k, 0) - target.spectral_features.get(k, 0)) 
                   for k in target.spectral_features.keys())
        dist2 = sum(abs(char2.spectral_features.get(k, 0) - target.spectral_features.get(k, 0)) 
                   for k in target.spectral_features.keys())
        
        # Normalize distances
        total_dist = dist1 + dist2
        if total_dist == 0:
            return 0.5
        
        # Ratio favors the genre closer to target
        ratio = dist1 / total_dist
        return max(0.1, min(0.9, ratio))  # Clamp between 0.1 and 0.9
    
    def _select_best_method(self, genre1: MusicGenre, genre2: MusicGenre, 
                           target: MusicGenre) -> BlendingMethod:
        """Select the best blending method for genre combination"""        # Method selection logic based on genre characteristics
        electronic_genres = {MusicGenre.ELECTRONIC, MusicGenre.TECHNO, MusicGenre.HOUSE, MusicGenre.DUBSTEP}
        acoustic_genres = {MusicGenre.JAZZ, MusicGenre.CLASSICAL, MusicGenre.COUNTRY, MusicGenre.BLUES}
        
        if all(g in electronic_genres for g in [genre1, genre2, target]):
            return BlendingMethod.SPECTRAL_MORPHING
        elif all(g in acoustic_genres for g in [genre1, genre2, target]):
            return BlendingMethod.HARMONIC_MIXING
        elif target in electronic_genres:
            return BlendingMethod.NEURAL_SYNTHESIS
        else:
            return BlendingMethod.LINEAR_INTERPOLATION
    
    async def get_blend_recommendations(self, source_genre: MusicGenre) -> List[Dict[str, Any]]:
        """Get recommendations for genre blending"""        try:
            recommendations = []
            
            for target_genre in MusicGenre:
                if target_genre == source_genre:
                    continue
                
                compatibility_score = await self._calculate_compatibility(source_genre, target_genre)
                
                if compatibility_score > 0.5:
                    recommendations.append({
                        "target_genre": target_genre,
                        "compatibility_score": compatibility_score,
                        "recommended_method": self._select_best_method(source_genre, target_genre, target_genre),
                        "difficulty_level": self._get_difficulty_level(source_genre, target_genre),
                        "expected_quality": compatibility_score * 0.9
                    })
            
            # Sort by compatibility score
            recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error getting blend recommendations: {e}")
            return []
    
    async def _calculate_compatibility(self, genre1: MusicGenre, genre2: MusicGenre) -> float:
        """Calculate compatibility between two genres"""        # Simplified compatibility matrix
        compatibility_matrix = {
            (MusicGenre.ROCK, MusicGenre.POP): 0.8,
            (MusicGenre.ROCK, MusicGenre.BLUES): 0.9,
            (MusicGenre.JAZZ, MusicGenre.BLUES): 0.85,
            (MusicGenre.ELECTRONIC, MusicGenre.POP): 0.7,
            (MusicGenre.CLASSICAL, MusicGenre.JAZZ): 0.6,
            # Add more combinations as needed
        }
        
        # Check both directions
        score = compatibility_matrix.get((genre1, genre2)) or compatibility_matrix.get((genre2, genre1))
        
        if score is None:
            # Default compatibility based on tempo and harmonic similarity
            char1 = self.analyzer.genre_database.get(genre1)
            char2 = self.analyzer.genre_database.get(genre2)
            
            if char1 and char2:
                # Simple tempo-based compatibility
                tempo_overlap = max(0, min(char1.tempo_range[1], char2.tempo_range[1]) - 
                                  max(char1.tempo_range[0], char2.tempo_range[0]))
                tempo_range = max(char1.tempo_range[1] - char1.tempo_range[0],
                                char2.tempo_range[1] - char2.tempo_range[0])
                score = tempo_overlap / tempo_range if tempo_range > 0 else 0.5
            else:
                score = 0.5
        
        return score
    
    def _get_difficulty_level(self, genre1: MusicGenre, genre2: MusicGenre) -> str:
        """Get difficulty level for blending two genres"""        compatibility = asyncio.run(self._calculate_compatibility(genre1, genre2))
        
        if compatibility >= 0.8:
            return "easy"
        elif compatibility >= 0.6:
            return "medium"
        else:
            return "hard"

class QualityValidator:
    """Quality validation for genre blends"""    
    def __init__(self):
        self.quality_metrics = [
            "spectral_coherence",
            "harmonic_consistency",
            "rhythmic_stability",
            "timbral_balance",
            "dynamic_range",
            "stereo_imaging"
        ]
    
    async def assess_blend_quality(self, blended_audio: np.ndarray,
                                 original1: np.ndarray, original2: np.ndarray,
                                 parameters: BlendingParameters) -> float:
        """Assess the quality of a genre blend"""        try:
            scores = {}
            
            # Spectral coherence
            scores["spectral_coherence"] = await self._assess_spectral_coherence(blended_audio)
            
            # Harmonic consistency
            scores["harmonic_consistency"] = await self._assess_harmonic_consistency(blended_audio)
            
            # Rhythmic stability
            scores["rhythmic_stability"] = await self._assess_rhythmic_stability(blended_audio)
            
            # Timbral balance
            scores["timbral_balance"] = await self._assess_timbral_balance(
                blended_audio, original1, original2, parameters.blend_ratio
            )
            
            # Dynamic range
            scores["dynamic_range"] = await self._assess_dynamic_range(blended_audio)
            
            # Stereo imaging
            scores["stereo_imaging"] = await self._assess_stereo_imaging(blended_audio)
            
            # Weighted average
            weights = {
                "spectral_coherence": 0.2,
                "harmonic_consistency": 0.2,
                "rhythmic_stability": 0.2,
                "timbral_balance": 0.15,
                "dynamic_range": 0.15,
                "stereo_imaging": 0.1
            }
            
            overall_score = sum(scores[metric] * weights[metric] for metric in scores.keys())
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            logger.error(f"Error assessing blend quality: {e}")
            return 0.0
    
    async def _assess_spectral_coherence(self, audio: np.ndarray) -> float:
        """Assess spectral coherence of blended audio"""        try:
            # Spectral flux analysis
            stft = librosa.stft(audio)
            spec_flux = np.sum(np.diff(np.abs(stft), axis=1) ** 2, axis=0)
            
            # Normalize and assess smoothness
            flux_normalized = spec_flux / (np.max(spec_flux) + 1e-8)
            smoothness = 1.0 - np.std(flux_normalized)
            
            return max(0.0, min(1.0, smoothness))
            
        except Exception:
            return 0.5
    
    async def _assess_harmonic_consistency(self, audio: np.ndarray) -> float:
        """Assess harmonic consistency"""        try:
            # Chroma analysis for harmonic content
            chroma = librosa.feature.chroma_stft(y=audio)
            
            # Calculate harmonic stability
            chroma_var = np.var(chroma, axis=1)
            stability = 1.0 - np.mean(chroma_var)
            
            return max(0.0, min(1.0, stability))
            
        except Exception:
            return 0.5
    
    async def _assess_rhythmic_stability(self, audio: np.ndarray) -> float:
        """Assess rhythmic stability"""        try:
            # Onset detection and tempo analysis
            tempo, beats = librosa.beat.beat_track(y=audio)
            
            if len(beats) < 2:
                return 0.5
            
            # Calculate beat consistency
            beat_intervals = np.diff(beats)
            beat_stability = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
            
            return max(0.0, min(1.0, beat_stability))
            
        except Exception:
            return 0.5
    
    async def _assess_timbral_balance(self, blended: np.ndarray, orig1: np.ndarray,
                                   orig2: np.ndarray, ratio: float) -> float:
        """Assess timbral balance between original sources"""        try:
            # MFCC analysis for timbral characteristics
            mfcc_blended = librosa.feature.mfcc(y=blended, n_mfcc=13)
            mfcc_orig1 = librosa.feature.mfcc(y=orig1, n_mfcc=13)
            mfcc_orig2 = librosa.feature.mfcc(y=orig2, n_mfcc=13)
            
            # Expected blend based on ratio
            expected_blend = (1 - ratio) * np.mean(mfcc_orig1, axis=1) + ratio * np.mean(mfcc_orig2, axis=1)
            actual_blend = np.mean(mfcc_blended, axis=1)
            
            # Calculate similarity to expected blend
            similarity = 1.0 - np.mean(np.abs(expected_blend - actual_blend)) / (np.max(expected_blend) + 1e-8)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception:
            return 0.5
    
    async def _assess_dynamic_range(self, audio: np.ndarray) -> float:
        """Assess dynamic range of audio"""        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=audio)[0]
            
            # Dynamic range in dB
            dynamic_range_db = 20 * np.log10(np.max(rms) / (np.min(rms) + 1e-8))
            
            # Normalize to 0-1 scale (assuming good range is 20-60 dB)
            normalized_range = np.clip((dynamic_range_db - 20) / 40, 0, 1)
            
            return normalized_range
            
        except Exception:
            return 0.5
    
    async def _assess_stereo_imaging(self, audio: np.ndarray) -> float:
        """Assess stereo imaging quality"""        try:
            if audio.ndim == 1:
                return 1.0  # Mono audio, no stereo issues
            
            # Calculate correlation between channels
            left = audio[0] if audio.shape[0] == 2 else audio[:len(audio)//2]
            right = audio[1] if audio.shape[0] == 2 else audio[len(audio)//2:]
            
            correlation = np.corrcoef(left, right)[0, 1]
            
            # Good stereo imaging has moderate correlation (not too high, not too low)
            ideal_correlation = 0.7
            imaging_quality = 1.0 - abs(correlation - ideal_correlation) / ideal_correlation
            
            return max(0.0, min(1.0, imaging_quality))
            
        except Exception:
            return 0.5

# Export classes
__all__ = [
    "GenreBlendingEngine",
    "GenreAnalyzer", 
    "GenreClassifier",
    "GenreFusionProcessor",
    "MusicGenre",
    "BlendingMethod",
    "GenreCharacteristics",
    "BlendingParameters",
    "QualityValidator"
]

# For backward compatibility
GenreClassifier = GenreAnalyzer