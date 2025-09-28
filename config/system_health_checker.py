#!/usr/bin/env python3
"""
🔧 System Health Checker - Professional Diagnostics
===================================================

Diagnostic complet du système pour identifier et corriger tous les problèmes.
Approche enterprise pour un système parfaitement opérationnel.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import sys
import os
import warnings
import importlib
from pathlib import Path

class SystemHealthChecker:
    """Vérificateur de santé système professionnel"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.warnings_found = []
    
    def check_critical_imports(self):
        """Vérification des imports critiques"""
        critical_modules = [
            'torch', 'torchvision', 'torchaudio',
            'opencv', 'PIL', 'numpy', 'scipy',
            'langdetect', 'essentia', 'librosa',
            'moviepy', 'ffmpeg', 'ultralytics'
        ]
        
        print("🔍 Vérification des imports critiques...")
        
        for module in critical_modules:
            try:
                if module == 'opencv':
                    import cv2
                    print(f"✅ {module} (cv2): OK")
                elif module == 'PIL':
                    from PIL import Image
                    print(f"✅ {module}: OK")
                elif module == 'ffmpeg':
                    import ffmpeg
                    print(f"✅ {module}: OK")
                else:
                    importlib.import_module(module)
                    print(f"✅ {module}: OK")
            except ImportError as e:
                self.issues.append(f"Module manquant: {module} - {e}")
                print(f"❌ {module}: MANQUANT - {e}")
    
    def check_langdetect_issue(self):
        """Vérification spécifique du problème LangDetectError"""
        print("\n🔍 Vérification LangDetect...")
        
        try:
            from langdetect import detect
            print("✅ langdetect.detect: OK")
            
            try:
                from langdetect import LangDetectException as LangDetectError
                print("✅ LangDetectError: OK (via LangDetectException)")
                return True
            except ImportError:
                try:
                    from langdetect.lang_detect_exception import LangDetectException as LangDetectError
                    print("✅ LangDetectError: OK (via lang_detect_exception)")
                    return True
                except ImportError:
                    self.issues.append("LangDetectError non accessible")
                    print("❌ LangDetectError: INACCESSIBLE")
                    return False
                    
        except ImportError as e:
            self.issues.append(f"langdetect non installé: {e}")
            print(f"❌ langdetect: NON INSTALLÉ - {e}")
            return False
    
    def check_essentia_models(self):
        """Vérification des modèles Essentia"""
        print("\n🔍 Vérification Essentia...")
        
        try:
            from essentia.standard import MusicExtractor
            
            # Test création d'extracteur
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    extractor = MusicExtractor()
                print("✅ MusicExtractor: OK")
                return True
            except Exception as e:
                self.issues.append(f"MusicExtractor configuration: {e}")
                print(f"⚠️  MusicExtractor: WARNING - {e}")
                return False
                
        except ImportError as e:
            self.issues.append(f"Essentia non installé: {e}")
            print(f"❌ Essentia: NON INSTALLÉ - {e}")
            return False
    
    def check_tensorflow_cuda(self):
        """Vérification TensorFlow/CUDA"""
        print("\n🔍 Vérification TensorFlow/CUDA...")
        
        # Configuration préventive
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Import TensorFlow via gestionnaire centralisé
                from core.tensorflow_singleton import get_tensorflow
                tf = get_tensorflow()
                
            # Test CPU seulement
            print("✅ TensorFlow: Configuré CPU seulement")
            print("✅ CUDA: Désactivé (comme prévu)")
            return True
            
        except ImportError:
            print("ℹ️  TensorFlow: Non installé (optionnel)")
            return True
    
    def run_comprehensive_check(self):
        """Exécution du diagnostic complet"""
        print("🏥 DIAGNOSTIC SYSTÈME COMPLET")
        print("=" * 50)
        
        self.check_critical_imports()
        self.check_langdetect_issue()
        self.check_essentia_models()
        self.check_tensorflow_cuda()
        
        print("\n📊 RÉSUMÉ DU DIAGNOSTIC:")
        print("=" * 30)
        
        if not self.issues:
            print("🎉 SYSTÈME PARFAITEMENT SAIN!")
            print("✅ Aucun problème détecté")
            return True
        else:
            print(f"⚠️  {len(self.issues)} problème(s) détecté(s):")
            for issue in self.issues:
                print(f"  - {issue}")
            return False

def run_system_health_check():
    """Exécution du diagnostic de santé système"""
    checker = SystemHealthChecker()
    return checker.run_comprehensive_check()

if __name__ == "__main__":
    success = run_system_health_check()
    sys.exit(0 if success else 1)