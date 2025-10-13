#!/usr/bin/env python3
"""
🔧 LangDetect Error Correction - Professional Fix
================================================

Correction professionnelle du problème d'import LangDetectError.
Installation et configuration appropriée pour éviter les warnings.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import sys
import logging

def fix_langdetect_imports():
    """Correction professionnelle des imports langdetect"""
    
    try:
        # Test d'import standard
        from langdetect import detect, detect_langs
        
        # Correction pour LangDetectError
        try:
            from langdetect import LangDetectException as LangDetectError
        except ImportError:
            try:
                from langdetect.lang_detect_exception import LangDetectException as LangDetectError
            except ImportError:
                # Création de la classe manquante
                class LangDetectError(Exception):
                    """Exception pour la détection de langue"""
                    pass
        
        # Injection dans le module langdetect pour compatibilité
        import langdetect
        if not hasattr(langdetect, 'LangDetectError'):
            langdetect.LangDetectError = LangDetectError
            
        return True, "LangDetect correctement configuré"
        
    except ImportError as e:
        logging.warning(f"LangDetect non disponible: {e}")
        return False, str(e)

def install_missing_langdetect():
    """Installation automatique si nécessaire"""
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "langdetect==1.0.9", "--upgrade"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return fix_langdetect_imports()
        else:
            return False, f"Installation échouée: {result.stderr}"
            
    except Exception as e:
        return False, f"Erreur installation: {e}"

# Auto-correction au chargement
success, message = fix_langdetect_imports()
if not success:
    success, message = install_missing_langdetect()

__all__ = ['fix_langdetect_imports', 'install_missing_langdetect']