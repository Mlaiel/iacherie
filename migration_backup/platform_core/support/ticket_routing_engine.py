"""🚀 Ticket Routing Engine - Intelligent Distribution Enterprise
=================================================================
Module: backend/platform_core/support/ticket_routing_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🏗️ ENGINE ROUTING INTELLIGENT TICKETS ENTERPRISE
Système de distribution intelligente avec ML et optimisation
- Classification automatique tickets avec Machine Learning
- Routing optimal selon expertise agents et workload
- Load balancing dynamique avec prédiction capacité
- SLA enforcement automatique avec escalation
- Analytics performance routing en temps réel
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

logger = logging.getLogger(__name__)


class TicketCategory(Enum):
    """Catégories tickets détectées par ML"""
    TECHNICAL_ISSUE = "technical_issue"
    BILLING_SUPPORT = "billing_support" 
    ACCOUNT_MANAGEMENT = "account_management"
    CONTENT_COPYRIGHT = "content_copyright"
    FEATURE_REQUEST = "feature_request"
    COLLABORATION_HELP = "collaboration_help"
    MONETIZATION_SUPPORT = "monetization_support"
    SEO_OPTIMIZATION = "seo_optimization"
    PLATFORM_INTEGRATION = "platform_integration"
    EMERGENCY_CRITICAL = "emergency_critical"


class AgentSpecialty(Enum):
    """Spécialités agents support"""
    TECHNICAL_SPECIALIST = "technical_specialist"
    BILLING_SPECIALIST = "billing_specialist"
    CREATOR_SUCCESS_MANAGER = "creator_success_manager"
    COPYRIGHT_LEGAL_EXPERT = "copyright_legal_expert"
    PRODUCT_SPECIALIST = "product_specialist"
    GENERAL_SUPPORT = "general_support"
    SENIOR_ESCALATION = "senior_escalation"


class TicketPriority(Enum):
    """Priorités avec SLA enforcement"""
    CRITICAL = "critical"  # 15 minutes
    HIGH = "high"         # 1 hour
    MEDIUM = "medium"     # 4 hours
    LOW = "low"          # 24 hours


@dataclass
class SupportAgent:
    """Profil agent support avec capacités"""
    agent_id: str
    name: str
    specialty: AgentSpecialty
    languages: List[str]
    creator_types_expertise: List[str]  # musician, blogger, photographer
    current_workload: int = 0
    max_capacity: int = 10
    avg_resolution_time: timedelta = field(default_factory=lambda: timedelta(hours=2))
    satisfaction_rating: float = 4.5
    availability_schedule: Dict[str, List[Tuple[int, int]]] = field(default_factory=dict)
    is_online: bool = True
    last_activity: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TicketRoutingRequest:
    """Requête routing ticket avec contexte"""
    ticket_id: str
    content: str
    creator_type: str
    creator_language: str
    creator_tier: str  # free, pro, enterprise
    urgency_indicators: List[str]
    created_at: datetime
    customer_sentiment: float = 0.0
    previous_agent_id: Optional[str] = None
    escalation_level: int = 0
    sla_deadline: Optional[datetime] = None


@dataclass
class RoutingDecision:
    """Décision routing avec justification"""
    assigned_agent_id: str
    agent_specialty: AgentSpecialty
    predicted_category: TicketCategory
    confidence_score: float
    routing_reason: str
    estimated_resolution_time: timedelta
    sla_deadline: datetime
    priority_level: TicketPriority
    backup_agents: List[str] = field(default_factory=list)


class TicketRoutingEngine:
    """🎯 Engine Routing Intelligent Tickets Enterprise
    
    Système ML-powered pour distribution optimale:
    - Classification tickets avec NLP et ML
    - Matching optimal agent-ticket avec scoring
    - Load balancing prédictif avec capacité
    - SLA enforcement automatique
    - Learning continu pour amélioration performance
    """
    
    def __init__(self):
        self.agents: Dict[str, SupportAgent] = {}
        self.classification_model = None
        self.routing_analytics = RoutingAnalytics()
        self.sla_thresholds = {
            TicketPriority.CRITICAL: timedelta(minutes=15),
            TicketPriority.HIGH: timedelta(hours=1),
            TicketPriority.MEDIUM: timedelta(hours=4),
            TicketPriority.LOW: timedelta(hours=24)
        }
        self.category_to_specialty_mapping = self._initialize_category_mappings()
        self.workload_predictor = WorkloadPredictor()
        
    def _initialize_category_mappings(self) -> Dict[TicketCategory, List[AgentSpecialty]]:
        """🎯 Mapping catégories vers spécialités agents"""
        return {
            TicketCategory.TECHNICAL_ISSUE: [
                AgentSpecialty.TECHNICAL_SPECIALIST,
                AgentSpecialty.PRODUCT_SPECIALIST
            ],
            TicketCategory.BILLING_SUPPORT: [
                AgentSpecialty.BILLING_SPECIALIST,
                AgentSpecialty.GENERAL_SUPPORT
            ],
            TicketCategory.CONTENT_COPYRIGHT: [
                AgentSpecialty.COPYRIGHT_LEGAL_EXPERT,
                AgentSpecialty.CREATOR_SUCCESS_MANAGER
            ],
            TicketCategory.COLLABORATION_HELP: [
                AgentSpecialty.CREATOR_SUCCESS_MANAGER,
                AgentSpecialty.PRODUCT_SPECIALIST
            ],
            TicketCategory.MONETIZATION_SUPPORT: [
                AgentSpecialty.CREATOR_SUCCESS_MANAGER,
                AgentSpecialty.BILLING_SPECIALIST
            ],
            TicketCategory.EMERGENCY_CRITICAL: [
                AgentSpecialty.SENIOR_ESCALATION,
                AgentSpecialty.TECHNICAL_SPECIALIST
            ]
        }

    async def initialize_ml_models(self, training_data_path: Optional[str] = None) -> None:
        """🤖 Initialisation modèles ML pour classification"""
        try:
            if training_data_path:
                # Chargement modèle pré-entraîné
                self.classification_model = joblib.load(training_data_path)
                logger.info("Modèle ML classification chargé avec succès")
            else:
                # Initialisation modèle par défaut
                self.classification_model = Pipeline([
                    ('tfidf', TfidfVectorizer(
                        max_features=5000,
                        stop_words='english',
                        ngram_range=(1, 2)
                    )),
                    ('classifier', MultinomialNB(alpha=0.1))
                ])
                
                # Entraînement avec données synthétiques de base
                await self._train_initial_model()
                logger.info("Modèle ML initialisé avec données synthétiques")
                
        except Exception as e:
            logger.error(f"Erreur initialisation ML: {e}")

    async def register_agent(self, agent: SupportAgent) -> None:
        """👥 Enregistrement agent avec validation capacités"""
        try:
            # Validation profil agent
            if not agent.agent_id or not agent.specialty:
                raise ValueError("ID agent et spécialité requis")
                
            # Mise à jour disponibilité
            agent.last_activity = datetime.utcnow()
            agent.is_online = True
            
            self.agents[agent.agent_id] = agent
            
            logger.info(f"Agent {agent.name} enregistré - Spécialité: {agent.specialty.value}")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement agent: {e}")

    async def route_ticket(self, request: TicketRoutingRequest) -> RoutingDecision:
        """🎯 Routing intelligent ticket avec ML et optimisation
        
        Args:
            request: Requête routing avec contexte ticket
            
        Returns:
            RoutingDecision: Décision routing optimale avec justification
        """
        try:
            # 1. Classification ticket avec ML
            predicted_category, confidence = await self._classify_ticket_category(
                request.content, request.creator_type
            )
            
            # 2. Détermination priorité automatique
            priority_level = await self._determine_priority(request, predicted_category)
            
            # 3. Calcul deadline SLA
            sla_deadline = request.created_at + self.sla_thresholds[priority_level]
            
            # 4. Sélection agent optimal
            optimal_agent = await self._select_optimal_agent(
                request, predicted_category, priority_level
            )
            
            if not optimal_agent:
                # Escalation automatique si aucun agent disponible
                optimal_agent = await self._handle_no_agent_available(request)
                
            # 5. Mise à jour workload agent
            await self._update_agent_workload(optimal_agent.agent_id, increment=1)
            
            # 6. Construction décision routing
            routing_decision = RoutingDecision(
                assigned_agent_id=optimal_agent.agent_id,
                agent_specialty=optimal_agent.specialty,
                predicted_category=predicted_category,
                confidence_score=confidence,
                routing_reason=self._generate_routing_reason(optimal_agent, predicted_category),
                estimated_resolution_time=optimal_agent.avg_resolution_time,
                sla_deadline=sla_deadline,
                priority_level=priority_level,
                backup_agents=await self._get_backup_agents(optimal_agent, predicted_category)
            )
            
            # 7. Analytics et learning
            await self.routing_analytics.record_routing_decision(request, routing_decision)
            
            logger.info(f"Ticket {request.ticket_id} routé vers {optimal_agent.name}")
            return routing_decision
            
        except Exception as e:
            logger.error(f"Erreur routing ticket: {e}")
            return await self._generate_fallback_routing(request)

    async def _classify_ticket_category(
        self, 
        content: str, 
        creator_type: str
    ) -> Tuple[TicketCategory, float]:
        """🧠 Classification ML ticket avec contexte créateur"""
        try:
            if not self.classification_model:
                # Classification basique par mots-clés si pas de ML
                return await self._classify_by_keywords(content)
                
            # Enrichissement contenu avec contexte créateur
            enriched_content = f"[{creator_type}] {content}"
            
            # Prédiction ML
            prediction = self.classification_model.predict([enriched_content])[0]
            probabilities = self.classification_model.predict_proba([enriched_content])[0]
            confidence = max(probabilities)
            
            # Conversion vers enum
            try:
                category = TicketCategory(prediction)
            except ValueError:
                category = TicketCategory.GENERAL_SUPPORT
                confidence = 0.5
                
            return category, confidence
            
        except Exception as e:
            logger.error(f"Erreur classification ML: {e}")
            return TicketCategory.GENERAL_SUPPORT, 0.3

    async def _classify_by_keywords(self, content: str) -> Tuple[TicketCategory, float]:
        """🔍 Classification fallback par mots-clés"""
        content_lower = content.lower()
        
        keyword_mappings = {
            TicketCategory.TECHNICAL_ISSUE: [
                "bug", "error", "crash", "broken", "not working", "issue", "problem"
            ],
            TicketCategory.BILLING_SUPPORT: [
                "billing", "payment", "invoice", "charge", "subscription", "refund"
            ],
            TicketCategory.CONTENT_COPYRIGHT: [
                "copyright", "dmca", "stolen", "plagiarism", "infringement", "legal"
            ],
            TicketCategory.COLLABORATION_HELP: [
                "collaborate", "share", "invite", "team", "project", "together"
            ],
            TicketCategory.MONETIZATION_SUPPORT: [
                "monetize", "earnings", "revenue", "ads", "sponsorship", "income"
            ],
            TicketCategory.EMERGENCY_CRITICAL: [
                "urgent", "critical", "emergency", "asap", "immediately", "escalate"
            ]
        }
        
        best_category = TicketCategory.GENERAL_SUPPORT
        best_score = 0.0
        
        for category, keywords in keyword_mappings.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > best_score:
                best_score = score
                best_category = category
                
        confidence = min(0.9, best_score / 10)  # Normalisation score
        return best_category, confidence

    async def _determine_priority(
        self, 
        request: TicketRoutingRequest, 
        category: TicketCategory
    ) -> TicketPriority:
        """⚡ Détermination priorité automatique multi-facteurs"""
        
        priority_score = 0
        
        # 1. Facteur catégorie
        category_priorities = {
            TicketCategory.EMERGENCY_CRITICAL: 100,
            TicketCategory.TECHNICAL_ISSUE: 60,
            TicketCategory.BILLING_SUPPORT: 50,
            TicketCategory.CONTENT_COPYRIGHT: 70,
            TicketCategory.COLLABORATION_HELP: 30,
            TicketCategory.MONETIZATION_SUPPORT: 40
        }
        priority_score += category_priorities.get(category, 20)
        
        # 2. Facteur tier créateur
        tier_bonuses = {
            "enterprise": 40,
            "pro": 20,
            "free": 0
        }
        priority_score += tier_bonuses.get(request.creator_tier, 0)
        
        # 3. Facteur sentiment négatif
        if request.customer_sentiment < -0.3:
            priority_score += 30
            
        # 4. Facteur indicateurs urgence
        urgency_keywords = ["urgent", "critical", "asap", "emergency", "broken"]
        if any(keyword in " ".join(request.urgency_indicators).lower() for keyword in urgency_keywords):
            priority_score += 50
            
        # 5. Facteur escalation précédente
        priority_score += request.escalation_level * 25
        
        # Conversion score vers priorité
        if priority_score >= 150:
            return TicketPriority.CRITICAL
        elif priority_score >= 100:
            return TicketPriority.HIGH
        elif priority_score >= 50:
            return TicketPriority.MEDIUM
        else:
            return TicketPriority.LOW

    async def _select_optimal_agent(
        self,
        request: TicketRoutingRequest,
        category: TicketCategory,
        priority: TicketPriority
    ) -> Optional[SupportAgent]:
        """🎯 Sélection agent optimal avec scoring multi-critères"""
        
        # Filtrage agents candidats
        candidate_agents = await self._filter_candidate_agents(request, category)
        
        if not candidate_agents:
            return None
            
        # Scoring multi-critères pour chaque agent
        agent_scores = []
        
        for agent in candidate_agents:
            score = await self._calculate_agent_score(agent, request, category, priority)
            agent_scores.append((agent, score))
            
        # Tri par score décroissant
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        return agent_scores[0][0] if agent_scores else None

    async def _filter_candidate_agents(
        self,
        request: TicketRoutingRequest,
        category: TicketCategory
    ) -> List[SupportAgent]:
        """🔍 Filtrage agents candidats selon critères"""
        
        candidates = []
        required_specialties = self.category_to_specialty_mapping.get(category, [])
        
        for agent in self.agents.values():
            # Vérifications de base
            if not agent.is_online:
                continue
                
            if agent.current_workload >= agent.max_capacity:
                continue
                
            # Vérification spécialité
            if required_specialties and agent.specialty not in required_specialties:
                continue
                
            # Vérification langue
            if request.creator_language not in agent.languages:
                continue
                
            # Vérification expertise type créateur
            if request.creator_type not in agent.creator_types_expertise:
                # Accepter agents généralistes
                if agent.specialty != AgentSpecialty.GENERAL_SUPPORT:
                    continue
                    
            candidates.append(agent)
            
        return candidates

    async def _calculate_agent_score(
        self,
        agent: SupportAgent,
        request: TicketRoutingRequest,
        category: TicketCategory,
        priority: TicketPriority
    ) -> float:
        """📊 Calcul score agent multi-critères"""
        
        score = 0.0
        
        # 1. Score spécialité (40%)
        if agent.specialty in self.category_to_specialty_mapping.get(category, []):
            score += 40.0
            
        # 2. Score workload (25%) - Moins c'est mieux
        workload_ratio = agent.current_workload / agent.max_capacity
        score += 25.0 * (1.0 - workload_ratio)
        
        # 3. Score satisfaction (20%)
        score += 20.0 * (agent.satisfaction_rating / 5.0)
        
        # 4. Score expertise créateur (10%)
        if request.creator_type in agent.creator_types_expertise:
            score += 10.0
            
        # 5. Score temps résolution (5%) - Plus rapide c'est mieux
        avg_hours = agent.avg_resolution_time.total_seconds() / 3600
        if avg_hours < 1:
            score += 5.0
        elif avg_hours < 4:
            score += 3.0
        elif avg_hours < 24:
            score += 1.0
            
        # Bonus éviter re-assignment
        if request.previous_agent_id and request.previous_agent_id != agent.agent_id:
            score += 5.0
            
        return score

    async def _update_agent_workload(self, agent_id: str, increment: int = 1) -> None:
        """📈 Mise à jour workload agent avec prédiction"""
        if agent_id in self.agents:
            self.agents[agent_id].current_workload += increment
            self.agents[agent_id].last_activity = datetime.utcnow()
            
            # Prédiction workload futur
            await self.workload_predictor.update_agent_workload(agent_id, increment)

    async def _get_backup_agents(
        self,
        primary_agent: SupportAgent,
        category: TicketCategory
    ) -> List[str]:
        """🔄 Sélection agents backup en cas d'indisponibilité"""
        
        backup_agents = []
        required_specialties = self.category_to_specialty_mapping.get(category, [])
        
        for agent in self.agents.values():
            if agent.agent_id == primary_agent.agent_id:
                continue
                
            if not agent.is_online:
                continue
                
            # Même spécialité ou senior
            if (agent.specialty in required_specialties or 
                agent.specialty == AgentSpecialty.SENIOR_ESCALATION):
                backup_agents.append(agent.agent_id)
                
        return backup_agents[:3]  # Max 3 backups

    async def balance_agent_workload(self) -> Dict[str, Any]:
        """⚖️ Rééquilibrage automatique workload agents"""
        try:
            # Analyse workload actuel
            workload_analysis = {}
            total_tickets = 0
            
            for agent in self.agents.values():
                workload_analysis[agent.agent_id] = {
                    "current_workload": agent.current_workload,
                    "capacity": agent.max_capacity,
                    "utilization": agent.current_workload / agent.max_capacity,
                    "specialty": agent.specialty.value
                }
                total_tickets += agent.current_workload
                
            # Identification déséquilibres
            overloaded_agents = [
                agent_id for agent_id, data in workload_analysis.items()
                if data["utilization"] > 0.8
            ]
            
            underutilized_agents = [
                agent_id for agent_id, data in workload_analysis.items()
                if data["utilization"] < 0.4 and self.agents[agent_id].is_online
            ]
            
            # Suggestions redistribution
            redistribution_suggestions = []
            
            for overloaded_id in overloaded_agents:
                for underutilized_id in underutilized_agents:
                    overloaded_agent = self.agents[overloaded_id]
                    underutilized_agent = self.agents[underutilized_id]
                    
                    # Vérification compatibilité spécialités
                    if self._are_specialties_compatible(
                        overloaded_agent.specialty, 
                        underutilized_agent.specialty
                    ):
                        tickets_to_move = min(
                            2,  # Max 2 tickets à la fois
                            overloaded_agent.current_workload - overloaded_agent.max_capacity
                        )
                        
                        if tickets_to_move > 0:
                            redistribution_suggestions.append({
                                "from_agent": overloaded_id,
                                "to_agent": underutilized_id,
                                "tickets_count": tickets_to_move,
                                "reason": "workload_balancing"
                            })
                            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_active_tickets": total_tickets,
                "workload_analysis": workload_analysis,
                "overloaded_agents": overloaded_agents,
                "underutilized_agents": underutilized_agents,
                "redistribution_suggestions": redistribution_suggestions,
                "balance_score": self._calculate_balance_score(workload_analysis)
            }
            
        except Exception as e:
            logger.error(f"Erreur balance workload: {e}")
            return {}

    async def enforce_sla_priorities(self) -> List[Dict[str, Any]]:
        """⏰ Enforcement SLA avec escalation automatique"""
        try:
            sla_violations = []
            current_time = datetime.utcnow()
            
            # Simulation tickets en cours (à remplacer par vraie DB)
            active_tickets = await self._get_active_tickets()
            
            for ticket in active_tickets:
                time_elapsed = current_time - ticket["created_at"]
                sla_threshold = self.sla_thresholds[TicketPriority(ticket["priority"])]
                
                # Détection violation SLA
                if time_elapsed > sla_threshold:
                    violation = {
                        "ticket_id": ticket["ticket_id"],
                        "agent_id": ticket["assigned_agent_id"],
                        "priority": ticket["priority"],
                        "time_elapsed": str(time_elapsed),
                        "sla_threshold": str(sla_threshold),
                        "violation_severity": self._calculate_violation_severity(
                            time_elapsed, sla_threshold
                        ),
                        "escalation_action": await self._determine_escalation_action(ticket)
                    }
                    
                    sla_violations.append(violation)
                    
                    # Actions automatiques
                    await self._execute_sla_escalation(ticket, violation)
                    
            return sla_violations
            
        except Exception as e:
            logger.error(f"Erreur enforcement SLA: {e}")
            return []

    def _generate_routing_reason(
        self, 
        agent: SupportAgent, 
        category: TicketCategory
    ) -> str:
        """📝 Génération justification routing"""
        return f"Agent {agent.name} sélectionné pour {category.value} - Spécialité: {agent.specialty.value}, Charge: {agent.current_workload}/{agent.max_capacity}"

    def _are_specialties_compatible(
        self, 
        specialty1: AgentSpecialty, 
        specialty2: AgentSpecialty
    ) -> bool:
        """🔗 Vérification compatibilité spécialités"""
        # Certaines spécialités peuvent gérer tickets d'autres
        compatible_mappings = {
            AgentSpecialty.SENIOR_ESCALATION: [  # Senior peut tout gérer
                AgentSpecialty.TECHNICAL_SPECIALIST,
                AgentSpecialty.BILLING_SPECIALIST,
                AgentSpecialty.CREATOR_SUCCESS_MANAGER,
                AgentSpecialty.PRODUCT_SPECIALIST
            ],
            AgentSpecialty.GENERAL_SUPPORT: [  # Généraliste peut aider
                AgentSpecialty.TECHNICAL_SPECIALIST,
                AgentSpecialty.BILLING_SPECIALIST
            ]
        }
        
        return (specialty1 == specialty2 or 
                specialty2 in compatible_mappings.get(specialty1, []) or
                specialty1 in compatible_mappings.get(specialty2, []))

    async def _handle_no_agent_available(self, request: TicketRoutingRequest) -> SupportAgent:
        """🆘 Gestion absence agents disponibles"""
        # Recherche agent senior ou escalation
        for agent in self.agents.values():
            if agent.specialty == AgentSpecialty.SENIOR_ESCALATION and agent.is_online:
                return agent
                
        # Sinon agent avec moindre charge
        available_agents = [a for a in self.agents.values() if a.is_online]
        if available_agents:
            return min(available_agents, key=lambda a: a.current_workload)
            
        # Dernière option: créer agent virtuel temporaire
        return SupportAgent(
            agent_id="virtual_agent_emergency",
            name="Emergency Virtual Agent",
            specialty=AgentSpecialty.GENERAL_SUPPORT,
            languages=["en", "fr"],
            creator_types_expertise=["musician", "blogger", "photographer"],
            max_capacity=50
        )

    async def _train_initial_model(self) -> None:
        """🎓 Entraînement initial modèle avec données synthétiques"""
        # Données synthétiques pour démarrage
        training_texts = [
            ("My audio upload is not working", "technical_issue"),
            ("I can't access my billing information", "billing_support"),
            ("Someone stole my music", "content_copyright"),
            ("How to collaborate with other artists", "collaboration_help"),
            ("Help with monetizing my content", "monetization_support"),
            ("This is urgent, my account is broken", "emergency_critical")
        ]
        
        texts, labels = zip(*training_texts)
        await asyncio.to_thread(self.classification_model.fit, texts, labels)


