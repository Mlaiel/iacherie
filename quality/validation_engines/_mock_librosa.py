#!/usr/bin/env python3
"""
Mock librosa pour éviter les erreurs d'import audio
"""

import numpy as np

def load(file_path, sr=22050):
    """Mock audio loading"""
    # Simulate audio data
    duration = 3.0  # 3 seconds
    samples = int(sr * duration)
    audio_data = np.random.random(samples) * 0.1  # Low amplitude noise
    return audio_data, sr

def stft(audio_data):
    """Mock STFT"""
    return np.random.random((1025, 100)) + 1j * np.random.random((1025, 100))

class feature:
    class mfcc:
        @staticmethod
        def mfcc(audio_data, sr=22050, n_mfcc=13):
            """Mock MFCC extraction"""
            return np.random.random((n_mfcc, 100))

class display:
    @staticmethod
    def waveshow(audio_data, sr=22050, **kwargs):
        """Mock waveform display"""
        pass
    
    @staticmethod
    def specshow(data, **kwargs):
        """Mock spectrogram display"""
        pass
