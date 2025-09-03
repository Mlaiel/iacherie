# 🐛 Ainflue Platform - Debugging Guide

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 2.0.0  
**Last Updated:** January 2025  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.

---

## 📚 Table of Contents

1. [**🔧 Development Environment Debugging**](#-development-environment-debugging)
2. [**🌐 API & Web Service Debugging**](#-api--web-service-debugging)
3. [**🗄️ Database Debugging**](#️-database-debugging)
4. [**🤖 AI/ML Model Debugging**](#-aiml-model-debugging)
5. [**⚡ Performance Debugging**](#-performance-debugging)
6. [**🔒 Security Issue Debugging**](#-security-issue-debugging)
7. [**📱 Production Debugging**](#-production-debugging)
8. [**🛠️ Debugging Tools & Techniques**](#️-debugging-tools--techniques)

---

## 🔧 Development Environment Debugging

### Python Application Debugging

#### 1. Using Built-in Debugger (pdb)
```python
import pdb

def process_audio_content(content_id: str):
    """Process audio content with debugging."""
    # Set breakpoint
    pdb.set_trace()
    
    # Your code here
    content = get_content(content_id)
    
    # Conditional breakpoint
    if content.status == "error":
        pdb.set_trace()
    
    # Process content
    result = analyze_content(content)
    
    # Another breakpoint for result inspection
    pdb.set_trace()
    
    return result

# pdb commands:
# n (next line)
# s (step into)
# c (continue)
# l (list current code)
# p variable_name (print variable)
# pp variable_name (pretty print)
# u (up stack frame)
# d (down stack frame)
# q (quit debugger)
```

#### 2. Enhanced Debugging with ipdb
```python
import ipdb

def complex_data_processing(data):
    """Process data with enhanced debugging."""
    try:
        # Enhanced breakpoint with context
        ipdb.set_trace()
        
        processed_data = []
        for item in data:
            # Post-mortem debugging on exception
            try:
                result = process_item(item)
                processed_data.append(result)
            except Exception:
                ipdb.post_mortem()
                raise
        
        return processed_data
        
    except Exception as e:
        # Drop into debugger on any exception
        ipdb.set_trace()
        raise

# ipdb additional features:
# tab completion
# syntax highlighting
# better formatting
# ?object (get help on object)
# ??object (get source code)
```

#### 3. VS Code Debugging Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug FastAPI App",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "api.asgi:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "stopOnEntry": false,
            "justMyCode": false,
            "pythonPath": "${workspaceFolder}/venv/bin/python"
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/",
                "-v",
                "--tb=short",
                "--capture=no"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Debug AI Processing",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/ai_engine/debug_runner.py",
            "args": ["--content-id", "test-content-123"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "DEBUG": "true"
            }
        },
        {
            "name": "Attach to Remote Process",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "justMyCode": false
        }
    ]
}
```

#### 4. Remote Debugging Setup
```python
# For remote debugging in containers or remote servers
import debugpy

def setup_remote_debugging(host="0.0.0.0", port=5678):
    """Setup remote debugging server."""
    debugpy.listen((host, port))
    print(f"Debugger listening on {host}:{port}")
    print("Attach VS Code debugger to continue...")
    debugpy.wait_for_client()  # Pause until debugger attaches

# Add to your application startup
if os.getenv("DEBUG_REMOTE"):
    setup_remote_debugging()
```

### Environment & Configuration Debugging

#### 1. Environment Variables Debugging
```python
import os
from dotenv import load_dotenv

def debug_environment():
    """Debug environment configuration issues."""
    load_dotenv()
    
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY',
        'OPENAI_API_KEY',
        'YOUTUBE_API_KEY'
    ]
    
    print("🔍 Environment Variables Debug Report")
    print("=" * 50)
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if any(sensitive in var.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Check .env file existence
    env_files = ['.env', '.env.local', '.env.development']
    print("\n📁 Environment Files:")
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ {env_file}: EXISTS")
        else:
            print(f"❌ {env_file}: NOT FOUND")
    
    # Check Python path
    print(f"\n🐍 Python Path: {os.sys.executable}")
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🔗 PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")

# Run debug function
if __name__ == "__main__":
    debug_environment()
```

#### 2. Configuration Validation
```python
from pydantic import BaseSettings, validator
from typing import Optional

class DebugSettings(BaseSettings):
    """Debug-enabled settings with validation."""
    
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters')
        return v
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('Invalid PostgreSQL URL format')
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

def validate_configuration():
    """Validate application configuration."""
    try:
        settings = DebugSettings()
        print("✅ Configuration validation passed")
        return settings
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return None
```

#### 3. Dependency Debugging
```python
import importlib
import sys
import pkg_resources

def debug_dependencies():
    """Debug dependency issues."""
    print("📦 Dependency Debug Report")
    print("=" * 40)
    
    critical_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'alembic',
        'redis',
        'openai',
        'torch',
        'librosa',
        'numpy',
        'pandas'
    ]
    
    for package in critical_packages:
        try:
            # Try to import the package
            module = importlib.import_module(package)
            
            # Get version if available
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"✅ {package}: {version}")
            except:
                print(f"✅ {package}: imported (version unknown)")
                
        except ImportError as e:
            print(f"❌ {package}: NOT INSTALLED - {e}")
    
    print(f"\n🐍 Python Version: {sys.version}")
    print(f"📂 Python Executable: {sys.executable}")
    print(f"📝 Installed Packages: {len(list(pkg_resources.working_set))}")

if __name__ == "__main__":
    debug_dependencies()
```

---

## 🌐 API & Web Service Debugging

### FastAPI Application Debugging

#### 1. Request/Response Debugging Middleware
```python
import time
import json
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class DebugMiddleware(BaseHTTPMiddleware):
    """Comprehensive debugging middleware for FastAPI."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Capture request details
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"[{request_id}] 📥 {request.method} {request.url}")
        logger.info(f"[{request_id}] 📋 Headers: {dict(request.headers)}")
        
        # Capture request body (be careful with large files)
        if request.headers.get("content-type", "").startswith("application/json"):
            body = await request.body()
            if body and len(body) < 10000:  # Only log small bodies
                try:
                    body_json = json.loads(body.decode())
                    logger.info(f"[{request_id}] 📄 Body: {body_json}")
                except:
                    logger.info(f"[{request_id}] 📄 Body: <binary or invalid JSON>")
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"[{request_id}] 📤 Response: {response.status_code} ({process_time:.3f}s)")
            
            # Add debug headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[{request_id}] ❌ Error: {str(e)} ({process_time:.3f}s)")
            raise

# Add to FastAPI app
from fastapi import FastAPI
app = FastAPI()
app.add_middleware(DebugMiddleware)
```

#### 2. API Endpoint Debugging
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/debug/content/analyze")
async def debug_content_analysis(
    content_id: str,
    debug_level: int = 1,
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint for content analysis with detailed logging."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        logger.info(f"[{request_id}] 🔍 Starting content analysis debug")
        logger.info(f"[{request_id}] 📊 Content ID: {content_id}")
        logger.info(f"[{request_id}] 👤 User: {current_user.id}")
        logger.info(f"[{request_id}] ⚙️ Debug Level: {debug_level}")
        
        # Step 1: Get content
        logger.info(f"[{request_id}] 📁 Fetching content...")
        content = await get_content_by_id(content_id)
        if not content:
            logger.warning(f"[{request_id}] ❌ Content not found")
            raise HTTPException(status_code=404, detail="Content not found")
        
        logger.info(f"[{request_id}] ✅ Content found: {content.title}")
        
        # Step 2: Validate permissions
        logger.info(f"[{request_id}] 🔐 Checking permissions...")
        if content.user_id != current_user.id:
            logger.warning(f"[{request_id}] ❌ Permission denied")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Step 3: Initialize AI processor
        logger.info(f"[{request_id}] 🤖 Initializing AI processor...")
        processor = AudioProcessor(debug=debug_level > 0)
        
        # Step 4: Process content
        logger.info(f"[{request_id}] ⚡ Processing content...")
        result = await processor.analyze_with_debug(
            content.file_path,
            debug_level=debug_level
        )
        
        logger.info(f"[{request_id}] ✅ Analysis completed successfully")
        
        return {
            "status": "success",
            "request_id": request_id,
            "content_id": content_id,
            "result": result,
            "debug_info": {
                "processing_time": result.get("processing_time"),
                "model_version": result.get("model_version"),
                "confidence_scores": result.get("confidence_scores")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] ❌ Unexpected error in content analysis")
        
        if debug_level > 0:
            # Return detailed error in debug mode
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "request_id": request_id,
                    "error": str(e),
                    "traceback": traceback.format_exc() if debug_level > 1 else None
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
```

#### 3. External API Debugging
```python
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DebugHTTPClient:
    """HTTP client with comprehensive debugging capabilities."""
    
    def __init__(self, timeout: float = 30.0, debug: bool = True):
        self.timeout = timeout
        self.debug = debug
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def debug_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with detailed debugging."""
        request_id = str(uuid.uuid4())[:8]
        
        if self.debug:
            logger.info(f"[{request_id}] 🌐 {method.upper()} {url}")
            
            # Log headers (mask sensitive ones)
            headers = kwargs.get('headers', {})
            safe_headers = {}
            for key, value in headers.items():
                if any(sensitive in key.lower() for sensitive in ['auth', 'key', 'token']):
                    safe_headers[key] = f"{value[:4]}***{value[-4:]}" if len(value) > 8 else "***"
                else:
                    safe_headers[key] = value
            
            if safe_headers:
                logger.info(f"[{request_id}] 📋 Headers: {safe_headers}")
            
            # Log request body (if small)
            if 'json' in kwargs and kwargs['json']:
                logger.info(f"[{request_id}] 📄 JSON Body: {kwargs['json']}")
        
        start_time = time.time()
        
        try:
            response = await self.client.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            if self.debug:
                logger.info(f"[{request_id}] ✅ Response: {response.status_code} ({duration:.3f}s)")
                logger.info(f"[{request_id}] 📏 Response Size: {len(response.content)} bytes")
            
            # Log response body (if JSON and small)
            if self.debug and response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_json = response.json()
                    if len(str(response_json)) < 1000:
                        logger.info(f"[{request_id}] 📄 Response: {response_json}")
                except:
                    pass
            
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "duration": duration,
                "request_id": request_id
            }
            
        except httpx.RequestError as e:
            duration = time.time() - start_time
            logger.error(f"[{request_id}] ❌ Request Error: {str(e)} ({duration:.3f}s)")
            return {
                "success": False,
                "error": "request_error",
                "message": str(e),
                "duration": duration,
                "request_id": request_id
            }
            
        except httpx.HTTPStatusError as e:
            duration = time.time() - start_time
            logger.error(f"[{request_id}] ❌ HTTP Error: {e.response.status_code} ({duration:.3f}s)")
            
            # Try to get error details from response
            error_detail = None
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            
            return {
                "success": False,
                "error": "http_error",
                "status_code": e.response.status_code,
                "message": str(e),
                "detail": error_detail,
                "duration": duration,
                "request_id": request_id
            }

# Usage example
async def debug_youtube_api_call():
    """Debug YouTube API integration."""
    client = DebugHTTPClient(debug=True)
    
    result = await client.debug_request(
        "GET",
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "q": "test query",
            "key": "your-api-key"
        }
    )
    
    if result["success"]:
        print("✅ API call successful")
        return result["data"]
    else:
        print(f"❌ API call failed: {result['message']}")
        return None
```

---

## 🗄️ Database Debugging

### SQLAlchemy & PostgreSQL Debugging

#### 1. Query Debugging and Logging
```python
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine

# Enable SQLAlchemy query logging
def setup_database_debugging():
    """Setup comprehensive database debugging."""
    
    # Configure logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
    
    # For async engines
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Log all SQL statements
        echo_pool=True,  # Log connection pool events
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections every hour
    )
    
    return engine

