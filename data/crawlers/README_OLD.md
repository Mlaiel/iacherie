# Crawlers Module - Professional Web Crawling System

## Overview

Industrial-grade multi-platform content monitoring and surveillance system implementing advanced crawling capabilities for copyright protection and content discovery across social media platforms and web domains.

## Team Expertise

This module has been developed by a world-class team combining all expertise domains:

- **Lead Dev IA** - AI Architecture & Machine Learning Integration
- **Backend Senior** - Advanced Python Development & System Architecture  
- **ML Engineer** - Content Fingerprinting & Similarity Algorithms
- **DBA** - Database Optimization & Data Management
- **Security Engineer** - Platform Security & Anti-Detection Systems
- **Microservices Architect** - Distributed Systems & Scalability
- **Audio Engineer** - Audio Content Processing & Analysis
- **DevOps Engineer** - Infrastructure & Deployment Automation
- **IA Prompt Engineer** - AI Model Fine-tuning & Optimization

**Project Lead & Creator:** Fahed Mlaiel  
**Contact:** mlaiel@live.de

## ⚠️ CRITICAL LEGAL WARNING ⚠️

**THIS CODE IS PROPRIETARY AND CONFIDENTIAL INTELLECTUAL PROPERTY**

Any unauthorized use, reproduction, distribution, copying, reverse engineering, or theft of this concept, code, methodology, or intellectual property is **STRICTLY PROHIBITED** and will result in immediate legal action.

**VIOLATIONS WILL BE PROSECUTED TO THE FULL EXTENT OF THE LAW** under German and International Copyright Laws.

**For licensing inquiries contact:** mlaiel@live.de

## Features

### 🎯 Multi-Platform Coverage
- **YouTube** - Complete API integration with quota management
- **Instagram** - Advanced scraping with anti-detection measures  
- **TikTok** - Mobile simulation and content extraction
- **Generic Web** - Comprehensive domain crawling with robots.txt compliance

### 🚀 Advanced Capabilities
- **Real-time Content Monitoring** - Continuous surveillance with alerts
- **AI-Powered Similarity Detection** - Vector-based content matching
- **Intelligent Rate Limiting** - Platform-specific throttling
- **Anti-Detection Systems** - Human-like browsing patterns
- **Scalable Architecture** - Concurrent multi-platform crawling
- **Comprehensive Logging** - Full audit trail and monitoring

### 🛡️ Security & Compliance
- **Robots.txt Compliance** - Respects platform guidelines
- **User-Agent Rotation** - Advanced anti-fingerprinting
- **Session Management** - Proper connection handling
- **Error Recovery** - Automatic retry mechanisms

## Architecture

```
Crawler Manager
├── Platform Crawlers
│   ├── YouTube Crawler (API-based)
│   ├── Instagram Crawler (Hybrid API/Scraping)
│   ├── TikTok Crawler (Advanced Scraping)
│   └── Generic Web Crawler (Domain Crawling)
├── Task Scheduling System
├── Vector Matching Engine
├── Anti-Detection Framework
└── Real-time Monitoring & Alerts
```

## Core Components

### PlatformCrawler (Base Class)
Abstract base class providing common functionality:
- Content search and extraction
- Metadata parsing
- Similarity calculation
- Rate limiting
- Error handling

### YouTubeCrawler
Professional YouTube content monitoring:
- YouTube Data API v3 integration
- Video metadata extraction
- Channel monitoring
- Comment analysis
- Quota management

### InstagramCrawler
Advanced Instagram content detection:
- Graph API integration
- Selenium-based scraping
- Hashtag monitoring
- Story and Reel detection
- Anti-detection measures

### TikTokCrawler
Sophisticated TikTok monitoring:
- Mobile browser simulation
- Advanced anti-detection
- Hashtag and user monitoring
- Video extraction
- Trend analysis

### GenericWebCrawler
Comprehensive web domain crawling:
- Multi-domain support
- Depth-limited crawling
- Content type filtering
- Media file discovery
- Structured data extraction

### CrawlerManager
Orchestration and management system:
- Task scheduling and prioritization
- Concurrent execution management
- Result aggregation
- Performance monitoring
- Event-driven notifications

## Usage Examples

### Basic Multi-Platform Search
```python
from backend.data.crawlers import CrawlerManager, CrawlerConfig

# Initialize crawler manager
manager = CrawlerManager(vector_matcher, max_concurrent_crawlers=5)

# Configure platforms
manager.register_crawler_config('youtube', {
    'api_key': 'your_youtube_api_key',
    'rate_limit_delay': 1.0
})

# Search across platforms
results = await manager.search_across_platforms(
    fingerprint_data={
        'search_terms': ['music track', 'artist name'],
        'title': 'Original Song Title',
        'artist': 'Artist Name'
    },
    platforms=['youtube', 'instagram', 'tiktok']
)
```

