"""Database Data Masking Engine

Enterprise-grade data masking and anonymization system for protecting sensitive
information in non-production environments and compliance with privacy regulations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced data masking architecture
- ML Engineer: AI-driven data anonymization
- DBA: Database masking optimization
- Security Expert: Enterprise data protection
- Microservices: Distributed masking services
- Audio Engineer: Audio data protection
- DevOps: Secure masking infrastructure
- IA Prompt Engineer: AI masking algorithms

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""
import asyncio
import logging
import json
import time
import hashlib
import random
import string
import re
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid
import secrets
from faker import Faker
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class MaskingTechnique(Enum):
    """Data masking techniques"""
    REDACTION = "redaction"  # Replace with asterisks or X's
    SUBSTITUTION = "substitution"  # Replace with realistic fake data
    SHUFFLING = "shuffling"  # Randomize order within column
    ENCRYPTION = "encryption"  # Encrypt with key
    HASHING = "hashing"  # One-way hash
    TOKENIZATION = "tokenization"  # Replace with tokens
    NULL_REPLACEMENT = "null_replacement"  # Replace with NULL values
    PARTIAL_MASKING = "partial_masking"  # Mask part of the value
    VARIANCE = "variance"  # Add statistical variance
    AGGREGATION = "aggregation"  # Group and aggregate data


class DataType(Enum):
    """Supported data types for masking"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    IP_ADDRESS = "ip_address"
    FINANCIAL = "financial"
    CUSTOM = "custom"
    TEXT = "text"
    NUMERIC = "numeric"
    DATE = "date"
    BOOLEAN = "boolean"


class SensitivityLevel(Enum):
    """Data sensitivity levels"""
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4
    TOP_SECRET = 5


@dataclass
class MaskingRule:
    """Data masking rule definition"""
    rule_id: str
    table_name: str
    column_name: str
    data_type: DataType
    sensitivity_level: SensitivityLevel
    masking_technique: MaskingTechnique
    preserve_format: bool = True
    preserve_length: bool = True
    preserve_null: bool = True
    custom_pattern: Optional[str] = None
    replacement_value: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MaskingJob:
    """Data masking job definition"""
    job_id: str
    name: str
    description: str
    source_database: str
    target_database: str
    masking_rules: List[MaskingRule]
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    progress: float = 0.0
    error_message: Optional[str] = None
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MaskingResult:
    """Data masking operation result"""
    job_id: str
    rule_id: str
    table_name: str
    column_name: str
    records_processed: int
    records_masked: int
    execution_time: float
    technique_used: MaskingTechnique
    quality_score: float
    errors: List[str] = field(default_factory=list)


class DataMasker(ABC):
    """Abstract data masker interface"""
    
    @property
    @abstractmethod
    def supported_data_types(self) -> List[DataType]:
        """List of supported data types"""
        pass
    
    @property
    @abstractmethod
    def technique(self) -> MaskingTechnique:
        """Masking technique this masker implements"""
        pass
    
    @abstractmethod
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask a single value according to the rule"""
        pass
    
    @abstractmethod
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate if rule is compatible with this masker"""
        pass


