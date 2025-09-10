# Platform Integration Guide

## Overview

This guide provides comprehensive instructions for integrating the Ainflue Distribution Platform with various social media platforms, content management systems, and third-party services.

## Supported Platforms

### Tier 1 Platforms (Full Integration)
- **YouTube**: Complete API integration with advanced analytics
- **Instagram**: Instagram Graph API with Stories and Reels support
- **TikTok**: TikTok for Business API integration
- **Facebook**: Facebook Graph API with comprehensive posting
- **Twitter/X**: Twitter API v2 with enhanced features
- **LinkedIn**: LinkedIn Marketing API integration

### Tier 2 Platforms (Standard Integration)
- **Spotify**: Spotify Web API for music distribution
- **Apple Music**: Apple Music API integration
- **SoundCloud**: SoundCloud API for audio content
- **Bandcamp**: Direct integration for independent musicians
- **Twitch**: Twitch API for streaming content
- **Discord**: Discord Bot API for community management

### Tier 3 Platforms (Basic Integration)
- **Reddit**: Reddit API for community engagement
- **Medium**: Medium API for blog publishing
- **Substack**: Newsletter platform integration
- **OnlyFans**: Content subscription platform
- **Patreon**: Creator subscription management
- **Dailymotion**: Video hosting platform

## Integration Architecture

### API Authentication

All platform integrations use OAuth 2.0 for secure authentication:

```python
from distribution.platform_connectors import PlatformConnectorFactory

# Initialize connector
connector = PlatformConnectorFactory.create_connector(
    platform='youtube',
    credentials={
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'redirect_uri': 'your_redirect_uri'
    }
)

# Authenticate
auth_url = connector.get_authorization_url()
# Redirect user to auth_url, then get authorization code
access_token = connector.exchange_code_for_token(authorization_code)
```

### Content Publishing

Universal content publishing interface:

```python
from distribution.publication_scheduler import DistributionScheduler

scheduler = DistributionScheduler()

# Schedule content across multiple platforms
publication_request = {
    'content': {
        'title': 'My Amazing Content',
        'description': 'Check out this amazing content!',
        'media_urls': ['https://example.com/video.mp4'],
        'tags': ['music', 'entertainment']
    },
    'platforms': ['youtube', 'instagram', 'tiktok'],
    'schedule_time': '2025-01-15T18:00:00Z',
    'optimization_settings': {
        'auto_hashtags': True,
        'platform_specific_formatting': True,
        'optimal_timing': True
    }
}

result = await scheduler.schedule_publication(publication_request)
```

## Platform-Specific Setup

### YouTube Integration

1. **Create Google Cloud Project**:
   ```bash
   # Enable YouTube Data API v3
   gcloud services enable youtube.googleapis.com
   ```

2. **Configure OAuth Credentials**:
   ```python
   youtube_config = {
       'client_id': 'your_google_client_id',
       'client_secret': 'your_google_client_secret',
       'scopes': [
           'https://www.googleapis.com/auth/youtube.upload',
           'https://www.googleapis.com/auth/youtube'
       ]
   }
   ```

3. **Upload Video**:
   ```python
   from distribution.youtube_connector import YouTubeConnector
   
   youtube = YouTubeConnector(youtube_config)
   
   upload_result = await youtube.upload_video(
       video_path='/path/to/video.mp4',
       title='My Video Title',
       description='Video description with #hashtags',
       tags=['tag1', 'tag2'],
       category_id='22',  # People & Blogs
       privacy_status='public'
   )
   ```

### Instagram Integration

1. **Facebook App Configuration**:
   ```python
   instagram_config = {
       'app_id': 'your_facebook_app_id',
       'app_secret': 'your_facebook_app_secret',
       'instagram_business_account_id': 'your_instagram_business_id'
   }
   ```

2. **Post Content**:
   ```python
   from distribution.instagram_connector import InstagramConnector
   
   instagram = InstagramConnector(instagram_config)
   
   # Post photo
   photo_result = await instagram.post_photo(
       image_url='https://example.com/image.jpg',
       caption='Amazing photo! #photography #art'
   )
   
   # Post video/reel
   video_result = await instagram.post_reel(
       video_url='https://example.com/video.mp4',
       caption='Check out this reel! #reel #viral'
   )
   ```

### TikTok Integration

1. **TikTok for Business Setup**:
   ```python
   tiktok_config = {
       'app_id': 'your_tiktok_app_id',
       'app_secret': 'your_tiktok_app_secret',
       'redirect_uri': 'your_redirect_uri'
   }
   ```

