"""
Data Validation Utilities
=========================

Comprehensive validation functions for model data.
Provides business logic validation, data integrity checks, and custom validators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import re
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException
import validators as url_validators

# Import enums for validation
from . import (
    ContentType, ContentStatus, ContentVisibility,
    UserType, UserStatus, SubscriptionTier,
    FingerprintType, FingerprintAlgorithm, FingerprintStatus,
    RevenueSource, RevenueStatus, PaymentMethod,
    AnalyticsType, MetricType, TimeGranularity,
    ProtectionType, ViolationType, SeverityLevel, ProtectionStatus,
    LicenseType, LicenseCategory, UsageType, LicenseStatus
)


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class ValidationResult:
    """Result of validation process"""
    def __init__(self):
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error"""
        self.is_valid = False
        self.errors.append({
            'field': field,
            'message': message,
            'value': value
        })
    
    def add_warning(self, field: str, message: str, value: Any = None):
        """Add validation warning"""
        self.warnings.append({
            'field': field,
            'message': message,
            'value': value
        })
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages"""



        return [f"{error['field']}: {error['message']}" for error in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Get all warning messages"""



        return [f"{warning['field']}: {warning['message']}" for warning in self.warnings]


class BaseValidator:
    """Base validator class"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> bool:
        """Validate required field"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValidationError(field_name, "This field is required")
        return True
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, 
                             min_length: int = 0, max_length: int = None) -> bool:
        """Validate string length"""
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", value)
        
        length = len(value)
        
        if length < min_length:
            raise ValidationError(
                field_name, 
                f"Must be at least {min_length} characters long", 
                value
            )
        
        if max_length and length > max_length:
            raise ValidationError(
                field_name, 
                f"Must be no more than {max_length} characters long", 
                value
            )
        
        return True
    
    @staticmethod
    def validate_email(value: str, field_name: str) -> bool:
        """Validate email address"""



        try:
            valid = validate_email(value)
            return True
        except EmailNotValidError as e:
            raise ValidationError(field_name, f"Invalid email address: {str(e)}", value)
    
    @staticmethod
    def validate_phone(value: str, field_name: str, region: str = None) -> bool:
        """Validate phone number"""



        try:
            parsed = phonenumbers.parse(value, region)
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError(field_name, "Invalid phone number", value)
            return True
        except NumberParseException as e:
            raise ValidationError(field_name, f"Invalid phone number: {str(e)}", value)
    
    @staticmethod
    def validate_url(value: str, field_name: str) -> bool:
        """Validate URL"""
        if not url_validators.url(value):
            raise ValidationError(field_name, "Invalid URL format", value)
        return True
    
    @staticmethod
    def validate_uuid(value: str, field_name: str) -> bool:
        """Validate UUID format"""



        try:
            uuid.UUID(value)
            return True
        except ValueError:
            raise ValidationError(field_name, "Invalid UUID format", value)
    
    @staticmethod
    def validate_decimal(value: Union[str, float, Decimal], field_name: str,
                        min_value: Decimal = None, max_value: Decimal = None,
                        decimal_places: int = None) -> bool:
        """Validate decimal value"""



        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValidationError(field_name, "Invalid decimal format", value)
        
        if min_value is not None and decimal_value < min_value:
            raise ValidationError(
                field_name, 
                f"Must be at least {min_value}", 
                value
            )
        
        if max_value is not None and decimal_value > max_value:
            raise ValidationError(
                field_name, 
                f"Must be no more than {max_value}", 
                value
            )
        
        if decimal_places is not None:
            # Check decimal places
            sign, digits, exponent = decimal_value.as_tuple()
            if exponent < -decimal_places:
                raise ValidationError(
                    field_name, 
                    f"Cannot have more than {decimal_places} decimal places", 
                    value
                )
        
        return True
    
    @staticmethod
    def validate_date_range(value: date, field_name: str,
                           min_date: date = None, max_date: date = None) -> bool:
        """Validate date range"""
        if min_date and value < min_date:
            raise ValidationError(
                field_name, 
                f"Date must be after {min_date}", 
                value
            )
        
        if max_date and value > max_date:
            raise ValidationError(
                field_name, 
                f"Date must be before {max_date}", 
                value
            )
        
        return True
    
    @staticmethod
    def validate_enum(value: str, field_name: str, enum_class) -> bool:
        """Validate enum value"""
        valid_values = [item.value for item in enum_class]
        if value not in valid_values:
            raise ValidationError(
                field_name, 
                f"Must be one of: {', '.join(valid_values)}", 
                value
            )
        return True


