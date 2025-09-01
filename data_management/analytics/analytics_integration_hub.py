"""🚀 Advanced Revenue Analytics Integration Hub - Enterprise Platform
==================================================================

Comprehensive integration module that orchestrates all advanced revenue
analytics components into a unified, real-time analytics platform.

Features:
- Real-time revenue tracking across 15+ platforms
- Content-specific revenue attribution
- Advanced ML revenue predictions
- Dynamic pricing optimization
- Global tax compliance (67 countries)
- Unified analytics dashboard
- Automated reporting and insights

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
import uuid
from decimal import Decimal
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
import aioredis
import asyncpg

# Import des modules analytics avancés
from .realtime_revenue_tracker import (
    RealtimeRevenueTracker, 
    RealtimeRevenueEvent, 
    RevenueStreamType
)
from .advanced_ml_prediction import (
    AdvancedRevenuePredictionEngine,
    RevenueForecast,
    ForecastHorizon
)
from ..billing.enhanced_tax_compliance import (
    EnhancedTaxComplianceEngine,
    EnhancedTaxCalculation
)
from ..pricing.enhanced_dynamic_pricing import (
    EnhancedDynamicPricingEngine,
    EnhancedPriceRecommendation,
    PricingStrategy
)

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsInsight:
    """
Insight analytique unifié"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    title: str = ""
    description: str = ""
    impact_level: str = "medium"  # low, medium, high, critical
    recommendations: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class UnifiedAnalyticsReport:
    """Rapport analytics unifié"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Métriques de revenus
    revenue_summary: Dict[str, Any] = field(default_factory=dict)
    platform_breakdown: Dict[str, Any] = field(default_factory=dict)
    content_attribution: Dict[str, Any] = field(default_factory=dict)
    
    # Prédictions et optimisations
    revenue_forecast: Optional[RevenueForecast] = None
    pricing_recommendations: List[EnhancedPriceRecommendation] = field(default_factory=list)
    
    # Conformité fiscale
    tax_compliance: Dict[str, Any] = field(default_factory=dict)
    
    # Insights et recommandations
    key_insights: List[AnalyticsInsight] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    
    # Méta-données
    generated_at: datetime = field(default_factory=datetime.now)
    report_version: str = "1.0"

class AdvancedRevenueAnalyticsHub:
    """
    Hub principal pour les analytics revenus avancés
    
    Orchestration de:
    - Tracking temps réel multi-plateformes
    - Prédictions ML avancées
    - Optimisation pricing dynamique
    - Conformité fiscale globale
    - Attribution revenus par contenu
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_url = config.get("database_url", "postgresql://localhost/ainflue")
        self.redis_url = config.get("redis_url", "redis://localhost:6379")
        
        # Composants analytics
        self.realtime_tracker: Optional[RealtimeRevenueTracker] = None
        self.ml_prediction_engine: Optional[AdvancedRevenuePredictionEngine] = None
        self.tax_compliance_engine: Optional[EnhancedTaxComplianceEngine] = None
        self.pricing_engine: Optional[EnhancedDynamicPricingEngine] = None
        
        # Connexions
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        
        # État et cache
        self.analytics_cache = {}
        self.connected_websockets: set = set()
        self.insights_engine = InsightsEngine()
        
    async def initialize(self):
        """Initialise tous les composants analytics"""
        try:
            # Connexions base de données
            self.db_pool = await asyncpg.create_pool(self.db_url)
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Initialisation des moteurs analytics
            await self._initialize_analytics_engines()
            
            # Configuration des tables
            await self._setup_analytics_database()
            
            # Démarrage des services temps réel
            await self._start_realtime_services()
            
            logger.info("Advanced Revenue Analytics Hub initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics hub: {e}")
            raise
    
    async def _initialize_analytics_engines(self):
        """Initialise tous les moteurs analytics"""
        try:
            # Moteur de tracking temps réel
            self.realtime_tracker = RealtimeRevenueTracker(self.redis_url)
            await self.realtime_tracker.initialize()
            
            # Moteur de prédiction ML
            self.ml_prediction_engine = AdvancedRevenuePredictionEngine(self.config)
            
            # Moteur de conformité fiscale
            self.tax_compliance_engine = EnhancedTaxComplianceEngine(
                self.db_url, self.redis_url
            )
            await self.tax_compliance_engine.initialize()
            
            # Moteur de pricing dynamique
            self.pricing_engine = EnhancedDynamicPricingEngine(self.config)
            await self.pricing_engine.initialize()
            
            logger.info("All analytics engines initialized")
            
        except Exception as e:
            logger.error(f"Error initializing analytics engines: {e}")
            raise
    
    async def _setup_analytics_database(self):
        """Configure les tables pour l'analytics unifié"""
        async with self.db_pool.acquire() as conn:
            # Table des rapports unifés
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS unified_analytics_reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    revenue_summary JSONB NOT NULL,
                    platform_breakdown JSONB NOT NULL,
                    content_attribution JSONB NOT NULL,
                    key_insights JSONB NOT NULL,
                    action_items JSONB NOT NULL,
                    generated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_unified_reports_creator (creator_id, period_end DESC)
                );
            """)
            
            # Table des insights
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_insights (
                    id SERIAL PRIMARY KEY,
                    insight_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    impact_level VARCHAR(20) NOT NULL,
                    recommendations JSONB NOT NULL,
                    data JSONB NOT NULL,
                    generated_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP,
                    INDEX idx_insights_creator_type (creator_id, type, generated_at DESC)
                );
            """)
    
    async def _start_realtime_services(self):
        """
Démarre les services temps réel"""
        try:
            # Tâche de génération d'insights en continu
            asyncio.create_task(self._continuous_insights_generation())
            
            # Tâche de mise à jour des métriques
            asyncio.create_task(self._continuous_metrics_update())
            
            # Tâche de diffusion WebSocket
            asyncio.create_task(self._websocket_broadcast_service())
            
            logger.info("Real-time analytics services started")
            
        except Exception as e:
            logger.error(f"Error starting real-time services: {e}")
    
    async def generate_unified_analytics_report(
        self,
        creator_id: str,
        period_start: datetime,
        period_end: datetime,
        include_predictions: bool = True,
        include_pricing: bool = True
    ) -> UnifiedAnalyticsReport:
        """
        Génère un rapport analytics unifié complet
        
        Args:
            creator_id: ID du créateur
            period_start: Début de la période
            period_end: Fin de la période
            include_predictions: Inclure les prédictions ML
            include_pricing: Inclure les recommandations de pricing
            
        Returns:
            UnifiedAnalyticsReport: Rapport complet
        """
        try:
            # 1. Collecte des données de revenus en temps réel
            revenue_summary = await self.realtime_tracker.get_revenue_summary(creator_id)
            
            # 2. Récupération de la répartition par plateforme
            platform_breakdown = await self._get_platform_breakdown(creator_id, period_start, period_end)
            
            # 3. Attribution par contenu
            content_attribution = await self._get_content_attribution_analysis(
                creator_id, period_start, period_end
            )
            
            # 4. Prédictions ML (optionnel)
            revenue_forecast = None
            if include_predictions and self.ml_prediction_engine:
                revenue_history = await self._get_revenue_history(creator_id, period_start, period_end)
                if revenue_history:
                    revenue_forecast = await self.ml_prediction_engine.generate_advanced_forecast(
                        creator_id, revenue_history, ForecastHorizon.NEXT_MONTH
                    )
            
            # 5. Recommandations de pricing (optionnel)
            pricing_recommendations = []
            if include_pricing and self.pricing_engine:
                for service_type in ["subscription", "one_time", "licensing"]:
                    try:
                        pricing_rec = await self.pricing_engine.generate_enhanced_pricing_recommendation(
                            creator_id, service_type
                        )
                        pricing_recommendations.append(pricing_rec)
                    except Exception as e:
                        logger.warning(f"Could not generate pricing for {service_type}: {e}")
            
            # 6. Analyse de conformité fiscale
            tax_compliance = await self.tax_compliance_engine.generate_compliance_report(
                creator_id, period_start, period_end
            )
            
            # 7. Génération d'insights
            key_insights = await self._generate_comprehensive_insights(
                revenue_summary, platform_breakdown, content_attribution,
                revenue_forecast, pricing_recommendations, tax_compliance
            )
            
            # 8. Éléments d'action
            action_items = self._generate_action_items(key_insights, revenue_forecast, pricing_recommendations)
            
            # Création du rapport
            report = UnifiedAnalyticsReport(
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                revenue_summary=revenue_summary,
                platform_breakdown=platform_breakdown,
                content_attribution=content_attribution,
                revenue_forecast=revenue_forecast,
                pricing_recommendations=pricing_recommendations,
                tax_compliance=tax_compliance,
                key_insights=key_insights,
                action_items=action_items
            )
            
            # Stockage du rapport
            await self._store_unified_report(report)
            
            logger.info(f"Generated unified analytics report for {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating unified analytics report: {e}")
            raise
    
    async def start_realtime_revenue_tracking(self, creator_id: str):
        """Démarre le tracking temps réel pour un créateur"""
        try:
            if not self.realtime_tracker:
                raise HTTPException(status_code=500, detail="Real-time tracker not initialized")
            
            # Démarrer le streaming
            await self.realtime_tracker.start_revenue_streaming(creator_id)
            
            logger.info(f"Started real-time tracking for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"Error starting real-time tracking: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start tracking: {e}")
    
    async def get_realtime_analytics_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Récupère les données pour le dashboard temps réel"""
        try:
            # Métriques temps réel
            realtime_revenue = await self.realtime_tracker.get_revenue_summary(creator_id)
            
            # Dernières prédictions
            latest_prediction = await self._get_latest_prediction(creator_id)
            
            # Statut de conformité fiscale
            tax_status = await self._get_tax_compliance_status(creator_id)
            
            # Recommandations de pricing actives
            active_pricing_recs = await self._get_active_pricing_recommendations(creator_id)
            
            # Insights récents
            recent_insights = await self._get_recent_insights(creator_id, limit=5)
            
            # Métriques de performance
            performance_metrics = await self._calculate_performance_metrics(creator_id)
            
            return {
                "creator_id": creator_id,
                "last_updated": datetime.now().isoformat(),
                "realtime_revenue": realtime_revenue,
                "latest_prediction": latest_prediction,
                "tax_compliance_status": tax_status,
                "pricing_recommendations": active_pricing_recs,
                "recent_insights": [
                    {
                        "type": insight.type,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_level": insight.impact_level,
                        "generated_at": insight.generated_at.isoformat()
                    }
                    for insight in recent_insights
                ],
                "performance_metrics": performance_metrics,
                "streaming_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime dashboard: {e}")
            return {"error": str(e)}
    
    async def process_revenue_transaction(
        self,
        creator_id: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Traite une transaction de revenus avec analytics complet
        
        Args:
            creator_id: ID du créateur
            transaction_data: Données de la transaction
            
        Returns:
            Dict avec résultats du traitement analytics
        """
        try:
            # 1. Calcul fiscal automatique
            tax_calculation = await self.tax_compliance_engine.calculate_enhanced_tax(
                transaction_id=transaction_data["transaction_id"],
                creator_id=creator_id,
                amount=Decimal(str(transaction_data["amount"])),
                customer_country=transaction_data["customer_country"],
                category=transaction_data.get("category", "digital_content"),
                currency=transaction_data.get("currency", "EUR")
            )
            
            # 2. Attribution par contenu
            content_attribution = await self._attribute_transaction_to_content(
                transaction_data, creator_id
            )
            
            # 3. Événement temps réel
            realtime_event = RealtimeRevenueEvent(
                event_type=RevenueStreamType.LIVE_EARNINGS,
                creator_id=creator_id,
                platform=transaction_data.get("platform", "direct"),
                content_id=content_attribution.get("content_id"),
                revenue_amount=Decimal(str(transaction_data["amount"])),
                currency=transaction_data.get("currency", "EUR"),
                attribution_data=content_attribution
            )
            
            # Ajouter à la queue temps réel
            self.realtime_tracker.revenue_buffer.append(realtime_event)
            
            # 4. Mise à jour des métriques
            await self._update_creator_metrics(creator_id, transaction_data, tax_calculation)
            
            # 5. Vérification des seuils et alertes
            alerts = await self._check_revenue_thresholds(creator_id, transaction_data)
            
            # 6. Mise à jour des prédictions si nécessaire
            await self._trigger_prediction_update_if_needed(creator_id)
            
            return {
                "transaction_processed": True,
                "tax_calculation": {
                    "total_tax": str(tax_calculation.tax_amount),
                    "net_amount": str(tax_calculation.net_amount),
                    "compliance_status": tax_calculation.compliance_status.value
                },
                "content_attribution": content_attribution,
                "alerts": alerts,
                "realtime_event_id": realtime_event.event_id
            }
            
        except Exception as e:
            logger.error(f"Error processing revenue transaction: {e}")
            return {"error": str(e), "transaction_processed": False}
    
    # WebSocket endpoints pour temps réel
    
    async def websocket_connect(self, websocket: WebSocket, creator_id: str):
        """Connexion WebSocket pour analytics temps réel"""
        try:
            await websocket.accept()
            self.connected_websockets.add(websocket)
            
            # Ajouter au tracker temps réel
            await self.realtime_tracker.add_websocket_client(websocket)
            
            # Envoyer les données initiales
            initial_data = await self.get_realtime_analytics_dashboard(creator_id)
            await websocket.send_json({
                "type": "initial_data",
                "data": initial_data
            })
            
            logger.info(f"WebSocket connected for creator {creator_id}")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def websocket_disconnect(self, websocket: WebSocket):
        """Déconnexion WebSocket"""
        try:
            self.connected_websockets.discard(websocket)
            await self.realtime_tracker.remove_websocket_client(websocket)
            
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}")
    
    # Services en arrière-plan
    
    async def _continuous_insights_generation(self):
        """Génération continue d'insights"""
        while True:
            try:
                # Récupérer la liste des créateurs actifs
                active_creators = await self._get_active_creators()
                
                for creator_id in active_creators:
                    # Générer des insights si nécessaire
                    await self._generate_insights_for_creator(creator_id)
                
                # Attendre 5 minutes avant la prochaine génération
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in continuous insights generation: {e}")
                await asyncio.sleep(60)
    
    async def _continuous_metrics_update(self):
        """Mise à jour continue des métriques"""
        while True:
            try:
                # Mettre à jour les métriques globales
                await self._update_global_metrics()
                
                # Attendre 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in continuous metrics update: {e}")
                await asyncio.sleep(30)
    
    async def _websocket_broadcast_service(self):
        """Service de diffusion WebSocket"""
        while True:
            try:
                if self.connected_websockets:
                    # Préparer les données de diffusion
                    broadcast_data = await self._prepare_broadcast_data()
                    
                    # Diffuser à tous les clients connectés
                    disconnected = set()
                    for websocket in self.connected_websockets:
                        try:
                            await websocket.send_json({
                                "type": "metrics_update",
                                "data": broadcast_data,
                                "timestamp": datetime.now().isoformat()
                            })
                        except:
                            disconnected.add(websocket)
                    
                    # Supprimer les connexions fermées
                    self.connected_websockets -= disconnected
                
                await asyncio.sleep(10)  # Diffuser toutes les 10 secondes
                
            except Exception as e:
                logger.error(f"Error in WebSocket broadcast: {e}")
                await asyncio.sleep(30)
    
    # Méthodes utilitaires
    
    async def _get_platform_breakdown(self, creator_id: str, start: datetime, end: datetime) -> Dict[str, Any]:
        """Récupère la répartition par plateforme"""
        # Implémentation simplifiée
        return {
            "spotify": {"revenue": 1250.50, "transactions": 125, "percentage": 35.2},
            "youtube": {"revenue": 980.25, "transactions": 98, "percentage": 27.6},
            "instagram": {"revenue": 750.00, "transactions": 75, "percentage": 21.1},
            "tiktok": {"revenue": 570.25, "transactions": 57, "percentage": 16.1}
        }
    
    async def _store_unified_report(self, report: UnifiedAnalyticsReport):
        """Stocke le rapport unifié"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO unified_analytics_reports 
                    (report_id, creator_id, period_start, period_end, revenue_summary, 
                     platform_breakdown, content_attribution, key_insights, action_items)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                report.report_id,
                report.creator_id,
                report.period_start,
                report.period_end,
                json.dumps(report.revenue_summary, default=str),
                json.dumps(report.platform_breakdown, default=str),
                json.dumps(report.content_attribution, default=str),
                json.dumps([
                    {
                        "type": insight.type,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_level": insight.impact_level,
                        "recommendations": insight.recommendations
                    }
                    for insight in report.key_insights
                ]),
                json.dumps(report.action_items)
                )
                
        except Exception as e:
            logger.error(f"Error storing unified report: {e}")

class InsightsEngine:
    """Moteur de génération d'insights automatisés"""
    
    async def generate_insights_from_data(
        self,
        revenue_data: Dict[str, Any],
        forecast_data: Optional[RevenueForecast],
        pricing_data: List[EnhancedPriceRecommendation]
    ) -> List[AnalyticsInsight]:
        """
Génère des insights à partir des données analytics"""
        insights = []
        
        try:
            # Insight sur la croissance des revenus
            if "growth_rate" in revenue_data:
                growth_rate = revenue_data["growth_rate"]
                if growth_rate > 0.20:  # 20% de croissance
                    insights.append(AnalyticsInsight(
                        type="revenue_growth",
                        title="Forte croissance des revenus détectée",
                        description=f"Vos revenus ont augmenté de {growth_rate:.1%} récemment",
                        impact_level="high",
                        recommendations=[
                            "Analyser les facteurs de cette croissance",
                            "Optimiser les canaux performants",
                            "Considérer une augmentation des prix"
                        ]
                    ))
            
            # Insight sur les prédictions
            if forecast_data and forecast_data.confidence_score > 0.8:
                insights.append(AnalyticsInsight(
                    type="revenue_forecast",
                    title="Prédiction de revenus très fiable",
                    description=f"Revenus prédits: €{forecast_data.predicted_amount} (confiance: {forecast_data.confidence_score:.1%})",
                    impact_level="medium",
                    recommendations=[
                        "Planifier les investissements basés sur cette prédiction",
                        "Ajuster la stratégie de contenu"
                    ]
                ))
            
            # Insight sur le pricing
            if pricing_data:
                high_confidence_pricing = [p for p in pricing_data if p.confidence_score > 0.8]
                if high_confidence_pricing:
                    insights.append(AnalyticsInsight(
                        type="pricing_optimization",
                        title="Opportunités d'optimisation des prix",
                        description=f"{len(high_confidence_pricing)} recommandations de prix à haute confiance disponibles",
                        impact_level="medium",
                        recommendations=[
                            "Tester les nouveaux prix recommandés",
                            "Analyser l'élasticité de la demande",
                            "Mettre en place des tests A/B"
                        ]
                    ))
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights

