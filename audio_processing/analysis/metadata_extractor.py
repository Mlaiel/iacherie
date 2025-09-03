"""📊 Audio Metadata Extractor - Professional Audio Metadata Analysis

Advanced metadata extraction engine for comprehensive audio file information,
technical specifications, and content analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import librosa


@dataclass
class AudioMetadata:
    """
Complete audio metadata"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int]
    format: str
    file_size: int
    technical_specs: Dict[str, Any]
    content_analysis: Dict[str, Any]


class AudioMetadataExtractor:
    """
Professional audio metadata extraction engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("AudioMetadataExtractor initialized")
    
    async def extract_metadata(self, 
                             audio_data: np.ndarray,
                             sample_rate: int = 44100,
                             **kwargs) -> AudioMetadata:
        """Extract comprehensive audio metadata"""
        try:
            # Basic technical specs
            duration = len(audio_data) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            
            # Content analysis
            content_analysis = {
                'peak_amplitude': float(np.max(np.abs(audio_data))),
                'rms_level': float(np.sqrt(np.mean(audio_data ** 2))),
                'dynamic_range': float(20 * np.log10(
                    np.max(np.abs(audio_data)) / (np.percentile(np.abs(audio_data), 10) + 1e-10)
                )),
                'zero_crossings': int(np.sum(np.diff(np.signbit(audio_data))))
            }
            
            # Technical specifications
            technical_specs = {
                'nyquist_frequency': sample_rate // 2,
                'total_samples': len(audio_data),
                'estimated_bitrate': sample_rate * channels * 16,  # Assume 16-bit
                'signal_to_noise_ratio': float(content_analysis['rms_level'] - content_analysis.get('noise_floor', -60))
            }
            
            metadata = AudioMetadata(
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=kwargs.get('bit_depth', 16),
                format=kwargs.get('format', 'unknown'),
                file_size=kwargs.get('file_size', len(audio_data) * 2),  # Estimate
                technical_specs=technical_specs,
                content_analysis=content_analysis
            )
            
            self.logger.info(f"Extracted metadata: {duration:.2f}s, {sample_rate}Hz, {channels}ch")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            raise
