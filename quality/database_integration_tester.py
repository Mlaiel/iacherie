#!/usr/bin/env python3
"""
Database Integration Testing Module - Ainflue Quality Platform
============================================================

Enterprise-grade database integration testing system.
Demonstrates DBA + Backend Senior + ML Engineer expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import asyncpg
import aioredis
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseTestResult:
    """Database test execution result."""
    test_name: str
    database_type: str
    database_name: str
    operation: str
    status: str  # 'passed', 'failed', 'error'
    execution_time_ms: float
    rows_affected: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DatabaseConnection:
    """Database connection configuration."""
    name: str
    type: str  # 'postgresql', 'mongodb', 'redis', 'mysql'
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
    pool_size: int = 10
    additional_params: Dict[str, Any] = field(default_factory=dict)


class DatabasePerformanceMonitor:
    """Monitor database performance during tests."""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = process.cpu_percent()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return metrics."""
        if self.start_time is None:
            return {}
        
        end_time = time.time()
        process = psutil.Process()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        
        return {
            'execution_time_ms': (end_time - self.start_time) * 1000,
            'memory_usage_mb': end_memory - self.start_memory,
            'cpu_usage_percent': end_cpu - self.start_cpu
        }


class PostgreSQLTester:
    """PostgreSQL database integration tester."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.pool = None
    
    async def connect(self):
        """Establish database connection pool."""
        try:
            dsn = f"postgresql://{self.connection.username}:{self.connection.password}@{self.connection.host}:{self.connection.port}/{self.connection.database}"
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=1,
                max_size=self.connection.pool_size,
                ssl=self.connection.ssl
            )
            logger.info(f"Connected to PostgreSQL: {self.connection.name}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL {self.connection.name}: {e}")
            raise
    
    async def test_basic_operations(self) -> List[DatabaseTestResult]:
        """Test basic CRUD operations."""
        results = []
        
        if not self.pool:
            await self.connect()
        
        # Test table creation
        result = await self._test_table_creation()
        results.append(result)
        
        # Test data insertion
        result = await self._test_data_insertion()
        results.append(result)
        
        # Test data selection
        result = await self._test_data_selection()
        results.append(result)
        
        # Test data update
        result = await self._test_data_update()
        results.append(result)
        
        # Test data deletion
        result = await self._test_data_deletion()
        results.append(result)
        
        # Test transaction handling
        result = await self._test_transaction_handling()
        results.append(result)
        
        return results
    
    async def _test_table_creation(self) -> DatabaseTestResult:
        """Test table creation."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="table_creation",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="CREATE TABLE",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            async with self.pool.acquire() as conn:
                # Drop table if exists
                await conn.execute("DROP TABLE IF EXISTS quality_test_table")
                
                # Create test table
                await conn.execute("""
                    CREATE TABLE quality_test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(150) UNIQUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB,
                        score NUMERIC(10,2)
                    )
                """)
                
                # Create index for performance testing
                await conn.execute("CREATE INDEX idx_quality_test_email ON quality_test_table(email)")
                
                result.status = "passed"
                
        except Exception as e:
            result.errors.append(f"Table creation failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_data_insertion(self) -> DatabaseTestResult:
        """Test data insertion with performance monitoring."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="data_insertion",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="INSERT",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            test_data = [
                ("Alice Smith", "alice@example.com", {"role": "creator", "tier": "premium"}, 95.5),
                ("Bob Johnson", "bob@example.com", {"role": "viewer", "tier": "basic"}, 78.2),
                ("Carol Davis", "carol@example.com", {"role": "admin", "tier": "enterprise"}, 99.1),
            ]
            
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    rows_inserted = 0
                    for name, email, metadata, score in test_data:
                        await conn.execute(
                            "INSERT INTO quality_test_table (name, email, metadata, score) VALUES ($1, $2, $3, $4)",
                            name, email, json.dumps(metadata), score
                        )
                        rows_inserted += 1
                    
                    result.rows_affected = rows_inserted
                    result.status = "passed"
                    
        except Exception as e:
            result.errors.append(f"Data insertion failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_data_selection(self) -> DatabaseTestResult:
        """Test data selection with complex queries."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="data_selection",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="SELECT",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            async with self.pool.acquire() as conn:
                # Simple select
                rows = await conn.fetch("SELECT * FROM quality_test_table")
                
                # Complex query with JSON operations
                premium_users = await conn.fetch("""
                    SELECT name, email, score 
                    FROM quality_test_table 
                    WHERE metadata->>'tier' = 'premium'
                    AND score > 90
                    ORDER BY score DESC
                """)
                
                # Aggregation query
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_users,
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score
                    FROM quality_test_table
                """)
                
                result.rows_affected = len(rows)
                result.metrics = {
                    'total_rows': len(rows),
                    'premium_users': len(premium_users),
                    'statistics': dict(stats) if stats else {}
                }
                result.status = "passed"
                
        except Exception as e:
            result.errors.append(f"Data selection failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_data_update(self) -> DatabaseTestResult:
        """Test data update operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="data_update",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="UPDATE",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            async with self.pool.acquire() as conn:
                # Update specific record
                update_result = await conn.execute(
                    "UPDATE quality_test_table SET score = score + 5 WHERE email = $1",
                    "alice@example.com"
                )
                
                # Bulk update with JSON operations
                bulk_result = await conn.execute("""
                    UPDATE quality_test_table 
                    SET metadata = metadata || '{"last_updated": "2025-01-12"}'::jsonb
                    WHERE metadata->>'tier' IN ('premium', 'enterprise')
                """)
                
                result.rows_affected = int(update_result.split()[-1]) if update_result else 0
                result.status = "passed"
                
        except Exception as e:
            result.errors.append(f"Data update failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_data_deletion(self) -> DatabaseTestResult:
        """Test data deletion operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="data_deletion",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="DELETE",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            async with self.pool.acquire() as conn:
                # Delete specific record
                delete_result = await conn.execute(
                    "DELETE FROM quality_test_table WHERE email = $1",
                    "bob@example.com"
                )
                
                result.rows_affected = int(delete_result.split()[-1]) if delete_result else 0
                result.status = "passed"
                
        except Exception as e:
            result.errors.append(f"Data deletion failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_transaction_handling(self) -> DatabaseTestResult:
        """Test transaction handling and rollback."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="transaction_handling",
            database_type="postgresql",
            database_name=self.connection.name,
            operation="TRANSACTION",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            async with self.pool.acquire() as conn:
                # Test successful transaction
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO quality_test_table (name, email, score) VALUES ($1, $2, $3)",
                        "Test User", "test@example.com", 85.0
                    )
                
                # Test rollback transaction
                try:
                    async with conn.transaction():
                        await conn.execute(
                            "INSERT INTO quality_test_table (name, email, score) VALUES ($1, $2, $3)",
                            "Rollback User", "test@example.com", 90.0  # Duplicate email should fail
                        )
                except Exception:
                    pass  # Expected to fail due to unique constraint
                
                # Verify rollback worked
                count = await conn.fetchval("SELECT COUNT(*) FROM quality_test_table WHERE email = $1", "test@example.com")
                
                if count == 1:
                    result.status = "passed"
                    result.metrics = {"transaction_test": "successful"}
                else:
                    result.errors.append(f"Transaction rollback test failed: found {count} records")
                    result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"Transaction handling test failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def cleanup(self):
        """Cleanup test resources."""
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    await conn.execute("DROP TABLE IF EXISTS quality_test_table")
                await self.pool.close()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class RedisTester:
    """Redis database integration tester."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.redis = None
    
    async def connect(self):
        """Establish Redis connection."""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{self.connection.host}:{self.connection.port}/{self.connection.database}",
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Connected to Redis: {self.connection.name}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis {self.connection.name}: {e}")
            raise
    
    async def test_basic_operations(self) -> List[DatabaseTestResult]:
        """Test basic Redis operations."""
        results = []
        
        if not self.redis:
            await self.connect()
        
        # Test string operations
        result = await self._test_string_operations()
        results.append(result)
        
        # Test hash operations
        result = await self._test_hash_operations()
        results.append(result)
        
        # Test list operations
        result = await self._test_list_operations()
        results.append(result)
        
        # Test set operations
        result = await self._test_set_operations()
        results.append(result)
        
        # Test expiration
        result = await self._test_expiration()
        results.append(result)
        
        return results
    
    async def _test_string_operations(self) -> DatabaseTestResult:
        """Test Redis string operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="string_operations",
            database_type="redis",
            database_name=self.connection.name,
            operation="STRING",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Set/Get operations
            await self.redis.set("test:string", "Hello Redis")
            value = await self.redis.get("test:string")
            
            # Increment operations
            await self.redis.set("test:counter", 0)
            await self.redis.incr("test:counter")
            counter_value = await self.redis.get("test:counter")
            
            if value == "Hello Redis" and counter_value == "1":
                result.status = "passed"
                result.metrics = {
                    "string_value": value,
                    "counter_value": int(counter_value)
                }
            else:
                result.errors.append("String operations validation failed")
                result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"String operations failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_hash_operations(self) -> DatabaseTestResult:
        """Test Redis hash operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="hash_operations",
            database_type="redis",
            database_name=self.connection.name,
            operation="HASH",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Hash operations
            await self.redis.hset("test:user:1", mapping={
                "name": "Alice",
                "email": "alice@example.com",
                "score": "95.5"
            })
            
            user_data = await self.redis.hgetall("test:user:1")
            score = await self.redis.hget("test:user:1", "score")
            
            if user_data.get("name") == "Alice" and score == "95.5":
                result.status = "passed"
                result.metrics = {"user_data": user_data}
            else:
                result.errors.append("Hash operations validation failed")
                result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"Hash operations failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_list_operations(self) -> DatabaseTestResult:
        """Test Redis list operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="list_operations",
            database_type="redis",
            database_name=self.connection.name,
            operation="LIST",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # List operations
            await self.redis.lpush("test:queue", "task1", "task2", "task3")
            list_length = await self.redis.llen("test:queue")
            first_item = await self.redis.lpop("test:queue")
            
            if list_length == 3 and first_item == "task3":
                result.status = "passed"
                result.metrics = {
                    "initial_length": list_length,
                    "first_item": first_item
                }
            else:
                result.errors.append("List operations validation failed")
                result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"List operations failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_set_operations(self) -> DatabaseTestResult:
        """Test Redis set operations."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="set_operations",
            database_type="redis",
            database_name=self.connection.name,
            operation="SET",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Set operations
            await self.redis.sadd("test:tags", "ai", "ml", "quality", "testing")
            set_size = await self.redis.scard("test:tags")
            is_member = await self.redis.sismember("test:tags", "ai")
            members = await self.redis.smembers("test:tags")
            
            if set_size == 4 and is_member and "ai" in members:
                result.status = "passed"
                result.metrics = {
                    "set_size": set_size,
                    "members": list(members)
                }
            else:
                result.errors.append("Set operations validation failed")
                result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"Set operations failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def _test_expiration(self) -> DatabaseTestResult:
        """Test Redis key expiration."""
        monitor = DatabasePerformanceMonitor()
        monitor.start_monitoring()
        
        result = DatabaseTestResult(
            test_name="expiration_test",
            database_type="redis",
            database_name=self.connection.name,
            operation="EXPIRE",
            status="error",
            execution_time_ms=0.0
        )
        
        try:
            # Set key with expiration
            await self.redis.setex("test:expire", 2, "temporary")  # 2 seconds
            exists_before = await self.redis.exists("test:expire")
            
            # Wait for expiration
            await asyncio.sleep(2.1)
            exists_after = await self.redis.exists("test:expire")
            
            if exists_before and not exists_after:
                result.status = "passed"
                result.metrics = {
                    "exists_before": bool(exists_before),
                    "exists_after": bool(exists_after)
                }
            else:
                result.errors.append("Expiration test validation failed")
                result.status = "failed"
                
        except Exception as e:
            result.errors.append(f"Expiration test failed: {str(e)}")
            result.status = "failed"
        
        metrics = monitor.stop_monitoring()
        result.execution_time_ms = metrics.get('execution_time_ms', 0.0)
        result.memory_usage_mb = metrics.get('memory_usage_mb', 0.0)
        result.cpu_usage_percent = metrics.get('cpu_usage_percent', 0.0)
        
        return result
    
    async def cleanup(self):
        """Cleanup test resources."""
        try:
            if self.redis:
                # Clean up test keys
                await self.redis.delete("test:string", "test:counter", "test:user:1", "test:queue", "test:tags", "test:expire")
                await self.redis.close()
        except Exception as e:
            logger.error(f"Redis cleanup failed: {e}")


class DatabaseIntegrationTester:
    """
    Enterprise Database Integration Testing Engine
    =============================================
    
    Comprehensive database integration testing for multi-database architecture.
    Demonstrates DBA + Backend Senior + ML Engineer expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.connections: Dict[str, DatabaseConnection] = {}
        self.test_results: List[DatabaseTestResult] = []
        
        # Initialize testers
        self.testers = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load testing configuration."""
        default_config = {
            'databases': {
                'postgresql_test': {
                    'type': 'postgresql',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'ainflue_test',
                    'username': 'postgres',
                    'password': 'password'
                },
                'redis_test': {
                    'type': 'redis',
                    'host': 'localhost',
                    'port': 6379,
                    'database': 0
                }
            },
            'test_settings': {
                'parallel_tests': 5,
                'timeout': 30,
                'cleanup_after_tests': True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def setup_connections(self):
        """Setup database connections from configuration."""
        for name, db_config in self.config['databases'].items():
            connection = DatabaseConnection(
                name=name,
                type=db_config['type'],
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                username=db_config.get('username'),
                password=db_config.get('password'),
                ssl=db_config.get('ssl', False),
                pool_size=db_config.get('pool_size', 10)
            )
            self.connections[name] = connection
            
            # Initialize appropriate tester
            if connection.type == 'postgresql':
                self.testers[name] = PostgreSQLTester(connection)
            elif connection.type == 'redis':
                self.testers[name] = RedisTester(connection)
            else:
                logger.warning(f"Unsupported database type: {connection.type}")
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive database integration tests."""
        logger.info("Starting database integration tests")
        
        self.setup_connections()
        
        all_results = []
        
        # Test each database
        for name, tester in self.testers.items():
            logger.info(f"Testing database: {name}")
            
            try:
                # Run basic operations tests
                results = await tester.test_basic_operations()
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"Failed to test database {name}: {e}")
                # Create error result
                error_result = DatabaseTestResult(
                    test_name="connection_test",
                    database_type=self.connections[name].type,
                    database_name=name,
                    operation="CONNECT",
                    status="error",
                    execution_time_ms=0.0,
                    errors=[f"Connection failed: {str(e)}"]
                )
                all_results.append(error_result)
        
        self.test_results = all_results
        
        # Generate comprehensive report
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_databases': len(self.connections),
                'total_tests': len(self.test_results),
                'passed_tests': len([r for r in self.test_results if r.status == 'passed']),
                'failed_tests': len([r for r in self.test_results if r.status == 'failed']),
                'error_tests': len([r for r in self.test_results if r.status == 'error']),
            },
            'databases': {},
            'performance': {
                'average_execution_time': 0.0,
                'total_execution_time': 0.0,
                'fastest_operation': None,
                'slowest_operation': None
            },
            'failures': []
        }
        
        # Calculate success rate
        total_tests = report['summary']['total_tests']
        if total_tests > 0:
            report['summary']['success_rate'] = (report['summary']['passed_tests'] / total_tests) * 100
        else:
            report['summary']['success_rate'] = 0.0
        
        # Group results by database
        for result in self.test_results:
            db_name = result.database_name
            if db_name not in report['databases']:
                report['databases'][db_name] = {
                    'type': result.database_type,
                    'total_tests': 0,
                    'passed_tests': 0,
                    'failed_tests': 0,
                    'error_tests': 0,
                    'average_execution_time': 0.0,
                    'tests': []
                }
            
            db_report = report['databases'][db_name]
            db_report['total_tests'] += 1
            db_report['tests'].append({
                'test_name': result.test_name,
                'operation': result.operation,
                'status': result.status,
                'execution_time_ms': result.execution_time_ms,
                'rows_affected': result.rows_affected,
                'errors': result.errors,
                'metrics': result.metrics
            })
            
            if result.status == 'passed':
                db_report['passed_tests'] += 1
            elif result.status == 'failed':
                db_report['failed_tests'] += 1
                report['failures'].append({
                    'database': db_name,
                    'test': result.test_name,
                    'operation': result.operation,
                    'errors': result.errors
                })
            else:
                db_report['error_tests'] += 1
                report['failures'].append({
                    'database': db_name,
                    'test': result.test_name,
                    'operation': result.operation,
                    'errors': result.errors
                })
        
        # Calculate database-specific averages
        for db_name, db_report in report['databases'].items():
            db_tests = [r for r in self.test_results if r.database_name == db_name]
            if db_tests:
                db_report['average_execution_time'] = sum(t.execution_time_ms for t in db_tests) / len(db_tests)
        
        # Performance analysis
        if self.test_results:
            total_time = sum(r.execution_time_ms for r in self.test_results)
            report['performance']['total_execution_time'] = total_time
            report['performance']['average_execution_time'] = total_time / len(self.test_results)
            
            fastest = min(self.test_results, key=lambda r: r.execution_time_ms)
            slowest = max(self.test_results, key=lambda r: r.execution_time_ms)
            
            report['performance']['fastest_operation'] = {
                'database': fastest.database_name,
                'test': fastest.test_name,
                'operation': fastest.operation,
                'time_ms': fastest.execution_time_ms
            }
            
            report['performance']['slowest_operation'] = {
                'database': slowest.database_name,
                'test': slowest.test_name,
                'operation': slowest.operation,
                'time_ms': slowest.execution_time_ms
            }
        
        return report
    
    async def cleanup(self):
        """Cleanup all test resources."""
        logger.info("Cleaning up database test resources")
        
        cleanup_tasks = []
        for name, tester in self.testers.items():
            cleanup_tasks.append(tester.cleanup())
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    
    async def save_report(self, report: Dict[str, Any], output_path: str = "database_test_report.json"):
        """Save test report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Database integration test report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for database integration testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Integration Testing Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", default="database_test_report.json", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize tester
    tester = DatabaseIntegrationTester(args.config)
    
    try:
        # Run tests
        report = await tester.run_integration_tests()
        
        # Save report
        await tester.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🗄️ Database Integration Test Results")
        print(f"{'='*50}")
        print(f"Databases Tested: {summary['total_databases']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Average Execution Time: {report['performance']['average_execution_time']:.2f}ms")
        
        if summary['success_rate'] < 100:
            print(f"\n❌ {len(report['failures'])} failures detected")
            for failure in report['failures'][:5]:  # Show first 5 failures
                print(f"  - {failure['database']}: {failure['test']} ({failure['operation']})")
        else:
            print(f"\n✅ All tests passed!")
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())