# API endpoints FastAPI

def create_analytics_api() -> FastAPI:
    """Crée l'API FastAPI pour les analytics avancés"""
    app = FastAPI(title="Advanced Revenue Analytics API", version="1.0.0")
    
    # Instance globale du hub
    analytics_hub: Optional[AdvancedRevenueAnalyticsHub] = None
    
    @app.on_event("startup")
    async def startup_event():
        nonlocal analytics_hub
        config = {
            "database_url": "postgresql://localhost/ainflue",
            "redis_url": "redis://localhost:6379"
        }
        analytics_hub = AdvancedRevenueAnalyticsHub(config)
        await analytics_hub.initialize()
    
    @app.get("/analytics/dashboard/{creator_id}")
    async def get_analytics_dashboard(creator_id: str):
        """Récupère le dashboard analytics temps réel"""
        if not analytics_hub:
            raise HTTPException(status_code=500, detail="Analytics hub not initialized")
        
        dashboard_data = await analytics_hub.get_realtime_analytics_dashboard(creator_id)
        return JSONResponse(content=dashboard_data)
    
    @app.post("/analytics/report/{creator_id}")
    async def generate_analytics_report(
        creator_id: str,
        period_start: datetime,
        period_end: datetime,
        include_predictions: bool = True,
        include_pricing: bool = True
    ):
        """Génère un rapport analytics complet"""
        if not analytics_hub:
            raise HTTPException(status_code=500, detail="Analytics hub not initialized")
        
        report = await analytics_hub.generate_unified_analytics_report(
            creator_id, period_start, period_end, include_predictions, include_pricing
        )
        
        # Conversion en dictionnaire pour la réponse JSON
        return {
            "report_id": report.report_id,
            "creator_id": report.creator_id,
            "period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat()
            },
            "revenue_summary": report.revenue_summary,
            "platform_breakdown": report.platform_breakdown,
            "key_insights": [
                {
                    "type": insight.type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_level": insight.impact_level,
                    "recommendations": insight.recommendations
                }
                for insight in report.key_insights
            ],
            "action_items": report.action_items,
            "generated_at": report.generated_at.isoformat()
        }
    
    @app.websocket("/analytics/realtime/{creator_id}")
    async def websocket_analytics(websocket: WebSocket, creator_id: str):
        """WebSocket pour analytics temps réel"""
        if not analytics_hub:
            await websocket.close(code=1003, reason="Analytics hub not initialized")
            return
        
        await analytics_hub.websocket_connect(websocket, creator_id)
        
        try:
            while True:
                # Maintenir la connexion
                await websocket.receive_text()
        except WebSocketDisconnect:
            await analytics_hub.websocket_disconnect(websocket)
    
    @app.post("/analytics/transaction")
    async def process_transaction(transaction_data: Dict[str, Any]):
        """Traite une transaction avec analytics complet"""
        if not analytics_hub:
            raise HTTPException(status_code=500, detail="Analytics hub not initialized")
        
        result = await analytics_hub.process_revenue_transaction(
            transaction_data["creator_id"], transaction_data
        )
        
        return JSONResponse(content=result)
    
    return app