# Query performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query start time."""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time."""
    total = time.time() - context._query_start_time
    
    # Log slow queries
    if total > 0.1:  # Queries taking more than 100ms
        logger.warning(f"🐌 Slow query ({total:.3f}s): {statement[:100]}...")
    
    logger.info(f"⚡ Query executed in {total:.3f}s")
```

#### 2. Database Connection Debugging
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
import asyncio

async def debug_database_connection():
    """Comprehensive database connection debugging."""
    print("🗄️ Database Connection Debug Report")
    print("=" * 50)
    
    try:
        async with get_async_session() as db:
            # Test basic connectivity
            print("1. Testing basic connectivity...")
            result = await db.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"   ✅ Basic query successful: {test_value}")
            
            # Check PostgreSQL version
            print("2. Checking PostgreSQL version...")
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✅ PostgreSQL version: {version}")
            
            # Check current database and user
            print("3. Checking database info...")
            result = await db.execute(text("SELECT current_database(), current_user"))
            db_info = result.first()
            print(f"   ✅ Database: {db_info[0]}, User: {db_info[1]}")
            
            # Check table existence
            print("4. Checking table existence...")
            tables = ['users', 'contents', 'content_analyses', 'protection_violations']
            for table in tables:
                result = await db.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
                ), {"table_name": table})
                exists = result.scalar()
                status = "✅" if exists else "❌"
                print(f"   {status} Table '{table}': {'EXISTS' if exists else 'NOT FOUND'}")
            
            # Check connection pool status
            print("5. Connection pool status...")
            pool = db.bind.pool
            print(f"   📊 Pool size: {pool.size()}")
            print(f"   📈 Checked out: {pool.checkedout()}")
            print(f"   📉 Overflow: {pool.overflow()}")
            
            # Test transaction
            print("6. Testing transaction...")
            async with db.begin():
                await db.execute(text("SELECT 1"))
                print("   ✅ Transaction test successful")
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_database_connection())
```

