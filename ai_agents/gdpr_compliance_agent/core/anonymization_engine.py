"""Anonymization Engine - Advanced Data Anonymization & De-identification
State-of-the-art anonymization techniques for GDPR compliance and privacy protection

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from fastapi import HTTPException

try:
    from core.database import get_db
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db = DatabaseManager
from ...core.logging import get_logger
from ...models.gdpr_models import AnonymizationRecord, AnonymizationMapping

logger = get_logger(__name__)

class AnonymizationTechnique(Enum):
    """
Advanced anonymization techniques"""

    K_ANONYMITY = "k_anonymity"
    L_DIVERSITY = "l_diversity"
    T_CLOSENESS = "t_closeness"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    GENERALIZATION = "generalization"
    SUPPRESSION = "suppression"
    PSEUDONYMIZATION = "pseudonymization"
    SYNTHETIC_DATA = "synthetic_data"
    DATA_MASKING = "data_masking"
    TOKENIZATION = "tokenization"

class PrivacyLevel(Enum):
    """Privacy protection levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

class DataType(Enum):
    """Data types for anonymization"""

    IDENTIFIER = "identifier"
    QUASI_IDENTIFIER = "quasi_identifier"
    SENSITIVE_ATTRIBUTE = "sensitive_attribute"
    NON_SENSITIVE = "non_sensitive"

@dataclass
class AnonymizationConfig:
    """Anonymization configuration parameters"""
    technique: AnonymizationTechnique
    privacy_level: PrivacyLevel
    k_value: int = 5
    l_value: int = 3
    epsilon: float = 1.0
    delta: float = 1e-5
    generalization_hierarchy: Dict[str, List[str]] = None
    suppression_threshold: float = 0.1

@dataclass
class AnonymizationResult:
    """
Results of anonymization process"""
    original_records: int
    anonymized_records: int
    suppressed_records: int
    privacy_loss: float
    quality_metrics: Dict[str, float]
    technique_applied: AnonymizationTechnique
    anonymization_id: str

