"""
🥁 Tempo Detector - Professional Tempo Detection & Analysis

Advanced tempo detection engine using multiple algorithms for accurate
beat-per-minute estimation and tempo stability analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple
import librosa


class TempoDetector:
    """Professional tempo detection engine"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.logger.info("TempoDetector initialized")
    
    async def detect_tempo(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Detect tempo and analyze stability"""



        try:
            # Primary tempo detection
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
            
            # Tempo stability analysis
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                tempo_stability = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
            else:
                tempo_stability = 0.0
            
            # Beat confidence
            onset_strength = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
            beat_strength = np.mean(onset_strength[beats]) if len(beats) > 0 else 0.0
            
            analysis = {
                'tempo_bpm': float(tempo),
                'tempo_confidence': float(min(1.0, beat_strength)),
                'tempo_stability': float(max(0.0, tempo_stability)),
                'beat_count': len(beats),
                'rhythm_regularity': float(tempo_stability)
            }
            
            self.logger.info(f"Detected tempo: {tempo:.1f} BPM")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Tempo detection failed: {e}")
            return {'tempo_bpm': 120.0, 'tempo_confidence': 0.0, 'tempo_stability': 0.0}