#### 3. Query Performance Analysis
```python
from sqlalchemy import text
from typing import List, Dict, Any
import time

class QueryDebugger:
    """Utility class for debugging database queries."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_query_performance(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Analyze query performance with EXPLAIN ANALYZE."""
        
        print(f"🔍 Analyzing query performance...")
        print(f"📝 Query: {query}")
        if params:
            print(f"📋 Parameters: {params}")
        
        # Execute EXPLAIN ANALYZE
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
        
        start_time = time.time()
        result = await self.session.execute(text(explain_query), params or {})
        execution_time = time.time() - start_time
        
        explain_result = result.scalar()
        
        # Extract key metrics
        plan = explain_result[0]['Plan']
        
        analysis = {
            "execution_time_ms": plan.get('Actual Total Time', 0),
            "planning_time_ms": explain_result[0].get('Planning Time', 0),
            "rows_returned": plan.get('Actual Rows', 0),
            "rows_estimated": plan.get('Plan Rows', 0),
            "node_type": plan.get('Node Type'),
            "total_cost": plan.get('Total Cost', 0),
            "buffers_hit": plan.get('Shared Hit Blocks', 0),
            "buffers_read": plan.get('Shared Read Blocks', 0),
            "buffers_written": plan.get('Shared Written Blocks', 0),
            "full_explain": explain_result
        }
        
        # Performance warnings
        warnings = []
        
        if analysis["execution_time_ms"] > 100:
            warnings.append(f"⚠️ Slow execution time: {analysis['execution_time_ms']:.2f}ms")
        
        if analysis["rows_returned"] != analysis["rows_estimated"]:
            ratio = analysis["rows_returned"] / max(analysis["rows_estimated"], 1)
            if ratio > 2 or ratio < 0.5:
                warnings.append(f"⚠️ Poor row estimation: estimated {analysis['rows_estimated']}, actual {analysis['rows_returned']}")
        
        if analysis["buffers_read"] > analysis["buffers_hit"]:
            warnings.append(f"⚠️ High disk reads: {analysis['buffers_read']} reads vs {analysis['buffers_hit']} hits")
        
        if "Seq Scan" in str(explain_result):
            warnings.append("⚠️ Sequential scan detected - consider adding indexes")
        
        analysis["warnings"] = warnings
        
        # Print analysis
        print("\n📊 Performance Analysis:")
        print(f"   ⏱️ Execution time: {analysis['execution_time_ms']:.2f}ms")
        print(f"   📏 Rows returned: {analysis['rows_returned']}")
        print(f"   💰 Total cost: {analysis['total_cost']:.2f}")
        print(f"   💾 Buffer hits: {analysis['buffers_hit']}")
        
        if warnings:
            print("\n⚠️ Performance Warnings:")
            for warning in warnings:
                print(f"   {warning}")
        
        return analysis
    
    async def debug_slow_queries(self, min_duration_ms: float = 100):
        """Find and analyze slow queries from pg_stat_statements."""
        
        # Check if pg_stat_statements is available
        check_extension = """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
        )
        """
        
        result = await self.session.execute(text(check_extension))
        has_extension = result.scalar()
        
        if not has_extension:
            print("❌ pg_stat_statements extension not available")
            return []
        
        # Get slow queries
        slow_queries_sql = """
        SELECT 
            query,
            calls,
            total_exec_time,
            mean_exec_time,
            rows,
            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
        FROM pg_stat_statements 
        WHERE mean_exec_time > :min_duration
        ORDER BY mean_exec_time DESC 
        LIMIT 10
        """
        
        result = await self.session.execute(
            text(slow_queries_sql), 
            {"min_duration": min_duration_ms}
        )
        
        slow_queries = result.fetchall()
        
        print(f"\n🐌 Slow Queries (>{min_duration_ms}ms average):")
        print("=" * 80)
        
        for i, query in enumerate(slow_queries, 1):
            print(f"{i}. Average time: {query.mean_exec_time:.2f}ms")
            print(f"   Calls: {query.calls}")
            print(f"   Total time: {query.total_exec_time:.2f}ms")
            print(f"   Cache hit ratio: {query.hit_percent:.1f}%")
            print(f"   Query: {query.query[:100]}...")
            print()
        
        return slow_queries
```

