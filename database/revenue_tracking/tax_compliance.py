"""Tax Compliance & Calculation System

Système avancé de conformité fiscale et calcul automatisé des taxes
pour la plateforme IA Influencer Agent avec support multi-juridictions.

Architecture: Multi-jurisdiction tax compliance with automated reporting
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe Projet: Lead AI Developer + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code et concept sont la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Violation = Poursuites judiciaires selon le droit allemand et international.
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
import logging
from dataclasses import dataclass, field
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.security import EncryptionService
from ...utils.financial import CurrencyConverter
from ...utils.validation import ValidationService
from ...core.cache import CacheManager
from ...core.events import EventEmitter

logger = logging.getLogger(__name__)

Base = declarative_base()


class TaxJurisdiction(Enum):
    """Juridictions fiscales supportées"""    GERMANY = "DE"
    FRANCE = "FR"
    UNITED_STATES = "US"
    UNITED_KINGDOM = "GB"
    CANADA = "CA"
    AUSTRALIA = "AU"
    NETHERLANDS = "NL"
    SWEDEN = "SE"
    NORWAY = "NO"
    DENMARK = "DK"
    SWITZERLAND = "CH"
    AUSTRIA = "AT"
    BELGIUM = "BE"
    ITALY = "IT"
    SPAIN = "ES"
    PORTUGAL = "PT"
    POLAND = "PL"
    CZECH_REPUBLIC = "CZ"
    SLOVAKIA = "SK"
    HUNGARY = "HU"
    ESTONIA = "EE"
    LATVIA = "LV"
    LITHUANIA = "LT"
    FINLAND = "FI"
    IRELAND = "IE"
    LUXEMBOURG = "LU"
    MALTA = "MT"
    CYPRUS = "CY"
    SLOVENIA = "SI"
    CROATIA = "HR"
    BULGARIA = "BG"
    ROMANIA = "RO"


class TaxType(Enum):
    """Types de taxes"""    INCOME_TAX = "income_tax"
    VAT = "vat"
    WITHHOLDING_TAX = "withholding_tax"
    CORPORATE_TAX = "corporate_tax"
    CAPITAL_GAINS_TAX = "capital_gains_tax"
    SOCIAL_SECURITY = "social_security"
    SALES_TAX = "sales_tax"
    DIGITAL_SERVICES_TAX = "digital_services_tax"
    ARTIST_TAX = "artist_tax"
    ROYALTY_TAX = "royalty_tax"


class TaxStatus(Enum):
    """Status des calculs fiscaux"""    CALCULATED = "calculated"
    REVIEWED = "reviewed"
    FILED = "filed"
    PAID = "paid"
    DISPUTED = "disputed"
    AMENDED = "amended"


@dataclass
class TaxJurisdictionRuleModel(BaseModel, TimestampMixin):
    """    Modèle des règles fiscales par juridiction
    """    __tablename__ = "tax_jurisdiction_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jurisdiction_code = Column(String(5), nullable=False, index=True)
    jurisdiction_name = Column(String(255), nullable=False)
    
    # Règles fiscales de base
    income_tax_rate = Column(Numeric(5, 4), nullable=True)
    vat_rate = Column(Numeric(5, 4), nullable=True)
    withholding_tax_rate = Column(Numeric(5, 4), nullable=True)
    
    # Seuils et exemptions
    tax_free_threshold = Column(Numeric(15, 4), nullable=True)
    minimum_withholding_amount = Column(Numeric(15, 4), nullable=True)
    digital_services_threshold = Column(Numeric(15, 4), nullable=True)
    
    # Règles spécifiques aux créateurs
    artist_tax_exemption = Column(Boolean, nullable=False, default=False)
    royalty_tax_rate = Column(Numeric(5, 4), nullable=True)
    streaming_revenue_rate = Column(Numeric(5, 4), nullable=True)
    
    # Métadonnées de calcul
    calculation_rules = Column(JSONB, nullable=True)
    reporting_requirements = Column(JSONB, nullable=True)
    filing_deadlines = Column(JSONB, nullable=True)
    
    # Validité
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relations
    tax_calculations = relationship("TaxCalculationModel", back_populates="jurisdiction_rule")


@dataclass
class TaxCalculationModel(BaseModel, TimestampMixin):
    """    Modèle des calculs fiscaux
    """    __tablename__ = "tax_calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants liés
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    jurisdiction_rule_id = Column(UUID(as_uuid=True), ForeignKey("tax_jurisdiction_rules.id"), nullable=False)
    
    # Détails du calcul
    gross_amount = Column(Numeric(15, 4), nullable=False)
    taxable_amount = Column(Numeric(15, 4), nullable=False)
    tax_exemption_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Calculs par type de taxe
    income_tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    vat_amount = Column(Numeric(15, 4), nullable=False, default=0)
    withholding_tax_amount = Column(Numeric(15, 4), nullable=False, default=0)
    social_security_amount = Column(Numeric(15, 4), nullable=False, default=0)
    other_taxes_amount = Column(Numeric(15, 4), nullable=False, default=0)
    
    total_tax_amount = Column(Numeric(15, 4), nullable=False)
    net_amount_after_tax = Column(Numeric(15, 4), nullable=False)
    
    # Métadonnées
    tax_year = Column(Integer, nullable=False)
    tax_period = Column(String(20), nullable=False)  # quarterly, annually, etc.
    jurisdiction_code = Column(String(5), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Status et dates
    calculation_status = Column(String(20), nullable=False, default="calculated")
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    review_date = Column(DateTime, nullable=True)
    filing_date = Column(DateTime, nullable=True)
    payment_due_date = Column(DateTime, nullable=True)
    
    # Détails de calcul
    calculation_breakdown = Column(JSONB, nullable=True)
    applied_exemptions = Column(JSONB, nullable=True)
    deductions_applied = Column(JSONB, nullable=True)
    
    # Audit et compliance
    audit_trail = Column(JSONB, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Relations
    jurisdiction_rule = relationship("TaxJurisdictionRuleModel", back_populates="tax_calculations")


@dataclass
class TaxReportModel(BaseModel, TimestampMixin):
    """    Modèle des rapports fiscaux
    """    __tablename__ = "tax_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    jurisdiction_code = Column(String(5), nullable=False)
    
    # Période du rapport
    tax_year = Column(Integer, nullable=False)
    reporting_period = Column(String(20), nullable=False)
    period_start_date = Column(DateTime, nullable=False)
    period_end_date = Column(DateTime, nullable=False)
    
    # Totaux du rapport
    total_gross_revenue = Column(Numeric(15, 4), nullable=False)
    total_taxable_amount = Column(Numeric(15, 4), nullable=False)
    total_tax_liability = Column(Numeric(15, 4), nullable=False)
    total_taxes_paid = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Détails par type de revenus
    streaming_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    licensing_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    merchandise_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    collaboration_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Données détaillées
    revenue_breakdown = Column(JSONB, nullable=True)
    tax_calculations_summary = Column(JSONB, nullable=True)
    deductions_summary = Column(JSONB, nullable=True)
    
    # Status du rapport
    report_status = Column(String(20), nullable=False, default="draft")
    generated_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    submitted_date = Column(DateTime, nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Fichiers associés
    report_file_path = Column(String(500), nullable=True)
    supporting_documents = Column(JSONB, nullable=True)


class TaxCalculationEngine:
    """    Moteur de calcul fiscal avancé
    """    
    def __init__(self, db_session: Session, cache_manager: CacheManager):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.currency_converter = CurrencyConverter()
        self.event_emitter = EventEmitter()
        
        # Cache des règles fiscales par juridiction
        self._jurisdiction_rules_cache = {}
        
    async def calculate_taxes(
        self,
        revenue_record_id: uuid.UUID,
        user_id: uuid.UUID,
        jurisdiction_code: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> TaxCalculationModel:
        """        Calcule les taxes pour un enregistrement de revenus
        """        try:
            # Récupération des données de base
            revenue_record = await self._get_revenue_record(revenue_record_id)
            user_profile = await self._get_user_tax_profile(user_id)
            jurisdiction_rule = await self._get_jurisdiction_rule(jurisdiction_code)
            
            # Calcul du montant imposable
            taxable_amount = await self._calculate_taxable_amount(
                revenue_record, user_profile, jurisdiction_rule
            )
            
            # Calcul des différents types de taxes
            income_tax = await self._calculate_income_tax(
                taxable_amount, user_profile, jurisdiction_rule
            )
            
            vat_amount = await self._calculate_vat(
                revenue_record, jurisdiction_rule
            )
            
            withholding_tax = await self._calculate_withholding_tax(
                revenue_record, user_profile, jurisdiction_rule
            )
            
            social_security = await self._calculate_social_security(
                taxable_amount, user_profile, jurisdiction_rule
            )
            
            # Total des taxes
            total_tax = income_tax + vat_amount + withholding_tax + social_security
            net_amount = revenue_record.amount_net - total_tax
            
            # Création de l'enregistrement de calcul
            tax_calculation = TaxCalculationModel(
                calculation_id=f"TAX_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
                revenue_record_id=revenue_record_id,
                user_id=user_id,
                jurisdiction_rule_id=jurisdiction_rule.id,
                gross_amount=revenue_record.amount_gross,
                taxable_amount=taxable_amount,
                income_tax_amount=income_tax,
                vat_amount=vat_amount,
                withholding_tax_amount=withholding_tax,
                social_security_amount=social_security,
                total_tax_amount=total_tax,
                net_amount_after_tax=net_amount,
                tax_year=datetime.utcnow().year,
                tax_period="quarterly",
                jurisdiction_code=jurisdiction_code,
                currency=revenue_record.currency,
                calculation_breakdown={
                    "base_calculations": {
                        "gross_amount": float(revenue_record.amount_gross),
                        "deductions": float(revenue_record.amount_gross - taxable_amount),
                        "taxable_base": float(taxable_amount)
                    },
                    "tax_rates_applied": {
                        "income_tax_rate": float(jurisdiction_rule.income_tax_rate or 0),
                        "vat_rate": float(jurisdiction_rule.vat_rate or 0),
                        "withholding_rate": float(jurisdiction_rule.withholding_tax_rate or 0)
                    },
                    "exemptions_applied": await self._get_applied_exemptions(user_profile, jurisdiction_rule),
                    "calculation_method": "ai_optimized_multi_jurisdiction"
                }
            )
            
            # Sauvegarde
            self.db_session.add(tax_calculation)
            await self.db_session.commit()
            
            # Émission d'événement
            await self.event_emitter.emit("tax_calculated", {
                "calculation_id": tax_calculation.calculation_id,
                "user_id": str(user_id),
                "total_tax": float(total_tax),
                "jurisdiction": jurisdiction_code
            })
            
            logger.info(f"Tax calculation completed: {tax_calculation.calculation_id}")
            return tax_calculation
            
        except Exception as e:
            logger.error(f"Tax calculation failed: {e}")
            await self.db_session.rollback()
            raise
    
    async def _calculate_taxable_amount(
        self,
        revenue_record,
        user_profile,
        jurisdiction_rule: TaxJurisdictionRuleModel
    ) -> Decimal:
        """        Calcule le montant imposable après déductions
        """        gross_amount = revenue_record.amount_net
        
        # Exemptions de base
        tax_free_threshold = jurisdiction_rule.tax_free_threshold or Decimal('0')
        if gross_amount <= tax_free_threshold:
            return Decimal('0')
        
        # Déductions pour les artistes
        artist_deductions = Decimal('0')
        if user_profile.get('is_artist', False) and jurisdiction_rule.artist_tax_exemption:
            # Déduction spéciale pour les artistes (par exemple 30% en Allemagne)
            artist_deductions = gross_amount * Decimal('0.30')
        
        # Déductions pour frais professionnels
        business_expenses = user_profile.get('business_expenses', Decimal('0'))
        
        # Déductions pour équipement
        equipment_depreciation = user_profile.get('equipment_depreciation', Decimal('0'))
        
        total_deductions = artist_deductions + business_expenses + equipment_depreciation
        taxable_amount = max(gross_amount - total_deductions, Decimal('0'))
        
        return taxable_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_income_tax(
        self,
        taxable_amount: Decimal,
        user_profile: Dict[str, Any],
        jurisdiction_rule: TaxJurisdictionRuleModel
    ) -> Decimal:
        """        Calcule l'impôt sur le revenu
        """        if not jurisdiction_rule.income_tax_rate or taxable_amount <= 0:
            return Decimal('0')
        
        # Système progressif pour certaines juridictions
        if jurisdiction_rule.jurisdiction_code in ['DE', 'FR', 'US']:
            return await self._calculate_progressive_income_tax(
                taxable_amount, jurisdiction_rule.jurisdiction_code
            )
        
        # Taux fixe
        income_tax = taxable_amount * jurisdiction_rule.income_tax_rate / 100
        return income_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_progressive_income_tax(
        self,
        taxable_amount: Decimal,
        jurisdiction_code: str
    ) -> Decimal:
        """        Calcule l'impôt progressif selon la juridiction
        """        # Barèmes progressifs (exemple pour l'Allemagne)
        if jurisdiction_code == 'DE':
            brackets = [
                (Decimal('10347'), Decimal('0')),      # Tranche 0%
                (Decimal('14926'), Decimal('14')),     # Tranche 14%
                (Decimal('58596'), Decimal('24')),     # Tranche 24%
                (Decimal('277825'), Decimal('42')),    # Tranche 42%
                (float('inf'), Decimal('45'))          # Tranche 45%
            ]
        elif jurisdiction_code == 'FR':
            brackets = [
                (Decimal('10777'), Decimal('0')),      # Tranche 0%
                (Decimal('27478'), Decimal('11')),     # Tranche 11%
                (Decimal('78570'), Decimal('30')),     # Tranche 30%
                (Decimal('168994'), Decimal('41')),    # Tranche 41%
                (float('inf'), Decimal('45'))          # Tranche 45%
            ]
        else:
            # Par défaut, taux fixe
            return taxable_amount * Decimal('20') / 100
        
        total_tax = Decimal('0')
        remaining_amount = taxable_amount
        previous_threshold = Decimal('0')
        
        for threshold, rate in brackets:
            if remaining_amount <= 0:
                break
                
            bracket_amount = min(remaining_amount, Decimal(str(threshold)) - previous_threshold)
            bracket_tax = bracket_amount * rate / 100
            total_tax += bracket_tax
            
            remaining_amount -= bracket_amount
            previous_threshold = Decimal(str(threshold))
        
        return total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_vat(
        self,
        revenue_record,
        jurisdiction_rule: TaxJurisdictionRuleModel
    ) -> Decimal:
        """        Calcule la TVA
        """        if not jurisdiction_rule.vat_rate:
            return Decimal('0')
        
        # La TVA s'applique sur le montant brut
        vat_amount = revenue_record.amount_gross * jurisdiction_rule.vat_rate / 100
        return vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_withholding_tax(
        self,
        revenue_record,
        user_profile: Dict[str, Any],
        jurisdiction_rule: TaxJurisdictionRuleModel
    ) -> Decimal:
        """        Calcule la retenue à la source
        """        if not jurisdiction_rule.withholding_tax_rate:
            return Decimal('0')
        
        # Vérification du seuil minimum
        if (jurisdiction_rule.minimum_withholding_amount and 
            revenue_record.amount_net < jurisdiction_rule.minimum_withholding_amount):
            return Decimal('0')
        
        # Exemptions pour résidents
        if user_profile.get('tax_residency') == jurisdiction_rule.jurisdiction_code:
            return Decimal('0')
        
        withholding_tax = revenue_record.amount_net * jurisdiction_rule.withholding_tax_rate / 100
        return withholding_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class TaxReportingEngine:
    """    Moteur de génération de rapports fiscaux
    """    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.event_emitter = EventEmitter()
    
    async def generate_tax_report(
        self,
        user_id: uuid.UUID,
        jurisdiction_code: str,
        tax_year: int,
        reporting_period: str = "annual"
    ) -> TaxReportModel:
        """        Génère un rapport fiscal complet
        """        try:
            # Définition de la période
            period_start, period_end = self._get_reporting_period_dates(tax_year, reporting_period)
            
            # Récupération des calculs fiscaux de la période
            tax_calculations = await self._get_tax_calculations_for_period(
                user_id, jurisdiction_code, period_start, period_end
            )
            
            # Calcul des totaux
            totals = await self._calculate_report_totals(tax_calculations)
            
            # Génération du rapport
            report = TaxReportModel(
                report_id=f"TAXRPT_{tax_year}_{jurisdiction_code}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                jurisdiction_code=jurisdiction_code,
                tax_year=tax_year,
                reporting_period=reporting_period,
                period_start_date=period_start,
                period_end_date=period_end,
                total_gross_revenue=totals['gross_revenue'],
                total_taxable_amount=totals['taxable_amount'],
                total_tax_liability=totals['tax_liability'],
                streaming_revenue=totals['streaming_revenue'],
                licensing_revenue=totals['licensing_revenue'],
                merchandise_revenue=totals['merchandise_revenue'],
                collaboration_revenue=totals['collaboration_revenue'],
                revenue_breakdown=totals['revenue_breakdown'],
                tax_calculations_summary=totals['tax_summary']
            )
            
            # Sauvegarde
            self.db_session.add(report)
            await self.db_session.commit()
            
            # Génération du fichier PDF
            await self._generate_report_pdf(report)
            
            logger.info(f"Tax report generated: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Tax report generation failed: {e}")
            raise


class TaxComplianceManager:
    """    Gestionnaire principal de conformité fiscale
    """    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_manager = CacheManager()
        self.calculator = TaxCalculationEngine(
            db_manager.get_session(), 
            self.cache_manager
        )
        self.reporter = TaxReportingEngine(db_manager.get_session())
    
    async def process_revenue_for_taxes(
        self,
        revenue_record_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[TaxCalculationModel]:
        """        Traite automatiquement les taxes pour un enregistrement de revenus
        """        # Détermination des juridictions applicables
        applicable_jurisdictions = await self._determine_applicable_jurisdictions(
            user_id, revenue_record_id
        )
        
        tax_calculations = []
        
        for jurisdiction_code in applicable_jurisdictions:
            calculation = await self.calculator.calculate_taxes(
                revenue_record_id=revenue_record_id,
                user_id=user_id,
                jurisdiction_code=jurisdiction_code
            )
            tax_calculations.append(calculation)
        
        logger.info(f"Tax calculations completed for {len(applicable_jurisdictions)} jurisdictions")
        return tax_calculations
    
    async def setup_jurisdiction_rules(
        self,
        jurisdiction_code: str,
        rules_config: Dict[str, Any]
    ) -> TaxJurisdictionRuleModel:
        """        Configure les règles fiscales pour une juridiction
        """        rule = TaxJurisdictionRuleModel(
            jurisdiction_code=jurisdiction_code,
            jurisdiction_name=rules_config['name'],
            income_tax_rate=Decimal(str(rules_config.get('income_tax_rate', 0))),
            vat_rate=Decimal(str(rules_config.get('vat_rate', 0))),
            withholding_tax_rate=Decimal(str(rules_config.get('withholding_tax_rate', 0))),
            tax_free_threshold=Decimal(str(rules_config.get('tax_free_threshold', 0))),
            artist_tax_exemption=rules_config.get('artist_tax_exemption', False),
            calculation_rules=rules_config.get('calculation_rules'),
            reporting_requirements=rules_config.get('reporting_requirements'),
            effective_date=rules_config.get('effective_date', datetime.utcnow())
        )
        
        async with self.db_manager.get_session() as session:
            session.add(rule)
            await session.commit()
        
        return rule
    
    async def generate_compliance_report(
        self,
        user_id: uuid.UUID,
        tax_year: int
    ) -> Dict[str, TaxReportModel]:
        """        Génère des rapports de conformité pour toutes les juridictions applicables
        """        user_jurisdictions = await self._get_user_applicable_jurisdictions(user_id)
        reports = {}
        
        for jurisdiction_code in user_jurisdictions:
            report = await self.reporter.generate_tax_report(
                user_id=user_id,
                jurisdiction_code=jurisdiction_code,
                tax_year=tax_year
            )
            reports[jurisdiction_code] = report
        
        return reports
