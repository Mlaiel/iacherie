"""
Enterprise Analytics Processor for IA Influencer Platform

Advanced analytics system providing comprehensive data processing,
trend analysis, and performance insights for recommendation systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import redis
import json

from .models import (
    InteractionEvent, ContentItem, UserProfile, CreatorProfile,
    TrendData, RevenueMetrics, InteractionType, ContentType
)


class AnalyticsProcessor:
    """
    Enterprise-grade analytics processor providing comprehensive
    data analysis, trend detection, and performance optimization insights.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        config: Dict[str, Any]
    ):
        self.redis_client = redis_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Analytics configuration
        self.analytics_config = {
            'trending_velocity_threshold': 0.15,
            'significance_threshold': 0.8,
            'clustering_max_clusters': 20,
            'anomaly_detection_threshold': 2.0,
            'seasonality_detection_window': 30  # days
        }
        
        # Machine learning components
        self.scaler = StandardScaler()
        self.trend_clusterer = KMeans(n_clusters=5, random_state=42)
        self.anomaly_detector = DBSCAN(eps=0.3, min_samples=5)
        
        # Time series analysis components
        self.seasonality_detector = None  # Would initialize with proper time series model
        self.trend_forecaster = None      # Would initialize with forecasting model
        
        # Performance metrics cache
        self.metrics_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def process_interaction_analytics(
        self,
        interactions: List[InteractionEvent],
        time_window: str = "24h"
    ) -> Dict[str, Any]:
        """
        Process interaction events to generate comprehensive analytics
        including engagement patterns, user behavior, and content performance.
        """
        try:
            self.logger.info(f"Processing {len(interactions)} interaction events")
            
            if not interactions:
                return {}
            
            analytics_result = {}
            
            # Convert interactions to DataFrame for analysis
            df = await self._interactions_to_dataframe(interactions)
            
            # Basic engagement analytics
            engagement_analytics = await self._analyze_engagement_patterns(df)
            analytics_result['engagement_analytics'] = engagement_analytics
            
            # User behavior analytics
            user_behavior = await self._analyze_user_behavior(df)
            analytics_result['user_behavior_analytics'] = user_behavior
            
            # Content performance analytics
            content_performance = await self._analyze_content_performance(df)
            analytics_result['content_performance'] = content_performance
            
            # Temporal analytics
            temporal_analytics = await self._analyze_temporal_patterns(df)
            analytics_result['temporal_analytics'] = temporal_analytics
            
            # Creator analytics
            creator_analytics = await self._analyze_creator_performance(df)
            analytics_result['creator_analytics'] = creator_analytics
            
            # Revenue analytics
            revenue_analytics = await self._analyze_revenue_patterns(df)
            analytics_result['revenue_analytics'] = revenue_analytics
            
            # Cohort analysis
            cohort_analytics = await self._perform_cohort_analysis(df)
            analytics_result['cohort_analytics'] = cohort_analytics
            
            # Anomaly detection
            anomalies = await self._detect_interaction_anomalies(df)
            analytics_result['anomalies'] = anomalies
            
            # Predictive insights
            predictions = await self._generate_predictive_insights(df)
            analytics_result['predictions'] = predictions
            
            return analytics_result
            
        except Exception as e:
            self.logger.error(f"Error processing interaction analytics: {str(e)}")
            return {}
    
    async def analyze_trending_patterns(
        self,
        content_data: List[ContentItem],
        interaction_data: List[InteractionEvent],
        time_window: str = "24h"
    ) -> List[TrendData]:
        """
        Analyze trending patterns in content and interactions to identify
        emerging trends, viral content, and market opportunities.
        """
        try:
            self.logger.info(f"Analyzing trending patterns for {len(content_data)} content items")
            
            trends = []
            
            # Create content engagement matrix
            engagement_matrix = await self._create_engagement_matrix(
                content_data, interaction_data
            )
            
            # Calculate velocity metrics
            velocity_metrics = await self._calculate_velocity_metrics(
                engagement_matrix, time_window
            )
            
            # Detect trending content
            trending_content = await self._detect_trending_content(
                velocity_metrics, content_data
            )
            
            # Analyze geographic distribution
            geographic_analysis = await self._analyze_geographic_trends(
                trending_content, interaction_data
            )
            
            # Analyze demographic patterns
            demographic_analysis = await self._analyze_demographic_trends(
                trending_content, interaction_data
            )
            
            # Create trend objects
            for content_id, trend_info in trending_content.items():
                content_item = next((c for c in content_data if c.content_id == content_id), None)
                if not content_item:
                    continue
                
                trend_data = TrendData(
                    content_id=content_id,
                    trend_type="content",
                    trend_score=trend_info['trend_score'],
                    velocity=trend_info['velocity'],
                    geographic_distribution=geographic_analysis.get(content_id, {}),
                    demographic_breakdown=demographic_analysis.get(content_id, {}),
                    engagement_patterns=await self._extract_engagement_patterns(content_id, interaction_data),
                    duration_prediction=await self._predict_trend_duration(trend_info),
                    monetization_potential=await self._calculate_trend_monetization_potential(
                        content_item, trend_info
                    ),
                    competition_level=await self._assess_trend_competition(content_item, trending_content)
                )
                
                trends.append(trend_data)
            
            # Sort by trend score
            trends.sort(key=lambda t: t.trend_score, reverse=True)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing trending patterns: {str(e)}")
            return []
    
    async def generate_performance_insights(
        self,
        entity_type: str,
        entity_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance insights for users, creators, or content
        including benchmarks, recommendations, and optimization opportunities.
        """
        try:
            self.logger.info(f"Generating performance insights for {entity_type} {entity_id}")
            
            insights = {}
            
            if entity_type == "user":
                insights = await self._generate_user_insights(entity_id, time_range)
            elif entity_type == "creator":
                insights = await self._generate_creator_insights(entity_id, time_range)
            elif entity_type == "content":
                insights = await self._generate_content_insights(entity_id, time_range)
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Add comparative analysis
            comparative_analysis = await self._generate_comparative_analysis(
                entity_type, entity_id, insights
            )
            insights['comparative_analysis'] = comparative_analysis
            
            # Generate actionable recommendations
            recommendations = await self._generate_actionable_recommendations(
                entity_type, entity_id, insights
            )
            insights['recommendations'] = recommendations
            
            # Calculate ROI and business impact
            business_impact = await self._calculate_business_impact(
                entity_type, entity_id, insights
            )
            insights['business_impact'] = business_impact
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating performance insights: {str(e)}")
            return {}
    
    async def detect_market_opportunities(
        self,
        category: Optional[str] = None,
        creator_tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect market opportunities based on content gaps, audience demand,
        and competitive landscape analysis.
        """
        try:
            self.logger.info(f"Detecting market opportunities for category: {category}")
            
            opportunities = []
            
            # Analyze content supply and demand
            supply_demand_analysis = await self._analyze_content_supply_demand(category)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(supply_demand_analysis)
            
            # Analyze audience unmet needs
            unmet_needs = await self._analyze_unmet_audience_needs(category)
            
            # Assess competitive landscape
            competitive_analysis = await self._assess_competitive_landscape(category, creator_tier)
            
            # Identify emerging niches
            emerging_niches = await self._identify_emerging_niches(category)
            
            # Generate opportunity recommendations
            for gap in content_gaps:
                opportunity = {
                    'opportunity_type': 'content_gap',
                    'category': gap['category'],
                    'gap_description': gap['description'],
                    'market_size_estimate': gap['market_size'],
                    'competition_level': competitive_analysis.get(gap['category'], 0.5),
                    'entry_difficulty': gap['entry_difficulty'],
                    'revenue_potential': gap['revenue_potential'],
                    'time_to_market': gap['time_to_market'],
                    'required_resources': gap['required_resources'],
                    'success_probability': gap['success_probability']
                }
                opportunities.append(opportunity)
            
            for need in unmet_needs:
                opportunity = {
                    'opportunity_type': 'audience_need',
                    'need_description': need['description'],
                    'audience_size': need['audience_size'],
                    'engagement_potential': need['engagement_potential'],
                    'monetization_potential': need['monetization_potential'],
                    'content_format_suggestions': need['format_suggestions'],
                    'target_demographics': need['demographics'],
                    'success_probability': need['success_probability']
                }
                opportunities.append(opportunity)
            
            for niche in emerging_niches:
                opportunity = {
                    'opportunity_type': 'emerging_niche',
                    'niche_name': niche['name'],
                    'growth_trajectory': niche['growth_rate'],
                    'early_adopter_advantage': niche['early_adopter_score'],
                    'market_maturity': niche['maturity_level'],
                    'key_success_factors': niche['success_factors'],
                    'recommended_approach': niche['approach'],
                    'success_probability': niche['success_probability']
                }
                opportunities.append(opportunity)
            
            # Sort by success probability and revenue potential
            opportunities.sort(
                key=lambda o: o.get('success_probability', 0) * o.get('revenue_potential', 0),
                reverse=True
            )
            
            return opportunities[:20]  # Top 20 opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting market opportunities: {str(e)}")
            return []
    
    async def calculate_recommendation_metrics(
        self,
        recommendations: List[ContentItem],
        user_feedback: List[InteractionEvent],
        time_window: str = "7d"
    ) -> Dict[str, float]:
        """
        Calculate comprehensive metrics for recommendation system performance
        including accuracy, diversity, novelty, and business impact.
        """
        try:
            if not recommendations or not user_feedback:
                return {}
            
            metrics = {}
            
            # Accuracy metrics
            accuracy_metrics = await self._calculate_accuracy_metrics(
                recommendations, user_feedback
            )
            metrics.update(accuracy_metrics)
            
            # Diversity metrics
            diversity_metrics = await self._calculate_diversity_metrics(recommendations)
            metrics.update(diversity_metrics)
            
            # Novelty metrics
            novelty_metrics = await self._calculate_novelty_metrics(
                recommendations, user_feedback
            )
            metrics.update(novelty_metrics)
            
            # Coverage metrics
            coverage_metrics = await self._calculate_coverage_metrics(recommendations)
            metrics.update(coverage_metrics)
            
            # Serendipity metrics
            serendipity_metrics = await self._calculate_serendipity_metrics(
                recommendations, user_feedback
            )
            metrics.update(serendipity_metrics)
            
            # Business impact metrics
            business_metrics = await self._calculate_business_impact_metrics(
                recommendations, user_feedback
            )
            metrics.update(business_metrics)
            
            # Fairness metrics
            fairness_metrics = await self._calculate_fairness_metrics(recommendations)
            metrics.update(fairness_metrics)
            
            # User satisfaction metrics
            satisfaction_metrics = await self._calculate_satisfaction_metrics(user_feedback)
            metrics.update(satisfaction_metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating recommendation metrics: {str(e)}")
            return {}
    
    # Private helper methods
    async def _interactions_to_dataframe(
        self,
        interactions: List[InteractionEvent]
    ) -> pd.DataFrame:
        """Convert interaction events to pandas DataFrame for analysis"""
        try:
            data = []
            for interaction in interactions:
                data.append({
                    'user_id': interaction.user_id,
                    'content_id': interaction.content_id,
                    'creator_id': interaction.creator_id,
                    'interaction_type': interaction.interaction_type.value,
                    'duration': interaction.duration,
                    'timestamp': interaction.timestamp,
                    'revenue_impact': interaction.revenue_impact,
                    'session_id': interaction.session_id,
                    'hour': interaction.timestamp.hour,
                    'day_of_week': interaction.timestamp.weekday(),
                    'is_weekend': interaction.timestamp.weekday() >= 5
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error converting interactions to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    async def _analyze_engagement_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze engagement patterns from interaction data"""
        try:
            if df.empty:
                return {}
            
            patterns = {}
            
            # Overall engagement metrics
            patterns['total_interactions'] = len(df)
            patterns['unique_users'] = df['user_id'].nunique()
            patterns['unique_content'] = df['content_id'].nunique()
            patterns['unique_creators'] = df['creator_id'].nunique()
            
            # Interaction type distribution
            interaction_dist = df['interaction_type'].value_counts(normalize=True).to_dict()
            patterns['interaction_type_distribution'] = interaction_dist
            
            # Temporal patterns
            hourly_activity = df['hour'].value_counts().sort_index().to_dict()
            patterns['hourly_activity'] = hourly_activity
            
            daily_activity = df['day_of_week'].value_counts().sort_index().to_dict()
            patterns['daily_activity'] = daily_activity
            
            # Session analysis
            if 'session_id' in df.columns:
                session_stats = df.groupby('session_id').agg({
                    'interaction_type': 'count',
                    'duration': 'sum'
                }).rename(columns={'interaction_type': 'interactions_per_session'})
                
                patterns['avg_interactions_per_session'] = session_stats['interactions_per_session'].mean()
                patterns['avg_session_duration'] = session_stats['duration'].mean()
            
            # Engagement quality metrics
            positive_interactions = df[df['interaction_type'].isin(['like', 'share', 'save', 'follow'])]
            patterns['positive_engagement_rate'] = len(positive_interactions) / len(df)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {}
    
    async def _analyze_user_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            if df.empty:
                return {}
            
            behavior_analysis = {}
            
            # User activity distribution
            user_activity = df['user_id'].value_counts()
            behavior_analysis['user_activity_distribution'] = {
                'mean': user_activity.mean(),
                'median': user_activity.median(),
                'std': user_activity.std(),
                'max': user_activity.max(),
                'min': user_activity.min()
            }
            
            # User engagement patterns
            user_engagement = df.groupby('user_id').agg({
                'interaction_type': lambda x: x.value_counts().to_dict(),
                'duration': ['mean', 'sum', 'count'],
                'revenue_impact': 'sum'
            })
            
            # Calculate user segments
            user_segments = await self._segment_users_by_behavior(df)
            behavior_analysis['user_segments'] = user_segments
            
            # Retention analysis
            retention_analysis = await self._analyze_user_retention(df)
            behavior_analysis['retention_analysis'] = retention_analysis
            
            return behavior_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user behavior: {str(e)}")
            return {}
    
    async def _calculate_velocity_metrics(
        self,
        engagement_matrix: pd.DataFrame,
        time_window: str
    ) -> Dict[str, float]:
        """Calculate velocity metrics for trend detection"""
        try:
            velocity_metrics = {}
            
            # Calculate time windows
            time_delta = self._parse_time_window(time_window)
            current_time = datetime.now()
            previous_time = current_time - time_delta
            
            # Calculate engagement velocity for each content item
            for content_id in engagement_matrix.columns:
                current_engagement = engagement_matrix[content_id].sum()
                
                # Calculate previous period engagement
                # This would require time-series data structure in real implementation
                previous_engagement = current_engagement * 0.8  # Mock calculation
                
                if previous_engagement > 0:
                    velocity = (current_engagement - previous_engagement) / previous_engagement
                else:
                    velocity = 1.0 if current_engagement > 0 else 0.0
                
                velocity_metrics[content_id] = velocity
            
            return velocity_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating velocity metrics: {str(e)}")
            return {}
    
    def _parse_time_window(self, time_window: str) -> timedelta:
        """Parse time window string to timedelta object"""
        try:
            if time_window.endswith('h'):
                hours = int(time_window[:-1])
                return timedelta(hours=hours)
            elif time_window.endswith('d'):
                days = int(time_window[:-1])
                return timedelta(days=days)
            elif time_window.endswith('w'):
                weeks = int(time_window[:-1])
                return timedelta(weeks=weeks)
            else:
                return timedelta(days=1)  # Default
                
        except ValueError:
            return timedelta(days=1)  # Default fallback
