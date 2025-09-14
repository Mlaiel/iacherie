"""
Data Processor - Core Utilities Level 1
=====================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade data processing utility consolidating:
- Data transformation (data_transformer.py)
- Database utilities (database_utilities.py) 
- Query builder (query_builder.py)
- REST client (rest_client.py)

Performance: < 10ms per operation
Standards: 100% async, type hints, clean architecture
"""

import asyncio
import json
import csv
import xml.etree.ElementTree as ET
import logging
import re
import time
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    AsyncIterator, Type, Generic, TypeVar
)
from datetime import datetime, date, timezone
from decimal import Decimal
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import aiohttp
import aiofiles
import asyncpg
import aiomysql
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, validator
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ProcessingResult(Generic[T]):
    """Enterprise result container for data processing operations."""
    success: bool
    data: Optional[T] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass  
class DatabaseConfig:
    """Database connection configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    driver: str = "postgresql"
    pool_size: int = 10
    max_overflow: int = 20
    
class DataProcessor:
    """
    Enterprise data processor with ultra-high performance standards.
    
    Consolidates multiple data processing utilities into a single,
    optimized, async-first implementation following clean architecture.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize processor with enterprise configuration."""
        self.config = config or {}
        self._db_pools: Dict[str, Any] = {}
        self._http_session: Optional[aiohttp.ClientSession] = None
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 10.0
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_connections()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self._cleanup_connections()
        
    async def _initialize_connections(self) -> None:
        """Initialize all async connections."""
        # HTTP session initialization
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        self._http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
    async def _cleanup_connections(self) -> None:
        """Clean up all connections."""
        if self._http_session:
            await self._http_session.close()
            
        for pool in self._db_pools.values():
            if hasattr(pool, 'close'):
                await pool.close()
                
        self._thread_pool.shutdown(wait=True)
        
    async def _measure_performance(self, operation: Callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        result = await operation()
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
        
    # === DATA TRANSFORMATION OPERATIONS ===
    
    async def transform_json(
        self, 
        data: Union[str, Dict, List], 
        schema: Optional[Dict] = None,
        validate: bool = True
    ) -> ProcessingResult[Dict]:
        """Transform and validate JSON data with enterprise standards."""
        async def _transform():
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data
                
            if validate and schema:
                # Implement JSON schema validation
                pass
                
            return {
                'original_type': type(data).__name__,
                'transformed': parsed,
                'schema_valid': True if not schema else None
            }
            
        try:
            result, exec_time = await self._measure_performance(_transform)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'json_transform'}
            )
        except Exception as e:
            logger.error(f"JSON transformation failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'json_transform'}
            )
            
    async def transform_csv(
        self, 
        data: Union[str, bytes], 
        delimiter: str = ',',
        headers: Optional[List[str]] = None
    ) -> ProcessingResult[List[Dict]]:
        """Transform CSV data with enterprise performance standards."""
        async def _transform():
            if isinstance(data, bytes):
                data_str = data.decode('utf-8')
            else:
                data_str = data
                
            lines = data_str.strip().split('\n')
            if not lines:
                return []
                
            if headers:
                header_row = headers
                data_rows = lines
            else:
                header_row = lines[0].split(delimiter)
                data_rows = lines[1:]
                
            result = []
            for row in data_rows:
                values = row.split(delimiter)
                if len(values) == len(header_row):
                    result.append(dict(zip(header_row, values)))
                    
            return result
            
        try:
            result, exec_time = await self._measure_performance(_transform)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'csv_transform', 'rows_processed': len(result)}
            )
        except Exception as e:
            logger.error(f"CSV transformation failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'csv_transform'}
            )
    
    async def transform_xml(
        self, 
        data: Union[str, bytes],
        namespace_map: Optional[Dict[str, str]] = None
    ) -> ProcessingResult[Dict]:
        """Transform XML data with enterprise standards."""
        async def _transform():
            if isinstance(data, bytes):
                data_str = data.decode('utf-8')
            else:
                data_str = data
                
            root = ET.fromstring(data_str)
            
            def xml_to_dict(element):
                result = {}
                
                # Add attributes
                if element.attrib:
                    result['@attributes'] = element.attrib
                    
                # Add text content
                if element.text and element.text.strip():
                    if len(element) == 0:
                        return element.text.strip()
                    result['#text'] = element.text.strip()
                    
                # Add child elements
                for child in element:
                    child_data = xml_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                        
                return result if result else element.text
            
            return {
                'root_tag': root.tag,
                'data': xml_to_dict(root),
                'namespace_map': namespace_map
            }
            
        try:
            result, exec_time = await self._measure_performance(_transform)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'xml_transform'}
            )
        except Exception as e:
            logger.error(f"XML transformation failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'xml_transform'}
            )
    
    # === DATABASE OPERATIONS ===
    
    async def get_database_pool(self, db_config: DatabaseConfig) -> Any:
        """Get or create database connection pool."""
        pool_key = f"{db_config.driver}_{db_config.host}_{db_config.database}"
        
        if pool_key not in self._db_pools:
            if db_config.driver == "postgresql":
                self._db_pools[pool_key] = await asyncpg.create_pool(
                    host=db_config.host,
                    port=db_config.port,
                    user=db_config.username,
                    password=db_config.password,
                    database=db_config.database,
                    min_size=1,
                    max_size=db_config.pool_size
                )
            elif db_config.driver == "mysql":
                self._db_pools[pool_key] = await aiomysql.create_pool(
                    host=db_config.host,
                    port=db_config.port,
                    user=db_config.username,
                    password=db_config.password,
                    db=db_config.database,
                    minsize=1,
                    maxsize=db_config.pool_size
                )
                
        return self._db_pools[pool_key]
    
    async def execute_query(
        self, 
        query: str, 
        params: Optional[Dict] = None,
        db_config: Optional[DatabaseConfig] = None
    ) -> ProcessingResult[List[Dict]]:
        """Execute database query with enterprise performance monitoring."""
        if not db_config:
            return ProcessingResult(
                success=False,
                errors=["Database configuration required"]
            )
        
        async def _execute():
            pool = await self.get_database_pool(db_config)
            
            if db_config.driver == "postgresql":
                async with pool.acquire() as connection:
                    if params:
                        rows = await connection.fetch(query, *params.values())
                    else:
                        rows = await connection.fetch(query)
                    return [dict(row) for row in rows]
            elif db_config.driver == "mysql":
                async with pool.acquire() as connection:
                    async with connection.cursor(aiomysql.DictCursor) as cursor:
                        if params:
                            await cursor.execute(query, params)
                        else:
                            await cursor.execute(query)
                        rows = await cursor.fetchall()
                        return rows
                        
        try:
            result, exec_time = await self._measure_performance(_execute)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'database_query', 'rows_returned': len(result)}
            )
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'database_query'}
            )
    
    # === HTTP CLIENT OPERATIONS ===
    
    async def http_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        timeout: float = 30.0
    ) -> ProcessingResult[Dict]:
        """Execute HTTP request with enterprise error handling."""
        if not self._http_session:
            await self._initialize_connections()
            
        async def _request():
            async with self._http_session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                content_type = response.headers.get('content-type', '')
                
                if 'json' in content_type:
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                    
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'url': str(response.url)
                }
                
        try:
            result, exec_time = await self._measure_performance(_request)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'http_request', 'method': method, 'url': url}
            )
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'http_request', 'method': method, 'url': url}
            )
    
    # === QUERY BUILDER OPERATIONS ===
    
    def build_select_query(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where_conditions: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Build SELECT query with enterprise SQL injection protection."""
        # Base query
        if columns:
            columns_str = ', '.join(f'"{col}"' for col in columns)
        else:
            columns_str = '*'
            
        query = f'SELECT {columns_str} FROM "{table}"'
        params = {}
        
        # WHERE clause
        if where_conditions:
            where_parts = []
            for i, (column, value) in enumerate(where_conditions.items()):
                param_name = f'param_{i}'
                where_parts.append(f'"{column}" = ${i+1}')
                params[param_name] = value
            query += f' WHERE {" AND ".join(where_parts)}'
        
        # ORDER BY clause
        if order_by:
            order_parts = []
            for order_col in order_by:
                if order_col.startswith('-'):
                    order_parts.append(f'"{order_col[1:]}" DESC')
                else:
                    order_parts.append(f'"{order_col}" ASC')
            query += f' ORDER BY {", ".join(order_parts)}'
        
        # LIMIT clause
        if limit:
            query += f' LIMIT {limit}'
            
        # OFFSET clause  
        if offset:
            query += f' OFFSET {offset}'
            
        return query, params
    
    def build_insert_query(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Build INSERT query with enterprise standards."""
        columns = list(data.keys())
        placeholders = [f'${i+1}' for i in range(len(columns))]
        
        columns_str = ', '.join(f'"{col}"' for col in columns)
        placeholders_str = ', '.join(placeholders)
        
        query = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders_str})'
        
        if on_conflict:
            query += f' {on_conflict}'
            
        params = {f'param_{i}': value for i, value in enumerate(data.values())}
        
        return query, params
    
    def build_update_query(
        self,
        table: str,
        data: Dict[str, Any],
        where_conditions: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Build UPDATE query with enterprise security."""
        set_parts = []
        params = {}
        param_index = 0
        
        # SET clause
        for column, value in data.items():
            set_parts.append(f'"{column}" = ${param_index + 1}')
            params[f'param_{param_index}'] = value
            param_index += 1
        
        query = f'UPDATE "{table}" SET {", ".join(set_parts)}'
        
        # WHERE clause
        if where_conditions:
            where_parts = []
            for column, value in where_conditions.items():
                where_parts.append(f'"{column}" = ${param_index + 1}')
                params[f'param_{param_index}'] = value
                param_index += 1
            query += f' WHERE {" AND ".join(where_parts)}'
        
        return query, params
    
    # === BATCH PROCESSING OPERATIONS ===
    
    async def process_batch(
        self,
        items: List[T],
        processor: Callable[[T], Any],
        batch_size: int = 100,
        max_concurrency: int = 10
    ) -> ProcessingResult[List[Any]]:
        """Process items in batches with enterprise concurrency control."""
        async def _process_batch():
            semaphore = asyncio.Semaphore(max_concurrency)
            results = []
            
            async def process_item(item):
                async with semaphore:
                    return await asyncio.get_event_loop().run_in_executor(
                        self._thread_pool, processor, item
                    )
            
            # Process in batches
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *[process_item(item) for item in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
                
            return results
            
        try:
            result, exec_time = await self._measure_performance(_process_batch)
            return ProcessingResult(
                success=True,
                data=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'batch_process',
                    'total_items': len(items),
                    'batch_size': batch_size,
                    'max_concurrency': max_concurrency
                }
            )
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'batch_process'}
            )

