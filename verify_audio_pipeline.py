#!/usr/bin/env python3
"""
Audio Processing Pipeline Verification

Simple verification that all modules can be imported and initialized.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

def test_imports():
    """Test that all modules can be imported"""
    print("🎵 Audio Processing Pipeline Verification")
    print("=" * 50)
    
    try:
        print("Testing module imports...")
        
        # Test processors
        from backend.services.audio.processors import VoiceAnalyzer, AudioFingerprint, NoiseReduction, MasteringEngine
        print("✅ Processors imported successfully")
        
        # Test protection
        from backend.services.audio.protection import WatermarkEngine, VoiceProtection
        print("✅ Protection modules imported successfully")
        
        # Test distribution
        from backend.services.audio.distribution import StreamingOptimizer
        print("✅ Distribution modules imported successfully")
        
        # Test main module
        from backend.services.audio import (
            VoiceAnalyzer, AudioFingerprint, NoiseReduction, MasteringEngine,
            WatermarkEngine, VoiceProtection, StreamingOptimizer
        )
        print("✅ Main audio module imported successfully")
        
        print("\nTesting module initialization...")
        
        # Test initialization
        voice_analyzer = VoiceAnalyzer()
        print("✅ VoiceAnalyzer initialized")
        
        audio_fingerprint = AudioFingerprint()
        print("✅ AudioFingerprint initialized")
        
        noise_reduction = NoiseReduction()
        print("✅ NoiseReduction initialized")
        
        mastering_engine = MasteringEngine()
        print("✅ MasteringEngine initialized")
        
        watermark_engine = WatermarkEngine()
        print("✅ WatermarkEngine initialized")
        
        voice_protection = VoiceProtection()
        print("✅ VoiceProtection initialized")
        
        streaming_optimizer = StreamingOptimizer()
        print("✅ StreamingOptimizer initialized")
        
        print("\n🎉 ALL MODULES VERIFIED SUCCESSFULLY!")
        print("\nThe audio processing pipeline is ready for use.")
        print("\nAvailable components:")
        print("  📊 VoiceAnalyzer - AI voice analysis")
        print("  🔍 AudioFingerprint - Audio fingerprinting")
        print("  🔇 NoiseReduction - Audio cleaning")
        print("  🎛️ MasteringEngine - Automatic mastering")
        print("  🏷️ WatermarkEngine - Inaudible watermarking")
        print("  🛡️ VoiceProtection - Voice cloning protection")
        print("  📡 StreamingOptimizer - Streaming optimization")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_directory_structure():
    """Test that the directory structure is correct"""
    import os
    
    print("\nVerifying directory structure...")
    
    base_path = "backend/services/audio"
    expected_structure = {
        "": ["__init__.py"],
        "processors": ["__init__.py", "voice_analyzer.py", "audio_fingerprint.py", "noise_reduction.py", "mastering_engine.py"],
        "protection": ["__init__.py", "watermark_engine.py", "voice_protection.py"],
        "distribution": ["__init__.py", "streaming_optimizer.py"]
    }
    
    all_present = True
    
    for subdir, files in expected_structure.items():
        dir_path = os.path.join(base_path, subdir)
        print(f"  Checking {dir_path}/...")
        
        for file in files:
            file_path = os.path.join(dir_path, file)
            if os.path.exists(file_path):
                print(f"    ✅ {file}")
            else:
                print(f"    ❌ {file} MISSING")
                all_present = False
    
    if all_present:
        print("✅ Directory structure is correct")
    else:
        print("❌ Directory structure has missing files")
    
    return all_present

if __name__ == "__main__":
    success = test_imports()
    structure_ok = test_directory_structure()
    
    if success and structure_ok:
        print("\n🚀 Audio Processing Pipeline is ready for production!")
        exit(0)
    else:
        print("\n❌ There are issues with the audio processing pipeline")
        exit(1)