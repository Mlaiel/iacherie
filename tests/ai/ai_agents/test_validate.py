# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive Tests for Validation Framework

Industrial-grade testing for data validation, schema validation,
business rule validation, and integrity checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union
import logging
from decimal import Decimal
from uuid import UUID

from ai.ai_agents.validate import (
    DataValidator,
    SchemaValidator,
    BusinessRuleValidator,
    IntegrityValidator,
    ValidationResult,
    ValidationRule,
    ValidationContext,
    FieldValidator,
    CompoundValidator,
    AsyncValidator,
    ValidationError,
    ValidationWarning
)

logger = logging.getLogger(__name__)


class TestDataValidator:
    """Test data validation functionality"""
    
    @pytest.fixture
    def data_validator(self):
        """Create data validator for testing"""
        return DataValidator()
    
    def test_basic_type_validation(self, data_validator):
        """Test basic data type validation"""
        # String validation
        string_result = data_validator.validate_type("test_string", str)
        assert string_result.is_valid is True
        
        invalid_string_result = data_validator.validate_type(123, str)
        assert invalid_string_result.is_valid is False
        assert "type mismatch" in invalid_string_result.error_message.lower()
        
        # Integer validation
        int_result = data_validator.validate_type(42, int)
        assert int_result.is_valid is True
        
        # Float validation
        float_result = data_validator.validate_type(3.14, float)
        assert float_result.is_valid is True
        
        # Boolean validation
        bool_result = data_validator.validate_type(True, bool)
        assert bool_result.is_valid is True
        
        # List validation
        list_result = data_validator.validate_type([1, 2, 3], list)
        assert list_result.is_valid is True
        
        # Dictionary validation
        dict_result = data_validator.validate_type({"key": "value"}, dict)
        assert dict_result.is_valid is True
    
    def test_string_validation_rules(self, data_validator):
        """Test string-specific validation rules"""
        # Length validation
        min_length_result = data_validator.validate_string_length("test", min_length=3)
        assert min_length_result.is_valid is True
        
        max_length_result = data_validator.validate_string_length("test", max_length=10)
        assert max_length_result.is_valid is True
        
        invalid_length_result = data_validator.validate_string_length("test", min_length=10)
        assert invalid_length_result.is_valid is False
        
        # Pattern validation (email)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        valid_email_result = data_validator.validate_pattern("test@example.com", email_pattern)
        assert valid_email_result.is_valid is True
        
        invalid_email_result = data_validator.validate_pattern("invalid-email", email_pattern)
        assert invalid_email_result.is_valid is False
        
        # URL validation
        url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        valid_url_result = data_validator.validate_pattern("https://example.com", url_pattern)
        assert valid_url_result.is_valid is True
        
        # Alphanumeric validation
        alphanumeric_result = data_validator.validate_alphanumeric("test123")
        assert alphanumeric_result.is_valid is True
        
        non_alphanumeric_result = data_validator.validate_alphanumeric("test-123!")
        assert non_alphanumeric_result.is_valid is False
    
    def test_numeric_validation_rules(self, data_validator):
        """Test numeric validation rules"""
        # Range validation
        in_range_result = data_validator.validate_range(50, min_value=0, max_value=100)
        assert in_range_result.is_valid is True
        
        out_of_range_result = data_validator.validate_range(150, min_value=0, max_value=100)
        assert out_of_range_result.is_valid is False
        
        # Positive number validation
        positive_result = data_validator.validate_positive(42)
        assert positive_result.is_valid is True
        
        negative_result = data_validator.validate_positive(-5)
        assert negative_result.is_valid is False
        
        # Even/odd validation
        even_result = data_validator.validate_even(8)
        assert even_result.is_valid is True
        
        odd_result = data_validator.validate_odd(7)
        assert odd_result.is_valid is True
        
        not_even_result = data_validator.validate_even(7)
        assert not_even_result.is_valid is False
    
    def test_collection_validation(self, data_validator):
        """Test collection validation rules"""
        # List validation
        valid_list = [1, 2, 3, 4, 5]
        list_length_result = data_validator.validate_list_length(valid_list, min_length=3, max_length=10)
        assert list_length_result.is_valid is True
        
        # Unique elements validation
        unique_list = [1, 2, 3, 4, 5]
        unique_result = data_validator.validate_unique_elements(unique_list)
        assert unique_result.is_valid is True
        
        duplicate_list = [1, 2, 3, 2, 5]
        non_unique_result = data_validator.validate_unique_elements(duplicate_list)
        assert non_unique_result.is_valid is False
        
        # Dictionary key validation
        valid_dict = {"name": "John", "age": 30, "email": "john@example.com"}
        required_keys = ["name", "age"]
        key_result = data_validator.validate_required_keys(valid_dict, required_keys)
        assert key_result.is_valid is True
        
        missing_keys_dict = {"name": "John"}
        missing_key_result = data_validator.validate_required_keys(missing_keys_dict, required_keys)
        assert missing_key_result.is_valid is False
    
    def test_date_time_validation(self, data_validator):
        """Test date and time validation"""
        # Date format validation
        valid_date_string = "2023-12-25"
        date_format_result = data_validator.validate_date_format(valid_date_string, "%Y-%m-%d")
        assert date_format_result.is_valid is True
        
        invalid_date_string = "25-12-2023"
        invalid_date_result = data_validator.validate_date_format(invalid_date_string, "%Y-%m-%d")
        assert invalid_date_result.is_valid is False
        
        # Date range validation
        current_date = datetime.now()
        past_date = current_date - timedelta(days=30)
        future_date = current_date + timedelta(days=30)
        
        date_range_result = data_validator.validate_date_range(
            current_date, 
            min_date=past_date, 
            max_date=future_date
        )
        assert date_range_result.is_valid is True
        
        # Future date validation
        future_date_result = data_validator.validate_future_date(future_date)
        assert future_date_result.is_valid is True
        
        past_date_result = data_validator.validate_future_date(past_date)
        assert past_date_result.is_valid is False
    
    def test_custom_validation_rules(self, data_validator):
        """Test custom validation rules"""
        # Custom password validation
        def validate_strong_password(password):
            """Validate password strength"""
            if len(password) < 8:
                return ValidationResult(False, "Password must be at least 8 characters long")
            
            if not re.search(r'[A-Z]', password):
                return ValidationResult(False, "Password must contain at least one uppercase letter")
            
            if not re.search(r'[a-z]', password):
                return ValidationResult(False, "Password must contain at least one lowercase letter")
            
            if not re.search(r'\d', password):
                return ValidationResult(False, "Password must contain at least one digit")
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return ValidationResult(False, "Password must contain at least one special character")
            
            return ValidationResult(True, "Password is strong")
        
        # Register custom validator
        data_validator.register_custom_validator("strong_password", validate_strong_password)
        
        # Test strong password
        strong_password_result = data_validator.validate_custom("strong_password", "StrongP@ssw0rd!")
        assert strong_password_result.is_valid is True
        
        # Test weak password
        weak_password_result = data_validator.validate_custom("strong_password", "weak")
        assert weak_password_result.is_valid is False
        
        # Custom phone number validation
        def validate_phone_number(phone):
            """Validate phone number format"""
            phone_pattern = r'^\+?1?\d{9,15}$'
            if re.match(phone_pattern, phone):
                return ValidationResult(True, "Valid phone number")
            return ValidationResult(False, "Invalid phone number format")
        
        data_validator.register_custom_validator("phone_number", validate_phone_number)
        
        valid_phone_result = data_validator.validate_custom("phone_number", "+1234567890")
        assert valid_phone_result.is_valid is True
        
        invalid_phone_result = data_validator.validate_custom("phone_number", "123")
        assert invalid_phone_result.is_valid is False


