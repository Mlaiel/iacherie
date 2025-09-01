"""Advanced Similarity Search Engine for Content Matching and Analysis
==================================================================

High-performance similarity search with content-aware algorithms, ranking,
and specialized detection for content protection and collaboration matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# Local imports
from . import VectorSearchResult
from .embedding_engine import MultiModalEmbeddingEngine

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """
Types of similarity searches."""

    EXACT_MATCH = "exact_match"
    DUPLICATE_DETECTION = "duplicate_detection"
    SIMILAR_CONTENT = "similar_content"
    COLLABORATION_MATCH = "collaboration_match"
    STYLE_SIMILARITY = "style_similarity"
    CONTENT_RECOMMENDATION = "content_recommendation"


class RankingStrategy(Enum):
    """Ranking strategies for search results."""

    SIMILARITY_ONLY = "similarity_only"
    METADATA_BOOST = "metadata_boost"
    TEMPORAL_DECAY = "temporal_decay"
    POPULARITY_BOOST = "popularity_boost"
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    HYBRID_RANKING = "hybrid_ranking"


@dataclass
class SearchConfig:
    """Configuration for similarity searches."""
    search_type: SearchType
    ranking_strategy: RankingStrategy
    similarity_threshold: float = 0.7
    max_results: int = 50
    boost_factors: Dict[str, float] = field(default_factory=dict)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    exclude_ids: Set[str] = field(default_factory=set)
    temporal_weight: float = 0.1
    popularity_weight: float = 0.1


@dataclass
class DuplicateAnalysis:
    """
Analysis results for duplicate content detection."""
    is_duplicate: bool
    confidence_score: float
    similarity_breakdown: Dict[str, float]
    evidence: List[str]
    recommendation: str
    technical_details: Dict[str, Any]


@dataclass
class CollaborationMatch:
    """
Results for collaboration matching."""
    creator_id: str
    compatibility_score: float
    shared_interests: List[str]
    complementary_skills: List[str]
    collaboration_potential: str
    suggested_projects: List[str]
    contact_recommendation: bool


@dataclass
class ContentRecommendation:
    """
