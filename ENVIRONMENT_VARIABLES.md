# 📋 Environment Variables Documentation - Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

This document provides comprehensive documentation for all environment variables required by the Ainflue Platform.

## 🚀 Quick Setup

Copy the appropriate environment file and customize:

```bash
# For development
cp .env.development .env

# For staging  
cp .env.staging .env

# For production
cp .env.production .env
```

## 📂 Core Application Variables

### Application Settings
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | `Ainflue` | ✅ |
| `APP_VERSION` | Application version | `1.0.0` | ✅ |
| `ENVIRONMENT` | Runtime environment | `development`, `staging`, `production` | ✅ |
| `DEBUG` | Enable debug mode | `true`, `false` | ✅ |
| `HOST` | Server host address | `0.0.0.0`, `127.0.0.1` | ✅ |
| `PORT` | Server port | `8000` | ✅ |
| `WORKERS` | Number of worker processes | `4` | ❌ |

### API Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `API_PREFIX` | API URL prefix | `/api/v1` | ❌ |
| `DOCS_URL` | Swagger docs URL | `/docs` (null for production) | ❌ |
| `REDOC_URL` | ReDoc URL | `/redoc` (null for production) | ❌ |

## 🗄️ Database Configuration

### PostgreSQL (Primary Database)
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` | ✅ |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | ✅ |
| `POSTGRES_USER` | Database username | `ainflue_prod` | ✅ |
| `POSTGRES_PASSWORD` | Database password | `secure_password_123` | ✅ |
| `POSTGRES_DB` | Database name | `ainflue_platform` | ✅ |

### Redis (Cache & Sessions)
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REDIS_HOST` | Redis host | `localhost` | ✅ |
| `REDIS_PORT` | Redis port | `6379` | ✅ |
| `REDIS_PASSWORD` | Redis password | `redis_password` | ❌ |
| `REDIS_DB` | Redis database number | `0` | ❌ |

### MongoDB (Documents & Metadata)
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `MONGODB_HOST` | MongoDB host | `localhost` | ❌ |
| `MONGODB_PORT` | MongoDB port | `27017` | ❌ |
| `MONGODB_USER` | MongoDB username | `ainflue_user` | ❌ |
| `MONGODB_PASSWORD` | MongoDB password | `mongo_password` | ❌ |
| `MONGODB_DB` | MongoDB database | `ainflue_documents` | ❌ |

## 🔐 Security Configuration

### JWT & Authentication
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET_KEY` | JWT signing key (256-bit) | `your_secure_jwt_key_here` | ✅ |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | ✅ |
| `JWT_ACCESS_TOKEN_EXPIRE` | Access token TTL (seconds) | `3600` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE` | Refresh token TTL (seconds) | `604800` | ❌ |

### Encryption & Hashing
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ENCRYPTION_KEY` | Data encryption key (256-bit) | `your_encryption_key_here` | ✅ |
| `PASSWORD_SALT` | Password hashing salt | `your_password_salt` | ❌ |

### OAuth2 Integration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `OAUTH2_GOOGLE_CLIENT_ID` | Google OAuth client ID | `123.apps.googleusercontent.com` | ❌ |
| `OAUTH2_GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `google_client_secret` | ❌ |
| `OAUTH2_GITHUB_CLIENT_ID` | GitHub OAuth client ID | `github_client_id` | ❌ |
| `OAUTH2_GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | `github_client_secret` | ❌ |

## 🌐 CORS Configuration

### Cross-Origin Resource Sharing
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://ainflue.com,https://app.ainflue.com` | ✅ |
| `CORS_METHODS` | Allowed HTTP methods | `GET,POST,PUT,DELETE,PATCH` | ✅ |

**Production CORS Example:**
```bash
CORS_ORIGINS=https://ainflue.com,https://www.ainflue.com,https://app.ainflue.com
CORS_METHODS=GET,POST,PUT,DELETE,PATCH
```

**Development CORS Example:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000
CORS_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
```

## 📊 Logging & Monitoring

### Logging Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` | ✅ |
| `LOG_FORMAT` | Log format | `text`, `json` | ✅ |

**Environment-specific logging:**
- **Development:** `LOG_LEVEL=DEBUG`, `LOG_FORMAT=text`
- **Staging:** `LOG_LEVEL=INFO`, `LOG_FORMAT=json`  
- **Production:** `LOG_LEVEL=INFO`, `LOG_FORMAT=json`

