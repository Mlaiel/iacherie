# Consolidated Models Documentation

## Overview

The `backend/core/models.py` file contains all 39+ data models for the IA Influencer Agent Platform, consolidating previously scattered model definitions into a single, comprehensive module.

## Features

- **39 Comprehensive Models** covering all business domains
- **Type-safe Enumerations** for data consistency  
- **Dynamic Model Registry** for programmatic access
- **Utility Functions** for model management
- **Professional Documentation** with clear structure
- **Full Test Coverage** ensuring reliability

## Usage

### Basic Import

```python
from backend.core.models import *
```

### Creating Models

```python
# Create a user
user = UserModel(
    username="john_creator",
    email="john@example.com",
    user_type=UserType.MUSICIAN,
    subscription_tier=SubscriptionTier.PROFESSIONAL
)

# Create content
content = ContentModel(
    title="My New Track",
    content_type=ContentType.AUDIO,
    creator_id=user.id,
    tags=["music", "original"]
)

# Create analytics
analytics = AnalyticsModel(
    entity_id=content.id,
    entity_type="content",
    metric_type=MetricType.ENGAGEMENT,
    metric_name="views",
    metric_value=1000.0
)
```

### Using Model Registry

```python
# List all available models
models = list_available_models()
print(f"Available models: {len(models)}")  # 39

# Get model class by name
UserModelClass = get_model("user")

# Create instance dynamically
user = create_model("user", username="dynamic_user", email="user@example.com")
```

### Model Conversion

```python
# Convert to dictionary
user_dict = user.to_dict()

# Update timestamp
user.update_timestamp()
```

## Model Categories

### User Models
- `UserModel` - Main user data
- `InfluencerModel` - Influencer-specific data
- `PersonalityModel` - AI personality traits

### Content Models
- `ContentModel` - Main content data
- `PostModel` - Social media posts
- `VideoModel` - Video-specific data
- `ImageModel` - Image-specific data
- `AudioModel` - Audio-specific data
- `VoiceModel` - Voice/speech data

### Financial Models
- `SubscriptionModel` - Subscription management
- `PaymentModel` - Payment processing
- `InvoiceModel` - Invoice generation
- `TransactionModel` - Financial transactions
- `WalletModel` - Digital wallet

### Marketplace Models
- `MarketplaceModel` - Platform marketplace
- `ProductModel` - Products for sale
- `OrderModel` - Purchase orders
- `ReviewModel` - Reviews and ratings
- `RatingModel` - Simple ratings

### Analytics Models
- `AnalyticsModel` - Core analytics
- `MetricsModel` - Metric aggregation
- `EngagementModel` - User engagement
- `GrowthModel` - Growth metrics
- `AudienceModel` - Audience analysis
- `DemographicModel` - Demographic data
- `LocationModel` - Location analytics

### Collaboration Models
- `CollaborationModel` - Creator collaborations
- `CampaignModel` - Marketing campaigns
- `BrandModel` - Brand information
- `SponsorModel` - Sponsorship deals
- `ContractModel` - Legal contracts

### Communication Models
- `NotificationModel` - System notifications
- `MessageModel` - Direct messages
- `ChatModel` - Chat conversations
- `CommentModel` - Content comments

### Social Interaction Models
- `LikeModel` - Likes and reactions
- `ShareModel` - Content sharing
- `FollowModel` - Follow relationships
- `BlockModel` - Blocking/muting

## Enumerations

### User Types
```python
UserType.CREATOR, UserType.ARTIST, UserType.INFLUENCER, UserType.MUSICIAN
```

### Content Types
```python
ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE, ContentType.PODCAST
```

### Payment Methods
```python
PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL, PaymentMethod.CRYPTO
```

### Engagement Types
```python
EngagementType.VIEW, EngagementType.LIKE, EngagementType.SHARE
```

## Migration from Old Models

To migrate from the old scattered model files:

1. **Update imports:**
   ```python
   # Old
   from data_management.models.user_model import UserModel
   from data_management.models.content_model import ContentModel
   
   # New
   from backend.core.models import UserModel, ContentModel
   ```

2. **Use new consolidated location:**
   ```python
   from backend.core.models import *
   ```

## Best Practices

1. **Use type hints** for better IDE support
2. **Leverage enumerations** for data consistency
3. **Use model registry** for dynamic model access
4. **Call update_timestamp()** when modifying models
5. **Convert to dict** when serializing for APIs

## Testing

The models include comprehensive test coverage. Run tests with:

```python
python backend/core/example_usage.py
```

## Support

For questions or issues with the consolidated models, contact:
- Author: Fahed Mlaiel <mlaiel@live.de>
- Repository: Mlaiel/Ainflue