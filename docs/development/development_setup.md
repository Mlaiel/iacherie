# Development Environment Setup Guide

## Overview
This guide helps developers set up a complete development environment for the Ainflue platform.

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Platform Version:** 1.0.0  

## Prerequisites

### Required Software
- Python 3.12+
- Node.js 18+ (for frontend development)
- Docker & Docker Compose
- Git
- PostgreSQL 15+
- Redis 7+
- MongoDB 7+

### Development Tools
- VS Code or PyCharm
- Postman or Insomnia (API testing)
- pgAdmin (PostgreSQL GUI)
- MongoDB Compass (MongoDB GUI)
- Redis Insight (Redis GUI)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.development.example .env

# Edit .env file with your configurations
nano .env
```

### 4. Database Setup
```bash
# Start databases with Docker
docker-compose -f docker-compose.yml up -d

# Initialize databases
python scripts/init_databases.py

# Run migrations
alembic upgrade head
```

### 5. Start Development Server
```bash
# Start the main application
python main.py

# Or use uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
Ainflue/
├── api/                    # FastAPI application
│   ├── main.py            # Main FastAPI app
│   └── routes/            # API routes
├── monetization/          # Revenue & payment processing
├── crawlers/             # Content monitoring crawlers
├── analytics/            # Analytics & reporting
├── ai_engine/            # AI/ML processing
├── services/             # Business logic services
├── database/             # Database schemas & migrations
├── core/                 # Core utilities
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── monitoring/           # Monitoring configurations
├── kubernetes/           # K8s deployment files
├── docker/               # Docker configurations
├── requirements.txt      # Python dependencies
├── main.py              # Application entry point
├── config.py            # Configuration management
└── README.md            # Project README
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Make your changes
# ...

# Run tests
pytest tests/ -v

# Run linting
black . && flake8 . && mypy .

# Commit changes
git add .
git commit -m "feat: add new feature description"

# Push branch
git push origin feature/new-feature-name
```

### 2. Testing
```bash
# Run all tests
pytest

# Run specific test category
pytest -m "unit"
pytest -m "integration"
pytest -m "monetization"

# Run with coverage
pytest --cov=. --cov-report=html

# Run performance tests
pytest -m "slow"
```

### 3. Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Security scanning
bandit -r .

# Dependency checking
safety check
```

## Database Development

### PostgreSQL Schema
```sql
-- Main application tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revenue tracking
CREATE TABLE revenue_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(id),
    platform VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MongoDB Collections
```javascript
// Content fingerprints
db.content_fingerprints.insertOne({
  content_id: "uuid",
  fingerprint_type: "audio_hash",
  fingerprint_data: "hash_value",
  metadata: {
    duration: 180,
    sample_rate: 44100,
    channels: 2
  },
  created_at: new Date()
});

// Platform monitoring results
db.monitoring_results.insertOne({
  original_content_id: "uuid",
  platform: "youtube",
  search_query: "search terms",
  potential_violations: [
    {
      platform_content_id: "external_id",
      similarity_score: 0.95,
      detected_segments: [
        {
          start: 10.5,
          end: 25.3,
          similarity: 0.92
        }
      ]
    }
  ],
  scan_date: new Date()
});
```

### Redis Cache Structure
```bash
# User sessions
SET "session:user_id" "session_data" EX 3600

# Revenue cache
SET "revenue:content_id:2025-01-15" "revenue_data" EX 86400

# Rate limiting
INCR "rate_limit:user_id:endpoint" EX 3600

# Platform API cache
SET "platform:youtube:video_id" "video_metadata" EX 300
```

## API Development

### Creating New Endpoints
```python
# api/routes/example.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from core.auth import get_current_user
from services.example_service import ExampleService

router = APIRouter(prefix="/example", tags=["example"])

class ExampleRequest(BaseModel):
    name: str
    value: int

class ExampleResponse(BaseModel):
    id: str
    name: str
    value: int

