"""Data Synchronization Engine - Real-time Multi-Platform Data Sync

Ultra-advanced data synchronization system ensuring consistent, real-time data flow
across all platform integrations with conflict resolution, data validation, and audit trails.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from enum import Enum
import uuid
from dataclasses import dataclass, field
from collections import defaultdict

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert

from .platform_connections import (
    PlatformConnection, PlatformAnalytics, PlatformRevenue,
    PlatformContentMetadata, Platform
)
from .revenue_models import RevenueRecord
from ..core.exceptions import DataSyncError, ConflictResolutionError
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class SyncConflictType(Enum):
    """Types of data synchronization conflicts"""    DUPLICATE_RECORD = "duplicate_record"
    VERSION_MISMATCH = "version_mismatch"
    DATA_INCONSISTENCY = "data_inconsistency"
    CURRENCY_MISMATCH = "currency_mismatch"
    TIMESTAMP_CONFLICT = "timestamp_conflict"
    PLATFORM_DISCREPANCY = "platform_discrepancy"


class SyncStrategy(Enum):
    """Data synchronization strategies"""    MERGE_LATEST = "merge_latest"
    PLATFORM_PRIORITY = "platform_priority"
    MANUAL_REVIEW = "manual_review"
    HIGHEST_VALUE = "highest_value"
    AGGREGATE_SUM = "aggregate_sum"
    KEEP_BOTH = "keep_both"


@dataclass
class SyncConflict:
    """Data synchronization conflict representation"""    conflict_id: str
    conflict_type: SyncConflictType
    platform_source: Platform
    affected_records: List[str]
    conflict_data: Dict[str, Any]
    suggested_resolution: SyncStrategy
    confidence_score: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SyncResult:
    """Synchronization operation result"""    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_skipped: int
    conflicts_detected: int
    conflicts_resolved: int
    errors: List[str]
    processing_time_seconds: float
    sync_metadata: Dict[str, Any]


class DataSynchronizationEngine:
    """    Ultra-advanced data synchronization engine with intelligent conflict resolution,
    real-time data validation, and comprehensive audit trails
    """    
    def __init__(self):
        self.redis_client = None
        self.conflict_resolvers = {}
        self.data_validators = {}
        self.sync_locks = {}
        
        # Initialize conflict resolution strategies
        self._initialize_conflict_resolvers()
        self._initialize_data_validators()
    
    async def initialize(self):
        """Initialize Redis connection and other async resources"""        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    def _initialize_conflict_resolvers(self):
        """Initialize conflict resolution strategies"""        self.conflict_resolvers = {
            SyncConflictType.DUPLICATE_RECORD: self._resolve_duplicate_record,
            SyncConflictType.VERSION_MISMATCH: self._resolve_version_mismatch,
            SyncConflictType.DATA_INCONSISTENCY: self._resolve_data_inconsistency,
            SyncConflictType.CURRENCY_MISMATCH: self._resolve_currency_mismatch,
            SyncConflictType.TIMESTAMP_CONFLICT: self._resolve_timestamp_conflict,
            SyncConflictType.PLATFORM_DISCREPANCY: self._resolve_platform_discrepancy
        }
    
    def _initialize_data_validators(self):
        """Initialize data validation rules"""        self.data_validators = {
            "analytics": self._validate_analytics_data,
            "revenue": self._validate_revenue_data,
            "content": self._validate_content_data
        }
    
    async def synchronize_platform_data(
        self,
        session: AsyncSession,
        user_id: str,
        platform_data: Dict[str, List[Dict[str, Any]]],
        sync_strategy: SyncStrategy = SyncStrategy.MERGE_LATEST
    ) -> SyncResult:
        """        Synchronize data from multiple platforms with intelligent conflict resolution
        """        start_time = datetime.now(timezone.utc)
        
        result = SyncResult(
            success=True,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_skipped=0,
            conflicts_detected=0,
            conflicts_resolved=0,
            errors=[],
            processing_time_seconds=0,
            sync_metadata={}
        )
        
        try:
            # Acquire sync lock for user
            lock_key = f"sync_lock:{user_id}"
            async with self._acquire_sync_lock(lock_key):
                
                # Process each data type
                for data_type, records in platform_data.items():
                    if data_type not in self.data_validators:
                        result.errors.append(f"Unknown data type: {data_type}")
                        continue
                    
                    type_result = await self._sync_data_type(
                        session, user_id, data_type, records, sync_strategy
                    )
                    
                    # Aggregate results
                    result.records_processed += type_result.records_processed
                    result.records_created += type_result.records_created
                    result.records_updated += type_result.records_updated
                    result.records_skipped += type_result.records_skipped
                    result.conflicts_detected += type_result.conflicts_detected
                    result.conflicts_resolved += type_result.conflicts_resolved
                    result.errors.extend(type_result.errors)
                    result.sync_metadata[data_type] = type_result.sync_metadata
                
                # Commit all changes
                await session.commit()
                
                # Update sync cache
                await self._update_sync_cache(user_id, result)
                
        except Exception as e:
            await session.rollback()
            result.success = False
            result.errors.append(f"Sync failed: {str(e)}")
            logger.error(f"Data synchronization failed for user {user_id}: {str(e)}")
        
        # Calculate processing time
        result.processing_time_seconds = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        
        return result
    
    async def _sync_data_type(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        records: List[Dict[str, Any]],
        sync_strategy: SyncStrategy
    ) -> SyncResult:
        """Synchronize a specific data type with conflict resolution"""        
        result = SyncResult(
            success=True,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_skipped=0,
            conflicts_detected=0,
            conflicts_resolved=0,
            errors=[],
            processing_time_seconds=0,
            sync_metadata={}
        )
        
        # Validate data before processing
        validated_records = []
        for record in records:
            validation_result = await self.data_validators[data_type](record)
            if validation_result["valid"]:
                validated_records.append(record)
            else:
                result.errors.append(f"Validation failed: {validation_result['error']}")
                result.records_skipped += 1
        
        # Group records by unique identifiers for conflict detection
        record_groups = await self._group_records_by_identity(
            session, user_id, data_type, validated_records
        )
        
        # Process each record group
        for group_key, group_records in record_groups.items():
            try:
                group_result = await self._process_record_group(
                    session, user_id, data_type, group_records, sync_strategy
                )
                
                result.records_processed += len(group_records)
                result.records_created += group_result.get("created", 0)
                result.records_updated += group_result.get("updated", 0)
                result.conflicts_detected += group_result.get("conflicts", 0)
                result.conflicts_resolved += group_result.get("resolved", 0)
                
            except Exception as e:
                result.errors.append(f"Failed to process group {group_key}: {str(e)}")
                logger.error(f"Record group processing failed: {str(e)}")
        
        return result
    
    async def _group_records_by_identity(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group records by their unique identity for conflict detection"""        
        groups = defaultdict(list)
        
        for record in records:
            # Generate unique key based on data type
            if data_type == "analytics":
                key = f"{record.get('platform')}:{record.get('content_id')}:{record.get('date')}:{record.get('metric_type')}"
            elif data_type == "revenue":
                key = f"{record.get('platform')}:{record.get('content_id')}:{record.get('date')}:{record.get('revenue_stream')}"
            elif data_type == "content":
                key = f"{record.get('platform')}:{record.get('content_id')}"
            else:
                # Generic key generation
                key = f"{record.get('platform')}:{record.get('id', uuid.uuid4())}"
            
            groups[key].append(record)
        
        return dict(groups)
    
    async def _process_record_group(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        records: List[Dict[str, Any]],
        sync_strategy: SyncStrategy
    ) -> Dict[str, int]:
        """Process a group of potentially conflicting records"""        
        result = {"created": 0, "updated": 0, "conflicts": 0, "resolved": 0}
        
        if len(records) == 1:
            # Single record, no conflicts
            success = await self._create_or_update_record(
                session, user_id, data_type, records[0]
            )
            if success:
                result["created"] = 1
            return result
        
        # Multiple records, potential conflict
        result["conflicts"] = 1
        
        # Check for existing records in database
        existing_records = await self._find_existing_records(
            session, user_id, data_type, records[0]
        )
        
        # Detect conflict type
        conflict_type = await self._detect_conflict_type(records, existing_records)
        
        # Create conflict object
        conflict = SyncConflict(
            conflict_id=str(uuid.uuid4()),
            conflict_type=conflict_type,
            platform_source=Platform(records[0].get("platform")),
            affected_records=[str(r.get("id", uuid.uuid4())) for r in records],
            conflict_data={
                "new_records": records,
                "existing_records": [self._record_to_dict(r) for r in existing_records]
            },
            suggested_resolution=sync_strategy,
            confidence_score=0.8
        )
        
        # Resolve conflict
        resolution_result = await self._resolve_conflict(
            session, user_id, data_type, conflict
        )
        
        if resolution_result["success"]:
            result["resolved"] = 1
            result["created"] = resolution_result.get("created", 0)
            result["updated"] = resolution_result.get("updated", 0)
        
        return result
    
    async def _detect_conflict_type(
        self,
        new_records: List[Dict[str, Any]],
        existing_records: List[Any]
    ) -> SyncConflictType:
        """Detect the type of conflict between records"""        
        if len(existing_records) > 0 and len(new_records) > 1:
            return SyncConflictType.DUPLICATE_RECORD
        
        if len(existing_records) > 0:
            # Check for version mismatches
            existing_record = existing_records[0]
            new_record = new_records[0]
            
            # Compare timestamps
            if hasattr(existing_record, 'updated_at') and 'updated_at' in new_record:
                existing_time = existing_record.updated_at
                new_time = datetime.fromisoformat(new_record['updated_at'])
                if abs((existing_time - new_time).total_seconds()) > 300:  # 5 minutes
                    return SyncConflictType.TIMESTAMP_CONFLICT
            
            # Compare currency for revenue data
            if hasattr(existing_record, 'currency') and 'currency' in new_record:
                if existing_record.currency != new_record['currency']:
                    return SyncConflictType.CURRENCY_MISMATCH
            
            # Compare key data fields
            if hasattr(existing_record, 'views') and 'views' in new_record:
                existing_views = getattr(existing_record, 'views', 0)
                new_views = new_record.get('views', 0)
                if abs(existing_views - new_views) > max(existing_views, new_views) * 0.1:  # 10% difference
                    return SyncConflictType.DATA_INCONSISTENCY
        
        # Check for platform discrepancies
        platforms = set(record.get('platform') for record in new_records)
        if len(platforms) > 1:
            return SyncConflictType.PLATFORM_DISCREPANCY
        
        return SyncConflictType.VERSION_MISMATCH
    
    async def _resolve_conflict(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve a data synchronization conflict"""        
        resolver = self.conflict_resolvers.get(conflict.conflict_type)
        if not resolver:
            logger.error(f"No resolver for conflict type: {conflict.conflict_type}")
            return {"success": False, "error": "No resolver available"}
        
        try:
            resolution_result = await resolver(session, user_id, data_type, conflict)
            
            # Log conflict resolution
            await self._log_conflict_resolution(conflict, resolution_result)
            
            return resolution_result
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _resolve_duplicate_record(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve duplicate record conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        existing_records = conflict.conflict_data["existing_records"]
        
        # Use the latest record based on timestamp
        latest_record = max(
            new_records,
            key=lambda r: datetime.fromisoformat(r.get('updated_at', r.get('created_at', '1970-01-01')))
        )
        
        # Update or create with latest data
        success = await self._create_or_update_record(
            session, user_id, data_type, latest_record
        )
        
        return {
            "success": success,
            "strategy": "latest_timestamp",
            "updated": 1 if success else 0
        }
    
    async def _resolve_version_mismatch(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve version mismatch conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        
        # Merge data from all records
        merged_record = await self._merge_record_data(new_records)
        
        success = await self._create_or_update_record(
            session, user_id, data_type, merged_record
        )
        
        return {
            "success": success,
            "strategy": "merge_latest",
            "updated": 1 if success else 0
        }
    
    async def _resolve_data_inconsistency(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve data inconsistency conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        
        # Use highest confidence/quality record
        best_record = max(
            new_records,
            key=lambda r: r.get('confidence_level', r.get('quality_score', 0))
        )
        
        success = await self._create_or_update_record(
            session, user_id, data_type, best_record
        )
        
        return {
            "success": success,
            "strategy": "highest_quality",
            "updated": 1 if success else 0
        }
    
    async def _resolve_currency_mismatch(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve currency mismatch conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        
        # Convert all to EUR (default currency)
        converted_records = []
        for record in new_records:
            converted_record = await self._convert_currency(record, "EUR")
            converted_records.append(converted_record)
        
        # Sum up amounts in same currency
        if data_type == "revenue":
            total_amount = sum(
                Decimal(str(r.get('net_revenue', 0))) for r in converted_records
            )
            
            merged_record = converted_records[0].copy()
            merged_record['net_revenue'] = float(total_amount)
            merged_record['gross_revenue'] = float(total_amount * Decimal('1.1'))  # Estimate
            merged_record['currency'] = "EUR"
            
            success = await self._create_or_update_record(
                session, user_id, data_type, merged_record
            )
            
            return {
                "success": success,
                "strategy": "currency_conversion_sum",
                "updated": 1 if success else 0
            }
        
        return {"success": False, "error": "Currency resolution not applicable"}
    
    async def _resolve_timestamp_conflict(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve timestamp conflict conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        
        # Use the most recent record
        latest_record = max(
            new_records,
            key=lambda r: datetime.fromisoformat(r.get('updated_at', r.get('date', '1970-01-01')))
        )
        
        success = await self._create_or_update_record(
            session, user_id, data_type, latest_record
        )
        
        return {
            "success": success,
            "strategy": "latest_timestamp",
            "updated": 1 if success else 0
        }
    
    async def _resolve_platform_discrepancy(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Resolve platform discrepancy conflicts"""        
        new_records = conflict.conflict_data["new_records"]
        
        # Create separate records for each platform
        created_count = 0
        for record in new_records:
            success = await self._create_or_update_record(
                session, user_id, data_type, record
            )
            if success:
                created_count += 1
        
        return {
            "success": created_count > 0,
            "strategy": "keep_separate",
            "created": created_count
        }
    
    async def _merge_record_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge data from multiple records intelligently"""        
        if not records:
            return {}
        
        merged = records[0].copy()
        
        for record in records[1:]:
            for key, value in record.items():
                if key not in merged or merged[key] is None:
                    merged[key] = value
                elif isinstance(value, (int, float)) and isinstance(merged[key], (int, float)):
                    # For numeric values, use the maximum (often more accurate)
                    merged[key] = max(merged[key], value)
                elif isinstance(value, str) and len(value) > len(str(merged[key])):
                    # For strings, use the longer one (often more complete)
                    merged[key] = value
                elif key == 'updated_at':
                    # For timestamps, use the latest
                    current_time = datetime.fromisoformat(merged[key])
                    new_time = datetime.fromisoformat(value)
                    if new_time > current_time:
                        merged[key] = value
        
        return merged
    
    async def _create_or_update_record(
        self,
        session: AsyncSession,
        user_id: str,
        data_type: str,
        record_data: Dict[str, Any]
    ) -> bool:
        """Create or update a record in the database"""        
        try:
            if data_type == "analytics":
                return await self._upsert_analytics_record(session, user_id, record_data)
            elif data_type == "revenue":
                return await self._upsert_revenue_record(session, user_id, record_data)
            elif data_type == "content":
                return await self._upsert_content_record(session, user_id, record_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create/update record: {str(e)}")
            return False
    
    async def _upsert_analytics_record(
        self,
        session: AsyncSession,
        user_id: str,
        record_data: Dict[str, Any]
    ) -> bool:
        """Insert or update analytics record"""        
        try:
            # Create upsert statement
            stmt = insert(PlatformAnalytics).values(
                user_id=uuid.UUID(user_id),
                platform=Platform(record_data["platform"]),
                metric_type=record_data["metric_type"],
                content_id=record_data.get("content_id"),
                content_title=record_data.get("content_title"),
                content_type=record_data.get("content_type"),
                date=datetime.fromisoformat(record_data["date"]) if isinstance(record_data["date"], str) else record_data["date"],
                period_type=record_data.get("period_type", "daily"),
                views=record_data.get("views", 0),
                likes=record_data.get("likes", 0),
                comments=record_data.get("comments", 0),
                shares=record_data.get("shares", 0),
                platform_specific_metrics=record_data.get("platform_specific_metrics", {})
            )
            
            # Handle conflicts
            stmt = stmt.on_conflict_do_update(
                constraint="uq_analytics_record",
                set_={
                    "views": stmt.excluded.views,
                    "likes": stmt.excluded.likes,
                    "comments": stmt.excluded.comments,
                    "shares": stmt.excluded.shares,
                    "platform_specific_metrics": stmt.excluded.platform_specific_metrics,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            
            await session.execute(stmt)
            return True
            
        except Exception as e:
            logger.error(f"Analytics upsert failed: {str(e)}")
            return False
    
    async def _upsert_revenue_record(
        self,
        session: AsyncSession,
        user_id: str,
        record_data: Dict[str, Any]
    ) -> bool:
        """Insert or update revenue record"""        
        try:
            # Create upsert statement
            stmt = insert(PlatformRevenue).values(
                user_id=uuid.UUID(user_id),
                platform=Platform(record_data["platform"]),
                revenue_stream=record_data["revenue_stream"],
                content_id=record_data.get("content_id"),
                content_title=record_data.get("content_title"),
                content_type=record_data.get("content_type"),
                date=datetime.fromisoformat(record_data["date"]) if isinstance(record_data["date"], str) else record_data["date"],
                gross_revenue=Decimal(str(record_data["gross_revenue"])),
                net_revenue=Decimal(str(record_data["net_revenue"])),
                currency=record_data.get("currency", "EUR"),
                platform_specific_data=record_data.get("platform_specific_data", {})
            )
            
            # Handle conflicts - sum revenue amounts
            stmt = stmt.on_conflict_do_update(
                index_elements=["connection_id", "platform", "content_id", "date", "revenue_stream"],
                set_={
                    "gross_revenue": PlatformRevenue.gross_revenue + stmt.excluded.gross_revenue,
                    "net_revenue": PlatformRevenue.net_revenue + stmt.excluded.net_revenue,
                    "platform_specific_data": stmt.excluded.platform_specific_data,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            
            await session.execute(stmt)
            return True
            
        except Exception as e:
            logger.error(f"Revenue upsert failed: {str(e)}")
            return False
    
    async def _validate_analytics_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analytics data record"""        
        required_fields = ["platform", "metric_type", "date"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}"
            }
        
        # Validate platform
        try:
            Platform(record["platform"])
        except ValueError:
            return {
                "valid": False,
                "error": f"Invalid platform: {record['platform']}"
            }
        
        # Validate numeric fields
        numeric_fields = ["views", "likes", "comments", "shares"]
        for field in numeric_fields:
            if field in record and not isinstance(record[field], (int, float)):
                return {
                    "valid": False,
                    "error": f"Invalid numeric value for {field}: {record[field]}"
                }
        
        return {"valid": True}
    
    async def _validate_revenue_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate revenue data record"""        
        required_fields = ["platform", "revenue_stream", "date", "gross_revenue", "net_revenue"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}"
            }
        
        # Validate platform
        try:
            Platform(record["platform"])
        except ValueError:
            return {
                "valid": False,
                "error": f"Invalid platform: {record['platform']}"
            }
        
        # Validate revenue amounts
        try:
            gross_revenue = Decimal(str(record["gross_revenue"]))
            net_revenue = Decimal(str(record["net_revenue"]))
            
            if gross_revenue < 0 or net_revenue < 0:
                return {
                    "valid": False,
                    "error": "Revenue amounts cannot be negative"
                }
            
            if net_revenue > gross_revenue:
                return {
                    "valid": False,
                    "error": "Net revenue cannot exceed gross revenue"
                }
                
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": "Invalid revenue amounts"
            }
        
        return {"valid": True}
    
    async def _validate_content_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content metadata record"""        
        required_fields = ["platform", "content_id", "content_type"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}"
            }
        
        # Validate platform
        try:
            Platform(record["platform"])
        except ValueError:
            return {
                "valid": False,
                "error": f"Invalid platform: {record['platform']}"
            }
        
        return {"valid": True}
    
    async def _acquire_sync_lock(self, lock_key: str, timeout: int = 300):
        """Acquire distributed lock for synchronization"""        
        class AsyncLock:
            def __init__(self, redis_client, key, timeout):
                self.redis_client = redis_client
                self.key = key
                self.timeout = timeout
                self.acquired = False
            
            async def __aenter__(self):
                # Try to acquire lock with timeout
                for _ in range(self.timeout):
                    if await self.redis_client.set(self.key, "locked", nx=True, ex=self.timeout):
                        self.acquired = True
                        return self
                    await asyncio.sleep(1)
                
                raise TimeoutError(f"Failed to acquire lock: {self.key}")
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.acquired:
                    await self.redis_client.delete(self.key)
        
        return AsyncLock(self.redis_client, lock_key, timeout)
    
    async def _update_sync_cache(self, user_id: str, result: SyncResult):
        """Update synchronization cache with latest results"""        
        cache_key = f"sync_result:{user_id}"
        cache_data = {
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "success": result.success,
            "records_processed": result.records_processed,
            "conflicts_resolved": result.conflicts_resolved,
            "processing_time": result.processing_time_seconds
        }
        
        await self.redis_client.setex(
            cache_key,
            timedelta(days=7).total_seconds(),
            json.dumps(cache_data)
        )
    
    async def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get synchronization status for a user"""        
        cache_key = f"sync_result:{user_id}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        return {
            "last_sync": None,
            "success": None,
            "records_processed": 0,
            "conflicts_resolved": 0,
            "processing_time": 0
        }
    
    def _record_to_dict(self, record) -> Dict[str, Any]:
        """Convert SQLAlchemy record to dictionary"""        
        if hasattr(record, '__dict__'):
            result = {}
            for key, value in record.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, datetime):
                        result[key] = value.isoformat()
                    elif isinstance(value, Decimal):
                        result[key] = float(value)
                    elif isinstance(value, uuid.UUID):
                        result[key] = str(value)
                    else:
                        result[key] = value
            return result
        
        return {}


# Export main classes and functions
__all__ = [
    'DataSynchronizationEngine',
    'SyncConflict',
    'SyncResult',
    'SyncConflictType',
    'SyncStrategy'
]
