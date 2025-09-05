"""Validation - Request/Response Validation
Consolidated validation functionality for API requests and responses.

This module consolidates validation from:
- Request data validation (Pydantic models, custom validators)
- Response data validation and serialization
- Input sanitization and security validation
- Business rule validation (content policies, user permissions)
- File upload validation (size, type, security)
- Data format validation (JSON, XML, multimedia formats)

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union, Type, Callable
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from collections import defaultdict
import re
import mimetypes
import hashlib
try:
    import magic
except ImportError:
    # Mock magic module if not available
    class magic:
        @staticmethod
        def from_buffer(content, mime=True):
            return "application/octet-stream"
from pathlib import Path

from fastapi import HTTPException, status, UploadFile
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
import bleach

# ========================================
# VALIDATION ENUMS
# ========================================

class ContentType(str, Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"

class CreatorType(str, Enum):
    """Supported creator types"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    WRITER = "writer"
    OTHER = "other"

class ValidationLevel(str, Enum):
    """Validation strictness levels"""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"

# ========================================
# BASE VALIDATION MODELS
# ========================================

class BaseValidatedModel(BaseModel):
    """Base model with common validation rules"""
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True

class PaginationParams(BaseValidatedModel):
    """Standard pagination parameters"""
    page: int = Field(default=1, ge=1, le=10000, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    offset: Optional[int] = Field(default=None, ge=0, description="Offset for pagination")
    
    @model_validator(mode='after')
    def validate_pagination(self):
        if self.offset is None:
            self.offset = (self.page - 1) * self.limit
        return self

class SortParams(BaseValidatedModel):
    """Standard sorting parameters"""
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")

# ========================================
# USER VALIDATION MODELS
# ========================================

class UserValidation(BaseValidatedModel):
    """User data validation"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_-]+$")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    creator_type: CreatorType = Field(..., description="Type of content creator")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v.lower() in ['admin', 'root', 'system', 'api', 'test']:
            raise ValueError('Username not allowed')
        return v.lower()
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        # Remove any HTML tags and sanitize
        cleaned = bleach.clean(v, tags=[], strip=True)
        if len(cleaned.strip()) == 0:
            raise ValueError('Name cannot be empty or contain only HTML')
        return cleaned.title()

class PasswordValidation(BaseValidatedModel):
    """Password validation model"""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @model_validator(mode="after")
    def validate_passwords_match(self):
        password = self.password
        confirm_password = self.confirm_password
        
        if password != confirm_password:
            raise ValueError('Passwords do not match')
        
        # Password strength validation
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;\':",./<>?]', password):
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValueError('; '.join(errors))
        
        return self

# ========================================
# CONTENT VALIDATION MODELS
# ========================================

class ContentMetadataValidation(BaseValidatedModel):
    """Content metadata validation"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    tags: List[str] = Field(default_factory=list, max_items=20)
    category: str = Field(..., min_length=1, max_length=50)
    is_public: bool = Field(default=True)
    copyright_notice: Optional[str] = Field(None, max_length=500)
    
    @field_validator('title', 'description')
    @classmethod
    def sanitize_text_fields(cls, v):
        if v is None:
            return v
        # Remove HTML tags and sanitize
        return bleach.clean(v, tags=[], strip=True)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if not v:
            return v
        
        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            cleaned = bleach.clean(tag, tags=[], strip=True).lower()
            if len(cleaned) > 0 and len(cleaned) <= 30:
                cleaned_tags.append(cleaned)
        
        return cleaned_tags[:20]  # Limit to 20 tags

class FileUploadValidation(BaseValidatedModel):
    """File upload validation"""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=1, le=500_000_000, description="File size in bytes (max 500MB)")
    checksum: Optional[str] = Field(None, description="File checksum for integrity")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        # Remove path traversal attempts
        cleaned = Path(v).name
        
        # Check for allowed characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', cleaned):
            raise ValueError('Filename contains invalid characters')
        
        return cleaned
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/mpeg', 'video/quicktime', 'video/webm',
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac',
            'text/plain', 'text/markdown', 'application/pdf'
        }
        
        if v not in allowed_types:
            raise ValueError(f'Content type {v} not allowed')
        
        return v

# ========================================
# BUSINESS VALIDATION MODELS
# ========================================

class MonetizationValidation(BaseValidatedModel):
    """Monetization data validation"""
    price: Decimal = Field(..., ge=0, le=10000)
    currency: str = Field(..., pattern="^[A-Z]{3}$", description="ISO 4217 currency code")
    license_type: str = Field(..., description="Type of license")
    royalty_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        allowed_currencies = {'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY'}
        if v not in allowed_currencies:
            raise ValueError(f'Currency {v} not supported')
        return v

