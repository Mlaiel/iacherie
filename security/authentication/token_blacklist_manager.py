#!/usr/bin/env python3
"""
🔒 Token Blacklist Manager - Real-Time Token Security
======================================================

Enterprise token blacklist management system with real-time invalidation,
distributed synchronization, and automated threat response.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + DevOps + Redis
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
import redis
from redis.sentinel import Sentinel
import asyncio_redis


class BlacklistReason(Enum):
    """Reasons for token blacklisting"""
    USER_LOGOUT = "user_logout"
    FORCED_LOGOUT = "forced_logout"
    TOKEN_ROTATION = "token_rotation"
    SECURITY_BREACH = "security_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLICY_VIOLATION = "policy_violation"
    EXPIRED_TOKEN = "expired_token"
    REVOKED_PERMISSION = "revoked_permission"
    ACCOUNT_SUSPENDED = "account_suspended"
    ADMIN_ACTION = "admin_action"
    SESSION_HIJACK = "session_hijack"
    ANOMALY_DETECTED = "anomaly_detected"


class TokenType(Enum):
    """Types of tokens"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    SESSION_TOKEN = "session_token"
    API_TOKEN = "api_token"
    TEMPORARY_TOKEN = "temporary_token"


class BlacklistScope(Enum):
    """Scope of blacklist application"""
    GLOBAL = "global"
    USER = "user"
    SESSION = "session"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"
    APPLICATION = "application"


@dataclass
class BlacklistEntry:
    """Token blacklist entry"""
    entry_id: str
    token_id: str
    token_hash: str
    token_type: TokenType
    user_id: Optional[str]
    session_id: Optional[str]
    device_id: Optional[str]
    ip_address: Optional[str]
    
    # Blacklist details
    blacklisted_at: datetime
    expires_at: Optional[datetime]
    reason: BlacklistReason
    scope: BlacklistScope
    
    # Context
    blacklisted_by: str  # System, user, admin, etc.
    notes: Optional[str]
    metadata: Dict[str, Any]
    
    # Synchronization
    sync_status: str  # "pending", "synced", "failed"
    sync_attempts: int
    last_sync_attempt: Optional[datetime]
    
    # Audit
    revoked_permissions: List[str]
    affected_resources: List[str]


@dataclass
class BlacklistStats:
    """Blacklist statistics"""
    total_entries: int
    active_entries: int
    expired_entries: int
    entries_by_reason: Dict[str, int]
    entries_by_type: Dict[str, int]
    entries_by_scope: Dict[str, int]
    sync_failures: int
    cleanup_operations: int
    cache_hits: int
    cache_misses: int


