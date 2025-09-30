#!/usr/bin/env python3
"""
Performance Analytics Demo - Démonstration Analytics Performance Affiliation
==========================================================================

Démonstration analytics performance ultra sophistiquées pour système d'affiliation Ainflue.
Inclut tracking temps réel, analytics prédictives, et insights business actionables.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging
import json
import random

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MetricType(str, Enum):
    """Types de métriques analytics"""
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    RETURN_ON_AD_SPEND = "return_on_ad_spend"
    AFFILIATE_PERFORMANCE = "affiliate_performance"
    ENGAGEMENT_RATE = "engagement_rate"
    ATTRIBUTION_SCORE = "attribution_score"


class AnalyticsTimeframe(str, Enum):
    """Périodes d'analyse"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PredictionModel(str, Enum):
    """Modèles de prédiction"""
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"


@dataclass
class PerformanceMetric:
    """Métrique de performance"""
    metric_id: str
    metric_type: MetricType
    value: Union[float, int, Decimal]
    timestamp: datetime
    affiliate_id: str
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsInsight:
    """Insight analytique actionable"""
    insight_id: str
    title: str
    description: str
    confidence_level: float
    impact_score: float
    recommended_actions: List[str]
    data_sources: List[str]
    created_at: datetime


@dataclass
class PredictiveAnalysis:
    """Analyse prédictive"""
    analysis_id: str
    model_used: PredictionModel
    prediction_target: str
    forecast_period: int  # days
    predicted_values: List[Dict[str, Any]]
    confidence_intervals: Dict[str, float]
    accuracy_score: float


