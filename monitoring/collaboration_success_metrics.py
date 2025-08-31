"""🤝 Collaboration Success Metrics - Partnership & Creator Analytics
================================================================

Advanced metrics tracking for collaboration success, creator partnerships,
and content co-creation effectiveness on the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, Counter
import statistics

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaborations"""    BRAND_PARTNERSHIP = "brand_partnership"
    CREATOR_COLLAB = "creator_collaboration"
    CONTENT_LICENSING = "content_licensing" 
    SPONSORED_CONTENT = "sponsored_content"
    CROSS_PROMOTION = "cross_promotion"
    AFFILIATE_MARKETING = "affiliate_marketing"
    INFLUENCER_CAMPAIGN = "influencer_campaign"


class CollaborationStatus(Enum):
    """Collaboration status"""    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class CollaborationEvent:
    """Individual collaboration event"""    collaboration_id: str
    creator_id: int
    brand_id: Optional[int]
    collaboration_type: CollaborationType
    status: CollaborationStatus
    timestamp: datetime
    value: Optional[Decimal] = None
    content_ids: List[int] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorPerformance:
    """Creator performance metrics"""    creator_id: int
    total_collaborations: int
    successful_collaborations: int
    total_revenue: Decimal
    average_engagement: float
    completion_rate: float
    satisfaction_score: float
    partner_retention_rate: float
    response_time_hours: float
    content_quality_score: float