Content recommendation result."""
    content_id: str
    recommendation_score: float
    recommendation_type: str
    reasoning: List[str]
    target_audience_match: float
    trend_alignment: float
    monetization_potential: float


class AdvancedSimilarityAnalyzer:
    """
    Advanced analyzer for deep similarity assessment.
    
    Provides content-specific similarity analysis with detailed breakdowns
    and confidence scoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_weights = config.get('content_weights', {
            'audio': {
                'spectral': 0.4,
                'rhythm': 0.3,
                'harmonic': 0.2,
                'metadata': 0.1
            },
            'image': {
                'visual': 0.5,
                'color': 0.2,
                'texture': 0.2,
                'metadata': 0.1
            },
            'text': {
                'semantic': 0.6,
                'linguistic': 0.2,
                'style': 0.1,
                'metadata': 0.1
            },
            'video': {
                'visual': 0.4,
                'temporal': 0.3,
                'audio': 0.2,
                'metadata': 0.1
            }
        })
    
    def analyze_audio_similarity(self, result: VectorSearchResult, 
                               query_metadata: Dict[str, Any]) -> Dict[str, float]:
        """
Analyze audio-specific similarity components."""
        try:
            similarity_breakdown = {}
            
            # Base similarity score
            similarity_breakdown['overall'] = result.similarity_score
            
            # Spectral similarity (estimated from overall score)
            similarity_breakdown['spectral'] = result.similarity_score * 0.9
            
            # Metadata-based similarities
            if 'tempo' in query_metadata and 'tempo' in result.metadata:
                tempo_diff = abs(query_metadata['tempo'] - result.metadata.get('tempo', 0))
                tempo_similarity = max(0, 1 - tempo_diff / 100)  # Normalize by 100 BPM range
                similarity_breakdown['tempo'] = tempo_similarity
            
            if 'genre' in query_metadata and 'genre' in result.metadata:
                genre_match = query_metadata['genre'] == result.metadata.get('genre')
                similarity_breakdown['genre'] = 1.0 if genre_match else 0.0
            
            if 'key' in query_metadata and 'key' in result.metadata:
                key_match = query_metadata['key'] == result.metadata.get('key')
                similarity_breakdown['key'] = 1.0 if key_match else 0.3  # Related keys still similar
            
            # Duration similarity
            if 'duration' in query_metadata and 'duration' in result.metadata:
                duration_ratio = min(query_metadata['duration'], result.metadata.get('duration', 1)) / \
                               max(query_metadata['duration'], result.metadata.get('duration', 1))
                similarity_breakdown['duration'] = duration_ratio
            
            return similarity_breakdown
            
        except Exception as e:
            logger.error(f"Audio similarity analysis failed: {str(e)}")
            return {'overall': result.similarity_score}
    
    def analyze_image_similarity(self, result: VectorSearchResult,
                               query_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze image-specific similarity components."""
        try:
            similarity_breakdown = {}
            
            # Base similarity score
            similarity_breakdown['overall'] = result.similarity_score
            
            # Visual similarity (estimated from overall score)
            similarity_breakdown['visual'] = result.similarity_score * 0.95
            
            # Color similarity (if available)
            if 'dominant_colors' in query_metadata and 'dominant_colors' in result.metadata:
                # Simplified color distance
                similarity_breakdown['color'] = result.similarity_score * 0.8
            
            # Hash-based similarity
            if 'perceptual_hash' in query_metadata and 'perceptual_hash' in result.metadata:
                query_hash = query_metadata['perceptual_hash']
                result_hash = result.metadata.get('perceptual_hash', '')
                
                if query_hash and result_hash:
                    # Hamming distance for perceptual hashes
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(query_hash, result_hash))
                    hash_similarity = max(0, 1 - hamming_dist / len(query_hash))
                    similarity_breakdown['perceptual_hash'] = hash_similarity
            
            # Resolution similarity
            if 'image_size' in query_metadata and 'image_size' in result.metadata:
                query_size = query_metadata['image_size']
                result_size = result.metadata.get('image_size', (1, 1))
                
                query_area = query_size[0] * query_size[1]
                result_area = result_size[0] * result_size[1]
                
                size_ratio = min(query_area, result_area) / max(query_area, result_area)
                similarity_breakdown['resolution'] = size_ratio
            
            return similarity_breakdown
            
        except Exception as e:
            logger.error(f"Image similarity analysis failed: {str(e)}")
            return {'overall': result.similarity_score}
    
    def analyze_text_similarity(self, result: VectorSearchResult,
                              query_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze text-specific similarity components."""
        try:
            similarity_breakdown = {}
            
            # Base similarity score
            similarity_breakdown['overall'] = result.similarity_score
            
            # Semantic similarity (main component)
            similarity_breakdown['semantic'] = result.similarity_score
            
            # Language similarity
            if 'language' in query_metadata and 'language' in result.metadata:
                lang_match = query_metadata['language'] == result.metadata.get('language')
                similarity_breakdown['language'] = 1.0 if lang_match else 0.0
            
            # Length similarity
            if 'length' in query_metadata and 'length' in result.metadata:
                query_len = query_metadata['length']
                result_len = result.metadata.get('length', 1)
                
                length_ratio = min(query_len, result_len) / max(query_len, result_len)
                similarity_breakdown['length'] = length_ratio
            
            # Category similarity
            if 'category' in query_metadata and 'category' in result.metadata:
                category_match = query_metadata['category'] == result.metadata.get('category')
                similarity_breakdown['category'] = 1.0 if category_match else 0.0
            
            return similarity_breakdown
            
        except Exception as e:
            logger.error(f"Text similarity analysis failed: {str(e)}")
            return {'overall': result.similarity_score}
    
    def analyze_video_similarity(self, result: VectorSearchResult,
                               query_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Analyze video-specific similarity components."""
        try:
            similarity_breakdown = {}
            
            # Base similarity score
            similarity_breakdown['overall'] = result.similarity_score
            
            # Visual similarity (main component)
            similarity_breakdown['visual'] = result.similarity_score * 0.9
            
            # Duration similarity
            if 'duration_estimate' in query_metadata and 'duration_estimate' in result.metadata:
                query_duration = query_metadata['duration_estimate']
                result_duration = result.metadata.get('duration_estimate', 1)
                
                duration_ratio = min(query_duration, result_duration) / max(query_duration, result_duration)
                similarity_breakdown['duration'] = duration_ratio
            
            # Motion similarity
            if 'motion_intensity' in query_metadata and 'motion_intensity' in result.metadata:
                query_motion = query_metadata['motion_intensity']
                result_motion = result.metadata.get('motion_intensity', 0)
                
                motion_diff = abs(query_motion - result_motion)
                motion_similarity = max(0, 1 - motion_diff)  # Normalized
                similarity_breakdown['motion'] = motion_similarity
            
            # Scene complexity similarity
            if 'scene_changes' in query_metadata and 'scene_changes' in result.metadata:
                query_scenes = query_metadata['scene_changes']
                result_scenes = result.metadata.get('scene_changes', 0)
                
                scene_ratio = min(query_scenes, result_scenes) / max(query_scenes, result_scenes) if max(query_scenes, result_scenes) > 0 else 1.0
                similarity_breakdown['scene_complexity'] = scene_ratio
            
            return similarity_breakdown
            
        except Exception as e:
            logger.error(f"Video similarity analysis failed: {str(e)}")
            return {'overall': result.similarity_score}


class DuplicateDetectionEngine:
    """
    Specialized engine for detecting duplicate and near-duplicate content.
    
    Uses multiple similarity metrics and heuristics to determine if content
    is a duplicate with high confidence.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analyzer = AdvancedSimilarityAnalyzer(config)
        
        # Thresholds for different content types
        self.duplicate_thresholds = config.get('duplicate_thresholds', {
            'audio': 0.92,
            'image': 0.95,
            'text': 0.88,
            'video': 0.90
        })
        
        # Near-duplicate thresholds
        self.near_duplicate_thresholds = config.get('near_duplicate_thresholds', {
            'audio': 0.85,
            'image': 0.88,
            'text': 0.80,
            'video': 0.83
        })
    
    async def analyze_potential_duplicate(self, result: VectorSearchResult,
                                       content_type: str,
                                       query_metadata: Dict[str, Any]) -> DuplicateAnalysis:
        """
Analyze if a search result is a potential duplicate."""
        try:
            # Get content-specific similarity breakdown
            if content_type == 'audio':
                similarity_breakdown = self.analyzer.analyze_audio_similarity(result, query_metadata)
            elif content_type == 'image':
                similarity_breakdown = self.analyzer.analyze_image_similarity(result, query_metadata)
            elif content_type == 'text':
                similarity_breakdown = self.analyzer.analyze_text_similarity(result, query_metadata)
            elif content_type == 'video':
                similarity_breakdown = self.analyzer.analyze_video_similarity(result, query_metadata)
            else:
                similarity_breakdown = {'overall': result.similarity_score}
            
            # Determine if it's a duplicate
            duplicate_threshold = self.duplicate_thresholds.get(content_type, 0.9)
            near_duplicate_threshold = self.near_duplicate_thresholds.get(content_type, 0.8)
            
            overall_similarity = similarity_breakdown.get('overall', 0)
            
            is_duplicate = overall_similarity >= duplicate_threshold
            is_near_duplicate = overall_similarity >= near_duplicate_threshold
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                similarity_breakdown, content_type, query_metadata, result.metadata
            )
            
            # Generate evidence
            evidence = self._generate_evidence(
                similarity_breakdown, content_type, is_duplicate, is_near_duplicate
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                is_duplicate, is_near_duplicate, confidence_score, content_type
            )
            
            # Technical details
            technical_details = {
                'similarity_score': overall_similarity,
                'duplicate_threshold': duplicate_threshold,
                'near_duplicate_threshold': near_duplicate_threshold,
                'content_type': content_type,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return DuplicateAnalysis(
                is_duplicate=is_duplicate or is_near_duplicate,
                confidence_score=confidence_score,
                similarity_breakdown=similarity_breakdown,
                evidence=evidence,
                recommendation=recommendation,
                technical_details=technical_details
            )
            
        except Exception as e:
            logger.error(f"Duplicate analysis failed: {str(e)}")
            # Return safe default
            return DuplicateAnalysis(
                is_duplicate=False,
                confidence_score=0.0,
                similarity_breakdown={'overall': result.similarity_score},
                evidence=[],
                recommendation="Analysis failed - manual review required",
                technical_details={}
            )
    
    def _calculate_confidence_score(self, similarity_breakdown: Dict[str, float],
                                  content_type: str, query_metadata: Dict[str, Any],
                                  result_metadata: Dict[str, Any]) -> float:
        """Calculate confidence score for duplicate detection."""
        try:
            confidence_factors = []
            
            # Base similarity confidence
            overall_sim = similarity_breakdown.get('overall', 0)
            confidence_factors.append(overall_sim)
            
            # Content-specific factors
            if content_type == 'audio':
                # High tempo similarity increases confidence
                if 'tempo' in similarity_breakdown:
                    confidence_factors.append(similarity_breakdown['tempo'] * 0.8)
                
                # Genre match increases confidence
                if 'genre' in similarity_breakdown:
                    confidence_factors.append(similarity_breakdown['genre'] * 0.6)
                    
            elif content_type == 'image':
                # Perceptual hash match is very strong indicator
                if 'perceptual_hash' in similarity_breakdown:
                    confidence_factors.append(similarity_breakdown['perceptual_hash'] * 1.2)
                    
            elif content_type == 'text':
                # Language match increases confidence
                if 'language' in similarity_breakdown:
                    confidence_factors.append(similarity_breakdown['language'] * 0.7)
                    
            elif content_type == 'video':
                # Duration similarity is important for videos
                if 'duration' in similarity_breakdown:
                    confidence_factors.append(similarity_breakdown['duration'] * 0.9)
            
            # Metadata consistency boost
            metadata_consistency = self._calculate_metadata_consistency(
                query_metadata, result_metadata
            )
            confidence_factors.append(metadata_consistency * 0.5)
            
            # Calculate weighted average
            confidence = np.mean(confidence_factors)
            
            # Cap at 1.0
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {str(e)}")
            return similarity_breakdown.get('overall', 0)
    
    def _calculate_metadata_consistency(self, query_meta: Dict[str, Any],
                                      result_meta: Dict[str, Any]) -> float:
        """Calculate how consistent metadata is between query and result."""
        try:
            if not query_meta or not result_meta:
                return 0.5  # Neutral when no metadata
            
            common_keys = set(query_meta.keys()) & set(result_meta.keys())
            if not common_keys:
                return 0.5  # Neutral when no common metadata
            
            matches = 0
            total = 0
            
            for key in common_keys:
                if key in ['content_id', 'created_at', 'updated_at']:
                    continue  # Skip these keys
                
                total += 1
                query_val = query_meta[key]
                result_val = result_meta[key]
                
                if isinstance(query_val, str) and isinstance(result_val, str):
                    # String comparison
                    if query_val.lower() == result_val.lower():
                        matches += 1
                elif isinstance(query_val, (int, float)) and isinstance(result_val, (int, float)):
                    # Numeric comparison with tolerance
                    relative_diff = abs(query_val - result_val) / max(abs(query_val), abs(result_val), 1)
                    if relative_diff < 0.1:  # 10% tolerance
                        matches += 1
                elif query_val == result_val:
                    # Exact match for other types
                    matches += 1
            
            return matches / total if total > 0 else 0.5
            
        except Exception as e:
            logger.error(f"Metadata consistency calculation failed: {str(e)}")
            return 0.5
    
    def _generate_evidence(self, similarity_breakdown: Dict[str, float],
                         content_type: str, is_duplicate: bool,
                         is_near_duplicate: bool) -> List[str]:
        """Generate human-readable evidence for duplicate detection."""
        evidence = []
        
        overall_sim = similarity_breakdown.get('overall', 0)
        evidence.append(f"Overall similarity: {overall_sim:.3f}")
        
        if content_type == 'audio':
            if 'spectral' in similarity_breakdown:
                evidence.append(f"Spectral similarity: {similarity_breakdown['spectral']:.3f}")
            if 'tempo' in similarity_breakdown:
                evidence.append(f"Tempo similarity: {similarity_breakdown['tempo']:.3f}")
            if 'genre' in similarity_breakdown and similarity_breakdown['genre'] > 0.5:
                evidence.append("Genre match detected")
                
        elif content_type == 'image':
            if 'perceptual_hash' in similarity_breakdown:
                evidence.append(f"Perceptual hash similarity: {similarity_breakdown['perceptual_hash']:.3f}")
            if 'color' in similarity_breakdown:
                evidence.append(f"Color similarity: {similarity_breakdown['color']:.3f}")
                
        elif content_type == 'text':
            if 'semantic' in similarity_breakdown:
                evidence.append(f"Semantic similarity: {similarity_breakdown['semantic']:.3f}")
            if 'language' in similarity_breakdown and similarity_breakdown['language'] > 0.5:
                evidence.append("Language match detected")
                
        elif content_type == 'video':
            if 'visual' in similarity_breakdown:
                evidence.append(f"Visual similarity: {similarity_breakdown['visual']:.3f}")
            if 'duration' in similarity_breakdown:
                evidence.append(f"Duration similarity: {similarity_breakdown['duration']:.3f}")
        
        # Add conclusion evidence
        if is_duplicate:
            evidence.append("HIGH CONFIDENCE: Content is likely a duplicate")
        elif is_near_duplicate:
            evidence.append("MEDIUM CONFIDENCE: Content is likely a near-duplicate or variation")
        else:
            evidence.append("LOW CONFIDENCE: Content similarity below duplicate threshold")
        
        return evidence
    
    def _generate_recommendation(self, is_duplicate: bool, is_near_duplicate: bool,
                               confidence_score: float, content_type: str) -> str:
        """Generate recommendation based on duplicate analysis."""
        if is_duplicate and confidence_score > 0.9:
            return f"TAKE ACTION: High confidence {content_type} duplicate detected. Consider filing DMCA takedown or contact platform."
        elif is_duplicate and confidence_score > 0.7:
            return f"REVIEW REQUIRED: Likely {content_type} duplicate detected. Manual verification recommended before action."
        elif is_near_duplicate and confidence_score > 0.8:
            return f"MONITOR: Potential {content_type} variation detected. Consider monitoring for unauthorized modifications."
        elif is_near_duplicate:
            return f"INVESTIGATE: Similar {content_type} found. May be derivative work or coincidental similarity."
        else:
            return f"NO ACTION: {content_type} similarity below concern threshold. Continue monitoring."


class CollaborationMatchingEngine:
    """
    Engine for finding compatible creators for collaboration opportunities.
    
    Analyzes content style, audience overlap, complementary skills, and
    collaboration potential between creators.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def find_collaboration_matches(self, creator_profile: Dict[str, Any],
                                       potential_matches: List[VectorSearchResult],
                                       content_type: str) -> List[CollaborationMatch]:
        """
Find potential collaboration matches from search results."""
        try:
            matches = []
            
            for result in potential_matches:
                match = await self._analyze_collaboration_potential(
                    creator_profile, result, content_type
                )
                if match and match.compatibility_score > 0.6:  # Minimum threshold
                    matches.append(match)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            return matches[:20]  # Return top 20 matches
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            return []
    
    async def _analyze_collaboration_potential(self, creator_profile: Dict[str, Any],
                                             result: VectorSearchResult,
                                             content_type: str) -> Optional[CollaborationMatch]:
        """Analyze collaboration potential between two creators."""
        try:
            creator_metadata = result.metadata
            
            # Calculate compatibility score
            compatibility_score = await self._calculate_compatibility_score(
                creator_profile, creator_metadata, content_type
            )
            
            # Find shared interests
            shared_interests = self._find_shared_interests(
                creator_profile, creator_metadata
            )
            
            # Find complementary skills
            complementary_skills = self._find_complementary_skills(
                creator_profile, creator_metadata, content_type
            )
            
            # Assess collaboration potential
            collaboration_potential = self._assess_collaboration_potential(
                compatibility_score, shared_interests, complementary_skills
            )
            
            # Generate project suggestions
            suggested_projects = self._suggest_collaboration_projects(
                creator_profile, creator_metadata, content_type
            )
            
            # Determine if contact is recommended
            contact_recommendation = (
                compatibility_score > 0.75 and 
                len(shared_interests) > 2 and 
                len(complementary_skills) > 1
            )
            
            return CollaborationMatch(
                creator_id=result.content_id,
                compatibility_score=compatibility_score,
                shared_interests=shared_interests,
                complementary_skills=complementary_skills,
                collaboration_potential=collaboration_potential,
                suggested_projects=suggested_projects,
                contact_recommendation=contact_recommendation
            )
            
        except Exception as e:
            logger.error(f"Collaboration analysis failed: {str(e)}")
            return None
    
    async def _calculate_compatibility_score(self, profile1: Dict[str, Any],
                                           profile2: Dict[str, Any],
                                           content_type: str) -> float:
        """Calculate compatibility score between two creators."""
        try:
            compatibility_factors = []
            
            # Style similarity (moderate - not too similar, not too different)
            style_similarity = profile2.get('style_score', 0.5)
            optimal_style_similarity = 1.0 - abs(style_similarity - 0.7)  # Optimal around 0.7
            compatibility_factors.append(optimal_style_similarity * 0.3)
            
            # Audience overlap (some overlap is good)
            audience_overlap = self._calculate_audience_overlap(profile1, profile2)
            compatibility_factors.append(audience_overlap * 0.2)
            
            # Complementary skills
            skill_complementarity = self._calculate_skill_complementarity(profile1, profile2)
            compatibility_factors.append(skill_complementarity * 0.3)
            
            # Experience level compatibility
            experience_compatibility = self._calculate_experience_compatibility(profile1, profile2)
            compatibility_factors.append(experience_compatibility * 0.1)
            
            # Collaboration history (if available)
            collab_history_score = profile2.get('collaboration_openness', 0.7)
            compatibility_factors.append(collab_history_score * 0.1)
            
            return np.mean(compatibility_factors)
            
        except Exception as e:
            logger.error(f"Compatibility score calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_audience_overlap(self, profile1: Dict[str, Any],
                                  profile2: Dict[str, Any]) -> float:
        """Calculate audience overlap between creators."""
        try:
            audience1 = set(profile1.get('target_audience', []))
            audience2 = set(profile2.get('target_audience', []))
            
            if not audience1 or not audience2:
                return 0.5  # Neutral when no audience data
            
            overlap = len(audience1 & audience2)
            total_unique = len(audience1 | audience2)
            
            # Some overlap is good, too much might mean competition
            overlap_ratio = overlap / total_unique
            
            # Optimal around 30-50% overlap
            if 0.3 <= overlap_ratio <= 0.5:
                return 1.0
            elif overlap_ratio < 0.3:
                return overlap_ratio / 0.3
            else:
                return max(0, 1.0 - (overlap_ratio - 0.5) / 0.5)
                
        except Exception as e:
            logger.error(f"Audience overlap calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_skill_complementarity(self, profile1: Dict[str, Any],
                                       profile2: Dict[str, Any]) -> float:
        """Calculate how well skills complement each other."""
        try:
            skills1 = set(profile1.get('skills', []))
            skills2 = set(profile2.get('skills', []))
            
            if not skills1 or not skills2:
                return 0.5  # Neutral when no skill data
            
            # Complementary skills are those present in one but not both
            complementary = (skills1 - skills2) | (skills2 - skills1)
            total_skills = skills1 | skills2
            
            if not total_skills:
                return 0.5
            
            complementarity_ratio = len(complementary) / len(total_skills)
            
            # High complementarity is good for collaboration
            return min(complementarity_ratio * 1.5, 1.0)
            
        except Exception as e:
            logger.error(f"Skill complementarity calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_experience_compatibility(self, profile1: Dict[str, Any],
                                          profile2: Dict[str, Any]) -> float:
        """Calculate experience level compatibility."""
        try:
            exp1 = profile1.get('experience_level', 5)  # Scale 1-10
            exp2 = profile2.get('experience_level', 5)
            
            # Moderate difference in experience can be beneficial
            exp_diff = abs(exp1 - exp2)
            
            if exp_diff <= 2:
                return 1.0  # Similar experience levels
            elif exp_diff <= 4:
                return 0.8  # Moderate difference can be good
            else:
                return 0.5  # Large difference might be challenging
                
        except Exception as e:
            logger.error(f"Experience compatibility calculation failed: {str(e)}")
            return 0.7
    
    def _find_shared_interests(self, profile1: Dict[str, Any],
                             profile2: Dict[str, Any]) -> List[str]:
        """Find shared interests between creators."""
        try:
            interests1 = set(profile1.get('interests', []))
            interests2 = set(profile2.get('interests', []))
            
            shared = interests1 & interests2
            return list(shared)
            
        except Exception as e:
            logger.error(f"Shared interests finding failed: {str(e)}")
            return []
    
    def _find_complementary_skills(self, profile1: Dict[str, Any],
                                 profile2: Dict[str, Any],
                                 content_type: str) -> List[str]:
        """Find complementary skills between creators."""
        try:
            skills1 = set(profile1.get('skills', []))
            skills2 = set(profile2.get('skills', []))
            
            # Skills present in one but not the other
            complementary = list((skills1 - skills2) | (skills2 - skills1))
            
            # Filter for relevant complementary skills by content type
            relevant_skills = self._filter_relevant_skills(complementary, content_type)
            
            return relevant_skills
            
        except Exception as e:
            logger.error(f"Complementary skills finding failed: {str(e)}")
            return []
    
    def _filter_relevant_skills(self, skills: List[str], content_type: str) -> List[str]:
        """Filter skills relevant for the content type."""
        relevant_skill_sets = {
            'audio': ['mixing', 'mastering', 'production', 'vocals', 'instruments', 'composition'],
            'video': ['editing', 'cinematography', 'animation', 'directing', 'scripting'],
            'image': ['photography', 'digital_art', 'design', 'retouching', 'illustration'],
            'text': ['writing', 'editing', 'translation', 'copywriting', 'research']
        }
        
        relevant_keywords = relevant_skill_sets.get(content_type, [])
        
        return [skill for skill in skills 
                if any(keyword in skill.lower() for keyword in relevant_keywords)]
    
    def _assess_collaboration_potential(self, compatibility_score: float,
                                      shared_interests: List[str],
                                      complementary_skills: List[str]) -> str:
        """
Assess overall collaboration potential."""
        if compatibility_score > 0.8 and len(shared_interests) > 3 and len(complementary_skills) > 2:
            return "EXCELLENT - Highly recommended collaboration opportunity"
        elif compatibility_score > 0.7 and len(shared_interests) > 2:
            return "GOOD - Strong potential for successful collaboration"
        elif compatibility_score > 0.6:
            return "MODERATE - Worth exploring collaboration possibilities"
        else:
            return "LIMITED - Low compatibility for collaboration"
    
    def _suggest_collaboration_projects(self, profile1: Dict[str, Any],
                                      profile2: Dict[str, Any],
                                      content_type: str) -> List[str]:
        """Suggest specific collaboration projects."""
        try:
            suggestions = []
            
            # Base suggestions by content type
            if content_type == 'audio':
                suggestions = [
                    "Co-produce a track combining both styles",
                    "Create a remix of each other's work",
                    "Collaborate on a concept album",
                    "Cross-promote on respective platforms"
                ]
            elif content_type == 'video':
                suggestions = [
                    "Create a collaborative video series",
                    "Cross-feature in each other's content",
                    "Joint live streaming sessions",
                    "Behind-the-scenes collaboration content"
                ]
            elif content_type == 'image':
                suggestions = [
                    "Joint photography project or exhibition",
                    "Style fusion artwork",
                    "Teaching collaboration tutorials",
                    "Cross-platform content sharing"
                ]
            elif content_type == 'text':
                suggestions = [
                    "Co-author articles or stories",
                    "Guest posting exchange",
                    "Joint newsletter or publication",
                    "Collaborative research project"
                ]
            
            # Add interest-based suggestions
            shared_interests = self._find_shared_interests(profile1, profile2)
            for interest in shared_interests[:3]:  # Top 3 shared interests
                suggestions.append(f"Collaborate on {interest}-themed content")
            
            return suggestions[:6]  # Return top 6 suggestions
            
        except Exception as e:
            logger.error(f"Project suggestion failed: {str(e)}")
            return ["Explore general collaboration opportunities"]


class ContentRecommendationEngine:
    """
    Engine for generating content recommendations based on similarity,
    trends, and audience preferences.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.trend_weight = config.get('trend_weight', 0.3)
        self.audience_weight = config.get('audience_weight', 0.4)
        self.similarity_weight = config.get('similarity_weight', 0.3)
    
    async def generate_recommendations(self, user_profile: Dict[str, Any],
                                     similar_content: List[VectorSearchResult],
                                     content_type: str) -> List[ContentRecommendation]:
        """
Generate content recommendations."""
        try:
            recommendations = []
            
            for result in similar_content:
                recommendation = await self._analyze_recommendation_potential(
                    user_profile, result, content_type
                )
                if recommendation and recommendation.recommendation_score > 0.5:
                    recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            
            return recommendations[:15]  # Return top 15 recommendations
            
        except Exception as e:
            logger.error(f"Content recommendation failed: {str(e)}")
            return []
    
    async def _analyze_recommendation_potential(self, user_profile: Dict[str, Any],
                                              result: VectorSearchResult,
                                              content_type: str) -> Optional[ContentRecommendation]:
        """Analyze recommendation potential for a content item."""
        try:
            # Calculate different scoring components
            similarity_score = result.similarity_score
            
            audience_match = self._calculate_audience_match(
                user_profile, result.metadata
            )
            
            trend_alignment = self._calculate_trend_alignment(
                result.metadata, content_type
            )
            
            monetization_potential = self._calculate_monetization_potential(
                result.metadata, content_type
            )
            
            # Combined recommendation score
            recommendation_score = (
                similarity_score * self.similarity_weight +
                audience_match * self.audience_weight +
                trend_alignment * self.trend_weight
            )
            
            # Determine recommendation type
            recommendation_type = self._determine_recommendation_type(
                similarity_score, audience_match, trend_alignment
            )
            
            # Generate reasoning
            reasoning = self._generate_recommendation_reasoning(
                similarity_score, audience_match, trend_alignment, recommendation_type
            )
            
            return ContentRecommendation(
                content_id=result.content_id,
                recommendation_score=recommendation_score,
                recommendation_type=recommendation_type,
                reasoning=reasoning,
                target_audience_match=audience_match,
                trend_alignment=trend_alignment,
                monetization_potential=monetization_potential
            )
            
        except Exception as e:
            logger.error(f"Recommendation analysis failed: {str(e)}")
            return None
    
    def _calculate_audience_match(self, user_profile: Dict[str, Any],
                                content_metadata: Dict[str, Any]) -> float:
        """Calculate how well content matches user's target audience."""
        try:
            user_audience = set(user_profile.get('target_audience', []))
            content_audience = set(content_metadata.get('target_audience', []))
            
            if not user_audience or not content_audience:
                return 0.5  # Neutral when no audience data
            
            overlap = len(user_audience & content_audience)
            total = len(user_audience | content_audience)
            
            return overlap / total if total > 0 else 0.5
            
        except Exception as e:
            logger.error(f"Audience match calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_trend_alignment(self, content_metadata: Dict[str, Any],
                                 content_type: str) -> float:
        """Calculate how well content aligns with current trends."""
        try:
            # Simplified trend calculation
            # In production, this would connect to trend analysis services
            
            trend_score = 0.5  # Base score
            
            # Recent content gets trend boost
            created_at = content_metadata.get('created_at')
            if created_at:
                # Simple recency boost
                try:
                    creation_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_old = (datetime.now() - creation_date).days
                    
                    if days_old < 30:
                        trend_score += 0.3
                    elif days_old < 90:
                        trend_score += 0.1
                except:
                    pass
            
            # Engagement metrics boost
            views = content_metadata.get('view_count', 0)
            likes = content_metadata.get('like_count', 0)
            
            if views > 10000:
                trend_score += 0.2
            if likes > 500:
                trend_score += 0.1
            
            return min(trend_score, 1.0)
            
        except Exception as e:
            logger.error(f"Trend alignment calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_monetization_potential(self, content_metadata: Dict[str, Any],
                                        content_type: str) -> float:
        """Calculate monetization potential of the content."""
        try:
            monetization_score = 0.5  # Base score
            
            # Quality indicators
            if content_metadata.get('quality_score', 0) > 0.8:
                monetization_score += 0.2
            
            # Engagement metrics
            engagement_rate = content_metadata.get('engagement_rate', 0)
            if engagement_rate > 0.05:  # 5% engagement rate
                monetization_score += 0.3
            
            # Content type specific factors
            if content_type == 'audio':
                # Music has high monetization potential
                monetization_score += 0.1
            elif content_type == 'video':
                # Videos have good monetization on multiple platforms
                monetization_score += 0.2
            
            return min(monetization_score, 1.0)
            
        except Exception as e:
            logger.error(f"Monetization potential calculation failed: {str(e)}")
            return 0.5
    
    def _determine_recommendation_type(self, similarity_score: float,
                                     audience_match: float,
                                     trend_alignment: float) -> str:
        """Determine the type of recommendation."""
        if similarity_score > 0.8:
            return "STYLE_INSPIRATION"
        elif audience_match > 0.8:
            return "TARGET_AUDIENCE_FIT" 
        elif trend_alignment > 0.8:
            return "TRENDING_OPPORTUNITY"
        elif similarity_score > 0.6 and audience_match > 0.6:
            return "STRATEGIC_REFERENCE"
        else:
            return "GENERAL_INSPIRATION"
    
    def _generate_recommendation_reasoning(self, similarity_score: float,
                                         audience_match: float,
                                         trend_alignment: float,
                                         recommendation_type: str) -> List[str]:
        """Generate human-readable reasoning for the recommendation."""
        reasoning = []
        
        if similarity_score > 0.7:
            reasoning.append(f"High style similarity ({similarity_score:.2f}) - good reference for your content direction")
        
        if audience_match > 0.7:
            reasoning.append(f"Strong audience overlap ({audience_match:.2f}) - targets similar demographics")
        
        if trend_alignment > 0.7:
            reasoning.append(f"High trend alignment ({trend_alignment:.2f}) - riding current trends")
        
        # Type-specific reasoning
        if recommendation_type == "STYLE_INSPIRATION":
            reasoning.append("Excellent style reference for developing your unique approach")
        elif recommendation_type == "TARGET_AUDIENCE_FIT":
            reasoning.append("Perfect match for your target audience preferences")
        elif recommendation_type == "TRENDING_OPPORTUNITY":
            reasoning.append("Capitalize on current trend momentum")
        
        if not reasoning:
            reasoning.append("General inspiration for creative development")
        
        return reasoning


class SimilaritySearchEngine:
    """
    Main similarity search engine that coordinates all search capabilities.
    
    Provides unified interface for different types of similarity searches
    with advanced ranking and filtering.
    """
    
    def __init__(self, vector_db_manager, config: Dict[str, Any]):
        self.vector_db = vector_db_manager
        self.config = config
        
        # Initialize specialized engines
        self.duplicate_engine = DuplicateDetectionEngine(config)
        self.collaboration_engine = CollaborationMatchingEngine(config)
        self.recommendation_engine = ContentRecommendationEngine(config)
        self.analyzer = AdvancedSimilarityAnalyzer(config)
        
        logger.info("Similarity search engine initialized")
    
    async def search(self, content_type: str, query_embedding: np.ndarray,
                    search_config: SearchConfig,
                    query_metadata: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Perform similarity search with advanced ranking and filtering.
        
        Args:
            content_type: Type of content to search
            query_embedding: Query vector
            search_config: Search configuration
            query_metadata: Additional query metadata
            
        Returns:
            Ranked and filtered search results
        """
        try:
            query_metadata = query_metadata or {}
            
            # Perform base similarity search
            base_results = await self.vector_db.search_similar_content(
                content_type, 
                query_embedding,
                k=search_config.max_results * 2,  # Get more to filter
                threshold=search_config.similarity_threshold
            )
            
            # Filter results
            filtered_results = self._apply_filters(base_results, search_config)
            
            # Apply ranking strategy
            ranked_results = await self._apply_ranking(
                filtered_results, search_config, query_metadata
            )
            
            # Limit to max results
            final_results = ranked_results[:search_config.max_results]
            
            logger.info(f"Similarity search completed: {len(final_results)} results for {content_type}")
            return final_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    async def find_duplicates(self, content_type: str, query_embedding: np.ndarray,
                            query_metadata: Dict[str, Any]) -> List[Tuple[VectorSearchResult, DuplicateAnalysis]]:
        """Find potential duplicates with detailed analysis."""
        try:
            # Use high similarity threshold for duplicate detection
            search_config = SearchConfig(
                search_type=SearchType.DUPLICATE_DETECTION,
                ranking_strategy=RankingStrategy.SIMILARITY_ONLY,
                similarity_threshold=0.75,  # Lower threshold to catch more potential duplicates
                max_results=50
            )
            
            results = await self.search(content_type, query_embedding, search_config, query_metadata)
            
            # Analyze each result for duplicate potential
            duplicate_analyses = []
            for result in results:
                analysis = await self.duplicate_engine.analyze_potential_duplicate(
                    result, content_type, query_metadata
                )
                if analysis.is_duplicate:
                    duplicate_analyses.append((result, analysis))
            
            # Sort by confidence score
            duplicate_analyses.sort(key=lambda x: x[1].confidence_score, reverse=True)
            
            logger.info(f"Found {len(duplicate_analyses)} potential duplicates for {content_type}")
            return duplicate_analyses
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            return []
    
    async def find_collaboration_opportunities(self, creator_profile: Dict[str, Any],
                                             content_type: str,
                                             query_embedding: np.ndarray) -> List[CollaborationMatch]:
        """Find collaboration opportunities with other creators."""
        try:
            search_config = SearchConfig(
                search_type=SearchType.COLLABORATION_MATCH,
                ranking_strategy=RankingStrategy.COLLABORATIVE_FILTERING,
                similarity_threshold=0.5,  # Lower threshold for collaboration
                max_results=100
            )
            
            results = await self.search(content_type, query_embedding, search_config)
            
            # Find collaboration matches
            matches = await self.collaboration_engine.find_collaboration_matches(
                creator_profile, results, content_type
            )
            
            logger.info(f"Found {len(matches)} collaboration opportunities for {content_type}")
            return matches
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            return []
    
    async def get_content_recommendations(self, user_profile: Dict[str, Any],
                                        content_type: str,
                                        query_embedding: np.ndarray) -> List[ContentRecommendation]:
        """Get content recommendations for inspiration and strategy."""
        try:
            search_config = SearchConfig(
                search_type=SearchType.CONTENT_RECOMMENDATION,
                ranking_strategy=RankingStrategy.HYBRID_RANKING,
                similarity_threshold=0.4,  # Lower threshold for recommendations
                max_results=80
            )
            
            results = await self.search(content_type, query_embedding, search_config)
            
            # Generate recommendations
            recommendations = await self.recommendation_engine.generate_recommendations(
                user_profile, results, content_type
            )
            
            logger.info(f"Generated {len(recommendations)} content recommendations for {content_type}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Content recommendation failed: {str(e)}")
            return []
    
    def _apply_filters(self, results: List[VectorSearchResult],
                      config: SearchConfig) -> List[VectorSearchResult]:
        """Apply filters to search results."""
        try:
            filtered_results = []
            
            for result in results:
                # Exclude specified IDs
                if result.content_id in config.exclude_ids:
                    continue
                
                # Apply metadata filters
                if config.metadata_filters:
                    if not self._matches_metadata_filters(result.metadata, config.metadata_filters):
                        continue
                
                filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Filter application failed: {str(e)}")
            return results
    
    def _matches_metadata_filters(self, metadata: Dict[str, Any],
                                filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the specified filters."""
        try:
            for key, expected_value in filters.items():
                if key not in metadata:
                    return False
                
                actual_value = metadata[key]
                
                if isinstance(expected_value, list):
                    # Check if actual value is in the list
                    if actual_value not in expected_value:
                        return False
                elif isinstance(expected_value, dict):
                    # Range filter: {'min': value, 'max': value}
                    if 'min' in expected_value and actual_value < expected_value['min']:
                        return False
                    if 'max' in expected_value and actual_value > expected_value['max']:
                        return False
                else:
                    # Exact match
                    if actual_value != expected_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Metadata filter matching failed: {str(e)}")
            return True  # Default to include when filter fails
    
    async def _apply_ranking(self, results: List[VectorSearchResult],
                           config: SearchConfig,
                           query_metadata: Dict[str, Any]) -> List[VectorSearchResult]:
        """Apply ranking strategy to search results."""
        try:
            if config.ranking_strategy == RankingStrategy.SIMILARITY_ONLY:
                # Already sorted by similarity
                return results
            
            elif config.ranking_strategy == RankingStrategy.METADATA_BOOST:
                return await self._apply_metadata_boost_ranking(results, config, query_metadata)
            
            elif config.ranking_strategy == RankingStrategy.TEMPORAL_DECAY:
                return self._apply_temporal_decay_ranking(results, config)
            
            elif config.ranking_strategy == RankingStrategy.POPULARITY_BOOST:
                return self._apply_popularity_boost_ranking(results, config)
            
            elif config.ranking_strategy == RankingStrategy.HYBRID_RANKING:
                return await self._apply_hybrid_ranking(results, config, query_metadata)
            
            else:
                return results
            
        except Exception as e:
            logger.error(f"Ranking application failed: {str(e)}")
            return results
    
    async def _apply_metadata_boost_ranking(self, results: List[VectorSearchResult],
                                          config: SearchConfig,
                                          query_metadata: Dict[str, Any]) -> List[VectorSearchResult]:
        """Apply metadata-based ranking boosts."""
        try:
            for result in results:
                boost_score = 0.0
                
                # Apply configured boost factors
                for boost_key, boost_factor in config.boost_factors.items():
                    if (boost_key in query_metadata and 
                        boost_key in result.metadata and
                        query_metadata[boost_key] == result.metadata[boost_key]):
                        boost_score += boost_factor
                
                # Update similarity score with boost
                result.similarity_score = min(1.0, result.similarity_score + boost_score)
            
            # Re-sort by updated scores
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Metadata boost ranking failed: {str(e)}")
            return results
    
    def _apply_temporal_decay_ranking(self, results: List[VectorSearchResult],
                                    config: SearchConfig) -> List[VectorSearchResult]:
        """Apply temporal decay to prioritize recent content."""
        try:
            current_time = datetime.now()
            
            for result in results:
                created_at = result.metadata.get('created_at')
                if created_at:
                    try:
                        creation_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_old = (current_time - creation_date).days
                        
                        # Apply exponential decay
                        decay_factor = math.exp(-days_old / 30.0)  # 30-day half-life
                        temporal_score = result.similarity_score * (1 + config.temporal_weight * decay_factor)
                        
                        result.similarity_score = min(1.0, temporal_score)
                    except:
                        pass  # Keep original score if date parsing fails
            
            # Re-sort by updated scores
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Temporal decay ranking failed: {str(e)}")
            return results
    
    def _apply_popularity_boost_ranking(self, results: List[VectorSearchResult],
                                      config: SearchConfig) -> List[VectorSearchResult]:
        """Apply popularity-based ranking boost."""
        try:
            for result in results:
                popularity_score = 0.0
                
                # Views boost
                views = result.metadata.get('view_count', 0)
                if views > 0:
                    popularity_score += math.log10(views + 1) / 6.0  # Normalize by log scale
                
                # Likes boost
                likes = result.metadata.get('like_count', 0)
                if likes > 0:
                    popularity_score += math.log10(likes + 1) / 4.0
                
                # Engagement rate boost
                engagement_rate = result.metadata.get('engagement_rate', 0)
                popularity_score += engagement_rate * 2.0
                
                # Apply popularity weight
                boosted_score = result.similarity_score + config.popularity_weight * popularity_score
                result.similarity_score = min(1.0, boosted_score)
            
            # Re-sort by updated scores
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Popularity boost ranking failed: {str(e)}")
            return results
    
    async def _apply_hybrid_ranking(self, results: List[VectorSearchResult],
                                  config: SearchConfig,
                                  query_metadata: Dict[str, Any]) -> List[VectorSearchResult]:
        """Apply hybrid ranking combining multiple strategies."""
        try:
            # Apply metadata boost
            results = await self._apply_metadata_boost_ranking(results, config, query_metadata)
            
            # Apply temporal decay
            results = self._apply_temporal_decay_ranking(results, config)
            
            # Apply popularity boost
            results = self._apply_popularity_boost_ranking(results, config)
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid ranking failed: {str(e)}")
            return results


# Export classes
__all__ = [
    'SimilaritySearchEngine',
    'AdvancedSimilarityAnalyzer',
    'DuplicateDetectionEngine',
    'CollaborationMatchingEngine',
    'ContentRecommendationEngine',
    'SearchConfig',
    'SearchType',
    'RankingStrategy',
    'DuplicateAnalysis',
    'CollaborationMatch',
    'ContentRecommendation'
]