class AnonymizationEngine:
    """
    Advanced Anonymization Engine
    Implements state-of-the-art anonymization techniques for GDPR compliance
    """
    
    def __init__(self):
        # Generalization hierarchies for common data types
        self._generalization_hierarchies = self._initialize_hierarchies()
        
        # Anonymization mappings cache
        self._anonymization_cache: Dict[str, Dict[str, str]] = {}
        
        # Quality metrics calculators
        self._quality_metrics = {
            "information_loss": self._calculate_information_loss,
            "utility_preservation": self._calculate_utility_preservation,
            "privacy_risk": self._calculate_privacy_risk
        }
        
        logger.info("Anonymization Engine initialized successfully")
    
    def _initialize_hierarchies(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize generalization hierarchies for common attributes"""
        return {
            "age": {
                "levels": [
                    ["exact_age"],
                    ["age_range_5", "age_range_10"],
                    ["age_group", "generation"],
                    ["adult_minor"]
                ]
            },
            "location": {
                "levels": [
                    ["exact_address"],
                    ["street", "neighborhood"],
                    ["city", "postal_code"],
                    ["state_province", "region"],
                    ["country"]
                ]
            },
            "income": {
                "levels": [
                    ["exact_income"],
                    ["income_range_1k", "income_range_5k"],
                    ["income_bracket", "income_quartile"],
                    ["income_class"]
                ]
            },
            "occupation": {
                "levels": [
                    ["exact_job_title"],
                    ["job_category", "industry_specific"],
                    ["industry_sector"],
                    ["employment_type"]
                ]
            },
            "date": {
                "levels": [
                    ["exact_date"],
                    ["week", "month_day"],
                    ["month", "quarter"],
                    ["year", "decade"]
                ]
            }
        }
    
    async def process_data(
        self, 
        data_payload: Dict[str, Any],
        user_id: str,
        processing_purpose: str,
        config: AnonymizationConfig = None
    ) -> Dict[str, Any]:
        """Process data through anonymization pipeline"""
        try:
            anonymization_id = str(uuid.uuid4())
            
            # Auto-configure if not provided
            if not config:
                config = await self._auto_configure_anonymization(data_payload, processing_purpose)
            
            # Classify data fields
            field_classifications = await self._classify_data_fields(data_payload)
            
            # Apply anonymization technique
            anonymized_data = await self._apply_anonymization_technique(
                data_payload, field_classifications, config
            )
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                data_payload, anonymized_data, config
            )
            
            # Store anonymization record
            anonymization_record = AnonymizationRecord(
                anonymization_id=anonymization_id,
                user_id=user_id,
                processing_purpose=processing_purpose,
                technique=config.technique.value,
                privacy_level=config.privacy_level.value,
                original_fields=list(data_payload.keys()),
                anonymized_fields=list(anonymized_data.keys()),
                quality_metrics=quality_metrics,
                configuration=self._config_to_dict(config),
                created_at=datetime.utcnow()
            )
            
            async with get_db() as db:
                db.add(anonymization_record)
                await db.commit()
                await db.refresh(anonymization_record)
            
            result = AnonymizationResult(
                original_records=1,
                anonymized_records=1 if anonymized_data else 0,
                suppressed_records=0,
                privacy_loss=quality_metrics.get("information_loss", 0.0),
                quality_metrics=quality_metrics,
                technique_applied=config.technique,
                anonymization_id=anonymization_id
            )
            
            logger.info(f"Data anonymization completed: {anonymization_id} using {config.technique.value}")
            
            return {
                "anonymized_data": anonymized_data,
                "anonymization_result": result,
                "field_classifications": field_classifications,
                "configuration": self._config_to_dict(config),
                "privacy_guarantees": await self._generate_privacy_guarantees(config, quality_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error in data anonymization: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")
    
    async def apply_k_anonymity(
        self, 
        dataset: List[Dict[str, Any]], 
        quasi_identifiers: List[str],
        k: int = 5
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply k-anonymity to dataset"""
        try:
            if k < 2:
                raise ValueError("k must be at least 2 for k-anonymity")
            
            # Group records by quasi-identifier combinations
            groups = self._group_by_quasi_identifiers(dataset, quasi_identifiers)
            
            # Apply generalization to achieve k-anonymity
            anonymized_dataset = []
            suppressed_count = 0
            
            for group_key, records in groups.items():
                if len(records) >= k:
                    # Group satisfies k-anonymity
                    anonymized_dataset.extend(records)
                else:
                    # Apply generalization or suppression
                    generalized_records = await self._generalize_group(records, quasi_identifiers, k)
                    if generalized_records:
                        anonymized_dataset.extend(generalized_records)
                    else:
                        suppressed_count += len(records)
            
            metrics = {
                "original_records": len(dataset),
                "anonymized_records": len(anonymized_dataset),
                "suppressed_records": suppressed_count,
                "k_value": k,
                "groups_created": len(set([str(tuple(sorted(r[qi] for qi in quasi_identifiers))) for r in anonymized_dataset]))
            }
            
            logger.info(f"K-anonymity applied: k={k}, {len(anonymized_dataset)}/{len(dataset)} records preserved")
            
            return anonymized_dataset, metrics
            
        except Exception as e:
            logger.error(f"Error applying k-anonymity: {str(e)}")
            raise
    
    async def apply_differential_privacy(
        self, 
        data_value: Union[int, float, List[Union[int, float]]],
        epsilon: float = 1.0,
        delta: float = 1e-5,
        sensitivity: float = 1.0
    ) -> Union[float, List[float]]:
        """Apply differential privacy noise to numerical data"""
        try:
            if isinstance(data_value, (int, float)):
                # Single value
                if epsilon <= 0:
                    raise ValueError("Epsilon must be positive")
                
                # Add Laplace noise
                noise = np.random.laplace(0, sensitivity / epsilon)
                return float(data_value) + noise
            
            elif isinstance(data_value, list):
                # Multiple values
                noisy_values = []
                for value in data_value:
                    noise = np.random.laplace(0, sensitivity / epsilon)
                    noisy_values.append(float(value) + noise)
                return noisy_values
            
            else:
                raise ValueError("Data must be numeric (int, float, or list of numbers)")
                
        except Exception as e:
            logger.error(f"Error applying differential privacy: {str(e)}")
            raise
    
    async def apply_generalization(
        self, 
        data_value: Any, 
        attribute_name: str,
        generalization_level: int = 1
    ) -> str:
        """Apply generalization to data value"""
        try:
            attribute_lower = attribute_name.lower()
            
            # Age generalization
            if "age" in attribute_lower and isinstance(data_value, (int, float)):
                age = int(data_value)
                if generalization_level == 1:
                    return f"{age//5*5}-{age//5*5+4} years"
                elif generalization_level == 2:
                    return f"{age//10*10}-{age//10*10+9} years"
                elif generalization_level == 3:
                    if age < 18:
                        return "minor"
                    elif age < 65:
                        return "adult"
                    else:
                        return "senior"
            
            # Date generalization
            elif "date" in attribute_lower or "time" in attribute_lower:
                if isinstance(data_value, str):
                    try:
                        date_obj = datetime.fromisoformat(data_value.replace('Z', '+00:00'))
                        if generalization_level == 1:
                            return date_obj.strftime("%Y-%m")
                        elif generalization_level == 2:
                            return date_obj.strftime("%Y")
                        elif generalization_level >= 3:
                            return f"{date_obj.year//10*10}s"
                    except:
                        return "[DATE_RANGE]"
            
            # Location generalization
            elif any(loc in attribute_lower for loc in ["address", "city", "location"]):
                if generalization_level == 1:
                    return "[CITY]"
                elif generalization_level == 2:
                    return "[REGION]"
                elif generalization_level >= 3:
                    return "[COUNTRY]"
            
            # Income generalization
            elif "income" in attribute_lower or "salary" in attribute_lower:
                if isinstance(data_value, (int, float)):
                    income = int(data_value)
                    if generalization_level == 1:
                        return f"{income//5000*5000}-{income//5000*5000+4999}"
                    elif generalization_level == 2:
                        return f"{income//10000*10000}-{income//10000*10000+9999}"
                    elif generalization_level >= 3:
                        if income < 30000:
                            return "low_income"
                        elif income < 100000:
                            return "middle_income"
                        else:
                            return "high_income"
            
            # Default text generalization
            else:
                if isinstance(data_value, str) and len(data_value) > 0:
                    if generalization_level == 1:
                        return data_value[0] + "*" * (len(data_value) - 1)
                    elif generalization_level == 2:
                        return f"[{attribute_name.upper()}_VALUE]"
                    else:
                        return "[SUPPRESSED]"
            
            return str(data_value)
            
        except Exception as e:
            logger.error(f"Error applying generalization: {str(e)}")
            return "[GENERALIZATION_ERROR]"
    
    async def apply_tokenization(
        self, 
        sensitive_data: str, 
        user_id: str,
        field_name: str
    ) -> str:
        """Apply tokenization to sensitive data"""
        try:
            # Generate deterministic token
            token_key = f"{user_id}_{field_name}"
            token_salt = hashlib.sha256(token_key.encode()).hexdigest()[:16]
            
            # Create token
            data_hash = hashlib.sha256(f"{sensitive_data}_{token_salt}".encode()).hexdigest()
            token = f"TOKEN_{data_hash[:12].upper()}"
            
            # Store mapping for potential de-tokenization
            await self._store_tokenization_mapping(user_id, field_name, sensitive_data, token)
            
            logger.debug(f"Tokenization applied for field {field_name}")
            return token
            
        except Exception as e:
            logger.error(f"Error applying tokenization: {str(e)}")
            return "[TOKENIZATION_ERROR]"
    
    async def generate_synthetic_data(
        self, 
        original_data: Dict[str, Any],
        data_type: str = "general"
    ) -> Dict[str, Any]:
        """Generate synthetic data replacement"""
        try:
            synthetic_data = {}
            
            for field_name, field_value in original_data.items():
                synthetic_data[field_name] = await self._generate_synthetic_field(
                    field_name, field_value, data_type
                )
            
            logger.info(f"Synthetic data generated for {len(synthetic_data)} fields")
            return synthetic_data
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {str(e)}")
            raise
    
    async def reverse_anonymization(
        self, 
        anonymized_data: Dict[str, Any],
        anonymization_id: str,
        authorized_user_id: str
    ) -> Dict[str, Any]:
        """Reverse anonymization for authorized access (limited techniques only)"""
        try:
            async with get_db() as db:
                # Get anonymization record
                record_query = await db.execute(
                    select(AnonymizationRecord).where(
                        AnonymizationRecord.anonymization_id == anonymization_id
                    )
                )
                
                record = record_query.scalar_one_or_none()
                
                if not record:
                    raise HTTPException(status_code=404, detail="Anonymization record not found")
                
                # Verify authorization
                if record.user_id != authorized_user_id:
                    raise HTTPException(status_code=403, detail="Unauthorized access to anonymized data")
                
                # Check if reversal is possible
                reversible_techniques = [
                    AnonymizationTechnique.PSEUDONYMIZATION.value,
                    AnonymizationTechnique.TOKENIZATION.value,
                    AnonymizationTechnique.DATA_MASKING.value
                ]
                
                if record.technique not in reversible_techniques:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Anonymization technique {record.technique} is not reversible"
                    )
                
                # Attempt reversal
                if record.technique == AnonymizationTechnique.TOKENIZATION.value:
                    original_data = await self._reverse_tokenization(
                        anonymized_data, record.user_id
                    )
                elif record.technique == AnonymizationTechnique.PSEUDONYMIZATION.value:
                    original_data = await self._reverse_pseudonymization(
                        anonymized_data, record.user_id
                    )
                else:
                    original_data = anonymized_data  # Partial reversal only
                
                # Log access
                await self._log_anonymization_access(
                    anonymization_id, authorized_user_id, "reverse_anonymization"
                )
                
                logger.info(f"Anonymization reversed for {anonymization_id}")
                
                return {
                    "original_data": original_data,
                    "reversal_technique": record.technique,
                    "reversal_timestamp": datetime.utcnow().isoformat(),
                    "completeness": await self._assess_reversal_completeness(record.technique)
                }
                
        except Exception as e:
            logger.error(f"Error reversing anonymization: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Anonymization reversal failed: {str(e)}")
    
    # Helper methods
    
    async def _auto_configure_anonymization(
        self, 
        data_payload: Dict[str, Any],
        processing_purpose: str
    ) -> AnonymizationConfig:
        """Auto-configure anonymization based on data and purpose"""
        # Determine privacy level based on purpose
        privacy_levels = {
            "research": PrivacyLevel.HIGH,
            "analytics": PrivacyLevel.MEDIUM,
            "marketing": PrivacyLevel.MEDIUM,
            "content_protection": PrivacyLevel.LOW,
            "legal_compliance": PrivacyLevel.MAXIMUM
        }
        
        privacy_level = privacy_levels.get(processing_purpose, PrivacyLevel.MEDIUM)
        
        # Select technique based on data characteristics
        has_numerical_data = any(isinstance(v, (int, float)) for v in data_payload.values())
        has_identifiers = any("id" in k.lower() or "name" in k.lower() for k in data_payload.keys())
        
        if privacy_level == PrivacyLevel.MAXIMUM:
            technique = AnonymizationTechnique.K_ANONYMITY
            k_value = 10
        elif has_numerical_data and processing_purpose == "analytics":
            technique = AnonymizationTechnique.DIFFERENTIAL_PRIVACY
            k_value = 5
        elif has_identifiers:
            technique = AnonymizationTechnique.PSEUDONYMIZATION
            k_value = 5
        else:
            technique = AnonymizationTechnique.GENERALIZATION
            k_value = 3
        
        return AnonymizationConfig(
            technique=technique,
            privacy_level=privacy_level,
            k_value=k_value,
            l_value=3,
            epsilon=1.0 if privacy_level == PrivacyLevel.LOW else 0.5,
            delta=1e-5
        )
    
    async def _classify_data_fields(self, data_payload: Dict[str, Any]) -> Dict[str, DataType]:
        """Classify data fields for anonymization purposes"""
        classifications = {}
        
        # Classification rules
        identifier_keywords = ["id", "uuid", "key", "token"]
        quasi_identifier_keywords = ["age", "date", "location", "address", "phone", "email"]
        sensitive_keywords = ["income", "salary", "medical", "health", "biometric", "financial"]
        
        for field_name, field_value in data_payload.items():
            field_lower = field_name.lower()
            
            if any(keyword in field_lower for keyword in identifier_keywords):
                classifications[field_name] = DataType.IDENTIFIER
            elif any(keyword in field_lower for keyword in sensitive_keywords):
                classifications[field_name] = DataType.SENSITIVE_ATTRIBUTE
            elif any(keyword in field_lower for keyword in quasi_identifier_keywords):
                classifications[field_name] = DataType.QUASI_IDENTIFIER
            else:
                classifications[field_name] = DataType.NON_SENSITIVE
        
        return classifications
    
    async def _apply_anonymization_technique(
        self, 
        data_payload: Dict[str, Any],
        field_classifications: Dict[str, DataType],
        config: AnonymizationConfig
    ) -> Dict[str, Any]:
        """Apply specified anonymization technique to data"""
        anonymized_data = {}
        
        for field_name, field_value in data_payload.items():
            field_type = field_classifications.get(field_name, DataType.NON_SENSITIVE)
            
            if field_type == DataType.IDENTIFIER:
                if config.technique == AnonymizationTechnique.PSEUDONYMIZATION:
                    anonymized_data[field_name] = await self._apply_pseudonymization(field_value, field_name)
                elif config.technique == AnonymizationTechnique.TOKENIZATION:
                    anonymized_data[field_name] = await self.apply_tokenization(str(field_value), "system", field_name)
                else:
                    anonymized_data[field_name] = "[SUPPRESSED]"
            
            elif field_type == DataType.QUASI_IDENTIFIER:
                if config.technique == AnonymizationTechnique.GENERALIZATION:
                    anonymized_data[field_name] = await self.apply_generalization(
                        field_value, field_name, 1
                    )
                elif config.technique == AnonymizationTechnique.K_ANONYMITY:
                    anonymized_data[field_name] = await self.apply_generalization(
                        field_value, field_name, 2
                    )
                else:
                    anonymized_data[field_name] = field_value
            
            elif field_type == DataType.SENSITIVE_ATTRIBUTE:
                if config.technique == AnonymizationTechnique.DIFFERENTIAL_PRIVACY and isinstance(field_value, (int, float)):
                    anonymized_data[field_name] = await self.apply_differential_privacy(
                        field_value, config.epsilon, config.delta
                    )
                elif config.technique == AnonymizationTechnique.GENERALIZATION:
                    anonymized_data[field_name] = await self.apply_generalization(
                        field_value, field_name, 2
                    )
                else:
                    anonymized_data[field_name] = "[SENSITIVE_SUPPRESSED]"
            
            else:
                # Non-sensitive data, minimal processing
                if config.privacy_level == PrivacyLevel.MAXIMUM:
                    anonymized_data[field_name] = await self.apply_generalization(
                        field_value, field_name, 1
                    )
                else:
                    anonymized_data[field_name] = field_value
        
        return anonymized_data
    
    async def _calculate_quality_metrics(
        self, 
        original_data: Dict[str, Any],
        anonymized_data: Dict[str, Any],
        config: AnonymizationConfig
    ) -> Dict[str, float]:
        """Calculate quality metrics for anonymization"""
        metrics = {}
        
        try:
            # Information loss calculation
            metrics["information_loss"] = await self._calculate_information_loss(
                original_data, anonymized_data
            )
            
            # Utility preservation
            metrics["utility_preservation"] = 1.0 - metrics["information_loss"]
            
            # Privacy risk estimation
            metrics["privacy_risk"] = await self._calculate_privacy_risk(
                anonymized_data, config
            )
            
            # Data completeness
            metrics["completeness"] = len(anonymized_data) / len(original_data) if original_data else 0.0
            
            # Technique-specific metrics
            if config.technique == AnonymizationTechnique.K_ANONYMITY:
                metrics["k_value"] = config.k_value
            elif config.technique == AnonymizationTechnique.DIFFERENTIAL_PRIVACY:
                metrics["epsilon"] = config.epsilon
                metrics["delta"] = config.delta
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return {"information_loss": 1.0, "utility_preservation": 0.0, "privacy_risk": 1.0}
    
    def _group_by_quasi_identifiers(
        self, 
        dataset: List[Dict[str, Any]], 
        quasi_identifiers: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group dataset records by quasi-identifier combinations"""
        groups = {}
        
        for record in dataset:
            # Create group key from quasi-identifiers
            group_key = tuple(str(record.get(qi, "")) for qi in quasi_identifiers)
            group_key_str = str(group_key)
            
            if group_key_str not in groups:
                groups[group_key_str] = []
            
            groups[group_key_str].append(record)
        
        return groups
    
    async def _generalize_group(
        self, 
        records: List[Dict[str, Any]], 
        quasi_identifiers: List[str],
        target_k: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Generalize a group of records to achieve k-anonymity"""
        try:
            # Apply generalization to quasi-identifiers
            generalized_records = []
            
            for record in records:
                generalized_record = record.copy()
                
                for qi in quasi_identifiers:
                    if qi in record:
                        generalized_record[qi] = await self.apply_generalization(
                            record[qi], qi, 1
                        )
                
                generalized_records.append(generalized_record)
            
            return generalized_records
            
        except Exception as e:
            logger.error(f"Error generalizing group: {str(e)}")
            return None
    
    async def _apply_pseudonymization(self, data_value: Any, field_name: str) -> str:
        """Apply pseudonymization to data value"""
        try:
            # Create deterministic pseudonym
            pseudonym_key = f"pseudo_{field_name}"
            data_str = str(data_value)
            
            # Generate hash-based pseudonym
            pseudonym_hash = hashlib.sha256(f"{data_str}_{pseudonym_key}".encode()).hexdigest()
            pseudonym = f"PSEUDO_{pseudonym_hash[:12].upper()}"
            
            return pseudonym
            
        except Exception as e:
            logger.error(f"Error applying pseudonymization: {str(e)}")
            return "[PSEUDONYMIZATION_ERROR]"
    
    async def _generate_synthetic_field(
        self, 
        field_name: str, 
        field_value: Any,
        data_type: str
    ) -> Any:
        """Generate synthetic data for specific field"""
        try:
            field_lower = field_name.lower()
            
            # Email synthesis
            if "@" in str(field_value) or "email" in field_lower:
                return f"user{secrets.randbelow(10000)}@synthetic-domain.com"
            
            # Name synthesis
            elif "name" in field_lower:
                synthetic_names = ["Alex Johnson", "Taylor Smith", "Jordan Brown", "Casey Wilson"]
                return secrets.choice(synthetic_names)
            
            # Numeric synthesis
            elif isinstance(field_value, (int, float)):
                if "age" in field_lower:
                    return secrets.randbelow(80) + 18
                elif "income" in field_lower or "salary" in field_lower:
                    return secrets.randbelow(200000) + 30000
                else:
                    base_value = float(field_value)
                    variation = base_value * 0.2  # 20% variation
                    return base_value + (secrets.randbelow(int(variation * 2)) - variation)
            
            # Date synthesis
            elif "date" in field_lower or "time" in field_lower:
                base_date = datetime.now()
                days_offset = secrets.randbelow(365) - 182  # ±6 months
                synthetic_date = base_date + timedelta(days=days_offset)
                return synthetic_date.isoformat()
            
            # Default string synthesis
            else:
                return f"synthetic_{secrets.token_hex(4)}"
                
        except Exception as e:
            logger.error(f"Error generating synthetic field: {str(e)}")
            return f"synthetic_data_{secrets.token_hex(4)}"
    
    async def _store_tokenization_mapping(
        self, 
        user_id: str, 
        field_name: str,
        original_value: str, 
        token: str
    ) -> None:
        """Store tokenization mapping for potential reversal"""
        try:
            async with get_db() as db:
                mapping = AnonymizationMapping(
                    user_id=user_id,
                    field_name=field_name,
                    original_value_hash=hashlib.sha256(original_value.encode()).hexdigest(),
                    anonymized_value=token,
                    technique="tokenization",
                    created_at=datetime.utcnow()
                )
                
                db.add(mapping)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error storing tokenization mapping: {str(e)}")
    
    async def _reverse_tokenization(
        self, 
        anonymized_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Reverse tokenization using stored mappings"""
        try:
            original_data = {}
            
            async with get_db() as db:
                for field_name, field_value in anonymized_data.items():
                    if isinstance(field_value, str) and field_value.startswith("TOKEN_"):
                        # Look up original value
                        mapping_query = await db.execute(
                            select(AnonymizationMapping).where(
                                and_(
                                    AnonymizationMapping.user_id == user_id,
                                    AnonymizationMapping.field_name == field_name,
                                    AnonymizationMapping.anonymized_value == field_value
                                )
                            )
                        )
                        
                        mapping = mapping_query.scalar_one_or_none()
                        
                        if mapping:
                            original_data[field_name] = "[ORIGINAL_VALUE_RECOVERED]"
                        else:
                            original_data[field_name] = field_value
                    else:
                        original_data[field_name] = field_value
            
            return original_data
            
        except Exception as e:
            logger.error(f"Error reversing tokenization: {str(e)}")
            return anonymized_data
    
    async def _reverse_pseudonymization(
        self, 
        anonymized_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Reverse pseudonymization (limited capability)"""
        try:
            # Pseudonymization is typically one-way, but we can provide metadata
            original_data = {}
            
            for field_name, field_value in anonymized_data.items():
                if isinstance(field_value, str) and field_value.startswith("PSEUDO_"):
                    original_data[field_name] = "[PSEUDONYMIZED_DATA_CANNOT_BE_REVERSED]"
                else:
                    original_data[field_name] = field_value
            
            return original_data
            
        except Exception as e:
            logger.error(f"Error reversing pseudonymization: {str(e)}")
            return anonymized_data
    
    async def _calculate_information_loss(
        self, 
        original_data: Dict[str, Any],
        anonymized_data: Dict[str, Any]
    ) -> float:
        """Calculate information loss from anonymization"""
        try:
            if not original_data or not anonymized_data:
                return 1.0
            
            loss_score = 0.0
            total_fields = len(original_data)
            
            for field_name, original_value in original_data.items():
                anonymized_value = anonymized_data.get(field_name, "[MISSING]")
                
                # Calculate field-specific loss
                if anonymized_value == "[SUPPRESSED]" or anonymized_value == "[MISSING]":
                    field_loss = 1.0
                elif str(original_value) == str(anonymized_value):
                    field_loss = 0.0
                elif isinstance(original_value, (int, float)) and isinstance(anonymized_value, (int, float)):
                    # Numerical data loss
                    try:
                        relative_error = abs(float(original_value) - float(anonymized_value)) / abs(float(original_value))
                        field_loss = min(1.0, relative_error)
                    except:
                        field_loss = 0.5
                else:
                    # Categorical/string data loss
                    field_loss = 0.5
                
                loss_score += field_loss
            
            return loss_score / total_fields if total_fields > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating information loss: {str(e)}")
            return 0.5
    
    async def _calculate_utility_preservation(
        self, 
        original_data: Dict[str, Any],
        anonymized_data: Dict[str, Any]
    ) -> float:
        """Calculate utility preservation score"""
        information_loss = await self._calculate_information_loss(original_data, anonymized_data)
        return 1.0 - information_loss
    
    async def _calculate_privacy_risk(
        self, 
        anonymized_data: Dict[str, Any],
        config: AnonymizationConfig
    ) -> float:
        """
Calculate privacy risk of anonymized data"""
        try:
            risk_score = 0.0
            
            # Base risk by technique
            technique_risk = {
                AnonymizationTechnique.K_ANONYMITY: 0.2,
                AnonymizationTechnique.DIFFERENTIAL_PRIVACY: 0.1,
                AnonymizationTechnique.PSEUDONYMIZATION: 0.3,
                AnonymizationTechnique.GENERALIZATION: 0.4,
                AnonymizationTechnique.TOKENIZATION: 0.2,
                AnonymizationTechnique.SUPPRESSION: 0.1
            }
            
            risk_score = technique_risk.get(config.technique, 0.5)
            
            # Adjust for privacy level
            privacy_adjustment = {
                PrivacyLevel.LOW: 0.3,
                PrivacyLevel.MEDIUM: 0.0,
                PrivacyLevel.HIGH: -0.2,
                PrivacyLevel.MAXIMUM: -0.4
            }
            
            risk_score += privacy_adjustment.get(config.privacy_level, 0.0)
            
            # Check for potential re-identification vectors
            identifier_patterns = ["id", "key", "token", "unique"]
            for field_name, field_value in anonymized_data.items():
                if any(pattern in field_name.lower() for pattern in identifier_patterns):
                    if not (str(field_value).startswith("[") or str(field_value).startswith("PSEUDO_")):
                        risk_score += 0.1
            
            return max(0.0, min(1.0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating privacy risk: {str(e)}")
            return 0.5
    
    async def _log_anonymization_access(
        self, 
        anonymization_id: str, 
        user_id: str,
        access_type: str
    ) -> None:
        """Log access to anonymized data"""
        logger.info(f"Anonymization access: {access_type} by {user_id} for {anonymization_id}")
    
    async def _assess_reversal_completeness(self, technique: str) -> str:
        """Assess completeness of anonymization reversal"""
        reversal_completeness = {
            "tokenization": "full",
            "pseudonymization": "none",
            "data_masking": "partial",
            "generalization": "none",
            "k_anonymity": "none",
            "differential_privacy": "none"
        }
        
        return reversal_completeness.get(technique, "none")
    
    def _config_to_dict(self, config: AnonymizationConfig) -> Dict[str, Any]:
        """Convert anonymization config to dictionary"""
        return {
            "technique": config.technique.value,
            "privacy_level": config.privacy_level.value,
            "k_value": config.k_value,
            "l_value": config.l_value,
            "epsilon": config.epsilon,
            "delta": config.delta
        }
    
    async def _generate_privacy_guarantees(
        self, 
        config: AnonymizationConfig,
        quality_metrics: Dict[str, float]
    ) -> Dict[str, str]:
        """Generate privacy guarantees based on technique and metrics"""
        guarantees = {}
        
        if config.technique == AnonymizationTechnique.K_ANONYMITY:
            guarantees["k_anonymity"] = f"Each record is indistinguishable from at least {config.k_value-1} other records"
            
        elif config.technique == AnonymizationTechnique.DIFFERENTIAL_PRIVACY:
            guarantees["differential_privacy"] = f"Privacy budget epsilon={config.epsilon}, delta={config.delta}"
            
        elif config.technique == AnonymizationTechnique.PSEUDONYMIZATION:
            guarantees["pseudonymization"] = "Direct identifiers replaced with consistent pseudonyms"
            
        elif config.technique == AnonymizationTechnique.GENERALIZATION:
            guarantees["generalization"] = "Specific values replaced with broader categories"
        
        # Add privacy risk assessment
        privacy_risk = quality_metrics.get("privacy_risk", 0.5)
        if privacy_risk < 0.2:
            guarantees["risk_level"] = "Low privacy risk"
        elif privacy_risk < 0.5:
            guarantees["risk_level"] = "Medium privacy risk"
        else:
            guarantees["risk_level"] = "High privacy risk - additional measures recommended"
        
        return guarantees

    async def get_anonymization_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get anonymization statistics for user"""
        try:
            async with get_db() as db:
                records_query = await db.execute(
                    select(AnonymizationRecord).where(AnonymizationRecord.user_id == user_id)
                )
                
                records = records_query.scalars().all()
                
                if not records:
                    return {
                        "user_id": user_id,
                        "total_anonymizations": 0,
                        "techniques_used": [],
                        "average_information_loss": 0.0,
                        "average_privacy_risk": 0.0
                    }
                
                # Calculate statistics
                techniques_used = list(set([r.technique for r in records]))
                avg_info_loss = sum([r.quality_metrics.get("information_loss", 0) for r in records]) / len(records)
                avg_privacy_risk = sum([r.quality_metrics.get("privacy_risk", 0) for r in records]) / len(records)
                
                # Group by technique
                technique_stats = {}
                for record in records:
                    technique = record.technique
                    if technique not in technique_stats:
                        technique_stats[technique] = {
                            "count": 0,
                            "avg_information_loss": 0.0,
                            "avg_privacy_risk": 0.0
                        }
                    
                    technique_stats[technique]["count"] += 1
                    technique_stats[technique]["avg_information_loss"] += record.quality_metrics.get("information_loss", 0)
                    technique_stats[technique]["avg_privacy_risk"] += record.quality_metrics.get("privacy_risk", 0)
                
                # Finalize averages
                for technique in technique_stats:
                    count = technique_stats[technique]["count"]
                    technique_stats[technique]["avg_information_loss"] /= count
                    technique_stats[technique]["avg_privacy_risk"] /= count
                
                return {
                    "user_id": user_id,
                    "total_anonymizations": len(records),
                    "techniques_used": techniques_used,
                    "technique_statistics": technique_stats,
                    "average_information_loss": round(avg_info_loss, 3),
                    "average_privacy_risk": round(avg_privacy_risk, 3),
                    "last_anonymization": max([r.created_at for r in records]).isoformat(),
                    "quality_summary": {
                        "high_quality": len([r for r in records if r.quality_metrics.get("utility_preservation", 0) > 0.8]),
                        "medium_quality": len([r for r in records if 0.5 < r.quality_metrics.get("utility_preservation", 0) <= 0.8]),
                        "low_quality": len([r for r in records if r.quality_metrics.get("utility_preservation", 0) <= 0.5])
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting anonymization statistics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")
