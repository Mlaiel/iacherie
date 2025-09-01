"""Regional Format Validation Engine - Ainflue Platform
================================================================================
Module: core/i18n/regional_format_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Regional Format Validation Engine - Localized Data Processing
Responsibility: Phone, address, postal code, date/time format validation by region
Technologies: Python, Regex patterns, Regional standards, Format validation
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Input data → Region detection → Format pattern matching → Validation rules → 
Regional compliance → Cultural appropriateness → Error reporting → Standardization
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat

logger = logging.getLogger(__name__)


class ValidationResult:
    """Format validation result"""
    def __init__(self, is_valid: bool, standardized_value: str = "", errors: List[str] = None, suggestions: List[str] = None):
        self.is_valid = is_valid
        self.standardized_value = standardized_value
        self.errors = errors or []
        self.suggestions = suggestions or []
        self.confidence = 1.0 if is_valid else 0.0


@dataclass
class RegionalFormatRules:
    """Regional format rules for a specific country/region"""
    country_code: str
    country_name: str
    phone_patterns: List[str]
    postal_code_pattern: str
    address_format: str
    date_format: str
    time_format: str
    number_format: Dict[str, str]
    currency_format: str
    name_format: str
    business_registration_format: str = ""
    tax_id_format: str = ""
    bank_account_format: str = ""
    drivers_license_format: str = ""
    national_id_format: str = ""


class RegionalFormatValidator:
    """Comprehensive regional format validator for international localization"""
    
    def __init__(self):
        self.regional_rules = {}
        self.fallback_patterns = {}
        self._initialize_regional_rules()
        self._initialize_fallback_patterns()
    
    def _initialize_regional_rules(self):
        """Initialize comprehensive regional format rules"""
        
        # North America
        self.regional_rules["US"] = RegionalFormatRules(
            country_code="US",
            country_name="United States",
            phone_patterns=[
                r"^\+1\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$",
                r"^\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$",
                r"^1\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}(-[0-9]{4})?$",
            address_format="{street_number} {street_name}, {city}, {state} {postal_code}",
            date_format="%m/%d/%Y",
            time_format="%I:%M %p",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="${amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9]{9}$",  # EIN
            tax_id_format=r"^[0-9]{3}-[0-9]{2}-[0-9]{4}$",  # SSN
            bank_account_format=r"^[0-9]{9,17}$",
            drivers_license_format=r"^[A-Z]{1,2}[0-9]{6,8}$",
            national_id_format=r"^[0-9]{3}-[0-9]{2}-[0-9]{4}$"  # SSN
        )
        
        self.regional_rules["CA"] = RegionalFormatRules(
            country_code="CA",
            country_name="Canada",
            phone_patterns=[
                r"^\+1\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$",
                r"^\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[A-Za-z][0-9][A-Za-z]\s?[0-9][A-Za-z][0-9]$",
            address_format="{street_number} {street_name}, {city}, {province} {postal_code}",
            date_format="%Y-%m-%d",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="${amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9]{9}$",
            tax_id_format=r"^[0-9]{9}$",  # SIN
            bank_account_format=r"^[0-9]{7,12}$",
            national_id_format=r"^[0-9]{9}$"  # SIN
        )
        
        self.regional_rules["MX"] = RegionalFormatRules(
            country_code="MX",
            country_name="Mexico",
            phone_patterns=[
                r"^\+52\s?([0-9]{2,3})\s?([0-9]{3,4})\s?([0-9]{4})$",
                r"^([0-9]{2,3})\s?([0-9]{3,4})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{street_name} {street_number}, {colony}, {postal_code} {city}, {state}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="${amount}",
            name_format="{first} {paternal} {maternal}",
            business_registration_format=r"^[A-Z]{3}[0-9]{6}[A-Z0-9]{3}$",  # RFC
            tax_id_format=r"^[A-Z]{4}[0-9]{6}[A-Z0-9]{3}$",  # RFC
            national_id_format=r"^[A-Z]{4}[0-9]{6}[A-Z0-9]{3}$"  # CURP
        )
        
        # Europe
        self.regional_rules["GB"] = RegionalFormatRules(
            country_code="GB",
            country_name="United Kingdom",
            phone_patterns=[
                r"^\+44\s?([0-9]{4})\s?([0-9]{6})$",
                r"^\+44\s?([0-9]{3})\s?([0-9]{3})\s?([0-9]{4})$",
                r"^0([0-9]{4})\s?([0-9]{6})$",
                r"^0([0-9]{3})\s?([0-9]{3})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[A-Za-z]{1,2}[0-9Rr][0-9A-Za-z]?\s?[0-9][A-Za-z]{2}$",
            address_format="{house_number} {street_name}, {city}, {postal_code}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="£{amount}",
            name_format="{title} {first} {middle} {last}",
            business_registration_format=r"^[0-9]{8}$",  # Company number
            tax_id_format=r"^[A-Z]{2}[0-9]{6}[A-Z]$",  # VAT number
            national_id_format=r"^[A-Z]{2}[0-9]{6}[A-Z]$"  # National Insurance
        )
        
        self.regional_rules["FR"] = RegionalFormatRules(
            country_code="FR",
            country_name="France",
            phone_patterns=[
                r"^\+33\s?([0-9])\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})$",
                r"^0([0-9])\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{street_number} {street_name}, {postal_code} {city}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ",", "thousands": " "},
            currency_format="{amount} €",
            name_format="{first} {last}",
            business_registration_format=r"^[0-9]{3}\s?[0-9]{3}\s?[0-9]{3}$",  # SIREN
            tax_id_format=r"^FR[0-9A-Z]{2}[0-9]{9}$",  # VAT number
            national_id_format=r"^[0-9]{13}[0-9]{2}$"  # INSEE number
        )
        
        self.regional_rules["DE"] = RegionalFormatRules(
            country_code="DE",
            country_name="Germany",
            phone_patterns=[
                r"^\+49\s?([0-9]{3,4})\s?([0-9]{3,8})$",
                r"^0([0-9]{3,4})\s?([0-9]{3,8})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{street_name} {street_number}, {postal_code} {city}",
            date_format="%d.%m.%Y",
            time_format="%H:%M",
            number_format={"decimal": ",", "thousands": "."},
            currency_format="{amount} €",
            name_format="{first} {last}",
            business_registration_format=r"^[A-Z]{2}[0-9]{3}[A-Z0-9]{6}$",
            tax_id_format=r"^DE[0-9]{9}$",  # VAT number
            national_id_format=r"^[0-9]{11}$"  # Steuerliche Identifikationsnummer
        )
        
        # Middle East & North Africa
        self.regional_rules["AE"] = RegionalFormatRules(
            country_code="AE",
            country_name="United Arab Emirates",
            phone_patterns=[
                r"^\+971\s?([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$",
                r"^0([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{building}, {street}, {area}, {emirate}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="AED {amount}",
            name_format="{first} {father} {family}",
            business_registration_format=r"^[0-9]{7,15}$",
            tax_id_format=r"^[0-9]{15}$",  # TRN
            national_id_format=r"^784-[0-9]{4}-[0-9]{7}-[0-9]$"  # Emirates ID
        )
        
        self.regional_rules["SA"] = RegionalFormatRules(
            country_code="SA",
            country_name="Saudi Arabia",
            phone_patterns=[
                r"^\+966\s?([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$",
                r"^0([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}(-[0-9]{4})?$",
            address_format="{building_number}, {street_name}, {district}, {city} {postal_code}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="SAR {amount}",
            name_format="{first} {father} {grandfather} {family}",
            business_registration_format=r"^[0-9]{10}$",  # Commercial Registration
            tax_id_format=r"^[0-9]{15}$",  # VAT number
            national_id_format=r"^[0-9]{10}$"  # National ID
        )
        
        self.regional_rules["MA"] = RegionalFormatRules(
            country_code="MA",
            country_name="Morocco",
            phone_patterns=[
                r"^\+212\s?([0-9])\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})$",
                r"^0([0-9])\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})\s?([0-9]{2})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{street_number} {street_name}, {neighborhood}, {postal_code} {city}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ",", "thousands": " "},
            currency_format="{amount} MAD",
            name_format="{first} {family}",
            business_registration_format=r"^[0-9]{6,15}$",  # RC
            tax_id_format=r"^[0-9]{8}$",  # ICE
            national_id_format=r"^[A-Z]{1,2}[0-9]{6}$"  # CIN
        )
        
        self.regional_rules["EG"] = RegionalFormatRules(
            country_code="EG",
            country_name="Egypt",
            phone_patterns=[
                r"^\+20\s?([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$",
                r"^0([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}$",
            address_format="{building_number} {street_name}, {district}, {governorate} {postal_code}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="EGP {amount}",
            name_format="{first} {father} {grandfather} {family}",
            business_registration_format=r"^[0-9]{6,15}$",
            tax_id_format=r"^[0-9]{9}$",  # Tax card number
            national_id_format=r"^[0-9]{14}$"  # National ID
        )
        
        # Asia
        self.regional_rules["JP"] = RegionalFormatRules(
            country_code="JP",
            country_name="Japan",
            phone_patterns=[
                r"^\+81\s?([0-9]{2,4})\s?([0-9]{4})\s?([0-9]{4})$",
                r"^0([0-9]{2,4})\s?([0-9]{4})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{3}-[0-9]{4}$",
            address_format="{postal_code} {prefecture} {city} {district} {street} {building}",
            date_format="%Y/%m/%d",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="¥{amount}",
            name_format="{family} {given}",
            business_registration_format=r"^[0-9]{13}$",  # Corporate Number
            tax_id_format=r"^T[0-9]{13}$",  # Qualified Invoice Number
            national_id_format=r"^[0-9]{12}$"  # My Number
        )
        
        self.regional_rules["CN"] = RegionalFormatRules(
            country_code="CN",
            country_name="China",
            phone_patterns=[
                r"^\+86\s?([0-9]{3})\s?([0-9]{4})\s?([0-9]{4})$",
                r"^([0-9]{3})\s?([0-9]{4})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{6}$",
            address_format="{province} {city} {district} {street} {number}",
            date_format="%Y-%m-%d",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="¥{amount}",
            name_format="{family}{given}",
            business_registration_format=r"^[0-9A-Z]{18}$",  # USCI
            tax_id_format=r"^[0-9A-Z]{18}$",  # USCI
            national_id_format=r"^[0-9]{17}[0-9X]$"  # National ID
        )
        
        self.regional_rules["IN"] = RegionalFormatRules(
            country_code="IN",
            country_name="India",
            phone_patterns=[
                r"^\+91\s?([0-9]{5})\s?([0-9]{5})$",
                r"^([0-9]{5})\s?([0-9]{5})$"
            ],
            postal_code_pattern=r"^[0-9]{6}$",
            address_format="{house_number}, {street}, {locality}, {city} - {postal_code}, {state}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="₹{amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9A-Z]{21}$",  # CIN
            tax_id_format=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9]Z[0-9A-Z]$",  # GSTIN
            national_id_format=r"^[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}$"  # Aadhaar
        )
        
        # Africa
        self.regional_rules["ZA"] = RegionalFormatRules(
            country_code="ZA",
            country_name="South Africa",
            phone_patterns=[
                r"^\+27\s?([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$",
                r"^0([0-9]{2})\s?([0-9]{3})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{4}$",
            address_format="{street_number} {street_name}, {suburb}, {city}, {postal_code}",
            date_format="%Y/%m/%d",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": " "},
            currency_format="R{amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9]{10}$",  # Company registration number
            tax_id_format=r"^[0-9]{10}$",  # VAT number
            national_id_format=r"^[0-9]{13}$"  # ID number
        )
        
        # South America
        self.regional_rules["BR"] = RegionalFormatRules(
            country_code="BR",
            country_name="Brazil",
            phone_patterns=[
                r"^\+55\s?([0-9]{2})\s?([0-9]{4,5})\s?([0-9]{4})$",
                r"^([0-9]{2})\s?([0-9]{4,5})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{5}-[0-9]{3}$",
            address_format="{street_type} {street_name}, {number}, {neighborhood}, {city} - {state}, CEP {postal_code}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ",", "thousands": "."},
            currency_format="R$ {amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$",  # CNPJ
            tax_id_format=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$",  # CPF
            national_id_format=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$"  # CPF
        )
        
        # Australia & Oceania
        self.regional_rules["AU"] = RegionalFormatRules(
            country_code="AU",
            country_name="Australia",
            phone_patterns=[
                r"^\+61\s?([0-9])\s?([0-9]{4})\s?([0-9]{4})$",
                r"^0([0-9])\s?([0-9]{4})\s?([0-9]{4})$"
            ],
            postal_code_pattern=r"^[0-9]{4}$",
            address_format="{street_number} {street_name}, {suburb} {state} {postal_code}",
            date_format="%d/%m/%Y",
            time_format="%H:%M",
            number_format={"decimal": ".", "thousands": ","},
            currency_format="${amount}",
            name_format="{first} {middle} {last}",
            business_registration_format=r"^[0-9]{3}\s?[0-9]{3}\s?[0-9]{3}$",  # ABN
            tax_id_format=r"^[0-9]{9}$",  # TFN
            national_id_format=r"^[0-9]{9}$"  # TFN
        )
    
    def _initialize_fallback_patterns(self):
        """Initialize fallback patterns for unknown regions"""
        
        self.fallback_patterns = {
            "phone": [
                r"^\+[0-9]{1,4}\s?[0-9\s-()]{6,15}$",  # International format
                r"^[0-9\s-()]{7,15}$"  # Local format
            ],
            "postal_code": [
                r"^[A-Za-z0-9\s-]{3,10}$"  # Generic alphanumeric
            ],
            "email": [
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            ],
            "website": [
                r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
            ]
        }
    
    def validate_phone_number(self, phone: str, country_code: str = None) -> ValidationResult:
        """Validate phone number for specific country or globally"""
        
        try:
            # Clean input
            phone_clean = re.sub(r'[^\d+()-\s]', '', phone.strip())
            
            if country_code and country_code in self.regional_rules:
                # Validate against specific country patterns
                rules = self.regional_rules[country_code]
                
                for pattern in rules.phone_patterns:
                    if re.match(pattern, phone_clean):
                        # Use phonenumbers library for standardization
                        try:
                            parsed = phonenumbers.parse(phone_clean, country_code)
                            if phonenumbers.is_valid_number(parsed):
                                standardized = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
                                return ValidationResult(
                                    is_valid=True,
                                    standardized_value=standardized
                                )
                        except NumberParseException:
                            pass
                        
                        return ValidationResult(
                            is_valid=True,
                            standardized_value=phone_clean
                        )
                
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Phone number does not match {rules.country_name} format"],
                    suggestions=[f"Expected format: {rules.phone_patterns[0]}"]
                )
            
            else:
                # Try fallback patterns
                for pattern in self.fallback_patterns["phone"]:
                    if re.match(pattern, phone_clean):
                        return ValidationResult(
                            is_valid=True,
                            standardized_value=phone_clean
                        )
                
                return ValidationResult(
                    is_valid=False,
                    errors=["Phone number format not recognized"],
                    suggestions=["Please include country code (e.g., +1 555-123-4567)"]
                )
        
        except Exception as e:
            logger.error(f"Error validating phone number: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def validate_postal_code(self, postal_code: str, country_code: str = None) -> ValidationResult:
        """Validate postal code for specific country"""
        
        try:
            postal_clean = postal_code.strip().upper()
            
            if country_code and country_code in self.regional_rules:
                rules = self.regional_rules[country_code]
                
                if re.match(rules.postal_code_pattern, postal_clean):
                    return ValidationResult(
                        is_valid=True,
                        standardized_value=postal_clean
                    )
                
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Postal code does not match {rules.country_name} format"],
                    suggestions=[f"Expected format: {rules.postal_code_pattern}"]
                )
            
            else:
                # Try fallback patterns
                for pattern in self.fallback_patterns["postal_code"]:
                    if re.match(pattern, postal_clean):
                        return ValidationResult(
                            is_valid=True,
                            standardized_value=postal_clean
                        )
                
                return ValidationResult(
                    is_valid=False,
                    errors=["Postal code format not recognized"]
                )
        
        except Exception as e:
            logger.error(f"Error validating postal code: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def validate_address(self, address_components: Dict[str, str], country_code: str = None) -> ValidationResult:
        """Validate complete address structure"""
        
        try:
            if country_code and country_code in self.regional_rules:
                rules = self.regional_rules[country_code]
                
                # Check required components based on country format
                required_components = self._extract_required_components(rules.address_format)
                missing_components = []
                
                for component in required_components:
                    if component not in address_components or not address_components[component].strip():
                        missing_components.append(component)
                
                if missing_components:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Missing required address components: {', '.join(missing_components)}"],
                        suggestions=[f"Expected format: {rules.address_format}"]
                    )
                
                # Validate postal code if present
                if "postal_code" in address_components:
                    postal_result = self.validate_postal_code(address_components["postal_code"], country_code)
                    if not postal_result.is_valid:
                        return ValidationResult(
                            is_valid=False,
                            errors=postal_result.errors,
                            suggestions=postal_result.suggestions
                        )
                
                # Format standardized address
                standardized = self._format_address(address_components, rules.address_format)
                
                return ValidationResult(
                    is_valid=True,
                    standardized_value=standardized
                )
            
            else:
                # Basic validation for unknown countries
                required = ["street_name", "city"]
                missing = [comp for comp in required if comp not in address_components or not address_components[comp].strip()]
                
                if missing:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Missing required components: {', '.join(missing)}"]
                    )
                
                return ValidationResult(
                    is_valid=True,
                    standardized_value=str(address_components)
                )
        
        except Exception as e:
            logger.error(f"Error validating address: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def validate_national_id(self, national_id: str, country_code: str) -> ValidationResult:
        """Validate national ID number for specific country"""
        
        try:
            if country_code not in self.regional_rules:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Validation rules not available for country: {country_code}"]
                )
            
            rules = self.regional_rules[country_code]
            id_clean = re.sub(r'[^\w]', '', national_id.strip().upper())
            
            if re.match(rules.national_id_format, national_id.strip()):
                # Additional validation based on country-specific algorithms
                if country_code == "US":  # SSN validation
                    return self._validate_ssn(national_id.strip())
                elif country_code == "BR":  # CPF validation
                    return self._validate_cpf(id_clean)
                elif country_code == "ZA":  # South African ID validation
                    return self._validate_south_african_id(id_clean)
                else:
                    return ValidationResult(
                        is_valid=True,
                        standardized_value=national_id.strip()
                    )
            
            return ValidationResult(
                is_valid=False,
                errors=[f"National ID does not match {rules.country_name} format"],
                suggestions=[f"Expected format: {rules.national_id_format}"]
            )
        
        except Exception as e:
            logger.error(f"Error validating national ID: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def validate_business_registration(self, registration: str, country_code: str) -> ValidationResult:
        """Validate business registration number for specific country"""
        
        try:
            if country_code not in self.regional_rules:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Validation rules not available for country: {country_code}"]
                )
            
            rules = self.regional_rules[country_code]
            
            if re.match(rules.business_registration_format, registration.strip()):
                return ValidationResult(
                    is_valid=True,
                    standardized_value=registration.strip()
                )
            
            return ValidationResult(
                is_valid=False,
                errors=[f"Business registration does not match {rules.country_name} format"],
                suggestions=[f"Expected format: {rules.business_registration_format}"]
            )
        
        except Exception as e:
            logger.error(f"Error validating business registration: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def _extract_required_components(self, format_string: str) -> List[str]:
        """Extract required components from address format string"""
        components = re.findall(r'\{(\w+)\}', format_string)
        return components
    
    def _format_address(self, components: Dict[str, str], format_string: str) -> str:
        """Format address according to regional format"""
        try:
            return format_string.format(**components)
        except KeyError as e:
            return str(components)  # Fallback to dict representation
    
    def _validate_ssn(self, ssn: str) -> ValidationResult:
        """Validate US Social Security Number"""
        # Remove dashes
        ssn_digits = re.sub(r'[^\d]', '', ssn)
        
        if len(ssn_digits) != 9:
            return ValidationResult(
                is_valid=False,
                errors=["SSN must be 9 digits"]
            )
        
        # Check for invalid patterns
        invalid_patterns = [
            "000", "666", "900", "999"  # Invalid area numbers
        ]
        
        area = ssn_digits[:3]
        if area in invalid_patterns or area.startswith("9"):
            return ValidationResult(
                is_valid=False,
                errors=["Invalid SSN area number"]
            )
        
        # Format standardized SSN
        standardized = f"{ssn_digits[:3]}-{ssn_digits[3:5]}-{ssn_digits[5:]}"
        
        return ValidationResult(
            is_valid=True,
            standardized_value=standardized
        )
    
    def _validate_cpf(self, cpf: str) -> ValidationResult:
        """Validate Brazilian CPF"""
        if len(cpf) != 11:
            return ValidationResult(
                is_valid=False,
                errors=["CPF must be 11 digits"]
            )
        
        # Check for repeated digits
        if cpf == cpf[0] * 11:
            return ValidationResult(
                is_valid=False,
                errors=["CPF cannot be all same digits"]
            )
        
        # Calculate verification digits
        def calculate_digit(cpf_digits, multiplier):
            total = sum(int(cpf_digits[i]) * multiplier[i] for i in range(len(multiplier)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # First verification digit
        digit1 = calculate_digit(cpf, [10, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(cpf[9]) != digit1:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid CPF verification digit"]
            )
        
        # Second verification digit
        digit2 = calculate_digit(cpf, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(cpf[10]) != digit2:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid CPF verification digit"]
            )
        
        # Format standardized CPF
        standardized = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        return ValidationResult(
            is_valid=True,
            standardized_value=standardized
        )
    
    def _validate_south_african_id(self, id_number: str) -> ValidationResult:
        """Validate South African ID number"""
        if len(id_number) != 13:
            return ValidationResult(
                is_valid=False,
                errors=["South African ID must be 13 digits"]
            )
        
        # Extract components
        birth_date = id_number[:6]
        gender = int(id_number[6:10])
        citizenship = int(id_number[10])
        
        # Validate birth date
        try:
            year = int("19" + birth_date[:2]) if int(birth_date[:2]) > 21 else int("20" + birth_date[:2])
            month = int(birth_date[2:4])
            day = int(birth_date[4:6])
            
            if month < 1 or month > 12 or day < 1 or day > 31:
                return ValidationResult(
                    is_valid=False,
                    errors=["Invalid birth date in ID number"]
                )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid birth date format in ID number"]
            )
        
        # Validate check digit using Luhn algorithm
        digits = [int(d) for d in id_number[:12]]
        
        # Luhn algorithm for check digit
        for i in range(1, 12, 2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] = digits[i] // 10 + digits[i] % 10
        
        total = sum(digits)
        check_digit = (10 - (total % 10)) % 10
        
        if int(id_number[12]) != check_digit:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid ID number check digit"]
            )
        
        return ValidationResult(
            is_valid=True,
            standardized_value=id_number
        )
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries for validation"""
        return list(self.regional_rules.keys())
    
    def get_country_format_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get format information for a specific country"""
        if country_code not in self.regional_rules:
            return None
        
        rules = self.regional_rules[country_code]
        return {
            "country_code": rules.country_code,
            "country_name": rules.country_name,
            "phone_formats": rules.phone_patterns,
            "postal_code_format": rules.postal_code_pattern,
            "address_format": rules.address_format,
            "date_format": rules.date_format,
            "time_format": rules.time_format,
            "number_format": rules.number_format,
            "currency_format": rules.currency_format,
            "name_format": rules.name_format
        }