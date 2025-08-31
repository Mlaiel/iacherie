"""
Response Handler Module
======================

Professional response handling system for API responses, crawler results, and platform interactions.
Manages response processing, validation, normalization, and error handling with enterprise reliability.

Response Types Supported:
- Platform API Responses (YouTube, Instagram, TikTok, Twitter)
- Web Scraping Results
- Content Detection Responses
- Fingerprinting Results
- Monetization API Responses
- Webhook Responses

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Type
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import re
from urllib.parse import urlparse, parse_qs
import hashlib
import base64
from decimal import Decimal
import aiohttp
from pydantic import BaseModel, ValidationError, validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import (
    ResponseHandlingError,
    ResponseValidationError,
    PlatformResponseError,
    DataNormalizationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.database.models import (
    CrawlerResponse, ContentFingerprint, User, 
    ProtectionAlert, RevenueTracking
)
from backend.database.session import async_session
from backend.utils.validation_utils import DataValidator
from backend.utils.encryption_utils import EncryptionManager
from backend.utils.rate_limit_utils import RateLimiter

logger = get_logger(__name__)


class ResponseType(Enum):
    """Enumeration of response types."""
    
    # Platform API Responses
    YOUTUBE_API = "youtube.api"
    INSTAGRAM_API = "instagram.api"
    TIKTOK_API = "tiktok.api"
    TWITTER_API = "twitter.api"
    SPOTIFY_API = "spotify.api"
    
    # Web Scraping
    WEB_SCRAPING = "web.scraping"
    HTML_PARSING = "html.parsing"
    
    # Content Processing
    FINGERPRINT_RESULT = "fingerprint.result"
    SIMILARITY_MATCH = "similarity.match"
    CONTENT_DETECTION = "content.detection"
    
    # Monetization
    REVENUE_DATA = "revenue.data"
    PAYMENT_RESPONSE = "payment.response"
    LICENSING_RESPONSE = "licensing.response"
    
    # System
    HEALTH_CHECK = "health.check"
    STATUS_UPDATE = "status.update"
    ERROR_RESPONSE = "error.response"


class ResponseStatus(Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"


@dataclass
class ResponseMetadata:
    """Response metadata structure."""
    
    response_id: str
    timestamp: datetime
    processing_time_ms: float
    source: str
    request_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    platform_rate_limit: Optional[Dict[str, Any]] = None
    cache_hit: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""



        return asdict(self)


class PlatformResponse(BaseModel):
    """Base model for platform responses."""
    
    response_id: str
    response_type: ResponseType
    status: ResponseStatus
    timestamp: datetime
    data: Dict[str, Any]
    metadata: ResponseMetadata
    raw_response: Optional[str] = None
    errors: List[str] = []
    warnings: List[str] = []
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
    
    @validator('response_id')
    def validate_response_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Response ID must be valid')
        return v
    
    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        return v


class YouTubeResponseModel(PlatformResponse):
    """YouTube API response model."""
    
    video_id: Optional[str] = None
    channel_id: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    revenue_data: Optional[Dict[str, Any]] = None
    content_claims: Optional[List[Dict[str, Any]]] = None
    
    @validator('video_id')
    def validate_video_id(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]{11}$', v):
            raise ValueError('Invalid YouTube video ID format')
        return v


class InstagramResponseModel(PlatformResponse):
    """Instagram API response model."""
    
    media_id: Optional[str] = None
    media_type: Optional[str] = None
    permalink: Optional[str] = None
    like_count: Optional[int] = None
    comments_count: Optional[int] = None
    insights_data: Optional[Dict[str, Any]] = None
    
    @validator('media_type')
    def validate_media_type(cls, v):
        if v and v not in ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']:
            raise ValueError('Invalid Instagram media type')
        return v


class TikTokResponseModel(PlatformResponse):
    """TikTok API response model."""
    
    video_id: Optional[str] = None
    username: Optional[str] = None
    video_description: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    share_count: Optional[int] = None
    comment_count: Optional[int] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^@?[a-zA-Z0-9_.]+$', v):
            raise ValueError('Invalid TikTok username format')
        return v


class FingerprintResponseModel(PlatformResponse):
    """Fingerprint processing response model."""
    
    content_id: int
    fingerprint_hash: str
    similarity_score: Optional[float] = None
    match_found: bool = False
    matched_content_ids: List[int] = []
    vector_embedding: Optional[str] = None  # Base64 encoded
    
    @validator('similarity_score')
    def validate_similarity_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Similarity score must be between 0 and 1')
        return v


class ResponseValidator:
    """Professional response validation system."""
    
    def __init__(self):
        self.data_validator = DataValidator()
        self.encryption_manager = EncryptionManager()
    
    async def validate_response(
        self, 
        response_data: Dict[str, Any], 
        response_type: ResponseType
    ) -> Tuple[bool, List[str], PlatformResponse]:
        """
        Validate response data against expected schema.
        
        Args:
            response_data: Raw response data
            response_type: Type of response
            
        Returns:
            Tuple of (is_valid, errors, parsed_response)
        """



        try:
            errors = []
            
            # Basic structure validation
            required_fields = ['response_id', 'timestamp', 'data']
            for field in required_fields:
                if field not in response_data:
                    errors.append(f"Missing required field: {field}")
            
            if errors:
                return False, errors, None
            
            # Get appropriate model class
            model_class = self._get_model_class(response_type)
            
            # Parse and validate
            try:
                parsed_response = model_class(**response_data)
                
                # Additional business logic validation
                validation_errors = await self._validate_business_logic(
                    parsed_response, response_type
                )
                errors.extend(validation_errors)
                
                is_valid = len(errors) == 0
                return is_valid, errors, parsed_response
                
            except ValidationError as e:
                validation_errors = [f"Validation error: {error['msg']}" for error in e.errors()]
                return False, validation_errors, None
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return False, [f"Validation exception: {e}"], None
    
    def _get_model_class(self, response_type: ResponseType) -> Type[PlatformResponse]:
        """Get appropriate response model class."""
        model_mapping = {
            ResponseType.YOUTUBE_API: YouTubeResponseModel,
            ResponseType.INSTAGRAM_API: InstagramResponseModel,
            ResponseType.TIKTOK_API: TikTokResponseModel,
            ResponseType.FINGERPRINT_RESULT: FingerprintResponseModel,
        }
        
        return model_mapping.get(response_type, PlatformResponse)
    
    async def _validate_business_logic(
        self, 
        response: PlatformResponse, 
        response_type: ResponseType
    ) -> List[str]:
        """Validate business logic rules."""
        errors = []
        
        try:
            # Platform-specific validation
            if response_type == ResponseType.YOUTUBE_API:
                errors.extend(await self._validate_youtube_response(response))
            elif response_type == ResponseType.INSTAGRAM_API:
                errors.extend(await self._validate_instagram_response(response))
            elif response_type == ResponseType.FINGERPRINT_RESULT:
                errors.extend(await self._validate_fingerprint_response(response))
            
            # Common validations
            if response.status == ResponseStatus.SUCCESS and not response.data:
                errors.append("Success status requires non-empty data")
            
            if response.metadata.processing_time_ms < 0:
                errors.append("Processing time cannot be negative")
            
        except Exception as e:
            errors.append(f"Business logic validation error: {e}")
        
        return errors
    
    async def _validate_youtube_response(self, response: YouTubeResponseModel) -> List[str]:
        """Validate YouTube-specific response data."""
        errors = []
        
        # Check for required YouTube fields
        if response.status == ResponseStatus.SUCCESS:
            if not response.video_id and not response.channel_id:
                errors.append("YouTube response must include video_id or channel_id")
            
            # Validate numeric fields
            numeric_fields = ['view_count', 'like_count', 'comment_count']
            for field in numeric_fields:
                value = getattr(response, field)
                if value is not None and value < 0:
                    errors.append(f"{field} cannot be negative")
        
        return errors
    
    async def _validate_instagram_response(self, response: InstagramResponseModel) -> List[str]:
        """Validate Instagram-specific response data."""
        errors = []
        
        if response.status == ResponseStatus.SUCCESS:
            if not response.media_id:
                errors.append("Instagram response must include media_id")
            
            if response.permalink and not response.permalink.startswith('https://'):
                errors.append("Instagram permalink must be a valid HTTPS URL")
        
        return errors
    
    async def _validate_fingerprint_response(self, response: FingerprintResponseModel) -> List[str]:
        """Validate fingerprint-specific response data."""
        errors = []
        
        if response.status == ResponseStatus.SUCCESS:
            if not response.fingerprint_hash:
                errors.append("Fingerprint response must include fingerprint_hash")
            
            if response.match_found and not response.matched_content_ids:
                errors.append("Match found but no matched_content_ids provided")
        
        return errors


class ResponseNormalizer:
    """Professional response normalization system."""
    
    def __init__(self):
        self.platform_mappings = self._load_platform_mappings()
    
    def _load_platform_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load platform field mappings for normalization."""



        return {
            'youtube': {
                'id': 'video_id',
                'snippet.title': 'title',
                'snippet.description': 'description',
                'statistics.viewCount': 'view_count',
                'statistics.likeCount': 'like_count',
                'statistics.commentCount': 'comment_count'
            },
            'instagram': {
                'id': 'media_id',
                'media_type': 'media_type',
                'permalink': 'permalink',
                'like_count': 'like_count',
                'comments_count': 'comments_count'
            },
            'tiktok': {
                'id': 'video_id',
                'author.unique_id': 'username',
                'desc': 'description',
                'stats.play_count': 'view_count',
                'stats.digg_count': 'like_count',
                'stats.share_count': 'share_count',
                'stats.comment_count': 'comment_count'
            }
        }
    
    async def normalize_response(
        self, 
        raw_data: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """
        Normalize platform response to standardized format.
        
        Args:
            raw_data: Raw platform response data
            platform: Platform name (youtube, instagram, tiktok)
            
        Returns:
            Normalized response data
        """



        try:
            if platform not in self.platform_mappings:
                return raw_data
            
            mapping = self.platform_mappings[platform]
            normalized = {}
            
            # Apply field mappings
            for source_path, target_field in mapping.items():
                value = self._extract_nested_value(raw_data, source_path)
                if value is not None:
                    normalized[target_field] = self._normalize_value(value, target_field)
            
            # Preserve original data
            normalized['_original'] = raw_data
            normalized['_platform'] = platform
            normalized['_normalized_at'] = datetime.utcnow().isoformat()
            
            return normalized
            
        except Exception as e:
            logger.error(f"Response normalization failed for {platform}: {e}")
            return raw_data
    
    def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dictionary using dot notation."""



        try:
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _normalize_value(self, value: Any, field_name: str) -> Any:
        """Normalize individual field values."""



        try:
            # Numeric fields
            if field_name.endswith('_count') or field_name in ['view_count', 'like_count']:
                return self._normalize_count(value)
            
            # URL fields
            if field_name.endswith('_url') or field_name == 'permalink':
                return self._normalize_url(value)
            
            # Text fields
            if field_name in ['title', 'description', 'username']:
                return self._normalize_text(value)
            
            # Default: return as-is
            return value
            
        except Exception as e:
            logger.warning(f"Value normalization failed for {field_name}: {e}")
            return value
    
    def _normalize_count(self, value: Any) -> int:
        """Normalize count values to integers."""
        if isinstance(value, str):
            # Handle string numbers like "1,234" or "1.2K"
            value = value.replace(',', '')
            
            # Handle abbreviated numbers (K, M, B)
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            for suffix, multiplier in multipliers.items():
                if value.upper().endswith(suffix):
                    number = float(value[:-1])
                    return int(number * multiplier)
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _normalize_url(self, value: Any) -> str:
        """Normalize URL values."""
        if not isinstance(value, str):
            return str(value)
        
        # Ensure HTTPS for security
        if value.startswith('http://'):
            value = value.replace('http://', 'https://', 1)
        elif not value.startswith('https://'):
            value = 'https://' + value.lstrip('/')
        
        return value
    
    def _normalize_text(self, value: Any) -> str:
        """Normalize text values."""
        if not isinstance(value, str):
            return str(value)
        
        # Clean and truncate text
        text = value.strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate if too long
        max_length = 5000  # Configurable
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text


class ResponseProcessor:
    """Professional response processing system."""
    
    def __init__(self):
        self.validator = ResponseValidator()
        self.normalizer = ResponseNormalizer()
        self.rate_limiter = RateLimiter()
    
    async def process_response(
        self, 
        raw_response: Dict[str, Any], 
        response_type: ResponseType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process raw response through validation, normalization, and enrichment.
        
        Args:
            raw_response: Raw response data
            response_type: Type of response
            context: Additional processing context
            
        Returns:
            Processed response data
        """



        try:
            processing_start = datetime.utcnow()
            response_id = str(uuid.uuid4())
            
            # Add metadata
            metadata = ResponseMetadata(
                response_id=response_id,
                timestamp=processing_start,
                processing_time_ms=0,
                source=context.get('source', 'unknown') if context else 'unknown',
                request_id=context.get('request_id') if context else None
            )
            
            # Prepare response structure
            response_data = {
                'response_id': response_id,
                'response_type': response_type,
                'status': ResponseStatus.SUCCESS,
                'timestamp': processing_start,
                'data': raw_response,
                'metadata': metadata,
                'errors': [],
                'warnings': []
            }
            
            # Validate response
            is_valid, validation_errors, parsed_response = await self.validator.validate_response(
                response_data, response_type
            )
            
            if not is_valid:
                response_data['status'] = ResponseStatus.FAILURE
                response_data['errors'].extend(validation_errors)
                logger.warning(f"Response validation failed: {validation_errors}")
            
            # Normalize data if validation passed
            if is_valid and context and 'platform' in context:
                normalized_data = await self.normalizer.normalize_response(
                    raw_response, context['platform']
                )
                response_data['data'] = normalized_data
            
            # Enrich with additional processing
            if is_valid:
                enrichment_data = await self._enrich_response(
                    response_data, response_type, context
                )
                response_data.update(enrichment_data)
            
            # Calculate processing time
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds() * 1000
            response_data['metadata'].processing_time_ms = processing_time
            
            # Store response
            await self._store_response(response_data)
            
            logger.info(f"Response processed successfully: {response_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Response processing failed: {e}")
            raise ResponseHandlingError(f"Failed to process response: {e}")
    
    async def _enrich_response(
        self, 
        response_data: Dict[str, Any], 
        response_type: ResponseType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enrich response with additional computed data."""
        enrichment = {}
        
        try:
            # Content-specific enrichment
            if response_type == ResponseType.FINGERPRINT_RESULT:
                enrichment.update(await self._enrich_fingerprint_response(response_data))
            elif response_type in [ResponseType.YOUTUBE_API, ResponseType.INSTAGRAM_API]:
                enrichment.update(await self._enrich_social_media_response(response_data))
            
            # Common enrichments
            enrichment['processing_quality'] = self._calculate_processing_quality(response_data)
            enrichment['data_completeness'] = self._calculate_data_completeness(response_data)
            
        except Exception as e:
            logger.warning(f"Response enrichment failed: {e}")
        
        return enrichment
    
    async def _enrich_fingerprint_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich fingerprint response with similarity analysis."""
        enrichment = {}
        
        try:
            data = response_data.get('data', {})
            
            if 'similarity_score' in data:
                score = data['similarity_score']
                enrichment['similarity_level'] = self._categorize_similarity(score)
            
            if 'matched_content_ids' in data:
                match_count = len(data['matched_content_ids'])
                enrichment['match_strength'] = 'high' if match_count > 5 else 'medium' if match_count > 1 else 'low'
            
        except Exception as e:
            logger.warning(f"Fingerprint enrichment failed: {e}")
        
        return enrichment
    
    async def _enrich_social_media_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich social media response with engagement metrics."""
        enrichment = {}
        
        try:
            data = response_data.get('data', {})
            
            # Calculate engagement rate
            view_count = data.get('view_count', 0)
            like_count = data.get('like_count', 0)
            comment_count = data.get('comment_count', 0)
            
            if view_count > 0:
                engagement_rate = (like_count + comment_count) / view_count
                enrichment['engagement_rate'] = round(engagement_rate, 4)
                enrichment['engagement_level'] = self._categorize_engagement(engagement_rate)
            
            # Viral potential
            if view_count > 1000000:  # 1M views
                enrichment['viral_potential'] = 'high'
            elif view_count > 100000:  # 100K views
                enrichment['viral_potential'] = 'medium'
            else:
                enrichment['viral_potential'] = 'low'
            
        except Exception as e:
            logger.warning(f"Social media enrichment failed: {e}")
        
        return enrichment
    
    def _categorize_similarity(self, score: float) -> str:
        """Categorize similarity score."""
        if score >= 0.9:
            return 'very_high'
        elif score >= 0.7:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _categorize_engagement(self, rate: float) -> str:
        """Categorize engagement rate."""
        if rate >= 0.1:  # 10%
            return 'exceptional'
        elif rate >= 0.05:  # 5%
            return 'high'
        elif rate >= 0.02:  # 2%
            return 'good'
        elif rate >= 0.01:  # 1%
            return 'average'
        else:
            return 'low'
    
    def _calculate_processing_quality(self, response_data: Dict[str, Any]) -> str:
        """Calculate overall processing quality."""



        try:
            error_count = len(response_data.get('errors', []))
            warning_count = len(response_data.get('warnings', []))
            
            if error_count == 0 and warning_count == 0:
                return 'excellent'
            elif error_count == 0 and warning_count <= 2:
                return 'good'
            elif error_count <= 1:
                return 'fair'
            else:
                return 'poor'
                
        except Exception:
            return 'unknown'
    
    def _calculate_data_completeness(self, response_data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage."""



        try:
            data = response_data.get('data', {})
            if not data:
                return 0.0
            
            # Count non-null values
            total_fields = len(data)
            complete_fields = sum(1 for v in data.values() if v is not None and v != '')
            
            return round(complete_fields / total_fields, 2) if total_fields > 0 else 0.0
            
        except Exception:
            return 0.0
    
    async def _store_response(self, response_data: Dict[str, Any]):
        """Store processed response in database."""



        try:
            async with async_session() as session:
                crawler_response = CrawlerResponse(
                    response_id=response_data['response_id'],
                    response_type=response_data['response_type'].value,
                    status=response_data['status'].value,
                    data=response_data['data'],
                    metadata=response_data['metadata'].to_dict(),
                    errors=response_data.get('errors', []),
                    warnings=response_data.get('warnings', []),
                    processing_time_ms=response_data['metadata'].processing_time_ms,
                    created_at=response_data['timestamp']
                )
                
                session.add(crawler_response)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to store response {response_data['response_id']}: {e}")


class ResponseHandler:
    """Main response handler orchestrating all response processing operations."""
    
    def __init__(self):
        self.processor = ResponseProcessor()
        self.rate_limiter = RateLimiter()
        logger.info("Response Handler initialized successfully")
    
    async def handle_response(
        self, 
        raw_response: Dict[str, Any], 
        response_type: ResponseType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for response handling.
        
        Args:
            raw_response: Raw response data
            response_type: Type of response
            context: Additional processing context
            
        Returns:
            Processed response result
        """



        try:
            # Rate limiting check
            source = context.get('source', 'unknown') if context else 'unknown'
            await self.rate_limiter.check_rate_limit(f"response_handler:{source}")
            
            logger.info(f"Processing {response_type.value} response from {source}")
            
            # Process response
            result = await self.processor.process_response(
                raw_response, response_type, context
            )
            
            logger.info(f"Response handling completed: {result['response_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Response handling failed: {e}")
            raise
    
    async def handle_batch_responses(
        self, 
        responses: List[Tuple[Dict[str, Any], ResponseType, Optional[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """Handle multiple responses in batch."""



        try:
            tasks = []
            for raw_response, response_type, context in responses:
                task = self.handle_response(raw_response, response_type, context)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch response {i} failed: {result}")
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch response handling failed: {e}")
            raise


# Factory function
def create_response_handler() -> ResponseHandler:
    """Create and return a ResponseHandler instance."""



    return ResponseHandler()