class TestSchemaValidator:
    """Test schema validation functionality"""
    
    @pytest.fixture
    def schema_validator(self):
        """Create schema validator for testing"""
        return SchemaValidator()
    
    def test_json_schema_validation(self, schema_validator):
        """Test JSON schema validation"""
        # Define user schema
        user_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "email": {"type": "string", "format": "email"},
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True
                },
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zipcode": {"type": "string", "pattern": "^\\d{5}$"}
                    },
                    "required": ["street", "city"]
                }
            },
            "required": ["name", "age", "email"]
        }
        
        # Valid user data
        valid_user = {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "skills": ["Python", "JavaScript", "React"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zipcode": "12345"
            }
        }
        
        valid_result = schema_validator.validate_json_schema(valid_user, user_schema)
        assert valid_result.is_valid is True
        
        # Invalid user data - missing required field
        invalid_user = {
            "name": "Jane Doe",
            "age": 25
            # Missing required email
        }
        
        invalid_result = schema_validator.validate_json_schema(invalid_user, user_schema)
        assert invalid_result.is_valid is False
        assert "email" in invalid_result.error_message.lower()
    
    def test_nested_schema_validation(self, schema_validator):
        """Test validation of nested schemas"""
        # Define agent configuration schema
        agent_config_schema = {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "minLength": 1},
                "agent_type": {"type": "string", "enum": ["ContentCreator", "SocialManager", "Analytics"]},
                "settings": {
                    "type": "object",
                    "properties": {
                        "max_tasks": {"type": "integer", "minimum": 1},
                        "timeout": {"type": "integer", "minimum": 30},
                        "capabilities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1
                        },
                        "resources": {
                            "type": "object",
                            "properties": {
                                "memory_limit": {"type": "string", "pattern": "^\\d+[GMK]B$"},
                                "cpu_limit": {"type": "number", "minimum": 0.1, "maximum": 4.0}
                            }
                        }
                    },
                    "required": ["max_tasks", "capabilities"]
                }
            },
            "required": ["agent_id", "agent_type", "settings"]
        }
        
        # Valid nested configuration
        valid_config = {
            "agent_id": "content_creator_001",
            "agent_type": "ContentCreator",
            "settings": {
                "max_tasks": 10,
                "timeout": 300,
                "capabilities": ["content_generation", "image_editing"],
                "resources": {
                    "memory_limit": "2GB",
                    "cpu_limit": 2.0
                }
            }
        }
        
        valid_result = schema_validator.validate_json_schema(valid_config, agent_config_schema)
        assert valid_result.is_valid is True
        
        # Invalid nested configuration
        invalid_config = {
            "agent_id": "invalid_agent",
            "agent_type": "InvalidType",  # Not in enum
            "settings": {
                "max_tasks": 0,  # Below minimum
                "capabilities": []  # Empty array not allowed
            }
        }
        
        invalid_result = schema_validator.validate_json_schema(invalid_config, agent_config_schema)
        assert invalid_result.is_valid is False
    
    def test_schema_composition(self, schema_validator):
        """Test schema composition with allOf, anyOf, oneOf"""
        # Schema with allOf
        all_of_schema = {
            "allOf": [
                {"type": "object", "properties": {"name": {"type": "string"}}},
                {"type": "object", "properties": {"age": {"type": "integer", "minimum": 0}}}
            ]
        }
        
        valid_all_of_data = {"name": "John", "age": 30}
        all_of_result = schema_validator.validate_json_schema(valid_all_of_data, all_of_schema)
        assert all_of_result.is_valid is True
        
        # Schema with anyOf
        any_of_schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer", "minimum": 0}
            ]
        }
        
        string_result = schema_validator.validate_json_schema("test", any_of_schema)
        assert string_result.is_valid is True
        
        integer_result = schema_validator.validate_json_schema(42, any_of_schema)
        assert integer_result.is_valid is True
        
        invalid_any_of_result = schema_validator.validate_json_schema(-5, any_of_schema)
        assert invalid_any_of_result.is_valid is False
        
        # Schema with oneOf
        one_of_schema = {
            "oneOf": [
                {"type": "string", "maxLength": 5},
                {"type": "string", "minLength": 10}
            ]
        }
        
        short_string_result = schema_validator.validate_json_schema("test", one_of_schema)
        assert short_string_result.is_valid is True
        
        long_string_result = schema_validator.validate_json_schema("this is a long string", one_of_schema)
        assert long_string_result.is_valid is True
        
        # String that matches both schemas (invalid for oneOf)
        ambiguous_result = schema_validator.validate_json_schema("", one_of_schema)
        assert ambiguous_result.is_valid is False
    
    def test_custom_format_validation(self, schema_validator):
        """Test custom format validators"""
        # Register custom UUID format validator
        def validate_uuid_format(value):
            try:
                UUID(value)
                return True
            except ValueError:
                return False
        
        schema_validator.register_format_validator("uuid", validate_uuid_format)
        
        # Schema using custom format
        uuid_schema = {
            "type": "string",
            "format": "uuid"
        }
        
        valid_uuid_result = schema_validator.validate_json_schema(
            "550e8400-e29b-41d4-a716-446655440000", 
            uuid_schema
        )
        assert valid_uuid_result.is_valid is True
        
        invalid_uuid_result = schema_validator.validate_json_schema("not-a-uuid", uuid_schema)
        assert invalid_uuid_result.is_valid is False
        
        # Register custom credit card format validator
        def validate_credit_card_format(value):
            # Simple Luhn algorithm check
            def luhn_check(card_num):
                def digits_of(n):
                    return [int(d) for d in str(n)]
                
                digits = digits_of(card_num)
                odd_digits = digits[-1::-2]
                even_digits = digits[-2::-2]
                checksum = sum(odd_digits)
                for d in even_digits:
                    checksum += sum(digits_of(d*2))
                return checksum % 10 == 0
            
            return luhn_check(value.replace(' ', '').replace('-', ''))
        
        schema_validator.register_format_validator("credit_card", validate_credit_card_format)
        
        credit_card_schema = {
            "type": "string",
            "format": "credit_card"
        }
        
        # Test valid credit card number
        valid_card_result = schema_validator.validate_json_schema(
            "4532015112830366", 
            credit_card_schema
        )
        assert valid_card_result.is_valid is True
    
    def test_schema_reference_resolution(self, schema_validator):
        """Test schema reference resolution"""
        # Define schemas with references
        address_schema = {
            "$id": "address",
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["street", "city", "country"]
        }
        
        person_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {"$ref": "#/definitions/address"}
            },
            "definitions": {
                "address": address_schema
            },
            "required": ["name", "address"]
        }
        
        # Register schema with references
        schema_validator.register_schema("person", person_schema)
        
        valid_person = {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "country": "USA"
            }
        }
        
        valid_result = schema_validator.validate_with_references(valid_person, "person")
        assert valid_result.is_valid is True


