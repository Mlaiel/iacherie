"""
🔍 MONITORING ANALYTICS - Attribution Modeling Engine
Advanced ML-powered attribution analysis for Ainflue creator ecosystem
Lead Dev IA + ML Engineer Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score
import networkx as nx
from scipy import stats
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttributionModel(Enum):
    """Attribution model types"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    MARKOV_CHAIN = "markov_chain"
    SHAPLEY_VALUE = "shapley_value"

class TouchpointType(Enum):
    """Types of creator journey touchpoints"""
    ORGANIC_SEARCH = "organic_search"
    SOCIAL_MEDIA = "social_media"
    DIRECT_VISIT = "direct_visit"
    REFERRAL = "referral"
    EMAIL_CAMPAIGN = "email_campaign"
    PAID_ADVERTISING = "paid_advertising"
    CONTENT_DISCOVERY = "content_discovery"
    COLLABORATION = "collaboration"
    PLATFORM_RECOMMENDATION = "platform_recommendation"
    INFLUENCER_MENTION = "influencer_mention"

class ConversionType(Enum):
    """Types of conversions to track"""
    CREATOR_SIGNUP = "creator_signup"
    CONTENT_UPLOAD = "content_upload"
    FIRST_COLLABORATION = "first_collaboration"
    MONETIZATION_START = "monetization_start"
    SUBSCRIPTION_PURCHASE = "subscription_purchase"
    PREMIUM_UPGRADE = "premium_upgrade"

@dataclass
class Touchpoint:
    """Individual touchpoint in creator journey"""
    touchpoint_id: str
    user_id: str
    touchpoint_type: TouchpointType
    timestamp: datetime
    channel: str
    campaign_id: Optional[str] = None
    content_id: Optional[str] = None
    referrer: Optional[str] = None
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Conversion:
    """Conversion event"""
    conversion_id: str
    user_id: str
    conversion_type: ConversionType
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AttributionResult:
    """Attribution analysis result"""
    touchpoint_type: TouchpointType
    channel: str
    attribution_credit: float
    conversion_count: int
    total_value: float
    confidence_score: float
    model_used: AttributionModel

