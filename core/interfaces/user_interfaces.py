"""User management interfaces for IA Influencer Agent.

Defines interfaces for user management, preferences, collaboration,
security and analytics functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
(c) 2025 - All rights reserved. Unauthorized use prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """
User roles in the system."""

    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    MANAGER = "manager"
    ADMIN = "admin"
    VIEWER = "viewer"
    MODERATOR = "moderator"
    ANALYST = "analyst"
    INVESTOR = "investor"


class AccountStatus(Enum):
    """User account status."""

    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    VERIFIED = "verified"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"


class PreferenceCategory(Enum):
    """User preference categories."""

    NOTIFICATION = "notification"
    PRIVACY = "privacy"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PLATFORM = "platform"
    ANALYTICS = "analytics"


class PrivacyLevel(Enum):
    """User privacy levels."""

    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    CUSTOM = "custom"
    COLLABORATORS_ONLY = "collaborators_only"


class UserManagerInterface(ABC):
    """Core interface for user management operations."""
    
    @abstractmethod
    async def create_user_profile(
        self,
        user_data: Dict[str, Any],
        initial_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new user profile.
        
        Args:
            user_data: User registration data
            initial_preferences: Initial user preferences
            
        Returns:
            Created user profile with ID and status
        """
        pass
    
    @abstractmethod
    async def update_user_profile(
        self,
        user_id: str,
        profile_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Update user profile information."""
        pass
    
    @abstractmethod
    async def get_user_profile(
        self,
        user_id: str,
        include_private: bool = False
    ) -> Dict[str, Any]:
        """
Retrieve user profile data."""
        pass
    
    @abstractmethod
    async def delete_user_account(
        self,
        user_id: str,
        deletion_reason: str
    ) -> bool:
        """
Permanently delete user account and data."""
        pass
    
    @abstractmethod
    async def suspend_user_account(
        self,
        user_id: str,
        suspension_reason: str,
        duration: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
Suspend user account temporarily."""
        pass
    
    @abstractmethod
    async def verify_user_identity(
        self,
        user_id: str,
        verification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Verify user identity for enhanced features."""
        pass


class UserPreferencesInterface(ABC):
    """
Interface for user preferences management."""
    
    @abstractmethod
    async def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Set user preferences and configuration.
        
        Args:
            user_id: User identifier
            preferences: User preferences dictionary
            
        Returns:
            Success status of preference update
        """
        pass
    
    @abstractmethod
    async def get_user_preferences(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Get user preferences, optionally filtered by category."""
        pass
    
    @abstractmethod
    async def update_notification_settings(
        self,
        user_id: str,
        notification_config: Dict[str, bool]
    ) -> bool:
        """
Update user notification preferences."""
        pass
    
    @abstractmethod
    async def set_privacy_settings(
        self,
        user_id: str,
        privacy_config: Dict[str, PrivacyLevel]
    ) -> bool:
        """
Configure user privacy settings."""
        pass
    
    @abstractmethod
    async def manage_content_preferences(
        self,
        user_id: str,
        content_preferences: Dict[str, Any]
    ) -> bool:
        """
Manage content creation and consumption preferences."""
        pass
    
    @abstractmethod
    async def set_collaboration_preferences(
        self,
        user_id: str,
        collaboration_settings: Dict[str, Any]
    ) -> bool:
        """
Set preferences for collaboration features."""
        pass


class UserCollaborationInterface(ABC):
    """
Interface for user collaboration management."""
    
    @abstractmethod
    async def create_collaboration_request(
        self,
        requester_id: str,
        target_user_id: str,
        collaboration_details: Dict[str, Any]
    ) -> str:
        """
        Create collaboration request between users.
        
        Args:
            requester_id: User sending the request
            target_user_id: User receiving the request
            collaboration_details: Details of proposed collaboration
            
        Returns:
            Collaboration request ID
        """
        pass
    
    @abstractmethod
    async def respond_to_collaboration(
        self,
        request_id: str,
        user_id: str,
        response: str,
        response_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Respond to collaboration request (accept/decline)."""
        pass
    
    @abstractmethod
    async def get_collaboration_history(
        self,
        user_id: str,
        include_pending: bool = True
    ) -> List[Dict[str, Any]]:
        """
Get user's collaboration history and active projects."""
        pass
    
    @abstractmethod
    async def find_collaboration_matches(
        self,
        user_id: str,
        collaboration_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
Find potential collaboration partners based on criteria."""
        pass
    
    @abstractmethod
    async def manage_collaboration_terms(
        self,
        collaboration_id: str,
        user_id: str,
        terms: Dict[str, Any]
    ) -> bool:
        """
Manage terms and conditions for collaboration."""
        pass


class UserSecurityInterface(ABC):
    """
Interface for user security management."""
    
    @abstractmethod
    async def setup_two_factor_auth(
        self,
        user_id: str,
        auth_method: str
    ) -> Dict[str, Any]:
        """
        Setup two-factor authentication for user.
        
        Args:
            user_id: User identifier
            auth_method: 2FA method (sms, email, app, hardware)
            
        Returns:
            2FA setup information and backup codes
        """
        pass
    
    @abstractmethod
    async def verify_two_factor_code(
        self,
        user_id: str,
        verification_code: str
    ) -> bool:
        """
Verify two-factor authentication code."""
        pass
    
    @abstractmethod
    async def generate_recovery_codes(
        self,
        user_id: str
    ) -> List[str]:
        """
Generate account recovery codes for user."""
        pass
    
    @abstractmethod
    async def audit_user_sessions(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
Audit active and recent user sessions."""
        pass
    
    @abstractmethod
    async def revoke_user_sessions(
        self,
        user_id: str,
        session_ids: Optional[List[str]] = None
    ) -> bool:
        """
Revoke user sessions (all or specific)."""
        pass
    
    @abstractmethod
    async def check_security_threats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
Check for security threats to user account."""
        pass


class UserAnalyticsInterface(ABC):
    """
Interface for user analytics and insights."""
    
    @abstractmethod
    async def get_user_activity_analytics(
        self,
        user_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Get user activity analytics.
        
        Args:
            user_id: User identifier
            timeframe: Analysis timeframe (day, week, month, year)
            
        Returns:
            User activity analytics and insights
        """
        pass
    
    @abstractmethod
    async def analyze_content_performance(
        self,
        user_id: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """
Analyze performance of user's content portfolio."""
        pass
    
    @abstractmethod
    async def track_collaboration_success(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
Track success metrics of user's collaborations."""
        pass
    
    @abstractmethod
    async def generate_growth_insights(
        self,
        user_id: str,
        focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """
Generate personalized growth insights and recommendations."""
        pass
    
    @abstractmethod
    async def predict_user_engagement(
        self,
        user_id: str,
        content_features: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Predict user engagement with different content types."""
        pass
    
    @abstractmethod
    async def benchmark_user_performance(
        self,
        user_id: str,
        comparison_group: str
    ) -> Dict[str, Any]:
        """
Benchmark user performance against similar creators."""
        pass