class TestBusinessRuleValidator:
    """Test business rule validation functionality"""
    
    @pytest.fixture
    def business_validator(self):
        """Create business rule validator for testing"""
        return BusinessRuleValidator()
    
    def test_simple_business_rules(self, business_validator):
        """Test simple business rule validation"""
        # Define age-based discount rule
        age_discount_rule = ValidationRule(
            name="age_discount_eligibility",
            description="Senior citizens (65+) are eligible for discount",
            condition=lambda data: data.get("age", 0) >= 65,
            error_message="Customer must be 65 or older for senior discount"
        )
        
        business_validator.add_rule(age_discount_rule)
        
        # Test eligible customer
        eligible_customer = {"name": "John Senior", "age": 70}
        eligible_result = business_validator.validate(eligible_customer)
        assert eligible_result.is_valid is True
        
        # Test ineligible customer
        ineligible_customer = {"name": "Jane Young", "age": 30}
        ineligible_result = business_validator.validate(ineligible_customer)
        assert ineligible_result.is_valid is False
        assert "65 or older" in ineligible_result.error_message
    
    def test_complex_business_rules(self, business_validator):
        """Test complex business rule validation"""
        # Define complex pricing rule
        pricing_rule = ValidationRule(
            name="bulk_pricing_rule",
            description="Bulk orders (100+ items) must have total value > $1000",
            condition=lambda data: (
                data.get("quantity", 0) < 100 or 
                data.get("total_value", 0) >= 1000
            ),
            error_message="Bulk orders (100+ items) must have minimum total value of $1000"
        )
        
        # Define membership rule
        membership_rule = ValidationRule(
            name="premium_member_rule",
            description="Premium features require premium membership",
            condition=lambda data: (
                not data.get("uses_premium_features", False) or 
                data.get("membership_type") == "premium"
            ),
            error_message="Premium membership required for premium features"
        )
        
        business_validator.add_rule(pricing_rule)
        business_validator.add_rule(membership_rule)
        
        # Test valid bulk order
        valid_bulk_order = {
            "quantity": 150,
            "total_value": 1500,
            "uses_premium_features": True,
            "membership_type": "premium"
        }
        
        valid_result = business_validator.validate(valid_bulk_order)
        assert valid_result.is_valid is True
        
        # Test invalid bulk order (low value)
        invalid_bulk_order = {
            "quantity": 120,
            "total_value": 800,  # Too low for bulk order
            "uses_premium_features": False,
            "membership_type": "basic"
        }
        
        invalid_result = business_validator.validate(invalid_bulk_order)
        assert invalid_result.is_valid is False
        
        # Test premium feature without membership
        premium_without_membership = {
            "quantity": 50,
            "total_value": 500,
            "uses_premium_features": True,
            "membership_type": "basic"  # Not premium
        }
        
        membership_result = business_validator.validate(premium_without_membership)
        assert membership_result.is_valid is False
    
    def test_conditional_business_rules(self, business_validator):
        """Test conditional business rules"""
        # Define conditional shipping rule
        shipping_rule = ValidationRule(
            name="free_shipping_rule",
            description="Free shipping for orders over $50 or premium members",
            condition=lambda data: (
                data.get("order_total", 0) >= 50 or
                data.get("membership_type") == "premium" or
                data.get("shipping_cost", 0) > 0
            ),
            error_message="Orders under $50 for non-premium members must include shipping cost"
        )
        
        business_validator.add_rule(shipping_rule)
        
        # Test premium member with small order (should pass)
        premium_small_order = {
            "order_total": 25,
            "membership_type": "premium",
            "shipping_cost": 0
        }
        
        premium_result = business_validator.validate(premium_small_order)
        assert premium_result.is_valid is True
        
        # Test large order (should pass)
        large_order = {
            "order_total": 75,
            "membership_type": "basic",
            "shipping_cost": 0
        }
        
        large_order_result = business_validator.validate(large_order)
        assert large_order_result.is_valid is True
        
        # Test small order with shipping (should pass)
        small_order_with_shipping = {
            "order_total": 25,
            "membership_type": "basic",
            "shipping_cost": 10
        }
        
        shipping_result = business_validator.validate(small_order_with_shipping)
        assert shipping_result.is_valid is True
        
        # Test small order without shipping (should fail)
        small_order_no_shipping = {
            "order_total": 25,
            "membership_type": "basic",
            "shipping_cost": 0
        }
        
        no_shipping_result = business_validator.validate(small_order_no_shipping)
        assert no_shipping_result.is_valid is False
    
    def test_rule_groups(self, business_validator):
        """Test business rule groups and priorities"""
        # Define critical rules (must pass)
        critical_rule_1 = ValidationRule(
            name="age_verification",
            description="User must be 18 or older",
            condition=lambda data: data.get("age", 0) >= 18,
            error_message="User must be 18 or older",
            priority="critical"
        )
        
        critical_rule_2 = ValidationRule(
            name="terms_acceptance",
            description="User must accept terms and conditions",
            condition=lambda data: data.get("terms_accepted", False) is True,
            error_message="Terms and conditions must be accepted",
            priority="critical"
        )
        
        # Define warning rules (can pass with warnings)
        warning_rule = ValidationRule(
            name="profile_completion",
            description="Profile should be complete for better experience",
            condition=lambda data: len(data.get("profile_fields", [])) >= 5,
            error_message="Consider completing your profile",
            priority="warning"
        )
        
        business_validator.add_rule_group("critical", [critical_rule_1, critical_rule_2])
        business_validator.add_rule_group("warnings", [warning_rule])
        
        # Test user that passes all rules
        complete_user = {
            "age": 25,
            "terms_accepted": True,
            "profile_fields": ["name", "email", "phone", "address", "interests", "bio"]
        }
        
        complete_result = business_validator.validate_with_groups(complete_user)
        assert complete_result.is_valid is True
        assert len(complete_result.warnings) == 0
        
        # Test user with warnings
        incomplete_user = {
            "age": 22,
            "terms_accepted": True,
            "profile_fields": ["name", "email"]  # Incomplete profile
        }
        
        warning_result = business_validator.validate_with_groups(incomplete_user)
        assert warning_result.is_valid is True  # Passes critical rules
        assert len(warning_result.warnings) == 1
        assert "profile" in warning_result.warnings[0].lower()
        
        # Test user that fails critical rules
        invalid_user = {
            "age": 16,  # Too young
            "terms_accepted": False,  # Not accepted
            "profile_fields": ["name"]
        }
        
        critical_fail_result = business_validator.validate_with_groups(invalid_user)
        assert critical_fail_result.is_valid is False
        assert len(critical_fail_result.errors) >= 2  # Multiple critical failures
    
    def test_cross_field_validation(self, business_validator):
        """Test cross-field business rule validation"""
        # Define password confirmation rule
        password_confirmation_rule = ValidationRule(
            name="password_confirmation",
            description="Password and confirmation must match",
            condition=lambda data: data.get("password") == data.get("password_confirmation"),
            error_message="Password and confirmation do not match"
        )
        
        # Define start/end date rule
        date_range_rule = ValidationRule(
            name="date_range_validation",
            description="End date must be after start date",
            condition=lambda data: (
                data.get("start_date") is None or 
                data.get("end_date") is None or
                data.get("end_date") > data.get("start_date")
            ),
            error_message="End date must be after start date"
        )
        
        business_validator.add_rule(password_confirmation_rule)
        business_validator.add_rule(date_range_rule)
        
        # Test matching passwords and valid date range
        valid_data = {
            "password": "securepassword123",
            "password_confirmation": "securepassword123",
            "start_date": datetime(2023, 1, 1),
            "end_date": datetime(2023, 12, 31)
        }
        
        valid_result = business_validator.validate(valid_data)
        assert valid_result.is_valid is True
        
        # Test mismatched passwords
        password_mismatch = {
            "password": "password123",
            "password_confirmation": "different_password",
            "start_date": datetime(2023, 1, 1),
            "end_date": datetime(2023, 12, 31)
        }
        
        password_result = business_validator.validate(password_mismatch)
        assert password_result.is_valid is False
        assert "match" in password_result.error_message.lower()
        
        # Test invalid date range
        invalid_dates = {
            "password": "password123",
            "password_confirmation": "password123",
            "start_date": datetime(2023, 12, 31),
            "end_date": datetime(2023, 1, 1)  # End before start
        }
        
        date_result = business_validator.validate(invalid_dates)
        assert date_result.is_valid is False
        assert "after" in date_result.error_message.lower()


