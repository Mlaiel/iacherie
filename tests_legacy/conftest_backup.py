"""Configuration pytest principale pour le projet Ainflue
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
    """
Configuration pytest principale"""
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
    """
Modifie la collection de tests"""
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
