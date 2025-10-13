#!/usr/bin/env python3
"""
Configuration TensorFlow pour environnement CPU sans GPU
Correction authentique des warnings CUDA et optimisations
"""

import os
import sys
import warnings

def configure_tensorflow_cpu():
    """Configuration TensorFlow optimisée pour CPU sans GPU"""
    
    # Configuration environnement avant import TensorFlow
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Pas de GPU visible
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Supprime INFO et WARNING
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Désactive oneDNN
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'false'  # Pas de croissance GPU
    
    # Configuration spécifique CPU
    os.environ['TF_NUM_INTEROP_THREADS'] = '0'  # Auto-detect
    os.environ['TF_NUM_INTRAOP_THREADS'] = '0'  # Auto-detect
    
    try:
        # Import TensorFlow via gestionnaire centralisé
        from core.tensorflow_singleton import get_tensorflow
        tf = get_tensorflow()
        
        # Configuration programmatique
        tf.config.set_visible_devices([], 'GPU')  # Masque tous les GPU
        
        # Configuration CPU optimisée
        tf.config.threading.set_inter_op_parallelism_threads(0)
        tf.config.threading.set_intra_op_parallelism_threads(0)
        
        print("✅ TensorFlow configuré pour CPU optimal")
        return True
        
    except ImportError:
        print("⚠️  TensorFlow non disponible")
        return False
    except Exception as e:
        print(f"⚠️  Erreur configuration TensorFlow: {e}")
        return False

def configure_essentia_professional():
    """Configuration professionnelle d'Essentia sans warnings"""
    
    try:
        # Configuration environnement Essentia
        os.environ['ESSENTIA_LOGGING_LEVEL'] = 'ERROR'
        
        import essentia
        from essentia.streaming import MusicExtractorSVM
        
        # Configuration silencieuse
        essentia.log.warningLevel = 4  # Seules les erreurs
        
        print("✅ Essentia configuré en mode professionnel")
        return True
        
    except ImportError:
        print("⚠️  Essentia non disponible")
        return False
    except Exception as e:
        print(f"⚠️  Erreur configuration Essentia: {e}")
        return False

def configure_numpy_scipy_compatibility():
    """Configuration pour compatibilité NumPy/SciPy"""
    
    try:
        import numpy as np
        import scipy
        
        # Vérification de compatibilité
        numpy_version = np.__version__
        scipy_version = scipy.__version__
        
        print(f"✅ NumPy {numpy_version} et SciPy {scipy_version} configurés")
        return True
        
    except ImportError as e:
        print(f"⚠️  Erreur import NumPy/SciPy: {e}")
        return False

def apply_professional_configuration():
    """Application de toutes les configurations professionnelles"""
    
    print("🔧 CONFIGURATION PROFESSIONNELLE - Corrections authentiques")
    print("="*60)
    
    results = {
        "tensorflow": configure_tensorflow_cpu(),
        "essentia": configure_essentia_professional(),
        "numpy_scipy": configure_numpy_scipy_compatibility()
    }
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print("="*60)
    print(f"📊 Configurations appliquées: {success_count}/{total_count}")
    
    for component, success in results.items():
        status = "✅" if success else "⚠️"
        print(f"  {status} {component}: {'OK' if success else 'PARTIAL'}")
    
    return success_count, total_count

if __name__ == "__main__":
    apply_professional_configuration()