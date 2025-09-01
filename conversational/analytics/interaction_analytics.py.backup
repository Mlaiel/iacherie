"""Interaction Analytics Engine for IA Influencer Agent Platform
Advanced user interaction tracking, pattern analysis, and behavioral insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use,
copying, distribution, or reproduction is strictly prohibited and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict, Counter
import json
import hashlib
from scipy import stats
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class InteractionType(Enum):
    """Types of user interactions to track."""
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    VOICE_INPUT = "voice_input"
    BUTTON_CLICK = "button_click"
    MENU_NAVIGATION = "menu_navigation"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_VIEW = "content_view"
    CONTENT_SHARE = "content_share"
    SEARCH_QUERY = "search_query"
    FEATURE_ACCESS = "feature_access"
    SETTINGS_CHANGE = "settings_change"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ERROR_ENCOUNTERED = "error_encountered"
    HELP_REQUESTED = "help_requested"


class UserSegment(Enum):
    """User behavior segments."""
    POWER_USER = "power_user"
    CASUAL_USER = "casual_user"
    NEW_USER = "new_user"
    CHURNING_USER = "churning_user"
    ENGAGED_CREATOR = "engaged_creator"
    PASSIVE_CONSUMER = "passive_consumer"
    HEAVY_COLLABORATOR = "heavy_collaborator"
    TECHNICAL_USER = "technical_user"


@dataclass
class InteractionEvent:
    """Individual interaction event data structure."""
    event_id: str
    user_id: str
    session_id: str
    interaction_type: InteractionType
    timestamp: datetime
    duration: float
    context: Dict[str, Any]
    device_info: Dict[str, str]
    location_data: Optional[Dict[str, str]]
    success: bool
    error_details: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserInteractionProfile:
    """Comprehensive user interaction profile."""
    user_id: str
    total_interactions: int
    interaction_frequency: float
    preferred_interaction_types: List[InteractionType]
    session_patterns: Dict[str, Any]
    engagement_score: float
    user_segment: UserSegment
    behavior_patterns: Dict[str, Any]
    usage_trends: Dict[str, Any]
    feature_adoption: Dict[str, float]
    interaction_efficiency: float
    last_updated: datetime


@dataclass
class InteractionFlow:
    """User interaction flow analysis."""
    flow_id: str
    user_id: str
    interaction_sequence: List[InteractionType]
    flow_duration: float
    success_rate: float
    bottlenecks: List[str]
    optimization_opportunities: List[str]
    flow_efficiency_score: float


class InteractionAnalytics:
    """
    Enterprise-grade interaction analytics engine for comprehensive
    user behavior analysis, pattern recognition, and UX optimization.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Analytics caches and stores
        self.interaction_cache = defaultdict(list)
        self.user_profiles = {}
        self.session_data = defaultdict(dict)
        self.interaction_flows = []
        
        # Analysis parameters
        self.analysis_window = timedelta(hours=24)
        self.session_timeout = timedelta(minutes=30)
        self.engagement_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        
        # Interaction weights for scoring
        self.interaction_weights = {
            InteractionType.MESSAGE_SENT: 1.0,
            InteractionType.VOICE_INPUT: 1.2,
            InteractionType.CONTENT_UPLOAD: 2.0,
            InteractionType.CONTENT_SHARE: 1.5,
            InteractionType.FEATURE_ACCESS: 0.8,
            InteractionType.SEARCH_QUERY: 0.6,
            InteractionType.BUTTON_CLICK: 0.3,
            InteractionType.MENU_NAVIGATION: 0.2,
            InteractionType.ERROR_ENCOUNTERED: -0.5,
            InteractionType.HELP_REQUESTED: -0.3
        }
        
        # Behavioral clustering model
        self.behavior_scaler = StandardScaler()
        self.behavior_clusters = None
    
    async def track_interaction(self, interaction_event: InteractionEvent) -> bool:
        """Track a user interaction event."""
        try:
            # Validate interaction event
            if not await self._validate_interaction_event(interaction_event):
                return False
            
            # Store interaction in cache
            self.interaction_cache[interaction_event.user_id].append(interaction_event)
            
            # Update session data
            await self._update_session_data(interaction_event)
            
            # Update user interaction profile
            await self._update_user_profile(interaction_event)
            
            # Analyze interaction patterns in real-time
            await self._analyze_real_time_patterns(interaction_event)
            
            # Persist to database
            await self._persist_interaction_to_db(interaction_event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking interaction: {str(e)}")
            return False
    
    async def analyze_user_behavior_patterns(self, user_id: str, time_period: int = 30) -> Dict[str, Any]:
        """Analyze comprehensive user behavior patterns."""
        try:
            # Get user interactions for the period
            user_interactions = await self._get_user_interactions(user_id, time_period)
            
            if not user_interactions:
                return {'error': 'No interaction data found for user'}
            
            # Analyze interaction patterns
            interaction_patterns = await self._analyze_interaction_patterns(user_interactions)
            
            # Analyze temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(user_interactions)
            
            # Analyze session behavior
            session_analysis = await self._analyze_session_behavior(user_interactions)
            
            # Analyze feature usage
            feature_usage = await self._analyze_feature_usage(user_interactions)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(user_interactions)
            
            # Identify behavior anomalies
            anomalies = await self._identify_behavior_anomalies(user_interactions)
            
            # Generate behavioral insights
            insights = await self._generate_behavioral_insights(
                interaction_patterns, temporal_patterns, session_analysis
            )
            
            return {
                'user_id': user_id,
                'analysis_period_days': time_period,
                'total_interactions': len(user_interactions),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'interaction_patterns': interaction_patterns,
                'temporal_patterns': temporal_patterns,
                'session_analysis': session_analysis,
                'feature_usage': feature_usage,
                'engagement_metrics': engagement_metrics,
                'behavior_anomalies': anomalies,
                'behavioral_insights': insights,
                'user_segment': await self._classify_user_segment(user_interactions),
                'recommendations': await self._generate_user_recommendations(insights)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user behavior patterns: {str(e)}")
            return {}
    
    async def analyze_interaction_flows(self, time_period: int = 7) -> Dict[str, Any]:
        """Analyze user interaction flows and identify optimization opportunities."""
        try:
            # Get interaction data for the period
            interactions = await self._get_interactions_by_period(time_period)
            
            # Group interactions by user sessions
            session_flows = await self._group_interactions_by_session(interactions)
            
            # Analyze common interaction flows
            common_flows = await self._identify_common_flows(session_flows)
            
            # Identify flow bottlenecks
            bottlenecks = await self._identify_flow_bottlenecks(session_flows)
            
            # Calculate flow efficiency metrics
            efficiency_metrics = await self._calculate_flow_efficiency(session_flows)
            
            # Analyze drop-off points
            dropoff_analysis = await self._analyze_dropoff_points(session_flows)
            
            # Generate flow optimization recommendations
            optimizations = await self._generate_flow_optimizations(bottlenecks, dropoff_analysis)
            
            return {
                'analysis_period_days': time_period,
                'total_flows_analyzed': len(session_flows),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'common_flows': common_flows,
                'flow_bottlenecks': bottlenecks,
                'efficiency_metrics': efficiency_metrics,
                'dropoff_analysis': dropoff_analysis,
                'optimization_recommendations': optimizations,
                'flow_success_rates': await self._calculate_flow_success_rates(session_flows),
                'user_journey_insights': await self._analyze_user_journeys(session_flows)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing interaction flows: {str(e)}")
            return {}
    
    async def segment_users_by_behavior(self) -> Dict[str, Any]:
        """Segment users based on behavioral patterns using machine learning."""
        try:
            # Get user behavior data
            users_data = await self._get_all_users_behavior_data()
            
            if len(users_data) < 10:  # Minimum users for meaningful clustering
                return {'error': 'Insufficient user data for segmentation'}
            
            # Prepare features for clustering
            feature_matrix = await self._prepare_clustering_features(users_data)
            
            # Perform behavioral clustering
            clusters = await self._perform_behavioral_clustering(feature_matrix)
            
            # Analyze cluster characteristics
            cluster_analysis = await self._analyze_clusters(clusters, users_data)
            
            # Assign segments to users
            user_segments = await self._assign_user_segments(clusters, users_data)
            
            # Generate segment insights
            segment_insights = await self._generate_segment_insights(cluster_analysis, user_segments)
            
            # Calculate segment metrics
            segment_metrics = await self._calculate_segment_metrics(user_segments, users_data)
            
            return {
                'segmentation_timestamp': datetime.utcnow().isoformat(),
                'total_users_segmented': len(users_data),
                'number_of_segments': len(set(user_segments.values())),
                'user_segments': user_segments,
                'segment_characteristics': cluster_analysis,
                'segment_insights': segment_insights,
                'segment_metrics': segment_metrics,
                'actionable_recommendations': await self._generate_segment_recommendations(segment_insights)
            }
            
        except Exception as e:
            self.logger.error(f"Error segmenting users by behavior: {str(e)}")
            return {}
    
    async def generate_ux_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive UX optimization report based on interaction analytics."""
        try:
            # Analyze interaction efficiency
            efficiency_analysis = await self._analyze_interaction_efficiency()
            
            # Identify UX pain points
            pain_points = await self._identify_ux_pain_points()
            
            # Analyze feature adoption rates
            adoption_analysis = await self._analyze_feature_adoption()
            
            # Study error patterns
            error_analysis = await self._analyze_error_patterns()
            
            # Analyze user onboarding flows
            onboarding_analysis = await self._analyze_onboarding_effectiveness()
            
            # Generate UX improvements
            ux_improvements = await self._generate_ux_improvements(
                efficiency_analysis, pain_points, adoption_analysis
            )
            
            # Prioritize improvements
            improvement_priorities = await self._prioritize_ux_improvements(ux_improvements)
            
            return {
                'report_timestamp': datetime.utcnow().isoformat(),
                'efficiency_analysis': efficiency_analysis,
                'identified_pain_points': pain_points,
                'feature_adoption_analysis': adoption_analysis,
                'error_pattern_analysis': error_analysis,
                'onboarding_effectiveness': onboarding_analysis,
                'recommended_improvements': ux_improvements,
                'improvement_priorities': improvement_priorities,
                'estimated_impact': await self._estimate_improvement_impact(ux_improvements),
                'implementation_roadmap': await self._create_implementation_roadmap(improvement_priorities)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating UX optimization report: {str(e)}")
            return {}
    
    async def analyze_engagement_drivers(self, time_period: int = 30) -> Dict[str, Any]:
        """Analyze factors that drive user engagement."""
        try:
            # Get engagement data
            engagement_data = await self._get_engagement_data(time_period)
            
            # Analyze correlation between interactions and engagement
            interaction_correlations = await self._analyze_interaction_engagement_correlation(engagement_data)
            
            # Identify high-engagement patterns
            high_engagement_patterns = await self._identify_high_engagement_patterns(engagement_data)
            
            # Analyze feature impact on engagement
            feature_impact = await self._analyze_feature_engagement_impact(engagement_data)
            
            # Study timing effects on engagement
            timing_analysis = await self._analyze_engagement_timing_effects(engagement_data)
            
            # Identify engagement triggers
            engagement_triggers = await self._identify_engagement_triggers(engagement_data)
            
            # Generate engagement optimization strategies
            optimization_strategies = await self._generate_engagement_strategies(
                interaction_correlations, high_engagement_patterns, feature_impact
            )
            
            return {
                'analysis_period_days': time_period,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'interaction_engagement_correlations': interaction_correlations,
                'high_engagement_patterns': high_engagement_patterns,
                'feature_engagement_impact': feature_impact,
                'timing_effects': timing_analysis,
                'engagement_triggers': engagement_triggers,
                'optimization_strategies': optimization_strategies,
                'predicted_engagement_impact': await self._predict_strategy_impact(optimization_strategies)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing engagement drivers: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _validate_interaction_event(self, event: InteractionEvent) -> bool:
        """Validate interaction event data."""
        try:
            # Check required fields
            if not all([event.event_id, event.user_id, event.session_id, event.interaction_type]):
                return False
            
            # Validate timestamp
            if event.timestamp > datetime.utcnow() + timedelta(minutes=5):
                return False
            
            # Validate duration
            if event.duration < 0:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating interaction event: {str(e)}")
            return False
    
    async def _update_session_data(self, interaction_event: InteractionEvent):
        """Update session data with new interaction."""
        try:
            session_id = interaction_event.session_id
            
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    'start_time': interaction_event.timestamp,
                    'last_activity': interaction_event.timestamp,
                    'interactions': [],
                    'user_id': interaction_event.user_id
                }
            
            # Update session info
            self.session_data[session_id]['last_activity'] = interaction_event.timestamp
            self.session_data[session_id]['interactions'].append(interaction_event)
            
            # Check for session timeout
            time_since_last = interaction_event.timestamp - self.session_data[session_id]['last_activity']
            if time_since_last > self.session_timeout:
                await self._finalize_session(session_id)
            
        except Exception as e:
            self.logger.error(f"Error updating session data: {str(e)}")
    
    async def _analyze_interaction_patterns(self, interactions: List[InteractionEvent]) -> Dict[str, Any]:
        """Analyze patterns in user interactions."""
        try:
            # Count interaction types
            interaction_counts = Counter([i.interaction_type for i in interactions])
            
            # Analyze interaction sequences
            sequences = []
            for i in range(len(interactions) - 1):
                sequences.append(f"{interactions[i].interaction_type.value} -> {interactions[i+1].interaction_type.value}")
            
            common_sequences = Counter(sequences).most_common(10)
            
            # Calculate interaction efficiency
            successful_interactions = sum(1 for i in interactions if i.success)
            efficiency_rate = successful_interactions / len(interactions) if interactions else 0
            
            # Analyze interaction timing
            interaction_intervals = []
            for i in range(1, len(interactions)):
                interval = (interactions[i].timestamp - interactions[i-1].timestamp).total_seconds()
                interaction_intervals.append(interval)
            
            return {
                'interaction_distribution': dict(interaction_counts),
                'most_common_sequences': common_sequences,
                'efficiency_rate': efficiency_rate,
                'average_interaction_interval': np.mean(interaction_intervals) if interaction_intervals else 0,
                'interaction_velocity': len(interactions) / ((interactions[-1].timestamp - interactions[0].timestamp).total_seconds() / 3600) if len(interactions) > 1 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing interaction patterns: {str(e)}")
            return {}
    
    async def _analyze_temporal_patterns(self, interactions: List[InteractionEvent]) -> Dict[str, Any]:
        """Analyze temporal patterns in user interactions."""
        try:
            # Group interactions by hour of day
            hourly_distribution = defaultdict(int)
            daily_distribution = defaultdict(int)
            
            for interaction in interactions:
                hourly_distribution[interaction.timestamp.hour] += 1
                daily_distribution[interaction.timestamp.weekday()] += 1
            
            # Find peak activity times
            peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 0
            peak_day = max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else 0
            
            # Calculate activity consistency
            hourly_variance = np.var(list(hourly_distribution.values())) if hourly_distribution else 0
            consistency_score = 1 / (1 + hourly_variance / 100)  # Normalize variance
            
            return {
                'hourly_distribution': dict(hourly_distribution),
                'daily_distribution': dict(daily_distribution),
                'peak_activity_hour': peak_hour,
                'peak_activity_day': peak_day,
                'activity_consistency_score': consistency_score,
                'total_active_hours': len(hourly_distribution),
                'total_active_days': len(daily_distribution)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return {}
    
    async def _calculate_engagement_metrics(self, interactions: List[InteractionEvent]) -> Dict[str, float]:
        """Calculate user engagement metrics."""
        try:
            if not interactions:
                return {}
            
            # Calculate weighted engagement score
            engagement_score = 0.0
            for interaction in interactions:
                weight = self.interaction_weights.get(interaction.interaction_type, 0.5)
                engagement_score += weight
            
            # Normalize by time period
            time_span = (interactions[-1].timestamp - interactions[0].timestamp).total_seconds() / 3600
            normalized_engagement = engagement_score / max(time_span, 1)
            
            # Calculate session metrics
            sessions = set(i.session_id for i in interactions)
            avg_session_length = np.mean([
                (max(i.timestamp for i in interactions if i.session_id == session_id) -
                 min(i.timestamp for i in interactions if i.session_id == session_id)).total_seconds()
                for session_id in sessions
            ]) if sessions else 0
            
            return {
                'total_engagement_score': engagement_score,
                'normalized_engagement_score': normalized_engagement,
                'session_count': len(sessions),
                'average_session_length_seconds': avg_session_length,
                'interactions_per_session': len(interactions) / len(sessions) if sessions else 0,
                'engagement_level': self._categorize_engagement_level(normalized_engagement)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement metrics: {str(e)}")
            return {}
    
    def _categorize_engagement_level(self, engagement_score: float) -> str:
        """Categorize engagement level based on score."""
        if engagement_score >= self.engagement_thresholds['high']:
            return "high"
        elif engagement_score >= self.engagement_thresholds['medium']:
            return "medium"
        else:
            return "low"
    
    async def _classify_user_segment(self, interactions: List[InteractionEvent]) -> UserSegment:
        """Classify user into behavioral segment."""
        try:
            if not interactions:
                return UserSegment.NEW_USER
            
            # Calculate key metrics
            total_interactions = len(interactions)
            unique_features = len(set(i.interaction_type for i in interactions))
            time_span_days = (interactions[-1].timestamp - interactions[0].timestamp).days + 1
            daily_avg_interactions = total_interactions / time_span_days
            
            # Content creation indicators
            content_interactions = sum(1 for i in interactions if i.interaction_type in [
                InteractionType.CONTENT_UPLOAD, InteractionType.CONTENT_SHARE
            ])
            
            # Advanced feature usage
            advanced_features = sum(1 for i in interactions if i.interaction_type in [
                InteractionType.VOICE_INPUT, InteractionType.FEATURE_ACCESS
            ])
            
            # Classification logic
            if total_interactions < 10:
                return UserSegment.NEW_USER
            elif daily_avg_interactions > 20 and unique_features > 8:
                return UserSegment.POWER_USER
            elif content_interactions > total_interactions * 0.3:
                return UserSegment.ENGAGED_CREATOR
            elif advanced_features > total_interactions * 0.2:
                return UserSegment.TECHNICAL_USER
            elif daily_avg_interactions < 2:
                return UserSegment.CHURNING_USER
            elif daily_avg_interactions < 5:
                return UserSegment.CASUAL_USER
            else:
                return UserSegment.PASSIVE_CONSUMER
            
        except Exception as e:
            self.logger.error(f"Error classifying user segment: {str(e)}")
            return UserSegment.CASUAL_USER
