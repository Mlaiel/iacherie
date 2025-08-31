#!/usr/bin/env python3
"""Script d'Import et Adaptation des Tests de l'Ancien Projet
=========================================================

Script pour importer, adapter et intégrer les fichiers de tests
de l'ancien projet IA-Influencer vers le nouveau projet Ainflue.

Author: GitHub Copilot
Date: 2025-08-31
"""
import os
import sys
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import requests
import zipfile
import tempfile

# Configuration
OLD_REPO_URL = "https://github.com/Mlaiel/IA-influencer/archive/refs/heads/main.zip"
PROJECT_ROOT = Path("/workspaces/Ainflue")
TESTS_DIR = PROJECT_ROOT / "tests"

# Mapping des modules de l'ancien vers le nouveau projet
MODULE_MAPPING = {
    "backend.ai": "ai",
    "backend.data": "data",
    "backend.business": "business",
    "backend.api": "api",
    "backend.core": "core",
    "backend.crawlers": "crawlers",
    "backend.services": "services",
    "backend.utils": "utils"
}

class TestImporter:
    """Importeur et adaptateur de tests"""
    
    def __init__(self):
        self.temp_dir = None
        self.old_tests_path = None
        self.imported_files = []
        self.adaptation_log = []
    
    def download_and_extract_repo(self) -> bool:
        """Télécharge et extrait l'ancien projet"""
        try:
            print("📥 Téléchargement de l'ancien projet...")
            
            # Créer un répertoire temporaire
            self.temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(self.temp_dir, "repo.zip")
            
            # Télécharger le zip
            response = requests.get(OLD_REPO_URL)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extraire
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Trouver le dossier des tests
            extracted_dirs = [d for d in os.listdir(self.temp_dir) if os.path.isdir(os.path.join(self.temp_dir, d))]
            if extracted_dirs:
                repo_dir = os.path.join(self.temp_dir, extracted_dirs[0])
                self.old_tests_path = Path(repo_dir) / "IA-Influencer-Agent" / "tests_backend"
                
                if self.old_tests_path.exists():
                    print(f"✅ Tests trouvés dans : {self.old_tests_path}")
                    return True
                else:
                    print(f"❌ Dossier tests non trouvé dans : {repo_dir}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement : {e}")
            return False
    
    def analyze_test_structure(self) -> Dict[str, List[str]]:
        """Analyse la structure des tests de l'ancien projet"""
        if not self.old_tests_path or not self.old_tests_path.exists():
            return {}
        
        structure = {}
        
        for root, dirs, files in os.walk(self.old_tests_path):
            rel_path = os.path.relpath(root, self.old_tests_path)
            if rel_path == ".":
                rel_path = ""
            
            test_files = [f for f in files if f.startswith("test_") and f.endswith(".py")]
            config_files = [f for f in files if f in ["conftest.py", "pytest.ini", "__init__.py"]]
            doc_files = [f for f in files if f.endswith((".md", ".rst"))]
            
            if test_files or config_files:
                structure[rel_path] = {
                    "test_files": test_files,
                    "config_files": config_files,
                    "doc_files": doc_files
                }
        
        return structure
    
    def adapt_imports(self, content: str, target_module: str) -> str:
        """Adapte les imports pour le nouveau projet"""
        lines = content.split('\n')
        adapted_lines = []
        
        for line in lines:
            original_line = line
            
            # Adapter les imports backend.*
            for old_module, new_module in MODULE_MAPPING.items():
                if f"from {old_module}" in line or f"import {old_module}" in line:
                    line = line.replace(old_module, new_module)
                    self.adaptation_log.append(f"Import adapté: {original_line} -> {line}")
            
            # Adapter les chemins de fichiers absolus
            if "/workspaces/Achiri/IA-Influencer-Agent" in line:
                line = line.replace("/workspaces/Achiri/IA-Influencer-Agent", "/workspaces/Ainflue")
                self.adaptation_log.append(f"Chemin adapté: {original_line} -> {line}")
            
            adapted_lines.append(line)
        
        return '\n'.join(adapted_lines)
    
    def copy_and_adapt_file(self, source_file: Path, target_file: Path) -> bool:
        """Copie et adapte un fichier de test"""
        try:
            # Créer le répertoire cible si nécessaire
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Lire le contenu source
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adapter le contenu
            target_module = str(target_file.relative_to(TESTS_DIR)).replace(os.sep, '.')
            adapted_content = self.adapt_imports(content, target_module)
            
            # Écrire le fichier adapté
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(adapted_content)
            
            self.imported_files.append(str(target_file))
            print(f"✅ Fichier adapté : {source_file.name} -> {target_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'adaptation de {source_file} : {e}")
            return False
    
    def import_test_module(self, module_path: str, test_info: Dict) -> bool:
        """Import un module de test complet"""
        source_module_path = self.old_tests_path / module_path
        target_module_path = TESTS_DIR / module_path
        
        if not source_module_path.exists():
            print(f"⚠️  Module source non trouvé : {source_module_path}")
            return False
        
        success_count = 0
        total_files = len(test_info["test_files"]) + len(test_info["config_files"])
        
        # Copier les fichiers de test
        for test_file in test_info["test_files"]:
            source_file = source_module_path / test_file
            target_file = target_module_path / test_file
            
            if self.copy_and_adapt_file(source_file, target_file):
                success_count += 1
        
        # Copier les fichiers de configuration
        for config_file in test_info["config_files"]:
            source_file = source_module_path / config_file
            target_file = target_module_path / config_file
            
            if self.copy_and_adapt_file(source_file, target_file):
                success_count += 1
        
        print(f"📊 Module {module_path} : {success_count}/{total_files} fichiers importés")
        return success_count > 0
    
    def create_master_conftest(self) -> bool:
        """Crée un fichier conftest.py principal"""
        conftest_content = '''"""Configuration pytest principale pour le projet Ainflue
====================================================

Configuration centralisée pour tous les tests du projet,
importée et adaptée de l'ancien projet IA-Influencer.

Author: GitHub Copilot (adapté du projet original)
Date: 2025-08-31
"""
import pytest
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration pytest
def pytest_configure(config):
    """Configuration pytest principale"""
    # Marqueurs de test
    config.addinivalue_line("markers", "unit: Tests unitaires")
    config.addinivalue_line("markers", "integration: Tests d'intégration") 
    config.addinivalue_line("markers", "performance: Tests de performance")
    config.addinivalue_line("markers", "security: Tests de sécurité")
    config.addinivalue_line("markers", "slow: Tests lents")
    config.addinivalue_line("markers", "fast: Tests rapides")
    config.addinivalue_line("markers", "ai: Tests IA")
    config.addinivalue_line("markers", "business: Tests logique métier")
    config.addinivalue_line("markers", "api: Tests API")
    config.addinivalue_line("markers", "database: Tests base de données")

@pytest.fixture(scope="session")
def event_loop():
    """Event loop pour les tests asyncio"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config():
    """Configuration de test globale"""
    return {
        "test_env": "pytest",
        "project_root": str(PROJECT_ROOT),
        "test_data_dir": str(PROJECT_ROOT / "tests" / "data"),
        "temp_dir": "/tmp/ainflue_tests"
    }

@pytest.fixture
def temp_dir(tmp_path):
    """Répertoire temporaire pour les tests"""
    return tmp_path

# Hook pour modifier la collection de tests
def pytest_collection_modifyitems(config, items):
    """Modifie la collection de tests"""
    for item in items:
        # Ajouter des marqueurs automatiquement basés sur le nom
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)

logger.info("🧪 Configuration pytest Ainflue chargée")
'''
        
        conftest_path = TESTS_DIR / "conftest.py"
        try:
            conftest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(conftest_path, 'w', encoding='utf-8') as f:
                f.write(conftest_content)
            print("✅ conftest.py principal créé")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la création de conftest.py : {e}")
            return False
    
    def create_pytest_ini(self) -> bool:
        """Crée le fichier pytest.ini"""
        pytest_ini_content = '''[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=ai
    --cov=business
    --cov=api
    --cov=core
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    -v
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Tests unitaires
    integration: Tests d'intégration
    performance: Tests de performance
    security: Tests de sécurité
    slow: Tests lents (>1s)
    fast: Tests rapides (<1s)
    ai: Tests des modules IA
    business: Tests logique métier
    api: Tests API
    database: Tests base de données
    asyncio: Tests asynchrones
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
asyncio_mode = auto
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
'''
        
        pytest_ini_path = PROJECT_ROOT / "pytest.ini"
        try:
            with open(pytest_ini_path, 'w', encoding='utf-8') as f:
                f.write(pytest_ini_content)
            print("✅ pytest.ini créé")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la création de pytest.ini : {e}")
            return False
    
    def generate_import_report(self) -> str:
        """Génère un rapport d'importation"""
        report = f"""# 📊 Rapport d'Importation des Tests

**Date :** {sys.version}
**Projet source :** IA-Influencer
**Projet cible :** Ainflue

## 📈 Statistiques

- **Fichiers importés :** {len(self.imported_files)}
- **Adaptations effectuées :** {len(self.adaptation_log)}

## 📁 Fichiers Importés

{chr(10).join(f"- {f}" for f in self.imported_files)}

## 🔧 Adaptations Effectuées

{chr(10).join(f"- {adapt}" for adapt in self.adaptation_log[:20])}

{'...' if len(self.adaptation_log) > 20 else ''}

## 🚀 Prochaines Étapes

1. Exécuter les tests : `pytest tests/ -v`
2. Vérifier les imports manquants
3. Adapter les modules spécifiques au nouveau projet
4. Compléter les fixtures selon les besoins

## 💡 Commandes Utiles

```bash
# Exécuter tous les tests
pytest tests/

# Exécuter seulement les tests rapides
pytest tests/ -m "fast"

# Exécuter avec couverture
pytest tests/ --cov

# Exécuter les tests IA
pytest tests/ai/ -v
```
"""
        return report
    
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("🧹 Fichiers temporaires nettoyés")
    
    def run_import(self) -> bool:
        """Exécute l'importation complète"""
        try:
            print("🚀 Démarrage de l'importation des tests...")
            
            # Télécharger l'ancien projet
            if not self.download_and_extract_repo():
                return False
            
            # Analyser la structure
            print("🔍 Analyse de la structure des tests...")
            test_structure = self.analyze_test_structure()
            
            if not test_structure:
                print("❌ Aucun test trouvé dans l'ancien projet")
                return False
            
            print(f"📊 {len(test_structure)} modules de tests trouvés")
            
            # Créer les fichiers de configuration
            self.create_master_conftest()
            self.create_pytest_ini()
            
            # Modules prioritaires à importer
            priority_modules = [
                "ai/core",
                "ai/quality_assessment", 
                "ai/config",
                "ai/ai_agents",
                "ai/monitoring",
                "ai/models"
            ]
            
            # Importer les modules prioritaires
            for module in priority_modules:
                if module in test_structure:
                    print(f"📦 Importation du module prioritaire : {module}")
                    self.import_test_module(module, test_structure[module])
            
            # Importer les autres modules
            for module_path, test_info in test_structure.items():
                if module_path not in priority_modules and module_path:
                    print(f"📦 Importation du module : {module_path}")
                    self.import_test_module(module_path, test_info)
            
            # Générer le rapport
            report = self.generate_import_report()
            report_path = PROJECT_ROOT / "TEST_IMPORT_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ Importation terminée ! Rapport généré : {report_path}")
            print(f"📊 {len(self.imported_files)} fichiers importés")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'importation : {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Fonction principale"""
    print("🔄 Script d'Importation des Tests - Ainflue")
    print("=" * 50)
    
    importer = TestImporter()
    
    if importer.run_import():
        print("\n🎉 Importation réussie !")
        print("💡 Vous pouvez maintenant exécuter : pytest tests/ -v")
        return 0
    else:
        print("\n❌ Échec de l'importation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
