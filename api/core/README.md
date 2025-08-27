# IA Influencer Agent - Core Infrastructure Module

## 🏗️ Enterprise-Grade Core Systems

This module provides the foundational infrastructure for the IA Influencer Agent platform, implementing professional-grade systems for content protection, AI processing, and influencer collaboration.

### 🎯 Business Logic Overview

**Multi-Creator Workflow:** Musicians, bloggers, photographers, influencers, comedians → Upload multi-format content → AI protection & rights management → Professional SEO → Collaboration matching → Multi-platform distribution

### 👥 Expert Team

**Project Lead & Architect:** Fahed Mlaiel <mlaiel@live.de>
- **Specialties:** Lead AI Developer, Senior Backend Engineer, ML Engineer, Database Administrator, Security Expert, Microservices Architect, Audio Processing Specialist, DevOps Engineer, AI Prompt Engineer

---

## ⚠️ INTELLECTUAL PROPERTY WARNING

**STRICT COPYRIGHT NOTICE - UNAUTHORIZED USE PROHIBITED**

This software, concept, and implementation are the exclusive intellectual property of **Fahed Mlaiel** (mlaiel@live.de). 

**WARNING TO ALL PERSONS AND ENTITIES:**
- **NO PERMISSION** is granted to copy, modify, distribute, or use this code without explicit written authorization from Fahed Mlaiel
- **LEGAL ACTION** will be pursued against any unauthorized use, copying, or theft of this intellectual property
- **MONETARY DAMAGES** and injunctive relief will be sought for any violations
- This code is protected under international copyright laws and treaties

**Contact for Licensing:** mlaiel@live.de

---

## 🏭 Core Infrastructure Components

### 🔧 Configuration Management (`config.py`)
- Environment-based configuration with secure defaults
- Multi-environment support (development, staging, production)
- Centralized settings with type validation using Pydantic

### 🗄️ Database Integration (`db.py`)
- PostgreSQL primary database with connection pooling
- Redis caching layer with intelligent strategies
- Database session management with proper lifecycle

### 📊 Enterprise Logging (`logging.py`)
- Structured JSON logging with correlation IDs
- Multiple output formats (console, file, remote)
- Performance monitoring and error tracking

### 🔐 Security Framework (`security.py`)
- JWT authentication with refresh tokens
- API key management with rate limiting
- Multi-tenant security isolation

### ⚡ Exception Management (`exceptions.py`)
- Comprehensive error hierarchy for business logic
- Professional error codes and user-friendly messages
- HTTP status code mapping with detailed context

### 🏗️ Dependency Injection (`container.py`)
- Professional IoC container with lifecycle management
- Service registration with singleton, transient, and scoped lifetimes
- Automatic dependency resolution with type hints

### 🚀 Event System (`events.py`)
- Domain event sourcing with comprehensive metadata
- Asynchronous event bus with priority handling
- Business events for content protection workflow

### 💾 Multi-Level Caching (`cache.py`)
- L1 (Memory) + L2 (Redis) + L3 (Database) caching hierarchy
- Intelligent cache invalidation strategies (LRU, LFU, TTL)
- Cache promotion and business-specific key generators

### 🌐 Request Context (`context.py`)
- Distributed tracing with correlation IDs
- User session and tenant isolation
- Business operation context tracking

### 📈 Metrics & Monitoring (`metrics.py`)
- Business metrics for content protection workflow
- System performance monitoring with timing and counters
- Professional observability with Prometheus-compatible format

### 🩺 Health Monitoring (`health.py`)
- Comprehensive health checks for all dependencies
- Database, Redis, external APIs, and storage monitoring
- Graceful degradation with detailed status reporting

### 🛡️ Rate Limiting (`rate_limit.py`)
- Multiple algorithms: Token Bucket, Sliding Window, Fixed Window
- Configurable scopes: User, IP, API Key, Endpoint, Tenant
- Professional rate limiting with proper headers

---

## 🚀 Quick Start

```python
from app.core import (
    settings,
    get_db,
    get_cache_manager,
    get_event_bus,
    get_metrics_registry,
    check_system_health
)

# Initialize core systems
cache = get_cache_manager()
metrics = get_metrics_registry()
event_bus = await get_event_bus()

# Check system health
health_status = await check_system_health()
print(f"System Status: {health_status.overall_status.value}")
```

## 🎯 Business Metrics Integration

```python
from app.core import get_business_metrics

business_metrics = get_business_metrics()

# Record content upload
business_metrics.record_content_upload(
    content_type="audio",
    file_size_mb=25.5,
    user_id="user123"
)

# Record fingerprint generation
business_metrics.record_fingerprint_generation(
    content_type="audio",
    duration_ms=1250.0,
    accuracy_score=0.95
)
```

## 🔄 Event-Driven Architecture

```python
from app.core import publish_event, ContentUploadedEvent

# Publish business event
await publish_event(ContentUploadedEvent(
    content_id="content123",
    user_id="user123",
    content_type="audio",
    file_path="/uploads/audio/song.mp3",
    file_size=26214400
))
```

## 🏷️ Professional Error Handling

```python
from app.core import ContentNotFoundException, ErrorCode

# Raise business exception
raise ContentNotFoundException(
    content_id="missing123",
    content_type="audio_track"
)

# Use error codes
if error_code == ErrorCode.FINGERPRINT_GENERATION_FAILED:
    # Handle fingerprint error
    pass
```

---

## 📋 Module Dependencies

- **FastAPI**: Modern web framework with automatic documentation
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: Database ORM with async support
- **Redis**: High-performance caching and session storage
- **Prometheus Client**: Metrics collection and monitoring

## 🔗 Integration Points

This core module integrates with:
- **Content Protection System** (`app.content_protection`)
- **AI Processing Pipeline** (`app.ai`)
- **Business Logic Layer** (`app.business`)
- **API Gateway** (`app.api`)
- **Security Framework** (`app.security`)

---

## 📝 License & Contact

**Copyright © 2025 IA Influencer Agent - Fahed Mlaiel**
**All Rights Reserved**

**For licensing inquiries:** mlaiel@live.de
**Unauthorized use strictly prohibited**
