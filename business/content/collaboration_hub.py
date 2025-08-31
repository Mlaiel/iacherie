"""Content Collaboration Hub - IA Influencer Agent Platform
=======================================================

Advanced real-time collaboration system for content creators, enabling seamless teamwork,
review workflows, and creative partnerships across multi-format content projects.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

import websockets
from ...core.config import get_settings
from ...core.database import get_database
from ...core.exceptions import CollaborationError
from ...core.logging import get_logger
from ...models.collaboration import CollaborationSession, CollaborationType, UserRole
from ...real_time.websocket_manager import WebSocketManager
from ...utils.notification_service import NotificationService

logger = get_logger(__name__)
settings = get_settings()


class ContentCollaborationHub:
    """Advanced real-time collaboration system for content creators."""    
    def __init__(self):
        self.db = get_database()
        self.websocket_manager = WebSocketManager()
        self.notification_service = NotificationService()
        
        # Collaboration types and their capabilities
        self.collaboration_types = {
            'content_creation': {
                'name': 'Content Creation',
                'description': 'Collaborative content creation and editing',
                'features': ['real_time_editing', 'version_control', 'comments', 'approvals'],
                'max_participants': 10
            },
            'content_review': {
                'name': 'Content Review',
                'description': 'Review and approval workflow for content',
                'features': ['annotations', 'feedback', 'approval_workflow', 'revision_tracking'],
                'max_participants': 5
            },
            'creative_partnership': {
                'name': 'Creative Partnership',
                'description': 'Long-term creative collaboration between creators',
                'features': ['project_management', 'resource_sharing', 'revenue_sharing', 'communication'],
                'max_participants': 20
            },
            'live_collaboration': {
                'name': 'Live Collaboration',
                'description': 'Real-time collaborative editing and creation',
                'features': ['live_editing', 'voice_chat', 'screen_sharing', 'instant_sync'],
                'max_participants': 8
            },
            'mentor_session': {
                'name': 'Mentor Session',
                'description': 'Mentorship and guidance sessions',
                'features': ['guided_editing', 'feedback', 'learning_resources', 'progress_tracking'],
                'max_participants': 2
            }
        }
        
        # User roles and permissions
        self.role_permissions = {
            UserRole.OWNER: {
                'edit_content': True,
                'invite_users': True,
                'manage_permissions': True,
                'approve_changes': True,
                'delete_session': True,
                'export_content': True
            },
            UserRole.COLLABORATOR: {
                'edit_content': True,
                'invite_users': False,
                'manage_permissions': False,
                'approve_changes': False,
                'delete_session': False,
                'export_content': True
            },
            UserRole.REVIEWER: {
                'edit_content': False,
                'invite_users': False,
                'manage_permissions': False,
                'approve_changes': True,
                'delete_session': False,
                'export_content': False
            },
            UserRole.VIEWER: {
                'edit_content': False,
                'invite_users': False,
                'manage_permissions': False,
                'approve_changes': False,
                'delete_session': False,
                'export_content': False
            }
        }
        
        # Active sessions tracking
        self.active_sessions: Dict[UUID, Dict[str, Any]] = {}
        self.user_sessions: Dict[UUID, Set[UUID]] = {}  # user_id -> set of session_ids
    
    async def create_collaboration_session(
        self,
        owner_id: UUID,
        content_id: UUID,
        collaboration_type: str,
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Create new collaboration session.
        
        Args:
            owner_id: Session owner's user ID
            content_id: Content being collaborated on
            collaboration_type: Type of collaboration
            session_config: Session configuration and settings
            
        Returns:
            Session information and access details
        """        try:
            # Validate collaboration type
            if collaboration_type not in self.collaboration_types:
                raise CollaborationError(f"Invalid collaboration type: {collaboration_type}")
            
            # Create session record
            session_id = uuid4()
            session_data = {
                'id': session_id,
                'owner_id': owner_id,
                'content_id': content_id,
                'collaboration_type': collaboration_type,
                'title': session_config.get('title', f'Collaboration on Content'),
                'description': session_config.get('description', ''),
                'settings': session_config.get('settings', {}),
                'status': 'active',
                'created_at': datetime.utcnow(),
                'expires_at': self._calculate_session_expiry(session_config)
            }
            
            session = await self.db.collaboration_sessions.create(session_data)
            
            # Add owner as participant
            await self._add_participant(session_id, owner_id, UserRole.OWNER)
            
            # Initialize session state
            await self._initialize_session_state(session_id, content_id, collaboration_type)
            
            # Store in active sessions
            self.active_sessions[session_id] = {
                'session': session,
                'participants': {owner_id: UserRole.OWNER},
                'state': await self._get_session_state(session_id),
                'last_activity': datetime.utcnow()
            }
            
            # Track user sessions
            if owner_id not in self.user_sessions:
                self.user_sessions[owner_id] = set()
            self.user_sessions[owner_id].add(session_id)
            
            result = {
                'session_id': str(session_id),
                'collaboration_type': collaboration_type,
                'session_url': f"/collaborate/{session_id}",
                'websocket_url': f"ws://{settings.HOST}:{settings.PORT}/ws/collaborate/{session_id}",
                'features': self.collaboration_types[collaboration_type]['features'],
                'max_participants': self.collaboration_types[collaboration_type]['max_participants'],
                'owner_permissions': self.role_permissions[UserRole.OWNER],
                'expires_at': session.expires_at.isoformat() if session.expires_at else None
            }
            
            logger.info(f"Collaboration session created: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create collaboration session: {str(e)}")
            raise CollaborationError(f"Failed to create session: {str(e)}")
    
    async def join_collaboration_session(
        self,
        session_id: UUID,
        user_id: UUID,
        join_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Join existing collaboration session.
        
        Args:
            session_id: Session to join
            user_id: User joining the session
            join_token: Optional invitation token
            
        Returns:
            Session access information and user permissions
        """        try:
            # Validate session exists and is active
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found or expired")
            
            # Check if user is already in session
            current_participants = session['participants']
            if user_id in current_participants:
                user_role = current_participants[user_id]
            else:
                # Verify invitation or permission to join
                invitation = await self._verify_session_invitation(session_id, user_id, join_token)
                if not invitation:
                    raise CollaborationError("No valid invitation found")
                
                user_role = invitation.get('role', UserRole.VIEWER)
                
                # Check participant limits
                collab_type = session['session'].collaboration_type
                max_participants = self.collaboration_types[collab_type]['max_participants']
                
                if len(current_participants) >= max_participants:
                    raise CollaborationError("Session is full")
                
                # Add user as participant
                await self._add_participant(session_id, user_id, user_role)
                current_participants[user_id] = user_role
                
                # Track user sessions
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(session_id)
            
            # Update last activity
            session['last_activity'] = datetime.utcnow()
            
            # Get user permissions
            permissions = self.role_permissions[user_role]
            
            # Notify other participants
            await self._broadcast_user_joined(session_id, user_id, user_role)
            
            result = {
                'session_id': str(session_id),
                'user_role': user_role.value,
                'permissions': permissions,
                'session_state': session['state'],
                'participants': await self._get_session_participants(session_id),
                'websocket_url': f"ws://{settings.HOST}:{settings.PORT}/ws/collaborate/{session_id}",
                'features': self.collaboration_types[session['session'].collaboration_type]['features']
            }
            
            logger.info(f"User {user_id} joined session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to join collaboration session: {str(e)}")
            raise CollaborationError(f"Failed to join session: {str(e)}")
    
    async def send_collaboration_update(
        self,
        session_id: UUID,
        user_id: UUID,
        update_type: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Send real-time collaboration update.
        
        Args:
            session_id: Session to update
            user_id: User sending the update
            update_type: Type of update (edit, comment, cursor_position, etc.)
            update_data: Update payload
            
        Returns:
            Update acknowledgment and broadcast status
        """        try:
            # Validate session and user permissions
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found")
            
            user_role = session['participants'].get(user_id)
            if not user_role:
                raise CollaborationError("User not in session")
            
            # Validate update permissions
            if not await self._validate_update_permission(update_type, user_role):
                raise CollaborationError("Insufficient permissions for this update")
            
            # Process update based on type
            processed_update = await self._process_collaboration_update(
                session_id, user_id, update_type, update_data
            )
            
            # Update session state
            await self._update_session_state(session_id, update_type, processed_update)
            
            # Broadcast to other participants
            broadcast_data = {
                'session_id': str(session_id),
                'user_id': str(user_id),
                'update_type': update_type,
                'update_data': processed_update,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_session(session_id, broadcast_data, exclude_user=user_id)
            
            # Update activity timestamp
            session['last_activity'] = datetime.utcnow()
            
            result = {
                'update_id': str(uuid4()),
                'status': 'broadcasted',
                'participants_notified': len(session['participants']) - 1,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send collaboration update: {str(e)}")
            raise CollaborationError(f"Failed to send update: {str(e)}")
    
    async def invite_user_to_session(
        self,
        session_id: UUID,
        inviter_id: UUID,
        invitee_email: str,
        role: UserRole = UserRole.COLLABORATOR,
        invitation_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Invite user to collaboration session.
        
        Args:
            session_id: Session to invite to
            inviter_id: User sending invitation
            invitee_email: Email of user to invite
            role: Role to assign to invited user
            invitation_message: Optional invitation message
            
        Returns:
            Invitation details and status
        """        try:
            # Validate session and permissions
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found")
            
            inviter_role = session['participants'].get(inviter_id)
            if not inviter_role:
                raise CollaborationError("User not in session")
            
            inviter_permissions = self.role_permissions[inviter_role]
            if not inviter_permissions.get('invite_users', False):
                raise CollaborationError("Insufficient permissions to invite users")
            
            # Check participant limits
            collab_type = session['session'].collaboration_type
            max_participants = self.collaboration_types[collab_type]['max_participants']
            
            if len(session['participants']) >= max_participants:
                raise CollaborationError("Session is full")
            
            # Create invitation
            invitation_id = uuid4()
            invitation_data = {
                'id': invitation_id,
                'session_id': session_id,
                'inviter_id': inviter_id,
                'invitee_email': invitee_email,
                'role': role,
                'message': invitation_message,
                'token': self._generate_invitation_token(),
                'expires_at': datetime.utcnow() + timedelta(days=7),
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            invitation = await self.db.collaboration_invitations.create(invitation_data)
            
            # Send invitation email
            await self.notification_service.send_collaboration_invitation(
                invitee_email=invitee_email,
                session_title=session['session'].title,
                inviter_name=await self._get_user_name(inviter_id),
                invitation_link=f"{settings.FRONTEND_URL}/collaborate/join/{invitation_id}",
                message=invitation_message
            )
            
            result = {
                'invitation_id': str(invitation_id),
                'invitee_email': invitee_email,
                'role': role.value,
                'status': 'sent',
                'expires_at': invitation.expires_at.isoformat(),
                'invitation_link': f"{settings.FRONTEND_URL}/collaborate/join/{invitation_id}"
            }
            
            logger.info(f"Invitation sent for session {session_id} to {invitee_email}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to send invitation: {str(e)}")
            raise CollaborationError(f"Failed to send invitation: {str(e)}")
    
    async def manage_session_permissions(
        self,
        session_id: UUID,
        manager_id: UUID,
        target_user_id: UUID,
        action: str,
        new_role: Optional[UserRole] = None
    ) -> Dict[str, Any]:
        """        Manage user permissions in collaboration session.
        
        Args:
            session_id: Session to manage
            manager_id: User managing permissions
            target_user_id: User whose permissions to change
            action: Action to perform (change_role, remove_user, etc.)
            new_role: New role for user (if changing role)
            
        Returns:
            Permission management result
        """        try:
            # Validate session and permissions
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found")
            
            manager_role = session['participants'].get(manager_id)
            if not manager_role:
                raise CollaborationError("Manager not in session")
            
            manager_permissions = self.role_permissions[manager_role]
            if not manager_permissions.get('manage_permissions', False):
                raise CollaborationError("Insufficient permissions to manage users")
            
            # Validate target user
            if target_user_id not in session['participants']:
                raise CollaborationError("Target user not in session")
            
            current_role = session['participants'][target_user_id]
            
            # Prevent self-modification of owner role
            if target_user_id == manager_id and manager_role == UserRole.OWNER:
                raise CollaborationError("Owner cannot modify their own role")
            
            # Process action
            if action == 'change_role':
                if not new_role:
                    raise CollaborationError("New role required for role change")
                
                # Update role in session
                session['participants'][target_user_id] = new_role
                
                # Update in database
                await self.db.collaboration_participants.update_role(
                    session_id, target_user_id, new_role
                )
                
                # Notify user of role change
                await self._notify_role_change(session_id, target_user_id, current_role, new_role)
                
                result = {
                    'action': 'role_changed',
                    'user_id': str(target_user_id),
                    'old_role': current_role.value,
                    'new_role': new_role.value
                }
                
            elif action == 'remove_user':
                # Remove from session
                del session['participants'][target_user_id]
                
                # Remove from database
                await self.db.collaboration_participants.remove(session_id, target_user_id)
                
                # Remove from user sessions tracking
                if target_user_id in self.user_sessions:
                    self.user_sessions[target_user_id].discard(session_id)
                
                # Notify user of removal
                await self._notify_user_removed(session_id, target_user_id)
                
                # Disconnect user's websockets
                await self.websocket_manager.disconnect_user_from_session(
                    session_id, target_user_id
                )
                
                result = {
                    'action': 'user_removed',
                    'user_id': str(target_user_id)
                }
                
            else:
                raise CollaborationError(f"Unknown action: {action}")
            
            # Broadcast change to other participants
            await self._broadcast_permission_change(session_id, result)
            
            logger.info(f"Permission management completed: {action} for user {target_user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to manage permissions: {str(e)}")
            raise CollaborationError(f"Failed to manage permissions: {str(e)}")
    
    async def get_session_analytics(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """        Get analytics for collaboration session.
        
        Args:
            session_id: Session to analyze
            user_id: User requesting analytics
            
        Returns:
            Session analytics and insights
        """        try:
            # Validate session and permissions
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found")
            
            user_role = session['participants'].get(user_id)
            if not user_role:
                raise CollaborationError("User not in session")
            
            # Get session history
            session_history = await self.db.collaboration_history.get_by_session(session_id)
            
            # Calculate analytics
            analytics = {
                'session_info': {
                    'session_id': str(session_id),
                    'collaboration_type': session['session'].collaboration_type,
                    'created_at': session['session'].created_at.isoformat(),
                    'duration_minutes': (datetime.utcnow() - session['session'].created_at).total_seconds() / 60,
                    'status': session['session'].status
                },
                'participation_stats': {
                    'total_participants': len(session['participants']),
                    'active_participants': await self._count_active_participants(session_id),
                    'participant_roles': self._analyze_participant_roles(session['participants'])
                },
                'activity_stats': {
                    'total_updates': len(session_history),
                    'updates_by_type': self._analyze_updates_by_type(session_history),
                    'updates_by_user': self._analyze_updates_by_user(session_history),
                    'activity_timeline': self._generate_activity_timeline(session_history)
                },
                'collaboration_metrics': {
                    'average_response_time': self._calculate_average_response_time(session_history),
                    'collaboration_score': self._calculate_collaboration_score(session_history),
                    'engagement_level': self._calculate_engagement_level(session_history)
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {str(e)}")
            raise CollaborationError(f"Failed to get analytics: {str(e)}")
    
    async def export_collaboration_data(
        self,
        session_id: UUID,
        user_id: UUID,
        export_format: str = 'json'
    ) -> Dict[str, Any]:
        """        Export collaboration session data.
        
        Args:
            session_id: Session to export
            user_id: User requesting export
            export_format: Export format (json, csv, pdf)
            
        Returns:
            Export file information and download link
        """        try:
            # Validate session and permissions
            session = await self._get_active_session(session_id)
            if not session:
                raise CollaborationError("Session not found")
            
            user_role = session['participants'].get(user_id)
            if not user_role:
                raise CollaborationError("User not in session")
            
            user_permissions = self.role_permissions[user_role]
            if not user_permissions.get('export_content', False):
                raise CollaborationError("Insufficient permissions to export")
            
            # Gather export data
            export_data = {
                'session_info': {
                    'session_id': str(session_id),
                    'title': session['session'].title,
                    'collaboration_type': session['session'].collaboration_type,
                    'created_at': session['session'].created_at.isoformat(),
                    'owner_id': str(session['session'].owner_id)
                },
                'participants': await self._get_detailed_participants(session_id),
                'session_history': await self.db.collaboration_history.get_by_session(session_id),
                'final_state': session['state'],
                'analytics': await self.get_session_analytics(session_id, user_id)
            }
            
            # Generate export file
            export_file_path = await self._generate_export_file(
                export_data, export_format, session_id
            )
            
            result = {
                'export_id': str(uuid4()),
                'format': export_format,
                'file_path': export_file_path,
                'download_url': f"/api/collaborate/download/{session_id}",
                'file_size': await self._get_file_size(export_file_path),
                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            logger.info(f"Collaboration data exported for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to export collaboration data: {str(e)}")
            raise CollaborationError(f"Failed to export data: {str(e)}")
    
    # Private helper methods
    
    async def _get_active_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """Get active session from memory or database."""        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Load from database if not in memory
        session = await self.db.collaboration_sessions.get_by_id(session_id)
        if session and session.status == 'active':
            participants = await self.db.collaboration_participants.get_by_session(session_id)
            
            self.active_sessions[session_id] = {
                'session': session,
                'participants': {p.user_id: p.role for p in participants},
                'state': await self._get_session_state(session_id),
                'last_activity': session.updated_at or session.created_at
            }
            
            return self.active_sessions[session_id]
        
        return None
    
    def _calculate_session_expiry(self, session_config: Dict[str, Any]) -> Optional[datetime]:
        """Calculate session expiry time."""        expiry_hours = session_config.get('expiry_hours', 24)
        if expiry_hours > 0:
            return datetime.utcnow() + timedelta(hours=expiry_hours)
        return None
    
    async def _add_participant(
        self,
        session_id: UUID,
        user_id: UUID,
        role: UserRole
    ) -> None:
        """Add participant to session."""        participant_data = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'joined_at': datetime.utcnow()
        }
        
        await self.db.collaboration_participants.create(participant_data)
    
    async def _initialize_session_state(
        self,
        session_id: UUID,
        content_id: UUID,
        collaboration_type: str
    ) -> None:
        """Initialize session state based on collaboration type."""        initial_state = {
            'content_id': str(content_id),
            'version': 1,
            'last_saved': datetime.utcnow().isoformat(),
            'changes': [],
            'comments': [],
            'approvals': [],
            'cursor_positions': {},
            'live_edits': {}
        }
        
        # Store initial state
        await self.db.collaboration_states.create({
            'session_id': session_id,
            'state_data': initial_state,
            'version': 1,
            'created_at': datetime.utcnow()
        })
    
    async def _get_session_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get current session state."""        state = await self.db.collaboration_states.get_latest(session_id)
        return state.state_data if state else {}
    
    async def _verify_session_invitation(
        self,
        session_id: UUID,
        user_id: UUID,
        join_token: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Verify session invitation."""        if join_token:
            invitation = await self.db.collaboration_invitations.get_by_token(
                session_id, join_token
            )
            if invitation and invitation.status == 'pending':
                # Check if invitation is for this user
                user = await self.db.users.get_by_email(invitation.invitee_email)
                if user and user.id == user_id:
                    return {
                        'role': invitation.role,
                        'invitation_id': invitation.id
                    }
        
        return None
    
    async def _validate_update_permission(
        self,
        update_type: str,
        user_role: UserRole
    ) -> bool:
        """Validate if user can perform update type."""        permissions = self.role_permissions[user_role]
        
        edit_updates = ['content_edit', 'text_change', 'media_upload', 'live_edit']
        approval_updates = ['approve_change', 'reject_change']
        
        if update_type in edit_updates:
            return permissions.get('edit_content', False)
        elif update_type in approval_updates:
            return permissions.get('approve_changes', False)
        else:
            # Comments, cursor moves, etc. allowed for all participants
            return True
    
    async def _process_collaboration_update(
        self,
        session_id: UUID,
        user_id: UUID,
        update_type: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate collaboration update."""        processed_update = {
            'user_id': str(user_id),
            'timestamp': datetime.utcnow().isoformat(),
            'type': update_type,
            'data': update_data
        }
        
        # Add update to session history
        await self.db.collaboration_history.create({
            'session_id': session_id,
            'user_id': user_id,
            'update_type': update_type,
            'update_data': processed_update,
            'created_at': datetime.utcnow()
        })
        
        return processed_update
    
    async def _update_session_state(
        self,
        session_id: UUID,
        update_type: str,
        update_data: Dict[str, Any]
    ) -> None:
        """Update session state based on update."""        current_state = await self._get_session_state(session_id)
        
        # Update state based on update type
        if update_type == 'content_edit':
            current_state['changes'].append(update_data)
            current_state['version'] += 1
        elif update_type == 'comment':
            current_state['comments'].append(update_data)
        elif update_type == 'cursor_position':
            current_state['cursor_positions'][update_data['user_id']] = update_data['position']
        elif update_type == 'live_edit':
            current_state['live_edits'][update_data['edit_id']] = update_data
        
        current_state['last_modified'] = datetime.utcnow().isoformat()
        
        # Save updated state
        await self.db.collaboration_states.create({
            'session_id': session_id,
            'state_data': current_state,
            'version': current_state['version'],
            'created_at': datetime.utcnow()
        })
        
        # Update in-memory state
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['state'] = current_state
    
    async def _broadcast_to_session(
        self,
        session_id: UUID,
        message_data: Dict[str, Any],
        exclude_user: Optional[UUID] = None
    ) -> None:
        """Broadcast message to all session participants."""        await self.websocket_manager.broadcast_to_session(
            session_id, message_data, exclude_user
        )
    
    async def _broadcast_user_joined(
        self,
        session_id: UUID,
        user_id: UUID,
        role: UserRole
    ) -> None:
        """Broadcast user joined notification."""        message = {
            'type': 'user_joined',
            'user_id': str(user_id),
            'role': role.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_session(session_id, message, exclude_user=user_id)
    
    async def _broadcast_permission_change(
        self,
        session_id: UUID,
        change_data: Dict[str, Any]
    ) -> None:
        """Broadcast permission change to session."""        message = {
            'type': 'permission_change',
            'change_data': change_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_session(session_id, message)
    
    def _generate_invitation_token(self) -> str:
        """Generate secure invitation token."""        import secrets
        return secrets.token_urlsafe(32)
    
    async def _get_user_name(self, user_id: UUID) -> str:
        """Get user display name."""        user = await self.db.users.get_by_id(user_id)
        return user.display_name if user else "Unknown User"
    
    async def _get_session_participants(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Get detailed session participants."""        participants = await self.db.collaboration_participants.get_by_session(session_id)
        
        participant_list = []
        for participant in participants:
            user = await self.db.users.get_by_id(participant.user_id)
            participant_list.append({
                'user_id': str(participant.user_id),
                'name': user.display_name if user else "Unknown",
                'role': participant.role.value,
                'joined_at': participant.joined_at.isoformat(),
                'is_active': await self._is_user_active(session_id, participant.user_id)
            })
        
        return participant_list
    
    async def _is_user_active(self, session_id: UUID, user_id: UUID) -> bool:
        """Check if user is currently active in session."""        return await self.websocket_manager.is_user_connected(session_id, user_id)
    
    async def _notify_role_change(
        self,
        session_id: UUID,
        user_id: UUID,
        old_role: UserRole,
        new_role: UserRole
    ) -> None:
        """Notify user of role change."""        await self.notification_service.send_role_change_notification(
            user_id=user_id,
            session_id=session_id,
            old_role=old_role.value,
            new_role=new_role.value
        )
    
    async def _notify_user_removed(self, session_id: UUID, user_id: UUID) -> None:
        """Notify user of removal from session."""        await self.notification_service.send_session_removal_notification(
            user_id=user_id,
            session_id=session_id
        )
    
    # Analytics helper methods
    
    async def _count_active_participants(self, session_id: UUID) -> int:
        """Count currently active participants."""        session = self.active_sessions.get(session_id)
        if not session:
            return 0
        
        active_count = 0
        for user_id in session['participants']:
            if await self._is_user_active(session_id, user_id):
                active_count += 1
        
        return active_count
    
    def _analyze_participant_roles(self, participants: Dict[UUID, UserRole]) -> Dict[str, int]:
        """Analyze distribution of participant roles."""        role_counts = {}
        for role in participants.values():
            role_counts[role.value] = role_counts.get(role.value, 0) + 1
        
        return role_counts
    
    def _analyze_updates_by_type(self, history: List[Any]) -> Dict[str, int]:
        """Analyze updates by type."""        update_counts = {}
        for update in history:
            update_type = update.update_type
            update_counts[update_type] = update_counts.get(update_type, 0) + 1
        
        return update_counts
    
    def _analyze_updates_by_user(self, history: List[Any]) -> Dict[str, int]:
        """Analyze updates by user."""        user_counts = {}
        for update in history:
            user_id = str(update.user_id)
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        return user_counts
    
    def _generate_activity_timeline(self, history: List[Any]) -> List[Dict[str, Any]]:
        """Generate activity timeline."""        timeline = []
        for update in history[-50:]:  # Last 50 updates
            timeline.append({
                'timestamp': update.created_at.isoformat(),
                'user_id': str(update.user_id),
                'type': update.update_type,
                'summary': self._generate_update_summary(update)
            })
        
        return timeline
    
    def _generate_update_summary(self, update: Any) -> str:
        """Generate human-readable update summary."""        summaries = {
            'content_edit': 'Made content changes',
            'comment': 'Added a comment',
            'approval': 'Approved changes',
            'cursor_position': 'Moved cursor',
            'live_edit': 'Made live edits'
        }
        
        return summaries.get(update.update_type, 'Performed an action')
    
    def _calculate_average_response_time(self, history: List[Any]) -> float:
        """Calculate average response time between updates."""        if len(history) < 2:
            return 0.0
        
        response_times = []
        for i in range(1, len(history)):
            time_diff = (history[i].created_at - history[i-1].created_at).total_seconds()
            response_times.append(time_diff)
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _calculate_collaboration_score(self, history: List[Any]) -> float:
        """Calculate collaboration quality score."""        if not history:
            return 0.0
        
        # Factors: variety of update types, user participation, activity frequency
        update_types = set(update.update_type for update in history)
        unique_users = set(str(update.user_id) for update in history)
        
        variety_score = min(len(update_types) / 5.0, 1.0)  # Max 5 different types
        participation_score = min(len(unique_users) / 3.0, 1.0)  # Max 3 active users
        activity_score = min(len(history) / 50.0, 1.0)  # Max 50 updates for full score
        
        return (variety_score + participation_score + activity_score) / 3.0
    
    def _calculate_engagement_level(self, history: List[Any]) -> str:
        """Calculate engagement level."""        score = self._calculate_collaboration_score(history)
        
        if score >= 0.8:
            return 'High'
        elif score >= 0.5:
            return 'Medium'
        elif score >= 0.2:
            return 'Low'
        else:
            return 'Minimal'
    
    # Export helper methods
    
    async def _get_detailed_participants(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Get detailed participant information for export."""        participants = await self.db.collaboration_participants.get_by_session(session_id)
        
        detailed_participants = []
        for participant in participants:
            user = await self.db.users.get_by_id(participant.user_id)
            detailed_participants.append({
                'user_id': str(participant.user_id),
                'name': user.display_name if user else "Unknown",
                'email': user.email if user else "unknown@example.com",
                'role': participant.role.value,
                'joined_at': participant.joined_at.isoformat(),
                'total_contributions': await self._count_user_contributions(
                    session_id, participant.user_id
                )
            })
        
        return detailed_participants
    
    async def _count_user_contributions(self, session_id: UUID, user_id: UUID) -> int:
        """Count user contributions to session."""        contributions = await self.db.collaboration_history.count_by_user(
            session_id, user_id
        )
        return contributions
    
    async def _generate_export_file(
        self,
        export_data: Dict[str, Any],
        format_type: str,
        session_id: UUID
    ) -> str:
        """Generate export file in specified format."""        import json
        from pathlib import Path
        
        export_dir = Path(settings.EXPORT_DIR) / "collaborations"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"collaboration_{session_id}_{timestamp}.{format_type}"
        file_path = export_dir / filename
        
        if format_type == 'json':
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format_type == 'csv':
            # Implement CSV export
            await self._export_to_csv(export_data, file_path)
        elif format_type == 'pdf':
            # Implement PDF export
            await self._export_to_pdf(export_data, file_path)
        
        return str(file_path)
    
    async def _export_to_csv(self, export_data: Dict[str, Any], file_path: Path) -> None:
        """Export data to CSV format."""        import csv
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write session info
            writer.writerow(['Session Information'])
            for key, value in export_data['session_info'].items():
                writer.writerow([key, value])
            
            writer.writerow([])  # Empty row
            
            # Write participants
            writer.writerow(['Participants'])
            writer.writerow(['Name', 'Role', 'Joined At', 'Contributions'])
            for participant in export_data['participants']:
                writer.writerow([
                    participant['name'],
                    participant['role'],
                    participant['joined_at'],
                    participant['total_contributions']
                ])
    
    async def _export_to_pdf(self, export_data: Dict[str, Any], file_path: Path) -> None:
        """Export data to PDF format."""        # This would use a PDF generation library like reportlab
        # For now, create a simple text file
        with open(file_path.with_suffix('.txt'), 'w') as f:
            f.write("Collaboration Session Export\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("Session Information:\n")
            for key, value in export_data['session_info'].items():
                f.write(f"{key}: {value}\n")
            
            f.write("\nParticipants:\n")
            for participant in export_data['participants']:
                f.write(f"- {participant['name']} ({participant['role']})\n")
    
    async def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""        return Path(file_path).stat().st_size
