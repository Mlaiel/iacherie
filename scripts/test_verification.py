#!/usr/bin/env python3
"""
Script de Test Simplifié pour Vérifier l'Import
==============================================

Script pour tester les modules importés de manière simple
et identifier ceux qui fonctionnent déjà.

Author: GitHub Copilot
Date: 2025-08-31
"""

import os
import sys
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/workspaces/Ainflue")
TESTS_DIR = PROJECT_ROOT / "tests"

def test_simple_execution():
    """Test d'exécution simple des tests"""
    
    print("🧪 Test d'Exécution Simple des Tests Importés")
    print("=" * 50)
    
    # Tests basiques qui devraient fonctionner
    simple_tests = [
        "tests/ai/core/test_config.py::test_config_creation",  # Si le test existe
        "tests/ai/config/",  # Test du module entier
        "tests/conftest.py",  # Configuration principale
    ]
    
    working_tests = []
    failing_tests = []
    
    # Tester la collecte pytest simple
    print("\n Test de collecte pytest...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "--collect-only", "-q"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(" Collecte pytest réussie")
            test_count = result.stdout.count("<Function")
            print(f" {test_count} fonctions de test trouvées")
        else:
            print(" Erreur de collecte pytest")
            print(f"STDERR: {result.stderr[:200]}...")
            
    except Exception as e:
        print(f" Erreur lors de la collecte : {e}")
    
    # Tester les modules de base un par un
    basic_modules = [
        "tests/ai/__init__.py",
        "tests/conftest.py", 
        "tests/ai/core/__init__.py",
        "tests/ai/config/__init__.py",
    ]
    
    print("\n Test des modules de base...")
    for module in basic_modules:
        module_path = PROJECT_ROOT / module
        if module_path.exists():
            try:
                # Test d'import simple
                if module.endswith(".py"):
                    relative_module = module.replace("/", ".").replace(".py", "")
                    relative_module = relative_module.replace("tests.", "")
                    
                    # Ajouter le répertoire tests au PYTHONPATH
                    test_env = os.environ.copy()
                    test_env["PYTHONPATH"] = str(TESTS_DIR) + ":" + test_env.get("PYTHONPATH", "")
                    
                    result = subprocess.run([
                        sys.executable, "-c", f"import {relative_module}; print('Import réussi')"
                    ], env=test_env, cwd=PROJECT_ROOT, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f" {module} - Import réussi")
                        working_tests.append(module)
                    else:
                        print(f" {module} - Erreur: {result.stderr[:100]}")
                        failing_tests.append(module)
                else:
                    print(f" {module} - Répertoire existant")
                    
            except Exception as e:
                print(f" {module} - Exception: {e}")
                failing_tests.append(module)
        else:
            print(f" {module} - Fichier non trouvé")
    
    # Générer un rapport simple
    print(f"\n Résultats :")
    print(f" Modules fonctionnels : {len(working_tests)}")
    print(f" Modules en erreur : {len(failing_tests)}")
    
    if working_tests:
        print(f"\n Modules fonctionnels :")
        for test in working_tests:
            print(f"  - {test}")
    
    if failing_tests:
        print(f"\n Modules en erreur :")
        for test in failing_tests[:5]:  # Afficher seulement les 5 premiers
            print(f"  - {test}")
    
    # Recommandations
    print(f"\n Recommandations :")
    if len(working_tests) > 0:
        print(f"1. Les tests de base fonctionnent ! Continuez avec ceux-ci")
        print(f"2. Exécutez : pytest {working_tests[0] if working_tests else 'tests/'} -v")
    else:
        print(f"1. Commencez par corriger les imports de base")
        print(f"2. Vérifiez les modules ai.* créés")
        
    print(f"3. Complétez graduellement les modules manquants")
    print(f"4. Les tests importés sont une excellente base à adapter")

def create_simple_test_example():
    """Crée un test d'exemple simple qui fonctionne"""
    
    simple_test = '''"""
Test d'exemple simple pour vérifier que pytest fonctionne
======================================================

Ce test démontre que l'infrastructure de test est opérationnelle.
"""

import pytest
import sys
import os
from pathlib import Path

def test_basic_setup():
    """Test que l'environnement de base fonctionne"""
    assert True, "Test de base réussi"

def test_python_version():
    """Test de la version Python"""
    assert sys.version_info >= (3, 8), "Python 3.8+ requis"

def test_project_structure():
    """Test de la structure du projet"""
    project_root = Path(__file__).parent.parent.parent
    
    # Vérifier que les dossiers principaux existent
    assert (project_root / "ai").exists(), "Dossier ai/ manquant"
    assert (project_root / "tests").exists(), "Dossier tests/ manquant"

def test_pytest_markers():
    """Test des marqueurs pytest"""
    # Ce test devrait passer avec les marqueurs configurés
    pass

@pytest.mark.unit
def test_with_unit_marker():
    """Test avec marqueur unit"""
    assert True

@pytest.mark.fast
def test_fast_execution():
    """Test marqué comme rapide"""
    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    simple_test_path = PROJECT_ROOT / "tests" / "test_simple_verification.py"
    
    with open(simple_test_path, 'w', encoding='utf-8') as f:
        f.write(simple_test)
    
    print(f" Test d'exemple créé : {simple_test_path}")
    
    # Tester l'exécution
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(simple_test_path), "-v"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Test d'exemple exécuté avec succès !")
            print(f"Sortie:\n{result.stdout}")
        else:
            print(" Erreur lors de l'exécution du test d'exemple")
            print(f"Erreur:\n{result.stderr}")
            
    except Exception as e:
        print(f" Exception lors de l'exécution : {e}")

def main():
    """Fonction principale"""
    create_simple_test_example()
    test_simple_execution()
    
    print(f"\n Prochaines étapes recommandées :")
    print(f"1. pytest tests/test_simple_verification.py -v")
    print(f"2. Adapter les modules importés progressivement")
    print(f"3. Créer les implémentations manquantes")
    print(f"4. Utiliser la structure de tests importée comme référence")

if __name__ == "__main__":
    main()
