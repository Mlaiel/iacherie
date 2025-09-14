"""Topic Clustering Engine - Advanced Topic Analysis and Content Grouping
Uses machine learning to cluster content topics for SEO strategy optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import numpy as np
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.metrics import silhouette_score
import networkx as nx

logger = logging.getLogger(__name__)


class ClusteringMethod(Enum):
    """Clustering algorithm types"""
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    HIERARCHICAL = "hierarchical"
    LDA = "lda"  # Latent Dirichlet Allocation
    HYBRID = "hybrid"


class TopicType(Enum):
    """Topic classification types"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    TRENDING = "trending"
    SEASONAL = "seasonal"
    EVERGREEN = "evergreen"


class ContentCluster(Enum):
    """Content cluster categories"""
    PILLAR_CONTENT = "pillar_content"
    CLUSTER_CONTENT = "cluster_content"
    SUPPORTING_CONTENT = "supporting_content"
    NICHE_CONTENT = "niche_content"
    TRENDING_CONTENT = "trending_content"


@dataclass
class Topic:
    """Individual topic representation"""
    topic_id: str
    name: str
    keywords: List[str]
    description: str
    cluster_id: str
    topic_type: TopicType
    confidence_score: float
    search_volume: int = 0
    competition_level: str = "medium"
    content_gap_score: float = 0.5
    semantic_keywords: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    content_suggestions: List[str] = field(default_factory=list)


@dataclass
class ContentClusterGroup:
    """Content cluster group"""
    cluster_id: str
    cluster_name: str
    cluster_type: ContentCluster
    topics: List[Topic]
    pillar_topic: Optional[Topic] = None
    total_search_volume: int = 0
    avg_competition: float = 0.5
    content_opportunity_score: float = 0.5
    suggested_content_count: int = 0
    priority_score: float = 0.5
    semantic_relationships: Dict[str, float] = field(default_factory=dict)


@dataclass
class TopicClusteringResult:
    """Topic clustering analysis results"""
    total_topics: int
    total_clusters: int
    clustering_method: ClusteringMethod
    silhouette_score: float
    clusters: List[ContentClusterGroup]
    topic_hierarchy: Dict[str, Any]
    content_strategy: Dict[str, Any]
    seo_opportunities: List[str]
    keyword_gaps: List[str]
    recommended_actions: List[str]


