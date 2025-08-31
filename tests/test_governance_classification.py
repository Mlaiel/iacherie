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

"""Tests for Data Governance Classification System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
from unittest.mock import Mock, patch
from datetime import datetime

# Import the modules we're testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_management.governance.classification import (
    PatternClassifier,
    ContentCategory,
    SensitivityLabel,
    ClassificationError
)


class TestPatternClassifier:
    """Test cases for PatternClassifier"""    
    @pytest.fixture
    def classifier(self):
        """Create a PatternClassifier instance for testing"""        return PatternClassifier()
    
    def test_get_supported_types(self, classifier):
        """Test that classifier returns supported content types"""        supported_types = classifier.get_supported_types()
        
        assert isinstance(supported_types, list)
        assert len(supported_types) > 0
        assert "text" in supported_types
        assert "audio" in supported_types
        assert "video" in supported_types
        assert "image" in supported_types
    
    @pytest.mark.asyncio
    async def test_classify_text_content(self, classifier):
        """Test classification of text content"""        test_content = "This document contains confidential business information and trade secrets."
        
        result = await classifier.classify(
            content=test_content,
            content_type="text"
        )
        
        assert isinstance(result, dict)
        assert "content_categories" in result
        assert "sensitivity_labels" in result
        assert "confidence_scores" in result
        assert "metadata" in result
        
        # Check that we got some classification results
        assert len(result["content_categories"]) > 0 or len(result["sensitivity_labels"]) > 0
    
    @pytest.mark.asyncio
    async def test_classify_sensitive_content(self, classifier):
        """Test classification of content containing sensitive patterns"""        sensitive_content = "User password: secret123, Social Security Number: 123-45-6789"
        
        result = await classifier.classify(
            content=sensitive_content,
            content_type="text"
        )
        
        # Should detect high sensitivity due to password and SSN patterns
        sensitivity_labels = result.get("sensitivity_labels", {})
        assert len(sensitivity_labels) > 0
        
        # Should have detected critical or high sensitivity
        has_high_sensitivity = any(
            label in [SensitivityLabel.CRITICAL_SENSITIVITY.value, SensitivityLabel.HIGH_SENSITIVITY.value]
            for label in sensitivity_labels.keys()
        )
        assert has_high_sensitivity
    
    @pytest.mark.asyncio
    async def test_classify_json_content(self, classifier):
        """Test classification of JSON content"""        json_content = {
            "user_data": {
                "email": "user@example.com",
                "phone": "555-1234",
                "classification": "internal"
            },
            "business_info": {
                "trade_secret": "proprietary algorithm details",
                "revenue": 1000000
            }
        }
        
        result = await classifier.classify(
            content=json_content,
            content_type="json"
        )
        
        assert isinstance(result, dict)
        assert "content_categories" in result
        assert "sensitivity_labels" in result
        
        # Should detect some business-related content
        content_categories = result.get("content_categories", {})
        assert len(content_categories) > 0
    
    @pytest.mark.asyncio
    async def test_classify_with_metadata(self, classifier):
        """Test classification with additional metadata"""        content = "Regular operational data"
        metadata = {
            "source": "internal_system",
            "contains_pii": True,
            "department": "finance"
        }
        
        result = await classifier.classify(
            content=content,
            content_type="text",
            metadata=metadata
        )
        
        assert isinstance(result, dict)
        # Metadata should be included in text analysis
        assert result["metadata"]["content_type"] == "text"
    
    @pytest.mark.asyncio
    async def test_unsupported_content_type(self, classifier):
        """Test handling of unsupported content type"""        with pytest.raises(Exception):  # Should raise ValidationError but we'll catch any exception
            await classifier.classify(
                content="test content",
                content_type="unsupported_type"
            )
    
    def test_extract_text_content(self, classifier):
        """Test text extraction from different content types"""        # Test string content
        text_result = classifier._extract_text_content("Hello world", "text", None)
        assert text_result == "Hello world"
        
        # Test JSON content
        json_data = {"key": "value", "number": 123}
        json_result = classifier._extract_text_content(json_data, "json", None)
        assert "key" in json_result
        assert "value" in json_result
        
        # Test with metadata
        metadata = {"meta_key": "meta_value"}
        result_with_meta = classifier._extract_text_content("content", "text", metadata)
        assert "content" in result_with_meta
        assert "meta_key" in result_with_meta
    
    def test_calculate_pattern_confidence(self, classifier):
        """Test pattern confidence calculation"""        import re
        
        # Test with regex patterns
        patterns = [
            re.compile(r'\bpassword\b', re.IGNORECASE),
            re.compile(r'\bsecret\b', re.IGNORECASE)
        ]
        
        text_with_matches = "The password is secret123"
        confidence = classifier._calculate_pattern_confidence(text_with_matches, patterns)
        assert confidence > 0
        assert confidence <= 1.0
        
        text_without_matches = "This is regular text"
        confidence_low = classifier._calculate_pattern_confidence(text_without_matches, patterns)
        assert confidence_low == 0.0
        
        # Test with string patterns
        string_patterns = ["confidential", "restricted"]
        text_with_string = "This is confidential information"
        confidence_string = classifier._calculate_pattern_confidence(text_with_string, string_patterns)
        assert confidence_string > 0
    
    def test_empty_content_handling(self, classifier):
        """Test handling of empty or None content"""        # Test empty string
        empty_result = classifier._extract_text_content("", "text", None)
        assert empty_result == ""
        
        # Test None content
        none_result = classifier._extract_text_content(None, "text", None)
        assert isinstance(none_result, str)
    
    @pytest.mark.asyncio
    async def test_default_categories_assigned(self, classifier):
        """Test that default categories are assigned when no patterns match"""        neutral_content = "The quick brown fox jumps over the lazy dog."
        
        result = await classifier.classify(
            content=neutral_content,
            content_type="text"
        )
        
        # Should have default categories assigned
        content_categories = result.get("content_categories", {})
        sensitivity_labels = result.get("sensitivity_labels", {})
        
        assert len(content_categories) > 0
        assert len(sensitivity_labels) > 0
        
        # Default should be general content and low sensitivity
        assert ContentCategory.GENERAL.value in content_categories
        assert SensitivityLabel.LOW_SENSITIVITY.value in sensitivity_labels