class UserValidator(BaseValidator):
    """User model specific validator"""
    
    def validate_user_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate complete user data"""
        result = ValidationResult()
        
        try:
            # Required fields
            self.validate_required(data.get('username'), 'username')
            self.validate_required(data.get('email'), 'email')
            self.validate_required(data.get('password_hash'), 'password_hash')
            
            # Username validation
            username = data.get('username')
            if username:
                self.validate_string_length(username, 'username', 3, 50)
                if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                    result.add_error('username', 'Can only contain letters, numbers, hyphens and underscores')
            
            # Email validation
            email = data.get('email')
            if email:
                self.validate_email(email, 'email')
            
            # User type validation
            user_type = data.get('user_type')
            if user_type:
                self.validate_enum(user_type, 'user_type', UserType)
            
            # Subscription tier validation
            subscription_tier = data.get('subscription_tier')
            if subscription_tier:
                self.validate_enum(subscription_tier, 'subscription_tier', SubscriptionTier)
            
            # Status validation
            status = data.get('status')
            if status:
                self.validate_enum(status, 'status', UserStatus)
            
            # Phone validation
            phone = data.get('phone_number')
            if phone:
                self.validate_phone(phone, 'phone_number')
            
            # Date of birth validation
            dob = data.get('date_of_birth')
            if dob:
                min_date = date.today() - timedelta(days=365*120)  # 120 years ago
                max_date = date.today() - timedelta(days=365*13)   # 13 years ago
                self.validate_date_range(dob, 'date_of_birth', min_date, max_date)
            
            # Business validations
            if data.get('is_verified') and not data.get('email_verified_at'):
                result.add_warning('email_verified_at', 'Verified users should have email verification date')
            
            if subscription_tier == SubscriptionTier.PREMIUM.value and not data.get('subscription_start_date'):
                result.add_warning('subscription_start_date', 'Premium users should have subscription start date')
        
        except ValidationError as e:
            result.add_error(e.field, e.message, e.value)
        
        return result


class ContentValidator(BaseValidator):
    """Content model specific validator"""
    
    def validate_content_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate complete content data"""
        result = ValidationResult()
        
        try:
            # Required fields
            self.validate_required(data.get('user_id'), 'user_id')
            self.validate_required(data.get('title'), 'title')
            self.validate_required(data.get('content_type'), 'content_type')
            
            # UUID validation
            user_id = data.get('user_id')
            if user_id:
                self.validate_uuid(user_id, 'user_id')
            
            # Title validation
            title = data.get('title')
            if title:
                self.validate_string_length(title, 'title', 1, 200)
            
            # Content type validation
            content_type = data.get('content_type')
            if content_type:
                self.validate_enum(content_type, 'content_type', ContentType)
            
            # Status validation
            status = data.get('status')
            if status:
                self.validate_enum(status, 'status', ContentStatus)
            
            # Visibility validation
            visibility = data.get('visibility')
            if visibility:
                self.validate_enum(visibility, 'visibility', ContentVisibility)
            
            # Numeric validations
            duration = data.get('duration_seconds')
            if duration is not None:
                if duration < 0:
                    result.add_error('duration_seconds', 'Duration cannot be negative')
                elif duration > 86400:  # 24 hours
                    result.add_warning('duration_seconds', 'Duration is unusually long (>24 hours)')
            
            file_size = data.get('file_size_bytes')
            if file_size is not None:
                if file_size < 0:
                    result.add_error('file_size_bytes', 'File size cannot be negative')
                elif file_size > 50 * 1024 * 1024 * 1024:  # 50GB
                    result.add_warning('file_size_bytes', 'File size is very large (>50GB)')
            
            # Count validations
            for count_field in ['view_count', 'like_count', 'comment_count', 'share_count']:
                count_value = data.get(count_field)
                if count_value is not None and count_value < 0:
                    result.add_error(count_field, 'Count cannot be negative')
            
            # Revenue validation
            revenue = data.get('revenue_total')
            if revenue is not None:
                self.validate_decimal(revenue, 'revenue_total', Decimal('0'), decimal_places=2)
            
            # URL validations
            for url_field in ['original_url', 'thumbnail_url']:
                url_value = data.get(url_field)
                if url_value:
                    self.validate_url(url_value, url_field)
            
            # Business logic validations
            if status == ContentStatus.PUBLISHED.value and not data.get('published_at'):
                result.add_warning('published_at', 'Published content should have publication date')
            
            if visibility == ContentVisibility.PRIVATE.value and data.get('view_count', 0) > 0:
                result.add_warning('view_count', 'Private content should not have public views')
        
        except ValidationError as e:
            result.add_error(e.field, e.message, e.value)
        
        return result


