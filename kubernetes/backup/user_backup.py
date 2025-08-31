"""User Data Backup Service for IA Influencer Agent Platform.

Handles backup and recovery of all user-related data including profiles,
content uploads, collaboration data, and monetization records.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import json

from ...database.repositories.user_repository import UserRepository
from ...database.repositories.content_repository import ContentRepository
from ...database.repositories.collaboration_repository import CollaborationRepository
from ...monetization.repositories.revenue_repository import RevenueRepository
from ...ai_agents.repositories.agent_repository import AgentRepository


@dataclass
class UserBackupRecord:
    """User backup record metadata."""    user_id: str
    backup_timestamp: datetime
    included_data: List[str]
    record_count: int
    checksum: str
    file_size: int


class UserDataBackupService:
    """    Enterprise user data backup service for IA platform.
    
    Manages backup and recovery of user profiles, content, collaborations,
    monetization data, and AI agent interactions.
    """
    def __init__(self, storage_config: Dict[str, Any]):
        """        Initialize user data backup service.
        
        Args:
            storage_config: Storage configuration
        """        self.logger = logging.getLogger(__name__)
        self.storage_config = storage_config
        
        # Initialize repositories
        self.user_repo = UserRepository()
        self.content_repo = ContentRepository()
        self.collaboration_repo = CollaborationRepository()
        self.revenue_repo = RevenueRepository()
        self.agent_repo = AgentRepository()
        
        # Backup tracking
        self.backup_progress = {}

    async def backup_all_users(self) -> Dict[str, Any]:
        """        Backup all user data across the platform.
        
        Returns:
            Complete user backup data
        """        self.logger.info("Starting complete user data backup...")
        
        backup_data = {
            "user_profiles": {},
            "user_content": {},
            "collaborations": {},
            "monetization_data": {},
            "agent_interactions": {},
            "user_analytics": {},
            "metadata": {
                "backup_timestamp": datetime.now().isoformat(),
                "total_users": 0,
                "backup_version": "2.0.0"
            }
        }
        
        # Get all users
        all_users = await self.user_repo.get_all_users()
        total_users = len(all_users)
        
        self.logger.info(f"Backing up {total_users} user accounts...")
        
        # Backup each user's complete data
        for user in all_users:
            user_id = user["user_id"]
            
            # Backup user profile
            backup_data["user_profiles"][user_id] = await self._backup_user_profile(user_id)
            
            # Backup user content
            backup_data["user_content"][user_id] = await self._backup_user_content(user_id)
            
            # Backup collaborations
            backup_data["collaborations"][user_id] = await self._backup_user_collaborations(user_id)
            
            # Backup monetization data
            backup_data["monetization_data"][user_id] = await self._backup_user_monetization(user_id)
            
            # Backup AI agent interactions
            backup_data["agent_interactions"][user_id] = await self._backup_user_agent_data(user_id)
            
            # Backup user analytics
            backup_data["user_analytics"][user_id] = await self._backup_user_analytics(user_id)
        
        # Update metadata
        backup_data["metadata"]["total_users"] = total_users
        backup_data["metadata"]["total_records"] = await self._calculate_total_records(backup_data)
        
        self.logger.info(f"User data backup completed: {total_users} users")
        return backup_data

    async def backup_changes_since(self, since_date: datetime) -> Dict[str, Any]:
        """        Backup user data changes since specified date.
        
        Args:
            since_date: Date to check for changes
            
        Returns:
            Incremental user backup data
        """        self.logger.info(f"Starting incremental user backup since {since_date}")
        
        backup_data = {
            "user_profiles": {},
            "user_content": {},
            "collaborations": {},
            "monetization_data": {},
            "agent_interactions": {},
            "user_analytics": {},
            "metadata": {
                "backup_timestamp": datetime.now().isoformat(),
                "since_date": since_date.isoformat(),
                "backup_type": "incremental",
                "backup_version": "2.0.0"
            }
        }
        
        # Get users with changes since date
        changed_users = await self.user_repo.get_users_changed_since(since_date)
        
        # Get content changes
        changed_content = await self.content_repo.get_user_content_changes_since(since_date)
        
        # Get collaboration changes
        changed_collaborations = await self.collaboration_repo.get_changes_since(since_date)
        
        # Get monetization changes
        changed_monetization = await self.revenue_repo.get_changes_since(since_date)
        
        # Get agent interaction changes
        changed_agent_data = await self.agent_repo.get_user_interactions_since(since_date)
        
        # Collect all affected user IDs
        affected_user_ids = set()
        
        for user in changed_users:
            affected_user_ids.add(user["user_id"])
        
        for content in changed_content:
            affected_user_ids.add(content["user_id"])
        
        for collab in changed_collaborations:
            affected_user_ids.add(collab["user_id"])
        
        for revenue in changed_monetization:
            affected_user_ids.add(revenue["user_id"])
        
        for interaction in changed_agent_data:
            affected_user_ids.add(interaction["user_id"])
        
        # Backup changes for affected users
        for user_id in affected_user_ids:
            # Check if user profile changed
            user_profile = next((u for u in changed_users if u["user_id"] == user_id), None)
            if user_profile:
                backup_data["user_profiles"][user_id] = await self._backup_user_profile(user_id)
            
            # Check for content changes
            user_content_changes = [c for c in changed_content if c["user_id"] == user_id]
            if user_content_changes:
                backup_data["user_content"][user_id] = await self._backup_user_content_changes(
                    user_id, since_date
                )
            
            # Check for collaboration changes
            user_collab_changes = [c for c in changed_collaborations if c["user_id"] == user_id]
            if user_collab_changes:
                backup_data["collaborations"][user_id] = await self._backup_user_collaboration_changes(
                    user_id, since_date
                )
            
            # Check for monetization changes
            user_revenue_changes = [r for r in changed_monetization if r["user_id"] == user_id]
            if user_revenue_changes:
                backup_data["monetization_data"][user_id] = await self._backup_user_monetization_changes(
                    user_id, since_date
                )
            
            # Check for agent interaction changes
            user_agent_changes = [a for a in changed_agent_data if a["user_id"] == user_id]
            if user_agent_changes:
                backup_data["agent_interactions"][user_id] = await self._backup_user_agent_changes(
                    user_id, since_date
                )
        
        total_affected = len(affected_user_ids)
        backup_data["metadata"]["affected_users"] = total_affected
        backup_data["metadata"]["total_changes"] = await self._calculate_total_records(backup_data)
        
        self.logger.info(f"Incremental user backup completed: {total_affected} users affected")
        return backup_data

    async def restore_users(
        self, 
        backup_data: Dict[str, Any], 
        target_path: Optional[str] = None
    ) -> bool:
        """        Restore user data from backup.
        
        Args:
            backup_data: User backup data to restore
            target_path: Optional target path for restoration
            
        Returns:
            Success status
        """        try:
            self.logger.info("Starting user data restoration...")
            
            # Restore user profiles
            if "user_profiles" in backup_data:
                await self._restore_user_profiles(
                    backup_data["user_profiles"], target_path
                )
            
            # Restore user content
            if "user_content" in backup_data:
                await self._restore_user_content(
                    backup_data["user_content"], target_path
                )
            
            # Restore collaborations
            if "collaborations" in backup_data:
                await self._restore_collaborations(
                    backup_data["collaborations"], target_path
                )
            
            # Restore monetization data
            if "monetization_data" in backup_data:
                await self._restore_monetization_data(
                    backup_data["monetization_data"], target_path
                )
            
            # Restore agent interactions
            if "agent_interactions" in backup_data:
                await self._restore_agent_interactions(
                    backup_data["agent_interactions"], target_path
                )
            
            # Restore user analytics
            if "user_analytics" in backup_data:
                await self._restore_user_analytics(
                    backup_data["user_analytics"], target_path
                )
            
            self.logger.info("User data restoration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"User data restoration failed: {e}")
            return False

    async def backup_specific_user(self, user_id: str) -> Dict[str, Any]:
        """        Backup specific user's complete data.
        
        Args:
            user_id: User identifier
            
        Returns:
            User backup data
        """        self.logger.info(f"Starting backup for user: {user_id}")
        
        user_backup = {
            "user_id": user_id,
            "profile": await self._backup_user_profile(user_id),
            "content": await self._backup_user_content(user_id),
            "collaborations": await self._backup_user_collaborations(user_id),
            "monetization": await self._backup_user_monetization(user_id),
            "agent_interactions": await self._backup_user_agent_data(user_id),
            "analytics": await self._backup_user_analytics(user_id),
            "backup_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"User backup completed: {user_id}")
        return user_backup

    async def _backup_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Backup user profile and account data."""        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            return {}
        
        # Get complete profile data
        profile_data = {
            "basic_info": user_data,
            "preferences": await self.user_repo.get_user_preferences(user_id),
            "settings": await self.user_repo.get_user_settings(user_id),
            "subscriptions": await self.user_repo.get_user_subscriptions(user_id),
            "permissions": await self.user_repo.get_user_permissions(user_id),
            "authentication": await self.user_repo.get_auth_data(user_id),
            "profile_media": await self.user_repo.get_profile_media(user_id)
        }
        
        return profile_data

    async def _backup_user_content(self, user_id: str) -> Dict[str, Any]:
        """Backup all user's content uploads and metadata."""        user_content = await self.content_repo.get_user_content(user_id)
        
        content_backup = {
            "uploaded_content": {},
            "content_metadata": {},
            "protection_status": {},
            "sharing_settings": {}
        }
        
        for content in user_content:
            content_id = content["content_id"]
            
            content_backup["uploaded_content"][content_id] = content
            content_backup["content_metadata"][content_id] = await self.content_repo.get_content_metadata(content_id)
            content_backup["protection_status"][content_id] = await self.content_repo.get_protection_status(content_id)
            content_backup["sharing_settings"][content_id] = await self.content_repo.get_sharing_settings(content_id)
        
        return content_backup

    async def _backup_user_collaborations(self, user_id: str) -> Dict[str, Any]:
        """Backup user's collaboration data."""        collaborations = await self.collaboration_repo.get_user_collaborations(user_id)
        
        collaboration_backup = {
            "active_collaborations": {},
            "collaboration_history": {},
            "collaboration_requests": {},
            "shared_projects": {}
        }
        
        for collab in collaborations:
            collab_id = collab["collaboration_id"]
            
            collaboration_backup["active_collaborations"][collab_id] = collab
            collaboration_backup["collaboration_history"][collab_id] = await self.collaboration_repo.get_collaboration_history(collab_id)
            collaboration_backup["collaboration_requests"][collab_id] = await self.collaboration_repo.get_collaboration_requests(collab_id)
            collaboration_backup["shared_projects"][collab_id] = await self.collaboration_repo.get_shared_projects(collab_id)
        
        return collaboration_backup

    async def _backup_user_monetization(self, user_id: str) -> Dict[str, Any]:
        """Backup user's monetization and revenue data."""        revenue_data = await self.revenue_repo.get_user_revenue_data(user_id)
        
        monetization_backup = {
            "revenue_records": revenue_data,
            "payment_methods": await self.revenue_repo.get_payment_methods(user_id),
            "payout_history": await self.revenue_repo.get_payout_history(user_id),
            "licensing_agreements": await self.revenue_repo.get_licensing_agreements(user_id),
            "revenue_analytics": await self.revenue_repo.get_revenue_analytics(user_id),
            "tax_documents": await self.revenue_repo.get_tax_documents(user_id)
        }
        
        return monetization_backup

    async def _backup_user_agent_data(self, user_id: str) -> Dict[str, Any]:
        """Backup user's AI agent interactions and data."""        agent_interactions = await self.agent_repo.get_user_interactions(user_id)
        
        agent_backup = {
            "interaction_history": agent_interactions,
            "agent_preferences": await self.agent_repo.get_user_agent_preferences(user_id),
            "recommendation_history": await self.agent_repo.get_recommendation_history(user_id),
            "ai_generated_content": await self.agent_repo.get_ai_generated_content(user_id),
            "learning_data": await self.agent_repo.get_user_learning_data(user_id),
            "feedback_data": await self.agent_repo.get_user_feedback_data(user_id)
        }
        
        return agent_backup

    async def _backup_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Backup user's analytics and usage data."""        analytics_data = {
            "usage_statistics": await self.user_repo.get_usage_statistics(user_id),
            "content_performance": await self.content_repo.get_content_performance(user_id),
            "engagement_metrics": await self.user_repo.get_engagement_metrics(user_id),
            "activity_logs": await self.user_repo.get_activity_logs(user_id),
            "platform_interactions": await self.user_repo.get_platform_interactions(user_id)
        }
        
        return analytics_data

    async def _backup_user_content_changes(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Backup user content changes since date."""        changed_content = await self.content_repo.get_user_content_changes_since(
            user_id, since_date
        )
        
        content_changes = {}
        for content in changed_content:
            content_id = content["content_id"]
            content_changes[content_id] = {
                "content_data": content,
                "metadata": await self.content_repo.get_content_metadata(content_id),
                "change_type": content.get("change_type", "unknown"),
                "change_timestamp": content.get("modified_at", datetime.now().isoformat())
            }
        
        return content_changes

    async def _backup_user_collaboration_changes(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Backup user collaboration changes since date."""        changed_collaborations = await self.collaboration_repo.get_user_changes_since(
            user_id, since_date
        )
        
        collaboration_changes = {}
        for collab in changed_collaborations:
            collab_id = collab["collaboration_id"]
            collaboration_changes[collab_id] = {
                "collaboration_data": collab,
                "change_type": collab.get("change_type", "unknown"),
                "change_timestamp": collab.get("modified_at", datetime.now().isoformat())
            }
        
        return collaboration_changes

    async def _backup_user_monetization_changes(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Backup user monetization changes since date."""        changed_revenue = await self.revenue_repo.get_user_changes_since(
            user_id, since_date
        )
        
        monetization_changes = {}
        for revenue in changed_revenue:
            revenue_id = revenue["revenue_id"]
            monetization_changes[revenue_id] = {
                "revenue_data": revenue,
                "change_type": revenue.get("change_type", "unknown"),
                "change_timestamp": revenue.get("modified_at", datetime.now().isoformat())
            }
        
        return monetization_changes

    async def _backup_user_agent_changes(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Backup user agent interaction changes since date."""        changed_interactions = await self.agent_repo.get_user_interactions_since(
            user_id, since_date
        )
        
        agent_changes = {}
        for interaction in changed_interactions:
            interaction_id = interaction["interaction_id"]
            agent_changes[interaction_id] = {
                "interaction_data": interaction,
                "change_type": interaction.get("change_type", "unknown"),
                "change_timestamp": interaction.get("created_at", datetime.now().isoformat())
            }
        
        return agent_changes

    async def _restore_user_profiles(
        self, 
        profile_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore user profiles from backup."""        for user_id, profile in profile_data.items():
            # Restore basic user info
            if "basic_info" in profile:
                await self.user_repo.restore_user(
                    profile["basic_info"], target_path
                )
            
            # Restore preferences
            if "preferences" in profile:
                await self.user_repo.restore_user_preferences(
                    user_id, profile["preferences"], target_path
                )
            
            # Restore settings
            if "settings" in profile:
                await self.user_repo.restore_user_settings(
                    user_id, profile["settings"], target_path
                )
            
            # Restore other profile components
            for key in ["subscriptions", "permissions", "authentication", "profile_media"]:
                if key in profile:
                    await getattr(self.user_repo, f"restore_{key}")(
                        user_id, profile[key], target_path
                    )

    async def _restore_user_content(
        self, 
        content_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore user content from backup."""        for user_id, content in content_data.items():
            for content_type in ["uploaded_content", "content_metadata", "protection_status", "sharing_settings"]:
                if content_type in content:
                    for content_id, content_item in content[content_type].items():
                        await getattr(self.content_repo, f"restore_{content_type}")(
                            content_id, content_item, target_path
                        )

    async def _restore_collaborations(
        self, 
        collaboration_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore collaboration data from backup."""        for user_id, collaborations in collaboration_data.items():
            for collab_type in ["active_collaborations", "collaboration_history", "collaboration_requests", "shared_projects"]:
                if collab_type in collaborations:
                    for collab_id, collab_item in collaborations[collab_type].items():
                        await getattr(self.collaboration_repo, f"restore_{collab_type}")(
                            collab_id, collab_item, target_path
                        )

    async def _restore_monetization_data(
        self, 
        monetization_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore monetization data from backup."""        for user_id, monetization in monetization_data.items():
            for data_type in ["revenue_records", "payment_methods", "payout_history", "licensing_agreements", "revenue_analytics", "tax_documents"]:
                if data_type in monetization:
                    await getattr(self.revenue_repo, f"restore_{data_type}")(
                        user_id, monetization[data_type], target_path
                    )

    async def _restore_agent_interactions(
        self, 
        agent_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore agent interaction data from backup."""        for user_id, interactions in agent_data.items():
            for interaction_type in ["interaction_history", "agent_preferences", "recommendation_history", "ai_generated_content", "learning_data", "feedback_data"]:
                if interaction_type in interactions:
                    await getattr(self.agent_repo, f"restore_{interaction_type}")(
                        user_id, interactions[interaction_type], target_path
                    )

    async def _restore_user_analytics(
        self, 
        analytics_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore user analytics from backup."""        for user_id, analytics in analytics_data.items():
            for analytics_type in ["usage_statistics", "content_performance", "engagement_metrics", "activity_logs", "platform_interactions"]:
                if analytics_type in analytics:
                    await getattr(self.user_repo, f"restore_{analytics_type}")(
                        user_id, analytics[analytics_type], target_path
                    )

    async def _calculate_total_records(self, backup_data: Dict[str, Any]) -> int:
        """Calculate total number of records in backup."""        total = 0
        
        for category in ["user_profiles", "user_content", "collaborations", "monetization_data", "agent_interactions", "user_analytics"]:
            if category in backup_data:
                for user_data in backup_data[category].values():
                    if isinstance(user_data, dict):
                        total += len(user_data)
                    elif isinstance(user_data, list):
                        total += len(user_data)
                    else:
                        total += 1
        
        return total

    def _calculate_user_checksum(self, user_data: Dict[str, Any]) -> str:
        """Calculate checksum for user data."""        user_str = json.dumps(user_data, sort_keys=True, default=str)
        return hashlib.sha256(user_str.encode()).hexdigest()

    async def get_user_backup_size(self, user_id: str) -> Dict[str, Any]:
        """        Calculate estimated backup size for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Size information
        """        size_info = {
            "profile_size": 0,
            "content_size": 0,
            "collaboration_size": 0,
            "monetization_size": 0,
            "agent_interaction_size": 0,
            "analytics_size": 0,
            "total_size": 0
        }
        
        # Estimate profile size
        profile_data = await self._backup_user_profile(user_id)
        size_info["profile_size"] = len(json.dumps(profile_data, default=str))
        
        # Estimate content size
        content_data = await self._backup_user_content(user_id)
        size_info["content_size"] = len(json.dumps(content_data, default=str))
        
        # Estimate other data sizes
        collaboration_data = await self._backup_user_collaborations(user_id)
        size_info["collaboration_size"] = len(json.dumps(collaboration_data, default=str))
        
        monetization_data = await self._backup_user_monetization(user_id)
        size_info["monetization_size"] = len(json.dumps(monetization_data, default=str))
        
        agent_data = await self._backup_user_agent_data(user_id)
        size_info["agent_interaction_size"] = len(json.dumps(agent_data, default=str))
        
        analytics_data = await self._backup_user_analytics(user_id)
        size_info["analytics_size"] = len(json.dumps(analytics_data, default=str))
        
        # Calculate total
        size_info["total_size"] = sum(
            size_info[key] for key in size_info if key != "total_size"
        )
        
        return size_info
