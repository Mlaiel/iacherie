# 🚀 Ainflue Platform Developer Guide

Complete guide for setting up and working with the Ainflue platform development environment.

## Quick Start

### 1. Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **VS Code** (recommended)

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue

# Run the setup script
chmod +x scripts/setup_dev_environment.sh
./scripts/setup_dev_environment.sh

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Start development services
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Verify Installation

```bash
# Run health checks
python -c "import main; print('✅ Main application imports successfully')"

# Run basic tests
pytest tests/simple_validation.py -v

# Check code quality
black --check .
flake8 .
mypy .
```

## Development Environment

### Docker Development Stack

The development environment includes:

- **Main API**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8080` 
- **PostgreSQL**: `localhost:5433`
- **Redis**: `localhost:6380`
- **MongoDB**: `localhost:27018`

### Hot Reload Features

The development environment supports:
- **File watching**: Automatic restart on code changes
- **Debug mode**: Remote debugging with VS Code
- **Performance monitoring**: Real-time performance metrics
- **Log streaming**: Live application logs

### VS Code Integration

#### Extensions Required
- Python
- Docker
- GitLens
- REST Client
- Prettier

#### Debug Configuration
```json
// .vscode/launch.json is pre-configured with:
{
    "name": "Python: FastAPI Development",
    "type": "python",
    "request": "launch",
    "program": "main.py",
    "env": {
        "ENVIRONMENT": "development",
        "DEBUG": "true"
    }
}
```

## Code Quality Standards

### Pre-commit Hooks

Automatically runs on each commit:
- **Black**: Code formatting
- **isort**: Import sorting  
- **Flake8**: Linting
- **MyPy**: Type checking
- **Bandit**: Security scanning

### Manual Quality Checks

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .

# Security scan
bandit -r .

# Dependency check
safety check
```

## Testing Framework

### Test Categories

```bash
# Unit tests
pytest -m "unit" -v

# Integration tests  
pytest -m "integration" -v

# API tests
pytest -m "api" -v

# Performance tests
pytest -m "performance" -v

# All tests with coverage
pytest --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_services/
│   ├── test_agents/
│   └── test_utils/
├── integration/            # Integration tests
│   ├── test_api/
│   ├── test_database/
│   └── test_external/
├── performance/            # Performance tests
│   ├── test_load/
│   └── test_stress/
└── conftest.py            # Test configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

class TestContentService:
    @pytest.fixture
    def service(self):
        return ContentService(config=test_config)
    
    @pytest.mark.unit
    async def test_analyze_content(self, service):
        # Unit test example
        result = await service.analyze("test_content")
        assert result["success"] is True
    
    @pytest.mark.integration  
    async def test_full_pipeline(self, service):
        # Integration test example
        result = await service.full_analysis_pipeline("content.mp4")
        assert "fingerprint" in result
        assert "copyright_check" in result
```

## API Development

### Creating New Endpoints

1. **Define Route Handler**:
```python
# api/routes/new_feature.py
from fastapi import APIRouter, Depends
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/new-feature", tags=["new-feature"])

@router.post("/process")
async def process_data(
    data: ProcessRequest,
    user: User = Depends(get_current_user)
) -> ProcessResponse:
    # Implementation
    return ProcessResponse(success=True)
```

2. **Add OpenAPI Documentation**:
```python
@router.post(
    "/process",
    summary="Process data",
    description="Process input data with AI analysis",
    response_model=ProcessResponse,
    responses={
        200: {"description": "Success"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"}
    }
)
```

3. **Include in Main App**:
```python
# api/asgi.py
from api.routes import new_feature

app.include_router(new_feature.router)
```

### API Documentation

Generate interactive documentation:
```bash
# Generate OpenAPI spec
python docs/interactive_api_documentation.py

# View at http://localhost:8080
```

## AI Agent Development

### Creating New AI Agents

Use the template generator:
```bash
# Interactive mode
python scripts/generate_template.py agent --interactive

# Command line mode
python scripts/generate_template.py agent \
    --name "ContentModerator" \
    --description "AI agent for content moderation" \
    --author-name "Your Name" \
    --author-email "your.email@example.com"
```

### Agent Structure

```python
from templates.agent_template import BaseAgent

class MyAgent(BaseAgent):
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Custom agent logic
        return {"response": "processed"}
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]):
        # Learning implementation
        pass
```

### Agent Testing

```python
class TestMyAgent:
    @pytest.fixture
    def agent(self):
        return MyAgent(config=test_config)
    
    @pytest.mark.ai
    async def test_agent_response(self, agent):
        response = await agent.process_request({
            "message": "test input"
        })
        assert response["success"] is True
```

## Service Development

### Creating New Services

Use the template generator:
```bash
python scripts/generate_template.py service \
    --name "AnalyticsService" \
    --description "Advanced analytics service"
```

### Service Structure

```python
from templates.service_template import BaseService

class MyService(BaseService):
    async def start(self) -> bool:
        # Service initialization
        return True
    
    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Business logic
        return {"result": "processed"}
```

## Database Development

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Database Testing

