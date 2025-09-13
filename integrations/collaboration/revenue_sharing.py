"""
Revenue Sharing - Collaboration Module
=====================================
Système automatisé de partage de revenus collaboratif.
Smart contracts, attribution tracking, paiements automatiques.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

class RevenueModel(Enum):
    """Modèles de partage de revenus."""
    EQUAL_SPLIT = "equal_split"
    CONTRIBUTION_BASED = "contribution_based"
    PERFORMANCE_BASED = "performance_based"
    CUSTOM_SPLIT = "custom_split"

class TransactionStatus(Enum):
    """Statuts de transaction."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"

@dataclass
class RevenueShare:
    """Part de revenus d'un créateur."""
    creator_id: str
    percentage: Decimal
    amount: Decimal
    basis: str  # Base du calcul

@dataclass
class RevenueTransaction:
    """Transaction de partage de revenus."""
    transaction_id: str
    collaboration_id: str
    total_revenue: Decimal
    shares: List[RevenueShare]
    status: TransactionStatus
    created_at: datetime
    processed_at: Optional[datetime]
    metadata: Dict[str, Any]

class RevenueSharing:
    """Gestionnaire de partage de revenus."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialise le système de partage de revenus."""
        self.config = config or {}
        self.transactions: Dict[str, RevenueTransaction] = {}
        self.collaboration_agreements: Dict[str, Dict] = {}
        logger.info("Revenue Sharing initialisé")
    
    async def calculate_revenue_shares(
        self,
        collaboration_id: str,
        total_revenue: Decimal,
        model: RevenueModel,
        creators: List[str],
        custom_params: Dict[str, Any] = None
    ) -> List[RevenueShare]:
        """Calcule les parts de revenus."""
        shares = []
        
        if model == RevenueModel.EQUAL_SPLIT:
            shares = self._calculate_equal_split(creators, total_revenue)
        elif model == RevenueModel.CONTRIBUTION_BASED:
            shares = await self._calculate_contribution_based(
                collaboration_id, creators, total_revenue, custom_params
            )
        elif model == RevenueModel.PERFORMANCE_BASED:
            shares = await self._calculate_performance_based(
                collaboration_id, creators, total_revenue, custom_params
            )
        elif model == RevenueModel.CUSTOM_SPLIT:
            shares = self._calculate_custom_split(
                creators, total_revenue, custom_params
            )
        
        # Vérifier que total = 100%
        total_percentage = sum(share.percentage for share in shares)
        if abs(total_percentage - Decimal('1.0')) > Decimal('0.01'):
            logger.warning(f"Total percentage {total_percentage} != 1.0")
        
        return shares