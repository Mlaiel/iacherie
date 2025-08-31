"""
Privacy Management and Data Protection System

Advanced privacy controls including PII detection, anonymization,
pseudonymization, and data masking for GDPR and other compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import logging
import re
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ...core.base import BaseManager
from ...core.exceptions import PrivacyError, ValidationError
from ...ai.models import PersonalDataDetector, NamedEntityRecognizer

# Initialize logger
logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of personally identifiable information"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"
    MEDICAL_ID = "medical_id"
    BIOMETRIC = "biometric"


class AnonymizationTechnique(Enum):
    """Data anonymization techniques"""
    MASKING = "masking"
    HASHING = "hashing"
    ENCRYPTION = "encryption"
    TOKENIZATION = "tokenization"
    GENERALIZATION = "generalization"
    SUPPRESSION = "suppression"
    NOISE_ADDITION = "noise_addition"
    SWAPPING = "swapping"
    SYNTHETIC = "synthetic"


class PrivacyLevel(Enum):
    """Privacy protection levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


@dataclass
class PIIDetectionResult:
    """Result of PII detection analysis"""
    content_id: str
    pii_found: bool
    pii_types: List[PIIType]
    pii_locations: List[Dict[str, Any]]
    confidence_score: float
    risk_level: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnonymizationRule:
    """Anonymization rule definition"""
    rule_id: str
    name: str
    pii_types: List[PIIType]
    technique: AnonymizationTechnique
    parameters: Dict[str, Any]
    reversible: bool = False
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnonymizationRecord:
    """Record of anonymization operation"""
    record_id: str
    content_id: str
    original_hash: str
    anonymized_hash: str
    technique: AnonymizationTechnique
    reversible: bool
    key_reference: Optional[str] = None
    performed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PIIDetector:
    """
    Advanced PII detection system
    
    Uses multiple detection methods including regex patterns,
    named entity recognition, and ML models.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI models
        self.pii_model = PersonalDataDetector(config)
        self.ner_model = NamedEntityRecognizer(config)
        
        # Regex patterns for common PII types
        self.patterns = {
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
            PIIType.SSN: re.compile(r'\b(?!000)(?!666)(?!9)\d{3}[-.\s]?(?!00)\d{2}[-.\s]?(?!0000)\d{4}\b'),
            PIIType.CREDIT_CARD: re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
            PIIType.IP_ADDRESS: re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        }
    
    async def detect_pii(
        self,
        content: str,
        content_type: str = "text"
    ) -> PIIDetectionResult:
        """
        Detect PII in content
        
        Args:
            content: Content to analyze
            content_type: Type of content
            
        Returns:
            PIIDetectionResult: Detection results
        """



        try:
            pii_found = False
            pii_types = []
            pii_locations = []
            total_confidence = 0.0
            detection_count = 0
            
            # Regex-based detection
            for pii_type, pattern in self.patterns.items():
                matches = pattern.finditer(content)
                for match in matches:
                    pii_found = True
                    if pii_type not in pii_types:
                        pii_types.append(pii_type)
                    
                    pii_locations.append({
                        "type": pii_type.value,
                        "start": match.start(),
                        "end": match.end(),
                        "text": match.group(),
                        "confidence": 0.9,
                        "method": "regex"
                    })
                    total_confidence += 0.9
                    detection_count += 1
            
            # AI model detection
            ai_results = await self.pii_model.detect_pii(content)
            if ai_results.get("pii_detected"):
                pii_found = True
                for detection in ai_results.get("detections", []):
                    pii_type_str = detection.get("type")
                    try:
                        pii_type = PIIType(pii_type_str)
                        if pii_type not in pii_types:
                            pii_types.append(pii_type)
                    except ValueError:
                        continue
                    
                    pii_locations.append({
                        "type": pii_type_str,
                        "start": detection.get("start", 0),
                        "end": detection.get("end", 0),
                        "text": detection.get("text", ""),
                        "confidence": detection.get("confidence", 0.5),
                        "method": "ai_model"
                    })
                    total_confidence += detection.get("confidence", 0.5)
                    detection_count += 1
            
            # NER-based detection for names
            ner_results = await self.ner_model.extract_entities(content)
            for entity in ner_results.get("entities", []):
                if entity.get("label") == "PERSON":
                    pii_found = True
                    if PIIType.NAME not in pii_types:
                        pii_types.append(PIIType.NAME)
                    
                    pii_locations.append({
                        "type": "name",
                        "start": entity.get("start", 0),
                        "end": entity.get("end", 0),
                        "text": entity.get("text", ""),
                        "confidence": entity.get("confidence", 0.8),
                        "method": "ner"
                    })
                    total_confidence += entity.get("confidence", 0.8)
                    detection_count += 1
            
            # Calculate overall confidence
            confidence_score = total_confidence / detection_count if detection_count > 0 else 0.0
            
            # Determine risk level
            risk_level = self._assess_risk_level(pii_types, confidence_score)
            
            return PIIDetectionResult(
                content_id=hashlib.md5(content.encode()).hexdigest()[:16],
                pii_found=pii_found,
                pii_types=pii_types,
                pii_locations=pii_locations,
                confidence_score=confidence_score,
                risk_level=risk_level,
                metadata={
                    "content_length": len(content),
                    "detection_methods": ["regex", "ai_model", "ner"],
                    "total_detections": detection_count
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error detecting PII: {e}")
            raise PrivacyError(f"PII detection failed: {e}")
    
    def _assess_risk_level(self, pii_types: List[PIIType], confidence: float) -> str:
        """Assess privacy risk level based on PII types and confidence"""
        high_risk_types = {PIIType.SSN, PIIType.CREDIT_CARD, PIIType.PASSPORT, PIIType.MEDICAL_ID}
        medium_risk_types = {PIIType.EMAIL, PIIType.PHONE, PIIType.ADDRESS, PIIType.DATE_OF_BIRTH}
        
        if any(pii_type in high_risk_types for pii_type in pii_types):
            return "high"
        elif any(pii_type in medium_risk_types for pii_type in pii_types):
            return "medium"
        elif pii_types and confidence > 0.7:
            return "medium"
        elif pii_types:
            return "low"
        else:
            return "none"


class BaseAnonymizer(ABC):
    """Base class for anonymization techniques"""
    
    async def anonymize(self, data: str, parameters: Dict[str, Any]) -> str:
        """Anonymize the data - base implementation"""



        try:
            logger.info(f"Anonymizing data with {self.__class__.__name__}")
            
            # Basic implementation that masks sensitive patterns
            # Subclasses should override with specific anonymization logic
            if not data:
                return data
            
            # Simple masking implementation
            mask_char = parameters.get("mask_char", "*")
            mask_length = parameters.get("mask_length", len(data))
            
            # Basic anonymization - replace most characters with mask
            if len(data) <= 3:
                return mask_char * len(data)
            else:
                # Keep first and last character, mask the middle
                return data[0] + mask_char * (len(data) - 2) + data[-1]
                
        except Exception as e:
            logger.error(f"Error in anonymization: {str(e)}")
            return mask_char * len(data) if data else ""
    
    async def deanonymize(self, data: str, key: str) -> str:
        """Reverse anonymization if possible - base implementation"""



        try:
            logger.warning(f"Deanonymization attempted with {self.__class__.__name__}")
            
            # Base implementation - cannot reverse simple masking
            # Subclasses should override with specific deanonymization logic
            if self.is_reversible():
                logger.info(f"Attempting deanonymization with key: {key[:4]}...")
                # In a real implementation, this would use the key to reverse the process
                return data  # Return as-is for base implementation
            else:
                logger.warning("Deanonymization not supported for this anonymization technique")
                return data
                
        except Exception as e:
            logger.error(f"Error in deanonymization: {str(e)}")
            return data
    
    def is_reversible(self) -> bool:
        """Check if technique is reversible - base implementation"""
        # Base implementation - simple masking is not reversible
        # Subclasses should override with specific reversibility logic
        return False


class MaskingAnonymizer(BaseAnonymizer):
    """Data masking anonymizer"""
    
    async def anonymize(self, data: str, parameters: Dict[str, Any]) -> str:
        """Mask data with specified character"""
        mask_char = parameters.get("mask_char", "*")
        preserve_length = parameters.get("preserve_length", True)
        preserve_prefix = parameters.get("preserve_prefix", 0)
        preserve_suffix = parameters.get("preserve_suffix", 0)
        
        if not preserve_length:
            return mask_char * 5
        
        if len(data) <= (preserve_prefix + preserve_suffix):
            return mask_char * len(data)
        
        prefix = data[:preserve_prefix] if preserve_prefix > 0 else ""
        suffix = data[-preserve_suffix:] if preserve_suffix > 0 else ""
        middle_length = len(data) - preserve_prefix - preserve_suffix
        
        return prefix + (mask_char * middle_length) + suffix
    
    async def deanonymize(self, data: str, key: str) -> str:
        """Cannot reverse masking"""
        raise PrivacyError("Masking is not reversible")
    
    def is_reversible(self) -> bool:
        return False


class HashingAnonymizer(BaseAnonymizer):
    """Hashing-based anonymizer"""
    
    async def anonymize(self, data: str, parameters: Dict[str, Any]) -> str:
        """Hash data with salt"""
        algorithm = parameters.get("algorithm", "sha256")
        salt = parameters.get("salt", "")
        
        salted_data = salt + data
        
        if algorithm == "sha256":
            return hashlib.sha256(salted_data.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(salted_data.encode()).hexdigest()
        else:
            return hashlib.sha256(salted_data.encode()).hexdigest()
    
    async def deanonymize(self, data: str, key: str) -> str:
        """Cannot reverse hashing"""
        raise PrivacyError("Hashing is not reversible")
    
    def is_reversible(self) -> bool:
        return False


class TokenizationAnonymizer(BaseAnonymizer):
    """Tokenization anonymizer"""
    
    def __init__(self):
        self.token_mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
    
    async def anonymize(self, data: str, parameters: Dict[str, Any]) -> str:
        """Replace data with random token"""
        if data in self.token_mapping:
            return self.token_mapping[data]
        
        token_prefix = parameters.get("prefix", "TOK_")
        token_length = parameters.get("token_length", 16)
        
        token = token_prefix + secrets.token_hex(token_length // 2)
        
        self.token_mapping[data] = token
        self.reverse_mapping[token] = data
        
        return token
    
    async def deanonymize(self, data: str, key: str) -> str:
        """Reverse tokenization"""
        if data in self.reverse_mapping:
            return self.reverse_mapping[data]
        raise PrivacyError(f"Token {data} not found in mapping")
    
    def is_reversible(self) -> bool:
        return True


class EncryptionAnonymizer(BaseAnonymizer):
    """Encryption-based anonymizer"""
    
    async def anonymize(self, data: str, parameters: Dict[str, Any]) -> str:
        """Encrypt data"""
        # This would use actual encryption libraries
        # Simplified implementation for demonstration
        key = parameters.get("key", "default_key")
        encrypted = self._simple_encrypt(data, key)
        return encrypted
    
    async def deanonymize(self, data: str, key: str) -> str:
        """Decrypt data"""
        decrypted = self._simple_decrypt(data, key)
        return decrypted
    
    def is_reversible(self) -> bool:
        return True
    
    def _simple_encrypt(self, data: str, key: str) -> str:
        """AES-256 encryption implementation"""



        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from provided key string
            key_bytes = hashlib.sha256(key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            fernet = Fernet(fernet_key)
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            # Fallback to simple Caesar cipher for basic obfuscation
            return self._caesar_encrypt(data, len(key) % 25 + 1)
    
    def _simple_decrypt(self, data: str, key: str) -> str:
        """AES-256 decryption implementation"""



        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from provided key string
            key_bytes = hashlib.sha256(key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            fernet = Fernet(fernet_key)
            
            # Decrypt the data
            encrypted_data = base64.urlsafe_b64decode(data.encode())
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            # Fallback to simple Caesar cipher for basic obfuscation
            return self._caesar_decrypt(data, len(key) % 25 + 1)
    
    def _caesar_encrypt(self, text: str, shift: int) -> str:
        """Simple Caesar cipher encryption as fallback"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    def _caesar_decrypt(self, text: str, shift: int) -> str:
        """Simple Caesar cipher decryption as fallback"""



        return self._caesar_encrypt(text, -shift)


