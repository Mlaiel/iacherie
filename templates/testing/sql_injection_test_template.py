# WARNING: Potential SQL injection risk - use parameterized queries
"""
🛡️ SQL INJECTION TEST TEMPLATE - SECURITY EXPERT IMPLEMENTATION
=================================================================

Enterprise-grade SQL injection prevention testing template for iacherie Creator Economy Platform.
Comprehensive SQL injection security testing covering:
- Classic SQL injection prevention
- Blind SQL injection detection
- Time-based SQL injection prevention
- Union-based SQL injection prevention
- Boolean-based SQL injection prevention
- NoSQL injection prevention (MongoDB, Redis)
- Prepared statement validation
- ORM security testing

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Security Expert & SQL Injection Prevention Specialist
Team: Lead Dev IA + Backend Senior + Security Engineer + DBA Expert
Version: 1.0.0
"""

import pytest
import asyncio
import json
import time
import re
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from faker import Faker
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pymongo
import redis.asyncio as redis

# Application imports
from core.security import SQLInjectionProtection, QueryValidator, DatabaseSecurity
from core.database import get_async_session, Database
from core.config import get_settings
from utils.exceptions import SQLInjectionError, SecurityError, ValidationError
from monitoring.test_metrics import TestMetricsCollector
from tests.fixtures import create_test_database, create_test_data

# Initialize test utilities
fake = Faker()
settings = get_settings()


class SQLInjectionType(Enum):
    """SQL injection attack type classifications"""
    CLASSIC = "classic"
    UNION_BASED = "union_based"
    BOOLEAN_BASED = "boolean_based"
    TIME_BASED = "time_based"
    ERROR_BASED = "error_based"
    BLIND = "blind"
    SECOND_ORDER = "second_order"
    NOSQL = "nosql"


