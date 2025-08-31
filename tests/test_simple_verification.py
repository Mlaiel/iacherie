"""Test d'exemple simple pour vérifier que pytest fonctionne
======================================================

Ce test démontre que l'infrastructure de test est opérationnelle.
"""
import pytest
import sys
import os
from pathlib import Path

def test_basic_setup():
    """Test que l'environnement de base fonctionne"""    assert True, "Test de base réussi"

def test_python_version():
    """Test de la version Python"""    assert sys.version_info >= (3, 8), "Python 3.8+ requis"

def test_project_structure():
    """Test de la structure du projet"""    project_root = Path(__file__).parent.parent
    
    # Vérifier que les dossiers principaux existent
    assert (project_root / "ai").exists(), "Dossier ai/ manquant"
    assert (project_root / "tests").exists(), "Dossier tests/ manquant"

def test_pytest_markers():
    """Test des marqueurs pytest"""    # Ce test devrait passer avec les marqueurs configurés
    pass

@pytest.mark.unit
def test_with_unit_marker():
    """Test avec marqueur unit"""    assert True

@pytest.mark.fast
def test_fast_execution():
    """Test marqué comme rapide"""    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
