# Communication Module Developer Documentation

## Module Architecture

The Communication module provides enterprise-grade real-time communication infrastructure for the IA Influencer Agent platform, supporting multi-format creator collaboration, live streaming, and comprehensive notification systems.

## Component Overview

### 1. WebSocket Manager (`websocket_manager.py`)
**Purpose**: Real-time bidirectional communication management
**Key Features**:
- Connection pooling and lifecycle management
- Room-based message routing
- Connection authentication and authorization
- Performance monitoring and health checks

```python
# Connection management
manager = WebSocketManager(redis_client, db_session)
await manager.initialize()

# Join collaboration room
await manager.join_room(connection_id, room_id, user_permissions)

# Broadcast message to room
await manager.broadcast_to_room(room_id, message_data)
```

### 2. Message Broker (`message_broker.py`)
**Purpose**: Asynchronous message processing and delivery
**Key Features**:
- Priority-based queuing system
- Dead letter queue handling
- Message persistence and retry logic
- Cross-service communication

```python
# Create message queue
await broker.create_queue(
    queue_name="creator_notifications",
    queue_type=QueueType.PRIORITY,
    max_size=10000
)

# Publish message
await broker.publish_message(
    queue_name="creator_notifications",
    payload=message_payload,
    header=message_header
)
```

### 3. Notification Engine (`notification_engine.py`)
**Purpose**: Multi-channel notification delivery system
**Key Features**:
- Template-based notifications with localization
- Multi-channel delivery (email, SMS, push, webhooks)
- User preference management
- Delivery analytics and tracking

```python
# Create notification template
await engine.create_template(
    template_key="collaboration_invite",
    name="Collaboration Invitation",
    notification_type=NotificationType.COLLABORATION_REQUEST,
    subject_template="Invitation to collaborate on {project_name}",
    body_template="You've been invited to collaborate...",
    variables=["project_name", "inviter_name"],
    creator_types=[ContentCreatorType.MUSICIAN, ContentCreatorType.BLOGGER]
)

# Send notification
await engine.send_notification(
    user_id="creator123",
    template_key="collaboration_invite",
    variables={"project_name": "Beat Session", "inviter_name": "DJ Max"}
)
```

### 4. Live Collaboration (`live_collaboration.py`)
**Purpose**: Real-time creator collaboration management
**Key Features**:
- Multi-format collaboration rooms
- File sharing with version control
- Role-based permissions
- Activity tracking and analytics

```python
# Create collaboration room
room_id = await collaboration.create_room(
    owner_id="creator456",
    name="Music Production Session",
    collaboration_type=CollaborationType.MUSIC_PRODUCTION,
    settings=RoomSettings(
        max_participants=10,
        enable_voice=True,
        enable_video=True,
        enable_file_sharing=True
    )
)

# Share content in room
content_id = await collaboration.share_content(
    room_id=room_id,
    owner_id="creator456",
    name="Beat_v1.wav",
    content_type="audio/wav",
    storage_path="/uploads/audio/beat_v1.wav",
    size_bytes=1024000
)
```

### 5. Streaming Coordinator (`streaming_coordinator.py`)
**Purpose**: Multi-platform live streaming management
**Key Features**:
- Simultaneous multi-platform streaming
- Real-time viewer analytics
- Stream quality monitoring
- Platform API integration

```python
# Create stream session
session_id = await coordinator.create_stream(
    streamer_id="streamer789",
    title="Live Music Production",
    stream_type=StreamType.LIVE_MUSIC,
    settings=StreamSettings(
        quality=StreamQuality.HIGH,
        enable_chat=True,
        enable_recording=True
    ),
    platforms=[
        PlatformConfig(
            platform=PlatformType.YOUTUBE,
            api_key="yt_key",
            stream_key="yt_stream_key",
            rtmp_url="rtmp://youtube.com/live"
        ),
        PlatformConfig(
            platform=PlatformType.TWITCH,
            api_key="twitch_key",
            stream_key="twitch_stream_key",
            rtmp_url="rtmp://live.twitch.tv/live"
        )
    ]
)

# Start streaming
await coordinator.start_stream(session_id, "streamer789")
```

