"""🎤 Instrument Identifier - AI-Powered Musical Instrument Recognition

Advanced instrument identification engine using machine learning and signal processing
to detect and classify musical instruments in audio signals.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import librosa


class InstrumentCategory(Enum):
    """
Musical instrument categories"""

    STRINGS = "strings"
    WOODWINDS = "woodwinds" 
    BRASS = "brass"
    PERCUSSION = "percussion"
    KEYBOARD = "keyboard"
    VOCALS = "vocals"
    ELECTRONIC = "electronic"


@dataclass 
class InstrumentDetection:
    """Individual instrument detection result"""
    instrument: str
    category: InstrumentCategory
    confidence: float
    temporal_presence: List[Tuple[float, float]]  # (start, end) times
    spectral_signature: np.ndarray


class InstrumentIdentifier:
    """
Professional instrument identification engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Instrument spectral signatures (simplified)
        self.instrument_signatures = {
            'guitar': {'category': InstrumentCategory.STRINGS, 'freq_range': (80, 5000)},
            'bass': {'category': InstrumentCategory.STRINGS, 'freq_range': (40, 400)},
            'piano': {'category': InstrumentCategory.KEYBOARD, 'freq_range': (27, 4200)},
            'drums': {'category': InstrumentCategory.PERCUSSION, 'freq_range': (20, 20000)},
            'vocals': {'category': InstrumentCategory.VOCALS, 'freq_range': (100, 8000)},
            'violin': {'category': InstrumentCategory.STRINGS, 'freq_range': (200, 4000)},
            'trumpet': {'category': InstrumentCategory.BRASS, 'freq_range': (150, 3000)},
            'saxophone': {'category': InstrumentCategory.WOODWINDS, 'freq_range': (140, 2500)}
        }
        
        self.logger.info("InstrumentIdentifier initialized")
    
    async def identify_instruments(self, 
                                 audio_data: np.ndarray, 
                                 sample_rate: int = 44100) -> List[InstrumentDetection]:
        """Identify instruments in audio signal"""
        try:
            detections = []
            
            # Extract spectral features
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            freqs = librosa.fft_frequencies(sr=sample_rate)
            
            # Analyze each instrument signature
            for instrument, signature in self.instrument_signatures.items():
                confidence = self._compute_instrument_confidence(
                    magnitude, freqs, signature
                )
                
                if confidence > 0.3:  # Threshold for detection
                    detection = InstrumentDetection(
                        instrument=instrument,
                        category=signature['category'],
                        confidence=confidence,
                        temporal_presence=[(0.0, len(audio_data) / sample_rate)],
                        spectral_signature=magnitude.mean(axis=1)
                    )
                    detections.append(detection)
            
            # Sort by confidence
            detections.sort(key=lambda x: x.confidence, reverse=True)
            
            self.logger.info(f"Identified {len(detections)} instruments")
            return detections
            
        except Exception as e:
            self.logger.error(f"Instrument identification failed: {e}")
            return []
    
    def _compute_instrument_confidence(self, 
                                     magnitude: np.ndarray,
                                     freqs: np.ndarray, 
                                     signature: Dict) -> float:
        """Compute confidence for instrument detection"""
        freq_min, freq_max = signature['freq_range']
        
        # Find frequency bins in range
        freq_mask = (freqs >= freq_min) & (freqs <= freq_max)
        
        if not np.any(freq_mask):
            return 0.0
        
        # Energy in frequency range
        range_energy = np.mean(magnitude[freq_mask])
        total_energy = np.mean(magnitude)
        
        # Confidence based on relative energy
        confidence = range_energy / (total_energy + 1e-10)
        
        return float(min(1.0, confidence))
