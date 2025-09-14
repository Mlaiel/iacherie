"""Data Infrastructure Utilities
import logging

==============================

Enterprise data infrastructure utilities for IA Influencer Agent platform.
Comprehensive validation, migration, and utility functions for enterprise-grade
data management with performance optimization and integrity enforcement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Comprehensive data validation with enterprise rules
• Database migration management with rollback capabilities
• Schema enforcement & validation
• Test data generation for development & testing
• Performance optimization & monitoring
• Error handling & logging systems
• Data integrity enforcement
• Enterprise-grade utility functions
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import uuid
import json
import re
import hashlib
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message -> None: str, field -> None: str = None, code -> None: str = None, details -> None: Dict[str, Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code
        self.details = details or {}
        
    def __str__(self) -> None:
        if self.field:
            return f"Validation error in field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"
    
    def to_dict(self) -> None:
        return {
            "error": "ValidationError",
            "message": self.message,
            "field": self.field,
            "code": self.code,
            "details": self.details
        }


class MigrationError(Exception):
    """Custom exception for migration errors"""
    
    def __init__(self, message -> None: str, migration_id -> None: str = None, details -> None: Dict[str, Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.migration_id = migration_id
        self.details = details or {}


class SchemaValidationError(Exception):
    """Custom exception for schema validation errors"""
    
    def __init__(self, message -> None: str, schema_name -> None: str = None, details -> None: Dict[str, Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.schema_name = schema_name
        self.details = details or {}


# ============================================================================
# VALIDATION RESULT CLASSES
# ============================================================================

class ValidationResult:
    """Container for validation results with detailed feedback"""
    
    def __init__(self, is_valid -> None: bool = True, errors -> None: List[str] = None, 
                 warnings -> None: List[str] = None, field_errors -> None: Dict[str, List[str]] = None,
                 metadata -> None: Dict[str, Any] = None) -> None:
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.field_errors = field_errors or {}
        self.metadata = metadata or {}
        
    def add_error(self, message -> None: str, field -> None: str = None) -> None:
        """Add an error to the validation result"""
        self.is_valid = False
        self.errors.append(message)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message -> None: str) -> None:
        """Add a warning to the validation result"""
        self.warnings.append(message)
    
    def merge(self, other -> None: 'ValidationResult') -> None:
        """Merge another validation result into this one"""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        for field, field_errors in other.field_errors.items():
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].extend(field_errors)
        self.metadata.update(other.metadata)
    
    def to_dict(self) -> None:
        """Convert validation result to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "field_errors": self.field_errors,
            "metadata": self.metadata
        }
    
    def __str__(self) -> None:
        if self.is_valid:
            status = "VALID"
            if self.warnings:
                status += f" (with {len(self.warnings)} warnings)"
        else:
            status = f"INVALID ({len(self.errors)} errors"
            if self.warnings:
                status += f", {len(self.warnings)} warnings"
            status += ")"
        return f"ValidationResult: {status}"


# ============================================================================
# MODEL DATA VALIDATOR
# ============================================================================

