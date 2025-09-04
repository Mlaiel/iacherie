"""Example usage of the consolidated models

This example demonstrates how to use the new consolidated models from backend.core.models
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.models import *
from datetime import datetime
from decimal import Decimal

def example_usage():
    """Demonstrate usage of the consolidated models"""
    
    print("🎯 Consolidated Models Usage Example")
    print("=" * 50)
    
    # Create a user
    user = UserModel(
        username="john_musician",
        email="john@example.com",
        user_type=UserType.MUSICIAN,
        subscription_tier=SubscriptionTier.PROFESSIONAL
    )
    print(f"✅ Created user: {user.username} ({user.user_type.value})")
    
    # Create content
    content = ContentModel(
        title="My New Song",
        description="Latest acoustic track",
        content_type=ContentType.AUDIO,
        creator_id=user.id,
        creator_username=user.username,
        tags=["acoustic", "indie", "original"]
    )
    print(f"✅ Created content: {content.title} ({content.content_type.value})")
    
    # Create a collaboration
    collaboration = CollaborationModel(
        initiator_id=user.id,
        collaborator_id="other_user_id",
        project_title="Collaborative Album",
        revenue_split={"initiator": 0.6, "collaborator": 0.4}
    )
    print(f"✅ Created collaboration: {collaboration.project_title}")
    
    # Create analytics
    analytics = AnalyticsModel(
        entity_id=content.id,
        entity_type="content",
        metric_type=MetricType.ENGAGEMENT,
        metric_name="views",
        metric_value=1500.0
    )
    print(f"✅ Created analytics: {analytics.metric_name} = {analytics.metric_value}")
    
    # Create payment
    payment = PaymentModel(
        user_id=user.id,
        amount=Decimal('29.99'),
        payment_method=PaymentMethod.CREDIT_CARD,
        status=PaymentStatus.COMPLETED
    )
    print(f"✅ Created payment: {payment.amount} {payment.currency}")
    
    # Show model registry usage
    print("\n📚 Model Registry Examples:")
    print(f"Available models: {len(list_available_models())}")
    
    # Create model dynamically
    dynamic_user = create_model("user", username="dynamic_user", email="dynamic@example.com")
    print(f"✅ Created user dynamically: {dynamic_user.username}")
    
    # Get model class
    user_class = get_model("user")
    print(f"✅ Retrieved model class: {user_class.__name__}")
    
    print("\n🎉 All examples completed successfully!")

if __name__ == "__main__":
    example_usage()