```python
@pytest.mark.database
async def test_user_creation():
    user = await create_user({"email": "test@example.com"})
    assert user.id is not None
```

## Performance Optimization

### Profiling

```bash
# Profile application
python -m cProfile -o profile.prof main.py

# Analyze profile
python -c "
import pstats
stats = pstats.Stats('profile.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)
"

# Memory profiling
python -m memory_profiler main.py
```

### Performance Monitoring

The development environment includes built-in performance monitoring:
```bash
# Start performance monitor
docker-compose -f docker-compose.dev.yml --profile monitoring up
```

### Load Testing

```bash
# Install tools
pip install locust

# Run load tests
locust -f tests/performance/load_test.py --host=http://localhost:8000
```

## Debugging

### VS Code Debugging

1. Set breakpoints in code
2. Run "Python: FastAPI with Debugpy" configuration
3. Attach debugger to running container

### Remote Debugging

```python
# Add to code for remote debugging
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()  # Optional: wait for debugger
```

### Log Analysis

```bash
# View application logs
docker-compose -f docker-compose.dev.yml logs -f ainflue-dev

# Structured logging
python -c "
from core.logging import logger
logger.info('Test message', extra={'user_id': '123'})
"
```

## Deployment

### Environment Configuration

```bash
# Development
export ENVIRONMENT=development
export DEBUG=true

# Staging  
export ENVIRONMENT=staging
export DEBUG=false

# Production
export ENVIRONMENT=production
export DEBUG=false
```

### Docker Build

```bash
# Build development image
docker build -f docker/Dockerfile.dev --target development -t ainflue:dev .

# Build production image
docker build -f docker/Dockerfile.dev --target production-dev -t ainflue:prod .
```

## SDK Development

### Python SDK

```bash
cd sdk/python

# Install in development mode
pip install -e .

# Run SDK tests
pytest tests/ -v

# Build package
python -m build

# Install from local build
pip install dist/ainflue_sdk-1.0.0-py3-none-any.whl
```

### SDK Testing

```python
# Test SDK functionality
import asyncio
from ainflue_sdk import AinflueSdk

async def test_sdk():
    async with AinflueSdk("test-api-key") as sdk:
        result = await sdk.content.analyze("test.mp4")
        print(result)

asyncio.run(test_sdk())
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Fix Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check imports
python -c "import sys; print(sys.path)"
```

#### Database Connection
```bash
# Check database status
docker-compose -f docker-compose.dev.yml ps postgres-dev

# Connect to database
docker exec -it ainflue-postgres-dev psql -U dev_user -d ainflue_dev
```

#### Redis Connection  
```bash
# Check Redis
docker exec -it ainflue-redis-dev redis-cli ping

# View Redis data
docker exec -it ainflue-redis-dev redis-cli keys "*"
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check application metrics
curl http://localhost:8000/metrics
```

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Run diagnostics**: `python scripts/dev_health_check.py`
3. **Check documentation**: `docs/` directory
4. **Contact support**: mlaiel@live.de

## Development Workflow

### Feature Development

1. **Create branch**: `git checkout -b feature/new-feature`
2. **Write tests**: Test-driven development
3. **Implement feature**: Follow coding standards
4. **Run quality checks**: Pre-commit hooks
5. **Test thoroughly**: Unit, integration, performance
6. **Update documentation**: API docs, README
7. **Create PR**: Detailed description
8. **Code review**: Address feedback
9. **Merge**: After approval

### Code Review Checklist

- [ ] Tests written and passing
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Backward compatibility maintained

## Best Practices

### Code Organization

```
project/
├── api/                    # API layer
├── core/                   # Core utilities
├── services/               # Business services
├── ai_agents/              # AI agent implementations
├── database/               # Database models
├── config/                 # Configuration
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Development scripts
└── templates/              # Code templates
```

### Error Handling

```python
from core.exceptions import AinfluException

try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    raise AinfluException(f"Operation failed: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    raise AinfluException("Unexpected error occurred")
```

### Logging

```python
from core.logging import logger

# Structured logging
logger.info(
    "User action completed",
    extra={
        "user_id": user.id,
        "action": "content_upload",
        "duration_ms": duration,
        "success": True
    }
)
```

### Configuration Management

```python
from config.settings import settings

# Type-safe configuration
database_url = settings.database.url
api_key = settings.external_apis.openai.api_key
debug_mode = settings.app.debug
```

## Resources

### Documentation
- [Architecture Guide](ARCHITECTURE.md)
- [API Documentation](https://docs.ainflue.com/api)
- [SDK Documentation](sdk/python/README.md)

### Tools
- [VS Code Extensions](.vscode/extensions.json)
- [Docker Compose](docker-compose.dev.yml)
- [Pre-commit Config](.pre-commit-config.yaml)

### Templates
- [Service Template](templates/service_template.py)
- [Agent Template](templates/agent_template.py)
- [Test Templates](tests/templates/)

---

**Happy Coding!** 🚀

For questions or support, contact [mlaiel@live.de](mailto:mlaiel@live.de)