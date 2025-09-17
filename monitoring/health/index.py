"""🏥 Health Monitoring - Main Orchestrator | Ainflue Creator Economy
==============================================================================
© 2025 Fahed Mlaiel <mlaiel@live.de> - TOUS DROITS RÉSERVÉS

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande: mlaiel@live.de
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
         Microservices + Audio + DevOps + IA Prompt Engineer
Architecture: Creator Economy Enterprise Health Monitoring System
==============================================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from enum import Enum
import json
from abc import ABC, abstractmethod

# Import existing components
from .health_checks import HealthChecksManager, MonitoringConfig, SystemMetrics
from . import creator_economy_health_orchestrator
from . import creator_performance_health_monitor
from . import ai_ml_health_intelligence_engine
from . import creator_content_pipeline_health_validator
from . import multi_format_processing_health_tracker

logger = logging.getLogger(__name__)

# =============== CREATOR ECONOMY HEALTH CONFIGURATION ===============

class CreatorTier(Enum):
    """Creator Economy Tier Levels"""
    EMERGING = "emerging"      # 0-1K followers
    RISING = "rising"         # 1K-10K followers  
    ESTABLISHED = "established" # 10K-100K followers
    PREMIUM = "premium"        # 100K-1M followers
    ELITE = "elite"           # 1M+ followers
    ENTERPRISE = "enterprise"  # Business accounts

class CreatorFormat(Enum):
    """Multi-Format Content Types"""
    MUSIC = "music"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    COMEDY = "comedy"
    EDUCATION = "education"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"

@dataclass
class CreatorEconomyHealthConfig:
    """Configuration santé Creator Economy enterprise"""
    # Core monitoring settings
    health_check_interval: int = 15  # Seconds
    real_time_monitoring: bool = True
    predictive_analytics: bool = True
    ai_powered_insights: bool = True
    
    # Creator-specific settings
    creator_tier_monitoring: bool = True
    content_pipeline_validation: bool = True
    monetization_tracking: bool = True
    collaboration_analytics: bool = True
    
    # Performance thresholds
    content_processing_max_time_ms: int = 5000
    ai_inference_max_time_ms: int = 2000
    api_response_max_time_ms: int = 500
    database_query_max_time_ms: int = 100
    
    # Alert configuration
    alert_channels: List[str] = field(default_factory=lambda: [
        "slack", "email", "pagerduty", "dashboard"
    ])
    critical_alert_immediate: bool = True
    
    # AI/ML settings
    ml_prediction_enabled: bool = True
    anomaly_detection_enabled: bool = True
    trend_analysis_enabled: bool = True
    
    # Business metrics
    revenue_tracking: bool = True
    engagement_monitoring: bool = True
    creator_satisfaction_tracking: bool = True
    
    # Compliance & Security
    gdpr_compliance_monitoring: bool = True
    security_audit_enabled: bool = True
    ip_protection_monitoring: bool = True

# =============== HEALTH MONITORING ORCHESTRATOR ===============

class HealthMonitoringOrchestrator:
    """🎯 Orchestrateur principal health monitoring Creator Economy
    
    Factory pattern pour instanciation des systèmes de monitoring,
    configuration centralisée et routing intelligent selon Creator tier.
    Coordination multi-domaines avec optimisation performances et caching.
    """
    
    def __init__(self, config: CreatorEconomyHealthConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.system_metrics = SystemMetrics()
        self.monitoring_config = MonitoringConfig(
            health_check_interval=config.health_check_interval,
            performance_tracking=True,
            metrics_enabled=True
        )
        self.health_checks_manager = HealthChecksManager(self.monitoring_config)
        
        # Creator Economy specialized components
        self.creator_orchestrator = None
        self.performance_monitor = None
        self.ai_intelligence_engine = None
        self.content_pipeline_validator = None
        self.multi_format_tracker = None
        
        # Health monitoring registry
        self.health_monitors: Dict[str, Any] = {}
        self.active_monitors: Dict[str, bool] = {}
        self.monitoring_metrics: Dict[str, Any] = {}
        
        # Performance optimization
        self.cache_ttl = 60  # seconds
        self.cached_health_status: Dict[str, Any] = {}
        self.last_cache_update: Dict[str, datetime] = {}
        
        # Event handling
        self.health_event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        self.logger.info("🚀 Health Monitoring Orchestrator initialized")
    
    async def initialize(self) -> bool:
        """🔧 Initialisation complète du système de monitoring
        
        Returns:
            bool: True si initialisation réussie
        """
        try:
            self.logger.info("🔄 Initializing Creator Economy Health Monitoring System...")
            
            # Initialize core health checks manager
            if not await self.health_checks_manager.start():
                self.logger.error("❌ Failed to start core health checks manager")
                return False
            
            # Initialize Creator Economy components
            await self._initialize_creator_economy_components()
            
            # Setup health monitoring registry
            await self._setup_health_monitoring_registry()
            
            # Configure event handlers
            await self._configure_event_handlers()
            
            # Start monitoring loops
            await self._start_monitoring_loops()
            
            self.running = True
            self.logger.info("✅ Creator Economy Health Monitoring System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize health monitoring system: {e}")
            return False
    
    async def _initialize_creator_economy_components(self):
        """Initialiser les composants spécialisés Creator Economy"""
        try:
            # Creator Economy Health Orchestrator
            from .creator_economy_health_orchestrator import CreatorEconomyHealthOrchestrator
            self.creator_orchestrator = CreatorEconomyHealthOrchestrator(self.config)
            await self.creator_orchestrator.initialize()
            
            # Performance Monitor
            from .creator_performance_health_monitor import CreatorPerformanceHealthMonitor
            self.performance_monitor = CreatorPerformanceHealthMonitor(self.config)
            await self.performance_monitor.initialize()
            
            # AI/ML Intelligence Engine
            from .ai_ml_health_intelligence_engine import AIMLHealthIntelligenceEngine
            self.ai_intelligence_engine = AIMLHealthIntelligenceEngine(self.config)
            await self.ai_intelligence_engine.initialize()
            
            # Content Pipeline Validator
            from .creator_content_pipeline_health_validator import CreatorContentPipelineHealthValidator
            self.content_pipeline_validator = CreatorContentPipelineHealthValidator(self.config)
            await self.content_pipeline_validator.initialize()
            
            # Multi-Format Processing Tracker
            from .multi_format_processing_health_tracker import MultiFormatProcessingHealthTracker
            self.multi_format_tracker = MultiFormatProcessingHealthTracker(self.config)
            await self.multi_format_tracker.initialize()
            
            self.logger.info("✅ Creator Economy specialized components initialized")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Some Creator Economy components not yet implemented: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error initializing Creator Economy components: {e}")
            raise
    
    async def _setup_health_monitoring_registry(self):
        """Configuration du registre de monitoring"""
        # Register core monitors
        self.health_monitors.update({
            "system": self.health_checks_manager,
            "creator_economy": self.creator_orchestrator,
            "performance": self.performance_monitor,
            "ai_ml": self.ai_intelligence_engine,
            "content_pipeline": self.content_pipeline_validator,
            "multi_format": self.multi_format_tracker
        })
        
        # Initialize active status
        for monitor_name in self.health_monitors.keys():
            self.active_monitors[monitor_name] = True
        
        self.logger.info(f"📋 Health monitoring registry setup with {len(self.health_monitors)} monitors")
    
    async def _configure_event_handlers(self):
        """Configuration des gestionnaires d'événements"""
        # Critical health events
        self.health_event_handlers["critical_alert"] = [
            self._handle_critical_alert,
            self._trigger_auto_recovery,
            self._notify_operations_team
        ]
        
        # Performance degradation events
        self.health_event_handlers["performance_degradation"] = [
            self._handle_performance_degradation,
            self._optimize_resource_allocation,
            self._scale_infrastructure
        ]
        
        # Creator Economy specific events
        self.health_event_handlers["creator_health_issue"] = [
            self._handle_creator_health_issue,
            self._notify_creator_support,
            self._analyze_creator_impact
        ]
        
        self.logger.info("📡 Event handlers configured")
    
    async def _start_monitoring_loops(self):
        """Démarrage des boucles de monitoring"""
        # Start main health monitoring loop
        asyncio.create_task(self._health_monitoring_loop())
        
        # Start Creator Economy specific monitoring
        asyncio.create_task(self._creator_economy_monitoring_loop())
        
        # Start predictive analytics loop
        if self.config.predictive_analytics:
            asyncio.create_task(self._predictive_analytics_loop())
        
        # Start real-time monitoring
        if self.config.real_time_monitoring:
            asyncio.create_task(self._real_time_monitoring_loop())
        
        self.logger.info("🔄 Monitoring loops started")
    
    async def get_comprehensive_health_status(self, creator_tier: Optional[CreatorTier] = None) -> Dict[str, Any]:
        """🩺 Obtenir le statut de santé complet du système
        
        Args:
            creator_tier: Niveau de créateur pour filtrage spécialisé
            
        Returns:
            Dict avec statut de santé complet
        """
        try:
            # Check cache first
            cache_key = f"health_status_{creator_tier.value if creator_tier else 'all'}"
            if self._is_cache_valid(cache_key):
                return self.cached_health_status[cache_key]
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "creator_tier": creator_tier.value if creator_tier else "all",
                "system_health": {},
                "creator_economy_health": {},
                "performance_metrics": {},
                "ai_ml_health": {},
                "content_pipeline_health": {},
                "multi_format_health": {},
                "alerts": [],
                "recommendations": []
            }
            
            # Collect health data from all monitors
            for monitor_name, monitor in self.health_monitors.items():
                if monitor and self.active_monitors.get(monitor_name, False):
                    try:
                        monitor_health = await self._get_monitor_health(monitor, creator_tier)
                        health_status[f"{monitor_name}_health"] = monitor_health
                        
                        # Update overall status
                        if monitor_health.get("status") != "healthy":
                            health_status["overall_status"] = "degraded"
                    
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error getting health from {monitor_name}: {e}")
                        health_status[f"{monitor_name}_health"] = {
                            "status": "error",
                            "error": str(e)
                        }
            
            # Add business metrics
            if self.config.revenue_tracking:
                health_status["business_metrics"] = await self._get_business_health_metrics()
            
            # Add security status
            if self.config.security_audit_enabled:
                health_status["security_status"] = await self._get_security_health_status()
            
            # Generate AI-powered insights
            if self.config.ai_powered_insights:
                health_status["ai_insights"] = await self._generate_ai_insights(health_status)
            
            # Cache result
            self.cached_health_status[cache_key] = health_status
            self.last_cache_update[cache_key] = datetime.now()
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Error getting comprehensive health status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def trigger_health_check(self, monitor_name: str, check_type: str = "full") -> Dict[str, Any]:
        """🔍 Déclencher une vérification de santé spécifique
        
        Args:
            monitor_name: Nom du monitor à vérifier
            check_type: Type de vérification (full, quick, deep)
            
        Returns:
            Résultat de la vérification
        """
        try:
            if monitor_name not in self.health_monitors:
                return {
                    "status": "error",
                    "error": f"Monitor {monitor_name} not found"
                }
            
            monitor = self.health_monitors[monitor_name]
            if not monitor:
                return {
                    "status": "error", 
                    "error": f"Monitor {monitor_name} not initialized"
                }
            
            # Execute health check based on type
            if check_type == "quick":
                result = await self._quick_health_check(monitor)
            elif check_type == "deep":
                result = await self._deep_health_check(monitor)
            else:  # full
                result = await self._full_health_check(monitor)
            
            # Log result
            self.logger.info(f"🩺 Health check {monitor_name}:{check_type} - Status: {result.get('status')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering health check {monitor_name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def optimize_creator_tier_health(self, creator_tier: CreatorTier) -> Dict[str, Any]:
        """🎯 Optimisation santé spécialisée par tier de créateur
        
        Args:
            creator_tier: Niveau de créateur à optimiser
            
        Returns:
            Résultats d'optimisation
        """
        try:
            optimization_results = {
                "creator_tier": creator_tier.value,
                "timestamp": datetime.now().isoformat(),
                "optimizations_applied": [],
                "performance_improvements": {},
                "recommendations": []
            }
            
            # Tier-specific optimizations
            if creator_tier == CreatorTier.ELITE:
                # Elite creators need premium performance
                await self._apply_elite_optimizations(optimization_results)
            elif creator_tier == CreatorTier.ENTERPRISE:
                # Enterprise needs maximum reliability
                await self._apply_enterprise_optimizations(optimization_results)
            elif creator_tier in [CreatorTier.PREMIUM, CreatorTier.ESTABLISHED]:
                # Mid-tier creators need balanced performance
                await self._apply_balanced_optimizations(optimization_results)
            else:
                # Emerging creators need cost-effective solutions
                await self._apply_cost_effective_optimizations(optimization_results)
            
            self.logger.info(f"⚡ Applied {len(optimization_results['optimizations_applied'])} optimizations for {creator_tier.value}")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing creator tier health: {e}")
            return {
                "error": str(e),
                "creator_tier": creator_tier.value
            }
    
    async def shutdown(self) -> bool:
        """⏹️ Arrêt propre du système de monitoring
        
        Returns:
            bool: True si arrêt réussi
        """
        try:
            self.logger.info("🔄 Shutting down Creator Economy Health Monitoring System...")
            
            self.running = False
            
            # Stop core health checks manager
            if self.health_checks_manager:
                await self.health_checks_manager.stop()
            
            # Stop Creator Economy components
            for component_name, component in [
                ("creator_orchestrator", self.creator_orchestrator),
                ("performance_monitor", self.performance_monitor),
                ("ai_intelligence_engine", self.ai_intelligence_engine),
                ("content_pipeline_validator", self.content_pipeline_validator),
                ("multi_format_tracker", self.multi_format_tracker)
            ]:
                if component and hasattr(component, 'shutdown'):
                    try:
                        await component.shutdown()
                        self.logger.info(f"✅ {component_name} shutdown successfully")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error shutting down {component_name}: {e}")
            
            # Clear monitoring data
            self.health_monitors.clear()
            self.active_monitors.clear()
            self.cached_health_status.clear()
            
            self.logger.info("✅ Creator Economy Health Monitoring System shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")
            return False
    
    # =============== HELPER METHODS ===============
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifier validité du cache"""
        if cache_key not in self.cached_health_status:
            return False
        
        last_update = self.last_cache_update.get(cache_key)
        if not last_update:
            return False
        
        return (datetime.now() - last_update).total_seconds() < self.cache_ttl
    
    async def _get_monitor_health(self, monitor: Any, creator_tier: Optional[CreatorTier]) -> Dict[str, Any]:
        """Obtenir santé d'un monitor spécifique"""
        try:
            if hasattr(monitor, 'get_health_status'):
                return await monitor.get_health_status(creator_tier=creator_tier)
            elif hasattr(monitor, 'run_all_checks'):
                return await monitor.run_all_checks()
            else:
                return {"status": "unknown", "error": "No health check method available"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _health_monitoring_loop(self):
        """Boucle principale de monitoring"""
        while self.running:
            try:
                # Collect comprehensive health metrics
                health_status = await self.get_comprehensive_health_status()
                
                # Check for critical issues
                if health_status.get("overall_status") != "healthy":
                    await self._handle_health_degradation(health_status)
                
                # Update monitoring metrics
                self.monitoring_metrics["last_health_check"] = datetime.now().isoformat()
                self.monitoring_metrics["overall_status"] = health_status.get("overall_status")
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in health monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _creator_economy_monitoring_loop(self):
        """Boucle monitoring spécialisée Creator Economy"""
        while self.running:
            try:
                # Monitor all creator tiers
                for tier in CreatorTier:
                    tier_health = await self.get_comprehensive_health_status(tier)
                    
                    # Check tier-specific issues
                    if tier_health.get("overall_status") != "healthy":
                        await self._handle_creator_tier_issues(tier, tier_health)
                
                await asyncio.sleep(self.config.health_check_interval * 2)  # Less frequent
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in creator economy monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _predictive_analytics_loop(self):
        """Boucle analytics prédictives"""
        while self.running:
            try:
                # Run predictive analytics
                predictions = await self._run_predictive_analytics()
                
                # Act on predictions
                for prediction in predictions:
                    if prediction.get("confidence", 0) > 0.8:
                        await self._act_on_prediction(prediction)
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in predictive analytics loop: {e}")
                await asyncio.sleep(60)
    
    async def _real_time_monitoring_loop(self):
        """Boucle monitoring temps réel"""
        while self.running:
            try:
                # Real-time metrics collection
                real_time_metrics = await self._collect_real_time_metrics()
                
                # Detect anomalies
                anomalies = await self._detect_real_time_anomalies(real_time_metrics)
                
                # Handle anomalies immediately
                for anomaly in anomalies:
                    await self._handle_real_time_anomaly(anomaly)
                
                await asyncio.sleep(1)  # Every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in real-time monitoring loop: {e}")
                await asyncio.sleep(5)
    
    # =============== PLACEHOLDER METHODS (TO BE IMPLEMENTED) ===============
    
    async def _quick_health_check(self, monitor: Any) -> Dict[str, Any]:
        """Quick health check implementation"""
        return {"status": "healthy", "check_type": "quick"}
    
    async def _deep_health_check(self, monitor: Any) -> Dict[str, Any]:
        """Deep health check implementation"""
        return {"status": "healthy", "check_type": "deep"}
    
    async def _full_health_check(self, monitor: Any) -> Dict[str, Any]:
        """Full health check implementation"""
        return {"status": "healthy", "check_type": "full"}
    
    async def _get_business_health_metrics(self) -> Dict[str, Any]:
        """Get business health metrics"""
        return {"revenue_health": "stable", "engagement_health": "growing"}
    
    async def _get_security_health_status(self) -> Dict[str, Any]:
        """Get security health status"""
        return {"security_score": 95, "threats_detected": 0, "status": "secure"}
    
    async def _generate_ai_insights(self, health_status: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights"""
        return ["System performing optimally", "No anomalies detected"]
    
    async def _apply_elite_optimizations(self, results: Dict[str, Any]):
        """Apply optimizations for elite creators"""
        results["optimizations_applied"].append("Premium resource allocation")
        results["optimizations_applied"].append("Advanced caching enabled")
    
    async def _apply_enterprise_optimizations(self, results: Dict[str, Any]):
        """Apply optimizations for enterprise creators"""
        results["optimizations_applied"].append("High availability configuration")
        results["optimizations_applied"].append("Enterprise security protocols")
    
    async def _apply_balanced_optimizations(self, results: Dict[str, Any]):
        """Apply balanced optimizations"""
        results["optimizations_applied"].append("Balanced resource allocation")
    
    async def _apply_cost_effective_optimizations(self, results: Dict[str, Any]):
        """Apply cost-effective optimizations"""
        results["optimizations_applied"].append("Efficient resource utilization")
    
    async def _handle_critical_alert(self, alert_data: Dict[str, Any]):
        """Handle critical alert"""
        self.logger.critical(f"🚨 Critical alert handled: {alert_data}")
    
    async def _trigger_auto_recovery(self, alert_data: Dict[str, Any]):
        """Trigger automatic recovery"""
        self.logger.info(f"🔧 Auto recovery triggered: {alert_data}")
    
    async def _notify_operations_team(self, alert_data: Dict[str, Any]):
        """Notify operations team"""
        self.logger.info(f"📱 Operations team notified: {alert_data}")
    
    async def _handle_performance_degradation(self, perf_data: Dict[str, Any]):
        """Handle performance degradation"""
        self.logger.warning(f"⚠️ Performance degradation handled: {perf_data}")
    
    async def _optimize_resource_allocation(self, perf_data: Dict[str, Any]):
        """Optimize resource allocation"""
        self.logger.info(f"⚡ Resource allocation optimized: {perf_data}")
    
    async def _scale_infrastructure(self, perf_data: Dict[str, Any]):
        """Scale infrastructure"""
        self.logger.info(f"📈 Infrastructure scaled: {perf_data}")
    
    async def _handle_creator_health_issue(self, creator_data: Dict[str, Any]):
        """Handle creator health issue"""
        self.logger.warning(f"🎨 Creator health issue handled: {creator_data}")
    
    async def _notify_creator_support(self, creator_data: Dict[str, Any]):
        """Notify creator support team"""
        self.logger.info(f"🎯 Creator support notified: {creator_data}")
    
    async def _analyze_creator_impact(self, creator_data: Dict[str, Any]):
        """Analyze creator impact"""
        self.logger.info(f"📊 Creator impact analyzed: {creator_data}")
    
    async def _handle_health_degradation(self, health_status: Dict[str, Any]):
        """Handle overall health degradation"""
        self.logger.warning(f"⚠️ Health degradation detected: {health_status.get('overall_status')}")
    
    async def _handle_creator_tier_issues(self, tier: CreatorTier, health_status: Dict[str, Any]):
        """Handle creator tier specific issues"""
        self.logger.warning(f"🎯 {tier.value} tier issues detected")
    
    async def _run_predictive_analytics(self) -> List[Dict[str, Any]]:
        """Run predictive analytics"""
        return [{"prediction": "system_stable", "confidence": 0.95}]
    
    async def _act_on_prediction(self, prediction: Dict[str, Any]):
        """Act on prediction"""
        self.logger.info(f"🔮 Acting on prediction: {prediction}")
    
    async def _collect_real_time_metrics(self) -> Dict[str, Any]:
        """Collect real-time metrics"""
        return {"cpu": 45.2, "memory": 67.8, "network": "healthy"}
    
    async def _detect_real_time_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect real-time anomalies"""
        return []  # No anomalies detected
    
    async def _handle_real_time_anomaly(self, anomaly: Dict[str, Any]):
        """Handle real-time anomaly"""
        self.logger.warning(f"🚨 Real-time anomaly handled: {anomaly}")


# =============== FACTORY FUNCTIONS ===============

async def create_health_monitoring_orchestrator(
    config: Optional[CreatorEconomyHealthConfig] = None
) -> HealthMonitoringOrchestrator:
    """🏭 Factory pour créer un orchestrateur de monitoring
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        HealthMonitoringOrchestrator initialisé
    """
    if config is None:
        config = CreatorEconomyHealthConfig()
    
    orchestrator = HealthMonitoringOrchestrator(config)
    
    if await orchestrator.initialize():
        return orchestrator
    else:
        raise RuntimeError("Failed to initialize Health Monitoring Orchestrator")

@asynccontextmanager
async def health_monitoring_context(
    config: Optional[CreatorEconomyHealthConfig] = None
):
    """🔧 Context manager pour le monitoring
    
    Usage:
        async with health_monitoring_context() as orchestrator:
            health_status = await orchestrator.get_comprehensive_health_status()
    """
    orchestrator = await create_health_monitoring_orchestrator(config)
    try:
        yield orchestrator
    finally:
        await orchestrator.shutdown()


# =============== EXPORT MODULE ===============

__all__ = [
    "HealthMonitoringOrchestrator",
    "CreatorEconomyHealthConfig", 
    "CreatorTier",
    "CreatorFormat",
    "create_health_monitoring_orchestrator",
    "health_monitoring_context"
]