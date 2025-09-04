# Integration Tests

This directory contains comprehensive integration tests for the Ainflue platform, covering all major components and workflows.

## Directory Structure

### `/api_endpoints/`
Tests for comprehensive API endpoint functionality including:
- Authentication and authorization endpoints
- Content management and fingerprinting APIs
- Monetization and payment processing endpoints
- Platform monitoring and analytics APIs
- User management and collaboration endpoints

### `/database/`
Tests for database operations including:
- CRUD operations across all models
- Transaction handling and rollbacks
- Data integrity and constraints
- Migration testing
- Connection pooling and performance

### `/external_apis/`
Tests for external service integrations including:
- Payment processors (Stripe, PayPal)
- Platform APIs (Spotify, YouTube, Instagram)
- AI/ML services for content analysis
- Email and notification services
- Authentication providers

### `/workflow/`
Tests for end-to-end workflows including:
- Content upload to protection workflow
- User registration to monetization workflow
- Collaboration creation to completion workflow
- License creation to payment workflow
- Monitoring setup to detection workflow

### `/security/`
Tests for security features including:
- Authentication and authorization flows
- JWT token validation and refresh
- Rate limiting and DDoS protection
- Data encryption and decryption
- Security headers and CORS
- Input validation and sanitization

## Running Integration Tests

### Run All Tests
```bash
# Run all integration tests
python tests/integration/run_integration_tests.py all

# Or use pytest directly
python -m pytest tests/integration/ -m integration -v
```

### Run Specific Categories
```bash
# API endpoint tests
python tests/integration/run_integration_tests.py api

# Database tests
python tests/integration/run_integration_tests.py database

# External API tests
python tests/integration/run_integration_tests.py external

# Workflow tests
python tests/integration/run_integration_tests.py workflow

# Security tests
python tests/integration/run_integration_tests.py security

# Cross-service tests
python tests/integration/run_integration_tests.py cross-service
```

### Run Fast Tests Only
```bash
# Run only fast tests (exclude slow/long-running tests)
python tests/integration/run_integration_tests.py fast
```

### Run Critical Tests Only
```bash
# Run only critical integration tests
python tests/integration/run_integration_tests.py critical
```

## Test Configuration

Tests are configured to use:
- **pytest** with async support
- **aiohttp** for HTTP client testing
- **Mock services** for external dependencies
- **Test database** for safe testing
- **Coverage reporting** (optional)
- **Parallel execution** (optional with pytest-xdist)

## Test Markers

- `@pytest.mark.integration` - Marks tests as integration tests
- `@pytest.mark.slow` - Marks slow-running tests
- `@pytest.mark.security` - Marks security-related tests
- `@pytest.mark.asyncio` - Marks async tests

## Environment Setup

Before running integration tests, ensure:

1. **Test Database**: Set up a separate test database
2. **Environment Variables**: Configure test environment variables
3. **External Services**: Mock or configure test external services
4. **Dependencies**: Install test dependencies from requirements.txt

## Expected Coverage

Integration tests cover:
- ✅ End-to-end workflow functionality
- ✅ Cross-service integration
- ✅ Database operations and transactions
- ✅ External API integrations
- ✅ Security mechanisms
- ✅ Error handling and recovery
- ✅ Performance under load

## CI/CD Integration

Tests are designed to run in CI/CD environments with:
- Timeout configurations
- JUnit XML output
- Parallel execution support
- Proper cleanup and teardown

## Best Practices

1. **Test Independence**: Each test should be independent and can run in isolation
2. **Data Cleanup**: Tests clean up after themselves
3. **Mock External Services**: Use mocks for external dependencies
4. **Realistic Data**: Use realistic test data and scenarios
5. **Performance Awareness**: Monitor test execution time
6. **Error Scenarios**: Test both success and failure scenarios

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure test database is accessible
2. **Authentication**: Verify test user credentials
3. **External Services**: Check mock service configurations
4. **Timeouts**: Increase timeout for slow operations
5. **Port Conflicts**: Ensure test ports are available

### Debug Mode
```bash
# Run with debug output
python -m pytest tests/integration/ -v -s --tb=long

# Run specific test with debug
python -m pytest tests/integration/database/test_crud_operations.py::TestUserCRUDOperations::test_create_user -v -s
```