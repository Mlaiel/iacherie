"""Advanced Rights Management Engine for IA Influencer Agent Protection System
Handles digital rights, licensing, monetization, and distribution control

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited
"""
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class RightType(Enum):
    """Types of digital rights"""
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution" 
    PUBLIC_PERFORMANCE = "public_performance"
    DISPLAY = "display"
    DERIVATIVE_WORKS = "derivative_works"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"
    MASTER_RECORDING = "master_recording"
    PUBLISHING = "publishing"
    MERCHANDISING = "merchandising"


class LicenseType(Enum):
    """License types for content usage"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    CUSTOM = "custom"


class UsageType(Enum):
    """Types of content usage"""
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"


@dataclass
class RightsBundle:
    """Bundle of rights for content"""
    bundle_id: str
    content_id: str
    owner_id: str
    rights_types: Set[RightType]
    territorial_scope: List[str]  # ISO country codes
    duration: timedelta
    created_at: datetime
    expires_at: datetime
    restrictions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.expires_at < self.created_at:
            raise ValueError("Expiration date cannot be before creation date")


@dataclass
class License:
    """Content license structure"""
    license_id: str
    rights_bundle_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    usage_types: Set[UsageType]
    territory: List[str]
    duration: timedelta
    granted_at: datetime
    expires_at: datetime
    royalty_rate: float = 0.0
    minimum_guarantee: float = 0.0
    usage_limits: Dict[str, int] = field(default_factory=dict)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    revenue_share: float = 0.0
    status: str = "active"
    terms_conditions: str = ""
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
        
    @property
    def days_remaining(self) -> int:
        if self.is_expired:
            return 0
        return (self.expires_at - datetime.utcnow()).days


@dataclass
class MonetizationRule:
    """Revenue and monetization rules"""
    rule_id: str
    content_id: str
    platform: str
    revenue_share_creator: float
    revenue_share_platform: float
    minimum_payout: float
    currency: str = "USD"
    payment_frequency: str = "monthly"  # monthly, quarterly, annual
    geographic_pricing: Dict[str, float] = field(default_factory=dict)
    premium_multiplier: float = 1.0
    active: bool = True


@dataclass
class UsageTracking:
    """Track content usage and consumption"""
    tracking_id: str
    content_id: str
    license_id: str
    user_id: Optional[str]
    platform: str
    usage_type: UsageType
    timestamp: datetime
    duration: Optional[int] = None  # seconds for audio/video
    views: int = 1
    geographic_location: Optional[str] = None
    device_type: Optional[str] = None
    revenue_generated: float = 0.0
    metadata: Dict = field(default_factory=dict)


class AdvancedRightsManager:
    """
    Ultra-advanced rights management system for content creators
    Handles licensing, monetization, usage tracking, and revenue optimization
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.rights_bundles: Dict[str, RightsBundle] = {}
        self.licenses: Dict[str, License] = {}
        self.monetization_rules: Dict[str, List[MonetizationRule]] = {}
        self.usage_tracking: List[UsageTracking] = []
        
        # Revenue optimization settings
        self.pricing_strategies = {
            'dynamic': self._dynamic_pricing_strategy,
            'fixed': self._fixed_pricing_strategy,
            'tiered': self._tiered_pricing_strategy,
            'auction': self._auction_pricing_strategy
        }
        
    def create_rights_bundle(self, content_id: str, owner_id: str, 
                           rights_config: Dict) -> RightsBundle:
        """
        Create comprehensive rights bundle for content
        
        Args:
            content_id: Content identifier
            owner_id: Rights owner identifier  
            rights_config: Configuration for rights bundle
            
        Returns:
            Created rights bundle
        """
        try:
            bundle_id = f"RIGHTS_{uuid.uuid4().hex[:16].upper()}"
            
            # Parse rights types
            rights_types = set()
            for right_str in rights_config.get('rights_types', []):
                try:
                    rights_types.add(RightType(right_str))
                except ValueError:
                    logger.warning(f"Invalid right type: {right_str}")
                    
            # Set duration
            duration_days = rights_config.get('duration_days', 365)
            duration = timedelta(days=duration_days)
            
            created_at = datetime.utcnow()
            expires_at = created_at + duration
            
            rights_bundle = RightsBundle(
                bundle_id=bundle_id,
                content_id=content_id,
                owner_id=owner_id,
                rights_types=rights_types,
                territorial_scope=rights_config.get('territories', ['WORLDWIDE']),
                duration=duration,
                created_at=created_at,
                expires_at=expires_at,
                restrictions=rights_config.get('restrictions', {}),
                metadata=rights_config.get('metadata', {})
            )
            
            # Store rights bundle
            self.rights_bundles[bundle_id] = rights_bundle
            
            logger.info(f"Created rights bundle {bundle_id} for content {content_id}")
            return rights_bundle
            
        except Exception as e:
            logger.error(f"Rights bundle creation failed: {str(e)}")
            raise
            
    def grant_license(self, rights_bundle_id: str, licensee_id: str, 
                     license_config: Dict) -> License:
        """
        Grant license for rights bundle to licensee
        
        Args:
            rights_bundle_id: Rights bundle identifier
            licensee_id: Licensee identifier
            license_config: License configuration
            
        Returns:
            Granted license
        """
        try:
            # Validate rights bundle exists
            if rights_bundle_id not in self.rights_bundles:
                raise ValueError(f"Rights bundle {rights_bundle_id} not found")
                
            rights_bundle = self.rights_bundles[rights_bundle_id]
            
            # Check if rights are still valid
            if rights_bundle.expires_at < datetime.utcnow():
                raise ValueError("Rights bundle has expired")
                
            license_id = f"LICENSE_{uuid.uuid4().hex[:16].upper()}"
            
            # Parse license configuration
            license_type = LicenseType(license_config.get('type', 'non_exclusive'))
            usage_types = set()
            for usage_str in license_config.get('usage_types', []):
                try:
                    usage_types.add(UsageType(usage_str))
                except ValueError:
                    logger.warning(f"Invalid usage type: {usage_str}")
                    
            # Set license duration
            license_duration_days = license_config.get('duration_days', 365)
            license_duration = timedelta(days=license_duration_days)
            
            granted_at = datetime.utcnow()
            license_expires_at = min(
                granted_at + license_duration,
                rights_bundle.expires_at
            )
            
            license = License(
                license_id=license_id,
                rights_bundle_id=rights_bundle_id,
                licensee_id=licensee_id,
                licensor_id=rights_bundle.owner_id,
                license_type=license_type,
                usage_types=usage_types,
                territory=license_config.get('territory', rights_bundle.territorial_scope),
                duration=license_duration,
                granted_at=granted_at,
                expires_at=license_expires_at,
                royalty_rate=license_config.get('royalty_rate', 0.0),
                minimum_guarantee=license_config.get('minimum_guarantee', 0.0),
                usage_limits=license_config.get('usage_limits', {}),
                restrictions=license_config.get('restrictions', {}),
                revenue_share=license_config.get('revenue_share', 0.0),
                terms_conditions=license_config.get('terms_conditions', '')
            )
            
            # Store license
            self.licenses[license_id] = license
            
            # Create monetization rules
            self._create_license_monetization_rules(license, license_config)
            
            logger.info(f"Granted license {license_id} to {licensee_id}")
            return license
            
        except Exception as e:
            logger.error(f"License granting failed: {str(e)}")
            raise
            
    def setup_monetization_strategy(self, content_id: str, 
                                  strategy_config: Dict) -> Dict:
        """
        Setup advanced monetization strategy for content
        
        Args:
            content_id: Content identifier
            strategy_config: Monetization configuration
            
        Returns:
            Setup result
        """
        try:
            monetization_rules = []
            
            # Create platform-specific rules
            for platform_config in strategy_config.get('platforms', []):
                platform = platform_config['platform']
                
                rule = MonetizationRule(
                    rule_id=f"MONETIZE_{uuid.uuid4().hex[:12].upper()}",
                    content_id=content_id,
                    platform=platform,
                    revenue_share_creator=platform_config.get('creator_share', 0.7),
                    revenue_share_platform=platform_config.get('platform_share', 0.3),
                    minimum_payout=platform_config.get('minimum_payout', 10.0),
                    currency=platform_config.get('currency', 'USD'),
                    payment_frequency=platform_config.get('payment_frequency', 'monthly'),
                    geographic_pricing=platform_config.get('geographic_pricing', {}),
                    premium_multiplier=platform_config.get('premium_multiplier', 1.0)
                )
                
                monetization_rules.append(rule)
                
            # Store monetization rules
            if content_id not in self.monetization_rules:
                self.monetization_rules[content_id] = []
            self.monetization_rules[content_id].extend(monetization_rules)
            
            # Setup dynamic pricing if configured
            pricing_strategy = strategy_config.get('pricing_strategy', 'fixed')
            if pricing_strategy in self.pricing_strategies:
                pricing_result = self.pricing_strategies[pricing_strategy](
                    content_id, strategy_config)
            else:
                pricing_result = {'strategy': 'default'}
                
            return {
                'success': True,
                'content_id': content_id,
                'rules_created': len(monetization_rules),
                'pricing_strategy': pricing_result,
                'estimated_revenue': self._estimate_revenue_potential(content_id)
            }
            
        except Exception as e:
            logger.error(f"Monetization setup failed: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def track_content_usage(self, content_id: str, usage_data: Dict) -> UsageTracking:
        """
        Track content usage and consumption for revenue calculation
        
        Args:
            content_id: Content identifier
            usage_data: Usage tracking data
            
        Returns:
            Usage tracking record
        """
        try:
            tracking_id = f"USAGE_{uuid.uuid4().hex[:16].upper()}"
            
            usage_record = UsageTracking(
                tracking_id=tracking_id,
                content_id=content_id,
                license_id=usage_data.get('license_id'),
                user_id=usage_data.get('user_id'),
                platform=usage_data.get('platform', 'unknown'),
                usage_type=UsageType(usage_data.get('usage_type', 'personal')),
                timestamp=datetime.utcnow(),
                duration=usage_data.get('duration'),
                views=usage_data.get('views', 1),
                geographic_location=usage_data.get('location'),
                device_type=usage_data.get('device_type'),
                revenue_generated=0.0,  # Will be calculated
                metadata=usage_data.get('metadata', {})
            )
            
            # Calculate revenue for this usage
            revenue = self._calculate_usage_revenue(usage_record)
            usage_record.revenue_generated = revenue
            
            # Store usage record
            self.usage_tracking.append(usage_record)
            
            # Update license usage limits
            if usage_record.license_id:
                self._update_license_usage(usage_record.license_id, usage_record)
                
            logger.debug(f"Tracked usage {tracking_id} with revenue ${revenue:.4f}")
            return usage_record
            
        except Exception as e:
            logger.error(f"Usage tracking failed: {str(e)}")
            raise
            
    def calculate_royalties(self, content_id: str, 
                          period: Tuple[datetime, datetime]) -> Dict:
        """
        Calculate royalties and revenue for content in given period
        
        Args:
            content_id: Content identifier
            period: Date range tuple (start, end)
            
        Returns:
            Detailed royalty calculation
        """
        try:
            start_date, end_date = period
            
            # Filter usage records for period
            period_usage = [
                usage for usage in self.usage_tracking
                if usage.content_id == content_id and 
                start_date <= usage.timestamp <= end_date
            ]
            
            # Calculate totals by platform and usage type
            platform_revenue = {}
            usage_type_revenue = {}
            geographic_revenue = {}
            
            total_revenue = 0.0
            total_views = 0
            unique_users = set()
            
            for usage in period_usage:
                revenue = usage.revenue_generated
                total_revenue += revenue
                total_views += usage.views
                
                if usage.user_id:
                    unique_users.add(usage.user_id)
                    
                # Platform breakdown
                platform = usage.platform
                if platform not in platform_revenue:
                    platform_revenue[platform] = {'revenue': 0.0, 'views': 0}
                platform_revenue[platform]['revenue'] += revenue
                platform_revenue[platform]['views'] += usage.views
                
                # Usage type breakdown
                usage_type = usage.usage_type.value
                if usage_type not in usage_type_revenue:
                    usage_type_revenue[usage_type] = {'revenue': 0.0, 'views': 0}
                usage_type_revenue[usage_type]['revenue'] += revenue
                usage_type_revenue[usage_type]['views'] += usage.views
                
                # Geographic breakdown
                location = usage.geographic_location or 'unknown'
                if location not in geographic_revenue:
                    geographic_revenue[location] = {'revenue': 0.0, 'views': 0}
                geographic_revenue[location]['revenue'] += revenue
                geographic_revenue[location]['views'] += usage.views
                
            # Calculate revenue distribution
            revenue_distribution = self._calculate_revenue_distribution(
                content_id, total_revenue)
                
            # Generate performance metrics
            metrics = self._calculate_performance_metrics(
                content_id, period_usage, total_revenue)
                
            return {
                'content_id': content_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_revenue': total_revenue,
                    'total_views': total_views,
                    'unique_users': len(unique_users),
                    'average_revenue_per_view': total_revenue / total_views if total_views > 0 else 0.0,
                    'usage_records': len(period_usage)
                },
                'breakdowns': {
                    'platforms': platform_revenue,
                    'usage_types': usage_type_revenue,
                    'geographic': geographic_revenue
                },
                'revenue_distribution': revenue_distribution,
                'performance_metrics': metrics,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Royalty calculation failed: {str(e)}")
            return {'error': str(e)}
            
    def optimize_pricing_strategy(self, content_id: str) -> Dict:
        """
        AI-powered pricing optimization based on performance data
        
        Args:
            content_id: Content identifier
            
        Returns:
            Pricing optimization recommendations
        """
        try:
            # Analyze historical performance
            historical_data = self._analyze_historical_performance(content_id)
            
            # Market analysis
            market_analysis = self._perform_market_analysis(content_id)
            
            # Generate pricing recommendations
            recommendations = self._generate_pricing_recommendations(
                historical_data, market_analysis)
                
            # Calculate potential revenue impact
            revenue_impact = self._calculate_pricing_impact(
                content_id, recommendations)
                
            return {
                'content_id': content_id,
                'current_performance': historical_data,
                'market_insights': market_analysis,
                'recommendations': recommendations,
                'revenue_impact': revenue_impact,
                'optimization_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pricing optimization failed: {str(e)}")
            return {'error': str(e)}
            
    def manage_license_compliance(self, license_id: str) -> Dict:
        """
        Monitor and enforce license compliance
        
        Args:
            license_id: License identifier
            
        Returns:
            Compliance status and actions
        """
        try:
            if license_id not in self.licenses:
                return {'error': 'License not found'}
                
            license_obj = self.licenses[license_id]
            
            # Check license expiration
            compliance_issues = []
            if license_obj.is_expired:
                compliance_issues.append({
                    'type': 'expired_license',
                    'severity': 'high',
                    'message': f'License expired on {license_obj.expires_at}'
                })
                
            # Check usage limits
            usage_violations = self._check_usage_limit_violations(license_obj)
            compliance_issues.extend(usage_violations)
            
            # Check territorial restrictions
            territory_violations = self._check_territorial_violations(license_obj)
            compliance_issues.extend(territory_violations)
            
            # Check revenue share compliance
            revenue_issues = self._check_revenue_compliance(license_obj)
            compliance_issues.extend(revenue_issues)
            
            # Generate compliance report
            compliance_status = 'compliant' if not compliance_issues else 'violations_detected'
            
            # Take automated actions if configured
            automated_actions = []
            if compliance_issues:
                automated_actions = self._take_compliance_actions(license_obj, compliance_issues)
                
            return {
                'license_id': license_id,
                'compliance_status': compliance_status,
                'issues_found': len(compliance_issues),
                'compliance_issues': compliance_issues,
                'automated_actions': automated_actions,
                'days_remaining': license_obj.days_remaining,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"License compliance check failed: {str(e)}")
            return {'error': str(e)}
            
    # Private helper methods
    
    def _create_license_monetization_rules(self, license: License, config: Dict):
        """Create monetization rules for granted license"""
        if 'monetization' in config:
            monetization_config = config['monetization']
            monetization_config['content_id'] = self.rights_bundles[license.rights_bundle_id].content_id
            self.setup_monetization_strategy(
                monetization_config['content_id'], 
                {'platforms': [monetization_config]}
            )
            
    def _calculate_usage_revenue(self, usage: UsageTracking) -> float:
        """Calculate revenue for specific usage"""
        content_id = usage.content_id
        platform = usage.platform
        
        # Get monetization rules for content and platform
        rules = self.monetization_rules.get(content_id, [])
        platform_rule = next((r for r in rules if r.platform == platform), None)
        
        if not platform_rule:
            return 0.0
            
        # Base revenue calculation
        base_revenue = 0.01  # Base rate per view
        
        # Apply geographic pricing
        if usage.geographic_location in platform_rule.geographic_pricing:
            base_revenue *= platform_rule.geographic_pricing[usage.geographic_location]
            
        # Apply premium multiplier
        base_revenue *= platform_rule.premium_multiplier
        
        # Calculate final revenue
        total_revenue = base_revenue * usage.views
        creator_revenue = total_revenue * platform_rule.revenue_share_creator
        
        return creator_revenue
        
    def _update_license_usage(self, license_id: str, usage: UsageTracking):
        """Update license usage limits"""
        if license_id in self.licenses:
            license_obj = self.licenses[license_id]
            # Update usage tracking in license metadata
            if 'usage_tracking' not in license_obj.restrictions:
                license_obj.restrictions['usage_tracking'] = []
            license_obj.restrictions['usage_tracking'].append({
                'tracking_id': usage.tracking_id,
                'timestamp': usage.timestamp.isoformat(),
                'views': usage.views
            })
            
    def _calculate_revenue_distribution(self, content_id: str, total_revenue: float) -> Dict:
        """Calculate revenue distribution among stakeholders"""
        # Get all licenses for content
        content_licenses = [
            license for license in self.licenses.values()
            if self.rights_bundles[license.rights_bundle_id].content_id == content_id
        ]
        
        distribution = {
            'creator_share': 0.0,
            'platform_shares': {},
            'license_royalties': {}
        }
        
        # Calculate distribution based on monetization rules and licenses
        rules = self.monetization_rules.get(content_id, [])
        
        for rule in rules:
            platform_revenue = total_revenue * (rule.revenue_share_creator + rule.revenue_share_platform)
            distribution['creator_share'] += total_revenue * rule.revenue_share_creator
            distribution['platform_shares'][rule.platform] = total_revenue * rule.revenue_share_platform
            
        return distribution
        
    def _calculate_performance_metrics(self, content_id: str, usage_records: List[UsageTracking], 
                                     total_revenue: float) -> Dict:
        """Calculate performance metrics for content"""
        if not usage_records:
            return {}
            
        metrics = {
            'engagement_rate': 0.0,
            'retention_rate': 0.0,
            'conversion_rate': 0.0,
            'revenue_growth_rate': 0.0,
            'top_performing_platform': '',
            'audience_demographics': {}
        }
        
        # Calculate platform performance
        platform_performance = {}
        for usage in usage_records:
            platform = usage.platform
            if platform not in platform_performance:
                platform_performance[platform] = {'revenue': 0.0, 'views': 0}
            platform_performance[platform]['revenue'] += usage.revenue_generated
            platform_performance[platform]['views'] += usage.views
            
        if platform_performance:
            top_platform = max(platform_performance.items(), key=lambda x: x[1]['revenue'])
            metrics['top_performing_platform'] = top_platform[0]
            
        return metrics
        
    def _dynamic_pricing_strategy(self, content_id: str, config: Dict) -> Dict:
        """Implement dynamic pricing strategy"""
        return {
            'strategy': 'dynamic',
            'factors': ['demand', 'competition', 'time_of_day', 'geographic_location'],
            'adjustment_frequency': 'hourly'
        }
        
    def _fixed_pricing_strategy(self, content_id: str, config: Dict) -> Dict:
        """Implement fixed pricing strategy"""
        return {
            'strategy': 'fixed',
            'base_price': config.get('base_price', 1.0),
            'currency': config.get('currency', 'USD')
        }
        
    def _tiered_pricing_strategy(self, content_id: str, config: Dict) -> Dict:
        """Implement tiered pricing strategy"""
        return {
            'strategy': 'tiered',
            'tiers': config.get('tiers', {
                'basic': 0.5,
                'premium': 1.0,
                'enterprise': 2.0
            })
        }
        
    def _auction_pricing_strategy(self, content_id: str, config: Dict) -> Dict:
        """Implement auction-based pricing strategy"""
        return {
            'strategy': 'auction',
            'reserve_price': config.get('reserve_price', 0.1),
            'auction_duration': config.get('auction_duration', 24)  # hours
        }
        
    def _estimate_revenue_potential(self, content_id: str) -> Dict:
        """Estimate revenue potential for content"""
        return {
            'daily_estimate': 10.0,
            'monthly_estimate': 300.0,
            'annual_estimate': 3600.0,
            'confidence': 0.7
        }
        
    def _analyze_historical_performance(self, content_id: str) -> Dict:
        """Analyze historical performance data"""
        content_usage = [u for u in self.usage_tracking if u.content_id == content_id]
        
        if not content_usage:
            return {'no_data': True}
            
        total_revenue = sum(u.revenue_generated for u in content_usage)
        total_views = sum(u.views for u in content_usage)
        
        return {
            'total_revenue': total_revenue,
            'total_views': total_views,
            'average_revenue_per_view': total_revenue / total_views if total_views > 0 else 0.0,
            'performance_trend': 'stable'  # Would be calculated from time series
        }
        
    def _perform_market_analysis(self, content_id: str) -> Dict:
        """Perform market analysis for pricing optimization"""
        return {
            'market_demand': 'moderate',
            'competition_level': 'medium',
            'price_elasticity': 0.8,
            'seasonal_factors': []
        }
        
    def _generate_pricing_recommendations(self, historical_data: Dict, market_analysis: Dict) -> Dict:
        """Generate AI-powered pricing recommendations"""
        return {
            'recommended_strategy': 'dynamic',
            'price_adjustments': {
                'peak_hours': 1.2,
                'off_peak': 0.8,
                'high_demand_regions': 1.5
            },
            'expected_revenue_increase': 15.0  # percentage
        }
        
    def _calculate_pricing_impact(self, content_id: str, recommendations: Dict) -> Dict:
        """Calculate potential revenue impact of pricing changes"""
        return {
            'current_monthly_revenue': 300.0,
            'projected_monthly_revenue': 345.0,
            'revenue_increase': 45.0,
            'roi_percentage': 15.0
        }
        
    def _check_usage_limit_violations(self, license: License) -> List[Dict]:
        """Check for usage limit violations"""
        violations = []
        
        if license.usage_limits:
            # Check against actual usage
            license_usage = [u for u in self.usage_tracking if u.license_id == license.license_id]
            total_views = sum(u.views for u in license_usage)
            
            if 'max_views' in license.usage_limits and total_views > license.usage_limits['max_views']:
                violations.append({
                    'type': 'usage_limit_exceeded',
                    'severity': 'high',
                    'message': f'View limit exceeded: {total_views}/{license.usage_limits["max_views"]}'
                })
                
        return violations
        
    def _check_territorial_violations(self, license: License) -> List[Dict]:
        """Check for territorial usage violations"""
        violations = []
        
        license_usage = [u for u in self.usage_tracking 
                        if u.license_id == license.license_id and u.geographic_location]
        
        for usage in license_usage:
            if usage.geographic_location not in license.territory:
                violations.append({
                    'type': 'territorial_violation',
                    'severity': 'medium',
                    'message': f'Usage detected in unauthorized territory: {usage.geographic_location}'
                })
                
        return violations
        
    def _check_revenue_compliance(self, license: License) -> List[Dict]:
        """Check revenue sharing compliance"""
        violations = []
        
        # Check if minimum guarantee is met
        license_usage = [u for u in self.usage_tracking if u.license_id == license.license_id]
        total_revenue = sum(u.revenue_generated for u in license_usage)
        
        if license.minimum_guarantee > 0 and total_revenue < license.minimum_guarantee:
            violations.append({
                'type': 'minimum_guarantee_not_met',
                'severity': 'medium',
                'message': f'Minimum guarantee not met: ${total_revenue:.2f}/${license.minimum_guarantee:.2f}'
            })
            
        return violations
        
    def _take_compliance_actions(self, license: License, issues: List[Dict]) -> List[Dict]:
        """Take automated compliance actions"""
        actions = []
        
        for issue in issues:
            if issue['type'] == 'expired_license':
                # Suspend license
                license.status = 'expired'
                actions.append({
                    'action': 'license_suspended',
                    'reason': 'license_expired'
                })
            elif issue['type'] == 'usage_limit_exceeded':
                # Temporary suspension
                license.status = 'suspended'
                actions.append({
                    'action': 'usage_suspended',
                    'reason': 'limit_exceeded'
                })
                
        return actions