### Monitoring & Observability
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | `true`, `false` | ❌ |
| `PROMETHEUS_PORT` | Prometheus metrics port | `9090` | ❌ |
| `SENTRY_DSN` | Sentry error tracking DSN | `https://sentry.io/project_id` | ❌ |
| `SENTRY_ENVIRONMENT` | Sentry environment tag | `production` | ❌ |

## 🤖 AI & Machine Learning

### AI Service Configuration  
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `HUGGINGFACE_TOKEN` | HuggingFace API token | `hf_your_token_here` | ❌ |
| `OPENAI_API_KEY` | OpenAI API key | `sk-your_openai_key_here` | ❌ |

### Content Processing
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `MAX_FILE_SIZE_MB` | Max upload size (MB) | `500` | ❌ |
| `SUPPORTED_AUDIO_FORMATS` | Audio formats | `mp3,wav,flac,m4a` | ❌ |
| `SUPPORTED_VIDEO_FORMATS` | Video formats | `mp4,avi,mov,mkv` | ❌ |
| `SUPPORTED_IMAGE_FORMATS` | Image formats | `jpg,jpeg,png,gif` | ❌ |

### Vector Database
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FAISS_INDEX_PATH` | FAISS index storage path | `/app/data/faiss_indexes` | ❌ |
| `VECTOR_DIMENSION` | Vector dimensions | `768` | ❌ |
| `SIMILARITY_THRESHOLD` | Similarity threshold | `0.85` | ❌ |

## 🌐 Platform Integrations

### YouTube Integration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API key | `AIzaSy_your_api_key` | ❌ |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | `client_id.googleusercontent.com` | ❌ |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth secret | `youtube_client_secret` | ❌ |

### Social Media Platforms
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `INSTAGRAM_ACCESS_TOKEN` | Instagram API token | `IGQVJy_your_token` | ❌ |
| `TIKTOK_API_KEY` | TikTok API key | `your_tiktok_api_key` | ❌ |
| `SPOTIFY_CLIENT_ID` | Spotify client ID | `spotify_client_id` | ❌ |
| `TWITTER_API_KEY` | Twitter/X API key | `twitter_api_key` | ❌ |

## 💳 Payment Processing

### Stripe Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | `pk_live_...` (prod) / `pk_test_...` (dev) | ❌ |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` (prod) / `sk_test_...` (dev) | ❌ |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` | ❌ |

### PayPal Configuration  
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `PAYPAL_CLIENT_ID` | PayPal client ID | `paypal_client_id` | ❌ |
| `PAYPAL_CLIENT_SECRET` | PayPal client secret | `paypal_client_secret` | ❌ |
| `PAYPAL_ENVIRONMENT` | PayPal environment | `live`, `sandbox` | ❌ |

## ☁️ Cloud Storage

### AWS S3 Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA_your_access_key` | ❌ |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `your_aws_secret_key` | ❌ |
| `AWS_REGION` | AWS region | `eu-central-1` | ❌ |
| `AWS_S3_BUCKET` | S3 bucket name | `ainflue-content-prod` | ❌ |

### CDN & Storage
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CDN_BASE_URL` | CDN base URL | `https://cdn.ainflue.com` | ❌ |
| `LOCAL_STORAGE_PATH` | Local storage path | `./storage` | ❌ |

## ⚡ Performance & Scaling

### Connection Pooling & Timeouts
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DB_POOL_SIZE` | Database connection pool size | `20` | ❌ |
| `DB_MAX_OVERFLOW` | Max connection overflow | `0` | ❌ |
| `DB_POOL_TIMEOUT` | Pool timeout (seconds) | `30` | ❌ |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `30` | ❌ |
| `WORKER_TIMEOUT` | Worker timeout (seconds) | `120` | ❌ |

### Caching Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CACHE_TTL` | Cache TTL (seconds) | `3600` | ❌ |
| `CACHE_MAX_SIZE` | Max cache size | `1000` | ❌ |

### Rate Limiting
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `API_RATE_LIMIT` | Requests per window | `1000` | ❌ |
| `API_RATE_LIMIT_WINDOW` | Time window (seconds) | `3600` | ❌ |

## 🔒 Security Headers & Policies

### Security Headers
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FORCE_HTTPS` | Force HTTPS redirects | `true`, `false` | ❌ |
| `HSTS_MAX_AGE` | HSTS max age (seconds) | `31536000` | ❌ |
| `HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `true`, `false` | ❌ |

