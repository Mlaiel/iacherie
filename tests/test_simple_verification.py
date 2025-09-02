"""Test d'exemple simple pour vérifier que pytest fonctionne
======================================================

Ce test démontre que l'infrastructure de test est opérationnelle.
"""

import pytest
import sys
import os
from pathlib import Path

def test_basic_setup():
    """
Test que l'environnement de base fonctionne"""
    assert True, "Test de base réussi"

def test_python_version():
    """Test de la version Python"""
    assert sys.version_info >= (3, 8), "Python 3.8+ requis"

def test_project_structure():
    """Test de la structure du projet"""
    project_root = Path(__file__).parent.parent
    
    # Vérifier que les dossiers principaux existent
    assert (project_root / "ai").exists(), "Dossier ai/ manquant"
    assert (project_root / "tests").exists(), "Dossier tests/ manquant"

def test_pytest_markers():
    """Test des marqueurs pytest"""
    # Test que les marqueurs pytest sont correctement configurés
    import pytest
    
    # Vérifier que pytest est disponible
    assert pytest is not None, "pytest module should be available"
    
    # Vérifier que le test fonctionne avec les marqueurs
    expected_markers = ['unit', 'integration', 'api', 'db', 'redis', 'external', 'security', 'performance', 'monetization']
    
    # Cette vérification s'assure que nous pouvons utiliser les marqueurs
    for marker in expected_markers:
        try:
            # Créer un marqueur fictif pour valider
            test_marker = pytest.mark.__getattr__(marker)
            assert test_marker is not None, f"Marker {marker} should be available"
        except AttributeError:
            pytest.fail(f"Marker {marker} is not properly configured")
    
    # Test réussi si on arrive ici
    assert True, "All pytest markers are properly configured"

@pytest.mark.unit
def test_with_unit_marker():
    """
Test avec marqueur unit"""
    assert True

@pytest.mark.fast
def test_fast_execution():
    """
Test marqué comme rapide"""
    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
