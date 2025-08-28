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
    ),
    
    # Additional Arabic dialects - Middle East & North Africa
    "ar_EG": DialectLocalization(
        dialect_code="ar_EG",
        region="Egypt",
        currency_symbol="ج.م",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+20 {area_code} {number}",
        country_code="20",
        greeting_style="friendly",
        politeness_level="medium"
    ),
    
    "ar_LB": DialectLocalization(
        dialect_code="ar_LB",
        region="Lebanon (Levantine)",
        currency_symbol="ل.ل",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+961 {area_code} {number}",
        country_code="961",
        greeting_style="warm",
        politeness_level="medium"
    ),
    
    "ar_AE": DialectLocalization(
        dialect_code="ar_AE",
        region="UAE (Gulf)",
        currency_symbol="د.إ",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+971 {area_code} {number}",
        country_code="971",
        greeting_style="formal",
        politeness_level="high",
        business_hours_format="12h"
    ),
    
    "ar_IQ": DialectLocalization(
        dialect_code="ar_IQ",
        region="Iraq (Mesopotamian)",
        currency_symbol="د.ع",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+964 {area_code} {number}",
        country_code="964",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    # Extended Spanish dialects - Latin America
    "es_AR": DialectLocalization(
        dialect_code="es_AR",
        region="Argentina (Rioplatense)",
        currency_symbol="$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+54 {area_code} {number}",
        country_code="54",
        greeting_style="friendly",
        politeness_level="medium",
        directness_preference="direct"
    ),
    
    "es_CO": DialectLocalization(
        dialect_code="es_CO",
        region="Colombia (Andean)",
        currency_symbol="$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+57 {area_code} {number}",
        country_code="57",
        greeting_style="warm",
        politeness_level="high"
    ),
    
    "es_PE": DialectLocalization(
        dialect_code="es_PE",
        region="Peru (Andean)",
        currency_symbol="S/",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+51 {area_code} {number}",
        country_code="51",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    "es_CU": DialectLocalization(
        dialect_code="es_CU",
        region="Cuba (Caribbean)",
        currency_symbol="$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+53 {area_code} {number}",
        country_code="53",
        greeting_style="warm",
        politeness_level="medium"
    ),
    
    # Extended French dialects - Francophonie
    "fr_BE": DialectLocalization(
        dialect_code="fr_BE",
        region="Belgium (Wallonia)",
        currency_symbol="€",
        currency_position="after",
        decimal_separator=",",
        thousand_separator=" ",
        date_format="%d/%m/%Y",
        phone_format="+32 {area_code} {number}",
        country_code="32",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    "fr_CI": DialectLocalization(
        dialect_code="fr_CI",
        region="Côte d'Ivoire (West African)",
        currency_symbol="CFA",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+225 {number}",
        country_code="225",
        greeting_style="respectful",
        politeness_level="high"
    ),
    
    "fr_SN": DialectLocalization(
        dialect_code="fr_SN",
        region="Senegal (West African)",
        currency_symbol="CFA",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+221 {number}",
        country_code="221",
        greeting_style="respectful",
        politeness_level="high"
    ),
    
    # Extended Portuguese dialects
    "pt_AO": DialectLocalization(
        dialect_code="pt_AO",
        region="Angola (African Portuguese)",
        currency_symbol="Kz",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+244 {area_code} {number}",
        country_code="244",
        greeting_style="respectful",
        politeness_level="high"
    ),
    
    "pt_MZ": DialectLocalization(
        dialect_code="pt_MZ",
        region="Mozambique (African Portuguese)",
        currency_symbol="MT",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+258 {area_code} {number}",
        country_code="258",
        greeting_style="respectful",
        politeness_level="high"
    ),
    
    # Extended Chinese dialects
    "zh_HK": DialectLocalization(
        dialect_code="zh_HK",
        region="Hong Kong (Cantonese)",
        currency_symbol="HK$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+852 {number}",
        country_code="852",
        greeting_style="respectful",
        politeness_level="high",
        business_hours_format="12h"
    ),
    
    "zh_SG": DialectLocalization(
        dialect_code="zh_SG",
        region="Singapore (Mandarin)",
        currency_symbol="S$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+65 {number}",
        country_code="65",
        greeting_style="neutral",
        politeness_level="medium"
    ),
    
    # Additional Amazigh/Berber dialects
    "rif_MA": DialectLocalization(
        dialect_code="rif_MA",
        region="Morocco (Rif Mountains)",
        currency_symbol="د.م.",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+212 {area_code} {number}",
        country_code="212",
        greeting_style="traditional",
        politeness_level="high"
    ),
    
    "shi_MA": DialectLocalization(
        dialect_code="shi_MA",
        region="Morocco (Tashelhit/Souss)",
        currency_symbol="د.م.",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+212 {area_code} {number}",
        country_code="212",
        greeting_style="traditional",
        politeness_level="high"
    ),
    
    # Extended German dialects
    "de_AT": DialectLocalization(
        dialect_code="de_AT",
        region="Austria (Austrian German)",
        currency_symbol="€",
        currency_position="after",
        decimal_separator=",",
        thousand_separator=".",
        date_format="%d.%m.%Y",
        phone_format="+43 {area_code} {number}",
        country_code="43",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    "de_LU": DialectLocalization(
        dialect_code="de_LU",
        region="Luxembourg (Luxembourgish German)",
        currency_symbol="€",
        currency_position="after",
        date_format="%d.%m.%Y",
        phone_format="+352 {number}",
        country_code="352",
        greeting_style="formal",
        politeness_level="high"
    ),
    
    # Additional indigenous and regional languages
    "qu_PE": DialectLocalization(
        dialect_code="qu_PE",
        region="Peru (Quechua)",
        currency_symbol="S/",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+51 {area_code} {number}",
        country_code="51",
        greeting_style="traditional",
        politeness_level="high"
    ),
    
    "nah_MX": DialectLocalization(
        dialect_code="nah_MX",
        region="Mexico (Nahuatl)",
        currency_symbol="$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+52 {area_code} {number}",
        country_code="52",
        greeting_style="traditional",
        politeness_level="high"
    ),
    
    # Enhanced indigenous and local dialect support
    "qu_PE": DialectLocalization(
        dialect_code="qu_PE",
        region="Peru (Quechua)",
        currency_symbol="S/",
        currency_position="before", 
        date_format="%d/%m/%Y",
        phone_format="+51 {area_code} {number}",
        country_code="51",
        greeting_style="traditional",
        politeness_level="high"
    ),
    
    "en_SG": DialectLocalization(
        dialect_code="en_SG",
        region="Singapore (Singlish)",
        currency_symbol="S$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+65 {number}",
        country_code="65",
        greeting_style="casual",
        politeness_level="medium"
    ),
    
    "en_MY": DialectLocalization(
        dialect_code="en_MY", 
        region="Malaysia (Malaysian English)",
        currency_symbol="RM",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+60 {area_code} {number}",
        country_code="60",
        greeting_style="casual",
        politeness_level="medium"
    ),
    
    "zh_HK_cant": DialectLocalization(
        dialect_code="zh_HK_cant",
        region="Hong Kong (Cantonese Traditional)",
        currency_symbol="HK$",
        currency_position="before",
        date_format="%d/%m/%Y",
        phone_format="+852 {number}",
        country_code="852",
        greeting_style="respectful",
        politeness_level="high"
    ),
    
    "ar_EG_local": DialectLocalization(
        dialect_code="ar_EG_local",
        region="Egypt (Egyptian Arabic)",
        currency_symbol="ج.م",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+20 {area_code} {number}",
        country_code="20",
        greeting_style="warm",
        politeness_level="medium"
    ),
    
    "fr_SN": DialectLocalization(
        dialect_code="fr_SN",
        region="Senegal (Wolof-French)",
        currency_symbol="CFA",
        currency_position="after",
        date_format="%d/%m/%Y",
        phone_format="+221 {number}",
        country_code="221",
        greeting_style="respectful",
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