"""Parsing Exceptions Module
========================

Custom exceptions for content parsing operations in the IA Influencer Agent platform.
Provides detailed error handling for various parsing scenarios.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""

from typing import Optional, Dict, Any


class ParsingError(Exception):
    """
Base exception for all parsing-related errors"""
    
    def __init__(
        self, 
        message: str, 
        parser_type: Optional[str] = None,
        content_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.parser_type = parser_type
        self.content_type = content_type
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_parts = [self.message]
        
        if self.parser_type:
            error_parts.append(f"Parser: {self.parser_type}")
        
        if self.content_type:
            error_parts.append(f"Content Type: {self.content_type}")
        
        if self.details:
            error_parts.append(f"Details: {self.details}")
        
        return " | ".join(error_parts)


class UnsupportedFormatError(ParsingError):
    """Raised when attempting to parse an unsupported format"""
    
    def __init__(
        self, 
        format_type: str, 
        supported_formats: Optional[list] = None,
        parser_type: Optional[str] = None
    ):
        self.format_type = format_type
        self.supported_formats = supported_formats or []
        
        message = f"Unsupported format: {format_type}"
        if self.supported_formats:
            message += f". Supported formats: {', '.join(self.supported_formats)}"
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            content_type=format_type,
            details={"supported_formats": self.supported_formats}
        )


class ValidationError(ParsingError):
    """Raised when content validation fails during parsing"""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        parser_type: Optional[str] = None
    ):
        self.field = field
        self.expected_type = expected_type
        self.actual_value = actual_value
        
        details = {}
        if field:
            details["field"] = field
        if expected_type:
            details["expected_type"] = expected_type
        if actual_value is not None:
            details["actual_value"] = str(actual_value)
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class ContentExtractionError(ParsingError):
    """Raised when content extraction fails"""
    
    def __init__(
        self, 
        message: str, 
        extraction_method: Optional[str] = None,
        source_url: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.extraction_method = extraction_method
        self.source_url = source_url
        
        details = {}
        if extraction_method:
            details["extraction_method"] = extraction_method
        if source_url:
            details["source_url"] = source_url
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class MetadataParsingError(ParsingError):
    """Raised when metadata parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        metadata_type: Optional[str] = None,
        missing_fields: Optional[list] = None,
        parser_type: Optional[str] = None
    ):
        self.metadata_type = metadata_type
        self.missing_fields = missing_fields or []
        
        details = {}
        if metadata_type:
            details["metadata_type"] = metadata_type
        if self.missing_fields:
            details["missing_fields"] = self.missing_fields
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class PlatformParsingError(ParsingError):
    """Raised when platform-specific parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        platform: Optional[str] = None,
        api_error: Optional[str] = None,
        rate_limited: bool = False,
        parser_type: Optional[str] = None
    ):
        self.platform = platform
        self.api_error = api_error
        self.rate_limited = rate_limited
        
        details = {}
        if platform:
            details["platform"] = platform
        if api_error:
            details["api_error"] = api_error
        if rate_limited:
            details["rate_limited"] = rate_limited
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class MediaParsingError(ParsingError):
    """Raised when media file parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        media_type: Optional[str] = None,
        file_size: Optional[int] = None,
        codec_error: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.media_type = media_type
        self.file_size = file_size
        self.codec_error = codec_error
        
        details = {}
        if media_type:
            details["media_type"] = media_type
        if file_size:
            details["file_size"] = file_size
        if codec_error:
            details["codec_error"] = codec_error
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class FingerprintParsingError(ParsingError):
    """Raised when fingerprint generation/parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        fingerprint_type: Optional[str] = None,
        algorithm: Optional[str] = None,
        content_quality: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.fingerprint_type = fingerprint_type
        self.algorithm = algorithm
        self.content_quality = content_quality
        
        details = {}
        if fingerprint_type:
            details["fingerprint_type"] = fingerprint_type
        if algorithm:
            details["algorithm"] = algorithm
        if content_quality:
            details["content_quality"] = content_quality
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class AnalyticsParsingError(ParsingError):
    """Raised when analytics data parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        analytics_platform: Optional[str] = None,
        date_range: Optional[str] = None,
        metric_type: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.analytics_platform = analytics_platform
        self.date_range = date_range
        self.metric_type = metric_type
        
        details = {}
        if analytics_platform:
            details["analytics_platform"] = analytics_platform
        if date_range:
            details["date_range"] = date_range
        if metric_type:
            details["metric_type"] = metric_type
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class RevenueParsingError(ParsingError):
    """Raised when revenue data parsing fails"""
    
    def __init__(
        self, 
        message: str, 
        revenue_platform: Optional[str] = None,
        currency: Optional[str] = None,
        period: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.revenue_platform = revenue_platform
        self.currency = currency
        self.period = period
        
        details = {}
        if revenue_platform:
            details["revenue_platform"] = revenue_platform
        if currency:
            details["currency"] = currency
        if period:
            details["period"] = period
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class TimeoutError(ParsingError):
    """Raised when parsing operations timeout"""
    
    def __init__(
        self, 
        message: str, 
        timeout_duration: Optional[float] = None,
        operation: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.timeout_duration = timeout_duration
        self.operation = operation
        
        details = {}
        if timeout_duration:
            details["timeout_duration"] = timeout_duration
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class RateLimitError(ParsingError):
    """Raised when API rate limits are exceeded"""
    
    def __init__(
        self, 
        message: str, 
        platform: Optional[str] = None,
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
        parser_type: Optional[str] = None
    ):
        self.platform = platform
        self.retry_after = retry_after
        self.limit_type = limit_type
        
        details = {}
        if platform:
            details["platform"] = platform
        if retry_after:
            details["retry_after"] = retry_after
        if limit_type:
            details["limit_type"] = limit_type
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )


class AuthenticationError(ParsingError):
    """Raised when authentication fails for platform APIs"""
    
    def __init__(
        self, 
        message: str, 
        platform: Optional[str] = None,
        auth_type: Optional[str] = None,
        expired: bool = False,
        parser_type: Optional[str] = None
    ):
        self.platform = platform
        self.auth_type = auth_type
        self.expired = expired
        
        details = {}
        if platform:
            details["platform"] = platform
        if auth_type:
            details["auth_type"] = auth_type
        if expired:
            details["expired"] = expired
        
        super().__init__(
            message=message,
            parser_type=parser_type,
            details=details
        )
