# Ainflue Python SDK

Official Python SDK for the Ainflue AI-powered content protection and monetization platform.

## Installation

```bash
pip install ainflue-sdk
```

Or install from source:

```bash
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue/sdk/python
pip install .
```

## Quick Start

### Async Usage

```python
import asyncio
from ainflue_sdk import create_sdk

async def main():
    # Create SDK instance
    async with create_sdk(api_key="your-api-key") as sdk:
        # Analyze content
        result = await sdk.analyze_content(
            content_data="Your content here",
            content_type="text"
        )
        
        print(f"Analysis complete: {result.content_id}")
        print(f"Confidence: {result.confidence}")

# Run the example
asyncio.run(main())
```

### Synchronous Usage

```python
from ainflue_sdk import create_sync_sdk

# Create sync SDK instance
sdk = create_sync_sdk(api_key="your-api-key")

try:
    # Analyze content
    result = sdk.analyze_content(
        content_data="Your content here",
        content_type="text"
    )
    
    print(f"Analysis complete: {result.content_id}")
    print(f"Confidence: {result.confidence}")
    
finally:
    sdk.close()
```

## Features

- **Content Analysis**: AI-powered content fingerprinting and analysis
- **Content Protection**: Multi-platform content monitoring and protection
- **Monetization**: Revenue optimization and licensing management
- **Analytics**: Comprehensive platform analytics and insights
- **User Management**: Account and profile management
- **Async & Sync**: Support for both async and synchronous usage
- **Type Safety**: Full type hints and Pydantic validation
- **Error Handling**: Comprehensive error handling and retries

## API Reference

### Content Analysis

```python
# Analyze text content
result = await sdk.analyze_content(
    content_data="Text to analyze",
    content_type="text",
    analysis_options={
        "generate_fingerprint": True,
        "detect_language": True,
        "extract_metadata": True
    }
)

# Upload and analyze file
upload_result = await sdk.upload_content(
    file_path="/path/to/file.mp3",
    title="My Audio Track",
    description="Original music composition",
    tags=["music", "original"]
)
```

### Content Protection

```python
# Enable content protection
protection = await sdk.protect_content(
    content_id="content-123",
    platforms=["youtube", "spotify", "instagram"],
    protection_options={
        "auto_takedown": True,
        "notification_email": True
    }
)

# Check protection status
status = await sdk.check_protection_status(protection.protection_id)

# Get detected matches
matches = await sdk.get_protection_matches(protection.protection_id)
```

### Monetization

```python
# Create content license
license = await sdk.create_license(
    content_id="content-123",
    license_type="royalty_free",
    terms={
        "usage_type": "commercial",
        "price": 99.99,
        "currency": "USD"
    }
)

# Get revenue statistics
revenue = await sdk.get_revenue_stats(
    date_from="2024-01-01",
    date_to="2024-12-31"
)
```

### Analytics

```python
# Get analytics data
analytics = await sdk.get_analytics(
    metric_type="content_performance",
    date_from="2024-01-01",
    date_to="2024-12-31",
    filters={"platform": "youtube"}
)
```

## Configuration

### Environment Variables

```bash
export AINFLUE_API_KEY="your-api-key"
export AINFLUE_BASE_URL="https://api.ainflue.com"
```

### Custom Configuration

```python
from ainflue_sdk import AinflueSdkConfig, AinflueSdk

config = AinflueSdkConfig(
    api_key="your-api-key",
    base_url="https://api.ainflue.com",
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)

sdk = AinflueSdk(config)
```

## Error Handling

```python
from ainflue_sdk import (
    AinflueSdkException,
    AuthenticationError,
    APIError,
    ValidationError
)

try:
    result = await sdk.analyze_content("content", "text")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid request: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except AinflueSdkException as e:
    print(f"SDK error: {e}")
```

## Examples

See the `examples.py` file for comprehensive usage examples:

- Content analysis and fingerprinting
- Multi-platform content protection
- Revenue optimization and licensing
- Batch processing workflows
- Error handling strategies
- Performance optimization

## Development

### Setup Development Environment

```bash
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue/sdk/python
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
black .
isort .
flake8 .
mypy .
```

## Support

- **Documentation**: https://docs.ainflue.com
- **Issues**: https://github.com/Mlaiel/Ainflue/issues
- **Email**: mlaiel@live.de

## License

This SDK is licensed under the MIT License. See LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Content analysis and protection
- Monetization features
- Comprehensive error handling
- Async and sync support