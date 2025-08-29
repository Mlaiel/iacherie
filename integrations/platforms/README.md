# Platform APIs Integration Module

A complete, enterprise-grade platform integration system for managing multiple social media and content platforms with unified authentication, rate limiting, and API management.

## Overview

This module provides a centralized way to interact with major content platforms through their APIs, with features like:

- **Multi-platform OAuth 2.0 authentication**
- **Intelligent rate limiting and request management**
- **Cross-platform content synchronization**
- **Aggregated analytics and insights**
- **Copyright protection and DMCA services**
- **Comprehensive error handling and fallback strategies**

## Supported Platforms

| Platform | API Version | Features Supported |
|----------|-------------|-------------------|
| **YouTube** | v3 + Content ID | Video upload, analytics, Content ID management, monetization |
| **Instagram** | Business API | Posts, stories, insights, business account management |
| **TikTok** | Creator API | Video upload, creator analytics, trending insights |
| **Spotify** | Web API + Artists | Artist analytics, track data, playlists, following |
| **Facebook** | Graph API v18.0 | Rights management, copyright claims, page insights |
| **Twitter** | API v2 | Tweets, user management, analytics, engagement |

## Architecture

```
integrations/platforms/
├── __init__.py                    # Module exports
├── platform_coordinator.py       # Central orchestrator
├── platform_oauth_manager.py     # Multi-platform OAuth 2.0
├── api_rate_limiter.py           # Intelligent rate limiting
├── youtube_content_id_api.py     # YouTube Content ID API
├── instagram_business_api.py     # Instagram Business API
├── tiktok_creator_api.py         # TikTok Creator API
├── spotify_artists_api.py        # Spotify for Artists API
├── facebook_rights_api.py        # Facebook Rights Manager API
├── twitter_api_v2.py             # Twitter API v2
└── dmca_services_api.py          # DMCA protection services
```

## Quick Start

### 1. Basic Setup

```python
import asyncio
from integrations.platforms import PlatformCoordinator

async def main():
    async with PlatformCoordinator() as coordinator:
        # Configure OAuth for YouTube
        coordinator.configure_platform_oauth(
            platform="youtube",
            client_id="your_client_id",
            client_secret="your_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        
        # Generate authentication URL
        auth_url = await coordinator.initiate_platform_auth("youtube", "user123")
        print(f"Authenticate at: {auth_url}")

asyncio.run(main())
```

### 2. Complete Authentication Flow

```python
async def authenticate_user(coordinator, platform, user_id):
    # Step 1: Generate auth URL
    auth_url = await coordinator.initiate_platform_auth(platform, user_id)
    
    # Step 2: User visits auth_url and authorizes
    # Step 3: Platform redirects with authorization code
    authorization_code = "code_from_callback"
    state = "state_from_callback"
    
    # Step 4: Complete authentication
    success = await coordinator.complete_platform_auth(
        platform, user_id, authorization_code, state
    )
    
    if success:
        print(f"✅ {platform} authentication successful")
    else:
        print(f"❌ {platform} authentication failed")
```

### 3. Cross-Platform Content Sync

```python
async def sync_content_example(coordinator, user_id):
    # Sync content across multiple platforms
    results = await coordinator.sync_content_across_platforms(
        user_id=user_id,
        content_title="My Amazing Content",
        content_description="Check out this amazing content!",
        content_file_path="/path/to/video.mp4",
        platforms=["youtube", "tiktok"],
        platform_specific_data={
            "youtube": {
                "tags": ["music", "entertainment"],
                "category_id": "10"
            },
            "tiktok": {
                "privacy_level": "PUBLIC_TO_EVERYONE"
            }
        }
    )
    
    for platform, result in results.items():
        if result["success"]:
            print(f"✅ {platform}: {result['content_id']}")
        else:
            print(f"❌ {platform}: {result['error']}")
```

### 4. Aggregated Analytics

```python
async def get_analytics_example(coordinator, user_id):
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    analytics = await coordinator.get_aggregated_analytics(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        platforms=["youtube", "instagram", "tiktok"]
    )
    
    print(f"Total views: {analytics.total_views:,}")
    print(f"Total engagement: {analytics.total_engagement:,}")
    print(f"Total followers: {analytics.total_followers:,}")
    print(f"Total revenue: ${analytics.total_revenue:.2f}")
```

### 5. Content Protection

```python
async def setup_content_protection(coordinator, user_id):
    # Monitor for copyright infringement
    monitor_id = await coordinator.monitor_content_protection(
        user_id=user_id,
        content_title="My Original Song",
        content_type="audio",
        keywords=["my original song", "artist name"]
    )
    
    # Handle infringement
    takedown_id = await coordinator.handle_copyright_infringement(
        user_id=user_id,
        infringing_url="https://example.com/stolen-content",
        original_content_url="https://mysite.com/original",
        description="Unauthorized use of my copyrighted content"
    )
    
    print(f"Monitor ID: {monitor_id}")
    print(f"Takedown ID: {takedown_id}")
```