class RoutingAnalytics:
    """📊 Analytics performance routing"""
    
    def __init__(self):
        self.routing_history = []
        self.performance_metrics = {
            "total_routings": 0,
            "successful_assignments": 0,
            "avg_routing_time": timedelta(),
            "category_accuracy": {},
            "agent_performance": {}
        }
        
    async def record_routing_decision(
        self, 
        request: TicketRoutingRequest, 
        decision: RoutingDecision
    ) -> None:
        """📈 Enregistrement décision routing pour analytics"""
        routing_record = {
            "timestamp": datetime.utcnow(),
            "ticket_id": request.ticket_id,
            "predicted_category": decision.predicted_category.value,
            "confidence_score": decision.confidence_score,
            "assigned_agent": decision.assigned_agent_id,
            "agent_specialty": decision.agent_specialty.value,
            "priority": decision.priority_level.value,
            "creator_type": request.creator_type,
            "creator_tier": request.creator_tier
        }
        
        self.routing_history.append(routing_record)
        self.performance_metrics["total_routings"] += 1

    def get_routing_analytics(self) -> Dict[str, Any]:
        """📋 Rapport analytics routing complet"""
        if not self.routing_history:
            return {"status": "no_data"}
            
        # Analyse distribution catégories
        category_distribution = {}
        for record in self.routing_history:
            cat = record["predicted_category"]
            category_distribution[cat] = category_distribution.get(cat, 0) + 1
            
        # Analyse performance agents
        agent_performance = {}
        for record in self.routing_history:
            agent = record["assigned_agent"]
            if agent not in agent_performance:
                agent_performance[agent] = {
                    "total_assignments": 0,
                    "avg_confidence": 0.0,
                    "categories_handled": set()
                }
            agent_performance[agent]["total_assignments"] += 1
            agent_performance[agent]["categories_handled"].add(record["predicted_category"])
            
        return {
            "total_routings": len(self.routing_history),
            "category_distribution": category_distribution,
            "agent_utilization": agent_performance,
            "avg_confidence_score": np.mean([r["confidence_score"] for r in self.routing_history]),
            "routing_trends": self._calculate_routing_trends(),
            "last_updated": datetime.utcnow().isoformat()
        }

    def _calculate_routing_trends(self) -> Dict[str, Any]:
        """📈 Calcul tendances routing"""
        if len(self.routing_history) < 10:
            return {"status": "insufficient_data"}
            
        recent = self.routing_history[-50:]  # 50 derniers
        older = self.routing_history[-100:-50] if len(self.routing_history) >= 100 else []
        
        trends = {
            "recent_avg_confidence": np.mean([r["confidence_score"] for r in recent]),
            "confidence_trend": "stable"
        }
        
        if older:
            older_confidence = np.mean([r["confidence_score"] for r in older])
            if trends["recent_avg_confidence"] > older_confidence + 0.05:
                trends["confidence_trend"] = "improving"
            elif trends["recent_avg_confidence"] < older_confidence - 0.05:
                trends["confidence_trend"] = "declining"
                
        return trends


