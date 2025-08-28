"""
🚀 Tax Calculator - IA Influencer Agent Platform Enterprise
========================================================
Module: backend/platform_core/billing/tax_calculator.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 CALCULATEUR DE TAXES INTERNATIONALES
Système de calcul automatique des taxes selon les juridictions
- Support TVA/TPS/HST/Sales Tax internationales
- Règles par pays/état/province configurables
- Intégration APIs officielles (Avalara, TaxJar)
- Exemptions et cas spéciaux automatiques
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

# Configuration
logger = logging.getLogger(__name__)

class TaxType(Enum):
    """Types de taxes"""
    VAT = "vat"  # TVA (Europe)
    GST = "gst"  # TPS (Canada, Australie)
    HST = "hst"  # TVH (Canada)
    SALES_TAX = "sales_tax"  # Taxe de vente (US)
    EXCISE = "excise"  # Accise
    CUSTOMS = "customs"  # Douane
    SERVICE_TAX = "service_tax"  # Taxe sur services

class TaxStatus(Enum):
    """Statuts fiscaux"""
    TAXABLE = "taxable"
    EXEMPT = "exempt"
    ZERO_RATED = "zero_rated"
    REVERSE_CHARGE = "reverse_charge"

@dataclass
class TaxRule:
    """Règle de taxation"""
    rule_id: str
    name: str
    country: str
    state_province: Optional[str] = None
    city: Optional[str] = None
    postal_code_pattern: Optional[str] = None
    
    # Configuration de la taxe
    tax_type: TaxType = TaxType.VAT
    tax_rate: Decimal = Decimal("0.0")
    compound: bool = False  # Taxe composée
    
    # Conditions d'application
    applies_to_digital_goods: bool = True
    applies_to_physical_goods: bool = True
    applies_to_services: bool = True
    minimum_amount: Decimal = Decimal("0.0")
    maximum_amount: Optional[Decimal] = None
    
    # Exemptions
    exempt_customer_types: List[str] = field(default_factory=list)
    exempt_product_categories: List[str] = field(default_factory=list)
    
    # Dates d'application
    effective_from: datetime = field(default_factory=datetime.utcnow)
    effective_until: Optional[datetime] = None
    
    # Métadonnées
    description: str = ""
    authority: str = ""  # Autorité fiscale
    registration_required: bool = False
    
    def is_applicable(self, 
                     amount: Decimal,
                     customer_type: Optional[str] = None,
                     product_category: Optional[str] = None,
                     transaction_date: Optional[datetime] = None) -> bool:
        """Vérifie si la règle s'applique"""
        
        # Vérifier les dates
        check_date = transaction_date or datetime.utcnow()
        if check_date < self.effective_from:
            return False
        if self.effective_until and check_date > self.effective_until:
            return False
            
        # Vérifier le montant
        if amount < self.minimum_amount:
            return False
        if self.maximum_amount and amount > self.maximum_amount:
            return False
            
        # Vérifier les exemptions
        if customer_type and customer_type in self.exempt_customer_types:
            return False
        if product_category and product_category in self.exempt_product_categories:
            return False
            
        return True

@dataclass
class TaxCalculationResult:
    """Résultat du calcul de taxes"""
    subtotal: Decimal
    total_tax: Decimal
    total_amount: Decimal
    tax_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    
    # Détails par type de taxe
    vat_amount: Decimal = Decimal("0.0")
    gst_amount: Decimal = Decimal("0.0")
    sales_tax_amount: Decimal = Decimal("0.0")
    
    # Métadonnées
    calculation_date: datetime = field(default_factory=datetime.utcnow)
    jurisdiction: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "subtotal": float(self.subtotal),
            "total_tax": float(self.total_tax),
            "total_amount": float(self.total_amount),
            "tax_breakdown": self.tax_breakdown,
            "applied_rules": self.applied_rules,
            "vat_amount": float(self.vat_amount),
            "gst_amount": float(self.gst_amount),
            "sales_tax_amount": float(self.sales_tax_amount),
            "calculation_date": self.calculation_date.isoformat(),
            "jurisdiction": self.jurisdiction
        }

