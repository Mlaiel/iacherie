# conftest.py - Configuration globale des tests
# Created by: Fahed Mlaiel (mlaiel@live.de)
# © 2025 Fahed Mlaiel. All rights reserved.

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Environment setup
os.environ.setdefault("AUDIO_TEST_ENV", "test")
os.environ.setdefault("AUDIO_TEST_DEBUG", "true")
os.environ.setdefault("PYTHONPATH", str(backend_path))

@pytest.fixture
def sample_audio():
    """Generate standard test audio samples"""
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    return {
        "sine_440": np.sin(2 * np.pi * 440 * t),
        "white_noise": np.random.normal(0, 0.1, len(t)),
        "silence": np.zeros(len(t)),
        "sample_rate": sample_rate,
        "duration": duration
    }

@pytest.fixture
def temp_audio_file(tmp_path, sample_audio):
    """Create a temporary audio file"""
    import soundfile as sf
    
    file_path = tmp_path / "test_audio.wav"
    sf.write(file_path, sample_audio["sine_440"], sample_audio["sample_rate"])
    return file_path
