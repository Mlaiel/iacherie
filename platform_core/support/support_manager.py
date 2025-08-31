"""🚀 Support System - IA Influencer Agent Platform Enterprise
==========================================================
Module: backend/platform_core/support/support_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE SUPPORT CLIENT ENTERPRISE
Support intelligent avec IA et automatisation avancée
- Ticketing system avec routing intelligent
- Live chat avec agents IA et humains
- Knowledge base avec recherche sémantique
- Analytics et KPIs de satisfaction client
"""
import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TicketStatus(Enum):
    """Statuts des tickets"""    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_INTERNAL = "pending_internal"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(Enum):
    """Priorités des tickets"""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class TicketCategory(Enum):
    """Catégories de tickets"""    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    CONTENT_PROTECTION = "content_protection"
    API_SUPPORT = "api_support"
    GENERAL = "general"


class AgentType(Enum):
    """Types d'agents de support"""    AI_BOT = "ai_bot"
    HUMAN_AGENT = "human_agent"
    SPECIALIST = "specialist"
    MANAGER = "manager"


@dataclass
class SupportTicket:
    """Ticket de support"""    ticket_id: str
    user_id: str
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    assigned_agent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    satisfaction_score: Optional[int] = None
    resolution_time_minutes: Optional[int] = None


@dataclass
class TicketMessage:
    """Message dans un ticket"""    message_id: str
    ticket_id: str
    sender_id: str
    sender_type: AgentType
    content: str
    timestamp: datetime
    is_internal: bool = False
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeBaseArticle:
    """Article de la base de connaissances"""    article_id: str
    title: str
    content: str
    category: TicketCategory
    tags: List[str]
    author_id: str
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    is_published: bool = True


@dataclass
class ChatSession:
    """Session de chat live"""    session_id: str
    user_id: str
    agent_id: Optional[str]
    agent_type: AgentType
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    satisfaction_score: Optional[int] = None


