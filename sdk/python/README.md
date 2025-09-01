# Ainflue Platform Python SDK

Official Python SDK for the Ainflue AI Platform API.

## Installation

```bash
pip install ainflue-sdk
```

## Quick Start

```python
import asyncio
from ainflue_sdk import AinflueSdk

async def main():
    # Initialize SDK with your API key
    async with AinflueSdk("your-api-key-here") as sdk:
        
        # Analyze content
        result = await sdk.content.analyze("path/to/your/video.mp4")
        print(f"Analysis complete: {result['analysis_id']}")
        
        # Chat with AI agent
        response = await sdk.ai_agents.chat(
            agent_name="content_analyzer",
            message="Please analyze this content for copyright issues"
        )
        print(f"Agent response: {response['response']['content']}")
        
        # Get analytics
        metrics = await sdk.analytics.get_performance_metrics()
        print(f"Performance metrics: {metrics}")

# Run the example
asyncio.run(main())
```

## Features

### Content Protection & Analysis
- **Content Fingerprinting**: Generate unique fingerprints for audio/video content
- **Copyright Detection**: Check content against global copyright databases
- **Content Analysis**: AI-powered content analysis and insights
- **Multi-format Support**: Support for various audio and video formats

### AI Agents
- **Intelligent Chat**: Interact with specialized AI agents
- **Content Processing**: AI-powered content understanding and processing
- **Multi-language Support**: 644+ languages supported
- **Learning Capabilities**: Agents learn and improve over time

### Monetization
- **Payment Processing**: Secure payment handling
- **Revenue Analytics**: Detailed revenue tracking and insights
- **Subscription Management**: Manage user subscriptions
- **Payout Automation**: Automated creator payouts

### Analytics & Reporting
- **Performance Metrics**: Comprehensive platform metrics
- **Custom Reports**: Generate custom analytical reports
- **Real-time Data**: Live performance monitoring
- **Export Options**: Multiple export formats (JSON, CSV, PDF)

## API Reference

### Content API

```python
# Analyze content
result = await sdk.content.analyze(
    content_path="video.mp4",
    analysis_type="comprehensive",  # basic, comprehensive, deep
    options={
        "include_fingerprint": True,
        "check_copyright": True,
        "extract_metadata": True
    }
)

# Generate fingerprint only
fingerprint = await sdk.content.fingerprint("audio.mp3")

# Check copyright
copyright_result = await sdk.content.check_copyright("content.mp4")
```

### AI Agents API

```python
# List available agents
agents = await sdk.ai_agents.list_agents()

# Get agent information
agent_info = await sdk.ai_agents.get_agent_info("content_analyzer")

# Chat with agent
response = await sdk.ai_agents.chat(
    agent_name="content_analyzer",
    message="Analyze this content for potential issues",
    context={"user_id": "123", "content_type": "video"},
    parameters={"analysis_depth": "deep"}
)
```

### Monetization API

```python
# Create payment
payment = await sdk.monetization.create_payment(
    amount=19.99,
    currency="USD",
    description="Premium subscription",
    metadata={"user_id": "123", "plan": "premium"}
)

# Get revenue analytics
revenue = await sdk.monetization.get_revenue_analytics(
    start_date="2025-01-01",
    end_date="2025-01-31",
    granularity="daily"
)
```

### Analytics API

```python
# Get performance metrics
metrics = await sdk.analytics.get_performance_metrics(
    metric_type="content",  # all, content, revenue, users
    time_period="7d"        # 1h, 1d, 7d, 30d
)

# Generate custom report
report = await sdk.analytics.generate_report(
    report_type="content_performance",
    parameters={
        "date_range": "last_30_days",
        "include_charts": True
    }
)
```

## Configuration

### Environment Configuration

```python
from ainflue_sdk import AinflueSdk, SdkConfig, Environment

# Production (default)
sdk = AinflueSdk("your-api-key")

# Staging
config = SdkConfig(
    api_key="your-api-key",
    base_url=Environment.STAGING.value
)
sdk = AinflueSdk("your-api-key", config=config)

# Development
config = SdkConfig(
    api_key="your-api-key",
    base_url=Environment.DEVELOPMENT.value,
    debug=True
)
sdk = AinflueSdk("your-api-key", config=config)
```

### Advanced Configuration

```python
config = SdkConfig(
    api_key="your-api-key",
    base_url="https://api.ainflue.com/v1",
    timeout=60,           # Request timeout in seconds
    max_retries=5,        # Maximum retry attempts
    retry_delay=2.0,      # Initial retry delay
    debug=True,           # Enable debug logging
    user_agent="MyApp/1.0"  # Custom user agent
)

sdk = AinflueSdk("your-api-key", config=config)
```

## Error Handling

```python
from ainflue_sdk import (
    AinflueSdk, 
    AuthenticationError, 
    RateLimitError, 
    ApiError
)

try:
    async with AinflueSdk("your-api-key") as sdk:
        result = await sdk.content.analyze("video.mp4")
        
except AuthenticationError:
    print("Invalid API key or authentication failed")
    
except RateLimitError:
    print("Rate limit exceeded, please try again later")
    
except ApiError as e:
    print(f"API error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

### Complete Content Analysis Pipeline

```python
import asyncio
from ainflue_sdk import AinflueSdk