## Integration Patterns

### 1. Service Initialization
```python
from backend.database.communication import get_communication_service

async def initialize_app():
    async with get_communication_service(redis_client, db_session) as comm_service:
        # Service is ready to use
        return comm_service
```

### 2. Creator Collaboration Workflow
```python
async def create_collaboration_session(owner_id: str, collaborators: List[str]):
    # 1. Create collaboration room
    room_id = await comm_service.live_collaboration.create_room(
        owner_id=owner_id,
        name="Project Collaboration",
        collaboration_type=CollaborationType.CONTENT_CREATION
    )
    
    # 2. Send invitations to collaborators
    for collaborator_id in collaborators:
        await comm_service.notification_engine.send_notification(
            user_id=collaborator_id,
            template_key="collaboration_invite",
            variables={
                "room_id": room_id,
                "owner_name": await get_user_name(owner_id)
            }
        )
    
    # 3. Set up real-time messaging
    await comm_service.websocket_manager.create_room(
        room_id=room_id,
        room_type=RoomType.PROJECT
    )
    
    return room_id
```

### 3. Live Streaming Workflow
```python
async def start_multi_platform_stream(streamer_id: str, platforms: List[str]):
    # 1. Create stream session
    session_id = await comm_service.streaming_coordinator.create_stream(
        streamer_id=streamer_id,
        title="Live Creator Session",
        stream_type=StreamType.LIVE_MUSIC,
        settings=default_stream_settings,
        platforms=prepare_platform_configs(platforms)
    )
    
    # 2. Notify followers
    followers = await get_user_followers(streamer_id)
    await comm_service.notification_engine.send_bulk_notification(
        user_ids=followers,
        template_key="stream_starting",
        variables={"streamer_name": await get_user_name(streamer_id)}
    )
    
    # 3. Start streaming
    success = await comm_service.streaming_coordinator.start_stream(
        session_id, streamer_id
    )
    
    return session_id if success else None
```

## Database Schema Integration

### Core Tables Structure
```sql
-- WebSocket connections
CREATE TABLE websocket_connections (
    id UUID PRIMARY KEY,
    connection_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    connected_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

-- Message queues
CREATE TABLE message_queues (
    id UUID PRIMARY KEY,
    queue_name VARCHAR(255) NOT NULL,
    queue_type VARCHAR(50) NOT NULL,
    config JSONB,
    stats JSONB
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    notification_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    notification_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    content TEXT,
    channels VARCHAR(50)[],
    created_at TIMESTAMP WITH TIME ZONE
);

-- Collaboration rooms
CREATE TABLE collaboration_rooms (
    id UUID PRIMARY KEY,
    room_id VARCHAR(255) UNIQUE NOT NULL,
    owner_id VARCHAR(255) NOT NULL,
    collaboration_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'creating',
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);

-- Stream sessions
CREATE TABLE stream_sessions (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    streamer_id VARCHAR(255) NOT NULL,
    stream_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    platforms JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);
```

## Performance Considerations

### 1. Connection Management
- **Connection Pooling**: Efficient WebSocket connection resource management
- **Load Balancing**: Distributed connection handling across multiple instances
- **Health Monitoring**: Continuous connection health checks and recovery

### 2. Message Processing
- **Queue Optimization**: Priority-based message processing
- **Batch Processing**: Efficient bulk message handling
- **Dead Letter Handling**: Automatic failed message recovery

### 3. Notification Delivery
- **Rate Limiting**: Configurable delivery rate limits per channel
- **Template Caching**: Notification template caching for performance
- **Delivery Optimization**: Intelligent delivery timing and batching

### 4. Real-time Collaboration
- **Event Batching**: Efficient real-time event processing
- **State Synchronization**: Optimized collaboration state management
- **File Handling**: Efficient large file sharing and versioning