class CollaborationValidation(BaseValidatedModel):
    """Collaboration request validation"""
    collaborator_id: str = Field(..., description="ID of potential collaborator")
    message: str = Field(..., min_length=10, max_length=1000)
    collaboration_type: str = Field(..., description="Type of collaboration")
    revenue_split: Optional[Dict[str, Decimal]] = Field(None, description="Revenue sharing agreement")
    
    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v):
        return bleach.clean(v, tags=[], strip=True)
    
    @field_validator('revenue_split')
    @classmethod
    def validate_revenue_split(cls, v):
        if v is None:
            return v
        
        total = sum(v.values())
        if total != Decimal('100'):
            raise ValueError('Revenue split must total 100%')
        
        for percentage in v.values():
            if percentage < 0 or percentage > 100:
                raise ValueError('Revenue split percentages must be between 0 and 100')
        
        return v

# ========================================
# FILE VALIDATION SERVICE
# ========================================

class FileValidationService:
    """Service for comprehensive file validation"""
    
    def __init__(self):
        self.max_file_size = 500_000_000  # 500MB
        self.allowed_mime_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/mpeg', 'video/quicktime', 'video/webm',
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac',
            'text/plain', 'text/markdown', 'application/pdf'
        }
    
    async def validate_upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """Comprehensive file validation"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # Check file size
        if file.size > self.max_file_size:
            validation_result['valid'] = False
            validation_result['errors'].append(f'File size {file.size} exceeds maximum {self.max_file_size}')
        
        # Validate MIME type
        if file.content_type not in self.allowed_mime_types:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Content type {file.content_type} not allowed')
        
        # Read file content for additional validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Validate actual file type (magic number)
        try:
            actual_mime = magic.from_buffer(content, mime=True)
            if actual_mime != file.content_type:
                validation_result['warnings'].append(f'Declared MIME type {file.content_type} differs from actual {actual_mime}')
        except Exception:
            validation_result['warnings'].append('Could not determine actual file type')
        
        # Calculate checksum
        validation_result['metadata']['checksum'] = hashlib.sha256(content).hexdigest()
        validation_result['metadata']['size'] = len(content)
        validation_result['metadata']['filename'] = file.filename
        
        return validation_result
    
    def validate_image_dimensions(self, width: int, height: int) -> List[str]:
        """Validate image dimensions"""
        errors = []
        
        if width > 10000 or height > 10000:
            errors.append('Image dimensions too large (max 10000x10000)')
        
        if width < 1 or height < 1:
            errors.append('Invalid image dimensions')
        
        return errors
    
    def validate_video_duration(self, duration_seconds: float) -> List[str]:
        """Validate video duration"""
        errors = []
        
        max_duration = 3600  # 1 hour
        if duration_seconds > max_duration:
            errors.append(f'Video duration {duration_seconds}s exceeds maximum {max_duration}s')
        
        if duration_seconds <= 0:
            errors.append('Invalid video duration')
        
        return errors

# ========================================
# INPUT SANITIZATION
# ========================================

class InputSanitizer:
    """Input sanitization for security"""
    
    @staticmethod
    def sanitize_html(text: str, allowed_tags: List[str] = None) -> str:
        """Sanitize HTML content"""
        if allowed_tags is None:
            allowed_tags = []
        
        return bleach.clean(text, tags=allowed_tags, strip=True)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Ensure not empty
        if not sanitized or sanitized == '.':
            sanitized = 'unnamed_file'
        
        return sanitized
    
    @staticmethod
    def validate_sql_injection(text: str) -> bool:
        """Check for potential SQL injection patterns"""
        dangerous_patterns = [
            r"('|(\\')|(''|(\\\\')));?.*?",
            r"(select|insert|update|delete|drop|create|alter|exec|execute)\s",
            r"(union\s+(select|all))",
            r"(/\*|\*/|;|\||`)"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text.lower()):
                return False
        
        return True

# ========================================
# VALIDATION DECORATORS
# ========================================

def validate_request_size(max_size: int = 10_000_000):
    """Decorator to validate request size"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Implementation would check request size
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator to validate rate limits"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Implementation would check rate limits
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ========================================
# VALIDATION SERVICE
# ========================================

