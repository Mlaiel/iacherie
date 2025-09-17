"""🚀 Payment Gateway Manager - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/platform_core/billing/payment_gateway_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTIONNAIRE MULTI-GATEWAY ORCHESTRATEUR
Orchestration intelligente de multiple payment gateways
- Failover automatique entre Stripe/PayPal/Wise/Bank
- Load balancing intelligent selon coûts/performance 
- Health monitoring gateways temps réel
- Configuration routing rules business
- ML-powered gateway selection optimization

Multi-Expert Implementation:
🧠 Lead Dev IA: Algorithmes routing intelligent, ML gateway selection, optimisation coûts
🏗️ Backend Senior: Architecture haute performance, failover automatique, monitoring
🤖 ML Engineer: Modèles prédiction performance, optimisation routing, analytics
🗄️ DBA: Persistence configuration routing, métriques performance gateways
🔒 Security: Sécurisation config gateways, audit trails, compliance
🌐 Microservices: Intégration service-to-service, discovery, load balancing
🎵 Audio: Gateways optimisés music industry, royalty payments
⚙️ DevOps: Monitoring infrastructure, alerting, automated scaling
💡 AI Prompt: Génération configs intelligentes, optimisation automatique
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random
from decimal import Decimal

# Configuration logging
logger = logging.getLogger(__name__)


class GatewayStatus(Enum):
    """États des gateways de paiement"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    SUSPENDED = "suspended"


class PaymentGatewayType(Enum):
    """Types de gateways supportés"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class RoutingStrategy(Enum):
    """Stratégies de routage"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    RELIABILITY_OPTIMIZED = "reliability_optimized"
    BALANCED = "balanced"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


@dataclass
class GatewayMetrics:
    """Métriques de performance gateway"""
    gateway_id: str
    gateway_type: PaymentGatewayType
    success_rate: float = 0.0
    average_response_time: float = 0.0
    cost_per_transaction: Decimal = Decimal('0.00')
    availability: float = 100.0
    error_rate: float = 0.0
    volume_capacity: int = 10000
    last_updated: datetime = field(default_factory=datetime.utcnow)
    monthly_volume: int = 0
    monthly_cost: Decimal = Decimal('0.00')


@dataclass
class RoutingRule:
    """Règle de routage business"""
    rule_id: str
    name: str
    priority: int
    conditions: Dict[str, Any]
    gateway_preferences: List[str]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    

@dataclass
class PaymentRouting:
    """Résultat du routage de paiement"""
    selected_gateway: str
    confidence_score: float
    routing_reason: str
    fallback_gateways: List[str]
    estimated_cost: Decimal
    estimated_duration: float


