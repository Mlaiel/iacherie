# Crawler Utils Module

***⚠️ COPYRIGHT WARNING - UNAUTHORIZED USE STRICTLY PROHIBITED**

**ALL RIGHTS RESERVED - FAHED MLAIEL**

This code is the intellectual property of **Fahed Mlaiel** (mlaiel@live.de). Any unauthorized copying, distribution, modification, or use of this code without explicit written permission is strictly prohibited and will result in immediate legal action under copyright law.

**🚨 STRONG WARNING TO THIEVES AND CONCEPT PLAGIARISTS 🚨**

Anyone who thinks of stealing this idea, concept, or code without my personal authorization clearly written from Fahed Mlaiel (mlaiel@live.de) will face severe legal consequences. This is protected intellectual property developed over thousands of hours of expert work.

**Contact for licensing:** mlaiel@live.deessional web crawling utilities for IA-Influencer-Agent**

## Overview

This module provides enterprise-grade utilities for web crawling operations, including intelligent rate limiting, content extraction, URL validation, cookie management, and CAPTCHA solving capabilities.

## Project Team

**Lead Developer & AI Architect:** Fahed Mlaiel (mlaiel@live.de)

**Expert Team Specialties:**
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization

## ⚠️ COPYRIGHT WARNING

**ALL RIGHTS RESERVED - UNAUTHORIZED USE STRICTLY PROHIBITED**

This code is the intellectual property of **Fahed Mlaiel** (mlaiel@live.de). Any unauthorized copying, distribution, modification, or use of this code without explicit written permission is strictly prohibited and will result in immediate legal action under copyright law.

**Contact for licensing:** mlaiel@live.de

## Features

### 🎯 Core Utilities

- **Rate Limiter**: Intelligent rate limiting with platform-specific configurations
- **Content Extractor**: AI-powered content analysis and extraction
- **URL Validator**: Comprehensive URL validation and security assessment
- **Cookie Manager**: Professional cookie handling with encryption
- **CAPTCHA Solver**: Multi-strategy CAPTCHA solving capabilities
- **Proxy Manager**: Advanced proxy rotation and management
- **User Agent Rotator**: Intelligent user agent rotation
- **Session Manager**: Persistent session management

### 🆕 Advanced Security & Surveillance

- **Content Fingerprinting**: Multi-modal fingerprinting (audio, video, image, text)
- **Surveillance Engine**: Real-time content monitoring and threat detection
- **Security Scanner**: Advanced URL and content security assessment
- **Content Encryption**: Enterprise-grade encryption with multiple algorithms
- **Access Control**: API key management and rate limiting
- **Performance Monitor**: Comprehensive performance tracking and optimization

### 🔧 Performance & Optimization

- **Advanced Cache**: Multi-strategy caching with Redis support
- **Connection Pool**: Optimized HTTP connection management
- **Resource Optimizer**: Memory and CPU optimization utilities
- **Performance Monitor**: Real-time metrics and reporting

### 🔧 Advanced Features

- **Multi-platform Support**: YouTube, Instagram, TikTok, Twitter, Facebook, Spotify
- **AI Content Analysis**: Sentiment analysis, topic classification, entity extraction
- **Security Features**: Malicious URL detection, content fingerprinting
- **Performance Optimization**: Distributed rate limiting with Redis
- **Content Quality Assessment**: Readability scoring, quality metrics
- **Multimedia Extraction**: Images, videos, audio, documents
- **Structured Data**: JSON-LD, Microdata, RDFa extraction

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# Install optional dependencies for advanced features
pip install opencv-python pytesseract nltk textstat langdetect
```

## Quick Start

### Rate Limiting

```python
from backend.crawlers.utils import create_rate_limiter

# Create platform-specific rate limiter
youtube_limiter = create_rate_limiter('youtube')

# Use in async context
await youtube_limiter.wait_if_needed()
# Make your request here
await youtube_limiter.update_usage()
```

### Content Extraction

```python
from backend.crawlers.utils import ContentExtractor

extractor = ContentExtractor()

# Extract content from HTML
content = await extractor.extract_content(html, url)

print(f"Title: {content.title}")
print(f"Word Count: {content.word_count}")
print(f"Quality Score: {content.content_quality_score}")
```

### URL Validation

```python
from backend.crawlers.utils import URLValidator

validator = URLValidator()

# Validate URL
result = await validator.validate_url("https://example.com")

if result.is_valid:
    print(f"Platform: {result.platform}")
    print(f"Security Score: {result.security_score}")
```

### CAPTCHA Solving

```python
from backend.crawlers.utils import setup_default_captcha_solver

solver = setup_default_captcha_solver({
    '2captcha': 'your_api_key'
})

# Detect and solve CAPTCHAs
solutions = await solver.detect_and_solve(html_content, page_url)
```

### Content Fingerprinting

```python
from backend.crawlers.utils import generate_content_fingerprint, calculate_content_similarity

# Generate fingerprint for content
fingerprint = await generate_content_fingerprint(
    content="Your content here",
    content_type="text",
    content_id="unique_id"
)

# Compare fingerprints
similarity = await calculate_content_similarity(fingerprint1, fingerprint2)
print(f"Similarity score: {similarity.similarity_score}")
```

### Surveillance Engine

```python
from backend.crawlers.utils import create_surveillance_engine, create_surveillance_target

# Create surveillance system
engine = create_surveillance_engine()