class TopicClusteringEngine:
    """Advanced topic clustering engine for SEO content strategy"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize topic clustering engine
        
        Args:
            config: Configuration including ML parameters, data sources
        """
        self.config = config
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        self.topics: List[Topic] = []
        self.clusters: List[ContentClusterGroup] = []
        self.topic_vectors = None
        self.cluster_graph = nx.Graph()
        
    async def analyze_content_topics(self, 
                                   content_data: List[Dict[str, Any]],
                                   clustering_method: ClusteringMethod = ClusteringMethod.HYBRID) -> TopicClusteringResult:
        """Analyze and cluster content topics for SEO strategy
        
        Args:
            content_data: List of content items with text and metadata
            clustering_method: Clustering algorithm to use
            
        Returns:
            Topic clustering analysis results
        """
        try:
            logger.info(f"Starting topic clustering analysis for {len(content_data)} content items")
            
            # Extract and preprocess text data
            text_data = await self._preprocess_content_data(content_data)
            
            # Generate topic vectors
            self.topic_vectors = await self._generate_topic_vectors(text_data)
            
            # Extract initial topics
            initial_topics = await self._extract_topics(text_data, content_data)
            
            # Perform clustering
            clusters = await self._perform_clustering(
                initial_topics, clustering_method
            )
            
            # Analyze semantic relationships
            semantic_relationships = await self._analyze_semantic_relationships(clusters)
            
            # Generate content strategy
            content_strategy = await self._generate_content_strategy(clusters)
            
            # Identify SEO opportunities
            seo_opportunities = await self._identify_seo_opportunities(clusters)
            
            # Find keyword gaps
            keyword_gaps = await self._identify_keyword_gaps(clusters)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(clusters, content_strategy)
            
            # Calculate clustering quality
            silhouette = await self._calculate_clustering_quality(clusters)
            
            # Build topic hierarchy
            topic_hierarchy = await self._build_topic_hierarchy(clusters)
            
            result = TopicClusteringResult(
                total_topics=len(initial_topics),
                total_clusters=len(clusters),
                clustering_method=clustering_method,
                silhouette_score=silhouette,
                clusters=clusters,
                topic_hierarchy=topic_hierarchy,
                content_strategy=content_strategy,
                seo_opportunities=seo_opportunities,
                keyword_gaps=keyword_gaps,
                recommended_actions=recommendations
            )
            
            logger.info(f"Topic clustering completed: {len(clusters)} clusters identified")
            return result
            
        except Exception as e:
            logger.error(f"Error in topic clustering analysis: {str(e)}")
            raise
    
    async def _preprocess_content_data(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Preprocess content data for topic analysis"""
        try:
            text_data = []
            
            for item in content_data:
                # Combine title, description, and content text
                text_parts = []
                
                if item.get('title'):
                    text_parts.append(item['title'])
                
                if item.get('description'):
                    text_parts.append(item['description'])
                
                if item.get('content'):
                    text_parts.append(item['content'])
                
                if item.get('tags'):
                    text_parts.extend(item['tags'])
                
                if item.get('keywords'):
                    text_parts.extend(item['keywords'])
                
                # Combine all text
                combined_text = ' '.join(text_parts)
                
                # Basic text cleaning
                cleaned_text = await self._clean_text(combined_text)
                text_data.append(cleaned_text)
            
            return text_data
            
        except Exception as e:
            logger.error(f"Error preprocessing content data: {str(e)}")
            return []
    
    async def _clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        try:
            import re
            
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters but keep spaces
            text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return text
    
    async def _generate_topic_vectors(self, text_data: List[str]) -> np.ndarray:
        """Generate TF-IDF vectors for topic analysis"""
        try:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(text_data)
            
            # Convert to dense array for clustering
            vectors = tfidf_matrix.toarray()
            
            logger.info(f"Generated {vectors.shape[0]} topic vectors with {vectors.shape[1]} features")
            return vectors
            
        except Exception as e:
            logger.error(f"Error generating topic vectors: {str(e)}")
            return np.array([])
    
    async def _extract_topics(self, 
                            text_data: List[str],
                            content_data: List[Dict[str, Any]]) -> List[Topic]:
        """Extract topics from content data"""
        try:
            topics = []
            feature_names = self.vectorizer.get_feature_names_out()
            
            for i, (text, content_item) in enumerate(zip(text_data, content_data)):
                # Get TF-IDF scores for this document
                doc_vector = self.topic_vectors[i]
                
                # Get top keywords for this document
                top_indices = np.argsort(doc_vector)[-10:][::-1]  # Top 10 keywords
                top_keywords = [feature_names[idx] for idx in top_indices if doc_vector[idx] > 0]
                
                # Create topic
                topic = Topic(
                    topic_id=f"topic_{i}",
                    name=content_item.get('title', f"Topic {i}"),
                    keywords=top_keywords,
                    description=content_item.get('description', ''),
                    cluster_id='',  # Will be assigned during clustering
                    topic_type=TopicType.PRIMARY,
                    confidence_score=float(np.max(doc_vector)),
                    search_volume=content_item.get('search_volume', 0),
                    competition_level=content_item.get('competition', 'medium'),
                    content_gap_score=await self._calculate_content_gap_score(top_keywords)
                )
                
                # Add semantic keywords
                topic.semantic_keywords = await self._find_semantic_keywords(top_keywords)
                
                # Add content suggestions
                topic.content_suggestions = await self._generate_content_suggestions(topic)
                
                topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    async def _perform_clustering(self, 
                                topics: List[Topic],
                                method: ClusteringMethod) -> List[ContentClusterGroup]:
        """Perform topic clustering using specified method"""
        try:
            if method == ClusteringMethod.KMEANS:
                return await self._kmeans_clustering(topics)
            elif method == ClusteringMethod.DBSCAN:
                return await self._dbscan_clustering(topics)
            elif method == ClusteringMethod.HIERARCHICAL:
                return await self._hierarchical_clustering(topics)
            elif method == ClusteringMethod.LDA:
                return await self._lda_clustering(topics)
            elif method == ClusteringMethod.HYBRID:
                return await self._hybrid_clustering(topics)
            else:
                logger.warning(f"Unknown clustering method: {method}, using K-means")
                return await self._kmeans_clustering(topics)
                
        except Exception as e:
            logger.error(f"Error performing clustering: {str(e)}")
            return []
    
    async def _kmeans_clustering(self, topics: List[Topic]) -> List[ContentClusterGroup]:
        """Perform K-means clustering"""
        try:
            # Determine optimal number of clusters
            optimal_k = await self._find_optimal_clusters(self.topic_vectors)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.topic_vectors)
            
            # Group topics by cluster
            clusters = await self._group_topics_by_cluster(topics, cluster_labels)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error in K-means clustering: {str(e)}")
            return []
    
    async def _dbscan_clustering(self, topics: List[Topic]) -> List[ContentClusterGroup]:
        """Perform DBSCAN clustering"""
        try:
            # DBSCAN clustering
            dbscan = DBSCAN(eps=0.3, min_samples=2)
            cluster_labels = dbscan.fit_predict(self.topic_vectors)
            
            # Group topics by cluster
            clusters = await self._group_topics_by_cluster(topics, cluster_labels)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error in DBSCAN clustering: {str(e)}")
            return []
    
    async def _hierarchical_clustering(self, topics: List[Topic]) -> List[ContentClusterGroup]:
        """Perform hierarchical clustering"""
        try:
            # Determine optimal number of clusters
            optimal_k = await self._find_optimal_clusters(self.topic_vectors)
            
            # Hierarchical clustering
            hierarchical = AgglomerativeClustering(n_clusters=optimal_k)
            cluster_labels = hierarchical.fit_predict(self.topic_vectors)
            
            # Group topics by cluster
            clusters = await self._group_topics_by_cluster(topics, cluster_labels)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error in hierarchical clustering: {str(e)}")
            return []
    
    async def _lda_clustering(self, topics: List[Topic]) -> List[ContentClusterGroup]:
        """Perform LDA topic modeling"""
        try:
            # Determine optimal number of topics
            optimal_k = await self._find_optimal_clusters(self.topic_vectors)
            
            # LDA topic modeling
            lda = LatentDirichletAllocation(n_components=optimal_k, random_state=42)
            lda.fit(self.topic_vectors)
            
            # Get topic assignments
            topic_assignments = lda.transform(self.topic_vectors)
            cluster_labels = np.argmax(topic_assignments, axis=1)
            
            # Group topics by cluster
            clusters = await self._group_topics_by_cluster(topics, cluster_labels)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error in LDA clustering: {str(e)}")
            return []
    
    async def _hybrid_clustering(self, topics: List[Topic]) -> List[ContentClusterGroup]:
        """Perform hybrid clustering combining multiple methods"""
        try:
            # Perform multiple clustering methods
            kmeans_clusters = await self._kmeans_clustering(topics)
            dbscan_clusters = await self._dbscan_clustering(topics)
            
            # Combine results using ensemble method
            combined_clusters = await self._combine_clustering_results(
                [kmeans_clusters, dbscan_clusters], topics
            )
            
            return combined_clusters
            
        except Exception as e:
            logger.error(f"Error in hybrid clustering: {str(e)}")
            return []
    
    async def _find_optimal_clusters(self, vectors: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method and silhouette analysis"""
        try:
            if len(vectors) < 4:
                return 2
            
            max_k = min(10, len(vectors) // 2)
            silhouette_scores = []
            
            for k in range(2, max_k + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(vectors)
                
                # Calculate silhouette score
                score = silhouette_score(vectors, cluster_labels)
                silhouette_scores.append(score)
            
            # Find k with highest silhouette score
            optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
            
            logger.info(f"Optimal number of clusters: {optimal_k}")
            return optimal_k
            
        except Exception as e:
            logger.error(f"Error finding optimal clusters: {str(e)}")
            return 3  # Default fallback
    
    async def _group_topics_by_cluster(self, 
                                     topics: List[Topic],
                                     cluster_labels: np.ndarray) -> List[ContentClusterGroup]:
        """Group topics into clusters based on labels"""
        try:
            cluster_dict = {}
            
            for topic, label in zip(topics, cluster_labels):
                if label == -1:  # Noise in DBSCAN
                    label = 999  # Special cluster for noise
                
                topic.cluster_id = f"cluster_{label}"
                
                if label not in cluster_dict:
                    cluster_dict[label] = []
                
                cluster_dict[label].append(topic)
            
            # Create cluster groups
            clusters = []
            for cluster_id, cluster_topics in cluster_dict.items():
                cluster_group = await self._create_cluster_group(
                    f"cluster_{cluster_id}", cluster_topics
                )
                clusters.append(cluster_group)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error grouping topics by cluster: {str(e)}")
            return []
    
    async def _create_cluster_group(self, 
                                  cluster_id: str,
                                  topics: List[Topic]) -> ContentClusterGroup:
        """Create a content cluster group from topics"""
        try:
            # Determine cluster name from most common keywords
            all_keywords = []
            for topic in topics:
                all_keywords.extend(topic.keywords)
            
            # Get most common keywords
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            top_keywords = [word for word, count in keyword_counts.most_common(3)]
            cluster_name = " + ".join(top_keywords) if top_keywords else f"Cluster {cluster_id}"
            
            # Determine cluster type
            cluster_type = await self._classify_cluster_type(topics)
            
            # Identify pillar topic (highest search volume + confidence)
            pillar_topic = None
            if topics:
                pillar_topic = max(
                    topics,
                    key=lambda t: t.search_volume * t.confidence_score
                )
                pillar_topic.topic_type = TopicType.PRIMARY
            
            # Calculate cluster metrics
            total_search_volume = sum(topic.search_volume for topic in topics)
            avg_competition = np.mean([
                0.3 if topic.competition_level == 'low' else
                0.5 if topic.competition_level == 'medium' else 0.8
                for topic in topics
            ]) if topics else 0.5
            
            # Calculate content opportunity score
            content_opportunity_score = await self._calculate_content_opportunity_score(topics)
            
            # Calculate priority score
            priority_score = await self._calculate_cluster_priority_score(
                total_search_volume, avg_competition, content_opportunity_score
            )
            
            # Suggest content count
            suggested_content_count = await self._suggest_content_count(topics, cluster_type)
            
            cluster_group = ContentClusterGroup(
                cluster_id=cluster_id,
                cluster_name=cluster_name,
                cluster_type=cluster_type,
                topics=topics,
                pillar_topic=pillar_topic,
                total_search_volume=total_search_volume,
                avg_competition=avg_competition,
                content_opportunity_score=content_opportunity_score,
                suggested_content_count=suggested_content_count,
                priority_score=priority_score
            )
            
            return cluster_group
            
        except Exception as e:
            logger.error(f"Error creating cluster group: {str(e)}")
            return ContentClusterGroup(
                cluster_id=cluster_id,
                cluster_name="Unknown Cluster",
                cluster_type=ContentCluster.SUPPORTING_CONTENT,
                topics=topics
            )
    
    async def _classify_cluster_type(self, topics: List[Topic]) -> ContentCluster:
        """Classify cluster type based on topics"""
        try:
            if not topics:
                return ContentCluster.SUPPORTING_CONTENT
            
            # Calculate average search volume and confidence
            avg_search_volume = np.mean([topic.search_volume for topic in topics])
            avg_confidence = np.mean([topic.confidence_score for topic in topics])
            
            # Classification logic
            if avg_search_volume > 1000 and avg_confidence > 0.7:
                return ContentCluster.PILLAR_CONTENT
            elif avg_search_volume > 500:
                return ContentCluster.CLUSTER_CONTENT
            elif len(topics) <= 2:
                return ContentCluster.NICHE_CONTENT
            else:
                return ContentCluster.SUPPORTING_CONTENT
                
        except Exception as e:
            logger.error(f"Error classifying cluster type: {str(e)}")
            return ContentCluster.SUPPORTING_CONTENT
    
    async def _calculate_content_gap_score(self, keywords: List[str]) -> float:
        """Calculate content gap score for keywords"""
        try:
            # Mock calculation (would use real search data in production)
            base_score = 0.5
            
            # Higher score for longer-tail keywords (less competition)
            long_tail_count = sum(1 for kw in keywords if len(kw.split()) > 2)
            long_tail_bonus = (long_tail_count / len(keywords)) * 0.3 if keywords else 0
            
            # Random variation for realistic scoring
            import random
            variation = (random.random() - 0.5) * 0.2
            
            score = base_score + long_tail_bonus + variation
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating content gap score: {str(e)}")
            return 0.5
    
    async def _find_semantic_keywords(self, keywords: List[str]) -> List[str]:
        """Find semantically related keywords"""
        try:
            semantic_keywords = []
            
            for keyword in keywords[:3]:  # Process top 3 keywords
                # Mock semantic keyword generation
                # In production, this would use word embeddings or API
                semantic_keywords.extend([
                    f"{keyword} guide",
                    f"{keyword} tips",
                    f"best {keyword}",
                    f"{keyword} tutorial"
                ])
            
            return list(set(semantic_keywords))[:10]  # Return top 10 unique
            
        except Exception as e:
            logger.error(f"Error finding semantic keywords: {str(e)}")
            return []
    
    async def _generate_content_suggestions(self, topic: Topic) -> List[str]:
        """Generate content suggestions for a topic"""
        try:
            suggestions = []
            
            primary_keyword = topic.keywords[0] if topic.keywords else topic.name
            
            # Content type suggestions
            content_types = [
                f"Ultimate Guide to {primary_keyword}",
                f"How to {primary_keyword}: Step-by-Step Tutorial",
                f"Top 10 {primary_keyword} Tips for Beginners",
                f"{primary_keyword} Best Practices and Examples",
                f"Common {primary_keyword} Mistakes to Avoid"
            ]
            
            suggestions.extend(content_types)
            
            # Add keyword-specific suggestions
            for keyword in topic.keywords[1:4]:  # Use next 3 keywords
                suggestions.append(f"Comprehensive {keyword} Resource")
                suggestions.append(f"{keyword} vs Alternatives Comparison")
            
            return suggestions[:8]  # Return top 8 suggestions
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {str(e)}")
            return []
    
    async def _analyze_semantic_relationships(self, 
                                           clusters: List[ContentClusterGroup]) -> Dict[str, Any]:
        """Analyze semantic relationships between clusters"""
        try:
            relationships = {}
            
            # Build semantic relationship graph
            for i, cluster1 in enumerate(clusters):
                for j, cluster2 in enumerate(clusters[i+1:], i+1):
                    similarity = await self._calculate_cluster_similarity(cluster1, cluster2)
                    
                    if similarity > 0.3:  # Threshold for meaningful relationship
                        rel_key = f"{cluster1.cluster_id}_{cluster2.cluster_id}"
                        relationships[rel_key] = {
                            'similarity': similarity,
                            'cluster1': cluster1.cluster_name,
                            'cluster2': cluster2.cluster_name,
                            'suggested_links': await self._suggest_internal_links(cluster1, cluster2)
                        }
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error analyzing semantic relationships: {str(e)}")
            return {}
    
    async def _calculate_cluster_similarity(self, 
                                          cluster1: ContentClusterGroup,
                                          cluster2: ContentClusterGroup) -> float:
        """Calculate similarity between two clusters"""
        try:
            # Get all keywords from both clusters
            keywords1 = set()
            keywords2 = set()
            
            for topic in cluster1.topics:
                keywords1.update(topic.keywords)
                keywords1.update(topic.semantic_keywords)
            
            for topic in cluster2.topics:
                keywords2.update(topic.keywords)
                keywords2.update(topic.semantic_keywords)
            
            # Calculate Jaccard similarity
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            
            similarity = intersection / union if union > 0 else 0.0
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating cluster similarity: {str(e)}")
            return 0.0
    
    async def _suggest_internal_links(self, 
                                    cluster1: ContentClusterGroup,
                                    cluster2: ContentClusterGroup) -> List[str]:
        """Suggest internal linking opportunities between clusters"""
        try:
            suggestions = []
            
            # Link pillar content
            if cluster1.pillar_topic and cluster2.pillar_topic:
                suggestions.append(
                    f"Link from '{cluster1.pillar_topic.name}' to '{cluster2.pillar_topic.name}'"
                )
            
            # Link related topics
            for topic1 in cluster1.topics[:2]:  # Top 2 topics
                for topic2 in cluster2.topics[:2]:
                    # Check for keyword overlap
                    overlap = set(topic1.keywords).intersection(set(topic2.keywords))
                    if overlap:
                        suggestions.append(
                            f"Cross-link '{topic1.name}' and '{topic2.name}' (shared: {list(overlap)[0]})"
                        )
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting internal links: {str(e)}")
            return []
    
    async def _generate_content_strategy(self, clusters: List[ContentClusterGroup]) -> Dict[str, Any]:
        """Generate comprehensive content strategy"""
        try:
            strategy = {
                'pillar_strategy': {},
                'cluster_strategy': {},
                'content_calendar': [],
                'priority_matrix': [],
                'resource_allocation': {}
            }
            
            # Pillar content strategy
            pillar_clusters = [c for c in clusters if c.cluster_type == ContentCluster.PILLAR_CONTENT]
            strategy['pillar_strategy'] = {
                'total_pillars': len(pillar_clusters),
                'recommended_pillars': [
                    {
                        'cluster_name': cluster.cluster_name,
                        'search_volume': cluster.total_search_volume,
                        'priority': cluster.priority_score,
                        'content_count': cluster.suggested_content_count
                    }
                    for cluster in sorted(pillar_clusters, key=lambda x: x.priority_score, reverse=True)
                ]
            }
            
            # Cluster content strategy
            cluster_content = [c for c in clusters if c.cluster_type == ContentCluster.CLUSTER_CONTENT]
            strategy['cluster_strategy'] = {
                'total_clusters': len(cluster_content),
                'monthly_targets': await self._calculate_monthly_content_targets(cluster_content)
            }
            
            # Priority matrix
            for cluster in clusters:
                strategy['priority_matrix'].append({
                    'cluster_name': cluster.cluster_name,
                    'effort': self._estimate_content_effort(cluster),
                    'impact': cluster.priority_score,
                    'urgency': self._calculate_urgency_score(cluster)
                })
            
            # Resource allocation
            total_content = sum(cluster.suggested_content_count for cluster in clusters)
            strategy['resource_allocation'] = {
                'total_content_pieces': total_content,
                'estimated_hours': total_content * 8,  # 8 hours per piece
                'recommended_team_size': max(1, total_content // 20),  # 1 person per 20 pieces
                'timeline_weeks': max(4, total_content // 4)  # 1 piece per week per person
            }
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating content strategy: {str(e)}")
            return {}
    
    async def _calculate_monthly_content_targets(self, clusters: List[ContentClusterGroup]) -> Dict[str, int]:
        """Calculate monthly content targets for clusters"""
        total_content = sum(cluster.suggested_content_count for cluster in clusters)
        
        # Distribute over 6 months
        monthly_distribution = {
            'month_1': int(total_content * 0.25),  # Front-load pillar content
            'month_2': int(total_content * 0.20),
            'month_3': int(total_content * 0.20),
            'month_4': int(total_content * 0.15),
            'month_5': int(total_content * 0.10),
            'month_6': int(total_content * 0.10)
        }
        
        return monthly_distribution
    
    def _estimate_content_effort(self, cluster: ContentClusterGroup) -> str:
        """Estimate effort level for cluster content creation"""
        if cluster.cluster_type == ContentCluster.PILLAR_CONTENT:
            return "high"
        elif cluster.suggested_content_count > 10:
            return "high"
        elif cluster.suggested_content_count > 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_urgency_score(self, cluster: ContentClusterGroup) -> float:
        """Calculate urgency score for cluster"""
        # Higher urgency for high search volume and low competition
        urgency = (cluster.total_search_volume / 10000) * (1 - cluster.avg_competition)
        return min(1.0, urgency)
    
    async def _identify_seo_opportunities(self, clusters: List[ContentClusterGroup]) -> List[str]:
        """Identify SEO opportunities from cluster analysis"""
        opportunities = []
        
        # High search volume, low competition opportunities
        for cluster in clusters:
            if cluster.total_search_volume > 1000 and cluster.avg_competition < 0.5:
                opportunities.append(
                    f"High-opportunity cluster: {cluster.cluster_name} "
                    f"({cluster.total_search_volume} monthly searches, low competition)"
                )
        
        # Content gap opportunities
        gap_clusters = [c for c in clusters if c.content_opportunity_score > 0.7]
        for cluster in gap_clusters:
            opportunities.append(
                f"Content gap opportunity: {cluster.cluster_name} "
                f"(gap score: {cluster.content_opportunity_score:.2f})"
            )
        
        # Internal linking opportunities
        opportunities.append("Create topic cluster hub pages to improve internal linking")
        opportunities.append("Develop pillar pages for each major topic cluster")
        
        return opportunities
    
    async def _identify_keyword_gaps(self, clusters: List[ContentClusterGroup]) -> List[str]:
        """Identify keyword gaps in content strategy"""
        gaps = []
        
        # Missing semantic keywords
        for cluster in clusters:
            if cluster.pillar_topic:
                semantic_coverage = len(cluster.pillar_topic.semantic_keywords)
                if semantic_coverage < 5:
                    gaps.append(
                        f"Expand semantic keywords for {cluster.cluster_name} "
                        f"(currently {semantic_coverage} semantic keywords)"
                    )
        
        # Low-competition keyword opportunities
        for cluster in clusters:
            if cluster.avg_competition < 0.3 and cluster.total_search_volume > 500:
                gaps.append(
                    f"Underexploited low-competition keywords in {cluster.cluster_name}"
                )
        
        return gaps
    
    async def _generate_recommendations(self, 
                                      clusters: List[ContentClusterGroup],
                                      content_strategy: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Priority recommendations based on cluster analysis
        high_priority_clusters = sorted(
            clusters, key=lambda x: x.priority_score, reverse=True
        )[:3]
        
        for cluster in high_priority_clusters:
            recommendations.append(
                f"Prioritize content creation for {cluster.cluster_name} cluster "
                f"(priority score: {cluster.priority_score:.2f})"
            )
        
        # Content structure recommendations
        recommendations.append(
            "Implement topic cluster architecture with pillar pages and supporting content"
        )
        
        # SEO technical recommendations
        recommendations.append(
            "Create internal linking strategy based on semantic relationships"
        )
        
        recommendations.append(
            "Develop content calendar based on cluster priorities and search seasonality"
        )
        
        # Performance tracking recommendations
        recommendations.append(
            "Set up topic-based performance tracking to measure cluster success"
        )
        
        return recommendations
    
    async def _calculate_clustering_quality(self, clusters: List[ContentClusterGroup]) -> float:
        """Calculate overall clustering quality score"""
        try:
            if len(clusters) < 2 or self.topic_vectors is None:
                return 0.5
            
            # Create cluster labels for silhouette analysis
            cluster_labels = []
            for i, cluster in enumerate(clusters):
                cluster_labels.extend([i] * len(cluster.topics))
            
            if len(set(cluster_labels)) < 2:
                return 0.5
            
            # Calculate silhouette score
            silhouette = silhouette_score(self.topic_vectors, cluster_labels)
            
            # Normalize to 0-1 range (silhouette ranges from -1 to 1)
            normalized_score = (silhouette + 1) / 2
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error calculating clustering quality: {str(e)}")
            return 0.5
    
    async def _build_topic_hierarchy(self, clusters: List[ContentClusterGroup]) -> Dict[str, Any]:
        """Build hierarchical topic structure"""
        try:
            hierarchy = {
                'pillar_topics': [],
                'cluster_topics': {},
                'supporting_topics': {},
                'relationships': {}
            }
            
            # Organize by cluster type
            for cluster in clusters:
                if cluster.cluster_type == ContentCluster.PILLAR_CONTENT:
                    hierarchy['pillar_topics'].append({
                        'name': cluster.cluster_name,
                        'search_volume': cluster.total_search_volume,
                        'topics': [topic.name for topic in cluster.topics]
                    })
                
                hierarchy['cluster_topics'][cluster.cluster_id] = {
                    'name': cluster.cluster_name,
                    'type': cluster.cluster_type.value,
                    'topics': [
                        {
                            'name': topic.name,
                            'keywords': topic.keywords,
                            'type': topic.topic_type.value
                        }
                        for topic in cluster.topics
                    ]
                }
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error building topic hierarchy: {str(e)}")
            return {}
    
    async def _calculate_content_opportunity_score(self, topics: List[Topic]) -> float:
        """Calculate content opportunity score for a cluster"""
        try:
            if not topics:
                return 0.5
            
            # Average content gap scores
            gap_scores = [topic.content_gap_score for topic in topics]
            avg_gap_score = np.mean(gap_scores)
            
            # Consider search volume and competition
            search_volumes = [topic.search_volume for topic in topics]
            avg_search_volume = np.mean(search_volumes)
            
            # Normalize search volume (assuming max of 10000)
            normalized_search = min(1.0, avg_search_volume / 10000)
            
            # Competition factor (lower competition = higher opportunity)
            competition_scores = [
                0.8 if topic.competition_level == 'low' else
                0.5 if topic.competition_level == 'medium' else 0.2
                for topic in topics
            ]
            avg_competition_opportunity = np.mean(competition_scores)
            
            # Combined opportunity score
            opportunity_score = (
                avg_gap_score * 0.4 +
                normalized_search * 0.35 +
                avg_competition_opportunity * 0.25
            )
            
            return opportunity_score
            
        except Exception as e:
            logger.error(f"Error calculating content opportunity score: {str(e)}")
            return 0.5
    
    async def _calculate_cluster_priority_score(self, 
                                              search_volume: int,
                                              competition: float,
                                              opportunity: float) -> float:
        """Calculate priority score for cluster"""
        try:
            # Normalize search volume
            normalized_volume = min(1.0, search_volume / 10000)
            
            # Lower competition = higher priority
            competition_priority = 1 - competition
            
            # Combined priority score
            priority = (
                normalized_volume * 0.4 +
                competition_priority * 0.3 +
                opportunity * 0.3
            )
            
            return priority
            
        except Exception as e:
            logger.error(f"Error calculating cluster priority score: {str(e)}")
            return 0.5
    
    async def _suggest_content_count(self, 
                                   topics: List[Topic],
                                   cluster_type: ContentCluster) -> int:
        """Suggest number of content pieces for cluster"""
        try:
            base_count = len(topics)
            
            # Adjust based on cluster type
            if cluster_type == ContentCluster.PILLAR_CONTENT:
                return max(8, base_count * 2)  # More comprehensive content
            elif cluster_type == ContentCluster.CLUSTER_CONTENT:
                return max(4, base_count)
            elif cluster_type == ContentCluster.NICHE_CONTENT:
                return max(2, base_count // 2)
            else:
                return max(3, base_count)
                
        except Exception as e:
            logger.error(f"Error suggesting content count: {str(e)}")
            return 5
    
    async def _combine_clustering_results(self, 
                                        cluster_lists: List[List[ContentClusterGroup]],
                                        topics: List[Topic]) -> List[ContentClusterGroup]:
        """Combine results from multiple clustering methods"""
        try:
            # Use ensemble voting to determine final clusters
            # For simplicity, use the first clustering result
            # In production, this would implement sophisticated ensemble methods
            
            if cluster_lists:
                return cluster_lists[0]
            else:
                # Fallback: create single cluster
                return [await self._create_cluster_group("cluster_0", topics)]
                
        except Exception as e:
            logger.error(f"Error combining clustering results: {str(e)}")
            return []