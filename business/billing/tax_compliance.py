"""Tax Compliance Engine - International tax compliance and reporting
=================================================================

Comprehensive tax compliance system supporting international tax
regulations, automated calculations, and compliance reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class TaxType(Enum):
    """Types of taxes"""    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"
    WITHHOLDING_TAX = "withholding_tax"

class ComplianceStatus(Enum):
    """Tax compliance status"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPTED = "exempted"

@dataclass
class TaxRule:
    """Tax rule configuration"""    rule_id: str
    country: str
    tax_type: TaxType
    rate: Decimal
    threshold: Optional[Decimal]
    applicable_categories: List[str]
    is_active: bool
    effective_date: datetime

@dataclass
class TaxCalculation:
    """Tax calculation result"""    transaction_id: str
    total_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    tax_breakdown: Dict[str, Decimal]
    applicable_rules: List[str]
    compliance_status: ComplianceStatus

class TaxComplianceEngine:
    """    Advanced tax compliance system supporting international tax regulations,
    automated calculations, compliance monitoring, and reporting.
    """    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize tax compliance engine"""        try:
            await self._setup_database_tables()
            await self._load_tax_rules()
            await self._setup_compliance_monitoring()
            logger.info("Tax Compliance Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tax Compliance Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for tax compliance"""        async with self.db_pool.acquire() as conn:
            await conn.execute("""                CREATE TABLE IF NOT EXISTS tax_rules (
                    id SERIAL PRIMARY KEY,
                    rule_id VARCHAR(100) UNIQUE NOT NULL,
                    country VARCHAR(2) NOT NULL,
                    tax_type VARCHAR(20) NOT NULL,
                    rate DECIMAL(10,6) NOT NULL,
                    threshold DECIMAL(15,2),
                    applicable_categories JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    effective_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_tax_rules_country_active (country, is_active),
                    INDEX idx_tax_rules_type (tax_type, effective_date DESC)
                );
            """)
            
            await conn.execute("""                CREATE TABLE IF NOT EXISTS tax_calculations (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(255) UNIQUE NOT NULL,
                    customer_country VARCHAR(2) NOT NULL,
                    total_amount DECIMAL(15,2) NOT NULL,
                    tax_amount DECIMAL(15,2) NOT NULL,
                    net_amount DECIMAL(15,2) NOT NULL,
                    tax_breakdown JSONB NOT NULL,
                    applicable_rules JSONB NOT NULL,
                    compliance_status VARCHAR(20) NOT NULL,
                    calculated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_tax_calc_country_date (customer_country, calculated_at DESC),
                    INDEX idx_tax_calc_status (compliance_status)
                );
            """)
            
            await conn.execute("""                CREATE TABLE IF NOT EXISTS tax_reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) UNIQUE NOT NULL,
                    report_type VARCHAR(30) NOT NULL,
                    country VARCHAR(2) NOT NULL,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    total_revenue DECIMAL(15,2) NOT NULL,
                    total_tax DECIMAL(15,2) NOT NULL,
                    transaction_count INTEGER NOT NULL,
                    report_data JSONB NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    submitted_at TIMESTAMP
                );
            """)

    async def _load_tax_rules(self) -> None:
        """Load tax rules for different countries"""        try:
            # Default tax rules for major markets
            default_rules = [
                # United States
                {
                    'rule_id': 'us_sales_tax',
                    'country': 'US',
                    'tax_type': TaxType.SALES_TAX,
                    'rate': Decimal('0.0875'),  # 8.75% average
                    'threshold': Decimal('0.00'),
                    'applicable_categories': ['digital_content', 'services']
                },
                # European Union - VAT
                {
                    'rule_id': 'eu_vat_standard',
                    'country': 'EU',
                    'tax_type': TaxType.VAT,
                    'rate': Decimal('0.20'),    # 20% standard rate
                    'threshold': Decimal('10000.00'),
                    'applicable_categories': ['digital_content', 'services']
                },
                # United Kingdom
                {
                    'rule_id': 'uk_vat',
                    'country': 'GB',
                    'tax_type': TaxType.VAT,
                    'rate': Decimal('0.20'),    # 20%
                    'threshold': Decimal('85000.00'),
                    'applicable_categories': ['digital_content', 'services']
                },
                # Canada
                {
                    'rule_id': 'ca_gst_hst',
                    'country': 'CA',
                    'tax_type': TaxType.GST,
                    'rate': Decimal('0.13'),    # 13% HST
                    'threshold': Decimal('30000.00'),
                    'applicable_categories': ['digital_content', 'services']
                },
                # Germany
                {
                    'rule_id': 'de_vat',
                    'country': 'DE',
                    'tax_type': TaxType.VAT,
                    'rate': Decimal('0.19'),    # 19%
                    'threshold': Decimal('22000.00'),
                    'applicable_categories': ['digital_content', 'services']
                }
            ]
            
            async with self.db_pool.acquire() as conn:
                for rule_data in default_rules:
                    await conn.execute("""                        INSERT INTO tax_rules 
                        (rule_id, country, tax_type, rate, threshold, applicable_categories, effective_date)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (rule_id) DO UPDATE SET
                            rate = EXCLUDED.rate,
                            threshold = EXCLUDED.threshold,
                            applicable_categories = EXCLUDED.applicable_categories
                    """,
                    rule_data['rule_id'],
                    rule_data['country'],
                    rule_data['tax_type'].value,
                    rule_data['rate'],
                    rule_data['threshold'],
                    json.dumps(rule_data['applicable_categories']),
                    datetime.now().date()
                    )
                    
        except Exception as e:
            logger.error(f"Failed to load tax rules: {e}")

    async def _setup_compliance_monitoring(self) -> None:
        """Setup compliance monitoring system"""        try:
            # Cache compliance thresholds
            thresholds = {
                'US': {'sales_tax': 100000},      # $100k
                'EU': {'vat': 10000},            # €10k
                'GB': {'vat': 85000},            # £85k
                'CA': {'gst': 30000},            # CAD $30k
                'DE': {'vat': 22000}             # €22k
            }
            
            for country, limits in thresholds.items():
                self.redis.setex(f"tax_threshold_{country}", 3600, json.dumps(limits))
                
        except Exception as e:
            logger.error(f"Failed to setup compliance monitoring: {e}")

    async def calculate_tax(self, transaction_id: str, amount: Decimal, 
                           customer_country: str, category: str = 'digital_content') -> TaxCalculation:
        """Calculate taxes for transaction"""        try:
            # Get applicable tax rules
            tax_rules = await self._get_tax_rules(customer_country, category)
            
            if not tax_rules:
                # No tax applicable
                return TaxCalculation(
                    transaction_id=transaction_id,
                    total_amount=amount,
                    tax_amount=Decimal('0.00'),
                    net_amount=amount,
                    tax_breakdown={},
                    applicable_rules=[],
                    compliance_status=ComplianceStatus.EXEMPTED
                )
            
            tax_breakdown = {}
            total_tax = Decimal('0.00')
            applicable_rules = []
            
            for rule in tax_rules:
                # Check threshold compliance
                if rule.threshold and amount < rule.threshold:
                    continue
                    
                tax_amount = amount * rule.rate
                tax_breakdown[f"{rule.tax_type.value}_{rule.country}"] = tax_amount
                total_tax += tax_amount
                applicable_rules.append(rule.rule_id)
            
            net_amount = amount - total_tax
            compliance_status = ComplianceStatus.COMPLIANT
            
            # Store calculation
            tax_calc = TaxCalculation(
                transaction_id=transaction_id,
                total_amount=amount,
                tax_amount=total_tax,
                net_amount=net_amount,
                tax_breakdown=tax_breakdown,
                applicable_rules=applicable_rules,
                compliance_status=compliance_status
            )
            
            await self._store_tax_calculation(tax_calc, customer_country)
            
            return tax_calc
            
        except Exception as e:
            logger.error(f"Failed to calculate tax: {e}")
            raise HTTPException(status_code=500, detail="Tax calculation failed")

    async def _get_tax_rules(self, country: str, category: str) -> List[TaxRule]:
        """Get applicable tax rules for country and category"""        try:
            async with self.db_pool.acquire() as conn:
                # Check for country-specific rules first
                rules_data = await conn.fetch("""                    SELECT rule_id, country, tax_type, rate, threshold, applicable_categories
                    FROM tax_rules 
                    WHERE (country = $1 OR country = 'EU') 
                    AND is_active = TRUE
                    AND effective_date <= CURRENT_DATE
                    ORDER BY effective_date DESC
                """, country)
                
                tax_rules = []
                for row in rules_data:
                    categories = row['applicable_categories']
                    if categories and category in categories:
                        tax_rules.append(TaxRule(
                            rule_id=row['rule_id'],
                            country=row['country'],
                            tax_type=TaxType(row['tax_type']),
                            rate=row['rate'],
                            threshold=row['threshold'],
                            applicable_categories=categories,
                            is_active=True,
                            effective_date=datetime.now()
                        ))
                
                return tax_rules
                
        except Exception as e:
            logger.error(f"Failed to get tax rules: {e}")
            return []

    async def _store_tax_calculation(self, tax_calc: TaxCalculation, customer_country: str) -> None:
        """Store tax calculation record"""        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO tax_calculations 
                    (transaction_id, customer_country, total_amount, tax_amount, net_amount,
                     tax_breakdown, applicable_rules, compliance_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                tax_calc.transaction_id,
                customer_country,
                tax_calc.total_amount,
                tax_calc.tax_amount,
                tax_calc.net_amount,
                json.dumps({k: str(v) for k, v in tax_calc.tax_breakdown.items()}),
                json.dumps(tax_calc.applicable_rules),
                tax_calc.compliance_status.value
                )
                
        except Exception as e:
            logger.error(f"Failed to store tax calculation: {e}")

    async def generate_tax_report(self, country: str, start_date: datetime, 
                                end_date: datetime, report_type: str = 'summary') -> Dict[str, Any]:
        """Generate tax compliance report"""        try:
            async with self.db_pool.acquire() as conn:
                # Get transaction summary
                summary = await conn.fetchrow("""                    SELECT 
                        COUNT(*) as transaction_count,
                        SUM(total_amount) as total_revenue,
                        SUM(tax_amount) as total_tax,
                        AVG(tax_amount / total_amount * 100) as avg_tax_rate
                    FROM tax_calculations 
                    WHERE customer_country = $1
                    AND calculated_at BETWEEN $2 AND $3
                    AND compliance_status != 'exempted'
                """, country, start_date, end_date)
                
                # Get tax breakdown
                breakdown = await conn.fetch("""                    SELECT 
                        jsonb_object_keys(tax_breakdown) as tax_type,
                        SUM((tax_breakdown ->> jsonb_object_keys(tax_breakdown))::decimal) as amount
                    FROM tax_calculations 
                    WHERE customer_country = $1
                    AND calculated_at BETWEEN $2 AND $3
                    GROUP BY jsonb_object_keys(tax_breakdown)
                """, country, start_date, end_date)
                
                # Monthly breakdown
                monthly_data = await conn.fetch("""                    SELECT 
                        DATE_TRUNC('month', calculated_at) as month,
                        COUNT(*) as transactions,
                        SUM(total_amount) as revenue,
                        SUM(tax_amount) as tax
                    FROM tax_calculations 
                    WHERE customer_country = $1
                    AND calculated_at BETWEEN $2 AND $3
                    GROUP BY DATE_TRUNC('month', calculated_at)
                    ORDER BY month
                """, country, start_date, end_date)
                
                report_data = {
                    'summary': {
                        'transaction_count': int(summary['transaction_count']) if summary else 0,
                        'total_revenue': float(summary['total_revenue'] or 0),
                        'total_tax': float(summary['total_tax'] or 0),
                        'average_tax_rate': float(summary['avg_tax_rate'] or 0)
                    },
                    'tax_breakdown': [
                        {
                            'tax_type': row['tax_type'],
                            'amount': float(row['amount'])
                        }
                        for row in breakdown
                    ],
                    'monthly_data': [
                        {
                            'month': row['month'].strftime('%Y-%m'),
                            'transactions': int(row['transactions']),
                            'revenue': float(row['revenue']),
                            'tax': float(row['tax'])
                        }
                        for row in monthly_data
                    ]
                }
                
                # Store report
                report_id = f"tax_report_{country}_{report_type}_{int(datetime.now().timestamp())}"
                await conn.execute("""                    INSERT INTO tax_reports 
                    (report_id, report_type, country, period_start, period_end,
                     total_revenue, total_tax, transaction_count, report_data, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'generated')
                """,
                report_id,
                report_type,
                country,
                start_date.date(),
                end_date.date(),
                summary['total_revenue'] if summary else 0,
                summary['total_tax'] if summary else 0,
                summary['transaction_count'] if summary else 0,
                json.dumps(report_data)
                )
                
                return {
                    'report_id': report_id,
                    'country': country,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'data': report_data,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate tax report: {e}")
            raise HTTPException(status_code=500, detail="Tax report generation failed")

    async def check_compliance_threshold(self, country: str, current_revenue: Decimal) -> Dict[str, Any]:
        """Check if revenue exceeds compliance thresholds"""        try:
            # Get threshold data
            cached_thresholds = self.redis.get(f"tax_threshold_{country}")
            if not cached_thresholds:
                return {'requires_registration': False, 'threshold_info': {}}
            
            thresholds = json.loads(cached_thresholds.decode())
            
            results = {}
            for tax_type, threshold in thresholds.items():
                exceeds_threshold = current_revenue >= Decimal(str(threshold))
                results[tax_type] = {
                    'threshold': threshold,
                    'current_revenue': float(current_revenue),
                    'exceeds_threshold': exceeds_threshold,
                    'remaining_allowance': max(0, threshold - float(current_revenue))
                }
            
            requires_registration = any(result['exceeds_threshold'] for result in results.values())
            
            return {
                'country': country,
                'requires_registration': requires_registration,
                'threshold_info': results,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check compliance threshold: {e}")
            return {'requires_registration': False, 'threshold_info': {}}

    async def update_tax_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update tax rule"""        try:
            async with self.db_pool.acquire() as conn:
                set_clauses = []
                values = []
                param_count = 1
                
                for field, value in updates.items():
                    if field in ['rate', 'threshold']:
                        set_clauses.append(f"{field} = ${param_count}")
                        values.append(Decimal(str(value)))
                    elif field in ['country', 'tax_type', 'is_active']:
                        set_clauses.append(f"{field} = ${param_count}")
                        values.append(value)
                    elif field == 'applicable_categories':
                        set_clauses.append(f"{field} = ${param_count}")
                        values.append(json.dumps(value))
                    param_count += 1
                
                if set_clauses:
                    values.append(rule_id)
                    query = f"""                        UPDATE tax_rules 
                        SET {', '.join(set_clauses)}
                        WHERE rule_id = ${param_count}
                    """                    
                    await conn.execute(query, *values)
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Failed to update tax rule: {e}")
            return False

    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get tax compliance dashboard data"""        try:
            async with self.db_pool.acquire() as conn:
                # Recent calculations
                recent_calcs = await conn.fetch("""                    SELECT 
                        transaction_id,
                        customer_country,
                        total_amount,
                        tax_amount,
                        compliance_status,
                        calculated_at
                    FROM tax_calculations
                    ORDER BY calculated_at DESC
                    LIMIT 20
                """)
                
                # Country summary
                country_summary = await conn.fetch("""                    SELECT 
                        customer_country,
                        COUNT(*) as transaction_count,
                        SUM(total_amount) as revenue,
                        SUM(tax_amount) as tax_collected
                    FROM tax_calculations
                    WHERE calculated_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY customer_country
                    ORDER BY revenue DESC
                """)
                
                # Compliance status distribution
                status_dist = await conn.fetch("""                    SELECT 
                        compliance_status,
                        COUNT(*) as count
                    FROM tax_calculations
                    WHERE calculated_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY compliance_status
                """)
                
                return {
                    'recent_calculations': [
                        {
                            'transaction_id': calc['transaction_id'],
                            'country': calc['customer_country'],
                            'total_amount': float(calc['total_amount']),
                            'tax_amount': float(calc['tax_amount']),
                            'status': calc['compliance_status'],
                            'calculated_at': calc['calculated_at'].isoformat()
                        }
                        for calc in recent_calcs
                    ],
                    'country_summary': [
                        {
                            'country': row['customer_country'],
                            'transactions': int(row['transaction_count']),
                            'revenue': float(row['revenue']),
                            'tax_collected': float(row['tax_collected'])
                        }
                        for row in country_summary
                    ],
                    'status_distribution': [
                        {
                            'status': row['compliance_status'],
                            'count': int(row['count'])
                        }
                        for row in status_dist
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get compliance dashboard: {e}")
            raise HTTPException(status_code=500, detail="Compliance dashboard data retrieval failed")