### Content Security Policy
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `CSP_DEFAULT_SRC` | CSP default source | `'self'` | ❌ |
| `CSP_SCRIPT_SRC` | CSP script sources | `'self' 'unsafe-inline'` | ❌ |

## 📧 Email & Notifications

### SMTP Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SMTP_HOST` | SMTP server host | `smtp.ainflue.com` | ❌ |
| `SMTP_PORT` | SMTP server port | `587` | ❌ |
| `SMTP_USERNAME` | SMTP username | `noreply@ainflue.com` | ❌ |
| `SMTP_PASSWORD` | SMTP password | `smtp_password` | ❌ |
| `SMTP_USE_TLS` | Use TLS encryption | `true`, `false` | ❌ |

### Email Settings
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FROM_EMAIL` | Default from email | `noreply@ainflue.com` | ❌ |
| `FROM_NAME` | Default from name | `Ainflue Platform` | ❌ |
| `ADMIN_EMAIL` | Admin contact email | `mlaiel@live.de` | ❌ |

## 🗂️ Backup & Disaster Recovery

### Backup Configuration
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `BACKUP_ENABLED` | Enable automatic backups | `true`, `false` | ❌ |
| `BACKUP_SCHEDULE` | Backup cron schedule | `0 2 * * *` | ❌ |
| `BACKUP_RETENTION_DAYS` | Backup retention (days) | `30` | ❌ |
| `BACKUP_S3_BUCKET` | Backup S3 bucket | `ainflue-backups-prod` | ❌ |

## ⚖️ Compliance & Legal

### GDPR & Data Protection
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GDPR_ENABLED` | Enable GDPR compliance | `true`, `false` | ❌ |
| `GDPR_RETENTION_DAYS` | Data retention period | `2555` (7 years) | ❌ |
| `AUDIT_LOG_ENABLED` | Enable audit logging | `true`, `false` | ❌ |
| `DATA_RETENTION_DAYS` | General data retention | `365` | ❌ |

## 🏗️ Feature Flags

### Core Features
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FEATURE_ADVANCED_ANALYTICS` | Advanced analytics | `true`, `false` | ❌ |
| `FEATURE_ML_PREDICTIONS` | ML predictions | `true`, `false` | ❌ |
| `FEATURE_REAL_TIME_MONITORING` | Real-time monitoring | `true`, `false` | ❌ |
| `FEATURE_MULTI_CURRENCY` | Multi-currency support | `true`, `false` | ❌ |

### Beta Features
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `BETA_VOICE_RECOGNITION` | Voice recognition beta | `true`, `false` | ❌ |
| `BETA_VIDEO_ANALYSIS` | Video analysis beta | `true`, `false` | ❌ |
| `BETA_BLOCKCHAIN_INTEGRATION` | Blockchain features | `true`, `false` | ❌ |

## 🛠️ Development Features

### Development Tools
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `AUTO_RELOAD` | Auto-reload on changes | `true`, `false` | ❌ |
| `MOCK_EXTERNAL_CALLS` | Mock external APIs | `true`, `false` | ❌ |
| `AUTO_MIGRATE` | Auto-run migrations | `true`, `false` | ❌ |
| `CREATE_SAMPLE_DATA` | Create sample data | `true`, `false` | ❌ |

## 🚨 Critical Security Notes

### Production Security Checklist

✅ **MUST DO for Production:**
- Replace all `CHANGE_ME_` values with secure, random keys
- Use external secret management (Kubernetes secrets, AWS Secrets Manager)
- Set `DEBUG=false` and `DOCS_URL=null` 
- Configure proper CORS origins (no wildcards)
- Use strong JWT and encryption keys (256-bit minimum)
- Enable HTTPS with proper SSL certificates
- Set up proper logging and monitoring

❌ **NEVER DO:**
- Commit `.env` files with real production values
- Use development keys in production
- Set `DEBUG=true` in production
- Allow wildcards in CORS origins for production
- Store secrets in code or config files

### Key Generation Commands

```bash
# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key  
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate password salt
python -c "import secrets; print(secrets.token_urlsafe(16))"

# Generate with OpenSSL
openssl rand -base64 32
```

## 📞 Support & Contact

**For production deployment assistance:**
- **Email:** mlaiel@live.de
- **Author:** Fahed Mlaiel
- **License:** All rights reserved

**Copyright Notice:**
© 2025 Fahed Mlaiel. All rights reserved. Unauthorized use, reproduction, or distribution prohibited.