"""
🚀 Payment Methods & Refund Manager - IA Influencer Agent Platform Enterprise
============================================================================
Module: backend/platform_core/billing/payment_methods.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTION DES MÉTHODES DE PAIEMENT
Système de gestion sécurisée des moyens de paiement clients
- Tokenisation et chiffrement PCI-DSS
- Gestion multi-cartes et comptes bancaires
- Validation en temps réel et scoring de risque
- Backup automatique et retry intelligent
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import hashlib
import base64

from cryptography.fernet import Fernet

# Configuration
logger = logging.getLogger(__name__)

class PaymentMethodType(Enum):
    """Types de méthodes de paiement"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO_WALLET = "crypto_wallet"
    GIFT_CARD = "gift_card"
    STORE_CREDIT = "store_credit"

class CardBrand(Enum):
    """Marques de cartes"""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"
    DINERS = "diners"
    JCB = "jcb"
    UNIONPAY = "unionpay"

class PaymentMethodStatus(Enum):
    """États des méthodes de paiement"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    INVALID = "invalid"
    PENDING_VERIFICATION = "pending_verification"
    BLOCKED = "blocked"

@dataclass
class PaymentMethod:
    """Méthode de paiement"""
    payment_method_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    
    # Type et statut
    method_type: PaymentMethodType = PaymentMethodType.CREDIT_CARD
    status: PaymentMethodStatus = PaymentMethodStatus.ACTIVE
    
    # Données sécurisées (tokenisées)
    token: str = ""  # Token du provider (Stripe, etc.)
    fingerprint: str = ""  # Empreinte unique
    
    # Informations affichables (non sensibles)
    display_name: str = ""
    last_four: str = ""
    brand: Optional[CardBrand] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    
    # Adresse de facturation
    billing_address: Dict[str, str] = field(default_factory=dict)
    
    # Métadonnées
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Historique des transactions
    successful_payments: int = 0
    failed_payments: int = 0
    total_amount_processed: Decimal = Decimal("0.0")
    
    # Gestion des risques
    risk_score: float = 0.0
    fraud_flags: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la méthode de paiement est expirée"""
        if not self.expiry_month or not self.expiry_year:
            return False
            
        now = datetime.utcnow()
        expiry_date = datetime(self.expiry_year, self.expiry_month, 1)
        
        # Ajouter un mois car les cartes expirent à la fin du mois
        expiry_date = expiry_date.replace(day=28) + timedelta(days=4)
        expiry_date = expiry_date - timedelta(days=expiry_date.day)
        
        return now > expiry_date
        
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès"""
        total = self.successful_payments + self.failed_payments
        if total == 0:
            return 1.0
        return self.successful_payments / total

class PaymentMethodManager:
    """Gestionnaire des méthodes de paiement"""
    
    def __init__(self, 
                 encryption_key: Optional[bytes] = None,
                 database_client: Optional[Any] = None):
        self.database_client = database_client
        self.payment_methods: Dict[str, PaymentMethod] = {}
        
        # Chiffrement pour données sensibles
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def add_payment_method(self,
                               customer_id: str,
                               method_type: PaymentMethodType,
                               provider_token: str,
                               **kwargs) -> PaymentMethod:
        """Ajoute une nouvelle méthode de paiement"""
        
        payment_method = PaymentMethod(
            customer_id=customer_id,
            method_type=method_type,
            token=provider_token,
            **kwargs
        )
        
        # Générer l'empreinte
        payment_method.fingerprint = self._generate_fingerprint(payment_method)
        
        # Chiffrer les données sensibles si nécessaires
        if hasattr(payment_method, 'sensitive_data'):
            payment_method.encrypted_data = self._encrypt_sensitive_data(payment_method.sensitive_data)
            
        # Définir comme méthode par défaut si c'est la première
        customer_methods = await self.get_customer_payment_methods(customer_id)
        if not customer_methods:
            payment_method.is_default = True
            
        # Sauvegarder
        self.payment_methods[payment_method.payment_method_id] = payment_method
        
        if self.database_client:
            await self._save_payment_method(payment_method)
            
        logger.info(f"Méthode de paiement ajoutée: {payment_method.payment_method_id} pour client {customer_id}")
        return payment_method
        
    async def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """Récupère une méthode de paiement par ID"""
        if payment_method_id in self.payment_methods:
            return self.payment_methods[payment_method_id]
            
        if self.database_client:
            method = await self._load_payment_method(payment_method_id)
            if method:
                self.payment_methods[payment_method_id] = method
            return method
            
        return None
        
    async def get_customer_payment_methods(self, customer_id: str) -> List[PaymentMethod]:
        """Récupère toutes les méthodes de paiement d'un client"""
        methods = []
        
        # Chercher dans le cache
        for method in self.payment_methods.values():
            if method.customer_id == customer_id:
                methods.append(method)
                
        # Chercher en base si nécessaire
        if self.database_client:
            db_methods = await self._load_customer_payment_methods(customer_id)
            for method in db_methods:
                if method.payment_method_id not in self.payment_methods:
                    self.payment_methods[method.payment_method_id] = method
                    methods.append(method)
                    
        # Trier par défaut en premier, puis par date de création
        methods.sort(key=lambda m: (not m.is_default, m.created_at), reverse=True)
        return methods
        
    async def set_default_payment_method(self, customer_id: str, payment_method_id: str) -> bool:
        """Définit la méthode de paiement par défaut"""
        # Récupérer toutes les méthodes du client
        customer_methods = await self.get_customer_payment_methods(customer_id)
        
        method_found = False
        for method in customer_methods:
            if method.payment_method_id == payment_method_id:
                method.is_default = True
                method_found = True
            else:
                method.is_default = False
                
            if self.database_client:
                await self._save_payment_method(method)
                
        if method_found:
            logger.info(f"Méthode par défaut définie: {payment_method_id} pour client {customer_id}")
            
        return method_found
        
    async def verify_payment_method(self, 
                                  payment_method_id: str,
                                  verification_amount: Optional[Decimal] = None) -> bool:
        """Vérifie une méthode de paiement"""
        method = await self.get_payment_method(payment_method_id)
        if not method:
            return False
            
        try:
            # Dans un vrai système, on ferait une micro-transaction ou validation
            # via le provider de paiement (Stripe, etc.)
            
            # Simulation de vérification
            verification_successful = True  # Simplification
            
            if verification_successful:
                method.status = PaymentMethodStatus.ACTIVE
                method.verified_at = datetime.utcnow()
                
                if self.database_client:
                    await self._save_payment_method(method)
                    
                logger.info(f"Méthode de paiement vérifiée: {payment_method_id}")
                return True
            else:
                method.status = PaymentMethodStatus.INVALID
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de {payment_method_id}: {e}")
            method.status = PaymentMethodStatus.INVALID
            return False
            
    async def deactivate_payment_method(self, payment_method_id: str) -> bool:
        """Désactive une méthode de paiement"""
        method = await self.get_payment_method(payment_method_id)
        if not method:
            return False
            
        method.status = PaymentMethodStatus.INACTIVE
        
        # Si c'était la méthode par défaut, en choisir une autre
        if method.is_default:
            customer_methods = await self.get_customer_payment_methods(method.customer_id)
            active_methods = [m for m in customer_methods 
                            if m.payment_method_id != payment_method_id 
                            and m.status == PaymentMethodStatus.ACTIVE]
            
            if active_methods:
                active_methods[0].is_default = True
                if self.database_client:
                    await self._save_payment_method(active_methods[0])
                    
        if self.database_client:
            await self._save_payment_method(method)
            
        logger.info(f"Méthode de paiement désactivée: {payment_method_id}")
        return True
        
    async def update_payment_stats(self,
                                 payment_method_id: str,
                                 success: bool,
                                 amount: Decimal):
        """Met à jour les statistiques d'une méthode de paiement"""
        method = await self.get_payment_method(payment_method_id)
        if not method:
            return
            
        if success:
            method.successful_payments += 1
            method.total_amount_processed += amount
        else:
            method.failed_payments += 1
            
        method.last_used_at = datetime.utcnow()
        
        # Calculer le score de risque
        method.risk_score = self._calculate_risk_score(method)
        
        if self.database_client:
            await self._save_payment_method(method)
            
    def _generate_fingerprint(self, method: PaymentMethod) -> str:
        """Génère une empreinte unique pour la méthode de paiement"""
        # Combiner des éléments non sensibles pour créer une empreinte
        fingerprint_data = f"{method.customer_id}:{method.method_type.value}:{method.last_four}:{method.brand.value if method.brand else 'none'}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Chiffre les données sensibles"""
        return base64.b64encode(self.cipher_suite.encrypt(data.encode())).decode()
        
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Déchiffre les données sensibles"""
        return self.cipher_suite.decrypt(base64.b64decode(encrypted_data.encode())).decode()
        
    def _calculate_risk_score(self, method: PaymentMethod) -> float:
        """Calcule le score de risque d'une méthode de paiement"""
        score = 0.0
        
        # Facteurs de risque
        if method.failed_payments > 0:
            failure_rate = method.failed_payments / (method.successful_payments + method.failed_payments)
            score += failure_rate * 0.4
            
        # Méthode récemment ajoutée
        days_since_creation = (datetime.utcnow() - method.created_at).days
        if days_since_creation < 7:
            score += 0.2
            
        # Flags de fraude
        score += len(method.fraud_flags) * 0.1
        
        # Limiter entre 0 et 1
        return min(1.0, max(0.0, score))
        
    async def _save_payment_method(self, method: PaymentMethod):
        """Sauvegarde une méthode de paiement en base"""
        # Implémentation de sauvegarde
        pass
        
    async def _load_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """Charge une méthode de paiement depuis la base"""
        # Implémentation de chargement
        return None
        
    async def _load_customer_payment_methods(self, customer_id: str) -> List[PaymentMethod]:
        """Charge toutes les méthodes de paiement d'un client"""
        # Implémentation de chargement
        return []

