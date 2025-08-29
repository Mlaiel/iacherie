# 🚀 Quick Setup Guide - API Documentation & Security Audit

## Prerequisites

1. **Python 3.8+** installed
2. **Git** for repository management
3. **Text editor** or IDE

## Installation Steps

### 1. Install Core Dependencies

```bash
# Core FastAPI dependencies
pip install fastapi uvicorn[standard] pydantic pydantic-settings

# Additional recommended dependencies
pip install python-multipart python-jose[cryptography] passlib[bcrypt]
```

### 2. Environment Configuration

Create `.env` file in the root directory:

```env
# API Configuration
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Security Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-min-32-chars
ENCRYPTION_KEY=your-encryption-key-here-32-chars

# Database Configuration (optional for basic testing)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ainflue
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=ainflue_platform

REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. Start the API Server

```bash
# Navigate to project directory
cd /path/to/Ainflue

# Start the development server
uvicorn api.asgi:app --host 0.0.0.0 --port 8000 --reload

# Alternative using Python
python -m uvicorn api.asgi:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 Accessing Documentation

### Swagger UI (Interactive)
- **URL**: http://localhost:8000/docs
- **Features**: Try-it-out functionality, authentication testing

### ReDoc (Alternative)
- **URL**: http://localhost:8000/redoc  
- **Features**: Clean documentation view

### OpenAPI JSON Schema
- **URL**: http://localhost:8000/openapi.json
- **Use**: For code generation, API testing tools

## 🔐 Testing Security Features

### 1. System Health Check
```bash
curl http://localhost:8000/health
```

### 2. Start Security Audit
```bash
curl -X POST "http://localhost:8000/api/v1/security/audit/start" \
     -H "Content-Type: application/json" \
     -d '{
       "audit_type": "quick",
       "scope": ["infrastructure", "application"],
       "priority": "normal"
     }'
```

### 3. Get Security Metrics
```bash
curl http://localhost:8000/api/v1/security/metrics
```

### 4. Security Dashboard
```bash
curl http://localhost:8000/api/v1/security/dashboard
```

## 🧪 Testing Authentication

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "username": "testuser",
       "password": "SecurePass123!",
       "confirm_password": "SecurePass123!",
       "full_name": "Test User",
       "terms_accepted": true,
       "privacy_policy_accepted": true
     }'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "SecurePass123!"
     }'
```

## 🛠️ Development Tools

### Interactive API Testing
1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Enter your API credentials
4. Test endpoints directly in browser

### API Testing with Postman
1. Import OpenAPI schema: http://localhost:8000/openapi.json
2. Configure authentication
3. Test all endpoints

### Code Generation
Use the OpenAPI schema to generate client libraries:
```bash
# Example with OpenAPI Generator
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client
```

## 🔍 Security Audit Features

### Supported Audit Types
- **quick**: Essential security checks (5-15 minutes)
- **full**: Comprehensive audit (1-3 hours)  
- **compliance**: Standards compliance (30-60 minutes)
- **targeted**: Specific component audit

### Compliance Standards
- **GDPR**: Data protection regulation
- **SOC2**: Service organization controls
- **ISO27001**: Information security management
- **OWASP**: Web application security
- **PCI-DSS**: Payment card security
- **HIPAA**: Healthcare data protection

### Security Scan Types
- **dependencies**: Third-party vulnerabilities
- **infrastructure**: Network and system security
- **application**: Code and configuration security
- **api**: API security and authentication

## 📊 Monitoring & Metrics

### Health Endpoints
- **System Health**: `/health`
- **Readiness Check**: `/ready`
- **Security Health**: `/api/v1/security/health`

### Metrics Endpoints
- **Security Metrics**: `/api/v1/security/metrics`
- **Dashboard Data**: `/api/v1/security/dashboard`
- **Compliance Status**: `/api/v1/security/compliance/report`

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **Authentication Errors**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration settings

3. **Database Connection**
   - Verify database configuration
   - Check connection strings

4. **Permission Errors**
   - Ensure proper file permissions
   - Check user access rights

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with verbose output
uvicorn api.asgi:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📧 Support

For issues or questions:
- **Email**: mlaiel@live.de
- **Documentation**: Available at `/docs` when server is running
- **Security Issues**: Use security audit endpoints for automated detection

---

🎉 **Ready to Go!** Your comprehensive API documentation and security audit system is now operational.