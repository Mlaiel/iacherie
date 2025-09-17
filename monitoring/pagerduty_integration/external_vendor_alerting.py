"""
External Vendor Alerting for PagerDuty - Ainflue Platform
Third-party service monitoring and vendor SLA tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

try:
    import requests
    import aiohttp
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None
    aiohttp = None

logger = logging.getLogger(__name__)


class VendorType(Enum):
    """Types of external vendors"""
    CLOUD_PROVIDER = "cloud_provider"
    PAYMENT_PROCESSOR = "payment_processor"
    CONTENT_DELIVERY = "content_delivery"
    ANALYTICS_PLATFORM = "analytics_platform"
    SOCIAL_MEDIA_API = "social_media_api"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    STORAGE_SERVICE = "storage_service"
    DATABASE_SERVICE = "database_service"
    MONITORING_SERVICE = "monitoring_service"


class ServiceStatus(Enum):
    """External service status"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class SLABreachSeverity(Enum):
    """SLA breach severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class VendorEndpoint:
    """External vendor endpoint configuration"""
    vendor_name: str
    vendor_type: VendorType
    endpoint_url: str
    api_key: Optional[str]
    health_check_url: str
    status_page_url: Optional[str]
    timeout_seconds: int
    check_interval_minutes: int
    sla_uptime_percentage: float
    sla_response_time_ms: int
    contact_info: Dict[str, str]
    business_criticality: str
    metadata: Dict[str, Any]


@dataclass
class VendorHealthCheck:
    """Vendor health check result"""
    vendor_name: str
    check_id: str
    timestamp: datetime
    status: ServiceStatus
    response_time_ms: float
    error_message: Optional[str]
    http_status_code: Optional[int]
    availability_percentage: float
    consecutive_failures: int
    last_success: Optional[datetime]
    sla_breach: bool
    details: Dict[str, Any]


@dataclass
class SLAMetrics:
    """SLA tracking metrics"""
    vendor_name: str
    period_start: datetime
    period_end: datetime
    total_checks: int
    successful_checks: int
    failed_checks: int
    availability_percentage: float
    average_response_time: float
    max_response_time: float
    min_response_time: float
    sla_target_availability: float
    sla_target_response_time: float
    sla_breach_count: int
    sla_credits_owed: float
    business_impact_score: float


@dataclass
class VendorAlert:
    """Vendor-related alert"""
    alert_id: str
    vendor_name: str
    vendor_type: VendorType
    alert_type: str
    severity: SLABreachSeverity
    message: str
    details: Dict[str, Any]
    sla_breach: bool
    business_impact: str
    affected_creator_features: List[str]
    escalation_required: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    pagerduty_incident_id: Optional[str]


class ExternalVendorAlerting:
    """
    External vendor monitoring and alerting system
    Tracks SLAs, health checks, and business impact for Creator Economy
    """
    
    def __init__(self, pagerduty_client=None):
        """Initialize external vendor alerting"""
        self.pagerduty_client = pagerduty_client
        self.vendor_endpoints = {}
        self.health_check_history = {}
        self.sla_metrics = {}
        self.active_alerts = {}
        self.vendor_dependencies = {}
        
        # Initialize vendor configurations
        self._initialize_vendor_endpoints()
        
        # Configuration
        self.config = {
            "health_check_timeout": 30,  # seconds
            "consecutive_failure_threshold": 3,
            "sla_breach_threshold": 0.99,  # 99% uptime
            "response_time_threshold": 2000,  # 2 seconds
            "business_impact_weights": {
                "creator_uploads": 0.3,
                "content_processing": 0.25,
                "monetization": 0.2,
                "collaboration": 0.15,
                "analytics": 0.1
            }
        }
        
        logger.info("External Vendor Alerting initialized")
    
    def _initialize_vendor_endpoints(self):
        """Initialize Creator Economy vendor endpoints"""
        
        # Cloud Infrastructure Vendors
        self.vendor_endpoints["aws"] = VendorEndpoint(
            vendor_name="aws",
            vendor_type=VendorType.CLOUD_PROVIDER,
            endpoint_url="https://aws.amazon.com",
            api_key=None,
            health_check_url="https://status.aws.amazon.com/rss/ec2-us-east-1.rss",
            status_page_url="https://status.aws.amazon.com",
            timeout_seconds=30,
            check_interval_minutes=5,
            sla_uptime_percentage=99.9,
            sla_response_time_ms=1000,
            contact_info={"support": "aws-support", "account_manager": "aws-tam"},
            business_criticality="critical",
            metadata={"region": "us-east-1", "services": ["ec2", "s3", "rds"]}
        )
        
        # Payment Processing
        self.vendor_endpoints["stripe"] = VendorEndpoint(
            vendor_name="stripe",
            vendor_type=VendorType.PAYMENT_PROCESSOR,
            endpoint_url="https://api.stripe.com",
            api_key="sk_live_...",
            health_check_url="https://api.stripe.com/v1/account",
            status_page_url="https://status.stripe.com",
            timeout_seconds=15,
            check_interval_minutes=2,
            sla_uptime_percentage=99.95,
            sla_response_time_ms=500,
            contact_info={"support": "stripe-support", "integration": "stripe-dev"},
            business_criticality="critical",
            metadata={"features": ["payments", "payouts", "subscriptions"]}
        )
        
        # Content Delivery Network
        self.vendor_endpoints["cloudflare"] = VendorEndpoint(
            vendor_name="cloudflare",
            vendor_type=VendorType.CONTENT_DELIVERY,
            endpoint_url="https://api.cloudflare.com",
            api_key="cf_api_key",
            health_check_url="https://api.cloudflare.com/client/v4/user",
            status_page_url="https://www.cloudflarestatus.com",
            timeout_seconds=20,
            check_interval_minutes=3,
            sla_uptime_percentage=99.9,
            sla_response_time_ms=200,
            contact_info={"support": "cloudflare-support", "enterprise": "cf-enterprise"},
            business_criticality="high",
            metadata={"features": ["cdn", "security", "analytics"]}
        )
        
        # Social Media APIs
        social_platforms = [
            ("youtube", "YouTube Data API", "https://www.googleapis.com/youtube/v3"),
            ("instagram", "Instagram Basic Display API", "https://graph.instagram.com"),
            ("tiktok", "TikTok API", "https://open-api.tiktok.com"),
            ("twitter", "Twitter API v2", "https://api.twitter.com/2"),
            ("linkedin", "LinkedIn API", "https://api.linkedin.com/v2")
        ]
        
        for platform_id, platform_name, api_url in social_platforms:
            self.vendor_endpoints[platform_id] = VendorEndpoint(
                vendor_name=platform_id,
                vendor_type=VendorType.SOCIAL_MEDIA_API,
                endpoint_url=api_url,
                api_key=f"{platform_id}_api_key",
                health_check_url=f"{api_url}/health",
                status_page_url=f"https://{platform_id}status.com",
                timeout_seconds=25,
                check_interval_minutes=5,
                sla_uptime_percentage=99.5,
                sla_response_time_ms=1500,
                contact_info={"support": f"{platform_id}-developer-support"},
                business_criticality="high",
                metadata={"platform": platform_name, "features": ["analytics", "publishing"]}
            )
        
        # Email Service
        self.vendor_endpoints["sendgrid"] = VendorEndpoint(
            vendor_name="sendgrid",
            vendor_type=VendorType.EMAIL_SERVICE,
            endpoint_url="https://api.sendgrid.com",
            api_key="sendgrid_api_key",
            health_check_url="https://api.sendgrid.com/v3/user/profile",
            status_page_url="https://status.sendgrid.com",
            timeout_seconds=15,
            check_interval_minutes=5,
            sla_uptime_percentage=99.9,
            sla_response_time_ms=1000,
            contact_info={"support": "sendgrid-support"},
            business_criticality="medium",
            metadata={"features": ["transactional", "marketing", "analytics"]}
        )
        
        # Database Services
        self.vendor_endpoints["mongodb_atlas"] = VendorEndpoint(
            vendor_name="mongodb_atlas",
            vendor_type=VendorType.DATABASE_SERVICE,
            endpoint_url="https://cloud.mongodb.com",
            api_key="mongodb_api_key",
            health_check_url="https://cloud.mongodb.com/api/atlas/v1.0/groups",
            status_page_url="https://status.mongodb.com",
            timeout_seconds=20,
            check_interval_minutes=3,
            sla_uptime_percentage=99.95,
            sla_response_time_ms=100,
            contact_info={"support": "mongodb-support", "account": "mongodb-account"},
            business_criticality="critical",
            metadata={"cluster": "creator-platform", "region": "us-east-1"}
        )
        
        # Analytics Platform
        self.vendor_endpoints["mixpanel"] = VendorEndpoint(
            vendor_name="mixpanel",
            vendor_type=VendorType.ANALYTICS_PLATFORM,
            endpoint_url="https://api.mixpanel.com",
            api_key="mixpanel_api_key",
            health_check_url="https://api.mixpanel.com/engage",
            status_page_url="https://status.mixpanel.com",
            timeout_seconds=20,
            check_interval_minutes=10,
            sla_uptime_percentage=99.5,
            sla_response_time_ms=800,
            contact_info={"support": "mixpanel-support"},
            business_criticality="medium",
            metadata={"features": ["events", "funnel", "retention"]}
        )
    
    async def perform_health_checks(self) -> Dict[str, VendorHealthCheck]:
        """Perform health checks on all vendor endpoints"""
        health_results = {}
        
        if not REQUESTS_AVAILABLE:
            logger.warning("HTTP client not available for health checks")
            return health_results
        
        try:
            # Create session for concurrent checks
            timeout = aiohttp.ClientTimeout(total=self.config["health_check_timeout"])
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                tasks = []
                
                for vendor_name, endpoint in self.vendor_endpoints.items():
                    task = self._check_vendor_health(session, vendor_name, endpoint)
                    tasks.append(task)
                
                # Execute health checks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    vendor_name = list(self.vendor_endpoints.keys())[i]
                    
                    if isinstance(result, Exception):
                        logger.error(f"Health check failed for {vendor_name}: {result}")
                        # Create failed health check
                        result = VendorHealthCheck(
                            vendor_name=vendor_name,
                            check_id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            status=ServiceStatus.UNKNOWN,
                            response_time_ms=0.0,
                            error_message=str(result),
                            http_status_code=None,
                            availability_percentage=0.0,
                            consecutive_failures=1,
                            last_success=None,
                            sla_breach=True,
                            details={"error": "Health check exception"}
                        )
                    
                    health_results[vendor_name] = result
                    
                    # Store in history
                    if vendor_name not in self.health_check_history:
                        self.health_check_history[vendor_name] = []
                    self.health_check_history[vendor_name].append(result)
                    
                    # Keep only last 1000 checks
                    if len(self.health_check_history[vendor_name]) > 1000:
                        self.health_check_history[vendor_name] = self.health_check_history[vendor_name][-1000:]
            
            logger.info(f"Health checks completed for {len(health_results)} vendors")
            
            # Process results and generate alerts
            await self._process_health_check_results(health_results)
            
            return health_results
            
        except Exception as e:
            logger.error(f"Health checks failed: {e}")
            return health_results
    
    async def _check_vendor_health(self, session: aiohttp.ClientSession, 
                                 vendor_name: str, endpoint: VendorEndpoint) -> VendorHealthCheck:
        """Check health of individual vendor"""
        start_time = datetime.utcnow()
        
        try:
            # Prepare headers
            headers = {"User-Agent": "Ainflue-Platform/1.0"}
            if endpoint.api_key:
                if "stripe" in vendor_name:
                    headers["Authorization"] = f"Bearer {endpoint.api_key}"
                elif "sendgrid" in vendor_name:
                    headers["Authorization"] = f"Bearer {endpoint.api_key}"
                else:
                    headers["X-API-Key"] = endpoint.api_key
            
            # Perform health check
            async with session.get(endpoint.health_check_url, headers=headers) as response:
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                # Determine status
                status = ServiceStatus.OPERATIONAL
                if response.status >= 500:
                    status = ServiceStatus.MAJOR_OUTAGE
                elif response.status >= 400:
                    status = ServiceStatus.DEGRADED
                elif response_time > endpoint.sla_response_time_ms:
                    status = ServiceStatus.DEGRADED
                
                # Calculate availability
                recent_checks = self.health_check_history.get(vendor_name, [])[-100:]
                successful_checks = sum(1 for check in recent_checks 
                                      if check.status == ServiceStatus.OPERATIONAL)
                availability = (successful_checks / len(recent_checks) * 100) if recent_checks else 100.0
                
                # Check for consecutive failures
                consecutive_failures = 0
                for check in reversed(recent_checks):
                    if check.status != ServiceStatus.OPERATIONAL:
                        consecutive_failures += 1
                    else:
                        break
                
                # SLA breach check
                sla_breach = (
                    availability < endpoint.sla_uptime_percentage or
                    response_time > endpoint.sla_response_time_ms or
                    consecutive_failures >= self.config["consecutive_failure_threshold"]
                )
                
                return VendorHealthCheck(
                    vendor_name=vendor_name,
                    check_id=str(uuid.uuid4()),
                    timestamp=start_time,
                    status=status,
                    response_time_ms=response_time,
                    error_message=None if response.status < 400 else f"HTTP {response.status}",
                    http_status_code=response.status,
                    availability_percentage=availability,
                    consecutive_failures=consecutive_failures,
                    last_success=start_time if status == ServiceStatus.OPERATIONAL else None,
                    sla_breach=sla_breach,
                    details={
                        "url": endpoint.health_check_url,
                        "response_headers": dict(response.headers),
                        "vendor_type": endpoint.vendor_type.value
                    }
                )
                
        except asyncio.TimeoutError:
            return VendorHealthCheck(
                vendor_name=vendor_name,
                check_id=str(uuid.uuid4()),
                timestamp=start_time,
                status=ServiceStatus.MAJOR_OUTAGE,
                response_time_ms=endpoint.timeout_seconds * 1000,
                error_message="Request timeout",
                http_status_code=None,
                availability_percentage=0.0,
                consecutive_failures=1,
                last_success=None,
                sla_breach=True,
                details={"error": "timeout", "timeout_seconds": endpoint.timeout_seconds}
            )
            
        except Exception as e:
            return VendorHealthCheck(
                vendor_name=vendor_name,
                check_id=str(uuid.uuid4()),
                timestamp=start_time,
                status=ServiceStatus.UNKNOWN,
                response_time_ms=0.0,
                error_message=str(e),
                http_status_code=None,
                availability_percentage=0.0,
                consecutive_failures=1,
                last_success=None,
                sla_breach=True,
                details={"error": "exception", "exception_type": type(e).__name__}
            )
    
    async def _process_health_check_results(self, health_results: Dict[str, VendorHealthCheck]):
        """Process health check results and generate alerts"""
        try:
            for vendor_name, health_check in health_results.items():
                endpoint = self.vendor_endpoints.get(vendor_name)
                if not endpoint:
                    continue
                
                # Check if alert should be generated
                should_alert = (
                    health_check.sla_breach or
                    health_check.status in [ServiceStatus.MAJOR_OUTAGE, ServiceStatus.PARTIAL_OUTAGE] or
                    health_check.consecutive_failures >= self.config["consecutive_failure_threshold"]
                )
                
                if should_alert:
                    await self._generate_vendor_alert(vendor_name, health_check, endpoint)
                else:
                    # Check if existing alert should be resolved
                    await self._check_alert_resolution(vendor_name, health_check)
            
        except Exception as e:
            logger.error(f"Processing health check results failed: {e}")
    
    async def _generate_vendor_alert(self, vendor_name: str, 
                                   health_check: VendorHealthCheck, 
                                   endpoint: VendorEndpoint):
        """Generate alert for vendor issue"""
        try:
            # Determine severity
            severity = SLABreachSeverity.MINOR
            if health_check.status == ServiceStatus.MAJOR_OUTAGE:
                severity = SLABreachSeverity.CRITICAL
            elif health_check.consecutive_failures >= 5:
                severity = SLABreachSeverity.MAJOR
            elif health_check.sla_breach:
                severity = SLABreachSeverity.MODERATE
            
            # Calculate business impact
            business_impact = self._calculate_business_impact(vendor_name, endpoint, health_check)
            
            # Get affected Creator features
            affected_features = self._get_affected_creator_features(vendor_name, endpoint.vendor_type)
            
            alert = VendorAlert(
                alert_id=str(uuid.uuid4()),
                vendor_name=vendor_name,
                vendor_type=endpoint.vendor_type,
                alert_type="vendor_health_issue",
                severity=severity,
                message=f"Vendor {vendor_name} experiencing issues: {health_check.error_message or 'SLA breach'}",
                details={
                    "health_check": asdict(health_check),
                    "endpoint": asdict(endpoint),
                    "business_impact_score": business_impact["score"],
                    "estimated_revenue_impact": business_impact["revenue_impact"]
                },
                sla_breach=health_check.sla_breach,
                business_impact=business_impact["description"],
                affected_creator_features=affected_features,
                escalation_required=severity in [SLABreachSeverity.MAJOR, SLABreachSeverity.CRITICAL],
                created_at=datetime.utcnow(),
                resolved_at=None,
                pagerduty_incident_id=None
            )
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Trigger PagerDuty incident
            if self.pagerduty_client:
                await self._trigger_vendor_pagerduty_incident(alert)
            
            logger.warning(f"Generated {severity.value} alert for vendor {vendor_name}")
            
        except Exception as e:
            logger.error(f"Generating vendor alert failed: {e}")
    
    def _calculate_business_impact(self, vendor_name: str, 
                                 endpoint: VendorEndpoint, 
                                 health_check: VendorHealthCheck) -> Dict[str, Any]:
        """Calculate business impact of vendor issue"""
        try:
            impact_score = 0.0
            revenue_impact = 0.0
            
            # Base impact by vendor type and criticality
            criticality_multiplier = {
                "critical": 1.0,
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2
            }.get(endpoint.business_criticality, 0.1)
            
            # Vendor type specific impact
            type_impact = {
                VendorType.PAYMENT_PROCESSOR: 0.9,  # High revenue impact
                VendorType.CLOUD_PROVIDER: 0.8,     # High availability impact
                VendorType.SOCIAL_MEDIA_API: 0.6,   # Medium creator feature impact
                VendorType.CONTENT_DELIVERY: 0.5,   # Medium performance impact
                VendorType.DATABASE_SERVICE: 0.8,   # High data impact
                VendorType.EMAIL_SERVICE: 0.3,      # Low immediate impact
                VendorType.ANALYTICS_PLATFORM: 0.2  # Low immediate impact
            }.get(endpoint.vendor_type, 0.1)
            
            # Severity multiplier
            severity_multiplier = {
                ServiceStatus.MAJOR_OUTAGE: 1.0,
                ServiceStatus.PARTIAL_OUTAGE: 0.6,
                ServiceStatus.DEGRADED: 0.3,
                ServiceStatus.MAINTENANCE: 0.1
            }.get(health_check.status, 0.1)
            
            impact_score = criticality_multiplier * type_impact * severity_multiplier
            
            # Estimate revenue impact (example: $1000/hour for critical payment issues)
            if endpoint.vendor_type == VendorType.PAYMENT_PROCESSOR and impact_score > 0.5:
                revenue_impact = 1000.0 * impact_score  # $1000/hour base
            elif endpoint.vendor_type == VendorType.CLOUD_PROVIDER and impact_score > 0.7:
                revenue_impact = 500.0 * impact_score   # $500/hour for cloud issues
            else:
                revenue_impact = 100.0 * impact_score   # Base revenue impact
            
            # Impact description
            if impact_score > 0.8:
                description = "Critical business impact - immediate attention required"
            elif impact_score > 0.6:
                description = "High business impact - escalation recommended"
            elif impact_score > 0.3:
                description = "Moderate business impact - monitoring required"
            else:
                description = "Low business impact - informational"
            
            return {
                "score": impact_score,
                "revenue_impact": revenue_impact,
                "description": description,
                "criticality": endpoint.business_criticality,
                "vendor_type": endpoint.vendor_type.value
            }
            
        except Exception as e:
            logger.error(f"Calculating business impact failed: {e}")
            return {"score": 0.0, "revenue_impact": 0.0, "description": "Unknown impact"}
    
    def _get_affected_creator_features(self, vendor_name: str, vendor_type: VendorType) -> List[str]:
        """Get Creator Economy features affected by vendor issue"""
        affected_features = []
        
        # Map vendor types to Creator features
        feature_mapping = {
            VendorType.PAYMENT_PROCESSOR: [
                "creator_payouts", "brand_payments", "subscription_billing", 
                "tip_processing", "revenue_analytics"
            ],
            VendorType.CLOUD_PROVIDER: [
                "content_upload", "video_processing", "image_processing", 
                "ai_protection", "content_storage", "backup_systems"
            ],
            VendorType.CONTENT_DELIVERY: [
                "content_delivery", "global_distribution", "streaming", 
                "download_speeds", "geographic_access"
            ],
            VendorType.SOCIAL_MEDIA_API: [
                "social_publishing", "cross_platform_posting", "analytics_sync", 
                "audience_insights", "engagement_tracking"
            ],
            VendorType.EMAIL_SERVICE: [
                "creator_notifications", "collaboration_emails", "marketing_campaigns", 
                "transactional_emails", "newsletter_delivery"
            ],
            VendorType.DATABASE_SERVICE: [
                "user_profiles", "content_metadata", "collaboration_data", 
                "analytics_storage", "backup_recovery"
            ],
            VendorType.ANALYTICS_PLATFORM: [
                "performance_analytics", "creator_insights", "revenue_tracking", 
                "audience_analytics", "engagement_metrics"
            ]
        }
        
        # Platform-specific features
        platform_features = {
            "youtube": ["youtube_analytics", "youtube_publishing", "youtube_monetization"],
            "instagram": ["instagram_stories", "instagram_reels", "instagram_shopping"],
            "tiktok": ["tiktok_publishing", "tiktok_analytics", "tiktok_trends"],
            "twitter": ["twitter_publishing", "twitter_analytics", "twitter_engagement"],
            "linkedin": ["linkedin_publishing", "linkedin_analytics", "professional_networking"]
        }
        
        # Get features by vendor type
        if vendor_type in feature_mapping:
            affected_features.extend(feature_mapping[vendor_type])
        
        # Get platform-specific features
        if vendor_name in platform_features:
            affected_features.extend(platform_features[vendor_name])
        
        return affected_features
    
    async def _trigger_vendor_pagerduty_incident(self, alert: VendorAlert):
        """Trigger PagerDuty incident for vendor alert"""
        try:
            if not self.pagerduty_client:
                return
            
            incident_details = {
                "summary": f"Vendor Alert: {alert.vendor_name} - {alert.message}",
                "source": f"vendor/{alert.vendor_name}",
                "severity": alert.severity.value,
                "component": alert.vendor_name,
                "group": "external-vendors",
                "class": "vendor_sla_breach" if alert.sla_breach else "vendor_health",
                "custom_details": {
                    "vendor_type": alert.vendor_type.value,
                    "business_impact": alert.business_impact,
                    "affected_features": alert.affected_creator_features,
                    "sla_breach": alert.sla_breach,
                    "escalation_required": alert.escalation_required,
                    "alert_details": alert.details
                }
            }
            
            incident_key = await self.pagerduty_client.trigger_incident(
                incident_details,
                dedup_key=f"vendor-{alert.vendor_name}-{alert.alert_type}"
            )
            
            if incident_key:
                alert.pagerduty_incident_id = incident_key
                logger.info(f"PagerDuty incident {incident_key} created for vendor alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"PagerDuty vendor incident creation failed: {e}")
    
    async def _check_alert_resolution(self, vendor_name: str, health_check: VendorHealthCheck):
        """Check if existing alerts should be resolved"""
        try:
            # Find active alerts for this vendor
            vendor_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.vendor_name == vendor_name and not alert.resolved_at
            ]
            
            # Check if vendor is healthy now
            if (health_check.status == ServiceStatus.OPERATIONAL and 
                not health_check.sla_breach and 
                health_check.consecutive_failures == 0):
                
                for alert in vendor_alerts:
                    # Resolve alert
                    alert.resolved_at = datetime.utcnow()
                    
                    # Resolve PagerDuty incident
                    if alert.pagerduty_incident_id and self.pagerduty_client:
                        await self.pagerduty_client.resolve_incident(
                            alert.pagerduty_incident_id,
                            resolver="Ainflue Vendor Monitor",
                            resolution_details=f"Vendor {vendor_name} health restored"
                        )
                    
                    logger.info(f"Resolved vendor alert {alert.alert_id} for {vendor_name}")
            
        except Exception as e:
            logger.error(f"Checking alert resolution failed: {e}")
    
    async def calculate_sla_metrics(self, vendor_name: str, 
                                  period_days: int = 30) -> Optional[SLAMetrics]:
        """Calculate SLA metrics for vendor over specified period"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            # Get health check history for period
            vendor_history = self.health_check_history.get(vendor_name, [])
            period_checks = [
                check for check in vendor_history
                if start_time <= check.timestamp <= end_time
            ]
            
            if not period_checks:
                return None
            
            # Calculate metrics
            total_checks = len(period_checks)
            successful_checks = sum(
                1 for check in period_checks 
                if check.status == ServiceStatus.OPERATIONAL
            )
            failed_checks = total_checks - successful_checks
            
            availability_percentage = (successful_checks / total_checks) * 100
            
            response_times = [check.response_time_ms for check in period_checks if check.response_time_ms > 0]
            average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            max_response_time = max(response_times) if response_times else 0.0
            min_response_time = min(response_times) if response_times else 0.0
            
            # Get SLA targets
            endpoint = self.vendor_endpoints.get(vendor_name)
            sla_target_availability = endpoint.sla_uptime_percentage if endpoint else 99.0
            sla_target_response_time = endpoint.sla_response_time_ms if endpoint else 1000.0
            
            # Count SLA breaches
            sla_breach_count = sum(1 for check in period_checks if check.sla_breach)
            
            # Calculate potential SLA credits (example calculation)
            availability_breach = max(0, sla_target_availability - availability_percentage)
            sla_credits_owed = availability_breach * 100.0  # $100 per percentage point
            
            # Business impact score
            business_impact_score = self._calculate_period_business_impact(
                vendor_name, period_checks
            )
            
            return SLAMetrics(
                vendor_name=vendor_name,
                period_start=start_time,
                period_end=end_time,
                total_checks=total_checks,
                successful_checks=successful_checks,
                failed_checks=failed_checks,
                availability_percentage=availability_percentage,
                average_response_time=average_response_time,
                max_response_time=max_response_time,
                min_response_time=min_response_time,
                sla_target_availability=sla_target_availability,
                sla_target_response_time=sla_target_response_time,
                sla_breach_count=sla_breach_count,
                sla_credits_owed=sla_credits_owed,
                business_impact_score=business_impact_score
            )
            
        except Exception as e:
            logger.error(f"Calculating SLA metrics failed: {e}")
            return None
    
    def _calculate_period_business_impact(self, vendor_name: str, 
                                        period_checks: List[VendorHealthCheck]) -> float:
        """Calculate business impact over period"""
        try:
            total_impact = 0.0
            
            for check in period_checks:
                if check.status != ServiceStatus.OPERATIONAL:
                    # Get time between checks (assuming regular intervals)
                    time_impact = 5.0  # 5 minutes between checks
                    
                    # Apply vendor-specific impact
                    endpoint = self.vendor_endpoints.get(vendor_name)
                    if endpoint:
                        if endpoint.business_criticality == "critical":
                            total_impact += time_impact * 1.0
                        elif endpoint.business_criticality == "high":
                            total_impact += time_impact * 0.7
                        elif endpoint.business_criticality == "medium":
                            total_impact += time_impact * 0.4
                        else:
                            total_impact += time_impact * 0.2
            
            return total_impact
            
        except Exception as e:
            logger.error(f"Calculating period business impact failed: {e}")
            return 0.0
    
    async def get_vendor_status_summary(self) -> Dict[str, Any]:
        """Get summary of all vendor statuses"""
        try:
            summary = {
                "total_vendors": len(self.vendor_endpoints),
                "operational": 0,
                "degraded": 0,
                "outage": 0,
                "unknown": 0,
                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved_at]),
                "sla_breaches": 0,
                "critical_vendors": [],
                "vendor_details": {}
            }
            
            for vendor_name, endpoint in self.vendor_endpoints.items():
                # Get latest health check
                vendor_history = self.health_check_history.get(vendor_name, [])
                latest_check = vendor_history[-1] if vendor_history else None
                
                if latest_check:
                    status = latest_check.status
                    if status == ServiceStatus.OPERATIONAL:
                        summary["operational"] += 1
                    elif status == ServiceStatus.DEGRADED:
                        summary["degraded"] += 1
                    elif status in [ServiceStatus.MAJOR_OUTAGE, ServiceStatus.PARTIAL_OUTAGE]:
                        summary["outage"] += 1
                    else:
                        summary["unknown"] += 1
                    
                    if latest_check.sla_breach:
                        summary["sla_breaches"] += 1
                    
                    if (endpoint.business_criticality == "critical" and 
                        status != ServiceStatus.OPERATIONAL):
                        summary["critical_vendors"].append(vendor_name)
                    
                    summary["vendor_details"][vendor_name] = {
                        "status": status.value,
                        "response_time": latest_check.response_time_ms,
                        "availability": latest_check.availability_percentage,
                        "sla_breach": latest_check.sla_breach,
                        "business_criticality": endpoint.business_criticality,
                        "vendor_type": endpoint.vendor_type.value
                    }
                else:
                    summary["unknown"] += 1
                    summary["vendor_details"][vendor_name] = {
                        "status": "no_data",
                        "business_criticality": endpoint.business_criticality,
                        "vendor_type": endpoint.vendor_type.value
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Getting vendor status summary failed: {e}")
            return {}


# Global external vendor alerting instance
_external_vendor_alerting = None


def get_external_vendor_alerting(pagerduty_client=None) -> ExternalVendorAlerting:
    """Get external vendor alerting instance"""
    global _external_vendor_alerting
    if _external_vendor_alerting is None:
        _external_vendor_alerting = ExternalVendorAlerting(pagerduty_client)
    return _external_vendor_alerting


def create_external_vendor_alerting(pagerduty_client=None) -> ExternalVendorAlerting:
    """Create new external vendor alerting instance"""
    return ExternalVendorAlerting(pagerduty_client)


# Export main classes and functions
__all__ = [
    'ExternalVendorAlerting',
    'VendorEndpoint',
    'VendorHealthCheck',
    'SLAMetrics',
    'VendorAlert',
    'VendorType',
    'ServiceStatus',
    'SLABreachSeverity',
    'get_external_vendor_alerting',
    'create_external_vendor_alerting'
]