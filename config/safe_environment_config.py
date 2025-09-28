#!/usr/bin/env python3
"""
Configuration professionnelle simplifiée sans import TensorFlow multiple
Correction authentique des warnings sans crash
"""

import os
import sys

def configure_environment_variables():
    """Configuration des variables d'environnement pour CPU optimal"""
    
    print("🔧 CONFIGURATION ENVIRONNEMENT - Corrections authentiques")
    print("="*60)
    
    # Configuration TensorFlow pour CPU
    env_vars = {
        'CUDA_VISIBLE_DEVICES': '',
        'TF_CPP_MIN_LOG_LEVEL': '2',
        'TF_ENABLE_ONEDNN_OPTS': '0',
        'TF_FORCE_GPU_ALLOW_GROWTH': 'false',
        'TF_NUM_INTEROP_THREADS': '0',
        'TF_NUM_INTRAOP_THREADS': '0',
        'ESSENTIA_LOGGING_LEVEL': 'ERROR'
    }
    
    applied_count = 0
    for var, value in env_vars.items():
        try:
            os.environ[var] = value
            print(f"✅ {var} = {value}")
            applied_count += 1
        except Exception as e:
            print(f"⚠️  {var}: {e}")
    
    print("="*60)
    print(f"📊 Variables configurées: {applied_count}/{len(env_vars)}")
    
    # Test versions des packages sans import problématique
    try:
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
    except ImportError:
        print("⚠️  NumPy non disponible")
    
    try:
        import scipy
        print(f"✅ SciPy version: {scipy.__version__}")
    except ImportError:
        print("⚠️  SciPy non disponible")
    
    return applied_count == len(env_vars)

if __name__ == "__main__":
    success = configure_environment_variables()
    if success:
        print("🎉 Configuration environnement réussie!")
    else:
        print("⚠️  Configuration partielle")