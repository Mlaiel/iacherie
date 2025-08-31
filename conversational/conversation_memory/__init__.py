"""Conversation Memory Module - IA Influencer Agent

Enterprise-grade conversation memory management system providing persistent
conversation storage, context retention, intelligent retrieval, and semantic
search capabilities for multi-format content creators.

This module implements advanced conversation memory techniques including:
- Long-term conversation storage with PostgreSQL
- Short-term memory caching with Redis
- Vector-based semantic search with FAISS
- Content-aware conversation indexing
- Multi-modal conversation tracking
- Creator collaboration memory
- Content protection conversation history

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This software and all associated intellectual property are the exclusive property
of Fahed Mlaiel. Unauthorized use, copying, distribution, modification, or 
commercialization without explicit written permission is strictly prohibited.

Any violation will result in immediate legal action under German and International
copyright law. This includes but is not limited to code theft, concept copying,
or unauthorized derivative works.

For licensing inquiries: mlaiel@live.de

---
Project Team Specialties:
• Lead IA Developer & System Architect: Advanced AI/ML system design
• Backend Senior Engineer: Enterprise Python & FastAPI development  
• ML Engineer: Machine Learning & Deep Learning implementation
• Database Administrator: PostgreSQL, Redis, Vector DB optimization
• Security Specialist: Cybersecurity & data protection compliance
• Microservices Architect: Distributed systems & API design
• Audio Processing Engineer: Audio analysis & fingerprinting
• DevOps Engineer: Infrastructure automation & deployment
• IA Prompt Engineer: Advanced prompt engineering & optimization
---
"""from typing import Dict, List, Optional, Any, Union, Tuple
import logging

from .managers import (
    ConversationMemoryManager,
    ConversationHistoryManager,
    MemoryIndexer
)

from .storage import (
    LongTermMemory,
    ShortTermMemory,
    ConversationDatabase,
    MemoryCache,
    VectorStore
)

from .retrieval import (
    ConversationRetriever,
    SemanticSearch,
    ContextualRetriever,
    ContentAwareRetriever,
    CollaborationMemoryRetriever
)

from .models import (
    ConversationRecord,
    MemoryEntry,
    ConversationContext,
    ContentContext,
    CollaborationContext,
    ProtectionContext
)

from .indexing import (
    ConversationIndexer,
    TopicIndexer,
    SemanticIndexer,
    ContentIndexer,
    TemporalIndexer
)

from .analytics import (
    ConversationAnalytics,
    MemoryMetrics,
    UsageTracker,
    PerformanceMonitor,
    InsightGenerator
)

# Version and package info
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Main exports
__all__ = [
    # Core Managers
    "ConversationMemoryManager",
    "ConversationHistoryManager", 
    "MemoryIndexer",
    
    # Storage Components
    "LongTermMemory",
    "ShortTermMemory",
    "ConversationDatabase",
    "MemoryCache",
    "VectorStore",
    
    # Retrieval Systems
    "ConversationRetriever",
    "SemanticSearch",
    "ContextualRetriever",
    "ContentAwareRetriever",
    "CollaborationMemoryRetriever",
    
    # Data Models
    "ConversationRecord",
    "MemoryEntry",
    "ConversationContext",
    "ContentContext", 
    "CollaborationContext",
    "ProtectionContext",
    
    # Indexing
    "ConversationIndexer",
    "TopicIndexer",
    "SemanticIndexer",
    "ContentIndexer",
    "TemporalIndexer",
    
    # Analytics
    "ConversationAnalytics",
    "MemoryMetrics",
    "UsageTracker",
    "PerformanceMonitor",
    "InsightGenerator"
]

# Module level configuration
logger = logging.getLogger(__name__)

# Initialize core components
conversation_memory_manager = None
conversation_history_manager = None
memory_indexer = None

def get_conversation_memory_manager() -> ConversationMemoryManager:
    """Get singleton instance of conversation memory manager"""    global conversation_memory_manager
    if conversation_memory_manager is None:
        conversation_memory_manager = ConversationMemoryManager()
    return conversation_memory_manager

def get_conversation_history_manager() -> ConversationHistoryManager:
    """Get singleton instance of conversation history manager"""    global conversation_history_manager
    if conversation_history_manager is None:
        conversation_history_manager = ConversationHistoryManager()
    return conversation_history_manager

def get_memory_indexer() -> MemoryIndexer:
    """Get singleton instance of memory indexer"""    global memory_indexer
    if memory_indexer is None:
        memory_indexer = MemoryIndexer()
    return memory_indexer

# Module initialization
logger.info("Conversation Memory module initialized - Enterprise Memory Management System")
logger.info(f"Version: {__version__} | Author: {__author__}")
logger.info("⚠️  Protected Intellectual Property - Unauthorized use prohibited")
