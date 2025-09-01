"""IA Influencer Agent - Geo Distribution Manager
Enterprise geographic content distribution and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT SÉVÈRE ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import geoip2.database
import geoip2.errors
import geopy.distance
from geopy.geocoders import Nominatim
import json
from datetime import datetime, timedelta
import numpy as np
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiohttp

from prometheus_client import Counter, Histogram, Gauge

# Metrics
geo_requests_total = Counter('geo_requests_total', 'Total geographic requests', ['country', 'region'])
geo_latency_seconds = Histogram('geo_latency_seconds', 'Geographic routing latency', ['source_region', 'target_region'])
geo_optimization_score = Gauge('geo_optimization_score', 'Geographic optimization score', ['region'])

logger = logging.getLogger(__name__)


class GeographicRegion(Enum):
    """Geographic regions for content distribution"""
    # Primary regions as per global deployment requirements
    US_EAST = "us-east"  # N. Virginia - Primary region
    US_WEST = "us-west"  # Oregon - Backup + West Coast users
    EU_WEST = "eu-west"  # Ireland - GDPR Compliance Europe
    AP_SOUTHEAST = "ap-southeast"  # Singapore - Asia-Pacific
    AP_NORTHEAST = "ap-northeast"  # Tokyo - Japan + Korea
    SA_EAST = "sa-east"  # São Paulo - South America
    
    # Legacy/secondary regions maintained for compatibility
    NORTH_AMERICA_EAST = "na-east"
    NORTH_AMERICA_WEST = "na-west"
    NORTH_AMERICA_CENTRAL = "na-central"
    EUROPE_WEST = "eu-west"
    EUROPE_CENTRAL = "eu-central"
    EUROPE_NORTH = "eu-north"
    ASIA_PACIFIC_EAST = "ap-east"
    ASIA_PACIFIC_SOUTHEAST = "ap-southeast"
    ASIA_PACIFIC_SOUTH = "ap-south"
    SOUTH_AMERICA_EAST = "sa-east"
    SOUTH_AMERICA_WEST = "sa-west"
    AFRICA_NORTH = "af-north"
    AFRICA_SOUTH = "af-south"
    MIDDLE_EAST = "me"
    OCEANIA = "oc"


class ContentDistributionStrategy(Enum):
    """Content distribution strategies"""
    GLOBAL = "global"           # Distribute to all regions
    SELECTIVE = "selective"     # Distribute to specific regions based on demand
    PROXIMITY = "proximity"     # Distribute based on user proximity
    LEGAL = "legal"            # Distribute based on legal restrictions
    PERFORMANCE = "performance" # Distribute based on performance optimization
    COST = "cost"              # Distribute based on cost optimization


class RegionPriority(Enum):
    """Region priority levels"""
    CRITICAL = "critical"    # Must have content immediately
    HIGH = "high"           # Should have content quickly
    MEDIUM = "medium"       # Can wait for content
    LOW = "low"            # Content optional
    BLOCKED = "blocked"     # Content not allowed


@dataclass
class GeographicPoint:
    """Geographic coordinate point"""
    latitude: float
    longitude: float
    country_code: str
    region_code: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None


@dataclass
class RegionMetrics:
    """Regional performance metrics"""
    region: GeographicRegion
    user_count: int
    request_count: int
    bandwidth_usage: int
    avg_latency: float
    error_rate: float
    cache_hit_ratio: float
    content_popularity: Dict[str, float]
    peak_hours: List[int]
    optimization_score: float


@dataclass
class ContentGeoDistribution:
    """Content geographic distribution configuration"""
    content_id: str
    content_type: str
    strategy: ContentDistributionStrategy
    primary_regions: List[GeographicRegion]
    secondary_regions: List[GeographicRegion]
    blocked_regions: List[GeographicRegion] = field(default_factory=list)
    legal_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    performance_requirements: Dict[str, float] = field(default_factory=dict)
    cost_constraints: Dict[str, float] = field(default_factory=dict)


@dataclass
class GeoOptimizationRule:
    """Geographic optimization rule"""
    name: str
    condition: str
    action: str
    priority: int
    source_regions: List[GeographicRegion]
    target_regions: List[GeographicRegion]
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class GeographicDistributionManager:
    """
    Geographic Distribution Manager for IA Influencer Agent Platform
    Optimizes content delivery based on geographic location and performance
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str = "redis://localhost:6379",
        geoip_database_path: str = "/etc/geoip/GeoLite2-City.mmdb"
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.geoip_database_path = geoip_database_path
        
        # Database connections
        self.engine = None
        self.session_factory = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # GeoIP and geocoding
        self.geoip_reader = None
        self.geocoder = Nominatim(user_agent="ia-influencer-agent")
        
        # Regional data
        self.region_endpoints: Dict[GeographicRegion, Dict[str, str]] = {}
        self.region_metrics: Dict[GeographicRegion, RegionMetrics] = {}
        self.optimization_rules: List[GeoOptimizationRule] = []
        
        # Content distribution
        self.content_distributions: Dict[str, ContentGeoDistribution] = {}
        self.distribution_cache: Dict[str, Any] = {}
        
        # Performance tracking
        self.latency_matrix: Dict[Tuple[GeographicRegion, GeographicRegion], float] = {}
        self.bandwidth_costs: Dict[GeographicRegion, float] = {}
    
    async def initialize(self) -> bool:
        """Initialize geographic distribution manager"""
        try:
            logger.info("Initializing Geographic Distribution Manager...")
            
            # Initialize database connection
            self.engine = create_async_engine(self.database_url)
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize GeoIP database
            await self._initialize_geoip()
            
            # Load regional configurations
            await self._load_regional_configurations()
            
            # Load optimization rules
            await self._load_optimization_rules()
            
            # Initialize latency matrix
            await self._initialize_latency_matrix()
            
            # Start background tasks
            asyncio.create_task(self._metrics_collection_loop())
            asyncio.create_task(self._optimization_loop())
            asyncio.create_task(self._latency_monitoring_loop())
            
            logger.info("Geographic Distribution Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Geographic Distribution Manager: {e}")
            return False
    
    async def determine_optimal_region(
        self,
        client_ip: str,
        content_id: str,
        request_type: str = "download"
    ) -> Optional[GeographicRegion]:
        """Determine optimal region for content delivery"""
        try:
            # Get client location
            client_location = await self._get_client_location(client_ip)
            if not client_location:
                return GeographicRegion.US_EAST  # Primary region fallback
            
            # Get content distribution configuration
            content_distribution = self.content_distributions.get(content_id)
            if not content_distribution:
                # Use default optimization
                return await self._get_default_optimal_region(client_location)
            
            # Check legal restrictions
            if client_location.country_code in content_distribution.blocked_regions:
                logger.warning(f"Content {content_id} blocked in {client_location.country_code}")
                return None
            
            # Apply distribution strategy
            optimal_region = await self._apply_distribution_strategy(
                content_distribution,
                client_location,
                request_type
            )
            
            # Validate region availability
            if optimal_region and await self._validate_region_availability(optimal_region):
                # Update metrics
                geo_requests_total.labels(
                    country=client_location.country_code,
                    region=optimal_region.value
                ).inc()
                
                return optimal_region
            
            # Fallback to secondary region
            return await self._get_fallback_region(content_distribution, client_location)
            
        except Exception as e:
            logger.error(f"Failed to determine optimal region: {e}")
            return GeographicRegion.US_EAST  # Primary region safe fallback
    
    async def optimize_content_distribution(
        self,
        content_id: str,
        content_metadata: Dict[str, Any]
    ) -> ContentGeoDistribution:
        """Optimize content distribution based on analytics and performance"""
        try:
            # Analyze content performance by region
            regional_performance = await self._analyze_regional_performance(content_id)
            
            # Analyze user geographic distribution
            user_distribution = await self._analyze_user_geographic_distribution(content_id)
            
            # Calculate optimal distribution strategy
            optimal_strategy = await self._calculate_optimal_strategy(
                content_metadata,
                regional_performance,
                user_distribution
            )
            
            # Determine primary and secondary regions
            primary_regions, secondary_regions = await self._optimize_region_selection(
                optimal_strategy,
                regional_performance,
                user_distribution
            )
            
            # Apply legal and compliance constraints
            blocked_regions, legal_restrictions = await self._apply_legal_constraints(
                content_metadata,
                primary_regions + secondary_regions
            )
            
            # Calculate performance requirements
            performance_requirements = await self._calculate_performance_requirements(
                content_metadata,
                primary_regions
            )
            
            # Calculate cost constraints
            cost_constraints = await self._calculate_cost_constraints(
                content_metadata,
                primary_regions + secondary_regions
            )
            
            # Create optimized distribution configuration
            distribution_config = ContentGeoDistribution(
                content_id=content_id,
                content_type=content_metadata.get('content_type', 'unknown'),
                strategy=optimal_strategy,
                primary_regions=primary_regions,
                secondary_regions=secondary_regions,
                blocked_regions=blocked_regions,
                legal_restrictions=legal_restrictions,
                performance_requirements=performance_requirements,
                cost_constraints=cost_constraints
            )
            
            # Store configuration
            self.content_distributions[content_id] = distribution_config
            await self._cache_distribution_config(distribution_config)
            
            logger.info(f"Optimized content distribution for: {content_id}")
            return distribution_config
            
        except Exception as e:
            logger.error(f"Failed to optimize content distribution: {e}")
            # Return default distribution
            return ContentGeoDistribution(
                content_id=content_id,
                content_type=content_metadata.get('content_type', 'unknown'),
                strategy=ContentDistributionStrategy.GLOBAL,
                primary_regions=list(GeographicRegion),
                secondary_regions=[]
            )
    
    async def get_regional_metrics(
        self,
        region: Optional[GeographicRegion] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, RegionMetrics]:
        """Get comprehensive regional performance metrics"""
        try:
            regions_to_analyze = [region] if region else list(GeographicRegion)
            regional_metrics = {}
            
            end_time = datetime.now()
            start_time = end_time - time_range
            
            for region in regions_to_analyze:
                # Get regional metrics from database
                async with self.session_factory() as session:
                    metrics_data = await self._get_regional_metrics_data(
                        session, region, start_time, end_time
                    )
                
                # Calculate derived metrics
                metrics = RegionMetrics(
                    region=region,
                    user_count=metrics_data.get('user_count', 0),
                    request_count=metrics_data.get('request_count', 0),
                    bandwidth_usage=metrics_data.get('bandwidth_usage', 0),
                    avg_latency=metrics_data.get('avg_latency', 0.0),
                    error_rate=metrics_data.get('error_rate', 0.0),
                    cache_hit_ratio=metrics_data.get('cache_hit_ratio', 0.0),
                    content_popularity=metrics_data.get('content_popularity', {}),
                    peak_hours=metrics_data.get('peak_hours', []),
                    optimization_score=await self._calculate_optimization_score(region, metrics_data)
                )
                
                regional_metrics[region.value] = metrics
                
                # Update Prometheus metrics
                geo_optimization_score.labels(region=region.value).set(metrics.optimization_score)
            
            return regional_metrics
            
        except Exception as e:
            logger.error(f"Failed to get regional metrics: {e}")
            return {}
    
    async def calculate_geographic_latency(
        self,
        source_region: GeographicRegion,
        target_region: GeographicRegion
    ) -> float:
        """Calculate latency between geographic regions"""
        try:
            # Check cache first
            cache_key = (source_region, target_region)
            if cache_key in self.latency_matrix:
                return self.latency_matrix[cache_key]
            
            # Calculate latency based on geographic distance and network topology
            latency = await self._calculate_network_latency(source_region, target_region)
            
            # Cache the result
            self.latency_matrix[cache_key] = latency
            
            # Update metrics
            geo_latency_seconds.labels(
                source_region=source_region.value,
                target_region=target_region.value
            ).observe(latency)
            
            return latency
            
        except Exception as e:
            logger.error(f"Failed to calculate geographic latency: {e}")
            return 999.0  # High latency as fallback
    
    async def apply_legal_restrictions(
        self,
        content_id: str,
        restrictions: Dict[str, List[str]]
    ) -> bool:
        """Apply legal restrictions to content distribution"""
        try:
            # Get current distribution
            distribution = self.content_distributions.get(content_id)
            if not distribution:
                logger.error(f"Content distribution not found: {content_id}")
                return False
            
            # Update legal restrictions
            distribution.legal_restrictions.update(restrictions)
            
            # Recalculate blocked regions based on restrictions
            blocked_regions = []
            for restriction_type, blocked_countries in restrictions.items():
                if restriction_type == "copyright":
                    # Block regions for copyright restrictions
                    for country in blocked_countries:
                        region = await self._get_region_for_country(country)
                        if region and region not in blocked_regions:
                            blocked_regions.append(region)
                
                elif restriction_type == "content_rating":
                    # Apply content rating restrictions
                    for country in blocked_countries:
                        region = await self._get_region_for_country(country)
                        if region and region not in blocked_regions:
                            blocked_regions.append(region)
            
            # Update blocked regions
            distribution.blocked_regions.extend(blocked_regions)
            distribution.blocked_regions = list(set(distribution.blocked_regions))  # Remove duplicates
            
            # Update primary and secondary regions
            distribution.primary_regions = [
                r for r in distribution.primary_regions 
                if r not in distribution.blocked_regions
            ]
            distribution.secondary_regions = [
                r for r in distribution.secondary_regions 
                if r not in distribution.blocked_regions
            ]
            
            # Save updated configuration
            await self._cache_distribution_config(distribution)
            
            logger.info(f"Applied legal restrictions to content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply legal restrictions: {e}")
            return False
    
    async def get_geographic_analytics(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get comprehensive geographic analytics"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            analytics = {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'regional_performance': {},
                'global_distribution': {},
                'optimization_opportunities': [],
                'cost_analysis': {},
                'latency_analysis': {}
            }
            
            # Get regional performance metrics
            analytics['regional_performance'] = await self.get_regional_metrics(time_range=time_range)
            
            # Calculate global distribution patterns
            analytics['global_distribution'] = await self._calculate_global_distribution_patterns(start_time, end_time)
            
            # Identify optimization opportunities
            analytics['optimization_opportunities'] = await self._identify_optimization_opportunities()
            
            # Calculate cost analysis
            analytics['cost_analysis'] = await self._calculate_geographic_costs(start_time, end_time)
            
            # Analyze latency patterns
            analytics['latency_analysis'] = await self._analyze_latency_patterns(start_time, end_time)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get geographic analytics: {e}")
            return {}
    
    async def predict_optimal_expansion(
        self,
        content_type: str,
        user_growth_predictions: Dict[str, float]
    ) -> List[GeographicRegion]:
        """Predict optimal regions for content expansion"""
        try:
            # Analyze current regional performance
            current_performance = await self.get_regional_metrics()
            
            # Calculate expansion scores for each region
            expansion_scores = {}
            
            for region in GeographicRegion:
                if region.value not in current_performance:
                    # Calculate potential for new region
                    score = await self._calculate_expansion_potential(
                        region,
                        content_type,
                        user_growth_predictions
                    )
                else:
                    # Calculate expansion opportunity for existing region
                    current_metrics = current_performance[region.value]
                    score = await self._calculate_expansion_opportunity(
                        region,
                        current_metrics,
                        user_growth_predictions
                    )
                
                expansion_scores[region] = score
            
            # Sort regions by expansion score
            sorted_regions = sorted(
                expansion_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return top regions with score > threshold
            recommended_regions = [
                region for region, score in sorted_regions
                if score > 0.7  # 70% threshold
            ]
            
            logger.info(f"Recommended {len(recommended_regions)} regions for expansion")
            return recommended_regions[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to predict optimal expansion: {e}")
            return []
    
    # Private methods
    
    async def _initialize_geoip(self) -> None:
        """Initialize GeoIP database"""
        try:
            self.geoip_reader = geoip2.database.Reader(self.geoip_database_path)
            logger.info("GeoIP database initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize GeoIP database: {e}")
            self.geoip_reader = None
    
    async def _get_client_location(self, client_ip: str) -> Optional[GeographicPoint]:
        """Get client geographic location from IP"""
        try:
            if not self.geoip_reader:
                return None
            
            response = self.geoip_reader.city(client_ip)
            
            return GeographicPoint(
                latitude=float(response.location.latitude),
                longitude=float(response.location.longitude),
                country_code=response.country.iso_code,
                region_code=response.subdivisions.most_specific.iso_code,
                city=response.city.name,
                timezone=response.location.time_zone
            )
            
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"IP address not found in GeoIP database: {client_ip}")
            return None
        except Exception as e:
            logger.error(f"Failed to get client location: {e}")
            return None
    
    async def _load_regional_configurations(self) -> None:
        """Load regional endpoint configurations"""
        try:
            # Primary regional endpoints for global multi-region deployment
            default_endpoints = {
                # Primary Regions as per Global Deployment Requirements
                GeographicRegion.US_EAST: {
                    'primary': 'https://cdn-us-east.influencer-agent.com',
                    'secondary': 'https://cdn-us-east-2.influencer-agent.com',
                    'location': {'lat': 38.9072, 'lon': -77.0369},  # N. Virginia
                    'region_name': 'US-East (N. Virginia)',
                    'priority': 'primary',
                    'compliance': ['SOC2', 'PCI-DSS'],
                    'aws_region': 'us-east-1'
                },
                GeographicRegion.US_WEST: {
                    'primary': 'https://cdn-us-west.influencer-agent.com',
                    'secondary': 'https://cdn-us-west-2.influencer-agent.com',
                    'location': {'lat': 45.5152, 'lon': -122.6784},  # Oregon
                    'region_name': 'US-West (Oregon)',
                    'priority': 'backup',
                    'compliance': ['SOC2', 'PCI-DSS'],
                    'aws_region': 'us-west-2'
                },
                GeographicRegion.EU_WEST: {
                    'primary': 'https://cdn-eu-west.influencer-agent.com',
                    'secondary': 'https://cdn-eu-west-2.influencer-agent.com',
                    'location': {'lat': 53.3498, 'lon': -6.2603},  # Ireland
                    'region_name': 'EU-West (Ireland)',
                    'priority': 'high',
                    'compliance': ['GDPR', 'SOC2', 'ISO27001'],
                    'aws_region': 'eu-west-1'
                },
                GeographicRegion.AP_SOUTHEAST: {
                    'primary': 'https://cdn-ap-southeast.influencer-agent.com',
                    'secondary': 'https://cdn-ap-southeast-2.influencer-agent.com',
                    'location': {'lat': 1.3521, 'lon': 103.8198},  # Singapore
                    'region_name': 'AP-Southeast (Singapore)',
                    'priority': 'high',
                    'compliance': ['SOC2', 'ISO27001'],
                    'aws_region': 'ap-southeast-1'
                },
                GeographicRegion.AP_NORTHEAST: {
                    'primary': 'https://cdn-ap-northeast.influencer-agent.com',
                    'secondary': 'https://cdn-ap-northeast-2.influencer-agent.com',
                    'location': {'lat': 35.6762, 'lon': 139.6503},  # Tokyo
                    'region_name': 'AP-Northeast (Tokyo)',
                    'priority': 'high',
                    'compliance': ['SOC2', 'ISO27001'],
                    'aws_region': 'ap-northeast-1'
                },
                GeographicRegion.SA_EAST: {
                    'primary': 'https://cdn-sa-east.influencer-agent.com',
                    'secondary': 'https://cdn-sa-east-2.influencer-agent.com',
                    'location': {'lat': -23.5505, 'lon': -46.6333},  # São Paulo
                    'region_name': 'SA-East (São Paulo)',
                    'priority': 'medium',
                    'compliance': ['SOC2'],
                    'aws_region': 'sa-east-1'
                },
                
                # Legacy/Secondary regions for compatibility
                GeographicRegion.NORTH_AMERICA_EAST: {
                    'primary': 'https://cdn-na-east.influencer-agent.com',
                    'secondary': 'https://cdn-na-east-2.influencer-agent.com',
                    'location': {'lat': 40.7128, 'lon': -74.0060},  # New York
                    'region_name': 'North America East (Legacy)',
                    'priority': 'legacy'
                },
                GeographicRegion.EUROPE_WEST: {
                    'primary': 'https://cdn-eu-west.influencer-agent.com',
                    'secondary': 'https://cdn-eu-west-2.influencer-agent.com',
                    'location': {'lat': 51.5074, 'lon': -0.1278},  # London
                    'region_name': 'Europe West (Legacy)',
                    'priority': 'legacy'
                }
            }
            
            self.region_endpoints.update(default_endpoints)
            logger.info(f"Loaded {len(self.region_endpoints)} regional configurations")
            
        except Exception as e:
            logger.error(f"Failed to load regional configurations: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while True:
            try:
                # Collect regional metrics every 5 minutes
                await asyncio.sleep(300)
                await self._collect_regional_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(300)
    
    async def _optimization_loop(self) -> None:
        """Geographic optimization loop"""
        while True:
            try:
                # Run optimization every hour
                await asyncio.sleep(3600)
                await self._run_geographic_optimization()
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(3600)