class RedactionMasker(DataMasker):
    """Redaction-based data masker"""
    
    @property
    def supported_data_types(self) -> List[DataType]:
        return list(DataType)  # Supports all data types
    
    @property
    def technique(self) -> MaskingTechnique:
        return MaskingTechnique.REDACTION
    
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask value using redaction technique"""
        if value is None and rule.preserve_null:
            return None
        
        if not isinstance(value, str):
            value = str(value)
        
        # Determine replacement character
        replacement_char = rule.replacement_value or "*"
        
        if rule.data_type == DataType.EMAIL:
            return await self._mask_email(value, replacement_char, rule)
        elif rule.data_type == DataType.PHONE:
            return await self._mask_phone(value, replacement_char, rule)
        elif rule.data_type == DataType.SSN:
            return await self._mask_ssn(value, replacement_char, rule)
        elif rule.data_type == DataType.CREDIT_CARD:
            return await self._mask_credit_card(value, replacement_char, rule)
        else:
            return await self._mask_generic(value, replacement_char, rule)
    
    async def _mask_email(self, email: str, replacement_char: str, rule: MaskingRule) -> str:
        """Mask email address"""
        if "@" in email:
            local, domain = email.split("@", 1)
            # Keep first and last character of local part
            if len(local) > 2:
                masked_local = local[0] + replacement_char * (len(local) - 2) + local[-1]
            else:
                masked_local = replacement_char * len(local)
            return f"{masked_local}@{domain}"
        else:
            return replacement_char * len(email)
    
    async def _mask_phone(self, phone: str, replacement_char: str, rule: MaskingRule) -> str:
        """Mask phone number"""
        # Keep format but mask digits
        masked = ""
        for char in phone:
            if char.isdigit():
                masked += replacement_char
            else:
                masked += char
        return masked
    
    async def _mask_ssn(self, ssn: str, replacement_char: str, rule: MaskingRule) -> str:
        """Mask Social Security Number"""
        # Typical format: XXX-XX-1234 (keep last 4 digits)
        cleaned = re.sub(r'\D', '', ssn)
        if len(cleaned) >= 4:
            masked_part = replacement_char * (len(cleaned) - 4)
            visible_part = cleaned[-4:]
            result = masked_part + visible_part
        else:
            result = replacement_char * len(cleaned)
        
        # Restore original formatting
        if "-" in ssn and len(result) == 9:
            return f"{result[:3]}-{result[3:5]}-{result[5:]}"
        return result
    
    async def _mask_credit_card(self, card: str, replacement_char: str, rule: MaskingRule) -> str:
        """Mask credit card number"""
        # Keep last 4 digits
        cleaned = re.sub(r'\D', '', card)
        if len(cleaned) >= 4:
            masked_part = replacement_char * (len(cleaned) - 4)
            visible_part = cleaned[-4:]
            result = masked_part + visible_part
        else:
            result = replacement_char * len(cleaned)
        
        # Restore spacing if present
        if " " in card and len(result) >= 12:
            return f"{result[:4]} {result[4:8]} {result[8:12]} {result[12:]}"
        return result
    
    async def _mask_generic(self, value: str, replacement_char: str, rule: MaskingRule) -> str:
        """Generic masking for text"""
        if rule.custom_pattern:
            # Apply custom pattern masking
            pattern = rule.custom_pattern
            # Simple pattern: 'show_first_2' -> show first 2 chars
            if pattern.startswith("show_first_"):
                try:
                    show_count = int(pattern.split("_")[-1])
                    if len(value) > show_count:
                        return value[:show_count] + replacement_char * (len(value) - show_count)
                except ValueError:
                    pass
            elif pattern.startswith("show_last_"):
                try:
                    show_count = int(pattern.split("_")[-1])
                    if len(value) > show_count:
                        return replacement_char * (len(value) - show_count) + value[-show_count:]
                except ValueError:
                    pass
        
        # Default: mask entire value
        if rule.preserve_length:
            return replacement_char * len(value)
        else:
            return replacement_char * 8  # Fixed length
    
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate redaction rule"""
        return rule.masking_technique == self.technique


class SubstitutionMasker(DataMasker):
    """Substitution-based data masker using realistic fake data"""
    
    def __init__(self, locale: str = "en_US"):
        self.faker = Faker(locale)
        self.faker.seed_instance(42)  # For reproducible results
    
    @property
    def supported_data_types(self) -> List[DataType]:
        return [
            DataType.EMAIL, DataType.PHONE, DataType.NAME, 
            DataType.ADDRESS, DataType.DATE_OF_BIRTH, DataType.TEXT
        ]
    
    @property
    def technique(self) -> MaskingTechnique:
        return MaskingTechnique.SUBSTITUTION
    
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask value using substitution technique"""
        if value is None and rule.preserve_null:
            return None
        
        # Generate realistic fake data based on data type
        if rule.data_type == DataType.EMAIL:
            return self.faker.email()
        elif rule.data_type == DataType.PHONE:
            return self.faker.phone_number()
        elif rule.data_type == DataType.NAME:
            return self.faker.name()
        elif rule.data_type == DataType.ADDRESS:
            return self.faker.address()
        elif rule.data_type == DataType.DATE_OF_BIRTH:
            return self.faker.date_of_birth().strftime("%Y-%m-%d")
        elif rule.data_type == DataType.TEXT:
            # Generate text of similar length
            original_length = len(str(value)) if value else 10
            return self.faker.text(max_nb_chars=original_length)
        else:
            return str(value)  # Fallback
    
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate substitution rule"""
        return (rule.masking_technique == self.technique and 
                rule.data_type in self.supported_data_types)