# Create monitoring target
target = create_surveillance_target(
    user_id="user123",
    name="My Content Protection",
    description="Monitor for unauthorized use",
    keywords=["my brand", "my content"],
    platforms=["youtube", "instagram", "tiktok"]
)

# Start monitoring
await engine.add_surveillance_target(target)
await engine.start_surveillance(target.target_id)
```

### Security Scanner

```python
from backend.crawlers.utils import quick_security_scan

# Scan URL for security threats
assessment = await quick_security_scan("https://example.com")

print(f"Security Level: {assessment.security_level}")
print(f"Threat Types: {assessment.threat_types}")
print(f"Risk Factors: {assessment.risk_factors}")
```

### Content Encryption

```python
from backend.crawlers.utils import quick_encrypt_content, create_content_encryption

# Quick encryption
encrypted = quick_encrypt_content("sensitive data")

# Advanced encryption
encryption = create_content_encryption()
key_id, key = encryption.generate_key()
encrypted_data = encryption.encrypt_content("sensitive data", key_id)
decrypted = encryption.decrypt_content(encrypted_data)
```

### Performance Monitoring

```python
from backend.crawlers.utils import create_performance_monitor, monitor_performance

# Create monitor
monitor = create_performance_monitor()
monitor.start_monitoring()

# Use decorator for automatic monitoring
@monitor_performance(monitor)
async def my_function():
    # Your code here
    pass

# Generate performance report
report = monitor.generate_performance_report()
print(f"Average response time: {report.average_response_time}s")
```

### Advanced Caching

```python
from backend.crawlers.utils import create_advanced_cache, CacheStrategy

# Create cache with LRU strategy
cache = create_advanced_cache(
    max_size=10000,
    strategy=CacheStrategy.LRU
)

# Cache operations
cache.set("key", "value", ttl=3600)
value = cache.get("key")
stats = cache.get_cache_stats()
```

## Configuration

### Platform Configurations

Each platform has optimized default settings:

```python
PLATFORM_CONFIGS = {
    "youtube": {
        "base_delay": 1.0,
        "max_requests_per_minute": 100,
        "burst_limit": 10
    },
    "instagram": {
        "base_delay": 2.0,
        "max_requests_per_minute": 60,
        "burst_limit": 5
    }
    # ... more platforms
}
```

### Redis Configuration

For distributed rate limiting:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
limiter = YouTubeRateLimiter(redis_client=redis_client)
```

## API Reference

### RateLimiter Classes

- `RateLimiter`: Base rate limiter with adaptive backoff
- `YouTubeRateLimiter`: YouTube-optimized rate limiting
- `InstagramRateLimiter`: Instagram-optimized rate limiting
- `TikTokRateLimiter`: TikTok-optimized rate limiting
- `TwitterRateLimiter`: Twitter-optimized rate limiting
- `FacebookRateLimiter`: Facebook-optimized rate limiting
- `SpotifyRateLimiter`: Spotify-optimized rate limiting

### Content Classes

- `ContentExtractor`: Advanced content extraction and analysis
- `ExtractedContent`: Structured content data
- `SocialMediaContent`: Social media specific content

### Validation Classes

- `URLValidator`: Comprehensive URL validation
- `URLValidationResult`: Validation result data
- `URLType`: URL type enumeration

### Security Classes

- `CookieManager`: Enterprise cookie management
- `CaptchaSolver`: Multi-strategy CAPTCHA solving

## Performance Metrics

The module tracks comprehensive performance metrics:

- **Rate Limiting**: Request counts, delays, backoff calculations
- **Content Quality**: Readability scores, sentiment analysis
- **Validation**: Security assessments, platform detection accuracy
- **CAPTCHA Solving**: Success rates, solving times

## Security Features

### URL Security Assessment

- Malicious domain detection
- Suspicious pattern recognition
- Security scoring (0.0-1.0)
- Protocol validation

### Cookie Security

- Encryption for sensitive cookies
- Domain restrictions
- Content validation
- Expiration management

### Content Fingerprinting

- SHA-256 content hashing
- Duplicate detection
- Content normalization

## Best Practices

### Rate Limiting

1. **Use platform-specific limiters** for optimal performance
2. **Enable Redis** for distributed environments
3. **Monitor rate limit statistics** for optimization
4. **Handle rate limit responses** gracefully

### Content Extraction

1. **Validate URLs** before extraction
2. **Handle dynamic content** with Selenium when needed
3. **Extract structured data** for better analysis
4. **Assess content quality** for filtering

### Security

1. **Validate all URLs** before processing
2. **Use encrypted cookie storage** for sensitive data
3. **Monitor security scores** for threat detection
4. **Regular security rule updates**

## Troubleshooting

### Common Issues

1. **Rate Limiting Too Aggressive**
   - Adjust `base_delay` and `backoff_factor`
   - Monitor platform responses

2. **Content Extraction Failures**
   - Check URL accessibility
   - Verify HTML structure
   - Enable dynamic content handling

3. **CAPTCHA Solving Failures**
   - Verify API keys
   - Check solver compatibility
   - Monitor success rates

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

This is proprietary software. Contact mlaiel@live.de for collaboration opportunities.

## License

Copyright © 2025 Fahed Mlaiel. All rights reserved.

**UNAUTHORIZED USE PROHIBITED**

This software is protected by copyright law. Any unauthorized use, reproduction, or distribution is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de

## Support

For technical support and licensing:
- **Email:** mlaiel@live.de
- **Project Owner:** Fahed Mlaiel

---

*Part of the IA-Influencer-Agent ecosystem - Professional AI-powered content protection and monetization platform.*
