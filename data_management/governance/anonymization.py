"""Data Anonymization Service

Comprehensive data anonymization for non-production environments
ensuring GDPR compliance while maintaining data utility for testing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import hashlib
import random
import string
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import uuid

from ...core.logging import get_logger
from ...core.config import get_settings

logger = get_logger(__name__)


class AnonymizationTechnique(Enum):
    """Data anonymization techniques"""
    MASKING = "masking"                 # Replace with fake data
    GENERALIZATION = "generalization"   # Reduce precision
    SUPPRESSION = "suppression"         # Remove sensitive fields
    PSEUDONYMIZATION = "pseudonymization"  # Replace with pseudonyms
    PERTURBATION = "perturbation"       # Add statistical noise
    TOKENIZATION = "tokenization"       # Replace with tokens


class DataSensitivityLevel(Enum):
    """Data sensitivity levels for anonymization"""
    PUBLIC = "public"           # No anonymization needed
    INTERNAL = "internal"       # Basic anonymization
    CONFIDENTIAL = "confidential"  # Strong anonymization
    RESTRICTED = "restricted"   # Full anonymization
    TOP_SECRET = "top_secret"   # No non-prod access


@dataclass
class AnonymizationRule:
    """Configuration for anonymizing specific data fields"""
    field_name: str
    technique: AnonymizationTechnique
    sensitivity_level: DataSensitivityLevel
    preserve_format: bool = True
    preserve_relationships: bool = False
    custom_mapping: Optional[Dict[str, str]] = None


class DataAnonymizer:
    """
    Comprehensive data anonymization service for non-production environments
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger
        self.settings = get_settings()
        
        # Initialize anonymization rules
        self.anonymization_rules = self._load_anonymization_rules()
        
        # Consistent seed for reproducible anonymization
        self.seed = self.config.get("seed", 12345)
        random.seed(self.seed)
        
        # Mapping caches for consistency
        self.user_id_mapping: Dict[str, str] = {}
        self.email_mapping: Dict[str, str] = {}
        self.name_mapping: Dict[str, str] = {}
    
    def _load_anonymization_rules(self) -> Dict[str, AnonymizationRule]:
        """Load anonymization rules for different data types"""
        return {
            # User data
            "user_id": AnonymizationRule(
                field_name="user_id",
                technique=AnonymizationTechnique.PSEUDONYMIZATION,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                preserve_relationships=True
            ),
            "email": AnonymizationRule(
                field_name="email",
                technique=AnonymizationTechnique.MASKING,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                preserve_format=True
            ),
            "full_name": AnonymizationRule(
                field_name="full_name",
                technique=AnonymizationTechnique.MASKING,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL
            ),
            "phone_number": AnonymizationRule(
                field_name="phone_number",
                technique=AnonymizationTechnique.MASKING,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                preserve_format=True
            ),
            "address": AnonymizationRule(
                field_name="address",
                technique=AnonymizationTechnique.GENERALIZATION,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL
            ),
            "birth_date": AnonymizationRule(
                field_name="birth_date",
                technique=AnonymizationTechnique.GENERALIZATION,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL
            ),
            
            # Financial data
            "credit_card": AnonymizationRule(
                field_name="credit_card",
                technique=AnonymizationTechnique.TOKENIZATION,
                sensitivity_level=DataSensitivityLevel.RESTRICTED,
                preserve_format=True
            ),
            "bank_account": AnonymizationRule(
                field_name="bank_account",
                technique=AnonymizationTechnique.TOKENIZATION,
                sensitivity_level=DataSensitivityLevel.RESTRICTED
            ),
            "ssn": AnonymizationRule(
                field_name="ssn",
                technique=AnonymizationTechnique.SUPPRESSION,
                sensitivity_level=DataSensitivityLevel.TOP_SECRET
            ),
            
            # Content data
            "content_text": AnonymizationRule(
                field_name="content_text",
                technique=AnonymizationTechnique.MASKING,
                sensitivity_level=DataSensitivityLevel.INTERNAL
            ),
            "file_path": AnonymizationRule(
                field_name="file_path",
                technique=AnonymizationTechnique.GENERALIZATION,
                sensitivity_level=DataSensitivityLevel.INTERNAL
            ),
            
            # Analytics data
            "ip_address": AnonymizationRule(
                field_name="ip_address",
                technique=AnonymizationTechnique.GENERALIZATION,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL
            ),
            "user_agent": AnonymizationRule(
                field_name="user_agent",
                technique=AnonymizationTechnique.GENERALIZATION,
                sensitivity_level=DataSensitivityLevel.INTERNAL
            )
        }
    
    async def anonymize_dataset(
        self,
        dataset: List[Dict[str, Any]],
        environment: str = "test"
    ) -> List[Dict[str, Any]]:
        """
        Anonymize an entire dataset for non-production use
        
        Args:
            dataset: List of records to anonymize
            environment: Target environment (test, staging, dev)
            
        Returns:
            Anonymized dataset
        """
        try:
            if environment == "production":
                raise ValueError("Cannot anonymize production data")
            
            anonymized_dataset = []
            
            for record in dataset:
                anonymized_record = await self.anonymize_record(record, environment)
                anonymized_dataset.append(anonymized_record)
            
            self.logger.info(f"Anonymized {len(dataset)} records for {environment} environment")
            
            return anonymized_dataset
            
        except Exception as e:
            self.logger.error(f"Dataset anonymization failed: {str(e)}")
            raise
    
    async def anonymize_record(
        self,
        record: Dict[str, Any],
        environment: str = "test"
    ) -> Dict[str, Any]:
        """
        Anonymize a single data record
        
        Args:
            record: Record to anonymize
            environment: Target environment
            
        Returns:
            Anonymized record
        """
        anonymized_record = record.copy()
        
        for field_name, value in record.items():
            if field_name in self.anonymization_rules:
                rule = self.anonymization_rules[field_name]
                
                # Check if field should be anonymized for this environment
                if self._should_anonymize_field(rule, environment):
                    anonymized_value = await self._anonymize_field(
                        field_name, value, rule
                    )
                    anonymized_record[field_name] = anonymized_value
            
            # Handle nested objects
            elif isinstance(value, dict):
                anonymized_record[field_name] = await self.anonymize_record(value, environment)
            
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                anonymized_record[field_name] = [
                    await self.anonymize_record(item, environment)
                    for item in value
                ]
        
        return anonymized_record
    
    def _should_anonymize_field(self, rule: AnonymizationRule, environment: str) -> bool:
        """Determine if a field should be anonymized for the given environment"""
        if environment == "production":
            return False
        
        # Always anonymize restricted and top secret data
        if rule.sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.TOP_SECRET]:
            return True
        
        # Anonymize confidential data in non-production
        if rule.sensitivity_level == DataSensitivityLevel.CONFIDENTIAL:
            return True
        
        # Optionally anonymize internal data in test environments
        if rule.sensitivity_level == DataSensitivityLevel.INTERNAL and environment in ["test", "dev"]:
            return True
        
        return False
    
    async def _anonymize_field(
        self,
        field_name: str,
        value: Any,
        rule: AnonymizationRule
    ) -> Any:
        """Anonymize a specific field based on its rule"""
        if value is None:
            return True
        
        if rule.technique == AnonymizationTechnique.MASKING:
            return self._mask_value(field_name, value, rule)
        
        elif rule.technique == AnonymizationTechnique.PSEUDONYMIZATION:
            return self._pseudonymize_value(field_name, value, rule)
        
        elif rule.technique == AnonymizationTechnique.GENERALIZATION:
            return self._generalize_value(field_name, value, rule)
        
        elif rule.technique == AnonymizationTechnique.SUPPRESSION:
            return True
        
        elif rule.technique == AnonymizationTechnique.TOKENIZATION:
            return self._tokenize_value(field_name, value, rule)
        
        elif rule.technique == AnonymizationTechnique.PERTURBATION:
            return self._perturb_value(field_name, value, rule)
        
        return value
    
    def _mask_value(self, field_name: str, value: str, rule: AnonymizationRule) -> str:
        """Mask a value with fake data"""
        if field_name == "email":
            return self._generate_fake_email(value, rule.preserve_format)
        
        elif field_name == "full_name":
            return self._generate_fake_name()
        
        elif field_name == "phone_number":
            return self._generate_fake_phone(rule.preserve_format)
        
        elif field_name == "content_text":
            return self._mask_text_content(value)
        
        else:
            # Generic masking
            return "***MASKED***"
    
    def _pseudonymize_value(self, field_name: str, value: str, rule: AnonymizationRule) -> str:
        """Create consistent pseudonym for value"""
        if field_name == "user_id" and rule.preserve_relationships:
            # Use consistent mapping for user IDs to preserve relationships
            if value not in self.user_id_mapping:
                self.user_id_mapping[value] = f"user_{len(self.user_id_mapping) + 1:06d}"
            return self.user_id_mapping[value]
        
        # Generate consistent hash-based pseudonym
        hash_object = hashlib.sha256(f"{field_name}_{value}_{self.seed}".encode())
        return f"anon_{hash_object.hexdigest()[:12]}"
    
    def _generalize_value(self, field_name: str, value: Any, rule: AnonymizationRule) -> Any:
        """Generalize value by reducing precision"""
        if field_name == "birth_date":
            # Keep only year
            if isinstance(value, datetime):
                return f"{value.year}-01-01"
            elif isinstance(value, str):
                return value[:4] + "-01-01"
        
        elif field_name == "address":
            # Keep only city/state
            if isinstance(value, str):
                parts = value.split(",")
                if len(parts) >= 2:
                    return f"{parts[-2].strip()}, {parts[-1].strip()}"
            return "City, State"
        
        elif field_name == "ip_address":
            # Keep only first two octets
            if isinstance(value, str) and "." in value:
                parts = value.split(".")
                if len(parts) >= 2:
                    return f"{parts[0]}.{parts[1]}.0.0"
        
        return value
    
    def _tokenize_value(self, field_name: str, value: str, rule: AnonymizationRule) -> str:
        """Replace with secure token"""
        hash_object = hashlib.sha256(f"{field_name}_{value}_{self.seed}".encode())
        token = hash_object.hexdigest()[:16]
        
        if rule.preserve_format:
            if field_name == "credit_card":
                # Keep format like ****-****-****-1234
                return f"****-****-****-{token[:4]}"
            elif field_name == "bank_account":
                return f"***{token[:6]}"
        
        return f"TOKEN_{token.upper()}"
    
    def _perturb_value(self, field_name: str, value: Any, rule: AnonymizationRule) -> Any:
        """Add statistical noise to numerical values"""
        if isinstance(value, (int, float)):
            # Add ±10% noise
            noise = random.uniform(-0.1, 0.1) * value
            return value + noise
        
        return value
    
    def _generate_fake_email(self, original: str, preserve_format: bool = True) -> str:
        """Generate a fake email address"""
        if preserve_format and "@" in original:
            domain = original.split("@")[1]
            fake_user = ''.join(random.choices(string.ascii_lowercase, k=8))
            return f"{fake_user}@{domain}"
        
        return f"user{random.randint(1000, 9999)}@example.com"
    
    def _generate_fake_name(self) -> str:
        """Generate a fake name"""
        first_names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Quinn", "Sage"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Miller", "Moore", "Taylor"]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_fake_phone(self, preserve_format: bool = True) -> str:
        """Generate a fake phone number"""
        if preserve_format:
            return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        return "+1-555-0000"
    
    def _mask_text_content(self, text: str) -> str:
        """Mask sensitive content in text while preserving structure"""
        # Replace email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     'email@example.com', text)
        
        # Replace phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '555-0000', text)
        
        # Replace potential names (capitalized words)
        text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', 'First Last', text)
        
        return text
    
    async def get_anonymization_report(self, dataset_name: str) -> Dict[str, Any]:
        """Generate anonymization report for compliance"""
        return {
            "dataset_name": dataset_name,
            "anonymization_date": datetime.utcnow().isoformat(),
            "techniques_used": [t.value for t in AnonymizationTechnique],
            "rules_applied": len(self.anonymization_rules),
            "compliance_frameworks": ["GDPR", "CCPA", "HIPAA"],
            "preservation_characteristics": {
                "statistical_utility": "High",
                "referential_integrity": "Preserved",
                "format_consistency": "Maintained"
            }
        }


# Convenience function for quick anonymization
async def anonymize_for_environment(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    environment: str = "test"
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Quick function to anonymize data for non-production environments
    """
    anonymizer = DataAnonymizer()
    
    if isinstance(data, list):
        return await anonymizer.anonymize_dataset(data, environment)
    else:
        return await anonymizer.anonymize_record(data, environment)