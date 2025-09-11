"""Data Masking Utilities for MongoDB
===================================

Advanced data masking and anonymization for sensitive data protection
with multiple masking strategies and reversible/irreversible options.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import hashlib
import secrets
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MaskingStrategy(Enum):
    """Data masking strategies."""
    REDACTION = "redaction"  # Replace with asterisks
    RANDOMIZATION = "randomization"  # Replace with random data
    SUBSTITUTION = "substitution"  # Replace with fake data
    HASHING = "hashing"  # One-way hash
    PARTIAL_MASKING = "partial_masking"  # Mask part of the data
    FORMAT_PRESERVING = "format_preserving"  # Keep format, change data

class DataMasking:
    """Data masking and anonymization utilities."""
    
    def __init__(self):
        """Initialize data masking."""
        self._masking_cache: Dict[str, str] = {}
        self._salt = secrets.token_hex(16)
    
    def mask_email(self, email: str, strategy: MaskingStrategy = MaskingStrategy.PARTIAL_MASKING) -> str:
        """Mask email address."""
        if not email or '@' not in email:
            return email
        
        if strategy == MaskingStrategy.REDACTION:
            return "***@***.***"
        elif strategy == MaskingStrategy.PARTIAL_MASKING:
            user, domain = email.split('@', 1)
            masked_user = user[0] + '*' * (len(user) - 1) if len(user) > 1 else '*'
            return f"{masked_user}@{domain}"
        elif strategy == MaskingStrategy.HASHING:
            return hashlib.sha256(f"{email}:{self._salt}".encode()).hexdigest()[:16]
        else:
            return "user@example.com"
    
    def mask_phone(self, phone: str, strategy: MaskingStrategy = MaskingStrategy.PARTIAL_MASKING) -> str:
        """Mask phone number."""
        if not phone:
            return phone
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        if strategy == MaskingStrategy.REDACTION:
            return "***-***-****"
        elif strategy == MaskingStrategy.PARTIAL_MASKING:
            if len(digits) >= 10:
                return f"***-***-{digits[-4:]}"
            return '*' * len(digits)
        elif strategy == MaskingStrategy.HASHING:
            return hashlib.sha256(f"{phone}:{self._salt}".encode()).hexdigest()[:12]
        else:
            return "555-555-5555"
    
    def mask_credit_card(self, card_number: str, strategy: MaskingStrategy = MaskingStrategy.PARTIAL_MASKING) -> str:
        """Mask credit card number."""
        if not card_number:
            return card_number
        
        digits = re.sub(r'\D', '', card_number)
        
        if strategy == MaskingStrategy.REDACTION:
            return "****-****-****-****"
        elif strategy == MaskingStrategy.PARTIAL_MASKING:
            if len(digits) >= 16:
                return f"****-****-****-{digits[-4:]}"
            return '*' * len(digits)
        elif strategy == MaskingStrategy.HASHING:
            return hashlib.sha256(f"{card_number}:{self._salt}".encode()).hexdigest()[:16]
        else:
            return "4000-0000-0000-0000"
    
    def mask_document(self, document: Dict[str, Any], 
                     masking_rules: Dict[str, MaskingStrategy] = None) -> Dict[str, Any]:
        """Mask sensitive fields in a document."""
        if not document:
            return document
        
        # Default masking rules
        default_rules = {
            'email': MaskingStrategy.PARTIAL_MASKING,
            'phone': MaskingStrategy.PARTIAL_MASKING,
            'credit_card': MaskingStrategy.PARTIAL_MASKING,
            'ssn': MaskingStrategy.REDACTION,
            'password': MaskingStrategy.REDACTION,
            'api_key': MaskingStrategy.REDACTION,
            'token': MaskingStrategy.REDACTION
        }
        
        rules = masking_rules or default_rules
        masked_doc = {}
        
        for field_name, value in document.items():
            if isinstance(value, dict):
                # Recursively mask nested documents
                masked_doc[field_name] = self.mask_document(value, rules)
            elif field_name.lower() in rules:
                strategy = rules[field_name.lower()]
                masked_doc[field_name] = self._mask_field_value(value, field_name, strategy)
            else:
                masked_doc[field_name] = value
        
        return masked_doc
    
    def _mask_field_value(self, value: Any, field_name: str, strategy: MaskingStrategy) -> Any:
        """Mask individual field value."""
        if value is None:
            return value
        
        value_str = str(value)
        field_lower = field_name.lower()
        
        if 'email' in field_lower:
            return self.mask_email(value_str, strategy)
        elif 'phone' in field_lower:
            return self.mask_phone(value_str, strategy)
        elif 'credit' in field_lower or 'card' in field_lower:
            return self.mask_credit_card(value_str, strategy)
        elif strategy == MaskingStrategy.REDACTION:
            return '*' * len(value_str)
        elif strategy == MaskingStrategy.HASHING:
            return hashlib.sha256(f"{value_str}:{self._salt}".encode()).hexdigest()[:16]
        elif strategy == MaskingStrategy.PARTIAL_MASKING:
            if len(value_str) <= 3:
                return '*' * len(value_str)
            return value_str[:2] + '*' * (len(value_str) - 4) + value_str[-2:]
        else:
            return "***MASKED***"

# Global data masking instance
_default_masking: Optional[DataMasking] = None

def get_data_masking() -> DataMasking:
    """Get or create default data masking instance."""
    global _default_masking
    if _default_masking is None:
        _default_masking = DataMasking()
    return _default_masking

__all__ = ['MaskingStrategy', 'DataMasking', 'get_data_masking']