#### 4. Database Migration Debugging
```python
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
import logging

def debug_database_migrations():
    """Debug database migration issues."""
    print("🔄 Database Migration Debug Report")
    print("=" * 50)
    
    try:
        # Load Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Get script directory
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get current revision
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            print(f"1. Current database revision: {current_rev}")
            
            # Get head revision
            head_rev = script.get_current_head()
            print(f"2. Latest migration revision: {head_rev}")
            
            # Check if migrations are needed
            if current_rev != head_rev:
                print("⚠️ Database is not up to date!")
                
                # Get pending migrations
                revisions = list(script.walk_revisions(current_rev, head_rev))
                print(f"📋 Pending migrations: {len(revisions)}")
                
                for rev in revisions:
                    print(f"   - {rev.revision}: {rev.doc}")
            else:
                print("✅ Database is up to date")
            
            # Check migration history
            print("\n3. Recent migration history:")
            history = list(script.walk_revisions())[:5]
            for rev in history:
                status = "✅ APPLIED" if rev.revision <= current_rev else "⏳ PENDING"
                print(f"   {status} {rev.revision}: {rev.doc}")
                
    except Exception as e:
        print(f"❌ Migration debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

def debug_migration_script(revision: str):
    """Debug specific migration script."""
    print(f"🔍 Debugging migration: {revision}")
    
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get migration script
        rev = script.get_revision(revision)
        
        print(f"📄 Migration file: {rev.path}")
        print(f"📝 Description: {rev.doc}")
        print(f"⬆️ Upgrade function: {rev.upgrade}")
        print(f"⬇️ Downgrade function: {rev.downgrade}")
        
        # Read and display the migration file
        with open(rev.path, 'r') as f:
            content = f.read()
            print(f"\n📋 Migration content:\n{content}")
            
    except Exception as e:
        print(f"❌ Failed to debug migration {revision}: {str(e)}")
```