### 5. Streaming Performance
- **Multi-platform Optimization**: Simultaneous platform streaming
- **Quality Adaptation**: Dynamic quality adjustment based on bandwidth
- **Analytics Processing**: Real-time viewer and engagement analytics

## Security Features

### 1. Authentication & Authorization
- **JWT Integration**: Secure token-based authentication
- **Role-based Access**: Granular permission management
- **Session Management**: Secure session handling and expiration

### 2. Content Protection
- **Encryption**: Message and content encryption in transit and at rest
- **Fingerprinting**: Real-time content fingerprinting for protection
- **Access Control**: Fine-grained content access permissions

### 3. Monitoring & Auditing
- **Activity Logging**: Comprehensive activity and security logging
- **Intrusion Detection**: Automated suspicious activity detection
- **Compliance**: GDPR and data protection compliance features

## Error Handling & Recovery

### 1. Connection Recovery
```python
# Automatic connection recovery
async def handle_connection_loss(connection_id: str):
    try:
        await websocket_manager.reconnect(connection_id)
    except Exception as e:
        await websocket_manager.cleanup_connection(connection_id)
        logger.error(f"Connection recovery failed: {e}")
```

### 2. Message Delivery Retry
```python
# Automatic message retry with exponential backoff
async def retry_failed_message(message_id: str):
    message = await message_broker.get_failed_message(message_id)
    if message.retry_count < message.max_retries:
        delay = min(300, 2 ** message.retry_count)
        await message_broker.schedule_retry(message_id, delay)
    else:
        await message_broker.move_to_dlq(message_id)
```

### 3. Stream Recovery
```python
# Stream interruption recovery
async def handle_stream_interruption(session_id: str):
    try:
        await streaming_coordinator.restart_stream(session_id)
    except Exception as e:
        await streaming_coordinator.emergency_stop(session_id)
        await notify_stream_failure(session_id)
```

## Monitoring & Metrics

### 1. Real-time Metrics
- **Connection Count**: Active WebSocket connections
- **Message Throughput**: Messages per second processing
- **Notification Delivery**: Success/failure rates per channel
- **Collaboration Activity**: Room activity and participant engagement
- **Stream Performance**: Viewer counts, quality metrics, platform health

### 2. Health Checks
```python
async def health_check():
    health = await comm_service.health_check()
    return {
        "status": health["status"],
        "components": health["components"],
        "timestamp": datetime.now().isoformat()
    }
```

### 3. Performance Analytics
- **Response Times**: API and service response time monitoring
- **Resource Usage**: Memory, CPU, and bandwidth utilization
- **Error Rates**: Component-wise error rate tracking
- **User Engagement**: Creator collaboration and streaming engagement metrics

## Testing Strategies

### 1. Unit Testing
```python
# Component testing
async def test_notification_engine():
    engine = NotificationEngine(mock_redis, mock_db)
    await engine.initialize()
    
    result = await engine.send_notification(
        user_id="test_user",
        template_key="test_template",
        variables={"name": "Test User"}
    )
    
    assert result is not None
    assert isinstance(result, str)
```

### 2. Integration Testing
```python
# Service integration testing
async def test_collaboration_workflow():
    async with get_communication_service(test_redis, test_db) as service:
        room_id = await service.live_collaboration.create_room(
            owner_id="owner123",
            name="Test Room",
            collaboration_type=CollaborationType.CONTENT_CREATION
        )
        
        success = await service.live_collaboration.join_room(
            room_id=room_id,
            user_id="collaborator456",
            role=ParticipantRole.COLLABORATOR
        )
        
        assert success is True
```

### 3. Load Testing
- **Connection Load**: Test concurrent WebSocket connections
- **Message Volume**: Test high-volume message processing
- **Notification Burst**: Test bulk notification delivery
- **Streaming Load**: Test multi-platform streaming performance

---

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Project:** IA Influencer Agent + Content Protection Platform  
**Module:** Communication Database Infrastructure  

This documentation provides comprehensive guidance for developers working with the Communication module, ensuring proper integration, optimal performance, and robust error handling.
