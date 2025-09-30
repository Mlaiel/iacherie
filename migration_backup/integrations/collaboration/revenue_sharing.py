"""
Revenue Sharing - Collaboration Module
=====================================
Système automatisé de partage de revenus collaboratif.
Smart contracts, attribution tracking, paiements automatiques.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import uuid
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
    
    def _calculate_equal_split(
        self,
        creators: List[str],
        total_revenue: Decimal
    ) -> List[RevenueShare]:
        """Calculate equal split among creators."""
        if not creators:
            return []
        
        percentage_per_creator = Decimal('1.0') / len(creators)
        amount_per_creator = (total_revenue * percentage_per_creator).quantize(
            Decimal('0.01'), rounding=ROUND_DOWN
        )
        
        shares = []
        for creator_id in creators:
            shares.append(RevenueShare(
                creator_id=creator_id,
                percentage=percentage_per_creator,
                amount=amount_per_creator,
                basis="equal_split"
            ))
        
        return shares
    
    async def _calculate_contribution_based(
        self,
        collaboration_id: str,
        creators: List[str],
        total_revenue: Decimal,
        custom_params: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate shares based on contribution metrics."""
        contribution_scores = custom_params.get('contribution_scores', {})
        
        if not contribution_scores:
            # Default to equal split if no contribution data
            return self._calculate_equal_split(creators, total_revenue)
        
        total_contribution = sum(contribution_scores.values())
        shares = []
        
        for creator_id in creators:
            contribution = contribution_scores.get(creator_id, 0)
            percentage = Decimal(str(contribution / total_contribution)) if total_contribution > 0 else Decimal('0')
            amount = (total_revenue * percentage).quantize(
                Decimal('0.01'), rounding=ROUND_DOWN
            )
            
            shares.append(RevenueShare(
                creator_id=creator_id,
                percentage=percentage,
                amount=amount,
                basis=f"contribution_score_{contribution}"
            ))
        
        return shares
    
    async def _calculate_performance_based(
        self,
        collaboration_id: str,
        creators: List[str],
        total_revenue: Decimal,
        custom_params: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate shares based on performance metrics."""
        performance_metrics = custom_params.get('performance_metrics', {})
        
        # Default performance weights
        metric_weights = {
            'views': 0.3,
            'engagement': 0.25,
            'conversions': 0.25,
            'reach': 0.2
        }
        
        creator_scores = {}
        
        for creator_id in creators:
            creator_metrics = performance_metrics.get(creator_id, {})
            score = 0
            
            for metric, weight in metric_weights.items():
                metric_value = creator_metrics.get(metric, 0)
                score += metric_value * weight
            
            creator_scores[creator_id] = score
        
        total_score = sum(creator_scores.values())
        shares = []
        
        for creator_id in creators:
            score = creator_scores.get(creator_id, 0)
            percentage = Decimal(str(score / total_score)) if total_score > 0 else Decimal('0')
            amount = (total_revenue * percentage).quantize(
                Decimal('0.01'), rounding=ROUND_DOWN
            )
            
            shares.append(RevenueShare(
                creator_id=creator_id,
                percentage=percentage,
                amount=amount,
                basis=f"performance_score_{score:.2f}"
            ))
        
        return shares
    
    def _calculate_custom_split(
        self,
        creators: List[str],
        total_revenue: Decimal,
        custom_params: Dict[str, Any]
    ) -> List[RevenueShare]:
        """Calculate shares based on custom percentages."""
        custom_splits = custom_params.get('custom_splits', {})
        
        shares = []
        for creator_id in creators:
            percentage = Decimal(str(custom_splits.get(creator_id, 0)))
            amount = (total_revenue * percentage).quantize(
                Decimal('0.01'), rounding=ROUND_DOWN
            )
            
            shares.append(RevenueShare(
                creator_id=creator_id,
                percentage=percentage,
                amount=amount,
                basis="custom_agreement"
            ))
        
        return shares
    
    async def process_revenue_transaction(
        self,
        collaboration_id: str,
        total_revenue: Decimal,
        model: RevenueModel,
        creators: List[str],
        custom_params: Dict[str, Any] = None
    ) -> str:
        """Process complete revenue transaction."""
        transaction_id = str(uuid.uuid4())
        
        # Calculate shares
        shares = await self.calculate_revenue_shares(
            collaboration_id, total_revenue, model, creators, custom_params
        )
        
        # Create transaction record
        transaction = RevenueTransaction(
            transaction_id=transaction_id,
            collaboration_id=collaboration_id,
            total_revenue=total_revenue,
            shares=shares,
            status=TransactionStatus.PENDING,
            created_at=datetime.now(),
            processed_at=None,
            metadata=custom_params or {}
        )
        
        self.transactions[transaction_id] = transaction
        
        # Process payments
        await self._process_payments(transaction)
        
        logger.info(f"Revenue transaction processed: {transaction_id}")
        return transaction_id
    
    async def _process_payments(self, transaction: RevenueTransaction) -> bool:
        """Process individual payments to creators."""
        transaction.status = TransactionStatus.PROCESSING
        
        try:
            for share in transaction.shares:
                # Simulate payment processing
                await self._send_payment(share)
            
            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.now()
            
            logger.info(f"Payments completed for transaction: {transaction.transaction_id}")
            return True
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            logger.error(f"Payment processing failed: {e}")
            return False
    
    async def _send_payment(self, share: RevenueShare) -> bool:
        """Send payment to individual creator."""
        # In production, this would integrate with payment processors
        # For now, we simulate the payment
        
        logger.info(f"Payment sent: {share.creator_id} receives {share.amount} ({share.percentage*100}%)")
        
        # Simulate payment delay
        await asyncio.sleep(0.1)
        
        return True
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction status and details."""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return None
        
        return {
            'transaction_id': transaction.transaction_id,
            'collaboration_id': transaction.collaboration_id,
            'total_revenue': float(transaction.total_revenue),
            'status': transaction.status.value,
            'shares': [
                {
                    'creator_id': share.creator_id,
                    'percentage': float(share.percentage),
                    'amount': float(share.amount),
                    'basis': share.basis
                }
                for share in transaction.shares
            ],
            'created_at': transaction.created_at.isoformat(),
            'processed_at': transaction.processed_at.isoformat() if transaction.processed_at else None
        }
    
    async def get_creator_revenue_history(
        self,
        creator_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get revenue history for a creator."""
        since_date = datetime.now() - timedelta(days=days)
        
        creator_transactions = []
        total_earned = Decimal('0')
        
        for transaction in self.transactions.values():
            if transaction.created_at >= since_date:
                for share in transaction.shares:
                    if share.creator_id == creator_id:
                        creator_transactions.append({
                            'transaction_id': transaction.transaction_id,
                            'collaboration_id': transaction.collaboration_id,
                            'amount': float(share.amount),
                            'percentage': float(share.percentage),
                            'status': transaction.status.value,
                            'date': transaction.created_at.isoformat()
                        })
                        
                        if transaction.status == TransactionStatus.COMPLETED:
                            total_earned += share.amount
        
        return {
            'creator_id': creator_id,
            'period_days': days,
            'total_earned': float(total_earned),
            'transaction_count': len(creator_transactions),
            'transactions': creator_transactions,
            'average_per_transaction': float(total_earned / len(creator_transactions)) if creator_transactions else 0
        }
    
    async def generate_revenue_report(
        self,
        collaboration_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive revenue report for collaboration."""
        collaboration_transactions = [
            t for t in self.transactions.values()
            if t.collaboration_id == collaboration_id
        ]
        
        if not collaboration_transactions:
            return {'error': 'No transactions found for collaboration'}
        
        total_revenue = sum(t.total_revenue for t in collaboration_transactions)
        total_distributed = sum(
            sum(share.amount for share in t.shares)
            for t in collaboration_transactions
            if t.status == TransactionStatus.COMPLETED
        )
        
        creator_earnings = {}
        for transaction in collaboration_transactions:
            if transaction.status == TransactionStatus.COMPLETED:
                for share in transaction.shares:
                    if share.creator_id not in creator_earnings:
                        creator_earnings[share.creator_id] = Decimal('0')
                    creator_earnings[share.creator_id] += share.amount
        
        return {
            'collaboration_id': collaboration_id,
            'total_revenue': float(total_revenue),
            'total_distributed': float(total_distributed),
            'pending_distribution': float(total_revenue - total_distributed),
            'transaction_count': len(collaboration_transactions),
            'creator_earnings': {k: float(v) for k, v in creator_earnings.items()},
            'status_breakdown': {
                status.value: len([t for t in collaboration_transactions if t.status == status])
                for status in TransactionStatus
            },
            'generated_at': datetime.now().isoformat()
        }
    
    async def setup_recurring_revenue(
        self,
        collaboration_id: str,
        revenue_schedule: Dict[str, Any]
    ) -> str:
        """Setup recurring revenue sharing for subscription-based content."""
        # This would integrate with scheduling system in production
        schedule_id = str(uuid.uuid4())
        
        self.collaboration_agreements[collaboration_id] = {
            'schedule_id': schedule_id,
            'frequency': revenue_schedule.get('frequency', 'monthly'),
            'model': revenue_schedule.get('model', RevenueModel.EQUAL_SPLIT),
            'creators': revenue_schedule.get('creators', []),
            'custom_params': revenue_schedule.get('custom_params', {}),
            'active': True,
            'created_at': datetime.now(),
            'next_payment': datetime.now() + timedelta(days=30)  # Default monthly
        }
        
        logger.info(f"Recurring revenue setup: {collaboration_id} - Schedule: {schedule_id}")
        return schedule_id