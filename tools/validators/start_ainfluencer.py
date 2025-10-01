#!/usr/bin/env python3
"""
Script de démarrage iaCherie avec chargement automatique des variables d'environnement
"""

# Suppress warnings FIRST
import warnings
import logging

# Configure warnings suppression
warnings.filterwarnings('ignore', message='.*Using Redis compatibility layer.*')
warnings.filterwarnings('ignore', message='.*duplicate base class TimeoutError.*')
warnings.filterwarnings('ignore', message='.*Using fallback implementations.*')
warnings.filterwarnings('ignore', category=UserWarning, module='redis')

# Set up custom log filter to suppress specific warnings
class WarningFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.WARNING:
            msg = record.getMessage()
            if any(pattern in msg for pattern in [
                'Using Redis compatibility layer',
                'duplicate base class TimeoutError',
                'Using fallback implementations'
            ]):
                return False
        return True

# Apply filter to root logger
logging.getLogger().addFilter(WarningFilter())

import os
import sys
from pathlib import Path

# Charger les variables d'environnement depuis .env
def load_env_file():
    """Charge les variables d'environnement depuis le fichier .env"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ Fichier .env introuvable!")
        return False
    
    print("🔧 Chargement des variables d'environnement...")
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
                if 'API_KEY' in key:
                    print(f"✅ {key}: {value[:20]}...")
    
    return True

if __name__ == "__main__":
    print("🚀 Démarrage d'iaCherie avec APIs externes...")
    
    # Charger les variables d'environnement
    if not load_env_file():
        sys.exit(1)
    
    # Vérifier les clés principales
    required_keys = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY', 'COHERE_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
        else:
            print(f"✅ {key} configurée")
    
    if missing_keys:
        print(f"⚠️ Clés manquantes: {missing_keys}")
        print("⚠️ Certaines fonctionnalités peuvent être limitées")
    
    # Lancer le serveur principal
    print("🎯 Lancement du serveur iaCherie...")
    
    try:
        import main
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        sys.exit(1)