2. **Upload Video**:
   ```python
   from distribution.tiktok_connector import TikTokConnector
   
   tiktok = TikTokConnector(tiktok_config)
   
   upload_result = await tiktok.upload_video(
       video_path='/path/to/video.mp4',
       caption='Viral TikTok content! #fyp #viral',
       privacy_level='PUBLIC'
   )
   ```

## Advanced Integration Features

### Multi-Platform Optimization

```python
from distribution.format_adapter import ContentFormatAdapter
from distribution.hashtag_optimizer import HashtagOptimizer

# Automatically adapt content for each platform
adapter = ContentFormatAdapter()
hashtag_optimizer = HashtagOptimizer()

original_content = {
    'title': 'My Content Title',
    'description': 'Long form description...',
    'media': '/path/to/media.mp4'
}

# Optimize for each platform
for platform in ['youtube', 'instagram', 'tiktok']:
    optimized_content = adapter.adapt_content(original_content, platform)
    optimized_hashtags = await hashtag_optimizer.optimize_hashtags(
        content=optimized_content,
        platform=platform,
        target_audience='general'
    )
    
    # Merge optimized hashtags
    optimized_content['hashtags'] = optimized_hashtags
```

### Analytics Integration

```python
from distribution.analytics_aggregator import AnalyticsAggregator

analytics = AnalyticsAggregator()

# Get cross-platform analytics
analytics_data = await analytics.get_unified_analytics(
    date_range={'start': '2025-01-01', 'end': '2025-01-31'},
    platforms=['youtube', 'instagram', 'tiktok'],
    metrics=['views', 'likes', 'shares', 'comments', 'engagement_rate']
)

print(f"Total views across platforms: {analytics_data['total_views']}")
print(f"Best performing platform: {analytics_data['top_platform']}")
```

## Error Handling and Retry Logic

```python
from distribution.platform_connectors import PlatformError, RateLimitError

async def robust_content_upload(content, platform):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = await platform.upload_content(content)
            return result
        
        except RateLimitError as e:
            # Wait and retry for rate limiting
            wait_time = e.retry_after or 60
            await asyncio.sleep(wait_time)
            retry_count += 1
        
        except PlatformError as e:
            if e.is_permanent_error():
                raise e
            else:
                # Temporary error, retry
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                retry_count += 1
    
    raise Exception(f"Failed to upload after {max_retries} retries")
```

## Webhook Configuration

### Setting up Webhooks

```python
from distribution.webhook_handler import WebhookHandler

webhook_handler = WebhookHandler()

# Configure platform webhooks
webhook_configs = {
    'youtube': {
        'events': ['video.published', 'video.analytics_updated'],
        'endpoint': 'https://your-domain.com/webhooks/youtube',
        'secret': 'your_webhook_secret'
    },
    'instagram': {
        'events': ['post.published', 'post.engagement_updated'],
        'endpoint': 'https://your-domain.com/webhooks/instagram',
        'secret': 'your_webhook_secret'
    }
}

# Register webhooks
for platform, config in webhook_configs.items():
    await webhook_handler.register_webhook(platform, config)
```

### Processing Webhook Events

```python
from fastapi import FastAPI, Request
from distribution.webhook_processor import WebhookProcessor

app = FastAPI()
processor = WebhookProcessor()

@app.post("/webhooks/{platform}")
async def handle_webhook(platform: str, request: Request):
    payload = await request.body()
    headers = dict(request.headers)
    
    # Verify webhook signature
    if not processor.verify_webhook_signature(platform, payload, headers):
        return {"error": "Invalid signature"}, 401
    
    # Process webhook event
    event = processor.parse_webhook_event(platform, payload)
    await processor.process_event(event)
    
    return {"status": "success"}
```

## Testing Integration

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from distribution.youtube_connector import YouTubeConnector

@pytest.fixture
def youtube_connector():
    config = {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret'
    }
    return YouTubeConnector(config)

@patch('distribution.youtube_connector.YouTube')
async def test_video_upload(mock_youtube, youtube_connector):
    # Mock API response
    mock_youtube.return_value.videos.return_value.insert.return_value.execute.return_value = {
        'id': 'test_video_id'
    }
    
    result = await youtube_connector.upload_video(
        video_path='/test/video.mp4',
        title='Test Video',
        description='Test Description'
    )
    
    assert result['video_id'] == 'test_video_id'
