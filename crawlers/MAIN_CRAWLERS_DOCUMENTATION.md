# 🕷️ Main Platform Crawlers Documentation

## Overview

This document describes the implementation of the 10 main platform crawlers for the Ainflue content protection system. Each crawler provides specialized functionality for monitoring and collecting content from major social media and content platforms.

## Supported Platforms

### 1. YouTube Crawler
- **API**: YouTube Data API v3
- **Features**: Copyright monitoring, video search, channel monitoring
- **Rate Limit**: 100 requests per window
- **Key Methods**:
  - `search_content(query, max_results)`: Search for videos
  - `get_content_details(video_id)`: Get detailed video information
  - `monitor_copyright_violations(protected_content, callback)`: Monitor for copyright violations

### 2. Instagram Crawler
- **API**: Instagram Graph API
- **Features**: Story monitoring, hashtag tracking, post analysis
- **Rate Limit**: 200 requests per hour
- **Key Methods**:
  - `search_content(hashtag, max_results)`: Search by hashtag
  - `get_content_details(post_id)`: Get post details
  - `monitor_stories(user_ids, callback)`: Monitor user stories

### 3. TikTok Crawler
- **API**: Unofficial API + automated browsing
- **Features**: Video discovery, trend analysis, user monitoring
- **Rate Limit**: 100 requests per window
- **Key Methods**:
  - `search_content(query, max_results)`: Search for videos
  - `get_content_details(video_id)`: Get video details

### 4. Twitter/X Crawler
- **API**: Twitter API v2
- **Features**: Real-time stream monitoring, tweet search, trend analysis
- **Rate Limit**: 300 requests per 15 minutes
- **Key Methods**:
  - `search_content(query, max_results)`: Search tweets
  - `get_content_details(tweet_id)`: Get tweet details
  - `monitor_real_time_stream(keywords, callback)`: Real-time monitoring

### 5. Facebook Crawler
- **API**: Facebook Graph API
- **Features**: Page monitoring, post tracking, engagement analysis
- **Rate Limit**: 200 requests per hour
- **Key Methods**:
  - `search_content(query, max_results)`: Search posts
  - `get_content_details(post_id)`: Get post details
  - `monitor_pages(page_ids, callback)`: Monitor Facebook pages

### 6. LinkedIn Crawler
- **API**: LinkedIn Marketing API
- **Features**: Company page monitoring, professional content tracking
- **Rate Limit**: 500 requests per hour
- **Key Methods**:
  - `search_content(query, max_results)`: Search posts
  - `get_content_details(post_id)`: Get post details
  - `monitor_companies(company_ids, callback)`: Monitor company pages

### 7. Pinterest Crawler
- **API**: Pinterest API
- **Features**: Board tracking, pin monitoring, trend analysis
- **Rate Limit**: 1000 requests per hour
- **Key Methods**:
  - `search_content(query, max_results)`: Search pins
  - `get_content_details(pin_id)`: Get pin details
  - `monitor_boards(board_ids, callback)`: Monitor Pinterest boards

### 8. Snapchat Crawler
- **API**: Snap Kit
- **Features**: Story monitoring, content discovery
- **Rate Limit**: 500 requests per hour
- **Key Methods**:
  - `search_content(query, max_results)`: Search content
  - `get_content_details(content_id)`: Get content details
  - `monitor_stories(user_ids, callback)`: Monitor Snapchat stories

### 9. Discord Crawler
- **API**: Discord Bot API
- **Features**: Server monitoring, message tracking, channel analysis
- **Rate Limit**: 50 requests per window
- **Key Methods**:
  - `search_content(query, max_results)`: Search messages
  - `get_content_details(message_id)`: Get message details
  - `monitor_servers(server_ids, callback)`: Monitor Discord servers

### 10. Telegram Crawler
- **API**: Telegram Bot API
- **Features**: Channel monitoring, message tracking, group analysis
- **Rate Limit**: 30 requests per window
- **Key Methods**:
  - `search_content(query, max_results)`: Search messages
  - `get_content_details(message_id)`: Get message details
  - `monitor_channels(channel_ids, callback)`: Monitor Telegram channels

## Usage Examples

### Basic Search Across All Platforms

```python
import asyncio
from crawlers.main_platform_crawlers import CrawlerOrchestrator

async def search_all_platforms():
    orchestrator = CrawlerOrchestrator()
    
    # Search across all platforms
    results = await orchestrator.search_all_platforms("my content", max_results=10)
    
    for platform, platform_results in results.items():
        print(f"{platform}: {len(platform_results)} results found")
        for result in platform_results:
            print(f"  - {result.title}")
            print(f"    URL: {result.url}")

# Run the search
asyncio.run(search_all_platforms())
```

### YouTube Copyright Monitoring

```python
import asyncio
from crawlers.main_platform_crawlers import YouTubeCrawler

async def monitor_copyright():
    # Initialize with API key
    youtube = YouTubeCrawler(api_key="YOUR_YOUTUBE_API_KEY")
    
    async def violation_callback(violation):
        print(f"🚨 Copyright violation detected!")
        print(f"Platform: {violation['platform']}")
        print(f"Content: {violation['content'].title}")
        print(f"Similarity: {violation['similarity_score']:.2%}")
    
    # Monitor for copyright violations
    protected_content = ["my song title", "my video title"]
    await youtube.monitor_copyright_violations(protected_content, violation_callback)

# Run monitoring
asyncio.run(monitor_copyright())
```

