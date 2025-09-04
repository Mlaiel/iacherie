# Live Streaming Module Documentation

## Overview

The `backend/streaming` module provides comprehensive live streaming functionality for the Ainflue platform, including:

- **Live Stream Management** - Core streaming operations and multi-platform broadcasting
- **Virtual Streamers** - AI-powered avatars and automated content creation  
- **Chat Moderation** - Advanced content filtering and community management
- **Donation Handling** - Payment processing, goals, and real-time alerts

## Quick Start

### 1. Import the modules

```python
from backend.streaming import (
    LiveStreamManager,
    VirtualStreamerEngine, 
    ChatModerator,
    DonationHandler
)
```

### 2. Initialize with Redis and Database

```python
import redis
from sqlalchemy.orm import Session

# Setup Redis and Database connections
redis_client = redis.Redis(host='localhost', port=6379, db=0)
db_session = Session()  # Your SQLAlchemy session

# Create managers
stream_manager = LiveStreamManager(redis_client, db_session)
virtual_engine = VirtualStreamerEngine(redis_client, db_session)
chat_moderator = ChatModerator(redis_client, db_session)
donation_handler = DonationHandler(redis_client, db_session)
```

### 3. Start the systems

```python
# Start all systems
await stream_manager.start_manager()
await virtual_engine.start_engine()
await chat_moderator.start_moderator()
await donation_handler.start_handler()
```

## Module Details

### Live Stream Manager

**Purpose**: Manages live streaming sessions, RTMP servers, and multi-platform broadcasting.

**Key Features**:
- Multi-platform streaming (Twitch, YouTube, Facebook, etc.)
- Real-time metrics and performance monitoring
- WebSocket notifications for stream events
- Automatic stream recording and archival

**Example Usage**:
```python
from backend.streaming import StreamConfig, StreamQuality, PlatformType

# Configure stream
config = StreamConfig(
    title="My Live Stream",
    quality=StreamQuality.HIGH,
    platforms=[PlatformType.TWITCH, PlatformType.YOUTUBE],
    enable_chat=True,
    enable_donations=True
)

# Create and start stream
stream_id = await stream_manager.create_stream("user_123", config)
success = await stream_manager.start_stream(stream_id)
```

### Virtual Streamer Engine

**Purpose**: Creates AI-powered virtual streamers with customizable personalities and avatars.

**Key Features**:
- Configurable AI personalities and behavior patterns
- Real-time chat interaction and response generation
- Avatar animation and voice synthesis integration
- Scheduled streaming and automated content creation

**Example Usage**:
```python
from backend.streaming import AvatarConfig, PersonalityConfig, AvatarType, PersonalityType

# Configure virtual streamer
avatar_config = AvatarConfig(
    avatar_type=AvatarType.ANIME,
    name="VTuber Bot",
    voice_settings={"language": "en", "voice": "friendly"}
)

personality_config = PersonalityConfig(
    personality_type=PersonalityType.ENERGETIC,
    traits=["helpful", "entertaining"],
    knowledge_areas=["gaming", "technology"]
)

# Create virtual streamer
streamer_id = await virtual_engine.create_virtual_streamer(
    "user_123", "VTuber Bot", avatar_config, personality_config
)

# Activate for a stream
await virtual_engine.activate_streamer(streamer_id, stream_id)
```

### Chat Moderator

**Purpose**: Provides advanced chat moderation with AI-powered content filtering.

**Key Features**:
- Real-time spam and toxicity detection
- User behavior analysis and trust scoring
- Automated moderation actions (warnings, timeouts, bans)
- Custom moderation rules and filters

