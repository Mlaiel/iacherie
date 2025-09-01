"""Content Aggregator - Multi-Source Content Aggregation Engine
===========================================================

The ContentAggregator collects, normalizes, and aggregates content
from multiple sources for unified management and distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from ..data.models.content import Content
from ..data.models.content_source import ContentSource
from ..integrations.platform_apis import PlatformAPIManager


@dataclass
class AggregationSource:
    """
Content aggregation source configuration"""
    source_id: str
    source_type: str  # platform, rss, api, webhook
    source_name: str
    api_config: Dict[str, Any]
    sync_frequency: int  # minutes
    enabled: bool = True
    last_sync: Optional[datetime] = None


@dataclass
class AggregationRule:
    """
Content aggregation rule definition"""
    rule_id: str
    source_ids: List[str]
    content_filters: Dict[str, Any]
    transformation_rules: Dict[str, Any]
    deduplication_strategy: str
    priority: int = 1
    enabled: bool = True


@dataclass
class AggregationResult:
    """
Content aggregation result container"""
    aggregation_id: str
    source_id: str
    items_processed: int
    items_created: int
    items_updated: int
    items_skipped: int
    items_errors: int
    aggregation_time: float
    errors: List[str] = None


class ContentAggregator:
    """
    Multi-Source Content Aggregation Engine
    
    Provides comprehensive content aggregation including:
    - Multi-platform content collection and synchronization
    - RSS feed monitoring and content import
    - API-based content ingestion from external sources
    - Real-time webhook processing
    - Content deduplication and normalization
    - Scheduled and on-demand aggregation
    - Content source quality scoring
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Platform API manager
        self.platform_api = PlatformAPIManager()
        
        # Aggregation state
        self.active_sources = {}
        self.aggregation_rules = {}
        self.aggregation_stats = {}
        
        # Deduplication cache
        self.content_fingerprints = set()
        
        # Load configurations
        asyncio.create_task(self._load_aggregation_configurations())

    async def aggregate_from_source(
        self,
        source_id: str,
        custom_filters: Dict[str, Any] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Aggregate content from a specific source
        
        Args:
            source_id: Source identifier
            custom_filters: Custom content filters
            force_refresh: Force refresh regardless of sync frequency
            
        Returns:
            Aggregation result with statistics and status
        """
        aggregation_start = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting content aggregation from source {source_id}")
            
            # Get source configuration
            source_config = await self._get_source_config(source_id)
            if not source_config:
                return {
                    "success": False,
                    "error": "Source configuration not found",
                    "source_id": source_id
                }
            
            # Check if aggregation is needed
            if not force_refresh and not await self._should_aggregate_source(source_config):
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Sync frequency not reached",
                    "source_id": source_id
                }
            
            # Route to appropriate aggregation method
            source_type = source_config.source_type
            
            if source_type == "platform":
                result = await self._aggregate_from_platform(source_config, custom_filters)
            elif source_type == "rss":
                result = await self._aggregate_from_rss(source_config, custom_filters)
            elif source_type == "api":
                result = await self._aggregate_from_api(source_config, custom_filters)
            elif source_type == "webhook":
                result = await self._aggregate_from_webhook(source_config, custom_filters)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported source type: {source_type}",
                    "source_id": source_id
                }
            
            # Update source sync status
            await self._update_source_sync_status(source_id, result)
            
            # Calculate aggregation time
            aggregation_time = (datetime.utcnow() - aggregation_start).total_seconds()
            result.aggregation_time = aggregation_time
            
            # Update aggregation statistics
            await self._update_aggregation_stats(source_id, result)
            
            self.logger.info(f"Content aggregation completed for source {source_id} in {aggregation_time:.2f}s")
            
            return {
                "success": True,
                "source_id": source_id,
                "aggregation_result": self._serialize_aggregation_result(result),
                "aggregation_time": aggregation_time
            }
            
        except Exception as e:
            aggregation_time = (datetime.utcnow() - aggregation_start).total_seconds()
            error_msg = f"Content aggregation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "source_id": source_id,
                "aggregation_time": aggregation_time
            }

    async def aggregate_all_sources(
        self,
        source_filter: Dict[str, Any] = None,
        parallel_execution: bool = True
    ) -> Dict[str, Any]:
        """
        Aggregate content from all configured sources
        
        Args:
            source_filter: Filter criteria for sources
            parallel_execution: Execute aggregations in parallel
            
        Returns:
            Combined aggregation results from all sources
        """
        try:
            self.logger.info("Starting aggregation from all sources")
            
            # Get all enabled sources
            sources = await self._get_enabled_sources(source_filter)
            
            if not sources:
                return {
                    "success": False,
                    "error": "No enabled sources found",
                    "sources_processed": 0
                }
            
            aggregation_results = []
            
            if parallel_execution:
                # Execute aggregations in parallel
                tasks = [
                    self.aggregate_from_source(source.source_id)
                    for source in sources
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Source {sources[i].source_id} aggregation failed: {str(result)}")
                        aggregation_results.append({
                            "source_id": sources[i].source_id,
                            "success": False,
                            "error": str(result)
                        })
                    else:
                        aggregation_results.append(result)
            else:
                # Execute aggregations sequentially
                for source in sources:
                    result = await self.aggregate_from_source(source.source_id)
                    aggregation_results.append(result)
            
            # Aggregate statistics
            total_processed = sum(
                r.get("aggregation_result", {}).get("items_processed", 0)
                for r in aggregation_results if r.get("success")
            )
            total_created = sum(
                r.get("aggregation_result", {}).get("items_created", 0)
                for r in aggregation_results if r.get("success")
            )
            total_errors = sum(
                r.get("aggregation_result", {}).get("items_errors", 0)
                for r in aggregation_results if r.get("success")
            )
            
            successful_sources = sum(1 for r in aggregation_results if r.get("success"))
            
            return {
                "success": True,
                "sources_processed": len(sources),
                "sources_successful": successful_sources,
                "total_items_processed": total_processed,
                "total_items_created": total_created,
                "total_errors": total_errors,
                "source_results": aggregation_results
            }
            
        except Exception as e:
            error_msg = f"Bulk aggregation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "sources_processed": 0
            }

    async def _aggregate_from_platform(
        self,
        source_config: AggregationSource,
        custom_filters: Dict[str, Any] = None
    ) -> AggregationResult:
        """
        Aggregate content from social media platforms
        
        Args:
            source_config: Source configuration
            custom_filters: Custom content filters
            
        Returns:
            Platform aggregation result
        """
        try:
            platform_name = source_config.api_config.get("platform_name", "")
            aggregation_id = str(uuid.uuid4())
            
            items_processed = 0
            items_created = 0
            items_updated = 0
            items_skipped = 0
            items_errors = 0
            errors = []
            
            # Get platform API client
            api_client = await self.platform_api.get_client(platform_name)
            
            if not api_client:
                raise Exception(f"Platform API client not available for {platform_name}")
            
            # Prepare aggregation parameters
            aggregation_params = source_config.api_config.copy()
            if custom_filters:
                aggregation_params.update(custom_filters)
            
            # Get content from platform
            if platform_name == "youtube":
                content_items = await self._aggregate_youtube_content(api_client, aggregation_params)
            elif platform_name == "instagram":
                content_items = await self._aggregate_instagram_content(api_client, aggregation_params)
            elif platform_name == "tiktok":
                content_items = await self._aggregate_tiktok_content(api_client, aggregation_params)
            elif platform_name == "spotify":
                content_items = await self._aggregate_spotify_content(api_client, aggregation_params)
            elif platform_name == "soundcloud":
                content_items = await self._aggregate_soundcloud_content(api_client, aggregation_params)
            else:
                raise Exception(f"Platform {platform_name} not supported for aggregation")
            
            # Process each content item
            for item in content_items:
                items_processed += 1
                
                try:
                    # Check for duplicates
                    if await self._is_duplicate_content(item):
                        items_skipped += 1
                        continue
                    
                    # Normalize content format
                    normalized_item = await self._normalize_platform_content(item, platform_name)
                    
                    # Apply content filters
                    if not await self._passes_content_filters(normalized_item, aggregation_params):
                        items_skipped += 1
                        continue
                    
                    # Check if content exists
                    existing_content = await self._find_existing_content(normalized_item)
                    
                    if existing_content:
                        # Update existing content
                        updated_content = await self._update_existing_content(
                            existing_content, normalized_item
                        )
                        if updated_content:
                            items_updated += 1
                    else:
                        # Create new content
                        new_content = await self._create_new_content(normalized_item, source_config.source_id)
                        if new_content:
                            items_created += 1
                    
                except Exception as e:
                    items_errors += 1
                    error_msg = f"Failed to process item {item.get('id', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            return AggregationResult(
                aggregation_id=aggregation_id,
                source_id=source_config.source_id,
                items_processed=items_processed,
                items_created=items_created,
                items_updated=items_updated,
                items_skipped=items_skipped,
                items_errors=items_errors,
                aggregation_time=0.0,
                errors=errors
            )
            
        except Exception as e:
            raise Exception(f"Platform aggregation failed: {str(e)}")

    async def _aggregate_from_rss(
        self,
        source_config: AggregationSource,
        custom_filters: Dict[str, Any] = None
    ) -> AggregationResult:
        """
        Aggregate content from RSS feeds
        
        Args:
            source_config: Source configuration
            custom_filters: Custom content filters
            
        Returns:
            RSS aggregation result
        """
        try:
            import feedparser
            
            aggregation_id = str(uuid.uuid4())
            rss_url = source_config.api_config.get("rss_url", "")
            
            if not rss_url:
                raise Exception("RSS URL not configured")
            
            items_processed = 0
            items_created = 0
            items_updated = 0
            items_skipped = 0
            items_errors = 0
            errors = []
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                self.logger.warning(f"RSS feed parsing warning for {rss_url}: {feed.bozo_exception}")
            
            # Process feed entries
            for entry in feed.entries:
                items_processed += 1
                
                try:
                    # Normalize RSS entry to content format
                    normalized_item = await self._normalize_rss_content(entry, feed)
                    
                    # Check for duplicates
                    if await self._is_duplicate_content(normalized_item):
                        items_skipped += 1
                        continue
                    
                    # Apply content filters
                    aggregation_params = source_config.api_config.copy()
                    if custom_filters:
                        aggregation_params.update(custom_filters)
                    
                    if not await self._passes_content_filters(normalized_item, aggregation_params):
                        items_skipped += 1
                        continue
                    
                    # Check if content exists
                    existing_content = await self._find_existing_content(normalized_item)
                    
                    if existing_content:
                        # Update existing content
                        updated_content = await self._update_existing_content(
                            existing_content, normalized_item
                        )
                        if updated_content:
                            items_updated += 1
                    else:
                        # Create new content
                        new_content = await self._create_new_content(normalized_item, source_config.source_id)
                        if new_content:
                            items_created += 1
                    
                except Exception as e:
                    items_errors += 1
                    error_msg = f"Failed to process RSS entry {entry.get('id', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            return AggregationResult(
                aggregation_id=aggregation_id,
                source_id=source_config.source_id,
                items_processed=items_processed,
                items_created=items_created,
                items_updated=items_updated,
                items_skipped=items_skipped,
                items_errors=items_errors,
                aggregation_time=0.0,
                errors=errors
            )
            
        except Exception as e:
            raise Exception(f"RSS aggregation failed: {str(e)}")

    async def _aggregate_from_api(
        self,
        source_config: AggregationSource,
        custom_filters: Dict[str, Any] = None
    ) -> AggregationResult:
        """
        Aggregate content from external APIs
        
        Args:
            source_config: Source configuration
            custom_filters: Custom content filters
            
        Returns:
            API aggregation result
        """
        try:
            import aiohttp
            
            aggregation_id = str(uuid.uuid4())
            api_config = source_config.api_config
            
            items_processed = 0
            items_created = 0
            items_updated = 0
            items_skipped = 0
            items_errors = 0
            errors = []
            
            # Prepare API request
            api_url = api_config.get("api_url", "")
            headers = api_config.get("headers", {})
            params = api_config.get("params", {})
            
            if custom_filters:
                params.update(custom_filters)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}")
                    
                    data = await response.json()
            
            # Extract content items from response
            items_path = api_config.get("items_path", "data")
            content_items = self._extract_nested_value(data, items_path)
            
            if not isinstance(content_items, list):
                content_items = [content_items] if content_items else []
            
            # Process each content item
            for item in content_items:
                items_processed += 1
                
                try:
                    # Normalize API content
                    normalized_item = await self._normalize_api_content(item, api_config)
                    
                    # Check for duplicates
                    if await self._is_duplicate_content(normalized_item):
                        items_skipped += 1
                        continue
                    
                    # Apply content filters
                    aggregation_params = source_config.api_config.copy()
                    if custom_filters:
                        aggregation_params.update(custom_filters)
                    
                    if not await self._passes_content_filters(normalized_item, aggregation_params):
                        items_skipped += 1
                        continue
                    
                    # Check if content exists
                    existing_content = await self._find_existing_content(normalized_item)
                    
                    if existing_content:
                        # Update existing content
                        updated_content = await self._update_existing_content(
                            existing_content, normalized_item
                        )
                        if updated_content:
                            items_updated += 1
                    else:
                        # Create new content
                        new_content = await self._create_new_content(normalized_item, source_config.source_id)
                        if new_content:
                            items_created += 1
                    
                except Exception as e:
                    items_errors += 1
                    error_msg = f"Failed to process API item: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            return AggregationResult(
                aggregation_id=aggregation_id,
                source_id=source_config.source_id,
                items_processed=items_processed,
                items_created=items_created,
                items_updated=items_updated,
                items_skipped=items_skipped,
                items_errors=items_errors,
                aggregation_time=0.0,
                errors=errors
            )
            
        except Exception as e:
            raise Exception(f"API aggregation failed: {str(e)}")

    # Helper methods

    async def _load_aggregation_configurations(self):
        """Load aggregation sources and rules from database"""
        try:
            # Load sources
            sources_result = await self.db.execute(
                select(ContentSource).where(ContentSource.enabled == True)
            )
            sources = sources_result.scalars().all()
            
            for source in sources:
                self.active_sources[source.id] = AggregationSource(
                    source_id=source.id,
                    source_type=source.source_type,
                    source_name=source.name,
                    api_config=source.api_config,
                    sync_frequency=source.sync_frequency,
                    enabled=source.enabled,
                    last_sync=source.last_sync
                )
            
        except Exception as e:
            self.logger.error(f"Failed to load aggregation configurations: {str(e)}")

    async def _get_source_config(self, source_id: str) -> Optional[AggregationSource]:
        """Get source configuration by ID"""
        return self.active_sources.get(source_id)

    async def _should_aggregate_source(self, source_config: AggregationSource) -> bool:
        """
Check if source should be aggregated based on frequency"""
        if not source_config.last_sync:
            return True
        
        time_since_sync = datetime.utcnow() - source_config.last_sync
        sync_interval = timedelta(minutes=source_config.sync_frequency)
        
        return time_since_sync >= sync_interval

    async def _is_duplicate_content(self, content_item: Dict[str, Any]) -> bool:
        """
Check if content is a duplicate"""
        # Generate content fingerprint
        fingerprint = await self._generate_content_fingerprint(content_item)
        
        if fingerprint in self.content_fingerprints:
            return True
        
        # Also check database for existing content with same fingerprint
        existing = await self.db.execute(
            select(Content).where(Content.content_fingerprint == fingerprint)
        )
        
        if existing.scalar_one_or_none():
            return True
        
        # Add to cache
        self.content_fingerprints.add(fingerprint)
        return False

    async def _generate_content_fingerprint(self, content_item: Dict[str, Any]) -> str:
        """
Generate unique fingerprint for content deduplication"""
        import hashlib
        
        # Use title, description, and source URL for fingerprint
        fingerprint_data = {
            "title": content_item.get("title", ""),
            "description": content_item.get("description", "")[:200],  # First 200 chars
            "source_url": content_item.get("source_url", ""),
            "content_type": content_item.get("content_type", "")
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()

    def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dictionary using dot notation"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value

    # Placeholder methods for actual implementations
    async def _get_enabled_sources(self, source_filter: Dict[str, Any] = None) -> List[AggregationSource]:
        """
Get all enabled aggregation sources"""
        return list(self.active_sources.values())

    async def _aggregate_youtube_content(self, api_client: Any, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Aggregate content from YouTube"""
        return []

    async def _aggregate_instagram_content(self, api_client: Any, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Aggregate content from Instagram"""
        return []

    async def _normalize_platform_content(self, item: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
Normalize platform content to standard format"""
        return item

    async def _normalize_rss_content(self, entry: Any, feed: Any) -> Dict[str, Any]:
        """
Normalize RSS content to standard format"""
        return {}

    async def _normalize_api_content(self, item: Dict[str, Any], api_config: Dict[str, Any]) -> Dict[str, Any]:
        """
Normalize API content to standard format"""
        return item

    async def _passes_content_filters(self, content: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
Check if content passes aggregation filters"""
        return True

    async def _find_existing_content(self, content: Dict[str, Any]) -> Optional[Any]:
        """
Find existing content in database"""
        return None

    async def _create_new_content(self, content: Dict[str, Any], source_id: str) -> Optional[Any]:
        """
Create new content record"""
        return None

    async def _update_existing_content(self, existing: Any, new_content: Dict[str, Any]) -> Optional[Any]:
        """
Update existing content record"""
        return None

    async def _update_source_sync_status(self, source_id: str, result: AggregationResult) -> None:
        """
Update source synchronization status"""
        pass

    async def _update_aggregation_stats(self, source_id: str, result: AggregationResult) -> None:
        """
Update aggregation statistics"""
        pass

    def _serialize_aggregation_result(self, result: AggregationResult) -> Dict[str, Any]:
        """
Convert aggregation result to serializable format"""
        return {
            "aggregation_id": result.aggregation_id,
            "source_id": result.source_id,
            "items_processed": result.items_processed,
            "items_created": result.items_created,
            "items_updated": result.items_updated,
            "items_skipped": result.items_skipped,
            "items_errors": result.items_errors,
            "aggregation_time": result.aggregation_time,
            "errors": result.errors or []
        }
