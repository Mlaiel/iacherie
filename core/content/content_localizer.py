#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Localizer Module
Provides comprehensive content localization services
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalizationLevel(Enum):
    """Content localization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ContentType(Enum):
    """Content types for localization"""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"

@dataclass
class LocalizationRequest:
    """Localization request data structure"""
    content: str
    source_locale: str
    target_locale: str
    content_type: ContentType = ContentType.TEXT
    level: LocalizationLevel = LocalizationLevel.STANDARD
    preserve_formatting: bool = True
    context: Optional[str] = None

@dataclass
class LocalizationResult:
    """Localization result data structure"""
    localized_content: str
    source_locale: str
    target_locale: str
    content_type: str
    confidence: float
    changes_made: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

class ContentLocalizer:
    """
    Enterprise-grade content localization service
    Handles text, formatting, and cultural adaptation
    """
    
    def __init__(self):
        """Initialize content localizer"""
        self.locale_mappings = {}
        self.format_patterns = {}
        self.cultural_adaptations = {}
        self.currency_mappings = {}
        self.date_patterns = {}
        
        # Initialize default configurations
        self._setup_locale_mappings()
        self._setup_format_patterns()
        self._setup_cultural_adaptations()
        self._setup_currency_mappings()
        self._setup_date_patterns()
        
        logger.info("🌍 Content Localizer initialized successfully")
    
    def _setup_locale_mappings(self):
        """Setup locale mappings"""
        self.locale_mappings = {
            'en': {
                'name': 'English',
                'direction': 'ltr',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'currency_symbol': '$',
                'date_format': 'MM/DD/YYYY',
                'time_format': 'HH:MM AM/PM'
            },
            'fr': {
                'name': 'Français',
                'direction': 'ltr',
                'decimal_separator': ',',
                'thousands_separator': ' ',
                'currency_symbol': '€',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:MM'
            },
            'es': {
                'name': 'Español',
                'direction': 'ltr',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'currency_symbol': '€',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:MM'
            },
            'de': {
                'name': 'Deutsch',
                'direction': 'ltr',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'currency_symbol': '€',
                'date_format': 'DD.MM.YYYY',
                'time_format': 'HH:MM'
            },
            'it': {
                'name': 'Italiano',
                'direction': 'ltr',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'currency_symbol': '€',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:MM'
            },
            'ar': {
                'name': 'العربية',
                'direction': 'rtl',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'currency_symbol': 'ريال',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:MM'
            },
            'zh': {
                'name': '中文',
                'direction': 'ltr',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'currency_symbol': '¥',
                'date_format': 'YYYY/MM/DD',
                'time_format': 'HH:MM'
            },
            'ja': {
                'name': '日本語',
                'direction': 'ltr',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'currency_symbol': '¥',
                'date_format': 'YYYY/MM/DD',
                'time_format': 'HH:MM'
            }
        }
    
    def _setup_format_patterns(self):
        """Setup formatting patterns"""
        self.format_patterns = {
            'number': {
                'decimal': r'(\d+)\.(\d+)',
                'thousands': r'(\d{1,3}(?:,\d{3})*)',
                'currency': r'\$(\d+(?:\.\d{2})?)',
                'percentage': r'(\d+(?:\.\d+)?)%'
            },
            'date': {
                'us_format': r'(\d{1,2})/(\d{1,2})/(\d{4})',
                'eu_format': r'(\d{1,2})/(\d{1,2})/(\d{4})',
                'iso_format': r'(\d{4})-(\d{2})-(\d{2})'
            },
            'time': {
                '12_hour': r'(\d{1,2}):(\d{2})\s*(AM|PM)',
                '24_hour': r'(\d{1,2}):(\d{2})'
            }
        }
    
    def _setup_cultural_adaptations(self):
        """Setup cultural adaptations"""
        self.cultural_adaptations = {
            'colors': {
                'en': {'positive': 'green', 'negative': 'red', 'neutral': 'blue'},
                'zh': {'positive': 'red', 'negative': 'white', 'neutral': 'yellow'},
                'ar': {'positive': 'green', 'negative': 'black', 'neutral': 'blue'}
            },
            'formality': {
                'en': {'formal': False, 'title_preference': 'first_name'},
                'de': {'formal': True, 'title_preference': 'last_name'},
                'ja': {'formal': True, 'title_preference': 'title_last_name'}
            },
            'direction': {
                'ar': 'rtl',
                'he': 'rtl',
                'default': 'ltr'
            }
        }
    
    def _setup_currency_mappings(self):
        """Setup currency mappings"""
        self.currency_mappings = {
            'USD': {'symbol': '$', 'position': 'before', 'locales': ['en', 'en-US']},
            'EUR': {'symbol': '€', 'position': 'after', 'locales': ['fr', 'de', 'es', 'it']},
            'GBP': {'symbol': '£', 'position': 'before', 'locales': ['en-GB']},
            'JPY': {'symbol': '¥', 'position': 'before', 'locales': ['ja']},
            'CNY': {'symbol': '¥', 'position': 'before', 'locales': ['zh']},
            'SAR': {'symbol': 'ريال', 'position': 'after', 'locales': ['ar']}
        }
    
    def _setup_date_patterns(self):
        """Setup date patterns"""
        self.date_patterns = {
            'en': 'MM/DD/YYYY',
            'en-US': 'MM/DD/YYYY',
            'en-GB': 'DD/MM/YYYY',
            'fr': 'DD/MM/YYYY',
            'de': 'DD.MM.YYYY',
            'es': 'DD/MM/YYYY',
            'it': 'DD/MM/YYYY',
            'zh': 'YYYY/MM/DD',
            'ja': 'YYYY/MM/DD',
            'ar': 'DD/MM/YYYY'
        }
    
    def localize_content(self, request: LocalizationRequest) -> LocalizationResult:
        """
        Localize content for target locale
        
        Args:
            request: Localization request with content and locale info
            
        Returns:
            LocalizationResult with localized content and metadata
        """
        try:
            content = request.content
            changes_made = []
            warnings = []
            
            # Apply number formatting
            content, number_changes = self._localize_numbers(
                content, request.source_locale, request.target_locale
            )
            changes_made.extend(number_changes)
            
            # Apply date formatting
            content, date_changes = self._localize_dates(
                content, request.source_locale, request.target_locale
            )
            changes_made.extend(date_changes)
            
            # Apply currency formatting
            content, currency_changes = self._localize_currency(
                content, request.source_locale, request.target_locale
            )
            changes_made.extend(currency_changes)
            
            # Apply cultural adaptations
            content, cultural_changes = self._apply_cultural_adaptations(
                content, request.source_locale, request.target_locale
            )
            changes_made.extend(cultural_changes)
            
            # Apply text direction for RTL languages
            content, direction_changes = self._apply_text_direction(
                content, request.target_locale, request.content_type
            )
            changes_made.extend(direction_changes)
            
            # Calculate confidence based on changes made
            confidence = self._calculate_localization_confidence(
                request.content, content, changes_made
            )
            
            return LocalizationResult(
                localized_content=content,
                source_locale=request.source_locale,
                target_locale=request.target_locale,
                content_type=request.content_type.value,
                confidence=confidence,
                changes_made=changes_made,
                warnings=warnings,
                metadata={
                    'level': request.level.value,
                    'preserve_formatting': request.preserve_formatting,
                    'total_changes': len(changes_made)
                }
            )
            
        except Exception as e:
            logger.error(f"Content localization failed: {str(e)}")
            return LocalizationResult(
                localized_content=request.content,  # Fallback to original
                source_locale=request.source_locale,
                target_locale=request.target_locale,
                content_type=request.content_type.value,
                confidence=0.0,
                changes_made=[],
                warnings=[f"Localization failed: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    def _localize_numbers(self, content: str, source_locale: str, target_locale: str) -> Tuple[str, List[str]]:
        """Localize number formatting"""
        changes = []
        
        if source_locale not in self.locale_mappings or target_locale not in self.locale_mappings:
            return content, changes
        
        source_config = self.locale_mappings[source_locale]
        target_config = self.locale_mappings[target_locale]
        
        # Convert decimal separators
        if source_config['decimal_separator'] != target_config['decimal_separator']:
            # Simple decimal conversion
            decimal_pattern = r'(\d+)\.(\d+)'
            matches = re.findall(decimal_pattern, content)
            for match in matches:
                old_format = f"{match[0]}.{match[1]}"
                new_format = f"{match[0]}{target_config['decimal_separator']}{match[1]}"
                content = content.replace(old_format, new_format)
                changes.append(f"Number format: {old_format} → {new_format}")
        
        return content, changes
    
    def _localize_dates(self, content: str, source_locale: str, target_locale: str) -> Tuple[str, List[str]]:
        """Localize date formatting"""
        changes = []
        
        if target_locale not in self.date_patterns:
            return content, changes
        
        # Simple date format conversion (MM/DD/YYYY to DD/MM/YYYY etc.)
        us_date_pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        matches = re.findall(us_date_pattern, content)
        
        for match in matches:
            month, day, year = match
            old_format = f"{month}/{day}/{year}"
            
            target_pattern = self.date_patterns[target_locale]
            if target_pattern == 'DD/MM/YYYY':
                new_format = f"{day}/{month}/{year}"
            elif target_pattern == 'DD.MM.YYYY':
                new_format = f"{day}.{month}.{year}"
            elif target_pattern == 'YYYY/MM/DD':
                new_format = f"{year}/{month}/{day}"
            else:
                new_format = old_format
            
            if old_format != new_format:
                content = content.replace(old_format, new_format)
                changes.append(f"Date format: {old_format} → {new_format}")
        
        return content, changes
    
    def _localize_currency(self, content: str, source_locale: str, target_locale: str) -> Tuple[str, List[str]]:
        """Localize currency formatting"""
        changes = []
        
        # Simple USD to EUR conversion example
        usd_pattern = r'\$(\d+(?:\.\d{2})?)'
        matches = re.findall(usd_pattern, content)
        
        for match in matches:
            old_format = f"${match}"
            
            if target_locale in ['fr', 'de', 'es', 'it']:
                new_format = f"{match}€"
                content = content.replace(old_format, new_format)
                changes.append(f"Currency format: {old_format} → {new_format}")
        
        return content, changes
    
    def _apply_cultural_adaptations(self, content: str, source_locale: str, target_locale: str) -> Tuple[str, List[str]]:
        """Apply cultural adaptations"""
        changes = []
        
        # Example: Adapt color references for cultural context
        if target_locale == 'zh':
            # In Chinese culture, red is often associated with good fortune
            content = content.replace('green light', 'red light')
            if 'green light' in content:
                changes.append("Cultural adaptation: green → red (Chinese context)")
        
        return content, changes
    
    def _apply_text_direction(self, content: str, target_locale: str, content_type: ContentType) -> Tuple[str, List[str]]:
        """Apply text direction for RTL languages"""
        changes = []
        
        if target_locale in ['ar', 'he'] and content_type == ContentType.HTML:
            # Add RTL direction to HTML content
            if '<html' in content and 'dir=' not in content:
                content = content.replace('<html', '<html dir="rtl"')
                changes.append("Added RTL text direction to HTML")
            elif content_type == ContentType.HTML and not content.startswith('<'):
                # Wrap text content in RTL div
                content = f'<div dir="rtl">{content}</div>'
                changes.append("Wrapped content in RTL container")
        
        return content, changes
    
    def _calculate_localization_confidence(self, original: str, localized: str, changes: List[str]) -> float:
        """Calculate confidence score for localization"""
        if original == localized:
            return 0.8  # No changes needed can be good
        
        if len(changes) == 0:
            return 0.5  # Content changed but no tracked changes
        
        # Higher confidence with more successful changes
        base_confidence = 0.7
        change_bonus = min(len(changes) * 0.05, 0.25)
        
        return min(base_confidence + change_bonus, 0.95)
    
    def get_supported_locales(self) -> List[str]:
        """Get list of supported locales"""
        return list(self.locale_mappings.keys())
    
    def get_locale_info(self, locale: str) -> Optional[Dict[str, Any]]:
        """Get locale configuration information"""
        return self.locale_mappings.get(locale)
    
    def batch_localize(self, requests: List[LocalizationRequest]) -> List[LocalizationResult]:
        """Localize multiple content items in batch"""
        results = []
        for request in requests:
            result = self.localize_content(request)
            results.append(result)
        return results
    
    def validate_locale(self, locale: str) -> bool:
        """Validate if locale is supported"""
        return locale in self.locale_mappings
    
    def get_cultural_preferences(self, locale: str) -> Dict[str, Any]:
        """Get cultural preferences for locale"""
        preferences = {}
        
        if locale in self.locale_mappings:
            locale_config = self.locale_mappings[locale]
            preferences.update(locale_config)
        
        # Add cultural adaptations
        for category, adaptations in self.cultural_adaptations.items():
            if locale in adaptations:
                preferences[category] = adaptations[locale]
            elif 'default' in adaptations:
                preferences[category] = adaptations['default']
        
        return preferences

# Create global instance
content_localizer = ContentLocalizer()

# Create alias for backward compatibility
LocalizationEngine = ContentLocalizer

# Export main classes and functions
__all__ = [
    'ContentLocalizer',
    'LocalizationEngine',  # Alias for authentication modules
    'LocalizationRequest',
    'LocalizationResult',
    'LocalizationLevel',
    'ContentType',
    'content_localizer'
]

# Log module initialization
logger.info("🌍 Content Localizer module loaded successfully")
logger.info("✅ Ready for comprehensive content localization")