## Platform-Specific Usage

### YouTube Content ID API

```python
from integrations.platforms import YouTubeContentIDAPI

async with YouTubeContentIDAPI() as youtube:
    # Upload video
    video = await youtube.upload_video(
        tokens, "/path/to/video.mp4", "Title", "Description"
    )
    
    # Get analytics
    analytics = await youtube.get_analytics(
        tokens, channel_id, start_date, end_date
    )
    
    # Create Content ID claim
    claim = await youtube.create_content_claim(
        tokens, video_id, asset_id, "audiovisual", "monetize"
    )
```

### Instagram Business API

```python
from integrations.platforms import InstagramBusinessAPI

async with InstagramBusinessAPI() as instagram:
    # Get account info
    user = await instagram.get_user_info(tokens)
    
    # Create and publish post
    container_id = await instagram.create_media_container(
        tokens, "me", "IMAGE", "https://example.com/image.jpg", "Caption"
    )
    media_id = await instagram.publish_media(tokens, "me", container_id)
    
    # Get insights
    insights = await instagram.get_media_insights(tokens, media_id)
```

### TikTok Creator API

```python
from integrations.platforms import TikTokCreatorAPI

async with TikTokCreatorAPI() as tiktok:
    # Upload video
    video_id = await tiktok.upload_video(
        tokens, "/path/to/video.mp4", "Title", "Description"
    )
    
    # Get creator insights
    analytics = await tiktok.get_creator_insights(tokens, date_range=7)
    
    # Search trending hashtags
    hashtags = await tiktok.get_trending_hashtags(tokens, "US", 20)
```

### Spotify Artists API

```python
from integrations.platforms import SpotifyArtistsAPI

async with SpotifyArtistsAPI() as spotify:
    # Get artist info
    artist = await spotify.get_artist_info(tokens, artist_id)
    
    # Get top tracks
    tracks = await spotify.get_artist_top_tracks(tokens, artist_id)
    
    # Get recommendations
    recommendations = await spotify.get_recommendations(
        tokens, seed_artists=[artist_id], limit=20
    )
```

## Configuration

### Environment Variables

```bash
# OAuth Configuration
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret

TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret

# DMCA Services
DMCA_API_KEY=your_dmca_service_api_key

# Redis (optional, for distributed rate limiting)
REDIS_URL=redis://localhost:6379/0
```

### Rate Limits

The module includes intelligent rate limiting for each platform:

| Platform | Default Limits | Endpoints |
|----------|---------------|-----------|
| YouTube | 10,000/day, 100/hour for search | Videos, Analytics, Search |
| Instagram | 200/hour | Media, Insights |
| TikTok | 1,000/day, 100/hour | Videos, Analytics |
| Spotify | 1,000/hour, 100/minute for artists | Search, Artists, Tracks |
| Facebook | 600/hour | Pages, Rights |
| Twitter | 300/15min | Tweets, Users |

## Error Handling

The module provides comprehensive error handling with:

- **Automatic retry with exponential backoff**
- **Rate limit detection and waiting**
- **Token refresh for expired credentials**
- **Fallback strategies for failed requests**
- **Detailed error logging and reporting**

```python
try:
    result = await coordinator.sync_content_across_platforms(...)
except Exception as e:
    logger.error(f"Content sync failed: {e}")
    # Handle specific error types
    if "rate_limit" in str(e).lower():
        # Wait and retry
        await asyncio.sleep(60)
        result = await coordinator.sync_content_across_platforms(...)
```

## Security Features

- **Secure token encryption using Fernet**
- **CSRF protection for OAuth flows**
- **Secure credential storage**
- **Request signing and validation**
- **SSL/TLS enforcement for all API calls**

## Performance Optimization

- **Asynchronous operations for all API calls**
- **Connection pooling for HTTP requests**
- **Intelligent caching strategies**
- **Batch operations where supported**
- **Memory-efficient data structures**

## Testing

Run the test suite:

```bash
cd /path/to/Ainflue
python -m pytest tests/test_platform_integrations.py -v
```

Run the example:

```bash
python examples/platform_integration_example.py
```

## Contributing

When adding new platform integrations:

1. Create a new API class in `integrations/platforms/`
2. Follow the existing patterns for OAuth and rate limiting
3. Add comprehensive error handling
4. Include proper type hints and documentation
5. Add tests for the new integration
6. Update this README with platform details

## License

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

## Support

For support and questions:
- Email: mlaiel@live.de
- Documentation: https://docs.ainflue.com/integrations
- Issues: https://github.com/Mlaiel/Ainflue/issues