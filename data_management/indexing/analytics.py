"""IA Influencer Agent - Advanced Indexing Analytics
=================================================

Enterprise-grade analytics system for content indexing insights,
trend analysis, usage patterns, and business intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from redis.asyncio import Redis
import io
import base64

logger = logging.getLogger(__name__)


@dataclass
class ContentAnalytics:
    """Content analytics structure"""
    total_content_indexed: int
    content_by_type: Dict[str, int]
    content_by_creator: Dict[str, int]
    trending_tags: List[Tuple[str, int]]
    popular_categories: List[Tuple[str, int]]
    indexing_velocity: Dict[str, float]  # items per hour by type
    storage_distribution: Dict[str, float]  # GB by type
    protection_levels: Dict[str, int]


@dataclass
class SearchAnalytics:
    """Search analytics structure"""
    total_searches: int
    search_types: Dict[str, int]  # text, vector, hybrid
    popular_queries: List[Tuple[str, int]]
    search_success_rate: float
    average_response_time: float
    results_clicked: Dict[str, int]
    search_patterns: Dict[str, Any]
    user_behavior: Dict[str, Any]


@dataclass
class PerformanceAnalytics:
    """Performance analytics structure"""
    processing_throughput: Dict[str, float]  # items per minute by type
    resource_utilization: Dict[str, float]  # CPU, memory, GPU, storage
    bottlenecks_identified: List[str]
    scalability_metrics: Dict[str, float]
    cost_efficiency: Dict[str, float]
    sla_compliance: Dict[str, float]


@dataclass
class BusinessInsights:
    """Business intelligence insights"""
    creator_engagement: Dict[str, Any]
    content_performance: Dict[str, Any]
    revenue_potential: Dict[str, float]
    market_trends: List[str]
    competitive_analysis: Dict[str, Any]
    growth_opportunities: List[str]


class ContentAnalyticsEngine:
    """Analyzes content indexing patterns and trends"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.analytics_cache = {}
        
    async def initialize(self):
        """Initialize analytics engine"""
        try:
            self.redis_client = Redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("ContentAnalyticsEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContentAnalyticsEngine: {e}")
            raise
    
    async def generate_content_analytics(
        self, time_range: Dict[str, datetime] = None
    ) -> ContentAnalytics:
        """Generate comprehensive content analytics"""
        try:
            if not time_range:
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=30)
                time_range = {"start": start_date, "end": end_date}
            
            # Get content data from Redis
            content_data = await self._fetch_content_data(time_range)
            
            # Analyze content distribution
            content_by_type = Counter()
            content_by_creator = Counter()
            all_tags = []
            all_categories = []
            protection_levels = Counter()
            storage_by_type = defaultdict(float)
            
            for content in content_data:
                content_type = content.get("content_type", "unknown")
                creator_id = content.get("creator_id", "unknown")
                tags = content.get("tags", [])
                category = content.get("category", "uncategorized")
                protection = content.get("protection_level", "standard")
                file_size = content.get("file_size", 0)
                
                content_by_type[content_type] += 1
                content_by_creator[creator_id] += 1
                all_tags.extend(tags)
                all_categories.append(category)
                protection_levels[protection] += 1
                storage_by_type[content_type] += file_size / (1024**3)  # GB
            
            # Calculate trending tags
            tag_counter = Counter(all_tags)
            trending_tags = tag_counter.most_common(20)
            
            # Calculate popular categories
            category_counter = Counter(all_categories)
            popular_categories = category_counter.most_common(10)
            
            # Calculate indexing velocity
            time_diff_hours = (time_range["end"] - time_range["start"]).total_seconds() / 3600
            indexing_velocity = {}
            for content_type, count in content_by_type.items():
                indexing_velocity[content_type] = count / time_diff_hours
            
            return ContentAnalytics(
                total_content_indexed=len(content_data),
                content_by_type=dict(content_by_type),
                content_by_creator=dict(content_by_creator.most_common(50)),
                trending_tags=trending_tags,
                popular_categories=popular_categories,
                indexing_velocity=indexing_velocity,
                storage_distribution=dict(storage_by_type),
                protection_levels=dict(protection_levels)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate content analytics: {e}")
            raise
    
    async def _fetch_content_data(
        self, time_range: Dict[str, datetime]
    ) -> List[Dict[str, Any]]:
        """Fetch content data from Redis for the specified time range"""
        try:
            # Get content IDs within time range
            start_timestamp = time_range["start"].timestamp()
            end_timestamp = time_range["end"].timestamp()
            
            content_ids = await self.redis_client.zrangebyscore(
                "indexed_content_timeline",
                start_timestamp,
                end_timestamp
            )
            
            # Fetch content metadata
            content_data = []
            for content_id in content_ids:
                metadata = await self.redis_client.hgetall(f"content_metadata:{content_id}")
                if metadata:
                    # Convert Redis hash to dict
                    content_dict = {}
                    for key, value in metadata.items():
                        try:
                            content_dict[key] = json.loads(value)
                        except:
                            content_dict[key] = value
                    content_data.append(content_dict)
            
            return content_data
            
        except Exception as e:
            logger.error(f"Failed to fetch content data: {e}")
            return []
    
    async def analyze_content_clusters(
        self, content_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content clusters using machine learning"""
        try:
            if len(content_data) < 10:
                return {"status": "insufficient_data"}
            
            # Prepare features for clustering
            features = []
            content_ids = []
            
            for content in content_data:
                if "embeddings" in content:
                    features.append(content["embeddings"])
                    content_ids.append(content.get("content_id", "unknown"))
            
            if len(features) < 10:
                return {"status": "insufficient_embeddings"}
            
            # Perform clustering
            features_array = np.array(features)
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features_array)
            
            # Determine optimal number of clusters
            max_clusters = min(10, len(features) // 5)
            if max_clusters < 2:
                max_clusters = 2
            
            kmeans = KMeans(n_clusters=max_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_features)
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id in range(max_clusters):
                cluster_indices = np.where(cluster_labels == cluster_id)[0]
                cluster_content = [content_data[i] for i in cluster_indices]
                
                # Analyze cluster characteristics
                cluster_types = Counter([
                    content.get("content_type", "unknown") 
                    for content in cluster_content
                ])
                
                cluster_creators = Counter([
                    content.get("creator_id", "unknown")
                    for content in cluster_content
                ])
                
                cluster_tags = []
                for content in cluster_content:
                    cluster_tags.extend(content.get("tags", []))
                cluster_tag_counter = Counter(cluster_tags)
                
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "size": len(cluster_content),
                    "content_types": dict(cluster_types),
                    "top_creators": dict(cluster_creators.most_common(5)),
                    "common_tags": dict(cluster_tag_counter.most_common(10)),
                    "centroid": kmeans.cluster_centers_[cluster_id].tolist()
                }
            
            return {
                "status": "success",
                "total_clusters": max_clusters,
                "cluster_analysis": cluster_analysis,
                "silhouette_score": self._calculate_silhouette_score(
                    scaled_features, cluster_labels
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze content clusters: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_silhouette_score(
        self, features: np.ndarray, labels: np.ndarray
    ) -> float:
        """Calculate silhouette score for clustering quality"""
        try:
            from sklearn.metrics import silhouette_score
            return float(silhouette_score(features, labels))
        except:
            return 0.0
    
    async def generate_trend_analysis(
        self, days_back: int = 30
    ) -> Dict[str, Any]:
        """Generate trend analysis for content indexing"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_back)
            
            # Get daily content counts
            daily_counts = defaultdict(lambda: defaultdict(int))
            
            for i in range(days_back):
                date = start_date + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Get content indexed on this date
                day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                time_range = {"start": day_start, "end": day_end}
                content_data = await self._fetch_content_data(time_range)
                
                for content in content_data:
                    content_type = content.get("content_type", "unknown")
                    daily_counts[date_str][content_type] += 1
                    daily_counts[date_str]["total"] += 1
            
            # Calculate trends
            trends = {}
            for content_type in ["audio", "video", "image", "text", "total"]:
                values = [
                    daily_counts[
                        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                    ][content_type]
                    for i in range(days_back)
                ]
                
                # Calculate trend direction and strength
                if len(values) > 1:
                    x = np.arange(len(values))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                    
                    trends[content_type] = {
                        "values": values,
                        "slope": float(slope),
                        "correlation": float(r_value),
                        "p_value": float(p_value),
                        "trend_direction": "increasing" if slope > 0 else "decreasing",
                        "trend_strength": abs(float(r_value)),
                        "average": float(np.mean(values)),
                        "growth_rate": float(slope * days_back / np.mean(values)) if np.mean(values) > 0 else 0
                    }
            
            return {
                "period_days": days_back,
                "trends": trends,
                "daily_counts": dict(daily_counts),
                "insights": self._generate_trend_insights(trends)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate trend analysis: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_trend_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []
        
        for content_type, trend_data in trends.items():
            if content_type == "total":
                continue
                
            growth_rate = trend_data.get("growth_rate", 0)
            trend_strength = trend_data.get("trend_strength", 0)
            
            if growth_rate > 0.1 and trend_strength > 0.5:
                insights.append(
                    f"{content_type.title()} content is growing rapidly "
                    f"({growth_rate:.1%} growth rate)"
                )
            elif growth_rate < -0.1 and trend_strength > 0.5:
                insights.append(
                    f"{content_type.title()} content is declining "
                    f"({abs(growth_rate):.1%} decline rate)"
                )
            elif trend_strength < 0.3:
                insights.append(
                    f"{content_type.title()} content shows stable pattern"
                )
        
        total_growth = trends.get("total", {}).get("growth_rate", 0)
        if total_growth > 0.2:
            insights.append("Overall content indexing is accelerating significantly")
        elif total_growth > 0.05:
            insights.append("Overall content indexing is growing steadily")
        elif total_growth < -0.05:
            insights.append("Overall content indexing is declining")
        
        return insights


class SearchAnalyticsEngine:
    """Analyzes search patterns and user behavior"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        
    async def initialize(self):
        """Initialize search analytics engine"""
        try:
            self.redis_client = Redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("SearchAnalyticsEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SearchAnalyticsEngine: {e}")
            raise
    
    async def generate_search_analytics(
        self, time_range: Dict[str, datetime] = None
    ) -> SearchAnalytics:
        """Generate comprehensive search analytics"""
        try:
            if not time_range:
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=7)
                time_range = {"start": start_date, "end": end_date}
            
            # Fetch search data
            search_data = await self._fetch_search_data(time_range)
            
            if not search_data:
                return SearchAnalytics(
                    total_searches=0,
                    search_types={},
                    popular_queries=[],
                    search_success_rate=0.0,
                    average_response_time=0.0,
                    results_clicked={},
                    search_patterns={},
                    user_behavior={}
                )
            
            # Analyze search types
            search_types = Counter([
                search.get("search_type", "unknown") for search in search_data
            ])
            
            # Analyze popular queries
            queries = [
                search.get("query_text", "") for search in search_data
                if search.get("query_text")
            ]
            query_counter = Counter(queries)
            popular_queries = query_counter.most_common(20)
            
            # Calculate success rate
            successful_searches = [
                search for search in search_data
                if search.get("results_count", 0) > 0
            ]
            success_rate = len(successful_searches) / len(search_data) * 100
            
            # Calculate average response time
            response_times = [
                search.get("response_time_ms", 0) for search in search_data
            ]
            avg_response_time = np.mean(response_times) if response_times else 0
            
            # Analyze click patterns
            results_clicked = Counter()
            for search in search_data:
                clicked_results = search.get("clicked_results", [])
                for result in clicked_results:
                    content_type = result.get("content_type", "unknown")
                    results_clicked[content_type] += 1
            
            # Analyze search patterns
            search_patterns = await self._analyze_search_patterns(search_data)
            
            # Analyze user behavior
            user_behavior = await self._analyze_user_behavior(search_data)
            
            return SearchAnalytics(
                total_searches=len(search_data),
                search_types=dict(search_types),
                popular_queries=popular_queries,
                search_success_rate=success_rate,
                average_response_time=avg_response_time,
                results_clicked=dict(results_clicked),
                search_patterns=search_patterns,
                user_behavior=user_behavior
            )
            
        except Exception as e:
            logger.error(f"Failed to generate search analytics: {e}")
            raise
    
    async def _fetch_search_data(
        self, time_range: Dict[str, datetime]
    ) -> List[Dict[str, Any]]:
        """Fetch search data from Redis"""
        try:
            start_timestamp = time_range["start"].timestamp()
            end_timestamp = time_range["end"].timestamp()
            
            search_entries = await self.redis_client.zrangebyscore(
                "search_analytics",
                start_timestamp,
                end_timestamp,
                withscores=True
            )
            
            search_data = []
            for entry, timestamp in search_entries:
                try:
                    search_dict = json.loads(entry)
                    search_dict["timestamp"] = timestamp
                    search_data.append(search_dict)
                except:
                    continue
            
            return search_data
            
        except Exception as e:
            logger.error(f"Failed to fetch search data: {e}")
            return []
    
    async def _analyze_search_patterns(
        self, search_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze search patterns"""
        try:
            # Hourly distribution
            hourly_distribution = defaultdict(int)
            for search in search_data:
                timestamp = search.get("timestamp", 0)
                hour = datetime.fromtimestamp(timestamp, timezone.utc).hour
                hourly_distribution[hour] += 1
            
            # Search length distribution
            query_lengths = [
                len(search.get("query_text", "").split())
                for search in search_data
                if search.get("query_text")
            ]
            
            # Filter usage
            filter_usage = Counter()
            for search in search_data:
                filters = search.get("filters", {})
                for filter_type in filters.keys():
                    filter_usage[filter_type] += 1
            
            return {
                "hourly_distribution": dict(hourly_distribution),
                "peak_hours": sorted(
                    hourly_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                "average_query_length": np.mean(query_lengths) if query_lengths else 0,
                "query_length_distribution": dict(Counter(query_lengths)),
                "filter_usage": dict(filter_usage)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze search patterns: {e}")
            return {}
    
    async def _analyze_user_behavior(
        self, search_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user search behavior"""
        try:
            # User session analysis
            user_sessions = defaultdict(list)
            for search in search_data:
                user_id = search.get("user_id", "anonymous")
                user_sessions[user_id].append(search)
            
            # Calculate session metrics
            session_lengths = []
            queries_per_session = []
            
            for user_id, sessions in user_sessions.items():
                session_lengths.append(len(sessions))
                if len(sessions) > 1:
                    # Calculate session duration
                    timestamps = [s.get("timestamp", 0) for s in sessions]
                    session_duration = max(timestamps) - min(timestamps)
                    queries_per_session.append(len(sessions))
            
            # Repeat search analysis
            repeat_queries = defaultdict(int)
            for search in search_data:
                query = search.get("query_text", "")
                if query:
                    repeat_queries[query] += 1
            
            repeated_queries = {
                query: count for query, count in repeat_queries.items()
                if count > 1
            }
            
            return {
                "unique_users": len(user_sessions),
                "average_queries_per_user": np.mean(session_lengths) if session_lengths else 0,
                "repeat_search_rate": len(repeated_queries) / len(repeat_queries) * 100 if repeat_queries else 0,
                "most_repeated_queries": sorted(
                    repeated_queries.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user behavior: {e}")
            return {}


class VisualizationEngine:
    """Generates visualizations for analytics data"""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.color_palette = sns.color_palette("husl", 10)
    
    async def create_content_distribution_chart(
        self, content_analytics: ContentAnalytics
    ) -> str:
        """Create content distribution pie chart"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Content by type
            types = list(content_analytics.content_by_type.keys())
            counts = list(content_analytics.content_by_type.values())
            
            ax1.pie(counts, labels=types, autopct='%1.1f%%', colors=self.color_palette)
            ax1.set_title('Content Distribution by Type', fontsize=14, fontweight='bold')
            
            # Storage distribution
            storage_types = list(content_analytics.storage_distribution.keys())
            storage_sizes = list(content_analytics.storage_distribution.values())
            
            ax2.pie(storage_sizes, labels=storage_types, autopct='%1.1f%%', colors=self.color_palette)
            ax2.set_title('Storage Distribution by Type (GB)', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Failed to create content distribution chart: {e}")
            return ""
    
    async def create_trend_analysis_chart(
        self, trend_data: Dict[str, Any]
    ) -> str:
        """Create trend analysis line chart"""
        try:
            trends = trend_data.get("trends", {})
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            for content_type, data in trends.items():
                if content_type == "total":
                    continue
                    
                values = data.get("values", [])
                if values:
                    days = list(range(len(values)))
                    ax.plot(days, values, marker='o', label=content_type.title(), linewidth=2)
            
            ax.set_xlabel('Days', fontsize=12)
            ax.set_ylabel('Content Count', fontsize=12)
            ax.set_title('Content Indexing Trends', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Failed to create trend analysis chart: {e}")
            return ""