class CollaborationSuccessTracker:
    """    Advanced collaboration success tracking system
    
    Features:
    - Partnership success analytics
    - Creator performance tracking
    - Brand satisfaction metrics
    - Content collaboration effectiveness
    - ROI analysis for partnerships
    - Collaboration funnel optimization
    - Network effect analysis
    """    
    def __init__(self):
        """Initialize collaboration success tracker"""        
        # Prometheus metrics
        self.collaborations_total = Counter(
            'ainflue_collaborations_total',
            'Total number of collaborations',
            ['type', 'status', 'creator_tier']
        )
        
        self.collaboration_success_rate = Gauge(
            'ainflue_collaboration_success_rate',
            'Collaboration success rate percentage',
            ['type', 'creator_tier']
        )
        
        self.collaboration_value = Histogram(
            'ainflue_collaboration_value_euros',
            'Collaboration value distribution',
            ['type'],
            buckets=[0, 100, 500, 1000, 5000, 10000, 50000, float('inf')]
        )
        
        self.creator_performance_score = Gauge(
            'ainflue_creator_performance_score',
            'Creator performance score (0-100)',
            ['creator_id', 'tier']
        )
        
        self.partnership_satisfaction = Gauge(
            'ainflue_partnership_satisfaction_score',
            'Partnership satisfaction score (0-10)',
            ['brand_id', 'collaboration_type']
        )
        
        self.collaboration_completion_time = Histogram(
            'ainflue_collaboration_completion_days',
            'Time to complete collaboration',
            ['type'],
            buckets=[1, 3, 7, 14, 30, 60, 90, float('inf')]
        )
        
        # Data storage
        self.collaboration_events: List[CollaborationEvent] = []
        self.creator_metrics: Dict[int, CreatorPerformance] = {}
        self.brand_metrics: Dict[int, Dict[str, Any]] = defaultdict(dict)
        self.collaboration_networks: Dict[str, Set[int]] = defaultdict(set)
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_timestamp = datetime.utcnow()
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("CollaborationSuccessTracker initialized successfully")
    
    async def track_collaboration_event(
        self,
        collaboration_id: str,
        creator_id: int,
        collaboration_type: CollaborationType,
        status: CollaborationStatus,
        brand_id: Optional[int] = None,
        value: Optional[Decimal] = None,
        content_ids: Optional[List[int]] = None,
        metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """        Track a collaboration event
        
        Args:
            collaboration_id: Unique collaboration identifier
            creator_id: Creator/influencer ID
            collaboration_type: Type of collaboration
            status: Current status
            brand_id: Brand/company ID (if applicable)
            value: Financial value of collaboration
            content_ids: Associated content IDs
            metrics: Performance metrics
            metadata: Additional data
        """        try:
            # Create collaboration event
            event = CollaborationEvent(
                collaboration_id=collaboration_id,
                creator_id=creator_id,
                brand_id=brand_id,
                collaboration_type=collaboration_type,
                status=status,
                timestamp=datetime.utcnow(),
                value=value,
                content_ids=content_ids or [],
                metrics=metrics or {},
                metadata=metadata or {}
            )
            
            # Store event
            self.collaboration_events.append(event)
            
            # Update network tracking
            if brand_id:
                self.collaboration_networks[f"brand_{brand_id}"].add(creator_id)
                self.collaboration_networks[f"creator_{creator_id}"].add(brand_id)
            
            # Update Prometheus metrics
            creator_tier = self._get_creator_tier(creator_id)
            
            self.collaborations_total.labels(
                type=collaboration_type.value,
                status=status.value,
                creator_tier=creator_tier
            ).inc()
            
            if value:
                self.collaboration_value.labels(
                    type=collaboration_type.value
                ).observe(float(value))
            
            # Update creator performance
            await self._update_creator_performance(creator_id)
            
            # Update brand metrics
            if brand_id:
                await self._update_brand_metrics(brand_id, event)
            
            # Calculate success rate
            await self._update_success_rates(collaboration_type, creator_tier)
            
            # Clear cache
            self.analytics_cache.clear()
            
            logger.debug(f"Collaboration event tracked: {collaboration_id} - {status.value}")
            
        except Exception as e:
            logger.error(f"Error tracking collaboration event: {e}")
    
    async def track_creator_satisfaction(
        self,
        creator_id: int,
        collaboration_id: str,
        satisfaction_score: float,
        feedback: Optional[str] = None
    ) -> None:
        """Track creator satisfaction with collaboration"""        try:
            # Find the collaboration
            collaboration = None
            for event in self.collaboration_events:
                if event.collaboration_id == collaboration_id:
                    collaboration = event
                    break
            
            if not collaboration:
                logger.warning(f"Collaboration {collaboration_id} not found")
                return
            
            # Update satisfaction metrics
            if collaboration.brand_id:
                self.partnership_satisfaction.labels(
                    brand_id=str(collaboration.brand_id),
                    collaboration_type=collaboration.collaboration_type.value
                ).set(satisfaction_score)
            
            # Store satisfaction data
            satisfaction_data = {
                "collaboration_id": collaboration_id,
                "creator_id": creator_id,
                "score": satisfaction_score,
                "feedback": feedback,
                "timestamp": datetime.utcnow()
            }
            
            # Update creator performance
            await self._update_creator_performance(creator_id)
            
            logger.debug(f"Creator satisfaction tracked: {satisfaction_score}/10 for {collaboration_id}")
            
        except Exception as e:
            logger.error(f"Error tracking creator satisfaction: {e}")
    
    async def get_collaboration_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """        Get comprehensive collaboration analytics
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Collaboration analytics data
        """        try:
            # Check cache
            cache_key = f"collaboration_analytics_{period_days}"
            if (cache_key in self.analytics_cache and 
                datetime.utcnow() - self.cache_timestamp < self.cache_ttl):
                return self.analytics_cache[cache_key]
            
            # Calculate analytics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            period_events = [
                event for event in self.collaboration_events
                if start_time <= event.timestamp <= end_time
            ]
            
            analytics = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": period_days
                },
                "summary": await self._calculate_collaboration_summary(period_events),
                "success_metrics": await self._calculate_success_metrics(period_events),
                "creator_performance": await self._calculate_top_creators(period_events),
                "brand_performance": await self._calculate_brand_metrics(period_events),
                "collaboration_funnel": await self._calculate_collaboration_funnel(period_events),
                "network_analysis": await self._calculate_network_metrics(),
                "trends": await self._calculate_collaboration_trends(period_days),
                "recommendations": await self._generate_optimization_recommendations(period_events)
            }
            
            # Cache results
            self.analytics_cache[cache_key] = analytics
            self.cache_timestamp = datetime.utcnow()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting collaboration analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_collaboration_summary(self, events: List[CollaborationEvent]) -> Dict[str, Any]:
        """Calculate collaboration summary statistics"""        if not events:
            return {
                "total_collaborations": 0,
                "total_value": 0,
                "average_value": 0,
                "unique_creators": 0,
                "unique_brands": 0
            }
        
        total_value = sum(event.value or Decimal('0') for event in events)
        unique_creators = len(set(event.creator_id for event in events))
        unique_brands = len(set(event.brand_id for event in events if event.brand_id))
        
        return {
            "total_collaborations": len(events),
            "total_value": float(total_value),
            "average_value": float(total_value / len(events)),
            "unique_creators": unique_creators,
            "unique_brands": unique_brands,
            "collaboration_types": dict(Counter(event.collaboration_type.value for event in events)),
            "status_distribution": dict(Counter(event.status.value for event in events))
        }
    
    async def _calculate_success_metrics(self, events: List[CollaborationEvent]) -> Dict[str, Any]:
        """Calculate collaboration success metrics"""        if not events:
            return {"overall_success_rate": 0, "completion_rate": 0, "average_duration": 0}
        
        # Group events by collaboration ID to track lifecycle
        collaborations = defaultdict(list)
        for event in events:
            collaborations[event.collaboration_id].append(event)
        
        successful = 0
        completed = 0
        total_duration = 0
        duration_count = 0
        
        for collab_id, collab_events in collaborations.items():
            # Sort events by timestamp
            collab_events.sort(key=lambda x: x.timestamp)
            
            final_status = collab_events[-1].status
            
            if final_status == CollaborationStatus.COMPLETED:
                successful += 1
                completed += 1
                
                # Calculate duration
                if len(collab_events) > 1:
                    duration = (collab_events[-1].timestamp - collab_events[0].timestamp).days
                    total_duration += duration
                    duration_count += 1
                    
                    # Update Prometheus metric
                    self.collaboration_completion_time.labels(
                        type=collab_events[0].collaboration_type.value
                    ).observe(duration)
            
            elif final_status in [CollaborationStatus.ACTIVE, CollaborationStatus.ACCEPTED]:
                # Consider these as ongoing successes
                successful += 0.5
        
        success_rate = (successful / len(collaborations)) * 100 if collaborations else 0
        completion_rate = (completed / len(collaborations)) * 100 if collaborations else 0
        average_duration = total_duration / duration_count if duration_count > 0 else 0
        
        return {
            "overall_success_rate": round(success_rate, 2),
            "completion_rate": round(completion_rate, 2),
            "average_duration_days": round(average_duration, 1),
            "success_by_type": await self._calculate_success_by_type(collaborations)
        }
    
    async def _calculate_success_by_type(self, collaborations: Dict[str, List[CollaborationEvent]]) -> Dict[str, float]:
        """Calculate success rate by collaboration type"""        type_success = defaultdict(list)
        
        for collab_events in collaborations.values():
            collab_type = collab_events[0].collaboration_type.value
            final_status = collab_events[-1].status
            
            success_score = 1.0 if final_status == CollaborationStatus.COMPLETED else 0.5 if final_status in [CollaborationStatus.ACTIVE, CollaborationStatus.ACCEPTED] else 0.0
            type_success[collab_type].append(success_score)
        
        return {
            collab_type: round(statistics.mean(scores) * 100, 2)
            for collab_type, scores in type_success.items()
        }
    
    async def _calculate_top_creators(self, events: List[CollaborationEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Calculate top performing creators"""        creator_stats = defaultdict(lambda: {
            "collaborations": 0,
            "successful": 0,
            "total_value": Decimal('0'),
            "types": set(),
            "brands": set()
        })
        
        # Group by collaboration to track success
        collaborations = defaultdict(list)
        for event in events:
            collaborations[event.collaboration_id].append(event)
        
        for collab_events in collaborations.values():
            creator_id = collab_events[0].creator_id
            final_status = collab_events[-1].status
            collab_type = collab_events[0].collaboration_type
            brand_id = collab_events[0].brand_id
            value = collab_events[0].value or Decimal('0')
            
            stats = creator_stats[creator_id]
            stats["collaborations"] += 1
            stats["total_value"] += value
            stats["types"].add(collab_type.value)
            
            if brand_id:
                stats["brands"].add(brand_id)
            
            if final_status == CollaborationStatus.COMPLETED:
                stats["successful"] += 1
        
        # Calculate performance scores and sort
        top_creators = []
        for creator_id, stats in creator_stats.items():
            success_rate = (stats["successful"] / stats["collaborations"]) * 100 if stats["collaborations"] > 0 else 0
            
            # Calculate performance score (weighted combination of metrics)
            performance_score = (
                success_rate * 0.4 +  # 40% success rate
                min(stats["collaborations"] * 2, 50) * 0.3 +  # 30% activity (capped at 25 collaborations = 50 points)
                min(float(stats["total_value"]) / 1000, 50) * 0.2 +  # 20% value (capped at 50k = 50 points)
                min(len(stats["brands"]) * 10, 50) * 0.1  # 10% network diversity (capped at 5 brands = 50 points)
            )
            
            # Update Prometheus metric
            creator_tier = self._get_creator_tier(creator_id)
            self.creator_performance_score.labels(
                creator_id=str(creator_id),
                tier=creator_tier
            ).set(performance_score)
            
            top_creators.append({
                "creator_id": creator_id,
                "performance_score": round(performance_score, 2),
                "success_rate": round(success_rate, 2),
                "total_collaborations": stats["collaborations"],
                "successful_collaborations": stats["successful"],
                "total_value": float(stats["total_value"]),
                "collaboration_types": len(stats["types"]),
                "brand_partnerships": len(stats["brands"]),
                "tier": creator_tier
            })
        
        return sorted(top_creators, key=lambda x: x["performance_score"], reverse=True)[:limit]
    
    async def _calculate_brand_metrics(self, events: List[CollaborationEvent]) -> Dict[str, Any]:
        """Calculate brand performance metrics"""        brand_stats = defaultdict(lambda: {
            "collaborations": 0,
            "successful": 0,
            "total_value": Decimal('0'),
            "creators": set(),
            "types": set()
        })
        
        # Group by collaboration
        collaborations = defaultdict(list)
        for event in events:
            collaborations[event.collaboration_id].append(event)
        
        for collab_events in collaborations.values():
            brand_id = collab_events[0].brand_id
            if not brand_id:
                continue
                
            creator_id = collab_events[0].creator_id
            final_status = collab_events[-1].status
            collab_type = collab_events[0].collaboration_type
            value = collab_events[0].value or Decimal('0')
            
            stats = brand_stats[brand_id]
            stats["collaborations"] += 1
            stats["total_value"] += value
            stats["creators"].add(creator_id)
            stats["types"].add(collab_type.value)
            
            if final_status == CollaborationStatus.COMPLETED:
                stats["successful"] += 1
        
        # Calculate brand metrics
        brand_metrics = []
        for brand_id, stats in brand_stats.items():
            success_rate = (stats["successful"] / stats["collaborations"]) * 100 if stats["collaborations"] > 0 else 0
            
            brand_metrics.append({
                "brand_id": brand_id,
                "success_rate": round(success_rate, 2),
                "total_collaborations": stats["collaborations"],
                "successful_collaborations": stats["successful"],
                "total_investment": float(stats["total_value"]),
                "creator_network_size": len(stats["creators"]),
                "collaboration_diversity": len(stats["types"])
            })
        
        return {
            "top_brands": sorted(brand_metrics, key=lambda x: x["success_rate"], reverse=True)[:10],
            "total_brands": len(brand_stats),
            "average_success_rate": statistics.mean([b["success_rate"] for b in brand_metrics]) if brand_metrics else 0
        }
    
    async def _calculate_collaboration_funnel(self, events: List[CollaborationEvent]) -> Dict[str, Any]:
        """Calculate collaboration conversion funnel"""        status_counts = Counter(event.status.value for event in events)
        
        # Define funnel stages
        funnel_stages = [
            ("proposed", "Proposals"),
            ("negotiating", "Negotiations"),
            ("accepted", "Accepted"),
            ("active", "Active"),
            ("completed", "Completed")
        ]
        
        funnel_data = []
        total_proposed = status_counts.get("proposed", 0) or 1  # Avoid division by zero
        
        for status, label in funnel_stages:
            count = status_counts.get(status, 0)
            conversion_rate = (count / total_proposed) * 100
            
            funnel_data.append({
                "stage": label,
                "count": count,
                "conversion_rate": round(conversion_rate, 2)
            })
        
        return {
            "funnel": funnel_data,
            "dropout_analysis": {
                "proposal_to_negotiation": round((status_counts.get("negotiating", 0) / total_proposed) * 100, 2),
                "negotiation_to_acceptance": round((status_counts.get("accepted", 0) / max(status_counts.get("negotiating", 1), 1)) * 100, 2),
                "acceptance_to_completion": round((status_counts.get("completed", 0) / max(status_counts.get("accepted", 1), 1)) * 100, 2)
            }
        }
    
    async def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate collaboration network metrics"""        # Calculate network density and connections
        total_creators = len([key for key in self.collaboration_networks.keys() if key.startswith("creator_")])
        total_brands = len([key for key in self.collaboration_networks.keys() if key.startswith("brand_")])
        
        # Calculate average connections
        creator_connections = [
            len(connections) for key, connections in self.collaboration_networks.items()
            if key.startswith("creator_")
        ]
        
        brand_connections = [
            len(connections) for key, connections in self.collaboration_networks.items()
            if key.startswith("brand_")
        ]
        
        return {
            "total_creators": total_creators,
            "total_brands": total_brands,
            "average_creator_connections": statistics.mean(creator_connections) if creator_connections else 0,
            "average_brand_connections": statistics.mean(brand_connections) if brand_connections else 0,
            "network_density": round((len(self.collaboration_events) / max(total_creators * total_brands, 1)) * 100, 4),
            "most_connected_creators": await self._get_most_connected_nodes("creator_"),
            "most_connected_brands": await self._get_most_connected_nodes("brand_")
        }
    
    async def _get_most_connected_nodes(self, prefix: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most connected nodes in collaboration network"""        connections = [
            (key.replace(prefix, ""), len(connections))
            for key, connections in self.collaboration_networks.items()
            if key.startswith(prefix)
        ]
        
        return [
            {"id": int(node_id), "connections": count}
            for node_id, count in sorted(connections, key=lambda x: x[1], reverse=True)[:limit]
        ]
    
    async def _calculate_collaboration_trends(self, period_days: int) -> Dict[str, Any]:
        """Calculate collaboration trends"""        # Implementation for trend calculation
        return {
            "growth_rate": "Implementation needed",
            "seasonal_patterns": "Implementation needed",
            "type_trends": "Implementation needed"
        }
    
    async def _generate_optimization_recommendations(self, events: List[CollaborationEvent]) -> List[str]:
        """Generate optimization recommendations"""        recommendations = []
        
        # Analyze success rates by type
        if events:
            type_success = await self._calculate_success_by_type({
                event.collaboration_id: [event] for event in events
            })
            
            # Find underperforming types
            for collab_type, success_rate in type_success.items():
                if success_rate < 50:
                    recommendations.append(f"Improve {collab_type.replace('_', ' ')} success rate (currently {success_rate}%)")
        
        return recommendations
    
    async def _update_creator_performance(self, creator_id: int) -> None:
        """Update creator performance metrics"""        try:
            creator_events = [
                event for event in self.collaboration_events
                if event.creator_id == creator_id
            ]
            
            if not creator_events:
                return
            
            # Calculate performance metrics
            total_collaborations = len(set(event.collaboration_id for event in creator_events))
            
            # Group by collaboration to determine success
            collaborations = defaultdict(list)
            for event in creator_events:
                collaborations[event.collaboration_id].append(event)
            
            successful = sum(
                1 for collab_events in collaborations.values()
                if collab_events[-1].status == CollaborationStatus.COMPLETED
            )
            
            total_revenue = sum(event.value or Decimal('0') for event in creator_events)
            
            # Store performance data
            performance = CreatorPerformance(
                creator_id=creator_id,
                total_collaborations=total_collaborations,
                successful_collaborations=successful,
                total_revenue=total_revenue,
                average_engagement=0.0,  # Would be calculated from actual engagement data
                completion_rate=(successful / total_collaborations * 100) if total_collaborations > 0 else 0,
                satisfaction_score=0.0,  # Would be calculated from satisfaction surveys
                partner_retention_rate=0.0,  # Would be calculated from repeat partnerships
                response_time_hours=0.0,  # Would be calculated from communication data
                content_quality_score=0.0  # Would be calculated from content analysis
            )
            
            self.creator_metrics[creator_id] = performance
            
        except Exception as e:
            logger.error(f"Error updating creator performance: {e}")
    
    async def _update_brand_metrics(self, brand_id: int, event: CollaborationEvent) -> None:
        """Update brand metrics"""        try:
            if brand_id not in self.brand_metrics:
                self.brand_metrics[brand_id] = {
                    "total_collaborations": 0,
                    "total_investment": Decimal('0'),
                    "creator_network": set(),
                    "satisfaction_scores": []
                }
            
            metrics = self.brand_metrics[brand_id]
            metrics["total_collaborations"] += 1
            metrics["creator_network"].add(event.creator_id)
            
            if event.value:
                metrics["total_investment"] += event.value
                
        except Exception as e:
            logger.error(f"Error updating brand metrics: {e}")
    
    async def _update_success_rates(self, collaboration_type: CollaborationType, creator_tier: str) -> None:
        """Update success rate metrics"""        try:
            # Calculate success rate for this type and tier
            relevant_events = [
                event for event in self.collaboration_events
                if event.collaboration_type == collaboration_type and self._get_creator_tier(event.creator_id) == creator_tier
            ]
            
            if not relevant_events:
                return
            
            # Group by collaboration ID
            collaborations = defaultdict(list)
            for event in relevant_events:
                collaborations[event.collaboration_id].append(event)
            
            successful = sum(
                1 for collab_events in collaborations.values()
                if collab_events[-1].status == CollaborationStatus.COMPLETED
            )
            
            success_rate = (successful / len(collaborations)) * 100 if collaborations else 0
            
            # Update Prometheus metric
            self.collaboration_success_rate.labels(
                type=collaboration_type.value,
                creator_tier=creator_tier
            ).set(success_rate)
            
        except Exception as e:
            logger.error(f"Error updating success rates: {e}")
    
    def _get_creator_tier(self, creator_id: int) -> str:
        """Get creator tier based on performance (simplified logic)"""        if creator_id in self.creator_metrics:
            performance = self.creator_metrics[creator_id]
            if performance.total_collaborations >= 10 and performance.completion_rate >= 80:
                return "premium"
            elif performance.total_collaborations >= 5 and performance.completion_rate >= 60:
                return "standard"
            else:
                return "basic"
        else:
            return "new"
    
    def get_tracker_stats(self) -> Dict[str, Any]:
        """Get collaboration tracker statistics"""        return {
            "total_events": len(self.collaboration_events),
            "unique_collaborations": len(set(event.collaboration_id for event in self.collaboration_events)),
            "unique_creators": len(set(event.creator_id for event in self.collaboration_events)),
            "unique_brands": len(set(event.brand_id for event in self.collaboration_events if event.brand_id)),
            "tracked_creators": len(self.creator_metrics),
            "tracked_brands": len(self.brand_metrics),
            "network_connections": len(self.collaboration_networks),
            "cache_entries": len(self.analytics_cache)
        }


# Export classes
__all__ = [
    "CollaborationSuccessTracker",
    "CollaborationEvent",
    "CreatorPerformance", 
    "CollaborationType",
    "CollaborationStatus"
]