### Continuous Monitoring
```python
# Create monitoring task
task_id = await manager.create_crawler_task(
    crawler_type='youtube',
    fingerprint_data=fingerprint_data,
    search_config={
        'search_terms': ['copyrighted content'],
        'similarity_threshold': 0.85,
        'max_results': 100
    },
    schedule_config={
        'type': 'interval',
        'interval_minutes': 60
    },
    priority=CrawlerPriority.HIGH,
    callback_url='https://your-app.com/webhook'
)
```

### Platform-Specific Crawling
```python
from backend.data.crawlers import YouTubeCrawler

# YouTube-specific operations
youtube_crawler = YouTubeCrawler(config, vector_matcher, api_key)

# Search videos
videos = await youtube_crawler.search_content(['music'], max_results=50)

# Get video metadata
metadata = await youtube_crawler.extract_content_metadata(video_url)

# Monitor channel
channel_videos = await youtube_crawler.search_videos_by_channel(channel_id)
```

## Configuration

### Crawler Configuration
```python
config = CrawlerConfig(
    platform_name='youtube',
    search_terms=['keyword1', 'keyword2'],
    similarity_threshold=0.8,
    max_results_per_search=100,
    crawl_interval_minutes=60,
    respect_robots_txt=True,
    rate_limit_delay=1.0,
    user_agent='IA-Influencer-Agent/1.0',
    timeout_seconds=30,
    retry_attempts=3
)
```

### Platform-Specific Settings
```python
# YouTube
youtube_config = {
    'api_key': 'your_api_key',
    'quota_limit': 10000,
    'rate_limit_delay': 1.0
}

# Instagram  
instagram_config = {
    'access_token': 'your_access_token',
    'app_secret': 'your_app_secret',
    'rate_limit_delay': 2.0
}

# TikTok
tiktok_config = {
    'rate_limit_delay': (3.0, 7.0),  # Random delay range
    'max_videos_per_user': 50
}
```

## Monitoring & Metrics

### Real-time Metrics
```python
# Get current metrics
metrics = manager.get_metrics()
print(f"Active crawlers: {metrics['active_crawlers']}")
print(f"Success rate: {metrics['success_rate']}%")
print(f"Total matches found: {metrics['total_matches_found']}")
```

### Task Status Monitoring
```python
# Check task status
status = await manager.get_task_status(task_id)
print(f"Task status: {status['is_running']}")

# Get all tasks
all_tasks = await manager.get_all_tasks_status()
```

## Error Handling & Recovery

The system implements comprehensive error handling:
- **Automatic Retry** - Failed tasks are automatically retried
- **Graceful Degradation** - Partial failures don't stop other crawlers
- **Circuit Breaker** - Protection against repeated failures
- **Detailed Logging** - Full error tracking and analysis

## Performance Optimization

### Concurrent Execution
- Configurable maximum concurrent crawlers
- Priority-based task scheduling
- Resource-aware load balancing

### Rate Limiting
- Platform-specific rate limiting
- Adaptive delay mechanisms
- Quota management for API-based crawlers

### Caching & Efficiency
- Duplicate URL detection
- Robots.txt caching
- Session reuse
- Optimized data extraction

## Security Considerations

### Anti-Detection
- User-agent rotation
- Randomized delays
- Session management
- Browser fingerprint masking

### Compliance
- Robots.txt compliance
- Platform terms of service adherence
- Data protection compliance
- Ethical crawling practices

## Dependencies

### Core Dependencies
```
aiohttp>=3.8.0
selenium>=4.0.0
beautifulsoup4>=4.10.0
scrapy>=2.6.0
google-api-python-client>=2.0.0
```

### System Requirements
- Python 3.9+
- Chrome/Chromium browser
- Adequate RAM for concurrent operations
- Stable internet connection

## Deployment

### Docker Support
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y chromium-browser
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "-m", "crawler_service"]
```

### Environment Variables
```bash
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
MAX_CONCURRENT_CRAWLERS=5
RATE_LIMIT_DELAY=1.0
```

## Support & Licensing

For technical support, feature requests, or licensing inquiries, please contact:

**Fahed Mlaiel**  
Email: mlaiel@live.de

---

**© 2025 Fahed Mlaiel - All Rights Reserved**

This module is part of the IA-Influencer-Agent platform - a comprehensive AI-powered content protection and monetization system for digital creators.