class TestIntegrityValidator:
    """Test data integrity validation functionality"""
    
    @pytest.fixture
    def integrity_validator(self):
        """Create integrity validator for testing"""
        return IntegrityValidator()
    
    def test_referential_integrity(self, integrity_validator):
        """Test referential integrity validation"""
        # Mock database tables
        users_table = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
        ]
        
        orders_table = [
            {"id": 101, "user_id": 1, "total": 100.0, "status": "completed"},
            {"id": 102, "user_id": 2, "total": 250.0, "status": "pending"},
            {"id": 103, "user_id": 4, "total": 75.0, "status": "completed"}  # Invalid user_id
        ]
        
        # Set up mock data
        integrity_validator.set_reference_data("users", users_table)
        integrity_validator.set_reference_data("orders", orders_table)
        
        # Define referential integrity rule
        user_order_integrity = {
            "name": "user_order_reference",
            "child_table": "orders",
            "child_field": "user_id",
            "parent_table": "users",
            "parent_field": "id"
        }
        
        integrity_validator.add_referential_integrity_rule(user_order_integrity)
        
        # Validate referential integrity
        integrity_result = integrity_validator.validate_referential_integrity()
        
        assert integrity_result.is_valid is False
        assert len(integrity_result.violations) == 1
        assert integrity_result.violations[0]["child_record"]["user_id"] == 4
    
    def test_uniqueness_constraints(self, integrity_validator):
        """Test uniqueness constraint validation"""
        # Mock user data with duplicate email
        users_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "John Different", "email": "john@example.com"}  # Duplicate email
        ]
        
        integrity_validator.set_reference_data("users", users_data)
        
        # Define uniqueness constraint
        email_uniqueness = {
            "table": "users",
            "fields": ["email"],
            "name": "unique_email"
        }
        
        integrity_validator.add_uniqueness_constraint(email_uniqueness)
        
        # Validate uniqueness
        uniqueness_result = integrity_validator.validate_uniqueness_constraints()
        
        assert uniqueness_result.is_valid is False
        assert len(uniqueness_result.violations) == 1
        assert uniqueness_result.violations[0]["constraint"] == "unique_email"
        assert uniqueness_result.violations[0]["field"] == "email"
    
    def test_data_consistency(self, integrity_validator):
        """Test data consistency validation"""
        # Mock order data with inconsistent totals
        order_items = [
            {"order_id": 101, "product": "Widget A", "quantity": 2, "price": 25.0},
            {"order_id": 101, "product": "Widget B", "quantity": 1, "price": 50.0},
            {"order_id": 102, "product": "Widget C", "quantity": 3, "price": 30.0}
        ]
        
        orders = [
            {"id": 101, "total": 100.0},  # Correct total (2*25 + 1*50 = 100)
            {"id": 102, "total": 75.0}    # Incorrect total (should be 3*30 = 90)
        ]
        
        integrity_validator.set_reference_data("order_items", order_items)
        integrity_validator.set_reference_data("orders", orders)
        
        # Define consistency rule
        def validate_order_total_consistency():
            """Validate that order totals match sum of item prices"""
            violations = []
            
            for order in orders:
                order_id = order["id"]
                stated_total = order["total"]
                
                # Calculate actual total from items
                items = [item for item in order_items if item["order_id"] == order_id]
                calculated_total = sum(item["quantity"] * item["price"] for item in items)
                
                if abs(stated_total - calculated_total) > 0.01:  # Allow for small rounding differences
                    violations.append({
                        "order_id": order_id,
                        "stated_total": stated_total,
                        "calculated_total": calculated_total,
                        "difference": abs(stated_total - calculated_total)
                    })
            
            return ValidationResult(
                is_valid=len(violations) == 0,
                error_message=f"Found {len(violations)} order total inconsistencies" if violations else None,
                violations=violations
            )
        
        integrity_validator.add_consistency_rule("order_total_consistency", validate_order_total_consistency)
        
        # Validate consistency
        consistency_result = integrity_validator.validate_consistency_rules()
        
        assert consistency_result.is_valid is False
        assert len(consistency_result.violations) == 1
        assert consistency_result.violations[0]["order_id"] == 102
    
    def test_cascade_validation(self, integrity_validator):
        """Test cascading integrity validation"""
        # Mock hierarchical data (categories -> products -> orders)
        categories = [
            {"id": 1, "name": "Electronics"},
            {"id": 2, "name": "Books"}
        ]
        
        products = [
            {"id": 101, "name": "Laptop", "category_id": 1},
            {"id": 102, "name": "Phone", "category_id": 1},
            {"id": 103, "name": "Novel", "category_id": 2},
            {"id": 104, "name": "Tablet", "category_id": 3}  # Invalid category
        ]
        
        order_items = [
            {"id": 1001, "product_id": 101, "quantity": 1},
            {"id": 1002, "product_id": 102, "quantity": 2},
            {"id": 1003, "product_id": 105, "quantity": 1}  # Invalid product
        ]
        
        integrity_validator.set_reference_data("categories", categories)
        integrity_validator.set_reference_data("products", products)
        integrity_validator.set_reference_data("order_items", order_items)
        
        # Define cascade integrity rules
        category_product_rule = {
            "name": "category_product_reference",
            "child_table": "products",
            "child_field": "category_id",
            "parent_table": "categories",
            "parent_field": "id"
        }
        
        product_order_rule = {
            "name": "product_order_reference",
            "child_table": "order_items",
            "child_field": "product_id",
            "parent_table": "products",
            "parent_field": "id"
        }
        
        integrity_validator.add_referential_integrity_rule(category_product_rule)
        integrity_validator.add_referential_integrity_rule(product_order_rule)
        
        # Validate cascade integrity
        cascade_result = integrity_validator.validate_cascade_integrity()
        
        assert cascade_result.is_valid is False
        assert len(cascade_result.violations) >= 2  # At least category and product violations
    
    @pytest.mark.performance
    def test_integrity_validation_performance(self, integrity_validator, assert_performance):
        """Test integrity validation performance with large datasets"""
        # Generate large dataset
        large_users = [{"id": i, "email": f"user{i}@example.com"} for i in range(1000)]
        large_orders = [{"id": i + 1000, "user_id": (i % 1000) + 1, "total": 100.0} for i in range(5000)]
        
        integrity_validator.set_reference_data("users", large_users)
        integrity_validator.set_reference_data("orders", large_orders)
        
        # Define integrity rule
        user_order_rule = {
            "name": "user_order_reference",
            "child_table": "orders",
            "child_field": "user_id",
            "parent_table": "users",
            "parent_field": "id"
        }
        
        integrity_validator.add_referential_integrity_rule(user_order_rule)
        
        # Measure validation performance
        start_time = datetime.now(timezone.utc)
        integrity_result = integrity_validator.validate_referential_integrity()
        validation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        assert validation_time < 10.0  # Should validate within 10 seconds
        assert_performance("integrity_validation", max_time=10.0)
        assert integrity_result.is_valid is True  # Should pass with properly generated data