class WorkloadPredictor:
    """🔮 Prédicteur workload agents"""
    
    def __init__(self):
        self.workload_history = {}
        self.prediction_models = {}
        
    async def update_agent_workload(self, agent_id: str, change: int) -> None:
        """📊 Mise à jour historique workload"""
        if agent_id not in self.workload_history:
            self.workload_history[agent_id] = []
            
        self.workload_history[agent_id].append({
            "timestamp": datetime.utcnow(),
            "workload_change": change,
            "hour_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday()
        })
        
    async def predict_future_workload(
        self, 
        agent_id: str, 
        hours_ahead: int = 4
    ) -> Dict[str, Any]:
        """🔮 Prédiction workload futur"""
        if agent_id not in self.workload_history or len(self.workload_history[agent_id]) < 10:
            return {"prediction": "insufficient_data"}
            
        history = self.workload_history[agent_id]
        
        # Analyse patterns horaires
        hourly_patterns = {}
        for record in history:
            hour = record["hour_of_day"]
            if hour not in hourly_patterns:
                hourly_patterns[hour] = []
            hourly_patterns[hour].append(record["workload_change"])
            
        # Prédiction simple basée patterns
        future_hour = (datetime.utcnow().hour + hours_ahead) % 24
        predicted_changes = hourly_patterns.get(future_hour, [0])
        predicted_workload_change = np.mean(predicted_changes) if predicted_changes else 0
        
        return {
            "agent_id": agent_id,
            "hours_ahead": hours_ahead,
            "predicted_workload_change": predicted_workload_change,
            "confidence": min(1.0, len(predicted_changes) / 10),
            "based_on_samples": len(predicted_changes)
        }