"""Content Clustering Workflow

AI-powered content clustering and topic modeling workflow for SEO optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class ContentCluster:
    """Content cluster definition"""
    cluster_id: str
    topic: str
    keywords: List[str]
    content_pieces: List[str]
    cluster_authority: float
    internal_linking_score: float
    content_gap_opportunities: List[str]
    pillar_content_url: str = ""


@dataclass
class ClusteringAnalysis:
    """Content clustering analysis result"""
    analysis_id: str
    clusters: List[ContentCluster]
    orphaned_content: List[str]
    linking_opportunities: List[Dict[str, Any]]
    content_strategy_recommendations: List[str]
    topical_authority_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContentClusteringWorkflow:
    """AI-powered content clustering workflow"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager()
        
    async def analyze_content_clusters(
        self,
        existing_content: List[Dict[str, Any]],
        target_keywords: List[str],
        domain: str
    ) -> ClusteringAnalysis:
        """
        Analyze and create content clusters for topical authority
        
        Args:
            existing_content: List of existing content pieces with metadata
            target_keywords: Target keywords for clustering
            domain: Domain for analysis
            
        Returns:
            ClusteringAnalysis with cluster recommendations
        """
        try:
            start_time = datetime.utcnow()
            analysis_id = f"clustering_{int(start_time.timestamp())}"
            
            logger.info(f"Starting content clustering analysis for {len(existing_content)} pieces")
            
            # Perform topic modeling
            topics = await self._identify_topics(existing_content, target_keywords)
            
            # Create content clusters
            clusters = await self._create_content_clusters(existing_content, topics)
            
            # Identify orphaned content
            orphaned_content = await self._identify_orphaned_content(existing_content, clusters)
            
            # Find internal linking opportunities
            linking_opportunities = await self._find_linking_opportunities(clusters)
            
            # Generate content strategy recommendations
            strategy_recommendations = await self._generate_strategy_recommendations(clusters, orphaned_content)
            
            # Calculate topical authority score
            authority_score = await self._calculate_topical_authority(clusters)
            
            analysis = ClusteringAnalysis(
                analysis_id=analysis_id,
                clusters=clusters,
                orphaned_content=orphaned_content,
                linking_opportunities=linking_opportunities,
                content_strategy_recommendations=strategy_recommendations,
                topical_authority_score=authority_score
            )
            
            # Cache result
            await self._cache_analysis(analysis)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric("clustering_duration", duration)
            await self.metrics_collector.record_metric("topical_authority_score", authority_score)
            
            logger.info(f"Content clustering completed. Authority score: {authority_score:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Content clustering analysis failed: {e}")
            raise WorkflowError(f"Content clustering analysis failed: {e}")
    
    async def _identify_topics(self, content: List[Dict[str, Any]], keywords: List[str]) -> List[str]:
        """Identify main topics from content and keywords"""
        # Simulate topic modeling
        topics = [
            "Digital Marketing",
            "SEO Optimization", 
            "Content Strategy",
            "Social Media",
            "Analytics & Reporting",
            "Technical SEO",
            "Local SEO",
            "Mobile Optimization"
        ]
        
        # Filter topics based on content and keywords
        relevant_topics = []
        for topic in topics:
            topic_relevance = sum(1 for kw in keywords if any(word in kw.lower() for word in topic.lower().split()))
            if topic_relevance > 0:
                relevant_topics.append(topic)
        
        return relevant_topics[:6]  # Limit to top 6 topics
    
    async def _create_content_clusters(self, content: List[Dict[str, Any]], topics: List[str]) -> List[ContentCluster]:
        """Create content clusters based on topics"""
        clusters = []
        
        for i, topic in enumerate(topics):
            # Simulate clustering
            import random
            
            cluster_keywords = [
                f"{topic.lower()} strategy",
                f"{topic.lower()} tips",
                f"{topic.lower()} best practices",
                f"how to {topic.lower()}",
                f"{topic.lower()} guide"
            ]
            
            # Assign content to clusters
            cluster_content = [
                item.get("url", f"https://example.com/content-{j}")
                for j, item in enumerate(content)
                if j % len(topics) == i
            ]
            
            # Calculate cluster metrics
            authority = random.uniform(0.4, 0.9)
            linking_score = random.uniform(0.3, 0.8)
            
            # Identify content gaps
            content_gaps = [
                f"{topic} comprehensive guide",
                f"{topic} case studies", 
                f"{topic} tools comparison",
                f"{topic} advanced techniques"
            ]
            
            cluster = ContentCluster(
                cluster_id=f"cluster_{i+1}",
                topic=topic,
                keywords=cluster_keywords,
                content_pieces=cluster_content,
                cluster_authority=authority,
                internal_linking_score=linking_score,
                content_gap_opportunities=content_gaps[:2],  # Top 2 gaps
                pillar_content_url=cluster_content[0] if cluster_content else ""
            )
            
            clusters.append(cluster)
        
        return clusters
    
    async def _identify_orphaned_content(self, content: List[Dict[str, Any]], clusters: List[ContentCluster]) -> List[str]:
        """Identify content that doesn't belong to any cluster"""
        clustered_urls = set()
        for cluster in clusters:
            clustered_urls.update(cluster.content_pieces)
        
        orphaned = []
        for item in content:
            url = item.get("url", "")
            if url and url not in clustered_urls:
                orphaned.append(url)
        
        return orphaned
    
    async def _find_linking_opportunities(self, clusters: List[ContentCluster]) -> List[Dict[str, Any]]:
        """Find internal linking opportunities between clusters"""
        opportunities = []
        
        for i, cluster1 in enumerate(clusters):
            for j, cluster2 in enumerate(clusters):
                if i != j and cluster1.content_pieces and cluster2.content_pieces:
                    # Simulate linking opportunity scoring
                    import random
                    relevance_score = random.uniform(0.3, 0.9)
                    
                    if relevance_score > 0.6:
                        opportunity = {
                            "from_cluster": cluster1.topic,
                            "to_cluster": cluster2.topic,
                            "from_url": cluster1.content_pieces[0],
                            "to_url": cluster2.content_pieces[0],
                            "relevance_score": relevance_score,
                            "anchor_text_suggestion": f"Learn more about {cluster2.topic.lower()}",
                            "link_placement": "contextual within content"
                        }
                        opportunities.append(opportunity)
        
        # Sort by relevance score and return top opportunities
        opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
        return opportunities[:20]
    
    async def _generate_strategy_recommendations(self, clusters: List[ContentCluster], orphaned: List[str]) -> List[str]:
        """Generate content strategy recommendations"""
        recommendations = []
        
        # Cluster-specific recommendations
        weak_clusters = [c for c in clusters if c.cluster_authority < 0.6]
        if weak_clusters:
            recommendations.append(f"Strengthen {len(weak_clusters)} weak content clusters with more comprehensive content")
        
        poor_linking_clusters = [c for c in clusters if c.internal_linking_score < 0.5]
        if poor_linking_clusters:
            recommendations.append(f"Improve internal linking for {len(poor_linking_clusters)} clusters")
        
        # Content gap recommendations
        total_gaps = sum(len(c.content_gap_opportunities) for c in clusters)
        if total_gaps > 0:
            recommendations.append(f"Create {total_gaps} new content pieces to fill identified gaps")
        
        # Orphaned content recommendations
        if orphaned:
            recommendations.append(f"Integrate {len(orphaned)} orphaned content pieces into relevant clusters")
        
        # General strategy recommendations
        recommendations.extend([
            "Establish pillar pages for each major topic cluster",
            "Create topic-specific content hubs with strong internal linking",
            "Develop comprehensive guides as cluster authority builders",
            "Implement consistent keyword targeting within each cluster",
            "Monitor cluster performance and adjust strategy based on rankings",
            "Build external links to strengthen cluster authority",
            "Create content calendars aligned with cluster topics",
            "Optimize existing content within clusters for better performance"
        ])
        
        return recommendations[:15]
    
    async def _calculate_topical_authority(self, clusters: List[ContentCluster]) -> float:
        """Calculate overall topical authority score"""
        if not clusters:
            return 0.0
        
        # Calculate weighted average based on cluster authority and size
        total_weight = 0
        weighted_authority = 0
        
        for cluster in clusters:
            content_count = len(cluster.content_pieces)
            weight = content_count * cluster.cluster_authority
            
            total_weight += content_count
            weighted_authority += weight
        
        if total_weight == 0:
            return 0.0
        
        base_authority = weighted_authority / total_weight
        
        # Bonus for having multiple strong clusters
        strong_clusters = len([c for c in clusters if c.cluster_authority > 0.7])
        cluster_bonus = min(strong_clusters / len(clusters) * 0.2, 0.2)
        
        # Bonus for good internal linking
        avg_linking_score = sum(c.internal_linking_score for c in clusters) / len(clusters)
        linking_bonus = avg_linking_score * 0.1
        
        total_authority = base_authority + cluster_bonus + linking_bonus
        return min(total_authority, 1.0)
    
    async def _cache_analysis(self, analysis -> None: ClusteringAnalysis) -> None:
        """Cache clustering analysis result"""
        cache_key = f"clustering_{analysis.analysis_id}"
        await self.cache_manager.set(cache_key, analysis, ttl=3600)
    
    async def recommend_pillar_content(self, clusters: List[ContentCluster]) -> List[Dict[str, Any]]:
        """Recommend pillar content for each cluster"""
        recommendations = []
        
        for cluster in clusters:
            if not cluster.pillar_content_url or cluster.cluster_authority < 0.7:
                recommendation = {
                    "cluster_topic": cluster.topic,
                    "suggested_title": f"Complete Guide to {cluster.topic}",
                    "target_keywords": cluster.keywords[:3],
                    "content_type": "comprehensive guide",
                    "estimated_word_count": 3000,
                    "sections_to_include": [
                        f"Introduction to {cluster.topic}",
                        f"{cluster.topic} fundamentals", 
                        f"Advanced {cluster.topic} strategies",
                        f"{cluster.topic} tools and resources",
                        f"{cluster.topic} best practices",
                        f"Common {cluster.topic} mistakes to avoid"
                    ],
                    "internal_links_to_include": cluster.content_pieces[:5],
                    "priority": "high" if cluster.cluster_authority < 0.5 else "medium"
                }
                recommendations.append(recommendation)
        
        return recommendations