class TestAsyncValidator:
    """Test asynchronous validation functionality"""
    
    @pytest.fixture
    async def async_validator(self):
        """Create async validator for testing"""
        validator = AsyncValidator()
        await validator.initialize()
        
        yield validator
        
        await validator.shutdown()
    
    async def test_async_validation_rules(self, async_validator):
        """Test asynchronous validation rules"""
        # Define async validation rule (simulating external API call)
        async def validate_email_deliverability(email):
            """Simulate checking email deliverability via external service"""
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simple mock validation - reject emails from blocked domains
            blocked_domains = ["spam.com", "fake.net", "invalid.org"]
            domain = email.split("@")[1] if "@" in email else ""
            
            if domain in blocked_domains:
                return ValidationResult(False, f"Email domain {domain} is not deliverable")
            
            return ValidationResult(True, "Email is deliverable")
        
        async_validator.add_async_rule("email_deliverability", validate_email_deliverability)
        
        # Test valid email
        valid_result = await async_validator.validate_async("test@example.com")
        assert valid_result.is_valid is True
        
        # Test blocked email
        blocked_result = await async_validator.validate_async("test@spam.com")
        assert blocked_result.is_valid is False
        assert "not deliverable" in blocked_result.error_message
    
    async def test_parallel_async_validation(self, async_validator):
        """Test parallel execution of async validation rules"""
        # Define multiple async validation rules
        async def validate_username_availability(username):
            """Simulate checking username availability"""
            await asyncio.sleep(0.2)
            
            taken_usernames = ["admin", "root", "test", "user"]
            if username.lower() in taken_usernames:
                return ValidationResult(False, f"Username '{username}' is not available")
            
            return ValidationResult(True, "Username is available")
        
        async def validate_phone_number_service(phone):
            """Simulate validating phone number via service"""
            await asyncio.sleep(0.15)
            
            # Simple validation - must start with country code
            if not phone.startswith("+"):
                return ValidationResult(False, "Phone number must include country code")
            
            return ValidationResult(True, "Phone number is valid")
        
        async_validator.add_async_rule("username_availability", validate_username_availability)
        async_validator.add_async_rule("phone_validation", validate_phone_number_service)
        
        # Test data for parallel validation
        test_data = {
            "username": "newuser",
            "phone": "+1234567890"
        }
        
        # Measure parallel validation time
        start_time = datetime.now(timezone.utc)
        results = await async_validator.validate_parallel(test_data, [
            ("username", "username_availability"),
            ("phone", "phone_validation")
        ])
        validation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Should complete in less time than sequential execution
        assert validation_time < 0.5  # Parallel should be faster than 0.2 + 0.15 = 0.35
        
        # Check results
        assert all(result.is_valid for result in results.values())
    
    async def test_async_validation_with_timeout(self, async_validator):
        """Test async validation with timeout handling"""
        # Define slow validation rule
        async def slow_validation(data):
            """Simulate slow external validation"""
            await asyncio.sleep(2.0)  # Intentionally slow
            return ValidationResult(True, "Validation completed")
        
        async_validator.add_async_rule("slow_validation", slow_validation, timeout=1.0)
        
        # Test validation with timeout
        with pytest.raises(asyncio.TimeoutError):
            await async_validator.validate_async_with_timeout("test_data", "slow_validation")
    
    async def test_async_validation_error_handling(self, async_validator):
        """Test error handling in async validation"""
        # Define validation rule that raises exception
        async def failing_validation(data):
            """Validation that raises an exception"""
            await asyncio.sleep(0.1)
            raise ValueError("Validation service unavailable")
        
        async_validator.add_async_rule("failing_validation", failing_validation)
        
        # Test error handling
        result = await async_validator.validate_async_safe("test_data", "failing_validation")
        
        assert result.is_valid is False
        assert "unavailable" in result.error_message.lower()
    
    async def test_async_batch_validation(self, async_validator):
        """Test batch validation of multiple items"""
        # Define batch validation rule
        async def validate_user_batch(users):
            """Validate a batch of users"""
            results = []
            
            for user in users:
                await asyncio.sleep(0.05)  # Simulate processing time per user
                
                # Simple validation - check required fields
                if not user.get("name") or not user.get("email"):
                    results.append(ValidationResult(False, "Name and email are required"))
                else:
                    results.append(ValidationResult(True, "User is valid"))
            
            return results
        
        # Test batch validation
        test_users = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"},
            {"name": "", "email": "invalid@example.com"},  # Invalid - no name
            {"name": "Bob Johnson", "email": ""}  # Invalid - no email
        ]
        
        batch_results = await async_validator.validate_batch(test_users, validate_user_batch)
        
        assert len(batch_results) == 4
        assert batch_results[0].is_valid is True
        assert batch_results[1].is_valid is True
        assert batch_results[2].is_valid is False
        assert batch_results[3].is_valid is False


