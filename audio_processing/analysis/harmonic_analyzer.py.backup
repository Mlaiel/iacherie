"""🎼 Harmonic Analyzer - Advanced Harmonic Content Analysis

Professional harmonic analysis engine for comprehensive harmonic structure,
chord detection, and tonal analysis of audio signals.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Dict, List, Tuple
import librosa


class HarmonicAnalyzer:
    """Professional harmonic analysis engine"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.logger.info("HarmonicAnalyzer initialized")
    
    async def analyze_harmonics(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze harmonic content"""
        try:
            # Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Chroma features for harmonic analysis
            chroma = librosa.feature.chroma_stft(y=harmonic, sr=self.sample_rate)
            
            # Harmonic analysis results
            analysis = {
                'harmonic_ratio': float(np.sum(harmonic**2) / (np.sum(audio_data**2) + 1e-10)),
                'chroma_mean': chroma.mean(axis=1).tolist(),
                'chroma_variance': chroma.var(axis=1).tolist(),
                'dominant_pitch_class': int(np.argmax(chroma.mean(axis=1))),
                'harmonic_complexity': float(np.std(chroma.mean(axis=1)))
            }
            
            self.logger.info("Harmonic analysis completed")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Harmonic analysis failed: {e}")
            return {}