@router.post("/", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    current_user = Depends(get_current_user),
    service: ExampleService = Depends()
):
    """Create a new example resource."""
    try:
        result = await service.create_example(
            user_id=current_user.id,
            name=request.name,
            value=request.value
        )
        return ExampleResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Adding to Main App
```python
# api/main.py
from api.routes import example

app.include_router(example.router, prefix="/api/v1")
```

## Service Development

### Service Pattern
```python
# services/example_service.py
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from database.models import ExampleModel
from core.exceptions import ServiceException

logger = logging.getLogger(__name__)

class ExampleService:
    """Example service for business logic."""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    async def create_example(
        self, 
        user_id: str, 
        name: str, 
        value: int
    ) -> Dict:
        """Create example with validation."""
        try:
            # Validation
            if not name or len(name) < 3:
                raise ServiceException("Name must be at least 3 characters")
            
            if value < 0:
                raise ServiceException("Value must be positive")
            
            # Business logic
            example_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": name,
                "value": value,
                "created_at": datetime.now()
            }
            
            # Database operation
            # await self.db_session.add(ExampleModel(**example_data))
            # await self.db_session.commit()
            
            logger.info(f"Example created: {example_data['id']}")
            return example_data
            
        except Exception as e:
            logger.error(f"Error creating example: {str(e)}")
            raise ServiceException(f"Failed to create example: {str(e)}")
    
    async def get_examples(self, user_id: str) -> List[Dict]:
        """Get user's examples."""
        try:
            # Database query
            # examples = await self.db_session.query(ExampleModel).filter_by(user_id=user_id).all()
            # return [example.to_dict() for example in examples]
            
            # Mock response for development
            return [
                {
                    "id": "example_1",
                    "name": "Example 1",
                    "value": 100,
                    "created_at": datetime.now()
                }
            ]
            
        except Exception as e:
            logger.error(f"Error fetching examples: {str(e)}")
            raise ServiceException(f"Failed to fetch examples: {str(e)}")
```

## Testing Development

### Unit Test Template
```python
# tests/test_services/test_example_service.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from services.example_service import ExampleService
from core.exceptions import ServiceException

class TestExampleService:
    """Test suite for ExampleService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ExampleService()
    
    @pytest.mark.unit
    async def test_create_example_success(self, service):
        """Test successful example creation."""
        result = await service.create_example(
            user_id="user_123",
            name="Test Example",
            value=100
        )
        
        assert result["user_id"] == "user_123"
        assert result["name"] == "Test Example"
        assert result["value"] == 100
        assert "id" in result
        assert "created_at" in result
    
    @pytest.mark.unit
    async def test_create_example_invalid_name(self, service):
        """Test example creation with invalid name."""
        with pytest.raises(ServiceException) as exc_info:
            await service.create_example(
                user_id="user_123",
                name="ab",  # Too short
                value=100
            )
        
        assert "Name must be at least 3 characters" in str(exc_info.value)
    
    @pytest.mark.unit
    async def test_create_example_negative_value(self, service):
        """Test example creation with negative value."""
        with pytest.raises(ServiceException) as exc_info:
            await service.create_example(
                user_id="user_123",
                name="Valid Name",
                value=-10  # Negative value
            )
        
        assert "Value must be positive" in str(exc_info.value)
    
    @pytest.mark.unit
    async def test_get_examples(self, service):
        """Test fetching user examples."""
        examples = await service.get_examples("user_123")
        
        assert isinstance(examples, list)
        assert len(examples) >= 0
        
        if examples:
            example = examples[0]
            assert "id" in example
            assert "name" in example
            assert "value" in example
```