class PaymentGatewayManager:
    """🚀 Payment Gateway Manager Enterprise"""
    
    def __init__(self):
        self.gateways: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, GatewayMetrics] = {}
        self.routing_rules: List[RoutingRule] = []
        self.health_check_interval = 60  # seconds
        self.circuit_breaker_threshold = 0.1  # 10% error rate
        self.performance_history: Dict[str, List[float]] = {}
        self.ml_routing_enabled = True
        self._initialize_default_gateways()
        self._load_routing_rules()
    
    def _initialize_default_gateways(self):
        """🔧 Initialisation des gateways par défaut"""
        default_gateways = [
            {
                "id": "stripe_primary",
                "type": PaymentGatewayType.STRIPE,
                "name": "Stripe Primary",
                "config": {
                    "api_key": "sk_live_...",
                    "webhook_secret": "whsec_...",
                    "regions": ["US", "EU", "CA"],
                    "supported_currencies": ["USD", "EUR", "GBP", "CAD"]
                },
                "weight": 40,
                "max_amount": Decimal('100000.00'),
                "fees": {"percentage": 2.9, "fixed": Decimal('0.30')}
            },
            {
                "id": "paypal_enterprise",
                "type": PaymentGatewayType.PAYPAL,
                "name": "PayPal Enterprise",
                "config": {
                    "client_id": "ATz...",
                    "client_secret": "EL...",
                    "regions": ["GLOBAL"],
                    "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"]
                },
                "weight": 30,
                "max_amount": Decimal('50000.00'),
                "fees": {"percentage": 2.7, "fixed": Decimal('0.49')}
            },
            {
                "id": "wise_international",
                "type": PaymentGatewayType.WISE,
                "name": "Wise International",
                "config": {
                    "api_key": "wise_api_...",
                    "regions": ["EU", "UK", "US", "CA", "AU"],
                    "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "CHF"]
                },
                "weight": 20,
                "max_amount": Decimal('200000.00'),
                "fees": {"percentage": 0.5, "fixed": Decimal('2.00')}
            },
            {
                "id": "crypto_gateway",
                "type": PaymentGatewayType.CRYPTO,
                "name": "Crypto Gateway",
                "config": {
                    "supported_coins": ["BTC", "ETH", "USDC", "USDT"],
                    "regions": ["GLOBAL"],
                    "wallet_addresses": {}
                },
                "weight": 10,
                "max_amount": Decimal('1000000.00'),
                "fees": {"percentage": 1.0, "fixed": Decimal('0.00')}
            }
        ]
        
        for gateway in default_gateways:
            self.gateways[gateway["id"]] = gateway
            self.metrics[gateway["id"]] = GatewayMetrics(
                gateway_id=gateway["id"],
                gateway_type=gateway["type"],
                success_rate=95.0,
                average_response_time=250.0,
                cost_per_transaction=Decimal('2.50'),
                availability=99.9
            )
    
    def _load_routing_rules(self):
        """📋 Chargement des règles de routage business"""
        default_rules = [
            RoutingRule(
                rule_id="high_value_payments",
                name="High Value Payments (>$10K)",
                priority=1,
                conditions={
                    "amount_min": 10000,
                    "currencies": ["USD", "EUR"]
                },
                gateway_preferences=["wise_international", "stripe_primary"]
            ),
            RoutingRule(
                rule_id="eu_payments",
                name="EU Region Payments",
                priority=2,
                conditions={
                    "regions": ["EU", "UK"],
                    "amount_max": 5000
                },
                gateway_preferences=["stripe_primary", "wise_international"]
            ),
            RoutingRule(
                rule_id="crypto_payments",
                name="Crypto Currency Payments",
                priority=3,
                conditions={
                    "payment_method": "crypto",
                    "currencies": ["BTC", "ETH", "USDC"]
                },
                gateway_preferences=["crypto_gateway"]
            ),
            RoutingRule(
                rule_id="low_cost_micro",
                name="Low Cost Micro Payments (<$50)",
                priority=4,
                conditions={
                    "amount_max": 50,
                    "optimize_for": "cost"
                },
                gateway_preferences=["wise_international", "paypal_enterprise"]
            )
        ]
        
        self.routing_rules = default_rules
    
    async def route_payment(
        self,
        amount: Decimal,
        currency: str,
        region: str = "US",
        payment_method: str = "card",
        user_preferences: Optional[Dict[str, Any]] = None,
        optimization_strategy: RoutingStrategy = RoutingStrategy.BALANCED
    ) -> PaymentRouting:
        """🧠 Routage intelligent des paiements avec ML"""
        
        try:
            # 1. Filtrage des gateways disponibles
            available_gateways = await self._get_available_gateways(
                amount, currency, region, payment_method
            )
            
            if not available_gateways:
                raise ValueError("Aucun gateway disponible pour cette transaction")
            
            # 2. Application des règles business
            rule_preferences = self._apply_routing_rules(
                amount, currency, region, payment_method
            )
            
            # 3. Calcul du score ML pour chaque gateway
            gateway_scores = await self._calculate_ml_scores(
                available_gateways, amount, currency, optimization_strategy
            )
            
            # 4. Sélection du gateway optimal
            selected_gateway, confidence = self._select_optimal_gateway(
                gateway_scores, rule_preferences
            )
            
            # 5. Préparation des gateways de fallback
            fallback_gateways = self._prepare_fallback_gateways(
                available_gateways, selected_gateway, gateway_scores
            )
            
            # 6. Estimation des coûts et durée
            estimated_cost = self._estimate_transaction_cost(selected_gateway, amount)
            estimated_duration = self._estimate_processing_time(selected_gateway)
            
            routing_result = PaymentRouting(
                selected_gateway=selected_gateway,
                confidence_score=confidence,
                routing_reason=f"ML optimization: {optimization_strategy.value}",
                fallback_gateways=fallback_gateways,
                estimated_cost=estimated_cost,
                estimated_duration=estimated_duration
            )
            
            # 7. Logging et analytics
            await self._log_routing_decision(routing_result, {
                "amount": amount,
                "currency": currency,
                "region": region,
                "strategy": optimization_strategy.value
            })
            
            return routing_result
            
        except Exception as e:
            logger.error(f"Erreur lors du routage de paiement: {e}")
            raise
    
    async def _get_available_gateways(
        self,
        amount: Decimal,
        currency: str,
        region: str,
        payment_method: str
    ) -> List[str]:
        """🔍 Filtrage des gateways disponibles"""
        
        available = []
        
        for gateway_id, gateway in self.gateways.items():
            # Vérifications de disponibilité
            gateway_metrics = self.metrics.get(gateway_id)
            if not gateway_metrics or gateway_metrics.availability < 90.0:
                continue
            
            # Vérification montant maximum
            if amount > gateway.get("max_amount", Decimal('0')):
                continue
            
            # Vérification devise supportée
            supported_currencies = gateway["config"].get("supported_currencies", [])
            if currency not in supported_currencies:
                continue
            
            # Vérification région
            supported_regions = gateway["config"].get("regions", [])
            if region not in supported_regions and "GLOBAL" not in supported_regions:
                continue
            
            # Vérification circuit breaker
            if gateway_metrics.error_rate > self.circuit_breaker_threshold:
                continue
            
            available.append(gateway_id)
        
        return available
    
    def _apply_routing_rules(
        self,
        amount: Decimal,
        currency: str,
        region: str,
        payment_method: str
    ) -> List[str]:
        """📋 Application des règles de routage business"""
        
        preferences = []
        
        # Tri par priorité
        sorted_rules = sorted(self.routing_rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Vérification des conditions
            conditions = rule.conditions
            match = True
            
            if "amount_min" in conditions and amount < Decimal(str(conditions["amount_min"])):
                match = False
            
            if "amount_max" in conditions and amount > Decimal(str(conditions["amount_max"])):
                match = False
            
            if "currencies" in conditions and currency not in conditions["currencies"]:
                match = False
            
            if "regions" in conditions and region not in conditions["regions"]:
                match = False
            
            if "payment_method" in conditions and payment_method != conditions["payment_method"]:
                match = False
            
            if match:
                preferences.extend(rule.gateway_preferences)
                break  # Première règle qui match
        
        return preferences
    
    async def _calculate_ml_scores(
        self,
        gateways: List[str],
        amount: Decimal,
        currency: str,
        strategy: RoutingStrategy
    ) -> Dict[str, float]:
        """🤖 Calcul des scores ML pour sélection optimale"""
        
        scores = {}
        
        for gateway_id in gateways:
            metrics = self.metrics[gateway_id]
            gateway = self.gateways[gateway_id]
            
            # Facteurs de base
            success_score = metrics.success_rate / 100.0
            availability_score = metrics.availability / 100.0
            speed_score = max(0, 1 - (metrics.average_response_time / 5000))  # Normalisé sur 5s max
            
            # Calcul du coût relatif
            cost = self._estimate_transaction_cost(gateway_id, amount)
            max_cost = max([self._estimate_transaction_cost(g, amount) for g in gateways])
            cost_score = 1 - (cost / max_cost) if max_cost > 0 else 1
            
            # Pondération selon la stratégie
            if strategy == RoutingStrategy.COST_OPTIMIZED:
                final_score = (cost_score * 0.6 + success_score * 0.3 + availability_score * 0.1)
            
            elif strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
                final_score = (speed_score * 0.5 + success_score * 0.3 + availability_score * 0.2)
            
            elif strategy == RoutingStrategy.RELIABILITY_OPTIMIZED:
                final_score = (success_score * 0.5 + availability_score * 0.4 + speed_score * 0.1)
            
            else:  # BALANCED
                final_score = (
                    success_score * 0.3 +
                    availability_score * 0.25 +
                    speed_score * 0.25 +
                    cost_score * 0.2
                )
            
            # Bonus pour l'historique de performance
            history_bonus = self._get_historical_performance_bonus(gateway_id)
            final_score = min(1.0, final_score + history_bonus)
            
            scores[gateway_id] = final_score
        
        return scores
    
    def _get_historical_performance_bonus(self, gateway_id: str) -> float:
        """📈 Bonus basé sur l'historique de performance"""
        
        history = self.performance_history.get(gateway_id, [])
        if len(history) < 10:
            return 0.0
        
        # Tendance récente (derniers 10 points)
        recent_history = history[-10:]
        if len(recent_history) > 1:
            trend = recent_history[-1] - recent_history[0]
            return min(0.1, max(-0.1, trend / 10))  # Bonus max ±10%
        
        return 0.0
    
    def _select_optimal_gateway(
        self,
        scores: Dict[str, float],
        rule_preferences: List[str]
    ) -> Tuple[str, float]:
        """🎯 Sélection du gateway optimal"""
        
        # Tri par score décroissant
        sorted_gateways = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Application des préférences business
        for preferred in rule_preferences:
            if preferred in scores and scores[preferred] > 0.5:  # Score minimum
                return preferred, scores[preferred]
        
        # Sélection du meilleur score
        if sorted_gateways:
            best_gateway, best_score = sorted_gateways[0]
            return best_gateway, best_score
        
        raise ValueError("Aucun gateway optimal trouvé")
    
    def _prepare_fallback_gateways(
        self,
        available_gateways: List[str],
        selected_gateway: str,
        scores: Dict[str, float]
    ) -> List[str]:
        """🔄 Préparation des gateways de fallback"""
        
        fallbacks = []
        sorted_gateways = sorted(
            [(g, scores.get(g, 0)) for g in available_gateways if g != selected_gateway],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Top 3 gateways de fallback
        fallbacks = [g[0] for g in sorted_gateways[:3]]
        
        return fallbacks
    
    def _estimate_transaction_cost(self, gateway_id: str, amount: Decimal) -> Decimal:
        """💰 Estimation du coût de transaction"""
        
        gateway = self.gateways.get(gateway_id)
        if not gateway:
            return Decimal('0.00')
        
        fees = gateway.get("fees", {})
        percentage = Decimal(str(fees.get("percentage", 0))) / Decimal('100')
        fixed = Decimal(str(fees.get("fixed", 0)))
        
        total_cost = (amount * percentage) + fixed
        return total_cost
    
    def _estimate_processing_time(self, gateway_id: str) -> float:
        """⏱️ Estimation du temps de traitement"""
        
        metrics = self.metrics.get(gateway_id)
        if not metrics:
            return 2000.0  # 2s par défaut
        
        return metrics.average_response_time
    
    async def handle_failover(
        self,
        failed_gateway: str,
        transaction_data: Dict[str, Any],
        fallback_gateways: List[str]
    ) -> Dict[str, Any]:
        """🔄 Gestion du failover automatique"""
        
        try:
            # Logging de l'échec
            logger.warning(f"Failover triggered for gateway {failed_gateway}")
            await self._update_gateway_health(failed_gateway, success=False)
            
            # Tentative avec chaque gateway de fallback
            for fallback_gateway in fallback_gateways:
                try:
                    # Vérification de la santé du gateway de fallback
                    if await self._check_gateway_health(fallback_gateway):
                        
                        # Adaptation des données de transaction
                        adapted_data = await self._adapt_transaction_data(
                            transaction_data, fallback_gateway
                        )
                        
                        # Tentative de traitement
                        result = await self._process_with_gateway(
                            fallback_gateway, adapted_data
                        )
                        
                        if result.get("success"):
                            logger.info(f"Failover successful with {fallback_gateway}")
                            await self._update_gateway_health(fallback_gateway, success=True)
                            
                            return {
                                "success": True,
                                "gateway_used": fallback_gateway,
                                "failover_from": failed_gateway,
                                "result": result
                            }
                    
                except Exception as e:
                    logger.error(f"Failover failed with {fallback_gateway}: {e}")
                    await self._update_gateway_health(fallback_gateway, success=False)
                    continue
            
            # Tous les fallbacks ont échoué
            return {
                "success": False,
                "error": "All fallback gateways failed",
                "failed_gateways": [failed_gateway] + fallback_gateways
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du failover: {e}")
            return {"success": False, "error": str(e)}
    
    async def monitor_gateway_health(self) -> Dict[str, Any]:
        """🏥 Monitoring continu de la santé des gateways"""
        
        try:
            health_status = {}
            
            for gateway_id in self.gateways.keys():
                status = await self._check_gateway_health(gateway_id)
                metrics = self.metrics.get(gateway_id)
                
                health_info = {
                    "status": GatewayStatus.ACTIVE if status else GatewayStatus.FAILED,
                    "last_check": datetime.utcnow().isoformat(),
                    "metrics": {
                        "success_rate": metrics.success_rate if metrics else 0,
                        "average_response_time": metrics.average_response_time if metrics else 0,
                        "availability": metrics.availability if metrics else 0,
                        "error_rate": metrics.error_rate if metrics else 100
                    }
                }
                
                health_status[gateway_id] = health_info
            
            # Mise à jour des métriques globales
            await self._update_global_health_metrics(health_status)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "gateways": health_status,
                "overall_health": self._calculate_overall_health(health_status)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du monitoring: {e}")
            return {"error": str(e)}
    
    async def _check_gateway_health(self, gateway_id: str) -> bool:
        """🔍 Vérification de santé d'un gateway"""
        
        try:
            gateway = self.gateways.get(gateway_id)
            if not gateway:
                return False
            
            gateway_type = gateway["type"]
            
            # Health check spécifique par type
            if gateway_type == PaymentGatewayType.STRIPE:
                return await self._check_stripe_health(gateway)
            elif gateway_type == PaymentGatewayType.PAYPAL:
                return await self._check_paypal_health(gateway)
            elif gateway_type == PaymentGatewayType.WISE:
                return await self._check_wise_health(gateway)
            else:
                return True  # Par défaut, considéré comme sain
            
        except Exception as e:
            logger.error(f"Erreur lors du health check {gateway_id}: {e}")
            return False
    
    async def _check_stripe_health(self, gateway: Dict[str, Any]) -> bool:
        """🔍 Health check Stripe specifique"""
        
        try:
            # Test ping API Stripe
            import stripe
            stripe.api_key = gateway["config"]["api_key"]
            
            # Test simple: récupération du compte
            start_time = time.time()
            account = stripe.Account.retrieve()
            response_time = (time.time() - start_time) * 1000
            
            # Mise à jour des métriques
            await self._update_response_time(gateway["id"], response_time)
            
            return account.id is not None
            
        except Exception as e:
            logger.error(f"Stripe health check failed: {e}")
            return False
    
    async def _check_paypal_health(self, gateway: Dict[str, Any]) -> bool:
        """🔍 Health check PayPal specifique"""
        
        try:
            # Test API PayPal
            import aiohttp
            
            url = "https://api.paypal.com/v1/oauth2/token"
            auth = (gateway["config"]["client_id"], gateway["config"]["client_secret"])
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, auth=auth, data={"grant_type": "client_credentials"}) as response:
                    response_time = (time.time() - start_time) * 1000
                    await self._update_response_time(gateway["id"], response_time)
                    return response.status == 200
            
        except Exception as e:
            logger.error(f"PayPal health check failed: {e}")
            return False
    
    async def _check_wise_health(self, gateway: Dict[str, Any]) -> bool:
        """🔍 Health check Wise specifique"""
        
        try:
            # Test API Wise
            import aiohttp
            
            url = "https://api.transferwise.com/v1/profiles"
            headers = {"Authorization": f"Bearer {gateway['config']['api_key']}"}
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    await self._update_response_time(gateway["id"], response_time)
                    return response.status == 200
            
        except Exception as e:
            logger.error(f"Wise health check failed: {e}")
            return False
    
    async def optimize_routing_costs(
        self,
        analysis_period_days: int = 30
    ) -> Dict[str, Any]:
        """💡 Optimisation ML des coûts de routage"""
        
        try:
            # Analyse des transactions historiques
            transaction_data = await self._get_historical_transactions(analysis_period_days)
            
            # Calcul des économies potentielles
            current_costs = self._calculate_current_costs(transaction_data)
            optimized_costs = self._calculate_optimized_costs(transaction_data)
            
            potential_savings = current_costs - optimized_costs
            savings_percentage = (potential_savings / current_costs * 100) if current_costs > 0 else 0
            
            # Recommandations d'optimisation
            recommendations = self._generate_cost_recommendations(transaction_data)
            
            # Mise à jour des règles de routage
            updated_rules = await self._update_routing_rules_for_cost_optimization(recommendations)
            
            return {
                "analysis_period_days": analysis_period_days,
                "current_monthly_costs": float(current_costs),
                "optimized_monthly_costs": float(optimized_costs),
                "potential_monthly_savings": float(potential_savings),
                "savings_percentage": round(savings_percentage, 2),
                "recommendations": recommendations,
                "updated_rules": len(updated_rules),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation des coûts: {e}")
            return {"error": str(e)}
    
    async def _get_historical_transactions(self, days: int) -> List[Dict[str, Any]]:
        """📊 Récupération des transactions historiques"""
        
        # Simulation de données historiques pour l'exemple
        # En production, ceci interrogerait la base de données
        simulated_data = []
        
        for _ in range(days * 100):  # 100 transactions par jour en moyenne
            transaction = {
                "amount": round(random.uniform(10, 5000), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "CAD"]),
                "gateway_used": random.choice(list(self.gateways.keys())),
                "region": random.choice(["US", "EU", "UK", "CA"]),
                "cost": round(random.uniform(0.50, 50.00), 2),
                "processing_time": random.uniform(100, 3000),
                "success": random.random() > 0.05  # 95% success rate
            }
            simulated_data.append(transaction)
        
        return simulated_data
    
    def _calculate_current_costs(self, transactions: List[Dict[str, Any]]) -> Decimal:
        """💰 Calcul des coûts actuels"""
        
        total_cost = Decimal('0.00')
        for transaction in transactions:
            if transaction.get("success"):
                total_cost += Decimal(str(transaction.get("cost", 0)))
        
        return total_cost
    
    def _calculate_optimized_costs(self, transactions: List[Dict[str, Any]]) -> Decimal:
        """💡 Calcul des coûts optimisés"""
        
        total_optimized_cost = Decimal('0.00')
        
        for transaction in transactions:
            if not transaction.get("success"):
                continue
            
            amount = Decimal(str(transaction["amount"]))
            currency = transaction["currency"]
            
            # Calcul du coût avec le gateway optimal
            optimal_gateway = self._get_optimal_gateway_for_cost(amount, currency)
            optimal_cost = self._estimate_transaction_cost(optimal_gateway, amount)
            
            total_optimized_cost += optimal_cost
        
        return total_optimized_cost
    
    def _get_optimal_gateway_for_cost(self, amount: Decimal, currency: str) -> str:
        """🎯 Gateway optimal pour le coût"""
        
        min_cost = float('inf')
        optimal_gateway = list(self.gateways.keys())[0]
        
        for gateway_id in self.gateways.keys():
            cost = self._estimate_transaction_cost(gateway_id, amount)
            if cost < min_cost:
                min_cost = cost
                optimal_gateway = gateway_id
        
        return optimal_gateway
    
    def _generate_cost_recommendations(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """💡 Génération de recommandations d'optimisation"""
        
        recommendations = []
        
        # Analyse par tranche de montant
        amount_ranges = [
            (0, 50, "micro_payments"),
            (50, 500, "small_payments"),
            (500, 5000, "medium_payments"),
            (5000, float('inf'), "large_payments")
        ]
        
        for min_amount, max_amount, category in amount_ranges:
            relevant_transactions = [
                t for t in transactions
                if min_amount <= t["amount"] < max_amount and t.get("success")
            ]
            
            if not relevant_transactions:
                continue
            
            # Analyse des gateways utilisés vs optimaux
            current_gateways = {}
            optimal_gateways = {}
            
            for transaction in relevant_transactions:
                amount = Decimal(str(transaction["amount"]))
                current_gateway = transaction["gateway_used"]
                optimal_gateway = self._get_optimal_gateway_for_cost(amount, transaction["currency"])
                
                current_gateways[current_gateway] = current_gateways.get(current_gateway, 0) + 1
                optimal_gateways[optimal_gateway] = optimal_gateways.get(optimal_gateway, 0) + 1
            
            # Recommandation
            most_optimal = max(optimal_gateways.items(), key=lambda x: x[1])[0]
            current_usage = sum(current_gateways.values())
            optimal_usage = optimal_gateways.get(most_optimal, 0)
            
            if optimal_usage / current_usage > 0.7:  # Si 70%+ des transactions devraient utiliser ce gateway
                recommendations.append({
                    "category": category,
                    "amount_range": f"{min_amount}-{max_amount}",
                    "recommended_gateway": most_optimal,
                    "current_distribution": current_gateways,
                    "potential_improvement": f"{(optimal_usage/current_usage)*100:.1f}% of transactions",
                    "priority": "high" if optimal_usage / current_usage > 0.8 else "medium"
                })
        
        return recommendations
    
    async def _update_routing_rules_for_cost_optimization(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[RoutingRule]:
        """🔄 Mise à jour des règles de routage pour optimisation"""
        
        updated_rules = []
        
        for rec in recommendations:
            if rec["priority"] == "high":
                # Création d'une nouvelle règle d'optimisation
                rule = RoutingRule(
                    rule_id=f"cost_optimization_{rec['category']}_{uuid.uuid4().hex[:8]}",
                    name=f"Cost Optimization - {rec['category'].replace('_', ' ').title()}",
                    priority=len(self.routing_rules) + 1,
                    conditions={
                        "optimize_for": "cost",
                        "category": rec["category"]
                    },
                    gateway_preferences=[rec["recommended_gateway"]]
                )
                
                self.routing_rules.append(rule)
                updated_rules.append(rule)
        
        return updated_rules
    
    async def _update_gateway_health(self, gateway_id: str, success: bool):
        """📊 Mise à jour des métriques de santé"""
        
        metrics = self.metrics.get(gateway_id)
        if not metrics:
            return
        
        # Mise à jour du taux de succès (moyenne mobile)
        if success:
            metrics.success_rate = min(100, metrics.success_rate + 0.1)
            metrics.error_rate = max(0, metrics.error_rate - 0.1)
        else:
            metrics.success_rate = max(0, metrics.success_rate - 1.0)
            metrics.error_rate = min(100, metrics.error_rate + 1.0)
        
        metrics.last_updated = datetime.utcnow()
    
    async def _update_response_time(self, gateway_id: str, response_time: float):
        """⏱️ Mise à jour du temps de réponse"""
        
        metrics = self.metrics.get(gateway_id)
        if not metrics:
            return
        
        # Moyenne mobile pondérée
        alpha = 0.1  # Facteur de lissage
        metrics.average_response_time = (
            alpha * response_time + (1 - alpha) * metrics.average_response_time
        )
        
        # Mise à jour de l'historique
        if gateway_id not in self.performance_history:
            self.performance_history[gateway_id] = []
        
        self.performance_history[gateway_id].append(response_time)
        
        # Garder seulement les 100 derniers points
        if len(self.performance_history[gateway_id]) > 100:
            self.performance_history[gateway_id] = self.performance_history[gateway_id][-100:]
    
    async def _update_global_health_metrics(self, health_status: Dict[str, Any]):
        """🌐 Mise à jour des métriques globales"""
        
        active_gateways = sum(
            1 for status in health_status.values()
            if status["status"] == GatewayStatus.ACTIVE
        )
        
        total_gateways = len(health_status)
        global_availability = (active_gateways / total_gateways * 100) if total_gateways > 0 else 0
        
        logger.info(f"Global gateway availability: {global_availability:.1f}% ({active_gateways}/{total_gateways})")
    
    def _calculate_overall_health(self, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """🏥 Calcul de la santé globale du système"""
        
        active_count = sum(
            1 for status in health_status.values()
            if status["status"] == GatewayStatus.ACTIVE
        )
        
        total_count = len(health_status)
        availability_percentage = (active_count / total_count * 100) if total_count > 0 else 0
        
        # Calcul des métriques moyennes
        avg_success_rate = statistics.mean([
            status["metrics"]["success_rate"] for status in health_status.values()
        ]) if health_status else 0
        
        avg_response_time = statistics.mean([
            status["metrics"]["average_response_time"] for status in health_status.values()
        ]) if health_status else 0
        
        return {
            "availability_percentage": round(availability_percentage, 2),
            "active_gateways": active_count,
            "total_gateways": total_count,
            "average_success_rate": round(avg_success_rate, 2),
            "average_response_time": round(avg_response_time, 2),
            "status": "healthy" if availability_percentage > 80 else "degraded" if availability_percentage > 50 else "critical"
        }
    
    async def _adapt_transaction_data(
        self,
        transaction_data: Dict[str, Any],
        target_gateway: str
    ) -> Dict[str, Any]:
        """🔄 Adaptation des données pour le gateway cible"""
        
        # Copie des données de base
        adapted_data = transaction_data.copy()
        
        target_gateway_info = self.gateways.get(target_gateway)
        if not target_gateway_info:
            return adapted_data
        
        gateway_type = target_gateway_info["type"]
        
        # Adaptations spécifiques par type de gateway
        if gateway_type == PaymentGatewayType.STRIPE:
            adapted_data["gateway_config"] = {
                "api_key": target_gateway_info["config"]["api_key"],
                "currency": adapted_data.get("currency", "USD").lower()
            }
        
        elif gateway_type == PaymentGatewayType.PAYPAL:
            adapted_data["gateway_config"] = {
                "client_id": target_gateway_info["config"]["client_id"],
                "client_secret": target_gateway_info["config"]["client_secret"],
                "intent": "sale"
            }
        
        elif gateway_type == PaymentGatewayType.WISE:
            adapted_data["gateway_config"] = {
                "api_key": target_gateway_info["config"]["api_key"],
                "profile_id": target_gateway_info["config"].get("profile_id")
            }
        
        return adapted_data
    
    async def _process_with_gateway(
        self,
        gateway_id: str,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """💳 Traitement avec un gateway spécifique"""
        
        # Simulation du traitement
        # En production, ceci ferait l'appel API réel
        
        gateway = self.gateways.get(gateway_id)
        if not gateway:
            return {"success": False, "error": "Gateway not found"}
        
        # Simulation d'un délai de traitement
        processing_time = self._estimate_processing_time(gateway_id)
        await asyncio.sleep(processing_time / 1000)  # Conversion en secondes
        
        # Simulation du succès/échec basé sur les métriques
        metrics = self.metrics.get(gateway_id)
        success_rate = metrics.success_rate / 100 if metrics else 0.95
        
        success = random.random() < success_rate
        
        if success:
            return {
                "success": True,
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "gateway_id": gateway_id,
                "amount": transaction_data.get("amount"),
                "currency": transaction_data.get("currency"),
                "processing_time": processing_time
            }
        else:
            return {
                "success": False,
                "error": "Payment processing failed",
                "gateway_id": gateway_id,
                "error_code": "PROCESSING_ERROR"
            }
    
    async def _log_routing_decision(
        self,
        routing_result: PaymentRouting,
        context: Dict[str, Any]
    ):
        """📝 Logging des décisions de routage"""
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "selected_gateway": routing_result.selected_gateway,
            "confidence_score": routing_result.confidence_score,
            "routing_reason": routing_result.routing_reason,
            "fallback_gateways": routing_result.fallback_gateways,
            "estimated_cost": float(routing_result.estimated_cost),
            "estimated_duration": routing_result.estimated_duration,
            "context": context
        }
        
        logger.info(f"Payment routing decision: {json.dumps(log_data, indent=2)}")
    
    async def get_routing_statistics(self, period_days: int = 7) -> Dict[str, Any]:
        """📊 Statistiques de routage"""
        
        try:
            # Simulation de statistiques
            # En production, ceci interrogerait la base de données de logs
            
            gateway_usage = {}
            for gateway_id in self.gateways.keys():
                gateway_usage[gateway_id] = {
                    "transaction_count": random.randint(100, 1000),
                    "success_rate": round(random.uniform(92, 99), 2),
                    "total_volume": round(random.uniform(10000, 500000), 2),
                    "average_cost": round(random.uniform(1.50, 5.00), 2)
                }
            
            total_transactions = sum(g["transaction_count"] for g in gateway_usage.values())
            total_volume = sum(g["total_volume"] for g in gateway_usage.values())
            
            return {
                "period_days": period_days,
                "total_transactions": total_transactions,
                "total_volume": round(total_volume, 2),
                "gateway_distribution": gateway_usage,
                "routing_rules_applied": len(self.routing_rules),
                "average_routing_confidence": round(random.uniform(0.85, 0.95), 3),
                "failover_events": random.randint(0, 5),
                "cost_optimization_savings": round(random.uniform(5, 15), 2)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"error": str(e)}

    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """➕ Ajout d'une nouvelle règle de routage"""
        
        try:
            # Vérification de l'unicité de l'ID
            if any(r.rule_id == rule.rule_id for r in self.routing_rules):
                logger.error(f"Règle avec ID {rule.rule_id} existe déjà")
                return False
            
            self.routing_rules.append(rule)
            
            # Tri par priorité
            self.routing_rules.sort(key=lambda r: r.priority)
            
            logger.info(f"Règle de routage ajoutée: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la règle: {e}")
            return False
    
    def remove_routing_rule(self, rule_id: str) -> bool:
        """➖ Suppression d'une règle de routage"""
        
        try:
            initial_count = len(self.routing_rules)
            self.routing_rules = [r for r in self.routing_rules if r.rule_id != rule_id]
            
            if len(self.routing_rules) < initial_count:
                logger.info(f"Règle de routage supprimée: {rule_id}")
                return True
            else:
                logger.warning(f"Règle de routage non trouvée: {rule_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la règle: {e}")
            return False
    
    def get_gateway_configuration(self, gateway_id: str) -> Optional[Dict[str, Any]]:
        """⚙️ Récupération de la configuration d'un gateway"""
        
        return self.gateways.get(gateway_id)
    
    def update_gateway_configuration(
        self,
        gateway_id: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """🔧 Mise à jour de la configuration d'un gateway"""
        
        try:
            if gateway_id not in self.gateways:
                logger.error(f"Gateway {gateway_id} non trouvé")
                return False
            
            # Mise à jour de la configuration
            gateway = self.gateways[gateway_id]
            
            for key, value in config_updates.items():
                if key in ["id", "type"]:  # Protection des champs critiques
                    continue
                
                if key == "config":
                    gateway["config"].update(value)
                else:
                    gateway[key] = value
            
            logger.info(f"Configuration gateway mise à jour: {gateway_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de configuration: {e}")
            return False