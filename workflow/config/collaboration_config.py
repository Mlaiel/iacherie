"""
🤝 COLLABORATION CONFIGURATION - AINFLUE ENTERPRISE PLATFORM

Ultra-advanced collaboration configuration with real-time features and gamification
Performance Target: < 5ms collaboration setup

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY SOFTWARE - COMMERCIAL USE PROHIBITED WITHOUT LICENSE
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types of collaboration supported"""
    REAL_TIME_EDITING = "real_time_editing"
    ASYNC_COLLABORATION = "async_collaboration"
    REVIEW_WORKFLOW = "review_workflow"
    APPROVAL_PROCESS = "approval_process"
    VERSION_CONTROL = "version_control"
    LIVE_SESSION = "live_session"
    PROJECT_MANAGEMENT = "project_management"

class PermissionLevel(Enum):
    """Permission levels for collaborators"""
    VIEWER = "viewer"
    COMMENTER = "commenter"
    EDITOR = "editor"
    MANAGER = "manager"
    ADMIN = "admin"
    OWNER = "owner"

class WorkspaceType(Enum):
    """Types of collaboration workspaces"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"
    TEAM = "team"
    ORGANIZATION = "organization"

class NotificationType(Enum):
    """Types of collaboration notifications"""
    MENTION = "mention"
    COMMENT = "comment"
    EDIT = "edit"
    APPROVAL_REQUEST = "approval_request"
    DEADLINE_REMINDER = "deadline_reminder"
    MILESTONE_ACHIEVED = "milestone_achieved"
    COLLABORATION_INVITE = "collaboration_invite"

class AchievementType(Enum):
    """Types of achievements in gamification"""
    FIRST_COLLABORATION = "first_collaboration"
    TEAM_PLAYER = "team_player"
    REVIEW_MASTER = "review_master"
    MILESTONE_CRUSHER = "milestone_crusher"
    CREATIVE_GENIUS = "creative_genius"
    MENTOR = "mentor"
    INNOVATOR = "innovator"

@dataclass
class WorkspaceConfig:
    """Configuration for collaboration workspace"""
    workspace_id: str
    name: str
    workspace_type: WorkspaceType
    max_collaborators: int = 50
    real_time_enabled: bool = True
    version_control_enabled: bool = True
    approval_workflow: bool = False
    guest_access_enabled: bool = False
    public_sharing: bool = False

@dataclass
class SharingConfig:
    """Configuration for content sharing"""
    public_sharing_enabled: bool = True
    link_sharing_enabled: bool = True
    password_protection: bool = False
    expiration_enabled: bool = True
    download_permissions: bool = True
    view_tracking: bool = True
    watermark_enabled: bool = False

@dataclass
class GamificationConfig:
    """Configuration for gamification features"""
    enabled: bool = True
    achievements_enabled: bool = True
    leaderboards_enabled: bool = True
    points_system_enabled: bool = True
    badges_enabled: bool = True
    challenges_enabled: bool = True
    team_competitions: bool = True

@dataclass
class CollaboratorProfile:
    """Profile for a collaborator"""
    user_id: str
    username: str
    email: str
    permission_level: PermissionLevel
    joined_at: float
    last_active: float
    contribution_score: int = 0
    achievements: List[str] = field(default_factory=list)
    role: Optional[str] = None

class CollaborationConfig:
    """
    Enterprise collaboration configuration manager
    Performance target: < 5ms collaboration setup
    """
    
    def __init__(self):
        self.workspace_config = WorkspaceConfig(
            workspace_id="default",
            name="Default Workspace",
            workspace_type=WorkspaceType.SHARED
        )
        self.sharing_config = SharingConfig()
        self.gamification_config = GamificationConfig()
        
        # Collaboration data
        self._active_workspaces: Dict[str, WorkspaceConfig] = {}
        self._collaborations: Dict[str, Dict[str, Any]] = {}
        self._real_time_sessions: Dict[str, Dict[str, Any]] = {}
        self._achievements_config: Dict[str, Dict[str, Any]] = {}
        self._leaderboards: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize default configurations
        self._setup_default_achievements()
        self._setup_default_notification_rules()
    
    def _setup_default_achievements(self):
        """Setup default achievement configurations"""
        self._achievements_config = {
            AchievementType.FIRST_COLLABORATION.value: {
                "name": "First Steps",
                "description": "Complete your first collaboration",
                "points": 100,
                "badge_icon": "🤝",
                "requirements": {
                    "collaboration_count": 1
                }
            },
            AchievementType.TEAM_PLAYER.value: {
                "name": "Team Player",
                "description": "Collaborate with 10 different creators",
                "points": 500,
                "badge_icon": "👥",
                "requirements": {
                    "unique_collaborators": 10
                }
            },
            AchievementType.REVIEW_MASTER.value: {
                "name": "Review Master",
                "description": "Complete 50 content reviews",
                "points": 750,
                "badge_icon": "🔍",
                "requirements": {
                    "reviews_completed": 50
                }
            },
            AchievementType.MILESTONE_CRUSHER.value: {
                "name": "Milestone Crusher",
                "description": "Hit 25 project milestones",
                "points": 1000,
                "badge_icon": "🎯",
                "requirements": {
                    "milestones_achieved": 25
                }
            },
            AchievementType.CREATIVE_GENIUS.value: {
                "name": "Creative Genius",
                "description": "Lead 10 successful collaborative projects",
                "points": 1500,
                "badge_icon": "🧠",
                "requirements": {
                    "projects_led": 10,
                    "success_rate": 0.8
                }
            },
            AchievementType.MENTOR.value: {
                "name": "Mentor",
                "description": "Help 5 new creators in their first collaboration",
                "points": 2000,
                "badge_icon": "🌟",
                "requirements": {
                    "mentees_helped": 5
                }
            },
            AchievementType.INNOVATOR.value: {
                "name": "Innovator",
                "description": "Introduce 3 new collaboration features",
                "points": 2500,
                "badge_icon": "💡",
                "requirements": {
                    "features_suggested": 3,
                    "features_implemented": 3
                }
            }
        }
    
    def _setup_default_notification_rules(self):
        """Setup default notification rules"""
        self._notification_rules = {
            NotificationType.MENTION.value: {
                "enabled": True,
                "real_time": True,
                "email": True,
                "push": True
            },
            NotificationType.COMMENT.value: {
                "enabled": True,
                "real_time": True,
                "email": False,
                "push": True
            },
            NotificationType.EDIT.value: {
                "enabled": True,
                "real_time": True,
                "email": False,
                "push": False
            },
            NotificationType.APPROVAL_REQUEST.value: {
                "enabled": True,
                "real_time": True,
                "email": True,
                "push": True
            },
            NotificationType.DEADLINE_REMINDER.value: {
                "enabled": True,
                "real_time": False,
                "email": True,
                "push": True
            },
            NotificationType.MILESTONE_ACHIEVED.value: {
                "enabled": True,
                "real_time": True,
                "email": True,
                "push": True
            },
            NotificationType.COLLABORATION_INVITE.value: {
                "enabled": True,
                "real_time": True,
                "email": True,
                "push": True
            }
        }
    
    async def configure_collaboration_workflows(self, creator_id: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure collaboration workflows for creator"""
        start_time = time.time()
        
        try:
            collaboration_setup = {
                "creator_id": creator_id,
                "workflow_id": f"workflow_{creator_id}_{int(time.time())}",
                "configuration": {
                    "real_time_collaboration": workflow_config.get("real_time", True),
                    "async_collaboration": workflow_config.get("async", True),
                    "review_workflow": workflow_config.get("review_workflow", True),
                    "approval_process": workflow_config.get("approval_process", False),
                    "version_control": workflow_config.get("version_control", True),
                    "max_collaborators": workflow_config.get("max_collaborators", 10)
                },
                "permissions": {
                    "default_permission": PermissionLevel.EDITOR.value,
                    "guest_access": workflow_config.get("guest_access", False),
                    "public_sharing": workflow_config.get("public_sharing", True)
                },
                "notification_settings": self._notification_rules.copy(),
                "gamification": {
                    "enabled": workflow_config.get("gamification", True),
                    "points_system": True,
                    "achievements": True,
                    "leaderboards": True
                },
                "created_at": time.time(),
                "status": "active"
            }
            
            # Store collaboration configuration
            self._collaborations[creator_id] = collaboration_setup
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Collaboration workflow configured for creator {creator_id} in {elapsed:.2f}ms")
            return collaboration_setup
            
        except Exception as e:
            logger.error(f"Failed to configure collaboration workflow: {e}")
            raise
    
    async def setup_shared_workspaces(self, workspace_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup shared workspaces for collaboration"""
        start_time = time.time()
        
        try:
            workspace_id = workspace_config.get("workspace_id", str(uuid.uuid4()))
            
            workspace = WorkspaceConfig(
                workspace_id=workspace_id,
                name=workspace_config.get("name", f"Workspace {workspace_id[:8]}"),
                workspace_type=WorkspaceType(workspace_config.get("type", "shared")),
                max_collaborators=workspace_config.get("max_collaborators", 50),
                real_time_enabled=workspace_config.get("real_time", True),
                version_control_enabled=workspace_config.get("version_control", True),
                approval_workflow=workspace_config.get("approval_workflow", False),
                guest_access_enabled=workspace_config.get("guest_access", False),
                public_sharing=workspace_config.get("public_sharing", False)
            )
            
            # Store workspace configuration
            self._active_workspaces[workspace_id] = workspace
            
            workspace_setup = {
                "workspace_id": workspace_id,
                "configuration": workspace.__dict__,
                "collaboration_features": {
                    "real_time_editing": workspace.real_time_enabled,
                    "version_history": workspace.version_control_enabled,
                    "comment_system": True,
                    "file_sharing": True,
                    "screen_sharing": workspace.real_time_enabled,
                    "video_chat": workspace.real_time_enabled
                },
                "security": {
                    "access_control": True,
                    "audit_logging": True,
                    "data_encryption": True,
                    "backup_enabled": True
                },
                "integrations": {
                    "calendar_sync": True,
                    "task_management": True,
                    "external_tools": True
                },
                "created_at": time.time(),
                "status": "active"
            }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Shared workspace {workspace_id} setup in {elapsed:.2f}ms")
            return workspace_setup
            
        except Exception as e:
            logger.error(f"Failed to setup shared workspace: {e}")
            raise
    
    async def collaboration_security_config(self, workspace_id: str) -> Dict[str, Any]:
        """Configure security for collaboration workspace"""
        start_time = time.time()
        
        try:
            workspace = self._active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            security_config = {
                "workspace_id": workspace_id,
                "access_control": {
                    "permission_matrix": {
                        PermissionLevel.VIEWER.value: ["view", "comment"],
                        PermissionLevel.COMMENTER.value: ["view", "comment"],
                        PermissionLevel.EDITOR.value: ["view", "comment", "edit", "share"],
                        PermissionLevel.MANAGER.value: ["view", "comment", "edit", "share", "manage_permissions"],
                        PermissionLevel.ADMIN.value: ["view", "comment", "edit", "share", "manage_permissions", "delete"],
                        PermissionLevel.OWNER.value: ["all_permissions"]
                    },
                    "guest_restrictions": {
                        "max_session_duration": 4 * 3600,  # 4 hours
                        "download_disabled": True,
                        "sharing_disabled": True
                    },
                    "ip_restrictions": workspace.workspace_type != WorkspaceType.PUBLIC
                },
                "data_protection": {
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                    "data_loss_prevention": True,
                    "watermarking": workspace.workspace_type == WorkspaceType.PUBLIC
                },
                "audit_and_compliance": {
                    "activity_logging": True,
                    "access_logging": True,
                    "change_tracking": True,
                    "compliance_reporting": True,
                    "data_retention_policy": "2_years"
                },
                "threat_protection": {
                    "malware_scanning": True,
                    "suspicious_activity_detection": True,
                    "brute_force_protection": True,
                    "rate_limiting": True
                },
                "configured_at": time.time()
            }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Collaboration security configured for workspace {workspace_id} in {elapsed:.2f}ms")
            return security_config
            
        except Exception as e:
            logger.error(f"Failed to configure collaboration security: {e}")
            raise
    
    async def real_time_collaboration_setup(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Setup real-time collaboration session"""
        start_time = time.time()
        
        try:
            real_time_session = {
                "session_id": session_id,
                "participants": participants,
                "session_config": {
                    "max_participants": 25,
                    "concurrent_editing": True,
                    "live_cursors": True,
                    "real_time_comments": True,
                    "voice_chat": True,
                    "video_chat": False,
                    "screen_sharing": True
                },
                "features": {
                    "operational_transform": True,  # For conflict resolution
                    "presence_awareness": True,
                    "synchronized_scrolling": True,
                    "collaborative_selection": True,
                    "real_time_notifications": True
                },
                "performance": {
                    "latency_target_ms": 50,
                    "sync_interval_ms": 100,
                    "conflict_resolution": "operational_transform",
                    "bandwidth_optimization": True
                },
                "quality_of_service": {
                    "connection_quality_monitoring": True,
                    "automatic_reconnection": True,
                    "offline_sync": True,
                    "backup_persistence": True
                },
                "created_at": time.time(),
                "status": "active"
            }
            
            # Store session configuration
            self._real_time_sessions[session_id] = real_time_session
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Real-time collaboration session {session_id} setup in {elapsed:.2f}ms")
            return real_time_session
            
        except Exception as e:
            logger.error(f"Failed to setup real-time collaboration: {e}")
            raise
    
    async def collaboration_analytics_config(self, workspace_id: str) -> Dict[str, Any]:
        """Configure analytics for collaboration workspace"""
        start_time = time.time()
        
        try:
            analytics_config = {
                "workspace_id": workspace_id,
                "analytics_enabled": True,
                "metrics_tracking": {
                    "collaboration_metrics": {
                        "active_collaborations": True,
                        "collaboration_duration": True,
                        "participant_engagement": True,
                        "content_contributions": True
                    },
                    "productivity_metrics": {
                        "tasks_completed": True,
                        "milestone_achievements": True,
                        "time_to_completion": True,
                        "efficiency_scores": True
                    },
                    "quality_metrics": {
                        "review_cycles": True,
                        "approval_rates": True,
                        "revision_counts": True,
                        "quality_scores": True
                    },
                    "engagement_metrics": {
                        "session_duration": True,
                        "interaction_frequency": True,
                        "comment_activity": True,
                        "real_time_participation": True
                    }
                },
                "reporting": {
                    "real_time_dashboard": True,
                    "collaboration_reports": True,
                    "productivity_reports": True,
                    "engagement_reports": True,
                    "custom_analytics": True
                },
                "insights": {
                    "collaboration_patterns": True,
                    "peak_activity_times": True,
                    "bottleneck_identification": True,
                    "improvement_recommendations": True
                },
                "configured_at": time.time()
            }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Collaboration analytics configured for workspace {workspace_id} in {elapsed:.2f}ms")
            return analytics_config
            
        except Exception as e:
            logger.error(f"Failed to configure collaboration analytics: {e}")
            raise
    
    async def collaboration_notification_setup(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Setup notification preferences for collaboration"""
        start_time = time.time()
        
        try:
            notification_config = {
                "user_id": user_id,
                "notification_preferences": {},
                "delivery_methods": {
                    "real_time": preferences.get("real_time", True),
                    "email": preferences.get("email", True),
                    "push": preferences.get("push", True),
                    "sms": preferences.get("sms", False)
                },
                "frequency_settings": {
                    "immediate": preferences.get("immediate_notifications", [
                        NotificationType.MENTION.value,
                        NotificationType.APPROVAL_REQUEST.value,
                        NotificationType.COLLABORATION_INVITE.value
                    ]),
                    "digest": preferences.get("digest_notifications", [
                        NotificationType.COMMENT.value,
                        NotificationType.EDIT.value
                    ]),
                    "weekly": preferences.get("weekly_notifications", [
                        NotificationType.MILESTONE_ACHIEVED.value
                    ])
                },
                "quiet_hours": {
                    "enabled": preferences.get("quiet_hours_enabled", True),
                    "start_time": preferences.get("quiet_start", "22:00"),
                    "end_time": preferences.get("quiet_end", "08:00"),
                    "timezone": preferences.get("timezone", "UTC")
                },
                "filters": {
                    "workspace_specific": preferences.get("workspace_filters", {}),
                    "collaboration_specific": preferences.get("collaboration_filters", {}),
                    "priority_only": preferences.get("priority_only", False)
                },
                "configured_at": time.time()
            }
            
            # Setup notification preferences for each type
            for notification_type in NotificationType:
                type_key = notification_type.value
                user_preference = preferences.get(type_key, {})
                
                notification_config["notification_preferences"][type_key] = {
                    "enabled": user_preference.get("enabled", True),
                    "real_time": user_preference.get("real_time", True),
                    "email": user_preference.get("email", False),
                    "push": user_preference.get("push", True)
                }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Collaboration notifications setup for user {user_id} in {elapsed:.2f}ms")
            return notification_config
            
        except Exception as e:
            logger.error(f"Failed to setup collaboration notifications: {e}")
            raise
    
    async def collaboration_access_control(self, workspace_id: str, access_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Configure access control for collaboration workspace"""
        start_time = time.time()
        
        try:
            workspace = self._active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            access_control_config = {
                "workspace_id": workspace_id,
                "access_rules": access_rules,
                "permission_management": {
                    "role_based_access": True,
                    "granular_permissions": True,
                    "permission_inheritance": True,
                    "temporary_permissions": True
                },
                "authentication": {
                    "multi_factor_auth": access_rules.get("mfa_required", False),
                    "sso_enabled": access_rules.get("sso_enabled", False),
                    "session_timeout": access_rules.get("session_timeout", 8 * 3600)  # 8 hours
                },
                "authorization_matrix": {
                    "resource_permissions": {
                        "documents": access_rules.get("document_permissions", {}),
                        "media_files": access_rules.get("media_permissions", {}),
                        "comments": access_rules.get("comment_permissions", {}),
                        "workspace_settings": access_rules.get("workspace_permissions", {})
                    },
                    "action_permissions": {
                        "create": access_rules.get("create_permissions", []),
                        "read": access_rules.get("read_permissions", []),
                        "update": access_rules.get("update_permissions", []),
                        "delete": access_rules.get("delete_permissions", []),
                        "share": access_rules.get("share_permissions", [])
                    }
                },
                "restrictions": {
                    "ip_whitelist": access_rules.get("ip_whitelist", []),
                    "time_based_access": access_rules.get("time_restrictions", {}),
                    "device_restrictions": access_rules.get("device_restrictions", {}),
                    "geographic_restrictions": access_rules.get("geo_restrictions", [])
                },
                "configured_at": time.time()
            }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Access control configured for workspace {workspace_id} in {elapsed:.2f}ms")
            return access_control_config
            
        except Exception as e:
            logger.error(f"Failed to configure collaboration access control: {e}")
            raise
    
    async def setup_gamification_system(self, workspace_id: str) -> Dict[str, Any]:
        """Setup gamification system for collaboration"""
        start_time = time.time()
        
        try:
            gamification_setup = {
                "workspace_id": workspace_id,
                "gamification_enabled": self.gamification_config.enabled,
                "points_system": {
                    "enabled": self.gamification_config.points_system_enabled,
                    "point_values": {
                        "create_content": 10,
                        "collaborate": 15,
                        "provide_feedback": 5,
                        "complete_review": 20,
                        "achieve_milestone": 50,
                        "help_teammate": 25,
                        "innovative_idea": 30
                    },
                    "bonus_multipliers": {
                        "quality_bonus": 1.5,
                        "speed_bonus": 1.2,
                        "collaboration_bonus": 1.3,
                        "innovation_bonus": 2.0
                    }
                },
                "achievements_system": {
                    "enabled": self.gamification_config.achievements_enabled,
                    "available_achievements": self._achievements_config,
                    "achievement_tracking": True,
                    "progress_notifications": True
                },
                "leaderboards": {
                    "enabled": self.gamification_config.leaderboards_enabled,
                    "leaderboard_types": {
                        "overall_points": True,
                        "collaboration_score": True,
                        "innovation_score": True,
                        "mentor_score": True,
                        "quality_score": True
                    },
                    "update_frequency": "real_time",
                    "reset_frequency": "monthly"
                },
                "badges_system": {
                    "enabled": self.gamification_config.badges_enabled,
                    "badge_categories": {
                        "collaboration": ["Team Player", "Mentor", "Leader"],
                        "quality": ["Quality Master", "Perfectionist", "Reviewer"],
                        "innovation": ["Innovator", "Creative Genius", "Trendsetter"],
                        "productivity": ["Speed Demon", "Milestone Crusher", "Efficient"]
                    }
                },
                "challenges": {
                    "enabled": self.gamification_config.challenges_enabled,
                    "challenge_types": {
                        "individual": True,
                        "team": True,
                        "workspace": True,
                        "organization": True
                    },
                    "challenge_frequency": "weekly"
                },
                "configured_at": time.time()
            }
            
            # Initialize leaderboard for workspace
            self._leaderboards[workspace_id] = []
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Gamification system setup for workspace {workspace_id} in {elapsed:.2f}ms")
            return gamification_setup
            
        except Exception as e:
            logger.error(f"Failed to setup gamification system: {e}")
            raise
    
    def add_collaborator(self, workspace_id: str, user_id: str, permission_level: PermissionLevel) -> bool:
        """Add collaborator to workspace"""
        workspace = self._active_workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Check if workspace has space for more collaborators
        current_collaborators = len(self.get_workspace_collaborators(workspace_id))
        if current_collaborators >= workspace.max_collaborators:
            return False
        
        # Add collaborator logic would go here
        return True
    
    def remove_collaborator(self, workspace_id: str, user_id: str) -> bool:
        """Remove collaborator from workspace"""
        workspace = self._active_workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Remove collaborator logic would go here
        return True
    
    def get_workspace_collaborators(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get list of collaborators for workspace"""
        # Would return actual collaborators from database
        return []
    
    def get_collaboration_status(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get collaboration status for creator"""
        return self._collaborations.get(creator_id)
    
    def get_active_sessions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get active real-time sessions for workspace"""
        return [
            session for session_id, session in self._real_time_sessions.items()
            if session.get("workspace_id") == workspace_id and session.get("status") == "active"
        ]
    
    def calculate_collaboration_score(self, user_id: str) -> int:
        """Calculate collaboration score for user"""
        # Would calculate based on actual collaboration data
        return 0
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements for user"""
        # Would return actual achievements from database
        return []

# Global collaboration configuration instance
collaboration_config = CollaborationConfig()

__all__ = [
    'CollaborationConfig',
    'CollaborationType',
    'PermissionLevel',
    'WorkspaceType',
    'NotificationType',
    'AchievementType',
    'WorkspaceConfig',
    'SharingConfig',
    'GamificationConfig',
    'CollaboratorProfile',
    'collaboration_config'
]