@dataclass
class TaxableItem:
    """Item soumis à taxation"""
    item_id: str
    description: str
    amount: Decimal
    quantity: int = 1
    
    # Classification
    product_category: Optional[str] = None
    tax_category: Optional[str] = None
    
    # Statut fiscal
    tax_status: TaxStatus = TaxStatus.TAXABLE
    
    # Métadonnées
    is_digital: bool = False
    is_service: bool = False
    origin_country: Optional[str] = None

@dataclass
class CustomerTaxInfo:
    """Informations fiscales client"""
    customer_id: str
    
    # Type de client
    customer_type: str = "individual"  # individual, business, non_profit, government
    
    # Numéros de TVA/Tax
    vat_number: Optional[str] = None
    tax_id: Optional[str] = None
    
    # Adresse fiscale
    country: str = ""
    state_province: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    
    # Exemptions
    tax_exempt: bool = False
    exempt_reason: Optional[str] = None
    exemption_certificate: Optional[str] = None

class TaxCalculator:
    """Calculateur de taxes intelligent"""
    
    def __init__(self):
        self.tax_rules: Dict[str, TaxRule] = {}
        self.tax_cache: Dict[str, TaxCalculationResult] = {}
        
        # Intégrations externes
        self.external_providers = {}
        
        # Charger les règles par défaut
        self._load_default_rules()
        
    def _load_default_rules(self):
        """Charge les règles de taxation par défaut"""
        
        # Canada - TPS/TVQ
        self.add_tax_rule(TaxRule(
            rule_id="ca_gst",
            name="TPS Canada",
            country="CA",
            tax_type=TaxType.GST,
            tax_rate=Decimal("5.0"),
            description="Taxe sur les produits et services fédérale"
        ))
        
        # Québec - TVQ
        self.add_tax_rule(TaxRule(
            rule_id="ca_qc_qst",
            name="TVQ Québec",
            country="CA",
            state_province="QC",
            tax_type=TaxType.SALES_TAX,
            tax_rate=Decimal("9.975"),
            description="Taxe de vente du Québec"
        ))
        
        # France - TVA
        self.add_tax_rule(TaxRule(
            rule_id="fr_vat_standard",
            name="TVA France Standard",
            country="FR",
            tax_type=TaxType.VAT,
            tax_rate=Decimal("20.0"),
            description="TVA normale France"
        ))
        
        # Allemagne - TVA
        self.add_tax_rule(TaxRule(
            rule_id="de_vat_standard",
            name="TVA Allemagne Standard",
            country="DE",
            tax_type=TaxType.VAT,
            tax_rate=Decimal("19.0"),
            description="Mehrwertsteuer Standard"
        ))
        
        # États-Unis - Sales Tax (exemple Californie)
        self.add_tax_rule(TaxRule(
            rule_id="us_ca_sales_tax",
            name="Sales Tax Californie",
            country="US",
            state_province="CA",
            tax_type=TaxType.SALES_TAX,
            tax_rate=Decimal("7.25"),
            description="California State Sales Tax"
        ))
        
        # Royaume-Uni - VAT
        self.add_tax_rule(TaxRule(
            rule_id="gb_vat_standard",
            name="VAT UK Standard",
            country="GB",
            tax_type=TaxType.VAT,
            tax_rate=Decimal("20.0"),
            description="UK VAT Standard Rate"
        ))
        
        logger.info(f"Règles de taxation chargées: {len(self.tax_rules)}")
        
    def add_tax_rule(self, rule: TaxRule):
        """Ajoute une règle de taxation"""
        self.tax_rules[rule.rule_id] = rule
        logger.debug(f"Règle ajoutée: {rule.name} ({rule.rule_id})")
        
    def remove_tax_rule(self, rule_id: str):
        """Supprime une règle de taxation"""
        if rule_id in self.tax_rules:
            del self.tax_rules[rule_id]
            logger.debug(f"Règle supprimée: {rule_id}")
            
    async def calculate_tax(self,
                           items: List[TaxableItem],
                           customer_info: CustomerTaxInfo,
                           transaction_date: Optional[datetime] = None) -> TaxCalculationResult:
        """Calcule les taxes pour une transaction"""
        
        cache_key = self._generate_cache_key(items, customer_info)
        if cache_key in self.tax_cache:
            return self.tax_cache[cache_key]
            
        subtotal = sum(item.amount * item.quantity for item in items)
        total_tax = Decimal("0.0")
        tax_breakdown = []
        applied_rules = []
        
        # Grouper les taxes par type
        tax_by_type = {
            TaxType.VAT: Decimal("0.0"),
            TaxType.GST: Decimal("0.0"),
            TaxType.SALES_TAX: Decimal("0.0")
        }
        
        # Vérifier si le client est exempté
        if customer_info.tax_exempt:
            result = TaxCalculationResult(
                subtotal=subtotal,
                total_tax=Decimal("0.0"),
                total_amount=subtotal,
                jurisdiction=f"{customer_info.country}-{customer_info.state_province or 'N/A'}"
            )
            self.tax_cache[cache_key] = result
            return result
            
        # Trouver les règles applicables
        applicable_rules = self._find_applicable_rules(customer_info, transaction_date)
        
        for rule in applicable_rules:
            rule_tax_total = Decimal("0.0")
            
            for item in items:
                if not rule.is_applicable(
                    amount=item.amount,
                    customer_type=customer_info.customer_type,
                    product_category=item.product_category,
                    transaction_date=transaction_date
                ):
                    continue
                    
                # Vérifier le statut fiscal de l'item
                if item.tax_status != TaxStatus.TAXABLE:
                    continue
                    
                # Calculer la taxe pour cet item
                item_amount = item.amount * item.quantity
                item_tax = item_amount * (rule.tax_rate / Decimal("100"))
                rule_tax_total += item_tax
                
            if rule_tax_total > 0:
                tax_breakdown.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "tax_type": rule.tax_type.value,
                    "tax_rate": float(rule.tax_rate),
                    "tax_amount": float(rule_tax_total),
                    "jurisdiction": f"{rule.country}-{rule.state_province or 'National'}"
                })
                
                applied_rules.append(rule.rule_id)
                total_tax += rule_tax_total
                
                # Grouper par type
                if rule.tax_type in tax_by_type:
                    tax_by_type[rule.tax_type] += rule_tax_total
                    
        result = TaxCalculationResult(
            subtotal=subtotal,
            total_tax=total_tax,
            total_amount=subtotal + total_tax,
            tax_breakdown=tax_breakdown,
            applied_rules=applied_rules,
            vat_amount=tax_by_type[TaxType.VAT],
            gst_amount=tax_by_type[TaxType.GST],
            sales_tax_amount=tax_by_type[TaxType.SALES_TAX],
            jurisdiction=f"{customer_info.country}-{customer_info.state_province or 'N/A'}"
        )
        
        # Mettre en cache
        self.tax_cache[cache_key] = result
        
        logger.debug(f"Taxes calculées: {total_tax} sur {subtotal}")
        return result
        
    def _find_applicable_rules(self,
                              customer_info: CustomerTaxInfo,
                              transaction_date: Optional[datetime] = None) -> List[TaxRule]:
        """Trouve les règles applicables pour un client"""
        applicable_rules = []
        
        for rule in self.tax_rules.values():
            # Vérifier le pays
            if rule.country != customer_info.country:
                continue
                
            # Vérifier l'état/province
            if rule.state_province and rule.state_province != customer_info.state_province:
                continue
                
            # Vérifier la ville
            if rule.city and rule.city != customer_info.city:
                continue
                
            # Vérifier le code postal (pattern matching)
            if rule.postal_code_pattern and customer_info.postal_code:
                import re
                if not re.match(rule.postal_code_pattern, customer_info.postal_code):
                    continue
                    
            # Vérifier les dates
            check_date = transaction_date or datetime.utcnow()
            if check_date < rule.effective_from:
                continue
            if rule.effective_until and check_date > rule.effective_until:
                continue
                
            applicable_rules.append(rule)
            
        # Trier par spécificité (plus spécifique en premier)
        applicable_rules.sort(key=lambda r: (
            1 if r.state_province else 0,
            1 if r.city else 0,
            1 if r.postal_code_pattern else 0
        ), reverse=True)
        
        return applicable_rules
        
    async def validate_vat_number(self, vat_number: str, country: str) -> Dict[str, Any]:
        """Valide un numéro de TVA"""
        # Simulation de validation - dans un vrai système, on utiliserait
        # l'API VIES pour l'Europe ou d'autres services officiels
        
        if not vat_number:
            return {"valid": False, "error": "Numéro de TVA vide"}
            
        # Formats de base par pays
        vat_patterns = {
            "FR": r"^FR[A-Z0-9]{11}$",
            "DE": r"^DE[0-9]{9}$",
            "GB": r"^GB[0-9]{9}$|^GB[0-9]{12}$",
            "IT": r"^IT[0-9]{11}$",
            "ES": r"^ES[A-Z][0-9]{8}$|^ES[0-9]{8}[A-Z]$",
            "NL": r"^NL[0-9]{9}B[0-9]{2}$"
        }
        
        pattern = vat_patterns.get(country.upper())
        if not pattern:
            return {"valid": False, "error": f"Validation non supportée pour {country}"}
            
        import re
        if re.match(pattern, vat_number.upper()):
            return {
                "valid": True,
                "vat_number": vat_number.upper(),
                "country": country.upper(),
                "format_valid": True
            }
        else:
            return {
                "valid": False,
                "error": "Format de numéro de TVA invalide",
                "expected_format": pattern
            }
            
    async def calculate_reverse_charge_vat(self,
                                         supplier_country: str,
                                         customer_country: str,
                                         customer_vat_number: Optional[str],
                                         amount: Decimal) -> Dict[str, Any]:
        """Calcule la TVA en auto-liquidation (reverse charge)"""
        
        # Règles générales UE pour reverse charge
        eu_countries = {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
            "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
            "PL", "PT", "RO", "SK", "SI", "ES", "SE"
        }
        
        # Vérifier si c'est une transaction B2B intra-UE
        if (supplier_country in eu_countries and 
            customer_country in eu_countries and 
            supplier_country != customer_country and
            customer_vat_number):
            
            # Valider le numéro de TVA
            vat_validation = await self.validate_vat_number(customer_vat_number, customer_country)
            
            if vat_validation["valid"]:
                return {
                    "reverse_charge_applicable": True,
                    "supplier_charges_vat": False,
                    "customer_self_assesses": True,
                    "vat_rate": self._get_standard_vat_rate(customer_country),
                    "amount": amount,
                    "vat_amount": amount * (self._get_standard_vat_rate(customer_country) / Decimal("100")),
                    "note": "Auto-liquidation TVA - Le client doit auto-liquider la TVA"
                }
                
        return {
            "reverse_charge_applicable": False,
            "supplier_charges_vat": True,
            "note": "TVA normale applicable"
        }
        
    def _get_standard_vat_rate(self, country: str) -> Decimal:
        """Retourne le taux de TVA standard d'un pays"""
        standard_rates = {
            "FR": Decimal("20.0"),
            "DE": Decimal("19.0"),
            "GB": Decimal("20.0"),
            "IT": Decimal("22.0"),
            "ES": Decimal("21.0"),
            "NL": Decimal("21.0"),
            "BE": Decimal("21.0"),
            "AT": Decimal("20.0")
        }
        return standard_rates.get(country.upper(), Decimal("20.0"))
        
    def _generate_cache_key(self, items: List[TaxableItem], customer_info: CustomerTaxInfo) -> str:
        """Génère une clé de cache pour le calcul"""
        import hashlib
        
        items_hash = hashlib.md5(
            json.dumps([{
                "amount": float(item.amount),
                "quantity": item.quantity,
                "category": item.product_category,
                "tax_status": item.tax_status.value
            } for item in items], sort_keys=True).encode()
        ).hexdigest()
        
        customer_hash = hashlib.md5(
            json.dumps({
                "country": customer_info.country,
                "state": customer_info.state_province,
                "city": customer_info.city,
                "type": customer_info.customer_type,
                "exempt": customer_info.tax_exempt
            }, sort_keys=True).encode()
        ).hexdigest()
        
        return f"{items_hash}:{customer_hash}"
        
    def get_tax_report(self, 
                      start_date: datetime,
                      end_date: datetime) -> Dict[str, Any]:
        """Génère un rapport fiscal"""
        # Dans un vrai système, on interrogerait la base de données
        # pour récupérer toutes les transactions sur la période
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_sales": 0.0,
                "total_tax_collected": 0.0,
                "tax_by_jurisdiction": {},
                "tax_by_type": {}
            },
            "details": [],
            "rules_applied": list(self.tax_rules.keys())
        }
        
    def get_calculator_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du calculateur"""
        return {
            "total_rules": len(self.tax_rules),
            "rules_by_country": {},
            "cache_size": len(self.tax_cache),
            "supported_tax_types": [t.value for t in TaxType]
        }