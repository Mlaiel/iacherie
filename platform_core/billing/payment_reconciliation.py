"""🚀 Payment Reconciliation System - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/platform_core/billing/payment_reconciliation.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME RÉCONCILIATION PAIEMENTS AUTOMATIQUE
Réconciliation intelligente des transactions avec ML anomaly detection
- Automated matching entre internal records et gateway statements
- Multi-gateway reconciliation avec variance analysis
- ML-powered dispute detection et resolution workflows
- Real-time discrepancy alerts et automated adjustments
- Comprehensive audit trails et regulatory compliance

Multi-Expert Implementation:
🧠 Lead Dev IA: ML anomaly detection, intelligent matching, automated reconciliation
🏗️ Backend Senior: High-performance transaction processing, concurrent reconciliation
🤖 ML Engineer: Pattern recognition, fraud detection, reconciliation optimization
🗄️ DBA: Transaction data modeling, audit trails, performance optimization
🔒 Security: Financial data protection, audit compliance, SOX controls
🌐 Microservices: Multi-gateway integrations, real-time data streaming
🎵 Audio: Music industry payment reconciliation, royalty tracking
⚙️ DevOps: Automated reconciliation monitoring, alerting, error handling
💡 AI Prompt: Intelligent discrepancy resolution, automated reporting
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from collections import defaultdict
import statistics

# Configuration logging
logger = logging.getLogger(__name__)


class ReconciliationStatus(Enum):
    """États de réconciliation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    MATCHED = "matched"
    DISCREPANCY = "discrepancy"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    FAILED = "failed"


class DiscrepancyType(Enum):
    """Types de discordances"""
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_INTERNAL = "missing_internal"
    MISSING_GATEWAY = "missing_gateway"
    DUPLICATE_TRANSACTION = "duplicate_transaction"
    TIMING_DIFFERENCE = "timing_difference"
    FEE_DISCREPANCY = "fee_discrepancy"
    CURRENCY_MISMATCH = "currency_mismatch"
    STATUS_MISMATCH = "status_mismatch"