class PerformanceAnalyticsDemo:
    """
    Démonstration analytics performance ultra sophistiquées
    Real-time tracking avec predictive analytics et business intelligence
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PerformanceAnalyticsDemo")
        
        # Simulate analytics services
        self.real_time_tracker = None
        self.predictive_engine = None
        self.business_intelligence = None
        self.insight_generator = None
        
        # Performance data storage
        self.metrics_history: List[PerformanceMetric] = []
        self.insights_database: List[AnalyticsInsight] = []
        self.predictions_cache: Dict[str, PredictiveAnalysis] = {}
        
        # Analytics configuration
        self.tracking_intervals = {
            AnalyticsTimeframe.REAL_TIME: 1,  # seconds
            AnalyticsTimeframe.HOURLY: 3600,
            AnalyticsTimeframe.DAILY: 86400,
            AnalyticsTimeframe.WEEKLY: 604800,
            AnalyticsTimeframe.MONTHLY: 2592000
        }
    
    async def initialize(self) -> bool:
        """Initialize the performance analytics demo"""
        try:
            self.logger.info("🚀 Initialisation Performance Analytics Demo")
            await asyncio.sleep(0.1)
            
            # Generate sample historical data
            await self._generate_sample_historical_data()
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def demonstrate_real_time_performance_tracking(self) -> Dict[str, Any]:
        """Démonstration tracking performance temps réel sophistiqué"""
        
        self.logger.info("⚡ DÉMONSTRATION TRACKING PERFORMANCE TEMPS RÉEL")
        self.logger.info("=" * 60)
        
        # Simulation données temps réel pour plusieurs affiliés
        affiliates_data = {
            "influencer_001": {
                "name": "Maya Trends",
                "tier": "platinum",
                "active_campaigns": 5,
                "current_performance": {
                    "revenue_today": Decimal("2847.50"),
                    "clicks_today": 1250,
                    "conversions_today": 47,
                    "engagement_rate": 0.087
                }
            },
            "musician_001": {
                "name": "Alex Symphony", 
                "tier": "premium",
                "active_campaigns": 3,
                "current_performance": {
                    "revenue_today": Decimal("1456.80"),
                    "clicks_today": 890,
                    "conversions_today": 23,
                    "engagement_rate": 0.071
                }
            },
            "photographer_001": {
                "name": "Sarah Visual",
                "tier": "professional",
                "active_campaigns": 4,
                "current_performance": {
                    "revenue_today": Decimal("1892.30"),
                    "clicks_today": 1050,
                    "conversions_today": 31,
                    "engagement_rate": 0.082
                }
            }
        }
        
        real_time_results = {}
        
        for affiliate_id, data in affiliates_data.items():
            self.logger.info(f"\n👤 AFFILIATE: {data['name']} ({affiliate_id})")
            self.logger.info(f"🏆 Tier: {data['tier']}")
            
            # Real-time metrics calculation
            performance = data["current_performance"]
            conversion_rate = (performance["conversions_today"] / performance["clicks_today"]) * 100
            revenue_per_click = performance["revenue_today"] / performance["clicks_today"]
            
            self.logger.info(f"💰 Revenue aujourd'hui: ${performance['revenue_today']}")
            self.logger.info(f"👆 Clics: {performance['clicks_today']}")
            self.logger.info(f"✅ Conversions: {performance['conversions_today']}")
            self.logger.info(f"📊 Taux conversion: {conversion_rate:.2f}%")
            self.logger.info(f"💵 Revenue/clic: ${revenue_per_click:.3f}")
            self.logger.info(f"❤️ Engagement: {performance['engagement_rate']:.1%}")
            
            # Performance trends calculation
            trend_analysis = await self._calculate_performance_trends(affiliate_id)
            self.logger.info(f"📈 Tendance revenue: {trend_analysis['revenue_trend']:.1%}")
            self.logger.info(f"📊 Tendance conversion: {trend_analysis['conversion_trend']:.1%}")
            
            # Real-time alerts
            alerts = await self._generate_real_time_alerts(affiliate_id, performance)
            if alerts:
                self.logger.info("🚨 ALERTES TEMPS RÉEL:")
                for alert in alerts:
                    self.logger.info(f"   ⚠️ {alert}")
            
            real_time_results[affiliate_id] = {
                "performance_metrics": performance,
                "calculated_metrics": {
                    "conversion_rate": conversion_rate,
                    "revenue_per_click": float(revenue_per_click)
                },
                "trends": trend_analysis,
                "alerts": alerts
            }
        
        # Global performance summary
        total_revenue = sum(Decimal(str(data["current_performance"]["revenue_today"])) 
                          for data in affiliates_data.values())
        total_clicks = sum(data["current_performance"]["clicks_today"] 
                         for data in affiliates_data.values())
        total_conversions = sum(data["current_performance"]["conversions_today"] 
                              for data in affiliates_data.values())
        
        self.logger.info(f"\n📊 PERFORMANCE GLOBALE AUJOURD'HUI:")
        self.logger.info(f"💰 Revenue total: ${total_revenue}")
        self.logger.info(f"👆 Clics total: {total_clicks}")
        self.logger.info(f"✅ Conversions total: {total_conversions}")
        self.logger.info(f"📈 Taux conversion global: {(total_conversions/total_clicks)*100:.2f}%")
        
        return {
            "affiliate_performances": real_time_results,
            "global_metrics": {
                "total_revenue": float(total_revenue),
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "global_conversion_rate": (total_conversions/total_clicks)*100
            },
            "tracking_timestamp": datetime.now().isoformat()
        }
    
    async def demonstrate_predictive_analytics(self) -> Dict[str, Any]:
        """Démonstration analytics prédictives pour optimisation performance"""
        
        self.logger.info("\n🔮 DÉMONSTRATION ANALYTICS PRÉDICTIVES")
        self.logger.info("=" * 60)
        
        # Prédictions revenue pour 30 prochains jours
        revenue_prediction = await self._generate_revenue_prediction(30)
        
        self.logger.info(f"📈 PRÉDICTION REVENUE - 30 JOURS:")
        self.logger.info(f"🤖 Modèle utilisé: {revenue_prediction.model_used}")
        self.logger.info(f"🎯 Accuracy: {revenue_prediction.accuracy_score:.1%}")
        
        # Affichage prédictions hebdomadaires
        weekly_predictions = [pred for pred in revenue_prediction.predicted_values 
                            if pred["period_type"] == "weekly"]
        
        for week_data in weekly_predictions[:4]:  # 4 premières semaines
            self.logger.info(f"📅 Semaine {week_data['week_number']}:")
            self.logger.info(f"   💰 Revenue prédit: ${week_data['predicted_revenue']:.2f}")
            self.logger.info(f"   📊 Confiance: {week_data['confidence']:.1%}")
            self.logger.info(f"   📈 Croissance vs semaine précédente: {week_data['growth_rate']:.1%}")
        
        # Prédictions performance par affilié
        affiliate_predictions = await self._predict_affiliate_performance()
        
        self.logger.info(f"\n🎯 PRÉDICTIONS PERFORMANCE AFFILIÉS:")
        for affiliate_id, prediction in affiliate_predictions.items():
            self.logger.info(f"👤 {affiliate_id}:")
            self.logger.info(f"   📈 Revenue prédit (7j): ${prediction['predicted_revenue_7d']:.2f}")
            self.logger.info(f"   📊 Conversions prédites: {prediction['predicted_conversions']}")
            self.logger.info(f"   🎖️ Tier prédit: {prediction['predicted_tier']}")
            self.logger.info(f"   ⚡ Recommandations:")
            for rec in prediction['recommendations']:
                self.logger.info(f"      • {rec}")
        
        # Market trends analysis
        market_analysis = await self._analyze_market_trends()
        
        self.logger.info(f"\n🌍 ANALYSE TENDANCES MARCHÉ:")
        self.logger.info(f"📊 Secteur le plus performant: {market_analysis['top_performing_sector']}")
        self.logger.info(f"📈 Croissance sectorielle: {market_analysis['sector_growth']:.1%}")
        self.logger.info(f"🎯 Opportunités émergentes: {len(market_analysis['emerging_opportunities'])}")
        
        for opportunity in market_analysis['emerging_opportunities'][:3]:
            self.logger.info(f"   💡 {opportunity['title']}: {opportunity['potential_impact']:.1%} impact")
        
        return {
            "revenue_prediction": {
                "model": revenue_prediction.model_used,
                "accuracy": revenue_prediction.accuracy_score,
                "weekly_forecasts": weekly_predictions
            },
            "affiliate_predictions": affiliate_predictions,
            "market_analysis": market_analysis,
            "prediction_timestamp": datetime.now().isoformat()
        }
    
    async def demonstrate_business_intelligence_insights(self) -> Dict[str, Any]:
        """Démonstration business intelligence avec insights actionables"""
        
        self.logger.info("\n🧠 DÉMONSTRATION BUSINESS INTELLIGENCE")
        self.logger.info("=" * 60)
        
        # Génération insights automatiques
        insights = await self._generate_business_insights()
        
        self.logger.info(f"💡 INSIGHTS BUSINESS AUTOMATIQUES ({len(insights)}):")
        
        for insight in insights:
            self.logger.info(f"\n📊 {insight.title}")
            self.logger.info(f"📝 {insight.description}")
            self.logger.info(f"🎯 Confiance: {insight.confidence_level:.1%}")
            self.logger.info(f"📈 Impact potentiel: {insight.impact_score:.1%}")
            self.logger.info(f"🔧 Actions recommandées:")
            for action in insight.recommended_actions:
                self.logger.info(f"   • {action}")
        
        # ROI analysis sophistiquée
        roi_analysis = await self._perform_roi_analysis()
        
        self.logger.info(f"\n💰 ANALYSE ROI SOPHISTIQUÉE:")
        self.logger.info(f"📊 ROI global: {roi_analysis['global_roi']:.1%}")
        self.logger.info(f"🏆 Meilleur affilié ROI: {roi_analysis['top_affiliate']['name']} ({roi_analysis['top_affiliate']['roi']:.1%})")
        self.logger.info(f"📈 ROI moyen par tier:")
        
        for tier, roi in roi_analysis['roi_by_tier'].items():
            self.logger.info(f"   {tier}: {roi:.1%}")
        
        # Attribution model comparison
        attribution_comparison = await self._compare_attribution_models()
        
        self.logger.info(f"\n🎯 COMPARAISON MODÈLES ATTRIBUTION:")
        for model, results in attribution_comparison.items():
            self.logger.info(f"📊 {model}:")
            self.logger.info(f"   💰 Revenue attribué: ${results['attributed_revenue']:.2f}")
            self.logger.info(f"   📈 Accuracy: {results['accuracy']:.1%}")
            self.logger.info(f"   ⚡ Recommandé: {'✅' if results['recommended'] else '❌'}")
        
        return {
            "business_insights": [
                {
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence_level,
                    "impact": insight.impact_score,
                    "actions": insight.recommended_actions
                }
                for insight in insights
            ],
            "roi_analysis": roi_analysis,
            "attribution_comparison": attribution_comparison,
            "intelligence_timestamp": datetime.now().isoformat()
        }
    
    # Helper methods for simulations
    async def _generate_sample_historical_data(self) -> None:
        """Génère des données historiques de test"""
        await asyncio.sleep(0.05)
        
        affiliates = ["influencer_001", "musician_001", "photographer_001"]
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            for affiliate_id in affiliates:
                # Simulate daily metrics
                daily_revenue = Decimal(str(random.uniform(500, 3000)))
                daily_clicks = random.randint(200, 1500)
                daily_conversions = random.randint(10, 50)
                
                metrics = [
                    PerformanceMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_type=MetricType.REVENUE,
                        value=daily_revenue,
                        timestamp=current_date,
                        affiliate_id=affiliate_id
                    ),
                    PerformanceMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_type=MetricType.CONVERSION_RATE,
                        value=(daily_conversions / daily_clicks) * 100,
                        timestamp=current_date,
                        affiliate_id=affiliate_id
                    )
                ]
                
                self.metrics_history.extend(metrics)
    
    async def _calculate_performance_trends(self, affiliate_id: str) -> Dict[str, float]:
        """Calcule les tendances de performance"""
        await asyncio.sleep(0.02)
        
        # Simulate trend calculation
        revenue_trend = random.uniform(-0.1, 0.25)  # -10% to +25%
        conversion_trend = random.uniform(-0.05, 0.15)  # -5% to +15%
        
        return {
            "revenue_trend": revenue_trend,
            "conversion_trend": conversion_trend
        }
    
    async def _generate_real_time_alerts(self, affiliate_id: str, performance: Dict) -> List[str]:
        """Génère des alertes temps réel"""
        await asyncio.sleep(0.01)
        
        alerts = []
        
        # Performance-based alerts
        if performance["conversions_today"] < 10:
            alerts.append("Conversions faibles - Optimisation recommandée")
        
        if performance["engagement_rate"] > 0.1:
            alerts.append("Engagement exceptionnel - Opportunité de scaling")
        
        if performance["revenue_today"] > Decimal("2500"):
            alerts.append("Performance revenue excellente - Bonus tier possible")
        
        return alerts
    
    async def _generate_revenue_prediction(self, days: int) -> PredictiveAnalysis:
        """Génère une prédiction de revenue"""
        await asyncio.sleep(0.1)
        
        # Simulate prediction data
        weekly_predictions = []
        base_revenue = 5000
        
        for week in range(1, 5):  # 4 weeks
            predicted_revenue = base_revenue * (1 + random.uniform(0.05, 0.2))
            growth_rate = random.uniform(0.02, 0.15)
            confidence = random.uniform(0.75, 0.95)
            
            weekly_predictions.append({
                "week_number": week,
                "period_type": "weekly",
                "predicted_revenue": predicted_revenue,
                "growth_rate": growth_rate,
                "confidence": confidence
            })
            
            base_revenue = predicted_revenue
        
        return PredictiveAnalysis(
            analysis_id=str(uuid.uuid4()),
            model_used=PredictionModel.ENSEMBLE,
            prediction_target="revenue",
            forecast_period=days,
            predicted_values=weekly_predictions,
            confidence_intervals={"lower": 0.80, "upper": 0.95},
            accuracy_score=0.87
        )
    
    async def _predict_affiliate_performance(self) -> Dict[str, Dict[str, Any]]:
        """Prédit la performance des affiliés"""
        await asyncio.sleep(0.08)
        
        return {
            "influencer_001": {
                "predicted_revenue_7d": 12500.00,
                "predicted_conversions": 95,
                "predicted_tier": "platinum_plus",
                "recommendations": [
                    "Augmenter budget campagnes vidéo",
                    "Explorer partenariats lifestyle",
                    "Optimiser horaires publication"
                ]
            },
            "musician_001": {
                "predicted_revenue_7d": 8900.00,
                "predicted_conversions": 67,
                "predicted_tier": "premium_plus",
                "recommendations": [
                    "Développer contenu audio exclusif",
                    "Cibler audiences musicales niche",
                    "Collaboration avec autres musiciens"
                ]
            },
            "photographer_001": {
                "predicted_revenue_7d": 9800.00,
                "predicted_conversions": 73,
                "predicted_tier": "professional_plus",
                "recommendations": [
                    "Créer portfolios thématiques",
                    "Proposer services personnalisés",
                    "Exploiter tendances visuelles"
                ]
            }
        }
    
    async def _analyze_market_trends(self) -> Dict[str, Any]:
        """Analyse les tendances du marché"""
        await asyncio.sleep(0.06)
        
        return {
            "top_performing_sector": "Content Creation & Influencer Marketing",
            "sector_growth": 0.34,  # 34% growth
            "emerging_opportunities": [
                {
                    "title": "AI-Generated Content Collaboration",
                    "potential_impact": 0.28
                },
                {
                    "title": "Virtual Reality Content Creation",
                    "potential_impact": 0.22
                },
                {
                    "title": "Sustainable Brand Partnerships",
                    "potential_impact": 0.19
                }
            ]
        }
    
    async def _generate_business_insights(self) -> List[AnalyticsInsight]:
        """Génère des insights business automatiques"""
        await asyncio.sleep(0.1)
        
        insights = [
            AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Optimisation Conversion Tier Premium",
                description="Les affiliés tier premium montrent 23% de conversion supérieure avec contenu vidéo",
                confidence_level=0.89,
                impact_score=0.31,
                recommended_actions=[
                    "Encourager production contenu vidéo",
                    "Fournir templates vidéo optimisés",
                    "Créer incentives spécifiques vidéo"
                ],
                data_sources=["conversion_tracking", "content_analysis", "tier_performance"],
                created_at=datetime.now()
            ),
            AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Saisonnalité Revenue Photographes",
                description="Revenue photographes augmente de 45% pendant saisons mariage et vacances",
                confidence_level=0.92,
                impact_score=0.28,
                recommended_actions=[
                    "Préparer campagnes saisonnières",
                    "Ajuster commissions selon saisons",
                    "Développer contenu thématique"
                ],
                data_sources=["seasonal_analysis", "photographer_metrics", "market_data"],
                created_at=datetime.now()
            ),
            AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Cross-Platform Synergy Effect",
                description="Affiliés actifs sur 3+ plateformes génèrent 67% plus de revenue",
                confidence_level=0.85,
                impact_score=0.42,
                recommended_actions=[
                    "Inciter diversification plateformes",
                    "Créer outils cross-platform",
                    "Bonus multi-plateforme"
                ],
                data_sources=["platform_analysis", "revenue_correlation", "affiliate_behavior"],
                created_at=datetime.now()
            )
        ]
        
        return insights
    
    async def _perform_roi_analysis(self) -> Dict[str, Any]:
        """Effectue une analyse ROI sophistiquée"""
        await asyncio.sleep(0.07)
        
        return {
            "global_roi": 0.342,  # 34.2%
            "top_affiliate": {
                "name": "Maya Trends",
                "roi": 0.456
            },
            "roi_by_tier": {
                "platinum": 0.398,
                "premium": 0.345,
                "professional": 0.312,
                "basic": 0.267
            }
        }
    
    async def _compare_attribution_models(self) -> Dict[str, Dict[str, Any]]:
        """Compare différents modèles d'attribution"""
        await asyncio.sleep(0.05)
        
        return {
            "First Touch": {
                "attributed_revenue": 15670.89,
                "accuracy": 0.72,
                "recommended": False
            },
            "Last Touch": {
                "attributed_revenue": 18923.45,
                "accuracy": 0.78,
                "recommended": False
            },
            "Linear": {
                "attributed_revenue": 17234.67,
                "accuracy": 0.83,
                "recommended": True
            },
            "Time Decay": {
                "attributed_revenue": 16789.23,
                "accuracy": 0.86,
                "recommended": True
            },
            "Data-Driven": {
                "attributed_revenue": 17891.34,
                "accuracy": 0.91,
                "recommended": True
            }
        }