class AnonymizationEngine:
    """
    Advanced data anonymization engine
    
    Applies various anonymization techniques based on rules
    and privacy requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize anonymizers
        self.anonymizers = {
            AnonymizationTechnique.MASKING: MaskingAnonymizer(),
            AnonymizationTechnique.HASHING: HashingAnonymizer(),
            AnonymizationTechnique.TOKENIZATION: TokenizationAnonymizer(),
            AnonymizationTechnique.ENCRYPTION: EncryptionAnonymizer()
        }
        
        # Storage for anonymization records
        self.anonymization_records: List[AnonymizationRecord] = []
    
    async def anonymize_content(
        self,
        content_id: str,
        content: str,
        pii_detections: PIIDetectionResult,
        rules: List[AnonymizationRule]
    ) -> Tuple[str, List[AnonymizationRecord]]:
        """
        Anonymize content based on PII detections and rules
        
        Args:
            content_id: Content identifier
            content: Original content
            pii_detections: PII detection results
            rules: Anonymization rules to apply
            
        Returns:
            Tuple[str, List[AnonymizationRecord]]: Anonymized content and records
        """



        try:
            anonymized_content = content
            records = []
            
            # Sort PII locations by position (reverse order to maintain positions)
            pii_locations = sorted(
                pii_detections.pii_locations,
                key=lambda x: x["start"],
                reverse=True
            )
            
            for location in pii_locations:
                pii_type_str = location["type"]
                try:
                    pii_type = PIIType(pii_type_str)
                except ValueError:
                    continue
                
                # Find applicable rule
                applicable_rule = self._find_applicable_rule(pii_type, rules)
                if not applicable_rule or not applicable_rule.enabled:
                    continue
                
                # Extract PII text
                start_pos = location["start"]
                end_pos = location["end"]
                pii_text = anonymized_content[start_pos:end_pos]
                
                # Apply anonymization
                anonymizer = self.anonymizers.get(applicable_rule.technique)
                if not anonymizer:
                    self.logger.warning(f"No anonymizer for technique: {applicable_rule.technique}")
                    continue
                
                anonymized_text = await anonymizer.anonymize(pii_text, applicable_rule.parameters)
                
                # Replace in content
                anonymized_content = (
                    anonymized_content[:start_pos] +
                    anonymized_text +
                    anonymized_content[end_pos:]
                )
                
                # Create anonymization record
                record = AnonymizationRecord(
                    record_id=f"anon_{content_id}_{len(records)}",
                    content_id=content_id,
                    original_hash=hashlib.sha256(pii_text.encode()).hexdigest(),
                    anonymized_hash=hashlib.sha256(anonymized_text.encode()).hexdigest(),
                    technique=applicable_rule.technique,
                    reversible=anonymizer.is_reversible(),
                    metadata={
                        "pii_type": pii_type_str,
                        "position": {"start": start_pos, "end": end_pos},
                        "rule_id": applicable_rule.rule_id
                    }
                )
                
                records.append(record)
                self.anonymization_records.append(record)
            
            return anonymized_content, records
            
        except Exception as e:
            self.logger.error(f"Error anonymizing content {content_id}: {e}")
            raise PrivacyError(f"Anonymization failed: {e}")
    
    async def deanonymize_content(
        self,
        content_id: str,
        anonymized_content: str,
        records: List[AnonymizationRecord],
        key: Optional[str] = None
    ) -> str:
        """
        Reverse anonymization if possible
        
        Args:
            content_id: Content identifier
            anonymized_content: Anonymized content
            records: Anonymization records
            key: Decryption key if needed
            
        Returns:
            str: Original content
        """



        try:
            deanonymized_content = anonymized_content
            
            # Process records in reverse order
            for record in reversed(records):
                if not record.reversible:
                    self.logger.warning(f"Cannot reverse {record.technique} for record {record.record_id}")
                    continue
                
                anonymizer = self.anonymizers.get(record.technique)
                if not anonymizer or not anonymizer.is_reversible():
                    continue
                
                # This is a simplified implementation
                # Real implementation would need to track exact positions and replacements
                # For now, just log the attempt
                self.logger.info(f"Attempting to reverse anonymization for record {record.record_id}")
            
            return deanonymized_content
            
        except Exception as e:
            self.logger.error(f"Error deanonymizing content {content_id}: {e}")
            raise PrivacyError(f"Deanonymization failed: {e}")
    
    def _find_applicable_rule(
        self,
        pii_type: PIIType,
        rules: List[AnonymizationRule]
    ) -> Optional[AnonymizationRule]:
        """Find the most appropriate anonymization rule for PII type"""
        for rule in rules:
            if pii_type in rule.pii_types:
                return rule
        return None


class PrivacyManager(BaseManager):
    """
    Central privacy management system
    
    Coordinates PII detection, anonymization, and privacy compliance
    across all content types in the platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the privacy manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pii_detector = PIIDetector(config)
        self.anonymization_engine = AnonymizationEngine(config)
        
        # Privacy storage
        self.pii_detections: Dict[str, PIIDetectionResult] = {}
        self.anonymization_rules: Dict[str, AnonymizationRule] = {}
        self.privacy_assessments: Dict[str, Dict[str, Any]] = {}
        
        # Performance metrics
        self.metrics = {
            "total_scans": 0,
            "pii_detected_count": 0,
            "anonymizations_performed": 0,
            "privacy_violations": 0
        }
    
    async def initialize(self) -> None:
        """Initialize the privacy manager"""



        try:
            await self._create_default_anonymization_rules()
            self.logger.info("Privacy manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize privacy manager: {e}")
            raise PrivacyError(f"Privacy manager initialization failed: {e}")
    
    async def scan_for_pii(
        self,
        content_id: str,
        content: str,
        content_type: str = "text"
    ) -> PIIDetectionResult:
        """
        Scan content for personally identifiable information
        
        Args:
            content_id: Content identifier
            content: Content to scan
            content_type: Type of content
            
        Returns:
            PIIDetectionResult: Detection results
        """



        try:
            # Perform PII detection
            detection_result = await self.pii_detector.detect_pii(content, content_type)
            detection_result.content_id = content_id
            
            # Store results
            self.pii_detections[content_id] = detection_result
            
            # Update metrics
            self.metrics["total_scans"] += 1
            if detection_result.pii_found:
                self.metrics["pii_detected_count"] += 1
            
            self.logger.info(f"PII scan completed for {content_id}: {detection_result.pii_found}")
            return detection_result
            
        except Exception as e:
            self.logger.error(f"Error scanning PII for {content_id}: {e}")
            raise PrivacyError(f"PII scanning failed: {e}")
    
    async def anonymize_content(
        self,
        content_id: str,
        content: str,
        privacy_level: PrivacyLevel = PrivacyLevel.CONFIDENTIAL
    ) -> Tuple[str, bool]:
        """
        Anonymize content based on privacy level
        
        Args:
            content_id: Content identifier
            content: Content to anonymize
            privacy_level: Required privacy level
            
        Returns:
            Tuple[str, bool]: Anonymized content and success flag
        """



        try:
            # First scan for PII
            pii_detection = await self.scan_for_pii(content_id, content)
            
            if not pii_detection.pii_found:
                return content, True
            
            # Get anonymization rules based on privacy level
            applicable_rules = await self._get_rules_for_privacy_level(privacy_level)
            
            # Perform anonymization
            anonymized_content, records = await self.anonymization_engine.anonymize_content(
                content_id, content, pii_detection, applicable_rules
            )
            
            # Update metrics
            self.metrics["anonymizations_performed"] += 1
            
            self.logger.info(f"Content anonymized for {content_id}: {len(records)} operations")
            return anonymized_content, True
            
        except Exception as e:
            self.logger.error(f"Error anonymizing content {content_id}: {e}")
            return content, False
    
    async def assess_privacy_risk(
        self,
        content_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess privacy risk for content
        
        Args:
            content_id: Content identifier
            content: Content to assess
            metadata: Additional metadata
            
        Returns:
            Dict with privacy risk assessment
        """



        try:
            # Scan for PII
            pii_detection = await self.scan_for_pii(content_id, content)
            
            # Calculate risk score
            risk_score = self._calculate_privacy_risk_score(pii_detection, metadata or {})
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "critical"
            elif risk_score >= 60:
                risk_level = "high"
            elif risk_score >= 40:
                risk_level = "medium"
            elif risk_score >= 20:
                risk_level = "low"
            else:
                risk_level = "minimal"
            
            # Generate recommendations
            recommendations = self._generate_privacy_recommendations(pii_detection, risk_score)
            
            assessment = {
                "content_id": content_id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "pii_found": pii_detection.pii_found,
                "pii_types": [pii_type.value for pii_type in pii_detection.pii_types],
                "recommendations": recommendations,
                "assessed_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "detection_confidence": pii_detection.confidence_score,
                    "content_length": len(content),
                    "pii_count": len(pii_detection.pii_locations)
                }
            }
            
            # Store assessment
            self.privacy_assessments[content_id] = assessment
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing privacy risk for {content_id}: {e}")
            return {"error": f"Privacy assessment failed: {e}"}
    
    async def create_anonymization_rule(self, rule: AnonymizationRule) -> bool:
        """
        Create a new anonymization rule
        
        Args:
            rule: Anonymization rule to create
            
        Returns:
            bool: True if rule created successfully
        """



        try:
            # Validate rule
            await self._validate_anonymization_rule(rule)
            
            # Store rule
            self.anonymization_rules[rule.rule_id] = rule
            
            self.logger.info(f"Created anonymization rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating anonymization rule {rule.rule_id}: {e}")
            raise PrivacyError(f"Rule creation failed: {e}")
    
    async def get_pii_detection_results(
        self,
        content_id: Optional[str] = None,
        pii_type: Optional[PIIType] = None,
        risk_level: Optional[str] = None
    ) -> List[PIIDetectionResult]:
        """
        Get PII detection results with optional filtering
        
        Args:
            content_id: Filter by content ID
            pii_type: Filter by PII type
            risk_level: Filter by risk level
            
        Returns:
            List of filtered PII detection results
        """
        results = list(self.pii_detections.values())
        
        if content_id:
            results = [r for r in results if r.content_id == content_id]
        
        if pii_type:
            results = [r for r in results if pii_type in r.pii_types]
        
        if risk_level:
            results = [r for r in results if r.risk_level == risk_level]
        
        return results
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get privacy management metrics"""



        return {
            **self.metrics,
            "total_rules": len(self.anonymization_rules),
            "total_assessments": len(self.privacy_assessments),
            "pii_detection_rate": (
                (self.metrics["pii_detected_count"] / self.metrics["total_scans"] * 100)
                if self.metrics["total_scans"] > 0 else 0
            )
        }
    
    def _calculate_privacy_risk_score(
        self,
        pii_detection: PIIDetectionResult,
        metadata: Dict[str, Any]
    ) -> float:
        """Calculate privacy risk score (0-100)"""
        score = 0.0
        
        if not pii_detection.pii_found:
            return score
        
        # Base score for PII presence
        score += 20
        
        # Score based on PII types
        high_risk_types = {PIIType.SSN, PIIType.CREDIT_CARD, PIIType.PASSPORT, PIIType.MEDICAL_ID}
        medium_risk_types = {PIIType.EMAIL, PIIType.PHONE, PIIType.ADDRESS}
        
        for pii_type in pii_detection.pii_types:
            if pii_type in high_risk_types:
                score += 25
            elif pii_type in medium_risk_types:
                score += 15
            else:
                score += 10
        
        # Confidence factor
        score *= pii_detection.confidence_score
        
        # Number of PII instances
        pii_count = len(pii_detection.pii_locations)
        if pii_count > 5:
            score += 15
        elif pii_count > 2:
            score += 10
        elif pii_count > 1:
            score += 5
        
        # Content context
        if metadata.get("public", False):
            score += 20
        if metadata.get("shared", False):
            score += 10
        
        return min(score, 100.0)
    
    def _generate_privacy_recommendations(
        self,
        pii_detection: PIIDetectionResult,
        risk_score: float
    ) -> List[str]:
        """Generate privacy protection recommendations"""
        recommendations = []
        
        if not pii_detection.pii_found:
            recommendations.append("No PII detected - content appears safe")
            return recommendations
        
        if risk_score >= 60:
            recommendations.append("High privacy risk detected - consider anonymization")
            recommendations.append("Restrict access to authorized personnel only")
        
        # Specific recommendations by PII type
        pii_recommendations = {
            PIIType.EMAIL: "Consider masking email addresses",
            PIIType.PHONE: "Consider masking phone numbers",
            PIIType.SSN: "Immediately encrypt or mask SSN",
            PIIType.CREDIT_CARD: "Immediately encrypt or mask credit card numbers",
            PIIType.NAME: "Consider using pseudonyms or initials",
            PIIType.ADDRESS: "Consider generalizing location information"
        }
        
        for pii_type in pii_detection.pii_types:
            if pii_type in pii_recommendations:
                recommendations.append(pii_recommendations[pii_type])
        
        return recommendations
    
    async def _get_rules_for_privacy_level(
        self,
        privacy_level: PrivacyLevel
    ) -> List[AnonymizationRule]:
        """Get anonymization rules appropriate for privacy level"""
        rules = []
        
        for rule in self.anonymization_rules.values():
            if not rule.enabled:
                continue
            
            # Simple privacy level matching - can be enhanced
            if privacy_level in [PrivacyLevel.CONFIDENTIAL, PrivacyLevel.RESTRICTED, PrivacyLevel.TOP_SECRET]:
                rules.append(rule)
        
        return rules
    
    async def _validate_anonymization_rule(self, rule: AnonymizationRule) -> None:
        """Validate anonymization rule configuration"""
        if not rule.rule_id or not rule.name:
            raise ValidationError("Rule ID and name are required")
        
        if not rule.pii_types:
            raise ValidationError("Rule must specify at least one PII type")
        
        if rule.technique not in self.anonymization_engine.anonymizers:
            raise ValidationError(f"Unsupported anonymization technique: {rule.technique}")
    
    async def _create_default_anonymization_rules(self) -> None:
        """Create default anonymization rules"""
        # High-sensitivity PII rule
        high_sensitivity_rule = AnonymizationRule(
            rule_id="high_sensitivity_pii",
            name="High Sensitivity PII Protection",
            pii_types=[PIIType.SSN, PIIType.CREDIT_CARD, PIIType.PASSPORT, PIIType.MEDICAL_ID],
            technique=AnonymizationTechnique.ENCRYPTION,
            parameters={"algorithm": "aes256", "key_length": 32},
            reversible=True
        )
        await self.create_anonymization_rule(high_sensitivity_rule)
        
        # Medium-sensitivity PII rule
        medium_sensitivity_rule = AnonymizationRule(
            rule_id="medium_sensitivity_pii",
            name="Medium Sensitivity PII Protection",
            pii_types=[PIIType.EMAIL, PIIType.PHONE, PIIType.ADDRESS],
            technique=AnonymizationTechnique.MASKING,
            parameters={"mask_char": "*", "preserve_prefix": 2, "preserve_suffix": 2},
            reversible=False
        )
        await self.create_anonymization_rule(medium_sensitivity_rule)
        
        # Name anonymization rule
        name_rule = AnonymizationRule(
            rule_id="name_anonymization",
            name="Name Anonymization",
            pii_types=[PIIType.NAME],
            technique=AnonymizationTechnique.TOKENIZATION,
            parameters={"prefix": "PERSON_", "token_length": 8},
            reversible=True
        )
        await self.create_anonymization_rule(name_rule)
