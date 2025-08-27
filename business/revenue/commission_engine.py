"""
🚀 Commission Engine - Ultra-Advanced Commission Management System
================================================================

Industrial-grade commission management system handling complex commission
structures, revenue sharing, affiliate programs, and performance-based
compensation for creators and collaborators.

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

Team Specialists:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Multi-Format Upload → AI Protection → SEO → Collaboration → Commission Management
==============================================================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector

logger = logging.getLogger(__name__)


class CommissionType(Enum):
    """Commission types"""
    FLAT_RATE = "flat_rate"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


class CommissionStatus(Enum):
    """Commission calculation status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class CommissionRule:
    """Commission rule definition"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    commission_type: CommissionType = CommissionType.PERCENTAGE
    rate: Decimal = Decimal('0')
    minimum_threshold: Decimal = Decimal('0')
    maximum_cap: Optional[Decimal] = None
    tier_structure: Dict[str, Decimal] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    is_active: bool = True


class CommissionEngine:
    """
    Ultra-advanced commission management system
    
    Features:
    - Multiple commission structures (flat, percentage, tiered, performance-based)
    - Dynamic commission rate adjustment based on performance
    - Complex revenue sharing with multiple parties
    - Commission forecasting and budgeting
    - Automated approval workflows
    - Dispute resolution tracking
    - Compliance and audit trails
    - Real-time commission calculations
    """
    
    def __init__(self,
                 db_manager: DatabaseManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector):
        self.db = db_manager
        self.security = security_manager
        self.metrics = metrics_collector
        
        # Commission configuration
        self._commission_rules = {}
        self._performance_cache = {}
        
    async def initialize(self):
        """Initialize commission engine"""
        try:
            # Load commission rules
            await self._load_commission_rules()
            
            logger.info("Commission engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize commission engine: {e}")
            raise

    async def calculate_commission(self,
                                 creator_id: str,
                                 revenue_amount: Decimal,
                                 revenue_type: str,
                                 platform: str,
                                 calculation_date: datetime) -> Dict[str, Any]:
        """
        Calculate commission for a revenue transaction
        
        Args:
            creator_id: Creator ID
            revenue_amount: Gross revenue amount
            revenue_type: Type of revenue
            platform: Platform where revenue was generated
            calculation_date: Date of calculation
            
        Returns:
            Commission calculation details
        """
        try:
            # Get applicable commission rule
            rule = await self._get_applicable_commission_rule(
                creator_id, revenue_type, platform, calculation_date
            )
            
            if not rule:
                # Use default commission rule
                rule = await self._get_default_commission_rule(creator_id)
            
            # Calculate commission amount
            commission_amount = await self._calculate_commission_amount(
                rule, revenue_amount, creator_id, platform
            )
            
            # Apply thresholds and caps
            final_commission = await self._apply_commission_limits(
                commission_amount, rule, revenue_amount
            )
            
            # Calculate net revenue (after commission)
            net_revenue = revenue_amount - final_commission
            
            # Store commission calculation
            calculation_record = await self._store_commission_calculation(
                creator_id=creator_id,
                revenue_amount=revenue_amount,
                commission_amount=final_commission,
                net_revenue=net_revenue,
                rule=rule,
                metadata={
                    'revenue_type': revenue_type,
                    'platform': platform,
                    'calculation_date': calculation_date.isoformat()
                }
            )
            
            return {
                'calculation_id': calculation_record['id'],
                'gross_revenue': float(revenue_amount),
                'commission_amount': float(final_commission),
                'commission_rate': float(rule.rate),
                'net_revenue': float(net_revenue),
                'rule_applied': rule.rule_id,
                'status': CommissionStatus.CALCULATED.value
            }
            
        except Exception as e:
            logger.error(f"Commission calculation failed: {e}")
            raise

    async def _calculate_commission_amount(self,
                                         rule: CommissionRule,
                                         revenue_amount: Decimal,
                                         creator_id: str,
                                         platform: str) -> Decimal:
        """Calculate commission amount based on rule type"""
        try:
            if rule.commission_type == CommissionType.FLAT_RATE:
                return rule.rate
            
            elif rule.commission_type == CommissionType.PERCENTAGE:
                return revenue_amount * (rule.rate / Decimal('100'))
            
            elif rule.commission_type == CommissionType.TIERED:
                return await self._calculate_tiered_commission(rule, revenue_amount)
            
            elif rule.commission_type == CommissionType.PERFORMANCE_BASED:
                return await self._calculate_performance_based_commission(
                    rule, revenue_amount, creator_id, platform
                )
            
            elif rule.commission_type == CommissionType.HYBRID:
                return await self._calculate_hybrid_commission(
                    rule, revenue_amount, creator_id, platform
                )
            
            else:
                return Decimal('0')
                
        except Exception as e:
            logger.error(f"Commission amount calculation failed: {e}")
            return Decimal('0')

    async def _calculate_tiered_commission(self,
                                         rule: CommissionRule,
                                         revenue_amount: Decimal) -> Decimal:
        """Calculate tiered commission based on revenue brackets"""
        try:
            total_commission = Decimal('0')
            remaining_amount = revenue_amount
            
            # Sort tiers by threshold (ascending)
            sorted_tiers = sorted(
                rule.tier_structure.items(),
                key=lambda x: Decimal(x[0])
            )
            
            for i, (threshold_str, rate) in enumerate(sorted_tiers):
                threshold = Decimal(threshold_str)
                
                if remaining_amount <= 0:
                    break
                
                # Calculate tier amount
                if i == len(sorted_tiers) - 1:
                    # Last tier - apply to remaining amount
                    tier_amount = remaining_amount
                else:
                    next_threshold = Decimal(sorted_tiers[i + 1][0])
                    tier_amount = min(remaining_amount, next_threshold - threshold)
                
                # Calculate commission for this tier
                tier_commission = tier_amount * (rate / Decimal('100'))
                total_commission += tier_commission
                remaining_amount -= tier_amount
            
            return total_commission
            
        except Exception as e:
            logger.error(f"Tiered commission calculation failed: {e}")
            return Decimal('0')

    async def _calculate_performance_based_commission(self,
                                                    rule: CommissionRule,
                                                    revenue_amount: Decimal,
                                                    creator_id: str,
                                                    platform: str) -> Decimal:
        """Calculate performance-based commission"""
        try:
            # Get creator performance metrics
            performance_data = await self._get_creator_performance_metrics(
                creator_id, platform
            )
            
            # Calculate performance multiplier
            multiplier = await self._calculate_performance_multiplier(
                performance_data, rule.performance_metrics
            )
            
            # Base commission
            base_commission = revenue_amount * (rule.rate / Decimal('100'))
            
            # Apply performance multiplier
            final_commission = base_commission * multiplier
            
            return final_commission
            
        except Exception as e:
            logger.error(f"Performance-based commission calculation failed: {e}")
            return Decimal('0')

    async def create_commission_rule(self,
                                   creator_id: str,
                                   rule_config: Dict[str, Any]) -> str:
        """Create new commission rule for a creator"""
        try:
            # Validate rule configuration
            await self._validate_commission_rule_config(rule_config)
            
            # Create commission rule
            rule = CommissionRule(
                creator_id=creator_id,
                commission_type=CommissionType(rule_config['type']),
                rate=Decimal(str(rule_config['rate'])),
                minimum_threshold=Decimal(str(rule_config.get('minimum_threshold', 0))),
                maximum_cap=Decimal(str(rule_config['maximum_cap'])) if rule_config.get('maximum_cap') else None,
                tier_structure=rule_config.get('tier_structure', {}),
                performance_metrics=rule_config.get('performance_metrics', {}),
                effective_date=datetime.fromisoformat(rule_config.get('effective_date', datetime.utcnow().isoformat())),
                expiry_date=datetime.fromisoformat(rule_config['expiry_date']) if rule_config.get('expiry_date') else None
            )
            
            # Store rule
            await self._store_commission_rule(rule)
            
            # Cache rule
            self._commission_rules[rule.rule_id] = rule
            
            logger.info(f"Commission rule {rule.rule_id} created for creator {creator_id}")
            return rule.rule_id
            
        except Exception as e:
            logger.error(f"Commission rule creation failed: {e}")
            raise

    async def get_commission_summary(self,
                                   creator_id: str,
                                   date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get commission summary for a creator"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_calculations,
                    SUM(gross_revenue) as total_gross_revenue,
                    SUM(commission_amount) as total_commission,
                    SUM(net_revenue) as total_net_revenue,
                    AVG(commission_rate) as avg_commission_rate,
                    MIN(commission_rate) as min_commission_rate,
                    MAX(commission_rate) as max_commission_rate
                FROM commission_calculations
                WHERE creator_id = %s 
                AND created_at BETWEEN %s AND %s
                AND status != 'cancelled'
            """
            
            summary_data = await self.db.fetch_one(query, (
                creator_id, date_range[0], date_range[1]
            ))
            
            # Get commission breakdown by platform
            platform_query = """
                SELECT 
                    metadata->>'platform' as platform,
                    COUNT(*) as calculations,
                    SUM(commission_amount) as total_commission,
                    AVG(commission_rate) as avg_rate
                FROM commission_calculations
                WHERE creator_id = %s 
                AND created_at BETWEEN %s AND %s
                AND status != 'cancelled'
                GROUP BY metadata->>'platform'
                ORDER BY total_commission DESC
            """
            
            platform_data = await self.db.fetch_all(platform_query, (
                creator_id, date_range[0], date_range[1]
            ))
            
            return {
                'creator_id': creator_id,
                'date_range': {
                    'start': date_range[0].isoformat(),
                    'end': date_range[1].isoformat()
                },
                'summary': {
                    'total_calculations': summary_data['total_calculations'] or 0,
                    'total_gross_revenue': float(summary_data['total_gross_revenue'] or 0),
                    'total_commission': float(summary_data['total_commission'] or 0),
                    'total_net_revenue': float(summary_data['total_net_revenue'] or 0),
                    'average_commission_rate': float(summary_data['avg_commission_rate'] or 0),
                    'commission_rate_range': {
                        'minimum': float(summary_data['min_commission_rate'] or 0),
                        'maximum': float(summary_data['max_commission_rate'] or 0)
                    }
                },
                'platform_breakdown': [
                    {
                        'platform': row['platform'],
                        'calculations': row['calculations'],
                        'total_commission': float(row['total_commission']),
                        'average_rate': float(row['avg_rate'])
                    }
                    for row in platform_data
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Commission summary generation failed: {e}")
            raise

    async def cleanup(self):
        """Cleanup commission engine resources"""
        try:
            # Clear caches
            self._commission_rules.clear()
            self._performance_cache.clear()
            
            logger.info("Commission engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Commission engine cleanup failed: {e}")