async def demonstrate() -> Dict[str, Any]:
    """
    Fonction principale de démonstration
    
    Returns:
        Résultats complets de la démonstration
    """
    demo = PerformanceAnalyticsDemo()
    
    if not await demo.initialize():
        return {"error": "Failed to initialize performance analytics demo"}
    
    try:
        # Real-time tracking demonstration
        real_time_results = await demo.demonstrate_real_time_performance_tracking()
        
        # Predictive analytics demonstration
        predictive_results = await demo.demonstrate_predictive_analytics()
        
        # Business intelligence demonstration
        bi_results = await demo.demonstrate_business_intelligence_insights()
        
        return {
            "demo_type": "performance_analytics",
            "demo_version": "3.0.0-ULTRA-ADVANCED",
            "execution_timestamp": datetime.now().isoformat(),
            "results": {
                "real_time_tracking": real_time_results,
                "predictive_analytics": predictive_results,
                "business_intelligence": bi_results
            },
            "success": True
        }
        
    except Exception as e:
        demo.logger.error(f"❌ Erreur durant la démonstration: {e}")
        return {"error": str(e), "success": False}


async def main(**kwargs) -> Dict[str, Any]:
    """
    Point d'entrée principal pour la démonstration
    Compatible avec l'interface du module affiliate examples
    """
    return await demonstrate()


if __name__ == "__main__":
    """Exécution directe du module"""
    print("=" * 70)
    print("📊 PERFORMANCE ANALYTICS DEMO - AINFLUE AFFILIATE SYSTEM")
    print("=" * 70)
    
    try:
        result = asyncio.run(demonstrate())
        
        if result.get("success"):
            print("\n✅ Démonstration terminée avec succès!")
            print(f"📊 Métriques trackées en temps réel")
            print(f"🔮 Prédictions générées avec ML")
            print(f"🧠 Insights business automatiques")
        else:
            print(f"\n❌ Erreur: {result.get('error')}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)