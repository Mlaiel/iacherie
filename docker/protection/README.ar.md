# خدمات Docker Protection

خدمات Docker احترافية لوظائف protection في منصة Ainflue.

## نظرة عامة

توفر هذه الوحدة خدمات protection المحاطة بحاويات مصممة للنشر على نطاق المؤسسات.

## البنية المعمارية

- **بناءات متعددة المراحل**: محسن للإنتاج
- **أمان مقوى**: مستخدم غير جذر، سطح هجوم أدنى
- **فحوصات الصحة**: مراقبة شاملة
- **محسن الموارد**: استخدام فعال للذاكرة ووحدة المعالجة المركزية

## الاستخدام

```bash
# بناء الخدمات
docker compose build

# بدء الخدمات
docker compose up -d

# عرض السجلات
docker compose logs -f
```

## Services Included

Multiple specialized Docker services for protection operations.

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Minimum 2GB RAM
- 10GB disk space

## Configuration

Configure environment variables in `.env` file:

```env
# PROTECTION_CONFIG
PROTECTION_LOG_LEVEL=INFO
PROTECTION_PORT=8080
```

## Health Monitoring

All services include comprehensive health checks:

- **Startup**: 30s initial delay
- **Interval**: 30s check frequency  
- **Timeout**: 10s response timeout
- **Retries**: 3 attempts before unhealthy

## Security

- Non-root container execution
- Minimal base images (distroless when possible)
- Regular security scanning
- Network isolation
- Secret management

## Performance

- Multi-stage builds for minimal image size
- Resource limits and reservations
- Horizontal scaling ready
- Optimized caching layers

## Support

For technical support, contact:
- **Author**: Fahed Mlaiel
- **Email**: mlaiel@live.de
- **Platform**: Ainflue Enterprise

## حقوق الطبع والنشر

© 2025 فهد ملائيل (mlaiel@live.de). جميع الحقوق محفوظة.