async def analyze_content_pipeline(content_path: str):
    async with AinflueSdk("your-api-key") as sdk:
        
        # Step 1: Basic content analysis
        print("🔍 Analyzing content...")
        analysis = await sdk.content.analyze(
            content_path=content_path,
            analysis_type="comprehensive"
        )
        
        print(f"✅ Analysis complete: {analysis['analysis_id']}")
        print(f"Content type: {analysis['content_type']}")
        print(f"Duration: {analysis['metadata']['duration']} seconds")
        
        # Step 2: Copyright check
        print("\n📄 Checking copyright...")
        copyright_result = await sdk.content.check_copyright(content_path)
        
        if copyright_result['matches_found']:
            print(f"⚠️ Copyright matches found: {len(copyright_result['matches'])}")
            for match in copyright_result['matches']:
                print(f"  - {match['title']} ({match['confidence']}% confidence)")
        else:
            print("✅ No copyright issues detected")
        
        # Step 3: AI agent analysis
        print("\n🤖 Getting AI insights...")
        agent_response = await sdk.ai_agents.chat(
            agent_name="content_analyzer",
            message=f"Please provide insights about the analysis: {analysis['analysis_id']}",
            context={"analysis_data": analysis}
        )
        
        print(f"🧠 AI Insights: {agent_response['response']['content']}")
        
        # Step 4: Generate report
        print("\n📊 Generating report...")
        report = await sdk.analytics.generate_report(
            report_type="content_analysis",
            parameters={
                "analysis_id": analysis['analysis_id'],
                "include_recommendations": True
            }
        )
        
        print(f"📄 Report generated: {report['report_url']}")
        
        return {
            "analysis": analysis,
            "copyright": copyright_result,
            "ai_insights": agent_response,
            "report": report
        }

# Run the pipeline
result = asyncio.run(analyze_content_pipeline("my_video.mp4"))
```

### Revenue Analytics Dashboard

```python
import asyncio
from datetime import datetime, timedelta
from ainflue_sdk import AinflueSdk

async def revenue_dashboard():
    async with AinflueSdk("your-api-key") as sdk:
        
        # Get current performance metrics
        metrics = await sdk.analytics.get_performance_metrics(
            metric_type="revenue",
            time_period="30d"
        )
        
        print("💰 Revenue Dashboard")
        print("=" * 50)
        print(f"Total Revenue (30d): ${metrics['total_revenue']:.2f}")
        print(f"Active Users: {metrics['active_users']:,}")
        print(f"Conversion Rate: {metrics['conversion_rate']:.2%}")
        
        # Get detailed revenue analytics
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        revenue_data = await sdk.monetization.get_revenue_analytics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            granularity="daily"
        )
        
        print(f"\n📈 Daily Revenue Trend:")
        for day_data in revenue_data['daily_revenue'][-7:]:  # Last 7 days
            date = day_data['date']
            revenue = day_data['revenue']
            print(f"  {date}: ${revenue:.2f}")
        
        # Create payment
        print(f"\n💳 Creating test payment...")
        payment = await sdk.monetization.create_payment(
            amount=29.99,
            currency="USD",
            description="Premium subscription upgrade",
            metadata={"user_id": "test_user", "plan": "premium"}
        )
        
        print(f"Payment created: {payment['payment_id']}")
        print(f"Payment URL: {payment['payment_url']}")

# Run the dashboard
asyncio.run(revenue_dashboard())
```

### AI Agent Conversation

```python
import asyncio
from ainflue_sdk import AinflueSdk

async def ai_conversation():
    async with AinflueSdk("your-api-key") as sdk:
        
        # List available agents
        agents = await sdk.ai_agents.list_agents()
        print("🤖 Available AI Agents:")
        for agent in agents:
            print(f"  - {agent['name']}: {agent['description']}")
        
        # Start conversation with content analyzer
        agent_name = "content_analyzer"
        conversation_context = {}
        
        messages = [
            "Hello! I need help analyzing a video file.",
            "The video is 5 minutes long and contains music.",
            "Can you check if there are any copyright issues?",
            "What are your recommendations for monetization?"
        ]
        
        print(f"\n💬 Conversation with {agent_name}:")
        print("=" * 50)
        
        for i, message in enumerate(messages, 1):
            print(f"\n👤 User ({i}): {message}")
            
            response = await sdk.ai_agents.chat(
                agent_name=agent_name,
                message=message,
                context=conversation_context,
                parameters={"conversation_id": "demo_conversation"}
            )
            
            print(f"🤖 Agent: {response['response']['content']}")
            
            # Update context with response for continuity
            conversation_context.update({
                "last_response": response['response'],
                "confidence": response['confidence']
            })
            
            # Simulate user reading time
            await asyncio.sleep(1)
        
        print(f"\n✅ Conversation completed!")
        print(f"Final confidence: {response['confidence']:.2%}")

# Run the conversation
asyncio.run(ai_conversation())
```

## Support

### Documentation
- **API Documentation**: https://docs.ainflue.com/api
- **SDK Documentation**: https://docs.ainflue.com/sdk/python
- **Examples**: https://github.com/Mlaiel/Ainflue/tree/main/examples/python

### Getting Help
- **Email Support**: mlaiel@live.de
- **GitHub Issues**: https://github.com/Mlaiel/Ainflue/issues
- **Community Forum**: https://community.ainflue.com

### Rate Limits
- **Free Tier**: 1,000 requests/hour
- **Pro Tier**: 10,000 requests/hour  
- **Enterprise**: Custom limits

Contact support for rate limit increases.

## License

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This SDK is provided under a proprietary license. See LICENSE file for details.