### Integration Test Template
```python
# tests/integration/test_example_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from api.main import app

class TestExampleAPI:
    """Integration tests for Example API."""
    
    @pytest.mark.integration
    async def test_create_example_endpoint(self, test_client: AsyncClient):
        """Test example creation endpoint."""
        request_data = {
            "name": "Integration Test Example",
            "value": 200
        }
        
        response = await test_client.post(
            "/api/v1/example/",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == request_data["name"]
        assert data["value"] == request_data["value"]
        assert "id" in data
    
    @pytest.mark.integration
    async def test_get_examples_endpoint(self, test_client: AsyncClient):
        """Test get examples endpoint."""
        response = await test_client.get(
            "/api/v1/example/",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

## Configuration Management

### Development Settings
```python
# config/development.py
from config.base import BaseSettings

class DevelopmentSettings(BaseSettings):
    """Development environment settings."""
    
    # Override base settings for development
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Database URLs for development
    postgres_host: str = "localhost"
    redis_host: str = "localhost"
    mongodb_host: str = "localhost"
    
    # Disable external services in development
    enable_email_notifications: bool = False
    enable_external_apis: bool = False
    
    # Mock payment processing
    stripe_secret_key: str = "sk_test_development"
    paypal_environment: str = "sandbox"
    
    # Fast processing for development
    cache_ttl: int = 60  # 1 minute instead of production values
    
    class Config:
        env_file = ".env.development"
```

## Debugging

### VS Code Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "ENVIRONMENT": "development",
                "DEBUG": "true"
            }
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "tests/"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### Logging Configuration
```python
# core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level: str = "INFO", format_type: str = "json"):
    """Setup application logging."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    if format_type == "json":
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        # Simple formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

## Performance Optimization

### Database Optimization
```python
# database/optimization.py
from sqlalchemy import Index, text
from sqlalchemy.ext.asyncio import AsyncSession

class DatabaseOptimization:
    """Database optimization utilities."""
    
    @staticmethod
    async def create_indexes(session: AsyncSession):
        """Create performance indexes."""
        indexes = [
            # User-related indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username)",
            
            # Content indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_id ON content(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_type ON content(content_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_created_at ON content(created_at)",
            
            # Revenue indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_revenue_content_id ON revenue_records(content_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_revenue_platform ON revenue_records(platform)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_revenue_period ON revenue_records(period_start, period_end)",
        ]
        
        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
                await session.commit()
            except Exception as e:
                logging.warning(f"Index creation failed: {e}")
                await session.rollback()
```

### Caching Strategy
```python
# core/cache.py
import asyncio
import json
from typing import Any, Optional
from redis.asyncio import Redis
from functools import wraps

class CacheManager:
    """Redis cache management."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value."""
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl)
        except Exception:
            pass  # Fail silently for cache operations
    
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
```

## Contribution Guidelines

### Code Standards
1. **PEP 8 Compliance**: Use black for formatting
2. **Type Hints**: All functions must have type hints
3. **Docstrings**: All public functions must have docstrings
4. **Error Handling**: Proper exception handling required
5. **Testing**: Minimum 90% test coverage for new code

### Commit Messages
```
feat: add new feature
fix: bug fix
docs: documentation update
style: code formatting
refactor: code refactoring
test: add or update tests
chore: maintenance tasks
```

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Submit pull request with detailed description
6. Address review feedback
7. Squash and merge after approval

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if database is running
   docker ps | grep postgres
   
   # Check connection
   psql -h localhost -U ainflue -d ainflue_platform
   ```

2. **Redis Connection Error**
   ```bash
   # Check Redis
   redis-cli ping
   
   # Check configuration
   echo "REDIS_HOST=localhost" >> .env
   ```

3. **Import Errors**
   ```bash
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Test Failures**
   ```bash
   # Run tests with verbose output
   pytest -v -s
   
   # Run specific test
   pytest tests/test_specific.py::test_function -v
   ```

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Redis Documentation**: https://redis.io/documentation
- **MongoDB Documentation**: https://docs.mongodb.com/
- **Pytest Documentation**: https://docs.pytest.org/

---

**For development support: mlaiel@live.de**

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**