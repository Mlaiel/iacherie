"""🚀 Platform Core Billing - Refund Management System
===========================================================
Module: backend/platform_core/billing/refund_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION DES REMBOURSEMENTS
Gestion complète des remboursements avec intelligence artificielle
- Remboursements automatiques et manuels
- Règles de remboursement personnalisables
- Analytics et rapports de remboursements
- Intégration avec tous les processeurs de paiement
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)


class RefundStatus(Enum):
    """Statuts des demandes de remboursement"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundReason(Enum):
    """Raisons de remboursement"""
    CUSTOMER_REQUEST = "customer_request"
    BILLING_ERROR = "billing_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DUPLICATE_CHARGE = "duplicate_charge"
    FRAUD = "fraud"
    TECHNICAL_ISSUE = "technical_issue"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class RefundRequest:
    """Modèle de demande de remboursement"""
    id: str
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    reason: RefundReason
    status: RefundStatus
    requested_at: datetime
    processed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la demande en dictionnaire"""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "reason": self.reason.value,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "approved_by": self.approved_by,
            "notes": self.notes,
            "metadata": self.metadata or {}
        }


class RefundManager:
    """Gestionnaire principal des remboursements"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire de remboursements
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.auto_approval_limit = Decimal(str(self.config.get("auto_approval_limit", "100.00")))
        self.max_refund_days = self.config.get("max_refund_days", 30)
        self.refund_requests: Dict[str, RefundRequest] = {}
        
        logger.info("RefundManager initialized")

    async def create_refund_request(
        self,
        transaction_id: str,
        customer_id: str,
        amount: Union[Decimal, float],
        reason: RefundReason,
        notes: Optional[str] = None
    ) -> RefundRequest:
        """Crée une nouvelle demande de remboursement
        
        Args:
            transaction_id: ID de la transaction à rembourser
            customer_id: ID du client
            amount: Montant à rembourser
            reason: Raison du remboursement
            notes: Notes additionnelles
            
        Returns:
            RefundRequest: La demande de remboursement créée
        """
        try:
            # Génération d'un ID unique
            request_id = f"refund_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.refund_requests)}"
            
            # Validation du montant
            if isinstance(amount, float):
                amount = Decimal(str(amount))
            
            # Création de la demande
            refund_request = RefundRequest(
                id=request_id,
                transaction_id=transaction_id,
                customer_id=customer_id,
                amount=amount,
                currency="USD",  # Default currency
                reason=reason,
                status=RefundStatus.PENDING,
                requested_at=datetime.now(),
                notes=notes
            )
            
            # Stockage de la demande
            self.refund_requests[request_id] = refund_request
            
            # Auto-approval pour les petits montants
            if amount <= self.auto_approval_limit:
                await self.approve_refund(request_id, "system_auto_approval")
            
            logger.info(f"Refund request created: {request_id}")
            return refund_request
            
        except Exception as e:
            logger.error(f"Error creating refund request: {e}")
            raise

    async def approve_refund(self, request_id: str, approved_by: str) -> bool:
        """Approuve une demande de remboursement
        
        Args:
            request_id: ID de la demande
            approved_by: Qui a approuvé la demande
            
        Returns:
            bool: True si approuvé avec succès
        """
        try:
            refund_request = self.refund_requests.get(request_id)
            if not refund_request:
                logger.error(f"Refund request not found: {request_id}")
                return False
            
            if refund_request.status != RefundStatus.PENDING:
                logger.error(f"Cannot approve refund in status: {refund_request.status}")
                return False
            
            # Mise à jour du statut
            refund_request.status = RefundStatus.APPROVED
            refund_request.approved_by = approved_by
            refund_request.processed_at = datetime.now()
            
            # Traitement du remboursement
            await self._process_refund(refund_request)
            
            logger.info(f"Refund approved: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving refund: {e}")
            return False

    async def reject_refund(self, request_id: str, rejected_by: str, reason: str) -> bool:
        """Rejette une demande de remboursement
        
        Args:
            request_id: ID de la demande
            rejected_by: Qui a rejeté la demande
            reason: Raison du rejet
            
        Returns:
            bool: True si rejeté avec succès
        """
        try:
            refund_request = self.refund_requests.get(request_id)
            if not refund_request:
                logger.error(f"Refund request not found: {request_id}")
                return False
            
            if refund_request.status != RefundStatus.PENDING:
                logger.error(f"Cannot reject refund in status: {refund_request.status}")
                return False
            
            # Mise à jour du statut
            refund_request.status = RefundStatus.REJECTED
            refund_request.approved_by = rejected_by
            refund_request.notes = f"Rejected: {reason}"
            refund_request.processed_at = datetime.now()
            
            logger.info(f"Refund rejected: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting refund: {e}")
            return False

    async def _process_refund(self, refund_request: RefundRequest) -> bool:
        """Traite effectivement le remboursement
        
        Args:
            refund_request: La demande de remboursement
            
        Returns:
            bool: True si traité avec succès
        """
        try:
            # Simulation du traitement du remboursement
            # En réalité, ici on appellerait l'API du processeur de paiement
            
            # Mise à jour du statut
            refund_request.status = RefundStatus.PROCESSED
            
            logger.info(f"Refund processed: {refund_request.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            refund_request.status = RefundStatus.FAILED
            return False

    def get_refund_request(self, request_id: str) -> Optional[RefundRequest]:
        """Récupère une demande de remboursement
        
        Args:
            request_id: ID de la demande
            
        Returns:
            Optional[RefundRequest]: La demande si trouvée
        """
        return self.refund_requests.get(request_id)

    def list_refund_requests(
        self,
        customer_id: Optional[str] = None,
        status: Optional[RefundStatus] = None
    ) -> List[RefundRequest]:
        """Liste les demandes de remboursement avec filtres optionnels
        
        Args:
            customer_id: Filtrer par client
            status: Filtrer par statut
            
        Returns:
            List[RefundRequest]: Liste des demandes filtrées
        """
        requests = list(self.refund_requests.values())
        
        if customer_id:
            requests = [r for r in requests if r.customer_id == customer_id]
        
        if status:
            requests = [r for r in requests if r.status == status]
        
        return requests

    def get_refund_stats(self) -> Dict[str, Any]:
        """Génère des statistiques sur les remboursements
        
        Returns:
            Dict[str, Any]: Statistiques des remboursements
        """
        try:
            total_requests = len(self.refund_requests)
            total_amount = sum(r.amount for r in self.refund_requests.values())
            
            status_counts = {}
            for status in RefundStatus:
                status_counts[status.value] = len([
                    r for r in self.refund_requests.values() 
                    if r.status == status
                ])
            
            return {
                "total_requests": total_requests,
                "total_amount": float(total_amount),
                "status_breakdown": status_counts,
                "auto_approval_rate": (
                    status_counts.get("approved", 0) / max(total_requests, 1) * 100
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating refund stats: {e}")
            return {}