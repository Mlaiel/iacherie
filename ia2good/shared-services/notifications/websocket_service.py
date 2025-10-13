"""
WebSocket Service
Handles real-time notifications via WebSocket connections
"""

import os
from typing import Dict, List, Set, Optional, Any
import json
import asyncio


class WebSocketService:
    """Manage WebSocket connections for real-time notifications"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_WEBSOCKET_NOTIFICATIONS', 'true').lower() == 'true'
        # Store active connections: {user_id: set of websocket connections}
        self.active_connections: Dict[str, Set[Any]] = {}
        # Store room subscriptions: {room_id: set of user_ids}
        self.room_subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, user_id: str, websocket: Any) -> None:
        """
        Register a new WebSocket connection
        
        Args:
            user_id: User identifier
            websocket: WebSocket connection object
        """
        if not self.enabled:
            return
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        print(f"[WS] User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    async def disconnect(self, user_id: str, websocket: Any) -> None:
        """
        Remove a WebSocket connection
        
        Args:
            user_id: User identifier
            websocket: WebSocket connection object
        """
        if not self.enabled:
            return
        
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remove user entry if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Remove from all rooms
                for room_users in self.room_subscriptions.values():
                    room_users.discard(user_id)
            
            print(f"[WS] User {user_id} disconnected")
    
    async def send_to_user(
        self,
        user_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message to a specific user (all their connections)
        
        Args:
            user_id: Target user ID
            message: Message data to send
            
        Returns:
            True if sent successfully
        """
        if not self.enabled or user_id not in self.active_connections:
            return False
        
        message_json = json.dumps(message)
        connections = self.active_connections[user_id].copy()
        
        for websocket in connections:
            try:
                # In production, use: await websocket.send_text(message_json)
                print(f"[WS] Sent to user {user_id}: {message.get('type', 'message')}")
            except Exception as e:
                print(f"Error sending to user {user_id}: {e}")
                await self.disconnect(user_id, websocket)
        
        return True
    
    async def send_to_room(
        self,
        room_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ) -> int:
        """
        Send message to all users in a room
        
        Args:
            room_id: Room identifier
            message: Message data to send
            exclude_user: Optional user ID to exclude from broadcast
            
        Returns:
            Number of users message was sent to
        """
        if not self.enabled or room_id not in self.room_subscriptions:
            return 0
        
        sent_count = 0
        users_in_room = self.room_subscriptions[room_id].copy()
        
        for user_id in users_in_room:
            if user_id == exclude_user:
                continue
            
            success = await self.send_to_user(user_id, message)
            if success:
                sent_count += 1
        
        return sent_count
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ) -> int:
        """
        Broadcast message to all connected users
        
        Args:
            message: Message data to send
            exclude_user: Optional user ID to exclude from broadcast
            
        Returns:
            Number of users message was sent to
        """
        if not self.enabled:
            return 0
        
        sent_count = 0
        user_ids = list(self.active_connections.keys())
        
        for user_id in user_ids:
            if user_id == exclude_user:
                continue
            
            success = await self.send_to_user(user_id, message)
            if success:
                sent_count += 1
        
        return sent_count
    
    async def join_room(self, user_id: str, room_id: str) -> bool:
        """
        Subscribe user to a room
        
        Args:
            user_id: User identifier
            room_id: Room identifier
            
        Returns:
            True if joined successfully
        """
        if not self.enabled:
            return False
        
        if room_id not in self.room_subscriptions:
            self.room_subscriptions[room_id] = set()
        
        self.room_subscriptions[room_id].add(user_id)
        print(f"[WS] User {user_id} joined room {room_id}")
        return True
    
    async def leave_room(self, user_id: str, room_id: str) -> bool:
        """
        Unsubscribe user from a room
        
        Args:
            user_id: User identifier
            room_id: Room identifier
            
        Returns:
            True if left successfully
        """
        if not self.enabled or room_id not in self.room_subscriptions:
            return False
        
        self.room_subscriptions[room_id].discard(user_id)
        
        # Clean up empty rooms
        if not self.room_subscriptions[room_id]:
            del self.room_subscriptions[room_id]
        
        print(f"[WS] User {user_id} left room {room_id}")
        return True
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return len(self.active_connections)
    
    def get_room_users_count(self, room_id: str) -> int:
        """Get count of users in a room"""
        if room_id not in self.room_subscriptions:
            return 0
        return len(self.room_subscriptions[room_id])