---

## 🤖 AI/ML Model Debugging

### Model Inference Debugging

#### 1. Audio Processing Model Debug
```python
import torch
import numpy as np
import librosa
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

class AudioModelDebugger:
    """Comprehensive debugging for audio processing models."""
    
    def __init__(self, model_path: str, debug_mode: bool = True):
        self.model_path = model_path
        self.debug_mode = debug_mode
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    async def debug_model_loading(self) -> Dict[str, Any]:
        """Debug model loading process."""
        debug_info = {
            "model_path": self.model_path,
            "device": str(self.device),
            "cuda_available": torch.cuda.is_available()
        }
        
        try:
            print(f"🤖 Loading model from: {self.model_path}")
            print(f"💻 Using device: {self.device}")
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load model
            self.model = torch.load(self.model_path, map_location=self.device)
            self.model.eval()
            
            # Get model info
            if hasattr(self.model, 'state_dict'):
                state_dict = self.model.state_dict()
                debug_info.update({
                    "model_loaded": True,
                    "num_parameters": sum(p.numel() for p in state_dict.values()),
                    "model_size_mb": sum(p.numel() * p.element_size() for p in state_dict.values()) / 1024 / 1024,
                    "layer_count": len(list(state_dict.keys()))
                })
                
                print(f"✅ Model loaded successfully")
                print(f"📊 Parameters: {debug_info['num_parameters']:,}")
                print(f"💾 Model size: {debug_info['model_size_mb']:.2f} MB")
            
        except Exception as e:
            debug_info.update({
                "model_loaded": False,
                "error": str(e)
            })
            print(f"❌ Model loading failed: {e}")
            
        return debug_info
    
    async def debug_audio_preprocessing(self, audio_path: str) -> Dict[str, Any]:
        """Debug audio preprocessing pipeline."""
        debug_info = {
            "audio_path": audio_path,
            "preprocessing_steps": []
        }
        
        try:
            print(f"🎵 Debugging audio preprocessing: {audio_path}")
            
            # Check file existence
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            step_info = {"step": "file_check", "status": "success"}
            debug_info["preprocessing_steps"].append(step_info)
            
            # Load audio
            print("1. Loading audio file...")
            audio, sr = librosa.load(audio_path, sr=None)
            
            step_info = {
                "step": "audio_loading",
                "status": "success",
                "original_sample_rate": sr,
                "duration_seconds": len(audio) / sr,
                "num_samples": len(audio)
            }
            debug_info["preprocessing_steps"].append(step_info)
            print(f"   ✅ Loaded: {len(audio)} samples at {sr} Hz ({len(audio)/sr:.2f}s)")
            
            # Check audio quality
            print("2. Analyzing audio quality...")
            
            # Check for silence
            rms = librosa.feature.rms(y=audio)[0]
            silence_ratio = np.sum(rms < 0.01) / len(rms)
            
            # Check for clipping
            clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)
            
            # Check dynamic range
            dynamic_range = np.max(audio) - np.min(audio)
            
            quality_info = {
                "step": "quality_analysis",
                "status": "success",
                "silence_ratio": float(silence_ratio),
                "clipping_ratio": float(clipping_ratio),
                "dynamic_range": float(dynamic_range),
                "rms_mean": float(np.mean(rms)),
                "rms_std": float(np.std(rms))
            }
            debug_info["preprocessing_steps"].append(quality_info)
            
            # Quality warnings
            if silence_ratio > 0.3:
                print(f"   ⚠️ High silence ratio: {silence_ratio:.1%}")
            if clipping_ratio > 0.01:
                print(f"   ⚠️ Audio clipping detected: {clipping_ratio:.1%}")
            if dynamic_range < 0.1:
                print(f"   ⚠️ Low dynamic range: {dynamic_range:.3f}")
            
            # Resample if needed
            target_sr = 22050
            if sr != target_sr:
                print(f"3. Resampling from {sr} Hz to {target_sr} Hz...")
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                sr = target_sr
                
                step_info = {
                    "step": "resampling",
                    "status": "success",
                    "target_sample_rate": target_sr,
                    "new_num_samples": len(audio)
                }
                debug_info["preprocessing_steps"].append(step_info)
            
            # Extract features
            print("4. Extracting features...")
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            
            features_info = {
                "step": "feature_extraction",
                "status": "success",
                "mfcc_shape": mfccs.shape,
                "mfcc_mean": float(np.mean(mfccs)),
                "mfcc_std": float(np.std(mfccs)),
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff))
            }
            debug_info["preprocessing_steps"].append(features_info)
            
            print(f"   ✅ MFCC shape: {mfccs.shape}")
            print(f"   ✅ Spectral centroid: {np.mean(spectral_centroids):.2f}")
            
            # Check for NaN or infinite values
            if np.isnan(mfccs).any():
                print("   ⚠️ NaN values detected in MFCC features")
            if np.isinf(mfccs).any():
                print("   ⚠️ Infinite values detected in MFCC features")
            
            # Save debug visualization
            if self.debug_mode:
                await self._save_debug_plots(audio, sr, mfccs, audio_path)
            
            debug_info["final_features"] = {
                "mfcc": mfccs.tolist(),
                "spectral_centroids": spectral_centroids.tolist(),
                "spectral_rolloff": spectral_rolloff.tolist()
            }
            
        except Exception as e:
            debug_info["error"] = str(e)
            print(f"❌ Preprocessing failed: {e}")
            import traceback
            traceback.print_exc()
        
        return debug_info
    
    async def debug_model_inference(self, features: np.ndarray) -> Dict[str, Any]:
        """Debug model inference process."""
        debug_info = {
            "input_shape": features.shape,
            "input_dtype": str(features.dtype)
        }
        
        try:
            print(f"🔮 Debugging model inference...")
            print(f"📊 Input shape: {features.shape}")
            print(f"🔢 Input dtype: {features.dtype}")
            
            # Check input validity
            if np.isnan(features).any():
                raise ValueError("Input contains NaN values")
            if np.isinf(features).any():
                raise ValueError("Input contains infinite values")
            
            # Convert to tensor
            input_tensor = torch.FloatTensor(features).to(self.device)
            if len(input_tensor.shape) == 2:
                input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension
            
            debug_info["tensor_shape"] = list(input_tensor.shape)
            
            print(f"🔄 Tensor shape: {input_tensor.shape}")
            
            # Model inference
            start_time = time.time()
            
            with torch.no_grad():
                output = self.model(input_tensor)
            
            inference_time = time.time() - start_time
            
            debug_info.update({
                "inference_time_ms": inference_time * 1000,
                "output_shape": list(output.shape),
                "output_dtype": str(output.dtype)
            })
            
            print(f"⚡ Inference time: {inference_time * 1000:.2f}ms")
            print(f"📤 Output shape: {output.shape}")
            
            # Convert output to numpy
            output_np = output.cpu().numpy()
            
            # Check output validity
            if np.isnan(output_np).any():
                print("⚠️ Model output contains NaN values")
            if np.isinf(output_np).any():
                print("⚠️ Model output contains infinite values")
            
            # Output statistics
            debug_info.update({
                "output_min": float(np.min(output_np)),
                "output_max": float(np.max(output_np)),
                "output_mean": float(np.mean(output_np)),
                "output_std": float(np.std(output_np))
            })
            
            print(f"📊 Output range: [{np.min(output_np):.4f}, {np.max(output_np):.4f}]")
            print(f"📊 Output mean: {np.mean(output_np):.4f}")
            
            # Interpret results (example for classification)
            if output.shape[-1] > 1:  # Multi-class classification
                probabilities = torch.softmax(output, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1)
                confidence = torch.max(probabilities, dim=-1)[0]
                
                debug_info.update({
                    "predicted_class": int(predicted_class.item()),
                    "confidence": float(confidence.item()),
                    "probabilities": probabilities.cpu().numpy().tolist()
                })
                
                print(f"🎯 Predicted class: {predicted_class.item()}")
                print(f"📊 Confidence: {confidence.item():.4f}")
            
            debug_info["success"] = True
            
        except Exception as e:
            debug_info.update({
                "success": False,
                "error": str(e)
            })
            print(f"❌ Model inference failed: {e}")
            import traceback
            traceback.print_exc()
        
        return debug_info
    
    async def _save_debug_plots(self, audio: np.ndarray, sr: int, mfccs: np.ndarray, audio_path: str):
        """Save debug visualization plots."""
        try:
            fig, axes = plt.subplots(3, 1, figsize=(12, 10))
            
            # Waveform
            axes[0].plot(np.linspace(0, len(audio)/sr, len(audio)), audio)
            axes[0].set_title("Audio Waveform")
            axes[0].set_xlabel("Time (s)")
            axes[0].set_ylabel("Amplitude")
            
            # Spectrogram
            D = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
            librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=axes[1])
            axes[1].set_title("Spectrogram")
            
            # MFCC
            librosa.display.specshow(mfccs, x_axis='time', ax=axes[2])
            axes[2].set_title("MFCC Features")
            axes[2].set_ylabel("MFCC Coefficients")
            
            plt.tight_layout()
            
            # Save plot
            debug_filename = f"/tmp/audio_debug_{os.path.basename(audio_path)}.png"
            plt.savefig(debug_filename, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"💾 Debug plot saved: {debug_filename}")
            
        except Exception as e:
            print(f"⚠️ Failed to save debug plots: {e}")
```

This comprehensive debugging guide provides practical tools and techniques for debugging every aspect of the Ainflue platform, from development environment issues to production problems. Each section includes real-world examples and actionable debugging code that developers can use immediately.