class SupportManager:
    """Gestionnaire principal du support"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tickets: Dict[str, SupportTicket] = {}
        self.messages: Dict[str, List[TicketMessage]] = {}
        self.knowledge_base: Dict[str, KnowledgeBaseArticle] = {}
        self.chat_sessions: Dict[str, ChatSession] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        self._setup_ai_agents()
        self._setup_routing_rules()
        
        logger.info("✅ SupportManager initialized")
    
    def _setup_ai_agents(self) -> None:
        """Configurer les agents IA"""        self.ai_agents = {
            "general_bot": {
                "name": "Assistant IA Général",
                "specialties": ["general", "account", "billing"],
                "max_concurrent_chats": 50,
                "escalation_threshold": 3
            },
            "technical_bot": {
                "name": "Expert Technique IA",
                "specialties": ["technical", "api_support", "bug_report"],
                "max_concurrent_chats": 30,
                "escalation_threshold": 2
            },
            "protection_bot": {
                "name": "Spécialiste Protection IA",
                "specialties": ["content_protection"],
                "max_concurrent_chats": 20,
                "escalation_threshold": 1
            }
        }
    
    def _setup_routing_rules(self) -> None:
        """Configurer les règles de routage"""        self.routing_rules = {
            TicketCategory.TECHNICAL: {
                "default_priority": TicketPriority.NORMAL,
                "auto_assign": "technical_team",
                "sla_hours": 24
            },
            TicketCategory.BILLING: {
                "default_priority": TicketPriority.HIGH,
                "auto_assign": "billing_team",
                "sla_hours": 8
            },
            TicketCategory.CONTENT_PROTECTION: {
                "default_priority": TicketPriority.HIGH,
                "auto_assign": "protection_team",
                "sla_hours": 4
            },
            TicketCategory.BUG_REPORT: {
                "default_priority": TicketPriority.HIGH,
                "auto_assign": "dev_team",
                "sla_hours": 12
            }
        }
    
    async def create_ticket(
        self,
        user_id: str,
        subject: str,
        description: str,
        category: TicketCategory,
        priority: Optional[TicketPriority] = None
    ) -> SupportTicket:
        """Créer un nouveau ticket"""        try:
            ticket_id = f"TK_{uuid.uuid4().hex[:12].upper()}"
            
            # Déterminer la priorité automatiquement si non spécifiée
            if priority is None:
                priority = self.routing_rules.get(category, {}).get("default_priority", TicketPriority.NORMAL)
            
            ticket = SupportTicket(
                ticket_id=ticket_id,
                user_id=user_id,
                subject=subject,
                description=description,
                category=category,
                priority=priority,
                status=TicketStatus.OPEN,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Auto-assignment selon les règles
            assigned_agent = await self._auto_assign_ticket(ticket)
            if assigned_agent:
                ticket.assigned_agent_id = assigned_agent
            
            self.tickets[ticket_id] = ticket
            self.messages[ticket_id] = []
            
            # Ajouter le message initial
            initial_message = TicketMessage(
                message_id=f"MSG_{uuid.uuid4().hex[:8]}",
                ticket_id=ticket_id,
                sender_id=user_id,
                sender_type=AgentType.HUMAN_AGENT,  # User
                content=description,
                timestamp=datetime.utcnow()
            )
            self.messages[ticket_id].append(initial_message)
            
            logger.info(f"✅ Ticket created: {ticket_id} - {subject}")
            return ticket
            
        except Exception as e:
            logger.error(f"❌ Failed to create ticket: {e}")
            raise
    
    async def _auto_assign_ticket(self, ticket: SupportTicket) -> Optional[str]:
        """Assigner automatiquement un ticket"""        try:
            # Logique d'assignment basée sur la catégorie et la charge
            routing_rule = self.routing_rules.get(ticket.category)
            if routing_rule:
                preferred_team = routing_rule.get("auto_assign")
                
                # Trouver l'agent le moins chargé dans l'équipe
                available_agents = [
                    agent_id for agent_id, agent in self.agents.items()
                    if agent.get("team") == preferred_team and agent.get("available", True)
                ]
                
                if available_agents:
                    # Retourner l'agent avec le moins de tickets actifs
                    return min(available_agents, key=lambda agent_id: 
                              len([t for t in self.tickets.values() 
                                   if t.assigned_agent_id == agent_id and t.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]]))
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Auto-assignment failed: {e}")
            return None
    
    async def add_message_to_ticket(
        self,
        ticket_id: str,
        sender_id: str,
        content: str,
        sender_type: AgentType = AgentType.HUMAN_AGENT,
        is_internal: bool = False
    ) -> TicketMessage:
        """Ajouter un message à un ticket"""        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket not found: {ticket_id}")
            
            message = TicketMessage(
                message_id=f"MSG_{uuid.uuid4().hex[:8]}",
                ticket_id=ticket_id,
                sender_id=sender_id,
                sender_type=sender_type,
                content=content,
                timestamp=datetime.utcnow(),
                is_internal=is_internal
            )
            
            self.messages[ticket_id].append(message)
            
            # Mettre à jour le ticket
            self.tickets[ticket_id].updated_at = datetime.utcnow()
            
            # Déclencher les réponses automatiques si nécessaire
            if sender_type != AgentType.AI_BOT:
                await self._trigger_ai_response(ticket_id, message)
            
            logger.info(f"✅ Message added to ticket {ticket_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Failed to add message: {e}")
            raise
    
    async def _trigger_ai_response(self, ticket_id: str, user_message: TicketMessage) -> None:
        """Déclencher une réponse IA si approprié"""        try:
            ticket = self.tickets[ticket_id]
            
            # Vérifier si le ticket nécessite une réponse IA
            if ticket.assigned_agent_id and not ticket.assigned_agent_id.startswith("ai_"):
                return  # Agent humain assigné
            
            # Déterminer quel bot IA utiliser
            suitable_bot = self._find_suitable_ai_bot(ticket.category)
            if not suitable_bot:
                return
            
            # Générer une réponse IA (placeholder)
            ai_response = await self._generate_ai_response(ticket, user_message.content)
            
            if ai_response:
                await self.add_message_to_ticket(
                    ticket_id=ticket_id,
                    sender_id=suitable_bot,
                    content=ai_response,
                    sender_type=AgentType.AI_BOT
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to trigger AI response: {e}")
    
    def _find_suitable_ai_bot(self, category: TicketCategory) -> Optional[str]:
        """Trouver le bot IA approprié pour une catégorie"""        for bot_id, bot_info in self.ai_agents.items():
            if category.value in bot_info["specialties"]:
                return bot_id
        return "general_bot"  # Bot par défaut
    
    async def _generate_ai_response(self, ticket: SupportTicket, user_message: str) -> Optional[str]:
        """Générer une réponse IA (placeholder)"""        try:
            # Placeholder pour intégration IA réelle
            responses = {
                TicketCategory.TECHNICAL: "Je comprends votre problème technique. Pouvez-vous me donner plus de détails sur votre configuration?",
                TicketCategory.BILLING: "Je vais vérifier votre compte de facturation. Un moment s'il vous plaît...",
                TicketCategory.CONTENT_PROTECTION: "Votre demande de protection de contenu est importante. Vérifions votre configuration...",
                TicketCategory.GENERAL: "Merci pour votre message. Comment puis-je vous aider aujourd'hui?"
            }
            
            return responses.get(ticket.category, responses[TicketCategory.GENERAL])
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI response: {e}")
            return None
    
    async def start_chat_session(self, user_id: str) -> ChatSession:
        """Démarrer une session de chat live"""        try:
            session_id = f"CHAT_{uuid.uuid4().hex[:12]}"
            
            # Assigner un agent IA disponible
            available_bot = self._find_available_ai_agent()
            
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                agent_id=available_bot,
                agent_type=AgentType.AI_BOT,
                status="active",
                started_at=datetime.utcnow()
            )
            
            self.chat_sessions[session_id] = session
            
            # Message de bienvenue
            welcome_message = {
                "id": f"MSG_{uuid.uuid4().hex[:8]}",
                "sender": "system",
                "content": "Bonjour! Je suis votre assistant IA. Comment puis-je vous aider?",
                "timestamp": datetime.utcnow().isoformat()
            }
            session.messages.append(welcome_message)
            
            logger.info(f"✅ Chat session started: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to start chat session: {e}")
            raise
    
    def _find_available_ai_agent(self) -> str:
        """Trouver un agent IA disponible"""        # Compter les sessions actives par bot
        active_sessions = {}
        for session in self.chat_sessions.values():
            if session.status == "active" and session.agent_id:
                active_sessions[session.agent_id] = active_sessions.get(session.agent_id, 0) + 1
        
        # Trouver le bot le moins chargé
        for bot_id, bot_info in self.ai_agents.items():
            current_load = active_sessions.get(bot_id, 0)
            if current_load < bot_info["max_concurrent_chats"]:
                return bot_id
        
        return "general_bot"  # Bot par défaut
    
    async def search_knowledge_base(self, query: str, category: Optional[TicketCategory] = None) -> List[KnowledgeBaseArticle]:
        """Rechercher dans la base de connaissances"""        try:
            results = []
            query_lower = query.lower()
            
            for article in self.knowledge_base.values():
                if not article.is_published:
                    continue
                
                # Filtrer par catégorie si spécifiée
                if category and article.category != category:
                    continue
                
                # Recherche simple dans le titre et le contenu
                if (query_lower in article.title.lower() or 
                    query_lower in article.content.lower() or
                    any(query_lower in tag.lower() for tag in article.tags)):
                    results.append(article)
            
            # Trier par pertinence (simple score basé sur le titre)
            results.sort(key=lambda a: query_lower in a.title.lower(), reverse=True)
            
            return results[:10]  # Limiter à 10 résultats
            
        except Exception as e:
            logger.error(f"❌ Knowledge base search failed: {e}")
            return []
    
    async def get_support_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Obtenir les analytics du support"""        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filtrer les tickets récents
            recent_tickets = [
                ticket for ticket in self.tickets.values()
                if ticket.created_at >= cutoff_date
            ]
            
            total_tickets = len(recent_tickets)
            resolved_tickets = len([t for t in recent_tickets if t.status == TicketStatus.RESOLVED])
            avg_resolution_time = None
            
            if resolved_tickets > 0:
                resolution_times = [t.resolution_time_minutes for t in recent_tickets 
                                 if t.resolution_time_minutes is not None]
                if resolution_times:
                    avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            # Calculs de satisfaction
            satisfaction_scores = [t.satisfaction_score for t in recent_tickets 
                                 if t.satisfaction_score is not None]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
            
            # Distribution par catégorie
            category_distribution = {}
            for ticket in recent_tickets:
                category = ticket.category.value
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            return {
                "period_days": days,
                "total_tickets": total_tickets,
                "resolved_tickets": resolved_tickets,
                "resolution_rate": (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                "avg_resolution_time_minutes": avg_resolution_time,
                "avg_satisfaction_score": avg_satisfaction,
                "category_distribution": category_distribution,
                "active_chat_sessions": len([s for s in self.chat_sessions.values() if s.status == "active"])
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get support analytics: {e}")
            return {"error": str(e)}


class KnowledgeBaseManager:
    """Gestionnaire de la base de connaissances"""    
    def __init__(self):
        self.articles: Dict[str, KnowledgeBaseArticle] = {}
        self._create_default_articles()
    
    def _create_default_articles(self) -> None:
        """Créer les articles par défaut"""        default_articles = [
            KnowledgeBaseArticle(
                article_id="getting_started",
                title="Guide de démarrage rapide",
                content="Ce guide vous aidera à commencer avec IA Influencer Agent...",
                category=TicketCategory.GENERAL,
                tags=["démarrage", "guide", "nouveau"],
                author_id="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                article_id="api_authentication",
                title="Authentification API",
                content="Pour utiliser notre API, vous devez d'abord obtenir une clé API...",
                category=TicketCategory.API_SUPPORT,
                tags=["api", "authentification", "clé"],
                author_id="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                article_id="content_protection_setup",
                title="Configuration de la protection de contenu",
                content="La protection de contenu IA vous permet de surveiller...",
                category=TicketCategory.CONTENT_PROTECTION,
                tags=["protection", "contenu", "configuration"],
                author_id="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for article in default_articles:
            self.articles[article.article_id] = article


# Exports
__all__ = [
    "SupportManager",
    "KnowledgeBaseManager",
    "SupportTicket",
    "TicketMessage",
    "KnowledgeBaseArticle",
    "ChatSession",
    "TicketStatus",
    "TicketPriority",
    "TicketCategory",
    "AgentType"
]