**Example Usage**:
```python
from backend.streaming import ModerationConfig, ChatMessage, UserRole

# Configure moderation
config = ModerationConfig(
    enabled=True,
    auto_moderation=True,
    strict_mode=False,
    max_message_length=500,
    spam_detection_sensitivity=0.8
)

# Setup stream moderation
await chat_moderator.configure_stream_moderation(stream_id, config)

# Moderate a message
message = ChatMessage(
    message_id="msg_123",
    stream_id=stream_id,
    user_id="user_456", 
    username="ChatUser",
    user_role=UserRole.VIEWER,
    content="Hello everyone!",
    timestamp=datetime.now(timezone.utc)
)

action, violations, score = await chat_moderator.moderate_message(stream_id, message)
```

### Donation Handler

**Purpose**: Processes donations, manages payment methods, and tracks fundraising goals.

**Key Features**:
- Multi-currency payment processing (Stripe, PayPal, crypto)
- Real-time donation alerts and notifications
- Fundraising goal tracking and progress monitoring
- Fraud detection and refund management

**Example Usage**:
```python
from backend.streaming import DonationConfig, CurrencyCode, PaymentMethod
from decimal import Decimal

# Configure donations
config = DonationConfig(
    enabled=True,
    min_amount=Decimal('1.00'),
    max_amount=Decimal('1000.00'),
    currency=CurrencyCode.USD,
    payment_methods=[PaymentMethod.STRIPE, PaymentMethod.PAYPAL]
)

# Setup stream donations
await donation_handler.configure_stream_donations(stream_id, "user_123", config)

# Process a donation
donor_info = {
    "user_id": "donor_123",
    "name": "Generous Viewer", 
    "email": "donor@example.com"
}

result = await donation_handler.process_donation(
    stream_id=stream_id,
    donor_info=donor_info,
    amount=Decimal('25.00'),
    currency=CurrencyCode.USD,
    payment_method=PaymentMethod.STRIPE,
    message="Great stream!"
)
```

## Database Models

The module includes SQLAlchemy models for persistent storage:

- `LiveStream` - Stream session data and configuration
- `VirtualStreamer` - Virtual streamer profiles and settings
- `ChatModeration` - Moderation logs and user history  
- `UserModerationRecord` - User behavior tracking
- `Donation` - Donation transactions and metadata
- `DonationGoalRecord` - Fundraising goals and progress

## Redis Integration

Real-time data is cached in Redis for performance:

- Stream status and metrics
- Active virtual streamer sessions
- Chat moderation state and user scores
- Donation alerts and goal progress
- WebSocket connection management

## WebSocket Events

The system publishes real-time events via Redis:

- `stream_started` / `stream_stopped` - Stream lifecycle events
- `donation_completed` - New donation notifications
- `goal_achieved` - Fundraising milestone reached
- `moderation_events` - Chat moderation actions
- `metrics_update` - Real-time performance data

## Error Handling

All modules include comprehensive error handling:

- Graceful degradation when services are unavailable
- Automatic retry mechanisms for transient failures
- Detailed logging for debugging and monitoring
- Circuit breaker patterns for external API calls

## Security Features

- Input validation and sanitization
- Rate limiting and abuse prevention
- Secure payment processing with PCI compliance
- Audit logging for all moderation actions
- Encrypted data storage for sensitive information

## Performance Considerations

- Asynchronous processing for all I/O operations
- Redis caching for frequently accessed data
- Database connection pooling and optimization
- Horizontal scaling support with load balancing
- Background task processing for heavy operations

## Configuration

Environment variables for configuration:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database Configuration  
DATABASE_URL=postgresql://user:pass@localhost/ainflue

# Payment Processors
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Streaming Configuration
RTMP_SERVER_URL=rtmp://live.ainflue.com/live
WEBHOOK_SECRET=your_webhook_secret
```

## Monitoring and Analytics

Built-in metrics and monitoring:

- Stream performance (bitrate, latency, viewer count)
- Virtual streamer engagement and interaction rates
- Chat moderation effectiveness and accuracy
- Donation conversion rates and goal completion
- System health and error rates

This module provides a complete live streaming solution with enterprise-grade features for content creators and platform operators.