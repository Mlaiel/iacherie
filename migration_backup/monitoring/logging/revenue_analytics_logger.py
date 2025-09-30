"""💰 Revenue Analytics Logger - Creator Economy Monetization Tracking
==================================================================
Experts: Backend Senior + DBA + Sécurité + ML Engineer + DevOps
Technologies: PostgreSQL + InfluxDB + Audit Logs + Financial APIs + Real-time Streaming
Business Logic: Monétisation créateur → Tracking revenus → Analytics ROI → Audit financier
==================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
import hashlib
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================

class RevenueType(Enum):
    """Types de revenus Creator Economy"""
    # Direct monetization
    SUBSCRIPTION = "subscription"
    ONE_TIME_PAYMENT = "one_time_payment"
    TIP_DONATION = "tip_donation"
    MERCHANDISE = "merchandise"
    
    # Content monetization
    CONTENT_LICENSING = "content_licensing"
    CONTENT_SALES = "content_sales"
    PAY_PER_VIEW = "pay_per_view"
    PREMIUM_CONTENT = "premium_content"
    
    # Collaboration revenue
    BRAND_PARTNERSHIP = "brand_partnership"
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_COMMISSION = "affiliate_commission"
    COLLABORATION_FEE = "collaboration_fee"
    
    # Platform revenue
    AD_REVENUE = "ad_revenue"
    PLATFORM_BONUS = "platform_bonus"
    REFERRAL_BONUS = "referral_bonus"
    ACHIEVEMENT_REWARD = "achievement_reward"

class PaymentMethod(Enum):
    """Méthodes de paiement"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    PLATFORM_CREDIT = "platform_credit"

class TransactionStatus(Enum):
    """Statuts de transaction"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class Currency(Enum):
    """Devises supportées"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    JPY = "JPY"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"

class AuditLevel(Enum):
    """Niveaux d'audit financier"""
    LOW = "low"           # Transactions standard
    MEDIUM = "medium"     # Transactions importantes
    HIGH = "high"         # Transactions critiques
    CRITICAL = "critical" # Transactions suspectes

# ==================== DATA MODELS ====================

