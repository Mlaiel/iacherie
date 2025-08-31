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

"""Core Monetization Module Unit Tests
==================================

Real unit tests for the monetization module to address critical testing gap.
These tests validate actual business logic and provide quality assurance.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Implement centralized unit tests for production quality validation
"""
import pytest
import sys
import os
from pathlib import Path
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestLicensingManager:
    """Test suite for LicensingManager core functionality"""    
    def test_licensing_manager_import(self):
        """Test that LicensingManager can be imported successfully"""        try:
            from monetization import LicensingManager
            assert LicensingManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import LicensingManager: {e}")
    
    def test_licensing_config_structure(self):
        """Test that licensing configuration is properly structured"""        from monetization import LICENSING_CONFIG
        
        assert "licensing_tiers" in LICENSING_CONFIG
        assert "royalty_rates" in LICENSING_CONFIG
        assert "auto_licensing" in LICENSING_CONFIG
        
        # Validate licensing tiers
        tiers = LICENSING_CONFIG["licensing_tiers"]
        assert "basic" in tiers
        assert "standard" in tiers
        assert "premium" in tiers
        
        # Validate each tier has required fields
        for tier_name, tier_config in tiers.items():
            assert "price" in tier_config
            assert "duration_days" in tier_config
            assert "usage_limits" in tier_config
            assert isinstance(tier_config["price"], (int, float))
            assert isinstance(tier_config["duration_days"], int)
    
    def test_royalty_rates_configuration(self):
        """Test royalty rates are properly configured"""        from monetization import LICENSING_CONFIG
        
        royalty_rates = LICENSING_CONFIG["royalty_rates"]
        assert "streaming" in royalty_rates
        assert "download" in royalty_rates
        assert "sync" in royalty_rates
        assert "commercial" in royalty_rates
        
        # Validate rates are reasonable
        assert 0 < royalty_rates["streaming"] < 1
        assert 0 < royalty_rates["download"] < 1
        assert 0 < royalty_rates["sync"] < 1
        assert 0 < royalty_rates["commercial"] < 1

class TestLicensingManagerInstance:
    """Test LicensingManager instance creation and basic methods"""    
    def test_licensing_manager_creation(self):
        """Test LicensingManager can be instantiated"""        from monetization import LicensingManager
        
        manager = LicensingManager()
        assert manager is not None
    
    def test_global_licensing_manager(self):
        """Test global licensing manager instance"""        from monetization import get_licensing_manager
        
        manager1 = get_licensing_manager()
        manager2 = get_licensing_manager()
        
        # Should return same instance (singleton pattern)
        assert manager1 is manager2
    
    @patch('monetization.LicensingManager')
    def test_create_license_function(self, mock_manager_class):
        """Test license creation function"""        from monetization import create_license
        
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.create_license.return_value = {"license_id": 123, "status": "active"}
        
        # Mock the global manager
        with patch('monetization._licensing_manager', mock_manager):
            result = create_license(
                content_id=1,
                licensee_id=2,
                license_type="standard",
                terms={"duration": 90}
            )
        
        assert result is not None
        mock_manager.create_license.assert_called_once_with(1, 2, "standard", {"duration": 90})

class TestRoyaltyCalculation:
    """Test royalty calculation logic"""    
    def test_royalty_calculation_streaming(self):
        """Test streaming royalty calculation"""        from monetization import LICENSING_CONFIG
        
        streaming_rate = LICENSING_CONFIG["royalty_rates"]["streaming"]
        streams = 1000
        expected_royalty = streams * streaming_rate
        
        # Basic calculation validation
        assert expected_royalty > 0
        assert expected_royalty == 1000 * 0.004  # Based on config
    
    def test_royalty_calculation_download(self):
        """Test download royalty calculation"""        from monetization import LICENSING_CONFIG
        
        download_rate = LICENSING_CONFIG["royalty_rates"]["download"]
        downloads = 100
        expected_royalty = downloads * download_rate
        
        # Basic calculation validation
        assert expected_royalty > 0
        assert expected_royalty == 100 * 0.1  # Based on config

class TestUsageTracking:
    """Test usage tracking functionality"""    
    @patch('monetization.LicensingManager')
    def test_track_usage_function(self, mock_manager_class):
        """Test usage tracking function"""        from monetization import track_usage
        
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.track_usage.return_value = {"success": True}
        
        # Mock the global manager
        with patch('monetization._licensing_manager', mock_manager):
            result = track_usage(
                license_id=123,
                usage_type="streaming",
                usage_data={"streams": 50, "duration": 180}
            )
        
        assert result is not None
        mock_manager.track_usage.assert_called_once_with(
            123, "streaming", {"streams": 50, "duration": 180}
        )

if __name__ == "__main__":
    # Run tests directly
    pytest.main([str(Path(__file__)), "-v"])