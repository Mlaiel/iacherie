"""Platform integration interfaces for IA Influencer Agent.

Defines interfaces for multi-platform connectivity, authentication,
data synchronization, distribution and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum


class PlatformType(Enum):
    """Supported platform types for integration."""    MUSIC_STREAMING = "music_streaming"  # Spotify, Apple Music, etc.
    VIDEO_SHARING = "video_sharing"      # YouTube, TikTok, etc.
    SOCIAL_MEDIA = "social_media"        # Instagram, Twitter, etc.
    CONTENT_CREATION = "content_creation" # Canva, Adobe, etc.
    MARKETPLACE = "marketplace"          # Etsy, Amazon, etc.
    COLLABORATION = "collaboration"      # Discord, Slack, etc.


class AuthMethod(Enum):
    """Authentication methods for platform integration."""    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


class PlatformConnectorInterface(ABC):
    """Core interface for platform connectivity."""    
    @abstractmethod
    async def connect_platform(
        self,
        platform_name: str,
        user_id: str,
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Connect user account to external platform.
        
        Args:
            platform_name: Name of platform to connect
            user_id: User identifier
            credentials: Platform authentication credentials
            
        Returns:
            Connection status and configuration
        """        pass
    
    @abstractmethod
    async def disconnect_platform(
        self,
        platform_name: str,
        user_id: str
    ) -> bool:
        """Disconnect user account from platform."""        pass
    
    @abstractmethod
    async def test_platform_connection(
        self,
        platform_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Test platform connection health and permissions."""        pass
    
    @abstractmethod
    async def get_connected_platforms(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get list of user's connected platforms."""        pass
    
    @abstractmethod
    async def refresh_platform_tokens(
        self,
        platform_name: str,
        user_id: str
    ) -> bool:
        """Refresh expired authentication tokens."""        pass


class PlatformAuthInterface(ABC):
    """Interface for platform authentication management."""    
    @abstractmethod
    async def initiate_oauth_flow(
        self,
        platform_name: str,
        user_id: str,
        callback_url: str
    ) -> str:
        """        Initiate OAuth authentication flow.
        
        Args:
            platform_name: Platform to authenticate with
            user_id: User identifier
            callback_url: OAuth callback URL
            
        Returns:
            Authorization URL for user redirection
        """        pass
    
    @abstractmethod
    async def handle_oauth_callback(
        self,
        platform_name: str,
        user_id: str,
        authorization_code: str
    ) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens."""        pass
    
    @abstractmethod
    async def store_platform_credentials(
        self,
        platform_name: str,
        user_id: str,
        credentials: Dict[str, Any],
        encryption_key: str
    ) -> bool:
        """Securely store platform credentials."""        pass
    
    @abstractmethod
    async def retrieve_platform_credentials(
        self,
        platform_name: str,
        user_id: str,
        encryption_key: str
    ) -> Dict[str, Any]:
        """Retrieve and decrypt platform credentials."""        pass
    
    @abstractmethod
    async def validate_platform_permissions(
        self,
        platform_name: str,
        user_id: str,
        required_scopes: List[str]
    ) -> Dict[str, bool]:
        """Validate platform permissions and scopes."""        pass


class PlatformDataInterface(ABC):
    """Interface for platform data synchronization."""    
    @abstractmethod
    async def sync_platform_data(
        self,
        platform_name: str,
        user_id: str,
        data_types: List[str]
    ) -> Dict[str, Any]:
        """        Synchronize data from platform.
        
        Args:
            platform_name: Platform to sync from
            user_id: User identifier
            data_types: Types of data to synchronize
            
        Returns:
            Synchronization results and status
        """        pass
    
    @abstractmethod
    async def fetch_user_profile(
        self,
        platform_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Fetch user profile data from platform."""        pass
    
    @abstractmethod
    async def fetch_content_analytics(
        self,
        platform_name: str,
        user_id: str,
        content_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Fetch content analytics from platform."""        pass
    
    @abstractmethod
    async def fetch_audience_insights(
        self,
        platform_name: str,
        user_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Fetch audience insights and demographics."""        pass
    
    @abstractmethod
    async def sync_content_metadata(
        self,
        platform_name: str,
        user_id: str,
        content_list: List[str]
    ) -> List[Dict[str, Any]]:
        """Sync metadata for multiple content items."""        pass


class PlatformDistributionInterface(ABC):
    """Interface for multi-platform content distribution."""    
    @abstractmethod
    async def distribute_content(
        self,
        content_id: str,
        platforms: List[str],
        distribution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Distribute content to multiple platforms.
        
        Args:
            content_id: Content identifier
            platforms: List of target platforms
            distribution_config: Distribution configuration
            
        Returns:
            Distribution results and status per platform
        """        pass
    
    @abstractmethod
    async def schedule_content_release(
        self,
        content_id: str,
        platforms: List[str],
        schedule: Dict[str, datetime]
    ) -> str:
        """Schedule content release across platforms."""        pass
    
    @abstractmethod
    async def update_content_metadata(
        self,
        platform_name: str,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update content metadata on specific platform."""        pass
    
    @abstractmethod
    async def monitor_distribution_status(
        self,
        distribution_id: str
    ) -> Dict[str, Any]:
        """Monitor status of content distribution."""        pass
    
    @abstractmethod
    async def optimize_platform_settings(
        self,
        platform_name: str,
        content_type: str,
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize platform-specific settings for content."""        pass


class PlatformMonetizationInterface(ABC):
    """Interface for platform monetization management."""    
    @abstractmethod
    async def fetch_revenue_data(
        self,
        platform_name: str,
        user_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """        Fetch revenue data from platform.
        
        Args:
            platform_name: Platform to fetch from
            user_id: User identifier
            timeframe: Time period for revenue data
            
        Returns:
            Revenue data and analytics
        """        pass
    
    @abstractmethod
    async def setup_monetization(
        self,
        platform_name: str,
        user_id: str,
        monetization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Setup monetization features on platform."""        pass
    
    @abstractmethod
    async def track_content_earnings(
        self,
        platform_name: str,
        content_id: str,
        timeframe: str
    ) -> Dict[str, float]:
        """Track earnings for specific content."""        pass
    
    @abstractmethod
    async def optimize_monetization_strategy(
        self,
        platform_name: str,
        user_id: str,
        performance_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate monetization optimization recommendations."""        pass
    
    @abstractmethod
    async def calculate_roi_metrics(
        self,
        platform_name: str,
        user_id: str,
        investment_data: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate return on investment metrics."""        pass
    
    @abstractmethod
    async def setup_revenue_sharing(
        self,
        platform_name: str,
        collaboration_id: str,
        sharing_terms: Dict[str, Any]
    ) -> str:
        """Setup automated revenue sharing for collaborations."""        pass