class RevenueValidator(BaseValidator):
    """Revenue model specific validator"""
    
    def validate_revenue_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate complete revenue data"""
        result = ValidationResult()
        
        try:
            # Required fields
            self.validate_required(data.get('user_id'), 'user_id')
            self.validate_required(data.get('revenue_source'), 'revenue_source')
            self.validate_required(data.get('gross_amount'), 'gross_amount')
            
            # UUID validations
            for uuid_field in ['user_id', 'content_id']:
                uuid_value = data.get(uuid_field)
                if uuid_value:
                    self.validate_uuid(uuid_value, uuid_field)
            
            # Enum validations
            revenue_source = data.get('revenue_source')
            if revenue_source:
                self.validate_enum(revenue_source, 'revenue_source', RevenueSource)
            
            status = data.get('status')
            if status:
                self.validate_enum(status, 'status', RevenueStatus)
            
            payment_method = data.get('payment_method')
            if payment_method:
                self.validate_enum(payment_method, 'payment_method', PaymentMethod)
            
            # Amount validations
            gross_amount = data.get('gross_amount')
            if gross_amount is not None:
                self.validate_decimal(gross_amount, 'gross_amount', Decimal('0'), decimal_places=2)
            
            platform_fee = data.get('platform_fee')
            if platform_fee is not None:
                self.validate_decimal(platform_fee, 'platform_fee', Decimal('0'), decimal_places=2)
            
            net_amount = data.get('net_amount')
            if net_amount is not None:
                self.validate_decimal(net_amount, 'net_amount', Decimal('0'), decimal_places=2)
            
            # Business logic validations
            if gross_amount and platform_fee and net_amount:
                expected_net = gross_amount - platform_fee
                if abs(expected_net - net_amount) > Decimal('0.01'):  # Allow 1 cent tolerance
                    result.add_error('net_amount', 
                                   f'Net amount should equal gross ({gross_amount}) minus fee ({platform_fee})')
            
            # CPM/CPC validations
            cpm = data.get('cpm')
            if cpm is not None:
                self.validate_decimal(cpm, 'cpm', Decimal('0'), Decimal('1000'), decimal_places=2)
            
            cpc = data.get('cpc')
            if cpc is not None:
                self.validate_decimal(cpc, 'cpc', Decimal('0'), Decimal('100'), decimal_places=2)
            
            # Currency validation
            currency = data.get('currency')
            if currency:
                if len(currency) != 3 or not currency.isupper():
                    result.add_error('currency', 'Currency must be 3-letter uppercase code (e.g., USD)')
            
        except ValidationError as e:
            result.add_error(e.field, e.message, e.value)
        
        return result


class AnalyticsValidator(BaseValidator):
    """Analytics model specific validator"""
    
    def validate_analytics_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate complete analytics data"""
        result = ValidationResult()
        
        try:
            # Required fields
            self.validate_required(data.get('user_id'), 'user_id')
            self.validate_required(data.get('analytics_type'), 'analytics_type')
            self.validate_required(data.get('metric_type'), 'metric_type')
            self.validate_required(data.get('value'), 'value')
            
            # UUID validations
            for uuid_field in ['user_id', 'content_id']:
                uuid_value = data.get(uuid_field)
                if uuid_value:
                    self.validate_uuid(uuid_value, uuid_field)
            
            # Enum validations
            analytics_type = data.get('analytics_type')
            if analytics_type:
                self.validate_enum(analytics_type, 'analytics_type', AnalyticsType)
            
            metric_type = data.get('metric_type')
            if metric_type:
                self.validate_enum(metric_type, 'metric_type', MetricType)
            
            time_granularity = data.get('time_granularity')
            if time_granularity:
                self.validate_enum(time_granularity, 'time_granularity', TimeGranularity)
            
            # Value validation
            value = data.get('value')
            if value is not None:
                self.validate_decimal(value, 'value', Decimal('0'), decimal_places=4)
            
            # Date validation
            measurement_date = data.get('measurement_date')
            if measurement_date:
                future_limit = date.today() + timedelta(days=1)
                past_limit = date.today() - timedelta(days=365*5)  # 5 years ago
                self.validate_date_range(measurement_date, 'measurement_date', past_limit, future_limit)
        
        except ValidationError as e:
            result.add_error(e.field, e.message, e.value)
        
        return result


