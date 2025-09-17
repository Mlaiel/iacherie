"""
Creator Error Impact Assessment Platform - Enterprise Creator Economy Platform
Advanced platform for assessing and quantifying error impact on creators

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
from decimal import Decimal

logger = logging.getLogger(__name__)


class ImpactCategory(Enum):
    """Catégories impact erreur"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REPUTATION = "reputation"
    USER_EXPERIENCE = "user_experience"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    PLATFORM_REACH = "platform_reach"


class ImpactSeverity(Enum):
    """Niveaux sévérité impact"""
    NEGLIGIBLE = "negligible"     # 0-5%
    MINOR = "minor"               # 5-15%
    MODERATE = "moderate"         # 15-30%
    SIGNIFICANT = "significant"   # 30-50%
    SEVERE = "severe"             # 50-75%
    CRITICAL = "critical"         # 75-100%


class RecoveryStatus(Enum):
    """Statuts récupération"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    MONITORING = "monitoring"


@dataclass
class ImpactMetric:
    """Métrique impact spécifique"""
    metric_name: str
    category: ImpactCategory
    baseline_value: float
    impact_value: float
    percentage_change: float
    severity: ImpactSeverity
    measurement_unit: str
    confidence_level: float
    recovery_target: Optional[float] = None
    recovery_deadline: Optional[datetime] = None


@dataclass
class ErrorImpactAssessment:
    """Assessment complet impact erreur"""
    assessment_id: str
    creator_id: str
    error_id: str
    error_type: str
    error_timestamp: datetime
    assessment_timestamp: datetime
    impact_metrics: List[ImpactMetric]
    overall_severity: ImpactSeverity
    estimated_recovery_time_hours: Optional[float]
    financial_impact_usd: Decimal
    reputation_score_change: float
    user_experience_impact: float
    mitigation_actions: List[str]
    recovery_plan: Dict[str, Any]
    lessons_learned: List[str]
    prevention_recommendations: List[str]


@dataclass
class CreatorProfile:
    """Profil créateur pour assessment"""
    creator_id: str
    creator_tier: str
    specialization: str
    baseline_metrics: Dict[str, float]
    historical_performance: Dict[str, List[float]]
    risk_factors: List[str]
    resilience_score: float
    recovery_capability: float


@dataclass
class RecoveryProgress:
    """Progression récupération"""
    assessment_id: str
    recovery_status: RecoveryStatus
    start_time: datetime
    target_completion: datetime
    current_progress_percentage: float
    completed_actions: List[str]
    pending_actions: List[str]
    obstacles_encountered: List[str]
    updated_eta: Optional[datetime] = None


class CreatorErrorImpactAssessmentPlatform:
    """
    📈 PLATEFORME ÉVALUATION IMPACT ERREURS CRÉATEURS ENTERPRISE
    
    Architecture assessment Backend Senior avec:
    - Évaluation impact multi-dimensionnelle
    - Quantification financière précise  
    - Plans récupération intelligents
    - Monitoring progression temps réel
    """
    
    def __init__(self):
        """Initialize Creator Error Impact Assessment Platform"""
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.impact_assessments: Dict[str, ErrorImpactAssessment] = {}
        self.recovery_progress: Dict[str, RecoveryProgress] = {}
        self.baseline_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.impact_templates: Dict[str, Dict[str, Any]] = {}
        self.assessment_cache: Dict[str, Any] = {}
        
        # Configuration plateforme assessment
        self.config = {
            'assessment_window_hours': 72,  # 3 days post-error
            'baseline_calculation_days': 30,
            'recovery_monitoring_days': 14,
            'confidence_threshold': 0.7,
            'significant_impact_threshold': 0.15,  # 15%
            'financial_impact_threshold': 100.0,  # $100
            'auto_recovery_tracking': True,
            'real_time_monitoring': True,
            'ml_impact_prediction': True
        }
        
        # Initialize impact calculation methods
        self.impact_calculators = {
            ImpactCategory.FINANCIAL: self._calculate_financial_impact,
            ImpactCategory.OPERATIONAL: self._calculate_operational_impact,
            ImpactCategory.REPUTATION: self._calculate_reputation_impact,
            ImpactCategory.USER_EXPERIENCE: self._calculate_ux_impact,
            ImpactCategory.CONTENT_QUALITY: self._calculate_content_quality_impact,
            ImpactCategory.ENGAGEMENT: self._calculate_engagement_impact,
            ImpactCategory.COLLABORATION: self._calculate_collaboration_impact,
            ImpactCategory.PLATFORM_REACH: self._calculate_platform_reach_impact
        }
        
        # Initialize recovery strategies
        self.recovery_strategies = {
            'financial': self._create_basic_recovery_plan,
            'operational': self._create_basic_recovery_plan,
            'reputation': self._create_basic_recovery_plan,
            'engagement': self._create_basic_recovery_plan
        }
        
        logger.info("Creator Error Impact Assessment Platform initialized")
    
    async def create_creator_profile(self,
                                   creator_id: str,
                                   creator_tier: str,
                                   specialization: str,
                                   baseline_data: Dict[str, Any]) -> CreatorProfile:
        """
        Create comprehensive creator profile for impact assessment
        
        Args:
            creator_id: ID créateur
            creator_tier: Tier créateur
            specialization: Spécialisation
            baseline_data: Données baseline
            
        Returns:
            Creator profile
        """
        try:
            # Calculate baseline metrics
            baseline_metrics = await self._calculate_baseline_metrics(creator_id, baseline_data)
            
            # Calculate historical performance
            historical_performance = await self._calculate_historical_performance(creator_id, baseline_data)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(creator_id, baseline_data)
            
            # Calculate resilience score
            resilience_score = await self._calculate_resilience_score(creator_id, baseline_data)
            
            # Calculate recovery capability
            recovery_capability = await self._calculate_recovery_capability(creator_id, baseline_data)
            
            # Create profile
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_tier=creator_tier,
                specialization=specialization,
                baseline_metrics=baseline_metrics,
                historical_performance=historical_performance,
                risk_factors=risk_factors,
                resilience_score=resilience_score,
                recovery_capability=recovery_capability
            )
            
            self.creator_profiles[creator_id] = profile
            
            logger.info(f"Creator profile created: {creator_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating creator profile: {e}")
            raise
    
    async def assess_error_impact(self,
                                creator_id: str,
                                error_id: str,
                                error_type: str,
                                error_timestamp: datetime,
                                error_data: Dict[str, Any],
                                current_metrics: Dict[str, float]) -> ErrorImpactAssessment:
        """
        Assess comprehensive impact of error on creator
        
        Args:
            creator_id: ID créateur
            error_id: ID erreur
            error_type: Type erreur
            error_timestamp: Timestamp erreur
            error_data: Données erreur
            current_metrics: Métriques actuelles
            
        Returns:
            Error impact assessment
        """
        try:
            # Get or create creator profile
            if creator_id not in self.creator_profiles:
                # Create basic profile with current data
                await self.create_creator_profile(
                    creator_id, "intermediate", "general", {"current": current_metrics}
                )
            
            profile = self.creator_profiles[creator_id]
            
            # Calculate impact metrics for each category
            impact_metrics = []
            
            for category in ImpactCategory:
                calculator = self.impact_calculators.get(category)
                if calculator:
                    category_metrics = await calculator(
                        profile, error_data, current_metrics, error_type
                    )
                    impact_metrics.extend(category_metrics)
            
            # Calculate overall severity
            overall_severity = self._calculate_overall_severity(impact_metrics)
            
            # Estimate recovery time
            recovery_time = await self._estimate_recovery_time(
                profile, impact_metrics, error_type
            )
            
            # Calculate financial impact
            financial_impact = await self._calculate_total_financial_impact(impact_metrics)
            
            # Calculate reputation score change
            reputation_change = self._calculate_reputation_change(impact_metrics)
            
            # Calculate UX impact
            ux_impact = self._calculate_ux_impact_score(impact_metrics)
            
            # Generate mitigation actions
            mitigation_actions = await self._generate_mitigation_actions(
                impact_metrics, error_type, profile
            )
            
            # Create recovery plan
            recovery_plan = await self._create_recovery_plan(
                profile, impact_metrics, error_type
            )
            
            # Generate lessons learned
            lessons_learned = await self._generate_lessons_learned(
                impact_metrics, error_type
            )
            
            # Generate prevention recommendations
            prevention_recommendations = await self._generate_prevention_recommendations(
                profile, impact_metrics, error_type
            )
            
            # Create assessment
            assessment_id = f"assessment_{creator_id}_{error_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            assessment = ErrorImpactAssessment(
                assessment_id=assessment_id,
                creator_id=creator_id,
                error_id=error_id,
                error_type=error_type,
                error_timestamp=error_timestamp,
                assessment_timestamp=datetime.utcnow(),
                impact_metrics=impact_metrics,
                overall_severity=overall_severity,
                estimated_recovery_time_hours=recovery_time,
                financial_impact_usd=financial_impact,
                reputation_score_change=reputation_change,
                user_experience_impact=ux_impact,
                mitigation_actions=mitigation_actions,
                recovery_plan=recovery_plan,
                lessons_learned=lessons_learned,
                prevention_recommendations=prevention_recommendations
            )
            
            self.impact_assessments[assessment_id] = assessment
            
            # Start recovery tracking if significant impact
            if overall_severity in [ImpactSeverity.SIGNIFICANT, ImpactSeverity.SEVERE, ImpactSeverity.CRITICAL]:
                await self._start_recovery_tracking(assessment)
            
            logger.info(f"Impact assessment completed: {assessment_id} - Severity: {overall_severity.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing error impact: {e}")
            raise
    
    async def _calculate_baseline_metrics(self,
                                        creator_id: str,
                                        baseline_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate baseline metrics for creator"""
        try:
            baseline_metrics = {}
            
            # Standard metrics with default values
            standard_metrics = {
                'daily_views': 1000.0,
                'engagement_rate': 0.05,
                'daily_revenue': 50.0,
                'upload_frequency': 1.0,
                'content_quality_score': 7.5,
                'follower_count': 5000.0,
                'collaboration_count': 2.0,
                'platform_reach': 3.0
            }
            
            # Use provided data or defaults
            current_data = baseline_data.get('current', {})
            
            for metric_name, default_value in standard_metrics.items():
                baseline_metrics[metric_name] = float(current_data.get(metric_name, default_value))
            
            return baseline_metrics
            
        except Exception as e:
            logger.error(f"Error calculating baseline metrics: {e}")
            return {}
    
    async def _calculate_historical_performance(self,
                                              creator_id: str,
                                              baseline_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Calculate historical performance trends"""
        try:
            historical_performance = {}
            
            # Generate sample historical data if not provided
            baseline_metrics = await self._calculate_baseline_metrics(creator_id, baseline_data)
            
            for metric_name, baseline_value in baseline_metrics.items():
                # Generate 30 days of synthetic historical data
                historical_values = []
                for day in range(30):
                    # Add some variance around baseline (±20%)
                    variance = (day % 7 - 3) * 0.05  # Weekly pattern
                    noise = (hash(f"{creator_id}_{metric_name}_{day}") % 100 - 50) * 0.002  # Random noise
                    
                    value = baseline_value * (1 + variance + noise)
                    historical_values.append(max(0, value))
                
                historical_performance[metric_name] = historical_values
            
            return historical_performance
            
        except Exception as e:
            logger.error(f"Error calculating historical performance: {e}")
            return {}
    
    async def _identify_risk_factors(self,
                                   creator_id: str,
                                   baseline_data: Dict[str, Any]) -> List[str]:
        """Identify creator risk factors"""
        try:
            risk_factors = []
            baseline_metrics = await self._calculate_baseline_metrics(creator_id, baseline_data)
            
            # Check for low engagement
            if baseline_metrics.get('engagement_rate', 0.05) < 0.02:
                risk_factors.append("Low engagement rate")
            
            # Check for irregular upload schedule
            if baseline_metrics.get('upload_frequency', 1.0) < 0.5:
                risk_factors.append("Irregular content schedule")
            
            # Check for low content quality
            if baseline_metrics.get('content_quality_score', 7.5) < 6.0:
                risk_factors.append("Content quality concerns")
            
            # Check for limited platform reach
            if baseline_metrics.get('platform_reach', 3.0) < 2.0:
                risk_factors.append("Limited platform diversity")
            
            # Check for low collaboration
            if baseline_metrics.get('collaboration_count', 2.0) < 1.0:
                risk_factors.append("Limited collaboration network")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
            return []
    
    async def _calculate_resilience_score(self,
                                        creator_id: str,
                                        baseline_data: Dict[str, Any]) -> float:
        """Calculate creator resilience score"""
        try:
            baseline_metrics = await self._calculate_baseline_metrics(creator_id, baseline_data)
            historical_performance = await self._calculate_historical_performance(creator_id, baseline_data)
            
            resilience_factors = []
            
            # Content consistency
            upload_frequency = baseline_metrics.get('upload_frequency', 1.0)
            resilience_factors.append(min(upload_frequency / 2.0, 1.0))
            
            # Engagement stability
            engagement_history = historical_performance.get('engagement_rate', [0.05] * 30)
            engagement_stability = 1.0 - (statistics.stdev(engagement_history) / statistics.mean(engagement_history))
            resilience_factors.append(max(0, engagement_stability))
            
            # Platform diversification
            platform_reach = baseline_metrics.get('platform_reach', 3.0)
            resilience_factors.append(min(platform_reach / 5.0, 1.0))
            
            # Content quality
            quality_score = baseline_metrics.get('content_quality_score', 7.5)
            resilience_factors.append(quality_score / 10.0)
            
            # Collaboration network
            collaboration_count = baseline_metrics.get('collaboration_count', 2.0)
            resilience_factors.append(min(collaboration_count / 5.0, 1.0))
            
            return statistics.mean(resilience_factors)
            
        except Exception as e:
            logger.error(f"Error calculating resilience score: {e}")
            return 0.5
    
    async def _calculate_recovery_capability(self,
                                           creator_id: str,
                                           baseline_data: Dict[str, Any]) -> float:
        """Calculate creator recovery capability"""
        try:
            baseline_metrics = await self._calculate_baseline_metrics(creator_id, baseline_data)
            
            recovery_factors = []
            
            # Audience size (larger = faster recovery)
            follower_count = baseline_metrics.get('follower_count', 5000.0)
            audience_factor = min(follower_count / 100000.0, 1.0)  # Normalize to 100K followers
            recovery_factors.append(audience_factor)
            
            # Revenue stability
            daily_revenue = baseline_metrics.get('daily_revenue', 50.0)
            revenue_factor = min(daily_revenue / 500.0, 1.0)  # Normalize to $500/day
            recovery_factors.append(revenue_factor)
            
            # Content quality
            quality_score = baseline_metrics.get('content_quality_score', 7.5)
            recovery_factors.append(quality_score / 10.0)
            
            # Platform presence
            platform_reach = baseline_metrics.get('platform_reach', 3.0)
            platform_factor = min(platform_reach / 5.0, 1.0)
            recovery_factors.append(platform_factor)
            
            return statistics.mean(recovery_factors)
            
        except Exception as e:
            logger.error(f"Error calculating recovery capability: {e}")
            return 0.5
    
    async def _calculate_financial_impact(self,
                                        profile: CreatorProfile,
                                        error_data: Dict[str, Any],
                                        current_metrics: Dict[str, float],
                                        error_type: str) -> List[ImpactMetric]:
        """Calculate financial impact metrics"""
        try:
            metrics = []
            
            # Daily revenue impact
            baseline_revenue = profile.baseline_metrics.get('daily_revenue', 50.0)
            current_revenue = current_metrics.get('daily_revenue', baseline_revenue)
            
            revenue_change = (current_revenue - baseline_revenue) / baseline_revenue if baseline_revenue > 0 else 0
            revenue_severity = self._determine_severity(abs(revenue_change))
            
            metrics.append(ImpactMetric(
                metric_name="daily_revenue",
                category=ImpactCategory.FINANCIAL,
                baseline_value=baseline_revenue,
                impact_value=current_revenue,
                percentage_change=revenue_change,
                severity=revenue_severity,
                measurement_unit="USD",
                confidence_level=0.85,
                recovery_target=baseline_revenue * 0.95,
                recovery_deadline=datetime.utcnow() + timedelta(days=7)
            ))
            
            # Monetization efficiency impact
            baseline_efficiency = profile.baseline_metrics.get('monetization_efficiency', 0.05)
            current_efficiency = current_metrics.get('monetization_efficiency', baseline_efficiency)
            
            efficiency_change = (current_efficiency - baseline_efficiency) / baseline_efficiency if baseline_efficiency > 0 else 0
            efficiency_severity = self._determine_severity(abs(efficiency_change))
            
            metrics.append(ImpactMetric(
                metric_name="monetization_efficiency",
                category=ImpactCategory.FINANCIAL,
                baseline_value=baseline_efficiency,
                impact_value=current_efficiency,
                percentage_change=efficiency_change,
                severity=efficiency_severity,
                measurement_unit="ratio",
                confidence_level=0.75
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating financial impact: {e}")
            return []
    
    async def _calculate_operational_impact(self,
                                          profile: CreatorProfile,
                                          error_data: Dict[str, Any],
                                          current_metrics: Dict[str, float],
                                          error_type: str) -> List[ImpactMetric]:
        """Calculate operational impact metrics"""
        try:
            metrics = []
            
            # Upload frequency impact
            baseline_frequency = profile.baseline_metrics.get('upload_frequency', 1.0)
            current_frequency = current_metrics.get('upload_frequency', baseline_frequency)
            
            frequency_change = (current_frequency - baseline_frequency) / baseline_frequency if baseline_frequency > 0 else 0
            frequency_severity = self._determine_severity(abs(frequency_change))
            
            metrics.append(ImpactMetric(
                metric_name="upload_frequency",
                category=ImpactCategory.OPERATIONAL,
                baseline_value=baseline_frequency,
                impact_value=current_frequency,
                percentage_change=frequency_change,
                severity=frequency_severity,
                measurement_unit="uploads/day",
                confidence_level=0.9
            ))
            
            # Processing efficiency impact
            baseline_processing = profile.baseline_metrics.get('processing_efficiency', 0.95)
            current_processing = current_metrics.get('processing_efficiency', baseline_processing)
            
            processing_change = (current_processing - baseline_processing) / baseline_processing if baseline_processing > 0 else 0
            processing_severity = self._determine_severity(abs(processing_change))
            
            metrics.append(ImpactMetric(
                metric_name="processing_efficiency",
                category=ImpactCategory.OPERATIONAL,
                baseline_value=baseline_processing,
                impact_value=current_processing,
                percentage_change=processing_change,
                severity=processing_severity,
                measurement_unit="ratio",
                confidence_level=0.8
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating operational impact: {e}")
            return []
    
    async def _calculate_reputation_impact(self,
                                         profile: CreatorProfile,
                                         error_data: Dict[str, Any],
                                         current_metrics: Dict[str, float],
                                         error_type: str) -> List[ImpactMetric]:
        """Calculate reputation impact metrics"""
        try:
            metrics = []
            
            # Brand sentiment impact
            baseline_sentiment = profile.baseline_metrics.get('brand_sentiment', 0.7)
            current_sentiment = current_metrics.get('brand_sentiment', baseline_sentiment)
            
            sentiment_change = (current_sentiment - baseline_sentiment) / baseline_sentiment if baseline_sentiment > 0 else 0
            sentiment_severity = self._determine_severity(abs(sentiment_change))
            
            metrics.append(ImpactMetric(
                metric_name="brand_sentiment",
                category=ImpactCategory.REPUTATION,
                baseline_value=baseline_sentiment,
                impact_value=current_sentiment,
                percentage_change=sentiment_change,
                severity=sentiment_severity,
                measurement_unit="score",
                confidence_level=0.7
            ))
            
            # Trust score impact
            baseline_trust = profile.baseline_metrics.get('trust_score', 0.8)
            current_trust = current_metrics.get('trust_score', baseline_trust)
            
            trust_change = (current_trust - baseline_trust) / baseline_trust if baseline_trust > 0 else 0
            trust_severity = self._determine_severity(abs(trust_change))
            
            metrics.append(ImpactMetric(
                metric_name="trust_score",
                category=ImpactCategory.REPUTATION,
                baseline_value=baseline_trust,
                impact_value=current_trust,
                percentage_change=trust_change,
                severity=trust_severity,
                measurement_unit="score",
                confidence_level=0.75
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating reputation impact: {e}")
            return []
    
    async def _calculate_ux_impact(self,
                                 profile: CreatorProfile,
                                 error_data: Dict[str, Any],
                                 current_metrics: Dict[str, float],
                                 error_type: str) -> List[ImpactMetric]:
        """Calculate user experience impact metrics"""
        try:
            metrics = []
            
            # User satisfaction impact
            baseline_satisfaction = profile.baseline_metrics.get('user_satisfaction', 0.8)
            current_satisfaction = current_metrics.get('user_satisfaction', baseline_satisfaction)
            
            satisfaction_change = (current_satisfaction - baseline_satisfaction) / baseline_satisfaction if baseline_satisfaction > 0 else 0
            satisfaction_severity = self._determine_severity(abs(satisfaction_change))
            
            metrics.append(ImpactMetric(
                metric_name="user_satisfaction",
                category=ImpactCategory.USER_EXPERIENCE,
                baseline_value=baseline_satisfaction,
                impact_value=current_satisfaction,
                percentage_change=satisfaction_change,
                severity=satisfaction_severity,
                measurement_unit="score",
                confidence_level=0.8
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating UX impact: {e}")
            return []
    
    async def _calculate_content_quality_impact(self,
                                              profile: CreatorProfile,
                                              error_data: Dict[str, Any],
                                              current_metrics: Dict[str, float],
                                              error_type: str) -> List[ImpactMetric]:
        """Calculate content quality impact metrics"""
        try:
            metrics = []
            
            # Content quality score impact
            baseline_quality = profile.baseline_metrics.get('content_quality_score', 7.5)
            current_quality = current_metrics.get('content_quality_score', baseline_quality)
            
            quality_change = (current_quality - baseline_quality) / baseline_quality if baseline_quality > 0 else 0
            quality_severity = self._determine_severity(abs(quality_change))
            
            metrics.append(ImpactMetric(
                metric_name="content_quality_score",
                category=ImpactCategory.CONTENT_QUALITY,
                baseline_value=baseline_quality,
                impact_value=current_quality,
                percentage_change=quality_change,
                severity=quality_severity,
                measurement_unit="score",
                confidence_level=0.85
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating content quality impact: {e}")
            return []
    
    async def _calculate_engagement_impact(self,
                                         profile: CreatorProfile,
                                         error_data: Dict[str, Any],
                                         current_metrics: Dict[str, float],
                                         error_type: str) -> List[ImpactMetric]:
        """Calculate engagement impact metrics"""
        try:
            metrics = []
            
            # Engagement rate impact
            baseline_engagement = profile.baseline_metrics.get('engagement_rate', 0.05)
            current_engagement = current_metrics.get('engagement_rate', baseline_engagement)
            
            engagement_change = (current_engagement - baseline_engagement) / baseline_engagement if baseline_engagement > 0 else 0
            engagement_severity = self._determine_severity(abs(engagement_change))
            
            metrics.append(ImpactMetric(
                metric_name="engagement_rate",
                category=ImpactCategory.ENGAGEMENT,
                baseline_value=baseline_engagement,
                impact_value=current_engagement,
                percentage_change=engagement_change,
                severity=engagement_severity,
                measurement_unit="ratio",
                confidence_level=0.9
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating engagement impact: {e}")
            return []
    
    async def _calculate_collaboration_impact(self,
                                            profile: CreatorProfile,
                                            error_data: Dict[str, Any],
                                            current_metrics: Dict[str, float],
                                            error_type: str) -> List[ImpactMetric]:
        """Calculate collaboration impact metrics"""
        try:
            metrics = []
            
            # Collaboration frequency impact
            baseline_collab = profile.baseline_metrics.get('collaboration_count', 2.0)
            current_collab = current_metrics.get('collaboration_count', baseline_collab)
            
            collab_change = (current_collab - baseline_collab) / baseline_collab if baseline_collab > 0 else 0
            collab_severity = self._determine_severity(abs(collab_change))
            
            metrics.append(ImpactMetric(
                metric_name="collaboration_count",
                category=ImpactCategory.COLLABORATION,
                baseline_value=baseline_collab,
                impact_value=current_collab,
                percentage_change=collab_change,
                severity=collab_severity,
                measurement_unit="count",
                confidence_level=0.75
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating collaboration impact: {e}")
            return []
    
    async def _calculate_platform_reach_impact(self,
                                             profile: CreatorProfile,
                                             error_data: Dict[str, Any],
                                             current_metrics: Dict[str, float],
                                             error_type: str) -> List[ImpactMetric]:
        """Calculate platform reach impact metrics"""
        try:
            metrics = []
            
            # Platform reach impact
            baseline_reach = profile.baseline_metrics.get('platform_reach', 3.0)
            current_reach = current_metrics.get('platform_reach', baseline_reach)
            
            reach_change = (current_reach - baseline_reach) / baseline_reach if baseline_reach > 0 else 0
            reach_severity = self._determine_severity(abs(reach_change))
            
            metrics.append(ImpactMetric(
                metric_name="platform_reach",
                category=ImpactCategory.PLATFORM_REACH,
                baseline_value=baseline_reach,
                impact_value=current_reach,
                percentage_change=reach_change,
                severity=reach_severity,
                measurement_unit="platforms",
                confidence_level=0.8
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating platform reach impact: {e}")
            return []
    
    def _determine_severity(self, percentage_change: float) -> ImpactSeverity:
        """Determine impact severity based on percentage change"""
        abs_change = abs(percentage_change)
        
        if abs_change < 0.05:
            return ImpactSeverity.NEGLIGIBLE
        elif abs_change < 0.15:
            return ImpactSeverity.MINOR
        elif abs_change < 0.30:
            return ImpactSeverity.MODERATE
        elif abs_change < 0.50:
            return ImpactSeverity.SIGNIFICANT
        elif abs_change < 0.75:
            return ImpactSeverity.SEVERE
        else:
            return ImpactSeverity.CRITICAL
    
    def _calculate_overall_severity(self, impact_metrics: List[ImpactMetric]) -> ImpactSeverity:
        """Calculate overall impact severity"""
        try:
            if not impact_metrics:
                return ImpactSeverity.NEGLIGIBLE
            
            # Weight severities
            severity_weights = {
                ImpactSeverity.NEGLIGIBLE: 0,
                ImpactSeverity.MINOR: 1,
                ImpactSeverity.MODERATE: 2,
                ImpactSeverity.SIGNIFICANT: 3,
                ImpactSeverity.SEVERE: 4,
                ImpactSeverity.CRITICAL: 5
            }
            
            # Calculate weighted average
            total_weight = 0
            weighted_sum = 0
            
            for metric in impact_metrics:
                weight = metric.confidence_level
                severity_value = severity_weights[metric.severity]
                
                weighted_sum += severity_value * weight
                total_weight += weight
            
            if total_weight == 0:
                return ImpactSeverity.NEGLIGIBLE
            
            avg_severity = weighted_sum / total_weight
            
            # Map back to severity enum
            if avg_severity < 0.5:
                return ImpactSeverity.NEGLIGIBLE
            elif avg_severity < 1.5:
                return ImpactSeverity.MINOR
            elif avg_severity < 2.5:
                return ImpactSeverity.MODERATE
            elif avg_severity < 3.5:
                return ImpactSeverity.SIGNIFICANT
            elif avg_severity < 4.5:
                return ImpactSeverity.SEVERE
            else:
                return ImpactSeverity.CRITICAL
                
        except Exception as e:
            logger.error(f"Error calculating overall severity: {e}")
            return ImpactSeverity.MODERATE
    
    async def _estimate_recovery_time(self,
                                    profile: CreatorProfile,
                                    impact_metrics: List[ImpactMetric],
                                    error_type: str) -> Optional[float]:
        """Estimate recovery time in hours"""
        try:
            if not impact_metrics:
                return None
            
            # Base recovery time by error type
            base_recovery_hours = {
                'upload_error': 2,
                'payment_error': 24,
                'processing_error': 6,
                'engagement_error': 72,
                'collaboration_error': 48,
                'reputation_error': 168  # 1 week
            }
            
            base_time = base_recovery_hours.get(error_type, 24)
            
            # Adjust for impact severity
            severity_multipliers = {
                ImpactSeverity.NEGLIGIBLE: 0.5,
                ImpactSeverity.MINOR: 1.0,
                ImpactSeverity.MODERATE: 1.5,
                ImpactSeverity.SIGNIFICANT: 2.0,
                ImpactSeverity.SEVERE: 3.0,
                ImpactSeverity.CRITICAL: 5.0
            }
            
            max_severity = max(metric.severity for metric in impact_metrics)
            severity_multiplier = severity_multipliers[max_severity]
            
            # Adjust for creator recovery capability
            capability_factor = 2.0 - profile.recovery_capability  # Higher capability = faster recovery
            
            # Calculate estimated time
            estimated_hours = base_time * severity_multiplier * capability_factor
            
            return min(estimated_hours, 720)  # Cap at 30 days
            
        except Exception as e:
            logger.error(f"Error estimating recovery time: {e}")
            return None
    
    async def _calculate_total_financial_impact(self, impact_metrics: List[ImpactMetric]) -> Decimal:
        """Calculate total financial impact in USD"""
        try:
            total_impact = Decimal('0')
            
            for metric in impact_metrics:
                if metric.category == ImpactCategory.FINANCIAL:
                    if metric.metric_name == 'daily_revenue':
                        # Calculate impact over estimated recovery period
                        daily_loss = max(0, metric.baseline_value - metric.impact_value)
                        recovery_days = 7  # Assume 7 days for financial recovery
                        total_impact += Decimal(str(daily_loss * recovery_days))
                    
                    elif metric.metric_name == 'monetization_efficiency':
                        # Estimate efficiency loss impact
                        if metric.percentage_change < 0:
                            efficiency_loss = abs(metric.percentage_change)
                            estimated_loss = efficiency_loss * 1000  # $1000 base impact
                            total_impact += Decimal(str(estimated_loss))
            
            return total_impact
            
        except Exception as e:
            logger.error(f"Error calculating total financial impact: {e}")
            return Decimal('0')
    
    def _calculate_reputation_change(self, impact_metrics: List[ImpactMetric]) -> float:
        """Calculate reputation score change"""
        try:
            reputation_changes = []
            
            for metric in impact_metrics:
                if metric.category == ImpactCategory.REPUTATION:
                    reputation_changes.append(metric.percentage_change)
            
            return statistics.mean(reputation_changes) if reputation_changes else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating reputation change: {e}")
            return 0.0
    
    def _calculate_ux_impact_score(self, impact_metrics: List[ImpactMetric]) -> float:
        """Calculate UX impact score"""
        try:
            ux_changes = []
            
            for metric in impact_metrics:
                if metric.category == ImpactCategory.USER_EXPERIENCE:
                    ux_changes.append(abs(metric.percentage_change))
            
            return statistics.mean(ux_changes) if ux_changes else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating UX impact score: {e}")
            return 0.0
    
    async def _generate_mitigation_actions(self,
                                         impact_metrics: List[ImpactMetric],
                                         error_type: str,
                                         profile: CreatorProfile) -> List[str]:
        """Generate mitigation actions based on impact assessment"""
        try:
            actions = []
            
            # Error-type specific actions
            if 'upload' in error_type:
                actions.extend([
                    "Implement backup upload channels",
                    "Pre-validate content before upload",
                    "Use progressive upload for large files"
                ])
            
            elif 'payment' in error_type:
                actions.extend([
                    "Set up alternative payment methods",
                    "Implement payment retry mechanisms",
                    "Review monetization settings"
                ])
            
            elif 'engagement' in error_type:
                actions.extend([
                    "Increase audience interaction",
                    "Optimize content posting schedule",
                    "Improve content quality standards"
                ])
            
            # Impact-specific actions
            high_impact_categories = [m.category for m in impact_metrics if m.severity in [ImpactSeverity.SIGNIFICANT, ImpactSeverity.SEVERE, ImpactSeverity.CRITICAL]]
            
            if ImpactCategory.FINANCIAL in high_impact_categories:
                actions.extend([
                    "Activate emergency revenue streams",
                    "Contact sponsors for advance payments",
                    "Implement cost reduction measures"
                ])
            
            if ImpactCategory.REPUTATION in high_impact_categories:
                actions.extend([
                    "Issue public communication about issues",
                    "Implement reputation recovery campaign",
                    "Increase community engagement"
                ])
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating mitigation actions: {e}")
            return []
    
    async def _create_recovery_plan(self,
                                  profile: CreatorProfile,
                                  impact_metrics: List[ImpactMetric],
                                  error_type: str) -> Dict[str, Any]:
        """Create comprehensive recovery plan"""
        try:
            recovery_plan = {
                'phases': [],
                'timeline': {},
                'resources_needed': [],
                'success_criteria': {},
                'monitoring_schedule': []
            }
            
            # Phase 1: Immediate stabilization (0-24 hours)
            phase1 = {
                'name': 'Immediate Stabilization',
                'duration_hours': 24,
                'actions': [
                    'Assess immediate damage',
                    'Implement emergency measures',
                    'Communicate with key stakeholders'
                ],
                'success_criteria': 'No further degradation'
            }
            recovery_plan['phases'].append(phase1)
            
            # Phase 2: Active recovery (1-7 days)
            phase2 = {
                'name': 'Active Recovery',
                'duration_hours': 144,  # 6 days
                'actions': [
                    'Execute mitigation strategies',
                    'Monitor progress closely',
                    'Adjust strategy as needed'
                ],
                'success_criteria': '50% recovery achieved'
            }
            recovery_plan['phases'].append(phase2)
            
            # Phase 3: Full restoration (1-4 weeks)
            phase3 = {
                'name': 'Full Restoration',
                'duration_hours': 336,  # 2 weeks
                'actions': [
                    'Complete recovery actions',
                    'Implement prevention measures',
                    'Document lessons learned'
                ],
                'success_criteria': '95% of baseline metrics restored'
            }
            recovery_plan['phases'].append(phase3)
            
            # Resources needed
            recovery_plan['resources_needed'] = [
                'Technical support team',
                'Content creation resources',
                'Marketing/PR support',
                'Financial backup reserves'
            ]
            
            # Success criteria
            for metric in impact_metrics:
                if metric.recovery_target:
                    recovery_plan['success_criteria'][metric.metric_name] = metric.recovery_target
            
            return recovery_plan
            
        except Exception as e:
            logger.error(f"Error creating recovery plan: {e}")
            return {}
    
    async def _generate_lessons_learned(self,
                                      impact_metrics: List[ImpactMetric],
                                      error_type: str) -> List[str]:
        """Generate lessons learned from impact assessment"""
        try:
            lessons = []
            
            # Generic lessons
            lessons.extend([
                "Importance of proactive monitoring",
                "Value of diversified revenue streams",
                "Need for robust backup systems"
            ])
            
            # Impact-specific lessons
            if any(m.severity in [ImpactSeverity.SEVERE, ImpactSeverity.CRITICAL] for m in impact_metrics):
                lessons.append("Critical errors require immediate escalation")
            
            if any(m.category == ImpactCategory.FINANCIAL for m in impact_metrics):
                lessons.append("Financial impacts compound quickly")
            
            if any(m.category == ImpactCategory.REPUTATION for m in impact_metrics):
                lessons.append("Reputation damage requires long-term recovery")
            
            return lessons
            
        except Exception as e:
            logger.error(f"Error generating lessons learned: {e}")
            return []
    
    async def _generate_prevention_recommendations(self,
                                                 profile: CreatorProfile,
                                                 impact_metrics: List[ImpactMetric],
                                                 error_type: str) -> List[str]:
        """Generate prevention recommendations"""
        try:
            recommendations = []
            
            # Error-type specific recommendations
            if 'upload' in error_type:
                recommendations.extend([
                    "Implement pre-upload validation",
                    "Set up redundant upload infrastructure",
                    "Create upload monitoring dashboard"
                ])
            
            elif 'payment' in error_type:
                recommendations.extend([
                    "Diversify payment processors",
                    "Implement payment health monitoring",
                    "Set up automatic failover systems"
                ])
            
            # Profile-based recommendations
            if profile.resilience_score < 0.7:
                recommendations.extend([
                    "Improve content consistency",
                    "Diversify platform presence",
                    "Build stronger collaboration network"
                ])
            
            if profile.recovery_capability < 0.6:
                recommendations.extend([
                    "Build larger audience base",
                    "Establish emergency revenue streams",
                    "Improve content quality processes"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating prevention recommendations: {e}")
            return []
    
    async def _start_recovery_tracking(self, assessment: ErrorImpactAssessment):
        """Start recovery progress tracking"""
        try:
            recovery_progress = RecoveryProgress(
                assessment_id=assessment.assessment_id,
                recovery_status=RecoveryStatus.NOT_STARTED,
                start_time=datetime.utcnow(),
                target_completion=datetime.utcnow() + timedelta(hours=assessment.estimated_recovery_time_hours or 72),
                current_progress_percentage=0.0,
                completed_actions=[],
                pending_actions=assessment.mitigation_actions.copy(),
                obstacles_encountered=[]
            )
            
            self.recovery_progress[assessment.assessment_id] = recovery_progress
            
            logger.info(f"Recovery tracking started: {assessment.assessment_id}")
            
        except Exception as e:
            logger.error(f"Error starting recovery tracking: {e}")
    
    async def get_impact_assessment(self, assessment_id: str) -> Optional[ErrorImpactAssessment]:
        """Get impact assessment by ID"""
        try:
            return self.impact_assessments.get(assessment_id)
        except Exception as e:
            logger.error(f"Error getting impact assessment: {e}")
            return None
    
    async def get_creator_assessments(self, creator_id: str, limit: int = 10) -> List[ErrorImpactAssessment]:
        """Get recent assessments for creator"""
        try:
            creator_assessments = [a for a in self.impact_assessments.values() if a.creator_id == creator_id]
            creator_assessments.sort(key=lambda x: x.assessment_timestamp, reverse=True)
            return creator_assessments[:limit]
        except Exception as e:
            logger.error(f"Error getting creator assessments: {e}")
            return []
    
    async def get_recovery_status(self, assessment_id: str) -> Optional[RecoveryProgress]:
        """Get recovery progress status"""
        try:
            return self.recovery_progress.get(assessment_id)
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return None
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide assessment metrics"""
        try:
            metrics = {
                'total_assessments': len(self.impact_assessments),
                'total_creators_tracked': len(self.creator_profiles),
                'active_recoveries': len([r for r in self.recovery_progress.values() if r.recovery_status == RecoveryStatus.IN_PROGRESS]),
                'average_recovery_time_hours': 48.0,  # Placeholder
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}


    async def _create_basic_recovery_plan(self, category: str, metrics: List[ImpactMetric]) -> Dict[str, Any]:
        """Create basic recovery plan for any category"""
        try:
            plan = {
                'category': category,
                'actions': [
                    f"Monitor {category} metrics closely",
                    f"Implement {category} recovery strategies",
                    f"Review {category} optimization opportunities"
                ],
                'timeline_days': 7,
                'success_criteria': f"Restore {category} metrics to baseline"
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating basic recovery plan: {e}")
            return {}


# Global instance
impact_assessment_platform = CreatorErrorImpactAssessmentPlatform()