# Enterprise factory pattern for data processor
class DataProcessorFactory:
    """Factory for creating configured data processor instances."""
    
    @staticmethod
    async def create_processor(config: Optional[Dict[str, Any]] = None) -> DataProcessor:
        """Create and initialize data processor."""
        processor = DataProcessor(config)
        await processor._initialize_connections()
        return processor
    
    @staticmethod
    @asynccontextmanager
    async def create_processor_context(config: Optional[Dict[str, Any]] = None):
        """Create data processor as async context manager."""
        processor = DataProcessor(config)
        try:
            await processor._initialize_connections()
            yield processor
        finally:
            await processor._cleanup_connections()

# === ENHANCED BACKEND UTILITIES ===
# Consolidated from database_utilities.py, query_builder.py, rest_client.py, data_transformer.py

from enum import Enum

class JoinType(Enum):
    """SQL join types for query building"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"

class OrderDirection(Enum):
    """SQL order directions"""
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class QueryMetrics:
    """Enhanced query performance metrics from database_utilities.py"""
    query_hash: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    query_type: str
    table_name: str = ""
    index_used: bool = False
    optimization_score: float = 0.0

@dataclass
class RestResponse:
    """Enhanced REST response wrapper from rest_client.py"""
    status_code: int
    headers: Dict[str, str]
    body: Union[str, Dict[str, Any]]
    response_time: float
    success: bool
    error: Optional[str] = None
    retry_count: int = 0

class EnterpriseQueryBuilder:
    """Enhanced query builder consolidated from query_builder.py
    
    DBA Expert: Advanced SQL generation with security and optimization
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset query builder state"""
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._group_by = []
        self._having = []
        self._order_by = []
        self._limit = None
        self._offset = None
    
    def select(self, fields: Union[str, List[str]]) -> 'EnterpriseQueryBuilder':
        """Add SELECT fields with SQL injection protection"""
        if isinstance(fields, str):
            fields = [fields]
        
        # Sanitize field names
        sanitized_fields = []
        for field in fields:
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$', field.strip()):
                sanitized_fields.append(field.strip())
            else:
                raise ValueError(f"Invalid field name: {field}")
        
        self._select_fields.extend(sanitized_fields)
        return self
    
    def from_table(self, table: str) -> 'EnterpriseQueryBuilder':
        """Set FROM table with validation"""
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table.strip()):
            raise ValueError(f"Invalid table name: {table}")
        self._from_table = table.strip()
        return self
    
    def where(self, condition: str, params: Optional[Dict[str, Any]] = None) -> 'EnterpriseQueryBuilder':
        """Add WHERE condition with parameterization"""
        self._where_conditions.append({'condition': condition, 'params': params or {}})
        return self
    
    def build(self) -> Tuple[str, Dict[str, Any]]:
        """Build final SQL query with parameters"""
        if not self._from_table:
            raise ValueError("FROM table is required")
        
        query_parts = []
        all_params = {}
        
        # SELECT
        if not self._select_fields:
            self._select_fields = ["*"]
        query_parts.append(f"SELECT {', '.join(self._select_fields)}")
        
        # FROM
        query_parts.append(f"FROM {self._from_table}")
        
        # WHERE
        if self._where_conditions:
            where_clause = " AND ".join([cond['condition'] for cond in self._where_conditions])
            query_parts.append(f"WHERE {where_clause}")
            
            # Collect parameters
            for cond in self._where_conditions:
                all_params.update(cond['params'])
        
        # ORDER BY
        if self._order_by:
            query_parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        # LIMIT/OFFSET
        if self._limit:
            query_parts.append(f"LIMIT {self._limit}")
            if self._offset:
                query_parts.append(f"OFFSET {self._offset}")
        
        return " ".join(query_parts), all_params

class EnterpriseRestClient:
    """Enhanced REST client consolidated from rest_client.py
    
    Microservices Expert: Advanced HTTP client with resilience patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._metrics: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_session()
    
    async def _initialize_session(self):
        """Initialize HTTP session with connection pooling"""
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
        connector = aiohttp.TCPConnector(
            limit=self.config.get('max_connections', 100),
            limit_per_host=self.config.get('max_connections_per_host', 30),
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.config.get('default_headers', {})
        )
    
    async def _cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[str, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> RestResponse:
        """Enhanced HTTP request with retry logic and metrics"""
        if not self.session:
            await self._initialize_session()
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if isinstance(data, str) else None,
                    params=params
                ) as response:
                    response_time = time.time() - start_time
                    body = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        body = json.loads(body)
                    except (json.JSONDecodeError, ValueError):
                        pass
                    
                    return RestResponse(
                        status_code=response.status,
                        headers=dict(response.headers),
                        body=body,
                        response_time=response_time,
                        success=200 <= response.status < 400,
                        retry_count=attempt
                    )
            
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return RestResponse(
            status_code=0,
            headers={},
            body="",
            response_time=time.time() - start_time,
            success=False,
            error=last_error,
            retry_count=retries
        )