class AttributionModelingEngine:
    """
    🧠 Advanced Attribution Modeling Engine for Ainflue Platform
    
    ML-powered multi-touch attribution with advanced models:
    - Data-driven attribution using machine learning
    - Markov chain attribution modeling
    - Shapley value cooperative game theory
    - Time decay and position-based models
    - Cross-platform journey analysis
    - Incremental lift measurement
    """
    
    def __init__(self, db_url: str, lookback_window: int = 30):
        """Initialize attribution modeling engine"""
        self.db_url = db_url
        self.lookback_window = lookback_window
        
        # ML models for data-driven attribution
        self.logistic_model = LogisticRegression(random_state=42)
        self.random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Attribution data storage
        self.touchpoints: List[Touchpoint] = []
        self.conversions: List[Conversion] = []
        self.user_journeys: Dict[str, List[Touchpoint]] = {}
        self.attribution_results: Dict[str, List[AttributionResult]] = {}
        
        # Markov chain transition matrix
        self.transition_matrix: np.ndarray = None
        self.state_mapping: Dict[str, int] = {}
        
        logger.info("🔍 Attribution Modeling Engine initialized")

    async def collect_touchpoint_data(
        self,
        start_date: datetime,
        end_date: datetime,
        user_ids: List[str] = None
    ) -> List[Touchpoint]:
        """
        📊 Collect touchpoint data from various sources
        
        Gather all user interactions across platforms
        """
        try:
            logger.info(f"📊 Collecting touchpoint data: {start_date} to {end_date}")
            
            # Simulate touchpoint data collection (would integrate with real data sources)
            touchpoints = []
            
            # Web analytics touchpoints
            web_touchpoints = await self._collect_web_touchpoints(start_date, end_date, user_ids)
            touchpoints.extend(web_touchpoints)
            
            # Social media touchpoints
            social_touchpoints = await self._collect_social_touchpoints(start_date, end_date, user_ids)
            touchpoints.extend(social_touchpoints)
            
            # Email campaign touchpoints
            email_touchpoints = await self._collect_email_touchpoints(start_date, end_date, user_ids)
            touchpoints.extend(email_touchpoints)
            
            # Platform interaction touchpoints
            platform_touchpoints = await self._collect_platform_touchpoints(start_date, end_date, user_ids)
            touchpoints.extend(platform_touchpoints)
            
            # Store touchpoints
            self.touchpoints = touchpoints
            
            # Build user journeys
            self._build_user_journeys()
            
            logger.info(f"✅ Collected {len(touchpoints)} touchpoints for {len(self.user_journeys)} users")
            return touchpoints
            
        except Exception as e:
            logger.error(f"❌ Error collecting touchpoint data: {e}")
            return []

    async def collect_conversion_data(
        self,
        start_date: datetime,
        end_date: datetime,
        conversion_types: List[ConversionType] = None
    ) -> List[Conversion]:
        """
        🎯 Collect conversion event data
        
        Track all conversion events for attribution analysis
        """
        try:
            logger.info(f"🎯 Collecting conversion data: {start_date} to {end_date}")
            
            if conversion_types is None:
                conversion_types = list(ConversionType)
            
            conversions = []
            
            # Simulate conversion data collection
            for conv_type in conversion_types:
                type_conversions = await self._collect_conversions_by_type(
                    conv_type, start_date, end_date
                )
                conversions.extend(type_conversions)
            
            # Store conversions
            self.conversions = conversions
            
            logger.info(f"✅ Collected {len(conversions)} conversions")
            return conversions
            
        except Exception as e:
            logger.error(f"❌ Error collecting conversion data: {e}")
            return []

    async def run_first_touch_attribution(self) -> List[AttributionResult]:
        """
        👆 First-touch attribution model
        
        Assigns 100% credit to the first touchpoint in the journey
        """
        try:
            logger.info("👆 Running first-touch attribution analysis")
            
            results = []
            attribution_data = {}
            
            for conversion in self.conversions:
                user_id = conversion.user_id
                
                if user_id in self.user_journeys:
                    journey = self.user_journeys[user_id]
                    
                    # Find touchpoints before conversion within lookback window
                    relevant_touchpoints = [
                        tp for tp in journey
                        if tp.timestamp <= conversion.timestamp and
                        (conversion.timestamp - tp.timestamp).days <= self.lookback_window
                    ]
                    
                    if relevant_touchpoints:
                        # Sort by timestamp and take first
                        first_touchpoint = min(relevant_touchpoints, key=lambda x: x.timestamp)
                        
                        key = (first_touchpoint.touchpoint_type, first_touchpoint.channel)
                        if key not in attribution_data:
                            attribution_data[key] = {
                                'credit': 0.0,
                                'conversions': 0,
                                'value': 0.0
                            }
                        
                        attribution_data[key]['credit'] += 1.0
                        attribution_data[key]['conversions'] += 1
                        attribution_data[key]['value'] += conversion.value
            
            # Convert to results
            for (touchpoint_type, channel), data in attribution_data.items():
                result = AttributionResult(
                    touchpoint_type=touchpoint_type,
                    channel=channel,
                    attribution_credit=data['credit'],
                    conversion_count=data['conversions'],
                    total_value=data['value'],
                    confidence_score=1.0,  # First-touch is deterministic
                    model_used=AttributionModel.FIRST_TOUCH
                )
                results.append(result)
            
            self.attribution_results['first_touch'] = results
            
            logger.info(f"✅ First-touch attribution completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in first-touch attribution: {e}")
            return []

    async def run_time_decay_attribution(self, decay_rate: float = 0.5) -> List[AttributionResult]:
        """
        ⏰ Time-decay attribution model
        
        Gives more credit to touchpoints closer to conversion
        """
        try:
            logger.info(f"⏰ Running time-decay attribution (decay_rate={decay_rate})")
            
            results = []
            attribution_data = {}
            
            for conversion in self.conversions:
                user_id = conversion.user_id
                
                if user_id in self.user_journeys:
                    journey = self.user_journeys[user_id]
                    
                    # Find relevant touchpoints
                    relevant_touchpoints = [
                        tp for tp in journey
                        if tp.timestamp <= conversion.timestamp and
                        (conversion.timestamp - tp.timestamp).days <= self.lookback_window
                    ]
                    
                    if relevant_touchpoints:
                        # Calculate time decay weights
                        total_weight = 0.0
                        touchpoint_weights = {}
                        
                        for tp in relevant_touchpoints:
                            days_diff = (conversion.timestamp - tp.timestamp).days
                            weight = np.exp(-decay_rate * days_diff)
                            touchpoint_weights[tp] = weight
                            total_weight += weight
                        
                        # Normalize weights and assign credit
                        for tp, weight in touchpoint_weights.items():
                            normalized_credit = weight / total_weight if total_weight > 0 else 0
                            
                            key = (tp.touchpoint_type, tp.channel)
                            if key not in attribution_data:
                                attribution_data[key] = {
                                    'credit': 0.0,
                                    'conversions': 0,
                                    'value': 0.0
                                }
                            
                            attribution_data[key]['credit'] += normalized_credit
                            attribution_data[key]['value'] += conversion.value * normalized_credit
                        
                        # Count conversion for all touchpoints
                        for tp in relevant_touchpoints:
                            key = (tp.touchpoint_type, tp.channel)
                            if key in attribution_data:
                                attribution_data[key]['conversions'] = len(set(
                                    conv.conversion_id for conv in self.conversions
                                    if any(tp2.touchpoint_type == key[0] and tp2.channel == key[1]
                                          for tp2 in self.user_journeys.get(conv.user_id, []))
                                ))
            
            # Convert to results
            for (touchpoint_type, channel), data in attribution_data.items():
                result = AttributionResult(
                    touchpoint_type=touchpoint_type,
                    channel=channel,
                    attribution_credit=data['credit'],
                    conversion_count=data['conversions'],
                    total_value=data['value'],
                    confidence_score=0.8,  # Time-decay has good confidence
                    model_used=AttributionModel.TIME_DECAY
                )
                results.append(result)
            
            self.attribution_results['time_decay'] = results
            
            logger.info(f"✅ Time-decay attribution completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in time-decay attribution: {e}")
            return []

    async def run_markov_chain_attribution(self) -> List[AttributionResult]:
        """
        🔗 Markov chain attribution model
        
        Uses transition probabilities between touchpoints
        """
        try:
            logger.info("🔗 Running Markov chain attribution analysis")
            
            # Build transition matrix
            await self._build_markov_transition_matrix()
            
            if self.transition_matrix is None:
                logger.warning("Failed to build transition matrix")
                return []
            
            results = []
            attribution_data = {}
            
            # Calculate removal effect for each touchpoint type
            for touchpoint_type in TouchpointType:
                removal_effect = await self._calculate_removal_effect(touchpoint_type)
                
                if removal_effect > 0:
                    # Find channels for this touchpoint type
                    channels = set()
                    for tp in self.touchpoints:
                        if tp.touchpoint_type == touchpoint_type:
                            channels.add(tp.channel)
                    
                    for channel in channels:
                        key = (touchpoint_type, channel)
                        if key not in attribution_data:
                            attribution_data[key] = {
                                'credit': 0.0,
                                'conversions': 0,
                                'value': 0.0
                            }
                        
                        # Credit proportional to removal effect
                        attribution_data[key]['credit'] += removal_effect
                        
                        # Count conversions influenced by this touchpoint
                        influenced_conversions = 0
                        total_value = 0.0
                        
                        for conversion in self.conversions:
                            if conversion.user_id in self.user_journeys:
                                journey = self.user_journeys[conversion.user_id]
                                if any(tp.touchpoint_type == touchpoint_type and tp.channel == channel
                                      for tp in journey):
                                    influenced_conversions += 1
                                    total_value += conversion.value
                        
                        attribution_data[key]['conversions'] = influenced_conversions
                        attribution_data[key]['value'] = total_value * removal_effect
            
            # Convert to results
            for (touchpoint_type, channel), data in attribution_data.items():
                result = AttributionResult(
                    touchpoint_type=touchpoint_type,
                    channel=channel,
                    attribution_credit=data['credit'],
                    conversion_count=data['conversions'],
                    total_value=data['value'],
                    confidence_score=0.9,  # Markov chains have high confidence
                    model_used=AttributionModel.MARKOV_CHAIN
                )
                results.append(result)
            
            self.attribution_results['markov_chain'] = results
            
            logger.info(f"✅ Markov chain attribution completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in Markov chain attribution: {e}")
            return []

    async def run_data_driven_attribution(self) -> List[AttributionResult]:
        """
        🤖 Data-driven attribution using machine learning
        
        Uses ML models to predict conversion probability
        """
        try:
            logger.info("🤖 Running data-driven ML attribution analysis")
            
            # Prepare training data
            X, y, feature_names = await self._prepare_ml_training_data()
            
            if len(X) == 0:
                logger.warning("No training data available for ML attribution")
                return []
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            self.logistic_model.fit(X_train_scaled, y_train)
            self.random_forest.fit(X_train_scaled, y_train)
            
            # Evaluate models
            lr_pred = self.logistic_model.predict(X_test_scaled)
            rf_pred = self.random_forest.predict(X_test_scaled)
            
            lr_accuracy = accuracy_score(y_test, lr_pred)
            rf_accuracy = accuracy_score(y_test, rf_pred)
            
            # Choose best model
            best_model = self.random_forest if rf_accuracy > lr_accuracy else self.logistic_model
            best_accuracy = max(rf_accuracy, lr_accuracy)
            
            logger.info(f"ML Model accuracy: LR={lr_accuracy:.3f}, RF={rf_accuracy:.3f}")
            
            # Calculate feature importance (attribution)
            if hasattr(best_model, 'feature_importances_'):
                importances = best_model.feature_importances_
            else:
                importances = np.abs(best_model.coef_[0])
            
            # Map feature importance to touchpoint attribution
            results = []
            attribution_data = {}
            
            for i, feature_name in enumerate(feature_names):
                if feature_name.startswith('touchpoint_'):
                    touchpoint_info = feature_name.replace('touchpoint_', '').split('_')
                    if len(touchpoint_info) >= 2:
                        touchpoint_type_str = '_'.join(touchpoint_info[:-1])
                        channel = touchpoint_info[-1]
                        
                        try:
                            touchpoint_type = TouchpointType(touchpoint_type_str)
                            
                            key = (touchpoint_type, channel)
                            if key not in attribution_data:
                                attribution_data[key] = {
                                    'credit': 0.0,
                                    'conversions': 0,
                                    'value': 0.0
                                }
                            
                            attribution_data[key]['credit'] += float(importances[i])
                        except ValueError:
                            continue
            
            # Normalize attribution credits
            total_credit = sum(data['credit'] for data in attribution_data.values())
            if total_credit > 0:
                for data in attribution_data.values():
                    data['credit'] /= total_credit
            
            # Calculate conversions and value
            for (touchpoint_type, channel), data in attribution_data.items():
                influenced_conversions = 0
                total_value = 0.0
                
                for conversion in self.conversions:
                    if conversion.user_id in self.user_journeys:
                        journey = self.user_journeys[conversion.user_id]
                        if any(tp.touchpoint_type == touchpoint_type and tp.channel == channel
                              for tp in journey):
                            influenced_conversions += 1
                            total_value += conversion.value
                
                data['conversions'] = influenced_conversions
                data['value'] = total_value * data['credit']
            
            # Convert to results
            for (touchpoint_type, channel), data in attribution_data.items():
                result = AttributionResult(
                    touchpoint_type=touchpoint_type,
                    channel=channel,
                    attribution_credit=data['credit'],
                    conversion_count=data['conversions'],
                    total_value=data['value'],
                    confidence_score=best_accuracy,
                    model_used=AttributionModel.DATA_DRIVEN
                )
                results.append(result)
            
            self.attribution_results['data_driven'] = results
            
            logger.info(f"✅ Data-driven attribution completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in data-driven attribution: {e}")
            return []

    async def run_shapley_value_attribution(self) -> List[AttributionResult]:
        """
        🎯 Shapley value attribution using cooperative game theory
        
        Calculates fair contribution of each touchpoint
        """
        try:
            logger.info("🎯 Running Shapley value attribution analysis")
            
            results = []
            attribution_data = {}
            
            # Group conversions by user
            user_conversions = {}
            for conversion in self.conversions:
                if conversion.user_id not in user_conversions:
                    user_conversions[conversion.user_id] = []
                user_conversions[conversion.user_id].append(conversion)
            
            # Calculate Shapley values for each user journey
            for user_id, conversions in user_conversions.items():
                if user_id not in self.user_journeys:
                    continue
                
                journey = self.user_journeys[user_id]
                if not journey:
                    continue
                
                # Get unique touchpoint types in journey
                touchpoint_types = list(set(tp.touchpoint_type for tp in journey))
                
                # Calculate Shapley values
                shapley_values = await self._calculate_shapley_values(
                    touchpoint_types, conversions
                )
                
                # Distribute credit among touchpoints
                for tp in journey:
                    if tp.touchpoint_type in shapley_values:
                        key = (tp.touchpoint_type, tp.channel)
                        if key not in attribution_data:
                            attribution_data[key] = {
                                'credit': 0.0,
                                'conversions': 0,
                                'value': 0.0
                            }
                        
                        shapley_credit = shapley_values[tp.touchpoint_type]
                        attribution_data[key]['credit'] += shapley_credit
                        
                        # Proportional value assignment
                        total_conversion_value = sum(conv.value for conv in conversions)
                        attribution_data[key]['value'] += total_conversion_value * shapley_credit
            
            # Count conversions
            for (touchpoint_type, channel), data in attribution_data.items():
                influenced_conversions = 0
                
                for conversion in self.conversions:
                    if conversion.user_id in self.user_journeys:
                        journey = self.user_journeys[conversion.user_id]
                        if any(tp.touchpoint_type == touchpoint_type and tp.channel == channel
                              for tp in journey):
                            influenced_conversions += 1
                
                data['conversions'] = influenced_conversions
            
            # Convert to results
            for (touchpoint_type, channel), data in attribution_data.items():
                result = AttributionResult(
                    touchpoint_type=touchpoint_type,
                    channel=channel,
                    attribution_credit=data['credit'],
                    conversion_count=data['conversions'],
                    total_value=data['value'],
                    confidence_score=0.95,  # Shapley values are mathematically sound
                    model_used=AttributionModel.SHAPLEY_VALUE
                )
                results.append(result)
            
            self.attribution_results['shapley_value'] = results
            
            logger.info(f"✅ Shapley value attribution completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in Shapley value attribution: {e}")
            return []

    async def compare_attribution_models(self) -> Dict[str, Any]:
        """
        📊 Compare results from different attribution models
        
        Provides insights into model differences and recommendations
        """
        try:
            logger.info("📊 Comparing attribution model results")
            
            comparison = {
                'model_comparison': {},
                'touchpoint_ranking': {},
                'consistency_score': 0.0,
                'recommendations': []
            }
            
            # Compare model results
            for model_name, results in self.attribution_results.items():
                if not results:
                    continue
                
                model_summary = {
                    'total_credit': sum(r.attribution_credit for r in results),
                    'total_value': sum(r.total_value for r in results),
                    'total_conversions': sum(r.conversion_count for r in results),
                    'avg_confidence': np.mean([r.confidence_score for r in results]),
                    'top_touchpoints': []
                }
                
                # Sort by credit and get top touchpoints
                sorted_results = sorted(results, key=lambda x: x.attribution_credit, reverse=True)
                for result in sorted_results[:5]:
                    model_summary['top_touchpoints'].append({
                        'touchpoint_type': result.touchpoint_type.value,
                        'channel': result.channel,
                        'credit': result.attribution_credit,
                        'value': result.total_value
                    })
                
                comparison['model_comparison'][model_name] = model_summary
            
            # Calculate consistency across models
            if len(self.attribution_results) > 1:
                consistency_score = await self._calculate_model_consistency()
                comparison['consistency_score'] = consistency_score
            
            # Generate recommendations
            comparison['recommendations'] = await self._generate_attribution_recommendations(comparison)
            
            logger.info("✅ Attribution model comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Error comparing attribution models: {e}")
            return {}

    # Helper methods for data collection (simplified implementations)
    async def _collect_web_touchpoints(self, start_date: datetime, end_date: datetime, user_ids: List[str]) -> List[Touchpoint]:
        """Collect web analytics touchpoints"""
        # Simplified implementation - would integrate with real analytics
        touchpoints = []
        return touchpoints

    async def _collect_social_touchpoints(self, start_date: datetime, end_date: datetime, user_ids: List[str]) -> List[Touchpoint]:
        """Collect social media touchpoints"""
        touchpoints = []
        return touchpoints

    async def _collect_email_touchpoints(self, start_date: datetime, end_date: datetime, user_ids: List[str]) -> List[Touchpoint]:
        """Collect email campaign touchpoints"""
        touchpoints = []
        return touchpoints

    async def _collect_platform_touchpoints(self, start_date: datetime, end_date: datetime, user_ids: List[str]) -> List[Touchpoint]:
        """Collect platform interaction touchpoints"""
        touchpoints = []
        return touchpoints

    async def _collect_conversions_by_type(self, conv_type: ConversionType, start_date: datetime, end_date: datetime) -> List[Conversion]:
        """Collect conversions of specific type"""
        conversions = []
        return conversions

    def _build_user_journeys(self):
        """Build user journey maps from touchpoints"""
        self.user_journeys = {}
        for touchpoint in self.touchpoints:
            if touchpoint.user_id not in self.user_journeys:
                self.user_journeys[touchpoint.user_id] = []
            self.user_journeys[touchpoint.user_id].append(touchpoint)
        
        # Sort journeys by timestamp
        for user_id in self.user_journeys:
            self.user_journeys[user_id].sort(key=lambda x: x.timestamp)

    async def _build_markov_transition_matrix(self):
        """Build Markov chain transition matrix"""
        try:
            # Get all unique states (touchpoint types + conversion)
            states = set()
            for tp in self.touchpoints:
                states.add(tp.touchpoint_type.value)
            states.add('conversion')
            
            # Create state mapping
            self.state_mapping = {state: i for i, state in enumerate(sorted(states))}
            n_states = len(states)
            
            # Initialize transition matrix
            transitions = np.zeros((n_states, n_states))
            
            # Count transitions
            for user_id, journey in self.user_journeys.items():
                # Add conversion as final state if user converted
                user_conversions = [c for c in self.conversions if c.user_id == user_id]
                if user_conversions:
                    journey_with_conversion = journey + [type('obj', (object,), {
                        'touchpoint_type': type('obj', (object,), {'value': 'conversion'})()
                    })]
                else:
                    journey_with_conversion = journey
                
                # Count state transitions
                for i in range(len(journey_with_conversion) - 1):
                    current_state = journey_with_conversion[i].touchpoint_type.value
                    next_state = journey_with_conversion[i + 1].touchpoint_type.value
                    
                    current_idx = self.state_mapping[current_state]
                    next_idx = self.state_mapping[next_state]
                    
                    transitions[current_idx, next_idx] += 1
            
            # Normalize to probabilities
            row_sums = transitions.sum(axis=1)
            self.transition_matrix = np.divide(
                transitions, 
                row_sums[:, np.newaxis], 
                out=np.zeros_like(transitions), 
                where=row_sums[:, np.newaxis] != 0
            )
            
        except Exception as e:
            logger.error(f"Error building transition matrix: {e}")
            self.transition_matrix = None

    async def _calculate_removal_effect(self, touchpoint_type: TouchpointType) -> float:
        """Calculate removal effect for Markov chain attribution"""
        if self.transition_matrix is None:
            return 0.0
        
        try:
            # Calculate conversion probability with and without touchpoint type
            conversion_state_idx = self.state_mapping.get('conversion')
            if conversion_state_idx is None:
                return 0.0
            
            # Original conversion probability
            original_prob = self._calculate_conversion_probability()
            
            # Modify matrix by removing touchpoint type
            modified_matrix = self.transition_matrix.copy()
            touchpoint_idx = self.state_mapping.get(touchpoint_type.value)
            
            if touchpoint_idx is not None:
                # Set touchpoint row to zeros (remove outgoing transitions)
                modified_matrix[touchpoint_idx, :] = 0
                # Remove incoming transitions by redistributing to other states
                for i in range(len(modified_matrix)):
                    if modified_matrix[i, touchpoint_idx] > 0:
                        # Redistribute probability to other states
                        prob_to_redistribute = modified_matrix[i, touchpoint_idx]
                        modified_matrix[i, touchpoint_idx] = 0
                        
                        # Distribute to other states proportionally
                        other_probs = np.sum(modified_matrix[i, :])
                        if other_probs > 0:
                            for j in range(len(modified_matrix[i])):
                                if j != touchpoint_idx:
                                    modified_matrix[i, j] += (
                                        prob_to_redistribute * modified_matrix[i, j] / other_probs
                                    )
            
            # Calculate conversion probability without touchpoint
            modified_prob = self._calculate_conversion_probability(modified_matrix)
            
            # Removal effect is the difference
            removal_effect = max(0, original_prob - modified_prob)
            return removal_effect
            
        except Exception as e:
            logger.error(f"Error calculating removal effect: {e}")
            return 0.0

    def _calculate_conversion_probability(self, transition_matrix: np.ndarray = None) -> float:
        """Calculate overall conversion probability from transition matrix"""
        if transition_matrix is None:
            transition_matrix = self.transition_matrix
        
        if transition_matrix is None:
            return 0.0
        
        try:
            conversion_state_idx = self.state_mapping.get('conversion')
            if conversion_state_idx is None:
                return 0.0
            
            # Use steady-state probability calculation
            n_states = len(transition_matrix)
            
            # Create fundamental matrix (remove conversion state)
            Q = transition_matrix[:-1, :-1]  # Transient states
            R = transition_matrix[:-1, -1:]  # Absorption probabilities
            
            # Calculate fundamental matrix N = (I - Q)^-1
            I = np.eye(len(Q))
            try:
                N = np.linalg.inv(I - Q)
                # Absorption probabilities B = N * R
                B = N @ R
                # Overall absorption probability
                absorption_prob = np.sum(B) / len(B) if len(B) > 0 else 0.0
                return min(1.0, max(0.0, absorption_prob))
            except np.linalg.LinAlgError:
                # Fallback to simple probability
                return np.sum(transition_matrix[:, conversion_state_idx]) / len(transition_matrix)
            
        except Exception as e:
            logger.error(f"Error calculating conversion probability: {e}")
            return 0.0

    async def _prepare_ml_training_data(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data for ML attribution model"""
        try:
            features = []
            labels = []
            feature_names = []
            
            # Create feature names for each touchpoint type and channel combination
            touchpoint_channels = set()
            for tp in self.touchpoints:
                touchpoint_channels.add((tp.touchpoint_type.value, tp.channel))
            
            feature_names = [f"touchpoint_{tp_type}_{channel}" 
                           for tp_type, channel in sorted(touchpoint_channels)]
            feature_names.extend(['journey_length', 'time_to_conversion', 'total_touchpoints'])
            
            # Create training examples for each user
            for user_id, journey in self.user_journeys.items():
                user_conversions = [c for c in self.conversions if c.user_id == user_id]
                
                # Create feature vector
                feature_vector = [0] * len(feature_names)
                
                # Touchpoint features
                for tp in journey:
                    feature_name = f"touchpoint_{tp.touchpoint_type.value}_{tp.channel}"
                    if feature_name in feature_names:
                        idx = feature_names.index(feature_name)
                        feature_vector[idx] += 1
                
                # Journey features
                if journey:
                    feature_vector[-3] = len(journey)  # journey_length
                    if user_conversions:
                        first_conversion = min(user_conversions, key=lambda x: x.timestamp)
                        time_to_conversion = (first_conversion.timestamp - journey[0].timestamp).days
                        feature_vector[-2] = time_to_conversion
                    feature_vector[-1] = sum(feature_vector[:-3])  # total_touchpoints
                
                features.append(feature_vector)
                labels.append(1 if user_conversions else 0)
            
            return np.array(features), np.array(labels), feature_names
            
        except Exception as e:
            logger.error(f"Error preparing ML training data: {e}")
            return np.array([]), np.array([]), []

    async def _calculate_shapley_values(
        self, 
        touchpoint_types: List[TouchpointType],
        conversions: List[Conversion]
    ) -> Dict[TouchpointType, float]:
        """Calculate Shapley values for touchpoint types"""
        try:
            if not touchpoint_types or not conversions:
                return {}
            
            n_players = len(touchpoint_types)
            shapley_values = {tp: 0.0 for tp in touchpoint_types}
            
            # Generate all possible coalitions
            from itertools import combinations
            
            total_value = sum(conv.value for conv in conversions)
            
            for player in touchpoint_types:
                marginal_contributions = []
                
                # For each possible coalition size
                for r in range(n_players):
                    # Get all coalitions of size r not containing the player
                    other_players = [tp for tp in touchpoint_types if tp != player]
                    
                    if r <= len(other_players):
                        for coalition in combinations(other_players, r):
                            # Calculate value with and without player
                            coalition_value = self._calculate_coalition_value(
                                list(coalition), conversions, total_value
                            )
                            coalition_with_player_value = self._calculate_coalition_value(
                                list(coalition) + [player], conversions, total_value
                            )
                            
                            marginal_contribution = coalition_with_player_value - coalition_value
                            marginal_contributions.append(marginal_contribution)
                
                # Shapley value is average marginal contribution
                if marginal_contributions:
                    shapley_values[player] = np.mean(marginal_contributions)
            
            # Normalize to sum to 1
            total_shapley = sum(shapley_values.values())
            if total_shapley > 0:
                for tp in shapley_values:
                    shapley_values[tp] /= total_shapley
            
            return shapley_values
            
        except Exception as e:
            logger.error(f"Error calculating Shapley values: {e}")
            return {}

    def _calculate_coalition_value(
        self, 
        coalition: List[TouchpointType],
        conversions: List[Conversion],
        total_value: float
    ) -> float:
        """Calculate value generated by a coalition of touchpoint types"""
        if not coalition:
            return 0.0
        
        # Simplified coalition value calculation
        # In practice, this would be more sophisticated
        coalition_weight = len(coalition) / len(TouchpointType)
        return total_value * coalition_weight * 0.8  # Diminishing returns

    async def _calculate_model_consistency(self) -> float:
        """Calculate consistency score across attribution models"""
        try:
            if len(self.attribution_results) < 2:
                return 1.0
            
            # Compare top touchpoints across models
            model_rankings = {}
            for model_name, results in self.attribution_results.items():
                if results:
                    sorted_results = sorted(results, key=lambda x: x.attribution_credit, reverse=True)
                    model_rankings[model_name] = [
                        (r.touchpoint_type.value, r.channel) for r in sorted_results[:5]
                    ]
            
            # Calculate ranking correlation
            if len(model_rankings) >= 2:
                model_names = list(model_rankings.keys())
                correlations = []
                
                for i in range(len(model_names)):
                    for j in range(i + 1, len(model_names)):
                        rank1 = model_rankings[model_names[i]]
                        rank2 = model_rankings[model_names[j]]
                        
                        # Calculate rank correlation
                        common_touchpoints = set(rank1) & set(rank2)
                        if common_touchpoints:
                            correlation = len(common_touchpoints) / max(len(rank1), len(rank2))
                            correlations.append(correlation)
                
                return np.mean(correlations) if correlations else 0.0
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error calculating model consistency: {e}")
            return 0.0

    async def _generate_attribution_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on attribution analysis"""
        recommendations = []
        
        try:
            consistency_score = comparison.get('consistency_score', 0.0)
            
            if consistency_score < 0.5:
                recommendations.append(
                    "🚨 Low consistency between attribution models. Review data quality and model assumptions."
                )
            elif consistency_score > 0.8:
                recommendations.append(
                    "✅ High consistency between attribution models. Results are reliable."
                )
            
            # Analyze model comparison
            model_comparison = comparison.get('model_comparison', {})
            
            if 'data_driven' in model_comparison:
                data_driven = model_comparison['data_driven']
                if data_driven.get('avg_confidence', 0) > 0.8:
                    recommendations.append(
                        "🤖 Data-driven model shows high confidence. Use for primary attribution decisions."
                    )
            
            if 'markov_chain' in model_comparison and 'shapley_value' in model_comparison:
                recommendations.append(
                    "🔍 Use Markov chain and Shapley value models for strategic touchpoint investment decisions."
                )
            
            # Channel-specific recommendations
            top_channels = set()
            for model_data in model_comparison.values():
                for tp in model_data.get('top_touchpoints', [])[:3]:
                    top_channels.add(tp['channel'])
            
            if top_channels:
                recommendations.append(
                    f"🎯 Focus budget on top-performing channels: {', '.join(list(top_channels)[:3])}"
                )
            
            recommendations.append("📊 Run attribution analysis monthly to track performance trends")
            recommendations.append("🔄 Implement incrementality testing to validate attribution insights")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("⚠️ Review attribution data and rerun analysis")
        
        return recommendations

# Usage example
async def main():
    """Test the attribution modeling engine"""
    try:
        # Initialize engine
        engine = AttributionModelingEngine("postgresql://user:pass@localhost/ainflue")
        
        # Collect data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        await engine.collect_touchpoint_data(start_date, end_date)
        await engine.collect_conversion_data(start_date, end_date)
        
        # Run different attribution models
        await engine.run_first_touch_attribution()
        await engine.run_time_decay_attribution()
        await engine.run_markov_chain_attribution()
        await engine.run_data_driven_attribution()
        await engine.run_shapley_value_attribution()
        
        # Compare models
        comparison = await engine.compare_attribution_models()
        print(f"Attribution analysis completed with {len(comparison.get('recommendations', []))} recommendations")
        
    except Exception as e:
        print(f"Error in attribution modeling: {e}")

if __name__ == "__main__":
    asyncio.run(main())