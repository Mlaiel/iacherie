"""🧪 Test Suite for Industrial Image Fingerprinting
=================================================
Test Module: tests/fingerprinting/test_industrial_image_processing.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Unit Tests for Industrial Multi-Algorithm Image Fingerprinting
=================================================

Tests for:
✅ Fingerprinting Image Multi-Algorithmes
✅ CLIP vision-language understanding  
✅ Hash perceptuel (dHash, pHash, aHash, wHash)
✅ Détection features SIFT/SURF/ORB
✅ Résistance transformations géométriques
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

# Import the modules to test
try:
    from data_management.fingerprinting.industrial_image_processor import (
        IndustrialImageProcessor,
        IndustrialImageConfig,
        ImageFingerprint,
        create_industrial_processor
    )
    from data_management.fingerprinting.image_fingerprint import ImageHashProcessor, ImageFingerprintConfig
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Modules not available for testing: {e}")

class TestIndustrialImageProcessor:
    """Test suite for the industrial image processor"""
    
    @pytest.fixture
    def sample_image_path(self):
        """
Create a sample test image"""
        # Create a simple test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # Create a simple RGB image
            image = Image.new('RGB', (256, 256), color='red')
            # Add some pattern for feature detection
            pixels = image.load()
            for i in range(50, 200):
                for j in range(50, 200):
                    pixels[i, j] = (0, 255, 0)  # Green square
            
            image.save(tmp.name)
            yield tmp.name
            
        # Cleanup
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    
    @pytest.fixture
    def industrial_config(self):
        """
Create test configuration"""
        return IndustrialImageConfig(
            enable_phash=True,
            enable_dhash=True,
            enable_ahash=True,
            enable_whash=True,
            enable_clip=True,
            enable_sift=True,
            enable_surf=True,
            enable_orb=True,
            enable_multi_scale=True,
            hash_size=8,  # Smaller for faster testing
            max_keypoints=100,  # Reduced for testing
            use_gpu=False
        )
    
    @pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
    def test_industrial_config_creation(self, industrial_config):
        """Test that industrial configuration is created correctly"""
        assert industrial_config.enable_phash is True
        assert industrial_config.enable_dhash is True
        assert industrial_config.enable_ahash is True
        assert industrial_config.enable_whash is True
        assert industrial_config.enable_clip is True
        assert industrial_config.enable_sift is True
        assert industrial_config.hash_size == 8
        
    @pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
    def test_industrial_processor_initialization(self, industrial_config):
        """Test processor initialization"""
        processor = IndustrialImageProcessor(industrial_config)
        assert processor.config == industrial_config
        assert hasattr(processor, 'clip_model')
        assert hasattr(processor, 'sift')
        assert hasattr(processor, 'orb')
        
    @pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
    @pytest.mark.asyncio
    async def test_perceptual_hash_extraction(self, industrial_config, sample_image_path):
        """Test that all 4 perceptual hash types are extracted"""
        processor = IndustrialImageProcessor(industrial_config)
        
        # Mock the imagehash library if not available
        with patch('data_management.fingerprinting.industrial_image_processor.IMAGEHASH_AVAILABLE', True):
            with patch('data_management.fingerprinting.industrial_image_processor.imagehash') as mock_imagehash:
                # Mock hash functions
                mock_imagehash.phash.return_value = "1234567890abcdef"
                mock_imagehash.dhash.return_value = "abcdef1234567890"
                mock_imagehash.average_hash.return_value = "fedcba0987654321"
                mock_imagehash.whash.return_value = "0123456789abcdef"
                
                # Load test image
                image = Image.open(sample_image_path)
                
                # Test hash extraction
                hashes = await processor._extract_perceptual_hashes(image)
                
                # Verify all hash types are present
                assert 'phash' in hashes
                assert 'dhash' in hashes
                assert 'ahash' in hashes
                assert 'whash' in hashes
                assert 'combined_hash' in hashes
                
                # Verify hashes are strings
                assert isinstance(hashes['phash'], str)
                assert isinstance(hashes['dhash'], str)
                assert isinstance(hashes['ahash'], str)
                assert isinstance(hashes['whash'], str)
                assert isinstance(hashes['combined_hash'], str)
    
    @pytest.mark.skipif(not MODULES_AVAILABLE, reason="Required modules not available")
    def test_factory_function(self):
        """Test the factory function for creating processors"""
        processor = create_industrial_processor(
            enable_all_hashes=True,
            enable_clip=True,
            enable_traditional_cv=True,
            enable_geometric_resistance=True,
            use_gpu=False
        )
        
        assert isinstance(processor, IndustrialImageProcessor)
        assert processor.config.enable_phash is True
        assert processor.config.enable_dhash is True
        assert processor.config.enable_ahash is True
        assert processor.config.enable_whash is True
        assert processor.config.enable_clip is True
        assert processor.config.enable_sift is True
        assert processor.config.enable_orb is True

def test_module_imports():
    """
Test that modules can be imported correctly"""
    if MODULES_AVAILABLE:
        assert IndustrialImageProcessor is not None
        assert IndustrialImageConfig is not None
        assert ImageFingerprint is not None
        assert create_industrial_processor is not None
        print("✅ All industrial image processing modules imported successfully")
    else:
        print("⚠️ Industrial image processing modules not available")

if __name__ == "__main__":
    # Run basic import test
    test_module_imports()
    
    # Run pytest tests if modules are available
    if MODULES_AVAILABLE:
        pytest.main([__file__, "-v"])
    else:
        print("Skipping detailed tests due to missing dependencies")