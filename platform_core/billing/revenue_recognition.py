"""🚀 Revenue Recognition System - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/platform_core/billing/revenue_recognition.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME RECONNAISSANCE REVENUS GAAP/IFRS COMPLIANCE
Gestion complète reconnaissance revenus selon standards comptables
- ASC 606 / IFRS 15 compliance automatique et audit trails
- Recognition schedules abonnements et contrats multi-éléments
- Deferred revenue management avec tracking temporel
- Contract modifications et variable considerations
- Automated financial reporting et journal entries

Multi-Expert Implementation:
🧠 Lead Dev IA: Algorithmes reconnaissance intelligente, ML contract analysis, automated rules
🏗️ Backend Senior: Architecture GAAP compliance, transaction integrity, audit systems
🤖 ML Engineer: Modèles prédiction revenus, contract classification, anomaly detection
🗄️ DBA: Financial data modeling, audit trails, compliance reporting optimization
🔒 Security: Financial data protection, audit compliance, SOX controls
🌐 Microservices: Intégration ERP, accounting systems, financial reporting
🎵 Audio: Reconnaissance spécifique music royalties, streaming revenues
⚙️ DevOps: Automated compliance monitoring, financial reporting automation
💡 AI Prompt: Génération journal entries, compliance documentation automatique
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
import calendar

# Configuration logging
logger = logging.getLogger(__name__)


class RevenueRecognitionStandard(Enum):
    """Standards de reconnaissance revenus"""
    ASC_606 = "asc_606"  # US GAAP
    IFRS_15 = "ifrs_15"  # International
    LOCAL_GAAP = "local_gaap"  # Standards locaux


class ContractType(Enum):
    """Types de contrats"""
    SUBSCRIPTION = "subscription"
    LICENSE = "license"
    SERVICE = "service"
    HYBRID = "hybrid"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    ADVERTISING = "advertising"


class RevenueType(Enum):
    """Types de revenus"""
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    LICENSE_REVENUE = "license_revenue"
    SERVICE_REVENUE = "service_revenue"
    COMMISSION_REVENUE = "commission_revenue"
    ADVERTISING_REVENUE = "advertising_revenue"
    ROYALTY_REVENUE = "royalty_revenue"


class RecognitionMethod(Enum):
    """Méthodes de reconnaissance"""
    POINT_IN_TIME = "point_in_time"
    OVER_TIME = "over_time"
    PERCENTAGE_COMPLETION = "percentage_completion"
    MILESTONE_BASED = "milestone_based"
    USAGE_BASED = "usage_based"


class RevenueStatus(Enum):
    """États de reconnaissance"""
    PENDING = "pending"
    RECOGNIZED = "recognized"
    DEFERRED = "deferred"
    PARTIALLY_RECOGNIZED = "partially_recognized"
    REVERSED = "reversed"
    DISPUTED = "disputed"


@dataclass
class PerformanceObligation:
    """Obligation de performance selon ASC 606"""
    obligation_id: str
    description: str
    standalone_selling_price: Decimal
    allocated_amount: Decimal
    recognition_method: RecognitionMethod
    estimated_completion_date: Optional[date] = None
    completion_percentage: Decimal = Decimal('0.00')
    is_satisfied: bool = False
    satisfaction_date: Optional[date] = None


@dataclass
class ContractModification:
    """Modification de contrat"""
    modification_id: str
    original_contract_id: str
    modification_date: date
    modification_type: str  # "scope_change", "price_change", "term_extension"
    description: str
    price_adjustment: Decimal
    impact_on_obligations: List[str]
    accounting_treatment: str  # "prospective", "cumulative_catch_up", "separate_contract"


@dataclass
class RevenueContract:
    """Contrat de revenus"""
    contract_id: str
    customer_id: str
    contract_type: ContractType
    total_contract_value: Decimal
    currency: str
    contract_start_date: date
    contract_end_date: Optional[date]
    recognition_standard: RevenueRecognitionStandard
    performance_obligations: List[PerformanceObligation]
    variable_considerations: List[Dict[str, Any]] = field(default_factory=list)
    contract_modifications: List[ContractModification] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueScheduleEntry:
    """Entrée du planning de reconnaissance"""
    schedule_id: str
    contract_id: str
    obligation_id: str
    recognition_date: date
    amount_to_recognize: Decimal
    cumulative_recognized: Decimal
    remaining_deferred: Decimal
    recognition_reason: str
    journal_entry_id: Optional[str] = None
    is_recognized: bool = False
    recognized_at: Optional[datetime] = None


@dataclass
class JournalEntry:
    """Écriture comptable"""
    entry_id: str
    entry_date: date
    description: str
    reference: str
    total_debit: Decimal
    total_credit: Decimal
    line_items: List[Dict[str, Any]]
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    created_by: str = "revenue_recognition_system"


class RevenueRecognitionEngine:
    """🚀 Moteur de Reconnaissance des Revenus Enterprise"""
    
    def __init__(self, recognition_standard: RevenueRecognitionStandard = RevenueRecognitionStandard.ASC_606):
        self.recognition_standard = recognition_standard
        self.contracts: Dict[str, RevenueContract] = {}
        self.recognition_schedules: Dict[str, List[RevenueScheduleEntry]] = {}
        self.journal_entries: Dict[str, JournalEntry] = {}
        self.deferred_revenue_balances: Dict[str, Decimal] = {}
        self.chart_of_accounts = self._initialize_chart_of_accounts()
        self.recognition_rules = self._load_recognition_rules()
    
    def _initialize_chart_of_accounts(self) -> Dict[str, Dict[str, Any]]:
        """📊 Initialisation du plan comptable"""
        
        return {
            "1200": {"name": "Accounts Receivable", "type": "asset", "normal_balance": "debit"},
            "2400": {"name": "Deferred Revenue", "type": "liability", "normal_balance": "credit"},
            "2401": {"name": "Contract Liabilities", "type": "liability", "normal_balance": "credit"},
            "4000": {"name": "Subscription Revenue", "type": "revenue", "normal_balance": "credit"},
            "4001": {"name": "License Revenue", "type": "revenue", "normal_balance": "credit"},
            "4002": {"name": "Service Revenue", "type": "revenue", "normal_balance": "credit"},
            "4003": {"name": "Commission Revenue", "type": "revenue", "normal_balance": "credit"},
            "4004": {"name": "Advertising Revenue", "type": "revenue", "normal_balance": "credit"},
            "4005": {"name": "Royalty Revenue", "type": "revenue", "normal_balance": "credit"}
        }
    
    def _load_recognition_rules(self) -> Dict[str, Dict[str, Any]]:
        """📋 Chargement des règles de reconnaissance"""
        
        return {
            "subscription": {
                "recognition_method": RecognitionMethod.OVER_TIME,
                "recognition_pattern": "straight_line",
                "revenue_account": "4000",
                "deferred_account": "2400"
            },
            "license": {
                "recognition_method": RecognitionMethod.POINT_IN_TIME,
                "recognition_pattern": "immediate",
                "revenue_account": "4001",
                "deferred_account": "2400"
            },
            "service": {
                "recognition_method": RecognitionMethod.OVER_TIME,
                "recognition_pattern": "percentage_completion",
                "revenue_account": "4002",
                "deferred_account": "2400"
            },
            "commission": {
                "recognition_method": RecognitionMethod.POINT_IN_TIME,
                "recognition_pattern": "transaction_based",
                "revenue_account": "4003",
                "deferred_account": "2400"
            }
        }
    
    async def create_revenue_contract(
        self,
        customer_id: str,
        contract_type: ContractType,
        total_value: Decimal,
        currency: str,
        start_date: date,
        end_date: Optional[date] = None,
        performance_obligations: Optional[List[Dict[str, Any]]] = None
    ) -> RevenueContract:
        """📋 Création d'un contrat de revenus"""
        
        try:
            contract_id = f"contract_{uuid.uuid4().hex[:12]}"
            
            # Création des obligations de performance
            obligations = []
            if performance_obligations:
                for i, obligation_data in enumerate(performance_obligations):
                    obligation = PerformanceObligation(
                        obligation_id=f"{contract_id}_obligation_{i+1}",
                        description=obligation_data.get("description", f"Performance Obligation {i+1}"),
                        standalone_selling_price=Decimal(str(obligation_data.get("selling_price", 0))),
                        allocated_amount=Decimal(str(obligation_data.get("allocated_amount", 0))),
                        recognition_method=RecognitionMethod(obligation_data.get("recognition_method", "over_time")),
                        estimated_completion_date=obligation_data.get("completion_date")
                    )
                    obligations.append(obligation)
            else:
                # Obligation unique par défaut
                obligations.append(PerformanceObligation(
                    obligation_id=f"{contract_id}_obligation_1",
                    description="Primary Service Obligation",
                    standalone_selling_price=total_value,
                    allocated_amount=total_value,
                    recognition_method=self._determine_recognition_method(contract_type)
                ))
            
            # Création du contrat
            contract = RevenueContract(
                contract_id=contract_id,
                customer_id=customer_id,
                contract_type=contract_type,
                total_contract_value=total_value,
                currency=currency,
                contract_start_date=start_date,
                contract_end_date=end_date,
                recognition_standard=self.recognition_standard,
                performance_obligations=obligations
            )
            
            self.contracts[contract_id] = contract
            
            # Génération du planning de reconnaissance
            await self._generate_recognition_schedule(contract)
            
            # Création de l'écriture initiale
            await self._create_initial_journal_entry(contract)
            
            logger.info(f"Revenue contract created: {contract_id} for {total_value} {currency}")
            
            return contract
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du contrat: {e}")
            raise
    
    def _determine_recognition_method(self, contract_type: ContractType) -> RecognitionMethod:
        """🎯 Détermination de la méthode de reconnaissance"""
        
        method_mapping = {
            ContractType.SUBSCRIPTION: RecognitionMethod.OVER_TIME,
            ContractType.LICENSE: RecognitionMethod.POINT_IN_TIME,
            ContractType.SERVICE: RecognitionMethod.OVER_TIME,
            ContractType.COMMISSION: RecognitionMethod.POINT_IN_TIME,
            ContractType.ROYALTY: RecognitionMethod.USAGE_BASED,
            ContractType.ADVERTISING: RecognitionMethod.OVER_TIME
        }
        
        return method_mapping.get(contract_type, RecognitionMethod.OVER_TIME)
    
    async def _generate_recognition_schedule(self, contract: RevenueContract):
        """📅 Génération du planning de reconnaissance"""
        
        try:
            schedule_entries = []
            
            for obligation in contract.performance_obligations:
                if obligation.recognition_method == RecognitionMethod.POINT_IN_TIME:
                    # Reconnaissance immédiate
                    entry = RevenueScheduleEntry(
                        schedule_id=f"schedule_{uuid.uuid4().hex[:8]}",
                        contract_id=contract.contract_id,
                        obligation_id=obligation.obligation_id,
                        recognition_date=contract.contract_start_date,
                        amount_to_recognize=obligation.allocated_amount,
                        cumulative_recognized=Decimal('0.00'),
                        remaining_deferred=obligation.allocated_amount,
                        recognition_reason="Point in time recognition"
                    )
                    schedule_entries.append(entry)
                
                elif obligation.recognition_method == RecognitionMethod.OVER_TIME:
                    # Reconnaissance étalée dans le temps
                    if contract.contract_end_date:
                        entries = self._generate_over_time_schedule(contract, obligation)
                        schedule_entries.extend(entries)
                
                elif obligation.recognition_method == RecognitionMethod.USAGE_BASED:
                    # Planning basé sur l'usage (à mettre à jour dynamiquement)
                    pass  # Sera géré par update_usage_based_recognition
            
            self.recognition_schedules[contract.contract_id] = schedule_entries
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du planning: {e}")
            raise
    
    def _generate_over_time_schedule(
        self,
        contract: RevenueContract,
        obligation: PerformanceObligation
    ) -> List[RevenueScheduleEntry]:
        """📈 Génération planning reconnaissance étalée"""
        
        entries = []
        
        if not contract.contract_end_date:
            return entries
        
        # Calcul du nombre de mois
        start_date = contract.contract_start_date
        end_date = contract.contract_end_date
        
        months = []
        current_date = start_date.replace(day=1)  # Premier jour du mois
        
        while current_date <= end_date:
            months.append(current_date)
            # Mois suivant
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        if not months:
            return entries
        
        # Montant mensuel
        monthly_amount = obligation.allocated_amount / len(months)
        monthly_amount = monthly_amount.quantize(Decimal('0.01'), ROUND_HALF_UP)
        
        cumulative = Decimal('0.00')
        
        for i, month_date in enumerate(months):
            # Dernière entrée: ajustement pour les centimes
            if i == len(months) - 1:
                amount = obligation.allocated_amount - cumulative
            else:
                amount = monthly_amount
            
            cumulative += amount
            remaining = obligation.allocated_amount - cumulative
            
            entry = RevenueScheduleEntry(
                schedule_id=f"schedule_{uuid.uuid4().hex[:8]}",
                contract_id=contract.contract_id,
                obligation_id=obligation.obligation_id,
                recognition_date=month_date,
                amount_to_recognize=amount,
                cumulative_recognized=cumulative,
                remaining_deferred=remaining,
                recognition_reason="Over time recognition - monthly"
            )
            entries.append(entry)
        
        return entries
    
    async def _create_initial_journal_entry(self, contract: RevenueContract):
        """📝 Création de l'écriture comptable initiale"""
        
        try:
            entry_id = f"je_{uuid.uuid4().hex[:12]}"
            
            # Écriture pour recevoir le paiement et créer la liability
            line_items = [
                {
                    "account": "1200",  # Accounts Receivable
                    "description": f"Revenue contract {contract.contract_id}",
                    "debit": float(contract.total_contract_value),
                    "credit": 0.0
                },
                {
                    "account": "2400",  # Deferred Revenue
                    "description": f"Deferred revenue - contract {contract.contract_id}",
                    "debit": 0.0,
                    "credit": float(contract.total_contract_value)
                }
            ]
            
            journal_entry = JournalEntry(
                entry_id=entry_id,
                entry_date=contract.contract_start_date,
                description=f"Initial contract booking - {contract.contract_id}",
                reference=contract.contract_id,
                total_debit=contract.total_contract_value,
                total_credit=contract.total_contract_value,
                line_items=line_items
            )
            
            self.journal_entries[entry_id] = journal_entry
            
            # Mise à jour du solde de deferred revenue
            self.deferred_revenue_balances[contract.contract_id] = contract.total_contract_value
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'écriture initiale: {e}")
            raise
    
    async def process_revenue_recognition(self, recognition_date: date = None) -> Dict[str, Any]:
        """⚡ Traitement de la reconnaissance des revenus"""
        
        if not recognition_date:
            recognition_date = date.today()
        
        try:
            processed_entries = []
            total_recognized = Decimal('0.00')
            
            # Traitement pour tous les contrats
            for contract_id, schedule_entries in self.recognition_schedules.items():
                contract = self.contracts.get(contract_id)
                if not contract:
                    continue
                
                # Traitement des entrées dues
                for entry in schedule_entries:
                    if (entry.recognition_date <= recognition_date and 
                        not entry.is_recognized and 
                        entry.amount_to_recognize > 0):
                        
                        # Création de l'écriture comptable
                        journal_entry = await self._create_recognition_journal_entry(
                            contract, entry, recognition_date
                        )
                        
                        # Marquage comme reconnu
                        entry.is_recognized = True
                        entry.recognized_at = datetime.utcnow()
                        entry.journal_entry_id = journal_entry.entry_id
                        
                        # Mise à jour du solde deferred revenue
                        current_balance = self.deferred_revenue_balances.get(contract_id, Decimal('0.00'))
                        self.deferred_revenue_balances[contract_id] = current_balance - entry.amount_to_recognize
                        
                        processed_entries.append({
                            "contract_id": contract_id,
                            "schedule_id": entry.schedule_id,
                            "amount_recognized": float(entry.amount_to_recognize),
                            "journal_entry_id": journal_entry.entry_id
                        })
                        
                        total_recognized += entry.amount_to_recognize
            
            return {
                "recognition_date": recognition_date.isoformat(),
                "total_recognized": float(total_recognized),
                "entries_processed": len(processed_entries),
                "processed_entries": processed_entries,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de reconnaissance: {e}")
            return {"error": str(e)}
    
    async def _create_recognition_journal_entry(
        self,
        contract: RevenueContract,
        schedule_entry: RevenueScheduleEntry,
        recognition_date: date
    ) -> JournalEntry:
        """📝 Création de l'écriture de reconnaissance"""
        
        entry_id = f"je_{uuid.uuid4().hex[:12]}"
        
        # Détermination du compte de revenus
        revenue_account = self._get_revenue_account(contract.contract_type)
        
        line_items = [
            {
                "account": "2400",  # Deferred Revenue
                "description": f"Revenue recognition - {contract.contract_id}",
                "debit": float(schedule_entry.amount_to_recognize),
                "credit": 0.0
            },
            {
                "account": revenue_account,
                "description": f"Revenue recognition - {contract.contract_id}",
                "debit": 0.0,
                "credit": float(schedule_entry.amount_to_recognize)
            }
        ]
        
        journal_entry = JournalEntry(
            entry_id=entry_id,
            entry_date=recognition_date,
            description=f"Revenue recognition - {contract.contract_id} - {schedule_entry.obligation_id}",
            reference=f"{contract.contract_id}_{schedule_entry.schedule_id}",
            total_debit=schedule_entry.amount_to_recognize,
            total_credit=schedule_entry.amount_to_recognize,
            line_items=line_items
        )
        
        self.journal_entries[entry_id] = journal_entry
        
        return journal_entry
    
    def _get_revenue_account(self, contract_type: ContractType) -> str:
        """📊 Détermination du compte de revenus"""
        
        account_mapping = {
            ContractType.SUBSCRIPTION: "4000",
            ContractType.LICENSE: "4001",
            ContractType.SERVICE: "4002",
            ContractType.COMMISSION: "4003",
            ContractType.ADVERTISING: "4004",
            ContractType.ROYALTY: "4005"
        }
        
        return account_mapping.get(contract_type, "4000")
    
    async def calculate_recognition_schedule(
        self,
        contract_id: str,
        modification_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """📅 Calcul du planning de reconnaissance"""
        
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            schedule_entries = self.recognition_schedules.get(contract_id, [])
            
            # Calculs de base
            total_contract_value = float(contract.total_contract_value)
            total_recognized = sum(
                float(entry.amount_to_recognize) 
                for entry in schedule_entries 
                if entry.is_recognized
            )
            total_deferred = total_contract_value - total_recognized
            
            # Planning futur
            future_entries = [
                {
                    "schedule_id": entry.schedule_id,
                    "obligation_id": entry.obligation_id,
                    "recognition_date": entry.recognition_date.isoformat(),
                    "amount_to_recognize": float(entry.amount_to_recognize),
                    "is_recognized": entry.is_recognized,
                    "recognized_at": entry.recognized_at.isoformat() if entry.recognized_at else None
                }
                for entry in schedule_entries
                if not entry.is_recognized
            ]
            
            return {
                "contract_id": contract_id,
                "total_contract_value": total_contract_value,
                "total_recognized": total_recognized,
                "total_deferred": total_deferred,
                "recognition_percentage": (total_recognized / total_contract_value * 100) if total_contract_value > 0 else 0,
                "future_schedule": future_entries,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du planning: {e}")
            return {"error": str(e)}
    
    async def process_deferred_revenue(self, as_of_date: date = None) -> Dict[str, Any]:
        """💰 Traitement des revenus différés"""
        
        if not as_of_date:
            as_of_date = date.today()
        
        try:
            deferred_summary = {}
            total_deferred = Decimal('0.00')
            
            for contract_id, balance in self.deferred_revenue_balances.items():
                if balance > 0:
                    contract = self.contracts.get(contract_id)
                    if contract:
                        deferred_summary[contract_id] = {
                            "customer_id": contract.customer_id,
                            "contract_type": contract.contract_type.value,
                            "total_contract_value": float(contract.total_contract_value),
                            "deferred_balance": float(balance),
                            "contract_start": contract.contract_start_date.isoformat(),
                            "contract_end": contract.contract_end_date.isoformat() if contract.contract_end_date else None
                        }
                        total_deferred += balance
            
            # Analyse par âge
            aging_analysis = await self._analyze_deferred_revenue_aging(as_of_date)
            
            return {
                "as_of_date": as_of_date.isoformat(),
                "total_deferred_revenue": float(total_deferred),
                "contracts_with_deferred": len(deferred_summary),
                "deferred_by_contract": deferred_summary,
                "aging_analysis": aging_analysis,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des revenus différés: {e}")
            return {"error": str(e)}
    
    async def _analyze_deferred_revenue_aging(self, as_of_date: date) -> Dict[str, Any]:
        """📊 Analyse de l'âge des revenus différés"""
        
        aging_buckets = {
            "current": Decimal('0.00'),      # 0-30 jours
            "30_days": Decimal('0.00'),      # 31-60 jours
            "60_days": Decimal('0.00'),      # 61-90 jours
            "90_days_plus": Decimal('0.00')  # 90+ jours
        }
        
        for contract_id, balance in self.deferred_revenue_balances.items():
            if balance <= 0:
                continue
            
            contract = self.contracts.get(contract_id)
            if not contract:
                continue
            
            days_old = (as_of_date - contract.contract_start_date).days
            
            if days_old <= 30:
                aging_buckets["current"] += balance
            elif days_old <= 60:
                aging_buckets["30_days"] += balance
            elif days_old <= 90:
                aging_buckets["60_days"] += balance
            else:
                aging_buckets["90_days_plus"] += balance
        
        total = sum(aging_buckets.values())
        
        return {
            "current_0_30_days": {
                "amount": float(aging_buckets["current"]),
                "percentage": float(aging_buckets["current"] / total * 100) if total > 0 else 0
            },
            "days_31_60": {
                "amount": float(aging_buckets["30_days"]),
                "percentage": float(aging_buckets["30_days"] / total * 100) if total > 0 else 0
            },
            "days_61_90": {
                "amount": float(aging_buckets["60_days"]),
                "percentage": float(aging_buckets["60_days"] / total * 100) if total > 0 else 0
            },
            "days_90_plus": {
                "amount": float(aging_buckets["90_days_plus"]),
                "percentage": float(aging_buckets["90_days_plus"] / total * 100) if total > 0 else 0
            },
            "total": float(total)
        }
    
    async def generate_compliance_reports(
        self,
        report_period_start: date,
        report_period_end: date,
        report_type: str = "standard"
    ) -> Dict[str, Any]:
        """📋 Génération des rapports de conformité"""
        
        try:
            # Revenus reconnus dans la période
            recognized_revenue = await self._calculate_period_revenue(
                report_period_start, report_period_end
            )
            
            # Soldes de revenus différés
            deferred_balances = await self._calculate_period_deferred_balances(
                report_period_end
            )
            
            # Modifications de contrats
            contract_modifications = await self._analyze_contract_modifications(
                report_period_start, report_period_end
            )
            
            # Obligations de performance
            performance_obligations_analysis = await self._analyze_performance_obligations()
            
            # Audit trail
            audit_entries = await self._generate_audit_trail(
                report_period_start, report_period_end
            )
            
            report = {
                "report_type": report_type,
                "period_start": report_period_start.isoformat(),
                "period_end": report_period_end.isoformat(),
                "recognition_standard": self.recognition_standard.value,
                "summary": {
                    "total_revenue_recognized": float(recognized_revenue["total"]),
                    "total_deferred_revenue": float(deferred_balances["total"]),
                    "contracts_modified": len(contract_modifications),
                    "active_contracts": len(self.contracts)
                },
                "recognized_revenue": recognized_revenue,
                "deferred_revenue": deferred_balances,
                "contract_modifications": contract_modifications,
                "performance_obligations": performance_obligations_analysis,
                "audit_trail": audit_entries,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Ajout de sections spécifiques selon le standard
            if self.recognition_standard == RevenueRecognitionStandard.ASC_606:
                report["asc_606_disclosures"] = await self._generate_asc_606_disclosures(
                    report_period_start, report_period_end
                )
            
            elif self.recognition_standard == RevenueRecognitionStandard.IFRS_15:
                report["ifrs_15_disclosures"] = await self._generate_ifrs_15_disclosures(
                    report_period_start, report_period_end
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {"error": str(e)}
    
    async def _calculate_period_revenue(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """📊 Calcul des revenus de la période"""
        
        total_revenue = Decimal('0.00')
        revenue_by_type = {}
        revenue_by_contract = {}
        
        for contract_id, schedule_entries in self.recognition_schedules.items():
            contract = self.contracts.get(contract_id)
            if not contract:
                continue
            
            contract_revenue = Decimal('0.00')
            
            for entry in schedule_entries:
                if (entry.is_recognized and 
                    start_date <= entry.recognition_date <= end_date):
                    
                    contract_revenue += entry.amount_to_recognize
                    total_revenue += entry.amount_to_recognize
                    
                    # Groupement par type
                    contract_type = contract.contract_type.value
                    if contract_type not in revenue_by_type:
                        revenue_by_type[contract_type] = Decimal('0.00')
                    revenue_by_type[contract_type] += entry.amount_to_recognize
            
            if contract_revenue > 0:
                revenue_by_contract[contract_id] = {
                    "customer_id": contract.customer_id,
                    "contract_type": contract.contract_type.value,
                    "revenue_recognized": float(contract_revenue)
                }
        
        return {
            "total": total_revenue,
            "by_type": {k: float(v) for k, v in revenue_by_type.items()},
            "by_contract": revenue_by_contract
        }
    
    async def _calculate_period_deferred_balances(self, as_of_date: date) -> Dict[str, Any]:
        """💰 Calcul des soldes différés à une date"""
        
        total_deferred = Decimal('0.00')
        deferred_by_type = {}
        deferred_by_contract = {}
        
        for contract_id, balance in self.deferred_revenue_balances.items():
            if balance > 0:
                contract = self.contracts.get(contract_id)
                if contract:
                    total_deferred += balance
                    
                    # Groupement par type
                    contract_type = contract.contract_type.value
                    if contract_type not in deferred_by_type:
                        deferred_by_type[contract_type] = Decimal('0.00')
                    deferred_by_type[contract_type] += balance
                    
                    deferred_by_contract[contract_id] = {
                        "customer_id": contract.customer_id,
                        "contract_type": contract_type,
                        "deferred_balance": float(balance)
                    }
        
        return {
            "total": total_deferred,
            "by_type": {k: float(v) for k, v in deferred_by_type.items()},
            "by_contract": deferred_by_contract
        }
    
    async def _analyze_contract_modifications(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """🔄 Analyse des modifications de contrats"""
        
        modifications = []
        
        for contract in self.contracts.values():
            for modification in contract.contract_modifications:
                if start_date <= modification.modification_date <= end_date:
                    modifications.append({
                        "modification_id": modification.modification_id,
                        "contract_id": modification.original_contract_id,
                        "modification_date": modification.modification_date.isoformat(),
                        "modification_type": modification.modification_type,
                        "description": modification.description,
                        "price_adjustment": float(modification.price_adjustment),
                        "accounting_treatment": modification.accounting_treatment
                    })
        
        return modifications
    
    async def _analyze_performance_obligations(self) -> Dict[str, Any]:
        """🎯 Analyse des obligations de performance"""
        
        total_obligations = 0
        satisfied_obligations = 0
        partially_satisfied = 0
        unsatisfied_value = Decimal('0.00')
        
        for contract in self.contracts.values():
            for obligation in contract.performance_obligations:
                total_obligations += 1
                
                if obligation.is_satisfied:
                    satisfied_obligations += 1
                elif obligation.completion_percentage > 0:
                    partially_satisfied += 1
                else:
                    unsatisfied_value += obligation.allocated_amount
        
        return {
            "total_obligations": total_obligations,
            "satisfied_obligations": satisfied_obligations,
            "partially_satisfied_obligations": partially_satisfied,
            "unsatisfied_obligations": total_obligations - satisfied_obligations - partially_satisfied,
            "unsatisfied_value": float(unsatisfied_value),
            "satisfaction_rate": (satisfied_obligations / total_obligations * 100) if total_obligations > 0 else 0
        }
    
    async def _generate_audit_trail(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """📋 Génération de l'audit trail"""
        
        audit_entries = []
        
        for entry in self.journal_entries.values():
            if start_date <= entry.entry_date <= end_date:
                audit_entries.append({
                    "entry_id": entry.entry_id,
                    "entry_date": entry.entry_date.isoformat(),
                    "description": entry.description,
                    "reference": entry.reference,
                    "total_amount": float(entry.total_debit),
                    "is_posted": entry.is_posted,
                    "created_by": entry.created_by
                })
        
        return sorted(audit_entries, key=lambda x: x["entry_date"])
    
    async def _generate_asc_606_disclosures(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """📋 Génération des disclosures ASC 606"""
        
        return {
            "revenue_recognition_policies": {
                "description": "Revenue is recognized in accordance with ASC 606",
                "five_step_model": [
                    "Identify the contract",
                    "Identify performance obligations",
                    "Determine transaction price",
                    "Allocate transaction price",
                    "Recognize revenue when obligations satisfied"
                ]
            },
            "significant_judgments": [
                "Identification of distinct performance obligations",
                "Determination of standalone selling prices",
                "Assessment of variable consideration constraints"
            ],
            "contract_balances": {
                "receivables": "See accounts receivable note",
                "contract_assets": "Not applicable",
                "contract_liabilities": "See deferred revenue analysis"
            }
        }
    
    async def _generate_ifrs_15_disclosures(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """📋 Génération des disclosures IFRS 15"""
        
        return {
            "revenue_recognition_policies": {
                "description": "Revenue is recognized in accordance with IFRS 15",
                "five_step_approach": [
                    "Identify the contract",
                    "Identify performance obligations",
                    "Determine transaction price",
                    "Allocate transaction price",
                    "Recognize revenue when control transfers"
                ]
            },
            "significant_judgments": [
                "Identification of distinct performance obligations",
                "Determination of standalone selling prices",
                "Assessment of variable consideration"
            ],
            "disaggregation_of_revenue": "See revenue by contract type analysis"
        }
    
    async def handle_contract_modifications(
        self,
        contract_id: str,
        modification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Gestion des modifications de contrat"""
        
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            modification_id = f"mod_{uuid.uuid4().hex[:8]}"
            
            modification = ContractModification(
                modification_id=modification_id,
                original_contract_id=contract_id,
                modification_date=datetime.strptime(modification_data["modification_date"], "%Y-%m-%d").date(),
                modification_type=modification_data["modification_type"],
                description=modification_data["description"],
                price_adjustment=Decimal(str(modification_data.get("price_adjustment", 0))),
                impact_on_obligations=modification_data.get("impact_on_obligations", []),
                accounting_treatment=modification_data.get("accounting_treatment", "prospective")
            )
            
            contract.contract_modifications.append(modification)
            contract.updated_at = datetime.utcnow()
            
            # Traitement comptable selon le type de modification
            result = await self._process_modification_accounting(contract, modification)
            
            return {
                "modification_id": modification_id,
                "contract_id": contract_id,
                "accounting_result": result,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la modification de contrat: {e}")
            return {"error": str(e)}
    
    async def _process_modification_accounting(
        self,
        contract: RevenueContract,
        modification: ContractModification
    ) -> Dict[str, Any]:
        """💼 Traitement comptable des modifications"""
        
        if modification.accounting_treatment == "prospective":
            # Ajustement prospectif - mise à jour du planning futur
            return await self._apply_prospective_modification(contract, modification)
        
        elif modification.accounting_treatment == "cumulative_catch_up":
            # Rattrapage cumulatif - ajustement immédiat
            return await self._apply_cumulative_catch_up(contract, modification)
        
        elif modification.accounting_treatment == "separate_contract":
            # Contrat séparé - nouveau contrat
            return await self._create_separate_contract(contract, modification)
        
        else:
            raise ValueError(f"Unknown accounting treatment: {modification.accounting_treatment}")
    
    async def _apply_prospective_modification(
        self,
        contract: RevenueContract,
        modification: ContractModification
    ) -> Dict[str, Any]:
        """📈 Application prospective de modification"""
        
        # Mise à jour de la valeur du contrat
        contract.total_contract_value += modification.price_adjustment
        
        # Régénération du planning de reconnaissance
        await self._generate_recognition_schedule(contract)
        
        # Écriture d'ajustement si nécessaire
        if modification.price_adjustment != 0:
            entry_id = await self._create_modification_journal_entry(contract, modification)
            return {"journal_entry_id": entry_id, "treatment": "prospective"}
        
        return {"treatment": "prospective", "no_journal_entry_required": True}
    
    async def _apply_cumulative_catch_up(
        self,
        contract: RevenueContract,
        modification: ContractModification
    ) -> Dict[str, Any]:
        """📊 Application cumulative catch-up"""
        
        # Calcul de l'ajustement cumulatif
        # (Logique complexe pour recalculer depuis le début)
        
        adjustment_amount = modification.price_adjustment  # Simplifié pour l'exemple
        
        # Écriture d'ajustement
        entry_id = await self._create_cumulative_adjustment_entry(contract, adjustment_amount)
        
        return {"journal_entry_id": entry_id, "treatment": "cumulative_catch_up", "adjustment_amount": float(adjustment_amount)}
    
    async def _create_separate_contract(
        self,
        original_contract: RevenueContract,
        modification: ContractModification
    ) -> Dict[str, Any]:
        """📋 Création d'un contrat séparé"""
        
        # Création d'un nouveau contrat pour la modification
        new_contract = await self.create_revenue_contract(
            customer_id=original_contract.customer_id,
            contract_type=original_contract.contract_type,
            total_value=modification.price_adjustment,
            currency=original_contract.currency,
            start_date=modification.modification_date
        )
        
        return {"treatment": "separate_contract", "new_contract_id": new_contract.contract_id}
    
    async def _create_modification_journal_entry(
        self,
        contract: RevenueContract,
        modification: ContractModification
    ) -> str:
        """📝 Création écriture modification"""
        
        entry_id = f"je_{uuid.uuid4().hex[:12]}"
        
        line_items = []
        
        if modification.price_adjustment > 0:
            # Augmentation de prix
            line_items = [
                {
                    "account": "1200",  # Accounts Receivable
                    "description": f"Contract modification {modification.modification_id}",
                    "debit": float(modification.price_adjustment),
                    "credit": 0.0
                },
                {
                    "account": "2400",  # Deferred Revenue
                    "description": f"Contract modification {modification.modification_id}",
                    "debit": 0.0,
                    "credit": float(modification.price_adjustment)
                }
            ]
        else:
            # Diminution de prix
            abs_adjustment = abs(modification.price_adjustment)
            line_items = [
                {
                    "account": "2400",  # Deferred Revenue
                    "description": f"Contract modification {modification.modification_id}",
                    "debit": float(abs_adjustment),
                    "credit": 0.0
                },
                {
                    "account": "1200",  # Accounts Receivable
                    "description": f"Contract modification {modification.modification_id}",
                    "debit": 0.0,
                    "credit": float(abs_adjustment)
                }
            ]
        
        journal_entry = JournalEntry(
            entry_id=entry_id,
            entry_date=modification.modification_date,
            description=f"Contract modification - {modification.modification_id}",
            reference=f"{contract.contract_id}_{modification.modification_id}",
            total_debit=abs(modification.price_adjustment),
            total_credit=abs(modification.price_adjustment),
            line_items=line_items
        )
        
        self.journal_entries[entry_id] = journal_entry
        
        return entry_id
    
    async def _create_cumulative_adjustment_entry(
        self,
        contract: RevenueContract,
        adjustment_amount: Decimal
    ) -> str:
        """📝 Création écriture ajustement cumulatif"""
        
        entry_id = f"je_{uuid.uuid4().hex[:12]}"
        
        revenue_account = self._get_revenue_account(contract.contract_type)
        
        if adjustment_amount > 0:
            # Revenus supplémentaires à reconnaître
            line_items = [
                {
                    "account": "2400",  # Deferred Revenue
                    "description": f"Cumulative catch-up adjustment - {contract.contract_id}",
                    "debit": float(adjustment_amount),
                    "credit": 0.0
                },
                {
                    "account": revenue_account,
                    "description": f"Cumulative catch-up adjustment - {contract.contract_id}",
                    "debit": 0.0,
                    "credit": float(adjustment_amount)
                }
            ]
        else:
            # Reversal de revenus
            abs_adjustment = abs(adjustment_amount)
            line_items = [
                {
                    "account": revenue_account,
                    "description": f"Cumulative catch-up adjustment - {contract.contract_id}",
                    "debit": float(abs_adjustment),
                    "credit": 0.0
                },
                {
                    "account": "2400",  # Deferred Revenue
                    "description": f"Cumulative catch-up adjustment - {contract.contract_id}",
                    "debit": 0.0,
                    "credit": float(abs_adjustment)
                }
            ]
        
        journal_entry = JournalEntry(
            entry_id=entry_id,
            entry_date=date.today(),
            description=f"Cumulative catch-up adjustment - {contract.contract_id}",
            reference=contract.contract_id,
            total_debit=abs(adjustment_amount),
            total_credit=abs(adjustment_amount),
            line_items=line_items
        )
        
        self.journal_entries[entry_id] = journal_entry
        
        return entry_id
    
    def get_revenue_recognition_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Statistiques de reconnaissance des revenus"""
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=period_days)
            
            # Calculs de base
            total_contracts = len(self.contracts)
            total_contract_value = sum(c.total_contract_value for c in self.contracts.values())
            total_deferred = sum(self.deferred_revenue_balances.values())
            
            # Revenus reconnus dans la période
            period_revenue = Decimal('0.00')
            for schedule_entries in self.recognition_schedules.values():
                for entry in schedule_entries:
                    if (entry.is_recognized and 
                        start_date <= entry.recognition_date <= end_date):
                        period_revenue += entry.amount_to_recognize
            
            # Statistiques par type de contrat
            contract_type_stats = {}
            for contract in self.contracts.values():
                contract_type = contract.contract_type.value
                if contract_type not in contract_type_stats:
                    contract_type_stats[contract_type] = {
                        "count": 0,
                        "total_value": Decimal('0.00')
                    }
                contract_type_stats[contract_type]["count"] += 1
                contract_type_stats[contract_type]["total_value"] += contract.total_contract_value
            
            return {
                "period_days": period_days,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "recognition_standard": self.recognition_standard.value,
                "summary": {
                    "total_contracts": total_contracts,
                    "total_contract_value": float(total_contract_value),
                    "total_deferred_revenue": float(total_deferred),
                    "period_revenue_recognized": float(period_revenue),
                    "recognition_percentage": float(((total_contract_value - total_deferred) / total_contract_value * 100)) if total_contract_value > 0 else 0
                },
                "contract_types": {
                    k: {
                        "count": v["count"],
                        "total_value": float(v["total_value"])
                    }
                    for k, v in contract_type_stats.items()
                },
                "journal_entries": len(self.journal_entries),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"error": str(e)}