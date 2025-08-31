"""🎹 Key Detector - Professional Musical Key Detection

Advanced key detection engine for identifying musical key signatures,
mode analysis, and tonal characteristics of audio signals.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Dict, Optional
import librosa


class KeyDetector:
    """Professional musical key detection engine"""    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Key templates (Krumhansl-Schmuckler)
        self.major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        self.minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        self.logger.info("KeyDetector initialized")
    
    async def detect_key(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Detect musical key"""        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Normalize chroma
            chroma_mean = chroma_mean / (np.sum(chroma_mean) + 1e-10)
            
            # Test all keys
            correlations = []
            
            # Major keys
            for shift in range(12):
                template = np.roll(self.major_profile, shift)
                template = np.array(template) / np.sum(template)
                correlation = np.corrcoef(chroma_mean, template)[0, 1]
                correlations.append(('major', shift, correlation if not np.isnan(correlation) else 0))
            
            # Minor keys  
            for shift in range(12):
                template = np.roll(self.minor_profile, shift)
                template = np.array(template) / np.sum(template)
                correlation = np.corrcoef(chroma_mean, template)[0, 1]
                correlations.append(('minor', shift, correlation if not np.isnan(correlation) else 0))
            
            # Find best match
            best_match = max(correlations, key=lambda x: x[2])
            mode, key_shift, confidence = best_match
            
            key_name = self.note_names[key_shift]
            detected_key = f"{key_name} {mode}"
            
            analysis = {
                'detected_key': detected_key,
                'confidence': float(confidence),
                'mode': mode,
                'tonic': key_name,
                'chroma_profile': chroma_mean.tolist(),
                'key_strength': float(confidence)
            }
            
            self.logger.info(f"Detected key: {detected_key} (confidence: {confidence:.2f})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Key detection failed: {e}")
            return {'detected_key': 'C major', 'confidence': 0.0}