class DatabaseType(Enum):
    """Database type classifications"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"


@dataclass
class SQLInjectionPayload:
    """SQL injection test payload with metadata"""
    
    payload: str
    injection_type: SQLInjectionType
    database_type: DatabaseType
    description: str
    expected_blocked: bool = True
    severity: str = "high"
    context: str = "query"
    
    def __post_init__(self):
        self.payload_hash = hash(self.payload)


@dataclass
class SQLTestContext:
    """SQL injection test context"""
    
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    database_url: str = "postgresql://test:test@localhost/test_db"
    mongodb_url: str = "mongodb://localhost:27017/test_db"
    redis_url: str = "redis://localhost:6379/0"
    test_tables: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.test_tables = ["users", "content", "collaborations", "payments"]


class SQLInjectionTestTemplate:
    """
    🛡️ ENTERPRISE SQL INJECTION PREVENTION TESTING FRAMEWORK
    
    Comprehensive SQL injection prevention testing template providing:
    - Classic SQL injection attack detection
    - Advanced blind SQL injection prevention
    - Time-based attack detection and prevention
    - Union-based injection prevention
    - Boolean-based injection detection
    - NoSQL injection prevention (MongoDB, Redis)
    - Prepared statement security validation
    - ORM security testing and validation
    - Creator Economy database security
    - Performance impact assessment
    """
    
    def __init__(self):
        self.sql_protection = SQLInjectionProtection()
        self.query_validator = QueryValidator()
        self.db_security = DatabaseSecurity()
        self.metrics_collector = TestMetricsCollector("sql_injection")
        self.test_payloads = self._generate_sql_injection_payloads()
        
    async def setup_test_environment(self) -> SQLTestContext:
        """Setup isolated SQL injection test environment"""
        context = SQLTestContext()
        
        # Setup test database connections
        await self._setup_test_databases(context)
        
        # Create test data
        await self._create_test_data(context)
        
        return context
    
    async def teardown_test_environment(self, context: SQLTestContext):
        """Clean up SQL injection test environment"""
        try:
            # Clean up test data
            await self._cleanup_test_data(context)
            
            # Close database connections
            await self._cleanup_test_databases(context)
            
        except Exception as e:
            self.metrics_collector.record_error("teardown_failed", str(e))
    
    def _generate_sql_injection_payloads(self) -> List[SQLInjectionPayload]:
        """Generate comprehensive SQL injection test payloads"""
        
        payloads = [
            # Classic SQL injection
            SQLInjectionPayload(
                payload="' OR '1'='1",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="Classic OR injection"
            ),
            
            SQLInjectionPayload(
                payload="' OR 1=1--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.MYSQL,
                description="Classic OR with comment"
            ),
            
            SQLInjectionPayload(
                payload="'; DROP TABLE users;--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="Table drop injection"
            ),
            
            # Union-based injection
            SQLInjectionPayload(
                payload="' UNION SELECT username, password FROM users--",
                injection_type=SQLInjectionType.UNION_BASED,
                database_type=DatabaseType.POSTGRESQL,
                description="Union select injection"
            ),
            
            SQLInjectionPayload(
                payload="' UNION ALL SELECT NULL, concat(username,0x3a,password), NULL FROM users#",
                injection_type=SQLInjectionType.UNION_BASED,
                database_type=DatabaseType.MYSQL,
                description="Union all with concat"
            ),
            
            # Boolean-based blind injection
            SQLInjectionPayload(
                payload="' AND (SELECT substring(username,1,1) FROM users WHERE id=1)='a",
                injection_type=SQLInjectionType.BOOLEAN_BASED,
                database_type=DatabaseType.POSTGRESQL,
                description="Boolean substring extraction"
            ),
            
            SQLInjectionPayload(
                payload="' AND (SELECT count(*) FROM users)>0--",
                injection_type=SQLInjectionType.BOOLEAN_BASED,
                database_type=DatabaseType.MYSQL,
                description="Boolean count injection"
            ),
            
            # Time-based blind injection
            SQLInjectionPayload(
                payload="'; SELECT pg_sleep(5)--",
                injection_type=SQLInjectionType.TIME_BASED,
                database_type=DatabaseType.POSTGRESQL,
                description="PostgreSQL time delay"
            ),
            
            SQLInjectionPayload(
                payload="' AND (SELECT sleep(5))#",
                injection_type=SQLInjectionType.TIME_BASED,
                database_type=DatabaseType.MYSQL,
                description="MySQL time delay"
            ),
            
            # Error-based injection
            SQLInjectionPayload(
                payload="' AND extractvalue(rand(),concat(0x3a,(SELECT version())))--",
                injection_type=SQLInjectionType.ERROR_BASED,
                database_type=DatabaseType.MYSQL,
                description="MySQL extractvalue error"
            ),
            
            SQLInjectionPayload(
                payload="' AND (SELECT * FROM (SELECT count(*),concat(version(),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
                injection_type=SQLInjectionType.ERROR_BASED,
                database_type=DatabaseType.MYSQL,
                description="MySQL duplicate key error"
            ),
            
            # Second-order injection
            SQLInjectionPayload(
                payload="admin'; INSERT INTO users (username) VALUES ('injected')--",
                injection_type=SQLInjectionType.SECOND_ORDER,
                database_type=DatabaseType.POSTGRESQL,
                description="Second-order insert injection"
            ),
            
            # NoSQL injection (MongoDB)
            SQLInjectionPayload(
                payload='{"username": {"$ne": null}, "password": {"$ne": null}}',
                injection_type=SQLInjectionType.NOSQL,
                database_type=DatabaseType.MONGODB,
                description="MongoDB $ne injection"
            ),
            
            SQLInjectionPayload(
                payload='{"username": {"$regex": ".*"}, "password": {"$regex": ".*"}}',
                injection_type=SQLInjectionType.NOSQL,
                database_type=DatabaseType.MONGODB,
                description="MongoDB regex injection"
            ),
            
            SQLInjectionPayload(
                payload='{"$where": "this.username == this.password"}',
                injection_type=SQLInjectionType.NOSQL,
                database_type=DatabaseType.MONGODB,
                description="MongoDB $where injection"
            ),
            
            # Advanced payloads with encoding
            SQLInjectionPayload(
                payload="' OR 1=1#",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.MYSQL,
                description="Basic injection with hash comment"
            ),
            
            SQLInjectionPayload(
                payload="%27%20OR%201%3D1--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="URL encoded injection"
            ),
            
            # Creator Economy specific payloads
            SQLInjectionPayload(
                payload="'; UPDATE content SET owner_id='attacker' WHERE title LIKE '%'--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="Content ownership hijack",
                context="creator_content"
            ),
            
            SQLInjectionPayload(
                payload="' UNION SELECT api_key, secret FROM creator_keys--",
                injection_type=SQLInjectionType.UNION_BASED,
                database_type=DatabaseType.POSTGRESQL,
                description="API key extraction",
                context="creator_api"
            ),
            
            SQLInjectionPayload(
                payload="'; INSERT INTO collaborations (content_id, user_id, permission) VALUES (ALL, 'attacker', 'admin')--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="Collaboration privilege escalation",
                context="collaboration"
            ),
            
            # Payment system injections
            SQLInjectionPayload(
                payload="'; UPDATE payments SET amount=0.01 WHERE user_id='victim'--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.POSTGRESQL,
                description="Payment amount manipulation",
                context="payment"
            ),
            
            # Advanced filter bypass
            SQLInjectionPayload(
                payload="' /**/OR/**/1=1--",
                injection_type=SQLInjectionType.CLASSIC,
                database_type=DatabaseType.MYSQL,
                description="Comment-based filter bypass"
            ),
            
            SQLInjectionPayload(
                payload="' UNI/**/ON SEL/**/ECT * FROM users--",
                injection_type=SQLInjectionType.UNION_BASED,
                database_type=DatabaseType.MYSQL,
                description="Keyword splitting bypass"
            ),
            
            SQLInjectionPayload(
                payload="' AND 1=1 AND '1'='1",
                injection_type=SQLInjectionType.BOOLEAN_BASED,
                database_type=DatabaseType.POSTGRESQL,
                description="Multiple condition bypass"
            )
        ]
        
        return payloads
    
    async def _setup_test_databases(self, context: SQLTestContext):
        """Setup test database connections"""
        # Implementation would setup test database connections
        pass
    
    async def _create_test_data(self, context: SQLTestContext):
        """Create test data for injection testing"""
        # Implementation would create test data
        pass
    
    async def _cleanup_test_data(self, context: SQLTestContext):
        """Clean up test data"""
        # Implementation would clean up test data
        pass
    
    async def _cleanup_test_databases(self, context: SQLTestContext):
        """Clean up test database connections"""
        # Implementation would clean up database connections
        pass

    # ==================== CLASSIC SQL INJECTION PREVENTION TESTS ====================
    
    async def test_classic_sql_injection_prevention(self, context: SQLTestContext):
        """Test classic SQL injection attack prevention"""
        start_time = time.time()
        
        try:
            classic_payloads = [
                payload for payload in self.test_payloads 
                if payload.injection_type == SQLInjectionType.CLASSIC
            ]
            
            for payload in classic_payloads:
                # Test query parameter injection
                query_params = {
                    "username": payload.payload,
                    "email": "test@example.com",
                    "content_id": "123"
                }
                
                is_safe = await self.sql_protection.validate_query_parameters(
                    query_params,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"SQL injection not blocked: {payload.description}"
                
                # Test form data injection
                form_data = {
                    "search": payload.payload,
                    "category": "music",
                    "user_id": context.user_id
                }
                
                is_safe = await self.sql_protection.validate_form_data(
                    form_data,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Form SQL injection not blocked: {payload.description}"
                
                # Test JSON payload injection
                json_data = {
                    "filters": {
                        "title": payload.payload,
                        "status": "published"
                    },
                    "user_id": context.user_id
                }
                
                is_safe = await self.sql_protection.validate_json_data(
                    json_data,
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"JSON SQL injection not blocked: {payload.description}"
            
            # Test specific Creator Economy queries
            creator_queries = [
                {
                    "query": "SELECT * FROM content WHERE owner_id = %s AND title LIKE %s",
                    "params": [context.user_id, "'; DROP TABLE content;--"],
                    "description": "Content search injection"
                },
                {
                    "query": "UPDATE collaborations SET status = %s WHERE id = %s",
                    "params": ["'; DELETE FROM collaborations;--", "123"],
                    "description": "Collaboration update injection"
                },
                {
                    "query": "INSERT INTO payments (user_id, amount) VALUES (%s, %s)",
                    "params": [context.user_id, "'; UPDATE payments SET amount=999999;--"],
                    "description": "Payment insert injection"
                }
            ]
            
            for query_test in creator_queries:
                is_safe = await self.sql_protection.validate_parameterized_query(
                    query_test["query"],
                    query_test["params"],
                    context
                )
                
                assert is_safe is False, f"Parameterized injection not blocked: {query_test['description']}"
            
            self.metrics_collector.record_success(
                "classic_sql_injection_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("classic_sql_injection_prevention_failed", str(e))
            raise AssertionError(f"Classic SQL injection prevention test failed: {e}")
    
    async def test_prepared_statement_validation(self, context: SQLTestContext):
        """Test prepared statement security validation"""
        start_time = time.time()
        
        try:
            # Test safe prepared statements
            safe_queries = [
                {
                    "query": "SELECT * FROM users WHERE id = $1",
                    "params": [123],
                    "description": "Safe user lookup"
                },
                {
                    "query": "INSERT INTO content (title, body, owner_id) VALUES ($1, $2, $3)",
                    "params": ["Safe Title", "Safe content body", context.user_id],
                    "description": "Safe content insert"
                },
                {
                    "query": "UPDATE collaborations SET status = $1 WHERE id = $2 AND user_id = $3",
                    "params": ["accepted", "123", context.user_id],
                    "description": "Safe collaboration update"
                }
            ]
            
            for query in safe_queries:
                is_safe = await self.sql_protection.validate_prepared_statement(
                    query["query"],
                    query["params"],
                    context
                )
                
                assert is_safe is True, f"Safe prepared statement incorrectly flagged: {query['description']}"
            
            # Test unsafe dynamic queries
            unsafe_queries = [
                {
                    "query": "SELECT * FROM users WHERE username = '" + "' OR '1'='1" + "'",
                    "params": [],
                    "description": "Dynamic string concatenation"
                },
                {
                    "query": f"DELETE FROM content WHERE id = {'; DROP TABLE content;--'}",
                    "params": [],
                    "description": "F-string injection"
                },
                {
                    "query": "SELECT * FROM users WHERE id = %s" % "1; DROP TABLE users;",
                    "params": [],
                    "description": "String formatting injection"
                }
            ]
            
            for query in unsafe_queries:
                is_safe = await self.sql_protection.validate_prepared_statement(
                    query["query"],
                    query["params"],
                    context
                )
                
                assert is_safe is False, f"Unsafe dynamic query not detected: {query['description']}"
            
            # Test parameter type validation
            type_validations = [
                {
                    "query": "SELECT * FROM users WHERE id = $1",
                    "params": ["'; DROP TABLE users;--"],  # String instead of int
                    "expected_types": [int],
                    "description": "Parameter type mismatch"
                },
                {
                    "query": "UPDATE content SET view_count = $1 WHERE id = $2",
                    "params": [999, "'; DELETE FROM content;--"],
                    "expected_types": [int, int],
                    "description": "Second parameter type mismatch"
                }
            ]
            
            for validation in type_validations:
                is_valid = await self.sql_protection.validate_parameter_types(
                    validation["params"],
                    validation["expected_types"],
                    context
                )
                
                assert is_valid is False, f"Parameter type validation failed: {validation['description']}"
            
            self.metrics_collector.record_success(
                "prepared_statement_validation",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("prepared_statement_validation_failed", str(e))
            raise AssertionError(f"Prepared statement validation test failed: {e}")

    # ==================== BLIND SQL INJECTION PREVENTION TESTS ====================
    
    async def test_blind_sql_injection_prevention(self, context: SQLTestContext):
        """Test blind SQL injection attack prevention"""
        start_time = time.time()
        
        try:
            # Boolean-based blind injection tests
            boolean_payloads = [
                payload for payload in self.test_payloads 
                if payload.injection_type == SQLInjectionType.BOOLEAN_BASED
            ]
            
            for payload in boolean_payloads:
                # Test response time analysis
                response_times = []
                
                for _ in range(5):  # Multiple requests to establish baseline
                    request_start = time.time()
                    
                    is_safe = await self.sql_protection.validate_query_parameters(
                        {"search": payload.payload},
                        context
                    )
                    
                    response_time = time.time() - request_start
                    response_times.append(response_time)
                
                avg_response_time = sum(response_times) / len(response_times)
                
                # Response time should be consistent (not indicating successful injection)
                assert max(response_times) - min(response_times) < 0.5, f"Response time variance indicates possible injection: {payload.description}"
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Boolean injection not blocked: {payload.description}"
            
            # Test character-by-character extraction patterns
            extraction_patterns = [
                "' AND (SELECT substring(username,{pos},1) FROM users WHERE id=1)='{char}",
                "' AND (SELECT ascii(substring(password,{pos},1)) FROM users WHERE id=1)={ascii_val}",
                "' AND (SELECT length(api_key) FROM creator_keys WHERE user_id=1)={length}",
                "' AND (SELECT count(*) FROM content WHERE owner_id='{user}')>{count}"
            ]
            
            for pattern in extraction_patterns:
                # Test with various positions/values
                test_injections = [
                    pattern.format(pos=1, char='a', ascii_val=97, length=32, user='admin', count=10),
                    pattern.format(pos=2, char='b', ascii_val=98, length=64, user='test', count=5),
                    pattern.format(pos=3, char='c', ascii_val=99, length=16, user='creator', count=1)
                ]
                
                for injection in test_injections:
                    is_safe = await self.sql_protection.validate_query_parameters(
                        {"filter": injection},
                        context
                    )
                    
                    assert is_safe is False, f"Character extraction pattern not blocked: {injection[:50]}..."
            
            self.metrics_collector.record_success(
                "blind_sql_injection_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("blind_sql_injection_prevention_failed", str(e))
            raise AssertionError(f"Blind SQL injection prevention test failed: {e}")
    
    async def test_time_based_sql_injection_prevention(self, context: SQLTestContext):
        """Test time-based SQL injection attack prevention"""
        start_time = time.time()
        
        try:
            time_based_payloads = [
                payload for payload in self.test_payloads 
                if payload.injection_type == SQLInjectionType.TIME_BASED
            ]
            
            for payload in time_based_payloads:
                # Test query execution time
                execution_start = time.time()
                
                is_safe = await self.sql_protection.validate_query_parameters(
                    {"search": payload.payload},
                    context
                )
                
                execution_time = time.time() - execution_start
                
                # Query should not take significantly longer (indicating successful delay injection)
                assert execution_time < 2.0, f"Query execution time indicates successful injection: {execution_time}s for {payload.description}"
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Time-based injection not blocked: {payload.description}"
            
            # Test database-specific time delay functions
            delay_functions = {
                DatabaseType.POSTGRESQL: [
                    "pg_sleep(5)",
                    "SELECT pg_sleep(10)",
                    "(SELECT count(*) FROM generate_series(1,1000000))"
                ],
                DatabaseType.MYSQL: [
                    "sleep(5)",
                    "SELECT sleep(10)",
                    "benchmark(10000000,encode('hello','goodbye'))"
                ],
                DatabaseType.SQLITE: [
                    "(SELECT count(*) FROM sqlite_master WHERE tbl_name LIKE '%')",
                    "randomblob(100000000)"
                ]
            }
            
            for db_type, functions in delay_functions.items():
                for delay_func in functions:
                    injection_payload = f"'; SELECT {delay_func}--"
                    
                    execution_start = time.time()
                    
                    is_safe = await self.sql_protection.validate_query_parameters(
                        {"data": injection_payload},
                        context
                    )
                    
                    execution_time = time.time() - execution_start
                    
                    assert execution_time < 1.0, f"Delay function not blocked: {delay_func}"
                    assert is_safe is False, f"Time delay injection not detected: {delay_func}"
            
            self.metrics_collector.record_success(
                "time_based_sql_injection_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("time_based_sql_injection_prevention_failed", str(e))
            raise AssertionError(f"Time-based SQL injection prevention test failed: {e}")

    # ==================== UNION-BASED SQL INJECTION PREVENTION TESTS ====================
    
    async def test_union_based_sql_injection_prevention(self, context: SQLTestContext):
        """Test union-based SQL injection attack prevention"""
        start_time = time.time()
        
        try:
            union_payloads = [
                payload for payload in self.test_payloads 
                if payload.injection_type == SQLInjectionType.UNION_BASED
            ]
            
            for payload in union_payloads:
                # Test union injection detection
                is_safe = await self.sql_protection.validate_query_parameters(
                    {"search": payload.payload},
                    context
                )
                
                if payload.expected_blocked:
                    assert is_safe is False, f"Union injection not blocked: {payload.description}"
            
            # Test Creator Economy specific union attacks
            creator_union_attacks = [
                "' UNION SELECT username, email, api_key FROM creator_profiles--",
                "' UNION SELECT password_hash, mfa_secret, NULL FROM users--",
                "' UNION SELECT content_id, revenue, payment_info FROM monetization--",
                "' UNION SELECT collaboration_id, permissions, revenue_share FROM collaborations--",
                "' UNION SELECT file_path, encryption_key, access_token FROM media_files--"
            ]
            
            for attack in creator_union_attacks:
                is_safe = await self.sql_protection.validate_query_parameters(
                    {"filter": attack},
                    context
                )
                
                assert is_safe is False, f"Creator Economy union attack not blocked: {attack[:50]}..."
            
            # Test union injection with different column counts
            column_variations = [
                "' UNION SELECT NULL--",
                "' UNION SELECT NULL, NULL--",
                "' UNION SELECT NULL, NULL, NULL--",
                "' UNION SELECT NULL, NULL, NULL, NULL--",
                "' UNION SELECT NULL, NULL, NULL, NULL, NULL--"
            ]
            
            for variation in column_variations:
                is_safe = await self.sql_protection.validate_query_parameters(
                    {"data": variation},
                    context
                )
                
                assert is_safe is False, f"Union column variation not blocked: {variation}"
            
            # Test union with information schema access
            info_schema_attacks = [
                "' UNION SELECT table_name, column_name FROM information_schema.columns--",
                "' UNION SELECT schema_name, NULL FROM information_schema.schemata--",
                "' UNION SELECT table_schema, table_name FROM information_schema.tables--",
                "' UNION SELECT constraint_name, table_name FROM information_schema.table_constraints--"
            ]
            
            for attack in info_schema_attacks:
                is_safe = await self.sql_protection.validate_query_parameters(
                    {"query": attack},
                    context
                )
                
                assert is_safe is False, f"Information schema attack not blocked: {attack[:50]}..."
            
            self.metrics_collector.record_success(
                "union_based_sql_injection_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("union_based_sql_injection_prevention_failed", str(e))
            raise AssertionError(f"Union-based SQL injection prevention test failed: {e}")

    # ==================== NOSQL INJECTION PREVENTION TESTS ====================
    
    async def test_nosql_injection_prevention(self, context: SQLTestContext):
        """Test NoSQL injection attack prevention"""
        start_time = time.time()
        
        try:
            nosql_payloads = [
                payload for payload in self.test_payloads 
                if payload.injection_type == SQLInjectionType.NOSQL
            ]
            
            for payload in nosql_payloads:
                # Test MongoDB injection
                if payload.database_type == DatabaseType.MONGODB:
                    try:
                        # Parse JSON payload
                        mongo_query = json.loads(payload.payload)
                        
                        is_safe = await self.sql_protection.validate_mongodb_query(
                            mongo_query,
                            context
                        )
                        
                        if payload.expected_blocked:
                            assert is_safe is False, f"MongoDB injection not blocked: {payload.description}"
                    
                    except json.JSONDecodeError:
                        # String-based MongoDB injection
                        is_safe = await self.sql_protection.validate_mongodb_string(
                            payload.payload,
                            context
                        )
                        
                        if payload.expected_blocked:
                            assert is_safe is False, f"MongoDB string injection not blocked: {payload.description}"
            
            # Test specific MongoDB injection techniques
            mongodb_attacks = [
                # Operator injection
                {"username": {"$ne": None}},
                {"password": {"$regex": ".*"}},
                {"$where": "this.username == this.password"},
                {"$where": "sleep(5000)"},
                
                # JavaScript injection
                {"$where": "function() { return true; }"},
                {"$where": "obj.credits - obj.debits < 0"},
                
                # Creator Economy specific
                {"content.owner_id": {"$ne": context.user_id}},
                {"collaborators": {"$elemMatch": {"user_id": {"$ne": None}}}},
                {"revenue_data": {"$exists": True}},
                {"$where": "this.api_key.length > 0"}
            ]
            
            for attack in mongodb_attacks:
                is_safe = await self.sql_protection.validate_mongodb_query(
                    attack,
                    context
                )
                
                assert is_safe is False, f"MongoDB attack not blocked: {json.dumps(attack)[:50]}..."
            
            # Test Redis injection prevention
            redis_attacks = [
                "FLUSHALL",
                "CONFIG SET dir /tmp/",
                "EVAL 'return 1' 0",
                "SCRIPT LOAD 'return redis.call(\"get\", \"secret\")'",
                "KEYS *",
                "GET user:*:password",
                "HGETALL creator:api_keys",
                "LPUSH malicious_list 'injected_data'"
            ]
            
            for attack in redis_attacks:
                is_safe = await self.sql_protection.validate_redis_command(
                    attack,
                    context
                )
                
                assert is_safe is False, f"Redis attack not blocked: {attack}"
            
            self.metrics_collector.record_success(
                "nosql_injection_prevention",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("nosql_injection_prevention_failed", str(e))
            raise AssertionError(f"NoSQL injection prevention test failed: {e}")

    # ==================== ORM SECURITY TESTING ====================
    
    async def test_orm_security_validation(self, context: SQLTestContext):
        """Test ORM security and injection prevention"""
        start_time = time.time()
        
        try:
            # Test SQLAlchemy security
            sqlalchemy_patterns = [
                # Safe patterns
                {
                    "query": "session.query(User).filter(User.id == user_id)",
                    "is_safe": True,
                    "description": "Safe parameterized filter"
                },
                {
                    "query": "session.execute(text('SELECT * FROM users WHERE id = :user_id'), {'user_id': 123})",
                    "is_safe": True,
                    "description": "Safe named parameter"
                },
                
                # Unsafe patterns
                {
                    "query": f"session.execute(text('SELECT * FROM users WHERE name = \\'{\"'; DROP TABLE users;--\"}\\'))",
                    "is_safe": False,
                    "description": "Unsafe string interpolation"
                },
                {
                    "query": "session.query(User).filter(text(f'username = \\'{user_input}\\'))",
                    "is_safe": False,
                    "description": "Unsafe f-string in filter"
                }
            ]
            
            for pattern in sqlalchemy_patterns:
                is_safe = await self.sql_protection.validate_sqlalchemy_pattern(
                    pattern["query"],
                    context
                )
                
                assert is_safe == pattern["is_safe"], f"SQLAlchemy pattern validation failed: {pattern['description']}"
            
            # Test raw SQL execution validation
            raw_sql_queries = [
                # Safe raw queries
                {
                    "query": "SELECT * FROM content WHERE owner_id = %s AND status = %s",
                    "params": [context.user_id, "published"],
                    "is_safe": True
                },
                {
                    "query": "INSERT INTO collaborations (content_id, user_id) VALUES (%s, %s)",
                    "params": ["123", context.user_id],
                    "is_safe": True
                },
                
                # Unsafe raw queries
                {
                    "query": f"SELECT * FROM users WHERE username = '{\"'; DROP TABLE users;--\"}'",
                    "params": [],
                    "is_safe": False
                },
                {
                    "query": "DELETE FROM content WHERE id = " + "'; DROP TABLE content;--",
                    "params": [],
                    "is_safe": False
                }
            ]
            
            for query_test in raw_sql_queries:
                is_safe = await self.sql_protection.validate_raw_sql(
                    query_test["query"],
                    query_test["params"],
                    context
                )
                
                assert is_safe == query_test["is_safe"], f"Raw SQL validation failed: {query_test['query'][:50]}..."
            
            # Test ORM relationship traversal security
            relationship_attacks = [
                "user.content.owner.api_key",  # Unauthorized data access
                "collaboration.content.revenue_data",  # Financial data access
                "user.payments.payment_method",  # Payment info access
                "creator.analytics.revenue_breakdown"  # Analytics access
            ]
            
            for attack in relationship_attacks:
                is_safe = await self.sql_protection.validate_relationship_access(
                    attack,
                    context.user_id,
                    context
                )
                
                # Should check authorization for sensitive relationships
                assert is_safe is False, f"Unauthorized relationship access allowed: {attack}"
            
            self.metrics_collector.record_success(
                "orm_security_validation",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("orm_security_validation_failed", str(e))
            raise AssertionError(f"ORM security validation test failed: {e}")

    # ==================== CREATOR ECONOMY SPECIFIC TESTS ====================
    
    async def test_creator_economy_sql_security(self, context: SQLTestContext):
        """Test Creator Economy specific SQL injection scenarios"""
        start_time = time.time()
        
        try:
            # Test content management injection scenarios
            content_attacks = [
                {
                    "endpoint": "/api/content/search",
                    "payload": {"title": "'; UPDATE content SET owner_id='attacker' WHERE '1'='1'--"},
                    "description": "Content ownership hijacking"
                },
                {
                    "endpoint": "/api/content/create",
                    "payload": {"tags": ["music", "'; DROP TABLE content_tags;--"]},
                    "description": "Tag injection attack"
                },
                {
                    "endpoint": "/api/content/metadata",
                    "payload": {"custom_field": "value'; INSERT INTO admin_users VALUES('hacker','password');--"},
                    "description": "Metadata injection"
                }
            ]
            
            for attack in content_attacks:
                is_safe = await self.sql_protection.validate_api_payload(
                    attack["endpoint"],
                    attack["payload"],
                    context
                )
                
                assert is_safe is False, f"Content attack not blocked: {attack['description']}"
            
            # Test collaboration injection scenarios
            collaboration_attacks = [
                {
                    "action": "invite_collaborator",
                    "payload": {"email": "test@example.com'; UPDATE collaborations SET permission='admin' WHERE '1'='1'--"},
                    "description": "Collaboration privilege escalation"
                },
                {
                    "action": "set_revenue_share",
                    "payload": {"percentage": "50'; UPDATE collaborations SET revenue_share=100 WHERE collaborator_id='attacker'--"},
                    "description": "Revenue share manipulation"
                },
                {
                    "action": "update_permissions",
                    "payload": {"permissions": ["edit'; INSERT INTO collaboration_permissions VALUES('admin');--"]},
                    "description": "Permission injection"
                }
            ]
            
            for attack in collaboration_attacks:
                is_safe = await self.sql_protection.validate_collaboration_action(
                    attack["action"],
                    attack["payload"],
                    context
                )
                
                assert is_safe is False, f"Collaboration attack not blocked: {attack['description']}"
            
            # Test monetization injection scenarios
            monetization_attacks = [
                {
                    "action": "set_pricing",
                    "payload": {"amount": "9.99'; UPDATE payments SET amount=0.01 WHERE user_id='victim'--"},
                    "description": "Price manipulation"
                },
                {
                    "action": "process_payment",
                    "payload": {"payment_method": "card_123'; INSERT INTO payments VALUES('attacker',999999,'completed');--"},
                    "description": "Payment injection"
                },
                {
                    "action": "revenue_report",
                    "payload": {"period": "month'; UNION SELECT api_key,secret FROM payment_providers--"},
                    "description": "Payment provider data extraction"
                }
            ]
            
            for attack in monetization_attacks:
                is_safe = await self.sql_protection.validate_monetization_action(
                    attack["action"],
                    attack["payload"],
                    context
                )
                
                assert is_safe is False, f"Monetization attack not blocked: {attack['description']}"
            
            # Test analytics injection scenarios
            analytics_attacks = [
                {
                    "query_type": "content_performance",
                    "filters": {"date_range": "2024-01-01'; DROP TABLE analytics;--"},
                    "description": "Analytics table destruction"
                },
                {
                    "query_type": "revenue_breakdown",
                    "filters": {"creator_id": "'; UNION SELECT user_id,total_revenue FROM creator_earnings--"},
                    "description": "Revenue data extraction"
                },
                {
                    "query_type": "user_engagement",
                    "filters": {"content_type": "video'; UPDATE analytics SET view_count=999999999 WHERE '1'='1'--"},
                    "description": "Engagement manipulation"
                }
            ]
            
            for attack in analytics_attacks:
                is_safe = await self.sql_protection.validate_analytics_query(
                    attack["query_type"],
                    attack["filters"],
                    context
                )
                
                assert is_safe is False, f"Analytics attack not blocked: {attack['description']}"
            
            self.metrics_collector.record_success(
                "creator_economy_sql_security",
                time.time() - start_time
            )
            
        except Exception as e:
            self.metrics_collector.record_error("creator_economy_sql_security_failed", str(e))
            raise AssertionError(f"Creator Economy SQL security test failed: {e}")

    # ==================== PERFORMANCE & LOAD TESTING ====================
    
    async def test_sql_injection_protection_performance(self, context: SQLTestContext):
        """Test SQL injection protection performance under load"""
        start_time = time.time()
        
        try:
            # Test concurrent validation performance
            concurrent_requests = 100
            max_response_time = 0.1  # 100ms max
            
            async def validate_sql_injection():
                validation_start = time.time()
                
                # Use complex injection payload
                payload = "'; UNION SELECT username,password,api_key FROM users WHERE id=1; DROP TABLE content;--"
                
                result = await self.sql_protection.validate_query_parameters(
                    {"search": payload},
                    context
                )
                
                validation_time = time.time() - validation_start
                return result, validation_time
            
            # Run concurrent SQL injection validation tests
            tasks = [validate_sql_injection() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_validations = 0
            total_validation_time = 0
            
            for result in results:
                if isinstance(result, tuple):
                    validation_result, validation_time = result
                    if validation_result is not None:
                        successful_validations += 1
                        total_validation_time += validation_time
                        assert validation_time < max_response_time, f"SQL validation took {validation_time}s (max: {max_response_time}s)"
            
            # Performance assertions
            success_rate = successful_validations / concurrent_requests
            avg_response_time = total_validation_time / successful_validations if successful_validations > 0 else 0
            
            assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
            assert avg_response_time < max_response_time / 2, f"Average response time {avg_response_time}s too high"
            
            # Test large payload validation performance
            large_payload = "'; " + "UNION SELECT * FROM users " * 100 + "DROP TABLE content;--"
            
            large_payload_start = time.time()
            result = await self.sql_protection.validate_query_parameters(
                {"data": large_payload},
                context
            )
            large_payload_time = time.time() - large_payload_start
            
            assert large_payload_time < 0.5, f"Large payload validation too slow: {large_payload_time}s"
            assert result is False, "Large injection payload not blocked"
            
            self.metrics_collector.record_performance(
                "sql_injection_protection_performance",
                {
                    "concurrent_requests": concurrent_requests,
                    "success_rate": success_rate,
                    "avg_validation_time": avg_response_time,
                    "large_payload_time": large_payload_time,
                    "total_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            self.metrics_collector.record_error("sql_injection_protection_performance_failed", str(e))
            raise AssertionError(f"SQL injection protection performance test failed: {e}")

    # ==================== COMPREHENSIVE TEST SUITE ====================
    
    async def run_comprehensive_sql_injection_tests(self) -> Dict[str, Any]:
        """Run complete SQL injection prevention test suite"""
        print("🛡️ Starting Comprehensive SQL Injection Prevention Testing...")
        
        context = await self.setup_test_environment()
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "security_score": 0
        }
        
        test_methods = [
            # Classic SQL Injection Tests
            self.test_classic_sql_injection_prevention,
            self.test_prepared_statement_validation,
            
            # Blind SQL Injection Tests
            self.test_blind_sql_injection_prevention,
            self.test_time_based_sql_injection_prevention,
            
            # Union-based Tests
            self.test_union_based_sql_injection_prevention,
            
            # NoSQL Tests
            self.test_nosql_injection_prevention,
            
            # ORM Security Tests
            self.test_orm_security_validation,
            
            # Creator Economy Tests
            self.test_creator_economy_sql_security,
            
            # Performance Tests
            self.test_sql_injection_protection_performance,
        ]
        
        for test_method in test_methods:
            test_results["total_tests"] += 1
            test_name = test_method.__name__
            
            try:
                print(f"  Running {test_name}...")
                await test_method(context)
                test_results["passed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "error": None
                })
                print(f"  ✅ {test_name} PASSED")
                
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ {test_name} FAILED: {e}")
        
        # Calculate security score
        security_score = (test_results["passed_tests"] / test_results["total_tests"]) * 100
        test_results["security_score"] = security_score
        
        # Collect performance metrics
        test_results["performance_metrics"] = self.metrics_collector.get_metrics()
        
        await self.teardown_test_environment(context)
        
        print(f"\n🛡️ SQL Injection Prevention Testing Complete!")
        print(f"   Tests Passed: {test_results['passed_tests']}/{test_results['total_tests']}")
        print(f"   Security Score: {security_score:.1f}%")
        
        return test_results


# ==================== PYTEST INTEGRATION ====================

@pytest.fixture
async def sql_test_template():
    """Pytest fixture for SQL injection testing"""
    template = SQLInjectionTestTemplate()
    yield template
    # Cleanup handled by template

@pytest.fixture
async def sql_context(sql_test_template):
    """Pytest fixture for SQL injection context"""
    context = await sql_test_template.setup_test_environment()
    yield context
    await sql_test_template.teardown_test_environment(context)

# Individual test functions for pytest discovery
@pytest.mark.asyncio
async def test_classic_sql_injection(sql_test_template, sql_context):
    """Test classic SQL injection prevention"""
    await sql_test_template.test_classic_sql_injection_prevention(sql_context)
    await sql_test_template.test_prepared_statement_validation(sql_context)

@pytest.mark.asyncio
async def test_blind_sql_injection(sql_test_template, sql_context):
    """Test blind SQL injection prevention"""
    await sql_test_template.test_blind_sql_injection_prevention(sql_context)
    await sql_test_template.test_time_based_sql_injection_prevention(sql_context)

@pytest.mark.asyncio
async def test_union_sql_injection(sql_test_template, sql_context):
    """Test union-based SQL injection prevention"""
    await sql_test_template.test_union_based_sql_injection_prevention(sql_context)

@pytest.mark.asyncio
async def test_nosql_injection(sql_test_template, sql_context):
    """Test NoSQL injection prevention"""
    await sql_test_template.test_nosql_injection_prevention(sql_context)

@pytest.mark.asyncio
async def test_orm_security(sql_test_template, sql_context):
    """Test ORM security validation"""
    await sql_test_template.test_orm_security_validation(sql_context)

@pytest.mark.asyncio
async def test_creator_economy_sql(sql_test_template, sql_context):
    """Test Creator Economy SQL security"""
    await sql_test_template.test_creator_economy_sql_security(sql_context)

@pytest.mark.asyncio
@pytest.mark.performance
async def test_sql_injection_performance(sql_test_template, sql_context):
    """Test SQL injection protection performance"""
    await sql_test_template.test_sql_injection_protection_performance(sql_context)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_comprehensive_sql_injection_suite(sql_test_template):
    """Run comprehensive SQL injection prevention test suite"""
    results = await sql_test_template.run_comprehensive_sql_injection_tests()
    assert results["security_score"] >= 90, f"Security score {results['security_score']}% below minimum 90%"


if __name__ == "__main__":
    """
    Run SQL injection prevention tests directly
    Usage: python sql_injection_test_template.py
    """
    async def main():
        template = SQLInjectionTestTemplate()
        results = await template.run_comprehensive_sql_injection_tests()
        
        print("\n" + "="*80)
        print("🛡️ SQL INJECTION PREVENTION TEST RESULTS")
        print("="*80)
        print(f"Security Score: {results['security_score']:.1f}%")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        
        if results['failed_tests'] > 0:
            print("\n❌ Failed Tests:")
            for test in results['test_details']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['name']}: {test['error']}")
        
        return results['security_score'] >= 90
    
    # Run the tests
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1)