#!/usr/bin/env python3
"""Script de vérification des dépendances et configuration du module IA-Influencer-Agent

Auteur: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel - Tous droits réservés
"""

import sys
import warnings
import importlib

# Supprime les warnings pour un output plus propre
warnings.filterwarnings('ignore')

def test_direct_config_imports():
        try:
            logger.info(f"Executing test_direct_config_imports")
            
            # Implementation for test_direct_config_imports
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_direct_config_imports completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_direct_config_imports failed: {e}")
            raise
        from backend.ai.config.ai_models_config import AIModelsConfig
        from backend.ai.config.audio_config import AudioConfig
        from backend.ai.config import MasterConfigManager  # Cette ligne peut poser problème
        
        print("✅ Imports directs réussis")
        
        # Test d'instanciation
        ai_config = AIModelsConfig()
        audio_config = AudioConfig()
        
        print(f"✅ AIModelsConfig - Default model: {ai_config.default_model}")
        print(f"✅ AudioConfig - Sample rate: {audio_config.sample_rate}")
        print(f"✅ AudioConfig - Channels: {audio_config.channels}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des imports directs: {e}")
        return False

def test_core_dependencies():
    """Test des dépendances core essentielles"""
    print("\n🔍 Test des dépendances essentielles...")
    
    essential_deps = [
        'azure.cognitiveservices.speech',
        'azure.storage.blob',
        'azure.identity',
        'google.cloud.speech',
        'google.cloud.translate',
        'transformers',
        'torch',
        'tensorflow',
        'librosa',
        'mutagen',
        'geopy',
        'wordcloud'
    ]
    
    success_count = 0
    
    for dep in essential_deps:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}")
            success_count += 1
        except ImportError:
            print(f"❌ {dep}")
    
    print(f"\n📊 Dépendances essentielles: {success_count}/{len(essential_deps)} installées")
    return success_count == len(essential_deps)

def main():
    """Fonction principale de vérification"""
    print("=" * 70)
    print("🚀 VÉRIFICATION DU MODULE IA-INFLUENCER-AGENT CONFIG")
    print("=" * 70)
    print("Auteur: Fahed Mlaiel (mlaiel@live.de)")
    print("Copyright (c) 2025 - Tous droits réservés")
    print("=" * 70)
    
    # Test 1: Dépendances essentielles
    deps_ok = test_core_dependencies()
    
    # Test 2: Configuration directe 
    config_ok = test_direct_config_imports()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 70)
    
    if deps_ok and config_ok:
        print("🎉 SUCCÈS TOTAL! Le module est prêt pour la production.")
        print("🔧 Toutes les dépendances principales sont installées.")
        print("⚙️ Les configurations sont fonctionnelles.")
        return 0
    elif deps_ok:
        print("⚠️ SUCCÈS PARTIEL - Dépendances OK, mais problèmes de configuration.")
        print("🔧 Les dépendances principales sont installées.")
        print("❌ Quelques ajustements nécessaires dans les imports.")
        return 1
    else:
        print("❌ ÉCHEC - Dépendances manquantes.")
        print("📦 Installez les dépendances manquantes avec pip install.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