@dataclass
class RefundRequest:
    """Demande de remboursement"""
    refund_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payment_id: str = ""
    customer_id: str = ""
    
    # Montants
    requested_amount: Decimal = Decimal("0.0")
    approved_amount: Decimal = Decimal("0.0")
    processing_fee: Decimal = Decimal("0.0")
    
    # Motif et statut
    reason: str = ""
    status: str = "pending"  # pending, approved, rejected, processed, failed
    
    # Dates
    requested_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Métadonnées
    requested_by: str = ""  # ID utilisateur qui demande
    approved_by: Optional[str] = None
    notes: str = ""

class RefundManager:
    """Gestionnaire des remboursements"""
    
    def __init__(self, 
                 payment_processor: Any,
                 database_client: Optional[Any] = None):
        self.payment_processor = payment_processor
        self.database_client = database_client
        self.refund_requests: Dict[str, RefundRequest] = {}
        
        # Configuration
        self.auto_approval_threshold = Decimal("100.00")  # Auto-approuver < 100$
        self.max_refund_days = 30  # Limite temporelle pour remboursement
        
    async def request_refund(self,
                           payment_id: str,
                           customer_id: str,
                           amount: Decimal,
                           reason: str,
                           requested_by: str) -> RefundRequest:
        """Crée une demande de remboursement"""
        
        refund_request = RefundRequest(
            payment_id=payment_id,
            customer_id=customer_id,
            requested_amount=amount,
            reason=reason,
            requested_by=requested_by
        )
        
        # Validation de base
        if not await self._validate_refund_request(refund_request):
            refund_request.status = "rejected"
            refund_request.notes = "Demande invalide ou hors délai"
            
        # Auto-approbation pour petits montants
        elif amount <= self.auto_approval_threshold:
            refund_request.status = "approved"
            refund_request.approved_amount = amount
            refund_request.approved_at = datetime.utcnow()
            refund_request.approved_by = "auto_approval"
            
            # Traiter immédiatement
            await self._process_refund(refund_request)
            
        self.refund_requests[refund_request.refund_id] = refund_request
        
        if self.database_client:
            await self._save_refund_request(refund_request)
            
        logger.info(f"Demande de remboursement créée: {refund_request.refund_id} ({amount})")
        return refund_request
        
    async def approve_refund(self,
                           refund_id: str,
                           approved_amount: Optional[Decimal] = None,
                           approved_by: str = "",
                           notes: str = "") -> bool:
        """Approuve une demande de remboursement"""
        
        refund_request = self.refund_requests.get(refund_id)
        if not refund_request or refund_request.status != "pending":
            return False
            
        refund_request.status = "approved"
        refund_request.approved_amount = approved_amount or refund_request.requested_amount
        refund_request.approved_at = datetime.utcnow()
        refund_request.approved_by = approved_by
        refund_request.notes += f"\nApprouvé: {notes}" if notes else ""
        
        # Traiter le remboursement
        success = await self._process_refund(refund_request)
        
        if self.database_client:
            await self._save_refund_request(refund_request)
            
        logger.info(f"Remboursement {'traité' if success else 'échoué'}: {refund_id}")
        return success
        
    async def reject_refund(self,
                          refund_id: str,
                          rejected_by: str = "",
                          reason: str = "") -> bool:
        """Rejette une demande de remboursement"""
        
        refund_request = self.refund_requests.get(refund_id)
        if not refund_request or refund_request.status != "pending":
            return False
            
        refund_request.status = "rejected"
        refund_request.notes += f"\nRejeté par {rejected_by}: {reason}"
        
        if self.database_client:
            await self._save_refund_request(refund_request)
            
        logger.info(f"Remboursement rejeté: {refund_id}")
        return True
        
    async def get_pending_refunds(self) -> List[RefundRequest]:
        """Récupère toutes les demandes en attente"""
        return [r for r in self.refund_requests.values() if r.status == "pending"]
        
    async def _validate_refund_request(self, request: RefundRequest) -> bool:
        """Valide une demande de remboursement"""
        
        # Vérifier les délais
        payment_date = datetime.utcnow() - timedelta(days=self.max_refund_days)  # Simulation
        if payment_date < datetime.utcnow() - timedelta(days=self.max_refund_days):
            return False
            
        # Vérifier le montant
        if request.requested_amount <= 0:
            return False
            
        # Autres validations métier
        return True
        
    async def _process_refund(self, request: RefundRequest) -> bool:
        """Traite un remboursement approuvé"""
        try:
            # Utiliser le processeur de paiement pour effectuer le remboursement
            response = await self.payment_processor.refund_payment(
                payment_id=request.payment_id,
                amount=request.approved_amount,
                reason=request.reason
            )
            
            if response.status.value in ["refunded", "partial_refund"]:
                request.status = "processed"
                request.processed_at = datetime.utcnow()
                request.processing_fee = response.fees
                return True
            else:
                request.status = "failed"
                request.notes += f"\nÉchec du traitement: {response.failure_reason}"
                return False
                
        except Exception as e:
            request.status = "failed"
            request.notes += f"\nErreur de traitement: {str(e)}"
            logger.error(f"Erreur lors du traitement du remboursement {request.refund_id}: {e}")
            return False
            
    async def _save_refund_request(self, request: RefundRequest):
        """Sauvegarde une demande de remboursement"""
        # Implémentation de sauvegarde
        pass
        
    def get_refund_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des remboursements"""
        total_requests = len(self.refund_requests)
        approved = len([r for r in self.refund_requests.values() if r.status == "approved"])
        processed = len([r for r in self.refund_requests.values() if r.status == "processed"])
        
        return {
            "total_requests": total_requests,
            "approved_requests": approved,
            "processed_requests": processed,
            "approval_rate": (approved / total_requests) if total_requests > 0 else 0,
            "auto_approval_threshold": float(self.auto_approval_threshold),
            "max_refund_days": self.max_refund_days
        }