class ReconciliationSource(Enum):
    """Sources de réconciliation"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_STATEMENT = "bank_statement"
    INTERNAL_LEDGER = "internal_ledger"
    MANUAL_ENTRY = "manual_entry"


@dataclass
class InternalTransaction:
    """Transaction interne"""
    internal_id: str
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    fee_amount: Decimal
    net_amount: Decimal
    transaction_type: str  # "payment", "refund", "chargeback"
    gateway: str
    gateway_transaction_id: Optional[str]
    status: str
    processed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayTransaction:
    """Transaction du gateway"""
    gateway_id: str
    gateway_transaction_id: str
    amount: Decimal
    currency: str
    fee_amount: Decimal
    net_amount: Decimal
    transaction_type: str
    status: str
    processed_at: datetime
    gateway_source: ReconciliationSource
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReconciliationMatch:
    """Match de réconciliation"""
    match_id: str
    internal_transaction: InternalTransaction
    gateway_transaction: Optional[GatewayTransaction]
    match_confidence: float
    match_criteria: List[str]
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    status: ReconciliationStatus = ReconciliationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class ReconciliationReport:
    """Rapport de réconciliation"""
    report_id: str
    period_start: date
    period_end: date
    total_internal_transactions: int
    total_gateway_transactions: int
    matched_transactions: int
    discrepancies_found: int
    unmatched_internal: int
    unmatched_gateway: int
    total_amount_reconciled: Decimal
    total_discrepancy_amount: Decimal
    reconciliation_rate: float
    processing_time_seconds: float
    generated_at: datetime = field(default_factory=datetime.utcnow)


class MLReconciliationEngine:
    """🤖 Moteur ML de réconciliation"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.matching_weights = {
            "exact_amount": 0.4,
            "transaction_id": 0.3,
            "timing_proximity": 0.15,
            "customer_match": 0.1,
            "gateway_consistency": 0.05
        }
        self.anomaly_threshold = 0.7
    
    def calculate_match_confidence(
        self,
        internal_tx: InternalTransaction,
        gateway_tx: GatewayTransaction
    ) -> Tuple[float, List[str]]:
        """🎯 Calcul de confiance de matching"""
        
        confidence_score = 0.0
        match_criteria = []
        
        # 1. Correspondance exacte du montant
        if internal_tx.amount == gateway_tx.amount:
            confidence_score += self.matching_weights["exact_amount"]
            match_criteria.append("exact_amount_match")
        elif abs(internal_tx.amount - gateway_tx.amount) <= Decimal('0.01'):
            confidence_score += self.matching_weights["exact_amount"] * 0.9
            match_criteria.append("near_amount_match")
        
        # 2. Correspondance ID de transaction
        if (internal_tx.gateway_transaction_id and 
            internal_tx.gateway_transaction_id == gateway_tx.gateway_transaction_id):
            confidence_score += self.matching_weights["transaction_id"]
            match_criteria.append("transaction_id_match")
        
        # 3. Proximité temporelle
        time_diff = abs((internal_tx.processed_at - gateway_tx.processed_at).total_seconds())
        if time_diff <= 300:  # 5 minutes
            confidence_score += self.matching_weights["timing_proximity"]
            match_criteria.append("exact_timing")
        elif time_diff <= 3600:  # 1 heure
            confidence_score += self.matching_weights["timing_proximity"] * 0.7
            match_criteria.append("close_timing")
        elif time_diff <= 86400:  # 24 heures
            confidence_score += self.matching_weights["timing_proximity"] * 0.3
            match_criteria.append("same_day")
        
        # 4. Correspondance client (si disponible)
        if hasattr(gateway_tx, 'customer_id') and internal_tx.customer_id == getattr(gateway_tx, 'customer_id', None):
            confidence_score += self.matching_weights["customer_match"]
            match_criteria.append("customer_match")
        
        # 5. Cohérence gateway
        if internal_tx.gateway.lower() == gateway_tx.gateway_source.value.lower():
            confidence_score += self.matching_weights["gateway_consistency"]
            match_criteria.append("gateway_consistency")
        
        return confidence_score, match_criteria
    
    def detect_anomalies(
        self,
        transactions: List[InternalTransaction],
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """🚨 Détection d'anomalies"""
        
        anomalies = []
        
        # Analyse par fenêtre temporelle
        now = datetime.utcnow()
        window_start = now - timedelta(hours=time_window_hours)
        
        recent_transactions = [
            tx for tx in transactions
            if tx.processed_at >= window_start
        ]
        
        if not recent_transactions:
            return anomalies
        
        # Calcul des métriques de base
        amounts = [float(tx.amount) for tx in recent_transactions]
        avg_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Détection d'anomalies de montant
        for tx in recent_transactions:
            z_score = abs(float(tx.amount) - avg_amount) / std_amount if std_amount > 0 else 0
            
            if z_score > 3:  # Anomalie statistique
                anomalies.append({
                    "type": "amount_anomaly",
                    "transaction_id": tx.internal_id,
                    "amount": float(tx.amount),
                    "z_score": z_score,
                    "severity": "high" if z_score > 5 else "medium",
                    "description": f"Transaction amount {tx.amount} is {z_score:.2f} standard deviations from the mean"
                })
        
        # Détection de transactions dupliquées
        seen_transactions = {}
        for tx in recent_transactions:
            key = (float(tx.amount), tx.customer_id, tx.gateway)
            
            if key in seen_transactions:
                time_diff = abs((tx.processed_at - seen_transactions[key].processed_at).total_seconds())
                
                if time_diff < 300:  # 5 minutes
                    anomalies.append({
                        "type": "potential_duplicate",
                        "transaction_id": tx.internal_id,
                        "duplicate_of": seen_transactions[key].internal_id,
                        "time_diff_seconds": time_diff,
                        "severity": "high",
                        "description": f"Potential duplicate transaction detected"
                    })
            else:
                seen_transactions[key] = tx
        
        # Détection de patterns de volume
        hourly_counts = defaultdict(int)
        for tx in recent_transactions:
            hour_key = tx.processed_at.strftime("%Y-%m-%d-%H")
            hourly_counts[hour_key] += 1
        
        if hourly_counts:
            avg_hourly = statistics.mean(hourly_counts.values())
            std_hourly = statistics.stdev(hourly_counts.values()) if len(hourly_counts) > 1 else 0
            
            for hour, count in hourly_counts.items():
                if std_hourly > 0:
                    z_score = abs(count - avg_hourly) / std_hourly
                    
                    if z_score > 2.5:
                        anomalies.append({
                            "type": "volume_anomaly",
                            "hour": hour,
                            "transaction_count": count,
                            "z_score": z_score,
                            "severity": "medium",
                            "description": f"Unusual transaction volume: {count} transactions in hour {hour}"
                        })
        
        return anomalies
    
    def suggest_matches(
        self,
        internal_tx: InternalTransaction,
        gateway_transactions: List[GatewayTransaction],
        min_confidence: float = 0.5
    ) -> List[Tuple[GatewayTransaction, float, List[str]]]:
        """💡 Suggestion de matches possibles"""
        
        suggestions = []
        
        for gateway_tx in gateway_transactions:
            confidence, criteria = self.calculate_match_confidence(internal_tx, gateway_tx)
            
            if confidence >= min_confidence:
                suggestions.append((gateway_tx, confidence, criteria))
        
        # Tri par confiance décroissante
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions


class PaymentReconciliationEngine:
    """🚀 Moteur de Réconciliation des Paiements Enterprise"""
    
    def __init__(self):
        self.ml_engine = MLReconciliationEngine()
        self.internal_transactions: Dict[str, InternalTransaction] = {}
        self.gateway_transactions: Dict[str, List[GatewayTransaction]] = defaultdict(list)
        self.reconciliation_matches: Dict[str, ReconciliationMatch] = {}
        self.reconciliation_reports: List[ReconciliationReport] = []
        self.discrepancy_rules = self._initialize_discrepancy_rules()
    
    def _initialize_discrepancy_rules(self) -> Dict[str, Dict[str, Any]]:
        """🔧 Initialisation des règles de discordance"""
        
        return {
            "amount_tolerance": {
                "percentage": 0.01,  # 1% de tolérance
                "absolute": Decimal('0.01')  # 1 centime
            },
            "timing_tolerance": {
                "seconds": 86400  # 24 heures
            },
            "fee_tolerance": {
                "percentage": 0.05  # 5% de tolérance sur les frais
            },
            "auto_resolve_thresholds": {
                "max_amount": Decimal('10.00'),
                "min_confidence": 0.95
            }
        }
    
    async def load_internal_transactions(
        self,
        transactions_data: List[Dict[str, Any]],
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """📥 Chargement des transactions internes"""
        
        try:
            loaded_count = 0
            
            for tx_data in transactions_data:
                internal_tx = InternalTransaction(
                    internal_id=tx_data["internal_id"],
                    transaction_id=tx_data["transaction_id"],
                    customer_id=tx_data["customer_id"],
                    amount=Decimal(str(tx_data["amount"])),
                    currency=tx_data["currency"],
                    fee_amount=Decimal(str(tx_data.get("fee_amount", 0))),
                    net_amount=Decimal(str(tx_data.get("net_amount", tx_data["amount"]))),
                    transaction_type=tx_data["transaction_type"],
                    gateway=tx_data["gateway"],
                    gateway_transaction_id=tx_data.get("gateway_transaction_id"),
                    status=tx_data["status"],
                    processed_at=datetime.fromisoformat(tx_data["processed_at"]),
                    metadata=tx_data.get("metadata", {})
                )
                
                # Filtrage par période
                if period_start <= internal_tx.processed_at.date() <= period_end:
                    self.internal_transactions[internal_tx.internal_id] = internal_tx
                    loaded_count += 1
            
            return {
                "status": "success",
                "loaded_transactions": loaded_count,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "loaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des transactions internes: {e}")
            return {"error": str(e)}
    
    async def load_gateway_transactions(
        self,
        gateway_source: ReconciliationSource,
        transactions_data: List[Dict[str, Any]],
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """📥 Chargement des transactions gateway"""
        
        try:
            loaded_count = 0
            
            for tx_data in transactions_data:
                gateway_tx = GatewayTransaction(
                    gateway_id=tx_data["gateway_id"],
                    gateway_transaction_id=tx_data["gateway_transaction_id"],
                    amount=Decimal(str(tx_data["amount"])),
                    currency=tx_data["currency"],
                    fee_amount=Decimal(str(tx_data.get("fee_amount", 0))),
                    net_amount=Decimal(str(tx_data.get("net_amount", tx_data["amount"]))),
                    transaction_type=tx_data["transaction_type"],
                    status=tx_data["status"],
                    processed_at=datetime.fromisoformat(tx_data["processed_at"]),
                    gateway_source=gateway_source,
                    raw_data=tx_data.get("raw_data", {})
                )
                
                # Filtrage par période
                if period_start <= gateway_tx.processed_at.date() <= period_end:
                    self.gateway_transactions[gateway_source.value].append(gateway_tx)
                    loaded_count += 1
            
            return {
                "status": "success",
                "gateway_source": gateway_source.value,
                "loaded_transactions": loaded_count,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "loaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des transactions gateway: {e}")
            return {"error": str(e)}
    
    async def perform_reconciliation(
        self,
        period_start: date,
        period_end: date,
        auto_resolve: bool = True
    ) -> ReconciliationReport:
        """⚡ Exécution de la réconciliation"""
        
        start_time = time.time()
        
        try:
            logger.info(f"Début réconciliation pour la période {period_start} - {period_end}")
            
            # Filtrage des transactions pour la période
            period_internal = {
                k: v for k, v in self.internal_transactions.items()
                if period_start <= v.processed_at.date() <= period_end
            }
            
            period_gateway = {}
            for source, transactions in self.gateway_transactions.items():
                period_gateway[source] = [
                    tx for tx in transactions
                    if period_start <= tx.processed_at.date() <= period_end
                ]
            
            # Aplatissement des transactions gateway
            all_gateway_transactions = []
            for transactions in period_gateway.values():
                all_gateway_transactions.extend(transactions)
            
            # Processus de matching
            matches = await self._match_transactions(
                list(period_internal.values()),
                all_gateway_transactions
            )
            
            # Analyse des discordances
            discrepancies = await self._analyze_discrepancies(matches)
            
            # Résolution automatique si activée
            if auto_resolve:
                await self._auto_resolve_discrepancies(matches)
            
            # Calcul des métriques
            matched_count = len([m for m in matches if m.status == ReconciliationStatus.MATCHED])
            discrepancy_count = len([m for m in matches if m.discrepancies])
            
            unmatched_internal = len(period_internal) - len(matches)
            unmatched_gateway = len(all_gateway_transactions) - len([m for m in matches if m.gateway_transaction])
            
            total_amount = sum(tx.amount for tx in period_internal.values())
            discrepancy_amount = sum(
                sum(Decimal(str(d.get('amount_difference', 0))) for d in m.discrepancies)
                for m in matches if m.discrepancies
            )
            
            reconciliation_rate = (matched_count / len(period_internal) * 100) if period_internal else 100
            
            # Génération du rapport
            report = ReconciliationReport(
                report_id=f"recon_{uuid.uuid4().hex[:12]}",
                period_start=period_start,
                period_end=period_end,
                total_internal_transactions=len(period_internal),
                total_gateway_transactions=len(all_gateway_transactions),
                matched_transactions=matched_count,
                discrepancies_found=discrepancy_count,
                unmatched_internal=unmatched_internal,
                unmatched_gateway=unmatched_gateway,
                total_amount_reconciled=total_amount,
                total_discrepancy_amount=discrepancy_amount,
                reconciliation_rate=round(reconciliation_rate, 2),
                processing_time_seconds=round(time.time() - start_time, 2)
            )
            
            self.reconciliation_reports.append(report)
            
            logger.info(f"Réconciliation terminée: {matched_count}/{len(period_internal)} transactions matchées")
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la réconciliation: {e}")
            raise
    
    async def _match_transactions(
        self,
        internal_transactions: List[InternalTransaction],
        gateway_transactions: List[GatewayTransaction]
    ) -> List[ReconciliationMatch]:
        """🎯 Matching des transactions"""
        
        matches = []
        used_gateway_transactions = set()
        
        for internal_tx in internal_transactions:
            best_match = None
            best_confidence = 0.0
            best_criteria = []
            
            # Recherche du meilleur match
            for gateway_tx in gateway_transactions:
                if gateway_tx.gateway_transaction_id in used_gateway_transactions:
                    continue
                
                confidence, criteria = self.ml_engine.calculate_match_confidence(
                    internal_tx, gateway_tx
                )
                
                if confidence > best_confidence:
                    best_match = gateway_tx
                    best_confidence = confidence
                    best_criteria = criteria
            
            # Création du match
            match_id = f"match_{uuid.uuid4().hex[:8]}"
            
            if best_match and best_confidence >= 0.5:  # Seuil minimum de confiance
                # Match trouvé
                match = ReconciliationMatch(
                    match_id=match_id,
                    internal_transaction=internal_tx,
                    gateway_transaction=best_match,
                    match_confidence=best_confidence,
                    match_criteria=best_criteria,
                    status=ReconciliationStatus.MATCHED if best_confidence >= 0.9 else ReconciliationStatus.PENDING
                )
                
                used_gateway_transactions.add(best_match.gateway_transaction_id)
                
            else:
                # Pas de match trouvé
                match = ReconciliationMatch(
                    match_id=match_id,
                    internal_transaction=internal_tx,
                    gateway_transaction=None,
                    match_confidence=0.0,
                    match_criteria=[],
                    status=ReconciliationStatus.DISCREPANCY
                )
                
                match.discrepancies.append({
                    "type": DiscrepancyType.MISSING_GATEWAY.value,
                    "description": "No matching gateway transaction found",
                    "internal_transaction_id": internal_tx.internal_id,
                    "severity": "medium"
                })
            
            matches.append(match)
            self.reconciliation_matches[match_id] = match
        
        return matches
    
    async def _analyze_discrepancies(self, matches: List[ReconciliationMatch]) -> List[Dict[str, Any]]:
        """🔍 Analyse des discordances"""
        
        discrepancies = []
        
        for match in matches:
            if not match.gateway_transaction:
                continue  # Déjà traité dans le matching
            
            internal_tx = match.internal_transaction
            gateway_tx = match.gateway_transaction
            
            # Vérification montant
            amount_diff = abs(internal_tx.amount - gateway_tx.amount)
            tolerance = self.discrepancy_rules["amount_tolerance"]
            
            if (amount_diff > tolerance["absolute"] and 
                amount_diff / internal_tx.amount > tolerance["percentage"]):
                
                discrepancy = {
                    "type": DiscrepancyType.AMOUNT_MISMATCH.value,
                    "description": f"Amount mismatch: Internal {internal_tx.amount} vs Gateway {gateway_tx.amount}",
                    "amount_difference": float(amount_diff),
                    "internal_amount": float(internal_tx.amount),
                    "gateway_amount": float(gateway_tx.amount),
                    "severity": "high" if amount_diff > Decimal('100') else "medium"
                }
                
                match.discrepancies.append(discrepancy)
                match.status = ReconciliationStatus.DISCREPANCY
                discrepancies.append(discrepancy)
            
            # Vérification timing
            time_diff = abs((internal_tx.processed_at - gateway_tx.processed_at).total_seconds())
            if time_diff > self.discrepancy_rules["timing_tolerance"]["seconds"]:
                
                discrepancy = {
                    "type": DiscrepancyType.TIMING_DIFFERENCE.value,
                    "description": f"Timing difference: {time_diff} seconds",
                    "time_difference_seconds": time_diff,
                    "internal_time": internal_tx.processed_at.isoformat(),
                    "gateway_time": gateway_tx.processed_at.isoformat(),
                    "severity": "low"
                }
                
                match.discrepancies.append(discrepancy)
                discrepancies.append(discrepancy)
            
            # Vérification frais
            fee_diff = abs(internal_tx.fee_amount - gateway_tx.fee_amount)
            fee_tolerance = self.discrepancy_rules["fee_tolerance"]["percentage"]
            
            if (gateway_tx.fee_amount > 0 and 
                fee_diff / gateway_tx.fee_amount > fee_tolerance):
                
                discrepancy = {
                    "type": DiscrepancyType.FEE_DISCREPANCY.value,
                    "description": f"Fee mismatch: Internal {internal_tx.fee_amount} vs Gateway {gateway_tx.fee_amount}",
                    "fee_difference": float(fee_diff),
                    "internal_fee": float(internal_tx.fee_amount),
                    "gateway_fee": float(gateway_tx.fee_amount),
                    "severity": "low"
                }
                
                match.discrepancies.append(discrepancy)
                discrepancies.append(discrepancy)
            
            # Vérification devise
            if internal_tx.currency != gateway_tx.currency:
                discrepancy = {
                    "type": DiscrepancyType.CURRENCY_MISMATCH.value,
                    "description": f"Currency mismatch: Internal {internal_tx.currency} vs Gateway {gateway_tx.currency}",
                    "internal_currency": internal_tx.currency,
                    "gateway_currency": gateway_tx.currency,
                    "severity": "high"
                }
                
                match.discrepancies.append(discrepancy)
                match.status = ReconciliationStatus.DISCREPANCY
                discrepancies.append(discrepancy)
            
            # Vérification statut
            if internal_tx.status != gateway_tx.status:
                discrepancy = {
                    "type": DiscrepancyType.STATUS_MISMATCH.value,
                    "description": f"Status mismatch: Internal {internal_tx.status} vs Gateway {gateway_tx.status}",
                    "internal_status": internal_tx.status,
                    "gateway_status": gateway_tx.status,
                    "severity": "medium"
                }
                
                match.discrepancies.append(discrepancy)
                discrepancies.append(discrepancy)
        
        return discrepancies
    
    async def _auto_resolve_discrepancies(self, matches: List[ReconciliationMatch]):
        """🤖 Résolution automatique des discordances"""
        
        auto_resolve_rules = self.discrepancy_rules["auto_resolve_thresholds"]
        
        for match in matches:
            if (match.status == ReconciliationStatus.DISCREPANCY and 
                match.match_confidence >= auto_resolve_rules["min_confidence"]):
                
                # Vérification si toutes les discordances sont mineures
                minor_discrepancies = True
                total_amount_diff = Decimal('0')
                
                for discrepancy in match.discrepancies:
                    if discrepancy.get("severity") == "high":
                        minor_discrepancies = False
                        break
                    
                    amount_diff = discrepancy.get("amount_difference", 0)
                    total_amount_diff += Decimal(str(amount_diff))
                
                # Résolution automatique si conditions remplies
                if (minor_discrepancies and 
                    total_amount_diff <= auto_resolve_rules["max_amount"]):
                    
                    match.status = ReconciliationStatus.RESOLVED
                    match.resolved_at = datetime.utcnow()
                    
                    # Ajout d'une note de résolution automatique
                    for discrepancy in match.discrepancies:
                        discrepancy["auto_resolved"] = True
                        discrepancy["resolution_reason"] = "Automatic resolution - minor discrepancy"
                    
                    logger.info(f"Auto-resolved match {match.match_id}")
    
    async def generate_discrepancy_report(
        self,
        period_start: date,
        period_end: date,
        severity_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """📋 Génération rapport de discordances"""
        
        try:
            # Filtrage des matches de la période
            period_matches = [
                match for match in self.reconciliation_matches.values()
                if (period_start <= match.internal_transaction.processed_at.date() <= period_end)
            ]
            
            # Filtrage par sévérité si spécifiée
            discrepancy_matches = [
                match for match in period_matches 
                if match.discrepancies
            ]
            
            if severity_filter:
                discrepancy_matches = [
                    match for match in discrepancy_matches
                    if any(d.get("severity") == severity_filter for d in match.discrepancies)
                ]
            
            # Groupement par type de discordance
            discrepancies_by_type = defaultdict(list)
            total_discrepancy_amount = Decimal('0')
            
            for match in discrepancy_matches:
                for discrepancy in match.discrepancies:
                    discrepancy_type = discrepancy["type"]
                    discrepancies_by_type[discrepancy_type].append({
                        "match_id": match.match_id,
                        "internal_transaction_id": match.internal_transaction.internal_id,
                        "gateway_transaction_id": match.gateway_transaction.gateway_transaction_id if match.gateway_transaction else None,
                        "discrepancy": discrepancy
                    })
                    
                    # Accumulation du montant de discordance
                    amount_diff = discrepancy.get("amount_difference", 0)
                    total_discrepancy_amount += Decimal(str(amount_diff))
            
            # Statistiques par type
            type_statistics = {}
            for disc_type, discrepancies in discrepancies_by_type.items():
                type_statistics[disc_type] = {
                    "count": len(discrepancies),
                    "percentage": round(len(discrepancies) / len(discrepancy_matches) * 100, 2) if discrepancy_matches else 0,
                    "total_amount": float(sum(
                        Decimal(str(d["discrepancy"].get("amount_difference", 0))) 
                        for d in discrepancies
                    ))
                }
            
            # Top discordances par montant
            top_discrepancies = []
            for match in discrepancy_matches:
                for discrepancy in match.discrepancies:
                    if "amount_difference" in discrepancy:
                        top_discrepancies.append({
                            "match_id": match.match_id,
                            "amount_difference": discrepancy["amount_difference"],
                            "type": discrepancy["type"],
                            "description": discrepancy["description"]
                        })
            
            top_discrepancies.sort(key=lambda x: x["amount_difference"], reverse=True)
            top_discrepancies = top_discrepancies[:10]  # Top 10
            
            return {
                "report_id": f"disc_report_{uuid.uuid4().hex[:8]}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "severity_filter": severity_filter,
                "summary": {
                    "total_matches_analyzed": len(period_matches),
                    "matches_with_discrepancies": len(discrepancy_matches),
                    "discrepancy_rate": round(len(discrepancy_matches) / len(period_matches) * 100, 2) if period_matches else 0,
                    "total_discrepancy_amount": float(total_discrepancy_amount)
                },
                "discrepancies_by_type": dict(discrepancies_by_type),
                "type_statistics": type_statistics,
                "top_discrepancies_by_amount": top_discrepancies,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport de discordances: {e}")
            return {"error": str(e)}
    
    async def resolve_discrepancy(
        self,
        match_id: str,
        resolution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔧 Résolution manuelle d'une discordance"""
        
        try:
            match = self.reconciliation_matches.get(match_id)
            if not match:
                raise ValueError(f"Match {match_id} not found")
            
            resolution_type = resolution_data.get("resolution_type")
            resolution_reason = resolution_data.get("reason", "Manual resolution")
            resolved_by = resolution_data.get("resolved_by", "system")
            
            if resolution_type == "accept_internal":
                # Accepter la version interne comme correcte
                match.status = ReconciliationStatus.RESOLVED
                
                for discrepancy in match.discrepancies:
                    discrepancy["resolution"] = "Accepted internal transaction as correct"
                    discrepancy["resolved_by"] = resolved_by
                    discrepancy["resolved_at"] = datetime.utcnow().isoformat()
            
            elif resolution_type == "accept_gateway":
                # Accepter la version gateway comme correcte
                match.status = ReconciliationStatus.RESOLVED
                
                for discrepancy in match.discrepancies:
                    discrepancy["resolution"] = "Accepted gateway transaction as correct"
                    discrepancy["resolved_by"] = resolved_by
                    discrepancy["resolved_at"] = datetime.utcnow().isoformat()
            
            elif resolution_type == "manual_adjustment":
                # Ajustement manuel
                adjustment_amount = Decimal(str(resolution_data.get("adjustment_amount", 0)))
                
                match.status = ReconciliationStatus.RESOLVED
                
                for discrepancy in match.discrepancies:
                    discrepancy["resolution"] = f"Manual adjustment of {adjustment_amount}"
                    discrepancy["adjustment_amount"] = float(adjustment_amount)
                    discrepancy["resolved_by"] = resolved_by
                    discrepancy["resolved_at"] = datetime.utcnow().isoformat()
            
            elif resolution_type == "dispute":
                # Marquer comme en dispute
                match.status = ReconciliationStatus.DISPUTED
                dispute_reason = resolution_data.get("dispute_reason", "Manual dispute")
                
                for discrepancy in match.discrepancies:
                    discrepancy["disputed"] = True
                    discrepancy["dispute_reason"] = dispute_reason
                    discrepancy["disputed_by"] = resolved_by
                    discrepancy["disputed_at"] = datetime.utcnow().isoformat()
            
            else:
                raise ValueError(f"Unknown resolution type: {resolution_type}")
            
            match.resolved_at = datetime.utcnow()
            
            return {
                "match_id": match_id,
                "status": match.status.value,
                "resolution_type": resolution_type,
                "resolved_by": resolved_by,
                "resolved_at": match.resolved_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la résolution de discordance: {e}")
            return {"error": str(e)}
    
    async def detect_anomalies(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """🚨 Détection d'anomalies dans les transactions"""
        
        try:
            # Filtrage des transactions de la période
            period_transactions = [
                tx for tx in self.internal_transactions.values()
                if period_start <= tx.processed_at.date() <= period_end
            ]
            
            # Détection d'anomalies avec ML
            anomalies = self.ml_engine.detect_anomalies(period_transactions)
            
            # Analyse des patterns de réconciliation
            reconciliation_anomalies = await self._detect_reconciliation_patterns(period_transactions)
            
            all_anomalies = anomalies + reconciliation_anomalies
            
            # Groupement par sévérité
            by_severity = defaultdict(list)
            for anomaly in all_anomalies:
                by_severity[anomaly["severity"]].append(anomaly)
            
            return {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_anomalies": len(all_anomalies),
                "by_severity": dict(by_severity),
                "anomalies": all_anomalies,
                "ml_model_version": self.ml_engine.model_version,
                "detected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'anomalies: {e}")
            return {"error": str(e)}
    
    async def _detect_reconciliation_patterns(self, transactions: List[InternalTransaction]) -> List[Dict[str, Any]]:
        """🔍 Détection de patterns de réconciliation suspects"""
        
        anomalies = []
        
        # Analyse des taux de réconciliation par gateway
        gateway_stats = defaultdict(lambda: {"total": 0, "reconciled": 0})
        
        for match in self.reconciliation_matches.values():
            gateway = match.internal_transaction.gateway
            gateway_stats[gateway]["total"] += 1
            
            if match.status in [ReconciliationStatus.MATCHED, ReconciliationStatus.RESOLVED]:
                gateway_stats[gateway]["reconciled"] += 1
        
        # Détection de taux de réconciliation anormalement bas
        for gateway, stats in gateway_stats.items():
            if stats["total"] > 10:  # Seuil minimum de transactions
                reconciliation_rate = stats["reconciled"] / stats["total"]
                
                if reconciliation_rate < 0.8:  # Moins de 80% de réconciliation
                    anomalies.append({
                        "type": "low_reconciliation_rate",
                        "gateway": gateway,
                        "reconciliation_rate": round(reconciliation_rate * 100, 2),
                        "total_transactions": stats["total"],
                        "reconciled_transactions": stats["reconciled"],
                        "severity": "high" if reconciliation_rate < 0.6 else "medium",
                        "description": f"Low reconciliation rate for gateway {gateway}: {reconciliation_rate:.1%}"
                    })
        
        return anomalies
    
    def get_reconciliation_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Statistiques de réconciliation"""
        
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=period_days)
            
            # Filtrage des rapports de la période
            period_reports = [
                report for report in self.reconciliation_reports
                if start_date <= report.period_start <= end_date
            ]
            
            if not period_reports:
                return {
                    "period_days": period_days,
                    "no_data": True,
                    "message": "No reconciliation reports found for the specified period"
                }
            
            # Calculs agrégés
            total_transactions = sum(r.total_internal_transactions for r in period_reports)
            total_matched = sum(r.matched_transactions for r in period_reports)
            total_discrepancies = sum(r.discrepancies_found for r in period_reports)
            total_amount = sum(r.total_amount_reconciled for r in period_reports)
            total_discrepancy_amount = sum(r.total_discrepancy_amount for r in period_reports)
            
            avg_reconciliation_rate = statistics.mean([r.reconciliation_rate for r in period_reports])
            avg_processing_time = statistics.mean([r.processing_time_seconds for r in period_reports])
            
            # Tendances
            latest_report = max(period_reports, key=lambda r: r.generated_at)
            oldest_report = min(period_reports, key=lambda r: r.generated_at)
            
            rate_trend = latest_report.reconciliation_rate - oldest_report.reconciliation_rate
            
            return {
                "period_days": period_days,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "summary": {
                    "total_transactions_processed": total_transactions,
                    "total_matched_transactions": total_matched,
                    "total_discrepancies_found": total_discrepancies,
                    "average_reconciliation_rate": round(avg_reconciliation_rate, 2),
                    "average_processing_time_seconds": round(avg_processing_time, 2)
                },
                "financial_summary": {
                    "total_amount_reconciled": float(total_amount),
                    "total_discrepancy_amount": float(total_discrepancy_amount),
                    "discrepancy_percentage": round((total_discrepancy_amount / total_amount * 100), 4) if total_amount > 0 else 0
                },
                "trends": {
                    "reconciliation_rate_change": round(rate_trend, 2),
                    "trend_direction": "improving" if rate_trend > 0 else "declining" if rate_trend < 0 else "stable"
                },
                "reports_analyzed": len(period_reports),
                "ml_engine_version": self.ml_engine.model_version,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des statistiques: {e}")
            return {"error": str(e)}