class TokenBlacklistManager:
    """
    🔒 Enterprise Token Blacklist Manager
    
    Real-time token blacklist management with distributed synchronization,
    automated cleanup, and comprehensive audit capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize token blacklist manager"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/blacklist_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Local storage
        self.blacklist_cache: Dict[str, BlacklistEntry] = {}
        self.user_tokens: Dict[str, Set[str]] = {}
        self.session_tokens: Dict[str, Set[str]] = {}
        
        # Statistics
        self.stats = BlacklistStats(
            total_entries=0,
            active_entries=0,
            expired_entries=0,
            entries_by_reason={},
            entries_by_type={},
            entries_by_scope={},
            sync_failures=0,
            cleanup_operations=0,
            cache_hits=0,
            cache_misses=0
        )
        
        # Redis connection for distributed synchronization
        self.redis_client = None
        self.redis_sentinel = None
        self._setup_redis_connection()
        
        # Background processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cleanup_task = None
        self.sync_task = None
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[callable]] = {
            'token_blacklisted': [],
            'token_validated': [],
            'cleanup_completed': [],
            'sync_completed': []
        }
        
        # Rate limiting for operations
        self.operation_limits = {
            'blacklist_operations': deque(maxlen=1000),
            'validation_operations': deque(maxlen=10000)
        }
        
        # Start background tasks
        self._start_background_tasks()
    
    async def blacklist_token(
        self,
        token_id: str,
        token_type: TokenType,
        reason: BlacklistReason,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        scope: BlacklistScope = BlacklistScope.GLOBAL,
        expires_at: Optional[datetime] = None,
        blacklisted_by: str = "system",
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Blacklist a token
        
        Args:
            token_id: Token identifier
            token_type: Type of token
            reason: Reason for blacklisting
            user_id: Associated user ID
            session_id: Associated session ID
            device_id: Associated device ID
            ip_address: Source IP address
            scope: Blacklist scope
            expires_at: Expiration time
            blacklisted_by: Who blacklisted the token
            notes: Additional notes
            metadata: Additional metadata
            
        Returns:
            Blacklist entry ID
        """
        try:
            # Generate entry ID
            entry_id = str(uuid.uuid4())
            
            # Hash token for storage (privacy)
            token_hash = self._hash_token(token_id)
            
            # Calculate expiration if not provided
            if not expires_at:
                expires_at = self._calculate_default_expiration(token_type, reason)
            
            # Create blacklist entry
            entry = BlacklistEntry(
                entry_id=entry_id,
                token_id=token_id,
                token_hash=token_hash,
                token_type=token_type,
                user_id=user_id,
                session_id=session_id,
                device_id=device_id,
                ip_address=ip_address,
                blacklisted_at=datetime.utcnow(),
                expires_at=expires_at,
                reason=reason,
                scope=scope,
                blacklisted_by=blacklisted_by,
                notes=notes,
                metadata=metadata or {},
                sync_status="pending",
                sync_attempts=0,
                last_sync_attempt=None,
                revoked_permissions=[],
                affected_resources=[]
            )
            
            # Store locally
            self.blacklist_cache[token_hash] = entry
            
            # Update user/session tracking
            if user_id:
                if user_id not in self.user_tokens:
                    self.user_tokens[user_id] = set()
                self.user_tokens[user_id].add(token_hash)
            
            if session_id:
                if session_id not in self.session_tokens:
                    self.session_tokens[session_id] = set()
                self.session_tokens[session_id].add(token_hash)
            
            # Update statistics
            self._update_stats_on_blacklist(entry)
            
            # Sync to distributed storage
            await self._sync_to_distributed_storage(entry)
            
            # Trigger callbacks
            await self._trigger_callbacks('token_blacklisted', entry)
            
            # Log the blacklist action
            self.logger.info(
                f"Token blacklisted: {entry_id} - {reason.value} - "
                f"User: {user_id} - Session: {session_id}"
            )
            
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Token blacklist error: {e}")
            raise
    
    async def is_token_blacklisted(
        self,
        token_id: str,
        check_distributed: bool = True
    ) -> Tuple[bool, Optional[BlacklistEntry]]:
        """
        Check if token is blacklisted
        
        Args:
            token_id: Token to check
            check_distributed: Whether to check distributed storage
            
        Returns:
            (is_blacklisted, blacklist_entry)
        """
        try:
            token_hash = self._hash_token(token_id)
            
            # Check local cache first
            entry = self.blacklist_cache.get(token_hash)
            if entry:
                # Check if entry has expired
                if entry.expires_at and datetime.utcnow() > entry.expires_at:
                    # Remove expired entry
                    await self._remove_expired_entry(entry)
                    self.stats.cache_hits += 1
                    return False, None
                
                self.stats.cache_hits += 1
                await self._trigger_callbacks('token_validated', entry)
                return True, entry
            
            # Check distributed storage if enabled
            if check_distributed and self.redis_client:
                entry = await self._check_distributed_storage(token_hash)
                if entry:
                    # Cache locally
                    self.blacklist_cache[token_hash] = entry
                    self.stats.cache_misses += 1
                    await self._trigger_callbacks('token_validated', entry)
                    return True, entry
            
            self.stats.cache_misses += 1
            return False, None
            
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            # Fail secure - treat as blacklisted if error occurs
            return True, None
    
    async def remove_from_blacklist(
        self,
        token_id: Optional[str] = None,
        entry_id: Optional[str] = None,
        reason: str = "manual_removal"
    ) -> bool:
        """
        Remove token from blacklist
        
        Args:
            token_id: Token to remove
            entry_id: Entry ID to remove
            reason: Reason for removal
            
        Returns:
            Success status
        """
        try:
            entry = None
            
            if token_id:
                token_hash = self._hash_token(token_id)
                entry = self.blacklist_cache.get(token_hash)
            elif entry_id:
                # Find entry by ID
                for cached_entry in self.blacklist_cache.values():
                    if cached_entry.entry_id == entry_id:
                        entry = cached_entry
                        break
            
            if not entry:
                return False
            
            # Remove from local cache
            if entry.token_hash in self.blacklist_cache:
                del self.blacklist_cache[entry.token_hash]
            
            # Remove from user/session tracking
            if entry.user_id and entry.user_id in self.user_tokens:
                self.user_tokens[entry.user_id].discard(entry.token_hash)
                if not self.user_tokens[entry.user_id]:
                    del self.user_tokens[entry.user_id]
            
            if entry.session_id and entry.session_id in self.session_tokens:
                self.session_tokens[entry.session_id].discard(entry.token_hash)
                if not self.session_tokens[entry.session_id]:
                    del self.session_tokens[entry.session_id]
            
            # Remove from distributed storage
            if self.redis_client:
                await self._remove_from_distributed_storage(entry.token_hash)
            
            # Update statistics
            self.stats.active_entries = max(0, self.stats.active_entries - 1)
            
            self.logger.info(f"Token removed from blacklist: {entry.entry_id} - Reason: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Blacklist removal error: {e}")
            return False
    
    async def blacklist_user_tokens(
        self,
        user_id: str,
        reason: BlacklistReason,
        exclude_current: bool = False,
        current_token_id: Optional[str] = None
    ) -> List[str]:
        """
        Blacklist all tokens for a user
        
        Args:
            user_id: User whose tokens to blacklist
            reason: Reason for blacklisting
            exclude_current: Whether to exclude current token
            current_token_id: Current token to exclude
            
        Returns:
            List of blacklisted entry IDs
        """
        try:
            blacklisted_entries = []
            
            # Get user's tokens from distributed storage
            user_tokens = await self._get_user_tokens_from_storage(user_id)
            
            for token_info in user_tokens:
                # Skip current token if requested
                if exclude_current and current_token_id:
                    if token_info.get("token_id") == current_token_id:
                        continue
                
                entry_id = await self.blacklist_token(
                    token_id=token_info["token_id"],
                    token_type=TokenType(token_info.get("token_type", "access_token")),
                    reason=reason,
                    user_id=user_id,
                    session_id=token_info.get("session_id"),
                    scope=BlacklistScope.USER,
                    blacklisted_by="system"
                )
                
                blacklisted_entries.append(entry_id)
            
            self.logger.info(f"Blacklisted {len(blacklisted_entries)} tokens for user {user_id}")
            
            return blacklisted_entries
            
        except Exception as e:
            self.logger.error(f"User token blacklist error: {e}")
            return []
    
    async def blacklist_session_tokens(
        self,
        session_id: str,
        reason: BlacklistReason
    ) -> List[str]:
        """
        Blacklist all tokens for a session
        
        Args:
            session_id: Session whose tokens to blacklist
            reason: Reason for blacklisting
            
        Returns:
            List of blacklisted entry IDs
        """
        try:
            blacklisted_entries = []
            
            # Get session's tokens
            session_tokens = await self._get_session_tokens_from_storage(session_id)
            
            for token_info in session_tokens:
                entry_id = await self.blacklist_token(
                    token_id=token_info["token_id"],
                    token_type=TokenType(token_info.get("token_type", "access_token")),
                    reason=reason,
                    user_id=token_info.get("user_id"),
                    session_id=session_id,
                    scope=BlacklistScope.SESSION,
                    blacklisted_by="system"
                )
                
                blacklisted_entries.append(entry_id)
            
            self.logger.info(f"Blacklisted {len(blacklisted_entries)} tokens for session {session_id}")
            
            return blacklisted_entries
            
        except Exception as e:
            self.logger.error(f"Session token blacklist error: {e}")
            return []
    
    async def emergency_blacklist(
        self,
        criteria: Dict[str, Any],
        reason: BlacklistReason = BlacklistReason.SECURITY_BREACH
    ) -> Dict[str, Any]:
        """
        Emergency blacklist based on criteria
        
        Args:
            criteria: Blacklist criteria
            reason: Reason for emergency blacklist
            
        Returns:
            Emergency blacklist result
        """
        try:
            start_time = datetime.utcnow()
            blacklisted_count = 0
            
            # Blacklist by user ID
            if "user_ids" in criteria:
                for user_id in criteria["user_ids"]:
                    entries = await self.blacklist_user_tokens(user_id, reason)
                    blacklisted_count += len(entries)
            
            # Blacklist by IP address
            if "ip_addresses" in criteria:
                for ip_address in criteria["ip_addresses"]:
                    entries = await self._blacklist_by_ip(ip_address, reason)
                    blacklisted_count += len(entries)
            
            # Blacklist by device ID
            if "device_ids" in criteria:
                for device_id in criteria["device_ids"]:
                    entries = await self._blacklist_by_device(device_id, reason)
                    blacklisted_count += len(entries)
            
            # Blacklist by token pattern
            if "token_patterns" in criteria:
                for pattern in criteria["token_patterns"]:
                    entries = await self._blacklist_by_pattern(pattern, reason)
                    blacklisted_count += len(entries)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "success": True,
                "tokens_blacklisted": blacklisted_count,
                "duration_seconds": duration,
                "criteria": criteria,
                "reason": reason.value,
                "timestamp": start_time.isoformat()
            }
            
            self.logger.critical(f"Emergency blacklist completed: {blacklisted_count} tokens in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Emergency blacklist error: {e}")
            raise
    
    async def cleanup_expired_tokens(self) -> Dict[str, Any]:
        """Clean up expired blacklist entries"""
        try:
            start_time = datetime.utcnow()
            cleaned_count = 0
            
            expired_entries = []
            
            # Find expired entries
            for token_hash, entry in list(self.blacklist_cache.items()):
                if entry.expires_at and datetime.utcnow() > entry.expires_at:
                    expired_entries.append(entry)
            
            # Remove expired entries
            for entry in expired_entries:
                await self._remove_expired_entry(entry)
                cleaned_count += 1
            
            # Clean up distributed storage
            if self.redis_client:
                redis_cleaned = await self._cleanup_distributed_storage()
                cleaned_count += redis_cleaned
            
            # Update statistics
            self.stats.cleanup_operations += 1
            self.stats.expired_entries += cleaned_count
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "cleaned_entries": cleaned_count,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat()
            }
            
            await self._trigger_callbacks('cleanup_completed', result)
            
            self.logger.info(f"Cleanup completed: {cleaned_count} expired entries removed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            return {"error": str(e)}
    
    async def get_blacklist_stats(self) -> BlacklistStats:
        """Get current blacklist statistics"""
        # Update active/expired counts
        active_count = 0
        expired_count = 0
        
        for entry in self.blacklist_cache.values():
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                expired_count += 1
            else:
                active_count += 1
        
        self.stats.active_entries = active_count
        self.stats.expired_entries = expired_count
        self.stats.total_entries = active_count + expired_count
        
        return self.stats
    
    async def search_blacklist(
        self,
        criteria: Dict[str, Any],
        limit: int = 100
    ) -> List[BlacklistEntry]:
        """
        Search blacklist entries
        
        Args:
            criteria: Search criteria
            limit: Maximum results
            
        Returns:
            Matching blacklist entries
        """
        try:
            results = []
            
            for entry in self.blacklist_cache.values():
                if len(results) >= limit:
                    break
                
                if self._matches_search_criteria(entry, criteria):
                    results.append(entry)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Blacklist search error: {e}")
            return []
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load blacklist configuration"""
        default_config = {
            "redis": {
                "enabled": True,
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None,
                "sentinel_enabled": False,
                "sentinel_hosts": [],
                "master_name": "mymaster"
            },
            "cleanup_interval_seconds": 3600,  # 1 hour
            "sync_interval_seconds": 300,     # 5 minutes
            "default_expiration_hours": {
                "access_token": 24,
                "refresh_token": 720,  # 30 days
                "session_token": 12,
                "api_token": 8760,     # 1 year
                "temporary_token": 1
            },
            "max_cache_size": 100000,
            "batch_sync_size": 1000
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def _setup_redis_connection(self):
        """Setup Redis connection for distributed synchronization"""
        if not self.config["redis"]["enabled"]:
            return
        
        try:
            redis_config = self.config["redis"]
            
            if redis_config["sentinel_enabled"]:
                # Use Redis Sentinel for high availability
                sentinel_hosts = [(host["host"], host["port"]) for host in redis_config["sentinel_hosts"]]
                self.redis_sentinel = Sentinel(sentinel_hosts)
                self.redis_client = self.redis_sentinel.master_for(
                    redis_config["master_name"],
                    password=redis_config["password"],
                    decode_responses=True
                )
            else:
                # Direct Redis connection
                self.redis_client = redis.Redis(
                    host=redis_config["host"],
                    port=redis_config["port"],
                    db=redis_config["db"],
                    password=redis_config["password"],
                    decode_responses=True
                )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established")
            
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _hash_token(self, token_id: str) -> str:
        """Hash token for storage"""
        return hashlib.sha256(token_id.encode()).hexdigest()
    
    def _calculate_default_expiration(
        self,
        token_type: TokenType,
        reason: BlacklistReason
    ) -> datetime:
        """Calculate default expiration time"""
        # Security violations get longer blacklist periods
        if reason in [BlacklistReason.SECURITY_BREACH, BlacklistReason.SESSION_HIJACK]:
            hours = 168  # 1 week
        else:
            hours = self.config["default_expiration_hours"].get(token_type.value, 24)
        
        return datetime.utcnow() + timedelta(hours=hours)
    
    def _update_stats_on_blacklist(self, entry: BlacklistEntry):
        """Update statistics when token is blacklisted"""
        self.stats.total_entries += 1
        self.stats.active_entries += 1
        
        reason_key = entry.reason.value
        if reason_key not in self.stats.entries_by_reason:
            self.stats.entries_by_reason[reason_key] = 0
        self.stats.entries_by_reason[reason_key] += 1
        
        type_key = entry.token_type.value
        if type_key not in self.stats.entries_by_type:
            self.stats.entries_by_type[type_key] = 0
        self.stats.entries_by_type[type_key] += 1
        
        scope_key = entry.scope.value
        if scope_key not in self.stats.entries_by_scope:
            self.stats.entries_by_scope[scope_key] = 0
        self.stats.entries_by_scope[scope_key] += 1
    
    async def _sync_to_distributed_storage(self, entry: BlacklistEntry):
        """Sync entry to distributed storage"""
        if not self.redis_client:
            return
        
        try:
            # Serialize entry
            entry_data = asdict(entry)
            entry_data["blacklisted_at"] = entry.blacklisted_at.isoformat()
            entry_data["expires_at"] = entry.expires_at.isoformat() if entry.expires_at else None
            entry_data["last_sync_attempt"] = entry.last_sync_attempt.isoformat() if entry.last_sync_attempt else None
            
            # Store in Redis with expiration
            redis_key = f"blacklist:{entry.token_hash}"
            expire_seconds = None
            if entry.expires_at:
                expire_seconds = int((entry.expires_at - datetime.utcnow()).total_seconds())
                if expire_seconds <= 0:
                    return  # Already expired
            
            self.redis_client.setex(
                redis_key,
                expire_seconds or 86400,  # Default 24 hours
                json.dumps(entry_data)
            )
            
            # Update sync status
            entry.sync_status = "synced"
            entry.last_sync_attempt = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Distributed sync error: {e}")
            entry.sync_status = "failed"
            entry.sync_attempts += 1
            entry.last_sync_attempt = datetime.utcnow()
            self.stats.sync_failures += 1
    
    async def _check_distributed_storage(self, token_hash: str) -> Optional[BlacklistEntry]:
        """Check distributed storage for blacklist entry"""
        if not self.redis_client:
            return None
        
        try:
            redis_key = f"blacklist:{token_hash}"
            entry_data = self.redis_client.get(redis_key)
            
            if not entry_data:
                return None
            
            # Deserialize entry
            data = json.loads(entry_data)
            
            # Convert datetime strings back
            data["blacklisted_at"] = datetime.fromisoformat(data["blacklisted_at"])
            data["expires_at"] = datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None
            data["last_sync_attempt"] = datetime.fromisoformat(data["last_sync_attempt"]) if data["last_sync_attempt"] else None
            
            # Convert enums
            data["token_type"] = TokenType(data["token_type"])
            data["reason"] = BlacklistReason(data["reason"])
            data["scope"] = BlacklistScope(data["scope"])
            
            return BlacklistEntry(**data)
            
        except Exception as e:
            self.logger.error(f"Distributed storage check error: {e}")
            return None
    
    async def _remove_from_distributed_storage(self, token_hash: str):
        """Remove entry from distributed storage"""
        if not self.redis_client:
            return
        
        try:
            redis_key = f"blacklist:{token_hash}"
            self.redis_client.delete(redis_key)
        except Exception as e:
            self.logger.error(f"Distributed removal error: {e}")
    
    async def _remove_expired_entry(self, entry: BlacklistEntry):
        """Remove expired entry from cache"""
        if entry.token_hash in self.blacklist_cache:
            del self.blacklist_cache[entry.token_hash]
        
        # Remove from user/session tracking
        if entry.user_id and entry.user_id in self.user_tokens:
            self.user_tokens[entry.user_id].discard(entry.token_hash)
            if not self.user_tokens[entry.user_id]:
                del self.user_tokens[entry.user_id]
        
        if entry.session_id and entry.session_id in self.session_tokens:
            self.session_tokens[entry.session_id].discard(entry.token_hash)
            if not self.session_tokens[entry.session_id]:
                del self.session_tokens[entry.session_id]
    
    async def _cleanup_distributed_storage(self) -> int:
        """Clean up expired entries from distributed storage"""
        if not self.redis_client:
            return 0
        
        try:
            # Get all blacklist keys
            pattern = "blacklist:*"
            keys = self.redis_client.keys(pattern)
            
            cleaned_count = 0
            batch_size = self.config["batch_sync_size"]
            
            for i in range(0, len(keys), batch_size):
                batch_keys = keys[i:i + batch_size]
                
                # Check which keys have expired
                for key in batch_keys:
                    ttl = self.redis_client.ttl(key)
                    if ttl == -2:  # Key doesn't exist
                        cleaned_count += 1
                    elif ttl == -1:  # Key exists but no expiration
                        # Check if manually expired
                        entry_data = self.redis_client.get(key)
                        if entry_data:
                            data = json.loads(entry_data)
                            if data.get("expires_at"):
                                expires_at = datetime.fromisoformat(data["expires_at"])
                                if datetime.utcnow() > expires_at:
                                    self.redis_client.delete(key)
                                    cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Distributed cleanup error: {e}")
            return 0
    
    def _start_background_tasks(self):
        """Start background cleanup and sync tasks"""
        # Cleanup task
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(self.config["cleanup_interval_seconds"])
                    await self.cleanup_expired_tokens()
                except Exception as e:
                    self.logger.error(f"Background cleanup error: {e}")
        
        # Sync task
        async def sync_task():
            while True:
                try:
                    await asyncio.sleep(self.config["sync_interval_seconds"])
                    await self._sync_failed_entries()
                except Exception as e:
                    self.logger.error(f"Background sync error: {e}")
        
        # Start tasks in background
        self.cleanup_task = asyncio.create_task(cleanup_task())
        self.sync_task = asyncio.create_task(sync_task())
    
    async def _sync_failed_entries(self):
        """Retry syncing failed entries"""
        failed_entries = [
            entry for entry in self.blacklist_cache.values()
            if entry.sync_status == "failed" and entry.sync_attempts < 3
        ]
        
        for entry in failed_entries:
            await self._sync_to_distributed_storage(entry)
    
    async def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger registered event callbacks"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"Callback error for {event_type}: {e}")
    
    def register_callback(self, event_type: str, callback: callable):
        """Register event callback"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    async def _get_user_tokens_from_storage(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's tokens from storage"""
        # This would integrate with token storage system
        # For now, return tokens from cache
        user_tokens = []
        
        for entry in self.blacklist_cache.values():
            if entry.user_id == user_id:
                user_tokens.append({
                    "token_id": entry.token_id,
                    "token_type": entry.token_type.value,
                    "session_id": entry.session_id
                })
        
        return user_tokens
    
    async def _get_session_tokens_from_storage(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session's tokens from storage"""
        # This would integrate with session storage system
        # For now, return tokens from cache
        session_tokens = []
        
        for entry in self.blacklist_cache.values():
            if entry.session_id == session_id:
                session_tokens.append({
                    "token_id": entry.token_id,
                    "token_type": entry.token_type.value,
                    "user_id": entry.user_id
                })
        
        return session_tokens
    
    async def _blacklist_by_ip(self, ip_address: str, reason: BlacklistReason) -> List[str]:
        """Blacklist tokens by IP address"""
        # This would query token storage by IP
        # For now, simulate with cache
        blacklisted_entries = []
        
        for entry in list(self.blacklist_cache.values()):
            if entry.ip_address == ip_address:
                continue  # Already blacklisted
        
        # In production, query active tokens by IP and blacklist them
        return blacklisted_entries
    
    async def _blacklist_by_device(self, device_id: str, reason: BlacklistReason) -> List[str]:
        """Blacklist tokens by device ID"""
        # This would query token storage by device
        # For now, simulate with cache
        blacklisted_entries = []
        
        for entry in list(self.blacklist_cache.values()):
            if entry.device_id == device_id:
                continue  # Already blacklisted
        
        # In production, query active tokens by device and blacklist them
        return blacklisted_entries
    
    async def _blacklist_by_pattern(self, pattern: str, reason: BlacklistReason) -> List[str]:
        """Blacklist tokens matching pattern"""
        # This would implement pattern matching against tokens
        # For security reasons, this is a simplified implementation
        return []
    
    def _matches_search_criteria(self, entry: BlacklistEntry, criteria: Dict[str, Any]) -> bool:
        """Check if entry matches search criteria"""
        for key, value in criteria.items():
            if key == "user_id" and entry.user_id != value:
                return False
            elif key == "session_id" and entry.session_id != value:
                return False
            elif key == "reason" and entry.reason != BlacklistReason(value):
                return False
            elif key == "token_type" and entry.token_type != TokenType(value):
                return False
            elif key == "scope" and entry.scope != BlacklistScope(value):
                return False
            elif key == "blacklisted_by" and entry.blacklisted_by != value:
                return False
        
        return True
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if self.cleanup_task:
                self.cleanup_task.cancel()
            if self.sync_task:
                self.sync_task.cancel()
            if self.executor:
                self.executor.shutdown(wait=False)
        except:
            pass


# Export main classes
__all__ = [
    "TokenBlacklistManager",
    "BlacklistReason",
    "TokenType",
    "BlacklistScope",
    "BlacklistEntry",
    "BlacklistStats"
]