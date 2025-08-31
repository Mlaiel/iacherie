"""Data Models Index - IA Influencer Agent Platform
Main entry point for all data models and schemas

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# Domain models
from .domain import (
    User,
    Creator,
    Content,
    MediaFile,
    Copyright,
    License,
    Collaboration,
    Project,
    Revenue,
    Distribution,
    Analytics,
    Notification
)

# Database models
from .database_models import (
    UserModel,
    CreatorModel,
    ContentModel,
    MediaFileModel,
    CopyrightModel,
    LicenseModel,
    CollaborationModel,
    ProjectModel,
    RevenueModel,
    DistributionModel,
    AnalyticsModel,
    NotificationModel
)

# API response models
from .api_models import (
    UserResponse,
    CreatorResponse,
    ContentResponse,
    MediaResponse,
    CopyrightResponse,
    LicenseResponse,
    CollaborationResponse,
    ProjectResponse,
    RevenueResponse,
    DistributionResponse,
    AnalyticsResponse,
    NotificationResponse
)

# Request models
from .request_models import (
    UserCreateRequest,
    UserUpdateRequest,
    ContentCreateRequest,
    ContentUpdateRequest,
    CollaborationCreateRequest,
    ProjectCreateRequest,
    LicenseCreateRequest,
    DistributionCreateRequest
)

# Base models and mixins
from .base import (
    BaseModel,
    TimestampMixin,
    UUIDMixin,
    AuditMixin,
    SoftDeleteMixin
)

# Model validators
from .validators import (
    EmailValidator,
    PasswordValidator,
    ContentValidator,
    MediaValidator,
    MetadataValidator,
    LicenseValidator
)

# Model factories
from .factories import (
    UserFactory,
    CreatorFactory,
    ContentFactory,
    MediaFactory,
    CollaborationFactory,
    ProjectFactory
)


def get_user_models():
    """Get all user-related models"""
    return {
        'domain': User,
        'database': UserModel,
        'response': UserResponse,
        'create_request': UserCreateRequest,
        'update_request': UserUpdateRequest,
        'factory': UserFactory
    }


def get_creator_models():
    """Get all creator-related models"""
    return {
        'domain': Creator,
        'database': CreatorModel,
        'response': CreatorResponse,
        'factory': CreatorFactory
    }


def get_content_models():
    """Get all content-related models"""
    return {
        'domain': Content,
        'database': ContentModel,
        'response': ContentResponse,
        'create_request': ContentCreateRequest,
        'update_request': ContentUpdateRequest,
        'factory': ContentFactory
    }


def get_media_models():
    """Get all media-related models"""
    return {
        'domain': MediaFile,
        'database': MediaFileModel,
        'response': MediaResponse,
        'factory': MediaFactory
    }


def get_collaboration_models():
    """Get all collaboration-related models"""
    return {
        'domain': Collaboration,
        'database': CollaborationModel,
        'response': CollaborationResponse,
        'create_request': CollaborationCreateRequest,
        'factory': CollaborationFactory
    }


def get_project_models():
    """Get all project-related models"""
    return {
        'domain': Project,
        'database': ProjectModel,
        'response': ProjectResponse,
        'create_request': ProjectCreateRequest,
        'factory': ProjectFactory
    }


def get_copyright_models():
    """Get all copyright-related models"""
    return {
        'domain': Copyright,
        'database': CopyrightModel,
        'response': CopyrightResponse
    }


def get_license_models():
    """Get all license-related models"""
    return {
        'domain': License,
        'database': LicenseModel,
        'response': LicenseResponse,
        'create_request': LicenseCreateRequest
    }


def get_revenue_models():
    """Get all revenue-related models"""
    return {
        'domain': Revenue,
        'database': RevenueModel,
        'response': RevenueResponse
    }


def get_distribution_models():
    """Get all distribution-related models"""
    return {
        'domain': Distribution,
        'database': DistributionModel,
        'response': DistributionResponse,
        'create_request': DistributionCreateRequest
    }


def get_all_models_by_category():
    """Get all models organized by category"""
    return {
        'user': get_user_models(),
        'creator': get_creator_models(),
        'content': get_content_models(),
        'media': get_media_models(),
        'collaboration': get_collaboration_models(),
        'project': get_project_models(),
        'copyright': get_copyright_models(),
        'license': get_license_models(),
        'revenue': get_revenue_models(),
        'distribution': get_distribution_models()
    }


__all__ = [
    # Domain Models
    'User',
    'Creator',
    'Content',
    'MediaFile',
    'Copyright',
    'License',
    'Collaboration',
    'Project',
    'Revenue',
    'Distribution',
    'Analytics',
    'Notification',
    
    # Database Models
    'UserModel',
    'CreatorModel',
    'ContentModel',
    'MediaFileModel',
    'CopyrightModel',
    'LicenseModel',
    'CollaborationModel',
    'ProjectModel',
    'RevenueModel',
    'DistributionModel',
    'AnalyticsModel',
    'NotificationModel',
    
    # API Response Models
    'UserResponse',
    'CreatorResponse',
    'ContentResponse',
    'MediaResponse',
    'CopyrightResponse',
    'LicenseResponse',
    'CollaborationResponse',
    'ProjectResponse',
    'RevenueResponse',
    'DistributionResponse',
    'AnalyticsResponse',
    'NotificationResponse',
    
    # Request Models
    'UserCreateRequest',
    'UserUpdateRequest',
    'ContentCreateRequest',
    'ContentUpdateRequest',
    'CollaborationCreateRequest',
    'ProjectCreateRequest',
    'LicenseCreateRequest',
    'DistributionCreateRequest',
    
    # Base Models
    'BaseModel',
    'TimestampMixin',
    'UUIDMixin',
    'AuditMixin',
    'SoftDeleteMixin',
    
    # Validators
    'EmailValidator',
    'PasswordValidator',
    'ContentValidator',
    'MediaValidator',
    'MetadataValidator',
    'LicenseValidator',
    
    # Factories
    'UserFactory',
    'CreatorFactory',
    'ContentFactory',
    'MediaFactory',
    'CollaborationFactory',
    'ProjectFactory',
    
    # Model Collections
    'get_user_models',
    'get_creator_models',
    'get_content_models',
    'get_media_models',
    'get_collaboration_models',
    'get_project_models',
    'get_copyright_models',
    'get_license_models',
    'get_revenue_models',
    'get_distribution_models',
    'get_all_models_by_category'
]