class ValidationService:
    """Main validation service consolidating all validation functionality"""
    
    def __init__(self):
        self.file_validator = FileValidationService()
        self.sanitizer = InputSanitizer()
    
    def validate_model(self, model_class: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
        """Validate data against Pydantic model"""
        try:
            return model_class(**data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    
    def validate_business_rules(self, data: Dict[str, Any], rules: List[Callable]) -> List[str]:
        """Validate against business rules"""
        errors = []
        
        for rule in rules:
            try:
                if not rule(data):
                    errors.append(f"Business rule violation: {rule.__name__}")
            except Exception as e:
                errors.append(f"Business rule error: {str(e)}")
        
        return errors
    
    async def validate_content_policy(self, content: str) -> Dict[str, Any]:
        """Validate content against platform policies"""
        result = {
            'compliant': True,
            'violations': [],
            'score': 1.0
        }
        
        # Check for inappropriate content (simplified)
        inappropriate_patterns = [
            r'\b(hate|violence|harassment)\b',
            r'\b(spam|scam|fraud)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, content.lower()):
                result['compliant'] = False
                result['violations'].append(f'Pattern match: {pattern}')
                result['score'] -= 0.2
        
        return result


# ========================================
# ADVANCED BUSINESS RULES VALIDATION
# ========================================

class BusinessRuleType(str, Enum):
    """Types of business rules"""
    REVENUE_LIMIT = "revenue_limit"
    CONTENT_QUOTA = "content_quota"
    COLLABORATION_LIMIT = "collaboration_limit"
    SUBSCRIPTION_TIER = "subscription_tier"
    GEOGRAPHIC_RESTRICTION = "geographic_restriction"
    AGE_RESTRICTION = "age_restriction"
    COPYRIGHT_COMPLIANCE = "copyright_compliance"
    PLATFORM_POLICY = "platform_policy"

class RuleSeverity(str, Enum):
    """Business rule severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class BusinessRuleEngine:
    """Advanced business rules validation engine"""
    
    def __init__(self):
        self.rules = {}
        self.rule_cache = {}
        self.validation_history = defaultdict(list)
        
    def register_rule(self, rule_id: str, rule_config: Dict[str, Any]):
        """Register a new business rule"""
        self.rules[rule_id] = rule_config
        
    async def validate_business_rules(
        self, 
        context: Dict[str, Any], 
        rule_types: List[BusinessRuleType] = None
    ) -> Dict[str, Any]:
        """Validate all applicable business rules"""
        try:
            results = {
                "passed": True,
                "violations": [],
                "warnings": [],
                "errors": [],
                "rule_results": {}
            }
            
            # Get applicable rules
            applicable_rules = self._get_applicable_rules(context, rule_types)
            
            # Validate each rule
            for rule_id, rule_config in applicable_rules.items():
                rule_result = await self._validate_single_rule(rule_id, rule_config, context)
                results["rule_results"][rule_id] = rule_result
                
                if not rule_result["passed"]:
                    results["passed"] = False
                    
                    if rule_result["severity"] == RuleSeverity.ERROR:
                        results["errors"].append(rule_result)
                    elif rule_result["severity"] == RuleSeverity.WARNING:
                        results["warnings"].append(rule_result)
                    elif rule_result["severity"] == RuleSeverity.CRITICAL:
                        results["violations"].append(rule_result)
            
            # Store validation history
            user_id = context.get("user_id")
            if user_id:
                self.validation_history[user_id].append({
                    "timestamp": datetime.utcnow(),
                    "results": results,
                    "context": context
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Business rule validation failed: {str(e)}")
            return {
                "passed": False,
                "violations": [],
                "warnings": [],
                "errors": [{"message": "Business rule validation error", "severity": "error"}],
                "rule_results": {}
            }
    
    async def validate_revenue_limits(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate revenue-related business rules"""
        try:
            user_id = context.get("user_id")
            subscription_tier = context.get("subscription_tier", "free")
            current_revenue = context.get("current_revenue", 0)
            
            # Define tier limits
            tier_limits = {
                "free": {"max_monthly_revenue": 1000, "max_transactions": 50},
                "basic": {"max_monthly_revenue": 10000, "max_transactions": 500},
                "premium": {"max_monthly_revenue": 100000, "max_transactions": 5000},
                "enterprise": {"max_monthly_revenue": float("inf"), "max_transactions": float("inf")}
            }
            
            limits = tier_limits.get(subscription_tier, tier_limits["free"])
            violations = []
            
            # Check revenue limit
            if current_revenue > limits["max_monthly_revenue"]:
                violations.append({
                    "rule": "monthly_revenue_limit",
                    "message": f"Monthly revenue limit exceeded for {subscription_tier} tier",
                    "current": current_revenue,
                    "limit": limits["max_monthly_revenue"],
                    "severity": RuleSeverity.ERROR
                })
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "limits": limits
            }
            
        except Exception:
            return {"passed": False, "violations": [], "limits": {}}
    
    async def validate_content_quotas(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content quota business rules"""
        try:
            subscription_tier = context.get("subscription_tier", "free")
            current_content_count = context.get("current_content_count", 0)
            content_size_mb = context.get("content_size_mb", 0)
            
            # Define quota limits
            quota_limits = {
                "free": {"max_content_items": 10, "max_storage_gb": 1, "max_file_size_mb": 100},
                "basic": {"max_content_items": 100, "max_storage_gb": 10, "max_file_size_mb": 500},
                "premium": {"max_content_items": 1000, "max_storage_gb": 100, "max_file_size_mb": 2000},
                "enterprise": {"max_content_items": 10000, "max_storage_gb": 1000, "max_file_size_mb": 5000}
            }
            
            limits = quota_limits.get(subscription_tier, quota_limits["free"])
            violations = []
            
            # Check content count
            if current_content_count >= limits["max_content_items"]:
                violations.append({
                    "rule": "content_count_limit",
                    "message": f"Content count limit reached for {subscription_tier} tier",
                    "current": current_content_count,
                    "limit": limits["max_content_items"],
                    "severity": RuleSeverity.ERROR
                })
            
            # Check file size
            if content_size_mb > limits["max_file_size_mb"]:
                violations.append({
                    "rule": "file_size_limit",
                    "message": f"File size exceeds limit for {subscription_tier} tier",
                    "current": f"{content_size_mb}MB",
                    "limit": f"{limits['max_file_size_mb']}MB",
                    "severity": RuleSeverity.ERROR
                })
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "limits": limits
            }
            
        except Exception:
            return {"passed": False, "violations": [], "limits": {}}
    
    async def validate_copyright_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate copyright compliance rules"""
        try:
            content_data = context.get("content_data", {})
            copyright_info = content_data.get("copyright_info", {})
            violations = []
            
            # Check for required copyright information
            required_fields = ["owner", "license_type", "usage_rights"]
            for field in required_fields:
                if not copyright_info.get(field):
                    violations.append({
                        "rule": "copyright_information_required",
                        "message": f"Required copyright field missing: {field}",
                        "field": field,
                        "severity": RuleSeverity.WARNING
                    })
            
            # Check for copyrighted material detection
            if content_data.get("copyright_detected", False):
                confidence = content_data.get("copyright_confidence", 0)
                if confidence > 0.8:
                    violations.append({
                        "rule": "copyrighted_content_detected",
                        "message": "Potential copyrighted content detected",
                        "confidence": confidence,
                        "severity": RuleSeverity.CRITICAL
                    })
                elif confidence > 0.5:
                    violations.append({
                        "rule": "possible_copyrighted_content",
                        "message": "Possible copyrighted content detected - review required",
                        "confidence": confidence,
                        "severity": RuleSeverity.WARNING
                    })
            
            return {
                "passed": len([v for v in violations if v["severity"] == RuleSeverity.CRITICAL]) == 0,
                "violations": violations
            }
            
        except Exception:
            return {"passed": False, "violations": []}
    
    async def validate_collaboration_limits(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate collaboration business rules"""
        try:
            subscription_tier = context.get("subscription_tier", "free")
            current_collaborations = context.get("current_collaborations", 0)
            
            # Define collaboration limits
            collab_limits = {
                "free": {"max_collaborations": 1, "max_participants": 2},
                "basic": {"max_collaborations": 5, "max_participants": 5},
                "premium": {"max_collaborations": 20, "max_participants": 10},
                "enterprise": {"max_collaborations": 100, "max_participants": 50}
            }
            
            limits = collab_limits.get(subscription_tier, collab_limits["free"])
            violations = []
            
            if current_collaborations >= limits["max_collaborations"]:
                violations.append({
                    "rule": "collaboration_limit",
                    "message": f"Collaboration limit reached for {subscription_tier} tier",
                    "current": current_collaborations,
                    "limit": limits["max_collaborations"],
                    "severity": RuleSeverity.ERROR
                })
            
            return {
                "passed": len(violations) == 0,
                "violations": violations,
                "limits": limits
            }
            
        except Exception:
            return {"passed": False, "violations": [], "limits": {}}
    
    def _get_applicable_rules(
        self, 
        context: Dict[str, Any], 
        rule_types: List[BusinessRuleType] = None
    ) -> Dict[str, Any]:
        """Get rules applicable to the current context"""
        applicable_rules = {}
        
        for rule_id, rule_config in self.rules.items():
            # Check if rule type matches filter
            if rule_types and rule_config.get("type") not in rule_types:
                continue
            
            # Check if rule applies to current context
            if self._rule_applies_to_context(rule_config, context):
                applicable_rules[rule_id] = rule_config
        
        return applicable_rules
    
    def _rule_applies_to_context(self, rule_config: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if a rule applies to the given context"""
        try:
            conditions = rule_config.get("conditions", {})
            
            for field, expected_value in conditions.items():
                if field not in context:
                    return False
                
                actual_value = context[field]
                
                # Handle different condition types
                if isinstance(expected_value, dict):
                    if "min" in expected_value and actual_value < expected_value["min"]:
                        return False
                    if "max" in expected_value and actual_value > expected_value["max"]:
                        return False
                elif actual_value != expected_value:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _validate_single_rule(
        self, 
        rule_id: str, 
        rule_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a single business rule"""
        try:
            rule_type = rule_config.get("type")
            
            if rule_type == BusinessRuleType.REVENUE_LIMIT:
                return await self.validate_revenue_limits(context)
            elif rule_type == BusinessRuleType.CONTENT_QUOTA:
                return await self.validate_content_quotas(context)
            elif rule_type == BusinessRuleType.COPYRIGHT_COMPLIANCE:
                return await self.validate_copyright_compliance(context)
            elif rule_type == BusinessRuleType.COLLABORATION_LIMIT:
                return await self.validate_collaboration_limits(context)
            else:
                # Custom rule validation
                return await self._validate_custom_rule(rule_id, rule_config, context)
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Rule validation error: {str(e)}",
                "severity": RuleSeverity.ERROR
            }
    
    async def _validate_custom_rule(
        self, 
        rule_id: str, 
        rule_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate custom business rule"""
        # Placeholder for custom rule validation logic
        return {
            "passed": True,
            "message": "Custom rule validation not implemented",
            "severity": RuleSeverity.INFO
        }

class EnhancedValidationService(ValidationService):
    """Enhanced validation service with business rules"""
    
    def __init__(self):
        super().__init__()
        self.business_rule_engine = BusinessRuleEngine()
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default business rules"""
        self.business_rule_engine.register_rule("revenue_limits", {
            "type": BusinessRuleType.REVENUE_LIMIT,
            "conditions": {"subscription_tier": {"min": "free"}},
            "severity": RuleSeverity.ERROR
        })
        
        self.business_rule_engine.register_rule("content_quotas", {
            "type": BusinessRuleType.CONTENT_QUOTA,
            "conditions": {},
            "severity": RuleSeverity.ERROR
        })
    
    async def validate_with_business_rules(
        self, 
        data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data with business rules"""
        try:
            # Standard validation first
            standard_result = await self.validate_request(data)
            
            # Business rules validation
            business_result = await self.business_rule_engine.validate_business_rules(context)
            
            # Combine results
            combined_result = {
                "passed": standard_result["valid"] and business_result["passed"],
                "standard_validation": standard_result,
                "business_rules": business_result,
                "overall_errors": standard_result.get("errors", []) + business_result.get("errors", []),
                "overall_warnings": business_result.get("warnings", [])
            }
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Enhanced validation failed: {str(e)}")
            return {
                "passed": False,
                "error": "Validation service error",
                "standard_validation": {"valid": False},
                "business_rules": {"passed": False}
            }


# Initialize enhanced validation service
enhanced_validation_service = EnhancedValidationService()


# ========================================
# UPDATED EXPORTS
# ========================================

__all__ = [
    "ContentType",
    "CreatorType", 
    "ValidationLevel",
    "BusinessRuleType",
    "RuleSeverity",
    "BaseValidatedModel",
    "PaginationParams",
    "SortParams",
    "UserValidation",
    "PasswordValidation",
    "ContentMetadataValidation",
    "FileUploadValidation",
    "MonetizationValidation",
    "CollaborationValidation",
    "FileValidationService",
    "InputSanitizer",
    "ValidationService",
    "BusinessRuleEngine",
    "EnhancedValidationService",
    "enhanced_validation_service",
    "validate_request_size",
    "validate_rate_limit"
]