### Instagram Story Monitoring

```python
import asyncio
from crawlers.main_platform_crawlers import InstagramCrawler

async def monitor_stories():
    # Initialize with access token
    instagram = InstagramCrawler(access_token="YOUR_INSTAGRAM_TOKEN")
    
    async def story_callback(update):
        print(f"📸 New story from {update['user_id']}")
        print(f"Stories count: {len(update['stories'])}")
    
    # Monitor specific users
    user_ids = ["user1", "user2", "user3"]
    await instagram.monitor_stories(user_ids, story_callback)

# Run monitoring
asyncio.run(monitor_stories())
```

### Twitter Real-Time Stream

```python
import asyncio
from crawlers.main_platform_crawlers import TwitterCrawler

async def monitor_twitter():
    # Initialize with bearer token
    twitter = TwitterCrawler(bearer_token="YOUR_TWITTER_BEARER_TOKEN")
    
    async def stream_callback(update):
        print(f"🐦 Real-time update for '{update['keyword']}'")
        for result in update['results']:
            print(f"  - {result.title}")
    
    # Monitor keywords in real-time
    keywords = ["my brand", "my product"]
    await twitter.monitor_real_time_stream(keywords, stream_callback)

# Run monitoring
asyncio.run(monitor_twitter())
```

### Individual Platform Usage

```python
import asyncio
from crawlers.main_platform_crawlers import CrawlerOrchestrator

async def use_individual_crawler():
    orchestrator = CrawlerOrchestrator()
    
    # Get specific crawler
    youtube = await orchestrator.get_crawler('youtube')
    
    # Search for content
    results = await youtube.search_content("music video", max_results=5)
    
    for result in results:
        print(f"Video: {result.title}")
        print(f"Author: {result.author}")
        print(f"URL: {result.url}")
        
        # Get detailed information
        details = await youtube.get_content_details(result.content_id)
        if details:
            print(f"Detailed info: {details.metadata}")

# Run individual crawler
asyncio.run(use_individual_crawler())
```

## Configuration

### Environment Variables

Set up the following environment variables for API access:

```bash
# YouTube
export YOUTUBE_API_KEY="your_youtube_api_key"

# Instagram
export INSTAGRAM_ACCESS_TOKEN="your_instagram_token"
export INSTAGRAM_USER_ID="your_instagram_user_id"

# Twitter
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"

# Facebook
export FACEBOOK_ACCESS_TOKEN="your_facebook_token"

# LinkedIn
export LINKEDIN_ACCESS_TOKEN="your_linkedin_token"

# Pinterest
export PINTEREST_ACCESS_TOKEN="your_pinterest_token"

# Snapchat
export SNAPCHAT_ACCESS_TOKEN="your_snapchat_token"

# Discord
export DISCORD_BOT_TOKEN="your_discord_bot_token"

# Telegram
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
```

### Rate Limiting

Each crawler implements intelligent rate limiting:

- **YouTube**: 100 requests per window
- **Instagram**: 200 requests per hour
- **TikTok**: 100 requests per window
- **Twitter**: 300 requests per 15 minutes
- **Facebook**: 200 requests per hour
- **LinkedIn**: 500 requests per hour
- **Pinterest**: 1000 requests per hour
- **Snapchat**: 500 requests per hour
- **Discord**: 50 requests per window
- **Telegram**: 30 requests per window

## Data Structures

### CrawlerResult

All crawlers return standardized `CrawlerResult` objects:

```python
@dataclass
class CrawlerResult:
    platform: str           # Platform name (e.g., "youtube")
    content_id: str         # Unique content identifier
    content_type: str       # Type of content (video, image, post, etc.)
    title: str              # Content title
    description: str        # Content description
    url: str                # Direct URL to content
    author: str             # Content author/creator
    timestamp: float        # Discovery timestamp
    metadata: Dict[str, Any] # Platform-specific metadata
    raw_data: Dict[str, Any] # Raw platform data
```

## Error Handling

All crawlers implement robust error handling:

- Automatic retry on transient failures
- Rate limit respect and backoff
- Graceful degradation when APIs are unavailable
- Comprehensive logging for debugging

## Architecture

The crawler system is built with:

- **Modular Design**: Each platform is a separate crawler
- **Async/Await**: High-performance asynchronous operations
- **Rate Limiting**: Intelligent per-platform rate limiting
- **Standardized Interface**: Common methods across all crawlers
- **Minimal Dependencies**: Core Python libraries only
- **Extensible**: Easy to add new platforms

## Testing

Run the test suite to verify all crawlers work correctly:

```bash
cd /path/to/ainflue
python test_main_crawlers_direct.py
```

Expected output:
```
🕷️ Testing Main Platform Crawlers
==================================================
✅ Supported platforms: youtube, instagram, tiktok, twitter, facebook, linkedin, pinterest, snapchat, discord, telegram

🔍 Searching for 'test content' across all platforms...
...
✅ All tests completed successfully!
```

## Next Steps

1. **API Setup**: Configure real API credentials for each platform
2. **Enhanced Features**: Add advanced filtering and search capabilities
3. **Storage Integration**: Connect to database for persistent storage
4. **Monitoring Dashboard**: Build web interface for monitoring
5. **Alert System**: Implement notification system for violations
6. **Machine Learning**: Add AI-powered content analysis
7. **Scalability**: Implement distributed crawling architecture

For more information, see the individual crawler implementations in `crawlers/main_platform_crawlers.py`.