class ModelDataValidator:
    """
    Enterprise-grade data validator for all model types.
    Comprehensive validation with business rules and performance optimization.
    """
    
    def __init__(self) -> None:
        self.validation_rules = self._load_validation_rules()
        self.business_rules = self._load_business_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different model types"""
        return {
            "user": {
                "required_fields": ["email", "username", "user_type"],
                "email_regex": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                "username_regex": r'^[a-zA-Z0-9_]{3,30}$',
                "password_min_length": 8,
                "allowed_user_types": ["musician", "blogger", "photographer", "influencer", "comedian", "podcaster"]
            },
            "content": {
                "required_fields": ["title", "content_type", "user_id"],
                "title_max_length": 500,
                "description_max_length": 5000,
                "allowed_content_types": ["music", "video", "image", "text", "podcast", "live_stream"],
                "allowed_visibility": ["public", "private", "unlisted", "premium"]
            },
            "revenue": {
                "required_fields": ["user_id", "gross_amount", "currency", "revenue_source"],
                "min_amount": 0.01,
                "max_amount": 1000000.00,
                "allowed_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"],
                "allowed_revenue_sources": ["ads", "subscriptions", "licensing", "donations", "nft_sales"]
            },
            "nft": {
                "required_fields": ["nft_name", "creator_id", "blockchain_network"],
                "name_max_length": 500,
                "description_max_length": 2000,
                "allowed_networks": ["ethereum", "polygon", "solana", "binance_smart_chain"],
                "royalty_percentage_max": 50.0
            }
        }
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules for validation"""
        return {
            "user": {
                "premium_user_content_limit": 1000,
                "free_user_content_limit": 10,
                "max_collaborations_per_month": 50
            },
            "content": {
                "max_file_size_mb": 500,
                "max_duration_hours": 12,
                "min_quality_score": 0.6
            },
            "revenue": {
                "max_monthly_revenue": 100000.00,
                "min_payout_threshold": 10.00
            }
        }
    
    def validate_user(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate user data"""
        result = ValidationResult()
        rules = self.validation_rules["user"]
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in data or not data[field]:
                result.add_error(f"Required field '{field}' is missing or empty", field)
        
        # Validate email format
        if "email" in data and data["email"]:
            if not re.match(rules["email_regex"], data["email"]):
                result.add_error("Invalid email format", "email")
        
        # Validate username
        if "username" in data and data["username"]:
            if not re.match(rules["username_regex"], data["username"]):
                result.add_error("Username must be 3-30 characters, alphanumeric and underscores only", "username")
        
        # Validate user type
        if "user_type" in data and data["user_type"]:
            if data["user_type"] not in rules["allowed_user_types"]:
                result.add_error(f"Invalid user type. Allowed: {', '.join(rules['allowed_user_types'])}", "user_type")
        
        # Validate subscription tier business rules
        if "subscription_tier" in data and "total_content_count" in data:
            max_content = self._get_content_limit_for_tier(data["subscription_tier"])
            if data["total_content_count"] > max_content:
                result.add_error(f"Content count exceeds limit for {data['subscription_tier']} tier", "total_content_count")
        
        return result
    
    def validate_content(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate content data"""
        result = ValidationResult()
        rules = self.validation_rules["content"]
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in data or not data[field]:
                result.add_error(f"Required field '{field}' is missing or empty", field)
        
        # Validate title length
        if "title" in data and data["title"]:
            if len(data["title"]) > rules["title_max_length"]:
                result.add_error(f"Title exceeds maximum length of {rules['title_max_length']} characters", "title")
        
        # Validate description length
        if "description" in data and data["description"]:
            if len(data["description"]) > rules["description_max_length"]:
                result.add_error(f"Description exceeds maximum length of {rules['description_max_length']} characters", "description")
        
        # Validate content type
        if "content_type" in data and data["content_type"]:
            if data["content_type"] not in rules["allowed_content_types"]:
                result.add_error(f"Invalid content type. Allowed: {', '.join(rules['allowed_content_types'])}", "content_type")
        
        # Validate visibility
        if "visibility" in data and data["visibility"]:
            if data["visibility"] not in rules["allowed_visibility"]:
                result.add_error(f"Invalid visibility. Allowed: {', '.join(rules['allowed_visibility'])}", "visibility")
        
        # Business rule validations
        business_rules = self.business_rules["content"]
        
        # Validate file size
        if "file_size" in data and data["file_size"]:
            max_size_bytes = business_rules["max_file_size_mb"] * 1024 * 1024
            if data["file_size"] > max_size_bytes:
                result.add_error(f"File size exceeds maximum of {business_rules['max_file_size_mb']}MB", "file_size")
        
        # Validate duration
        if "duration" in data and data["duration"]:
            max_duration_seconds = business_rules["max_duration_hours"] * 3600
            if data["duration"] > max_duration_seconds:
                result.add_error(f"Duration exceeds maximum of {business_rules['max_duration_hours']} hours", "duration")
        
        return result
    
    def validate_revenue(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate revenue data"""
        result = ValidationResult()
        rules = self.validation_rules["revenue"]
        
        # Check required fields
        for field in rules["required_fields"]:
            if field not in data or data[field] is None:
                result.add_error(f"Required field '{field}' is missing or empty", field)
        
        # Validate amount range
        if "gross_amount" in data and data["gross_amount"] is not None:
            amount = float(data["gross_amount"])
            if amount < rules["min_amount"]:
                result.add_error(f"Amount must be at least {rules['min_amount']}", "gross_amount")
            if amount > rules["max_amount"]:
                result.add_error(f"Amount exceeds maximum of {rules['max_amount']}", "gross_amount")
        
        # Validate currency
        if "currency" in data and data["currency"]:
            if data["currency"] not in rules["allowed_currencies"]:
                result.add_error(f"Invalid currency. Allowed: {', '.join(rules['allowed_currencies'])}", "currency")
        
        # Validate revenue source
        if "revenue_source" in data and data["revenue_source"]:
            if data["revenue_source"] not in rules["allowed_revenue_sources"]:
                result.add_error(f"Invalid revenue source. Allowed: {', '.join(rules['allowed_revenue_sources'])}", "revenue_source")
        
        return result
    
    def validate_analytics(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate analytics data"""
        result = ValidationResult()
        
        # Check required fields
        required_fields = ["user_id", "metric_name", "value", "measurement_date"]
        for field in required_fields:
            if field not in data or data[field] is None:
                result.add_error(f"Required field '{field}' is missing or empty", field)
        
        # Validate metric value
        if "value" in data and data["value"] is not None:
            try:
                value = float(data["value"])
                if value < 0:
                    result.add_error("Metric value cannot be negative", "value")
            except (ValueError, TypeError):
                result.add_error("Metric value must be a number", "value")
        
        # Validate measurement date
        if "measurement_date" in data and data["measurement_date"]:
            if isinstance(data["measurement_date"], str):
                try:
                    datetime.fromisoformat(data["measurement_date"].replace('Z', '+00:00'))
                except ValueError:
                    result.add_error("Invalid measurement date format", "measurement_date")
        
        return result
    
    def _get_content_limit_for_tier(self, tier: str) -> int:
        """Get content limit based on subscription tier"""
        limits = {
            "free": 10,
            "basic": 50,
            "pro": 200,
            "premium": 500,
            "enterprise": 1000
        }
        return limits.get(tier, 10)
    
    def validate_batch(self, items: List[Dict[str, Any]], model_type: str) -> List[ValidationResult]:
        """Validate a batch of items"""
        results = []
        validator_method = getattr(self, f"validate_{model_type}", None)
        
        if not validator_method:
            raise ValueError(f"No validator available for model type: {model_type}")
        
        for item in items:
            result = validator_method(item)
            results.append(result)
        
        return results


# ============================================================================
# MIGRATION MANAGER
# ============================================================================

class MigrationManager:
    """
    Enterprise database migration manager with rollback capabilities.
    Comprehensive migration tracking and version management.
    """
    
    def __init__(self, database_url -> None: str) -> None:
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self._ensure_migration_table()
    
    def _ensure_migration_table(self) -> None:
        """Ensure migration tracking table exists"""
        migration_table_sql = """
        CREATE TABLE IF NOT EXISTS migration_history (
            id SERIAL PRIMARY KEY,
            migration_id VARCHAR(200) UNIQUE NOT NULL,
            migration_name VARCHAR(500) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            rollback_sql TEXT,
            checksum VARCHAR(200),
            execution_time_seconds FLOAT,
            applied_by VARCHAR(200),
            status VARCHAR(50) DEFAULT 'completed',
            error_message TEXT
        );
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(migration_table_sql))
            conn.commit()
    
    def apply_migration(self, migration_id: str, migration_name: str, 
                       migration_sql: str, rollback_sql: str = None,
                       applied_by: str = "system") -> bool:
        """Apply a database migration"""
        session = self.Session()
        start_time = datetime.utcnow()
        
        try:
            # Check if migration already applied
            existing = session.execute(
                text("SELECT migration_id FROM migration_history WHERE migration_id = :mid"),
                {"mid": migration_id}
            ).fetchone()
            
            if existing:
                raise MigrationError(f"Migration {migration_id} already applied")
            
            # Calculate checksum
            checksum = hashlib.sha256(migration_sql.encode()).hexdigest()
            
            # Execute migration
            session.execute(text(migration_sql))
            
            # Record migration
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            session.execute(
                text("""
                INSERT INTO migration_history 
                (migration_id, migration_name, rollback_sql, checksum, 
                 execution_time_seconds, applied_by, status)
                VALUES (:mid, :name, :rollback, :checksum, :time, :by, 'completed')
                """),
                {
                    "mid": migration_id,
                    "name": migration_name,
                    "rollback": rollback_sql,
                    "checksum": checksum,
                    "time": execution_time,
                    "by": applied_by
                }
            )
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            
            # Record failed migration
            session.execute(
                text("""
                INSERT INTO migration_history 
                (migration_id, migration_name, status, error_message, applied_by)
                VALUES (:mid, :name, 'failed', :error, :by)
                """),
                {
                    "mid": migration_id,
                    "name": migration_name,
                    "error": str(e),
                    "by": applied_by
                }
            )
            session.commit()
            
            raise MigrationError(f"Migration {migration_id} failed: {str(e)}", migration_id)
        
        finally:
            session.close()
    
    def rollback_migration(self, migration_id: str, rolled_back_by: str = "system") -> bool:
        """Rollback a specific migration"""
        session = self.Session()
        
        try:
            # Get migration details
            migration = session.execute(
                text("SELECT rollback_sql FROM migration_history WHERE migration_id = :mid AND status = 'completed'"),
                {"mid": migration_id}
            ).fetchone()
            
            if not migration or not migration[0]:
                raise MigrationError(f"Migration {migration_id} not found or no rollback SQL available")
            
            # Execute rollback
            session.execute(text(migration[0]))
            
            # Update migration status
            session.execute(
                text("UPDATE migration_history SET status = 'rolled_back' WHERE migration_id = :mid"),
                {"mid": migration_id}
            )
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise MigrationError(f"Rollback of {migration_id} failed: {str(e)}", migration_id)
        
        finally:
            session.close()
    
    def get_migration_status(self) -> List[Dict[str, Any]]:
        """Get status of all migrations"""
        session = self.Session()
        
        try:
            migrations = session.execute(
                text("SELECT * FROM migration_history ORDER BY applied_at DESC")
            ).fetchall()
            
            return [
                {
                    "migration_id": row[1],
                    "migration_name": row[2],
                    "applied_at": row[3],
                    "execution_time_seconds": row[5],
                    "applied_by": row[6],
                    "status": row[7],
                    "error_message": row[8]
                }
                for row in migrations
            ]
        
        finally:
            session.close()
    
    def generate_migration_template(self, migration_name: str) -> str:
        """Generate a migration template"""
        migration_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{migration_name.lower().replace(' ', '_')}"
        
        template = f"""-- Migration: {migration_name}
-- ID: {migration_id}
-- Created: {datetime.utcnow().isoformat()}

-- Forward migration (apply changes)
BEGIN;

-- Your migration SQL here
-- Example:
-- CREATE TABLE example_table (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

COMMIT;

-- Rollback migration (undo changes)
-- BEGIN;
-- DROP TABLE IF EXISTS example_table;
-- COMMIT;
"""
        return template


# ============================================================================
# SCHEMA VALIDATOR
# ============================================================================

class SchemaValidator:
    """
    Enterprise schema validation and enforcement.
    Comprehensive schema checking with performance optimization.
    """
    
    def __init__(self, database_url -> None: str) -> None:
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.inspector = inspect(self.engine)
    
    def validate_table_schema(self, table_name: str, expected_schema: Dict[str, Any]) -> ValidationResult:
        """Validate table schema against expected structure"""
        result = ValidationResult()
        
        try:
            # Check if table exists
            if not self.inspector.has_table(table_name):
                result.add_error(f"Table '{table_name}' does not exist")
                return result
            
            # Get actual columns
            actual_columns = {col['name']: col for col in self.inspector.get_columns(table_name)}
            expected_columns = expected_schema.get('columns', {})
            
            # Check for missing columns
            for col_name, col_spec in expected_columns.items():
                if col_name not in actual_columns:
                    result.add_error(f"Missing column '{col_name}' in table '{table_name}'")
                else:
                    # Validate column properties
                    actual_col = actual_columns[col_name]
                    
                    # Check nullable
                    if 'nullable' in col_spec and actual_col['nullable'] != col_spec['nullable']:
                        result.add_warning(f"Column '{col_name}' nullable mismatch: expected {col_spec['nullable']}, got {actual_col['nullable']}")
            
            # Check for extra columns
            for col_name in actual_columns:
                if col_name not in expected_columns:
                    result.add_warning(f"Unexpected column '{col_name}' in table '{table_name}'")
            
            # Validate indexes
            if 'indexes' in expected_schema:
                self._validate_indexes(table_name, expected_schema['indexes'], result)
            
            # Validate foreign keys
            if 'foreign_keys' in expected_schema:
                self._validate_foreign_keys(table_name, expected_schema['foreign_keys'], result)
            
        except Exception as e:
            result.add_error(f"Schema validation error for table '{table_name}': {str(e)}")
        
        return result
    
    def _validate_indexes(self, table_name -> None: str, expected_indexes -> None: List[Dict[str, Any]], result -> None: ValidationResult) -> None:
        """Validate table indexes"""
        actual_indexes = {idx['name']: idx for idx in self.inspector.get_indexes(table_name)}
        
        for expected_idx in expected_indexes:
            idx_name = expected_idx['name']
            if idx_name not in actual_indexes:
                result.add_error(f"Missing index '{idx_name}' on table '{table_name}'")
    
    def _validate_foreign_keys(self, table_name -> None: str, expected_fks -> None: List[Dict[str, Any]], result -> None: ValidationResult) -> None:
        """Validate foreign key constraints"""
        actual_fks = self.inspector.get_foreign_keys(table_name)
        
        expected_fk_names = {fk['name'] for fk in expected_fks}
        actual_fk_names = {fk['name'] for fk in actual_fks}
        
        missing_fks = expected_fk_names - actual_fk_names
        for fk_name in missing_fks:
            result.add_error(f"Missing foreign key '{fk_name}' on table '{table_name}'")
    
    def validate_all_schemas(self, schema_definitions: Dict[str, Dict[str, Any]]) -> Dict[str, ValidationResult]:
        """Validate all table schemas"""
        results = {}
        
        for table_name, schema_def in schema_definitions.items():
            results[table_name] = self.validate_table_schema(table_name, schema_def)
        
        return results


# ============================================================================
# EXAMPLE DATA GENERATOR
# ============================================================================

class ExampleDataGenerator:
    """
    Enterprise test data generator for development and testing.
    Realistic data generation with relationships and constraints.
    """
    
    def __init__(self) -> None:
        self.faker_available = self._check_faker()
        if self.faker_available:
            from faker import Faker
            self.fake = Faker()
    
    def _check_faker(self) -> bool:
        """Check if Faker library is available"""
        try:
            import faker
            return True
        except ImportError:
            return False
    
    def generate_user_data(self, count: int = 10, user_type: str = None) -> List[Dict[str, Any]]:
        """Generate example user data"""
        users = []
        user_types = ["musician", "blogger", "photographer", "influencer", "comedian", "podcaster"]
        
        for i in range(count):
            user_id = str(uuid.uuid4())
            
            if self.faker_available:
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                email = self.fake.email()
                username = self.fake.user_name()
            else:
                first_name = f"User{i+1}"
                last_name = "Test"
                email = f"user{i+1}@example.com"
                username = f"user{i+1}"
            
            user_data = {
                "id": user_id,
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "display_name": f"{first_name} {last_name}",
                "user_type": user_type or user_types[i % len(user_types)],
                "status": "active",
                "subscription_tier": "free",
                "bio": f"Test bio for {first_name} {last_name}",
                "total_content_count": 0,
                "total_followers": 0,
                "total_views": 0,
                "total_revenue": 0.0,
                "verification_status": "unverified",
                "trust_score": 0.0,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "is_verified": False,
                "is_deleted": False
            }
            
            users.append(user_data)
        
        return users
    
    def generate_content_data(self, user_ids: List[str], count: int = 50) -> List[Dict[str, Any]]:
        """Generate example content data"""
        content_items = []
        content_types = ["music", "video", "image", "text", "podcast"]
        visibilities = ["public", "private", "unlisted"]
        
        for i in range(count):
            content_id = str(uuid.uuid4())
            user_id = user_ids[i % len(user_ids)] if user_ids else str(uuid.uuid4())
            content_type = content_types[i % len(content_types)]
            
            content_data = {
                "id": content_id,
                "user_id": user_id,
                "content_type": content_type,
                "status": "published",
                "visibility": visibilities[i % len(visibilities)],
                "title": f"Sample {content_type.title()} Content {i+1}",
                "description": f"This is a sample {content_type} content item for testing purposes.",
                "tags": [content_type, "sample", "test"],
                "categories": ["entertainment"],
                "language": "en",
                "view_count": i * 10,
                "like_count": i * 2,
                "share_count": i,
                "comment_count": i,
                "revenue_total": i * 1.5,
                "created_at": datetime.utcnow(),
                "published_at": datetime.utcnow(),
                "is_featured": i % 10 == 0,
                "is_trending": i % 15 == 0,
                "is_monetized": i % 5 == 0,
                "is_deleted": False
            }
            
            content_items.append(content_data)
        
        return content_items
    
    def generate_revenue_data(self, user_ids: List[str], content_ids: List[str], count: int = 100) -> List[Dict[str, Any]]:
        """Generate example revenue data"""
        revenue_records = []
        revenue_sources = ["ads", "subscriptions", "licensing", "donations", "nft_sales"]
        currencies = ["USD", "EUR", "GBP"]
        platforms = ["youtube", "spotify", "instagram", "platform_wide"]
        
        for i in range(count):
            revenue_id = str(uuid.uuid4())
            user_id = user_ids[i % len(user_ids)] if user_ids else str(uuid.uuid4())
            content_id = content_ids[i % len(content_ids)] if content_ids and i % 2 == 0 else None
            
            gross_amount = round((i + 1) * 2.5, 2)
            platform_fee = round(gross_amount * 0.15, 2)
            net_amount = round(gross_amount - platform_fee, 2)
            
            revenue_data = {
                "id": revenue_id,
                "user_id": user_id,
                "content_id": content_id,
                "revenue_source": revenue_sources[i % len(revenue_sources)],
                "status": "processed",
                "gross_amount": gross_amount,
                "net_amount": net_amount,
                "platform_fee": platform_fee,
                "currency": currencies[i % len(currencies)],
                "platform": platforms[i % len(platforms)],
                "earned_date": datetime.utcnow(),
                "payment_date": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "is_recurring": i % 10 == 0,
                "is_disputed": False,
                "is_deleted": False
            }
            
            revenue_records.append(revenue_data)
        
        return revenue_records
    
    def generate_analytics_data(self, user_ids: List[str], content_ids: List[str], count: int = 200) -> List[Dict[str, Any]]:
        """Generate example analytics data"""
        analytics_records = []
        analytics_types = ["views", "engagement", "revenue", "performance"]
        metric_types = ["daily", "weekly", "monthly", "real_time"]
        time_granularities = ["hour", "day", "week", "month"]
        
        for i in range(count):
            analytics_id = str(uuid.uuid4())
            user_id = user_ids[i % len(user_ids)] if user_ids else str(uuid.uuid4())
            content_id = content_ids[i % len(content_ids)] if content_ids and i % 3 == 0 else None
            
            analytics_data = {
                "id": analytics_id,
                "user_id": user_id,
                "content_id": content_id,
                "analytics_type": analytics_types[i % len(analytics_types)],
                "metric_type": metric_types[i % len(metric_types)],
                "time_granularity": time_granularities[i % len(time_granularities)],
                "measurement_date": datetime.utcnow(),
                "value": (i + 1) * 10.5,
                "metric_name": f"test_metric_{i % 10}",
                "platform": "platform_wide",
                "created_at": datetime.utcnow(),
                "is_deleted": False
            }
            
            analytics_records.append(analytics_data)
        
        return analytics_records


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_user(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for user validation"""
    validator = ModelDataValidator()
    return validator.validate_user(data)


def validate_content(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for content validation"""
    validator = ModelDataValidator()
    return validator.validate_content(data)


def validate_revenue(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for revenue validation"""
    validator = ModelDataValidator()
    return validator.validate_revenue(data)


def validate_analytics(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for analytics validation"""
    validator = ModelDataValidator()
    return validator.validate_analytics(data)


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Exceptions
    'ValidationError', 'MigrationError', 'SchemaValidationError',
    
    # Result Classes
    'ValidationResult',
    
    # Main Classes
    'ModelDataValidator', 'MigrationManager', 'SchemaValidator', 'ExampleDataGenerator',
    
    # Convenience Functions
    'validate_user', 'validate_content', 'validate_revenue', 'validate_analytics'
]