"""Momentum Capitalizer

Viral momentum detection and capitalization system that identifies when content
is gaining viral traction and automatically amplifies it for maximum impact.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class MomentumType(Enum):
    """Types of momentum patterns"""
    VIRAL_SPIKE = "viral_spike"
    STEADY_GROWTH = "steady_growth"
    EXPONENTIAL = "exponential"
    PLATEAU_BREAK = "plateau_break"
    SECOND_WAVE = "second_wave"
    CROSS_PLATFORM = "cross_platform"


class MomentumStage(Enum):
    """Stages of momentum development"""
    INITIAL = "initial"
    BUILDING = "building"
    ACCELERATING = "accelerating"
    PEAK = "peak"
    SUSTAINING = "sustaining"
    DECLINING = "declining"


@dataclass
class MomentumAnalysis:
    """Momentum analysis data structure"""
    content_id: str
    momentum_type: MomentumType
    momentum_stage: MomentumStage
    velocity: float  # Views/engagement per minute
    acceleration: float  # Change in velocity
    viral_coefficient: float  # How viral the content is becoming
    growth_rate: float  # Current growth rate
    momentum_score: float  # Overall momentum score (0-1)
    peak_prediction: datetime
    sustainability_score: float  # How long momentum will last
    cross_platform_factor: float  # Momentum across platforms
    detected_at: datetime
    confidence_level: float
    triggers: List[str]  # What triggered the momentum
    metrics: Dict[str, Any]


@dataclass
class CapitalizationStrategy:
    """Momentum capitalization strategy"""
    strategy_id: str
    momentum_types: List[MomentumType]
    trigger_thresholds: Dict[str, float]
    amplification_tactics: List[str]
    budget_allocation: Dict[str, float]
    timing_optimization: Dict[str, Any]
    risk_tolerance: float
    expected_roi: float
    automatic_execution: bool


@dataclass
class CapitalizationResult:
    """Result of momentum capitalization actions"""
    capitalization_id: str
    content_id: str
    momentum_analysis: MomentumAnalysis
    strategy_used: str
    actions_executed: List[Dict[str, Any]]
    investment_made: float
    predicted_amplification: Dict[str, float]
    actual_amplification: Optional[Dict[str, float]]
    roi_achieved: Optional[float]
    peak_reached: Optional[datetime]
    momentum_sustained: bool
    execution_timestamp: datetime
    completion_timestamp: Optional[datetime]


class MomentumCapitalizer:
    """Viral momentum detection and capitalization system"""
    
    def __init__(self):
        """Initialize momentum capitalizer"""
        self.active_momentum = {}
        self.capitalization_strategies = self._init_strategies()
        self.momentum_history = {}
        self.velocity_trackers = {}
        self.monitoring_active = False
        
    def _init_strategies(self) -> Dict[str, CapitalizationStrategy]:
        """Initialize capitalization strategies"""
        strategies = {}
        
        # Viral Spike Strategy
        strategies['viral_spike'] = CapitalizationStrategy(
            strategy_id='viral_spike',
            momentum_types=[MomentumType.VIRAL_SPIKE, MomentumType.EXPONENTIAL],
            trigger_thresholds={
                'velocity': 1000.0,  # Views per minute
                'acceleration': 2.0,  # 2x acceleration
                'viral_coefficient': 0.8,
                'momentum_score': 0.85
            },
            amplification_tactics=[
                'cross_platform_boost',
                'influencer_outreach',
                'paid_amplification',
                'community_activation'
            ],
            budget_allocation={
                'paid_boost': 0.6,
                'influencer_outreach': 0.3,
                'community_activation': 0.1
            },
            timing_optimization={
                'immediate_boost': True,
                'sustained_campaign': True,
                'peak_timing_critical': True
            },
            risk_tolerance=0.3,
            expected_roi=5.0,
            automatic_execution=True
        )
        
        # Steady Growth Strategy
        strategies['steady_growth'] = CapitalizationStrategy(
            strategy_id='steady_growth',
            momentum_types=[MomentumType.STEADY_GROWTH],
            trigger_thresholds={
                'velocity': 100.0,
                'acceleration': 1.2,
                'viral_coefficient': 0.5,
                'momentum_score': 0.6
            },
            amplification_tactics=[
                'organic_amplification',
                'hashtag_optimization',
                'timing_optimization',
                'cross_posting'
            ],
            budget_allocation={
                'organic_amplification': 0.5,
                'hashtag_optimization': 0.2,
                'timing_optimization': 0.2,
                'cross_posting': 0.1
            },
            timing_optimization={
                'gradual_boost': True,
                'sustained_campaign': True,
                'peak_timing_critical': False
            },
            risk_tolerance=0.1,
            expected_roi=2.0,
            automatic_execution=True
        )
        
        # Cross-Platform Strategy
        strategies['cross_platform'] = CapitalizationStrategy(
            strategy_id='cross_platform',
            momentum_types=[MomentumType.CROSS_PLATFORM],
            trigger_thresholds={
                'cross_platform_factor': 0.7,
                'momentum_score': 0.7,
                'velocity': 500.0
            },
            amplification_tactics=[
                'synchronized_posting',
                'platform_specific_optimization',
                'cross_platform_promotion',
                'unified_hashtag_strategy'
            ],
            budget_allocation={
                'synchronized_posting': 0.4,
                'platform_optimization': 0.3,
                'cross_promotion': 0.2,
                'hashtag_strategy': 0.1
            },
            timing_optimization={
                'synchronized_timing': True,
                'platform_specific_timing': True,
                'peak_timing_critical': True
            },
            risk_tolerance=0.2,
            expected_roi=3.5,
            automatic_execution=True
        )
        
        return strategies
    
    async def start_momentum_monitoring(self, content_ids: List[str]) -> bool:
        """Start monitoring momentum for specified content"""
        try:
            logger.info(f"Starting momentum monitoring for {len(content_ids)} content items")
            
            self.monitoring_active = True
            
            # Initialize velocity trackers
            for content_id in content_ids:
                self.velocity_trackers[content_id] = {
                    'data_points': [],
                    'last_update': datetime.utcnow(),
                    'baseline_established': False
                }
            
            # Start monitoring loop
            asyncio.create_task(self._momentum_monitoring_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting momentum monitoring: {str(e)}")
            return False
    
    async def detect_viral_momentum(
        self,
        content_id: str,
        current_metrics: Dict[str, Any],
        platform_data: Optional[Dict[str, Any]] = None
    ) -> Optional[MomentumAnalysis]:
        """Detect viral momentum in content performance"""
        try:
            logger.info(f"Analyzing momentum for content: {content_id}")
            
            # Update velocity tracking
            await self._update_velocity_tracking(content_id, current_metrics)
            
            # Calculate velocity and acceleration
            velocity = await self._calculate_velocity(content_id, current_metrics)
            acceleration = await self._calculate_acceleration(content_id)
            
            # Calculate viral coefficient
            viral_coefficient = await self._calculate_viral_coefficient(current_metrics)
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(content_id, current_metrics)
            
            # Calculate momentum score
            momentum_score = await self._calculate_momentum_score(
                velocity, acceleration, viral_coefficient, growth_rate
            )
            
            # Check if momentum is significant enough
            if momentum_score < 0.5:
                return None
            
            # Determine momentum type
            momentum_type = await self._determine_momentum_type(
                velocity, acceleration, viral_coefficient, platform_data
            )
            
            # Determine momentum stage
            momentum_stage = await self._determine_momentum_stage(
                content_id, momentum_score, acceleration
            )
            
            # Predict peak timing
            peak_prediction = await self._predict_momentum_peak(
                content_id, velocity, acceleration, momentum_type
            )
            
            # Calculate sustainability score
            sustainability_score = await self._calculate_sustainability_score(
                momentum_type, current_metrics, platform_data
            )
            
            # Calculate cross-platform factor
            cross_platform_factor = await self._calculate_cross_platform_factor(
                content_id, platform_data
            )
            
            # Identify momentum triggers
            triggers = await self._identify_momentum_triggers(
                content_id, current_metrics, platform_data
            )
            
            # Calculate confidence level
            confidence_level = await self._calculate_confidence_level(
                velocity, acceleration, momentum_score
            )
            
            momentum_analysis = MomentumAnalysis(
                content_id=content_id,
                momentum_type=momentum_type,
                momentum_stage=momentum_stage,
                velocity=velocity,
                acceleration=acceleration,
                viral_coefficient=viral_coefficient,
                growth_rate=growth_rate,
                momentum_score=momentum_score,
                peak_prediction=peak_prediction,
                sustainability_score=sustainability_score,
                cross_platform_factor=cross_platform_factor,
                detected_at=datetime.utcnow(),
                confidence_level=confidence_level,
                triggers=triggers,
                metrics=current_metrics
            )
            
            # Store active momentum
            self.active_momentum[content_id] = momentum_analysis
            
            logger.info(f"Momentum detected: {momentum_type.value} - Score: {momentum_score:.3f}")
            
            return momentum_analysis
            
        except Exception as e:
            logger.error(f"Error detecting viral momentum: {str(e)}")
            return None
    
    async def capitalize_momentum(
        self,
        content_id: str,
        momentum: MomentumAnalysis,
        strategy: Optional[CapitalizationStrategy] = None
    ) -> CapitalizationResult:
        """Automatically capitalize on detected momentum"""
        try:
            logger.info(f"Capitalizing momentum for content: {content_id}")
            
            execution_start = datetime.utcnow()
            
            # Select strategy if not provided
            if not strategy:
                strategy = await self._select_optimal_strategy(momentum)
            
            # Check if momentum meets strategy thresholds
            threshold_check = await self._check_strategy_thresholds(momentum, strategy)
            if not threshold_check['eligible']:
                logger.warning(f"Momentum doesn't meet thresholds: {threshold_check['reason']}")
                return await self._create_failed_capitalization(
                    content_id, momentum, strategy, threshold_check['reason']
                )
            
            # Calculate optimal investment
            investment_amount = await self._calculate_optimal_investment(momentum, strategy)
            
            # Generate amplification actions
            amplification_actions = await self._generate_amplification_actions(
                content_id, momentum, strategy, investment_amount
            )
            
            # Execute amplification actions
            execution_results = await self._execute_amplification_actions(
                content_id, amplification_actions
            )
            
            # Calculate predicted amplification
            predicted_amplification = await self._predict_amplification_impact(
                momentum, amplification_actions, investment_amount
            )
            
            # Create capitalization result
            result = CapitalizationResult(
                capitalization_id=f"cap_{content_id}_{int(execution_start.timestamp())}",
                content_id=content_id,
                momentum_analysis=momentum,
                strategy_used=strategy.strategy_id,
                actions_executed=execution_results,
                investment_made=investment_amount,
                predicted_amplification=predicted_amplification,
                actual_amplification=None,  # Will be measured later
                roi_achieved=None,
                peak_reached=None,
                momentum_sustained=False,
                execution_timestamp=execution_start,
                completion_timestamp=None
            )
            
            # Store capitalization result
            await self._store_capitalization_result(result)
            
            # Schedule impact measurement
            asyncio.create_task(self._measure_capitalization_impact(result))
            
            return result
            
        except Exception as e:
            logger.error(f"Error capitalizing momentum: {str(e)}")
            raise
    
    async def predict_momentum_peak(
        self,
        content_id: str,
        current_velocity: float,
        platform_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Predict when momentum will reach its peak"""
        try:
            if content_id not in self.active_momentum:
                return {}
            
            momentum = self.active_momentum[content_id]
            
            # Analyze velocity trends
            velocity_trend = await self._analyze_velocity_trend(content_id)
            
            # Calculate peak timing based on momentum type
            peak_timing = await self._calculate_peak_timing(
                momentum, velocity_trend, platform_context
            )
            
            # Predict peak metrics
            peak_metrics = await self._predict_peak_metrics(
                momentum, peak_timing, velocity_trend
            )
            
            # Calculate confidence in prediction
            prediction_confidence = await self._calculate_peak_prediction_confidence(
                momentum, velocity_trend
            )
            
            # Generate recommendations for peak timing
            peak_recommendations = await self._generate_peak_timing_recommendations(
                momentum, peak_timing
            )
            
            return {
                'content_id': content_id,
                'predicted_peak_time': peak_timing.get('peak_time'),
                'time_to_peak': peak_timing.get('time_to_peak'),
                'peak_metrics': peak_metrics,
                'prediction_confidence': prediction_confidence,
                'momentum_type': momentum.momentum_type.value,
                'current_stage': momentum.momentum_stage.value,
                'recommendations': peak_recommendations,
                'optimal_capitalization_window': peak_timing.get('capitalization_window')
            }
            
        except Exception as e:
            logger.error(f"Error predicting momentum peak: {str(e)}")
            return {}
    
    async def get_momentum_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive momentum monitoring dashboard"""
        try:
            dashboard = {
                'timestamp': datetime.utcnow(),
                'active_momentum_count': len(self.active_momentum),
                'momentum_breakdown': {},
                'stage_breakdown': {},
                'high_potential_content': [],
                'capitalization_opportunities': [],
                'performance_metrics': {}
            }
            
            # Analyze active momentum
            for content_id, momentum in self.active_momentum.items():
                # Count by type
                momentum_type = momentum.momentum_type.value
                dashboard['momentum_breakdown'][momentum_type] = dashboard['momentum_breakdown'].get(momentum_type, 0) + 1
                
                # Count by stage
                stage = momentum.momentum_stage.value
                dashboard['stage_breakdown'][stage] = dashboard['stage_breakdown'].get(stage, 0) + 1
                
                # Identify high potential content
                if momentum.momentum_score > 0.8:
                    dashboard['high_potential_content'].append({
                        'content_id': content_id,
                        'momentum_score': momentum.momentum_score,
                        'velocity': momentum.velocity,
                        'predicted_peak': momentum.peak_prediction,
                        'type': momentum_type
                    })
                
                # Identify capitalization opportunities
                if (momentum.momentum_score > 0.7 and 
                    momentum.momentum_stage in [MomentumStage.BUILDING, MomentumStage.ACCELERATING]):
                    dashboard['capitalization_opportunities'].append({
                        'content_id': content_id,
                        'opportunity_score': momentum.momentum_score,
                        'time_sensitive': momentum.momentum_stage == MomentumStage.ACCELERATING,
                        'investment_recommendation': await self._calculate_investment_recommendation(momentum)
                    })
            
            # Get performance metrics
            dashboard['performance_metrics'] = await self._get_momentum_performance_metrics()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting momentum dashboard: {str(e)}")
            return {}
    
    # Private helper methods
    async def _momentum_monitoring_loop(self):
        """Main momentum monitoring loop"""
        while self.monitoring_active:
            try:
                # Check all tracked content for momentum
                for content_id in list(self.velocity_trackers.keys()):
                    # Get current metrics (placeholder)
                    current_metrics = await self._get_current_metrics(content_id)
                    
                    # Detect momentum
                    momentum = await self.detect_viral_momentum(content_id, current_metrics)
                    
                    # Auto-capitalize if strategy allows
                    if momentum and momentum.momentum_score > 0.8:
                        strategy = await self._select_optimal_strategy(momentum)
                        if strategy.automatic_execution:
                            await self.capitalize_momentum(content_id, momentum, strategy)
                
                # Clean up old momentum data
                await self._cleanup_old_momentum()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in momentum monitoring loop: {str(e)}")
                await asyncio.sleep(300)
    
    async def _update_velocity_tracking(self, content_id: str, metrics: Dict[str, Any]):
        """Update velocity tracking data"""
        if content_id not in self.velocity_trackers:
            self.velocity_trackers[content_id] = {
                'data_points': [],
                'last_update': datetime.utcnow(),
                'baseline_established': False
            }
        
        tracker = self.velocity_trackers[content_id]
        current_time = datetime.utcnow()
        
        data_point = {
            'timestamp': current_time,
            'views': metrics.get('total_views', 0),
            'engagement': metrics.get('total_engagement', 0),
            'shares': metrics.get('total_shares', 0)
        }
        
        tracker['data_points'].append(data_point)
        tracker['last_update'] = current_time
        
        # Keep only last 100 data points
        if len(tracker['data_points']) > 100:
            tracker['data_points'] = tracker['data_points'][-100:]
        
        # Establish baseline after 10 data points
        if len(tracker['data_points']) >= 10:
            tracker['baseline_established'] = True
    
    async def _calculate_velocity(self, content_id: str, current_metrics: Dict[str, Any]) -> float:
        """Calculate current velocity (views/engagement per minute)"""
        tracker = self.velocity_trackers.get(content_id, {})
        data_points = tracker.get('data_points', [])
        
        if len(data_points) < 2:
            return 0.0
        
        # Calculate velocity from last two data points
        latest = data_points[-1]
        previous = data_points[-2]
        
        time_diff = (latest['timestamp'] - previous['timestamp']).total_seconds() / 60  # minutes
        views_diff = latest['views'] - previous['views']
        
        if time_diff > 0:
            return views_diff / time_diff
        return 0.0
    
    async def _calculate_acceleration(self, content_id: str) -> float:
        """Calculate acceleration (change in velocity)"""
        tracker = self.velocity_trackers.get(content_id, {})
        data_points = tracker.get('data_points', [])
        
        if len(data_points) < 3:
            return 0.0
        
        # Calculate velocity for last two intervals
        latest = data_points[-1]
        middle = data_points[-2]
        earliest = data_points[-3]
        
        # Velocity 1 (middle to latest)
        time_diff_1 = (latest['timestamp'] - middle['timestamp']).total_seconds() / 60
        velocity_1 = (latest['views'] - middle['views']) / time_diff_1 if time_diff_1 > 0 else 0
        
        # Velocity 2 (earliest to middle)
        time_diff_2 = (middle['timestamp'] - earliest['timestamp']).total_seconds() / 60
        velocity_2 = (middle['views'] - earliest['views']) / time_diff_2 if time_diff_2 > 0 else 0
        
        # Acceleration is change in velocity
        return velocity_1 - velocity_2
    
    async def _calculate_viral_coefficient(self, metrics: Dict[str, Any]) -> float:
        """Calculate viral coefficient (how viral the content is becoming)"""
        total_views = metrics.get('total_views', 1)
        total_shares = metrics.get('total_shares', 0)
        total_engagement = metrics.get('total_engagement', 0)
        
        # Simple viral coefficient calculation
        share_rate = total_shares / total_views if total_views > 0 else 0
        engagement_rate = total_engagement / total_views if total_views > 0 else 0
        
        # Viral coefficient combines share rate and engagement rate
        viral_coefficient = (share_rate * 0.7 + engagement_rate * 0.3) * 10
        
        return min(1.0, viral_coefficient)
    
    async def _calculate_growth_rate(self, content_id: str, current_metrics: Dict[str, Any]) -> float:
        """Calculate current growth rate"""
        tracker = self.velocity_trackers.get(content_id, {})
        data_points = tracker.get('data_points', [])
        
        if len(data_points) < 2:
            return 0.0
        
        # Calculate growth rate over last hour
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        # Find data point closest to 1 hour ago
        hour_ago_point = None
        for point in reversed(data_points):
            if point['timestamp'] <= hour_ago:
                hour_ago_point = point
                break
        
        if not hour_ago_point:
            hour_ago_point = data_points[0]
        
        current_views = current_metrics.get('total_views', 0)
        past_views = hour_ago_point['views']
        
        if past_views > 0:
            growth_rate = (current_views - past_views) / past_views
        else:
            growth_rate = 0.0
        
        return growth_rate
    
    async def _calculate_momentum_score(
        self, 
        velocity: float, 
        acceleration: float, 
        viral_coefficient: float, 
        growth_rate: float
    ) -> float:
        """Calculate overall momentum score"""
        # Normalize values
        normalized_velocity = min(1.0, velocity / 1000.0)  # Normalize to 1000 views/min
        normalized_acceleration = min(1.0, max(-1.0, acceleration / 500.0))  # Normalize to 500 views/min change
        normalized_growth = min(1.0, growth_rate)
        
        # Weight different factors
        momentum_score = (
            normalized_velocity * 0.3 +
            normalized_acceleration * 0.3 +
            viral_coefficient * 0.25 +
            normalized_growth * 0.15
        )
        
        return max(0.0, min(1.0, momentum_score))
    
    async def _determine_momentum_type(
        self, 
        velocity: float, 
        acceleration: float, 
        viral_coefficient: float, 
        platform_data: Optional[Dict[str, Any]]
    ) -> MomentumType:
        """Determine the type of momentum"""
        if viral_coefficient > 0.8 and acceleration > 100:
            return MomentumType.VIRAL_SPIKE
        elif acceleration > 50 and velocity > 200:
            return MomentumType.EXPONENTIAL
        elif velocity > 50 and acceleration > 0:
            return MomentumType.STEADY_GROWTH
        elif platform_data and len(platform_data) > 1:
            return MomentumType.CROSS_PLATFORM
        elif acceleration > 10:
            return MomentumType.PLATEAU_BREAK
        else:
            return MomentumType.STEADY_GROWTH
    
    async def _determine_momentum_stage(
        self, 
        content_id: str, 
        momentum_score: float, 
        acceleration: float
    ) -> MomentumStage:
        """Determine current stage of momentum"""
        tracker = self.velocity_trackers.get(content_id, {})
        data_points = tracker.get('data_points', [])
        
        if len(data_points) < 5:
            return MomentumStage.INITIAL
        elif momentum_score < 0.3:
            return MomentumStage.INITIAL
        elif momentum_score < 0.6 and acceleration > 0:
            return MomentumStage.BUILDING
        elif momentum_score < 0.8 and acceleration > 10:
            return MomentumStage.ACCELERATING
        elif momentum_score > 0.8 and acceleration > 0:
            return MomentumStage.PEAK
        elif momentum_score > 0.6 and acceleration <= 0:
            return MomentumStage.SUSTAINING
        else:
            return MomentumStage.DECLINING
    
    async def _predict_momentum_peak(
        self, 
        content_id: str, 
        velocity: float, 
        acceleration: float, 
        momentum_type: MomentumType
    ) -> datetime:
        """Predict when momentum will peak"""
        current_time = datetime.utcnow()
        
        # Different momentum types have different peak timing patterns
        if momentum_type == MomentumType.VIRAL_SPIKE:
            # Viral spikes peak quickly
            peak_hours = 2 + (velocity / 1000)  # 2-6 hours typically
        elif momentum_type == MomentumType.EXPONENTIAL:
            # Exponential growth peaks within hours
            peak_hours = 4 + (acceleration / 100)  # 4-10 hours
        elif momentum_type == MomentumType.STEADY_GROWTH:
            # Steady growth peaks over days
            peak_hours = 24 + (velocity / 50)  # 1-3 days
        else:
            # Default prediction
            peak_hours = 12
        
        return current_time + timedelta(hours=peak_hours)
    
    async def _calculate_sustainability_score(
        self, 
        momentum_type: MomentumType, 
        metrics: Dict[str, Any], 
        platform_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate how sustainable the momentum is"""
        base_sustainability = {
            MomentumType.VIRAL_SPIKE: 0.3,  # Viral spikes are short-lived
            MomentumType.STEADY_GROWTH: 0.8,  # Steady growth is sustainable
            MomentumType.EXPONENTIAL: 0.5,  # Exponential can be sustained
            MomentumType.CROSS_PLATFORM: 0.7,  # Cross-platform is more sustainable
            MomentumType.PLATEAU_BREAK: 0.6,  # Plateau breaks can sustain
            MomentumType.SECOND_WAVE: 0.4  # Second waves are harder to sustain
        }
        
        base_score = base_sustainability.get(momentum_type, 0.5)
        
        # Adjust based on content quality indicators
        engagement_rate = metrics.get('engagement_rate', 0)
        if engagement_rate > 0.1:  # High engagement
            base_score += 0.1
        
        # Adjust based on platform diversity
        if platform_data and len(platform_data) > 2:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _calculate_cross_platform_factor(
        self, 
        content_id: str, 
        platform_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate cross-platform momentum factor"""
        if not platform_data or len(platform_data) <= 1:
            return 0.0
        
        # Calculate variance in performance across platforms
        platform_performances = []
        for platform, data in platform_data.items():
            performance = data.get('momentum_score', 0)
            platform_performances.append(performance)
        
        if not platform_performances:
            return 0.0
        
        # Higher factor if momentum is consistent across platforms
        avg_performance = sum(platform_performances) / len(platform_performances)
        variance = sum((p - avg_performance) ** 2 for p in platform_performances) / len(platform_performances)
        
        # Lower variance means better cross-platform momentum
        cross_platform_factor = avg_performance * (1 - min(1.0, variance))
        
        return cross_platform_factor
    
    async def _identify_momentum_triggers(
        self, 
        content_id: str, 
        metrics: Dict[str, Any], 
        platform_data: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Identify what triggered the momentum"""
        triggers = []
        
        # Check for viral indicators
        viral_coefficient = await self._calculate_viral_coefficient(metrics)
        if viral_coefficient > 0.7:
            triggers.append('high_viral_coefficient')
        
        # Check for engagement spike
        engagement_rate = metrics.get('engagement_rate', 0)
        if engagement_rate > 0.1:
            triggers.append('engagement_spike')
        
        # Check for share velocity
        share_rate = metrics.get('total_shares', 0) / max(metrics.get('total_views', 1), 1)
        if share_rate > 0.05:
            triggers.append('high_share_velocity')
        
        # Check for algorithm boost
        velocity = await self._calculate_velocity(content_id, metrics)
        if velocity > 500:
            triggers.append('algorithm_boost')
        
        # Check for influencer mention
        if metrics.get('influencer_mentions', 0) > 0:
            triggers.append('influencer_mention')
        
        # Check for trending hashtag
        if metrics.get('trending_hashtags', 0) > 0:
            triggers.append('trending_hashtag')
        
        return triggers
    
    async def _calculate_confidence_level(
        self, 
        velocity: float, 
        acceleration: float, 
        momentum_score: float
    ) -> float:
        """Calculate confidence level in momentum detection"""
        # Higher confidence with higher velocity and score
        velocity_confidence = min(1.0, velocity / 1000.0)
        score_confidence = momentum_score
        acceleration_confidence = min(1.0, max(0.0, acceleration / 100.0))
        
        overall_confidence = (
            velocity_confidence * 0.4 +
            score_confidence * 0.4 +
            acceleration_confidence * 0.2
        )
        
        return overall_confidence
    
    async def _select_optimal_strategy(self, momentum: MomentumAnalysis) -> CapitalizationStrategy:
        """Select optimal capitalization strategy for momentum"""
        # Find strategy that best matches momentum type
        for strategy in self.capitalization_strategies.values():
            if momentum.momentum_type in strategy.momentum_types:
                return strategy
        
        # Return default strategy if no match
        return list(self.capitalization_strategies.values())[0]
    
    async def _check_strategy_thresholds(
        self, 
        momentum: MomentumAnalysis, 
        strategy: CapitalizationStrategy
    ) -> Dict[str, Any]:
        """Check if momentum meets strategy thresholds"""
        thresholds = strategy.trigger_thresholds
        
        # Check velocity threshold
        if momentum.velocity < thresholds.get('velocity', 0):
            return {'eligible': False, 'reason': 'Velocity below threshold'}
        
        # Check acceleration threshold
        if momentum.acceleration < thresholds.get('acceleration', 0):
            return {'eligible': False, 'reason': 'Acceleration below threshold'}
        
        # Check viral coefficient threshold
        if momentum.viral_coefficient < thresholds.get('viral_coefficient', 0):
            return {'eligible': False, 'reason': 'Viral coefficient below threshold'}
        
        # Check momentum score threshold
        if momentum.momentum_score < thresholds.get('momentum_score', 0):
            return {'eligible': False, 'reason': 'Momentum score below threshold'}
        
        return {'eligible': True, 'reason': 'All thresholds met'}
    
    async def _calculate_optimal_investment(
        self, 
        momentum: MomentumAnalysis, 
        strategy: CapitalizationStrategy
    ) -> float:
        """Calculate optimal investment amount for capitalization"""
        # Base investment on momentum score and expected ROI
        base_investment = momentum.momentum_score * 1000.0  # Base up to $1000
        
        # Adjust based on momentum type
        type_multipliers = {
            MomentumType.VIRAL_SPIKE: 2.0,
            MomentumType.EXPONENTIAL: 1.5,
            MomentumType.STEADY_GROWTH: 1.0,
            MomentumType.CROSS_PLATFORM: 1.8,
            MomentumType.PLATEAU_BREAK: 1.2,
            MomentumType.SECOND_WAVE: 0.8
        }
        
        multiplier = type_multipliers.get(momentum.momentum_type, 1.0)
        optimal_investment = base_investment * multiplier
        
        # Cap investment based on strategy limits
        max_investment = strategy.budget_allocation.get('total_budget', 5000.0)
        
        return min(optimal_investment, max_investment)
    
    # Additional helper methods (placeholders)
    async def _generate_amplification_actions(self, content_id: str, momentum: MomentumAnalysis, strategy: CapitalizationStrategy, investment: float) -> List[Dict[str, Any]]:
        """Generate amplification actions"""
        return [
            {'action': 'cross_platform_boost', 'investment': investment * 0.4},
            {'action': 'influencer_outreach', 'investment': investment * 0.3},
            {'action': 'paid_amplification', 'investment': investment * 0.3}
        ]
    
    async def _execute_amplification_actions(self, content_id: str, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute amplification actions"""
        results = []
        for action in actions:
            results.append({
                'action': action['action'],
                'status': 'success',
                'cost': action['investment']
            })
        return results
    
    async def _predict_amplification_impact(self, momentum: MomentumAnalysis, actions: List[Dict[str, Any]], investment: float) -> Dict[str, float]:
        """Predict amplification impact"""
        return {
            'reach_multiplier': 2.5,
            'engagement_boost': 1.8,
            'viral_acceleration': 3.0
        }
    
    async def _store_capitalization_result(self, result: CapitalizationResult):
        """Store capitalization result"""
        logger.info(f"Stored capitalization result: {result.capitalization_id}")
    
    async def _measure_capitalization_impact(self, result: CapitalizationResult):
        """Measure actual impact of capitalization"""
        await asyncio.sleep(3600)  # Wait 1 hour
        logger.info(f"Measuring impact for capitalization: {result.capitalization_id}")
    
    async def _create_failed_capitalization(self, content_id: str, momentum: MomentumAnalysis, strategy: CapitalizationStrategy, reason: str) -> CapitalizationResult:
        """Create failed capitalization result"""
        return CapitalizationResult(
            capitalization_id=f"failed_{content_id}",
            content_id=content_id,
            momentum_analysis=momentum,
            strategy_used=strategy.strategy_id,
            actions_executed=[],
            investment_made=0.0,
            predicted_amplification={},
            actual_amplification=None,
            roi_achieved=None,
            peak_reached=None,
            momentum_sustained=False,
            execution_timestamp=datetime.utcnow(),
            completion_timestamp=None
        )
    
    async def _get_current_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get current metrics for content"""
        return {
            'total_views': 10000,
            'total_engagement': 500,
            'total_shares': 50,
            'engagement_rate': 0.05
        }
    
    async def _cleanup_old_momentum(self):
        """Clean up old momentum data"""
        current_time = datetime.utcnow()
        expired_content = []
        
        for content_id, momentum in self.active_momentum.items():
            if current_time > momentum.detected_at + timedelta(hours=48):
                expired_content.append(content_id)
        
        for content_id in expired_content:
            del self.active_momentum[content_id]
    
    # Additional placeholder methods for completeness
    async def _analyze_velocity_trend(self, content_id: str) -> Dict[str, Any]:
        return {'trend': 'increasing', 'confidence': 0.8}
    
    async def _calculate_peak_timing(self, momentum: MomentumAnalysis, trend: Dict, context: Optional[Dict]) -> Dict[str, Any]:
        return {'peak_time': momentum.peak_prediction, 'time_to_peak': timedelta(hours=4)}
    
    async def _predict_peak_metrics(self, momentum: MomentumAnalysis, timing: Dict, trend: Dict) -> Dict[str, Any]:
        return {'peak_views': 1000000, 'peak_engagement': 50000}
    
    async def _calculate_peak_prediction_confidence(self, momentum: MomentumAnalysis, trend: Dict) -> float:
        return 0.85
    
    async def _generate_peak_timing_recommendations(self, momentum: MomentumAnalysis, timing: Dict) -> List[str]:
        return ['Boost content in next 2 hours', 'Prepare cross-platform campaign']
    
    async def _calculate_investment_recommendation(self, momentum: MomentumAnalysis) -> float:
        return momentum.momentum_score * 500.0
    
    async def _get_momentum_performance_metrics(self) -> Dict[str, Any]:
        return {'success_rate': 0.87, 'average_roi': 3.2}


__all__ = [
    'MomentumCapitalizer', 'MomentumAnalysis', 'CapitalizationStrategy', 'CapitalizationResult',
    'MomentumType', 'MomentumStage'
]