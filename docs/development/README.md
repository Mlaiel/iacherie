# Ainflue Platform Developer Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Git
- Node.js 18+ (for frontend development)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue
```

2. **Run the setup script**
```bash
./scripts/dev/setup.sh
```

3. **Start the development environment**
```bash
# Option 1: Local development
./scripts/dev/run.sh

# Option 2: Docker Compose
docker-compose up
```

4. **Access the application**
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- API Base URL: http://localhost:8000/api/v1
- Grafana Dashboard: http://localhost:3000 (admin/admin123)
- Prometheus Metrics: http://localhost:9090

## 🛠️ Development Tools

### IDE Configuration

The project includes VSCode configuration with:
- Python linting and formatting
- Type checking with MyPy
- Debugging configurations
- Testing support
- Docker integration

**Extensions Recommended:**
- Python
- Pylance
- Black Formatter
- Docker
- REST Client
- GitLens

### Code Quality Tools

```bash
# Format code
./scripts/dev/lint.sh

# Run tests
./scripts/dev/test.sh

# Profile performance
./scripts/dev/profile.sh

# Check code quality
pre-commit run --all-files
```

### Pre-commit Hooks

The project uses pre-commit hooks for automated code quality:

```bash
# Install hooks (done automatically by setup script)
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## 📚 Project Structure

```
Ainflue/
├── api/                    # FastAPI application
│   ├── routes/            # API route handlers
│   ├── middleware/        # Custom middleware
│   └── asgi.py           # ASGI application
├── core/                  # Core business logic
│   ├── models/           # Data models
│   ├── services/         # Business services
│   └── database/         # Database configuration
├── ai_agents/            # AI processing agents
├── config/               # Configuration management
├── tests/                # Test suite
├── scripts/              # Development scripts
├── docs/                 # Documentation
├── sdk/                  # SDK for developers
├── templates/            # Code templates
├── docker/               # Docker configurations
└── monitoring/           # Monitoring configs
```

## 🔧 Development Workflow

### 1. Creating New Services

Use the service generator to create new services:

```bash
# Generate a new service
python scripts/dev/generate_service.py ContentAnalysis \
  --author "Your Name" \
  --email "your.email@example.com" \
  --description "Advanced content analysis service"

# This creates:
# - services/content_analysis_service.py
# - api/routes/content_analysis_routes.py
# - tests/services/test_content_analysis_service.py
# - docs/services/content_analysis.md
```

### 2. Creating AI Agents

Generate new AI agents for specific tasks:

```bash
# Generate a new AI agent
python scripts/dev/generate_agent.py ContentClassifier \
  --author "Your Name" \
  --email "your.email@example.com" \
  --description "AI agent for content classification"

# This creates:
# - ai_agents/content_classifier_agent.py
# - tests/ai_agents/test_content_classifier_agent.py
# - docs/ai_agents/content_classifier.md
```

### 3. Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Downgrade to previous version
alembic downgrade -1
```

### 4. Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_content_service.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run performance tests
pytest -m performance

# Run integration tests
pytest -m integration
```

### 5. API Development

#### Adding New Endpoints

1. **Create the route handler**:
```python
# api/routes/my_new_routes.py
from fastapi import APIRouter, Depends
from services.my_service import MyService

router = APIRouter(prefix="/my-endpoint", tags=["My Service"])

@router.post("/process")
async def process_data(
    data: MyRequestModel,
    service: MyService = Depends(get_my_service)
):
    result = await service.process(data)
    return result
```

2. **Register the router**:
```python
# api/asgi.py or main router file
from api.routes.my_new_routes import router as my_router
app.include_router(my_router)
```

3. **Add tests**:
```python
# tests/api/test_my_new_routes.py
def test_process_endpoint(client):
    response = client.post("/my-endpoint/process", json={...})
    assert response.status_code == 200
```

### 6. Environment Configuration

#### Development Environment
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

#### Docker Environment
```bash
# Environment variables in docker-compose.yml
POSTGRES_HOST=postgres
REDIS_HOST=redis
MONGODB_HOST=mongodb
```

## 🐛 Debugging

### Local Debugging

1. **Using VSCode**:
   - Set breakpoints in your code
   - Press F5 or use "Debug Ainflue API" configuration
   - The debugger will start and stop at breakpoints

2. **Using command line**:
```bash
# Run with debugger
python -m pdb main.py

# Or with ipdb (if installed)
python -m ipdb main.py
```