@dataclass
class RevenueTransaction:
    """Transaction de revenus complète"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Creator context
    creator_id: str = ""
    creator_tier: Optional[str] = None
    
    # Transaction details
    transaction_type: RevenueType = RevenueType.ONE_TIME_PAYMENT
    amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    currency: Currency = Currency.USD
    exchange_rate: Optional[Decimal] = None
    amount_usd: Optional[Decimal] = None
    
    # Payment details
    payment_method: Optional[PaymentMethod] = None
    payment_processor: Optional[str] = None
    transaction_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    
    # Status tracking
    status: TransactionStatus = TransactionStatus.PENDING
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Content/collaboration context
    content_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    campaign_id: Optional[str] = None
    
    # Fees and commissions
    platform_fee: Decimal = field(default_factory=lambda: Decimal('0.00'))
    processing_fee: Decimal = field(default_factory=lambda: Decimal('0.00'))
    net_amount: Optional[Decimal] = None
    
    # Tax information
    tax_rate: Decimal = field(default_factory=lambda: Decimal('0.00'))
    tax_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    tax_jurisdiction: Optional[str] = None
    
    # Analytics metrics
    conversion_source: Optional[str] = None
    roi_factor: Optional[Decimal] = None
    customer_ltv: Optional[Decimal] = None
    
    # Security and compliance
    audit_level: AuditLevel = AuditLevel.LOW
    risk_score: float = 0.0
    compliance_flags: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Technical context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization calculations"""
        # Calculate net amount
        if self.net_amount is None:
            self.net_amount = self.amount - self.platform_fee - self.processing_fee - self.tax_amount
        
        # Convert to USD if needed
        if self.amount_usd is None and self.currency != Currency.USD:
            exchange_rate = self.exchange_rate or Decimal('1.0')
            self.amount_usd = self.amount * exchange_rate
        elif self.currency == Currency.USD:
            self.amount_usd = self.amount
        
        # Set initial status
        if not self.status_history:
            self.add_status_change(self.status, "Initial transaction creation")
    
    def add_status_change(self, new_status: TransactionStatus, reason: str = ""):
        """Ajoute un changement de statut"""
        self.status_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'old_status': self.status.value if hasattr(self, 'status') else None,
            'new_status': new_status.value,
            'reason': reason
        })
        self.status = new_status
    
    def calculate_risk_score(self) -> float:
        """Calcule le score de risque de la transaction"""
        risk_score = 0.0
        
        # Amount-based risk
        if self.amount > Decimal('1000'):
            risk_score += 0.3
        elif self.amount > Decimal('5000'):
            risk_score += 0.5
        elif self.amount > Decimal('10000'):
            risk_score += 0.7
        
        # Payment method risk
        high_risk_methods = [PaymentMethod.CRYPTOCURRENCY, PaymentMethod.BANK_TRANSFER]
        if self.payment_method in high_risk_methods:
            risk_score += 0.2
        
        # Compliance flags
        risk_score += len(self.compliance_flags) * 0.1
        
        # First-time creator risk
        if self.creator_tier == "starter":
            risk_score += 0.1
        
        self.risk_score = min(risk_score, 1.0)
        return self.risk_score
    
    def set_audit_level(self):
        """Détermine le niveau d'audit requis"""
        risk = self.calculate_risk_score()
        
        if risk >= 0.8 or self.amount > Decimal('10000'):
            self.audit_level = AuditLevel.CRITICAL
        elif risk >= 0.6 or self.amount > Decimal('5000'):
            self.audit_level = AuditLevel.HIGH
        elif risk >= 0.3 or self.amount > Decimal('1000'):
            self.audit_level = AuditLevel.MEDIUM
        else:
            self.audit_level = AuditLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'creator_id': self.creator_id,
            'creator_tier': self.creator_tier,
            'transaction_type': self.transaction_type.value,
            'amount': str(self.amount),
            'currency': self.currency.value,
            'exchange_rate': str(self.exchange_rate) if self.exchange_rate else None,
            'amount_usd': str(self.amount_usd) if self.amount_usd else None,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'payment_processor': self.payment_processor,
            'transaction_id': self.transaction_id,
            'external_transaction_id': self.external_transaction_id,
            'status': self.status.value,
            'status_history': self.status_history,
            'content_id': self.content_id,
            'collaboration_id': self.collaboration_id,
            'campaign_id': self.campaign_id,
            'platform_fee': str(self.platform_fee),
            'processing_fee': str(self.processing_fee),
            'net_amount': str(self.net_amount) if self.net_amount else None,
            'tax_rate': str(self.tax_rate),
            'tax_amount': str(self.tax_amount),
            'tax_jurisdiction': self.tax_jurisdiction,
            'conversion_source': self.conversion_source,
            'roi_factor': str(self.roi_factor) if self.roi_factor else None,
            'customer_ltv': str(self.customer_ltv) if self.customer_ltv else None,
            'audit_level': self.audit_level.value,
            'risk_score': self.risk_score,
            'compliance_flags': self.compliance_flags,
            'description': self.description,
            'tags': self.tags,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id
        }

@dataclass
class RevenueReport:
    """Rapport de revenus créateur"""
    creator_id: str
    period_start: datetime
    period_end: datetime
    
    # Summary metrics
    total_revenue: Decimal = field(default_factory=lambda: Decimal('0.00'))
    total_transactions: int = 0
    net_revenue: Decimal = field(default_factory=lambda: Decimal('0.00'))
    total_fees: Decimal = field(default_factory=lambda: Decimal('0.00'))
    total_tax: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    # Revenue breakdown
    revenue_by_type: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_currency: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_month: Dict[str, Decimal] = field(default_factory=dict)
    
    # Performance metrics
    average_transaction: Decimal = field(default_factory=lambda: Decimal('0.00'))
    conversion_rate: float = 0.0
    customer_count: int = 0
    repeat_customer_rate: float = 0.0
    
    # Growth metrics
    growth_rate: float = 0.0
    projection_next_month: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    # Top performing content
    top_content: List[Dict[str, Any]] = field(default_factory=list)
    top_collaborations: List[Dict[str, Any]] = field(default_factory=list)

# ==================== ANALYTICS ENGINE ====================

