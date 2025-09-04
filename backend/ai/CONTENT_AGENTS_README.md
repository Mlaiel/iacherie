# Consolidated Content AI Agents

This module consolidates all content-related AI agents into a single, cohesive interface for the IA Influencer platform.

## Overview

The `backend/ai/content.py` module provides a unified interface for all content creation and optimization needs through the following specialized agents:

1. **Content Optimizer Agent** - Optimizes content for specific platforms and engagement
2. **Hashtag Generator Agent** - Generates relevant and trending hashtags
3. **Caption Writer Agent** - Creates compelling captions in various styles
4. **Story Teller Agent** - Crafts engaging narratives and stories
5. **Reply Generator Agent** - Generates appropriate responses to comments
6. **Viral Predictor Agent** - Predicts viral potential and provides optimization suggestions
7. **Content Scheduler Agent** - Schedules content for optimal timing

## Quick Start

```python
from backend.ai.content import (
    create_content_agent,
    ContentRequest,
    ContentType,
    Platform,
    ContentStyle
)

# Create the consolidated agent
agent = create_content_agent()

# Process a content request
request = ContentRequest(
    content_type=ContentType.CAPTION,
    platform=Platform.INSTAGRAM,
    style=ContentStyle.CASUAL,
    target_audience="general",
    topic="artificial intelligence"
)

result = await agent.process_content_request(request)
print(f"Generated content: {result.content}")
```

## Supported Platforms

- Instagram
- TikTok
- YouTube
- Twitter
- LinkedIn
- Facebook
- Snapchat
- Pinterest

## Content Types

- Text
- Image
- Video
- Audio
- Story
- Caption
- Hashtag Set
- Reply
- Post
- Article
- Script

## Content Styles

- Casual
- Professional
- Humorous
- Educational
- Promotional
- Storytelling
- Viral
- Trendy

## Main Features

### 1. Content Optimization
Automatically optimizes content for:
- Platform-specific requirements (length, format, etc.)
- Engagement keywords
- Call-to-action elements
- Platform best practices

### 2. Hashtag Generation
Generates optimized hashtags based on:
- Content analysis
- Platform trends
- Category relevance
- Performance prediction

### 3. Caption Writing
Creates captions with:
- Style-specific templates
- Platform adaptation
- Audience targeting
- Length optimization

### 4. Storytelling
Builds compelling narratives using:
- Hero's journey structure
- Before/after format
- Problem/solution approach
- Engagement analysis

### 5. Reply Generation
Generates contextual replies with:
- Sentiment analysis
- Tone matching
- Platform adaptation
- Response templates

### 6. Viral Prediction
Analyzes viral potential through:
- Content length analysis
- Emotional word detection
- Call-to-action presence
- Visual elements assessment
- Timing optimization

### 7. Content Scheduling
Optimizes publication timing with:
- Platform-specific optimal times
- Audience activity patterns
- Cross-promotion suggestions
- Follow-up action planning

## Complete Content Package

Create a comprehensive content package:

```python
package = await agent.create_complete_content_package(
    topic="machine learning",
    platform=Platform.INSTAGRAM,
    style=ContentStyle.EDUCATIONAL
)

# Package includes:
# - Optimized main content
# - Related story
# - Hashtag suggestions
# - Viral analysis
# - Sample replies
# - Scheduling suggestions
```

## Agent Status

Check the status of all agents:

```python
status = await agent.get_agent_status()
print(f"Status: {status['status']}")
print(f"Available agents: {status['agents']}")
print(f"Capabilities: {status['capabilities']}")
```

## Error Handling

All agents include comprehensive error handling and will return appropriate error messages in case of issues.

## Integration

This module integrates seamlessly with:
- Existing AI agent framework
- Platform APIs
- Content management systems
- Analytics and monitoring tools

## Author

**Fahed Mlaiel** - mlaiel@live.de  
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

## License

⚠️ **PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL** ⚠️

This module is the exclusive intellectual property of Fahed Mlaiel and is protected by copyright law.