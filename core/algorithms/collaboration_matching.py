"""Collaboration Matching Engine - Intelligent Creator Pairing
==========================================================

Advanced algorithm engine for intelligent creator collaboration matching providing:
- Multi-dimensional Creator Profiling
- Compatibility Analysis & Scoring
- Collaborative Opportunity Detection
- Audience Overlap Analysis
- Content Synergy Assessment
- Revenue Potential Calculation
- Partnership Risk Evaluation
- Real-time Matching Recommendations

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import networkx as nx
from scipy.spatial.distance import euclidean
import json

logger = logging.getLogger(__name__)

@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    creator_id: str
    content_type: List[str]  # ['music', 'video', 'photography', 'blog', 'comedy']
    genre_tags: List[str]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    content_quality_score: float
    collaboration_history: List[Dict[str, Any]]
    availability_calendar: Dict[str, Any]
    revenue_potential: float
    geographic_location: str
    language_preferences: List[str]
    brand_alignment: Dict[str, float]
    expertise_level: str  # 'beginner', 'intermediate', 'advanced', 'expert'

@dataclass
class CollaborationMatch:
    """Collaboration match result"""
    creator_a_id: str
    creator_b_id: str
    compatibility_score: float
    synergy_potential: float
    audience_overlap: float
    revenue_potential: float
    collaboration_type: str
    recommended_projects: List[str]
    risk_factors: List[str]
    success_probability: float

class CollaborationMatchingEngine:
    """
    Industrial-grade collaboration matching engine for creators
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.clustering_model = None
        self.collaboration_graph = nx.Graph()
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.matching_weights = self._initialize_weights()
        
        logger.info("CollaborationMatchingEngine initialized successfully")
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize matching algorithm weights"""
        return {
            'content_synergy': 0.25,
            'audience_overlap': 0.20,
            'engagement_compatibility': 0.15,
            'quality_alignment': 0.15,
            'geographic_proximity': 0.10,
            'availability_match': 0.10,
            'revenue_potential': 0.05
        }
    
    def _update_collaboration_graph(self, profile: CreatorProfile) -> None:
        """Update the collaboration network graph"""
        try:
            # Add creator node to graph
            self.collaboration_graph.add_node(
                profile.creator_id,
                content_type=profile.content_type,
                quality_score=profile.content_quality_score,
                revenue_potential=profile.revenue_potential
            )
            
            # Add edges based on collaboration history
            for collab in profile.collaboration_history:
                partner_id = collab.get('partner_id')
                if partner_id and partner_id in self.collaboration_graph:
                    self.collaboration_graph.add_edge(
                        profile.creator_id,
                        partner_id,
                        weight=collab.get('success_score', 0.5),
                        collaboration_type=collab.get('type', 'unknown')
                    )
                    
        except Exception as e:
            logger.error(f"Failed to update collaboration graph: {e}")
    
    def find_matches(self, creator_id: str, max_matches: int = 10, 
                    min_compatibility: float = 0.6) -> List[CollaborationMatch]:
        """
        Find potential collaboration matches for a creator
        """
        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            source_profile = self.creator_profiles[creator_id]
            matches = []
            
            for candidate_id, candidate_profile in self.creator_profiles.items():
                if candidate_id == creator_id:
                    continue
                
                # Calculate compatibility score
                match = self._calculate_compatibility(source_profile, candidate_profile)
                
                if match.compatibility_score >= min_compatibility:
                    matches.append(match)
            
            # Sort by compatibility score and return top matches
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches[:max_matches]
            
        except Exception as e:
            logger.error(f"Failed to find matches for {creator_id}: {e}")
            return []
    
    def _calculate_compatibility(self, profile_a: CreatorProfile, 
                                profile_b: CreatorProfile) -> CollaborationMatch:
        """Calculate comprehensive compatibility between two creators"""
        try:
            # Content synergy analysis
            content_synergy = self._analyze_content_synergy(profile_a, profile_b)
            
            # Audience overlap analysis
            audience_overlap = self._calculate_audience_overlap(profile_a, profile_b)
            
            # Engagement compatibility
            engagement_compatibility = self._assess_engagement_compatibility(profile_a, profile_b)
            
            # Quality alignment
            quality_alignment = self._assess_quality_alignment(profile_a, profile_b)
            
            # Geographic proximity
            geographic_proximity = self._calculate_geographic_proximity(profile_a, profile_b)
            
            # Availability matching
            availability_match = self._assess_availability_compatibility(profile_a, profile_b)
            
            # Revenue potential
            revenue_potential = self._estimate_collaboration_revenue(profile_a, profile_b)
            
            # Calculate weighted compatibility score
            compatibility_score = (
                content_synergy * self.matching_weights['content_synergy'] +
                audience_overlap * self.matching_weights['audience_overlap'] +
                engagement_compatibility * self.matching_weights['engagement_compatibility'] +
                quality_alignment * self.matching_weights['quality_alignment'] +
                geographic_proximity * self.matching_weights['geographic_proximity'] +
                availability_match * self.matching_weights['availability_match'] +
                revenue_potential * self.matching_weights['revenue_potential']
            )
            
            # Determine collaboration type
            collaboration_type = self._determine_collaboration_type(profile_a, profile_b)
            
            # Generate project recommendations
            recommended_projects = self._generate_project_recommendations(profile_a, profile_b)
            
            # Assess risk factors
            risk_factors = self._assess_risk_factors(profile_a, profile_b)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(
                compatibility_score, profile_a, profile_b
            )
            
            return CollaborationMatch(
                creator_a_id=profile_a.creator_id,
                creator_b_id=profile_b.creator_id,
                compatibility_score=compatibility_score,
                synergy_potential=content_synergy,
                audience_overlap=audience_overlap,
                revenue_potential=revenue_potential,
                collaboration_type=collaboration_type,
                recommended_projects=recommended_projects,
                risk_factors=risk_factors,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {e}")
            return CollaborationMatch(
                creator_a_id=profile_a.creator_id,
                creator_b_id=profile_b.creator_id,
                compatibility_score=0.0,
                synergy_potential=0.0,
                audience_overlap=0.0,
                revenue_potential=0.0,
                collaboration_type='unknown',
                recommended_projects=[],
                risk_factors=['calculation_error'],
                success_probability=0.0
            )
    
    def _analyze_content_synergy(self, profile_a: CreatorProfile, 
                                profile_b: CreatorProfile) -> float:
        """Analyze potential content synergy between creators"""
        try:
            # Content type compatibility matrix
            synergy_matrix = {
                ('music', 'video'): 0.9,
                ('music', 'photography'): 0.7,
                ('video', 'photography'): 0.8,
                ('blog', 'photography'): 0.8,
                ('comedy', 'video'): 0.9,
                ('music', 'comedy'): 0.6,
                ('music', 'music'): 0.95,
                ('video', 'video'): 0.8,
                ('photography', 'photography'): 0.7
            }
            
            max_synergy = 0.0
            
            for content_a in profile_a.content_type:
                for content_b in profile_b.content_type:
                    key = tuple(sorted([content_a, content_b]))
                    synergy = synergy_matrix.get(key, 0.5)
                    max_synergy = max(max_synergy, synergy)
            
            # Genre tag overlap bonus
            common_genres = set(profile_a.genre_tags) & set(profile_b.genre_tags)
            genre_bonus = min(len(common_genres) * 0.1, 0.3)
            
            return min(max_synergy + genre_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Content synergy analysis failed: {e}")
            return 0.5
    
    def _calculate_audience_overlap(self, profile_a: CreatorProfile, 
                                   profile_b: CreatorProfile) -> float:
        """Calculate audience demographic overlap"""
        try:
            demographics_a = profile_a.audience_demographics
            demographics_b = profile_b.audience_demographics
            
            overlap_score = 0.0
            factors = 0
            
            # Age group overlap
            if 'age_distribution' in demographics_a and 'age_distribution' in demographics_b:
                age_overlap = self._calculate_distribution_overlap(
                    demographics_a['age_distribution'],
                    demographics_b['age_distribution']
                )
                overlap_score += age_overlap
                factors += 1
            
            # Gender overlap
            if 'gender_distribution' in demographics_a and 'gender_distribution' in demographics_b:
                gender_overlap = self._calculate_distribution_overlap(
                    demographics_a['gender_distribution'],
                    demographics_b['gender_distribution']
                )
                overlap_score += gender_overlap
                factors += 1
            
            # Geographic overlap
            if 'geographic_distribution' in demographics_a and 'geographic_distribution' in demographics_b:
                geo_overlap = self._calculate_distribution_overlap(
                    demographics_a['geographic_distribution'],
                    demographics_b['geographic_distribution']
                )
                overlap_score += geo_overlap
                factors += 1
            
            # Interest overlap
            if 'interests' in demographics_a and 'interests' in demographics_b:
                interests_a = set(demographics_a['interests'])
                interests_b = set(demographics_b['interests'])
                interest_overlap = len(interests_a & interests_b) / len(interests_a | interests_b)
                overlap_score += interest_overlap
                factors += 1
            
            return overlap_score / factors if factors > 0 else 0.5
            
        except Exception as e:
            logger.error(f"Audience overlap calculation failed: {e}")
            return 0.5
    
    def _calculate_distribution_overlap(self, dist_a: Dict[str, float], 
                                       dist_b: Dict[str, float]) -> float:
        """Calculate overlap between two probability distributions"""
        try:
            all_keys = set(dist_a.keys()) | set(dist_b.keys())
            overlap = 0.0
            
            for key in all_keys:
                prob_a = dist_a.get(key, 0.0)
                prob_b = dist_b.get(key, 0.0)
                overlap += min(prob_a, prob_b)
            
            return overlap
            
        except Exception as e:
            logger.error(f"Distribution overlap calculation failed: {e}")
            return 0.0
    
    def _assess_engagement_compatibility(self, profile_a: CreatorProfile, 
                                        profile_b: CreatorProfile) -> float:
        """Assess engagement rate compatibility"""
        try:
            metrics_a = profile_a.engagement_metrics
            metrics_b = profile_b.engagement_metrics
            
            # Key engagement metrics to compare
            key_metrics = ['like_rate', 'comment_rate', 'share_rate', 'response_rate']
            
            compatibility_scores = []
            
            for metric in key_metrics:
                if metric in metrics_a and metric in metrics_b:
                    # Calculate similarity (1 - normalized difference)
                    value_a = metrics_a[metric]
                    value_b = metrics_b[metric]
                    
                    if value_a + value_b > 0:
                        difference = abs(value_a - value_b) / max(value_a, value_b)
                        similarity = 1 - difference
                        compatibility_scores.append(similarity)
            
            return np.mean(compatibility_scores) if compatibility_scores else 0.5
            
        except Exception as e:
            logger.error(f"Engagement compatibility assessment failed: {e}")
            return 0.5
    
    def _assess_quality_alignment(self, profile_a: CreatorProfile, 
                                 profile_b: CreatorProfile) -> float:
        """Assess content quality alignment"""
        try:
            quality_a = profile_a.content_quality_score
            quality_b = profile_b.content_quality_score
            
            # Quality scores should be relatively close for good collaboration
            quality_difference = abs(quality_a - quality_b)
            
            # Normalize to 0-1 scale (lower difference = higher alignment)
            alignment_score = max(0, 1 - quality_difference)
            
            return alignment_score
            
        except Exception as e:
            logger.error(f"Quality alignment assessment failed: {e}")
            return 0.5
    
    def _calculate_geographic_proximity(self, profile_a: CreatorProfile, 
                                       profile_b: CreatorProfile) -> float:
        """Calculate geographic proximity score"""
        try:
            location_a = profile_a.geographic_location
            location_b = profile_b.geographic_location
            
            # Simplified proximity calculation (in real implementation, use actual coordinates)
            if location_a == location_b:
                return 1.0
            elif location_a.split(',')[0] == location_b.split(',')[0]:  # Same country
                return 0.7
            else:
                return 0.3  # Different countries
                
        except Exception as e:
            logger.error(f"Geographic proximity calculation failed: {e}")
            return 0.5
    
    def _assess_availability_compatibility(self, profile_a: CreatorProfile, 
                                          profile_b: CreatorProfile) -> float:
        """Assess schedule compatibility"""
        try:
            calendar_a = profile_a.availability_calendar
            calendar_b = profile_b.availability_calendar
            
            # Simplified availability matching
            available_slots_a = set(calendar_a.get('available_slots', []))
            available_slots_b = set(calendar_b.get('available_slots', []))
            
            if not available_slots_a or not available_slots_b:
                return 0.5
            
            # Calculate overlap
            common_slots = available_slots_a & available_slots_b
            total_slots = available_slots_a | available_slots_b
            
            return len(common_slots) / len(total_slots) if total_slots else 0.5
            
        except Exception as e:
            logger.error(f"Availability compatibility assessment failed: {e}")
            return 0.5
    
    def _estimate_collaboration_revenue(self, profile_a: CreatorProfile, 
                                       profile_b: CreatorProfile) -> float:
        """Estimate potential revenue from collaboration"""
        try:
            # Simple revenue potential calculation
            revenue_a = profile_a.revenue_potential
            revenue_b = profile_b.revenue_potential
            
            # Collaboration can amplify individual potentials
            synergy_multiplier = 1.2  # 20% boost from collaboration
            combined_potential = (revenue_a + revenue_b) * synergy_multiplier
            
            # Normalize to 0-1 scale (assuming max potential is 100000)
            max_potential = 100000
            normalized_potential = min(combined_potential / max_potential, 1.0)
            
            return normalized_potential
            
        except Exception as e:
            logger.error(f"Revenue estimation failed: {e}")
            return 0.5
    
    def _determine_collaboration_type(self, profile_a: CreatorProfile, 
                                     profile_b: CreatorProfile) -> str:
        """Determine the best collaboration type"""
        try:
            content_types_a = set(profile_a.content_type)
            content_types_b = set(profile_b.content_type)
            
            # Determine collaboration type based on content types
            if 'music' in content_types_a and 'video' in content_types_b:
                return 'music_video'
            elif 'music' in content_types_a and 'music' in content_types_b:
                return 'musical_collaboration'
            elif 'video' in content_types_a and 'video' in content_types_b:
                return 'video_collaboration'
            elif 'photography' in content_types_a or 'photography' in content_types_b:
                return 'visual_content'
            elif 'comedy' in content_types_a or 'comedy' in content_types_b:
                return 'entertainment'
            else:
                return 'cross_format'
                
        except Exception as e:
            logger.error(f"Collaboration type determination failed: {e}")
            return 'general'
    
    def _generate_project_recommendations(self, profile_a: CreatorProfile, 
                                         profile_b: CreatorProfile) -> List[str]:
        """Generate specific project recommendations"""
        try:
            recommendations = []
            
            content_types_a = set(profile_a.content_type)
            content_types_b = set(profile_b.content_type)
            
            # Generate recommendations based on content synergy
            if 'music' in content_types_a and 'video' in content_types_b:
                recommendations.extend([
                    'Music video production',
                    'Live performance recording',
                    'Behind-the-scenes documentary'
                ])
            
            if 'music' in content_types_a and 'music' in content_types_b:
                recommendations.extend([
                    'Duet/collaboration song',
                    'Album collaboration',
                    'Live concert tour'
                ])
            
            if 'photography' in content_types_a or 'photography' in content_types_b:
                recommendations.extend([
                    'Photo shoot collaboration',
                    'Visual storytelling project',
                    'Portfolio cross-promotion'
                ])
            
            if 'blog' in content_types_a or 'blog' in content_types_b:
                recommendations.extend([
                    'Guest blog posts',
                    'Interview series',
                    'Collaborative content series'
                ])
            
            # Add genre-specific recommendations
            common_genres = set(profile_a.genre_tags) & set(profile_b.genre_tags)
            for genre in common_genres:
                recommendations.append(f'{genre.title()} themed collaboration')
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Project recommendation generation failed: {e}")
            return ['General collaboration project']
    
    def _assess_risk_factors(self, profile_a: CreatorProfile, 
                            profile_b: CreatorProfile) -> List[str]:
        """Assess potential collaboration risks"""
        try:
            risk_factors = []
            
            # Quality mismatch risk
            quality_diff = abs(profile_a.content_quality_score - profile_b.content_quality_score)
            if quality_diff > 0.3:
                risk_factors.append('significant_quality_difference')
            
            # Experience level mismatch
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            level_a = experience_levels.index(profile_a.expertise_level)
            level_b = experience_levels.index(profile_b.expertise_level)
            
            if abs(level_a - level_b) > 1:
                risk_factors.append('experience_level_mismatch')
            
            # Geographic distance
            if profile_a.geographic_location != profile_b.geographic_location:
                risk_factors.append('geographic_distance')
            
            # Limited collaboration history
            if len(profile_a.collaboration_history) == 0 or len(profile_b.collaboration_history) == 0:
                risk_factors.append('limited_collaboration_experience')
            
            # Audience overlap too high (competition risk)
            audience_overlap = self._calculate_audience_overlap(profile_a, profile_b)
            if audience_overlap > 0.8:
                risk_factors.append('high_audience_overlap_competition')
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return ['assessment_error']
    
    def _calculate_success_probability(self, compatibility_score: float, 
                                      profile_a: CreatorProfile, 
                                      profile_b: CreatorProfile) -> float:
        """Calculate collaboration success probability"""
        try:
            base_probability = compatibility_score
            
            # Adjust based on collaboration history
            history_a = len(profile_a.collaboration_history)
            history_b = len(profile_b.collaboration_history)
            
            experience_bonus = min((history_a + history_b) * 0.05, 0.2)
            
            # Adjust based on quality scores
            avg_quality = (profile_a.content_quality_score + profile_b.content_quality_score) / 2
            quality_bonus = avg_quality * 0.1
            
            # Calculate final probability
            success_probability = base_probability + experience_bonus + quality_bonus
            
            return min(success_probability, 1.0)
            
        except Exception as e:
            logger.error(f"Success probability calculation failed: {e}")
            return 0.5
    
    def get_collaboration_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive collaboration insights for a creator"""
        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            profile = self.creator_profiles[creator_id]
            
            # Find potential matches
            matches = self.find_matches(creator_id, max_matches=20)
            
            # Analyze collaboration patterns
            collaboration_patterns = self._analyze_collaboration_patterns(profile)
            
            # Generate optimization recommendations
            optimization_tips = self._generate_optimization_recommendations(profile, matches)
            
            return {
                'creator_id': creator_id,
                'total_potential_matches': len(matches),
                'top_matches': matches[:5],
                'collaboration_patterns': collaboration_patterns,
                'optimization_recommendations': optimization_tips,
                'network_centrality': self._calculate_network_centrality(creator_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get collaboration insights: {e}")
            return {}
    
    def _analyze_collaboration_patterns(self, profile: CreatorProfile) -> Dict[str, Any]:
        """Analyze historical collaboration patterns"""
        try:
            history = profile.collaboration_history
            
            if not history:
                return {'pattern': 'no_history'}
            
            # Analyze collaboration frequency
            collaboration_types = [collab.get('type', 'unknown') for collab in history]
            type_distribution = dict(Counter(collaboration_types))
            
            # Analyze success rates
            success_scores = [collab.get('success_score', 0.5) for collab in history]
            avg_success = np.mean(success_scores)
            
            return {
                'total_collaborations': len(history),
                'collaboration_types': type_distribution,
                'average_success_rate': avg_success,
                'most_successful_type': max(type_distribution.items(), key=lambda x: x[1])[0]
            }
            
        except Exception as e:
            logger.error(f"Collaboration pattern analysis failed: {e}")
            return {}
    
    def _generate_optimization_recommendations(self, profile: CreatorProfile, 
                                              matches: List[CollaborationMatch]) -> List[str]:
        """Generate recommendations to improve collaboration potential"""
        try:
            recommendations = []
            
            if not matches:
                recommendations.append("Improve content quality to attract more collaboration opportunities")
                return recommendations
            
            # Analyze match patterns
            avg_compatibility = np.mean([match.compatibility_score for match in matches])
            
            if avg_compatibility < 0.7:
                recommendations.append("Consider diversifying content types to increase collaboration opportunities")
            
            if profile.content_quality_score < 0.7:
                recommendations.append("Focus on improving content quality to attract higher-quality collaborators")
            
            # Analyze audience demographics
            if not profile.audience_demographics:
                recommendations.append("Complete audience demographic analysis to improve matching accuracy")
            
            # Check collaboration history
            if len(profile.collaboration_history) < 3:
                recommendations.append("Build collaboration experience with smaller projects first")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {e}")
            return []
    
    def _calculate_network_centrality(self, creator_id: str) -> float:
        """Calculate creator's centrality in the collaboration network"""
        try:
            if creator_id not in self.collaboration_graph:
                return 0.0
            
            # Calculate betweenness centrality
            centrality = nx.betweenness_centrality(self.collaboration_graph)
            return centrality.get(creator_id, 0.0)
            
        except Exception as e:
            logger.error(f"Network centrality calculation failed: {e}")
            return 0.0
    
    def _update_collaboration_graph(self, profile: CreatorProfile) -> None:
        """Update the collaboration network graph"""
        self.collaboration_graph.add_node(
            profile.creator_id,
            content_type=profile.content_type,
            quality_score=profile.content_quality_score,
            revenue_potential=profile.revenue_potential
        )
    
    def find_collaboration_matches(self, creator_id: str, 
                                 top_k: int = 10) -> List[CollaborationMatch]:
        """Find top collaboration matches for a creator"""
        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            source_profile = self.creator_profiles[creator_id]
            matches = []
            
            for candidate_id, candidate_profile in self.creator_profiles.items():
                if candidate_id == creator_id:
                    continue
                
                match = self._calculate_match_score(source_profile, candidate_profile)
                if match.compatibility_score > 0.3:  # Minimum threshold
                    matches.append(match)
            
            # Sort by compatibility score and return top K
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find matches for {creator_id}: {e}")
            return []
    
    def _calculate_match_score(self, profile_a: CreatorProfile, 
                              profile_b: CreatorProfile) -> CollaborationMatch:
        """Calculate comprehensive match score between two creators"""
        
        # Content synergy calculation
        content_synergy = self._calculate_content_synergy(profile_a, profile_b)
        
        # Audience overlap analysis
        audience_overlap = self._calculate_audience_overlap(profile_a, profile_b)
        
        # Engagement compatibility
        engagement_compat = self._calculate_engagement_compatibility(profile_a, profile_b)
        
        # Quality alignment
        quality_alignment = self._calculate_quality_alignment(profile_a, profile_b)
        
        # Geographic proximity
        geo_proximity = self._calculate_geographic_proximity(profile_a, profile_b)
        
        # Availability match
        availability_match = self._calculate_availability_match(profile_a, profile_b)
        
        # Revenue potential
        revenue_potential = self._calculate_joint_revenue_potential(profile_a, profile_b)
        
        # Weighted compatibility score
        compatibility_score = (
            self.matching_weights['content_synergy'] * content_synergy +
            self.matching_weights['audience_overlap'] * audience_overlap +
            self.matching_weights['engagement_compatibility'] * engagement_compat +
            self.matching_weights['quality_alignment'] * quality_alignment +
            self.matching_weights['geographic_proximity'] * geo_proximity +
            self.matching_weights['availability_match'] * availability_match +
            self.matching_weights['revenue_potential'] * revenue_potential
        )
        
        # Determine collaboration type
        collaboration_type = self._determine_collaboration_type(profile_a, profile_b)
        
        # Generate project recommendations
        recommended_projects = self._generate_project_recommendations(profile_a, profile_b)
        
        # Assess risk factors
        risk_factors = self._assess_risk_factors(profile_a, profile_b)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(
            compatibility_score, profile_a, profile_b
        )
        
        return CollaborationMatch(
            creator_a_id=profile_a.creator_id,
            creator_b_id=profile_b.creator_id,
            compatibility_score=compatibility_score,
            synergy_potential=content_synergy,
            audience_overlap=audience_overlap,
            revenue_potential=revenue_potential,
            collaboration_type=collaboration_type,
            recommended_projects=recommended_projects,
            risk_factors=risk_factors,
            success_probability=success_probability
        )
    
    def _calculate_content_synergy(self, profile_a: CreatorProfile, 
                                  profile_b: CreatorProfile) -> float:
        """Calculate content type synergy score"""
        try:
            # Content type compatibility matrix
            synergy_matrix = {
                ('music', 'video'): 0.9,
                ('music', 'photography'): 0.7,
                ('video', 'photography'): 0.8,
                ('blog', 'photography'): 0.75,
                ('comedy', 'video'): 0.85,
                ('music', 'comedy'): 0.6,
                # Add more combinations as needed
            }
            
            max_synergy = 0.0
            for type_a in profile_a.content_type:
                for type_b in profile_b.content_type:
                    key = tuple(sorted([type_a, type_b]))
                    synergy = synergy_matrix.get(key, 0.3)  # Default synergy
                    max_synergy = max(max_synergy, synergy)
            
            # Genre overlap bonus
            genre_overlap = len(set(profile_a.genre_tags) & set(profile_b.genre_tags))
            genre_bonus = min(genre_overlap * 0.1, 0.2)
            
            return min(max_synergy + genre_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content synergy: {e}")
            return 0.0
    
    def _calculate_audience_overlap(self, profile_a: CreatorProfile, 
                                   profile_b: CreatorProfile) -> float:
        """Calculate audience demographic overlap"""
        try:
            demo_a = profile_a.audience_demographics
            demo_b = profile_b.audience_demographics
            
            # Age group overlap
            age_overlap = self._calculate_demographic_overlap(
                demo_a.get('age_distribution', {}),
                demo_b.get('age_distribution', {})
            )
            
            # Geographic overlap
            geo_overlap = self._calculate_demographic_overlap(
                demo_a.get('geographic_distribution', {}),
                demo_b.get('geographic_distribution', {})
            )
            
            # Interest overlap
            interest_overlap = self._calculate_demographic_overlap(
                demo_a.get('interests', {}),
                demo_b.get('interests', {})
            )
            
            # Weighted average
            return (age_overlap * 0.4 + geo_overlap * 0.3 + interest_overlap * 0.3)
            
        except Exception as e:
            logger.error(f"Error calculating audience overlap: {e}")
            return 0.0
    
    def _calculate_demographic_overlap(self, dist_a: Dict[str, float], 
                                     dist_b: Dict[str, float]) -> float:
        """Calculate overlap between two demographic distributions"""
        if not dist_a or not dist_b:
            return 0.0
        
        overlap = 0.0
        total_keys = set(dist_a.keys()) | set(dist_b.keys())
        
        for key in total_keys:
            val_a = dist_a.get(key, 0.0)
            val_b = dist_b.get(key, 0.0)
            overlap += min(val_a, val_b)
        
        return overlap
    
    def _calculate_engagement_compatibility(self, profile_a: CreatorProfile, 
                                          profile_b: CreatorProfile) -> float:
        """Calculate engagement metrics compatibility"""
        try:
            metrics_a = profile_a.engagement_metrics
            metrics_b = profile_b.engagement_metrics
            
            # Normalize engagement rates
            engagement_ratio = min(
                metrics_a.get('engagement_rate', 0) / max(metrics_b.get('engagement_rate', 0.01), 0.01),
                metrics_b.get('engagement_rate', 0) / max(metrics_a.get('engagement_rate', 0.01), 0.01)
            )
            
            # Follower count compatibility (closer counts = better)
            follower_ratio = min(
                metrics_a.get('follower_count', 0) / max(metrics_b.get('follower_count', 1), 1),
                metrics_b.get('follower_count', 0) / max(metrics_a.get('follower_count', 1), 1)
            )
            
            return (engagement_ratio * 0.6 + follower_ratio * 0.4)
            
        except Exception as e:
            logger.error(f"Error calculating engagement compatibility: {e}")
            return 0.0
    
    def _calculate_quality_alignment(self, profile_a: CreatorProfile, 
                                   profile_b: CreatorProfile) -> float:
        """Calculate content quality alignment"""
        quality_diff = abs(profile_a.content_quality_score - profile_b.content_quality_score)
        return max(0.0, 1.0 - quality_diff)
    
    def _calculate_geographic_proximity(self, profile_a: CreatorProfile, 
                                      profile_b: CreatorProfile) -> float:
        """Calculate geographic proximity score"""
        if profile_a.geographic_location == profile_b.geographic_location:
            return 1.0
        
        # Implement geographic distance calculation
        # For now, return moderate score for different locations
        return 0.5
    
    def _calculate_availability_match(self, profile_a: CreatorProfile, 
                                    profile_b: CreatorProfile) -> float:
        """Calculate availability calendar overlap"""
        # Simplified availability matching
        # In production, implement detailed calendar analysis
        return 0.7
    
    def _calculate_joint_revenue_potential(self, profile_a: CreatorProfile, 
                                         profile_b: CreatorProfile) -> float:
        """Calculate joint revenue potential"""
        individual_avg = (profile_a.revenue_potential + profile_b.revenue_potential) / 2
        synergy_multiplier = 1.3  # Collaboration typically increases revenue
        return min(individual_avg * synergy_multiplier / 100, 1.0)
    
    def _determine_collaboration_type(self, profile_a: CreatorProfile, 
                                    profile_b: CreatorProfile) -> str:
        """Determine the type of collaboration"""
        content_types = set(profile_a.content_type + profile_b.content_type)
        
        if 'music' in content_types and 'video' in content_types:
            return 'music_video_production'
        elif 'photography' in content_types and 'blog' in content_types:
            return 'visual_storytelling'
        elif 'comedy' in content_types:
            return 'entertainment_collaboration'
        else:
            return 'cross_platform_content'
    
    def _generate_project_recommendations(self, profile_a: CreatorProfile, 
                                        profile_b: CreatorProfile) -> List[str]:
        """Generate collaboration project recommendations"""
        projects = []
        content_types = set(profile_a.content_type + profile_b.content_type)
        
        if 'music' in content_types and 'video' in content_types:
            projects.extend(['Music Video', 'Live Performance Recording', 'Behind-the-Scenes Content'])
        
        if 'photography' in content_types:
            projects.extend(['Photo Series', 'Visual Album', 'Brand Photoshoot'])
        
        if 'blog' in content_types:
            projects.extend(['Joint Blog Series', 'Interview Content', 'Tutorial Content'])
        
        return projects[:5]  # Return top 5 recommendations
    
    def _assess_risk_factors(self, profile_a: CreatorProfile, 
                           profile_b: CreatorProfile) -> List[str]:
        """Assess potential collaboration risks"""
        risks = []
        
        # Quality mismatch risk
        quality_diff = abs(profile_a.content_quality_score - profile_b.content_quality_score)
        if quality_diff > 0.3:
            risks.append('Content quality mismatch')
        
        # Experience level mismatch
        levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        level_diff = abs(levels.get(profile_a.expertise_level, 2) - 
                        levels.get(profile_b.expertise_level, 2))
        if level_diff > 1:
            risks.append('Experience level mismatch')
        
        # Brand alignment issues
        brand_score = min(profile_a.brand_alignment.values()) if profile_a.brand_alignment else 0.5
        if brand_score < 0.3:
            risks.append('Brand alignment concerns')
        
        return risks
    
    def _calculate_success_probability(self, compatibility_score: float, 
                                     profile_a: CreatorProfile, 
                                     profile_b: CreatorProfile) -> float:
        """Calculate collaboration success probability"""
        base_probability = compatibility_score
        
        # Boost for previous collaboration success
        collab_history_a = len([c for c in profile_a.collaboration_history 
                               if c.get('success_rating', 0) > 0.7])
        collab_history_b = len([c for c in profile_b.collaboration_history 
                               if c.get('success_rating', 0) > 0.7])
        
        history_boost = min((collab_history_a + collab_history_b) * 0.05, 0.2)
        
        return min(base_probability + history_boost, 1.0)
    
    def get_collaboration_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get collaboration analytics for a creator"""
        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            profile = self.creator_profiles[creator_id]
            matches = self.find_collaboration_matches(creator_id, top_k=50)
            
            analytics = {
                'total_potential_matches': len(matches),
                'high_compatibility_matches': len([m for m in matches if m.compatibility_score > 0.7]),
                'average_compatibility_score': np.mean([m.compatibility_score for m in matches]) if matches else 0,
                'collaboration_types': list(set([m.collaboration_type for m in matches])),
                'revenue_potential': sum([m.revenue_potential for m in matches]),
                'recommended_collaboration_count': len([m for m in matches if m.success_probability > 0.6])
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get analytics for {creator_id}: {e}")
            return {}
    
    def update_collaboration_result(self, creator_a_id: str, creator_b_id: str, 
                                  success_rating: float, feedback: Dict[str, Any]) -> None:
        """Update collaboration history with results"""
        try:
            collaboration_record = {
                'partner_id': creator_b_id,
                'success_rating': success_rating,
                'feedback': feedback,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            if creator_a_id in self.creator_profiles:
                self.creator_profiles[creator_a_id].collaboration_history.append(collaboration_record)
            
            # Add reverse record for partner
            reverse_record = collaboration_record.copy()
            reverse_record['partner_id'] = creator_a_id
            
            if creator_b_id in self.creator_profiles:
                self.creator_profiles[creator_b_id].collaboration_history.append(reverse_record)
            
            logger.info(f"Updated collaboration history for {creator_a_id} and {creator_b_id}")
            
        except Exception as e:
            logger.error(f"Failed to update collaboration result: {e}")
