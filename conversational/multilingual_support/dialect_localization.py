"""
Dialect-Specific Localization Features
Enhanced regional customization for comprehensive multilingual support

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LocalizationFeature(Enum):
    """Enhanced localization features for regional variants"""
    CURRENCY_FORMAT = "currency_format"
    DATE_FORMAT = "date_format"
    TIME_FORMAT = "time_format"
    NUMBER_FORMAT = "number_format"
    ADDRESS_FORMAT = "address_format"
    PHONE_FORMAT = "phone_format"
    MEASUREMENT_UNITS = "measurement_units"
    CALENDAR_SYSTEM = "calendar_system"

@dataclass
class DialectLocalization:
    """Comprehensive dialect-specific localization settings"""
    dialect_code: str
    region: str
    
    # Currency and numbers
    currency_symbol: str = "$"
    currency_position: str = "before"  # before, after
    decimal_separator: str = "."
    thousand_separator: str = ","
    currency_decimal_places: int = 2
    
    # Date and time formats
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M"
    datetime_format: str = "%Y-%m-%d %H:%M"
    first_day_of_week: int = 1  # 0=Sunday, 1=Monday
    week_numbering: str = "iso"  # iso, us
    
    # Address formatting
    address_format: str = "{street}\n{city}, {state} {postal_code}\n{country}"
    postal_code_format: str = r"^\d{5}(-\d{4})?$"
    
    # Phone formatting
    phone_format: str = "+{country_code} {area_code} {number}"
    country_code: str = "1"
    
    # Measurement preferences
    temperature_unit: str = "celsius"  # celsius, fahrenheit
    distance_unit: str = "metric"     # metric, imperial
    weight_unit: str = "metric"       # metric, imperial
    
    # Cultural preferences
    formal_address_required: bool = False
    business_hours_format: str = "24h"  # 12h, 24h
    punctuality_tolerance: int = 15  # minutes
    
    # Content preferences
    greeting_style: str = "neutral"   # formal, neutral, casual
    politeness_level: str = "medium"  # low, medium, high
    directness_preference: str = "balanced"  # direct, indirect, balanced

# Pre-configured dialect localizations
DIALECT_LOCALIZATIONS: Dict[str, DialectLocalization] = {
    # English variants
    "en_US": DialectLocalization(
        dialect_code="en_US",
        region="United States",
        currency_symbol="$",
        date_format="%m/%d/%Y",
        address_format="{street}\n{city}, {state} {postal_code}",
        postal_code_format=r"^\d{5}(-\d{4})?$",
        phone_format="+1 ({area_code}) {number}",
        temperature_unit="fahrenheit",
        distance_unit="imperial",
        first_day_of_week=0,
        greeting_style="casual",
        directness_preference="direct"
    ),
    
    "en_GB": DialectLocalization(
        dialect_code="en_GB",
        region="United Kingdom",
        currency_symbol="£",
        date_format="%d/%m/%Y",
        address_format="{street}\n{city}\n{postal_code}",
        postal_code_format=r"^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}$",
        phone_format="+44 {area_code} {number}",
        country_code="44",
        greeting_style="formal",
        politeness_level="high",
        directness_preference="indirect"
    ),
    
    "en_AU": DialectLocalization(
        dialect_code="en_AU",
        region="Australia",
        currency_symbol="A$",
        date_format="%d/%m/%Y",
        postal_code_format=r"^\d{4}$",
        phone_format="+61 {area_code} {number}",
        country_code="61",
        greeting_style="casual",
        directness_preference="direct"
    ),
    
    # German variants
    "de_DE": DialectLocalization(
        dialect_code="de_DE",
        region="Germany",
        currency_symbol="€",
        currency_position="after",
        decimal_separator=",",
        thousand_separator=".",
        date_format="%d.%m.%Y",
        time_format="%H:%M",
        phone_format="+49 {area_code} {number}",
        country_code="49",
        formal_address_required=True,
        greeting_style="formal",
        politeness_level="high",
        punctuality_tolerance=5
    ),
    
    "de_CH": DialectLocalization(
        dialect_code="de_CH",
        region="Switzerland",
        currency_symbol="CHF",
        currency_position="before",
        date_format="%d.%m.%Y",
        postal_code_format=r"^\d{4}$",
        phone_format="+41 {area_code} {number}",
        country_code="41",
        formal_address_required=True,
        greeting_style="formal",
        politeness_level="high",
        punctuality_tolerance=0  # Swiss precision!
    ),
    
    # Arabic variants
    "ar_SA": DialectLocalization(
        dialect_code="ar_SA",
        region="Saudi Arabia",
        currency_symbol="ر.س",
        currency_position="after",
        date_format="%d/%m/%Y",
        first_day_of_week=6,  # Saturday
        phone_format="+966 {area_code} {number}",
        country_code="966",
        formal_address_required=True,
        greeting_style="formal",
        politeness_level="high",
        business_hours_format="12h"
    ),
    
    "ar_MA": DialectLocalization(
        dialect_code="ar_MA",
        region="Morocco",
        currency_symbol="د.م.",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+212 {area_code} {number}",
        country_code="212",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    # French variants
    "fr_FR": DialectLocalization(
        dialect_code="fr_FR",
        region="France",
        currency_symbol="€",
        currency_position="after",
        decimal_separator=",",
        thousand_separator=" ",
        date_format="%d/%m/%Y",
        phone_format="+33 {area_code} {number}",
        country_code="33",
        greeting_style="formal",
        politeness_level="high",
        directness_preference="indirect"
    ),
    
    "fr_CA": DialectLocalization(
        dialect_code="fr_CA",
        region="Quebec, Canada",
        currency_symbol="$",
        date_format="%Y-%m-%d",
        phone_format="+1 ({area_code}) {number}",
        country_code="1",
        greeting_style="neutral",
        politeness_level="medium",
        temperature_unit="celsius",
        distance_unit="metric"
    ),
    
    # Spanish variants
    "es_ES": DialectLocalization(
        dialect_code="es_ES",
        region="Spain",
        currency_symbol="€",
        currency_position="after",
        decimal_separator=",",
        thousand_separator=".",
        date_format="%d/%m/%Y",
        phone_format="+34 {number}",
        country_code="34",
        greeting_style="formal",
        politeness_level="medium"
    ),
    
    "es_MX": DialectLocalization(
        dialect_code="es_MX",
        region="Mexico",
        currency_symbol="$",
        date_format="%d/%m/%Y",
        phone_format="+52 {area_code} {number}",
        country_code="52",
        greeting_style="neutral",
        politeness_level="medium"
    ),
    
    # Amazigh/Berber variants
    "tzm_MA": DialectLocalization(
        dialect_code="tzm_MA",
        region="Morocco (Central Atlas)",
        currency_symbol="د.م.",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+212 {area_code} {number}",
        country_code="212",
        formal_address_required=True,
        greeting_style="formal",
        politeness_level="high",
        first_day_of_week=1  # Monday
    ),
    
    "kab_DZ": DialectLocalization(
        dialect_code="kab_DZ", 
        region="Algeria (Kabylie)",
        currency_symbol="د.ج",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+213 {area_code} {number}",
        country_code="213",
        greeting_style="formal",
        politeness_level="high"
    )
}

class EnhancedDialectProcessor:
    """Enhanced processor for dialect-specific content formatting"""
    
    def __init__(self):
        self.localizations = DIALECT_LOCALIZATIONS
    
    def format_currency(self, amount: float, dialect_code: str) -> str:
        """Format currency according to dialect preferences"""
        localization = self.localizations.get(dialect_code)
        if not localization:
            return f"${amount:.2f}"  # Default fallback
            
        formatted_amount = f"{amount:.{localization.currency_decimal_places}f}"
        
        # Apply thousand separators
        if localization.thousand_separator:
            parts = formatted_amount.split('.')
            parts[0] = self._add_thousand_separators(parts[0], localization.thousand_separator)
            formatted_amount = localization.decimal_separator.join(parts)
        
        # Apply currency symbol position
        if localization.currency_position == "before":
            return f"{localization.currency_symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {localization.currency_symbol}"
    
    def format_date(self, date_obj, dialect_code: str) -> str:
        """Format date according to dialect preferences"""
        localization = self.localizations.get(dialect_code)
        if not localization:
            return date_obj.strftime("%Y-%m-%d")
            
        return date_obj.strftime(localization.date_format)
    
    def format_phone(self, number: str, area_code: str, dialect_code: str) -> str:
        """Format phone number according to dialect preferences"""
        localization = self.localizations.get(dialect_code)
        if not localization:
            return f"+1 {area_code} {number}"
            
        return localization.phone_format.format(
            country_code=localization.country_code,
            area_code=area_code,
            number=number
        )
    
    def get_greeting_style(self, dialect_code: str) -> str:
        """Get appropriate greeting style for dialect"""
        localization = self.localizations.get(dialect_code)
        return localization.greeting_style if localization else "neutral"
    
    def get_cultural_preferences(self, dialect_code: str) -> Dict[str, Any]:
        """Get cultural preferences for dialect"""
        localization = self.localizations.get(dialect_code)
        if not localization:
            return {}
            
        return {
            "formal_address_required": localization.formal_address_required,
            "punctuality_tolerance": localization.punctuality_tolerance,
            "politeness_level": localization.politeness_level,
            "directness_preference": localization.directness_preference,
            "business_hours_format": localization.business_hours_format
        }
    
    def _add_thousand_separators(self, number_str: str, separator: str) -> str:
        """Add thousand separators to number string"""
        reversed_chars = list(reversed(number_str))
        grouped = []
        
        for i, char in enumerate(reversed_chars):
            if i > 0 and i % 3 == 0:
                grouped.append(separator)
            grouped.append(char)
            
        return ''.join(reversed(grouped))

# Global instance for easy access
dialect_processor = EnhancedDialectProcessor()