class ModelDataValidator:
    """Main validator class that orchestrates all model validations"""
    
    def __init__(self):
        self.user_validator = UserValidator()
        self.content_validator = ContentValidator()
        self.revenue_validator = RevenueValidator()
        self.analytics_validator = AnalyticsValidator()
    
    def validate_model_data(self, model_name: str, data: Dict[str, Any]) -> ValidationResult:
        """Validate data for any model"""
        validators = {
            'UserModel': self.user_validator.validate_user_data,
            'ContentModel': self.content_validator.validate_content_data,
            'RevenueModel': self.revenue_validator.validate_revenue_data,
            'AnalyticsModel': self.analytics_validator.validate_analytics_data,
        }
        
        validator_func = validators.get(model_name)
        if validator_func:
            return validator_func(data)
        else:
            # Generic validation for models without specific validators
            result = ValidationResult()
            result.add_warning('validation', f'No specific validator for {model_name}')
            return result
    
    def validate_cross_model_relationships(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate relationships between models"""
        result = ValidationResult()
        
        # Example: Check if user exists when creating content
        if 'ContentModel' in data and 'UserModel' not in data:
            user_id = data['ContentModel'].get('user_id')
            if user_id:
                result.add_warning('user_id', 'Referenced user should exist')
        
        # Add more cross-model validations as needed
        
        return result


# Convenience functions
def validate_user(data: Dict[str, Any]) -> ValidationResult:
    """Quick user validation"""



    return UserValidator().validate_user_data(data)

def validate_content(data: Dict[str, Any]) -> ValidationResult:
    """Quick content validation"""



    return ContentValidator().validate_content_data(data)

def validate_revenue(data: Dict[str, Any]) -> ValidationResult:
    """Quick revenue validation"""



    return RevenueValidator().validate_revenue_data(data)

def validate_analytics(data: Dict[str, Any]) -> ValidationResult:
    """Quick analytics validation"""



    return AnalyticsValidator().validate_analytics_data(data)


# Export all validators
__all__ = [
    'ValidationError',
    'ValidationResult',
    'BaseValidator',
    'UserValidator',
    'ContentValidator',
    'RevenueValidator',
    'AnalyticsValidator',
    'ModelDataValidator',
    'validate_user',
    'validate_content',
    'validate_revenue',
    'validate_analytics'
]