class EncryptionMasker(DataMasker):
    """Encryption-based data masker"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or secrets.token_hex(32)
    
    @property
    def supported_data_types(self) -> List[DataType]:
        return list(DataType)  # Supports all data types
    
    @property
    def technique(self) -> MaskingTechnique:
        return MaskingTechnique.ENCRYPTION
    
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask value using encryption"""
        if value is None and rule.preserve_null:
            return None
        
        # Simple encryption using hash (for demo purposes)
        # In production, use proper encryption like AES
        value_str = str(value)
        combined = f"{self.encryption_key}:{value_str}"
        encrypted = hashlib.sha256(combined.encode()).hexdigest()
        
        if rule.preserve_length and len(value_str) < len(encrypted):
            return encrypted[:len(value_str)]
        
        return encrypted
    
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate encryption rule"""
        return rule.masking_technique == self.technique


class ShufflingMasker(DataMasker):
    """Shuffling-based data masker"""
    
    def __init__(self):
        self.column_values: Dict[str, List[Any]] = {}
    
    @property
    def supported_data_types(self) -> List[DataType]:
        return list(DataType)  # Supports all data types
    
    @property
    def technique(self) -> MaskingTechnique:
        return MaskingTechnique.SHUFFLING
    
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask value using shuffling technique"""
        if value is None and rule.preserve_null:
            return None
        
        # For shuffling, we need all column values
        # This is a simplified implementation
        column_key = f"{rule.table_name}.{rule.column_name}"
        
        if column_key not in self.column_values:
            # In real implementation, this would fetch all column values
            self.column_values[column_key] = [value]
        
        # Return a random value from the column (simplified)
        if self.column_values[column_key]:
            return random.choice(self.column_values[column_key])
        
        return value
    
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate shuffling rule"""
        return rule.masking_technique == self.technique


class TokenizationMasker(DataMasker):
    """Tokenization-based data masker"""
    
    def __init__(self):
        self.token_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
    
    @property
    def supported_data_types(self) -> List[DataType]:
        return list(DataType)  # Supports all data types
    
    @property
    def technique(self) -> MaskingTechnique:
        return MaskingTechnique.TOKENIZATION
    
    async def mask_value(
        self, 
        value: Any, 
        rule: MaskingRule,
        context: Dict[str, Any] = None
    ) -> Any:
        """Mask value using tokenization"""
        if value is None and rule.preserve_null:
            return None
        
        value_str = str(value)
        
        # Check if we already have a token for this value
        if value_str in self.token_map:
            return self.token_map[value_str]
        
        # Generate new token
        if rule.preserve_format and rule.data_type == DataType.EMAIL:
            # Generate email-like token
            token = f"token{len(self.token_map)}@example.com"
        elif rule.preserve_format and rule.data_type == DataType.PHONE:
            # Generate phone-like token
            token = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        else:
            # Generate generic token
            if rule.preserve_length:
                token_length = len(value_str)
            else:
                token_length = 16
            
            token = f"TOKEN_{uuid.uuid4().hex[:token_length-6]}"
        
        # Store mapping
        self.token_map[value_str] = token
        self.reverse_map[token] = value_str
        
        return token
    
    async def validate_rule(self, rule: MaskingRule) -> bool:
        """Validate tokenization rule"""
        return rule.masking_technique == self.technique
    
    def detokenize(self, token: str) -> Optional[str]:
        """Reverse tokenization to get original value"""
        return self.reverse_map.get(token)


class DataMaskingEngine:
    """
    Enterprise-grade data masking engine
    
    Provides comprehensive data masking capabilities including:
    - Multiple masking techniques (redaction, substitution, encryption, etc.)
    - Support for various data types
    - Configurable masking rules
    - Batch processing capabilities
    - Quality validation and reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data masking engine"""
        self.config = config or {}
        self.maskers: Dict[MaskingTechnique, DataMasker] = {}
        self.masking_rules: Dict[str, MaskingRule] = {}
        self.masking_jobs: Dict[str, MaskingJob] = {}
        
        # Configuration
        self.batch_size = self.config.get("batch_size", 1000)
        self.parallel_workers = self.config.get("parallel_workers", 4)
        self.quality_threshold = self.config.get("quality_threshold", 0.95)
        self.preserve_referential_integrity = self.config.get("preserve_referential_integrity", True)
        
        # Initialize maskers
        self._initialize_maskers()
        
        logger.info("Data masking engine initialized successfully")
    
    def _initialize_maskers(self):
        """Initialize data masking implementations"""
        try:
            # Register built-in maskers
            self.maskers[MaskingTechnique.REDACTION] = RedactionMasker()
            self.maskers[MaskingTechnique.SUBSTITUTION] = SubstitutionMasker()
            self.maskers[MaskingTechnique.ENCRYPTION] = EncryptionMasker()
            self.maskers[MaskingTechnique.SHUFFLING] = ShufflingMasker()
            self.maskers[MaskingTechnique.TOKENIZATION] = TokenizationMasker()
            
            logger.info(f"Initialized {len(self.maskers)} data maskers")
            
        except Exception as e:
            logger.error(f"Failed to initialize maskers: {e}")
            raise
    
    async def add_masking_rule(self, rule: MaskingRule) -> bool:
        """
        Add data masking rule
        
        Args:
            rule: Masking rule definition
            
        Returns:
            True if rule added successfully, False otherwise
        """
        try:
            # Validate rule
            if not await self._validate_masking_rule(rule):
                logger.error(f"Invalid masking rule: {rule.rule_id}")
                return False
            
            # Store rule
            self.masking_rules[rule.rule_id] = rule
            
            logger.info(f"Added masking rule: {rule.rule_id} for {rule.table_name}.{rule.column_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add masking rule: {e}")
            return False
    
    async def _validate_masking_rule(self, rule: MaskingRule) -> bool:
        """Validate masking rule"""
        try:
            # Check if masker exists for technique
            if rule.masking_technique not in self.maskers:
                logger.error(f"No masker available for technique: {rule.masking_technique}")
                return False
            
            # Validate with specific masker
            masker = self.maskers[rule.masking_technique]
            return await masker.validate_rule(rule)
            
        except Exception as e:
            logger.error(f"Rule validation error: {e}")
            return False
    
    async def create_masking_job(
        self,
        name: str,
        description: str,
        source_database: str,
        target_database: str,
        rule_ids: List[str],
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """
        Create data masking job
        
        Args:
            name: Job name
            description: Job description
            source_database: Source database connection
            target_database: Target database connection
            rule_ids: List of masking rule IDs to apply
            scheduled_at: Optional scheduled execution time
            
        Returns:
            Job ID
        """
        try:
            # Validate rules exist
            job_rules = []
            for rule_id in rule_ids:
                if rule_id not in self.masking_rules:
                    raise ValueError(f"Masking rule not found: {rule_id}")
                job_rules.append(self.masking_rules[rule_id])
            
            # Create job
            job = MaskingJob(
                job_id=str(uuid.uuid4()),
                name=name,
                description=description,
                source_database=source_database,
                target_database=target_database,
                masking_rules=job_rules,
                scheduled_at=scheduled_at
            )
            
            # Store job
            self.masking_jobs[job.job_id] = job
            
            # Start job if not scheduled
            if not scheduled_at:
                asyncio.create_task(self._execute_masking_job(job))
            
            logger.info(f"Created masking job: {job.job_id}")
            return job.job_id
            
        except Exception as e:
            logger.error(f"Failed to create masking job: {e}")
            raise
    
    async def _execute_masking_job(self, job: MaskingJob):
        """Execute data masking job"""
        try:
            # Update job status
            job.status = "running"
            job.statistics = {
                "start_time": datetime.now().isoformat(),
                "tables_processed": 0,
                "records_processed": 0,
                "records_masked": 0,
                "errors": []
            }
            
            logger.info(f"Starting masking job: {job.job_id}")
            
            # Group rules by table
            rules_by_table = {}
            for rule in job.masking_rules:
                table = rule.table_name
                if table not in rules_by_table:
                    rules_by_table[table] = []
                rules_by_table[table].append(rule)
            
            total_tables = len(rules_by_table)
            processed_tables = 0
            
            # Process each table
            for table_name, table_rules in rules_by_table.items():
                try:
                    await self._mask_table(job, table_name, table_rules)
                    processed_tables += 1
                    job.progress = (processed_tables / total_tables) * 100
                    
                except Exception as e:
                    error_msg = f"Error masking table {table_name}: {e}"
                    job.statistics["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Update final status
            job.status = "completed" if not job.statistics["errors"] else "completed_with_errors"
            job.statistics["end_time"] = datetime.now().isoformat()
            job.progress = 100.0
            
            logger.info(f"Masking job completed: {job.job_id}")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.statistics["end_time"] = datetime.now().isoformat()
            logger.error(f"Masking job failed: {job.job_id} - {e}")
    
    async def _mask_table(self, job: MaskingJob, table_name: str, rules: List[MaskingRule]):
        """Mask data in a specific table"""
        try:
            # In a real implementation, this would:
            # 1. Connect to source database
            # 2. Read data in batches
            # 3. Apply masking rules
            # 4. Write to target database
            
            # Simulate processing
            simulated_record_count = 1000  # Simulate 1000 records
            batch_count = (simulated_record_count + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(batch_count):
                batch_start = batch_idx * self.batch_size
                batch_end = min(batch_start + self.batch_size, simulated_record_count)
                batch_size = batch_end - batch_start
                
                # Simulate masking each column in the batch
                for rule in rules:
                    # Simulate masking data
                    masker = self.maskers[rule.masking_technique]
                    
                    # Sample values for demonstration
                    sample_values = await self._generate_sample_values(rule.data_type, batch_size)
                    
                    for value in sample_values:
                        masked_value = await masker.mask_value(value, rule)
                        # In real implementation, this would update the database
                    
                    job.statistics["records_masked"] += batch_size
                
                job.statistics["records_processed"] += batch_size
                
                # Simulate processing delay
                await asyncio.sleep(0.01)
            
            job.statistics["tables_processed"] += 1
            logger.info(f"Masked table {table_name} with {len(rules)} rules")
            
        except Exception as e:
            logger.error(f"Failed to mask table {table_name}: {e}")
            raise
    
    async def _generate_sample_values(self, data_type: DataType, count: int) -> List[Any]:
        """Generate sample values for testing (development only)"""
        faker = Faker()
        values = []
        
        for _ in range(count):
            if data_type == DataType.EMAIL:
                values.append(faker.email())
            elif data_type == DataType.PHONE:
                values.append(faker.phone_number())
            elif data_type == DataType.NAME:
                values.append(faker.name())
            elif data_type == DataType.ADDRESS:
                values.append(faker.address())
            elif data_type == DataType.SSN:
                values.append(faker.ssn())
            elif data_type == DataType.CREDIT_CARD:
                values.append(faker.credit_card_number())
            else:
                values.append(faker.text(max_nb_chars=50))
        
        return values
    
    async def test_masking_rule(self, rule_id: str, sample_values: List[Any]) -> Dict[str, Any]:
        """
        Test masking rule with sample values
        
        Args:
            rule_id: Masking rule ID
            sample_values: Sample values to test
            
        Returns:
            Test results including original and masked values
        """
        try:
            if rule_id not in self.masking_rules:
                raise ValueError(f"Masking rule not found: {rule_id}")
            
            rule = self.masking_rules[rule_id]
            masker = self.maskers[rule.masking_technique]
            
            test_results = {
                "rule_id": rule_id,
                "technique": rule.masking_technique.value,
                "data_type": rule.data_type.value,
                "test_cases": []
            }
            
            for original_value in sample_values:
                try:
                    masked_value = await masker.mask_value(original_value, rule)
                    
                    test_case = {
                        "original": original_value,
                        "masked": masked_value,
                        "success": True,
                        "quality_score": await self._calculate_quality_score(
                            original_value, masked_value, rule
                        )
                    }
                    
                except Exception as e:
                    test_case = {
                        "original": original_value,
                        "masked": None,
                        "success": False,
                        "error": str(e),
                        "quality_score": 0.0
                    }
                
                test_results["test_cases"].append(test_case)
            
            # Calculate overall quality
            successful_cases = [tc for tc in test_results["test_cases"] if tc["success"]]
            if successful_cases:
                avg_quality = sum(tc["quality_score"] for tc in successful_cases) / len(successful_cases)
                test_results["overall_quality"] = avg_quality
                test_results["success_rate"] = len(successful_cases) / len(sample_values)
            else:
                test_results["overall_quality"] = 0.0
                test_results["success_rate"] = 0.0
            
            return test_results
            
        except Exception as e:
            logger.error(f"Failed to test masking rule: {e}")
            raise
    
    async def _calculate_quality_score(
        self, 
        original: Any, 
        masked: Any, 
        rule: MaskingRule
    ) -> float:
        """Calculate quality score for masked value"""
        score = 0.0
        
        if original is None and masked is None:
            return 1.0  # Perfect for null preservation
        
        if original is not None and masked is not None:
            score += 0.3  # Basic masking success
            
            # Check format preservation
            if rule.preserve_format:
                if self._has_similar_format(original, masked, rule.data_type):
                    score += 0.3
            else:
                score += 0.3  # No format requirement
            
            # Check length preservation
            if rule.preserve_length:
                if len(str(original)) == len(str(masked)):
                    score += 0.2
            else:
                score += 0.2  # No length requirement
            
            # Check that value is actually masked (different)
            if str(original) != str(masked):
                score += 0.2
        
        return min(score, 1.0)
    
    def _has_similar_format(self, original: Any, masked: Any, data_type: DataType) -> bool:
        """Check if masked value preserves format of original"""
        orig_str = str(original)
        masked_str = str(masked)
        
        if data_type == DataType.EMAIL:
            return "@" in orig_str and "@" in masked_str
        elif data_type == DataType.PHONE:
            # Check if both have similar non-digit characters
            orig_pattern = re.sub(r'\d', 'X', orig_str)
            masked_pattern = re.sub(r'\d', 'X', masked_str)
            return orig_pattern == masked_pattern
        elif data_type == DataType.SSN:
            return re.sub(r'\d', 'X', orig_str) == re.sub(r'\d', 'X', masked_str)
        elif data_type == DataType.CREDIT_CARD:
            return re.sub(r'\d', 'X', orig_str) == re.sub(r'\d', 'X', masked_str)
        
        return True  # Default to true for other types
    
    def get_job_status(self, job_id: str) -> Optional[MaskingJob]:
        """Get masking job status"""
        return self.masking_jobs.get(job_id)
    
    def list_masking_rules(self) -> List[MaskingRule]:
        """List all masking rules"""
        return list(self.masking_rules.values())
    
    def list_active_jobs(self) -> List[MaskingJob]:
        """List active masking jobs"""
        return [
            job for job in self.masking_jobs.values()
            if job.status in ["pending", "running"]
        ]
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel running masking job"""
        try:
            if job_id in self.masking_jobs:
                job = self.masking_jobs[job_id]
                if job.status in ["pending", "running"]:
                    job.status = "cancelled"
                    logger.info(f"Masking job cancelled: {job_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def get_masking_metrics(self) -> Dict[str, Any]:
        """Get data masking metrics"""
        total_jobs = len(self.masking_jobs)
        completed_jobs = sum(
            1 for job in self.masking_jobs.values() 
            if job.status == "completed"
        )
        failed_jobs = sum(
            1 for job in self.masking_jobs.values() 
            if job.status == "failed"
        )
        
        total_records = sum(
            job.statistics.get("records_processed", 0) 
            for job in self.masking_jobs.values()
        )
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (completed_jobs / max(total_jobs, 1)) * 100,
            "total_records_processed": total_records,
            "total_masking_rules": len(self.masking_rules),
            "available_techniques": [t.value for t in self.maskers.keys()],
            "active_jobs": len(self.list_active_jobs())
        }


# Module initialization
logger.info("Database data masking engine module loaded successfully")