### Docker Debugging

```bash
# Debug in Docker container
docker-compose exec app python -m ipdb main.py

# View logs
docker-compose logs -f app

# Shell into container
docker-compose exec app bash
```

### Remote Debugging

For debugging in production-like environments:

```python
# Add to your code
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()  # Optional: wait for debugger
```

## 📊 Performance Monitoring

### Local Profiling

```bash
# CPU profiling
./scripts/dev/profile.sh

# Memory profiling
python -m memory_profiler main.py

# Line profiling (requires @profile decorators)
kernprof -l -v main.py
```

### Metrics Collection

The application exposes Prometheus metrics at `/metrics`:

```python
# Custom metrics example
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    request_duration.observe(time.time() - start_time)
    request_count.inc()
    return response
```

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`):
   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`tests/integration/`):
   - Test service interactions
   - Use test database
   - Test API endpoints

3. **End-to-End Tests** (`tests/e2e/`):
   - Test complete workflows
   - Use full application stack
   - Simulate real user scenarios

### Test Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)

@pytest.fixture
async def db_session():
    """Database session for testing"""
    # Setup test database
    # Yield session
    # Cleanup
```

### Mocking External Services

```python
# tests/test_external_service.py
from unittest.mock import patch

@patch('services.external_api.make_request')
async def test_external_service_call(mock_request):
    mock_request.return_value = {"status": "success"}
    
    result = await my_service.call_external_api()
    assert result["status"] == "success"
```

## 🔒 Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        # Custom email validation
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v
```

### Authentication

```python
from fastapi import Depends, HTTPException, status
from core.security import verify_token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user
```

### Rate Limiting

```python
from fastapi import Depends
from core.rate_limiter import RateLimiter

rate_limiter = RateLimiter(requests_per_minute=60)

@app.post("/api/endpoint")
async def protected_endpoint(
    request: Request,
    _: None = Depends(rate_limiter)
):
    # Endpoint logic
    pass
```

## 📦 Deployment

### Local Deployment

```bash
# Build and run locally
./scripts/dev/run.sh

# Or with Docker
docker-compose up --build
```

### Staging Deployment

```bash
# Build for staging
docker build -f docker/Dockerfile.dev --target production .

# Deploy to staging
kubectl apply -f k8s/staging/
```

### Production Deployment

```bash
# Production build
docker build -f docker/Dockerfile.production .

# Deploy to production
kubectl apply -f k8s/production/
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=$(pwd)
   ```

2. **Database Connection**:
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # View database logs
   docker-compose logs postgres
   ```

3. **Port Conflicts**:
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

### Debugging Commands

```bash
# Check application health
curl http://localhost:8000/health

# View application logs
docker-compose logs -f app

# Check service status
docker-compose ps

# Restart specific service
docker-compose restart app
```

## 📖 API Documentation

### OpenAPI Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Spec: http://localhost:8000/openapi.json

### Adding Documentation

```python
@app.post(
    "/content/analyze",
    response_model=AnalysisResult,
    summary="Analyze content",
    description="Analyze content for fingerprinting and protection",
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_content(content: ContentInput):
    """
    Analyze content for AI-powered fingerprinting.
    
    - **content**: The content to analyze
    - **options**: Analysis configuration options
    
    Returns detailed analysis results including:
    - Content fingerprint
    - Metadata extraction
    - Similarity scores
    - Protection recommendations
    """
    # Implementation
    pass
```

## 🤝 Contributing

### Code Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Write docstrings for public APIs
- Maximum line length: 100 characters

### Commit Messages

```
feat: add new content analysis endpoint
fix: resolve authentication token expiration
docs: update API documentation
test: add integration tests for payment service
refactor: optimize database queries
```

### Pull Request Process

1. Create feature branch from main
2. Make changes with tests
3. Run quality checks: `./scripts/dev/lint.sh`
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

## 📞 Support

### Getting Help

- **Documentation**: Check `/docs` directory
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: mlaiel@live.de for direct support

### Development Resources

- **API Reference**: Generated OpenAPI docs
- **Architecture Guide**: `/docs/architecture/README.md`
- **SDK Documentation**: `/sdk/python/README.md`
- **Examples**: `/examples` directory

---

**Happy Coding! 🎉**

For more information, visit the [project repository](https://github.com/Mlaiel/Ainflue).