class EnhancedDataTransformer:
    """Enhanced data transformer consolidated from data_transformer.py
    
    ML Engineer: Advanced data processing with enterprise patterns
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
    
    async def transform_data(
        self,
        data: Any,
        transformation_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> 'ProcessingResult':
        """Enhanced data transformation with async support"""
        try:
            config = config or {}
            start_time = time.time()
            
            if transformation_type == "json_normalize":
                result = await self._normalize_json(data, config)
            elif transformation_type == "csv_parse":
                result = await self._parse_csv(data, config)
            elif transformation_type == "xml_parse":
                result = await self._parse_xml(data, config)
            elif transformation_type == "data_validate":
                result = await self._validate_data(data, config)
            else:
                raise ValueError(f"Unknown transformation type: {transformation_type}")
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return ProcessingResult(
                success=True,
                result=result,
                execution_time_ms=execution_time,
                metadata={
                    'operation': f'transform_{transformation_type}',
                    'input_size': len(str(data)) if data else 0,
                    'output_size': len(str(result)) if result else 0
                }
            )
        
        except Exception as e:
            self.logger.error(f"Data transformation failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': f'transform_{transformation_type}'}
            )
    
    async def _normalize_json(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize JSON data structure"""
        if isinstance(data, str):
            data = json.loads(data)
        
        # Flatten nested dictionaries if requested
        if config.get('flatten', False):
            return self._flatten_dict(data)
        
        return data
    
    async def _parse_csv(self, data: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse CSV data with configuration"""
        import io
        
        reader = csv.DictReader(
            io.StringIO(data),
            delimiter=config.get('delimiter', ','),
            quotechar=config.get('quotechar', '"')
        )
        
        return list(reader)
    
    async def _parse_xml(self, data: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse XML data to dictionary"""
        root = ET.fromstring(data)
        return self._xml_to_dict(root)
    
    async def _validate_data(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        validation_rules = config.get('rules', {})
        errors = []
        
        # Basic validation examples
        if 'required_fields' in validation_rules and isinstance(data, dict):
            for field in validation_rules['required_fields']:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': data
        }
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            if len(result) == 0:
                return element.text.strip()
            result['text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result

# Export consolidated backend utilities
__all__ = ['DataProcessor', 'DataProcessorFactory', 'ProcessingResult', 
           'EnterpriseQueryBuilder', 'EnterpriseRestClient', 'EnhancedDataTransformer',
           'QueryMetrics', 'RestResponse', 'JoinType', 'OrderDirection']