class RevenueAnalyticsEngine:
    """Moteur d'analytics avancé pour revenus Creator Economy"""
    
    def __init__(self):
        self.transactions: Dict[str, List[RevenueTransaction]] = defaultdict(list)
        self.revenue_trends = defaultdict(list)
        self.performance_metrics = defaultdict(dict)
        self.fraud_patterns = defaultdict(list)
        self.lock = threading.RLock()
        
        # Real-time metrics
        self.realtime_metrics = {
            'total_revenue_today': Decimal('0.00'),
            'active_earners': 0,
            'average_transaction': Decimal('0.00'),
            'highest_earner': None,
            'trending_revenue_types': []
        }
    
    def analyze_transaction(self, transaction: RevenueTransaction):
        """Analyse une transaction en temps réel"""
        with self.lock:
            creator_id = transaction.creator_id
            
            # Ajouter à l'historique
            self.transactions[creator_id].append(transaction)
            
            # Analytics spécialisées
            self._analyze_revenue_trends(transaction)
            self._analyze_performance_metrics(transaction)
            self._detect_fraud_patterns(transaction)
            self._update_realtime_metrics()
            
            # Alertes si nécessaire
            self._check_alerts(transaction)
    
    def _analyze_revenue_trends(self, transaction: RevenueTransaction):
        """Analyse les tendances de revenus"""
        creator_id = transaction.creator_id
        date_key = transaction.timestamp.strftime('%Y-%m-%d')
        
        # Tendances par jour
        self.revenue_trends[f"{creator_id}_{date_key}"].append({
            'amount': transaction.amount,
            'type': transaction.transaction_type.value,
            'timestamp': transaction.timestamp,
            'net_amount': transaction.net_amount
        })
        
        # Tendances globales
        self.revenue_trends[f"global_{date_key}"].append({
            'creator_id': creator_id,
            'amount': transaction.amount,
            'type': transaction.transaction_type.value
        })
    
    def _analyze_performance_metrics(self, transaction: RevenueTransaction):
        """Analyse les métriques de performance"""
        creator_id = transaction.creator_id
        
        if creator_id not in self.performance_metrics:
            self.performance_metrics[creator_id] = {
                'total_revenue': Decimal('0.00'),
                'transaction_count': 0,
                'revenue_types': defaultdict(Decimal),
                'monthly_revenue': defaultdict(Decimal),
                'conversion_sources': defaultdict(int),
                'highest_transaction': Decimal('0.00'),
                'first_transaction': transaction.timestamp,
                'last_transaction': transaction.timestamp
            }
        
        metrics = self.performance_metrics[creator_id]
        
        # Mise à jour des métriques
        metrics['total_revenue'] += transaction.amount
        metrics['transaction_count'] += 1
        metrics['revenue_types'][transaction.transaction_type.value] += transaction.amount
        
        month_key = transaction.timestamp.strftime('%Y-%m')
        metrics['monthly_revenue'][month_key] += transaction.amount
        
        if transaction.conversion_source:
            metrics['conversion_sources'][transaction.conversion_source] += 1
        
        if transaction.amount > metrics['highest_transaction']:
            metrics['highest_transaction'] = transaction.amount
        
        metrics['last_transaction'] = transaction.timestamp
    
    def _detect_fraud_patterns(self, transaction: RevenueTransaction):
        """Détection de patterns frauduleux"""
        creator_id = transaction.creator_id
        
        # Pattern: Transactions multiples rapides
        recent_transactions = [
            t for t in self.transactions[creator_id]
            if t.timestamp >= datetime.utcnow() - timedelta(minutes=10)
        ]
        
        if len(recent_transactions) > 5:
            self.fraud_patterns[creator_id].append({
                'type': 'rapid_transactions',
                'timestamp': transaction.timestamp,
                'count': len(recent_transactions),
                'severity': 'medium'
            })
            transaction.compliance_flags.append('rapid_transactions')
        
        # Pattern: Montants ronds suspects
        if transaction.amount % 100 == 0 and transaction.amount > Decimal('1000'):
            self.fraud_patterns[creator_id].append({
                'type': 'round_amount_suspicious',
                'timestamp': transaction.timestamp,
                'amount': transaction.amount,
                'severity': 'low'
            })
            transaction.compliance_flags.append('round_amount')
        
        # Pattern: Même IP pour créateurs différents
        if transaction.ip_address:
            similar_ip_creators = [
                cid for cid, transactions in self.transactions.items()
                if any(t.ip_address == transaction.ip_address for t in transactions)
                and cid != creator_id
            ]
            
            if similar_ip_creators:
                self.fraud_patterns[creator_id].append({
                    'type': 'shared_ip_address',
                    'timestamp': transaction.timestamp,
                    'ip': transaction.ip_address,
                    'other_creators': similar_ip_creators,
                    'severity': 'high'
                })
                transaction.compliance_flags.append('shared_ip')
    
    def _update_realtime_metrics(self):
        """Met à jour les métriques temps réel"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Revenue total aujourd'hui
        today_revenue = Decimal('0.00')
        today_transactions = []
        active_earners = set()
        
        for creator_id, transactions in self.transactions.items():
            creator_today = [
                t for t in transactions
                if t.timestamp.strftime('%Y-%m-%d') == today
            ]
            
            if creator_today:
                active_earners.add(creator_id)
                for t in creator_today:
                    today_revenue += t.amount
                    today_transactions.append(t)
        
        self.realtime_metrics['total_revenue_today'] = today_revenue
        self.realtime_metrics['active_earners'] = len(active_earners)
        
        if today_transactions:
            avg_transaction = today_revenue / len(today_transactions)
            self.realtime_metrics['average_transaction'] = avg_transaction
        
        # Top earner
        if self.performance_metrics:
            top_earner = max(
                self.performance_metrics.items(),
                key=lambda x: x[1]['total_revenue']
            )
            self.realtime_metrics['highest_earner'] = {
                'creator_id': top_earner[0],
                'total_revenue': str(top_earner[1]['total_revenue'])
            }
        
        # Types de revenus tendance
        type_counts = defaultdict(int)
        for transactions in self.transactions.values():
            for t in transactions:
                if t.timestamp.strftime('%Y-%m-%d') == today:
                    type_counts[t.transaction_type.value] += 1
        
        trending_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        self.realtime_metrics['trending_revenue_types'] = [
            {'type': t[0], 'count': t[1]} for t in trending_types
        ]
    
    def _check_alerts(self, transaction: RevenueTransaction):
        """Vérifie et génère des alertes"""
        alerts = []
        
        # Alerte: Transaction importante
        if transaction.amount > Decimal('5000'):
            alerts.append({
                'type': 'high_value_transaction',
                'severity': 'high',
                'message': f"High value transaction: {transaction.amount} {transaction.currency.value}",
                'transaction_id': transaction.id
            })
        
        # Alerte: Risque élevé
        if transaction.risk_score > 0.7:
            alerts.append({
                'type': 'high_risk_transaction',
                'severity': 'critical',
                'message': f"High risk transaction detected: risk score {transaction.risk_score}",
                'transaction_id': transaction.id
            })
        
        # Alerte: Flags de compliance
        if transaction.compliance_flags:
            alerts.append({
                'type': 'compliance_flags',
                'severity': 'medium',
                'message': f"Compliance flags: {', '.join(transaction.compliance_flags)}",
                'transaction_id': transaction.id
            })
        
        # Log des alertes
        for alert in alerts:
            logger.warning(f"Revenue Alert: {alert['message']}")
    
    def generate_creator_report(self, creator_id: str, 
                              start_date: datetime, 
                              end_date: datetime) -> RevenueReport:
        """Génère un rapport de revenus pour un créateur"""
        
        creator_transactions = [
            t for t in self.transactions.get(creator_id, [])
            if start_date <= t.timestamp <= end_date
        ]
        
        if not creator_transactions:
            return RevenueReport(
                creator_id=creator_id,
                period_start=start_date,
                period_end=end_date
            )
        
        report = RevenueReport(
            creator_id=creator_id,
            period_start=start_date,
            period_end=end_date
        )
        
        # Calculs de base
        report.total_transactions = len(creator_transactions)
        report.total_revenue = sum(t.amount for t in creator_transactions)
        report.net_revenue = sum(t.net_amount or Decimal('0.00') for t in creator_transactions)
        report.total_fees = sum(t.platform_fee + t.processing_fee for t in creator_transactions)
        report.total_tax = sum(t.tax_amount for t in creator_transactions)
        
        # Moyennes
        if report.total_transactions > 0:
            report.average_transaction = report.total_revenue / report.total_transactions
        
        # Breakdown par type
        for transaction in creator_transactions:
            rev_type = transaction.transaction_type.value
            if rev_type not in report.revenue_by_type:
                report.revenue_by_type[rev_type] = Decimal('0.00')
            report.revenue_by_type[rev_type] += transaction.amount
        
        # Breakdown par devise
        for transaction in creator_transactions:
            currency = transaction.currency.value
            if currency not in report.revenue_by_currency:
                report.revenue_by_currency[currency] = Decimal('0.00')
            report.revenue_by_currency[currency] += transaction.amount
        
        # Breakdown par mois
        for transaction in creator_transactions:
            month_key = transaction.timestamp.strftime('%Y-%m')
            if month_key not in report.revenue_by_month:
                report.revenue_by_month[month_key] = Decimal('0.00')
            report.revenue_by_month[month_key] += transaction.amount
        
        # Calcul du taux de croissance
        monthly_revenues = list(report.revenue_by_month.values())
        if len(monthly_revenues) >= 2:
            last_month = monthly_revenues[-1]
            prev_month = monthly_revenues[-2]
            if prev_month > 0:
                report.growth_rate = float((last_month - prev_month) / prev_month * 100)
        
        # Projection mois suivant (simple moyenne mobile)
        if len(monthly_revenues) >= 3:
            avg_growth = sum(monthly_revenues[-3:]) / 3
            report.projection_next_month = avg_growth
        
        return report
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        total_creators = len(self.transactions)
        total_transactions = sum(len(transactions) for transactions in self.transactions.values())
        total_revenue = sum(
            sum(t.amount for t in transactions)
            for transactions in self.transactions.values()
        )
        
        # Top performers
        top_creators = []
        for creator_id, metrics in self.performance_metrics.items():
            top_creators.append({
                'creator_id': creator_id,
                'total_revenue': str(metrics['total_revenue']),
                'transaction_count': metrics['transaction_count']
            })
        
        top_creators.sort(key=lambda x: Decimal(x['total_revenue']), reverse=True)
        
        return {
            'platform_overview': {
                'total_creators': total_creators,
                'total_transactions': total_transactions,
                'total_revenue': str(total_revenue),
                'average_revenue_per_creator': str(total_revenue / total_creators) if total_creators > 0 else '0.00'
            },
            'realtime_metrics': {
                'total_revenue_today': str(self.realtime_metrics['total_revenue_today']),
                'active_earners': self.realtime_metrics['active_earners'],
                'average_transaction': str(self.realtime_metrics['average_transaction']),
                'highest_earner': self.realtime_metrics['highest_earner'],
                'trending_revenue_types': self.realtime_metrics['trending_revenue_types']
            },
            'top_creators': top_creators[:10],
            'fraud_alerts': sum(len(patterns) for patterns in self.fraud_patterns.values())
        }

# ==================== MAIN LOGGER CLASS ====================

class RevenueAnalyticsLogger:
    """Logger principal pour analytics de revenus Creator Economy"""
    
    def __init__(self, buffer_size: int = 5000, auto_flush_interval: int = 60):
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        
        # Storage
        self.transaction_buffer = deque(maxlen=buffer_size)
        self.analytics_engine = RevenueAnalyticsEngine()
        
        # Threading
        self.lock = threading.RLock()
        self.is_running = False
        self.flush_thread = None
        
        # Metrics
        self.total_logged = 0
        self.total_value_logged = Decimal('0.00')
        self.dropped_transactions = 0
        
        logger.info("💰 Revenue Analytics Logger initialized")
    
    def start(self):
        """Démarre le logger"""
        if self.is_running:
            return
            
        self.is_running = True
        self.flush_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="RevenueLogger-AutoFlush"
        )
        self.flush_thread.start()
        
        logger.info("🚀 Revenue Analytics Logger started")
    
    def stop(self):
        """Arrête le logger"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
            
        # Flush final
        self._flush_buffer()
        
        logger.info("🛑 Revenue Analytics Logger stopped")
    
    def _auto_flush_loop(self):
        """Boucle de flush automatique"""
        while self.is_running:
            time.sleep(self.auto_flush_interval)
            if self.is_running:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Vide le buffer et traite les transactions"""
        with self.lock:
            transactions_to_process = list(self.transaction_buffer)
            self.transaction_buffer.clear()
        
        for transaction in transactions_to_process:
            try:
                # Calculate risk and audit level
                transaction.calculate_risk_score()
                transaction.set_audit_level()
                
                # Analyze transaction
                self.analytics_engine.analyze_transaction(transaction)
                
                logger.debug(f"Processed revenue transaction {transaction.id}")
            except Exception as e:
                logger.error(f"Error processing transaction {transaction.id}: {e}")
    
    def log_transaction(self, 
                       creator_id: str,
                       amount: Union[float, Decimal],
                       currency: Union[str, Currency] = Currency.USD,
                       transaction_type: RevenueType = RevenueType.ONE_TIME_PAYMENT,
                       **kwargs) -> str:
        """Log une transaction de revenus"""
        
        # Conversion types
        if isinstance(currency, str):
            currency = Currency(currency)
        
        if isinstance(amount, float):
            amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        transaction = RevenueTransaction(
            creator_id=creator_id,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            **kwargs
        )
        
        with self.lock:
            if len(self.transaction_buffer) >= self.buffer_size:
                self.dropped_transactions += 1
                logger.warning(f"Transaction buffer full, dropping transaction for creator {creator_id}")
                return ""
            
            self.transaction_buffer.append(transaction)
            self.total_logged += 1
            self.total_value_logged += amount
        
        logger.info(f"Logged revenue transaction: {amount} {currency.value} for creator {creator_id}")
        return transaction.id
    
    # ==================== SPECIALIZED LOG METHODS ====================
    
    def log_subscription_payment(self, creator_id: str, amount: Union[float, Decimal],
                               subscription_tier: str = "", **kwargs) -> str:
        """Log paiement d'abonnement"""
        return self.log_transaction(
            creator_id=creator_id,
            amount=amount,
            transaction_type=RevenueType.SUBSCRIPTION,
            description=f"Subscription payment - {subscription_tier}",
            tags=["subscription", subscription_tier],
            **kwargs
        )
    
    def log_content_sale(self, creator_id: str, content_id: str, 
                        amount: Union[float, Decimal], **kwargs) -> str:
        """Log vente de contenu"""
        return self.log_transaction(
            creator_id=creator_id,
            amount=amount,
            transaction_type=RevenueType.CONTENT_SALES,
            content_id=content_id,
            description=f"Content sale - {content_id}",
            tags=["content_sale"],
            **kwargs
        )
    
    def log_brand_partnership(self, creator_id: str, amount: Union[float, Decimal],
                            brand_name: str = "", campaign_id: str = "", **kwargs) -> str:
        """Log revenus de partenariat marque"""
        return self.log_transaction(
            creator_id=creator_id,
            amount=amount,
            transaction_type=RevenueType.BRAND_PARTNERSHIP,
            campaign_id=campaign_id,
            description=f"Brand partnership - {brand_name}",
            tags=["brand_partnership", brand_name],
            metadata={"brand_name": brand_name},
            **kwargs
        )
    
    def log_tip_donation(self, creator_id: str, amount: Union[float, Decimal],
                        donor_message: str = "", **kwargs) -> str:
        """Log pourboire/donation"""
        return self.log_transaction(
            creator_id=creator_id,
            amount=amount,
            transaction_type=RevenueType.TIP_DONATION,
            description=f"Tip/Donation: {donor_message[:50]}",
            tags=["tip", "donation"],
            metadata={"donor_message": donor_message},
            **kwargs
        )
    
    def log_ad_revenue(self, creator_id: str, amount: Union[float, Decimal],
                      views: int = 0, cpm: float = 0.0, **kwargs) -> str:
        """Log revenus publicitaires"""
        return self.log_transaction(
            creator_id=creator_id,
            amount=amount,
            transaction_type=RevenueType.AD_REVENUE,
            description=f"Ad revenue - {views} views",
            tags=["ad_revenue"],
            metadata={"views": views, "cpm": cpm},
            **kwargs
        )
    
    # ==================== ANALYTICS METHODS ====================
    
    def generate_revenue_report(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """Génère un rapport de revenus"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        report = self.analytics_engine.generate_creator_report(creator_id, start_date, end_date)
        
        # Convert Decimal to string for JSON serialization
        report_dict = {
            'creator_id': report.creator_id,
            'period': {
                'start': report.period_start.isoformat(),
                'end': report.period_end.isoformat(),
                'days': days
            },
            'summary': {
                'total_revenue': str(report.total_revenue),
                'total_transactions': report.total_transactions,
                'net_revenue': str(report.net_revenue),
                'total_fees': str(report.total_fees),
                'total_tax': str(report.total_tax),
                'average_transaction': str(report.average_transaction),
                'growth_rate': report.growth_rate,
                'projection_next_month': str(report.projection_next_month)
            },
            'breakdown': {
                'by_type': {k: str(v) for k, v in report.revenue_by_type.items()},
                'by_currency': {k: str(v) for k, v in report.revenue_by_currency.items()},
                'by_month': {k: str(v) for k, v in report.revenue_by_month.items()}
            }
        }
        
        return report_dict
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        return self.analytics_engine.get_platform_analytics()
    
    def get_fraud_alerts(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère les alertes de fraude"""
        if creator_id:
            return self.analytics_engine.fraud_patterns.get(creator_id, [])
        else:
            all_alerts = []
            for patterns in self.analytics_engine.fraud_patterns.values():
                all_alerts.extend(patterns)
            return sorted(all_alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Statistiques du logger"""
        with self.lock:
            buffer_size = len(self.transaction_buffer)
            
        return {
            'total_logged': self.total_logged,
            'total_value_logged': str(self.total_value_logged),
            'dropped_transactions': self.dropped_transactions,
            'current_buffer_size': buffer_size,
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': buffer_size / self.buffer_size,
            'is_running': self.is_running,
            'total_creators_earning': len(self.analytics_engine.transactions),
            'fraud_patterns_detected': sum(len(p) for p in self.analytics_engine.fraud_patterns.values())
        }

# ==================== HELPER FUNCTIONS ====================

# Instance globale
_revenue_logger_instance: Optional[RevenueAnalyticsLogger] = None

def get_revenue_logger() -> RevenueAnalyticsLogger:
    """Récupère l'instance singleton du logger"""
    global _revenue_logger_instance
    
    if _revenue_logger_instance is None:
        _revenue_logger_instance = RevenueAnalyticsLogger()
        _revenue_logger_instance.start()
        
    return _revenue_logger_instance

def log_creator_revenue(creator_id: str, amount: float, revenue_type: str = "one_time_payment", **kwargs):
    """Helper: Log revenus créateur"""
    logger_instance = get_revenue_logger()
    rev_type = RevenueType(revenue_type) if revenue_type in [t.value for t in RevenueType] else RevenueType.ONE_TIME_PAYMENT
    return logger_instance.log_transaction(creator_id, amount, transaction_type=rev_type, **kwargs)

def log_subscription_revenue(creator_id: str, amount: float, **kwargs):
    """Helper: Log revenus d'abonnement"""
    logger_instance = get_revenue_logger()
    return logger_instance.log_subscription_payment(creator_id, amount, **kwargs)

def log_brand_collaboration_revenue(creator_id: str, amount: float, brand: str, **kwargs):
    """Helper: Log revenus de collaboration marque"""
    logger_instance = get_revenue_logger()
    return logger_instance.log_brand_partnership(creator_id, amount, brand_name=brand, **kwargs)

# ==================== DEMO ====================

if __name__ == "__main__":
    # Configuration et démonstration
    logger = RevenueAnalyticsLogger(buffer_size=1000, auto_flush_interval=10)
    logger.start()
    
    try:
        # Simulation de transactions
        creators = ["creator_1", "creator_2", "creator_3"]
        
        for i, creator_id in enumerate(creators):
            # Revenus d'abonnement
            logger.log_subscription_payment(
                creator_id=creator_id,
                amount=Decimal('29.99'),
                subscription_tier="premium"
            )
            
            # Vente de contenu
            logger.log_content_sale(
                creator_id=creator_id,
                content_id=f"content_{i+1}",
                amount=Decimal('9.99')
            )
            
            # Partenariat marque
            logger.log_brand_partnership(
                creator_id=creator_id,
                amount=Decimal('500.00') + Decimal(str(i * 200)),
                brand_name=f"Brand_{i+1}",
                campaign_id=f"campaign_{i+1}"
            )
            
            # Pourboires
            logger.log_tip_donation(
                creator_id=creator_id,
                amount=Decimal('5.00'),
                donor_message="Great content!"
            )
        
        # Attendre le traitement
        time.sleep(2)
        
        # Afficher les analytics
        print("💰 Revenue Analytics Logger Demo Results:")
        print("\n🔧 Logger Stats:")
        print(json.dumps(logger.get_logger_stats(), indent=2))
        
        print("\n🎯 Platform Analytics:")
        platform_analytics = logger.get_platform_analytics()
        print(json.dumps(platform_analytics, indent=2, default=str))
        
        print("\n👤 Creator Revenue Report (creator_1):")
        creator_report = logger.generate_revenue_report("creator_1", days=30)
        print(json.dumps(creator_report, indent=2))
        
        print("\n🚨 Fraud Alerts:")
        fraud_alerts = logger.get_fraud_alerts()
        print(json.dumps(fraud_alerts[:5], indent=2, default=str))  # Top 5 alerts
        
    finally:
        logger.stop()