@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for complete validation system"""
    
    @pytest.fixture
    async def complete_validator(self):
        """Create complete validation system for integration testing"""
        from ai.ai_agents.validate import ValidationSystem
        
        system = ValidationSystem()
        await system.initialize()
        
        yield system
        
        await system.shutdown()
    
    async def test_multi_layer_validation(self, complete_validator):
        """Test multi-layer validation (data -> schema -> business -> integrity)"""
        # Define user registration data
        registration_data = {
            "username": "johndoe",
            "email": "john.doe@example.com",
            "password": "SecureP@ssw0rd123",
            "password_confirmation": "SecureP@ssw0rd123",
            "age": 25,
            "terms_accepted": True,
            "profile": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890"
            }
        }
        
        # Perform complete validation
        validation_result = await complete_validator.validate_complete(
            data=registration_data,
            validation_type="user_registration"
        )
        
        assert validation_result.is_valid is True
        assert validation_result.passed_layers == ["data", "schema", "business", "integrity"]
    
    async def test_validation_pipeline_with_failures(self, complete_validator):
        """Test validation pipeline with failures at different layers"""
        # Define invalid registration data
        invalid_data = {
            "username": "admin",  # Business rule violation - reserved username
            "email": "invalid-email",  # Schema violation - invalid format
            "password": "weak",  # Data validation violation - too weak
            "password_confirmation": "different",  # Business rule violation - mismatch
            "age": 15,  # Business rule violation - too young
            "terms_accepted": False  # Business rule violation - not accepted
        }
        
        # Perform validation expecting failures
        validation_result = await complete_validator.validate_complete(
            data=invalid_data,
            validation_type="user_registration"
        )
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert "data" in validation_result.failed_layers
        assert "schema" in validation_result.failed_layers
        assert "business" in validation_result.failed_layers
    
    async def test_conditional_validation_flows(self, complete_validator):
        """Test conditional validation flows based on data type"""
        # Test admin user registration (different rules)
        admin_data = {
            "username": "admin_user",
            "email": "admin@company.com",
            "password": "AdminP@ssw0rd123",
            "password_confirmation": "AdminP@ssw0rd123",
            "age": 30,
            "role": "admin",
            "security_clearance": "high",
            "two_factor_enabled": True
        }
        
        admin_result = await complete_validator.validate_complete(
            data=admin_data,
            validation_type="admin_registration"
        )
        
        assert admin_result.is_valid is True
        
        # Test premium membership validation
        premium_data = {
            "user_id": 12345,
            "membership_type": "premium",
            "payment_method": "credit_card",
            "billing_cycle": "annual",
            "features": ["advanced_analytics", "priority_support", "custom_branding"]
        }
        
        premium_result = await complete_validator.validate_complete(
            data=premium_data,
            validation_type="premium_membership"
        )
        
        assert premium_result.is_valid is True
    
    @pytest.mark.performance
    async def test_validation_system_performance(self, complete_validator, assert_performance):
        """Test performance of complete validation system"""
        # Generate test data for performance testing
        test_users = []
        for i in range(100):
            test_users.append({
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": f"SecureP@ssw0rd{i}",
                "password_confirmation": f"SecureP@ssw0rd{i}",
                "age": 20 + (i % 30),
                "terms_accepted": True
            })
        
        # Measure validation performance
        start_time = datetime.now(timezone.utc)
        
        validation_tasks = [
            complete_validator.validate_complete(user, "user_registration")
            for user in test_users
        ]
        
        results = await asyncio.gather(*validation_tasks)
        validation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Verify all validations completed successfully
        assert all(result.is_valid for result in results)
        
        # Performance assertion
        assert validation_time < 30.0  # Should validate 100 users within 30 seconds
        assert_performance("batch_validation", max_time=30.0)
