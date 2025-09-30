"""
💬 COMMENT SYSTEM - ENTERPRISE ARCHITECTURE
========================================

Timeline-based comment system for multimedia collaboration with threading,
mentions, reactions, and real-time synchronization across all participants.

**Expert Implementation:**
- Backend Senior: High-performance comment storage and retrieval
- Database Administrator: Efficient comment indexing and search
- Frontend Engineer: Rich timeline comment interface
- Security Engineer: Comment moderation and access control

**Features:** Timeline comments, Threading, Mentions, Reactions, Real-time sync
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import re

# Comment system libraries
try:
    import redis
    import asyncpg
    from datetime import datetime, timedelta
    import bleach
    import markdown
except ImportError as e:
    logging.warning(f"Comment system dependencies not available: {e}")

logger = logging.getLogger(__name__)

class CommentType(Enum):
    """Types of comments"""
    GENERAL = "general"
    FEEDBACK = "feedback"
    SUGGESTION = "suggestion"
    ISSUE = "issue"
    APPROVAL = "approval"
    QUESTION = "question"
    ANNOTATION = "annotation"

class CommentStatus(Enum):
    """Comment status states"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    DELETED = "deleted"
    HIDDEN = "hidden"

class ReactionType(Enum):
    """Types of reactions"""
    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    HEART = "heart"
    FIRE = "fire"
    EYES = "eyes"

@dataclass
class Comment:
    """Comment representation"""
    comment_id: str
    content_id: str
    user_id: str
    username: str
    content: str
    comment_type: CommentType
    timestamp: float
    timeline_position: Optional[float]  # For timeline-based comments
    parent_comment_id: Optional[str]  # For threaded comments
    mentions: List[str]  # User IDs mentioned in comment
    attachments: List[Dict[str, Any]]
    status: CommentStatus
    metadata: Dict[str, Any]
    edited_at: Optional[float]
    edit_history: List[Dict[str, Any]]

@dataclass
class CommentReaction:
    """Comment reaction representation"""
    reaction_id: str
    comment_id: str
    user_id: str
    reaction_type: ReactionType
    timestamp: float

@dataclass
class CommentThread:
    """Comment thread representation"""
    thread_id: str
    root_comment_id: str
    content_id: str
    participant_ids: Set[str]
    comment_count: int
    last_activity: float
    is_resolved: bool
    resolver_id: Optional[str]
    resolved_at: Optional[float]

