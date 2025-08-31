# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Simple Pytest Validation Test
=============================

Basic pytest test to validate that pytest framework works 
independently of conftest configuration issues.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2
    assert "test" in "testing"
    assert len([1, 2, 3]) == 3

def test_async_functionality():
    """Test async functionality works"""
    async def async_test():
        return "async works"
    
    result = asyncio.run(async_test())
    assert result == "async works"

def test_imports_work():
    """Test that basic imports work without conftest"""
    try:
        import numpy as np
        # Test numpy works
        arr = np.array([1, 2, 3])
        assert len(arr) == 3
    except ImportError:
        # If numpy not available, create mock test
        mock_array = [1, 2, 3]
        assert len(mock_array) == 3
    
    import json
    import os
    
    # Test json works
    data = {"test": "value"}
    assert json.dumps(data) == '{"test": "value"}'

def test_test_file_structure():
    """Test that test files exist"""
    test_files = [
        "test_ai_agents_core.py",
        "test_fingerprinting_agent.py",
        "test_monetization_agent.py"
    ]
    
    current_dir = Path(__file__).parent
    
    for test_file in test_files:
        file_path = current_dir / test_file
        assert file_path.exists(), f"Test file {test_file} should exist"

if __name__ == "__main__":
    # Run tests directly if called as script
    print("Running basic pytest validation...")
    pytest.main([str(Path(__file__)), "-v"])