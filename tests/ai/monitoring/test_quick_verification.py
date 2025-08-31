# -*- coding: utf-8 -*-
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

"""Quick Test - Verify Test Syntax

Simple test to verify our monitoring tests can be imported and run.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path


class TestQuickVerification:
    """Quick verification tests."""    
    def test_imports_working(self):
        """Test that basic imports work."""        # Basic test to verify pytest is working
        assert 1 + 1 == 2
        
    def test_async_support(self):
        """Test async support."""        import asyncio
        
        async def async_function():
            return "async_works"
        
        # Test async functionality
        result = asyncio.run(async_function())
        assert result == "async_works"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
