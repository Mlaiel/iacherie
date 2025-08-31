""" Platform Core Support System - IA Influencer Agent Platform Enterprise
=========================================================================
Module: backend/platform_core/support/
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 SYSTÈME DE SUPPORT CLIENT ENTERPRISE
Support intelligent avec IA et automatisation avancée
- Ticketing system avec routing intelligent
- Live chat avec agents IA et humains
- Knowledge base avec recherche sémantique
- Analytics et KPIs de satisfaction client
"""
from .support_manager import (
    SupportManager,
    KnowledgeBaseManager,
    SupportTicket,
    TicketMessage,
    KnowledgeBaseArticle,
    ChatSession,
    TicketStatus,
    TicketPriority,
    TicketCategory,
    AgentType
)

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

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