class CommentEngine:
    """Core comment engine with threading and timeline support"""
    
    def __init__(self):
        self.comments = {}  # comment_id -> Comment
        self.content_comments = defaultdict(list)  # content_id -> [comment_ids]
        self.comment_threads = {}  # thread_id -> CommentThread
        self.comment_reactions = defaultdict(list)  # comment_id -> [reactions]
        self.user_mentions = defaultdict(list)  # user_id -> [comment_ids]
        
        # Real-time notifications
        self.notification_callbacks = []
        self.websocket_connections = {}
        
        # Database connections
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except:
            self.redis_client = None
            logger.warning("Redis not available for comment caching")
        
        # Comment settings
        self.max_comment_length = 2000
        self.mention_pattern = re.compile(r'@(\w+)')
        self.auto_resolve_timeout = 86400  # 24 hours
        self.allowed_html_tags = ['b', 'i', 'u', 'a', 'br', 'p']
        
    async def add_comment(self, content_id: str, user_id: str, username: str,
                         content: str, comment_type: CommentType = CommentType.GENERAL,
                         timeline_position: Optional[float] = None,
                         parent_comment_id: Optional[str] = None,
                         attachments: List[Dict[str, Any]] = None) -> Comment:
        """Add new comment"""
        try:
            comment_id = str(uuid.uuid4())
            
            # Sanitize content
            clean_content = await self._sanitize_content(content)
            
            # Extract mentions
            mentions = await self._extract_mentions(clean_content)
            
            # Create comment
            comment = Comment(
                comment_id=comment_id,
                content_id=content_id,
                user_id=user_id,
                username=username,
                content=clean_content,
                comment_type=comment_type,
                timestamp=time.time(),
                timeline_position=timeline_position,
                parent_comment_id=parent_comment_id,
                mentions=mentions,
                attachments=attachments or [],
                status=CommentStatus.ACTIVE,
                metadata={},
                edited_at=None,
                edit_history=[]
            )
            
            # Store comment
            self.comments[comment_id] = comment
            self.content_comments[content_id].append(comment_id)
            
            # Handle threading
            if parent_comment_id:
                await self._add_to_thread(comment)
            else:
                await self._create_thread(comment)
            
            # Process mentions
            await self._process_mentions(comment)
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_comment_redis(comment)
            
            # Send real-time notification
            await self._notify_comment_added(comment)
            
            logger.info(f"Added comment {comment_id} to content {content_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            raise
    
    async def add_timeline_comment(self, content_id: str, user_id: str, username: str,
                                 content: str, timestamp: float,
                                 comment_type: CommentType = CommentType.FEEDBACK) -> Comment:
        """Add timeline-specific comment with precise timing"""
        return await self.add_comment(
            content_id=content_id,
            user_id=user_id,
            username=username,
            content=content,
            comment_type=comment_type,
            timeline_position=timestamp
        )
    
    async def reply_to_comment(self, parent_comment_id: str, user_id: str, 
                             username: str, content: str) -> Comment:
        """Reply to existing comment"""
        try:
            parent_comment = self.comments.get(parent_comment_id)
            if not parent_comment:
                raise ValueError(f"Parent comment {parent_comment_id} not found")
            
            return await self.add_comment(
                content_id=parent_comment.content_id,
                user_id=user_id,
                username=username,
                content=content,
                parent_comment_id=parent_comment_id
            )
            
        except Exception as e:
            logger.error(f"Failed to reply to comment: {e}")
            raise
    
    async def edit_comment(self, comment_id: str, user_id: str, 
                         new_content: str) -> Comment:
        """Edit existing comment"""
        try:
            comment = self.comments.get(comment_id)
            if not comment:
                raise ValueError(f"Comment {comment_id} not found")
            
            # Check permissions
            if comment.user_id != user_id:
                raise PermissionError("User can only edit their own comments")
            
            # Save edit history
            edit_entry = {
                'previous_content': comment.content,
                'edited_at': time.time(),
                'editor_id': user_id
            }
            comment.edit_history.append(edit_entry)
            
            # Update content
            comment.content = await self._sanitize_content(new_content)
            comment.edited_at = time.time()
            comment.mentions = await self._extract_mentions(comment.content)
            
            # Update in storage
            if self.redis_client:
                await self._store_comment_redis(comment)
            
            # Notify edit
            await self._notify_comment_edited(comment)
            
            logger.info(f"Edited comment {comment_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Failed to edit comment: {e}")
            raise
    
    async def delete_comment(self, comment_id: str, user_id: str, 
                           soft_delete: bool = True) -> bool:
        """Delete comment (soft or hard delete)"""
        try:
            comment = self.comments.get(comment_id)
            if not comment:
                raise ValueError(f"Comment {comment_id} not found")
            
            # Check permissions
            if comment.user_id != user_id:
                raise PermissionError("User can only delete their own comments")
            
            if soft_delete:
                # Soft delete - mark as deleted
                comment.status = CommentStatus.DELETED
                comment.content = "[Comment deleted]"
            else:
                # Hard delete - remove completely
                del self.comments[comment_id]
                self.content_comments[comment.content_id].remove(comment_id)
            
            # Notify deletion
            await self._notify_comment_deleted(comment_id, user_id, soft_delete)
            
            logger.info(f"Deleted comment {comment_id} (soft: {soft_delete})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete comment: {e}")
            return False
    
    async def add_reaction(self, comment_id: str, user_id: str, 
                         reaction_type: ReactionType) -> CommentReaction:
        """Add reaction to comment"""
        try:
            if comment_id not in self.comments:
                raise ValueError(f"Comment {comment_id} not found")
            
            # Check if user already reacted with this type
            existing_reactions = self.comment_reactions[comment_id]
            for reaction in existing_reactions:
                if reaction.user_id == user_id and reaction.reaction_type == reaction_type:
                    raise ValueError("User already reacted with this type")
            
            reaction = CommentReaction(
                reaction_id=str(uuid.uuid4()),
                comment_id=comment_id,
                user_id=user_id,
                reaction_type=reaction_type,
                timestamp=time.time()
            )
            
            self.comment_reactions[comment_id].append(reaction)
            
            # Notify reaction
            await self._notify_reaction_added(reaction)
            
            logger.info(f"Added reaction {reaction_type.value} to comment {comment_id}")
            return reaction
            
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            raise
    
    async def remove_reaction(self, comment_id: str, user_id: str, 
                            reaction_type: ReactionType) -> bool:
        """Remove reaction from comment"""
        try:
            reactions = self.comment_reactions[comment_id]
            
            for i, reaction in enumerate(reactions):
                if reaction.user_id == user_id and reaction.reaction_type == reaction_type:
                    del reactions[i]
                    await self._notify_reaction_removed(comment_id, user_id, reaction_type)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove reaction: {e}")
            return False
    
    async def get_comments(self, content_id: str, 
                         include_deleted: bool = False,
                         timeline_start: Optional[float] = None,
                         timeline_end: Optional[float] = None) -> List[Comment]:
        """Get comments for content"""
        try:
            comment_ids = self.content_comments.get(content_id, [])
            comments = []
            
            for comment_id in comment_ids:
                comment = self.comments.get(comment_id)
                if not comment:
                    continue
                
                # Filter deleted comments
                if not include_deleted and comment.status == CommentStatus.DELETED:
                    continue
                
                # Filter by timeline range
                if timeline_start is not None and comment.timeline_position is not None:
                    if comment.timeline_position < timeline_start:
                        continue
                
                if timeline_end is not None and comment.timeline_position is not None:
                    if comment.timeline_position > timeline_end:
                        continue
                
                comments.append(comment)
            
            # Sort by timestamp
            comments.sort(key=lambda c: c.timestamp)
            
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get comments: {e}")
            return []
    
    async def get_timeline_comments(self, content_id: str, 
                                  timestamp: float, 
                                  tolerance: float = 1.0) -> List[Comment]:
        """Get comments near specific timeline position"""
        try:
            comments = await self.get_comments(content_id)
            
            timeline_comments = []
            for comment in comments:
                if comment.timeline_position is not None:
                    time_diff = abs(comment.timeline_position - timestamp)
                    if time_diff <= tolerance:
                        timeline_comments.append(comment)
            
            # Sort by distance from target timestamp
            timeline_comments.sort(key=lambda c: abs(c.timeline_position - timestamp))
            
            return timeline_comments
            
        except Exception as e:
            logger.error(f"Failed to get timeline comments: {e}")
            return []
    
    async def get_comment_thread(self, comment_id: str) -> Dict[str, Any]:
        """Get complete comment thread"""
        try:
            root_comment = self.comments.get(comment_id)
            if not root_comment:
                raise ValueError(f"Comment {comment_id} not found")
            
            # Find root comment if this is a reply
            while root_comment.parent_comment_id:
                root_comment = self.comments.get(root_comment.parent_comment_id)
                if not root_comment:
                    break
            
            if not root_comment:
                return {}
            
            # Build thread structure
            thread_comments = []
            await self._build_thread_structure(root_comment.comment_id, thread_comments)
            
            # Get thread info
            thread_info = None
            for thread in self.comment_threads.values():
                if thread.root_comment_id == root_comment.comment_id:
                    thread_info = thread
                    break
            
            return {
                'root_comment': asdict(root_comment),
                'thread_comments': thread_comments,
                'thread_info': asdict(thread_info) if thread_info else None,
                'total_comments': len(thread_comments) + 1
            }
            
        except Exception as e:
            logger.error(f"Failed to get comment thread: {e}")
            return {}
    
    async def resolve_thread(self, thread_id: str, resolver_id: str) -> bool:
        """Mark comment thread as resolved"""
        try:
            thread = self.comment_threads.get(thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            
            thread.is_resolved = True
            thread.resolver_id = resolver_id
            thread.resolved_at = time.time()
            
            # Notify thread resolution
            await self._notify_thread_resolved(thread)
            
            logger.info(f"Resolved thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve thread: {e}")
            return False
    
    async def search_comments(self, content_id: str, query: str, 
                            search_type: str = "content") -> List[Comment]:
        """Search comments by content, user, or mentions"""
        try:
            comments = await self.get_comments(content_id)
            results = []
            
            query_lower = query.lower()
            
            for comment in comments:
                match = False
                
                if search_type == "content":
                    if query_lower in comment.content.lower():
                        match = True
                elif search_type == "user":
                    if query_lower in comment.username.lower():
                        match = True
                elif search_type == "mentions":
                    if query in comment.mentions:
                        match = True
                elif search_type == "all":
                    if (query_lower in comment.content.lower() or 
                        query_lower in comment.username.lower() or 
                        query in comment.mentions):
                        match = True
                
                if match:
                    results.append(comment)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search comments: {e}")
            return []
    
    async def get_comment_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get comment analytics for content"""
        try:
            comments = await self.get_comments(content_id, include_deleted=True)
            
            # Basic metrics
            total_comments = len(comments)
            active_comments = len([c for c in comments if c.status == CommentStatus.ACTIVE])
            deleted_comments = len([c for c in comments if c.status == CommentStatus.DELETED])
            
            # Comment types
            type_breakdown = defaultdict(int)
            for comment in comments:
                type_breakdown[comment.comment_type.value] += 1
            
            # Timeline distribution
            timeline_comments = [c for c in comments if c.timeline_position is not None]
            
            # User activity
            user_activity = defaultdict(int)
            for comment in comments:
                user_activity[comment.user_id] += 1
            
            # Recent activity (last 24 hours)
            recent_cutoff = time.time() - 86400
            recent_comments = len([c for c in comments if c.timestamp > recent_cutoff])
            
            return {
                'content_id': content_id,
                'total_comments': total_comments,
                'active_comments': active_comments,
                'deleted_comments': deleted_comments,
                'comment_types': dict(type_breakdown),
                'timeline_comments': len(timeline_comments),
                'unique_commenters': len(user_activity),
                'most_active_users': sorted(user_activity.items(), 
                                          key=lambda x: x[1], reverse=True)[:5],
                'recent_activity_24h': recent_comments,
                'threads_count': len(self.comment_threads),
                'resolved_threads': len([t for t in self.comment_threads.values() if t.is_resolved])
            }
            
        except Exception as e:
            logger.error(f"Failed to get comment analytics: {e}")
            return {}
    
    async def _sanitize_content(self, content: str) -> str:
        """Sanitize comment content"""
        try:
            # Remove potentially harmful HTML
            clean_content = bleach.clean(content, tags=self.allowed_html_tags, strip=True)
            
            # Limit length
            if len(clean_content) > self.max_comment_length:
                clean_content = clean_content[:self.max_comment_length] + "..."
            
            return clean_content
            
        except Exception as e:
            logger.error(f"Failed to sanitize content: {e}")
            return content
    
    async def _extract_mentions(self, content: str) -> List[str]:
        """Extract user mentions from content"""
        try:
            mentions = self.mention_pattern.findall(content)
            return list(set(mentions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Failed to extract mentions: {e}")
            return []
    
    async def _create_thread(self, comment: Comment):
        """Create new comment thread"""
        try:
            thread_id = str(uuid.uuid4())
            
            thread = CommentThread(
                thread_id=thread_id,
                root_comment_id=comment.comment_id,
                content_id=comment.content_id,
                participant_ids={comment.user_id},
                comment_count=1,
                last_activity=comment.timestamp,
                is_resolved=False,
                resolver_id=None,
                resolved_at=None
            )
            
            self.comment_threads[thread_id] = thread
            
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
    
    async def _add_to_thread(self, comment: Comment):
        """Add comment to existing thread"""
        try:
            # Find thread by root comment
            thread = None
            for t in self.comment_threads.values():
                if t.root_comment_id == comment.parent_comment_id or \
                   comment.parent_comment_id in [c.comment_id for c in self._get_thread_comments(t.thread_id)]:
                    thread = t
                    break
            
            if thread:
                thread.participant_ids.add(comment.user_id)
                thread.comment_count += 1
                thread.last_activity = comment.timestamp
            
        except Exception as e:
            logger.error(f"Failed to add to thread: {e}")
    
    def _get_thread_comments(self, thread_id: str) -> List[Comment]:
        """Get all comments in thread"""
        thread = self.comment_threads.get(thread_id)
        if not thread:
            return []
        
        thread_comments = []
        root_comment = self.comments.get(thread.root_comment_id)
        if root_comment:
            thread_comments.append(root_comment)
            # Add replies recursively
            self._add_replies_to_list(root_comment.comment_id, thread_comments)
        
        return thread_comments
    
    def _add_replies_to_list(self, parent_id: str, comment_list: List[Comment]):
        """Recursively add replies to comment list"""
        for comment in self.comments.values():
            if comment.parent_comment_id == parent_id:
                comment_list.append(comment)
                self._add_replies_to_list(comment.comment_id, comment_list)
    
    async def _build_thread_structure(self, root_id: str, result: List[Dict[str, Any]]):
        """Build hierarchical thread structure"""
        try:
            for comment in self.comments.values():
                if comment.parent_comment_id == root_id:
                    comment_data = asdict(comment)
                    comment_data['replies'] = []
                    
                    # Recursively add replies
                    await self._build_thread_structure(comment.comment_id, comment_data['replies'])
                    
                    result.append(comment_data)
                    
        except Exception as e:
            logger.error(f"Failed to build thread structure: {e}")
    
    async def _process_mentions(self, comment: Comment):
        """Process user mentions in comment"""
        try:
            for mentioned_user in comment.mentions:
                self.user_mentions[mentioned_user].append(comment.comment_id)
                
                # Send mention notification
                await self._notify_user_mentioned(mentioned_user, comment)
                
        except Exception as e:
            logger.error(f"Failed to process mentions: {e}")
    
    async def _notify_comment_added(self, comment: Comment):
        """Notify about new comment"""
        try:
            notification = {
                'type': 'comment_added',
                'comment_id': comment.comment_id,
                'content_id': comment.content_id,
                'user_id': comment.user_id,
                'username': comment.username,
                'timestamp': comment.timestamp,
                'timeline_position': comment.timeline_position
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify comment added: {e}")
    
    async def _notify_comment_edited(self, comment: Comment):
        """Notify about comment edit"""
        try:
            notification = {
                'type': 'comment_edited',
                'comment_id': comment.comment_id,
                'user_id': comment.user_id,
                'edited_at': comment.edited_at
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify comment edited: {e}")
    
    async def _notify_comment_deleted(self, comment_id: str, user_id: str, soft_delete: bool):
        """Notify about comment deletion"""
        try:
            notification = {
                'type': 'comment_deleted',
                'comment_id': comment_id,
                'user_id': user_id,
                'soft_delete': soft_delete,
                'timestamp': time.time()
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify comment deleted: {e}")
    
    async def _notify_reaction_added(self, reaction: CommentReaction):
        """Notify about reaction added"""
        try:
            notification = {
                'type': 'reaction_added',
                'reaction_id': reaction.reaction_id,
                'comment_id': reaction.comment_id,
                'user_id': reaction.user_id,
                'reaction_type': reaction.reaction_type.value,
                'timestamp': reaction.timestamp
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify reaction added: {e}")
    
    async def _notify_reaction_removed(self, comment_id: str, user_id: str, reaction_type: ReactionType):
        """Notify about reaction removed"""
        try:
            notification = {
                'type': 'reaction_removed',
                'comment_id': comment_id,
                'user_id': user_id,
                'reaction_type': reaction_type.value,
                'timestamp': time.time()
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify reaction removed: {e}")
    
    async def _notify_user_mentioned(self, mentioned_user: str, comment: Comment):
        """Notify user about mention"""
        try:
            notification = {
                'type': 'user_mentioned',
                'mentioned_user': mentioned_user,
                'comment_id': comment.comment_id,
                'mentioner_id': comment.user_id,
                'mentioner_username': comment.username,
                'content_id': comment.content_id,
                'timestamp': comment.timestamp
            }
            
            await self._send_notification(notification, target_user=mentioned_user)
            
        except Exception as e:
            logger.error(f"Failed to notify user mentioned: {e}")
    
    async def _notify_thread_resolved(self, thread: CommentThread):
        """Notify about thread resolution"""
        try:
            notification = {
                'type': 'thread_resolved',
                'thread_id': thread.thread_id,
                'resolver_id': thread.resolver_id,
                'resolved_at': thread.resolved_at
            }
            
            await self._send_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to notify thread resolved: {e}")
    
    async def _send_notification(self, notification: Dict[str, Any], target_user: str = None):
        """Send notification to users"""
        try:
            # Send to all connected users or specific user
            if target_user:
                if target_user in self.websocket_connections:
                    websocket = self.websocket_connections[target_user]
                    await websocket.send(json.dumps(notification))
            else:
                for user_id, websocket in self.websocket_connections.items():
                    try:
                        await websocket.send(json.dumps(notification))
                    except:
                        # Remove broken connection
                        del self.websocket_connections[user_id]
                        
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def _store_comment_redis(self, comment: Comment):
        """Store comment in Redis"""
        try:
            if self.redis_client:
                key = f"comment:{comment.comment_id}"
                value = json.dumps(asdict(comment), default=str)
                self.redis_client.setex(key, 86400, value)  # 24 hour expiry
                
        except Exception as e:
            logger.error(f"Failed to store comment in Redis: {e}")

class TimelineCommentManager:
    """Specialized manager for timeline-based comments"""
    
    def __init__(self):
        self.comment_engine = CommentEngine()
        self.timeline_index = defaultdict(list)  # content_id -> [(timestamp, comment_id)]
        
    async def add_timeline_comment(self, content_id: str, user_id: str, username: str,
                                 content: str, timestamp: float,
                                 comment_type: CommentType = CommentType.FEEDBACK) -> Comment:
        """Add comment at specific timeline position"""
        comment = await self.comment_engine.add_timeline_comment(
            content_id, user_id, username, content, timestamp, comment_type
        )
        
        # Add to timeline index
        self.timeline_index[content_id].append((timestamp, comment.comment_id))
        self.timeline_index[content_id].sort()  # Keep sorted by timestamp
        
        return comment
    
    async def get_timeline_comments_range(self, content_id: str, 
                                        start_time: float, end_time: float) -> List[Comment]:
        """Get all comments within timeline range"""
        timeline_entries = self.timeline_index.get(content_id, [])
        
        # Find comments in range
        comment_ids_in_range = []
        for timestamp, comment_id in timeline_entries:
            if start_time <= timestamp <= end_time:
                comment_ids_in_range.append(comment_id)
        
        # Get comment objects
        comments = []
        for comment_id in comment_ids_in_range:
            comment = self.comment_engine.comments.get(comment_id)
            if comment and comment.status == CommentStatus.ACTIVE:
                comments.append(comment)
        
        return comments
    
    async def get_next_comment(self, content_id: str, current_timestamp: float) -> Optional[Comment]:
        """Get next comment after current timestamp"""
        timeline_entries = self.timeline_index.get(content_id, [])
        
        for timestamp, comment_id in timeline_entries:
            if timestamp > current_timestamp:
                comment = self.comment_engine.comments.get(comment_id)
                if comment and comment.status == CommentStatus.ACTIVE:
                    return comment
        
        return None
    
    async def get_previous_comment(self, content_id: str, current_timestamp: float) -> Optional[Comment]:
        """Get previous comment before current timestamp"""
        timeline_entries = self.timeline_index.get(content_id, [])
        
        # Search backwards
        for timestamp, comment_id in reversed(timeline_entries):
            if timestamp < current_timestamp:
                comment = self.comment_engine.comments.get(comment_id)
                if comment and comment.status == CommentStatus.ACTIVE:
                    return comment
        
        return None

# Module exports
__all__ = [
    'CommentEngine',
    'TimelineCommentManager',
    'Comment',
    'CommentReaction',
    'CommentThread',
    'CommentType',
    'CommentStatus',
    'ReactionType'
]