```

### Integration Testing

```python
async def test_end_to_end_publishing():
    """Test complete publishing workflow"""
    
    # Setup test content
    test_content = {
        'title': 'Integration Test Video',
        'description': 'Test description',
        'media_path': '/test/assets/video.mp4'
    }
    
    # Test multi-platform publishing
    scheduler = DistributionScheduler()
    
    result = await scheduler.publish_immediately(
        content=test_content,
        platforms=['youtube_sandbox', 'instagram_sandbox']
    )
    
    # Verify successful publishing
    assert result['youtube_sandbox']['status'] == 'success'
    assert result['instagram_sandbox']['status'] == 'success'
    
    # Verify content was adapted correctly
    assert 'video_id' in result['youtube_sandbox']
    assert 'media_id' in result['instagram_sandbox']
```

## Performance Optimization

### Connection Pooling

```python
from distribution.connection_pool import PlatformConnectionPool

# Configure connection pool
pool_config = {
    'max_connections_per_platform': 10,
    'connection_timeout': 30,
    'idle_timeout': 300,
    'retry_attempts': 3
}

connection_pool = PlatformConnectionPool(pool_config)

# Use pooled connections
async with connection_pool.get_connection('youtube') as conn:
    result = await conn.upload_video(video_data)
```

### Caching Strategy

```python
from distribution.cache_manager import CacheManager

cache = CacheManager()

# Cache platform metadata
@cache.cached(ttl=3600)  # Cache for 1 hour
async def get_platform_categories(platform: str):
    connector = PlatformConnectorFactory.create_connector(platform)
    return await connector.get_categories()

# Cache user profiles
@cache.cached(ttl=1800)  # Cache for 30 minutes
async def get_user_profile(platform: str, user_id: str):
    connector = PlatformConnectorFactory.create_connector(platform)
    return await connector.get_user_profile(user_id)
```

## Monitoring and Observability

### Health Checks

```python
from distribution.health_monitor import PlatformHealthMonitor

health_monitor = PlatformHealthMonitor()

# Check platform connectivity
health_status = await health_monitor.check_all_platforms()

for platform, status in health_status.items():
    if status['healthy']:
        print(f"{platform}: ✅ Healthy")
    else:
        print(f"{platform}: ❌ Issues: {status['issues']}")
```

### Metrics Collection

```python
from distribution.metrics_collector import MetricsCollector

metrics = MetricsCollector()

# Track API usage
await metrics.record_api_call(
    platform='youtube',
    endpoint='videos.insert',
    response_time=1.2,
    status_code=200
)

# Track publishing success rate
await metrics.record_publication_result(
    platform='instagram',
    success=True,
    content_type='image'
)
```

## Security Best Practices

### Credential Management

```python
from distribution.credential_vault import CredentialVault

vault = CredentialVault()

# Store credentials securely
await vault.store_credentials(
    platform='youtube',
    user_id='user123',
    credentials={
        'access_token': 'encrypted_access_token',
        'refresh_token': 'encrypted_refresh_token',
        'expires_at': '2025-12-31T23:59:59Z'
    }
)

# Retrieve and decrypt credentials
credentials = await vault.get_credentials('youtube', 'user123')
```

### Rate Limiting

```python
from distribution.rate_limiter import RateLimiter

rate_limiter = RateLimiter()

# Configure platform-specific rate limits
rate_limiter.configure_limits({
    'youtube': {'requests_per_minute': 100, 'uploads_per_day': 50},
    'instagram': {'requests_per_hour': 200, 'posts_per_day': 25},
    'tiktok': {'uploads_per_day': 10}
})

# Use rate limiter
async def safe_api_call(platform, api_function, *args, **kwargs):
    await rate_limiter.acquire(platform)
    try:
        return await api_function(*args, **kwargs)
    finally:
        rate_limiter.release(platform)
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Check credential expiration
   - Verify OAuth scopes
   - Confirm redirect URI configuration

2. **Upload Failures**:
   - Validate file format and size
   - Check platform-specific requirements
   - Verify content compliance

3. **Rate Limiting**:
   - Implement exponential backoff
   - Monitor API quota usage
   - Use batch operations when available

### Debug Mode

```python
import logging
from distribution import enable_debug_mode

# Enable debug logging
enable_debug_mode()
logging.getLogger('distribution').setLevel(logging.DEBUG)

# Detailed error information will be logged
```

## Support and Resources

- **Documentation**: [https://docs.ainflue.com](https://docs.ainflue.com)
- **API Reference**: [https://api.ainflue.com/docs](https://api.ainflue.com/docs)
- **Support**: [support@ainflue.com](mailto:support@ainflue.com)
- **Community**: [https://community.ainflue.com](https://community.ainflue.com)

---

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**