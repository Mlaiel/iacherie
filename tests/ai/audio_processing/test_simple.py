# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Simple pytest-compatible test
Created by: Fahed Mlaiel (mlaiel@live.de)
"""
import numpy as np

def test_basic_audio():
    """Test basic audio generation"""
    # Generate simple sine wave
    sr = 44100
    t = np.linspace(0, 1, sr)
    audio = np.sin(2 * np.pi * 440 * t)
    
    # Validate
    assert len(audio) == sr
    assert np.max(audio) <= 1.0
    assert np.min(audio) >= -1.0
    
    print(f"✅ Generated {len(audio)} samples")

def test_audio_rms():
    """Test RMS calculation"""
    sr = 44100
    t = np.linspace(0, 1, sr)
    audio = np.sin(2 * np.pi * 440 * t)
    
    rms = np.sqrt(np.mean(audio**2))
    
    # RMS of sine wave should be ~0.707
    assert 0.7 < rms < 0.71
    
    print(f"✅ RMS: {rms:.6f}")

def test_fft_peak():
    """Test FFT peak detection"""
    sr = 44100
    freq = 440
    t = np.linspace(0, 1, sr)
    audio = np.sin(2 * np.pi * freq * t)
    
    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(audio), 1/sr)
    
    magnitude = np.abs(fft)
    peak_idx = np.argmax(magnitude[1:len(magnitude)//2]) + 1
    detected_freq = freqs[peak_idx]
    
    assert abs(detected_freq - freq) < 1
    
    print(f"✅ Detected freq: {detected_freq:.1f} Hz")

if __name__ == "__main__":
    print("🎵 Running simple audio tests...")
    test_basic_audio()
    test_audio_rms()
    test_fft_peak()
    print("✅ All tests passed!")
