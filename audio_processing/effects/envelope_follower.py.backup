"""📊 Envelope Follower - Professional Audio Level Detection

High-quality envelope following for dynamic processing applications with
multiple detection modes and adaptive response characteristics.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
from typing import Optional


class EnvelopeFollower:
    """Professional envelope follower for dynamics processing"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.envelope = 0.0
        self.peak_hold = 0.0
        self.rms_buffer = np.zeros(1024)  # RMS calculation buffer
        self.rms_index = 0
        
    def process_peak(self, audio_data: np.ndarray, attack_time: float, release_time: float) -> np.ndarray:
        """Peak envelope following"""
        attack_coeff = np.exp(-1.0 / (attack_time * self.sample_rate))
        release_coeff = np.exp(-1.0 / (release_time * self.sample_rate))
        
        envelope = np.zeros_like(audio_data)
        current_envelope = self.envelope
        
        for i, sample in enumerate(np.abs(audio_data)):
            if sample > current_envelope:
                current_envelope = sample + (current_envelope - sample) * attack_coeff
            else:
                current_envelope = sample + (current_envelope - sample) * release_coeff
            
            envelope[i] = current_envelope
        
        self.envelope = current_envelope
        return envelope
    
    def process_rms(self, audio_data: np.ndarray, attack_time: float, release_time: float) -> np.ndarray:
        """RMS envelope following"""
        attack_coeff = np.exp(-1.0 / (attack_time * self.sample_rate))
        release_coeff = np.exp(-1.0 / (release_time * self.sample_rate))
        
        envelope = np.zeros_like(audio_data)
        current_envelope = self.envelope
        
        for i, sample in enumerate(audio_data):
            # Update RMS buffer
            self.rms_buffer[self.rms_index] = sample * sample
            self.rms_index = (self.rms_index + 1) % len(self.rms_buffer)
            
            # Calculate RMS
            rms_value = np.sqrt(np.mean(self.rms_buffer))
            
            if rms_value > current_envelope:
                current_envelope = rms_value + (current_envelope - rms_value) * attack_coeff
            else:
                current_envelope = rms_value + (current_envelope - rms_value) * release_coeff
            
            envelope[i] = current_envelope
        
        self.envelope = current_envelope
        return envelope
