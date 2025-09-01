"""Content processing and protection interfaces for IA Influencer Agent.

Defines interfaces for multi-format content handling, protection,
fingerprinting, validation and metadata management.

Author: Fahed Mlaiel <mlaiel@live.de>
(c) 2025 - All rights reserved. Unauthorized use prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum
import numpy as np


class ContentType(Enum):
    """
Supported content types for processing and protection."""

    AUDIO = "audio"
    VIDEO = "video"  
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MUSIC = "music"
    PODCAST = "podcast"
    STREAM = "stream"


class ProtectionLevel(Enum):
    """Content protection security levels."""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ContentProcessorInterface(ABC):
    """Interface for multi-format content processing."""
    
    @abstractmethod
    async def process_content(
        self,
        content_data: bytes,
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process content data and extract features.
        
        Args:
            content_data: Raw content bytes
            content_type: Type of content being processed
            metadata: Additional content metadata
            
        Returns:
            Processing results with extracted features
        """
        pass
    
    @abstractmethod
    async def extract_features(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> np.ndarray:
        """
Extract feature vectors from content."""
        pass
    
    @abstractmethod
    async def normalize_content(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> bytes:
        """
Normalize content for consistent processing."""
        pass
    
    @abstractmethod
    async def validate_content_quality(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> Dict[str, float]:
        """
Validate and score content quality metrics."""
        pass


class ContentProtectionInterface(ABC):
    """
Interface for content protection and rights management."""
    
    @abstractmethod
    async def protect_content(
        self,
        content_id: str,
        user_id: str,
        protection_level: ProtectionLevel
    ) -> Dict[str, Any]:
        """
        Apply protection to content.
        
        Args:
            content_id: Unique content identifier
            user_id: Content owner identifier
            protection_level: Level of protection to apply
            
        Returns:
            Protection configuration and status
        """
        pass
    
    @abstractmethod
    async def check_content_rights(
        self,
        content_id: str,
        user_id: str
    ) -> Dict[str, bool]:
        """
Check user rights for content access and modification."""
        pass
    
    @abstractmethod
    async def generate_protection_certificate(
        self,
        content_id: str,
        protection_config: Dict[str, Any]
    ) -> str:
        """
Generate cryptographic protection certificate."""
        pass
    
    @abstractmethod
    async def verify_content_integrity(
        self,
        content_id: str,
        current_hash: str
    ) -> bool:
        """
Verify content hasn't been tampered with."""
        pass
    
    @abstractmethod
    async def create_licensing_terms(
        self,
        content_id: str,
        terms: Dict[str, Any]
    ) -> str:
        """
Create licensing terms for content usage."""
        pass


class ContentFingerprinterInterface(ABC):
    """
Interface for AI-powered content fingerprinting."""
    
    @abstractmethod
    async def generate_fingerprint(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> str:
        """
        Generate unique fingerprint for content.
        
        Args:
            content_data: Raw content bytes
            content_type: Type of content
            
        Returns:
            Unique fingerprint hash
        """
        pass
    
    @abstractmethod
    async def generate_vector_embedding(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> np.ndarray:
        """
Generate vector embedding for similarity matching."""
        pass
    
    @abstractmethod
    async def compare_fingerprints(
        self,
        fingerprint1: str,
        fingerprint2: str
    ) -> float:
        """
Compare two fingerprints and return similarity score."""
        pass
    
    @abstractmethod
    async def search_similar_content(
        self,
        fingerprint: str,
        threshold: float = 0.9
    ) -> List[Dict[str, Any]]:
        """
Search for similar content using fingerprint matching."""
        pass
    
    @abstractmethod
    async def batch_fingerprint(
        self,
        content_batch: List[Tuple[bytes, ContentType]]
    ) -> List[str]:
        """
Generate fingerprints for multiple content items."""
        pass


class ContentValidatorInterface(ABC):
    """
Interface for content validation and compliance."""
    
    @abstractmethod
    async def validate_content_format(
        self,
        content_data: bytes,
        expected_type: ContentType
    ) -> bool:
        """
Validate content matches expected format."""
        pass
    
    @abstractmethod
    async def scan_for_malware(
        self,
        content_data: bytes
    ) -> Dict[str, Any]:
        """
Scan content for malicious code or threats."""
        pass
    
    @abstractmethod
    async def check_copyright_compliance(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
Check content for copyright violations."""
        pass
    
    @abstractmethod
    async def validate_content_metadata(
        self,
        metadata: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
Validate content metadata completeness and accuracy."""
        pass
    
    @abstractmethod
    async def check_platform_guidelines(
        self,
        content_data: bytes,
        platform: str
    ) -> Dict[str, Any]:
        """
Check content compliance with platform guidelines."""
        pass


class ContentMetadataInterface(ABC):
    """
Interface for content metadata management."""
    
    @abstractmethod
    async def extract_metadata(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content.
        
        Args:
            content_data: Raw content bytes
            content_type: Type of content
            
        Returns:
            Extracted metadata dictionary
        """
        pass
    
    @abstractmethod
    async def enrich_metadata(
        self,
        base_metadata: Dict[str, Any],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
Enrich metadata with AI-generated insights."""
        pass
    
    @abstractmethod
    async def generate_tags(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> List[str]:
        """
Generate relevant tags for content discovery."""
        pass
    
    @abstractmethod
    async def extract_technical_specs(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
Extract technical specifications and quality metrics."""
        pass
    
    @abstractmethod
    async def generate_content_summary(
        self,
        content_data: bytes,
        metadata: Dict[str, Any]
    ) -> str:
        """
Generate AI-powered content summary description."""
        pass
    
    @abstractmethod
    async def classify_content_genre(
        self,
        content_data: bytes,
        content_type: ContentType
    ) -> Dict[str, float]:
        """
Classify content genre with confidence scores."""
        pass
