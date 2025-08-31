"""Result Aggregator Implementation
===============================

Advanced result aggregation system for combining and analyzing crawler results.
Implements sophisticated scoring, deduplication, and evidence correlation.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

from .content_detector import DetectionResult, DetectionType
from .platform_crawler import ContentMatch, CrawlerResult


class AggregationMethod(Enum):
    """Methods for aggregating results"""    WEIGHTED_AVERAGE = "weighted_average"
    MAXIMUM_SCORE = "maximum_score"
    CONSENSUS_VOTING = "consensus_voting"
    MACHINE_LEARNING = "machine_learning"


class EvidenceType(Enum):
    """Types of evidence for content matches"""    FINGERPRINT_MATCH = "fingerprint_match"
    METADATA_SIMILARITY = "metadata_similarity"
    VISUAL_SIMILARITY = "visual_similarity"
    AUDIO_SIMILARITY = "audio_similarity"
    TEXT_SIMILARITY = "text_similarity"
    PLATFORM_CROSS_REFERENCE = "platform_cross_reference"
    TEMPORAL_CORRELATION = "temporal_correlation"


@dataclass
class MatchScore:
    """Comprehensive scoring for content matches"""    overall_score: float
    confidence_level: float
    evidence_strength: float
    platform_reliability: float
    temporal_relevance: float
    fingerprint_accuracy: float
    metadata_consistency: float
    cross_platform_validation: float
    false_positive_probability: float
    components: Dict[str, float] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    """Individual piece of evidence for a match"""    evidence_type: EvidenceType
    source_platform: str
    evidence_data: Dict[str, Any]
    confidence_score: float
    timestamp: datetime
    verification_status: str = "pending"  # pending, verified, disputed, false
    correlation_id: Optional[str] = None


@dataclass
class AggregatedResult:
    """Aggregated result from multiple crawler sources"""    result_id: str
    original_content_id: str
    detected_urls: List[str]
    platforms: List[str]
    match_score: MatchScore
    evidence_items: List[EvidenceItem]
    detection_summary: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    geographic_distribution: Dict[str, int]
    recommendation: str  # takedown, monitor, investigate, ignore
    priority_level: str  # critical, high, medium, low
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # active, resolved, disputed, archived


class ResultAggregator:
    """    Advanced result aggregation system for combining and analyzing crawler results.
    
    Features:
    - Multi-platform result correlation
    - Advanced scoring algorithms
    - Evidence collection and verification
    - Temporal analysis and trending
    - Geographic distribution tracking
    - False positive filtering
    - Automated decision recommendations
    - Cross-reference validation
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Aggregation configuration
        self.similarity_threshold = 0.85
        self.evidence_weight_config = {
            EvidenceType.FINGERPRINT_MATCH: 0.35,
            EvidenceType.METADATA_SIMILARITY: 0.20,
            EvidenceType.VISUAL_SIMILARITY: 0.15,
            EvidenceType.AUDIO_SIMILARITY: 0.15,
            EvidenceType.TEXT_SIMILARITY: 0.10,
            EvidenceType.PLATFORM_CROSS_REFERENCE: 0.05
        }
        
        # Platform reliability scores
        self.platform_reliability = {
            'youtube': 0.95,
            'spotify': 0.90,
            'instagram': 0.85,
            'tiktok': 0.80,
            'facebook': 0.75,
            'twitter': 0.70,
            'soundcloud': 0.85,
            'vimeo': 0.90,
            'web': 0.60
        }
        
        # Aggregated results storage
        self.aggregated_results: Dict[str, AggregatedResult] = {}
        self.correlation_cache: Dict[str, List[str]] = {}
        
        # Analytics data
        self.analytics = {
            'total_results': 0,
            'platforms_analyzed': set(),
            'detection_trends': defaultdict(int),
            'processing_times': [],
            'accuracy_metrics': defaultdict(float)
        }
    
    async def aggregate_crawler_results(self, 
                                      crawler_results: List[CrawlerResult],
                                      original_content_id: str) -> AggregatedResult:
        """        Aggregate results from multiple crawler sources.
        
        Args:
            crawler_results: List of crawler results to aggregate
            original_content_id: ID of the original content being monitored
            
        Returns:
            Aggregated result with comprehensive analysis
        """        try:
            start_time = datetime.utcnow()
            
            # Extract all matches from crawler results
            all_matches = []
            platforms = []
            
            for result in crawler_results:
                all_matches.extend(result.matches)
                platforms.append(result.platform)
            
            # Remove duplicates and cluster similar matches
            unique_matches = await self._deduplicate_matches(all_matches)
            clustered_matches = await self._cluster_similar_matches(unique_matches)
            
            # Generate evidence items
            evidence_items = await self._generate_evidence_items(clustered_matches, crawler_results)
            
            # Calculate comprehensive match score
            match_score = await self._calculate_comprehensive_score(
                clustered_matches, evidence_items, platforms
            )
            
            # Analyze temporal patterns
            timeline = await self._analyze_temporal_patterns(crawler_results)
            
            # Analyze geographic distribution
            geo_distribution = await self._analyze_geographic_distribution(clustered_matches)
            
            # Generate detection summary
            detection_summary = await self._generate_detection_summary(
                clustered_matches, evidence_items, platforms
            )
            
            # Generate recommendation and priority
            recommendation = await self._generate_recommendation(match_score, evidence_items)
            priority_level = await self._determine_priority_level(match_score, len(clustered_matches))
            
            # Create aggregated result
            result_id = f"agg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{original_content_id[:8]}"
            
            aggregated_result = AggregatedResult(
                result_id=result_id,
                original_content_id=original_content_id,
                detected_urls=[match.url for match in clustered_matches],
                platforms=list(set(platforms)),
                match_score=match_score,
                evidence_items=evidence_items,
                detection_summary=detection_summary,
                timeline=timeline,
                geographic_distribution=geo_distribution,
                recommendation=recommendation,
                priority_level=priority_level
            )
            
            # Store result
            self.aggregated_results[result_id] = aggregated_result
            
            # Update analytics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_analytics(aggregated_result, processing_time)
            
            self.logger.info(f"Aggregated {len(crawler_results)} crawler results in {processing_time:.2f}s")
            
            return aggregated_result
            
        except Exception as e:
            self.logger.error(f"Error aggregating crawler results: {str(e)}")
            raise
    
    async def correlate_cross_platform_matches(self, 
                                             time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """        Correlate matches across platforms within a time window.
        
        Args:
            time_window_hours: Time window for correlation analysis
            
        Returns:
            List of cross-platform correlations
        """        try:
            correlations = []
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Get recent results
            recent_results = [
                result for result in self.aggregated_results.values()
                if result.created_at >= cutoff_time
            ]
            
            # Group by content fingerprint similarity
            correlation_groups = await self._group_by_similarity(recent_results)
            
            for group in correlation_groups:
                if len(group) > 1:  # Multiple matches found
                    correlation = await self._analyze_correlation_group(group)
                    correlations.append(correlation)
            
            self.logger.info(f"Found {len(correlations)} cross-platform correlations")
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error correlating cross-platform matches: {str(e)}")
            return []
    
    async def analyze_detection_trends(self, 
                                     time_period_days: int = 30) -> Dict[str, Any]:
        """        Analyze detection trends over time period.
        
        Args:
            time_period_days: Number of days to analyze
            
        Returns:
            Trend analysis data
        """        try:
            cutoff_time = datetime.utcnow() - timedelta(days=time_period_days)
            
            # Filter results by time period
            recent_results = [
                result for result in self.aggregated_results.values()
                if result.created_at >= cutoff_time
            ]
            
            # Analyze trends
            trends = {
                'total_detections': len(recent_results),
                'detections_by_platform': defaultdict(int),
                'detections_by_day': defaultdict(int),
                'average_confidence': 0.0,
                'high_confidence_detections': 0,
                'platform_effectiveness': {},
                'detection_patterns': {}
            }
            
            confidence_scores = []
            
            for result in recent_results:
                # Platform distribution
                for platform in result.platforms:
                    trends['detections_by_platform'][platform] += 1
                
                # Daily distribution
                day_key = result.created_at.strftime('%Y-%m-%d')
                trends['detections_by_day'][day_key] += 1
                
                # Confidence analysis
                confidence_scores.append(result.match_score.confidence_level)
                if result.match_score.confidence_level >= 0.8:
                    trends['high_confidence_detections'] += 1
            
            # Calculate averages
            if confidence_scores:
                trends['average_confidence'] = sum(confidence_scores) / len(confidence_scores)
            
            # Platform effectiveness
            for platform, count in trends['detections_by_platform'].items():
                reliability = self.platform_reliability.get(platform, 0.5)
                trends['platform_effectiveness'][platform] = {
                    'detection_count': count,
                    'reliability_score': reliability,
                    'effectiveness_score': count * reliability
                }
            
            # Identify patterns
            trends['detection_patterns'] = await self._identify_detection_patterns(recent_results)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing detection trends: {str(e)}")
            return {}
    
    async def filter_false_positives(self, 
                                   results: List[AggregatedResult],
                                   strict_mode: bool = False) -> List[AggregatedResult]:
        """        Filter out likely false positive results.
        
        Args:
            results: List of aggregated results to filter
            strict_mode: Use stricter filtering criteria
            
        Returns:
            Filtered list of results
        """        try:
            filtered_results = []
            false_positive_threshold = 0.7 if strict_mode else 0.5
            
            for result in results:
                # Calculate false positive probability
                fp_probability = await self._calculate_false_positive_probability(result)
                
                if fp_probability < false_positive_threshold:
                    # Additional validation checks
                    if await self._validate_result_authenticity(result):
                        filtered_results.append(result)
                    else:
                        self.logger.debug(f"Result {result.result_id} failed authenticity validation")
                else:
                    self.logger.debug(f"Result {result.result_id} flagged as likely false positive")
            
            self.logger.info(f"Filtered {len(results) - len(filtered_results)} false positives")
            
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Error filtering false positives: {str(e)}")
            return results
    
    # Private helper methods
    
    async def _deduplicate_matches(self, matches: List[ContentMatch]) -> List[ContentMatch]:
        """Remove duplicate matches based on URL and similarity"""        try:
            seen_urls = set()
            unique_matches = []
            
            # Sort by similarity score descending
            sorted_matches = sorted(matches, key=lambda x: x.similarity_score, reverse=True)
            
            for match in sorted_matches:
                # Normalize URL for comparison
                normalized_url = self._normalize_url(match.url)
                
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    unique_matches.append(match)
            
            return unique_matches
            
        except Exception as e:
            self.logger.error(f"Error deduplicating matches: {str(e)}")
            return matches
    
    async def _cluster_similar_matches(self, matches: List[ContentMatch]) -> List[ContentMatch]:
        """Cluster similar matches to identify related content"""        try:
            if len(matches) < 2:
                return matches
            
            # Create feature vectors for clustering
            features = []
            for match in matches:
                feature_vector = [
                    match.similarity_score,
                    match.view_count / 1000000,  # Normalize view count
                    match.like_count / 10000,    # Normalize like count
                    len(match.title) / 100,      # Title length
                    1 if match.thumbnail_url else 0  # Has thumbnail
                ]
                features.append(feature_vector)
            
            # Perform DBSCAN clustering
            features_array = np.array(features)
            clustering = DBSCAN(eps=0.3, min_samples=2).fit(features_array)
            
            # Group matches by clusters
            clusters = defaultdict(list)
            for i, label in enumerate(clustering.labels_):
                clusters[label].append(matches[i])
            
            # Return representative matches from each cluster
            clustered_matches = []
            for cluster_id, cluster_matches in clusters.items():
                if cluster_id != -1:  # -1 is noise in DBSCAN
                    # Select match with highest similarity score as representative
                    representative = max(cluster_matches, key=lambda x: x.similarity_score)
                    clustered_matches.append(representative)
                else:
                    # Add noise points individually
                    clustered_matches.extend(cluster_matches)
            
            return clustered_matches
            
        except Exception as e:
            self.logger.error(f"Error clustering matches: {str(e)}")
            return matches
    
    async def _generate_evidence_items(self, 
                                     matches: List[ContentMatch],
                                     crawler_results: List[CrawlerResult]) -> List[EvidenceItem]:
        """Generate evidence items from matches and crawler results"""        try:
            evidence_items = []
            
            for match in matches:
                # Fingerprint evidence
                if match.similarity_score >= 0.8:
                    evidence = EvidenceItem(
                        evidence_type=EvidenceType.FINGERPRINT_MATCH,
                        source_platform=match.platform,
                        evidence_data={
                            'similarity_score': match.similarity_score,
                            'match_type': match.match_type.value,
                            'url': match.url
                        },
                        confidence_score=match.similarity_score,
                        timestamp=datetime.utcnow()
                    )
                    evidence_items.append(evidence)
                
                # Metadata evidence
                if match.title or match.author:
                    metadata_confidence = await self._calculate_metadata_confidence(match)
                    evidence = EvidenceItem(
                        evidence_type=EvidenceType.METADATA_SIMILARITY,
                        source_platform=match.platform,
                        evidence_data={
                            'title': match.title,
                            'author': match.author,
                            'upload_date': match.upload_date.isoformat() if match.upload_date else None
                        },
                        confidence_score=metadata_confidence,
                        timestamp=datetime.utcnow()
                    )
                    evidence_items.append(evidence)
                
                # Visual evidence
                if match.thumbnail_url:
                    evidence = EvidenceItem(
                        evidence_type=EvidenceType.VISUAL_SIMILARITY,
                        source_platform=match.platform,
                        evidence_data={
                            'thumbnail_url': match.thumbnail_url,
                            'visual_match_score': 0.7  # Placeholder
                        },
                        confidence_score=0.7,
                        timestamp=datetime.utcnow()
                    )
                    evidence_items.append(evidence)
            
            return evidence_items
            
        except Exception as e:
            self.logger.error(f"Error generating evidence items: {str(e)}")
            return []
    
    async def _calculate_comprehensive_score(self, 
                                           matches: List[ContentMatch],
                                           evidence_items: List[EvidenceItem],
                                           platforms: List[str]) -> MatchScore:
        """Calculate comprehensive match score"""        try:
            if not matches:
                return MatchScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
            
            # Base score from highest similarity match
            base_score = max(match.similarity_score for match in matches)
            
            # Evidence strength
            evidence_strength = sum(evidence.confidence_score for evidence in evidence_items) / len(evidence_items) if evidence_items else 0.0
            
            # Platform reliability
            platform_scores = [self.platform_reliability.get(platform, 0.5) for platform in platforms]
            platform_reliability = sum(platform_scores) / len(platform_scores) if platform_scores else 0.5
            
            # Temporal relevance (newer matches score higher)
            now = datetime.utcnow()
            temporal_scores = []
            for match in matches:
                if match.upload_date:
                    days_old = (now - match.upload_date).days
                    temporal_score = max(0.0, 1.0 - (days_old / 365))  # Decay over a year
                    temporal_scores.append(temporal_score)
            temporal_relevance = sum(temporal_scores) / len(temporal_scores) if temporal_scores else 0.5
            
            # Fingerprint accuracy
            fingerprint_scores = [match.similarity_score for match in matches if match.similarity_score >= 0.7]
            fingerprint_accuracy = sum(fingerprint_scores) / len(fingerprint_scores) if fingerprint_scores else 0.0
            
            # Metadata consistency
            metadata_consistency = await self._calculate_metadata_consistency(matches)
            
            # Cross-platform validation
            cross_platform_validation = min(1.0, len(set(platforms)) / 3.0)  # Up to 3 platforms
            
            # False positive probability
            false_positive_probability = await self._estimate_false_positive_probability(
                matches, evidence_items, platforms
            )
            
            # Overall confidence
            confidence_factors = [
                evidence_strength,
                platform_reliability,
                fingerprint_accuracy,
                metadata_consistency,
                cross_platform_validation
            ]
            confidence_level = sum(confidence_factors) / len(confidence_factors)
            
            # Calculate weighted overall score
            score_components = {
                'base_similarity': base_score * 0.3,
                'evidence_strength': evidence_strength * 0.25,
                'platform_reliability': platform_reliability * 0.2,
                'cross_platform_validation': cross_platform_validation * 0.15,
                'metadata_consistency': metadata_consistency * 0.1
            }
            
            overall_score = sum(score_components.values())
            
            return MatchScore(
                overall_score=overall_score,
                confidence_level=confidence_level,
                evidence_strength=evidence_strength,
                platform_reliability=platform_reliability,
                temporal_relevance=temporal_relevance,
                fingerprint_accuracy=fingerprint_accuracy,
                metadata_consistency=metadata_consistency,
                cross_platform_validation=cross_platform_validation,
                false_positive_probability=false_positive_probability,
                components=score_components
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive score: {str(e)}")
            return MatchScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    
    async def _analyze_temporal_patterns(self, crawler_results: List[CrawlerResult]) -> List[Dict[str, Any]]:
        """Analyze temporal patterns in crawler results"""        try:
            timeline = []
            
            for result in crawler_results:
                timeline_entry = {
                    'timestamp': result.start_time.isoformat(),
                    'platform': result.platform,
                    'matches_found': result.total_matches,
                    'high_confidence_matches': result.high_similarity_matches,
                    'processing_time': result.processing_time
                }
                timeline.append(timeline_entry)
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x['timestamp'])
            
            return timeline
            
        except Exception as e:
            self.logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return []
    
    async def _analyze_geographic_distribution(self, matches: List[ContentMatch]) -> Dict[str, int]:
        """Analyze geographic distribution of matches"""        try:
            # This would analyze location data from matches
            # Placeholder implementation
            geo_distribution = defaultdict(int)
            
            for match in matches:
                # Extract location from metadata if available
                location = match.metadata.get('location', 'unknown')
                geo_distribution[location] += 1
            
            return dict(geo_distribution)
            
        except Exception as e:
            self.logger.error(f"Error analyzing geographic distribution: {str(e)}")
            return {}
    
    async def _generate_detection_summary(self, 
                                        matches: List[ContentMatch],
                                        evidence_items: List[EvidenceItem],
                                        platforms: List[str]) -> Dict[str, Any]:
        """Generate comprehensive detection summary"""        try:
            summary = {
                'total_matches': len(matches),
                'platforms_detected': len(set(platforms)),
                'highest_similarity': max(match.similarity_score for match in matches) if matches else 0.0,
                'average_similarity': sum(match.similarity_score for match in matches) / len(matches) if matches else 0.0,
                'evidence_types': list(set(evidence.evidence_type.value for evidence in evidence_items)),
                'total_evidence_items': len(evidence_items),
                'detection_types': list(set(match.match_type.value for match in matches)),
                'content_distribution': self._analyze_content_distribution(matches)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating detection summary: {str(e)}")
            return {}
    
    async def _generate_recommendation(self, match_score: MatchScore, 
                                     evidence_items: List[EvidenceItem]) -> str:
        """Generate action recommendation based on analysis"""        try:
            overall_score = match_score.overall_score
            confidence = match_score.confidence_level
            evidence_strength = match_score.evidence_strength
            
            # High confidence, high score = takedown recommendation
            if overall_score >= 0.85 and confidence >= 0.8 and evidence_strength >= 0.7:
                return "takedown"
            
            # Medium confidence = investigate further
            elif overall_score >= 0.7 and confidence >= 0.6:
                return "investigate"
            
            # Lower scores but multiple evidence = monitor
            elif overall_score >= 0.5 and len(evidence_items) >= 3:
                return "monitor"
            
            # Low scores = ignore
            else:
                return "ignore"
                
        except Exception as e:
            self.logger.error(f"Error generating recommendation: {str(e)}")
            return "investigate"
    
    async def _determine_priority_level(self, match_score: MatchScore, num_matches: int) -> str:
        """Determine priority level for the detection"""        try:
            score = match_score.overall_score
            confidence = match_score.confidence_level
            
            # Critical: High score, high confidence, multiple matches
            if score >= 0.9 and confidence >= 0.85 and num_matches >= 5:
                return "critical"
            
            # High: Good score and confidence
            elif score >= 0.8 and confidence >= 0.7:
                return "high"
            
            # Medium: Moderate score or confidence
            elif score >= 0.6 or confidence >= 0.6:
                return "medium"
            
            # Low: Everything else
            else:
                return "low"
                
        except Exception as e:
            self.logger.error(f"Error determining priority level: {str(e)}")
            return "medium"
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""        try:
            from urllib.parse import urlparse, parse_qs
            
            parsed = urlparse(url)
            
            # Remove query parameters that don't affect content identity
            query_params = parse_qs(parsed.query)
            relevant_params = {}
            
            # Keep only relevant parameters
            for key, value in query_params.items():
                if key in ['v', 'id', 'video_id', 'track_id', 'post_id']:
                    relevant_params[key] = value
            
            # Reconstruct URL
            query_string = '&'.join(f"{k}={v[0]}" for k, v in relevant_params.items())
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if query_string:
                normalized += f"?{query_string}"
            
            return normalized.lower()
            
        except Exception as e:
            self.logger.error(f"Error normalizing URL: {str(e)}")
            return url.lower()
    
    async def _calculate_metadata_confidence(self, match: ContentMatch) -> float:
        """Calculate confidence score for metadata similarity"""        try:
            confidence_factors = []
            
            # Title presence and length
            if match.title:
                title_score = min(1.0, len(match.title) / 50)  # Longer titles generally better
                confidence_factors.append(title_score)
            
            # Author presence
            if match.author:
                confidence_factors.append(0.8)
            
            # Upload date presence
            if match.upload_date:
                confidence_factors.append(0.6)
            
            # View/engagement metrics
            if match.view_count > 0:
                confidence_factors.append(0.5)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating metadata confidence: {str(e)}")
            return 0.0
    
    async def _calculate_metadata_consistency(self, matches: List[ContentMatch]) -> float:
        """Calculate metadata consistency across matches"""        try:
            if len(matches) <= 1:
                return 1.0
            
            # Check consistency of authors
            authors = [match.author for match in matches if match.author]
            author_consistency = len(set(authors)) / len(authors) if authors else 1.0
            
            # Check consistency of titles (similar titles should be close)
            titles = [match.title for match in matches if match.title]
            title_consistency = 1.0  # Simplified implementation
            
            return (author_consistency + title_consistency) / 2
            
        except Exception as e:
            self.logger.error(f"Error calculating metadata consistency: {str(e)}")
            return 0.5
    
    async def _estimate_false_positive_probability(self, 
                                                 matches: List[ContentMatch],
                                                 evidence_items: List[EvidenceItem],
                                                 platforms: List[str]) -> float:
        """Estimate probability of false positive"""        try:
            # Base false positive rate by platform
            platform_fp_rates = {
                'youtube': 0.05,
                'spotify': 0.03,
                'instagram': 0.10,
                'tiktok': 0.15,
                'facebook': 0.12,
                'twitter': 0.20,
                'web': 0.25
            }
            
            # Calculate weighted false positive rate
            total_weight = 0
            weighted_fp_rate = 0
            
            for platform in platforms:
                reliability = self.platform_reliability.get(platform, 0.5)
                fp_rate = platform_fp_rates.get(platform, 0.15)
                weight = reliability
                
                weighted_fp_rate += fp_rate * weight
                total_weight += weight
            
            base_fp_rate = weighted_fp_rate / total_weight if total_weight > 0 else 0.15
            
            # Adjust based on evidence strength
            evidence_strength = sum(evidence.confidence_score for evidence in evidence_items) / len(evidence_items) if evidence_items else 0.5
            
            # Adjust based on similarity scores
            avg_similarity = sum(match.similarity_score for match in matches) / len(matches) if matches else 0.5
            
            # Lower FP rate with stronger evidence and higher similarity
            adjusted_fp_rate = base_fp_rate * (1.0 - evidence_strength * 0.5) * (1.0 - avg_similarity * 0.3)
            
            return max(0.01, min(0.99, adjusted_fp_rate))
            
        except Exception as e:
            self.logger.error(f"Error estimating false positive probability: {str(e)}")
            return 0.15
    
    def _analyze_content_distribution(self, matches: List[ContentMatch]) -> Dict[str, int]:
        """Analyze distribution of content types in matches"""        try:
            distribution = defaultdict(int)
            
            for match in matches:
                # Categorize by platform
                distribution[match.platform] += 1
                
                # Categorize by content type if available
                if hasattr(match, 'content_type'):
                    distribution[f"type_{match.content_type}"] += 1
            
            return dict(distribution)
            
        except Exception as e:
            self.logger.error(f"Error analyzing content distribution: {str(e)}")
            return {}
    
    def _update_analytics(self, result: AggregatedResult, processing_time: float):
        """Update analytics with new result"""        try:
            self.analytics['total_results'] += 1
            self.analytics['platforms_analyzed'].update(result.platforms)
            self.analytics['processing_times'].append(processing_time)
            
            # Track detection trends
            for platform in result.platforms:
                self.analytics['detection_trends'][platform] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating analytics: {str(e)}")
    
    def get_aggregation_statistics(self) -> Dict[str, Any]:
        """Get aggregation system statistics"""        try:
            stats = {
                'total_aggregated_results': len(self.aggregated_results),
                'total_processed': self.analytics['total_results'],
                'platforms_analyzed': list(self.analytics['platforms_analyzed']),
                'average_processing_time': (
                    sum(self.analytics['processing_times']) / len(self.analytics['processing_times'])
                    if self.analytics['processing_times'] else 0.0
                ),
                'detection_trends': dict(self.analytics['detection_trends']),
                'active_correlations': len(self.correlation_cache)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting aggregation statistics: {str(e)}")
            return {}
