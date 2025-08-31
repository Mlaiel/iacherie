#!/usr/bin/env python3
"""Script de Correction et Adaptation des Tests Importés
===================================================

Script pour corriger les imports et adapter les tests importés
pour qu'ils fonctionnent avec la structure actuelle du projet.

Author: GitHub Copilot
Date: 2025-08-31
"""
import os
import re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path("/workspaces/Ainflue")
TESTS_DIR = PROJECT_ROOT / "tests"

class TestFixer:
    """Correcteur de tests importés"""
    
    def __init__(self):
        self.fixed_files = []
        self.errors = []
    
    def find_missing_imports(self, file_path: Path) -> List[str]:
        """Trouve les imports manquants dans un fichier"""
        missing = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher les imports backend.*
        import_patterns = [
            r'from\s+(ai\.[a-zA-Z_][a-zA-Z0-9_.]*)',
            r'from\s+(business\.[a-zA-Z_][a-zA-Z0-9_.]*)',
            r'from\s+(core\.[a-zA-Z_][a-zA-Z0-9_.]*)',
            r'import\s+(ai\.[a-zA-Z_][a-zA-Z0-9_.]*)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if not self.check_module_exists(match):
                    missing.append(match)
        
        return missing
    
    def check_module_exists(self, module_name: str) -> bool:
        """Vérifie si un module existe dans le projet"""
        module_path = module_name.replace('.', '/')
        
        # Vérifier dans le répertoire racine
        full_path = PROJECT_ROOT / module_path
        if full_path.exists():
            return True
        
        # Vérifier avec __init__.py
        init_path = PROJECT_ROOT / module_path / "__init__.py"
        if init_path.exists():
            return True
        
        # Vérifier comme fichier .py
        py_path = PROJECT_ROOT / f"{module_path}.py"
        if py_path.exists():
            return True
        
        return False
    
    def create_minimal_module(self, module_name: str):
        """Crée un module minimal pour satisfaire les imports"""
        module_path = module_name.replace('.', '/')
        full_path = PROJECT_ROOT / module_path
        
        # Créer le répertoire
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Créer __init__.py minimal
        init_path = full_path / "__init__.py"
        if not init_path.exists():
            minimal_content = f'''"""Module {module_name} - Version Minimale
====================================

Module généré automatiquement pour satisfaire les imports des tests.
Ce module doit être complété avec la véritable implémentation.

Author: GitHub Copilot (auto-généré)
Date: 2025-08-31
"""# Classes et fonctions de base pour les tests
class BaseClass:
    """Classe de base minimale"""
    pass

class TestConfig:
    """Configuration de test minimale"""
    def __init__(self):
        self.test_mode = True

# Fonctions utilitaires de base
def get_default_config():
    """Retourne une configuration par défaut"""
    return TestConfig()

def initialize():
    """Initialise le module"""
    pass

# Exports minimaux
__all__ = [
    'BaseClass',
    'TestConfig', 
    'get_default_config',
    'initialize'
]
'''
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(minimal_content)
            
            print(f"✅ Module minimal créé : {module_name}")
    
    def fix_test_file(self, file_path: Path) -> bool:
        """Corrige un fichier de test"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Corrections communes
            fixes = [
                # Remplacer les imports backend.* par des imports relatifs
                (r'from\s+backend\.', 'from '),
                (r'import\s+backend\.', 'import '),
                
                # Corriger les chemins absolus spécifiques
                (r'/workspaces/Achiri/IA-Influencer-Agent', '/workspaces/Ainflue'),
                
                # Ajouter des imports manquants courants
                (r'import pytest\n', 'import pytest\nimport sys\nimport os\nfrom pathlib import Path\n'),
                
                # Corriger les assertions pytest obsolètes
                (r'pytest\.main\(\[__file__', 'pytest.main([str(Path(__file__))'),
            ]
            
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)
            
            # Ajouter un en-tête de compatibilité si nécessaire
            if '# -*- coding: utf-8 -*-' not in content:
                compatibility_header = '''# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

'''
                content = compatibility_header + content
            
            # Écrire le fichier corrigé si des changements ont été faits
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(str(file_path))
                return True
            
            return False
            
        except Exception as e:
            self.errors.append(f"Erreur lors de la correction de {file_path}: {e}")
            return False
    
    def create_test_requirements(self):
        """Crée un fichier requirements-test.txt"""
        requirements_content = '''# Dépendances pour les tests - Projet Ainflue
# Généré automatiquement lors de l'import des tests

# Framework de test principal
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=6.0.0
pytest-mock>=3.12.0
pytest-benchmark>=4.0.0

# Dépendances pour les tests IA
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0

# Utilitaires de test
requests>=2.31.0
aiohttp>=3.9.0
Pillow>=10.0.0

# Outils de développement
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0

# Logging et monitoring
structlog>=23.1.0

# Base de données de test
sqlite3

# Utilitaires
python-dotenv>=1.0.0
pyyaml>=6.0.0
'''
        
        requirements_path = PROJECT_ROOT / "requirements-test.txt"
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"✅ Fichier requirements-test.txt créé")
    
    def run_fixes(self):
        """Exécute toutes les corrections"""
        print("🔧 Démarrage des corrections des tests importés...")
        
        # Créer les modules manquants de base
        basic_modules = [
            "ai.nlp",
            "ai.core", 
            "ai.models",
            "ai.engines",
            "ai.config",
            "business.core",
            "business.analytics",
            "core.utils",
            "core.config"
        ]
        
        for module in basic_modules:
            if not self.check_module_exists(module):
                self.create_minimal_module(module)
        
        # Parcourir tous les fichiers de test
        for root, dirs, files in os.walk(TESTS_DIR):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    file_path = Path(root) / file
                    if self.fix_test_file(file_path):
                        print(f"🔧 Fichier corrigé : {file_path}")
        
        # Créer le fichier requirements-test.txt
        self.create_test_requirements()
        
        # Rapport final
        print(f"\n📊 Corrections terminées :")
        print(f"✅ Fichiers corrigés : {len(self.fixed_files)}")
        print(f"❌ Erreurs : {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Erreurs rencontrées :")
            for error in self.errors[:5]:  # Afficher seulement les 5 premières
                print(f"  - {error}")
        
        print(f"\n💡 Prochaines étapes :")
        print(f"1. Installer les dépendances : pip install -r requirements-test.txt")
        print(f"2. Tester l'exécution : pytest tests/ai/core/ -v --tb=short")
        print(f"3. Compléter les modules minimaux créés")

def main():
    """Fonction principale"""
    print("🔧 Script de Correction des Tests Importés - Ainflue")
    print("=" * 55)
    
    fixer = TestFixer()
    fixer.run_fixes()
    
    return 0

if __name__ == "__main__":
    exit(main())
